from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ComplianceRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: str = Field(..., regex="^(position_limit|concentration|sector_limit|custom)$")
    parameters: Dict[str, Any]
    severity: str = Field("warning", regex="^(info|warning|error|critical)$")
    is_active: bool = True

class ComplianceRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rule_type: str
    parameters: Dict[str, Any]
    severity: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ComplianceCheckRequest(BaseModel):
    portfolio_id: Optional[int] = None
    rules: Optional[List[int]] = None
    order_details: Optional[Dict[str, Any]] = None

class ComplianceCheckResponse(BaseModel):
    passed: bool
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    timestamp: datetime

class ViolationResponse(BaseModel):
    id: int
    portfolio_id: Optional[int]
    rule_id: Optional[int]
    violation_date: datetime
    severity: Optional[str]
    description: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True
