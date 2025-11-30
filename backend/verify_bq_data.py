from google.cloud import bigquery
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID", "nova_banking_data_v2")

def verify_data():
    client = bigquery.Client(project=PROJECT_ID)
    
    # Check users
    query = f"SELECT count(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.users`"
    result = client.query(query).result()
    for row in result:
        print(f"Users count: {row.count}")

    # Check transactions
    query = f"SELECT count(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.transactions`"
    result = client.query(query).result()
    for row in result:
        print(f"Transactions count: {row.count}")

    # Check accounts
    query = f"SELECT count(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.accounts`"
    result = client.query(query).result()
    for row in result:
        print(f"Accounts count: {row.count}")

    # Check offers
    query = f"SELECT count(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.offers`"
    result = client.query(query).result()
    for row in result:
        print(f"Offers count: {row.count}")

    # List tables in dataset
    print(f"\nTables in {DATASET_ID}:")
    tables = client.list_tables(DATASET_ID)
    # Try inserting one transaction manually
    print("\nAttempting manual insertion...")
    import datetime
    row = {
        "transaction_id": "test_tx_1",
        "user_id": "user_001",
        "date": datetime.datetime.utcnow().isoformat(),
        "merchant": "Test Merchant",
        "category": "Test",
        "amount": 10.0,
        "description": "Test",
        "status": "completed"
    }
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.transactions"
    errors = client.insert_rows_json(table_ref, [row])
    if errors:
        print(f"Manual insertion errors: {errors}")
    else:
        print("Manual insertion successful")

    # Check transactions again
    query = f"SELECT count(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.transactions`"
    result = client.query(query).result()
    for row in result:
        print(f"Transactions count after manual insert: {row.count}")

if __name__ == "__main__":
    verify_data()
