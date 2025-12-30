from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.core.models import Portfolio, Position, ComplianceRule, ComplianceViolation

async def check_compliance(
    portfolio_id: int,
    rules: Optional[List[int]],
    db: AsyncSession
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    if rules:
        rules_query = select(ComplianceRule).where(
            and_(ComplianceRule.id.in_(rules), ComplianceRule.is_active == True)
        )
    else:
        rules_query = select(ComplianceRule).where(ComplianceRule.is_active == True)
    
    result = await db.execute(rules_query)
    compliance_rules = result.scalars().all()
    
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    violations = []
    warnings = []
    
    for rule in compliance_rules:
        violation = await evaluate_rule(rule, portfolio, positions, db)
        if violation:
            if rule.severity in ["error", "critical"]:
                violations.append(violation)
            else:
                warnings.append(violation)
    
    passed = len(violations) == 0
    
    return {
        "passed": passed,
        "violations": violations,
        "warnings": warnings,
        "timestamp": datetime.utcnow()
    }

async def evaluate_rule(
    rule: ComplianceRule,
    portfolio: Portfolio,
    positions: List[Position],
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    if rule.rule_type == "position_limit":
        return await check_position_limit(rule, portfolio, positions, db)
    elif rule.rule_type == "concentration":
        return await check_concentration(rule, portfolio, positions, db)
    elif rule.rule_type == "sector_limit":
        return await check_sector_limit(rule, portfolio, positions, db)
    elif rule.rule_type == "custom":
        return await check_custom_rule(rule, portfolio, positions, db)
    
    return None

async def check_position_limit(
    rule: ComplianceRule,
    portfolio: Portfolio,
    positions: List[Position],
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    max_position = rule.parameters.get("max_position_weight", 0.25)
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    if portfolio_value == 0:
        return None
    
    for position in positions:
        weight = float(position.market_value or 0) / portfolio_value
        if weight > max_position:
            violation = ComplianceViolation(
                portfolio_id=portfolio.id,
                rule_id=rule.id,
                violation_date=datetime.utcnow(),
                severity=rule.severity,
                description=f"Position {position.ticker} exceeds maximum weight: {weight:.2%} > {max_position:.2%}",
                resolved=False
            )
            db.add(violation)
            await db.commit()
            
            return {
                "rule_id": rule.id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "description": violation.description,
                "ticker": position.ticker,
                "current_weight": weight,
                "limit": max_position
            }
    
    return None

async def check_concentration(
    rule: ComplianceRule,
    portfolio: Portfolio,
    positions: List[Position],
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    max_issuer_concentration = rule.parameters.get("max_issuer_concentration", 0.10)
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    if portfolio_value == 0:
        return None
    
    issuer_exposures = {}
    for position in positions:
        issuer = position.ticker
        exposure = float(position.market_value or 0) / portfolio_value
        issuer_exposures[issuer] = issuer_exposures.get(issuer, 0) + exposure
    
    for issuer, exposure in issuer_exposures.items():
        if exposure > max_issuer_concentration:
            violation = ComplianceViolation(
                portfolio_id=portfolio.id,
                rule_id=rule.id,
                violation_date=datetime.utcnow(),
                severity=rule.severity,
                description=f"Issuer {issuer} concentration exceeds limit: {exposure:.2%} > {max_issuer_concentration:.2%}",
                resolved=False
            )
            db.add(violation)
            await db.commit()
            
            return {
                "rule_id": rule.id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "description": violation.description,
                "issuer": issuer,
                "current_concentration": exposure,
                "limit": max_issuer_concentration
            }
    
    return None

async def check_sector_limit(
    rule: ComplianceRule,
    portfolio: Portfolio,
    positions: List[Position],
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    max_sector_exposure = rule.parameters.get("max_sector_exposure", 0.40)
    
    portfolio_value = sum(float(p.market_value or 0) for p in positions)
    
    if portfolio_value == 0:
        return None
    
    sector_exposures = {}
    for position in positions:
        sector = "Technology"
        exposure = float(position.market_value or 0) / portfolio_value
        sector_exposures[sector] = sector_exposures.get(sector, 0) + exposure
    
    for sector, exposure in sector_exposures.items():
        if exposure > max_sector_exposure:
            violation = ComplianceViolation(
                portfolio_id=portfolio.id,
                rule_id=rule.id,
                violation_date=datetime.utcnow(),
                severity=rule.severity,
                description=f"Sector {sector} exposure exceeds limit: {exposure:.2%} > {max_sector_exposure:.2%}",
                resolved=False
            )
            db.add(violation)
            await db.commit()
            
            return {
                "rule_id": rule.id,
                "rule_name": rule.name,
                "severity": rule.severity,
                "description": violation.description,
                "sector": sector,
                "current_exposure": exposure,
                "limit": max_sector_exposure
            }
    
    return None

async def check_custom_rule(
    rule: ComplianceRule,
    portfolio: Portfolio,
    positions: List[Position],
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    return None

async def run_pre_trade_compliance(
    portfolio_id: int,
    order_details: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id)
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = list(result.scalars().all())
    
    ticker = order_details.get("ticker")
    quantity = order_details.get("quantity", 0)
    side = order_details.get("side", "buy")
    price = order_details.get("price", 100)
    
    simulated_positions = positions.copy()
    
    existing_position = next((p for p in simulated_positions if p.ticker == ticker), None)
    
    if side == "buy":
        if existing_position:
            new_shares = float(existing_position.shares) + float(quantity)
            existing_position.shares = new_shares
            existing_position.market_value = new_shares * float(price)
        else:
            from backend.core.models import Position
            new_position = Position(
                portfolio_id=portfolio_id,
                ticker=ticker,
                shares=quantity,
                market_value=float(quantity) * float(price),
                current_price=price
            )
            simulated_positions.append(new_position)
    elif side == "sell":
        if existing_position:
            new_shares = float(existing_position.shares) - float(quantity)
            if new_shares > 0:
                existing_position.shares = new_shares
                existing_position.market_value = new_shares * float(price)
            else:
                simulated_positions.remove(existing_position)
    
    compliance_result = await check_compliance(portfolio_id, None, db)
    
    return compliance_result
