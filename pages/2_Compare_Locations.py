import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium

# --- 1. Config ---
st.set_page_config(page_title="เปรียบเทียบทำเล - SongTumLay", layout="wide", page_icon="⚖️")

# --- 2. Theme & Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
        color: var(--text-color);
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(120deg, var(--secondary-background-color) 0%, var(--background-color) 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid rgba(128,128,128,0.1);
    }
    .main-title { font-size: 36px; font-weight: 700; color: var(--text-color); margin-bottom: 10px; }
    .sub-title { font-size: 18px; font-weight: 300; color: var(--text-color); opacity: 0.7; }
    
    /* VS Badge */
    .vs-badge {
        background-color: var(--text-color);
        color: var(--background-color);
        width: 40px; height: 40px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; font-size: 14px; margin: 0 auto;
        border: 2px solid var(--secondary-background-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Verdict Box */
    .verdict-box {
        background-color: var(--secondary-background-color);
        padding: 20px; border-radius: 10px; margin-top: 20px;
        text-align: center; font-weight: 600; color: var(--text-color);
        border: 1px solid rgba(128,128,128,0.1);
    }
    
    /* Stat Card */
    .stat-card {
        background: var(--secondary-background-color);
        padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center; margin-bottom: 10px;
        border: 1px solid rgba(128,128,128,0.2);
        color: var(--text-color);
    }

    /* Mobile Responsive */
    @media only screen and (max-width: 600px) {
        .header-container { padding: 20px 10px; }
        .main-title { font-size: 24px; }
        .sub-title { font-size: 14px; }
        .js-plotly-plot { height: 400px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Load Data & Helper Functions ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        latest_year = df['Year'].max()
        df = df[df['Year'] == latest_year].copy()
        df['Full_Location'] = df['Amphoe'] + ", " + df['Province']
        
        # Calculate Scores
        df['Score_Price'] = (df['Avg_Land_Price'] / df['Avg_Land_Price'].max()) * 100
        df['Score_Income'] = (df['Avg_Income'] / df['Avg_Income'].max()) * 100
        df['Score_Pop'] = (df['Total_Pop'] / df['Total_Pop'].max()) * 100
        return df
    except:
        return pd.DataFrame()

def get_coordinates(province_name):
    # พิกัดหัวเมืองใหญ่
    coords = {
        "เชียงใหม่": [18.7883, 98.9853], "ขอนแก่น": [16.4322, 102.8236],
        "ภูเก็ต": [7.8804, 98.3923], "กรุงเทพมหานคร": [13.7563, 100.5018],
        "นครราชสีมา": [14.9799, 102.0978], "ชลบุรี": [13.3611, 100.9847],
        "สงขลา": [7.1988, 100.5951], "อุดรธานี": [17.4138, 102.7872],
        "ประจวบคีรีขันธ์": [11.8124, 99.7973], "ระยอง": [12.6815, 101.2816],
        "พระนครศรีอยุธยา": [14.3532, 100.5684], "สุราษฎร์ธานี": [9.1382, 99.3217],
        "เชียงราย": [19.9105, 99.8406], "อุบลราชธานี": [15.2448, 104.8473],
        "พิษณุโลก": [16.8211, 100.2659], "กาญจนบุรี": [14.0225, 99.5327]
    }
    return coords.get(province_name, [13.7563, 100.5018])

df = load_data()

# --- 4. UI ---
st.markdown("""
<div class="header-container">
    <div class="main-title">⚖️ Compare Locations</div>
    <div class="sub-title">เปรียบเทียบศักยภาพทำเล ชัดเจน เข้าใจง่าย</div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("ไม่พบข้อมูล final_master_data_multiyear.csv")
    st.stop()

col1, col2 = st.columns(2)
locations_list = sorted(df['Full_Location'].unique())

with col1:
    st.markdown("### 🟦 ทำเลที่ 1 (สีฟ้า)")
    idx1 = locations_list.index("เมืองเชียงใหม่, เชียงใหม่") if "เมืองเชียงใหม่, เชียงใหม่" in locations_list else 0
    loc1_name = st.selectbox("เลือกทำเล A", locations_list, index=idx1, key='loc1')

with col2:
    st.markdown("### 🟩 ทำเลที่ 2 (สีเขียว)")
    idx2 = locations_list.index("เมืองขอนแก่น, ขอนแก่น") if "เมืองขอนแก่น, ขอนแก่น" in locations_list else 1
    loc2_name = st.selectbox("เลือกทำเล B", locations_list, index=idx2, key='loc2')

# --- 5. Process Comparison ---
if loc1_name and loc2_name:
    data1 = df[df['Full_Location'] == loc1_name].iloc[0]
    data2 = df[df['Full_Location'] == loc2_name].iloc[0]
    
    st.markdown("---")
    
    # === Graph Section ===
    st.markdown("#### 📊 เปรียบเทียบคะแนนศักยภาพ")
    cats = ['ราคาที่ดิน', 'รายได้ประชากร', 'จำนวนประชากร']
    sc1 = [data1['Score_Price'], data1['Score_Income'], data1['Score_Pop']]
    sc2 = [data2['Score_Price'], data2['Score_Income'], data2['Score_Pop']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=cats, x=sc1, name=data1['Amphoe'], orientation='h', marker_color='#3498DB', opacity=0.9, text=[f"{s:.0f}" for s in sc1], textposition='auto'))
    fig.add_trace(go.Bar(y=cats, x=sc2, name=data2['Amphoe'], orientation='h', marker_color='#2ECC71', opacity=0.9, text=[f"{s:.0f}" for s in sc2], textposition='auto'))
    
    fig.update_layout(
        barmode='group', 
        xaxis=dict(range=[0, 110], color='gray'),
        yaxis=dict(autorange="reversed", color='gray'), 
        height=350, margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", y=1.1, font=dict(color='gray')),
        font=dict(family="Sarabun", size=14),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # === Stats Section ===
    st.markdown("#### ⚡ วัดกันที่ตัวเลขจริง")
    c_s1, c_s2, c_s3 = st.columns(3)
    
    def create_stat_card(title, val1, val2, unit):
        diff = val1 - val2
        if val1 > val2: wc="color:#3498DB;"; wi="🟦 A ชนะ"
        elif val2 > val1: wc="color:#2ECC71;"; wi="🟩 B ชนะ"
        else: wc="color:gray;"; wi="➖ เสมอ"

        return f"""
        <div class="stat-card">
            <div style="font-size:15px; font-weight:bold; margin-bottom:10px;">{title}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
                <div style="text-align:left; width:40%; min-width:80px; color:#3498DB; font-weight:bold; font-size:18px;">{val1:,.0f}</div>
                <div style="width:20%; display:flex; justify-content:center;"><div class="vs-badge">VS</div></div>
                <div style="text-align:right; width:40%; min-width:80px; color:#2ECC71; font-weight:bold; font-size:18px;">{val2:,.0f}</div>
            </div>
            <div style="font-size:12px; opacity:0.7;">ส่วนต่าง {abs(diff):,.0f} {unit}</div>
            <div style="margin-top:5px; font-weight:bold; font-size:13px; {wc}">{wi}</div>
        </div>
        """
    with c_s1: st.markdown(create_stat_card("ราคาที่ดินเฉลี่ย", data1['Avg_Land_Price'], data2['Avg_Land_Price'], "บาท"), unsafe_allow_html=True)
    with c_s2: st.markdown(create_stat_card("รายได้ครัวเรือน", data1['Avg_Income'], data2['Avg_Income'], "บาท"), unsafe_allow_html=True)
    with c_s3: st.markdown(create_stat_card("จำนวนประชากร", data1['Total_Pop'], data2['Total_Pop'], "คน"), unsafe_allow_html=True)

    # === 🗺️ NEW MAP SECTION (แผนที่แบบใหม่) ===
    st.markdown("#### 🗺️ แผนที่เปรียบเทียบตำแหน่ง")
    
    # 1. หาพิกัด
    lat1, lon1 = get_coordinates(data1['Province'])
    lat2, lon2 = get_coordinates(data2['Province'])
    
    # 2. คำนวณจุดกึ่งกลาง (Center) เพื่อให้แผนที่แสดงทั้งคู่
    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2
    
    # 3. สร้างแผนที่ Folium (ใช้ธีม CartoDB positron สีสะอาดตา ดูง่าย)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="CartoDB positron")
    
    # 4. สร้างจุด Marker วงกลมใหญ่ๆ (CircleMarker)
    # จุดที่ 1: สีฟ้า (Blue)
    folium.CircleMarker(
        location=[lat1, lon1],
        radius=15,          # ✅ กำหนดขนาดจุดเป็น Pixel (ใหญ่ชัดเจน)
        color="white",      # ขอบสีขาว
        weight=2,
        fill=True,
        fill_color="#3498DB", # สีฟ้า
        fill_opacity=1.0,   # สีทึบ ไม่โปร่งใส
        popup=f"<b>{data1['Amphoe']}</b><br>ราคา: {data1['Avg_Land_Price']:,}",
        tooltip=f"A: {data1['Amphoe']}"
    ).add_to(m)
    
    # จุดที่ 2: สีเขียว (Green)
    folium.CircleMarker(
        location=[lat2, lon2],
        radius=15,          # ✅ จุดใหญ่เท่ากัน
        color="white",
        weight=2,
        fill=True,
        fill_color="#2ECC71", # สีเขียว
        fill_opacity=1.0,
        popup=f"<b>{data2['Amphoe']}</b><br>ราคา: {data2['Avg_Land_Price']:,}",
        tooltip=f"B: {data2['Amphoe']}"
    ).add_to(m)
    
    # แสดงแผนที่
    st_folium(m, height=400, use_container_width=True)

    # === Verdict ===
    rec = ""
    if data1['Score_Price'] < data2['Score_Price'] and data1['Score_Income'] > data2['Score_Income']:
        rec = f"✨ **{data1['Amphoe']}** ดูคุ้มค่ากว่า! (ที่ดินถูกกว่า + คนรวยกว่า)"
    elif data2['Score_Price'] < data1['Score_Price'] and data2['Score_Income'] > data1['Score_Income']:
        rec = f"✨ **{data2['Amphoe']}** ดูคุ้มค่ากว่า! (ที่ดินถูกกว่า + คนรวยกว่า)"
    elif data1['Total_Pop'] > data2['Total_Pop']:
        rec = f"🏙️ หากเน้นคนพลุกพล่าน **{data1['Amphoe']}** ตอบโจทย์กว่ามาก"
    else:
        rec = f"🏙️ หากเน้นคนพลุกพล่าน **{data2['Amphoe']}** ตอบโจทย์กว่ามาก"

    st.markdown(f"""<div class="verdict-box">{rec}</div>""", unsafe_allow_html=True)
