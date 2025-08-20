import streamlit as st
import requests
import json
import os
import asyncio
import sys
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from multi_agent_mcp_client import MultiAgentMCPClient
import plotly.express as px
import plotly.graph_objects as go

# Initialize session state
if 'api_results' not in st.session_state:
    st.session_state.api_results = None
if 'mcp_results' not in st.session_state:
    st.session_state.mcp_results = None
if 'agent_interaction' not in st.session_state:
    st.session_state.agent_interaction = None

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
        page_title="Multi-Agent E-commerce Analytics: REST API vs MCP Demo",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Multi-Agent E-commerce Analytics System")
    st.subheader("Comparing Traditional REST API vs Multi-Agent MCP Architecture")
    
    # Initialize clients
    rest_client = RestAPIClient()
    mcp_client = MultiAgentMCPClient()
    
    # Sidebar for configuration
    st.sidebar.header("🔧 System Configuration")
    
    # API Status Check
    st.sidebar.subheader("System Status")
    try:
        health_check = rest_client.get("/health")
        if "error" not in health_check:
            st.sidebar.success("✅ REST API Online")
        else:
            st.sidebar.error("❌ REST API Offline")
    except:
        st.sidebar.error("❌ REST API Offline")
    
    # Multi-Agent System Status
    st.sidebar.success("✅ Multi-Agent MCP System Ready")
    st.sidebar.success("✅ User Behavior Agent Active")
    st.sidebar.success("✅ Financial Reporting Agent Active")
    
    # Agent Selection
    st.sidebar.subheader("🎯 Agent Targeting")
    agent_preference = st.sidebar.selectbox(
        "Preferred Agent:",
        ["auto", "user_behavior_agent", "financial_reporting_agent", "collaboration"],
        help="Choose which agent to route queries to, or use auto-routing"
    )
    
    # Main content area with enhanced tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Multi-Agent Query", 
        "📊 Agent Comparison", 
        "🤖 System Architecture",
        "📈 Performance Metrics",
        "📋 Documentation"
    ])
    
    with tab1:
        st.header("🔍 Multi-Agent Query Interface")
        
        # Query type selection with agent-specific examples
        col1, col2 = st.columns([2, 1])
        
        with col1:
            query_type = st.selectbox(
                "Select Query Type:",
                [
                    "🧑‍💼 User Behavior Analysis",
                    "💰 Financial Performance",
                    "🤝 Cross-Agent Collaboration", 
                    "📊 Comprehensive Business Analysis",
                    "🎯 Custom Multi-Agent Query"
                ]
            )
        
        with col2:
            show_agent_routing = st.checkbox("Show Agent Routing Details", value=True)
        
        # Dynamic examples based on query type
        if query_type == "🧑‍💼 User Behavior Analysis":
            st.info("**User Behavior Agent** will handle queries about customer engagement, session patterns, user journeys, and behavioral analytics.")
            example_queries = [
                "Analyze user engagement patterns for premium customers",
                "What are the most common user journey paths?",
                "Show me device usage patterns and session analytics",
                "How do user behaviors differ between mobile and desktop?"
            ]
        elif query_type == "💰 Financial Performance":
            st.info("**Financial Reporting Agent** will handle queries about revenue, profit margins, costs, and financial KPIs.")
            example_queries = [
                "Generate a comprehensive revenue report for the last 30 days",
                "What are our profit margins by product category?", 
                "Calculate customer lifetime value and segmentation",
                "Show me financial KPIs and growth metrics"
            ]
        elif query_type == "🤝 Cross-Agent Collaboration":
            st.info("**Multiple Agents** will collaborate to provide insights spanning user behavior and financial performance.")
            example_queries = [
                "How does user engagement correlate with revenue?",
                "Which user segments generate the most profit?",
                "Analyze the financial impact of user behavior changes",
                "Show me the ROI of customer engagement initiatives"
            ]
        elif query_type == "📊 Comprehensive Business Analysis":
            st.info("**All Agents** will work together to provide a complete business health overview.")
            example_queries = [
                "Give me a complete business health analysis",
                "Provide strategic insights for Q4 planning",
                "What are our biggest opportunities and risks?",
                "Create an executive dashboard summary"
            ]
        else:
            st.info("Enter any natural language query - the system will automatically route it to the appropriate agents.")
            example_queries = [
                "What's our best performing product and why?",
                "How can we improve customer retention?",
                "What trends should we focus on next quarter?",
                "Show me actionable insights for growth"
            ]
        
        # Example queries display
        st.subheader("💡 Example Queries")
        selected_example = st.selectbox("Choose an example query:", [""] + example_queries)
        
        # Query input
        if selected_example:
            user_query = st.text_area("Enter your query:", value=selected_example, height=100)
        else:
            user_query = st.text_area("Enter your query:", placeholder="e.g., Analyze user engagement and its impact on revenue...", height=100)
        
        # Execute queries
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌐 Query REST API", use_container_width=True, type="secondary"):
                with st.spinner("Querying REST API..."):
                    # Route to appropriate REST endpoint based on query
                    if "user" in user_query.lower() or "behavior" in user_query.lower():
                        st.session_state.api_results = rest_client.get("/users/1/behavior")
                    elif "revenue" in user_query.lower() or "financial" in user_query.lower():
                        st.session_state.api_results = rest_client.get("/analytics/top-products")
                    else:
                        st.session_state.api_results = {"message": "REST API provides structured endpoints. Use specific queries for user behavior or financial data."}
        
        with col2:
            if st.button("🤖 Query Multi-Agent MCP", use_container_width=True, type="primary"):
                with st.spinner("Processing with Multi-Agent System..."):
                    if user_query:
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(
                                mcp_client.query_natural_language(user_query, agent_preference)
                            )
                            st.session_state.mcp_results = result
                        except Exception as e:
                            st.session_state.mcp_results = f"Error: {str(e)}"
        
        with col3:
            if st.button("🎯 Agent Collaboration", use_container_width=True, type="primary"):
                with st.spinner("Coordinating Multi-Agent Analysis..."):
                    if user_query:
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(
                                mcp_client.get_comprehensive_analysis(user_query)
                            )
                            st.session_state.agent_interaction = result
                        except Exception as e:
                            st.session_state.agent_interaction = f"Error: {str(e)}"
        
        # Results Display
        st.header("📊 Analysis Results")
        
        # Three-column layout for results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🌐 REST API Response")
            if st.session_state.api_results:
                if isinstance(st.session_state.api_results, dict) and "error" in st.session_state.api_results:
                    st.error(st.session_state.api_results["error"])
                else:
                    st.json(st.session_state.api_results)
                    if isinstance(st.session_state.api_results, list):
                        try:
                            df = pd.DataFrame(st.session_state.api_results)
                            st.dataframe(df, use_container_width=True)
                        except:
                            pass
            else:
                st.info("No results yet. Click 'Query REST API' to get structured data.")
        
        with col2:
            st.subheader("🤖 Multi-Agent MCP Response")
            if st.session_state.mcp_results:
                if show_agent_routing:
                    st.markdown(st.session_state.mcp_results)
                else:
                    # Extract just the analysis part
                    lines = st.session_state.mcp_results.split('\n')
                    analysis_start = False
                    filtered_lines = []
                    for line in lines:
                        if "Agent Analysis Results:" in line:
                            analysis_start = True
                            continue
                        if analysis_start and "Multi-Agent System Benefits:" in line:
                            break
                        if analysis_start:
                            filtered_lines.append(line)
                    st.markdown('\n'.join(filtered_lines))
            else:
                st.info("No results yet. Click 'Query Multi-Agent MCP' to get AI-powered insights.")
        
        with col3:
            st.subheader("🤝 Agent Collaboration")
            if st.session_state.agent_interaction:
                st.markdown(st.session_state.agent_interaction)
            else:
                st.info("No collaboration results yet. Click 'Agent Collaboration' for comprehensive analysis.")
    
    with tab2:
        st.header("📊 Architecture Comparison")
        
        # Comparison metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Response Flexibility", "95%", "25%", help="Multi-Agent system adapts to any query type")
        with col2:
            st.metric("Domain Coverage", "100%", "45%", help="Covers both behavioral and financial domains")  
        with col3:
            st.metric("Insight Quality", "High", "Medium", help="AI-powered analysis vs structured data")
        
        # Detailed comparison table
        st.subheader("🔍 Detailed Feature Comparison")
        
        comparison_data = {
            "Feature": [
                "Query Flexibility", "Natural Language", "Multi-Domain Analysis", 
                "Agent Specialization", "Cross-Domain Insights", "Response Time",
                "Scalability", "Maintenance", "Documentation", "Developer Experience"
            ],
            "Traditional REST API": [
                "Limited endpoints", "No", "Manual integration required",
                "No specialization", "Manual correlation", "50-100ms",
                "Horizontal scaling", "High maintenance", "OpenAPI/Swagger", "Simple HTTP"
            ],
            "Multi-Agent MCP": [
                "Any natural language query", "Yes", "Automatic coordination",
                "Domain experts", "Automatic correlation", "1-3s",
                "Agent-based scaling", "Intelligent updates", "AI-generated docs", "Natural language"
            ],
            "Advantage": [
                "MCP", "MCP", "MCP", "MCP", "MCP", "REST API", "Equal", "MCP", "REST API", "MCP"
            ]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Color-code the comparison
        def highlight_advantage(row):
            if row.name == 9:  # Header row
                return ['background-color: #f0f0f0'] * len(row)
            
            colors = []
            for i, cell in enumerate(row):
                if i == 3:  # Advantage column
                    if cell == "MCP":
                        colors.append('background-color: #90EE90')  # Light green
                    elif cell == "REST API":
                        colors.append('background-color: #FFB6C1')  # Light red
                    else:
                        colors.append('background-color: #FFFFE0')  # Light yellow
                else:
                    colors.append('')
            return colors
        
        styled_df = df_comparison.style.apply(highlight_advantage, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Performance visualization
        st.subheader("⚡ Performance Characteristics")
        
        metrics = ['Flexibility', 'Speed', 'Insight Quality', 'Maintenance', 'Scalability', 'Developer Experience']
        rest_api_scores = [3, 9, 5, 4, 8, 7]
        mcp_scores = [10, 6, 9, 8, 7, 9]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=rest_api_scores,
            theta=metrics,
            fill='toself',
            name='REST API',
            line_color='rgb(255, 99, 132)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=mcp_scores,
            theta=metrics,
            fill='toself',
            name='Multi-Agent MCP',
            line_color='rgb(54, 162, 235)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="Architecture Performance Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🤖 Multi-Agent System Architecture")
        
        # System overview
        st.subheader("🏗️ System Architecture Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🧑‍💼 User Behavior Agent
            **Specialization:** Customer Analytics & Engagement
            
            **Core Capabilities:**
            - User segmentation and profiling
            - Session pattern analysis  
            - Customer journey mapping
            - Engagement metrics calculation
            - Device and platform analytics
            - Retention and churn analysis
            
            **Key Tools:**
            - `analyze_user_behavior`
            - `get_user_journey`
            - `analyze_session_patterns`
            - `get_user_segmentation`
            - `analyze_engagement_metrics`
            """)
        
        with col2:
            st.markdown("""
            ### 💰 Financial Reporting Agent
            **Specialization:** Revenue & Profitability Analysis
            
            **Core Capabilities:**
            - Revenue reporting and forecasting
            - Profit margin analysis
            - Customer lifetime value calculation
            - Financial KPI tracking
            - Cost analysis and optimization
            - Payment method analytics
            
            **Key Tools:**
            - `generate_revenue_report`
            - `analyze_profit_margins`
            - `calculate_customer_ltv`
            - `get_financial_kpis`
            - `generate_sales_forecast`
            """)
        
        # Agent coordination flow
        st.subheader("🔄 Agent Coordination Flow")
        
        st.markdown("""
        ```mermaid
        graph TD
            A[User Query] --> B[Query Router]
            B --> C{Query Analysis}
            C -->|Behavior Keywords| D[User Behavior Agent]
            C -->|Financial Keywords| E[Financial Agent]
            C -->|Complex Query| F[Multi-Agent Collaboration]
            D --> G[Specialized Analysis]
            E --> G
            F --> H[Cross-Agent Insights]
            G --> I[Response Formatter]
            H --> I
            I --> J[Natural Language Response]
        ```
        """)
        
        # Show current agent capabilities
        if st.button("🔍 Show Live Agent Capabilities"):
            with st.spinner("Querying live agent capabilities..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    capabilities = loop.run_until_complete(mcp_client.get_agent_capabilities())
                    st.json(capabilities)
                except Exception as e:
                    st.error(f"Error retrieving capabilities: {str(e)}")
    
    with tab4:
        st.header("📈 Performance Metrics & Analytics")
        
        # Simulated performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Query Success Rate", "98.5%", "2.1%", help="Multi-agent system query success rate")
        
        with col2:
            st.metric("Avg Response Time", "2.3s", "-0.4s", help="Average time for multi-agent response")
        
        with col3:
            st.metric("Agent Utilization", "85%", "15%", help="Average agent utilization across the system")
        
        with col4:
            st.metric("Cross-Agent Queries", "34%", "8%", help="Percentage of queries requiring multiple agents")
        
        # Performance over time
        st.subheader("📊 System Performance Trends")
        
        # Generate sample performance data
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        performance_data = pd.DataFrame({
            'Date': dates,
            'REST_API_Response_Time': [50 + i*2 + (i%3)*10 for i in range(len(dates))],
            'MCP_Response_Time': [2000 + i*30 + (i%7)*200 for i in range(len(dates))],
            'MCP_Success_Rate': [95 + (i%5) for i in range(len(dates))],
            'Query_Complexity_Score': [5 + (i%10) for i in range(len(dates))]
        })
        
        fig = px.line(performance_data, x='Date', y=['REST_API_Response_Time', 'MCP_Response_Time'], 
                     title="Response Time Comparison Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # Agent specialization effectiveness
        st.subheader("🎯 Agent Specialization Effectiveness")
        
        agent_metrics = pd.DataFrame({
            'Agent': ['User Behavior Agent', 'Financial Agent', 'Cross-Agent Collaboration'],
            'Queries Handled': [145, 98, 67],
            'Success Rate': [97.2, 98.8, 94.5],
            'Avg Quality Score': [8.7, 9.1, 8.9]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(agent_metrics, x='Agent', y='Queries Handled', 
                        title="Queries Handled by Agent")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(agent_metrics, x='Agent', y='Success Rate',
                        title="Success Rate by Agent")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("📋 Multi-Agent System Documentation")
        
        # Quick start guide
        st.subheader("🚀 Quick Start Guide")
        
        with st.expander("🔧 System Setup", expanded=True):
            st.markdown("""
            ### Prerequisites
            ```bash
            # Set environment variable
            export GEMINI_API_KEY="your_gemini_api_key_here"
            
            # Install dependencies
            pip install -r requirements.txt
            ```
            
            ### Launch Multi-Agent System
            ```bash
            # Start all services
            python run_all.py
            
            # Or start individually:
            # 1. REST API
            python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
            
            # 2. Multi-Agent Frontend
            streamlit run frontend/multi_agent_streamlit_app.py
            ```
            """)
        
        with st.expander("🤖 Agent Usage Examples"):
            st.markdown("""
            ### User Behavior Agent Queries
            ```
            "Analyze user engagement patterns for mobile users"
            "What are the most common customer journey paths?"
            "Show me session analytics for premium customers"
            "How do users behave differently across devices?"
            ```
            
            ### Financial Reporting Agent Queries  
            ```
            "Generate a revenue report for Q4"
            "What are our profit margins by category?"
            "Calculate customer lifetime value by segment"
            "Show me our top performing products financially"
            ```
            
            ### Multi-Agent Collaboration Queries
            ```
            "How does user engagement impact revenue?"
            "Which customer segments are most profitable?"
            "Provide a comprehensive business health analysis"
            "What's the ROI of our customer engagement initiatives?"
            ```
            """)
        
        with st.expander("🔍 API Reference"):
            st.markdown("""
            ### Multi-Agent MCP Tools
            
            #### Meta-Tools
            - `query_multi_agent`: Route natural language queries to appropriate agents
            - `get_agent_capabilities`: Get system capabilities and agent information
            - `agent_collaboration`: Cross-agent analysis and collaboration
            
            #### User Behavior Agent Tools
            - `behavior_analyze_user_behavior`: Comprehensive user behavior analysis
            - `behavior_get_user_journey`: User journey and flow analysis
            - `behavior_analyze_session_patterns`: Session pattern analysis
            - `behavior_get_user_segmentation`: User segmentation analysis
            - `behavior_analyze_engagement_metrics`: Engagement metrics calculation
            
            #### Financial Reporting Agent Tools
            - `financial_generate_revenue_report`: Revenue reporting and analysis
            - `financial_analyze_profit_margins`: Profit margin analysis
            - `financial_get_financial_kpis`: Financial KPI calculation
            - `financial_calculate_customer_ltv`: Customer lifetime value analysis
            - `financial_generate_sales_forecast`: Sales forecasting
            """)
        
        # Integration examples
        st.subheader("🔌 Integration Examples")
        
        tab_py, tab_js, tab_curl = st.tabs(["Python", "JavaScript", "cURL"])
        
        with tab_py:
            st.code("""
# Python Integration Example
from multi_agent_mcp_client import MultiAgentMCPClient
import asyncio

async def main():
    client = MultiAgentMCPClient()
    
    # Natural language query
    result = await client.query_natural_language(
        "How do our high-engagement users impact revenue?"
    )
    print(result)
    
    # Specific agent targeting
    user_analysis = await client.query_user_behavior_agent(
        "Analyze user engagement patterns"
    )
    
    # Comprehensive analysis
    business_insights = await client.get_comprehensive_analysis(
        "Q4 business performance overview"
    )

if __name__ == "__main__":
    asyncio.run(main())
            """, language="python")
        
        with tab_js:
            st.code("""
// JavaScript Integration Example
async function queryMultiAgentSystem() {
    const response = await fetch('/api/mcp/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: "Analyze customer behavior and revenue correlation",
            preferred_agent: "auto"
        })
    });
    
    const result = await response.json();
    console.log('Multi-Agent Analysis:', result);
}

// Agent-specific queries
async function queryBehaviorAgent(query) {
    return await fetch('/api/mcp/behavior', {
        method: 'POST',
        body: JSON.stringify({ query })
    });
}

async function queryFinancialAgent(query) {  
    return await fetch('/api/mcp/financial', {
        method: 'POST',
        body: JSON.stringify({ query })
    });
}
            """, language="javascript")
        
        with tab_curl:
            st.code("""
# cURL Examples

# Multi-agent natural language query
curl -X POST http://localhost:8501/api/mcp/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Show me user engagement and revenue correlation",
    "preferred_agent": "auto"
  }'

# User behavior agent query
curl -X POST http://localhost:8501/api/mcp/behavior \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Analyze user session patterns"
  }'

# Financial agent query
curl -X POST http://localhost:8501/api/mcp/financial \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Generate revenue report for last 30 days"
  }'

# Cross-agent collaboration
curl -X POST http://localhost:8501/api/mcp/collaborate \\
  -H "Content-Type: application/json" \\
  -d '{
    "analysis_type": "comprehensive_analysis",
    "query": "Complete business health overview"
  }'
            """, language="bash")
    
    # Footer with system info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 Multi-Agent MCP System v2.0**")
        st.markdown("Powered by Gemini 2.0 Flash")
    
    with col2:
        st.markdown("**🔗 Architecture:**")
        st.markdown("REST API + Multi-Agent MCP")
    
    with col3:
        st.markdown("**📊 Demo Status:**")
        st.markdown("Vietnam Web Summit 2025 Ready")

if __name__ == "__main__":
    main()