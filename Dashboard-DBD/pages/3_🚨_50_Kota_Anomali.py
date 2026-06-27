import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Deteksi Anomali 50 Kota", page_icon="🚨", layout="wide")

# --- UI HEADER YANG KONSISTEN ---
st.title("🚨 Deteksi Anomali DBD: 50 Kota")
st.markdown("Analisis deteksi dini wilayah yang mengalami lonjakan kasus DBD tidak wajar menggunakan Machine Learning.")
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

# --- LOADING ANIMATION ---
with st.spinner('Memuat analisis data 50 Kota...'):
    try:
        df_50kota, geo_50kota = load_data_50kota()
        kolom_kasus = 'Jumlah_Kasus' if 'Jumlah_Kasus' in df_50kota.columns else 'Kasus'
        
        # --- TAB NAVIGATION ---
        tab1, tab2 = st.tabs(["🗺️ Peta Spasial & Anomali", "📈 Analisis Tren Temporal"])
        
        with tab1:
            st.subheader("Peta Sebaran DBD & Titik Anomali")
            
            # Filter Tahun
            tahun_list = sorted(df_50kota['Tahun'].unique(), reverse=True)
            tahun = st.selectbox("🗓️ Pilih Tahun Pantauan:", tahun_list)
            df_year = df_50kota[df_50kota['Tahun'] == tahun].copy()
            df_year[kolom_kasus] = df_year[kolom_kasus].fillna(0)
            
            # Mapbox Map
            fig_map = px.choropleth_mapbox(
                df_year, geojson=geo_50kota, locations='Kecamatan', 
                featureidkey="properties.district", color=kolom_kasus,
                color_continuous_scale="Reds", mapbox_style="carto-positron",
                center={"lat": -0.166, "lon": 100.65}, zoom=9.5,
                hover_name='Kecamatan',
                range_color=(0, df_year[kolom_kasus].max() if df_year[kolom_kasus].max() > 0 else 1)
            )
            
            # Add Anomaly Overlay (Cek kolom lat/lon ada atau tidak)
            if 'lat' in df_year.columns and 'lon' in df_year.columns:
                df_anomali_year = df_year[df_year['is_anomali'] == True]
                if not df_anomali_year.empty:
                    fig_map.add_scattermapbox(
                        lat=df_anomali_year['lat'], lon=df_anomali_year['lon'],
                        mode='markers', marker=dict(size=14, color='white', symbol='cross'),
                        name='Anomali Terdeteksi'
                    )
            
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Data Table Anomali
            st.write("### ⚠️ Detail Kecamatan Anomali")
            if 'is_anomali' in df_year.columns:
                df_anomali = df_year[df_year['is_anomali'] == True]
                if not df_anomali.empty:
                    st.error(f"Terdeteksi {len(df_anomali)} titik anomali.")
                    st.dataframe(df_anomali[['Kecamatan', kolom_kasus]], use_container_width=True)
                else:
                    st.success("Semua kecamatan dalam kondisi normal.")

        with tab2:
            st.subheader("Tren Kasus per Kecamatan")
            kec_list = sorted(df_50kota['Kecamatan'].unique())
            selected_kec = st.multiselect("Pilih Kecamatan untuk Dilihat Tren-nya:", kec_list, default=kec_list[:3])
            
            df_filtered = df_50kota[df_50kota['Kecamatan'].isin(selected_kec)]
            fig_line = px.line(df_filtered, x='Tahun', y=kolom_kasus, color='Kecamatan', markers=True)
            
            # Anomali overlay pada line chart
            df_anomali_all = df_50kota[df_50kota['is_anomali'] == True]
            if not df_anomali_all.empty:
                fig_line.add_scatter(x=df_anomali_all['Tahun'], y=df_anomali_all[kolom_kasus], 
                                     mode='markers', marker=dict(color='red', size=8, symbol='x'), name='Anomali')
            
            st.plotly_chart(fig_line, use_container_width=True)
            st.info("Keterangan: Tanda silang (x) menunjukkan tahun terjadinya anomali pada kecamatan tersebut.")

    except Exception as e:
        st.error(f"Terjadi error pada dataset: {e}")