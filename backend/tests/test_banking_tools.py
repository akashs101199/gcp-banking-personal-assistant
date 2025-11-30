import pytest
import pytest
import unittest
from unittest.mock import MagicMock, AsyncMock
from backend.tools.banking_tools import BankingTools

@pytest.fixture
def mock_bq_client():
    with unittest.mock.patch('google.cloud.bigquery.Client') as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def banking_tools(mock_bq_client):
    tools = BankingTools(project_id="test-project")
    # The mock_bq_client fixture already patched the class, so tools.bq_client is the mock
    return tools

@pytest.mark.asyncio
async def test_transfer_funds_needs_confirmation(banking_tools):
    args = {
        "from_account": "acc1",
        "to_account": "acc2",
        "amount": 100.0,
        "confirmed": False
    }
    result = await banking_tools.transfer_funds(args)
    assert result["status"] == "pending_confirmation"

@pytest.mark.asyncio
async def test_transfer_funds_high_value_needs_pin(banking_tools):
    args = {
        "from_account": "acc1",
        "to_account": "acc2",
        "amount": 2000.0,
        "confirmed": True,
        "pin": "wrong"
    }
    result = await banking_tools.transfer_funds(args)
    assert result["status"] == "failed"
    assert "PIN" in result["error"]

@pytest.mark.asyncio
async def test_transfer_funds_success(banking_tools):
    args = {
        "from_account": "acc1",
        "to_account": "acc2",
        "amount": 2000.0,
        "confirmed": True,
        "pin": "1234"
    }
    result = await banking_tools.transfer_funds(args)
    assert result["status"] == "completed"
    assert result["amount"] == 2000.0

@pytest.mark.asyncio
async def test_detect_anomalies(banking_tools):
    # Mock BigQuery result
    mock_row = MagicMock()
    mock_row.transaction_id = "t1"
    mock_row.date.isoformat.return_value = "2023-01-01"
    mock_row.merchant = "Test Merchant"
    mock_row.category = "Food"
    mock_row.amount = 100.0
    mock_row.z_score = 4.5
    
    mock_job = MagicMock()
    mock_job.result.return_value = [mock_row]
    banking_tools.bq_client.query.return_value = mock_job
    
    args = {"user_id": "user1", "sensitivity": 5.0}
    result = await banking_tools.detect_anomalies(args)
    
    assert result["count"] == 1
    assert result["anomalies"][0]["severity"] == "high"

@pytest.mark.asyncio
async def test_predict_cashflow_risk(banking_tools):
    # Mock BigQuery results
    # First query: daily spending
    mock_row1 = MagicMock()
    mock_row1.avg_daily_spend = 100.0
    
    # Second query: balance
    mock_row2 = MagicMock()
    mock_row2.account_balance = 500.0
    
    # Setup side effects for multiple query calls
    mock_job1 = MagicMock()
    mock_job1.result.return_value = iter([mock_row1])
    
    mock_job2 = MagicMock()
    mock_job2.result.return_value = iter([mock_row2])
    
    banking_tools.bq_client.query.side_effect = [mock_job1, mock_job2]
    
    args = {"user_id": "user1", "forecast_days": 10}
    result = await banking_tools.predict_cashflow(args)
    
    # Predicted spend = 100 * 10 = 1000
    # Balance = 500
    # Projected = 500 - 1000 = -500
    assert result["projected_balance"] == -500.0
    assert result["status"] == "risk"
