import pandas as pd
import numpy as np
import ta
from backend.utils.logger import logger

class FeatureEngineer:
    def __init__(self):
        pass

    def _fix_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure OHLCV columns are 1D Series and handle MultiIndex"""
        result = df.copy()

        # Handle yfinance MultiIndex (e.g., ('Close', 'AAPL'))
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = result.columns.get_level_values(0)
        
        # Ensure result is a single-level index and select standard columns
        # If there are duplicate column names after flattening, take the first
        result = result.loc[:, ~result.columns.duplicated()]

        return result

    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding technical features...")
        result = df.copy()

        # .squeeze() ensures that if 'Close' is a 1-column DataFrame, it becomes a Series
        close = df['Close'].squeeze().astype(float)
        high = df['High'].squeeze().astype(float)
        low = df['Low'].squeeze().astype(float)
        volume = df['Volume'].squeeze().astype(float)

        # Moving averages
        result['sma_20'] = ta.trend.sma_indicator(close, window=20) ## 
        result['sma_50'] = ta.trend.sma_indicator(close, window=50)
        result['sma_200'] = ta.trend.sma_indicator(close, window=200)

        result['ema_12'] = ta.trend.ema_indicator(close, window=12)
        result['ema_26'] = ta.trend.ema_indicator(close, window=26)

        # MACD
        macd = ta.trend.MACD(close)
        result['macd'] = macd.macd()
        result['macd_signal'] = macd.macd_signal()
        result['macd_diff'] = macd.macd_diff()

        # RSI
        result['rsi_14'] = ta.momentum.rsi(close, window=14)

        # Bollinger
        bb = ta.volatility.BollingerBands(close)
        result['bb_high'] = bb.bollinger_hband()
        result['bb_mid'] = bb.bollinger_mavg()
        result['bb_low'] = bb.bollinger_lband()
        result['bb_width'] = bb.bollinger_wband()

        # ATR
        result['atr_14'] = ta.volatility.average_true_range(high, low, close, window=14)

        # ADX
        result['adx_14'] = ta.trend.adx(high, low, close, window=14)

        # Stochastic
        stoch = ta.momentum.StochasticOscillator(high, low, close)
        result['stoch_k'] = stoch.stoch()
        result['stoch_d'] = stoch.stoch_signal()

        # Volume indicators
        result['obv'] = ta.volume.on_balance_volume(close, volume)
        result['mfi_14'] = ta.volume.money_flow_index(high, low, close, volume, window=14)

        # CCI
        result['cci_20'] = ta.trend.cci(high, low, close, window=20)

        # Williams %R
        result['williams_r'] = ta.momentum.williams_r(high, low, close, lbp=14)

        return result

    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding price features...")
        result = df.copy()
        close = df['Close'].squeeze()

        result['returns'] = close.pct_change()
        result['log_returns'] = np.log(close / close.shift(1))

        for lag in [1, 2, 3, 5, 10]:
            result[f'returns_lag_{lag}'] = result['returns'].shift(lag)

        for window in [5, 10, 20, 60]:
            result[f'rolling_mean_{window}'] = close.rolling(window).mean()
            result[f'rolling_std_{window}'] = close.rolling(window).std()

        result['momentum_20'] = close / close.shift(20) - 1
        result['zscore_20'] = (close - close.rolling(20).mean()) / close.rolling(20).std()
        
        if 'sma_20' in result.columns:
            result['dist_sma_20'] = (close - result['sma_20']) / result['sma_20']

        return result

    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding volume features...")
        result = df.copy()
        volume = df['Volume'].squeeze()
        close = df['Close'].squeeze()

        result['volume_ratio_20'] = volume / volume.rolling(20).mean()
        result['volume_change'] = volume.pct_change()
        result['price_volume_corr_20'] = close.rolling(20).corr(volume)
        return result

    def add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding volatility features...")
        result = df.copy()
        returns = df['Close'].squeeze().pct_change()
        result['volatility_20'] = returns.rolling(20).std()
        result['vol_cluster_20'] = returns.rolling(20).std().rolling(20).std()
        return result

    def add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding momentum features...")
        result = df.copy()
        close = df['Close'].squeeze()
        result['roc_20'] = ta.momentum.roc(close, window=20)
        result['momentum_rank'] = close.pct_change(60).rank(pct=True)
        return result

    def add_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        returns = df['Close'].squeeze().pct_change()
        result['sharpe_20'] = returns.rolling(20).mean() / returns.rolling(20).std()
        return result

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Adding time features...")
        result = df.copy()
        result['day_of_week'] = df.index.dayofweek
        result['month'] = df.index.month
        result['day_sin'] = np.sin(2 * np.pi * result['day_of_week'] / 7)
        result['day_cos'] = np.cos(2 * np.pi * result['day_of_week'] / 7)
        return result

    def create_feature_set(self, df: pd.DataFrame, technical=True, price=True, 
                           volume=True, volatility=True, momentum=True, 
                           time=True) -> pd.DataFrame:
        """Full feature pipeline matching your notebook call signature"""
        
        # 1. Clean MultiIndex and ensure 1D columns
        result = self._fix_columns(df)

        # 2. Add features conditionally
        if technical:
            result = self.add_technical_features(result)
        if price:
            result = self.add_price_features(result)
        if volume:
            result = self.add_volume_features(result)
        if volatility:
            result = self.add_volatility_features(result)
        if momentum:
            result = self.add_momentum_features(result)
        
        # These were called by default in your script logic
        result = self.add_performance_features(result)
        
        if time:
            result = self.add_time_features(result)

        result = result.dropna()
        logger.info(f"Feature engineering complete: {len(result.columns)} features")
        return result