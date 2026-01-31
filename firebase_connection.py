"""
Firebase Connection Module
يوفر اتصال آمن ومستقر مع Firebase Realtime Database
"""

import firebase_admin
from firebase_admin import credentials, db
from utils import resource_path
import sys
import os

def initialize_firebase():
    """تهيئة Firebase بشكل آمن"""
    try:
        # التحقق من وجود تطبيق Firebase مفعّل مسبقاً
        if firebase_admin._apps:
            print("✅ Firebase already initialized")
            return True
        
        # الحصول على مسار ملف الاعتماد
        cred_path = resource_path("recruitmentify.json")
        
        if not os.path.exists(cred_path):
            print(f"❌ Firebase credentials file not found at: {cred_path}")
            return False
        
        # تحميل بيانات الاعتماد
        cred = credentials.Certificate(cred_path)
        
        # تهيئة Firebase
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://recruitmentify-803e7-default-rtdb.firebaseio.com/'
        })
        
        print("✅ Firebase initialized successfully")
        print(f"📁 Credentials loaded from: {cred_path}")
        return True
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Check if recruitmentify.json exists")
        print("2. Verify database URL is correct")
        print("3. Ensure internet connection is active")
        print("4. Check Firebase project permissions")
        return False

# تهيئة Firebase عند استيراد الموديول
firebase_initialized = initialize_firebase()

if not firebase_initialized:
    print("\n⚠️ WARNING: Firebase not initialized properly!")
    print("The application may not work correctly.")
    print("Please check the error messages above.\n")

# الحصول على مراجع قاعدة البيانات
try:
    ref = db.reference('users')
    cref = db.reference('companies')
    jref = db.reference('jops')
    
    print("✅ Database references created successfully")
    print("   - users")
    print("   - companies")
    print("   - jops")
    
except Exception as e:
    print(f"❌ Failed to create database references: {str(e)}")
    # إنشاء مراجع وهمية لتجنب الأخطاء
    ref = None
    cref = None
    jref = None


def test_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        if ref is None:
            print("❌ Database reference is None")
            return False
        
        # محاولة قراءة بسيطة
        data = ref.limit_to_first(1).get()
        print("✅ Connection test successful")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


def get_database_info():
    """الحصول على معلومات قاعدة البيانات"""
    try:
        if not firebase_initialized:
            return {
                'status': 'Not Initialized',
                'users': 0,
                'companies': 0,
                'jobs': 0
            }
        
        users_count = len(ref.get() or {})
        companies_count = len(cref.get() or {})
        jobs_count = len(jref.get() or {})
        
        return {
            'status': 'Connected',
            'users': users_count,
            'companies': companies_count,
            'jobs': jobs_count
        }
        
    except Exception as e:
        print(f"❌ Error getting database info: {str(e)}")
        return {
            'status': 'Error',
            'error': str(e)
        }


# عرض معلومات الاتصال عند الاستيراد
if __name__ != "__main__":
    info = get_database_info()
    if info['status'] == 'Connected':
        print(f"\n📊 Database Statistics:")
        print(f"   Users: {info['users']}")
        print(f"   Companies: {info['companies']}")
        print(f"   Jobs: {info['jobs']}\n")


# للاختبار المباشر
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Firebase Connection Test")
    print("="*50 + "\n")
    
    if test_connection():
        info = get_database_info()
        print("\n📊 Database Info:")
        for key, value in info.items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ Connection test failed!")
    
    print("\n" + "="*50)