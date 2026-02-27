"""
1_Marketplace.py — ตลาดทำเล: กรอง + แสดงการ์ดแบบ Grid
"""

import streamlit as st
import pandas as pd

from style_utils import apply_custom_style, get_hero_bg_css
from data_utils import get_latest_data, score_color, score_grade

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SongTumLay — Marketplace",
    layout="wide",
    page_icon="🏠",
    initial_sidebar_state="expanded",
)
apply_custom_style()

# CSS เพิ่มเติมเฉพาะหน้า Marketplace
st.markdown("""
<style>
.mk-card {
    background-color: #ffffff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.05);
    height: 100%;
    display: flex;
    flex-direction: column;
}
.mk-title {
    font-weight: 800;
    font-size: 17px;
    color: #111111;
    line-height: 1.3;
    margin-bottom: 4px;
}
.mk-location {
    font-size: 13px;
    color: #666666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 12px;
}
.mk-footer {
    margin-top: auto;
    border-top: 1px dashed #ddd;
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.mk-price {
    color: #2ECC71;
    font-size: 20px;
    font-weight: 700;
}
.mk-badge {
    background: linear-gradient(135deg,#1A365D,#2C5282);
    color: white;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 900;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# โหลดข้อมูล (จาก final_master_data_tambon_price.csv)
# ─────────────────────────────────────────
with st.spinner("🔄 กำลังโหลดข้อมูล..."):
    df = get_latest_data()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

min_price = max_price = 0
price_range = (0, 0)

if not df.empty:
    min_price = int(df["Est_Land_Price"].min())
    max_price = int(df["Est_Land_Price"].max())

    st.sidebar.write("💰 **งบประมาณ (บาท/ตร.ว.)**")
    price_range = st.sidebar.slider(
        "ช่วงราคา",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=1_000,
        format="฿%d",
        label_visibility="collapsed",
    )
    st.sidebar.caption(f"฿{price_range[0]:,} — ฿{price_range[1]:,}")

provinces = (
    ["ทั้งหมด"] + sorted(df["Province"].unique().tolist())
    if not df.empty else ["ทั้งหมด"]
)
sel_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if sel_prov != "ทั้งหมด" and not df.empty:
    amphoes += sorted(df[df["Province"] == sel_prov]["Amphoe"].unique().tolist())
sel_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)

# Sort options
sort_opts = {
    "คะแนนสูงสุด":    ("Total_Score",     False),
    "ราคาสูง → ต่ำ":  ("Est_Land_Price",  False),
    "ราคาต่ำ → สูง":  ("Est_Land_Price",  True),
    "ประชากรมากสุด":   ("Total_Pop",       False),
}
sort_label = st.sidebar.selectbox("📊 เรียงตาม", list(sort_opts.keys()))
sort_col, sort_asc = sort_opts[sort_label]

st.sidebar.markdown("---")
st.sidebar.caption(f"📅 ข้อมูลปีล่าสุด")
st.sidebar.caption("© 2024 SongTumLay")

# ─────────────────────────────────────────
# FILTER + SORT
# ─────────────────────────────────────────
df_show = pd.DataFrame()
if not df.empty:
    df_show = df[
        (df["Est_Land_Price"] >= price_range[0]) &
        (df["Est_Land_Price"] <= price_range[1])
    ].copy()

    if sel_prov != "ทั้งหมด":
        df_show = df_show[df_show["Province"] == sel_prov]
        if sel_amphoe != "ทั้งหมด":
            df_show = df_show[df_show["Amphoe"] == sel_amphoe]
    else:
        # ถ้าดูทั้งหมด → แสดงตัวแทน 1 ตำบลต่อจังหวัด (คะแนนสูงสุด)
        df_show = (
            df_show
            .sort_values("Total_Score", ascending=False)
            .drop_duplicates(subset=["Province"], keep="first")
        )

    df_show = df_show.sort_values(sort_col, ascending=sort_asc)

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
hero_bg = get_hero_bg_css(
    "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?q=80&w=2070&auto=format&fit=crop"
)
st.markdown(f"""
<div style="
    background-image: linear-gradient(rgba(0,0,0,0.65),rgba(0,0,0,0.65)), {hero_bg};
    background-size:cover; background-position:center;
    padding:55px 20px; border-radius:14px; text-align:center;
    margin-bottom:28px; color:white;
    box-shadow:0 8px 30px rgba(0,0,0,0.4);
">
    <div style="font-size:52px;font-weight:900;letter-spacing:2px;margin-bottom:8px;">
        🏠 MARKETPLACE
    </div>
    <div style="font-size:18px;opacity:0.85;">ทำเลทอง 77 จังหวัดทั่วไทย</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# RESULT COUNT
# ─────────────────────────────────────────
if not df_show.empty:
    st.markdown(
        f"<div style='color:#aaa;margin-bottom:16px;'>"
        f"พบ <b style='color:white'>{len(df_show):,}</b> รายการ"
        f" • เรียงตาม <b style='color:white'>{sort_label}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────
    # CARD GRID (4 คอลัมน์)
    # ─────────────────────────────────────────
    COLS = 4
    rows = [df_show.iloc[i:i+COLS] for i in range(0, len(df_show), COLS)]

    for row_df in rows:
        cols = st.columns(COLS)
        for i, (_, item) in enumerate(row_df.iterrows()):
            with cols[i]:
                grade = score_grade(item["Total_Score"])
                clr   = score_color(item["Total_Score"])
                # ป้ายรายได้ครัวเรือน
                income_str = f"฿{item['Avg_Income']:,.0f}/เดือน" if pd.notna(item['Avg_Income']) else ""

                st.markdown(f"""
<div class="mk-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div class="mk-title">{item['Tambon']}</div>
        <div class="mk-badge">{item['Total_Score']:.1f}</div>
    </div>
    <div class="mk-location">📍 {item['Amphoe']}, {item['Province']}</div>
    <div style="display:flex;gap:8px;margin-bottom:4px;flex-wrap:wrap;">
        <span style="background:{clr}22;color:{clr};border:1px solid {clr};
                     padding:2px 8px;border-radius:20px;font-size:11px;
                     font-weight:700;">เกรด {grade}</span>
        <span style="background:#1e2a35;color:#aaa;
                     padding:2px 8px;border-radius:20px;font-size:11px;">
            👥 {item['Total_Pop']:,} คน
        </span>
    </div>
    <div class="mk-footer">
        <div class="mk-price">
            ฿{item['Est_Land_Price']:,.0f}
            <span style="font-size:12px;color:#888;font-weight:400;">/ตร.ว.</span>
        </div>
        <div style="font-size:11px;color:#999;">{income_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("ไม่พบข้อมูลในช่วงราคานี้ ลองปรับตัวกรองใหม่นะครับ 🙏")
