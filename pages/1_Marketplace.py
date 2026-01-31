import streamlit as st
import pandas as pd
import base64
import os
import numpy as np
from style_utils import apply_custom_style # ✅

st.set_page_config(page_title="SongTumLay Marketplace", layout="wide", page_icon="🏠")
apply_custom_style() # ✅

# --- Functions ---
def get_image_base64(path):
    if path is None or not os.path.exists(path): return None
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

def find_province_image(prov_name):
    if not prov_name: return None
    target_folders = ["images", "data/provinces"] 
    candidates = [prov_name]
    if "กรุงเทพ" in prov_name: candidates.extend(["กรุงเทพ", "กรุงเทพมหานคร"])
    for folder in target_folders:
        for name in candidates:
            for ext in [".png", ".jpg", ".jpeg"]:
                path = os.path.join(folder, name + ext)
                if os.path.exists(path): return path
    return None

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
    .card-img-container { height: 160px; width: 100%; display: flex; justify-content: center; align-items: center; padding: 15px; border-bottom: 1px solid rgba(128,128,128,0.1); }
    .card-img { max-height: 120px; max-width: 120px; object-fit: contain; }
    .card-body { padding: 15px 20px; flex-grow: 1; display: flex; flex-direction: column; }
    .card-price { color: #2ECC71; font-size: 22px; font-weight: 700; margin-top: auto; }
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero-container"><div style="font-size:42px; font-weight:800;">MARKETPLACE</div><div>ทำเลทอง 77 จังหวัด</div></div>""", unsafe_allow_html=True)

st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")
provinces = ["ทั้งหมด"] + sorted(list(df['Province'].unique())) if not df.empty else []
sel_prov = st.sidebar.selectbox("📍 เลือกจังหวัด", provinces)
amphoes = ["ทั้งหมด"]
if sel_prov != "ทั้งหมด": amphoes += sorted(df[df['Province'] == sel_prov]['Amphoe'].unique())
sel_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)

df_show = df.copy()
if sel_prov == "ทั้งหมด":
    df_show = df_show.sort_values('Est_Land_Price', ascending=False).drop_duplicates(subset=['Province'], keep='first').sort_values('Est_Land_Price', ascending=False)
else:
    df_show = df_show[df_show['Province'] == sel_prov]
    if sel_amphoe != "ทั้งหมด": df_show = df_show[df_show['Amphoe'] == sel_amphoe]
    df_show = df_show.sort_values('Est_Land_Price', ascending=False)

if not df_show.empty:
    cols_per_row = 4
    df_display = df_show.head(100)
    rows = [df_display.iloc[i:i+cols_per_row] for i in range(0, len(df_display), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, (index, item) in enumerate(row.iterrows()):
            with cols[i]:
                img_path = find_province_image(item['Province'])
                img_b64 = get_image_base64(img_path)
                img_html = f'<img src="data:image/png;base64,{img_b64}" class="card-img">' if img_b64 else f'<div style="font-size:40px; color:#CBD5E0; font-weight:bold;">{item["Province"][0]}</div>'
                card_html = f"""<div class="listing-card"><div class="card-img-container">{img_html}</div><div class="card-body"><div style="font-weight:800; font-size:18px;">ต. {item['Tambon']}</div><div style="font-size:14px; opacity:0.7;">📍 {item['Amphoe']}, {item['Province']}</div><div class="card-price">฿{item['Est_Land_Price']:,.0f}</div></div></div>"""
                st.markdown(card_html, unsafe_allow_html=True)
else: st.info("ไม่พบข้อมูล")