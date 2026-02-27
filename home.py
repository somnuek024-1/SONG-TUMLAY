import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.graph_objects as go

from style_utils import apply_custom_style
from data_utils import load_and_process, filter_df

# ── 1. Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="SONGTUMLAY Pro", layout="wide", page_icon="🏙️")
apply_custom_style()

# ── 2. Data ────────────────────────────────────────────────────────────────
df_all = load_and_process()

# ── 3. Sidebar ─────────────────────────────────────────────────────────────
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

if not df_all.empty:
    price_min_data = int(df_all["Est_Land_Price"].min())
    price_max_data = int(df_all["Est_Land_Price"].max())

    st.sidebar.write("💰 **งบประมาณ (ทุน)**")
    col_min, col_max = st.sidebar.columns(2)
    with col_min:
        min_input = st.number_input(
            "ต่ำสุด", min_value=0, max_value=price_max_data,
            value=price_min_data, step=50_000
        )
    with col_max:
        max_input = st.number_input(
            "สูงสุด", min_value=0, max_value=price_max_data,
            value=price_max_data, step=50_000
        )
else:
    min_input, max_input = 0, 0
    price_min_data, price_max_data = 0, 0

provinces = ["ทั้งหมด"] + sorted(df_all["Province"].unique().tolist()) if not df_all.empty else ["ทั้งหมด"]
selected_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if selected_prov != "ทั้งหมด" and not df_all.empty:
    amphoes += sorted(df_all[df_all["Province"] == selected_prov]["Amphoe"].unique().tolist())
selected_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)
st.sidebar.caption("© 2024 SongTumLay Pro")

# ── 4. Filter data ─────────────────────────────────────────────────────────
df_display = filter_df(
    df_all,
    province=selected_prov,
    amphoe=selected_amphoe,
    price_min=min_input,
    price_max=max_input,
)

# ── 5. Hero Banner ─────────────────────────────────────────────────────────
area_label = selected_prov if selected_prov != "ทั้งหมด" else "ภาพรวมประเทศไทย"
budget_label = ""
if not df_all.empty and (min_input > price_min_data or max_input < price_max_data):
    budget_label = f" | งบ ฿{min_input:,.0f} – ฿{max_input:,.0f}"

st.markdown(
    f"""
<div class="hero-banner" style="
    background-image: linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.70)),
    url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2613&auto=format&fit=crop');
">
    <div class="hero-title">แผนที่วิเคราะห์ทำเล</div>
    <div class="hero-sub">{area_label}{budget_label}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ── 6. Main Layout: Map | Top-5 ────────────────────────────────────────────
col_map, col_list = st.columns([2, 1.2])

with col_map:
    # --- Folium Map ---
    if df_display.empty:
        center, zoom = [13.7563, 100.5018], 6
    else:
        center = [df_display["lat"].mean(), df_display["lon"].mean()]
        zoom = 6 if selected_prov == "ทั้งหมด" else (10 if selected_amphoe == "ทั้งหมด" else 11)

    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

    if not df_display.empty:
        mc = MarkerCluster().add_to(m)
        for _, row in df_display.iterrows():
            if not (row["lat"] != row["lat"]):  # skip NaN
                score = row["Total_Score"]
                color = "#2ECC71" if score >= 6 else ("#F1C40F" if score >= 3 else "#E74C3C")
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.88,
                    popup=folium.Popup(
                        f"<b>{row['Tambon']}</b><br>{row['Amphoe']}, {row['Province']}"
                        f"<br>💰 ฿{row['Est_Land_Price']:,.0f}<br>⭐ {row['Total_Score']}",
                        max_width=200,
                    ),
                    tooltip=f"{row['Tambon']} | ฿{row['Est_Land_Price']:,.0f}",
                ).add_to(mc)

    st_folium(m, height=500, use_container_width=True)

    # --- Summary Stats ---
    if not df_display.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 สรุปสถิติภาพรวมพื้นที่")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-label">ราคาเฉลี่ย (ตร.ว.)</div>
                    <div class="stat-value" style="color:#2ECC71;">฿{df_display['Est_Land_Price'].mean():,.0f}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-label">คะแนนเฉลี่ย</div>
                    <div class="stat-value" style="color:#3498DB;">{df_display['Total_Score'].mean():.2f} / 10</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""<div class="stat-card">
                    <div class="stat-label">จำนวนพื้นที่ในโซนนี้</div>
                    <div class="stat-value" style="color:#F1C40F;">{len(df_display):,} แห่ง</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # --- Map Legend ---
        st.markdown(
            """
<div class="map-legend">
    <div style="font-weight:800; font-size:15px; margin-bottom:12px; color:white;">📍 คำอธิบายสัญลักษณ์</div>
    <div style="display:flex; flex-wrap:wrap; gap:18px;">
        <div><span class="legend-dot" style="background:#2ECC71; box-shadow:0 0 6px #2ECC71;"></span>
             <span style="color:white;">เกรด A — คะแนน 6–10</span></div>
        <div><span class="legend-dot" style="background:#F1C40F; box-shadow:0 0 6px #F1C40F;"></span>
             <span style="color:white;">เกรด B — คะแนน 3–5.9</span></div>
        <div><span class="legend-dot" style="background:#E74C3C; box-shadow:0 0 6px #E74C3C;"></span>
             <span style="color:white;">เกรด C — คะแนน &lt; 3</span></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

with col_list:
    st.subheader("🏆 Top 5 ทำเลแนะนำ")
    if not df_display.empty:
        top5 = df_display.nlargest(5, "Total_Score")
        for _, row in top5.iterrows():
            st.markdown(
                f"""
<div class="property-card">
    <div class="card-title-row">
        <div class="card-title-text">{row['Tambon']}</div>
        <span class="score-badge">{row['Total_Score']:.2f}</span>
    </div>
    <div class="card-location">📍 {row['Amphoe']}, {row['Province']}</div>
    <div class="card-divider"></div>
    <div class="card-price">฿{row['Est_Land_Price']:,.0f}
        <span style="font-size:14px; color:#888; font-weight:normal;">/ตร.ว.</span>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
    else:
        st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้")

# ── 7. Price Breakdown ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🧮 แกะสูตรคำนวณราคา (Price Breakdown)")

if not df_display.empty:
    st.info("เลือกตำบลด้านล่าง เพื่อดูว่าแต่ละปัจจัยส่งผลต่อราคาอย่างไร")

    # Search box + dropdown รวมกัน
    search_text = st.text_input("🔍 พิมพ์ชื่อตำบล (ค้นหาแบบ free-text)", placeholder="เช่น พระบรมมหาราชวัง")
    tambon_opts = df_display["Tambon"].unique().tolist()
    if search_text:
        tambon_opts = [t for t in tambon_opts if search_text.lower() in t.lower()]
    
    if not tambon_opts:
        st.warning("ไม่พบตำบลที่ค้นหา")
    else:
        target_tambon = st.selectbox("เลือกตำบลเพื่อถอดสูตร", tambon_opts)

        row = df_display[df_display["Tambon"] == target_tambon].iloc[0]
        base_price   = row["Avg_Land_Price"]
        density_fac  = row["Factor_Density"]
        central_fac  = row["Factor_Centrality"]
        final_price  = row["Est_Land_Price"]
        avg_price    = df_display["Est_Land_Price"].mean()
        pct_change   = ((final_price - base_price) / base_price * 100) if base_price else 0

        # Metric Cards
        st.markdown(
            f"""
<style>
.metric-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:18px; margin-bottom:26px; }}
.m-card {{ border-radius:12px; padding:18px; position:relative; overflow:hidden; border:1px solid rgba(0,0,0,0.07); }}
.m-card-title {{ font-size:14px; font-weight:700; color:#555; margin-bottom:8px; }}
.m-card-value {{ font-size:26px; font-weight:900; }}
.m-card-icon {{ position:absolute; top:14px; right:14px; font-size:36px; opacity:0.18; }}
.m-card-foot {{ margin-top:12px; font-size:12px; font-weight:700; padding-top:10px; border-top:1px solid rgba(0,0,0,0.08); }}
</style>
<div class="metric-grid">
  <div class="m-card" style="background:#E3F2FD;">
    <div class="m-card-title">ราคาตั้งต้น (Base)</div>
    <div class="m-card-value" style="color:#1565C0;">฿{base_price:,.0f}</div>
    <div class="m-card-icon">🏷️</div>
    <div class="m-card-foot" style="color:#1565C0;">ราคาประเมินกรมที่ดิน</div>
  </div>
  <div class="m-card" style="background:#FFF3E0;">
    <div class="m-card-title">Density Factor</div>
    <div class="m-card-value" style="color:#E65100;">× {density_fac:.2f}</div>
    <div class="m-card-icon">👥</div>
    <div class="m-card-foot" style="color:#E65100;">ปรับตามความหนาแน่นประชากร</div>
  </div>
  <div class="m-card" style="background:#F3E5F5;">
    <div class="m-card-title">Location Factor</div>
    <div class="m-card-value" style="color:#7B1FA2;">× {central_fac:.1f}</div>
    <div class="m-card-icon">🏙️</div>
    <div class="m-card-foot" style="color:#7B1FA2;">ปรับตามโซนอำเภอ (3 ระดับ)</div>
  </div>
  <div class="m-card" style="background:#E8F5E9; border:2px solid #4CAF50;">
    <div class="m-card-title">ราคาประเมิน AI</div>
    <div class="m-card-value" style="color:#2E7D32;">฿{final_price:,.0f}</div>
    <div class="m-card-icon" style="opacity:1;">💰</div>
    <div class="m-card-foot" style="color:#2E7D32;">ราคาสรุปหลังคำนวณทุกปัจจัย</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Factor Analysis
        fa1, fa2 = st.columns(2)
        with fa1:
            if density_fac > 1.0:
                st.success(f"📈 **Density (+):** ประชากรหนาแน่นกว่าค่าเฉลี่ย ({density_fac:.2f}×)")
            else:
                st.warning(f"📉 **Density (-):** ประชากรน้อยกว่าค่าเฉลี่ย ({density_fac:.2f}×)")
        with fa2:
            tier = {1.2: "🏙️ ศูนย์กลางเมือง (×1.2)", 1.1: "🏘️ อำเภอรอง (×1.1)", 1.0: "🏡 พื้นที่รอบนอก (×1.0)"}
            st.info(f"**Location:** {tier.get(central_fac, str(central_fac))}")

        # Graph
        st.subheader("📈 เปรียบเทียบราคา vs ค่าเฉลี่ยโซน")
        change_color = "#2ECC71" if pct_change >= 0 else "#E74C3C"
        arrow = "▲" if pct_change >= 0 else "▼"

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["ราคาพื้นฐาน"], y=[base_price], name="ราคาพื้นฐาน",
            marker_color="#90A4AE", text=[f"฿{base_price:,.0f}"], textposition="auto", width=0.4,
        ))
        fig.add_trace(go.Bar(
            x=["ราคาประเมิน AI"], y=[final_price], name="ราคาประเมิน AI",
            marker_color="#4CAF50", text=[f"฿{final_price:,.0f}"], textposition="auto", width=0.4,
        ))
        fig.add_shape(type="line", x0=-0.5, x1=1.5, y0=avg_price, y1=avg_price,
                      line=dict(color="#FF5722", width=2, dash="dash"))
        fig.add_annotation(x=1.5, y=avg_price, text=f"ค่าเฉลี่ย: ฿{avg_price:,.0f}",
                           showarrow=False, yshift=10, xanchor="right",
                           font=dict(color="#FF5722", size=12))
        fig.add_annotation(
            x=0.5, y=max(base_price, final_price) * 1.06,
            text=f"{arrow} {pct_change:+.1f}% Impact",
            showarrow=False,
            font=dict(size=18, color=change_color),
            bgcolor="white", bordercolor=change_color, borderwidth=1, borderpad=5,
        )
        fig.update_layout(
            height=460, barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Sarabun", size=14, color="white"),
            yaxis=dict(showgrid=True, gridcolor="#2d3540"),
            xaxis=dict(showgrid=False),
            showlegend=False, margin=dict(t=50, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้ หรือในพื้นที่ที่เลือก กรุณาปรับตัวกรอง")
