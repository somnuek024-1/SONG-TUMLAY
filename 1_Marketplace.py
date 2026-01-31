import streamlit as st
import pandas as pd
import base64
import os
import numpy as np # ต้องใช้ numpy สำหรับคำนวณสูตร

# --- 1. Config ---
st.set_page_config(page_title="SongTumLay Marketplace", layout="wide", page_icon="🏠")

# ==========================================
# 🖼️ ระบบจัดการรูปภาพ
# ==========================================
def get_image_base64(path):
    """แปลงไฟล์รูปภาพเป็น Base64 string เพื่อฝังใน HTML"""
    if path is None or not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

def find_province_image(prov_name):
    if not prov_name:
        return None
    target_folders = ["images", "data/provinces"] 
    extensions = [".png", ".jpg", ".jpeg"]
    candidates = [prov_name]
    if "กรุงเทพ" in prov_name:
        candidates.append("กรุงเทพ")
        candidates.append("กรุงเทพมหานคร")
    
    for folder in target_folders:
        for name in candidates:
            for ext in extensions:
                path = os.path.join(folder, name + ext)
                if os.path.exists(path):
                    return path
                clean_name = name.replace("จ.", "").strip()
                path_clean = os.path.join(folder, clean_name + ext)
                if os.path.exists(path_clean):
                    return path_clean
    return None

# --- 2. Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
        color: #1A202C;
    }
    
    .hero-container {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1596422846543-75c6fc197f07?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        padding: 60px 20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .hero-title { font-size: 42px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }
    .hero-subtitle { font-size: 18px; font-weight: 300; margin-bottom: 10px; color: #E2E8F0; }

    .listing-card {
        background: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
    }
    .listing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-color: #CBD5E0;
    }
    
    .card-img-container {
        height: 160px;
        width: 100%;
        background: radial-gradient(circle, #F7FAFC 0%, #EDF2F7 100%);
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid #EDF2F7;
    }
    .card-img {
        max-height: 120px;
        max-width: 120px;
        object-fit: contain;
        filter: drop-shadow(0 4px 4px rgba(0,0,0,0.1));
        transition: transform 0.3s;
    }
    .listing-card:hover .card-img { transform: scale(1.1); }

    .card-body { padding: 15px 20px; flex-grow: 1; display: flex; flex-direction: column; }
    .card-title-text { font-size: 18px; font-weight: 800; color: #2D3748; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-loc { font-size: 14px; color: #718096; margin-bottom: 10px; display: flex; align-items: center; gap: 4px; }
    .card-price { color: #2ECC71; font-size: 22px; font-weight: 700; margin-top: auto; } /* เปลี่ยนเป็นสีเขียวเหมือน Dashboard */
    .unit-text { font-size: 13px; color: #A0AEC0; font-weight: normal; }

    .card-stats {
        display: flex; justify-content: space-between; background-color: #F7FAFC;
        padding: 10px 20px; border-top: 1px solid #EDF2F7; font-size: 13px; color: #4A5568; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Load Data & Apply Logic (เหมือน Dashboard) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        latest_year = df['Year'].max()
        df_latest = df[df['Year'] == latest_year].copy()
        
        # --- 🧠 เพิ่มสูตรคำนวณ (Logic เดียวกับ Dashboard) ---
        prov_pop_mean = df_latest.groupby('Province')['Total_Pop'].transform('mean').replace(0, 1)
        pop_ratio = df_latest['Total_Pop'] / prov_pop_mean
        
        df_latest['Factor_Density'] = np.power(pop_ratio, 0.3)
        
        def check_centrality(amphoe_name):
            return 1.2 if ('เมือง' in str(amphoe_name) or 'เขต' in str(amphoe_name)) else 1.0
        
        df_latest['Factor_Centrality'] = df_latest['Amphoe'].apply(check_centrality)
        df_latest['Factor_Total'] = (df_latest['Factor_Density'] * df_latest['Factor_Centrality']).clip(0.5, 3.0)
        
        # สร้างราคาประเมิน (Est_Land_Price)
        df_latest['Est_Land_Price'] = df_latest['Avg_Land_Price'] * df_latest['Factor_Total']
        
        return df_latest
    except:
        return pd.DataFrame()

df = load_data()

# --- 4. UI ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">MARKETPLACE</div>
    <div class="hero-subtitle">แหล่งรวมข้อมูลศักยภาพทำเลทอง 77 จังหวัดทั่วไทย (วิเคราะห์ด้วย AI Model)</div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🔍 ค้นหาพื้นที่")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    provinces = ["ทั้งหมด"] + sorted(list(df['Province'].unique())) if not df.empty else []
    sel_prov = st.selectbox("📍 เลือกจังหวัด", provinces)

with c2:
    amphoes = ["ทั้งหมด"]
    if sel_prov != "ทั้งหมด":
        amphoes += sorted(df[df['Province'] == sel_prov]['Amphoe'].unique())
    sel_amphoe = st.selectbox("🏙️ เลือกอำเภอ/เขต", amphoes)

with c3:
    st.write("")
    st.write("")
    st.markdown('<div style="text-align:right; color:#718096; font-size:14px; padding-top:10px;">ข้อมูลอัปเดตล่าสุด ✅</div>', unsafe_allow_html=True)

# --- 5. Data Filtering ---
df_show = df.copy()

# 🔴 LOGIC ใหม่: แสดง Top ของแต่ละจังหวัดเมื่อเลือกทั้งหมด โดยใช้ Est_Land_Price
if sel_prov == "ทั้งหมด":
    # 1. เรียงตามราคาประเมิน (Est_Land_Price)
    df_show = df_show.sort_values('Est_Land_Price', ascending=False)
    
    # 2. ตัดซ้ำ เอา Top 1 ของแต่ละจังหวัด
    df_show = df_show.drop_duplicates(subset=['Province'], keep='first')
    
    # 3. เรียงอีกรอบเพื่อโชว์จังหวัดที่แพงที่สุดก่อน
    df_show = df_show.sort_values('Est_Land_Price', ascending=False)
    
    msg_status = f"🏆 แสดงทำเลศักยภาพสูงสุดของแต่ละจังหวัด (เรียงตามราคาประเมินโมเดล)"

else:
    df_show = df_show[df_show['Province'] == sel_prov]
    if sel_amphoe != "ทั้งหมด":
        df_show = df_show[df_show['Amphoe'] == sel_amphoe]
        
    # เรียงตามราคาประเมินเช่นกัน
    df_show = df_show.sort_values('Est_Land_Price', ascending=False)
    msg_status = f"**ผลการค้นหา: {len(df_show):,} รายการ**"

# --- 6. Listings Grid ---
st.markdown(f"---")
st.markdown(msg_status)

if not df_show.empty:
    cols_per_row = 4
    max_items = 100
    if len(df_show) > max_items:
        st.caption(f"แสดง {max_items} รายการแรก")
        df_display = df_show.head(max_items)
    else:
        df_display = df_show

    rows = [df_display.iloc[i:i+cols_per_row] for i in range(0, len(df_display), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, (index, item) in enumerate(row.iterrows()):
            with cols[i]:
                img_path = find_province_image(item['Province'])
                img_b64 = get_image_base64(img_path)
                
                if img_b64:
                    img_html = f'<img src="data:image/png;base64,{img_b64}" class="card-img" alt="{item["Province"]}">'
                else:
                    initial = item['Province'][0] if item['Province'] else "?"
                    img_html = f'<div style="font-size:40px; color:#CBD5E0; font-weight:bold;">{initial}</div>'

                # ✅ เปลี่ยนมาโชว์ราคา Est_Land_Price เพื่อให้ตรงกับ Dashboard
                price_txt = f"฿{item['Est_Land_Price']:,.0f}"
                
                card_html = f"""<div class="listing-card"><div class="card-img-container">{img_html}</div><div class="card-body"><div class="card-title-text">ต. {item['Tambon']}</div><div class="card-loc">📍 {item['Amphoe']}, {item['Province']}</div><div class="card-price">{price_txt} <span class="unit-text">/ตร.ว.</span></div></div><div class="card-stats"><span>👥 {item['Total_Pop']:,}</span><span>💰 {item['Avg_Income']/1000:.1f}k</span></div></div>"""
                
                st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("ไม่พบข้อมูลตามเงื่อนไข")