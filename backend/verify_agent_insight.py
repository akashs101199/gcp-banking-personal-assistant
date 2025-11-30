from google.cloud import bigquery
import os
from datetime import datetime, timedelta

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")

def verify_insight():
    client = bigquery.Client(project=PROJECT_ID)
    user_id = "user_001"
    
    print(f"Verifying data for {user_id}...")

    # 1. Get Current Balance
    query_balance = f"""
        SELECT account_balance
        FROM `{PROJECT_ID}.{DATASET_ID}.users`
        WHERE user_id = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    )
    result_balance = client.query(query_balance, job_config=job_config).result()
    row_balance = next(result_balance, None)
    current_balance = row_balance.account_balance if row_balance else 0
    print(f"Current Balance: ${current_balance:,.2f}")

    # 2. Calculate Average Daily Spend (Last 90 Days)
    # Logic mirrors _predict_cashflow in mcp_server.py
    query_spend = f"""
        WITH daily_spending AS (
            SELECT 
                DATE(date) as day,
                SUM(amount) as daily_total
            FROM `{PROJECT_ID}.{DATASET_ID}.transactions`
            WHERE user_id = @user_id
            AND date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            GROUP BY day
        )
        SELECT 
            AVG(daily_total) as avg_daily_spend,
            COUNT(*) as days_with_spend
        FROM daily_spending
    """
    result_spend = client.query(query_spend, job_config=job_config).result()
    row_spend = next(result_spend, None)
    avg_daily_spend = row_spend.avg_daily_spend if row_spend and row_spend.avg_daily_spend else 0
    print(f"Average Daily Spend (Last 90 Days): ${avg_daily_spend:,.2f}")

    # 3. Project Balance for Next 30 Days
    forecast_days = 30
    projected_spend = avg_daily_spend * forecast_days
    projected_balance = current_balance - projected_spend
    
    print(f"\n--- Projection (Next {forecast_days} Days) ---")
    print(f"Projected Total Spend: ${projected_spend:,.2f}")
    print(f"Projected Balance: ${projected_balance:,.2f}")
    
    if projected_balance < 0:
        print("✓ VERIFIED: Balance is projected to dip below zero.")
    else:
        print("✗ DISCREPANCY: Balance is NOT projected to dip below zero.")

if __name__ == "__main__":
    verify_insight()
