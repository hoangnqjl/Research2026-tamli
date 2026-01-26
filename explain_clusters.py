import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# EXPLAINABLE CLUSTERING (Giai thich cum bang Cay Quyet Dinh)
# Muc tieu: Tim ra "Luat" (Rules) de xac dinh mot nguoi thuoc cum nao.
# ==============================================================================

print("--- [EXPLAIN CLUSTERS] BAT DAU PHAN TICH LUAT PHAN LOAI ---")

# 1. LOAD DATA
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error: {e}")
    exit()

# 2. INPUT: 17 VARS
feature_cols = [
    '[SumScore_Work_Check]', '[SumScore_Source_Check]', '[SumScore_Sleep_Loss]',
    '[SumScore_Obsess_Loop]', '[SumScore_Obsess_Debate]', '[SumScore_Obsess_Celeb]',
    '[SumScore_FOMO_Reaction]', '[SumScore_Fatigue]', '[SumScore_Escapism]',
    '[SumScore_Deepfake_Detect]', '[SumScore_Deep_Reading]', '[SumScore_Crowd_Pressure]',
    '[SumScore_Control_Time]', '[SumScore_Clickbait_Aware]', '[SumScore_AI_Trust]',
    '[SumScore_AI_Freq]', '[SumBeh_Study_Score]'
]

model_data = df[feature_cols].dropna()
X = model_data.values

# 3. K-MEANS (BLIND - KHONG BIET TEN)
# Chung ta van chay K=3 de tim ra cau truc tu nhien
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
labels = kmeans.fit_predict(X_scaled)

# 4. DECISION TREE (De tim ra Luat)
# Chung ta huan luyen cay quyet dinh de "hoc" lai ket qua cua K-Means
# Cay se chon ra nhung bien quan trong nhat de phan chia.
tree = DecisionTreeClassifier(max_depth=3, random_state=42) # Max depth 3 de luat don gian, de hieu
tree.fit(model_data, labels) # Train on RAW scores for readability (not scaled)

# 5. HIEN THI LUAT (RULES)
print("\n" + "="*60)
print("CAC LUAT QUYET DINH (DECISION RULES)")
print("Cach doc: Neu [Bien] <= [Gia tri] thi di theo nhanh do.")
print("="*60)

# Lay ten cac bien cho de doc
r = export_text(tree, feature_names=feature_cols)
print(r)

# 6. FEATURE IMPORTANCE (Bien nao quan trong nhat?)
print("\n" + "="*60)
print("MUC DO QUAN TRONG CUA TUNG BIEN (FEATURE IMPORTANCE)")
print("Bien nao co % cao nhat la bien quyet dinh 'song con' de phan chia.")
print("="*60)

importances = tree.feature_importances_
indices = np.argsort(importances)[::-1]

for i in range(len(feature_cols)):
    if importances[indices[i]] > 0: # Chi hien thi bien co tac dong
        print(f"{i+1}. {feature_cols[indices[i]]:<30} : {importances[indices[i]]*100:.1f}%")

# 7. IDENTIFY CLUSTERS (Tu dong dat ten dua tren luat)
# De nguoi dung biet Class 0, 1, 2 la gi
print("\n" + "="*60)
print("NHAN DIEN CUM (MAPPING)")
print("="*60)
# Tinh trung binh tung cum de biet no la ai
model_data['Cluster'] = labels
means = model_data.groupby('Cluster').mean()

for c_id in [0, 1, 2]:
    # Check key traits identified previously
    fomo = means.loc[c_id, '[SumScore_FOMO_Reaction]']
    work_check = means.loc[c_id, '[SumScore_Work_Check]']
    fatigue = means.loc[c_id, '[SumScore_Fatigue]']
    
    guess = "Unknown"
    if fomo < 2.0: guess = "-> (Kha nang la Burnout/Ly tri)"
    elif work_check > 3.0 and fomo > 2.5: guess = "-> (Kha nang la Zombie/No le)"
    else: guess = "-> (Kha nang la Healthy/Can bang)"
    
    print(f"Class {c_id}: FOMO={fomo:.1f}, Distraction={work_check:.1f}, Fatigue={fatigue:.1f} {guess}")

# 8. SUMMARY STATISTICS (Thong ke so luong)
print("\n" + "="*60)
print("THONG KE SO LUONG (SUMMARY)")
print("="*60)

# Map labels to names based on our logic
# Note: K-Means labels might change IDs (0,1,2) but the logic (Means) remains same.
# We use the mapping derived above.
cluster_name_map = {}
for c_id in [0, 1, 2]:
    fomo = means.loc[c_id, '[SumScore_FOMO_Reaction]']
    work_check = means.loc[c_id, '[SumScore_Work_Check]']
    
    if fomo < 2.0: 
        cluster_name_map[c_id] = "High-Tech Burnout"
    elif work_check > 3.0 and fomo > 2.5: 
        cluster_name_map[c_id] = "Zombie"
    else: 
        cluster_name_map[c_id] = "Healthy"

counts = pd.Series(labels).value_counts().sort_index()
total = len(model_data)

print(f"{'Cluster ID':<10} | {'Name':<20} | {'Count':<10} | {'Ratio':<10}")
print("-" * 60)

for c_id in [0, 1, 2]:
    name = cluster_name_map.get(c_id, "Unknown")
    count = counts.get(c_id, 0)
    ratio = (count / total) * 100
    print(f"{c_id:<10} | {name:<20} | {count:<10} | {ratio:.1f}%")
    
print("-" * 60)
print(f"{'TOTAL':<10} | {'':<20} | {total:<10} | 100%")

# 9. SECONDARY DIFFERENTIATORS (Cac yeu to phan biet phu)
print("\n" + "="*60)
print("CAC HANH VI PHAN BIET KHAC (SECONDARY DIFFERENTIATORS)")
print("Ngoai 3 bien chinh (FOMO, Distraction, Fatigue), cac bien sau day cung phan biet ro ret:")
print("="*60)

# Define main 3 to exclude from this list
main_traits = ['[SumScore_FOMO_Reaction]', '[SumScore_Work_Check]', '[SumScore_Fatigue]']
remaining_traits = [c for c in feature_cols if c not in main_traits]

# Calculate ranges for normalization again inside this script
ranges = {}
for trait in feature_cols:
    val_min = model_data[trait].min()
    val_max = model_data[trait].max()
    ranges[trait] = val_max - val_min if (val_max - val_min) > 0 else 1.0

for c_id in [0, 1, 2]:
    name = cluster_name_map.get(c_id, "Unknown")
    print(f"\n>>> {name.upper()} (vs Others):")
    
    this_mean = means.loc[c_id]
    # Calculate mean of OTHER groups for comparison
    other_mean = means.drop(c_id).mean()
    diff = this_mean - other_mean
    
    # Sort remaining traits by impact
    impacts = []
    for trait in remaining_traits:
        norm_diff = diff[trait] / ranges[trait]
        impacts.append((trait, norm_diff, this_mean[trait]))
        
    # Sort descending abs
    impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Print Top 3 Secondary
    for trait, ndiff, val in impacts[:3]:
        status = "HIGHER" if ndiff > 0 else "LOWER"
        print(f"   - {trait:<30} : {status:<6} ({ndiff*100:+.1f}%) -> Val: {val:.2f}")
        
        # Add interpretation
        if trait == '[SumScore_Obsess_Debate]' and ndiff > 0: print("     (Thich tranh luan/Gay gat)")
        if trait == '[SumScore_Escapism]' and ndiff > 0: print("     (Tron tranh thuc tai)")
        if trait == '[SumScore_Sleep_Loss]' and ndiff > 0: print("     (Mat ngu nghiem trong)")
        if trait == '[SumScore_Crowd_Pressure]' and ndiff < 0: print("     (It bi ap luc dam dong)")


        if trait == '[SumScore_Crowd_Pressure]' and ndiff < 0: print("     (It bi ap luc dam dong)")

# 10. TARGETED ANALYSIS (Phan tich 4 dac diem ban yeu cau)
print("\n" + "="*60)
print("PHAN TICH SAU 4 DAC DIEM CHI DINH (TARGETED ANALYSIS)")
print("1. Tron tranh (Escapism) | 2. Mat ngu (Sleep Loss)")
print("3. Kiem soat (Control Time) | 4. Tin AI (AI Trust)")
print("="*60)

target_traits = [
    '[SumScore_Escapism]', 
    '[SumScore_Sleep_Loss]', 
    '[SumScore_Control_Time]', 
    '[SumScore_AI_Trust]'
]

# Calculate global averages for comparison context
global_means = model_data[target_traits].mean()

print(f"{'Cluster':<20} | {'Trait':<25} | {'Value':<6} | {'Status (vs Global Avg)':<20}")
print("-" * 80)

for c_id in [0, 1, 2]:
    name = cluster_name_map.get(c_id, "Unknown")
    this_mean = means.loc[c_id]
    
    for trait in target_traits:
        val = this_mean[trait]
        global_avg = global_means[trait]
        diff_pct = (val - global_avg) / ranges[trait] * 100
        
        status = "Unknown"
        if diff_pct > 10: status = "++ CAO HON TB"
        elif diff_pct < -10: status = "-- THAP HON TB"
        else: status = "== NGANGBANG TB"
        
        # Highlight distinct ones only? No, user wants to see all 4.
        print(f"{name:<20} | {trait:<25} | {val:<6.2f} | {status:<20} ({diff_pct:+.1f}%)")
    print("-" * 80)

print("\nAnalysis Completed.")
