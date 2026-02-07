"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatCurrency } from "@/lib/utils";
import { Calculator, PiggyBank, Receipt, TrendingDown } from "lucide-react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";

// Thai tax brackets for 2024
const TAX_BRACKETS = [
    { min: 0, max: 150000, rate: 0 },
    { min: 150001, max: 300000, rate: 0.05 },
    { min: 300001, max: 500000, rate: 0.10 },
    { min: 500001, max: 750000, rate: 0.15 },
    { min: 750001, max: 1000000, rate: 0.20 },
    { min: 1000001, max: 2000000, rate: 0.25 },
    { min: 2000001, max: 5000000, rate: 0.30 },
    { min: 5000001, max: Infinity, rate: 0.35 },
];

// Calculate progressive tax
function calculateTax(income: number): { tax: number; effectiveRate: number; breakdown: { bracket: string; tax: number }[] } {
    let remainingIncome = income;
    let totalTax = 0;
    const breakdown: { bracket: string; tax: number }[] = [];

    for (const bracket of TAX_BRACKETS) {
        if (remainingIncome <= 0) break;

        const taxableInBracket = Math.min(
            remainingIncome,
            bracket.max - bracket.min + 1
        );
        const taxInBracket = taxableInBracket * bracket.rate;

        if (taxInBracket > 0) {
            breakdown.push({
                bracket: `${formatCurrency(bracket.min)} - ${bracket.max === Infinity ? 'ขึ้นไป' : formatCurrency(bracket.max)}`,
                tax: taxInBracket,
            });
        }

        totalTax += taxInBracket;
        remainingIncome -= taxableInBracket;
    }

    return {
        tax: totalTax,
        effectiveRate: income > 0 ? totalTax / income : 0,
        breakdown,
    };
}

export default function TaxPlannerPage() {
    // Income inputs
    const [salary, setSalary] = useState("720000");
    const [bonus, setBonus] = useState("60000");
    const [otherIncome, setOtherIncome] = useState("0");

    // Deduction inputs
    const [personalDeduction] = useState(60000); // Fixed
    const [spouseDeduction, setSpouseDeduction] = useState("0");
    const [childDeduction, setChildDeduction] = useState("0");
    const [parentDeduction, setParentDeduction] = useState("0");
    const [insuranceDeduction, setInsuranceDeduction] = useState("0");
    const [providentFund, setProvidentFund] = useState("0");
    const [rmfDeduction, setRmfDeduction] = useState("0");
    const [ssfDeduction, setSsfDeduction] = useState("0");
    const [homeLoanInterest, setHomeLoanInterest] = useState("0");

    // Calculate totals
    const totalIncome = (parseFloat(salary) || 0) + (parseFloat(bonus) || 0) + (parseFloat(otherIncome) || 0);

    const totalDeductions =
        personalDeduction +
        (parseFloat(spouseDeduction) || 0) +
        (parseFloat(childDeduction) || 0) +
        (parseFloat(parentDeduction) || 0) +
        (parseFloat(insuranceDeduction) || 0) +
        (parseFloat(providentFund) || 0) +
        (parseFloat(rmfDeduction) || 0) +
        (parseFloat(ssfDeduction) || 0) +
        (parseFloat(homeLoanInterest) || 0);

    // Expense deduction (50% of income, max 100,000)
    const expenseDeduction = Math.min(totalIncome * 0.5, 100000);

    const taxableIncome = Math.max(0, totalIncome - expenseDeduction - totalDeductions);
    const { tax, effectiveRate, breakdown } = calculateTax(taxableIncome);

    // Chart data for tax breakdown
    const chartData = breakdown.map((item, index) => ({
        ...item,
        color: ["#00D26A", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444", "#EC4899", "#06B6D4", "#84CC16"][index % 8],
    }));

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold">
                    <span className="text-gradient">🧮 วางแผนภาษี</span>
                </h1>
                <p className="text-gray-500 mt-2">
                    คำนวณภาษีเงินได้บุคคลธรรมดา ปี 2567 และวางแผนลดหย่อน
                </p>
            </div>

            {/* Summary Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    label="💰 รายได้รวม"
                    value={formatCurrency(totalIncome)}
                    change="ต่อปี"
                    changeType="neutral"
                    icon={Receipt}
                />
                <MetricCard
                    label="📝 ลดหย่อนรวม"
                    value={formatCurrency(totalDeductions + expenseDeduction)}
                    change={`รวมค่าใช้จ่าย ${formatCurrency(expenseDeduction)}`}
                    changeType="neutral"
                    icon={TrendingDown}
                />
                <MetricCard
                    label="📊 เงินได้สุทธิ"
                    value={formatCurrency(taxableIncome)}
                    change="หลังหักลดหย่อน"
                    changeType="neutral"
                    icon={Calculator}
                />
                <MetricCard
                    label="💸 ภาษีที่ต้องจ่าย"
                    value={formatCurrency(tax)}
                    change={`อัตราจริง ${(effectiveRate * 100).toFixed(2)}%`}
                    changeType={tax > 0 ? "negative" : "positive"}
                    icon={PiggyBank}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Income Panel */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">💵 รายได้</h3>
                    <div className="space-y-4">
                        <Input
                            label="เงินเดือน (บาท/ปี)"
                            type="number"
                            value={salary}
                            onChange={(e) => setSalary(e.target.value)}
                            placeholder="720,000"
                        />
                        <Input
                            label="โบนัส (บาท/ปี)"
                            type="number"
                            value={bonus}
                            onChange={(e) => setBonus(e.target.value)}
                            placeholder="60,000"
                        />
                        <Input
                            label="รายได้อื่นๆ (บาท/ปี)"
                            type="number"
                            value={otherIncome}
                            onChange={(e) => setOtherIncome(e.target.value)}
                            placeholder="0"
                        />
                    </div>
                </div>

                {/* Deductions Panel */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">📝 ค่าลดหย่อน</h3>
                    <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                        <div className="p-3 bg-primary/10 border border-primary/30 rounded-lg">
                            <p className="text-sm text-gray-400">ค่าลดหย่อนส่วนตัว</p>
                            <p className="text-lg font-semibold text-primary">{formatCurrency(personalDeduction)}</p>
                        </div>
                        <Input
                            label="คู่สมรส (ไม่มีรายได้)"
                            type="number"
                            value={spouseDeduction}
                            onChange={(e) => setSpouseDeduction(e.target.value)}
                            placeholder="0 - 60,000"
                            helperText="สูงสุด 60,000 บาท"
                        />
                        <Input
                            label="บุตร (คนละ 30,000)"
                            type="number"
                            value={childDeduction}
                            onChange={(e) => setChildDeduction(e.target.value)}
                            placeholder="0"
                            helperText="บุตรคนที่ 2 เป็นต้นไป 60,000"
                        />
                        <Input
                            label="บิดามารดา (คนละ 30,000)"
                            type="number"
                            value={parentDeduction}
                            onChange={(e) => setParentDeduction(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 120,000 บาท"
                        />
                        <Input
                            label="ประกันชีวิต"
                            type="number"
                            value={insuranceDeduction}
                            onChange={(e) => setInsuranceDeduction(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 100,000 บาท"
                        />
                        <Input
                            label="กองทุนสำรองเลี้ยงชีพ"
                            type="number"
                            value={providentFund}
                            onChange={(e) => setProvidentFund(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 15% ของเงินเดือน"
                        />
                        <Input
                            label="RMF (กองทุนรวมเพื่อการเลี้ยงชีพ)"
                            type="number"
                            value={rmfDeduction}
                            onChange={(e) => setRmfDeduction(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 30% ไม่เกิน 500,000"
                        />
                        <Input
                            label="SSF (กองทุนรวมเพื่อการออม)"
                            type="number"
                            value={ssfDeduction}
                            onChange={(e) => setSsfDeduction(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 30% ไม่เกิน 200,000"
                        />
                        <Input
                            label="ดอกเบี้ยบ้าน"
                            type="number"
                            value={homeLoanInterest}
                            onChange={(e) => setHomeLoanInterest(e.target.value)}
                            placeholder="0"
                            helperText="สูงสุด 100,000 บาท"
                        />
                    </div>
                </div>

                {/* Results Panel */}
                <div className="space-y-6">
                    {/* Tax Breakdown Chart */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">📊 ภาษีแต่ละขั้น</h3>
                        {chartData.length > 0 ? (
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} layout="vertical">
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis type="number" stroke="#9CA3AF" fontSize={12} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                                        <YAxis type="category" dataKey="bracket" stroke="#9CA3AF" fontSize={10} width={100} hide />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "#1E222A",
                                                border: "1px solid #374151",
                                                borderRadius: "8px",
                                            }}
                                            formatter={(value: number) => [formatCurrency(value), "ภาษี"]}
                                        />
                                        <Bar dataKey="tax" radius={[0, 4, 4, 0]}>
                                            {chartData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="h-64 flex items-center justify-center text-gray-500">
                                <p>ไม่มีภาษีที่ต้องจ่าย 🎉</p>
                            </div>
                        )}
                    </div>

                    {/* Tax Brackets Info */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">📋 อัตราภาษี</h3>
                        <div className="space-y-2 text-sm">
                            {TAX_BRACKETS.map((bracket, index) => (
                                <div key={index} className="flex justify-between text-gray-400">
                                    <span>
                                        {formatCurrency(bracket.min)} - {bracket.max === Infinity ? 'ขึ้นไป' : formatCurrency(bracket.max)}
                                    </span>
                                    <span className="text-white font-medium">{(bracket.rate * 100)}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
