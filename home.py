import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import numpy as np
import plotly.express as px
from style_utils import apply_custom_style  # ✅ เรียกใช้ไฟล์กลาง

# --- 1. Config ---
st.set_page_config(page_title="SONGTUMLAY Pro", layout="wide", page_icon="🏙️")
apply_custom_style() # ✅ ใช้งาน Theme

# --- 2. Helper Functions & Data ---
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

# --- 3. Sidebar Inputs ---
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")
provinces = ["ทั้งหมด"] + sorted(list(df_all_years['Province'].unique())) if not df_all_years.empty else []
selected_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)
amphoes = ["ทั้งหมด"]
if selected_prov != "ทั้งหมด":
    amphoes += sorted(df_all_years[df_all_years['Province'] == selected_prov]['Amphoe'].unique())
selected_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)
st.sidebar.caption("© 2024 SongTumLay Pro")

# --- 4. Main Content ---
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
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:bold; font-size:20px;">{row['Tambon']}</div>
                    <div style="background:#1A365D; color:white; padding:4px 10px; border-radius:10px; font-size:14px; font-weight:bold;">{row['Total_Score']}</div>
                </div>
                <div style="font-size:14px; opacity:0.8; margin-top:5px;">📍 {row['Amphoe']}, {row['Province']}</div>
                <div style="margin-top:8px; font-weight:bold; color:#2ECC71; font-size:22px;">฿{row['Est_Land_Price']:,.0f}</div>
            </div>""", unsafe_allow_html=True)

# --- 5. Price Breakdown Section (Dashboard Style Design) ---
st.markdown("---")
st.subheader("🧮 แกะสูตรคำนวณราคา (Price Breakdown)")
st.info("เลือกตำบลด้านล่าง เพื่อดูว่าทฤษฎีแต่ละตัวส่งผลต่อราคาอย่างไร")

if not df_display.empty:
    tambon_opts = df_display['Tambon'].unique()
    target_tambon = st.selectbox("🔍 เลือกตำบลเพื่อถอดสูตร", tambon_opts)
    
    if target_tambon:
        row = df_display[df_display['Tambon'] == target_tambon].iloc[0]
        
        base_price = row['Avg_Land_Price']
        density_fac = row['Factor_Density']
        central_fac = row['Factor_Centrality']
        final_price = row['Est_Land_Price']
        
        # ✅ Dashboard Style HTML: แบ่ง 4 การ์ด สีพาสเทล + ไอคอน
        html_code = f"""
        <style>
            .metric-container {{
                display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 25px;
            }}
            .metric-card {{
                flex: 1; min-width: 220px;
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(0,0,0,0.05);
            }}
            .card-title {{ font-size: 16px; font-weight: bold; color: #555; margin-bottom: 10px; }}
            .card-value {{ font-size: 28px; font-weight: 900; color: #333; }}
            .card-icon {{ 
                position: absolute; top: 15px; right: 15px; font-size: 40px; opacity: 0.2; 
            }}
            .card-footer {{ 
                margin-top: 15px; font-size: 13px; font-weight: bold; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1); 
            }}
        </style>

        <div class="metric-container">
            <div class="metric-card" style="background: #E3F2FD;">
                <div class="card-title">ราคาตั้งต้น (Base)</div>
                <div class="card-value" style="color:#1565C0;">฿{base_price:,.0f}</div>
                <div class="card-icon">🏷️</div>
                <div class="card-footer" style="color:#1565C0;">ราคาประเมินกรมที่ดิน</div>
            </div>

            <div class="metric-card" style="background: #FFF3E0;">
                <div class="card-title">Density Factor</div>
                <div class="card-value" style="color:#E65100;">x {density_fac:.2f}</div>
                <div class="card-icon">👥</div>
                <div class="card-footer" style="color:#E65100;">ปรับตามความหนาแน่น</div>
            </div>

            <div class="metric-card" style="background: #F3E5F5;">
                <div class="card-title">Location Factor</div>
                <div class="card-value" style="color:#7B1FA2;">x {central_fac:.1f}</div>
                <div class="card-icon">🏙️</div>
                <div class="card-footer" style="color:#7B1FA2;">ปรับตามโซนเมือง</div>
            </div>

            <div class="metric-card" style="background: #E8F5E9; border: 2px solid #4CAF50;">
                <div class="card-title">ราคาประเมิน AI</div>
                <div class="card-value" style="color:#2E7D32;">฿{final_price:,.0f}</div>
                <div class="card-icon" style="opacity:1;">💰</div>
                <div class="card-footer" style="color:#2E7D32;">สรุปราคาขายจริง</div>
            </div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 วิเคราะห์ปัจจัย (Factors)")
            if density_fac > 1.0:
                st.success(f"📈 **Population Density (+):** ประชากรหนาแน่นกว่าค่าเฉลี่ย ({density_fac:.2f} เท่า)")
            else:
                st.warning(f"📉 **Population Density (-):** ประชากรน้อยกว่าค่าเฉลี่ย ({density_fac:.2f} เท่า)")
                
            if central_fac > 1.0:
                st.info(f"🏙️ **Central Place Effect:** อยู่ในเขตอำเภอเมือง/ศูนย์กลาง")
            else:
                st.markdown(f"🏡 **Central Place Effect:** เป็นพื้นที่รอบนอก")

        with c2:
            st.markdown("### 📈 เทียบราคา")
            comp_data = pd.DataFrame({
                'Type': ['ราคาพื้นฐาน', 'ราคาประเมิน AI'],
                'Price': [base_price, final_price]
            })
            fig = px.bar(comp_data, x='Type', y='Price', color='Type', 
                         color_discrete_map={'ราคาพื้นฐาน':'#90A4AE', 'ราคาประเมิน AI':'#4CAF50'},
                         text_auto='.2s')
            
            fig.update_layout(showlegend=False, height=250, 
                              paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=20, r=20, t=20, b=20),
                              font=dict(color=st.get_option("theme.textColor")))
            st.plotly_chart(fig, use_container_width=True)
