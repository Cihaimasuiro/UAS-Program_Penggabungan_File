"""
Configuration module for File Merger Pro
Menyimpan semua konstanta, settings, dan konfigurasi aplikasi
"""

import os
from pathlib import Path

# ==================== APPLICATION INFO ====================
APP_NAME = "File Merger Pro"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Anindyar Bintang Rahma Esa"
APP_DESCRIPTION = "Advanced file merging tool with GUI support"

# ==================== PATHS ====================
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
LOG_DIR = BASE_DIR / "logs"

# Buat direktori jika belum ada
for directory in [OUTPUT_DIR, TEMP_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# ==================== FILE TYPES ====================
SUPPORTED_IMAGE_FORMATS = {
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.ico', '.svg'
}

SUPPORTED_TEXT_FORMATS = {
    '.txt', '.md', '.csv', '.json', '.xml', 
    '.log', '.ini', '.yaml', '.yml'
}

SUPPORTED_DOCUMENT_FORMATS = {
    '.pdf', '.docx', '.doc', '.odt'
}

ALL_SUPPORTED_FORMATS = (
    SUPPORTED_IMAGE_FORMATS | 
    SUPPORTED_TEXT_FORMATS | 
    SUPPORTED_DOCUMENT_FORMATS
)

# ==================== IMAGE PROCESSING ====================
class ImageConfig:
    """Konfigurasi untuk pemrosesan gambar"""
    
    # Grid layouts
    LAYOUT_VERTICAL = "vertical"
    LAYOUT_HORIZONTAL = "horizontal"
    LAYOUT_GRID = "grid"
    LAYOUT_CUSTOM = "custom"
    
    # Default settings
    DEFAULT_LAYOUT = LAYOUT_VERTICAL
    DEFAULT_SPACING = 10  # pixels
    DEFAULT_BACKGROUND = (255, 255, 255)  # white
    DEFAULT_QUALITY = 95  # JPEG quality
    
    # Max dimensions (untuk prevent memory issues)
    MAX_IMAGE_WIDTH = 10000
    MAX_IMAGE_HEIGHT = 10000
    MAX_GRID_SIZE = 100  # max total images
    
    # Resize options
    RESIZE_MODES = {
        'fit': 'Fit to dimension',
        'fill': 'Fill and crop',
        'stretch': 'Stretch to fit',
        'none': 'Keep original'
    }
    
    # Filters available
    FILTERS = {
        'none': 'No filter',
        'grayscale': 'Grayscale',
        'sepia': 'Sepia tone',
        'blur': 'Blur',
        'sharpen': 'Sharpen',
        'edge': 'Edge enhance'
    }

# ==================== TEXT PROCESSING ====================
class TextConfig:
    """Konfigurasi untuk pemrosesan teks"""
    
    DEFAULT_ENCODING = 'utf-8'
    FALLBACK_ENCODINGS = ['latin-1', 'cp1252', 'iso-8859-1']
    
    # Separator styles
    SEPARATOR_STYLES = {
        'simple': '=== {filename} ===',
        'fancy': '╔══════════════════════════════════════╗\n║ {filename}\n╚══════════════════════════════════════╝',
        'minimal': '--- {filename} ---',
        'none': '{filename}'
    }
    
    DEFAULT_SEPARATOR = 'simple'
    ADD_LINE_NUMBERS = False
    ADD_TIMESTAMPS = False
    STRIP_WHITESPACE = False

# ==================== OUTPUT SETTINGS ====================
class OutputConfig:
    """Konfigurasi untuk output files"""
    
    # Naming conventions
    DEFAULT_IMAGE_OUTPUT = "merged_images.png"
    DEFAULT_TEXT_OUTPUT = "merged_text.txt"
    DEFAULT_PDF_OUTPUT = "merged_document.pdf"
    
    # Auto-naming dengan timestamp
    USE_TIMESTAMP = True
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    
    # Overwrite behavior
    AUTO_OVERWRITE = False
    CREATE_BACKUP = True

# ==================== LOGGING ====================
class LogConfig:
    """Konfigurasi untuk logging"""
    
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOG_DIR / "app.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5

# ==================== PERFORMANCE ====================
class PerformanceConfig:
    """Konfigurasi untuk performa"""
    
    USE_ASYNC = True
    MAX_WORKERS = 4  # untuk thread pool
    CHUNK_SIZE = 8192  # untuk file reading
    ENABLE_CACHING = True
    CACHE_SIZE = 128  # MB

# ==================== UI SETTINGS ====================
class UIConfig:
    """Konfigurasi untuk user interface"""
    
    # CLI
    CLI_PROMPT = "FileMerger> "
    CLI_HISTORY_FILE = BASE_DIR / ".cli_history"
    
    # GUI (untuk future web interface)
    GUI_THEME = "dark"
    GUI_PORT = 8080
    GUI_HOST = "localhost"

# ==================== ERROR MESSAGES ====================
ERROR_MESSAGES = {
    'file_not_found': "File tidak ditemukan: {path}",
    'invalid_format': "Format file tidak didukung: {format}",
    'read_error': "Gagal membaca file: {error}",
    'write_error': "Gagal menulis file: {error}",
    'permission_error': "Tidak ada permission untuk akses file: {path}",
    'memory_error': "Memori tidak cukup untuk memproses file",
    'empty_input': "Tidak ada file yang dipilih untuk diproses",
    'mixed_types': "Tidak dapat menggabungkan file dengan tipe berbeda"
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    'merge_complete': "✓ Berhasil menggabungkan {count} file",
    'save_complete': "✓ File disimpan ke: {path}",
    'batch_complete': "✓ Batch processing selesai: {count}/{total} berhasil"
}

# ==================== HELPER FUNCTIONS ====================
def get_output_path(filename: str, use_timestamp: bool = None) -> Path:
    """Generate output path dengan optional timestamp"""
    if use_timestamp is None:
        use_timestamp = OutputConfig.USE_TIMESTAMP
    
    if use_timestamp:
        from datetime import datetime
        timestamp = datetime.now().strftime(OutputConfig.TIMESTAMP_FORMAT)
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
    
    return OUTPUT_DIR / filename

def is_supported_file(filepath: str) -> bool:
    """Check apakah file format didukung"""
    ext = Path(filepath).suffix.lower()
    return ext in ALL_SUPPORTED_FORMATS

def get_file_category(filepath: str) -> str:
    """Tentukan kategori file"""
    ext = Path(filepath).suffix.lower()
    
    if ext in SUPPORTED_IMAGE_FORMATS:
        return 'image'
    elif ext in SUPPORTED_TEXT_FORMATS:
        return 'text'
    elif ext in SUPPORTED_DOCUMENT_FORMATS:
        return 'document'
    return 'unknown'