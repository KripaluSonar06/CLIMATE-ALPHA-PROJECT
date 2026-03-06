# 🚀 QUICK START GUIDE
## Climate-Alpha: Quantitative ESG Trading Platform

Get up and running in **10 minutes**!

---

## ⚡ Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- (Optional) Jupyter Notebook
- (Optional) API keys for Alpha Vantage, News API

---

## 📥 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/climate-alpha-quant.git
cd climate-alpha-quant
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages (may take 5-10 minutes).

### Step 4: Configure Environment

```bash
# Copy environment template
cp config/.env.example config/.env

# Edit with your API keys (optional for basic functionality)
nano config/.env  # or use any text editor
```

### Step 5: Run Setup

```bash
python scripts/setup.py
```

This creates necessary directories and initializes the project.

---

## 📊 Download Data

Download market data for the clean energy and traditional energy universe:

```bash
python scripts/download_data.py
```

This downloads:
- Clean energy ETFs and stocks (ICLN, TAN, ENPH, FSLR, etc.)
- Traditional energy ETFs and stocks (XLE, XOM, CVX, etc.)
- Benchmark data (SPY, TLT, GLD)

**Time**: ~5 minutes  
**Storage**: ~50MB

---

## 🎯 Run Your First Analysis

### Option 1: Jupyter Notebook (Recommended)

```bash
jupyter notebook notebooks/00_complete_demonstration.ipynb
```

This notebook demonstrates:
- ✅ Data loading and visualization
- ✅ Feature engineering
- ✅ LSTM price prediction
- ✅ Pairs trading strategy
- ✅ Portfolio optimization
- ✅ Risk management (VaR, stress testing)

### Option 2: Python Scripts

```bash
# Run pairs trading backtest
python -c "
from backend.data.collectors import DataCollector
from backend.strategies.pairs_trading import PairsTradingStrategy

collector = DataCollector()
data = collector.load_cached_data('market_data_2019-01-01_*.csv')
close_prices = data.xs('Close', axis=1, level=1)

strategy = PairsTradingStrategy()
pairs = strategy.find_cointegrated_pairs(close_prices)
print(f'Found {len(pairs)} cointegrated pairs')
"
```

---

## 🎨 Launch Dashboard

### Option 1: Use Lovable (Recommended for UI)

1. Go to [Lovable.dev](https://lovable.dev)
2. Copy the prompt from `frontend_instructions/LOVABLE_PROMPT.md`
3. Paste into Lovable
4. Click "Generate"
5. Get a beautiful, production-ready dashboard in minutes!

### Option 2: Local Dashboard (Coming Soon)

```bash
python scripts/run_dashboard.py
# Open browser to http://localhost:8050
```

---

## 🔬 Run Backtests

Test different quantitative strategies:

```bash
# Run all strategies
python scripts/run_backtest.py --strategy all

# Run specific strategy
python scripts/run_backtest.py --strategy pairs_trading

# With custom parameters
python scripts/run_backtest.py --strategy pairs_trading --capital 1000000
```

Results saved to `data/results/`

---

## 📈 View Results

### Performance Metrics

```python
from backend.utils.metrics import PerformanceMetrics
import pandas as pd

# Load your strategy returns
returns = pd.read_csv('data/results/strategy_returns.csv')

# Calculate metrics
metrics = PerformanceMetrics(returns['returns'])
metrics.print_summary()
```

Output:
```
=====================================
PERFORMANCE METRICS SUMMARY
=====================================
Return Metrics:
  Total Return:        24.79%
  Annualized Return:   18.30%
  Annualized Vol:      12.10%

Risk-Adjusted Metrics:
  Sharpe Ratio:        1.47
  Sortino Ratio:       1.82
  Calmar Ratio:        1.15
...
```

---

## 🎓 Learning Path

### Beginner
1. Run `notebooks/00_complete_demonstration.ipynb`
2. Explore data in `notebooks/01_data_exploration.ipynb`
3. Read `docs/STRATEGIES.md`

### Intermediate
1. Customize strategies in `backend/strategies/`
2. Add new features in `backend/data/features.py`
3. Experiment with different ML models

### Advanced
1. Deploy to production using Docker
2. Integrate with trading APIs
3. Build custom risk models
4. Add real-time data feeds

---

## 🐳 Docker Deployment (Optional)

```bash
# Build image
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📚 Project Structure

```
climate-alpha-quant/
├── backend/              # Core application code
│   ├── data/            # Data collection & processing
│   ├── models/          # ML models (LSTM, XGBoost)
│   ├── strategies/      # Trading strategies
│   ├── risk/            # Risk management & optimization
│   └── utils/           # Helper functions
├── notebooks/           # Jupyter notebooks for analysis
├── data/                # Data storage
│   ├── raw/            # Raw market data
│   ├── processed/      # Processed features
│   └── results/        # Backtest results
├── config/              # Configuration files
├── scripts/             # Utility scripts
├── docs/                # Documentation
└── frontend_instructions/ # Lovable UI instructions
```

---

## ⚙️ Common Tasks

### Update Data
```bash
python scripts/download_data.py
```

### Train New ML Model
```bash
python -c "
from backend.models.lstm_predictor import LSTMPredictor
predictor = LSTMPredictor()
# ... your training code ...
predictor.save('my_model')
"
```

### Run Risk Analysis
```bash
python -c "
from backend.risk.var_calculator import RiskCalculator
risk = RiskCalculator()
# ... your risk analysis ...
"
```

### Optimize Portfolio
```bash
python -c "
from backend.risk.portfolio_opt import PortfolioOptimizer
optimizer = PortfolioOptimizer()
# ... your optimization ...
"
```

---

## 🆘 Troubleshooting

### ImportError: No module named 'backend'
```bash
# Make sure you're in the project root
pwd  # Should show /path/to/climate-alpha-quant

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or in Python scripts
import sys
sys.path.append('.')
```

### API Rate Limits
- Yahoo Finance is free but rate-limited
- Use `time.sleep()` between requests
- Cache data locally after first download

### Memory Issues with LSTM
- Reduce `batch_size` in model training
- Use fewer features
- Train on smaller dataset

### Can't Find Data Files
```bash
# Check if data was downloaded
ls data/raw/

# If empty, run download script
python scripts/download_data.py
```

---

## 📖 Next Steps

1. **Read Documentation**:
   - [API Documentation](docs/API.md)
   - [Strategy Guide](docs/STRATEGIES.md)
   - [Deployment Guide](docs/DEPLOYMENT.md)

2. **Join Community**:
   - Star the repo ⭐
   - Report issues
   - Contribute improvements

3. **Build Your Own**:
   - Customize strategies
   - Add new data sources
   - Create your own ML models

---

## 🎯 Quick Wins

Want to see results immediately? Try these:

### 1. Generate Pairs Trading Signals (30 seconds)
```bash
jupyter notebook notebooks/00_complete_demonstration.ipynb
# Run cells 1-5
```

### 2. Calculate Portfolio Risk (30 seconds)
```bash
jupyter notebook notebooks/00_complete_demonstration.ipynb
# Run cells 1-2, then cell 13
```

### 3. Build Beautiful Dashboard (5 minutes)
- Copy `frontend_instructions/LOVABLE_PROMPT.md`
- Paste into Lovable.dev
- Done!

---

## 💡 Tips & Best Practices

1. **Start Small**: Test strategies on small date ranges first
2. **Version Control**: Commit frequently as you experiment
3. **Save Results**: Always save backtest results for comparison
4. **Document Changes**: Keep notes on what works and what doesn't
5. **Use Notebooks**: Great for exploration and visualization
6. **Production Code**: Move tested strategies to `backend/` modules

---

## 🎉 Success!

You now have a production-ready quantitative trading platform that:
- ✅ Downloads and processes financial data
- ✅ Engineers 100+ features
- ✅ Trains ML models for prediction
- ✅ Runs multiple trading strategies
- ✅ Optimizes portfolios with ESG constraints
- ✅ Calculates comprehensive risk metrics
- ✅ Generates beautiful reports and visualizations

**This platform addresses UN SDG 13 (Climate Action) and SDG 7 (Affordable Clean Energy) while showcasing advanced quantitative finance skills perfect for both IBM certification and quant internship applications!**

---

## 📧 Need Help?

- 📖 Check the [README.md](README.md)
- 🐛 Report issues on GitHub
- 💬 Ask questions in Discussions
- 📧 Email: your.email@example.com

---

**Happy Trading! 🚀📈🌍**
