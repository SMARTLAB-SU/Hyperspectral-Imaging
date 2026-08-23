import os
import sys
import traceback

def show_error_message(title, message):
    """
    Shows a critical error messagebox using PyQt6 if available, falling back
    to Windows native MessageBoxW or standard error print to avoid silent crashes.
    """
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # 0x10 is MB_ICONERROR
        except Exception:
            print(f"{title}: {message}", file=sys.stderr)

# Add shared directory to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "shared"))
if SHARED_DIR not in sys.path:
    sys.path.append(SHARED_DIR)

try:
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from camera.camera_thread import CameraThread
except Exception as e:
    show_error_message(
        "Startup Error - Missing Dependency", 
        f"Failed to import required application libraries.\n\n"
        f"Error Details: {str(e)}\n\n"
        f"Please ensure all required packages are correctly packaged or install the "
        f"Microsoft Visual C++ Redistributable on this computer.\n\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    sys.exit(1)

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, supporting both local development
    and PyInstaller packaged executable execution environments.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts bundled files to a temporary folder sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # Local development environment: resolve from the shared directory
    return os.path.join(SHARED_DIR, relative_path)

def create_desktop_shortcut():
    """
    Creates a desktop shortcut pointing to the executable when running
    in a packaged PyInstaller environment.
    Supports OneDrive-synced Desktops and includes a PowerShell fallback.
    """
    import sys
    import os
    if getattr(sys, 'frozen', False):
        # 1. Resolve the correct Desktop path (handling OneDrive redirection)
        desktop = None
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            desktop = shell.SpecialFolders('Desktop')
        except Exception:
            pass
            
        if not desktop:
            # Fallback path checking
            user_profile = os.environ.get("USERPROFILE", "")
            onedrive_desktop = os.path.join(user_profile, "OneDrive", "Desktop")
            if os.path.exists(onedrive_desktop):
                desktop = onedrive_desktop
            else:
                desktop = os.path.join(user_profile, "Desktop")
                
        shortcut_path = os.path.join(desktop, "Hyperspectral Imaging System.lnk")
        data_shortcut_path = os.path.join(desktop, "Hyperspectral Imaging System Data.lnk")
        
        exe_path = os.path.abspath(sys.executable)
        working_dir = os.path.dirname(exe_path)
        data_dir = os.path.join(working_dir, "HyperspectralImaging_Data")
        os.makedirs(data_dir, exist_ok=True)
        
        # 2. Try native COM shortcut creation
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            
            # App Shortcut
            if not os.path.exists(shortcut_path):
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.TargetPath = exe_path
                shortcut.WorkingDirectory = working_dir
                shortcut.IconLocation = exe_path
                shortcut.save()
                
            # Data Folder Shortcut
            if not os.path.exists(data_shortcut_path):
                shortcut_data = shell.CreateShortCut(data_shortcut_path)
                shortcut_data.TargetPath = data_dir
                shortcut_data.WorkingDirectory = working_dir
                shortcut_data.save()
            return
        except Exception:
            pass
            
        # 3. Fallback to PowerShell command if win32com fails
        try:
            ps_command = ""
            if not os.path.exists(shortcut_path):
                ps_command += (
                    f'$WshShell = New-Object -ComObject WScript.Shell; '
                    f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
                    f'$Shortcut.TargetPath = "{exe_path}"; '
                    f'$Shortcut.WorkingDirectory = "{working_dir}"; '
                    f'$Shortcut.Save(); '
                )
            if not os.path.exists(data_shortcut_path):
                ps_command += (
                    f'$WshShell = New-Object -ComObject WScript.Shell; '
                    f'$ShortcutData = $WshShell.CreateShortcut("{data_shortcut_path}"); '
                    f'$ShortcutData.TargetPath = "{data_dir}"; '
                    f'$ShortcutData.WorkingDirectory = "{working_dir}"; '
                    f'$ShortcutData.Save(); '
                )
            if ps_command:
                import subprocess
                subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
        except Exception:
            pass

def main():
    try:
        # Create desktop shortcut automatically on startup
        create_desktop_shortcut()

        # Resolve weight and calibration paths dynamically
        weight_npz_path = get_resource_path("weight.npz")
        cr_weights_path = get_resource_path("cr_weights")
        
        # Simple debugging output
        print("Hyperspectral Desktop App starting...")
        print(f"Loading weight file from: {weight_npz_path}")
        print(f"Loading calibration directory from: {cr_weights_path}")
        
        # Quick integrity checks with user-facing alerts
        if not os.path.exists(weight_npz_path):
            show_error_message(
                "Missing Resource File",
                f"Critical Error: weight.npz not found!\n\n"
                f"Expected path: {weight_npz_path}\n\n"
                f"Please verify that the weight file is bundled properly."
            )
            sys.exit(1)
            
        if not os.path.exists(cr_weights_path):
            show_error_message(
                "Missing Calibration Folder",
                f"Critical Error: cr_weights folder not found!\n\n"
                f"Expected path: {cr_weights_path}\n\n"
                f"Please verify that the calibration folder is bundled properly."
            )
            sys.exit(1)
            
        # Start QApplication
        app = QApplication(sys.argv)
        
        # Create the background camera and processing thread
        camera_thread = CameraThread(weight_npz_path, cr_weights_path)
        
        # Create and display the main window
        window = MainWindow(camera_thread)
        window.show()
        
        # Run the Qt main event loop
        sys.exit(app.exec())
    except Exception as e:
        show_error_message(
            "Application Crash",
            f"An unexpected error occurred during application execution:\n\n"
            f"Error Details: {str(e)}\n\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()

