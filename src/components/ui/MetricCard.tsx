import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
    label: string;
    value: string;
    change?: string;
    changeType?: "positive" | "negative" | "neutral";
    icon?: LucideIcon;
    className?: string;
}

export function MetricCard({
    label,
    value,
    change,
    changeType = "neutral",
    icon: Icon,
    className,
}: MetricCardProps) {
    return (
        <div className={cn("metric-card", className)}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-gray-400 mb-1">{label}</p>
                    <p className="text-2xl font-bold text-white">{value}</p>
                    {change && (
                        <p
                            className={cn(
                                "text-sm mt-1 font-medium",
                                changeType === "positive" && "text-green-400",
                                changeType === "negative" && "text-red-400",
                                changeType === "neutral" && "text-gray-400"
                            )}
                        >
                            {change}
                        </p>
                    )}
                </div>
                {Icon && (
                    <div className="p-3 bg-primary/10 rounded-xl">
                        <Icon className="w-6 h-6 text-primary" />
                    </div>
                )}
            </div>
        </div>
    );
}
