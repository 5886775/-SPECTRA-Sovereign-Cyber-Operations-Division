#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔰 EYE OF HORUS - نظام حماية الوعي الوطني المصري
نظام استخبارات إلكترونية متكامل للحماية من الحروب النفسية والتضليل الإلكتروني

المطور: Manus AI
الإصدار: 2.0 Advanced
التاريخ: 2025-08-03
"""

import os
import sys
import json
import time
import sqlite3
import hashlib
import threading
import subprocess
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import re
import random
import base64
from cryptography.fernet import Fernet
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# ASCII Art للنظام
SYSTEM_BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ███████╗██╗   ██╗███████╗     ██████╗ ███████╗    ██╗  ██╗ ██████╗ ██████╗ ║
║    ██╔════╝╚██╗ ██╔╝██╔════╝    ██╔═══██╗██╔════╝    ██║  ██║██╔═══██╗██╔══██╗║
║    █████╗   ╚████╔╝ █████╗      ██║   ██║█████╗      ███████║██║   ██║██████╔╝║
║    ██╔══╝    ╚██╔╝  ██╔══╝      ██║   ██║██╔══╝      ██╔══██║██║   ██║██╔══██╗║
║    ███████╗   ██║   ███████╗    ╚██████╔╝██║         ██║  ██║╚██████╔╝██║  ██║║
║    ╚══════╝   ╚═╝   ╚══════╝     ╚═════╝ ╚═╝         ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝║
║                                                                              ║
║                    🛡️ نظام حماية الوعي الوطني المصري 🛡️                    ║
║                                                                              ║
║    🔰 نظام استخبارات إلكترونية متكامل للحماية من الحروب النفسية            ║
║    🔰 رصد وتحليل حملات التضليل الإلكتروني                                  ║
║    🔰 الردع التلقائي والإعلام المضاد                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

class EyeOfHorusSystem:
    def __init__(self):
        self.version = "2.0 Advanced"
        self.start_time = datetime.now()
        self.config = self.load_config()
        self.setup_logging()
        self.setup_database()
        self.encryption_key = self.generate_encryption_key()
        self.running_modules = {}
        
        # إعداد المجلدات
        self.create_directories()
        
        print(SYSTEM_BANNER)
        print(f"🔰 تم تهيئة نظام EYE OF HORUS بنجاح")
        print(f"📅 وقت البدء: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔢 الإصدار: {self.version}")
        print("=" * 80)

    def load_config(self):
        """تحميل إعدادات النظام"""
        default_config = {
            "database_path": "eyeofhorus.db",
            "log_level": "INFO",
            "max_threads": 10,
            "scan_interval": 300,  # 5 دقائق
            "platforms": {
                "twitter": {"enabled": True, "priority": "high"},
                "facebook": {"enabled": True, "priority": "high"},
                "telegram": {"enabled": True, "priority": "medium"},
                "youtube": {"enabled": True, "priority": "medium"}
            },
            "keywords": [
                "مصر", "السيسي", "الحكومة المصرية", "القاهرة", "الإسكندرية",
                "تظاهرات", "احتجاجات", "فساد", "اقتصاد مصر", "الجيش المصري"
            ],
            "threat_indicators": [
                "انقلاب", "ثورة", "إسقاط النظام", "تخريب", "عنف",
                "إرهاب", "تفجير", "اغتيال", "فوضى", "انهيار"
            ]
        }
        
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_config
        else:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config

    def setup_logging(self):
        """إعداد نظام السجلات"""
        logging.basicConfig(
            level=getattr(logging, self.config.get("log_level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('eyeofhorus.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('EyeOfHorus')

    def setup_database(self):
        """إعداد قاعدة البيانات"""
        self.db_path = self.config.get("database_path", "eyeofhorus.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # إنشاء الجداول
        self.create_tables()

    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT,
                url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'new',
                hash TEXT UNIQUE,
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT,
                followers_count INTEGER,
                following_count INTEGER,
                account_created DATE,
                verified BOOLEAN DEFAULT FALSE,
                suspicious_score INTEGER DEFAULT 0,
                last_activity DATETIME,
                metadata TEXT,
                UNIQUE(platform, username)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date DATETIME,
                end_date DATETIME,
                platforms TEXT,
                keywords TEXT,
                threat_level TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id INTEGER,
                file_path TEXT,
                file_hash TEXT,
                file_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                encrypted BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (threat_id) REFERENCES threats (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                report_type TEXT,
                generated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                threats_included TEXT,
                file_path TEXT
            )
            """
        ]
        
        for table in tables:
            self.conn.execute(table)
        self.conn.commit()

    def create_directories(self):
        """إنشاء المجلدات المطلوبة"""
        directories = [
            "evidence", "reports", "logs", "temp", "archive",
            "screenshots", "profiles", "campaigns"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def generate_encryption_key(self):
        """إنشاء مفتاح التشفير"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_data(self, data):
        """تشفير البيانات"""
        f = Fernet(self.encryption_key)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return f.encrypt(data)

    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_data).decode('utf-8')

    def calculate_hash(self, content):
        """حساب الهاش للمحتوى"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def install_dependencies(self):
        """تثبيت المتطلبات تلقائياً"""
        print("🔧 جاري تثبيت المتطلبات...")
        
        required_packages = [
            "requests", "beautifulsoup4", "selenium", "cryptography",
            "nltk", "textblob", "pandas", "numpy", "matplotlib",
            "flask", "flask-cors", "sqlite3"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} متوفر")
            except ImportError:
                print(f"📦 تثبيت {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    def check_system_requirements(self):
        """فحص متطلبات النظام"""
        print("🔍 فحص متطلبات النظام...")
        
        # فحص Python
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 7:
            print(f"✅ Python {python_version.major}.{python_version.minor} متوافق")
        else:
            print("❌ يتطلب Python 3.7 أو أحدث")
            return False
        
        # فحص المساحة المتاحة
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        if free_space >= 1:
            print(f"✅ مساحة متاحة: {free_space:.1f} GB")
        else:
            print("⚠️ مساحة قليلة متاحة")
        
        # فحص الاتصال بالإنترنت
        try:
            requests.get("https://www.google.com", timeout=5)
            print("✅ الاتصال بالإنترنت متاح")
        except:
            print("❌ لا يوجد اتصال بالإنترنت")
            return False
        
        return True

class OSINTModule:
    """وحدة رصد وتتبع الحملات العدائية"""
    
    def __init__(self, system):
        self.system = system
        self.logger = system.logger
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """إعداد جلسة الطلبات"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(headers)

    def scan_platform(self, platform, keywords):
        """مسح منصة معينة"""
        print(f"🔍 مسح {platform} للكلمات المفتاحية: {', '.join(keywords)}")
        
        results = []
        
        if platform == "twitter":
            results = self.scan_twitter(keywords)
        elif platform == "facebook":
            results = self.scan_facebook(keywords)
        elif platform == "telegram":
            results = self.scan_telegram(keywords)
        elif platform == "youtube":
            results = self.scan_youtube(keywords)
        
        return results

    def scan_twitter(self, keywords):
        """مسح تويتر (محاكاة)"""
        # في التطبيق الحقيقي، سيتم استخدام تقنيات web scraping متقدمة
        print("🐦 مسح Twitter...")
        
        # محاكاة النتائج
        mock_results = [
            {
                "platform": "twitter",
                "content": "محتوى مشبوه يحتوي على تحريض ضد الحكومة المصرية",
                "author": "@suspicious_account",
                "url": "https://twitter.com/suspicious_account/status/123456789",
                "timestamp": datetime.now(),
                "severity": "high"
            }
        ]
        
        return mock_results

    def scan_facebook(self, keywords):
        """مسح فيسبوك (محاكاة)"""
        print("📘 مسح Facebook...")
        
        mock_results = [
            {
                "platform": "facebook",
                "content": "منشور يحتوي على معلومات مضللة حول الاقتصاد المصري",
                "author": "حساب مشبوه",
                "url": "https://facebook.com/post/123456789",
                "timestamp": datetime.now(),
                "severity": "medium"
            }
        ]
        
        return mock_results

    def scan_telegram(self, keywords):
        """مسح تليجرام (محاكاة)"""
        print("✈️ مسح Telegram...")
        
        mock_results = [
            {
                "platform": "telegram",
                "content": "رسالة في قناة تحتوي على دعوة للتظاهر",
                "author": "قناة مشبوهة",
                "url": "https://t.me/suspicious_channel/123",
                "timestamp": datetime.now(),
                "severity": "high"
            }
        ]
        
        return mock_results

    def scan_youtube(self, keywords):
        """مسح يوتيوب (محاكاة)"""
        print("📺 مسح YouTube...")
        
        mock_results = [
            {
                "platform": "youtube",
                "content": "فيديو يحتوي على انتقادات حادة للحكومة",
                "author": "قناة معارضة",
                "url": "https://youtube.com/watch?v=123456789",
                "timestamp": datetime.now(),
                "severity": "medium"
            }
        ]
        
        return mock_results

    def analyze_content(self, content):
        """تحليل المحتوى للكشف عن التهديدات"""
        threat_score = 0
        threat_indicators = self.system.config.get("threat_indicators", [])
        
        for indicator in threat_indicators:
            if indicator in content.lower():
                threat_score += 10
        
        # تحديد مستوى الخطورة
        if threat_score >= 30:
            severity = "critical"
        elif threat_score >= 20:
            severity = "high"
        elif threat_score >= 10:
            severity = "medium"
        else:
            severity = "low"
        
        return {
            "threat_score": threat_score,
            "severity": severity,
            "indicators_found": [ind for ind in threat_indicators if ind in content.lower()]
        }

class AIAnalysisModule:
    """محرك التحليل الاستخباراتي والذكاء الاصطناعي"""
    
    def __init__(self, system):
        self.system = system
        self.logger = system.logger

    def analyze_threat(self, threat_data):
        """تحليل التهديد باستخدام الذكاء الاصطناعي"""
        print(f"🧠 تحليل التهديد من {threat_data['platform']}")
        
        analysis = {
            "threat_id": threat_data.get("id"),
            "content_analysis": self.analyze_content_sentiment(threat_data["content"]),
            "author_analysis": self.analyze_author_profile(threat_data.get("author")),
            "network_analysis": self.analyze_social_network(threat_data),
            "geolocation": self.estimate_geolocation(threat_data),
            "risk_assessment": self.calculate_risk_score(threat_data)
        }
        
        return analysis

    def analyze_content_sentiment(self, content):
        """تحليل المشاعر في المحتوى"""
        # تحليل بسيط للمشاعر (في التطبيق الحقيقي سيتم استخدام NLP متقدم)
        negative_words = ["سيء", "فاسد", "ظالم", "مجرم", "كاذب", "فاشل"]
        positive_words = ["جيد", "ممتاز", "رائع", "نجح", "تقدم"]
        
        negative_count = sum(1 for word in negative_words if word in content)
        positive_count = sum(1 for word in positive_words if word in content)
        
        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "negative_score": negative_count,
            "positive_score": positive_count,
            "emotional_intensity": abs(negative_count - positive_count)
        }

    def analyze_author_profile(self, author):
        """تحليل ملف المؤلف"""
        if not author:
            return {"profile_risk": "unknown"}
        
        # تحليل بسيط للملف الشخصي
        risk_indicators = ["bot", "fake", "anonymous", "new"]
        risk_score = 0
        
        for indicator in risk_indicators:
            if indicator in author.lower():
                risk_score += 25
        
        return {
            "author": author,
            "risk_score": risk_score,
            "profile_risk": "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
        }

    def analyze_social_network(self, threat_data):
        """تحليل الشبكة الاجتماعية"""
        return {
            "network_size": random.randint(10, 1000),
            "connection_strength": random.choice(["weak", "medium", "strong"]),
            "bot_probability": random.randint(0, 100)
        }

    def estimate_geolocation(self, threat_data):
        """تقدير الموقع الجغرافي"""
        # في التطبيق الحقيقي سيتم استخدام تحليل متقدم للموقع
        possible_locations = ["مصر", "السعودية", "الإمارات", "قطر", "تركيا", "غير محدد"]
        
        return {
            "estimated_country": random.choice(possible_locations),
            "confidence": random.randint(30, 90),
            "timezone_analysis": "UTC+2"
        }

    def calculate_risk_score(self, threat_data):
        """حساب درجة المخاطر الإجمالية"""
        base_score = 0
        
        # عوامل المخاطر
        if threat_data.get("severity") == "critical":
            base_score += 40
        elif threat_data.get("severity") == "high":
            base_score += 30
        elif threat_data.get("severity") == "medium":
            base_score += 20
        
        # إضافة عوامل أخرى
        base_score += random.randint(0, 20)  # عوامل عشوائية للمحاكاة
        
        return min(base_score, 100)

class AutoReportModule:
    """نظام الردع الإلكتروني التلقائي"""
    
    def __init__(self, system):
        self.system = system
        self.logger = system.logger

    def process_threat(self, threat_data, analysis):
        """معالجة التهديد واتخاذ الإجراءات المناسبة"""
        risk_score = analysis.get("risk_assessment", 0)
        
        actions_taken = []
        
        if risk_score >= 70:
            actions_taken.extend(self.high_risk_response(threat_data))
        elif risk_score >= 40:
            actions_taken.extend(self.medium_risk_response(threat_data))
        else:
            actions_taken.extend(self.low_risk_response(threat_data))
        
        return actions_taken

    def high_risk_response(self, threat_data):
        """استجابة للتهديدات عالية المخاطر"""
        actions = []
        
        # بلاغ فوري
        if self.submit_urgent_report(threat_data):
            actions.append("urgent_report_submitted")
        
        # إنشاء محتوى مضاد
        counter_content = self.generate_counter_content(threat_data)
        if counter_content:
            actions.append("counter_content_generated")
        
        # تنبيه الجهات المختصة
        if self.alert_authorities(threat_data):
            actions.append("authorities_alerted")
        
        return actions

    def medium_risk_response(self, threat_data):
        """استجابة للتهديدات متوسطة المخاطر"""
        actions = []
        
        # بلاغ عادي
        if self.submit_standard_report(threat_data):
            actions.append("standard_report_submitted")
        
        # مراقبة إضافية
        if self.add_to_watchlist(threat_data):
            actions.append("added_to_watchlist")
        
        return actions

    def low_risk_response(self, threat_data):
        """استجابة للتهديدات منخفضة المخاطر"""
        actions = []
        
        # توثيق فقط
        if self.document_threat(threat_data):
            actions.append("threat_documented")
        
        return actions

    def submit_urgent_report(self, threat_data):
        """تقديم بلاغ عاجل"""
        print(f"🚨 تقديم بلاغ عاجل للتهديد: {threat_data.get('id')}")
        # في التطبيق الحقيقي سيتم إرسال البلاغ للجهات المختصة
        return True

    def submit_standard_report(self, threat_data):
        """تقديم بلاغ عادي"""
        print(f"📋 تقديم بلاغ عادي للتهديد: {threat_data.get('id')}")
        return True

    def generate_counter_content(self, threat_data):
        """إنشاء محتوى مضاد"""
        print(f"📝 إنشاء محتوى مضاد للتهديد: {threat_data.get('id')}")
        
        counter_templates = [
            "تحذير: تم رصد محتوى مضلل يستهدف الأمن القومي المصري",
            "تنبيه: حملة تضليل منظمة تستهدف استقرار مصر",
            "إنذار: محاولة تلاعب بالرأي العام المصري"
        ]
        
        return random.choice(counter_templates)

    def alert_authorities(self, threat_data):
        """تنبيه الجهات المختصة"""
        print(f"🚔 تنبيه الجهات المختصة للتهديد: {threat_data.get('id')}")
        return True

    def add_to_watchlist(self, threat_data):
        """إضافة للقائمة المراقبة"""
        print(f"👁️ إضافة للمراقبة: {threat_data.get('author')}")
        return True

    def document_threat(self, threat_data):
        """توثيق التهديد"""
        print(f"📄 توثيق التهديد: {threat_data.get('id')}")
        return True

class EvidenceArchiveModule:
    """نظام توثيق الأدلة"""
    
    def __init__(self, system):
        self.system = system
        self.logger = system.logger

    def archive_threat(self, threat_data, analysis, actions):
        """أرشفة التهديد والأدلة"""
        print(f"🗄️ أرشفة التهديد: {threat_data.get('id')}")
        
        # إنشاء هاش للمحتوى
        content_hash = self.system.calculate_hash(threat_data["content"])
        
        # حفظ في قاعدة البيانات
        threat_id = self.save_to_database(threat_data, content_hash)
        
        # حفظ الأدلة
        evidence_files = self.save_evidence_files(threat_data, analysis, threat_id)
        
        # إنشاء تقرير
        report_path = self.generate_evidence_report(threat_data, analysis, actions, threat_id)
        
        return {
            "threat_id": threat_id,
            "content_hash": content_hash,
            "evidence_files": evidence_files,
            "report_path": report_path
        }

    def save_to_database(self, threat_data, content_hash):
        """حفظ في قاعدة البيانات"""
        cursor = self.system.conn.cursor()
        
        cursor.execute("""
            INSERT INTO threats (platform, content, author, url, severity, hash, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            threat_data["platform"],
            threat_data["content"],
            threat_data.get("author"),
            threat_data.get("url"),
            threat_data.get("severity"),
            content_hash,
            json.dumps(threat_data, ensure_ascii=False, default=str)
        ))
        
        threat_id = cursor.lastrowid
        self.system.conn.commit()
        
        return threat_id

    def save_evidence_files(self, threat_data, analysis, threat_id):
        """حفظ ملفات الأدلة"""
        evidence_files = []
        
        # حفظ المحتوى الأصلي
        content_file = f"evidence/threat_{threat_id}_content.txt"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(threat_data["content"])
        evidence_files.append(content_file)
        
        # حفظ التحليل
        analysis_file = f"evidence/threat_{threat_id}_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
        evidence_files.append(analysis_file)
        
        # تشفير الملفات الحساسة
        for file_path in evidence_files:
            self.encrypt_evidence_file(file_path, threat_id)
        
        return evidence_files

    def encrypt_evidence_file(self, file_path, threat_id):
        """تشفير ملف الأدلة"""
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = self.system.encrypt_data(file_data)
        
        encrypted_path = f"{file_path}.encrypted"
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # حذف الملف الأصلي
        os.remove(file_path)
        
        # تسجيل في قاعدة البيانات
        cursor = self.system.conn.cursor()
        cursor.execute("""
            INSERT INTO evidence (threat_id, file_path, file_hash, file_type, encrypted)
            VALUES (?, ?, ?, ?, ?)
        """, (
            threat_id,
            encrypted_path,
            hashlib.sha256(file_data).hexdigest(),
            os.path.splitext(file_path)[1],
            True
        ))
        self.system.conn.commit()

    def generate_evidence_report(self, threat_data, analysis, actions, threat_id):
        """إنشاء تقرير الأدلة"""
        report_content = f"""
# تقرير الأدلة - التهديد رقم {threat_id}

## معلومات أساسية
- **رقم التهديد:** {threat_id}
- **المنصة:** {threat_data['platform']}
- **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **مستوى الخطورة:** {threat_data.get('severity', 'غير محدد')}

## المحتوى
```
{threat_data['content']}
```

## المؤلف
- **اسم المستخدم:** {threat_data.get('author', 'غير محدد')}
- **الرابط:** {threat_data.get('url', 'غير متاح')}

## التحليل
- **تحليل المشاعر:** {analysis.get('content_analysis', {}).get('sentiment', 'غير محدد')}
- **درجة المخاطر:** {analysis.get('risk_assessment', 0)}
- **الموقع المقدر:** {analysis.get('geolocation', {}).get('estimated_country', 'غير محدد')}

## الإجراءات المتخذة
{chr(10).join(f"- {action}" for action in actions)}

## التوقيع الرقمي
- **الهاش:** {self.system.calculate_hash(threat_data['content'])}
- **وقت الإنشاء:** {datetime.now().isoformat()}
"""
        
        report_path = f"reports/threat_{threat_id}_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path

class ReportGenerator:
    """مولد التقارير"""
    
    def __init__(self, system):
        self.system = system
        self.logger = system.logger

    def generate_summary_report(self):
        """إنشاء تقرير ملخص"""
        print("📊 إنشاء تقرير ملخص...")
        
        cursor = self.system.conn.cursor()
        
        # إحصائيات عامة
        cursor.execute("SELECT COUNT(*) FROM threats")
        total_threats = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM threats WHERE severity = 'critical'")
        critical_threats = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM threats WHERE severity = 'high'")
        high_threats = cursor.fetchone()[0]
        
        cursor.execute("SELECT platform, COUNT(*) FROM threats GROUP BY platform")
        platform_stats = cursor.fetchall()
        
        # إنشاء التقرير
        report_content = f"""
# تقرير ملخص نظام EYE OF HORUS

## الإحصائيات العامة
- **إجمالي التهديدات المكتشفة:** {total_threats}
- **التهديدات الحرجة:** {critical_threats}
- **التهديدات عالية الخطورة:** {high_threats}

## توزيع التهديدات حسب المنصة
{chr(10).join(f"- **{platform}:** {count}" for platform, count in platform_stats)}

## فترة التقرير
- **من:** {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}
- **إلى:** {datetime.now().strftime('%Y-%m-%d')}

## التوصيات
1. زيادة المراقبة للمنصات عالية النشاط
2. تحديث قوائم الكلمات المفتاحية
3. تعزيز آليات الاستجابة السريعة

---
*تم إنشاء هذا التقرير تلقائياً بواسطة نظام EYE OF HORUS*
"""
        
        report_path = f"reports/summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ تم إنشاء التقرير: {report_path}")
        return report_path

    def generate_detailed_report(self, threat_ids):
        """إنشاء تقرير مفصل"""
        print(f"📋 إنشاء تقرير مفصل لـ {len(threat_ids)} تهديد...")
        
        cursor = self.system.conn.cursor()
        
        report_content = "# تقرير مفصل - التهديدات المحددة\n\n"
        
        for threat_id in threat_ids:
            cursor.execute("SELECT * FROM threats WHERE id = ?", (threat_id,))
            threat = cursor.fetchone()
            
            if threat:
                report_content += f"""
## التهديد رقم {threat[0]}
- **المنصة:** {threat[1]}
- **المحتوى:** {threat[2][:200]}...
- **المؤلف:** {threat[3]}
- **التاريخ:** {threat[5]}
- **الخطورة:** {threat[6]}

---
"""
        
        report_path = f"reports/detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ تم إنشاء التقرير المفصل: {report_path}")
        return report_path

def main():
    """الدالة الرئيسية"""
    try:
        # تهيئة النظام
        system = EyeOfHorusSystem()
        
        # فحص المتطلبات
        if not system.check_system_requirements():
            print("❌ فشل في فحص متطلبات النظام")
            return
        
        # تثبيت المتطلبات
        system.install_dependencies()
        
        # تهيئة الوحدات
        osint = OSINTModule(system)
        ai_analysis = AIAnalysisModule(system)
        auto_report = AutoReportModule(system)
        evidence_archive = EvidenceArchiveModule(system)
        report_generator = ReportGenerator(system)
        
        print("\n🚀 بدء تشغيل نظام EYE OF HORUS")
        print("=" * 80)
        
        # القائمة الرئيسية
        while True:
            print("\n🔰 القائمة الرئيسية:")
            print("1. بدء مسح شامل")
            print("2. مسح منصة محددة")
            print("3. عرض التهديدات المكتشفة")
            print("4. إنشاء تقرير ملخص")
            print("5. إنشاء تقرير مفصل")
            print("6. إعدادات النظام")
            print("7. حالة النظام")
            print("0. خروج")
            
            choice = input("\n🔹 اختر العملية المطلوبة: ").strip()
            
            if choice == "1":
                # مسح شامل
                print("\n🔍 بدء المسح الشامل...")
                keywords = system.config.get("keywords", [])
                platforms = [p for p, config in system.config.get("platforms", {}).items() if config.get("enabled")]
                
                all_threats = []
                
                for platform in platforms:
                    threats = osint.scan_platform(platform, keywords)
                    all_threats.extend(threats)
                
                # معالجة التهديدات
                for threat in all_threats:
                    analysis = ai_analysis.analyze_threat(threat)
                    actions = auto_report.process_threat(threat, analysis)
                    archive_result = evidence_archive.archive_threat(threat, analysis, actions)
                    
                    print(f"✅ تم معالجة التهديد: {archive_result['threat_id']}")
                
                print(f"\n🎯 تم اكتشاف ومعالجة {len(all_threats)} تهديد")
            
            elif choice == "2":
                # مسح منصة محددة
                platforms = list(system.config.get("platforms", {}).keys())
                print("\nالمنصات المتاحة:")
                for i, platform in enumerate(platforms, 1):
                    print(f"{i}. {platform}")
                
                try:
                    platform_choice = int(input("اختر المنصة: ")) - 1
                    if 0 <= platform_choice < len(platforms):
                        platform = platforms[platform_choice]
                        keywords = system.config.get("keywords", [])
                        threats = osint.scan_platform(platform, keywords)
                        
                        for threat in threats:
                            analysis = ai_analysis.analyze_threat(threat)
                            actions = auto_report.process_threat(threat, analysis)
                            archive_result = evidence_archive.archive_threat(threat, analysis, actions)
                            print(f"✅ تم معالجة التهديد: {archive_result['threat_id']}")
                        
                        print(f"\n🎯 تم اكتشاف ومعالجة {len(threats)} تهديد من {platform}")
                except ValueError:
                    print("❌ اختيار غير صحيح")
            
            elif choice == "3":
                # عرض التهديدات
                cursor = system.conn.cursor()
                cursor.execute("SELECT id, platform, content, severity, timestamp FROM threats ORDER BY timestamp DESC LIMIT 10")
                threats = cursor.fetchall()
                
                if threats:
                    print("\n📋 آخر التهديدات المكتشفة:")
                    print("-" * 80)
                    for threat in threats:
                        print(f"🆔 {threat[0]} | 📱 {threat[1]} | ⚠️ {threat[3]} | 📅 {threat[4]}")
                        print(f"📝 {threat[2][:100]}...")
                        print("-" * 80)
                else:
                    print("📭 لا توجد تهديدات مكتشفة")
            
            elif choice == "4":
                # تقرير ملخص
                report_path = report_generator.generate_summary_report()
                print(f"📊 تم إنشاء التقرير: {report_path}")
            
            elif choice == "5":
                # تقرير مفصل
                cursor = system.conn.cursor()
                cursor.execute("SELECT id FROM threats ORDER BY timestamp DESC LIMIT 5")
                threat_ids = [row[0] for row in cursor.fetchall()]
                
                if threat_ids:
                    report_path = report_generator.generate_detailed_report(threat_ids)
                    print(f"📋 تم إنشاء التقرير المفصل: {report_path}")
                else:
                    print("📭 لا توجد تهديدات للتقرير")
            
            elif choice == "6":
                # إعدادات النظام
                print("\n⚙️ إعدادات النظام:")
                print("1. عرض الإعدادات الحالية")
                print("2. تحديث الكلمات المفتاحية")
                print("3. تحديث مؤشرات التهديد")
                
                setting_choice = input("اختر الإعداد: ").strip()
                
                if setting_choice == "1":
                    print("\n📋 الإعدادات الحالية:")
                    print(json.dumps(system.config, ensure_ascii=False, indent=2))
                
                elif setting_choice == "2":
                    new_keywords = input("أدخل الكلمات المفتاحية الجديدة (مفصولة بفواصل): ").split(',')
                    system.config["keywords"] = [kw.strip() for kw in new_keywords if kw.strip()]
                    print("✅ تم تحديث الكلمات المفتاحية")
                
                elif setting_choice == "3":
                    new_indicators = input("أدخل مؤشرات التهديد الجديدة (مفصولة بفواصل): ").split(',')
                    system.config["threat_indicators"] = [ind.strip() for ind in new_indicators if ind.strip()]
                    print("✅ تم تحديث مؤشرات التهديد")
            
            elif choice == "7":
                # حالة النظام
                print("\n📊 حالة النظام:")
                print(f"🕐 وقت التشغيل: {datetime.now() - system.start_time}")
                print(f"🔢 الإصدار: {system.version}")
                
                cursor = system.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM threats")
                total_threats = cursor.fetchone()[0]
                print(f"🎯 إجمالي التهديدات: {total_threats}")
                
                cursor.execute("SELECT COUNT(*) FROM threats WHERE date(timestamp) = date('now')")
                today_threats = cursor.fetchone()[0]
                print(f"📅 تهديدات اليوم: {today_threats}")
                
                print(f"💾 قاعدة البيانات: {system.db_path}")
                print(f"🔐 التشفير: مفعل")
            
            elif choice == "0":
                print("\n👋 شكراً لاستخدام نظام EYE OF HORUS")
                print("🛡️ حماية الوعي الوطني المصري")
                break
            
            else:
                print("❌ اختيار غير صحيح، حاول مرة أخرى")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في النظام: {str(e)}")
    finally:
        print("\n🔒 إغلاق النظام...")

if __name__ == "__main__":
    main()

