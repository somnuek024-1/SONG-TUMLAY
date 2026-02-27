"""
home.py — หน้าหลัก: แผนที่ + Top5 + Price Breakdown
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go

from style_utils import apply_custom_style, get_hero_bg_css
from data_utils import get_latest_data, score_color, score_grade

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="SongTumLay — ส่องทำเล",
    layout="wide",
    page_icon="🏙️",
    initial_sidebar_state="expanded",
)
apply_custom_style()

# ─────────────────────────────────────────
# โหลดข้อมูล (จาก final_master_data_tambon_price.csv)
# ─────────────────────────────────────────
with st.spinner("🔄 กำลังโหลดข้อมูล..."):
    df_view = get_latest_data()

latest_year = int(df_view["Year"].max()) if not df_view.empty else 0

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

# ✅ ป้องกัน NameError — กำหนดค่า default ก่อนเสมอ
min_price = max_price = 0
price_range = (0, 0)

if not df_view.empty:
    min_price = int(df_view["Est_Land_Price"].min())
    max_price = int(df_view["Est_Land_Price"].max())

    st.sidebar.write("💰 **งบประมาณ (บาท/ตร.ว.)**")
    # ✅ เปลี่ยนเป็นกรอกตัวเลข 2 ช่อง ตามที่ผู้ใช้ต้องการ
    col_min, col_max = st.sidebar.columns(2)
    with col_min:
        input_min = st.number_input(
            "ต่ำสุด", min_value=0, max_value=max_price,
            value=min_price, step=1_000, key="input_min"
        )
    with col_max:
        input_max = st.number_input(
            "สูงสุด", min_value=0, max_value=max_price,
            value=max_price, step=1_000, key="input_max"
        )
    # ป้องกัน min > max
    if input_min > input_max:
        st.sidebar.warning("⚠️ ค่าต่ำสุดต้องไม่มากกว่าค่าสูงสุด")
        input_min, input_max = input_max, input_min
    price_range = (input_min, input_max)

provinces = (
    ["ทั้งหมด"] + sorted(df_view["Province"].unique().tolist())
    if not df_view.empty else ["ทั้งหมด"]
)
sel_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if sel_prov != "ทั้งหมด" and not df_view.empty:
    amphoes += sorted(
        df_view[df_view["Province"] == sel_prov]["Amphoe"].unique().tolist()
    )
sel_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)

st.sidebar.markdown("---")
st.sidebar.caption(f"📅 ข้อมูลล่าสุด ปี พ.ศ. {latest_year}")
st.sidebar.caption("© 2024 SongTumLay — ส่องทำเล")

# ─────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────
df_display = pd.DataFrame()
if not df_view.empty:
    df_display = df_view[
        (df_view["Est_Land_Price"] >= price_range[0]) &
        (df_view["Est_Land_Price"] <= price_range[1])
    ].copy()
    if sel_prov   != "ทั้งหมด": df_display = df_display[df_display["Province"] == sel_prov]
    if sel_amphoe != "ทั้งหมด": df_display = df_display[df_display["Amphoe"]   == sel_amphoe]

# ─────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────
subtitle = f"พื้นที่: {sel_prov}" if sel_prov != "ทั้งหมด" else "ภาพรวมประเทศไทย 77 จังหวัด"
if price_range != (min_price, max_price):
    subtitle += f"  •  ฿{price_range[0]:,} – ฿{price_range[1]:,}"

hero_bg = get_hero_bg_css(
    "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2613&auto=format&fit=crop"
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
        🏙️ แผนที่วิเคราะห์ทำเล
    </div>
    <div style="font-size:18px;opacity:0.85;">{subtitle}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAP  +  TOP-5 LIST
# ─────────────────────────────────────────
col_map, col_list = st.columns([2, 1.2])

with col_map:
    # ── Folium Map ──
    if not df_display.empty:
        center = [df_display["lat"].mean(), df_display["lon"].mean()]
        zoom   = 6 if sel_prov == "ทั้งหมด" else (10 if sel_amphoe == "ทั้งหมด" else 12)
    else:
        center, zoom = [13.7563, 100.5018], 6

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

    if not df_display.empty:
        mc = MarkerCluster().add_to(m)
        # ✅ itertuples เร็วกว่า iterrows ~4x
        for row in df_display.itertuples(index=False):
            if pd.notna(row.lat):
                clr   = score_color(row.Total_Score)
                grade = score_grade(row.Total_Score)
                popup = (
                    f"<div style='font-family:sans-serif;min-width:160px;'>"
                    f"<b style='font-size:15px'>{row.Tambon}</b><br>"
                    f"<span style='color:#666'>{row.Amphoe}, {row.Province}</span>"
                    f"<hr style='margin:6px 0'>"
                    f"💰 <b>฿{row.Est_Land_Price:,.0f}</b>/ตร.ว.<br>"
                    f"👥 ประชากร {row.Total_Pop:,} คน<br>"
                    f"🏅 เกรด <b style='color:{clr}'>{grade}</b> ({row.Total_Score:.1f}/10)"
                    f"</div>"
                )
                folium.CircleMarker(
                    location=[row.lat, row.lon],
                    radius=6, color=clr,
                    fill=True, fill_color=clr, fill_opacity=0.9,
                    popup=folium.Popup(popup, max_width=230),
                    tooltip=f"{row.Tambon} — ฿{row.Est_Land_Price:,.0f}",
                ).add_to(mc)

    st_folium(m, height=480, use_container_width=True)

    # ── Summary Stats ──
    if not df_display.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 สรุปสถิติพื้นที่")
        c1, c2, c3 = st.columns(3)
        for col, label, val, clr in [
            (c1, "ราคาเฉลี่ย (ตร.ว.)",  f"฿{df_display['Est_Land_Price'].mean():,.0f}", "#2ECC71"),
            (c2, "คะแนนเฉลี่ย",          f"{df_display['Total_Score'].mean():.1f} / 10",  "#3498DB"),
            (c3, "จำนวนพื้นที่",          f"{len(df_display):,} แห่ง",                   "#F1C40F"),
        ]:
            with col:
                st.markdown(f"""
                <div class="dark-stat-box">
                    <div style="font-size:13px;color:#aaa;margin-bottom:6px;">{label}</div>
                    <div style="font-size:26px;font-weight:900;color:{clr};">{val}</div>
                </div>""", unsafe_allow_html=True)

        # ── Map Legend ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#262730;padding:18px;border-radius:12px;
                    border:1px solid rgba(255,255,255,0.08);">
            <div style="font-weight:800;font-size:15px;margin-bottom:12px;color:white;">
                📍 คำอธิบายสัญลักษณ์
            </div>
            <div style="display:flex;gap:24px;flex-wrap:wrap;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:16px;height:16px;border-radius:50%;
                                background:#2ECC71;box-shadow:0 0 8px #2ECC71;"></div>
                    <span style="color:white;">เกรด A (6–10)</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:16px;height:16px;border-radius:50%;
                                background:#F1C40F;box-shadow:0 0 8px #F1C40F;"></div>
                    <span style="color:white;">เกรด B (3–5.9)</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:16px;height:16px;border-radius:50%;
                                background:#E74C3C;box-shadow:0 0 8px #E74C3C;"></div>
                    <span style="color:white;">เกรด C (&lt;3)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้ กรุณาปรับตัวกรอง")

with col_list:
    st.markdown("### 🏆 Top 5 ทำเลแนะนำ")
    if not df_display.empty:
        top5 = df_display.sort_values("Total_Score", ascending=False).head(5)
        for rank, row in enumerate(top5.itertuples(index=False), 1):
            grade = score_grade(row.Total_Score)
            clr   = score_color(row.Total_Score)
            st.markdown(f"""
            <div class="property-card">

                <!-- บรรทัดที่ 1: อันดับ + ชื่อตำบล -->
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <div style="background:#1A365D;color:white;width:26px;height:26px;
                                border-radius:50%;display:flex;align-items:center;
                                justify-content:center;font-size:13px;font-weight:800;
                                flex-shrink:0;">
                        {rank}
                    </div>
                    <div style="font-weight:900;font-size:20px;color:#111;line-height:1.2;">
                        {row.Tambon}
                    </div>
                </div>

                <!-- บรรทัดที่ 2: ที่ตั้ง -->
                <div style="font-size:14px;color:#666;margin-bottom:14px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    📍 {row.Amphoe}, {row.Province}
                </div>

                <!-- กล่องคะแนน: ข้อความ + ตัวเลข + /10 บรรทัดเดียวกัน -->
                <div style="background:linear-gradient(135deg,#1A365D,#2C5282);
                            border-radius:12px;padding:12px 16px;margin-bottom:14px;
                            display:flex;align-items:center;justify-content:space-between;">
                    <div style="color:rgba(255,255,255,0.85);font-size:14px;font-weight:600;">
                        คะแนนความน่าลงทุน
                    </div>
                    <div style="display:flex;align-items:baseline;gap:3px;">
                        <span style="color:white;font-size:28px;font-weight:900;
                                     line-height:1;">{row.Total_Score:.1f}</span>
                        <span style="color:rgba(255,255,255,0.65);font-size:15px;
                                     font-weight:600;">/10</span>
                    </div>
                </div>

                <!-- ราคา + เกรด -->
                <div style="border-top:1px dashed #eee;padding-top:12px;
                            display:flex;justify-content:space-between;align-items:center;">
                    <div style="color:#2ECC71;font-size:20px;font-weight:700;">
                        ฿{row.Est_Land_Price:,.0f}
                        <span style="font-size:13px;color:#888;font-weight:400;">/ตร.ว.</span>
                    </div>
                    <div style="background:{clr}22;color:{clr};
                                border:2px solid {clr};padding:5px 16px;
                                border-radius:20px;font-size:15px;font-weight:800;
                                letter-spacing:0.5px;">
                        เกรด {grade}
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ ไม่พบข้อมูล")

# ─────────────────────────────────────────
# PRICE BREAKDOWN
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("### 🧮 แกะสูตรคำนวณราคา (Price Breakdown)")

if not df_display.empty:
    st.info("เลือกตำบลด้านล่าง เพื่อดูว่าแต่ละปัจจัยส่งผลต่อราคาอย่างไร")

    # ✅ ป้องกันตำบลชื่อซ้ำ — ใส่ชื่ออำเภอกำกับ
    df_display = df_display.copy()
    df_display["_label"] = df_display["Tambon"] + "  [" + df_display["Amphoe"] + "]"
    target_label = st.selectbox("🔍 เลือกตำบลเพื่อถอดสูตร", df_display["_label"].tolist())
    row = df_display[df_display["_label"] == target_label].iloc[0]

    base_price  = row["Avg_Land_Price"]
    dens_fac    = row["Factor_Density"]
    cent_fac    = row["Factor_Centrality"]
    final_price = row["Est_Land_Price"]
    avg_price   = df_display["Est_Land_Price"].mean()
    pct_change  = ((final_price - base_price) / base_price * 100) if base_price else 0
    chg_color   = "#2ECC71" if pct_change >= 0 else "#E74C3C"
    chg_arrow   = "▲" if pct_change >= 0 else "▼"

    # ── Metric Cards ──
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
                gap:20px;margin-bottom:28px;">
        <div style="background:#E3F2FD;border-radius:14px;padding:22px;position:relative;">
            <div style="font-size:15px;font-weight:700;color:#555;">ราคาตั้งต้น (Base)</div>
            <div style="font-size:30px;font-weight:900;color:#1565C0;margin:8px 0;">
                ฿{base_price:,.0f}
            </div>
            <div style="font-size:45px;position:absolute;top:12px;right:16px;opacity:0.15;">🏷️</div>
            <div style="font-size:12px;font-weight:700;color:#1565C0;
                        border-top:1px solid rgba(21,101,192,0.2);padding-top:8px;">
                ราคาประเมินกรมที่ดิน
            </div>
        </div>
        <div style="background:#FFF3E0;border-radius:14px;padding:22px;position:relative;">
            <div style="font-size:15px;font-weight:700;color:#555;">Density Factor</div>
            <div style="font-size:30px;font-weight:900;color:#E65100;margin:8px 0;">
                × {dens_fac:.2f}
            </div>
            <div style="font-size:45px;position:absolute;top:12px;right:16px;opacity:0.15;">👥</div>
            <div style="font-size:12px;font-weight:700;color:#E65100;
                        border-top:1px solid rgba(230,81,0,0.2);padding-top:8px;">
                ปรับตามความหนาแน่นประชากร
            </div>
        </div>
        <div style="background:#F3E5F5;border-radius:14px;padding:22px;position:relative;">
            <div style="font-size:15px;font-weight:700;color:#555;">Location Factor</div>
            <div style="font-size:30px;font-weight:900;color:#7B1FA2;margin:8px 0;">
                × {cent_fac:.1f}
            </div>
            <div style="font-size:45px;position:absolute;top:12px;right:16px;opacity:0.15;">🏙️</div>
            <div style="font-size:12px;font-weight:700;color:#7B1FA2;
                        border-top:1px solid rgba(123,31,162,0.2);padding-top:8px;">
                {"อำเภอเมือง/ศูนย์กลาง (+20%)" if cent_fac > 1.0 else "พื้นที่รอบนอก"}
            </div>
        </div>
        <div style="background:#E8F5E9;border-radius:14px;padding:22px;
                    border:2px solid #4CAF50;position:relative;">
            <div style="font-size:15px;font-weight:700;color:#555;">ราคาประเมิน AI</div>
            <div style="font-size:30px;font-weight:900;color:#2E7D32;margin:8px 0;">
                ฿{final_price:,.0f}
            </div>
            <div style="font-size:45px;position:absolute;top:12px;right:16px;opacity:0.3;">💰</div>
            <div style="font-size:12px;font-weight:700;color:#2E7D32;
                        border-top:1px solid rgba(46,125,50,0.2);padding-top:8px;">
                ราคาสรุปหลังปรับปัจจัยแล้ว
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Factor Analysis ──
    st.markdown("#### 📊 วิเคราะห์ปัจจัย")
    fa, fb = st.columns(2)
    with fa:
        if dens_fac > 1.0:
            st.success(f"📈 **Population Density (+):** หนาแน่นกว่าค่าเฉลี่ยจังหวัด ({dens_fac:.2f}×)")
        else:
            st.warning(f"📉 **Population Density (-):** น้อยกว่าค่าเฉลี่ยจังหวัด ({dens_fac:.2f}×)")
    with fb:
        if cent_fac > 1.0:
            st.info("🏙️ **Location:** อยู่ในเขตอำเภอเมือง/ศูนย์กลาง (+20%)")
        else:
            st.markdown("""<div style="padding:10px;border-radius:5px;
                background:#1e2a35;color:#ccc;border:1px solid #444;">
                🏡 <b>Location:</b> พื้นที่รอบนอก (ไม่มี bonus)
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar Chart ──
    st.markdown("#### 📈 เปรียบเทียบราคา vs ค่าเฉลี่ย")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["ราคาพื้นฐาน (Base)"], y=[base_price], name="Base",
        marker_color="#90A4AE",
        text=[f"฿{base_price:,.0f}"], textposition="auto", width=0.4,
    ))
    fig.add_trace(go.Bar(
        x=["ราคาประเมิน AI"], y=[final_price], name="AI Estimate",
        marker_color="#4CAF50",
        text=[f"฿{final_price:,.0f}"], textposition="auto", width=0.4,
    ))
    # เส้นค่าเฉลี่ย
    fig.add_shape(type="line", x0=-0.5, x1=1.5,
                  y0=avg_price, y1=avg_price,
                  line=dict(color="#FF5722", width=2, dash="dash"))
    fig.add_annotation(x=1.5, y=avg_price,
                       text=f"ค่าเฉลี่ย ฿{avg_price:,.0f}",
                       showarrow=False, yshift=10, xanchor="right",
                       font=dict(color="#FF5722", size=12))
    # % impact
    fig.add_annotation(x=0.5, y=max(base_price, final_price) * 1.08,
                       text=f"{chg_arrow} {pct_change:+.1f}% Impact",
                       showarrow=False,
                       font=dict(size=20, color=chg_color),
                       bgcolor="white", bordercolor=chg_color,
                       borderwidth=1, borderpad=5)
    fig.update_layout(
        height=420, showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sarabun", size=14, color="white"),
        yaxis=dict(showgrid=True, gridcolor="#333"),
        xaxis=dict(showgrid=False),
        bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้ กรุณาปรับตัวกรอง")
