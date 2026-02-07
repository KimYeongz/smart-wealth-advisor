"""
Supabase Authentication Module
==============================
จัดการ Authentication และ Role-based Access Control

Roles:
- client: ลูกค้าทั่วไป
- advisor: ที่ปรึกษาการเงิน
- admin: ผู้ดูแลระบบ
"""

import os
import streamlit as st
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from enum import Enum

# Try to import supabase, fallback to mock mode if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Check if we should use mock mode
MOCK_MODE = not (SUPABASE_URL and SUPABASE_KEY and SUPABASE_AVAILABLE)


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class UserRole(Enum):
    CLIENT = "client"
    ADVISOR = "advisor"
    ADMIN = "admin"


@dataclass
class User:
    """ข้อมูลผู้ใช้"""
    id: str
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    advisor_id: Optional[str] = None
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_advisor(self) -> bool:
        return self.role == UserRole.ADVISOR
    
    @property
    def is_client(self) -> bool:
        return self.role == UserRole.CLIENT
    
    def has_role(self, role: UserRole) -> bool:
        return self.role == role
    
    def can_access(self, required_roles: List[UserRole]) -> bool:
        """ตรวจสอบว่า user มีสิทธิ์เข้าถึงหรือไม่"""
        # Admin can access everything
        if self.is_admin:
            return True
        return self.role in required_roles


@dataclass
class AuthResult:
    """ผลลัพธ์การ authentication"""
    success: bool
    message: str
    user: Optional[User] = None
    error_code: Optional[str] = None


# =============================================================================
# MOCK DATA (for development/testing) - Passwords are hashed for security
# =============================================================================

import hashlib
from collections import defaultdict
import time

def hash_password(password: str) -> str:
    """Hash password using SHA256 - Use bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed

# Pre-hashed passwords (original: client123, advisor123, admin123)
MOCK_USERS = {
    "client@example.com": {
        "id": "user-001",
        "email": "client@example.com",
        "password_hash": hash_password("client123"),
        "full_name": "คุณสมชาย ใจดี",
        "role": "client",
        "phone": "081-234-5678",
        "advisor_id": "user-002"
    },
    "advisor@example.com": {
        "id": "user-002",
        "email": "advisor@example.com",
        "password_hash": hash_password("advisor123"),
        "full_name": "คุณวิชัย ที่ปรึกษา",
        "role": "advisor",
        "phone": "082-345-6789"
    },
    "admin@example.com": {
        "id": "user-003",
        "email": "admin@example.com",
        "password_hash": hash_password("admin123"),
        "full_name": "ผู้ดูแลระบบ",
        "role": "admin",
        "phone": "083-456-7890"
    }
}

# Rate limiting configuration
LOGIN_ATTEMPTS = defaultdict(list)  # email -> [timestamp, ...]
MAX_ATTEMPTS = 5  # Max login attempts
LOCKOUT_DURATION = 300  # 5 minutes lockout

def check_rate_limit(email: str) -> Tuple[bool, str]:
    """
    Check if login is rate limited.
    Returns (is_allowed, message)
    """
    email = email.lower().strip()
    current_time = time.time()
    
    # Clean old attempts (older than lockout duration)
    LOGIN_ATTEMPTS[email] = [
        t for t in LOGIN_ATTEMPTS[email] 
        if current_time - t < LOCKOUT_DURATION
    ]
    
    if len(LOGIN_ATTEMPTS[email]) >= MAX_ATTEMPTS:
        remaining = int(LOCKOUT_DURATION - (current_time - LOGIN_ATTEMPTS[email][0]))
        return False, f"บัญชีถูกล็อคชั่วคราว กรุณารอ {remaining} วินาที"
    
    return True, ""

def record_login_attempt(email: str):
    """Record a failed login attempt."""
    email = email.lower().strip()
    LOGIN_ATTEMPTS[email].append(time.time())

def clear_login_attempts(email: str):
    """Clear login attempts after successful login."""
    email = email.lower().strip()
    LOGIN_ATTEMPTS[email] = []


# =============================================================================
# AUTH CLASS
# =============================================================================

class SupabaseAuth:
    """จัดการ Authentication กับ Supabase หรือ Mock Mode"""
    
    def __init__(self):
        self.mock_mode = MOCK_MODE
        self.client: Optional[Client] = None
        
        if not self.mock_mode:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                self.mock_mode = True
    
    def _dict_to_user(self, data: Dict) -> User:
        """แปลง dict เป็น User object"""
        return User(
            id=data.get("id", ""),
            email=data.get("email", ""),
            full_name=data.get("full_name", ""),
            role=UserRole(data.get("role", "client")),
            phone=data.get("phone"),
            advisor_id=data.get("advisor_id")
        )
    
    # =========================================================================
    # LOGIN
    # =========================================================================
    
    def login(self, email: str, password: str) -> AuthResult:
        """
        เข้าสู่ระบบด้วย email และ password
        
        Args:
            email: อีเมล
            password: รหัสผ่าน
        
        Returns:
            AuthResult
        """
        # Check rate limiting first
        is_allowed, rate_msg = check_rate_limit(email)
        if not is_allowed:
            return AuthResult(
                success=False,
                message=rate_msg,
                error_code="RATE_LIMITED"
            )
        
        if self.mock_mode:
            return self._mock_login(email, password)
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Get user profile from profiles table
                profile = self.client.table("profiles").select("*").eq(
                    "id", response.user.id
                ).single().execute()
                
                if profile.data:
                    clear_login_attempts(email)  # Clear on success
                    user = self._dict_to_user(profile.data)
                    return AuthResult(
                        success=True,
                        message="เข้าสู่ระบบสำเร็จ",
                        user=user
                    )
            
            record_login_attempt(email)  # Record failed attempt
            return AuthResult(
                success=False,
                message="อีเมลหรือรหัสผ่านไม่ถูกต้อง",
                error_code="INVALID_CREDENTIALS"
            )
            
        except Exception as e:
            record_login_attempt(email)  # Record failed attempt
            return AuthResult(
                success=False,
                message=f"เกิดข้อผิดพลาด: {str(e)}",
                error_code="AUTH_ERROR"
            )
    
    def _mock_login(self, email: str, password: str) -> AuthResult:
        """Mock login for development with hashed password verification"""
        email = email.lower().strip()
        
        if email in MOCK_USERS:
            user_data = MOCK_USERS[email]
            # Verify password using hash
            if verify_password(password, user_data["password_hash"]):
                clear_login_attempts(email)  # Clear on success
                user = self._dict_to_user(user_data)
                return AuthResult(
                    success=True,
                    message="[Mock] เข้าสู่ระบบสำเร็จ",
                    user=user
                )
        
        record_login_attempt(email)  # Record failed attempt
        return AuthResult(
            success=False,
            message="อีเมลหรือรหัสผ่านไม่ถูกต้อง",
            error_code="INVALID_CREDENTIALS"
        )
    
    # =========================================================================
    # REGISTER
    # =========================================================================
    
    def register(
        self, 
        email: str, 
        password: str, 
        full_name: str,
        role: UserRole = UserRole.CLIENT,
        phone: Optional[str] = None
    ) -> AuthResult:
        """
        ลงทะเบียนผู้ใช้ใหม่
        
        Args:
            email: อีเมล
            password: รหัสผ่าน
            full_name: ชื่อเต็ม
            role: บทบาท (default: client)
            phone: เบอร์โทรศัพท์
        
        Returns:
            AuthResult
        """
        if self.mock_mode:
            return self._mock_register(email, password, full_name, role, phone)
        
        try:
            # Create auth user
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Create profile
                profile_data = {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "role": role.value,
                    "phone": phone
                }
                
                self.client.table("profiles").insert(profile_data).execute()
                
                user = self._dict_to_user(profile_data)
                return AuthResult(
                    success=True,
                    message="ลงทะเบียนสำเร็จ! กรุณายืนยันอีเมล",
                    user=user
                )
            
            return AuthResult(
                success=False,
                message="ไม่สามารถสร้างบัญชีได้",
                error_code="REGISTRATION_FAILED"
            )
            
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return AuthResult(
                    success=False,
                    message="อีเมลนี้ถูกใช้งานแล้ว",
                    error_code="EMAIL_EXISTS"
                )
            return AuthResult(
                success=False,
                message=f"เกิดข้อผิดพลาด: {error_msg}",
                error_code="REGISTRATION_ERROR"
            )
    
    def _mock_register(
        self, 
        email: str, 
        password: str, 
        full_name: str,
        role: UserRole,
        phone: Optional[str]
    ) -> AuthResult:
        """Mock register for development with hashed passwords"""
        email = email.lower().strip()
        
        if email in MOCK_USERS:
            return AuthResult(
                success=False,
                message="อีเมลนี้ถูกใช้งานแล้ว",
                error_code="EMAIL_EXISTS"
            )
        
        # Add to mock users with hashed password
        new_id = f"user-{len(MOCK_USERS) + 1:03d}"
        MOCK_USERS[email] = {
            "id": new_id,
            "email": email,
            "password_hash": hash_password(password),  # Hash the password!
            "full_name": full_name,
            "role": role.value,
            "phone": phone
        }
        
        user = self._dict_to_user(MOCK_USERS[email])
        return AuthResult(
            success=True,
            message="[Mock] ลงทะเบียนสำเร็จ!",
            user=user
        )
    
    # =========================================================================
    # PASSWORD RESET
    # =========================================================================
    
    def reset_password(self, email: str) -> AuthResult:
        """
        ส่งอีเมลรีเซ็ตรหัสผ่าน
        
        Args:
            email: อีเมลที่ลงทะเบียน
        
        Returns:
            AuthResult
        """
        if self.mock_mode:
            return AuthResult(
                success=True,
                message="[Mock] ส่งลิงก์รีเซ็ตรหัสผ่านไปที่อีเมลแล้ว"
            )
        
        try:
            self.client.auth.reset_password_email(email)
            return AuthResult(
                success=True,
                message="ส่งลิงก์รีเซ็ตรหัสผ่านไปที่อีเมลแล้ว"
            )
        except Exception as e:
            return AuthResult(
                success=False,
                message=f"เกิดข้อผิดพลาด: {str(e)}",
                error_code="RESET_ERROR"
            )
    
    # =========================================================================
    # LOGOUT
    # =========================================================================
    
    def logout(self) -> AuthResult:
        """ออกจากระบบ"""
        if not self.mock_mode and self.client:
            try:
                self.client.auth.sign_out()
            except:
                pass
        
        return AuthResult(
            success=True,
            message="ออกจากระบบสำเร็จ"
        )
    
    # =========================================================================
    # USER MANAGEMENT (Admin only)
    # =========================================================================
    
    def get_all_users(self) -> List[User]:
        """ดึงรายชื่อผู้ใช้ทั้งหมด (Admin only)"""
        if self.mock_mode:
            return [self._dict_to_user(u) for u in MOCK_USERS.values()]
        
        try:
            response = self.client.table("profiles").select("*").execute()
            return [self._dict_to_user(u) for u in response.data]
        except:
            return []
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """ดึงรายชื่อผู้ใช้ตาม role"""
        if self.mock_mode:
            return [
                self._dict_to_user(u) 
                for u in MOCK_USERS.values() 
                if u["role"] == role.value
            ]
        
        try:
            response = self.client.table("profiles").select("*").eq(
                "role", role.value
            ).execute()
            return [self._dict_to_user(u) for u in response.data]
        except:
            return []
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> AuthResult:
        """เปลี่ยน role ของ user (Admin only)"""
        if self.mock_mode:
            for email, user in MOCK_USERS.items():
                if user["id"] == user_id:
                    user["role"] = new_role.value
                    return AuthResult(
                        success=True,
                        message=f"[Mock] เปลี่ยน role เป็น {new_role.value} สำเร็จ"
                    )
            return AuthResult(success=False, message="ไม่พบผู้ใช้")
        
        try:
            self.client.table("profiles").update({
                "role": new_role.value
            }).eq("id", user_id).execute()
            
            return AuthResult(
                success=True,
                message=f"เปลี่ยน role เป็น {new_role.value} สำเร็จ"
            )
        except Exception as e:
            return AuthResult(
                success=False,
                message=f"เกิดข้อผิดพลาด: {str(e)}"
            )
    
    def get_advisor_clients(self, advisor_id: str) -> List[User]:
        """ดึงรายชื่อลูกค้าของที่ปรึกษา"""
        if self.mock_mode:
            return [
                self._dict_to_user(u) 
                for u in MOCK_USERS.values() 
                if u.get("advisor_id") == advisor_id
            ]
        
        try:
            response = self.client.table("profiles").select("*").eq(
                "advisor_id", advisor_id
            ).execute()
            return [self._dict_to_user(u) for u in response.data]
        except:
            return []


# =============================================================================
# SESSION MANAGEMENT (Streamlit)
# =============================================================================

def init_session_state():
    """Initialize session state for authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth" not in st.session_state:
        st.session_state.auth = SupabaseAuth()


def get_current_user() -> Optional[User]:
    """ดึงข้อมูล user ปัจจุบัน"""
    init_session_state()
    return st.session_state.user if st.session_state.authenticated else None


def is_authenticated() -> bool:
    """ตรวจสอบว่า login แล้วหรือยัง"""
    init_session_state()
    return st.session_state.authenticated


def login_user(user: User):
    """บันทึก user ลง session"""
    st.session_state.authenticated = True
    st.session_state.user = user


def logout_user():
    """ล้าง session"""
    st.session_state.authenticated = False
    st.session_state.user = None
    if "auth" in st.session_state:
        st.session_state.auth.logout()


def require_auth():
    """ตรวจสอบว่า login แล้ว ถ้าไม่ให้หยุดแสดงผล"""
    if not is_authenticated():
        st.warning("กรุณาเข้าสู่ระบบก่อน")
        st.stop()


def require_role(allowed_roles: List[UserRole]):
    """ตรวจสอบว่า user มี role ที่อนุญาต"""
    require_auth()
    user = get_current_user()
    
    if user and not user.can_access(allowed_roles):
        st.error("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def show_login_form() -> Optional[User]:
    """แสดงฟอร์ม Login"""
    init_session_state()
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='
            background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        '>💎 Smart Wealth Advisor</h1>
        <p style='color: #888;'>ระบบที่ปรึกษาการเงินอัจฉริยะ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for Login / Register
    tab_login, tab_register, tab_forgot = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สมัครสมาชิก", "🔑 ลืมรหัสผ่าน"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("📧 อีเมล", placeholder="your@email.com")
            password = st.text_input("🔒 รหัสผ่าน", type="password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox("จดจำฉัน")
            
            submitted = st.form_submit_button("เข้าสู่ระบบ", type="primary", use_container_width=True)
            
            if submitted:
                if not email or not password:
                    st.error("กรุณากรอกอีเมลและรหัสผ่าน")
                else:
                    result = st.session_state.auth.login(email, password)
                    if result.success:
                        login_user(result.user)
                        st.success(result.message)
                        st.rerun()
                    else:
                        st.error(result.message)
        
        # Mock mode notice
        if MOCK_MODE:
            st.info("""
            📌 **โหมดทดสอบ** - ใช้บัญชีตัวอย่าง:
            - Client: `client@example.com` / `client123`
            - Advisor: `advisor@example.com` / `advisor123`
            - Admin: `admin@example.com` / `admin123`
            """)
    
    with tab_register:
        with st.form("register_form"):
            new_email = st.text_input("📧 อีเมล", placeholder="your@email.com", key="reg_email")
            new_password = st.text_input("🔒 รหัสผ่าน", type="password", key="reg_pass")
            confirm_password = st.text_input("🔒 ยืนยันรหัสผ่าน", type="password")
            full_name = st.text_input("👤 ชื่อ-นามสกุล", placeholder="สมชาย ใจดี")
            phone = st.text_input("📞 เบอร์โทรศัพท์", placeholder="08x-xxx-xxxx")
            
            submitted = st.form_submit_button("สมัครสมาชิก", type="primary", use_container_width=True)
            
            if submitted:
                if not new_email or not new_password or not full_name:
                    st.error("กรุณากรอกข้อมูลให้ครบ")
                elif new_password != confirm_password:
                    st.error("รหัสผ่านไม่ตรงกัน")
                elif len(new_password) < 6:
                    st.error("รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
                else:
                    result = st.session_state.auth.register(
                        email=new_email,
                        password=new_password,
                        full_name=full_name,
                        role=UserRole.CLIENT,
                        phone=phone
                    )
                    if result.success:
                        st.success(result.message)
                        if MOCK_MODE:
                            # Auto login in mock mode
                            login_user(result.user)
                            st.rerun()
                    else:
                        st.error(result.message)
    
    with tab_forgot:
        with st.form("forgot_form"):
            reset_email = st.text_input("📧 อีเมลที่ลงทะเบียน", placeholder="your@email.com")
            
            submitted = st.form_submit_button("ส่งลิงก์รีเซ็ตรหัสผ่าน", type="primary", use_container_width=True)
            
            if submitted:
                if not reset_email:
                    st.error("กรุณากรอกอีเมล")
                else:
                    result = st.session_state.auth.reset_password(reset_email)
                    if result.success:
                        st.success(result.message)
                    else:
                        st.error(result.message)
    
    return None


def show_user_menu():
    """แสดงเมนู user ใน sidebar"""
    user = get_current_user()
    if not user:
        return
    
    st.sidebar.markdown("---")
    
    # User info
    role_badge = {
        UserRole.CLIENT: "🧑‍💼 ลูกค้า",
        UserRole.ADVISOR: "👨‍💼 ที่ปรึกษา",
        UserRole.ADMIN: "👑 แอดมิน"
    }
    
    st.sidebar.markdown(f"""
    <div style='padding: 1rem; background: #1a1d24; border-radius: 10px; margin-bottom: 1rem;'>
        <p style='color: #888; margin: 0; font-size: 0.85rem;'>เข้าสู่ระบบในฐานะ</p>
        <p style='color: #fff; margin: 0.3rem 0 0 0; font-weight: 600;'>{user.full_name}</p>
        <p style='color: #00D26A; margin: 0.2rem 0 0 0; font-size: 0.9rem;'>{role_badge.get(user.role, "")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.sidebar.button("🚪 ออกจากระบบ", use_container_width=True):
        logout_user()
        st.rerun()


def get_menu_by_role(user: User) -> Tuple[List[str], List[str]]:
    """ดึงเมนูตาม role ของ user"""
    base_menu = ["แดชบอร์ด", "จัดการพอร์ต"]
    base_icons = ["speedometer2", "wallet2"]
    
    if user.is_client:
        return (
            base_menu + ["Monte Carlo", "วางแผนภาษี", "รายงาน PDF", "ติดต่อที่ปรึกษา"],
            base_icons + ["bar-chart-line", "calculator", "file-pdf", "telephone"]
        )
    
    elif user.is_advisor:
        return (
            base_menu + ["ลูกค้าของฉัน", "Black-Litterman", "Monte Carlo", "ปรับสมดุล", "รายงาน PDF"],
            base_icons + ["people", "graph-up-arrow", "bar-chart-line", "arrow-repeat", "file-pdf"]
        )
    
    elif user.is_admin:
        return (
            base_menu + ["จัดการผู้ใช้", "Black-Litterman", "Monte Carlo", "ปรับสมดุล", "วางแผนภาษี", "รายงาน PDF", "ติดต่อที่ปรึกษา"],
            base_icons + ["people-fill", "graph-up-arrow", "bar-chart-line", "arrow-repeat", "calculator", "file-pdf", "telephone"]
        )
    
    return base_menu, base_icons

