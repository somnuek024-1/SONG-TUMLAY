import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import numpy as np
import plotly.express as px
from style_utils import apply_custom_style  # ✅ เรียกใช้ไฟล์กลาง

# --- Config ---
st.set_page_config(page_title="SONGTUMLAY Pro", layout="wide", page_icon="🏙️")
apply_custom_style() # ✅ ใช้งาน Theme

# --- Helper Functions ---
def get_coordinates(province_name):
    coords = {
        "เชียงใหม่": [18.7883, 98.9853], "ขอนแก่น": [16.4322, 102.8236], "ภูเก็ต": [7.8804, 98.3923], 
        "กรุงเทพมหานคร": [13.7563, 100.5018], "นครราชสีมา": [14.9799, 102.0978], "ชลบุรี": [13.3611, 100.9847],
        "สงขลา": [7.1988, 100.5951], "อุดรธานี": [17.4138, 102.7872], "ประจวบคีรีขันธ์": [11.8124, 99.7973], 
        "ระยอง": [12.6815, 101.2816], "พระนครศรีอยุธยา": [14.3532, 100.5684], "สุราษฎร์ธานี": [9.1382, 99.3217],
        "เชียงราย": [19.9105, 99.8406], "อุบลราชธานี": [15.2448, 104.8473], "พิษณุโลก": [16.8211, 100.2659], 
        "กาญจนบุรี": [14.0225, 99.5327]
    }
    return coords.get(province_name, [13.7563, 100.5018])

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        if 'lat' not in df.columns or 'lon' not in df.columns:
            coords = df['Province'].apply(get_coordinates)
            df['lat'] = coords.apply(lambda x: x[0]) + np.random.normal(0, 0.02, size=len(df))
            df['lon'] = coords.apply(lambda x: x[1]) + np.random.normal(0, 0.02, size=len(df))
        return df
    except FileNotFoundError: return pd.DataFrame()

df_all_years = load_data()

@st.cache_data
def process_latest_view(df):
    if df.empty: return pd.DataFrame(), "N/A"
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year].copy()
    
    prov_pop_mean = df_latest.groupby('Province')['Total_Pop'].transform('mean').replace(0, 1)
    pop_ratio = df_latest['Total_Pop'] / prov_pop_mean
    df_latest['Factor_Density'] = np.power(pop_ratio, 0.3)
    df_latest['Factor_Centrality'] = df_latest['Amphoe'].apply(lambda x: 1.2 if ('เมือง' in str(x) or 'เขต' in str(x)) else 1.0)
    df_latest['Factor_Total'] = (df_latest['Factor_Density'] * df_latest['Factor_Centrality']).clip(0.5, 3.0)
    df_latest['Est_Land_Price'] = df_latest['Avg_Land_Price'] * df_latest['Factor_Total']
    
    max_inc = df_latest['Avg_Income'].max() or 1
    max_land = df_latest['Est_Land_Price'].max() or 1
    max_pop = df_latest['Total_Pop'].max() or 1
    df_latest['Total_Score'] = ((df_latest['Avg_Income']/max_inc * 3) + (df_latest['Est_Land_Price']/max_land * 2) + (df_latest['Total_Pop']/max_pop * 5)).round(1)
    
    return df_latest, str(latest_year)

if not df_all_years.empty:
    df_view, latest_year_str = process_latest_view(df_all_years)
else:
    df_view = pd.DataFrame()
    latest_year_str = "N/A"

# --- Sidebar Inputs ---
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")
provinces = ["ทั้งหมด"] + sorted(list(df_all_years['Province'].unique())) if not df_all_years.empty else []
selected_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)
amphoes = ["ทั้งหมด"]
if selected_prov != "ทั้งหมด":
    amphoes += sorted(df_all_years[df_all_years['Province'] == selected_prov]['Amphoe'].unique())
selected_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)
st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
st.sidebar.caption("© 2024 SongTumLay Pro")

# --- Main Content ---
st.title(f"วิเคราะห์ทำเล: {selected_prov if selected_prov!='ทั้งหมด' else 'ภาพรวม'}")

df_display = df_view.copy()
if selected_prov != "ทั้งหมด": df_display = df_display[df_display['Province'] == selected_prov]
if selected_amphoe != "ทั้งหมด": df_display = df_display[df_display['Amphoe'] == selected_amphoe]

col_map, col_list = st.columns([2, 1.2])

with col_map:
    st.subheader(f"🗺️ แผนที่ราคา ({latest_year_str})")
    center = [13.7563, 100.5018]
    zoom = 6
    if not df_display.empty:
        center = [df_display['lat'].mean(), df_display['lon'].mean()]
        zoom = 10 if selected_amphoe == "ทั้งหมด" else 11
        
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    mc = MarkerCluster().add_to(m)
    if not df_display.empty:
        for _, row in df_display.iterrows():
            if pd.notna(row['lat']):
                color = '#2ECC71' if row['Total_Score'] >= 6 else ('#F1C40F' if row['Total_Score'] >= 3 else '#E74C3C')
                folium.CircleMarker(
                    [row['lat'], row['lon']], radius=6, color=color, fill=True, fill_color=color, fill_opacity=0.9,
                    popup=f"<b>{row['Tambon']}</b><br>฿{row['Est_Land_Price']:,.0f}", tooltip=row['Tambon']
                ).add_to(mc)
    st_folium(m, height=500, use_container_width=True)

with col_list:
    st.subheader("🏆 รายการ (Top 5)")
    if not df_display.empty:
        top_list = df_display.sort_values('Total_Score', ascending=False).head(5)
        for _, row in top_list.iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display:flex; justify-content:space-between;">
                    <div style="font-weight:bold;">{row['Tambon']}</div>
                    <div style="background:#1A365D; color:white; padding:2px 8px; border-radius:10px; font-size:11px;">{row['Total_Score']}</div>
                </div>
                <div style="font-size:12px; opacity:0.7;">📍 {row['Amphoe']}, {row['Province']}</div>
                <div style="margin-top:5px; font-weight:bold; color:#2ECC71; font-size:16px;">฿{row['Est_Land_Price']:,.0f}</div>
            </div>""", unsafe_allow_html=True)