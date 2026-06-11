#!/usr/bin/env python3
"""
OrangeHRM 5.8.1 - Health Check & Diagnostics
==============================================
Run this anytime to check:
  - VM status on Azure
  - Apache / MySQL service status
  - PHP extension availability
  - OrangeHRM file permissions
  - Database connectivity

Usage:
  python 05_health_check.py
"""

import json
import os
import sys
import subprocess
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import paramiko
except ImportError:
    os.system("pip install paramiko --quiet")
    import paramiko

SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_WEB_DIR = "/var/www/html/orangehrm"


def run_local(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def ssh_connect(host, username, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username,
                       key_filename=key_path, timeout=15)
        return client
    except Exception as e:
        print(f"❌  SSH failed: {e}")
        return None


def run_remote(client, command):
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err


def check_remote(client, command, label):
    out, err = run_remote(client, command)
    status = "✅" if out and "active" in out.lower() or out else "⚠️ "
    print(f"  {status} {label}: {out or err or 'no output'}")
    return out


def main():
    print("=" * 60)
    print("  OrangeHRM — Health Check & Diagnostics")
    print("=" * 60)

    if not os.path.exists("azure_vm_info.json"):
        print("❌  azure_vm_info.json not found.")
        sys.exit(1)

    with open("azure_vm_info.json") as f:
        vm_info = json.load(f)

    with open("db_config.json") if os.path.exists("db_config.json") else open(os.devnull) as f:
        db = json.load(f) if os.path.exists("db_config.json") else {}

    host = vm_info["public_ip"]
    username = vm_info["admin_username"]
    rg = vm_info["resource_group"]
    vm_name = vm_info["vm_name"]

    print(f"\n  🌐 VM IP     : {host}")
    print(f"  🏷️  VM Name  : {vm_name}")
    print(f"  📦 RG       : {rg}")

    # ── Azure VM Status
    print("\n──────────────────────────────────────")
    print("  AZURE VM STATUS")
    print("──────────────────────────────────────")
    vm_state = run_local(
        f"az vm show --resource-group {rg} --name {vm_name} "
        f"--show-details --query powerState -o tsv 2>/dev/null"
    )
    state_icon = "✅" if "running" in vm_state.lower() else "❌"
    print(f"  {state_icon} Power State : {vm_state or 'Unknown (check Azure Portal)'}")

    # ── SSH & Service Checks
    print("\n──────────────────────────────────────")
    print("  VM SERVICE STATUS (via SSH)")
    print("──────────────────────────────────────")
    client = ssh_connect(host, username, SSH_KEY_PATH)
    if not client:
        print("❌  Cannot SSH into VM. Check your key or VM status.")
        return

    check_remote(client, "sudo systemctl is-active apache2", "Apache")
    check_remote(client, "sudo systemctl is-active mysql", "MySQL")
    check_remote(client, "php8.1 --version | head -1", "PHP Version")

    # ── PHP Extensions
    print("\n──────────────────────────────────────")
    print("  PHP EXTENSIONS")
    print("──────────────────────────────────────")
    required_exts = ["pdo", "pdo_mysql", "mysqli", "mbstring", "xml", "zip", "curl", "gd", "intl"]
    for ext in required_exts:
        out, _ = run_remote(client, f"php8.1 -m | grep -i {ext}")
        icon = "✅" if out else "❌"
        print(f"  {icon} {ext}")

    # ── File Permissions
    print("\n──────────────────────────────────────")
    print("  FILE PERMISSIONS")
    print("──────────────────────────────────────")
    out, _ = run_remote(client, f"ls -la {REMOTE_WEB_DIR} | head -15")
    print(f"  {out or 'Directory not found'}")

    # ── Database Connectivity
    if db:
        print("\n──────────────────────────────────────")
        print("  DATABASE CONNECTIVITY")
        print("──────────────────────────────────────")
        db_user = db['db_user']
        db_password = db['db_password']
        db_name = db['db_name']
        db_test_cmd = (
            f"mysql -u {db_user} -p'{db_password}' "
            f"-e 'SELECT COUNT(*) as tables FROM information_schema.tables "
            f"WHERE table_schema=\"{db_name}\";' 2>/dev/null"
        )
        out, err = run_remote(client, db_test_cmd)
        if out:
            print(f"  ✅ Database connected: {db['db_name']}")
            print(f"     {out}")
        else:
            print(f"  ❌ DB connection failed: {err}")

    # ── Disk Usage
    print("\n──────────────────────────────────────")
    print("  DISK USAGE")
    print("──────────────────────────────────────")
    out, _ = run_remote(client, "df -h /")
    print(f"  {out}")

    # ── OrangeHRM URL
    print("\n──────────────────────────────────────")
    print("  ACCESS URLS")
    print("──────────────────────────────────────")
    print(f"  🌐 OrangeHRM : http://{host}/")
    if os.path.exists("installer_info.json"):
        with open("installer_info.json") as f:
            info = json.load(f)
        if "web_installer_url" in info:
            print(f"  🔧 Installer : {info['web_installer_url']}")

    client.close()
    print("\n" + "=" * 60)
    print("  Health check complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
