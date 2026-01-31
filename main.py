import re
import os
import sys
from firebase_admin import db
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QHBoxLayout, QWidget, QComboBox, QDialog, QMessageBox, QProgressBar,
    QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from dotenv import load_dotenv
import google.generativeai as genai

# Import custom modules
from firebase_connection import ref, cref, jref
from functions import pdf_push_to_ai, push_customer_data_to_firebase

# Load environment variables
load_dotenv()

# Get API key
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        gemini_api_key = line.strip().split('=', 1)[1].strip('"\'')
                        break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    if not gemini_api_key:
        gemini_api_key = "AIzaSyAldaZINHy1iNK88iY5fG0XQ5paBNfARXY"
        print("⚠️ Using fallback API key")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)


class TextProcessor:
    @staticmethod
    def stripText(aiout):
        rating_match = re.search(r'Rating\s*:\s*(\d+)', aiout)
        summary_match = re.search(r'Summary\s*:\s*(.*)', aiout, re.DOTALL)
        
        if rating_match:
            rating = int(rating_match.group(1).strip())
        else:
            rating = 0
            print("⚠️ Rating not found, using default 0")
        
        if summary_match:
            summary = summary_match.group(1).strip()
        else:
            summary = "No summary available"
            print("⚠️ Summary not found")
        
        return [rating, summary]


class ModernResumeApp(QWidget):
    """تطبيق تقديم السيرة الذاتية المحسّن"""
    
    rating = None
    summary = None
    filepath = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle('🎯 Recruitmentify - تقديم السيرة الذاتية')
        self.setGeometry(100, 100, 1000, 700)
        self.dark_mode = False
        self.setAcceptDrops(True)
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        """إنشاء الواجهة"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # الجزء الأيسر - معلومات ترحيبية
        left_panel = self.create_welcome_panel()
        
        # الجزء الأيمن - النموذج
        right_panel = self.create_form_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)

    def create_welcome_panel(self):
        """لوحة الترحيب الجانبية"""
        panel = QFrame()
        panel.setObjectName("welcomePanel")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # الشعار
        logo = QLabel("🎯")
        logo.setStyleSheet("font-size: 80px;")
        logo.setAlignment(Qt.AlignCenter)
        
        # العنوان
        title = QLabel("Recruitmentify")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        
        # الوصف
        subtitle = QLabel("نظام ذكي لإدارة طلبات التوظيف")
        subtitle.setStyleSheet("font-size: 16px; color: rgba(255,255,255,0.8);")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        
        # الميزات
        features = QVBoxLayout()
        features.setSpacing(15)
        
        feature1 = self.create_feature_item("✅", "تقييم ذكي بالـ AI")
        feature2 = self.create_feature_item("⚡", "نتائج فورية")
        feature3 = self.create_feature_item("🔒", "آمن ومحمي")
        feature4 = self.create_feature_item("📊", "تحليل شامل")
        
        features.addWidget(feature1)
        features.addWidget(feature2)
        features.addWidget(feature3)
        features.addWidget(feature4)
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addLayout(features)
        layout.addStretch()
        
        # معلومات التواصل
        contact = QLabel("للدعم: support@recruitmentify.com")
        contact.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6);")
        contact.setAlignment(Qt.AlignCenter)
        layout.addWidget(contact)
        
        panel.setLayout(layout)
        return panel

    def create_feature_item(self, icon, text):
        """عنصر ميزة"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        container.setLayout(layout)
        return container

    def create_form_panel(self):
        """لوحة النموذج"""
        panel = QFrame()
        panel.setObjectName("formPanel")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 40, 50, 40)
        
        # الترويسة
        header = self.create_form_header()
        layout.addWidget(header)
        
        # النموذج
        form = self.create_form()
        layout.addLayout(form)
        
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel

    def create_form_header(self):
        """ترويسة النموذج"""
        container = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # زر الثيم
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        
        self.theme_button = QPushButton("🌙 الوضع الداكن")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setFixedSize(130, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        theme_layout.addWidget(self.theme_button)
        
        # العنوان
        title = QLabel("قدّم سيرتك الذاتية")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        
        subtitle = QLabel("املأ المعلومات أدناه وسنقوم بتقييم ملفك تلقائياً")
        subtitle.setStyleSheet("font-size: 14px; color: #666;")
        subtitle.setWordWrap(True)
        
        layout.addLayout(theme_layout)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        container.setLayout(layout)
        return container

    def create_form(self):
        """إنشاء النموذج"""
        form = QVBoxLayout()
        form.setSpacing(20)
        
        # الاسم الكامل
        self.full_name_label = QLabel("الاسم الكامل *")
        self.full_name_label.setStyleSheet("font-weight: bold;")
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("أدخل اسمك الكامل")
        self.full_name_input.setObjectName("formInput")
        self.full_name_input.setFixedHeight(50)
        
        # البريد الإلكتروني
        self.email_label = QLabel("البريد الإلكتروني *")
        self.email_label.setStyleSheet("font-weight: bold;")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        self.email_input.setObjectName("formInput")
        self.email_input.setFixedHeight(50)
        
        # الشركة
        self.company_label = QLabel("الشركة *")
        self.company_label.setStyleSheet("font-weight: bold;")
        
        self.company_dropdown = QComboBox()
        self.company_dropdown.setObjectName("formInput")
        self.company_dropdown.setFixedHeight(50)
        self.company_dropdown.addItem("اختر الشركة...")
        
        # تحميل أسماء الشركات
        company_names = self.get_company_names()
        if company_names:
            self.company_dropdown.addItems(company_names)
        
        self.company_dropdown.currentIndexChanged.connect(self.on_company_selected)
        
        # الوظيفة
        self.work_label = QLabel("الوظيفة المطلوبة *")
        self.work_label.setStyleSheet("font-weight: bold;")
        self.work_label.hide()
        
        self.work_dropdown = QComboBox()
        self.work_dropdown.setObjectName("formInput")
        self.work_dropdown.setFixedHeight(50)
        self.work_dropdown.hide()
        
        # منطقة السحب والإفلات
        self.drop_area = QFrame()
        self.drop_area.setObjectName("dropArea")
        self.drop_area.setFixedHeight(120)
        self.drop_area.setAcceptDrops(True)
        
        drop_layout = QVBoxLayout()
        
        drop_icon = QLabel("📄")
        drop_icon.setStyleSheet("font-size: 40px;")
        drop_icon.setAlignment(Qt.AlignCenter)
        
        self.drop_label = QLabel("اسحب وأفلت ملف PDF هنا\nأو انقر للاختيار")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("color: #666; font-size: 14px;")
        
        drop_layout.addWidget(drop_icon)
        drop_layout.addWidget(self.drop_label)
        
        self.drop_area.setLayout(drop_layout)
        self.drop_area.mousePressEvent = lambda e: self.select_file()
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        # زر الإرسال
        submit_btn = QPushButton("📤 إرسال الطلب")
        submit_btn.setObjectName("submitButton")
        submit_btn.setFixedHeight(55)
        submit_btn.clicked.connect(self.onsubmited)
        
        # ملاحظة
        note = QLabel("* جميع الحقول مطلوبة")
        note.setStyleSheet("font-size: 12px; color: #999; font-style: italic;")
        
        # إضافة العناصر للنموذج
        form.addWidget(self.full_name_label)
        form.addWidget(self.full_name_input)
        form.addWidget(self.email_label)
        form.addWidget(self.email_input)
        form.addWidget(self.company_label)
        form.addWidget(self.company_dropdown)
        form.addWidget(self.work_label)
        form.addWidget(self.work_dropdown)
        form.addWidget(QLabel("السيرة الذاتية *", styleSheet="font-weight: bold;"))
        form.addWidget(self.drop_area)
        form.addWidget(self.progress_bar)
        form.addWidget(submit_btn)
        form.addWidget(note)
        
        return form

    def select_file(self):
        """اختيار ملف يدوياً"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            ModernResumeApp.filepath = file_path
            self.drop_label.setText(f"✅ تم اختيار: {os.path.basename(file_path)}")
            self.drop_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
        
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            urls = event.mimeData().urls()
            
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                
                if file_path.lower().endswith('.pdf'):
                    ModernResumeApp.filepath = file_path
                    self.drop_label.setText(f"✅ تم اختيار: {os.path.basename(file_path)}")
                    self.drop_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
                else:
                    QMessageBox.warning(self, "خطأ", "يرجى اختيار ملف PDF فقط!")
                    ModernResumeApp.filepath = None
        else:
            event.ignore()

    def get_company_names(self):
        """الحصول على أسماء الشركات"""
        try:
            companies = cref.get()
            if not companies:
                return []
            
            company_names = []
            for company_id, company_data in companies.items():
                name = company_data.get('company_name')
                if name:
                    company_names.append(name)
            
            return sorted(company_names)
            
        except Exception as e:
            print(f"❌ خطأ في تحميل الشركات: {e}")
            QMessageBox.critical(
                self,
                "خطأ في الاتصال",
                "تعذر الاتصال بقاعدة البيانات.\nيرجى التحقق من اتصالك بالإنترنت."
            )
            return []

    def get_jops_data(self):
        """الحصول على بيانات الوظائف"""
        try:
            jops = jref.get()
            if not jops:
                print("⚠️ لا توجد وظائف في قاعدة البيانات")
                return []
            
            jops_data = []
            for jop_id, jop_data in jops.items():
                name = jop_data.get('name')
                value = jop_data.get('value')
                compname = jop_data.get('company_name')
                
                if name and value and compname:
                    jops_data.append((name, value, compname))
                else:
                    print(f"⚠️ بيانات ناقصة للوظيفة: {jop_id}")
            
            return jops_data
            
        except Exception as e:
            print(f"❌ خطأ في تحميل الوظائف: {e}")
            return []

    def on_company_selected(self):
        """عند اختيار شركة"""
        selected_company = self.company_dropdown.currentText()
        
        if selected_company != "اختر الشركة...":
            self.work_label.show()
            self.work_dropdown.show()
            self.work_dropdown.clear()
            
            jops_data = self.get_jops_data()
            
            # تصفية الوظائف حسب الشركة
            for name, value, compname in jops_data:
                if compname == selected_company:
                    self.work_dropdown.addItem(name, userData=(value, compname))
            
            if self.work_dropdown.count() == 0:
                self.work_dropdown.addItem("لا توجد وظائف متاحة")
        else:
            self.work_label.hide()
            self.work_dropdown.hide()
            self.work_dropdown.clear()

    def onsubmited(self):
        """عند الإرسال"""
        # التحقق من البيانات
        fullname = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        company = self.company_dropdown.currentText()
        
        if not fullname:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال الاسم الكامل")
            return
        
        if not email or '@' not in email:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال بريد إلكتروني صحيح")
            return
        
        if company == "اختر الشركة...":
            QMessageBox.warning(self, "خطأ", "يرجى اختيار الشركة")
            return
        
        if not ModernResumeApp.filepath:
            QMessageBox.warning(self, "خطأ", "يرجى إرفاق ملف السيرة الذاتية PDF")
            return
        
        selected_work_data = self.work_dropdown.currentData()
        
        if not selected_work_data:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار الوظيفة")
            return
        
        selected_work_text = self.work_dropdown.currentText()
        work_value, work_company_name = selected_work_data
        
        # عرض شريط التقدم
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # وضع غير محدد
        
        # معالجة الطلب
        QTimer.singleShot(100, lambda: self.process_application(
            fullname, email, company, work_value, selected_work_text
        ))

    def process_application(self, fullname, email, company, work_value, job_name):
        """معالجة الطلب"""
        try:
            self.summarize(fullname, email, company, work_value, job_name)
            self.progress_bar.hide()
            
            # رسالة نجاح
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("تم بنجاح! ✅")
            msg.setText("تم إرسال طلبك بنجاح!")
            msg.setInformativeText(
                f"شكراً {fullname}!\n\n"
                f"تم استلام سيرتك الذاتية وتقييمها.\n"
                f"التقييم: {ModernResumeApp.rating}/100\n\n"
                "سنتواصل معك قريباً عبر البريد الإلكتروني."
            )
            msg.exec_()
            
            # مسح النموذج
            self.clear_form()
            
        except Exception as e:
            self.progress_bar.hide()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def summarize(self, fullname, email, company, company_value, job_name):
        """تلخيص السيرة الذاتية باستخدام AI"""
        try:
            if not ModernResumeApp.filepath or not os.path.exists(ModernResumeApp.filepath):
                raise Exception("ملف السيرة الذاتية غير موجود")
            
            # معالجة بالـ AI
            aiout = pdf_push_to_ai(ModernResumeApp.filepath, company_value)
            
            # استخراج التقييم والملخص
            ModernResumeApp.rating, ModernResumeApp.summary = TextProcessor.stripText(aiout)
            
            # حفظ في قاعدة البيانات
            push_customer_data_to_firebase(
                fullname, email, "Pending", 
                ModernResumeApp.rating, ModernResumeApp.summary,
                ModernResumeApp.filepath, company, job_name
            )
            
            print(f"✅ تم معالجة طلب {fullname} بنجاح - التقييم: {ModernResumeApp.rating}")
            
        except Exception as e:
            print(f"❌ خطأ في المعالجة: {e}")
            raise

    def clear_form(self):
        """مسح النموذج"""
        self.full_name_input.clear()
        self.email_input.clear()
        self.company_dropdown.setCurrentIndex(0)
        self.work_dropdown.clear()
        self.work_label.hide()
        self.work_dropdown.hide()
        ModernResumeApp.filepath = None
        self.drop_label.setText("اسحب وأفلت ملف PDF هنا\nأو انقر للاختيار")
        self.drop_label.setStyleSheet("color: #666; font-size: 14px;")

    def toggle_theme(self):
        """تبديل الثيم"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """تطبيق الثيم"""
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, sans-serif;
                }
                
                #welcomePanel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                }
                
                #formPanel {
                    background-color: #2a2a2a;
                }
                
                #formInput {
                    background-color: #3a3a3a;
                    border: 2px solid #444;
                    border-radius: 10px;
                    padding: 12px;
                    color: white;
                    font-size: 14px;
                }
                
                #formInput:focus {
                    border: 2px solid #667eea;
                }
                
                #dropArea {
                    background-color: #3a3a3a;
                    border: 2px dashed #555;
                    border-radius: 12px;
                }
                
                #dropArea:hover {
                    border-color: #667eea;
                    background-color: #404040;
                }
                
                #submitButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }
                
                #submitButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5568d3, stop:1 #6538a3);
                }
                
                #themeButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    font-size: 13px;
                }
                
                #themeButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                
                #progressBar {
                    background-color: #3a3a3a;
                    border-radius: 4px;
                }
                
                #progressBar::chunk {
                    background-color: #667eea;
                    border-radius: 4px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: #3a3a3a;
                    color: white;
                    selection-background-color: #667eea;
                }
            """)
            self.theme_button.setText("☀️ الوضع الفاتح")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #333333;
                    font-family: 'Segoe UI', Tahoma, sans-serif;
                }
                
                #welcomePanel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                }
                
                #formPanel {
                    background-color: #f8f9fa;
                }
                
                #formInput {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 12px;
                    color: #333;
                    font-size: 14px;
                }
                
                #formInput:focus {
                    border: 2px solid #667eea;
                }
                
                #dropArea {
                    background-color: #f0f7ff;
                    border: 2px dashed #ccc;
                    border-radius: 12px;
                }
                
                #dropArea:hover {
                    border-color: #667eea;
                    background-color: #e6f2ff;
                }
                
                #submitButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }
                
                #submitButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5568d3, stop:1 #6538a3);
                }
                
                #themeButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    font-size: 13px;
                }
                
                #themeButton:hover {
                    background-color: #d0d0d0;
                }
                
                #progressBar {
                    background-color: #e0e0e0;
                    border-radius: 4px;
                }
                
                #progressBar::chunk {
                    background-color: #667eea;
                    border-radius: 4px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #333;
                    selection-background-color: #667eea;
                    selection-color: white;
                }
            """)
            self.theme_button.setText("🌙 الوضع الداكن")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # تطبيق خط عربي أفضل
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernResumeApp()
    window.show()
    
    sys.exit(app.exec_())