"""
Data collection module for market data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import time

from backend.utils.logger import logger


class DataCollector:
    """Collect and manage market data"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data collector
        
        Args:
            data_dir: Directory to store data
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def download_stock_data(self, 
                           tickers: List[str],
                           start_date: str = "2019-01-01",
                           end_date: Optional[str] = None,
                           interval: str = "1d") -> pd.DataFrame:
        """
        Download stock price data
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            interval: Data interval (1d, 1h, etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Downloading data for {len(tickers)} tickers from {start_date} to {end_date}")
        
        all_data = {}
        
        for ticker in tickers:
            try:
                logger.info(f"Downloading {ticker}...")
                data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    progress=False
                )
                
                if not data.empty:
                    all_data[ticker] = data
                    logger.info(f"✓ {ticker}: {len(data)} rows")
                else:
                    logger.warning(f"✗ {ticker}: No data returned")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"✗ {ticker}: Error - {str(e)}")
        
        # Combine all data
        if all_data:
            combined = pd.concat(all_data, axis=1, keys=all_data.keys())
            combined.index.name = 'Date'
            
            # Save to file
            filename = f"market_data_{start_date}_{end_date}.csv"
            filepath = self.raw_dir / filename
            combined.to_csv(filepath)
            logger.info(f"Saved data to {filepath}")
            
            return combined
        else:
            logger.error("No data downloaded")
            return pd.DataFrame()
    
    def get_clean_energy_universe(self) -> List[str]:
        """Get list of clean energy tickers"""
        return [
            # Clean Energy ETFs
            'ICLN',  # iShares Global Clean Energy
            'TAN',   # Invesco Solar
            'QCLN',  # First Trust NASDAQ Clean Edge
            'PBW',   # Invesco WilderHill Clean Energy
            'FAN',   # First Trust Global Wind Energy
            'ACES',  # ALPS Clean Energy
            
            # Clean Energy Stocks
            'ENPH',  # Enphase Energy
            'SEDG',  # SolarEdge
            'FSLR',  # First Solar
            'RUN',   # Sunrun
            'NEE',   # NextEra Energy
            'BEP',   # Brookfield Renewable Partners
            'PLUG',  # Plug Power
            'BE',    # Bloom Energy
            'NOVA',  # Sunnova Energy
            'ARRY',  # Array Technologies
        ]
    
    def get_traditional_energy_universe(self) -> List[str]:
        """Get list of traditional energy tickers"""
        return [
            # Traditional Energy ETFs
            'XLE',   # Energy Select Sector SPDR
            'XOP',   # SPDR S&P Oil & Gas Exploration
            'IEO',   # iShares U.S. Oil & Gas Exploration
            
            # Oil & Gas Stocks
            'XOM',   # Exxon Mobil
            'CVX',   # Chevron
            'COP',   # ConocoPhillips
            'SLB',   # Schlumberger
            'EOG',   # EOG Resources
            'MPC',   # Marathon Petroleum
            'PSX',   # Phillips 66
            'VLO',   # Valero Energy
            'OXY',   # Occidental Petroleum
            'HAL',   # Halliburton
        ]
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns from prices
        
        Args:
            prices: DataFrame with price data
        
        Returns:
            DataFrame with returns
        """
        return prices.pct_change().dropna()
    
    def calculate_log_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log returns from prices
        
        Args:
            prices: DataFrame with price data
        
        Returns:
            DataFrame with log returns
        """
        return np.log(prices / prices.shift(1)).dropna()
    
    def resample_data(self, data: pd.DataFrame, freq: str = 'M') -> pd.DataFrame:
        """
        Resample data to different frequency
        
        Args:
            data: DataFrame with time series data
            freq: Frequency ('D', 'W', 'M', etc.)
        
        Returns:
            Resampled DataFrame
        """
        return data.resample(freq).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
    
    def load_cached_data(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load cached data from file
        
        Args:
            filename: Name of the file
        
        Returns:
            DataFrame or None if not found
        """
        filepath = self.raw_dir / filename
        if filepath.exists():
            logger.info(f"Loading cached data from {filepath}")
            return pd.read_csv(filepath, index_col=0, parse_dates=True, header=[0, 1])
        return None
    
    def get_sp500_tickers(self) -> List[str]:
        """Get S&P 500 tickers (simplified list)"""
        return ['SPY', 'IVV', 'VOO']  # S&P 500 ETFs as proxy
    
    def download_benchmark(self, benchmark: str = 'SPY',
                          start_date: str = "2019-01-01",
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Download benchmark data
        
        Args:
            benchmark: Benchmark ticker (default: SPY)
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with benchmark data
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Downloading benchmark {benchmark}")
        
        data = yf.download(benchmark, start=start_date, end=end_date, progress=False)
        
        # Save
        filename = f"benchmark_{benchmark}_{start_date}_{end_date}.csv"
        filepath = self.raw_dir / filename
        data.to_csv(filepath)
        logger.info(f"Saved benchmark data to {filepath}")
        
        return data
    
    def download_full_universe(self, start_date: str = "2019-01-01",
                               end_date: Optional[str] = None):
        """
        Download data for full universe (clean + traditional energy)
        
        Args:
            start_date: Start date
            end_date: End date
        """
        clean_energy = self.get_clean_energy_universe()
        traditional_energy = self.get_traditional_energy_universe()
        benchmark = ['SPY', 'TLT', 'GLD']  # Benchmark + bonds + gold
        
        all_tickers = clean_energy + traditional_energy + benchmark
        
        logger.info(f"Downloading full universe: {len(all_tickers)} tickers")
        
        return self.download_stock_data(
            tickers=all_tickers,
            start_date=start_date,
            end_date=end_date
        )


if __name__ == "__main__":
    # Example usage
    collector = DataCollector()
    
    # Download full universe
    data = collector.download_full_universe(
        start_date="2019-01-01",
        end_date="2024-12-31"
    )
    
    print(f"\nDownloaded data shape: {data.shape}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
