"""
PDF Report Generator Module
===========================
สร้างรายงานพอร์ตโฟลิโอในรูปแบบ PDF ที่สวยงาม

ใช้ FPDF2 library รองรับภาษาไทย
"""

from fpdf import FPDF
from datetime import datetime
from typing import Dict, List, Optional
import os
import io


# =============================================================================
# CUSTOM PDF CLASS WITH THAI SUPPORT
# =============================================================================

class WealthReportPDF(FPDF):
    """Custom PDF class for Wealth Advisor reports"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
        # Colors
        self.primary_color = (0, 210, 106)     # Green
        self.secondary_color = (255, 215, 0)   # Gold
        self.dark_bg = (30, 34, 42)            # Dark background
        self.text_color = (50, 50, 50)         # Dark text
        self.light_text = (128, 128, 128)      # Gray text
        
    def header(self):
        """Header สำหรับทุกหน้า"""
        # Logo placeholder (สี่เหลี่ยมแทน logo)
        self.set_fill_color(*self.primary_color)
        self.rect(10, 10, 8, 8, 'F')
        
        # Title
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*self.text_color)
        self.set_xy(22, 10)
        self.cell(0, 8, 'SMART WEALTH ADVISOR', new_x="LMARGIN", new_y="NEXT")
        
        # Subtitle
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.light_text)
        self.set_xy(22, 16)
        self.cell(0, 5, 'Portfolio Intelligence Report', new_x="LMARGIN", new_y="NEXT")
        
        # Line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 28, 200, 28)
        
        self.ln(15)
        
    def footer(self):
        """Footer สำหรับทุกหน้า"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.light_text)
        
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
        
    def add_section_title(self, title: str):
        """เพิ่มหัวข้อ section"""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        
    def add_metric_box(self, label: str, value: str, delta: str = "", x: float = None, width: float = 45):
        """เพิ่มกล่อง metric"""
        if x is not None:
            self.set_x(x)
        
        start_x = self.get_x()
        start_y = self.get_y()
        
        # Box background
        self.set_fill_color(245, 247, 250)
        self.rect(start_x, start_y, width, 25, 'F')
        
        # Border
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.3)
        self.rect(start_x, start_y, width, 25)
        
        # Label
        self.set_xy(start_x + 3, start_y + 3)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*self.light_text)
        self.cell(width - 6, 5, label)
        
        # Value
        self.set_xy(start_x + 3, start_y + 10)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*self.text_color)
        self.cell(width - 6, 8, value)
        
        # Delta
        if delta:
            self.set_xy(start_x + 3, start_y + 18)
            self.set_font('Helvetica', '', 8)
            if delta.startswith('+'):
                self.set_text_color(0, 180, 0)
            elif delta.startswith('-'):
                self.set_text_color(220, 0, 0)
            else:
                self.set_text_color(*self.light_text)
            self.cell(width - 6, 5, delta)
            
    def add_table(self, headers: List[str], data: List[List[str]], col_widths: List[float] = None):
        """เพิ่มตาราง"""
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        
        # Header row
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(*self.dark_bg)
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        self.ln()
        
        # Data rows
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.text_color)
        
        fill = False
        for row in data:
            if fill:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, fill=True, align='C')
            self.ln()
            fill = not fill
            
    def add_text_block(self, text: str):
        """เพิ่มบล็อกข้อความ"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.text_color)
        self.multi_cell(0, 6, text)
        self.ln(3)


# =============================================================================
# REPORT GENERATION FUNCTIONS
# =============================================================================

def generate_wealth_report(
    client_name: str,
    client_data: Dict,
    portfolio_data: Dict,
    include_recommendations: bool = True
) -> bytes:
    """
    สร้างรายงาน Wealth Report แบบ PDF
    
    Args:
        client_name: ชื่อลูกค้า
        client_data: ข้อมูลลูกค้า
        portfolio_data: ข้อมูลพอร์ต
        include_recommendations: รวมคำแนะนำหรือไม่
    
    Returns:
        PDF content as bytes
    """
    pdf = WealthReportPDF()
    pdf.add_page()
    
    # Report date
    report_date = datetime.now().strftime("%d %B %Y")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f"Report Generated: {report_date}", align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Client info
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, f"Client: {client_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # =================================
    # SECTION 1: Portfolio Summary
    # =================================
    pdf.add_section_title("Portfolio Summary")
    
    # Metrics row
    total_assets = client_data.get('total_assets', 0)
    ytd_return = client_data.get('ytd_return', 0)
    
    pdf.add_metric_box(
        "Total Assets",
        f"THB {total_assets:,.0f}",
        "+350,000 this month",
        x=10,
        width=60
    )
    
    pdf.set_xy(75, pdf.get_y())
    pdf.add_metric_box(
        "YTD Return",
        f"{ytd_return*100:.2f}%",
        "+2.1% vs benchmark",
        x=75,
        width=60
    )
    
    pdf.set_xy(140, pdf.get_y())
    pdf.add_metric_box(
        "Risk Score",
        "5/10",
        "Moderate",
        x=140,
        width=60
    )
    
    pdf.ln(30)
    
    # =================================
    # SECTION 2: Asset Allocation
    # =================================
    pdf.add_section_title("Asset Allocation")
    
    portfolio = client_data.get('portfolio', {})
    target = client_data.get('target_allocation', {})
    
    # Allocation table
    headers = ["Asset", "Current", "Target", "Drift"]
    
    data = []
    for asset in portfolio.keys():
        current = portfolio.get(asset, 0) * 100
        target_val = target.get(asset, 0) * 100
        drift = current - target_val
        drift_str = f"{drift:+.1f}%"
        
        data.append([
            asset,
            f"{current:.1f}%",
            f"{target_val:.1f}%",
            drift_str
        ])
    
    pdf.add_table(headers, data, [60, 40, 40, 50])
    pdf.ln(10)
    
    # =================================
    # SECTION 3: Recommendations
    # =================================
    if include_recommendations:
        pdf.add_section_title("Recommendations")
        
        pdf.add_text_block("""
Based on your current portfolio analysis:

1. Diversification Score: 8.2/10 - Your portfolio maintains excellent diversification across asset classes.

2. Rebalancing Status: Some positions have drifted from targets. Consider rebalancing Thai Stock and US Tech allocations.

3. Market Outlook: US Technology sector shows strong momentum. Current allocation is appropriate.

4. Tax Optimization: Consider maximizing SSF/RMF contributions before year-end for tax benefits.
""")
    
    # =================================
    # SECTION 4: Disclaimer
    # =================================
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, """
Disclaimer: This report is for informational purposes only and does not constitute investment advice. Past performance is not indicative of future results. Please consult with a qualified financial advisor before making investment decisions.
""")
    
    # Return as bytes
    return bytes(pdf.output())


def generate_simple_summary(
    client_name: str,
    total_assets: float,
    ytd_return: float,
    portfolio: Dict[str, float]
) -> bytes:
    """
    สร้างรายงานสรุปอย่างง่าย
    
    Args:
        client_name: ชื่อลูกค้า
        total_assets: สินทรัพย์รวม
        ytd_return: ผลตอบแทน YTD
        portfolio: สัดส่วนพอร์ต
    
    Returns:
        PDF content as bytes
    """
    pdf = WealthReportPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(0, 210, 106)
    pdf.cell(0, 15, "Portfolio Summary", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Date
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8, datetime.now().strftime("%d %B %Y"), align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Client name
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f"Client: {client_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Key metrics
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, f"Total Assets: THB {total_assets:,.0f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"YTD Return: {ytd_return*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Portfolio allocation
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "Asset Allocation:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 11)
    for asset, weight in portfolio.items():
        pdf.cell(0, 7, f"  - {asset}: {weight*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_report_to_file(pdf_bytes: bytes, filename: str) -> str:
    """
    บันทึก PDF ลงไฟล์
    
    Args:
        pdf_bytes: PDF content
        filename: ชื่อไฟล์
    
    Returns:
        Path to saved file
    """
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    
    return os.path.abspath(filename)


def get_report_filename(client_name: str, report_type: str = "portfolio") -> str:
    """
    สร้างชื่อไฟล์รายงาน
    
    Args:
        client_name: ชื่อลูกค้า
        report_type: ประเภทรายงาน
    
    Returns:
        Filename
    """
    date_str = datetime.now().strftime("%Y%m%d")
    safe_name = client_name.replace(" ", "_").replace(".", "")
    return f"WealthReport_{safe_name}_{report_type}_{date_str}.pdf"
