import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from style_utils import apply_custom_style

# --- 1. Config ---
st.set_page_config(page_title="Compare Locations", layout="wide", page_icon="⚖️")
apply_custom_style()

# --- 2. Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        return df
    except FileNotFoundError: return pd.DataFrame()

df_all_years = load_data()

@st.cache_data
def process_data(df):
    if df.empty: return pd.DataFrame()
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
    
    return df_latest

df_display = process_data(df_all_years)

# --- CSS Styling (Dark Theme Only) ---
st.markdown("""
<style>
    /* พื้นหลังหลักสี Dark #1A2228 */
    [data-testid="stAppViewContainer"] {
        background-color: #1A2228;
        color: white;
    }
    
    /* Header สีเดียวกับพื้นหลัง */
    header[data-testid="stHeader"] {
        background-color: #1A2228;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Header Banner ---
st.markdown("""
<div style="
    background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=2670&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    padding: 60px 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
">
    <div style="font-size: 48px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
        COMPARE LOCATIONS
    </div>
    <div style="font-size: 18px; font-weight: 300; opacity: 0.9;">
        เปรียบเทียบศักยภาพทำเลแบบ Head-to-Head
    </div>
</div>
""", unsafe_allow_html=True)

# ❌ ลบส่วน Slider (ตัวกรองงบประมาณ) ออกแล้วครับ

# --- 4. Location Selectors ---
if not df_display.empty:
    col_sel1, col_vs, col_sel2 = st.columns([1, 0.2, 1])
    
    # ใช้ df_display เต็มๆ โดยไม่ต้องกรองราคา
    
    with col_sel1:
        st.markdown("### 🏙️ ทำเลที่ 1 (Location A)")
        prov1 = st.selectbox("เลือกจังหวัด A", sorted(df_display['Province'].unique()), key="p1")
        amp_list1 = sorted(df_display[df_display['Province'] == prov1]['Amphoe'].unique())
        amp1 = st.selectbox("เลือกอำเภอ A", amp_list1, key="a1")
        tam_list1 = sorted(df_display[(df_display['Province'] == prov1) & (df_display['Amphoe'] == amp1)]['Tambon'].unique())
        tam1 = st.selectbox("เลือกตำบล A", tam_list1, key="t1")
        
    with col_vs:
        st.markdown("<br><br><div style='text-align:center; font-size:30px; font-weight:bold; color:#BDC3C7;'>VS</div>", unsafe_allow_html=True)
        
    with col_sel2:
        st.markdown("### 🏙️ ทำเลที่ 2 (Location B)")
        prov2 = st.selectbox("เลือกจังหวัด B", sorted(df_display['Province'].unique()), index=min(1, len(df_display['Province'].unique())-1), key="p2")
        amp_list2 = sorted(df_display[df_display['Province'] == prov2]['Amphoe'].unique())
        amp2 = st.selectbox("เลือกอำเภอ B", amp_list2, key="a2")
        tam_list2 = sorted(df_display[(df_display['Province'] == prov2) & (df_display['Amphoe'] == amp2)]['Tambon'].unique())
        tam2 = st.selectbox("เลือกตำบล B", tam_list2, key="t2")

    # ดึงข้อมูลมาแสดงผล
    try:
        row1 = df_display[(df_display['Province'] == prov1) & (df_display['Amphoe'] == amp1) & (df_display['Tambon'] == tam1)].iloc[0]
        row2 = df_display[(df_display['Province'] == prov2) & (df_display['Amphoe'] == amp2) & (df_display['Tambon'] == tam2)].iloc[0]

        st.markdown("---")

        # --- 5. Head-to-Head Comparison ---
        st.markdown("""
            <div style="font-size:24px; font-weight:bold; margin-bottom:20px; display:flex; align-items:center;">
                ⚡ วัดกันที่ตัวเลขจริง (Head-to-Head)
            </div>
        """, unsafe_allow_html=True)

        def create_compare_card(title, val1, val2, unit):
            winner = "A" if val1 > val2 else ("B" if val2 > val1 else "Draw")
            color_a = "#2ECC71" if winner == "A" else "#BDC3C7"
            color_b = "#2ECC71" if winner == "B" else "#BDC3C7"
            
            total = val1 + val2
            if total == 0:
                flex_a, flex_b = 1, 1
            else:
                flex_a = (val1 / total) * 100
                flex_b = (val2 / total) * 100

            return f"""
            <div style="background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 20px;">
                <div style="font-size:16px; font-weight:bold; color:#555; margin-bottom:15px; text-align:center;">{title}</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="text-align:center; width:40%;">
                        <div style="font-size:22px; font-weight:900; color:#1A365D;">{val1:,.0f}</div>
                        <div style="font-size:12px; color:#888;">{unit}</div>
                        <div style="font-size:12px; font-weight:bold; color:{color_a}; margin-top:5px;">{ "🏆 WIN" if winner=="A" else "&nbsp;" }</div>
                    </div>
                    <div style="width:20%; text-align:center;">
                        <div style="width:35px; height:35px; background:#F0F2F6; color:#888; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:12px; margin:0 auto;">VS</div>
                    </div>
                    <div style="text-align:center; width:40%;">
                        <div style="font-size:22px; font-weight:900; color:#1A365D;">{val2:,.0f}</div>
                        <div style="font-size:12px; color:#888;">{unit}</div>
                        <div style="font-size:12px; font-weight:bold; color:{color_b}; margin-top:5px;">{ "🏆 WIN" if winner=="B" else "&nbsp;" }</div>
                    </div>
                </div>
                <div style="margin-top:15px; display:flex; height:6px; border-radius:3px; overflow:hidden;">
                    <div style="width:{flex_a}%; background:{color_a};"></div>
                    <div style="width:2px; background:white;"></div>
                    <div style="width:{flex_b}%; background:{color_b};"></div>
                </div>
            </div>
            """

        c_price, c_income, c_pop = st.columns(3)
        
        with c_price:
            st.markdown(create_compare_card("💰 ราคาที่ดิน (Land Price)", row1['Est_Land_Price'], row2['Est_Land_Price'], "บาท"), unsafe_allow_html=True)
        with c_income:
            st.markdown(create_compare_card("💵 รายได้เฉลี่ย (Income)", row1['Avg_Income'], row2['Avg_Income'], "บาท/เดือน"), unsafe_allow_html=True)
        with c_pop:
            st.markdown(create_compare_card("👥 ประชากร (Population)", row1['Total_Pop'], row2['Total_Pop'], "คน"), unsafe_allow_html=True)

        # --- 6. Total Score Comparison ---
        st.markdown("### 🏆 สรุปคะแนนรวม (Total Score)")
        
        col_score_chart, col_score_card = st.columns([2, 1])
        
        with col_score_chart:
            labels = ['คะแนนรวม', 'Factor ทำเล', 'Factor ความหนาแน่น']
            val1 = [row1['Total_Score'], row1['Factor_Centrality']*3, row1['Factor_Density']*3]
            val2 = [row2['Total_Score'], row2['Factor_Centrality']*3, row2['Factor_Density']*3]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=labels, x=val1, name=row1['Tambon'], orientation='h',
                marker_color='#3498DB', text=[f"{v:.1f}" for v in val1], textposition='auto'
            ))
            fig.add_trace(go.Bar(
                y=labels, x=val2, name=row2['Tambon'], orientation='h',
                marker_color='#E67E22', text=[f"{v:.1f}" for v in val2], textposition='auto'
            ))
            
            fig.update_layout(
                barmode='group', height=350,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Sarabun", color="white"), # ตัวอักษรสีขาว
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", y=1.1, font=dict(color="white"))
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_score_card:
            score_diff = abs(row1['Total_Score'] - row2['Total_Score'])
            winner_name = row1['Tambon'] if row1['Total_Score'] > row2['Total_Score'] else row2['Tambon']
            
            score_html = f"""
            <div style="background:#F4F6F7; padding:25px; border-radius:12px; text-align:center; height:100%; border:2px solid #BDC3C7;">
                <div style="font-size:18px; color:#555;">ผู้ชนะคือ</div>
                <div style="font-size:32px; font-weight:900; color:#2ECC71; margin:10px 0;">{winner_name}</div>
                <div style="font-size:14px; color:#7F8C8D;">คะแนนนำอยู่ <b>{score_diff:.1f}</b> แต้ม</div>
                <div style="margin-top:20px; font-size:50px;">👑</div>
            </div>
            """
            st.markdown(score_html, unsafe_allow_html=True)
    except IndexError:
        st.warning("กรุณาเลือกตำบลให้ครบทั้ง 2 ฝั่งครับ")

else:
    st.error("ไม่พบข้อมูล กรุณาตรวจสอบไฟล์ CSV")
