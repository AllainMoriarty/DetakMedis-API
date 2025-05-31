import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import io
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Rumah Sakit",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .patient-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .consult-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .doctor-card {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Data dummy untuk pasien
@st.cache_data
def load_patient_data():
    patients = [
        {
            "id": "P001",
            "nama": "Ahmad Wijaya",
            "umur": 45,
            "jenis_kelamin": "Laki-laki",
            "alamat": "Jl. Merdeka No. 123, Jakarta",
            "telepon": "081234567890",
            "tanggal_daftar": "2024-01-15"
        },
        {
            "id": "P002", 
            "nama": "Siti Nurhaliza",
            "umur": 32,
            "jenis_kelamin": "Perempuan",
            "alamat": "Jl. Sudirman No. 456, Bandung",
            "telepon": "081234567891",
            "tanggal_daftar": "2024-02-20"
        },
        {
            "id": "P003",
            "nama": "Budi Santoso",
            "umur": 28,
            "jenis_kelamin": "Laki-laki", 
            "alamat": "Jl. Gatot Subroto No. 789, Surabaya",
            "telepon": "081234567892",
            "tanggal_daftar": "2024-03-10"
        },
        {
            "id": "P004",
            "nama": "Maya Sari",
            "umur": 38,
            "jenis_kelamin": "Perempuan",
            "alamat": "Jl. Diponegoro No. 321, Yogyakarta", 
            "telepon": "081234567893",
            "tanggal_daftar": "2024-04-05"
        },
        {
            "id": "P005",
            "nama": "Rudi Hartono",
            "umur": 52,
            "jenis_kelamin": "Laki-laki",
            "alamat": "Jl. Ahmad Yani No. 654, Malang",
            "telepon": "081234567894", 
            "tanggal_daftar": "2024-05-12"
        }
    ]
    return pd.DataFrame(patients)

# Data dummy untuk history konsultasi
@st.cache_data
def load_consultation_data():
    consultations = [
        {
            "patient_id": "P001",
            "tanggal": "2024-05-28",
            "keluhan": "Nyeri dada dan sesak napas",
            "diagnosis": "Hipertensi ringan",
            "dokter": "Dr. Sarah Wijayanti, Sp.JP",
            "poli": "Kardiologi",
            "xray_status": "Ada",
            "tindakan": "Terapi obat antihipertensi",
            "catatan": "Kontrol tekanan darah rutin"
        },
        {
            "patient_id": "P001", 
            "tanggal": "2024-04-15",
            "keluhan": "Batuk berkepanjangan",
            "diagnosis": "Bronkitis kronis",
            "dokter": "Dr. Ahmad Fauzi, Sp.P",
            "poli": "Paru",
            "xray_status": "Ada",
            "tindakan": "Bronkodilator dan mukolitik",
            "catatan": "Hindari asap rokok"
        },
        {
            "patient_id": "P002",
            "tanggal": "2024-05-25", 
            "keluhan": "Mual dan muntah",
            "diagnosis": "Gastritis akut",
            "dokter": "Dr. Lisa Handayani, Sp.PD",
            "poli": "Penyakit Dalam",
            "xray_status": "Tidak ada",
            "tindakan": "Terapi simptomatik",
            "catatan": "Diet lunak dan teratur"
        },
        {
            "patient_id": "P003",
            "tanggal": "2024-05-20",
            "keluhan": "Nyeri punggung bawah",
            "diagnosis": "Lumbalgia",
            "dokter": "Dr. Bambang Susilo, Sp.OT",
            "poli": "Ortopedi",
            "xray_status": "Ada", 
            "tindakan": "Fisioterapi dan NSAID",
            "catatan": "Postur tubuh yang baik"
        },
        {
            "patient_id": "P004",
            "tanggal": "2024-05-18",
            "keluhan": "Pusing dan lemas",
            "diagnosis": "Anemia defisiensi besi",
            "dokter": "Dr. Maya Kusuma, Sp.PD",
            "poli": "Penyakit Dalam", 
            "xray_status": "Tidak ada",
            "tindakan": "Suplementasi besi",
            "catatan": "Konsumsi makanan kaya zat besi"
        },
        {
            "patient_id": "P005",
            "tanggal": "2024-05-30",
            "keluhan": "Nyeri sendi lutut",
            "diagnosis": "Osteoartritis",
            "dokter": "Dr. Rini Astuti, Sp.RM",
            "poli": "Rehabilitasi Medik",
            "xray_status": "Ada",
            "tindakan": "Fisioterapi dan analgetik",
            "catatan": "Olahraga ringan teratur"
        }
    ]
    return pd.DataFrame(consultations)

# Data dummy untuk poli dan dokter
@st.cache_data  
def load_doctor_data():
    doctors = [
        {
            "poli": "Kardiologi",
            "nama_dokter": "Dr. Sarah Wijayanti, Sp.JP",
            "jadwal": "Senin, Rabu, Jumat (08:00-12:00)",
            "pengalaman": "15 tahun",
            "spesialisasi": "Penyakit Jantung & Pembuluh Darah"
        },
        {
            "poli": "Kardiologi", 
            "nama_dokter": "Dr. Indra Gunawan, Sp.JP",
            "jadwal": "Selasa, Kamis, Sabtu (13:00-17:00)",
            "pengalaman": "12 tahun",
            "spesialisasi": "Intervensi Kardiologi"
        },
        {
            "poli": "Paru",
            "nama_dokter": "Dr. Ahmad Fauzi, Sp.P", 
            "jadwal": "Senin-Jumat (08:00-15:00)",
            "pengalaman": "18 tahun",
            "spesialisasi": "Penyakit Paru & Pernapasan"
        },
        {
            "poli": "Penyakit Dalam",
            "nama_dokter": "Dr. Lisa Handayani, Sp.PD",
            "jadwal": "Senin, Rabu, Jumat (09:00-16:00)", 
            "pengalaman": "10 tahun",
            "spesialisasi": "Penyakit Dalam Umum"
        },
        {
            "poli": "Penyakit Dalam",
            "nama_dokter": "Dr. Maya Kusuma, Sp.PD",
            "jadwal": "Selasa, Kamis (08:00-14:00)",
            "pengalaman": "8 tahun", 
            "spesialisasi": "Endokrinologi"
        },
        {
            "poli": "Ortopedi",
            "nama_dokter": "Dr. Bambang Susilo, Sp.OT",
            "jadwal": "Senin-Sabtu (10:00-16:00)",
            "pengalaman": "20 tahun",
            "spesialisasi": "Bedah Tulang & Sendi"
        },
        {
            "poli": "Rehabilitasi Medik",
            "nama_dokter": "Dr. Rini Astuti, Sp.RM", 
            "jadwal": "Selasa, Kamis, Sabtu (08:00-12:00)",
            "pengalaman": "7 tahun",
            "spesialisasi": "Fisioterapi & Rehabilitasi"
        },
        {
            "poli": "Neurologi",
            "nama_dokter": "Dr. Andi Pratama, Sp.N",
            "jadwal": "Rabu, Jumat (13:00-17:00)",
            "pengalaman": "14 tahun",
            "spesialisasi": "Penyakit Saraf"
        }
    ]
    return pd.DataFrame(doctors)

# Header utama
st.markdown("""
<div class="main-header">
    <h1>🏥 Dashboard Rumah Sakit</h1>
</div>
""", unsafe_allow_html=True)

# Load data
patients_df = load_patient_data()
consultations_df = load_consultation_data()
doctors_df = load_doctor_data()

# Sidebar untuk navigasi
st.sidebar.title("📋 Menu Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    ["📊 Dashboard Utama", "👥 Daftar Pasien", "🩺 History Konsultasi", "🏥 Daftar Poli & Dokter"]
)

if menu == "📊 Dashboard Utama":
    st.title("Dashboard Utama")
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1f77b4;">👥 Total Pasien</h3>
            <h1 style="color: #1f77b4; margin: 0;">{}</h1>
        </div>
        """.format(len(patients_df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ff7f0e;">🩺 Total Konsultasi</h3>
            <h1 style="color: #ff7f0e; margin: 0;">{}</h1>
        </div>
        """.format(len(consultations_df)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #2ca02c;">🏥 Jumlah Poli</h3>
            <h1 style="color: #2ca02c; margin: 0;">{}</h1>
        </div>
        """.format(doctors_df['poli'].nunique()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #d62728;">👨‍⚕️ Total Dokter</h3>
            <h1 style="color: #d62728; margin: 0;">{}</h1>
        </div>
        """.format(len(doctors_df)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grafik statistik
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribusi Pasien per Poli")
        poli_stats = consultations_df['poli'].value_counts()
        st.bar_chart(poli_stats)
    
    with col2:
        st.subheader("🔄 Konsultasi per Bulan")
        consultations_df['tanggal'] = pd.to_datetime(consultations_df['tanggal'])
        monthly_stats = consultations_df.groupby(consultations_df['tanggal'].dt.to_period('M')).size()
        st.line_chart(monthly_stats)

elif menu == "👥 Daftar Pasien":
    st.title("Daftar Pasien")
    
    # Filter dan pencarian
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Cari pasien (nama/ID):", "")
    with col2:
        gender_filter = st.selectbox("Filter Jenis Kelamin:", ["Semua", "Laki-laki", "Perempuan"])
    
    # Filter data
    filtered_patients = patients_df.copy()
    if search_term:
        filtered_patients = filtered_patients[
            (filtered_patients['nama'].str.contains(search_term, case=False)) |
            (filtered_patients['id'].str.contains(search_term, case=False))
        ]
    if gender_filter != "Semua":
        filtered_patients = filtered_patients[filtered_patients['jenis_kelamin'] == gender_filter]
    
    # Tampilkan daftar pasien
    for idx, patient in filtered_patients.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="patient-card">
                <h4>👤 {patient['nama']} (ID: {patient['id']})</h4>
                <p><strong>Umur:</strong> {patient['umur']} tahun | <strong>Jenis Kelamin:</strong> {patient['jenis_kelamin']}</p>
                <p><strong>Alamat:</strong> {patient['alamat']}</p>
                <p><strong>Telepon:</strong> {patient['telepon']} | <strong>Tanggal Daftar:</strong> {patient['tanggal_daftar']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if len(filtered_patients) == 0:
        st.info("Tidak ada pasien yang ditemukan dengan kriteria pencarian tersebut.")

elif menu == "🩺 History Konsultasi":
    st.title("History Konsultasi Pasien")
    
    # Pilih pasien
    selected_patient = st.selectbox(
        "Pilih Pasien:",
        options=patients_df['id'].tolist(),
        format_func=lambda x: f"{x} - {patients_df[patients_df['id']==x]['nama'].iloc[0]}"
    )
    
    if selected_patient:
        patient_info = patients_df[patients_df['id'] == selected_patient].iloc[0]
        st.markdown(f"""
        <div class="patient-card">
            <h4>📋 Informasi Pasien</h4>
            <p><strong>Nama:</strong> {patient_info['nama']} | <strong>ID:</strong> {patient_info['id']}</p>
            <p><strong>Umur:</strong> {patient_info['umur']} tahun | <strong>Jenis Kelamin:</strong> {patient_info['jenis_kelamin']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # History konsultasi untuk pasien terpilih
        patient_consultations = consultations_df[consultations_df['patient_id'] == selected_patient]
        
        if len(patient_consultations) > 0:
            st.subheader(f"📋 Riwayat Konsultasi ({len(patient_consultations)} kali)")
            
            for idx, consult in patient_consultations.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="consult-card">
                        <h4>🗓️ {consult['tanggal']} - {consult['poli']}</h4>
                        <p><strong>Dokter:</strong> {consult['dokter']}</p>
                        <p><strong>Keluhan:</strong> {consult['keluhan']}</p>
                        <p><strong>Diagnosis:</strong> {consult['diagnosis']}</p>
                        <p><strong>Tindakan:</strong> {consult['tindakan']}</p>
                        <p><strong>X-Ray:</strong> {"✅ Tersedia" if consult['xray_status'] == "Ada" else "❌ Tidak Ada"}</p>
                        <p><strong>Catatan:</strong> {consult['catatan']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Simulasi tampilan X-Ray (jika ada)
                    if consult['xray_status'] == "Ada":
                        with st.expander("🔍 Lihat X-Ray"):
                            st.info("📸 X-Ray image akan ditampilkan di sini dalam implementasi sesungguhnya")
                            st.text("Filename: xray_" + selected_patient + "_" + consult['tanggal'] + ".jpg")
        else:
            st.info("Belum ada riwayat konsultasi untuk pasien ini.")

elif menu == "🏥 Daftar Poli & Dokter":
    st.title("Daftar Poli & Dokter")
    
    # Filter berdasarkan poli
    poli_list = ["Semua"] + sorted(doctors_df['poli'].unique().tolist())
    selected_poli = st.selectbox("🏥 Filter berdasarkan Poli:", poli_list)
    
    # Filter data dokter
    if selected_poli == "Semua":
        filtered_doctors = doctors_df
    else:
        filtered_doctors = doctors_df[doctors_df['poli'] == selected_poli]
    
    # Grupkan berdasarkan poli
    for poli in filtered_doctors['poli'].unique():
        st.subheader(f"🏥 {poli}")
        poli_doctors = filtered_doctors[filtered_doctors['poli'] == poli]
        
        for idx, doctor in poli_doctors.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="doctor-card">
                    <h4>👨‍⚕️ {doctor['nama_dokter']}</h4>
                    <p><strong>Spesialisasi:</strong> {doctor['spesialisasi']}</p>
                    <p><strong>Pengalaman:</strong> {doctor['pengalaman']}</p>
                    <p><strong>Jadwal Praktik:</strong> {doctor['jadwal']}</p>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🏥 <strong>Dashboard Rumah Sakit</strong> | Dikembangkan dengan Streamlit</p>
    <p>📅 Last updated: {}</p>
</div>
""".format(datetime.datetime.now().strftime("%d %B %Y")), unsafe_allow_html=True)