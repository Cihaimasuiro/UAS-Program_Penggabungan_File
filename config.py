"""
Configuration Module
Centralizes application constants, file types, and default settings.
Standardized to English for consistency.
"""

import os
from pathlib import Path

# ==================== APPLICATION INFO ====================
APP_NAME = "File Merger Pro"
APP_VERSION = "2.3.0"
APP_AUTHOR = "Tim Damkar (TIA6) - Universitas Duta Bangsa Surakarta"
APP_DESCRIPTION = "Advanced file merging tool with Bauhaus-style GUI"

# ==================== PATHS ====================
BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
LOG_DIR = BASE_DIR / "logs"

for directory in [OUTPUT_DIR, TEMP_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==================== FILE TYPES ====================
SUPPORTED_IMAGE_FORMATS = {
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.ico'
}

SUPPORTED_TEXT_FORMATS = {
    '.txt', '.md', '.csv', '.json', '.xml', 
    '.log', '.ini', '.yaml', '.yml',
    '.html', '.htm', '.css', '.js', '.php', '.asp', '.jsx', '.ts',
    '.py', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rs', '.sh', '.bat', '.sql'
}

SUPPORTED_DOCUMENT_FORMATS = {
    '.pdf', '.docx', '.doc', '.odt'
}

SUPPORTED_OFFICE_FORMATS = {
    '.xlsx', '.xls', '.pptx', '.ppt'
}

SUPPORTED_BINARY_FORMATS = {
    '.exe', '.msi', '.bin', '.dll',
    '.zip', '.rar', '.7z', '.tar', '.gz'
}

ALL_SUPPORTED_FORMATS = (
    SUPPORTED_IMAGE_FORMATS | 
    SUPPORTED_TEXT_FORMATS | 
    SUPPORTED_DOCUMENT_FORMATS |
    SUPPORTED_OFFICE_FORMATS |
    SUPPORTED_BINARY_FORMATS
)

# ==================== DEFAULTS: IMAGE ====================
class ImageConfig:
    LAYOUT_VERTICAL = "vertical"
    LAYOUT_HORIZONTAL = "horizontal"
    LAYOUT_GRID = "grid"
    
    DEFAULT_LAYOUT = LAYOUT_VERTICAL
    DEFAULT_SPACING = 10
    DEFAULT_BACKGROUND = (255, 255, 255)
    DEFAULT_QUALITY = 95
    
    RESIZE_MODES = {
        'none': 'Original Size',
        'fit': 'Fit to Box (Aspect Ratio)',
        'fill': 'Fill Box (Crop)',
        'stretch': 'Stretch (Distort)'
    }
    
    FILTERS = {
        'none': 'No Filter',
        'grayscale': 'B&W / Grayscale',
        'sepia': 'Sepia Tone',
        'blur': 'Gaussian Blur',
        'sharpen': 'Sharpen',
    }

# ==================== DEFAULTS: TEXT ====================
class TextConfig:
    DEFAULT_ENCODING = 'utf-8'
    DEFAULT_SEPARATOR = 'simple'
    SEPARATOR_STYLES = {
        'simple': '=== {filename} ===',
        'fancy': '╔{border}╗\n║ {filename}\n╚{border}╝',
        'minimal': '--- {filename} ---',
        'none': ''
    }

# ==================== DEFAULTS: PDF (NEW) ====================
class PdfConfig:
    DEFAULT_PAGE_SIZE = 'A4' # A4, LETTER
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_FONT_SIZE = 10
    SHOW_PAGE_NUMBERS = True
    
    PAGE_SIZES = {
        'A4': (595.27, 841.89),
        'LETTER': (612.0, 792.0),
        'LEGAL': (612.0, 1008.0)
    }

# ==================== LOGGING & OUTPUT ====================
class LogConfig:
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOG_DIR / "app.log"

class OutputConfig:
    USE_TIMESTAMP = True
    AUTO_OVERWRITE = False
    CREATE_BACKUP = True

# ==================== HELPERS ====================
def get_output_path(filename: str, use_timestamp: bool = True) -> Path:
    name, ext = os.path.splitext(filename)
    if use_timestamp:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{ts}{ext}"
    return OUTPUT_DIR / filename

def is_supported_file(filepath: str) -> bool:
    return Path(filepath).suffix.lower() in ALL_SUPPORTED_FORMATS

def get_file_category(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext in SUPPORTED_IMAGE_FORMATS: return 'image'
    if ext in SUPPORTED_TEXT_FORMATS: return 'text'
    if ext in SUPPORTED_DOCUMENT_FORMATS: return 'document'
    if ext in SUPPORTED_OFFICE_FORMATS: return 'office'
    if ext in SUPPORTED_BINARY_FORMATS: return 'binary'
    return 'unknown'