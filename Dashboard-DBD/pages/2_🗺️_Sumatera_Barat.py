import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="DBD Sumatera Barat", page_icon="🗺️", layout="wide")

st.title("🗺️ Peta Sebaran Kasus DBD: Sumatera Barat")
st.write("Visualisasi Spasio-Temporal Tingkat Kabupaten/Kota - Informatika UNAND")
st.markdown("---")

base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_sumbar_clean_long.csv')
geo_path = os.path.join(base_path, 'all_kabkota_ind.geojson')

# NAMA FUNGSI DIBEDAKAN
@st.cache_data
def load_data_sumbar():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r') as f:
        geo = json.load(f)
    return df, geo

try:
    df_sumbar, geo_sumbar_raw = load_data_sumbar()
    
    # FIX CASE MISMATCH: Jadikan huruf kapital semua
    df_sumbar['Kab/Kota'] = df_sumbar['Kab/Kota'].str.upper()
    
    # TRIK: Filter GeoJSON hanya untuk Sumatera Barat agar peta langsung nge-zoom ke Sumbar!
    geo_sumbar = geo_sumbar_raw.copy()
    geo_sumbar['features'] = [f for f in geo_sumbar_raw['features'] if f['properties'].get('prov_name') == 'SUMATERA BARAT']
    
    kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_sumbar.columns else 'Kasus'
    
    tahun = st.slider("Pilih Tahun:", int(df_sumbar['Tahun'].min()), int(df_sumbar['Tahun'].max()), int(df_sumbar['Tahun'].max()))
    df_year = df_sumbar[df_sumbar['Tahun'] == tahun]
    
    fig = px.choropleth(
        df_year, 
        geojson=geo_sumbar, 
        locations='Kab/Kota', 
        featureidkey="properties.name", 
        color=kolom_kasus,
        color_continuous_scale="Oranges", 
        title=f"Sebaran Sumatera Barat Tahun {tahun}"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error: {e}. Gagal membaca data di path: {csv_path} atau {geo_path}")