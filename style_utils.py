"""
style_utils.py — CSS และ Helper ทั้งหมด (เวอร์ชันแก้ไขสมบูรณ์)
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

    # ✅ แสดงโลโก้ผ่าน st.sidebar.image() แทน CSS background-image
    # วิธีนี้เสถียรกว่ามาก ไม่โดน Streamlit override
    # ✅ logo.png คือไฟล์ที่ไม่มีพื้นหลัง — ขึ้นก่อนเสมอ
    logo_file = _find_file([
        "logo.png",
        "logonobackgroundoriginal.png",
        "logonobackground.png",
        "logo.jpg",
    ])
    if logo_file:
        try:
            st.sidebar.image(logo_file, use_container_width=True)
        except Exception:
            pass

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    /* ── Dark Background ── */
    [data-testid="stAppViewContainer"] { background-color: #1A2228; }
    header[data-testid="stHeader"]     { background-color: #1A2228; }

    /* ═══════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════ */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1A365D 0%, #0F2137 100%);
    }

    /* ✅ ระบุ element ชัดเจน ไม่ใช้ * wildcard
       เพื่อป้องกันการ override background ของ element อื่น */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small {
        color: white !important;
    }

    /* โลโก้ที่แสดงผ่าน st.sidebar.image() */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        background: transparent !important;
        padding: 24px 28px 16px 28px !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        border-radius: 0 !important;
        display: block;
    }
    /* กำจัด margin/padding รอบๆ image widget */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        background: transparent !important;
    }

    /* ── Sidebar Nav (กล่องเมนู) ── */
    div[data-testid="stSidebarNav"] {
        background-color: #1A365D !important;
        padding-bottom: 8px;
    }

    /* ลบ background ออกจาก element ลูกใน nav */
    div[data-testid="stSidebarNav"] ul,
    div[data-testid="stSidebarNav"] li {
        background-color: transparent !important;
    }
    div[data-testid="stSidebarNav"] a {
        background-color: transparent !important;
        color: white !important;
    }
    div[data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 8px;
    }
    div[data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: rgba(255,255,255,0.18) !important;
        border-radius: 8px;
        font-weight: 700;
    }
    div[data-testid="stSidebarNav"] > ul {
        transform: scale(1.05);
        transform-origin: top center;
        width: 95% !important;
        margin: 0 auto;
    }

    /* ═══════════════════════════════════════
       WIDGETS
    ═══════════════════════════════════════ */
    /* Dropdown */
    div[data-baseweb="select"] > div {
        background-color: #262730 !important;
        color: white !important;
        border-color: rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
    }

    /* Number Input */
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #262730 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #333842 !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: white !important;
    }

    /* Sidebar dropdown override */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
    }

    /* ═══════════════════════════════════════
       CARDS
    ═══════════════════════════════════════ */
    .property-card, .mk-card {
        background-color: #ffffff !important;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(0,0,0,0.06);
    }

    /* ═══════════════════════════════════════
       DARK STAT BOX
    ═══════════════════════════════════════ */
    .dark-stat-box {
        background-color: #262730;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
