import streamlit as st
import pandas as pd
import datetime
# from PIL import Image
# import io
# import base64
import requests
# import json
# import os
from collections import Counter # Untuk menghitung frekuensi

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Detak Medis",
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
.diagnosis-result {
    white-space: pre-wrap;
    background-color: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    font-family: monospace;
}
.doctor-card {
    background: #d1ecf1;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #17a2b8;
    margin-bottom: 1rem;
}
.poli-card {
    background: #e2e3e5;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #6c757d;
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

# Base URL API
BASE_URL = "http://127.0.0.1:8000"

# Fungsi untuk fetch data poli
@st.cache_data
def fetch_poli_data():
    try:
        response = requests.get(f"{BASE_URL}/poli")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching poli data: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error fetching poli data: {e}")
        return []

# Fungsi untuk fetch data dokter
@st.cache_data
def fetch_doctor_data():
    try:
        response = requests.get(f"{BASE_URL}/doctor")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching doctor data: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error fetching doctor data: {e}")
        return []

# Fungsi untuk fetch data pasien dari API
@st.cache_data
def fetch_patient_api_data():
    try:
        response = requests.get(f"{BASE_URL}/auth/patient")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching patient data from API: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error while fetching patient data: {e}")
        return []

# Fungsi untuk memproses dan memuat data pasien
@st.cache_data
def load_patient_data():
    api_data = fetch_patient_api_data()
    if api_data:
        transformed_data = []
        for patient in api_data:
            transformed_data.append({
                "id": patient.get("id"),
                "name": patient.get("name"),
                "contact": patient.get("email"),
                "created_at": patient.get("created_at")
            })
        if transformed_data:
            return pd.DataFrame(transformed_data)
    return pd.DataFrame(columns=["id", "name", "contact", "created_at"])


# Fungsi untuk fetch dokter berdasarkan poli
@st.cache_data
def fetch_doctors_by_poli(poli_id):
    try:
        response = requests.get(f"{BASE_URL}/doctor/poli/{poli_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching doctors by poli: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return []

# Fungsi untuk fetch poli berdasarkan ID
@st.cache_data
def fetch_poli_by_id(poli_id):
    try:
        response = requests.get(f"{BASE_URL}/poli/{poli_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching poli by ID: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

# Fungsi untuk fetch data diagnosis per pasien
@st.cache_data
def fetch_diagnoses_data(patient_id):
    if patient_id is None:
        return []
    try:
        response = requests.get(f"{BASE_URL}/diagnoses/patient/{patient_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return []
        else:
            st.error(f"Error fetching diagnoses data for patient {patient_id}: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error fetching diagnoses for patient {patient_id}: {e}")
        return []

# Fungsi untuk fetch semua data diagnosis (untuk total konsultasi dan grafik dashboard)
@st.cache_data
def fetch_all_diagnoses_data():
    try:
        response = requests.get(f"{BASE_URL}/diagnoses")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching all diagnoses data: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error fetching all diagnoses: {e}")
        return []

# Fungsi BARU untuk fetch semua data gambar medis
@st.cache_data
def fetch_all_medical_images_data():
    try:
        response = requests.get(f"{BASE_URL}/medical-images")
        if response.status_code == 200:
            return response.json() # Mengharapkan list dari semua record gambar medis
        else:
            st.error(f"Error fetching all medical images data: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error fetching all medical images: {e}")
        return []


# Fungsi untuk memotong deskripsi
def truncate_description(text, max_length=150):
    if not isinstance(text, str):
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

# Header utama
st.markdown("""
<div class="main-header">
    <h1>🏥 Dashboard Detak Medis</h1>
</div>
""", unsafe_allow_html=True)

# Load data pasien
patients_df = load_patient_data()

# Sidebar untuk navigasi
st.sidebar.title("📋 Menu Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    ["📊 Dashboard Utama", "👥 Daftar Pasien", "🩺 History Konsultasi", "🏥 Daftar Poli & Dokter"]
)

if menu == "📊 Dashboard Utama":
    st.title("Dashboard Utama")

    poli_data = fetch_poli_data()
    doctor_data = fetch_doctor_data()
    all_diagnoses_list = fetch_all_diagnoses_data() # Untuk metrik total dan grafik spesialisasi
    total_real_consultations = len(all_diagnoses_list)
    
    all_medical_images_list = fetch_all_medical_images_data() # Untuk grafik distribusi gambar per pasien

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #1f77b4;">👥 Total Pasien</h3>
            <h1 style="color: #1f77b4; margin: 0;">{len(patients_df) if not patients_df.empty else 0}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff7f0e;">🩺 Total Diagnosis</h3>
            <h1 style="color: #ff7f0e; margin: 0;">{total_real_consultations}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2ca02c;">🏥 Jumlah Poli</h3>
            <h1 style="color: #2ca02c; margin: 0;">{len(poli_data)}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #d62728;">👨‍⚕️ Total Dokter</h3>
            <h1 style="color: #d62728; margin: 0;">{len(doctor_data)}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Persiapan DataFrame untuk grafik dari all_diagnoses_list
    if all_diagnoses_list:
        diagnoses_df_for_charts = pd.DataFrame(all_diagnoses_list)
    else:
        diagnoses_df_for_charts = pd.DataFrame()

    # Persiapan DataFrame untuk grafik dari all_medical_images_list
    if all_medical_images_list:
        medical_images_df_for_charts = pd.DataFrame(all_medical_images_list)
    else:
        medical_images_df_for_charts = pd.DataFrame()


    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚕️ Frekuensi Diagnosis per Spesialisasi Dokter")
        if not diagnoses_df_for_charts.empty and 'related_doctors' in diagnoses_df_for_charts.columns:
            specialities_from_diagnoses = []
            for doctors_list in diagnoses_df_for_charts['related_doctors'].dropna():
                if isinstance(doctors_list, list):
                    for doctor in doctors_list:
                        if isinstance(doctor, dict) and doctor.get('speciality'):
                            specialities_from_diagnoses.append(doctor.get('speciality'))
            
            if specialities_from_diagnoses:
                speciality_counts = pd.Series(Counter(specialities_from_diagnoses)).sort_values(ascending=False)
                top_n = 10
                if len(speciality_counts) > top_n:
                    st.bar_chart(speciality_counts.head(top_n))
                    st.caption(f"Menampilkan Top {top_n} spesialisasi. Total jenis spesialisasi: {len(speciality_counts)}")
                else:
                    st.bar_chart(speciality_counts)
            else:
                st.info("Tidak ada data spesialisasi dokter yang ditemukan dalam diagnosis.")
        else:
            st.info("Data diagnosis tidak tersedia atau format tidak sesuai untuk analisis spesialisasi.")

    with col2:
        st.subheader("🖼️ Distribusi Jumlah Konsultasi per Pasien")
        # Asumsi field 'patient_id' ada di response /medical-images
        # Sesuaikan 'patient_id_column_in_images' jika nama fieldnya berbeda
        patient_id_column_in_images = 'patient_id' 

        if not medical_images_df_for_charts.empty and patient_id_column_in_images in medical_images_df_for_charts.columns:
            try:
                # Hitung jumlah gambar medis per pasien
                images_per_patient = medical_images_df_for_charts[patient_id_column_in_images].value_counts()
                
                # Hitung distribusi dari jumlah gambar tersebut
                distribution_of_images_counts = images_per_patient.value_counts().sort_index()
                
                if not distribution_of_images_counts.empty:
                    distribution_of_images_counts.index.name = "Jumlah Gambar Medis"
                    st.bar_chart(distribution_of_images_counts.rename("Jumlah Pasien"))
                    st.caption("Grafik menunjukkan berapa banyak pasien yang memiliki sejumlah gambar medis tertentu.")
                else:
                    st.info("Tidak ada data gambar medis yang valid untuk membuat distribusi per pasien.")
            except Exception as e:
                st.warning(f"Tidak dapat membuat grafik distribusi gambar medis per pasien: {e}.")
        else:
            st.info(f"Data gambar medis tidak memiliki kolom ('{patient_id_column_in_images}') yang diperlukan, atau data kosong.")


elif menu == "👥 Daftar Pasien":
    st.title("Daftar Pasien")

    if patients_df.empty:
        st.warning("Tidak ada data pasien yang berhasil dimuat dari API atau API tidak mengembalikan data.")
    else:
        search_term = st.text_input("🔍 Cari pasien (nama/ID):", "")

        filtered_patients = patients_df.copy()
        if search_term:
            search_df_patients = patients_df.copy()
            search_df_patients['name_search'] = search_df_patients['name'].astype(str).fillna('') if 'name' in search_df_patients.columns else pd.Series([''] * len(search_df_patients))
            search_df_patients['id_search'] = search_df_patients['id'].astype(str).fillna('') if 'id' in search_df_patients.columns else pd.Series([''] * len(search_df_patients))
            mask = (search_df_patients['name_search'].str.contains(search_term, case=False, na=False)) | \
                   (search_df_patients['id_search'].str.contains(search_term, case=False, na=False))
            filtered_patients = patients_df[mask]

        if not filtered_patients.empty:
            for idx, patient in filtered_patients.iterrows():
                created_at_display = patient.get('created_at', 'N/A')
                try:
                    dt_obj = datetime.datetime.fromisoformat(str(created_at_display).replace("Z", "+00:00"))
                    created_at_display = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass
                st.markdown(f"""
                <div class="patient-card">
                    <h4>👤 {patient.get('name', 'N/A')} (ID: {patient.get('id', 'N/A')})</h4>
                    <p><strong>Kontak (Email):</strong> {patient.get('contact', 'N/A')}</p>
                    <p><strong>Tanggal Daftar:</strong> {created_at_display}</p>
                </div>
                """, unsafe_allow_html=True)
        elif search_term:
             st.info("Tidak ada pasien yang ditemukan dengan kriteria pencarian tersebut.")

elif menu == "🩺 History Konsultasi":
    st.title("History Konsultasi Pasien")

    if patients_df.empty:
        st.warning("Data pasien tidak tersedia. Tidak dapat menampilkan history konsultasi.")
    else:
        if 'id' in patients_df.columns and 'name' in patients_df.columns:
            patients_df_for_select = patients_df.copy()
            patients_df_for_select['name_display'] = patients_df_for_select['name'].astype(str).fillna('Nama Tidak Tersedia')

            selected_patient_id = st.selectbox(
                "Pilih Pasien:",
                options=patients_df_for_select['id'].tolist(),
                format_func=lambda x: f"{x} - {patients_df_for_select[patients_df_for_select['id']==x]['name_display'].iloc[0] if not patients_df_for_select[patients_df_for_select['id']==x].empty else 'N/A'}"
            )

            if selected_patient_id is not None:
                patient_info_series = patients_df[patients_df['id'] == selected_patient_id]
                if not patient_info_series.empty:
                    patient_info = patient_info_series.iloc[0]

                    created_at_display_hist = patient_info.get('created_at', 'N/A')
                    try:
                        dt_obj_hist = datetime.datetime.fromisoformat(str(created_at_display_hist).replace("Z", "+00:00"))
                        created_at_display_hist = dt_obj_hist.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pass

                    st.markdown(f"""
                    <div class="patient-card">
                        <h4>📋 Informasi Pasien</h4>
                        <p><strong>Nama:</strong> {patient_info.get('name', 'N/A')} | <strong>ID:</strong> {patient_info.get('id', 'N/A')}</p>
                        <p><strong>Kontak (Email):</strong> {patient_info.get('contact', 'N/A')}</p>
                        <p><strong>Tanggal Daftar:</strong> {created_at_display_hist}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.subheader("Riwayat Diagnosis Pasien")
                    diagnoses_data = fetch_diagnoses_data(selected_patient_id)

                    if diagnoses_data:
                        for record_idx, diagnosis_record in enumerate(diagnoses_data):
                            with st.container():
                                st.markdown(f"<div class='consult-card'>", unsafe_allow_html=True)
                                st.markdown(f"<h5>Diagnosis ke-{record_idx + 1}</h5>", unsafe_allow_html=True)

                                keluhan = diagnosis_record.get('query', 'Tidak ada data keluhan.')
                                st.markdown(f"<p><strong>Keluhan:</strong><br>{keluhan}</p>", unsafe_allow_html=True)

                                hasil_diagnosis = diagnosis_record.get('result', 'Tidak ada data hasil diagnosis.')
                                st.markdown(f"<p><strong>Hasil Diagnosis:</strong></p>", unsafe_allow_html=True)
                                st.markdown(f"<div class='diagnosis-result'>{hasil_diagnosis}</div>", unsafe_allow_html=True)

                                image_path_from_api = diagnosis_record.get('path')
                                if image_path_from_api:
                                    image_display_path = image_path_from_api

                                    with st.expander("🖼️ Lihat Gambar Terkait (klik untuk buka/tutup)", expanded=False):
                                        try:
                                            st.image(image_display_path, use_container_width=True)
                                        except Exception as e:
                                            st.error(f"Tidak dapat memuat gambar dari path: {image_display_path}. Error: {e}")
                                else:
                                    st.markdown("<p><em>Tidak ada gambar terkait untuk diagnosis ini.</em></p>", unsafe_allow_html=True)

                                st.markdown(f"</div>", unsafe_allow_html=True)
                                st.markdown("---")
                    else:
                        st.info(f"Tidak ada riwayat diagnosis yang ditemukan untuk pasien ID {selected_patient_id}.")
                else:
                    st.warning(f"Tidak dapat menemukan informasi untuk pasien ID {selected_patient_id}.")
            else:
                st.info("Silakan pilih pasien untuk melihat history konsultasi.")
        else:
            st.error("Format data pasien tidak sesuai. Kolom 'id' dan 'name' dibutuhkan untuk memilih pasien.")


elif menu == "🏥 Daftar Poli & Dokter":
    st.title("Daftar Poli & Dokter")
    poli_data = fetch_poli_data()
    doctor_data = fetch_doctor_data()

    if not poli_data:
        st.error("Tidak dapat mengambil data poli. Pastikan API server berjalan.")
    else:
        poli_options = ["Semua"] + [poli.get('name', f"Poli Tanpa Nama (ID: {poli.get('id')})") for poli in poli_data]
        selected_poli_name = st.selectbox("🏥 Filter berdasarkan Poli:", poli_options)

        active_poli_list = []
        if selected_poli_name == "Semua":
            active_poli_list = poli_data
        else:
            selected_poli_obj = next((p for p in poli_data if p.get('name', f"Poli Tanpa Nama (ID: {p.get('id')})") == selected_poli_name), None)
            if selected_poli_obj:
                active_poli_list = [selected_poli_obj]
            else:
                 st.error(f"Detail untuk poli '{selected_poli_name}' tidak ditemukan.")

        if not active_poli_list and selected_poli_name != "Semua":
            pass
        elif not active_poli_list and selected_poli_name == "Semua":
             st.info("Tidak ada data poli untuk ditampilkan.")
        else:
            for poli in active_poli_list:
                st.subheader(f"🏥 {poli.get('name', 'N/A')}")
                st.markdown(f"""
                <div class="poli-card">
                    <h4>📋 Informasi Poli</h4>
                    <p><strong>Nama:</strong> {poli.get('name', 'N/A')}</p>
                    <p><strong>Deskripsi:</strong> {truncate_description(poli.get('description', ''))}</p>
                </div>
                """, unsafe_allow_html=True)

                current_poli_doctors = []
                if doctor_data:
                    current_poli_doctors = [doc for doc in doctor_data if doc.get('poli_id') == poli.get('id')]

                if current_poli_doctors:
                    st.write(f"**Dokter yang tersedia ({len(current_poli_doctors)} orang):**")
                    for doctor in current_poli_doctors:
                        schedule = doctor.get('practice_schedule', {})
                        schedule_days = ", ".join(schedule.get('days', []))
                        schedule_time = schedule.get('time', 'N/A')
                        schedule_note = schedule.get('note', '')
                        full_schedule = f"{schedule_days} ({schedule_time})"
                        if schedule_note:
                            full_schedule += f" - {schedule_note}"

                        st.markdown(f"""
                        <div class="doctor-card">
                            <h4>👨‍⚕️ {doctor.get('name', 'N/A')}</h4>
                            <p><strong>Spesialisasi:</strong> {doctor.get('speciality', 'N/A')}</p>
                            <p><strong>Profil:</strong> {truncate_description(doctor.get('profile', ''))}</p>
                            <p><strong>Jadwal Praktik:</strong> {full_schedule}</p>
                            <p><strong>Lokasi:</strong> {doctor.get('location', 'N/A')}</p>
                            <p><strong>Kontak:</strong> {doctor.get('contact_info', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Belum ada dokter terdaftar untuk poli ini atau data dokter tidak dapat dimuat.")
                if selected_poli_name == "Semua":
                    st.markdown("---")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🏥 <strong>Dashboard Detak Medis</strong></p>
    <p>📅 Last updated: {datetime.datetime.now().strftime("%d %B %Y")}</p>
</div>
""", unsafe_allow_html=True)