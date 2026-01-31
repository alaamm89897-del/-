# utils.py - Utility functions for file paths
import os
import sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Args:
        relative_path: المسار النسبي للملف
        
    Returns:
        المسار المطلق
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(f"🎁 Running as packaged app, base: {base_path}")
    except Exception:
        # Running in development
        base_path = os.path.abspath(".")
        print(f"💻 Running in development mode, base: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    print(f"📂 Resource path for '{relative_path}': {full_path}")
    
    return full_path


def get_app_directory():
    """
    الحصول على مجلد التطبيق
    
    Returns:
        مسار مجلد التطبيق
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def ensure_directory_exists(directory):
    """
    التأكد من وجود مجلد، إنشاؤه إذا لم يكن موجوداً
    
    Args:
        directory: مسار المجلد
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ Created directory: {directory}")
    else:
        print(f"📁 Directory exists: {directory}")


# للاختبار
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Utils Module Test")
    print("="*50 + "\n")
    
    # اختبار resource_path
    print("Testing resource_path:")
    test_file = "recruitmentify.json"
    path = resource_path(test_file)
    print(f"Result: {path}")
    print(f"Exists: {os.path.exists(path)}\n")
    
    # اختبار get_app_directory
    print("Testing get_app_directory:")
    app_dir = get_app_directory()
    print(f"App Directory: {app_dir}\n")
    
    print("="*50)