# QUICK START GUIDE - OrangeHRM Azure Deployment

## 🚀 Get Started in 5 Minutes

This guide will get you from zero to deployed OrangeHRM application on Azure!

---

## STEP 1: Prerequisites Check ✓

Make sure you have installed (takes 2-3 minutes):

```bash
# Check Python
python --version          # Should be 3.8+

# Check Git
git --version            # Should be 2.0+

# Check Azure CLI
az --version             # Should be installed
```

If any are missing, install from links in DEPLOYMENT_GUIDE.md

---

## STEP 2: Azure Preparation ✓ (Takes 10 minutes)

### 2.1: Get Azure Subscription

1. Go to https://azure.microsoft.com/en-us/free/
2. Click "Start Free" and create account
3. Get your **Subscription ID**:
   ```bash
   az login
   az account show --query id
   ```
   Copy the ID (looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 2.2: Create Service Principal

```bash
# Replace YOUR_SUBSCRIPTION_ID with your actual ID
az ad sp create-for-rbac --name orangehrm-deployer \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID
```

**Save the output** (you'll need these values):
```
appId           → AZURE_CLIENT_ID
password        → AZURE_CLIENT_SECRET
tenant          → AZURE_TENANT_ID
```

---

## STEP 3: Setup Configuration ✓ (Takes 5 minutes)

### 3.1: Navigate to Deployment Folder

```bash
cd c:\Users\DELL\Downloads\orangehrm-5.8.1\orangehrm-5.8.1\azure-deployment
```

### 3.2: Create .env File

```bash
copy .env.example .env
```

### 3.3: Edit .env with Your Values

**Open `.env` in text editor and fill in:**

```ini
AZURE_SUBSCRIPTION_ID=<your_subscription_id>
AZURE_TENANT_ID=<your_tenant_id>
AZURE_CLIENT_ID=<your_app_id>
AZURE_CLIENT_SECRET=<your_password>

# Change these to unique names (use your name/company):
APP_SERVICE_NAME=orangehrm-yourname-12345
DB_SERVER_NAME=orangehrm-mysql-yourname-12345
STORAGE_ACCOUNT_NAME=orangehrm12345

# Set a strong database password:
DB_ADMIN_PASSWORD=YourSecure@Pass123!

# Keep rest as defaults
```

**Save the file.**

---

## STEP 4: Install Dependencies ✓ (Takes 2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

---

## STEP 5: Validate Setup ✓ (Takes 1 minute)

```bash
python pre_deployment_checks.py
```

Should show:
```
✓ Python 3.x detected
✓ Azure CLI installed
✓ All Python dependencies installed
✓ VALIDATION PASSED - Ready for deployment
```

If you see errors, fix them before proceeding.

---

## STEP 6: Deploy! 🚀 (Takes 30-45 minutes)

```bash
python deployment_orchestrator.py
```

### What Happens:

1. ✓ Validates environment
2. ✓ Creates Azure resources (5-10 mins)
3. ✓ Sets up database (5-10 mins)
4. ✓ Builds application (5-10 mins)
5. ✓ Deploys to Azure (5-10 mins)

**Watch the progress in console.** It will show:
```
STEP 1: VALIDATE ENVIRONMENT
STEP 2: SETUP AZURE RESOURCES
STEP 3: SETUP DATABASE
STEP 4: BUILD APPLICATION
STEP 5: DEPLOY APPLICATION
```

---

## STEP 7: Access Your Application ✓

When deployment completes, you'll see:

```
✓ Application URL:
   https://orangehrm-yourname-12345.azurewebsites.net
```

1. **Open the URL in browser**
2. **Complete OrangeHRM installer:**
   - Select language
   - Accept license
   - Verify database
   - Create admin user
3. **Login and use OrangeHRM!**

---

## ⚠️ TROUBLESHOOTING

### "Can't find venv"
```bash
# Activate virtual environment again:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### "Azure CLI not found"
```bash
# Install Azure CLI from:
https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
```

### "Deployment failed"
1. Check logs: `type logs\deployment.log`
2. Verify .env values are correct
3. Ensure Azure subscription has available credits
4. Check resource names don't already exist

### "Can't access the app"
1. Wait 5-10 minutes after deployment
2. App Service needs time to start
3. Check Application URL spelling
4. Check internet connection

---

## 📊 What Was Created on Azure?

After deployment, you have:

```
Resource Group: orangehrm-rg
├── App Service (orangehrm-app)
├── Database Server (orangehrm-mysql.mysql.database.azure.com)
├── Storage Account (orangehrmsa)
└── Associated Resources (Plan, IPs, etc.)
```

**Estimated Monthly Cost:**
- App Service B2: $15-30
- Database B1ms: $15-30
- Storage: $5-10
- **Total: ~$35-70/month**

---

## 🎯 Next Steps

After deployment:

1. ✓ Complete OrangeHRM setup wizard
2. ✓ Create your organization
3. ✓ Add employees
4. ✓ Configure modules you need
5. ✓ Enable backups (in Azure Portal)
6. ✓ Monitor application (View logs)

---

## 📖 FULL GUIDE

For detailed instructions, see: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Covers:
- Advanced configuration
- Troubleshooting
- Scaling
- Security
- Monitoring
- Maintenance

---

## ✅ Checklist

Before running deployment:

- [ ] Python 3.8+ installed
- [ ] Azure CLI installed
- [ ] Git installed
- [ ] Azure account created
- [ ] Subscription ID noted
- [ ] Service Principal created
- [ ] .env file created and filled
- [ ] All required tools installed
- [ ] Validation passed
- [ ] Ready to deploy!

---

## 🆘 Need Help?

1. **Check logs:** `logs/deployment.log`
2. **Review guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. **Azure Portal:** https://portal.azure.com
4. **OrangeHRM Help:** https://starterhelp.orangehrm.com

---

## ⏱️ Time Breakdown

| Step | Time | Task |
|------|------|------|
| 1 | 5 min | Prerequisites check |
| 2 | 10 min | Azure setup & Service Principal |
| 3 | 5 min | Configuration |
| 4 | 2 min | Install dependencies |
| 5 | 1 min | Validation |
| 6 | 30-45 min | Deployment ⏳ |
| **Total** | **~60 min** | **✓ Live on Azure!** |

---

**You're all set! Happy deploying! 🎉**
