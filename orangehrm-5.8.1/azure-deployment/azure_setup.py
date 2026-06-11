"""
Azure Resource Setup and Provisioning
"""
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import ResourceExistsError
from config import AzureConfig
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureResourceManager:
    """Manages Azure resource creation and provisioning"""
    
    def __init__(self):
        """Initialize Azure clients"""
        self.config = AzureConfig
        self.authenticate()
        self.subscription_id = self.config.SUBSCRIPTION_ID
        
    def authenticate(self):
        """Authenticate with Azure using service principal"""
        logger.info("Authenticating with Azure...")
        
        try:
            self.credential = ClientSecretCredential(
                tenant_id=self.config.TENANT_ID,
                client_id=self.config.CLIENT_ID,
                client_secret=self.config.CLIENT_SECRET
            )
            
            # Initialize clients
            self.resource_client = ResourceManagementClient(
                self.credential, self.subscription_id
            )
            self.web_client = WebSiteManagementClient(
                self.credential, self.subscription_id
            )
            self.sql_client = SqlManagementClient(
                self.credential, self.subscription_id
            )
            self.storage_client = StorageManagementClient(
                self.credential, self.subscription_id
            )
            self.network_client = NetworkManagementClient(
                self.credential, self.subscription_id
            )
            
            logger.info("✓ Successfully authenticated with Azure")
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def create_resource_group(self):
        """Create Azure resource group"""
        logger.info(f"Creating resource group: {self.config.RESOURCE_GROUP_NAME}...")
        
        try:
            resource_group_params = {
                'location': self.config.LOCATION
            }
            
            self.resource_client.resource_groups.create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                resource_group_params
            )
            
            logger.info(f"✓ Resource group created: {self.config.RESOURCE_GROUP_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create resource group: {str(e)}")
            return False
    
    def create_app_service_plan(self):
        """Create Azure App Service Plan"""
        logger.info(f"Creating App Service Plan: {self.config.APP_SERVICE_PLAN_NAME}...")
        
        try:
            app_service_plan = {
                'location': self.config.LOCATION,
                'sku': {
                    'name': self.config.APP_SERVICE_SKU,
                    'tier': self._get_tier_from_sku(self.config.APP_SERVICE_SKU)
                }
            }
            
            result = self.web_client.app_service_plans.begin_create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                self.config.APP_SERVICE_PLAN_NAME,
                app_service_plan
            ).result()
            
            logger.info(f"✓ App Service Plan created: {self.config.APP_SERVICE_PLAN_NAME}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create App Service Plan: {str(e)}")
            return None
    
    def create_app_service(self):
        """Create Azure App Service"""
        logger.info(f"Creating App Service: {self.config.APP_SERVICE_NAME}...")
        
        try:
            app_service = {
                'location': self.config.LOCATION,
                'server_farm_id': f"/subscriptions/{self.subscription_id}/resourceGroups/{self.config.RESOURCE_GROUP_NAME}/providers/Microsoft.Web/serverfarms/{self.config.APP_SERVICE_PLAN_NAME}",
                'site_config': {
                    'php_version': self.config.PHP_VERSION,
                    'web_sockets_enabled': True,
                    'app_settings': [
                        {'name': 'COMPOSER_EXTENSIONS', 'value': 'true'},
                        {'name': 'COMPOSER_AUTOLOADER_SUFFIX', 'value': 'STG'},
                    ]
                }
            }
            
            result = self.web_client.web_apps.begin_create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                self.config.APP_SERVICE_NAME,
                app_service
            ).result()
            
            logger.info(f"✓ App Service created: {self.config.APP_SERVICE_NAME}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create App Service: {str(e)}")
            return None
    
    def create_mysql_database(self):
        """Create Azure Database for MySQL"""
        logger.info(f"Creating MySQL Server: {self.config.DB_SERVER_NAME}...")
        
        try:
            mysql_server = {
                'location': self.config.LOCATION,
                'sku': {
                    'name': self.config.DB_SKU,
                    'tier': 'Burstable'
                },
                'storage': {
                    'storageSizeGB': int(self.config.DB_STORAGE_SIZE)
                },
                'backup': {
                    'backupRetentionDays': 7,
                    'geoRedundantBackup': 'Disabled'
                },
                'version': self.config.DB_VERSION,
                'administrator_login': self.config.DB_ADMIN_USER,
                'administrator_login_password': self.config.DB_ADMIN_PASSWORD,
            }
            
            result = self.sql_client.servers.begin_create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                self.config.DB_SERVER_NAME,
                mysql_server
            ).result()
            
            logger.info(f"✓ MySQL Server created: {self.config.DB_SERVER_NAME}")
            
            # Create database
            self.create_database()
            
            # Configure firewall rules
            self.configure_firewall_rules()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create MySQL Server: {str(e)}")
            return None
    
    def create_database(self):
        """Create OrangeHRM database"""
        logger.info(f"Creating database: {self.config.DB_NAME}...")
        
        try:
            database = {
                'location': self.config.LOCATION,
                'collation': 'utf8_general_ci'
            }
            
            # This is a simplified approach - actual MySQL database creation
            # might require direct connection after server is created
            logger.info(f"✓ Database setup will be completed during migration")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {str(e)}")
            return False
    
    def configure_firewall_rules(self):
        """Configure Azure firewall rules for database access"""
        logger.info("Configuring firewall rules...")
        
        try:
            # Allow Azure services
            firewall_rule = {
                'start_ip_address': '0.0.0.0',
                'end_ip_address': '0.0.0.0'
            }
            
            self.sql_client.firewall_rules.create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                self.config.DB_SERVER_NAME,
                'AllowAllAzureIps',
                firewall_rule
            )
            
            logger.info("✓ Firewall rules configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure firewall: {str(e)}")
            return False
    
    def create_storage_account(self):
        """Create Azure Storage Account"""
        logger.info(f"Creating Storage Account: {self.config.STORAGE_ACCOUNT_NAME}...")
        
        try:
            storage_account = {
                'location': self.config.LOCATION,
                'sku': {
                    'name': 'Standard_LRS'
                },
                'kind': 'StorageV2',
                'access_tier': 'Hot'
            }
            
            result = self.storage_client.storage_accounts.begin_create_or_update(
                self.config.RESOURCE_GROUP_NAME,
                self.config.STORAGE_ACCOUNT_NAME,
                storage_account
            ).result()
            
            logger.info(f"✓ Storage Account created: {self.config.STORAGE_ACCOUNT_NAME}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create Storage Account: {str(e)}")
            return None
    
    def setup_all_resources(self):
        """Setup all Azure resources"""
        logger.info("="*70)
        logger.info("STARTING AZURE RESOURCE PROVISIONING")
        logger.info("="*70)
        
        success = True
        
        # Create resource group
        if not self.create_resource_group():
            success = False
        
        time.sleep(5)  # Wait for resource group to be ready
        
        # Create App Service Plan
        if not self.create_app_service_plan():
            success = False
        
        # Create App Service
        if not self.create_app_service():
            success = False
        
        # Create MySQL Database
        if not self.create_mysql_database():
            success = False
        
        time.sleep(10)  # Wait for database to be ready
        
        # Create Storage Account
        if not self.create_storage_account():
            success = False
        
        logger.info("="*70)
        if success:
            logger.info("✓ AZURE RESOURCE PROVISIONING COMPLETED SUCCESSFULLY")
        else:
            logger.info("✗ AZURE RESOURCE PROVISIONING COMPLETED WITH ERRORS")
        logger.info("="*70)
        
        return success
    
    @staticmethod
    def _get_tier_from_sku(sku):
        """Get tier name from SKU"""
        tier_mapping = {
            'F1': 'Free', 'D1': 'Shared',
            'B1': 'Basic', 'B2': 'Basic', 'B3': 'Basic',
            'S1': 'Standard', 'S2': 'Standard', 'S3': 'Standard',
            'P1': 'Premium', 'P2': 'Premium', 'P3': 'Premium'
        }
        return tier_mapping.get(sku, 'Standard')


def main():
    """Main function"""
    try:
        manager = AzureResourceManager()
        success = manager.setup_all_resources()
        
        if success:
            logger.info("\n✓ All resources created successfully!")
            logger.info("Next steps:")
            logger.info("1. Note down the resource names")
            logger.info("2. Run: python database_setup.py")
            logger.info("3. Run: python build_and_deploy.py")
        else:
            logger.error("\n✗ Some resources failed to create. Check logs above.")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == '__main__':
    main()
