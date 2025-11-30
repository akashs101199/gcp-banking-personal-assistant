import os
import uuid
from typing import Dict, Any, List, Optional
from google.cloud import bigquery
from google.cloud.bigquery import ScalarQueryParameter
from backend.models.schemas import (
    GetAccountBalanceInput, GetRecentTransactionsInput, GetSpendingAnalysisInput,
    GetCreditScoreInput, GetPersonalizedOffersInput, TransferFundsInput, PayBillInput,
    DetectAnomaliesInput, PredictCashflowInput
)

class BankingTools:
    def __init__(self, project_id: str, dataset_id: Optional[str] = None):
        self.project_id = project_id
        self.dataset_id = dataset_id or os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")
        self.bq_client = bigquery.Client(project=project_id)

    async def get_account_balance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = GetAccountBalanceInput(**args)
        query = f"""
            SELECT account_balance, name
            FROM `{self.project_id}.{self.dataset_id}.users`
            WHERE user_id = @user_id
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id)
            ]
        )
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            return {
                "balance": row.account_balance,
                "name": row.name,
                "currency": "USD"
            }
        return {"error": "Account not found"}

    async def get_recent_transactions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = GetRecentTransactionsInput(**args)
        query = f"""
            SELECT transaction_id, date, merchant, category, amount, description
            FROM `{self.project_id}.{self.dataset_id}.transactions`
            WHERE user_id = @user_id
            ORDER BY date DESC
            LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id),
                ScalarQueryParameter("limit", "INT64", input_data.limit)
            ]
        )
        result = self.bq_client.query(query, job_config=job_config).result()
        
        transactions = []
        for row in result:
            transactions.append({
                "id": row.transaction_id,
                "date": row.date.isoformat() if row.date else None,
                "merchant": row.merchant,
                "category": row.category,
                "amount": row.amount,
                "description": row.description
            })
        
        return {"transactions": transactions}

    async def get_spending_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = GetSpendingAnalysisInput(**args)
        query = f"""
            SELECT 
                category,
                SUM(amount) as total_spent,
                COUNT(*) as transaction_count,
                AVG(amount) as avg_transaction
            FROM `{self.project_id}.{self.dataset_id}.transactions`
            WHERE user_id = @user_id
            AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            GROUP BY category
            ORDER BY total_spent DESC
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id),
                ScalarQueryParameter("days", "INT64", input_data.days)
            ]
        )
        result = self.bq_client.query(query, job_config=job_config).result()
        
        analysis = []
        for row in result:
            analysis.append({
                "category": row.category,
                "total_spent": row.total_spent,
                "transaction_count": row.transaction_count,
                "avg_transaction": row.avg_transaction
            })
        
        return {"spending_by_category": analysis, "period_days": input_data.days}

    async def get_credit_score(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = GetCreditScoreInput(**args)
        query = f"""
            SELECT credit_score, name
            FROM `{self.project_id}.{self.dataset_id}.users`
            WHERE user_id = @user_id
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id)
            ]
        )
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            return {
                "credit_score": row.credit_score,
                "name": row.name,
                "rating": "Excellent" if row.credit_score > 750 else "Good" if row.credit_score > 670 else "Fair"
            }
        return {"error": "User not found"}

    async def get_personalized_offers(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Note: In a real scenario, we might use user_id to filter offers
        input_data = GetPersonalizedOffersInput(**args)
        query = f"""
            SELECT offer_id, title, description, category, match_score
            FROM `{self.project_id}.{self.dataset_id}.offers`
            WHERE valid_until > CURRENT_TIMESTAMP()
            ORDER BY match_score DESC
            LIMIT 5
        """
        result = self.bq_client.query(query).result()
        
        offers = []
        for row in result:
            offers.append({
                "id": row.offer_id,
                "title": row.title,
                "description": row.description,
                "category": row.category,
                "match_score": row.match_score
            })
        
        return {"offers": offers}

    async def transfer_funds(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = TransferFundsInput(**args)
        
        if not input_data.confirmed:
            return {
                "status": "pending_confirmation",
                "message": f"Please confirm transfer of ${input_data.amount} from {input_data.from_account} to {input_data.to_account}. A PIN may be required."
            }
        
        # Mock PIN verification
        if input_data.amount > 1000:
            if not input_data.pin or input_data.pin != "1234":
                return {
                    "status": "failed",
                    "error": "Invalid or missing PIN for high-value transaction"
                }

        # Log transaction (simplified)
        return {
            "status": "completed",
            "transaction_id": str(uuid.uuid4()),
            "amount": input_data.amount,
            "message": "Transfer completed successfully"
        }

    async def pay_bill(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = PayBillInput(**args)
        return {
            "status": "completed",
            "transaction_id": str(uuid.uuid4()),
            "payee": input_data.payee,
            "amount": input_data.amount,
            "message": f"Payment of ${input_data.amount} to {input_data.payee} completed"
        }

    async def detect_anomalies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = DetectAnomaliesInput(**args)
        
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
                ABS(t.amount - s.avg_amount) / NULLIF(s.stddev_amount, 0) as z_score
            FROM `{self.project_id}.{self.dataset_id}.transactions` t
            JOIN stats s ON t.category = s.category
            WHERE t.user_id = @user_id
            AND t.date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND ABS(t.amount - s.avg_amount) > (s.stddev_amount * @threshold)
            ORDER BY z_score DESC
            LIMIT 5
        """
        
        threshold = 3.0 - (input_data.sensitivity / 10.0)
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id),
                ScalarQueryParameter("threshold", "FLOAT64", threshold)
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
                "z_score": float(row.z_score),
                "severity": "high" if row.z_score > 3 else "medium"
            })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies)
        }

    async def predict_cashflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_data = PredictCashflowInput(**args)
        
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
            )
            SELECT 
                AVG(daily_total) as avg_daily_spend
            FROM daily_spending
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("user_id", "STRING", input_data.user_id)
            ]
        )
        
        result = self.bq_client.query(query, job_config=job_config).result()
        row = next(result, None)
        
        if row:
            avg_daily = float(row.avg_daily_spend or 0)
            predicted_total = avg_daily * input_data.forecast_days
            
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
                        ScalarQueryParameter("user_id", "STRING", input_data.user_id)
                    ]
                )
            ).result()
            
            balance_row = next(balance_result, None)
            current_balance = float(balance_row.account_balance) if balance_row else 0
            
            projected_balance = current_balance - predicted_total
            
            return {
                "forecast_days": input_data.forecast_days,
                "current_balance": current_balance,
                "predicted_total_spend": predicted_total,
                "projected_balance": projected_balance,
                "status": "healthy" if projected_balance > 0 else "risk"
            }
        
        return {"error": "Insufficient data"}
