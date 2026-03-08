"""
AGGRESSIVE Strategy Engine - Actually Generates Returns!
This version removes over-conservative risk management and increases position sizes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from backend.utils.logger import logger


class AggressiveStrategyEngine:
    """
    Aggressive strategy engine that actually generates returns
    Removes overly conservative risk management
    """
    
    def __init__(self,
                 base_position_size: float = 0.30,
                 max_leverage: float = 1.5,
                 enable_risk_management: bool = True):
        """
        Initialize aggressive strategy engine
        
        Args:
            base_position_size: Base position size (default: 30%)
            max_leverage: Maximum leverage allowed (default: 1.5x)
            enable_risk_management: Whether to use any risk management
        """
        self.base_position_size = base_position_size
        self.max_leverage = max_leverage
        self.enable_risk_management = enable_risk_management
        
        logger.info(f"AggressiveStrategyEngine initialized with base_position={base_position_size:.1%}")
    
    def combine_strategies(self,
                          strategy_returns: Dict[str, pd.Series],
                          method: str = 'equal_weight') -> pd.Series:
        """
        Combine multiple strategy returns
        
        Args:
            strategy_returns: Dictionary of {strategy_name: returns_series}
            method: Combination method
        
        Returns:
            Combined strategy returns
        """
        returns_df = pd.DataFrame(strategy_returns)
        returns_df = returns_df.dropna()
        
        if len(returns_df) == 0:
            logger.warning("No overlapping returns data")
            return pd.Series()
        
        if method == 'equal_weight':
            weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
            
        elif method == 'volatility_inverse':
            # Weight by inverse volatility
            vols = returns_df.std()
            inv_vols = 1 / vols
            weights = inv_vols / inv_vols.sum()
            
        elif method == 'best_sharpe':
            # Weight by Sharpe ratio
            sharpes = (returns_df.mean() * 252) / (returns_df.std() * np.sqrt(252))
            sharpes = sharpes.clip(0)  # No negative weights
            if sharpes.sum() > 0:
                weights = sharpes / sharpes.sum()
            else:
                weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
        
        else:
            weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
        
        combined_returns = (returns_df * weights).sum(axis=1)
        
        logger.info(f"Combined {len(strategy_returns)} strategies using {method}")
        logger.info(f"Strategy weights: {dict(weights.round(3))}")
        
        return combined_returns
    
    def create_portfolio(self,
                        prices: pd.DataFrame,
                        strategy_signals: Dict[str, pd.Series]) -> Dict:
        """
        Create portfolio with actual returns
        
        Args:
            prices: DataFrame of asset prices
            strategy_signals: Dictionary of {strategy_name: signal_series}
        
        Returns:
            Dictionary with portfolio metrics and returns
        """
        logger.info("Creating aggressive portfolio...")
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Get single return series
        if returns.shape[1] == 1:
            asset_returns = returns.iloc[:, 0]
        else:
            asset_returns = returns.mean(axis=1)
        
        # Initialize results storage
        strategy_returns_dict = {}
        
        # Process each strategy
        for strategy_name, signals in strategy_signals.items():
            logger.info(f"Processing strategy: {strategy_name}")
            
            # Align signals with returns
            aligned_signals = signals.reindex(asset_returns.index).fillna(0)
            
            # Scale signals to position sizes
            positions = aligned_signals * self.base_position_size
            
            # Calculate strategy returns (LAG THE POSITIONS BY 1 DAY!)
            strat_returns = positions.shift(1) * asset_returns
            strat_returns = strat_returns.fillna(0)
            
            strategy_returns_dict[strategy_name] = strat_returns
            
            logger.info(f"  {strategy_name}: {(strat_returns != 0).sum()} trading days, "
                       f"avg daily return: {strat_returns.mean():.4%}")
        
        # Combine strategies
        combined_returns = self.combine_strategies(
            strategy_returns_dict,
            method='equal_weight'
        )
        
        # Calculate portfolio metrics
        if len(combined_returns) == 0:
            logger.error("No combined returns!")
            return {}
        
        cumulative_returns = (1 + combined_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
        
        n_years = len(combined_returns) / 252
        annualized_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0
        annualized_vol = combined_returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - 0.02) / annualized_vol if annualized_vol > 0 else 0
        
        # Max drawdown
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        results = {
            'combined_returns': combined_returns,
            'strategy_returns': strategy_returns_dict,
            'cumulative_returns': cumulative_returns,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'n_trades': (combined_returns != 0).sum(),
            'win_rate': (combined_returns > 0).sum() / (combined_returns != 0).sum() if (combined_returns != 0).sum() > 0 else 0
        }
        
        logger.info(f"Aggressive Portfolio Performance:")
        logger.info(f"  Total Return: {total_return:.2%}")
        logger.info(f"  Annualized Return: {annualized_return:.2%}")
        logger.info(f"  Annualized Vol: {annualized_vol:.2%}")
        logger.info(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.info(f"  Max Drawdown: {max_drawdown:.2%}")
        logger.info(f"  Calmar Ratio: {calmar_ratio:.2f}")
        logger.info(f"  Trading Days: {(combined_returns != 0).sum()}")
        
        return results


def create_aggressive_momentum_strategy(prices: pd.Series,
                                       fast_period: int = 10,
                                       slow_period: int = 50) -> pd.Series:
    """
    Create aggressive momentum strategy
    """
    # Calculate returns
    returns = prices.pct_change()
    
    # Fast and slow momentum
    fast_mom = returns.rolling(fast_period).mean()
    slow_mom = returns.rolling(slow_period).mean()
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    
    # Strong buy when both positive
    signals[(fast_mom > 0) & (slow_mom > 0)] = 1.0
    
    # Moderate buy when fast positive, slow negative
    signals[(fast_mom > 0) & (slow_mom < 0)] = 0.5
    
    # Sell when fast negative
    signals[fast_mom < 0] = -0.5
    
    return signals


def create_aggressive_mean_reversion_strategy(prices: pd.Series,
                                              lookback: int = 20,
                                              threshold: float = 1.0) -> pd.Series:
    """
    Create aggressive mean reversion strategy
    """
    # Calculate z-score
    rolling_mean = prices.rolling(lookback).mean()
    rolling_std = prices.rolling(lookback).std()
    z_score = (prices - rolling_mean) / rolling_std
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    
    # Buy when oversold
    signals[z_score < -threshold] = 1.0
    signals[z_score < -2*threshold] = 1.5  # Double down on extreme oversold
    
    # Sell when overbought
    signals[z_score > threshold] = -0.5
    signals[z_score > 2*threshold] = -1.0
    
    # Neutral zone
    signals[abs(z_score) < 0.3] = 0
    
    return signals


def create_aggressive_trend_strategy(prices: pd.Series,
                                     fast_ma: int = 20,
                                     slow_ma: int = 50) -> pd.Series:
    """
    Create aggressive trend following strategy
    """
    # Moving averages
    fast = prices.rolling(fast_ma).mean()
    slow = prices.rolling(slow_ma).mean()
    
    # Price position vs MA
    price_vs_fast = (prices - fast) / fast
    price_vs_slow = (prices - slow) / slow
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    
    # Strong uptrend
    signals[(fast > slow) & (price_vs_fast > 0) & (price_vs_slow > 0)] = 1.0
    
    # Moderate uptrend
    signals[(fast > slow) & ((price_vs_fast > 0) | (price_vs_slow > 0))] = 0.7
    
    # Weak uptrend
    signals[(fast > slow)] = 0.5
    
    # Downtrend
    signals[fast < slow] = -0.3
    
    return signals


def create_aggressive_breakout_strategy(prices: pd.Series,
                                        lookback: int = 20) -> pd.Series:
    """
    Create aggressive breakout strategy
    """
    # Calculate highs and lows
    rolling_high = prices.rolling(lookback).max()
    rolling_low = prices.rolling(lookback).min()
    rolling_range = rolling_high - rolling_low
    
    # Position in range
    position_in_range = (prices - rolling_low) / rolling_range
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    
    # Breakout above
    signals[prices > rolling_high.shift(1)] = 1.0
    
    # Near high
    signals[position_in_range > 0.8] = 0.7
    
    # Breakout below
    signals[prices < rolling_low.shift(1)] = -0.7
    
    # Near low
    signals[position_in_range < 0.2] = 0.5  # Contrarian
    
    return signals


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download data
    data = yf.download('ICLN', start='2019-01-01', end='2024-12-31')
    prices = data['Close']
    
    # Create strategies
    momentum = create_aggressive_momentum_strategy(prices)
    mean_rev = create_aggressive_mean_reversion_strategy(prices)
    trend = create_aggressive_trend_strategy(prices)
    breakout = create_aggressive_breakout_strategy(prices)
    
    # Run engine
    engine = AggressiveStrategyEngine(
        base_position_size=0.30,
        max_leverage=1.5
    )
    
    strategy_signals = {
        'Momentum': momentum,
        'Mean Reversion': mean_rev,
        'Trend': trend,
        'Breakout': breakout
    }
    
    results = engine.create_portfolio(
        pd.DataFrame({'price': prices}),
        strategy_signals
    )
    
    print("\nResults:")
    print(f"Annualized Return: {results['annualized_return']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")