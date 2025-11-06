"""
CLI Interface Module
Interactive command line interface dengan rich formatting
"""

import sys
from typing import List, Optional
from pathlib import Path
import logging

from config import (
    APP_NAME, APP_VERSION, ImageConfig, TextConfig,
    get_output_path, get_file_category
)
from core.file_manager import FileManager
from core.image_processor import ImageProcessor
from core.text_processor import TextProcessor
from ui.settings_ui import show_settings
from core.settings_manager import get_settings_manager

logger = logging.getLogger(__name__)


class CLI:
    """Command Line Interface handler"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        self.files = []
    
    def print_header(self):
        """Print aplikasi header"""
        print("\n" + "=" * 60)
        print(f"  {APP_NAME} v{APP_VERSION}".center(60))
        print("  Advanced File Merging Tool".center(60))
        print("=" * 60 + "\n")
    
    def print_menu(self):
        """Print main menu"""
        print("\n┌─────────────────────────────────────────┐")
        print("│           MAIN MENU                     │")
        print("├─────────────────────────────────────────┤")
        print("│ 1. Add Files                            │")
        print("│ 2. View Selected Files                  │")
        print("│ 3. Clear Selection                      │")
        print("│ 4. Process & Merge Files                │")
        print("│ 5. Batch Process Directory              │")
        print("│ 6. Settings                             │")
        print("│ 7. Help                                 │")
        print("│ 0. Exit                                 │")
        print("└─────────────────────────────────────────┘\n")
    
    def add_files(self):
        """Interactive file selection"""
        print("\n📁 ADD FILES")
        print("Enter file paths (one per line, empty line to finish):")
        print("Tip: You can drag & drop files here\n")
        
        while True:
            filepath = input("File path: ").strip().strip('"').strip("'")
            
            if not filepath:
                break
            
            # Validate
            is_valid, error = self.file_manager.validate_file(filepath)
            
            if is_valid:
                if filepath not in self.files:
                    self.files.append(filepath)
                    print(f"  ✓ Added: {Path(filepath).name}")
                else:
                    print(f"  ⚠ Already added: {Path(filepath).name}")
            else:
                print(f"  ✗ Error: {error}")
        
        print(f"\n✓ Total files selected: {len(self.files)}")
    
    def view_files(self):
        """Display selected files"""
        if not self.files:
            print("\n⚠ No files selected yet.")
            return
        
        print(f"\n📋 SELECTED FILES ({len(self.files)} files)")
        print("-" * 70)
        
        total_size = 0
        for i, filepath in enumerate(self.files, 1):
            info = self.file_manager.get_file_info(filepath)
            print(f"{i:2}. {info['name']:<40} {info['size_mb']:>8.2f} MB  [{info['category']}]")
            total_size += info['size']
        
        print("-" * 70)
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
    
    def clear_selection(self):
        """Clear selected files"""
        if not self.files:
            print("\n⚠ No files to clear.")
            return
        
        confirm = input(f"\n⚠ Clear {len(self.files)} selected files? (y/n): ").lower()
        if confirm == 'y':
            self.files.clear()
            print("✓ Selection cleared.")
    
    def process_images(self):
        """Process and merge images with options"""
        print("\n🎨 IMAGE PROCESSING OPTIONS")
        
        # Layout
        print("\nSelect layout:")
        print("1. Vertical (stack)")
        print("2. Horizontal (side by side)")
        print("3. Grid (auto)")
        print("4. Grid (custom)")
        
        layout_choice = input("Layout (1-4) [1]: ").strip() or "1"
        layout_map = {'1': 'vertical', '2': 'horizontal', '3': 'grid', '4': 'grid'}
        layout = layout_map.get(layout_choice, 'vertical')
        
        grid_cols = None
        if layout_choice == '4':
            grid_cols = int(input("Number of columns: ").strip() or "3")
        
        # Spacing
        spacing = int(input("Spacing between images (pixels) [10]: ").strip() or "10")
        
        # Resize
        print("\nResize mode:")
        print("1. None (keep original)")
        print("2. Fit (maintain aspect ratio)")
        print("3. Fill (crop to fit)")
        print("4. Stretch")
        
        resize_choice = input("Resize (1-4) [1]: ").strip() or "1"
        resize_map = {'1': 'none', '2': 'fit', '3': 'fill', '4': 'stretch'}
        resize_mode = resize_map.get(resize_choice, 'none')
        
        target_size = None
        if resize_mode != 'none':
            width = input("Target width (pixels): ").strip()
            height = input("Target height (pixels): ").strip()
            if width and height:
                target_size = (int(width), int(height))
        
        # Filter
        print("\nApply filter:")
        print("1. None")
        print("2. Grayscale")
        print("3. Sepia")
        print("4. Blur")
        print("5. Sharpen")
        
        filter_choice = input("Filter (1-5) [1]: ").strip() or "1"
        filter_map = {'1': 'none', '2': 'grayscale', '3': 'sepia', '4': 'blur', '5': 'sharpen'}
        filter_name = filter_map.get(filter_choice, 'none')
        
        # Watermark
        watermark = input("Add watermark text (empty to skip): ").strip() or None
        
        # Output
        output_name = input("Output filename [merged_images.png]: ").strip() or "merged_images.png"
        output_path = str(get_output_path(output_name))
        
        # Process
        print("\n⏳ Processing images...")
        success, error = self.image_processor.process_and_merge(
            self.files,
            output_path,
            layout=layout,
            resize_mode=resize_mode,
            target_size=target_size,
            filter_name=filter_name,
            watermark=watermark,
            spacing=spacing,
            grid_cols=grid_cols
        )
        
        if success:
            print(f"\n✅ Success! Saved to: {output_path}")
        else:
            print(f"\n❌ Error: {error}")
    
    def process_text(self):
        """Process and merge text files"""
        print("\n📝 TEXT PROCESSING OPTIONS")
        
        # Separator style
        print("\nSeparator style:")
        print("1. Simple")
        print("2. Fancy")
        print("3. Minimal")
        print("4. None")
        
        sep_choice = input("Style (1-4) [1]: ").strip() or "1"
        sep_map = {'1': 'simple', '2': 'fancy', '3': 'minimal', '4': 'none'}
        separator_style = sep_map.get(sep_choice, 'simple')
        
        # Options
        add_line_numbers = input("Add line numbers? (y/n) [n]: ").lower() == 'y'
        add_timestamps = input("Add timestamps? (y/n) [n]: ").lower() == 'y'
        strip_whitespace = input("Strip whitespace? (y/n) [n]: ").lower() == 'y'
        
        # Output format
        print("\nOutput format:")
        print("1. Text (.txt)")
        print("2. Markdown (.md)")
        
        format_choice = input("Format (1-2) [1]: ").strip() or "1"
        
        if format_choice == '2':
            output_name = input("Output filename [merged.md]: ").strip() or "merged.md"
            output_path = str(get_output_path(output_name))
            
            print("\n⏳ Converting to markdown...")
            success, error = self.text_processor.convert_to_markdown(
                self.files, output_path
            )
        else:
            output_name = input("Output filename [merged.txt]: ").strip() or "merged.txt"
            output_path = str(get_output_path(output_name))
            
            print("\n⏳ Merging text files...")
            success, error = self.text_processor.merge_text_files(
                self.files,
                output_path,
                separator_style=separator_style,
                add_line_numbers=add_line_numbers,
                add_timestamps=add_timestamps,
                strip_whitespace=strip_whitespace
            )
        
        if success:
            print(f"\n✅ Success! Saved to: {output_path}")
            
            # Show statistics
            stats = self.text_processor.get_statistics(self.files)
            print(f"\n📊 Statistics:")
            print(f"  Files: {stats['total_files']}")
            print(f"  Lines: {stats['total_lines']:,}")
            print(f"  Words: {stats['total_words']:,}")
            print(f"  Characters: {stats['total_chars']:,}")
        else:
            print(f"\n❌ Error: {error}")
    
    def process_files(self):
        """Main processing dispatcher"""
        if not self.files:
            print("\n⚠ No files selected. Please add files first.")
            return
        
        # Check file types consistency
        is_consistent, category = self.file_manager.check_file_types_consistency(self.files)
        
        if not is_consistent:
            print("\n⚠ Warning: Mixed file types detected!")
            print("All files should be of the same type (all images or all text).")
            return
        
        if category == 'image':
            self.process_images()
        elif category == 'text':
            self.process_text()
        else:
            print(f"\n⚠ Unsupported file category: {category}")
    
    def batch_process(self):
        """Batch process all files in directory"""
        print("\n📦 BATCH PROCESSING")
        directory = input("Enter directory path: ").strip().strip('"')
        
        if not Path(directory).exists():
            print("❌ Directory not found.")
            return
        
        print("\nSelect file type to process:")
        print("1. Images")
        print("2. Text files")
        
        choice = input("Type (1-2): ").strip()
        
        # Get all files in directory
        path = Path(directory)
        if choice == '1':
            extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        else:
            extensions = {'.txt', '.md', '.log', '.csv'}
        
        files = [str(f) for f in path.iterdir() if f.suffix.lower() in extensions]
        
        if not files:
            print(f"❌ No matching files found in directory.")
            return
        
        print(f"\n✓ Found {len(files)} files")
        self.files = files
        self.view_files()
        
        confirm = input("\nProcess these files? (y/n): ").lower()
        if confirm == 'y':
            self.process_files()
    
    def show_help(self):
        """Show help information"""
        print("\n" + "=" * 60)
        print("  HELP & USAGE".center(60))
        print("=" * 60)
        print("""
📖 How to use File Merger Pro:

1. ADD FILES
   - Select files one by one
   - Drag & drop supported
   - Files will be validated automatically

2. VIEW FILES
   - See all selected files
   - Check file sizes and types

3. PROCESS & MERGE
   - Choose processing options
   - Images: layouts, filters, watermarks
   - Text: separators, formatting, markdown

4. BATCH PROCESS
   - Process entire directory at once
   - Auto-detect file types

💡 Tips:
   - All files must be same type (all images or all text)
   - Output files saved to 'output' directory
   - Use timestamps to avoid overwriting
   - Check logs in 'logs' directory for errors

🎨 Image Features:
   - Multiple layouts (vertical, horizontal, grid)
   - Resize with different modes
   - Apply filters (grayscale, sepia, blur, etc.)
   - Add watermarks

📝 Text Features:
   - Multiple separator styles
   - Add line numbers
   - Add timestamps
   - Convert to Markdown
   - Merge JSON and CSV files

For more info, check the documentation.
        """)
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main CLI loop"""
        self.print_header()
        
        # Load user settings
        from core.settings_manager import get_settings_manager
        settings_mgr = get_settings_manager()
        settings_mgr.apply_to_config()
        
        while True:
            self.print_menu()
            choice = input("Select option (0-7): ").strip()
            
            if choice == '0':
                print("\n👋 Thanks for using File Merger Pro!")
                sys.exit(0)
            
            elif choice == '1':
                self.add_files()
            
            elif choice == '2':
                self.view_files()
            
            elif choice == '3':
                self.clear_selection()
            
            elif choice == '4':
                self.process_files()
            
            elif choice == '5':
                self.batch_process()
            
            elif choice == '6':
                            logger.info("Entering settings menu...")
                            show_settings()
                            logger.info("Exited settings menu.")
                            
                            try:
                                get_settings_manager().apply_to_config()
                                self.image_processor = ImageProcessor()
                                self.text_processor = TextProcessor()
                                print("\n✅ Settings applied to current session!")
                            except Exception as e:
                                logger.error(f"Failed to re-apply settings: {e}")
            
            elif choice == '7':
                self.show_help()
            
            else:
                print("\n❌ Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    cli = CLI()
    cli.run()