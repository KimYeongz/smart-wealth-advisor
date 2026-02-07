import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// Format Thai Baht currency
export function formatCurrency(value: number): string {
    return new Intl.NumberFormat("th-TH", {
        style: "currency",
        currency: "THB",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
}

// Format percentage
export function formatPercent(value: number, decimals = 2): string {
    return `${(value * 100).toFixed(decimals)}%`;
}

// Format date in Thai
export function formatThaiDate(date: Date | string): string {
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toLocaleDateString("th-TH", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

// Format short date
export function formatShortDate(date: Date | string): string {
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toLocaleDateString("th-TH", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
    });
}

// Calculate YTD return percentage
export function calculateYTDReturn(currentValue: number, startValue: number): number {
    if (startValue === 0) return 0;
    return (currentValue - startValue) / startValue;
}

// Get color based on value (positive/negative)
export function getChangeColor(value: number): string {
    if (value > 0) return "text-green-400";
    if (value < 0) return "text-red-400";
    return "text-gray-400";
}

// Get risk score label
export function getRiskLabel(score: number): string {
    if (score <= 3) return "ต่ำ";
    if (score <= 6) return "ปานกลาง";
    if (score <= 8) return "สูง";
    return "สูงมาก";
}

// Get risk color
export function getRiskColor(score: number): string {
    if (score <= 3) return "text-green-400";
    if (score <= 6) return "text-yellow-400";
    if (score <= 8) return "text-orange-400";
    return "text-red-400";
}
