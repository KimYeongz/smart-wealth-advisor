"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { formatCurrency, formatThaiDate } from "@/lib/utils";
import { FileText, Download, Calendar, TrendingUp, PieChart, BarChart3 } from "lucide-react";

interface ReportTemplate {
    id: string;
    title: string;
    description: string;
    icon: React.ReactNode;
    type: "monthly" | "quarterly" | "annual" | "custom";
}

const reportTemplates: ReportTemplate[] = [
    {
        id: "portfolio-summary",
        title: "สรุปพอร์ตโฟลิโอ",
        description: "รายงานสรุปมูลค่าพอร์ต สัดส่วนการลงทุน และผลตอบแทน",
        icon: <PieChart className="w-6 h-6" />,
        type: "monthly",
    },
    {
        id: "performance",
        title: "ผลการดำเนินงาน",
        description: "วิเคราะห์ผลตอบแทนเทียบกับเบนช์มาร์กและดัชนีตลาด",
        icon: <TrendingUp className="w-6 h-6" />,
        type: "quarterly",
    },
    {
        id: "transaction-history",
        title: "ประวัติธุรกรรม",
        description: "รายละเอียดการซื้อขาย ฝากถอน และเงินปันผล",
        icon: <BarChart3 className="w-6 h-6" />,
        type: "monthly",
    },
    {
        id: "tax-report",
        title: "รายงานภาษี",
        description: "สรุปรายได้และค่าลดหย่อนสำหรับยื่นภาษี",
        icon: <FileText className="w-6 h-6" />,
        type: "annual",
    },
];

// Mock generated reports
const mockGeneratedReports = [
    { id: "1", title: "สรุปพอร์ตโฟลิโอ - ม.ค. 2567", date: new Date("2024-01-31"), size: "245 KB" },
    { id: "2", title: "ผลการดำเนินงาน Q4/2566", date: new Date("2023-12-31"), size: "512 KB" },
    { id: "3", title: "ประวัติธุรกรรม - ธ.ค. 2566", date: new Date("2023-12-31"), size: "128 KB" },
];

export default function ReportsPage() {
    const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedReports, setGeneratedReports] = useState(mockGeneratedReports);

    const handleGenerateReport = (templateId: string) => {
        setSelectedTemplate(templateId);
        setIsGenerating(true);

        // Simulate report generation
        setTimeout(() => {
            const template = reportTemplates.find((t) => t.id === templateId);
            if (template) {
                const newReport = {
                    id: `${Date.now()}`,
                    title: `${template.title} - ${formatThaiDate(new Date())}`,
                    date: new Date(),
                    size: `${Math.floor(Math.random() * 500 + 100)} KB`,
                };
                setGeneratedReports((prev) => [newReport, ...prev]);
            }
            setIsGenerating(false);
            setSelectedTemplate(null);
        }, 2000);
    };

    const handleDownload = (reportId: string) => {
        // In a real app, this would trigger a download
        const report = generatedReports.find((r) => r.id === reportId);
        if (report) {
            // Create a dummy PDF download
            const content = `
        Smart Wealth Advisor - รายงาน
        =====================================
        
        ${report.title}
        วันที่: ${formatThaiDate(report.date)}
        
        สรุปพอร์ตโฟลิโอ
        - มูลค่ารวม: ฿5,000,000
        - ผลตอบแทน YTD: +8.23%
        - ระดับความเสี่ยง: 6/10
        
        สัดส่วนการลงทุน:
        - หุ้นไทย: 30%
        - หุ้น US: 35%
        - ทองคำ: 15%
        - พันธบัตร: 20%
        
        =====================================
        สร้างโดย Smart Wealth Advisor
      `;

            const blob = new Blob([content], { type: "text/plain" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${report.title.replace(/ /g, "_")}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold">
                    <span className="text-gradient">📄 รายงาน PDF</span>
                </h1>
                <p className="text-gray-500 mt-2">
                    สร้างและดาวน์โหลดรายงานสรุปพอร์ตโฟลิโอ
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Template Selection */}
                <div className="lg:col-span-2">
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">📋 เลือกประเภทรายงาน</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {reportTemplates.map((template) => (
                                <div
                                    key={template.id}
                                    className={`p-4 border rounded-xl cursor-pointer transition-all duration-200 ${selectedTemplate === template.id
                                            ? "border-primary bg-primary/10"
                                            : "border-gray-700 hover:border-gray-600 bg-dark-100"
                                        }`}
                                    onClick={() => !isGenerating && setSelectedTemplate(template.id)}
                                >
                                    <div className="flex items-start gap-4">
                                        <div className={`p-3 rounded-lg ${selectedTemplate === template.id ? "bg-primary/20 text-primary" : "bg-dark-50 text-gray-400"
                                            }`}>
                                            {template.icon}
                                        </div>
                                        <div className="flex-1">
                                            <h4 className="font-medium text-white">{template.title}</h4>
                                            <p className="text-sm text-gray-500 mt-1">{template.description}</p>
                                            <span className={`inline-block mt-2 text-xs px-2 py-1 rounded-full ${template.type === "monthly" ? "bg-blue-500/20 text-blue-400" :
                                                    template.type === "quarterly" ? "bg-purple-500/20 text-purple-400" :
                                                        template.type === "annual" ? "bg-green-500/20 text-green-400" :
                                                            "bg-gray-500/20 text-gray-400"
                                                }`}>
                                                {template.type === "monthly" ? "รายเดือน" :
                                                    template.type === "quarterly" ? "รายไตรมาส" :
                                                        template.type === "annual" ? "รายปี" : "กำหนดเอง"}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {selectedTemplate && (
                            <div className="mt-6">
                                <Button
                                    onClick={() => handleGenerateReport(selectedTemplate)}
                                    isLoading={isGenerating}
                                    className="w-full"
                                >
                                    <FileText className="w-4 h-4 mr-2" />
                                    {isGenerating ? "กำลังสร้างรายงาน..." : "สร้างรายงาน"}
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Generated Reports */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">📥 รายงานที่สร้างแล้ว</h3>

                    {generatedReports.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                            <p>ยังไม่มีรายงาน</p>
                            <p className="text-sm mt-1">เลือกประเภทและสร้างรายงานใหม่</p>
                        </div>
                    ) : (
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {generatedReports.map((report) => (
                                <div
                                    key={report.id}
                                    className="p-4 bg-dark-100 rounded-lg border border-gray-700/50 hover:border-gray-600 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-white truncate">{report.title}</p>
                                            <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                                                <span className="flex items-center gap-1">
                                                    <Calendar className="w-3 h-3" />
                                                    {formatThaiDate(report.date)}
                                                </span>
                                                <span>{report.size}</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDownload(report.id)}
                                            className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
                                            title="ดาวน์โหลด"
                                        >
                                            <Download className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Report Preview */}
            <div className="mt-6 glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">👀 ตัวอย่างรายงาน</h3>
                <div className="bg-dark-100 rounded-lg p-6 border border-gray-700/50">
                    <div className="max-w-2xl mx-auto">
                        {/* Mock PDF Preview */}
                        <div className="bg-white text-black p-8 rounded-lg shadow-lg">
                            <div className="text-center border-b border-gray-300 pb-4 mb-4">
                                <h2 className="text-xl font-bold">💎 Smart Wealth Advisor</h2>
                                <p className="text-gray-600">รายงานสรุปพอร์ตโฟลิโอ</p>
                                <p className="text-sm text-gray-500">{formatThaiDate(new Date())}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div className="p-3 bg-gray-100 rounded">
                                    <p className="text-xs text-gray-500">มูลค่ารวม</p>
                                    <p className="text-lg font-bold">฿5,000,000</p>
                                </div>
                                <div className="p-3 bg-gray-100 rounded">
                                    <p className="text-xs text-gray-500">ผลตอบแทน YTD</p>
                                    <p className="text-lg font-bold text-green-600">+8.23%</p>
                                </div>
                                <div className="p-3 bg-gray-100 rounded">
                                    <p className="text-xs text-gray-500">ระดับความเสี่ยง</p>
                                    <p className="text-lg font-bold">6/10</p>
                                </div>
                                <div className="p-3 bg-gray-100 rounded">
                                    <p className="text-xs text-gray-500">Sharpe Ratio</p>
                                    <p className="text-lg font-bold">1.42</p>
                                </div>
                            </div>

                            <div className="text-center text-xs text-gray-400 pt-4 border-t border-gray-300">
                                สร้างโดยระบบ Smart Wealth Advisor
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
