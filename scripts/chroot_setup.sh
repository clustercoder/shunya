#!/bin/bash
set -e
 
echo "[*] Setting up Shunya Wipe inside live ISO..."

apt-get update
apt-get install -y python3 python3-pip smartmontools util-linux

pip3 install -r /custom/shunya/requirements.txt

echo "[*] Shunya Wipe installed. Run with:"
echo "    python3 -m wipe_tool.cli --list"
 
# ===========================
# Auto-run Shunya CLI on boot
# ===========================

mkdir -p /etc/skel/.config/autostart

cat <<EOF > /etc/skel/.config/autostart/shunya-demo.desktop
[Desktop Entry]
Type=Application
Name=Shunya Wipe Demo
Exec=gnome-terminal --full-screen -- bash -c "python3 -m wipe_tool.cli --list; exec bash"
X-GNOME-Autostart-enabled=true
EOF

echo "[*] Autostart configured: Shunya CLI will run on boot"

