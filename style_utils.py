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
        logo_css = f"""
            background-image: url("data:image/png;base64,{img_base64}");
            background-repeat: no-repeat;
            background-position: center top 20px; 
            background-size: 280px auto; 
            padding-top: 260px !important; 
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

        /* จัดการส่วนเมนู Navigation */
        div[data-testid="stSidebarNav"] {{
            {logo_css}
        }}

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
        
        .sidebar-divider {{
            margin: 15px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        /* ============================================================
           ✅ ส่วนที่แก้ไข: บังคับการ์ดให้สูงเท่ากันและจัดระเบียบภายใน
           ============================================================ */
        .listing-card, .property-card, .stat-card {{
            background-color: #FFFFFF !important;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #E0E0E0;
            padding: 25px;

            /* 1. ตั้งค่าความสูงขั้นต่ำ (แก้เลขนี้ถ้าต้องการให้สูง/เตี้ยลง) */
            min-height: 180px; 
            
            /* 2. ใช้ Flexbox จัดระเบียบแนวตั้ง */
            display: flex;
            flex-direction: column;
            justify-content: space-between; /* ดันเนื้อหาหัว-ท้ายแยกกัน */
        }}

        /* เทคนิคพิเศษ: ดัน div ตัวสุดท้าย (ส่วนราคา) ไปชิดขอบล่างเสมอ */
        .property-card > div:last-child, .listing-card .card-body > div:last-child {{
             margin-top: auto !important; /* เขียนทับ inline style เดิมใน home.py */
             padding-top: 15px;          /* เพิ่มช่องว่างเหนือราคา */
        }}

        /* บังคับตัวหนังสือข้างในให้เป็นสีเข้ม */
        .listing-card div, .property-card div, .stat-card div {{
            color: #31333F; 
        }}

        /* ยกเว้น: ราคาให้เป็นสีเขียว */
        .card-price, div[style*="color:#2ECC71"] {{
            color: #2ECC71 !important;
        }}
        
        /* ยกเว้น: ป้ายคะแนน */
        div[style*="background:#1A365D"] {{
            color: #FFFFFF !important;
        }}
        
        .vs-badge {{
            background-color: #31333F; 
            color: #FFFFFF;
            width: 40px; height: 40px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 900;
            border: 2px solid #FFFFFF;
        }}
    </style>
    """, unsafe_allow_html=True)
