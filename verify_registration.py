import requests

BASE_URL = "http://localhost:8000"

def test_registration():
    print("--- User Registration API Verification ---")
    
    test_mobile = "9999999999"
    test_pass = "password123"
    test_name = "Verification User"

    # 1. Test Registration
    print("[1] Testing Registration...")
    res = requests.post(f"{BASE_URL}/api/auth/register", data={
        "mobile": test_mobile,
        "password": test_pass,
        "full_name": test_name
    })
    
    if res.status_code == 200:
        print(f"[SUCCESS] {res.json()['message']}")
    else:
        print(f"[FAIL] {res.text}")

    # 2. Test Login with new user
    print("[2] Testing Login with new user...")
    res = requests.post(f"{BASE_URL}/api/token", data={
        "mobile": test_mobile,
        "password": test_pass
    })
    
    if res.status_code == 200:
        print("[SUCCESS] Login successful, token received.")
    else:
        print(f"[FAIL] Login failed: {res.text}")

    # 3. Test Duplicate Registration (should fail)
    print("[3] Testing Duplicate Registration...")
    res = requests.post(f"{BASE_URL}/api/auth/register", data={
        "mobile": test_mobile,
        "password": test_pass,
        "full_name": test_name
    })
    
    if res.status_code == 400:
        print(f"[SUCCESS] Expected failure: {res.json()['detail']}")
    else:
        print(f"[FAIL] Should have failed but got: {res.status_code}")

if __name__ == "__main__":
    test_registration()
