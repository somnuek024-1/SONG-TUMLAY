"""
style_utils.py — CSS และ Helper ทั้งหมด
"""

import streamlit as st
import base64
import os


def _b64(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _find_file(candidates: list[str]) -> str | None:
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

    # ✅ แก้ไขชื่อไฟล์โลโก้ให้ตรงกับไฟล์จริง
    logo_file = _find_file([
        "logo.png",
        
    ])
    logo_css = ""
    if logo_file:
        b64 = _b64(logo_file)
        logo_css = f"""
            background-image: url("data:image/png;base64,{b64}");
            background-repeat: no-repeat;
            background-position: center top 20px;
            background-size: 260px auto;
            padding-top: 255px !important;
            background-color: #1A365D;
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

    /* ── Sidebar ── */
    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, #1A365D 0%, #0F2137 100%);
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}

    /* ── ทำให้ทุกส่วนใน Sidebar กลืนกับพื้นหลัง ── */
    [data-testid="stSidebar"] section[data-testid="stSidebarContent"] {{
        background: transparent !important;
    }}

    /* กล่อง Nav (โลโก้ + เมนู) */
    div[data-testid="stSidebarNav"] {{
        {logo_css}
        background: linear-gradient(180deg, #1A365D 0%, #0F2137 100%) !important;
    }}

    /* ลบพื้นขาวออกจาก Nav container ทุก layer */
    div[data-testid="stSidebarNav"] *,
    div[data-testid="stSidebarNav"]::before,
    div[data-testid="stSidebarNav"]::after {{
        background-color: transparent !important;
    }}

    /* กล่องเมนูแต่ละ item */
    div[data-testid="stSidebarNav"] ul li {{
        background: transparent !important;
    }}
    div[data-testid="stSidebarNav"] ul li a {{
        background: transparent !important;
        color: white !important;
    }}
    div[data-testid="stSidebarNav"] ul li a:hover {{
        background: rgba(255,255,255,0.12) !important;
        border-radius: 8px;
    }}

    /* Active page highlight */
    div[data-testid="stSidebarNav"] ul li a[aria-current="page"] {{
        background: rgba(255,255,255,0.18) !important;
        border-radius: 8px;
    }}

    /* เส้นคั่นระหว่าง nav กับ widget */
    div[data-testid="stSidebarNav"] + div {{
        background: transparent !important;
    }}

    div[data-testid="stSidebarNav"] > ul {{
        transform: scale(1.06);
        transform-origin: top center;
        width: 95% !important;
        margin: 0 auto;
    }}

    /* ── Typography (Dark theme) ── */
    .stMarkdown p, .stMarkdown li,
    h1, h2, h3, label, p {{ color: #ffffff !important; }}

    /* ── Widgets ── */
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
    /* Slider track */
    div[data-testid="stSlider"] label {{ color: white !important; }}

    /* ── Sidebar dropdown override ── */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: rgba(255,255,255,0.08) !important;
        color: white !important;
    }}

    /* ── White Card ── */
    .property-card, .mk-card {{
        background-color: #ffffff !important;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.05);
    }}

    /* ── Dark Stat Box ── */
    .dark-stat-box {{
        background-color: #262730;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)
