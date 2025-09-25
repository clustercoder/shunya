# wipe_tool/cli.py
from wipe_tool import safety
import argparse
from wipe_tool import drive_detect, wipe_methods, certificate, health_check

def banner(): 
    print("=" * 60)
    print("     SHUNYA SECURE WIPE - LIVE DEMO EDITION")
    print("=" * 60)

def main():
    banner()

    parser = argparse.ArgumentParser(description="Secure Data Wipe MVP")
    parser.add_argument("--list", action="store_true", help="List available drives")
    parser.add_argument("--device", type=str, help="Device to wipe (e.g., /dev/sdb)")
    parser.add_argument(
        "--method",
        type=str,
        choices=["standard", "quantum", "eco"],
        help="Wipe method",
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Safe demo mode: write to a simulated file instead of a real device",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run: show commands without executing (additional safety)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a destructive wipe even if safety checks warn (use with extreme caution)",
    )

    args = parser.parse_args()

    if args.list:
        drives = drive_detect.list_drives()
        print("\nAvailable Drives:")
        for d in drives:
            print(f"{d['name']} - {d['size']} - {d['type']}")
        return

    if args.device and args.method:
        print(f"[+] Starting wipe on {args.device} using {args.method} method")

        # Safety check (skip if safe-demo)
        if not args.safe:
            try:
                safety.safety_check(args.device, force=args.force)
            except RuntimeError as e:
                print(f"\n[!] SAFETY CHECK FAILED:\n{e}\n")
                return

        # Run wipe -> returns path to wipe log
        wipe_log_path = wipe_methods.run_wipe(
            args.device, args.method, dry_run=args.dry_run, safe_demo=args.safe, force=args.force
        )

        print("[+] Generating certificate...")
        json_cert, pdf_cert, qr_path = certificate.generate_certificate(wipe_log_path)
        print(f"[+] Certificate JSON: {json_cert}")
        print(f"[+] Certificate PDF: {pdf_cert}")
        print(f"[+] QR Code: {qr_path}")

        print("[+] Running post-wipe health check...")
        status = health_check.run_smart_test(args.device) if not args.safe else "SKIPPED (safe demo)"
        print(f"[+] Disk Health: {status}")

    else:
        parser.print_help()



if __name__ == "__main__":
    banner()
    main()