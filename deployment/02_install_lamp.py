#!/usr/bin/env python3
"""
OrangeHRM 5.8.1 - LAMP Stack Installer on Azure VM
=====================================================
This script SSHes into your Azure VM and installs:
  - Apache 2.4
  - PHP 8.1 (with all required extensions)
  - MySQL 8.0
  - Composer (for OrangeHRM dependencies)

Requirements:
  pip install paramiko
  azure_vm_info.json must exist (from 01_provision_azure.py)

Usage:
  python 02_install_lamp.py
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
    print("📦 Installing paramiko...")
    os.system("pip install paramiko --quiet")
    import paramiko

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")   # Your private key
MYSQL_ROOT_PASSWORD = "OrangeHRM@Azure2025!"          # Change this!
MYSQL_DB_NAME = "orangehrm_db"
MYSQL_DB_USER = "orangehrm_user"
MYSQL_DB_PASSWORD = "OrangeDB@Pass2025!"              # Change this!

# LAMP installation bash script (runs on the remote VM)
LAMP_INSTALL_SCRIPT = f"""
#!/bin/bash
set -e

echo "========================================"
echo "  Step 1: System Update"
echo "========================================"
sudo apt-get update -y
sudo apt-get upgrade -y

echo "========================================"
echo "  Step 2: Install Apache"
echo "========================================"
sudo apt-get install -y apache2
sudo systemctl enable apache2
sudo systemctl start apache2

echo "========================================"
echo "  Step 3: Install PHP 8.1 + Extensions"
echo "========================================"
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:ondrej/php
sudo apt-get update -y

sudo apt-get install -y \\
    php8.1 \\
    php8.1-cli \\
    php8.1-common \\
    php8.1-mysql \\
    php8.1-zip \\
    php8.1-gd \\
    php8.1-mbstring \\
    php8.1-curl \\
    php8.1-xml \\
    php8.1-bcmath \\
    php8.1-intl \\
    php8.1-ldap \\
    php8.1-soap \\
    libapache2-mod-php8.1

sudo a2enmod php8.1
sudo a2enmod rewrite
sudo systemctl restart apache2

echo "========================================"
echo "  Step 4: Install MySQL 8.0"
echo "========================================"
# Non-interactive MySQL install
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password {MYSQL_ROOT_PASSWORD}"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password {MYSQL_ROOT_PASSWORD}"
sudo apt-get install -y mysql-server

sudo systemctl enable mysql
sudo systemctl start mysql

echo "========================================"
echo "  Step 5: Create OrangeHRM Database"
echo "========================================"
if sudo mysql -e "status" >/dev/null 2>&1; then
    echo "Configuring MySQL for the first time..."
    sudo mysql <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{MYSQL_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS {MYSQL_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '{MYSQL_DB_USER}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{MYSQL_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON {MYSQL_DB_NAME}.* TO '{MYSQL_DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
else
    echo "MySQL root password already configured. Authenticating with password..."
    sudo mysql -u root -p"{MYSQL_ROOT_PASSWORD}" <<SQL
CREATE DATABASE IF NOT EXISTS {MYSQL_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '{MYSQL_DB_USER}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{MYSQL_DB_PASSWORD}';
ALTER USER '{MYSQL_DB_USER}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{MYSQL_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON {MYSQL_DB_NAME}.* TO '{MYSQL_DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
fi

echo "✅ Database created: {MYSQL_DB_NAME}"
echo "✅ User created: {MYSQL_DB_USER}"

echo "========================================"
echo "  Step 6: PHP Configuration for OrangeHRM"
echo "========================================"
sudo sed -i 's/memory_limit = .*/memory_limit = 256M/' /etc/php/8.1/apache2/php.ini
sudo sed -i 's/upload_max_filesize = .*/upload_max_filesize = 64M/' /etc/php/8.1/apache2/php.ini
sudo sed -i 's/post_max_size = .*/post_max_size = 64M/' /etc/php/8.1/apache2/php.ini
sudo sed -i 's/max_execution_time = .*/max_execution_time = 300/' /etc/php/8.1/apache2/php.ini

echo "========================================"
echo "  Step 7: Create OrangeHRM Web Directory"
echo "========================================"
sudo mkdir -p /var/www/html/orangehrm
sudo chown -R www-data:www-data /var/www/html/orangehrm
sudo chmod -R 755 /var/www/html/orangehrm

echo "========================================"
echo "  Step 8: Configure Apache Virtual Host"
echo "========================================"
sudo tee /etc/apache2/sites-available/orangehrm.conf > /dev/null <<'APACHECONF'
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html/orangehrm

    <Directory /var/www/html/orangehrm>
        Options -Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${{APACHE_LOG_DIR}}/orangehrm-error.log
    CustomLog ${{APACHE_LOG_DIR}}/orangehrm-access.log combined
</VirtualHost>
APACHECONF

sudo a2dissite 000-default
sudo a2ensite orangehrm
sudo systemctl restart apache2

echo "========================================"
echo "  Step 9: Install unzip + curl utilities"
echo "========================================"
sudo apt-get install -y unzip curl wget git

echo "========================================"
echo "  ✅  LAMP STACK INSTALLATION COMPLETE!"
echo "========================================"
echo "  Apache  : $(apache2 -v | head -1)"
echo "  PHP     : $(php8.1 --version | head -1)"
echo "  MySQL   : $(mysql --version)"
echo ""
echo "  DB Name : {MYSQL_DB_NAME}"
echo "  DB User : {MYSQL_DB_USER}"
echo "  DB Pass : {MYSQL_DB_PASSWORD}"
"""

def ssh_connect(host, username, key_path, retries=5):
    """Connect to SSH with retry logic."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(retries):
        try:
            print(f"   Connecting to {host} (attempt {attempt+1}/{retries})...")
            client.connect(
                hostname=host,
                username=username,
                key_filename=key_path,
                timeout=30
            )
            print("✅  SSH connected!")
            return client
        except Exception as e:
            print(f"   ⚠️  {e} — retrying in 15s...")
            time.sleep(15)

    print("❌ Could not connect after multiple attempts.")
    sys.exit(1)

def run_remote(client, command, description):
    """Run a command on remote SSH host with live output."""
    print(f"\n⏳  {description}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True, timeout=600)

    # Stream output
    while True:
        line = stdout.readline()
        if not line:
            break
        print(f"   {line}", end="")

    exit_code = stdout.channel.recv_exit_status()
    if exit_code != 0:
        err = stderr.read().decode()
        print(f"❌  Command failed (exit {exit_code}): {err}")
        sys.exit(1)
    print(f"✅  Done.")

def main():
    print("=" * 60)
    print("  OrangeHRM Azure Deployment — LAMP Stack Installer")
    print("=" * 60)

    # Load VM info from previous step
    if not os.path.exists("azure_vm_info.json"):
        print("❌  azure_vm_info.json not found!")
        print("   Please run 01_provision_azure.py first.")
        sys.exit(1)

    with open("azure_vm_info.json") as f:
        vm_info = json.load(f)

    host = vm_info["public_ip"]
    username = vm_info["admin_username"]
    key_path = os.path.expanduser(SSH_KEY_PATH)

    print(f"  🌐 Target VM : {host}")
    print(f"  👤 User      : {username}")
    print(f"  🔑 SSH Key   : {key_path}")

    if not os.path.exists(key_path):
        print(f"❌  SSH key not found at {key_path}")
        print("   Generate one with: ssh-keygen -t rsa -b 4096")
        sys.exit(1)

    # Connect
    client = ssh_connect(host, username, key_path)

    # Write and execute LAMP script
    print("\n📤  Uploading install script to VM...")
    sftp = client.open_sftp()
    with sftp.open("/tmp/install_lamp.sh", "w") as f:
        f.write(LAMP_INSTALL_SCRIPT)
    sftp.close()

    run_remote(client, "chmod +x /tmp/install_lamp.sh && bash /tmp/install_lamp.sh", 
               "Installing LAMP stack (this takes 5-10 minutes)...")

    # Save DB config for next step
    db_config = {
        "host": "localhost",
        "db_name": MYSQL_DB_NAME,
        "db_user": MYSQL_DB_USER,
        "db_password": MYSQL_DB_PASSWORD,
        "mysql_root_password": MYSQL_ROOT_PASSWORD
    }
    with open("db_config.json", "w") as f:
        json.dump(db_config, f, indent=2)

    client.close()

    print("\n" + "=" * 60)
    print("  ✅  LAMP STACK READY!")
    print("=" * 60)
    print(f"  🗄️  Database : {MYSQL_DB_NAME}")
    print(f"  👤 DB User  : {MYSQL_DB_USER}")
    print(f"\n  ➡️  Next Step: Run   python 03_deploy_orangehrm.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
