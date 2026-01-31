import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium
from style_utils import apply_custom_style # ✅

st.set_page_config(page_title="เปรียบเทียบทำเล - SongTumLay", layout="wide", page_icon="⚖️")
apply_custom_style() # ✅

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        latest_year = df['Year'].max()
        df = df[df['Year'] == latest_year].copy()
        df['Full_Location'] = df['Amphoe'] + ", " + df['Province']
        df['Score_Price'] = (df['Avg_Land_Price'] / df['Avg_Land_Price'].max()) * 100
        df['Score_Income'] = (df['Avg_Income'] / df['Avg_Income'].max()) * 100
        df['Score_Pop'] = (df['Total_Pop'] / df['Total_Pop'].max()) * 100
        return df
    except: return pd.DataFrame()

def get_coordinates(province_name):
    coords = { "เชียงใหม่": [18.7883, 98.9853], "ขอนแก่น": [16.4322, 102.8236], "ภูเก็ต": [7.8804, 98.3923], "กรุงเทพมหานคร": [13.7563, 100.5018], "นครราชสีมา": [14.9799, 102.0978], "ชลบุรี": [13.3611, 100.9847], "สงขลา": [7.1988, 100.5951], "อุดรธานี": [17.4138, 102.7872], "ประจวบคีรีขันธ์": [11.8124, 99.7973], "ระยอง": [12.6815, 101.2816], "พระนครศรีอยุธยา": [14.3532, 100.5684], "สุราษฎร์ธานี": [9.1382, 99.3217], "เชียงราย": [19.9105, 99.8406], "อุบลราชธานี": [15.2448, 104.8473], "พิษณุโลก": [16.8211, 100.2659], "กาญจนบุรี": [14.0225, 99.5327] }
    return coords.get(province_name, [13.7563, 100.5018])

df = load_data()

st.markdown("""<div style="text-align:center; padding:40px; background:linear-gradient(120deg, var(--secondary-background-color), var(--background-color)); border-radius:20px; margin-bottom:30px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid rgba(128,128,128,0.1);"><div style="font-size:36px; font-weight:700;">⚖️ Compare Locations</div><div style="opacity:0.7;">เปรียบเทียบศักยภาพทำเล</div></div>""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚡ เลือกคู่เปรียบเทียบ")
col1, col2 = st.columns(2)
locations_list = sorted(df['Full_Location'].unique())

with col1:
    idx1 = locations_list.index("เมืองเชียงใหม่, เชียงใหม่") if "เมืองเชียงใหม่, เชียงใหม่" in locations_list else 0
    loc1_name = st.selectbox("เลือกทำเล A (ฟ้า)", locations_list, index=idx1)
with col2:
    idx2 = locations_list.index("เมืองขอนแก่น, ขอนแก่น") if "เมืองขอนแก่น, ขอนแก่น" in locations_list else 1
    loc2_name = st.selectbox("เลือกทำเล B (เขียว)", locations_list, index=idx2)

if loc1_name and loc2_name:
    data1 = df[df['Full_Location'] == loc1_name].iloc[0]
    data2 = df[df['Full_Location'] == loc2_name].iloc[0]
    st.markdown("---")
    
    st.markdown("#### 📊 คะแนนศักยภาพ")
    cats = ['ราคาที่ดิน', 'รายได้', 'ประชากร']
    fig = go.Figure()
    fig.add_trace(go.Bar(y=cats, x=[data1['Score_Price'], data1['Score_Income'], data1['Score_Pop']], name=data1['Amphoe'], orientation='h', marker_color='#3498DB', opacity=0.9, textposition='auto'))
    fig.add_trace(go.Bar(y=cats, x=[data2['Score_Price'], data2['Score_Income'], data2['Score_Pop']], name=data2['Amphoe'], orientation='h', marker_color='#2ECC71', opacity=0.9, textposition='auto'))
    fig.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### ⚡ วัดกันที่ตัวเลขจริง")
    c_s1, c_s2, c_s3 = st.columns(3)
    def create_stat(t, v1, v2, u):
        diff = v1 - v2
        wc = "color:#3498DB;" if v1 > v2 else ("color:#2ECC71;" if v2 > v1 else "color:gray;")
        wi = "🟦 A ชนะ" if v1 > v2 else ("🟩 B ชนะ" if v2 > v1 else "➖ เสมอ")
        return f"""<div class="stat-card"><div style="font-weight:bold;">{t}</div><div style="display:flex; justify-content:space-between; margin-top:10px;"><span style="color:#3498DB; font-weight:bold;">{v1:,.0f}</span><div class="vs-badge">VS</div><span style="color:#2ECC71; font-weight:bold;">{v2:,.0f}</span></div><div style="font-size:12px; margin-top:5px; {wc}">{wi}</div></div>"""
    
    with c_s1: st.markdown(create_stat("ราคาที่ดิน", data1['Avg_Land_Price'], data2['Avg_Land_Price'], "฿"), unsafe_allow_html=True)
    with c_s2: st.markdown(create_stat("รายได้", data1['Avg_Income'], data2['Avg_Income'], "฿"), unsafe_allow_html=True)
    with c_s3: st.markdown(create_stat("ประชากร", data1['Total_Pop'], data2['Total_Pop'], "คน"), unsafe_allow_html=True)

    st.markdown("#### 🗺️ แผนที่เปรียบเทียบตำแหน่ง")
    lat1, lon1 = get_coordinates(data1['Province'])
    lat2, lon2 = get_coordinates(data2['Province'])
    m = folium.Map(location=[(lat1+lat2)/2, (lon1+lon2)/2], zoom_start=6, tiles="CartoDB positron")
    folium.CircleMarker([lat1, lon1], radius=15, color="white", fill=True, fill_color="#3498DB", fill_opacity=1, popup=data1['Amphoe']).add_to(m)
    folium.CircleMarker([lat2, lon2], radius=15, color="white", fill=True, fill_color="#2ECC71", fill_opacity=1, popup=data2['Amphoe']).add_to(m)
    st_folium(m, height=400, use_container_width=True)

    rec = ""
    if data1['Score_Price'] < data2['Score_Price'] and data1['Score_Income'] > data2['Score_Income']: rec = f"✨ **{data1['Amphoe']}** คุ้มกว่า (ถูกกว่า+รวยกว่า)"
    elif data2['Score_Price'] < data1['Score_Price'] and data2['Score_Income'] > data1['Score_Income']: rec = f"✨ **{data2['Amphoe']}** คุ้มกว่า (ถูกกว่า+รวยกว่า)"
    elif data1['Total_Pop'] > data2['Total_Pop']: rec = f"🏙️ **{data1['Amphoe']}** คนเยอะกว่า เหมาะค้าขาย"
    else: rec = f"🏙️ **{data2['Amphoe']}** คนเยอะกว่า เหมาะค้าขาย"
    st.markdown(f"""<div style="background-color:var(--secondary-background-color); padding:20px; border-radius:10px; margin-top:20px; text-align:center; font-weight:600; border:1px solid rgba(128,128,128,0.1);">{rec}</div>""", unsafe_allow_html=True)