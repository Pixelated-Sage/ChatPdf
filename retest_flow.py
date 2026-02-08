import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 1. Upload
    print("Testing Upload...")
    file_path = "backend/test_sample.pdf"
    with open(file_path, "rb") as f:
        files = {"file": ("retest_sample.pdf", f, "application/pdf")}
        r = requests.post(f"{BASE_URL}/upload", files=files)
    
    if r.status_code != 202:
        print(f"Upload failed: {r.text}")
        return
    
    doc_id = r.json()["document_id"]
    print(f"Uploaded: {doc_id}")

    # 2. Polling for processing
    print("Waiting for processing...")
    for _ in range(10):
        r = requests.get(f"{BASE_URL}/documents/{doc_id}")
        if r.json().get("processed"):
            print("Processing complete!")
            break
        time.sleep(2)
    else:
        print("Processing timed out.")
        return

    # 3. Chat
    print("\nTesting Chat with Citation Parsing...")
    payload = {
        "question": "What is mentioned in the document?",
        "document_ids": [doc_id]
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload, stream=True)
    
    full_content = ""
    citations = []
    conv_id = None
    
    for line in r.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                data = json.loads(decoded[6:])
                if data["type"] == "start":
                    conv_id = data["conversation_id"]
                    print(f"Conversation ID: {conv_id}")
                elif data["type"] == "chunk":
                    chunk_content = data["content"]
                    print(chunk_content, end="", flush=True)
                    full_content += chunk_content
                elif data["type"] == "citation":
                    citations.append(data["data"])
                elif data["type"] == "error":
                    print(f"\nError from backend: {data['content']}")
                elif data["type"] == "done":
                    print("\nStream finished.")

    print(f"\nFinal Response: {full_content[:100]}...")
    print(f"Citations found: {len(citations)}")
    for c in citations:
        print(f"- {c['filename']} (Page {c['page']})")

    # 4. Check Persistence
    print("\nChecking Persistence...")
    r = requests.get(f"{BASE_URL}/conversations")
    convs = r.json()
    found = any(c["id"] == conv_id for c in convs)
    print(f"Conversation persisted: {found}")

    if conv_id:
        r = requests.get(f"{BASE_URL}/conversations/{conv_id}/messages")
        msgs = r.json()
        print(f"Messages count: {len(msgs)}")
        for i, m in enumerate(msgs):
            print(f"[{i}] {m['role']}: {m['content'][:30]}...")
            if m['role'] == 'assistant':
                print(f"    Citations saved: {m.get('citations') is not None and len(m.get('citations', [])) > 0}")

if __name__ == "__main__":
    test_flow()
