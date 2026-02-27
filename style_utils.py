import streamlit as st
import base64
import os


# ==========================================
# ⚙️ Helper Functions
# ==========================================
def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def find_logo_file() -> str | None:
    candidates = ["logonobackground.png", "logo.png", "logo.jpg", "logo.jpeg"]
    for filename in candidates:
        if os.path.exists(filename):
            return filename
    return None


def apply_custom_style():
    """
    ฝัง CSS ทั้งหมดครั้งเดียว:
    - Dark Theme กลาง (ใช้ทุกหน้า)
    - Sidebar + Logo
    - Widget (Select, NumberInput)
    - Card components (mk-card, property-card, stat-card, compare-card)
    """

    # --- โลโก้ Sidebar ---
    target_file = find_logo_file()
    logo_css = ""
    if target_file:
        img_b64 = get_base64_of_bin_file(target_file)
        logo_css = f"""
            background-image: url("data:image/png;base64,{img_b64}");
            background-repeat: no-repeat;
            background-position: center top 20px;
            background-size: 260px auto;
            padding-top: 250px !important;
        """

    st.markdown(
        f"""
    <style>
    /* ── FONT ── */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800;900&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Sarabun', sans-serif;
    }}

    /* ── DARK APP BACKGROUND ── */
    [data-testid="stAppViewContainer"] {{
        background-color: #1A2228;
        color: #ffffff;
    }}
    header[data-testid="stHeader"] {{
        background-color: #1A2228;
    }}

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, #1A365D 0%, #142847 100%);
    }}
    div[data-testid="stSidebarNav"] {{
        {logo_css}
    }}
    div[data-testid="stSidebarNav"] > ul {{
        transform: scale(1.06);
        transform-origin: top center;
        width: 95% !important;
        margin: 0 auto;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}

    /* ── DROPDOWN (Dark) ── */
    div[data-baseweb="select"] > div {{
        background-color: #262730 !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.2) !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: #ffffff !important;
    }}

    /* ── NUMBER INPUT (Dark) ── */
    div[data-testid="stNumberInput"] input {{
        color: #ffffff !important;
        background-color: #262730 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 4px;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }}

    /* ── TEXT ── */
    .stMarkdown, p, h1, h2, h3, label,
    .stSelectbox label, [data-testid="stMarkdownContainer"] p {{
        color: #ffffff !important;
    }}

    /* ── HERO BANNER ── */
    .hero-banner {{
        background-size: cover;
        background-position: center;
        padding: 55px 20px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 28px;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }}
    .hero-title {{
        font-size: 46px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
        color: white;
    }}
    .hero-sub {{
        font-size: 18px;
        font-weight: 300;
        opacity: 0.88;
        color: white;
    }}

    /* ── MARKETPLACE CARD (mk-card) ── */
    .mk-card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
        border: 1px solid rgba(180,180,180,0.25);
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .mk-title-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }}
    .mk-title-text {{
        font-weight: 800;
        font-size: 17px;
        color: #111111;
        line-height: 1.25;
        width: 72%;
    }}
    .mk-score-badge {{
        background-color: #1A365D;
        color: white;
        padding: 5px 11px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 900;
        text-align: center;
        white-space: nowrap;
    }}
    .mk-location {{
        font-size: 13px;
        color: #666666;
        margin-bottom: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .mk-footer {{ margin-top: auto; }}
    .mk-divider {{ border-top: 1px dashed #ddd; margin-bottom: 12px; }}
    .mk-price {{
        color: #2ECC71;
        font-size: 20px;
        font-weight: 700;
    }}

    /* ── HOME TOP-5 CARD (property-card) ── */
    .property-card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid rgba(128,128,128,0.2);
    }}
    .card-title-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }}
    .card-title-text {{
        font-weight: 800;
        font-size: 18px;
        color: #111111 !important;
        flex: 1;
    }}
    .score-badge {{
        background-color: #1A365D;
        color: white !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 900;
        white-space: nowrap;
    }}
    .card-location {{
        font-size: 13px;
        color: #666666 !important;
        margin-bottom: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .card-divider {{ border-top: 1px dashed #ddd; margin: 12px 0; }}
    .card-price {{
        font-weight: bold;
        color: #2ECC71 !important;
        font-size: 22px;
    }}

    /* ── STAT CARD (dark bg) ── */
    .stat-card {{
        background-color: #262730;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    .stat-label {{ font-size: 13px; color: #aaaaaa; margin-bottom: 6px; }}
    .stat-value {{ font-size: 24px; font-weight: 800; }}

    /* ── MAP LEGEND ── */
    .map-legend {{
        background-color: #262730;
        padding: 18px 22px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 16px;
    }}
    .legend-dot {{
        width: 18px; height: 18px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        vertical-align: middle;
    }}

    /* ── COMPARE CARD ── */
    .compare-card {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        border: 1px solid #eee;
        margin-bottom: 20px;
    }}
    .compare-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: #444444;
        margin-bottom: 14px;
        text-align: center;
    }}
    .compare-value {{
        font-size: 22px;
        font-weight: 900;
        color: #1A365D;
    }}

    /* ── SIDEBAR DIVIDER ── */
    .sidebar-divider {{
        margin: 14px 0;
        border: 0;
        border-top: 1px solid rgba(255,255,255,0.18);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
