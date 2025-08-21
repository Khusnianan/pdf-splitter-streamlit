# app.py
import streamlit as st
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="PDF Splitter & Merger", page_icon="📑", layout="centered")

def parse_ranges(ranges_str, max_page):
    """Parse a ranges string like '1-3,5,7-9' into sorted unique 1-based page numbers."""
    pages = set()
    if not ranges_str.strip():
        return []
    for part in ranges_str.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                raise ValueError(f"Rentang tidak valid: '{part}'")
            if start < 1 or end < 1 or start > max_page or end > max_page or start > end:
                raise ValueError(f"Rentang di luar batas halaman: '{part}' (maks {max_page})")
            pages.update(range(start, end + 1))
        else:
            try:
                p = int(part)
            except ValueError:
                raise ValueError(f"Nomor halaman tidak valid: '{part}'")
            if p < 1 or p > max_page:
                raise ValueError(f"Halaman {p} di luar batas (1..{max_page})")
            pages.add(p)
    return sorted(pages)

def split_each_page(reader: PdfReader):
    outputs = []
    for idx in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[idx])
        bio = BytesIO()
        writer.write(bio)
        bio.seek(0)
        outputs.append((f"page_{idx+1}.pdf", bio.getvalue()))
    return outputs

def split_by_ranges(reader: PdfReader, page_list):
    outputs = []
    current_start = None
    for i, p in enumerate(page_list):
        if current_start is None:
            current_start = p
        if i == len(page_list) - 1 or page_list[i+1] != p + 1:
            writer = PdfWriter()
            for k in range(current_start - 1, p):
                writer.add_page(reader.pages[k])
            label = f"pages_{current_start}" if current_start == p else f"pages_{current_start}-{p}"
            bio = BytesIO()
            writer.write(bio)
            bio.seek(0)
            outputs.append((f"{label}.pdf", bio.getvalue()))
            current_start = None
    return outputs

def split_every_n(reader: PdfReader, n: int):
    outputs = []
    total = len(reader.pages)
    start = 0
    part = 1
    while start < total:
        writer = PdfWriter()
        end = min(start + n, total)
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        bio = BytesIO()
        writer.write(bio)
        bio.seek(0)
        outputs.append((f"part_{part}.pdf", bio.getvalue()))
        start = end
        part += 1
    return outputs

def split_odd_even(reader: PdfReader, mode: str):
    outputs = []
    odd_writer = PdfWriter()
    even_writer = PdfWriter()
    for i in range(len(reader.pages)):
        if (i + 1) % 2 == 1:
            odd_writer.add_page(reader.pages[i])
        else:
            even_writer.add_page(reader.pages[i])
    if mode in ("odd", "both"):
        bio = BytesIO()
        odd_writer.write(bio)
        bio.seek(0)
        outputs.append(("odd_pages.pdf", bio.getvalue()))
    if mode in ("even", "both"):
        bio = BytesIO()
        even_writer.write(bio)
        bio.seek(0)
        outputs.append(("even_pages.pdf", bio.getvalue()))
    return outputs

def merge_all(reader: PdfReader):
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    bio = BytesIO()
    writer.write(bio)
    bio.seek(0)
    return [("merged_all.pdf", bio.getvalue())]

st.title("📑 PDF Splitter & Merger")
st.write("Unggah file PDF dan pilih mode pemisahan atau penggabungan.")

uploaded_file = st.file_uploader("Unggah PDF", type=["pdf"])

with st.expander("⚙️ Opsi", expanded=True):
    mode = st.radio(
        "Pilih mode:",
        options=[
            "Setiap Halaman Terpisah",
            "Rentang Halaman Kustom",
            "Setiap N Halaman",
            "Halaman Ganjil/Genap",
            "Gabungkan Semua Halaman"
        ],
        index=0
    )
    if mode == "Rentang Halaman Kustom":
        ranges_str = st.text_input("Masukkan rentang (misal: 1-3,5,7-9)", value="1-3")
    elif mode == "Setiap N Halaman":
        n = st.number_input("Jumlah halaman per file", min_value=1, value=5, step=1)
    elif mode == "Halaman Ganjil/Genap":
        odd_even = st.selectbox("Pilih:", options=["Ganjil saja", "Genap saja", "Keduanya"], index=0)

col1, col2 = st.columns(2)
with col1:
    add_suffix = st.text_input("Tambahkan suffix nama file (opsional)", value="split")
with col2:
    zip_name = st.text_input("Nama berkas ZIP hasil", value="result.zip")

st.markdown("---")

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        st.info(f"File: **{uploaded_file.name}** • {total_pages} halaman")
        
        if st.button("🚀 Proses", use_container_width=True):
            outputs = []
            if mode == "Setiap Halaman Terpisah":
                outputs = split_each_page(reader)
            elif mode == "Rentang Halaman Kustom":
                page_list = parse_ranges(ranges_str, total_pages)
                if not page_list:
                    st.warning("Tidak ada halaman terpilih.")
                else:
                    outputs = split_by_ranges(reader, page_list)
            elif mode == "Setiap N Halaman":
                outputs = split_every_n(reader, int(n))
            elif mode == "Halaman Ganjil/Genap":
                m = "odd" if odd_even == "Ganjil saja" else ("even" if odd_even == "Genap saja" else "both")
                outputs = split_odd_even(reader, m)
            elif mode == "Gabungkan Semua Halaman":
                outputs = merge_all(reader)

            if not outputs:
                st.stop()

            mem_zip = BytesIO()
            with ZipFile(mem_zip, mode="w", compression=ZIP_DEFLATED) as zf:
                for fname, data in outputs:
                    base = fname.rsplit(".pdf", 1)[0]
                    out_name = f"{base}_{add_suffix}.pdf" if add_suffix else f"{base}.pdf"
                    zf.writestr(out_name, data)
            mem_zip.seek(0)

            st.success(f"Selesai! {len(outputs)} berkas dibuat.")
            st.download_button(
                "⬇️ Unduh Hasil (ZIP)",
                data=mem_zip,
                file_name=zip_name or "result.zip",
                mime="application/zip",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan unggah berkas PDF untuk mulai.")
