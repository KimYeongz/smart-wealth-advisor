"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { createClient, isMockMode } from "@/lib/supabase/client";
import { User } from "@/types";

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
    logout: () => Promise<void>;
    register: (data: RegisterData) => Promise<{ success: boolean; message: string }>;
}

interface RegisterData {
    email: string;
    password: string;
    fullName: string;
    phone?: string;
}

// Mock users for development when Supabase is not configured
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
        if (isMockMode()) {
            // Mock mode - check localStorage
            const storedUser = localStorage.getItem("wealth_advisor_user");
            if (storedUser) {
                try {
                    setUser(JSON.parse(storedUser));
                } catch {
                    localStorage.removeItem("wealth_advisor_user");
                }
            }
            setIsLoading(false);
            return;
        }

        // Supabase mode - check session
        const supabase = createClient();

        // Get initial session
        supabase.auth.getSession().then(async ({ data: { session } }) => {
            if (session?.user) {
                const profile = await fetchProfile(session.user.id);
                setUser(profile);
            }
            setIsLoading(false);
        });

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, session) => {
                if (event === "SIGNED_IN" && session?.user) {
                    const profile = await fetchProfile(session.user.id);
                    setUser(profile);
                } else if (event === "SIGNED_OUT") {
                    setUser(null);
                }
            }
        );

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    // Fetch user profile from Supabase
    async function fetchProfile(userId: string): Promise<User | null> {
        const supabase = createClient();
        const { data, error } = await supabase
            .from("profiles")
            .select("*")
            .eq("id", userId)
            .single();

        if (error || !data) {
            console.error("Error fetching profile:", error);
            return null;
        }

        return {
            id: data.id,
            email: data.email,
            full_name: data.full_name,
            role: data.role,
            phone: data.phone,
            advisor_id: data.advisor_id,
        };
    }

    const login = async (email: string, password: string) => {
        setIsLoading(true);
        const normalizedEmail = email.toLowerCase().trim();

        if (isMockMode()) {
            // Mock login
            await new Promise((resolve) => setTimeout(resolve, 500));
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
        }

        // Supabase login
        const supabase = createClient();
        const { data, error } = await supabase.auth.signInWithPassword({
            email: normalizedEmail,
            password,
        });

        if (error) {
            setIsLoading(false);
            return {
                success: false,
                message: error.message === "Invalid login credentials"
                    ? "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
                    : error.message
            };
        }

        if (data.user) {
            const profile = await fetchProfile(data.user.id);
            setUser(profile);
        }

        setIsLoading(false);
        return { success: true, message: "เข้าสู่ระบบสำเร็จ" };
    };

    const logout = async () => {
        if (isMockMode()) {
            setUser(null);
            localStorage.removeItem("wealth_advisor_user");
            return;
        }

        const supabase = createClient();
        await supabase.auth.signOut();
        setUser(null);
    };

    const register = async (data: RegisterData) => {
        setIsLoading(true);
        const normalizedEmail = data.email.toLowerCase().trim();

        if (isMockMode()) {
            // Mock register
            await new Promise((resolve) => setTimeout(resolve, 500));

            if (MOCK_USERS[normalizedEmail]) {
                setIsLoading(false);
                return { success: false, message: "อีเมลนี้ถูกใช้งานแล้ว" };
            }

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
        }

        // Supabase register
        const supabase = createClient();
        const { data: authData, error } = await supabase.auth.signUp({
            email: normalizedEmail,
            password: data.password,
            options: {
                data: {
                    full_name: data.fullName,
                    phone: data.phone,
                },
            },
        });

        if (error) {
            setIsLoading(false);
            if (error.message.includes("already registered")) {
                return { success: false, message: "อีเมลนี้ถูกใช้งานแล้ว" };
            }
            return { success: false, message: error.message };
        }

        if (authData.user) {
            // Wait a moment for trigger to create profile
            await new Promise((resolve) => setTimeout(resolve, 500));
            const profile = await fetchProfile(authData.user.id);
            setUser(profile);
        }

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
