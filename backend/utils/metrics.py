"""
Performance metrics calculator for trading strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from scipy import stats


class PerformanceMetrics:
    """Calculate comprehensive performance metrics for trading strategies"""
    
    def __init__(self, returns: pd.Series, benchmark_returns: Optional[pd.Series] = None,
                 risk_free_rate: float = 0.02):
        """
        Initialize metrics calculator
        
        Args:
            returns: Series of strategy returns
            benchmark_returns: Series of benchmark returns (optional)
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        # Handle DataFrame input - convert to Series
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                raise ValueError("PerformanceMetrics expects a Series or single-column DataFrame")
        
        if benchmark_returns is not None and isinstance(benchmark_returns, pd.DataFrame):
            if benchmark_returns.shape[1] == 1:
                benchmark_returns = benchmark_returns.iloc[:, 0]
            else:
                raise ValueError("benchmark_returns expects a Series or single-column DataFrame")
        
        self.returns = returns
        self.benchmark_returns = benchmark_returns
        self.risk_free_rate = risk_free_rate
        self.trading_days = 252
    
    def total_return(self) -> float:
        """Calculate total cumulative return"""
        return (1 + self.returns).prod() - 1
    
    def annualized_return(self) -> float:
        """Calculate annualized return"""
        total_ret = self.total_return()
        n_years = len(self.returns) / self.trading_days
        return (1 + total_ret) ** (1 / n_years) - 1
    
    def annualized_volatility(self) -> float:
        """Calculate annualized volatility"""
        # Handle DataFrame
        returns = self.returns
        if isinstance(returns, pd.DataFrame):
            returns = returns.iloc[:, 0]
        
        vol = returns.std() * np.sqrt(self.trading_days)
        if isinstance(vol, pd.Series):
            vol = vol.iloc[0]
        return float(vol)
    
    def sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = self.annualized_return() - self.risk_free_rate
        return excess_returns / self.annualized_volatility()
    
    def sortino_ratio(self) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        excess_returns = self.annualized_return() - self.risk_free_rate
        downside_returns = self.returns[self.returns < 0]
        downside_std = downside_returns.std() * np.sqrt(self.trading_days)
        
        # Ensure scalar
        if isinstance(downside_std, pd.Series):
            downside_std = downside_std.iloc[0]
        downside_std = float(downside_std)
        
        return excess_returns / downside_std if downside_std != 0 else 0.0
    
    def calmar_ratio(self) -> float:
        """Calculate Calmar ratio (return / max drawdown)"""
        max_dd = self.max_drawdown()
        # max_dd is already a float from the fixed method
        return self.annualized_return() / abs(max_dd) if abs(max_dd) > 1e-10 else 0.0
    
    def max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        # Force clean 1D array
        if isinstance(self.returns, pd.DataFrame):
            values = self.returns.iloc[:, 0].values
        else:
            values = self.returns.values
        
        # Ensure 1D
        if values.ndim > 1:
            values = values.flatten()
        
        returns = pd.Series(values)
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        
        if isinstance(max_dd, pd.Series):
            max_dd = max_dd.iloc[0]
        
        return float(max_dd)
    
    def max_drawdown_duration(self) -> int:
        """Calculate maximum drawdown duration in days"""
        # Force clean 1D array
        if isinstance(self.returns, pd.DataFrame):
            values = self.returns.iloc[:, 0].values
        else:
            values = self.returns.values
        
        # Ensure 1D
        if values.ndim > 1:
            values = values.flatten()
        
        returns = pd.Series(values)
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative.values - running_max.values) / running_max.values
        drawdown = pd.Series(drawdown)
        
        # Find drawdown periods using simple loop (avoid groupby)
        is_in_drawdown = (drawdown < 0).astype(int).values
        
        max_duration = 0
        current_duration = 0
        
        for in_dd in is_in_drawdown:
            if in_dd == 1:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return int(max_duration)
    
    def win_rate(self) -> float:
        """Calculate win rate (% of positive returns)"""
        return (self.returns > 0).sum() / len(self.returns)
    
    def profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = self.returns[self.returns > 0].sum()
        gross_loss = abs(self.returns[self.returns < 0].sum())
        
        # Ensure scalars
        if isinstance(gross_profit, pd.Series):
            gross_profit = gross_profit.iloc[0]
        if isinstance(gross_loss, pd.Series):
            gross_loss = gross_loss.iloc[0]
        
        gross_profit = float(gross_profit)
        gross_loss = float(gross_loss)
        
        return gross_profit / gross_loss if gross_loss != 0 else np.inf
    
    def var(self, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk
        
        Args:
            confidence: Confidence level (default: 95%)
        """
        return np.percentile(self.returns, (1 - confidence) * 100)
    
    def cvar(self, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        
        Args:
            confidence: Confidence level (default: 95%)
        """
        var = self.var(confidence)
        tail_losses = self.returns[self.returns <= var]
        cvar_val = tail_losses.mean()
        
        if isinstance(cvar_val, pd.Series):
            cvar_val = cvar_val.iloc[0]
        
        return float(cvar_val) if not pd.isna(cvar_val) else 0.0
    
    def skewness(self) -> float:
        """Calculate return distribution skewness"""
        skew = stats.skew(self.returns.dropna())
        if isinstance(skew, (pd.Series, np.ndarray)):
            skew = float(skew.item() if hasattr(skew, 'item') else skew[0])
        return float(skew)
    
    def kurtosis(self) -> float:
        """Calculate return distribution kurtosis"""
        kurt = stats.kurtosis(self.returns.dropna())
        if isinstance(kurt, (pd.Series, np.ndarray)):
            kurt = float(kurt.item() if hasattr(kurt, 'item') else kurt[0])
        return float(kurt)
    
    def beta(self) -> Optional[float]:
        """Calculate beta vs benchmark"""
        if self.benchmark_returns is None:
            return None
        
        # Align returns
        aligned_returns = pd.DataFrame({
            'strategy': self.returns,
            'benchmark': self.benchmark_returns
        }).dropna()
        
        if len(aligned_returns) < 2:
            return None
        
        covariance = aligned_returns.cov().loc['strategy', 'benchmark']
        benchmark_variance = aligned_returns['benchmark'].var()
        
        # Ensure scalars
        if isinstance(covariance, pd.Series):
            covariance = covariance.iloc[0]
        if isinstance(benchmark_variance, pd.Series):
            benchmark_variance = benchmark_variance.iloc[0]
        
        covariance = float(covariance)
        benchmark_variance = float(benchmark_variance)
        
        return covariance / benchmark_variance if benchmark_variance != 0 else None
    
    def alpha(self) -> Optional[float]:
        """Calculate alpha vs benchmark"""
        if self.benchmark_returns is None:
            return None
        
        beta = self.beta()
        if beta is None:
            return None
        
        benchmark_annual_return = (1 + self.benchmark_returns).prod() ** (
            self.trading_days / len(self.benchmark_returns)
        ) - 1
        
        return self.annualized_return() - (
            self.risk_free_rate + beta * (benchmark_annual_return - self.risk_free_rate)
        )
    
    def information_ratio(self) -> Optional[float]:
        """Calculate information ratio vs benchmark"""
        if self.benchmark_returns is None:
            return None
        
        # Align returns
        aligned_returns = pd.DataFrame({
            'strategy': self.returns,
            'benchmark': self.benchmark_returns
        }).dropna()
        
        if len(aligned_returns) < 2:
            return None
        
        excess_returns = aligned_returns['strategy'] - aligned_returns['benchmark']
        tracking_error = excess_returns.std() * np.sqrt(self.trading_days)
        excess_mean = excess_returns.mean() * self.trading_days
        
        # Ensure scalars
        if isinstance(tracking_error, pd.Series):
            tracking_error = tracking_error.iloc[0]
        if isinstance(excess_mean, pd.Series):
            excess_mean = excess_mean.iloc[0]
        
        tracking_error = float(tracking_error)
        excess_mean = float(excess_mean)
        
        if tracking_error == 0:
            return None
        
        return excess_mean / tracking_error
    
    def treynor_ratio(self) -> Optional[float]:
        """Calculate Treynor ratio"""
        beta = self.beta()
        if beta is None or beta == 0:
            return None
        
        return (self.annualized_return() - self.risk_free_rate) / beta
    
    def get_all_metrics(self) -> Dict[str, float]:
        """Get all performance metrics as dictionary"""
        metrics = {
            'total_return': self.total_return(),
            'annualized_return': self.annualized_return(),
            'annualized_volatility': self.annualized_volatility(),
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'max_drawdown': self.max_drawdown(),
            'max_dd_duration': self.max_drawdown_duration(),
            'win_rate': self.win_rate(),
            'profit_factor': self.profit_factor(),
            'var_95': self.var(0.95),
            'cvar_95': self.cvar(0.95),
            'var_99': self.var(0.99),
            'cvar_99': self.cvar(0.99),
            'skewness': self.skewness(),
            'kurtosis': self.kurtosis(),
        }
        
        # Add benchmark-relative metrics if available
        if self.benchmark_returns is not None:
            metrics.update({
                'beta': self.beta(),
                'alpha': self.alpha(),
                'information_ratio': self.information_ratio(),
                'treynor_ratio': self.treynor_ratio(),
            })
        
        return metrics
    
    def print_summary(self):
        """Print formatted summary of all metrics"""
        metrics = self.get_all_metrics()
        
        print("\n" + "="*60)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*60)
        
        print(f"\nReturn Metrics:")
        print(f"  Total Return:        {metrics['total_return']:>10.2%}")
        print(f"  Annualized Return:   {metrics['annualized_return']:>10.2%}")
        print(f"  Annualized Vol:      {metrics['annualized_volatility']:>10.2%}")
        
        print(f"\nRisk-Adjusted Metrics:")
        print(f"  Sharpe Ratio:        {metrics['sharpe_ratio']:>10.2f}")
        print(f"  Sortino Ratio:       {metrics['sortino_ratio']:>10.2f}")
        print(f"  Calmar Ratio:        {metrics['calmar_ratio']:>10.2f}")
        
        print(f"\nDrawdown Metrics:")
        print(f"  Max Drawdown:        {metrics['max_drawdown']:>10.2%}")
        print(f"  Max DD Duration:     {metrics['max_dd_duration']:>10.0f} days")
        
        print(f"\nTrade Metrics:")
        print(f"  Win Rate:            {metrics['win_rate']:>10.2%}")
        print(f"  Profit Factor:       {metrics['profit_factor']:>10.2f}")
        
        print(f"\nRisk Metrics:")
        print(f"  VaR (95%):           {metrics['var_95']:>10.2%}")
        print(f"  CVaR (95%):          {metrics['cvar_95']:>10.2%}")
        print(f"  VaR (99%):           {metrics['var_99']:>10.2%}")
        print(f"  CVaR (99%):          {metrics['cvar_99']:>10.2%}")
        
        print(f"\nDistribution:")
        print(f"  Skewness:            {metrics['skewness']:>10.2f}")
        print(f"  Kurtosis:            {metrics['kurtosis']:>10.2f}")
        
        if self.benchmark_returns is not None:
            print(f"\nBenchmark-Relative:")
            print(f"  Beta:                {metrics.get('beta', 'N/A'):>10.2f}")
            print(f"  Alpha:               {metrics.get('alpha', 'N/A'):>10.2%}")
            print(f"  Information Ratio:   {metrics.get('information_ratio', 'N/A'):>10.2f}")
            print(f"  Treynor Ratio:       {metrics.get('treynor_ratio', 'N/A'):>10.2f}")
        
        print("="*60 + "\n")