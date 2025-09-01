"""
Chat service for managing conversation context and real-time messaging
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.conversation import Conversation, MessageRole


class ChatService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_conversation_context(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation messages for context"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [
            {
                "role": message.role.value,
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "metadata": message.msg_metadata or {}
            }
            for message in messages
        ]
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary and statistics"""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return {}
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()
        
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
        
        total_tokens = sum(m.tokens_used or 0 for m in assistant_messages)
        avg_response_time = sum(m.response_time or 0 for m in assistant_messages) / len(assistant_messages) if assistant_messages else 0
        
        return {
            "id": conversation.id,
            "scenario_type": conversation.scenario_type.value,
            "status": conversation.status.value,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "message_count": len(messages),
            "user_message_count": len(user_messages),
            "assistant_message_count": len(assistant_messages),
            "total_tokens_used": total_tokens,
            "average_response_time_ms": int(avg_response_time)
        }
    
    async def analyze_conversation_sentiment(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation sentiment (simplified implementation)"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == MessageRole.USER
        ).all()
        
        # Simple sentiment analysis based on keywords
        positive_keywords = ["thank", "great", "good", "excellent", "helpful", "love", "perfect"]
        negative_keywords = ["bad", "terrible", "awful", "hate", "frustrated", "angry", "disappointed"]
        
        sentiment_scores = []
        
        for message in messages:
            content_lower = message.content.lower()
            positive_count = sum(1 for word in positive_keywords if word in content_lower)
            negative_count = sum(1 for word in negative_keywords if word in content_lower)
            
            if positive_count > negative_count:
                sentiment_scores.append(1)  # Positive
            elif negative_count > positive_count:
                sentiment_scores.append(-1)  # Negative
            else:
                sentiment_scores.append(0)  # Neutral
        
        if not sentiment_scores:
            return {"overall_sentiment": "neutral", "confidence": 0.0}
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        if avg_sentiment > 0.3:
            sentiment = "positive"
        elif avg_sentiment < -0.3:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "overall_sentiment": sentiment,
            "confidence": abs(avg_sentiment),
            "message_count": len(messages),
            "positive_messages": sentiment_scores.count(1),
            "negative_messages": sentiment_scores.count(-1),
            "neutral_messages": sentiment_scores.count(0)
        }
    
    async def should_escalate_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Determine if conversation should be escalated to human agent"""
        sentiment = await self.analyze_conversation_sentiment(conversation_id)
        summary = await self.get_conversation_summary(conversation_id)
        
        escalation_factors = []
        escalation_score = 0.0
        
        # Factor 1: Negative sentiment
        if sentiment["overall_sentiment"] == "negative" and sentiment["confidence"] > 0.5:
            escalation_factors.append("Negative customer sentiment detected")
            escalation_score += 0.4
        
        # Factor 2: Long conversation without resolution
        if summary["message_count"] > 20:
            escalation_factors.append("Extended conversation length")
            escalation_score += 0.3
        
        # Factor 3: High response time (indicates complex queries)
        if summary["average_response_time_ms"] > 10000:  # > 10 seconds
            escalation_factors.append("Complex queries requiring extended processing")
            escalation_score += 0.2
        
        # Factor 4: Repeated similar questions (check last few messages)
        recent_messages = await self.get_conversation_context(conversation_id, 6)
        user_messages = [m["content"] for m in recent_messages if m["role"] == "USER"]
        
        if len(user_messages) >= 3:
            # Simple check for repeated keywords
            all_words = " ".join(user_messages).lower().split()
            word_counts = {}
            for word in all_words:
                if len(word) > 4:  # Only count meaningful words
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            repeated_words = [word for word, count in word_counts.items() if count >= 3]
            if repeated_words:
                escalation_factors.append("Customer appears to be asking repeated questions")
                escalation_score += 0.3
        
        should_escalate = escalation_score >= 0.6
        
        return {
            "should_escalate": should_escalate,
            "escalation_score": escalation_score,
            "factors": escalation_factors,
            "recommendation": "Escalate to human agent" if should_escalate else "Continue with AI assistance"
        }