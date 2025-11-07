"""
Tkinter GUI for the 7 main menu features

This provides a lightweight GUI front-end that reuses the existing core
processors (FileManager, ImageProcessor, TextProcessor) and the CLI's
internal file list. It implements:

1. Add Files (open file dialog)
2. View Selected Files (popup with info)
3. Clear Selection
4. Process & Merge Files (auto-detect type and run with sensible defaults)
5. Batch Process Directory (pick folder and process matching files)
6. Settings (open settings.json in default editor)
7. Help (show help text)

This file intentionally keeps interactions simple — most options use
defaults from the SettingsManager when available.
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, StringVar, BooleanVar, IntVar, DoubleVar
from typing import List

# Import core components
from ui.cli import CLI
from core.settings_manager import get_settings_manager
from config import get_output_path, ImageConfig, TextConfig, OUTPUT_DIR
from core.file_manager import FileManager
from core.image_processor import ImageProcessor
from core.text_processor import TextProcessor
from ui.gui_settings import SettingsWindow  # <-- IMPORT BARU


class GUIApp:
    def __init__(self):
        self.settings_mgr = get_settings_manager()
        self.file_manager = FileManager()
        
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        
        # Internal state
        self.files = []

        self.root = tk.Tk()
        self.root.title("File Merger Pro - GUI")
        self.root.geometry("800x600")
        
        # Style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') 

        self._build_ui()

    def _build_ui(self):
        # Main layout with a resizable pane
        main_paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True)

        # Left control frame
        left = ttk.Frame(main_paned_window, padding=10, width=200)
        left.pack_propagate(False) # Prevent frame from shrinking
        
        btn_add = ttk.Button(left, text="Tambah File", width=25, command=self.add_files)
        btn_add.pack(pady=5, fill=tk.X)

        btn_clear = ttk.Button(left, text="Kosongkan Pilihan", width=25, command=self.clear_selection)
        btn_clear.pack(pady=5, fill=tk.X)

        btn_process = ttk.Button(left, text="Proses & Gabung File", width=25, command=self.process_files)
        btn_process.pack(pady=5, fill=tk.X)

        btn_batch = ttk.Button(left, text="Proses Batch Folder", width=25, command=self.batch_process)
        btn_batch.pack(pady=5, fill=tk.X)

        btn_settings = ttk.Button(left, text="Pengaturan", width=25, command=self.open_settings)
        btn_settings.pack(pady=5, fill=tk.X)

        btn_help = ttk.Button(left, text="Bantuan", width=25, command=self.show_help)
        btn_help.pack(pady=5, fill=tk.X)
        
        # --- Separator and New Buttons ---
        ttk.Separator(left, orient='horizontal').pack(pady=10, fill=tk.X)
        
        btn_open_output = ttk.Button(left, text="Buka Folder Output", width=25, command=self._open_output_folder)
        btn_open_output.pack(pady=5, fill=tk.X)

        btn_exit = ttk.Button(left, text="Keluar", width=25, command=self.root.destroy)
        btn_exit.pack(pady=5, fill=tk.X)
        
        main_paned_window.add(left, weight=0)

        # Right main frame with Notebook (Tabs)
        right = ttk.Frame(main_paned_window, padding=(10, 10, 10, 10))
        
        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: File List
        tab_files = ttk.Frame(notebook, padding=5)
        self._build_file_list_tab(tab_files)
        notebook.add(tab_files, text="File Terpilih")
        
        # Tab 2: Logs
        tab_logs = ttk.Frame(notebook, padding=5)
        self._build_log_tab(tab_logs)
        notebook.add(tab_logs, text="Status / Log")

        main_paned_window.add(right, weight=1)

    def _build_file_list_tab(self, parent):
        """Builds the content of the 'Selected Files' tab"""
        cols = ('name', 'size_mb', 'category')
        self.treeview = ttk.Treeview(parent, columns=cols, show='headings', height=15)
        
        self.treeview.heading('name', text='Nama File')
        self.treeview.heading('size_mb', text='Ukuran (MB)')
        self.treeview.heading('category', text='Tipe')
        
        self.treeview.column('name', width=350)
        self.treeview.column('size_mb', width=100, anchor=tk.E)
        self.treeview.column('category', width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(fill=tk.BOTH, expand=True)

    def _build_log_tab(self, parent):
        """Builds the content of the 'Logs' tab"""
        self.log = tk.Text(parent, height=10, state='disabled', wrap=tk.WORD, font=("Courier", 9))
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _log(self, msg: str):
        self.log.configure(state='normal')
        self.log.insert(tk.END, f"[{threading.current_thread().name}] {msg}\n")
        self.log.see(tk.END)
        self.log.configure(state='disabled')

    def _refresh_file_tree(self):
        # Clear existing items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Add new items
        for f in self.files:
            try:
                info = self.file_manager.get_file_info(f)
                self.treeview.insert('', tk.END, values=(info['name'], f"{info['size_mb']:.2f}", info['category']))
            except Exception as e:
                 self.treeview.insert('', tk.END, values=(os.path.basename(f), "N/A", "Error"))
                 self._log(f"✗ Error mendapatkan info file {f}: {e}")

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Pilih file untuk ditambah")
        if not paths:
            return

        added = 0
        for p in paths:
            is_valid, err = self.file_manager.validate_file(p)
            if is_valid and p not in self.files:
                self.files.append(p)
                added += 1
            elif not is_valid:
                self._log(f"✗ Tidak valid: {p} - {err}")
            elif p in self.files:
                 self._log(f"⚠ Sudah ada: {p}")

        self._log(f"✓ {added} file baru ditambah. Total: {len(self.files)}")
        self._refresh_file_tree()

    def clear_selection(self):
        if not self.files:
            self._log("⚠ Tidak ada file untuk dibersihkan")
            return

        if messagebox.askyesno("Kosongkan Pilihan", f"Bersihkan {len(self.files)} file terpilih?"):
            self.files.clear()
            self._refresh_file_tree()
            self._log("✓ Pilihan dibersihkan")

    def process_files(self):
        if not self.files:
            messagebox.showwarning("Tidak ada file", "Silakan tambahkan file sebelum memproses")
            return

        is_consistent, category = self.file_manager.check_file_types_consistency(self.files)

        if not is_consistent:
            self._log("⚠ Tipe file campuran. Proses dibatalkan.")
            messagebox.showerror("Tipe Campuran", "File yang dipilih memiliki tipe berbeda. Pastikan semua file sejenis.")
            return
            
        # Terapkan settings
        try:
            self.settings_mgr.apply_to_config()
            self.image_processor = ImageProcessor()
            self.text_processor = TextProcessor()
        except Exception as e:
            self._log(f"Error menerapkan settings: {e}")

        # Tanya mode: Gabung atau Kumpulkan
        mode_choice = self._ask_merge_or_collect()
        
        if mode_choice == 'collect':
            self._collect_files(category)
        elif mode_choice == 'merge':
            if category == 'image':
                self.show_image_options()
            elif category == 'text':
                self.show_text_options()
            else:
                self._log(f"⚠ Kategori tidak didukung untuk digabung: {category}")
                messagebox.showwarning("Tidak Didukung", f"Kategori tidak didukung: {category}")

    def _collect_files(self, category: str):
        dest_dir = filedialog.askdirectory(title="Pilih folder tujuan (Batal untuk default)")
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_folder = str(get_output_path(f'collected_{category}_{timestamp}'))
        out_folder = dest_dir if dest_dir else default_folder

        move_flag = messagebox.askyesno("Salin atau Pindah?", "Pindahkan file (move)?\nYa = Pindah (hapus asli)\nTidak = Salin (simpan asli)")

        self._log(f"⏳ Mengumpulkan {len(self.files)} file ke {out_folder} (Pindah: {move_flag})...")
        
        thread = threading.Thread(
            target=self._process_files_background,
            args=('collect', {'files': self.files, 'out_folder': out_folder, 'move_flag': move_flag}),
            daemon=True,
            name="CollectThread"
        )
        thread.start()

    def show_image_options(self):
        """Menampilkan Toplevel window dengan opsi penggabungan gambar."""
        s = self.settings_mgr.settings
        
        win = Toplevel(self.root)
        win.title("Opsi Gabung Gambar")
        win.transient(self.root)
        win.grab_set()
        
        # Variabel
        layout_var = StringVar(value=s.image_default_layout)
        spacing_var = IntVar(value=s.image_default_spacing)
        grid_cols_var = IntVar(value=3)
        
        resize_var = StringVar(value=s.image_default_resize_mode)
        width_var = IntVar(value=1920)
        height_var = IntVar(value=1080)
        
        filter_var = StringVar(value=s.image_default_filter)
        
        watermark_var = BooleanVar(value=s.image_add_watermark)
        watermark_text_var = StringVar(value=s.image_watermark_text)
        
        # --- Layout ---
        lf_layout = ttk.LabelFrame(win, text="Tata Letak", padding=10)
        lf_layout.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        ttk.Label(lf_layout, text="Tata Letak:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        layout_opts = [ImageConfig.LAYOUT_VERTICAL, ImageConfig.LAYOUT_HORIZONTAL, ImageConfig.LAYOUT_GRID]
        ttk.Combobox(lf_layout, textvariable=layout_var, values=layout_opts, state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(lf_layout, text="Jarak (px):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Spinbox(lf_layout, from_=0, to=500, textvariable=spacing_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(lf_layout, text="Kolom Grid (jika grid):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Spinbox(lf_layout, from_=1, to=20, textvariable=grid_cols_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # --- Resize ---
        lf_resize = ttk.LabelFrame(win, text="Ubah Ukuran", padding=10)
        lf_resize.pack(fill=tk.X, expand=True, padx=10, pady=5)
        
        ttk.Label(lf_resize, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        resize_opts = list(ImageConfig.RESIZE_MODES.keys())
        ttk.Combobox(lf_resize, textvariable=resize_var, values=resize_opts, state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(lf_resize, text="Lebar (px):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Spinbox(lf_resize, from_=0, to=10000, textvariable=width_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(lf_resize, text="Tinggi (px):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Spinbox(lf_resize, from_=0, to=10000, textvariable=height_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Filter & Watermark ---
        lf_extra = ttk.LabelFrame(win, text="Tambahan", padding=10)
        lf_extra.pack(fill=tk.X, expand=True, padx=10, pady=5)

        ttk.Label(lf_extra, text="Filter:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        filter_opts = list(ImageConfig.FILTERS.keys())
        ttk.Combobox(lf_extra, textvariable=filter_var, values=filter_opts, state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Checkbutton(lf_extra, text="Tambah Watermark", variable=watermark_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(lf_extra, textvariable=watermark_text_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Tombol Proses ---
        def on_process():
            target_size = None
            if resize_var.get() != 'none':
                target_size = (width_var.get(), height_var.get())
                
            watermark = watermark_text_var.get() if watermark_var.get() else None
            
            options = {
                'layout': layout_var.get(),
                'spacing': spacing_var.get(),
                'grid_cols': grid_cols_var.get(),
                'resize_mode': resize_var.get(),
                'target_size': target_size,
                'filter_name': filter_var.get(),
                'watermark': watermark,
            }
            win.destroy()
            
            output_name = "merged_images.png"
            output_path = str(get_output_path(output_name))
            
            options['files'] = self.files
            options['output_path'] = output_path
            
            self._log(f"⏳ Memulai penggabungan gambar dengan opsi: {options}")
            thread = threading.Thread(target=self._process_files_background, args=('image', options), daemon=True, name="ImageProcessThread")
            thread.start()

        ttk.Button(win, text="Proses Gambar", command=on_process).pack(pady=10)
        
    def show_text_options(self):
        """Menampilkan Toplevel window dengan opsi penggabungan teks."""
        s = self.settings_mgr.settings

        win = Toplevel(self.root)
        win.title("Opsi Gabung Teks")
        win.transient(self.root)
        win.grab_set()

        # Variabel
        separator_var = StringVar(value=s.text_default_separator)
        line_numbers_var = BooleanVar(value=s.text_add_line_numbers)
        timestamps_var = BooleanVar(value=s.text_add_timestamps)
        strip_ws_var = BooleanVar(value=s.text_strip_whitespace)
        markdown_var = BooleanVar(value=s.text_markdown_export)

        # --- Opsi ---
        lf_options = ttk.LabelFrame(win, text="Format", padding=10)
        lf_options.pack(fill=tk.X, expand=True, padx=10, pady=5)

        ttk.Label(lf_options, text="Gaya Pemisah:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        sep_opts = list(TextConfig.SEPARATOR_STYLES.keys())
        ttk.Combobox(lf_options, textvariable=separator_var, values=sep_opts, state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Checkbutton(lf_options, text="Tambah Nomor Baris", variable=line_numbers_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(lf_options, text="Tambah Stempel Waktu", variable=timestamps_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(lf_options, text="Hapus Spasi Berlebih", variable=strip_ws_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Checkbutton(lf_options, text="Ekspor ke Markdown", variable=markdown_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        # --- Tombol Proses ---
        def on_process():
            options = {
                'separator_style': separator_var.get(),
                'add_line_numbers': line_numbers_var.get(),
                'add_timestamps': timestamps_var.get(),
                'strip_whitespace': strip_ws_var.get(),
                'as_markdown': markdown_var.get()
            }
            win.destroy()
            
            output_name = "merged.md" if options['as_markdown'] else "merged.txt"
            output_path = str(get_output_path(output_name))
            
            options['files'] = self.files
            options['output_path'] = output_path

            self._log(f"⏳ Memulai pemrosesan teks dengan opsi: {options}")
            thread = threading.Thread(target=self._process_files_background, args=('text', options), daemon=True, name="TextProcessThread")
            thread.start()

        ttk.Button(win, text="Proses Teks", command=on_process).pack(pady=10)

    def _process_files_background(self, category: str, options: dict):
        """
        Menjalankan proses di background thread.
        'category' bisa 'image', 'text', or 'collect'.
        'options' adalah dict parameter.
        """
        try:
            if category == 'collect':
                success, error = self.file_manager.copy_files_to_folder(
                    options['files'], options['out_folder'], move=options['move_flag']
                )
                if success:
                    verb = 'dipindah' if options['move_flag'] else 'disalin'
                    self._log(f"✅ File {verb} ke folder: {options['out_folder']}")
                    if messagebox.askyesno("Sukses", f"File berhasil {verb} ke folder:\n{options['out_folder']}\n\nBuka folder output?"):
                        self._open_output_folder()
                else:
                    self._log(f"❌ Error saat menyalin/memindah file: {error}")
                    messagebox.showerror("Error", str(error))
                return

            if category == 'image':
                success, error = self.image_processor.process_and_merge(
                    options['files'],
                    options['output_path'],
                    layout=options['layout'],
                    resize_mode=options['resize_mode'],
                    target_size=options['target_size'],
                    filter_name=options['filter_name'],
                    watermark=options['watermark'],
                    spacing=options['spacing'],
                    grid_cols=options['grid_cols']
                )

                if success:
                    self._log(f"✅ Gambar digabung: {options['output_path']}")
                    if messagebox.askyesno("Sukses", f"Gambar berhasil digabung:\n{options['output_path']}\n\nBuka folder output?"):
                        self._open_output_folder()
                else:
                    self._log(f"❌ Error: {error}")
                    messagebox.showerror("Error", str(error))

            elif category == 'text':
                if options['as_markdown']:
                    success, error = self.text_processor.convert_to_markdown(
                        options['files'],
                        options['output_path']
                    )
                else:
                    success, error = self.text_processor.merge_text_files(
                        options['files'],
                        options['output_path'],
                        separator_style=options['separator_style'],
                        add_line_numbers=options['add_line_numbers'],
                        add_timestamps=options['add_timestamps'],
                        strip_whitespace=options['strip_whitespace']
                    )

                if success:
                    self._log(f"✅ Teks diproses: {options['output_path']}")
                    if messagebox.askyesno("Sukses", f"Teks berhasil diproses:\n{options['output_path']}\n\nBuka folder output?"):
                        self._open_output_folder()
                else:
                    self._log(f"❌ Error: {error}")
                    messagebox.showerror("Error", str(error))
        except Exception as e:
            self._log(f"❌ Terjadi error fatal: {e}")
            messagebox.showerror("Error Fatal", f"Terjadi error fatal saat pemrosesan:\n{e}")

    def batch_process(self):
        directory = filedialog.askdirectory(title="Pilih folder untuk diproses batch")
        if not directory:
            return

        # Tanya user mau proses gambar atau teks
        choice = messagebox.askquestion("Tipe Batch", "Proses gambar di folder ini? (Klik 'Tidak' untuk file teks)")
        
        path = os.path.abspath(directory)
        files_found = []

        if choice == 'yes':
            exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}
            category = 'gambar'
        else:
            exts = {'.txt', '.md', '.log', '.csv', '.json', '.xml', '.py'}
            category = 'teks'

        for entry in os.scandir(path):
            if entry.is_file() and os.path.splitext(entry.name)[1].lower() in exts:
                files_found.append(entry.path)

        if not files_found:
            messagebox.showinfo("Tidak ada file", "Tidak ada file yang cocok di folder terpilih.")
            return

        self.files = files_found
        self._refresh_file_tree()
        self._log(f"✓ Ditemukan {len(files_found)} file {category} di {directory}")
        
        if messagebox.askyesno("Konfirmasi Batch", f"Ditemukan {len(files_found)} file {category}. Proses sekarang?"):
            self.process_files()

    def open_settings(self):
        """
        Membuka menu settings GUI (Tkinter) baru.
        Menggantikan TUI yang lama.
        """
        self._log("Membuka pengaturan...")
        try:
            # Membuat instance dari jendela pengaturan baru
            settings_win = SettingsWindow(self.root, self.settings_mgr)
            # Jendela ini modal (grab_set), jadi GUI utama akan menunggu.
            # Saat ditutup, settings_mgr akan diperbarui jika user klik 'Simpan'
        except Exception as e:
            self._log(f"❌ Gagal membuka GUI settings: {e}")
            messagebox.showerror("Error", f"Gagal membuka GUI settings: {e}\n{e.__traceback__}")


    def _open_output_folder(self):
        """Membuka folder output di file explorer default."""
        output_dir_path = str(OUTPUT_DIR)
        self._log(f"Membuka folder output: {output_dir_path}")
        try:
            if sys.platform == 'win32':
                os.startfile(output_dir_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', output_dir_path])
            else: # 'linux' atau UNIX lain
                subprocess.Popen(['xdg-open', output_dir_path])
        except Exception as e:
            self._log(f"Gagal membuka folder output: {e}")
            messagebox.showerror("Error", f"Tidak dapat membuka folder output:\n{e}")

    def show_help(self):
        message = (
            "File Merger Pro - Bantuan\n\n"
            "1. Tambah File: Pilih file gambar atau teks untuk diproses.\n"
            "2. Kosongkan Pilihan: Mengosongkan daftar file.\n"
            "3. Proses & Gabung: \n"
            "   - Pilih 'Gabung' (kombinasi) atau 'Kumpulkan' (salin ke folder).\n"
            "   - Jika 'Gabung', window baru akan muncul untuk memilih opsi.\n"
            "4. Proses Batch: Pilih folder untuk memproses semua file sejenis.\n"
            "5. Pengaturan: Membuka menu pengaturan (TUI) di terminal baru.\n"
            "6. Buka Folder Output: Membuka folder 'output' di file explorer.\n"
            "7. Keluar: Menutup aplikasi.\n\n"
            "• File hasil disimpan di folder 'output' (bisa diubah di Pengaturan)."
        )
        messagebox.showinfo("Bantuan", message)

    def run(self):
        self.root.mainloop()

    def _ask_merge_or_collect(self) -> str:
        """Menampilkan dialog modal untuk memilih 'Gabung' atau 'Kumpulkan'.
        Mengembalikan 'merge' atau 'collect'.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Pilih aksi")
        dialog.geometry("380x130")
        dialog.transient(self.root)
        dialog.grab_set()

        label = ttk.Label(dialog, text="Apa yang ingin Anda lakukan dengan file terpilih?", justify=tk.CENTER)
        label.pack(pady=15)

        choice = {'value': 'merge'} # Default jika window ditutup

        def on_merge():
            choice['value'] = 'merge'
            dialog.destroy()

        def on_collect():
            choice['value'] = 'collect'
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=8)

        btn_merge = ttk.Button(btn_frame, text="Gabung jadi satu file", command=on_merge)
        btn_merge.pack(side=tk.LEFT, padx=10)

        btn_collect = ttk.Button(btn_frame, text="Kumpulkan ke folder", command=on_collect)
        btn_collect.pack(side=tk.LEFT, padx=10)
        
        dialog.protocol("WM_DELETE_WINDOW", on_merge) # Default ke 'merge'
        self.root.wait_window(dialog)
        return choice['value']


def run_gui():
    app = GUIApp()
    app.run()


if __name__ == '__main__':
    run_gui()