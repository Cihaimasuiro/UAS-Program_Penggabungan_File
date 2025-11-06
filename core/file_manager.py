"""
File Manager Module
Handle semua operasi file: validasi, reading, writing, backup
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
import logging

from config import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, 
    get_file_category, is_supported_file
)

logger = logging.getLogger(__name__)


class FileManager:
    """Class untuk handle operasi file"""
    
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
    
    @staticmethod
    def validate_file(filepath: str) -> Tuple[bool, Optional[str]]:
        """
        Validasi file existence dan format
        Returns: (is_valid, error_message)
        """
        path = Path(filepath)
        
        # Check existence
        if not path.exists():
            return False, ERROR_MESSAGES['file_not_found'].format(path=filepath)
        
        # Check if it's a file
        if not path.is_file():
            return False, f"{filepath} bukan file yang valid"
        
        # Check format support
        if not is_supported_file(filepath):
            ext = path.suffix
            return False, ERROR_MESSAGES['invalid_format'].format(format=ext)
        
        # Check readability
        if not os.access(filepath, os.R_OK):
            return False, ERROR_MESSAGES['permission_error'].format(path=filepath)
        
        return True, None
    
    @staticmethod
    def validate_files(filepaths: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Validasi multiple files
        Returns: (valid_files, failed_files_with_errors)
        """
        valid = []
        failed = []
        
        for filepath in filepaths:
            is_valid, error = FileManager.validate_file(filepath)
            if is_valid:
                valid.append(filepath)
                logger.info(f"✓ Valid: {Path(filepath).name}")
            else:
                failed.append((filepath, error))
                logger.warning(f"✗ Invalid: {filepath} - {error}")
        
        return valid, failed
    
    @staticmethod
    def check_file_types_consistency(filepaths: List[str]) -> Tuple[bool, str]:
        """
        Check apakah semua file punya kategori yang sama
        Returns: (is_consistent, category)
        """
        if not filepaths:
            return False, 'unknown'
        
        categories = set(get_file_category(f) for f in filepaths)
        
        if len(categories) == 1:
            return True, categories.pop()
        else:
            return False, 'mixed'
    
    @staticmethod
    def get_file_info(filepath: str) -> dict:
        """Get informasi detail tentang file"""
        path = Path(filepath)
        stat = path.stat()
        
        return {
            'name': path.name,
            'path': str(path.absolute()),
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': path.suffix.lower(),
            'category': get_file_category(filepath)
        }
    
    @staticmethod
    def create_backup(filepath: str) -> Optional[str]:
        """
        Buat backup file jika sudah exist
        Returns: backup path or None
        """
        path = Path(filepath)
        
        if not path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
        backup_path = path.parent / backup_name
        
        try:
            shutil.copy2(filepath, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    @staticmethod
    def safe_write(output_path: str, content, mode='w', encoding='utf-8', 
                   create_backup=True) -> Tuple[bool, Optional[str]]:
        """
        Safe file writing dengan backup option
        Returns: (success, error_message)
        """
        path = Path(output_path)
        
        try:
            # Backup if exists
            if path.exists() and create_backup:
                FileManager.create_backup(output_path)
            
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            if isinstance(content, bytes):
                with open(path, 'wb') as f:
                    f.write(content)
            elif hasattr(content, 'save'):  # PIL Image object
                content.save(path)
            else:
                with open(path, mode, encoding=encoding) as f:
                    f.write(content)
            
            logger.info(SUCCESS_MESSAGES['save_complete'].format(path=output_path))
            return True, None
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['write_error'].format(error=str(e))
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def read_file_safe(filepath: str, mode='r', encoding='utf-8', 
                       fallback_encodings=None) -> Tuple[Optional[str], Optional[str]]:
        """
        Safe file reading dengan fallback encodings
        Returns: (content, error_message)
        """
        if fallback_encodings is None:
            fallback_encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        
        # Try primary encoding
        try:
            with open(filepath, mode, encoding=encoding) as f:
                return f.read(), None
        except UnicodeDecodeError:
            logger.warning(f"Failed with {encoding}, trying fallback encodings")
        except Exception as e:
            return None, ERROR_MESSAGES['read_error'].format(error=str(e))
        
        # Try fallback encodings
        for enc in fallback_encodings:
            try:
                with open(filepath, mode, encoding=enc) as f:
                    logger.info(f"Successfully read with encoding: {enc}")
                    return f.read(), None
            except:
                continue
        
        return None, f"Failed to read file with any encoding"
    
    @staticmethod
    def get_unique_filename(filepath: str) -> str:
        """Generate unique filename jika file sudah exist"""
        path = Path(filepath)
        
        if not path.exists():
            return filepath
        
        counter = 1
        while True:
            new_name = f"{path.stem}_{counter}{path.suffix}"
            new_path = path.parent / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1
    
    @staticmethod
    def clean_temp_files(temp_dir: str):
        """Bersihkan temporary files"""
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)
            logger.info("Temporary files cleaned")
        except Exception as e:
            logger.error(f"Failed to clean temp files: {e}")
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size

    @staticmethod
    def copy_files_to_folder(filepaths: List[str], dest_dir: str, move: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Copy or move a list of files into a destination folder.
        Returns: (success, error_message)
        """
        path = Path(dest_dir)
        try:
            path.mkdir(parents=True, exist_ok=True)
            failed = []
            for filepath in filepaths:
                src = Path(filepath)
                if not src.exists():
                    failed.append((filepath, 'not found'))
                    continue
                try:
                    if move:
                        shutil.move(str(src), str(path))
                    else:
                        shutil.copy2(str(src), str(path))
                    logger.info(f"Copied: {src.name} -> {path}")
                except Exception as e:
                    logger.error(f"Failed to copy {src}: {e}")
                    failed.append((filepath, str(e)))

            if failed:
                return False, f"Some files failed to copy: {failed}"
            return True, None
        except Exception as e:
            logger.error(f"Failed to create destination folder or copy files: {e}")
            return False, str(e)
    
    def get_statistics(self) -> dict:
        """Get statistik dari processing yang sudah dilakukan"""
        return {
            'total_processed': len(self.processed_files),
            'total_failed': len(self.failed_files),
            'success_rate': (
                len(self.processed_files) / 
                (len(self.processed_files) + len(self.failed_files)) * 100
                if (self.processed_files or self.failed_files) else 0
            )
        }