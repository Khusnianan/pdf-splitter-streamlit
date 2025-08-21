# PDF Splitter (Streamlit)

Aplikasi Streamlit sederhana untuk memisahkan file PDF menjadi beberapa berkas berdasarkan:
- Setiap halaman terpisah
- Rentang halaman kustom (mis. `1-3,5,7-9`)
- Setiap N halaman
- Halaman ganjil/genap

## Menjalankan Secara Lokal

```bash
# 1) Buat & aktifkan virtual env (opsional tapi disarankan)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependensi
pip install -r requirements.txt

# 3) Jalankan
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud

1. Buat repository GitHub baru, misalnya: `pdf-splitter-streamlit`.
2. Upload file berikut ke repo:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Buka https://share.streamlit.io/ dan **Sign in** dengan GitHub Anda.
4. Klik **New app** → pilih repo, branch `main`, file path `app.py`.
5. Klik **Deploy**.

> Tips: Pastikan repository **public** agar bisa di-deploy gratis.

## Struktur Project
```
.
├── app.py
├── requirements.txt
└── README.md
```

## Catatan
- Menggunakan library [`pypdf`](https://pypi.org/project/pypdf/) (fork modern dari PyPDF2).
- File hasil dikemas menjadi ZIP agar mudah diunduh sekaligus.
- Input rentang halaman menggunakan indexing berbasis 1 (halaman pertama = 1).
