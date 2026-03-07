"""
Value at Risk (VaR) and risk metrics calculator
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats
from arch import arch_model
from backend.utils.logger import logger


class RiskCalculator:
    """Calculate Value at Risk and other risk metrics"""
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize risk calculator
        
        Args:
            confidence_level: Confidence level for VaR (default: 95%)
        """
        self.confidence_level = confidence_level
        self.trading_days = 252
    
    def historical_var(self,
                      returns: pd.Series,
                      confidence: float = None) -> float:
        """
        Calculate Historical VaR
        
        Args:
            returns: Series of returns
            confidence: Confidence level (uses default if None)
        
        Returns:
            VaR value (positive number)
        """
        if confidence is None:
            confidence = self.confidence_level
        
        # Handle DataFrame input
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                raise ValueError("historical_var expects a Series, not a multi-column DataFrame")
        
        var = -np.percentile(returns.dropna(), (1 - confidence) * 100)
        
        # Ensure it's a scalar
        if isinstance(var, (pd.Series, np.ndarray)):
            var = float(var.item() if hasattr(var, 'item') else var[0])
        
        logger.debug(f"Historical VaR ({confidence:.0%}): {var:.4f}")
        
        return float(var)
    
    def parametric_var(self,
                      returns: pd.Series,
                      confidence: float = None) -> float:
        """
        Calculate Parametric VaR (assumes normal distribution)
        
        Args:
            returns: Series of returns
            confidence: Confidence level
        
        Returns:
            VaR value
        """
        if confidence is None:
            confidence = self.confidence_level
        
        # Handle DataFrame input
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                raise ValueError("parametric_var expects a Series, not a multi-column DataFrame")
        
        mean = returns.mean()
        std = returns.std()
        
        # Ensure they're scalars
        if isinstance(mean, pd.Series):
            mean = mean.iloc[0]
        if isinstance(std, pd.Series):
            std = std.iloc[0]
        
        # Z-score for confidence level
        z_score = stats.norm.ppf(1 - confidence)
        
        var = -(mean + z_score * std)
        
        logger.debug(f"Parametric VaR ({confidence:.0%}): {var:.4f}")
        
        return float(var)
    
    def monte_carlo_var(self,
                       returns: pd.Series,
                       n_simulations: int = 10000,
                       horizon: int = 1,
                       confidence: float = None) -> float:
        """
        Calculate Monte Carlo VaR
        
        Args:
            returns: Series of returns
            n_simulations: Number of Monte Carlo simulations
            horizon: Time horizon in days
            confidence: Confidence level
        
        Returns:
            VaR value
        """
        if confidence is None:
            confidence = self.confidence_level
        
        # Fit distribution
        mean = returns.mean()
        std = returns.std()
        
        # Ensure they're scalars
        if isinstance(mean, pd.Series):
            mean = mean.iloc[0]
        if isinstance(std, pd.Series):
            std = std.iloc[0]
        
        # Generate random scenarios
        simulated_returns = np.random.normal(
            mean * horizon,
            std * np.sqrt(horizon),
            n_simulations
        )
        
        # Calculate VaR
        var = -np.percentile(simulated_returns, (1 - confidence) * 100)
        
        logger.debug(f"Monte Carlo VaR ({confidence:.0%}, {horizon}d): {var:.4f}")
        
        return float(var)
    
    def conditional_var(self,
                       returns: pd.Series,
                       confidence: float = None) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall / CVaR)
        
        Args:
            returns: Series of returns
            confidence: Confidence level
        
        Returns:
            CVaR value
        """
        if confidence is None:
            confidence = self.confidence_level
        
        # Handle DataFrame input
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                raise ValueError("conditional_var expects a Series, not a multi-column DataFrame")
        
        var = self.historical_var(returns, confidence)
        
        # Average of losses beyond VaR
        tail_losses = returns[returns <= -var]
        
        if len(tail_losses) == 0:
            cvar = var  # If no losses beyond VaR, use VaR itself
        else:
            cvar = -tail_losses.mean()
            # Ensure it's a scalar
            if isinstance(cvar, pd.Series):
                cvar = cvar.iloc[0]
        
        logger.debug(f"Conditional VaR ({confidence:.0%}): {cvar:.4f}")
        
        return float(cvar)
    
    def calculate_all_var(self, returns: pd.Series,
                         confidence_levels: List[float] = [0.95, 0.99]) -> pd.DataFrame:
        """
        Calculate all VaR methods for multiple confidence levels
        
        Args:
            returns: Series of returns
            confidence_levels: List of confidence levels
        
        Returns:
            DataFrame with VaR values
        """
        results = []
        
        for conf in confidence_levels:
            results.append({
                'confidence': conf,
                'historical_var': self.historical_var(returns, conf),
                'parametric_var': self.parametric_var(returns, conf),
                'monte_carlo_var': self.monte_carlo_var(returns, confidence=conf),
                'conditional_var': self.conditional_var(returns, conf)
            })
        
        return pd.DataFrame(results)
    
    def garch_forecast(self,
                      returns: pd.Series,
                      horizon: int = 1,
                      p: int = 1,
                      q: int = 1) -> Tuple[float, float]:
        """
        Forecast volatility using GARCH model
        
        Args:
            returns: Series of returns
            horizon: Forecast horizon
            p: GARCH p parameter
            q: GARCH q parameter
        
        Returns:
            Tuple of (forecasted_mean, forecasted_volatility)
        """
        logger.info(f"Fitting GARCH({p},{q}) model...")
        
        # Fit GARCH model
        model = arch_model(
            returns * 100,  # Convert to percentage
            vol='Garch',
            p=p,
            q=q
        )
        
        fitted_model = model.fit(disp='off')
        
        # Forecast
        forecast = fitted_model.forecast(horizon=horizon)
        
        forecasted_mean = forecast.mean.iloc[-1, 0] / 100
        forecasted_var = forecast.variance.iloc[-1, 0] / 10000
        forecasted_vol = np.sqrt(forecasted_var)
        
        logger.info(f"GARCH forecast: mean={forecasted_mean:.4f}, "
                   f"vol={forecasted_vol:.4f}")
        
        return forecasted_mean, forecasted_vol
    
    def beta_calculation(self,
                        asset_returns: pd.Series,
                        market_returns: pd.Series) -> float:
        """
        Calculate beta vs market
        
        Args:
            asset_returns: Series of asset returns
            market_returns: Series of market returns
        
        Returns:
            Beta value
        """
        # Align returns
        aligned = pd.concat([asset_returns, market_returns], axis=1).dropna()
        
        if len(aligned) < 2:
            return np.nan
        
        # Calculate beta
        covariance = aligned.cov().iloc[0, 1]
        market_variance = aligned.iloc[:, 1].var()
        
        beta = covariance / market_variance if market_variance != 0 else np.nan
        
        return beta
    
    def stress_test(self,
                   returns: pd.Series,
                   portfolio_value: float,
                   scenarios: Dict[str, float]) -> pd.DataFrame:
        """
        Perform stress testing under various scenarios
        
        Args:
            returns: Series of returns
            portfolio_value: Current portfolio value
            scenarios: Dictionary of scenario names and shock sizes
        
        Returns:
            DataFrame with stress test results
        """
        logger.info(f"Running stress tests on ${portfolio_value:,.0f} portfolio...")
        
        results = []
        
        for scenario, shock in scenarios.items():
            # Calculate portfolio value after shock
            shocked_value = portfolio_value * (1 + shock)
            loss = portfolio_value - shocked_value
            loss_pct = -shock
            
            results.append({
                'scenario': scenario,
                'shock': shock,
                'final_value': shocked_value,
                'loss': loss,
                'loss_pct': loss_pct
            })
        
        stress_df = pd.DataFrame(results)
        
        logger.info(f"Stress test complete: {len(scenarios)} scenarios tested")
        
        return stress_df
    
    def correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix
        
        Args:
            returns: DataFrame with multiple asset returns
        
        Returns:
            Correlation matrix
        """
        return returns.corr()
    
    def rolling_volatility(self,
                          returns: pd.Series,
                          window: int = 20) -> pd.Series:
        """
        Calculate rolling volatility
        
        Args:
            returns: Series of returns
            window: Rolling window size
        
        Returns:
            Series of rolling volatility
        """
        return returns.rolling(window=window).std() * np.sqrt(self.trading_days)
    
    def maximum_drawdown(self, returns: pd.Series) -> Tuple[float, int]:
        """
        Calculate maximum drawdown and duration
        
        Args:
            returns: Series of returns
        
        Returns:
            Tuple of (max_drawdown, duration_days)
        """
        # Force conversion to clean numpy array and back to Series
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                values = returns.iloc[:, 0].values
            else:
                raise ValueError("maximum_drawdown expects a Series, not a multi-column DataFrame")
        else:
            values = returns.values
        
        # Create clean Series without any metadata
        clean_returns = pd.Series(values)
        
        # Cumulative returns
        cumulative = (1 + clean_returns).cumprod()
        
        # Running maximum
        running_max = cumulative.expanding().max()
        
        # Drawdown as simple calculation
        drawdown = (cumulative.values - running_max.values) / running_max.values
        drawdown = pd.Series(drawdown)
        
        # Maximum drawdown
        max_dd = float(drawdown.min())
        
        # Calculate duration using simple logic
        is_in_drawdown = (drawdown < 0).astype(int).values
        
        # Find consecutive drawdown periods
        max_duration = 0
        current_duration = 0
        
        for in_dd in is_in_drawdown:
            if in_dd == 1:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_dd, int(max_duration)
    
    def downside_deviation(self,
                          returns: pd.Series,
                          target: float = 0) -> float:
        """
        Calculate downside deviation
        
        Args:
            returns: Series of returns
            target: Target return threshold
        
        Returns:
            Downside deviation
        """
        downside_returns = returns[returns < target]
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_dev = downside_returns.std() * np.sqrt(self.trading_days)
        
        # Ensure it's a scalar
        if isinstance(downside_dev, pd.Series):
            downside_dev = downside_dev.iloc[0]
        
        return float(downside_dev)
    
    def tail_ratio(self, returns: pd.Series) -> float:
        """
        Calculate tail ratio (95th percentile / 5th percentile)
        
        Args:
            returns: Series of returns
        
        Returns:
            Tail ratio
        """
        p95 = np.percentile(returns, 95)
        p5 = np.percentile(returns, 5)
        
        # Ensure they're scalars
        if isinstance(p95, (pd.Series, np.ndarray)):
            p95 = float(p95.item() if hasattr(p95, 'item') else p95[0])
        if isinstance(p5, (pd.Series, np.ndarray)):
            p5 = float(p5.item() if hasattr(p5, 'item') else p5[0])
        
        tail_ratio = abs(p95 / p5) if p5 != 0 else np.inf
        
        return float(tail_ratio)
    
    def comprehensive_risk_report(self,
                                 returns: pd.Series,
                                 portfolio_value: float = 1000000) -> Dict:
        """
        Generate comprehensive risk report
        
        Args:
            returns: Series of returns
            portfolio_value: Portfolio value for VaR calculation
        
        Returns:
            Dictionary with all risk metrics
        """
        logger.info("Generating comprehensive risk report...")
        
        # Handle DataFrame input - convert to Series at the start
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                raise ValueError("comprehensive_risk_report expects a Series, not a multi-column DataFrame")
        
        # Ensure it's a clean Series
        returns = pd.Series(returns.values, index=returns.index)
        
        # VaR metrics
        var_95 = self.historical_var(returns, 0.95)
        var_99 = self.historical_var(returns, 0.99)
        cvar_95 = self.conditional_var(returns, 0.95)
        cvar_99 = self.conditional_var(returns, 0.99)
        
        # Volatility
        annual_vol = returns.std() * np.sqrt(self.trading_days)
        if isinstance(annual_vol, pd.Series):
            annual_vol = annual_vol.iloc[0]
        annual_vol = float(annual_vol)
        
        # Drawdown
        max_dd, dd_duration = self.maximum_drawdown(returns)
        
        # Other metrics
        downside_dev = self.downside_deviation(returns)
        tail_r = self.tail_ratio(returns)
        
        # Statistical moments
        skewness = stats.skew(returns.dropna())
        kurtosis = stats.kurtosis(returns.dropna())
        
        # Ensure all are scalars
        if isinstance(skewness, (pd.Series, np.ndarray)):
            skewness = float(skewness.item() if hasattr(skewness, 'item') else skewness[0])
        if isinstance(kurtosis, (pd.Series, np.ndarray)):
            kurtosis = float(kurtosis.item() if hasattr(kurtosis, 'item') else kurtosis[0])
        
        report = {
            'portfolio_value': float(portfolio_value),
            'annual_volatility': annual_vol,
            'var_95_pct': float(var_95),
            'var_95_dollar': float(var_95 * portfolio_value),
            'var_99_pct': float(var_99),
            'var_99_dollar': float(var_99 * portfolio_value),
            'cvar_95_pct': float(cvar_95),
            'cvar_95_dollar': float(cvar_95 * portfolio_value),
            'cvar_99_pct': float(cvar_99),
            'cvar_99_dollar': float(cvar_99 * portfolio_value),
            'max_drawdown': float(max_dd),
            'max_dd_duration': int(dd_duration),
            'downside_deviation': float(downside_dev),
            'tail_ratio': float(tail_r),
            'skewness': float(skewness),
            'kurtosis': float(kurtosis)
        }
        
        logger.info("Risk report complete")
        
        return report
    
    def print_risk_report(self, report: Dict):
        """
        Print formatted risk report
        
        Args:
            report: Risk report dictionary
        """
        print("\n" + "="*60)
        print("COMPREHENSIVE RISK REPORT")
        print("="*60)
        
        print(f"\nPortfolio Value: ${report['portfolio_value']:,.0f}")
        print(f"Annual Volatility: {report['annual_volatility']:.2%}")
        
        print(f"\nValue at Risk (VaR):")
        print(f"  95% VaR: {report['var_95_pct']:.2%} (${report['var_95_dollar']:,.0f})")
        print(f"  99% VaR: {report['var_99_pct']:.2%} (${report['var_99_dollar']:,.0f})")
        
        print(f"\nConditional VaR (Expected Shortfall):")
        print(f"  95% CVaR: {report['cvar_95_pct']:.2%} (${report['cvar_95_dollar']:,.0f})")
        print(f"  99% CVaR: {report['cvar_99_pct']:.2%} (${report['cvar_99_dollar']:,.0f})")
        
        print(f"\nDrawdown Metrics:")
        print(f"  Maximum Drawdown: {report['max_drawdown']:.2%}")
        print(f"  Max DD Duration: {report['max_dd_duration']:.0f} days")
        
        print(f"\nOther Metrics:")
        print(f"  Downside Deviation: {report['downside_deviation']:.2%}")
        print(f"  Tail Ratio: {report['tail_ratio']:.2f}")
        print(f"  Skewness: {report['skewness']:.2f}")
        print(f"  Kurtosis: {report['kurtosis']:.2f}")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download sample data
    data = yf.download('ICLN', start='2019-01-01', end='2024-12-31')
    returns = data['Close'].pct_change().dropna()
    
    # Initialize risk calculator
    risk_calc = RiskCalculator()
    
    # Generate comprehensive report
    report = risk_calc.comprehensive_risk_report(returns, portfolio_value=1000000)
    risk_calc.print_risk_report(report)
    
    # Stress testing
    scenarios = {
        '2008 Crisis': -0.35,
        'COVID-19': -0.25,
        'Climate 2°C': -0.10,
        'Climate 3°C': -0.20,
        'Carbon Tax': -0.15
    }
    
    stress_results = risk_calc.stress_test(returns, 1000000, scenarios)
    print("\nStress Test Results:")
    print(stress_results)