"""
File Manager Module
Handles file I/O with safety checks and decoupling from specific libraries.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
import logging

from config import is_supported_file, get_file_category

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
    
    @staticmethod
    def validate_file(filepath: str) -> Tuple[bool, Optional[str]]:
        """Validate file existence, format, and basic security checks."""
        try:
            path = Path(filepath).resolve()
            
            if not path.exists():
                return False, "File not found"
            if not path.is_file():
                return False, "Not a file"
            
            # Basic Read Permission Check
            if not os.access(filepath, os.R_OK):
                return False, "Permission denied"
            
            # Check format support
            if not is_supported_file(filepath):
                return False, f"Unsupported format: {path.suffix}"
                
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def check_file_types_consistency(filepaths: List[str]) -> Tuple[bool, str]:
        """
        Check if files are consistent or mixed.
        Now returns True for 'mixed' to allow Universal Merging.
        """
        if not filepaths: return False, 'unknown'
        
        first_cat = get_file_category(filepaths[0])
        is_consistent = True
        
        for f in filepaths[1:]:
            if get_file_category(f) != first_cat:
                is_consistent = False
                break
        
        if is_consistent:
            return True, first_cat
        else:
            # Valid "Mixed" state for Universal Processor
            return True, 'mixed'

    @staticmethod
    def get_file_info(filepath: str) -> dict:
        """Get safe file metadata."""
        try:
            path = Path(filepath)
            stat = path.stat()
            return {
                'name': path.name,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'category': get_file_category(filepath),
                'extension': path.suffix.lower()
            }
        except Exception:
            return {'name': os.path.basename(filepath), 'size_mb': 0, 'category': 'unknown'}

    @staticmethod
    def safe_write(output_path: str, content, mode='w', encoding='utf-8') -> Tuple[bool, Optional[str]]:
        """Writes content to file safely with automatic backup."""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = path.parent / f"{path.stem}_bak_{timestamp}{path.suffix}"
                try:
                    shutil.copy2(path, backup)
                    logger.info(f"Backup created: {backup}")
                except OSError as e:
                    logger.warning(f"Failed to create backup: {e}")

            if isinstance(content, bytes):
                with open(path, 'wb') as f:
                    f.write(content)
            elif isinstance(content, str):
                with open(path, mode, encoding=encoding) as f:
                    f.write(content)
            else:
                return False, f"Unsupported content type: {type(content)}"
                
            logger.info(f"File saved: {output_path}")
            return True, None
            
        except Exception as e:
            logger.error(f"Write failed: {e}")
            return False, str(e)

    @staticmethod
    def read_file_safe(filepath: str) -> Tuple[Optional[str], Optional[str]]:
        """Attempts to read text file with multiple encodings."""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read(), None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return None, str(e)
        return None, "Failed to decode file (unknown encoding)"

    @staticmethod
    def copy_files_to_folder(files: List[str], dest: str, move: bool = False) -> Tuple[bool, Optional[str]]:
        """Batch copy or move files to destination."""
        try:
            dest_path = Path(dest)
            dest_path.mkdir(parents=True, exist_ok=True)
            errors = []
            for f in files:
                try:
                    src = Path(f)
                    if not src.exists():
                        errors.append(f"{src.name} (not found)")
                        continue
                    dest_file = dest_path / src.name
                    if dest_file.exists():
                        timestamp = datetime.now().strftime("%H%M%S")
                        dest_file = dest_path / f"{src.stem}_{timestamp}{src.suffix}"
                    if move:
                        shutil.move(str(src), str(dest_file))
                    else:
                        shutil.copy2(str(src), str(dest_file))
                except Exception as e:
                    errors.append(f"{src.name} ({str(e)})")
            if errors:
                return False, f"Errors occurred: {', '.join(errors)}"
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_unique_filename(filepath: str) -> str:
        path = Path(filepath)
        if not path.exists(): return str(path)
        counter = 1
        while True:
            new_name = f"{path.stem}_{counter}{path.suffix}"
            new_path = path.parent / new_name
            if not new_path.exists(): return str(new_path)
            counter += 1

    @staticmethod
    def clean_temp_files(temp_dir: str):
        try:
            path = Path(temp_dir)
            if path.exists():
                shutil.rmtree(path)
                path.mkdir()
        except Exception: pass

    @staticmethod
    def get_directory_size(directory: str) -> int:
        total = 0
        try:
            for entry in os.scandir(directory):
                if entry.is_file(): total += entry.stat().st_size
                elif entry.is_dir(): total += FileManager.get_directory_size(entry.path)
        except Exception: pass
        return total