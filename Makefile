# Makefile for Shunya Wipe Tool
 
.PHONY: setup run list clean iso

setup:
	@echo "[*] Installing dependencies..."
	sudo apt update
	sudo apt install -y python3 python3-pip smartmontools util-linux genisoimage squashfs-tools
	pip3 install -r requirements.txt

list:
	python3 -m wipe_tool.cli --list

run:
	python3 -m wipe_tool.cli --device /dev/sda --method standard

iso:
	bash scripts/build_iso.sh

clean:
	rm -rf iso_builder/build iso_builder/casper iso_builder/iso
