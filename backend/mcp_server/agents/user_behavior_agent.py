"""
User Behavior Agent - Specialized in analyzing user behavior patterns and interactions
"""

import sys
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import json

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.database.models import User, Product, UserSession, PageView, Purchase, Review
from .base_agent import BaseAgent, AgentCapability


class UserBehaviorAgent(BaseAgent):
    """Agent specialized in user behavior analysis and customer insights"""
    
    def __init__(self):
        super().__init__(
            agent_id="user_behavior_agent",
            name="User Behavior Analyst",
            description="Specializes in analyzing user behavior patterns, customer engagement, session analysis, and user journey insights"
        )
        
        # Register tools
        self.tools = {
            "analyze_user_behavior": self._analyze_user_behavior,
            "get_user_journey": self._get_user_journey,
            "analyze_session_patterns": self._analyze_session_patterns,
            "get_user_segmentation": self._get_user_segmentation,
            "analyze_engagement_metrics": self._analyze_engagement_metrics,
            "get_user_retention": self._get_user_retention,
            "analyze_page_interactions": self._analyze_page_interactions,
            "get_device_behavior": self._get_device_behavior
        }
    
    def get_capabilities(self) -> List[str]:
        """Return this agent's capabilities"""
        return [
            AgentCapability.USER_BEHAVIOR,
            AgentCapability.SESSION_ANALYSIS,
            AgentCapability.PRODUCT_ANALYTICS
        ]
    
    def can_handle_query(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        
        behavior_keywords = [
            "user", "customer", "behavior", "session", "engagement", 
            "activity", "interaction", "browsing", "page view", "journey",
            "retention", "segmentation", "device", "usage pattern"
        ]
        
        return any(keyword in query_lower for keyword in behavior_keywords)
    
    def process_query(self, query: str, db: Session, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user behavior related queries"""
        query_lower = query.lower()
        
        try:
            # Route to appropriate analysis based on query content
            if "journey" in query_lower:
                return self._analyze_user_journey_from_query(query, db)
            elif "session" in query_lower:
                return self._analyze_sessions_from_query(query, db)
            elif "engagement" in query_lower:
                return self._analyze_engagement_from_query(query, db)
            elif "retention" in query_lower:
                return self._analyze_retention_from_query(query, db)
            elif "device" in query_lower:
                return self._analyze_device_behavior_from_query(query, db)
            elif "segment" in query_lower:
                return self._analyze_segmentation_from_query(query, db)
            else:
                # General user behavior analysis
                return self._analyze_general_behavior(query, db)
                
        except Exception as e:
            return {"error": f"User Behavior Agent error: {str(e)}"}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools for this agent"""
        return [
            {
                "name": "analyze_user_behavior",
                "description": "Comprehensive analysis of specific user's behavior patterns",
                "parameters": ["user_id", "days_back", "include_details"]
            },
            {
                "name": "get_user_journey",
                "description": "Track user journey and interaction flow",
                "parameters": ["user_id", "session_id", "journey_type"]
            },
            {
                "name": "analyze_session_patterns",
                "description": "Analyze session patterns across users or specific segments",
                "parameters": ["user_segment", "time_period", "device_filter"]
            },
            {
                "name": "get_user_segmentation",
                "description": "Segment users based on behavior patterns",
                "parameters": ["segmentation_criteria", "min_activity_level"]
            },
            {
                "name": "analyze_engagement_metrics",
                "description": "Calculate and analyze user engagement metrics",
                "parameters": ["metric_type", "time_period", "user_group"]
            },
            {
                "name": "get_user_retention",
                "description": "Analyze user retention and churn patterns",
                "parameters": ["cohort_period", "retention_metric"]
            },
            {
                "name": "analyze_page_interactions",
                "description": "Analyze how users interact with different pages",
                "parameters": ["page_type", "interaction_metric", "time_period"]
            },
            {
                "name": "get_device_behavior",
                "description": "Analyze user behavior across different devices",
                "parameters": ["device_comparison", "behavior_metric"]
            }
        ]
    
    def _analyze_user_behavior(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze comprehensive user behavior"""
        user_id = parameters.get("user_id")
        days_back = parameters.get("days_back", 30)
        include_details = parameters.get("include_details", True)
        
        if not user_id:
            return {"error": "user_id is required"}
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": f"User {user_id} not found"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Session analysis
        sessions = db.query(UserSession).filter(
            and_(UserSession.user_id == user_id, UserSession.session_start >= cutoff_date)
        ).all()
        
        # Purchase analysis
        purchases = db.query(Purchase).filter(
            and_(Purchase.user_id == user_id, Purchase.purchase_date >= cutoff_date)
        ).all()
        
        # Page view analysis
        page_views = db.query(PageView).join(UserSession).filter(
            and_(UserSession.user_id == user_id, PageView.timestamp >= cutoff_date)
        ).all()
        
        # Calculate metrics
        total_sessions = len(sessions)
        avg_session_duration = sum(s.session_duration_minutes or 0 for s in sessions) / max(total_sessions, 1)
        total_page_views = len(page_views)
        pages_per_session = total_page_views / max(total_sessions, 1)
        
        # Device usage
        device_usage = {}
        for session in sessions:
            device_usage[session.device_type] = device_usage.get(session.device_type, 0) + 1
        
        # Purchase behavior
        total_purchases = len(purchases)
        total_spent = sum(p.total_amount for p in purchases)
        avg_order_value = total_spent / max(total_purchases, 1)
        
        result = {
            "user_profile": {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "is_premium": user.is_premium,
                "registration_date": user.registration_date.isoformat()
            },
            "behavior_summary": {
                "analysis_period_days": days_back,
                "total_sessions": total_sessions,
                "avg_session_duration_minutes": round(avg_session_duration, 2),
                "total_page_views": total_page_views,
                "pages_per_session": round(pages_per_session, 2),
                "total_purchases": total_purchases,
                "total_spent": round(total_spent, 2),
                "avg_order_value": round(avg_order_value, 2)
            },
            "device_preferences": device_usage,
            "engagement_level": self._calculate_engagement_level(sessions, page_views, purchases)
        }
        
        if include_details:
            result["detailed_sessions"] = [
                {
                    "session_id": s.id,
                    "start_time": s.session_start.isoformat(),
                    "duration_minutes": s.session_duration_minutes,
                    "pages_viewed": s.pages_viewed,
                    "device_type": s.device_type,
                    "browser": s.browser
                } for s in sessions[-10:]  # Last 10 sessions
            ]
        
        return result
    
    def _get_user_journey(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze user journey and interaction flow"""
        user_id = parameters.get("user_id")
        session_id = parameters.get("session_id")
        
        if session_id:
            # Analyze specific session journey
            session = db.query(UserSession).filter(UserSession.id == session_id).first()
            if not session:
                return {"error": f"Session {session_id} not found"}
            
            page_views = db.query(PageView).filter(PageView.session_id == session_id)\
                          .order_by(PageView.timestamp).all()
            
            journey_steps = []
            total_time = 0
            
            for i, pv in enumerate(page_views):
                step = {
                    "step": i + 1,
                    "page_type": pv.page_type,
                    "product_id": pv.product_id,
                    "timestamp": pv.timestamp.isoformat(),
                    "time_spent_seconds": pv.time_spent_seconds
                }
                
                if pv.product_id:
                    product = db.query(Product).filter(Product.id == pv.product_id).first()
                    if product:
                        step["product_name"] = product.name
                        step["product_category"] = product.category
                
                journey_steps.append(step)
                total_time += pv.time_spent_seconds
            
            return {
                "session_info": {
                    "session_id": session.id,
                    "user_id": session.user_id,
                    "device_type": session.device_type,
                    "browser": session.browser,
                    "total_duration_minutes": session.session_duration_minutes
                },
                "journey_steps": journey_steps,
                "journey_summary": {
                    "total_steps": len(journey_steps),
                    "total_time_seconds": total_time,
                    "avg_time_per_step": total_time / max(len(journey_steps), 1)
                }
            }
        
        elif user_id:
            # Analyze user's typical journey patterns
            recent_sessions = db.query(UserSession).filter(UserSession.user_id == user_id)\
                               .order_by(desc(UserSession.session_start)).limit(10).all()
            
            journey_patterns = {}
            for session in recent_sessions:
                page_views = db.query(PageView).filter(PageView.session_id == session.id)\
                              .order_by(PageView.timestamp).all()
                
                journey_pattern = " -> ".join([pv.page_type for pv in page_views])
                journey_patterns[journey_pattern] = journey_patterns.get(journey_pattern, 0) + 1
            
            return {
                "user_id": user_id,
                "journey_patterns": journey_patterns,
                "most_common_pattern": max(journey_patterns.items(), key=lambda x: x[1]) 
                                       if journey_patterns else None
            }
        
        return {"error": "Either user_id or session_id is required"}
    
    def _analyze_session_patterns(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze session patterns across users"""
        time_period = parameters.get("time_period", 30)
        device_filter = parameters.get("device_filter")
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        query = db.query(UserSession).filter(UserSession.session_start >= cutoff_date)
        
        if device_filter:
            query = query.filter(UserSession.device_type == device_filter)
        
        sessions = query.all()
        
        # Analyze patterns
        hourly_patterns = {}
        daily_patterns = {}
        device_patterns = {}
        duration_patterns = {"short": 0, "medium": 0, "long": 0}
        
        for session in sessions:
            # Hourly patterns
            hour = session.session_start.hour
            hourly_patterns[hour] = hourly_patterns.get(hour, 0) + 1
            
            # Daily patterns
            day = session.session_start.strftime("%A")
            daily_patterns[day] = daily_patterns.get(day, 0) + 1
            
            # Device patterns
            device_patterns[session.device_type] = device_patterns.get(session.device_type, 0) + 1
            
            # Duration patterns
            duration = session.session_duration_minutes or 0
            if duration < 5:
                duration_patterns["short"] += 1
            elif duration < 30:
                duration_patterns["medium"] += 1
            else:
                duration_patterns["long"] += 1
        
        total_sessions = len(sessions)
        avg_duration = sum(s.session_duration_minutes or 0 for s in sessions) / max(total_sessions, 1)
        
        return {
            "analysis_period_days": time_period,
            "total_sessions_analyzed": total_sessions,
            "average_session_duration": round(avg_duration, 2),
            "patterns": {
                "hourly_distribution": hourly_patterns,
                "daily_distribution": daily_patterns,
                "device_distribution": device_patterns,
                "duration_distribution": duration_patterns
            },
            "insights": {
                "peak_hour": max(hourly_patterns.items(), key=lambda x: x[1])[0] if hourly_patterns else None,
                "peak_day": max(daily_patterns.items(), key=lambda x: x[1])[0] if daily_patterns else None,
                "preferred_device": max(device_patterns.items(), key=lambda x: x[1])[0] if device_patterns else None
            }
        }
    
    def _get_user_segmentation(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Segment users based on behavior patterns"""
        segmentation_criteria = parameters.get("segmentation_criteria", "engagement")
        min_activity_level = parameters.get("min_activity_level", 1)
        
        # Get all users with their activity metrics
        users = db.query(User).all()
        segments = {
            "high_engagement": [],
            "medium_engagement": [],
            "low_engagement": [],
            "inactive": []
        }
        
        for user in users:
            # Calculate engagement score
            sessions_count = db.query(UserSession).filter(UserSession.user_id == user.id).count()
            purchases_count = db.query(Purchase).filter(Purchase.user_id == user.id).count()
            total_spent = db.query(func.sum(Purchase.total_amount))\
                           .filter(Purchase.user_id == user.id).scalar() or 0
            
            engagement_score = sessions_count + (purchases_count * 2) + (total_spent / 100)
            
            user_info = {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "is_premium": user.is_premium,
                "engagement_score": round(engagement_score, 2),
                "sessions_count": sessions_count,
                "purchases_count": purchases_count,
                "total_spent": float(total_spent)
            }
            
            # Segment based on engagement score
            if engagement_score == 0:
                segments["inactive"].append(user_info)
            elif engagement_score < 5:
                segments["low_engagement"].append(user_info)
            elif engagement_score < 20:
                segments["medium_engagement"].append(user_info)
            else:
                segments["high_engagement"].append(user_info)
        
        return {
            "segmentation_criteria": segmentation_criteria,
            "segments": segments,
            "segment_summary": {
                "high_engagement": len(segments["high_engagement"]),
                "medium_engagement": len(segments["medium_engagement"]),
                "low_engagement": len(segments["low_engagement"]),
                "inactive": len(segments["inactive"])
            }
        }
    
    def _analyze_engagement_metrics(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        metric_type = parameters.get("metric_type", "overall")
        time_period = parameters.get("time_period", 30)
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        # Calculate various engagement metrics
        total_users = db.query(User).count()
        active_users = db.query(UserSession.user_id.distinct())\
                        .filter(UserSession.session_start >= cutoff_date).count()
        
        total_sessions = db.query(UserSession)\
                          .filter(UserSession.session_start >= cutoff_date).count()
        
        total_page_views = db.query(PageView)\
                            .filter(PageView.timestamp >= cutoff_date).count()
        
        purchasing_users = db.query(Purchase.user_id.distinct())\
                            .filter(Purchase.purchase_date >= cutoff_date).count()
        
        # Calculate metrics
        user_activity_rate = (active_users / max(total_users, 1)) * 100
        sessions_per_user = total_sessions / max(active_users, 1)
        pages_per_session = total_page_views / max(total_sessions, 1)
        conversion_rate = (purchasing_users / max(active_users, 1)) * 100
        
        return {
            "metric_type": metric_type,
            "time_period_days": time_period,
            "engagement_metrics": {
                "user_activity_rate": round(user_activity_rate, 2),
                "sessions_per_user": round(sessions_per_user, 2),
                "pages_per_session": round(pages_per_session, 2),
                "conversion_rate": round(conversion_rate, 2)
            },
            "raw_numbers": {
                "total_users": total_users,
                "active_users": active_users,
                "total_sessions": total_sessions,
                "total_page_views": total_page_views,
                "purchasing_users": purchasing_users
            }
        }
    
    def _get_user_retention(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze user retention and churn patterns"""
        cohort_period = parameters.get("cohort_period", 30)
        retention_metric = parameters.get("retention_metric", "login")
        
        # Get users registered in different periods
        cutoff_date = datetime.utcnow() - timedelta(days=cohort_period)
        
        # Users from different cohorts
        recent_users = db.query(User).filter(User.registration_date >= cutoff_date).all()
        older_users = db.query(User).filter(User.registration_date < cutoff_date).all()
        
        # Calculate retention for recent cohort
        active_recent = 0
        for user in recent_users:
            recent_sessions = db.query(UserSession).filter(
                and_(UserSession.user_id == user.id, 
                     UserSession.session_start >= cutoff_date)
            ).count()
            if recent_sessions > 0:
                active_recent += 1
        
        # Calculate retention for older cohort
        active_older = 0
        for user in older_users:
            recent_sessions = db.query(UserSession).filter(
                and_(UserSession.user_id == user.id,
                     UserSession.session_start >= cutoff_date)
            ).count()
            if recent_sessions > 0:
                active_older += 1
        
        retention_rate_recent = (active_recent / max(len(recent_users), 1)) * 100
        retention_rate_older = (active_older / max(len(older_users), 1)) * 100
        
        return {
            "analysis_period_days": cohort_period,
            "retention_metric": retention_metric,
            "cohort_analysis": {
                "recent_cohort": {
                    "total_users": len(recent_users),
                    "active_users": active_recent,
                    "retention_rate": round(retention_rate_recent, 2)
                },
                "older_cohort": {
                    "total_users": len(older_users),
                    "active_users": active_older,
                    "retention_rate": round(retention_rate_older, 2)
                }
            },
            "insights": {
                "overall_retention_trend": "improving" if retention_rate_recent > retention_rate_older else "declining",
                "churn_risk": "low" if retention_rate_recent > 70 else "medium" if retention_rate_recent > 50 else "high"
            }
        }
    
    def _analyze_page_interactions(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze how users interact with different pages"""
        page_type = parameters.get("page_type")
        interaction_metric = parameters.get("interaction_metric", "time_spent")
        time_period = parameters.get("time_period", 30)
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        query = db.query(PageView).filter(PageView.timestamp >= cutoff_date)
        if page_type:
            query = query.filter(PageView.page_type == page_type)
        
        page_views = query.all()
        
        page_interactions = {}
        for pv in page_views:
            page_key = pv.page_type
            if page_key not in page_interactions:
                page_interactions[page_key] = {
                    "total_views": 0,
                    "total_time_spent": 0,
                    "avg_time_spent": 0,
                    "unique_sessions": set()
                }
            
            page_interactions[page_key]["total_views"] += 1
            page_interactions[page_key]["total_time_spent"] += pv.time_spent_seconds
            page_interactions[page_key]["unique_sessions"].add(pv.session_id)
        
        # Calculate averages and convert sets to counts
        for page_key, data in page_interactions.items():
            data["avg_time_spent"] = data["total_time_spent"] / max(data["total_views"], 1)
            data["unique_sessions"] = len(data["unique_sessions"])
            data["total_time_spent"] = round(data["total_time_spent"], 2)
            data["avg_time_spent"] = round(data["avg_time_spent"], 2)
        
        return {
            "analysis_period_days": time_period,
            "interaction_metric": interaction_metric,
            "page_interactions": page_interactions,
            "insights": {
                "most_engaging_page": max(page_interactions.items(), 
                                        key=lambda x: x[1]["avg_time_spent"])[0] if page_interactions else None,
                "most_viewed_page": max(page_interactions.items(),
                                      key=lambda x: x[1]["total_views"])[0] if page_interactions else None
            }
        }
    
    def _get_device_behavior(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze user behavior across different devices"""
        device_comparison = parameters.get("device_comparison", "all")
        behavior_metric = parameters.get("behavior_metric", "session_duration")
        
        # Get all sessions
        sessions = db.query(UserSession).all()
        
        device_behavior = {}
        for session in sessions:
            device = session.device_type
            if device not in device_behavior:
                device_behavior[device] = {
                    "total_sessions": 0,
                    "total_duration": 0,
                    "total_pages": 0,
                    "avg_duration": 0,
                    "avg_pages_per_session": 0,
                    "unique_users": set()
                }
            
            device_behavior[device]["total_sessions"] += 1
            device_behavior[device]["total_duration"] += session.session_duration_minutes or 0
            device_behavior[device]["total_pages"] += session.pages_viewed or 0
            device_behavior[device]["unique_users"].add(session.user_id)
        
        # Calculate averages and convert sets to counts
        for device, data in device_behavior.items():
            data["avg_duration"] = data["total_duration"] / max(data["total_sessions"], 1)
            data["avg_pages_per_session"] = data["total_pages"] / max(data["total_sessions"], 1)
            data["unique_users"] = len(data["unique_users"])
            data["avg_duration"] = round(data["avg_duration"], 2)
            data["avg_pages_per_session"] = round(data["avg_pages_per_session"], 2)
        
        return {
            "device_comparison": device_comparison,
            "behavior_metric": behavior_metric,
            "device_analysis": device_behavior,
            "insights": {
                "most_used_device": max(device_behavior.items(),
                                      key=lambda x: x[1]["total_sessions"])[0] if device_behavior else None,
                "highest_engagement_device": max(device_behavior.items(),
                                               key=lambda x: x[1]["avg_duration"])[0] if device_behavior else None
            }
        }
    
    def _calculate_engagement_level(self, sessions: List, page_views: List, purchases: List) -> str:
        """Calculate user engagement level"""
        session_score = len(sessions) * 1
        page_view_score = len(page_views) * 0.5
        purchase_score = len(purchases) * 3
        
        total_score = session_score + page_view_score + purchase_score
        
        if total_score > 50:
            return "high"
        elif total_score > 15:
            return "medium"
        elif total_score > 0:
            return "low"
        else:
            return "inactive"
    
    def _analyze_user_journey_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Extract user journey analysis from natural language query"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        import re
        
        # Extract user ID if mentioned
        user_match = re.search(r'user\s+(\d+)', query.lower())
        if user_match:
            user_id = int(user_match.group(1))
            return self._get_user_journey({"user_id": user_id}, db)
        
        # Default journey analysis for recent users
        recent_sessions = db.query(UserSession).order_by(desc(UserSession.session_start)).limit(5).all()
        journey_examples = []
        
        for session in recent_sessions:
            journey_data = self._get_user_journey({"session_id": session.id}, db)
            journey_examples.append(journey_data)
        
        return {
            "query_analysis": "General user journey patterns",
            "sample_journeys": journey_examples
        }
    
    def _analyze_sessions_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze sessions based on query"""
        return self._analyze_session_patterns({}, db)
    
    def _analyze_engagement_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze engagement based on query"""
        return self._analyze_engagement_metrics({}, db)
    
    def _analyze_retention_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze retention based on query"""
        return {"message": "Retention analysis feature coming soon"}
    
    def _analyze_device_behavior_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze device behavior based on query"""
        return self._analyze_session_patterns({"group_by": "device"}, db)
    
    def _analyze_segmentation_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze user segmentation based on query"""
        return self._get_user_segmentation({}, db)
    
    def _analyze_general_behavior(self, query: str, db: Session) -> Dict[str, Any]:
        """General behavior analysis"""
        # Extract user ID if mentioned
        import re
        user_match = re.search(r'user\s+(\d+)', query.lower())
        
        if user_match:
            user_id = int(user_match.group(1))
            return self._analyze_user_behavior({"user_id": user_id}, db)
        else:
            # Return overall behavior patterns
            return self._analyze_engagement_metrics({}, db)
    
    def _create_summary(self, data: Dict[str, Any]) -> str:
        """Create human-readable summary of user behavior data"""
        if "behavior_summary" in data:
            summary = data["behavior_summary"]
            user = data.get("user_profile", {})
            
            return f"""
User Behavior Analysis for {user.get('name', 'Unknown User')}:

📊 Activity Summary:
• Sessions: {summary.get('total_sessions', 0)} over {summary.get('analysis_period_days', 0)} days
• Average session duration: {summary.get('avg_session_duration_minutes', 0):.1f} minutes
• Page views: {summary.get('total_page_views', 0)} ({summary.get('pages_per_session', 0):.1f} per session)

💰 Purchase Behavior:
• Total purchases: {summary.get('total_purchases', 0)}
• Total spent: ${summary.get('total_spent', 0):.2f}
• Average order value: ${summary.get('avg_order_value', 0):.2f}

📱 Device Preferences: {', '.join(f"{k}: {v}" for k, v in data.get('device_preferences', {}).items())}
🎯 Engagement Level: {data.get('engagement_level', 'unknown').title()}
            """.strip()
        
        return f"User Behavior Agent processed: {json.dumps(data, indent=2, default=str)}"