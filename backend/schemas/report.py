from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReportRequest(BaseModel):
    start_date: date
    end_date: date
    format: str = "pdf"
    include_charts: bool = True
    custom_sections: Optional[list] = None

class ReportResponse(BaseModel):
    report_id: str
    portfolio_id: int
    report_type: str
    status: str
    download_url: Optional[str]
    generated_at: Optional[str]
