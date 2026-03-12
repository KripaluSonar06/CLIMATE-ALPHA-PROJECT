import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { HOLDINGS, SECTOR_ALLOCATION, ALLOCATION_TARGETS } from "@/data/constants";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { useState, useMemo } from "react";
import { Search, ArrowUpDown } from "lucide-react";
import { toast } from "sonner";

type SortKey = 'ticker' | 'shares' | 'currentPrice' | 'weight';

export default function Portfolio() {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("weight");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const filtered = useMemo(() => {
    let data = HOLDINGS.filter(h => h.ticker.toLowerCase().includes(search.toLowerCase()) || h.name.toLowerCase().includes(search.toLowerCase()));
    data.sort((a, b) => sortDir === "asc" ? (a[sortKey] > b[sortKey] ? 1 : -1) : (a[sortKey] < b[sortKey] ? 1 : -1));
    return data;
  }, [search, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir("desc"); }
  };

  const rebalanceData = ALLOCATION_TARGETS.map(a => ({ ...a, name: a.sector }));

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Portfolio</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie Chart */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Sector Allocation</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={SECTOR_ALLOCATION} cx="50%" cy="50%" innerRadius={60} outerRadius={110} dataKey="value" nameKey="name" stroke="none">
                      {SECTOR_ALLOCATION.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} formatter={(v: number) => [`${v}%`, 'Allocation']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-3 justify-center mt-2">
                {SECTOR_ALLOCATION.map(s => (
                  <div key={s.name} className="flex items-center gap-1.5 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                    <span className="text-muted-foreground">{s.name} ({s.value}%)</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Rebalancing */}
          <Card className="glass-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Rebalancing</CardTitle>
              <Button size="sm" onClick={() => toast.success("Rebalancing initiated")}>Rebalance</Button>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rebalanceData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(213 25% 25%)" />
                    <XAxis type="number" stroke="hsl(200 15% 73%)" fontSize={11} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" stroke="hsl(200 15% 73%)" fontSize={11} width={100} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(213 44% 18%)', border: '1px solid hsl(213 25% 25%)', borderRadius: '8px', color: 'hsl(210 20% 98%)' }} />
                    <Bar dataKey="current" fill="hsl(207 90% 54%)" name="Current" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="target" fill="hsl(145 100% 39%)" name="Target" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Holdings Table */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Holdings</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search ticker..." className="pl-9 h-9 bg-muted/50 border-border/50" value={search} onChange={e => setSearch(e.target.value)} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/50 text-muted-foreground">
                    {([['Ticker', 'ticker'], ['Shares', 'shares'], ['Avg Price', 'ticker'], ['Price', 'currentPrice'], ['P&L', 'ticker'], ['P&L %', 'ticker'], ['Weight', 'weight']] as const).map(([label, key]) => (
                      <th key={label} className="text-left py-3 px-2 font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort(key as SortKey)}>
                        <span className="flex items-center gap-1">{label}<ArrowUpDown className="h-3 w-3" /></span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(h => {
                    const pnl = (h.currentPrice - h.avgPrice) * h.shares;
                    const pnlPct = ((h.currentPrice - h.avgPrice) / h.avgPrice) * 100;
                    return (
                      <tr key={h.ticker} className="border-b border-border/30 hover:bg-accent/30 transition-colors">
                        <td className="py-3 px-2 font-medium">{h.ticker}</td>
                        <td className="py-3 px-2 tabular-nums">{h.shares}</td>
                        <td className="py-3 px-2 tabular-nums">${h.avgPrice.toFixed(2)}</td>
                        <td className="py-3 px-2 tabular-nums">${h.currentPrice.toFixed(2)}</td>
                        <td className={`py-3 px-2 tabular-nums font-medium ${pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
                          {pnl >= 0 ? '+' : ''}${pnl.toFixed(0)}
                        </td>
                        <td className={`py-3 px-2 tabular-nums font-medium ${pnlPct >= 0 ? 'text-profit' : 'text-loss'}`}>
                          {pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(1)}%
                        </td>
                        <td className="py-3 px-2 tabular-nums">{h.weight}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
