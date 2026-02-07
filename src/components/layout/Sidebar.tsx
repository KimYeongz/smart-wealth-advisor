"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Wallet,
    BarChart3,
    Calculator,
    FileText,
    Phone,
    Users,
    Settings,
    LogOut,
    ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface SidebarProps {
    userRole?: "client" | "advisor" | "admin";
    userName?: string;
    onLogout?: () => void;
}

const menuItems = {
    client: [
        { href: "/dashboard", icon: LayoutDashboard, label: "แดชบอร์ด" },
        { href: "/portfolio", icon: Wallet, label: "จัดการพอร์ต" },
        { href: "/monte-carlo", icon: BarChart3, label: "Monte Carlo" },
        { href: "/tax-planner", icon: Calculator, label: "วางแผนภาษี" },
        { href: "/reports", icon: FileText, label: "รายงาน PDF" },
        { href: "/contact-advisor", icon: Phone, label: "ติดต่อที่ปรึกษา" },
    ],
    advisor: [
        { href: "/dashboard", icon: LayoutDashboard, label: "แดชบอร์ด" },
        { href: "/portfolio", icon: Wallet, label: "จัดการพอร์ต" },
        { href: "/clients", icon: Users, label: "ลูกค้าของฉัน" },
        { href: "/monte-carlo", icon: BarChart3, label: "Monte Carlo" },
        { href: "/reports", icon: FileText, label: "รายงาน PDF" },
    ],
    admin: [
        { href: "/dashboard", icon: LayoutDashboard, label: "แดชบอร์ด" },
        { href: "/portfolio", icon: Wallet, label: "จัดการพอร์ต" },
        { href: "/users", icon: Users, label: "จัดการผู้ใช้" },
        { href: "/monte-carlo", icon: BarChart3, label: "Monte Carlo" },
        { href: "/tax-planner", icon: Calculator, label: "วางแผนภาษี" },
        { href: "/reports", icon: FileText, label: "รายงาน PDF" },
        { href: "/settings", icon: Settings, label: "ตั้งค่า" },
    ],
};

export function Sidebar({ userRole = "client", userName = "ผู้ใช้", onLogout }: SidebarProps) {
    const pathname = usePathname();
    const [collapsed, setCollapsed] = useState(false);
    const items = menuItems[userRole];

    return (
        <aside
            className={cn(
                "fixed left-0 top-0 h-screen bg-dark-100 border-r border-gray-800",
                "flex flex-col transition-all duration-300 z-50",
                collapsed ? "w-20" : "w-64"
            )}
        >
            {/* Logo */}
            <div className="p-6 border-b border-gray-800">
                <Link href="/dashboard" className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
                        <span className="text-xl">💎</span>
                    </div>
                    {!collapsed && (
                        <div>
                            <h1 className="font-bold text-white">ที่ปรึกษาการเงิน</h1>
                            <p className="text-xs text-gray-500">ระบบจัดการพอร์ตอัจฉริยะ</p>
                        </div>
                    )}
                </Link>
            </div>

            {/* Toggle button */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="absolute -right-3 top-20 w-6 h-6 bg-dark-100 border border-gray-700 rounded-full
                   flex items-center justify-center hover:bg-dark-50 transition-colors"
            >
                <ChevronLeft
                    className={cn("w-4 h-4 text-gray-400 transition-transform", collapsed && "rotate-180")}
                />
            </button>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {items.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "sidebar-item",
                                isActive && "active",
                                collapsed && "justify-center px-2"
                            )}
                            title={collapsed ? item.label : undefined}
                        >
                            <item.icon className="w-5 h-5 flex-shrink-0" />
                            {!collapsed && <span>{item.label}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* User section */}
            <div className="p-4 border-t border-gray-800">
                <div className={cn("flex items-center gap-3 mb-3", collapsed && "justify-center")}>
                    <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold">{userName.charAt(0)}</span>
                    </div>
                    {!collapsed && (
                        <div>
                            <p className="text-sm font-medium text-white truncate">{userName}</p>
                            <p className="text-xs text-gray-500 capitalize">{userRole}</p>
                        </div>
                    )}
                </div>
                <button
                    onClick={onLogout}
                    className={cn(
                        "flex items-center gap-3 w-full px-4 py-2.5 rounded-lg",
                        "text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-all",
                        collapsed && "justify-center px-2"
                    )}
                    title={collapsed ? "ออกจากระบบ" : undefined}
                >
                    <LogOut className="w-5 h-5" />
                    {!collapsed && <span>ออกจากระบบ</span>}
                </button>
            </div>
        </aside>
    );
}
