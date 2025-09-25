# wipe_tool/blockchain_stub.py

"""
Lightweight blockchain simulation.
Each certificate JSON is appended as a "block" in a local chain.
""" 

import os
import json
import hashlib

CHAIN_FILE = os.path.join(os.path.dirname(__file__), "../data/blockchain.json")


def append_block(cert_json_path: str):
    with open(cert_json_path, "r") as f:
        cert = json.load(f)

    if os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, "r") as f:
            chain = json.load(f)
    else:
        chain = []

    prev_hash = chain[-1]["hash"] if chain else "0" * 64
    block_data = json.dumps(cert, sort_keys=True).encode()
    block_hash = hashlib.sha256(block_data + prev_hash.encode()).hexdigest()

    block = {
        "cert": cert,
        "prev_hash": prev_hash,
        "hash": block_hash,
    }

    chain.append(block)
    with open(CHAIN_FILE, "w") as f:
        json.dump(chain, f, indent=4)

    print(f"[+] Block added to local blockchain: {block_hash}")
