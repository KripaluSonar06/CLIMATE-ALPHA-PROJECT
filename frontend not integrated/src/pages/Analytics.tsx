import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ML_PREDICTIONS, ML_METRICS, FACTOR_EXPOSURES, PERFORMANCE_DATA } from "@/data/constants";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";
import { MetricCard } from "@/components/MetricCard";
import { Brain, Target, TrendingUp } from "lucide-react";

export default function Analytics() {
  // Backtest data: create 3 strategy equity curves
  const backtestData = Array.from({ length: 52 }, (_, i) => ({
    week: i + 1,
    mlMomentum: +(100 * (1 + 0.24 * (i / 52)) + Math.sin(i / 4) * 3 + Math.random() * 2).toFixed(1),
    pairsTrading: +(100 * (1 + 0.18 * (i / 52)) + Math.cos(i / 5) * 2 + Math.random() * 1.5).toFixed(1),
    factorLS: +(100 * (1 + 0.15 * (i / 52)) + Math.sin(i / 6) * 1.5 + Math.random() * 1).toFixed(1),
  }));

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Analytics</h1>

        {/* ML Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard title="RMSE" value={ML_METRICS.rmse.toString()} icon={<Brain className="h-4 w-4 text-secondary" />} />
          <MetricCard title="MAE" value={ML_METRICS.mae.toString()} icon={<Target className="h-4 w-4 text-secondary" />} />
          <MetricCard title="Directional Accuracy" value={`${ML_METRICS.directionalAccuracy}%`} trend="up" icon={<TrendingUp className="h-4 w-4 text-primary" />} />
        </div>

        {/* ML Predictions */}
        <Card className="glass-card">
          <CardHeader><CardTitle className="text-base">LSTM Predictions vs Actual</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={ML_PREDICTIONS}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                  <XAxis dataKey="day" stroke="hsl(200 15% 73%)" fontSize={11} />
                  <YAxis stroke="hsl(200 15% 73%)" fontSize={11} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                  <Legend />
                  <Line type="monotone" dataKey="actual" stroke="hsl(207 90% 54%)" strokeWidth={2} dot={false} name="Actual" />
                  <Line type="monotone" dataKey="predicted" stroke="hsl(145 100% 39%)" strokeWidth={2} dot={false} name="Predicted" strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Factor Exposures */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Factor Exposures</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={FACTOR_EXPOSURES}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                    <XAxis dataKey="factor" stroke="hsl(200 15% 73%)" fontSize={11} />
                    <YAxis stroke="hsl(200 15% 73%)" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                    <Legend />
                    <Bar dataKey="portfolio" fill="hsl(145 100% 39%)" name="Portfolio" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="benchmark" fill="hsl(207 90% 54%)" name="Benchmark" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Backtest */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Backtest Equity Curves</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={backtestData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                    <XAxis dataKey="week" stroke="hsl(200 15% 73%)" fontSize={11} label={{ value: 'Week', position: 'bottom', fill: 'hsl(200 15% 73%)', fontSize: 10 }} />
                    <YAxis stroke="hsl(200 15% 73%)" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                    <Legend />
                    <Line type="monotone" dataKey="mlMomentum" stroke="hsl(145 100% 39%)" strokeWidth={2} dot={false} name="ML Momentum" />
                    <Line type="monotone" dataKey="pairsTrading" stroke="hsl(207 90% 54%)" strokeWidth={2} dot={false} name="Pairs Trading" />
                    <Line type="monotone" dataKey="factorLS" stroke="hsl(45 100% 51%)" strokeWidth={2} dot={false} name="Factor L/S" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
