"""
2_Compare_Locations.py — เปรียบเทียบทำเล Head-to-Head
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from style_utils import apply_custom_style, get_hero_bg_css
from data_utils import get_latest_data, get_all_years_data, score_color, score_grade

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SongTumLay — Compare",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded",
)
apply_custom_style()

# ─────────────────────────────────────────
# โหลดข้อมูล (จาก final_master_data_tambon_price.csv)
# ─────────────────────────────────────────
with st.spinner("🔄 กำลังโหลดข้อมูล..."):
    df      = get_latest_data()
    df_all  = get_all_years_data()

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
hero_bg = get_hero_bg_css(
    "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=2670&auto=format&fit=crop"
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
        ⚖️ COMPARE LOCATIONS
    </div>
    <div style="font-size:18px;opacity:0.85;">เปรียบเทียบศักยภาพทำเลแบบ Head-to-Head</div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("❌ ไม่พบข้อมูล กรุณาตรวจสอบไฟล์ CSV")
    st.stop()

# ─────────────────────────────────────────
# LOCATION SELECTORS
# ─────────────────────────────────────────
col_a, col_vs, col_b = st.columns([1, 0.15, 1])

all_provs = sorted(df["Province"].unique().tolist())

with col_a:
    st.markdown("### 🔵 ทำเลที่ 1 (Location A)")
    prov_a = st.selectbox("จังหวัด A", all_provs, key="prov_a")
    amps_a = sorted(df[df["Province"] == prov_a]["Amphoe"].unique().tolist())
    amp_a  = st.selectbox("อำเภอ A", amps_a, key="amp_a")
    tams_a = sorted(
        df[(df["Province"] == prov_a) & (df["Amphoe"] == amp_a)]["Tambon"].unique().tolist()
    )
    tam_a  = st.selectbox("ตำบล A", tams_a, key="tam_a")

with col_vs:
    st.markdown("<div style='text-align:center;padding-top:120px;"
                "font-size:28px;font-weight:900;color:#BDC3C7;'>VS</div>",
                unsafe_allow_html=True)

with col_b:
    st.markdown("### 🟠 ทำเลที่ 2 (Location B)")
    default_b = min(1, len(all_provs) - 1)
    prov_b = st.selectbox("จังหวัด B", all_provs, index=default_b, key="prov_b")
    amps_b = sorted(df[df["Province"] == prov_b]["Amphoe"].unique().tolist())
    amp_b  = st.selectbox("อำเภอ B", amps_b, key="amp_b")
    tams_b = sorted(
        df[(df["Province"] == prov_b) & (df["Amphoe"] == amp_b)]["Tambon"].unique().tolist()
    )
    tam_b  = st.selectbox("ตำบล B", tams_b, key="tam_b")

# ─────────────────────────────────────────
# ✅ ดึงข้อมูลด้วย Province+Amphoe+Tambon (ป้องกันชื่อซ้ำ)
# ─────────────────────────────────────────
try:
    row_a = df[
        (df["Province"] == prov_a) &
        (df["Amphoe"]   == amp_a)  &
        (df["Tambon"]   == tam_a)
    ].iloc[0]

    row_b = df[
        (df["Province"] == prov_b) &
        (df["Amphoe"]   == amp_b)  &
        (df["Tambon"]   == tam_b)
    ].iloc[0]
except IndexError:
    st.warning("กรุณาเลือกตำบลให้ครบทั้ง 2 ฝั่งครับ")
    st.stop()

# ✅ ตรวจเลือกซ้ำ
if prov_a == prov_b and amp_a == amp_b and tam_a == tam_b:
    st.warning("⚠️ กรุณาเลือกตำบลที่แตกต่างกันทั้ง 2 ฝั่ง")

st.markdown("---")

# ─────────────────────────────────────────
# HEAD-TO-HEAD CARDS
# ─────────────────────────────────────────
st.markdown("### ⚡ วัดกันที่ตัวเลขจริง (Head-to-Head)")


def compare_card(title: str, val_a: float, val_b: float, unit: str,
                 label_a: str, label_b: str) -> str:
    """สร้าง HTML การ์ดเปรียบเทียบ"""
    winner = "A" if val_a > val_b else ("B" if val_b > val_a else "Draw")
    ca = "#2ECC71" if winner == "A" else "#BDC3C7"
    cb = "#2ECC71" if winner == "B" else "#BDC3C7"
    total = val_a + val_b or 1
    fw_a = val_a / total * 100
    fw_b = val_b / total * 100
    win_a = "🏆 WIN" if winner == "A" else "&nbsp;"
    win_b = "🏆 WIN" if winner == "B" else "&nbsp;"

    return f"""
    <div style="background:white;padding:22px;border-radius:16px;
                box-shadow:0 4px 15px rgba(0,0,0,0.08);
                border:1px solid #eee;margin-bottom:20px;">
        <div style="font-size:15px;font-weight:700;color:#555;
                    text-align:center;margin-bottom:16px;">{title}</div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="text-align:center;width:42%;">
                <div style="font-size:11px;color:#999;margin-bottom:4px;">{label_a}</div>
                <div style="font-size:22px;font-weight:900;color:#1A365D;">
                    {val_a:,.0f}
                </div>
                <div style="font-size:11px;color:#888;">{unit}</div>
                <div style="font-size:12px;font-weight:700;color:{ca};margin-top:5px;">
                    {win_a}
                </div>
            </div>
            <div style="width:16%;text-align:center;">
                <div style="width:34px;height:34px;background:#F0F2F6;color:#888;
                            border-radius:50%;display:flex;align-items:center;
                            justify-content:center;font-weight:900;font-size:11px;
                            margin:0 auto;">VS</div>
            </div>
            <div style="text-align:center;width:42%;">
                <div style="font-size:11px;color:#999;margin-bottom:4px;">{label_b}</div>
                <div style="font-size:22px;font-weight:900;color:#1A365D;">
                    {val_b:,.0f}
                </div>
                <div style="font-size:11px;color:#888;">{unit}</div>
                <div style="font-size:12px;font-weight:700;color:{cb};margin-top:5px;">
                    {win_b}
                </div>
            </div>
        </div>
        <div style="margin-top:14px;display:flex;height:6px;
                    border-radius:3px;overflow:hidden;">
            <div style="width:{fw_a}%;background:{ca};"></div>
            <div style="width:2px;background:white;"></div>
            <div style="width:{fw_b}%;background:{cb};"></div>
        </div>
    </div>
    """


label_a = f"{tam_a} ({prov_a})"
label_b = f"{tam_b} ({prov_b})"

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(compare_card(
        "💰 ราคาที่ดิน (บาท/ตร.ว.)",
        row_a["Est_Land_Price"], row_b["Est_Land_Price"],
        "บาท/ตร.ว.", label_a, label_b,
    ), unsafe_allow_html=True)
with c2:
    st.markdown(compare_card(
        "💵 รายได้เฉลี่ยครัวเรือน",
        row_a["Avg_Income"], row_b["Avg_Income"],
        "บาท/เดือน", label_a, label_b,
    ), unsafe_allow_html=True)
with c3:
    st.markdown(compare_card(
        "👥 ประชากร",
        row_a["Total_Pop"], row_b["Total_Pop"],
        "คน", label_a, label_b,
    ), unsafe_allow_html=True)

# ─────────────────────────────────────────
# TOTAL SCORE
# ─────────────────────────────────────────
st.markdown("### 🏆 สรุปคะแนนรวม (Total Score)")
col_chart, col_winner = st.columns([2, 1])

with col_chart:
    metrics = ["คะแนนรวม", "Factor ทำเล (×3)", "Factor ความหนาแน่น (×3)"]
    vals_a  = [row_a["Total_Score"], row_a["Factor_Centrality"]*3, row_a["Factor_Density"]*3]
    vals_b  = [row_b["Total_Score"], row_b["Factor_Centrality"]*3, row_b["Factor_Density"]*3]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=metrics, x=vals_a, name=tam_a, orientation="h",
        marker_color="#3498DB",
        text=[f"{v:.2f}" for v in vals_a], textposition="auto",
    ))
    fig.add_trace(go.Bar(
        y=metrics, x=vals_b, name=tam_b, orientation="h",
        marker_color="#E67E22",
        text=[f"{v:.2f}" for v in vals_b], textposition="auto",
    ))
    fig.update_layout(
        barmode="group", height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sarabun", color="white"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=1.12, font=dict(color="white")),
        xaxis=dict(showgrid=True, gridcolor="#333"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_winner:
    score_diff  = abs(row_a["Total_Score"] - row_b["Total_Score"])
    if row_a["Total_Score"] > row_b["Total_Score"]:
        winner_name  = tam_a
        winner_prov  = prov_a
        winner_score = row_a["Total_Score"]
        winner_color = "#3498DB"
    elif row_b["Total_Score"] > row_a["Total_Score"]:
        winner_name  = tam_b
        winner_prov  = prov_b
        winner_score = row_b["Total_Score"]
        winner_color = "#E67E22"
    else:
        winner_name  = "เสมอ!"
        winner_prov  = ""
        winner_score = row_a["Total_Score"]
        winner_color = "#2ECC71"

    st.markdown(f"""
    <div style="background:#F4F6F7;padding:28px;border-radius:14px;
                text-align:center;border:2px solid #BDC3C7;height:100%;">
        <div style="font-size:16px;color:#555;margin-bottom:8px;">🏅 ผู้ชนะ</div>
        <div style="font-size:28px;font-weight:900;color:{winner_color};
                    margin-bottom:4px;">{winner_name}</div>
        <div style="font-size:13px;color:#999;margin-bottom:16px;">{winner_prov}</div>
        <div style="font-size:42px;font-weight:900;color:#1A365D;margin-bottom:4px;">
            {winner_score:.1f}
        </div>
        <div style="font-size:13px;color:#7F8C8D;">
            นำอยู่ <b>{score_diff:.2f}</b> แต้ม
        </div>
        <div style="margin-top:16px;font-size:48px;">👑</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# TREND CHART (ถ้ามีข้อมูลหลายปี)
# ─────────────────────────────────────────
if not df_all.empty:
    st.markdown("---")
    st.markdown("### 📈 Trend ราคาตลอด 5 ปี")

    # ✅ filter ด้วย Province+Amphoe+Tambon พร้อมกัน
    trend_a = df_all[
        (df_all["Province"] == prov_a) &
        (df_all["Amphoe"]   == amp_a)  &
        (df_all["Tambon"]   == tam_a)
    ].sort_values("Year")

    trend_b = df_all[
        (df_all["Province"] == prov_b) &
        (df_all["Amphoe"]   == amp_b)  &
        (df_all["Tambon"]   == tam_b)
    ].sort_values("Year")

    if not trend_a.empty and not trend_b.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=trend_a["Year"], y=trend_a["Est_Land_Price"],
            mode="lines+markers", name=tam_a,
            line=dict(color="#3498DB", width=3),
            marker=dict(size=8),
        ))
        fig2.add_trace(go.Scatter(
            x=trend_b["Year"], y=trend_b["Est_Land_Price"],
            mode="lines+markers", name=tam_b,
            line=dict(color="#E67E22", width=3),
            marker=dict(size=8),
        ))
        fig2.update_layout(
            height=350,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Sarabun", color="white"),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.12, font=dict(color="white")),
            xaxis=dict(showgrid=False, title="ปี พ.ศ."),
            yaxis=dict(showgrid=True, gridcolor="#333", title="ราคา (บาท/ตร.ว.)"),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("ไม่พบข้อมูล Trend สำหรับทำเลที่เลือก")
