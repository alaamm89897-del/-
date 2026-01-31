"""
Functions Module - Enhanced
يحتوي على وظائف معالجة السير الذاتية والتفاعل مع الـ AI
"""

import os
import sys
import base64
from firebase_connection import ref
from dotenv import load_dotenv
import google.generativeai as genai


def get_gemini_api_key():
    """
    الحصول على مفتاح API من عدة مصادر
    Returns: API key or None
    """
    # 1. محاولة الحصول من متغيرات البيئة
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        print("✅ API key loaded from environment")
        return api_key
    
    # 2. محاولة القراءة من ملف .env
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
                        api_key = line.strip().split('=', 1)[1].strip('"\'')
                        print("✅ API key loaded from .env file")
                        return api_key
        except Exception as e:
            print(f"⚠️ Error reading .env file: {e}")
    
    # 3. محاولة استخدام dotenv
    try:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            print("✅ API key loaded via dotenv")
            return api_key
    except:
        pass
    
    # 4. استخدام المفتاح الاحتياطي
    fallback_key = "AIzaSyAldaZINHy1iNK88iY5fG0XQ5paBNfARXY"
    print("⚠️ Using fallback API key")
    return fallback_key


def pdf_push_to_ai(pdfpath, ai_value):
    """
    إرسال ملف PDF للذكاء الاصطناعي لتحليله
    
    Args:
        pdfpath: مسار ملف PDF
        ai_value: الكلمات المفتاحية للوظيفة
        
    Returns:
        نص يحتوي على التقييم والملخص
    """
    try:
        # التحقق من وجود الملف
        if not os.path.exists(pdfpath):
            raise FileNotFoundError(f"PDF file not found: {pdfpath}")
        
        # الحصول على API key
        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("No API key available")
        
        # تكوين Gemini API
        genai.configure(api_key=api_key)
        
        print(f"📄 Processing PDF: {os.path.basename(pdfpath)}")
        print(f"🎯 Keywords: {ai_value}")
        
        # تحميل الملف
        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_file = genai.upload_file(path=pdfpath, display_name="resume.pdf")
        
        print("⏳ Uploading to AI...")
        
        # إنشاء الـ prompt المحسّن
        prompt = f"""
        Analyze this CV/Resume and provide:
        
        1. A comprehensive summary of the candidate's skills and experience
        2. Key strengths relevant to the position
        3. Areas for improvement
        4. An accurate rating from 1 to 100 based on these keywords: {ai_value}
        
        Important:
        - Give precise ratings (avoid round numbers like 85, 95)
        - Use specific ratings like 73, 82, 88, etc.
        - Be fair and objective in your assessment
        
        CRITICAL: Output MUST be in this EXACT format:
        Rating: <number>
        Summary: <detailed summary>
        
        Keep it professional and concise.
        """
        
        # إرسال للـ AI
        response = model.generate_content([sample_file, prompt])
        
        print("✅ AI analysis completed")
        
        # حذف الملف المؤقت من Gemini
        try:
            sample_file.delete()
        except:
            pass
        
        return response.text
        
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        raise
    except Exception as e:
        print(f"❌ AI processing error: {e}")
        print(f"   Type: {type(e).__name__}")
        raise


def encode_file_to_base64(file_path):
    """
    تحويل ملف إلى Base64
    
    Args:
        file_path: مسار الملف
        
    Returns:
        نص Base64 أو None
    """
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        # قراءة الملف
        with open(file_path, "rb") as file:
            file_data = file.read()
        
        # تحويل إلى Base64
        encoded_string = base64.b64encode(file_data).decode("utf-8")
        
        # حساب حجم البيانات
        size_kb = len(encoded_string) / 1024
        print(f"✅ File encoded: {size_kb:.2f} KB")
        
        return encoded_string
        
    except Exception as e:
        print(f"❌ Encoding error: {e}")
        return None


def push_customer_data_to_firebase(full_name, email, status, rating, summary, file_path, company, job):
    """
    حفظ بيانات المتقدم في Firebase
    
    Args:
        full_name: الاسم الكامل
        email: البريد الإلكتروني
        status: الحالة (Pending/Approved/Rejected)
        rating: التقييم
        summary: الملخص
        file_path: مسار ملف السيرة الذاتية
        company: اسم الشركة
        job: اسم الوظيفة
    """
    try:
        print("\n" + "="*50)
        print("💾 Saving to Firebase...")
        print("="*50)
        
        # إعداد بيانات المستخدم
        user_data = {
            "full_name": full_name,
            "email": email,
            "status": status,
            "raiting": rating,  # ملاحظة: الاسم بنفس الشكل في قاعدة البيانات
            "summary": summary,
            "company": company,
            "job": job
        }
        
        print(f"👤 Name: {full_name}")
        print(f"📧 Email: {email}")
        print(f"💼 Company: {company}")
        print(f"🎯 Job: {job}")
        print(f"⭐ Rating: {rating}/100")
        
        # التحقق من نوع الملف
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported")
        
        print(f"📄 Processing file: {os.path.basename(file_path)}")
        
        # تحويل الملف إلى Base64
        encoded_file = encode_file_to_base64(file_path)
        
        if not encoded_file:
            raise Exception("Failed to encode file")
        
        # إضافة البيانات المشفرة
        user_data["resume_data"] = encoded_file
        
        print("🔐 File encoded successfully")
        
        # حفظ في قاعدة البيانات
        if ref is None:
            raise Exception("Firebase reference is None")
        
        new_user_ref = ref.push(user_data)
        
        print(f"✅ Data saved successfully!")
        print(f"🔑 Firebase Key: {new_user_ref.key}")
        print("="*50 + "\n")
        
        return new_user_ref.key
        
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        raise
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        print(f"   Type: {type(e).__name__}")
        raise


def validate_email(email):
    """
    التحقق من صحة البريد الإلكتروني
    
    Args:
        email: البريد الإلكتروني
        
    Returns:
        True إذا كان صحيحاً
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_pdf_file(file_path):
    """
    التحقق من صحة ملف PDF
    
    Args:
        file_path: مسار الملف
        
    Returns:
        (bool, str): (صحيح/خطأ, رسالة)
    """
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # التحقق من الامتداد
    if not file_path.lower().endswith('.pdf'):
        return False, "File is not a PDF"
    
    # التحقق من حجم الملف (أقل من 10 MB)
    file_size = os.path.getsize(file_path)
    max_size = 10 * 1024 * 1024  # 10 MB
    
    if file_size > max_size:
        return False, f"File too large ({file_size / (1024*1024):.2f} MB). Maximum is 10 MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    # التحقق من أن الملف PDF حقيقي (يبدأ بـ %PDF)
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                return False, "File is not a valid PDF"
    except:
        return False, "Cannot read file"
    
    return True, "Valid PDF file"


def get_application_stats(company_name):
    """
    الحصول على إحصائيات الطلبات لشركة معينة
    
    Args:
        company_name: اسم الشركة
        
    Returns:
        dict: إحصائيات الطلبات
    """
    try:
        if ref is None:
            return None
        
        all_users = ref.get()
        
        if not all_users:
            return {
                'total': 0,
                'pending': 0,
                'approved': 0,
                'rejected': 0,
                'avg_rating': 0
            }
        
        # فلترة حسب الشركة
        company_users = [
            user for user in all_users.values()
            if user.get('company') == company_name
        ]
        
        if not company_users:
            return {
                'total': 0,
                'pending': 0,
                'approved': 0,
                'rejected': 0,
                'avg_rating': 0
            }
        
        # حساب الإحصائيات
        stats = {
            'total': len(company_users),
            'pending': sum(1 for u in company_users if u.get('status') == 'Pending'),
            'approved': sum(1 for u in company_users if u.get('status') == 'Approved'),
            'rejected': sum(1 for u in company_users if u.get('status') == 'Rejected'),
        }
        
        # حساب متوسط التقييم
        ratings = [
            float(u.get('raiting', 0))
            for u in company_users
            if u.get('raiting')
        ]
        
        stats['avg_rating'] = sum(ratings) / len(ratings) if ratings else 0
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None


# اختبار الوظائف
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Functions Module Test")
    print("="*50 + "\n")
    
    # اختبار API key
    print("1. Testing API Key...")
    key = get_gemini_api_key()
    print(f"   API Key: {'✅ Found' if key else '❌ Not Found'}\n")
    
    # اختبار التحقق من البريد
    print("2. Testing Email Validation...")
    test_emails = [
        "test@example.com",
        "invalid.email",
        "user@domain.co.uk"
    ]
    
    for email in test_emails:
        valid = validate_email(email)
        print(f"   {email}: {'✅ Valid' if valid else '❌ Invalid'}")
    
    print("\n" + "="*50)