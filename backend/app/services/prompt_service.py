"""
Enhanced Prompt Service for dynamic, context-aware prompt generation
"""

import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.conversation import ScenarioType
from app.services.knowledge_service import KnowledgeService


class PromptService:
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.knowledge_service = KnowledgeService()
    
    def load_prompt_template(self, scenario: Union[ScenarioType, str]) -> str:
        """Load scenario-specific prompt template"""
        # Handle built-in scenarios
        if isinstance(scenario, ScenarioType):
            scenario_map = {
                ScenarioType.ECOMMERCE: "ecommerce",
                ScenarioType.SAAS: "saas", 
                ScenarioType.SERVICE_BUSINESS: "service"
            }
            
            # Load base prompt
            base_prompt_path = self.prompts_dir / "base" / "system_base.md"
            base_prompt = self._load_file(base_prompt_path)
            
            # Load scenario-specific prompt
            scenario_dir = scenario_map.get(scenario, "ecommerce")
            scenario_prompt_path = self.prompts_dir / scenario_dir / "system.md"
            scenario_prompt = self._load_file(scenario_prompt_path)
            
            return f"{base_prompt}\n\n{scenario_prompt}"
        else:
            # For custom scenarios, return a basic prompt - the ScenarioService will handle the custom prompt
            return "You are a helpful customer support assistant."
    
    def build_context_aware_prompt(
        self,
        scenario: Union[ScenarioType, str],
        user_message: str,
        conversation_history: List[Dict[str, Any]] = None,
        business_context: str = None,
        db: Session = None
    ) -> str:
        """Build a complete, context-aware prompt"""
        
        # 1. Load base prompt template
        system_prompt = self.load_prompt_template(scenario)
        
        # 2. Add business context from uploaded documents
        context_sections = []
        
        if business_context:
            context_sections.append(f"## Business Context\n{business_context}")
        
        # 3. Perform RAG search for relevant knowledge
        if db:
            # Search for top 3 most relevant context pieces
            scenario_category = scenario.value if hasattr(scenario, 'value') else str(scenario)
            relevant_knowledge = self.knowledge_service.semantic_search(
                user_message, 
                limit=3, 
                db=db,
                category=f"{scenario_category}_BUSINESS_CONTEXT"
            )
            
            if relevant_knowledge:
                knowledge_context = "## Relevant Business Context (Top 3 Matches)\n"
                for i, knowledge in enumerate(relevant_knowledge, 1):
                    knowledge_context += f"\n**Source {i}: {knowledge.title}**\n{knowledge.content}\n"
                    if i < len(relevant_knowledge):
                        knowledge_context += "\n---\n"
                context_sections.append(knowledge_context)
        
        # 4. Add conversation history
        if conversation_history:
            history_context = self._format_conversation_history(conversation_history)
            context_sections.append(f"## Previous Conversation\n{history_context}")
        
        # 5. Combine all context
        full_context = "\n\n".join(context_sections) if context_sections else ""
        
        # 6. Build final prompt
        final_prompt = f"""{system_prompt}

{full_context}

## Current Customer Query
Customer: {user_message}

Please provide a helpful, accurate response based on the above context. If you don't have enough information to provide a complete answer, say so and suggest next steps."""
        
        return final_prompt
    
    def _load_file(self, file_path: Path) -> str:
        """Load content from a file"""
        try:
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            else:
                return f"# Prompt file not found: {file_path}"
        except Exception as e:
            return f"# Error loading prompt: {str(e)}"
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for prompt context"""
        if not history:
            return ""
        
        formatted_messages = []
        for msg in history[-6:]:  # Limit to last 6 messages for context
            role = "Customer" if msg["role"] in ["USER", "user"] else "Assistant"
            formatted_messages.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted_messages)
    
    def get_business_context_for_scenario(
        self, 
        scenario: Union[ScenarioType, str], 
        db: Session
    ) -> Optional[str]:
        """Get business context from uploaded documents for a specific scenario"""
        try:
            # Search for business context documents
            # Handle both ScenarioType enum and custom scenario strings
            scenario_id = scenario.value if hasattr(scenario, 'value') else str(scenario)
            business_docs = self.knowledge_service.get_knowledge_by_category(
                category=f"{scenario_id}_BUSINESS_CONTEXT",
                db=db,
                limit=3
            )
            
            if business_docs:
                context_parts = []
                for doc in business_docs:
                    context_parts.append(f"**{doc.title}**\n{doc.content}")
                
                return "\n\n".join(context_parts)
            
            return None
        except Exception:
            return None
    
    def validate_prompt_templates(self) -> Dict[str, bool]:
        """Validate that all required prompt templates exist"""
        required_files = [
            "base/system_base.md",
            "ecommerce/system.md", 
            "saas/system.md",
            "service/system.md"
        ]
        
        validation_results = {}
        for file_path in required_files:
            full_path = self.prompts_dir / file_path
            validation_results[file_path] = full_path.exists()
        
        return validation_results