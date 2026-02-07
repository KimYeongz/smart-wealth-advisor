-- =============================================================================
-- Portfolio Tables Schema for Supabase
-- =============================================================================
-- Run this AFTER supabase_schema.sql

-- Portfolios table - stores portfolio summary for each user
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    total_value DECIMAL(15,2) DEFAULT 0,
    cash_balance DECIMAL(15,2) DEFAULT 0,
    ytd_return DECIMAL(8,4) DEFAULT 0,
    risk_score INTEGER DEFAULT 5 CHECK (risk_score >= 1 AND risk_score <= 10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Portfolio holdings - individual asset allocations
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE NOT NULL,
    asset_name TEXT NOT NULL,
    current_weight DECIMAL(5,4) DEFAULT 0 CHECK (current_weight >= 0 AND current_weight <= 1),
    target_weight DECIMAL(5,4) DEFAULT 0 CHECK (target_weight >= 0 AND target_weight <= 1),
    value DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, asset_name)
);

-- Transactions table - track deposits, withdrawals, trades
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('deposit', 'withdraw', 'buy', 'sell', 'rebalance')),
    asset_name TEXT,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON portfolio_holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at DESC);

-- Enable Row Level Security
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for portfolios
CREATE POLICY "Users can view own portfolio" ON portfolios
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own portfolio" ON portfolios
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can insert own portfolio" ON portfolios
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Advisors can view their clients' portfolios
CREATE POLICY "Advisors can view client portfolios" ON portfolios
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = portfolios.user_id AND advisor_id = auth.uid()
        )
    );

-- RLS Policies for holdings (inherit from portfolio)
CREATE POLICY "Users can view own holdings" ON portfolio_holdings
    FOR SELECT USING (
        portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can manage own holdings" ON portfolio_holdings
    FOR ALL USING (
        portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
    );

-- RLS Policies for transactions
CREATE POLICY "Users can view own transactions" ON transactions
    FOR SELECT USING (
        portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own transactions" ON transactions
    FOR INSERT WITH CHECK (
        portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
    );

-- Function to create portfolio for new user
CREATE OR REPLACE FUNCTION create_user_portfolio()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO portfolios (user_id, total_value, cash_balance, risk_score)
    VALUES (NEW.id, 0, 0, 5);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create portfolio on user signup
DROP TRIGGER IF EXISTS on_profile_created ON profiles;
CREATE TRIGGER on_profile_created
    AFTER INSERT ON profiles
    FOR EACH ROW EXECUTE FUNCTION create_user_portfolio();

-- Function to update portfolio timestamp
CREATE OR REPLACE FUNCTION update_portfolio_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS portfolios_updated_at ON portfolios;
CREATE TRIGGER portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_portfolio_timestamp();

DROP TRIGGER IF EXISTS holdings_updated_at ON portfolio_holdings;
CREATE TRIGGER holdings_updated_at
    BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW EXECUTE FUNCTION update_portfolio_timestamp();
