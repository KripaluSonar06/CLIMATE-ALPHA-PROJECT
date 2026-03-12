import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { useState } from "react";
import { Save, RotateCcw, Plug } from "lucide-react";

export default function SettingsPage() {
  const [positionSize, setPositionSize] = useState([5]);
  const [stopLoss, setStopLoss] = useState([2]);
  const [rebalFreq, setRebalFreq] = useState([30]);
  const [maxPosition, setMaxPosition] = useState([10]);
  const [maxLeverage, setMaxLeverage] = useState([1.5]);
  const [varLimit, setVarLimit] = useState([5]);

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-4xl">
        <h1 className="text-2xl font-bold">Settings</h1>

        {/* Strategy Parameters */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Strategy Parameters</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => { setPositionSize([5]); setStopLoss([2]); setRebalFreq([30]); }}>
                <RotateCcw className="h-4 w-4 mr-1" /> Reset
              </Button>
              <Button size="sm" onClick={() => toast.success("Parameters saved")}>
                <Save className="h-4 w-4 mr-1" /> Save
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Position Sizing (%)</Label>
                <span className="text-sm tabular-nums font-medium">{positionSize[0]}%</span>
              </div>
              <Slider value={positionSize} onValueChange={setPositionSize} max={20} step={0.5} className="[&>span>span]:bg-primary" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Stop Loss (%)</Label>
                <span className="text-sm tabular-nums font-medium">{stopLoss[0]}%</span>
              </div>
              <Slider value={stopLoss} onValueChange={setStopLoss} max={10} step={0.5} className="[&>span>span]:bg-destructive" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Rebalancing Frequency (days)</Label>
                <span className="text-sm tabular-nums font-medium">{rebalFreq[0]} days</span>
              </div>
              <Slider value={rebalFreq} onValueChange={setRebalFreq} max={90} step={1} className="[&>span>span]:bg-secondary" />
            </div>
          </CardContent>
        </Card>

        {/* Risk Limits */}
        <Card className="glass-card">
          <CardHeader><CardTitle className="text-base">Risk Limits</CardTitle></CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Max Position Size (%)</Label>
                <span className="text-sm tabular-nums font-medium">{maxPosition[0]}%</span>
              </div>
              <Slider value={maxPosition} onValueChange={setMaxPosition} max={25} step={1} className="[&>span>span]:bg-primary" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>Max Portfolio Leverage</Label>
                <span className="text-sm tabular-nums font-medium">{maxLeverage[0]}x</span>
              </div>
              <Slider value={maxLeverage} onValueChange={setMaxLeverage} max={3} step={0.1} className="[&>span>span]:bg-secondary" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>VaR Limit (%)</Label>
                <span className="text-sm tabular-nums font-medium">{varLimit[0]}%</span>
              </div>
              <Slider value={varLimit} onValueChange={setVarLimit} max={10} step={0.5} className="[&>span>span]:bg-destructive" />
            </div>
          </CardContent>
        </Card>

        {/* API Configuration */}
        <Card className="glass-card">
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><Plug className="h-4 w-4" /> API Configuration</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Market Data API Key</Label>
              <Input type="password" placeholder="••••••••••••" className="bg-muted/50 border-border/50" />
            </div>
            <div className="space-y-2">
              <Label>Broker API Key</Label>
              <Input type="password" placeholder="••••••••••••" className="bg-muted/50 border-border/50" />
            </div>
            <div className="space-y-2">
              <Label>Broker API Secret</Label>
              <Input type="password" placeholder="••••••••••••" className="bg-muted/50 border-border/50" />
            </div>
            <Button variant="outline" className="mt-2" onClick={() => toast.success("Connection successful")}>
              Test Connection
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
