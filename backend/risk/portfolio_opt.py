"""
Portfolio optimization using Modern Portfolio Theory and advanced techniques
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import cvxpy as cp
from scipy.optimize import minimize
from backend.utils.logger import logger


class PortfolioOptimizer:
    """Portfolio optimization with multiple methods"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Annual risk-free rate
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days = 252
    
    def calculate_returns_cov(self, returns: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate expected returns and covariance matrix
        
        Args:
            returns: DataFrame with asset returns
        
        Returns:
            Tuple of (expected_returns, covariance_matrix)
        """
        # Annualized returns
        expected_returns = returns.mean() * self.trading_days
        
        # Covariance matrix (annualized)
        cov_matrix = returns.cov() * self.trading_days
        
        return expected_returns.values, cov_matrix.values
    
    def mean_variance_optimization(self,
                                  returns: pd.DataFrame,
                                  target_return: Optional[float] = None,
                                  max_weight: float = 1.0,
                                  min_weight: float = 0.0) -> Dict:
        """
        Mean-variance optimization (Markowitz)
        
        Args:
            returns: DataFrame with asset returns
            target_return: Target return (if None, maximize Sharpe)
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
        
        Returns:
            Dictionary with optimal weights and metrics
        """
        logger.info("Running mean-variance optimization...")
        
        expected_returns, cov_matrix = self.calculate_returns_cov(returns)
        n_assets = len(expected_returns)
        
        # Define optimization variables
        weights = cp.Variable(n_assets)
        
        # Define portfolio return and risk
        portfolio_return = expected_returns @ weights
        portfolio_risk = cp.quad_form(weights, cov_matrix)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Weights sum to 1
            weights >= min_weight,  # Min weight
            weights <= max_weight   # Max weight
        ]
        
        if target_return is not None:
            # Minimize risk for target return
            constraints.append(portfolio_return >= target_return)
            objective = cp.Minimize(portfolio_risk)
        else:
            # Maximize Sharpe ratio (equivalent to maximizing return for unit risk)
            objective = cp.Maximize(
                (portfolio_return - self.risk_free_rate) / cp.sqrt(portfolio_risk)
            )
        
        # Solve
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        if weights.value is None:
            logger.error("Optimization failed")
            return {}
        
        # Results
        optimal_weights = pd.Series(weights.value, index=returns.columns)
        portfolio_ret = expected_returns @ weights.value
        portfolio_vol = np.sqrt(portfolio_risk.value)
        sharpe = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        
        results = {
            'weights': optimal_weights,
            'expected_return': portfolio_ret,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe
        }
        
        logger.info(f"Optimal portfolio: Return={portfolio_ret:.2%}, "
                   f"Vol={portfolio_vol:.2%}, Sharpe={sharpe:.2f}")
        
        return results
    
    def efficient_frontier(self,
                          returns: pd.DataFrame,
                          n_points: int = 50) -> pd.DataFrame:
        """
        Calculate efficient frontier
        
        Args:
            returns: DataFrame with asset returns
            n_points: Number of points on frontier
        
        Returns:
            DataFrame with frontier points
        """
        logger.info(f"Calculating efficient frontier with {n_points} points...")
        
        expected_returns, cov_matrix = self.calculate_returns_cov(returns)
        
        # Range of target returns
        min_ret = expected_returns.min()
        max_ret = expected_returns.max()
        target_returns = np.linspace(min_ret, max_ret, n_points)
        
        frontier_results = []
        
        for target_ret in target_returns:
            result = self.mean_variance_optimization(returns, target_return=target_ret)
            if result:
                frontier_results.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe': result['sharpe_ratio']
                })
        
        frontier_df = pd.DataFrame(frontier_results)
        
        logger.info(f"Efficient frontier calculated with {len(frontier_df)} points")
        
        return frontier_df
    
    def risk_parity_optimization(self, returns: pd.DataFrame) -> Dict:
        """
        Risk parity portfolio optimization
        
        Args:
            returns: DataFrame with asset returns
        
        Returns:
            Dictionary with optimal weights and metrics
        """
        logger.info("Running risk parity optimization...")
        
        _, cov_matrix = self.calculate_returns_cov(returns)
        n_assets = len(returns.columns)
        
        def risk_parity_objective(weights):
            """Objective: minimize difference in risk contributions"""
            weights = weights.reshape(-1, 1)
            portfolio_var = weights.T @ cov_matrix @ weights
            marginal_contrib = cov_matrix @ weights
            contrib = np.multiply(marginal_contrib, weights.T).T
            
            # Each asset should contribute equally
            target = portfolio_var / n_assets
            return np.sum((contrib - target) ** 2)
        
        # Initial guess: equal weights
        x0 = np.ones(n_assets) / n_assets
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Optimize
        result = minimize(
            risk_parity_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = pd.Series(result.x, index=returns.columns)
        
        # Calculate metrics
        expected_returns, _ = self.calculate_returns_cov(returns)
        portfolio_ret = expected_returns @ result.x
        portfolio_vol = np.sqrt(result.x.T @ cov_matrix @ result.x)
        sharpe = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        
        results = {
            'weights': optimal_weights,
            'expected_return': portfolio_ret,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe
        }
        
        logger.info(f"Risk parity portfolio: Return={portfolio_ret:.2%}, "
                   f"Vol={portfolio_vol:.2%}, Sharpe={sharpe:.2f}")
        
        return results
    
    def black_litterman(self,
                       returns: pd.DataFrame,
                       market_caps: Optional[pd.Series] = None,
                       views: Optional[Dict] = None,
                       tau: float = 0.025) -> Dict:
        """
        Black-Litterman model
        
        Args:
            returns: DataFrame with asset returns
            market_caps: Series with market capitalizations (optional)
            views: Dictionary with view returns and confidence (optional)
            tau: Scaling factor for uncertainty
        
        Returns:
            Dictionary with optimal weights and metrics
        """
        logger.info("Running Black-Litterman optimization...")
        
        expected_returns, cov_matrix = self.calculate_returns_cov(returns)
        n_assets = len(expected_returns)
        
        # Market-cap weighted equilibrium returns (if market caps provided)
        if market_caps is not None:
            market_weights = market_caps / market_caps.sum()
            pi = self.risk_free_rate + cov_matrix @ market_weights
        else:
            # Use historical returns as equilibrium
            pi = expected_returns
        
        # If no views, use equilibrium
        if views is None or len(views) == 0:
            bl_returns = pi
        else:
            # Incorporate views
            P = np.zeros((len(views), n_assets))
            Q = np.zeros(len(views))
            omega_diag = []
            
            for i, (asset, view) in enumerate(views.items()):
                asset_idx = returns.columns.get_loc(asset)
                P[i, asset_idx] = 1
                Q[i] = view['return']
                omega_diag.append(view.get('confidence', 0.1))
            
            omega = np.diag(omega_diag)
            
            # Black-Litterman formula
            tau_sigma = tau * cov_matrix
            inv_tau_sigma = np.linalg.inv(tau_sigma)
            inv_omega = np.linalg.inv(omega)
            
            bl_cov_inv = inv_tau_sigma + P.T @ inv_omega @ P
            bl_cov = np.linalg.inv(bl_cov_inv)
            bl_returns = bl_cov @ (inv_tau_sigma @ pi + P.T @ inv_omega @ Q)
        
        # Optimize using BL returns
        weights = cp.Variable(n_assets)
        portfolio_return = bl_returns @ weights
        portfolio_risk = cp.quad_form(weights, cov_matrix)
        
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,
            weights <= 1
        ]
        
        objective = cp.Maximize(
            (portfolio_return - self.risk_free_rate) / cp.sqrt(portfolio_risk)
        )
        
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        optimal_weights = pd.Series(weights.value, index=returns.columns)
        portfolio_ret = bl_returns @ weights.value
        portfolio_vol = np.sqrt(portfolio_risk.value)
        sharpe = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        
        results = {
            'weights': optimal_weights,
            'expected_return': portfolio_ret,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe,
            'bl_returns': pd.Series(bl_returns, index=returns.columns)
        }
        
        logger.info(f"Black-Litterman portfolio: Return={portfolio_ret:.2%}, "
                   f"Vol={portfolio_vol:.2%}, Sharpe={sharpe:.2f}")
        
        return results
    
    def esg_constrained_optimization(self,
                                    returns: pd.DataFrame,
                                    esg_scores: pd.Series,
                                    min_esg_score: float = 7.0) -> Dict:
        """
        Portfolio optimization with ESG constraints
        
        Args:
            returns: DataFrame with asset returns
            esg_scores: Series with ESG scores (0-10)
            min_esg_score: Minimum portfolio ESG score
        
        Returns:
            Dictionary with optimal weights and metrics
        """
        logger.info(f"Running ESG-constrained optimization (min score: {min_esg_score})...")
        
        expected_returns, cov_matrix = self.calculate_returns_cov(returns)
        n_assets = len(expected_returns)
        
        # Align ESG scores with returns
        aligned_scores = esg_scores.reindex(returns.columns).fillna(0)
        
        # Optimization
        weights = cp.Variable(n_assets)
        portfolio_return = expected_returns @ weights
        portfolio_risk = cp.quad_form(weights, cov_matrix)
        portfolio_esg = aligned_scores.values @ weights
        
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,
            weights <= 1,
            portfolio_esg >= min_esg_score  # ESG constraint
        ]
        
        objective = cp.Maximize(
            (portfolio_return - self.risk_free_rate) / cp.sqrt(portfolio_risk)
        )
        
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        optimal_weights = pd.Series(weights.value, index=returns.columns)
        portfolio_ret = expected_returns @ weights.value
        portfolio_vol = np.sqrt(portfolio_risk.value)
        sharpe = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        portfolio_esg_score = aligned_scores.values @ weights.value
        
        results = {
            'weights': optimal_weights,
            'expected_return': portfolio_ret,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe,
            'esg_score': portfolio_esg_score
        }
        
        logger.info(f"ESG portfolio: Return={portfolio_ret:.2%}, Vol={portfolio_vol:.2%}, "
                   f"Sharpe={sharpe:.2f}, ESG={portfolio_esg_score:.1f}")
        
        return results


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download sample data
    tickers = ['ICLN', 'TAN', 'ENPH', 'FSLR', 'NEE']
    data = yf.download(tickers, start='2020-01-01', end='2024-12-31')['Close']
    returns = data.pct_change().dropna()
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer()
    
    # Mean-variance optimization
    mv_result = optimizer.mean_variance_optimization(returns)
    print("\nMean-Variance Optimization:")
    print(mv_result['weights'])
    
    # Risk parity
    rp_result = optimizer.risk_parity_optimization(returns)
    print("\nRisk Parity:")
    print(rp_result['weights'])
    
    # ESG-constrained (example ESG scores)
    esg_scores = pd.Series({
        'ICLN': 8.5, 'TAN': 8.0, 'ENPH': 7.5, 'FSLR': 8.2, 'NEE': 9.0
    })
    esg_result = optimizer.esg_constrained_optimization(returns, esg_scores)
    print("\nESG-Constrained:")
    print(esg_result['weights'])
