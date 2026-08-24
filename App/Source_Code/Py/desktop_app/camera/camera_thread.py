import os
import sys
import time
import tempfile
import numpy as np
import cv2
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

# Add shared directory to path for standalone execution/testing
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "shared"))
if SHARED_DIR not in sys.path:
    sys.path.append(SHARED_DIR)

from processor import HyperspectralModel

def get_linux_camera_indices():
    indices = []
    if not sys.platform.startswith('linux'):
        return list(range(8))
    
    try:
        import re
        v4l_dir = '/sys/class/video4linux'
        if os.path.exists(v4l_dir):
            for dev in os.listdir(v4l_dir):
                m = re.match(r'video(\d+)', dev)
                if m:
                    idx = int(m.group(1))
                    # Exclude virtual/helper/codec/ISP nodes (typically >= 10 on Pi/SoC devices) to prevent OpenCV hanging
                    if idx >= 10:
                        continue
                    name_file = os.path.join(v4l_dir, dev, 'name')
                    if os.path.exists(name_file):
                        with open(name_file, 'r') as f:
                            dev_name = f.read().lower()
                        # Exclude metadata, codec, and isp nodes
                        if 'metadata' in dev_name or 'meta' in dev_name:
                            continue
                        if 'isp' in dev_name:
                            continue
                        if 'codec' in dev_name:
                            continue
                    indices.append(idx)
    except Exception:
        pass
    
    if not indices:
        indices = [0, 2, 4, 6]
    return sorted(list(set(indices)))

class CameraThread(QThread):
    # Signals
    frame_ready = pyqtSignal(np.ndarray)
    status_message = pyqtSignal(str)
    
    def __init__(self, weight_path, cr_weights_path, parent=None):
        super().__init__(parent)
        self.weight_path = weight_path
        self.cr_weights_path = cr_weights_path
        
        # Thread safety mutex
        self.mutex = QMutex()
        
        # Thread states
        self._is_running = True
        self.use_simulation = False
        self.frame_id = 0
        
        # Thread safety state request flags
        self.cap = None
        self._pause_requested = False
        self._resume_requested = False
        self._is_paused = False
        self.successful_camera_idx = None
        self.successful_backend = None
        
        # Settings (guarded by mutex)
        self.gain = 1.0
        self.bands = [
            {"lower": 400, "upper": 450},
            {"lower": 500, "upper": 550},
            {"lower": 600, "upper": 650},
            {"lower": 700, "upper": 750}
        ]
        
        # Video recording states
        self._is_recording = False
        self.video_writer = None
        self.video_writer_orig = None
        self.record_width = 640
        self.record_height = 480
        self.record_fps = 15.0  # Capped at 15 FPS
        # Ensure a safe, ASCII-only temp directory for OpenCV VideoWriter on Windows
        temp_dir = tempfile.gettempdir()
        if os.name == 'nt':
            import ctypes
            buf = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetShortPathNameW(temp_dir, buf, 1024):
                temp_dir = buf.value
            else:
                # If short path fails and contains Unicode, fallback to Public directory
                if any(ord(c) > 127 for c in temp_dir):
                    public_dir = os.environ.get('PUBLIC', 'C:\\Users\\Public')
                    temp_dir = os.path.join(public_dir, "HyperspectralImagingTemp")
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_video_path = os.path.join(temp_dir, "hsi_temp_record.avi")
        self.temp_video_orig_path = os.path.join(temp_dir, "hsi_temp_record_orig.avi")
        
        # Cache for the last processed frame
        self.last_frame_bgr = None
        
        # Model instance (loaded in run())
        self.model = None

        # Pre-allocated arrays for Downscaling & Processing (Fix 4)
        self.prealloc_raw_320 = np.zeros((240, 320, 3), dtype=np.uint8)
        self.prealloc_bgr_upscaled = np.zeros((480, 640, 3), dtype=np.uint8)
        self.prealloc_rgb_upscaled = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 15 FPS Throttle (Fix 1)
        self.last_inference_time = 0.0
        
        # Full-resolution camera cache for Photo Capture (Fix 2)
        self.last_raw_frame_full = None

    def update_settings(self, gain, bands):
        """Thread-safe update of gain and band configuration settings"""
        locker = QMutexLocker(self.mutex)
        self.gain = gain
        self.bands = bands

    def get_settings(self):
        """Thread-safe retrieval of settings"""
        locker = QMutexLocker(self.mutex)
        return self.gain, list(self.bands)

    def pause_camera(self):
        """Request the camera thread to release the camera hardware"""
        locker = QMutexLocker(self.mutex)
        self._pause_requested = True
        self._resume_requested = False
        self._is_paused = True
        self.status_message.emit("Camera turn-off requested...")

    def resume_camera(self):
        """Request the camera thread to re-initialize the camera hardware"""
        locker = QMutexLocker(self.mutex)
        self._resume_requested = True
        self._pause_requested = False
        self._is_paused = False
        self.status_message.emit("Camera resume requested...")

    def _load_pi_camera_driver(self):
        if sys.platform.startswith('linux'):
            # Check if /dev/video0 exists
            if not os.path.exists('/dev/video0'):
                self.status_message.emit("Pi Camera /dev/video0 not found. Attempting to load V4L2 driver module...")
                try:
                    import subprocess
                    # Run modprobe with sudo non-interactively
                    result = subprocess.run(['sudo', '-n', 'modprobe', 'bcm2835-v4l2'], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.status_message.emit("Successfully loaded bcm2835-v4l2 driver module.")
                        time.sleep(1.0) # Wait a bit for the device node to populate
                    else:
                        self.status_message.emit(f"Failed to load driver module: {result.stderr.strip()}")
                except Exception as e:
                    self.status_message.emit(f"Error loading Pi camera driver: {str(e)}")

    def _open_camera(self):
        opened = False
        self.cap = None
        
        # Auto-load camera driver module if running on Raspberry Pi / Linux
        self._load_pi_camera_driver()
        
        # 1. Try the cached successful camera first
        if self.successful_camera_idx is not None and self.successful_backend is not None:
            self.status_message.emit(f"Opening cached camera (Index {self.successful_camera_idx})...")
            try:
                if self.successful_backend[1] == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(self.successful_camera_idx)
                else:
                    cap = cv2.VideoCapture(self.successful_camera_idx, self.successful_backend[1])
                
                if cap.isOpened():
                    frame_read_success = False
                    for attempt in range(5):
                        ret, temp_frame = cap.read()
                        if ret and temp_frame is not None:
                            frame_read_success = True
                            break
                        time.sleep(0.3)
                    if frame_read_success:
                        self.cap = cap
                        self.status_message.emit("Camera reconnected successfully.")
                        self.use_simulation = False
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        time.sleep(0.5)
                        return
                    cap.release()
            except Exception as e:
                self.status_message.emit(f"Cached camera reconnect failed: {str(e)}")
        
        # 2. Fall back to scanning camera indices
        if sys.platform.startswith('win32'):
            camera_indices = list(range(8))
            backends = [
                ("DirectShow", cv2.CAP_DSHOW),
                ("Media Foundation", cv2.CAP_MSMF),
                ("Default", cv2.CAP_ANY)
            ]
        elif sys.platform.startswith('linux'):
            camera_indices = get_linux_camera_indices()
            backends = [
                ("V4L2", cv2.CAP_V4L2),
                ("Default", cv2.CAP_ANY)
            ]
        else:
            camera_indices = list(range(8))
            backends = [
                ("Default", cv2.CAP_ANY)
            ]
        
        for cam_idx in camera_indices:
            if opened:
                break
                
            for backend_name, backend_id in backends:
                self.status_message.emit(f"Scanning camera index {cam_idx} with {backend_name}...")
                try:
                    if backend_id == cv2.CAP_ANY:
                        cap = cv2.VideoCapture(cam_idx)
                    else:
                        cap = cv2.VideoCapture(cam_idx, backend_id)
                        
                    if cap.isOpened():
                        frame_read_success = False
                        frame = None
                        for attempt in range(5):
                            ret, temp_frame = cap.read()
                            if ret and temp_frame is not None:
                                frame = temp_frame
                                frame_read_success = True
                                break
                            time.sleep(0.3)
                            
                        if frame_read_success:
                            self.cap = cap
                            self.successful_camera_idx = cam_idx
                            self.successful_backend = (backend_name, backend_id)
                            self.status_message.emit(f"Camera index {cam_idx} ({backend_name}) connected successfully.")
                            opened = True
                            break
                        
                        cap.release()
                except Exception as e:
                    self.status_message.emit(f"{backend_name} error on index {cam_idx}: {str(e)}")
                
        if not opened:
            self.status_message.emit("No working physical camera detected. Running simulation.")
            self.use_simulation = True
        else:
            self.use_simulation = False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            time.sleep(0.5)

    def start_recording(self):
        """Starts recording processed and raw frames to temporary files in parallel"""
        locker = QMutexLocker(self.mutex)
        if self._is_recording:
            return
            
        # Clean up existing temp videos if any
        for path in [self.temp_video_path, self.temp_video_orig_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
                
        # Initialize VideoWriters
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # AVI format compatibility
        self.video_writer = cv2.VideoWriter(
            self.temp_video_path, 
            fourcc, 
            self.record_fps, 
            (self.record_width, self.record_height)
        )
        self.video_writer_orig = cv2.VideoWriter(
            self.temp_video_orig_path, 
            fourcc, 
            self.record_fps, 
            (self.record_width, self.record_height)
        )
        self._is_recording = True
        self.status_message.emit("Recording started...")

    def stop_recording(self):
        """Stops recording and releases the VideoWriters"""
        locker = QMutexLocker(self.mutex)
        if not self._is_recording:
            return
            
        self._is_recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        if self.video_writer_orig is not None:
            self.video_writer_orig.release()
            self.video_writer_orig = None
        self.status_message.emit("Recording stopped.")

    def is_recording(self):
        """Thread-safe check if currently recording"""
        locker = QMutexLocker(self.mutex)
        return self._is_recording

    def stop(self):
        """Safely stops the thread"""
        locker = QMutexLocker(self.mutex)
        self._is_running = False
        self.quit()

    def capture_full_resolution(self):
        """Processes the last raw full-resolution camera frame and returns the processed BGR image (Fix 2)"""
        locker = QMutexLocker(self.mutex)
        if self.last_raw_frame_full is None:
            return None
        
        # Get settings thread-safely
        gain = self.gain
        bands = list(self.bands)
        
        # Run inference on the FULL resolution raw frame (not downscaled)
        try:
            if not bands:
                return self.last_raw_frame_full.copy()
            full_processed_bgr = self.model.process_frame(self.last_raw_frame_full, gain=gain, bands=bands)
            return full_processed_bgr
        except Exception as e:
            self.status_message.emit(f"Full-res capture error: {str(e)}")
            return None

    def generate_mock_tissue(self, frame_id, width=1280, height=720):
        """
        Generates a highly realistic, moving procedural biological tissue biopsy slide
        with cells, purple nuclei, and branching blood capillaries. (Default high resolution)
        """
        # Create empty canvas with pale pink/purple cytoplasm background
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:, :] = [230, 210, 240]  # BGR pale pinkish purple
        
        # Dynamic camera drift simulation (slow organic panning)
        t = frame_id * 0.04
        dx = int(15 * np.sin(t * 0.6))
        dy = int(15 * np.cos(t * 0.4))
        
        # Use deterministic seeding per cell so cell layout remains stable
        np.random.seed(42)
        
        # 1. Cytoplasm / Cell Membranes
        for i in range(24):
            cx = int(np.random.randint(40, width - 40) + dx)
            cy = int(np.random.randint(40, height - 40) + dy)
            r = np.random.randint(45, 95)
            color = [np.random.randint(200, 220), np.random.randint(170, 195), np.random.randint(215, 235)]
            cv2.circle(img, (cx, cy), r, color, -1)
            cv2.circle(img, (cx, cy), r, [170, 145, 190], 1)
            
        # 2. Cell Nuclei (highly visible dense chromatin bodies)
        np.random.seed(42)
        for i in range(24):
            cx = int(np.random.randint(40, width - 40) + dx)
            cy = int(np.random.randint(40, height - 40) + dy)
            ncx = cx + int(3 * np.sin(t * 1.5 + i))
            ncy = cy + int(3 * np.cos(t * 1.5 + i))
            r = np.random.randint(20, 35)
            # Deep violet purple
            cv2.circle(img, (ncx, ncy), r, [140, 60, 110], -1)
            cv2.circle(img, (ncx, ncy), r, [100, 30, 75], 1)
            
        # 3. Branching Blood Vessels (erythrocyte-rich capillaries)
        np.random.seed(1337)
        for v in range(4):
            start_x = np.random.randint(-50, width + 50)
            start_y = np.random.randint(-50, height + 50)
            points = []
            curr_x, curr_y = start_x, start_y
            angle = np.random.uniform(0, 2 * np.pi)
            
            for step in range(15):
                curr_x += int(np.random.randint(45, 95) * np.cos(angle + 0.15 * np.sin(t * 0.2 + step)))
                curr_y += int(np.random.randint(45, 95) * np.sin(angle + 0.15 * np.sin(t * 0.2 + step)))
                points.append((curr_x + dx, curr_y + dy))
                
            for p in range(len(points) - 1):
                thickness = np.random.randint(5, 12)
                color = [60, 45, 225]  # BGR
                cv2.line(img, points[p], points[p+1], color, thickness)
                
                if np.random.rand() > 0.6:
                    bx = (points[p][0] + points[p+1][0]) // 2
                    by = (points[p][1] + points[p+1][1]) // 2
                    angle_branch = angle + np.random.choice([-np.pi/3, np.pi/3])
                    bx2 = bx + int(60 * np.cos(angle_branch))
                    by2 = by + int(60 * np.sin(angle_branch))
                    cv2.line(img, (bx, by), (bx2, by2), [90, 60, 195], thickness - 3)

        # 4. Sensor noise
        noise = np.random.normal(0, 6, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # 5. Microscopic optical diffusion
        img = cv2.GaussianBlur(img, (3, 3), 0)
        return img

    def run(self):
        self.status_message.emit("Initializing Hyperspectral Model...")
        try:
            self.model = HyperspectralModel(self.weight_path, self.cr_weights_path)
            self.status_message.emit("Model loaded successfully!")
        except Exception as e:
            self.status_message.emit(f"Model error: {str(e)}")
            self._is_running = False
            return

        self._open_camera()
        
        # Loop delay of ~33ms corresponds to 30 FPS tick
        while True:
            pause_to_handle = False
            resume_to_handle = False
            with QMutexLocker(self.mutex):
                if not self._is_running:
                    break
                if self._pause_requested:
                    pause_to_handle = True
                    self._pause_requested = False
                if self._resume_requested:
                    resume_to_handle = True
                    self._resume_requested = False
            
            if pause_to_handle:
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                    self.status_message.emit("Camera turned off.")
            
            if resume_to_handle:
                self._open_camera()
            
            # Process next frame
            self.process_next_frame()
            time.sleep(0.033)
        
        # Clean up on exit
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            
        with QMutexLocker(self.mutex):
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            if self.video_writer_orig is not None:
                self.video_writer_orig.release()
                self.video_writer_orig = None
                
        self.status_message.emit("Camera thread terminated.")

    def process_next_frame(self):
        """Handles frame reading, throttling, processing, and emission completely in background thread"""
        with QMutexLocker(self.mutex):
            if self._is_paused:
                return

        # 1. 15 FPS Throttle perf_counter check (Bug 1 Step 2)
        current_time = time.perf_counter()
        elapsed = current_time - self.last_inference_time
        
        # If less than 66ms, we emit the last processed frame buffer copy to avoid CPU work
        if elapsed < 0.066:
            if self.prealloc_rgb_upscaled is not None:
                self.frame_ready.emit(self.prealloc_rgb_upscaled.copy())
            return

        raw_frame = None
        if self.use_simulation:
            self.frame_id += 1
            raw_frame = self.generate_mock_tissue(self.frame_id)
        else:
            if self.cap is None:
                return
            ret, raw_frame = self.cap.read()
            if not ret:
                self.status_message.emit("Camera frame capture failed. Launching simulation.")
                self.use_simulation = True
                self.frame_id += 1
                raw_frame = self.generate_mock_tissue(self.frame_id)

        if raw_frame is not None:
            self.last_inference_time = current_time
            self.last_raw_frame_full = raw_frame.copy()
            
            # Retrieve settings thread-safely
            gain, bands = self.get_settings()
            
            try:
                if not bands:
                    cv2.resize(raw_frame, (640, 480), dst=self.prealloc_bgr_upscaled, interpolation=cv2.INTER_LINEAR)
                    cv2.cvtColor(self.prealloc_bgr_upscaled, cv2.COLOR_BGR2RGB, dst=self.prealloc_rgb_upscaled)
                else:
                    # 2. Downscale raw frame to 320x240 for processing (Bug 1 Step 3)
                    cv2.resize(raw_frame, (320, 240), dst=self.prealloc_raw_320, interpolation=cv2.INTER_LINEAR)
                    
                    # 3. Process the downscaled frame entirely inside background QThread (Bug 1 Step 1)
                    processed_small = self.model.process_frame(self.prealloc_raw_320, gain=gain, bands=bands)
                    
                    # 4. Upscale back to display size 640x480 (Bug 1 Step 3)
                    cv2.resize(processed_small, (640, 480), dst=self.prealloc_bgr_upscaled, interpolation=cv2.INTER_LINEAR)
                    
                    # 5. Convert BGR to RGB
                    cv2.cvtColor(self.prealloc_bgr_upscaled, cv2.COLOR_BGR2RGB, dst=self.prealloc_rgb_upscaled)
                
                # Cache BGR for video writing
                self.last_frame_bgr = self.prealloc_bgr_upscaled.copy()
                
                # Write to file if recording is in progress
                with QMutexLocker(self.mutex):
                    if self._is_recording and self.video_writer is not None:
                        record_frame = cv2.resize(self.last_frame_bgr, (self.record_width, self.record_height))
                        self.video_writer.write(record_frame)
                    if self._is_recording and self.video_writer_orig is not None:
                        record_frame_orig = cv2.resize(raw_frame, (self.record_width, self.record_height))
                        self.video_writer_orig.write(record_frame_orig)
                
                # Emit processed frame to main thread
                self.frame_ready.emit(self.prealloc_rgb_upscaled.copy())
                
            except Exception as e:
                self.status_message.emit(f"Processing error: {str(e)}")
