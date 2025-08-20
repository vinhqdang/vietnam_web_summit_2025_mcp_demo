import asyncio
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from pathlib import Path

class GeminiMCPClient:
    """
    Gemini client that uses MCP tools for database queries
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.mcp_server_path = Path(__file__).parent.parent / "backend" / "mcp_server" / "mcp_server.py"
        
    async def query_with_tools(self, user_query: str) -> str:
        """
        Query the database using Gemini with MCP tools
        """
        try:
            # Define the tools available to Gemini (simulating MCP tools)
            tools = self._get_available_tools()
            
            # Create a system prompt that explains the available tools
            system_prompt = f"""
            You are an AI assistant with access to an e-commerce user behavior database through MCP tools.
            
            Available tools:
            {json.dumps(tools, indent=2)}
            
            The database contains:
            - Users (100 users): id, name, email, age, gender, location, registration_date, is_premium
            - Products (50 products): id, name, category, price, brand, rating, stock_quantity, description
            - User Sessions: user_id, session_start, session_duration, pages_viewed, device_type, browser
            - Page Views: session_id, product_id, page_type, timestamp, time_spent_seconds
            - Purchases: user_id, product_id, quantity, total_amount, purchase_date, payment_method
            - Reviews: user_id, product_id, rating, review_text, review_date
            
            When responding to queries:
            1. First determine which tool(s) would be most appropriate
            2. Explain what tool you would call and with what parameters
            3. Simulate calling the tool and provide realistic sample data
            4. Provide insights and analysis based on the simulated results
            
            Be specific and provide actionable insights. Format your response to be informative and professional.
            """
            
            # Generate response using Gemini
            response = self.model.generate_content(
                f"{system_prompt}\n\nUser Query: {user_query}\n\nPlease provide a comprehensive response with specific data insights."
            )
            
            return response.text
            
        except Exception as e:
            return f"Error processing query with Gemini MCP: {str(e)}"
    
    def _get_available_tools(self) -> List[Dict]:
        """
        Get the list of available MCP tools
        """
        return [
            {
                "name": "get_user_info",
                "description": "Get user information by user ID or email",
                "parameters": ["user_id", "email"]
            },
            {
                "name": "get_user_behavior_summary", 
                "description": "Get comprehensive behavior summary for a user",
                "parameters": ["user_id"]
            },
            {
                "name": "search_products",
                "description": "Search products by name, category, brand, or price range",
                "parameters": ["name", "category", "brand", "min_price", "max_price", "limit"]
            },
            {
                "name": "get_product_analytics",
                "description": "Get detailed analytics for a product",
                "parameters": ["product_id"]
            },
            {
                "name": "get_top_products",
                "description": "Get top products by various metrics",
                "parameters": ["metric", "limit", "category"]
            },
            {
                "name": "analyze_user_sessions",
                "description": "Analyze user session patterns",
                "parameters": ["user_id", "days_back"]
            },
            {
                "name": "get_purchase_patterns",
                "description": "Analyze purchase patterns and trends",
                "parameters": ["user_id", "product_id", "category", "days_back"]
            },
            {
                "name": "query_database",
                "description": "Execute natural language queries on the database",
                "parameters": ["query_description"]
            }
        ]
    
    async def simulate_mcp_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """
        Simulate an MCP tool call with realistic sample data
        """
        # This would normally call the actual MCP server
        # For demo purposes, we'll return realistic sample data
        
        if tool_name == "get_user_behavior_summary":
            return {
                "user": {
                    "id": parameters.get("user_id", 1),
                    "name": "Alice Johnson 1",
                    "email": "user1@example.com",
                    "is_premium": True
                },
                "session_activity": {
                    "total_sessions": 15,
                    "avg_session_duration_minutes": 12.5,
                    "total_pages_viewed": 180
                },
                "purchase_behavior": {
                    "total_purchases": 8,
                    "total_spent": 1250.50,
                    "favorite_category": "Electronics"
                },
                "device_preferences": {
                    "mobile": 8,
                    "desktop": 5,
                    "tablet": 2
                }
            }
        
        elif tool_name == "get_product_analytics":
            return {
                "product": {
                    "id": parameters.get("product_id", 1),
                    "name": "Product 1",
                    "category": "Electronics",
                    "brand": "Apple",
                    "price": 299.99
                },
                "engagement": {
                    "total_views": 1250,
                    "total_purchases": 45,
                    "conversion_rate": 3.6
                },
                "revenue": {
                    "total_revenue": 13499.55,
                    "avg_order_value": 299.99
                },
                "reviews": {
                    "total_reviews": 32,
                    "average_rating": 4.2
                }
            }
        
        elif tool_name == "get_top_products":
            metric = parameters.get("metric", "revenue")
            limit = parameters.get("limit", 10)
            return [
                {
                    "id": i,
                    "name": f"Product {i}",
                    "category": ["Electronics", "Clothing", "Books"][i % 3],
                    "revenue": 15000 - (i * 500),
                    "views": 2000 - (i * 100),
                    "purchases": 100 - (i * 5),
                    "rating": 4.5 - (i * 0.1)
                }
                for i in range(1, min(limit + 1, 11))
            ]
        
        else:
            return {"message": f"Tool {tool_name} called with parameters: {parameters}"}

class EnhancedMCPClient:
    """
    Enhanced MCP client that provides both direct tool access and LLM integration
    """
    
    def __init__(self):
        self.gemini_client = GeminiMCPClient()
    
    async def query_natural_language(self, query: str) -> str:
        """
        Process natural language query using Gemini with MCP context
        """
        return await self.gemini_client.query_with_tools(query)
    
    async def get_user_behavior(self, user_id: int) -> Dict:
        """
        Get user behavior using direct MCP tool simulation
        """
        return await self.gemini_client.simulate_mcp_tool_call(
            "get_user_behavior_summary", 
            {"user_id": user_id}
        )
    
    async def get_product_analytics(self, product_id: int) -> Dict:
        """
        Get product analytics using direct MCP tool simulation
        """
        return await self.gemini_client.simulate_mcp_tool_call(
            "get_product_analytics",
            {"product_id": product_id}
        )
    
    async def get_top_products(self, metric: str = "revenue", limit: int = 10) -> List[Dict]:
        """
        Get top products using direct MCP tool simulation
        """
        return await self.gemini_client.simulate_mcp_tool_call(
            "get_top_products",
            {"metric": metric, "limit": limit}
        )
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities of this MCP client
        """
        return {
            "natural_language_queries": True,
            "direct_tool_access": True,
            "llm_integration": "Gemini 2.0 Flash",
            "available_tools": self.gemini_client._get_available_tools()
        }

# Example usage
async def main():
    """
    Example usage of the MCP client
    """
    client = EnhancedMCPClient()
    
    # Test natural language query
    nl_result = await client.query_natural_language(
        "What is the behavior summary for user 5? Include their purchase patterns and session activity."
    )
    print("Natural Language Query Result:")
    print(nl_result)
    print("\n" + "="*50 + "\n")
    
    # Test direct tool access
    behavior_result = await client.get_user_behavior(user_id=5)
    print("Direct Tool Access Result:")
    print(json.dumps(behavior_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())