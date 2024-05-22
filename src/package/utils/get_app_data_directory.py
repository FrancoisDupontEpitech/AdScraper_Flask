import os
import platform

def get_app_data_directory(app_name):
    """Get the application data directory based on the operating system."""
    if platform.system() == "Windows":
        base_dir = os.environ['APPDATA']
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support')
    else:  # Assuming Linux/Unix
        base_dir = os.path.expanduser('~/.local/share')

    app_data_directory = os.path.join(base_dir, app_name)
    os.makedirs(app_data_directory, exist_ok=True)
    return app_data_directory