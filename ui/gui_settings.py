"""
Modul Pengaturan GUI Native (Tkinter)
Berisi kelas SettingsWindow yang menyediakan antarmuka
full Tkinter untuk mengedit pengaturan dari SettingsManager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, StringVar, BooleanVar, IntVar
from core.settings_manager import SettingsManager, UserSettings
from config import ImageConfig, TextConfig

class SettingsWindow(tk.Toplevel):
    """Jendela Toplevel modal untuk mengedit pengaturan."""
    
    def __init__(self, parent, manager: SettingsManager):
        super().__init__(parent)
        self.manager = manager
        self.original_settings = self.manager.load_settings() # Salinan untuk "Batal"
        
        # Variabel untuk menampung semua setting
        self.vars = {}

        self.title("Pengaturan")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self._create_variables()
        self._load_settings_to_vars()
        self._build_ui()

    def _create_variables(self):
        """Buat instance Tkinter Variable untuk setiap pengaturan."""
        # Menggunakan UserSettings.__annotations__ untuk introspeksi
        for setting_name, setting_type in UserSettings.__annotations__.items():
            if setting_type == str:
                self.vars[setting_name] = StringVar()
            elif setting_type == int:
                self.vars[setting_name] = IntVar()
            elif setting_type == bool:
                self.vars[setting_name] = BooleanVar()
        
        # Pastikan kita tidak melewatkan apapun (jika anotasi tidak lengkap)
        for setting_name in self.original_settings.__dict__:
            if setting_name not in self.vars:
                value = getattr(self.original_settings, setting_name)
                if isinstance(value, str):
                    self.vars[setting_name] = StringVar()
                elif isinstance(value, int):
                    self.vars[setting_name] = IntVar()
                elif isinstance(value, bool):
                    self.vars[setting_name] = BooleanVar()

    def _load_settings_to_vars(self):
        """Muat nilai dari manajer ke dalam variabel Tkinter."""
        for key, var in self.vars.items():
            if hasattr(self.original_settings, key):
                var.set(getattr(self.original_settings, key))

    def _build_ui(self):
        """Bangun antarmuka pengguna dengan Notebook/Tabs."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Membuat tab
        tab_image = ttk.Frame(notebook, padding=10)
        tab_text = ttk.Frame(notebook, padding=10)
        tab_output = ttk.Frame(notebook, padding=10)
        tab_advanced = ttk.Frame(notebook, padding=10)
        
        notebook.add(tab_image, text='Gambar')
        notebook.add(tab_text, text='Teks')
        notebook.add(tab_output, text='Output')
        notebook.add(tab_advanced, text='Lanjutan')

        # Isi setiap tab
        self._build_image_tab(tab_image)
        self._build_text_tab(tab_text)
        self._build_output_tab(tab_output)
        self._build_advanced_tab(tab_advanced)

        # Tombol Aksi
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        ttk.Button(btn_frame, text="Simpan & Tutup", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Terapkan", command=self._on_apply).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self._on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Reset", command=self._on_reset).pack(side=tk.LEFT, padx=5)

    def _build_image_tab(self, parent):
        """Isi tab pengaturan Gambar."""
        lf_layout = ttk.LabelFrame(parent, text="Tata Letak", padding=10)
        lf_layout.pack(fill=tk.X, pady=5)
        
        ttk.Label(lf_layout, text="Layout Default:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_layout, textvariable=self.vars['image_default_layout'], 
                     values=[ImageConfig.LAYOUT_VERTICAL, ImageConfig.LAYOUT_HORIZONTAL, ImageConfig.LAYOUT_GRID],
                     state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(lf_layout, text="Jarak Default (px):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(lf_layout, from_=0, to=500, textvariable=self.vars['image_default_spacing']).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        lf_quality = ttk.LabelFrame(parent, text="Kualitas & Filter", padding=10)
        lf_quality.pack(fill=tk.X, pady=5)

        ttk.Label(lf_quality, text="Kualitas JPEG (1-100):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(lf_quality, from_=1, to=100, textvariable=self.vars['image_default_quality']).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(lf_quality, text="Mode Resize Default:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_quality, textvariable=self.vars['image_default_resize_mode'],
                     values=list(ImageConfig.RESIZE_MODES.keys()),
                     state='readonly').grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(lf_quality, text="Filter Default:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_quality, textvariable=self.vars['image_default_filter'],
                     values=list(ImageConfig.FILTERS.keys()),
                     state='readonly').grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        lf_watermark = ttk.LabelFrame(parent, text="Watermark", padding=10)
        lf_watermark.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(lf_watermark, text="Tambah Watermark Default", 
                        variable=self.vars['image_add_watermark']).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        ttk.Label(lf_watermark, text="Teks Watermark:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(lf_watermark, textvariable=self.vars['image_watermark_text']).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

    def _build_text_tab(self, parent):
        """Isi tab pengaturan Teks."""
        lf_format = ttk.LabelFrame(parent, text="Format Teks", padding=10)
        lf_format.pack(fill=tk.X, pady=5)

        ttk.Label(lf_format, text="Gaya Pemisah Default:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_format, textvariable=self.vars['text_default_separator'],
                     values=list(TextConfig.SEPARATOR_STYLES.keys()),
                     state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(lf_format, text="Encoding Default:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_format, textvariable=self.vars['text_default_encoding'],
                     values=['utf-8', 'latin-1', 'ascii', 'cp1252']).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        lf_options = ttk.LabelFrame(parent, text="Opsi Tambahan", padding=10)
        lf_options.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(lf_options, text="Tambah Nomor Baris", 
                        variable=self.vars['text_add_line_numbers']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(lf_options, text="Tambah Stempel Waktu", 
                        variable=self.vars['text_add_timestamps']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(lf_options, text="Hapus Spasi Berlebih", 
                        variable=self.vars['text_strip_whitespace']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(lf_options, text="Ekspor ke Markdown", 
                        variable=self.vars['text_markdown_export']).pack(anchor=tk.W, padx=5)

    def _build_output_tab(self, parent):
        """Isi tab pengaturan Output."""
        lf_general = ttk.LabelFrame(parent, text="Opsi Output", padding=10)
        lf_general.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(lf_general, text="Gunakan Stempel Waktu di Nama File", 
                        variable=self.vars['output_use_timestamp']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(lf_general, text="Timpa File Otomatis (Overwrite)", 
                        variable=self.vars['output_auto_overwrite']).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(lf_general, text="Buat Backup Saat Overwrite", 
                        variable=self.vars['output_create_backup']).pack(anchor=tk.W, padx=5)

        lf_dir = ttk.LabelFrame(parent, text="Folder Output", padding=10)
        lf_dir.pack(fill=tk.X, pady=5)

        ttk.Label(lf_dir, text="Folder Output Default:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        dir_frame = ttk.Frame(lf_dir)
        dir_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(dir_frame, textvariable=self.vars['output_default_directory'], width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="...", width=3, command=self._select_output_dir).pack(side=tk.LEFT, padx=(5,0))

    def _build_advanced_tab(self, parent):
        """Isi tab pengaturan Lanjutan."""
        lf_perf = ttk.LabelFrame(parent, text="Performa", padding=10)
        lf_perf.pack(fill=tk.X, pady=5)

        ttk.Label(lf_perf, text="Max Workers (Thread):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(lf_perf, from_=1, to=16, textvariable=self.vars['performance_max_workers']).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        lf_log = ttk.LabelFrame(parent, text="Logging & Debug", padding=10)
        lf_log.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(lf_log, text="Mode Debug", 
                        variable=self.vars['advanced_debug_mode']).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(lf_log, text="Level Log:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Combobox(lf_log, textvariable=self.vars['advanced_log_level'],
                     values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                     state='readonly').grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

    def _select_output_dir(self):
        """Buka dialog untuk memilih folder output."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.vars['output_default_directory'].set(folder_selected)

    def _on_save(self):
        """Simpan pengaturan dan tutup jendela."""
        self._on_apply()
        self.destroy()

    def _on_apply(self):
        """Terapkan dan simpan pengaturan tanpa menutup."""
        try:
            for key, var in self.vars.items():
                if hasattr(self.manager.settings, key):
                    # Dapatkan nilai dari var
                    value = var.get()
                    # Set di instance settings manajer
                    self.manager.set_setting(key, value)
            
            # Simpan ke file
            self.manager.save_settings()
            # Terapkan ke config yang sedang berjalan
            self.manager.apply_to_config()
            
            # Update original settings
            self.original_settings = self.manager.load_settings()
            
            messagebox.showinfo("Tersimpan", "Pengaturan berhasil disimpan dan diterapkan.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan pengaturan:\n{e}", parent=self)

    def _on_cancel(self):
        """Tutup jendela tanpa menyimpan."""
        self.destroy()

    def _on_reset(self):
        """Kembalikan semua pengaturan ke default."""
        if messagebox.askyesno("Reset Pengaturan", 
                               "Anda yakin ingin mengembalikan semua pengaturan ke default?\n"
                               "Perubahan yang belum disimpan akan hilang.", 
                               parent=self):
            
            self.manager.reset_to_defaults()
            # Simpan perubahan (default) ke file
            self.manager.save_settings() 
            # Terapkan config
            self.manager.apply_to_config()
            # Muat ulang nilai default ke variabel
            self.original_settings = self.manager.load_settings()
            self._load_settings_to_vars()
            messagebox.showinfo("Reset", "Pengaturan telah dikembalikan ke default.", parent=self)