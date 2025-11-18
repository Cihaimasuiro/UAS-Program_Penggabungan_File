# file: setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="file-merger-pro",
    version="2.2.0",
    author="Tim Damkar - Universitas Duta Bangsa Surakarta",
    author_email="230103186@mhs.udb.ac.id",
    description="Advanced file merging tool by Damkar Team",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File", # <--- DIPERBARUI
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
        'advanced': [
            'PyPDF2>=3.0.0',
            'openpyxl>=3.1.0',
            'rich>=13.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'file-merger=main:main',
        ],
    },
    include_package_data=True,
    keywords='file merger, image processing, text processing, file tools, utilities',
    project_urls={
        'Bug Reports': 'https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File/issues', # <--- DIPERBARUI
        'Source': 'https://github.com/Cihaimasuiro/UAS_Program_Penggabung_File',       # <--- DIPERBARUI
    },
)