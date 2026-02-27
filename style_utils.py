"""
style_utils.py — CSS และ Helper ทั้งหมด
"""

import streamlit as st
import base64
import os


def _b64(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _mime_type(filepath: str) -> str:
    """ตรวจ MIME type จาก header bytes จริง"""
    with open(filepath, "rb") as f:
        header = f.read(8)
    if header[:2] == b'\xff\xd8':
        return "image/jpeg"
    if header[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if header[:4] == b'RIFF':
        return "image/webp"
    return "image/jpeg"


def _find_file(candidates: list) -> str | None:
    for f in candidates:
        if os.path.exists(f):
            return f
    return None


def get_hero_bg_css(fallback_url: str = "") -> str:
    bg = _find_file(["background.jpg", "background.png", "background.webp"])
    if bg:
        mime = _mime_type(bg)
        return f"url('data:{mime};base64,{_b64(bg)}')"
    if fallback_url:
        return f"url('{fallback_url}')"
    return "linear-gradient(135deg,#1A365D 0%,#2C5282 100%)"


def apply_custom_style():
    """เรียกครั้งเดียวในทุกหน้า — ฝัง CSS ทั้งหมด"""

    # ── โลโก้ ──
    logo_file = _find_file([
        "logo.png",
        "logonobackgroundoriginal.png",
        "logonobackground.png",
        "logo.jpg",
    ])

    logo_css = ""
    if logo_file:
        b64  = _b64(logo_file)
        mime = _mime_type(logo_file)
        logo_css = f"""
            background-image: url("data:{mime};base64,{b64}");
            background-repeat: no-repeat;
            background-position: center top 20px;
            /* ปรับให้โลโก้กว้าง 85% ของแถบ เพื่อให้ใหญ่เต็มตาแต่ไม่ล้น */
            background-size: 85% auto; 
            padding-top: 260px !important;
        """

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
       SIDEBAR (แก้ปัญหากรอบสี่เหลี่ยมแยกสี)
    ═══════════════════════════════════════ */
    /* 1. บังคับสีพื้นหลัง Sidebar ตัวแม่ให้เป็นสีน้ำเงินเข้มสีเดียวทั้งแผ่น */
    [data-testid="stSidebar"] > div:first-child {{
        background: #1A365D !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* 2. ทำให้กล่องโลโก้ (stSidebarNav) โปร่งใส เพื่อให้กลืนไปกับสีหลัก */
    div[data-testid="stSidebarNav"] {{
        {logo_css}
        background-color: transparent !important; 
    }}

    /* ลบสีพื้นหลังของกล่องย่อยๆ ออกให้หมด */
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
    div[data-testid="stSidebarNav"] > ul {{
        transform: scale(1.05);
        transform-origin: top center;
        width: 95% !important;
        margin: 0 auto;
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
        caret-color: #ffffff !important;
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: #333842 !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: white !important;
    }}

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
    }}

    /* ═══════════════════════════════════════
       TYPOGRAPHY
    ═══════════════════════════════════════ */
    .stMarkdown p, .stMarkdown li, h1, h2, h3, label, p {{
        color: #ffffff !important;
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

    .dark-stat-box {{
        background-color: #262730;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)
