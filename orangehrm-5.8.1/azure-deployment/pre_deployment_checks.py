"""
Pre-Deployment Checks and Validation
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from config import AzureConfig, DeploymentConfig
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PreDeploymentValidator:
    """Validates environment and prerequisites before deployment"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def check_all(self):
        """Run all validation checks"""
        logger.info("Starting pre-deployment validation...")
        
        self.check_azure_cli()
        self.check_python_version()
        self.check_dependencies()
        self.check_required_tools()
        self.check_application_structure()
        self.check_configuration()
        self.check_environment_variables()
        
        return self.print_report()
    
    def check_python_version(self):
        """Check Python version (3.8+)"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python 3.8+ required, found {version.major}.{version.minor}")
        else:
            self.info.append(f"✓ Python {version.major}.{version.minor} detected")
    
    def check_azure_cli(self):
        """Check if Azure CLI is installed"""
        try:
            result = subprocess.run(['az', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.info.append(f"✓ Azure CLI installed: {version_line}")
            else:
                self.errors.append("Azure CLI not properly installed")
        except FileNotFoundError:
            self.errors.append("Azure CLI not found. Install with: pip install azure-cli")
    
    def check_required_tools(self):
        """Check for required tools"""
        tools = {
            'git': 'Git',
            'npm': 'Node.js/npm',
            'composer': 'Composer (PHP)',
            'php': 'PHP'
        }
        
        for tool, name in tools.items():
            if shutil.which(tool):
                try:
                    result = subprocess.run([tool, '--version'], capture_output=True, text=True)
                    version = result.stdout.split('\n')[0] if result.stdout else 'installed'
                    self.info.append(f"✓ {name}: {version[:50]}")
                except:
                    self.warnings.append(f"{name} found but version check failed")
            else:
                self.warnings.append(f"{name} not found in PATH")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        required_packages = [
            'azure.identity',
            'azure.mgmt.resource',
            'azure.mgmt.web',
            'azure.mgmt.sql',
            'azure.storage.blob',
            'dotenv',
            'requests'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').split('.')[0])
            except ImportError:
                missing.append(package)
        
        if missing:
            self.errors.append(f"Missing Python packages: {', '.join(missing)}. Run: pip install -r requirements.txt")
        else:
            self.info.append(f"✓ All Python dependencies installed")
    
    def check_application_structure(self):
        """Check if application files exist"""
        required_dirs = [
            DeploymentConfig.SRC_DIR,
            DeploymentConfig.WEB_DIR,
            DeploymentConfig.INSTALLER_DIR
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                self.info.append(f"✓ Found: {dir_path.name}")
            else:
                self.errors.append(f"Missing directory: {dir_path}")
    
    def check_configuration(self):
        """Validate Azure configuration"""
        try:
            AzureConfig.validate()
            self.info.append("✓ Azure configuration validated")
        except ValueError as e:
            self.errors.append(f"Configuration error: {str(e)}")
    
    def check_environment_variables(self):
        """Check environment variables"""
        env_file = Path('.env')
        if env_file.exists():
            self.info.append(f"✓ Found .env file")
        else:
            self.warnings.append(".env file not found. Create from .env.example")
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("PRE-DEPLOYMENT VALIDATION REPORT")
        print("="*70)
        
        if self.info:
            print("\n✓ INFO:")
            for item in self.info:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n✗ ERRORS:")
            for item in self.errors:
                print(f"  {item}")
            print("\n" + "="*70)
            print("VALIDATION FAILED - Please fix errors above")
            print("="*70 + "\n")
            return False
        else:
            print("\n" + "="*70)
            print("✓ VALIDATION PASSED - Ready for deployment")
            print("="*70 + "\n")
            return True


def create_env_template():
    """Create .env.example template"""
    env_template = """# Azure Configuration
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

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
APP_REPO_PATH=.
ENABLE_BUILD=true
COMPOSER_INSTALL=true
NPM_INSTALL=true
PROD_BUILD=true
ZIP_DEPLOYMENT=true
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_template)
    
    logger.info("Created .env.example template")


if __name__ == '__main__':
    validator = PreDeploymentValidator()
    success = validator.check_all()
    
    # Create env template if it doesn't exist
    if not Path('.env.example').exists():
        create_env_template()
    
    sys.exit(0 if success else 1)
