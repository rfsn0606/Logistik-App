# app.py (Versi Profesional Baru - Tema Dark Teal)
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import time
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# -------------------------
# Helper: safe rerun (compatibility)
# -------------------------
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# -------------------------
# Page config (Wide layout)
# -------------------------
st.set_page_config(
    page_title="LOGITRACK",
    page_icon="📦",
    layout="wide", # Layout wide untuk dashboard
    initial_sidebar_state="expanded" # Sidebar selalu terbuka
)

# -------------------------
# Load environment & Supabase
# -------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL atau SUPABASE_KEY tidak ditemukan. Pastikan file .env berada di folder yang benar.")
    st.stop()

@st.cache_resource
def init_supabase():
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Gagal inisiasi Supabase: {e}")
        return None

supabase = init_supabase()

if not supabase:
    st.stop()

# -------------------------
# Global session defaults
# -------------------------
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "user" not in st.session_state:
    st.session_state.user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "Karyawan" # Default role
if "page" not in st.session_state:
    st.session_state.page = "home"
if "stok" not in st.session_state:
    st.session_state.stok = pd.DataFrame(columns=["id", "Daftar Barang", "Jumlah Stok", "Satuan", "Harga Satuan", "Gambar"])
if "riwayat_transaksi" not in st.session_state:
    st.session_state.riwayat_transaksi = pd.DataFrame(columns=["Tanggal","Barang","Jenis","Jumlah","Satuan","Nilai"])
# Menambah state untuk editing
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# Daftar satuan yang diminta
SATUAN_OPTIONS = ["meter", "unit", "pcs", "roll"]

# -------------------------
# CSS / Tema (TEMA BARU: DARK TEAL - Sesuai Referensi)
# -------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', 'Inter', sans-serif;
        color: #E0E0E0; /* Teks abu-abu muda */
    }
    
    /* Latar belakang utama (background) */
    .main .block-container {
        background: linear-gradient(180deg, #0A191E 0%, #0F2C35 100%); /* Dark Teal */
        padding-top: 2rem;
    }
    
    /* Latar belakang Halaman Login */
    body > [class*="st-"] {
        background: linear-gradient(180deg, #0A191E 0%, #0F2C35 100%);
    }

    /* Sidebar */
    .st-emotion-cache-16txtl3 {
        background: #0F2C35; /* Dark teal (lebih pekat) */
        border-right: 1px solid #1A4A5A;
    }
    
    /* Header / Title */
    .main-title {
        font-size: 50px;
        font-weight: 700;
        letter-spacing: 1px;
        text-align: center;
        margin: 6px 0 0 0;
        background: linear-gradient(90deg, #003366, #f0f8ff); /* Teal/Cyan gradient (dari ref) */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center;
        color: #9CBC6; /* Muted teal */
        margin-bottom: 24px;
        font-weight: 650;
    }


    /* Card */
    .card {
        background: #13541; /* Sedikit lebih terang dari bg */
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        border: 1px solid #1A4A5A;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        height: 100%;
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 200, 168, 0.1);
        border-color: #00C8A8;
    }
    
    .card img {
        border-radius: 8px;
        object-fit: cover;
        height: 180px; /* Tinggi gambar dibuat sedang */
        width: 100%;
        margin-bottom: 12px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00A98F, #00C8A8) !important; /* Teal gradient */
        color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        border: none !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 169, 143, 0.4);
    }
    
    /* Tombol Logout (khusus) */
    .st-emotion-cache-1v0mbdj .stButton>button {
        background: linear-gradient(90deg, #b00020, #e53935) !important; /* Merah */
    }
    .st-emotion-cache-1v0mbdj .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.4);
    }

    /* Input styling (dibuat gelap seperti ref) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div, .stDateInput>div>div {
        border-radius: 10px;
        background: #0A191E; /* Sangat gelap */
        border: 1px solid #1A4A5A;
        color: #E0E0E0;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #00C8A8;
    }
    
    /* Metric styling */
    .st-emotion-cache-1g8p5z1 {
        background: #103541;
        border: 1px solid #1A4A5A;
        padding: 16px;
        border-radius: 12px;
    }
    
    /* Plotly (Grafik) */
    .js-plotly-plot {
        background: #103541 !important;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Utility: normalize supabase columns -> app columns

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    cols_lower = [c.lower() for c in df.columns]
    
    #id
    if 'id_barang' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='id_barang'][0]] = "id"

    # name
    if 'nama_barang' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='nama_barang'][0]] = "Daftar Barang"
    
    # stok
    if 'jumlah_stok' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='jumlah_stok'][0]] = "Jumlah Stok"
    if 'satuan' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='satuan'][0]] = "Satuan"
    
    # price
    if 'harga_satuan' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='harga_satuan'][0]] = "Harga Satuan"
    
    # image
    if 'gambar_url' in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='gambar_url'][0]] = "Gambar"
    if 'gambar' in cols_lower and 'gambar_url' not in cols_lower:
        mapping[[c for c in df.columns if c.lower()=='gambar'][0]] = "Gambar"

    if mapping:
        df = df.rename(columns=mapping)
    return df

# -------------------------
# Load data from Supabase (Fungsi Optimal)

def load_stok_from_supabase():
    try:
        resp = supabase.table("daftar_barang").select("*").execute()
        items = resp.data if resp.data else []
        if items:
            df = pd.DataFrame(items)
            df = normalize_columns(df)
            # Pastikan kolom utama ada
            for col in ["id", "Daftar Barang","Jumlah Stok","Satuan","Harga Satuan","Gambar"]:
                if col not in df.columns:
                    df[col] = ""
            df["id"] = df["id"].astype(str) # Pastikan ID adalah string untuk hashing di tombol edit/delete
            df = df[["id", "Daftar Barang","Jumlah Stok","Satuan","Harga Satuan","Gambar"]] # Ambil ID
            st.session_state.stok = df
        else:
            st.session_state.stok = pd.DataFrame(columns=["id", "Daftar Barang","Jumlah Stok","Satuan","Harga Satuan","Gambar"])
    except Exception as e:
        st.warning(f"Warning: gagal memuat data daftar_barang dari Supabase ({e}).")

def load_riwayat_from_supabase():
    try:
        resp = supabase.table("riwayat_transaksi").select("*").order("tanggal", desc=True).limit(1000).execute() # Ambil 1000 terbaru
        items = resp.data if resp.data else []
        if items:
            df = pd.DataFrame(items)
            # Normalisasi kolom jika nama di Supabase berbeda
            mapping = {
                "tanggal": "Tanggal",
                "barang": "Barang",
                "jenis": "Jenis",
                "jumlah": "Jumlah",
                "satuan": "Satuan",
                "nilai": "Nilai"
            }
            # Hanya rename kolom yang ada
            df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
            df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.strftime('%Y-%m-%d')
            st.session_state.riwayat_transaksi = df[mapping.values()] # Pastikan urutan
        else:
            st.session_state.riwayat_transaksi = pd.DataFrame(columns=["Tanggal","Barang","Jenis","Jumlah","Satuan","Nilai"])
    except Exception as e:
        st.warning(f"Warning: gagal memuat data riwayat_transaksi dari Supabase ({e}).")

# -------------------------
# Navigation helper
# -------------------------
def go_to_page(page_name):
    st.session_state.page = page_name
    safe_rerun()
    
# -------------------------
# Fungsi CRUD Tambahan (Hanya Atasan)
# -------------------------
def delete_barang(barang_id):
    try:
        # Hapus barang dari daftar_barang
        supabase.table("daftar_barang").delete().eq("id_barang", barang_id).execute()
        st.success("✅ Barang berhasil dihapus!")
        time.sleep(1)
        load_stok_from_supabase()
        safe_rerun()
    except Exception as e:
        st.error(f"❌ Gagal menghapus barang: {e}")

def set_edit_mode(barang_id):
    st.session_state.edit_id = barang_id
    go_to_page("edit_barang") # Pindah ke halaman edit
    
# -------------------------
# AUTH UI (centered boxes)
# -------------------------
def login_page():
    c1, c2, c3 = st.columns([1, 1.3, 1]) # Dibuat sedikit lebih sempit
    with c2:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        # Anda bisa tambahkan logo di sini jika mau
        # st.image("url_logo_anda.png", use_container_width=True) 
        st.markdown('<h1 class="main-title">Welcome Back!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Masuk ke akun LOGITRACK Anda</p>', unsafe_allow_html=True)
        
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="btn_login", use_container_width=True):
            try:
                user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = user_session
                
                # --- INI KODE FITUR ROLE (SAMA SEPERTI SEBELUMNYA) ---
                user_data = user_session.user.user_metadata
                role = user_data.get('role', 'Karyawan') # Default 'Karyawan'
                st.session_state.user_role = role
                
                st.success(f"✅ Login berhasil! Selamat datang!")
                time.sleep(1)
                safe_rerun()
            except Exception as e:
                st.error(f"Login Gagal: {e}")
        st.markdown("<hr style='border-color:#1A4A5A'>", unsafe_allow_html=True)
        
        # Link register
        if st.button("Belum punya akun? Register Sekarang.", key="btn_goto_register", use_container_width=True):
            st.session_state.auth_mode = "register"
            safe_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def register_page():
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">Create Account</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Mulai kelola stok Anda</p>', unsafe_allow_html=True)
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password (min 6 karakter)", type="password", key="reg_pass")
        
        # --- ROLE OTOMATIS "Karyawan" SAAT DAFTAR ---
        user_metadata = {'role': 'Karyawan', 'joined_at': datetime.now().isoformat()}
        
        if st.button("Register", key="btn_register", use_container_width=True):
            if not email or not password:
                st.error("Email dan Password tidak boleh kosong.")
            elif len(password) < 6:
                st.error("Password minimal 6 karakter.")
            else:
                try:
                    supabase.auth.sign_up({
                        "email": email, 
                        "password": password,
                        "options": {
                            "data": user_metadata # Menetapkan role 'Karyawan'
                        }
                    })
                    st.success("Akun berhasil dibuat!")
                    st.session_state.auth_mode = "login"
                    time.sleep(1)
                    safe_rerun()
                except Exception as e:
                    st.error(f"Gagal mendaftar: {e}")
        st.markdown("<hr style='border-color:#f0f8ff'>", unsafe_allow_html=True)
        if st.button("Sudah punya akun? Login", key="btn_goto_login", use_container_width=True):
            st.session_state.auth_mode = "login"
            safe_rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ======================== START APLIKASI UTAMA ===========================

# If not logged in, show auth (center)
if st.session_state.user is None:
    if st.session_state.auth_mode == "login":
        login_page()
    else:
        register_page()
    st.stop()

# --- Jika SUDAH LOGIN, tampilkan layout utama ---

# 1. Load data dari Supabase (Stok DAN Riwayat)
with st.spinner("Memuat data..."):
    load_stok_from_supabase()
    load_riwayat_from_supabase()

# 2. Setup Sidebar (Navigasi Baru)
with st.sidebar:
    # Anda bisa tambahkan logo di sini
    # st.image("https://plus.unsplash.com/premium_photo-1661962960694-0b4ed303744f?q=80&w=735&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)
    st.markdown(f"### 👤 {st.session_state.user.user.email}")
    st.markdown(f"**{st.session_state.user_role.capitalize()}**")
    st.markdown("---")
    
    st.subheader("Menu Navigasi")
    if st.button("🏠 Home Dashboard", key="nav_home", use_container_width=True):
        go_to_page("home")
    if st.button("📊 Daftar Barang", key="nav_daftar", use_container_width=True):
        go_to_page("Daftar Barang")
    if st.button("🔄 Catat Transaksi", key="nav_transaksi", use_container_width=True):
        go_to_page("transaksi")

    # --- FITUR ROLE BERAKSI (Hanya Atasan) ---
    # Cek di sini apakah Anda sudah login sebagai Atasan
    if st.session_state.user_role == "atasan":
        st.markdown("---")
        st.subheader("Menu Atasan")
        if st.button("➕ Tambah Barang Baru", key="nav_tambah", use_container_width=True):
            st.session_state.edit_id = None # Pastikan edit mode mati
            go_to_page("tambah_barang")
        if st.button("📈 Laporan", key="nav_laporan", use_container_width=True):
            go_to_page("laporan")
            
    st.markdown("---")
    if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.user_role = "Karyawan"
        st.session_state.page = "home"
        safe_rerun()

# 3. Tampilkan Halaman (Page) sesuai Pilihan Sidebar
main_container = st.container()

with main_container:

    # ---------- HOME ----------
    if st.session_state.page == "home":
        st.markdown('<h1 class="main-title">LOGITRACK</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Dashboard Sistem Manajemen Stok Profesional</p>', unsafe_allow_html=True)

        try:
            total_barang = len(st.session_state.stok)
            total_stok = int(pd.to_numeric(st.session_state.stok["Jumlah Stok"], errors="coerce").fillna(0).sum())
            nilai_total = int((pd.to_numeric(st.session_state.stok["Jumlah Stok"], errors="coerce").fillna(0) *
                               pd.to_numeric(st.session_state.stok["Harga Satuan"], errors="coerce").fillna(0)).sum())
            barang_kritis = len(st.session_state.stok[pd.to_numeric(st.session_state.stok["Jumlah Stok"], errors="coerce").fillna(0) < 10])
        except Exception:
            total_barang = 0
            total_stok = 0
            nilai_total = 0
            barang_kritis = 0

        # 4 cards (layout wide)
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            st.metric("📦 Total Jenis Barang", total_barang)
        with c2:
            st.metric("💰 Nilai Inventaris", f"Rp {nilai_total:,}")
        with c3:
            st.metric("🧾 Transaksi Tercatat", len(st.session_state.riwayat_transaksi))
        with c4:
            st.metric("⚠️ Stok Kritis (<10)", barang_kritis, delta=barang_kritis, delta_color="inverse")

        st.markdown("---")
        
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            st.subheader("📦 5 Barang dengan Stok Terendah")
            if not st.session_state.stok.empty:
                stok_df = st.session_state.stok.copy()
                stok_df["Jumlah Stok"] = pd.to_numeric(stok_df["Jumlah Stok"], errors="coerce").fillna(0)
                st.dataframe(
                    stok_df.sort_values("Jumlah Stok").head(5)[["Daftar Barang", "Jumlah Stok", "Satuan"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Belum ada data barang.")

        with c_right:
            st.subheader("📜 5 Transaksi Terakhir")
            if not st.session_state.riwayat_transaksi.empty:
                st.dataframe(
                    st.session_state.riwayat_transaksi.head(5)[["Tanggal", "Barang", "Jenis", "Jumlah"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Belum ada data transaksi.")


    # ---------- DAFTAR BARANG (dengan search & gambar) ----------
    elif st.session_state.page == "Daftar Barang":
        st.markdown('<h1 class="main-title">Daftar Barang</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Cari dan lihat detail stok barang Anda</p>', unsafe_allow_html=True)

        # Search bar
        search = st.text_input("Cari barang...", key="search_barang", placeholder="Ketik nama barang...", label_visibility="collapsed")

        if search:
            mask = st.session_state.stok["Daftar Barang"].astype(str).str.contains(search, case=False, na=False)
            filtered = st.session_state.stok[mask].copy()
        else:
            filtered = st.session_state.stok.copy()

        if filtered.empty:
            st.info("Belum ada data barang yang tersimpan atau hasil pencarian kosong.")
        else:
            # Tampilan grid card yang lebih baik
            ncols = 4 # 4 kolom di layout wide
            items = filtered.reset_index(drop=True)
            rows = (len(items) + ncols - 1) // ncols

            for r in range(rows):
                # Ubah gap dari "medium" menjadi "small" agar card tampak lebih kecil (menurut permintaan "sedang")
                cols_row = st.columns(ncols, gap="small") 
                for c in range(ncols):
                    idx = r * ncols + c
                    if idx < len(items):
                        row = items.loc[idx]
                        with cols_row[c]:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            img_url = str(row.get("Gambar", "")).strip()
                            
                            # Kontainer untuk gambar agar ukurannya tetap
                            st.markdown('<div style="height: 180px; overflow: hidden; border-radius: 8px;">', unsafe_allow_html=True)
                            if img_url:
                                st.image(img_url, use_container_width=True) # CSS akan menangani styling
                            else:
                                st.image("https://via.placeholder.com/400x250.png/103541/9ECBC6?text=Tidak+Ada+Gambar", use_container_width=True) # Placeholder tema baru
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.markdown(f"<h4>{row['Daftar Barang']}</h4>", unsafe_allow_html=True)
                            stok = row.get("Jumlah Stok", 0)
                            satuan = row.get("Satuan", "")
                            harga = pd.to_numeric(row.get("Harga Satuan", 0), errors='coerce')
                            st.markdown(f"<p>Stok: {stok} {satuan}<br>Harga: Rp {int(harga):,}</p>", unsafe_allow_html=True)
                            
                            # --- FITUR EDIT DAN HAPUS (Hanya Atasan) ---
                            if st.session_state.user_role == "atasan":
                                col_edit, col_delete = st.columns(2)
                                with col_edit:
                                    # Menggunakan ID sebagai key
                                    if st.button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True):
                                        set_edit_mode(row['id'])
                                with col_delete:
                                    if st.button("🗑️ Hapus", key=f"delete_{row['id']}", use_container_width=True):
                                        delete_barang(row['id'])
                                        
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("") # Menambah spasi antar baris


    # ---------- TRANSAKSI (LOGIKA OPTIMAL) ----------
    elif st.session_state.page == "transaksi":
        st.markdown('<h1 class="main-title">Transaksi Barang</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Catat barang masuk / keluar (langsung ke database)</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1.5], gap="large") # Layout form dan riwayat
        
        with col1:
            with st.form("form_transaksi"):
                st.subheader("Form Transaksi")
                
                if st.session_state.stok.empty:
                    st.warning("Daftar stok kosong. Tambahkan data barang dulu (via menu Atasan).")
                    barang = ""
                    barang_options = []
                else:
                    barang_options = st.session_state.stok["Daftar Barang"].astype(str).tolist()
                    barang = st.selectbox("Pilih Barang", barang_options, key="select_barang", index=None, placeholder="Pilih barang...")
                
                jenis = st.radio("Jenis Transaksi", ["Masuk","Keluar"], horizontal=True, key="radio_jenis")
                jumlah = st.number_input("Jumlah", min_value=1, value=1, key="num_jumlah")
                tanggal = st.date_input("Tanggal", datetime.now(), key="date_tanggal")
                
                submitted = st.form_submit_button("Simpan Transaksi", use_container_width=True)
                
            if submitted:
                if not barang:
                    st.error("Pilih barang terlebih dahulu.")
                else:
                    try:
                        barang_data = st.session_state.stok[st.session_state.stok["Daftar Barang"] == barang].iloc[0]
                        barang_id = barang_data["id"] # Ambil ID unik
                        satuan = barang_data["Satuan"]
                        harga = int(pd.to_numeric(barang_data["Harga Satuan"], errors="coerce"))
                        stok_lama = int(pd.to_numeric(barang_data["Jumlah Stok"], errors="coerce"))
                        nilai = jumlah * harga

                        if jenis == "Masuk":
                            stok_baru = stok_lama + jumlah
                        else: # Jenis "Keluar"
                            if jumlah > stok_lama:
                                st.error(f"❌ Stok tidak cukup! Stok saat ini: {stok_lama}")
                                st.stop() 
                            stok_baru = stok_lama - jumlah

                        # LOGIKA PENYIMPANAN OPTIMAL
                        payload_t = {
                            "tanggal": tanggal.strftime("%Y-%m-%d"),
                            "barang": barang,
                            "jenis": jenis,
                            "jumlah": int(jumlah),
                            "satuan": satuan,
                            "nilai": float(nilai)
                        }
                        payload_s = {"jumlah_stok": stok_baru}

                        with st.spinner("Menyimpan ke database..."):
                            # 1. Simpan Riwayat (INSERT)
                            supabase.table("riwayat_transaksi").insert(payload_t).execute()
                            
                            # 2. Simpan Stok (UPDATE)
                            supabase.table("daftar_barang").update(payload_s).eq("id_barang", barang_id).execute()

                        st.success(f"✅ Transaksi '{jenis}' {jumlah} {satuan} '{barang}' berhasil disimpan!")
                        time.sleep(1)
                        load_stok_from_supabase() 
                        load_riwayat_from_supabase()
                        safe_rerun()

                    except Exception as e:
                        st.error(f"Gagal menyimpan transaksi: {e}")
                        st.error("PASTIKAN RLS (ROW LEVEL SECURITY) DI SUPABASE SUDAH DIMATIKAN UNTUK TABEL INI.")


        with col2:
            st.subheader("📜 Riwayat Transaksi Terbaru")
            if not st.session_state.riwayat_transaksi.empty:
                st.dataframe(
                    st.session_state.riwayat_transaksi, # Tampilkan semua
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Belum ada transaksi yang tercatat.")


    # ---------- FITUR BARU: TAMBAH BARANG (Hanya Atasan) ----------
    elif st.session_state.page == "tambah_barang":
        
        # Keamanan ganda
        if st.session_state.user_role != "atasan":
            st.error("Anda tidak memiliki izin untuk mengakses halaman ini.")
            st.stop()
            
        st.markdown('<h1 class="main-title">Tambah Barang Baru</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Halaman ini hanya untuk Atasan</p>', unsafe_allow_html=True)

        with st.form("form_tambah_barang", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                nama_barang = st.text_input("Nama Barang", placeholder="Contoh: Semen Gresik 50kg")
                jumlah_stok = st.number_input("Jumlah Stok Awal", min_value=0, value=0)
            with col2:
                # Perubahan: Satuan menggunakan selectbox dari list global SATUAN_OPTIONS
                satuan = st.selectbox("Satuan", SATUAN_OPTIONS, index=None, placeholder="Pilih satuan...")
                harga_satuan = st.number_input("Harga Satuan (Rp)", min_value=0, value=0)
            gambar_url = st.text_input("URL Gambar", placeholder="https://.../gambar.jpg")
            
            submitted = st.form_submit_button("Simpan Barang", use_container_width=True)

        if submitted:
            if not nama_barang or not satuan:
                st.error("Nama Barang dan Satuan wajib diisi!")
            else:
                try:
                    # Cek duplikat
                    resp_cek = supabase.table("daftar_barang").select("id_barang").eq("nama_barang", nama_barang).execute()
                    if resp_cek.data:
                        st.error(f"Gagal: Barang dengan nama '{nama_barang}' sudah ada di database.")
                    else:
                        # Buat payload
                        payload = {
                            "nama_barang": nama_barang,
                            "jumlah_stok": int(jumlah_stok),
                            "satuan": satuan,
                            "harga_satuan": int(harga_satuan),
                            "gambar_url": gambar_url
                        }
                        
                        with st.spinner("Menambahkan barang..."):
                            # Insert ke Supabase
                            supabase.table("daftar_barang").insert(payload).execute()
                        
                        st.success(f"Barang '{nama_barang}' berhasil ditambahkan!")
                        time.sleep(1)
                        load_stok_from_supabase()
                        go_to_page("Daftar Barang")

                except Exception as e:
                    st.error(f"Gagal menambahkan barang: {e}")
                    st.error("PASTIKAN RLS (ROW LEVEL SECURITY) DI SUPABASE SUDAH DIMATIKAN UNTUK TABEL INI.")

    # ---------- FITUR BARU: EDIT BARANG (Hanya Atasan) ----------
    elif st.session_state.page == "edit_barang":
        
        if st.session_state.user_role != "atasan":
            st.error("Anda tidak memiliki izin untuk mengakses halaman ini.")
            st.session_state.edit_id = None
            st.stop()
        
        barang_id = st.session_state.edit_id
        
        if not barang_id:
            st.warning("Tidak ada barang yang dipilih untuk diedit.")
            go_to_page("Daftar Barang")
            st.stop()
            
        # Ambil data barang yang akan diedit
        try:
            barang_data = st.session_state.stok[st.session_state.stok["id"] == barang_id].iloc[0]
        except IndexError:
            st.error("Data barang tidak ditemukan.")
            st.session_state.edit_id = None
            go_to_page("Daftar Barang")
            st.stop()

        st.markdown(f'<h1 class="main-title">{barang_data["Daftar Barang"]}</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Perbarui Detail Barang Anda</p>', unsafe_allow_html=True)

        with st.form("form_edit_barang"):
            col1, col2 = st.columns(2, gap="large")
            
            # Cari index satuan saat ini untuk pre-select
            try:
                current_satuan_index = SATUAN_OPTIONS.index(barang_data["Satuan"])
            except ValueError:
                current_satuan_index = None # Jika satuan tidak ada di list, set None
                
            with col1:
                # Nama barang tidak boleh diubah (sebaiknya dijadikan ID unik, tapi di sini hanya dibuat read-only)
                st.text_input("Nama Barang (Tidak Dapat Diubah)", value=barang_data["Daftar Barang"], disabled=True)
                # Stok TIDAK diubah di sini, tapi di menu transaksi
                st.number_input("Jumlah Stok Saat Ini", value=int(barang_data["Jumlah Stok"]), disabled=True)
            with col2:
                # Perubahan: Satuan menggunakan selectbox dari list global SATUAN_OPTIONS
                satuan_baru = st.selectbox("Satuan", SATUAN_OPTIONS, index=current_satuan_index, placeholder="Pilih satuan...")
                harga_satuan_baru = st.number_input("Harga Satuan (Rp)", min_value=0, value=int(barang_data["Harga Satuan"]))
            
            gambar_url_baru = st.text_input("URL Gambar", value=barang_data["Gambar"], placeholder="https://.../gambar.jpg")
            
            submitted = st.form_submit_button("Simpan Perubahan", use_container_width=True)

        if submitted:
            if not satuan_baru:
                st.error("Satuan wajib diisi!")
            else:
                try:
                    payload = {
                        "satuan": satuan_baru,
                        "harga_satuan": int(harga_satuan_baru),
                        "gambar_url": gambar_url_baru
                    }
                    
                    with st.spinner(f"Memperbarui barang {barang_data['Daftar Barang']}..."):
                        # Update ke Supabase
                        supabase.table("daftar_barang").update(payload).eq("id_barang", barang_id).execute()
                    
                    st.success(f"Barang '{barang_data['Daftar Barang']}' berhasil diperbarui!")
                    time.sleep(1)
                    st.session_state.edit_id = None # Matikan edit mode
                    load_stok_from_supabase()
                    go_to_page("Daftar Barang")

                except Exception as e:
                    st.error(f"Gagal memperbarui barang: {e}")
                    st.error("PASTIKAN RLS (ROW LEVEL SECURITY) DI SUPABASE SUDAH DIMATIKAN UNTUK TABEL INI.")


    # ---------- LAPORAN (Hanya Atasan) ----------
    elif st.session_state.page == "laporan":
        
        # Keamanan ganda
        if st.session_state.user_role != "atasan":
            st.error("Anda tidak memiliki izin untuk mengakses halaman ini.")
            st.stop()

        st.markdown('<h1 class="main-title">Laporan Stok & Transaksi</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Unduh laporan dan lihat analisis data (Hanya Atasan)</p>', unsafe_allow_html=True)
        
        riwayat_df = st.session_state.riwayat_transaksi
        
        total_transaksi = len(riwayat_df)
        total_masuk = riwayat_df[riwayat_df["Jenis"]=="Masuk"]["Jumlah"].sum() if total_transaksi > 0 else 0
        total_keluar = riwayat_df[riwayat_df["Jenis"]=="Keluar"]["Jumlah"].sum() if total_transaksi > 0 else 0

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            st.metric("Total Transaksi", total_transaksi)
        with c2:
            st.metric("Total Barang Masuk", f"{int(total_masuk)} unit")
        with c3:
            st.metric("Total Barang Keluar", f"{int(total_keluar)} unit")

        st.markdown("---")

        if not riwayat_df.empty:
            
            st.markdown('<h2 class="centered-subheader">Grafik Aktivitas Transaksi</h2>', unsafe_allow_html=True)
            riwayat_df["Tanggal"] = pd.to_datetime(riwayat_df["Tanggal"])
            transaksi_harian = riwayat_df.groupby(["Tanggal", "Jenis"])["Jumlah"].sum().reset_index()
            
            fig = px.bar(transaksi_harian, x="Tanggal", y="Jumlah", color="Jenis", 
                         title="Aktivitas Transaksi Harian", barmode="group", text_auto=True,
                         color_discrete_map={"Masuk": "#c0d6e4", "Keluar": "#003366"}) # Warna tema baru
            
            # Update layout agar cocok dengan tema
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#82ABDA", # Warna font baru
                legend_title_text=''
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi untuk ditampilkan di grafik.")

        st.markdown("---")
        st.subheader("Unduh Data Laporan")
        laporan_csv = st.session_state.stok.to_csv(index=False).encode('utf-8')
        transaksi_csv = st.session_state.riwayat_transaksi.to_csv(index=False).encode('utf-8')
        
        dl1, dl2 = st.columns(2, gap="large")
        with dl1:
            st.download_button("📦 Unduh Laporan Stok (.csv)", laporan_csv, file_name=f"Laporan_Stok_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
        with dl2:
            st.download_button("🔄 Unduh Laporan Transaksi (.csv)", transaksi_csv, file_name=f"Laporan_Transaksi_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

# End of file