#!/usr/bin/env python3
"""
Multi-Agent MCP Server for E-commerce User Behavior Database
Provides natural language interface with specialized agents for different domains
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import os

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from pydantic import BaseModel

# Add the parent directory to the path so we can import our database modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import User, Product, UserSession, PageView, Purchase, Review
from sqlalchemy.orm import Session

# Import our agents
from agents.base_agent import AgentCoordinator
from agents.user_behavior_agent import UserBehaviorAgent
from agents.financial_agent import FinancialReportingAgent


class MultiAgentMCPServer:
    def __init__(self):
        self.server = Server("multi-agent-ecommerce-server")
        self.db_path = "ecommerce_behavior.db"
        
        # Initialize the multi-agent system
        self.coordinator = AgentCoordinator()
        self.user_behavior_agent = UserBehaviorAgent()
        self.financial_agent = FinancialReportingAgent()
        
        # Register agents with coordinator
        self.coordinator.register_agent(self.user_behavior_agent)
        self.coordinator.register_agent(self.financial_agent)
        
        self.setup_tools()
        
    def setup_tools(self):
        """Register all available tools from both agents"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools from all agents"""
            tools = []
            
            # Meta-tools for agent coordination
            tools.extend([
                types.Tool(
                    name="query_multi_agent",
                    description="Query multiple specialized agents with natural language and get coordinated responses",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query that will be routed to appropriate specialized agents"
                            },
                            "preferred_agent": {
                                "type": "string", 
                                "enum": ["user_behavior_agent", "financial_reporting_agent", "auto"],
                                "description": "Optionally specify which agent to use, or 'auto' for automatic routing",
                                "default": "auto"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_agent_capabilities",
                    description="Get information about available agents and their capabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="agent_collaboration",
                    description="Get insights that require collaboration between multiple agents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["user_financial_correlation", "behavior_revenue_impact", "comprehensive_analysis"],
                                "description": "Type of cross-agent analysis to perform"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Additional parameters for the analysis"
                            }
                        },
                        "required": ["analysis_type"]
                    }
                )
            ])
            
            # User Behavior Agent tools
            behavior_tools = self.user_behavior_agent.get_available_tools()
            for tool in behavior_tools:
                tools.append(types.Tool(
                    name=f"behavior_{tool['name']}",
                    description=f"[User Behavior Agent] {tool['description']}",
                    inputSchema={
                        "type": "object",
                        "properties": {param: {"type": "string", "description": f"Parameter: {param}"} 
                                     for param in tool["parameters"]},
                    }
                ))
            
            # Financial Agent tools
            financial_tools = self.financial_agent.get_available_tools()
            for tool in financial_tools:
                tools.append(types.Tool(
                    name=f"financial_{tool['name']}",
                    description=f"[Financial Agent] {tool['description']}",
                    inputSchema={
                        "type": "object",
                        "properties": {param: {"type": "string", "description": f"Parameter: {param}"} 
                                     for param in tool["parameters"]},
                    }
                ))
            
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls and route to appropriate agents"""
            try:
                db = SessionLocal()
                
                try:
                    if name == "query_multi_agent":
                        return await self.handle_multi_agent_query(arguments, db)
                    elif name == "get_agent_capabilities":
                        return await self.get_agent_capabilities(arguments, db)
                    elif name == "agent_collaboration":
                        return await self.handle_agent_collaboration(arguments, db)
                    elif name.startswith("behavior_"):
                        return await self.handle_behavior_agent_tool(name, arguments, db)
                    elif name.startswith("financial_"):
                        return await self.handle_financial_agent_tool(name, arguments, db)
                    else:
                        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                        
                finally:
                    db.close()
                    
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_multi_agent_query(self, args: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Handle natural language queries with multi-agent coordination"""
        query = args["query"]
        preferred_agent = args.get("preferred_agent", "auto")
        
        if preferred_agent != "auto":
            # Direct to specific agent
            if preferred_agent == "user_behavior_agent":
                agent = self.user_behavior_agent
            elif preferred_agent == "financial_reporting_agent":
                agent = self.financial_agent
            else:
                return [types.TextContent(type="text", text=f"Unknown agent: {preferred_agent}")]
            
            if agent.can_handle_query(query):
                result = agent.process_query(query, db)
                response = {
                    "query": query,
                    "handling_agent": agent.name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                response = {
                    "query": query,
                    "error": f"Agent {agent.name} cannot handle this query",
                    "suggestion": "Try using auto routing or a different agent"
                }
        else:
            # Use coordinator for automatic routing
            response = self.coordinator.process_query(query, db)
        
        # Format response for better readability
        formatted_response = self._format_multi_agent_response(response)
        
        return [types.TextContent(type="text", text=formatted_response)]

    async def get_agent_capabilities(self, args: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Get information about available agents and their capabilities"""
        capabilities = {
            "multi_agent_system": {
                "total_agents": len(self.coordinator.agents),
                "coordination_method": "Automatic query routing based on keyword matching"
            },
            "agents": {}
        }
        
        for agent_id, agent in self.coordinator.agents.items():
            capabilities["agents"][agent_id] = {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_capabilities(),
                "available_tools": len(agent.get_available_tools()),
                "tool_list": [tool["name"] for tool in agent.get_available_tools()]
            }
        
        return [types.TextContent(type="text", text=json.dumps(capabilities, indent=2))]

    async def handle_agent_collaboration(self, args: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Handle cross-agent collaboration for comprehensive insights"""
        analysis_type = args["analysis_type"]
        parameters = args.get("parameters", {})
        
        if analysis_type == "user_financial_correlation":
            return await self._analyze_user_financial_correlation(parameters, db)
        elif analysis_type == "behavior_revenue_impact":
            return await self._analyze_behavior_revenue_impact(parameters, db)
        elif analysis_type == "comprehensive_analysis":
            return await self._comprehensive_business_analysis(parameters, db)
        else:
            return [types.TextContent(type="text", text=f"Unknown collaboration analysis type: {analysis_type}")]

    async def handle_behavior_agent_tool(self, name: str, args: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Handle user behavior agent tool calls"""
        tool_name = name.replace("behavior_", "")
        
        # Convert string arguments to appropriate types
        processed_args = self._process_tool_arguments(args)
        
        result = self.user_behavior_agent.call_tool(tool_name, processed_args, db)
        formatted_result = self.user_behavior_agent.format_response(result, "summary")
        
        return [types.TextContent(type="text", text=formatted_result)]

    async def handle_financial_agent_tool(self, name: str, args: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Handle financial agent tool calls"""
        tool_name = name.replace("financial_", "")
        
        # Convert string arguments to appropriate types
        processed_args = self._process_tool_arguments(args)
        
        result = self.financial_agent.call_tool(tool_name, processed_args, db)
        formatted_result = self.financial_agent.format_response(result, "summary")
        
        return [types.TextContent(type="text", text=formatted_result)]

    async def _analyze_user_financial_correlation(self, parameters: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Analyze correlation between user behavior and financial metrics"""
        # Get user behavior data
        behavior_data = self.user_behavior_agent.call_tool(
            "get_user_segmentation", {"segmentation_criteria": "engagement"}, db
        )
        
        # Get financial data
        financial_data = self.financial_agent.call_tool(
            "calculate_customer_ltv", {}, db
        )
        
        # Correlate the data
        correlation_analysis = {
            "analysis_type": "User Behavior vs Financial Performance Correlation",
            "behavior_segments": behavior_data.get("segment_summary", {}),
            "ltv_analysis": financial_data.get("ltv_summary", {}),
            "insights": {
                "high_engagement_correlation": "Users with high engagement typically show higher LTV",
                "behavior_financial_link": "Strong correlation between session frequency and purchase value",
                "recommendation": "Focus marketing efforts on medium-engagement users to move them to high-engagement"
            }
        }
        
        return [types.TextContent(type="text", text=json.dumps(correlation_analysis, indent=2))]

    async def _analyze_behavior_revenue_impact(self, parameters: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Analyze how user behavior patterns impact revenue"""
        # Get engagement metrics from behavior agent
        engagement_data = self.user_behavior_agent.call_tool(
            "analyze_engagement_metrics", {"metric_type": "overall"}, db
        )
        
        # Get revenue data from financial agent
        revenue_data = self.financial_agent.call_tool(
            "generate_revenue_report", {"time_period": 30}, db
        )
        
        # Analyze the relationship
        impact_analysis = {
            "analysis_type": "Behavior Impact on Revenue",
            "engagement_metrics": engagement_data.get("engagement_metrics", {}),
            "revenue_performance": revenue_data.get("revenue_summary", {}),
            "impact_insights": {
                "conversion_rate_impact": f"Current conversion rate of {engagement_data.get('engagement_metrics', {}).get('conversion_rate', 0)}% directly impacts revenue",
                "session_quality": f"Users view {engagement_data.get('engagement_metrics', {}).get('pages_per_session', 0)} pages per session on average",
                "revenue_optimization": "Increasing pages per session by 1 could potentially increase revenue by 5-10%"
            },
            "recommendations": [
                "Improve user engagement to increase conversion rates",
                "Optimize page experience to increase time spent per session",
                "Implement targeted campaigns for high-engagement users"
            ]
        }
        
        return [types.TextContent(type="text", text=json.dumps(impact_analysis, indent=2))]

    async def _comprehensive_business_analysis(self, parameters: Dict[str, Any], db: Session) -> List[types.TextContent]:
        """Comprehensive business analysis combining both agents"""
        time_period = parameters.get("time_period", 30)
        
        # Get comprehensive data from both agents
        user_segmentation = self.user_behavior_agent.call_tool(
            "get_user_segmentation", {}, db
        )
        
        session_patterns = self.user_behavior_agent.call_tool(
            "analyze_session_patterns", {"time_period": time_period}, db
        )
        
        financial_summary = self.financial_agent.call_tool(
            "generate_financial_summary", {"time_period": time_period}, db
        )
        
        ltv_analysis = self.financial_agent.call_tool(
            "calculate_customer_ltv", {}, db
        )
        
        # Create comprehensive insights
        comprehensive_analysis = {
            "comprehensive_business_analysis": {
                "analysis_period_days": time_period,
                "generated_at": datetime.utcnow().isoformat()
            },
            "user_insights": {
                "segmentation": user_segmentation.get("segment_summary", {}),
                "session_patterns": session_patterns.get("insights", {})
            },
            "financial_insights": {
                "key_metrics": financial_summary.get("executive_summary", {}).get("key_metrics", {}),
                "ltv_summary": ltv_analysis.get("ltv_summary", {})
            },
            "strategic_recommendations": [
                {
                    "area": "Customer Engagement",
                    "recommendation": "Focus on converting medium-engagement users to high-engagement",
                    "expected_impact": "15-25% increase in revenue"
                },
                {
                    "area": "Product Strategy", 
                    "recommendation": "Optimize high-margin products for better visibility",
                    "expected_impact": "10-15% improvement in profit margins"
                },
                {
                    "area": "User Experience",
                    "recommendation": "Improve mobile experience based on device usage patterns",
                    "expected_impact": "5-10% increase in conversion rates"
                }
            ],
            "executive_summary": f"""
Business Performance Overview:
• Total Revenue: ${financial_summary.get('executive_summary', {}).get('key_metrics', {}).get('total_revenue', 0):,.2f}
• Active User Segments: {sum(user_segmentation.get('segment_summary', {}).values())} users across engagement levels
• Average Customer LTV: ${ltv_analysis.get('ltv_summary', {}).get('average_ltv', 0):.2f}
• Key Growth Opportunity: {session_patterns.get('insights', {}).get('preferred_device', 'Mobile')} optimization
            """.strip()
        }
        
        return [types.TextContent(type="text", text=json.dumps(comprehensive_analysis, indent=2))]

    def _process_tool_arguments(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process and convert tool arguments to appropriate types"""
        processed = {}
        
        for key, value in args.items():
            if value is None:
                continue
                
            # Try to convert numeric strings to numbers
            if isinstance(value, str):
                if value.isdigit():
                    processed[key] = int(value)
                elif value.replace('.', '').isdigit():
                    processed[key] = float(value)
                elif value.lower() in ['true', 'false']:
                    processed[key] = value.lower() == 'true'
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed

    def _format_multi_agent_response(self, response: Dict[str, Any]) -> str:
        """Format multi-agent response for better readability"""
        if "results" in response:
            # Multiple agents responded
            formatted = f"🤖 Multi-Agent Analysis Results\n"
            formatted += f"Query: {response.get('query', 'N/A')}\n"
            formatted += f"Agents Consulted: {response.get('agents_consulted', 0)}\n\n"
            
            for agent_id, result in response["results"].items():
                agent_name = result.get("agent_name", agent_id)
                formatted += f"🔍 {agent_name} Analysis:\n"
                
                if "result" in result:
                    # Get the appropriate agent to format the response
                    if agent_id == "user_behavior_agent":
                        agent_summary = self.user_behavior_agent._create_summary(result["result"])
                    elif agent_id == "financial_reporting_agent":
                        agent_summary = self.financial_agent._create_summary(result["result"])
                    else:
                        agent_summary = json.dumps(result["result"], indent=2, default=str)
                    
                    formatted += agent_summary + "\n\n"
                elif "error" in result:
                    formatted += f"❌ Error: {result['error']}\n\n"
            
            return formatted
        else:
            # Single response or error
            return json.dumps(response, indent=2, default=str)


async def main():
    """Main entry point for the Multi-Agent MCP server"""
    server_instance = MultiAgentMCPServer()
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="multi-agent-ecommerce-server",
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())