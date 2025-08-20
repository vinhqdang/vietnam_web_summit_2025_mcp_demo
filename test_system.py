#!/usr/bin/env python3
"""
Simple test script to verify the multi-agent MCP system works correctly
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that all components can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test database components
        from backend.database.database import SessionLocal, create_database
        from backend.database.models import User, Product
        print("✅ Database components imported successfully")
        
        # Test API components  
        from backend.api.main import app
        from backend.api import crud, schemas
        print("✅ API components imported successfully")
        
        # Test multi-agent system
        from backend.mcp_server.agents.base_agent import AgentCoordinator
        from backend.mcp_server.agents.user_behavior_agent import UserBehaviorAgent
        from backend.mcp_server.agents.financial_agent import FinancialReportingAgent
        print("✅ Multi-agent system imported successfully")
        
        # Test frontend components
        from frontend.multi_agent_mcp_client import MultiAgentMCPClient
        print("✅ Frontend components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_setup():
    """Test database initialization and sample data"""
    print("\n🗄️ Testing database setup...")
    
    try:
        from backend.database.database import SessionLocal, create_database
        from backend.database.models import User, Product, Purchase
        
        # Create database tables
        create_database()
        print("✅ Database tables created")
        
        # Test database connection
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            product_count = db.query(Product).count()
            purchase_count = db.query(Purchase).count()
            
            print(f"✅ Database connected: {user_count} users, {product_count} products, {purchase_count} purchases")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_multi_agent_system():
    """Test multi-agent system initialization"""
    print("\n🤖 Testing multi-agent system...")
    
    try:
        from backend.mcp_server.agents.base_agent import AgentCoordinator
        from backend.mcp_server.agents.user_behavior_agent import UserBehaviorAgent
        from backend.mcp_server.agents.financial_agent import FinancialReportingAgent
        
        # Initialize coordinator and agents
        coordinator = AgentCoordinator()
        user_agent = UserBehaviorAgent()
        financial_agent = FinancialReportingAgent()
        
        # Register agents
        coordinator.register_agent(user_agent)
        coordinator.register_agent(financial_agent)
        
        print(f"✅ Coordinator initialized with {len(coordinator.agents)} agents")
        print(f"✅ User Behavior Agent: {len(user_agent.get_available_tools())} tools")
        print(f"✅ Financial Agent: {len(financial_agent.get_available_tools())} tools")
        
        # Test query routing
        test_queries = [
            "Analyze user engagement patterns",
            "Generate revenue report", 
            "Show comprehensive business analysis"
        ]
        
        for query in test_queries:
            agents = coordinator.route_query(query)
            print(f"✅ Query '{query[:30]}...' → {len(agents)} agent(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent system error: {e}")
        return False

async def test_mcp_client():
    """Test MCP client functionality"""
    print("\n🔗 Testing MCP client...")
    
    try:
        from frontend.multi_agent_mcp_client import MultiAgentMCPClient
        
        client = MultiAgentMCPClient()
        capabilities = await client.get_agent_capabilities()
        
        print("✅ MCP client initialized successfully")
        print(f"✅ System capabilities: {capabilities['multi_agent_system']['version']}")
        
        # Test a simple query (simulation)
        test_query = "What are our top performing products?"
        result = await client.query_natural_language(test_query)
        
        if "Multi-Agent E-commerce Analytics System" in result:
            print("✅ MCP client query processing works")
            return True
        else:
            print("⚠️ MCP client query returned unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ MCP client error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Multi-Agent MCP System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Component Imports", test_imports),
        ("Database Setup", test_database_setup),
        ("Multi-Agent System", test_multi_agent_system),
        ("MCP Client", lambda: asyncio.run(test_mcp_client()))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-agent system is ready for demo!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())