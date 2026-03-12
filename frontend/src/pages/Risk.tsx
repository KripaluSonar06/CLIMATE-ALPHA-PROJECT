import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VAR_DATA, STRESS_SCENARIOS, CORRELATION_MATRIX, DRAWDOWN_DATA } from "@/data/constants";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";

function VarGauge({ label, percent, value }: { label: string; percent: number; value: number }) {
  const angle = (percent / 5) * 180;
  return (
    <Card className="glass-card text-center">
      <CardContent className="pt-6">
        <div className="relative w-32 h-16 mx-auto mb-3 overflow-hidden">
          <svg viewBox="0 0 120 60" className="w-full">
            <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="hsl(213 25% 25%)" strokeWidth="8" strokeLinecap="round" />
            <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="url(#varGrad)" strokeWidth="8" strokeLinecap="round" strokeDasharray={`${angle * 0.87} 300`} />
            <defs><linearGradient id="varGrad"><stop offset="0%" stopColor="hsl(145 100% 39%)" /><stop offset="100%" stopColor="hsl(4 90% 58%)" /></linearGradient></defs>
          </svg>
        </div>
        <p className="text-2xl font-bold tabular-nums">{percent}%</p>
        <p className="text-xs text-muted-foreground">${value.toLocaleString()}</p>
        <p className="text-sm font-medium text-muted-foreground mt-1">{label}</p>
      </CardContent>
    </Card>
  );
}

function CorrelationHeatmap() {
  const { tickers, data } = CORRELATION_MATRIX;
  const getColor = (v: number) => {
    if (v >= 0.8) return 'hsl(4 90% 58%)';
    if (v >= 0.6) return 'hsl(25 90% 55%)';
    if (v >= 0.4) return 'hsl(45 100% 51%)';
    if (v >= 0.2) return 'hsl(145 60% 50%)';
    return 'hsl(207 90% 54%)';
  };

  return (
    <div className="overflow-x-auto">
      <table className="text-xs mx-auto">
        <thead>
          <tr>
            <th className="p-2" />
            {tickers.map(t => <th key={t} className="p-2 font-medium text-muted-foreground">{t}</th>)}
          </tr>
        </thead>
        <tbody>
          {tickers.map((t, i) => (
            <tr key={t}>
              <td className="p-2 font-medium text-muted-foreground">{t}</td>
              {data[i].map((v, j) => (
                <td key={j} className="p-1">
                  <div
                    className="w-12 h-10 rounded flex items-center justify-center font-medium tabular-nums"
                    style={{ backgroundColor: getColor(v), color: v > 0.6 ? 'hsl(210 20% 98%)' : 'hsl(216 50% 10%)' }}
                    title={`${tickers[i]} / ${tickers[j]}: ${v.toFixed(2)}`}
                  >
                    {v.toFixed(2)}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Risk() {
  const stressData = STRESS_SCENARIOS.map(s => ({
    ...s,
    fill: s.severity === 'severe' ? 'hsl(4 90% 58%)' : s.severity === 'high' ? 'hsl(25 90% 55%)' : s.severity === 'moderate' ? 'hsl(45 100% 51%)' : 'hsl(145 100% 39%)',
  }));

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Risk Management</h1>

        {/* VaR Gauges */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <VarGauge label="95% VaR" percent={VAR_DATA.var95.percent} value={VAR_DATA.var95.value} />
          <VarGauge label="99% VaR" percent={VAR_DATA.var99.percent} value={VAR_DATA.var99.value} />
          <VarGauge label="CVaR 95%" percent={VAR_DATA.cvar95.percent} value={VAR_DATA.cvar95.value} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Stress Test */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Stress Test Scenarios</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stressData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                    <XAxis type="number" stroke="hsl(200 15% 73%)" fontSize={11} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" stroke="hsl(200 15% 73%)" fontSize={11} width={100} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                    <Bar dataKey="impact" name="Impact" radius={[0, 4, 4, 0]}>
                      {stressData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Correlation Matrix */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Correlation Matrix</CardTitle></CardHeader>
            <CardContent>
              <CorrelationHeatmap />
            </CardContent>
          </Card>
        </div>

        {/* Drawdown Chart */}
        <Card className="glass-card">
          <CardHeader><CardTitle className="text-base">Portfolio Drawdown</CardTitle></CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={DRAWDOWN_DATA.filter((_, i) => i % 3 === 0)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                  <XAxis dataKey="date" stroke="hsl(200 15% 73%)" fontSize={11} tickFormatter={(v) => new Date(v).toLocaleDateString('en-US', { month: 'short' })} interval={20} />
                  <YAxis stroke="hsl(200 15% 73%)" fontSize={11} tickFormatter={v => `${v}%`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                  <Area type="monotone" dataKey="drawdown" stroke="hsl(4 90% 58%)" fill="hsl(4 90% 58% / 0.2)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

// Need to import Cell for the stress test bar colors
import { Cell } from "recharts";
