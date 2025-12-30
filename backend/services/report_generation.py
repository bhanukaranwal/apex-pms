from typing import Dict, Any, Optional
from datetime import date, datetime
import pandas as pd
from io import BytesIO
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.core.models import Portfolio, Position
from backend.services.analytics import calculate_returns
from backend.services.risk_management import calculate_risk_metrics

async def generate_performance_report(
    portfolio_id: int,
    start_date: date,
    end_date: date,
    format: str,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == user_id
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    returns_data = await calculate_returns(
        portfolio_id, start_date, end_date, "monthly", db, user_id
    )
    
    risk_data = await calculate_risk_metrics(
        portfolio_id, 252, db, user_id
    )
    
    report_id = str(uuid.uuid4())
    
    if format == "pdf":
        report_content = await generate_pdf_report(portfolio, returns_data, risk_data)
    elif format == "excel":
        report_content = await generate_excel_report(portfolio, returns_data, risk_data)
    else:
        report_content = None
    
    return {
        "report_id": report_id,
        "portfolio_id": portfolio_id,
        "report_type": "performance",
        "status": "completed",
        "download_url": f"/api/reports/{portfolio_id}/download/{report_id}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def generate_holdings_report(
    portfolio_id: int,
    as_of_date: date,
    format: str,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    result = await db.execute(
        select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.owner_id == user_id
            )
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    positions = result.scalars().all()
    
    report_id = str(uuid.uuid4())
    
    return {
        "report_id": report_id,
        "portfolio_id": portfolio_id,
        "report_type": "holdings",
        "status": "completed",
        "download_url": f"/api/reports/{portfolio_id}/download/{report_id}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def generate_risk_report(
    portfolio_id: int,
    start_date: date,
    end_date: date,
    format: str,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    risk_data = await calculate_risk_metrics(
        portfolio_id, 252, db, user_id
    )
    
    report_id = str(uuid.uuid4())
    
    return {
        "report_id": report_id,
        "portfolio_id": portfolio_id,
        "report_type": "risk",
        "status": "completed",
        "download_url": f"/api/reports/{portfolio_id}/download/{report_id}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def generate_tax_report(
    portfolio_id: int,
    tax_year: int,
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    report_id = str(uuid.uuid4())
    
    return {
        "report_id": report_id,
        "portfolio_id": portfolio_id,
        "report_type": "tax",
        "status": "completed",
        "download_url": f"/api/reports/{portfolio_id}/download/{report_id}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def generate_pdf_report(
    portfolio: Portfolio,
    returns_data: Dict[str, Any],
    risk_data: Dict[str, Any]
) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.drawString(100, 750, f"Performance Report - {portfolio.name}")
    c.drawString(100, 730, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    
    c.drawString(100, 700, f"Cumulative Return: {returns_data['cumulative_return']:.2%}")
    c.drawString(100, 680, f"Annualized Return: {returns_data['annualized_return']:.2%}")
    c.drawString(100, 660, f"Volatility: {risk_data['volatility']:.2%}")
    c.drawString(100, 640, f"Sharpe Ratio: {risk_data['sharpe_ratio']:.2f}")
    c.drawString(100, 620, f"Max Drawdown: {risk_data['max_drawdown']:.2%}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.read()

async def generate_excel_report(
    portfolio: Portfolio,
    returns_data: Dict[str, Any],
    risk_data: Dict[str, Any]
) -> bytes:
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        summary_data = {
            "Metric": ["Cumulative Return", "Annualized Return", "Volatility", "Sharpe Ratio", "Max Drawdown"],
            "Value": [
                f"{returns_data['cumulative_return']:.2%}",
                f"{returns_data['annualized_return']:.2%}",
                f"{risk_data['volatility']:.2%}",
                f"{risk_data['sharpe_ratio']:.2f}",
                f"{risk_data['max_drawdown']:.2%}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        returns_df = pd.DataFrame(returns_data['returns'])
        returns_df.to_excel(writer, sheet_name='Returns', index=False)
    
    buffer.seek(0)
    return buffer.read()

async def get_report_file(
    report_id: str,
    portfolio_id: int,
    user_id: int,
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    return {
        "content": b"Sample report content",
        "media_type": "application/pdf",
        "filename": f"report_{report_id}.pdf"
    }
