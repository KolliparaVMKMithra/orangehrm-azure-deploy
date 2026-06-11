"""
Main Deployment Orchestrator
Coordinates all deployment steps
"""
import sys
import logging
from pathlib import Path
from config import AzureConfig, DeploymentConfig
from pre_deployment_checks import PreDeploymentValidator, create_env_template
from azure_setup import AzureResourceManager
from database_setup import DatabaseManager
from build_and_deploy import ApplicationBuilder, AzureDeployer
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(DeploymentConfig.LOGS_DIR) / 'deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates the entire deployment process"""
    
    def __init__(self):
        self.steps_completed = []
        self.errors = []
    
    def step_1_validate_environment(self):
        """Step 1: Validate environment and prerequisites"""
        logger.info("\n" + "="*70)
        logger.info("STEP 1: VALIDATE ENVIRONMENT")
        logger.info("="*70)
        
        try:
            # Create env template if needed
            if not Path('.env').exists():
                logger.warning(".env file not found. Creating from template...")
                create_env_template()
                logger.error("\n⚠ IMPORTANT: Edit .env.example with your Azure credentials and rename to .env")
                return False
            
            validator = PreDeploymentValidator()
            if not validator.check_all():
                self.errors.append("Environment validation failed")
                return False
            
            self.steps_completed.append("1. Environment Validation")
            return True
            
        except Exception as e:
            logger.error(f"Step 1 failed: {str(e)}")
            self.errors.append(f"Step 1: {str(e)}")
            return False
    
    def step_2_setup_azure_resources(self):
        """Step 2: Create Azure resources"""
        logger.info("\n" + "="*70)
        logger.info("STEP 2: SETUP AZURE RESOURCES")
        logger.info("="*70)
        
        try:
            AzureConfig.validate()
            manager = AzureResourceManager()
            
            if not manager.setup_all_resources():
                self.errors.append("Azure resource setup failed")
                return False
            
            # Wait for resources to stabilize
            logger.info("Waiting for resources to stabilize...")
            time.sleep(30)
            
            self.steps_completed.append("2. Azure Resources Setup")
            return True
            
        except Exception as e:
            logger.error(f"Step 2 failed: {str(e)}")
            self.errors.append(f"Step 2: {str(e)}")
            return False
    
    def step_3_setup_database(self):
        """Step 3: Setup database"""
        logger.info("\n" + "="*70)
        logger.info("STEP 3: SETUP DATABASE")
        logger.info("="*70)
        
        try:
            db_manager = DatabaseManager()
            
            if not db_manager.setup_all():
                self.errors.append("Database setup failed")
                logger.warning("Database setup encountered issues. Check logs.")
                # Don't fail completely - might need manual intervention
            
            self.steps_completed.append("3. Database Setup")
            return True
            
        except Exception as e:
            logger.error(f"Step 3 failed: {str(e)}")
            self.errors.append(f"Step 3: {str(e)}")
            return False
    
    def step_4_build_application(self):
        """Step 4: Build application"""
        logger.info("\n" + "="*70)
        logger.info("STEP 4: BUILD APPLICATION")
        logger.info("="*70)
        
        try:
            builder = ApplicationBuilder()
            success, zip_path = builder.build_all()
            
            if not success or not zip_path:
                self.errors.append("Application build failed")
                return False
            
            self.zip_path = zip_path
            self.steps_completed.append("4. Application Build")
            return True
            
        except Exception as e:
            logger.error(f"Step 4 failed: {str(e)}")
            self.errors.append(f"Step 4: {str(e)}")
            return False
    
    def step_5_deploy_application(self):
        """Step 5: Deploy application"""
        logger.info("\n" + "="*70)
        logger.info("STEP 5: DEPLOY APPLICATION")
        logger.info("="*70)
        
        try:
            if not hasattr(self, 'zip_path'):
                self.errors.append("No deployment package found")
                return False
            
            deployer = AzureDeployer()
            
            if not deployer.deploy_all(self.zip_path):
                self.errors.append("Application deployment failed")
                return False
            
            self.steps_completed.append("5. Application Deployment")
            return True
            
        except Exception as e:
            logger.error(f"Step 5 failed: {str(e)}")
            self.errors.append(f"Step 5: {str(e)}")
            return False
    
    def run_full_deployment(self):
        """Run complete deployment process"""
        logger.info("\n" + "="*80)
        logger.info("ORANGEHRM AZURE DEPLOYMENT - STARTING")
        logger.info("="*80)
        
        # Step 1: Validate
        if not self.step_1_validate_environment():
            logger.error("Environment validation failed. Cannot proceed.")
            return False
        
        # Step 2: Setup Azure Resources
        if not self.step_2_setup_azure_resources():
            logger.error("Azure resource setup failed.")
            return False
        
        # Step 3: Setup Database
        if not self.step_3_setup_database():
            logger.warning("Database setup encountered issues.")
            # Don't fail - database setup might require manual steps
        
        # Step 4: Build Application
        if not self.step_4_build_application():
            logger.error("Application build failed.")
            return False
        
        # Step 5: Deploy Application
        if not self.step_5_deploy_application():
            logger.error("Application deployment failed.")
            return False
        
        return True
    
    def print_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "="*80)
        logger.info("DEPLOYMENT SUMMARY")
        logger.info("="*80)
        
        logger.info("\n✓ COMPLETED STEPS:")
        for step in self.steps_completed:
            logger.info(f"  • {step}")
        
        if self.errors:
            logger.info("\n✗ ERRORS ENCOUNTERED:")
            for error in self.errors:
                logger.info(f"  • {error}")
        
        logger.info("\n" + "="*80)
        
        if not self.errors:
            logger.info("✓ DEPLOYMENT COMPLETED SUCCESSFULLY!")
            logger.info(f"\n📍 Application URL:")
            logger.info(f"   https://{AzureConfig.APP_SERVICE_NAME}.azurewebsites.net")
            logger.info(f"\n📊 Resources Created:")
            logger.info(f"   • Resource Group: {AzureConfig.RESOURCE_GROUP_NAME}")
            logger.info(f"   • App Service: {AzureConfig.APP_SERVICE_NAME}")
            logger.info(f"   • Database Server: {AzureConfig.DB_SERVER_NAME}.mysql.database.azure.com")
            logger.info(f"   • Storage Account: {AzureConfig.STORAGE_ACCOUNT_NAME}")
            logger.info("\n📝 Log file: logs/deployment.log")
        else:
            logger.error("✗ DEPLOYMENT FAILED")
            logger.error("\nRefer to logs/deployment.log for details")
        
        logger.info("="*80 + "\n")


def main():
    """Main entry point"""
    try:
        # Create necessary directories
        DeploymentConfig.create_directories()
        
        # Run orchestration
        orchestrator = DeploymentOrchestrator()
        
        success = orchestrator.run_full_deployment()
        orchestrator.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.error("\nDeployment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
