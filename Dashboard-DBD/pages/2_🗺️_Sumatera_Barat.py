import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="DBD Sumatera Barat", page_icon="🗺️", layout="wide")

# --- UI Header ---
st.title("🗺️ Peta Sebaran Kasus DBD: Sumatera Barat")
st.markdown("Analisis spasial kasus DBD tingkat Kabupaten/Kota untuk wilayah Sumatera Barat.")
st.markdown("---")

base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_sumbar_clean_long.csv')
geo_path = os.path.join(base_path, 'all_kabkota_ind.geojson')

@st.cache_data
def load_data_sumbar():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    return df, geo

try:
    df_sumbar, geo_sumbar_raw = load_data_sumbar()
    
    # Preprocessing
    df_sumbar['Kab/Kota'] = df_sumbar['Kab/Kota'].str.upper()
    geo_sumbar = geo_sumbar_raw.copy()
    geo_sumbar['features'] = [f for f in geo_sumbar_raw['features'] if f['properties'].get('prov_name') == 'SUMATERA BARAT']
    
    kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_sumbar.columns else 'Kasus'
    
    # Sidebar Filter
    st.sidebar.header("Filter Data")
    tahun = st.sidebar.slider("Pilih Tahun:", int(df_sumbar['Tahun'].min()), int(df_sumbar['Tahun'].max()), int(df_sumbar['Tahun'].max()))
    df_year = df_sumbar[df_sumbar['Tahun'] == tahun]
    
    # KPI Metric Row
    col1, col2 = st.columns(2)
    max_row = df_year.loc[df_year[kolom_kasus].idxmax()]
    col1.metric("Total Kasus Sumbar", f"{df_year[kolom_kasus].sum():,.0f}")
    col2.metric("Tertinggi di", max_row['Kab/Kota'], f"{max_row[kolom_kasus]:,.0f} Kasus")

    # --- Peta Mapbox (Lebih Pro) ---
    fig = px.choropleth_mapbox(
        df_year, 
        geojson=geo_sumbar, 
        locations='Kab/Kota', 
        featureidkey="properties.name", 
        color=kolom_kasus,
        color_continuous_scale="Reds", # Warna merah lebih terasa 'urgensi' DBD
        mapbox_style="carto-positron",
        center={"lat": -0.7399, "lon": 100.8000}, # Koordinat tengah Sumbar
        zoom=6.5,
        hover_name='Kab/Kota',
        hover_data={kolom_kasus: True, 'Kab/Kota': False}
    )
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Terjadi kesalahan: {e}")