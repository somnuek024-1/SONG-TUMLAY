import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# ==========================================
# 1. ตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(
    page_title="SONGTUMLAY | ส่องทำเลทอง",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. ฟังก์ชันโหลดข้อมูล (Cache Data เพื่อความเร็ว)
# ==========================================
@st.cache_data
def load_data():
    # อ่านไฟล์ Master Data ฉบับสมบูรณ์ของเรา
    df = pd.read_csv("final_master_data_tambon_price.csv")
    
    # ดึงเฉพาะข้อมูลปีล่าสุด
    latest_year = df['Year'].max()
    df = df[df['Year'] == latest_year].copy()
    
    # ลบแถวที่พิกัดแผนที่ (lat, lon) ว่างเปล่าออก ป้องกันแผนที่พัง
    df = df.dropna(subset=['lat', 'lon'])
    return df

df = load_data()

# ==========================================
# 3. แถบเมนูด้านข้าง (Sidebar Filters & Weights)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/854/854878.png", width=80)
st.sidebar.title("⚙️ ปรับแต่งทำเลทอง")
st.sidebar.markdown("เลือกปัจจัยที่สำคัญสำหรับธุรกิจของคุณ")

# 3.1 ฟิลเตอร์จังหวัด
all_provinces = sorted(df['Province'].unique().tolist())
selected_prov = st.sidebar.multiselect(
    "📍 เลือกระบุจังหวัด (เว้นว่างเพื่อดูทั้งประเทศ):", 
    all_provinces, 
    default=["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี"]
)

# 3.2 แถบเลื่อนปรับน้ำหนัก AI (AI Weights)
st.sidebar.subheader("🧠 ให้น้ำหนักการคำนวณคะแนน")
w_pop = st.sidebar.slider("👥 ความหนาแน่นประชากร", 0, 100, 50)
w_inc = st.sidebar.slider("💰 กำลังซื้อ (รายได้เฉลี่ยสูง)", 0, 100, 30)
w_price = st.sidebar.slider("🏷️ ต้นทุนที่ดิน (เน้นราคาถูก)", 0, 100, 20)

# ==========================================
# 4. ประมวลผลและคำนวณคะแนน (Data Processing)
# ==========================================
# กรองข้อมูลตามจังหวัดที่เลือก
if selected_prov:
    filter_df = df[df['Province'].isin(selected_prov)].copy()
else:
    filter_df = df.copy()

# คำนวณค่า Max ของแต่ละคอลัมน์เพื่อทำ Normalization (ทำให้เป็นสัดส่วน 0-1)
max_pop = filter_df['Total_Pop'].max() or 1
max_inc = filter_df['Avg_Income'].max() or 1
max_price = filter_df['Avg_Land_Price'].max() or 1

# สูตรคำนวณคะแนนทำเล (คะแนนเต็ม 100)
# ข้อสังเกต: ราคาที่ดินใช้สูตร (1 - สัดส่วนราคา) เพราะยิ่งที่ดินถูก ควรจะได้คะแนนความคุ้มค่าสูง
filter_df['Score'] = (
    (filter_df['Total_Pop'] / max_pop * w_pop) +
    (filter_df['Avg_Income'] / max_inc * w_inc) +
    ((1 - (filter_df['Avg_Land_Price'] / max_price)) * w_price)
).round(2)

# เรียงลำดับจากคะแนนมากไปน้อย
filter_df = filter_df.sort_values(by='Score', ascending=False).reset_index(drop=True)

# ==========================================
# 5. พื้นที่แสดงผลหลัก (Main Dashboard)
# ==========================================
st.title("🏙️ SONGTUMLAY (ส่องทำเล)")
st.markdown("ระบบ AI วิเคราะห์และจัดอันดับทำเลศักยภาพทั่วประเทศไทย อ้างอิงจากข้อมูลจริงของภาครัฐ")

# 5.1 กล่องสรุปสถิติ (KPIs)
st.subheader("📊 ภาพรวมพื้นที่ที่ค้นหา")
col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนตำบลที่พบ", f"{len(filter_df):,} พื้นที่")
col2.metric("ราคาที่ดินเฉลี่ย", f"{filter_df['Avg_Land_Price'].mean():,.0f} ฿/ตร.ว.")
col3.metric("รายได้เฉลี่ย", f"{filter_df['Avg_Income'].mean():,.0f} ฿/เดือน")
col4.metric("ทำเลที่คะแนนสูงสุด", f"{filter_df['Tambon'].iloc[0] if len(filter_df)>0 else '-'}")

st.divider()

# 5.2 แผนที่แบบ 3D Interactive (PyDeck)
st.subheader("🗺️ แผนที่ความร้อน (Heatmap & Scatter)")
st.markdown("*จุดสีแดงขนาดใหญ่ หมายถึง พื้นที่ที่มีคะแนนทำเลสูงตามเกณฑ์ที่คุณตั้งไว้*")

if not filter_df.empty:
    # ตั้งค่าจุดศูนย์กลางแผนที่
    midpoint = (np.average(filter_df['lat']), np.average(filter_df['lon']))
    
    # สร้างเลเยอร์จุดบนแผนที่
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filter_df,
        get_position="[lon, lat]",
        get_radius="Score * 30", # ยิ่งคะแนนเยอะ วงกลมยิ่งใหญ่
        get_color="[255, 75, 75, 160]", # สีแดงโปร่งแสง
        pickable=True,
    )

    # วาดแผนที่
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=9,
            pitch=40, # แกนเอียง 3 มิติ
        ),
        layers=[layer],
        tooltip={"text": "ต.{Tambon} อ.{Amphoe} จ.{Province}\nคะแนน: {Score}\nประชากร: {Total_Pop} คน\nราคาประเมิน: {Avg_Land_Price} ฿/ตร.ว."}
    ))
else:
    st.warning("ไม่พบข้อมูลสำหรับพื้นที่ที่คุณเลือก")

st.divider()

# 5.3 ตารางจัดอันดับ (Top 10 Leaderboard)
st.subheader("🏆 10 อันดับทำเลทองที่น่าลงทุนที่สุด")

# จัดรูปแบบตารางให้สวยงามก่อนแสดงผล
display_df = filter_df[['Province', 'Amphoe', 'Tambon', 'Score', 'Total_Pop', 'Avg_Income', 'Avg_Land_Price']].head(50).copy()
display_df.columns = ['จังหวัด', 'อำเภอ/เขต', 'ตำบล/แขวง', 'คะแนนทำเล (เต็ม 100)', 'ประชากร (คน)', 'รายได้ (บาท/เดือน)', 'ราคาที่ดิน (บาท/ตร.ว.)']

# แสดงตารางแบบให้ผู้ใช้กดเรียง (Sort) ได้เอง
st.dataframe(
    display_df.style.format({
        'คะแนนทำเล (เต็ม 100)': '{:.2f}',
        'ประชากร (คน)': '{:,.0f}',
        'รายได้ (บาท/เดือน)': '{:,.0f}',
        'ราคาที่ดิน (บาท/ตร.ว.)': '{:,.0f}'
    }).background_gradient(subset=['คะแนนทำเล (เต็ม 100)'], cmap='YlOrRd'),
    use_container_width=True,
    height=400
)

st.caption("อ้างอิงข้อมูลประชากรและรายได้จากสำนักงานสถิติแห่งชาติ และราคาประเมินที่ดินจากกรมธนารักษ์ (รอบบัญชี 2566-2569)")
