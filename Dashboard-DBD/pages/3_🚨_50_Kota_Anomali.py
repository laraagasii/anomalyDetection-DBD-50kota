import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Deteksi Anomali 50 Kota", page_icon="🚨", layout="wide")

# --- UI Header ---
st.title("🚨 Deteksi Anomali DBD: 50 Kota")
st.markdown("Analisis deteksi dini wilayah yang mengalami lonjakan kasus DBD tidak wajar.")
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

# --- ANIMASI LOADING (ST.SPINNER) ---
with st.spinner('Memuat data deteksi anomali...'):
    try:
        df_50kota, geo_50kota = load_data_50kota()
        kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_50kota.columns else 'Kasus'
        
        tab1, tab2 = st.tabs(["🗺️ Peta Spasial & Anomali", "📈 Analisis Tren Temporal"])
        
        with tab1:
            st.subheader("Peta Sebaran DBD & Titik Anomali")
            tahun = st.slider("Pilih Tahun:", int(df_50kota['Tahun'].min()), int(df_50kota['Tahun'].max()), int(df_50kota['Tahun'].max()))
            df_year = df_50kota[df_50kota['Tahun'] == tahun]
            
            # Peta Mapbox untuk level kecamatan
            fig_map = px.choropleth_mapbox(
                df_year, 
                geojson=geo_50kota, 
                locations='Kecamatan', 
                featureidkey="properties.district", 
                color=kolom_kasus,
                color_continuous_scale="Reds", 
                mapbox_style="carto-positron",
                center={"lat": -0.166, "lon": 100.65},
                zoom=9.5,
                hover_name='Kecamatan'
            )
            
            # Overlay Titik Anomali
            df_anomali_year = df_year[df_year['is_anomali'] == True]
            if not df_anomali_year.empty:
                fig_map.add_scattermapbox(
                    lat=df_anomali_year['lat'], 
                    lon=df_anomali_year['lon'],
                    mode='markers',
                    marker=dict(size=12, color='white', symbol='cross'),
                    name='Anomali Terdeteksi'
                )
                
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Alert UI
            if not df_anomali_year.empty:
                st.error(f"⚠️ Terdeteksi {len(df_anomali_year)} Kecamatan Anomali di Tahun {tahun}!")
                st.dataframe(df_anomali_year[['Kecamatan', kolom_kasus]], use_container_width=True)
            else:
                st.success("✅ Aman! Tidak ada anomali terdeteksi pada tahun ini.")
            
        with tab2:
            st.subheader("Tren Kasus Waktu")
            kec_list = sorted(df_50kota['Kecamatan'].unique())
            selected_kec = st.multiselect("Pilih Kecamatan:", kec_list, default=kec_list[:3])
            
            df_filtered = df_50kota[df_50kota['Kecamatan'].isin(selected_kec)]
            fig_line = px.line(df_filtered, x='Tahun', y=kolom_kasus, color='Kecamatan', markers=True)
            
            # Highlight Anomali di Line Chart
            df_anomali = df_filtered[df_filtered['is_anomali'] == True]
            if not df_anomali.empty:
                fig_line.add_scatter(x=df_anomali['Tahun'], y=df_anomali[kolom_kasus], 
                                     mode='markers', marker=dict(color='black', size=10, symbol='x'), name='Anomali')
            st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")