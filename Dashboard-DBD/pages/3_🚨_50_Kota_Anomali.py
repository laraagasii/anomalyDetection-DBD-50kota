import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Deteksi Anomali 50 Kota", page_icon="🚨", layout="wide")

st.title("🚨 Deteksi Anomali DBD: 50 Kota")
st.markdown("---")

base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_50kota_anomali.csv')
geo_path = os.path.join(base_path, 'id1308_lima_puluh_kota.geojson')

@st.cache_data
def load_data_50kota():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    return df, geo

with st.spinner('Mendeteksi anomali...'):
    try:
        df_50kota, geo_50kota = load_data_50kota()
        
        # --- DEBUGGING: CEK NAMA YANG BELUM MATCH ---
        kec_csv = set(df_50kota['Kecamatan'].unique())
        kec_json = set([f['properties']['district'] for f in geo_50kota['features']])
        
        # --- MAPPING NAMA (SESUAIKAN DENGAN OUTPUT DEBUG DI BAWAH) ---
        # Contoh: kalau di GeoJSON namanya 'KEC. HARAU' dan di CSV 'HARAU', tambahkan di sini
        mapping_nama = {
            # 'HARAU': 'KEC. HARAU'  <-- tambahkan mapping kamu di sini
        }
        df_50kota['Kecamatan'] = df_50kota['Kecamatan'].replace(mapping_nama)
        
        kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_50kota.columns else 'Kasus'
        
        # --- TAB & DROPDOWN ---
        tab1, tab2 = st.tabs(["🗺️ Peta Spasial", "📈 Tren Temporal"])
        
        with tab1:
            # Dropdown tahun
            tahun_list = sorted(df_50kota['Tahun'].unique(), reverse=True)
            tahun = st.selectbox("🗓️ Pilih Tahun:", tahun_list)
            df_year = df_50kota[df_50kota['Tahun'] == tahun]
            
            fig_map = px.choropleth_mapbox(
                df_year, geojson=geo_50kota, locations='Kecamatan', 
                featureidkey="properties.district", color=kolom_kasus,
                color_continuous_scale="Reds", mapbox_style="carto-positron",
                center={"lat": -0.166, "lon": 100.65}, zoom=9.5
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Debugging info (hapus jika sudah rapi)
            if st.checkbox("Cek Nama yang Belum Match"):
                st.write("Nama di CSV tapi gaada di GeoJSON:", kec_csv - kec_json)
        
    except Exception as e:
        st.error(f"⚠️ Error: {e}")