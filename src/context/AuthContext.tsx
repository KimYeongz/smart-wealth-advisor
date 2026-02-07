"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User } from "@/types";

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
    logout: () => void;
    register: (data: RegisterData) => Promise<{ success: boolean; message: string }>;
}

interface RegisterData {
    email: string;
    password: string;
    fullName: string;
    phone?: string;
}

// Mock users for development - passwords are shown for testing
const MOCK_USERS: Record<string, User & { password: string }> = {
    "client@example.com": {
        id: "user-001",
        email: "client@example.com",
        password: "client123",
        full_name: "คุณสมชาย ใจดี",
        role: "client",
        phone: "081-234-5678",
        advisor_id: "user-002",
    },
    "advisor@example.com": {
        id: "user-002",
        email: "advisor@example.com",
        password: "advisor123",
        full_name: "คุณพิชชาพล ดวิเม",
        role: "advisor",
        phone: "082-345-6789",
    },
    "admin@example.com": {
        id: "user-003",
        email: "admin@example.com",
        password: "admin123",
        full_name: "Admin User",
        role: "admin",
        phone: "083-456-7890",
    },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for stored user on mount
        const storedUser = localStorage.getItem("wealth_advisor_user");
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch {
                localStorage.removeItem("wealth_advisor_user");
            }
        }
        setIsLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        setIsLoading(true);

        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 500));

        const normalizedEmail = email.toLowerCase().trim();
        const mockUser = MOCK_USERS[normalizedEmail];

        if (mockUser && mockUser.password === password) {
            const { password: _, ...userWithoutPassword } = mockUser;
            setUser(userWithoutPassword);
            localStorage.setItem("wealth_advisor_user", JSON.stringify(userWithoutPassword));
            setIsLoading(false);
            return { success: true, message: "เข้าสู่ระบบสำเร็จ" };
        }

        setIsLoading(false);
        return { success: false, message: "อีเมลหรือรหัสผ่านไม่ถูกต้อง" };
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem("wealth_advisor_user");
    };

    const register = async (data: RegisterData) => {
        setIsLoading(true);
        await new Promise((resolve) => setTimeout(resolve, 500));

        const normalizedEmail = data.email.toLowerCase().trim();

        if (MOCK_USERS[normalizedEmail]) {
            setIsLoading(false);
            return { success: false, message: "อีเมลนี้ถูกใช้งานแล้ว" };
        }

        // Create new user
        const newUser: User = {
            id: `user-${Date.now()}`,
            email: normalizedEmail,
            full_name: data.fullName,
            role: "client",
            phone: data.phone,
        };

        setUser(newUser);
        localStorage.setItem("wealth_advisor_user", JSON.stringify(newUser));
        setIsLoading(false);

        return { success: true, message: "ลงทะเบียนสำเร็จ" };
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, login, logout, register }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
