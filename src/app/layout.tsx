import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
    title: "Smart Wealth Advisor | ที่ปรึกษาการเงิน",
    description: "ระบบจัดการพอร์ตการลงทุนอัจฉริยะสำหรับคนไทย - Smart Portfolio Management with AI",
    keywords: ["การลงทุน", "พอร์ตโฟลิโอ", "ที่ปรึกษาการเงิน", "investment", "portfolio"],
    authors: [{ name: "Smart Wealth Advisor Team" }],
    openGraph: {
        title: "Smart Wealth Advisor | ที่ปรึกษาการเงิน",
        description: "ระบบจัดการพอร์ตการลงทุนอัจฉริยะสำหรับคนไทย",
        type: "website",
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="th" className="dark">
            <body className="min-h-screen bg-dark-300">
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
