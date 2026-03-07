"""
Feature engineering for quantitative models
"""

import pandas as pd
import numpy as np
import ta
from typing import Optional, List
from backend.utils.logger import logger


class FeatureEngineer:
    """Engineer features for ML models"""
    
    def __init__(self):
        """Initialize feature engineer"""
        pass
    
    def add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with technical features
        """
        logger.info("Adding technical features...")
        
        result = df.copy()
        
        # Simple Moving Averages
        result['sma_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        result['sma_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        result['sma_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        
        # Exponential Moving Averages
        result['ema_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        result['ema_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        result['macd'] = macd.macd()
        result['macd_signal'] = macd.macd_signal()
        result['macd_diff'] = macd.macd_diff()
        
        # RSI
        result['rsi_14'] = ta.momentum.rsi(df['Close'], window=14)
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        result['bb_high'] = bollinger.bollinger_hband()
        result['bb_mid'] = bollinger.bollinger_mavg()
        result['bb_low'] = bollinger.bollinger_lband()
        result['bb_width'] = bollinger.bollinger_wband()
        
        # ATR (Average True Range)
        result['atr_14'] = ta.volatility.average_true_range(
            df['High'], df['Low'], df['Close'], window=14
        )
        
        # ADX (Average Directional Index)
        result['adx_14'] = ta.trend.adx(df['High'], df['Low'], df['Close'], window=14)
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        result['stoch_k'] = stoch.stoch()
        result['stoch_d'] = stoch.stoch_signal()
        
        # On-Balance Volume
        result['obv'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        
        # Money Flow Index
        result['mfi_14'] = ta.volume.money_flow_index(
            df['High'], df['Low'], df['Close'], df['Volume'], window=14
        )
        
        # Commodity Channel Index
        result['cci_20'] = ta.trend.cci(df['High'], df['Low'], df['Close'], window=20)
        
        # Williams %R
        result['williams_r'] = ta.momentum.williams_r(
            df['High'], df['Low'], df['Close'], lbp=14
        )
        
        logger.info(f"Added {len(result.columns) - len(df.columns)} technical features")
        
        return result
    
    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price-based features
        
        Args:
            df: DataFrame with price data
        
        Returns:
            DataFrame with price features
        """
        logger.info("Adding price features...")
        
        result = df.copy()
        
        # Returns
        result['returns'] = df['Close'].pct_change()
        result['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Lagged returns
        for lag in [1, 2, 3, 5, 10]:
            result[f'returns_lag_{lag}'] = result['returns'].shift(lag)
        
        # Rolling statistics
        for window in [5, 10, 20, 60]:
            result[f'rolling_mean_{window}'] = df['Close'].rolling(window).mean()
            result[f'rolling_std_{window}'] = df['Close'].rolling(window).std()
            result[f'rolling_min_{window}'] = df['Close'].rolling(window).min()
            result[f'rolling_max_{window}'] = df['Close'].rolling(window).max()
        
        # Price momentum
        result['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        result['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        result['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        result['momentum_60'] = df['Close'] / df['Close'].shift(60) - 1
        
        # Distance from moving averages
        result['dist_sma_20'] = (df['Close'] - result['sma_20']) / result['sma_20']
        result['dist_sma_50'] = (df['Close'] - result['sma_50']) / result['sma_50']
        result['dist_sma_200'] = (df['Close'] - result['sma_200']) / result['sma_200']
        
        # High-Low range
        result['high_low_range'] = (df['High'] - df['Low']) / df['Close']
        result['close_open_range'] = (df['Close'] - df['Open']) / df['Open']
        
        logger.info(f"Added price features")
        
        return result
    
    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based features
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with volume features
        """
        logger.info("Adding volume features...")
        
        result = df.copy()
        
        # Volume ratios
        result['volume_ratio_5'] = df['Volume'] / df['Volume'].rolling(5).mean()
        result['volume_ratio_10'] = df['Volume'] / df['Volume'].rolling(10).mean()
        result['volume_ratio_20'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Volume change
        result['volume_change'] = df['Volume'].pct_change()
        
        # Price-Volume correlation
        result['price_volume_corr_20'] = df['Close'].rolling(20).corr(df['Volume'])
        
        logger.info(f"Added volume features")
        
        return result
    
    def add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volatility features
        
        Args:
            df: DataFrame with returns data
        
        Returns:
            DataFrame with volatility features
        """
        logger.info("Adding volatility features...")
        
        result = df.copy()
        
        if 'returns' not in result.columns:
            result['returns'] = df['Close'].pct_change()
        
        # Historical volatility
        for window in [5, 10, 20, 60]:
            result[f'volatility_{window}'] = result['returns'].rolling(window).std()
        
        # Parkinson volatility (using High-Low)
        result['parkinson_vol_20'] = np.sqrt(
            (1 / (4 * np.log(2))) * 
            ((np.log(df['High'] / df['Low']) ** 2).rolling(20).mean())
        )
        
        # Garman-Klass volatility
        result['gk_vol_20'] = np.sqrt(
            0.5 * (np.log(df['High'] / df['Low']) ** 2).rolling(20).mean() -
            (2 * np.log(2) - 1) * (np.log(df['Close'] / df['Open']) ** 2).rolling(20).mean()
        )
        
        logger.info(f"Added volatility features")
        
        return result
    
    def add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add momentum features
        
        Args:
            df: DataFrame with price data
        
        Returns:
            DataFrame with momentum features
        """
        logger.info("Adding momentum features...")
        
        result = df.copy()
        
        # ROC (Rate of Change)
        for period in [5, 10, 20, 60]:
            result[f'roc_{period}'] = ta.momentum.roc(df['Close'], window=period)
        
        # TSI (True Strength Index)
        result['tsi'] = ta.momentum.tsi(df['Close'])
        
        # Ultimate Oscillator
        result['uo'] = ta.momentum.ultimate_oscillator(
            df['High'], df['Low'], df['Close']
        )
        
        # Awesome Oscillator
        result['ao'] = ta.momentum.awesome_oscillator(df['High'], df['Low'])
        
        logger.info(f"Added momentum features")
        
        return result
    
    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features
        
        Args:
            df: DataFrame with datetime index
        
        Returns:
            DataFrame with time features
        """
        logger.info("Adding time features...")
        
        result = df.copy()
        
        # Extract time components
        result['day_of_week'] = df.index.dayofweek
        result['day_of_month'] = df.index.day
        result['month'] = df.index.month
        result['quarter'] = df.index.quarter
        result['year'] = df.index.year
        
        # Cyclical encoding
        result['day_sin'] = np.sin(2 * np.pi * result['day_of_week'] / 7)
        result['day_cos'] = np.cos(2 * np.pi * result['day_of_week'] / 7)
        result['month_sin'] = np.sin(2 * np.pi * result['month'] / 12)
        result['month_cos'] = np.cos(2 * np.pi * result['month'] / 12)
        
        # Is month end
        result['is_month_end'] = df.index.is_month_end.astype(int)
        result['is_month_start'] = df.index.is_month_start.astype(int)
        result['is_quarter_end'] = df.index.is_quarter_end.astype(int)
        
        logger.info(f"Added time features")
        
        return result
    
    def create_feature_set(self, df: pd.DataFrame,
                          technical: bool = True,
                          price: bool = True,
                          volume: bool = True,
                          volatility: bool = True,
                          momentum: bool = True,
                          time: bool = True) -> pd.DataFrame:
        """
        Create complete feature set
        
        Args:
            df: DataFrame with OHLCV data
            technical: Include technical indicators
            price: Include price features
            volume: Include volume features
            volatility: Include volatility features
            momentum: Include momentum features
            time: Include time features
        
        Returns:
            DataFrame with all features
        """
        result = df.copy()
        
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
        
        if time:
            result = self.add_time_features(result)
        
        # Drop NaN rows
        initial_rows = len(result)
        result = result.dropna()
        dropped_rows = initial_rows - len(result)
        
        logger.info(f"Feature engineering complete: {len(result.columns)} columns, "
                   f"dropped {dropped_rows} rows with NaN")
        
        return result
    
    def get_feature_importance(self, features: pd.DataFrame, target: pd.Series,
                             top_n: int = 20) -> pd.DataFrame:
        """
        Calculate feature importance using random forest
        
        Args:
            features: Feature DataFrame
            target: Target variable
            top_n: Number of top features to return
        
        Returns:
            DataFrame with feature importance
        """
        from sklearn.ensemble import RandomForestRegressor
        
        # Remove NaN
        data = pd.concat([features, target], axis=1).dropna()
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        
        # Train random forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Get importance
        importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance.head(top_n)