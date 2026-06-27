import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Dashboard DBD Nasional", page_icon="🌍", layout="wide")

st.title("🌍 Peta Sebaran Kasus DBD: Nasional")
st.write("Visualisasi Spasio-Temporal Tingkat Provinsi - Informatika UNAND")
st.markdown("---")

# --- LOGIKA PATH ANTI-ERROR ---
base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_indonesia_clean_long.csv')
geo_path = os.path.join(base_path, 'all_kabkota_ind.geojson')

@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r') as f:
        geo = json.load(f)
    return df, geo

try:
    df_indo, geo_indo = load_data()
    
    # Cek dinamis nama kolom jumlah kasus
    kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_indo.columns else 'Kasus'
    
    tahun = st.slider("Pilih Tahun:", int(df_indo['Tahun'].min()), int(df_indo['Tahun'].max()), int(df_indo['Tahun'].max()))
    df_year = df_indo[df_indo['Tahun'] == tahun]
    
    fig = px.choropleth(
        df_year, 
        geojson=geo_indo, 
        locations='Provinsi', 
        featureidkey="properties.prov_name", 
        color=kolom_kasus,
        color_continuous_scale="YlOrRd", 
        title=f"Sebaran Nasional Tahun {tahun}"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error: {e}. Gagal membaca data di path: {csv_path} atau {geo_path}")