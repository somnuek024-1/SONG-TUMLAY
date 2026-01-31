import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def find_logo_file():
    candidates = ["logonobackground.png", "logo.png", "logo.jpg", "logo.jpeg"]
    for filename in candidates:
        if os.path.exists(filename):
            return filename
    return None

def apply_custom_style():
    target_file = find_logo_file()
    if not target_file:
        st.error("⚠️ ไม่พบไฟล์โลโก้")
        return

    img_base64 = get_base64_of_bin_file(target_file)

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Sarabun', sans-serif;
            color: var(--text-color);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            background: linear-gradient(180deg, #1A365D 0%, #142847 100%);
        }}

        /* ------------------------------------------------------- */
        /* 🎯 ส่วนจัดการโลโก้และเมนู */
        /* ------------------------------------------------------- */
        div[data-testid="stSidebarNav"] {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-repeat: no-repeat;
            background-position: center top 20px; 
            background-size: 280px auto;         
            
            /* ✅ 1. ขยับเมนูขึ้น: ลดตัวเลขนี้ลง (เดิม 320px -> 260px) */
            /* ถ้าอยากให้ขึ้นอีก ให้ลดเลขลง (เช่น 240px) */
            padding-top: 260px !important;       
        }}

        /* ✅ 2. เพิ่มขนาดเมนู (Home, Marketplace...) */
        div[data-testid="stSidebarNav"] > ul {{
            transform: scale(1.1);        /* ขยายใหญ่ขึ้น 8% (ถ้าอยากใหญ่กว่านี้ใส่ 1.1 หรือ 1.2) */
            transform-origin: top center; /* ขยายจากจุดกึ่งกลาง */
            width: 95% !important;        /* จัดความกว้างให้พอดี */
            margin: 0 auto;               /* จัดกึ่งกลาง */
        }}
        /* ------------------------------------------------------- */

        [data-testid="stSidebar"] * {{ color: white !important; }}

        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            color: var(--text-color) !important;
            background-color: var(--background-color) !important;
        }}
        
        .listing-card, .property-card, .stat-card {{
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid rgba(128, 128, 128, 0.2);
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

    with st.sidebar:
        st.write("") 
        st.markdown('<hr style="margin:10px 0; border:0; border-top:1px solid rgba(255,255,255,0.2);">', unsafe_allow_html=True)