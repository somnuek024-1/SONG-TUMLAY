import pandas as pd
import glob
import os

print("🔄 กำลังประมวลผลข้อมูล V5 (Code Matching - แม่นยำ 100%)...")

# --- 1. โหลดพิกัด (Reference from Codes) ---
print("\n1. 📍 โหลดพิกัดตำบล (ใช้รหัส TA_ID)...")
try:
    # อ่าน TA_ID เป็น String เพื่อความชัวร์
    coords = pd.read_csv("raw_data/tambon.csv", dtype={'TA_ID': str, 'CH_ID': str, 'AM_ID': str})
    
    # ล้างชื่อให้สะอาดเพื่อความสวยงาม
    coords['Tambon'] = coords['TAMBON_T'].str.replace(r'^[ต]\.\s*', '', regex=True).str.strip()
    coords['Amphoe'] = coords['AMPHOE_T'].str.replace(r'^[อ]\.\s*', '', regex=True).str.strip()
    coords['Province'] = coords['CHANGWAT_T'].str.replace(r'^[จ]\.\s*', '', regex=True).str.strip()
    
    # เตรียม Key สำหรับจับคู่ (TA_ID 6 หลัก)
    # บางทีอาจมีจุดทศนิยมถ้าอ่านผิด ให้แก้เป็น int ก่อนแล้วค่อย str
    coords['Join_ID'] = coords['TA_ID'].astype(str).str.split('.').str[0]
    
    # เลือกคอลัมน์
    coords = coords[['Join_ID', 'Province', 'Amphoe', 'Tambon', 'LAT', 'LONG']].copy()
    coords.rename(columns={'LAT': 'lat', 'LONG': 'lon'}, inplace=True)
    
    # ลบแถวที่ไม่มีพิกัด
    coords = coords.dropna(subset=['lat', 'lon'])
    
    # Group by ID (เผื่อมีซ้ำ)
    coords = coords.groupby('Join_ID').agg({
        'Province': 'first', 'Amphoe': 'first', 'Tambon': 'first',
        'lat': 'mean', 'lon': 'mean'
    }).reset_index()
    
    print(f"   ✅ พบรหัสตำบล {len(coords):,} แห่ง")
    
except Exception as e:
    print(f"❌ Error พิกัด: {e}")
    exit()

# --- 2. โหลดเศรษฐกิจ (Economy) ---
print("\n2. 💰 โหลดข้อมูลเศรษฐกิจ...")
econ_years = {}
try:
    econ_df = pd.read_csv("raw_data/Thailand_Complete_Analysis_Yearly_All.csv")
    valid_years = sorted(econ_df['ปีพ.ศ'].unique())
    
    for y in valid_years:
        sub = econ_df[econ_df['ปีพ.ศ'] == y].copy()
        # Clean Province Name ให้ตรงกับ Standard ใน coords
        # (เช่น 'จ.กรุงเทพ' -> 'กรุงเทพมหานคร')
        # วิธีง่ายสุด: เราจะ Merge ด้วยชื่อจังหวัด (ต้อง Clean นิดหน่อย)
        sub['Province_Clean'] = sub['จังหวัด'].astype(str).str.replace(r'จังหวัด|จ\.', '', regex=True).str.strip()
        econ_years[y] = sub[['Province_Clean', 'รายได้เฉลี่ยต่อครัวเรือน', 'ราคาที่ดินเฉลี่ย(บาท/ตร.ว)']]
        econ_years[y].columns = ['Province_Clean', 'Avg_Income', 'Avg_Land_Price']
        
except Exception as e:
    print(f"❌ Error เศรษฐกิจ: {e}")
    exit()

# --- 3. โหลดประชากร (Population by Code) ---
print("\n3. 👥 ประมวลผลประชากร (จับคู่ด้วยรหัส)...")
pop_files = sorted(glob.glob("raw_data/stat_m*.csv"))
all_data = []

for f in pop_files:
    fname = os.path.basename(f)
    y_str = ''.join(filter(str.isdigit, fname))
    if len(y_str) >= 2:
        year = int(y_str[-2:]) + 2500
    else:
        continue
        
    if year not in econ_years:
        continue
        
    print(f"   > ปี {year}...", end=" ")
    
    try:
        try:
            # อ่านรหัสตำบลเป็น String
            df = pd.read_csv(f, thousands=',', dtype={'รหัสตำบล': str, 'รหัสจังหวัด': str})
        except:
            df = pd.read_csv(f, thousands=',', encoding='tis-620', dtype={'รหัสตำบล': str, 'รหัสจังหวัด': str})
            
        # ลบช่องว่างหัวคอลัมน์
        df.columns = df.columns.str.strip()
        
        # หาคอลัมน์สำคัญ
        c_pop = next((c for c in df.columns if 'ประชากรทั้งหมด' in c or 'รวมทั้งสิ้น' in c), None)
        c_code = 'รหัสตำบล'
        
        if not c_pop or c_code not in df.columns:
            print("      ❌ ไม่พบคอลัมน์รหัสตำบล หรือ ประชากร")
            continue
            
        # กรองข้อมูล (รหัสตำบลต้องมีค่า และไม่เป็น 0, รหัสหมู่บ้านเป็น 0)
        # หมายเหตุ: เราใช้ Code เป็นหลัก ดังนั้นชื่อไม่สำคัญเท่าไหร่
        if 'รหัสหมู่บ้าน' in df.columns:
            # แปลงเป็น str ก่อนเทียบ
            df = df[df['รหัสหมู่บ้าน'].astype(str) == '0']
        
        df = df[df[c_code].notna() & (df[c_code] != '0')].copy()
        
        # สร้าง Join_ID (ตัด 2 หลักท้ายทิ้ง: 10010100 -> 100101)
        # รหัสตำบลใน stat มักจะมี 8 หลัก (2 จว + 2 อ + 2 ต + 2 ม)
        # รหัสตำบลใน coords มี 6 หลัก (2 จว + 2 อ + 2 ต)
        df['Join_ID'] = df[c_code].astype(str).str.slice(0, 6)
        
        # แปลงประชากร
        df['Total_Pop'] = pd.to_numeric(df[c_pop].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        # เลือกเฉพาะที่ต้องใช้
        df_pop_clean = df[['Join_ID', 'Total_Pop']].groupby('Join_ID').sum().reset_index()
        
        # --- MERGE ---
        # 1. เอาโครงจาก Coords (ที่มีชื่อถูกต้อง + พิกัด) มาตั้ง
        # 2. แปะยอดประชากรจาก stat (โดยใช้ Join_ID)
        merged = pd.merge(coords, df_pop_clean, on='Join_ID', how='inner')
        
        # 3. แปะข้อมูลเศรษฐกิจ (ใช้ชื่อจังหวัดจาก Coords)
        # ต้อง Clean ชื่อจังหวัดใน Coords อีกนิดเพื่อให้ตรงกับ Econ
        merged['Province_Clean'] = merged['Province'].str.replace(r'จังหวัด|จ\.', '', regex=True).str.strip()
        merged['Province_Clean'] = merged['Province_Clean'].replace({'กทม.': 'กรุงเทพมหานคร', 'กทม': 'กรุงเทพมหานคร'})
        
        # แก้ปัญหากรุงเทพ (Coords ใช้ 'กรุงเทพมหานคร' หรือเปล่า?)
        # ใน tambon.csv ปกติคือ "จ. กรุงเทพมหานคร" -> Clean แล้วได้ "กรุงเทพมหานคร"
        
        merged_final = pd.merge(merged, econ_years[year], on='Province_Clean', how='left')
        merged_final['Year'] = year
        
        # ลบคอลัมน์ช่วย
        if 'Province_Clean' in merged_final.columns:
            del merged_final['Province_Clean']
            
        count = len(merged_final)
        print(f"-> ได้ {count:,} แถว")
        
        all_data.append(merged_final)
        
    except Exception as e:
        print(f"\n      ❌ Error: {e}")

# --- Save ---
if all_data:
    master = pd.concat(all_data)
    master.to_csv("final_master_data_multiyear.csv", index=False, encoding='utf-8-sig')
    print(f"\n✅ สำเร็จ! ข้อมูลทั้งหมด {len(master):,} แถว")
    
    # Check Bangkok
    bkk = master[master['Province'].str.contains('กรุงเทพ')]
    print(f"🔎 เช็ค: พบข้อมูลกรุงเทพฯ {len(bkk)} แถว")
else:
    print("\n❌ ไม่ได้ข้อมูลเลย")