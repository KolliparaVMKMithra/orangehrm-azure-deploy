#!/usr/bin/env python3
"""
OrangeHRM 5.8.1 - Upload & Deploy to Azure VM
===============================================
This script:
  1. Zips your local OrangeHRM-5.8.1 folder
  2. Uploads it to the Azure VM via SCP/SFTP
  3. Extracts and sets correct permissions
  4. Runs pre-flight checks

Requirements:
  pip install paramiko
  azure_vm_info.json (from step 1)
  db_config.json     (from step 2)

Usage:
  python 03_deploy_orangehrm.py
"""

import json
import os
import sys
import zipfile
import time
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import paramiko
except ImportError:
    os.system("pip install paramiko --quiet")
    import paramiko

# ─────────────────────────────────────────────
# CONFIGURATION — Edit the path to your OrangeHRM
# ─────────────────────────────────────────────
# Path to your extracted OrangeHRM-5.8.1 folder on YOUR LOCAL machine
LOCAL_ORANGEHRM_PATH = "C:/Users/DELL/Downloads/orangehrm-5.8.1/orangehrm-5.8.1"   # Adjust this to your actual path!
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_WEB_DIR = "/var/www/html/orangehrm"


def ssh_connect(host, username, key_path, retries=5):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for attempt in range(retries):
        try:
            print(f"   Connecting (attempt {attempt+1}/{retries})...")
            client.connect(hostname=host, username=username,
                           key_filename=key_path, timeout=30)
            print("✅  SSH connected!")
            return client
        except Exception as e:
            print(f"   ⚠️  {e} — retrying in 10s...")
            time.sleep(10)
    print("❌ Could not connect.")
    sys.exit(1)


def run_remote(client, command, description, allow_fail=False):
    print(f"\n⏳  {description}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True, timeout=300)
    output = []
    while True:
        line = stdout.readline()
        if not line:
            break
        output.append(line.strip())
        print(f"   {line}", end="")
    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0 and not allow_fail:
        err = stderr.read().decode()
        print(f"❌  Command failed: {err}")
        sys.exit(1)
    print(f"✅  Done.")
    return "\n".join(output)


def zip_orangehrm(local_path):
    """Zip the OrangeHRM folder for upload."""
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "orangehrm_upload.zip"))
    print(f"\n📦  Zipping {local_path} → {zip_path} ...")

    if not os.path.exists(local_path):
        print(f"❌  OrangeHRM folder not found: {local_path}")
        print("   Please set LOCAL_ORANGEHRM_PATH correctly in this script.")
        sys.exit(1)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(local_path):
            # Skip node_modules and .git if present (keep vendor!)
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git"]]
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, os.path.dirname(local_path))
                zf.write(filepath, arcname)

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"✅  Zip created: {size_mb:.1f} MB")
    return zip_path


def upload_file(client, local_path, remote_path):
    """Upload file via SFTP with progress."""
    print(f"\n📤  Uploading to VM...")
    sftp = client.open_sftp()
    file_size = os.path.getsize(local_path)
    uploaded = [0]

    def progress(sent, total):
        pct = (sent / total) * 100
        print(f"\r   Progress: {pct:.1f}% ({sent/1024/1024:.1f}/{total/1024/1024:.1f} MB)", end="")

    sftp.put(local_path, remote_path, callback=progress)
    sftp.close()
    print(f"\n✅  Upload complete!")


def main():
    print("=" * 60)
    print("  OrangeHRM Azure Deployment — Upload & Configure")
    print("=" * 60)

    # Load configs
    for fname in ["azure_vm_info.json", "db_config.json"]:
        if not os.path.exists(fname):
            print(f"❌  {fname} not found. Run previous steps first.")
            sys.exit(1)

    with open("azure_vm_info.json") as f:
        vm_info = json.load(f)
    with open("db_config.json") as f:
        db = json.load(f)

    host = vm_info["public_ip"]
    username = vm_info["admin_username"]

    print(f"  🌐 Target VM : {host}")
    print(f"  📁 Source    : {LOCAL_ORANGEHRM_PATH}")
    print(f"  🗄️  Database  : {db['db_name']}")

    # Step 1: Zip the OrangeHRM folder
    zip_path = zip_orangehrm(LOCAL_ORANGEHRM_PATH)

    # Step 2: SSH connect
    client = ssh_connect(host, username, SSH_KEY_PATH)

    # Step 3: Upload zip
    upload_file(client, zip_path, "/tmp/orangehrm_upload.zip")

    # Step 4: Extract on remote
    deploy_script = f"""
set -e

echo "Extracting OrangeHRM..."
sudo rm -rf {REMOTE_WEB_DIR}/*
sudo unzip -q /tmp/orangehrm_upload.zip -d /tmp/orangehrm_extracted/

# Find the actual orangehrm folder inside the zip
EXTRACTED_DIR=$(ls /tmp/orangehrm_extracted/)
echo "Extracted folder: $EXTRACTED_DIR"

sudo cp -r /tmp/orangehrm_extracted/$EXTRACTED_DIR/. {REMOTE_WEB_DIR}/

echo "Creating writable directories..."
sudo mkdir -p {REMOTE_WEB_DIR}/src/cache
sudo mkdir -p {REMOTE_WEB_DIR}/src/log  
sudo mkdir -p {REMOTE_WEB_DIR}/web/uploads
sudo mkdir -p {REMOTE_WEB_DIR}/lib/confs
sudo mkdir -p {REMOTE_WEB_DIR}/lib/logs

echo "Setting permissions..."
sudo chown -R www-data:www-data {REMOTE_WEB_DIR}
sudo chmod -R 755 {REMOTE_WEB_DIR}
sudo chmod -R 777 {REMOTE_WEB_DIR}/src/cache
sudo chmod -R 777 {REMOTE_WEB_DIR}/src/log
sudo chmod -R 777 {REMOTE_WEB_DIR}/web/uploads
sudo chmod -R 777 {REMOTE_WEB_DIR}/lib/confs
sudo chmod -R 777 {REMOTE_WEB_DIR}/lib/logs

echo "Cleaning up temp files on VM..."
sudo rm -rf /tmp/orangehrm_extracted /tmp/orangehrm_upload.zip

echo "✅ OrangeHRM files deployed to {REMOTE_WEB_DIR}"
ls -la {REMOTE_WEB_DIR} | head -20
"""
    run_remote(client, deploy_script, "Extracting and deploying OrangeHRM files...")

    # Step 5: Configure .htaccess / check mod_rewrite
    run_remote(client,
        "sudo a2enmod rewrite && sudo systemctl restart apache2",
        "Enabling Apache mod_rewrite")

    # Step 6: Pre-flight PHP check
    preflight = f"""
echo "=== PHP Version ==="
php8.1 --version

echo ""
echo "=== Required PHP Extensions ==="
for ext in pdo pdo_mysql mysqli mbstring xml zip curl gd intl; do
    php8.1 -m | grep -q $ext && echo "✅ $ext" || echo "❌ MISSING: $ext"
done

echo ""
echo "=== MySQL Connectivity ==="
mysql -u {db['db_user']} -p'{db['db_password']}' -e "SHOW DATABASES;" {db['db_name']} && echo "✅ DB connection OK" || echo "❌ DB connection failed"

echo ""
echo "=== Apache Status ==="
sudo systemctl is-active apache2

echo ""
echo "=== Web Directory ==="
ls -la {REMOTE_WEB_DIR} | head -10
"""
    run_remote(client, preflight, "Running pre-flight checks...")

    client.close()

    print("\n" + "=" * 60)
    print("  ✅  ORANGEHRM FILES DEPLOYED!")
    print("=" * 60)
    print(f"  🌐 Web Installer URL : http://{host}/")
    print(f"  🗄️  DB Host           : localhost")
    print(f"  🗄️  DB Name           : {db['db_name']}")
    print(f"  🗄️  DB User           : {db['db_user']}")
    print(f"  🗄️  DB Password       : {db['db_password']}")
    print(f"\n  ➡️  Next Step: Open the URL above in your browser")
    print(f"             and complete the OrangeHRM web installer!")
    print("=" * 60)

    # Save installer info
    with open("installer_info.json", "w") as f:
        json.dump({
            "web_installer_url": f"http://{host}/",
            "db_host": "localhost",
            "db_name": db["db_name"],
            "db_user": db["db_user"],
            "db_password": db["db_password"]
        }, f, indent=2)
    print("\n  📋 Installer details saved to installer_info.json")

    # Clean up local zip file
    if os.path.exists(zip_path):
        print(f"\n🧹  Cleaning up local zip: {zip_path}")
        os.remove(zip_path)

if __name__ == "__main__":
    main()
