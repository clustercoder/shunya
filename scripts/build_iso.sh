#!/bin/bash
set -e
 
ISO_NAME="shunya-wipe.iso"
WORKDIR="iso_builder"

BASE_ISO="ubuntu-24.04.3-desktop-amd64.iso"  # change if using another base
CUSTOM_ISO="iso/$ISO_NAME"

mkdir -p $WORKDIR
cd $WORKDIR

# Step 1: Download base ISO if missing
if [ ! -f $BASE_ISO ]; then
    echo "[*] Downloading Ubuntu base ISO..."
    wget https://releases.ubuntu.com/22.04/$BASE_ISO
fi

# Step 2: Extract ISO
mkdir -p extract iso
sudo mount -o loop $BASE_ISO extract
cp -r extract iso
sudo umount extract

# Step 3: Copy repo into ISO
mkdir -p iso/custom/shunya
cp -r ../wipe_tool ../requirements.txt ../scripts ../data iso/custom/shunya

# Step 4: Setup chroot environment
cp ../scripts/chroot_setup.sh iso/custom/
chmod +x iso/custom/chroot_setup.sh

# Step 5: Repack ISO
echo "[*] Building custom ISO..."
genisoimage -D -r -V "SHUNYA_WIPE" \
    -cache-inodes -J -l \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -o $CUSTOM_ISO iso/

echo "[+] ISO built: $CUSTOM_ISO"
