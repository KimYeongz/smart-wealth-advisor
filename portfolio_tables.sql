-- =============================================================================
-- Portfolio Tables for Smart Wealth Advisor
-- Run this AFTER supabase_schema.sql
-- =============================================================================

-- Create portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    cash_balance DECIMAL(15, 2) DEFAULT 0,
    invested_amount DECIMAL(15, 2) DEFAULT 0,
    thai_allocation INTEGER DEFAULT 25 CHECK (thai_allocation >= 0 AND thai_allocation <= 100),
    us_allocation INTEGER DEFAULT 25 CHECK (us_allocation >= 0 AND us_allocation <= 100),
    gold_allocation INTEGER DEFAULT 25 CHECK (gold_allocation >= 0 AND gold_allocation <= 100),
    bonds_allocation INTEGER DEFAULT 25 CHECK (bonds_allocation >= 0 AND bonds_allocation <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('deposit', 'withdraw', 'invest')),
    amount DECIMAL(15, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at DESC);

-- Enable RLS
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policies for portfolios
CREATE POLICY "Users can read own portfolio" ON portfolios
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own portfolio" ON portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own portfolio" ON portfolios
    FOR UPDATE USING (auth.uid() = user_id);

-- Advisors can read client portfolios
CREATE POLICY "Advisors can read client portfolios" ON portfolios
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = portfolios.user_id 
            AND profiles.advisor_id = auth.uid()
        )
    );

-- Policies for transactions
CREATE POLICY "Users can read own transactions" ON transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own transactions" ON transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Advisors can read client transactions
CREATE POLICY "Advisors can read client transactions" ON transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = transactions.user_id 
            AND profiles.advisor_id = auth.uid()
        )
    );

-- Trigger for updated_at on portfolios
DROP TRIGGER IF EXISTS portfolios_updated_at ON portfolios;
CREATE TRIGGER portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function to create portfolio on profile creation
CREATE OR REPLACE FUNCTION handle_new_profile()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.portfolios (user_id, cash_balance, invested_amount)
    VALUES (NEW.id, 0, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create portfolio automatically
DROP TRIGGER IF EXISTS on_profile_created ON profiles;
CREATE TRIGGER on_profile_created
    AFTER INSERT ON profiles
    FOR EACH ROW EXECUTE FUNCTION handle_new_profile();
