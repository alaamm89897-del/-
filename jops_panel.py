from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QListWidget, QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from firebase_admin import db
from session_handler import load_session
from firebase_connection import jref


class JobManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Manager")
        self.setMinimumWidth(600)
        self.current_theme = "dark"

        session = load_session()
        self.company_name = session.get("company_name", "")
        if not self.company_name:
            QMessageBox.critical(self, "Session Error", "No company session found.")
            return

        self.layout = QVBoxLayout()

        # Header layout (title + theme toggle)
        header_layout = QHBoxLayout()
        self.title = QLabel(f"Welcome, {self.company_name}")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(self.title)

        self.toggle_button = QPushButton("Switch to Light Mode")
        self.toggle_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.toggle_button, alignment=Qt.AlignRight)

        self.layout.addLayout(header_layout)

        self.job_list = QListWidget()
        self.layout.addWidget(self.job_list)

        self.input_layout = QHBoxLayout()
        self.job_name_input = QLineEdit()
        self.job_name_input.setPlaceholderText("Job Title")
        self.input_layout.addWidget(self.job_name_input)

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Important Keywords (comma separated)")
        self.input_layout.addWidget(self.keywords_input)

        self.layout.addLayout(self.input_layout)

        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Job")
        self.add_button.clicked.connect(self.add_job)
        self.button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_job)
        self.button_layout.addWidget(self.remove_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        self.load_jobs()
        self.apply_theme(self.current_theme)

    def apply_theme(self, mode):
        if mode == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #e0e0e0;
                    font-family: Arial;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #1f1f1f;
                    border: 1px solid #333;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px;
                    color: #fff;
                }
                QListWidget {
                    background-color: #1a1a1a;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 4px;
                }
            """)
            self.toggle_button.setText("Switch to Light Mode")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f4f4f4;
                    color: #202020;
                    font-family: Arial;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #eeeeee;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    padding: 6px;
                    color: #000;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    padding: 4px;
                }
            """)
            self.toggle_button.setText("Switch to Dark Mode")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(self.current_theme)

    def load_jobs(self):
        self.job_list.clear()
        jref = db.reference('jops')
        all_jobs = jref.get()

        if not all_jobs:
            return

        self.jobs_dict = {}
        for key, job in all_jobs.items():
            if job.get("company_name") == self.company_name:
                display = f"{job.get('name')} - Keywords: {job.get('value')}"
                self.job_list.addItem(display)
                self.jobs_dict[display] = key

    def add_job(self):
        name = self.job_name_input.text().strip()
        value = self.keywords_input.text().strip()
        if not name or not value:
            QMessageBox.warning(self, "Missing Info", "Job title and keywords are required.")
            return

        db.reference("jops").push().set({
            "name": name,
            "value": value,
            "company_name": self.company_name
        })

        self.job_name_input.clear()
        self.keywords_input.clear()
        self.load_jobs()
        QMessageBox.information(self, "Success", "Job added successfully!")

    def remove_selected_job(self):
        selected = self.job_list.currentItem()
        if selected:
            key = self.jobs_dict.get(selected.text())
            if key:
                db.reference(f"jops/{key}").delete()
                self.load_jobs()
        else:
            QMessageBox.information(self, "No Selection", "Please select a job to remove.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = JobManager()
    window.show()
    sys.exit(app.exec_())
