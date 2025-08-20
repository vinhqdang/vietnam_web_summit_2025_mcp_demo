#!/usr/bin/env python3
"""
MCP Server for E-commerce User Behavior Database
Provides natural language interface to query user behavior data
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import sqlite3
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
from sqlalchemy import func, desc, and_, or_

class EcommerceMCPServer:
    def __init__(self):
        self.server = Server("ecommerce-behavior-server")
        self.db_path = "ecommerce_behavior.db"
        self.setup_tools()
        
    def setup_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools for querying e-commerce data"""
            return [
                types.Tool(
                    name="get_user_info",
                    description="Get user information by user ID or email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID to lookup"
                            },
                            "email": {
                                "type": "string",
                                "description": "User email to lookup"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_user_behavior_summary",
                    description="Get comprehensive behavior summary for a user including purchase history, session data, and preferences",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID to get behavior summary for"
                            }
                        },
                        "required": ["user_id"]
                    }
                ),
                types.Tool(
                    name="search_products",
                    description="Search products by name, category, brand, or price range",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Product name to search for"
                            },
                            "category": {
                                "type": "string",
                                "description": "Product category to filter by"
                            },
                            "brand": {
                                "type": "string",
                                "description": "Product brand to filter by"
                            },
                            "min_price": {
                                "type": "number",
                                "description": "Minimum price filter"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price filter"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_product_analytics",
                    description="Get detailed analytics for a product including views, purchases, revenue, and reviews",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "integer",
                                "description": "Product ID to get analytics for"
                            }
                        },
                        "required": ["product_id"]
                    }
                ),
                types.Tool(
                    name="get_top_products",
                    description="Get top products by various metrics (revenue, views, purchases, rating)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric": {
                                "type": "string",
                                "enum": ["revenue", "views", "purchases", "rating"],
                                "description": "Metric to rank products by",
                                "default": "revenue"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top products to return",
                                "default": 10
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by product category"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="analyze_user_sessions",
                    description="Analyze user session patterns including device usage, session duration, and activity patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID to analyze sessions for"
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "Number of days back to analyze",
                                "default": 30
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_purchase_patterns",
                    description="Analyze purchase patterns and trends for users or products",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID to analyze purchase patterns for"
                            },
                            "product_id": {
                                "type": "integer",
                                "description": "Product ID to analyze purchase patterns for"
                            },
                            "category": {
                                "type": "string",
                                "description": "Product category to analyze"
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "Number of days back to analyze",
                                "default": 30
                            }
                        }
                    }
                ),
                types.Tool(
                    name="query_database",
                    description="Execute custom SQL-like queries on the e-commerce database with natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query_description": {
                                "type": "string",
                                "description": "Natural language description of what you want to query"
                            }
                        },
                        "required": ["query_description"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_user_info":
                    return await self.get_user_info(arguments)
                elif name == "get_user_behavior_summary":
                    return await self.get_user_behavior_summary(arguments)
                elif name == "search_products":
                    return await self.search_products(arguments)
                elif name == "get_product_analytics":
                    return await self.get_product_analytics(arguments)
                elif name == "get_top_products":
                    return await self.get_top_products(arguments)
                elif name == "analyze_user_sessions":
                    return await self.analyze_user_sessions(arguments)
                elif name == "get_purchase_patterns":
                    return await self.get_purchase_patterns(arguments)
                elif name == "query_database":
                    return await self.query_database(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def get_user_info(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get user information"""
        db = SessionLocal()
        try:
            user = None
            if "user_id" in args:
                user = db.query(User).filter(User.id == args["user_id"]).first()
            elif "email" in args:
                user = db.query(User).filter(User.email == args["email"]).first()
            
            if not user:
                return [types.TextContent(type="text", text="User not found")]
            
            user_info = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "age": user.age,
                "gender": user.gender,
                "location": user.location,
                "registration_date": user.registration_date.isoformat(),
                "is_premium": user.is_premium
            }
            
            return [types.TextContent(type="text", text=json.dumps(user_info, indent=2))]
        finally:
            db.close()

    async def get_user_behavior_summary(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get comprehensive user behavior summary"""
        db = SessionLocal()
        try:
            user_id = args["user_id"]
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return [types.TextContent(type="text", text="User not found")]
            
            # Get session stats
            session_stats = db.query(
                func.count(UserSession.id).label('total_sessions'),
                func.avg(UserSession.session_duration_minutes).label('avg_duration'),
                func.sum(UserSession.pages_viewed).label('total_pages')
            ).filter(UserSession.user_id == user_id).first()
            
            # Get purchase stats
            purchase_stats = db.query(
                func.count(Purchase.id).label('total_purchases'),
                func.sum(Purchase.total_amount).label('total_spent')
            ).filter(Purchase.user_id == user_id).first()
            
            # Get favorite category
            favorite_category = db.query(
                Product.category,
                func.count(Purchase.id).label('purchase_count')
            ).join(Purchase, Product.id == Purchase.product_id)\
             .filter(Purchase.user_id == user_id)\
             .group_by(Product.category)\
             .order_by(desc('purchase_count')).first()
            
            # Get device usage
            device_usage = db.query(
                UserSession.device_type,
                func.count(UserSession.id).label('count')
            ).filter(UserSession.user_id == user_id)\
             .group_by(UserSession.device_type).all()
            
            summary = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "is_premium": user.is_premium
                },
                "session_activity": {
                    "total_sessions": session_stats.total_sessions or 0,
                    "avg_session_duration_minutes": float(session_stats.avg_duration or 0),
                    "total_pages_viewed": session_stats.total_pages or 0
                },
                "purchase_behavior": {
                    "total_purchases": purchase_stats.total_purchases or 0,
                    "total_spent": float(purchase_stats.total_spent or 0),
                    "favorite_category": favorite_category.category if favorite_category else "None"
                },
                "device_preferences": {
                    device.device_type: device.count for device in device_usage
                }
            }
            
            return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]
        finally:
            db.close()

    async def search_products(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Search products with various filters"""
        db = SessionLocal()
        try:
            query = db.query(Product)
            
            if "name" in args:
                query = query.filter(Product.name.contains(args["name"]))
            if "category" in args:
                query = query.filter(Product.category == args["category"])
            if "brand" in args:
                query = query.filter(Product.brand == args["brand"])
            if "min_price" in args:
                query = query.filter(Product.price >= args["min_price"])
            if "max_price" in args:
                query = query.filter(Product.price <= args["max_price"])
            
            limit = args.get("limit", 10)
            products = query.limit(limit).all()
            
            results = []
            for product in products:
                results.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "brand": product.brand,
                    "price": product.price,
                    "rating": product.rating,
                    "stock_quantity": product.stock_quantity
                })
            
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        finally:
            db.close()

    async def get_product_analytics(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed product analytics"""
        db = SessionLocal()
        try:
            product_id = args["product_id"]
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return [types.TextContent(type="text", text="Product not found")]
            
            # Get view stats
            total_views = db.query(func.count(PageView.id))\
                           .filter(PageView.product_id == product_id).scalar() or 0
            
            # Get purchase stats
            purchase_stats = db.query(
                func.count(Purchase.id).label('total_purchases'),
                func.sum(Purchase.total_amount).label('total_revenue'),
                func.sum(Purchase.quantity).label('total_quantity')
            ).filter(Purchase.product_id == product_id).first()
            
            # Get review stats
            review_stats = db.query(
                func.count(Review.id).label('total_reviews'),
                func.avg(Review.rating).label('avg_rating')
            ).filter(Review.product_id == product_id).first()
            
            analytics = {
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "brand": product.brand,
                    "price": product.price
                },
                "engagement": {
                    "total_views": total_views,
                    "total_purchases": purchase_stats.total_purchases or 0,
                    "total_quantity_sold": purchase_stats.total_quantity or 0,
                    "conversion_rate": round((purchase_stats.total_purchases or 0) / max(total_views, 1) * 100, 2)
                },
                "revenue": {
                    "total_revenue": float(purchase_stats.total_revenue or 0),
                    "avg_order_value": float(purchase_stats.total_revenue or 0) / max(purchase_stats.total_purchases or 1, 1)
                },
                "reviews": {
                    "total_reviews": review_stats.total_reviews or 0,
                    "average_rating": float(review_stats.avg_rating or 0)
                }
            }
            
            return [types.TextContent(type="text", text=json.dumps(analytics, indent=2))]
        finally:
            db.close()

    async def get_top_products(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get top products by specified metric"""
        db = SessionLocal()
        try:
            metric = args.get("metric", "revenue")
            limit = args.get("limit", 10)
            category = args.get("category")
            
            # Base query
            query = db.query(Product)
            if category:
                query = query.filter(Product.category == category)
            
            products = query.all()
            results = []
            
            for product in products:
                # Calculate metrics for each product
                views = db.query(func.count(PageView.id))\
                         .filter(PageView.product_id == product.id).scalar() or 0
                
                purchase_stats = db.query(
                    func.count(Purchase.id).label('purchases'),
                    func.sum(Purchase.total_amount).label('revenue')
                ).filter(Purchase.product_id == product.id).first()
                
                purchases = purchase_stats.purchases or 0
                revenue = float(purchase_stats.revenue or 0)
                rating = product.rating
                
                results.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "brand": product.brand,
                    "price": product.price,
                    "views": views,
                    "purchases": purchases,
                    "revenue": revenue,
                    "rating": rating
                })
            
            # Sort by metric
            if metric == "revenue":
                results.sort(key=lambda x: x["revenue"], reverse=True)
            elif metric == "views":
                results.sort(key=lambda x: x["views"], reverse=True)
            elif metric == "purchases":
                results.sort(key=lambda x: x["purchases"], reverse=True)
            elif metric == "rating":
                results.sort(key=lambda x: x["rating"], reverse=True)
            
            return [types.TextContent(type="text", text=json.dumps(results[:limit], indent=2))]
        finally:
            db.close()

    async def analyze_user_sessions(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Analyze user session patterns"""
        db = SessionLocal()
        try:
            user_id = args.get("user_id")
            days_back = args.get("days_back", 30)
            
            query = db.query(UserSession)
            if user_id:
                query = query.filter(UserSession.user_id == user_id)
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(UserSession.session_start >= cutoff_date)
            
            sessions = query.all()
            
            if not sessions:
                return [types.TextContent(type="text", text="No sessions found for the specified criteria")]
            
            # Analyze patterns
            total_sessions = len(sessions)
            total_duration = sum(s.session_duration_minutes or 0 for s in sessions)
            avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
            
            device_stats = {}
            browser_stats = {}
            
            for session in sessions:
                device_stats[session.device_type] = device_stats.get(session.device_type, 0) + 1
                browser_stats[session.browser] = browser_stats.get(session.browser, 0) + 1
            
            analysis = {
                "summary": {
                    "total_sessions": total_sessions,
                    "avg_session_duration_minutes": round(avg_duration, 2),
                    "total_duration_minutes": round(total_duration, 2)
                },
                "device_breakdown": device_stats,
                "browser_breakdown": browser_stats,
                "period_analyzed_days": days_back
            }
            
            if user_id:
                analysis["user_id"] = user_id
            
            return [types.TextContent(type="text", text=json.dumps(analysis, indent=2))]
        finally:
            db.close()

    async def get_purchase_patterns(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Analyze purchase patterns"""
        db = SessionLocal()
        try:
            user_id = args.get("user_id")
            product_id = args.get("product_id")
            category = args.get("category")
            days_back = args.get("days_back", 30)
            
            query = db.query(Purchase)
            
            # Apply filters
            if user_id:
                query = query.filter(Purchase.user_id == user_id)
            if product_id:
                query = query.filter(Purchase.product_id == product_id)
            
            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(Purchase.purchase_date >= cutoff_date)
            
            # Join with Product if category filter is needed
            if category:
                query = query.join(Product).filter(Product.category == category)
            
            purchases = query.all()
            
            if not purchases:
                return [types.TextContent(type="text", text="No purchases found for the specified criteria")]
            
            # Analyze patterns
            total_purchases = len(purchases)
            total_amount = sum(p.total_amount for p in purchases)
            avg_order_value = total_amount / total_purchases if total_purchases > 0 else 0
            
            # Payment method breakdown
            payment_methods = {}
            for purchase in purchases:
                payment_methods[purchase.payment_method] = payment_methods.get(purchase.payment_method, 0) + 1
            
            # Category breakdown (if not filtering by category)
            category_stats = {}
            if not category:
                for purchase in purchases:
                    product = db.query(Product).filter(Product.id == purchase.product_id).first()
                    if product:
                        category_stats[product.category] = category_stats.get(product.category, 0) + 1
            
            analysis = {
                "summary": {
                    "total_purchases": total_purchases,
                    "total_amount": round(total_amount, 2),
                    "average_order_value": round(avg_order_value, 2)
                },
                "payment_method_breakdown": payment_methods,
                "period_analyzed_days": days_back
            }
            
            if category_stats:
                analysis["category_breakdown"] = category_stats
            
            if user_id:
                analysis["user_id"] = user_id
            if product_id:
                analysis["product_id"] = product_id
            if category:
                analysis["category"] = category
            
            return [types.TextContent(type="text", text=json.dumps(analysis, indent=2))]
        finally:
            db.close()

    async def query_database(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle natural language database queries"""
        query_description = args["query_description"].lower()
        
        # This is a simplified natural language processor
        # In a real implementation, you'd use more sophisticated NLP
        
        try:
            if "user" in query_description and "behavior" in query_description:
                # Extract user ID if mentioned
                import re
                user_match = re.search(r'user\s+(\d+)', query_description)
                if user_match:
                    user_id = int(user_match.group(1))
                    return await self.get_user_behavior_summary({"user_id": user_id})
            
            elif "top" in query_description and "product" in query_description:
                metric = "revenue"
                if "view" in query_description:
                    metric = "views"
                elif "purchase" in query_description:
                    metric = "purchases"
                elif "rating" in query_description:
                    metric = "rating"
                
                return await self.get_top_products({"metric": metric, "limit": 10})
            
            elif "search" in query_description and "product" in query_description:
                # Simple product search
                return await self.search_products({"limit": 10})
            
            else:
                return [types.TextContent(
                    type="text", 
                    text="I can help you query user behavior, product analytics, purchase patterns, and session data. Please be more specific about what you'd like to know."
                )]
                
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error processing query: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    server_instance = EcommerceMCPServer()
    
    # Import required for datetime operations
    from datetime import timedelta
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ecommerce-behavior-server",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())