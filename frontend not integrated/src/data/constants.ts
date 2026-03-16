// Portfolio Overview
export const PORTFOLIO = {
  totalValue: 1247850,
  dailyPnL: 12450,
  dailyPnLPercent: 1.01,
  totalReturn: 24.79,
  sharpeRatio: 1.71,
  esgScore: 8.4,
  annualReturn: 18.3,
  volatility: 12.1,
  maxDrawdown: -8.4,
};

// Performance chart data
export const PERFORMANCE_DATA = Array.from({ length: 365 }, (_, i) => {
  const date = new Date(2024, 0, 1);
  date.setDate(date.getDate() + i);
  const base = 1000000;
  const portfolioGrowth = base * (1 + 0.25 * (i / 365)) + Math.sin(i / 20) * 20000 + Math.random() * 10000;
  const sp500Growth = base * (1 + 0.12 * (i / 365)) + Math.sin(i / 25) * 15000 + Math.random() * 8000;
  return {
    date: date.toISOString().split('T')[0],
    portfolio: Math.round(portfolioGrowth),
    sp500: Math.round(sp500Growth),
  };
});

// Holdings
export const HOLDINGS = [
  { ticker: 'ICLN', name: 'iShares Global Clean Energy', shares: 500, avgPrice: 23.30, currentPrice: 24.50, sector: 'Clean Energy ETF', esgScore: 8.7, weight: 9.8 },
  { ticker: 'ENPH', name: 'Enphase Energy', shares: 200, avgPrice: 129.20, currentPrice: 145.30, sector: 'Solar', esgScore: 9.1, weight: 23.3 },
  { ticker: 'FSLR', name: 'First Solar', shares: 150, avgPrice: 202.40, currentPrice: 198.20, sector: 'Solar', esgScore: 8.5, weight: 23.8 },
  { ticker: 'NEE', name: 'NextEra Energy', shares: 300, avgPrice: 63.40, currentPrice: 68.90, sector: 'Utilities', esgScore: 8.9, weight: 16.6 },
  { ticker: 'TAN', name: 'Invesco Solar ETF', shares: 400, avgPrice: 49.10, currentPrice: 52.30, sector: 'Solar ETF', esgScore: 8.3, weight: 16.8 },
  { ticker: 'PLUG', name: 'Plug Power', shares: 1000, avgPrice: 3.80, currentPrice: 3.95, sector: 'Hydrogen', esgScore: 7.8, weight: 3.2 },
  { ticker: 'BE', name: 'Bloom Energy', shares: 250, avgPrice: 12.50, currentPrice: 13.20, sector: 'Fuel Cells', esgScore: 8.0, weight: 2.6 },
  { ticker: 'SEDG', name: 'SolarEdge Technologies', shares: 80, avgPrice: 55.00, currentPrice: 52.80, sector: 'Solar', esgScore: 8.6, weight: 3.4 },
];

// Recent Trades
export const RECENT_TRADES = [
  { date: '2024-12-15', ticker: 'ENPH', side: 'Buy' as const, quantity: 50, price: 142.50, pnl: 140 },
  { date: '2024-12-14', ticker: 'FSLR', side: 'Sell' as const, quantity: 30, price: 199.80, pnl: -78 },
  { date: '2024-12-13', ticker: 'ICLN', side: 'Buy' as const, quantity: 100, price: 24.20, pnl: 30 },
  { date: '2024-12-12', ticker: 'NEE', side: 'Buy' as const, quantity: 75, price: 67.50, pnl: 105 },
  { date: '2024-12-11', ticker: 'TAN', side: 'Sell' as const, quantity: 50, price: 51.80, pnl: 135 },
  { date: '2024-12-10', ticker: 'PLUG', side: 'Buy' as const, quantity: 200, price: 3.75, pnl: 40 },
  { date: '2024-12-09', ticker: 'SEDG', side: 'Sell' as const, quantity: 20, price: 54.20, pnl: -16 },
  { date: '2024-12-08', ticker: 'BE', side: 'Buy' as const, quantity: 100, price: 12.80, pnl: 40 },
];

// Strategies
export const STRATEGIES = [
  {
    id: 'pairs',
    name: 'Pairs Trading',
    description: 'Statistical arbitrage between correlated clean energy stocks',
    status: 'Active' as const,
    return: 18.5,
    sharpe: 1.92,
    winRate: 64,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.6 + Math.random() * 3 })),
  },
  {
    id: 'ml-momentum',
    name: 'ML Momentum',
    description: 'LSTM-based momentum strategy with ESG signal overlay',
    status: 'Active' as const,
    return: 24.3,
    sharpe: 2.15,
    winRate: 58,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.8 + Math.random() * 4 })),
  },
  {
    id: 'factor-ls',
    name: 'Factor Long/Short',
    description: 'Multi-factor model combining value, momentum, and ESG scores',
    status: 'Active' as const,
    return: 15.7,
    sharpe: 1.65,
    winRate: 61,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.5 + Math.random() * 2.5 })),
  },
  {
    id: 'carbon-arb',
    name: 'Carbon Arbitrage',
    description: 'Trade spread between carbon credit markets and equities',
    status: 'Paused' as const,
    return: 8.2,
    sharpe: 1.12,
    winRate: 52,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.27 + Math.random() * 2 })),
  },
  {
    id: 'mean-rev',
    name: 'Mean Reversion',
    description: 'Bollinger band mean reversion on renewable energy sector ETFs',
    status: 'Active' as const,
    return: 12.1,
    sharpe: 1.43,
    winRate: 67,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.4 + Math.sin(i) * 2 })),
  },
  {
    id: 'sentiment',
    name: 'ESG Sentiment',
    description: 'NLP-driven trading based on ESG news sentiment analysis',
    status: 'Paused' as const,
    return: 6.8,
    sharpe: 0.95,
    winRate: 55,
    data: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100 + i * 0.22 + Math.random() * 1.5 })),
  },
];

// VaR Data
export const VAR_DATA = {
  var95: { percent: 2.4, value: 29948 },
  var99: { percent: 3.8, value: 47418 },
  cvar95: { percent: 3.1, value: 38683 },
};

// Stress Test Scenarios
export const STRESS_SCENARIOS = [
  { name: '2008 Crisis', impact: -32, severity: 'severe' },
  { name: 'COVID-19', impact: -18, severity: 'high' },
  { name: 'Climate 2°C', impact: -5, severity: 'mild' },
  { name: 'Climate 3°C', impact: -12, severity: 'moderate' },
  { name: 'Climate 4°C', impact: -22, severity: 'high' },
  { name: 'Carbon Tax', impact: -8, severity: 'moderate' },
];

// Correlation matrix
export const CORRELATION_MATRIX = {
  tickers: ['ICLN', 'ENPH', 'FSLR', 'NEE', 'TAN', 'PLUG'],
  data: [
    [1.0, 0.72, 0.68, 0.45, 0.91, 0.55],
    [0.72, 1.0, 0.78, 0.38, 0.69, 0.62],
    [0.68, 0.78, 1.0, 0.35, 0.65, 0.58],
    [0.45, 0.38, 0.35, 1.0, 0.42, 0.28],
    [0.91, 0.69, 0.65, 0.42, 1.0, 0.52],
    [0.55, 0.62, 0.58, 0.28, 0.52, 1.0],
  ],
};

// Drawdown data
export const DRAWDOWN_DATA = Array.from({ length: 365 }, (_, i) => {
  const date = new Date(2024, 0, 1);
  date.setDate(date.getDate() + i);
  let dd = 0;
  if (i > 50 && i < 80) dd = -(i - 50) * 0.28;
  else if (i > 150 && i < 200) dd = -(i - 150) * 0.168;
  else if (i > 280 && i < 310) dd = -(i - 280) * 0.14;
  else dd = -Math.random() * 1.5;
  return { date: date.toISOString().split('T')[0], drawdown: Math.max(dd, -8.4) };
});

// ESG Data
export const ESG_BREAKDOWN = {
  environmental: 8.8,
  social: 7.9,
  governance: 8.5,
  benchmark: 6.2,
};

export const CARBON_DATA = {
  portfolioIntensity: 42,
  benchmarkIntensity: 125,
  reductionPercent: 66,
  co2Avoided: 1250,
  renewableExposure: 87,
  cleanEnergyCompanies: 8,
};

// Factor exposures
export const FACTOR_EXPOSURES = [
  { factor: 'Value', portfolio: 0.35, benchmark: 0.22 },
  { factor: 'Momentum', portfolio: 0.62, benchmark: 0.28 },
  { factor: 'Quality', portfolio: 0.48, benchmark: 0.35 },
  { factor: 'ESG', portfolio: 0.85, benchmark: 0.42 },
  { factor: 'Size', portfolio: -0.15, benchmark: 0.10 },
  { factor: 'Volatility', portfolio: 0.28, benchmark: 0.45 },
];

// ML Model metrics
export const ML_METRICS = {
  rmse: 2.34,
  mae: 1.87,
  directionalAccuracy: 68.5,
};

export const ML_PREDICTIONS = Array.from({ length: 60 }, (_, i) => {
  const actual = 24 + Math.sin(i / 5) * 3 + i * 0.05 + Math.random() * 0.5;
  const predicted = actual + (Math.random() - 0.5) * 1.5;
  return { day: i + 1, actual: +actual.toFixed(2), predicted: +predicted.toFixed(2) };
});

// Sector allocation for pie chart
export const SECTOR_ALLOCATION = [
  { name: 'Solar', value: 50.5, color: '#00c853' },
  { name: 'Clean Energy ETF', value: 26.6, color: '#2196f3' },
  { name: 'Utilities', value: 16.6, color: '#4caf50' },
  { name: 'Hydrogen', value: 3.2, color: '#00bcd4' },
  { name: 'Fuel Cells', value: 2.6, color: '#009688' },
];

// Allocation targets for rebalancing
export const ALLOCATION_TARGETS = [
  { sector: 'Solar', current: 50.5, target: 45.0 },
  { sector: 'Clean Energy ETF', current: 26.6, target: 25.0 },
  { sector: 'Utilities', current: 16.6, target: 20.0 },
  { sector: 'Hydrogen', current: 3.2, target: 5.0 },
  { sector: 'Fuel Cells', current: 2.6, target: 5.0 },
];
