"""
Black-Litterman Algorithm Module
================================
Implements the Black-Litterman model for portfolio optimization.

The Black-Litterman model combines:
1. Market equilibrium (implied returns from CAPM)
2. Investor views (subjective expectations)

This produces a new set of expected returns that can be used
for mean-variance optimization.

Mathematical Background:
------------------------
The model starts with the equilibrium excess returns (π):
    π = δ * Σ * w_mkt

Where:
    δ = risk aversion coefficient
    Σ = covariance matrix of returns
    w_mkt = market capitalization weights

Then incorporates investor views through Bayesian updating:
    E[R] = [(τΣ)^(-1) + P'Ω^(-1)P]^(-1) * [(τΣ)^(-1)π + P'Ω^(-1)Q]

Where:
    τ = scaling factor (uncertainty in equilibrium)
    P = pick matrix (which assets are in each view)
    Q = view returns (expected outperformance)
    Ω = uncertainty in views
"""

import numpy as np
import pandas as pd
from scipy import optimize
from typing import Dict, List, Tuple, Optional


# =============================================================================
# EQUILIBRIUM RETURNS (CAPM)
# =============================================================================

def calculate_equilibrium_returns(
    cov_matrix: pd.DataFrame,
    market_weights: Dict[str, float],
    risk_aversion: float = 2.5,
    risk_free_rate: float = 0.02
) -> pd.Series:
    """
    Calculate equilibrium (implied) returns using reverse optimization.
    
    The idea: Given market cap weights represent the "optimal" portfolio
    held by the aggregate market, what expected returns would justify
    this allocation under mean-variance optimization?
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix of asset returns (annualized)
    market_weights : dict
        Market capitalization weights for each asset
    risk_aversion : float
        Risk aversion coefficient (typically 2-4)
        Higher = more risk averse
    risk_free_rate : float
        Annual risk-free rate
        
    Returns
    -------
    pd.Series
        Implied equilibrium returns for each asset
        
    Mathematical Derivation:
    -----------------------
    From mean-variance optimization, optimal weights satisfy:
        w* = (1/δ) * Σ^(-1) * (μ - rf)
    
    Rearranging for returns:
        μ = rf + δ * Σ * w*
    
    The excess return (π) is:
        π = δ * Σ * w_mkt
    """
    assets = list(market_weights.keys())
    
    # Convert to numpy arrays maintaining order
    weights = np.array([market_weights[asset] for asset in assets])
    cov = cov_matrix.loc[assets, assets].values
    
    # Calculate excess returns: π = δ * Σ * w
    excess_returns = risk_aversion * cov @ weights
    
    # Add risk-free rate for total returns
    total_returns = excess_returns + risk_free_rate
    
    return pd.Series(total_returns, index=assets, name="Equilibrium Returns")


# =============================================================================
# BLACK-LITTERMAN MODEL
# =============================================================================

def black_litterman(
    cov_matrix: pd.DataFrame,
    market_weights: Dict[str, float],
    views: Dict[str, float],
    view_confidences: Optional[Dict[str, float]] = None,
    tau: float = 0.05,
    risk_aversion: float = 2.5,
    risk_free_rate: float = 0.02
) -> Tuple[pd.Series, pd.Series]:
    """
    Implement the Black-Litterman model to combine equilibrium returns
    with investor views.
    
    Parameters
    ----------
    cov_matrix : pd.DataFrame
        Covariance matrix of asset returns (annualized)
    market_weights : dict
        Market capitalization weights
    views : dict
        Investor views as {asset: expected_excess_return}
        e.g., {"US Tech": 0.05} means "US Tech will outperform by 5%"
    view_confidences : dict, optional
        Confidence in each view (0-1). Higher = more confident.
        Defaults to 0.5 for all views.
    tau : float
        Scaling factor representing uncertainty in equilibrium.
        Typically 0.01 to 0.1. Lower = trust equilibrium more.
    risk_aversion : float
        Risk aversion coefficient
    risk_free_rate : float
        Annual risk-free rate
        
    Returns
    -------
    tuple
        (posterior_returns, optimal_weights)
        
    Example:
    --------
    If you believe US Tech will outperform by 5%:
        views = {"US Tech": 0.05}
        
    The model will adjust all asset returns, not just US Tech,
    accounting for correlations between assets.
    """
    assets = list(market_weights.keys())
    n_assets = len(assets)
    
    # Step 1: Get equilibrium returns
    pi = calculate_equilibrium_returns(
        cov_matrix, market_weights, risk_aversion, risk_free_rate
    )
    
    # If no views, return equilibrium
    if not views:
        weights = _optimize_portfolio(pi, cov_matrix, risk_aversion)
        return pi, weights
    
    # Step 2: Build view matrices
    # P: Pick matrix (n_views x n_assets)
    # Q: View returns vector (n_views,)
    n_views = len(views)
    P = np.zeros((n_views, n_assets))
    Q = np.zeros(n_views)
    
    # Default confidences
    if view_confidences is None:
        view_confidences = {asset: 0.5 for asset in views}
    
    for i, (asset, view_return) in enumerate(views.items()):
        if asset in assets:
            asset_idx = assets.index(asset)
            P[i, asset_idx] = 1.0
            Q[i] = view_return
    
    # Step 3: Build uncertainty matrix (Omega)
    # Ω = diag(P * τ * Σ * P')
    # This scales uncertainty by the variance of the view portfolio
    # Adjust by confidence: lower confidence = higher uncertainty
    Sigma = cov_matrix.loc[assets, assets].values
    omega_diag = np.diag(P @ (tau * Sigma) @ P.T)
    
    # Adjust by confidence (inverse relationship)
    for i, asset in enumerate(views.keys()):
        conf = view_confidences.get(asset, 0.5)
        # Confidence of 1 = use omega as is
        # Confidence of 0.1 = multiply omega by 10 (higher uncertainty)
        omega_diag[i] /= max(conf, 0.1)
    
    Omega = np.diag(omega_diag)
    
    # Step 4: Bayesian update (Black-Litterman formula)
    # Posterior expected returns:
    # E[R] = [(τΣ)^(-1) + P'Ω^(-1)P]^(-1) * [(τΣ)^(-1)π + P'Ω^(-1)Q]
    
    tau_Sigma = tau * Sigma
    tau_Sigma_inv = np.linalg.inv(tau_Sigma)
    Omega_inv = np.linalg.inv(Omega)
    
    # Left side: [( τΣ)^(-1) + P'Ω^(-1)P]^(-1)
    left_term = np.linalg.inv(tau_Sigma_inv + P.T @ Omega_inv @ P)
    
    # Right side: [(τΣ)^(-1)π + P'Ω^(-1)Q]
    pi_array = pi.loc[assets].values
    right_term = tau_Sigma_inv @ pi_array + P.T @ Omega_inv @ Q
    
    # Posterior returns
    posterior_returns = left_term @ right_term
    posterior_series = pd.Series(posterior_returns, index=assets, name="BL Returns")
    
    # Step 5: Optimize portfolio with new returns
    optimal_weights = _optimize_portfolio(posterior_series, cov_matrix, risk_aversion)
    
    return posterior_series, optimal_weights


def _optimize_portfolio(
    expected_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_aversion: float = 2.5
) -> pd.Series:
    """
    Mean-variance optimization with constraints.
    
    Maximize: μ'w - (δ/2) * w'Σw
    Subject to: sum(w) = 1, w >= 0
    
    This is the standard quadratic utility function where we balance
    expected return against portfolio variance.
    """
    assets = expected_returns.index.tolist()
    n = len(assets)
    mu = expected_returns.values
    Sigma = cov_matrix.loc[assets, assets].values
    
    # Objective: minimize -(μ'w - (δ/2) * w'Σw) = -μ'w + (δ/2) * w'Σw
    def objective(w):
        return -mu @ w + (risk_aversion / 2) * w @ Sigma @ w
    
    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum to 1
    ]
    
    # Bounds: no short selling (0 <= w <= 1)
    bounds = [(0, 1) for _ in range(n)]
    
    # Initial guess: equal weights
    w0 = np.ones(n) / n
    
    # Optimize
    result = optimize.minimize(
        objective, w0, method='SLSQP',
        bounds=bounds, constraints=constraints
    )
    
    if result.success:
        weights = result.x
    else:
        # Fallback to market weights if optimization fails
        weights = np.array([1/n] * n)
    
    # Clean up small weights (< 1%)
    weights = np.where(weights < 0.01, 0, weights)
    weights = weights / weights.sum()  # Renormalize
    
    return pd.Series(weights, index=assets, name="Optimal Weights")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_view_from_outlook(
    asset: str,
    outlook: str,
    magnitude: float = 0.05
) -> Dict[str, float]:
    """
    Create a view dictionary from a qualitative outlook.
    
    Parameters
    ----------
    asset : str
        Asset name
    outlook : str
        One of "bullish", "bearish", "neutral"
    magnitude : float
        Expected outperformance/underperformance magnitude
        
    Returns
    -------
    dict
        View dictionary for black_litterman function
    """
    if outlook.lower() == "bullish":
        return {asset: magnitude}
    elif outlook.lower() == "bearish":
        return {asset: -magnitude}
    else:
        return {}


def combine_views(*view_dicts: Dict[str, float]) -> Dict[str, float]:
    """Combine multiple view dictionaries into one."""
    combined = {}
    for view in view_dicts:
        combined.update(view)
    return combined


def display_allocation_comparison(
    market_weights: Dict[str, float],
    bl_weights: pd.Series
) -> pd.DataFrame:
    """
    Create a comparison table of market vs BL-optimized weights.
    """
    assets = bl_weights.index.tolist()
    
    comparison = pd.DataFrame({
        "Asset": assets,
        "Market Weight": [market_weights.get(a, 0) for a in assets],
        "BL Optimal Weight": bl_weights.values,
    })
    
    comparison["Difference"] = comparison["BL Optimal Weight"] - comparison["Market Weight"]
    
    return comparison
