import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="DBD Sumatera Barat", page_icon="🗺️", layout="wide")

st.title("🗺️ Peta Sebaran Kasus DBD: Sumatera Barat")
st.markdown("Visualisasi spasial DBD tingkat Kabupaten/Kota.")
st.markdown("---")

base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
try:
    with st.spinner('Menyiapkan data Sumatera Barat...'):
        df = pd.read_csv(os.path.join(base_path, 'dataset_sumbar_clean_long.csv'))
        with open(os.path.join(base_path, 'all_kabkota_ind.geojson'), 'r', encoding='utf-8') as f:
            geo = json.load(f)
        
        df['Kab/Kota'] = df['Kab/Kota'].str.upper().replace({'KAB. PADANG PARIAMAN': 'PADANG PARIAMAN', 'KOTA PADANG': 'PADANG'})
        geo['features'] = [f for f in geo['features'] if f['properties'].get('prov_name') == 'SUMATERA BARAT']
        
        tahun = st.sidebar.selectbox("🗓️ Pilih Tahun:", sorted(df['Tahun'].unique(), reverse=True))
        df_year = df[df['Tahun'] == tahun].copy()
        df_year['Jumlah_Kasus'] = df_year['Jumlah_Kasus'].fillna(0)
        
        col1, col2 = st.columns(2)
        if not df_year.empty:
            max_row = df_year.loc[df_year['Jumlah_Kasus'].idxmax()]
            col1.metric("Total Kasus Sumbar", f"{df_year['Jumlah_Kasus'].sum():,.0f}")
            col2.metric("Tertinggi di", max_row['Kab/Kota'], f"{max_row['Jumlah_Kasus']:,.0f} Kasus")
            
        fig = px.choropleth_mapbox(df_year, geojson=geo, locations='Kab/Kota', featureidkey="properties.name", 
                                   color='Jumlah_Kasus', color_continuous_scale="Reds", mapbox_style="carto-positron",
                                   center={"lat": -0.7399, "lon": 100.8000}, zoom=6.8, hover_name='Kab/Kota')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### 📋 Tabel Data Kasus")
        st.dataframe(df_year[['Kab/Kota', 'Jumlah_Kasus']], use_container_width=True)
except Exception as e:
    st.error(f"Error: {e}")