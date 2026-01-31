import json
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SESSION_FILE = "session.json"

def save_session(company_name, email, password):
    session_file = get_resource_path(SESSION_FILE)
    with open(session_file, "w") as f:
        json.dump({
            "company_name": company_name,
            "email": email,
            "password": password
        }, f)

def load_session():
    session_file = get_resource_path(SESSION_FILE)
    try:
        with open(session_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def clear_session():
    session_file = get_resource_path(SESSION_FILE)
    if os.path.exists(session_file):
        os.remove(session_file)
