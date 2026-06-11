"""
Database Setup and Migration for OrangeHRM
"""
import os
import sys
import subprocess
import logging
import time
from pathlib import Path
from config import AzureConfig, DatabaseConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database setup and migrations"""
    
    def __init__(self):
        self.config = AzureConfig
        self.db_config = DatabaseConfig
        self.db_host = self.config.DB_SERVER_NAME + '.mysql.database.azure.com'
        self.db_user = self.config.DB_ADMIN_USER + '@' + self.config.DB_SERVER_NAME
        
    def wait_for_database(self, max_retries=30, retry_delay=10):
        """Wait for database to be ready"""
        logger.info("Waiting for database to be ready...")
        
        for attempt in range(max_retries):
            try:
                import mysql.connector
                connection = mysql.connector.connect(
                    host=self.db_host,
                    user=self.db_user,
                    password=self.config.DB_ADMIN_PASSWORD,
                    port=3306
                )
                connection.close()
                logger.info("✓ Database is ready")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"Database not ready, retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Database failed to be ready after {max_retries} attempts")
                    return False
        
        return False
    
    def create_database(self):
        """Create OrangeHRM database"""
        logger.info(f"Creating database: {self.config.DB_NAME}...")
        
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.config.DB_ADMIN_PASSWORD,
                port=3306
            )
            
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            logger.info(f"✓ Database created: {self.config.DB_NAME}")
            
            cursor.close()
            connection.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {str(e)}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        logger.info("Running database migrations...")
        
        try:
            # Navigate to application directory
            src_dir = Path(self.config.APP_REPO_PATH) / 'src'
            
            if not src_dir.exists():
                logger.error(f"Source directory not found: {src_dir}")
                return False
            
            os.chdir(src_dir)
            
            # Run Doctrine migrations
            migration_command = [
                'php', 'bin/console', 'doctrine:migrations:migrate',
                '--env=prod', '--no-interaction'
            ]
            
            result = subprocess.run(migration_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Database migrations completed")
                return True
            else:
                logger.error(f"Migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to run migrations: {str(e)}")
            return False
    
    def seed_initial_data(self):
        """Seed initial data for OrangeHRM"""
        logger.info("Seeding initial data...")
        
        try:
            src_dir = Path(self.config.APP_REPO_PATH) / 'src'
            os.chdir(src_dir)
            
            # Run seeding command if available
            seed_command = [
                'php', 'bin/console', 'orangehrm:seed:load',
                '--env=prod'
            ]
            
            result = subprocess.run(seed_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Initial data seeded")
                return True
            else:
                # Seed command might not exist - this is optional
                logger.warning("Seeding command not available or failed (optional)")
                return True
                
        except Exception as e:
            logger.warning(f"Seeding failed (optional): {str(e)}")
            return True
    
    def setup_database_connection(self):
        """Configure database connection in application"""
        logger.info("Configuring database connection...")
        
        try:
            # Update environment variables or config files
            config_file = Path(self.config.APP_REPO_PATH) / 'src' / '.env.local'
            
            env_content = f"""DATABASE_URL=mysql://{self.config.DB_ADMIN_USER}:{self.config.DB_ADMIN_PASSWORD}@{self.db_host}:3306/{self.config.DB_NAME}?serverVersion=8.0
APP_ENV=prod
APP_DEBUG=0
APP_SECRET=your-secret-key-here
"""
            
            with open(config_file, 'w') as f:
                f.write(env_content)
            
            logger.info("✓ Database connection configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure database connection: {str(e)}")
            return False
    
    def setup_all(self):
        """Setup database completely"""
        logger.info("="*70)
        logger.info("STARTING DATABASE SETUP")
        logger.info("="*70)
        
        success = True
        
        # Wait for database
        if not self.wait_for_database():
            logger.error("Cannot proceed - database is not responding")
            return False
        
        # Create database
        if not self.create_database():
            success = False
        
        # Setup connection config
        if not self.setup_database_connection():
            success = False
        
        # Run migrations
        if not self.run_migrations():
            success = False
        
        # Seed initial data
        if not self.seed_initial_data():
            success = False
        
        logger.info("="*70)
        if success:
            logger.info("✓ DATABASE SETUP COMPLETED SUCCESSFULLY")
        else:
            logger.info("✗ DATABASE SETUP COMPLETED WITH ERRORS")
        logger.info("="*70)
        
        return success


def main():
    """Main function"""
    try:
        manager = DatabaseManager()
        success = manager.setup_all()
        
        if success:
            logger.info("\n✓ Database setup completed successfully!")
            logger.info("Next step: Run 'python build_and_deploy.py'")
        else:
            logger.error("\n✗ Database setup failed. Check logs above.")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
