"""
Smart Wealth Advisor Platform (ภาษาไทย)
========================================
แดชบอร์ดที่ปรึกษาด้านการลงทุนแบบพรีเมียม สร้างด้วย Streamlit

คุณสมบัติ:
- แดชบอร์ดลูกค้าพร้อมตัวชี้วัดสำคัญ
- การปรับพอร์ตโฟลิโอด้วย Black-Litterman
- การจำลอง Monte Carlo สำหรับวางแผนเกษียณ
- ระบบปรับสมดุลพอร์ตอัจฉริยะ
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import custom modules
from data_loader import (
    get_historical_prices, 
    get_market_caps, 
    calculate_statistics,
    simulate_supabase_connection,
    format_currency,
    format_percentage
)
from algo import black_litterman, calculate_equilibrium_returns, display_allocation_comparison
from models import (
    run_monte_carlo, 
    summarize_simulation,
    calculate_drift, 
    generate_action_plan, 
    format_action_plan,
    calculate_risk_score
)
from tax_optimizer import (
    calculate_full_tax,
    calculate_ssf_rmf_recommendation,
    calculate_optimal_allocation,
    TaxDeductions,
    get_tax_bracket_info,
    format_thai_currency
)
from line_notify import (
    send_advisor_alert,
    create_panic_alert,
    test_line_notify,
    set_line_token,
    get_notify_status
)
from pdf_generator import (
    generate_wealth_report,
    generate_simple_summary,
    get_report_filename
)
from auth import (
    init_session_state,
    is_authenticated,
    get_current_user,
    login_user,
    logout_user,
    show_login_form,
    show_user_menu,
    get_menu_by_role,
    require_auth,
    require_role,
    UserRole,
    MOCK_MODE as AUTH_MOCK_MODE
)
from portfolio_service import (
    get_portfolio_service,
    Portfolio,
    TransactionType
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ที่ปรึกษาการเงินอัจฉริยะ",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication session state
init_session_state()

# Custom CSS for premium look with Thai font support
st.markdown("""
<style>
    /* Import Google Fonts - Thai */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Apply font globally */
    html, body, [class*="css"] {
        font-family: 'Noto Sans Thai', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container styling */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    
    h3 {
        font-size: 1.4rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        color: #ffffff !important;
    }
    
    /* Metric Cards - Larger and Cleaner */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e222a 0%, #292d38 100%);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(0, 210, 106, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="metric-container"] label {
        color: #9CA3AF !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.95rem !important;
    }
    
    /* Slider Styling - Much More Readable */
    .stSlider {
        padding: 1rem 0 !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #00D26A 0%, #00a854 100%) !important;
        height: 8px !important;
        border-radius: 4px !important;
    }
    
    .stSlider label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #E5E7EB !important;
        margin-bottom: 0.8rem !important;
    }
    
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #9CA3AF !important;
    }
    
    /* Number Input Styling */
    .stNumberInput label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #E5E7EB !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stNumberInput input {
        font-size: 1.2rem !important;
        padding: 0.8rem 1rem !important;
        background: #1e222a !important;
        border: 2px solid #374151 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stNumberInput input:focus {
        border-color: #00D26A !important;
        box-shadow: 0 0 0 3px rgba(0, 210, 106, 0.2) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00D26A 0%, #00a854 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
        text-transform: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 210, 106, 0.4);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #E5E7EB !important;
        background: #1e222a !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 12px !important;
        padding: 1.2rem !important;
        font-size: 1rem !important;
    }
    
    /* DataFrame/Table Styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    
    /* Markdown text */
    .stMarkdown p {
        font-size: 1rem;
        line-height: 1.7;
        color: #D1D5DB;
    }
    
    /* Section spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# AUTHENTICATION CHECK
# =============================================================================

# Show login form if not authenticated
if not is_authenticated():
    show_login_form()
    st.stop()

# Get current user
current_user = get_current_user()

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    # Logo and branding
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='
            font-size: 1.6rem; 
            margin: 0;
            background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        '>💎 ที่ปรึกษาการเงิน</h1>
        <p style='color: #888; font-size: 0.85rem; margin-top: 0.5rem;'>
            ระบบวิเคราะห์พอร์ตอัจฉริยะ
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get menu based on user role
    menu_options, menu_icons = get_menu_by_role(current_user)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0"},
            "icon": {"color": "#00D26A", "font-size": "1.1rem"},
            "nav-link": {
                "font-size": "1rem",
                "text-align": "left",
                "margin": "0.3rem 0",
                "padding": "0.8rem 1rem",
                "border-radius": "8px",
                "--hover-color": "#1a1d24",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, rgba(0, 210, 106, 0.2) 0%, rgba(255, 215, 0, 0.1) 100%)",
                "border": "1px solid rgba(0, 210, 106, 0.3)",
            },
        }
    )
    
    # User menu (logout, etc)
    show_user_menu()


# =============================================================================
# INITIALIZE DATA
# =============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and cache market data."""
    prices = get_historical_prices()
    market_caps = get_market_caps()
    expected_returns, cov_matrix = calculate_statistics(prices)
    return prices, market_caps, expected_returns, cov_matrix

# Load data
prices, market_caps, expected_returns, cov_matrix = load_data()

# Get client data based on logged-in user with portfolio service
def get_current_client_data():
    """Get client data for the currently logged-in user from portfolio service."""
    user = get_current_user()
    
    if user:
        # Get portfolio from portfolio service
        portfolio_svc = get_portfolio_service()
        portfolio = portfolio_svc.get_portfolio(user.id)
        
        if portfolio:
            return {
                'id': 1,
                'name': user.full_name,
                'email': user.email,
                'user_id': user.id,
                'total_assets': portfolio.total_value,
                'cash_balance': portfolio.cash_balance,
                'ytd_return': portfolio.ytd_return,
                'risk_score': portfolio.risk_score,
                'portfolio': portfolio.holdings if any(portfolio.holdings.values()) else {
                    'Thai Stock': 0.30,
                    'US Tech': 0.35,
                    'Gold': 0.15,
                    'Bonds': 0.20
                },
                'target_allocation': portfolio.target_allocation
            }
    
    # Fallback for not logged in
    from data_loader import simulate_supabase_connection
    db = simulate_supabase_connection()
    return db.get_client(1)

client = get_current_client_data()


# =============================================================================
# DASHBOARD PAGE (แดชบอร์ด)
# =============================================================================

if selected == "แดชบอร์ด":
    # Header
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        📊 แดชบอร์ดพอร์ตโฟลิโอ
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>ภาพรวมพอร์ตและผลการดำเนินงานแบบเรียลไทม์</p>
    """, unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 สินทรัพย์รวม",
            value=f"฿{client['total_assets']:,.0f}",
            delta="+฿350,000 เดือนนี้"
        )
    
    with col2:
        st.metric(
            label="📈 ผลตอบแทน YTD",
            value=f"{client['ytd_return']*100:.2f}%",
            delta="+2.1% เหนือเกณฑ์"
        )
    
    with col3:
        risk_score = calculate_risk_score(client['portfolio'])
        st.metric(
            label="⚠️ ระดับความเสี่ยง",
            value=f"{risk_score}/10",
            delta="ปานกลาง" if risk_score <= 6 else "สูง",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            label="📊 Sharpe Ratio",
            value="1.42",
            delta="+0.15 จากไตรมาสก่อน"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 🥧 สัดส่วนการลงทุน ปัจจุบัน vs เป้าหมาย")
        
        # Donut chart for portfolio allocation
        current_weights = list(client['portfolio'].values())
        target_weights = list(client['target_allocation'].values())
        labels_th = ["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"]
        
        fig = make_subplots(
            rows=1, cols=2, 
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            subplot_titles=("สัดส่วนปัจจุบัน", "สัดส่วนเป้าหมาย")
        )
        
        colors = ['#00D26A', '#007AFF', '#FFD700', '#FF6B6B']
        
        fig.add_trace(
            go.Pie(
                labels=labels_th,
                values=current_weights,
                hole=0.6,
                marker_colors=colors,
                textinfo='percent',
                textfont_size=14,
                hovertemplate="<b>%{label}</b><br>สัดส่วน: %{percent}<extra></extra>"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=labels_th,
                values=target_weights,
                hole=0.6,
                marker_colors=colors,
                textinfo='percent',
                textfont_size=14,
                hovertemplate="<b>%{label}</b><br>สัดส่วน: %{percent}<extra></extra>"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=380,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=13)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#fff', size=13),
            margin=dict(t=50, b=60, l=20, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown("### 📈 ผลการดำเนินงาน (1 ปี)")
        
        # Performance line chart
        if not prices.empty:
            # Normalize to starting point = 100
            normalized = (prices / prices.iloc[0]) * 100
            
            # Calculate portfolio value
            weights = np.array(list(client['portfolio'].values()))
            portfolio_perf = (normalized * weights).sum(axis=1)
            
            fig = go.Figure()
            
            # Add portfolio line
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=portfolio_perf,
                mode='lines',
                name='พอร์ตของคุณ',
                line=dict(color='#00D26A', width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 210, 106, 0.1)'
            ))
            
            # Add benchmark (equal weight)
            benchmark = normalized.mean(axis=1)
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=benchmark,
                mode='lines',
                name='ดัชนีเปรียบเทียบ',
                line=dict(color='#888', width=2, dash='dash')
            ))
            
            fig.update_layout(
                height=380,
                xaxis_title="",
                yaxis_title="มูลค่า (ฐาน = 100)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#fff', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="left",
                    x=0,
                    font=dict(size=13)
                ),
                margin=dict(t=30, b=30, l=50, r=20),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Quick Insights
    st.markdown("### 💡 ข้อมูลเชิงลึก")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🎯 **คะแนนกระจายความเสี่ยง:** 8.2/10 - พอร์ตของคุณกระจายความเสี่ยงได้ดี")
    
    with col2:
        drift_df = calculate_drift(client['portfolio'], client['target_allocation'])
        max_drift = drift_df['Drift (%)'].abs().max()
        if max_drift > 5:
            st.warning(f"⚠️ **แจ้งเตือน:** สัดส่วนเบี่ยงเบนสูงสุด {max_drift:.1f}% ควรพิจารณาปรับสมดุล")
        else:
            st.success("✅ **สถานะ:** พอร์ตอยู่ในช่วงเป้าหมาย")
    
    with col3:
        st.info("📊 **มุมมองตลาด:** หุ้นเทคโนโลยี US มีโมเมนตัมที่ดี แนะนำรักษาสัดส่วน")


# =============================================================================
# PORTFOLIO MANAGEMENT PAGE (จัดการพอร์ต)
# =============================================================================

elif selected == "จัดการพอร์ต":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        💼 จัดการพอร์ตโฟลิโอ
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        ฝากเงิน ถอนเงิน และจัดสรรการลงทุนของคุณ
    </p>
    """, unsafe_allow_html=True)
    
    # Get current user and portfolio
    user = get_current_user()
    portfolio_svc = get_portfolio_service()
    user_portfolio = portfolio_svc.get_portfolio(user.id) if user else None
    
    if not user_portfolio:
        st.error("ไม่พบข้อมูลพอร์ตโฟลิโอ กรุณาลองใหม่อีกครั้ง")
        st.stop()
    
    # Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 มูลค่ารวม",
            value=f"฿{user_portfolio.total_value:,.0f}",
            delta="ทั้งหมด"
        )
    
    with col2:
        st.metric(
            label="💵 เงินสด",
            value=f"฿{user_portfolio.cash_balance:,.0f}",
            delta="พร้อมลงทุน"
        )
    
    with col3:
        invested = user_portfolio.total_value - user_portfolio.cash_balance
        st.metric(
            label="📈 ลงทุนแล้ว",
            value=f"฿{invested:,.0f}",
            delta=f"{user_portfolio.ytd_return*100:.1f}% YTD" if user_portfolio.ytd_return else "0%"
        )
    
    with col4:
        st.metric(
            label="⚠️ ระดับความเสี่ยง",
            value=f"{user_portfolio.risk_score}/10",
            delta="ปานกลาง" if user_portfolio.risk_score <= 6 else "สูง",
            delta_color="off"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for different actions
    tab_deposit, tab_withdraw, tab_invest, tab_history = st.tabs([
        "💳 ฝากเงิน", 
        "🏧 ถอนเงิน", 
        "📊 ลงทุน",
        "📜 ประวัติ"
    ])
    
    # Deposit Tab
    with tab_deposit:
        st.markdown("### ฝากเงินเข้าพอร์ต")
        
        with st.form("deposit_form"):
            deposit_amount = st.number_input(
                "จำนวนเงิน (บาท)",
                min_value=0.0,
                max_value=100000000.0,
                value=100000.0,
                step=10000.0,
                format="%.2f"
            )
            deposit_desc = st.text_input("หมายเหตุ (ไม่บังคับ)", value="ฝากเงิน")
            
            if st.form_submit_button("ฝากเงิน", type="primary", use_container_width=True):
                if deposit_amount > 0:
                    success, msg = portfolio_svc.deposit(user.id, deposit_amount, deposit_desc)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("กรุณาระบุจำนวนเงินที่มากกว่า 0")
    
    # Withdraw Tab
    with tab_withdraw:
        st.markdown("### ถอนเงินจากพอร์ต")
        st.info(f"💵 ยอดเงินสดคงเหลือ: **฿{user_portfolio.cash_balance:,.2f}**")
        
        with st.form("withdraw_form"):
            withdraw_amount = st.number_input(
                "จำนวนเงิน (บาท)",
                min_value=0.0,
                max_value=max(0.0, float(user_portfolio.cash_balance)),
                value=min(50000.0, float(user_portfolio.cash_balance)),
                step=10000.0,
                format="%.2f"
            )
            withdraw_desc = st.text_input("หมายเหตุ (ไม่บังคับ)", value="ถอนเงิน", key="wd_desc")
            
            if st.form_submit_button("ถอนเงิน", type="primary", use_container_width=True):
                if withdraw_amount > 0:
                    success, msg = portfolio_svc.withdraw(user.id, withdraw_amount, withdraw_desc)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("กรุณาระบุจำนวนเงินที่มากกว่า 0")
    
    # Invest Tab
    with tab_invest:
        st.markdown("### ลงทุนตามสัดส่วน")
        
        if user_portfolio.cash_balance <= 0:
            st.warning("⚠️ ไม่มียอดเงินสดสำหรับลงทุน กรุณาฝากเงินก่อน")
        else:
            st.info(f"💵 เงินสดพร้อมลงทุน: **฿{user_portfolio.cash_balance:,.2f}**")
            
            st.markdown("#### เลือกสัดส่วนการลงทุน")
            
            # Allocation sliders
            col1, col2 = st.columns(2)
            
            with col1:
                thai_alloc = st.slider("🇹🇭 หุ้นไทย", 0, 100, 25, 5, format="%d%%", key="thai_alloc")
                us_alloc = st.slider("🇺🇸 หุ้นเทคโนโลยี US", 0, 100, 35, 5, format="%d%%", key="us_alloc")
            
            with col2:
                gold_alloc = st.slider("🪙 ทองคำ", 0, 100, 20, 5, format="%d%%", key="gold_alloc")
                bonds_alloc = st.slider("📜 พันธบัตร", 0, 100, 20, 5, format="%d%%", key="bonds_alloc")
            
            total_alloc = thai_alloc + us_alloc + gold_alloc + bonds_alloc
            
            if total_alloc != 100:
                st.warning(f"⚠️ สัดส่วนรวม: **{total_alloc}%** (ต้องเท่ากับ 100%)")
            else:
                st.success(f"✅ สัดส่วนรวม: **{total_alloc}%**")
                
                # Preview allocation
                alloc_preview = {
                    "Thai Stock": f"฿{user_portfolio.cash_balance * thai_alloc / 100:,.0f}",
                    "US Tech": f"฿{user_portfolio.cash_balance * us_alloc / 100:,.0f}",
                    "Gold": f"฿{user_portfolio.cash_balance * gold_alloc / 100:,.0f}",
                    "Bonds": f"฿{user_portfolio.cash_balance * bonds_alloc / 100:,.0f}"
                }
                st.markdown("**ตัวอย่างการจัดสรร:**")
                st.json(alloc_preview)
                
                if st.button("ยืนยันลงทุน", type="primary", use_container_width=True):
                    allocation = {
                        "Thai Stock": thai_alloc / 100,
                        "US Tech": us_alloc / 100,
                        "Gold": gold_alloc / 100,
                        "Bonds": bonds_alloc / 100
                    }
                    success, msg = portfolio_svc.invest(user.id, allocation)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    
    # Transaction History Tab
    with tab_history:
        st.markdown("### ประวัติธุรกรรม")
        
        transactions = portfolio_svc.get_transactions(user.id, limit=20)
        
        if not transactions:
            st.info("ยังไม่มีประวัติธุรกรรม")
        else:
            # Create table data
            tx_data = []
            for tx in transactions:
                tx_type_th = {
                    TransactionType.DEPOSIT: "💳 ฝากเงิน",
                    TransactionType.WITHDRAW: "🏧 ถอนเงิน",
                    TransactionType.BUY: "📈 ซื้อ",
                    TransactionType.SELL: "📉 ขาย",
                    TransactionType.REBALANCE: "⚖️ ปรับสมดุล"
                }
                tx_data.append({
                    "วันที่": tx.created_at.strftime("%Y-%m-%d %H:%M") if tx.created_at else "-",
                    "ประเภท": tx_type_th.get(tx.type, str(tx.type)),
                    "จำนวน": f"฿{tx.amount:,.2f}",
                    "รายละเอียด": tx.description or "-"
                })
            
            st.dataframe(tx_data, use_container_width=True, hide_index=True)


# =============================================================================
# BLACK-LITTERMAN PAGE
# =============================================================================

elif selected == "Black-Litterman":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🧠 Black-Litterman Optimizer
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        ผสานมุมมองตลาดกับความคิดเห็นของคุณเพื่อหาสัดส่วนที่เหมาะสม
    </p>
    """, unsafe_allow_html=True)
    
    # Explanation card
    with st.expander("ℹ️ Black-Litterman ทำงานอย่างไร?", expanded=False):
        st.markdown("""
        **โมเดล Black-Litterman** เป็นเทคนิคการปรับพอร์ตขั้นสูงที่:
        
        1. **เริ่มจากจุดสมดุลตลาด** - ใช้สัดส่วนตามมูลค่าตลาดเป็นฐาน
        2. **รับมุมมองของคุณ** - ให้คุณแสดงความคาดหวังต่อสินทรัพย์แต่ละตัว
        3. **สร้างผลตอบแทนปรับปรุง** - รวมจุดสมดุลกับมุมมองโดยใช้สถิติ Bayesian
        4. **หาสัดส่วนที่เหมาะสม** - หาน้ำหนักที่เพิ่มผลตอบแทนต่อความเสี่ยงสูงสุด
        
        วิธีนี้หลีกเลี่ยงการจัดสรรแบบสุดโต่งที่มักเกิดจาก Mean-Variance Optimization แบบดั้งเดิม
        """)
    
    st.markdown("### 🎯 ใส่มุมมองการลงทุนของคุณ")
    st.markdown("*ปรับ slider เพื่อระบุผลตอบแทนส่วนเกินที่คาดหวังสำหรับแต่ละสินทรัพย์*")
    
    # View input sliders
    views = {}
    confidences = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### มุมมองต่อสินทรัพย์ (ผลตอบแทนส่วนเกินที่คาดหวัง)")
        
        thai_view = st.slider(
            "🇹🇭 หุ้นไทย",
            min_value=-10.0, max_value=10.0, value=0.0, step=0.5,
            format="%.1f%%",
            help="ผลตอบแทนส่วนเกินที่คุณคาดหวังเทียบกับจุดสมดุล"
        )
        if thai_view != 0:
            views["Thai Stock"] = thai_view / 100
        
        us_view = st.slider(
            "🇺🇸 หุ้นเทคโนโลยี US",
            min_value=-10.0, max_value=10.0, value=5.0, step=0.5,
            format="%.1f%%"
        )
        if us_view != 0:
            views["US Tech"] = us_view / 100
        
        gold_view = st.slider(
            "🪙 ทองคำ",
            min_value=-10.0, max_value=10.0, value=0.0, step=0.5,
            format="%.1f%%"
        )
        if gold_view != 0:
            views["Gold"] = gold_view / 100
        
        bonds_view = st.slider(
            "📜 พันธบัตร",
            min_value=-10.0, max_value=10.0, value=0.0, step=0.5,
            format="%.1f%%"
        )
        if bonds_view != 0:
            views["Bonds"] = bonds_view / 100
    
    with col2:
        st.markdown("#### ระดับความมั่นใจ (คุณมั่นใจแค่ไหน?)")
        
        asset_names_th = {"Thai Stock": "หุ้นไทย", "US Tech": "หุ้นเทคโนโลยี US", "Gold": "ทองคำ", "Bonds": "พันธบัตร"}
        
        for asset in ["Thai Stock", "US Tech", "Gold", "Bonds"]:
            if asset in views:
                conf = st.slider(
                    f"ความมั่นใจใน{asset_names_th[asset]}",
                    min_value=0.1, max_value=1.0, value=0.5, step=0.1,
                    key=f"conf_{asset}",
                    help="1.0 = มั่นใจมาก, 0.1 = ไม่แน่ใจ"
                )
                confidences[asset] = conf
    
    st.markdown("---")
    
    # Advanced settings
    with st.expander("⚙️ ตั้งค่าขั้นสูง"):
        col1, col2 = st.columns(2)
        with col1:
            tau = st.slider(
                "Tau (ความไม่แน่นอนในจุดสมดุล)",
                min_value=0.01, max_value=0.20, value=0.05, step=0.01,
                help="ค่าต่ำ = เชื่อถือจุดสมดุลตลาดมากขึ้น"
            )
        with col2:
            risk_aversion = st.slider(
                "ค่าสัมประสิทธิ์ความเสี่ยง",
                min_value=1.0, max_value=5.0, value=2.5, step=0.5,
                help="ค่าสูง = การจัดสรรอนุรักษ์นิยมมากขึ้น"
            )
    
    # Calculate and display results
    if st.button("🚀 คำนวณสัดส่วนที่เหมาะสม", type="primary"):
        with st.spinner("กำลังประมวลผล Black-Litterman..."):
            # Get equilibrium returns
            equilibrium = calculate_equilibrium_returns(cov_matrix, market_caps, risk_aversion)
            
            # Run Black-Litterman
            bl_returns, optimal_weights = black_litterman(
                cov_matrix=cov_matrix,
                market_weights=market_caps,
                views=views if views else {},
                view_confidences=confidences if confidences else None,
                tau=tau,
                risk_aversion=risk_aversion
            )
            
            st.markdown("### 📊 ผลลัพธ์การปรับพอร์ต")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### เปรียบเทียบผลตอบแทนที่คาดหวัง")
                
                returns_df = pd.DataFrame({
                    "สินทรัพย์": ["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"],
                    "จุดสมดุล (%)": (equilibrium.values * 100).round(2),
                    "BL ปรับปรุง (%)": (bl_returns.values * 100).round(2)
                })
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=returns_df["สินทรัพย์"],
                    y=returns_df["จุดสมดุล (%)"],
                    name="จุดสมดุลตลาด",
                    marker_color='#666'
                ))
                
                fig.add_trace(go.Bar(
                    x=returns_df["สินทรัพย์"],
                    y=returns_df["BL ปรับปรุง (%)"],
                    name="BL ปรับปรุง",
                    marker_color='#00D26A'
                ))
                
                fig.update_layout(
                    height=320,
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#fff', size=12),
                    yaxis_title="ผลตอบแทนที่คาดหวัง (%)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=12)),
                    margin=dict(t=50, b=30)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### สัดส่วนที่แนะนำ")
                
                fig = go.Figure(go.Pie(
                    labels=["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"],
                    values=optimal_weights.values,
                    hole=0.6,
                    marker_colors=['#00D26A', '#007AFF', '#FFD700', '#FF6B6B'],
                    textinfo='label+percent',
                    textfont_size=13
                ))
                
                fig.update_layout(
                    height=320,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#fff', size=12),
                    margin=dict(t=20, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Comparison table
            st.markdown("#### ตารางเปรียบเทียบ")
            comparison = display_allocation_comparison(market_caps, optimal_weights)
            comparison.columns = ["สินทรัพย์", "น้ำหนักตลาด", "น้ำหนัก BL", "ส่วนต่าง"]
            comparison["สินทรัพย์"] = ["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"]
            comparison["น้ำหนักตลาด"] = (comparison["น้ำหนักตลาด"] * 100).round(1).astype(str) + "%"
            comparison["น้ำหนัก BL"] = (comparison["น้ำหนัก BL"] * 100).round(1).astype(str) + "%"
            comparison["ส่วนต่าง"] = (comparison["ส่วนต่าง"] * 100).round(1).astype(str) + "%"
            
            st.dataframe(comparison, use_container_width=True, hide_index=True)


# =============================================================================
# MONTE CARLO PAGE
# =============================================================================

elif selected == "Monte Carlo":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🎲 เครื่องจำลอง Monte Carlo
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        จำลองสถานการณ์ตลาดนับพันเพื่อวางแผนเกษียณอายุ
    </p>
    """, unsafe_allow_html=True)
    
    # Input parameters
    st.markdown("### 📝 พารามิเตอร์การจำลอง")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_wealth = st.number_input(
            "💰 เงินปัจจุบัน (บาท)",
            min_value=100000,
            max_value=100000000,
            value=client['total_assets'],
            step=100000,
            format="%d"
        )
    
    with col2:
        monthly_contribution = st.number_input(
            "📥 เงินออมต่อเดือน (บาท)",
            min_value=0,
            max_value=1000000,
            value=50000,
            step=5000,
            format="%d"
        )
    
    with col3:
        years_to_retire = st.number_input(
            "📅 จำนวนปีถึงเกษียณ",
            min_value=1,
            max_value=50,
            value=20,
            step=1
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        annual_return = st.slider(
            "📈 ผลตอบแทนรายปีที่คาดหวัง (%)",
            min_value=3.0, max_value=15.0, value=7.0, step=0.5
        ) / 100
    
    with col2:
        annual_volatility = st.slider(
            "📉 ความผันผวนรายปี (%)",
            min_value=5.0, max_value=30.0, value=15.0, step=1.0
        ) / 100
    
    with col3:
        goal_amount = st.number_input(
            "🎯 เป้าหมายเงินเกษียณ (บาท)",
            min_value=1000000,
            max_value=500000000,
            value=30000000,
            step=1000000,
            format="%d"
        )
    
    st.markdown("---")
    
    if st.button("🎲 รันจำลอง 1,000 ครั้ง", type="primary"):
        with st.spinner("กำลังจำลอง Monte Carlo..."):
            # Run simulation
            result = run_monte_carlo(
                current_wealth=current_wealth,
                monthly_contribution=monthly_contribution,
                years_to_retire=years_to_retire,
                annual_return=annual_return,
                annual_volatility=annual_volatility,
                n_simulations=1000,
                goal_amount=goal_amount
            )
            
            # Summary metrics
            st.markdown("### 📊 ผลลัพธ์การจำลอง")
            
            col1, col2, col3, col4 = st.columns(4)
            
            summary = summarize_simulation(result)
            
            with col1:
                st.metric(
                    "💵 มูลค่ามัธยฐาน",
                    f"฿{summary['Median Final Value']:,.0f}",
                    f"หลังจาก {years_to_retire} ปี"
                )
            
            with col2:
                st.metric(
                    "📉 กรณีเลวร้าย (10%)",
                    f"฿{summary['10th Percentile']:,.0f}",
                    "ประมาณการอนุรักษ์นิยม"
                )
            
            with col3:
                st.metric(
                    "📈 กรณีดีที่สุด (90%)",
                    f"฿{summary['90th Percentile']:,.0f}",
                    "ประมาณการมองบวก"
                )
            
            with col4:
                prob = result.probability_of_success * 100
                st.metric(
                    "🎯 โอกาสสำเร็จ",
                    f"{prob:.1f}%",
                    "เหนือเป้าหมาย" if prob >= 70 else "ต่ำกว่าเป้าหมาย",
                    delta_color="normal" if prob >= 70 else "inverse"
                )
            
            # Projection chart
            st.markdown("### 📈 การคาดการณ์มูลค่าพอร์ต (Percentile 10 / 50 / 90)")
            
            fig = go.Figure()
            
            # Add percentile bands
            fig.add_trace(go.Scatter(
                x=result.years,
                y=result.percentile_90,
                mode='lines',
                name='กรณีดีที่สุด (Percentile 90)',
                line=dict(color='#00D26A', width=1, dash='dot'),
                fill=None
            ))
            
            fig.add_trace(go.Scatter(
                x=result.years,
                y=result.percentile_10,
                mode='lines',
                name='กรณีเลวร้าย (Percentile 10)',
                line=dict(color='#FF6B6B', width=1, dash='dot'),
                fill='tonexty',
                fillcolor='rgba(0, 210, 106, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=result.years,
                y=result.percentile_50,
                mode='lines',
                name='กรณีฐาน (Percentile 50)',
                line=dict(color='#FFD700', width=3)
            ))
            
            # Add goal line
            fig.add_hline(
                y=goal_amount, 
                line_dash="dash", 
                line_color="#888",
                annotation_text=f"เป้าหมาย: ฿{goal_amount:,.0f}",
                annotation_position="right"
            )
            
            fig.update_layout(
                height=450,
                xaxis_title="ปี",
                yaxis_title="มูลค่าพอร์ต (บาท)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#fff', size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12)
                ),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickformat=',.0f'),
                margin=dict(t=50, b=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribution of final values
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 การกระจายมูลค่าสุดท้าย")
                
                fig = go.Figure()
                
                fig.add_trace(go.Histogram(
                    x=result.final_values,
                    nbinsx=50,
                    marker_color='#00D26A',
                    opacity=0.7
                ))
                
                fig.add_vline(
                    x=goal_amount,
                    line_dash="dash",
                    line_color="#FFD700",
                    annotation_text="เป้าหมาย"
                )
                
                fig.update_layout(
                    height=300,
                    xaxis_title="มูลค่าพอร์ตสุดท้าย (บาท)",
                    yaxis_title="ความถี่",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#fff', size=12),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickformat=',.0f'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    margin=dict(t=20, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 💡 ข้อมูลสำคัญ")
                
                total_contribution = current_wealth + (monthly_contribution * 12 * years_to_retire)
                median_gain = summary['Median Final Value'] - total_contribution
                
                st.success(f"""
                **เงินลงทุนรวม:** ฿{total_contribution:,.0f}  
                **มูลค่ามัธยฐาน:** ฿{summary['Median Final Value']:,.0f}  
                **กำไรที่คาดหวัง:** ฿{median_gain:,.0f} ({median_gain/total_contribution*100:.1f}%)
                """)
                
                if prob >= 80:
                    st.info("✅ **ความมั่นใจสูง:** คุณมีโอกาสสำเร็จตามเป้าหมายสูงมาก!")
                elif prob >= 60:
                    st.warning("⚠️ **ความมั่นใจปานกลาง:** ควรพิจารณาเพิ่มเงินออมหรือขยายระยะเวลา")
                else:
                    st.error("❌ **ความมั่นใจต่ำ:** คุณอาจต้องปรับแผนอย่างมาก")


# =============================================================================
# REBALANCING PAGE (ปรับสมดุล)
# =============================================================================

elif selected == "ปรับสมดุล":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        ⚖️ ระบบปรับสมดุลอัจฉริยะ
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        ติดตามการเบี่ยงเบนสัดส่วน และรับคำแนะนำการซื้อขาย
    </p>
    """, unsafe_allow_html=True)
    
    # Current portfolio summary
    st.markdown("### 📊 สถานะสัดส่วนปัจจุบัน")
    
    # Calculate drift
    drift_df = calculate_drift(client['portfolio'], client['target_allocation'])
    
    # Visual drift indicator
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Drift bar chart
        fig = go.Figure()
        
        colors = ['#FF6B6B' if x > 0 else '#00D26A' for x in drift_df['Drift (%)']]
        
        asset_labels_th = ["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"]
        
        fig.add_trace(go.Bar(
            x=asset_labels_th,
            y=drift_df['Drift (%)'],
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in drift_df['Drift (%)']],
            textposition='outside',
            textfont=dict(size=14)
        ))
        
        # Add threshold lines
        fig.add_hline(y=5, line_dash="dash", line_color="#FFD700", 
                      annotation_text="เกณฑ์ปรับสมดุล (+5%)")
        fig.add_hline(y=-5, line_dash="dash", line_color="#FFD700",
                      annotation_text="เกณฑ์ปรับสมดุล (-5%)")
        
        fig.update_layout(
            height=380,
            xaxis_title="",
            yaxis_title="การเบี่ยงเบน (%)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#fff', size=13),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[-15, 15]),
            margin=dict(t=30, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📖 คำอธิบาย")
        st.markdown("""
        - 🔴 **เกินสัดส่วน:** ต้องขาย
        - 🟢 **ต่ำกว่าสัดส่วน:** ต้องซื้อ
        - ⚡ **เกณฑ์:** ±5% จะเรียกการปรับสมดุล
        """)
        
        # Summary stats
        max_over = drift_df['Drift (%)'].max()
        max_under = drift_df['Drift (%)'].min()
        
        st.metric("เกินสัดส่วนสูงสุด", f"{max_over:+.1f}%")
        st.metric("ต่ำกว่าสัดส่วนสูงสุด", f"{max_under:+.1f}%")
    
    st.markdown("---")
    
    # Drift table
    st.markdown("### 📋 รายละเอียดการเบี่ยงเบน")
    
    drift_df_th = drift_df.copy()
    drift_df_th['Asset'] = ["หุ้นไทย", "หุ้นเทคโนโลยี US", "ทองคำ", "พันธบัตร"]
    drift_df_th.columns = ['สินทรัพย์', 'ปัจจุบัน (%)', 'เป้าหมาย (%)', 'เบี่ยงเบน (%)', 'สถานะ']
    drift_df_th['สถานะ'] = drift_df_th['สถานะ'].replace({
        '🔴 Rebalance Needed': '🔴 ต้องปรับสมดุล',
        '🟡 Monitor': '🟡 ควรติดตาม',
        '🟢 On Target': '🟢 ตามเป้าหมาย'
    })
    
    st.dataframe(drift_df_th, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Action Plan
    st.markdown("### 🎯 แผนการดำเนินการที่แนะนำ")
    
    # Drift threshold setting
    threshold = st.slider(
        "เกณฑ์การปรับสมดุล (%)",
        min_value=1.0, max_value=10.0, value=5.0, step=0.5,
        help="สร้างคำสั่งซื้อขายเฉพาะสินทรัพย์ที่เบี่ยงเบนเกินเกณฑ์นี้"
    ) / 100
    
    # Generate and display action plan
    actions = generate_action_plan(
        current_weights=client['portfolio'],
        target_weights=client['target_allocation'],
        portfolio_value=client['total_assets'],
        drift_threshold=threshold
    )
    
    if actions:
        # Create Thai action plan table
        action_data = []
        for action in actions:
            asset_th = {"Thai Stock": "หุ้นไทย", "US Tech": "หุ้นเทคโนโลยี US", "Gold": "ทองคำ", "Bonds": "พันธบัตร"}
            action_data.append({
                "การดำเนินการ": f"{'🔻 ขาย' if action.action == 'SELL' else '🔺 ซื้อ'}",
                "สินทรัพย์": asset_th.get(action.asset, action.asset),
                "จำนวนหน่วย": f"{action.trade_units:,}",
                "มูลค่า": f"฿{action.trade_amount:,.0f}",
                "ปัจจุบัน → เป้าหมาย": f"{action.current_weight*100:.1f}% → {action.target_weight*100:.1f}%"
            })
        
        action_df = pd.DataFrame(action_data)
        st.dataframe(action_df, use_container_width=True, hide_index=True)
        
        # Summary
        total_trades = sum(a.trade_amount for a in actions)
        st.info(f"💰 **มูลค่าการซื้อขายรวม:** ฿{total_trades:,.0f}")
        
        # Execution button (simulated)
        if st.button("✅ ดำเนินการปรับสมดุล", type="primary"):
            st.success("🎉 คำสั่งปรับสมดุลถูกส่งไปดำเนินการแล้ว!")
            st.balloons()
    else:
        st.success("✅ **ไม่ต้องปรับสมดุล** - พอร์ตของคุณอยู่ในสัดส่วนเป้าหมายแล้ว!")


# =============================================================================
# TAX OPTIMIZER PAGE (วางแผนภาษี)
# =============================================================================

elif selected == "วางแผนภาษี":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🧮 วางแผนภาษีและ SSF/RMF
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        คำนวณภาษีตามอัตรา 2567 และแนะนำการลงทุน SSF/RMF ที่เหมาะสม
    </p>
    """, unsafe_allow_html=True)
    
    # Tax bracket info
    with st.expander("📊 อัตราภาษีเงินได้บุคคลธรรมดา 2567", expanded=False):
        brackets = get_tax_bracket_info()
        bracket_df = pd.DataFrame(brackets)
        bracket_df.columns = ["เงินได้สุทธิ (บาท)", "อัตราภาษี", "อัตรา (%)"]
        st.dataframe(bracket_df, use_container_width=True, hide_index=True)
    
    st.markdown("### 📝 กรอกข้อมูลรายได้")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gross_income = st.number_input(
            "💵 รายได้รวมต่อปี (บาท)",
            min_value=0,
            max_value=100_000_000,
            value=1_200_000,
            step=100_000,
            format="%d",
            help="รายได้รวมก่อนหักค่าใช้จ่ายและลดหย่อน"
        )
        
        marital_status = st.selectbox(
            "👫 สถานะสมรส",
            options=["โสด", "สมรส (คู่สมรสไม่มีรายได้)", "สมรส (คู่สมรสมีรายได้)"],
            index=0
        )
        
        num_children = st.number_input(
            "👶 จำนวนบุตร",
            min_value=0,
            max_value=10,
            value=0,
            step=1
        )
        
        num_parents = st.number_input(
            "👴 จำนวนบิดามารดาที่เลี้ยงดู (สูงสุด 4)",
            min_value=0,
            max_value=4,
            value=0,
            step=1
        )
    
    with col2:
        life_insurance = st.number_input(
            "🛡️ เบี้ยประกันชีวิต (บาท)",
            min_value=0,
            max_value=100_000,
            value=0,
            step=10_000,
            help="สูงสุด 100,000 บาท"
        )
        
        health_insurance = st.number_input(
            "🏥 เบี้ยประกันสุขภาพ (บาท)",
            min_value=0,
            max_value=25_000,
            value=0,
            step=5_000,
            help="สูงสุด 25,000 บาท"
        )
        
        social_security = st.number_input(
            "📋 เงินสมทบประกันสังคม (บาท)",
            min_value=0,
            max_value=9_000,
            value=9_000,
            step=1_000,
            help="สูงสุด 9,000 บาท"
        )
        
        provident_fund = st.number_input(
            "🏦 กองทุนสำรองเลี้ยงชีพ (บาท)",
            min_value=0,
            max_value=500_000,
            value=0,
            step=10_000,
            help="สูงสุด 15% ของเงินเดือน หรือ 500,000 บาท"
        )
    
    st.markdown("---")
    st.markdown("### 📈 SSF/RMF ที่ซื้อแล้วในปีนี้")
    
    col1, col2 = st.columns(2)
    
    with col1:
        existing_ssf = st.number_input(
            "📊 SSF ที่ซื้อแล้ว (บาท)",
            min_value=0,
            max_value=200_000,
            value=0,
            step=10_000,
            help="Super Savings Fund - สูงสุด 30% ของรายได้ หรือ 200,000 บาท"
        )
    
    with col2:
        existing_rmf = st.number_input(
            "📈 RMF ที่ซื้อแล้ว (บาท)",
            min_value=0,
            max_value=500_000,
            value=0,
            step=10_000,
            help="Retirement Mutual Fund - สูงสุด 30% ของรายได้ หรือ 500,000 บาท"
        )
    
    st.markdown("---")
    
    if st.button("🧮 คำนวณภาษีและคำแนะนำ", type="primary"):
        # Create deductions object
        deductions = TaxDeductions(
            spouse=60_000 if "ไม่มีรายได้" in marital_status else 0,
            children=num_children,
            parents=num_parents,
            life_insurance=life_insurance,
            health_insurance=health_insurance,
            social_security=social_security,
            provident_fund=provident_fund,
            ssf_current=existing_ssf,
            rmf_current=existing_rmf
        )
        
        # Calculate tax
        tax_result = calculate_full_tax(gross_income, deductions)
        
        # Calculate SSF/RMF recommendation
        recommendation = calculate_ssf_rmf_recommendation(gross_income, deductions)
        
        # Display results
        st.markdown("### 📊 ผลการคำนวณภาษี")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 เงินได้สุทธิ",
                f"฿{tax_result.net_income:,.0f}",
                f"ฐาน {tax_result.tax_bracket}"
            )
        
        with col2:
            st.metric(
                "📋 ภาษีที่ต้องจ่าย",
                f"฿{tax_result.tax_after_deduction:,.0f}",
                f"อัตราที่แท้จริง {tax_result.effective_rate:.2f}%"
            )
        
        with col3:
            st.metric(
                "🎯 Marginal Rate",
                f"{recommendation.marginal_rate*100:.0f}%",
                "อัตราภาษีส่วนเพิ่ม"
            )
        
        with col4:
            st.metric(
                "💵 ค่าลดหย่อนรวม",
                f"฿{tax_result.total_deductions:,.0f}",
                "รวมทุกรายการ"
            )
        
        st.markdown("---")
        st.markdown("### 🎯 คำแนะนำ SSF/RMF")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 SSF (Super Savings Fund)")
            
            ssf_progress = existing_ssf / recommendation.ssf_max_allowed * 100 if recommendation.ssf_max_allowed > 0 else 0
            st.progress(min(ssf_progress / 100, 1.0))
            
            st.markdown(f"""
            - **ซื้อแล้ว:** ฿{existing_ssf:,.0f}
            - **ซื้อได้สูงสุด:** ฿{recommendation.ssf_max_allowed:,.0f}
            - **แนะนำซื้อเพิ่ม:** 🟢 **฿{recommendation.ssf_recommended:,.0f}**
            - **ประหยัดภาษีได้:** ฿{recommendation.ssf_tax_saving:,.0f}
            """)
        
        with col2:
            st.markdown("#### 📈 RMF (Retirement Mutual Fund)")
            
            rmf_progress = existing_rmf / recommendation.rmf_max_allowed * 100 if recommendation.rmf_max_allowed > 0 else 0
            st.progress(min(rmf_progress / 100, 1.0))
            
            st.markdown(f"""
            - **ซื้อแล้ว:** ฿{existing_rmf:,.0f}
            - **ซื้อได้สูงสุด:** ฿{recommendation.rmf_max_allowed:,.0f}
            - **แนะนำซื้อเพิ่ม:** 🟢 **฿{recommendation.rmf_recommended:,.0f}**
            - **ประหยัดภาษีได้:** ฿{recommendation.rmf_tax_saving:,.0f}
            """)
        
        # Summary box
        st.markdown("---")
        
        if recommendation.total_tax_saving > 0:
            st.success(f"""
            ### 💰 สรุป: ถ้าซื้อ SSF/RMF ตามคำแนะนำ
            
            - **SSF ซื้อเพิ่ม:** ฿{recommendation.ssf_recommended:,.0f}
            - **RMF ซื้อเพิ่ม:** ฿{recommendation.rmf_recommended:,.0f}
            - **รวมลงทุนเพิ่ม:** ฿{recommendation.ssf_recommended + recommendation.rmf_recommended:,.0f}
            - **ประหยัดภาษีรวม:** 🎉 **฿{recommendation.total_tax_saving:,.0f}**
            
            📌 *กองทุนเกษียณรวม (SSF + RMF + กองทุนสำรองฯ) ใช้แล้ว ฿{recommendation.combined_current:,.0f} / ฿{recommendation.combined_max:,.0f}*
            """)
        else:
            st.info("✅ คุณใช้สิทธิลดหย่อน SSF/RMF เต็มที่แล้ว!")
        
        st.warning("⚠️ **ข้อมูลนี้เป็นการประมาณการเท่านั้น** กรุณาปรึกษาผู้เชี่ยวชาญด้านภาษีก่อนตัดสินใจ")


# =============================================================================
# PDF REPORT PAGE (รายงาน PDF)
# =============================================================================

elif selected == "รายงาน PDF":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        📄 สร้างรายงาน PDF
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        ดาวน์โหลดรายงานสรุปพอร์ตโฟลิโอในรูปแบบ PDF
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 เลือกประเภทรายงาน")
    
    report_type = st.radio(
        "เลือกรายงาน:",
        options=["รายงานสรุปพอร์ต", "รายงานฉบับเต็ม"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Preview section
    st.markdown("### 👁️ ตัวอย่างข้อมูลในรายงาน")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 ข้อมูลลูกค้า")
        st.markdown(f"""
        - **ชื่อ:** {client['name']}
        - **สินทรัพย์รวม:** ฿{client['total_assets']:,.0f}
        - **ผลตอบแทน YTD:** {client['ytd_return']*100:.2f}%
        - **วันที่รายงาน:** {pd.Timestamp.now().strftime('%d/%m/%Y')}
        """)
    
    with col2:
        st.markdown("#### 🥧 สัดส่วนพอร์ต")
        for asset, weight in client['portfolio'].items():
            asset_th = {"Thai Stock": "หุ้นไทย", "US Tech": "หุ้นเทคโนโลยี US", "Gold": "ทองคำ", "Bonds": "พันธบัตร"}
            st.markdown(f"- **{asset_th.get(asset, asset)}:** {weight*100:.1f}%")
    
    st.markdown("---")
    
    # Generate button
    if st.button("📥 สร้างและดาวน์โหลด PDF", type="primary"):
        with st.spinner("กำลังสร้างรายงาน PDF..."):
            # Generate PDF
            if report_type == "รายงานสรุปพอร์ต":
                pdf_bytes = generate_simple_summary(
                    client_name=client['name'],
                    total_assets=client['total_assets'],
                    ytd_return=client['ytd_return'],
                    portfolio=client['portfolio']
                )
            else:
                pdf_bytes = generate_wealth_report(
                    client_name=client['name'],
                    client_data=client,
                    portfolio_data=client['portfolio'],
                    include_recommendations=True
                )
            
            # Create download button
            filename = get_report_filename(client['name'], "portfolio")
            
            st.download_button(
                label="📄 ดาวน์โหลด PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="secondary"
            )
            
            st.success("✅ รายงาน PDF พร้อมดาวน์โหลดแล้ว!")
    
    # Info box
    st.info("""
    💡 **เคล็ดลับ:**
    - รายงานสรุปพอร์ต: 1 หน้า สำหรับดูภาพรวม
    - รายงานฉบับเต็ม: หลายหน้า รวมคำแนะนำและการวิเคราะห์
    """)


# =============================================================================
# ADVISOR CONTACT PAGE (ติดต่อที่ปรึกษา)
# =============================================================================

elif selected == "ติดต่อที่ปรึกษา":
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        📞 ติดต่อที่ปรึกษา
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        ขอคำปรึกษาจากผู้เชี่ยวชาญเมื่อต้องการความช่วยเหลือ
    </p>
    """, unsafe_allow_html=True)
    
    # Check portfolio status
    daily_change = -150000  # Simulated daily change
    daily_change_pct = (daily_change / client['total_assets']) * 100
    
    # Alert section if portfolio is down
    if daily_change < 0:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 107, 107, 0.1) 100%);
            border: 1px solid rgba(255, 107, 107, 0.5);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        '>
            <h3 style='color: #FF6B6B; margin: 0;'>⚠️ พอร์ตของคุณปรับลดลงวันนี้</h3>
            <p style='color: #FF9999; margin: 0.5rem 0 0 0;'>
                ไม่ต้องกังวล! ที่ปรึกษาของเราพร้อมช่วยเหลือคุณ
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "📉 การเปลี่ยนแปลงวันนี้",
                f"฿{daily_change:,.0f}",
                f"{daily_change_pct:.2f}%"
            )
        
        with col2:
            st.metric(
                "💰 มูลค่าพอร์ตปัจจุบัน",
                f"฿{client['total_assets']:,.0f}",
                ""
            )
    
    st.markdown("---")
    
    # Contact form
    st.markdown("### 📝 ขอนัดพูดคุยกับที่ปรึกษา")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contact_reason = st.selectbox(
            "เหตุผลที่ต้องการพูดคุย",
            options=[
                "พอร์ตติดลบ ต้องการคำปรึกษา",
                "ต้องการปรับกลยุทธ์การลงทุน",
                "สอบถามเรื่อง SSF/RMF",
                "วางแผนการเกษียณ",
                "อื่นๆ"
            ]
        )
        
        contact_phone = st.text_input(
            "📞 เบอร์โทรศัพท์ติดต่อกลับ",
            placeholder="08x-xxx-xxxx"
        )
    
    with col2:
        preferred_time = st.selectbox(
            "ช่วงเวลาที่สะดวก",
            options=[
                "ทันที (ด่วน)",
                "ช่วงเช้า (9:00 - 12:00)",
                "ช่วงบ่าย (13:00 - 17:00)",
                "ช่วงเย็น (17:00 - 19:00)"
            ]
        )
        
        additional_note = st.text_area(
            "📋 หมายเหตุเพิ่มเติม",
            placeholder="ข้อมูลอื่นๆ ที่ต้องการแจ้ง...",
            height=100
        )
    
    st.markdown("---")
    
    # LINE Notify settings
    with st.expander("⚙️ ตั้งค่า LINE Notify (สำหรับที่ปรึกษา)"):
        notify_status = get_notify_status()
        
        if notify_status['mock_mode']:
            st.warning("📌 ระบบอยู่ใน **Mock Mode** - ไม่ได้ส่ง LINE จริง")
        else:
            st.success("✅ ระบบเชื่อมต่อ LINE Notify แล้ว")
        
        line_token = st.text_input(
            "LINE Notify Token",
            type="password",
            placeholder="วาง Token ที่นี่...",
            help="ขอ Token ได้ที่ https://notify-bot.line.me/"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 บันทึก Token"):
                if set_line_token(line_token):
                    st.success("✅ บันทึก Token สำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ Token ไม่ถูกต้อง")
        
        with col2:
            if st.button("🧪 ทดสอบส่ง LINE"):
                result = test_line_notify(line_token if line_token else None)
                if result.success:
                    if result.mock_mode:
                        st.info("📌 [Mock Mode] ข้อความถูกบันทึกแล้ว")
                    else:
                        st.success("✅ ส่ง LINE สำเร็จ!")
                else:
                    st.error(f"❌ Error: {result.message}")
    
    st.markdown("---")
    
    # Send alert button
    if st.button("🚨 ส่งคำขอติดต่อที่ปรึกษา", type="primary"):
        if not contact_phone:
            st.error("กรุณากรอกเบอร์โทรศัพท์")
        else:
            # Create alert
            alert = create_panic_alert(
                client_name=client['name'],
                client_id=1,
                portfolio_value=client['total_assets'],
                daily_change=daily_change,
                contact_phone=contact_phone
            )
            alert.alert_reason = f"{contact_reason} | เวลา: {preferred_time}"
            
            # Send notification
            with st.spinner("กำลังส่งคำขอ..."):
                result = send_advisor_alert(alert)
            
            if result.success:
                if result.mock_mode:
                    st.success("""
                    ### ✅ บันทึกคำขอสำเร็จ!
                    
                    📌 **[Mock Mode]** ระบบบันทึกคำขอแล้ว
                    
                    เมื่อตั้งค่า LINE Notify Token แล้ว ที่ปรึกษาจะได้รับแจ้งเตือนทันที
                    """)
                    
                    # Show what would be sent
                    with st.expander("👁️ ตัวอย่างข้อความที่จะส่ง"):
                        st.code(f"""
🚨 แจ้งเตือนจากระบบ Wealth Advisor

👤 ลูกค้า: {client['name']} (ID: 1)
💰 มูลค่าพอร์ต: ฿{client['total_assets']:,.0f}
📉 เปลี่ยนแปลง: ฿{daily_change:+,.0f} ({daily_change_pct:+.2f}%)

📋 เหตุผล: {contact_reason} | เวลา: {preferred_time}
📞 โทร: {contact_phone}

⏰ เวลา: {result.timestamp}
                        """)
                else:
                    st.success("🎉 ส่งคำขอถึงที่ปรึกษาเรียบร้อยแล้ว! จะมีผู้ติดต่อกลับเร็วๆ นี้")
                    st.balloons()
            else:
                st.error(f"❌ เกิดข้อผิดพลาด: {result.message}")


# =============================================================================
# ADMIN PANEL PAGE (จัดการผู้ใช้) - Admin Only
# =============================================================================

elif selected == "จัดการผู้ใช้":
    # Check role
    require_role([UserRole.ADMIN])
    
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        👑 แผงควบคุมผู้ดูแลระบบ
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        จัดการผู้ใช้และดูสถิติระบบ
    </p>
    """, unsafe_allow_html=True)
    
    # Stats
    auth = st.session_state.auth
    all_users = auth.get_all_users()
    clients = [u for u in all_users if u.is_client]
    advisors = [u for u in all_users if u.is_advisor]
    admins = [u for u in all_users if u.is_admin]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 ผู้ใช้ทั้งหมด", len(all_users))
    with col2:
        st.metric("🧑‍💼 ลูกค้า", len(clients))
    with col3:
        st.metric("👨‍💼 ที่ปรึกษา", len(advisors))
    with col4:
        st.metric("👑 แอดมิน", len(admins))
    
    st.markdown("---")
    
    # User list
    st.markdown("### 📋 รายชื่อผู้ใช้ทั้งหมด")
    
    if all_users:
        user_data = []
        for user in all_users:
            role_badge = {"client": "🧑‍💼 ลูกค้า", "advisor": "👨‍💼 ที่ปรึกษา", "admin": "👑 แอดมิน"}
            user_data.append({
                "ID": user.id,
                "ชื่อ": user.full_name,
                "อีเมล": user.email,
                "บทบาท": role_badge.get(user.role.value, user.role.value),
                "โทรศัพท์": user.phone or "-"
            })
        
        user_df = pd.DataFrame(user_data)
        st.dataframe(user_df, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีผู้ใช้ในระบบ")
    
    st.markdown("---")
    
    # Change user role
    st.markdown("### ⚙️ เปลี่ยนบทบาทผู้ใช้")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_emails = [u.email for u in all_users if u.email != current_user.email]
        selected_user = st.selectbox(
            "เลือกผู้ใช้",
            options=user_emails if user_emails else ["ไม่มีผู้ใช้อื่น"]
        )
    
    with col2:
        new_role = st.selectbox(
            "บทบาทใหม่",
            options=["ลูกค้า", "ที่ปรึกษา", "แอดมิน"]
        )
    
    role_mapping = {"ลูกค้า": UserRole.CLIENT, "ที่ปรึกษา": UserRole.ADVISOR, "แอดมิน": UserRole.ADMIN}
    
    if st.button("💾 บันทึกการเปลี่ยนแปลง", type="primary"):
        if selected_user and selected_user != "ไม่มีผู้ใช้อื่น":
            target_user = next((u for u in all_users if u.email == selected_user), None)
            if target_user:
                result = auth.update_user_role(target_user.id, role_mapping[new_role])
                if result.success:
                    st.success(f"✅ เปลี่ยนบทบาทของ {selected_user} เป็น {new_role} สำเร็จ!")
                    st.rerun()
                else:
                    st.error(f"❌ เกิดข้อผิดพลาด: {result.message}")
    
    # Mock mode notice
    if AUTH_MOCK_MODE:
        st.info("📌 **โหมดทดสอบ** - การเปลี่ยนแปลงจะหายไปเมื่อรีเฟรชหน้า")


# =============================================================================
# ADVISOR CLIENT LIST PAGE (ลูกค้าของฉัน) - Advisor Only
# =============================================================================

elif selected == "ลูกค้าของฉัน":
    # Check role
    require_role([UserRole.ADVISOR, UserRole.ADMIN])
    
    st.markdown("""
    <h1 style='margin-bottom: 0.5rem;'>
        <span style='background: linear-gradient(135deg, #00D26A 0%, #FFD700 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        👥 ลูกค้าของฉัน
        </span>
    </h1>
    <p style='color: #888; margin-bottom: 2rem; font-size: 1.1rem;'>
        รายชื่อลูกค้าที่อยู่ในความดูแล
    </p>
    """, unsafe_allow_html=True)
    
    # Get clients for this advisor
    auth = st.session_state.auth
    
    if current_user.is_admin:
        my_clients = auth.get_users_by_role(UserRole.CLIENT)
        st.info("👑 คุณเป็น Admin - แสดงลูกค้าทั้งหมดในระบบ")
    else:
        my_clients = auth.get_advisor_clients(current_user.id)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 จำนวนลูกค้า", len(my_clients))
    with col2:
        st.metric("💰 AUM รวม", f"฿{5_250_000 * len(my_clients):,.0f}")  # Mock data
    with col3:
        st.metric("📈 ผลตอบแทนเฉลี่ย", "+12.5%")  # Mock data
    
    st.markdown("---")
    
    if my_clients:
        st.markdown("### 📋 รายชื่อลูกค้า")
        
        for client_user in my_clients:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 0.5rem;'>
                        <p style='margin: 0; font-weight: 600; color: #fff;'>{client_user.full_name}</p>
                        <p style='margin: 0; color: #888; font-size: 0.85rem;'>{client_user.email}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"📞 {client_user.phone or '-'}")
                
                with col3:
                    # Mock portfolio status
                    st.markdown("""
                    <span style='
                        background: rgba(0, 210, 106, 0.2);
                        color: #00D26A;
                        padding: 0.3rem 0.6rem;
                        border-radius: 4px;
                        font-size: 0.85rem;
                    '>📈 +8.5%</span>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if st.button("ดูพอร์ต", key=f"view_{client_user.id}"):
                        st.session_state.viewing_client = client_user.id
                        st.info(f"กำลังดูพอร์ตของ {client_user.full_name}")
                
                st.markdown("---")
    else:
        st.info("ยังไม่มีลูกค้าในความดูแล")
    
    # Quick actions
    st.markdown("### ⚡ การดำเนินการด่วน")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 สร้างรายงานรวม", use_container_width=True):
            st.info("กำลังสร้างรายงาน... (Mock)")
    
    with col2:
        if st.button("📧 ส่งข่าวสารถึงลูกค้า", use_container_width=True):
            st.info("เปิดหน้าส่งข่าวสาร... (Mock)")
    
    with col3:
        if st.button("🔔 ตั้งการแจ้งเตือน", use_container_width=True):
            st.info("เปิดการตั้งค่าการแจ้งเตือน... (Mock)")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p style='margin: 0; font-size: 1rem;'>💎 ระบบที่ปรึกษาการเงินอัจฉริยะ v1.2</p>
    <p style='margin: 0.3rem 0 0 0; font-size: 0.85rem;'>
        ขับเคลื่อนด้วย Black-Litterman, Monte Carlo & Supabase Auth
    </p>
</div>
""", unsafe_allow_html=True)


