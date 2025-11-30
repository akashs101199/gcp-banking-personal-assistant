"""
BigQuery Data Seeding Script for Banking AI
Seeds mock data into GCP BigQuery tables
"""

from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import os
import uuid
import time

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")

def seed_bigquery_data():
    """Seed BigQuery with realistic banking data"""
    
    client = bigquery.Client(project=PROJECT_ID)
    
    print("Starting BigQuery data seeding (Transactions Only)...")

    # Dataset exists, skipping creation
    # dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    # ...

    # Define schemas
    tables_schema = {
        "transactions": [
            bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING"),
            bigquery.SchemaField("date", "TIMESTAMP"),
            bigquery.SchemaField("merchant", "STRING"),
            bigquery.SchemaField("category", "STRING"),
            bigquery.SchemaField("amount", "FLOAT"),
            bigquery.SchemaField("description", "STRING"),
            bigquery.SchemaField("status", "STRING"),
        ]
    }

    # Re-create transactions table
    for table_name, schema in tables_schema.items():
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        # Delete table if exists
        try:
            client.delete_table(table_ref, not_found_ok=True)
            print(f"Deleted table {table_name}")
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")

        # Create table
        table = bigquery.Table(table_ref, schema=schema)
        try:
            client.create_table(table)
            print(f"Table {table_name} created")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
    
    print("Waiting 10 seconds for table to initialize...")
    time.sleep(10)
    
    # Generate user data (needed for user_ids)
    users_data = [
        {"user_id": "user_001", "account_balance": 12450.50},
        {"user_id": "user_002", "account_balance": 45230.75},
        {"user_id": "user_003", "account_balance": 8750.25},
        {"user_id": "demo_user", "account_balance": 12450.50}
    ]
    
    # Skip inserting users
    # ...
    users_data = [
        {
            "user_id": "user_001",
            "name": "Alex Chen",
            "email": "alex.chen@email.com",
            "phone": "+1-555-0101",
            "credit_score": 742,
            "account_balance": 12450.50,
            "created_at": (datetime.utcnow() - timedelta(days=365)).isoformat()
        },
        {
            "user_id": "user_002",
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1-555-0102",
            "credit_score": 810,
            "account_balance": 45230.75,
            "created_at": (datetime.utcnow() - timedelta(days=730)).isoformat()
        },
        {
            "user_id": "user_003",
            "name": "Michael Torres",
            "email": "m.torres@email.com",
            "phone": "+1-555-0103",
            "credit_score": 685,
            "account_balance": 8750.25,
            "created_at": (datetime.utcnow() - timedelta(days=180)).isoformat()
        },
        {
            "user_id": "demo_user",
            "name": "Demo User",
            "email": "demo@nova.ai",
            "phone": "+1-555-0100",
            "credit_score": 742,
            "account_balance": 12450.50,
            "created_at": (datetime.utcnow() - timedelta(days=365)).isoformat()
        }
    ]
    
    '''
    # Insert users
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.users"
    errors = client.insert_rows_json(table_ref, users_data)
    if errors:
        print(f"Errors inserting users: {errors}")
    else:
        print(f"✓ Inserted {len(users_data)} users")
    '''
    
    # Generate transactions
    categories = {
        "Food & Dining": ["Starbucks", "Whole Foods", "Local Bistro", "Pizza Place", "Sushi Bar", "Uber Eats"],
        "Shopping": ["Amazon", "Target", "Nike", "Apple Store", "Best Buy", "Zara"],
        "Transportation": ["Uber", "Shell Gas", "Chevron", "Metro Transit", "Parking"],
        "Bills & Utilities": ["Electric Company", "Water Utility", "Internet ISP", "Mobile Carrier", "Gas Company"],
        "Entertainment": ["Netflix", "Spotify", "Cinema", "Concert Tickets", "Gaming Store"],
        "Travel": ["Airbnb", "Hilton Hotel", "Delta Airlines", "Expedia", "Hertz Rental"],
        "Healthcare": ["CVS Pharmacy", "Medical Clinic", "Dentist Office", "Gym Membership"],
        "Personal": ["Salon", "Dry Cleaning", "Pet Store", "Bookstore"]
    }
    
    transactions_data = []
    
    # Generate accounts
    accounts_data = []
    for user in users_data:
        # Primary checking account
        accounts_data.append({
            "account_id": f"{user['user_id']}_checking",
            "user_id": user["user_id"],
            "account_type": "Checking",
            "balance": user["account_balance"] * 0.6,
            "currency": "USD",
            "status": "active",
            "opened_date": user["created_at"]
        })
        
        # Savings account
        accounts_data.append({
            "account_id": f"{user['user_id']}_savings",
            "user_id": user["user_id"],
            "account_type": "Savings",
            "balance": user["account_balance"] * 0.3,
            "currency": "USD",
            "status": "active",
            "opened_date": user["created_at"]
        })

        # Credit Card account
        accounts_data.append({
            "account_id": f"{user['user_id']}_credit",
            "user_id": user["user_id"],
            "account_type": "Credit Card",
            "balance": -round(random.uniform(500, 5000), 2),
            "currency": "USD",
            "status": "active",
            "opened_date": user["created_at"]
        })
    
    '''
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.accounts"
    errors = client.insert_rows_json(table_ref, accounts_data)
    if errors:
        print(f"Errors inserting accounts: {errors}")
    else:
        print(f"✓ Inserted {len(accounts_data)} accounts")
    '''

    # Generate transactions
    # The categories dictionary is defined twice, keeping the second one as it's used below.
    # The first definition is kept for context as it was in the original document.
    categories = {
        "Food & Dining": ["Starbucks", "Whole Foods", "Local Bistro", "Pizza Place", "Sushi Bar", "Uber Eats"],
        "Shopping": ["Amazon", "Target", "Nike", "Apple Store", "Best Buy", "Zara"],
        "Transportation": ["Uber", "Shell Gas", "Chevron", "Metro Transit", "Parking"],
        "Bills & Utilities": ["Electric Company", "Water Utility", "Internet ISP", "Mobile Carrier", "Gas Company"],
        "Entertainment": ["Netflix", "Spotify", "Cinema", "Concert Tickets", "Gaming Store"],
        "Travel": ["Airbnb", "Hilton Hotel", "Delta Airlines", "Expedia", "Hertz Rental"],
        "Healthcare": ["CVS Pharmacy", "Medical Clinic", "Dentist Office", "Gym Membership"],
        "Personal": ["Salon", "Dry Cleaning", "Pet Store", "Bookstore"]
    }
    
    transactions_data = []
    
    for user in users_data:
        user_id = user["user_id"]
        # Generate 1 year of data
        start_date = datetime.utcnow() - timedelta(days=365)
        
        # Generate 300-500 transactions per user for a year
        num_transactions = random.randint(300, 500)
        
        for _ in range(num_transactions):
            category = random.choice(list(categories.keys()))
            merchant = random.choice(categories[category])
            
            # Category-specific amount ranges
            if category == "Travel":
                amount = round(random.uniform(200, 2000), 2)
            elif category == "Bills & Utilities":
                amount = round(random.uniform(50, 300), 2)
            elif category == "Shopping":
                if random.random() > 0.7:  # 30% chance of large purchase
                    amount = round(random.uniform(200, 800), 2)
                else:
                    amount = round(random.uniform(15, 150), 2)
            elif category == "Food & Dining":
                amount = round(random.uniform(8, 85), 2)
            else:
                amount = round(random.uniform(10, 200), 2)
            
            transaction_date = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            transactions_data.append({
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "date": transaction_date.isoformat(),
                "merchant": merchant,
                "category": category,
                "amount": amount,
                "description": f"{merchant} purchase",
                "status": "completed"
            })

        # Inject Fraudulent Transactions (Anomalies)
        # 1. High amount in unusual category
        fraud_date = datetime.utcnow() - timedelta(days=random.randint(1, 10))
        transactions_data.append({
            "transaction_id": str(uuid.uuid4()),
            "user_id": user_id,
            "date": fraud_date.isoformat(),
            "merchant": "Electronics Overseas",
            "category": "Shopping",
            "amount": 2500.00, # High amount
            "description": "Electronics purchase",
            "status": "completed"
        })

        # 2. Rapid succession transactions
        rapid_date = datetime.utcnow() - timedelta(days=random.randint(1, 5))
        for i in range(3):
            transactions_data.append({
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "date": (rapid_date + timedelta(minutes=i*5)).isoformat(),
                "merchant": "Unknown Vendor",
                "category": "Services",
                "amount": 99.99,
                "description": "Service charge",
                "status": "completed"
            })

    # Insert transactions using load_table_from_json (Batch Load)
    print(f"Inserting {len(transactions_data)} transactions...")
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.transactions"
    job_config = bigquery.LoadJobConfig(
        schema=tables_schema["transactions"],
        write_disposition="WRITE_APPEND"
    )
    
    try:
        job = client.load_table_from_json(transactions_data, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete.
        print(f"✓ Loaded {len(transactions_data)} transactions via batch job")
    except Exception as e:
        print(f"Error loading transactions: {e}")
        if hasattr(e, 'errors'):
            print(f"Detailed errors: {e.errors}")
    
    # Generate offers
    offers_data = [
        {
            "offer_id": "offer_001",
            "title": "Premium Travel Rewards Card",
            "description": "Earn 3x points on travel and dining. 60,000 bonus points after spending $4,000 in first 3 months.",
            "category": "Credit Card",
            "match_score": 95,
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            "offer_id": "offer_002",
            "title": "Home Improvement Loan",
            "description": "Low 4.5% APR for renovation projects up to $100,000. No origination fees.",
            "category": "Loan",
            "match_score": 82,
            "valid_until": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        {
            "offer_id": "offer_003",
            "title": "High Yield Savings Account",
            "description": "4.2% APY with no minimum balance. FDIC insured up to $250,000.",
            "category": "Savings",
            "match_score": 78,
            "valid_until": (datetime.utcnow() + timedelta(days=90)).isoformat()
        },
        {
            "offer_id": "offer_004",
            "title": "Cash Back Credit Card",
            "description": "Unlimited 2% cash back on all purchases. No annual fee. $200 welcome bonus.",
            "category": "Credit Card",
            "match_score": 88,
            "valid_until": (datetime.utcnow() + timedelta(days=45)).isoformat()
        },
        {
            "offer_id": "offer_005",
            "title": "Investment Advisory Service",
            "description": "Professional portfolio management with 0.25% advisory fee. Minimum $10,000 investment.",
            "category": "Investment",
            "match_score": 70,
            "valid_until": (datetime.utcnow() + timedelta(days=120)).isoformat()
        },
        {
            "offer_id": "offer_006",
            "title": "Auto Loan Refinancing",
            "description": "Refinance your auto loan and save up to $100/month. Rates as low as 3.9% APR.",
            "category": "Loan",
            "match_score": 65,
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            "offer_id": "offer_007",
            "title": "Business Checking Account",
            "description": "Free business checking with no monthly fees. Includes 200 free transactions/month.",
            "category": "Business Banking",
            "match_score": 55,
            "valid_until": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        {
            "offer_id": "offer_008",
            "title": "Certificate of Deposit (12-month)",
            "description": "Guaranteed 4.5% APY for 12-month term. Minimum deposit $1,000.",
            "category": "Savings",
            "match_score": 72,
            "valid_until": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
    ]
    
    '''
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.offers"
    errors = client.insert_rows_json(table_ref, offers_data)
    if errors:
        print(f"Errors inserting offers: {errors}")
    else:
        print(f"✓ Inserted {len(offers_data)} offers")
    '''
    
    # Generate some sample conversations
    conversations_data = [
        {
            "conversation_id": str(uuid.uuid4()),
            "user_id": "demo_user",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "user_message": "What's my account balance?",
            "ai_response": "Your current account balance is $12,450.50. You have $8,715.35 in checking and $3,735.15 in savings.",
            "intent": "account_inquiry",
            "sentiment": 0.8
        },
        {
            "conversation_id": str(uuid.uuid4()),
            "user_id": "demo_user",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "user_message": "Show me my spending this month",
            "ai_response": "This month you've spent $2,345.67 total. Your top categories are: Food & Dining ($567), Shopping ($445), and Transportation ($234).",
            "intent": "spending_analysis",
            "sentiment": 0.6
        }
    ]
    
    '''
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.conversations"
    errors = client.insert_rows_json(table_ref, conversations_data)
    if errors:
        print(f"Errors inserting conversations: {errors}")
    else:
        print(f"✓ Inserted {len(conversations_data)} conversation records")
    '''
    
    print("\n" + "="*50)
    print("BigQuery seeding completed successfully!")
    print("="*50)
    print(f"\nDataset: {DATASET_ID}")
    print(f"Users: {len(users_data)}")
    print(f"Transactions: {len(transactions_data)}")
    print(f"Accounts: {len(accounts_data)}")
    print(f"Offers: {len(offers_data)}")
    print(f"Conversations: {len(conversations_data)}")


if __name__ == "__main__":
    seed_bigquery_data()