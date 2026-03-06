# LOVABLE FRONTEND INSTRUCTIONS
## Climate-Alpha Quantitative ESG Trading Platform

This document contains the complete prompt for generating the frontend UI using Lovable.

---

## PROMPT FOR LOVABLE

Create a professional quantitative finance dashboard for Climate-Alpha, a sustainable ESG trading platform. The dashboard should have a dark theme with green/blue accents representing clean energy.

### KEY PAGES & FEATURES:

#### 1. DASHBOARD (Home Page)
- **Portfolio Overview Card**:
  - Total portfolio value with animated counter
  - Daily P&L (green/red)
  - Total return percentage
  - Sharpe ratio badge
  
- **Performance Chart**:
  - Line chart showing portfolio value over time
  - Comparison with S&P 500 benchmark
  - Toggle between 1M, 3M, 6M, 1Y, ALL timeframes
  - Interactive tooltips with date and value
  
- **Quick Stats Grid** (4 cards):
  - Annual Return (with trend arrow)
  - Volatility (with risk meter visual)
  - Max Drawdown (with red highlight)
  - ESG Score (with green progress bar 0-10)
  
- **Recent Trades Table**:
  - Columns: Date, Ticker, Side (Buy/Sell), Quantity, Price, P&L
  - Color-coded rows (green for profitable, red for losses)
  - Pagination

#### 2. STRATEGIES PAGE
- **Strategy Cards** (Grid layout):
  Each card shows:
  - Strategy name (e.g., "Pairs Trading", "ML Momentum", "Factor Long/Short")
  - Status badge (Active/Paused)
  - Performance metrics: Return, Sharpe, Win Rate
  - Mini chart of strategy returns
  - Toggle switch to enable/disable
  
- **Strategy Details Modal** (on card click):
  - Detailed performance metrics
  - Parameters configuration
  - Historical backtest results chart
  - Risk metrics

#### 3. PORTFOLIO PAGE
- **Asset Allocation Pie Chart**:
  - Interactive donut chart
  - Hover shows ticker, allocation %, value
  - Color-coded by sector (Clean Energy green, Traditional red)
  
- **Holdings Table**:
  - Columns: Ticker, Shares, Avg Price, Current Price, P&L, P&L %, Weight
  - Sortable columns
  - Search/filter functionality
  
- **Rebalancing Section**:
  - Target vs Current allocation comparison bars
  - "Rebalance" button
  - Shows required trades to rebalance

#### 4. RISK MANAGEMENT PAGE
- **VaR Gauges** (Semi-circle gauges):
  - 95% VaR
  - 99% VaR
  - CVaR
  - Each showing percentage and dollar value
  
- **Stress Test Results**:
  - Bar chart showing portfolio value under different scenarios
  - Scenarios: 2008 Crisis, COVID-19, Climate 2°C/3°C/4°C, Carbon Tax
  - Color gradient from green (mild) to red (severe)
  
- **Correlation Matrix Heatmap**:
  - Interactive heatmap of asset correlations
  - Color scale from blue (negative) to red (positive)
  
- **Drawdown Chart**:
  - Area chart showing drawdown over time
  - Highlighted max drawdown period

#### 5. ESG IMPACT PAGE
- **ESG Score Card**:
  - Large circular progress indicator (0-10)
  - Breakdown: Environmental, Social, Governance sub-scores
  - Comparison with benchmark
  
- **Carbon Footprint**:
  - Portfolio carbon intensity vs benchmark
  - Reduction percentage badge
  - Trend chart over time
  
- **SDG Alignment**:
  - Icons for SDG 7 and SDG 13
  - Impact metrics:
    - Renewable energy exposure %
    - Clean energy companies supported
    - Estimated CO2 avoided (tons)
  
- **ESG Holdings Table**:
  - Companies ranked by ESG score
  - Shows ticker, name, ESG score (0-10), sector
  - Green highlight for top performers

#### 6. ANALYTICS PAGE
- **ML Model Performance**:
  - LSTM prediction accuracy chart
  - Actual vs Predicted prices comparison
  - Model metrics: RMSE, MAE, Directional Accuracy
  
- **Factor Analysis**:
  - Bar chart of factor exposures
  - Factors: Value, Momentum, Quality, ESG
  - Comparison with benchmark
  
- **Backtesting Results**:
  - Equity curve comparison (multiple strategies)
  - Key metrics table
  - Monte Carlo simulation results

#### 7. SETTINGS PAGE
- **Strategy Parameters**:
  - Sliders and inputs for:
    - Position sizing
    - Stop loss levels
    - Rebalancing frequency
  - Save/Reset buttons
  
- **Risk Limits**:
  - Max position size
  - Max portfolio leverage
  - VaR limits
  
- **API Configuration**:
  - Input fields for API keys (masked)
  - Test connection button

---

### DESIGN REQUIREMENTS:

**Color Scheme**:
- Background: Dark navy (#0a1929)
- Cards: Slightly lighter navy (#132f4c)
- Primary: Green (#00c853) for positive/clean energy
- Secondary: Blue (#2196f3) for neutral/info
- Accent: Red (#f44336) for negative/traditional energy
- Text: White (#ffffff) and light gray (#b0bec5)

**Typography**:
- Font: Inter or similar modern sans-serif
- Headers: Bold, 24-32px
- Body: Regular, 14-16px
- Metrics: Tabular numbers, 18-24px

**Components**:
- Modern cards with subtle shadows
- Smooth animations on hover
- Loading skeletons for data
- Toast notifications for actions
- Responsive grid layout (adapts to mobile)

**Charts Library**: Use Recharts or Chart.js
- Line charts for performance
- Pie/Donut for allocation
- Bar charts for comparisons
- Gauges for risk metrics
- Heatmaps for correlations

**Navigation**:
- Sidebar with icons + labels
- Top bar with:
  - Logo (Climate-Alpha with leaf/chart icon)
  - Portfolio selector dropdown
  - User profile dropdown
  - Notifications bell icon

**Data Refresh**:
- Auto-refresh every 5 seconds for live data
- Manual refresh button
- Last updated timestamp

---

### INTERACTIVE ELEMENTS:

1. **Tooltips**: Show detailed info on hover for all charts
2. **Modals**: For strategy details, trade confirmation, settings
3. **Dropdowns**: Time period selection, portfolio selection
4. **Toggles**: Enable/disable strategies, switch views
5. **Search**: Filter holdings, search tickers
6. **Sorting**: Click column headers to sort tables
7. **Export**: Download buttons for reports (CSV, PDF)

---

### RESPONSIVE DESIGN:
- Desktop (1920x1080): Full 3-column grid
- Tablet (768x1024): 2-column grid
- Mobile (375x812): Single column, bottom nav

---

### SAMPLE DATA (Use for prototype):

**Portfolio**:
- Value: $1,247,850
- Daily P&L: +$12,450 (+1.01%)
- Total Return: +24.79%
- Sharpe Ratio: 1.71
- ESG Score: 8.4/10

**Holdings**:
- ICLN: 500 shares, $24.50, +5.2%
- ENPH: 200 shares, $145.30, +12.4%
- FSLR: 150 shares, $198.20, -2.1%
- NEE: 300 shares, $68.90, +8.7%
- TAN: 400 shares, $52.30, +6.5%

**VaR**:
- 95% VaR: 2.4% ($29,948)
- 99% VaR: 3.8% ($47,418)
- CVaR 95%: 3.1% ($38,683)

---

### LOVABLE SPECIFIC INSTRUCTIONS:

1. Create a multi-page SPA using React Router
2. Use Tailwind CSS for styling with custom dark theme
3. Implement all charts using Recharts
4. Add smooth page transitions
5. Include loading states for all async operations
6. Make all cards and components reusable
7. Add proper TypeScript types
8. Include sample data in separate constants file
9. Make it production-ready and visually stunning

**Technical Stack**:
- React 18+
- TypeScript
- Tailwind CSS
- Recharts
- React Router
- Lucide Icons
- shadcn/ui components

Create this as a complete, deployable application with all pages, components, and functionality. Focus on making it look professional and suitable for presenting to investors or in a portfolio.

---

END OF LOVABLE PROMPT
