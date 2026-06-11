"""
Build and Deployment Script for Azure
"""
import os
import sys
import subprocess
import logging
import shutil
import zipfile
from pathlib import Path
from config import AzureConfig, DeploymentConfig
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ApplicationBuilder:
    """Builds OrangeHRM application for deployment"""
    
    def __init__(self):
        self.config = AzureConfig
        self.deploy_config = DeploymentConfig
        self.base_dir = Path(self.config.APP_REPO_PATH)
        
    def install_php_dependencies(self):
        """Install PHP dependencies with Composer"""
        logger.info("Installing PHP dependencies...")
        
        try:
            src_dir = self.base_dir / 'src'
            
            if not src_dir.exists():
                logger.error(f"Source directory not found: {src_dir}")
                return False
            
            os.chdir(src_dir)
            
            # Run composer install
            command = ['composer', 'install', '--no-dev', '--optimize-autoloader']
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ PHP dependencies installed")
                return True
            else:
                logger.error(f"Composer install failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install PHP dependencies: {str(e)}")
            return False
    
    def install_node_dependencies(self):
        """Install Node.js dependencies"""
        logger.info("Installing Node.js dependencies...")
        
        try:
            client_dir = self.base_dir / 'src' / 'client'
            
            if not client_dir.exists():
                logger.warning(f"Client directory not found: {client_dir}")
                return False
            
            os.chdir(client_dir)
            
            # Run npm install
            command = ['npm', 'install', '--production=false']
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Node.js dependencies installed")
                return True
            else:
                logger.error(f"NPM install failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install Node.js dependencies: {str(e)}")
            return False
    
    def build_frontend(self):
        """Build Vue.js frontend"""
        logger.info("Building frontend...")
        
        try:
            client_dir = self.base_dir / 'src' / 'client'
            
            if not client_dir.exists():
                logger.warning(f"Client directory not found: {client_dir}")
                return False
            
            os.chdir(client_dir)
            
            # Run build
            command = ['npm', 'run', 'build']
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Frontend built successfully")
                return True
            else:
                logger.error(f"Frontend build failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to build frontend: {str(e)}")
            return False
    
    def build_installer(self):
        """Build installer frontend"""
        logger.info("Building installer UI...")
        
        try:
            installer_dir = self.base_dir / 'installer' / 'client'
            
            if not installer_dir.exists():
                logger.warning(f"Installer directory not found: {installer_dir}")
                return True  # Optional
            
            os.chdir(installer_dir)
            
            # Run build
            command = ['npm', 'run', 'build']
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Installer UI built successfully")
                return True
            else:
                logger.warning(f"Installer build failed (optional): {result.stderr}")
                return True  # Optional
                
        except Exception as e:
            logger.warning(f"Failed to build installer (optional): {str(e)}")
            return True  # Optional
    
    def create_deployment_package(self):
        """Create deployment package (ZIP file)"""
        logger.info("Creating deployment package...")
        
        try:
            # Create build directory
            self.deploy_config.create_directories()
            
            # Define output zip
            zip_path = self.deploy_config.BUILD_DIR / 'orangehrm-deploy.zip'
            
            # Files/folders to include
            include_paths = [
                self.base_dir / 'src',
                self.base_dir / 'web',
                self.base_dir / 'bin',
                self.base_dir / 'lib',
                self.base_dir / 'index.php',
                self.base_dir / 'README.md'
            ]
            
            # Create zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for path in include_paths:
                    if path.exists():
                        if path.is_file():
                            arcname = path.name
                            zipf.write(path, arcname)
                            logger.info(f"  Added: {arcname}")
                        else:
                            # Add directory
                            for root, dirs, files in os.walk(path):
                                for file in files:
                                    file_path = Path(root) / file
                                    arcname = file_path.relative_to(self.base_dir)
                                    zipf.write(file_path, arcname)
                    else:
                        logger.warning(f"Path not found: {path}")
            
            logger.info(f"✓ Deployment package created: {zip_path}")
            logger.info(f"  Size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
            
            return str(zip_path)
            
        except Exception as e:
            logger.error(f"Failed to create deployment package: {str(e)}")
            return None
    
    def build_all(self):
        """Build application completely"""
        logger.info("="*70)
        logger.info("STARTING APPLICATION BUILD")
        logger.info("="*70)
        
        success = True
        
        # Change to base directory
        os.chdir(self.base_dir)
        
        # Install PHP dependencies
        if self.config.COMPOSER_INSTALL and not self.install_php_dependencies():
            success = False
        
        # Install Node dependencies
        if self.config.NPM_INSTALL and not self.install_node_dependencies():
            logger.warning("Node dependencies installation failed, continuing...")
        
        # Build frontend
        if self.config.PROD_BUILD and not self.build_frontend():
            logger.warning("Frontend build failed, continuing...")
        
        # Build installer
        if self.config.PROD_BUILD and not self.build_installer():
            logger.warning("Installer build failed (optional), continuing...")
        
        # Create deployment package
        zip_path = self.create_deployment_package()
        if not zip_path:
            success = False
        
        logger.info("="*70)
        if success:
            logger.info("✓ APPLICATION BUILD COMPLETED SUCCESSFULLY")
            logger.info(f"  Package: {zip_path}")
        else:
            logger.info("✗ APPLICATION BUILD COMPLETED WITH ERRORS")
        logger.info("="*70)
        
        return success, zip_path if success else None


class AzureDeployer:
    """Deploys application to Azure App Service"""
    
    def __init__(self):
        self.config = AzureConfig
        self.deploy_config = DeploymentConfig
        
    def deploy_via_zip(self, zip_path):
        """Deploy via ZIP file upload"""
        logger.info(f"Deploying via ZIP: {zip_path}...")
        
        try:
            from azure.identity import ClientSecretCredential
            from azure.storage.blob import BlobServiceClient
            
            # Authenticate
            credential = ClientSecretCredential(
                tenant_id=self.config.TENANT_ID,
                client_id=self.config.CLIENT_ID,
                client_secret=self.config.CLIENT_SECRET
            )
            
            # Upload to storage
            storage_account_url = f"https://{self.config.STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            blob_service_client = BlobServiceClient(storage_account_url, credential=credential)
            container_client = blob_service_client.get_container_client(self.config.STORAGE_CONTAINER_NAME)
            
            blob_name = Path(zip_path).name
            with open(zip_path, 'rb') as data:
                container_client.upload_blob(blob_name, data, overwrite=True)
            
            logger.info(f"✓ ZIP uploaded to storage: {blob_name}")
            
            # Deploy to App Service
            deploy_command = [
                'az', 'webapp', 'deployment', 'source', 'config-zip',
                '--resource-group', self.config.RESOURCE_GROUP_NAME,
                '--name', self.config.APP_SERVICE_NAME,
                '--src', zip_path
            ]
            
            result = subprocess.run(deploy_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Application deployed successfully")
                return True
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to deploy: {str(e)}")
            return False
    
    def deploy_all(self, zip_path):
        """Deploy application"""
        logger.info("="*70)
        logger.info("STARTING APPLICATION DEPLOYMENT")
        logger.info("="*70)
        
        success = self.deploy_via_zip(zip_path)
        
        if success:
            # Configure app settings
            self.configure_app_settings()
        
        logger.info("="*70)
        if success:
            logger.info("✓ DEPLOYMENT COMPLETED SUCCESSFULLY")
        else:
            logger.info("✗ DEPLOYMENT COMPLETED WITH ERRORS")
        logger.info("="*70)
        
        return success
    
    def configure_app_settings(self):
        """Configure App Service settings"""
        logger.info("Configuring App Service settings...")
        
        try:
            settings = [
                ('PHP_VERSION', self.config.PHP_VERSION),
                ('APP_ENV', 'prod'),
                ('APP_DEBUG', '0'),
                ('COMPOSER_EXTENSIONS', 'true'),
            ]
            
            for setting_name, setting_value in settings:
                command = [
                    'az', 'webapp', 'config', 'appsettings', 'set',
                    '--resource-group', self.config.RESOURCE_GROUP_NAME,
                    '--name', self.config.APP_SERVICE_NAME,
                    '--settings', f'{setting_name}={setting_value}'
                ]
                
                result = subprocess.run(command, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"  ✓ {setting_name} configured")
                else:
                    logger.warning(f"  ✗ Failed to set {setting_name}")
            
            logger.info("✓ App settings configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure app settings: {str(e)}")
            return False


def main():
    """Main function"""
    try:
        # Build application
        builder = ApplicationBuilder()
        build_success, zip_path = builder.build_all()
        
        if not build_success or not zip_path:
            logger.error("Build failed. Cannot proceed with deployment.")
            return 1
        
        # Deploy application
        deployer = AzureDeployer()
        deploy_success = deployer.deploy_all(zip_path)
        
        if deploy_success:
            logger.info("\n✓ Application deployment completed successfully!")
            logger.info(f"\nAccess your application at:")
            logger.info(f"  https://{AzureConfig.APP_SERVICE_NAME}.azurewebsites.net")
            return 0
        else:
            logger.error("\n✗ Application deployment failed.")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
