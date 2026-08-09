#!/usr/bin/env python3
"""
Example Script: Automated MUD Exploration Session
Shows how an AI agent or script imports mud_client to connect, inspect player state, and explore rooms.
"""

import sys
import os
import time

# Ensure parent directory is in sys.path to import mud_client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from mud_client import MUDClient

def run_exploration():
    host = "127.0.0.1"
    port = 4000
    user = "dummy"
    password = "helloworld"

    print(f"[+] Initializing connection to {host}:{port}...")
    client = MUDClient(host=host, port=port)

    # 1. Login
    success, log = client.login(username=user, password=password)
    if not success:
        print(f"[-] Login failed. Banner/Log:\n{log}")
        return

    print(f"[+] Login successful as '{user}'. Inspecting initial state...")

    # 2. Check initial character state
    status = client.execute_commands(["score", "equipment", "inventory", "look"])
    for item in status["results"]:
        print(f"\n--- Output for '{item['command']}' ---")
        print(item["output"])

    # 3. Explore adjacent exits
    print("\n[+] Checking available exits...")
    exits_info = client.execute_commands(["exits"])
    print(exits_info["results"][0]["output"])

    # 4. Safe disconnect
    client.execute_commands(["quit"])
    client.close()
    print("[+] Exploration completed and logged out.")

if __name__ == "__main__":
    run_exploration()
