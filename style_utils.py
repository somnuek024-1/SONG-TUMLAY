"""
style_utils.py — CSS และ Helper ทั้งหมด
"""

import streamlit as st
import base64
import os


def _b64(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _find_file(candidates: list) -> str | None:
    for f in candidates:
        if os.path.exists(f):
            return f
    return None


def get_hero_bg_css(fallback_url: str = "") -> str:
    """คืน CSS background-image — ใช้ไฟล์ local ก่อน ถ้าไม่มีใช้ URL"""
    bg = _find_file(["background.jpg", "background.png", "background.webp"])
    if bg:
        ext = bg.split(".")[-1].replace("jpg", "jpeg")
        return f"url('data:image/{ext};base64,{_b64(bg)}')"
    if fallback_url:
        return f"url('{fallback_url}')"
    return "linear-gradient(135deg,#1A365D 0%,#2C5282 100%)"


def apply_custom_style():
    """เรียกครั้งเดียวในทุกหน้า — ฝัง CSS ทั้งหมด"""

    # ── โลโก้: อ่านเป็น base64 เพื่อฝังใน CSS
    # ใน Streamlit multipage app, stSidebarNav อยู่เหนือ sidebar content
    # วิธีเดียวที่โลโก้จะอยู่เหนือ nav คือใส่เป็น CSS background-image
    logo_b64 = ""
    logo_file = _find_file([
        "logo.png",                       # ✅ ไฟล์ที่ user เตรียมไว้ (ไม่มีพื้นหลัง)
        "logonobackgroundoriginal.png",
        "logonobackground.png",
        "logo.jpg",
    ])
    if logo_file:
        logo_b64 = _b64(logo_file)

    # ── กำหนด CSS สำหรับโลโก้ (ถ้ามีไฟล์)
    # ⚠️ สำคัญ: ต้องใช้ background-image และ background-color แยกกัน
    #    ห้ามใช้ background shorthand เพราะจะ reset background-image ทิ้ง
    if logo_b64:
        logo_section_css = f"""
            /* โลโก้อยู่เหนือ nav — ใช้ background-image บน stSidebarNav */
            div[data-testid="stSidebarNav"] {{
                background-image: url("data:image/png;base64,{logo_b64}") !important;
                background-repeat: no-repeat !important;
                background-position: center 24px !important;
                background-size: 200px auto !important;
                /* ✅ background-color แยก property — ไม่ทับ background-image */
                background-color: #1A365D !important;
                padding-top: 220px !important;
                padding-bottom: 8px !important;
            }}
        """
    else:
        logo_section_css = """
            div[data-testid="stSidebarNav"] {
                background-color: #1A365D !important;
                padding-bottom: 8px !important;
            }
        """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {{
        font-family: 'Sarabun', sans-serif;
    }}

    /* ── Dark Background ── */
    [data-testid="stAppViewContainer"] {{ background-color: #1A2228; }}
    header[data-testid="stHeader"]     {{ background-color: #1A2228; }}

    /* ═══════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════ */
    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, #1A365D 0%, #0F2137 100%);
    }}

    /* สีตัวอักษรใน Sidebar — ระบุ element เฉพาะ ไม่ใช้ * wildcard */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .stMarkdown {{
        color: white !important;
    }}

    /* ═══════════════════════════════════════
       SIDEBAR NAV + LOGO
    ═══════════════════════════════════════ */
    {logo_section_css}

    /* ลบ background ออกจาก element ลูกใน nav (ไม่แตะ stSidebarNav เอง) */
    div[data-testid="stSidebarNav"] ul,
    div[data-testid="stSidebarNav"] li {{
        background-color: transparent !important;
    }}
    div[data-testid="stSidebarNav"] a {{
        background-color: transparent !important;
        color: rgba(255,255,255,0.85) !important;
    }}
    div[data-testid="stSidebarNav"] a:hover {{
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 8px;
        color: white !important;
    }}
    div[data-testid="stSidebarNav"] a[aria-current="page"] {{
        background-color: rgba(255,255,255,0.18) !important;
        border-radius: 8px;
        font-weight: 700;
        color: white !important;
    }}

    /* Scale nav items */
    div[data-testid="stSidebarNav"] > ul {{
        transform: scale(1.05);
        transform-origin: top center;
        width: 95% !important;
        margin: 0 auto;
    }}

    /* ═══════════════════════════════════════
       WIDGETS
    ═══════════════════════════════════════ */
    /* Dropdown */
    div[data-baseweb="select"] > div {{
        background-color: #262730 !important;
        color: white !important;
        border-color: rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }}

    /* Number Input */
    div[data-testid="stNumberInput"] input {{
        color: #ffffff !important;
        background-color: #262730 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: #333842 !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: white !important;
    }}

    /* Sidebar dropdown */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
    }}

    /* ═══════════════════════════════════════
       CARDS
    ═══════════════════════════════════════ */
    .property-card, .mk-card {{
        background-color: #ffffff !important;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(0,0,0,0.06);
    }}

    /* ═══════════════════════════════════════
       DARK STAT BOX
    ═══════════════════════════════════════ */
    .dark-stat-box {{
        background-color: #262730;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)
