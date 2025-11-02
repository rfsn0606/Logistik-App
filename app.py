import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="LogiTrack",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
    <style>
    /* Import font modern dan elegan */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* Reset dan font keseluruhan */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
        color: #1E293B;
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        margin: 0;
        padding: 0;
    }

    /* Header dengan efek gradien dan animasi */
    .main-title {
        font-size: 56px;
        font-weight: 700;
        background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
        animation: fadeIn 1s ease-in-out;
    }

    /* Subheader */
    .sub-title {
        font-size: 24px;
        font-weight: 400;
        text-align: center;
        color: #475569;
        margin-bottom: 50px;
        line-height: 1.5;
        opacity: 0.9;
    }

    /* Card untuk navigasi, metrik, dan barang */
    .card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F1F5F9 100%);
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(20, 184, 166, 0.1), transparent);
        transition: left 0.5s;
    }
    .card:hover::before {
        left: 100%;
    }
    .card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }

    /* Gambar di card barang */
    .card img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 15px;
    }

    /* Tombol navigasi */
    .nav-button {
        background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
        color: white;
        border-radius: 16px;
        height: 60px;
        width: 100%;
        font-size: 18px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(15, 118, 110, 0.3);
        cursor: pointer;
        margin: 10px 0;
        text-align: center;  /* Pastikan teks di tengah */
    }
    .nav-button:hover {
        background: linear-gradient(135deg, #0D5F5F 0%, #0F766E 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(15, 118, 110, 0.4);
    }

    /* Tombol umum */
    .stButton button {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
        color: white;
        border-radius: 12px;
        height: 50px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3);
        cursor: pointer;
        text-align: center;  /* Teks tombol di tengah */
        display: block;
        margin: 0 auto;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #6D28D9 0%, #9333EA 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
    }

    /* Form dan tabel */
    .stForm {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }

    /* Animasi */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.5s ease-in-out;
    }

    /* Responsivitas */
    @media (max-width: 768px) {
        .main-title { font-size: 40px; }
        .card { padding: 15px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- Inisialisasi Session State ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Data stok dengan 30 jenis barang (cocok untuk logistik: kemasan, bahan baku, dll.)
# Menggunakan URL gambar placeholder dari unsplash untuk demo
if "stok" not in st.session_state:
    st.session_state.stok = pd.DataFrame({
        "Nama Barang": [
            "Karton", "Botol Plastik", "Label Stiker", "Tutup Botol", "Dus Kardus", "Palet Kayu", "Kantong Plastik",
            "Bungkus Vakum", "Pita Pengikat", "Kotak Makanan", "Gelas Kertas", "Sendok Plastik", "Sedotan", "Tisu Basah",
            "Sabun Cuci", "Deterjen", "Kemasan Bubble Wrap", "Kertas Wrapping", "Box Hadiah", "Tas Belanja",
            "Botol Kaca", "Kaleng Minuman", "Tutup Kaleng", "Label Kemasan", "Pembungkus Makanan", "Kantong Kertas",
            "Palet Plastik", "Kemasan Vakum", "Kotak Kardus Besar", "Bahan Pengisi"
        ],
        "Jumlah Stok": [120, 200, 150, 300, 90, 50, 180, 220, 140, 160, 190, 250, 300, 100, 80, 120, 170, 130, 110, 140,
                        90, 200, 180, 160, 210, 150, 70, 190, 100, 230],
        "Satuan": ["pcs", "pcs", "pcs", "pcs", "pcs", "pcs", "pcs", "roll", "roll", "pcs", "pcs", "pcs", "pcs", "pack",
                   "liter", "kg", "roll", "roll", "pcs", "pcs", "pcs", "pcs", "pcs", "pcs", "pack", "pcs", "pcs", "roll",
                   "pcs", "kg"],
        "Harga Satuan": [5000, 3000, 1000, 2000, 8000, 15000, 1500, 10000, 5000, 4000, 2000, 500, 300, 6000,
                         25000, 18000, 12000, 8000, 10000, 3000, 7000, 4000, 1500, 800, 15000, 2000, 20000, 15000,
                         12000, 10000],
        "Gambar": [
            "https://images.unsplash.com/photo-1586105251261-72a756497a11?w=300",  # Karton
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300",  # Botol Plastik
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=300",  # Label
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=300",  # Tutup
            "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=300",  # Dus
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300",  # Palet
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300",  # Kantong Plastik
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300",  # Bungkus Vakum
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",  # Pita
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",  # Kotak Makanan
            "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300",  # Gelas
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300",  # Sendok
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300",  # Sedotan
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=300",  # Tisu
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300",  # Sabun
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300",  # Deterjen
            "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=300",  # Bubble Wrap
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=300",  # Kertas Wrapping
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",  # Box Hadiah
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300",  # Tas Belanja
            "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300",  # Botol Kaca
            "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300",  # Kaleng
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=300",  # Tutup Kaleng
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=300",  # Label Kemasan
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",  # Pembungkus
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300",  # Kantong Kertas
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300",  # Palet Plastik
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300",  # Kemasan Vakum
            "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=300",  # Kotak Besar
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300"   # Bahan Pengisi
        ]
    })

if "riwayat_transaksi" not in st.session_state:
    st.session_state.riwayat_transaksi = pd.DataFrame(columns=["Tanggal", "Barang", "Jenis", "Jumlah", "Satuan", "Nilai"])

# --- Fungsi Navigasi ---
def go_to_page(page_name):
    st.session_state.page = page_name

# --- Fungsi Kreatif: Simulasi Loading ---
def loading_animation():
    with st.spinner("Memuat data..."):
        time.sleep(1)

# --- Definisi Metrik Global ---
total_barang = len(st.session_state.stok)
total_stok = st.session_state.stok["Jumlah Stok"].sum()
nilai_total = (st.session_state.stok["Jumlah Stok"] * st.session_state.stok["Harga Satuan"]).sum()
barang_kritis = len(st.session_state.stok[st.session_state.stok["Jumlah Stok"] < 100])

# --- HALAMAN UTAMA (Dashboard dengan Navigasi) ---
if st.session_state.page == 'home':
    st.markdown('<h1 class="main-title">📦 Sistem Manajemen Stok Barang</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Kelola stok barang logistik Anda dengan mudah, efisien, dan kreatif. Pilih menu di bawah untuk mulai!</p>', unsafe_allow_html=True)

    # Metrik Cepat di Home
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Jenis Barang", total_barang)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Stok", f"{total_stok} unit")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Nilai Inventaris", f"Rp {nilai_total:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Barang Kritis", barang_kritis)
        st.markdown('</div>', unsafe_allow_html=True)

    # Navigasi dengan Tombol
    st.subheader("🧭 Pilih Menu")
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown('<div class="card"><span style="font-size:64px;">📊</span><br>Dashboard Detail</div>', unsafe_allow_html=True)
        if st.button("Buka Dashboard", key="dashboard", help="Lihat analisis stok lengkap"):
            go_to_page('dashboard')
    with col2:
        st.markdown('<div class="card"><span style="font-size:64px;">🔄</span><br>Transaksi</div>', unsafe_allow_html=True)
        if st.button("Buka Transaksi", key="transaksi", help="Kelola barang masuk/keluar"):
            go_to_page('transaksi')
    with col3:
        st.markdown('<div class="card"><span style="font-size:64px;">📄</span><br>Laporan</div>', unsafe_allow_html=True)
        if st.button("Buka Laporan", key="laporan", help="Unduh laporan dan analisis"):
            go_to_page('laporan')

# --- HALAMAN DASHBOARD DETAIL ---
elif st.session_state.page == 'dashboard':
    loading_animation()
    st.markdown('<h1 class="main-title fade-in">📊 Dashboard Detail</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Analisis mendalam stok barang logistik Anda.</p>', unsafe_allow_html=True)

    # Tampilkan Barang dalam Grid Card dengan Gambar
    st.subheader("📦 Daftar Barang dengan Gambar")
    cols = st.columns(3)
    for i, row in st.session_state.stok.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
                <div class="card">
                    <img src="{row['Gambar']}" alt="{row['Nama Barang']}">
                    <h4>{row['Nama Barang']}</h4>
                    <p>Stok: {row['Jumlah Stok']} {row['Satuan']}</p>
                    <p>Harga: Rp {row['Harga Satuan']:,}</p>
                </div>
            """, unsafe_allow_html=True)

    # Grafik
    fig1 = px.bar(st.session_state.stok, x="Nama Barang", y="Jumlah Stok", color="Nama Barang",
                  title="Distribusi Stok", template="plotly_white")
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    if barang_kritis > 0:
        st.error("🚨 Stok rendah! Segera restok:")
        st.dataframe(st.session_state.stok/st)