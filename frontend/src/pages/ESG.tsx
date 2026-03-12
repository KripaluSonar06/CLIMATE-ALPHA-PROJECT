import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { PORTFOLIO, ESG_BREAKDOWN, CARBON_DATA, HOLDINGS } from "@/data/constants";
import { Leaf, Wind, Zap, Globe } from "lucide-react";

export default function ESG() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">ESG Impact</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* ESG Score Card */}
          <Card className="glass-card glow-green">
            <CardHeader><CardTitle className="text-base">Overall ESG Score</CardTitle></CardHeader>
            <CardContent className="flex flex-col items-center">
              <div className="relative w-36 h-36 mb-4">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(213 25% 25%)" strokeWidth="8" />
                  <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(145 100% 39%)" strokeWidth="8" strokeLinecap="round" strokeDasharray={`${PORTFOLIO.esgScore * 26.4} 264`} />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold">{PORTFOLIO.esgScore}</span>
                  <span className="text-xs text-muted-foreground">/10</span>
                </div>
              </div>
              <div className="w-full space-y-3">
                {[
                  { label: 'Environmental', score: ESG_BREAKDOWN.environmental, icon: Leaf },
                  { label: 'Social', score: ESG_BREAKDOWN.social, icon: Globe },
                  { label: 'Governance', score: ESG_BREAKDOWN.governance, icon: Zap },
                ].map(({ label, score, icon: Icon }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground flex items-center gap-1"><Icon className="w-3 h-3" />{label}</span>
                      <span className="font-medium">{score}/10</span>
                    </div>
                    <Progress value={score * 10} className="h-1.5 [&>div]:bg-primary" />
                  </div>
                ))}
                <div className="text-center pt-2">
                  <p className="text-xs text-muted-foreground">Benchmark: {ESG_BREAKDOWN.benchmark}/10</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Carbon Footprint */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">Carbon Footprint</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Portfolio Intensity</span>
                <span className="text-2xl font-bold text-profit">{CARBON_DATA.portfolioIntensity}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Benchmark Intensity</span>
                <span className="text-2xl font-bold text-muted-foreground">{CARBON_DATA.benchmarkIntensity}</span>
              </div>
              <Badge className="w-full justify-center py-2 text-sm" variant="default">
                {CARBON_DATA.reductionPercent}% Lower than Benchmark
              </Badge>
              <div className="border-t border-border/50 pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">CO₂ Avoided</span>
                  <span className="font-medium">{CARBON_DATA.co2Avoided} tons</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Renewable Exposure</span>
                  <span className="font-medium text-profit">{CARBON_DATA.renewableExposure}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Clean Energy Cos.</span>
                  <span className="font-medium">{CARBON_DATA.cleanEnergyCompanies}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* SDG Alignment */}
          <Card className="glass-card">
            <CardHeader><CardTitle className="text-base">SDG Alignment</CardTitle></CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-4 justify-center">
                {[{ num: 7, label: 'Affordable & Clean Energy', icon: Zap }, { num: 13, label: 'Climate Action', icon: Wind }].map(sdg => (
                  <div key={sdg.num} className="text-center">
                    <div className="w-16 h-16 rounded-lg gradient-green-blue flex items-center justify-center mx-auto mb-2">
                      <sdg.icon className="w-8 h-8 text-primary-foreground" />
                    </div>
                    <p className="text-xs font-medium">SDG {sdg.num}</p>
                    <p className="text-[10px] text-muted-foreground">{sdg.label}</p>
                  </div>
                ))}
              </div>
              <div className="space-y-3 pt-2">
                {[
                  { label: 'Renewable Energy Exposure', value: `${CARBON_DATA.renewableExposure}%`, color: 'text-profit' },
                  { label: 'Clean Energy Companies', value: CARBON_DATA.cleanEnergyCompanies.toString(), color: 'text-foreground' },
                  { label: 'Est. CO₂ Avoided', value: `${CARBON_DATA.co2Avoided} tons`, color: 'text-profit' },
                ].map(m => (
                  <div key={m.label} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{m.label}</span>
                    <span className={`font-medium ${m.color}`}>{m.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ESG Holdings Table */}
        <Card className="glass-card">
          <CardHeader><CardTitle className="text-base">ESG Holdings Ranking</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/50 text-muted-foreground">
                    <th className="text-left py-3 px-2 font-medium">Rank</th>
                    <th className="text-left py-3 px-2 font-medium">Ticker</th>
                    <th className="text-left py-3 px-2 font-medium">Name</th>
                    <th className="text-left py-3 px-2 font-medium">Sector</th>
                    <th className="text-right py-3 px-2 font-medium">ESG Score</th>
                  </tr>
                </thead>
                <tbody>
                  {[...HOLDINGS].sort((a, b) => b.esgScore - a.esgScore).map((h, i) => (
                    <tr key={h.ticker} className={`border-b border-border/30 hover:bg-accent/30 transition-colors ${i < 3 ? 'bg-primary/5' : ''}`}>
                      <td className="py-3 px-2 tabular-nums">{i + 1}</td>
                      <td className="py-3 px-2 font-medium">{h.ticker}</td>
                      <td className="py-3 px-2 text-muted-foreground">{h.name}</td>
                      <td className="py-3 px-2 text-muted-foreground">{h.sector}</td>
                      <td className="py-3 px-2 text-right">
                        <Badge variant={h.esgScore >= 8.5 ? "default" : "secondary"} className="tabular-nums">
                          {h.esgScore}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
