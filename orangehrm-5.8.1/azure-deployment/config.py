"""
Configuration Management for OrangeHRM Azure Deployment
"""
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class AzureConfig:
    """Azure Configuration Settings"""
    
    # Azure Subscription
    SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID', '')
    
    # Azure Credentials
    TENANT_ID = os.getenv('AZURE_TENANT_ID', '')
    CLIENT_ID = os.getenv('AZURE_CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', '')
    
    # Resource Group
    RESOURCE_GROUP_NAME = os.getenv('RESOURCE_GROUP_NAME', 'orangehrm-rg')
    LOCATION = os.getenv('AZURE_LOCATION', 'eastus')
    
    # App Service
    APP_SERVICE_PLAN_NAME = os.getenv('APP_SERVICE_PLAN_NAME', 'orangehrm-plan')
    APP_SERVICE_NAME = os.getenv('APP_SERVICE_NAME', 'orangehrm-app')
    APP_SERVICE_SKU = os.getenv('APP_SERVICE_SKU', 'B2')  # B1, B2, S1, S2, P1, P2, P3
    
    # Database
    DB_SERVER_NAME = os.getenv('DB_SERVER_NAME', 'orangehrm-mysql')
    DB_NAME = os.getenv('DB_NAME', 'orangehrm')
    DB_ADMIN_USER = os.getenv('DB_ADMIN_USER', 'orangeadmin')
    DB_ADMIN_PASSWORD = os.getenv('DB_ADMIN_PASSWORD', '')
    DB_SKU = os.getenv('DB_SKU', 'B_Standard_B1ms')  # Burstable tier
    DB_VERSION = os.getenv('DB_VERSION', '8.0')  # MySQL version
    DB_STORAGE_SIZE = os.getenv('DB_STORAGE_SIZE', '32768')  # 32GB
    
    # Storage Account
    STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME', 'orangehrmsa')
    STORAGE_CONTAINER_NAME = os.getenv('STORAGE_CONTAINER_NAME', 'orangehrm-files')
    
    # Application Settings
    PHP_VERSION = os.getenv('PHP_VERSION', '8.2')
    NODE_VERSION = os.getenv('NODE_VERSION', '18')
    
    # OrangeHRM Configuration
    APP_NAME = 'OrangeHRM'
    APP_VERSION = '5.8.1'
    APP_REPO_PATH = os.getenv('APP_REPO_PATH', '.')
    
    # Deployment
    DEPLOY_BRANCH = os.getenv('DEPLOY_BRANCH', 'main')
    DEPLOYMENT_METHOD = os.getenv('DEPLOYMENT_METHOD', 'zip')  # zip or git
    
    @classmethod
    def validate(cls):
        """Validate all required configuration values"""
        required_fields = [
            'SUBSCRIPTION_ID',
            'TENANT_ID',
            'CLIENT_ID',
            'CLIENT_SECRET',
            'DB_ADMIN_PASSWORD'
        ]
        
        missing = []
        for field in required_fields:
            if not getattr(cls, field):
                missing.append(field)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def to_dict(cls):
        """Convert configuration to dictionary"""
        return {
            'subscription_id': cls.SUBSCRIPTION_ID,
            'tenant_id': cls.TENANT_ID,
            'client_id': cls.CLIENT_ID,
            'resource_group': cls.RESOURCE_GROUP_NAME,
            'location': cls.LOCATION,
            'app_service_name': cls.APP_SERVICE_NAME,
            'app_service_plan': cls.APP_SERVICE_PLAN_NAME,
            'db_server': cls.DB_SERVER_NAME,
            'db_name': cls.DB_NAME,
            'storage_account': cls.STORAGE_ACCOUNT_NAME,
            'php_version': cls.PHP_VERSION,
            'node_version': cls.NODE_VERSION
        }
    
    @classmethod
    def save_to_file(cls, filepath):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(cls.to_dict(), f, indent=2)


class DeploymentConfig:
    """Deployment Configuration"""
    
    # Paths
    BASE_DIR = Path(os.getenv('APP_REPO_PATH', '.'))
    SRC_DIR = BASE_DIR / 'src'
    WEB_DIR = BASE_DIR / 'web'
    INSTALLER_DIR = BASE_DIR / 'installer'
    BUILD_DIR = BASE_DIR / 'build-output'
    LOGS_DIR = BASE_DIR / 'logs'
    DIST_DIR = WEB_DIR / 'dist'
    
    # Build Settings
    ENABLE_BUILD = os.getenv('ENABLE_BUILD', 'true').lower() == 'true'
    COMPOSER_INSTALL = os.getenv('COMPOSER_INSTALL', 'true').lower() == 'true'
    NPM_INSTALL = os.getenv('NPM_INSTALL', 'true').lower() == 'true'
    PROD_BUILD = os.getenv('PROD_BUILD', 'true').lower() == 'true'
    
    # Deployment Settings
    ZIP_DEPLOYMENT = os.getenv('ZIP_DEPLOYMENT', 'true').lower() == 'true'
    PUBLISH_PROFILE_PATH = os.getenv('PUBLISH_PROFILE_PATH', '')
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        for directory in [cls.BUILD_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


class DatabaseConfig:
    """Database Configuration"""
    
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = os.getenv('DB_PORT', '3306')
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE = os.getenv('DB_NAME', 'orangehrm')
    
    # Connection parameters
    CHARSET = 'utf8mb4'
    COLLATION = 'utf8mb4_unicode_ci'


if __name__ == '__main__':
    print("Azure Configuration Loaded")
    print(json.dumps(AzureConfig.to_dict(), indent=2))
