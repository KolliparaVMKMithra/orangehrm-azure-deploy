# TROUBLESHOOTING GUIDE

## Common Issues and Solutions

---

## 🔴 Pre-Deployment Issues

### Issue 1: Python Not Found

**Error Message:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

1. **Install Python:**
   - Go to https://www.python.org/downloads/
   - Download latest Python 3.x
   - **IMPORTANT:** Check "Add Python to PATH" during installation
   - Restart your terminal

2. **Check Installation:**
   ```bash
   python --version
   ```

3. **Verify PATH:**
   - Windows: Search "Environment Variables"
   - Add Python installation path to PATH
   - Restart terminal

---

### Issue 2: Azure CLI Not Found

**Error Message:**
```
'az' is not recognized as an internal or external command
```

**Solutions:**

1. **Install Azure CLI:**
   - Go to https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
   - Download and install for your OS
   - Restart terminal

2. **Verify Installation:**
   ```bash
   az --version
   ```

3. **Troubleshoot:**
   ```bash
   # Check if installed
   where az              # Windows
   which az              # Mac/Linux
   
   # Reinstall if needed
   pip install azure-cli
   ```

---

### Issue 3: Virtual Environment Won't Activate

**Error Message:**
```
'activate' is not recognized
```

**Solutions:**

**Windows:**
```bash
# Correct command
venv\Scripts\activate

# Common mistake (use above, not this):
# source venv/bin/activate  ← This is for Mac/Linux
```

**Mac/Linux:**
```bash
# Correct command
source venv/bin/activate

# NOT on Windows
```

**If still failing:**
```bash
# Recreate virtual environment
python -m venv venv

# Then activate again (see above)
```

---

### Issue 4: "Cannot find .env file"

**Error Message:**
```
Missing required configuration
```

**Solutions:**

1. **Create .env from template:**
   ```bash
   copy .env.example .env              # Windows
   cp .env.example .env                # Mac/Linux
   ```

2. **Verify file exists:**
   ```bash
   ls -la .env                         # Mac/Linux
   dir .env                            # Windows
   ```

3. **Check file is in correct location:**
   - Should be: `azure-deployment/.env`
   - Not: `azure-deployment/.env.example`

---

## 🔴 Configuration Issues

### Issue 5: "Invalid Azure Credentials"

**Error Message:**
```
Authentication failed: Invalid credentials
```

**Solutions:**

1. **Verify Service Principal creation:**
   ```bash
   az login
   
   # Get subscription ID
   az account show --query id
   
   # Create service principal
   az ad sp create-for-rbac --name orangehrm-deployer \
     --role Contributor \
     --scopes /subscriptions/<YOUR_ID>
   ```

2. **Check .env values:**
   - Copy exact values from output above
   - No extra spaces or quotes
   - Check spelling

3. **Test Azure login:**
   ```bash
   az login
   az account show
   ```

4. **Recreate credentials if needed:**
   ```bash
   # Delete old
   az ad sp delete --id <CLIENT_ID>
   
   # Create new
   az ad sp create-for-rbac --name orangehrm-deployer \
     --role Contributor \
     --scopes /subscriptions/<YOUR_ID>
   ```

---

### Issue 6: "Resource Names Already Exist"

**Error Message:**
```
Resource 'orangehrm-app' already exists
```

**Solutions:**

1. **Use unique names in .env:**
   ```ini
   APP_SERVICE_NAME=orangehrm-yourname-12345
   DB_SERVER_NAME=orangehrm-mysql-yourname-12345
   STORAGE_ACCOUNT_NAME=orangehrm12345abc
   ```

2. **Check Azure Portal:**
   - Go to https://portal.azure.com
   - See if resource already exists
   - Delete if from previous attempt

3. **Delete entire resource group:**
   ```bash
   az group delete --resource-group orangehrm-rg --yes
   ```

---

### Issue 7: "Invalid Database Password"

**Error Message:**
```
Password validation failed
```

**Solutions:**

1. **Password Requirements:**
   - Minimum 8 characters
   - Uppercase: A-Z
   - Lowercase: a-z
   - Numbers: 0-9
   - Special: !@#$%^&*

2. **Good Passwords:**
   ```
   ✓ Or@ngeH1rM2024!
   ✓ AzureSQL#Pass123
   ✓ DB@Pass2024!Sec
   ```

3. **Bad Passwords:**
   ```
   ✗ 12345678 (numbers only)
   ✗ password (lowercase only)
   ✗ Orange@1 (too short)
   ✗ mypassword (no numbers/special)
   ```

---

## 🔴 Deployment Issues

### Issue 8: "Insufficient Azure Credits"

**Error Message:**
```
Subscription quota exceeded
InvalidTemplateDeployment
```

**Solutions:**

1. **Check credit balance:**
   - Go to https://portal.azure.com
   - Click your account (top right)
   - Select "Cost Management"
   - Check available credits

2. **Add payment method:**
   - Portal → Subscriptions
   - Click your subscription
   - Add payment method
   - Set spending limit

3. **Reduce resource size:**
   ```ini
   # Use smaller tiers temporarily
   APP_SERVICE_SKU=B1
   DB_SKU=B_Standard_B1ms
   ```

---

### Issue 9: "Deployment Timeout"

**Error Message:**
```
Operation timed out
Deployment did not complete
```

**Solutions:**

1. **Wait longer:**
   - First deployment takes 30-45 minutes
   - Azure resources can take 10+ minutes each
   - Be patient, don't interrupt

2. **Check status in Portal:**
   - Go to Resource Group
   - See resource status
   - Check if still provisioning

3. **Retry deployment:**
   - If truly hung, can restart
   - Existing resources won't conflict (checked)
   - Try again

4. **Monitor logs:**
   ```bash
   # Watch logs in real-time
   az webapp log tail --resource-group orangehrm-rg \
     --name orangehrm-app
   ```

---

### Issue 10: "Build Failed - npm not found"

**Error Message:**
```
'npm' is not recognized
npm install failed
```

**Solutions:**

1. **Install Node.js:**
   - Go to https://nodejs.org/
   - Download LTS version (16 or 18)
   - Install and select "Add to PATH"
   - Restart terminal

2. **Verify Installation:**
   ```bash
   node --version
   npm --version
   ```

3. **Manually install dependencies:**
   ```bash
   cd src/client
   npm install --production=false
   npm run build
   cd ../..
   ```

---

### Issue 11: "Build Failed - Composer not found"

**Error Message:**
```
'composer' is not recognized
composer install failed
```

**Solutions:**

1. **Install Composer:**
   - Go to https://getcomposer.org/
   - Download installer for your OS
   - Install globally

2. **Verify Installation:**
   ```bash
   composer --version
   ```

3. **Manually install dependencies:**
   ```bash
   cd src
   composer install --no-dev
   cd ..
   ```

---

### Issue 12: "ZIP Package Too Large"

**Error Message:**
```
Package exceeds size limit
Upload failed
```

**Solutions:**

1. **Exclude files from build:**
   ```bash
   # Remove node_modules
   rmdir /s /q src\node_modules
   rmdir /s /q installer\client\node_modules
   
   # Remove test directories
   rmdir /s /q src\tests
   ```

2. **Build slimmer package:**
   - Skip optional components
   - Remove development files
   - Compress aggressively

3. **Deploy in parts:**
   - Upload code via ZIP
   - Install dependencies on server
   - Run migrations after

---

## 🔴 Post-Deployment Issues

### Issue 13: "Application Won't Load"

**Error Message:**
```
404 Not Found
Connection refused
Timeout
```

**Solutions:**

1. **Wait for startup:**
   - Takes 5-10 minutes after deployment
   - App Service needs to start
   - Database needs to be ready
   - Be patient, retry in 5 minutes

2. **Check App Service status:**
   ```bash
   az webapp show --resource-group orangehrm-rg \
     --name orangehrm-app --query state
   ```

3. **Restart App Service:**
   ```bash
   az webapp restart --resource-group orangehrm-rg \
     --name orangehrm-app
   ```

4. **Check URL spelling:**
   ```
   ✓ https://orangehrm-app.azurewebsites.net
   ✗ http://orangehrm-app.azurewebsites.net (not https)
   ✗ https://orangehrm-app.azurewebsite.net (missing 's')
   ```

---

### Issue 14: "Database Connection Error"

**Error Message:**
```
Connection refused
SQLSTATE[HY000]
Cannot connect to database
```

**Solutions:**

1. **Wait for database:**
   - Can take 5-10 minutes after creation
   - Check Portal if "Creating" status
   - Wait if "Updating"

2. **Check firewall rules:**
   ```bash
   # Database should allow Azure services
   az mysql db server firewall-rule list \
     --resource-group orangehrm-rg \
     --server-name orangehrm-mysql
   ```

3. **Verify connection string:**
   - Should be: `mysql://user:pass@server.mysql.database.azure.com:3306/db`
   - Check no typos in password
   - Check server name is correct

4. **Test connection locally:**
   ```bash
   mysql -h orangehrm-mysql.mysql.database.azure.com \
     -u orangeadmin@orangehrm-mysql \
     -p
   ```

---

### Issue 15: "500 Internal Server Error"

**Error Message:**
```
500 Internal Server Error
White Page
Application Error
```

**Solutions:**

1. **View logs:**
   ```bash
   # Real-time logs
   az webapp log tail --resource-group orangehrm-rg \
     --name orangehrm-app
   
   # Download all logs
   az webapp log download --resource-group orangehrm-rg \
     --name orangehrm-app --log-file logs.zip
   ```

2. **Check common issues:**
   - Database migrations failed
   - File permissions wrong
   - PHP extensions missing
   - Memory limit exceeded

3. **Enable debugging:**
   ```bash
   az webapp config appsettings set \
     --resource-group orangehrm-rg \
     --name orangehrm-app \
     --settings APP_DEBUG=1
   ```

4. **Check disk space:**
   - Application might be out of space
   - Check storage limits
   - Clean old files

---

### Issue 16: "Installer Won't Complete"

**Error Message:**
```
Installer stuck on step
Cannot save configuration
Database check fails
```

**Solutions:**

1. **Verify database is ready:**
   - Wait full 5-10 minutes after setup
   - Test connection manually
   - Check firewall allows connection

2. **Check file permissions:**
   ```bash
   # Ensure app service can write
   # Usually automatic, but verify in portal
   ```

3. **Clear installer cache:**
   - Delete `/installer/temp/` directory
   - Reload installer page
   - Try again

4. **Manual database setup:**
   - If installer won't work
   - Run migrations manually
   - Check logs for specific error

---

### Issue 17: "Performance Issues - Slow Application"

**Error Message:**
```
Application is slow
Pages load slowly
Database queries slow
```

**Solutions:**

1. **Scale up resources:**
   ```bash
   # Upgrade App Service
   az appservice plan update --resource-group orangehrm-rg \
     --name orangehrm-plan --sku S1
   
   # Upgrade Database
   az mysql db server update --name orangehrm-mysql \
     --resource-group orangehrm-rg --sku-name B_Standard_B2s
   ```

2. **Check metrics:**
   - Portal → App Service → Metrics
   - Check CPU, memory, response time
   - Identify bottleneck

3. **Optimize application:**
   - Check database indexes
   - Enable caching
   - Optimize queries
   - Enable compression

---

## 🟢 Logging & Debugging

### Enable Verbose Logging

```bash
# Python scripts with debug
python deployment_orchestrator.py --debug

# Azure logs
az webapp log config --resource-group orangehrm-rg \
  --name orangehrm-app --web-server-logging filesystem

# View logs
az webapp log tail --resource-group orangehrm-rg \
  --name orangehrm-app --lines 50
```

### Check Script Logs

```bash
# Deployment log
cat logs/deployment.log      # Mac/Linux
type logs\deployment.log     # Windows

# Search for errors
grep ERROR logs/deployment.log
```

---

## 🟡 When Nothing Works

### Nuclear Option: Start Fresh

```bash
# Delete all resources
az group delete --resource-group orangehrm-rg --yes --no-wait

# Wait 5 minutes for deletion

# Start over
python deployment_orchestrator.py
```

### Get Help

1. **Check detailed log:**
   ```bash
   cat logs/deployment.log | grep -i error
   ```

2. **Test individual components:**
   ```bash
   python pre_deployment_checks.py
   python azure_setup.py
   python database_setup.py
   python build_and_deploy.py
   ```

3. **Manual Azure Portal check:**
   - https://portal.azure.com
   - Check each resource status
   - Look for error messages

4. **Contact Support:**
   - OrangeHRM: https://starterhelp.orangehrm.com
   - Azure: https://azure.microsoft.com/en-us/support/
   - Stack Overflow: Tag your question

---

## 📞 Quick Checklist

Before contacting support, verify:

- [ ] .env file exists and is filled correctly
- [ ] Service Principal has Contributor role
- [ ] Azure subscription has available credits
- [ ] All required tools installed and in PATH
- [ ] Pre-deployment validation passes
- [ ] Checked logs for specific error
- [ ] Tried restarting application
- [ ] Waited sufficient time for provisioning
- [ ] No typos in resource names
- [ ] Database firewall allows Azure services

---

## 📚 Reference

**Script Output Locations:**
- Logs: `logs/deployment.log`
- Built package: `build-output/orangehrm-deploy.zip`
- Configuration: `.env`

**Useful Commands:**
```bash
# Status
az group show --name orangehrm-rg

# Restart
az webapp restart --resource-group orangehrm-rg --name orangehrm-app

# Clean
az group delete --resource-group orangehrm-rg --yes

# Connect
az mysql db server show --resource-group orangehrm-rg --name orangehrm-mysql
```

---

**Good luck! Most issues are fixable with a little patience and debugging.** 🚀
