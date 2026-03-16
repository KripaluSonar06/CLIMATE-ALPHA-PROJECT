import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { STRATEGIES } from "@/data/constants";
import { LineChart, Line, ResponsiveContainer } from "recharts";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";

export default function Strategies() {
  const [strategies, setStrategies] = useState(STRATEGIES);

  const toggleStrategy = (id: string) => {
    setStrategies(prev => prev.map(s => s.id === id ? { ...s, status: s.status === 'Active' ? 'Paused' as const : 'Active' as const } : s));
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Trading Strategies</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage and monitor your quantitative strategies</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {strategies.map((strategy) => (
            <Dialog key={strategy.id}>
              <DialogTrigger asChild>
                <Card className="glass-card cursor-pointer hover:border-primary/30 transition-all hover:glow-green">
                  <CardHeader className="flex flex-row items-start justify-between pb-2">
                    <div>
                      <CardTitle className="text-base">{strategy.name}</CardTitle>
                      <p className="text-xs text-muted-foreground mt-1">{strategy.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={strategy.status === 'Active' ? 'default' : 'secondary'} className="text-xs">
                        {strategy.status}
                      </Badge>
                      <Switch
                        checked={strategy.status === 'Active'}
                        onCheckedChange={() => toggleStrategy(strategy.id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-16 mb-3">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={strategy.data}>
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke={strategy.status === 'Active' ? 'hsl(145 100% 39%)' : 'hsl(200 15% 73%)'}
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-xs text-muted-foreground">Return</p>
                        <p className="text-sm font-bold text-profit tabular-nums">+{strategy.return}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Sharpe</p>
                        <p className="text-sm font-bold tabular-nums">{strategy.sharpe}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Win Rate</p>
                        <p className="text-sm font-bold tabular-nums">{strategy.winRate}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </DialogTrigger>
              <DialogContent className="bg-card border-border max-w-lg">
                <DialogHeader>
                  <DialogTitle>{strategy.name}</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">{strategy.description}</p>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={strategy.data}>
                        <Line type="monotone" dataKey="value" stroke="hsl(145 100% 39%)" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'Return', value: `+${strategy.return}%` },
                      { label: 'Sharpe Ratio', value: strategy.sharpe.toString() },
                      { label: 'Win Rate', value: `${strategy.winRate}%` },
                      { label: 'Status', value: strategy.status },
                    ].map(m => (
                      <div key={m.label} className="bg-muted/50 rounded-lg p-3">
                        <p className="text-xs text-muted-foreground">{m.label}</p>
                        <p className="text-lg font-bold tabular-nums">{m.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
