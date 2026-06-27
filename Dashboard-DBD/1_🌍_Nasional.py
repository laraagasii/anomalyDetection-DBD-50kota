import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Dashboard DBD Nasional", page_icon="🌍", layout="wide")

st.title("🌍 Pantau & Deteksi DBD Indonesia")
st.markdown("Dashboard monitoring sebaran kasus DBD skala nasional.")
st.markdown("---")

base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
try:
    with st.spinner('Memuat data nasional...'):
        df = pd.read_csv(os.path.join(base_path, 'dataset_indonesia_clean_long.csv'))
        with open(os.path.join(base_path, 'indonesia.json'), 'r', encoding='utf-8') as f:
            geo = json.load(f)
        
        df['Provinsi'] = df['Provinsi'].str.title().replace({'Dki Jakarta': 'Jakarta Raya', 'Di Yogyakarta': 'Yogyakarta', 'Bangka Belitung': 'Bangka-Belitung'})
        
        # Filter Tahun
        tahun_list = sorted(df['Tahun'].unique(), reverse=True)
        tahun = st.sidebar.selectbox("🗓️ Pilih Tahun Pantauan:", tahun_list)
        df_year = df[df['Tahun'] == tahun]
        
        # KPI Metrics
        total_kasus = df_year['Jumlah_Kasus'].sum()
        max_prov = df_year.loc[df_year['Jumlah_Kasus'].idxmax()]
        
        col1, col2 = st.columns(2)
        col1.metric("Total Kasus Nasional", f"{total_kasus:,.0f}")
        col2.metric("Provinsi Tertinggi", max_prov['Provinsi'], f"{max_prov['Jumlah_Kasus']:,.0f} Kasus")
        
        # Mapbox
        fig = px.choropleth_mapbox(df_year, geojson=geo, locations='Provinsi', featureidkey="properties.state", 
                                   color='Jumlah_Kasus', color_continuous_scale="YlOrRd", mapbox_style="carto-positron",
                                   center={"lat": -0.7893, "lon": 113.9213}, zoom=3.8, hover_name='Provinsi')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### 📊 Data Detail per Provinsi")
        st.dataframe(df_year[['Provinsi', 'Jumlah_Kasus']], use_container_width=True)
except Exception as e:
    st.error(f"Error: {e}")