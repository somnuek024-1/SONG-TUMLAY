import streamlit as st
import pandas as pd
import os
import numpy as np
from style_utils import apply_custom_style

st.set_page_config(page_title="SongTumLay Marketplace", layout="wide", page_icon="🏠")
apply_custom_style()

# --- Functions ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        latest_year = df['Year'].max()
        df_latest = df[df['Year'] == latest_year].copy()
        prov_pop_mean = df_latest.groupby('Province')['Total_Pop'].transform('mean').replace(0, 1)
        pop_ratio = df_latest['Total_Pop'] / prov_pop_mean
        df_latest['Factor_Density'] = np.power(pop_ratio, 0.3)
        df_latest['Factor_Centrality'] = df_latest['Amphoe'].apply(lambda x: 1.2 if ('เมือง' in str(x) or 'เขต' in str(x)) else 1.0)
        df_latest['Factor_Total'] = (df_latest['Factor_Density'] * df_latest['Factor_Centrality']).clip(0.5, 3.0)
        df_latest['Est_Land_Price'] = df_latest['Avg_Land_Price'] * df_latest['Factor_Total']
        return df_latest
    except: return pd.DataFrame()

df = load_data()

# --- CSS เฉพาะหน้า Marketplace ---
st.markdown("""
<style>
    .hero-container {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1596422846543-75c6fc197f07?q=80&w=2070&auto=format&fit=crop');
        background-size: cover; background-position: center; padding: 60px 20px; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 30px; color: white;
    }
    .card-body { 
        padding: 20px; 
        flex-grow: 1; display: flex; flex-direction: column; 
        min-height: 120px; 
    }
    .card-price { color: #2ECC71; font-size: 22px; font-weight: 700; margin-top: auto; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero-container"><div style="font-size:42px; font-weight:800;">MARKETPLACE</div><div>ทำเลทอง 77 จังหวัด</div></div>""", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

# 1. ช่องกรอกราคา (Input Number)
if not df.empty:
    min_val_data = int(df['Est_Land_Price'].min())
    max_val_data = int(df['Est_Land_Price'].max())
    
    st.sidebar.write("💰 **งบประมาณ (ทุน)**")
    
    col_min, col_max = st.sidebar.columns(2)
    
    with col_min:
        min_input = st.number_input("ต่ำสุด (Min)", min_value=0, max_value=max_val_data, value=min_val_data, step=50000)
        
    with col_max:
        max_input = st.number_input("สูงสุด (Max)", min_value=0, max_value=max_val_data, value=max_val_data, step=50000)
    
    price_range = (min_input, max_input)
else:
    price_range = (0, 0)

# 2. ตัวเลือกจังหวัดและอำเภอ
provinces = ["ทั้งหมด"] + sorted(list(df['Province'].unique())) if not df.empty else []
sel_prov = st.sidebar.selectbox("📍 เลือกจังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if sel_prov != "ทั้งหมด": amphoes += sorted(df[df['Province'] == sel_prov]['Amphoe'].unique())
sel_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)

# --- Logic การกรองข้อมูล ---
df_show = df.copy()

# กรองราคา
df_show = df_show[
    (df_show['Est_Land_Price'] >= price_range[0]) & 
    (df_show['Est_Land_Price'] <= price_range[1])
]

# กรองจังหวัดและอำเภอ
if sel_prov == "ทั้งหมด":
    df_show = df_show.sort_values('Est_Land_Price', ascending=False).drop_duplicates(subset=['Province'], keep='first').sort_values('Est_Land_Price', ascending=False)
else:
    df_show = df_show[df_show['Province'] == sel_prov]
    if sel_amphoe != "ทั้งหมด": df_show = df_show[df_show['Amphoe'] == sel_amphoe]
    df_show = df_show.sort_values('Est_Land_Price', ascending=False)

# --- Display Grid ---
if not df_show.empty:
    st.write(f"พบ {len(df_show)} รายการในช่วงราคา {price_range[0]:,} - {price_range[1]:,} บาท")
    
    cols_per_row = 4
    df_display = df_show.head(100)
    rows = [df_display.iloc[i:i+cols_per_row] for i in range(0, len(df_display), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, (index, item) in enumerate(row.iterrows()):
            with cols[i]:
                # ✅ จุดที่แก้ไข: ปรับ CSS ในบรรทัดที่แสดงชื่ออำเภอ/จังหวัด
                # 1. white-space: nowrap -> บังคับบรรทัดเดียว
                # 2. overflow: hidden; text-overflow: ellipsis; -> ถ้าชื่อยาวเกินให้ขึ้น ...
                # 3. font-size: 16px -> เพิ่มขนาด
                # 4. color: #000000 -> เปลี่ยนเป็นสีดำ
                
                card_html = f"""
                <div class="listing-card">
                    <div class="card-body">
                        <div style="font-weight:800; font-size:18px;">ต. {item['Tambon']}</div>
                        <div style="font-size:16px; color:#000000; margin-bottom:5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">📍 {item['Amphoe']}, {item['Province']}</div>
                        <div class="card-price">฿{item['Est_Land_Price']:,.0f}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("ไม่พบข้อมูลในช่วงราคานี้ ลองปรับงบประมาณใหม่นะครับ")
