import streamlit as st
import base64
import os

# ==========================================
# ⚙️ Helper Functions
# ==========================================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def find_logo_file():
    """ค้นหาไฟล์โลโก้ (รองรับหลายนามสกุล)"""
    candidates = ["logonobackground.png", "logo.png", "logo.jpg", "logo.jpeg"]
    for filename in candidates:
        if os.path.exists(filename):
            return filename
    return None

def apply_custom_style():
    """ฟังก์ชันหลักสำหรับฝัง CSS"""
    
    # 1. เตรียมรูปโลโก้
    target_file = find_logo_file()
    logo_css = ""
    
    if target_file:
        img_base64 = get_base64_of_bin_file(target_file)
        # CSS สำหรับฝังโลโก้ลงในเมนู
        logo_css = f"""
            background-image: url("data:image/png;base64,{img_base64}");
            background-repeat: no-repeat;
            background-position: center top 20px; 
            background-size: 280px auto; /* ขนาดรูป */
            padding-top: 260px !important; /* ดันเมนูลงมา */
        """

    # 2. ฝัง CSS ทั้งหมด
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Sarabun', sans-serif;
            color: var(--text-color);
        }}

        /* --- Sidebar Styling --- */
        [data-testid="stSidebar"] > div:first-child {{
            background: linear-gradient(180deg, #1A365D 0%, #142847 100%);
        }}

        /* จัดการส่วนเมนู Navigation (ใส่โลโก้ + ขยับตำแหน่ง) */
        div[data-testid="stSidebarNav"] {{
            {logo_css}
        }}

        /* ขยายขนาดเมนูให้ใหญ่ขึ้นเล็กน้อย */
        div[data-testid="stSidebarNav"] > ul {{
            transform: scale(1.08);
            transform-origin: top center;
            width: 95% !important;
            margin: 0 auto;
        }}

        /* สีตัวหนังสือใน Sidebar */
        [data-testid="stSidebar"] * {{ color: white !important; }}

        /* แก้สี Dropdown ใน Sidebar */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            color: var(--text-color) !important;
            background-color: var(--background-color) !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] svg {{
            fill: var(--text-color) !important;
        }}
        
        /* เส้นคั่น */
        .sidebar-divider {{
            margin: 15px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        /* --- Card Styling (Top 5 & Stats) --- */
        .listing-card, .property-card, .stat-card {{
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 25px; 
        }}
        
        .vs-badge {{
            background-color: var(--text-color); color: var(--background-color);
            width: 40px; height: 40px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 900;
            border: 2px solid var(--secondary-background-color);
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # ❌ ลบส่วน with st.sidebar ด้านล่างนี้ออกไปแล้ว เพื่อไม่ให้มีช่องว่างเกินจำเป็น
