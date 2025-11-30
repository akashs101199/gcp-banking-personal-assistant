import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_list_tools():
    print("\nTesting /mcp/tools/list...")
    try:
        response = requests.post(f"{BASE_URL}/mcp/tools/list")
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            print(f"✓ Success! Found {len(tools)} tools.")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_call_tool(tool_name, args):
    print(f"\nTesting /mcp/tools/call ({tool_name})...")
    payload = {
        "name": tool_name,
        "arguments": args
    }
    try:
        response = requests.post(f"{BASE_URL}/mcp/tools/call", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("Waiting for server to start...")
    time.sleep(5)
    
    if not test_list_tools():
        print("Aborting tests due to list_tools failure.")
        return

    # Test 1: Get Account Balance (via query_transactions as a proxy or just check transactions)
    # Note: mcp_server.py doesn't have get_account_balance, it has query_transactions
    
    # Test 2: Query Transactions
    test_call_tool("query_transactions", {
        "user_id": "user_001",
        "limit": 5
    })

    # Test 3: Detect Anomalies
    test_call_tool("detect_anomalies", {
        "user_id": "user_001",
        "sensitivity": 8
    })

    # Test 4: Predict Cashflow
    test_call_tool("predict_cashflow", {
        "user_id": "user_001",
        "forecast_days": 30
    })

if __name__ == "__main__":
    main()
