import pandas as pd
import numpy as np
import streamlit as st

CSV_FILE = "final_master_data_tambon_price.csv"

@st.cache_data
def load_and_process() -> pd.DataFrame:
    """
    โหลดและประมวลผลข้อมูลครั้งเดียว แชร์ใช้ทุกหน้า
    แก้ไข:
      - ชื่อไฟล์ CSV รวมไว้ที่เดียว
      - คำนวณ factors / score จากข้อมูลทั้งหมด (global max) ให้คะแนนสอดคล้องกันทุกหน้า
      - lat/lon ใช้ค่าจริงจาก CSV ไม่สุ่ม noise
    """
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        st.error(f"❌ ไม่พบไฟล์ {CSV_FILE} กรุณาตรวจสอบ path")
        return pd.DataFrame()

    # ใช้ข้อมูลปีล่าสุด
    latest_year = df["Year"].max()
    df = df[df["Year"] == latest_year].copy()

    # --- ราคาฐาน ---
    if "Base_Land_Price_Prov" in df.columns:
        df["Avg_Land_Price"] = df["Base_Land_Price_Prov"]

    # --- Factor: Density (ความหนาแน่นประชากรเทียบระดับจังหวัด) ---
    prov_pop_mean = (
        df.groupby("Province")["Total_Pop"]
        .transform("mean")
        .replace(0, 1)
    )
    pop_ratio = df["Total_Pop"] / prov_pop_mean
    df["Factor_Density"] = np.power(pop_ratio, 0.3).clip(0.5, 2.0)

    # --- Factor: Centrality (โซนอำเภอ) แบบ 3 ระดับ ---
    def centrality_score(amphoe: str) -> float:
        a = str(amphoe)
        if "เมือง" in a or "เขต" in a:
            return 1.2  # ศูนย์กลาง
        secondary_keywords = ["บางรัก", "ห้วยขวาง", "ลาดกระบัง", "มีนบุรี",
                              "บึงกุ่ม", "สาทร", "บางนา", "คลอง"]
        if any(kw in a for kw in secondary_keywords):
            return 1.1  # อำเภอรอง
        return 1.0      # รอบนอก

    df["Factor_Centrality"] = df["Amphoe"].apply(centrality_score)
    df["Factor_Total"] = (df["Factor_Density"] * df["Factor_Centrality"]).clip(0.5, 3.0)
    df["Est_Land_Price"] = df["Avg_Land_Price"] * df["Factor_Total"]

    # --- Total Score (normalize จาก global max เสมอ ไม่ขึ้นกับ filter) ---
    max_inc  = df["Avg_Income"].max() or 1
    max_land = df["Est_Land_Price"].max() or 1
    max_pop  = df["Total_Pop"].max() or 1

    df["Total_Score"] = (
        (df["Avg_Income"]     / max_inc  * 3) +
        (df["Est_Land_Price"] / max_land * 2) +
        (df["Total_Pop"]      / max_pop  * 5)
    ).round(2)

    # --- lat/lon: ใช้ค่าจริงจากไฟล์เท่านั้น ไม่ random noise ---
    if "lat" not in df.columns or "lon" not in df.columns:
        PROVINCE_COORDS = {
            "กรุงเทพมหานคร": [13.7563, 100.5018], "เชียงใหม่": [18.7883, 98.9853],
            "ขอนแก่น": [16.4322, 102.8236], "ภูเก็ต": [7.8804, 98.3923],
            "นครราชสีมา": [14.9799, 102.0978], "ชลบุรี": [13.3611, 100.9847],
            "สงขลา": [7.1988, 100.5951], "อุดรธานี": [17.4138, 102.7872],
            "ระยอง": [12.6815, 101.2816], "พระนครศรีอยุธยา": [14.3532, 100.5684],
            "สุราษฎร์ธานี": [9.1382, 99.3217], "เชียงราย": [19.9105, 99.8406],
            "อุบลราชธานี": [15.2448, 104.8473], "พิษณุโลก": [16.8211, 100.2659],
            "กาญจนบุรี": [14.0225, 99.5327],
        }
        coords = df["Province"].apply(lambda p: PROVINCE_COORDS.get(p, [13.7563, 100.5018]))
        df["lat"] = coords.apply(lambda c: c[0])
        df["lon"] = coords.apply(lambda c: c[1])

    return df


def filter_df(
    df: pd.DataFrame,
    province: str = "ทั้งหมด",
    amphoe: str = "ทั้งหมด",
    price_min: float = 0,
    price_max: float = float("inf"),
) -> pd.DataFrame:
    """Helper กรองข้อมูลตาม filter ที่ผู้ใช้เลือก"""
    out = df.copy()
    out = out[(out["Est_Land_Price"] >= price_min) & (out["Est_Land_Price"] <= price_max)]
    if province != "ทั้งหมด":
        out = out[out["Province"] == province]
    if amphoe != "ทั้งหมด":
        out = out[out["Amphoe"] == amphoe]
    return out
