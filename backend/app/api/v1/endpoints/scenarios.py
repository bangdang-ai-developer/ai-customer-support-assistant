"""
Custom scenario management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.scenario import CustomScenario
from app.schemas.scenario import (
    CustomScenarioCreate, 
    CustomScenarioUpdate, 
    CustomScenarioResponse,
    ScenarioTemplate
)

router = APIRouter()

# Pre-defined scenario templates for quick setup
SCENARIO_TEMPLATES = {
    "RESTAURANT": ScenarioTemplate(
        id="RESTAURANT",
        name="Restaurant Business",
        description="Food service, reservations, and dining experience support",
        icon="ChefHat",
        color_gradient="from-orange-500 to-red-600",
        system_prompt="""You are a helpful restaurant assistant. Focus on:
- Taking reservations and managing bookings
- Describing menu items and daily specials
- Handling dietary restrictions and allergies
- Providing restaurant hours and location info
- Assisting with takeout and delivery orders
- Managing waitlists and special events

Be warm, welcoming, and food-focused in your responses.""",
        sample_queries=[
            "Make a reservation for tonight",
            "What's on the menu today?",
            "Do you have gluten-free options?",
            "What time do you close?",
            "Can I order takeout?"
        ],
        specialization=["reservations", "menu", "dietary_restrictions", "hours", "takeout"]
    ),
    
    "HEALTHCARE": ScenarioTemplate(
        id="HEALTHCARE",
        name="Healthcare Provider",
        description="Medical appointments, patient services, and health information",
        icon="Heart",
        color_gradient="from-red-500 to-pink-600",
        system_prompt="""You are a healthcare support assistant. Focus on:
- Scheduling appointments and managing patient requests
- Providing general health information and resources
- Explaining services and procedures
- Handling insurance and billing questions
- Emergency contact and urgent care guidance
- Patient privacy and HIPAA compliance

Be compassionate, professional, and health-focused. Never provide medical diagnoses.""",
        sample_queries=[
            "Schedule an appointment",
            "What insurance do you accept?",
            "What are your emergency hours?",
            "How do I prepare for my procedure?",
            "Can I get a prescription refill?"
        ],
        specialization=["appointments", "insurance", "procedures", "emergency", "prescriptions"]
    ),
    
    "LEGAL": ScenarioTemplate(
        id="LEGAL",
        name="Legal Services",
        description="Legal consultations, document services, and legal guidance",
        icon="Scale",
        color_gradient="from-blue-500 to-indigo-600", 
        system_prompt="""You are a legal services assistant. Focus on:
- Scheduling consultations with attorneys
- Explaining legal services and procedures
- Providing general legal information and resources
- Handling document preparation requests
- Managing case inquiries and status updates
- Directing urgent legal matters appropriately

Be professional, precise, and legally-minded. Never provide legal advice - only information.""",
        sample_queries=[
            "Schedule a consultation",
            "What legal services do you offer?",
            "How much does document review cost?",
            "Can you help with contract disputes?",
            "What do I need for bankruptcy?"
        ],
        specialization=["consultations", "documents", "contracts", "litigation", "bankruptcy"]
    )
}


@router.get("/templates", response_model=List[ScenarioTemplate])
async def get_scenario_templates():
    """Get available scenario templates for quick setup"""
    return list(SCENARIO_TEMPLATES.values())


@router.post("/", response_model=CustomScenarioResponse)
async def create_custom_scenario(
    scenario_data: CustomScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new custom scenario"""
    
    # Check if scenario ID already exists
    existing = db.query(CustomScenario).filter(
        CustomScenario.id == scenario_data.id.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Scenario with ID '{scenario_data.id}' already exists"
        )
    
    # Create new scenario
    scenario = CustomScenario(
        id=scenario_data.id.upper(),
        name=scenario_data.name,
        description=scenario_data.description,
        icon=scenario_data.icon,
        color_gradient=scenario_data.color_gradient,
        system_prompt=scenario_data.system_prompt,
        sample_queries=scenario_data.sample_queries,
        escalation_triggers=scenario_data.escalation_triggers,
        business_context=scenario_data.business_context,
        tone=scenario_data.tone,
        specialization=scenario_data.specialization,
        created_by=current_user.id
    )
    
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    
    return scenario


@router.get("/")
async def get_all_scenarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all scenarios (built-in + custom)"""
    from app.services.scenario_service import ScenarioService
    
    scenario_service = ScenarioService()
    all_scenarios = scenario_service.get_all_scenarios(db)
    
    return all_scenarios


@router.get("/{scenario_id}", response_model=CustomScenarioResponse)
async def get_custom_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific custom scenario"""
    scenario = db.query(CustomScenario).filter(
        CustomScenario.id == scenario_id.upper(),
        CustomScenario.is_active == True
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail="Custom scenario not found"
        )
    
    return scenario


@router.put("/{scenario_id}", response_model=CustomScenarioResponse)
async def update_custom_scenario(
    scenario_id: str,
    scenario_data: CustomScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a custom scenario"""
    scenario = db.query(CustomScenario).filter(
        CustomScenario.id == scenario_id.upper(),
        CustomScenario.is_active == True
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail="Custom scenario not found"
        )
    
    # Update fields
    update_data = scenario_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)
    
    db.commit()
    db.refresh(scenario)
    
    return scenario


@router.delete("/{scenario_id}")
async def delete_custom_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a custom scenario"""
    scenario = db.query(CustomScenario).filter(
        CustomScenario.id == scenario_id.upper(),
        CustomScenario.is_active == True
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail="Custom scenario not found"
        )
    
    # Soft delete
    scenario.is_active = False
    db.commit()
    
    return {"message": f"Scenario '{scenario_id}' deleted successfully"}


@router.post("/from-template/{template_id}", response_model=CustomScenarioResponse)
async def create_from_template(
    template_id: str,
    custom_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a custom scenario from a pre-defined template"""
    
    template = SCENARIO_TEMPLATES.get(template_id.upper())
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_id}' not found"
        )
    
    # Check if scenario already exists
    existing = db.query(CustomScenario).filter(
        CustomScenario.id == template.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Scenario '{template.id}' already exists"
        )
    
    # Create scenario from template
    scenario = CustomScenario(
        id=template.id,
        name=custom_name or template.name,
        description=template.description,
        icon=template.icon,
        color_gradient=template.color_gradient,
        system_prompt=template.system_prompt,
        sample_queries=template.sample_queries,
        escalation_triggers=[],
        business_context="",
        tone="Professional",
        specialization=template.specialization,
        created_by=current_user.id
    )
    
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    
    return scenario