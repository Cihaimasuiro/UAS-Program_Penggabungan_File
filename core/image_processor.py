# file: core/image_processor.py

"""
Image Processor Module
Handle advanced image operations: merging, resizing, filters, watermarks
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Dict
import logging
from pathlib import Path
import math

from config import ImageConfig, ERROR_MESSAGES
from core.file_manager import FileManager

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Advanced image processing class"""
    
    def __init__(self, config: Optional[ImageConfig] = None):
        self.config = config or ImageConfig()
        self.file_manager = FileManager()
    
    def load_images(self, filepaths: List[str]) -> Tuple[List[Image.Image], List[str]]:
        """
        Load multiple images
        Returns: (loaded_images, failed_files)
        """
        images = []
        failed = []
        
        for filepath in filepaths:
            try:
                img = Image.open(filepath)
                img.load() 
                
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                images.append(img)
                logger.info(f"✓ Loaded: {Path(filepath).name} ({img.size})")
            except Exception as e:
                logger.error(f"✗ Failed to load {filepath}: {e}")
                failed.append(filepath)
        
        return images, failed
    
    def resize_image(self, image: Image.Image, target_size: Tuple[int, int], 
                     mode: str = 'fit') -> Image.Image:
        """
        Resize image dengan berbagai mode
        """
        if mode == 'none':
            return image
        
        original_size = image.size
        
        if mode == 'fit':
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            return image
        
        elif mode == 'fill':
            scale = max(target_size[0] / original_size[0], 
                       target_size[1] / original_size[1])
            new_size = (int(original_size[0] * scale), 
                       int(original_size[1] * scale))
            
            img = image.resize(new_size, Image.Resampling.LANCZOS)
            
            left = (img.width - target_size[0]) // 2
            top = (img.height - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]
            
            return img.crop((left, top, right, bottom))
        
        elif mode == 'stretch':
            return image.resize(target_size, Image.Resampling.LANCZOS)
        
        return image
    
    def apply_filter(self, image: Image.Image, filter_name: str) -> Image.Image:
        """Apply filter ke image"""
        if filter_name == 'none':
            return image
        
        if filter_name == 'grayscale':
            return image.copy().convert('L').convert('RGB')
        
        elif filter_name == 'sepia':            
            img = image.convert('RGB')
            pixels = img.load()
            
            if pixels is None:
                logger.warning("Gagal memuat pixel data untuk filter sepia.")
                return image 
            
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    # Sepia formula
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
            return img
        
        elif filter_name == 'blur':
            return image.copy().filter(ImageFilter.BLUR)
        
        elif filter_name == 'sharpen':
            return image.copy().filter(ImageFilter.SHARPEN)
        
        elif filter_name == 'edge':
            return image.copy().filter(ImageFilter.FIND_EDGES)
        
        return image.copy() # Kembalikan salinan gambar asli jika filter tidak ada
    
    def add_watermark(self, image: Image.Image, text: str, 
                     position: str = 'bottom-right', 
                     opacity: int = 128) -> Image.Image:
        """Add text watermark ke image"""
        img = image.copy()
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        font_size = max(15, int(img.width * 0.03))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            logger.warning("Font Arial tidak ditemukan, menggunakan font default.")
            try:
                font = ImageFont.load_default(size=font_size)
            except:
                font = ImageFont.load_default()
        
        # Gunakan textbbox() yang modern
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = 20
        if position == 'bottom-right':
            x = img.width - text_width - margin
            y = img.height - text_height - margin
        elif position == 'bottom-left':
            x = margin
            y = img.height - text_height - margin
        elif position == 'top-right':
            x = img.width - text_width - margin
            y = margin
        elif position == 'top-left':
            x = margin
            y = margin
        else:  # center
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, opacity), font=font)
        
        img = Image.alpha_composite(img, overlay)
        
        if image.mode != 'RGBA':
            img = img.convert('RGB')
            
        return img
    
    def merge_vertical(self, images: List[Image.Image], 
                      spacing: int = 0, 
                      background: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        if not images:
            raise ValueError("No images to merge")
        
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
        
        result = Image.new('RGB', (max_width, total_height), background)
        
        y_offset = 0
        for img in images:
            x_offset = (max_width - img.width) // 2
            result.paste(img, (x_offset, y_offset))
            y_offset += img.height + spacing
        
        logger.info(f"✓ Merged {len(images)} images vertically: {result.size}")
        return result
    
    def merge_horizontal(self, images: List[Image.Image], 
                        spacing: int = 0,
                        background: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        if not images:
            raise ValueError("No images to merge")
        
        max_height = max(img.height for img in images)
        total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
        
        result = Image.new('RGB', (total_width, max_height), background)
        
        x_offset = 0
        for img in images:
            y_offset = (max_height - img.height) // 2
            result.paste(img, (x_offset, y_offset))
            x_offset += img.width + spacing
        
        logger.info(f"✓ Merged {len(images)} images horizontally: {result.size}")
        return result
    
    def merge_grid(self, images: List[Image.Image], 
                   cols: Optional[int] = None,
                   spacing: int = 0,
                   background: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        if not images:
            raise ValueError("No images to merge")
        
        if cols is None:
            cols = math.ceil(math.sqrt(len(images)))
        
        rows = math.ceil(len(images) / cols)
        
        cell_width = max(img.width for img in images)
        cell_height = max(img.height for img in images)
        
        total_width = cell_width * cols + spacing * (cols - 1)
        total_height = cell_height * rows + spacing * (rows - 1)
        
        result = Image.new('RGB', (total_width, total_height), background)
        
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols
            
            x = col * (cell_width + spacing) + (cell_width - img.width) // 2
            y = row * (cell_height + spacing) + (cell_height - img.height) // 2
            
            result.paste(img, (x, y))
        
        logger.info(f"✓ Merged {len(images)} images in {rows}x{cols} grid: {result.size}")
        return result
    
    def process_and_merge(self, filepaths: List[str], 
                         output_path: str,
                         layout: str = 'vertical',
                         resize_mode: str = 'none',
                         target_size: Optional[Tuple[int, int]] = None,
                         filter_name: str = 'none',
                         watermark: Optional[str] = None,
                         spacing: int = 10,
                         grid_cols: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        try:
            images, failed = self.load_images(filepaths)
            
            if not images:
                return False, "No valid images to process"
            
            processed_images = []
            for img in images:
                processed_img = img 
                
                if target_size and resize_mode != 'none':
                    processed_img = self.resize_image(processed_img, target_size, resize_mode)
                
                if filter_name != 'none':
                    processed_img = self.apply_filter(processed_img, filter_name)
                
                if watermark:
                    processed_img = self.add_watermark(processed_img, watermark) 
                
                processed_images.append(processed_img)
            
            bg_color = self.config.DEFAULT_BACKGROUND
            
            if layout == 'vertical':
                result = self.merge_vertical(processed_images, spacing, bg_color)
            elif layout == 'horizontal':
                result = self.merge_horizontal(processed_images, spacing, bg_color)
            elif layout == 'grid':
                result = self.merge_grid(processed_images, grid_cols, spacing, bg_color)
            else:
                result = self.merge_vertical(processed_images, spacing, bg_color)
            
            success, error = self.file_manager.safe_write(output_path, result)
            
            if success:
                logger.info(f"✓ Successfully saved merged image to: {output_path}")
                return True, None
            else:
                return False, error
            
        except Exception as e:
            error_msg = f"Error during image processing: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg