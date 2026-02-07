"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatCurrency } from "@/lib/utils";
import { Users, TrendingUp, AlertCircle, Search, Eye, MessageCircle, Filter } from "lucide-react";

interface Client {
    id: string;
    name: string;
    email: string;
    phone: string;
    portfolioValue: number;
    ytdReturn: number;
    riskLevel: number;
    status: "active" | "pending" | "inactive";
    lastActivity: Date;
}

const mockClients: Client[] = [
    {
        id: "1",
        name: "คุณสมชาย ใจดี",
        email: "somchai@email.com",
        phone: "089-123-4567",
        portfolioValue: 5000000,
        ytdReturn: 12.5,
        riskLevel: 6,
        status: "active",
        lastActivity: new Date("2024-01-20"),
    },
    {
        id: "2",
        name: "คุณสมหญิง รักเรียน",
        email: "somying@email.com",
        phone: "081-234-5678",
        portfolioValue: 3200000,
        ytdReturn: 8.3,
        riskLevel: 4,
        status: "active",
        lastActivity: new Date("2024-01-19"),
    },
    {
        id: "3",
        name: "คุณประยุทธ์ จริงใจ",
        email: "prayuth@email.com",
        phone: "082-345-6789",
        portfolioValue: 15000000,
        ytdReturn: 15.2,
        riskLevel: 8,
        status: "active",
        lastActivity: new Date("2024-01-18"),
    },
    {
        id: "4",
        name: "คุณมานี มีทรัพย์",
        email: "manee@email.com",
        phone: "083-456-7890",
        portfolioValue: 800000,
        ytdReturn: -2.1,
        riskLevel: 3,
        status: "pending",
        lastActivity: new Date("2024-01-15"),
    },
    {
        id: "5",
        name: "คุณวิชัย ร่ำรวย",
        email: "wichai@email.com",
        phone: "084-567-8901",
        portfolioValue: 25000000,
        ytdReturn: 18.7,
        riskLevel: 9,
        status: "active",
        lastActivity: new Date("2024-01-21"),
    },
];

export default function ClientsPage() {
    const [clients] = useState<Client[]>(mockClients);
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState<"all" | "active" | "pending" | "inactive">("all");
    const [selectedClient, setSelectedClient] = useState<Client | null>(null);

    const filteredClients = clients.filter((client) => {
        const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            client.email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === "all" || client.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const totalAUM = clients.reduce((sum, c) => sum + c.portfolioValue, 0);
    const avgReturn = clients.reduce((sum, c) => sum + c.ytdReturn, 0) / clients.length;
    const activeClients = clients.filter((c) => c.status === "active").length;

    const getStatusColor = (status: Client["status"]) => {
        switch (status) {
            case "active": return "bg-green-500/20 text-green-400";
            case "pending": return "bg-yellow-500/20 text-yellow-400";
            case "inactive": return "bg-gray-500/20 text-gray-400";
        }
    };

    const getStatusText = (status: Client["status"]) => {
        switch (status) {
            case "active": return "ใช้งาน";
            case "pending": return "รอดำเนินการ";
            case "inactive": return "ไม่ใช้งาน";
        }
    };

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold">
                    <span className="text-gradient">👥 ลูกค้าของฉัน</span>
                </h1>
                <p className="text-gray-500 mt-2">
                    จัดการและติดตามพอร์ตโฟลิโอของลูกค้า
                </p>
            </div>

            {/* Summary Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    label="👥 ลูกค้าทั้งหมด"
                    value={`${clients.length} คน`}
                    change={`${activeClients} ใช้งาน`}
                    changeType="neutral"
                    icon={Users}
                />
                <MetricCard
                    label="💰 AUM รวม"
                    value={formatCurrency(totalAUM)}
                    change="สินทรัพย์ภายใต้การดูแล"
                    changeType="neutral"
                    icon={TrendingUp}
                />
                <MetricCard
                    label="📈 ผลตอบแทนเฉลี่ย"
                    value={`${avgReturn.toFixed(2)}%`}
                    change="YTD"
                    changeType={avgReturn >= 0 ? "positive" : "negative"}
                    icon={TrendingUp}
                />
                <MetricCard
                    label="⚠️ ต้องติดตาม"
                    value={`${clients.filter(c => c.ytdReturn < 0).length} คน`}
                    change="ผลตอบแทนติดลบ"
                    changeType="negative"
                    icon={AlertCircle}
                />
            </div>

            {/* Filters */}
            <div className="glass-card p-4 mb-6">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="ค้นหาชื่อหรืออีเมล..."
                            className="w-full bg-dark-100 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-gray-500 focus:border-primary focus:outline-none"
                        />
                    </div>
                    <div className="flex gap-2">
                        {(["all", "active", "pending", "inactive"] as const).map((status) => (
                            <button
                                key={status}
                                onClick={() => setStatusFilter(status)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${statusFilter === status
                                        ? "bg-primary text-white"
                                        : "bg-dark-100 text-gray-400 hover:text-white"
                                    }`}
                            >
                                {status === "all" ? "ทั้งหมด" : getStatusText(status)}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Client Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-dark-100">
                            <tr>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">ลูกค้า</th>
                                <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">มูลค่าพอร์ต</th>
                                <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">ผลตอบแทน YTD</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">ความเสี่ยง</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">สถานะ</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">จัดการ</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {filteredClients.map((client) => (
                                <tr key={client.id} className="hover:bg-dark-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-gradient-to-br from-primary to-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                                                {client.name.charAt(3)}
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">{client.name}</p>
                                                <p className="text-sm text-gray-500">{client.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <p className="font-medium text-white">{formatCurrency(client.portfolioValue)}</p>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span className={`font-medium ${client.ytdReturn >= 0 ? "text-green-400" : "text-red-400"}`}>
                                            {client.ytdReturn >= 0 ? "+" : ""}{client.ytdReturn.toFixed(2)}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <div className="flex items-center justify-center gap-1">
                                            {[...Array(10)].map((_, i) => (
                                                <div
                                                    key={i}
                                                    className={`w-2 h-4 rounded-sm ${i < client.riskLevel
                                                            ? client.riskLevel <= 3
                                                                ? "bg-green-500"
                                                                : client.riskLevel <= 6
                                                                    ? "bg-yellow-500"
                                                                    : "bg-red-500"
                                                            : "bg-gray-700"
                                                        }`}
                                                />
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(client.status)}`}>
                                            {getStatusText(client.status)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-center gap-2">
                                            <button
                                                onClick={() => setSelectedClient(client)}
                                                className="p-2 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                                                title="ดูรายละเอียด"
                                            >
                                                <Eye className="w-5 h-5" />
                                            </button>
                                            <button
                                                className="p-2 text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                                                title="ส่งข้อความ"
                                            >
                                                <MessageCircle className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {filteredClients.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>ไม่พบลูกค้าที่ตรงกับเงื่อนไข</p>
                    </div>
                )}
            </div>

            {/* Client Detail Modal */}
            {selectedClient && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="glass-card w-full max-w-lg p-6">
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center gap-4">
                                <div className="w-16 h-16 bg-gradient-to-br from-primary to-blue-500 rounded-full flex items-center justify-center text-2xl text-white font-medium">
                                    {selectedClient.name.charAt(3)}
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-white">{selectedClient.name}</h3>
                                    <p className="text-gray-400">{selectedClient.email}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedClient(null)}
                                className="text-gray-400 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-4 bg-dark-100 rounded-lg">
                                <p className="text-sm text-gray-500">มูลค่าพอร์ต</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(selectedClient.portfolioValue)}</p>
                            </div>
                            <div className="p-4 bg-dark-100 rounded-lg">
                                <p className="text-sm text-gray-500">ผลตอบแทน YTD</p>
                                <p className={`text-xl font-bold ${selectedClient.ytdReturn >= 0 ? "text-green-400" : "text-red-400"}`}>
                                    {selectedClient.ytdReturn >= 0 ? "+" : ""}{selectedClient.ytdReturn.toFixed(2)}%
                                </p>
                            </div>
                            <div className="p-4 bg-dark-100 rounded-lg">
                                <p className="text-sm text-gray-500">เบอร์โทร</p>
                                <p className="text-white font-medium">{selectedClient.phone}</p>
                            </div>
                            <div className="p-4 bg-dark-100 rounded-lg">
                                <p className="text-sm text-gray-500">ระดับความเสี่ยง</p>
                                <p className="text-white font-medium">{selectedClient.riskLevel}/10</p>
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <Button className="flex-1">
                                <Eye className="w-4 h-4 mr-2" />
                                ดูพอร์ตโฟลิโอ
                            </Button>
                            <Button variant="secondary" className="flex-1">
                                <MessageCircle className="w-4 h-4 mr-2" />
                                ส่งข้อความ
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
}
