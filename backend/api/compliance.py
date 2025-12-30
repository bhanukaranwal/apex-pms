from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from backend.core.database import get_db
from backend.core.models import ComplianceRule, ComplianceViolation, Portfolio
from backend.core.security import get_current_user, require_role
from backend.schemas.compliance import (
    ComplianceRuleCreate,
    ComplianceRuleResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ViolationResponse
)
from backend.services.compliance_engine import check_compliance, run_pre_trade_compliance

router = APIRouter()

@router.post("/rules", response_model=ComplianceRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_rule(
    rule_data: ComplianceRuleCreate,
    current_user: Dict = Depends(require_role("compliance")),
    db: AsyncSession = Depends(get_db)
) -> ComplianceRule:
    new_rule = ComplianceRule(
        name=rule_data.name,
        description=rule_data.description,
        rule_type=rule_data.rule_type,
        parameters=rule_data.parameters,
        severity=rule_data.severity,
        is_active=rule_data.is_active
    )
    
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    return new_rule

@router.get("/rules", response_model=List[ComplianceRuleResponse])
async def list_compliance_rules(
    is_active: Optional[bool] = None,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ComplianceRule]:
    query = select(ComplianceRule)
    
    if is_active is not None:
        query = query.where(ComplianceRule.is_active == is_active)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return rules

@router.post("/{portfolio_id}/check", response_model=ComplianceCheckResponse)
async def check_portfolio_compliance(
    portfolio_id: int,
    check_request: ComplianceCheckRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == int(current_user["id"])
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    compliance_result = await check_compliance(
        portfolio_id=portfolio_id,
        rules=check_request.rules,
        db=db
    )
    
    return compliance_result

@router.post("/pre-trade-check", response_model=ComplianceCheckResponse)
async def pre_trade_compliance_check(
    check_request: ComplianceCheckRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    compliance_result = await run_pre_trade_compliance(
        portfolio_id=check_request.portfolio_id,
        order_details=check_request.order_details,
        db=db
    )
    
    return compliance_result

@router.get("/violations", response_model=List[ViolationResponse])
async def list_violations(
    portfolio_id: Optional[int] = None,
    resolved: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ComplianceViolation]:
    query = select(ComplianceViolation)
    
    if portfolio_id:
        result = await db.execute(
            select(Portfolio).where(
                and_(
                    Portfolio.id == portfolio_id,
                    Portfolio.owner_id == int(current_user["id"])
                )
            )
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        query = query.where(ComplianceViolation.portfolio_id == portfolio_id)
    
    if resolved is not None:
        query = query.where(ComplianceViolation.resolved == resolved)
    
    if start_date:
        query = query.where(ComplianceViolation.violation_date >= start_date)
    
    if end_date:
        query = query.where(ComplianceViolation.violation_date <= end_date)
    
    query = query.order_by(ComplianceViolation.violation_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    violations = result.scalars().all()
    
    return violations

@router.put("/violations/{violation_id}/resolve", response_model=ViolationResponse)
async def resolve_violation(
    violation_id: int,
    notes: str,
    current_user: Dict = Depends(require_role("compliance")),
    db: AsyncSession = Depends(get_db)
) -> ComplianceViolation:
    result = await db.execute(
        select(ComplianceViolation).where(ComplianceViolation.id == violation_id)
    )
    violation = result.scalar_one_or_none()
    
    if not violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Violation not found"
        )
    
    violation.resolved = True
    violation.resolved_at = datetime.utcnow()
    violation.resolved_by = int(current_user["id"])
    violation.notes = notes
    
    await db.commit()
    await db.refresh(violation)
    
    return violation
