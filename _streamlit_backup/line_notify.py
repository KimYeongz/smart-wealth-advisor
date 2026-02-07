"""
LINE Notify Integration Module
==============================
ส่งการแจ้งเตือนผ่าน LINE Notify API

การใช้งาน:
1. ขอ Token จาก https://notify-bot.line.me/
2. ตั้งค่า Token ใน environment variable หรือ config
3. เรียกใช้ send_line_notify()
"""

import requests
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime
import os


# =============================================================================
# CONFIGURATION
# =============================================================================

# LINE Notify API Endpoint
LINE_NOTIFY_API = "https://notify-api.line.me/api/notify"

# ดึง Token จาก Environment Variable หรือใช้ค่า default (mock mode)
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN", "")

# Mock mode flag
MOCK_MODE = True  # เปลี่ยนเป็น False เมื่อมี Token จริง


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class NotifyResult:
    """ผลลัพธ์การส่งการแจ้งเตือน"""
    success: bool
    status_code: int
    message: str
    timestamp: str
    mock_mode: bool = False


@dataclass 
class AdvisorAlert:
    """ข้อมูลแจ้งเตือนที่ปรึกษา"""
    client_name: str
    client_id: int
    portfolio_value: float
    daily_change: float
    daily_change_pct: float
    alert_reason: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    priority: str = "NORMAL"  # NORMAL, HIGH, URGENT


# =============================================================================
# LINE NOTIFY FUNCTIONS
# =============================================================================

def send_line_notify(
    message: str,
    token: Optional[str] = None,
    image_url: Optional[str] = None
) -> NotifyResult:
    """
    ส่งข้อความผ่าน LINE Notify
    
    Args:
        message: ข้อความที่ต้องการส่ง
        token: LINE Notify Token (ถ้าไม่ระบุจะใช้ค่าจาก env)
        image_url: URL รูปภาพ (optional)
    
    Returns:
        NotifyResult พร้อมสถานะการส่ง
    """
    use_token = token or LINE_NOTIFY_TOKEN
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Mock mode - ไม่ส่งจริง แต่ log ไว้
    if MOCK_MODE or not use_token:
        print(f"[MOCK LINE NOTIFY] {timestamp}")
        print(f"Message: {message}")
        print("-" * 50)
        
        return NotifyResult(
            success=True,
            status_code=200,
            message="[MOCK] ข้อความถูกบันทึก (ไม่ได้ส่งจริง)",
            timestamp=timestamp,
            mock_mode=True
        )
    
    # ส่งจริง
    try:
        headers = {
            "Authorization": f"Bearer {use_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {"message": message}
        
        if image_url:
            payload["imageThumbnail"] = image_url
            payload["imageFullsize"] = image_url
        
        response = requests.post(
            LINE_NOTIFY_API,
            headers=headers,
            data=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return NotifyResult(
                success=True,
                status_code=200,
                message="ส่งข้อความสำเร็จ",
                timestamp=timestamp
            )
        else:
            return NotifyResult(
                success=False,
                status_code=response.status_code,
                message=f"Error: {response.text}",
                timestamp=timestamp
            )
            
    except requests.exceptions.RequestException as e:
        return NotifyResult(
            success=False,
            status_code=500,
            message=f"Connection Error: {str(e)}",
            timestamp=timestamp
        )


def format_advisor_alert(alert: AdvisorAlert) -> str:
    """
    จัดรูปแบบข้อความแจ้งเตือนที่ปรึกษา
    
    Args:
        alert: ข้อมูลการแจ้งเตือน
    
    Returns:
        ข้อความที่จัดรูปแบบแล้ว
    """
    # กำหนด emoji ตาม priority
    priority_emoji = {
        "NORMAL": "📊",
        "HIGH": "⚠️",
        "URGENT": "🚨"
    }
    emoji = priority_emoji.get(alert.priority, "📊")
    
    # กำหนดสีตามการเปลี่ยนแปลง
    change_symbol = "📈" if alert.daily_change >= 0 else "📉"
    
    message = f"""
{emoji} แจ้งเตือนจากระบบ Wealth Advisor

👤 ลูกค้า: {alert.client_name} (ID: {alert.client_id})
💰 มูลค่าพอร์ต: ฿{alert.portfolio_value:,.0f}
{change_symbol} เปลี่ยนแปลง: ฿{alert.daily_change:+,.0f} ({alert.daily_change_pct:+.2f}%)

📋 เหตุผล: {alert.alert_reason}
"""
    
    if alert.contact_phone:
        message += f"📞 โทร: {alert.contact_phone}\n"
    
    if alert.contact_email:
        message += f"📧 Email: {alert.contact_email}\n"
    
    message += f"\n⏰ เวลา: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    return message


def send_advisor_alert(alert: AdvisorAlert, token: Optional[str] = None) -> NotifyResult:
    """
    ส่งการแจ้งเตือนถึงที่ปรึกษา
    
    Args:
        alert: ข้อมูลการแจ้งเตือน
        token: LINE Notify Token
    
    Returns:
        NotifyResult
    """
    message = format_advisor_alert(alert)
    return send_line_notify(message, token)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_portfolio_needs_alert(
    current_value: float,
    previous_value: float,
    threshold_pct: float = -5.0
) -> bool:
    """
    ตรวจสอบว่าพอร์ตต้องการแจ้งเตือนหรือไม่
    
    Args:
        current_value: มูลค่าปัจจุบัน
        previous_value: มูลค่าเดิม
        threshold_pct: เกณฑ์การแจ้งเตือน (default: -5%)
    
    Returns:
        True ถ้าต้องแจ้งเตือน
    """
    if previous_value <= 0:
        return False
    
    change_pct = ((current_value - previous_value) / previous_value) * 100
    return change_pct <= threshold_pct


def create_panic_alert(
    client_name: str,
    client_id: int,
    portfolio_value: float,
    daily_change: float,
    contact_phone: Optional[str] = None
) -> AdvisorAlert:
    """
    สร้างการแจ้งเตือนฉุกเฉิน (ตลาดตก ลูกค้าแพนิค)
    
    Args:
        client_name: ชื่อลูกค้า
        client_id: รหัสลูกค้า
        portfolio_value: มูลค่าพอร์ต
        daily_change: การเปลี่ยนแปลง
        contact_phone: เบอร์โทรศัพท์
    
    Returns:
        AdvisorAlert
    """
    daily_change_pct = (daily_change / (portfolio_value - daily_change)) * 100
    
    return AdvisorAlert(
        client_name=client_name,
        client_id=client_id,
        portfolio_value=portfolio_value,
        daily_change=daily_change,
        daily_change_pct=daily_change_pct,
        alert_reason="ลูกค้าต้องการคำปรึกษา - พอร์ตติดลบ",
        contact_phone=contact_phone,
        priority="URGENT"
    )


def test_line_notify(token: Optional[str] = None) -> NotifyResult:
    """
    ทดสอบการเชื่อมต่อ LINE Notify
    
    Args:
        token: LINE Notify Token
    
    Returns:
        NotifyResult
    """
    test_message = """
🧪 ทดสอบการเชื่อมต่อ LINE Notify

✅ ระบบ Wealth Advisor เชื่อมต่อสำเร็จ
📊 พร้อมส่งการแจ้งเตือนแล้ว
"""
    return send_line_notify(test_message, token)


# =============================================================================
# CONFIGURATION HELPERS
# =============================================================================

def set_line_token(token: str) -> bool:
    """
    ตั้งค่า LINE Notify Token
    
    Args:
        token: LINE Notify Token
    
    Returns:
        True ถ้าตั้งค่าสำเร็จ
    """
    global LINE_NOTIFY_TOKEN, MOCK_MODE
    
    if token and len(token) > 10:
        LINE_NOTIFY_TOKEN = token
        MOCK_MODE = False
        return True
    return False


def get_notify_status() -> Dict:
    """
    ดึงสถานะการตั้งค่า LINE Notify
    
    Returns:
        Dict with status information
    """
    return {
        "token_set": bool(LINE_NOTIFY_TOKEN),
        "mock_mode": MOCK_MODE,
        "api_endpoint": LINE_NOTIFY_API
    }
