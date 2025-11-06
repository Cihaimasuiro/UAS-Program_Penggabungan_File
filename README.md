# 🎓 UAS: Program Penggabung File (File Merger Pro)

Ini adalah proyek Ujian Akhir Semester (UAS) yang dikembangkan sebagai aplikasi *command-line* (CLI) canggih untuk menggabungkan berbagai jenis file.

**[Lihat Repositori di GitHub](https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File)**

---

### 👤 Informasi Pengembang

* **Nama:** Anindyar Bintang Rahma Esa
* **NIM:** 230103186
* **Kelas:** TI A6

---

## 🚀 Fitur Utama

Aplikasi ini dirancang dengan arsitektur modular dan profesional, memisahkan logika inti (`core`), antarmuka pengguna (`ui`), dan konfigurasi (`config`).

### 🎨 Pemrosesan Gambar
* **Gabung Vertikal:** Menumpuk gambar secara vertikal.
* **Gabung Horizontal:** Menjajarkan gambar secara berdampingan.
* **Gabung Grid:** Menyusun gambar dalam grid (misalnya 2x2, 3x3) secara otomatis atau kustom.
* **Resize:** Mengubah ukuran gambar dengan mode *fit*, *fill*, atau *stretch*.
* **Filter:** Menerapkan filter seperti *Grayscale*, *Sepia*, *Blur*, dan *Sharpen*.
* **Watermark:** Menambahkan watermark teks ke gambar.

### 📝 Pemrosesan Teks
* **Gabung Teks:** Menggabungkan beberapa file `.txt`, `.md`, `.log`, dll.
* **Separator Kustom:** Memilih gaya pemisah antar file (simple, fancy, dll.).
* **Opsi Lanjutan:** Menambahkan nomor baris, *timestamp*, atau menghapus spasi berlebih.
* **Konversi Markdown:** Menggabungkan beberapa file teks dan menyimpannya sebagai satu file Markdown.

### 🏗️ Fitur Arsitektur
* **Modular:** Kode dipecah menjadi modul-modul yang mudah dikelola (`file_manager.py`, `image_processor.py`, `text_processor.py`).
* **Konfigurasi Terpusat:** Semua pengaturan (path, format, pesan error) disimpan di `config.py`.
* **CLI Interaktif:** Antarmuka `ui/cli.py` yang ramah pengguna untuk memandu proses.
* **Logging:** Mencatat semua aktivitas dan error ke file `logs/app.log` untuk *debugging*.
* **Penanganan Error:** Validasi file yang kuat untuk memastikan file ada, dapat dibaca, dan didukung.

## 🛠️ Teknologi yang Digunakan

* **Python 3.8+**
* **Pillow (PIL):** Untuk semua operasi pemrosesan gambar.
* **(Opsional) Rich/Questionary:** Untuk antarmuka CLI yang lebih canggih (jika ditambahkan).

## ⚙️ Cara Menjalankan

1.  **Clone repositori:**
    ```bash
    git clone [https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File.git](https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File.git)
    cd UAS_Program_Penggabung_File
    ```

2.  **Buat virtual environment (direkomendasikan):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Di Windows: venv\Scripts\activate
    ```

3.  **Install dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan aplikasi:**
    ```bash
    python main.py
    ```

5.  **Ikuti menu interaktif** yang muncul di terminal Anda.