"""
Settings Manager Module
Handle user preferences and application settings with persistence
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

from config import BASE_DIR, ImageConfig, TextConfig, OutputConfig

logger = logging.getLogger(__name__)


@dataclass
class UserSettings:
    """User preferences data class"""
    
    # Image Settings
    image_default_layout: str = 'vertical'
    image_default_spacing: int = 10
    image_default_quality: int = 95
    image_default_resize_mode: str = 'none'
    image_default_filter: str = 'none'
    image_add_watermark: bool = False
    image_watermark_text: str = '© 2024'
    image_watermark_position: str = 'bottom-right'
    image_watermark_opacity: int = 128
    
    # Text Settings
    text_default_separator: str = 'simple'
    text_default_encoding: str = 'utf-8'
    text_add_line_numbers: bool = False
    text_add_timestamps: bool = False
    text_strip_whitespace: bool = False
    text_markdown_export: bool = False
    
    # Output Settings
    output_use_timestamp: bool = True
    output_auto_overwrite: bool = False
    output_create_backup: bool = True
    output_default_directory: str = 'output'
    
    # UI Settings
    ui_show_file_size: bool = True
    ui_show_statistics: bool = True
    ui_confirm_before_process: bool = True
    ui_clear_screen: bool = False
    ui_color_output: bool = True
    
    # Performance Settings
    performance_max_workers: int = 4
    performance_chunk_size: int = 8192
    performance_enable_cache: bool = True
    performance_cache_size_mb: int = 128
    
    # Advanced Settings
    advanced_debug_mode: bool = False
    advanced_log_level: str = 'INFO'
    advanced_backup_count: int = 5
    advanced_auto_cleanup: bool = True
    
    # Metadata
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = '2.0.0'


class SettingsManager:
    """Manage application settings with persistence"""
    
    SETTINGS_FILE = BASE_DIR / 'settings.json'
    
    def __init__(self):
        self.settings = self.load_settings()
        self._original_settings = None  # For reset functionality
    
    def load_settings(self) -> UserSettings:
        """Load settings from file or create default"""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info("Settings loaded from file")
                return UserSettings(**data)
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                logger.info("Using default settings")
        
        # Return default settings
        return UserSettings()
    
    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            self.settings.last_modified = datetime.now().isoformat()
            
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2)
            
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.settings = UserSettings()
        logger.info("Settings reset to defaults")
    
    def backup_settings(self) -> Optional[str]:
        """Create backup of current settings"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BASE_DIR / f'settings_backup_{timestamp}.json'
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2)
            
            logger.info(f"Settings backed up to: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Failed to backup settings: {e}")
            return None
    
    def restore_settings(self, backup_file: str) -> bool:
        """Restore settings from backup file"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.settings = UserSettings(**data)
            logger.info(f"Settings restored from: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
            return False
    
    def export_settings(self, export_path: str) -> bool:
        """Export settings to specific path"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2)
            
            logger.info(f"Settings exported to: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """Import settings from file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.settings = UserSettings(**data)
            logger.info(f"Settings imported from: {import_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get specific setting value"""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set specific setting value"""
        try:
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
                logger.debug(f"Setting updated: {key} = {value}")
                return True
            else:
                logger.warning(f"Unknown setting key: {key}")
                return False
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def apply_to_config(self):
        """Apply user settings to config modules"""
        # Apply image settings
        ImageConfig.DEFAULT_LAYOUT = self.settings.image_default_layout
        ImageConfig.DEFAULT_SPACING = self.settings.image_default_spacing
        ImageConfig.DEFAULT_QUALITY = self.settings.image_default_quality
        
        # Apply text settings
        TextConfig.DEFAULT_ENCODING = self.settings.text_default_encoding
        TextConfig.DEFAULT_SEPARATOR = self.settings.text_default_separator
        TextConfig.ADD_LINE_NUMBERS = self.settings.text_add_line_numbers
        TextConfig.ADD_TIMESTAMPS = self.settings.text_add_timestamps
        TextConfig.STRIP_WHITESPACE = self.settings.text_strip_whitespace
        
        # Apply output settings
        OutputConfig.USE_TIMESTAMP = self.settings.output_use_timestamp
        OutputConfig.AUTO_OVERWRITE = self.settings.output_auto_overwrite
        OutputConfig.CREATE_BACKUP = self.settings.output_create_backup
        
        logger.info("User settings applied to configuration")
    
    def get_all_settings(self) -> Dict:
        """Get all settings as dictionary"""
        return asdict(self.settings)
    
    def validate_settings(self) -> Dict[str, list]:
        """Validate current settings and return issues"""
        issues = {}
        
        # Validate image settings
        if self.settings.image_default_quality < 1 or self.settings.image_default_quality > 100:
            issues.setdefault('image', []).append('Quality must be between 1-100')
        
        if self.settings.image_default_spacing < 0:
            issues.setdefault('image', []).append('Spacing cannot be negative')
        
        if self.settings.image_watermark_opacity < 0 or self.settings.image_watermark_opacity > 255:
            issues.setdefault('image', []).append('Watermark opacity must be between 0-255')
        
        # Validate performance settings
        if self.settings.performance_max_workers < 1:
            issues.setdefault('performance', []).append('Max workers must be at least 1')
        
        if self.settings.performance_cache_size_mb < 0:
            issues.setdefault('performance', []).append('Cache size cannot be negative')
        
        # Validate advanced settings
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.settings.advanced_log_level not in valid_log_levels:
            issues.setdefault('advanced', []).append(f'Log level must be one of: {valid_log_levels}')
        
        return issues
    
    def get_settings_summary(self) -> str:
        """Get human-readable summary of current settings"""
        s = self.settings
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    CURRENT SETTINGS                          ║
╚══════════════════════════════════════════════════════════════╝

📸 IMAGE SETTINGS
  Layout:              {s.image_default_layout}
  Spacing:             {s.image_default_spacing}px
  Quality:             {s.image_default_quality}%
  Resize Mode:         {s.image_default_resize_mode}
  Default Filter:      {s.image_default_filter}
  Watermark:           {'Enabled' if s.image_add_watermark else 'Disabled'}
  Watermark Text:      {s.image_watermark_text}
  Watermark Position:  {s.image_watermark_position}
  Watermark Opacity:   {s.image_watermark_opacity}/255

📝 TEXT SETTINGS
  Separator Style:     {s.text_default_separator}
  Encoding:            {s.text_default_encoding}
  Line Numbers:        {'Yes' if s.text_add_line_numbers else 'No'}
  Timestamps:          {'Yes' if s.text_add_timestamps else 'No'}
  Strip Whitespace:    {'Yes' if s.text_strip_whitespace else 'No'}
  Markdown Export:     {'Yes' if s.text_markdown_export else 'No'}

💾 OUTPUT SETTINGS
  Use Timestamp:       {'Yes' if s.output_use_timestamp else 'No'}
  Auto Overwrite:      {'Yes' if s.output_auto_overwrite else 'No'}
  Create Backup:       {'Yes' if s.output_create_backup else 'No'}
  Output Directory:    {s.output_default_directory}

🎨 UI SETTINGS
  Show File Size:      {'Yes' if s.ui_show_file_size else 'No'}
  Show Statistics:     {'Yes' if s.ui_show_statistics else 'No'}
  Confirm Processing:  {'Yes' if s.ui_confirm_before_process else 'No'}
  Clear Screen:        {'Yes' if s.ui_clear_screen else 'No'}
  Color Output:        {'Yes' if s.ui_color_output else 'No'}

⚡ PERFORMANCE SETTINGS
  Max Workers:         {s.performance_max_workers}
  Chunk Size:          {s.performance_chunk_size} bytes
  Enable Cache:        {'Yes' if s.performance_enable_cache else 'No'}
  Cache Size:          {s.performance_cache_size_mb} MB

🔧 ADVANCED SETTINGS
  Debug Mode:          {'Yes' if s.advanced_debug_mode else 'No'}
  Log Level:           {s.advanced_log_level}
  Backup Count:        {s.advanced_backup_count}
  Auto Cleanup:        {'Yes' if s.advanced_auto_cleanup else 'No'}

📊 METADATA
  Last Modified:       {s.last_modified}
  Version:             {s.version}
        """
        
        return summary


# Singleton instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get singleton settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager