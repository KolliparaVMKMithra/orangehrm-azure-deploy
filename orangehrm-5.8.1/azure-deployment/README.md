# OrangeHRM Azure Deployment Scripts

## Overview

This directory contains Python scripts for deploying OrangeHRM 5.8.1 to Microsoft Azure with complete automation, including resource provisioning, database setup, application building, and deployment.

## 📁 Files in This Directory

### Core Scripts

| File | Purpose | Run Time |
|------|---------|----------|
| `deployment_orchestrator.py` | **Main script** - coordinates entire deployment | 30-45 min |
| `pre_deployment_checks.py` | Validates environment & prerequisites | 2-3 min |
| `azure_setup.py` | Creates Azure resources | 5-10 min |
| `database_setup.py` | Sets up database & migrations | 5-10 min |
| `build_and_deploy.py` | Builds app & deploys to Azure | 10-15 min |

### Configuration

| File | Purpose |
|------|---------|
| `config.py` | Configuration management & environment variables |
| `.env.example` | Template for environment variables |
| `.env` | Your actual configuration (created from template) |
| `requirements.txt` | Python dependencies |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `QUICK_START.md` | Fast 5-step deployment guide |
| `DEPLOYMENT_GUIDE.md` | Comprehensive step-by-step guide |

---

## 🚀 Quick Start

### 1. Install Prerequisites

```bash
# Python 3.8+, Azure CLI, PHP 8.0+, Node.js 16+, Composer
# See DEPLOYMENT_GUIDE.md for detailed installation
```

### 2. Setup Configuration

```bash
cd azure-deployment
copy .env.example .env
# Edit .env with your Azure credentials and resource names
```

### 3. Run Full Deployment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run full deployment
python deployment_orchestrator.py
```

### 4. Access Your Application

```
https://your-app-service-name.azurewebsites.net
```

**For detailed steps, see [QUICK_START.md](QUICK_START.md)**

---

## 📋 Prerequisites

### System Requirements

- **OS:** Windows, macOS, or Linux
- **Python:** 3.8 or higher
- **Disk Space:** 5-10 GB
- **Memory:** 4 GB RAM minimum

### Required Software

- ✅ Python 3.8+
- ✅ Azure CLI 2.0+
- ✅ Git 2.0+
- ✅ PHP 8.0+ (with required extensions)
- ✅ Node.js 16+ & npm
- ✅ Composer (PHP package manager)

### Azure Requirements

- ✅ Active Azure Subscription
- ✅ Sufficient credits/budget (~$35-70/month)
- ✅ Service Principal with Contributor role

---

## 🔧 Configuration

### Environment Variables (.env)

Copy `.env.example` to `.env` and fill in:

```ini
# Azure Authentication
AZURE_SUBSCRIPTION_ID=xxx
AZURE_TENANT_ID=xxx
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx

# Resource Names
RESOURCE_GROUP_NAME=orangehrm-rg
APP_SERVICE_NAME=orangehrm-app
DB_SERVER_NAME=orangehrm-mysql
STORAGE_ACCOUNT_NAME=orangehrmsa

# Database
DB_ADMIN_PASSWORD=StrongPassword123!@

# Other settings
AZURE_LOCATION=eastus
PHP_VERSION=8.2
NODE_VERSION=18
```

### Creating Service Principal

```bash
az login
az ad sp create-for-rbac --name orangehrm-deployer \
  --role Contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>
```

Output contains:
- `appId` → AZURE_CLIENT_ID
- `password` → AZURE_CLIENT_SECRET
- `tenant` → AZURE_TENANT_ID

---

## ▶️ Running Deployment

### Option 1: Full Automated Deployment (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run orchestrator (does everything)
python deployment_orchestrator.py
```

**This will:**
1. Validate environment
2. Create Azure resources
3. Setup database
4. Build application
5. Deploy to Azure

### Option 2: Run Steps Individually

```bash
# Step 1: Validate environment
python pre_deployment_checks.py

# Step 2: Create Azure resources
python azure_setup.py

# Step 3: Setup database
python database_setup.py

# Step 4: Build and deploy
python build_and_deploy.py
```

### Option 3: Run Specific Component

```bash
# Only deploy (assumes resources exist)
python build_and_deploy.py

# Only setup database
python database_setup.py
```

---

## 📊 Deployment Process

### Step 1: Environment Validation
```
✓ Checks Python version
✓ Checks Azure CLI
✓ Checks required tools
✓ Validates application structure
✓ Validates Azure configuration
```

### Step 2: Azure Resource Setup
```
✓ Creates Resource Group
✓ Creates App Service Plan
✓ Creates App Service
✓ Creates MySQL Database
✓ Configures Firewall Rules
✓ Creates Storage Account
```

### Step 3: Database Setup
```
✓ Waits for database readiness
✓ Creates database
✓ Configures connection
✓ Runs migrations
✓ Seeds initial data
```

### Step 4: Application Build
```
✓ Installs PHP dependencies (Composer)
✓ Installs Node dependencies (npm)
✓ Builds Vue.js frontend
✓ Creates deployment package (ZIP)
```

### Step 5: Deploy to Azure
```
✓ Uploads package to storage
✓ Deploys to App Service
✓ Configures app settings
```

---

## 📁 What Gets Deployed

```
deployment/
├── PHP Backend (src/)
│   ├── Symfony Framework
│   ├── Doctrine ORM
│   ├── Twig Templates
│   └── Dependencies
├── Vue.js Frontend (web/dist/)
│   ├── Built/minified code
│   ├── Assets
│   └── Dependencies
├── Database
│   ├── Schema
│   ├── Migrations
│   └── Initial data
└── Configuration
    ├── .env settings
    ├── Database config
    └── App settings
```

---

## 🌐 After Deployment

### Access Application

```
https://<APP_SERVICE_NAME>.azurewebsites.net
```

### Complete Installation

1. Open application URL
2. Follow OrangeHRM installer
3. Create admin user
4. Configure your organization

### Monitor Application

```bash
# View logs
az webapp log tail --resource-group orangehrm-rg --name orangehrm-app

# Check status
az webapp show --resource-group orangehrm-rg --name orangehrm-app
```

### Scale Resources

```bash
# Scale up App Service
az appservice plan update --resource-group orangehrm-rg \
  --name orangehrm-plan --sku S1

# Scale up Database
az mysql db server update --name orangehrm-mysql \
  --resource-group orangehrm-rg --sku-name B_Standard_B2s
```

---

## 🔧 Troubleshooting

### Validation Fails

**Issue:** "Missing required configuration"

**Solution:**
1. Check .env file exists
2. Fill in all values in .env
3. Verify credentials are correct

### Resource Creation Fails

**Issue:** "Resource already exists" or "Invalid credentials"

**Solution:**
1. Verify Azure CLI is logged in: `az login`
2. Check Service Principal has Contributor role
3. Try different resource names (must be globally unique)
4. Check subscription has available credits

### Database Connection Fails

**Issue:** "Cannot connect to database"

**Solution:**
1. Wait 5-10 minutes after creation
2. Check firewall rules allow Azure services
3. Verify database admin password
4. Check database is in running state in Portal

### Build Fails

**Issue:** "npm/composer not found"

**Solution:**
1. Install Node.js and Composer
2. Restart terminal after installation
3. Verify PATH environment variables
4. Test: `npm --version` and `composer --version`

### Deployment Fails

**Issue:** "Cannot upload package"

**Solution:**
1. Check App Service is running
2. Check storage account credentials
3. Reduce package size if too large
4. Try manual deployment via Portal

### Application Shows 500 Error

**Issue:** "Internal Server Error"

**Solution:**
1. Check logs: `az webapp log tail ...`
2. Verify database connection
3. Check file permissions
4. Verify PHP extensions are enabled

---

## 📝 Logs

Deployment logs are saved to:

```
logs/deployment.log
```

View in real-time:
```bash
# Tail application logs
az webapp log tail --resource-group orangehrm-rg --name orangehrm-app

# Download logs
az webapp log download --resource-group orangehrm-rg \
  --name orangehrm-app --log-file logs.zip
```

---

## 💾 Backup & Recovery

### Enable Backups

```bash
# In Azure Portal:
# App Service → Backups → Configure
# Database → Backups → View backups
```

### Restore from Backup

```bash
az mysql db server restore --name orangehrm-mysql \
  --resource-group orangehrm-rg \
  --restore-point-in-time "2024-01-15T10:00:00"
```

---

## 🔐 Security

### Best Practices

1. ✓ Never commit .env to version control
2. ✓ Use strong database password
3. ✓ Enable HTTPS (automatic in Azure)
4. ✓ Limit database access
5. ✓ Rotate credentials every 3-6 months
6. ✓ Enable MFA on Azure account
7. ✓ Monitor logs for suspicious activity
8. ✓ Keep software updated

### .gitignore

```gitignore
.env
.env.local
logs/
build-output/
venv/
.DS_Store
*.pyc
__pycache__/
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Increase App Service tier
az appservice plan update --resource-group orangehrm-rg \
  --name orangehrm-plan --sku S2
```

### Vertical Scaling

```bash
# Upgrade Database tier
az mysql db server update --name orangehrm-mysql \
  --resource-group orangehrm-rg --sku-name GP_Standard_D4s
```

### Recommended Tiers

| Users | App Service | Database | Monthly Cost |
|-------|-------------|----------|--------------|
| <50 | B2 | B_Standard_B1ms | $30-50 |
| 50-500 | S1 | B_Standard_B2s | $50-100 |
| 500+ | S3 | GP_Standard_D2s | $150-300 |

---

## 🗑️ Cleanup

### Delete All Resources

```bash
# Delete resource group (removes everything)
az group delete --resource-group orangehrm-rg --yes
```

### Delete Specific Resources

```bash
# Delete App Service only
az webapp delete --resource-group orangehrm-rg --name orangehrm-app

# Delete Database only
az mysql db server delete --resource-group orangehrm-rg --name orangehrm-mysql
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | 5-step quick deployment guide |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Comprehensive step-by-step guide |
| `.env.example` | Configuration template with detailed notes |

---

## 🆘 Support & Resources

### Documentation Links

- **OrangeHRM:** https://starterhelp.orangehrm.com
- **Azure App Service:** https://learn.microsoft.com/en-us/azure/app-service/
- **Azure MySQL:** https://learn.microsoft.com/en-us/azure/mysql/
- **Symfony:** https://symfony.com/doc/
- **Vue.js:** https://vuejs.org/

### Contact

- OrangeHRM Support: https://starterhelp.orangehrm.com
- Azure Support: https://portal.azure.com (Help + Support)
- Stack Overflow: Tag `orangehrm` or `azure`

---

## 📌 Important Notes

⚠️ **IMPORTANT:**

1. Keep `.env` file secure - never commit to git
2. Store database password securely
3. Monitor Azure costs regularly
4. Enable automated backups
5. Test disaster recovery procedures
6. Keep software and dependencies updated
7. Review security settings regularly
8. Enable logging and monitoring

---

## 📊 Project Information

- **OrangeHRM Version:** 5.8.1
- **PHP Version:** 8.0+
- **Node.js Version:** 16+
- **Azure Services Used:**
  - App Service (Web hosting)
  - Azure Database for MySQL (Database)
  - Storage Account (File storage)
  - Resource Groups (Organization)
- **Estimated Cost:** $35-70/month (B2 tier)
- **Estimated Deployment Time:** 30-45 minutes

---

## 📄 License

These deployment scripts are provided as-is for deploying OrangeHRM to Azure.

OrangeHRM is licensed under GNU General Public License v3.0 or later.

---

## 🎯 Next Steps

1. Read [QUICK_START.md](QUICK_START.md) for immediate deployment
2. Complete [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed information
3. Fill in `.env` with your configuration
4. Run `python deployment_orchestrator.py`
5. Access your application and complete setup

---

**Happy Deploying! 🚀**

For issues or questions, check the troubleshooting section or consult DEPLOYMENT_GUIDE.md
