"""
Schemas for custom scenario management
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class CustomScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = "Briefcase"  # Default Lucide icon
    color_gradient: Optional[str] = "from-gray-500 to-gray-600"
    system_prompt: str
    sample_queries: Optional[List[str]] = []
    escalation_triggers: Optional[List[str]] = []
    business_context: Optional[str] = None
    tone: Optional[str] = "Professional"
    specialization: Optional[List[str]] = []


class CustomScenarioCreate(CustomScenarioBase):
    id: str  # Unique identifier like "RESTAURANT", "HEALTHCARE"


class CustomScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color_gradient: Optional[str] = None
    system_prompt: Optional[str] = None
    sample_queries: Optional[List[str]] = None
    escalation_triggers: Optional[List[str]] = None
    business_context: Optional[str] = None
    tone: Optional[str] = None
    specialization: Optional[List[str]] = None


class CustomScenarioResponse(CustomScenarioBase):
    id: str
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScenarioTemplate(BaseModel):
    """Pre-defined scenario templates for quick setup"""
    id: str
    name: str
    description: str
    icon: str
    color_gradient: str
    system_prompt: str
    sample_queries: List[str]
    specialization: List[str]
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "id": "RESTAURANT",
                    "name": "Restaurant Business",
                    "description": "Food service, reservations, and dining experience",
                    "icon": "ChefHat",
                    "color_gradient": "from-orange-500 to-red-600",
                    "system_prompt": "You are a helpful restaurant assistant...",
                    "sample_queries": ["Make a reservation", "What's on the menu today?"],
                    "specialization": ["reservations", "menu", "dietary_restrictions"]
                }
            ]
        }