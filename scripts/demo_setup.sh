#!/bin/bash
set -e
 
echo "[*] Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip smartmontools util-linux

echo "[*] Installing Python packages..."
pip3 install -r requirements.txt

echo "[*] Setup complete. Run demo with:"
echo "    python3 -m wipe_tool.cli --list"
