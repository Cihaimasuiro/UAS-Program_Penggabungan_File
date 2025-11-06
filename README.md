# 🎓 UAS: Program Penggabung File (File Merger Pro)

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

## 📋 Daftar Isi
- [Overview](#-overview)
- [Fitur Utama](#-fitur-utama)
- [Teknologi](#-teknologi)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [Struktur Proyek](#-struktur-proyek)
- [Dokumentasi](#-dokumentasi)
- [Tim Pengembang](#-tim-pengembang)
- [Lisensi](#-lisensi)

---

## 📖 Overview

**File Merger Pro** adalah aplikasi Python canggih yang dikembangkan sebagai proyek Ujian Akhir Semester (UAS) untuk menggabungkan berbagai jenis file dengan antarmuka command-line yang intuitif dan fitur-fitur profesional.

🔗 **Repositori GitHub:** [github.com/Cihaimasuiro/UAS-Program_Penggabungan_File](https://github.com/Cihaimasuiro/UAS-Program_Penggabungan_File)

---

## ✨ Fitur Utama

### 🎨 **Pemrosesan Gambar Lengkap**
| Fitur | Deskripsi | Opsi |
|-------|-----------|------|
| **Gabung Vertikal** | Menumpuk gambar secara vertikal | Auto-resize, Padding |
| **Gabung Horizontal** | Menjajarkan gambar berdampingan | Alignment, Spacing |
| **Gabung Grid** | Susun gambar dalam grid (2x2, 3x3, dll) | Custom grid, Auto-layout |
| **Resize Otomatis** | Ubah ukuran gambar | Fit, Fill, Stretch modes |
| **Filter Gambar** | Efek khusus pada gambar | Grayscale, Sepia, Blur, Sharpen |
| **Watermark** | Tambahkan teks watermark | Custom text, Position, Opacity |

### 📝 **Pemrosesan Teks Canggih**
| Fitur | Format File | Opsi |
|-------|-------------|------|
| **Gabung Teks** | .txt, .md, .log, .py | Multiple encodings |
| **Separator Kustom** | Berbagai gaya pemisah | Simple, Fancy, Custom text |
| **Opsi Lanjutan** | Enhanced features | Line numbers, Timestamp, Remove extra spaces |
| **Konversi Format** | Multi-format support | To Markdown, To HTML |

### ⚡ **Fitur Sistem Professional**
- **🔄 Auto-detection** - Deteksi otomatis tipe file
- **📊 Progress Tracking** - Indikator progres real-time
- **🔒 Error Handling** - Penanganan error yang robust
- **📁 Batch Processing** - Proses multiple file sekaligus
- **🎯 Config Management** - Konfigurasi terpusat yang fleksibel

---

## 🛠️ Teknologi

### **Core Technologies**
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-9.0+-8B4513?logo=python&logoColor=white)

### **Dependencies Utama**
```python
Pillow>=9.0.0      # Image processing
colorama>=0.4.4    # Terminal colors
tqdm>=4.60.0       # Progress bars
```

### **Arsitektur**
- **Modular Design** - Kode terpisah untuk maintainability
- **MVC Pattern** - Separation of concerns
- **Plugin Architecture** - Mudah dikembangkan

---

## ⚙️ Instalasi

### **Prasyarat**
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### **Langkah Instalasi**

1. **Clone Repository**
```bash
git clone https://github.com/Cihaimasuiro/UAS-Program_Penggabungan_File.git
cd UAS-Program_Penggabungan_File
```

2. **Setup Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Verifikasi Instalasi**
```bash
python main.py --version
```

---

## 🚀 Penggunaan

### **Mode Interaktif** (Recommended untuk Pengguna Baru)
```bash
python main.py
```
📝 *Aplikasi akan memandu Anda melalui menu step-by-step*

### **Mode Command-Line** (Untuk Pengguna Advanced)
```bash
# Gabung gambar horizontal
python main.py --images img1.jpg img2.jpg --mode horizontal --output result.jpg

# Gabung file teks
python main.py --texts file1.txt file2.txt --separator fancy --output merged.txt

# Gabung grid gambar
python main.py --images *.jpg --mode grid --columns 3 --output grid_result.jpg
```

### **Menu Utama Aplikasi**
```
🔄 FILE MERGER PRO - MENU UTAMA
├── 🖼️  Gabung Gambar
│   ├── Horizontal
│   ├── Vertikal  
│   └── Grid
├── 📝 Gabung Teks
│   ├── Simple Merge
│   ├── Dengan Separator
│   └── Advanced Options
├── ⚙️  Pengaturan
└── ❌ Keluar
```

---

## 📁 Struktur Proyek

```
UAS-Program_Penggabungan_File/
├── 📂 core/                    # Core application logic
│   ├── file_manager.py        # File operations & validation
│   ├── image_processor.py     # All image processing functions
│   ├── text_processor.py      # Text merging & formatting
│   └── validator.py           # Input validation utilities
├── 📂 ui/                     # User interface components
│   ├── cli.py                 # Command-line interface
│   ├── menu.py                # Interactive menus
│   └── display.py             # Output formatting
├── 📂 utils/                  # Utility functions
│   ├── logger.py              # Logging configuration
│   ├── config_loader.py       # Configuration management
│   └── progress_bar.py        # Progress indicators
├── 📂 tests/                  # Test suites
│   ├── test_image_merge.py
│   └── test_text_merge.py
├── 📂 examples/               # Usage examples
│   ├── sample_images/
│   └── sample_texts/
├── 📜 main.py                 # Application entry point
├── 📜 config.py               # Main configuration
├── 📜 requirements.txt        # Dependencies
├── 📜 README.md               # This file
└── 📜 LICENSE                 # MIT License
```

---

## 📊 Dokumentasi

### **Supported Formats**

| Tipe File | Format | Status |
|-----------|--------|--------|
| **Gambar** | JPG, PNG, BMP, GIF | ✅ Full Support |
| **Gambar** | WebP, TIFF | ✅ Experimental |
| **Teks** | TXT, MD, LOG | ✅ Full Support |
| **Teks** | PY, JS, HTML | ✅ Basic Support |

### **Contoh Penggunaan**

**1. Menggabung Gambar Horizontal**
```python
from core.image_processor import ImageMerger

merger = ImageMerger()
result = merger.merge_horizontal(
    images=['foto1.jpg', 'foto2.jpg'],
    output_path='hasil_gabungan.jpg',
    resize_mode='fit'
)
```

**2. Menggabung File Teks dengan Format**
```python
from core.text_processor import TextMerger

merger = TextMerger()
result = merger.merge_files(
    files=['doc1.txt', 'doc2.md'],
    output_path='gabungan.txt',
    separator='fancy',
    add_timestamp=True
)
```

### **Konfigurasi**
Edit `config.py` untuk kustomisasi:
```python
# Image settings
IMAGE_SETTINGS = {
    'default_format': 'JPEG',
    'quality': 95,
    'max_width': 3840,
    'max_height': 2160
}

# Text settings  
TEXT_SETTINGS = {
    'encoding': 'utf-8',
    'max_file_size': 10485760  # 10MB
}
```

---

## 👥 Tim Pengembang

### **Universitas Duta Bangsa Surakarta**
**Program Studi:** Teknik Informatika  
**Mata Kuliah:** Pemrograman Python  
**Dosen Pengampu:** [Nama Dosen]

### **Anggota Tim** 🎯

| Nama | NIM | Role | Kontribusi |
|------|-----|------|------------|
| **Anindyar Bintang Rahma Esa** | 230103186 | Team Lead | Architecture & Core Logic |
| **Ridwan Yoga Pertama** | 230103206 | Backend Developer | Image Processing Module |
| **Ramdan Oky Sulistyawan** | 230103205 | UI Developer | CLI Interface & UX |
| **Muhammad Fakhriy Najib** | 230103069 | QA Engineer | Testing & Documentation |

### **Pembagian Tugas**
- **🔄 System Architecture** - Anindyar Bintang R.E.
- **🎨 Image Processing** - Ridwan Yoga P. 
- **📝 Text Processing** - Muhammad Fakhriy N.
- **🖥️ User Interface** - Ramdan Oky S.
- **📚 Documentation** - Tim Collective
- **🐛 Testing & Debugging** - Muhammad Fakhriy N.

---

## 📞 Support & Kontribusi

### **Melaporkan Issue**
Jika menemukan bug atau memiliki fitur request, silakan buat issue di [GitHub Issues](https://github.com/Cihaimasuiro/UAS-Program_Penggabungan_File/issues)

### **Berkontribusi**
1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

---

## 📜 Lisensi

Distributed under MIT License. See `LICENSE` file untuk detail lengkap.

---

## 🎓 Tentang UAS

Proyek ini dikembangkan sebagai bagian dari penilaian Ujian Akhir Semester mata kuliah **Pemrograman Python** di **Universitas Duta Bangsa Surakarta**.

**📅 Timeline Pengembangan:**
- **Analisis Kebutuhan:** Minggu 1-2
- **Desain Arsitektur:** Minggu 3-4  
- **Implementasi:** Minggu 5-8
- **Testing & Debugging:** Minggu 9-10
- **Documentation:** Minggu 11-12
- **Final Review:** Minggu 13-14

---
<div align="center">

### **⭐ Jika project ini membantu, jangan lupa beri star di repository!**

**Dibuat dengan ❤️ oleh Tim TI A6 - Universitas Duta Bangsa Surakarta**

</div>