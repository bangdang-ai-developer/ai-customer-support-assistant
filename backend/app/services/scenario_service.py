"""
Scenario service for managing built-in and custom business scenarios
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from app.models.conversation import ScenarioType
from app.models.scenario import CustomScenario


class ScenarioService:
    """Unified service for handling both built-in and custom scenarios"""
    
    def __init__(self):
        self.built_in_scenarios = {
            ScenarioType.ECOMMERCE: {
                "name": "E-Commerce Store",
                "description": "Customer support for online retail business",
                "icon": "ShoppingCart",
                "color_gradient": "from-green-500 to-emerald-600"
            },
            ScenarioType.SAAS: {
                "name": "SaaS Platform", 
                "description": "Technical support for software services",
                "icon": "Monitor",
                "color_gradient": "from-blue-500 to-cyan-600"
            },
            ScenarioType.SERVICE_BUSINESS: {
                "name": "Service Business",
                "description": "Support for service-based businesses",
                "icon": "Briefcase", 
                "color_gradient": "from-purple-500 to-pink-600"
            }
        }
    
    def get_all_scenarios(self, db: Session) -> List[Dict[str, Any]]:
        """Get all available scenarios (built-in + custom)"""
        scenarios = []
        
        # Add built-in scenarios
        for scenario_type, config in self.built_in_scenarios.items():
            scenarios.append({
                "id": scenario_type.value,
                "name": config["name"],
                "description": config["description"],
                "icon": config["icon"],
                "color_gradient": config["color_gradient"],
                "type": "built_in",
                "is_active": True
            })
        
        # Add custom scenarios
        custom_scenarios = db.query(CustomScenario).filter(
            CustomScenario.is_active == True
        ).all()
        
        for custom in custom_scenarios:
            scenarios.append({
                "id": custom.id,
                "name": custom.name,
                "description": custom.description,
                "icon": custom.icon,
                "color_gradient": custom.color_gradient,
                "type": "custom",
                "is_active": True,
                "created_at": custom.created_at,
                "created_by": custom.created_by
            })
        
        return scenarios
    
    def get_scenario_config(
        self, 
        scenario_id: str, 
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific scenario"""
        
        # Check built-in scenarios first
        for scenario_type in ScenarioType:
            if scenario_type.value == scenario_id:
                config = self.built_in_scenarios[scenario_type]
                return {
                    "id": scenario_id,
                    "type": "built_in",
                    **config
                }
        
        # Check custom scenarios
        custom_scenario = db.query(CustomScenario).filter(
            CustomScenario.id == scenario_id,
            CustomScenario.is_active == True
        ).first()
        
        if custom_scenario:
            return {
                "id": custom_scenario.id,
                "name": custom_scenario.name,
                "description": custom_scenario.description,
                "icon": custom_scenario.icon,
                "color_gradient": custom_scenario.color_gradient,
                "type": "custom",
                "system_prompt": custom_scenario.system_prompt,
                "sample_queries": custom_scenario.sample_queries,
                "business_context": custom_scenario.business_context,
                "tone": custom_scenario.tone,
                "specialization": custom_scenario.specialization
            }
        
        return None
    
    def get_system_prompt(
        self, 
        scenario_id: str, 
        db: Session
    ) -> str:
        """Get system prompt for a scenario (built-in or custom)"""
        
        # For built-in scenarios, use the prompt service
        try:
            scenario_type = ScenarioType(scenario_id)
            from app.services.prompt_service import PromptService
            prompt_service = PromptService()
            return prompt_service.load_prompt_template(scenario_type)
        except ValueError:
            pass
        
        # For custom scenarios, get from database
        custom_scenario = db.query(CustomScenario).filter(
            CustomScenario.id == scenario_id,
            CustomScenario.is_active == True
        ).first()
        
        if custom_scenario:
            return custom_scenario.system_prompt
        
        # Fallback to default
        return "You are a helpful customer support assistant."
    
    def is_valid_scenario(self, scenario_id: str, db: Session) -> bool:
        """Check if a scenario ID is valid (built-in or custom)"""
        
        # Check built-in scenarios
        for scenario_type in ScenarioType:
            if scenario_type.value == scenario_id:
                return True
        
        # Check custom scenarios
        custom_scenario = db.query(CustomScenario).filter(
            CustomScenario.id == scenario_id,
            CustomScenario.is_active == True
        ).first()
        
        return custom_scenario is not None
    
    def get_scenario_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about scenarios"""
        
        total_custom = db.query(CustomScenario).filter(
            CustomScenario.is_active == True
        ).count()
        
        total_built_in = len(ScenarioType)
        
        return {
            "total_scenarios": total_built_in + total_custom,
            "built_in_scenarios": total_built_in,
            "custom_scenarios": total_custom,
            "available_templates": len(SCENARIO_TEMPLATES)
        }