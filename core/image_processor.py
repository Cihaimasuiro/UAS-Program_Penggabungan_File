"""
Image Processor Module
Optimized for memory usage (stream processing) and detailed reporting.
"""

from PIL import Image, ImageFilter, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import logging
import math

from config import ImageConfig
from core.file_manager import FileManager

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self, config: Optional[ImageConfig] = None):
        self.config = config or ImageConfig()
        self.file_manager = FileManager()

    def _get_font(self, size: int):
        """Safely load a font with fallback strategy."""
        try:
            import sys
            if sys.platform == "win32":
                return ImageFont.truetype("arial.ttf", size)
            elif sys.platform == "darwin":
                return ImageFont.truetype("Helvetica.ttc", size)
            elif sys.platform == "linux":
                return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            pass
        return ImageFont.load_default()

    def process_and_merge(self, files: List[str], output_path: str,
                         layout: str = 'vertical',
                         spacing: int = 10,
                         resize_mode: str = 'none',
                         target_size: Optional[Tuple[int, int]] = None,
                         filter_name: str = 'none',
                         watermark: Optional[str] = None,
                         grid_cols: Optional[int] = None) -> Tuple[bool, str]:
        """
        Merges images with memory safety and returns detailed statistics.
        """
        try:
            if not files:
                return False, "No files provided"

            # --- PASS 1: Scan Dimensions ---
            dims = []
            valid_count = 0
            
            for f in files:
                try:
                    with Image.open(f) as img:
                        w, h = img.size
                        # If resizing, use the target size for calculation
                        if target_size and resize_mode != 'none':
                            # Simple prediction (actual resize logic might vary slightly)
                            w, h = target_size
                        dims.append((w, h))
                        valid_count += 1
                except Exception as e:
                    logger.warning(f"Skipping invalid image {f}: {e}")
                    dims.append(None)

            if valid_count == 0:
                return False, "All images failed to load."

            # --- Calculate Canvas Size ---
            valid_dims = [d for d in dims if d is not None]
            canvas_w, canvas_h = 0, 0
            
            if layout == 'vertical':
                canvas_w = max(d[0] for d in valid_dims)
                canvas_h = sum(d[1] for d in valid_dims) + spacing * (len(valid_dims) - 1)
            
            elif layout == 'horizontal':
                canvas_w = sum(d[0] for d in valid_dims) + spacing * (len(valid_dims) - 1)
                canvas_h = max(d[1] for d in valid_dims)
            
            elif layout == 'grid':
                if not grid_cols:
                    grid_cols = math.ceil(math.sqrt(len(valid_dims)))
                
                # Row-based calculation
                rows = []
                current_row_h = 0
                current_row_w = 0
                max_row_w = 0
                
                for i, (w, h) in enumerate(valid_dims):
                    if i % grid_cols == 0 and i > 0:
                        rows.append((current_row_w, current_row_h))
                        max_row_w = max(max_row_w, current_row_w)
                        current_row_h = 0
                        current_row_w = 0
                    
                    current_row_w += w + spacing
                    current_row_h = max(current_row_h, h)
                
                # Append last row
                rows.append((current_row_w, current_row_h))
                max_row_w = max(max_row_w, current_row_w)
                
                canvas_w = max_row_w - spacing
                canvas_h = sum(r[1] for r in rows) + spacing * (len(rows) - 1)

            # --- PASS 2: Process & Paste ---
            # Create canvas (RGB)
            bg_color = self.config.DEFAULT_BACKGROUND
            canvas = Image.new('RGB', (canvas_w, canvas_h), bg_color)
            
            x, y = 0, 0
            processed_count = 0
            
            # Grid helpers
            col_idx = 0
            row_max_h = 0

            for i, f in enumerate(files):
                if dims[i] is None: continue # Skip previously identified invalid files
                
                try:
                    with Image.open(f) as img:
                        # 1. Normalize Mode
                        if img.mode not in ('RGB', 'RGBA'):
                            img = img.convert('RGB')
                        
                        # 2. Resize
                        processed = img
                        if target_size and resize_mode != 'none':
                            processed = self.resize_image(img, target_size, resize_mode)
                        
                        # 3. Filter
                        if filter_name != 'none':
                            processed = self.apply_filter(processed, filter_name)
                        
                        # 4. Watermark
                        if watermark:
                            processed = self.add_watermark(processed, watermark)

                        # 5. Paste
                        if layout == 'vertical':
                            paste_x = (canvas_w - processed.width) // 2
                            canvas.paste(processed, (paste_x, y))
                            y += processed.height + spacing
                            
                        elif layout == 'horizontal':
                            paste_y = (canvas_h - processed.height) // 2
                            canvas.paste(processed, (x, paste_y))
                            x += processed.width + spacing
                            
                        elif layout == 'grid':
                            canvas.paste(processed, (x, y))
                            
                            x += processed.width + spacing
                            row_max_h = max(row_max_h, processed.height)
                            col_idx += 1
                            
                            if col_idx >= grid_cols:
                                col_idx = 0
                                x = 0
                                y += row_max_h + spacing
                                row_max_h = 0
                        
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed during processing of {f}: {e}")
                    continue

            # Save final result
            canvas.save(output_path, quality=self.config.DEFAULT_QUALITY)
            
            # Detailed Status Message
            if processed_count == len(files):
                return True, f"Successfully merged all {processed_count} images."
            else:
                return True, f"Merged {processed_count} images. ({len(files) - processed_count} skipped/failed)."

        except Exception as e:
            logger.error(f"Fatal image processing error: {e}", exc_info=True)
            return False, str(e)

    def resize_image(self, image: Image.Image, target_size: Tuple[int, int], mode: str) -> Image.Image:
        """Helper to resize a single image based on mode."""
        if mode == 'none': return image
        
        if mode == 'fit':
            img_copy = image.copy()
            img_copy.thumbnail(target_size, Image.Resampling.LANCZOS)
            return img_copy
            
        elif mode == 'stretch':
            return image.resize(target_size, Image.Resampling.LANCZOS)
            
        elif mode == 'fill':
            # Crop center to fill target box
            ratio_w = target_size[0] / image.width
            ratio_h = target_size[1] / image.height
            ratio = max(ratio_w, ratio_h)
            
            new_size = (int(image.width * ratio), int(image.height * ratio))
            img = image.resize(new_size, Image.Resampling.LANCZOS)
            
            left = (img.width - target_size[0]) // 2
            top = (img.height - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]
            
            return img.crop((left, top, right, bottom))
        
        return image

    def apply_filter(self, image: Image.Image, name: str) -> Image.Image:
        """Apply standard PIL filters."""
        if name == 'grayscale':
            return image.convert('L').convert('RGB')
        elif name == 'blur':
            return image.filter(ImageFilter.BLUR)
        elif name == 'sharpen':
            return image.filter(ImageFilter.SHARPEN)
        elif name == 'edge':
            return image.filter(ImageFilter.FIND_EDGES)
        elif name == 'sepia':
            # Simple Sepia Matrix
            width, height = image.size
            pixels = image.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = image.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
            return image
        return image

    def add_watermark(self, image: Image.Image, text: str) -> Image.Image:
        """Add text watermark to bottom-right."""
        # Create transparent layer
        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Dynamic font size (5% of image width)
        font_size = int(image.width * 0.05)
        font_size = max(12, min(font_size, 100)) # Clamp size
        font = self._get_font(font_size)
        
        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = 20
        x = image.width - text_width - margin
        y = image.height - text_height - margin
        
        # Draw semi-transparent text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))
        
        # Composite
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        result = Image.alpha_composite(image, txt_layer)
        return result.convert('RGB')