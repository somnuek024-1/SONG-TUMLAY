import pandas as pd
import glob
import os

print("🔍 เริ่มการตรวจสอบข้อมูล (Diagnostics)...")

# 1. ตรวจไฟล์พิกัด (tambon.csv)
print("\n--- 1. ตรวจสอบไฟล์พิกัด (raw_data/tambon.csv) ---")
if os.path.exists("raw_data/tambon.csv"):
    try:
        # ลองอ่านแบบปกติ
        df_coord = pd.read_csv("raw_data/tambon.csv", nrows=5)
        print("✅ อ่านไฟล์สำเร็จ! ตัวอย่าง 5 แถวแรก:")
        print(df_coord.to_string()) # Print all columns
        print("\nรายชื่อคอลัมน์:", df_coord.columns.tolist())
    except Exception as e:
        print(f"❌ อ่านไม่ได้: {e}")
else:
    print("❌ หาไฟล์ raw_data/tambon.csv ไม่เจอ")

# 2. ตรวจไฟล์ประชากร (stat_m*.csv)
print("\n--- 2. ตรวจสอบไฟล์ประชากร (stat_m*.csv) ---")
pop_files = glob.glob("raw_data/stat_m*.csv")
if pop_files:
    target_file = pop_files[0]
    print(f"เจอไฟล์: {target_file}")
    try:
        # ลองอ่านด้วย encoding ต่างๆ
        try:
            df_pop = pd.read_csv(target_file, thousands=',', nrows=5)
            encoding_used = "utf-8 (default)"
        except:
            df_pop = pd.read_csv(target_file, thousands=',', encoding='tis-620', nrows=5)
            encoding_used = "tis-620"
            
        print(f"✅ อ่านไฟล์สำเร็จ (ใช้ {encoding_used})! ตัวอย่าง 5 แถวแรก:")
        print(df_pop.to_string())
        print("\nรายชื่อคอลัมน์:", df_pop.columns.tolist())
        
        # เช็คชื่อจังหวัดในไฟล์จริง
        if 'ชื่อจังหวัด' in df_pop.columns:
            print("\nตัวอย่างชื่อจังหวัด:", df_pop['ชื่อจังหวัด'].unique())
        elif 'จังหวัด' in df_pop.columns:
            print("\nตัวอย่างชื่อจังหวัด:", df_pop['จังหวัด'].unique())
            
    except Exception as e:
        print(f"❌ อ่านไม่ได้: {e}")
else:
    print("❌ ไม่พบไฟล์ stat_m*.csv ในโฟลเดอร์ raw_data")

print("\n--- จบการตรวจสอบ ---")