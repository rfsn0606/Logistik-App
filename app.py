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
        color: #6B8E23;
        background: url('https://www.toptal.com/designers/subtlepatterns/uploads/dot-grid.png'), 
            linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        background-repeat: repeat;
        background-attachment: fixed;

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
        height: 300px;
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
# Menggunakan URL gambar dari unsplash untuk demo
if "stok" not in st.session_state:
    st.session_state.stok = pd.DataFrame({
        "Daftar Barang": [
            "Kain Katun", "Kain Polyester", "Kain Denim", "Kain Satin", "Kain Fleece", "Benang Katun", "Benang Polyester","Benang Sulam/Embroidery",
            "Pewarna Kain","Kancing", "Zipper/Resleting", "Label Pakaian", "Jarum Jahit","Tali/Pita","Mesin Jahit","Mesin Sablon","Mesin Potong Kain",
            "Mesin Bordir","Papan Pola/Pattern","Kertas Pola/Pattern","Meja Jahit","Setrika/Ironing","Manekin/Dummy","Peniti/Safety Pin",
        ],
        "Jumlah Stok": [500, 450, 300, 275, 100, 550, 350, 120, 235, 160, 500, 1200, 185, 110, 4, 3, 3,
                        5, 75, 200, 10, 6, 25, 150],
        "Satuan": ["Meter", "Meter", "Meter", "Meter", "Meter", "Roll", "Roll", "Roll", "Kg", "Box", "Pcs", "Pcs", "Box",
                   "Roll", "Unit", "Unit", "Unit", "Unit", "Pcs", "Lembar", "Unit", "Unit",
                   "Unit", "Box"],
        "Harga Satuan": [25000, 30000, 40000, 35000, 45000, 12000, 15000, 18000, 60000, 25000, 5000, 500, 10000,
                         15000, 3750000, 2500000, 2000000, 5000000, 50000, 5000, 40000, 350000,
                         250000, 8000],
        "Gambar": [
            "https://images.unsplash.com/photo-1630920501459-f3e99320c4a5?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1974",  # Kain Katun
            "https://images.unsplash.com/photo-1651509245933-12e6cc1b24bc?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2070",  # Kain Polyester
            "https://images.unsplash.com/photo-1737093805570-5d314ff60b11?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2070",  # Kain Denim
            "https://images.unsplash.com/photo-1619043518800-7f14be467dca?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1074",  # Kain Satin
            "https://plus.unsplash.com/premium_photo-1740017727071-a531c023dd29?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1974",  # Kain Fleece
            "https://images.unsplash.com/photo-1663612318024-52d6b1fff823?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2067",  # Benang Katun
            "https://plus.unsplash.com/premium_photo-1723489262770-1038d8b8e584?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2070",  # Benang Polyester
            "https://images.pexels.com/photos/6634613/pexels-photo-6634613.jpeg",  # Benang Sulam
            "https://down-id.img.susercontent.com/file/id-11134201-7qul1-lg5fr8r5625z78_tn.webp",  # Pewarna Kain
            "https://images.unsplash.com/photo-1711610378090-779a7881a789?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2067",  # Kancing
            "https://plus.unsplash.com/premium_photo-1675179041387-83807aa274aa?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2070",  # Zipper/Resleting
            "https://images.pexels.com/photos/9594079/pexels-photo-9594079.jpeg",  # Label Pakaian
            "https://m.media-amazon.com/images/I/81fFgnSrXYL._AC_SL1500_.jpg",  # Jarum Jahit
            "https://plus.unsplash.com/premium_photo-1675202429654-4cc9d0e8f521?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",  # Tali/Pita
            "https://images.unsplash.com/photo-1486622923572-7a7e18acf192?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1140",  # Mesin Jahit
            "https://images.unsplash.com/photo-1614494731690-53925976ea29?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=735",  # Mesin Sablon
            "https://image.galerymesinjahit.com/s3/productimages/webp/co16518/p91619/w300-h300/1bd770f0-6107-49df-9570-6f8cd5ec2e68w.jpg",  # Mesin Potong Kain 
            "https://images.unsplash.com/photo-1633546805843-b2a1247dcf6f?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",  # Mesin Bordir
            "https://images.unsplash.com/photo-1738441639602-f6f2ff69a814?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2070",  # Papan Pola/Pattern
            "https://images.pexels.com/photos/4614228/pexels-photo-4614228.jpeg",  # Kertas Pola/Pattern
            "https://images-cdn.ubuy.co.id/633cdc6af345a132355c7401-sewing-machine-table-compact-folding.jpg",  # Meja Jahit
            "https://plus.unsplash.com/premium_photo-1667238557714-f92e4a2b2d1c?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=2015",  # Setrika/Ironing
            "https://plus.unsplash.com/premium_photo-1677838848150-0f749b7ee8b9?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1171",  # Manekin/Dummy
            "https://plus.unsplash.com/premium_photo-1759882509155-535a06e9fb14?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170"   # Peniti/Safety Pin
        ]
    })

if "riwayat_transaksi" not in st.session_state:
    st.session_state.riwayat_transaksi = pd.DataFrame(columns=["Tanggal", "Barang", "Jenis", "Jumlah", "Satuan", "Nilai"])

# --- Fungsi Simpan & Muat Data ---
def simpan_data():
    st.session_state.stok.to_csv("data_stok.csv", index=False)
    st.session_state.riwayat_transaksi.to_csv("riwayat_transaksi.csv", index=False)

def muat_data():
    try:
        st.session_state.stok = pd.read_csv("data_stok.csv")
        st.session_state.riwayat_transaksi = pd.read_csv("riwayat_transaksi.csv")
        muat_data()
    except FileNotFoundError:
        pass

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
    st.markdown('<h1 class="main-title">Sistem Manajemen Stok Barang</h1>', unsafe_allow_html=True)
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
    st.subheader("Menu")
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown('<div class="card"><span style="font-size:64px;">📊</span><br>Dashboard Detail</div>', unsafe_allow_html=True)
        if st.button("Buka Daftar Barang", key="Daftar Barang", help="Lihat analisis stok lengkap"):
            go_to_page('Daftar Barang')
    with col2:
        st.markdown('<div class="card"><span style="font-size:64px;">🔄</span><br>Transaksi</div>', unsafe_allow_html=True)
        if st.button("Buka Transaksi", key="transaksi", help="Kelola barang masuk/keluar"):
            go_to_page('transaksi')
    with col3:
        st.markdown('<div class="card"><span style="font-size:64px;">📄</span><br>Laporan</div>', unsafe_allow_html=True)
        if st.button("Buka Laporan", key="laporan", help="Unduh laporan dan analisis"):
            go_to_page('laporan')

# --- HALAMAN DASHBOARD DETAIL ---
elif st.session_state.page == 'Daftar Barang':
    loading_animation()
    st.markdown('<h1 class="main-title fade-in" style="text-align:center;">Daftar Barang</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lihat Detail Barang Anda di Sini!</p>', unsafe_allow_html=True)
    if st.button("Kembali", key="back_home_barang"):
        go_to_page('home')

    # Tampilkan Barang dalam Grid Card dengan Gambar
    cols = st.columns(3)
    for i, row in st.session_state.stok.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
                <div class="card">
                    <img src="{row['Gambar']}" alt="{row['Daftar Barang']}">
                    <h4>{row['Daftar Barang']}</h4>
                    <p>Stok: {row['Jumlah Stok']} {row['Satuan']}</p>
                    <p>Harga: Rp {row['Harga Satuan']:,}</p>
                </div>
            """, unsafe_allow_html=True)
            
# --- HALAMAN TRANSAKSI (BARANG MASUK / KELUAR) ---
elif st.session_state.page == 'transaksi':
    loading_animation()
    st.markdown('<h1 class="main-title fade-in" style="text-align:center;">Transaksi Barang</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Catat barang yang masuk atau keluar dari gudang Anda.</p>', unsafe_allow_html=True)

    # Form input transaksi
    with st.form("form_transaksi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            barang = st.selectbox("Pilih Barang", st.session_state.stok["Daftar Barang"])
            jenis = st.radio("Jenis Transaksi", ["Masuk", "Keluar"], horizontal=True)
        with col2:
            jumlah = st.number_input("Jumlah", min_value=1, value=1)
            tanggal = st.date_input("Tanggal", datetime.now())

        submitted = st.form_submit_button("Simpan Transaksi")

    # Proses simpan transaksi
    if submitted:
        # Dapatkan indeks barang yang dipilih
        idx = st.session_state.stok.index[st.session_state.stok["Daftar Barang"] == barang][0]
        satuan = st.session_state.stok.loc[idx, "Satuan"]
        harga = st.session_state.stok.loc[idx, "Harga Satuan"]
        nilai = jumlah * harga

        if jenis == "Masuk":
            st.session_state.stok.loc[idx, "Jumlah Stok"] += jumlah
        else:
            if jumlah > st.session_state.stok.loc[idx, "Jumlah Stok"]:
                st.error("Jumlah keluar melebihi stok yang tersedia!")
            else:
                st.session_state.stok.loc[idx, "Jumlah Stok"] -= jumlah

        # Simpan ke riwayat
        new_row = {
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Barang": barang,
            "Jenis": jenis,
            "Jumlah": jumlah,
            "Satuan": satuan,
            "Nilai": nilai
        }
        st.session_state.riwayat_transaksi = pd.concat([
            st.session_state.riwayat_transaksi,
            pd.DataFrame([new_row])
        ], ignore_index=True)

        st.success("Transaksi berhasil disimpan!")
        simpan_data()

    # Tampilkan tabel riwayat
    st.markdown("### 📜 Riwayat Transaksi Terbaru")
    if not st.session_state.riwayat_transaksi.empty:
        st.dataframe(st.session_state.riwayat_transaksi.sort_values("Tanggal", ascending=False), use_container_width=True)
    else:
        st.info("Belum ada transaksi yang tercatat.")

    # Tombol kembali
    if st.button("Kembali"):
        go_to_page('home')


# --- HALAMAN LAPORAN ---
elif st.session_state.page == 'laporan':
    loading_animation()
    st.markdown('<h1 class="main-title fade-in" style="text-align:center;">Laporan Stok & Transaksi</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Unduh laporan dan lihat analisis data Anda di sini.</p>', unsafe_allow_html=True)

    # Ringkasan metrik laporan
    total_transaksi = len(st.session_state.riwayat_transaksi)
    total_masuk = st.session_state.riwayat_transaksi[st.session_state.riwayat_transaksi["Jenis"] == "Masuk"]["Jumlah"].sum() if total_transaksi > 0 else 0
    total_keluar = st.session_state.riwayat_transaksi[st.session_state.riwayat_transaksi["Jenis"] == "Keluar"]["Jumlah"].sum() if total_transaksi > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Transaksi", total_transaksi)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Barang Masuk", f"{total_masuk} unit")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Barang Keluar", f"{total_keluar} unit")
        st.markdown('</div>', unsafe_allow_html=True)

    # Grafik Analisis Transaksi
    if not st.session_state.riwayat_transaksi.empty:
        fig = px.bar(
            st.session_state.riwayat_transaksi,
            x="Tanggal",
            y="Jumlah",
            color="Jenis",
            title="Aktivitas Transaksi Harian",
            text_auto=True,
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data transaksi untuk ditampilkan di grafik.")

    # Download laporan
    st.markdown("### 💾 Unduh Laporan")
    laporan_csv = st.session_state.stok.to_csv(index=False).encode('utf-8')
    transaksi_csv = st.session_state.riwayat_transaksi.to_csv(index=False).encode('utf-8')

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📦 Unduh Laporan Stok (.csv)",
            data=laporan_csv,
            file_name=f"Laporan_Stok_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            label="🔄 Unduh Laporan Transaksi (.csv)",
            data=transaksi_csv,
            file_name=f"Laporan_Transaksi_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # Tombol kembali
    if st.button("Kembali", key="back_home"):
        go_to_page('home')
