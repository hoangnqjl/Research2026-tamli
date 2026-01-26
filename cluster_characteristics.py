import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. SETUP & DATA LOAD
print("--- PHAN TICH DAC DIEM NOI BAT CUA TUNG CUM (TOP 3 TRAITS) ---")
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    exit()

# 2. DEFINE 17 VARIABLES (INPUT)
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

# Check missing columns
missing = [c for c in feature_cols if c not in df.columns]
if missing:
    print(f"Missing columns: {missing}")
    exit()

model_data = df[feature_cols].dropna()
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# 3. RUN K-MEANS (K=3)
# Exact same settings as before for consistency
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
clusters = kmeans.fit_predict(data_scaled)

# 4. NAMING LOGIC (RE-APPLYING TO ENSURE ACCURACY)
means = model_data.copy()
means['Cluster'] = clusters
grouped_means = means.groupby('Cluster').mean()

cluster_names = {}
cluster_ids = grouped_means.index.tolist()

# Healthy: Lowest Fatigue
healthy_id = grouped_means['[SumScore_Fatigue]'].idxmin()
cluster_names[healthy_id] = "Healthy"
cluster_ids.remove(healthy_id)

# Zombie: Highest Work_Check (Distraction)
remaining = grouped_means.loc[cluster_ids]
zombie_id = remaining['[SumScore_Work_Check]'].idxmax()
cluster_names[zombie_id] = "Zombie"
cluster_ids.remove(zombie_id)

# Burnout: The last one
burnout_id = cluster_ids[0]
cluster_names[burnout_id] = "High-Tech Burnout"

# 5. FIND TOP 3 DISTINCTIVE TRAITS
print(f"\n{'='*60}")
print(f"{'CLUSTER NAME':<20} | {'TOP 3 DISTINCTIVE TRAITS (Dac diem khac biet nhat)':<40}")
print(f"{'='*60}")

for c_id in [0, 1, 2]:
    name = cluster_names[c_id]
    
    # Calculate Difference: This Cluster Mean vs Average of Others
    this_mean = grouped_means.loc[c_id]
    other_mean = grouped_means.drop(c_id).mean()
    diff = this_mean - other_mean
    
    # Sort by Absolute Difference (Magnitude of distinction)
    sorted_diff = diff.abs().sort_values(ascending=False)
    
    # Get Top 3
    top_3 = sorted_diff.head(3).index.tolist()
    
    print(f"\n>>> GROUP: {name.upper()}")
    for i, trait in enumerate(top_3, 1):
        actual_val = this_mean[trait]
        gap = diff[trait]
        
        # Translate variable names to Vietnamese for easier reading (optional)
        # Just keeping original ID for precision as requested
        
        status = "HIGHEST" if gap > 0 else "LOWEST"
        # Compare to average
        avg_others = other_mean[trait]
        
        print(f"   {i}. {trait}")
        print(f"      - {status} vs others (Val: {actual_val:.2f} vs AvgOthers: {avg_others:.2f})")
        if trait == '[SumScore_FOMO_Reaction]':
            print("      -> (It FOMO nhat)")
        if trait == '[SumScore_Work_Check]':
            print("      -> (Xao nhang nhat)" if status=="HIGHEST" else "      -> (Tap trung nhat)")
        if trait == '[SumScore_Fatigue]':
            print("      -> (Kiet suc nhat)" if status=="HIGHEST" else "      -> (Khoe manh nhat)")
        if trait == '[SumScore_Escapism]':
            print("      -> (Thoat ly thuc te)")

print(f"\n{'='*60}")
print("Code completed successfully.")
