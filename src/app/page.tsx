"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export default function LoginPage() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [fullName, setFullName] = useState("");
    const [phone, setPhone] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { login, register } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            let result;

            if (isLogin) {
                result = await login(email, password);
            } else {
                result = await register({ email, password, fullName, phone });
            }

            if (result.success) {
                router.push("/dashboard");
            } else {
                setError(result.message);
            }
        } catch (err) {
            setError("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left side - form */}
            <div className="flex-1 flex items-center justify-center p-8">
                <div className="w-full max-w-md">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-2xl mb-4">
                            <span className="text-3xl">💎</span>
                        </div>
                        <h1 className="text-2xl font-bold text-gradient">Smart Wealth Advisor</h1>
                        <p className="text-gray-500 mt-2">ระบบจัดการพอร์ตการลงทุนอัจฉริยะ</p>
                    </div>

                    {/* Form card */}
                    <div className="glass-card p-8">
                        <h2 className="text-xl font-bold text-white mb-6">
                            {isLogin ? "เข้าสู่ระบบ" : "สมัครสมาชิก"}
                        </h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            {!isLogin && (
                                <>
                                    <Input
                                        label="ชื่อ-นามสกุล"
                                        type="text"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        placeholder="กรุณากรอกชื่อ-นามสกุล"
                                        required
                                    />
                                    <Input
                                        label="เบอร์โทรศัพท์"
                                        type="tel"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                        placeholder="081-234-5678"
                                    />
                                </>
                            )}

                            <Input
                                label="อีเมล"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="email@example.com"
                                required
                            />

                            <Input
                                label="รหัสผ่าน"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                            />

                            {error && (
                                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                                    <p className="text-sm text-red-400">{error}</p>
                                </div>
                            )}

                            <Button
                                type="submit"
                                className="w-full"
                                isLoading={isSubmitting}
                            >
                                {isLogin ? "เข้าสู่ระบบ" : "สมัครสมาชิก"}
                            </Button>
                        </form>

                        <div className="mt-6 text-center">
                            <p className="text-gray-400 text-sm">
                                {isLogin ? "ยังไม่มีบัญชี?" : "มีบัญชีอยู่แล้ว?"}
                                <button
                                    type="button"
                                    onClick={() => {
                                        setIsLogin(!isLogin);
                                        setError("");
                                    }}
                                    className="text-primary hover:underline ml-1 font-medium"
                                >
                                    {isLogin ? "สมัครสมาชิก" : "เข้าสู่ระบบ"}
                                </button>
                            </p>
                        </div>

                        {/* Demo accounts */}
                        {isLogin && (
                            <div className="mt-6 p-4 bg-dark-100 rounded-lg">
                                <p className="text-xs text-gray-500 mb-2">🔑 บัญชีทดสอบ:</p>
                                <div className="space-y-1 text-xs">
                                    <p className="text-gray-400">
                                        <span className="text-primary">Client:</span> client@example.com / client123
                                    </p>
                                    <p className="text-gray-400">
                                        <span className="text-yellow-400">Advisor:</span> advisor@example.com / advisor123
                                    </p>
                                    <p className="text-gray-400">
                                        <span className="text-red-400">Admin:</span> admin@example.com / admin123
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Right side - hero */}
            <div className="hidden lg:flex flex-1 bg-gradient-to-br from-dark-100 to-dark-300 items-center justify-center p-8 relative overflow-hidden">
                {/* Background decoration */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary rounded-full blur-3xl" />
                    <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-gold rounded-full blur-3xl" />
                </div>

                <div className="relative z-10 text-center max-w-lg">
                    <h2 className="text-4xl font-bold text-white mb-4">
                        จัดการการเงินของคุณ
                        <br />
                        <span className="text-gradient">อย่างชาญฉลาด</span>
                    </h2>
                    <p className="text-gray-400 text-lg">
                        ระบบที่ปรึกษาการเงินอัจฉริยะ พร้อมเครื่องมือวิเคราะห์ขั้นสูง
                        ช่วยให้คุณบรรลุเป้าหมายทางการเงิน
                    </p>

                    <div className="mt-8 flex justify-center gap-8">
                        <div className="text-center">
                            <p className="text-3xl font-bold text-primary">฿500M+</p>
                            <p className="text-sm text-gray-500">มูลค่าบริหาร</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold text-gold">1,000+</p>
                            <p className="text-sm text-gray-500">ลูกค้าที่ไว้วางใจ</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold text-white">15%</p>
                            <p className="text-sm text-gray-500">ผลตอบแทนเฉลี่ย</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
