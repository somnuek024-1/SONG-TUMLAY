import streamlit as st
import base64
import os
import mimetypes

def _b64(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _find_file(candidates: list) -> str | None:
    for f in candidates:
        if os.path.exists(f):
            return f
    return None

def apply_custom_style():
    """เรียกครั้งเดียวในทุกหน้า — ฝัง CSS ทั้งหมด"""

    # ── 1. โลโก้ (เปลี่ยนวิธีอ่านไฟล์ให้ปลอดภัยขึ้น) ──
    logo_file = _find_file([
        "logo.png",
        "logonobackgroundoriginal.png",
        "logonobackground.png",
        "logo.jpg",
        "logo.jpeg"
    ])

    logo_css = ""
    if logo_file:
        b64 = _b64(logo_file)
        mime_type, _ = mimetypes.guess_type(logo_file)
        if not mime_type:
            mime_type = "image/png"

        logo_css = f"""
            background-image: url("data:{mime_type};base64,{b64}");
            background-repeat: no-repeat;
            background-position: center top 20px;
            background-size: 70% auto; /* ปรับขนาดโลโก้ */
            padding-top: 240px !important;
        """
    else:
        st.sidebar.warning("⚠️ ไม่พบไฟล์รูปโลโก้")

    # ── 2. ฝัง CSS ขั้นเด็ดขาด ──
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {{
        font-family: 'Sarabun', sans-serif;
    }}

    [data-testid="stAppViewContainer"] {{ background-color: #1A2228; }}
    header[data-testid="stHeader"]     {{ background-color: transparent; }}

    /* ═══════════════════════════════════════
       SIDEBAR BACKGROUND (บังคับสีทึบทั้งหมด)
    ═══════════════════════════════════════ */
    /* เล็งเป้าไปที่ section ตัวแม่ของ Sidebar เพื่อบังคับให้สีเนียนจรดขอบล่าง */
    section[data-testid="stSidebar"] {{
        background-color: #1A365D !important;
        border-right: none !important;
    }}
    
    /* ล้างสีพื้นหลังของ div ลูกๆ ทิ้งทั้งหมด เพื่อให้สีแม่ทะลุขึ้นมา */
    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* ── Logo + Nav ── */
    div[data-testid="stSidebarNav"] {{
        {logo_css}
        background-color: transparent !important;
    }}

    div[data-testid="stSidebarNav"] ul,
    div[data-testid="stSidebarNav"] li,
    div[data-testid="stSidebarNav"] a,
    div[data-testid="stSidebarNav"] span {{
        background-color: transparent !important;
    }}

    div[data-testid="stSidebarNav"] a:hover {{
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 8px;
    }}
    div[data-testid="stSidebarNav"] a[aria-current="page"] {{
        background-color: rgba(255,255,255,0.18) !important;
        border-radius: 8px;
        font-weight: 700;
    }}

    /* ═══════════════════════════════════════
       WIDGETS
    ═══════════════════════════════════════ */
    div[data-baseweb="select"] > div {{
        background-color: #262730 !important;
        color: white !important;
        border-color: rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stNumberInput"] input {{
        color: #ffffff !important;
        background-color: #262730 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)
