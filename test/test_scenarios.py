import requests
import time

API_URL = "http://localhost:8000/chat"
SESSION_ID = "test_user123"

def send_message(message, session_id=SESSION_ID):
    """Helper untuk kirim pesan ke chatbot API"""
    payload = {"session_id": session_id, "message": message}
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["reply"]
    return f"Error: {response.status_code}"

def test_scenario(title, messages):
    """Cetak skenario percakapan"""
    print(f"\n<== {title} ==>")
    print("=" * 50)

    for msg in messages:
        print(f"\n=> User: {msg}")
        reply = send_message(msg)
        print(f"<= Bot : {reply}")
        time.sleep(0.5)

# =============================================================================
# CORE TESTS
# =============================================================================

def run_core_tests():
    # 1. Order status
    test_scenario(
        "1. Status Pesanan",
        [
            "Status pesanan 2001",
            "Pesanan 9999 dimana?"
        ]
    )

    # 2. Product info
    test_scenario(
        "2. Informasi Produk",
        [
            "Info tentang dress summer",
            "Produk apa saja yang tersedia?"
        ]
    )

    # 3. Warranty
    test_scenario(
        "3. Kebijakan Garansi",
        [
            "Bagaimana cara claim garansi?",
            "Garansi berlaku berapa lama?"
        ]
    )

    # 4. Memory (last 3 interaction)
    test_scenario(
        "4. Memory",
        [
            "Halo, nama saya Malinda",
            "Status pesanan 2002",
            "Siapa nama saya?"
        ]
    )

    # 5. GREETING (rule-based)
    test_scenario(
        "5. Greeting",
        [
            "Halo",
            "Selamat pagi"
        ]
    )

if __name__ == "__main__":
    print("<========= Starting Core Chatbot Test =========>")
    print("Make sure FastAPI server is running on http://localhost:8000")

    input("\nPress Enter to start tests...")

    run_core_tests()

    print("\n===> Core tests completed!")
