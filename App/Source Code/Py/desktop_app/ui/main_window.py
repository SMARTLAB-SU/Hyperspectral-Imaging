import sys, os, shutil, datetime, cv2, numpy as np
import tempfile, uuid
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QPushButton, QFileDialog, QGroupBox, QStatusBar, QFrame, QLineEdit, QSizePolicy, QScrollArea, QStackedWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIntValidator

def get_save_root():
    # Try to locate the user's Desktop directory first for easy access
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(desktop):
        return desktop
    
    # Fallback to the application directory if Desktop is not found
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def safe_imread(path):
    try:
        # Read file as bytes to support Unicode paths on Windows
        with open(path, "rb") as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is not None:
                return img
    except Exception:
        pass
    return cv2.imread(path)

def safe_imwrite(path, img):
    try:
        ext = os.path.splitext(path)[1]
        ret, buf = cv2.imencode(ext, img)
        if ret:
            # Ensure folder exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "wb") as f:
                f.write(buf)
            return True
    except Exception:
        pass
    return cv2.imwrite(path, img)

def safe_video_capture(path):
    if isinstance(path, int):
        return cv2.VideoCapture(path)
    # Try Windows short path (8.3 format) first
    if os.name == 'nt':
        import ctypes
        parent = os.path.dirname(os.path.abspath(path))
        buf = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(parent, buf, 1024):
            short_path = os.path.join(buf.value, os.path.basename(path))
            cap = cv2.VideoCapture(short_path)
            if cap.isOpened():
                return cap
    # Fallback: copy file to safe ASCII temp folder and read from there
    if any(ord(c) > 127 for c in path):
        temp_dir = tempfile.gettempdir()
        if os.name == 'nt' and any(ord(c) > 127 for c in temp_dir):
            public_dir = os.environ.get('PUBLIC', 'C:\\Users\\Public')
            temp_dir = os.path.join(public_dir, "HyperspectralImagingTemp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"temp_read_{uuid.uuid4().hex}.avi")
        try:
            shutil.copy2(path, temp_path)
            cap = cv2.VideoCapture(temp_path)
            if cap.isOpened():
                orig_release = cap.release
                def custom_release():
                    orig_release()
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception:
                        pass
                cap.release = custom_release
                return cap
        except Exception:
            pass
    return cv2.VideoCapture(path)

def safe_video_writer(path, fourcc, fps, frame_size):
    # Try Windows short path (8.3 format) first
    if os.name == 'nt':
        import ctypes
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        buf = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(parent, buf, 1024):
            short_path = os.path.join(buf.value, os.path.basename(path))
            writer = cv2.VideoWriter(short_path, fourcc, fps, frame_size)
            if writer.isOpened():
                return writer
    # Fallback: write to safe ASCII temp folder and copy on release
    if any(ord(c) > 127 for c in path):
        temp_dir = tempfile.gettempdir()
        if os.name == 'nt' and any(ord(c) > 127 for c in temp_dir):
            public_dir = os.environ.get('PUBLIC', 'C:\\Users\\Public')
            temp_dir = os.path.join(public_dir, "HyperspectralImagingTemp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"temp_write_{uuid.uuid4().hex}.avi")
        writer = cv2.VideoWriter(temp_path, fourcc, fps, frame_size)
        if writer.isOpened():
            writer._final_dest = path
            writer._temp_path = temp_path
            orig_release = writer.release
            def custom_release():
                orig_release()
                if hasattr(writer, '_final_dest') and writer._final_dest:
                    try:
                        os.makedirs(os.path.dirname(os.path.abspath(writer._final_dest)), exist_ok=True)
                        if os.path.exists(writer._final_dest):
                            os.remove(writer._final_dest)
                        shutil.move(writer._temp_path, writer._final_dest)
                    except Exception:
                        pass
            writer.release = custom_release
            return writer
    return cv2.VideoWriter(path, fourcc, fps, frame_size)

class MainWindow(QMainWindow):
    def __init__(self, camera_thread):
        super().__init__()
        self.camera_thread = camera_thread
        self.setWindowTitle("Hyperspectral Imaging System")
        self.setMinimumSize(800, 480)
        self.captured_frame_bgr = None
        self.is_view_frozen = self.is_uploaded_mode = False
        self.current_mode = "photo"
        self.uploaded_image_bgr = None
        self.init_ui()
        self.camera_thread.frame_ready.connect(self.on_frame_ready)
        self.camera_thread.status_message.connect(self.on_status_message)
        self.on_settings_changed()
        self.camera_thread.start()
        self.showMaximized()

    def create_session_folder(self):
        sample_val = self.sample_le.text().strip()
        if not sample_val:
            sample_val = "1"
        name = f"sample{sample_val}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data_root = os.path.join(get_save_root(), "HyperspectralImaging_Data")
        self.session_folder = os.path.join(data_root, name)
        os.makedirs(self.session_folder, exist_ok=True)

    def show_custom_save_dialog(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Save Complete")
        msg.setText(f"Files auto saved to:\n{self.session_folder}")
        msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        custom_btn = msg.addButton("Save to Custom Location", QMessageBox.ButtonRole.ActionRole)
        msg.exec()

        if msg.clickedButton() == custom_btn:
            custom_dir = QFileDialog.getExistingDirectory(self, "Choose Save Location")
            if custom_dir:
                # Copy entire session folder contents to chosen location
                dest = os.path.join(custom_dir, os.path.basename(self.session_folder))
                shutil.copytree(self.session_folder, dest, dirs_exist_ok=True)
                self.status_bar.showMessage(f"Also saved to {dest}")

    def init_ui(self):
        self.setStyleSheet(self.get_stylesheet())
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        left_scroll.setMaximumWidth(280)

        left_panel = QWidget()
        left_panel.setMaximumWidth(260)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        import sys
        if hasattr(sys, '_MEIPASS'):
            sanjivani_path = os.path.join(sys._MEIPASS, "sanjivani.png")
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            sanjivani_path = os.path.join(project_root, "sanjivani.png")
            
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        px = QPixmap(sanjivani_path)
        if not px.isNull():
            logo_label.setPixmap(px.scaled(240, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("HSI")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333; qproperty-alignment: 'AlignCenter';")
        left_layout.addWidget(logo_label)
        
        gain_group = QGroupBox("Gain Settings")
        gain_layout = QVBoxLayout(gain_group)
        gain_layout.setContentsMargins(8, 8, 8, 8)
        gain_layout.setSpacing(8)
        
        slider_row = QHBoxLayout()
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(10, 500)
        self.gain_slider.setValue(10)
        self.gain_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.gain_slider.setTickInterval(50)
        self.gain_slider.valueChanged.connect(self.on_gain_changed)
        
        self.gain_value_le = QLineEdit("1.0x")
        self.gain_value_le.setStyleSheet("max-width: 50px; font-weight: bold; font-size: 13px; qproperty-alignment: 'AlignCenter';")
        self.gain_value_le.editingFinished.connect(self.on_gain_typed)
        
        slider_row.addWidget(self.gain_slider)
        slider_row.addWidget(self.gain_value_le)
        gain_layout.addLayout(slider_row)
        left_layout.addWidget(gain_group)
        
        bands_group = QGroupBox("Band Settings")
        bands_layout = QVBoxLayout(bands_group)
        bands_layout.setContentsMargins(8, 8, 8, 8)
        bands_layout.setSpacing(8)
        
        val_generic_int = QIntValidator()
        self.band_widgets = []
        self.last_valid_bands = [{"lower": 400, "upper": 450}, {"lower": 500, "upper": 550}, {"lower": 600, "upper": 650}, {"lower": 700, "upper": 750}]
        
        for idx, band_dict in enumerate(self.last_valid_bands):
            band_frame, low_le, high_le = self.create_band_control(idx, band_dict["lower"], band_dict["upper"], val_generic_int)
            bands_layout.addWidget(band_frame)
            self.band_widgets.append((low_le, high_le))
            if idx < 3:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                line.setStyleSheet("background-color: #eeeeee; max-height: 1px; border: none;")
                bands_layout.addWidget(line)
        
        self.btn_clear_bands = QPushButton("Clear Bands")
        self.btn_clear_bands.clicked.connect(self.on_clear_bands_clicked)
        bands_layout.addWidget(self.btn_clear_bands)
                
        left_layout.addWidget(bands_group)

        sample_group = QGroupBox("Sample Settings")
        sample_layout = QVBoxLayout(sample_group)
        sample_layout.setContentsMargins(8, 8, 8, 8)
        sample_layout.setSpacing(8)
        
        sample_row = QHBoxLayout()
        sample_lbl = QLabel("Sample No:")
        sample_lbl.setStyleSheet("font-weight: bold; color: #555555;")
        self.sample_le = QLineEdit("1")
        self.sample_le.setStyleSheet("font-size: 13px; padding: 4px;")
        
        sample_row.addWidget(sample_lbl)
        sample_row.addWidget(self.sample_le)
        sample_layout.addLayout(sample_row)
        left_layout.addWidget(sample_group)
        
        left_layout.addStretch()
        left_scroll.setWidget(left_panel)
        main_layout.addWidget(left_scroll)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        self.canvas_stack = QStackedWidget()
        self.canvas_label = QLabel()
        self.canvas_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas_label.setMinimumSize(100, 100)
        self.canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas_label.setStyleSheet("border: 1px solid #cccccc; background-color: #ffffff; border-radius: 4px;")
        
        self.canvas_stack.addWidget(self.canvas_label)
        self._build_split_canvas()
        right_layout.addWidget(self.canvas_stack)
        
        self._build_thumbnail_strip(right_layout)
        self._build_controls(right_layout)
        
        main_layout.addWidget(right_panel)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.set_active_mode("photo")

    def _build_split_canvas(self):
        self.split_canvas_widget = QWidget()
        split_layout = QHBoxLayout(self.split_canvas_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(8)
        
        # Left Panel (Original)
        left_split_panel = QWidget()
        left_split_layout = QVBoxLayout(left_split_panel)
        left_split_layout.setContentsMargins(0, 0, 0, 0)
        left_split_layout.setSpacing(4)
        left_title = QLabel("Original")
        left_title.setStyleSheet("font-size: 11px; color: #555555; background: transparent; font-weight: normal;")
        self.orig_canvas_label = QLabel()
        self.orig_canvas_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.orig_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orig_canvas_label.setStyleSheet("border: 1px solid #cccccc; background-color: #ffffff; border-radius: 4px;")
        left_split_layout.addWidget(left_title)
        left_split_layout.addWidget(self.orig_canvas_label)
        
        # Right Panel (Processed)
        right_split_panel = QWidget()
        right_split_layout = QVBoxLayout(right_split_panel)
        right_split_layout.setContentsMargins(0, 0, 0, 0)
        right_split_layout.setSpacing(4)
        right_title = QLabel("Processed")
        right_title.setStyleSheet("font-size: 11px; color: #555555; background: transparent; font-weight: normal;")
        self.proc_canvas_label = QLabel()
        self.proc_canvas_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.proc_canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.proc_canvas_label.setStyleSheet("border: 1px solid #cccccc; background-color: #ffffff; border-radius: 4px;")
        right_split_layout.addWidget(right_title)
        right_split_layout.addWidget(self.proc_canvas_label)
        
        split_layout.addWidget(left_split_panel)
        split_layout.addWidget(right_split_panel)
        self.canvas_stack.addWidget(self.split_canvas_widget)

    def _build_thumbnail_strip(self, right_layout):
        self.thumbnail_scroll = QScrollArea()
        self.thumbnail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumbnail_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thumbnail_scroll.setWidgetResizable(True)
        self.thumbnail_scroll.setFixedHeight(85)
        self.thumbnail_scroll.setStyleSheet("QScrollArea { border: 1px solid #cccccc; background-color: #f5f5f5; border-radius: 4px; }")
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QHBoxLayout(self.thumbnail_container)
        self.thumbnail_layout.setContentsMargins(4, 4, 4, 4)
        self.thumbnail_layout.setSpacing(8)
        self.thumbnail_layout.addStretch()
        self.thumbnail_scroll.setWidget(self.thumbnail_container)
        self.thumbnail_scroll.setVisible(False)
        right_layout.addWidget(self.thumbnail_scroll)

    def _build_controls(self, right_layout):
        controls_group = QFrame()
        controls_group.setStyleSheet("QFrame { background-color: #fcfcfc; border: 1px solid #e0e0e0; border-radius: 4px; }")
        
        # Create horizontal scroll area for controls layout
        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        controls_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        controls_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        controls_content = QWidget()
        controls_content.setStyleSheet("background: transparent;")
        controls_layout = QHBoxLayout(controls_content)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)
        self.btn_mode_photo = QPushButton("Photo")
        self.btn_mode_video = QPushButton("Video")
        self.btn_mode_photo.setCheckable(True)
        self.btn_mode_video.setCheckable(True)
        self.btn_mode_photo.clicked.connect(lambda: self.set_active_mode("photo"))
        self.btn_mode_video.clicked.connect(lambda: self.set_active_mode("video"))
        mode_layout.addWidget(self.btn_mode_photo)
        mode_layout.addWidget(self.btn_mode_video)
        controls_layout.addLayout(mode_layout)
        
        self.btn_upload = QPushButton("Upload Image")
        self.btn_upload.clicked.connect(self.on_upload_clicked)
        self.btn_resume = QPushButton("Resume Live")
        self.btn_resume.clicked.connect(self.on_resume_clicked)
        self.btn_resume.setVisible(False)
        self.btn_capture = QPushButton("Capture")
        self.btn_capture.clicked.connect(self.on_capture_clicked)
        self.btn_record = QPushButton("Record")
        self.btn_record.clicked.connect(self.on_record_clicked)
        self.btn_record.setVisible(False)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setVisible(False)
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_save.setEnabled(False)
        
        controls_layout.addWidget(self.btn_upload)
        controls_layout.addWidget(self.btn_resume)
        controls_layout.addWidget(self.btn_capture)
        controls_layout.addWidget(self.btn_record)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_save)
        
        controls_scroll.setWidget(controls_content)
        
        group_layout = QHBoxLayout(controls_group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.addWidget(controls_scroll)
        
        right_layout.addWidget(controls_group)

    def create_band_control(self, idx, def_low, def_high, val_validator):
        band_frame = QFrame()
        band_frame.setStyleSheet("QFrame { border: none; background: transparent; }")
        layout = QVBoxLayout(band_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        title = QLabel(f"Band {idx + 1}")
        title.setStyleSheet("font-weight: bold; color: #555555;")
        layout.addWidget(title)
        
        spin_btn_style = "min-width: 18px; max-width: 18px; min-height: 18px; max-height: 18px; padding: 0px; font-size: 9px; font-weight: bold; border: 1px solid #cccccc; border-radius: 2px; background-color: #ffffff; color: #555555;"
        
        # Min row layout
        row_min = QHBoxLayout()
        row_min.setContentsMargins(0, 0, 0, 0)
        row_min.setSpacing(6)
        low_lbl = QLabel("Min:")
        low_lbl.setFixedWidth(30)
        low_le = QLineEdit()
        low_le.setStyleSheet("max-width: 60px; font-size: 12px; padding: 2px;")
        low_le.setValidator(val_validator)
        low_le.setText(str(def_low))
        low_nm = QLabel("nm")
        low_nm.setFixedWidth(20)
        low_nm.setStyleSheet("font-size: 11px; color: #666666;")
        btn_low_up = QPushButton("▲")
        btn_low_up.setStyleSheet(spin_btn_style)
        btn_low_up.clicked.connect(lambda: self.adjust_band_value(low_le, 1))
        btn_low_down = QPushButton("▼")
        btn_low_down.setStyleSheet(spin_btn_style)
        btn_low_down.clicked.connect(lambda: self.adjust_band_value(low_le, -1))
        
        row_min.addWidget(low_lbl)
        row_min.addWidget(low_le)
        row_min.addWidget(low_nm)
        row_min.addWidget(btn_low_up)
        row_min.addWidget(btn_low_down)
        row_min.addStretch()
        
        # Max row layout
        row_max = QHBoxLayout()
        row_max.setContentsMargins(0, 0, 0, 0)
        row_max.setSpacing(6)
        high_lbl = QLabel("Max:")
        high_lbl.setFixedWidth(30)
        high_le = QLineEdit()
        high_le.setStyleSheet("max-width: 60px; font-size: 12px; padding: 2px;")
        high_le.setValidator(val_validator)
        high_le.setText(str(def_high))
        high_nm = QLabel("nm")
        high_nm.setFixedWidth(20)
        high_nm.setStyleSheet("font-size: 11px; color: #666666;")
        btn_high_up = QPushButton("▲")
        btn_high_up.setStyleSheet(spin_btn_style)
        btn_high_up.clicked.connect(lambda: self.adjust_band_value(high_le, 1))
        btn_high_down = QPushButton("▼")
        btn_high_down.setStyleSheet(spin_btn_style)
        btn_high_down.clicked.connect(lambda: self.adjust_band_value(high_le, -1))
        
        row_max.addWidget(high_lbl)
        row_max.addWidget(high_le)
        row_max.addWidget(high_nm)
        row_max.addWidget(btn_high_up)
        row_max.addWidget(btn_high_down)
        row_max.addStretch()
        
        low_le.editingFinished.connect(lambda: self.on_editing_finished(low_le, idx, "lower"))
        high_le.editingFinished.connect(lambda: self.on_editing_finished(high_le, idx, "upper"))
        
        layout.addLayout(row_min)
        layout.addLayout(row_max)
        
        return band_frame, low_le, high_le

    def on_gain_changed(self, value):
        self.gain_value_le.setText(f"{value / 10.0:.1f}x")
        self.on_settings_changed()

    def on_gain_typed(self):
        try:
            val = max(1.0, min(50.0, float(self.gain_value_le.text().replace("x", ""))))
            self.gain_slider.blockSignals(True)
            self.gain_slider.setValue(int(val * 10))
            self.gain_slider.blockSignals(False)
            self.gain_value_le.setText(f"{val:.1f}x")
            self.on_settings_changed()
        except ValueError:
            self.gain_value_le.setText(f"{self.gain_slider.value() / 10.0:.1f}x")

    def adjust_band_value(self, line_edit, delta):
        val = int(line_edit.text()) if line_edit.text() else 0
        line_edit.setText(str(val + delta))
        line_edit.editingFinished.emit()
        self.on_settings_changed()

    def on_editing_finished(self, line_edit, band_idx, limit_type):
        if line_edit.text():
            try: self.last_valid_bands[band_idx][limit_type] = int(line_edit.text())
            except ValueError: pass
        self.on_settings_changed()

    def _get_bands(self):
        bands = []
        for low_le, high_le in self.band_widgets:
            if low_le.text() and high_le.text():
                try: bands.append({"lower": int(low_le.text()), "upper": int(high_le.text())})
                except ValueError: pass
        return bands

    def _set_pixmap(self, label, frame_rgb):
        clipped = np.clip(frame_rgb, 10, 255)
        h, w, ch = clipped.shape
        q = QImage(clipped.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
        tw, th = self.width() - 340, self.height() - 180
        px = QPixmap.fromImage(q).scaled(tw, th, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(px.copy((px.width() - tw) // 2, (px.height() - th) // 2, tw, th))



    def on_settings_changed(self, *args):
        gain = float(self.gain_slider.value()) / 10.0
        bands = self._get_bands()
        self.camera_thread.update_settings(gain, bands)
        self.check_band_warnings(bands)
        if self.is_uploaded_mode:
            self.process_and_display_uploaded_image()
        elif self.is_view_frozen and self.current_mode == "photo":
            if hasattr(self, "captured_raw_frame_bgr") and self.captured_raw_frame_bgr is not None:
                try:
                    if not bands:
                        processed_bgr = self.captured_raw_frame_bgr.copy()
                    else:
                        processed_bgr = self.camera_thread.model.process_frame(self.captured_raw_frame_bgr, gain=gain, bands=bands)
                    self.captured_frame_bgr = processed_bgr
                    self._show_split_view(self.captured_raw_frame_bgr, processed_bgr)
                except Exception: pass

    def on_clear_bands_clicked(self):
        for low_le, high_le in self.band_widgets:
            low_le.clear()
            high_le.clear()
        self.on_settings_changed()

    def check_band_warnings(self, bands):
        warning_active = False
        for b in bands:
            if (320 <= b["lower"] <= 420) or (320 <= b["upper"] <= 420):
                warning_active = True
                break
        if warning_active:
            self.status_bar.showMessage("Band range 320-420nm may produce low output — try 420nm and above")

    def set_active_mode(self, mode):
        self.current_mode = mode
        if self.is_view_frozen and not self.is_uploaded_mode:
            self.on_resume_clicked()
        is_photo = mode == "photo"
        self.btn_mode_photo.setProperty("active", str(is_photo).lower())
        self.btn_mode_video.setProperty("active", str(not is_photo).lower())
        self.btn_capture.setVisible(is_photo)
        self.btn_record.setVisible(not is_photo)
        self.btn_stop.setVisible(not is_photo)
        self.btn_save.setEnabled(False)
        self.btn_mode_photo.style().unpolish(self.btn_mode_photo)
        self.btn_mode_photo.style().polish(self.btn_mode_photo)
        self.btn_mode_video.style().unpolish(self.btn_mode_video)
        self.btn_mode_video.style().polish(self.btn_mode_video)
        self.status_bar.showMessage(f"Switched to {mode.capitalize()} Mode.")

    def _set_recording_state(self, active):
        self.btn_record.setEnabled(not active)
        self.btn_stop.setEnabled(active)
        self.btn_save.setEnabled(not active)
        self.btn_mode_photo.setEnabled(not active)
        self.btn_mode_video.setEnabled(not active)

    def on_frame_ready(self, frame_rgb):
        if not self.is_view_frozen:
            self._set_pixmap(self.canvas_label, frame_rgb)

    def on_status_message(self, msg):
        self.status_bar.showMessage(msg)

    def _show_split_view(self, orig_bgr, proc_bgr):
        self.canvas_stack.setCurrentIndex(1)
        if not hasattr(self, "_split_cw") or self._split_cw is None:
            self._split_cw = (self.width() - 340) // 2
            self._split_ch = self.height() - 180
            self.orig_canvas_label.setMaximumSize(self._split_cw, self._split_ch)
            self.proc_canvas_label.setMaximumSize(self._split_cw, self._split_ch)
        cw, ch_val = self._split_cw, self._split_ch
        for label, bgr in [(self.orig_canvas_label, orig_bgr), (self.proc_canvas_label, proc_bgr)]:
            rgb = cv2.cvtColor(np.clip(bgr, 10, 255), cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            q = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            px = QPixmap.fromImage(q).scaled(cw, ch_val, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(px.copy((px.width() - cw) // 2, (px.height() - ch_val) // 2, cw, ch_val))

    def on_capture_clicked(self):
        self.create_session_folder()
        full_res_bgr = self.camera_thread.capture_full_resolution()
        if full_res_bgr is not None:
            self.camera_thread.pause_camera() # Turn off camera completely
            self.captured_raw_frame_bgr = self.camera_thread.last_raw_frame_full.copy()
            self.captured_frame_bgr = full_res_bgr
            self.is_view_frozen = True
            self.btn_resume.setVisible(True)
            self.btn_save.setEnabled(True)
            self._show_split_view(self.captured_raw_frame_bgr, full_res_bgr)
            
            # Save original
            cv2.imwrite(os.path.join(self.session_folder, "original.png"), self.captured_raw_frame_bgr)
            # Save processed
            cv2.imwrite(os.path.join(self.session_folder, "processed.png"), full_res_bgr)
            self.status_bar.showMessage(f"Saved to {self.session_folder}")
            self.show_custom_save_dialog()
        else:
            self.status_bar.showMessage("Error: No frame captured yet or camera offline.")

    def on_record_clicked(self):
        self.create_session_folder()
        self._set_recording_state(True)
        self.status_bar.showMessage("Recording video... Capturing live stream frames. Press Stop.")
        self.camera_thread.start_recording()

    def on_stop_clicked(self):
        self.camera_thread.stop_recording()
        self.camera_thread.pause_camera() # Turn off camera completely
        self._set_recording_state(False)
        
        has_saved = False
        if os.path.exists(self.camera_thread.temp_video_path):
            try:
                shutil.copy2(self.camera_thread.temp_video_path, os.path.join(self.session_folder, "processed_video.avi"))
                has_saved = True
            except Exception: pass
        if hasattr(self.camera_thread, 'temp_raw_video_path') and os.path.exists(self.camera_thread.temp_raw_video_path):
            try:
                shutil.copy2(self.camera_thread.temp_raw_video_path, os.path.join(self.session_folder, "original_video.avi"))
                has_saved = True
            except Exception: pass
        elif hasattr(self.camera_thread, 'temp_video_orig_path') and os.path.exists(self.camera_thread.temp_video_orig_path):
            try:
                shutil.copy2(self.camera_thread.temp_video_orig_path, os.path.join(self.session_folder, "original_video.avi"))
                has_saved = True
            except Exception: pass
            
        if has_saved:
            self.status_bar.showMessage(f"Video saved to {self.session_folder}")
            self.show_custom_save_dialog()
        else:
            self.status_bar.showMessage("Error: Recorded video files not found.")
            
        self.is_view_frozen = True
        self.btn_resume.setVisible(True)
        self._start_video_replay()

    def on_save_clicked(self):
        if self.is_uploaded_mode:
            if hasattr(self, "uploaded_images") and self.uploaded_images:
                self.create_session_folder()
                gain = float(self.gain_slider.value()) / 10.0
                bands = self._get_bands()
                for i, (fp, img) in enumerate(self.uploaded_images):
                    processed = self.camera_thread.model.process_frame(img, gain=gain, bands=bands)
                    cv2.imwrite(os.path.join(self.session_folder, f"original_{i+1}.png"), img)
                    cv2.imwrite(os.path.join(self.session_folder, f"processed_{i+1}.png"), processed)
                self.status_bar.showMessage(f"Saved {len(self.uploaded_images)} pairs to {self.session_folder}")
                self.show_custom_save_dialog()
        elif self.current_mode == "photo":
            if self.captured_frame_bgr is not None:
                self.create_session_folder()
                cv2.imwrite(os.path.join(self.session_folder, "original.png"), self.captured_raw_frame_bgr)
                cv2.imwrite(os.path.join(self.session_folder, "processed.png"), self.captured_frame_bgr)
                self.status_bar.showMessage(f"Saved to {self.session_folder}")
                self.show_custom_save_dialog()
        elif self.current_mode == "video":
            # Stop and release replay captures to avoid Windows file lock issues
            was_replaying = False
            if hasattr(self, "replay_timer") and self.replay_timer.isActive():
                self.replay_timer.stop()
                was_replaying = True
            if hasattr(self, "replay_cap") and self.replay_cap is not None:
                self.replay_cap.release()
                self.replay_cap = None
            if hasattr(self, "replay_cap_proc") and self.replay_cap_proc is not None:
                self.replay_cap_proc.release()
                self.replay_cap_proc = None

            if hasattr(self.camera_thread, 'temp_video_orig_path') and os.path.exists(self.camera_thread.temp_video_orig_path):
                video_orig_path = self.camera_thread.temp_video_orig_path
            elif hasattr(self.camera_thread, 'temp_raw_video_path') and os.path.exists(self.camera_thread.temp_raw_video_path):
                video_orig_path = self.camera_thread.temp_raw_video_path
            else:
                video_orig_path = None

            video_proc_path = getattr(self.camera_thread, 'temp_video_path', None)

            if video_orig_path:
                self.create_session_folder()
                dest_orig = os.path.join(self.session_folder, "original_video.avi")
                dest_proc = os.path.join(self.session_folder, "processed_video.avi")
                try:
                    shutil.copy2(video_orig_path, dest_orig)
                except Exception:
                    pass
                
                copied_live_proc = False
                if video_proc_path and os.path.exists(video_proc_path):
                    try:
                        shutil.copy2(video_proc_path, dest_proc)
                        copied_live_proc = True
                    except Exception:
                        pass
                
                if not copied_live_proc:
                    # Fallback to reprocessing raw video if the pre-recorded processed file is missing/inaccessible
                    gain = float(self.gain_slider.value()) / 10.0
                    bands = self._get_bands()
                    cap = safe_video_capture(video_orig_path)
                    if cap.isOpened():
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        out = None
                        while True:
                            ret, frame = cap.read()
                            if not ret: break
                            if out is None:
                                h, w = frame.shape[:2]
                                out = safe_video_writer(dest_proc, fourcc, 15.0, (w, h))
                            if not bands:
                                proc = frame.copy()
                            else:
                                proc = self.camera_thread.model.process_frame(frame, gain=gain, bands=bands)
                            out.write(proc)
                        if out is not None: out.release()
                        cap.release()
                        
                self.status_bar.showMessage(f"Video saved to {self.session_folder}")
                self.show_custom_save_dialog()
            else:
                self.status_bar.showMessage("Error: Recorded video file not found.")

            # Restart replay if it was active
            if was_replaying:
                self._start_video_replay()

    def on_upload_clicked(self):
        self.camera_thread.pause_camera() # Turn off camera completely
        fps, _ = QFileDialog.getOpenFileNames(self, "Upload Images", "", "Images (*.png *.jpg *.jpeg)")
        if fps:
            self.clear_thumbnails()
            self.uploaded_images = []
            for fp in fps:
                img = safe_imread(fp)
                if img is not None: self.uploaded_images.append((fp, img))
            if self.uploaded_images:
                self.canvas_stack.setCurrentIndex(1)
                self.is_uploaded_mode = self.is_view_frozen = True
                self.btn_resume.setVisible(True)
                self.btn_save.setEnabled(True)
                self.thumbnail_scroll.setVisible(True)
                self.populate_thumbnails()
                self.select_uploaded_image(0)
                self.status_bar.showMessage(f"Uploaded {len(self.uploaded_images)} images. Click a thumbnail to process.")
            else:
                self.status_bar.showMessage("Error: Failed to load selected images.")
        else:
            self.camera_thread.resume_camera() # Turn camera back on if cancelled
            self.status_bar.showMessage("Upload cancelled. Camera active.")

    def populate_thumbnails(self):
        while self.thumbnail_layout.count():
            item = self.thumbnail_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.thumbnail_labels = []
        for idx, (fp, img) in enumerate(self.uploaded_images):
            thumb_bgr = cv2.resize(img, (80, 60), interpolation=cv2.INTER_AREA)
            thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
            h, w, ch = thumb_rgb.shape
            q_img = QImage(thumb_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            lbl = QLabel()
            lbl.setPixmap(QPixmap.fromImage(q_img))
            lbl.setFixedSize(80, 60)
            lbl.setStyleSheet("border: 2px solid transparent; border-radius: 2px;")
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda e, i=idx: self.select_uploaded_image(i)
            self.thumbnail_layout.addWidget(lbl)
            self.thumbnail_labels.append(lbl)
        self.thumbnail_layout.addStretch()

    def select_uploaded_image(self, idx):
        if not hasattr(self, 'uploaded_images') or idx < 0 or idx >= len(self.uploaded_images):
            return
        self.selected_uploaded_idx = idx
        for i, lbl in enumerate(self.thumbnail_labels):
            lbl.setStyleSheet("border: 2px solid #333333; border-radius: 2px;" if i == idx else "border: 2px solid transparent; border-radius: 2px;")
        self.uploaded_image_bgr = self.uploaded_images[idx][1]
        self.process_and_display_uploaded_image()

    def clear_thumbnails(self):
        self.uploaded_images, self.selected_uploaded_idx = [], -1
        self.thumbnail_scroll.setVisible(False)
        [self.thumbnail_layout.takeAt(0).widget().deleteLater() for _ in range(self.thumbnail_layout.count()) if self.thumbnail_layout.itemAt(0) and self.thumbnail_layout.itemAt(0).widget()]

    def on_resume_clicked(self):
        self.canvas_stack.setCurrentIndex(0)
        self.clear_thumbnails()
        self.uploaded_image_bgr = None
        self.is_uploaded_mode = self.is_view_frozen = False
        self.btn_resume.setVisible(False)
        self.btn_save.setEnabled(False)
        if hasattr(self, "replay_timer"): self.replay_timer.stop()
        if hasattr(self, "replay_cap") and self.replay_cap is not None:
            self.replay_cap.release()
            self.replay_cap = None
        if hasattr(self, "replay_cap_proc") and self.replay_cap_proc is not None:
            self.replay_cap_proc.release()
            self.replay_cap_proc = None
        self._split_cw = None
        self._split_ch = None
        self.orig_canvas_label.setMaximumSize(16777215, 16777215)
        self.proc_canvas_label.setMaximumSize(16777215, 16777215)
        self.camera_thread.resume_camera() # Turn camera back on
        self.status_bar.showMessage("Live feed resumed.")

    def process_and_display_uploaded_image(self):
        if self.uploaded_image_bgr is not None and hasattr(self.camera_thread, 'model') and self.camera_thread.model is not None:
            gain = float(self.gain_slider.value()) / 10.0
            bands = self._get_bands()
            try:
                if not bands:
                    processed_bgr = self.uploaded_image_bgr.copy()
                else:
                    processed_bgr = self.camera_thread.model.process_frame(self.uploaded_image_bgr, gain=gain, bands=bands)
                self.captured_frame_bgr = processed_bgr
                self._show_split_view(self.uploaded_image_bgr, processed_bgr)
                self.status_bar.showMessage(f"Processed image @ {gain:.1f}x")
            except Exception: pass

    def closeEvent(self, event):
        self.camera_thread.stop()
        self.camera_thread.wait()
        if hasattr(self, "replay_timer"): self.replay_timer.stop()
        if hasattr(self, "replay_cap") and self.replay_cap is not None:
            self.replay_cap.release()
        if hasattr(self, "replay_cap_proc") and self.replay_cap_proc is not None:
            self.replay_cap_proc.release()
        if os.path.exists(self.camera_thread.temp_video_path):
            try: os.remove(self.camera_thread.temp_video_path)
            except Exception: pass
        if hasattr(self.camera_thread, 'temp_video_orig_path') and os.path.exists(self.camera_thread.temp_video_orig_path):
            try: os.remove(self.camera_thread.temp_video_orig_path)
            except Exception: pass
        if hasattr(self.camera_thread, 'temp_raw_video_path') and os.path.exists(self.camera_thread.temp_raw_video_path):
            try: os.remove(self.camera_thread.temp_raw_video_path)
            except Exception: pass
        event.accept()

    def _start_video_replay(self):
        if hasattr(self, "replay_timer") and self.replay_timer.isActive(): self.replay_timer.stop()
        if hasattr(self, "replay_cap") and self.replay_cap is not None: self.replay_cap.release()
        if hasattr(self, "replay_cap_proc") and self.replay_cap_proc is not None: self.replay_cap_proc.release()
        
        path = getattr(self.camera_thread, 'temp_video_orig_path', None) or getattr(self.camera_thread, 'temp_raw_video_path', None)
        path_proc = getattr(self.camera_thread, 'temp_video_path', None)
        
        self.replay_cap = safe_video_capture(path) if path else None
        self.replay_cap_proc = safe_video_capture(path_proc) if (path_proc and os.path.exists(path_proc)) else None
        
        if self.replay_cap:
            self.replay_timer = QTimer(self)
            self.replay_timer.timeout.connect(self._replay_next_frame)
            self.replay_timer.start(33)

    def _replay_next_frame(self):
        if hasattr(self, "replay_cap") and self.replay_cap.isOpened():
            ret, frame = self.replay_cap.read()
            if ret:
                proc = None
                if hasattr(self, "replay_cap_proc") and self.replay_cap_proc is not None and self.replay_cap_proc.isOpened():
                    ret_proc, frame_proc = self.replay_cap_proc.read()
                    if ret_proc:
                        proc = frame_proc
                
                if proc is None:
                    gain = float(self.gain_slider.value()) / 10.0
                    bands = self._get_bands()
                    if not bands:
                        proc = frame.copy()
                    else:
                        proc = self.camera_thread.model.process_frame(frame, gain=gain, bands=bands)
                
                self._show_split_view(frame, proc)
            else: self.replay_timer.stop()

    def get_stylesheet(self):
        return "QWidget{font-family:'Segoe UI',Arial;color:#333;background:#fff;}QGroupBox{border:1px solid #ccc;border-radius:4px;margin-top:8px;padding-top:12px;font-weight:bold;background:#fff;}QGroupBox::title{subcontrol-origin:margin;subcontrol-position:top left;left:8px;padding:0 4px;background:#fff;}QSlider::groove:horizontal{border:1px solid #ccc;height:6px;background:#f0f0f0;border-radius:3px;}QSlider::handle:horizontal{background:#fff;border:1px solid #777;width:14px;height:14px;margin:-4px 0;border-radius:7px;}QSlider::handle:horizontal:hover{background:#eee;border-color:#333;}QPushButton{background:#fff;border:1px solid #999;border-radius:4px;padding:4px 8px;font-size:11px;font-weight:500;}QPushButton:hover{background:#f5f5f5;border-color:#666;}QPushButton:pressed{background:#e5e5e5;}QPushButton:disabled{background:#f9f9f9;color:#ccc;border:1px solid #e0e0e0;}QPushButton[active=\"true\"]{background:#e5e5e5;border:2px solid #333;font-weight:bold;}QLineEdit{border:1px solid #ccc;border-radius:2px;padding:2px;background:#fff;}QLineEdit:focus{border:1px solid #666;}QStatusBar{background:#f9f9f9;border-top:1px solid #ddd;color:#333;}"
