"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { MetricCard } from "@/components/ui/MetricCard";
import { useAuth } from "@/context/AuthContext";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { getAllMarketData, calculatePortfolioValue, generatePerformanceHistory, MarketPrice } from "@/lib/marketData";
import { Wallet, TrendingUp, PieChart, BarChart3, RefreshCw } from "lucide-react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart as RePieChart,
    Pie,
    Cell,
    Legend,
} from "recharts";

const COLORS = ["#00D26A", "#3B82F6", "#FFD700", "#8B5CF6"];

export default function DashboardPage() {
    const { user } = useAuth();
    const [marketData, setMarketData] = useState<MarketPrice[]>([]);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [isRefreshing, setIsRefreshing] = useState(false);

    // Load portfolio from localStorage or use defaults
    const [portfolio, setPortfolio] = useState(() => {
        if (typeof window !== "undefined") {
            const saved = localStorage.getItem("portfolio");
            if (saved) return JSON.parse(saved);
        }
        return {
            cashBalance: 0,
            invested: 0,
            allocation: { thai: 25, us: 25, gold: 25, bonds: 25 },
        };
    });

    const [performanceData, setPerformanceData] = useState<{ month: string; portfolio: number; benchmark: number }[]>([]);

    // Fetch market data on mount and every 10 seconds
    useEffect(() => {
        const fetchData = () => {
            const data = getAllMarketData();
            setMarketData(data);
            setLastUpdate(new Date());
        };

        fetchData();
        setPerformanceData(generatePerformanceHistory(12));

        const interval = setInterval(fetchData, 10000); // Update every 10 seconds
        return () => clearInterval(interval);
    }, []);

    // Calculate portfolio values based on market data
    const portfolioCalc = calculatePortfolioValue(
        portfolio.cashBalance,
        portfolio.allocation,
        portfolio.invested,
        marketData
    );

    const handleRefresh = () => {
        setIsRefreshing(true);
        const data = getAllMarketData();
        setMarketData(data);
        setLastUpdate(new Date());
        setPerformanceData(generatePerformanceHistory(12));
        setTimeout(() => setIsRefreshing(false), 500);
    };

    // Allocation data for pie chart
    const allocationData = portfolioCalc.holdings.map((h, index) => ({
        name: h.name,
        value: h.allocation,
        amount: h.value,
        color: COLORS[index % COLORS.length],
    }));

    // Calculate Sharpe Ratio (simplified)
    const sharpeRatio = (8.23 - 2.5) / 12; // (Return - RiskFree) / Volatility

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">
                        <span className="text-gradient">📊 แดชบอร์ดพอร์ตโฟลิโอ</span>
                    </h1>
                    <p className="text-gray-500 mt-2">
                        ยินดีต้อนรับ, {user?.full_name} • ภาพรวมพอร์ตและผลการดำเนินงาน
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right text-sm">
                        <p className="text-gray-500">อัพเดทล่าสุด</p>
                        <p className="text-white font-medium">
                            {lastUpdate.toLocaleTimeString("th-TH")}
                        </p>
                    </div>
                    <button
                        onClick={handleRefresh}
                        className={`p-3 rounded-lg bg-dark-50 text-gray-400 hover:text-primary transition-all ${isRefreshing ? "animate-spin" : ""
                            }`}
                    >
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Live Market Ticker */}
            <div className="glass-card p-4 mb-6 overflow-hidden">
                <div className="flex items-center gap-8 animate-marquee">
                    {marketData.map((item) => (
                        <div key={item.symbol} className="flex items-center gap-3 whitespace-nowrap">
                            <span className="text-gray-400">{item.name}</span>
                            <span className="text-white font-medium">
                                {item.currency === "%" ? `${item.price}%` : item.price.toLocaleString()}
                            </span>
                            <span className={`text-sm ${item.change >= 0 ? "text-green-400" : "text-red-400"}`}>
                                {item.change >= 0 ? "▲" : "▼"} {Math.abs(item.changePercent).toFixed(2)}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    label="💰 มูลค่ารวม"
                    value={formatCurrency(portfolioCalc.totalValue)}
                    change={`${portfolioCalc.dailyChange >= 0 ? "+" : ""}${formatCurrency(portfolioCalc.dailyChange)} วันนี้`}
                    changeType={portfolioCalc.dailyChange >= 0 ? "positive" : "negative"}
                    icon={Wallet}
                />
                <MetricCard
                    label="📈 ผลตอบแทน YTD"
                    value={`+8.23%`}
                    change={`+${formatCurrency(portfolioCalc.totalValue * 0.0823)} ปีนี้`}
                    changeType="positive"
                    icon={TrendingUp}
                />
                <MetricCard
                    label="⚠️ ระดับความเสี่ยง"
                    value="6/10"
                    change="ปานกลาง"
                    changeType="neutral"
                    icon={BarChart3}
                />
                <MetricCard
                    label="📊 Sharpe Ratio"
                    value={sharpeRatio.toFixed(2)}
                    change="+0.15 จากไตรมาสก่อน"
                    changeType="positive"
                    icon={PieChart}
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Allocation Pie Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">🥧 สัดส่วนการลงทุน</h3>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <RePieChart>
                                <Pie
                                    data={allocationData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={3}
                                    dataKey="value"
                                    label={({ name, value }) => `${value}%`}
                                    labelLine={false}
                                >
                                    {allocationData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1E222A",
                                        border: "1px solid #374151",
                                        borderRadius: "8px",
                                    }}
                                    formatter={(value: number, name: string, props: any) => [
                                        `${value}% (${formatCurrency(props.payload.amount)})`,
                                        name,
                                    ]}
                                />
                                <Legend
                                    verticalAlign="bottom"
                                    height={36}
                                    formatter={(value) => <span className="text-gray-300 text-sm">{value}</span>}
                                />
                            </RePieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Performance Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">📈 ผลการดำเนินงาน (1 ปี)</h3>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={performanceData}>
                                <defs>
                                    <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#00D26A" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#00D26A" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
                                <YAxis stroke="#9CA3AF" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1E222A",
                                        border: "1px solid #374151",
                                        borderRadius: "8px",
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="portfolio"
                                    stroke="#00D26A"
                                    strokeWidth={3}
                                    fill="url(#colorPortfolio)"
                                    name="พอร์ตโฟลิโอ"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="benchmark"
                                    stroke="#FFD700"
                                    strokeWidth={2}
                                    fill="transparent"
                                    strokeDasharray="5 5"
                                    name="Benchmark"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Holdings Table */}
            <div className="glass-card p-6 mb-8">
                <h3 className="text-lg font-semibold text-white mb-4">💼 การถือครอง</h3>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-700">
                                <th className="text-left py-3 px-4 text-gray-400 font-medium">สินทรัพย์</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium">สัดส่วน</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium">มูลค่า</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium">กำไร/ขาดทุน</th>
                            </tr>
                        </thead>
                        <tbody>
                            {portfolioCalc.holdings.map((holding, index) => (
                                <tr key={holding.symbol} className="border-b border-gray-700/50 hover:bg-dark-50">
                                    <td className="py-4 px-4">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className="w-3 h-3 rounded-full"
                                                style={{ backgroundColor: COLORS[index % COLORS.length] }}
                                            />
                                            <span className="text-white font-medium">{holding.name}</span>
                                        </div>
                                    </td>
                                    <td className="text-right py-4 px-4 text-white">{holding.allocation}%</td>
                                    <td className="text-right py-4 px-4 text-white">{formatCurrency(holding.value)}</td>
                                    <td className="text-right py-4 px-4">
                                        <span className={holding.gain >= 0 ? "text-green-400" : "text-red-400"}>
                                            {holding.gain >= 0 ? "+" : ""}{formatCurrency(holding.gain)}
                                            <span className="text-sm ml-1">
                                                ({holding.gainPercent >= 0 ? "+" : ""}{holding.gainPercent.toFixed(2)}%)
                                            </span>
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            <tr className="border-b border-gray-700/50 hover:bg-dark-50">
                                <td className="py-4 px-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-3 h-3 rounded-full bg-gray-500" />
                                        <span className="text-white font-medium">💵 เงินสด</span>
                                    </div>
                                </td>
                                <td className="text-right py-4 px-4 text-white">-</td>
                                <td className="text-right py-4 px-4 text-white">{formatCurrency(portfolio.cashBalance)}</td>
                                <td className="text-right py-4 px-4 text-gray-500">-</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Quick Insights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 border-l-4 border-green-500">
                    <div className="flex items-center gap-2 text-green-400 mb-2">
                        <span>✅</span>
                        <span className="font-medium">สถานะพอร์ต</span>
                    </div>
                    <p className="text-gray-400 text-sm">
                        พอร์ตโฟลิโอของคุณมีผลการดำเนินงานดีกว่า Benchmark {formatPercent(8.23 - 6.5)} ในปีนี้
                    </p>
                </div>
                <div className="glass-card p-6 border-l-4 border-yellow-500">
                    <div className="flex items-center gap-2 text-yellow-400 mb-2">
                        <span>⚠️</span>
                        <span className="font-medium">แนะนำ</span>
                    </div>
                    <p className="text-gray-400 text-sm">
                        สัดส่วนเงินสด {((portfolio.cashBalance / portfolioCalc.totalValue) * 100).toFixed(1)}% ควรพิจารณาลงทุนเพิ่ม
                    </p>
                </div>
                <div className="glass-card p-6 border-l-4 border-blue-500">
                    <div className="flex items-center gap-2 text-blue-400 mb-2">
                        <span>📊</span>
                        <span className="font-medium">ข้อมูลตลาด</span>
                    </div>
                    <p className="text-gray-400 text-sm">
                        {marketData.find(m => m.symbol === "^SET")?.name}: {" "}
                        <span className={marketData.find(m => m.symbol === "^SET")?.change || 0 >= 0 ? "text-green-400" : "text-red-400"}>
                            {marketData.find(m => m.symbol === "^SET")?.changePercent?.toFixed(2)}%
                        </span>
                    </p>
                </div>
            </div>
        </DashboardLayout>
    );
}
