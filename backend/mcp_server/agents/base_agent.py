"""
Base Agent class for the multi-agent MCP system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = []
        self.tools = {}
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    @abstractmethod
    def can_handle_query(self, query: str) -> bool:
        """Determine if this agent can handle the given query"""
        pass
    
    @abstractmethod
    def process_query(self, query: str, db: Session, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return results"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for this agent"""
        pass
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Call a specific tool"""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not available for agent {self.name}"}
        
        try:
            return self.tools[tool_name](parameters, db)
        except Exception as e:
            return {"error": f"Error calling tool {tool_name}: {str(e)}"}
    
    def format_response(self, data: Dict[str, Any], format_type: str = "json") -> str:
        """Format response data"""
        if format_type == "json":
            return json.dumps(data, indent=2, default=str)
        elif format_type == "summary":
            return self._create_summary(data)
        else:
            return str(data)
    
    def _create_summary(self, data: Dict[str, Any]) -> str:
        """Create a human-readable summary of the data"""
        # Default implementation - subclasses should override
        return f"Agent {self.name} processed data: {json.dumps(data, default=str)}"
    
    def log_interaction(self, query: str, response: Dict[str, Any]):
        """Log agent interactions for debugging"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "query": query,
            "response_keys": list(response.keys()) if isinstance(response, dict) else "non-dict",
            "status": "success" if "error" not in response else "error"
        }
        # In a real system, this would write to a log file or database
        print(f"[{self.name}] {log_entry}")


class AgentCapability:
    """Define agent capabilities and their matching patterns"""
    
    USER_BEHAVIOR = "user_behavior"
    FINANCIAL_ANALYSIS = "financial_analysis"
    PRODUCT_ANALYTICS = "product_analytics"
    SESSION_ANALYSIS = "session_analysis"
    PURCHASE_PATTERNS = "purchase_patterns"
    REVENUE_REPORTING = "revenue_reporting"
    PROFIT_ANALYSIS = "profit_analysis"
    COST_ANALYSIS = "cost_analysis"
    
    # Keyword mappings for query routing
    CAPABILITY_KEYWORDS = {
        USER_BEHAVIOR: [
            "user", "customer", "behavior", "activity", "engagement", 
            "session", "page view", "interaction", "browsing"
        ],
        FINANCIAL_ANALYSIS: [
            "revenue", "profit", "financial", "earnings", "income", "sales",
            "money", "cost", "expense", "margin", "roi", "financial report"
        ],
        PRODUCT_ANALYTICS: [
            "product", "conversion", "performance", "analytics", "metrics"
        ],
        SESSION_ANALYSIS: [
            "session", "duration", "device", "browser", "time spent"
        ],
        PURCHASE_PATTERNS: [
            "purchase", "buy", "order", "transaction", "payment"
        ],
        REVENUE_REPORTING: [
            "revenue", "sales report", "income", "earnings", "financial performance"
        ],
        PROFIT_ANALYSIS: [
            "profit", "margin", "profitability", "cost analysis", "roi"
        ]
    }
    
    @classmethod
    def match_capability(cls, query: str) -> List[str]:
        """Match query to capabilities based on keywords"""
        query_lower = query.lower()
        matched_capabilities = []
        
        for capability, keywords in cls.CAPABILITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if capability not in matched_capabilities:
                        matched_capabilities.append(capability)
                    break
        
        return matched_capabilities


class AgentCoordinator:
    """Coordinates multiple agents and routes queries"""
    
    def __init__(self):
        self.agents = {}
        self.interaction_history = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
    
    def route_query(self, query: str) -> List[BaseAgent]:
        """Route query to appropriate agents"""
        capabilities_needed = AgentCapability.match_capability(query)
        suitable_agents = []
        
        for agent in self.agents.values():
            agent_capabilities = agent.get_capabilities()
            if any(cap in agent_capabilities for cap in capabilities_needed):
                suitable_agents.append(agent)
        
        # If no specific match, return all agents (they can decide if they can handle it)
        if not suitable_agents:
            suitable_agents = list(self.agents.values())
        
        return suitable_agents
    
    def process_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Process query using appropriate agents"""
        agents = self.route_query(query)
        results = {}
        
        for agent in agents:
            if agent.can_handle_query(query):
                try:
                    result = agent.process_query(query, db)
                    results[agent.agent_id] = {
                        "agent_name": agent.name,
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    results[agent.agent_id] = {
                        "agent_name": agent.name,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        # Log the interaction
        self.interaction_history.append({
            "query": query,
            "agents_used": [agent.agent_id for agent in agents],
            "timestamp": datetime.utcnow().isoformat(),
            "results_count": len(results)
        })
        
        return {
            "query": query,
            "agents_consulted": len(agents),
            "results": results,
            "processing_timestamp": datetime.utcnow().isoformat()
        }