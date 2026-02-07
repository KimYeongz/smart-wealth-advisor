"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatThaiDate } from "@/lib/utils";
import { Users, UserPlus, Shield, Search, Edit, Trash2, MoreVertical, Check, X } from "lucide-react";

interface User {
    id: string;
    name: string;
    email: string;
    role: "client" | "advisor" | "admin";
    status: "active" | "suspended" | "pending";
    createdAt: Date;
    lastLogin: Date | null;
}

const mockUsers: User[] = [
    { id: "1", name: "คุณสมชาย ใจดี", email: "somchai@email.com", role: "client", status: "active", createdAt: new Date("2023-06-15"), lastLogin: new Date("2024-01-20") },
    { id: "2", name: "คุณพิชชาพล ดวิเม", email: "advisor@smartwealth.th", role: "advisor", status: "active", createdAt: new Date("2023-01-01"), lastLogin: new Date("2024-01-21") },
    { id: "3", name: "คุณสมหญิง รักเรียน", email: "somying@email.com", role: "client", status: "active", createdAt: new Date("2023-08-20"), lastLogin: new Date("2024-01-19") },
    { id: "4", name: "คุณมานี มีทรัพย์", email: "manee@email.com", role: "client", status: "pending", createdAt: new Date("2024-01-15"), lastLogin: null },
    { id: "5", name: "คุณวิชัย ร่ำรวย", email: "wichai@email.com", role: "client", status: "suspended", createdAt: new Date("2023-03-10"), lastLogin: new Date("2023-12-01") },
    { id: "6", name: "Admin System", email: "admin@smartwealth.th", role: "admin", status: "active", createdAt: new Date("2022-01-01"), lastLogin: new Date("2024-01-21") },
];

export default function UsersPage() {
    const [users, setUsers] = useState<User[]>(mockUsers);
    const [searchTerm, setSearchTerm] = useState("");
    const [roleFilter, setRoleFilter] = useState<"all" | "client" | "advisor" | "admin">("all");
    const [showAddModal, setShowAddModal] = useState(false);
    const [newUser, setNewUser] = useState({ name: "", email: "", role: "client" as User["role"] });

    const filteredUsers = users.filter((user) => {
        const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesRole = roleFilter === "all" || user.role === roleFilter;
        return matchesSearch && matchesRole;
    });

    const getRoleColor = (role: User["role"]) => {
        switch (role) {
            case "admin": return "bg-red-500/20 text-red-400";
            case "advisor": return "bg-blue-500/20 text-blue-400";
            case "client": return "bg-green-500/20 text-green-400";
        }
    };

    const getRoleText = (role: User["role"]) => {
        switch (role) {
            case "admin": return "ผู้ดูแลระบบ";
            case "advisor": return "ที่ปรึกษา";
            case "client": return "ลูกค้า";
        }
    };

    const getStatusText = (status: User["status"]) => {
        switch (status) {
            case "active": return "ใช้งาน";
            case "suspended": return "ระงับ";
            case "pending": return "รอยืนยัน";
        }
    };

    const handleAddUser = () => {
        if (!newUser.name || !newUser.email) return;
        const user: User = {
            id: `${Date.now()}`,
            ...newUser,
            status: "pending",
            createdAt: new Date(),
            lastLogin: null,
        };
        setUsers((prev) => [user, ...prev]);
        setNewUser({ name: "", email: "", role: "client" });
        setShowAddModal(false);
    };

    const handleDeleteUser = (userId: string) => {
        setUsers((prev) => prev.filter((u) => u.id !== userId));
    };

    const handleToggleStatus = (userId: string) => {
        setUsers((prev) => prev.map((u) => {
            if (u.id === userId) {
                return { ...u, status: u.status === "active" ? "suspended" : "active" };
            }
            return u;
        }));
    };

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">
                        <span className="text-gradient">⚙️ จัดการผู้ใช้</span>
                    </h1>
                    <p className="text-gray-500 mt-2">จัดการบัญชีผู้ใช้ในระบบ</p>
                </div>
                <Button onClick={() => setShowAddModal(true)}>
                    <UserPlus className="w-4 h-4 mr-2" />
                    เพิ่มผู้ใช้
                </Button>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    label="👥 ผู้ใช้ทั้งหมด"
                    value={`${users.length} คน`}
                    change={`${users.filter(u => u.status === "active").length} ใช้งาน`}
                    changeType="neutral"
                    icon={Users}
                />
                <MetricCard
                    label="👤 ลูกค้า"
                    value={`${users.filter(u => u.role === "client").length} คน`}
                    change="Client accounts"
                    changeType="neutral"
                    icon={Users}
                />
                <MetricCard
                    label="👨‍💼 ที่ปรึกษา"
                    value={`${users.filter(u => u.role === "advisor").length} คน`}
                    change="Advisor accounts"
                    changeType="neutral"
                    icon={Shield}
                />
                <MetricCard
                    label="🔐 ผู้ดูแล"
                    value={`${users.filter(u => u.role === "admin").length} คน`}
                    change="Admin accounts"
                    changeType="neutral"
                    icon={Shield}
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
                        {(["all", "client", "advisor", "admin"] as const).map((role) => (
                            <button
                                key={role}
                                onClick={() => setRoleFilter(role)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${roleFilter === role
                                        ? "bg-primary text-white"
                                        : "bg-dark-100 text-gray-400 hover:text-white"
                                    }`}
                            >
                                {role === "all" ? "ทั้งหมด" : getRoleText(role)}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-dark-100">
                            <tr>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">ผู้ใช้</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">บทบาท</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">สถานะ</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">สมัครเมื่อ</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">เข้าใช้ล่าสุด</th>
                                <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">จัดการ</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {filteredUsers.map((user) => (
                                <tr key={user.id} className="hover:bg-dark-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-medium ${user.role === "admin" ? "bg-gradient-to-br from-red-500 to-orange-500" :
                                                    user.role === "advisor" ? "bg-gradient-to-br from-blue-500 to-purple-500" :
                                                        "bg-gradient-to-br from-primary to-teal-500"
                                                }`}>
                                                {user.name.charAt(3)}
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">{user.name}</p>
                                                <p className="text-sm text-gray-500">{user.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                                            {getRoleText(user.role)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${user.status === "active" ? "bg-green-500/20 text-green-400" :
                                                user.status === "pending" ? "bg-yellow-500/20 text-yellow-400" :
                                                    "bg-red-500/20 text-red-400"
                                            }`}>
                                            {getStatusText(user.status)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-center text-gray-400 text-sm">
                                        {formatThaiDate(user.createdAt)}
                                    </td>
                                    <td className="px-6 py-4 text-center text-gray-400 text-sm">
                                        {user.lastLogin ? formatThaiDate(user.lastLogin) : "-"}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-center gap-2">
                                            <button
                                                onClick={() => handleToggleStatus(user.id)}
                                                className={`p-2 rounded-lg transition-colors ${user.status === "active"
                                                        ? "text-red-400 hover:bg-red-500/10"
                                                        : "text-green-400 hover:bg-green-500/10"
                                                    }`}
                                                title={user.status === "active" ? "ระงับ" : "เปิดใช้งาน"}
                                            >
                                                {user.status === "active" ? <X className="w-5 h-5" /> : <Check className="w-5 h-5" />}
                                            </button>
                                            <button
                                                onClick={() => handleDeleteUser(user.id)}
                                                className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                                title="ลบ"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add User Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="glass-card w-full max-w-md p-6">
                        <h3 className="text-xl font-semibold text-white mb-6">➕ เพิ่มผู้ใช้ใหม่</h3>
                        <div className="space-y-4">
                            <Input
                                label="ชื่อ-นามสกุล"
                                value={newUser.name}
                                onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                                placeholder="คุณสมชาย ใจดี"
                            />
                            <Input
                                label="อีเมล"
                                type="email"
                                value={newUser.email}
                                onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                                placeholder="email@example.com"
                            />
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">บทบาท</label>
                                <select
                                    value={newUser.role}
                                    onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value as User["role"] }))}
                                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-primary focus:outline-none"
                                >
                                    <option value="client">ลูกค้า</option>
                                    <option value="advisor">ที่ปรึกษา</option>
                                    <option value="admin">ผู้ดูแลระบบ</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <Button variant="secondary" onClick={() => setShowAddModal(false)} className="flex-1">
                                ยกเลิก
                            </Button>
                            <Button onClick={handleAddUser} className="flex-1">
                                เพิ่มผู้ใช้
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
}
