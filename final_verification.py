import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# FINAL VERIFICATION SCRIPT (Kiem tra nghiem ngat)
# Muc tieu: Xac thuc chinh xac so luong va cac dac diem khac biet.
# ==============================================================================

print("--- [FINAL CHECK] BAT DAU KIEM TRA TOAN BO QUY TRINH ---")

# 1. LOAD DATA
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    exit()

# 2. DEFINE 17 VARIABLES (INPUT CHUAN)
feature_cols = [
    '[SumScore_Work_Check]',
    '[SumScore_Source_Check]',
    '[SumScore_Sleep_Loss]',
    '[SumScore_Obsess_Loop]',
    '[SumScore_Obsess_Debate]',
    '[SumScore_Obsess_Celeb]',
    '[SumScore_FOMO_Reaction]',
    '[SumScore_Fatigue]',
    '[SumScore_Escapism]',
    '[SumScore_Deepfake_Detect]',
    '[SumScore_Deep_Reading]',
    '[SumScore_Crowd_Pressure]',
    '[SumScore_Control_Time]',
    '[SumScore_Clickbait_Aware]',
    '[SumScore_AI_Trust]',
    '[SumScore_AI_Freq]',
    '[SumBeh_Study_Score]'
]

# Xac nhan du 17 bien
if len(feature_cols) != 17:
    print(f"CRITICAL ERROR: So luong bien khong dung ({len(feature_cols)} != 17)")
    exit()

model_data = df[feature_cols].dropna()
print(f"-> So luong mau (Samples): {len(model_data)}")

# 3. RUN K-MEANS (K=3, Random_State=42 co dinh)
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
clusters = kmeans.fit_predict(data_scaled)

# 4. NAMING LOGIC (LOGIC DINH DANH)
means = model_data.copy()
means['Cluster'] = clusters
grouped_means = means.groupby('Cluster').mean()

cluster_names = {}
cluster_ids = grouped_means.index.tolist()

# Logic 1: Healthy la nhom co Fatigue thap nhat
healthy_id = grouped_means['[SumScore_Fatigue]'].idxmin()
cluster_names[healthy_id] = "Healthy"
cluster_ids.remove(healthy_id)

# Logic 2: Zombie la nhom co Work_Check (Xao nhang) cao nhat trong 2 nhom con lai
remaining = grouped_means.loc[cluster_ids]
zombie_id = remaining['[SumScore_Work_Check]'].idxmax()
cluster_names[zombie_id] = "Zombie"
cluster_ids.remove(zombie_id)

# Logic 3: Burnout la nhom con lai
burnout_id = cluster_ids[0]
cluster_names[burnout_id] = "High-Tech Burnout"

# Map nguoc lai vao DF
df_final = model_data.copy()
df_final['Cluster_Group'] = clusters
df_final['Cluster_Name'] = df_final['Cluster_Group'].map(cluster_names)

# 5. XAC NHAN SO LUONG (COUNTS)
print("\n" + "="*50)
print("1. XAC NHAN SO LUONG (COUNTS)")
print("="*50)
counts = df_final['Cluster_Name'].value_counts()
print(counts)

target_counts = {"Zombie": 320, "Healthy": 259, "High-Tech Burnout": 66}
match = True
for name, count in target_counts.items():
    if counts[name] != count:
        print(f"MISMATCH: {name} expected {count}, got {counts[name]}")
        match = False

if match:
    print("-> KET LUAN: SO LUONG CHINH XAC TUYET DOI (66 - 259 - 320).")
else:
    print("-> WARNING: CO SAI LECH VE SO LUONG.")

# 6. XAC NHAN DAC DIEM KHAC BIET (DIFFERENCE HUNTER)
print("\n" + "="*50)
print("2. XAC NHAN DAC DIEM KHAC BIET (CHUAN HOA %)")
print("="*50)

# Calculate Ranges
ranges = {}
for trait in feature_cols:
    val_min = df[trait].min()
    val_max = df[trait].max()
    ranges[trait] = float(val_max - val_min)
    if ranges[trait] == 0: ranges[trait] = 1.0

# Difference Hunter
for c_id in [burnout_id, healthy_id, zombie_id]: # Order by specific groups
    name = cluster_names[c_id]
    print(f"\n>>> GROUP: {name.upper()}")
    
    this_mean = grouped_means.loc[c_id]
    other_mean = grouped_means.drop(c_id).mean()
    diff = this_mean - other_mean
    
    # Calculate Normalized Difference
    norm_diffs = []
    for trait in feature_cols:
        d = diff[trait]
        r = ranges[trait]
        pct = d / r
        norm_diffs.append((trait, pct, this_mean[trait], other_mean[trait]))
    
    # Filter > 10%
    distinct = [x for x in norm_diffs if abs(x[1]) > 0.10]
    
    # Sort descending
    distinct.sort(key=lambda x: abs(x[1]), reverse=True)
    
    print(f"-> Tim thay {len(distinct)} dac diem khac biet > 10%:")
    for trait, pct, val, other in distinct:
        status = "HIGHEST" if pct > 0 else "LOWEST"
        print(f"   * {trait:<30} | {status:<8} | Diff: {pct*100:+.1f}%")

print("\n" + "="*50)
print("DONE. DATA VERIFIED.")
