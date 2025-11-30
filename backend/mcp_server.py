"""
MCP Server for Banking Data Lake Integration
Provides structured access to BigQuery data lake for AI agents
"""

from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
import json
import asyncio
from datetime import datetime, timedelta

from google.cloud import bigquery
from google.cloud import storage
import os

# MCP Protocol Types
@dataclass
class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class Resource:
    uri: str
    name: str
    description: str
    mime_type: str


class MCPBankingServer:
    """MCP Server for Banking Data Lake Operations"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")
        self.bq_client = bigquery.Client(project=self.project_id)
        self.storage_client = storage.Client(project=self.project_id)
        
        # Define available tools
        self.tools = self._initialize_tools()
        
        # Define available resources
        self.resources = self._initialize_resources()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize MCP tools for banking operations"""
        
        return [
            Tool(
                name="query_transactions",
                description="Query transaction data from BigQuery data lake with filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to filter transactions"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        },
                        "category": {
                            "type": "string",
                            "description": "Transaction category filter"
                        },
                        "min_amount": {
                            "type": "number",
                            "description": "Minimum transaction amount"
                        },
                        "max_amount": {
                            "type": "number",
                            "description": "Maximum transaction amount"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 100
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="aggregate_spending",
                description="Aggregate spending data by time period and category",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["day", "week", "month", "category"],
                            "description": "Grouping dimension"
                        },
                        "period_days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 30
                        }
                    },
                    "required": ["user_id", "group_by"]
                }
            ),
            
            Tool(
                name="detect_anomalies",
                description="Detect unusual spending patterns or anomalous transactions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "sensitivity": {
                            "type": "number",
                            "description": "Anomaly detection sensitivity (1-10)",
                            "default": 5
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="compare_spending",
                description="Compare user spending against average or previous periods",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "comparison_type": {
                            "type": "string",
                            "enum": ["month_over_month", "year_over_year", "vs_average"],
                            "description": "Type of comparison"
                        }
                    },
                    "required": ["user_id", "comparison_type"]
                }
            ),
            
            Tool(
                name="predict_cashflow",
                description="Predict future cashflow based on historical patterns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "forecast_days": {
                            "type": "integer",
                            "description": "Number of days to forecast",
                            "default": 30
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="search_merchants",
                description="Search and analyze merchant transaction patterns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "merchant_name": {
                            "type": "string",
                            "description": "Merchant name or pattern to search"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="get_credit_insights",
                description="Get detailed credit score analysis and recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="generate_report",
                description="Generate comprehensive financial report",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "report_type": {
                            "type": "string",
                            "enum": ["monthly_summary", "annual_review", "spending_analysis", "tax_summary"],
                            "description": "Type of report to generate"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "pdf", "csv"],
                            "description": "Output format",
                            "default": "json"
                        }
                    },
                    "required": ["user_id", "report_type"]
                }
            ),
            
            Tool(
                name="get_personalized_insights",
                description="Get AI-generated personalized financial insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        },
                        "insight_type": {
                            "type": "string",
                            "enum": ["savings_opportunities", "budget_recommendations", "investment_suggestions"],
                            "description": "Type of insight"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            
            Tool(
                name="execute_sql_query",
                description="Execute custom SQL query on data lake (admin only)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Query parameters"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    def _initialize_resources(self) -> List[Resource]:
        """Initialize MCP resources for data access"""
        
        return [
            Resource(
                uri="bigquery://nova_banking_data/transactions",
                name="Transactions Data Lake",
                description="Complete transaction history in BigQuery",
                mime_type="application/vnd.google.bigquery.table"
            ),
            Resource(
                uri="bigquery://nova_banking_data/users",
                name="User Profiles Data Lake",
                description="User profile and account information",
                mime_type="application/vnd.google.bigquery.table"
            ),
            Resource(
                uri="bigquery://nova_banking_data/offers",
                name="Financial Offers Data",
                description="Available financial products and offers",
                mime_type="application/vnd.google.bigquery.table"
            ),
            Resource(
                uri="gcs://banking-analytics/ml-models",
                name="ML Models Repository",
                description="Trained ML models for predictions",
                mime_type="application/octet-stream"
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool call execution"""
        
        handlers = {
            "query_transactions": self._query_transactions,
            "aggregate_spending": self._aggregate_spending,
            "detect_anomalies": self._detect_anomalies,
            "compare_spending": self._compare_spending,
            "predict_cashflow": self._predict_cashflow,
            "search_merchants": self._search_merchants,
            "get_credit_insights": self._get_credit_insights,
            "generate_report": self._generate_report,
            "get_personalized_insights": self._get_personalized_insights,
            "execute_sql_query": self._execute_sql_query
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = await handler(arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _query_transactions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query transactions with filters"""
        
        user_id = args["user_id"]
        conditions = ["user_id = @user_id"]
        params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        
        if "start_date" in args:
            conditions.append("date >= @start_date")
            params.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", args["start_date"]))
        
        if "end_date" in args:
            conditions.append("date <= @end_date")
            params.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", args["end_date"]))
        
        if "category" in args:
            conditions.append("category = @category")
            params.append(bigquery.ScalarQueryParameter("category", "STRING", args["category"]))
        
        if "min_amount" in args:
            conditions.append("amount >= @min_amount")
            params.append(bigquery.ScalarQueryParameter("min_amount", "FLOAT64", args["min_amount"]))
        
        if "max_amount" in args:
            conditions.append("amount <= @max_amount")
            params.append(bigquery.ScalarQueryParameter("max_amount", "FLOAT64", args["max_amount"]))
        
        limit = args.get("limit", 100)
        
        query = f"""
            SELECT 
                transaction_id,
                date,
                merchant,
                category,
                amount,
                description,
                status
            FROM `{self.project_id}.{self.dataset_id}.transactions`
            WHERE {' AND '.join(conditions)}
            ORDER BY date DESC
            LIMIT @limit
        """
        
        params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        result = self.bq_client.query(query, job_config=job_config).result()
        
        transactions = []
        for row in result:
            transactions.append({
                "transaction_id": row.transaction_id,
                "date": row.date.isoformat() if row.date else None,
                "merchant": row.merchant,
                "category": row.category,
                "amount": float(row.amount),
                "description": row.description,
                "status": row.status
            })
        
        return {
            "transactions": transactions,
            "count": len(transactions),
            "filters_applied": {k: v for k, v in args.items() if k != "user_id"}
        }
    
    async def _aggregate_spending(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate spending by dimension"""
        
        user_id = args["user_id"]
        group_by = args["group_by"]
        period_days = args.get("period_days", 30)
        
        if group_by == "category":
            query = f"""
                SELECT 
                    category,
                    SUM(amount) as total_amount,
                    COUNT(*) as transaction_count,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM `{self.project_id}.{self.dataset_id}.transactions`
                WHERE user_id = @user_id
                AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
                GROUP BY category
                ORDER BY total_amount DESC
            """
        elif group_by in ["day", "week", "month"]:
            time_format = {
                "day": "DATE(date)",
                "week": "DATE_TRUNC(date, WEEK)",
                "month": "DATE_TRUNC(date, MONTH)"
            }
            
            query = f"""
                SELECT 
                    {time_format[group_by]} as period,
                    SUM(amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM `{self.project_id}.{self.dataset_id}.transactions`
                WHERE user_id = @user_id
                AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
                GROUP BY period
                ORDER BY period DESC
            """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("days", "INT64", period_days)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        
        aggregates = []
        for row in result:
            item = {k: v for k, v in row.items()}
            if "period" in item and item["period"]:
                item["period"] = item["period"].isoformat()
            aggregates.append(item)
        
        return {
            "aggregates": aggregates,
            "group_by": group_by,
            "period_days": period_days
        }
    
    async def _detect_anomalies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalous transactions"""
        
        user_id = args["user_id"]
        sensitivity = args.get("sensitivity", 5)
        
        # Calculate statistical thresholds
        query = f"""
            WITH stats AS (
                SELECT 
                    category,
                    AVG(amount) as avg_amount,
                    STDDEV(amount) as stddev_amount
                FROM `{self.project_id}.{self.dataset_id}.transactions`
                WHERE user_id = @user_id
                AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
                GROUP BY category
            )
            SELECT 
                t.transaction_id,
                t.date,
                t.merchant,
                t.category,
                t.amount,
                s.avg_amount,
                s.stddev_amount,
                ABS(t.amount - s.avg_amount) / s.stddev_amount as z_score
            FROM `{self.project_id}.{self.dataset_id}.transactions` t
            JOIN stats s ON t.category = s.category
            WHERE t.user_id = @user_id
            AND t.date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND ABS(t.amount - s.avg_amount) > (s.stddev_amount * @threshold)
            ORDER BY z_score DESC
            LIMIT 20
        """
        
        threshold = 3.0 - (sensitivity / 10.0)  # Higher sensitivity = lower threshold
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("threshold", "FLOAT64", threshold)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        
        anomalies = []
        for row in result:
            anomalies.append({
                "transaction_id": row.transaction_id,
                "date": row.date.isoformat() if row.date else None,
                "merchant": row.merchant,
                "category": row.category,
                "amount": float(row.amount),
                "avg_amount": float(row.avg_amount),
                "z_score": float(row.z_score),
                "severity": "high" if row.z_score > 3 else "medium"
            })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "sensitivity": sensitivity
        }
    
    async def _compare_spending(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare spending across time periods"""
        
        user_id = args["user_id"]
        comparison_type = args["comparison_type"]
        
        if comparison_type == "month_over_month":
            query = f"""
                WITH current_month AS (
                    SELECT SUM(amount) as total
                    FROM `{self.project_id}.{self.dataset_id}.transactions`
                    WHERE user_id = @user_id
                    AND date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                ),
                previous_month AS (
                    SELECT SUM(amount) as total
                    FROM `{self.project_id}.{self.dataset_id}.transactions`
                    WHERE user_id = @user_id
                    AND date >= DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 1 MONTH)
                    AND date < DATE_TRUNC(CURRENT_DATE(), MONTH)
                )
                SELECT 
                    c.total as current_period,
                    p.total as previous_period,
                    ((c.total - p.total) / p.total * 100) as percent_change
                FROM current_month c, previous_month p
            """
        elif comparison_type == "year_over_year":
            query = f"""
                WITH current_year AS (
                    SELECT SUM(amount) as total
                    FROM `{self.project_id}.{self.dataset_id}.transactions`
                    WHERE user_id = @user_id
                    AND date >= DATE_TRUNC(CURRENT_DATE(), YEAR)
                ),
                previous_year AS (
                    SELECT SUM(amount) as total
                    FROM `{self.project_id}.{self.dataset_id}.transactions`
                    WHERE user_id = @user_id
                    AND date >= DATE_SUB(DATE_TRUNC(CURRENT_DATE(), YEAR), INTERVAL 1 YEAR)
                    AND date < DATE_TRUNC(CURRENT_DATE(), YEAR)
                )
                SELECT 
                    c.total as current_period,
                    p.total as previous_period,
                    ((c.total - p.total) / p.total * 100) as percent_change
                FROM current_year c, previous_year p
            """
        else:  # vs_average
            query = f"""
                WITH user_current AS (
                    SELECT SUM(amount) as total
                    FROM `{self.project_id}.{self.dataset_id}.transactions`
                    WHERE user_id = @user_id
                    AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                ),
                user_avg AS (
                    SELECT AVG(monthly_total) as avg_total
                    FROM (
                        SELECT DATE_TRUNC(date, MONTH) as month, SUM(amount) as monthly_total
                        FROM `{self.project_id}.{self.dataset_id}.transactions`
                        WHERE user_id = @user_id
                        GROUP BY month
                    )
                )
                SELECT 
                    c.total as current_period,
                    a.avg_total as average_period,
                    ((c.total - a.avg_total) / a.avg_total * 100) as percent_change
                FROM user_current c, user_avg a
            """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            return {
                "comparison_type": comparison_type,
                "current_period": float(row.current_period or 0),
                "comparison_period": float(row.previous_period or row.average_period or 0),
                "percent_change": float(row.percent_change or 0),
                "trend": "increasing" if row.percent_change > 0 else "decreasing"
            }
        
        return {"error": "No data available"}
    
    async def _predict_cashflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future cashflow (simplified ML-based)"""
        
        user_id = args["user_id"]
        forecast_days = args.get("forecast_days", 30)
        
        # Simple moving average prediction
        query = f"""
            WITH daily_spending AS (
                SELECT 
                    DATE(date) as day,
                    SUM(amount) as daily_total
                FROM `{self.project_id}.{self.dataset_id}.transactions`
                WHERE user_id = @user_id
                AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
                GROUP BY day
                ORDER BY day
            )
            SELECT 
                AVG(daily_total) as avg_daily_spend,
                STDDEV(daily_total) as stddev_daily_spend
            FROM daily_spending
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            avg_daily = float(row.avg_daily_spend or 0)
            predicted_total = avg_daily * forecast_days
            
            # Get current balance
            balance_query = f"""
                SELECT account_balance
                FROM `{self.project_id}.{self.dataset_id}.users`
                WHERE user_id = @user_id
            """
            
            balance_result = self.bq_client.query(
                balance_query,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                    ]
                )
            ).result()
            
            balance_row = next(balance_result, None)
            current_balance = float(balance_row.account_balance) if balance_row else 0
            
            projected_balance = current_balance - predicted_total
            
            return {
                "forecast_days": forecast_days,
                "current_balance": current_balance,
                "avg_daily_spend": avg_daily,
                "predicted_total_spend": predicted_total,
                "projected_balance": projected_balance,
                "warning": "low_balance" if projected_balance < 1000 else None
            }
        
        return {"error": "Insufficient data for prediction"}
    
    async def _search_merchants(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search merchant transactions"""
        
        user_id = args["user_id"]
        merchant_name = args.get("merchant_name", "")
        
        query = f"""
            SELECT 
                merchant,
                COUNT(*) as transaction_count,
                SUM(amount) as total_spent,
                AVG(amount) as avg_transaction,
                MIN(date) as first_transaction,
                MAX(date) as last_transaction
            FROM `{self.project_id}.{self.dataset_id}.transactions`
            WHERE user_id = @user_id
            AND LOWER(merchant) LIKE LOWER(@merchant_pattern)
            GROUP BY merchant
            ORDER BY total_spent DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("merchant_pattern", "STRING", f"%{merchant_name}%")
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        
        merchants = []
        for row in result:
            merchants.append({
                "merchant": row.merchant,
                "transaction_count": row.transaction_count,
                "total_spent": float(row.total_spent),
                "avg_transaction": float(row.avg_transaction),
                "first_transaction": row.first_transaction.isoformat() if row.first_transaction else None,
                "last_transaction": row.last_transaction.isoformat() if row.last_transaction else None
            })
        
        return {
            "merchants": merchants,
            "count": len(merchants)
        }
    
    async def _get_credit_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit score insights"""
        
        user_id = args["user_id"]
        
        query = f"""
            SELECT credit_score, name
            FROM `{self.project_id}.{self.dataset_id}.users`
            WHERE user_id = @user_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            score = row.credit_score
            
            # Generate insights based on score
            if score >= 750:
                rating = "Excellent"
                recommendations = [
                    "You qualify for premium credit cards with best rewards",
                    "Consider applying for low-interest personal loans",
                    "You're eligible for the best mortgage rates"
                ]
            elif score >= 670:
                rating = "Good"
                recommendations = [
                    "Continue making on-time payments to reach excellent",
                    "Keep credit utilization below 30%",
                    "Consider a credit limit increase"
                ]
            else:
                rating = "Fair"
                recommendations = [
                    "Focus on paying down existing debt",
                    "Set up automatic payments to avoid late fees",
                    "Check credit report for errors"
                ]
            
            return {
                "credit_score": score,
                "rating": rating,
                "recommendations": recommendations,
                "next_steps": "Check back in 30 days for score update"
            }
        
        return {"error": "User not found"}
    
    async def _generate_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        
        user_id = args["user_id"]
        report_type = args["report_type"]
        
        # Execute multiple queries to build report
        spending = await self._aggregate_spending({
            "user_id": user_id,
            "group_by": "category",
            "period_days": 30 if report_type == "monthly_summary" else 365
        })
        
        anomalies = await self._detect_anomalies({
            "user_id": user_id,
            "sensitivity": 5
        })
        
        return {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "spending_summary": spending,
            "anomalies_detected": anomalies["count"],
            "format": args.get("format", "json")
        }
    
    async def _get_personalized_insights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights"""
        
        user_id = args["user_id"]
        insight_type = args["insight_type"]
        
        # Get spending data
        spending = await self._aggregate_spending({
            "user_id": user_id,
            "group_by": "category",
            "period_days": 30
        })
        
        insights = []
        
        if insight_type == "savings_opportunities":
            # Analyze high-spend categories
            for item in spending["aggregates"][:3]:
                category = item.get("category")
                total = item.get("total_amount", 0)
                insights.append(f"You spent ${total:.2f} on {category}. Consider reducing by 10% to save ${total * 0.1:.2f}/month")
        
        elif insight_type == "budget_recommendations":
            # Generate budget based on spending
            total_spend = sum(item.get("total_amount", 0) for item in spending["aggregates"])
            insights.append(f"Your current monthly spending is ${total_spend:.2f}")
            insights.append(f"Recommended budget: ${total_spend * 1.1:.2f} (10% buffer)")
            
        elif insight_type == "investment_suggestions":
            # Check available balance
            balance_query = f"""
                SELECT account_balance
                FROM `{self.project_id}.{self.dataset_id}.users`
                WHERE user_id = @user_id
            """
            result = self.bq_client.query(
                balance_query,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                    ]
                )
            ).result()
            
            row = next(result, None)
            if row:
                balance = row.account_balance
                investable = balance * 0.2  # 20% of balance
                insights.append(f"You have ${balance:.2f} available")
                insights.append(f"Consider investing ${investable:.2f} in diversified portfolio")
        
        return {
            "insight_type": insight_type,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_sql_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom SQL (with security checks)"""
        
        query = args["query"]
        
        # Security: Block dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "UPDATE"]
        if any(keyword in query.upper() for keyword in dangerous_keywords):
            return {"error": "Query contains forbidden operations"}
        
        try:
            result = self.bq_client.query(query).result()
            
            rows = []
            for row in result:
                rows.append({k: v for k, v in row.items()})
            
            return {
                "rows": rows,
                "count": len(rows)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of available MCP tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self.tools
        ]
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Return list of available MCP resources"""
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type
            }
            for resource in self.resources
        ]


# FastAPI integration for MCP server
from fastapi import FastAPI, Request

mcp_app = FastAPI(title="Banking MCP Server")

mcp_server = MCPBankingServer()


@mcp_app.post("/mcp/tools/list")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": mcp_server.get_available_tools()
    }


@mcp_app.post("/mcp/tools/call")
async def call_tool(request: Request):
    """Execute MCP tool"""
    data = await request.json()
    tool_name = data.get("name")
    arguments = data.get("arguments", {})
    
    result = await mcp_server.handle_tool_call(tool_name, arguments)
    
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    }


@mcp_app.post("/mcp/resources/list")
async def list_resources():
    """List available MCP resources"""
    return {
        "resources": mcp_server.get_available_resources()
    }


@mcp_app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)