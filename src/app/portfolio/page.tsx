"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { MetricCard } from "@/components/ui/MetricCard";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { formatCurrency, formatThaiDate } from "@/lib/utils";
import { getAllMarketData, calculatePortfolioValue, MarketPrice } from "@/lib/marketData";
import { Wallet, PiggyBank, TrendingUp, ArrowUpDown, RefreshCw, Check, AlertCircle } from "lucide-react";

interface Transaction {
    id: string;
    type: "deposit" | "withdraw" | "invest";
    amount: number;
    date: Date;
    description: string;
}

interface Portfolio {
    cashBalance: number;
    invested: number;
    allocation: { thai: number; us: number; gold: number; bonds: number };
}

export default function PortfolioPage() {
    const [marketData, setMarketData] = useState<MarketPrice[]>([]);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

    // Load from localStorage
    const [portfolio, setPortfolio] = useState<Portfolio>(() => {
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

    const [transactions, setTransactions] = useState<Transaction[]>(() => {
        if (typeof window !== "undefined") {
            const saved = localStorage.getItem("transactions");
            if (saved) return JSON.parse(saved).map((t: any) => ({ ...t, date: new Date(t.date) }));
        }
        return [];
    });

    const [activeTab, setActiveTab] = useState<"deposit" | "withdraw" | "invest" | "history">("deposit");
    const [amount, setAmount] = useState("");
    const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    // Allocation state with percentage inputs
    const [allocation, setAllocation] = useState({
        thai: portfolio.allocation.thai.toString(),
        us: portfolio.allocation.us.toString(),
        gold: portfolio.allocation.gold.toString(),
        bonds: portfolio.allocation.bonds.toString(),
    });

    // Fetch market data
    useEffect(() => {
        const fetchData = () => {
            const data = getAllMarketData();
            setMarketData(data);
            setLastUpdate(new Date());
        };
        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, []);

    // Save to localStorage
    useEffect(() => {
        localStorage.setItem("portfolio", JSON.stringify(portfolio));
    }, [portfolio]);

    useEffect(() => {
        localStorage.setItem("transactions", JSON.stringify(transactions));
    }, [transactions]);

    // Calculate portfolio values
    const portfolioCalc = calculatePortfolioValue(
        portfolio.cashBalance,
        portfolio.allocation,
        portfolio.invested,
        marketData
    );

    const addTransaction = (type: Transaction["type"], amount: number, description: string) => {
        const newTx: Transaction = {
            id: `tx-${Date.now()}`,
            type,
            amount,
            date: new Date(),
            description,
        };
        setTransactions(prev => [newTx, ...prev]);
    };

    const handleDeposit = () => {
        const depositAmount = parseFloat(amount);
        if (isNaN(depositAmount) || depositAmount <= 0) {
            setMessage({ type: "error", text: "กรุณาระบุจำนวนเงินที่ถูกต้อง" });
            return;
        }

        setPortfolio(prev => ({
            ...prev,
            cashBalance: prev.cashBalance + depositAmount,
        }));
        addTransaction("deposit", depositAmount, `ฝากเงิน ${formatCurrency(depositAmount)}`);
        setAmount("");
        setMessage({ type: "success", text: `ฝากเงิน ${formatCurrency(depositAmount)} สำเร็จ` });
    };

    const handleWithdraw = () => {
        const withdrawAmount = parseFloat(amount);
        if (isNaN(withdrawAmount) || withdrawAmount <= 0) {
            setMessage({ type: "error", text: "กรุณาระบุจำนวนเงินที่ถูกต้อง" });
            return;
        }
        if (withdrawAmount > portfolio.cashBalance) {
            setMessage({ type: "error", text: "ยอดเงินสดไม่เพียงพอ" });
            return;
        }

        setPortfolio(prev => ({
            ...prev,
            cashBalance: prev.cashBalance - withdrawAmount,
        }));
        addTransaction("withdraw", withdrawAmount, `ถอนเงิน ${formatCurrency(withdrawAmount)}`);
        setAmount("");
        setMessage({ type: "success", text: `ถอนเงิน ${formatCurrency(withdrawAmount)} สำเร็จ` });
    };

    const handleInvest = () => {
        const thai = parseFloat(allocation.thai) || 0;
        const us = parseFloat(allocation.us) || 0;
        const gold = parseFloat(allocation.gold) || 0;
        const bonds = parseFloat(allocation.bonds) || 0;
        const total = thai + us + gold + bonds;

        if (total !== 100) {
            setMessage({ type: "error", text: `สัดส่วนรวมต้องเท่ากับ 100% (ปัจจุบัน: ${total}%)` });
            return;
        }
        if (portfolio.cashBalance <= 0) {
            setMessage({ type: "error", text: "ไม่มียอดเงินสดสำหรับลงทุน" });
            return;
        }

        const investAmount = portfolio.cashBalance;
        const newAllocation = { thai, us, gold, bonds };

        setPortfolio(prev => ({
            ...prev,
            invested: prev.invested + investAmount,
            cashBalance: 0,
            allocation: newAllocation,
        }));
        addTransaction("invest", investAmount, `ลงทุน: หุ้นไทย ${thai}%, หุ้น US ${us}%, ทองคำ ${gold}%, พันธบัตร ${bonds}%`);
        setMessage({ type: "success", text: `ลงทุน ${formatCurrency(investAmount)} ตามสัดส่วนที่กำหนด` });
    };

    const handleAllocationChange = (key: keyof typeof allocation, value: string) => {
        // Only allow numbers and decimal point
        if (value && !/^\d*\.?\d*$/.test(value)) return;
        setAllocation(prev => ({ ...prev, [key]: value }));
    };

    const totalAllocation =
        (parseFloat(allocation.thai) || 0) +
        (parseFloat(allocation.us) || 0) +
        (parseFloat(allocation.gold) || 0) +
        (parseFloat(allocation.bonds) || 0);

    const getTransactionIcon = (type: Transaction["type"]) => {
        switch (type) {
            case "deposit": return "💳";
            case "withdraw": return "🏧";
            case "invest": return "📊";
        }
    };

    const getTransactionColor = (type: Transaction["type"]) => {
        switch (type) {
            case "deposit": return "text-green-400";
            case "withdraw": return "text-red-400";
            case "invest": return "text-blue-400";
        }
    };

    const tabs = [
        { id: "deposit", label: "💳 ฝากเงิน" },
        { id: "withdraw", label: "🏧 ถอนเงิน" },
        { id: "invest", label: "📊 ลงทุน" },
        { id: "history", label: "📜 ประวัติ" },
    ];

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">
                        <span className="text-gradient">💼 จัดการพอร์ตโฟลิโอ</span>
                    </h1>
                    <p className="text-gray-500 mt-2">ฝากเงิน ถอนเงิน และจัดสรรการลงทุนของคุณ</p>
                </div>
                <div className="text-right text-sm">
                    <p className="text-gray-500">อัพเดทตลาด</p>
                    <p className="text-white font-medium flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        {lastUpdate.toLocaleTimeString("th-TH")}
                    </p>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    label="💰 มูลค่ารวม"
                    value={formatCurrency(portfolioCalc.totalValue)}
                    change={`${portfolioCalc.dailyChange >= 0 ? "+" : ""}${formatCurrency(portfolioCalc.dailyChange)} วันนี้`}
                    changeType={portfolioCalc.dailyChange >= 0 ? "positive" : "negative"}
                    icon={Wallet}
                />
                <MetricCard
                    label="💵 เงินสด"
                    value={formatCurrency(portfolio.cashBalance)}
                    change="พร้อมลงทุน"
                    changeType="neutral"
                    icon={PiggyBank}
                />
                <MetricCard
                    label="📈 ลงทุนแล้ว"
                    value={formatCurrency(portfolio.invested)}
                    change={`${portfolioCalc.dailyChangePercent >= 0 ? "+" : ""}${portfolioCalc.dailyChangePercent.toFixed(2)}% วันนี้`}
                    changeType={portfolioCalc.dailyChangePercent >= 0 ? "positive" : "negative"}
                    icon={TrendingUp}
                />
                <MetricCard
                    label="⚠️ ระดับความเสี่ยง"
                    value="6/10"
                    change="ปานกลาง"
                    changeType="neutral"
                    icon={ArrowUpDown}
                />
            </div>

            {/* Tab Navigation */}
            <div className="glass-card">
                <div className="flex border-b border-gray-700">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${activeTab === tab.id
                                ? "text-primary border-b-2 border-primary bg-primary/5"
                                : "text-gray-400 hover:text-white hover:bg-dark-50"
                                }`}
                            onClick={() => {
                                setActiveTab(tab.id as typeof activeTab);
                                setMessage(null);
                            }}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="p-6">
                    {/* Message */}
                    {message && (
                        <div
                            className={`mb-6 p-4 rounded-lg border flex items-center gap-3 ${message.type === "success"
                                ? "bg-green-500/10 border-green-500/30 text-green-400"
                                : "bg-red-500/10 border-red-500/30 text-red-400"
                                }`}
                        >
                            {message.type === "success" ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                            {message.text}
                        </div>
                    )}

                    {/* Deposit Tab */}
                    {activeTab === "deposit" && (
                        <div className="max-w-md">
                            <h3 className="text-lg font-semibold text-white mb-4">ฝากเงินเข้าพอร์ต</h3>
                            <div className="space-y-4">
                                <Input
                                    label="จำนวนเงิน (บาท)"
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    placeholder="100,000"
                                />
                                <div className="flex gap-2">
                                    {[10000, 50000, 100000, 500000].map((preset) => (
                                        <button
                                            key={preset}
                                            onClick={() => setAmount(preset.toString())}
                                            className="px-3 py-2 bg-dark-100 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white hover:border-primary transition-colors"
                                        >
                                            {(preset / 1000).toFixed(0)}K
                                        </button>
                                    ))}
                                </div>
                                <Button onClick={handleDeposit} className="w-full">
                                    ฝากเงิน
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* Withdraw Tab */}
                    {activeTab === "withdraw" && (
                        <div className="max-w-md">
                            <h3 className="text-lg font-semibold text-white mb-4">ถอนเงินจากพอร์ต</h3>
                            <p className="text-sm text-gray-400 mb-4">
                                💵 ยอดเงินสดคงเหลือ: <span className="text-white font-medium">{formatCurrency(portfolio.cashBalance)}</span>
                            </p>
                            <div className="space-y-4">
                                <Input
                                    label="จำนวนเงิน (บาท)"
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    placeholder="50,000"
                                />
                                <Button onClick={handleWithdraw} className="w-full">
                                    ถอนเงิน
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* Invest Tab */}
                    {activeTab === "invest" && (
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">ลงทุนตามสัดส่วน</h3>
                            {portfolio.cashBalance <= 0 ? (
                                <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-400 flex items-center gap-3">
                                    <AlertCircle className="w-5 h-5" />
                                    ไม่มียอดเงินสดสำหรับลงทุน กรุณาฝากเงินก่อน
                                </div>
                            ) : (
                                <>
                                    <p className="text-sm text-gray-400 mb-6">
                                        💵 เงินสดพร้อมลงทุน: <span className="text-white font-medium">{formatCurrency(portfolio.cashBalance)}</span>
                                    </p>

                                    {/* Percentage Input Fields */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">🇹🇭 หุ้นไทย</label>
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={allocation.thai}
                                                    onChange={(e) => handleAllocationChange("thai", e.target.value)}
                                                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 pr-10 text-white text-center text-lg font-medium focus:border-primary focus:outline-none"
                                                    placeholder="0"
                                                />
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">%</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1 text-center">
                                                = {formatCurrency(portfolio.cashBalance * (parseFloat(allocation.thai) || 0) / 100)}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">🇺🇸 หุ้น US</label>
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={allocation.us}
                                                    onChange={(e) => handleAllocationChange("us", e.target.value)}
                                                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 pr-10 text-white text-center text-lg font-medium focus:border-blue-500 focus:outline-none"
                                                    placeholder="0"
                                                />
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">%</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1 text-center">
                                                = {formatCurrency(portfolio.cashBalance * (parseFloat(allocation.us) || 0) / 100)}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">🪙 ทองคำ</label>
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={allocation.gold}
                                                    onChange={(e) => handleAllocationChange("gold", e.target.value)}
                                                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 pr-10 text-white text-center text-lg font-medium focus:border-yellow-500 focus:outline-none"
                                                    placeholder="0"
                                                />
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">%</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1 text-center">
                                                = {formatCurrency(portfolio.cashBalance * (parseFloat(allocation.gold) || 0) / 100)}
                                            </p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">📜 พันธบัตร</label>
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={allocation.bonds}
                                                    onChange={(e) => handleAllocationChange("bonds", e.target.value)}
                                                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 pr-10 text-white text-center text-lg font-medium focus:border-purple-500 focus:outline-none"
                                                    placeholder="0"
                                                />
                                                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">%</span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-1 text-center">
                                                = {formatCurrency(portfolio.cashBalance * (parseFloat(allocation.bonds) || 0) / 100)}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Quick Presets */}
                                    <div className="flex gap-2 mb-6">
                                        <button
                                            onClick={() => setAllocation({ thai: "25", us: "25", gold: "25", bonds: "25" })}
                                            className="px-4 py-2 bg-dark-100 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white hover:border-primary transition-colors"
                                        >
                                            สมดุล (25/25/25/25)
                                        </button>
                                        <button
                                            onClick={() => setAllocation({ thai: "40", us: "40", gold: "10", bonds: "10" })}
                                            className="px-4 py-2 bg-dark-100 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white hover:border-primary transition-colors"
                                        >
                                            เชิงรุก (40/40/10/10)
                                        </button>
                                        <button
                                            onClick={() => setAllocation({ thai: "20", us: "20", gold: "20", bonds: "40" })}
                                            className="px-4 py-2 bg-dark-100 border border-gray-700 rounded-lg text-sm text-gray-400 hover:text-white hover:border-primary transition-colors"
                                        >
                                            ปลอดภัย (20/20/20/40)
                                        </button>
                                    </div>

                                    {/* Total Indicator */}
                                    <div
                                        className={`p-4 rounded-lg border mb-6 ${totalAllocation === 100
                                            ? "bg-green-500/10 border-green-500/30 text-green-400"
                                            : "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"
                                            }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="flex items-center gap-2">
                                                {totalAllocation === 100 ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                                                สัดส่วนรวม: {totalAllocation}%
                                            </span>
                                            {totalAllocation !== 100 && (
                                                <span className="text-sm">ต้องเท่ากับ 100%</span>
                                            )}
                                        </div>
                                    </div>

                                    <Button onClick={handleInvest} className="w-full" disabled={totalAllocation !== 100}>
                                        ยืนยันลงทุน {formatCurrency(portfolio.cashBalance)}
                                    </Button>
                                </>
                            )}
                        </div>
                    )}

                    {/* History Tab */}
                    {activeTab === "history" && (
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">ประวัติธุรกรรม</h3>
                            {transactions.length === 0 ? (
                                <div className="text-center py-12 text-gray-500">
                                    <p className="text-4xl mb-4">📜</p>
                                    <p>ยังไม่มีประวัติธุรกรรม</p>
                                    <p className="text-sm mt-2">เริ่มต้นด้วยการฝากเงินเข้าพอร์ต</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {transactions.map((tx) => (
                                        <div
                                            key={tx.id}
                                            className="flex items-center justify-between p-4 bg-dark-100 rounded-lg border border-gray-700/50"
                                        >
                                            <div className="flex items-center gap-4">
                                                <span className="text-2xl">{getTransactionIcon(tx.type)}</span>
                                                <div>
                                                    <p className="font-medium text-white">{tx.description}</p>
                                                    <p className="text-sm text-gray-500">{formatThaiDate(tx.date)}</p>
                                                </div>
                                            </div>
                                            <p className={`font-bold ${getTransactionColor(tx.type)}`}>
                                                {tx.type === "deposit" ? "+" : tx.type === "withdraw" ? "-" : ""}
                                                {formatCurrency(tx.amount)}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
