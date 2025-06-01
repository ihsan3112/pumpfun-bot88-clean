import requests
import time
import threading
from flask import Flask, request
from solana.rpc.api import Client
from solana.keypair import Keypair
import base58

# === Konfigurasi ===
PRIVATE_KEY = "3erUyYNgnzbZ3HF8kpir7e2uHjmRNUU3bvTpMdjZRfrJR9QAXxMTvTB7LTht6admrGnSyYio3oK6F6J2RGmF7LQB"
RPC_URL = "https://rpc.ankr.com/solana"
BUY_AMOUNT_SOL = 0.03
BUYER_THRESHOLD = 10
MAX_ACTIVE_TRADES = 5
ACCESS_KEY = "sansha99"

# === Inisialisasi ===
client = Client(RPC_URL)
app = Flask(__name__)
robot_ready = False
active_trades = []
known_tokens = set()

# === Wallet ===
keypair = Keypair.from_secret_key(base58.b58decode(PRIVATE_KEY))
wallet_address = str(keypair.public_key)

def fetch_new_tokens():
    response = requests.get("https://pump.fun/api/tokens")
    return response.json()

def buy_token(token_address):
    print(f"💰 Membeli token: {token_address}")

def get_token_price(token_address):
    return 0.01

def sell_token(token_address):
    print(f"💸 Menjual token: {token_address}")

def monitor_price_and_sell(token_address, buy_price):
    print(f"📈 Monitoring harga {token_address} dari {buy_price}")

def start_robot():
    global active_trades, known_tokens
    tokens = fetch_new_tokens()
    for token in tokens:
        address = token["address"]
        buyers = token.get("buyerCount", 0)

        if address in known_tokens or buyers < BUYER_THRESHOLD:
            continue
        if len(active_trades) >= MAX_ACTIVE_TRADES:
            continue

        known_tokens.add(address)
        active_trades.append(address)
        buy_token(address)
        buy_price = get_token_price(address)
        threading.Thread(target=monitor_price_and_sell, args=(address, buy_price)).start()
        time.sleep(2)

@app.route('/start')
def trigger():
    global robot_ready
    if request.args.get("key") != ACCESS_KEY:
        return "Unauthorized", 403
    robot_ready = True
    return "✅ Bot aktif!"

@app.route('/pause')
def pause():
    global robot_ready
    if request.args.get("key") != ACCESS_KEY:
        return "Unauthorized", 403
    robot_ready = False
    return "⏸️ Bot dijeda"

def background_loop():
    while True:
        if robot_ready:
            start_robot()
        time.sleep(1)

# Mulai loop saat dijalankan
threading.Thread(target=background_loop, daemon=True).start()
