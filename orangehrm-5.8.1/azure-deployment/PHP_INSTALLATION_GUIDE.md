# How to Install PHP on Windows

Complete step-by-step guide to install PHP 8.2 on Windows for OrangeHRM deployment.

---

## TABLE OF CONTENTS

1. [Download PHP](#download-php)
2. [Extract PHP](#extract-php)
3. [Configure PHP](#configure-php)
4. [Add to System PATH](#add-to-system-path)
5. [Install Required Extensions](#install-required-extensions)
6. [Verify Installation](#verify-installation)
7. [Troubleshooting](#troubleshooting)

---

## STEP 1: DOWNLOAD PHP

**Estimated Time: 5 minutes**

### Download PHP 8.2

1. **Go to PHP Download Page**
   - Open: https://www.php.net/downloads
   - You should see "PHP 8.2" as latest stable version

2. **Click PHP 8.2 Download**
   - You'll see "Current Stable PHP 8.2.x Version"
   - Click the version number (e.g., "8.2.19")

3. **Select Windows Download**
   - You'll see different download options
   - Look for **Windows downloads** section
   - Choose based on your system:

   **For Most Windows Users:**
   - Click **"Zip"** next to "VC16 x64"
   - This is the recommended version
   - File will be named something like: `php-8.2.19-Win32-vs16-x64.zip`

   **What do these mean?**
   - **VC16:** Visual Studio 2019 runtime (most compatible)
   - **x64:** 64-bit version (for modern Windows)
   - **Zip:** Portable version (no installer needed)

4. **Click Download**
   - Browser will download the ZIP file
   - Should be 30-50 MB
   - Wait for download to complete

### Verify Download

- Check your Downloads folder
- Should see file like: `php-8.2.19-Win32-vs16-x64.zip`
- File size: ~40-50 MB

---

## STEP 2: EXTRACT PHP

**Estimated Time: 3 minutes**

### Extract to Program Files

1. **Open Downloads Folder**
   - Windows: Press `Windows Key + E` to open File Explorer
   - Navigate to: `C:\Users\[YourUsername]\Downloads`

2. **Find PHP ZIP File**
   - Look for: `php-8.2.*.zip` file
   - Right-click on it

3. **Extract the ZIP**
   - Right-click → "Extract All..."
   - Or use 7-Zip: "7-Zip" → "Extract Here"

4. **Create PHP Directory**
   - You need to put PHP in Program Files
   - Create folder: `C:\php`
   - Steps:
     - Open File Explorer
     - Go to: `C:\` (root drive)
     - Right-click in empty space
     - Select "New" → "Folder"
     - Name it: `php`

5. **Move Extracted Files to C:\php**
   - Extract downloaded ZIP (creates a folder with PHP files)
   - Cut all files from extracted folder
   - Paste into `C:\php`
   - Should now have: `C:\php\php.exe`, `C:\php\php.ini-production`, etc.

### Verify Extraction

```
C:\php should contain:
✓ php.exe (the main executable)
✓ php-cgi.exe
✓ php.ini-production (configuration template)
✓ php.ini-development (configuration template)
✓ ext/ folder (extensions)
✓ Many other files
```

---

## STEP 3: CONFIGURE PHP

**Estimated Time: 3 minutes**

### Create PHP Configuration File

1. **Go to C:\php Directory**
   - Open File Explorer
   - Navigate to: `C:\php`

2. **Find Configuration Files**
   - You should see: `php.ini-production` and `php.ini-development`
   - For production: use `php.ini-production`
   - For development: use `php.ini-development`

3. **Create php.ini**
   - Right-click on `php.ini-production`
   - Select "Copy"
   - Right-click in empty space
   - Select "Paste"
   - Rename to: `php.ini`
   - Now you have: `php.ini` (this is the active config)

### Edit PHP Configuration

1. **Open php.ini**
   - Right-click on `php.ini`
   - Select "Open with" → "Notepad"

2. **Enable Required Extensions**
   - Find these lines and uncomment them (remove `;` at start):
   
   ```ini
   ; Find these lines and uncomment:
   
   extension=pdo_mysql
   extension=curl
   extension=json
   extension=mbstring
   extension=zip
   extension=dom
   extension=xml
   extension=simplexml
   extension=gd
   extension=ldap
   extension=openssl
   ```

   **How to uncomment:**
   - Find the line (use Ctrl+F to search)
   - If line starts with `;extension=curl`
   - Change to: `extension=curl` (remove the `;`)

3. **Set Extension Directory**
   - Find line: `;extension_dir = "ext"`
   - Change to: `extension_dir = "C:\php\ext"`
   - Remove the `;` at beginning

4. **Set Timezone (Optional)**
   - Find: `;date.timezone =`
   - Change to: `date.timezone = UTC`
   - Or use your timezone (e.g., `America/New_York`, `Europe/London`, etc.)

5. **Increase Memory Limit (Optional but Recommended)**
   - Find: `memory_limit = 128M`
   - Change to: `memory_limit = 512M` (for better performance)

6. **Save File**
   - Press Ctrl+S
   - Close Notepad

### Verify Extensions Folder

- In `C:\php\` folder, you should have `ext` subfolder
- Open it: `C:\php\ext`
- Should see `.dll` files like:
  ```
  ✓ php_pdo_mysql.dll
  ✓ php_curl.dll
  ✓ php_mbstring.dll
  ✓ php_xml.dll
  ✓ php_gd.dll
  ```

---

## STEP 4: ADD TO SYSTEM PATH

**Estimated Time: 5 minutes**

This allows you to run `php` command from anywhere in terminal.

### Add PHP to Windows PATH

1. **Open Environment Variables**
   - Press: `Windows Key + X`
   - Select: "System"
   - Or search for: "Environment Variables"

2. **Go to Environment Variables**
   - In System window, click: "Advanced system settings"
   - Click: "Environment Variables" button (bottom right)

3. **Edit PATH Variable**
   - Under "System variables" section (lower half)
   - Find and click: `Path`
   - Click: "Edit" button

4. **Add PHP Path**
   - Click: "New" button
   - Type: `C:\php`
   - Click: "OK"

5. **Apply and Close**
   - Click: "OK" on all dialogs
   - Close all windows

6. **Restart Terminal**
   - Close any open PowerShell or Command Prompt windows
   - **Important:** Must restart terminal for PATH changes to take effect
   - Open new PowerShell or Command Prompt

### Verify PATH Update

```powershell
# In new terminal/PowerShell window, type:
php --version

# Should show something like:
# PHP 8.2.19 (cli) (built: ...)
# Zend Engine v4.2.x ...
```

---

## STEP 5: INSTALL REQUIRED EXTENSIONS

**Estimated Time: 2 minutes**

### Verify All Extensions are Present

Open PowerShell and check which extensions are available:

```powershell
php -m
```

This lists all loaded extensions. Should see:

```
✓ PDO
✓ pdo_mysql
✓ cURL
✓ json
✓ mbstring
✓ zip
✓ DOM
✓ xml
✓ SimpleXML
✓ gd
✓ openssl
```

### If Extensions Are Missing

**For PDO MySQL:**
1. Go to `C:\php\php.ini`
2. Find and uncomment: `extension=pdo_mysql`
3. Verify `C:\php\ext\php_pdo_mysql.dll` exists
4. Restart terminal

**For Other Extensions:**
- Same process as above
- Find extension line in `php.ini`
- Uncomment it (remove `;`)
- Restart terminal

### Verify Installation

```powershell
# Check specific extension
php -r "phpinfo();" | findstr "PDO"

# Or just run phpinfo to see all info
php -r "phpinfo();"
```

---

## STEP 6: VERIFY INSTALLATION

**Estimated Time: 2 minutes**

### Run Verification Commands

Open PowerShell and run:

```powershell
# Check PHP version
php --version

# Check loaded extensions
php -m

# Check specific extensions
php -r "echo 'PDO: ' . (extension_loaded('pdo_mysql') ? 'YES' : 'NO') . PHP_EOL;"
php -r "echo 'CURL: ' . (extension_loaded('curl') ? 'YES' : 'NO') . PHP_EOL;"
php -r "echo 'MBSTRING: ' . (extension_loaded('mbstring') ? 'YES' : 'NO') . PHP_EOL;"
```

### Expected Output

```
PHP 8.2.19 (cli) (built: ...)
Zend Engine v4.2.x ...

// And when checking modules:
[PHP Modules]
...
PDO
pdo_mysql
curl
json
mbstring
zip
...
```

---

## STEP 7: TROUBLESHOOTING

### Issue: "php command not found"

**Solution:**
1. Check PHP is in `C:\php`
2. Verify `php.exe` exists there
3. Check PATH was added (type: `echo $env:Path` in PowerShell)
4. Restart PowerShell after adding PATH
5. Try again

### Issue: Extensions Not Loading

**Symptom:** `php -m` doesn't show expected extensions

**Solution:**
1. Verify extension is uncommented in `php.ini`
2. Verify DLL file exists in `C:\php\ext`
3. Check extension_dir is set correctly in php.ini
4. Restart PowerShell
5. Check for errors: `php -r "phpinfo();"` and look for errors

### Issue: "VC16 Redistributable Not Found"

**Symptom:** Error about missing Visual Studio runtime

**Solution:**
1. Download Visual Studio 2019 Runtime:
   https://support.microsoft.com/en-us/help/2977003/
2. Or download from Microsoft:
   https://visualstudio.microsoft.com/downloads/
3. Choose: Visual Studio 2019 → Tools and Libraries
4. Select: VC++ 2019 Redistributable
5. Install it
6. Try PHP again

### Issue: Some Extensions Won't Load

**Symptom:** Error loading certain DLLs

**Solution:**
1. Some extensions have dependencies
2. Try installing Visual C++ runtime (see above)
3. Or download precompiled extensions from:
   https://windows.php.net/downloads/pecl/

### Issue: PHP Runs But Configuration Not Applied

**Symptom:** Extensions or settings don't seem to work

**Solution:**
1. Check you edited correct file: `C:\php\php.ini`
2. Not: `php.ini-production` or `php.ini-development`
3. Restart terminal/PowerShell
4. Verify: `php --ini` shows `Loaded Configuration File: C:\php\php.ini`

---

## NEXT STEPS

After PHP is installed and verified:

1. ✓ Install Node.js (if not already)
   - https://nodejs.org/

2. ✓ Install Composer (PHP package manager)
   - https://getcomposer.org/

3. ✓ Verify all tools:
   ```powershell
   php --version
   composer --version
   node --version
   npm --version
   git --version
   ```

4. ✓ Continue with OrangeHRM deployment

---

## QUICK REFERENCE

### PHP Installation Summary

```
1. Download PHP 8.2 (VC16 x64 Zip) from https://www.php.net/downloads
2. Extract to C:\php
3. Copy php.ini-production to php.ini
4. Uncomment required extensions in php.ini
5. Set extension_dir = C:\php\ext
6. Add C:\php to Windows PATH
7. Restart terminal
8. Verify: php --version
9. Check extensions: php -m
```

### Commands Reference

```powershell
# Verify PHP installed
php --version

# List all loaded extensions
php -m

# Show PHP configuration
php --ini

# Run PHP code
php -r "echo 'Hello PHP';"

# Check specific extension
php -r "echo extension_loaded('pdo_mysql') ? 'YES' : 'NO';"

# Full phpinfo (lots of info!)
php -r "phpinfo();"
```

### Important Paths

```
PHP Installation:     C:\php
Configuration File:   C:\php\php.ini
Extensions:          C:\php\ext
Main Executable:     C:\php\php.exe
```

---

## VERIFY YOUR INSTALLATION

After installation, in PowerShell, paste this and run:

```powershell
Write-Host "=== PHP Installation Check ===" -ForegroundColor Green
Write-Host ""

# Check PHP version
Write-Host "1. PHP Version:" -ForegroundColor Yellow
php --version
Write-Host ""

# Check Extensions
Write-Host "2. Required Extensions:" -ForegroundColor Yellow
php -r "
\$extensions = ['pdo_mysql', 'curl', 'json', 'mbstring', 'zip', 'dom', 'xml', 'simplexml', 'gd', 'openssl'];
foreach(\$ext in \$extensions) {
    \$status = extension_loaded(\$ext) ? 'YES' : 'NO';
    echo \$ext . ': ' . \$status . PHP_EOL;
}
"
Write-Host ""

# Check Configuration
Write-Host "3. PHP Configuration:" -ForegroundColor Yellow
php --ini
```

This will show you everything you need to verify PHP is properly installed.

---

**PHP Installation Complete! Ready for next steps. 🎉**

Next: Install Composer (PHP package manager)
