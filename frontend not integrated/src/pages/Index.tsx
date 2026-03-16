import { DashboardLayout } from "@/components/DashboardLayout";
import { MetricCard } from "@/components/MetricCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PORTFOLIO, PERFORMANCE_DATA, RECENT_TRADES } from "@/data/constants";
import { TrendingUp, TrendingDown, Activity, Shield, Leaf, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useState } from "react";

const timeframes = ["1M", "3M", "6M", "1Y", "ALL"] as const;
const timeframeDays: Record<string, number> = { "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "ALL": 365 };

export default function Dashboard() {
  const [timeframe, setTimeframe] = useState<string>("1Y");
  const [tradesPage, setTradesPage] = useState(0);
  const perPage = 5;

  const chartData = PERFORMANCE_DATA.slice(-timeframeDays[timeframe]);
  const paginatedTrades = RECENT_TRADES.slice(tradesPage * perPage, (tradesPage + 1) * perPage);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Portfolio Overview */}
        <div className="flex flex-col md:flex-row gap-4 items-start">
          <Card className="glass-card glow-green flex-1">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Total Portfolio Value</p>
              <p className="text-4xl font-bold tabular-nums text-foreground">${PORTFOLIO.totalValue.toLocaleString()}</p>
              <div className="flex items-center gap-4 mt-3">
                <span className="text-profit flex items-center gap-1 text-sm font-medium">
                  <ArrowUpRight className="w-4 h-4" />
                  +${PORTFOLIO.dailyPnL.toLocaleString()} ({PORTFOLIO.dailyPnLPercent}%)
                </span>
                <Badge variant="outline" className="border-primary/30 text-primary">
                  Sharpe {PORTFOLIO.sharpeRatio}
                </Badge>
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card flex-1">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-1">Total Return</p>
              <p className="text-4xl font-bold tabular-nums text-profit">+{PORTFOLIO.totalReturn}%</p>
              <p className="text-xs text-muted-foreground mt-3">Since inception · 12 months</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Annual Return"
            value={`${PORTFOLIO.annualReturn}%`}
            trend="up"
            subtitle="↑ 2.1% vs benchmark"
            icon={<TrendingUp className="h-4 w-4 text-primary" />}
          />
          <MetricCard
            title="Volatility"
            value={`${PORTFOLIO.volatility}%`}
            trend="neutral"
            icon={<Activity className="h-4 w-4 text-secondary" />}
          >
            <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-secondary rounded-full" style={{ width: `${PORTFOLIO.volatility * 5}%` }} />
            </div>
          </MetricCard>
          <MetricCard
            title="Max Drawdown"
            value={`${PORTFOLIO.maxDrawdown}%`}
            trend="down"
            icon={<TrendingDown className="h-4 w-4 text-destructive" />}
          />
          <MetricCard
            title="ESG Score"
            value={`${PORTFOLIO.esgScore}/10`}
            trend="up"
            icon={<Leaf className="h-4 w-4 text-primary" />}
          >
            <Progress value={PORTFOLIO.esgScore * 10} className="mt-2 h-2 [&>div]:bg-primary" />
          </MetricCard>
        </div>

        {/* Performance Chart */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Portfolio Performance</CardTitle>
            <div className="flex gap-1">
              {timeframes.map((tf) => (
                <Button
                  key={tf}
                  variant={timeframe === tf ? "default" : "ghost"}
                  size="sm"
                  className="h-7 text-xs px-3"
                  onClick={() => setTimeframe(tf)}
                >
                  {tf}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                  <XAxis 
                    dataKey="date" 
                    stroke="hsl(200 15% 73%)" 
                    fontSize={11}
                    tickFormatter={(v) => new Date(v).toLocaleDateString('en-US', { month: 'short' })}
                    interval={Math.floor(chartData.length / 6)}
                  />
                  <YAxis 
                    stroke="hsl(200 15% 73%)" 
                    fontSize={11}
                    tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }}
                    labelFormatter={(v) => new Date(v).toLocaleDateString()}
                    formatter={(v: number) => [`$${v.toLocaleString()}`, '']}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="portfolio" stroke="hsl(145 100% 39%)" strokeWidth={2} dot={false} name="Portfolio" />
                  <Line type="monotone" dataKey="sp500" stroke="hsl(207 90% 54%)" strokeWidth={2} dot={false} name="S&P 500" strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Recent Trades */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-base">Recent Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/50 text-muted-foreground">
                    <th className="text-left py-3 px-2 font-medium">Date</th>
                    <th className="text-left py-3 px-2 font-medium">Ticker</th>
                    <th className="text-left py-3 px-2 font-medium">Side</th>
                    <th className="text-right py-3 px-2 font-medium">Qty</th>
                    <th className="text-right py-3 px-2 font-medium">Price</th>
                    <th className="text-right py-3 px-2 font-medium">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedTrades.map((trade, i) => (
                    <tr key={i} className="border-b border-border/30 hover:bg-accent/30 transition-colors">
                      <td className="py-3 px-2 tabular-nums">{trade.date}</td>
                      <td className="py-3 px-2 font-medium">{trade.ticker}</td>
                      <td className="py-3 px-2">
                        <Badge variant={trade.side === 'Buy' ? 'default' : 'destructive'} className="text-xs">
                          {trade.side}
                        </Badge>
                      </td>
                      <td className="py-3 px-2 text-right tabular-nums">{trade.quantity}</td>
                      <td className="py-3 px-2 text-right tabular-nums">${trade.price.toFixed(2)}</td>
                      <td className={`py-3 px-2 text-right tabular-nums font-medium ${trade.pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
                        {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" size="sm" disabled={tradesPage === 0} onClick={() => setTradesPage(p => p - 1)}>Previous</Button>
              <Button variant="ghost" size="sm" disabled={(tradesPage + 1) * perPage >= RECENT_TRADES.length} onClick={() => setTradesPage(p => p + 1)}>Next</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
