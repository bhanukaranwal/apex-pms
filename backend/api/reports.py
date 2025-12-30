from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from datetime import date
import io

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.services.report_generation import (
    generate_performance_report,
    generate_holdings_report,
    generate_risk_report,
    generate_tax_report
)
from backend.schemas.report import ReportRequest, ReportResponse

router = APIRouter()

@router.post("/{portfolio_id}/performance", response_model=ReportResponse)
async def generate_performance_report_endpoint(
    portfolio_id: int,
    report_request: ReportRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    report = await generate_performance_report(
        portfolio_id=portfolio_id,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
        format=report_request.format,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return report

@router.post("/{portfolio_id}/holdings", response_model=ReportResponse)
async def generate_holdings_report_endpoint(
    portfolio_id: int,
    report_request: ReportRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    report = await generate_holdings_report(
        portfolio_id=portfolio_id,
        as_of_date=report_request.end_date,
        format=report_request.format,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return report

@router.post("/{portfolio_id}/risk", response_model=ReportResponse)
async def generate_risk_report_endpoint(
    portfolio_id: int,
    report_request: ReportRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    report = await generate_risk_report(
        portfolio_id=portfolio_id,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
        format=report_request.format,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return report

@router.post("/{portfolio_id}/tax", response_model=ReportResponse)
async def generate_tax_report_endpoint(
    portfolio_id: int,
    tax_year: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    report = await generate_tax_report(
        portfolio_id=portfolio_id,
        tax_year=tax_year,
        db=db,
        user_id=int(current_user["id"])
    )
    
    return report

@router.get("/{portfolio_id}/download/{report_id}")
async def download_report(
    portfolio_id: int,
    report_id: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from backend.services.report_generation import get_report_file
    
    report_file = await get_report_file(
        report_id=report_id,
        portfolio_id=portfolio_id,
        user_id=int(current_user["id"]),
        db=db
    )
    
    if not report_file:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    return Response(
        content=report_file["content"],
        media_type=report_file["media_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{report_file["filename"]}"'
        }
    )
