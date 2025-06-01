import requests
import time
import threading
from flask import Flask, request
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import transfer, TransferParams
from solana.rpc.types import TxOpts
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

# === Load Keypair ===
keypair = Keypair.from_secret_key(base58.b58decode(PRIVATE_KEY))
wallet_address = keypair.public_key

# === Fungsi Pantau Token Baru ===
def fetch_new_tokens():
    try:
        response = requests.get("https://client-api-2-74b6e9733e6d.herokuapp.com/")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# === Fungsi Beli Token ===
def buy_token(token_address):
    print(f"[BELI] Token: {token_address}")
    to_pubkey = PublicKey(token_address)
    lamports = int(BUY_AMOUNT_SOL * 1e9)
    tx = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=wallet_address,
                to_pubkey=to_pubkey,
                lamports=lamports
            )
        )
    )
    try:
        result = client.send_transaction(tx, keypair, opts=TxOpts(skip_preflight=True))
        print(f"[SUKSES BELI] Tx Hash: {result['result']}")
    except Exception as e:
        print(f"[GAGAL BELI] {e}")

# === Fungsi Dummy Harga Token ===
def get_token_price(token_address):
    return 1.0 + (time.time() % 10) / 100

# === Fungsi Jual Token ===
def sell_token(token_address):
    print(f"[JUAL] Token: {token_address} dijual karena harga turun 20%")
    if token_address in active_trades:
        active_trades.remove(token_address)

# === Fungsi Pantau Harga ===
def monitor_price_and_sell(token_address, buy_price):
    highest = buy_price
    while True:
        try:
            price = get_token_price(token_address)
            if price > highest:
                highest = price
            if (highest - price) / highest >= 0.2:
                sell_token(token_address)
                break
        except:
            break
        time.sleep(3)

# === Fungsi Utama ===
def start_robot():
    global active_trades
    tokens = fetch_new_tokens()
    for token in tokens:
        address = token.get("address")
        buyers = token.get("buyers")
        if address and buyers and address not in known_tokens and buyers >= BUYER_THRESHOLD:
            if len(active_trades) >= MAX_ACTIVE_TRADES:
                continue
            known_tokens.add(address)
            active_trades.append(address)
            buy_token(address)
            buy_price = get_token_price(address)
            threading.Thread(target=monitor_price_and_sell, args=(address, buy_price)).start()
            time.sleep(2)

# === Endpoint Flask ===
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

# === Thread utama (tanpa app.run) ===
def background_loop():
    while True:
        if robot_ready:
            start_robot()
        time.sleep(1)

# Mulai loop saat app di-import oleh gunicorn
threading.Thread(target=background_loop, daemon=True).start()
