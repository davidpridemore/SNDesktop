import sys
import os
import platform
import socket
import uuid
import json
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

CONFIG_FILE = Path.home() / ".sn_notifier_config.json"
DEFAULT_INSTANCE = ""

def collect_machine_facts():
    u = platform.uname()
    return {
        "hostname": os.environ.get("COMPUTERNAME") or socket.gethostname(),
        "u_os": u.system,
        "os_version": u.release,
        "arch": u.machine
    }

def is_already_registered(session, instance, machine_id):
    try:
        resp = session.get(
            f"{instance}/api/226399/desktop_notify/register",
            params={"machine_id": machine_id},
            timeout=10
        )
        if resp.status_code == 200:
            res = resp.json().get("result", {})
            return bool(res.get("sys_id"))
    except Exception:
        pass
    return False

class InstallerApp:
    def __init__(self, root):
        self.auth = tk.StringVar(value="basic")
        self.instance_url = tk.StringVar(value=DEFAULT_INSTANCE)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.machine_id = str(uuid.uuid4())

        self.auth.trace_add('write', lambda *args: self.toggle_creds())
        self.build_ui(root)
        self.toggle_creds()

    def build_ui(self, root):
        root.title("SN Desktop Notifier Installer")
        tk.Label(root, text="ServiceNow Instance:").pack(pady=5)
        tk.Entry(root, textvariable=self.instance_url, width=40).pack()

        tk.Label(root, text="Authentication Method:").pack(pady=5)
        tk.Radiobutton(root, text="Basic Auth", variable=self.auth, value="basic").pack(anchor="w")
        tk.Radiobutton(root, text="SSO via OAuth", variable=self.auth, value="sso").pack(anchor="w")

        self.cred_frame = tk.Frame(root)
        tk.Label(self.cred_frame, text="Username:").grid(row=0, column=0, padx=5, pady=2)
        tk.Entry(self.cred_frame, textvariable=self.username, width=30).grid(row=0, column=1, padx=5, pady=2)
        tk.Label(self.cred_frame, text="Password:").grid(row=1, column=0, padx=5, pady=2)
        tk.Entry(self.cred_frame, textvariable=self.password, show="*", width=30).grid(row=1, column=1, padx=5, pady=2)
        self.cred_frame.pack(pady=5)

        ttk.Button(root, text="Install & Register", command=self.install).pack(pady=15)

    def toggle_creds(self):
        if self.auth.get() == "basic":
            self.cred_frame.pack(pady=5)
        else:
            self.cred_frame.pack_forget()

    def install(self):
        inst = self.instance_url.get().strip().rstrip("/")
        config = {"instance": inst, "machine_id": self.machine_id, "auth_type": self.auth.get()}

        session = requests.Session()
        if config["auth_type"] == "basic":
            user = self.username.get().strip()
            pwd = self.password.get()
            session.auth = (user, pwd)
            config["username"] = user
            config["password"] = pwd

        if is_already_registered(session, inst, self.machine_id):
            messagebox.showinfo("Registered", "Machine is already registered.")
        else:
            try:
                payload = {"machine_id": self.machine_id, **collect_machine_facts()}
                resp = session.post(f"{inst}/api/226399/desktop_notify/register", json=payload, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                messagebox.showerror("Registration Failed", str(e))
                return

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        messagebox.showinfo("Success", "Machine registration completed.")
        tk._default_root.quit()

def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
