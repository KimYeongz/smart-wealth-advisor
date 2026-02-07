"""
Thai Tax Optimization Module (ภาษี 2567)
==========================================
คำนวณการลดหย่อนภาษีและแนะนำ SSF/RMF ที่เหมาะสม

อ้างอิง: กฎเกณฑ์ภาษี พ.ศ. 2567 (ปีภาษี 2024)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


# =============================================================================
# TAX RATES 2567 (2024)
# =============================================================================

# อัตราภาษีเงินได้บุคคลธรรมดา 2567
TAX_BRACKETS_2567 = [
    (150_000, 0.00),      # 0 - 150,000 = ยกเว้น
    (300_000, 0.05),      # 150,001 - 300,000 = 5%
    (500_000, 0.10),      # 300,001 - 500,000 = 10%
    (750_000, 0.15),      # 500,001 - 750,000 = 15%
    (1_000_000, 0.20),    # 750,001 - 1,000,000 = 20%
    (2_000_000, 0.25),    # 1,000,001 - 2,000,000 = 25%
    (5_000_000, 0.30),    # 2,000,001 - 5,000,000 = 30%
    (float('inf'), 0.35)  # มากกว่า 5,000,000 = 35%
]

# ค่าลดหย่อนพื้นฐาน
PERSONAL_DEDUCTION = 60_000          # ค่าลดหย่อนส่วนตัว
SPOUSE_DEDUCTION = 60_000            # คู่สมรส
CHILD_DEDUCTION = 30_000             # บุตร (ต่อคน)
PARENT_DEDUCTION = 30_000            # บิดามารดา (ต่อคน สูงสุด 4)
INSURANCE_LIFE_MAX = 100_000         # ประกันชีวิต
INSURANCE_HEALTH_MAX = 25_000        # ประกันสุขภาพ
SOCIAL_SECURITY_MAX = 9_000          # ประกันสังคม
PROVIDENT_FUND_MAX_PERCENT = 0.15    # กองทุนสำรองเลี้ยงชีพ (15% ของเงินเดือน)
PROVIDENT_FUND_MAX = 500_000         # กองทุนสำรองเลี้ยงชีพ สูงสุด

# SSF/RMF Limits
SSF_MAX_PERCENT = 0.30               # SSF สูงสุด 30% ของรายได้
SSF_MAX_AMOUNT = 200_000             # SSF สูงสุด 200,000 บาท
RMF_MAX_PERCENT = 0.30               # RMF สูงสุด 30% ของรายได้
RMF_MAX_AMOUNT = 500_000             # RMF สูงสุด 500,000 บาท

# รวม SSF + RMF + กองทุนสำรองฯ + ประกันบำนาญ ไม่เกิน 500,000
RETIREMENT_COMBINED_MAX = 500_000


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TaxDeductions:
    """ค่าลดหย่อนทั้งหมดของผู้เสียภาษี"""
    personal: float = PERSONAL_DEDUCTION
    spouse: float = 0
    children: int = 0
    parents: int = 0
    life_insurance: float = 0
    health_insurance: float = 0
    social_security: float = 0
    provident_fund: float = 0
    ssf_current: float = 0
    rmf_current: float = 0
    other_deductions: float = 0


@dataclass
class TaxResult:
    """ผลลัพธ์การคำนวณภาษี"""
    gross_income: float              # รายได้รวม
    expense_deduction: float         # หักค่าใช้จ่าย
    total_deductions: float          # ค่าลดหย่อนรวม
    net_income: float                # เงินได้สุทธิ
    tax_before_deduction: float      # ภาษีก่อนลดหย่อน
    tax_after_deduction: float       # ภาษีหลังลดหย่อน
    effective_rate: float            # อัตราภาษีที่แท้จริง
    tax_bracket: str                 # ฐานภาษีสูงสุด
    
    
@dataclass
class SSFRMFRecommendation:
    """คำแนะนำ SSF/RMF"""
    ssf_current: float
    ssf_max_allowed: float
    ssf_recommended: float
    ssf_tax_saving: float
    
    rmf_current: float
    rmf_max_allowed: float
    rmf_recommended: float
    rmf_tax_saving: float
    
    combined_current: float
    combined_max: float
    combined_remaining: float
    
    total_tax_saving: float
    marginal_rate: float


# =============================================================================
# TAX CALCULATION FUNCTIONS
# =============================================================================

def calculate_expense_deduction(income: float, income_type: str = "salary") -> float:
    """
    คำนวณค่าใช้จ่าย (หักเหมา)
    
    Args:
        income: รายได้รวม
        income_type: ประเภทรายได้ ("salary" = เงินเดือน, "business" = ธุรกิจ, etc.)
    
    Returns:
        จำนวนเงินที่หักเป็นค่าใช้จ่าย
    """
    if income_type == "salary":
        # เงินเดือน: หักได้ 50% สูงสุด 100,000 บาท
        return min(income * 0.50, 100_000)
    elif income_type == "freelance":
        # อาชีพอิสระ: ตามประเภทงาน (ใช้ค่าเฉลี่ย 50%)
        return min(income * 0.50, 100_000)
    else:
        return min(income * 0.50, 100_000)


def calculate_total_deductions(deductions: TaxDeductions, income: float) -> float:
    """
    คำนวณค่าลดหย่อนรวมทั้งหมด
    
    Args:
        deductions: ข้อมูลค่าลดหย่อน
        income: รายได้รวม
    
    Returns:
        ค่าลดหย่อนรวม
    """
    total = deductions.personal
    
    # คู่สมรส
    total += min(deductions.spouse, SPOUSE_DEDUCTION)
    
    # บุตร (สูงสุดไม่จำกัด)
    total += deductions.children * CHILD_DEDUCTION
    
    # บิดามารดา (สูงสุด 4 คน = 120,000)
    total += min(deductions.parents, 4) * PARENT_DEDUCTION
    
    # ประกันชีวิต
    total += min(deductions.life_insurance, INSURANCE_LIFE_MAX)
    
    # ประกันสุขภาพ
    total += min(deductions.health_insurance, INSURANCE_HEALTH_MAX)
    
    # ประกันสังคม
    total += min(deductions.social_security, SOCIAL_SECURITY_MAX)
    
    # กองทุนสำรองเลี้ยงชีพ
    pf_max = min(income * PROVIDENT_FUND_MAX_PERCENT, PROVIDENT_FUND_MAX)
    total += min(deductions.provident_fund, pf_max)
    
    # SSF
    ssf_max = min(income * SSF_MAX_PERCENT, SSF_MAX_AMOUNT)
    total += min(deductions.ssf_current, ssf_max)
    
    # RMF
    rmf_max = min(income * RMF_MAX_PERCENT, RMF_MAX_AMOUNT)
    total += min(deductions.rmf_current, rmf_max)
    
    # อื่นๆ
    total += deductions.other_deductions
    
    return total


def calculate_tax(net_income: float) -> Tuple[float, str]:
    """
    คำนวณภาษีจากเงินได้สุทธิ
    
    Args:
        net_income: เงินได้สุทธิ (หลังหักค่าใช้จ่ายและค่าลดหย่อน)
    
    Returns:
        (จำนวนภาษี, ฐานภาษีสูงสุดที่ใช้)
    """
    if net_income <= 0:
        return 0, "0%"
    
    tax = 0
    remaining = net_income
    prev_bracket = 0
    current_rate = "0%"
    
    for bracket, rate in TAX_BRACKETS_2567:
        taxable = min(remaining, bracket - prev_bracket)
        if taxable > 0:
            tax += taxable * rate
            current_rate = f"{rate*100:.0f}%"
        remaining -= taxable
        prev_bracket = bracket
        if remaining <= 0:
            break
    
    return tax, current_rate


def get_marginal_rate(net_income: float) -> float:
    """
    หาอัตราภาษีส่วนเพิ่ม (Marginal Tax Rate)
    
    Args:
        net_income: เงินได้สุทธิ
    
    Returns:
        อัตราภาษีส่วนเพิ่ม (0.0 - 0.35)
    """
    prev_bracket = 0
    for bracket, rate in TAX_BRACKETS_2567:
        if net_income <= bracket:
            return rate
        prev_bracket = bracket
    return 0.35


def calculate_full_tax(
    gross_income: float,
    deductions: TaxDeductions,
    income_type: str = "salary"
) -> TaxResult:
    """
    คำนวณภาษีแบบครบถ้วน
    
    Args:
        gross_income: รายได้รวมต่อปี
        deductions: ค่าลดหย่อนต่างๆ
        income_type: ประเภทรายได้
    
    Returns:
        TaxResult พร้อมรายละเอียดทั้งหมด
    """
    # หักค่าใช้จ่าย
    expense = calculate_expense_deduction(gross_income, income_type)
    
    # หักค่าลดหย่อน
    total_deductions = calculate_total_deductions(deductions, gross_income)
    
    # เงินได้สุทธิ
    net_income = max(0, gross_income - expense - total_deductions)
    
    # คำนวณภาษี
    tax, bracket = calculate_tax(net_income)
    
    # Effective rate
    effective_rate = (tax / gross_income * 100) if gross_income > 0 else 0
    
    return TaxResult(
        gross_income=gross_income,
        expense_deduction=expense,
        total_deductions=total_deductions,
        net_income=net_income,
        tax_before_deduction=tax,
        tax_after_deduction=tax,
        effective_rate=effective_rate,
        tax_bracket=bracket
    )


# =============================================================================
# SSF/RMF OPTIMIZATION
# =============================================================================

def calculate_ssf_rmf_recommendation(
    gross_income: float,
    deductions: TaxDeductions,
    income_type: str = "salary"
) -> SSFRMFRecommendation:
    """
    คำนวณคำแนะนำ SSF/RMF ที่เหมาะสม
    
    Args:
        gross_income: รายได้รวมต่อปี
        deductions: ค่าลดหย่อนปัจจุบัน
        income_type: ประเภทรายได้
    
    Returns:
        SSFRMFRecommendation พร้อมคำแนะนำ
    """
    # คำนวณภาษีปัจจุบัน
    current_tax = calculate_full_tax(gross_income, deductions, income_type)
    marginal_rate = get_marginal_rate(current_tax.net_income)
    
    # คำนวณ limit ต่างๆ
    ssf_max_by_income = gross_income * SSF_MAX_PERCENT
    ssf_max_allowed = min(ssf_max_by_income, SSF_MAX_AMOUNT)
    ssf_current = deductions.ssf_current
    
    rmf_max_by_income = gross_income * RMF_MAX_PERCENT
    rmf_max_allowed = min(rmf_max_by_income, RMF_MAX_AMOUNT)
    rmf_current = deductions.rmf_current
    
    # รวมกองทุนเกษียณทั้งหมด
    combined_current = ssf_current + rmf_current + deductions.provident_fund
    combined_remaining = max(0, RETIREMENT_COMBINED_MAX - combined_current)
    
    # คำนวณว่าซื้อเพิ่มได้อีกเท่าไร
    ssf_can_add = min(
        ssf_max_allowed - ssf_current,
        combined_remaining
    )
    
    rmf_can_add = min(
        rmf_max_allowed - rmf_current,
        combined_remaining - ssf_can_add  # หลังหัก SSF ที่แนะนำ
    )
    
    # คำนวณภาษีที่ประหยัดได้
    ssf_tax_saving = ssf_can_add * marginal_rate
    rmf_tax_saving = rmf_can_add * marginal_rate
    total_tax_saving = ssf_tax_saving + rmf_tax_saving
    
    return SSFRMFRecommendation(
        ssf_current=ssf_current,
        ssf_max_allowed=ssf_max_allowed,
        ssf_recommended=ssf_can_add,
        ssf_tax_saving=ssf_tax_saving,
        
        rmf_current=rmf_current,
        rmf_max_allowed=rmf_max_allowed,
        rmf_recommended=rmf_can_add,
        rmf_tax_saving=rmf_tax_saving,
        
        combined_current=combined_current,
        combined_max=RETIREMENT_COMBINED_MAX,
        combined_remaining=combined_remaining,
        
        total_tax_saving=total_tax_saving,
        marginal_rate=marginal_rate
    )


def calculate_optimal_allocation(
    gross_income: float,
    provident_fund: float = 0,
    existing_ssf: float = 0,
    existing_rmf: float = 0
) -> Dict[str, float]:
    """
    คำนวณการจัดสรร SSF/RMF ที่เหมาะสมที่สุด (Simple version)
    
    Args:
        gross_income: รายได้รวมต่อปี
        provident_fund: กองทุนสำรองเลี้ยงชีพ
        existing_ssf: SSF ที่ซื้อแล้วในปีนี้
        existing_rmf: RMF ที่ซื้อแล้วในปีนี้
    
    Returns:
        Dict with optimal SSF and RMF amounts
    """
    # รวมกองทุนเกษียณที่มีอยู่
    combined_existing = provident_fund + existing_ssf + existing_rmf
    room_remaining = max(0, RETIREMENT_COMBINED_MAX - combined_existing)
    
    # SSF limit
    ssf_limit = min(gross_income * SSF_MAX_PERCENT, SSF_MAX_AMOUNT)
    ssf_can_buy = max(0, ssf_limit - existing_ssf)
    ssf_optimal = min(ssf_can_buy, room_remaining)
    
    # RMF limit (ใช้ room ที่เหลือ)
    room_after_ssf = max(0, room_remaining - ssf_optimal)
    rmf_limit = min(gross_income * RMF_MAX_PERCENT, RMF_MAX_AMOUNT)
    rmf_can_buy = max(0, rmf_limit - existing_rmf)
    rmf_optimal = min(rmf_can_buy, room_after_ssf)
    
    return {
        "ssf_optimal": ssf_optimal,
        "rmf_optimal": rmf_optimal,
        "total_optimal": ssf_optimal + rmf_optimal,
        "room_used": ssf_optimal + rmf_optimal,
        "room_remaining": room_remaining - ssf_optimal - rmf_optimal
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_thai_currency(amount: float) -> str:
    """Format number as Thai Baht"""
    return f"฿{amount:,.0f}"


def get_tax_bracket_info() -> List[Dict]:
    """Return tax bracket information for display"""
    brackets = [
        {"range": "0 - 150,000", "rate": "ยกเว้น", "rate_pct": 0},
        {"range": "150,001 - 300,000", "rate": "5%", "rate_pct": 5},
        {"range": "300,001 - 500,000", "rate": "10%", "rate_pct": 10},
        {"range": "500,001 - 750,000", "rate": "15%", "rate_pct": 15},
        {"range": "750,001 - 1,000,000", "rate": "20%", "rate_pct": 20},
        {"range": "1,000,001 - 2,000,000", "rate": "25%", "rate_pct": 25},
        {"range": "2,000,001 - 5,000,000", "rate": "30%", "rate_pct": 30},
        {"range": "มากกว่า 5,000,000", "rate": "35%", "rate_pct": 35},
    ]
    return brackets
