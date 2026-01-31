import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFrame, QGridLayout, QMessageBox,
    QScrollArea, QTabWidget, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
import firebase_admin
from firebase_admin import credentials, db
from firebase_connection import cref
from session_handler import load_session
from datetime import datetime, timedelta


class AnimatedStatCard(QFrame):
    """بطاقة إحصائيات متحركة"""
    def __init__(self, title, value, color, icon="📊"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.darken_color(color)});
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # الأيقونة والعنوان
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        header.addWidget(icon_label)
        header.addStretch()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        # القيمة
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")
        
        layout.addLayout(header)
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMinimumHeight(150)
        
    def darken_color(self, color):
        """تغميق اللون للتدرج"""
        color_map = {
            "#4CAF50": "#388E3C",
            "#2196F3": "#1976D2",
            "#FF9800": "#F57C00",
            "#F44336": "#D32F2F",
            "#9C27B0": "#7B1FA2"
        }
        return color_map.get(color, "#555555")
    
    def update_value(self, new_value):
        """تحديث القيمة بشكل متحرك"""
        self.value_label.setText(str(new_value))


class EnhancedDashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        session = load_session()
        self.company_name = session.get("company_name", "")
        self.company_email = session.get("email", "")
        self.company_id = None
        
        self.setWindowTitle("لوحة التحكم الذكية - Recruitmentify")
        self.setGeometry(50, 50, 1400, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        self.init_ui()
        self.load_data()
        
        # تحديث تلقائي كل 30 ثانية
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # الترويسة
        header = self.create_header()
        main_layout.addWidget(header)
        
        # التبويبات
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
            }
        """)
        
        # تبويب الإحصائيات
        stats_tab = self.create_statistics_tab()
        tabs.addTab(stats_tab, "📊 الإحصائيات")
        
        # تبويب الرسوم البيانية
        charts_tab = self.create_charts_tab()
        tabs.addTab(charts_tab, "📈 التحليلات")
        
        # تبويب الإعدادات
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "⚙️ الإعدادات")
        
        # تبويب التقارير
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📄 التقارير")
        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
        
    def create_header(self):
        """إنشاء ترويسة احترافية"""
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
        
        # معلومات الشركة
        company_info = QVBoxLayout()
        
        welcome = QLabel(f"مرحباً بك، {self.company_name}")
        welcome.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        date_label = QLabel(datetime.now().strftime("%A, %d %B %Y"))
        date_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        
        company_info.addWidget(welcome)
        company_info.addWidget(date_label)
        
        layout.addLayout(company_info)
        layout.addStretch()
        
        # أزرار سريعة
        quick_actions = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(self.button_style("#ffffff", "#f0f0f0"))
        refresh_btn.clicked.connect(self.refresh_data)
        
        export_btn = QPushButton("📥 تصدير")
        export_btn.setStyleSheet(self.button_style("#ffffff", "#f0f0f0"))
        export_btn.clicked.connect(self.export_report)
        
        quick_actions.addWidget(refresh_btn)
        quick_actions.addWidget(export_btn)
        
        layout.addLayout(quick_actions)
        header.setLayout(layout)
        
        return header
    
    def create_statistics_tab(self):
        """تبويب الإحصائيات مع بطاقات متحركة"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # بطاقات الإحصائيات
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        self.total_card = AnimatedStatCard("إجمالي الطلبات", "0", "#2196F3", "📋")
        self.approved_card = AnimatedStatCard("المقبولة", "0", "#4CAF50", "✅")
        self.pending_card = AnimatedStatCard("قيد المراجعة", "0", "#FF9800", "⏳")
        self.rejected_card = AnimatedStatCard("المرفوضة", "0", "#F44336", "❌")
        
        cards_layout.addWidget(self.total_card, 0, 0)
        cards_layout.addWidget(self.approved_card, 0, 1)
        cards_layout.addWidget(self.pending_card, 0, 2)
        cards_layout.addWidget(self.rejected_card, 0, 3)
        
        layout.addLayout(cards_layout)
        
        # إحصائيات إضافية
        extra_stats = QGridLayout()
        
        # معدل القبول
        acceptance_frame = self.create_stat_frame("معدل القبول", "0%", "#9C27B0")
        extra_stats.addWidget(acceptance_frame, 0, 0)
        
        # متوسط التقييم
        rating_frame = self.create_stat_frame("متوسط التقييم", "0.0", "#00BCD4")
        extra_stats.addWidget(rating_frame, 0, 1)
        
        # الطلبات هذا الشهر
        monthly_frame = self.create_stat_frame("طلبات هذا الشهر", "0", "#8BC34A")
        extra_stats.addWidget(monthly_frame, 0, 2)
        
        layout.addLayout(extra_stats)
        
        # جدول أحدث الطلبات
        recent_applications = self.create_recent_applications_widget()
        layout.addWidget(recent_applications)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_stat_frame(self, title, value, color):
        """إنشاء إطار إحصائيات"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #333; font-size: 28px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        frame.setLayout(layout)
        return frame
    
    def create_recent_applications_widget(self):
        """ويدجت أحدث الطلبات"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("أحدث الطلبات")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        self.recent_list = QTextEdit()
        self.recent_list.setReadOnly(True)
        self.recent_list.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(self.recent_list)
        
        frame.setLayout(layout)
        return frame
    
    def create_charts_tab(self):
        """تبويب الرسوم البيانية"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Pie Chart - توزيع الحالات
        pie_chart = self.create_pie_chart()
        layout.addWidget(pie_chart)
        
        # Bar Chart - الطلبات حسب الوظيفة
        bar_chart = self.create_bar_chart()
        layout.addWidget(bar_chart)
        
        widget.setLayout(layout)
        return widget
    
    def create_pie_chart(self):
        """إنشاء رسم بياني دائري"""
        series = QPieSeries()
        
        approved_slice = series.append("مقبول", 10)
        pending_slice = series.append("قيد المراجعة", 5)
        rejected_slice = series.append("مرفوض", 3)
        
        approved_slice.setBrush(QColor("#4CAF50"))
        pending_slice.setBrush(QColor("#FF9800"))
        rejected_slice.setBrush(QColor("#F44336"))
        
        # تفعيل العرض عند التحويم
        for slice in series.slices():
            slice.setLabelVisible(True)
            slice.setLabelColor(Qt.white)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("توزيع حالات الطلبات")
        chart.legend().setVisible(True)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def create_bar_chart(self):
        """إنشاء رسم بياني بالأعمدة"""
        set0 = QBarSet("عدد الطلبات")
        set0.append([15, 10, 8, 12, 6])
        set0.setColor(QColor("#667eea"))
        
        series = QBarSeries()
        series.append(set0)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("الطلبات حسب نوع الوظيفة")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        categories = ["مطور", "مصمم", "محاسب", "مدير", "أخرى"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 20)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def create_settings_tab(self):
        """تبويب الإعدادات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم معلومات الشركة
        company_section = self.create_company_info_section()
        layout.addWidget(company_section)
        
        # قسم تغيير كلمة المرور
        password_section = self.create_password_section()
        layout.addWidget(password_section)
        
        # قسم الإشعارات
        notifications_section = self.create_notifications_section()
        layout.addWidget(notifications_section)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_company_info_section(self):
        """قسم معلومات الشركة"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("معلومات الشركة")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("اسم الشركة:"), 0, 0)
        self.company_name_input = QLineEdit(self.company_name)
        self.company_name_input.setReadOnly(True)
        self.company_name_input.setStyleSheet(self.input_style())
        grid.addWidget(self.company_name_input, 0, 1)
        
        grid.addWidget(QLabel("البريد الإلكتروني:"), 1, 0)
        email_input = QLineEdit(self.company_email)
        email_input.setReadOnly(True)
        email_input.setStyleSheet(self.input_style())
        grid.addWidget(email_input, 1, 1)
        
        layout.addWidget(title)
        layout.addLayout(grid)
        
        frame.setLayout(layout)
        return frame
    
    def create_password_section(self):
        """قسم تغيير كلمة المرور"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("تغيير كلمة المرور")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        
        grid = QGridLayout()
        
        grid.addWidget(QLabel("كلمة المرور القديمة:"), 0, 0)
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setStyleSheet(self.input_style())
        grid.addWidget(self.old_password, 0, 1)
        
        grid.addWidget(QLabel("كلمة المرور الجديدة:"), 1, 0)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(self.input_style())
        grid.addWidget(self.new_password, 1, 1)
        
        grid.addWidget(QLabel("تأكيد كلمة المرور:"), 2, 0)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(self.input_style())
        grid.addWidget(self.confirm_password, 2, 1)
        
        change_btn = QPushButton("تغيير كلمة المرور")
        change_btn.setStyleSheet(self.button_style("#667eea", "#764ba2"))
        change_btn.clicked.connect(self.change_password)
        
        layout.addWidget(title)
        layout.addLayout(grid)
        layout.addWidget(change_btn)
        
        frame.setLayout(layout)
        return frame
    
    def create_notifications_section(self):
        """قسم إعدادات الإشعارات"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("إعدادات الإشعارات")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        
        info = QLabel("سيتم إضافة نظام الإشعارات قريباً...")
        info.setStyleSheet("color: #666;")
        
        layout.addWidget(title)
        layout.addWidget(info)
        
        frame.setLayout(layout)
        return frame
    
    def create_reports_tab(self):
        """تبويب التقارير"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        
        title = QLabel("تصدير التقارير")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        # خيارات التقرير
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("نوع التقرير:"))
        report_type = QComboBox()
        report_type.addItems(["تقرير شامل", "المقبولين فقط", "المرفوضين فقط", "قيد المراجعة"])
        report_type.setStyleSheet(self.combo_style())
        options_layout.addWidget(report_type)
        
        options_layout.addWidget(QLabel("الصيغة:"))
        format_combo = QComboBox()
        format_combo.addItems(["PDF", "Excel", "CSV"])
        format_combo.setStyleSheet(self.combo_style())
        options_layout.addWidget(format_combo)
        
        export_btn = QPushButton("📥 تصدير التقرير")
        export_btn.setStyleSheet(self.button_style("#4CAF50", "#388E3C"))
        export_btn.clicked.connect(self.export_report)
        
        frame_layout.addWidget(title)
        frame_layout.addLayout(options_layout)
        frame_layout.addWidget(export_btn)
        
        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """تحميل البيانات من Firebase"""
        try:
            cref_db = db.reference('companies')
            all_companies = cref_db.get()
            
            if all_companies:
                for cid, data in all_companies.items():
                    if data.get('email') == self.company_email:
                        self.company_id = cid
                        break
            
            self.load_resume_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {str(e)}")
    
    def load_resume_stats(self):
        """تحميل إحصائيات السير الذاتية"""
        try:
            uref = db.reference('users')
            all_users = uref.get()
            
            approved = pending = rejected = 0
            total_rating = 0
            rating_count = 0
            recent_apps = []
            
            if all_users:
                for user_id, user in all_users.items():
                    if user.get("company") == self.company_name:
                        status = user.get("status", "").lower()
                        
                        if status == "approved":
                            approved += 1
                        elif status == "pending":
                            pending += 1
                        elif status == "rejected":
                            rejected += 1
                        
                        # حساب متوسط التقييم
                        rating = user.get("raiting", 0)
                        if rating:
                            try:
                                total_rating += float(rating)
                                rating_count += 1
                            except:
                                pass
                        
                        # إضافة للطلبات الحديثة
                        recent_apps.append({
                            'name': user.get('full_name', 'غير معروف'),
                            'job': user.get('job', 'غير محدد'),
                            'status': status
                        })
            
            total = approved + pending + rejected
            
            # تحديث البطاقات
            self.total_card.update_value(total)
            self.approved_card.update_value(approved)
            self.pending_card.update_value(pending)
            self.rejected_card.update_value(rejected)
            
            # تحديث قائمة الطلبات الحديثة
            recent_text = ""
            for app in recent_apps[:5]:  # أحدث 5 طلبات
                status_emoji = "✅" if app['status'] == "approved" else "⏳" if app['status'] == "pending" else "❌"
                recent_text += f"{status_emoji} {app['name']} - {app['job']}\n"
            
            self.recent_list.setText(recent_text if recent_text else "لا توجد طلبات حديثة")
            
        except Exception as e:
            print(f"خطأ في تحميل الإحصائيات: {str(e)}")
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_resume_stats()
        QMessageBox.information(self, "تحديث", "تم تحديث البيانات بنجاح!")
    
    def change_password(self):
        """تغيير كلمة المرور"""
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        
        if not all([old_pass, new_pass, confirm_pass]):
            QMessageBox.warning(self, "تنبيه", "جميع الحقول مطلوبة.")
            return
        
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "تنبيه", "كلمتا المرور غير متطابقتين.")
            return
        
        if len(new_pass) < 6:
            QMessageBox.warning(self, "تنبيه", "كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
            return
        
        try:
            cref_db = db.reference(f'companies/{self.company_id}')
            company_data = cref_db.get()
            
            if company_data.get('password') != old_pass:
                QMessageBox.critical(self, "خطأ", "كلمة المرور القديمة غير صحيحة.")
                return
            
            cref_db.update({'password': new_pass})
            QMessageBox.information(self, "نجح", "تم تغيير كلمة المرور بنجاح!")
            
            self.old_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحديث كلمة المرور: {str(e)}")
    
    def export_report(self):
        """تصدير التقرير"""
        QMessageBox.information(self, "تصدير", "سيتم إضافة ميزة التصدير قريباً...")
    
    # أنماط CSS
    def button_style(self, color1, color2):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                padding: 11px 19px 9px 21px;
            }}
        """
    
    def input_style(self):
        return """
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """
    
    def combo_