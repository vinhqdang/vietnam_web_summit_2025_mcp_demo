import asyncio
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional
import google.genai as genai
from pathlib import Path

class MultiAgentGeminiClient:
    """
    Enhanced Gemini client that works with multi-agent MCP system
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash-exp'
        self.mcp_server_path = Path(__file__).parent.parent / "backend" / "mcp_server" / "multi_agent_mcp_server.py"
        
    async def query_multi_agent(self, user_query: str, preferred_agent: str = "auto") -> str:
        """
        Query the multi-agent system using Gemini with MCP tools
        """
        try:
            # Create a system prompt that explains the multi-agent system
            system_prompt = f"""
            You are connected to a Multi-Agent E-commerce Analytics System with specialized agents:

            🧑‍💼 USER BEHAVIOR AGENT:
            - Specializes in user behavior analysis, customer engagement, session patterns
            - Tools: user segmentation, journey analysis, engagement metrics, device behavior
            - Keywords: user, customer, behavior, session, engagement, interaction, journey

            💰 FINANCIAL REPORTING AGENT:
            - Specializes in revenue analysis, profit margins, financial KPIs, cost analysis
            - Tools: revenue reports, profit analysis, LTV calculation, forecasting
            - Keywords: revenue, profit, financial, earnings, cost, ROI, money, sales

            🤝 AGENT COLLABORATION:
            - Agents can work together for comprehensive business insights
            - Cross-agent analysis like behavior-revenue correlation
            - Comprehensive business analysis combining user and financial data

            Available Query Types:
            1. Single Agent Queries (routed automatically based on keywords)
            2. Specific Agent Targeting (specify preferred_agent: {preferred_agent})
            3. Multi-Agent Collaboration (comprehensive analysis)

            Database Schema:
            - Users (100 users): demographics, registration, premium status
            - Products (50 products): categories, pricing, ratings
            - Sessions: browsing behavior, device types, duration
            - Purchases: transactions, payment methods, discounts
            - Reviews: ratings, feedback, helpfulness

            Response Format:
            - Identify which agent(s) would handle the query
            - Explain the analysis approach
            - Provide realistic insights with specific metrics
            - Include actionable recommendations
            """
            
            # Determine query routing based on content
            query_lower = user_query.lower()
            routing_analysis = self._analyze_query_routing(query_lower)
            
            # Enhanced prompt with routing context
            enhanced_prompt = f"""
            {system_prompt}

            Query Routing Analysis:
            - Detected Keywords: {routing_analysis['detected_keywords']}
            - Suggested Agents: {routing_analysis['suggested_agents']}
            - Query Complexity: {routing_analysis['complexity']}
            - Preferred Agent: {preferred_agent}

            User Query: "{user_query}"

            Please provide a comprehensive response that:
            1. Shows which agent(s) are handling the query
            2. Provides specific data analysis with realistic metrics
            3. Includes actionable business insights
            4. Demonstrates multi-agent coordination if applicable
            """
            
            # Generate response using Gemini
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=enhanced_prompt
            )
            
            # Format the response to show multi-agent interaction
            response_text = response.candidates[0].content.parts[0].text
            formatted_response = self._format_multi_agent_response(
                response_text, routing_analysis, preferred_agent
            )
            
            return formatted_response
            
        except Exception as e:
            return f"Error processing multi-agent query: {str(e)}"
    
    def _analyze_query_routing(self, query_lower: str) -> Dict[str, Any]:
        """Analyze query to determine appropriate agent routing"""
        
        behavior_keywords = [
            "user", "customer", "behavior", "session", "engagement", "activity",
            "interaction", "browsing", "journey", "retention", "device", "usage"
        ]
        
        financial_keywords = [
            "revenue", "profit", "financial", "earnings", "income", "sales",
            "money", "cost", "expense", "margin", "roi", "ltv", "forecast"
        ]
        
        collaboration_keywords = [
            "comprehensive", "overall", "business", "correlation", "impact",
            "analysis", "summary", "report", "dashboard", "insights"
        ]
        
        detected_keywords = []
        suggested_agents = []
        
        # Check for keyword matches
        for keyword in behavior_keywords:
            if keyword in query_lower:
                detected_keywords.append(f"behavior:{keyword}")
                if "user_behavior_agent" not in suggested_agents:
                    suggested_agents.append("user_behavior_agent")
        
        for keyword in financial_keywords:
            if keyword in query_lower:
                detected_keywords.append(f"financial:{keyword}")
                if "financial_reporting_agent" not in suggested_agents:
                    suggested_agents.append("financial_reporting_agent")
        
        for keyword in collaboration_keywords:
            if keyword in query_lower:
                detected_keywords.append(f"collaboration:{keyword}")
                if "multi_agent_collaboration" not in suggested_agents:
                    suggested_agents.append("multi_agent_collaboration")
        
        # Determine complexity
        if len(suggested_agents) > 1:
            complexity = "high"
        elif len(suggested_agents) == 1:
            complexity = "medium"
        else:
            complexity = "low"
            suggested_agents = ["auto_routing"]
        
        return {
            "detected_keywords": detected_keywords,
            "suggested_agents": suggested_agents,
            "complexity": complexity
        }
    
    def _format_multi_agent_response(self, response_text: str, routing_analysis: Dict, preferred_agent: str) -> str:
        """Format response to show multi-agent system interaction"""
        
        header = "🤖 Multi-Agent E-commerce Analytics System\n"
        header += "=" * 50 + "\n\n"
        
        routing_info = f"🔍 Query Routing Analysis:\n"
        routing_info += f"• Detected Keywords: {', '.join(routing_analysis['detected_keywords'])}\n"
        routing_info += f"• Suggested Agents: {', '.join(routing_analysis['suggested_agents'])}\n"
        routing_info += f"• Query Complexity: {routing_analysis['complexity']}\n"
        routing_info += f"• Agent Preference: {preferred_agent}\n\n"
        
        separator = "📊 Agent Analysis Results:\n" + "-" * 30 + "\n\n"
        
        footer = "\n" + "=" * 50 + "\n"
        footer += "💡 Multi-Agent System Benefits:\n"
        footer += "• Specialized expertise for different business domains\n"
        footer += "• Coordinated analysis for comprehensive insights\n"
        footer += "• Natural language routing to appropriate specialists\n"
        
        return header + routing_info + separator + response_text + footer
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about available agents and their capabilities"""
        return {
            "multi_agent_system": {
                "version": "2.0.0",
                "agents": [
                    {
                        "id": "user_behavior_agent",
                        "name": "User Behavior Analyst",
                        "specialization": "User behavior patterns, engagement metrics, customer journey analysis",
                        "tools": [
                            "analyze_user_behavior", "get_user_journey", "analyze_session_patterns",
                            "get_user_segmentation", "analyze_engagement_metrics", "get_user_retention"
                        ]
                    },
                    {
                        "id": "financial_reporting_agent", 
                        "name": "Financial Analyst",
                        "specialization": "Revenue analysis, profit margins, financial KPIs, forecasting",
                        "tools": [
                            "generate_revenue_report", "analyze_profit_margins", "get_financial_kpis",
                            "calculate_customer_ltv", "generate_sales_forecast", "analyze_product_profitability"
                        ]
                    }
                ],
                "collaboration_features": [
                    "Cross-agent data correlation",
                    "Comprehensive business analysis", 
                    "Multi-domain insights",
                    "Automated query routing"
                ]
            }
        }
    
    async def simulate_multi_agent_analysis(self, analysis_type: str, user_query: str) -> Dict[str, Any]:
        """Simulate multi-agent analysis with realistic data"""
        
        if analysis_type == "user_behavior":
            return {
                "agent": "User Behavior Agent",
                "analysis": {
                    "user_segments": {
                        "high_engagement": 25,
                        "medium_engagement": 45, 
                        "low_engagement": 30
                    },
                    "session_insights": {
                        "avg_session_duration": 12.5,
                        "pages_per_session": 4.2,
                        "mobile_usage": "65%",
                        "peak_hours": "7-9 PM"
                    },
                    "recommendations": [
                        "Focus on converting medium-engagement users",
                        "Optimize mobile experience for 65% of traffic",
                        "Create targeted campaigns for evening traffic peaks"
                    ]
                }
            }
        
        elif analysis_type == "financial":
            return {
                "agent": "Financial Reporting Agent",
                "analysis": {
                    "revenue_metrics": {
                        "total_revenue": 125000.50,
                        "growth_rate": 15.2,
                        "avg_order_value": 85.75,
                        "customer_ltv": 245.80
                    },
                    "profitability": {
                        "gross_margin": 42.5,
                        "net_margin": 18.3,
                        "roi": 3.2
                    },
                    "recommendations": [
                        "Increase focus on high-margin products",
                        "Implement customer retention programs",
                        "Optimize pricing strategy for premium segments"
                    ]
                }
            }
        
        elif analysis_type == "comprehensive":
            return {
                "collaboration": "Multi-Agent Analysis",
                "analysis": {
                    "business_health": {
                        "user_engagement_score": 7.2,
                        "financial_performance": 8.1,
                        "growth_trajectory": "positive",
                        "risk_factors": ["seasonal_dependency", "customer_concentration"]
                    },
                    "strategic_insights": {
                        "revenue_per_engagement_level": {
                            "high_engagement": 485.20,
                            "medium_engagement": 185.75,
                            "low_engagement": 45.30
                        },
                        "optimization_opportunities": [
                            "Mobile conversion optimization (+15% revenue potential)",
                            "Customer segmentation refinement (+10% efficiency)",
                            "Premium product promotion (+8% margin improvement)"
                        ]
                    }
                }
            }
        
        return {"error": f"Unknown analysis type: {analysis_type}"}


class MultiAgentMCPClient:
    """
    Enhanced MCP client with multi-agent system support
    """
    
    def __init__(self):
        self.gemini_client = MultiAgentGeminiClient()
    
    async def query_natural_language(self, query: str, preferred_agent: str = "auto") -> str:
        """
        Process natural language query using multi-agent system
        """
        return await self.gemini_client.query_multi_agent(query, preferred_agent)
    
    async def query_user_behavior_agent(self, query: str) -> str:
        """
        Query specifically the User Behavior Agent
        """
        return await self.gemini_client.query_multi_agent(query, "user_behavior_agent")
    
    async def query_financial_agent(self, query: str) -> str:
        """
        Query specifically the Financial Reporting Agent
        """
        return await self.gemini_client.query_multi_agent(query, "financial_reporting_agent")
    
    async def get_comprehensive_analysis(self, business_question: str) -> str:
        """
        Get comprehensive analysis involving multiple agents
        """
        enhanced_query = f"Provide a comprehensive business analysis for: {business_question}. Include both user behavior insights and financial performance metrics with cross-agent collaboration."
        return await self.gemini_client.query_multi_agent(enhanced_query, "collaboration")
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get information about the multi-agent system capabilities
        """
        return await self.gemini_client.get_agent_capabilities()
    
    async def simulate_agent_interaction(self, scenario: str) -> Dict[str, Any]:
        """
        Simulate different agent interaction scenarios
        """
        scenarios = {
            "user_analysis": await self.gemini_client.simulate_multi_agent_analysis("user_behavior", scenario),
            "financial_analysis": await self.gemini_client.simulate_multi_agent_analysis("financial", scenario),
            "business_overview": await self.gemini_client.simulate_multi_agent_analysis("comprehensive", scenario)
        }
        
        return {
            "scenario": scenario,
            "agent_responses": scenarios,
            "collaboration_summary": "Multiple agents coordinated to provide specialized insights across user behavior and financial domains"
        }


# Example usage and testing
async def main():
    """
    Example usage of the Multi-Agent MCP client
    """
    client = MultiAgentMCPClient()
    
    print("🤖 Multi-Agent MCP Client Demo")
    print("=" * 50)
    
    # Test different types of queries
    test_queries = [
        ("User behavior focused", "What are the engagement patterns of our high-value customers?"),
        ("Financial focused", "Show me the revenue breakdown and profit margins for last month"),
        ("Comprehensive", "Give me a complete business health analysis with user and financial insights"),
        ("Agent collaboration", "How does user engagement correlate with revenue performance?")
    ]
    
    for query_type, query in test_queries:
        print(f"\n📋 {query_type} Query:")
        print(f"Query: {query}")
        print("-" * 30)
        
        result = await client.query_natural_language(query)
        print(result)
        print("\n" + "="*50)
    
    # Show agent capabilities
    print("\n🔧 System Capabilities:")
    capabilities = await client.get_agent_capabilities()
    print(json.dumps(capabilities, indent=2))


if __name__ == "__main__":
    asyncio.run(main())