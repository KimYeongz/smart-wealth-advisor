"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Bell, Lock, User, Palette, Globe, Shield, Save, Check } from "lucide-react";

interface SettingsSection {
    id: string;
    title: string;
    icon: React.ReactNode;
}

const sections: SettingsSection[] = [
    { id: "profile", title: "โปรไฟล์", icon: <User className="w-5 h-5" /> },
    { id: "notifications", title: "การแจ้งเตือน", icon: <Bell className="w-5 h-5" /> },
    { id: "security", title: "ความปลอดภัย", icon: <Lock className="w-5 h-5" /> },
    { id: "appearance", title: "ธีมและการแสดงผล", icon: <Palette className="w-5 h-5" /> },
];

export default function SettingsPage() {
    const [activeSection, setActiveSection] = useState("profile");
    const [saved, setSaved] = useState(false);

    // Profile settings
    const [profile, setProfile] = useState({
        name: "คุณสมชาย ใจดี",
        email: "somchai@email.com",
        phone: "089-123-4567",
        language: "th",
    });

    // Notification settings
    const [notifications, setNotifications] = useState({
        email: true,
        push: true,
        sms: false,
        portfolioUpdates: true,
        marketNews: true,
        advisorMessages: true,
        monthlyReport: true,
    });

    // Security settings
    const [security, setSecurity] = useState({
        twoFactor: false,
        sessionTimeout: "30",
        loginAlerts: true,
    });

    // Appearance settings
    const [appearance, setAppearance] = useState({
        theme: "dark",
        compactMode: false,
        animationsEnabled: true,
    });

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const Toggle = ({ enabled, onChange }: { enabled: boolean; onChange: () => void }) => (
        <button
            onClick={onChange}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${enabled ? "bg-primary" : "bg-gray-600"
                }`}
        >
            <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? "translate-x-6" : "translate-x-1"
                    }`}
            />
        </button>
    );

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">
                        <span className="text-gradient">⚙️ ตั้งค่า</span>
                    </h1>
                    <p className="text-gray-500 mt-2">จัดการการตั้งค่าบัญชีและการแจ้งเตือน</p>
                </div>
                <Button onClick={handleSave}>
                    {saved ? <Check className="w-4 h-4 mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                    {saved ? "บันทึกแล้ว" : "บันทึก"}
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar */}
                <div className="glass-card p-4 h-fit">
                    <nav className="space-y-1">
                        {sections.map((section) => (
                            <button
                                key={section.id}
                                onClick={() => setActiveSection(section.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${activeSection === section.id
                                        ? "bg-primary/10 text-primary border border-primary/30"
                                        : "text-gray-400 hover:text-white hover:bg-dark-50"
                                    }`}
                            >
                                {section.icon}
                                {section.title}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content */}
                <div className="lg:col-span-3">
                    <div className="glass-card p-6">
                        {/* Profile Section */}
                        {activeSection === "profile" && (
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-6">👤 โปรไฟล์</h3>
                                <div className="space-y-6">
                                    <div className="flex items-center gap-6 mb-8">
                                        <div className="w-20 h-20 bg-gradient-to-br from-primary to-blue-500 rounded-full flex items-center justify-center text-3xl text-white">
                                            👤
                                        </div>
                                        <div>
                                            <Button variant="secondary" size="sm">เปลี่ยนรูปโปรไฟล์</Button>
                                            <p className="text-sm text-gray-500 mt-2">JPG, PNG ขนาดไม่เกิน 2MB</p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <Input
                                            label="ชื่อ-นามสกุล"
                                            value={profile.name}
                                            onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                                        />
                                        <Input
                                            label="อีเมล"
                                            type="email"
                                            value={profile.email}
                                            onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                                        />
                                        <Input
                                            label="เบอร์โทรศัพท์"
                                            value={profile.phone}
                                            onChange={(e) => setProfile(prev => ({ ...prev, phone: e.target.value }))}
                                        />
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">ภาษา</label>
                                            <select
                                                value={profile.language}
                                                onChange={(e) => setProfile(prev => ({ ...prev, language: e.target.value }))}
                                                className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-primary focus:outline-none"
                                            >
                                                <option value="th">🇹🇭 ไทย</option>
                                                <option value="en">🇬🇧 English</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Notifications Section */}
                        {activeSection === "notifications" && (
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-6">🔔 การแจ้งเตือน</h3>

                                <div className="space-y-6">
                                    <div>
                                        <h4 className="font-medium text-white mb-4">ช่องทางการแจ้งเตือน</h4>
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">อีเมล</p>
                                                    <p className="text-sm text-gray-500">รับการแจ้งเตือนทางอีเมล</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.email}
                                                    onChange={() => setNotifications(prev => ({ ...prev, email: !prev.email }))}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">Push Notification</p>
                                                    <p className="text-sm text-gray-500">รับการแจ้งเตือนบนเบราว์เซอร์</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.push}
                                                    onChange={() => setNotifications(prev => ({ ...prev, push: !prev.push }))}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">SMS</p>
                                                    <p className="text-sm text-gray-500">รับการแจ้งเตือนทาง SMS</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.sms}
                                                    onChange={() => setNotifications(prev => ({ ...prev, sms: !prev.sms }))}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-white mb-4">ประเภทการแจ้งเตือน</h4>
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">อัพเดทพอร์ตโฟลิโอ</p>
                                                    <p className="text-sm text-gray-500">เมื่อมีการเปลี่ยนแปลงในพอร์ต</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.portfolioUpdates}
                                                    onChange={() => setNotifications(prev => ({ ...prev, portfolioUpdates: !prev.portfolioUpdates }))}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">ข่าวตลาด</p>
                                                    <p className="text-sm text-gray-500">ข่าวสารและบทวิเคราะห์</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.marketNews}
                                                    onChange={() => setNotifications(prev => ({ ...prev, marketNews: !prev.marketNews }))}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">ข้อความจากที่ปรึกษา</p>
                                                    <p className="text-sm text-gray-500">เมื่อที่ปรึกษาติดต่อ</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.advisorMessages}
                                                    onChange={() => setNotifications(prev => ({ ...prev, advisorMessages: !prev.advisorMessages }))}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                                <div>
                                                    <p className="text-white">รายงานรายเดือน</p>
                                                    <p className="text-sm text-gray-500">สรุปผลการดำเนินงานทุกเดือน</p>
                                                </div>
                                                <Toggle
                                                    enabled={notifications.monthlyReport}
                                                    onChange={() => setNotifications(prev => ({ ...prev, monthlyReport: !prev.monthlyReport }))}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Security Section */}
                        {activeSection === "security" && (
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-6">🔒 ความปลอดภัย</h3>
                                <div className="space-y-6">
                                    <div className="p-4 bg-dark-100 rounded-lg">
                                        <div className="flex items-center justify-between mb-4">
                                            <div>
                                                <p className="text-white font-medium">ยืนยันตัวตน 2 ขั้นตอน (2FA)</p>
                                                <p className="text-sm text-gray-500">เพิ่มความปลอดภัยด้วย OTP</p>
                                            </div>
                                            <Toggle
                                                enabled={security.twoFactor}
                                                onChange={() => setSecurity(prev => ({ ...prev, twoFactor: !prev.twoFactor }))}
                                            />
                                        </div>
                                        {security.twoFactor && (
                                            <Button variant="secondary" size="sm">ตั้งค่า 2FA</Button>
                                        )}
                                    </div>

                                    <div className="p-4 bg-dark-100 rounded-lg">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-white font-medium">แจ้งเตือนเมื่อมีการล็อกอิน</p>
                                                <p className="text-sm text-gray-500">รับอีเมลเมื่อมีการเข้าสู่ระบบจากอุปกรณ์ใหม่</p>
                                            </div>
                                            <Toggle
                                                enabled={security.loginAlerts}
                                                onChange={() => setSecurity(prev => ({ ...prev, loginAlerts: !prev.loginAlerts }))}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">หมดเวลาเซสชัน (นาที)</label>
                                        <select
                                            value={security.sessionTimeout}
                                            onChange={(e) => setSecurity(prev => ({ ...prev, sessionTimeout: e.target.value }))}
                                            className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-primary focus:outline-none"
                                        >
                                            <option value="15">15 นาที</option>
                                            <option value="30">30 นาที</option>
                                            <option value="60">1 ชั่วโมง</option>
                                            <option value="120">2 ชั่วโมง</option>
                                        </select>
                                    </div>

                                    <div className="pt-4 border-t border-gray-700">
                                        <Button variant="secondary">เปลี่ยนรหัสผ่าน</Button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Appearance Section */}
                        {activeSection === "appearance" && (
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-6">🎨 ธีมและการแสดงผล</h3>
                                <div className="space-y-6">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-4">ธีม</label>
                                        <div className="grid grid-cols-3 gap-4">
                                            {[
                                                { id: "dark", label: "มืด", icon: "🌙" },
                                                { id: "light", label: "สว่าง", icon: "☀️" },
                                                { id: "system", label: "ตามระบบ", icon: "💻" },
                                            ].map((theme) => (
                                                <button
                                                    key={theme.id}
                                                    onClick={() => setAppearance(prev => ({ ...prev, theme: theme.id }))}
                                                    className={`p-4 rounded-lg border text-center transition-colors ${appearance.theme === theme.id
                                                            ? "border-primary bg-primary/10"
                                                            : "border-gray-700 bg-dark-100 hover:border-gray-600"
                                                        }`}
                                                >
                                                    <span className="text-2xl">{theme.icon}</span>
                                                    <p className="text-sm text-white mt-2">{theme.label}</p>
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                        <div>
                                            <p className="text-white">โหมด Compact</p>
                                            <p className="text-sm text-gray-500">แสดงผลแบบกระชับ</p>
                                        </div>
                                        <Toggle
                                            enabled={appearance.compactMode}
                                            onChange={() => setAppearance(prev => ({ ...prev, compactMode: !prev.compactMode }))}
                                        />
                                    </div>

                                    <div className="flex items-center justify-between p-4 bg-dark-100 rounded-lg">
                                        <div>
                                            <p className="text-white">เปิดใช้ Animation</p>
                                            <p className="text-sm text-gray-500">เอฟเฟกต์การเคลื่อนไหว</p>
                                        </div>
                                        <Toggle
                                            enabled={appearance.animationsEnabled}
                                            onChange={() => setAppearance(prev => ({ ...prev, animationsEnabled: !prev.animationsEnabled }))}
                                        />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
