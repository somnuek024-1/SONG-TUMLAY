"""
data_utils.py — Single Source of Truth สำหรับทุกหน้า
ทุกการโหลดและคำนวณข้อมูลอยู่ที่นี่ที่เดียว
"""

import pandas as pd
import numpy as np
import streamlit as st

DATA_FILE = "final_master_data_tambon_price.csv"


# ─────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_raw_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_FILE)
        df.columns = df.columns.str.lstrip("\ufeff").str.strip()
        return df
    except FileNotFoundError:
        st.error(f"❌ ไม่พบไฟล์ '{DATA_FILE}' — กรุณาวางไฟล์ในโฟลเดอร์เดียวกับแอป")
        return pd.DataFrame()


# ─────────────────────────────────────────────────
# COMPUTE  (สูตรทั้งหมดอยู่ที่นี่ที่เดียว)
# ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    คำนวณ Factor และ Score — แก้สูตรที่นี่ที่เดียว มีผลทุกหน้า

    Factor_Density    = (ประชากรตำบล / ค่าเฉลี่ยประชากรจังหวัด) ^ 0.3
    Factor_Centrality = 1.2 ถ้าอำเภอเมือง/เขต, 1.0 อื่นๆ
    Factor_Total      = Density x Centrality  (clip 0.5-3.0)
    Est_Land_Price    = Avg_Land_Price x Factor_Total
    Total_Score       = (Income/Max*3) + (Land/Max*2) + (Pop/Max*5)  → 0-10
    """
    if df.empty:
        return df.copy()

    out = df.copy()

    prov_mean = out.groupby("Province")["Total_Pop"].transform("mean").replace(0, 1)
    out["Factor_Density"] = np.power((out["Total_Pop"] / prov_mean).clip(lower=0), 0.3)
    out["Factor_Centrality"] = out["Amphoe"].apply(
        lambda x: 1.2 if ("เมือง" in str(x) or "เขต" in str(x)) else 1.0
    )
    out["Factor_Total"] = (out["Factor_Density"] * out["Factor_Centrality"]).clip(0.5, 3.0)
    out["Est_Land_Price"] = (out["Avg_Land_Price"] * out["Factor_Total"]).round(2)

    max_inc  = out["Avg_Income"].max()     or 1
    max_land = out["Est_Land_Price"].max() or 1
    max_pop  = out["Total_Pop"].max()      or 1

    out["Total_Score"] = (
        (out["Avg_Income"]     / max_inc  * 3) +
        (out["Est_Land_Price"] / max_land * 2) +
        (out["Total_Pop"]      / max_pop  * 5)
    ).round(2).clip(0, 10)

    return out


@st.cache_data(show_spinner=False)
def get_latest_data() -> pd.DataFrame:
    """ข้อมูลปีล่าสุด + คะแนนครบ"""
    df = compute_scores(load_raw_data())
    if df.empty:
        return df
    return df[df["Year"] == df["Year"].max()].copy()


@st.cache_data(show_spinner=False)
def get_all_years_data() -> pd.DataFrame:
    """ข้อมูลทุกปี + คะแนน"""
    return compute_scores(load_raw_data())


# ─────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────
def score_color(score: float) -> str:
    if score >= 6:  return "#2ECC71"
    if score >= 3:  return "#F1C40F"
    return "#E74C3C"


def score_grade(score: float) -> str:
    if score >= 6:  return "A"
    if score >= 3:  return "B"
    return "C"
