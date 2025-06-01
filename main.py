import threading
import time
import random
from flask import Flask

app = Flask(__name__)

robot_ready = True  # Aktif otomatis tanpa perlu trigger
safety_lock = False  # Tidak diblokir di awal
known_tokens = set()
max_price_tracker = {}

# ===== Dummy Data Fetcher (ganti nanti dengan real API) =====
def get_buyer_count(address):
    return random.randint(3, 10)  # Buyer count < 20

def get_token_price(address):
    return random.uniform(0.002, 0.005)  # Harga token dummy

def execute_buy(address):
    print(f"[EXECUTE] Beli token {address} sebanyak 0.001 SOL")

def execute_sell(address):
    print(f"[SELL] Jual token {address} karena turun >20% dari harga tertinggi")

# ===== Core Logic =====
def buy_token(address):
    if safety_lock:
        print("[LOCKED] Bot dikunci")
        return

    if address in known_tokens:
        print(f"[SKIP] Token {address} sudah dibeli")
        return

    buyer_count = get_buyer_count(address)
    if buyer_count > 10:
        print(f"[SKIP] Buyer count {buyer_count} terlalu tinggi")
        return

    known_tokens.add(address)
    price = get_token_price(address)
    max_price_tracker[address] = price
    execute_buy(address)
    print(f"[BUY] Token {address} @ {price:.5f} dengan buyer {buyer_count}")

def check_trailing_stop():
    for address in list(max_price_tracker.keys()):
        current_price = get_token_price(address)
        max_price = max_price_tracker[address]

        if current_price > max_price:
            max_price_tracker[address] = current_price
            print(f"[UPDATE] Harga tertinggi baru {current_price:.5f} untuk {address}")

        drop = (max_price - current_price) / max_price
        if drop >= 0.2:
            execute_sell(address)
            del max_price_tracker[address]

# ===== Main Loop (Otomatis) =====
def start_robot():
    while True:
        if robot_ready:
            dummy_token = "So11111111111111111111111111111111111111112"
            buy_token(dummy_token)
            check_trailing_stop()
        time.sleep(10)

threading.Thread(target=start_robot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
