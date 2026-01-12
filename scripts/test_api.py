
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api():
    print("⏳ Waiting for API to spin up...")
    time.sleep(3) 

    # 1. Test GET News
    print("\n📰 Testing GET /news/ ...")
    try:
        response = requests.get(f"{BASE_URL}/news/")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data) if isinstance(data, list) else 0)
            print(f"   ✅ Success! Found {count} articles.")
            # Print first one
            results = data.get('results', data)
            if results:
                print(f"      Sample: {results[0]['title'][:50]}... ({results[0]['sentiment_label']})")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

    # 2. Test POST Chat (RAG)
    print("\n🤖 Testing POST /chat/ (RAG) ...")
    payload = {"query": "politics in Venezuela"}
    try:
        response = requests.post(
            f"{BASE_URL}/chat/", 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Answer: {data.get('answer')}")
            results = data.get('results', [])
            if results:
                print(f"      Top Result: {results[0]['text'][:80]}...")
            else:
                print("      ⚠️ No results found.")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

if __name__ == "__main__":
    test_api()
