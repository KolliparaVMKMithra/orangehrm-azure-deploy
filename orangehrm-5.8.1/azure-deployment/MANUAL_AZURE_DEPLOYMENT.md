# OrangeHRM Azure Manual Deployment - Step by Step

## Complete Manual Deployment Guide (No Scripts Needed)

This guide walks you through deploying OrangeHRM 5.8.1 to Azure entirely through the Azure Portal, doing everything manually yourself.

---

## TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Create Resource Group](#create-resource-group)
3. [Create App Service Plan](#create-app-service-plan)
4. [Create App Service](#create-app-service)
5. [Configure PHP Settings](#configure-php-settings)
6. [Create MySQL Database](#create-mysql-database)
7. [Configure Database Firewall](#configure-database-firewall)
8. [Create Storage Account](#create-storage-account)
9. [Build Application Locally](#build-application-locally)
10. [Deploy Application](#deploy-application)
11. [Configure Database](#configure-database)
12. [Complete OrangeHRM Setup](#complete-orangehrm-setup)
13. [Post-Deployment Configuration](#post-deployment-configuration)

---

## PREREQUISITES

**Estimated Time: Already Done**

### What You Need

✓ Azure subscription (you already have this)
✓ Local development environment:
  - PHP 8.0+ with required extensions
  - Node.js 16+ with npm
  - Composer (PHP package manager)
  - Git (for downloading code)
  - MySQL Client (optional, for testing)

### Install Required Tools (if not already installed)

**Windows:**
```powershell
# Using Chocolatey (if installed)
choco install php composer nodejs git mysql-cli

# Or download manually:
# - PHP: https://www.php.net/downloads
# - Node.js: https://nodejs.org/
# - Composer: https://getcomposer.org/
# - Git: https://git-scm.com/
```

**macOS:**
```bash
brew install php composer node git mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install php php-cli php-composer-bin nodejs npm mysql-client git
sudo apt-get install php-mysql php-curl php-json php-mbstring php-xml php-gd
```

### Verify Installation

```bash
php --version
composer --version
node --version
npm --version
git --version
```

---

## STEP 1: CREATE RESOURCE GROUP

**Estimated Time: 2 minutes**

A Resource Group is a container for all your Azure resources.

### Instructions

1. **Open Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Create New Resource Group**
   - Click "Resource groups" in the left sidebar (or search for it)
   - Click "Create" button at the top

3. **Fill in Resource Group Details**
   ```
   Subscription:        [Your subscription name]
   Resource group name: orangehrm-rg
   Region:             [Choose closest to you: eastus, westeurope, etc.]
   ```

4. **Review and Create**
   - Click "Review + create" button
   - Click "Create" button

5. **Wait for Completion**
   - Wait for "Deployment successful" notification
   - Should take 10-30 seconds

### Verify

- You should see "orangehrm-rg" in your resource groups list
- Green checkmark indicates success

---

## STEP 2: CREATE APP SERVICE PLAN

**Estimated Time: 5 minutes**

An App Service Plan defines the computing resources for hosting your web application.

### Instructions

1. **Navigate to Resource Group**
   - Go to https://portal.azure.com
   - Click "Resource groups" in left sidebar
   - Click "orangehrm-rg" that you just created

2. **Create New Resource**
   - Click "Create resources" button (or "Create" at top)
   - Search for "App Service Plan"
   - Click "App Service Plan" in results
   - Click "Create" button

3. **Fill in Basic Details**
   ```
   Subscription:          [Your subscription]
   Resource group:        orangehrm-rg
   Name:                 orangehrm-plan
   Operating System:     Linux (recommended)
   Region:               [Same as resource group]
   Sku and size:         (click "Change size")
   ```

4. **Select Pricing Tier**
   - Click "Change size" or "Pricing tier"
   - Select **B2** (Basic tier - good for testing)
     - **B1:** $15/month (minimal)
     - **B2:** $30/month (recommended) ← SELECT THIS
     - **S1:** $60/month (production)
   - Click "Apply" button

5. **Review and Create**
   - Click "Review + create"
   - Review all settings
   - Click "Create"

6. **Wait for Completion**
   - Should take 1-2 minutes
   - Wait for success notification

### Verify

- Resource group shows "orangehrm-plan"
- Status should be "Succeeded"

---

## STEP 3: CREATE APP SERVICE

**Estimated Time: 5 minutes**

This is your web application hosting environment.

### Instructions

1. **Navigate to Resource Group**
   - Go to https://portal.azure.com
   - Go to "Resource groups" → "orangehrm-rg"

2. **Create New App Service**
   - Click "Create resources" button
   - Search for "App Service"
   - Click "App Service"
   - Click "Create" button

3. **Fill in Project Details**
   ```
   Subscription:        [Your subscription]
   Resource group:      orangehrm-rg
   Name:               orangehrm-app
   Publish:            Code
   Runtime stack:      PHP 8.2 (IMPORTANT!)
   Operating System:   Linux
   Region:             [Same as resource group]
   App Service Plan:   orangehrm-plan
   ```

4. **Click Through Tabs**
   - **Basics:** Filled above
   - **MySQL:**
     - Select "Create new" MySQL database
     - Server name: orangehrm-mysql
     - Database name: orangehrm
     - Admin username: orangeadmin
     - Admin password: YourSecure@Pass123! (strong password!)
     - Click through this for now
   - **Deployment:** Skip for now (we'll deploy manually)
   - **Monitoring:** Enable if desired

5. **Review and Create**
   - Click "Review + create"
   - Check all settings
   - Click "Create"

6. **Wait for Completion**
   - This takes 2-3 minutes
   - Watch for success notification

### Verify

- You'll see "orangehrm-app" in resource group
- Status shows "Created"

### Get Your App Service URL

After creation, find your application URL:
- In resource group, click "orangehrm-app"
- Look for "Default domain" or "URL" at top right
- Format: `https://orangehrm-app.azurewebsites.net`
- **Save this URL** - you'll need it later

---

## STEP 4: CONFIGURE PHP SETTINGS

**Estimated Time: 5 minutes**

Configure PHP runtime and extensions for OrangeHRM.

### Instructions

1. **Go to App Service**
   - Azure Portal → Resource groups → orangehrm-rg
   - Click "orangehrm-app"

2. **Open Configuration**
   - In left sidebar, scroll down
   - Click "Configuration" under "Settings"

3. **Configure General Settings**
   - Scroll down to "General settings" section
   - PHP version: **8.2** (select from dropdown)
   - Web sockets: **On**
   - Click "Save" button at top

4. **Add Application Settings**
   - Still in Configuration, scroll to "Application settings"
   - Click "+ New application setting"
   - Add these settings one by one:
     ```
     Name: APP_ENV          Value: prod
     Name: APP_DEBUG        Value: 0
     Name: COMPOSER_EXTENSIONS  Value: true
     ```
   - After each, click "Add" and then add the next one
   - Click "Save" at the top

5. **Verify PHP Extensions**
   - Click "Extensions" in left sidebar (under App Service)
   - Look for installed extensions
   - PHP should have: pdo, curl, json, mbstring, zip, xml, gd

### Important App Settings

These are critical for OrangeHRM:

```
APP_ENV = prod
APP_DEBUG = 0
PHP_VERSION = 8.2
```

---

## STEP 5: CREATE MYSQL DATABASE

**Estimated Time: 10-15 minutes**

Create Azure Database for MySQL to store OrangeHRM data.

### Instructions

1. **Navigate to Create Resource**
   - Azure Portal → "Create a resource"
   - Search for "Azure Database for MySQL"
   - Click "Azure Database for MySQL – Flexible Server"
   - Click "Create"

2. **Fill in Basic Information**
   ```
   Subscription:         [Your subscription]
   Resource group:       orangehrm-rg
   Server name:          orangehrm-mysql
   Region:              [Same as others]
   MySQL version:       8.0 (important!)
   Workload type:       Development
   ```

3. **Set Admin Credentials**
   - Admin username: `orangeadmin`
   - Password: `YourSecure@Pass123!` (use strong password)
   - Confirm password: (same)

4. **Configure Compute and Storage**
   - Click "Configure server" or go to "Compute + storage" tab
   - Burstable tier: **Standard_B1ms** (for dev/test)
     - CPU: 1 vCore
     - Storage: 32 GB
     - Memory: 2 GB
   - Click "OK" or "Apply"

5. **High Availability (Optional)**
   - You can skip this for development
   - For production, enable Zone redundancy

6. **Networking**
   - Public access: **Yes**
   - Check "Allow public access from any Azure service"
   - Click to add firewall rule: "Allow access from current IP"

7. **Tags (Optional)**
   - Add tags to organize resources:
     ```
     Environment: Development
     Application: OrangeHRM
     ```

8. **Review and Create**
   - Click "Review + create"
   - Review all settings
   - Click "Create"

9. **Wait for Deployment**
   - Takes 5-10 minutes
   - Watch for completion notification
   - Very important: Wait until fully deployed!

### Get Database Connection Details

After creation, find your database connection info:

1. Go to "orangehrm-mysql" resource in Azure Portal
2. Look for "Server name" - copy it (format: `orangehrm-mysql.mysql.database.azure.com`)
3. Admin username: `orangeadmin@orangehrm-mysql`
4. Password: Whatever you set above

**Save these details** - you'll need them for:
- Database migrations
- Application configuration
- Testing connections

### Verify Database is Ready

```
Server name:    orangehrm-mysql.mysql.database.azure.com
Admin user:     orangeadmin@orangehrm-mysql
Database name:  orangehrm (not created yet - we'll do this manually)
Port:           3306
```

---

## STEP 6: CONFIGURE DATABASE FIREWALL

**Estimated Time: 3 minutes**

Allow your App Service to connect to the database.

### Instructions

1. **Go to MySQL Database**
   - Azure Portal → Resource groups → orangehrm-rg
   - Click "orangehrm-mysql"

2. **Open Networking**
   - In left sidebar under "Settings"
   - Click "Networking"

3. **Configure Firewall Rules**
   - Section "Firewall rules"
   - Check "Allow public access from any Azure service within Azure IP range"
   - This allows App Service to connect

4. **Add Rule for Your Computer (Optional)**
   - To connect locally for testing
   - Click "+ Add current client IP address"
   - This adds your current IP

5. **Save**
   - Click "Save" button at top

### Important

✓ Must have firewall rule allowing Azure services
✓ Without this, App Service can't connect to database

---

## STEP 7: CREATE STORAGE ACCOUNT

**Estimated Time: 5 minutes**

Create storage account for application files and uploads.

### Instructions

1. **Create New Resource**
   - Azure Portal → "Create a resource"
   - Search for "Storage account"
   - Click "Storage account"
   - Click "Create"

2. **Fill in Storage Details**
   ```
   Subscription:        [Your subscription]
   Resource group:      orangehrm-rg
   Storage account name: orangehrmsa (must be unique, lowercase only)
   Region:             [Same as others]
   Performance:        Standard
   Redundancy:         Locally-redundant storage (LRS)
   ```

3. **Advanced Settings (Optional)**
   - Leave defaults
   - Click "Next: Advanced" if needed

4. **Networking (Optional)**
   - Leave defaults
   - Click "Next: Networking" if needed

5. **Data Protection (Optional)**
   - Leave defaults

6. **Review and Create**
   - Click "Review + create"
   - Click "Create"

7. **Wait for Completion**
   - Takes 1-2 minutes

### Verify

- Storage account "orangehrmsa" appears in resource group
- Status shows "Created"

---

## STEP 8: BUILD APPLICATION LOCALLY

**Estimated Time: 10-15 minutes**

Prepare your OrangeHRM application for deployment.

### Instructions

1. **Open Terminal/PowerShell**
   - Navigate to your OrangeHRM directory
   ```bash
   cd c:\Users\DELL\Downloads\orangehrm-5.8.1\orangehrm-5.8.1
   ```

2. **Install PHP Dependencies**
   ```bash
   cd src
   composer install --no-dev --optimize-autoloader
   cd ..
   ```
   - Takes 3-5 minutes
   - Installs all required PHP packages

3. **Install JavaScript Dependencies**
   ```bash
   cd src\client
   npm install --production=false
   cd ..\..
   ```
   - Takes 5-10 minutes
   - Installs Vue.js and frontend dependencies

4. **Build Frontend**
   ```bash
   cd src\client
   npm run build
   cd ..\..
   ```
   - Takes 2-3 minutes
   - Creates optimized frontend in `web/dist/`

5. **Verify Build Output**
   - Check that `src/vendor/` directory exists
   - Check that `web/dist/` directory exists
   - If both exist, build was successful

### Build Commands Summary

```bash
# Step 1: Install PHP packages
cd src
composer install --no-dev --optimize-autoloader

# Step 2: Install frontend packages
cd client
npm install --production=false

# Step 3: Build frontend
npm run build

# Step 4: Go back to root
cd ../..
```

---

## STEP 9: DEPLOY APPLICATION

**Estimated Time: 10-15 minutes**

Upload your application to Azure App Service.

### Instructions

1. **Create ZIP Package**
   - Select these folders in your OrangeHRM directory:
     ```
     ✓ src/         (entire folder)
     ✓ web/         (entire folder)
     ✓ bin/         (entire folder)
     ✓ lib/         (entire folder)
     ✓ index.php    (file)
     ```
   - Right-click → "Send to" → "Compressed (zipped) folder"
   - Name it: `orangehrm-deploy.zip`
   - Should be 50-150 MB

2. **Go to App Service in Azure Portal**
   - Azure Portal → Resource groups → orangehrm-rg
   - Click "orangehrm-app"

3. **Open Deployment Center**
   - In left sidebar under "Deployment"
   - Click "Deployment Center"

4. **Upload ZIP File**
   - Find "Publish" button or dropdown
   - Choose "Zip Deploy" method
   - Drag and drop your `orangehrm-deploy.zip` file
   - Or click "Upload file" and select the ZIP

5. **Wait for Deployment**
   - Deployment status shows "Creating"
   - Takes 3-5 minutes to upload and extract
   - Wait for "Active" status

6. **Verify Deployment**
   - After completion, go to "App Service Editor" (optional)
   - Or visit your app URL to test

### Alternative: Upload via Azure CLI

If ZIP upload doesn't work:

```bash
az webapp deployment source config-zip \
  --resource-group orangehrm-rg \
  --name orangehrm-app \
  --src c:\path\to\orangehrm-deploy.zip
```

---

## STEP 10: CONFIGURE DATABASE

**Estimated Time: 5 minutes**

Create the database and configure connection.

### Instructions

1. **Connect to MySQL Database**
   
   **Option A: Using MySQL Workbench** (GUI tool)
   - Download from https://www.mysql.com/products/workbench/
   - Create new connection:
     ```
     Connection Name: OrangeHRM Azure
     Hostname: orangehrm-mysql.mysql.database.azure.com
     Port: 3306
     Username: orangeadmin@orangehrm-mysql
     Password: (your password)
     ```
   - Click "Test Connection" to verify
   - Click "OK"

   **Option B: Using Command Line**
   ```bash
   mysql -h orangehrm-mysql.mysql.database.azure.com \
     -u orangeadmin@orangehrm-mysql \
     -p
   ```
   - It will prompt for password
   - Enter your database password

2. **Create Database**
   
   Run this SQL command:
   ```sql
   CREATE DATABASE IF NOT EXISTS orangehrm 
   CHARACTER SET utf8mb4 
   COLLATE utf8mb4_unicode_ci;
   ```

3. **Verify Database Created**
   ```sql
   SHOW DATABASES;
   ```
   - You should see "orangehrm" in the list

4. **Create Application Configuration File**

   On your App Service, create `.env.local` file in `/src/` directory:
   
   ```
   DATABASE_URL=mysql://orangeadmin%40orangehrm-mysql:YourPassword@orangehrm-mysql.mysql.database.azure.com:3306/orangehrm?serverVersion=8.0
   APP_ENV=prod
   APP_DEBUG=0
   ```
   
   **How to create this file:**
   - Option 1: Use App Service Editor (in Portal)
     - Go to App Service → App Service Editor
     - Navigate to `/src/` folder
     - Create new file `.env.local`
     - Add content above
   
   - Option 2: Via SSH (if enabled)
     - Connect via SSH
     - Create file with `nano` or `vi`

---

## STEP 11: RUN DATABASE MIGRATIONS

**Estimated Time: 5 minutes**

Run Doctrine migrations to create database schema.

### Instructions

1. **Connect via SSH to App Service**
   - In Azure Portal, go to App Service
   - Click "SSH" or "Advanced Tools" → "Go" (opens Kudu)
   - Or: Click "Settings" → "Extensions" → "SSH" if available

2. **Navigate to Application Directory**
   ```bash
   cd /home/site/wwwroot/src
   ```

3. **Run Database Migrations**
   ```bash
   php bin/console doctrine:migrations:migrate --env=prod --no-interaction
   ```
   - This creates database schema
   - Takes 2-3 minutes
   - Should show success message

4. **Verify Tables Created**
   ```bash
   mysql -h orangehrm-mysql.mysql.database.azure.com \
     -u orangeadmin@orangehrm-mysql -p orangehrm
   
   SHOW TABLES;
   ```
   - Should list many tables (100+)

### Alternative: Run Migrations Locally

If SSH doesn't work, run on your local machine:

```bash
cd src

# Set environment variable
set DATABASE_URL=mysql://orangeadmin%40orangehrm-mysql:YourPassword@orangehrm-mysql.mysql.database.azure.com:3306/orangehrm?serverVersion=8.0

# Run migrations
php bin/console doctrine:migrations:migrate --env=prod --no-interaction
```

---

## STEP 12: COMPLETE ORANGEHRM SETUP

**Estimated Time: 10-15 minutes**

Access your application and complete the OrangeHRM installer.

### Instructions

1. **Open Application in Browser**
   - Go to your App Service URL
   - Format: `https://orangehrm-app.azurewebsites.net`
   - Wait 5-10 seconds for first load

2. **You Should See**
   - OrangeHRM Installer page
   - Language selection dropdown
   - Step indicators at left

3. **Follow Installer Steps**

   **Step 1: Language Selection**
   - Select your language
   - Click "Next"

   **Step 2: License Agreement**
   - Read license terms
   - Check "I accept the terms and conditions"
   - Click "Next"

   **Step 3: System Check**
   - Should show all green checkmarks ✓
   - If any red X, you need to fix PHP settings
   - Click "Next"

   **Step 4: Database Configuration**
   - Host: `orangehrm-mysql.mysql.database.azure.com`
   - Database Name: `orangehrm`
   - Username: `orangeadmin@orangehrm-mysql`
   - Password: (your database password)
   - Port: `3306`
   - Click "Next"

   **Step 5: Database Verification**
   - Should show "Database connection verified"
   - If error: Check firewall rules, credentials
   - Click "Next"

   **Step 6: Create Admin Account**
   - First Name: (your name)
   - Last Name: (your name)
   - Email: (your email)
   - Username: `admin`
   - Password: (strong password)
   - Confirm Password: (same)
   - Click "Next"

   **Step 7: Organization Setup**
   - Organization Name: (your company name)
   - Country: (select from dropdown)
   - Employees: (your choice)
   - Click "Next"

   **Step 8: Localization**
   - Date Format: (select preference)
   - Time Zone: (select your timezone)
   - Time Format: (select preference)
   - Click "Next"

   **Step 9: Installation Complete**
   - Should show "Installation Completed Successfully"
   - Click "Finish" or login link

4. **Login to OrangeHRM**
   - Username: `admin`
   - Password: (what you set in Step 6)
   - You're now logged into OrangeHRM!

### Troubleshooting Installer

**Problem: Database connection fails**
- Check firewall rule allows Azure services
- Verify credentials are correct
- Test connection locally first

**Problem: System Check shows errors**
- Usually means PHP extensions missing
- Check App Service Configuration
- Verify PHP 8.2 is selected
- Restart App Service

**Problem: Installer won't load**
- Wait 10 minutes after deployment
- App Service might still be starting
- Reload the page
- Check browser developer console for errors

---

## STEP 13: POST-DEPLOYMENT CONFIGURATION

**Estimated Time: 10 minutes**

Configure your Azure resources for production use.

### Instructions

1. **Enable HTTPS Only**
   - Go to App Service → orangehrm-app
   - Click "TLS/SSL settings" in left sidebar
   - Set "HTTPS only" to "On"
   - This forces all traffic to HTTPS

2. **Configure Custom Domain (Optional)**
   - If you have a domain name
   - Go to "Custom domains" in App Service
   - Add your domain
   - Configure DNS records as instructed

3. **Enable Backups**
   - Go to App Service → orangehrm-app
   - Click "Backups" in left sidebar (may be under "Disaster recovery")
   - Click "Configure"
   - Select storage account (orangehrmsa)
   - Set schedule: Daily (recommended)
   - Backup retention: 7 days minimum

4. **Configure Database Backups**
   - Go to MySQL Database → orangehrm-mysql
   - Look for "Backup and restore" or "Disaster recovery"
   - Azure automatically backs up MySQL
   - Retention period: 7 days (default)
   - Backup location: (select if options available)

5. **Enable Application Logging (Optional)**
   - Go to App Service → orangehrm-app
   - Click "App Service logs" under Monitoring
   - Enable:
     - "Application logging (Filesystem)" - On
     - "Web server logging" - On
   - Retention period: 1 day minimum
   - Click "Save"

6. **Monitor Application**
   - Go to App Service → orangehrm-app
   - Click "Metrics" under Monitoring
   - Watch for:
     - CPU Percentage
     - Memory Percentage
     - Response time
   - Set up alerts if needed

7. **Scale Up if Needed**
   - If application is slow:
   - Go to App Service → orangehrm-app
   - Click "Scale up (App Service plan)"
   - Choose higher tier (S1, S2, etc.)
   - Click "Apply"

### Recommended Post-Deployment

- [ ] Enable HTTPS only
- [ ] Enable automatic backups
- [ ] Enable application logging
- [ ] Configure monitoring alerts
- [ ] Test disaster recovery (restore from backup)
- [ ] Document your setup
- [ ] Create administrator guide for your team

---

## MONITORING & MAINTENANCE

### View Application Logs

1. **In Azure Portal**
   - App Service → orangehrm-app
   - Click "Log stream" under Monitoring
   - Watch real-time logs

2. **Download Logs**
   - Click "Kudu Console" (Advanced Tools)
   - Download logs from `/LogFiles/`

### Check Resource Health

```
App Service Dashboard:
├── Overview (status, URL, usage)
├── Metrics (CPU, Memory, Response Time)
├── Alerts (set up warnings)
├── Backups (restore if needed)
└── Settings (configuration)

MySQL Database Dashboard:
├── Overview (server status)
├── Metrics (CPU, Memory, Connections)
├── Backups (automatic daily)
└── Networking (firewall rules)

Storage Account Dashboard:
├── Overview (usage statistics)
├── Metrics (transactions, throughput)
└── Containers (files and backups)
```

### Restart Application (if issues)

1. Go to App Service → orangehrm-app
2. Click "Restart" button at top
3. Wait 2-3 minutes for restart

### Update Application

To deploy new version:

1. Build application locally
2. Create new ZIP file
3. Go to Deployment Center
4. Upload new ZIP file
5. Wait for deployment
6. Restart if needed

---

## TROUBLESHOOTING

### Application Shows 500 Error

1. Check logs: App Service → Log stream
2. Verify database connection
3. Check `.env.local` file exists
4. Restart App Service

### Cannot Connect to Database

1. Check firewall rule allows Azure services
2. Verify credentials in `.env.local`
3. Test connection locally first
4. Check database server is running

### Installer Won't Complete

1. Wait 10 minutes after deployment
2. Check database is accessible
3. Verify all database migrations completed
4. Check file permissions on App Service

### Application is Slow

1. Check CPU/Memory metrics
2. Scale up to higher tier if needed
3. Optimize database queries
4. Enable caching

### 403 Forbidden Error

1. Check file permissions
2. Verify App Service has write access
3. Check firewall rules aren't blocking
4. Restart App Service

### 404 Not Found

1. Verify correct URL
2. Check if application deployed successfully
3. Check web.config file exists
4. Verify routing is correct

---

## IMPORTANT NOTES

### Security

⚠️ **CRITICAL:**
- [ ] Store database password securely
- [ ] Enable HTTPS only (forces all traffic to HTTPS)
- [ ] Enable backups for disaster recovery
- [ ] Monitor bills for unexpected charges
- [ ] Review access logs regularly
- [ ] Keep PHP and dependencies updated
- [ ] Use strong passwords (12+ characters, mixed case)

### Costs

Monthly cost estimates (B2 tier):
- App Service Plan (B2): $30
- MySQL Database (B1ms): $30
- Storage Account: $5
- **Total: ~$65/month**

Costs can be reduced by:
- Using B1 tier instead of B2: Save $15/month
- Reducing database backup retention
- Deleting unused resources

### Backup Strategy

- [ ] App Service: Daily backups enabled
- [ ] MySQL Database: Daily automatic backups (7 days)
- [ ] Test restore procedures monthly
- [ ] Keep offline backup of critical data
- [ ] Document recovery procedures

---

## NEXT STEPS AFTER DEPLOYMENT

1. ✓ Test application thoroughly
2. ✓ Configure your organization in OrangeHRM
3. ✓ Add employees and departments
4. ✓ Setup workflows and processes
5. ✓ Enable SSO/LDAP if needed
6. ✓ Configure email for notifications
7. ✓ Train your team on using OrangeHRM
8. ✓ Setup regular backups and monitoring
9. ✓ Plan for scaling as users grow
10. ✓ Schedule regular maintenance windows

---

## QUICK REFERENCE - RESOURCE LOCATIONS

### All Resources Created

| Resource | Location in Portal | Purpose |
|----------|-------------------|---------|
| orangehrm-rg | Resource Groups | Container for all resources |
| orangehrm-plan | Resource Groups → App Service Plans | Hosting plan |
| orangehrm-app | Resource Groups → App Services | Web application |
| orangehrm-mysql | Resource Groups → Azure Databases for MySQL | Database server |
| orangehrmsa | Resource Groups → Storage Accounts | File storage |

### Important URLs & Information

```
Application URL:
  https://orangehrm-app.azurewebsites.net

Database Connection:
  Server: orangehrm-mysql.mysql.database.azure.com
  Username: orangeadmin@orangehrm-mysql
  Database: orangehrm
  Port: 3306

SSH Access:
  https://orangehrm-app.scm.azurewebsites.net

Kudu Console:
  https://orangehrm-app.scm.azurewebsites.net/

Log Stream:
  App Service → Monitoring → Log stream
```

---

## HELPFUL AZURE CLI COMMANDS (Optional)

If you want to use command line instead of Portal:

```bash
# Login to Azure
az login

# List all resources in resource group
az resource list --resource-group orangehrm-rg

# Restart app service
az webapp restart --resource-group orangehrm-rg --name orangehrm-app

# View application settings
az webapp config appsettings list --resource-group orangehrm-rg --name orangehrm-app

# View logs
az webapp log tail --resource-group orangehrm-rg --name orangehrm-app

# Stop app service
az webapp stop --resource-group orangehrm-rg --name orangehrm-app

# Start app service
az webapp start --resource-group orangehrm-rg --name orangehrm-app

# Get database connection string
az mysql db server show-connection-string --server-name orangehrm-mysql
```

---

## COMPLETION CHECKLIST

Mark these as completed:

- [ ] Resource Group created
- [ ] App Service Plan created
- [ ] App Service created
- [ ] PHP configured (version 8.2)
- [ ] MySQL Database created
- [ ] Database firewall configured
- [ ] Storage Account created
- [ ] Application built locally
- [ ] Application deployed to Azure
- [ ] Database created and configured
- [ ] Database migrations run
- [ ] OrangeHRM installer completed
- [ ] Admin account created
- [ ] HTTPS enabled
- [ ] Backups configured
- [ ] Application tested and working

**When all items checked: ✓ DEPLOYMENT COMPLETE!**

---

## SUMMARY

**What you just deployed:**

✓ Production-ready OrangeHRM instance on Azure
✓ Scalable web application infrastructure
✓ Managed MySQL database with automated backups
✓ Storage for uploads and files
✓ HTTPS/SSL security
✓ Automatic monitoring and logging

**You now have:**

✓ Live web application at `https://orangehrm-app.azurewebsites.net`
✓ Full HR management system for your organization
✓ Secure, scalable cloud infrastructure
✓ Daily automated backups
✓ Professional monitoring and logging

**Estimated deployment time: 1-2 hours**

**Total monthly cost: $50-70** (can be reduced with smaller tiers)

---

**Congratulations! Your OrangeHRM application is now live on Azure! 🎉**

For support:
- OrangeHRM Help: https://starterhelp.orangehrm.com
- Azure Support: https://portal.azure.com (Help + Support)
- Stack Overflow: Tag your questions with `orangehrm` and `azure`
