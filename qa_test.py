import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_health():
    print("Checking health...")
    response = requests.get("http://localhost:8000/")
    print(response.json())

def test_upload():
    print("\nTesting PDF upload...")
    file_path = "backend/test_sample.pdf"
    with open(file_path, "rb") as f:
        files = {"file": ("test_sample.pdf", f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 202:
        data = response.json()
        print(f"Upload successful: {data}")
        return data["document_id"]
    else:
        print(f"Upload failed: {response.status_code} {response.text}")
        return None

def test_documents():
    print("\nListing documents...")
    response = requests.get(f"{BASE_URL}/documents")
    print(response.json())

def test_chat(doc_id):
    print("\nTesting chat...")
    payload = {
        "question": "What is the content of this PDF?",
        "document_ids": [doc_id]
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload, stream=True)
    
    print("Streaming response:")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))

if __name__ == "__main__":
    test_health()
    doc_id = test_upload()
    if doc_id:
        # Wait for processing
        time.sleep(5)
        test_documents()
        test_chat(doc_id)
