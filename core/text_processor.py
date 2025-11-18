"""
Text Processor Module
Includes robust CSV/JSON handling and safer merging logic.
"""

from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime
import logging
import json
import csv
import io

from config import TextConfig
from core.file_manager import FileManager

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, config: Optional[TextConfig] = None):
        self.config = config or TextConfig()
        self.file_manager = FileManager()

    def merge_text_files(self, filepaths: List[str], output_path: str,
                        separator_style: str = 'simple',
                        add_line_numbers: bool = False,
                        add_timestamps: bool = False,
                        strip_whitespace: bool = False) -> Tuple[bool, Optional[str]]:
        """Merge text files by streaming content to output."""
        try:
            with open(output_path, 'w', encoding='utf-8') as out_f:
                for fpath in filepaths:
                    content, err = self.file_manager.read_file_safe(fpath)
                    if content is None:
                        logger.warning(f"Skipping {fpath}: {err}")
                        continue

                    if strip_whitespace:
                        content = content.strip()
                    
                    # Process content (in-memory for simplicity, but per-file)
                    if add_line_numbers:
                        lines = content.splitlines()
                        content = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(lines))

                    # Header
                    sep = self._get_separator(Path(fpath).name, separator_style)
                    out_f.write(f"{sep}\n")
                    
                    if add_timestamps:
                        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        out_f.write(f"Processed: {ts}\n\n")
                    else:
                        out_f.write("\n")
                    
                    out_f.write(content)
                    out_f.write("\n\n")
            
            return True, None
        except Exception as e:
            return False, str(e)

    def convert_to_markdown(self, filepaths: List[str], output_path: str) -> Tuple[bool, Optional[str]]:
        """Convert files to a single Markdown document with code blocks."""
        try:
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write(f"# Merged Document\nGenerated: {datetime.now()}\n\n")
                
                for fpath in filepaths:
                    content, err = self.file_manager.read_file_safe(fpath)
                    if not content: continue
                    
                    name = Path(fpath).name
                    ext = Path(fpath).suffix.lstrip('.') or 'text'
                    
                    out_f.write(f"## {name}\n")
                    out_f.write(f"```{ext}\n")
                    out_f.write(content)
                    out_f.write("\n```\n\n")
            return True, None
        except Exception as e:
            return False, str(e)

    def merge_csv_files(self, filepaths: List[str], output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Robust CSV Merging using csv module.
        Handles quoted newlines correctly.
        """
        try:
            headers = []
            
            # First pass: Detect headers from the first valid file
            first_file = None
            for f in filepaths:
                try:
                    with open(f, 'r', encoding='utf-8', newline='') as csvfile:
                        sample = csvfile.read(1024)
                        has_header = csv.Sniffer().has_header(sample)
                        csvfile.seek(0)
                        reader = csv.reader(csvfile)
                        if has_header:
                            headers = next(reader)
                        else:
                            # Generate generic headers if missing
                            headers = [f"Col_{i}" for i in range(len(next(reader)))]
                        first_file = f
                        break
                except Exception:
                    continue

            if not headers:
                return False, "No valid CSV data found."

            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                # Add source column
                writer.writerow(['source_file'] + headers)
                
                for fpath in filepaths:
                    try:
                        with open(fpath, 'r', encoding='utf-8', newline='') as infile:
                            reader = csv.reader(infile)
                            
                            # Skip header if present
                            try:
                                # Naive check: if first row matches our detected headers
                                rows = list(reader)
                                if not rows: continue
                                
                                start_idx = 0
                                if rows[0] == headers:
                                    start_idx = 1
                                
                                name = Path(fpath).name
                                for row in rows[start_idx:]:
                                    writer.writerow([name] + row)
                            except csv.Error:
                                logger.warning(f"CSV Parse Error in {fpath}")
                                
                    except Exception as e:
                        logger.warning(f"Failed to process CSV {fpath}: {e}")
                        
            return True, None
        except Exception as e:
            return False, str(e)

    def merge_json_files(self, filepaths: List[str], output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Merge JSON files.
        - Array mode: Concatenates lists.
        - Object mode: Merges keys (collisions handled by appending filename to key).
        """
        try:
            merged_data = {} # For object mode
            merged_list = [] # For array mode
            is_array_mode = False
            
            # Detect mode from first file
            with open(filepaths[0], 'r', encoding='utf-8') as f:
                first_char = f.read(1).strip()
                if first_char == '[':
                    is_array_mode = True

            for fpath in filepaths:
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        if is_array_mode:
                            if isinstance(data, list):
                                merged_list.extend(data)
                            else:
                                merged_list.append(data)
                        else:
                            # Object merge
                            if isinstance(data, dict):
                                fname = Path(fpath).stem
                                # Avoid overwriting: Namespace the keys if collision risk?
                                # Simple strategy: Add as sub-object keyed by filename
                                merged_data[fname] = data
                            else:
                                logger.warning(f"Skipping {fpath}: Expected dict, got list/primitive")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {fpath}")

            with open(output_path, 'w', encoding='utf-8') as out:
                json.dump(merged_list if is_array_mode else merged_data, out, indent=2)
                
            return True, None
        except Exception as e:
            return False, str(e)

    def _get_separator(self, filename, style):
        # Safer formatting using f-strings instead of format()
        if style == 'fancy':
            return f"╔{'═'*40}╗\n║ {filename}\n╚{'═'*40}╝"
        elif style == 'minimal':
            return f"--- {filename} ---"
        elif style == 'none':
            return ""
        return f"=== {filename} ==="