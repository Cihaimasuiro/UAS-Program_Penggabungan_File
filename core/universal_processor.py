"""
Universal Processor Module
Handles merging of Images, Text, Office, and Binary files into a single PDF.
Respects user configuration for Layout/Fonts.
"""

import os
import io
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfWriter, PdfReader

# Optional: Excel Support
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

from config import get_file_category, PdfConfig
from core.file_manager import FileManager

logger = logging.getLogger(__name__)

class UniversalProcessor:
    def __init__(self):
        self.file_manager = FileManager()
        self._update_config()

    def _update_config(self):
        """Fetch current page size and settings."""
        self.page_size = PdfConfig.PAGE_SIZES.get(PdfConfig.DEFAULT_PAGE_SIZE, PdfConfig.PAGE_SIZES['A4'])
        self.font_name = PdfConfig.DEFAULT_FONT
        self.font_size = PdfConfig.DEFAULT_FONT_SIZE
        self.show_numbers = PdfConfig.SHOW_PAGE_NUMBERS

    def merge_all_to_pdf(self, filepaths: List[str], output_path: str) -> Tuple[bool, Optional[str]]:
        try:
            self._update_config() # Ensure latest config is used
            writer = PdfWriter()
            success_count = 0
            
            for fpath in filepaths:
                category = get_file_category(fpath)
                logger.info(f"Processing {Path(fpath).name} as {category}")

                try:
                    if category == 'document' and fpath.lower().endswith('.pdf'):
                        self._append_pdf(writer, fpath)
                    elif category == 'image':
                        self._image_to_pdf_pages(writer, fpath)
                    elif category == 'text':
                        self._text_to_pdf_pages(writer, fpath)
                    elif category == 'office':
                        self._office_to_pdf_pages(writer, fpath)
                    elif category == 'binary':
                        self._binary_to_pdf_pages(writer, fpath)
                    else:
                        self._binary_to_pdf_pages(writer, fpath)
                    
                    success_count += 1
                except Exception as item_error:
                    logger.error(f"Failed to process item {fpath}: {item_error}")
                    self._create_error_page(writer, fpath, str(item_error))

            with open(output_path, "wb") as out_f:
                writer.write(out_f)
            
            return True, f"Merged {success_count} files into PDF."

        except Exception as e:
            logger.error(f"Universal merge failed: {e}", exc_info=True)
            return False, str(e)

    def _append_pdf(self, writer: PdfWriter, filepath: str):
        reader = PdfReader(filepath)
        for page in reader.pages:
            writer.add_page(page)

    def _image_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        packet = io.BytesIO()
        img = ImageReader(filepath)
        iw, ih = img.getSize()
        
        # Use image size directly for best quality
        c = canvas.Canvas(packet, pagesize=(iw, ih))
        c.drawImage(img, 0, 0, width=iw, height=ih)
        c.showPage()
        c.save()
        
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])

    def _text_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        content, _ = self.file_manager.read_file_safe(filepath)
        if not content: return

        packet = io.BytesIO()
        w, h = self.page_size
        c = canvas.Canvas(packet, pagesize=self.page_size)
        
        # Header
        c.setFont(f"{self.font_name}-Bold", self.font_size + 2)
        c.drawString(40, h - 40, f"File: {Path(filepath).name}")
        c.setLineWidth(1)
        c.line(40, h - 45, w - 40, h - 45)
        
        # Content
        text_obj = c.beginText(40, h - 65)
        text_obj.setFont("Courier", self.font_size)
        
        lines = content.split('\n')
        current_line = 0
        max_lines = int((h - 100) / (self.font_size * 1.2)) # Dynamic line calc
        
        for line in lines:
            safe_line = line.replace('\r', '').replace('\t', '    ')
            chars_per_line = int((w - 80) / (self.font_size * 0.6))
            chunks = [safe_line[i:i+chars_per_line] for i in range(0, len(safe_line), chars_per_line)] or [""]
            
            for chunk in chunks:
                text_obj.textLine(chunk)
                current_line += 1
            
            if current_line >= max_lines:
                c.drawText(text_obj)
                if self.show_numbers: 
                    c.setFont(self.font_name, 8)
                    c.drawString(w-40, 20, "Page Cont.")
                c.showPage()
                
                # Reset
                c.setFont(f"{self.font_name}-Bold", self.font_size + 2)
                c.drawString(40, h - 40, f"File: {Path(filepath).name} (Cont.)")
                c.line(40, h - 45, w - 40, h - 45)
                
                text_obj = c.beginText(40, h - 65)
                text_obj.setFont("Courier", self.font_size)
                current_line = 0
        
        c.drawText(text_obj)
        c.showPage()
        c.save()
        
        packet.seek(0)
        for page in PdfReader(packet).pages:
            writer.add_page(page)

    def _office_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        if not HAS_OPENPYXL and filepath.endswith(('.xlsx', '.xls')):
            self._create_error_page(writer, filepath, "Missing library: openpyxl")
            return

        if filepath.endswith(('.xlsx', '.xls')):
            try:
                wb = openpyxl.load_workbook(filepath, data_only=True)
                packet = io.BytesIO()
                w, h = self.page_size
                c = canvas.Canvas(packet, pagesize=self.page_size)
                y = h - 40
                
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    c.setFont(f"{self.font_name}-Bold", self.font_size + 4)
                    c.drawString(40, y, f"Sheet: {sheet} ({Path(filepath).name})")
                    y -= 25
                    c.setFont(self.font_name, self.font_size - 2)
                    
                    for row in ws.iter_rows(values_only=True):
                        row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                        # Truncate based on page width
                        limit = int((w - 80) / 5)
                        if len(row_text) > limit: row_text = row_text[:limit-3] + "..."
                        
                        c.drawString(40, y, row_text)
                        y -= 12
                        
                        if y < 40:
                            c.showPage()
                            y = h - 40
                            c.setFont(self.font_name, self.font_size - 2)
                    
                    c.showPage()
                    y = h - 40

                c.save()
                packet.seek(0)
                for page in PdfReader(packet).pages:
                    writer.add_page(page)
            except Exception as e:
                self._create_error_page(writer, filepath, f"Excel error: {e}")
        else:
            self._binary_to_pdf_pages(writer, filepath)

    def _binary_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        packet = io.BytesIO()
        w, h = self.page_size
        c = canvas.Canvas(packet, pagesize=self.page_size)
        
        c.setStrokeColorRGB(0.3, 0.3, 0.3)
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(50, h - 300, w - 100, 200, fill=1)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont(f"{self.font_name}-Bold", 16)
        c.drawString(70, h - 140, "FILE ATTACHMENT")
        
        c.setFont(self.font_name, 12)
        c.drawString(70, h - 180, f"Filename: {Path(filepath).name}")
        
        ext = Path(filepath).suffix.upper()
        c.drawString(70, h - 220, f"Type: {ext}")
        
        c.setFont(f"{self.font_name}-Oblique", 10)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(70, h - 260, "This file cannot be visually rendered.")
        
        c.showPage()
        c.save()
        
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])

    def _create_error_page(self, writer: PdfWriter, filepath: str, error: str):
        packet = io.BytesIO()
        w, h = self.page_size
        c = canvas.Canvas(packet, pagesize=self.page_size)
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0.8, 0, 0)
        c.drawString(50, h/2 + 20, f"ERROR PROCESSING: {Path(filepath).name}")
        
        c.setFont("Courier", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(50, h/2, f"Details: {error}")
        
        c.showPage()
        c.save()
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])