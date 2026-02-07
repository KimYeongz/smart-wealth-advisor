"""
Data Loader Module
==================
Handles all data fetching operations including:
- Historical price data via yfinance
- Market capitalization data
- Supabase connection simulation
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# =============================================================================
# ASSET CONFIGURATION
# =============================================================================

# Asset tickers mapping
# - Thai Stock: Using SET index ETF proxy (THD)
# - US Tech: NASDAQ-100 ETF (QQQ)
# - Gold: SPDR Gold Shares (GLD)
# - Bonds: iShares Core US Aggregate Bond ETF (AGG)
ASSET_TICKERS = {
    "Thai Stock": "THD",
    "US Tech": "QQQ", 
    "Gold": "GLD",
    "Bonds": "AGG"
}

# Simulated market capitalizations (in billions USD)
# These represent approximate relative market sizes for equilibrium weights
MARKET_CAPS = {
    "Thai Stock": 500,    # Thai equity market
    "US Tech": 15000,     # US Tech sector
    "Gold": 3000,         # Gold market
    "Bonds": 50000        # US Bond market
}


# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

def get_historical_prices(
    tickers: Optional[Dict[str, str]] = None,
    period: str = "2y",
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch historical adjusted close prices for specified assets.
    
    Parameters
    ----------
    tickers : dict, optional
        Mapping of asset names to ticker symbols.
        Defaults to ASSET_TICKERS.
    period : str
        Data period (e.g., "1y", "2y", "5y", "max")
    interval : str
        Data interval (e.g., "1d", "1wk", "1mo")
        
    Returns
    -------
    pd.DataFrame
        DataFrame with dates as index and asset names as columns,
        containing adjusted close prices.
    """
    if tickers is None:
        tickers = ASSET_TICKERS
    
    try:
        # Download data for all tickers at once for efficiency
        ticker_symbols = list(tickers.values())
        data = yf.download(
            ticker_symbols, 
            period=period, 
            interval=interval,
            progress=False,
            auto_adjust=True
        )
        
        # Extract Close prices
        if len(ticker_symbols) == 1:
            prices = data[['Close']].copy()
            prices.columns = [list(tickers.keys())[0]]
        else:
            prices = data['Close'].copy()
            # Rename columns to asset names
            reverse_map = {v: k for k, v in tickers.items()}
            prices.columns = [reverse_map.get(col, col) for col in prices.columns]
        
        # Drop any rows with missing values
        prices = prices.dropna()
        
        return prices
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Return synthetic data as fallback
        return _generate_synthetic_prices(tickers, period)


def _generate_synthetic_prices(
    tickers: Dict[str, str], 
    period: str = "2y"
) -> pd.DataFrame:
    """
    Generate synthetic price data as fallback when API fails.
    Uses geometric Brownian motion to simulate realistic price paths.
    """
    # Parse period to get number of days
    period_days = {"1y": 252, "2y": 504, "5y": 1260, "max": 2520}
    n_days = period_days.get(period, 504)
    
    # Generate date range
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=n_days, freq='B')
    
    # Asset-specific parameters (annual return, volatility)
    params = {
        "Thai Stock": (0.08, 0.20, 100),
        "US Tech": (0.15, 0.25, 400),
        "Gold": (0.05, 0.15, 180),
        "Bonds": (0.03, 0.05, 100)
    }
    
    np.random.seed(42)  # For reproducibility
    prices_data = {}
    
    for asset in tickers.keys():
        mu, sigma, initial = params.get(asset, (0.07, 0.18, 100))
        
        # Daily parameters
        daily_return = mu / 252
        daily_vol = sigma / np.sqrt(252)
        
        # Generate GBM path
        returns = np.random.normal(daily_return, daily_vol, n_days)
        price_path = initial * np.exp(np.cumsum(returns))
        prices_data[asset] = price_path
    
    return pd.DataFrame(prices_data, index=dates)


def get_market_caps(assets: Optional[List[str]] = None) -> Dict[str, float]:
    """
    Get market capitalization weights for assets.
    
    Parameters
    ----------
    assets : list, optional
        List of asset names. Defaults to all assets in MARKET_CAPS.
        
    Returns
    -------
    dict
        Mapping of asset names to market cap weights (normalized to sum to 1)
    """
    if assets is None:
        assets = list(MARKET_CAPS.keys())
    
    caps = {asset: MARKET_CAPS.get(asset, 1000) for asset in assets}
    total = sum(caps.values())
    
    return {asset: cap / total for asset, cap in caps.items()}


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate log returns from price data.
    
    Log returns are preferred for financial calculations because:
    1. They are time-additive (can sum across periods)
    2. They are symmetric (for small returns)
    3. Better for statistical properties
    """
    return np.log(prices / prices.shift(1)).dropna()


def calculate_statistics(
    prices: pd.DataFrame
) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Calculate expected returns and covariance matrix from price data.
    
    Returns
    -------
    tuple
        (expected_returns, covariance_matrix)
        - expected_returns: Annualized mean returns
        - covariance_matrix: Annualized covariance matrix
    """
    returns = calculate_returns(prices)
    
    # Annualize: multiply daily stats by 252 trading days
    expected_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    return expected_returns, cov_matrix


# =============================================================================
# SUPABASE SIMULATION
# =============================================================================

class SupabaseSimulator:
    """
    Simulates Supabase connection for prototype purposes.
    In production, replace with actual Supabase client.
    """
    
    def __init__(self, url: str = "https://your-project.supabase.co", key: str = "your-anon-key"):
        self.url = url
        self.key = key
        self.connected = True
        self._mock_data = self._init_mock_data()
    
    def _init_mock_data(self) -> Dict:
        """Initialize mock client data."""
        return {
            "clients": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "total_assets": 5000000,
                    "ytd_return": 0.0823,
                    "risk_score": 7,
                    "portfolio": {
                        "Thai Stock": 0.30,
                        "US Tech": 0.35,
                        "Gold": 0.15,
                        "Bonds": 0.20
                    },
                    "target_allocation": {
                        "Thai Stock": 0.25,
                        "US Tech": 0.35,
                        "Gold": 0.20,
                        "Bonds": 0.20
                    }
                }
            ]
        }
    
    def get_client(self, client_id: int = 1) -> Dict:
        """Fetch client data by ID."""
        for client in self._mock_data["clients"]:
            if client["id"] == client_id:
                return client
        return self._mock_data["clients"][0]
    
    def update_portfolio(self, client_id: int, new_allocation: Dict) -> bool:
        """Update client's portfolio allocation."""
        for client in self._mock_data["clients"]:
            if client["id"] == client_id:
                client["portfolio"] = new_allocation
                return True
        return False
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self.connected


def simulate_supabase_connection() -> SupabaseSimulator:
    """
    Create and return a simulated Supabase connection.
    
    Usage:
        db = simulate_supabase_connection()
        client_data = db.get_client(1)
    """
    return SupabaseSimulator()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_currency(value: float, currency: str = "฿") -> str:
    """Format number as currency string."""
    if value >= 1_000_000:
        return f"{currency}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{currency}{value/1_000:.2f}K"
    else:
        return f"{currency}{value:.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format decimal as percentage string."""
    return f"{value * 100:.{decimals}f}%"
