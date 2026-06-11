# OrangeHRM Azure Deployment Guide

## Complete Step-by-Step Deployment Instructions

---

## TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Azure Account Setup](#azure-account-setup)
3. [Service Principal Creation](#service-principal-creation)
4. [Local Environment Setup](#local-environment-setup)
5. [Configuration Setup](#configuration-setup)
6. [Deployment Execution](#deployment-execution)
7. [Post-Deployment Configuration](#post-deployment-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Monitoring & Maintenance](#monitoring--maintenance)

---

## PREREQUISITES

### Required Tools

Before starting, ensure you have installed:

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Azure CLI**
   - Download from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
   - Verify: `az --version`

3. **Git**
   - Download from: https://git-scm.com/
   - Verify: `git --version`

4. **PHP 8.0+**
   - Download from: https://www.php.net/downloads
   - Verify: `php --version`
   - Extensions needed: pdo, curl, json, mbstring, zip, dom, xml, simplexml, gd, ldap, openssl

5. **Node.js 16+**
   - Download from: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

6. **Composer** (PHP Package Manager)
   - Download from: https://getcomposer.org/
   - Verify: `composer --version`

7. **MySQL Client** (optional, for local testing)
   - Download from: https://dev.mysql.com/downloads/
   - Verify: `mysql --version`

### Required Azure Resources

- **Azure Subscription** with active billing
- Minimum credits/budget to provision:
  - App Service Plan (B2 tier recommended)
  - Azure Database for MySQL
  - Storage Account
  - Estimated cost: $50-150/month depending on usage

### Recommended VS Code Extensions

- Azure Tools
- REST Client
- Thunder Client

---

## AZURE ACCOUNT SETUP

### Step 1: Create Azure Account

1. Go to https://azure.microsoft.com/en-us/free/
2. Click "Start Free"
3. Sign in with Microsoft account (or create one)
4. Complete identity verification
5. Add payment method
6. Note your **Subscription ID** (you'll need this later)

### Step 2: Verify Azure Subscription

```bash
az login
az account show
```

---

## SERVICE PRINCIPAL CREATION

### Why Service Principal?

A Service Principal is a non-interactive account that allows deployment scripts to authenticate with Azure without manual login prompts.

### Step 1: Create Service Principal

```bash
# Login to Azure
az login

# Create service principal with Contributor role
az ad sp create-for-rbac --name orangehrm-deployer --role Contributor --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>

# Replace <YOUR_SUBSCRIPTION_ID> with your actual subscription ID
```

**Output will be JSON like this:**
```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "orangehrm-deployer",
  "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### Step 2: Save Service Principal Credentials

Save this information safely. You'll need:
- **appId** → AZURE_CLIENT_ID
- **password** → AZURE_CLIENT_SECRET
- **tenant** → AZURE_TENANT_ID

---

## LOCAL ENVIRONMENT SETUP

### Step 1: Navigate to Deployment Directory

```bash
cd /path/to/orangehrm-5.8.1/azure-deployment
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install System Dependencies

**Windows (PowerShell as Administrator):**
```powershell
# Install required tools using chocolatey (if installed)
choco install php composer nodejs mysql-cli git

# Or download and install manually from provided links
```

**macOS:**
```bash
brew install php composer node mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install php php-composer-bin nodejs npm mysql-client git

# For PHP extensions
sudo apt-get install php-mysql php-curl php-json php-mbstring php-xml php-gd
```

---

## CONFIGURATION SETUP

### Step 1: Create Environment File

```bash
# Copy template to .env
cp .env.example .env
```

### Step 2: Edit .env with Your Values

**Open `.env` and fill in all values:**

```ini
# Azure Configuration
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Resource Configuration
RESOURCE_GROUP_NAME=orangehrm-rg
AZURE_LOCATION=eastus

# App Service Configuration
APP_SERVICE_PLAN_NAME=orangehrm-plan
APP_SERVICE_NAME=orangehrm-app
APP_SERVICE_SKU=B2

# Database Configuration
DB_SERVER_NAME=orangehrm-mysql
DB_NAME=orangehrm
DB_ADMIN_USER=orangeadmin
DB_ADMIN_PASSWORD=YourSecurePassword123!@#
DB_SKU=B_Standard_B1ms
DB_VERSION=8.0
DB_STORAGE_SIZE=32768

# Storage Configuration
STORAGE_ACCOUNT_NAME=orangehrmsa
STORAGE_CONTAINER_NAME=orangehrm-files

# Application Settings
PHP_VERSION=8.2
NODE_VERSION=18
DEPLOY_BRANCH=main

# Deployment Settings
DEPLOYMENT_METHOD=zip
APP_REPO_PATH=..
ENABLE_BUILD=true
COMPOSER_INSTALL=true
NPM_INSTALL=true
PROD_BUILD=true
ZIP_DEPLOYMENT=true
```

### Important Configuration Notes

**APP_REPO_PATH**: Set to the path of your OrangeHRM application (usually `..` if running from azure-deployment folder)

**Database Password**: Use a strong password with:
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, and special characters
- Example: `Or@ngeH1rM2024!`

**Location**: Choose Azure region nearest to you:
- `eastus`, `westus`, `northeurope`, `westeurope`, `southeastasia`, etc.

---

## DEPLOYMENT EXECUTION

### Step 1: Validate Environment

```bash
# Run pre-deployment checks
python pre_deployment_checks.py
```

Expected output:
```
✓ Python 3.x detected
✓ Azure CLI installed
✓ Found: src
✓ Azure configuration validated
✓ VALIDATION PASSED - Ready for deployment
```

### Step 2: Run Full Deployment

```bash
# Start complete deployment process
python deployment_orchestrator.py
```

This will:
1. Validate environment
2. Create Azure resources (Resource Group, App Service, Database, Storage)
3. Setup database and run migrations
4. Build application (install dependencies, compile frontend)
5. Deploy to Azure App Service

**Estimated time: 30-45 minutes**

### Step 3: Monitor Deployment

Watch the console output for progress. Logs are also saved to:
```
logs/deployment.log
```

### Alternative: Run Steps Individually

If you prefer to run steps manually:

```bash
# Step 1: Validate environment
python pre_deployment_checks.py

# Step 2: Setup Azure resources
python azure_setup.py

# Step 3: Setup database
python database_setup.py

# Step 4: Build and deploy
python build_and_deploy.py
```

---

## POST-DEPLOYMENT CONFIGURATION

### Step 1: Access Your Application

After deployment completes successfully, access your application:

```
https://<APP_SERVICE_NAME>.azurewebsites.net
```

Example: `https://orangehrm-app.azurewebsites.net`

### Step 2: Complete OrangeHRM Installation

1. Open your application URL in browser
2. You should see OrangeHRM installer
3. Follow installer steps:
   - Select language
   - Accept license agreement
   - Verify database connection
   - Create admin user
   - Complete setup

### Step 3: Configure Application Settings

**Via Azure Portal:**

1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to App Service → Your App Service Name
3. Click "Configuration"
4. Add/modify application settings:
   - `APP_ENV`: `prod`
   - `APP_DEBUG`: `0`
   - `PHP_VERSION`: `8.2`

### Step 4: Configure Custom Domain (Optional)

1. In Azure Portal, go to Custom domains
2. Add your custom domain
3. Configure DNS records as instructed
4. Enable HTTPS/SSL

### Step 5: Setup Backups (Recommended)

1. Go to App Service → Backups
2. Click "Configure"
3. Enable automatic backups
4. Choose storage account
5. Set backup frequency (daily recommended)

---

## TROUBLESHOOTING

### Issue: "Authentication Failed"

**Solution:**
1. Verify Azure CLI is installed: `az --version`
2. Verify .env has correct credentials
3. Run `az login` and login interactively
4. Check Service Principal has Contributor role:
   ```bash
   az role assignment list --assignee <AZURE_CLIENT_ID>
   ```

### Issue: "Resource Already Exists"

**Solution:**
1. Resources from previous deployment already exist
2. Either:
   - Delete resource group: `az group delete --name orangehrm-rg`
   - Or rename resources in .env and retry

### Issue: "Database Connection Failed"

**Solution:**
1. Verify database server is running in Azure Portal
2. Check firewall rules allow Azure services
3. Verify credentials in database_setup.py
4. Wait a few minutes for database to be fully provisioned

### Issue: "Build Failed - npm/composer not found"

**Solution:**
1. Ensure Node.js and Composer are installed
2. Verify they're in system PATH
3. Restart terminal after installation
4. Test: `npm --version` and `composer --version`

### Issue: "Deployment Package Too Large"

**Solution:**
1. Remove unnecessary files before deploying
2. Delete node_modules folders: `del src\node_modules`
3. Exclude test directories
4. Rebuild package

### Issue: "Application Shows 500 Error"

**Solution:**
1. Check App Service logs:
   ```bash
   az webapp log tail --resource-group orangehrm-rg --name orangehrm-app
   ```
2. Check storage file system has write permissions
3. Verify database migrations completed successfully
4. Check PHP error logs in Azure portal

### Issue: "Installer Won't Complete"

**Solution:**
1. Verify database is accessible
2. Check database migrations ran successfully
3. Try accessing installer at: `https://your-app-url/installer/index.php`
4. Check logs for specific error

---

## MONITORING & MAINTENANCE

### View Application Logs

**Azure Portal Method:**
1. Go to App Service
2. Click "Log Stream"
3. View real-time logs

**CLI Method:**
```bash
# View last 100 lines
az webapp log tail --resource-group orangehrm-rg --name orangehrm-app --lines 100

# Stream logs in real-time
az webapp log tail --resource-group orangehrm-rg --name orangehrm-app
```

### Monitor Database

**Azure Portal:**
1. Go to Azure Database for MySQL
2. View Metrics:
   - CPU percentage
   - Memory percentage
   - Storage used

**Scale Database if Needed:**
```bash
az mysql db server update --name orangehrm-mysql \
  --resource-group orangehrm-rg \
  --sku-name <NEW_SKU>
```

### View Application Performance

**Application Insights (Optional):**
1. Enable in App Service
2. Monitor:
   - Response times
   - Failures
   - Dependencies
   - Requests

### Database Backups

**Check Backup Status:**
```bash
az mysql db server restore --name orangehrm-mysql \
  --resource-group orangehrm-rg \
  --backup-name latest
```

### Update Application

To deploy new version:

```bash
# Build new version
python build_and_deploy.py
```

Or redeploy specific component:

```bash
# Frontend only
cd src/client
npm run build
cd ../..

# Backend only
cd src
composer install --no-dev
cd ..
```

---

## SCALING RECOMMENDATIONS

### For Small Deployments (< 50 users)
- App Service: B1 or B2
- Database: B_Standard_B1ms
- Storage: Standard LRS

### For Medium Deployments (50-500 users)
- App Service: S1 or S2
- Database: B_Standard_B2s or GP_Standard
- Storage: Standard GRS

### For Large Deployments (500+ users)
- App Service: S3 or P1V2
- Database: GP_Standard or MO_Standard (higher tier)
- Storage: Premium or GRS

**Scale resources:**
```bash
# Scale App Service
az appservice plan update --resource-group orangehrm-rg \
  --name orangehrm-plan \
  --sku S1

# Scale Database
az mysql db server update --name orangehrm-mysql \
  --resource-group orangehrm-rg \
  --sku-name B_Standard_B2s
```

---

## SECURITY BEST PRACTICES

1. **Enable HTTPS**
   - Azure handles automatically
   - Verify in browser

2. **Regular Backups**
   - Enable automatic backups
   - Test restore procedures

3. **Monitor Logs**
   - Check for suspicious activity
   - Monitor failed authentication attempts

4. **Update Software**
   - Keep PHP updated
   - Keep dependencies updated: `composer update`, `npm update`

5. **Limit Database Access**
   - Only allow Azure services
   - Use firewall rules

6. **Secure Credentials**
   - Store .env securely
   - Rotate Service Principal credentials periodically
   - Never commit credentials to git

---

## SUPPORT & RESOURCES

### Documentation
- OrangeHRM: https://starterhelp.orangehrm.com
- Azure App Service: https://learn.microsoft.com/en-us/azure/app-service/
- Azure MySQL: https://learn.microsoft.com/en-us/azure/mysql/

### Community
- OrangeHRM Forums: https://forums.orangehrm.com
- Stack Overflow: Tag `orangehrm` or `azure`

### Deployment Scripts GitHub
Issues and discussions about these scripts should be posted to your repository.

---

## NEXT STEPS

After successful deployment:

1. ✓ Access your application
2. ✓ Complete OrangeHRM setup
3. ✓ Configure your organization
4. ✓ Add users
5. ✓ Enable SSO/LDAP (optional)
6. ✓ Setup backup schedules
7. ✓ Monitor performance

---

## QUICK REFERENCE COMMANDS

```bash
# View deployment status
az deployment group show --resource-group orangehrm-rg

# List all resources
az resource list --resource-group orangehrm-rg

# Get App Service URL
az webapp show --resource-group orangehrm-rg --name orangehrm-app --query 'defaultHostName'

# Restart App Service
az webapp restart --resource-group orangehrm-rg --name orangehrm-app

# View database connection string
az mysql db server show-connection-string --server-name orangehrm-mysql

# Delete all resources
az group delete --resource-group orangehrm-rg --yes --no-wait
```

---

## VERSION INFORMATION

- OrangeHRM Version: 5.8.1
- PHP Version: 8.0+
- Node.js Version: 16+
- Azure Services: App Service, MySQL Database, Storage Account
- Last Updated: 2024

---

**Good luck with your OrangeHRM deployment! 🚀**
