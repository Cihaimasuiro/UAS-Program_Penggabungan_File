"""
Settings Manager Module
Handles persistence of user preferences with robust error handling.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass, asdict, field
from datetime import datetime

from config import BASE_DIR, ImageConfig, TextConfig, OutputConfig

logger = logging.getLogger(__name__)

@dataclass
class UserSettings:
    """User preferences data class (Source of Truth)."""
    
    # Image
    image_default_layout: str = 'vertical'
    image_default_spacing: int = 10
    image_default_quality: int = 95
    image_default_resize_mode: str = 'none'
    image_default_filter: str = 'none'
    image_add_watermark: bool = False
    image_watermark_text: str = 'Copyright 2025'
    
    # Text
    text_default_separator: str = 'simple'
    text_default_encoding: str = 'utf-8'
    text_add_line_numbers: bool = False
    text_markdown_export: bool = False
    
    # Output
    output_use_timestamp: bool = True
    output_create_backup: bool = True
    output_default_directory: str = 'output'
    
    # System
    performance_max_workers: int = 4
    advanced_debug_mode: bool = False
    
    # Meta
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = '2.0.0'

class SettingsManager:
    SETTINGS_FILE = BASE_DIR / 'settings.json'
    
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self) -> UserSettings:
        """Load settings from JSON or return defaults on failure."""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Filter out keys that no longer exist in the dataclass (migration safety)
                valid_keys = UserSettings.__annotations__.keys()
                filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                return UserSettings(**filtered_data)
            except Exception as e:
                logger.error(f"Failed to load settings: {e}. Reverting to defaults.")
        
        return UserSettings()
    
    def save_settings(self) -> bool:
        """
        Save current settings to disk.
        Returns True if successful, False otherwise.
        """
        try:
            self.settings.last_modified = datetime.now().isoformat()
            
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2)
            
            logger.info("Settings saved.")
            return True
        except Exception as e:
            logger.error(f"CRITICAL: Failed to save settings: {e}")
            return False
    
    def reset_to_defaults(self):
        """Hard reset to factory defaults."""
        self.settings = UserSettings()
        self.save_settings()
        logger.info("Settings reset to factory defaults.")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any):
        """Update a setting dynamically."""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
        else:
            logger.warning(f"Attempted to set unknown setting: {key}")

    def apply_to_config(self):
        """
        Propagate user settings to global Config classes.
        This allows the rest of the app to read Config.* instead of passing settings objects everywhere.
        """
        # Image
        ImageConfig.DEFAULT_LAYOUT = self.settings.image_default_layout
        ImageConfig.DEFAULT_SPACING = self.settings.image_default_spacing
        ImageConfig.DEFAULT_QUALITY = self.settings.image_default_quality
        
        # Text
        TextConfig.DEFAULT_SEPARATOR = self.settings.text_default_separator
        TextConfig.DEFAULT_ENCODING = self.settings.text_default_encoding
        
        # Output
        OutputConfig.USE_TIMESTAMP = self.settings.output_use_timestamp
        OutputConfig.CREATE_BACKUP = self.settings.output_create_backup
        
        logger.info("User settings applied to runtime configuration.")

# Singleton pattern
_manager_instance = None

def get_settings_manager() -> SettingsManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SettingsManager()
    return _manager_instance