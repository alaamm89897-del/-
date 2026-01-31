# main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from firebase_admin import db
fimport EnhancedAdminPage as AdminPage  # استخدام النسخة المحسنة
from companies.session_handler import save_session


class CompanyLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Company Login")
        self.setFixedSize(400, 340)
        self.setStyleSheet(self.load_styles())
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)

        title = QLabel("Company Login")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Company Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setStyleSheet("background-color: #2c8c4c;")

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.login_button)
        main_layout.addWidget(self.signup_button)
        main_layout.addWidget(self.error_label)

        self.setLayout(main_layout)

        self.login_button.clicked.connect(self.handle_login)
        self.signup_button.clicked.connect(self.open_signup_window)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Please enter email and password.")
            return

        try:
            ref = db.reference("companies")
            companies = ref.get()

            if companies:
                for key, value in companies.items():
                    stored_email = value.get("email")
                    stored_password = value.get("password")
                    stored_name = value.get("company_name")
                    if stored_email == email and stored_password == password:
                        self.error_label.setStyleSheet("color: lightgreen;")
                        self.error_label.setText("Login successful.")
                        save_session(stored_name,stored_email,stored_password)
                        self.open_admin_window()  #Open admin window
                        return

            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Invalid email or password.")
        except Exception as e:
            self.error_label.setText(f"Error: {str(e)}")
            print("Login error:", e)

    def open_admin_window(self):
        from enhanced_admin import EnhancedAdminPage
self.admin_window = EnhancedAdminPage()
        self.admin_window.show()
        self.hide()  # Hide login window instead of closing it

    def open_signup_window(self):
        self.signup_window = CompanySignUp()
        self.signup_window.show()
        self.hide()

    def load_styles(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: Arial;
        }

        QLineEdit {
            padding: 10px;
            border: 1px solid #3e3e50;
            border-radius: 8px;
            background-color: #2c2c3c;
            color: #ffffff;
        }

        QPushButton {
            background-color: #5c7cfa;
            color: white;
            padding: 10px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #4c6ef5;
        }

        QPushButton:pressed {
            background-color: #3b5bdb;
        }
        """


class CompanySignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Company Sign Up")
        self.setFixedSize(400, 400)
        self.setStyleSheet(self.load_styles())
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)

        title = QLabel("Create Account")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Company Name")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Company Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setStyleSheet("background-color: #2c8c4c;")

        self.back_button = QPushButton("Back to Login")

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(self.company_name_input)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.signup_button)
        main_layout.addWidget(self.back_button)
        main_layout.addWidget(self.error_label)

        self.setLayout(main_layout)

        self.signup_button.clicked.connect(self.handle_signup)
        self.back_button.clicked.connect(self.go_back_to_login)

    def handle_signup(self):
        company_name = self.company_name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not company_name or not email or not password:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("All fields are required.")
            return

        if len(password) < 6:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Password must be at least 6 characters.")
            return

        try:
            ref = db.reference("companies")
            companies = ref.get()

            if companies:
                for key, value in companies.items():
                    stored_email = value.get("email")
                    if stored_email == email:
                        self.error_label.setStyleSheet("color: red;")
                        self.error_label.setText("Email already registered.")
                        return

            ref.push({
                "company_name": company_name,
                "email": email,
                "password": password
            })

            self.error_label.setStyleSheet("color: lightgreen;")
            self.error_label.setText("Sign up successful! You can now log in.")

            self.company_name_input.clear()
            self.email_input.clear()
            self.password_input.clear()

        except Exception as e:
            self.error_label.setText(f"Error during signup: {str(e)}")
            print("Signup error:", e)

    def go_back_to_login(self):
        self.login_window = CompanyLogin()
        self.login_window.show()
        self.close()

    def load_styles(self):
        return """
        QWidget {
            background-color: #1e1e2f;
            color: #ffffff;
            font-family: Arial;
        }

        QLineEdit {
            padding: 10px;
            border: 1px solid #3e3e50;
            border-radius: 8px;
            background-color: #2c2c3c;
            color: #ffffff;
        }

        QPushButton {
            background-color: #5c7cfa;
            color: white;
            padding: 10px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #4c6ef5;
        }

        QPushButton:pressed {
            background-color: #3b5bdb;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompanyLogin()
    window.show()
    sys.exit(app.exec_())