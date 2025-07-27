import sys, os

# --- Fix win10toast_click pkg_resources issue when frozen ---
try:
    import pkg_resources
    if getattr(sys, "frozen", False):
        pkg_resources.resource_filename = lambda *args, **kwargs: os.path.join(
            sys._MEIPASS, "win10toast_click", "toast.wav"
        )
except Exception:
    pass
# ------------------------------------------------------------

import time
import json
import requests
import logging
import webbrowser
from pathlib import Path
from win10toast_click import ToastNotifier

# ------------ config ------------
CONFIG_FILE = Path.home() / ".sn_notifier_config.json"
POLL_INTERVAL = 10  # seconds
FULL_MESSAGE_LOG = Path.home() / "sn_full_messages.log"

logging.basicConfig(
    filename=Path.home() / "sn_notifier.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

toaster = ToastNotifier()

# ------------ helpers ------------

def log_full_message(title, message, url):
    try:
        with open(FULL_MESSAGE_LOG, "a", encoding="utf-8") as f:
            f.write(
                f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {title}\nURL: {url}\n"
                f"{message}\n{'-'*80}\n"
            )
    except Exception as e:
        logging.error(f"Failed to log full message: {e}")

def show_notification(title, message, url):
    logging.info(f"Notification → {title} ({url})")
    print(f"[NOTIFY] {title} -> {url}")
    log_full_message(title, message, url)

    try:
        toaster.show_toast(
            title=title,
            msg="Click to open in ServiceNow",
            duration=10,
            threaded=True,
            callback_on_click=lambda: webbrowser.open(url)
        )
    except Exception as e:
        logging.error(f"Notification Error: {e}")
        print(f"[ERROR] Notification Error: {e}")

def load_config():
    if not CONFIG_FILE.exists():
        raise RuntimeError("Configuration not found. Run installer.py first.")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------ poll loop ------------

def poll(instance, auth, machine_id):
    url = f"{instance}/api/226399/desktop_notify/poll"
    params = {"machine_id": machine_id}
    headers = {"Accept": "application/json", "User-Agent": "SN Desktop Notifier"}

    logging.info(f"Starting poller for {instance} (machine_id={machine_id})")
    print(f"[INFO] Polling {instance} every {POLL_INTERVAL}s for machine_id={machine_id}")

    try:
        while True:
            try:
                r = requests.get(url, auth=auth, params=params, headers=headers, timeout=10)
                r.raise_for_status()
                data = r.json()
                notes = data.get("result", {}).get("notifications", [])
                if notes:
                    for note in notes:
                        title = note.get("title", "Notice")
                        msg = note.get("message", "")
                        target_url = note.get("url", instance)
                        show_notification(title, msg, target_url)
            except Exception as e:
                show_notification("Polling Error", str(e), instance)
                logging.error(f"Polling Error: {e}")

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("[INFO] Poller stopped by user.")
        logging.info("Poller stopped by user.")

# ------------ main ------------

if __name__ == "__main__":
    config = load_config()
    auth = (config["username"], config["password"]) if config["auth_type"] == "basic" else None
    poll(config["instance"], auth, config["machine_id"])
