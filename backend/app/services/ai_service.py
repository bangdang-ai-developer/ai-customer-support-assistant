"""
Enhanced AI Service with RAG and context-aware prompt generation
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import asyncio
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.conversation import ScenarioType
from app.services.prompt_service import PromptService
from app.services.scenario_service import ScenarioService

logger = logging.getLogger(__name__)

# Configure Gemini AI
if settings.GOOGLE_AI_API_KEY:
    genai.configure(api_key=settings.GOOGLE_AI_API_KEY)


class AIResponse(BaseModel):
    content: str
    model: str
    tokens_used: Optional[int] = None
    confidence: Optional[float] = None
    context_used: Optional[List[str]] = None  # Sources used in response
    knowledge_entries: Optional[List[int]] = None  # Knowledge base IDs used


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.prompt_service = PromptService()
        self.scenario_service = ScenarioService()
    
    async def generate_response(
        self,
        message: str,
        scenario_type: Union[ScenarioType, str],
        conversation_context: List[Dict[str, Any]] = None,
        db: Session = None
    ) -> AIResponse:
        """Generate context-aware AI response using RAG"""
        try:
            # Handle both built-in ScenarioType and custom scenario strings
            scenario_id = scenario_type.value if isinstance(scenario_type, ScenarioType) else scenario_type
            
            # Get system prompt (built-in or custom)
            if db:
                system_prompt = self.scenario_service.get_system_prompt(scenario_id, db)
            else:
                # Fallback to prompt service for built-in scenarios
                if isinstance(scenario_type, ScenarioType):
                    system_prompt = self.prompt_service.load_prompt_template(scenario_type)
                else:
                    system_prompt = "You are a helpful customer support assistant."
            
            # Get business context for this scenario
            business_context = None
            if db:
                business_context = self.prompt_service.get_business_context_for_scenario(
                    scenario_type, db
                )
            
            # Build context-aware prompt using RAG
            full_prompt = self.prompt_service.build_context_aware_prompt(
                scenario=scenario_type,
                user_message=message,
                conversation_history=conversation_context,
                business_context=business_context,
                db=db
            )
            
            # Generate response using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            # Extract knowledge sources used
            context_sources = []
            knowledge_ids = []
            
            if db:
                # Get the knowledge entries that were used
                relevant_knowledge = self.prompt_service.knowledge_service.semantic_search(
                    message, 
                    limit=3, 
                    db=db,
                    category=f"{scenario_id}_BUSINESS_CONTEXT"
                )
                
                for knowledge in relevant_knowledge:
                    context_sources.append(knowledge.title)
                    knowledge_ids.append(knowledge.id)
            
            return AIResponse(
                content=response.text,
                model="gemini-2.5-flash",
                tokens_used=self._estimate_tokens(response.text),
                confidence=0.9,
                context_used=context_sources,
                knowledge_entries=knowledge_ids
            )
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return AIResponse(
                content=self._get_fallback_response(scenario_type),
                model="fallback",
                tokens_used=0,
                confidence=0.1,
                context_used=[],
                knowledge_entries=[]
            )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for response text"""
        return int(len(text.split()) * 1.3)  # Rough estimation, ensure integer
    
    def _get_fallback_response(self, scenario_type: ScenarioType) -> str:
        """Generate fallback response when AI service fails"""
        fallback_responses = {
            ScenarioType.ECOMMERCE: "I apologize, but I'm experiencing some technical difficulties right now. Please contact our support team at support@company.com or try again in a few minutes.",
            ScenarioType.SAAS: "I'm currently experiencing technical issues. Please check our status page or contact our technical support team for immediate assistance.",
            ScenarioType.SERVICE_BUSINESS: "I'm sorry, but I'm having trouble processing your request right now. Please call us directly or try again shortly."
        }
        
        return fallback_responses.get(scenario_type, fallback_responses[ScenarioType.ECOMMERCE])


class ContextAnalyzer:
    """Analyze conversation context and suggest improvements"""
    
    def __init__(self):
        pass
    
    def analyze_context_gaps(
        self, 
        conversation_history: List[Dict[str, Any]], 
        scenario: ScenarioType
    ) -> Dict[str, Any]:
        """Analyze conversation for context gaps that could be filled with knowledge base"""
        
        # Extract keywords from conversation
        all_messages = " ".join([msg.get("content", "") for msg in conversation_history])
        
        # Simple keyword analysis (could be enhanced with NLP)
        business_keywords = {
            ScenarioType.ECOMMERCE: ["product", "order", "shipping", "return", "refund", "payment"],
            ScenarioType.SAAS: ["feature", "account", "billing", "integration", "API", "setup"],
            ScenarioType.SERVICE_BUSINESS: ["appointment", "booking", "service", "pricing", "availability"]
        }
        
        scenario_keywords = business_keywords.get(scenario, [])
        mentioned_keywords = [kw for kw in scenario_keywords if kw.lower() in all_messages.lower()]
        
        return {
            "mentioned_keywords": mentioned_keywords,
            "suggested_context": f"Consider uploading business documentation about: {', '.join(scenario_keywords)}",
            "context_coverage": len(mentioned_keywords) / len(scenario_keywords) * 100 if scenario_keywords else 0
        }