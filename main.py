"""
File Merger Pro - Main Application
Entry point with robust error handling and logging setup.
"""

import sys
import logging
from pathlib import Path

# Setup logging
from config import LogConfig, APP_NAME, APP_VERSION
from core.settings_manager import get_settings_manager

def setup_logging():
    """Configure logging system."""
    logging.basicConfig(
        level=getattr(logging, LogConfig.LOG_LEVEL, logging.INFO),
        format=LogConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(LogConfig.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence noisy libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    return logger

def main():
    logger = setup_logging()
    
    # Apply user settings at startup
    try:
        get_settings_manager().apply_to_config()
        logger.info("Settings loaded.")
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")

    try:
        # Mode Selection
        mode = 'cli'
        if '--gui' in sys.argv:
            mode = 'gui'
        elif '--cli' in sys.argv:
            mode = 'cli'
        else:
            # Default behavior: Ask if interactive, otherwise CLI
            if sys.stdin.isatty():
                print(f"Welcome to {APP_NAME}")
                print("[1] GUI (Graphical Interface)")
                print("[2] CLI (Command Line)")
                choice = input("Select mode [1]: ").strip()
                if choice in ('', '1', 'gui', 'g'):
                    mode = 'gui'
            else:
                mode = 'cli'

        # Launch
        if mode == 'gui':
            try:
                # Lazy import to avoid Tkinter overhead if not needed
                from ui.gui import GUIApp
                app = GUIApp()
                app.run()
            except ImportError as e:
                logger.error(f"GUI dependencies missing: {e}")
                print("❌ GUI failed to start. Falling back to CLI.")
                from ui.cli import CLI
                CLI().run()
            except Exception as e:
                logger.error(f"GUI Crash: {e}", exc_info=True)
                print(f"❌ GUI Crash: {e}")
        else:
            from ui.cli import CLI
            CLI().run()

    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal Error: {e}", exc_info=True)
        print(f"Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()