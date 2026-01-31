import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. Config ---
st.set_page_config(page_title="เปรียบเทียบทำเล - SongTumLay", layout="wide", page_icon="⚖️")

# --- 2. Theme & Custom CSS (Universal Design) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
        color: #333333;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .main-title { font-size: 36px; font-weight: 700; color: #2C3E50; margin-bottom: 10px; }
    .sub-title { font-size: 18px; font-weight: 300; color: #7F8C8D; }
    
    /* VS Badge Style */
    .vs-badge {
        background-color: #ECF0F1;
        color: #000000;           /* ✅ แก้เป็นสีดำสนิท */
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;         /* ✅ ปรับตัวหนาพิเศษ */
        font-size: 14px;
        margin: 0 auto;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Verdict Box */
    .verdict-box {
        background-color: #F0F3F4;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        text-align: center;
        font-weight: 600;
        color: #2C3E50;
    }
    
</style>
""", unsafe_allow_html=True)

# --- 3. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_master_data_multiyear.csv")
        latest_year = df['Year'].max()
        df = df[df['Year'] == latest_year].copy()
        
        df['Full_Location'] = df['Amphoe'] + ", " + df['Province']
        
        # Calculate Scores
        df['Score_Price'] = (df['Avg_Land_Price'] / df['Avg_Land_Price'].max()) * 100
        df['Score_Income'] = (df['Avg_Income'] / df['Avg_Income'].max()) * 100
        df['Score_Pop'] = (df['Total_Pop'] / df['Total_Pop'].max()) * 100
        
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- 4. UI Structure ---
st.markdown("""
<div class="header-container">
    <div class="main-title">⚖️ Compare Locations</div>
    <div class="sub-title">เปรียบเทียบศักยภาพทำเล ชัดเจน เข้าใจง่าย</div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("ไม่พบข้อมูล final_master_data_multiyear.csv")
    st.stop()

# --- 5. Selectors ---
col1, col2 = st.columns(2)

locations_list = sorted(df['Full_Location'].unique())

with col1:
    st.markdown("### 🟦 ทำเลที่ 1 (สีฟ้า)")
    idx1 = locations_list.index("เมืองเชียงใหม่, เชียงใหม่") if "เมืองเชียงใหม่, เชียงใหม่" in locations_list else 0
    loc1_name = st.selectbox("เลือกทำเล A", locations_list, index=idx1, key='loc1')

with col2:
    st.markdown("### 🟩 ทำเลที่ 2 (สีเขียว)")
    idx2 = locations_list.index("เมืองขอนแก่น, ขอนแก่น") if "เมืองขอนแก่น, ขอนแก่น" in locations_list else 1
    loc2_name = st.selectbox("เลือกทำเล B", locations_list, index=idx2, key='loc2')

# --- 6. Process Comparison ---
if loc1_name and loc2_name:
    data1 = df[df['Full_Location'] == loc1_name].iloc[0]
    data2 = df[df['Full_Location'] == loc2_name].iloc[0]
    
    st.markdown("---")
    
    # === ส่วนที่ 1: Bar Chart ===
    st.markdown("#### 📊 เปรียบเทียบคะแนนศักยภาพ (Bar Chart)")
    
    categories = ['ราคาที่ดิน', 'รายได้ประชากร', 'จำนวนประชากร']
    scores1 = [data1['Score_Price'], data1['Score_Income'], data1['Score_Pop']]
    scores2 = [data2['Score_Price'], data2['Score_Income'], data2['Score_Pop']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories, x=scores1, name=data1['Amphoe'], orientation='h',
        marker_color='#3498DB', opacity=0.9, text=[f"{s:.0f}/100" for s in scores1], textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        y=categories, x=scores2, name=data2['Amphoe'], orientation='h',
        marker_color='#2ECC71', opacity=0.9, text=[f"{s:.0f}/100" for s in scores2], textposition='auto'
    ))
    
    fig.update_layout(
        barmode='group', xaxis=dict(title='คะแนนศักยภาพ (เต็ม 100)', range=[0, 110]),
        yaxis=dict(autorange="reversed"), height=350, margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Sarabun", size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # === ส่วนที่ 2: Stat Comparison ===
    st.markdown("#### ⚡ วัดกันที่ตัวเลขจริง")
    
    c_stat1, c_stat2, c_stat3 = st.columns(3)
    
    def create_stat_card(title, val1, val2, unit):
        diff = val1 - val2
        if val1 > val2:
            win_color = "color: #3498DB;" 
            win_icon = "🟦 A ชนะ"
        elif val2 > val1:
            win_color = "color: #2ECC71;" 
            win_icon = "🟩 B ชนะ"
        else:
            win_color = "color: #95A5A6;"
            win_icon = "➖ เสมอ"

        # HTML: แก้สีหัวข้อ title เป็น #333333 (ดำเข้ม)
        return f"""<div style="background:white; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05); text-align:center; margin-bottom:10px; border:1px solid #ECF0F1;"><div style="color:#333333; font-size:15px; font-weight:bold; margin-bottom:10px;">{title}</div><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><div style="text-align:left; width:40%;"><div style="color:#3498DB; font-weight:bold; font-size:18px;">{val1:,.0f}</div></div><div style="width:20%;"><div class="vs-badge">VS</div></div><div style="text-align:right; width:40%;"><div style="color:#2ECC71; font-weight:bold; font-size:18px;">{val2:,.0f}</div></div></div><div style="font-size:12px; color:#555555;">ส่วนต่าง {abs(diff):,.0f} {unit}</div><div style="margin-top:5px; font-weight:bold; font-size:13px; {win_color}">{win_icon}</div></div>"""

    with c_stat1:
        st.markdown(create_stat_card("ราคาที่ดินเฉลี่ย", data1['Avg_Land_Price'], data2['Avg_Land_Price'], "บาท"), unsafe_allow_html=True)
    with c_stat2:
        st.markdown(create_stat_card("รายได้ครัวเรือน", data1['Avg_Income'], data2['Avg_Income'], "บาท"), unsafe_allow_html=True)
    with c_stat3:
        st.markdown(create_stat_card("จำนวนประชากร", data1['Total_Pop'], data2['Total_Pop'], "คน"), unsafe_allow_html=True)

    # === ส่วนที่ 3: สรุป ===
    recommendation = ""
    if data1['Score_Price'] < data2['Score_Price'] and data1['Score_Income'] > data2['Score_Income']:
        recommendation = f"✨ **{data1['Amphoe']}** ดูคุ้มค่ากว่า! (ที่ดินถูกกว่า + คนรวยกว่า)"
    elif data2['Score_Price'] < data1['Score_Price'] and data2['Score_Income'] > data1['Score_Income']:
        recommendation = f"✨ **{data2['Amphoe']}** ดูคุ้มค่ากว่า! (ที่ดินถูกกว่า + คนรวยกว่า)"
    elif data1['Total_Pop'] > data2['Total_Pop']:
        recommendation = f"🏙️ หากเน้นคนพลุกพล่าน **{data1['Amphoe']}** ตอบโจทย์กว่ามาก"
    else:
        recommendation = f"🏙️ หากเน้นคนพลุกพล่าน **{data2['Amphoe']}** ตอบโจทย์กว่ามาก"

    st.markdown(f"""<div class="verdict-box">{recommendation}</div>""", unsafe_allow_html=True)