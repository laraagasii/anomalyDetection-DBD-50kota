import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Deteksi Anomali 50 Kota", page_icon="🚨", layout="wide")

st.title("🚨 Deteksi Anomali DBD: 50 Kota")
st.write("Analisis Spasio-Temporal Tingkat Kecamatan menggunakan Machine Learning")
st.markdown("---")

# --- LOGIKA PATH ANTI-ERROR ---
base_path = 'Dashboard-DBD' if os.path.exists('Dashboard-DBD') else '.'
csv_path = os.path.join(base_path, 'dataset_50kota_anomali.csv')
geo_path = os.path.join(base_path, 'id1308_lima_puluh_kota.geojson')

@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    with open(geo_path, 'r') as f:
        geo = json.load(f)
    return df, geo

try:
    df_50kota, geo_50kota = load_data()
    
    # Cek dinamis nama kolom jumlah kasus
    kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_50kota.columns else 'Kasus'
    
    tab1, tab2 = st.tabs(["🗺️ Peta Spasial & Anomali", "📈 Tren Temporal"])
    
    # === TAB 1: PETA SPASIAL ===
    with tab1:
        st.subheader("Peta Sebaran DBD & Titik Anomali")
        tahun = st.slider("Pilih Tahun:", int(df_50kota['Tahun'].min()), int(df_50kota['Tahun'].max()), int(df_50kota['Tahun'].max()))
        df_year = df_50kota[df_50kota['Tahun'] == tahun]
        
        fig_map = px.choropleth(
            df_year, 
            geojson=geo_50kota, 
            locations='Kecamatan', 
            featureidkey="properties.district", 
            color=kolom_kasus,
            color_continuous_scale="Reds", 
            title=f"Sebaran 50 Kota Tahun {tahun}"
        )
        
        # Highlight Anomali
        df_anomali_year = df_year[df_year['is_anomali'] == True]
        if not df_anomali_year.empty:
            fig_map.add_scattergeo(
                locations=df_anomali_year['Kecamatan'], 
                geojson=geo_50kota,
                featureidkey="properties.district", 
                mode='markers',
                marker=dict(size=12, color='blue', symbol='x'), 
                name='Anomali Terdeteksi'
            )
            
        fig_map.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.write("### ⚠️ Kecamatan Anomali di Tahun Ini")
        if not df_anomali_year.empty:
            st.dataframe(df_anomali_year[['Kecamatan', kolom_kasus]], use_container_width=True)
        else:
            st.success("Tidak ada anomali terdeteksi pada tahun ini.")
        
    # === TAB 2: TREN TEMPORAL ===
    with tab2:
        st.subheader("Tren Kasus Waktu (Temporal)")
        kec_list = sorted(df_50kota['Kecamatan'].unique())
        selected_kec = st.multiselect("Pilih Kecamatan:", kec_list, default=kec_list[:3])
        
        df_filtered = df_50kota[df_50kota['Kecamatan'].isin(selected_kec)]
        fig_line = px.line(df_filtered, x='Tahun', y=kolom_kasus, color='Kecamatan', markers=True)
        
        df_anomali = df_filtered[df_filtered['is_anomali'] == True]
        if not df_anomali.empty:
            fig_line.add_scatter(
                x=df_anomali['Tahun'], y=df_anomali[kolom_kasus], 
                mode='markers', marker=dict(color='red', size=12, symbol='x'), name='Anomali'
            )
        st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error: {e}. Gagal membaca data di path: {csv_path} atau {geo_path}")