import streamlit as st
import math

from style_utils import apply_custom_style
from data_utils import load_and_process, filter_df

st.set_page_config(page_title="SongTumLay Marketplace", layout="wide", page_icon="🏠")
apply_custom_style()

# ── Data ───────────────────────────────────────────────────────────────────
df_all = load_and_process()

# ── Sidebar Filters ────────────────────────────────────────────────────────
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

if not df_all.empty:
    price_min_data = int(df_all["Est_Land_Price"].min())
    price_max_data = int(df_all["Est_Land_Price"].max())

    st.sidebar.write("💰 **งบประมาณ (ทุน)**")
    col_min, col_max = st.sidebar.columns(2)
    with col_min:
        min_input = st.number_input(
            "ต่ำสุด (Min)", min_value=0, max_value=price_max_data,
            value=price_min_data, step=50_000
        )
    with col_max:
        max_input = st.number_input(
            "สูงสุด (Max)", min_value=0, max_value=price_max_data,
            value=price_max_data, step=50_000
        )
else:
    min_input, max_input = 0, 0

provinces = ["ทั้งหมด"] + sorted(df_all["Province"].unique().tolist()) if not df_all.empty else ["ทั้งหมด"]
sel_prov = st.sidebar.selectbox("📍 เลือกจังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if sel_prov != "ทั้งหมด" and not df_all.empty:
    amphoes += sorted(df_all[df_all["Province"] == sel_prov]["Amphoe"].unique().tolist())
sel_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)

# ── Search Box ─────────────────────────────────────────────────────────────
# (แก้ปัญหา UX: ค้นหาชื่อตำบลได้โดยตรง)
search_text = st.sidebar.text_input("🔎 ค้นหาชื่อตำบล", placeholder="พิมพ์ชื่อตำบล...")

# ── Hero Banner ────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-banner" style="
    background-image: linear-gradient(rgba(0,0,0,0.68), rgba(0,0,0,0.68)),
    url('https://images.unsplash.com/photo-1596422846543-75c6fc197f07?q=80&w=2070&auto=format&fit=crop');
">
    <div class="hero-title">MARKETPLACE</div>
    <div class="hero-sub">ทำเลทอง 77 จังหวัด</div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Filter & Sort data ─────────────────────────────────────────────────────
df_show = filter_df(df_all, province=sel_prov, amphoe=sel_amphoe,
                    price_min=min_input, price_max=max_input)

# Full-text search
if search_text and not df_show.empty:
    df_show = df_show[df_show["Tambon"].str.contains(search_text, na=False)]

# ถ้าเลือก "ทั้งหมด" → แสดงตัวแทน 1 ตำบล/จังหวัด (ราคาสูงสุด)
if sel_prov == "ทั้งหมด":
    df_show = (
        df_show
        .sort_values("Est_Land_Price", ascending=False)
        .drop_duplicates(subset=["Province"], keep="first")
        .sort_values("Est_Land_Price", ascending=False)
    )
else:
    df_show = df_show.sort_values("Est_Land_Price", ascending=False)

# ── Display Grid ───────────────────────────────────────────────────────────
if df_show.empty:
    st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข ลองปรับตัวกรองใหม่นะครับ")
else:
    st.markdown(
        f"<div style='color:#aaa; margin-bottom:16px;'>พบ <b style='color:white;'>{len(df_show)}</b> รายการ</div>",
        unsafe_allow_html=True,
    )

    COLS = 4   # จำนวนคอลัมน์ต่อแถว
    rows = [df_show.iloc[i : i + COLS] for i in range(0, len(df_show), COLS)]

    for row_df in rows:
        cols = st.columns(COLS)
        for i, (_, item) in enumerate(row_df.iterrows()):
            with cols[i]:
                score_val = f"{item['Total_Score']:.2f}"
                grade_color = (
                    "#2ECC71" if item["Total_Score"] >= 6
                    else ("#F1C40F" if item["Total_Score"] >= 3 else "#E74C3C")
                )
                st.markdown(
                    f"""
<div class="mk-card">
    <div class="mk-title-row">
        <div class="mk-title-text">{item['Tambon']}</div>
        <div class="mk-score-badge" style="border-left: 3px solid {grade_color};">{score_val}</div>
    </div>
    <div class="mk-location">📍 {item['Amphoe']}, {item['Province']}</div>
    <div class="mk-footer">
        <div class="mk-divider"></div>
        <div class="mk-price">฿{item['Est_Land_Price']:,.0f}
            <span style="font-size:12px; color:#888; font-weight:normal;">/ตร.ว.</span>
        </div>
        <div style="font-size:12px; color:#999; margin-top:6px;">
            👥 {item['Total_Pop']:,} คน &nbsp;|&nbsp; 💵 ฿{item['Avg_Income']:,.0f}/เดือน
        </div>
    </div>
</div>
""",
                    unsafe_allow_html=True,
                )

        # เติม cols ว่างให้ครบแถว (ป้องกัน layout แตก)
        remaining = COLS - len(row_df)
        for j in range(remaining):
            with cols[len(row_df) + j]:
                st.empty()
