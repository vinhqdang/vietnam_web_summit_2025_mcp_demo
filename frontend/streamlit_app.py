import streamlit as st
import requests
import json
import os
import asyncio
import sys
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from mcp_client import EnhancedMCPClient

# Initialize session state
if 'api_results' not in st.session_state:
    st.session_state.api_results = None
if 'mcp_results' not in st.session_state:
    st.session_state.mcp_results = None

class RestAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request to REST API"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def main():
    st.set_page_config(
        page_title="E-commerce Analytics: REST API vs MCP Demo",
        page_icon="🛒",
        layout="wide"
    )
    
    st.title("🛒 E-commerce User Behavior Analytics")
    st.subtitle("Comparing REST API vs MCP Approaches")
    
    # Initialize clients
    rest_client = RestAPIClient()
    mcp_client = EnhancedMCPClient()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # API Status Check
    st.sidebar.subheader("API Status")
    try:
        health_check = rest_client.get("/health")
        if "error" not in health_check:
            st.sidebar.success("✅ REST API Online")
        else:
            st.sidebar.error("❌ REST API Offline")
    except:
        st.sidebar.error("❌ REST API Offline")
    
    # Check MCP availability (simulated)
    st.sidebar.success("✅ MCP Server Ready")
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Query Interface", "📊 Comparison", "📋 API Documentation"])
    
    with tab1:
        st.header("Query Both Systems")
        
        # Query input
        query_type = st.selectbox(
            "Select Query Type:",
            [
                "User Behavior Summary",
                "Product Analytics",
                "Top Products by Revenue",
                "User Session Analysis",
                "Purchase Patterns",
                "Custom Query"
            ]
        )
        
        # Dynamic input based on query type
        query_params = {}
        
        if query_type == "User Behavior Summary":
            user_id = st.number_input("User ID", min_value=1, max_value=100, value=1)
            query_params["user_id"] = user_id
            rest_endpoint = f"/users/{user_id}/behavior"
            mcp_query = f"Get comprehensive behavior summary for user {user_id}"
            
        elif query_type == "Product Analytics":
            product_id = st.number_input("Product ID", min_value=1, max_value=50, value=1)
            query_params["product_id"] = product_id
            rest_endpoint = f"/products/{product_id}/analytics"
            mcp_query = f"Get detailed analytics for product {product_id}"
            
        elif query_type == "Top Products by Revenue":
            limit = st.number_input("Number of products", min_value=1, max_value=20, value=10)
            query_params["limit"] = limit
            rest_endpoint = "/analytics/top-products"
            mcp_query = f"Show me the top {limit} products by revenue"
            
        elif query_type == "User Session Analysis":
            user_id = st.number_input("User ID (optional)", min_value=0, max_value=100, value=0)
            days_back = st.number_input("Days back", min_value=1, max_value=365, value=30)
            if user_id > 0:
                query_params["user_id"] = user_id
            rest_endpoint = "/sessions"
            mcp_query = f"Analyze user session patterns for {'user ' + str(user_id) if user_id > 0 else 'all users'} in the last {days_back} days"
            
        elif query_type == "Purchase Patterns":
            user_id = st.number_input("User ID (optional)", min_value=0, max_value=100, value=0)
            if user_id > 0:
                query_params["user_id"] = user_id
            rest_endpoint = "/purchases"
            mcp_query = f"Analyze purchase patterns for {'user ' + str(user_id) if user_id > 0 else 'all users'}"
            
        else:  # Custom Query
            custom_query = st.text_area("Enter your query:", placeholder="e.g., What are the most popular products in the Electronics category?")
            rest_endpoint = "/users"  # Default endpoint
            mcp_query = custom_query
        
        # Execute queries
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🌐 Query REST API", use_container_width=True):
                with st.spinner("Querying REST API..."):
                    if query_type == "Custom Query":
                        st.session_state.api_results = {"message": "Custom queries not directly supported by REST API. Please use specific endpoints."}
                    else:
                        st.session_state.api_results = rest_client.get(rest_endpoint, query_params)
        
        with col2:
            if st.button("🔗 Query MCP + Gemini", use_container_width=True):
                with st.spinner("Querying MCP with Gemini..."):
                    if query_type != "Custom Query":
                        query_text = mcp_query
                    else:
                        query_text = custom_query
                    
                    if query_text:
                        # Use asyncio to run the async function
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(mcp_client.query_natural_language(query_text))
                            st.session_state.mcp_results = result
                        except Exception as e:
                            st.session_state.mcp_results = f"Error: {str(e)}"
        
        # Display results
        st.header("Results Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌐 REST API Response")
            if st.session_state.api_results:
                if isinstance(st.session_state.api_results, dict) and "error" in st.session_state.api_results:
                    st.error(st.session_state.api_results["error"])
                else:
                    st.json(st.session_state.api_results)
                    
                    # Convert to DataFrame if it's a list
                    if isinstance(st.session_state.api_results, list):
                        try:
                            df = pd.DataFrame(st.session_state.api_results)
                            st.dataframe(df)
                        except:
                            pass
            else:
                st.info("No results yet. Click 'Query REST API' to get data.")
        
        with col2:
            st.subheader("🔗 MCP + Gemini Response")
            if st.session_state.mcp_results:
                st.markdown(st.session_state.mcp_results)
            else:
                st.info("No results yet. Click 'Query MCP + Gemini' to get insights.")
    
    with tab2:
        st.header("📊 Performance & Feature Comparison")
        
        # Comparison table
        comparison_data = {
            "Aspect": [
                "Response Time",
                "Data Format",
                "Natural Language Understanding",
                "Flexibility",
                "Caching",
                "Error Handling",
                "Documentation",
                "Integration Complexity"
            ],
            "REST API": [
                "Fast (< 100ms)",
                "Structured JSON",
                "No",
                "Limited to predefined endpoints",
                "Standard HTTP caching",
                "HTTP status codes",
                "OpenAPI/Swagger",
                "Simple HTTP requests"
            ],
            "MCP + Gemini": [
                "Slower (LLM processing)",
                "Natural language + structured data",
                "Yes",
                "Highly flexible queries",
                "Model-specific caching",
                "Natural language error explanations",
                "Tool descriptions",
                "Requires MCP client integration"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Metrics visualization
        st.subheader("Sample Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("REST API Avg Response", "85ms", "-15ms")
        
        with col2:
            st.metric("MCP Avg Response", "2.3s", "+0.3s")
        
        with col3:
            st.metric("REST API Success Rate", "99.8%", "0.1%")
        
        with col4:
            st.metric("MCP Query Understanding", "94%", "2%")
    
    with tab3:
        st.header("📋 API Documentation")
        
        # REST API Documentation
        st.subheader("🌐 REST API Endpoints")
        
        endpoints = [
            {"Method": "GET", "Endpoint": "/users", "Description": "Get all users with pagination"},
            {"Method": "GET", "Endpoint": "/users/{user_id}", "Description": "Get specific user"},
            {"Method": "GET", "Endpoint": "/users/{user_id}/behavior", "Description": "Get user behavior summary"},
            {"Method": "GET", "Endpoint": "/products", "Description": "Get all products"},
            {"Method": "GET", "Endpoint": "/products/{product_id}/analytics", "Description": "Get product analytics"},
            {"Method": "GET", "Endpoint": "/sessions", "Description": "Get user sessions"},
            {"Method": "GET", "Endpoint": "/purchases", "Description": "Get purchase data"},
            {"Method": "GET", "Endpoint": "/analytics/top-products", "Description": "Get top products by revenue"},
            {"Method": "GET", "Endpoint": "/analytics/device-usage", "Description": "Get device usage statistics"}
        ]
        
        st.dataframe(pd.DataFrame(endpoints), use_container_width=True)
        
        st.info("💡 Full interactive documentation available at: http://localhost:8000/docs")
        
        # MCP Documentation
        st.subheader("🔗 MCP Tools Available")
        
        mcp_tools = [
            {"Tool": "get_user_info", "Description": "Get user information by ID or email"},
            {"Tool": "get_user_behavior_summary", "Description": "Get comprehensive user behavior analysis"},
            {"Tool": "search_products", "Description": "Search products with various filters"},
            {"Tool": "get_product_analytics", "Description": "Get detailed product performance metrics"},
            {"Tool": "get_top_products", "Description": "Get top products by different metrics"},
            {"Tool": "analyze_user_sessions", "Description": "Analyze user session patterns"},
            {"Tool": "get_purchase_patterns", "Description": "Analyze purchase behavior patterns"},
            {"Tool": "query_database", "Description": "Natural language database queries"}
        ]
        
        st.dataframe(pd.DataFrame(mcp_tools), use_container_width=True)
        
        # Example queries
        st.subheader("Example Natural Language Queries for MCP")
        
        example_queries = [
            "Show me the purchasing behavior of user 5",
            "What are the top 10 products by revenue in the Electronics category?",
            "How do users behave differently on mobile vs desktop?",
            "Which products have the highest conversion rates?",
            "What's the average session duration for premium users?",
            "Show me purchase patterns for users aged 25-35",
            "Which payment methods are most popular?",
            "What's the correlation between product ratings and sales?"
        ]
        
        for i, query in enumerate(example_queries, 1):
            st.code(f"{i}. {query}")

if __name__ == "__main__":
    main()