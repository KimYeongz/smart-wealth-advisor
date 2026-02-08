// Portfolio Service - Supabase operations for portfolio data
import { createClient, isMockMode } from "@/lib/supabase/client";

export interface Portfolio {
    id: string;
    userId: string;
    cashBalance: number;
    investedAmount: number;
    allocation: {
        thai: number;
        us: number;
        gold: number;
        bonds: number;
    };
    createdAt: Date;
    updatedAt: Date;
}

export interface Transaction {
    id: string;
    userId: string;
    type: "deposit" | "withdraw" | "invest";
    amount: number;
    description: string;
    createdAt: Date;
}

// Local storage key for mock mode
const PORTFOLIO_KEY = "portfolio";
const TRANSACTIONS_KEY = "transactions";

// Get portfolio for a user
export async function getPortfolio(userId: string): Promise<Portfolio | null> {
    if (isMockMode()) {
        const saved = localStorage.getItem(PORTFOLIO_KEY);
        if (saved) {
            const data = JSON.parse(saved);
            return {
                id: "mock-portfolio",
                userId,
                cashBalance: data.cashBalance || 0,
                investedAmount: data.invested || 0,
                allocation: data.allocation || { thai: 25, us: 25, gold: 25, bonds: 25 },
                createdAt: new Date(),
                updatedAt: new Date(),
            };
        }
        return null;
    }

    const supabase = createClient();
    const { data, error } = await supabase
        .from("portfolios")
        .select("*")
        .eq("user_id", userId)
        .single();

    if (error || !data) {
        console.error("Error fetching portfolio:", error);
        return null;
    }

    return {
        id: data.id,
        userId: data.user_id,
        cashBalance: parseFloat(data.cash_balance) || 0,
        investedAmount: parseFloat(data.invested_amount) || 0,
        allocation: {
            thai: data.thai_allocation,
            us: data.us_allocation,
            gold: data.gold_allocation,
            bonds: data.bonds_allocation,
        },
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
    };
}

// Update portfolio
export async function updatePortfolio(
    userId: string,
    updates: Partial<{
        cashBalance: number;
        investedAmount: number;
        allocation: { thai: number; us: number; gold: number; bonds: number };
    }>
): Promise<boolean> {
    if (isMockMode()) {
        const saved = localStorage.getItem(PORTFOLIO_KEY);
        const current = saved ? JSON.parse(saved) : { cashBalance: 0, invested: 0, allocation: { thai: 25, us: 25, gold: 25, bonds: 25 } };

        const updated = {
            ...current,
            cashBalance: updates.cashBalance ?? current.cashBalance,
            invested: updates.investedAmount ?? current.invested,
            allocation: updates.allocation ?? current.allocation,
        };

        localStorage.setItem(PORTFOLIO_KEY, JSON.stringify(updated));
        return true;
    }

    const supabase = createClient();

    const updateData: Record<string, unknown> = {};
    if (updates.cashBalance !== undefined) updateData.cash_balance = updates.cashBalance;
    if (updates.investedAmount !== undefined) updateData.invested_amount = updates.investedAmount;
    if (updates.allocation) {
        updateData.thai_allocation = updates.allocation.thai;
        updateData.us_allocation = updates.allocation.us;
        updateData.gold_allocation = updates.allocation.gold;
        updateData.bonds_allocation = updates.allocation.bonds;
    }

    const { error } = await supabase
        .from("portfolios")
        .update(updateData)
        .eq("user_id", userId);

    if (error) {
        console.error("Error updating portfolio:", error);
        return false;
    }

    return true;
}

// Add transaction
export async function addTransaction(
    userId: string,
    type: "deposit" | "withdraw" | "invest",
    amount: number,
    description: string
): Promise<Transaction | null> {
    const transaction: Transaction = {
        id: `tx-${Date.now()}`,
        userId,
        type,
        amount,
        description,
        createdAt: new Date(),
    };

    if (isMockMode()) {
        const saved = localStorage.getItem(TRANSACTIONS_KEY);
        const transactions = saved ? JSON.parse(saved) : [];
        transactions.unshift(transaction);
        localStorage.setItem(TRANSACTIONS_KEY, JSON.stringify(transactions));
        return transaction;
    }

    const supabase = createClient();
    const { data, error } = await supabase
        .from("transactions")
        .insert({
            user_id: userId,
            type,
            amount,
            description,
        })
        .select()
        .single();

    if (error) {
        console.error("Error adding transaction:", error);
        return null;
    }

    return {
        id: data.id,
        userId: data.user_id,
        type: data.type,
        amount: parseFloat(data.amount),
        description: data.description,
        createdAt: new Date(data.created_at),
    };
}

// Get transactions for a user
export async function getTransactions(userId: string, limit: number = 50): Promise<Transaction[]> {
    if (isMockMode()) {
        const saved = localStorage.getItem(TRANSACTIONS_KEY);
        if (!saved) return [];

        const transactions = JSON.parse(saved);
        return transactions.slice(0, limit).map((t: Transaction & { createdAt: string }) => ({
            ...t,
            createdAt: new Date(t.createdAt),
        }));
    }

    const supabase = createClient();
    const { data, error } = await supabase
        .from("transactions")
        .select("*")
        .eq("user_id", userId)
        .order("created_at", { ascending: false })
        .limit(limit);

    if (error) {
        console.error("Error fetching transactions:", error);
        return [];
    }

    return data.map((t) => ({
        id: t.id,
        userId: t.user_id,
        type: t.type as "deposit" | "withdraw" | "invest",
        amount: parseFloat(t.amount),
        description: t.description,
        createdAt: new Date(t.created_at),
    }));
}

// Deposit money
export async function deposit(userId: string, amount: number): Promise<boolean> {
    const portfolio = await getPortfolio(userId);
    if (!portfolio) return false;

    const newBalance = portfolio.cashBalance + amount;
    const success = await updatePortfolio(userId, { cashBalance: newBalance });

    if (success) {
        await addTransaction(userId, "deposit", amount, `ฝากเงิน ฿${amount.toLocaleString()}`);
    }

    return success;
}

// Withdraw money
export async function withdraw(userId: string, amount: number): Promise<{ success: boolean; message: string }> {
    const portfolio = await getPortfolio(userId);
    if (!portfolio) return { success: false, message: "ไม่พบข้อมูลพอร์ตโฟลิโอ" };

    if (amount > portfolio.cashBalance) {
        return { success: false, message: "ยอดเงินสดไม่เพียงพอ" };
    }

    const newBalance = portfolio.cashBalance - amount;
    const success = await updatePortfolio(userId, { cashBalance: newBalance });

    if (success) {
        await addTransaction(userId, "withdraw", amount, `ถอนเงิน ฿${amount.toLocaleString()}`);
    }

    return { success, message: success ? "ถอนเงินสำเร็จ" : "เกิดข้อผิดพลาด" };
}

// Invest with allocation
export async function invest(
    userId: string,
    allocation: { thai: number; us: number; gold: number; bonds: number }
): Promise<{ success: boolean; message: string }> {
    const portfolio = await getPortfolio(userId);
    if (!portfolio) return { success: false, message: "ไม่พบข้อมูลพอร์ตโฟลิโอ" };

    if (portfolio.cashBalance <= 0) {
        return { success: false, message: "ไม่มียอดเงินสดสำหรับลงทุน" };
    }

    const total = allocation.thai + allocation.us + allocation.gold + allocation.bonds;
    if (total !== 100) {
        return { success: false, message: `สัดส่วนรวมต้องเท่ากับ 100% (ปัจจุบัน: ${total}%)` };
    }

    const investAmount = portfolio.cashBalance;
    const success = await updatePortfolio(userId, {
        cashBalance: 0,
        investedAmount: portfolio.investedAmount + investAmount,
        allocation,
    });

    if (success) {
        await addTransaction(
            userId,
            "invest",
            investAmount,
            `ลงทุน: หุ้นไทย ${allocation.thai}%, หุ้น US ${allocation.us}%, ทองคำ ${allocation.gold}%, พันธบัตร ${allocation.bonds}%`
        );
    }

    return { success, message: success ? "ลงทุนสำเร็จ" : "เกิดข้อผิดพลาด" };
}
