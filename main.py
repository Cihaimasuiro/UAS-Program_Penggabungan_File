"""
File Merger Pro - Main Application
Entry point untuk aplikasi dengan logging dan error handling
"""

import sys
import logging
from pathlib import Path

# Setup logging
from config import LogConfig, APP_NAME, APP_VERSION
from core.settings_manager import get_settings_manager

def setup_logging():
    """Configure logging system"""
    logging.basicConfig(
        level=getattr(logging, LogConfig.LOG_LEVEL),
        format=LogConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(LogConfig.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set library loggers to WARNING
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    return logger

def apply_user_settings(logger):
    """Load and apply settings from settings.json at startup"""
    try:
        manager = get_settings_manager()
        manager.apply_to_config()
        logger.info("User settings loaded and applied to config.")
    except Exception as e:
        logger.error(f"Failed to apply user settings: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required = ['PIL', 'pathlib']
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install Pillow")
        sys.exit(1)

def main():
    """Main application entry point"""
    # Setup
    logger = setup_logging()
    apply_user_settings(logger)
    check_dependencies()
    
    try:
        # Import CLI
        from ui.cli import CLI
        
        # Run application
        cli = CLI()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error occurred: {str(e)}")
        print("Check logs for details: logs/app.log")
        sys.exit(1)

if __name__ == "__main__":
    main()