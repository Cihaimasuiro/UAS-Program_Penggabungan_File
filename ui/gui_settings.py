"""
Settings GUI Module - Bauhaus Edition
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, StringVar, BooleanVar, IntVar
from core.settings_manager import SettingsManager, UserSettings
from config import ImageConfig, TextConfig

# Bauhaus Palette (Local Definition for containment)
COLOR_BG = "#F2F2F2"
COLOR_FG = "#1A1A1A"
COLOR_ACCENT_1 = "#D22730"
COLOR_ACCENT_2 = "#1F3A93"
COLOR_PANEL = "#FFFFFF"

class SettingsWindow(tk.Toplevel):
    """Bauhaus-styled settings modal."""
    
    def __init__(self, parent, manager: SettingsManager):
        super().__init__(parent)
        self.manager = manager
        self.original_settings = self.manager.load_settings()
        
        self.title("Pengaturan")
        self.geometry("700x600")
        self.configure(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        
        self.vars = {}
        self._create_variables()
        self._load_settings_to_vars()
        self._build_ui()

    def _create_variables(self):
        # Automatically create variables based on UserSettings dataclass
        for key, value in self.original_settings.__dict__.items():
            if isinstance(value, bool):
                self.vars[key] = BooleanVar()
            elif isinstance(value, int):
                self.vars[key] = IntVar()
            else:
                self.vars[key] = StringVar()

    def _load_settings_to_vars(self):
        for key, var in self.vars.items():
            if hasattr(self.original_settings, key):
                var.set(getattr(self.original_settings, key))

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_BG)
        header.pack(fill=tk.X, padx=20, pady=20)
        tk.Label(header, text="KONFIGURASI", font=("Helvetica", 16, "bold"), 
                 bg=COLOR_BG, fg=COLOR_FG).pack(side=tk.LEFT)

        # Styled Notebook
        style = ttk.Style()
        style.configure("TNotebook", background=COLOR_BG)
        style.configure("TNotebook.Tab", font=("Helvetica", 10), padding=[10, 5])
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self._build_tab(notebook, "  GAMBAR  ", self._build_image_tab)
        self._build_tab(notebook, "  TEKS  ", self._build_text_tab)
        self._build_tab(notebook, "  OUTPUT  ", self._build_output_tab)
        self._build_tab(notebook, "  SISTEM  ", self._build_advanced_tab)

        # Footer Actions
        footer = tk.Frame(self, bg=COLOR_BG, pady=20)
        footer.pack(fill=tk.X, padx=20)

        # Helper for buttons
        def btn(txt, cmd, style_name="TButton"):
            ttk.Button(footer, text=txt, style=style_name, command=cmd).pack(side=tk.RIGHT, padx=5)

        btn("SIMPAN & TUTUP", self._on_save, "Primary.TButton")
        btn("Terapkan", self._on_apply, "Secondary.TButton")
        btn("Batal", self.destroy)
        
        ttk.Button(footer, text="Reset Default", style="TButton", 
                   command=self._on_reset).pack(side=tk.LEFT)

    def _build_tab(self, notebook, title, content_func):
        frame = ttk.Frame(notebook, style="TFrame", padding=15)
        notebook.add(frame, text=title)
        content_func(frame)

    def _section(self, parent, title):
        lbl = tk.Label(parent, text=title, font=("Helvetica", 11, "bold"), 
                       bg=COLOR_BG, fg=COLOR_ACCENT_2, pady=10)
        lbl.pack(anchor="w")
        return ttk.Frame(parent, style="Card.TFrame", padding=10)

    def _build_image_tab(self, parent):
        p = self._section(parent, "Tata Letak & Ukuran")
        p.pack(fill=tk.X)
        
        self._combo(p, "Default Layout:", 'image_default_layout', 
                    ['vertical', 'horizontal', 'grid'])
        self._spin(p, "Spacing (px):", 'image_default_spacing', 0, 500)
        self._combo(p, "Resize Mode:", 'image_default_resize_mode', 
                    list(ImageConfig.RESIZE_MODES.keys()))

        p = self._section(parent, "Efek & Watermark")
        p.pack(fill=tk.X, pady=10)
        
        self._combo(p, "Default Filter:", 'image_default_filter', 
                    list(ImageConfig.FILTERS.keys()))
        self._check(p, "Aktifkan Watermark Otomatis", 'image_add_watermark')
        self._entry(p, "Teks Watermark:", 'image_watermark_text')

    def _build_text_tab(self, parent):
        p = self._section(parent, "Format Dokumen")
        p.pack(fill=tk.X)
        
        self._combo(p, "Separator Style:", 'text_default_separator', 
                    list(TextConfig.SEPARATOR_STYLES.keys()))
        self._check(p, "Nomor Baris (Line Numbers)", 'text_add_line_numbers')
        self._check(p, "Export ke Markdown (.md)", 'text_markdown_export')
        
        p = self._section(parent, "Encoding")
        p.pack(fill=tk.X, pady=10)
        self._combo(p, "Default Encoding:", 'text_default_encoding', 
                    ['utf-8', 'latin-1', 'cp1252', 'ascii'])

    def _build_output_tab(self, parent):
        p = self._section(parent, "Penyimpanan")
        p.pack(fill=tk.X)
        
        f = tk.Frame(p, bg=COLOR_PANEL)
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Output Folder:", bg=COLOR_PANEL).pack(anchor="w")
        
        e = ttk.Entry(f, textvariable=self.vars['output_default_directory'])
        e.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2)
        ttk.Button(f, text="...", width=3, command=self._select_dir).pack(side=tk.LEFT, padx=5)

        self._check(p, "Timestamp di Nama File", 'output_use_timestamp')
        self._check(p, "Backup File Lama (Safe Mode)", 'output_create_backup')

    def _build_advanced_tab(self, parent):
        p = self._section(parent, "Performa")
        p.pack(fill=tk.X)
        self._spin(p, "Max Threads:", 'performance_max_workers', 1, 16)
        self._check(p, "Debug Mode (Log Verbose)", 'advanced_debug_mode')

    # --- UI Helpers ---
    def _combo(self, parent, label, key, values):
        f = tk.Frame(parent, bg=COLOR_PANEL)
        f.pack(fill=tk.X, pady=2)
        tk.Label(f, text=label, width=20, anchor="w", bg=COLOR_PANEL).pack(side=tk.LEFT)
        ttk.Combobox(f, textvariable=self.vars[key], values=values, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _entry(self, parent, label, key):
        f = tk.Frame(parent, bg=COLOR_PANEL)
        f.pack(fill=tk.X, pady=2)
        tk.Label(f, text=label, width=20, anchor="w", bg=COLOR_PANEL).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.vars[key]).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _spin(self, parent, label, key, _min, _max):
        f = tk.Frame(parent, bg=COLOR_PANEL)
        f.pack(fill=tk.X, pady=2)
        tk.Label(f, text=label, width=20, anchor="w", bg=COLOR_PANEL).pack(side=tk.LEFT)
        ttk.Spinbox(f, from_=_min, to=_max, textvariable=self.vars[key]).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _check(self, parent, label, key):
        f = tk.Frame(parent, bg=COLOR_PANEL)
        f.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(f, text=label, variable=self.vars[key]).pack(side=tk.LEFT)

    def _select_dir(self):
        d = filedialog.askdirectory()
        if d: self.vars['output_default_directory'].set(d)

    def _on_save(self):
        self._on_apply()
        self.destroy()

    def _on_apply(self):
        try:
            for k, v in self.vars.items():
                self.manager.set_setting(k, v.get())
            if self.manager.save_settings():
                self.manager.apply_to_config()
                messagebox.showinfo("Sukses", "Pengaturan disimpan!", parent=self)
            else:
                messagebox.showerror("Error", "Gagal menulis file settings.json", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _on_reset(self):
        if messagebox.askyesno("Reset", "Kembalikan ke pengaturan pabrik?"):
            self.manager.reset_to_defaults()
            self.manager.save_settings()
            self.original_settings = self.manager.load_settings()
            self._load_settings_to_vars()