// User types
export interface User {
    id: string;
    email: string;
    full_name: string;
    role: "client" | "advisor" | "admin";
    phone?: string;
    advisor_id?: string;
    created_at?: string;
}

// Portfolio types
export interface Portfolio {
    id: string;
    user_id: string;
    total_value: number;
    cash_balance: number;
    ytd_return: number;
    risk_score: number;
    holdings: Record<string, number>;
    target_allocation: Record<string, number>;
    created_at?: string;
    updated_at?: string;
}

// Transaction types
export type TransactionType = "deposit" | "withdraw" | "buy" | "sell" | "rebalance";

export interface Transaction {
    id: string;
    portfolio_id: string;
    type: TransactionType;
    amount: number;
    asset_name?: string;
    description?: string;
    created_at?: string;
}

// Auth types
export interface AuthResult {
    success: boolean;
    message: string;
    user?: User;
    error_code?: string;
}

// Dashboard metric types
export interface DashboardMetric {
    label: string;
    value: string;
    change?: string;
    changeType?: "positive" | "negative" | "neutral";
    icon?: string;
}

// Chart data types
export interface ChartDataPoint {
    date: string;
    value: number;
    benchmark?: number;
}

export interface AllocationData {
    name: string;
    value: number;
    color: string;
}

// API response types
export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}
