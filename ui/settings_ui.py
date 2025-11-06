"""
Settings UI Module
Interactive settings menu untuk configure user preferences
"""

import os
import logging
from pathlib import Path
from typing import Optional

from core.settings_manager import get_settings_manager, SettingsManager

logger = logging.getLogger(__name__)


class SettingsUI:
    """Interactive settings interface"""
    
    def __init__(self):
        self.manager = get_settings_manager()
        self.modified = False
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {title}".center(70))
        print("=" * 70 + "\n")
    
    def get_input(self, prompt: str, default: any = None, type_cast=str) -> any:
        """Get user input with default value"""
        if default is not None:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        user_input = input(full_prompt).strip()
        
        if not user_input and default is not None:
            return default
        
        try:
            return type_cast(user_input)
        except ValueError:
            print(f"⚠ Invalid input, using default: {default}")
            return default
    
    def get_bool_input(self, prompt: str, default: bool = False) -> bool:
        """Get boolean input"""
        default_str = 'y' if default else 'n'
        response = input(f"{prompt} (y/n) [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
    
    def show_main_menu(self):
        """Display main settings menu"""
        while True:
            self.print_header("⚙️  SETTINGS MENU")
            
            print("┌─────────────────────────────────────────────┐")
            print("│  1. Image Processing Settings              │")
            print("│  2. Text Processing Settings               │")
            print("│  3. Output Settings                        │")
            print("│  4. UI Settings                            │")
            print("│  5. Performance Settings                   │")
            print("│  6. Advanced Settings                      │")
            print("│                                            │")
            print("│  7. View All Settings                      │")
            print("│  8. Reset to Defaults                      │")
            print("│  9. Import/Export Settings                 │")
            print("│  0. Save & Exit                            │")
            print("└─────────────────────────────────────────────┘\n")
            
            if self.modified:
                print("⚠ You have unsaved changes!\n")
            
            choice = input("Select option (0-9): ").strip()
            
            if choice == '0':
                if self.exit_settings():
                    break
            elif choice == '1':
                self.configure_image_settings()
            elif choice == '2':
                self.configure_text_settings()
            elif choice == '3':
                self.configure_output_settings()
            elif choice == '4':
                self.configure_ui_settings()
            elif choice == '5':
                self.configure_performance_settings()
            elif choice == '6':
                self.configure_advanced_settings()
            elif choice == '7':
                self.view_all_settings()
            elif choice == '8':
                self.reset_settings()
            elif choice == '9':
                self.import_export_menu()
            else:
                print("❌ Invalid option!")
            
            input("\nPress Enter to continue...")
    
    def configure_image_settings(self):
        """Configure image processing settings"""
        self.print_header("📸 IMAGE PROCESSING SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Layout: {s.image_default_layout}")
        print(f"  Spacing: {s.image_default_spacing}px")
        print(f"  Quality: {s.image_default_quality}%")
        print(f"  Resize Mode: {s.image_default_resize_mode}")
        print(f"  Filter: {s.image_default_filter}")
        print(f"  Watermark: {'Enabled' if s.image_add_watermark else 'Disabled'}")
        
        print("\nModify Settings:\n")
        
        # Layout
        print("Layout options: vertical, horizontal, grid")
        layout = self.get_input("Default layout", s.image_default_layout)
        if layout in ['vertical', 'horizontal', 'grid']:
            s.image_default_layout = layout
            self.modified = True
        
        # Spacing
        spacing = self.get_input("Default spacing (px)", s.image_default_spacing, int)
        if spacing >= 0:
            s.image_default_spacing = spacing
            self.modified = True
        
        # Quality
        quality = self.get_input("JPEG quality (1-100)", s.image_default_quality, int)
        if 1 <= quality <= 100:
            s.image_default_quality = quality
            self.modified = True
        else:
            print("⚠ Quality must be between 1-100")
        
        # Resize mode
        print("\nResize modes: none, fit, fill, stretch")
        resize = self.get_input("Default resize mode", s.image_default_resize_mode)
        if resize in ['none', 'fit', 'fill', 'stretch']:
            s.image_default_resize_mode = resize
            self.modified = True
        
        # Filter
        print("\nFilters: none, grayscale, sepia, blur, sharpen, edge")
        filter_name = self.get_input("Default filter", s.image_default_filter)
        if filter_name in ['none', 'grayscale', 'sepia', 'blur', 'sharpen', 'edge']:
            s.image_default_filter = filter_name
            self.modified = True
        
        # Watermark
        add_watermark = self.get_bool_input("\nAdd watermark by default?", s.image_add_watermark)
        s.image_add_watermark = add_watermark
        self.modified = True
        
        if add_watermark:
            watermark_text = self.get_input("Watermark text", s.image_watermark_text)
            s.image_watermark_text = watermark_text
            
            print("\nPositions: top-left, top-right, bottom-left, bottom-right, center")
            position = self.get_input("Watermark position", s.image_watermark_position)
            if position in ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center']:
                s.image_watermark_position = position
            
            opacity = self.get_input("Watermark opacity (0-255)", s.image_watermark_opacity, int)
            if 0 <= opacity <= 255:
                s.image_watermark_opacity = opacity
        
        print("\n✅ Image settings updated!")
    
    def configure_text_settings(self):
        """Configure text processing settings"""
        self.print_header("📝 TEXT PROCESSING SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Separator: {s.text_default_separator}")
        print(f"  Encoding: {s.text_default_encoding}")
        print(f"  Line Numbers: {'Yes' if s.text_add_line_numbers else 'No'}")
        print(f"  Timestamps: {'Yes' if s.text_add_timestamps else 'No'}")
        
        print("\nModify Settings:\n")
        
        # Separator
        print("Separator styles: simple, fancy, minimal, none")
        separator = self.get_input("Default separator", s.text_default_separator)
        if separator in ['simple', 'fancy', 'minimal', 'none']:
            s.text_default_separator = separator
            self.modified = True
        
        # Encoding
        print("\nCommon encodings: utf-8, latin-1, ascii, cp1252")
        encoding = self.get_input("Default encoding", s.text_default_encoding)
        s.text_default_encoding = encoding
        self.modified = True
        
        # Options
        s.text_add_line_numbers = self.get_bool_input("\nAdd line numbers by default?", s.text_add_line_numbers)
        s.text_add_timestamps = self.get_bool_input("Add timestamps by default?", s.text_add_timestamps)
        s.text_strip_whitespace = self.get_bool_input("Strip whitespace by default?", s.text_strip_whitespace)
        s.text_markdown_export = self.get_bool_input("Export as Markdown by default?", s.text_markdown_export)
        
        self.modified = True
        print("\n✅ Text settings updated!")
    
    def configure_output_settings(self):
        """Configure output settings"""
        self.print_header("💾 OUTPUT SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Use Timestamp: {'Yes' if s.output_use_timestamp else 'No'}")
        print(f"  Auto Overwrite: {'Yes' if s.output_auto_overwrite else 'No'}")
        print(f"  Create Backup: {'Yes' if s.output_create_backup else 'No'}")
        print(f"  Output Directory: {s.output_default_directory}")
        
        print("\nModify Settings:\n")
        
        s.output_use_timestamp = self.get_bool_input(
            "Add timestamp to filenames?", s.output_use_timestamp
        )
        
        s.output_auto_overwrite = self.get_bool_input(
            "Auto overwrite existing files?", s.output_auto_overwrite
        )
        
        s.output_create_backup = self.get_bool_input(
            "Create backup before overwriting?", s.output_create_backup
        )
        
        output_dir = self.get_input("Output directory", s.output_default_directory)
        s.output_default_directory = output_dir
        
        self.modified = True
        print("\n✅ Output settings updated!")
    
    def configure_ui_settings(self):
        """Configure UI settings"""
        self.print_header("🎨 USER INTERFACE SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Show File Size: {'Yes' if s.ui_show_file_size else 'No'}")
        print(f"  Show Statistics: {'Yes' if s.ui_show_statistics else 'No'}")
        print(f"  Confirm Before Process: {'Yes' if s.ui_confirm_before_process else 'No'}")
        print(f"  Clear Screen: {'Yes' if s.ui_clear_screen else 'No'}")
        print(f"  Color Output: {'Yes' if s.ui_color_output else 'No'}")
        
        print("\nModify Settings:\n")
        
        s.ui_show_file_size = self.get_bool_input(
            "Show file sizes in file list?", s.ui_show_file_size
        )
        
        s.ui_show_statistics = self.get_bool_input(
            "Show statistics after processing?", s.ui_show_statistics
        )
        
        s.ui_confirm_before_process = self.get_bool_input(
            "Require confirmation before processing?", s.ui_confirm_before_process
        )
        
        s.ui_clear_screen = self.get_bool_input(
            "Clear screen between operations?", s.ui_clear_screen
        )
        
        s.ui_color_output = self.get_bool_input(
            "Use colored output?", s.ui_color_output
        )
        
        self.modified = True
        print("\n✅ UI settings updated!")
    
    def configure_performance_settings(self):
        """Configure performance settings"""
        self.print_header("⚡ PERFORMANCE SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Max Workers: {s.performance_max_workers}")
        print(f"  Chunk Size: {s.performance_chunk_size} bytes")
        print(f"  Enable Cache: {'Yes' if s.performance_enable_cache else 'No'}")
        print(f"  Cache Size: {s.performance_cache_size_mb} MB")
        
        print("\nModify Settings:\n")
        print("⚠ Warning: Incorrect settings may affect performance!")
        
        workers = self.get_input("Max workers (1-16)", s.performance_max_workers, int)
        if 1 <= workers <= 16:
            s.performance_max_workers = workers
            self.modified = True
        
        chunk_size = self.get_input("Chunk size (bytes)", s.performance_chunk_size, int)
        if chunk_size > 0:
            s.performance_chunk_size = chunk_size
            self.modified = True
        
        s.performance_enable_cache = self.get_bool_input(
            "Enable caching?", s.performance_enable_cache
        )
        
        cache_size = self.get_input("Cache size (MB)", s.performance_cache_size_mb, int)
        if cache_size >= 0:
            s.performance_cache_size_mb = cache_size
            self.modified = True
        
        print("\n✅ Performance settings updated!")
    
    def configure_advanced_settings(self):
        """Configure advanced settings"""
        self.print_header("🔧 ADVANCED SETTINGS")
        
        s = self.manager.settings
        
        print("Current Settings:")
        print(f"  Debug Mode: {'Yes' if s.advanced_debug_mode else 'No'}")
        print(f"  Log Level: {s.advanced_log_level}")
        print(f"  Backup Count: {s.advanced_backup_count}")
        print(f"  Auto Cleanup: {'Yes' if s.advanced_auto_cleanup else 'No'}")
        
        print("\nModify Settings:\n")
        print("⚠ Warning: Advanced settings for experienced users!")
        
        s.advanced_debug_mode = self.get_bool_input(
            "Enable debug mode?", s.advanced_debug_mode
        )
        
        print("\nLog levels: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        log_level = self.get_input("Log level", s.advanced_log_level).upper()
        if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            s.advanced_log_level = log_level
            self.modified = True
        
        backup_count = self.get_input("Backup files to keep", s.advanced_backup_count, int)
        if backup_count >= 0:
            s.advanced_backup_count = backup_count
            self.modified = True
        
        s.advanced_auto_cleanup = self.get_bool_input(
            "Auto cleanup temp files?", s.advanced_auto_cleanup
        )
        
        self.modified = True
        print("\n✅ Advanced settings updated!")
    
    def view_all_settings(self):
        """Display all current settings"""
        self.clear_screen()
        print(self.manager.get_settings_summary())
        
        # Validate settings
        issues = self.manager.validate_settings()
        if issues:
            print("\n⚠ VALIDATION WARNINGS:")
            for category, problems in issues.items():
                print(f"\n  {category.upper()}:")
                for problem in problems:
                    print(f"    - {problem}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        self.print_header("🔄 RESET SETTINGS")
        
        print("⚠ WARNING: This will reset ALL settings to default values!")
        confirm = input("\nAre you sure? Type 'RESET' to confirm: ").strip()
        
        if confirm == 'RESET':
            # Backup current settings
            backup_file = self.manager.backup_settings()
            if backup_file:
                print(f"✅ Current settings backed up to: {backup_file}")
            
            # Reset
            self.manager.reset_to_defaults()
            self.modified = True
            print("\n✅ Settings reset to defaults!")
        else:
            print("\n❌ Reset cancelled.")
    
    def import_export_menu(self):
        """Import/Export settings menu"""
        self.print_header("📦 IMPORT/EXPORT SETTINGS")
        
        print("┌─────────────────────────────────────────┐")
        print("│  1. Export Settings                    │")
        print("│  2. Import Settings                    │")
        print("│  3. Backup Settings                    │")
        print("│  4. Restore from Backup                │")
        print("│  0. Back                               │")
        print("└─────────────────────────────────────────┘\n")
        
        choice = input("Select option (0-4): ").strip()
        
        if choice == '1':
            self.export_settings()
        elif choice == '2':
            self.import_settings()
        elif choice == '3':
            self.backup_settings()
        elif choice == '4':
            self.restore_settings()
    
    def export_settings(self):
        """Export settings to file"""
        print("\n📤 EXPORT SETTINGS")
        
        export_path = input("Export to (path/filename.json): ").strip()
        if not export_path:
            print("❌ Export cancelled.")
            return
        
        if not export_path.endswith('.json'):
            export_path += '.json'
        
        if self.manager.export_settings(export_path):
            print(f"✅ Settings exported to: {export_path}")
        else:
            print("❌ Export failed!")
    
    def import_settings(self):
        """Import settings from file"""
        print("\n📥 IMPORT SETTINGS")
        
        import_path = input("Import from (path/filename.json): ").strip().strip('"')
        if not import_path:
            print("❌ Import cancelled.")
            return
        
        if not Path(import_path).exists():
            print("❌ File not found!")
            return
        
        confirm = input("⚠ This will overwrite current settings. Continue? (y/n): ").lower()
        if confirm == 'y':
            if self.manager.import_settings(import_path):
                print("✅ Settings imported successfully!")
                self.modified = False
            else:
                print("❌ Import failed!")
    
    def backup_settings(self):
        """Create backup of current settings"""
        print("\n💾 BACKUP SETTINGS")
        
        backup_file = self.manager.backup_settings()
        if backup_file:
            print(f"✅ Backup created: {backup_file}")
        else:
            print("❌ Backup failed!")
    
    def restore_settings(self):
        """Restore settings from backup"""
        print("\n♻️  RESTORE SETTINGS")
        
        backup_path = input("Backup file path: ").strip().strip('"')
        if not backup_path:
            print("❌ Restore cancelled.")
            return
        
        if not Path(backup_path).exists():
            print("❌ Backup file not found!")
            return
        
        if self.manager.restore_settings(backup_path):
            print("✅ Settings restored successfully!")
            self.modified = False
        else:
            print("❌ Restore failed!")
    
    def exit_settings(self) -> bool:
        """Handle exit with save prompt"""
        if self.modified:
            self.print_header("💾 SAVE CHANGES?")
            
            print("You have unsaved changes.")
            print("\n1. Save and Exit")
            print("2. Exit without Saving")
            print("3. Cancel")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                if self.manager.save_settings():
                    self.manager.apply_to_config()
                    print("\n✅ Settings saved and applied!")
                    return True
                else:
                    print("\n❌ Failed to save settings!")
                    return False
            elif choice == '2':
                confirm = input("⚠ Discard all changes? (y/n): ").lower()
                if confirm == 'y':
                    print("\n⚠ Changes discarded.")
                    return True
                return False
            else:
                return False
        else:
            return True
    
    def run(self):
        """Run settings UI"""
        try:
            self.show_main_menu()
        except KeyboardInterrupt:
            print("\n\n⚠ Settings menu interrupted.")
            if self.modified:
                save = input("Save changes before exit? (y/n): ").lower()
                if save == 'y':
                    self.manager.save_settings()
                    self.manager.apply_to_config()


# Convenience function
def show_settings():
    """Show settings UI"""
    ui = SettingsUI()
    ui.run()