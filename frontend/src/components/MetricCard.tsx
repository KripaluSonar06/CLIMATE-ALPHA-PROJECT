import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function MetricCard({ title, value, subtitle, trend, icon, children, className }: MetricCardProps) {
  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className={cn(
          "text-2xl font-bold tabular-nums animate-counter",
          trend === "up" && "text-profit",
          trend === "down" && "text-loss",
        )}>
          {value}
        </div>
        {subtitle && (
          <p className={cn(
            "text-xs mt-1",
            trend === "up" ? "text-profit" : trend === "down" ? "text-loss" : "text-muted-foreground"
          )}>
            {subtitle}
          </p>
        )}
        {children}
      </CardContent>
    </Card>
  );
}
