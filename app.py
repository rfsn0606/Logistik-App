# app.py (Versi Profesional Baru - Tema VIBRANT GLASS)
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import time
from supabase import create_client, Client
import os
from dotenv import load_dotenv


# --- TAMBAHAN IMPORT UNTUK SCANNER ---
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from pyzbar.pyzbar import decode
from PIL import Image  
import io              
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import base64


def generate_barcode_image(code_string):
    """
    Menghasilkan gambar barcode (Code 128) sebagai bytes data.
    Input: string kode unik (misalnya LGT-001)
    Output: bytes data gambar PNG
    """
    try:
        # 1. Pilih format Code 128
        Code128 = barcode.get_barcode_class('code128')
        
        # 2. Buat instance barcode
        barcode_instance = Code128(str(code_string).upper(), writer=ImageWriter())
        
        # 3. Simpan gambar ke memori (buffer)
        buffer = io.BytesIO()
        # Parameter output_format='png' sudah default jika menggunakan ImageWriter
        barcode_instance.write(buffer) 
        buffer.seek(0)
        
        # 4. Baca bytes data
        return buffer.read()
    except Exception as e:
        print(f"Gagal generate barcode: {e}")
        return None

# --- KELAS PEMROSES VIDEO UNTUK SCANNER ---
class BarcodeScanner(VideoTransformerBase):
    def __init__(self):
        self.found_barcode = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
# Debugging: Tampilkan frame count di layar
        cv2.putText(img, f"Frame: {self.frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Deteksi barcode dalam frame
        decoded_objects = decode(img)
        if decoded_objects:
            for obj in decoded_objects:
            # Ambil data barcode
                barcode_data = obj.data.decode("utf-8")
                self.found_barcode = barcode_data
            
            # Gambar kotak hijau di sekitar barcode (Visual Feedback)
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([p for p in points], dtype=np.float32))
                    hull = hull.reshape((-1, 1, 2))
                    cv2.polylines(img, [np.int32(hull)], True, (0, 255, 0), 3)
                else:
                    cv2.polylines(img, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 3)

            # Tampilkan teks barcode di layar kamera
                cv2.putText(img, barcode_data, (obj.rect.left, obj.rect.top - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            # Jika tidak ada barcode, tampilkan pesan
            cv2.putText(img, "No barcode detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        return img
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
if "delete_id" not in st.session_state:
    st.session_state.delete_id = None
if "show_delete_confirmation" not in st.session_state:
    st.session_state.show_delete_confirmation = False
     

# Daftar satuan yang diminta
SATUAN_OPTIONS = ["meter", "unit", "pcs", "roll","kotak"]


# CSS / Tema

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', 'Inter', sans-serif;
        color: #FFFFFF;
    }
    
    body {
        background: linear-gradient(135deg, #0a1d37, #0f4c75, #3282b8);
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
        height: 100vh;
        overflow-x: hidden;
    }

    /* Background container utama */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05) !important; /* Sedikit transparan */
        backdrop-filter: blur(5px);
        padding-center: 2rem;
        border-radius: 18px;
        margin: 20px;
    }

    /* Sidebar */
    .st-emotion-cache-16txtl3 {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header / Title */
    .main-title {
        font-size: 80px;
        font-weight: 700;
        letter-spacing: 1px;
        text-align: center;
        margin: 6px 0 0 0;
        background: linear-gradient(90deg, #bbe1fa, #f7b733); /* Biru ke Gold */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center;
        color: #E0E0E0;
        margin-bottom: 24px;
        font-weight: 500;
    }

    /* Welcome Container 
    .welcome-container {
        position: relative;
        height: calc(100vh - 90px);
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 20px;
        z-index: 10;
    }

    .welcome-title {
        font-size: 3.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        z-index: 10;
    }

    .welcome-sub {
        font-size: 1.2rem;
        max-width: 650px;
        margin: 0 auto;
        z-index: 10;
        opacity: 0.9;
    }

    .cta-btn {
        margin-center: 30px;
        background: #bbe1fa;
        color: #0a1d37;
        padding: 15px 30px;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        cursor: pointer;
        font-weight: bold;
        transition: 0.3s;
        z-index: 10;
    }

    .cta-btn:hover {
        background: white;
        transform: scale(1.05);
    }

    /* Auth box */
    .auth-box {
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 26px;
        max-width: 480px;
        margin: 22px auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    /* Card (Daftar Barang) */
    .card {
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        border: 1px solid rgba(300, 255, 255, 0.1);
        height: 200%;
        transition: all 0.3s ease;

/* --- TAMBAHAN CSS UNTUK GAMBAR SERAGAM --- */
    .img-container {
        width: 100%;
        height: 180px;  /* TINGGI TETAP: Ubah angka ini jika ingin lebih tinggi/pendek */
        overflow: hidden;
        border-radius: 10px;
        margin-bottom: 12px;
        background-color: #eee; /* Warna loading sementara */
        position: relative;
    }

    .img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* MAGIC: Memotong gambar agar pas tanpa gepeng */
        object-position: center; /* Fokus ke tengah gambar */
        transition: transform 0.3s ease;
    }

    .card:hover .img-container img {
        transform: scale(1.0); /* Efek zoom dikit saat di-hover biar keren */
    }        

    }
    .card img {
        border-radius: 8px;
        object-fit: cover;
        height: 180px;
        width: 100%;
        margin-bottom: 12px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ff4b2b, #ff7854) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
    }
    
    /* Tombol Logout */
    div[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(90deg, #b00020, #e53935) !important;
    }
    div[data-testid="stSidebar"] .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(229, 57, 53, 0.4);
    }
    
    /* Tombol Edit/Delete */
    .card .stButton>button {
        background: linear-gradient(90deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    .card .stButton>button:hover {
        border-color: #f7b733 !important;
    }

    /* Input styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div, .stDateInput>div>div {
        border-radius: 10px;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #f7b733;
    }
    
    /* Metric styling */
    .st-emotion-cache-1g8p5z1 {
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
        border-radius: 12px;
        transition: transform 0.3s ease;
    }
    .st-emotion-cache-1g8p5z1:hover {
        transform: scale(1.05);
    }
    
    /* Plotly */
    .js-plotly-plot {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 14px;
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

def load_stok_from_supabase_VFINAL():
    try:
        resp = supabase.table("daftar_barang").select("*").execute()
        items = resp.data if resp.data else []


        if items:
            df = pd.DataFrame(items)
            df = normalize_columns(df)
            # Pastikan kolom utama ada
            for col in ["id_barang","nama_barang","jumlah_stok","satuan","harga_satuan","gambar_url","tanggal_update","kode_barcode"]:
                if col not in df.columns:
                    df[col] = 0 if col in ["jumlah_stok", "harga_satuan"] else ""
            
           # 1. FIX: GANTI NULL menjadi 0
            df['harga_satuan'] = df['harga_satuan'].apply(lambda x: 0 if pd.isna(x) or str(x).strip() == '' else x)
            df['jumlah_stok'] = df['jumlah_stok'].apply(lambda x: 0 if pd.isna(x) or str(x).strip() == '' else x)

            # 2. BRUTAL FIX: HAPUS SEMUA NON-ANGKA (Rp, Koma, Spasi)
            df['jumlah_stok'] = pd.to_numeric(df['jumlah_stok'], errors='coerce').fillna(0).astype(int)
            df['harga_satuan'] = pd.to_numeric(df['harga_satuan'], errors='coerce').fillna(0).astype(int)
            
            # 3. Final Konversi ke numeric (INI KUNCI PERHITUNGAN)
            df['jumlah_stok'] = df['jumlah_stok'].fillna(0).astype(int) 
            df['harga_satuan'] = df['harga_satuan'].fillna(0).astype(int)

            #Buat kolom ID dan tampilan
            
            if 'id' in df.columns:
                df["id"] = df["id"].astype(str) # Pastikan kolom ID di konversi

# KARENA DATA MENTAH SUDAH BERSIH, HANYA PERLU KONVERSI TIPE DATA SEBAGAI PENGAMAN:
            if 'Jumlah Stok' in df.columns:
                df['Jumlah Stok'] = pd.to_numeric(df['Jumlah Stok'], errors='coerce').fillna(0).astype(int)
            if 'Harga Satuan' in df.columns:
                df['Harga Satuan'] = pd.to_numeric(df['Harga Satuan'], errors='coerce').fillna(0).astype(int)
            st.session_state.stok = df
        else:
            # Pastikan semua kolom logika dan tampilan ada di DataFrame kosong
            cols = ["id_barang", "kode_barcode", "Daftar Barang","Jumlah Stok","Satuan","Harga Satuan","Gambar", "nama_barang", "gambar_url", "tanggal_update", "jumlah_stok"]
            st.session_state.stok = pd.DataFrame(columns=cols)
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
                "tanggal": "Tanggal",          # Wajib ada
                "nama_barang": "Barang",       # Wajib ada
                "jenis": "Jenis",              # PENTING: Masuk/Keluar
                "jumlah": "Jumlah",
                "satuan": "Satuan",
                "nilai": "Nilai"               # Total harga transaksi
            
            }
            # Hanya rename kolom yang ada
            df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
           
            if 'Tanggal' in df.columns:
                df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.strftime('%Y-%m-%d')
            elif 'tanggal' in df.columns:
                df['Tanggal'] = pd.to_datetime(df['tanggal']).dt.strftime('%Y-%m-%d')
            
            # 5. Ambil kolom untuk ditampilkan
            cols_wanted = [v for v in mapping.values() if v in df.columns]
            st.session_state.riwayat_transaksi = df[cols_wanted]
            
        else:
            st.session_state.riwayat_transaksi = pd.DataFrame(columns=["Tanggal", "Barang", "Jenis", "Jumlah", "Satuan", "Nilai"])
            
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
        load_stok_from_supabase_VFINAL()
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
        st.markdown('<h1 class="main-title">Selamat Datang!</h1>', unsafe_allow_html=True)
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
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)
        
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
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)
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
with st.spinner("Loading..."):
    load_stok_from_supabase_VFINAL()
    load_riwayat_from_supabase()

# 2. Setup Sidebar (Navigasi Baru)
with st.sidebar:
    # Anda bisa tambahkan logo di sini
    # st.image("URL_LOGO_ANDA", use_container_width=True)
    st.markdown(f"### 👤 {st.session_state.user.user.email}")
    st.markdown(f"**{st.session_state.user_role.capitalize()}**")
    st.markdown("---")
    
    st.subheader("Navigasi")
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
        st.subheader("Edit dan Tambah Barang")
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
            df_stok = st.session_state.stok.copy()
            df_stok['Jumlah Stok'] = pd.to_numeric(
                df_stok['Jumlah Stok'].astype(str).str.replace(r'[^\d]', '', regex=True),
                errors='coerce'
            ).fillna(0)
            df_stok['Harga Satuan'] = pd.to_numeric(
                df_stok['Harga Satuan'].astype(str).str.replace(r'[^\d]', '', regex=True),
                errors='coerce'
            ).fillna(0)
            total_barang = len(df_stok)
            total_stok = int(df_stok["Jumlah Stok"].sum())
            nilai_total = int((df_stok["Jumlah Stok"] * df_stok["Harga Satuan"]).sum())
            barang_kritis = barang_kritis = len(df_stok[df_stok["Jumlah Stok"] < 10])
        except Exception:
            st.error(f"⚠️ **ERROR FATAL PERHITUNGAN NILAI INVENTARIS:** {e}")
            total_barang = 0
            total_stok = 0
            nilai_total = 0
            barang_kritis = 0

        st.markdown('<div id="metrics"></div>', unsafe_allow_html=True)

        # 4 cards (layout wide)
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            st.metric("📦 Total Jenis Barang", total_barang)
        with c2:
            st.metric("💰 Nilai Inventaris", f"Rp {nilai_total:,.0f}")
        with c3:
            st.metric("🧾 Transaksi Tercatat", len(st.session_state.riwayat_transaksi))
        with c4:
            st.metric("⚠️ Stok Kritis (<10)", barang_kritis, delta=barang_kritis, delta_color="inverse")

        st.markdown("---")
        
        c_left, c_right = st.columns(2, gap="large")
        with c_left:
            st.subheader("Daftar Barang dengan Stok Terendah")

            if not st.session_state.stok.empty:
                stok_df = st.session_state.stok.copy()
                stok_df["Jumlah Stok"] = pd.to_numeric(stok_df["Jumlah Stok"], errors="coerce").fillna(0)
                stok_df["Harga Satuan"] = pd.to_numeric(stok_df["Harga Satuan"], errors="coerce").fillna(0)
                #HITUNG TOTAL NILAI INVENTARIS
                stok_df["Nilai Aset"] = stok_df["Jumlah Stok"] * stok_df["Harga Satuan"]
                nilai_total = stok_df["Nilai Aset"].sum()
    
            #LANJUTKAN DENGAN MENAMPILKAN DATAFRAME STOK RENDAH
                st.dataframe(
                    stok_df.sort_values("Jumlah Stok").head(15)[["Daftar Barang", "Jumlah Stok", "Satuan"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.metric("Total Nilai Inventaris (Total Aset)", "Rp 0") # Tampilkan 0 jika stok kosong
                st.info("Belum ada data barang.")
                


    # ---------- DAFTAR BARANG (dengan search & gambar) ----------
    elif st.session_state.page == "Daftar Barang":
        st.markdown('<h1 class="main-title">Daftar Barang</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Cari dan lihat detail stok barang Anda</p>', unsafe_allow_html=True)

        if st.session_state.get("show_delete_confirmation", False):
            st.warning("Apakah Anda yakin ingin menghapus barang ini? Tindakan ini tidak dapat dibatalkan.")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("Ya, Hapus", key="confirm_delete", use_container_width=True):
                    delete_barang(st.session_state.delete_id)
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_id = None
                    safe_rerun()
            with col_cancel:
                if st.button("Batal", key="cancel_delete", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_id = None
                    safe_rerun()

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
                cols_row = st.columns(ncols, gap="large") 
                for c in range(ncols):
                    idx = r * ncols + c
                    if idx < len(items):
                        row = items.loc[idx]
                        id_barang_value = row.get('id_barang') or row.get('id')
                        kode_barcode_value = row.get('kode_barcode')
                        unique_key = f"{id_barang_value}_{idx}"
                        with cols_row[c]:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            gambar_url = str(row.get("Gambar", "")).strip()
                            
                        
                            st.markdown(f"""
                            <div style="
                                width: 100%; 
                                height: 350px; 
                                overflow: hidden; 
                                border-radius: 10px; 
                                margin-bottom: 12px;
                                background-color: #e08484; 
                                position: relative;">
                                <img src="{gambar_url}" 
                                     style="width: 100%; height: 100%; object-fit: cover; object-position: center;" 
                                     onerror="this.onerror=null; this.src='{gambar_url}';">
                            </div>
                            """, unsafe_allow_html=True)          
                                          
                            st.markdown(f"<h4>{row['Daftar Barang']}</h4>", unsafe_allow_html=True)
                            
                            stok_raw = row.get("Jumlah Stok", 0)
                            satuan = row.get("Satuan", "")
                            harga_raw = row.get("Harga Satuan", 0)

                            # Konversi numerik
                            harga_float = pd.to_numeric(harga_raw, errors='coerce')
                            stok_float = pd.to_numeric(stok_raw, errors='coerce')

                            # WAJIB ADA: Definisikan 'safe' (int/0 jika data kotor/NaN)
                            harga_safe = int(harga_float) if pd.notna(harga_float) else 0
                            stok_safe = int(stok_float) if pd.notna(stok_float) else 0

                            st.markdown(f"<p>Stok: {stok_safe} {satuan}<br>Harga: Rp {harga_safe:,}</p>", unsafe_allow_html=True)

                            # --- FITUR EDIT DAN HAPUS (Hanya Atasan) ---
                            if st.session_state.user_role == "atasan":
                                col_edit, col_delete = st.columns(2)
                                with col_edit:
                                    # Menggunakan ID sebagai key
                                    if st.button("✏️ Edit", key=f"edit_{unique_key}", use_container_width=True):
                                    # ... logika edit ..
                                        st.session_state.edit_id = id_barang_value 
                                        st.session_state.page = "edit_barang" 
                                        safe_rerun()
                                with col_delete:
                                    # Perbaiki key di tombol Hapus
                                    if st.button("🗑️ Hapus", key=f"delete_{unique_key}", use_container_width=True): 
                                    # ... logika hapus Anda ...
                                        st.session_state.delete_id = id_barang_value 
                                        st.session_state.show_delete_confirmation = True
                                        safe_rerun()    
                                  
                            st.markdown('</div>', unsafe_allow_html=True)

# ---------- TRANSAKSI (DENGAN KAMERA SCANNER) ----------
    elif st.session_state.page == "transaksi":
        st.markdown('<h1 class="main-title">Transaksi Barang</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Scan barcode menggunakan kamera untuk mencatat transaksi</p>', unsafe_allow_html=True)

        col1, col2 = st.columns([1.2, 1], gap="large") 
        
        barang_data = None
        scan_result = None

        with col1:
            
            # 1. KAMERA LIVE SCANNER (Prioritas 1)

            st.subheader("📷 Ambil Foto Barcode")
        
        # Tombol kamera untuk ambil foto
            camera_image = st.camera_input("Klik untuk ambil foto barcode", key="camera_input")
        
            scan_result_camera = None
            if camera_image is not None:
                try:
                    # Proses gambar dari kamera
                    image = Image.open(camera_image)
                    img_np = np.array(image.convert('RGB')) 
                    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                    decoded_objects = decode(img_gray)

                    if decoded_objects:
                        scan_result_camera = decoded_objects[0].data.decode("utf-8")
                        st.success(f"🎉 Barcode Terdeteksi dari Foto: **{scan_result_camera}**")
                    
                    # Tampilkan gambar dengan kotak hijau di sekitar barcode (opsional)
                        for obj in decoded_objects:
                            points = obj.polygon
                            if len(points) > 4:
                                hull = cv2.convexHull(np.array([p for p in points], dtype=np.float32))
                                cv2.polylines(img_np, [np.int32(hull)], True, (0, 255, 0), 3)
                            else:
                                cv2.polylines(img_np, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 3)
                            cv2.putText(img_np, scan_result_camera, (obj.rect.left, obj.rect.top - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Tampilkan gambar hasil
                        st.image(img_np, caption="Foto dengan Barcode Terdeteksi", use_column_width=True)
                    else:
                        st.warning("⚠️ Tidak ada barcode yang terdeteksi di foto ini. Coba ambil foto lagi dengan pencahayaan baik.")
                    
                except Exception as e:
                    st.error(f"Gagal memproses foto: {e}")
                
            # 2. UPLOAD GAMBAR BARCODE (Prioritas 2)
            # ----------------------------------------------------
            st.markdown("---")
            st.subheader("🖼️ Atau Upload Gambar Barcode")
            uploaded_file = st.file_uploader("Pilih gambar barcode (.jpg/.png)", type=['jpg', 'jpeg', 'png'])

            scan_result_upload = None
            if uploaded_file is not None:
                # Membaca dan memproses gambar yang diunggah
                try:
                    image = Image.open(io.BytesIO(uploaded_file.read()))
                    img_np = np.array(image.convert('RGB')) 
                    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                    decoded_objects = decode(img_gray)
                    
                    if decoded_objects:
                        scan_result_upload = decoded_objects[0].data.decode("utf-8")
                        st.success(f"Barcode dari Gambar Terdeteksi: **{scan_result_upload}**")
                    else:
                        st.warning("⚠️ Tidak ada barcode yang terdeteksi di gambar ini.")
                        
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")

            # ----------------------------------------------------
            # 3. KONSOLIDASI HASIL SCAN (Penentuan Prioritas)
            # ----------------------------------------------------
            kode_barcode_final = scan_result_camera or scan_result_upload
                     
            # ----------------------------------------------------
            # 4. INPUT MANUAL (Prioritas 3 / Paling Rendah)
            # ----------------------------------------------------
            st.markdown("---")
            manual_code = st.text_input("Atau Masukkan Kode Manual", 
                                        value=kode_barcode_final if kode_barcode_final else "", 
                                        placeholder="Ketik kode disini...",
                                        key="manual_input_code")
            
            # Jika semua scan kosong, pakai manual
            if not kode_barcode_final:
                kode_barcode_final = manual_code
            
            # ----------------------------------------------------
            # 5. PENCARIAN & TAMPILAN DATA BARANG
            # ----------------------------------------------------
            if kode_barcode_final:
                st.info(f"Kode Diproses: **{kode_barcode_final}**")
                
                # CARI DI DATABASE (Sama seperti sebelumnya)
                if "kode_barcode" in st.session_state.stok.columns:
                    df_match = st.session_state.stok[st.session_state.stok["kode_barcode"] == kode_barcode_final]
                    
                    if not df_match.empty:
                        barang_data = df_match.iloc[0]
                        st.success(f"✅ Barang Ditemukan: **{barang_data['Daftar Barang']}**")
                        
                        harga_disp = int(pd.to_numeric(barang_data['Harga Satuan'], errors='coerce') or 0)
                        st.markdown(f"""
                        <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; border: 1px solid #00C8A8;">
                            <h4 style="margin:0;">Sisa Stok: {barang_data['Jumlah Stok']} {barang_data['Satuan']}</h4>
                            <p style="margin:0;">Harga: Rp {harga_disp:,}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Barang dengan kode '{kode_barcode_final}' tidak ditemukan di database.")
                else:
                    st.warning("⚠️ Kolom 'kode_barcode' belum ada di data stok.")
           
        with col2:
            # FORM INPUT TRANSAKSI (HANYA MUNCUL JIKA BARANG DITEMUKAN)
            if barang_data is not None:
                with st.form("form_transaksi_final"):
                    st.subheader("Detail Transaksi")
                    
                    # Tampilkan nama barang (readonly)
                    st.text_input("Nama Barang", value=barang_data['Daftar Barang'], disabled=True)
                    
                    # Input Jenis & Jumlah
                    jenis = st.radio("Jenis Transaksi", ["Masuk", "Keluar"], horizontal=True)
                    jumlah = st.number_input(f"Jumlah ({barang_data['Satuan']})", min_value=1, value=1)
                    tanggal = st.date_input("Tanggal", datetime.now().date())
                    
                    submitted = st.form_submit_button("Simpan Transaksi", use_container_width=True)
                
                # LOGIKA SIMPAN
                if submitted:
                    try:
                        # Ambil data
                        barang_id = barang_data["id_barang"] # Pastikan id_barang ada
                        stok_lama = int(pd.to_numeric(barang_data["Jumlah Stok"], errors="coerce") or 0)
                        harga = int(pd.to_numeric(barang_data["Harga Satuan"], errors="coerce") or 0)
                        nilai = jumlah * harga

                        # Hitung Stok Baru
                        if jenis == "Masuk":
                            stok_baru = stok_lama + jumlah
                        else: # Keluar
                            if jumlah > stok_lama:
                                st.error(f"❌ Stok kurang! Sisa: {stok_lama}")
                                st.stop()
                            stok_baru = stok_lama - jumlah

                        # Payload untuk Supabase
                        payload_t = {
                            "tanggal": tanggal.strftime("%Y-%m-%d"),
                            "id_barang": barang_id, # ID Barang (Foreign Key)
                            "nama_barang": barang_data["Daftar Barang"],
                            "jenis": jenis,
                            "jumlah": int(jumlah),
                            "satuan": barang_data["Satuan"],
                            "nilai": float(nilai)
                        }
                        
                        # Eksekusi Database
                        with st.spinner("Menyimpan..."):
                            # Pastikan tabel riwayat_transaksi memiliki kolom 'id' sebagai Primary Key (Identity)
                            # dan kolom 'id_barang' BUKAN Primary Key.
                            supabase.table("riwayat_transaksi").insert(payload_t).execute()
                            supabase.table("daftar_barang").update({"jumlah_stok": stok_baru}).eq("id_barang", barang_id).execute()
                        
                        st.success("Transaksi Berhasil Disimpan!")
                        time.sleep(1)
                        load_stok_from_supabase_VFINAL()
                        load_riwayat_from_supabase()
                        safe_rerun()

                    except Exception as e:
                        st.error(f"Gagal menyimpan: {e}")
            
            else:
                # Tampilan Default (Instruksi) jika belum ada barang discan
                st.info("👈 Arahkan kamera ke barcode barang atau ketik kode manual di sebelah kiri.")
                
                # Tampilkan Riwayat Singkat
                st.markdown("### 📜 Riwayat Terakhir")
                if not st.session_state.riwayat_transaksi.empty:
                    st.dataframe(
                        st.session_state.riwayat_transaksi.head(5)[['Tanggal', 'Barang', 'Jenis', 'Jumlah']], 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.write("Belum ada riwayat transaksi.")

    # ---------- FITUR BARU: TAMBAH BARANG (Hanya Atasan) ----------
    elif st.session_state.page == "tambah_barang":
        
        # Keamanan ganda
        if st.session_state.user_role != "atasan":
            st.error("Anda tidak memiliki izin untuk mengakses halaman ini.")
            st.stop()
            
        st.markdown('<h1 class="main-title">Tambah Barang Baru</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Isi form berikut ini</p>', unsafe_allow_html=True)

        barcode_placeholder = st.empty()

        with st.form("form_tambah_barang", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                nama_barang = st.text_input("Nama Barang", placeholder="Contoh: Kain Katun")
                jumlah_stok = st.number_input("Jumlah Stok Awal", min_value=0, value=0)
            with col2:
                # Perubahan: Satuan menggunakan selectbox dari list global SATUAN_OPTIONS
                satuan = st.selectbox("Satuan", SATUAN_OPTIONS, index=None, placeholder="Pilih satuan...")
                harga_satuan = st.text_input("Harga Satuan (Rp)")
                gambar_url = st.text_input("URL Gambar", placeholder="https://.../gambar.jpg")
            
            kode_barcode = st.text_input("Kode Barcode", placeholder="Contoh: LGT-001")

            #GENERATOR BARCODE
            barcode_bytes = None
            if kode_barcode:
                barcode_bytes = generate_barcode_image(kode_barcode)
            
            if barcode_bytes:
                st.session_state['current_barcode_bytes'] = barcode_bytes
                st.session_state['current_barcode_code'] = kode_barcode
            else:
            # Kosongkan jika kode barcode dihapus
                st.session_state['current_barcode_bytes'] = None
                st.session_state['current_barcode_code'] = None

            submitted = st.form_submit_button("Simpan Barang", use_container_width=True)

# TAMPILAN DAN DOWNLOAD BARCODE (DI LUAR FORM!)
        # ------------------------------------------------------------------
        if st.session_state.get('current_barcode_bytes') and st.session_state.get('current_barcode_code'):
            b_bytes = st.session_state['current_barcode_bytes']
            b_code = st.session_state['current_barcode_code']
            
            # Gunakan placeholder untuk menampilkan di posisi atas
            with barcode_placeholder.container():
                st.markdown("---")
                st.markdown("### 🏷️ Pratinjau Barcode yang Akan Dibuat")
                
                # Konversi bytes ke format Base64 agar Streamlit bisa menampilkannya
                base64_img = base64.b64encode(b_bytes).decode('utf-8')
                
                st.markdown(f'''
                <div style="border: 1px solid #00C8A8; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{base64_img}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;">
                </div>
                ''', unsafe_allow_html=True)
                
                # Tombol DOWNLOAD sekarang di luar form, jadi AMAN!
                st.download_button(
                    label=f"⬇️ Unduh Barcode '{b_code}' (Wajib Dicetak)",
                    data=b_bytes,
                    file_name=f"barcode_{b_code}.png",
                    mime="image/png",
                    use_container_width=True,
                    key="download_barcode_final"
                )
                st.markdown("---")
                
        # ------------------------------------------------------------------
        # LOGIKA PENYIMPANAN DATA (Jika submitted)
        # ------------------------------------------------------------------
        if submitted:
            if not nama_barang or not satuan:
                st.error("Nama Barang dan Satuan wajib diisi!")
            else:
                try:
                    # ... (Logika Cek Duplikat dan Simpan ke Supabase tetap sama) ...
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
                            # Pastikan konversi harga aman
                            "harga_satuan":int((harga_satuan.replace(',', '').replace('.', '') if harga_satuan else '0')), 
                            "gambar_url": gambar_url,
                            "kode_barcode": kode_barcode.strip() 
                        }
                    
                        with st.spinner("Menambahkan barang..."):
                            supabase.table("daftar_barang").insert(payload).execute()
                        
                        st.success(f"✅ Barang '{nama_barang}' berhasil ditambahkan!")

# --- OTOMATIS DOWNLOAD BARCODE DI SINI ---
                        if kode_barcode and st.session_state.get('current_barcode_bytes'):
                            
                            b_bytes = st.session_state['current_barcode_bytes']
                            b_code = st.session_state['current_barcode_code']
                            
                            st.info(f"Barcode untuk '{b_code}' siap diunduh.")

# Tombol DOWNLOAD diletakkan di sini, di luar form, setelah success
                            st.download_button(
                                label=f"⬇️ KLIK UNTUK UNDUH BARCODE '{b_code}' SEKARANG", 
                                data=b_bytes,
                                file_name=f"barcode_{b_code}.png",
                                mime="image/png",
                                use_container_width=True,
                                key="download_after_submit" # Ganti key agar unik
                            )
                        
                        # Refresh data
                        load_stok_from_supabase_VFINAL()
                        
                        # Tombol Pindah Halaman Manual (tetap ada)
                        if st.button("Lanjutkan ke Daftar Barang"):
                            # Hapus state barcode agar tidak muncul di load berikutnya
                            if 'current_barcode_bytes' in st.session_state:
                                 del st.session_state['current_barcode_bytes']
                            go_to_page("Daftar Barang")
                            
                except Exception as e:
                    st.error(f"Gagal menambahkan barang: {e}")
                    st.error("PASTIKAN RLS (ROW LEVEL SECURITY) DI SUPABASE SUDAH DIMATIKAN UNTUK TABEL INI.")
                            
    # ---------- FITUR BARU: 
    # EDIT BARANG (Hanya Atasan) ----------
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

        load_stok_from_supabase_VFINAL()
        

        # Ambil data barang yang akan diedit
        try: 
            barang_data = st.session_state.stok[st.session_state.stok["id"] == barang_id].iloc[0]
        except IndexError:
            st.error("Data barang tidak ditemukan.")
            st.session_state.edit_id = None
            go_to_page("Daftar Barang")
            st.stop()
        except Exception as e:
            st.error(f"Error tak terduga: {e}")
            st.session_state.edit_id = None
            go_to_page("Daftar Barang")
            st.stop()

        st.markdown(f'<h1 class="main-title">Edit Barang: {barang_data["Daftar Barang"]}</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Perbarui detail barang Anda (Halaman ini hanya untuk Atasan)</p>', unsafe_allow_html=True)

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
            kode_barcode_baru = st.text_input("Kode Barcode", value=barang_data.get("kode_barcode", ""), placeholder="Contoh: LGT-001")
            
            submitted = st.form_submit_button("Simpan Perubahan", use_container_width=True)

        barcode_edit_bytes = None
        current_code = barang_data.get("kode_barcode", "") # Ambil kode yang tersimpan
        
        if current_code:
            barcode_edit_bytes = generate_barcode_image(current_code)
            
            if barcode_edit_bytes:
                st.markdown("---")
                st.markdown("### 🏷️ Barcode Tersimpan (Dapat Diunduh Kapan Saja)")
                
                # Tampilkan Pratinjau
                base64_img = base64.b64encode(barcode_edit_bytes).decode('utf-8')
                st.markdown(f'''
                <div style="border: 1px solid #00C8A8; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.1);">
                    <img src="data:image/png;base64,{base64_img}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;">
                </div>
                ''', unsafe_allow_html=True)
                
                # Tombol Download Permanen
                st.download_button(
                    label=f"⬇️ Unduh Ulang Barcode '{current_code}'",
                    data=barcode_edit_bytes,
                    file_name=f"barcode_{current_code}_regen.png",
                    mime="image/png",
                    use_container_width=True,
                    key="download_barcode_edit"
                )           

        if submitted:
            if not satuan_baru:
                st.error("Satuan wajib diisi!")
            else:
                try:
                    payload = {
                        "satuan": satuan_baru,
                        "harga_satuan": int(harga_satuan_baru),
                        "gambar_url": gambar_url_baru,
                        "kode_barcode": kode_barcode_baru.strip()
                    }
                    
                    with st.spinner(f"Memperbarui barang {barang_data['Daftar Barang']}..."):
                        # Update ke Supabase
                        supabase.table("daftar_barang").update(payload).eq("id_barang", barang_id).execute()
                    
                    st.success(f"Barang '{barang_data['Daftar Barang']}' berhasil diperbarui!")
                    time.sleep(1)
                    st.session_state.edit_id = None # Matikan edit mode
                    load_stok_from_supabase_VFINAL()
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
        st.markdown('<p class="sub-title">Unduh laporan dan lihat analisis data</p>', unsafe_allow_html=True)
        
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
            
            # Perubahan: Mengganti st.subheader dengan st.markdown berkelas CSS
            st.markdown('<h2 class="centered-subheader">Grafik Aktivitas Transaksi</h2>', unsafe_allow_html=True)
            
            riwayat_df["Tanggal"] = pd.to_datetime(riwayat_df["Tanggal"])
            transaksi_harian = riwayat_df.groupby(["Tanggal", "Jenis"])["Jumlah"].sum().reset_index()
            
            fig = px.bar(transaksi_harian, x="Tanggal", y="Jumlah", color="Jenis", 
                         title="", barmode="group", text_auto=True,
                         color_discrete_map={"Masuk": "#b89d99", "Keluar": "#f7b733"}) # Warna tema baru
            
            # Update layout agar cocok dengan tema
            fig.update_layout(
                plot_bgcolor="#cd7f59", 
                paper_bgcolor= "#ECB079",
                font_color="#231F1F", # Warna font baru
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