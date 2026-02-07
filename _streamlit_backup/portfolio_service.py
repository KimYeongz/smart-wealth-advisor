"""
Portfolio Service Module
========================
จัดการข้อมูลพอร์ตโฟลิโอของ user

Features:
- CRUD operations สำหรับ portfolio
- Transaction history
- Mock mode สำหรับ development
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

# Try to import supabase
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
MOCK_MODE = not (SUPABASE_URL and SUPABASE_KEY and SUPABASE_AVAILABLE)


# =============================================================================
# DATA CLASSES
# =============================================================================

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    BUY = "buy"
    SELL = "sell"
    REBALANCE = "rebalance"


@dataclass
class Portfolio:
    """ข้อมูลพอร์ตโฟลิโอ"""
    id: str
    user_id: str
    total_value: float = 0.0
    cash_balance: float = 0.0
    ytd_return: float = 0.0
    risk_score: int = 5
    holdings: Dict[str, float] = field(default_factory=dict)  # asset -> weight
    target_allocation: Dict[str, float] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Transaction:
    """ข้อมูลธุรกรรม"""
    id: str
    portfolio_id: str
    type: TransactionType
    amount: float
    asset_name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None


# =============================================================================
# MOCK DATA STORAGE
# =============================================================================

# In-memory storage for mock mode
MOCK_PORTFOLIOS: Dict[str, Portfolio] = {}
MOCK_TRANSACTIONS: Dict[str, List[Transaction]] = {}


# =============================================================================
# PORTFOLIO SERVICE
# =============================================================================

class PortfolioService:
    """จัดการข้อมูลพอร์ตโฟลิโอ"""
    
    def __init__(self):
        self.mock_mode = MOCK_MODE
        self.client: Optional[Client] = None
        
        if not self.mock_mode:
            try:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                self.mock_mode = True
    
    # =========================================================================
    # GET PORTFOLIO
    # =========================================================================
    
    def get_portfolio(self, user_id: str) -> Optional[Portfolio]:
        """ดึงข้อมูลพอร์ตของ user"""
        if self.mock_mode:
            return self._mock_get_portfolio(user_id)
        
        try:
            # Get portfolio
            result = self.client.table("portfolios").select("*").eq(
                "user_id", user_id
            ).single().execute()
            
            if not result.data:
                return None
            
            portfolio_data = result.data
            
            # Get holdings
            holdings_result = self.client.table("portfolio_holdings").select("*").eq(
                "portfolio_id", portfolio_data["id"]
            ).execute()
            
            holdings = {}
            target_alloc = {}
            for h in holdings_result.data:
                holdings[h["asset_name"]] = h["current_weight"]
                target_alloc[h["asset_name"]] = h["target_weight"]
            
            return Portfolio(
                id=portfolio_data["id"],
                user_id=user_id,
                total_value=float(portfolio_data.get("total_value", 0)),
                cash_balance=float(portfolio_data.get("cash_balance", 0)),
                ytd_return=float(portfolio_data.get("ytd_return", 0)),
                risk_score=portfolio_data.get("risk_score", 5),
                holdings=holdings,
                target_allocation=target_alloc
            )
            
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return self._mock_get_portfolio(user_id)
    
    def _mock_get_portfolio(self, user_id: str) -> Portfolio:
        """Mock: ดึงหรือสร้างพอร์ตใหม่"""
        if user_id not in MOCK_PORTFOLIOS:
            # Create new empty portfolio
            MOCK_PORTFOLIOS[user_id] = Portfolio(
                id=f"portfolio-{user_id}",
                user_id=user_id,
                total_value=0,
                cash_balance=0,
                ytd_return=0,
                risk_score=5,
                holdings={
                    "Thai Stock": 0,
                    "US Tech": 0,
                    "Gold": 0,
                    "Bonds": 0
                },
                target_allocation={
                    "Thai Stock": 0.25,
                    "US Tech": 0.35,
                    "Gold": 0.20,
                    "Bonds": 0.20
                },
                created_at=datetime.now()
            )
            MOCK_TRANSACTIONS[user_id] = []
        
        return MOCK_PORTFOLIOS[user_id]
    
    # =========================================================================
    # DEPOSIT / WITHDRAW
    # =========================================================================
    
    def deposit(self, user_id: str, amount: float, description: str = "ฝากเงิน") -> Tuple[bool, str]:
        """ฝากเงินเข้าพอร์ต"""
        if amount <= 0:
            return False, "จำนวนเงินต้องมากกว่า 0"
        
        if self.mock_mode:
            return self._mock_deposit(user_id, amount, description)
        
        try:
            portfolio = self.get_portfolio(user_id)
            if not portfolio:
                return False, "ไม่พบพอร์ตโฟลิโอ"
            
            new_balance = portfolio.cash_balance + amount
            new_total = portfolio.total_value + amount
            
            # Update portfolio
            self.client.table("portfolios").update({
                "cash_balance": new_balance,
                "total_value": new_total
            }).eq("user_id", user_id).execute()
            
            # Record transaction
            self.client.table("transactions").insert({
                "portfolio_id": portfolio.id,
                "type": "deposit",
                "amount": amount,
                "description": description
            }).execute()
            
            return True, f"ฝากเงิน ฿{amount:,.2f} สำเร็จ"
            
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"
    
    def _mock_deposit(self, user_id: str, amount: float, description: str) -> Tuple[bool, str]:
        """Mock: ฝากเงิน"""
        portfolio = self._mock_get_portfolio(user_id)
        portfolio.cash_balance += amount
        portfolio.total_value += amount
        portfolio.updated_at = datetime.now()
        
        # Record transaction
        tx = Transaction(
            id=f"tx-{len(MOCK_TRANSACTIONS.get(user_id, []))+1}",
            portfolio_id=portfolio.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            description=description,
            created_at=datetime.now()
        )
        MOCK_TRANSACTIONS.setdefault(user_id, []).append(tx)
        
        return True, f"[Mock] ฝากเงิน ฿{amount:,.2f} สำเร็จ"
    
    def withdraw(self, user_id: str, amount: float, description: str = "ถอนเงิน") -> Tuple[bool, str]:
        """ถอนเงินจากพอร์ต"""
        if amount <= 0:
            return False, "จำนวนเงินต้องมากกว่า 0"
        
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return False, "ไม่พบพอร์ตโฟลิโอ"
        
        if amount > portfolio.cash_balance:
            return False, f"ยอดเงินสดไม่เพียงพอ (คงเหลือ ฿{portfolio.cash_balance:,.2f})"
        
        if self.mock_mode:
            return self._mock_withdraw(user_id, amount, description)
        
        try:
            new_balance = portfolio.cash_balance - amount
            new_total = portfolio.total_value - amount
            
            self.client.table("portfolios").update({
                "cash_balance": new_balance,
                "total_value": new_total
            }).eq("user_id", user_id).execute()
            
            self.client.table("transactions").insert({
                "portfolio_id": portfolio.id,
                "type": "withdraw",
                "amount": amount,
                "description": description
            }).execute()
            
            return True, f"ถอนเงิน ฿{amount:,.2f} สำเร็จ"
            
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"
    
    def _mock_withdraw(self, user_id: str, amount: float, description: str) -> Tuple[bool, str]:
        """Mock: ถอนเงิน"""
        portfolio = MOCK_PORTFOLIOS[user_id]
        portfolio.cash_balance -= amount
        portfolio.total_value -= amount
        portfolio.updated_at = datetime.now()
        
        tx = Transaction(
            id=f"tx-{len(MOCK_TRANSACTIONS.get(user_id, []))+1}",
            portfolio_id=portfolio.id,
            type=TransactionType.WITHDRAW,
            amount=amount,
            description=description,
            created_at=datetime.now()
        )
        MOCK_TRANSACTIONS.setdefault(user_id, []).append(tx)
        
        return True, f"[Mock] ถอนเงิน ฿{amount:,.2f} สำเร็จ"
    
    # =========================================================================
    # INVEST (Buy Assets)
    # =========================================================================
    
    def invest(self, user_id: str, allocation: Dict[str, float]) -> Tuple[bool, str]:
        """
        ลงทุนตามสัดส่วนที่กำหนด
        
        Args:
            allocation: Dict of asset_name -> percentage (0-1)
                        ต้องรวมกันเป็น 1.0
        """
        # Validate allocation
        total_alloc = sum(allocation.values())
        if abs(total_alloc - 1.0) > 0.01:
            return False, f"สัดส่วนรวมต้องเท่ากับ 100% (ปัจจุบัน: {total_alloc*100:.1f}%)"
        
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return False, "ไม่พบพอร์ตโฟลิโอ"
        
        if portfolio.cash_balance <= 0:
            return False, "ไม่มียอดเงินสดสำหรับลงทุน กรุณาฝากเงินก่อน"
        
        if self.mock_mode:
            return self._mock_invest(user_id, allocation)
        
        # In real mode, would update holdings in Supabase
        # For now, use mock implementation
        return self._mock_invest(user_id, allocation)
    
    def _mock_invest(self, user_id: str, allocation: Dict[str, float]) -> Tuple[bool, str]:
        """Mock: ลงทุน"""
        portfolio = MOCK_PORTFOLIOS[user_id]
        
        # Move cash to investments based on allocation
        investment_amount = portfolio.cash_balance
        portfolio.cash_balance = 0
        
        # Update holdings
        for asset, weight in allocation.items():
            portfolio.holdings[asset] = weight
            portfolio.target_allocation[asset] = weight
        
        portfolio.updated_at = datetime.now()
        
        # Record transaction
        tx = Transaction(
            id=f"tx-{len(MOCK_TRANSACTIONS.get(user_id, []))+1}",
            portfolio_id=portfolio.id,
            type=TransactionType.BUY,
            amount=investment_amount,
            description=f"ลงทุนตามสัดส่วน: {', '.join([f'{k}:{v*100:.0f}%' for k,v in allocation.items()])}",
            created_at=datetime.now()
        )
        MOCK_TRANSACTIONS.setdefault(user_id, []).append(tx)
        
        return True, f"[Mock] ลงทุน ฿{investment_amount:,.2f} ตามสัดส่วนที่กำหนด"
    
    # =========================================================================
    # TRANSACTIONS HISTORY
    # =========================================================================
    
    def get_transactions(self, user_id: str, limit: int = 20) -> List[Transaction]:
        """ดึงประวัติธุรกรรม"""
        if self.mock_mode:
            return self._mock_get_transactions(user_id, limit)
        
        try:
            portfolio = self.get_portfolio(user_id)
            if not portfolio:
                return []
            
            result = self.client.table("transactions").select("*").eq(
                "portfolio_id", portfolio.id
            ).order("created_at", desc=True).limit(limit).execute()
            
            return [
                Transaction(
                    id=t["id"],
                    portfolio_id=t["portfolio_id"],
                    type=TransactionType(t["type"]),
                    amount=t["amount"],
                    asset_name=t.get("asset_name"),
                    description=t.get("description"),
                    created_at=t.get("created_at")
                )
                for t in result.data
            ]
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def _mock_get_transactions(self, user_id: str, limit: int) -> List[Transaction]:
        """Mock: ดึงประวัติธุรกรรม"""
        txs = MOCK_TRANSACTIONS.get(user_id, [])
        return sorted(txs, key=lambda x: x.created_at or datetime.min, reverse=True)[:limit]
    
    # =========================================================================
    # UPDATE SETTINGS
    # =========================================================================
    
    def update_risk_score(self, user_id: str, risk_score: int) -> Tuple[bool, str]:
        """อัพเดทระดับความเสี่ยง"""
        if risk_score < 1 or risk_score > 10:
            return False, "ระดับความเสี่ยงต้องอยู่ระหว่าง 1-10"
        
        if self.mock_mode:
            portfolio = self._mock_get_portfolio(user_id)
            portfolio.risk_score = risk_score
            return True, f"[Mock] อัพเดทระดับความเสี่ยงเป็น {risk_score}"
        
        try:
            self.client.table("portfolios").update({
                "risk_score": risk_score
            }).eq("user_id", user_id).execute()
            
            return True, f"อัพเดทระดับความเสี่ยงเป็น {risk_score}"
            
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"
    
    def update_target_allocation(self, user_id: str, allocation: Dict[str, float]) -> Tuple[bool, str]:
        """อัพเดทสัดส่วนเป้าหมาย"""
        total = sum(allocation.values())
        if abs(total - 1.0) > 0.01:
            return False, f"สัดส่วนรวมต้องเท่ากับ 100%"
        
        if self.mock_mode:
            portfolio = self._mock_get_portfolio(user_id)
            portfolio.target_allocation = allocation
            return True, "[Mock] อัพเดทสัดส่วนเป้าหมายสำเร็จ"
        
        # Real Supabase implementation
        try:
            portfolio = self.get_portfolio(user_id)
            if not portfolio:
                return False, "ไม่พบพอร์ตโฟลิโอ"
            
            for asset, weight in allocation.items():
                self.client.table("portfolio_holdings").upsert({
                    "portfolio_id": portfolio.id,
                    "asset_name": asset,
                    "target_weight": weight
                }).execute()
            
            return True, "อัพเดทสัดส่วนเป้าหมายสำเร็จ"
            
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_portfolio_service: Optional[PortfolioService] = None

def get_portfolio_service() -> PortfolioService:
    """Get the portfolio service singleton."""
    global _portfolio_service
    if _portfolio_service is None:
        _portfolio_service = PortfolioService()
    return _portfolio_service
