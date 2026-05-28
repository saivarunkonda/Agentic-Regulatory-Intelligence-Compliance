"""Pydantic models for Departments."""
from pydantic import BaseModel
from typing import Optional


class DepartmentUpdate(BaseModel):
    head: Optional[str] = None
    contact: Optional[str] = None
    compliance_score: Optional[float] = None
