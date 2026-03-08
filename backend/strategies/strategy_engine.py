"""
Advanced Strategy Engine - Combines multiple strategies with risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from backend.utils.logger import logger


class StrategyEngine:
    """
    Advanced strategy engine that combines multiple trading strategies
    with proper risk management, position sizing, and portfolio optimization
    """
    
    def __init__(self,
                 max_position_size: float = 0.10,
                 stop_loss_pct: float = 0.02,
                 max_portfolio_risk: float = 0.15,
                 rebalance_frequency: int = 5):
        """
        Initialize strategy engine
        
        Args:
            max_position_size: Maximum position size as fraction of portfolio (default: 10%)
            stop_loss_pct: Stop loss percentage (default: 2%)
            max_portfolio_risk: Maximum portfolio risk (default: 15%)
            rebalance_frequency: Rebalance every N days (default: 5)
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.max_portfolio_risk = max_portfolio_risk
        self.rebalance_frequency = rebalance_frequency
        
        logger.info(f"StrategyEngine initialized with max_position={max_position_size:.1%}, "
                   f"stop_loss={stop_loss_pct:.1%}")
    
    def apply_position_sizing(self,
                            signals: pd.Series,
                            returns: pd.Series,
                            method: str = 'volatility_target') -> pd.Series:
        """
        Apply intelligent position sizing to signals
        
        Args:
            signals: Raw trading signals (-1 to 1)
            returns: Historical returns for volatility calculation
            method: Position sizing method ('fixed', 'volatility_target', 'kelly')
        
        Returns:
            Sized positions
        """
        if method == 'fixed':
            # Fixed position size
            positions = signals * self.max_position_size
            
        elif method == 'volatility_target':
            # Target volatility position sizing
            rolling_vol = returns.rolling(20).std()
            target_vol = 0.15 / np.sqrt(252)  # 15% annual vol target
            
            # Scale positions inversely with volatility
            vol_scalar = target_vol / rolling_vol.fillna(rolling_vol.mean())
            vol_scalar = vol_scalar.clip(0.5, 2.0)  # Limit scaling
            
            positions = signals * self.max_position_size * vol_scalar
            
        elif method == 'kelly':
            # Kelly Criterion
            win_rate = (returns > 0).rolling(60).mean()
            avg_win = returns[returns > 0].rolling(60).mean()
            avg_loss = abs(returns[returns < 0].rolling(60).mean())
            
            # Kelly fraction
            kelly_fraction = win_rate - ((1 - win_rate) / (avg_win / avg_loss).replace([np.inf, -np.inf], 1))
            kelly_fraction = kelly_fraction.clip(0, 1) * 0.5  # Half Kelly
            
            positions = signals * kelly_fraction.fillna(self.max_position_size)
        
        else:
            positions = signals * self.max_position_size
        
        # Ensure within limits
        positions = positions.clip(-self.max_position_size, self.max_position_size)
        
        return positions
    
    def apply_stop_loss(self,
                       positions: pd.Series,
                       returns: pd.Series) -> pd.Series:
        """
        Apply stop loss to positions
        
        Args:
            positions: Position sizes
            returns: Asset returns
        
        Returns:
            Positions with stop loss applied
        """
        portfolio_value = (1 + (positions.shift(1) * returns).fillna(0)).cumprod()
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        
        # Exit all positions when drawdown exceeds stop loss
        stop_triggered = drawdown < -self.stop_loss_pct
        
        protected_positions = positions.copy()
        protected_positions[stop_triggered] = 0
        
        # Gradually re-enter after stop loss (50% after 5 days, full after 10 days)
        for i in range(len(stop_triggered)):
            if stop_triggered.iloc[i]:
                # Find when to re-enter
                future_idx = min(i + 5, len(stop_triggered) - 1)
                if future_idx < len(protected_positions):
                    protected_positions.iloc[future_idx] = positions.iloc[future_idx] * 0.5
                
                future_idx = min(i + 10, len(stop_triggered) - 1)
                if future_idx < len(protected_positions):
                    protected_positions.iloc[future_idx] = positions.iloc[future_idx]
        
        return protected_positions
    
    def detect_regime(self, returns: pd.Series, lookback: int = 60) -> pd.Series:
        """
        Detect market regime (bull/bear/sideways)
        
        Args:
            returns: Market returns
            lookback: Lookback period
        
        Returns:
            Regime multiplier (0.5 in bear/high vol, 1.0 in bull)
        """
        # Handle DataFrame input
        if isinstance(returns, pd.DataFrame):
            if returns.shape[1] == 1:
                returns = returns.iloc[:, 0]
            else:
                returns = returns.mean(axis=1)
        
        # Ensure clean Series with no multi-index
        if hasattr(returns, 'values'):
            returns = pd.Series(returns.values, index=returns.index)
        
        rolling_return = returns.rolling(lookback).mean() * 252  # Annualized
        rolling_vol = returns.rolling(lookback).std() * np.sqrt(252)
        
        # Bull market: positive returns and moderate volatility
        bull_market = (rolling_return > 0.05) & (rolling_vol < 0.30)
        
        # High volatility: reduce exposure
        high_vol = rolling_vol > rolling_vol.quantile(0.75)
        
        # Create regime multiplier
        regime_multiplier = pd.Series(1.0, index=returns.index)
        
        # Use .loc for safe boolean indexing
        bearish_or_high_vol = (~bull_market | high_vol).fillna(False)
        regime_multiplier.loc[bearish_or_high_vol] = 0.5
        
        return regime_multiplier
    
    def combine_strategies(self,
                          strategy_returns: Dict[str, pd.Series],
                          method: str = 'equal_weight') -> pd.Series:
        """
        Combine multiple strategy returns
        
        Args:
            strategy_returns: Dictionary of {strategy_name: returns_series}
            method: Combination method ('equal_weight', 'risk_parity', 'optimal')
        
        Returns:
            Combined strategy returns
        """
        # Align all returns
        returns_df = pd.DataFrame(strategy_returns)
        returns_df = returns_df.dropna()
        
        if len(returns_df) == 0:
            logger.warning("No overlapping returns data for strategy combination")
            return pd.Series()
        
        if method == 'equal_weight':
            # Simple equal weighting
            weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
            
        elif method == 'risk_parity':
            # Risk parity: weight inversely proportional to volatility
            vols = returns_df.std()
            inv_vols = 1 / vols
            weights = inv_vols / inv_vols.sum()
            
        elif method == 'optimal':
            # Mean-variance optimal (maximize Sharpe)
            mean_returns = returns_df.mean() * 252
            cov_matrix = returns_df.cov() * 252
            
            # Simple optimization: inverse variance weighting with return adjustment
            inv_var = 1 / np.diag(cov_matrix)
            return_adjustment = mean_returns / mean_returns.sum()
            
            weights = inv_var * return_adjustment
            weights = weights / weights.sum()
        
        else:
            weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
        
        # Combine returns
        combined_returns = (returns_df * weights).sum(axis=1)
        
        logger.info(f"Combined {len(strategy_returns)} strategies using {method}")
        logger.info(f"Strategy weights: {dict(weights.round(3))}")
        
        return combined_returns
    
    def create_enhanced_portfolio(self,
                                 prices: pd.DataFrame,
                                 strategy_signals: Dict[str, pd.Series],
                                 benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Create enhanced portfolio with all improvements
        
        Args:
            prices: DataFrame of asset prices
            strategy_signals: Dictionary of {strategy_name: signal_series}
            benchmark_returns: Benchmark returns for regime detection
        
        Returns:
            Dictionary with portfolio metrics and returns
        """
        logger.info("Creating enhanced portfolio...")
        
        # Clean benchmark returns if provided
        if benchmark_returns is not None:
            if isinstance(benchmark_returns, pd.DataFrame):
                if benchmark_returns.shape[1] == 1:
                    benchmark_returns = benchmark_returns.iloc[:, 0]
                else:
                    benchmark_returns = benchmark_returns.mean(axis=1)
            # Ensure clean Series
            benchmark_returns = pd.Series(benchmark_returns.values, index=benchmark_returns.index)
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Initialize results storage
        strategy_returns_dict = {}
        
        # Process each strategy
        for strategy_name, signals in strategy_signals.items():
            logger.info(f"Processing strategy: {strategy_name}")
            
            # Align signals with returns
            aligned_signals = signals.reindex(returns.index).fillna(0)
            
            # Apply position sizing
            positions = self.apply_position_sizing(
                aligned_signals,
                returns.mean(axis=1) if returns.shape[1] > 1 else returns.iloc[:, 0],
                method='volatility_target'
            )
            
            # Apply stop loss
            positions = self.apply_stop_loss(positions, returns.mean(axis=1) if returns.shape[1] > 1 else returns.iloc[:, 0])
            
            # Apply regime detection if benchmark provided
            if benchmark_returns is not None:
                regime_mult = self.detect_regime(benchmark_returns)
                positions = positions * regime_mult.reindex(positions.index).fillna(1.0)
            
            # Calculate strategy returns
            if returns.shape[1] == 1:
                strat_returns = positions.shift(1) * returns.iloc[:, 0]
            else:
                strat_returns = positions.shift(1) * returns.mean(axis=1)
            
            strategy_returns_dict[strategy_name] = strat_returns.fillna(0)
        
        # Combine strategies
        combined_returns = self.combine_strategies(
            strategy_returns_dict,
            method='risk_parity'
        )
        
        # Calculate portfolio metrics
        cumulative_returns = (1 + combined_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
        
        n_years = len(combined_returns) / 252
        annualized_return = (1 + total_return) ** (1 / n_years) - 1
        annualized_vol = combined_returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - 0.02) / annualized_vol if annualized_vol > 0 else 0
        
        # Max drawdown
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        results = {
            'combined_returns': combined_returns,
            'strategy_returns': strategy_returns_dict,
            'cumulative_returns': cumulative_returns,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'n_trades': (combined_returns != 0).sum(),
            'win_rate': (combined_returns > 0).sum() / (combined_returns != 0).sum()
        }
        
        logger.info(f"Enhanced Portfolio Performance:")
        logger.info(f"  Annualized Return: {annualized_return:.2%}")
        logger.info(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.info(f"  Max Drawdown: {max_drawdown:.2%}")
        
        return results


def create_simple_momentum_strategy(prices: pd.DataFrame,
                                   lookback: int = 20,
                                   holding_period: int = 5) -> pd.Series:
    """
    Create a simple momentum strategy
    
    Args:
        prices: Price data
        lookback: Lookback period for momentum
        holding_period: How long to hold positions
    
    Returns:
        Signal series
    """
    returns = prices.pct_change()
    
    # Calculate momentum
    momentum = returns.rolling(lookback).mean()
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[momentum > momentum.quantile(0.6)] = 1  # Long top 40%
    signals[momentum < momentum.quantile(0.4)] = -1  # Short bottom 40%
    
    # Hold for holding_period days
    signals = signals.rolling(holding_period).apply(lambda x: x.iloc[0] if len(x) > 0 else 0)
    
    return signals


def create_mean_reversion_strategy(prices: pd.DataFrame,
                                   lookback: int = 20,
                                   entry_threshold: float = 1.5) -> pd.Series:
    """
    Create a mean reversion strategy
    
    Args:
        prices: Price data
        lookback: Lookback period
        entry_threshold: Z-score threshold for entry
    
    Returns:
        Signal series
    """
    returns = prices.pct_change()
    
    # Calculate z-score
    rolling_mean = prices.rolling(lookback).mean()
    rolling_std = prices.rolling(lookback).std()
    z_score = (prices - rolling_mean) / rolling_std
    
    # Generate signals (buy when oversold, sell when overbought)
    signals = pd.Series(0, index=prices.index)
    signals[z_score < -entry_threshold] = 1  # Buy oversold
    signals[z_score > entry_threshold] = -1  # Sell overbought
    signals[abs(z_score) < 0.5] = 0  # Exit near mean
    
    return signals


def create_trend_following_strategy(prices: pd.DataFrame,
                                    fast_period: int = 10,
                                    slow_period: int = 30) -> pd.Series:
    """
    Create a dual moving average trend following strategy
    
    Args:
        prices: Price data
        fast_period: Fast MA period
        slow_period: Slow MA period
    
    Returns:
        Signal series
    """
    # Calculate moving averages
    fast_ma = prices.rolling(fast_period).mean()
    slow_ma = prices.rolling(slow_period).mean()
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[fast_ma > slow_ma] = 1  # Bullish
    signals[fast_ma < slow_ma] = -1  # Bearish
    
    return signals


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download sample data
    tickers = ['ICLN', 'TAN', 'ENPH']
    data = yf.download(tickers, start='2019-01-01', end='2024-12-31')
    prices = data['Close'].mean(axis=1)  # Average price
    
    # Create strategies
    momentum_signals = create_simple_momentum_strategy(prices)
    mean_reversion_signals = create_mean_reversion_strategy(prices)
    trend_signals = create_trend_following_strategy(prices)
    
    # Combine with strategy engine
    engine = StrategyEngine(
        max_position_size=0.15,
        stop_loss_pct=0.03,
        max_portfolio_risk=0.20
    )
    
    strategy_signals = {
        'Momentum': momentum_signals,
        'Mean Reversion': mean_reversion_signals,
        'Trend Following': trend_signals
    }
    
    # Get benchmark
    spy = yf.download('SPY', start='2019-01-01', end='2024-12-31')['Close']
    spy_returns = spy.pct_change().dropna()
    
    # Create enhanced portfolio
    results = engine.create_enhanced_portfolio(
        pd.DataFrame({'price': prices}),
        strategy_signals,
        benchmark_returns=spy_returns
    )
    
    print("\nEnhanced Portfolio Results:")
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Annualized Return: {results['annualized_return']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")