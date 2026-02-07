"""
Financial Models Module
=======================
Contains mathematical models for:
1. Monte Carlo Simulation for retirement planning
2. Portfolio rebalancing calculations
3. Risk metrics and analytics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# =============================================================================
# MONTE CARLO SIMULATION
# =============================================================================

@dataclass
class SimulationResult:
    """Container for Monte Carlo simulation results."""
    years: np.ndarray
    paths: np.ndarray  # Shape: (n_simulations, n_years)
    percentile_10: np.ndarray
    percentile_50: np.ndarray
    percentile_90: np.ndarray
    final_values: np.ndarray
    probability_of_success: float  # Probability of reaching goal


def run_monte_carlo(
    current_wealth: float,
    monthly_contribution: float,
    years_to_retire: int,
    annual_return: float = 0.07,
    annual_volatility: float = 0.15,
    n_simulations: int = 1000,
    goal_amount: Optional[float] = None
) -> SimulationResult:
    """
    Run Monte Carlo simulation for retirement planning.
    
    Uses Geometric Brownian Motion (GBM) to model portfolio value over time:
        dS = μS dt + σS dW
    
    Where:
        S = portfolio value
        μ = expected annual return
        σ = annual volatility
        dW = Wiener process (random walk)
    
    Discrete-time approximation:
        S(t+1) = S(t) * exp((μ - σ²/2)Δt + σ√Δt * Z)
    
    Where Z ~ N(0,1)
    
    Parameters
    ----------
    current_wealth : float
        Starting portfolio value
    monthly_contribution : float
        Monthly savings contribution
    years_to_retire : int
        Investment horizon in years
    annual_return : float
        Expected annual return (e.g., 0.07 for 7%)
    annual_volatility : float
        Annual volatility (e.g., 0.15 for 15%)
    n_simulations : int
        Number of simulation paths (default 1000)
    goal_amount : float, optional
        Target retirement amount for success probability
        
    Returns
    -------
    SimulationResult
        Object containing all simulation results and statistics
        
    Financial Interpretation:
    ------------------------
    - 10th percentile: "Worst case" - only 10% of outcomes are worse
    - 50th percentile: "Base case" - median outcome
    - 90th percentile: "Best case" - only 10% of outcomes are better
    
    This helps clients understand the range of possible outcomes
    and plan accordingly.
    """
    np.random.seed(42)  # For reproducibility in demo
    
    # Time parameters
    n_periods = years_to_retire * 12  # Monthly periods
    dt = 1/12  # Time step (1 month = 1/12 year)
    
    # Convert annual parameters to monthly
    monthly_return = annual_return / 12
    monthly_volatility = annual_volatility / np.sqrt(12)
    
    # GBM drift adjustment to ensure expected return is correct
    # E[exp(X)] = exp(μ + σ²/2), so we subtract σ²/2 from μ
    drift = (annual_return - 0.5 * annual_volatility**2) / 12
    
    # Initialize paths array
    paths = np.zeros((n_simulations, n_periods + 1))
    paths[:, 0] = current_wealth
    
    # Generate random returns for all simulations at once
    # Using vectorized operations for efficiency
    random_shocks = np.random.standard_normal((n_simulations, n_periods))
    
    # Simulate paths
    for t in range(1, n_periods + 1):
        # GBM step: S(t+1) = S(t) * exp(drift + vol * Z) + contribution
        growth_factor = np.exp(drift + monthly_volatility * random_shocks[:, t-1])
        paths[:, t] = paths[:, t-1] * growth_factor + monthly_contribution
    
    # Calculate statistics at each time point
    percentile_10 = np.percentile(paths, 10, axis=0)
    percentile_50 = np.percentile(paths, 50, axis=0)
    percentile_90 = np.percentile(paths, 90, axis=0)
    
    # Final values for success probability
    final_values = paths[:, -1]
    
    # Calculate probability of reaching goal
    if goal_amount is not None:
        probability_of_success = np.mean(final_values >= goal_amount)
    else:
        probability_of_success = 1.0  # No goal specified
    
    # Create year array for plotting (convert months to years)
    years = np.arange(n_periods + 1) / 12
    
    return SimulationResult(
        years=years,
        paths=paths,
        percentile_10=percentile_10,
        percentile_50=percentile_50,
        percentile_90=percentile_90,
        final_values=final_values,
        probability_of_success=probability_of_success
    )


def summarize_simulation(result: SimulationResult) -> Dict:
    """
    Create a summary dictionary of simulation results.
    """
    return {
        "Initial Wealth": result.paths[0, 0],
        "Years": result.years[-1],
        "Median Final Value": np.median(result.final_values),
        "10th Percentile": np.percentile(result.final_values, 10),
        "90th Percentile": np.percentile(result.final_values, 90),
        "Mean Final Value": np.mean(result.final_values),
        "Std Dev": np.std(result.final_values),
        "Probability of Success": result.probability_of_success
    }


# =============================================================================
# PORTFOLIO REBALANCING
# =============================================================================

@dataclass
class RebalanceAction:
    """Represents a single rebalancing trade."""
    asset: str
    action: str  # "BUY" or "SELL"
    current_weight: float
    target_weight: float
    drift: float
    trade_amount: float  # In currency units
    trade_units: int  # Estimated units (shares/funds)


def calculate_drift(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float]
) -> pd.DataFrame:
    """
    Calculate drift between current and target allocations.
    
    Drift = Current Weight - Target Weight
    
    Interpretation:
    - Positive drift: Over-allocated (need to sell)
    - Negative drift: Under-allocated (need to buy)
    
    Parameters
    ----------
    current_weights : dict
        Current portfolio weights
    target_weights : dict
        Target portfolio weights
        
    Returns
    -------
    pd.DataFrame
        DataFrame with assets, weights, and drift values
    """
    assets = list(set(current_weights.keys()) | set(target_weights.keys()))
    
    drift_data = []
    for asset in assets:
        current = current_weights.get(asset, 0)
        target = target_weights.get(asset, 0)
        drift = current - target
        
        drift_data.append({
            "Asset": asset,
            "Current (%)": current * 100,
            "Target (%)": target * 100,
            "Drift (%)": drift * 100,
            "Status": _get_drift_status(drift)
        })
    
    return pd.DataFrame(drift_data).sort_values("Drift (%)", ascending=False)


def _get_drift_status(drift: float) -> str:
    """Get status emoji based on drift magnitude."""
    abs_drift = abs(drift)
    if abs_drift > 0.05:  # > 5%
        return "🔴 Rebalance Needed"
    elif abs_drift > 0.02:  # 2-5%
        return "🟡 Monitor"
    else:
        return "🟢 On Target"


def generate_action_plan(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    portfolio_value: float,
    asset_prices: Optional[Dict[str, float]] = None,
    drift_threshold: float = 0.05
) -> List[RebalanceAction]:
    """
    Generate specific trade recommendations for rebalancing.
    
    Only generates actions for assets with drift > threshold.
    
    Parameters
    ----------
    current_weights : dict
        Current portfolio weights
    target_weights : dict
        Target portfolio weights
    portfolio_value : float
        Total portfolio value in currency units
    asset_prices : dict, optional
        Current price per unit for each asset
        (used to calculate number of units to trade)
    drift_threshold : float
        Minimum absolute drift to trigger rebalancing (default 5%)
        
    Returns
    -------
    list
        List of RebalanceAction objects with trade details
        
    Example Output:
    --------------
    "SELL 1,000 units of K-US-Tech (reducing from 40% to 35%)"
    "BUY 500 units of Gold (increasing from 10% to 20%)"
    """
    # Default prices if not provided
    if asset_prices is None:
        asset_prices = {
            "Thai Stock": 100,
            "US Tech": 450,
            "Gold": 180,
            "Bonds": 100
        }
    
    actions = []
    assets = list(set(current_weights.keys()) | set(target_weights.keys()))
    
    for asset in assets:
        current = current_weights.get(asset, 0)
        target = target_weights.get(asset, 0)
        drift = current - target
        
        # Only create action if drift exceeds threshold
        if abs(drift) > drift_threshold:
            # Calculate trade amount in currency
            trade_amount = abs(drift) * portfolio_value
            
            # Calculate units to trade
            price = asset_prices.get(asset, 100)
            trade_units = int(trade_amount / price)
            
            action = RebalanceAction(
                asset=asset,
                action="SELL" if drift > 0 else "BUY",
                current_weight=current,
                target_weight=target,
                drift=drift,
                trade_amount=trade_amount,
                trade_units=trade_units
            )
            actions.append(action)
    
    # Sort by absolute trade amount (largest first)
    actions.sort(key=lambda x: abs(x.trade_amount), reverse=True)
    
    return actions


def format_action_plan(actions: List[RebalanceAction]) -> pd.DataFrame:
    """
    Format action plan as a readable DataFrame.
    """
    if not actions:
        return pd.DataFrame({"Message": ["No rebalancing needed at this time."]})
    
    data = []
    for action in actions:
        data.append({
            "Action": f"{'🔻 SELL' if action.action == 'SELL' else '🔺 BUY'}",
            "Asset": action.asset,
            "Units": f"{action.trade_units:,}",
            "Amount": f"฿{action.trade_amount:,.0f}",
            "Current → Target": f"{action.current_weight*100:.1f}% → {action.target_weight*100:.1f}%"
        })
    
    return pd.DataFrame(data)


# =============================================================================
# RISK METRICS
# =============================================================================

def calculate_risk_score(
    weights: Dict[str, float],
    asset_risk_ratings: Optional[Dict[str, int]] = None
) -> int:
    """
    Calculate portfolio risk score (1-10 scale).
    
    Risk is a weighted average of individual asset risk ratings.
    
    Parameters
    ----------
    weights : dict
        Portfolio weights
    asset_risk_ratings : dict, optional
        Risk rating for each asset (1-10)
        Higher = more risky
        
    Returns
    -------
    int
        Overall portfolio risk score (1-10)
    """
    # Default risk ratings
    if asset_risk_ratings is None:
        asset_risk_ratings = {
            "Thai Stock": 7,   # Emerging market equity
            "US Tech": 8,     # High volatility sector
            "Gold": 5,        # Moderate, hedge asset
            "Bonds": 2        # Low risk fixed income
        }
    
    # Calculate weighted average risk
    total_risk = 0
    total_weight = 0
    
    for asset, weight in weights.items():
        risk = asset_risk_ratings.get(asset, 5)
        total_risk += weight * risk
        total_weight += weight
    
    if total_weight > 0:
        avg_risk = total_risk / total_weight
    else:
        avg_risk = 5
    
    return round(avg_risk)


def calculate_portfolio_volatility(
    weights: Dict[str, float],
    cov_matrix: pd.DataFrame
) -> float:
    """
    Calculate annualized portfolio volatility (standard deviation).
    
    Portfolio variance: σ²_p = w' Σ w
    
    Parameters
    ----------
    weights : dict
        Portfolio weights
    cov_matrix : pd.DataFrame
        Covariance matrix of asset returns
        
    Returns
    -------
    float
        Annualized portfolio volatility
    """
    assets = list(weights.keys())
    w = np.array([weights.get(a, 0) for a in assets])
    Sigma = cov_matrix.loc[assets, assets].values
    
    portfolio_variance = w @ Sigma @ w
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    return portfolio_volatility


def calculate_expected_return(
    weights: Dict[str, float],
    expected_returns: pd.Series
) -> float:
    """
    Calculate portfolio expected return.
    
    E[R_p] = Σ w_i * E[R_i]
    """
    portfolio_return = 0
    for asset, weight in weights.items():
        if asset in expected_returns.index:
            portfolio_return += weight * expected_returns[asset]
    
    return portfolio_return


def calculate_sharpe_ratio(
    weights: Dict[str, float],
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.02
) -> float:
    """
    Calculate Sharpe Ratio.
    
    Sharpe = (E[R_p] - R_f) / σ_p
    
    Interpretation:
    - > 1.0: Good
    - > 2.0: Very good
    - > 3.0: Excellent
    """
    port_return = calculate_expected_return(weights, expected_returns)
    port_vol = calculate_portfolio_volatility(weights, cov_matrix)
    
    if port_vol > 0:
        sharpe = (port_return - risk_free_rate) / port_vol
    else:
        sharpe = 0
    
    return sharpe
