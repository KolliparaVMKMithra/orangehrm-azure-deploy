#!/usr/bin/env python3
"""
OrangeHRM 5.8.1 - HTTPS / SSL Setup (Optional but Recommended)
================================================================
This script sets up Let's Encrypt SSL on your Azure VM using Certbot.

PREREQUISITE: You need a domain name pointing to your VM's IP.
  - Go to your domain registrar (GoDaddy, Namecheap, etc.)
  - Add an A record: yourdomain.com → <your VM public IP>
  - Wait 5-30 min for DNS propagation

If you don't have a domain, skip this script — HTTP will still work.

Usage:
  python 04_setup_ssl.py
"""

import json
import os
import sys
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


def ssh_connect(host, username, key_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for attempt in range(5):
        try:
            client.connect(hostname=host, username=username,
                           key_filename=key_path, timeout=30)
            return client
        except Exception as e:
            print(f"   ⚠️  Retry {attempt+1}: {e}")
            time.sleep(10)
    sys.exit(1)


def run_remote(client, command, description, allow_fail=False):
    print(f"\n⏳  {description}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True, timeout=300)
    while True:
        line = stdout.readline()
        if not line:
            break
        print(f"   {line}", end="")
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0 and not allow_fail:
        err = stderr.read().decode()
        print(f"❌  Failed: {err}")
        sys.exit(1)
    print("✅  Done.")


def main():
    print("=" * 60)
    print("  OrangeHRM — HTTPS / SSL Setup")
    print("=" * 60)

    if not os.path.exists("azure_vm_info.json"):
        print("❌  azure_vm_info.json not found. Run step 1 first.")
        sys.exit(1)

    with open("azure_vm_info.json") as f:
        vm_info = json.load(f)

    host = vm_info["public_ip"]
    username = vm_info["admin_username"]

    print(f"\n  🌐 VM IP: {host}")
    domain = input("\n  Enter your domain name (e.g. hrm.mycompany.com): ").strip()
    email = input("  Enter your email for SSL certificate alerts: ").strip()

    if not domain or not email:
        print("❌  Domain and email are required.")
        sys.exit(1)

    print(f"\n  🔒 Setting up SSL for: {domain}")

    client = ssh_connect(host, username, SSH_KEY_PATH)

    # Install Certbot
    run_remote(client, "sudo apt-get install -y certbot python3-certbot-apache",
               "Installing Certbot...")

    # Update Apache VirtualHost with ServerName
    update_vhost = f"""
sudo sed -i 's/ServerAdmin webmaster@localhost/ServerAdmin {email}/' /etc/apache2/sites-available/orangehrm.conf
sudo sed -i '/ServerAdmin/a\\    ServerName {domain}' /etc/apache2/sites-available/orangehrm.conf
sudo systemctl reload apache2
"""
    run_remote(client, update_vhost, "Updating Apache config with domain name...")

    # Run Certbot
    certbot_cmd = (
        f"sudo certbot --apache "
        f"--non-interactive "
        f"--agree-tos "
        f"--email {email} "
        f"-d {domain} "
        f"--redirect"
    )
    run_remote(client, certbot_cmd, "Obtaining and installing SSL certificate...")

    # Test auto-renewal
    run_remote(client, "sudo certbot renew --dry-run",
               "Testing certificate auto-renewal...", allow_fail=True)

    client.close()

    print("\n" + "=" * 60)
    print("  ✅  HTTPS SETUP COMPLETE!")
    print("=" * 60)
    print(f"  🔒 Secure URL : https://{domain}/")
    print(f"  🔄 Cert renews automatically every 90 days")
    print("=" * 60)


if __name__ == "__main__":
    main()
