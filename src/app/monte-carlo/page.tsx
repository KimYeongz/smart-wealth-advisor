"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { TrendingUp, Target, AlertTriangle, BarChart3 } from "lucide-react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from "recharts";

// Monte Carlo simulation function
function runMonteCarloSimulation(
    initialInvestment: number,
    monthlyContribution: number,
    years: number,
    expectedReturn: number,
    volatility: number,
    simulations: number
): { paths: number[][]; percentiles: { p10: number[]; p50: number[]; p90: number[] } } {
    const months = years * 12;
    const monthlyReturn = expectedReturn / 12;
    const monthlyVol = volatility / Math.sqrt(12);

    const allPaths: number[][] = [];

    for (let sim = 0; sim < simulations; sim++) {
        const path: number[] = [initialInvestment];
        let value = initialInvestment;

        for (let month = 1; month <= months; month++) {
            // Generate random return using Box-Muller transform
            const u1 = Math.random();
            const u2 = Math.random();
            const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);

            const monthReturn = monthlyReturn + monthlyVol * z;
            value = value * (1 + monthReturn) + monthlyContribution;

            // Record yearly values
            if (month % 12 === 0) {
                path.push(value);
            }
        }
        allPaths.push(path);
    }

    // Calculate percentiles for each year
    const p10: number[] = [];
    const p50: number[] = [];
    const p90: number[] = [];

    for (let year = 0; year <= years; year++) {
        const valuesAtYear = allPaths.map(path => path[year]).sort((a, b) => a - b);
        p10.push(valuesAtYear[Math.floor(simulations * 0.1)]);
        p50.push(valuesAtYear[Math.floor(simulations * 0.5)]);
        p90.push(valuesAtYear[Math.floor(simulations * 0.9)]);
    }

    return { paths: allPaths.slice(0, 50), percentiles: { p10, p50, p90 } };
}

export default function MonteCarloPage() {
    const [initialInvestment, setInitialInvestment] = useState("1000000");
    const [monthlyContribution, setMonthlyContribution] = useState("20000");
    const [years, setYears] = useState("10");
    const [expectedReturn, setExpectedReturn] = useState("8");
    const [volatility, setVolatility] = useState("15");
    const [isRunning, setIsRunning] = useState(false);
    const [results, setResults] = useState<{
        paths: number[][];
        percentiles: { p10: number[]; p50: number[]; p90: number[] };
    } | null>(null);

    const runSimulation = () => {
        setIsRunning(true);

        // Simulate async operation
        setTimeout(() => {
            const result = runMonteCarloSimulation(
                parseFloat(initialInvestment) || 0,
                parseFloat(monthlyContribution) || 0,
                parseInt(years) || 10,
                (parseFloat(expectedReturn) || 8) / 100,
                (parseFloat(volatility) || 15) / 100,
                1000
            );
            setResults(result);
            setIsRunning(false);
        }, 500);
    };

    // Prepare chart data
    const chartData = results
        ? results.percentiles.p50.map((_, index) => ({
            year: `ปี ${index}`,
            p10: results.percentiles.p10[index],
            p50: results.percentiles.p50[index],
            p90: results.percentiles.p90[index],
        }))
        : [];

    const totalContributed = results
        ? parseFloat(initialInvestment) + parseFloat(monthlyContribution) * parseInt(years) * 12
        : 0;

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold">
                    <span className="text-gradient">📈 Monte Carlo Simulation</span>
                </h1>
                <p className="text-gray-500 mt-2">
                    จำลองผลตอบแทนการลงทุนในอนาคตด้วยวิธี Monte Carlo (1,000 simulations)
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Input Panel */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">⚙️ พารามิเตอร์</h3>

                    <div className="space-y-4">
                        <Input
                            label="เงินลงทุนเริ่มต้น (บาท)"
                            type="number"
                            value={initialInvestment}
                            onChange={(e) => setInitialInvestment(e.target.value)}
                            placeholder="1,000,000"
                        />
                        <Input
                            label="เงินลงทุนรายเดือน (บาท)"
                            type="number"
                            value={monthlyContribution}
                            onChange={(e) => setMonthlyContribution(e.target.value)}
                            placeholder="20,000"
                        />
                        <Input
                            label="ระยะเวลา (ปี)"
                            type="number"
                            value={years}
                            onChange={(e) => setYears(e.target.value)}
                            placeholder="10"
                        />
                        <Input
                            label="ผลตอบแทนคาดหวัง (%/ปี)"
                            type="number"
                            value={expectedReturn}
                            onChange={(e) => setExpectedReturn(e.target.value)}
                            placeholder="8"
                        />
                        <Input
                            label="ความผันผวน (%/ปี)"
                            type="number"
                            value={volatility}
                            onChange={(e) => setVolatility(e.target.value)}
                            placeholder="15"
                        />

                        <Button onClick={runSimulation} className="w-full" isLoading={isRunning}>
                            🎲 รัน Simulation
                        </Button>
                    </div>
                </div>

                {/* Results Panel */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Metrics */}
                    {results && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <MetricCard
                                label="📊 Median (P50)"
                                value={formatCurrency(results.percentiles.p50[results.percentiles.p50.length - 1])}
                                change="คาดการณ์กลาง"
                                changeType="neutral"
                                icon={Target}
                            />
                            <MetricCard
                                label="🎯 Best Case (P90)"
                                value={formatCurrency(results.percentiles.p90[results.percentiles.p90.length - 1])}
                                change="กรณีดีที่สุด"
                                changeType="positive"
                                icon={TrendingUp}
                            />
                            <MetricCard
                                label="⚠️ Worst Case (P10)"
                                value={formatCurrency(results.percentiles.p10[results.percentiles.p10.length - 1])}
                                change="กรณีเลวร้าย"
                                changeType="negative"
                                icon={AlertTriangle}
                            />
                            <MetricCard
                                label="💰 ลงทุนรวม"
                                value={formatCurrency(totalContributed)}
                                change={`${parseInt(years) * 12} เดือน`}
                                changeType="neutral"
                                icon={BarChart3}
                            />
                        </div>
                    )}

                    {/* Chart */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">
                            📈 ผลการจำลอง (Confidence Interval)
                        </h3>

                        {results ? (
                            <div className="h-80">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorP90" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#00D26A" stopOpacity={0.2} />
                                                <stop offset="95%" stopColor="#00D26A" stopOpacity={0} />
                                            </linearGradient>
                                            <linearGradient id="colorP10" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2} />
                                                <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis dataKey="year" stroke="#9CA3AF" fontSize={12} />
                                        <YAxis
                                            stroke="#9CA3AF"
                                            fontSize={12}
                                            tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "#1E222A",
                                                border: "1px solid #374151",
                                                borderRadius: "8px",
                                            }}
                                            formatter={(value: number) => [formatCurrency(value), ""]}
                                        />
                                        <ReferenceLine
                                            y={totalContributed}
                                            stroke="#FFD700"
                                            strokeDasharray="5 5"
                                            label={{ value: "ทุน", fill: "#FFD700", fontSize: 12 }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="p90"
                                            stroke="#00D26A"
                                            strokeWidth={2}
                                            fill="url(#colorP90)"
                                            name="P90 (Best)"
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="p50"
                                            stroke="#3B82F6"
                                            strokeWidth={3}
                                            fill="transparent"
                                            name="P50 (Median)"
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="p10"
                                            stroke="#EF4444"
                                            strokeWidth={2}
                                            fill="url(#colorP10)"
                                            name="P10 (Worst)"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="h-80 flex items-center justify-center text-gray-500">
                                <div className="text-center">
                                    <p className="text-4xl mb-4">🎲</p>
                                    <p>กรุณากรอกพารามิเตอร์และกด "รัน Simulation"</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Legend */}
                    {results && (
                        <div className="glass-card p-4">
                            <div className="flex flex-wrap gap-6 justify-center text-sm">
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-1 bg-green-500 rounded"></div>
                                    <span className="text-gray-400">P90 - 90% ของผลลัพธ์ต่ำกว่านี้</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-1 bg-blue-500 rounded"></div>
                                    <span className="text-gray-400">P50 - ค่ากลาง (Median)</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-1 bg-red-500 rounded"></div>
                                    <span className="text-gray-400">P10 - 10% ของผลลัพธ์ต่ำกว่านี้</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-1 bg-yellow-500 rounded border-dashed"></div>
                                    <span className="text-gray-400">เงินต้นที่ลงทุน</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
