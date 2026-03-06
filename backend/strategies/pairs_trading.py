"""
Pairs trading strategy using cointegration
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Optional
from statsmodels.tsa.stattools import coint, adfuller
from sklearn.linear_model import LinearRegression
from backend.utils.logger import logger


class PairsTradingStrategy:
    """Statistical arbitrage through pairs trading"""
    
    def __init__(self,
                 lookback_period: int = 252,
                 entry_zscore: float = 2.0,
                 exit_zscore: float = 0.5,
                 stop_loss_zscore: float = 3.5,
                 position_size: float = 0.05):
        """
        Initialize pairs trading strategy
        
        Args:
            lookback_period: Lookback window for calculating spread statistics
            entry_zscore: Z-score threshold for entry
            exit_zscore: Z-score threshold for exit
            stop_loss_zscore: Z-score for stop loss
            position_size: Position size as fraction of portfolio
        """
        self.lookback_period = lookback_period
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore
        self.stop_loss_zscore = stop_loss_zscore
        self.position_size = position_size
    
    def find_cointegrated_pairs(self,
                               data: pd.DataFrame,
                               significance: float = 0.05) -> List[Tuple[str, str, float]]:
        """
        Find cointegrated pairs in the universe
        
        Args:
            data: DataFrame with price data for multiple securities
            significance: Significance level for cointegration test
        
        Returns:
            List of (ticker1, ticker2, p_value) tuples
        """
        n = data.shape[1]
        pairs = []
        
        logger.info(f"Testing {n*(n-1)//2} potential pairs for cointegration...")
        
        for i in range(n):
            for j in range(i+1, n):
                ticker1 = data.columns[i]
                ticker2 = data.columns[j]
                
                # Get price series
                s1 = data[ticker1].dropna()
                s2 = data[ticker2].dropna()
                
                # Align dates
                aligned = pd.concat([s1, s2], axis=1).dropna()
                if len(aligned) < 20:  # Minimum data requirement
                    continue
                
                # Cointegration test
                score, p_value, _ = coint(aligned.iloc[:, 0], aligned.iloc[:, 1])
                
                if p_value < significance:
                    pairs.append((ticker1, ticker2, p_value))
                    logger.info(f"✓ Cointegrated pair found: {ticker1} - {ticker2} (p={p_value:.4f})")
        
        logger.info(f"Found {len(pairs)} cointegrated pairs")
        
        # Sort by p-value (strongest cointegration first)
        pairs.sort(key=lambda x: x[2])
        
        return pairs
    
    def calculate_hedge_ratio(self, s1: pd.Series, s2: pd.Series) -> float:
        """
        Calculate hedge ratio using linear regression
        
        Args:
            s1: Price series for stock 1
            s2: Price series for stock 2
        
        Returns:
            Hedge ratio (beta)
        """
        # Align series
        aligned = pd.concat([s1, s2], axis=1).dropna()
        
        # Linear regression: s1 = alpha + beta * s2
        X = aligned.iloc[:, 1].values.reshape(-1, 1)
        y = aligned.iloc[:, 0].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        hedge_ratio = model.coef_[0]
        
        return hedge_ratio
    
    def calculate_spread(self, s1: pd.Series, s2: pd.Series,
                        hedge_ratio: Optional[float] = None) -> pd.Series:
        """
        Calculate spread between two securities
        
        Args:
            s1: Price series for stock 1
            s2: Price series for stock 2
            hedge_ratio: Hedge ratio (calculated if not provided)
        
        Returns:
            Spread series
        """
        # Align series
        aligned = pd.concat([s1, s2], axis=1).dropna()
        
        # Calculate hedge ratio if not provided
        if hedge_ratio is None:
            hedge_ratio = self.calculate_hedge_ratio(
                aligned.iloc[:, 0],
                aligned.iloc[:, 1]
            )
        
        # Calculate spread
        spread = aligned.iloc[:, 0] - hedge_ratio * aligned.iloc[:, 1]
        
        return spread
    
    def calculate_zscore(self, spread: pd.Series, window: Optional[int] = None) -> pd.Series:
        """
        Calculate z-score of the spread
        
        Args:
            spread: Spread series
            window: Rolling window (uses lookback_period if not specified)
        
        Returns:
            Z-score series
        """
        if window is None:
            window = self.lookback_period
        
        # Rolling mean and std
        spread_mean = spread.rolling(window=window).mean()
        spread_std = spread.rolling(window=window).std()
        
        # Z-score
        zscore = (spread - spread_mean) / spread_std
        
        return zscore
    
    def generate_signals(self, s1: pd.Series, s2: pd.Series,
                        hedge_ratio: Optional[float] = None) -> pd.DataFrame:
        """
        Generate trading signals based on z-score
        
        Args:
            s1: Price series for stock 1
            s2: Price series for stock 2
            hedge_ratio: Hedge ratio (calculated if not provided)
        
        Returns:
            DataFrame with signals and positions
        """
        # Calculate spread and z-score
        spread = self.calculate_spread(s1, s2, hedge_ratio)
        zscore = self.calculate_zscore(spread)
        
        # Initialize signals
        signals = pd.DataFrame(index=zscore.index)
        signals['spread'] = spread
        signals['zscore'] = zscore
        signals['signal'] = 0
        signals['position_s1'] = 0
        signals['position_s2'] = 0
        
        # Entry signals
        # Long spread (buy s1, sell s2) when z-score < -entry_zscore
        signals.loc[zscore < -self.entry_zscore, 'signal'] = 1
        
        # Short spread (sell s1, buy s2) when z-score > entry_zscore
        signals.loc[zscore > self.entry_zscore, 'signal'] = -1
        
        # Exit signals (mean reversion)
        signals.loc[abs(zscore) < self.exit_zscore, 'signal'] = 0
        
        # Stop loss
        signals.loc[abs(zscore) > self.stop_loss_zscore, 'signal'] = 0
        
        # Convert signals to positions (forward fill)
        signals['position_s1'] = signals['signal']
        signals['position_s2'] = -signals['signal'] * (
            hedge_ratio if hedge_ratio else self.calculate_hedge_ratio(s1, s2)
        )
        
        return signals
    
    def backtest_pair(self, s1: pd.Series, s2: pd.Series,
                     initial_capital: float = 100000) -> Dict:
        """
        Backtest pairs trading strategy
        
        Args:
            s1: Price series for stock 1
            s2: Price series for stock 2
            initial_capital: Initial capital
        
        Returns:
            Dictionary with backtest results
        """
        # Calculate hedge ratio using first half of data
        split = len(s1) // 2
        hedge_ratio = self.calculate_hedge_ratio(s1[:split], s2[:split])
        
        logger.info(f"Backtesting pair with hedge ratio: {hedge_ratio:.4f}")
        
        # Generate signals
        signals = self.generate_signals(s1, s2, hedge_ratio)
        
        # Calculate returns
        returns_s1 = s1.pct_change()
        returns_s2 = s2.pct_change()
        
        # Align everything
        data = pd.concat([
            signals,
            returns_s1.rename('returns_s1'),
            returns_s2.rename('returns_s2')
        ], axis=1).dropna()
        
        # Calculate strategy returns
        data['strategy_returns'] = (
            data['position_s1'].shift(1) * data['returns_s1'] +
            data['position_s2'].shift(1) * data['returns_s2']
        ) * self.position_size
        
        # Calculate cumulative returns
        data['cumulative_returns'] = (1 + data['strategy_returns']).cumprod()
        data['portfolio_value'] = initial_capital * data['cumulative_returns']
        
        # Calculate metrics
        total_return = data['cumulative_returns'].iloc[-1] - 1
        annual_return = (1 + total_return) ** (252 / len(data)) - 1
        annual_vol = data['strategy_returns'].std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_vol if annual_vol > 0 else 0
        
        # Max drawdown
        cumulative = data['cumulative_returns']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (data['strategy_returns'] > 0).sum() / len(data)
        
        # Number of trades
        num_trades = (data['position_s1'].diff() != 0).sum()
        
        results = {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': num_trades,
            'hedge_ratio': hedge_ratio,
            'signals': signals,
            'backtest_data': data
        }
        
        logger.info(f"Backtest complete: Return={total_return:.2%}, Sharpe={sharpe_ratio:.2f}, "
                   f"Max DD={max_drawdown:.2%}, Trades={num_trades}")
        
        return results
    
    def test_stationarity(self, series: pd.Series) -> Tuple[bool, float]:
        """
        Test if spread is stationary using Augmented Dickey-Fuller test
        
        Args:
            series: Time series to test
        
        Returns:
            Tuple of (is_stationary, p_value)
        """
        result = adfuller(series.dropna())
        p_value = result[1]
        is_stationary = p_value < 0.05
        
        logger.info(f"Stationarity test: p-value={p_value:.4f}, "
                   f"stationary={is_stationary}")
        
        return is_stationary, p_value


if __name__ == "__main__":
    # Example usage
    import yfinance as yf
    
    # Download sample data
    tickers = ['ICLN', 'XLE', 'TAN', 'XOP']
    data = yf.download(tickers, start='2019-01-01', end='2024-12-31')['Close']
    
    # Initialize strategy
    strategy = PairsTradingStrategy()
    
    # Find cointegrated pairs
    pairs = strategy.find_cointegrated_pairs(data)
    
    if pairs:
        # Backtest best pair
        ticker1, ticker2, p_value = pairs[0]
        s1 = data[ticker1]
        s2 = data[ticker2]
        
        results = strategy.backtest_pair(s1, s2)
        
        print(f"\nBacktest Results for {ticker1} - {ticker2}:")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print(f"Number of Trades: {results['num_trades']}")
