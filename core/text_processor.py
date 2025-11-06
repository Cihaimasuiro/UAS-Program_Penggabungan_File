"""
Text Processor Module
Handle text file operations: merging, formatting, encoding
"""

from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime
import logging
import json
import csv

from config import TextConfig, ERROR_MESSAGES
from core.file_manager import FileManager

logger = logging.getLogger(__name__)


class TextProcessor:
    """Advanced text processing class"""
    
    def __init__(self, config: Optional[TextConfig] = None):
        self.config = config or TextConfig()
        self.file_manager = FileManager()
    
    def read_text_file(self, filepath: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Read text file dengan fallback encoding
        Returns: (content, error_message)
        """
        return self.file_manager.read_file_safe(
            filepath,
            encoding=self.config.DEFAULT_ENCODING,
            fallback_encodings=self.config.FALLBACK_ENCODINGS
        )
    
    def format_separator(self, filename: str, style: str = 'simple') -> str:
        """Generate separator berdasarkan style"""
        separator_template = self.config.SEPARATOR_STYLES.get(
            style, 
            self.config.SEPARATOR_STYLES['simple']
        )
        
        return separator_template.format(filename=filename)
    
    def add_line_numbers(self, content: str) -> str:
        """Add line numbers ke content"""
        lines = content.split('\n')
        numbered = []
        
        max_digits = len(str(len(lines)))
        
        for i, line in enumerate(lines, 1):
            numbered.append(f"{i:>{max_digits}}: {line}")
        
        return '\n'.join(numbered)
    
    def add_metadata(self, filename: str, content: str, 
                    add_timestamp: bool = True,
                    add_file_info: bool = True) -> str:
        """Add metadata ke content"""
        metadata = []
        
        if add_file_info:
            info = self.file_manager.get_file_info(filename)
            metadata.append(f"File: {info['name']}")
            metadata.append(f"Size: {info['size_mb']} MB")
            metadata.append(f"Modified: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if add_timestamp:
            metadata.append(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if metadata:
            return '\n'.join(metadata) + '\n\n' + content
        
        return content
    
    def merge_text_files(self, filepaths: List[str], 
                        output_path: str,
                        separator_style: str = 'simple',
                        add_line_numbers: bool = False,
                        add_timestamps: bool = False,
                        strip_whitespace: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Merge multiple text files dengan formatting options
        Returns: (success, error_message)
        """
        try:
            merged_content = []
            failed_files = []
            
            for filepath in filepaths:
                # Read file
                content, error = self.read_text_file(filepath)
                
                if content is None:
                    logger.error(f"Failed to read {filepath}: {error}")
                    failed_files.append((filepath, error))
                    continue
                
                # Strip whitespace if needed
                if strip_whitespace:
                    content = content.strip()
                
                # Add line numbers if needed
                if add_line_numbers:
                    content = self.add_line_numbers(content)
                
                # Add metadata if needed
                if add_timestamps:
                    content = self.add_metadata(filepath, content)
                
                # Add separator
                filename = Path(filepath).name
                separator = self.format_separator(filename, separator_style)
                
                merged_content.append(f"\n{separator}\n\n{content}\n")
                logger.info(f"✓ Added: {filename}")
            
            if not merged_content:
                return False, "No files could be processed"
            
            # Join all content
            final_content = '\n'.join(merged_content)
            
            # Save
            success, error = self.file_manager.safe_write(
                output_path, 
                final_content,
                encoding=self.config.DEFAULT_ENCODING
            )
            
            if success:
                logger.info(f"✓ Merged {len(merged_content)} files successfully")
                if failed_files:
                    logger.warning(f"✗ Failed to process {len(failed_files)} files")
                return True, None
            else:
                return False, error
            
        except Exception as e:
            error_msg = f"Error during text merging: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def merge_json_files(self, filepaths: List[str], 
                        output_path: str,
                        merge_mode: str = 'array') -> Tuple[bool, Optional[str]]:
        """
        Merge JSON files
        merge_mode: 'array' (list of objects) or 'object' (merge into one object)
        """
        try:
            if merge_mode == 'array':
                merged_data = []
                
                for filepath in filepaths:
                    content, error = self.read_text_file(filepath)
                    if content:
                        try:
                            data = json.loads(content)
                            merged_data.append({
                                'source': Path(filepath).name,
                                'data': data
                            })
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in {filepath}: {e}")
                
                result = json.dumps(merged_data, indent=2, ensure_ascii=False)
            
            elif merge_mode == 'object':
                merged_data = {}
                
                for filepath in filepaths:
                    content, error = self.read_text_file(filepath)
                    if content:
                        try:
                            data = json.loads(content)
                            filename = Path(filepath).stem
                            merged_data[filename] = data
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in {filepath}: {e}")
                
                result = json.dumps(merged_data, indent=2, ensure_ascii=False)
            
            # Save
            success, error = self.file_manager.safe_write(output_path, result)
            return success, error
            
        except Exception as e:
            error_msg = f"Error merging JSON files: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def merge_csv_files(self, filepaths: List[str], 
                       output_path: str,
                       add_source_column: bool = True) -> Tuple[bool, Optional[str]]:
        """Merge CSV files with optional source tracking"""
        try:
            all_rows = []
            headers = None
            
            for filepath in filepaths:
                content, error = self.read_text_file(filepath)
                if not content:
                    continue
                
                # Parse CSV
                lines = content.strip().split('\n')
                reader = csv.reader(lines)
                
                file_rows = list(reader)
                if not file_rows:
                    continue
                
                # Get headers from first file
                if headers is None:
                    headers = file_rows[0]
                    if add_source_column:
                        headers.append('source_file')
                
                # Add data rows
                source_name = Path(filepath).name
                for row in file_rows[1:]:
                    if add_source_column:
                        row.append(source_name)
                    all_rows.append(row)
            
            if not all_rows or headers is None:
                return False, "No CSV data to merge"
            
            # Write merged CSV
            output_lines = [','.join(f'"{cell}"' for cell in headers)]
            for row in all_rows:
                output_lines.append(','.join(f'"{cell}"' for cell in row))
            
            result = '\n'.join(output_lines)
            
            success, error = self.file_manager.safe_write(output_path, result)
            return success, error
            
        except Exception as e:
            error_msg = f"Error merging CSV files: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def convert_to_markdown(self, filepaths: List[str], 
                          output_path: str) -> Tuple[bool, Optional[str]]:
        """Convert merged files to markdown format"""
        try:
            markdown_content = []
            markdown_content.append("# Merged Document\n")
            markdown_content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            markdown_content.append("---\n")
            
            for filepath in filepaths:
                content, error = self.read_text_file(filepath)
                if not content:
                    continue
                
                filename = Path(filepath).name
                
                # Add section
                markdown_content.append(f"\n## {filename}\n")
                markdown_content.append("```")
                markdown_content.append(content)
                markdown_content.append("```\n")
            
            result = '\n'.join(markdown_content)
            
            success, error = self.file_manager.safe_write(output_path, result)
            return success, error
            
        except Exception as e:
            error_msg = f"Error converting to markdown: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_statistics(self, filepaths: List[str]) -> Dict:
        """Get statistics dari text files"""
        stats = {
            'total_files': len(filepaths),
            'total_lines': 0,
            'total_words': 0,
            'total_chars': 0,
            'file_details': []
        }
        
        for filepath in filepaths:
            content, error = self.read_text_file(filepath)
            if content:
                lines = content.count('\n') + 1
                words = len(content.split())
                chars = len(content)
                
                stats['total_lines'] += lines
                stats['total_words'] += words
                stats['total_chars'] += chars
                
                stats['file_details'].append({
                    'name': Path(filepath).name,
                    'lines': lines,
                    'words': words,
                    'chars': chars
                })
        
        return stats