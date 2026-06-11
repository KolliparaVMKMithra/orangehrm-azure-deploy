# How to Find and Create Web App / App Service in Azure Portal

## Quick Answer

**"Web App" = "App Service"** - They're the same thing in Azure Portal

The resource might be called:
- **Web App** (most common in newer Portal)
- **App Service** (older Portal name)
- **App Service (Web App)** (sometimes shows both)

---

## WHERE TO FIND IT IN AZURE PORTAL

### Method 1: Quick Search (EASIEST)

1. **Go to Azure Portal**
   - https://portal.azure.com

2. **Use Search Bar at Top**
   - Click search box at very top of page (🔍)
   - Type: `web app`
   - Or type: `app service`

3. **Click Result**
   - You'll see: "Web App" or "App Service" in results
   - Click it
   - Then click "Create" button

### Method 2: Create Resource Page

1. **Click "Create a resource"**
   - At top left, or search for "Create a resource"

2. **Search**
   - In the search box, type: `web app`
   - Or: `app service`

3. **Click Result**
   - Should show: "Web App" 
   - Click it
   - Click "Create" button

### Method 3: Browse Categories

1. **Click "Create a resource"**

2. **Look for Categories** (on left side or top)
   - Scroll through categories
   - Look for "Compute"
   - Or look for "Web"

3. **Find Web App / App Service**
   - Should be there
   - Click "Create"

---

## EXACT STEPS IN AZURE PORTAL (Updated)

### Step 1: Search for Web App

```
Azure Portal Home
    ↓
🔍 Search Box (top center)
    ↓
Type: "web app"
    ↓
Click: "Web App" from results
```

### Step 2: Create Web App

```
Web App page
    ↓
Click: "Create" button
    ↓
Shows: Web App Creation Form
```

### Step 3: Fill in Details

The form will show tabs:
- **Basics** (most important - fill this first)
- MySQL
- Deployment
- Monitoring
- Tags

**In Basics tab, fill:**
```
Subscription:        [Your subscription]
Resource group:      orangehrm-rg (select from dropdown)
Name:               orangehrm-app (must be unique)
Publish:            Code
Runtime stack:      PHP 8.2 (select from dropdown)
Operating System:   Linux
Region:             [Same as resource group - eastus, etc.]
App Service Plan:   orangehrm-plan (click "Create new" if doesn't exist)
```

### Step 4: Click "Review + Create"

- Scroll down
- Click blue "Review + create" button
- Check all settings
- Click "Create" button

---

## IF YOU STILL CAN'T FIND IT

### Troubleshooting

**Problem: "Web App" option not showing**

Solution 1: Try searching different terms:
```
Search for:
- "web app"
- "app service"  
- "php"
- "create web"
```

Solution 2: Make sure you're logged in
- Check account at top right
- Should show your email/name
- If not, click and login

Solution 3: Check subscription
- Top left should show your subscription
- If it says "No subscriptions", switch accounts

Solution 4: Go directly to this URL
```
https://portal.azure.com/#create/Microsoft.WebSite
```
This should open Web App creation page directly

---

## SCREENSHOTS DESCRIPTIONS

### In Azure Portal, you'll see:

**Top Search Bar Area:**
```
┌─────────────────────────────────────────────┐
│ 🔍 Search resources, services, docs...     │  ← Click here
└─────────────────────────────────────────────┘
```

**After typing "web app":**
```
Search Results:
┌─────────────────────┐
│ Web App             │ ← Click this
│ Web App for        │
│   Containers       │
│ App Service        │  ← Or this
│ App Service Plan   │
└─────────────────────┘
```

**Click either "Web App" or "App Service"**

Both will take you to the same creation page.

---

## COMPARISON TABLE

| Term | Same? | Where Found | Status |
|------|-------|-------------|--------|
| Web App | ✓ YES | Azure Portal search | Current name |
| App Service | ✓ YES | Azure Portal search | Also valid |
| App Service Plan | ✗ NO | Different resource | For compute resources |
| App Service (Web App) | ✓ YES | Some Portal pages | Shows both names |
| Web App for Containers | ✗ NO | Different option | For Docker containers |

---

## QUICK FIX - DIRECT LINK

If you're having trouble finding it, use this direct link:

```
https://portal.azure.com/#create/Microsoft.WebSite
```

Paste this into your browser and it will open the **Web App creation page** directly.

---

## STEP-BY-STEP WITH PICTURES (Text Description)

### Step 1: Open Azure Portal
```
1. Go to https://portal.azure.com
2. You see the Portal homepage
3. At TOP CENTER, there's a search box (like Google Search)
4. It says: "🔍 Search resources, services, docs..."
```

### Step 2: Search for Web App
```
1. Click on the search box
2. Type: web app
3. You see dropdown with results
4. First result should be: "Web App" (with a blue icon)
5. Click it
```

### Step 3: Create Web App
```
1. You're now on "Web App" page
2. Click big blue button: "Create"
3. Form appears with empty fields
```

### Step 4: Fill Basic Information
```
Subscription:        [Click dropdown, select yours]
Resource group:      [Click dropdown, select "orangehrm-rg"]
Name:               [Type: orangehrm-app]
Publish:            [Select: Code]
Runtime stack:      [Click dropdown, find and select: PHP 8.2]
Operating System:   [Select: Linux]
Region:             [Select: Same as your resource group]
App Service Plan:   [Click "Create new" if needed]
```

### Step 5: Create App Service Plan
```
If you clicked "Create new" for App Service Plan:
1. New form appears
2. Fill:
   - Name: orangehrm-plan
   - Operating System: Linux
   - Region: [Same as above]
   - Sku and size: [Click "Change size"]
   - Select: B2 (Basic, $30/month)
3. Click "OK"
```

### Step 6: Review and Create
```
1. Scroll down
2. Click blue "Review + create" button
3. Check all your entries
4. If correct, click "Create"
5. Wait for deployment (shows progress)
```

---

## WHAT YOU'RE CREATING

When you create a **Web App**, you're creating:

```
Web App (Container for your application)
    ↓
App Service Plan (Computing resources)
    ↓
Linux Machine with PHP 8.2 Runtime
    ↓
Ready to host OrangeHRM application
```

---

## COMMON CONFUSION

### "What's the difference between..."

**Web App vs App Service?**
- Same thing - Microsoft just renamed it
- "Web App" is the newer name
- Both terms work

**Web App vs App Service Plan?**
- Web App = Your application
- App Service Plan = The underlying server/resources
- You need BOTH

**Web App vs Web App for Containers?**
- Web App = Regular PHP/Node/Python/etc.
- Web App for Containers = Docker containers only
- Use regular "Web App" for OrangeHRM

---

## AFTER YOU CREATE WEB APP

Once created, you should see:

```
In Resource Group (orangehrm-rg):
✓ orangehrm-plan (App Service Plan)
✓ orangehrm-app (Web App)
```

Then you can:
1. ✓ Configure PHP settings
2. ✓ Deploy your application
3. ✓ Setup database
4. ✓ Run installer

---

## IF STILL STUCK

Try this exact URL:
```
https://portal.azure.com/#create/Microsoft.WebSite
```

This opens Web App creation form directly - should work no matter what.

---

**Still having trouble? Let me know and I can take you through each click step-by-step!** 👍
