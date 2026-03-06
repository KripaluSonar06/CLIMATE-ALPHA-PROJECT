"""
Download all required market data
"""

import sys
sys.path.append('.')

from backend.data.collectors import DataCollector
from backend.utils.logger import logger
from datetime import datetime


def main():
    """Download all market data"""
    
    print("\n" + "="*60)
    print("CLIMATE-ALPHA DATA DOWNLOAD")
    print("="*60 + "\n")
    
    # Initialize collector
    collector = DataCollector()
    
    # Date range
    start_date = "2019-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Downloading data from {start_date} to {end_date}")
    
    # Download full universe
    print("\n1. Downloading full universe...")
    data = collector.download_full_universe(
        start_date=start_date,
        end_date=end_date
    )
    
    if data.empty:
        logger.error("Failed to download data")
        return
    
    print(f"\n✓ Downloaded {data.shape[0]} rows, {data.shape[1]} columns")
    print(f"  Tickers: {data.columns.get_level_values(0).unique().tolist()}")
    
    # Download benchmark
    print("\n2. Downloading benchmark (SPY)...")
    benchmark = collector.download_benchmark(
        benchmark='SPY',
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"✓ Downloaded {len(benchmark)} rows for SPY")
    
    print("\n" + "="*60)
    print("DATA DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"\nData saved to: data/raw/")
    print(f"\nNext steps:")
    print("1. Run: jupyter notebook notebooks/00_complete_demonstration.ipynb")
    print("2. Or explore the data in your own notebook")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
