"""
Settings Examples - How to use Settings Manager programmatically
"""

import sys
sys.path.append('..')

from core.settings_manager import get_settings_manager, UserSettings


def example_1_load_and_display():
    """Example 1: Load and display current settings"""
    print("\n" + "="*60)
    print("Example 1: Load and Display Settings")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Display all settings
    print(manager.get_settings_summary())
    
    # Get specific setting
    layout = manager.get_setting('image_default_layout')
    print(f"\nCurrent image layout: {layout}")


def example_2_modify_settings():
    """Example 2: Modify settings programmatically"""
    print("\n" + "="*60)
    print("Example 2: Modify Settings")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Modify image settings
    manager.set_setting('image_default_quality', 100)
    manager.set_setting('image_default_spacing', 20)
    manager.set_setting('image_add_watermark', True)
    manager.set_setting('image_watermark_text', '© My Portfolio 2024')
    
    print("✅ Image settings modified:")
    print(f"  Quality: {manager.settings.image_default_quality}")
    print(f"  Spacing: {manager.settings.image_default_spacing}")
    print(f"  Watermark: {manager.settings.image_watermark_text}")
    
    # Save changes
    if manager.save_settings():
        print("\n✅ Settings saved successfully!")


def example_3_apply_to_config():
    """Example 3: Apply user settings to config"""
    print("\n" + "="*60)
    print("Example 3: Apply Settings to Config")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Modify some settings
    manager.set_setting('image_default_layout', 'grid')
    manager.set_setting('text_default_separator', 'fancy')
    
    # Apply to config modules
    manager.apply_to_config()
    
    print("✅ Settings applied to configuration modules")
    
    # Verify
    from config import ImageConfig, TextConfig
    print(f"\nImageConfig.DEFAULT_LAYOUT: {ImageConfig.DEFAULT_LAYOUT}")
    print(f"TextConfig.DEFAULT_SEPARATOR: {TextConfig.DEFAULT_SEPARATOR}")


def example_4_validate_settings():
    """Example 4: Validate settings"""
    print("\n" + "="*60)
    print("Example 4: Validate Settings")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Set some invalid values for testing
    manager.set_setting('image_default_quality', 150)  # Invalid (>100)
    manager.set_setting('image_default_spacing', -10)  # Invalid (negative)
    
    # Validate
    issues = manager.validate_settings()
    
    if issues:
        print("⚠ Validation issues found:")
        for category, problems in issues.items():
            print(f"\n  {category.upper()}:")
            for problem in problems:
                print(f"    - {problem}")
    else:
        print("✅ All settings are valid!")
    
    # Fix invalid settings
    manager.set_setting('image_default_quality', 95)
    manager.set_setting('image_default_spacing', 10)
    
    print("\n✅ Settings corrected")


def example_5_backup_restore():
    """Example 5: Backup and restore settings"""
    print("\n" + "="*60)
    print("Example 5: Backup and Restore")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Create backup
    backup_file = manager.backup_settings()
    print(f"✅ Backup created: {backup_file}")
    
    # Modify settings
    original_quality = manager.settings.image_default_quality
    manager.set_setting('image_default_quality', 50)
    print(f"\n📝 Quality changed from {original_quality} to 50")
    
    # Restore from backup
    if backup_file:
        manager.restore_settings(backup_file)
        print(f"✅ Settings restored from backup")
        print(f"📝 Quality restored to: {manager.settings.image_default_quality}")


def example_6_export_import():
    """Example 6: Export and import settings"""
    print("\n" + "="*60)
    print("Example 6: Export and Import")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Export settings
    export_path = 'my_settings_preset.json'
    if manager.export_settings(export_path):
        print(f"✅ Settings exported to: {export_path}")
    
    # Modify some settings
    manager.set_setting('image_default_quality', 80)
    print(f"\n📝 Quality changed to 80")
    
    # Import settings back
    if manager.import_settings(export_path):
        print(f"✅ Settings imported from: {export_path}")
        print(f"📝 Quality restored to: {manager.settings.image_default_quality}")


def example_7_reset_defaults():
    """Example 7: Reset to default settings"""
    print("\n" + "="*60)
    print("Example 7: Reset to Defaults")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Show current settings
    print("Current quality:", manager.settings.image_default_quality)
    print("Current spacing:", manager.settings.image_default_spacing)
    
    # Modify
    manager.set_setting('image_default_quality', 50)
    manager.set_setting('image_default_spacing', 100)
    print("\n📝 Settings modified")
    
    # Reset to defaults
    manager.reset_to_defaults()
    print("✅ Reset to defaults")
    
    print("\nAfter reset:")
    print("Quality:", manager.settings.image_default_quality)
    print("Spacing:", manager.settings.image_default_spacing)


def example_8_custom_preset():
    """Example 8: Create custom preset"""
    print("\n" + "="*60)
    print("Example 8: Custom Preset - High Quality Images")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Create high-quality preset
    print("Creating 'High Quality' preset...")
    
    manager.set_setting('image_default_quality', 100)
    manager.set_setting('image_default_spacing', 30)
    manager.set_setting('image_default_filter', 'sharpen')
    manager.set_setting('image_add_watermark', True)
    manager.set_setting('image_watermark_text', '© High Quality Portfolio')
    manager.set_setting('output_use_timestamp', True)
    manager.set_setting('output_create_backup', True)
    
    # Save as preset
    preset_file = 'preset_high_quality.json'
    manager.export_settings(preset_file)
    
    print(f"✅ High Quality preset saved to: {preset_file}")
    print("\nPreset settings:")
    print(f"  Quality: {manager.settings.image_default_quality}")
    print(f"  Spacing: {manager.settings.image_default_spacing}")
    print(f"  Filter: {manager.settings.image_default_filter}")
    print(f"  Watermark: {manager.settings.image_watermark_text}")


def example_9_batch_settings():
    """Example 9: Update multiple settings at once"""
    print("\n" + "="*60)
    print("Example 9: Batch Settings Update")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Define batch updates
    updates = {
        'image_default_quality': 95,
        'image_default_spacing': 15,
        'image_default_layout': 'grid',
        'text_default_separator': 'fancy',
        'text_add_timestamps': True,
        'output_use_timestamp': True,
        'ui_show_statistics': True
    }
    
    print("Applying batch updates...")
    for key, value in updates.items():
        manager.set_setting(key, value)
        print(f"  ✓ {key}: {value}")
    
    # Save all changes
    manager.save_settings()
    print("\n✅ All settings updated and saved!")


def example_10_conditional_settings():
    """Example 10: Apply settings conditionally"""
    print("\n" + "="*60)
    print("Example 10: Conditional Settings")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Check if processing large files
    processing_large_files = True
    
    if processing_large_files:
        print("Detected large files - applying optimized settings...")
        
        # Reduce quality for faster processing
        manager.set_setting('image_default_quality', 85)
        
        # Increase workers
        manager.set_setting('performance_max_workers', 8)
        
        # Enable cache
        manager.set_setting('performance_enable_cache', True)
        
        print("✅ Optimized settings applied:")
        print(f"  Quality: {manager.settings.image_default_quality}")
        print(f"  Workers: {manager.settings.performance_max_workers}")
        print(f"  Cache: {manager.settings.performance_enable_cache}")
    
    # For presentations
    creating_portfolio = True
    
    if creating_portfolio:
        print("\nDetected portfolio mode - applying quality settings...")
        
        manager.set_setting('image_default_quality', 100)
        manager.set_setting('image_add_watermark', True)
        manager.set_setting('image_watermark_text', '© My Portfolio 2024')
        manager.set_setting('output_create_backup', True)
        
        print("✅ Portfolio settings applied")


def example_11_get_all_settings():
    """Example 11: Get all settings as dictionary"""
    print("\n" + "="*60)
    print("Example 11: Get All Settings Dictionary")
    print("="*60)
    
    manager = get_settings_manager()
    
    # Get all settings as dict
    all_settings = manager.get_all_settings()
    
    print("All settings:")
    
    # Group by category
    categories = {
        'image': [],
        'text': [],
        'output': [],
        'ui': [],
        'performance': [],
        'advanced': []
    }
    
    for key, value in all_settings.items():
        for category in categories.keys():
            if key.startswith(category):
                categories[category].append((key, value))
                break
    
    for category, settings in categories.items():
        if settings:
            print(f"\n{category.upper()}:")
            for key, value in settings:
                print(f"  {key}: {value}")


def example_12_settings_with_processing():
    """Example 12: Use settings in actual processing"""
    print("\n" + "="*60)
    print("Example 12: Settings with Image Processing")
    print("="*60)
    
    # Setup custom settings
    manager = get_settings_manager()
    manager.set_setting('image_default_layout', 'grid')
    manager.set_setting('image_default_quality', 95)
    manager.set_setting('image_add_watermark', True)
    manager.apply_to_config()
    
    print("✅ Custom settings applied")
    
    # Now use in processing
    from core.image_processor import ImageProcessor
    from config import ImageConfig
    
    processor = ImageProcessor()
    
    # Settings are automatically used
    print(f"\nCurrent settings from config:")
    print(f"  Layout: {ImageConfig.DEFAULT_LAYOUT}")
    print(f"  Quality: {ImageConfig.DEFAULT_QUALITY}")
    print(f"  Spacing: {ImageConfig.DEFAULT_SPACING}")
    
    # Process with these settings
    # processor.process_and_merge(...)
    print("\n💡 Processor will use these default settings!")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("SETTINGS MANAGER - USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples show how to use Settings Manager API\n")
    
    examples = [
        ("Load and Display", example_1_load_and_display),
        ("Modify Settings", example_2_modify_settings),
        ("Apply to Config", example_3_apply_to_config),
        ("Validate Settings", example_4_validate_settings),
        ("Backup & Restore", example_5_backup_restore),
        ("Export & Import", example_6_export_import),
        ("Reset Defaults", example_7_reset_defaults),
        ("Custom Preset", example_8_custom_preset),
        ("Batch Updates", example_9_batch_settings),
        ("Conditional Settings", example_10_conditional_settings),
        ("Get All Settings", example_11_get_all_settings),
        ("Settings with Processing", example_12_settings_with_processing),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i:2}. {name}")
    
    print("\nRun specific example by uncommenting it in main()")
    print("Or run interactively by selecting number\n")
    
    # Uncomment to run specific examples:
    # example_1_load_and_display()
    # example_2_modify_settings()
    # example_3_apply_to_config()
    # example_4_validate_settings()
    # example_5_backup_restore()
    # example_6_export_import()
    # example_7_reset_defaults()
    # example_8_custom_preset()
    # example_9_batch_settings()
    # example_10_conditional_settings()
    # example_11_get_all_settings()
    # example_12_settings_with_processing()
    
    print("="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()