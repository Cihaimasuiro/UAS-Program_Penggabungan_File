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
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

from ui.cli import CLI
from core.settings_manager import get_settings_manager
from config import get_output_path


class GUIApp:
    def __init__(self):
        self.cli = CLI()
        self.settings_mgr = get_settings_manager()

        self.root = tk.Tk()
        self.root.title("File Merger Pro - GUI")
        self.root.geometry("800x500")

        self._build_ui()

    def _build_ui(self):
        # Left control frame
        left = ttk.Frame(self.root, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        btn_add = ttk.Button(left, text="1. Add Files", width=25, command=self.add_files)
        btn_add.pack(pady=4)

        btn_view = ttk.Button(left, text="2. View Selected Files", width=25, command=self.view_files)
        btn_view.pack(pady=4)

        btn_clear = ttk.Button(left, text="3. Clear Selection", width=25, command=self.clear_selection)
        btn_clear.pack(pady=4)

        btn_process = ttk.Button(left, text="4. Process & Merge Files", width=25, command=self.process_files)
        btn_process.pack(pady=4)

        btn_batch = ttk.Button(left, text="5. Batch Process Directory", width=25, command=self.batch_process)
        btn_batch.pack(pady=4)

        btn_settings = ttk.Button(left, text="6. Settings", width=25, command=self.open_settings)
        btn_settings.pack(pady=4)

        btn_help = ttk.Button(left, text="7. Help", width=25, command=self.show_help)
        btn_help.pack(pady=4)

        # Right main frame
        right = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        lbl = ttk.Label(right, text="Selected Files")
        lbl.pack(anchor=tk.W)

        self.listbox = tk.Listbox(right, height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Small status/log area
        status_lbl = ttk.Label(right, text="Status / Logs")
        status_lbl.pack(anchor=tk.W, pady=(8, 0))

        self.log = tk.Text(right, height=8, state='disabled')
        self.log.pack(fill=tk.BOTH, expand=False)

        # Populate any pre-existing files
        self._refresh_listbox()

    def _log(self, msg: str):
        self.log.configure(state='normal')
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state='disabled')

    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.cli.files:
            self.listbox.insert(tk.END, f)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select files to add")
        if not paths:
            return

        added = 0
        for p in paths:
            is_valid, err = self.cli.file_manager.validate_file(p)
            if is_valid and p not in self.cli.files:
                self.cli.files.append(p)
                added += 1
            elif not is_valid:
                self._log(f"✗ Invalid: {p} - {err}")

        self._log(f"✓ Added {added} files")
        self._refresh_listbox()

    def view_files(self):
        if not self.cli.files:
            messagebox.showinfo("Selected Files", "No files selected")
            return

        top = tk.Toplevel(self.root)
        top.title("Selected Files")
        top.geometry("600x400")

        tree = ttk.Treeview(top, columns=("size", "type"), show='headings')
        tree.heading('size', text='Size (MB)')
        tree.heading('type', text='Category')
        tree.pack(fill=tk.BOTH, expand=True)

        for f in self.cli.files:
            info = self.cli.file_manager.get_file_info(f)
            tree.insert('', tk.END, values=(info['name'], f"{info['size_mb']:.2f}", info['category']))

    def clear_selection(self):
        if not self.cli.files:
            self._log("⚠ No files to clear")
            return

        if messagebox.askyesno("Clear Selection", f"Clear {len(self.cli.files)} selected files?"):
            self.cli.files.clear()
            self._refresh_listbox()
            self._log("✓ Selection cleared")

    def process_files(self):
        if not self.cli.files:
            messagebox.showwarning("No files", "Please add files before processing")
            return

        # Run processing in a background thread to keep GUI responsive
        thread = threading.Thread(target=self._process_files_background, daemon=True)
        thread.start()

    def _process_files_background(self):
        self._log("⏳ Detecting file types and processing...")
        is_consistent, category = self.cli.file_manager.check_file_types_consistency(self.cli.files)

        if not is_consistent:
            self._log("⚠ Mixed file types detected. Aborting.")
            messagebox.showerror("Mixed types", "Selected files have mixed categories. Make sure all are the same type.")
            return

        # Apply settings to use defaults
        try:
            self.settings_mgr.apply_to_config()
        except Exception:
            pass

        if category == 'image':
            # Use defaults from settings manager where possible
            s = self.settings_mgr.settings
            layout = s.image_default_layout
            spacing = s.image_default_spacing
            resize_mode = s.image_default_resize_mode
            filter_name = s.image_default_filter
            watermark = s.image_watermark_text if s.image_add_watermark else None

            output_name = f"merged_images.png"
            output_path = str(get_output_path(output_name))

            success, error = self.cli.image_processor.process_and_merge(
                self.cli.files,
                output_path,
                layout=layout,
                resize_mode=resize_mode,
                target_size=None,
                filter_name=filter_name,
                watermark=watermark,
                spacing=spacing,
                grid_cols=None
            )

            if success:
                self._log(f"✅ Images merged: {output_path}")
                messagebox.showinfo("Success", f"Images merged:\n{output_path}")
            else:
                self._log(f"❌ Error: {error}")
                messagebox.showerror("Error", str(error))

        elif category == 'text':
            s = self.settings_mgr.settings
            separator = s.text_default_separator
            add_ln = s.text_add_line_numbers
            add_ts = s.text_add_timestamps
            strip_ws = s.text_strip_whitespace

            output_name = f"merged.txt"
            output_path = str(get_output_path(output_name))

            success, error = self.cli.text_processor.merge_text_files(
                self.cli.files,
                output_path,
                separator_style=separator,
                add_line_numbers=add_ln,
                add_timestamps=add_ts,
                strip_whitespace=strip_ws
            )

            if success:
                self._log(f"✅ Text merged: {output_path}")
                messagebox.showinfo("Success", f"Text merged:\n{output_path}")
            else:
                self._log(f"❌ Error: {error}")
                messagebox.showerror("Error", str(error))
        else:
            self._log(f"⚠ Unsupported category: {category}")
            messagebox.showwarning("Unsupported", f"Unsupported category: {category}")

    def batch_process(self):
        directory = filedialog.askdirectory(title="Select directory to batch process")
        if not directory:
            return

        # Ask user whether to process images or text
        choice = messagebox.askquestion("Batch Type", "Process images in folder? Click 'No' for text files.")
        # Determine extensions set
        path = os.path.abspath(directory)
        files = []

        if choice == 'yes':
            exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        else:
            exts = {'.txt', '.md', '.log', '.csv'}

        for entry in os.scandir(path):
            if entry.is_file() and os.path.splitext(entry.name)[1].lower() in exts:
                files.append(entry.path)

        if not files:
            messagebox.showinfo("No files", "No matching files found in the selected directory.")
            return

        self.cli.files = files
        self._refresh_listbox()
        self._log(f"✓ Found {len(files)} files in {directory}")
        self.process_files()

    def open_settings(self):
        # Open settings.json in default editor (platform-specific)
        sm = self.settings_mgr
        settings_path = sm.SETTINGS_FILE if hasattr(sm, 'SETTINGS_FILE') else None
        if settings_path and settings_path.exists():
            try:
                # Windows-friendly
                if os.name == 'nt':
                    os.startfile(str(settings_path))
                else:
                    # Fallback to xdg-open / open
                    opener = 'open' if os.uname().sysname == 'Darwin' else 'xdg-open'
                    os.system(f"{opener} '{settings_path}'")
                self._log(f"Opened settings: {settings_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open settings: {e}")
        else:
            messagebox.showinfo("Settings", "No settings file found. Settings will be saved on next change.")

    def show_help(self):
        from ui.cli import CLI
        help_text = CLI().show_help.__doc__ or "See CLI help for usage."
        # Provide a friendly help popup with brief info
        message = (
            "File Merger Pro GUI\n\n" 
            "• Add files then click 'Process & Merge Files'.\n"
            "• Batch process a directory using option 5.\n"
            "• Settings opens the settings.json for manual editing.\n"
            "• Output files are saved to the configured output folder.\n"
        )
        messagebox.showinfo("Help", message)

    def run(self):
        self.root.mainloop()


def run_gui():
    app = GUIApp()
    app.run()


if __name__ == '__main__':
    run_gui()
