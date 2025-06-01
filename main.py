import requests
import threading
import time
from flask import Flask
from solders.keypair import Keypair

# === Konfigurasi ===
PRIVATE_KEY = "3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB"
BUY_AMOUNT_SOL = 0.01
BUYER_THRESHOLD = 10
MAX_ACTIVE_TRADES = 3

# === Setup Wallet ===
try:
    keypair = Keypair.from_base58_string(PRIVATE_KEY)
    wallet_address = str(keypair.pubkey())
    print(f"👛 Wallet aktif: {wallet_address}")
except Exception as e:
    print("❌ Gagal memuat PRIVATE_KEY:", e)
    exit(1)

# === Bot State ===
active_trades = []
known_tokens = set()

# === Bot Logic ===
def fetch_new_tokens():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get("https://pump.fun/api/communities", headers=headers)
        return response.json()
    except Exception as e:
        print("⚠️ Gagal fetch token:", e)
        return []

def buy_token(token_address):
    print(f"🟢 Membeli token: {token_address} sebesar {BUY_AMOUNT_SOL} SOL")
    # Tambahkan logika pembelian nyata di sini

def get_token_price(token_address):
    return 0.01  # Dummy

def sell_token(token_address):
    print(f"🔴 Menjual token: {token_address}")
    # Tambahkan logika jual di sini

def monitor_price_and_sell(token_address, buy_price):
    print(f"📊 Monitoring harga {token_address} dari {buy_price}")
    # Tambahkan trailing stop di sini

def start_robot():
    global active_trades, known_tokens
    print("🚀 Trigger diterima. Bot mulai bekerja...")

    tokens = fetch_new_tokens()
    for token in tokens:
        try:
            address = token["address"]
            buyers = token.get("buyerCount", 0)

            if address in known_tokens or buyers < BUYER_THRESHOLD:
                continue
            if len(active_trades) >= MAX_ACTIVE_TRADES:
                continue

            known_tokens.add(address)
            active_trades.append(address)
            print(f"✅ Token valid: {address} ({buyers} buyers)")
            buy_token(address)
            buy_price = get_token_price(address)
            threading.Thread(target=monitor_price_and_sell, args=(address, buy_price)).start()
            time.sleep(2)
        except Exception as e:
            print("❗ Error saat proses token:", e)

# === Flask App ===
app = Flask(__name__)

@app.route('/trigger')
def trigger():
    threading.Thread(target=start_robot).start()
    return "🤖 Bot dimulai melalui trigger URL!"

if __name__ == "__main__":
    print("🌐 Bot standby, menunggu trigger...")
    app.run(host="0.0.0.0", port=3000)
