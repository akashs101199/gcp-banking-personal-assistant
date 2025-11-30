from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- API Models ---

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    history: List[ChatMessage] = []

# --- Tool Input Models ---

class GetAccountBalanceInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")

class GetRecentTransactionsInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")
    limit: int = Field(10, description="Number of transactions to retrieve")

class GetSpendingAnalysisInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")
    days: int = Field(30, description="Number of days to analyze")

class GetCreditScoreInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")

class GetPersonalizedOffersInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")

class TransferFundsInput(BaseModel):
    from_account: str = Field(..., description="Source account ID")
    to_account: str = Field(..., description="Destination account ID")
    amount: float = Field(..., description="Amount to transfer")
    confirmed: bool = Field(False, description="User confirmation flag")
    pin: Optional[str] = Field(None, description="Security PIN for confirmation")

class PayBillInput(BaseModel):
    payee: str = Field(..., description="Bill payee name")
    amount: float = Field(..., description="Payment amount")
    account_id: str = Field(..., description="Account to pay from")
    confirmed: bool = Field(False, description="User confirmation flag")

class DetectAnomaliesInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")
    sensitivity: float = Field(5.0, description="Sensitivity level (1-10)")

class PredictCashflowInput(BaseModel):
    user_id: str = Field(..., description="The user's account ID")
    forecast_days: int = Field(30, description="Number of days to forecast")

# --- Data Models (BigQuery) ---

class User(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    credit_score: Optional[int] = None
    account_balance: Optional[float] = None
    created_at: Optional[datetime] = None

class Transaction(BaseModel):
    transaction_id: str
    user_id: Optional[str] = None
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
