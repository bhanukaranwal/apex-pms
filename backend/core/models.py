from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Numeric, Date, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
import enum
from backend.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PORTFOLIO_MANAGER = "portfolio_manager"
    ANALYST = "analyst"
    CLIENT = "client"
    COMPLIANCE = "compliance"

class AssetClass(str, enum.Enum):
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    DERIVATIVE = "derivative"
    ALTERNATIVE = "alternative"
    CASH = "cash"
    CRYPTO = "crypto"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    portfolios = relationship("Portfolio", back_populates="owner")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    strategy = Column(String(100))
    benchmark = Column(String(50))
    inception_date = Column(Date, nullable=False)
    base_currency = Column(String(3), default="USD")
    aum = Column(Numeric(20, 2))
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio", cascade="all, delete-orphan")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    asset_class = Column(SQLEnum(AssetClass), default=AssetClass.EQUITY)
    shares = Column(Numeric(20, 6), nullable=False)
    cost_basis = Column(Numeric(20, 4))
    current_price = Column(Numeric(20, 4))
    market_value = Column(Numeric(20, 2))
    unrealized_pnl = Column(Numeric(20, 2))
    weight = Column(Float)
    currency = Column(String(3), default="USD")
    opened_date = Column(Date)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    metadata = Column(JSON)
    
    portfolio = relationship("Portfolio", back_populates="positions")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)
    shares = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 4), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    fees = Column(Numeric(20, 2), default=0)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    settlement_date = Column(Date)
    notes = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", back_populates="transactions")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 4))
    stop_price = Column(Numeric(20, 4))
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    filled_quantity = Column(Numeric(20, 6), default=0)
    average_fill_price = Column(Numeric(20, 4))
    broker = Column(String(50))
    broker_order_id = Column(String(100))
    submitted_at = Column(DateTime(timezone=True))
    filled_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    portfolio = relationship("Portfolio", back_populates="orders")

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(20, 4))
    high = Column(Numeric(20, 4))
    low = Column(Numeric(20, 4))
    close = Column(Numeric(20, 4), nullable=False)
    volume = Column(BigInteger)
    adjusted_close = Column(Numeric(20, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskMetric(Base):
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    calculation_date = Column(Date, nullable=False, index=True)
    var_95 = Column(Numeric(20, 2))
    var_99 = Column(Numeric(20, 2))
    cvar_95 = Column(Numeric(20, 2))
    cvar_99 = Column(Numeric(20, 2))
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)
    tracking_error = Column(Float)
    information_ratio = Column(Float)
    correlation_to_benchmark = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=False)
    severity = Column(String(20), default="warning")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ComplianceViolation(Base):
    __tablename__ = "compliance_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"), index=True)
    violation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    severity = Column(String(20))
    description = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
