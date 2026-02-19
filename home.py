import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from style_utils import apply_custom_style

# --- 1. Config ---
st.set_page_config(page_title="SONGTUMLAY Pro", layout="wide", page_icon="🏙️")
apply_custom_style()

# --- 2. Helper Functions & Data ---
def get_coordinates(province_name):
    coords = {
        "เชียงใหม่": [18.7883, 98.9853], "ขอนแก่น": [16.4322, 102.8236], "ภูเก็ต": [7.8804, 98.3923], 
        "กรุงเทพมหานคร": [13.7563, 100.5018], "นครราชสีมา": [14.9799, 102.0978], "ชลบุรี": [13.3611, 100.9847],
        "สงขลา": [7.1988, 100.5951], "อุดรธานี": [17.4138, 102.7872], "ประจวบคีรีขันธ์": [11.8124, 99.7973], 
        "ระยอง": [12.6815, 101.2816], "พระนครศรีอยุธยา": [14.3532, 100.5684], "สุราษฎร์ธานี": [9.1382, 99.3217],
        "เชียงราย": [19.9105, 99.8406], "อุบลราชธานี": [15.2448, 104.8473], "พิษณุโลก": [16.8211, 100.2659], 
        "กาญจนบุรี": [14.0225, 99.5327]
    }
    return coords.get(province_name, [13.7563, 100.5018])

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        if 'lat' not in df.columns or 'lon' not in df.columns:
            coords = df['Province'].apply(get_coordinates)
            df['lat'] = coords.apply(lambda x: x[0]) + np.random.normal(0, 0.02, size=len(df))
            df['lon'] = coords.apply(lambda x: x[1]) + np.random.normal(0, 0.02, size=len(df))
        return df
    except FileNotFoundError: return pd.DataFrame()

df_all_years = load_data()

@st.cache_data
def process_latest_view(df):
    if df.empty: return pd.DataFrame(), "N/A"
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year].copy()
    
    prov_pop_mean = df_latest.groupby('Province')['Total_Pop'].transform('mean').replace(0, 1)
    pop_ratio = df_latest['Total_Pop'] / prov_pop_mean
    df_latest['Factor_Density'] = np.power(pop_ratio, 0.3)
    df_latest['Factor_Centrality'] = df_latest['Amphoe'].apply(lambda x: 1.2 if ('เมือง' in str(x) or 'เขต' in str(x)) else 1.0)
    df_latest['Factor_Total'] = (df_latest['Factor_Density'] * df_latest['Factor_Centrality']).clip(0.5, 3.0)
    df_latest['Est_Land_Price'] = df_latest['Avg_Land_Price'] * df_latest['Factor_Total']
    
    max_inc = df_latest['Avg_Income'].max() or 1
    max_land = df_latest['Est_Land_Price'].max() or 1
    max_pop = df_latest['Total_Pop'].max() or 1
    df_latest['Total_Score'] = ((df_latest['Avg_Income']/max_inc * 3) + (df_latest['Est_Land_Price']/max_land * 2) + (df_latest['Total_Pop']/max_pop * 5)).round(1)
    
    return df_latest, str(latest_year)

if not df_all_years.empty:
    df_view, latest_year_str = process_latest_view(df_all_years)
else:
    df_view = pd.DataFrame()
    latest_year_str = "N/A"

# --- CSS Styling สำหรับหน้า Home ---
st.markdown("""
<style>
    /* พื้นหลังหลักสี Dark Theme */
    [data-testid="stAppViewContainer"] {
        background-color: #1A2228;
        color: white;
    }
    
    /* Header สีเดียวกับพื้นหลัง */
    header[data-testid="stHeader"] {
        background-color: #1A2228;
    }
    
    /* บังคับตัวอักษรเป็นสีขาว */
    .stMarkdown, p, h1, h2, h3 {
        color: #ffffff !important;
    }

    /* Style ของกล่องตัวเลือกจังหวัด/อำเภอ */
    div[data-baseweb="select"] > div {
        background-color: #262730 !important;
        color: white !important;
        border-color: rgba(255,255,255,0.2) !important;
    }

    /* บังคับช่องกรอกตัวเลข (Number Input) ให้เข้ากับ Dark Theme */
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #262730 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 4px;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }

    /* Style ให้กับ property-card ใหม่ */
    .property-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .card-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .card-title-text {
        font-weight: 800;
        font-size: 20px;
        color: #000000 !important;
    }

    /* ปรับแต่งกล่องคะแนนให้ใหญ่ขึ้น */
    .score-badge {
        background-color: #1A365D;
        color: white !important;
        padding: 8px 18px; 
        border-radius: 8px;
        font-size: 22px; 
        font-weight: 900;
    }

    .card-location {
        font-size: 14px;
        color: #666666 !important;
        margin-bottom: 15px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .card-divider {
        border-top: 1px dashed #ddd;
        margin: 15px 0;
    }

    .card-price {
        font-weight: bold;
        color: #2ECC71 !important;
        font-size: 24px;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. Sidebar Inputs ---
st.sidebar.markdown("### 🔍 ค้นหาพื้นที่")

# เปลี่ยนตัวกรองงบประมาณเป็น Number Input 2 ช่อง
if not df_view.empty:
    min_p = int(df_view['Est_Land_Price'].min())
    max_p = int(df_view['Est_Land_Price'].max())
    
    st.sidebar.write("💰 **งบประมาณ (ทุน)**")
    
    col_min, col_max = st.sidebar.columns(2)
    with col_min:
        min_input = st.number_input("ต่ำสุด (Min)", min_value=0, max_value=max_p, value=min_p, step=50000)
    with col_max:
        max_input = st.number_input("สูงสุด (Max)", min_value=0, max_value=max_p, value=max_p, step=50000)
    
    price_range = (min_input, max_input)
else:
    price_range = (0, 0)

provinces = ["ทั้งหมด"] + sorted(list(df_all_years['Province'].unique())) if not df_all_years.empty else []
selected_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)
amphoes = ["ทั้งหมด"]
if selected_prov != "ทั้งหมด":
    amphoes += sorted(df_all_years[df_all_years['Province'] == selected_prov]['Amphoe'].unique())
selected_amphoe = st.sidebar.selectbox("🏙️ อำเภอ/เขต", amphoes)
st.sidebar.caption("© 2024 SongTumLay Pro")

# --- 4. Main Content ---

df_display = df_view.copy()

if not df_display.empty:
    df_display = df_display[
        (df_display['Est_Land_Price'] >= price_range[0]) & 
        (df_display['Est_Land_Price'] <= price_range[1])
    ]

if selected_prov != "ทั้งหมด": df_display = df_display[df_display['Province'] == selected_prov]
if selected_amphoe != "ทั้งหมด": df_display = df_display[df_display['Amphoe'] == selected_amphoe]

subtitle_text = f"พื้นที่: {selected_prov}" if selected_prov != 'ทั้งหมด' else "ภาพรวมประเทศไทย"
if price_range[0] > min_p or price_range[1] < max_p:
    subtitle_text += f" (งบ: ฿{price_range[0]:,.0f} - ฿{price_range[1]:,.0f})"

st.markdown(f"""
<div style="
    background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2613&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    padding: 50px 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
">
    <div style="font-size: 48px; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">
        แผนที่วิเคราะห์ทำเล
    </div>
    <div style="font-size: 18px; font-weight: 300; opacity: 0.9;">
        {subtitle_text}
    </div>
</div>
""", unsafe_allow_html=True)

col_map, col_list = st.columns([2, 1.2])

with col_map:
    center = [13.7563, 100.5018]
    zoom = 6
    if not df_display.empty:
        center = [df_display['lat'].mean(), df_display['lon'].mean()]
        zoom = 10 if selected_amphoe == "ทั้งหมด" else 11
        
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    
    if not df_display.empty:
        mc = MarkerCluster().add_to(m)
        for _, row in df_display.iterrows():
            if pd.notna(row['lat']):
                color = '#2ECC71' if row['Total_Score'] >= 6 else ('#F1C40F' if row['Total_Score'] >= 3 else '#E74C3C')
                folium.CircleMarker(
                    [row['lat'], row['lon']], radius=6, color=color, fill=True, fill_color=color, fill_opacity=0.9,
                    popup=f"<b>{row['Tambon']}</b><br>฿{row['Est_Land_Price']:,.0f}", tooltip=row['Tambon']
                ).add_to(mc)
    st_folium(m, height=500, use_container_width=True)

with col_list:
    st.subheader("🏆 รายการ (Top 5)")
    if not df_display.empty:
        top_list = df_display.sort_values('Total_Score', ascending=False).head(5)
        for _, row in top_list.iterrows():
            # ✅ แก้ไขการเว้นวรรคและจัดรูปแบบ HTML เพื่อป้องกันปัญหาแสดงเป็นโค้ดดิบ
            card_html = f"""
            <div class="property-card">
                <div class="card-title-row">
                    <div class="card-title-text">{row['Tambon']}</div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:20px; font-weight:bold; color:#000000;">คะแนนความน่าลงทุน</span>
                        <span class="score-badge">{row['Total_Score']}</span>
                    </div>
                </div>
                <div class="card-location">📍 {row['Amphoe']}, {row['Province']}</div>
                <div class="card-divider"></div>
                <div class="card-price">฿{row['Est_Land_Price']:,.0f}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้")

# --- 5. Price Breakdown Section (New Layout) ---
st.markdown("---")
st.subheader("🧮 แกะสูตรคำนวณราคา (Price Breakdown)")

if not df_display.empty:
    st.info("เลือกตำบลด้านล่าง เพื่อดูว่าทฤษฎีแต่ละตัวส่งผลต่อราคาอย่างไร")
    tambon_opts = df_display['Tambon'].unique()
    target_tambon = st.selectbox("🔍 เลือกตำบลเพื่อถอดสูตร", tambon_opts)
    
    if target_tambon:
        row = df_display[df_display['Tambon'] == target_tambon].iloc[0]
        
        base_price = row['Avg_Land_Price']
        density_fac = row['Factor_Density']
        central_fac = row['Factor_Centrality']
        final_price = row['Est_Land_Price']
        
        # 1. Metric Cards (Grid Layout)
        html_code = f"""
       <style>
            .metric-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .metric-card {{ background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); position: relative; overflow: hidden; border: 1px solid rgba(0,0,0,0.05); }}
            .card-title {{ font-size: 16px; font-weight: bold; color: #555; margin-bottom: 10px; }}
            .card-value {{ font-size: 28px; font-weight: 900; color: #333; }}
            .card-icon {{ position: absolute; top: 15px; right: 15px; font-size: 40px; opacity: 0.2; }}
            .card-footer {{ margin-top: 15px; font-size: 13px; font-weight: bold; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1); }}
        </style>
        <div class="metric-container">
            <div class="metric-card" style="background: #E3F2FD;">
                <div class="card-title">ราคาตั้งต้น (Base)</div>
                <div class="card-value" style="color:#1565C0;">฿{base_price:,.0f}</div>
                <div class="card-icon">🏷️</div>
                <div class="card-footer" style="color:#1565C0;">ราคาประเมินกรมที่ดิน</div>
            </div>
            <div class="metric-card" style="background: #FFF3E0;">
                <div class="card-title">Density Factor</div>
                <div class="card-value" style="color:#E65100;">x {density_fac:.2f}</div>
                <div class="card-icon">👥</div>
                <div class="card-footer" style="color:#E65100;">ปรับตามความหนาแน่น</div>
            </div>
            <div class="metric-card" style="background: #F3E5F5;">
                <div class="card-title">Location Factor</div>
                <div class="card-value" style="color:#7B1FA2;">x {central_fac:.1f}</div>
                <div class="card-icon">🏙️</div>
                <div class="card-footer" style="color:#7B1FA2;">ปรับตามโซนเมือง</div>
            </div>
            <div class="metric-card" style="background: #E8F5E9; border: 2px solid #4CAF50;">
                <div class="card-title">ราคาประเมิน AI</div>
                <div class="card-value" style="color:#2E7D32;">฿{final_price:,.0f}</div>
                <div class="card-icon" style="opacity:1;">💰</div>
                <div class="card-footer" style="color:#2E7D32;">สรุปราคาขายจริง</div>
            </div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)
        
        # 2. Factor Analysis
        st.subheader("📊 วิเคราะห์ปัจจัย (Factors Analysis)")
        f1, f2 = st.columns(2)
        with f1:
            if density_fac > 1.0:
                st.success(f"📈 **Population Density (+):** ประชากรหนาแน่นกว่าค่าเฉลี่ย ({density_fac:.2f} เท่า)")
            else:
                st.warning(f"📉 **Population Density (-):** ประชากรน้อยกว่าค่าเฉลี่ย ({density_fac:.2f} เท่า)")
        with f2:
            if central_fac > 1.0:
                st.info(f"🏙️ **Central Place Effect:** อยู่ในเขตอำเภอเมือง/ศูนย์กลาง")
            else:
                st.markdown(f"""<div style="padding:10px; border-radius:5px; background-color:#F0F2F6; color:#31333F;">
                🏡 <b>Central Place Effect:</b> เป็นพื้นที่รอบนอก</div>""", unsafe_allow_html=True)
        
        st.write("")

        # 3. Graph
        st.subheader("📈 เปรียบเทียบราคาและวิเคราะห์เชิงลึก (Price Comparison)")
        avg_area_price = df_display['Est_Land_Price'].mean()
        pct_change = ((final_price - base_price) / base_price) * 100
        change_color = "#2ECC71" if pct_change >= 0 else "#E74C3C"
        change_arrow = "▲" if pct_change >= 0 else "▼"

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=['ราคาพื้นฐาน'], y=[base_price], name='ราคาพื้นฐาน',
            marker=dict(color=base_price, colorscale=[[0, '#CFD8DC'], [1, '#90A4AE']]),
            text=[f"฿{base_price:,.0f}"], textposition='auto', width=0.4
        ))

        fig.add_trace(go.Bar(
            x=['ราคาประเมิน AI'], y=[final_price], name='ราคาประเมิน AI',
            marker=dict(color=final_price, colorscale=[[0, '#A5D6A7'], [1, '#4CAF50']]),
            text=[f"฿{final_price:,.0f}"], textposition='auto', width=0.4
        ))
        
        fig.add_shape(type="line", x0=-0.5, x1=1.5, y0=avg_area_price, y1=avg_area_price,
            line=dict(color="#FF5722", width=2, dash="dash"),
        )
        fig.add_annotation(
            x=1.5, y=avg_area_price, text=f"ค่าเฉลี่ย: ฿{avg_area_price:,.0f}",
            showarrow=False, yshift=10, xanchor="right", font=dict(color="#FF5722", size=12)
        )

        fig.add_annotation(
            x=0.5, y=max(base_price, final_price) * 1.05,
            text=f"{change_arrow} {pct_change:+.1f}% Impact",
            showarrow=False,
            font=dict(size=20, color=change_color, weight="bold"),
            bgcolor="white", bordercolor=change_color, borderwidth=1, borderpad=5
        )

        fig.update_layout(
            title="เปรียบเทียบราคา vs ปัจจัยผลกระทบ", height=500,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Sarabun", size=14, color="white"), # เปลี่ยนสีอักษรกราฟเป็นสีขาวให้เข้ากับ Dark Mode
            yaxis=dict(showgrid=True, gridcolor='#333'), xaxis=dict(showgrid=False),
            bargap=0.2, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ ไม่พบข้อมูลในช่วงราคานี้ หรือ ในพื้นที่ที่เลือก กรุณาปรับตัวกรอง")
