import base64
import tempfile
import os
import sys
import signal

from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QWidget, QSplitter, QTextEdit, QComboBox, QHeaderView,
    QDialog, QMessageBox, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPalette, QFont

from firebase_connection import ref
from session_handler import load_session
from jops_panel import JobManager
from enhanced_dashboard import EnhancedDashboard
from chatbot import FloatingChatBot, RecruitmentChatBot


class EnhancedAdminPage(QWidget):
    def __init__(self):
        super().__init__()
        session = load_session()
        self.company_name = session.get("company_name", "")
        self.setWindowTitle('🎯 Recruitmentify - نظام الإدارة الذكية')
        self.setGeometry(50, 50, 1400, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 14px;
            }
        """)
        self.additional_data = {}
        self.current_row = None
        self.setProperty("dark_theme", False)  # ابدأ بالوضع الفاتح

        self.init_ui()
        self.load_data()
        
        # تحديث تلقائي كل دقيقة
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.load_data)
        self.auto_refresh_timer.start(60000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # الترويسة المحسنة
        header = self.create_modern_header()
        main_layout.addWidget(header)

        # شريط البحث والفلتر
        search_filter_bar = self.create_search_filter_bar()
        main_layout.addWidget(search_filter_bar)

        # منطقة المحتوى الرئيسية
        splitter = QSplitter(Qt.Horizontal)
        
        # الجزء الأيسر - الجدول
        left_widget = self.create_table_section()
        
        # الجزء الأيمن - التفاصيل
        right_widget = self.create_details_section()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 600])

        main_layout.addWidget(splitter)

        # إضافة زر الشات بوت العائم
        self.add_floating_chatbot()

    def create_modern_header(self):
        """ترويسة حديثة وجميلة"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # القسم الأيسر - العنوان والترحيب
        left_section = QVBoxLayout()
        
        title = QLabel("🎯 نظام الإدارة الذكية للتوظيف")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        welcome = QLabel(f"مرحباً {self.company_name}")
        welcome.setStyleSheet("color: #e0e0e0; font-size: 16px;")
        
        left_section.addWidget(title)
        left_section.addWidget(welcome)
        
        layout.addLayout(left_section)
        layout.addStretch()
        
        # القسم الأيمن - أزرار التنقل السريع
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # زر لوحة التحكم
        dashboard_btn = QPushButton("📊 لوحة التحكم")
        dashboard_btn.setStyleSheet(self.header_button_style())
        dashboard_btn.clicked.connect(self.open_dashboard)
        
        # زر الوظائف
        jobs_btn = QPushButton("💼 إدارة الوظائف")
        jobs_btn.setStyleSheet(self.header_button_style())
        jobs_btn.clicked.connect(self.open_jobs_window)
        
        # زر التقارير
        reports_btn = QPushButton("📈 التقارير")
        reports_btn.setStyleSheet(self.header_button_style())
        reports_btn.clicked.connect(self.show_reports)
        
        # زر الثيم
        self.theme_btn = QPushButton("🌙 الوضع الداكن")
        self.theme_btn.setStyleSheet(self.header_button_style())
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        buttons_layout.addWidget(dashboard_btn)
        buttons_layout.addWidget(jobs_btn)
        buttons_layout.addWidget(reports_btn)
        buttons_layout.addWidget(self.theme_btn)
        
        layout.addLayout(buttons_layout)
        
        header.setLayout(layout)
        header.setMinimumHeight(100)
        
        return header

    def create_search_filter_bar(self):
        """شريط البحث والفلترة"""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # البحث
        search_label = QLabel("🔍 البحث:")
        search_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث بالاسم، البريد، أو الوظيفة...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        
        # الفلتر حسب الحالة
        filter_label = QLabel("🎯 الحالة:")
        filter_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(["الكل", "مقبول", "قيد المراجعة", "مرفوض"])
        self.filter_dropdown.setStyleSheet(self.modern_combo_style())
        self.filter_dropdown.currentTextChanged.connect(self.filter_table)
        
        # الترتيب
        sort_label = QLabel("📊 الترتيب:")
        sort_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.sort_dropdown = QComboBox()
        self.sort_dropdown.addItems(["الاسم", "الوظيفة", "التقييم", "الحالة"])
        self.sort_dropdown.setStyleSheet(self.modern_combo_style())
        self.sort_dropdown.currentIndexChanged.connect(self.sort_table)
        
        # زر التحديث
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(self.action_button_style("#4CAF50"))
        refresh_btn.clicked.connect(self.load_data)
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input, 3)
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_dropdown, 1)
        layout.addWidget(sort_label)
        layout.addWidget(self.sort_dropdown, 1)
        layout.addWidget(refresh_btn)
        
        bar.setLayout(layout)
        
        return bar

    def create_table_section(self):
        """قسم الجدول"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # عنوان القسم
        section_header = QFrame()
        section_header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 قائمة المتقدمين")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        self.count_label = QLabel("(0 متقدم)")
        self.count_label.setStyleSheet("font-size: 14px; color: #666;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        
        # أزرار الإجراءات
        export_btn = QPushButton("📥 تصدير")
        export_btn.setStyleSheet(self.action_button_style("#2196F3"))
        export_btn.clicked.connect(self.export_data)
        
        delete_btn = QPushButton("🗑️ حذف المحدد")
        delete_btn.setStyleSheet(self.action_button_style("#F44336"))
        delete_btn.clicked.connect(self.delete_selected)
        
        header_layout.addWidget(export_btn)
        header_layout.addWidget(delete_btn)
        
        section_header.setLayout(header_layout)
        
        # الجدول
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الاسم الكامل", "البريد الإلكتروني", "الوظيفة", "الحالة", "التقييم"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet(self.modern_table_style())
        self.table.cellClicked.connect(self.show_resume_details)
        
        # رسالة لا توجد بيانات
        self.no_resume_label = QLabel("📭 لا توجد طلبات حالياً")
        self.no_resume_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 16px;
                font-style: italic;
                padding: 40px;
            }
        """)
        self.no_resume_label.setAlignment(Qt.AlignCenter)
        self.no_resume_label.hide()
        
        layout.addWidget(section_header)
        layout.addWidget(self.table)
        layout.addWidget(self.no_resume_label)
        
        return widget

    def create_details_section(self):
        """قسم التفاصيل"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # ترويسة القسم
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout()
        
        self.details_label = QLabel("👤 تفاصيل المتقدم")
        self.details_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        header_layout.addWidget(self.details_label)
        header_layout.addStretch()
        
        header_frame.setLayout(header_layout)
        
        # منطقة التفاصيل
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.details_text.setPlaceholderText("اختر متقدماً لعرض التفاصيل...")
        
        # أزرار الإجراءات
        actions_layout = QHBoxLayout()
        
        self.open_resume_btn = QPushButton("📄 فتح السيرة الذاتية")
        self.open_resume_btn.setStyleSheet(self.action_button_style("#667eea"))
        self.open_resume_btn.clicked.connect(self.open_resume)
        
        self.send_email_btn = QPushButton("📧 إرسال بريد")
        self.send_email_btn.setStyleSheet(self.action_button_style("#9C27B0"))
        self.send_email_btn.clicked.connect(self.send_email_to_applicant)
        
        actions_layout.addWidget(self.open_resume_btn)
        actions_layout.addWidget(self.send_email_btn)
        
        layout.addWidget(header_frame)
        layout.addWidget(self.details_text)
        layout.addLayout(actions_layout)
        
        return widget

    def add_floating_chatbot(self):
        """إضافة زر الشات بوت العائم"""
        self.chatbot_btn = FloatingChatBot(self)
        self.chatbot_btn.move(self.width() - 80, self.height() - 80)

    def resizeEvent(self, event):
        """إعادة وضع زر الشات بوت عند تغيير حجم النافذة"""
        super().resizeEvent(event)
        if hasattr(self, 'chatbot_btn'):
            self.chatbot_btn.move(self.width() - 80, self.height() - 80)

    # وظائف الأزرار
    def open_dashboard(self):
        """فتح لوحة التحكم"""
        self.dashboard_window = EnhancedDashboard()
        self.dashboard_window.show()

    def open_jobs_window(self):
        """فتح نافذة الوظائف"""
        self.jobs_window = JobManager()
        self.jobs_window.show()

    def show_reports(self):
        """عرض التقارير"""
        QMessageBox.information(self, "التقارير", 
            "سيتم فتح صفحة التقارير المتقدمة قريباً!\n\n"
            "الميزات القادمة:\n"
            "• تقارير PDF شاملة\n"
            "• تصدير Excel\n"
            "• رسوم بيانية تحليلية\n"
            "• إحصائيات مفصلة"
        )

    def export_data(self):
        """تصدير البيانات"""
        QMessageBox.information(self, "تصدير", 
            "سيتم تصدير البيانات بصيغة Excel/CSV قريباً!"
        )

    def delete_selected(self):
        """حذف العنصر المحدد"""
        if self.current_row is None:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار متقدم أولاً.")
            return
        
        reply = QMessageBox.question(self, 'تأكيد الحذف', 
            'هل أنت متأكد من حذف هذا الطلب؟',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                firebase_key = self.additional_data[self.current_row]['firebase_key']
                ref.child(firebase_key).delete()
                QMessageBox.information(self, "نجح", "تم الحذف بنجاح!")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحذف: {str(e)}")

    def send_email_to_applicant(self):
        """إرسال بريد إلكتروني للمتقدم"""
        if self.current_row is None:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار متقدم أولاً.")
            return
        
        email = self.table.item(self.current_row, 1).text()
        QMessageBox.information(self, "إرسال بريد", 
            f"سيتم فتح برنامج البريد الإلكتروني للتواصل مع:\n{email}\n\n"
            "(هذه الميزة قيد التطوير)"
        )

    def toggle_theme(self):
        """تبديل الثيم"""
        is_dark = self.property("dark_theme")
        
        if not is_dark:
            # تطبيق الثيم الداكن
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
            """)
            self.theme_btn.setText("☀️ الوضع الفاتح")
        else:
            # تطبيق الثيم الفاتح
            self.setStyleSheet("""
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
            """)
            self.theme_btn.setText("🌙 الوضع الداكن")
        
        self.setProperty("dark_theme", not is_dark)

    def filter_table(self):
        """فلترة الجدول"""
        search_text = self.search_input.text().lower()
        status_filter = self.filter_dropdown.currentText()
        
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            email = self.table.item(row, 1).text().lower()
            job = self.table.item(row, 2).text().lower()
            status_widget = self.table.cellWidget(row, 3)
            
            # فحص البحث
            search_match = (search_text in name or 
                          search_text in email or 
                          search_text in job)
            
            # فحص الحالة
            if status_widget:
                row_status = status_widget.currentText()
                if status_filter == "الكل":
                    status_match = True
                else:
                    status_match = (row_status == status_filter)
            else:
                status_match = True
            
            should_show = search_match and status_match
            self.table.setRowHidden(row, not should_show)

    def sort_table(self, index):
        """ترتيب الجدول"""
        rows = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            email = self.table.item(row, 1).text()
            job = self.table.item(row, 2).text()
            status = self.table.cellWidget(row, 3).currentText()
            rating = self.table.item(row, 4).text()
            additional_info = self.additional_data.get(row, {})
            rows.append((name, email, job, status, rating, additional_info))

        if index == 0:  # الاسم
            rows.sort(key=lambda x: x[0])
        elif index == 1:  # الوظيفة
            rows.sort(key=lambda x: x[2])
        elif index == 2:  # التقييم
            rows.sort(key=lambda x: float(x[4]) if x[4].replace('.','').isdigit() else 0, reverse=True)
        elif index == 3:  # الحالة
            rows.sort(key=lambda x: x[3])

        self.repopulate_table(rows)

    def load_data(self):
        """تحميل البيانات من Firebase"""
        try:
            current_company = self.company_name
            if not current_company:
                self.no_resume_label.setText("❌ لم يتم العثور على الشركة في الجلسة")
                self.no_resume_label.show()
                return

            all_data = ref.get()

            if all_data:
                filtered_data = {
                    key: resume for key, resume in all_data.items()
                    if resume.get("company") == current_company
                }
                self.populate_table(filtered_data)
            else:
                self.no_resume_label.setText("📭 لا توجد بيانات في قاعدة البيانات")
                self.no_resume_label.show()

        except Exception as e:
            error_msg = f"❌ خطأ في الاتصال بقاعدة البيانات:\n{str(e)}"
            self.no_resume_label.setText(error_msg)
            self.no_resume_label.show()
            QMessageBox.critical(self, "خطأ", error_msg)

    def populate_table(self, data):
        """ملء الجدول بالبيانات"""
        self.table.setRowCount(0)
        self.additional_data.clear()
        
        if not data:
            self.no_resume_label.show()
            self.count_label.setText("(0 متقدم)")
            return
        
        self.no_resume_label.hide()
        self.count_label.setText(f"({len(data)} متقدم)")

        for key, resume in data.items():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # الاسم
            name_item = QTableWidgetItem(resume.get('full_name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_position, 0, name_item)

            # البريد
            email_item = QTableWidgetItem(resume.get('email', ''))
            email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_position, 1, email_item)

            # الوظيفة
            job_item = QTableWidgetItem(resume.get('job', ''))
            job_item.setFlags(job_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_position, 2, job_item)

            # الحالة
            status_dropdown = QComboBox()
            status_dropdown.addItems(["مقبول", "قيد المراجعة", "مرفوض"])
            
            # تعيين الحالة الحالية
            current_status = resume.get('status', 'Pending')
            status_map = {
                'Approved': 'مقبول',
                'Pending': 'قيد المراجعة',
                'Rejected': 'مرفوض'
            }
            status_dropdown.setCurrentText(status_map.get(current_status, 'قيد المراجعة'))
            
            status_dropdown.setStyleSheet(self.modern_combo_style())
            status_dropdown.currentTextChanged.connect(
                lambda status, row=row_position: self.update_status(row, status)
            )
            self.table.setCellWidget(row_position, 3, status_dropdown)

            # التقييم
            rating_item = QTableWidgetItem(str(resume.get('raiting', '0')))
            rating_item.setFlags(rating_item.flags() & ~Qt.ItemIsEditable)
            
            # تلوين التقييم
            try:
                rating_value = float(resume.get('raiting', 0))
                if rating_value >= 8:
                    rating_item.setForeground(QColor("#4CAF50"))  # أخضر
                elif rating_value >= 6:
                    rating_item.setForeground(QColor("#FF9800"))  # برتقالي
                else:
                    rating_item.setForeground(QColor("#F44336"))  # أحمر
            except:
                pass
            
            self.table.setItem(row_position, 4, rating_item)

            # حفظ البيانات الإضافية
            self.additional_data[row_position] = {
                'summary': resume.get('summary', ''),
                'resume_data': resume.get('resume_data', ''),
                'firebase_key': key
            }

    def repopulate_table(self, rows):
        """إعادة ملء الجدول بعد الترتيب"""
        self.table.setRowCount(0)
        self.additional_data.clear()
        
        for i, (name, email, job, status, rating, additional_info) in enumerate(rows):
            self.table.insertRow(i)

            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, name_item)

            email_item = QTableWidgetItem(email)
            email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, email_item)

            job_item = QTableWidgetItem(job)
            job_item.setFlags(job_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, job_item)

            status_dropdown = QComboBox()
            status_dropdown.addItems(["مقبول", "قيد المراجعة", "مرفوض"])
            status_dropdown.setCurrentText(status)
            status_dropdown.setStyleSheet(self.modern_combo_style())
            status_dropdown.currentTextChanged.connect(
                lambda s, row=i: self.update_status(row, s)
            )
            self.table.setCellWidget(i, 3, status_dropdown)

            rating_item = QTableWidgetItem(rating)
            rating_item.setFlags(rating_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 4, rating_item)

            self.additional_data[i] = additional_info

    def update_status(self, row, new_status):
        """تحديث الحالة في Firebase"""
        firebase_key = self.additional_data[row]['firebase_key']
        
        # تحويل من العربية للإنجليزية
        status_map = {
            'مقبول': 'Approved',
            'قيد المراجعة': 'Pending',
            'مرفوض': 'Rejected'
        }
        
        try:
            ref.child(firebase_key).update({'status': status_map.get(new_status, 'Pending')})
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحديث الحالة: {str(e)}")

    def show_resume_details(self, row, column):
        """عرض تفاصيل السيرة الذاتية"""
        self.current_row = row
        
        name = self.table.item(row, 0).text()
        email = self.table.item(row, 1).text()
        job = self.table.item(row, 2).text()
        status = self.table.cellWidget(row, 3).currentText()
        rating = self.table.item(row, 4).text()
        
        additional_info = self.additional_data.get(row, {})
        summary = additional_info.get('summary', 'لا يوجد ملخص')
        
        details_html = f"""
        <div style='font-family: Arial; line-height: 1.8;'>
            <h2 style='color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>
                معلومات المتقدم
            </h2>
            
            <p><strong>👤 الاسم:</strong> {name}</p>
            <p><strong>📧 البريد الإلكتروني:</strong> {email}</p>
            <p><strong>💼 الوظيفة المطلوبة:</strong> {job}</p>
            <p><strong>📊 الحالة:</strong> <span style='color: {"#4CAF50" if status == "مقبول" else "#FF9800" if status == "قيد المراجعة" else "#F44336"};'>{status}</span></p>
            <p><strong>⭐ التقييم:</strong> {rating}/10</p>
            
            <h3 style='color: #667eea; margin-top: 20px;'>📝 الملخص:</h3>
            <p style='background-color: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;'>
                {summary}
            </p>
        </div>
        """
        
        self.details_text.setHtml(details_html)

    def open_resume(self):
        """فتح السيرة الذاتية"""
        if self.current_row is None:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار متقدم من الجدول أولاً.")
            return
        
        additional_info = self.additional_data.get(self.current_row, {})
        image_data = additional_info.get('resume_data', '')
        
        if not image_data:
            QMessageBox.warning(self, "تنبيه", "لم يتم العثور على ملف السيرة الذاتية.")
            return
        
        try:
            decoded_data = base64.b64decode(image_data)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(decoded_data)
                temp_file_path = temp_file.name
            
            # فتح الملف حسب نظام التشغيل
            if os.name == 'nt':  # Windows
                os.startfile(temp_file_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{temp_file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{temp_file_path}"')
                
            QMessageBox.information(self, "نجح", "تم فتح السيرة الذاتية بنجاح!")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل فتح الملف: {str(e)}")

    # الأنماط CSS
    def header_button_style(self):
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """

    def action_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                padding: 11px 14px 9px 16px;
            }}
        """

    def modern_combo_style(self):
        return """
            QComboBox {
                padding: 8px 12px;
                border-radius: 6px;
                border: 2px solid #e0e0e0;
                background-color: white;
                color: #333;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 2px solid #667eea;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #667eea;
                background-color: white;
                selection-background-color: #667eea;
                selection-color: white;
                padding: 5px;
            }
        """

    def modern_table_style(self):
        return """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #f0f0ff;
            }
            QHeaderView::section {
                background-color: #667eea;
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
                font-size: 14px;
            }
            QHeaderView::section:hover {
                background-color: #5568d3;
            }
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # تطبيق نمط عام
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.WindowText, QColor("#333333"))
    app.setPalette(palette)
    
    window = EnhancedAdminPage()
    window.show()
    
    sys.exit(app.exec_())