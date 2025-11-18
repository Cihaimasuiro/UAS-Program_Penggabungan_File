"""
Universal Processor Module
Handles merging of Images, Text, Office, and Binary files into a single PDF.
"""

import os
import io
import logging
from pathlib import Path
from typing import List, Tuple, Optional

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from pypdf import PdfWriter, PdfReader

# Optional: Excel Support
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Corrected Import
from config import get_file_category, PdfConfig
from core.file_manager import FileManager

logger = logging.getLogger(__name__)

class UniversalProcessor:
    def __init__(self):
        self.file_manager = FileManager()
        # Cache common page size
        self.page_width, self.page_height = A4

    def merge_all_to_pdf(self, filepaths: List[str], output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Universal Merging Strategy:
        - PDF: Append pages directly.
        - Image: Draw image onto a new PDF page.
        - Text/Web/Code: Read text and render nicely onto PDF page.
        - Office (Excel): Parse data and render as text/table on PDF page.
        - Binary/Archive: Generate a "File Info" placeholder card page.
        """
        try:
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
                        # Fallback
                        self._binary_to_pdf_pages(writer, fpath)
                    
                    success_count += 1
                except Exception as item_error:
                    logger.error(f"Failed to process item {fpath}: {item_error}")
                    self._create_error_page(writer, fpath, str(item_error))

            # Write final output
            with open(output_path, "wb") as out_f:
                writer.write(out_f)
            
            return True, f"Merged {success_count} files into PDF."

        except Exception as e:
            logger.error(f"Universal merge failed: {e}", exc_info=True)
            return False, str(e)

    def _append_pdf(self, writer: PdfWriter, filepath: str):
        """Append pages from an existing PDF."""
        reader = PdfReader(filepath)
        for page in reader.pages:
            writer.add_page(page)

    def _image_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        """Draw an image onto a PDF page matching its dimensions."""
        packet = io.BytesIO()
        img = ImageReader(filepath)
        iw, ih = img.getSize()
        
        c = canvas.Canvas(packet, pagesize=(iw, ih))
        c.drawImage(img, 0, 0, width=iw, height=ih)
        c.showPage()
        c.save()
        
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])

    def _text_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        """Render text file content (code, html, txt) onto pages."""
        content, _ = self.file_manager.read_file_safe(filepath)
        if not content: return

        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        margin = PdfConfig.MARGIN
        width, height = A4
        
        # Header
        c.setFont(PdfConfig.FONT_HEADER, PdfConfig.FONT_SIZE_HEADER)
        c.drawString(margin, height - margin, f"File: {Path(filepath).name}")
        c.setLineWidth(1)
        c.line(margin, height - margin - 5, width - margin, height - margin - 5)
        
        # Content
        y_pos = height - margin - 20
        text_obj = c.beginText(margin, y_pos)
        text_obj.setFont(PdfConfig.FONT_BODY, PdfConfig.FONT_SIZE_BODY)
        
        lines = content.split('\n')
        max_lines = 55 # Approx lines per page
        current_line_count = 0
        
        for line in lines:
            safe_line = line.replace('\r', '').replace('\t', '    ')
            chars_per_line = 90
            chunks = [safe_line[i:i+chars_per_line] for i in range(0, len(safe_line), chars_per_line)] or [""]
            
            for chunk in chunks:
                text_obj.textLine(chunk)
                current_line_count += 1
            
            if current_line_count >= max_lines:
                c.drawText(text_obj)
                c.showPage()
                
                # New Page Header
                c.setFont(PdfConfig.FONT_HEADER, PdfConfig.FONT_SIZE_HEADER)
                c.drawString(margin, height - margin, f"File: {Path(filepath).name} (Cont.)")
                c.line(margin, height - margin - 5, width - margin, height - margin - 5)
                
                text_obj = c.beginText(margin, height - margin - 20)
                text_obj.setFont(PdfConfig.FONT_BODY, PdfConfig.FONT_SIZE_BODY)
                current_line_count = 0
        
        c.drawText(text_obj)
        c.showPage()
        c.save()
        
        packet.seek(0)
        for page in PdfReader(packet).pages:
            writer.add_page(page)

    def _office_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        """Render Excel data as text tables."""
        if not HAS_OPENPYXL and filepath.endswith(('.xlsx', '.xls')):
            self._create_error_page(writer, filepath, "Missing library: openpyxl")
            return

        if filepath.endswith(('.xlsx', '.xls')):
            try:
                wb = openpyxl.load_workbook(filepath, data_only=True)
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=A4)
                margin = PdfConfig.MARGIN
                height = A4[1]
                y = height - margin
                
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    c.setFont(PdfConfig.FONT_HEADER, 14)
                    c.drawString(margin, y, f"Sheet: {sheet} ({Path(filepath).name})")
                    y -= 25
                    c.setFont("Helvetica", 8)
                    
                    for row in ws.iter_rows(values_only=True):
                        row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                        if len(row_text) > 110: 
                            row_text = row_text[:107] + "..."
                            
                        c.drawString(margin, y, row_text)
                        y -= 12
                        
                        if y < margin:
                            c.showPage()
                            y = height - margin
                            c.setFont("Helvetica", 8)
                    
                    y -= 20
                    if y < 60:
                        c.showPage()
                        y = height - margin

                c.save()
                packet.seek(0)
                for page in PdfReader(packet).pages:
                    writer.add_page(page)
            except Exception as e:
                self._create_error_page(writer, filepath, f"Excel error: {e}")
        else:
            self._binary_to_pdf_pages(writer, filepath)

    def _binary_to_pdf_pages(self, writer: PdfWriter, filepath: str):
        """Create placeholder card for binaries."""
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        w, h = A4
        
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(50, h - 300, w - 100, 200, fill=1)
        c.setFillColorRGB(0, 0, 0)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(70, h - 140, "FILE ATTACHMENT / BINARY")
        
        c.setFont("Helvetica", 12)
        c.drawString(70, h - 180, f"Filename: {Path(filepath).name}")
        
        try:
            size = os.path.getsize(filepath)
            sz_str = f"{size/(1024*1024):.2f} MB" if size > 1024*1024 else f"{size/1024:.2f} KB"
        except: sz_str = "Unknown"
            
        c.drawString(70, h - 200, f"Size: {sz_str}")
        
        c.showPage()
        c.save()
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])

    def _create_error_page(self, writer: PdfWriter, filepath: str, error: str):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)
        w, h = A4
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0.8, 0, 0)
        c.drawString(50, h/2 + 20, f"ERROR: {Path(filepath).name}")
        
        c.setFont("Courier", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(50, h/2, f"{error}")
        
        c.showPage()
        c.save()
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])