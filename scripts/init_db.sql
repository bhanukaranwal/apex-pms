CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE INDEX IF NOT EXISTS idx_positions_portfolio_ticker ON positions(portfolio_id, ticker);
CREATE INDEX IF NOT EXISTS idx_positions_ticker ON positions(ticker);
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_date ON transactions(portfolio_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_ticker ON transactions(ticker);
CREATE INDEX IF NOT EXISTS idx_orders_portfolio_status ON orders(portfolio_id, status);
CREATE INDEX IF NOT EXISTS idx_price_data_ticker_date ON price_data(ticker, date);
CREATE INDEX IF NOT EXISTS idx_risk_metrics_portfolio_date ON risk_metrics(portfolio_id, calculation_date);
CREATE INDEX IF NOT EXISTS idx_compliance_violations_portfolio ON compliance_violations(portfolio_id, violation_date);
