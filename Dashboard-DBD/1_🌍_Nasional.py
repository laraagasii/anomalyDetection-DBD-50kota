import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Dashboard DBD Nasional", page_icon="🌍", layout="wide")

# --- 1. HERO SECTION & ONBOARDING ---
st.title("🌍 Pantau & Deteksi DBD Indonesia")
st.markdown("""
Aplikasi **Spatio-Temporal Anomaly Detection** ini memfasilitasi pemantauan sebaran kasus Demam Berdarah Dengue (DBD). 
Gunakan menu navigasi di sebelah kiri untuk melihat data dari skala Nasional, merayap turun ke Provinsi Sumatera Barat, 
hingga deteksi anomali di tingkat Kecamatan pada 50 Kota menggunakan *Machine Learning*.
""")

with st.expander("📖 Panduan Singkat Penggunaan Dashboard (Klik untuk membuka)"):
    st.markdown("""
    *   **Tab Nasional:** Memberikan gambaran besar tren kasus DBD per provinsi di Indonesia.
    *   **Tab Sumatera Barat:** Fokus visualisasi pada distribusi kasus antar Kabupaten/Kota di Sumbar.
    *   **Tab 50 Kota Anomali:** Merupakan inti dari sistem cerdas ini. Sistem akan menandai kecamatan anomali dengan titik peringatan.
    """)
st.markdown("---")

# --- 2. LOGIKA PATH ANTI-ERROR ---
base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_indonesia_clean_long.csv')

# MENGGUNAKAN FILE JSON PROVINSI BARU
geo_path = os.path.join(base_path, 'indonesia_prov.json')

@st.cache_data
def load_data_nasional():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r') as f:
        geo = json.load(f)
    return df, geo

try:
    df_indo, geo_indo = load_data_nasional()

    
    # Tambahin baris ini sementara buat ngintip struktur JSON-nya
    st.write("Melihat struktur JSON:", geo_indo['features'][0]['properties'])
    
    # Menyamakan format teks ke Title Case ("Sumatera Barat") sesuai JSON
    df_indo['Provinsi'] = df_indo['Provinsi'].str.title()
    # Pengecualian untuk DKI Jakarta karena singkatan
    df_indo['Provinsi'] = df_indo['Provinsi'].replace('Dki Jakarta', 'DKI Jakarta')
    
    kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_indo.columns else 'Kasus'
    
    # --- 3. FILTER (DROPDOWN) & KPI CARDS ---
    col_filter, col_empty = st.columns([1, 2])
    with col_filter:
        tahun_list = sorted(df_indo['Tahun'].unique(), reverse=True)
        tahun = st.selectbox("🗓️ Pilih Tahun Pantauan:", tahun_list)
    
    df_year = df_indo[df_indo['Tahun'] == tahun]
    
    total_kasus = df_year[kolom_kasus].sum()
    prov_tertinggi = df_year.loc[df_year[kolom_kasus].idxmax()]
    
    st.markdown("### 📌 *Quick Insight*")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Kasus Nasional", value=f"{total_kasus:,.0f}")
    col2.metric(label="Provinsi Kasus Tertinggi", value=prov_tertinggi['Provinsi'])
    col3.metric(label="Jumlah di Provinsi Tertinggi", value=f"{prov_tertinggi[kolom_kasus]:,.0f} Kasus")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. VISUALISASI PETA ---
    st.subheader(f"Peta Intensitas DBD Tahun {tahun}")
    
    fig = px.choropleth(
        df_year, 
        geojson=geo_indo, 
        locations='Provinsi', 
        # INI KUNCI UTAMANYA: Mengambil data dari key "PROVINSI" di JSON kamu[cite: 4]
        featureidkey="properties.PROVINSI", 
        color=kolom_kasus,
        color_continuous_scale="YlOrRd",
        hover_name='Provinsi',
        hover_data={kolom_kasus: True, 'Provinsi': False} 
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
    )
    fig.update_geos(fitbounds="locations", visible=False)
    
    with st.container():
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error: {e}. Pastikan file 'indonesia_prov.json' sudah diupload.")

st.sidebar.markdown("---")
st.sidebar.caption("Proyek Akhir Big Data - Informatika UNAND")