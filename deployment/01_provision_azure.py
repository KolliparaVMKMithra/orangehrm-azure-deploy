#!/usr/bin/env python3
"""
OrangeHRM 5.8.1 - Azure Infrastructure Provisioning Script
=============================================================
This script creates all required Azure resources:
  - Resource Group
  - Virtual Network + Subnet
  - Network Security Group (ports 22, 80, 443)
  - Public IP Address
  - Network Interface
  - Ubuntu 22.04 Virtual Machine

Requirements:
  pip install azure-cli  (or run: az login first)
  Python 3.8+

Usage:
  python 01_provision_azure.py
"""

import subprocess
import json
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────
# CONFIGURATION — Edit these values
# ─────────────────────────────────────────────
CONFIG = {
    "resource_group":   "orangehrm-uk-rg",
    "location":         "uksouth",            # Change to your preferred region
    "vm_name":          "orangehrm-vm",
    "vm_size":          "Standard_B2s",      # 2 vCPU, 4GB RAM — good for small HR teams
    "admin_username":   "azureuser",
    "ssh_key_path":     "~/.ssh/id_rsa.pub", # Your SSH public key path
    "vnet_name":        "orangehrm-vnet",
    "subnet_name":      "orangehrm-subnet",
    "nsg_name":         "orangehrm-nsg",
    "public_ip_name":   "orangehrm-ip",
    "nic_name":         "orangehrm-nic",
    "os_disk_size":     "30",               # GB
    "image":            "Ubuntu2204",
}

def run(cmd, description, capture=True):
    """Run an Azure CLI command and return output."""
    print(f"\n⏳  {description}...")
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True
    )
    if result.returncode != 0:
        print(f"❌  ERROR: {result.stderr}")
        sys.exit(1)
    if capture and result.stdout.strip():
        print(f"✅  Done.")
    else:
        print(f"✅  Done.")
    return result.stdout.strip() if capture else ""

def run_json(cmd, description):
    """Run a command and parse JSON output."""
    output = run(cmd, description)
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}

def main():
    print("=" * 60)
    print("  OrangeHRM Azure Deployment — Infrastructure Provisioning")
    print("=" * 60)

    c = CONFIG
    import os
    c['ssh_key_path'] = os.path.expanduser(c['ssh_key_path']).replace('\\', '/')

    # 1. Check Azure CLI is logged in
    run("az account show", "Checking Azure login status")

    # 2. Create Resource Group
    run(
        f"az group create --name {c['resource_group']} --location {c['location']}",
        f"Creating resource group '{c['resource_group']}' in {c['location']}"
    )

    # 3. Create Virtual Network
    run(
        f"az network vnet create "
        f"--resource-group {c['resource_group']} "
        f"--name {c['vnet_name']} "
        f"--address-prefix 10.0.0.0/16 "
        f"--subnet-name {c['subnet_name']} "
        f"--subnet-prefix 10.0.1.0/24",
        "Creating virtual network and subnet"
    )

    # 4. Create Network Security Group
    run(
        f"az network nsg create "
        f"--resource-group {c['resource_group']} "
        f"--name {c['nsg_name']}",
        "Creating network security group"
    )

    # 5. Open ports: SSH (22), HTTP (80), HTTPS (443)
    for port, name, priority in [("22", "SSH", "1000"), ("80", "HTTP", "1010"), ("443", "HTTPS", "1020")]:
        run(
            f"az network nsg rule create "
            f"--resource-group {c['resource_group']} "
            f"--nsg-name {c['nsg_name']} "
            f"--name Allow-{name} "
            f"--protocol tcp "
            f"--priority {priority} "
            f"--destination-port-range {port} "
            f"--access Allow",
            f"Opening port {port} ({name})"
        )

    # 6. Create Public IP
    run(
        f"az network public-ip create "
        f"--resource-group {c['resource_group']} "
        f"--name {c['public_ip_name']} "
        f"--sku Standard "
        f"--allocation-method Static",
        "Creating static public IP address"
    )

    # 7. Create Network Interface
    run(
        f"az network nic create "
        f"--resource-group {c['resource_group']} "
        f"--name {c['nic_name']} "
        f"--vnet-name {c['vnet_name']} "
        f"--subnet {c['subnet_name']} "
        f"--network-security-group {c['nsg_name']} "
        f"--public-ip-address {c['public_ip_name']}",
        "Creating network interface card"
    )

    # 8. Create Virtual Machine (with automated fallback for VM sizes due to capacity restrictions)
    sizes_to_try = [
        c['vm_size'],  # Start with configured size (e.g. Standard_B2s)
        "Standard_B2ms",
        "Standard_DS1_v2",
        "Standard_D2s_v3",
        "Standard_D2s_v5"
    ]
    # Deduplicate while preserving order
    seen = set()
    sizes_to_try = [x for x in sizes_to_try if not (x in seen or seen.add(x))]

    vm_created = False
    for size in sizes_to_try:
        print(f"\n⏳  Attempting to create VM '{c['vm_name']}' with size '{size}'...")
        cmd = (
            f"az vm create "
            f"--resource-group {c['resource_group']} "
            f"--name {c['vm_name']} "
            f"--nics {c['nic_name']} "
            f"--image {c['image']} "
            f"--size {size} "
            f"--admin-username {c['admin_username']} "
            f"--ssh-key-values {c['ssh_key_path']} "
            f"--os-disk-size-gb {c['os_disk_size']} "
            f"--no-wait"
        )
        # We capture output to check for SkuNotAvailable or other errors if it fails
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅  VM creation initiated successfully with size '{size}'!")
            c['vm_size'] = size
            vm_created = True
            break
        else:
            print(f"❌  Size '{size}' failed. Error:")
            print(result.stderr.strip())
            print("Trying the next available size...")

    if not vm_created:
        print("\n❌  All VM size options failed. Please check Azure capacity or try another location.")
        sys.exit(1)

    # 9. Wait for VM to be ready
    print("\n⏳  Waiting for VM to be fully provisioned (up to 5 minutes)...")
    for i in range(30):
        result = subprocess.run(
            f"az vm show --resource-group {c['resource_group']} --name {c['vm_name']} --query provisioningState -o tsv",
            shell=True, capture_output=True, text=True
        )
        state = result.stdout.strip()
        if state == "Succeeded":
            print("✅  VM is ready!")
            break
        print(f"   Status: {state}... waiting ({(i+1)*10}s)")
        time.sleep(10)
    else:
        print("⚠️  VM may still be provisioning. Check Azure Portal.")

    # 10. Get Public IP
    ip_result = subprocess.run(
        f"az network public-ip show "
        f"--resource-group {c['resource_group']} "
        f"--name {c['public_ip_name']} "
        f"--query ipAddress -o tsv",
        shell=True, capture_output=True, text=True
    )
    public_ip = ip_result.stdout.strip()

    # 11. Save connection info
    info = {
        "public_ip": public_ip,
        "admin_username": c["admin_username"],
        "resource_group": c["resource_group"],
        "vm_name": c["vm_name"],
        "ssh_command": f"ssh {c['admin_username']}@{public_ip}"
    }
    with open("azure_vm_info.json", "w") as f:
        json.dump(info, f, indent=2)

    print("\n" + "=" * 60)
    print("  ✅  AZURE INFRASTRUCTURE READY!")
    print("=" * 60)
    print(f"  🌐 Public IP   : {public_ip}")
    print(f"  👤 SSH User    : {c['admin_username']}")
    print(f"  🔗 SSH Command : ssh {c['admin_username']}@{public_ip}")
    print(f"\n  ➡️  Next Step: Run   python 02_install_lamp.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
