import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_flow():
    print("--- Phase 10 Verification ---")
    
    # 1. Test Login
    print("[1] Testing Login...")
    res = requests.post(f"{BASE_URL}/api/token", data={
        "mobile": "8888888888",
        "password": "user123"
    })
    if res.status_code == 200:
        token = res.json()["access_token"]
        print("[SUCCESS] Login successful, token received.")
    else:
        print(f"[FAIL] Login failed: {res.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Protected Search
    print("[2] Testing Protected Search...")
    res = requests.post(f"{BASE_URL}/api/memory/search", data={"query": "test"}, headers=headers)
    if res.status_code == 200:
        print("[SUCCESS] Protected search successful.")
    else:
        print(f"[FAIL] Protected search failed: {res.text}")

    # 3. Test Logout Cleanup
    print("[3] Testing Logout Cleanup...")
    # First, let's check if there are any jobs
    res = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    if res.status_code == 200:
        print("[SUCCESS] Logout cleanup reported success.")
    else:
        print(f"[FAIL] Logout failed: {res.text}")

    print("\nVerification complete. Manually check if data/jobs and ChromaDB are cleared.")

if __name__ == "__main__":
    test_flow()
