# file: core/__init__.py
"""
Core package - Contains main business logic modules
"""

from .file_manager import FileManager
from .image_processor import ImageProcessor
from .text_processor import TextProcessor

__all__ = ['FileManager', 'ImageProcessor', 'TextProcessor']    