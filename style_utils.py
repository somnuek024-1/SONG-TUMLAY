"""
style_utils.py — CSS และ Helper ทั้งหมด
"""

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


def get_hero_bg_css(fallback_url: str = "") -> str:
    """คืน CSS background-image — ใช้ไฟล์ local ก่อน ถ้าไม่มีใช้ URL"""
    bg = _find_file(["background.jpg", "background.png", "background.webp"])
    if bg:
        mime, _ = mimetypes.guess_type(bg)
        if not mime: mime = "image/jpeg"
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
            background-size: 70% auto;
            padding-top: 240px !important;
        """
    else:
        st.sidebar.warning("⚠️ ไม่พบไฟล์รูปโลโก้ กรุณาเช็คชื่อไฟล์")

    # ── ฝัง CSS ──
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {{
        font-family: 'Sarabun', sans-serif;
    }}

    /* ── Dark Background ── */
    [data-testid="stAppViewContainer"] {{ background-color: #1A2228; }}
    header[data-testid="stHeader"]     {{ background-color: transparent; }}

    /* ═══════════════════════════════════════
       SIDEBAR BACKGROUND (บังคับสีทึบทั้งหมด)
    ═══════════════════════════════════════ */
    section[data-testid="stSidebar"] {{
        background-color: #1A365D !important;
        border-right: none !important;
    }}
    
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
