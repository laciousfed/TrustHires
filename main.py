import sqlite3
import os
import json
from datetime import datetime
from kivy.animation import Animation
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Line
from kivymd.uix.filemanager import MDFileManager
import re
from functools import partial
from kivymd.theming import ThemableBehavior
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDButton, MDIconButton,MDButtonText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingAvatar, MDListItemTertiaryText, MDListItemLeadingIcon, MDListItemTrailingIcon
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.filemanager import MDFileManager


from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.core.window import Window
from kivy.utils import platform

# Import your screens (uncomment as needed)
from python.payment_screen import PaymentScreen
from python.welcome import WelcomeScreen
from python.login import LoginScreen
from python.setting import SettingsScreen
from python.search import SearchScreen
from python.result import ResultScreen
from python.register import RegisterScreen
from python.show import ShowScreen
from python.profile import ProfileScreen
from python.home import HomeScreen
from python.onboard import OnboardingScreen
from python.worker_profile import WorkerProfile
from python.listing import ListingScreen
from python.verify import VerificationScreen  # Your updated verification screen
from python.edit_profile import EditScreen
from python.category_card import CategoryCard
# from python.new import NewScreen
# from python.edit_profile import EditScreen
from python.privacy import PrivacyScreen
from kivy.logger import Logger
from kivy.utils import platform

from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, ColorProperty, ListProperty

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg"}
Window.size = (300, 600)

def show_toast(message, duration=3):
    """Simple cross-platform toast function"""
    snackbar = MDSnackbar(
        MDSnackbarText(text=message),
        duration=duration,
        padding=20,
        size_hint_x=0.9,
        y=dp(24),
        pos_hint={"center_x": 0.5, "y": 0.1}
    )
    snackbar.open()

import sqlite3

class DatabaseManager:
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use absolute path to ensure consistency
        self.database_path = os.path.abspath("trusthire.db")
        self.uploaded_documents = []
        self.dialog = None
        self.name = "verify"
        print(f"Database path: {self.database_path}")
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create necessary tables."""
        try:
            print(f"Initializing database at: {self.database_path}")
            
            # Remove existing database file to start fresh (for debugging)
            # if os.path.exists(self.database_path):
            #     os.remove(self.database_path)
            #     print("Removed existing database file")
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Enable foreign key constraints and WAL mode
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
        
        
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    user_type TEXT NOT NULL,  -- 'employer' or 'worker'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS privacy_terms_agreements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    terms_version TEXT NOT NULL DEFAULT '1.0',
                    privacy_version TEXT NOT NULL DEFAULT '1.0',
                    terms_accepted BOOLEAN NOT NULL DEFAULT 0,
                    privacy_accepted BOOLEAN NOT NULL DEFAULT 0,
                    terms_accepted_at TIMESTAMP NULL,
                    privacy_accepted_at TIMESTAMP NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, terms_version, privacy_version)
                )
            ''')
            
            # Worker profiles table - Updated to match WorkerProfile screen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS worker_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    full_name TEXT,
                    state TEXT,
                    city TEXT,
                    service_type TEXT,
                    phone_number TEXT,  -- Changed from INTEGER to TEXT to handle formatting
                    verified BOOLEAN DEFAULT 1,
                    employment_type TEXT,
                    profile_picture TEXT,
                    rating REAL DEFAULT 0.0,  -- Added for worker rating
                    total_reviews INTEGER DEFAULT 0,  -- Added for review count
                    status TEXT DEFAULT 'active',  -- Added for worker status
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    full_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    verification_status TEXT DEFAULT 'pending',
                    verification_fee_paid BOOLEAN DEFAULT FALSE,
                    payment_reference TEXT,
                    documents_uploaded BOOLEAN DEFAULT FALSE,
                    document_paths TEXT,
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_date TIMESTAMP NULL,
                    background_check_status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verification_id INTEGER NOT NULL,
                    document_type TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (verification_id) REFERENCES verifications (id)
                )
            ''')
            
            # Create payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verification_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL DEFAULT 10000.00,
                    currency TEXT DEFAULT 'NGN',
                    payment_method TEXT,
                    payment_reference TEXT UNIQUE,
                    payment_status TEXT DEFAULT 'pending',
                    payment_date TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (verification_id) REFERENCES verifications (id)
                )
            ''')
            
            # Job postings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_postings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employer_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    job_type TEXT,
                    salary_range TEXT,
                    location TEXT,
                    requirements TEXT,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employer_id) REFERENCES users (id)
                )
            ''')
            
            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    worker_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES job_postings (id),
                    FOREIGN KEY (worker_id) REFERENCES users (id)
                )
            ''')
            
            # Testimonials table
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS testimonials (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                testimonial_text TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users (id)
                            )
                        ''')

            # Other tables that were in migration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accepted_workers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employer_id INTEGER,
                    worker_id INTEGER,
                    worker_name TEXT,
                    service_type TEXT,
                    phone_number TEXT,
                    location TEXT,
                    profile_picture TEXT,
                    status TEXT DEFAULT 'active',
                    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employer_id) REFERENCES users (id),
                    FOREIGN KEY (worker_id) REFERENCES users (id),
                    UNIQUE(employer_id, worker_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employer_id INTEGER,
                    worker_id INTEGER,
                    accepted_worker_id INTEGER,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employer_id) REFERENCES users (id),
                    FOREIGN KEY (worker_id) REFERENCES users (id),
                    FOREIGN KEY (accepted_worker_id) REFERENCES accepted_workers (id),
                    UNIQUE(employer_id, worker_id)
                )
            ''')

            

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employer_id INTEGER,
                    worker_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employer_id) REFERENCES users (id),
                    FOREIGN KEY (worker_id) REFERENCES users (id),
                    UNIQUE(employer_id, worker_id)
                )
            ''')
            
            # Force commit
            conn.commit()
            
            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            print(f"Created tables: {table_names}")
            
            # Test insert to verify table works
            cursor.execute("SELECT COUNT(*) FROM verifications")
            count = cursor.fetchone()[0]
            print(f"Verifications table has {count} records")
            
            conn.close()
            print("Database initialized successfully")
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise e
    
    def get_safe_database_connection(self):
        """Get a safe database connection with table verification."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempting to connect to database (attempt {attempt + 1})")
                print(f"Database file exists: {os.path.exists(self.database_path)}")
                
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                
                # Test the connection by checking if tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='verifications';
                """)
                result = cursor.fetchone()
                
                if result:
                    print("Verifications table found in database")
                    return conn
                else:
                    print("Verifications table NOT found, recreating database")
                    conn.close()
                    if attempt < max_retries - 1:
                        self.init_database()
                    else:
                        raise sqlite3.OperationalError("Could not create verifications table")
                        
            except sqlite3.Error as e:
                print(f"Database connection error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise e
                else:
                    # Try to recreate database
                    try:
                        self.init_database()
                    except Exception as init_error:
                        print(f"Failed to recreate database: {init_error}")
        
        raise sqlite3.OperationalError("Could not establish database connection")
    
    def get_user_by_id(self, id):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    # Add these methods to your DatabaseManager class

    def get_privacy_terms_agreement(self, user_id, terms_version, privacy_version):
        """Get privacy and terms agreement for a user"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT terms_accepted, privacy_accepted, terms_accepted_at, privacy_accepted_at,
                    ip_address, user_agent, created_at, updated_at
                FROM privacy_terms_agreements 
                WHERE user_id = ? AND terms_version = ? AND privacy_version = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id, terms_version, privacy_version))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'terms_accepted': result[0],
                    'privacy_accepted': result[1],
                    'terms_accepted_at': result[2],
                    'privacy_accepted_at': result[3],
                    'ip_address': result[4],
                    'user_agent': result[5],
                    'created_at': result[6],
                    'updated_at': result[7]
                }
            return None
            
        except Exception as e:
            print(f"Error getting privacy terms agreement: {e}")
            return None

    def update_terms_acceptance(self, user_id, terms_accepted, terms_version, privacy_version):
        """Update terms acceptance for a user"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute('''
                SELECT id FROM privacy_terms_agreements 
                WHERE user_id = ? AND terms_version = ? AND privacy_version = ?
            ''', (user_id, terms_version, privacy_version))
            
            existing = cursor.fetchone()
            current_time = datetime.now().isoformat()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE privacy_terms_agreements 
                    SET terms_accepted = ?, terms_accepted_at = ?, updated_at = ?
                    WHERE id = ?
                ''', (terms_accepted, current_time if terms_accepted else None, current_time, existing[0]))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO privacy_terms_agreements 
                    (user_id, terms_version, privacy_version, terms_accepted, terms_accepted_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, terms_version, privacy_version, terms_accepted, 
                    current_time if terms_accepted else None))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating terms acceptance: {e}")
            return False

    

    def update_privacy_acceptance(self, user_id, privacy_accepted, terms_version, privacy_version):
        """Update privacy acceptance for a user"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute('''
                SELECT id FROM privacy_terms_agreements 
                WHERE user_id = ? AND terms_version = ? AND privacy_version = ?
            ''', (user_id, terms_version, privacy_version))
            
            existing = cursor.fetchone()
            current_time = datetime.now().isoformat()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE privacy_terms_agreements 
                    SET privacy_accepted = ?, privacy_accepted_at = ?, updated_at = ?
                    WHERE id = ?
                ''', (privacy_accepted, current_time if privacy_accepted else None, current_time, existing[0]))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO privacy_terms_agreements 
                    (user_id, terms_version, privacy_version, privacy_accepted, privacy_accepted_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, terms_version, privacy_version, privacy_accepted, 
                    current_time if privacy_accepted else None))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating privacy acceptance: {e}")
            return False

    def save_privacy_terms_agreement(self, user_id, terms_accepted, privacy_accepted, 
                                    ip_address=None, user_agent=None, terms_version="1.0", privacy_version="1.0"):
        """Save complete privacy and terms agreement"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            
            # Check if record exists
            cursor.execute('''
                SELECT id FROM privacy_terms_agreements 
                WHERE user_id = ? AND terms_version = ? AND privacy_version = ?
            ''', (user_id, terms_version, privacy_version))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE privacy_terms_agreements 
                    SET terms_accepted = ?, privacy_accepted = ?, 
                        terms_accepted_at = ?, privacy_accepted_at = ?,
                        ip_address = ?, user_agent = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    terms_accepted, privacy_accepted,
                    current_time if terms_accepted else None,
                    current_time if privacy_accepted else None,
                    ip_address, user_agent, current_time, existing[0]
                ))
                agreement_id = existing[0]
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO privacy_terms_agreements 
                    (user_id, terms_version, privacy_version, terms_accepted, privacy_accepted,
                    terms_accepted_at, privacy_accepted_at, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, terms_version, privacy_version,
                    terms_accepted, privacy_accepted,
                    current_time if terms_accepted else None,
                    current_time if privacy_accepted else None,
                    ip_address, user_agent
                ))
                agreement_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return agreement_id
            
        except Exception as e:
            print(f"Error saving privacy terms agreement: {e}")
            return None

    def user_has_accepted_current_terms(self, user_id, terms_version, privacy_version):
        """Check if user has accepted current terms and privacy policy"""
        try:
            agreement = self.get_privacy_terms_agreement(user_id, terms_version, privacy_version)
            if agreement:
                return bool(agreement['terms_accepted']) and bool(agreement['privacy_accepted'])
            return False
            
        except Exception as e:
            print(f"Error checking terms acceptance: {e}")
            return False
    
    # ============= VERIFICATION METHODS - INSERT ONLY =============

    def save_verification_data(self, user_id, full_name, phone_number, uploaded_documents=None):
        """Save verification data to database - Updated to accept parameters instead of accessing UI directly."""
        
        print(f"Attempting to save verification data for user {user_id}")
        print(f"Full name: {full_name}, Phone: {phone_number}")
        
        conn = None
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Double-check table exists
            cursor.execute("SELECT sql FROM sqlite_master WHERE name='verifications'")
            table_schema = cursor.fetchone()
            if table_schema:
                print("Table schema verified")
            else:
                raise sqlite3.OperationalError("Table schema not found")
            
            # Check if verification already exists for this user
            cursor.execute('SELECT id FROM verifications WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                verification_id = existing[0]
                cursor.execute('''
                    UPDATE verifications 
                    SET full_name = ?, phone_number = ?, documents_uploaded = ?, updated_at = ?
                    WHERE id = ?
                ''', (full_name, phone_number, len(uploaded_documents or []) > 0, datetime.now(), verification_id))
                print(f"Updated verification record {verification_id}")
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO verifications 
                    (user_id, full_name, phone_number, documents_uploaded, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, full_name, phone_number, len(uploaded_documents or []) > 0, datetime.now(), datetime.now()))
                
                verification_id = cursor.lastrowid
                print(f"Created new verification record {verification_id}")
            
            # Save uploaded documents if provided
            if uploaded_documents:
                self.save_uploaded_documents(cursor, verification_id, uploaded_documents)
            
            conn.commit()
            conn.close()
            
            print("Verification data saved successfully")
            return verification_id
            
        except sqlite3.Error as e:
            print(f"SQLite error saving verification data: {e}")
            print(f"Error type: {type(e).__name__}")
            if conn:
                try:
                    conn.close()
                except:
                    pass
            return None
        except Exception as e:
            print(f"General error saving verification data: {e}")
            if conn:
                try:
                    conn.close()
                except:
                    pass
            return None

    def save_uploaded_documents(self, cursor, verification_id, uploaded_documents):
        """Save uploaded document information to the database."""
        try:
            for doc_path in uploaded_documents:
                # Extract filename from path
                filename = os.path.basename(doc_path) if doc_path else "unknown"
                
                cursor.execute('''
                    INSERT INTO verification_documents 
                    (verification_id, document_type, original_filename, stored_filename, file_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (verification_id, "identity", filename, filename, doc_path))
                
            print(f"Saved {len(uploaded_documents)} document records")
            
        except Exception as e:
            print(f"Error saving document records: {e}")
            # Don't raise the error, just log it since main verification was successful
    
    def debug_database_state(self):
        """Debug method to check database state."""
        print(f"\n=== DATABASE DEBUG INFO ===")
        print(f"Database path: {self.database_path}")
        print(f"Database file exists: {os.path.exists(self.database_path)}")
        print(f"Database file size: {os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 'N/A'} bytes")
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            # Check verifications table specifically
            cursor.execute("SELECT sql FROM sqlite_master WHERE name='verifications';")
            schema = cursor.fetchone()
            if schema:
                print("Verifications table schema exists")
            else:
                print("Verifications table schema NOT found")
            
            # Try to query the table
            cursor.execute("SELECT COUNT(*) FROM verifications")
            count = cursor.fetchone()[0]
            print(f"Records in verifications table: {count}")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database debug error: {e}")
        
        print("=== END DEBUG INFO ===\n")

    def get_user_basic_info(self, user_id):
        """Get basic user information from users table"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, email, user_type
                FROM users
                WHERE id = ?
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            
            if user_info:
                conn.close()
                return {
                    'username': user_info[0],
                    'email': user_info[1],
                    'user_type': user_info[2]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting user basic info: {e}")
            return None

    def get_user_profile(self, user_id):
        """Get user profile information including full_name and profile_picture"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # First try to get from worker_profiles table (most complete profile data)
            cursor.execute('''
                SELECT wp.full_name, wp.profile_picture, wp.phone_number, wp.city, wp.state, 
                    wp.service_type, wp.verified, u.email, u.username, u.user_type
                FROM worker_profiles wp
                JOIN users u ON wp.user_id = u.id
                WHERE wp.user_id = ?
            ''', (user_id,))
            
            worker_profile = cursor.fetchone()
            
            if worker_profile:
                conn.close()
                return {
                    'full_name': worker_profile[0],
                    'profile_picture': worker_profile[1],
                    'phone_number': worker_profile[2],
                    'city': worker_profile[3],
                    'state': worker_profile[4],
                    'service_type': worker_profile[5],
                    'verified': worker_profile[6],
                    'email': worker_profile[7],
                    'username': worker_profile[8],
                    'user_type': worker_profile[9]
                }
            
            # If not found in worker_profiles, try verifications table
            cursor.execute('''
                SELECT v.full_name, u.email, u.username, u.user_type
                FROM verifications v
                JOIN users u ON v.user_id = u.id
                WHERE v.user_id = ?
            ''', (user_id,))
            
            verification_profile = cursor.fetchone()
            
            if verification_profile:
                conn.close()
                return {
                    'full_name': verification_profile[0],
                    'profile_picture': None,  # No profile picture in verifications table
                    'email': verification_profile[1],
                    'username': verification_profile[2],
                    'user_type': verification_profile[3]
                }
            
            # If not found in either table, get basic user info
            cursor.execute('''
                SELECT username, email, user_type
                FROM users
                WHERE id = ?
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            
            if user_info:
                conn.close()
                return {
                    'full_name': user_info[0],  # Use username as fallback
                    'profile_picture': None,
                    'email': user_info[1],
                    'username': user_info[0],
                    'user_type': user_info[2]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def initiate_payment(self, verification_id):
        """Initiate payment process."""
        self.close_dialog()
        
        try:
            # Create payment record
            payment_reference = self.generate_payment_reference()
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO verification_payments 
                (verification_id, amount, payment_reference)
                VALUES (?, ?, ?)
            ''', (verification_id, 10000.00, payment_reference))
            
            conn.commit()
            conn.close()
            
            # Here you would integrate with actual payment gateway
            # For now, we'll simulate the payment process
            show_toast("Redirecting to payment gateway...")
            
            # You can navigate to payment screen or open payment gateway
            # self.manager.current = "payment_screen"
            
        except sqlite3.Error as e:
            print(f"Error creating payment record: {e}")
            ("Error initiating payment. Please try again.")
    
    def generate_payment_reference(self):
        """Generate unique payment reference."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_id = self.get_current_user_id()
        return f"VER_{user_id}_{timestamp}"
    
    def insert_verification_record(self, data):
        """Insert verification record - same pattern as insert_worker_profile"""
        conn = None
        try:
            print(f"DEBUG: Attempting to insert verification data: {data}")
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check if data has required fields
            required_fields = ['user_id', 'full_name', 'phone_number']
            for field in required_fields:
                if not data.get(field):
                    print(f"ERROR: Missing required field: {field}")
                    return None
            
            # Prepare the values
            user_id = data.get('user_id')
            full_name = data.get('full_name')
            phone_number = data.get('phone_number')
            document_paths = data.get('document_paths')  # Default to empty string if None
            
            
            print(f"DEBUG: Inserting values: user_id={user_id}, full_name={full_name}, phone_number={phone_number}, document_paths={document_paths}")
            
            cursor.execute('''
                INSERT INTO verifications (user_id, full_name, phone_number, document_paths)
                VALUES (?, ?, ?, ?)
            ''', (user_id, full_name, phone_number, document_paths))
            
            # Check if any rows were affected
            if cursor.rowcount == 0:
                print("WARNING: No rows were inserted")
                return None
                
            conn.commit()
            verification_id = cursor.lastrowid
            print(f"SUCCESS: Inserted verification record with ID: {verification_id}")
            
            # Verify the insert by querying back
            cursor.execute('SELECT * FROM verifications WHERE id = ?', (verification_id,))
            result = cursor.fetchone()
            print(f"DEBUG: Verification - inserted record: {result}")
            
            return verification_id
            
        except Exception as e:
            print(f"Error inserting verification record: {str(e)}")
            import traceback
            traceback.print_exc()
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def debug_verifications_table(self):
        """Debug method to check the actual table structure"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(verifications)")
            columns = cursor.fetchall()
            print("DEBUG: Verifications table structure:")
            for col in columns:
                print(f"  - {col}")
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verifications'")
            exists = cursor.fetchone()
            print(f"DEBUG: Table exists: {exists is not None}")
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM verifications")
            count = cursor.fetchone()[0]
            print(f"DEBUG: Total records in verifications table: {count}")
            
            # Show all records
            cursor.execute("SELECT * FROM verifications")
            records = cursor.fetchall()
            print(f"DEBUG: All records:")
            for record in records:
                print(f"  - {record}")
                
        except Exception as e:
            print(f"Error debugging table: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()

    def recreate_verifications_table(self):
        """Recreate the verifications table with the correct schema"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Drop the existing table
            cursor.execute("DROP TABLE IF EXISTS verifications")
            print("DEBUG: Dropped existing verifications table")
            
            # Recreate with correct schema
            cursor.execute('''
                CREATE TABLE verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    full_name TEXT,
                    phone_number TEXT,
                    document_paths TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            print("DEBUG: Recreated verifications table with correct schema")
            
            conn.commit()
            
            # Verify the new structure
            cursor.execute("PRAGMA table_info(verifications)")
            columns = cursor.fetchall()
            print("DEBUG: New table structure:")
            for col in columns:
                print(f"  - {col}")
                
        except Exception as e:
            print(f"Error recreating table: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def get_verification_record(self, user_id):
        """Get verification record"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM verifications WHERE user_id = ?', (user_id,))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
            
        except Exception as e:
            print(f"Error getting verification record: {str(e)}")
            return None
        finally:
            conn.close()  # Always close the connection
        
        # ============= USER MANAGEMENT METHODS =============
    def create_user(self, username, email, password, user_type):
        """Create a new user"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, user_type)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password, user_type))
            
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, user_type FROM users 
            WHERE email = ? AND password = ?
        ''', (email, password))
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def authenticate_user(self, email, password):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def get_user_by_id(self, id):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def email_exists(self, email):
        """Check if email already exists"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def username_exists(self, username):
        """Check if username already exists"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    # ============= WORKER PROFILE METHODS =============
    def insert_worker_profile(self, data: dict):
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute(
            """INSERT INTO worker_profiles
            (user_id, full_name, state, city, service_type, phone_number, employment_type, profile_picture)
            VALUES (:user_id, :full_name, :state, :city, :service_type, :phone_number, :employment_type, :profile_picture)""",
            data,
        )
        conn.commit()
        conn.close()
    
    def get_worker_profile(self, user_id):
        """Get worker profile by user ID"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM worker_profiles WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        return profile
    
    def get_next_user_id(self):
        """Get the next sequential user_id"""
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        
        # Get the maximum user_id from the worker_profiles table
        c.execute("SELECT MAX(user_id) FROM worker_profiles")
        result = c.fetchone()
        
        conn.close()
        
        # If no records exist, start with 1, otherwise increment the max
        if result[0] is None:
            return 1
        else:
            return result[0] + 1
    
    def get_user_profile(self, id):
        """Get user profile by user ID with enhanced debugging"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Debug: Check if user_id exists in worker_profiles
            cursor.execute("SELECT COUNT(*) FROM worker_profiles WHERE id=?", (id,))
            count = cursor.fetchone()[0]
            print(f"Found {count} worker profiles for user_id: {id}")
            
            if count == 0:
                print(f"No worker profile found for user_id: {id}")
                conn.close()
                return None
            
            # Get the profile data
            cursor.execute("SELECT full_name, profile_picture FROM worker_profiles WHERE id=?", (id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"Retrieved profile: full_name='{result[0]}', profile_picture='{result[1]}'")
                return {
                    "full_name": result[0],
                    "profile_picture": result[1]
                }
            else:
                print(f"No result returned for user_id: {id}")
                return None
                
        except Exception as e:
            print(f"Error in get_user_profile: {e}")
            return None

    def get_user_basic_info(self, id):
        """Get basic user info from users table as fallback"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username, email, user_type FROM users WHERE id=?", (id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"Retrieved basic user info: username='{result[0]}', email='{result[1]}', user_type='{result[2]}'")
                return {
                    'username': result[0],
                    'email': result[1],
                    'user_type': result[2]
                }
            else:
                print(f"No user found with id: {id}")
                return None
                
        except Exception as e:
            print(f"Error in get_user_basic_info: {e}")
            
            
            if result:
                return {
                    "full_name": result[0],
                    "profile_picture": result[1]
                }
            return None
        
    def get_feature_worker(self, verified=None, limit=10):
        """Get featured workers from worker_profiles table"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Base query to get worker profiles with user information
            query = '''
                SELECT wp.id, wp.user_id, wp.full_name, wp.service_type, wp.city, wp.state,
                    wp.phone_number, wp.profile_picture, wp.rating, wp.total_reviews,
                    wp.verified, wp.employment_type, wp.status, u.email
                FROM worker_profiles wp
                JOIN users u ON wp.user_id = u.id
                WHERE wp.status = 'active'
            '''
            
            params = []
            
            # Add verified filter if specified
            if verified is not None:
                query += ' AND wp.verified = ?'
                params.append(verified)
            
            # Order by rating and total reviews to get "featured" workers
            query += ' ORDER BY wp.rating DESC, wp.total_reviews DESC, wp.created_at DESC'
            
            # Add limit
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            workers = []
            for row in results:
                worker = {
                    'id': row[0],
                    'user_id': row[1],
                    'full_name': row[2],
                    'service_type': row[3],
                    'city': row[4],
                    'state': row[5],
                    'phone_number': row[6],
                    'profile_picture': row[7],
                    'rating': row[8] or 0.0,
                    'total_reviews': row[9] or 0,
                    'verified': bool(row[10]),
                    'employment_type': row[11],
                    'status': row[12],
                    'email': row[13]
                }
                workers.append(worker)
            
            conn.close()
            print(f"Retrieved {len(workers)} featured workers")
            return workers
            
        except Exception as e:
            print(f"Error getting featured workers: {e}")
            return []

    def get_worker_profiles_by_service(self, service_type, verified_only=False):
        """Get worker profiles by service type"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT wp.*, u.email, u.username
                FROM worker_profiles wp
                JOIN users u ON wp.user_id = u.id
                WHERE wp.service_type = ? AND wp.status = 'active'
            '''
            
            params = [service_type]
            
            if verified_only:
                query += ' AND wp.verified = 1'
            
            query += ' ORDER BY wp.rating DESC, wp.total_reviews DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to dictionaries
            workers = []
            columns = [description[0] for description in cursor.description]
            
            for row in results:
                worker = dict(zip(columns, row))
                workers.append(worker)
            
            conn.close()
            return workers
            
        except Exception as e:
            print(f"Error getting worker profiles by service: {e}")
            return []

    def update_worker_verification_status(self, user_id, verified=True):
        """Update worker verification status"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Update worker profile verification status
            cursor.execute('''
                UPDATE worker_profiles 
                SET verified = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (verified, user_id))
            
            # Also update the verification record
            cursor.execute('''
                UPDATE verifications 
                SET verification_status = ?, verification_date = CURRENT_TIMESTAMP,
                    background_check_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', ('approved' if verified else 'rejected', 'completed' if verified else 'failed', user_id))
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            print(f"Updated verification status for user {user_id}: {verified}")
            return rows_affected > 0
            
        except Exception as e:
            print(f"Error updating worker verification status: {e}")
            return False

    def get_verification_status(self, user_id):
        """Get verification status for a user"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT v.*, wp.verified as worker_verified
                FROM verifications v
                LEFT JOIN worker_profiles wp ON v.user_id = wp.user_id
                WHERE v.user_id = ?
                ORDER BY v.created_at DESC
                LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
            
        except Exception as e:
            print(f"Error getting verification status: {e}")
            return None

    def get_pending_verifications(self, limit=None):
        """Get pending verification requests for admin review"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT v.*, u.username, u.email, wp.service_type
                FROM verifications v
                JOIN users u ON v.user_id = u.id
                LEFT JOIN worker_profiles wp ON v.user_id = wp.user_id
                WHERE v.verification_status = 'pending'
                ORDER BY v.submission_date ASC
            '''
            
            params = []
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to dictionaries
            verifications = []
            columns = [description[0] for description in cursor.description]
            
            for row in results:
                verification = dict(zip(columns, row))
                verifications.append(verification)
            
            conn.close()
            return verifications
            
        except Exception as e:
            print(f"Error getting pending verifications: {e}")
            return []

    def approve_verification(self, verification_id, admin_notes=None):
        """Approve a verification request"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Get the user_id from verification
            cursor.execute('SELECT user_id FROM verifications WHERE id = ?', (verification_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"Verification {verification_id} not found")
                return False
            
            user_id = result[0]
            
            # Update verification record
            cursor.execute('''
                UPDATE verifications 
                SET verification_status = 'approved', 
                    verification_date = CURRENT_TIMESTAMP,
                    background_check_status = 'completed',
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (admin_notes, verification_id))
            
            # Update worker profile verification status
            cursor.execute('''
                UPDATE worker_profiles 
                SET verified = 1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"Approved verification {verification_id} for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error approving verification: {e}")
            return False

    def reject_verification(self, verification_id, admin_notes=None):
        """Reject a verification request"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Get the user_id from verification
            cursor.execute('SELECT user_id FROM verifications WHERE id = ?', (verification_id,))
            result = cursor.fetchone()
            
            if not result:
                print(f"Verification {verification_id} not found")
                return False
            
            user_id = result[0]
            
            # Update verification record
            cursor.execute('''
                UPDATE verifications 
                SET verification_status = 'rejected', 
                    verification_date = CURRENT_TIMESTAMP,
                    background_check_status = 'failed',
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (admin_notes, verification_id))
            
            # Ensure worker profile verification status is false
            cursor.execute('''
                UPDATE worker_profiles 
                SET verified = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"Rejected verification {verification_id} for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error rejecting verification: {e}")
            return False

    def get_verification_documents(self, verification_id):
        """Get documents for a verification"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM verification_documents 
                WHERE verification_id = ?
                ORDER BY upload_date DESC
            ''', (verification_id,))
            
            results = cursor.fetchall()
            
            # Convert to dictionaries
            documents = []
            columns = [description[0] for description in cursor.description]
            
            for row in results:
                document = dict(zip(columns, row))
                documents.append(document)
            
            conn.close()
            return documents
            
        except Exception as e:
            print(f"Error getting verification documents: {e}")
            return []

    def search_workers(self, service_type=None, city=None, state=None, verified_only=False):
        """Search workers with filters"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT wp.*, u.email, u.username
                FROM worker_profiles wp
                JOIN users u ON wp.user_id = u.id
                WHERE wp.status = 'active'
            '''
            
            params = []
            
            if service_type:
                query += ' AND wp.service_type = ?'
                params.append(service_type)
            
            if city:
                query += ' AND wp.city = ?'
                params.append(city)
            
            if state:
                query += ' AND wp.state = ?'
                params.append(state)
            
            if verified_only:
                query += ' AND wp.verified = 1'
            
            query += ' ORDER BY wp.rating DESC, wp.total_reviews DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to dictionaries
            workers = []
            columns = [description[0] for description in cursor.description]
            
            for row in results:
                worker = dict(zip(columns, row))
                workers.append(worker)
            
            conn.close()
            return workers
            
        except Exception as e:
            print(f"Error searching workers: {e}")
            return []

    
    
    def update_worker_profile(self, user_id, **kwargs):
        """Update worker profile"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if value is not None:  # Only update non-None values
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(user_id)
            query = f'''
                UPDATE worker_profiles 
                SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            affected_rows = cursor.rowcount
            return affected_rows > 0
        except Exception as e:
            print(f"Error updating worker profile: {str(e)}")
            return False
        finally:
            conn.close()
    
    def search_workers(self, service_type=None, state=None, city=None, verified_only=False):
        """Search workers with filters"""
        conn = sqlite3.connect(self.database_path )
        cursor = conn.cursor()
        
        query = '''
            SELECT wp.*, u.username, u.email 
            FROM worker_profiles wp
            JOIN users u ON wp.user_id = u.id
            WHERE wp.status = 'active'
        '''
        params = []
        
        if service_type:
            query += ' AND wp.service_type = ?'
            params.append(service_type)
        
        if state:
            query += ' AND wp.state = ?'
            params.append(state)
        
        if city:
            query += ' AND wp.city = ?'
            params.append(city)
        
        if verified_only:
            query += ' AND wp.verified = 1'
        
        query += ' ORDER BY wp.rating DESC, wp.created_at DESC'
        
        cursor.execute(query, params)
        workers = cursor.fetchall()
        conn.close()
        return workers
    
    def get_all_workers(self):
        """Get all active workers"""
        return self.search_workers()
    
    def mark_worker_verified(self, user_id):
        """Mark worker as verified"""
        return self.update_worker_profile(user_id, verified=True)
    
    # ============= TESTIMONIALS METHODS =============

    def insert_testimonial(self, user_id, testimonial_text):
        """Insert a new testimonial into the database"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Insert the testimonial (only user_id and testimonial_text)
            cursor.execute('''
                INSERT INTO testimonials (user_id, testimonial_text)
                VALUES (?, ?)
            ''', (user_id, testimonial_text))
            
            testimonial_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Testimonial inserted successfully with ID: {testimonial_id}")
            return testimonial_id
            
        except Exception as e:
            print(f"Error inserting testimonial: {e}")
            return None

    def get_testimonials(self, user_id=None, limit=None):
        """Get testimonials from the database with joined worker profile data"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            # Join testimonials with worker_profiles to get full_name and profile_picture
            query = '''
                SELECT t.id, t.user_id, t.testimonial_text, t.created_at,
                    wp.full_name, wp.profile_picture
                FROM testimonials t
                LEFT JOIN worker_profiles wp ON t.user_id = wp.user_id
                WHERE 1=1
            '''
            params = []
            
            if user_id:
                query += ' AND t.id = ?'
                params.append(user_id)
            
            query += ' ORDER BY t.created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            testimonials = []
            for row in results:
                testimonials.append({
                    'id': row[0],
                    'user_id': row[1],
                    'testimonial_text': row[2],
                    'created_at': row[3],
                    'full_name': row[4],
                    'profile_picture': row[5]
                })
            
            return testimonials
            
        except Exception as e:
            print(f"Error getting testimonials: {e}")
            return []

    def update_testimonial(self, testimonial_id, testimonial_text):
        """Update an existing testimonial"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE testimonials 
                SET testimonial_text = ?
                WHERE id = ?
            ''', (testimonial_text, testimonial_id))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error updating testimonial: {e}")
            return False

    def delete_testimonial(self, testimonial_id):
        """Delete a testimonial from the database"""
        try:
            conn = self.get_safe_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM testimonials WHERE id = ?', (testimonial_id,))
            conn.commit()
            
            success = cursor.rowcount > 0
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error deleting testimonial: {e}")
            return False
    
    
    def add_testimonial(self, user_id, customer_name, testimonial_text, rating=5, service_type=None, customer_image=None):
        """Add a new testimonial"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO testimonials (user_id, customer_name, customer_image, testimonial_text, rating, service_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, customer_name, customer_image, testimonial_text, rating, service_type))
        
        conn.commit()
        testimonial_id = cursor.lastrowid
        conn.close()
        return testimonial_id
    

    def accept_worker(self, employer_id, worker_data):
        """Accept a worker and add to employer's list"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO accepted_workers 
                (employer_id, worker_id, worker_name, service_type, phone_number, location, profile_picture)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                employer_id,
                worker_data['worker_id'],
                worker_data['worker_name'],
                worker_data['service_type'],
                worker_data['phone_number'],
                worker_data['location'],
                worker_data['profile_picture']
            ))
            
            conn.commit()
            accepted_id = cursor.lastrowid
            conn.close()
            return accepted_id
            
        except sqlite3.IntegrityError:
            # Worker already accepted by this employer
            conn.close()
            return False
        except Exception as e:
            conn.close()
            print(f"Error accepting worker: {e}")
            return False
        
    def get_accepted_workers(self, employer_id):
        """Get all workers accepted by an employer"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT aw.*, r.rating, r.review_text
            FROM accepted_workers aw
            LEFT JOIN reviews r ON aw.id = r.accepted_worker_id AND r.employer_id = ?
            WHERE aw.employer_id = ?
            ORDER BY aw.accepted_at DESC
        ''', (employer_id, employer_id))
        
        workers = cursor.fetchall()
        conn.close()
        return workers
    
    def add_review(self, employer_id, worker_id, accepted_worker_id, rating, review_text=""):
        """Add or update a review for a worker"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            # Check if review already exists
            cursor.execute('''
                SELECT id FROM reviews 
                WHERE employer_id = ? AND worker_id = ?
            ''', (employer_id, worker_id))
            
            existing_review = cursor.fetchone()
            
            if existing_review:
                # Update existing review
                cursor.execute('''
                    UPDATE reviews 
                    SET rating = ?, review_text = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE employer_id = ? AND worker_id = ?
                ''', (rating, review_text, employer_id, worker_id))
            else:
                # Insert new review
                cursor.execute('''
                    INSERT INTO reviews (employer_id, worker_id, accepted_worker_id, rating, review_text)
                    VALUES (?, ?, ?, ?, ?)
                ''', (employer_id, worker_id, accepted_worker_id, rating, review_text))
            
            # Update worker's average rating
            cursor.execute('''
                SELECT AVG(rating), COUNT(rating) FROM reviews WHERE worker_id = ?
            ''', (worker_id,))
            
            avg_rating, review_count = cursor.fetchone()
            
            cursor.execute('''
                UPDATE worker_profiles 
                SET rating = ?, total_reviews = ?
                WHERE user_id = ?
            ''', (round(avg_rating, 1) if avg_rating else 0, review_count, worker_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.close()
            print(f"Error adding review: {e}")
            return False
    
    def get_worker_reviews(self, worker_id, limit=10):
        """Get reviews for a specific worker"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.rating, r.review_text, r.created_at, u.username
            FROM reviews r
            JOIN users u ON r.employer_id = u.id
            WHERE r.worker_id = ?
            ORDER BY r.created_at DESC
            LIMIT ?
        ''', (worker_id, limit))
        
        reviews = cursor.fetchall()
        conn.close()
        return reviews
    
    def add_to_favorites(self, employer_id, worker_id):
        """Add worker to employer's favorites"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO favorites (employer_id, worker_id)
                VALUES (?, ?)
            ''', (employer_id, worker_id))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Already in favorites
            conn.close()
            return False
        except Exception as e:
            conn.close()
            print(f"Error adding to favorites: {e}")
            return False
    
    def remove_from_favorites(self, employer_id, worker_id):
        """Remove worker from employer's favorites"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM favorites 
            WHERE employer_id = ? AND worker_id = ?
        ''', (employer_id, worker_id))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows > 0
    
    def is_favorite(self, employer_id, worker_id):
        """Check if worker is in employer's favorites"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM favorites 
            WHERE employer_id = ? AND worker_id = ?
        ''', (employer_id, worker_id))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_favorites(self, employer_id):
        """Get employer's favorite workers"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT wp.*, u.username, u.email, f.created_at as favorited_at
            FROM favorites f
            JOIN worker_profiles wp ON f.worker_id = wp.user_id
            JOIN users u ON wp.user_id = u.id
            WHERE f.employer_id = ?
            ORDER BY f.created_at DESC
        ''', (employer_id,))
        
        favorites = cursor.fetchall()
        conn.close()
        return favorites


def close_connection(self):
    """Close database connection - for app lifecycle management"""
    try:
        # Since your DatabaseManager doesn't keep persistent connections,
        # this method is mainly for logging and cleanup
        Logger.info("DatabaseManager: Database connections closed")
        
        # If you had any persistent connections, you'd close them here
        # For example:
        # if hasattr(self, 'persistent_conn') and self.persistent_conn:
        #     self.persistent_conn.close()
        #     self.persistent_conn = None
        
    except Exception as e:
        Logger.error(f"DatabaseManager: Error during cleanup: {str(e)}")

def cleanup_temp_files(self):
    """Clean up temporary files and resources"""
    try:
        # Clean up any temporary files your app might create
        if hasattr(self, 'uploaded_documents'):
            self.uploaded_documents.clear()
        
        # Clean up any temporary database files
        temp_files = [
            f"{self.database_path}-wal",
            f"{self.database_path}-shm"
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    Logger.info(f"DatabaseManager: Cleaned up {temp_file}")
                except Exception as e:
                    Logger.warning(f"DatabaseManager: Could not remove {temp_file}: {e}")
                    
    except Exception as e:
        Logger.error(f"DatabaseManager: Error during temp file cleanup: {str(e)}")

def get_database_stats(self):
    """Get database statistics for monitoring"""
    try:
        conn = self.get_safe_database_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Get table counts
        tables = ['users', 'worker_profiles', 'verifications', 'job_postings', 'applications']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except sqlite3.Error:
                stats[table] = 0
        
        # Get database size
        if os.path.exists(self.database_path):
            stats['database_size'] = os.path.getsize(self.database_path)
        
        conn.close()
        return stats
        
    except Exception as e:
        Logger.error(f"DatabaseManager: Error getting stats: {str(e)}")
        return {}


ANDROID_AVAILABLE = False
try:
    if platform == 'android':
        from android.storage import app_storage_path
        ANDROID_AVAILABLE = True
except ImportError:
    Logger.info("RecruitmentApp: Running in development environment (not Android)")
    ANDROID_AVAILABLE = False

class RecruitmentApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user_id = None
        self.current_user_type = None
        self.current_user_name = None
        self.current_user_email = None
        self.current_user_password = None
        
        # App lifecycle state management
        self.app_state = "starting"  # starting, running, paused, stopped
        self.pause_start_time = None
        self.session_start_time = None
        self.auto_logout_timer = None
        self.background_tasks = []
        
        # Session management
        self.session_data = {}
        self.user_preferences = {}
        
        # Initialize database
        self.db = None
        
        # Mobile-specific settings
        self.auto_logout_timeout = 300  # 5 minutes of inactivity
        self.session_timeout = 1800     # 30 minutes total session
        self.background_sync_interval = 60  # 1 minute
        
        # Live update system
        self.data_observers = {}  # {data_type: [callback_functions]}
        self.screen_refresh_callbacks = {}  # {screen_name: callback_function}
        self.last_data_update = {}  # {data_type: timestamp}
        self.auto_refresh_enabled = True
        self.refresh_interval = 30  # 30 seconds for auto-refresh
        
        # Data cache for efficient updates
        self.data_cache = {
            'profiles': {},
            'listings': {},
            'notifications': {},
            'search_results': {},
            'user_data': {}
        }

    def build(self):
        """Build the app interface"""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.theme_style = "Dark"

        try:
            # Initialize database
            self.db = DatabaseManager()
            Logger.info("RecruitmentApp: Database manager initialized successfully")
            
            # Test database connection
            test_user = self.db.get_user_by_id(1)
            Logger.info("RecruitmentApp: Database connection test passed")
            
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error initializing app: {str(e)}")
            raise
        
        # Load user preferences and session data
        self.load_app_state()
        
        # Create screen manager
        sm = MDScreenManager()
        
        # Add all screens
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(OnboardingScreen(name='onboard'))
        sm.add_widget(ShowScreen(name='show'))
        sm.add_widget(ResultScreen(name='results'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(SettingsScreen(name="setting"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(EditScreen(name="edit_profile"))
        sm.add_widget(WorkerProfile(name='worker_profile'))
        sm.add_widget(ListingScreen(name="my_list"))
        sm.add_widget(VerificationScreen())
        sm.add_widget(PaymentScreen())
        sm.add_widget(PrivacyScreen(name="privacy"))
        
        # Setup screen change listener for auto-refresh
        sm.bind(current=self.on_screen_change)
        
        # Start session tracking
        self.start_session()
        
        return sm

    def on_start(self):
        """Called when the app starts"""
        Logger.info("RecruitmentApp: App started")
        self.app_state = "running"
        
        # Check if returning from background and restore session if needed
        if self.should_restore_session():
            self.restore_user_session()
        
        # Start background tasks
        self.start_background_tasks()
        
        # Setup live data monitoring
        self.setup_live_data_monitoring()
        
        # Show welcome message
        Clock.schedule_once(self.show_startup_message, 1)

    def on_pause(self):
        """Called when the app is paused (goes to background)"""
        Logger.info("RecruitmentApp: App paused")
        self.app_state = "paused"
        self.pause_start_time = datetime.now()
        
        # Save current app state
        self.save_app_state()
        
        # Cancel auto-logout timer if running
        if self.auto_logout_timer:
            self.auto_logout_timer.cancel()
            self.auto_logout_timer = None
        
        # Stop background tasks to save battery
        self.stop_background_tasks()
        
        # Show pause notification
        if self.current_user_id:
            show_toast("App paused - your session is saved")
        
        # Return True to allow pausing
        return True

    def on_resume(self):
        """Called when the app resumes from background"""
        Logger.info("RecruitmentApp: App resumed")
        self.app_state = "running"
        
        # Calculate time spent in background
        if self.pause_start_time:
            pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
            Logger.info(f"RecruitmentApp: Was paused for {pause_duration} seconds")
            
            # Auto-logout if paused too long
            if pause_duration > self.auto_logout_timeout and self.current_user_id:
                self.auto_logout("Session expired due to inactivity")
                return
            
            # Session timeout check
            if self.session_start_time:
                total_session_time = (datetime.now() - self.session_start_time).total_seconds()
                if total_session_time > self.session_timeout and self.current_user_id:
                    self.auto_logout("Session expired - please log in again")
                    return
        
        # Restore session and restart background tasks
        self.load_app_state()
        self.start_background_tasks()
        
        # Refresh all data when resuming
        self.refresh_all_data()
        
        # Reset auto-logout timer
        if self.current_user_id:
            self.reset_auto_logout_timer()
            show_toast("Welcome back!")
        
        self.pause_start_time = None

    def on_stop(self):
        """Called when the app is closed"""
        Logger.info("RecruitmentApp: App stopping")
        self.app_state = "stopped"
        
        # Save all app state
        self.save_app_state()
        
        # Clean up resources
        self.cleanup_resources()
        
        # Cancel all timers
        if self.auto_logout_timer:
            self.auto_logout_timer.cancel()
        
        # Stop background tasks
        self.stop_background_tasks()
        
        # Close database connection
        if self.db:
            try:
                # Check if close_connection method exists
                if hasattr(self.db, 'close_connection'):
                    self.db.close_connection()
                elif hasattr(self.db, 'close'):
                    self.db.close()
                Logger.info("RecruitmentApp: Database connection closed")
            except Exception as e:
                Logger.error(f"RecruitmentApp: Error closing database: {str(e)}")

    # Live Data Update System
    def setup_live_data_monitoring(self):
        """Setup live data monitoring system"""
        # Schedule periodic data checks
        if self.auto_refresh_enabled:
            Clock.schedule_interval(self.check_for_data_updates, self.refresh_interval)
        
        Logger.info("RecruitmentApp: Live data monitoring setup complete")

    def register_data_observer(self, data_type, callback):
        """Register a callback to be called when specific data changes"""
        if data_type not in self.data_observers:
            self.data_observers[data_type] = []
        
        if callback not in self.data_observers[data_type]:
            self.data_observers[data_type].append(callback)
            Logger.info(f"RecruitmentApp: Registered observer for {data_type}")

    def unregister_data_observer(self, data_type, callback):
        """Unregister a data observer"""
        if data_type in self.data_observers and callback in self.data_observers[data_type]:
            self.data_observers[data_type].remove(callback)
            Logger.info(f"RecruitmentApp: Unregistered observer for {data_type}")

    def register_screen_refresh_callback(self, screen_name, callback):
        """Register a callback for screen-specific refresh"""
        self.screen_refresh_callbacks[screen_name] = callback
        Logger.info(f"RecruitmentApp: Registered refresh callback for {screen_name}")

    def notify_data_changed(self, data_type, new_data=None, change_type="update"):
        """Notify observers that data has changed"""
        self.last_data_update[data_type] = datetime.now()
        
        # Update cache if new data provided
        if new_data is not None:
            self.data_cache[data_type] = new_data
        
        # Notify all observers
        if data_type in self.data_observers:
            for callback in self.data_observers[data_type]:
                try:
                    Clock.schedule_once(lambda dt: callback(data_type, new_data, change_type), 0)
                except Exception as e:
                    Logger.error(f"RecruitmentApp: Error notifying observer: {str(e)}")
        
        Logger.info(f"RecruitmentApp: Data change notification sent for {data_type}")

    def check_for_data_updates(self, dt):
        """Check for data updates periodically"""
        if self.current_user_id and self.app_state == "running":
            try:
                # Check for profile updates
                self.check_profile_updates()
                
                # Check for listing updates
                self.check_listing_updates()
                
                # Check for notification updates
                self.check_notification_updates()
                
                # Check for search result updates if on search screen
                if self.root.current == "search":
                    self.check_search_updates()
                
            except Exception as e:
                Logger.error(f"RecruitmentApp: Error checking for updates: {str(e)}")

    def check_profile_updates(self):
        """Check for profile data updates"""
        try:
            if self.current_user_id:
                # Get current profile data
                current_profile = self.db.get_user_profile(self.current_user_id)
                
                # Compare with cached data
                cached_profile = self.data_cache.get('profiles', {}).get(self.current_user_id)
                
                if current_profile != cached_profile:
                    # Update cache
                    if 'profiles' not in self.data_cache:
                        self.data_cache['profiles'] = {}
                    self.data_cache['profiles'][self.current_user_id] = current_profile
                    
                    # Notify observers
                    self.notify_data_changed('profile', current_profile)
                    
                    # Update current user data
                    if current_profile:
                        self.current_user_name = current_profile.get('name', self.current_user_name)
                        self.current_user_email = current_profile.get('email', self.current_user_email)
                    
                    Logger.info("RecruitmentApp: Profile data updated")
                    
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error checking profile updates: {str(e)}")

    # def get_user_listings(self):
    #     pass

    # def get_user_notifications(self):
    #     pass

    def check_listing_updates(self):
        """Check for job listing updates"""
        try:
            if self.current_user_id:
                # Get current listings
                current_listings = self.db.get_user_listings(self.current_user_id)
                
                # Compare with cached data
                cached_listings = self.data_cache.get('listings', {}).get(self.current_user_id)
                
                if current_listings != cached_listings:
                    # Update cache
                    if 'listings' not in self.data_cache:
                        self.data_cache['listings'] = {}
                    self.data_cache['listings'][self.current_user_id] = current_listings
                    
                    # Notify observers
                    self.notify_data_changed('listings', current_listings)
                    
                    Logger.info("RecruitmentApp: Listings data updated")
                    
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error checking listing updates: {str(e)}")

    def check_notification_updates(self):
        """Check for notification updates"""
        try:
            if self.current_user_id:
                # Get current notifications
                current_notifications = self.db.get_user_notifications(self.current_user_id)
                
                # Compare with cached data
                cached_notifications = self.data_cache.get('notifications', {}).get(self.current_user_id)
                
                if current_notifications != cached_notifications:
                    # Update cache
                    if 'notifications' not in self.data_cache:
                        self.data_cache['notifications'] = {}
                    self.data_cache['notifications'][self.current_user_id] = current_notifications
                    
                    # Notify observers
                    self.notify_data_changed('notifications', current_notifications)
                    
                    Logger.info("RecruitmentApp: Notifications data updated")
                    
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error checking notification updates: {str(e)}")

    def check_search_updates(self):
        """Check for search result updates"""
        try:
            # This would check if search results have changed
            # Implementation depends on your search logic
            pass
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error checking search updates: {str(e)}")

    def on_screen_change(self, screen_manager, screen_name):
        """Called when screen changes"""
        Logger.info(f"RecruitmentApp: Screen changed to {screen_name}")
        
        # Update last activity
        self.update_last_activity()
        
        # Update session data
        self.session_data['current_screen'] = screen_name
        
        # Trigger screen-specific refresh if callback exists
        if screen_name in self.screen_refresh_callbacks:
            try:
                self.screen_refresh_callbacks[screen_name]()
            except Exception as e:
                Logger.error(f"RecruitmentApp: Error in screen refresh callback: {str(e)}")
        
        # Refresh data for specific screens
        if screen_name == "profile":
            self.refresh_profile_data()
        elif screen_name == "my_list":
            self.refresh_listings_data()
        elif screen_name == "search":
            self.refresh_search_data()
        elif screen_name == "home":
            self.refresh_home_data()

    def refresh_profile_data(self):
        """Refresh profile data immediately"""
        try:
            if self.current_user_id:
                profile_data = self.db.get_user_profile(self.current_user_id)
                self.notify_data_changed('profile', profile_data)
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error refreshing profile data: {str(e)}")

    def refresh_listings_data(self):
        """Refresh listings data immediately"""
        try:
            if self.current_user_id:
                listings_data = self.db.get_user_listings(self.current_user_id)
                self.notify_data_changed('listings', listings_data)
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error refreshing listings data: {str(e)}")

    def refresh_search_data(self):
        """Refresh search data immediately"""
        try:
            # Implement search data refresh logic
            pass
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error refreshing search data: {str(e)}")

    def refresh_home_data(self):
        """Refresh home screen data immediately"""
        try:
            if self.current_user_id:
                # Refresh multiple data types for home screen
                self.refresh_profile_data()
                self.refresh_listings_data()
                self.check_notification_updates()
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error refreshing home data: {str(e)}")

    def refresh_all_data(self):
        """Refresh all cached data"""
        try:
            self.refresh_profile_data()
            self.refresh_listings_data()
            self.check_notification_updates()
            Logger.info("RecruitmentApp: All data refreshed")
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error refreshing all data: {str(e)}")

    def force_refresh_current_screen(self):
        """Force refresh the current screen"""
        current_screen_name = self.root.current
        self.on_screen_change(self.root, current_screen_name)
        show_toast("Data refreshed")

    def manual_refresh(self):
        """Manual refresh triggered by user"""
        self.refresh_all_data()
        show_toast("Data refreshed")

    # Profile Management with Live Updates
    def create_profile(self, profile_data):
        """Create new profile with live update notification"""
        try:
            result = self.db.create_profile(profile_data)
            if result:
                # Notify about profile creation
                self.notify_data_changed('profile', profile_data, 'create')
                show_toast("Profile created successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error creating profile: {str(e)}")
            show_toast("Error creating profile")
            return False

    def update_profile(self, profile_data):
        """Update profile with live update notification"""
        try:
            result = self.db.update_profile(self.current_user_id, profile_data)
            if result:
                # Notify about profile update
                self.notify_data_changed('profile', profile_data, 'update')
                show_toast("Profile updated successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error updating profile: {str(e)}")
            show_toast("Error updating profile")
            return False

    def delete_profile(self, profile_id):
        """Delete profile with live update notification"""
        try:
            result = self.db.delete_profile(profile_id)
            if result:
                # Notify about profile deletion
                self.notify_data_changed('profile', None, 'delete')
                show_toast("Profile deleted successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error deleting profile: {str(e)}")
            show_toast("Error deleting profile")
            return False

    # Listing Management with Live Updates
    def create_listing(self, listing_data):
        """Create new listing with live update notification"""
        try:
            result = self.db.create_listing(listing_data)
            if result:
                # Notify about listing creation
                self.notify_data_changed('listings', listing_data, 'create')
                show_toast("Listing created successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error creating listing: {str(e)}")
            show_toast("Error creating listing")
            return False

    def update_listing(self, listing_id, listing_data):
        """Update listing with live update notification"""
        try:
            result = self.db.update_listing(listing_id, listing_data)
            if result:
                # Notify about listing update
                self.notify_data_changed('listings', listing_data, 'update')
                show_toast("Listing updated successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error updating listing: {str(e)}")
            show_toast("Error updating listing")
            return False

    def delete_listing(self, listing_id):
        """Delete listing with live update notification"""
        try:
            result = self.db.delete_listing(listing_id)
            if result:
                # Notify about listing deletion
                self.notify_data_changed('listings', None, 'delete')
                show_toast("Listing deleted successfully")
                return True
            return False
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error deleting listing: {str(e)}")
            show_toast("Error deleting listing")
            return False

    # Existing methods continue...
    def start_session(self):
        """Start a new user session"""
        self.session_start_time = datetime.now()
        self.session_data = {
            'start_time': self.session_start_time.isoformat(),
            'last_activity': datetime.now().isoformat(),
            'current_screen': 'welcome'
        }
        Logger.info("RecruitmentApp: New session started")

    def reset_auto_logout_timer(self):
        """Reset the auto-logout timer"""
        if self.auto_logout_timer:
            self.auto_logout_timer.cancel()
        
        if self.current_user_id:
            self.auto_logout_timer = Clock.schedule_once(
                lambda dt: self.auto_logout("Auto-logout due to inactivity"),
                self.auto_logout_timeout
            )

    def auto_logout(self, reason="Session expired"):
        """Automatically logout user"""
        Logger.info(f"RecruitmentApp: Auto-logout triggered: {reason}")
        show_toast(reason)
        self.logout()

    def update_last_activity(self):
        """Update last activity timestamp"""
        if self.current_user_id:
            self.session_data['last_activity'] = datetime.now().isoformat()
            self.reset_auto_logout_timer()

    def save_app_state(self):
        """Save current app state to persistent storage"""
        try:
            app_state = {
                'user_id': self.current_user_id,
                'user_type': self.current_user_type,
                'user_name': self.current_user_name,
                'user_email': self.current_user_email,
                'current_screen': self.root.current if self.root else 'welcome',
                'session_data': self.session_data,
                'user_preferences': self.user_preferences,
                'data_cache': self.data_cache,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to app's private storage
            state_file = self.get_state_file_path()
            with open(state_file, 'w') as f:
                json.dump(app_state, f)
            
            Logger.info("RecruitmentApp: App state saved successfully")
            
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error saving app state: {str(e)}")

    def load_app_state(self):
        """Load app state from persistent storage"""
        try:
            state_file = self.get_state_file_path()
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    app_state = json.load(f)
                
                # Check if state is recent (within 24 hours)
                if self.is_state_valid(app_state.get('timestamp')):
                    self.session_data = app_state.get('session_data', {})
                    self.user_preferences = app_state.get('user_preferences', {})
                    self.data_cache = app_state.get('data_cache', {})
                    
                    Logger.info("RecruitmentApp: App state loaded successfully")
                    return app_state
                else:
                    Logger.info("RecruitmentApp: Saved state is too old, starting fresh")
                    
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error loading app state: {str(e)}")
        
        return None

    def should_restore_session(self):
        """Check if we should restore the user session"""
        saved_state = self.load_app_state()
        if saved_state and saved_state.get('user_id'):
            # Check if session is still valid
            if self.pause_start_time:
                pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
                return pause_duration < self.auto_logout_timeout
            return True
        return False

    def restore_user_session(self):
        """Restore user session from saved state"""
        saved_state = self.load_app_state()
        if saved_state:
            self.current_user_id = saved_state.get('user_id')
            self.current_user_type = saved_state.get('user_type')
            self.current_user_name = saved_state.get('user_name')
            self.current_user_email = saved_state.get('user_email')
            
            # Navigate to saved screen
            current_screen = saved_state.get('current_screen', 'welcome')
            if self.root and current_screen != 'welcome':
                Clock.schedule_once(lambda dt: setattr(self.root, 'current', current_screen), 0.5)
            
            # Restart auto-logout timer
            self.reset_auto_logout_timer()
            
            Logger.info("RecruitmentApp: User session restored")
            show_toast("Session restored")

    def start_background_tasks(self):
        """Start background tasks like data sync"""
        if self.current_user_id:
            # Schedule periodic background sync
            sync_task = Clock.schedule_interval(
                self.background_sync,
                self.background_sync_interval
            )
            self.background_tasks.append(sync_task)
            
            Logger.info("RecruitmentApp: Background tasks started")

    def stop_background_tasks(self):
        """Stop all background tasks"""
        for task in self.background_tasks:
            task.cancel()
        self.background_tasks.clear()
        
        # Also stop live data monitoring
        Clock.unschedule(self.check_for_data_updates)
        
        Logger.info("RecruitmentApp: Background tasks stopped")

    def background_sync(self, dt):
        """Perform background data synchronization"""
        if self.current_user_id and self.app_state == "running":
            try:
                # Sync user data, notifications, etc.
                # This is where you'd implement actual sync logic
                Logger.info("RecruitmentApp: Background sync completed")
            except Exception as e:
                Logger.error(f"RecruitmentApp: Background sync failed: {str(e)}")

    def cleanup_resources(self):
        """Clean up resources before app shutdown"""
        try:
            # Clear temporary files
            self.clear_temp_files()
            
            # Clean up database resources
            if self.db and hasattr(self.db, 'cleanup_temp_files'):
                self.db.cleanup_temp_files()
            
            # Cancel scheduled tasks
            Clock.unschedule(self.background_sync)
            Clock.unschedule(self.check_for_data_updates)
            
            # Clear observers
            self.data_observers.clear()
            self.screen_refresh_callbacks.clear()
            
            Logger.info("RecruitmentApp: Resources cleaned up")
            
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error during cleanup: {str(e)}")

    def get_state_file_path(self):
        """Get the path for the state file"""
        try:
            if platform == 'android':
                # Import android.storage only when actually needed and on Android
                try:
                    from android.storage import app_storage_path
                    return os.path.join(app_storage_path(), 'app_state.json')
                except ImportError:
                    Logger.warning("RecruitmentApp: Android storage not available, using fallback")
                    # Fall through to desktop path
            
            # For desktop/development environment
            # Create app data directory if it doesn't exist
            app_data_dir = self.user_data_dir
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            return os.path.join(app_data_dir, 'app_state.json')
            
        except Exception as e:
            # Final fallback to current directory
            Logger.warning(f"RecruitmentApp: Error getting state file path: {e}, using current directory")
            return os.path.join(os.getcwd(), 'app_state.json')

    def clear_temp_files(self):
        """Clear temporary files"""
        try:
            temp_dir = os.path.join(self.user_data_dir, 'temp')
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                Logger.info("RecruitmentApp: Temporary files cleared")
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error clearing temp files: {str(e)}")

    def is_state_valid(self, timestamp_str):
        """Check if saved state timestamp is valid (within 24 hours)"""
        if not timestamp_str:
            return False
        
        try:
            saved_time = datetime.fromisoformat(timestamp_str)
            time_diff = (datetime.now() - saved_time).total_seconds()
            return time_diff < 86400  # 24 hours
        except:
            return False

    def show_startup_message(self, dt):
        """Show startup message"""
        if self.current_user_id:
            show_toast(f"Welcome back, {self.current_user_name}!")
        else:
            show_toast("Welcome to Recruitment App!")

    def fetch_and_display_data(self, service_name):
        """Method to handle service card clicks from KV file"""
        self.update_last_activity()  # Update activity on user interaction
        
        current_screen = self.root.current_screen
        if hasattr(current_screen, 'fetch_and_display_data'):
            current_screen.fetch_and_display_data(service_name)

    def logout(self):
        """Logout current user"""
        Logger.info("RecruitmentApp: User logging out")
        
        # Clear user data
        self.current_user_id = None
        self.current_user_type = None
        self.current_user_name = None
        self.current_user_email = None
        self.current_user_password = None
        
        # Cancel auto-logout timer
        if self.auto_logout_timer:
            self.auto_logout_timer.cancel()
            self.auto_logout_timer = None
        
        # Stop background tasks
        self.stop_background_tasks()
        
        # Clear session data and cache
        self.session_data = {}
        self.session_start_time = None
        self.data_cache = {
            'profiles': {},
            'listings': {},
            'notifications': {},
            'search_results': {},
            'user_data': {}
        }
        
        # Clear observers
        self.data_observers.clear()
        self.screen_refresh_callbacks.clear()
        
        # Save cleared state
        self.save_app_state()
        
        # Navigate to login screen
        self.root.current = "login"
        
        # Reset the ShowScreen's internal screen manager to Home
        show_screen = None
        for screen in self.root.screens:
            if screen.name == "show":
                show_screen = screen
                break
        
        if show_screen and hasattr(show_screen, 'ids') and 'screen_manager' in show_screen.ids:
            show_screen.ids.screen_manager.current = "Home"
            
            if hasattr(show_screen, 'reset_to_home'):
                show_screen.reset_to_home()
        
        show_toast("Logged out successfully")

    def user_login_success(self, user_id, user_type, user_name, user_email, password=None):
        """Handle successful user login"""
        self.current_user_id = user_id
        self.current_user_type = user_type
        self.current_user_name = user_name
        self.current_user_email = user_email
        self.current_user_password = password
        
        # Start session management
        self.start_session()
        self.reset_auto_logout_timer()
        self.start_background_tasks()
        
        # Setup live data monitoring
        self.setup_live_data_monitoring()
        
        # Initial data load
        self.refresh_all_data()
        
        # Save state
        self.save_app_state()
        
        Logger.info(f"RecruitmentApp: User {user_name} logged in successfully")

    def on_user_interaction(self):
        """Call this method on any user interaction to reset timers"""
        self.update_last_activity()

    # Additional utility methods for screen integration
    def get_screen_by_name(self, screen_name):
        """Get screen instance by name"""
        for screen in self.root.screens:
            if screen.name == screen_name:
                return screen
        return None

    def refresh_screen_data(self, screen_name):
        """Refresh data for a specific screen"""
        screen = self.get_screen_by_name(screen_name)
        if screen and hasattr(screen, 'refresh_data'):
            screen.refresh_data()

    def toggle_auto_refresh(self, enabled=None):
        """Toggle auto-refresh on/off"""
        if enabled is None:
            self.auto_refresh_enabled = not self.auto_refresh_enabled
        else:
            self.auto_refresh_enabled = enabled
        
        if self.auto_refresh_enabled:
            # Start auto-refresh
            Clock.schedule_interval(self.check_for_data_updates, self.refresh_interval)
            show_toast("Auto-refresh enabled")
        else:
            # Stop auto-refresh
            Clock.unschedule(self.check_for_data_updates)
            show_toast("Auto-refresh disabled")
        
        Logger.info(f"RecruitmentApp: Auto-refresh {'enabled' if self.auto_refresh_enabled else 'disabled'}")

    def set_refresh_interval(self, interval):
        """Set the refresh interval in seconds"""
        self.refresh_interval = interval
        
        # Restart auto-refresh with new interval
        if self.auto_refresh_enabled:
            Clock.unschedule(self.check_for_data_updates)
            Clock.schedule_interval(self.check_for_data_updates, self.refresh_interval)
        
        Logger.info(f"RecruitmentApp: Refresh interval set to {interval} seconds")

    def get_cached_data(self, data_type, key=None):
        """Get cached data"""
        if data_type in self.data_cache:
            if key:
                return self.data_cache[data_type].get(key)
            return self.data_cache[data_type]
        return None

    def clear_data_cache(self, data_type=None):
        """Clear data cache"""
        if data_type:
            if data_type in self.data_cache:
                self.data_cache[data_type].clear()
                Logger.info(f"RecruitmentApp: Cleared {data_type} cache")
        else:
            self.data_cache = {
                'profiles': {},
                'listings': {},
                'notifications': {},
                'search_results': {},
                'user_data': {}
            }
            Logger.info("RecruitmentApp: Cleared all data cache")

    def add_refresh_button_to_screen(self, screen):
        """Add a refresh button to a screen (helper method)"""
        # This is a helper method that screens can use to add refresh functionality
        # Implementation would depend on the specific screen layout
        pass

    def show_data_loading_indicator(self, show=True):
        """Show/hide data loading indicator"""
        # This would show a loading spinner or indicator
        # Implementation depends on your UI design
        pass

    def handle_data_error(self, error_message):
        """Handle data loading errors"""
        Logger.error(f"RecruitmentApp: Data error: {error_message}")
        show_toast(f"Data error: {error_message}")

    def sync_offline_changes(self):
        """Sync any offline changes when connection is restored"""
        # This would handle syncing changes made while offline
        try:
            # Implement offline sync logic here
            Logger.info("RecruitmentApp: Offline changes synced")
        except Exception as e:
            Logger.error(f"RecruitmentApp: Error syncing offline changes: {str(e)}")


if __name__ == "__main__":
    RecruitmentApp().run()