import streamlit as st
import plotly.graph_objects as go

from style_utils import apply_custom_style
from data_utils import load_and_process

# ── 1. Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Compare Locations", layout="wide", page_icon="⚖️")
apply_custom_style()

# ── 2. Data ────────────────────────────────────────────────────────────────
df = load_and_process()

# ── 3. Hero Banner ─────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-banner" style="
    background-image: linear-gradient(rgba(0,0,0,0.62), rgba(0,0,0,0.62)),
    url('https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=2670&auto=format&fit=crop');
">
    <div class="hero-title">COMPARE LOCATIONS</div>
    <div class="hero-sub">เปรียบเทียบศักยภาพทำเลแบบ Head-to-Head</div>
</div>
""",
    unsafe_allow_html=True,
)

# ── 4. Location Selectors ──────────────────────────────────────────────────
if df.empty:
    st.error("ไม่พบข้อมูล กรุณาตรวจสอบไฟล์ CSV")
    st.stop()

provinces = sorted(df["Province"].unique().tolist())

col_a, col_vs, col_b = st.columns([1, 0.15, 1])

with col_a:
    st.markdown("### 🔵 ทำเลที่ 1 (Location A)")
    prov_a = st.selectbox("จังหวัด A", provinces, key="p_a")
    amp_list_a = sorted(df[df["Province"] == prov_a]["Amphoe"].unique().tolist())
    amp_a = st.selectbox("อำเภอ A", amp_list_a, key="a_a")
    tam_list_a = sorted(
        df[(df["Province"] == prov_a) & (df["Amphoe"] == amp_a)]["Tambon"].unique().tolist()
    )
    tam_a = st.selectbox("ตำบล A", tam_list_a, key="t_a")

with col_vs:
    st.markdown(
        "<div style='text-align:center; margin-top:90px; font-size:28px; font-weight:900; color:#BDC3C7;'>VS</div>",
        unsafe_allow_html=True,
    )

with col_b:
    st.markdown("### 🟠 ทำเลที่ 2 (Location B)")
    default_b_idx = min(1, len(provinces) - 1)
    prov_b = st.selectbox("จังหวัด B", provinces, index=default_b_idx, key="p_b")
    amp_list_b = sorted(df[df["Province"] == prov_b]["Amphoe"].unique().tolist())
    amp_b = st.selectbox("อำเภอ B", amp_list_b, key="a_b")
    tam_list_b = sorted(
        df[(df["Province"] == prov_b) & (df["Amphoe"] == amp_b)]["Tambon"].unique().tolist()
    )
    tam_b = st.selectbox("ตำบล B", tam_list_b, key="t_b")

# ── 5. Fetch rows ──────────────────────────────────────────────────────────
try:
    row_a = df[
        (df["Province"] == prov_a) & (df["Amphoe"] == amp_a) & (df["Tambon"] == tam_a)
    ].iloc[0]
    row_b = df[
        (df["Province"] == prov_b) & (df["Amphoe"] == amp_b) & (df["Tambon"] == tam_b)
    ].iloc[0]
except IndexError:
    st.warning("กรุณาเลือกตำบลให้ครบทั้ง 2 ฝั่งครับ")
    st.stop()

st.markdown("---")

# ── 6. Head-to-Head Cards ──────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:22px; font-weight:800; margin-bottom:18px; color:white;'>⚡ วัดกันที่ตัวเลขจริง (Head-to-Head)</div>",
    unsafe_allow_html=True,
)


def compare_card(title: str, val_a: float, val_b: float, unit: str, format_func=None) -> str:
    """สร้าง HTML การ์ดเปรียบเทียบ 2 ค่า"""
    if format_func is None:
        fmt = lambda v: f"{v:,.0f}"
    else:
        fmt = format_func

    winner = "A" if val_a > val_b else ("B" if val_b > val_a else "D")
    col_a  = "#2ECC71" if winner == "A" else ("#BDC3C7" if winner != "D" else "#F1C40F")
    col_b  = "#2ECC71" if winner == "B" else ("#BDC3C7" if winner != "D" else "#F1C40F")
    total  = val_a + val_b or 1
    bar_a  = val_a / total * 100
    bar_b  = val_b / total * 100
    badge_a = "🏆 WIN" if winner == "A" else ("🤝" if winner == "D" else "&nbsp;")
    badge_b = "🏆 WIN" if winner == "B" else ("🤝" if winner == "D" else "&nbsp;")

    return f"""
<div class="compare-card">
    <div class="compare-card-title">{title}</div>
    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
        <div style="text-align:center; width:40%;">
            <div style="font-size:11px; font-weight:700; color:#3498DB; margin-bottom:4px;">ทำเล A</div>
            <div class="compare-value" style="color:#1A365D;">{fmt(val_a)}</div>
            <div style="font-size:11px; color:#888; margin-top:2px;">{unit}</div>
            <div style="font-size:13px; font-weight:700; color:{col_a}; margin-top:6px;">{badge_a}</div>
        </div>
        <div style="width:14%; text-align:center;">
            <div style="width:34px; height:34px; background:#F0F2F6; color:#555;
                        border-radius:50%; display:flex; align-items:center;
                        justify-content:center; font-weight:900; font-size:11px; margin:0 auto;">VS</div>
        </div>
        <div style="text-align:center; width:40%;">
            <div style="font-size:11px; font-weight:700; color:#E67E22; margin-bottom:4px;">ทำเล B</div>
            <div class="compare-value" style="color:#1A365D;">{fmt(val_b)}</div>
            <div style="font-size:11px; color:#888; margin-top:2px;">{unit}</div>
            <div style="font-size:13px; font-weight:700; color:{col_b}; margin-top:6px;">{badge_b}</div>
        </div>
    </div>
    <div style="margin-top:14px; display:flex; height:5px; border-radius:3px; overflow:hidden;">
        <div style="width:{bar_a:.1f}%; background:{col_a};"></div>
        <div style="width:2px; background:white;"></div>
        <div style="width:{bar_b:.1f}%; background:{col_b};"></div>
    </div>
</div>
"""


c_price, c_income, c_pop = st.columns(3)
with c_price:
    st.markdown(
        compare_card("💰 ราคาที่ดิน (Est. Land Price)", row_a["Est_Land_Price"], row_b["Est_Land_Price"], "บาท/ตร.ว."),
        unsafe_allow_html=True,
    )
with c_income:
    st.markdown(
        compare_card("💵 รายได้เฉลี่ย (Avg Income)", row_a["Avg_Income"], row_b["Avg_Income"], "บาท/เดือน"),
        unsafe_allow_html=True,
    )
with c_pop:
    st.markdown(
        compare_card("👥 ประชากร (Population)", row_a["Total_Pop"], row_b["Total_Pop"], "คน"),
        unsafe_allow_html=True,
    )

# ── 7. Factor Comparison ───────────────────────────────────────────────────
c_density, c_central, c_score = st.columns(3)
with c_density:
    st.markdown(
        compare_card(
            "📊 Factor ความหนาแน่น",
            row_a["Factor_Density"], row_b["Factor_Density"], "×",
            format_func=lambda v: f"{v:.2f}",
        ),
        unsafe_allow_html=True,
    )
with c_central:
    st.markdown(
        compare_card(
            "🏙️ Factor ทำเล",
            row_a["Factor_Centrality"], row_b["Factor_Centrality"], "×",
            format_func=lambda v: f"{v:.1f}",
        ),
        unsafe_allow_html=True,
    )
with c_score:
    st.markdown(
        compare_card(
            "⭐ คะแนนรวม (Total Score)",
            row_a["Total_Score"], row_b["Total_Score"], "คะแนน",
            format_func=lambda v: f"{v:.2f}",
        ),
        unsafe_allow_html=True,
    )

# ── 8. Chart + Winner Card ─────────────────────────────────────────────────
st.markdown("### 📊 กราฟเปรียบเทียบตัวชี้วัดหลัก")

col_chart, col_winner = st.columns([2, 1])

with col_chart:
    metrics   = ["คะแนนรวม", "Factor ทำเล (×3)", "Factor ความหนาแน่น (×3)"]
    vals_a    = [row_a["Total_Score"], row_a["Factor_Centrality"] * 3, row_a["Factor_Density"] * 3]
    vals_b    = [row_b["Total_Score"], row_b["Factor_Centrality"] * 3, row_b["Factor_Density"] * 3]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=metrics, x=vals_a, name=f"A: {row_a['Tambon']}", orientation="h",
        marker_color="#3498DB", text=[f"{v:.2f}" for v in vals_a], textposition="auto",
    ))
    fig.add_trace(go.Bar(
        y=metrics, x=vals_b, name=f"B: {row_b['Tambon']}", orientation="h",
        marker_color="#E67E22", text=[f"{v:.2f}" for v in vals_b], textposition="auto",
    ))
    fig.update_layout(
        barmode="group", height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sarabun", color="white", size=13),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=1.12, font=dict(color="white")),
        xaxis=dict(showgrid=True, gridcolor="#2d3540"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_winner:
    score_diff  = abs(row_a["Total_Score"] - row_b["Total_Score"])
    is_a_winner = row_a["Total_Score"] > row_b["Total_Score"]
    is_draw     = row_a["Total_Score"] == row_b["Total_Score"]

    if is_draw:
        winner_name = "เสมอกัน!"
        winner_color = "#F1C40F"
        diff_text = "คะแนนเท่ากันทุกประการ 🤝"
        crown = "🤝"
    else:
        winner_name = row_a["Tambon"] if is_a_winner else row_b["Tambon"]
        winner_color = "#3498DB" if is_a_winner else "#E67E22"
        winner_prov  = row_a["Province"] if is_a_winner else row_b["Province"]
        diff_text = f"คะแนนนำอยู่ <b>{score_diff:.2f}</b> แต้ม"
        crown = "👑"

    st.markdown(
        f"""
<div style="
    background:#1e2832;
    padding:28px 22px;
    border-radius:14px;
    text-align:center;
    border:2px solid {winner_color};
    height:100%;
    box-sizing:border-box;
">
    <div style="font-size:15px; color:#aaa; margin-bottom:6px;">🏆 ผู้ชนะคือ</div>
    <div style="font-size:26px; font-weight:900; color:{winner_color}; margin:10px 0; line-height:1.2;">
        {winner_name}
    </div>
    {'<div style="font-size:13px; color:#aaa; margin-bottom:14px;">' + winner_prov + '</div>' if not is_draw else ''}
    <div style="font-size:14px; color:#ccc; margin-bottom:16px;">{diff_text}</div>
    <div style="font-size:52px;">{crown}</div>
</div>
""",
        unsafe_allow_html=True,
    )

# ── 9. Detail Summary Table ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 สรุปข้อมูลเปรียบเทียบ")

import pandas as pd
summary = pd.DataFrame({
    "ตัวชี้วัด": [
        "ตำบล", "อำเภอ", "จังหวัด",
        "ราคาประเมิน AI (฿/ตร.ว.)", "รายได้เฉลี่ย (฿/เดือน)",
        "ประชากร (คน)", "Factor ความหนาแน่น", "Factor ทำเล", "คะแนนรวม",
    ],
    "ทำเล A 🔵": [
        row_a["Tambon"], row_a["Amphoe"], row_a["Province"],
        f"฿{row_a['Est_Land_Price']:,.0f}", f"฿{row_a['Avg_Income']:,.0f}",
        f"{row_a['Total_Pop']:,}", f"{row_a['Factor_Density']:.2f}",
        f"{row_a['Factor_Centrality']:.1f}", f"{row_a['Total_Score']:.2f}",
    ],
    "ทำเล B 🟠": [
        row_b["Tambon"], row_b["Amphoe"], row_b["Province"],
        f"฿{row_b['Est_Land_Price']:,.0f}", f"฿{row_b['Avg_Income']:,.0f}",
        f"{row_b['Total_Pop']:,}", f"{row_b['Factor_Density']:.2f}",
        f"{row_b['Factor_Centrality']:.1f}", f"{row_b['Total_Score']:.2f}",
    ],
})
st.dataframe(summary, use_container_width=True, hide_index=True)
