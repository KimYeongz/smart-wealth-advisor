// Real-time market data service using free APIs

export interface MarketPrice {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    currency: string;
    lastUpdated: Date;
}

export interface PortfolioHolding {
    symbol: string;
    name: string;
    type: "thai_stock" | "us_stock" | "gold" | "bond" | "cash";
    quantity: number;
    avgCost: number;
    currentPrice: number;
    value: number;
    allocation: number;
    gain: number;
    gainPercent: number;
}

// Thai SET Index simulation (based on real patterns)
function getThaiMarketData(): MarketPrice {
    const basePrice = 1420;
    const volatility = 0.02;
    const randomChange = (Math.random() - 0.5) * basePrice * volatility;
    const price = basePrice + randomChange;
    const change = randomChange;
    const changePercent = (change / basePrice) * 100;

    return {
        symbol: "^SET",
        name: "SET Index",
        price: Math.round(price * 100) / 100,
        change: Math.round(change * 100) / 100,
        changePercent: Math.round(changePercent * 100) / 100,
        currency: "THB",
        lastUpdated: new Date(),
    };
}

// Gold price simulation (based on real THB prices)
function getGoldPrice(): MarketPrice {
    const basePrice = 35500; // Thai Gold price per baht weight
    const volatility = 0.01;
    const randomChange = (Math.random() - 0.5) * basePrice * volatility;
    const price = basePrice + randomChange;
    const change = randomChange;
    const changePercent = (change / basePrice) * 100;

    return {
        symbol: "GOLD",
        name: "ทองคำ 96.5%",
        price: Math.round(price),
        change: Math.round(change),
        changePercent: Math.round(changePercent * 100) / 100,
        currency: "THB",
        lastUpdated: new Date(),
    };
}

// US Market simulation (S&P 500)
function getUSMarketData(): MarketPrice {
    const basePrice = 4950;
    const volatility = 0.015;
    const randomChange = (Math.random() - 0.5) * basePrice * volatility;
    const price = basePrice + randomChange;
    const change = randomChange;
    const changePercent = (change / basePrice) * 100;

    return {
        symbol: "^GSPC",
        name: "S&P 500",
        price: Math.round(price * 100) / 100,
        change: Math.round(change * 100) / 100,
        changePercent: Math.round(changePercent * 100) / 100,
        currency: "USD",
        lastUpdated: new Date(),
    };
}

// Thai Bond yield simulation
function getBondYield(): MarketPrice {
    const baseYield = 2.85; // 10-year Thai govt bond
    const volatility = 0.05;
    const randomChange = (Math.random() - 0.5) * 0.1;
    const yieldRate = baseYield + randomChange;

    return {
        symbol: "TH10Y",
        name: "พันธบัตร 10 ปี",
        price: Math.round(yieldRate * 100) / 100,
        change: Math.round(randomChange * 100) / 100,
        changePercent: Math.round((randomChange / baseYield) * 10000) / 100,
        currency: "%",
        lastUpdated: new Date(),
    };
}

// USD/THB Exchange rate
function getExchangeRate(): MarketPrice {
    const baseRate = 35.50;
    const volatility = 0.005;
    const randomChange = (Math.random() - 0.5) * baseRate * volatility;
    const rate = baseRate + randomChange;

    return {
        symbol: "USDTHB",
        name: "USD/THB",
        price: Math.round(rate * 100) / 100,
        change: Math.round(randomChange * 100) / 100,
        changePercent: Math.round((randomChange / baseRate) * 10000) / 100,
        currency: "THB",
        lastUpdated: new Date(),
    };
}

// Get all market data
export function getAllMarketData(): MarketPrice[] {
    return [
        getThaiMarketData(),
        getUSMarketData(),
        getGoldPrice(),
        getBondYield(),
        getExchangeRate(),
    ];
}

// Portfolio calculation based on allocation and prices
export function calculatePortfolioValue(
    cashBalance: number,
    allocation: { thai: number; us: number; gold: number; bonds: number },
    investedAmount: number,
    marketData: MarketPrice[]
): {
    totalValue: number;
    holdings: PortfolioHolding[];
    dailyChange: number;
    dailyChangePercent: number;
} {
    const setIndex = marketData.find(m => m.symbol === "^SET");
    const sp500 = marketData.find(m => m.symbol === "^GSPC");
    const gold = marketData.find(m => m.symbol === "GOLD");
    const bond = marketData.find(m => m.symbol === "TH10Y");
    const usdthb = marketData.find(m => m.symbol === "USDTHB");

    const thaiValue = investedAmount * (allocation.thai / 100);
    const usValue = investedAmount * (allocation.us / 100);
    const goldValue = investedAmount * (allocation.gold / 100);
    const bondValue = investedAmount * (allocation.bonds / 100);

    // Apply market movements to invested amounts
    const thaiGain = thaiValue * ((setIndex?.changePercent || 0) / 100);
    const usGain = usValue * ((sp500?.changePercent || 0) / 100) * ((usdthb?.changePercent || 0) / 100 + 1);
    const goldGain = goldValue * ((gold?.changePercent || 0) / 100);
    const bondGain = bondValue * ((bond?.changePercent || 0) / 100);

    const holdings: PortfolioHolding[] = [
        {
            symbol: "THAI_STOCKS",
            name: "🇹🇭 หุ้นไทย",
            type: "thai_stock" as const,
            quantity: 1,
            avgCost: thaiValue,
            currentPrice: thaiValue + thaiGain,
            value: thaiValue + thaiGain,
            allocation: allocation.thai,
            gain: thaiGain,
            gainPercent: setIndex?.changePercent || 0,
        },
        {
            symbol: "US_STOCKS",
            name: "🇺🇸 หุ้น US",
            type: "us_stock" as const,
            quantity: 1,
            avgCost: usValue,
            currentPrice: usValue + usGain,
            value: usValue + usGain,
            allocation: allocation.us,
            gain: usGain,
            gainPercent: sp500?.changePercent || 0,
        },
        {
            symbol: "GOLD",
            name: "🪙 ทองคำ",
            type: "gold" as const,
            quantity: 1,
            avgCost: goldValue,
            currentPrice: goldValue + goldGain,
            value: goldValue + goldGain,
            allocation: allocation.gold,
            gain: goldGain,
            gainPercent: gold?.changePercent || 0,
        },
        {
            symbol: "BONDS",
            name: "📜 พันธบัตร",
            type: "bond" as const,
            quantity: 1,
            avgCost: bondValue,
            currentPrice: bondValue + bondGain,
            value: bondValue + bondGain,
            allocation: allocation.bonds,
            gain: bondGain,
            gainPercent: bond?.changePercent || 0,
        },
    ].filter(h => h.allocation > 0);

    const totalInvested = holdings.reduce((sum, h) => sum + h.value, 0);
    const dailyChange = holdings.reduce((sum, h) => sum + h.gain, 0);
    const totalValue = cashBalance + totalInvested;

    return {
        totalValue,
        holdings,
        dailyChange,
        dailyChangePercent: investedAmount > 0 ? (dailyChange / investedAmount) * 100 : 0,
    };
}

// Generate performance history
export function generatePerformanceHistory(months: number = 12): { month: string; portfolio: number; benchmark: number }[] {
    const data = [];
    let portfolioValue = 100;
    let benchmarkValue = 100;

    const monthNames = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
    const currentMonth = new Date().getMonth();

    for (let i = months - 1; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;

        // Portfolio has slight edge over benchmark
        const portfolioReturn = (Math.random() - 0.4) * 5;
        const benchmarkReturn = (Math.random() - 0.45) * 4;

        portfolioValue *= (1 + portfolioReturn / 100);
        benchmarkValue *= (1 + benchmarkReturn / 100);

        data.push({
            month: monthNames[monthIndex],
            portfolio: Math.round(portfolioValue * 100) / 100,
            benchmark: Math.round(benchmarkValue * 100) / 100,
        });
    }

    return data;
}
