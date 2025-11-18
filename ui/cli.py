"""
CLI Interface Module - Universal Edition v2.1
"""

import sys
from pathlib import Path
from config import APP_NAME, APP_VERSION, get_output_path
from core.file_manager import FileManager
from core.image_processor import ImageProcessor
from core.text_processor import TextProcessor
from core.universal_processor import UniversalProcessor
from core.settings_manager import get_settings_manager

class CLI:
    def __init__(self):
        self.file_manager = FileManager()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        self.universal_processor = UniversalProcessor()
        self.files = []
    
    def add_files(self):
        print("\n📁 ADD FILES (Empty line to finish)")
        while True:
            fp = input("Path: ").strip().strip('"')
            if not fp: break
            valid, err = self.file_manager.validate_file(fp)
            if valid: 
                self.files.append(fp)
                print(f"Added [{len(self.files)}]: {Path(fp).name}")
            else: print(f"Error: {err}")

    def manage_files(self):
        if not self.files:
            print("List is empty.")
            return

        print("\n📋 CURRENT LIST:")
        for i, f in enumerate(self.files):
            print(f"[{i+1}] {Path(f).name}")
        
        print("\n[D] Delete specific item  [C] Clear all  [B] Back")
        choice = input("Choice: ").strip().upper()
        
        if choice == 'D':
            try:
                idx = int(input("Enter number to delete: ")) - 1
                if 0 <= idx < len(self.files):
                    removed = self.files.pop(idx)
                    print(f"Removed: {Path(removed).name}")
                else:
                    print("Invalid index.")
            except ValueError:
                print("Invalid input.")
        elif choice == 'C':
            self.files = []
            print("List cleared.")

    def process_files(self):
        if not self.files: return print("No files.")
        
        valid, cat = self.file_manager.check_file_types_consistency(self.files)
        print(f"\nCategory: {cat.upper()}")
        
        if cat == 'image': self._process_images()
        elif cat == 'text': self._process_text()
        elif cat in ('mixed', 'document'):
            print("Detected mixed/document types. Using Universal PDF Merge.")
            self._process_universal()
        else: print("Unknown category.")

    def _process_universal(self):
        out = input("Output PDF [merged.pdf]: ").strip() or "merged.pdf"
        print("Merging...")
        ok, msg = self.universal_processor.merge_all_to_pdf(self.files, str(get_output_path(out)))
        print(msg) # Print the detailed stats

    def _process_images(self):
        layout = input("Layout [vertical/horizontal/grid]: ").strip() or 'vertical'
        out = input("Output [merged.png]: ").strip() or "merged.png"
        ok, msg = self.image_processor.process_and_merge(self.files, str(get_output_path(out)), layout=layout)
        print(msg)

    def _process_text(self):
        out = input("Output [merged.txt]: ").strip() or "merged.txt"
        ok, msg = self.text_processor.merge_text_files(self.files, str(get_output_path(out)))
        print(msg)

    def run(self):
        print(f"{APP_NAME} v{APP_VERSION}")
        get_settings_manager().apply_to_config()
        while True:
            c = input("\n[1] Add Files  [2] Manage List  [3] Process  [0] Exit: ").strip()
            if c=='0': sys.exit()
            elif c=='1': self.add_files()
            elif c=='2': self.manage_files()
            elif c=='3': self.process_files()

if __name__ == "__main__":
    CLI().run()