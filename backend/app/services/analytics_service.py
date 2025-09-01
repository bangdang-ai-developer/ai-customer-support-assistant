"""
Analytics service for tracking and reporting on chatbot performance
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json

from app.models.conversation import (
    Conversation, ConversationStatus, 
    MessageRole, ScenarioType
)
# MessageFeedback and FeedbackRating temporarily disabled
from app.models.message import Message


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_dashboard_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Basic conversation metrics
        total_conversations = self.db.query(Conversation).filter(
            Conversation.created_at >= start_date
        ).count()
        
        active_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.status == ConversationStatus.ACTIVE,
                Conversation.created_at >= start_date
            )
        ).count()
        
        completed_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.status == ConversationStatus.COMPLETED,
                Conversation.created_at >= start_date
            )
        ).count()
        
        escalated_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.status == ConversationStatus.ESCALATED,
                Conversation.created_at >= start_date
            )
        ).count()
        
        # Message metrics
        total_messages = self.db.query(Message).filter(
            Message.timestamp >= start_date
        ).count()
        
        user_messages = self.db.query(Message).filter(
            and_(
                Message.role == MessageRole.USER,
                Message.timestamp >= start_date
            )
        ).count()
        
        assistant_messages = self.db.query(Message).filter(
            and_(
                Message.role == MessageRole.ASSISTANT,
                Message.timestamp >= start_date
            )
        ).count()
        
        # Average response time
        avg_response_time = self.db.query(func.avg(Message.response_time)).filter(
            and_(
                Message.role == MessageRole.ASSISTANT,
                Message.timestamp >= start_date,
                Message.response_time.isnot(None)
            )
        ).scalar() or 0
        
        # Feedback metrics
        # Temporarily disabled - MessageFeedback not available
        positive_feedback = 0
        negative_feedback = 0
        
        total_feedback = positive_feedback + negative_feedback
        satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        # Resolution rate
        resolution_rate = (completed_conversations / total_conversations * 100) if total_conversations > 0 else 0
        escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        return {
            "period_days": days,
            "conversations": {
                "total": total_conversations,
                "active": active_conversations,
                "completed": completed_conversations,
                "escalated": escalated_conversations,
                "resolution_rate": round(resolution_rate, 1),
                "escalation_rate": round(escalation_rate, 1)
            },
            "messages": {
                "total": total_messages,
                "user": user_messages,
                "assistant": assistant_messages,
                "avg_response_time_ms": round(avg_response_time, 1) if avg_response_time else 0
            },
            "feedback": {
                "total": total_feedback,
                "positive": positive_feedback,
                "negative": negative_feedback,
                "satisfaction_rate": round(satisfaction_rate, 1)
            },
            "performance": {
                "avg_response_time": f"{round(avg_response_time/1000, 2)}s" if avg_response_time else "0s",
                "messages_per_conversation": round(total_messages / total_conversations, 1) if total_conversations > 0 else 0
            }
        }
    
    async def get_scenario_breakdown(self, days: int = 7) -> Dict[ScenarioType, Dict[str, Any]]:
        """Get metrics broken down by scenario type"""
        start_date = datetime.now() - timedelta(days=days)
        
        scenarios = {}
        
        for scenario in ScenarioType:
            # Conversations for this scenario
            scenario_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.scenario_type == scenario,
                    Conversation.created_at >= start_date
                )
            ).all()
            
            total_conversations = len(scenario_conversations)
            completed = sum(1 for c in scenario_conversations if c.status == ConversationStatus.COMPLETED)
            escalated = sum(1 for c in scenario_conversations if c.status == ConversationStatus.ESCALATED)
            
            # Messages for this scenario
            conversation_ids = [c.id for c in scenario_conversations]
            if conversation_ids:
                messages = self.db.query(Message).filter(
                    Message.conversation_id.in_(conversation_ids)
                ).all()
                
                assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
                avg_response_time = sum(m.response_time or 0 for m in assistant_messages) / len(assistant_messages) if assistant_messages else 0
                
                # Feedback for assistant messages
                assistant_message_ids = [m.id for m in assistant_messages]
                if assistant_message_ids:
                    # Temporarily disabled - MessageFeedback not available
                    feedback = []
                    
                    positive = 0
                    total_feedback = len(feedback)
                    satisfaction = (positive / total_feedback * 100) if total_feedback > 0 else 0
                else:
                    satisfaction = 0
                    total_feedback = 0
            else:
                avg_response_time = 0
                satisfaction = 0
                total_feedback = 0
            
            scenarios[scenario] = {
                "total_conversations": total_conversations,
                "completed": completed,
                "escalated": escalated,
                "resolution_rate": round(completed / total_conversations * 100, 1) if total_conversations > 0 else 0,
                "escalation_rate": round(escalated / total_conversations * 100, 1) if total_conversations > 0 else 0,
                "avg_response_time_ms": round(avg_response_time, 1),
                "satisfaction_rate": round(satisfaction, 1),
                "total_feedback": total_feedback
            }
        
        return scenarios
    
    async def get_hourly_activity(self, days: int = 1) -> List[Dict[str, Any]]:
        """Get hourly activity breakdown for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Query messages grouped by hour
        messages_by_hour = self.db.query(
            func.extract('hour', Message.timestamp).label('hour'),
            func.count(Message.id).label('count'),
            func.avg(Message.response_time).label('avg_response_time')
        ).filter(
            and_(
                Message.timestamp >= start_date,
                Message.role == MessageRole.USER  # Count user messages as activity
            )
        ).group_by(
            func.extract('hour', Message.timestamp)
        ).all()
        
        # Fill in missing hours with zeros
        hourly_data = []
        activity_map = {int(row.hour): {"count": row.count, "avg_response_time": row.avg_response_time or 0} for row in messages_by_hour}
        
        for hour in range(24):
            data = activity_map.get(hour, {"count": 0, "avg_response_time": 0})
            hourly_data.append({
                "hour": hour,
                "messages": data["count"],
                "avg_response_time": round(data["avg_response_time"], 1)
            })
        
        return hourly_data
    
    async def get_top_issues(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Analyze user messages to identify common issues/topics"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Get user messages from the period
        user_messages = self.db.query(Message).filter(
            and_(
                Message.role == MessageRole.USER,
                Message.timestamp >= start_date
            )
        ).all()
        
        # Simple keyword analysis (in production, would use NLP)
        keyword_counts = {}
        common_keywords = [
            'order', 'payment', 'shipping', 'return', 'refund', 'cancel',
            'account', 'login', 'password', 'setup', 'configuration', 'api',
            'booking', 'appointment', 'schedule', 'service', 'pricing', 'availability'
        ]
        
        for message in user_messages:
            content_lower = message.content.lower()
            for keyword in common_keywords:
                if keyword in content_lower:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top issues
        top_issues = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {
                "issue": issue,
                "count": count,
                "percentage": round(count / len(user_messages) * 100, 1) if user_messages else 0
            }
            for issue, count in top_issues
        ]
    
    async def get_performance_trends(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Daily conversation counts
        daily_conversations = self.db.query(
            func.date(Conversation.created_at).label('date'),
            func.count(Conversation.id).label('count')
        ).filter(
            Conversation.created_at >= start_date
        ).group_by(
            func.date(Conversation.created_at)
        ).all()
        
        # Daily average response times
        daily_response_times = self.db.query(
            func.date(Message.timestamp).label('date'),
            func.avg(Message.response_time).label('avg_response_time')
        ).filter(
            and_(
                Message.timestamp >= start_date,
                Message.role == MessageRole.ASSISTANT,
                Message.response_time.isnot(None)
            )
        ).group_by(
            func.date(Message.timestamp)
        ).all()
        
        # Daily satisfaction rates - temporarily disabled
        daily_feedback = []
        
        # Format the data
        conversation_trend = [
            {
                "date": str(row.date),
                "count": row.count
            }
            for row in daily_conversations
        ]
        
        response_time_trend = [
            {
                "date": str(row.date),
                "avg_response_time": round(row.avg_response_time, 1) if row.avg_response_time else 0
            }
            for row in daily_response_times
        ]
        
        satisfaction_trend = [
            {
                "date": str(row.date),
                "satisfaction_rate": round(row.positive / row.total * 100, 1) if row.total > 0 else 0
            }
            for row in daily_feedback
        ]
        
        return {
            "conversations": conversation_trend,
            "response_times": response_time_trend,
            "satisfaction": satisfaction_trend
        }
    
    async def generate_insights(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate actionable insights from the data"""
        metrics = await self.get_dashboard_metrics(days)
        scenario_breakdown = await self.get_scenario_breakdown(days)
        
        insights = []
        
        # Escalation rate insight
        if metrics["conversations"]["escalation_rate"] > 15:
            insights.append({
                "type": "warning",
                "title": "High Escalation Rate",
                "description": f"Escalation rate is {metrics['conversations']['escalation_rate']}%, which is above the 15% threshold.",
                "recommendation": "Consider improving AI training data or adding more specific knowledge base articles.",
                "priority": "high"
            })
        
        # Response time insight
        avg_response_ms = metrics["messages"]["avg_response_time_ms"]
        if avg_response_ms > 3000:  # 3 seconds
            insights.append({
                "type": "performance",
                "title": "Slow Response Times",
                "description": f"Average response time is {avg_response_ms/1000:.1f}s, which may impact user experience.",
                "recommendation": "Optimize AI model calls or consider caching common responses.",
                "priority": "medium"
            })
        
        # Satisfaction insight
        if metrics["feedback"]["satisfaction_rate"] < 80:
            insights.append({
                "type": "quality",
                "title": "Low Satisfaction Rate",
                "description": f"User satisfaction is {metrics['feedback']['satisfaction_rate']}%, below the 80% target.",
                "recommendation": "Review negative feedback and improve response quality in identified areas.",
                "priority": "high"
            })
        
        # Scenario-specific insights
        for scenario, data in scenario_breakdown.items():
            if data["resolution_rate"] < 70:
                insights.append({
                    "type": "scenario",
                    "title": f"Low Resolution Rate for {scenario.value}",
                    "description": f"{scenario.value} has a {data['resolution_rate']}% resolution rate.",
                    "recommendation": f"Focus on improving knowledge base and AI training for {scenario.value} scenarios.",
                    "priority": "medium"
                })
        
        # Positive insights
        if metrics["conversations"]["resolution_rate"] > 85:
            insights.append({
                "type": "success",
                "title": "Excellent Resolution Rate",
                "description": f"Resolution rate of {metrics['conversations']['resolution_rate']}% is exceeding expectations.",
                "recommendation": "Continue current practices and consider documenting successful strategies.",
                "priority": "low"
            })
        
        return insights