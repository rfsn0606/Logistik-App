import streamlit as st
import pandas as pd
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Sistem Manajemen Stok Barang",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Warna Tema (CSS) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1E3A8A;
        color: white;
    }
    .main {
        background-color: #FFFACD;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        height: 2.5em;
        width: 10em;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigasi ---
st.sidebar.title("📦 Navigasi")
menu = st.sidebar.radio("Pilih Halaman", ["Dashboard", "Data Barang", "Transaksi", "Laporan"])

# --- Data Sementara (Simulasi) ---
if "stok" not in st.session_state:
    st.session_state.stok = pd.DataFrame({
        "Nama Barang": ["Karton", "Botol", "Label", "Tutup", "Dus"],
        "Jumlah Stok": [120, 200, 150, 300, 90],
        "Satuan": ["pcs", "pcs", "pcs", "pcs", "pcs"]
    })

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Dashboard Gudang")
    total_barang = len(st.session_state.stok)
    total_stok = st.session_state.stok["Jumlah Stok"].sum()
    barang_kritis = len(st.session_state.stok[st.session_state.stok["Jumlah Stok"] < 100])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jenis Barang", total_barang)
    col2.metric("Total Stok Barang", total_stok)
    col3.metric("Barang Hampir Habis", barang_kritis)

    st.subheader("📈 Grafik Jumlah Stok Barang")
    st.bar_chart(st.session_state.stok.set_index("Nama Barang")["Jumlah Stok"])

# --- DATA BARANG ---
elif menu == "Data Barang":
    st.title("📦 Data Barang di Gudang")
    st.dataframe(st.session_state.stok, use_container_width=True)
    
    st.subheader("➕ Tambah Barang Baru")
    with st.form("tambah_barang"):
        nama = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah Awal", min_value=1)
        satuan = st.selectbox("Satuan", ["pcs", "kg", "liter", "box"])
        tambah = st.form_submit_button("Tambah")
        if tambah:
            new_row = pd.DataFrame({"Nama Barang": [nama], "Jumlah Stok": [jumlah], "Satuan": [satuan]})
            st.session_state.stok = pd.concat([st.session_state.stok, new_row], ignore_index=True)
            st.success(f"Barang '{nama}' berhasil ditambahkan!")

# --- TRANSAKSI ---
elif menu == "Transaksi":
    st.title("🔁 Transaksi Barang Masuk/Keluar")
    pilihan = st.radio("Pilih Jenis Transaksi:", ["Barang Masuk", "Barang Keluar"])
    barang = st.selectbox("Pilih Barang", st.session_state.stok["Nama Barang"])
    jumlah = st.number_input("Jumlah", min_value=1)
    simpan = st.button("Simpan Transaksi")

    if simpan:
        idx = st.session_state.stok[st.session_state.stok["Nama Barang"] == barang].index[0]
        if pilihan == "Barang Masuk":
            st.session_state.stok.at[idx, "Jumlah Stok"] += jumlah
            st.success(f"{jumlah} {st.session_state.stok.at[idx, 'Satuan']} '{barang}' masuk gudang.")
        else:
            if jumlah > st.session_state.stok.at[idx, "Jumlah Stok"]:
                st.error("❌ Jumlah keluar melebihi stok!")
            else:
                st.session_state.stok.at[idx, "Jumlah Stok"] -= jumlah
                st.success(f"{jumlah} {st.session_state.stok.at[idx, 'Satuan']} '{barang}' keluar gudang.")

# --- LAPORAN ---
elif menu == "Laporan":
    st.title("📄 Laporan Stok Barang")
    st.dataframe(st.session_state.stok, use_container_width=True)
    csv = st.session_state.stok.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Laporan CSV", csv, "laporan_stok.csv", "text/csv")
