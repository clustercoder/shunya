# wipe_tool/certificate.py

import json
import os
import hashlib
from datetime import datetime
from wipe_tool.wipe_logger import LOG_DIR
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode

CERT_DIR = os.path.join(os.path.dirname(__file__), "../data/certificates")
os.makedirs(CERT_DIR, exist_ok=True)

# ===========================
# Generate or load key pair
# ===========================
KEY_FILE = os.path.join(CERT_DIR, "private_key.pem")
if not os.path.exists(KEY_FILE):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"[+] Generated new private key at {KEY_FILE}")
else:
    with open(KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

public_key = private_key.public_key()

# ===========================
# Core Certificate Functions
# ===========================
def generate_certificate(wipe_log_path: str):
    # Load wipe log
    with open(wipe_log_path, "r") as f:
        log_data = json.load(f)

    # Compute SHA256 hash of log data
    log_bytes = json.dumps(log_data, sort_keys=True).encode()
    log_hash = hashlib.sha256(log_bytes).hexdigest()

    # Sign the hash
    signature = private_key.sign(
        log_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Create certificate JSON
    certificate = {
        "device": log_data["drive_path"],
        "wipe_method": log_data["method"],
        "start_time": log_data["start_time"],
        "end_time": log_data["end_time"],
        "nonce": log_data["nonce"],
        "log_hash": log_hash,
        "signature": signature.hex(),
        "generated_at": datetime.utcnow().isoformat()
    }

    # Save JSON
    json_path = os.path.join(CERT_DIR, f"certificate_{log_data['nonce']}.json")
    with open(json_path, "w") as f:
        json.dump(certificate, f, indent=4)
    print(f"[+] Certificate JSON saved: {json_path}")

    # Generate PDF certificate
    pdf_path = os.path.join(CERT_DIR, f"certificate_{log_data['nonce']}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Certificate of Data Destruction")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Device: {log_data['drive_path']}")
    c.drawString(50, height - 120, f"Wipe Method: {log_data['method']}")
    c.drawString(50, height - 140, f"Start Time: {log_data['start_time']}")
    c.drawString(50, height - 160, f"End Time: {log_data['end_time']}")
    c.drawString(50, height - 180, f"Nonce: {log_data['nonce']}")
    c.drawString(50, height - 200, f"Log Hash: {log_hash}")
    c.drawString(50, height - 220, f"Generated At: {certificate['generated_at']}")

    # Add QR code linking to the log hash (for demo verification)
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(f"SHA256:{log_hash}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_path = os.path.join(CERT_DIR, f"certificate_qr_{log_data['nonce']}.png")
    img.save(img_path)
    c.drawImage(img_path, 50, height - 400, width=150, height=150)

    c.showPage()
    c.save()
    print(f"[+] Certificate PDF saved: {pdf_path}")

    return json_path, pdf_path, img_path

 
# ===========================
# Demo
# ===========================
if __name__ == "__main__":
    # Pick the last wipe log in logs folder
    logs = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".json")])
    if not logs:
        print("[!] No wipe logs found. Run a wipe first.")
    else:
        last_log = os.path.join(LOG_DIR, logs[-1])
        generate_certificate(last_log)
