"""
Financial Reporting Agent - Specialized in financial analysis, revenue reporting, and profit analysis
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


class FinancialReportingAgent(BaseAgent):
    """Agent specialized in financial analysis, revenue reporting, and profitability analysis"""
    
    def __init__(self):
        super().__init__(
            agent_id="financial_reporting_agent",
            name="Financial Analyst",
            description="Specializes in revenue analysis, profit margins, financial reporting, cost analysis, and business performance metrics"
        )
        
        # Register tools
        self.tools = {
            "generate_revenue_report": self._generate_revenue_report,
            "analyze_profit_margins": self._analyze_profit_margins,
            "get_financial_kpis": self._get_financial_kpis,
            "analyze_payment_methods": self._analyze_payment_methods,
            "calculate_customer_ltv": self._calculate_customer_ltv,
            "generate_sales_forecast": self._generate_sales_forecast,
            "analyze_product_profitability": self._analyze_product_profitability,
            "get_cohort_revenue": self._get_cohort_revenue,
            "analyze_discount_impact": self._analyze_discount_impact,
            "generate_financial_summary": self._generate_financial_summary
        }
        
        # Financial assumptions for calculations (in a real system, these would be configurable)
        self.cost_assumptions = {
            "cost_of_goods_sold_percentage": 0.60,  # 60% COGS
            "operational_cost_percentage": 0.25,    # 25% operational costs
            "customer_acquisition_cost": 15.0,      # $15 per customer
            "return_rate": 0.05,                    # 5% return rate
        }
    
    def get_capabilities(self) -> List[str]:
        """Return this agent's capabilities"""
        return [
            AgentCapability.FINANCIAL_ANALYSIS,
            AgentCapability.REVENUE_REPORTING,
            AgentCapability.PROFIT_ANALYSIS,
            AgentCapability.COST_ANALYSIS
        ]
    
    def can_handle_query(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        
        financial_keywords = [
            "revenue", "profit", "financial", "earnings", "income", "sales",
            "money", "cost", "expense", "margin", "roi", "ltv", "lifetime value",
            "financial report", "profit margin", "revenue report", "kpi",
            "payment", "discount", "forecast", "profitability"
        ]
        
        return any(keyword in query_lower for keyword in financial_keywords)
    
    def process_query(self, query: str, db: Session, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process financial analysis related queries"""
        query_lower = query.lower()
        
        try:
            # Route to appropriate analysis based on query content
            if "revenue" in query_lower and "report" in query_lower:
                return self._generate_revenue_report_from_query(query, db)
            elif "profit" in query_lower:
                return self._analyze_profit_from_query(query, db)
            elif "kpi" in query_lower or "financial" in query_lower:
                return self._get_financial_kpis_from_query(query, db)
            elif "payment" in query_lower:
                return self._analyze_payment_methods_from_query(query, db)
            elif "ltv" in query_lower or "lifetime" in query_lower:
                return self._calculate_ltv_from_query(query, db)
            elif "forecast" in query_lower:
                return self._generate_forecast_from_query(query, db)
            elif "discount" in query_lower:
                return self._analyze_discounts_from_query(query, db)
            else:
                # General financial analysis
                return self._generate_financial_summary({}, db)
                
        except Exception as e:
            return {"error": f"Financial Reporting Agent error: {str(e)}"}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return available tools for this agent"""
        return [
            {
                "name": "generate_revenue_report",
                "description": "Generate comprehensive revenue reports with breakdowns",
                "parameters": ["time_period", "granularity", "include_forecasts"]
            },
            {
                "name": "analyze_profit_margins",
                "description": "Analyze profit margins by product, category, or time period",
                "parameters": ["analysis_type", "product_filter", "time_period"]
            },
            {
                "name": "get_financial_kpis",
                "description": "Calculate key financial performance indicators",
                "parameters": ["kpi_set", "time_period", "comparison_period"]
            },
            {
                "name": "analyze_payment_methods",
                "description": "Analyze revenue by payment method and trends",
                "parameters": ["include_trends", "time_period"]
            },
            {
                "name": "calculate_customer_ltv",
                "description": "Calculate customer lifetime value and segmentation",
                "parameters": ["calculation_method", "customer_segment"]
            },
            {
                "name": "generate_sales_forecast",
                "description": "Generate sales and revenue forecasts",
                "parameters": ["forecast_period", "forecast_method", "confidence_level"]
            },
            {
                "name": "analyze_product_profitability",
                "description": "Analyze profitability by product or category",
                "parameters": ["profitability_metric", "product_filter"]
            },
            {
                "name": "get_cohort_revenue",
                "description": "Analyze revenue by customer cohorts",
                "parameters": ["cohort_period", "revenue_metric"]
            },
            {
                "name": "analyze_discount_impact",
                "description": "Analyze the financial impact of discounts and promotions",
                "parameters": ["discount_analysis_type", "time_period"]
            },
            {
                "name": "generate_financial_summary",
                "description": "Generate executive financial summary report",
                "parameters": ["summary_type", "time_period"]
            }
        ]
    
    def _generate_revenue_report(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate comprehensive revenue report"""
        time_period = parameters.get("time_period", 30)
        granularity = parameters.get("granularity", "daily")
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        # Get all purchases in the period
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date).all()
        
        # Calculate basic revenue metrics
        total_revenue = sum(p.total_amount for p in purchases)
        total_orders = len(purchases)
        avg_order_value = total_revenue / max(total_orders, 1)
        
        # Revenue by category
        category_revenue = {}
        for purchase in purchases:
            product = db.query(Product).filter(Product.id == purchase.product_id).first()
            if product:
                category = product.category
                category_revenue[category] = category_revenue.get(category, 0) + purchase.total_amount
        
        # Revenue by payment method
        payment_revenue = {}
        for purchase in purchases:
            method = purchase.payment_method
            payment_revenue[method] = payment_revenue.get(method, 0) + purchase.total_amount
        
        # Revenue over time (simplified daily aggregation)
        daily_revenue = {}
        for purchase in purchases:
            date_key = purchase.purchase_date.strftime("%Y-%m-%d")
            daily_revenue[date_key] = daily_revenue.get(date_key, 0) + purchase.total_amount
        
        # Calculate growth rate (comparing to previous period)
        previous_cutoff = cutoff_date - timedelta(days=time_period)
        previous_purchases = db.query(Purchase).filter(
            and_(Purchase.purchase_date >= previous_cutoff, Purchase.purchase_date < cutoff_date)
        ).all()
        previous_revenue = sum(p.total_amount for p in previous_purchases)
        growth_rate = ((total_revenue - previous_revenue) / max(previous_revenue, 1)) * 100
        
        return {
            "report_period": {
                "days": time_period,
                "start_date": cutoff_date.strftime("%Y-%m-%d"),
                "end_date": datetime.utcnow().strftime("%Y-%m-%d")
            },
            "revenue_summary": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "average_order_value": round(avg_order_value, 2),
                "growth_rate_percent": round(growth_rate, 2)
            },
            "revenue_breakdown": {
                "by_category": {k: round(v, 2) for k, v in category_revenue.items()},
                "by_payment_method": {k: round(v, 2) for k, v in payment_revenue.items()},
                "daily_revenue": {k: round(v, 2) for k, v in daily_revenue.items()}
            },
            "insights": {
                "top_revenue_category": max(category_revenue.items(), key=lambda x: x[1])[0] if category_revenue else None,
                "preferred_payment_method": max(payment_revenue.items(), key=lambda x: x[1])[0] if payment_revenue else None,
                "peak_revenue_day": max(daily_revenue.items(), key=lambda x: x[1])[0] if daily_revenue else None
            }
        }
    
    def _analyze_profit_margins(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze profit margins with cost assumptions"""
        analysis_type = parameters.get("analysis_type", "overall")
        time_period = parameters.get("time_period", 30)
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date).all()
        
        total_revenue = sum(p.total_amount for p in purchases)
        
        # Calculate costs based on assumptions
        cogs = total_revenue * self.cost_assumptions["cost_of_goods_sold_percentage"]
        operational_costs = total_revenue * self.cost_assumptions["operational_cost_percentage"]
        total_costs = cogs + operational_costs
        
        gross_profit = total_revenue - cogs
        net_profit = total_revenue - total_costs
        
        gross_margin = (gross_profit / max(total_revenue, 1)) * 100
        net_margin = (net_profit / max(total_revenue, 1)) * 100
        
        # Profit by category
        category_profit = {}
        for purchase in purchases:
            product = db.query(Product).filter(Product.id == purchase.product_id).first()
            if product:
                category = product.category
                revenue = purchase.total_amount
                category_cogs = revenue * self.cost_assumptions["cost_of_goods_sold_percentage"]
                category_profit[category] = category_profit.get(category, 0) + (revenue - category_cogs)
        
        return {
            "analysis_period_days": time_period,
            "profit_analysis": {
                "total_revenue": round(total_revenue, 2),
                "cost_of_goods_sold": round(cogs, 2),
                "operational_costs": round(operational_costs, 2),
                "gross_profit": round(gross_profit, 2),
                "net_profit": round(net_profit, 2)
            },
            "margin_analysis": {
                "gross_margin_percent": round(gross_margin, 2),
                "net_margin_percent": round(net_margin, 2)
            },
            "profit_by_category": {k: round(v, 2) for k, v in category_profit.items()},
            "cost_assumptions": self.cost_assumptions
        }
    
    def _get_financial_kpis(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Calculate key financial performance indicators"""
        time_period = parameters.get("time_period", 30)
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        # Revenue metrics
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date).all()
        total_revenue = sum(p.total_amount for p in purchases)
        total_orders = len(purchases)
        
        # Customer metrics
        unique_customers = len(set(p.user_id for p in purchases))
        total_customers = db.query(User).count()
        
        # Session metrics
        sessions = db.query(UserSession).filter(UserSession.session_start >= cutoff_date).all()
        total_sessions = len(sessions)
        
        # Calculate KPIs
        aov = total_revenue / max(total_orders, 1)  # Average Order Value
        revenue_per_customer = total_revenue / max(unique_customers, 1)  # Revenue per Customer
        conversion_rate = (unique_customers / max(total_sessions, 1)) * 100 if total_sessions > 0 else 0
        customer_acquisition_rate = (unique_customers / max(total_customers, 1)) * 100
        
        # Financial health indicators
        gross_profit = total_revenue * (1 - self.cost_assumptions["cost_of_goods_sold_percentage"])
        roi = (gross_profit / max(total_revenue * self.cost_assumptions["cost_of_goods_sold_percentage"], 1)) * 100
        
        return {
            "kpi_period_days": time_period,
            "revenue_kpis": {
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(aov, 2),
                "revenue_per_customer": round(revenue_per_customer, 2),
                "total_orders": total_orders
            },
            "customer_kpis": {
                "unique_purchasing_customers": unique_customers,
                "total_registered_customers": total_customers,
                "customer_acquisition_rate": round(customer_acquisition_rate, 2),
                "conversion_rate": round(conversion_rate, 2)
            },
            "profitability_kpis": {
                "gross_profit": round(gross_profit, 2),
                "estimated_roi": round(roi, 2),
                "profit_margin": round((gross_profit / max(total_revenue, 1)) * 100, 2)
            },
            "operational_kpis": {
                "total_sessions": total_sessions,
                "sessions_to_purchase_ratio": round(total_sessions / max(total_orders, 1), 2)
            }
        }
    
    def _analyze_payment_methods(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze revenue and trends by payment method"""
        time_period = parameters.get("time_period", 30)
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date).all()
        
        payment_analysis = {}
        for purchase in purchases:
            method = purchase.payment_method
            if method not in payment_analysis:
                payment_analysis[method] = {
                    "total_revenue": 0,
                    "order_count": 0,
                    "avg_order_value": 0
                }
            
            payment_analysis[method]["total_revenue"] += purchase.total_amount
            payment_analysis[method]["order_count"] += 1
        
        # Calculate averages and percentages
        total_revenue = sum(p.total_amount for p in purchases)
        total_orders = len(purchases)
        
        for method, data in payment_analysis.items():
            data["avg_order_value"] = data["total_revenue"] / max(data["order_count"], 1)
            data["revenue_percentage"] = (data["total_revenue"] / max(total_revenue, 1)) * 100
            data["order_percentage"] = (data["order_count"] / max(total_orders, 1)) * 100
        
        return {
            "analysis_period_days": time_period,
            "payment_method_analysis": {
                method: {
                    "total_revenue": round(data["total_revenue"], 2),
                    "order_count": data["order_count"],
                    "avg_order_value": round(data["avg_order_value"], 2),
                    "revenue_percentage": round(data["revenue_percentage"], 2),
                    "order_percentage": round(data["order_percentage"], 2)
                }
                for method, data in payment_analysis.items()
            },
            "insights": {
                "most_popular_payment": max(payment_analysis.items(), 
                                          key=lambda x: x[1]["order_count"])[0] if payment_analysis else None,
                "highest_revenue_payment": max(payment_analysis.items(), 
                                             key=lambda x: x[1]["total_revenue"])[0] if payment_analysis else None,
                "highest_aov_payment": max(payment_analysis.items(), 
                                         key=lambda x: x[1]["avg_order_value"])[0] if payment_analysis else None
            }
        }
    
    def _calculate_customer_ltv(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Calculate Customer Lifetime Value"""
        calculation_method = parameters.get("calculation_method", "historical")
        
        users = db.query(User).all()
        ltv_data = []
        
        for user in users:
            purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
            
            if purchases:
                total_spent = sum(p.total_amount for p in purchases)
                purchase_count = len(purchases)
                first_purchase = min(p.purchase_date for p in purchases)
                last_purchase = max(p.purchase_date for p in purchases)
                
                # Calculate customer lifespan in days
                lifespan_days = (last_purchase - first_purchase).days + 1
                avg_order_value = total_spent / purchase_count
                purchase_frequency = purchase_count / max(lifespan_days / 30, 1)  # purchases per month
                
                # Simple LTV calculation: AOV × Purchase Frequency × Customer Lifespan (in months)
                ltv = avg_order_value * purchase_frequency * (lifespan_days / 30)
                
                ltv_data.append({
                    "user_id": user.id,
                    "user_name": user.name,
                    "total_spent": round(total_spent, 2),
                    "purchase_count": purchase_count,
                    "avg_order_value": round(avg_order_value, 2),
                    "customer_lifespan_days": lifespan_days,
                    "purchase_frequency_per_month": round(purchase_frequency, 2),
                    "estimated_ltv": round(ltv, 2),
                    "is_premium": user.is_premium
                })
        
        # Calculate aggregate metrics
        if ltv_data:
            avg_ltv = sum(customer["estimated_ltv"] for customer in ltv_data) / len(ltv_data)
            median_ltv = sorted([customer["estimated_ltv"] for customer in ltv_data])[len(ltv_data) // 2]
            
            # Segment by LTV
            high_value = [c for c in ltv_data if c["estimated_ltv"] > avg_ltv * 1.5]
            medium_value = [c for c in ltv_data if avg_ltv * 0.5 <= c["estimated_ltv"] <= avg_ltv * 1.5]
            low_value = [c for c in ltv_data if c["estimated_ltv"] < avg_ltv * 0.5]
        else:
            avg_ltv = median_ltv = 0
            high_value = medium_value = low_value = []
        
        return {
            "calculation_method": calculation_method,
            "ltv_summary": {
                "average_ltv": round(avg_ltv, 2),
                "median_ltv": round(median_ltv, 2),
                "total_customers_analyzed": len(ltv_data)
            },
            "customer_segments": {
                "high_value_customers": len(high_value),
                "medium_value_customers": len(medium_value),
                "low_value_customers": len(low_value)
            },
            "top_customers_by_ltv": sorted(ltv_data, key=lambda x: x["estimated_ltv"], reverse=True)[:10],
            "methodology": {
                "ltv_formula": "AOV × Purchase Frequency × Customer Lifespan (months)",
                "assumptions": "Based on historical purchase data and observed behavior patterns"
            }
        }
    
    def _generate_sales_forecast(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate simple sales forecast based on historical trends"""
        forecast_period = parameters.get("forecast_period", 30)
        
        # Get historical data for trend analysis (last 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date)\
                     .order_by(Purchase.purchase_date).all()
        
        if not purchases:
            return {"error": "Insufficient historical data for forecasting"}
        
        # Simple trend analysis - group by week
        weekly_revenue = {}
        for purchase in purchases:
            week_key = purchase.purchase_date.strftime("%Y-W%U")
            weekly_revenue[week_key] = weekly_revenue.get(week_key, 0) + purchase.total_amount
        
        # Calculate trend (linear approximation)
        weeks = sorted(weekly_revenue.keys())
        revenues = [weekly_revenue[week] for week in weeks]
        
        if len(revenues) >= 2:
            # Simple linear trend
            trend = (revenues[-1] - revenues[0]) / max(len(revenues) - 1, 1)
            avg_weekly_revenue = sum(revenues) / len(revenues)
            
            # Forecast future weeks
            forecast_weeks = forecast_period // 7
            forecast_data = []
            
            for i in range(1, forecast_weeks + 1):
                projected_revenue = avg_weekly_revenue + (trend * i)
                forecast_data.append({
                    "week": i,
                    "projected_revenue": round(max(projected_revenue, 0), 2),
                    "confidence": "medium" if i <= 4 else "low"
                })
            
            total_forecast = sum(item["projected_revenue"] for item in forecast_data)
        else:
            trend = 0
            avg_weekly_revenue = revenues[0] if revenues else 0
            forecast_data = []
            total_forecast = 0
        
        return {
            "forecast_period_days": forecast_period,
            "historical_analysis": {
                "data_period_days": 90,
                "average_weekly_revenue": round(avg_weekly_revenue, 2),
                "trend_per_week": round(trend, 2),
                "total_weeks_analyzed": len(weeks)
            },
            "forecast": {
                "total_projected_revenue": round(total_forecast, 2),
                "weekly_projections": forecast_data
            },
            "methodology": "Linear trend analysis based on 90-day historical data",
            "disclaimer": "Forecasts are estimates based on historical trends and should be used for planning purposes only"
        }
    
    def _analyze_product_profitability(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze profitability by product"""
        time_period = parameters.get("time_period", 30)
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        # Get all products and their sales
        products = db.query(Product).all()
        profitability_data = []
        
        for product in products:
            purchases = db.query(Purchase).filter(
                and_(Purchase.product_id == product.id, Purchase.purchase_date >= cutoff_date)
            ).all()
            
            if purchases:
                total_revenue = sum(p.total_amount for p in purchases)
                units_sold = sum(p.quantity for p in purchases)
                
                # Calculate costs (simplified)
                cogs = total_revenue * self.cost_assumptions["cost_of_goods_sold_percentage"]
                gross_profit = total_revenue - cogs
                profit_margin = (gross_profit / max(total_revenue, 1)) * 100
                
                profitability_data.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "category": product.category,
                    "brand": product.brand,
                    "price": product.price,
                    "units_sold": units_sold,
                    "total_revenue": round(total_revenue, 2),
                    "estimated_cogs": round(cogs, 2),
                    "gross_profit": round(gross_profit, 2),
                    "profit_margin_percent": round(profit_margin, 2),
                    "revenue_per_unit": round(total_revenue / max(units_sold, 1), 2)
                })
        
        # Sort by profitability
        profitability_data.sort(key=lambda x: x["gross_profit"], reverse=True)
        
        return {
            "analysis_period_days": time_period,
            "products_analyzed": len(profitability_data),
            "profitability_ranking": profitability_data,
            "summary": {
                "most_profitable_product": profitability_data[0]["product_name"] if profitability_data else None,
                "highest_margin_product": max(profitability_data, key=lambda x: x["profit_margin_percent"])["product_name"] if profitability_data else None,
                "total_gross_profit": round(sum(p["gross_profit"] for p in profitability_data), 2)
            }
        }
    
    def _generate_financial_summary(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate executive financial summary"""
        time_period = parameters.get("time_period", 30)
        
        # Get comprehensive financial data
        revenue_report = self._generate_revenue_report({"time_period": time_period}, db)
        profit_analysis = self._analyze_profit_margins({"time_period": time_period}, db)
        kpis = self._get_financial_kpis({"time_period": time_period}, db)
        
        return {
            "executive_summary": {
                "report_period_days": time_period,
                "generated_at": datetime.utcnow().isoformat(),
                "key_metrics": {
                    "total_revenue": revenue_report["revenue_summary"]["total_revenue"],
                    "gross_profit": profit_analysis["profit_analysis"]["gross_profit"],
                    "net_profit": profit_analysis["profit_analysis"]["net_profit"],
                    "profit_margin": profit_analysis["margin_analysis"]["gross_margin_percent"],
                    "average_order_value": kpis["revenue_kpis"]["average_order_value"],
                    "conversion_rate": kpis["customer_kpis"]["conversion_rate"]
                }
            },
            "detailed_reports": {
                "revenue_analysis": revenue_report,
                "profitability_analysis": profit_analysis,
                "key_performance_indicators": kpis
            }
        }
    
    # Query processing methods
    def _generate_revenue_report_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Generate revenue report from natural language query"""
        # Extract time period if mentioned
        import re
        period_match = re.search(r'(\d+)\s*(day|week|month)', query.lower())
        time_period = 30  # default
        
        if period_match:
            number = int(period_match.group(1))
            unit = period_match.group(2)
            if unit == "week":
                time_period = number * 7
            elif unit == "month":
                time_period = number * 30
            else:
                time_period = number
        
        return self._generate_revenue_report({"time_period": time_period}, db)
    
    def _analyze_profit_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze profit from natural language query"""
        return self._analyze_profit_margins({}, db)
    
    def _get_financial_kpis_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Get financial KPIs from natural language query"""
        return self._get_financial_kpis({}, db)
    
    def _analyze_payment_methods_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze payment methods from query"""
        return self._analyze_payment_methods({}, db)
    
    def _calculate_ltv_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Calculate LTV from query"""
        return self._calculate_customer_ltv({}, db)
    
    def _generate_forecast_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Generate forecast from query"""
        return self._generate_sales_forecast({}, db)
    
    def _analyze_discounts_from_query(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze discount impact from query"""
        return self._analyze_discount_impact({}, db)
    
    def _analyze_discount_impact(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze the impact of discounts on revenue and profitability"""
        time_period = parameters.get("time_period", 30)
        cutoff_date = datetime.utcnow() - timedelta(days=time_period)
        
        purchases = db.query(Purchase).filter(Purchase.purchase_date >= cutoff_date).all()
        
        discounted_purchases = [p for p in purchases if p.discount_applied > 0]
        full_price_purchases = [p for p in purchases if p.discount_applied == 0]
        
        if not purchases:
            return {"error": "No purchase data available for analysis"}
        
        # Calculate metrics
        total_discount_amount = sum(p.total_amount * p.discount_applied for p in discounted_purchases)
        discounted_revenue = sum(p.total_amount for p in discounted_purchases)
        full_price_revenue = sum(p.total_amount for p in full_price_purchases)
        
        discount_rate = len(discounted_purchases) / len(purchases) * 100
        avg_discount = sum(p.discount_applied for p in discounted_purchases) / max(len(discounted_purchases), 1) * 100
        
        return {
            "analysis_period_days": time_period,
            "discount_analysis": {
                "total_orders": len(purchases),
                "discounted_orders": len(discounted_purchases),
                "full_price_orders": len(full_price_purchases),
                "discount_adoption_rate": round(discount_rate, 2),
                "average_discount_percentage": round(avg_discount, 2)
            },
            "financial_impact": {
                "total_discount_amount": round(total_discount_amount, 2),
                "discounted_revenue": round(discounted_revenue, 2),
                "full_price_revenue": round(full_price_revenue, 2),
                "revenue_impact_percentage": round((total_discount_amount / max(discounted_revenue + full_price_revenue, 1)) * 100, 2)
            }
        }
    
    def _get_cohort_revenue(self, parameters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze revenue by customer registration cohorts"""
        cohort_period = parameters.get("cohort_period", "month")
        
        users = db.query(User).all()
        cohort_data = {}
        
        for user in users:
            # Group users by registration month
            cohort_key = user.registration_date.strftime("%Y-%m")
            
            if cohort_key not in cohort_data:
                cohort_data[cohort_key] = {
                    "users": 0,
                    "total_revenue": 0,
                    "total_orders": 0
                }
            
            cohort_data[cohort_key]["users"] += 1
            
            # Get user's purchases
            purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
            user_revenue = sum(p.total_amount for p in purchases)
            user_orders = len(purchases)
            
            cohort_data[cohort_key]["total_revenue"] += user_revenue
            cohort_data[cohort_key]["total_orders"] += user_orders
        
        # Calculate per-user metrics for each cohort
        for cohort_key, data in cohort_data.items():
            data["revenue_per_user"] = data["total_revenue"] / max(data["users"], 1)
            data["orders_per_user"] = data["total_orders"] / max(data["users"], 1)
            data["total_revenue"] = round(data["total_revenue"], 2)
            data["revenue_per_user"] = round(data["revenue_per_user"], 2)
            data["orders_per_user"] = round(data["orders_per_user"], 2)
        
        return {
            "cohort_period": cohort_period,
            "cohort_analysis": cohort_data,
            "insights": {
                "most_valuable_cohort": max(cohort_data.items(), key=lambda x: x[1]["revenue_per_user"])[0] if cohort_data else None,
                "largest_cohort": max(cohort_data.items(), key=lambda x: x[1]["users"])[0] if cohort_data else None
            }
        }
    
    def _create_summary(self, data: Dict[str, Any]) -> str:
        """Create human-readable summary of financial data"""
        if "revenue_summary" in data:
            summary = data["revenue_summary"]
            period = data.get("report_period", {}).get("days", "N/A")
            
            return f"""
Financial Report Summary ({period} days):

💰 Revenue Performance:
• Total Revenue: ${summary.get('total_revenue', 0):,.2f}
• Total Orders: {summary.get('total_orders', 0):,}
• Average Order Value: ${summary.get('average_order_value', 0):.2f}
• Growth Rate: {summary.get('growth_rate_percent', 0):.1f}%

📊 Key Insights:
• Top Category: {data.get('insights', {}).get('top_revenue_category', 'N/A')}
• Preferred Payment: {data.get('insights', {}).get('preferred_payment_method', 'N/A')}
• Peak Day: {data.get('insights', {}).get('peak_revenue_day', 'N/A')}
            """.strip()
        
        elif "profit_analysis" in data:
            profit = data["profit_analysis"]
            margins = data["margin_analysis"]
            
            return f"""
Profit Analysis Summary:

💸 Cost Structure:
• Total Revenue: ${profit.get('total_revenue', 0):,.2f}
• Cost of Goods Sold: ${profit.get('cost_of_goods_sold', 0):,.2f}
• Operational Costs: ${profit.get('operational_costs', 0):,.2f}

📈 Profitability:
• Gross Profit: ${profit.get('gross_profit', 0):,.2f}
• Net Profit: ${profit.get('net_profit', 0):,.2f}
• Gross Margin: {margins.get('gross_margin_percent', 0):.1f}%
• Net Margin: {margins.get('net_margin_percent', 0):.1f}%
            """.strip()
        
        return f"Financial Reporting Agent processed: {json.dumps(data, indent=2, default=str)}"