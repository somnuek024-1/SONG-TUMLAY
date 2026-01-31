import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import MarkerCluster
import numpy as np

# --- 1. Config & Design ---
st.set_page_config(page_title="SONGTUMLAY Pro", layout="wide", page_icon="🏙️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
        color: var(--text-color); /* บังคับให้ใช้สีตามธีม */
    }
    
    /* --- Property Card (ปรับให้รองรับ Dark Mode) --- */
    .property-card {
        /* ใช้สีพื้นหลังรองของระบบ (Light=เทาอ่อน / Dark=เทาเข้ม) */
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2); /* ขอบสีจางๆ */
        transition: transform 0.2s;
    }
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.2);
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-color); /* สีเปลี่ยนตามธีม */
        margin-bottom: 5px;
    }
    
    .card-subtitle {
        font-size: 12px;
        color: var(--text-color);
        opacity: 0.8; /* ทำให้จางลงนิดหน่อยแทนการ Fix สีเทา */
        margin-bottom: 10px;
    }
    
    .score-badge {
        background: linear-gradient(90deg, #1A365D 0%, #2A4365 100%);
        color: white; /* Badge บังคับสีขาวเพราะพื้นหลังเข้มเสมอ */
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Growth Tags */
    .growth-tag {
        font-size: 11px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 5px;
    }
    .growth-up { background-color: rgba(60, 179, 113, 0.2); color: #2ECC71; }
    .growth-down { background-color: rgba(220, 20, 60, 0.2); color: #E53E3E; }
    
    /* --- Formula Box (กล่องสมการ) --- */
    .formula-box {
        background-color: var(--secondary-background-color);
        border: 1px dashed var(--primary-color);
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
        text-align: center;
    }
    .formula-item {
        display: inline-block;
        margin: 0 10px;
        text-align: center;
    }
    .formula-val {
        font-size: 24px;
        font-weight: bold;
        color: var(--text-color); /* สีเปลี่ยนตามธีม */
    }
    .formula-label {
        font-size: 12px;
        color: var(--text-color);
        opacity: 0.7;
    }
    .operator {
        font-size: 20px;
        color: var(--primary-color);
        vertical-align: super;
    }
    
    /* Sidebar Fix */
    [data-testid="stSidebar"] { 
        background-color: #1A365D; /* Sidebar สีน้ำเงินเข้มเสมอ */
    }
    [data-testid="stSidebar"] * { 
        color: white !important; /* บังคับตัวอักษรใน Sidebar เป็นสีขาวเสมอ */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        return df
    except FileNotFoundError:
        st.error("❌ ไม่พบไฟล์ final_master_data_multiyear.csv")
        return pd.DataFrame()

df_all_years = load_data()

# --- 3. Logic: Advanced Pricing Model ---
@st.cache_data
def process_latest_view(df):
    if df.empty: return pd.DataFrame(), "N/A"
    
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year].copy()
    
    # Growth Rate
    growth_map = {}
    grouped = df.sort_values('Year').groupby(['Province', 'Amphoe', 'Tambon'])
    for name, group in grouped:
        if len(group) > 1:
            start_pop = group.iloc[0]['Total_Pop']
            end_pop = group.iloc[-1]['Total_Pop']
            growth = ((end_pop - start_pop) / start_pop * 100) if start_pop > 0 else 0
            growth_map[name] = growth
        else:
            growth_map[name] = 0
    df_latest['Growth_Pop'] = df_latest.set_index(['Province', 'Amphoe', 'Tambon']).index.map(growth_map).fillna(0)

    # --- Theory Calculation ---
    
    # 1. Base Price
    
    # 2. Scaling Factor
    prov_pop_mean = df_latest.groupby('Province')['Total_Pop'].transform('mean').replace(0, 1)
    pop_ratio = df_latest['Total_Pop'] / prov_pop_mean
    alpha = 0.3
    df_latest['Factor_Density'] = np.power(pop_ratio, alpha)
    
    # 3. Centrality Factor
    def check_centrality(amphoe_name):
        if 'เมือง' in str(amphoe_name) or 'เขต' in str(amphoe_name):
            return 1.2 
        return 1.0
    df_latest['Factor_Centrality'] = df_latest['Amphoe'].apply(check_centrality)
    
    # 4. Final Calculation
    df_latest['Factor_Total'] = (df_latest['Factor_Density'] * df_latest['Factor_Centrality']).clip(0.5, 3.0)
    df_latest['Est_Land_Price'] = df_latest['Avg_Land_Price'] * df_latest['Factor_Total']
    
    # Scoring
    max_inc = df_latest['Avg_Income'].max() or 1
    max_land = df_latest['Est_Land_Price'].max() or 1
    max_pop = df_latest['Total_Pop'].max() or 1

    df_latest['Score_Econ'] = ((df_latest['Avg_Income']/max_inc * 6) + (df_latest['Est_Land_Price']/max_land * 4))
    df_latest['Score_Pop'] = (df_latest['Total_Pop'] / max_pop * 10)
    df_latest['Bonus_Score'] = df_latest['Growth_Pop'].apply(lambda x: 1.0 if x > 5 else (0.5 if x > 0 else 0))
    
    df_latest['Total_Score'] = (df_latest['Score_Econ']*0.5 + df_latest['Score_Pop']*0.4 + df_latest['Bonus_Score']).round(1)
    
    return df_latest, str(latest_year)

if not df_all_years.empty:
    df_view, latest_year_str = process_latest_view(df_all_years)
else:
    df_view = pd.DataFrame()
    latest_year_str = "N/A"

# --- 4. Sidebar ---
st.sidebar.title("🏙️ SONGTUMLAY")
st.sidebar.caption("Price Breakdown Mode")
st.sidebar.markdown("---")

provinces = ["ทั้งหมด"] + sorted(list(df_all_years['Province'].unique())) if not df_all_years.empty else []
selected_prov = st.sidebar.selectbox("📍 จังหวัด", provinces)

amphoes = ["ทั้งหมด"]
if selected_prov != "ทั้งหมด":
    amphoe_list = sorted(df_all_years[df_all_years['Province'] == selected_prov]['Amphoe'].unique())
    amphoes += amphoe_list
selected_amphoe = st.sidebar.selectbox("อำเภอ/เขต", amphoes)

# Filter
df_display = df_view.copy()
if selected_prov != "ทั้งหมด":
    df_display = df_display[df_display['Province'] == selected_prov]
if selected_amphoe != "ทั้งหมด":
    df_display = df_display[df_display['Amphoe'] == selected_amphoe]

# --- 5. Main Content ---
st.title(f"วิเคราะห์ทำเล: {selected_prov if selected_prov!='ทั้งหมด' else 'ภาพรวม'}")

col_map, col_list = st.columns([2, 1.2])

with col_map:
    st.subheader(f"🗺️ แผนที่ราคา ({latest_year_str})")
    center = [13.7563, 100.5018]
    zoom = 6
    if not df_display.empty:
        center = [df_display['lat'].mean(), df_display['lon'].mean()]
        zoom = 10 if selected_amphoe == "ทั้งหมด" else 11
        
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    mc = MarkerCluster().add_to(m)
    
    if not df_display.empty:
        for _, row in df_display.iterrows():
            if pd.notna(row['lat']):
                color = '#2ECC71' if row['Total_Score'] >= 6 else ('#F1C40F' if row['Total_Score'] >= 3 else '#E74C3C')
                price_text = f"{row['Est_Land_Price']:,.0f}"
                
                popup_html = f"""
                <div style="font-family:Sarabun; width:200px;">
                    <b>{row['Tambon']}</b><br>
                    Score: {row['Total_Score']}<hr>
                    <b>฿ {price_text}</b><br>
                    (Base: {row['Avg_Land_Price']:,.0f} x {row['Factor_Total']:.2f})
                </div>
                """
                folium.CircleMarker(
                    [row['lat'], row['lon']], radius=6, color=color, fill=True, fill_color=color, fill_opacity=0.9,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['Tambon']}"
                ).add_to(mc)
    st_folium(m, height=500, use_container_width=True)

with col_list:
    st.subheader("🏆 รายการ")
    if not df_display.empty:
        top_list = df_display.sort_values('Total_Score', ascending=False).head(5)
        for _, row in top_list.iterrows():
            st.markdown(f"""
            <div class="property-card">
                <div style="display:flex; justify-content:space-between;">
                    <div class="card-title" style="font-size:16px;">{row['Tambon']}</div>
                    <div class="score-badge">{row['Total_Score']}</div>
                </div>
                <div class="card-subtitle">📍 {row['Amphoe']}</div>
                <div style="margin-top:8px; font-weight:bold; color:#2ECC71; font-size:18px;">฿{row['Est_Land_Price']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 6. 🧮 Price Breakdown Section ---
st.markdown("---")
st.subheader("🧮 แกะสูตรคำนวณราคา (Price Breakdown)")
st.info("เลือกตำบลด้านล่าง เพื่อดูว่าทฤษฎีแต่ละตัวส่งผลต่อราคาอย่างไร")

if not df_display.empty:
    tambon_opts = df_display['Tambon'].unique()
    target_tambon = st.selectbox("🔍 เลือกตำบลเพื่อถอดสูตร", tambon_opts)
    
    row = df_display[df_display['Tambon'] == target_tambon].iloc[0]
    
    base_price = row['Avg_Land_Price']
    density_fac = row['Factor_Density']
    central_fac = row['Factor_Centrality']
    final_price = row['Est_Land_Price']
    
    # Formula Box
    st.markdown(f"""
    <div class="formula-box">
        <div class="formula-item">
            <div class="formula-val">{base_price:,.0f}</div>
            <div class="formula-label">ราคาเฉลี่ยจังหวัด<br>(Base Price)</div>
        </div>
        <span class="operator">×</span>
        <div class="formula-item">
            <div class="formula-val" style="color:orange;">{density_fac:.2f}</div>
            <div class="formula-label">Bid-Rent Factor<br>(ความหนาแน่น)</div>
        </div>
        <span class="operator">×</span>
        <div class="formula-item">
            <div class="formula-val" style="color:dodgerblue;">{central_fac:.1f}</div>
            <div class="formula-label">Centrality Factor<br>(ศูนย์กลางเมือง)</div>
        </div>
        <span class="operator">=</span>
        <div class="formula-item">
            <div class="formula-val" style="color:#2ECC71;">{final_price:,.0f}</div>
            <div class="formula-label">ราคาประเมินสุทธิ<br>(Estimated Price)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Explanation & Chart
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📊 วิเคราะห์ปัจจัย (Factors)")
        if density_fac > 1.0:
            st.success(f"📈 **Bid-Rent Effect (+):** ประชากรหนาแน่นกว่าค่าเฉลี่ยจังหวัด ({density_fac:.2f} เท่า)")
        else:
            st.warning(f"📉 **Bid-Rent Effect (-):** ประชากรน้อยกว่าค่าเฉลี่ย ({density_fac:.2f} เท่า)")
            
        if central_fac > 1.0:
            st.info(f"🏙️ **Central Place Effect:** เป็นพื้นที่ศูนย์กลาง ({row['Amphoe']})")
        else:
            st.markdown(f"🏡 **Central Place Effect:** เป็นพื้นที่รอบนอก")

    with c2:
        st.markdown("### 📈 เทียบราคา")
        comp_data = pd.DataFrame({
            'Type': ['เฉลี่ยจังหวัด', 'ราคาประเมินตำบลนี้'],
            'Price': [base_price, final_price]
        })
        fig = px.bar(comp_data, x='Type', y='Price', color='Type', 
                     color_discrete_map={'เฉลี่ยจังหวัด':'#A0AEC0', 'ราคาประเมินตำบลนี้':'#2ECC71'},
                     text_auto='.2s')
        fig.update_layout(showlegend=False, height=250, 
                          paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color="grey")) # ปรับสีฟอนต์กราฟให้กลางๆ
        st.plotly_chart(fig, use_container_width=True)