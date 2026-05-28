"""Pydantic models for MAPs."""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MAPStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    escalated = "escalated"


class MAPCreate(BaseModel):
    regulation_id: int
    title: str
    description: str
    priority: str = "medium"
    department: str
    deadline: Optional[str] = None


class MAPUpdate(BaseModel):
    status: str
    actor: Optional[str] = "System"
    notes: Optional[str] = None
