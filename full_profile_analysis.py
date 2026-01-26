import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. LOAD DATA
print("--- [FULL PROFILE] PHAN TICH TOAN BO 17 CHI SO ---")
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    exit()

# 2. DEFINE 17 VARIABLES
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

model_data = df[feature_cols].dropna()
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# 3. RUN K-MEANS (K=3)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
clusters = kmeans.fit_predict(data_scaled)

# 4. NAMING LOGIC
means = model_data.copy()
means['Cluster'] = clusters
grouped_means = means.groupby('Cluster').mean()

cluster_names = {}
cluster_ids = grouped_means.index.tolist()

# Healthy: Lowest Fatigue
healthy_id = grouped_means['[SumScore_Fatigue]'].idxmin()
cluster_names[healthy_id] = "Healthy"
cluster_ids.remove(healthy_id)

# Zombie: Highest Work_Check
remaining = grouped_means.loc[cluster_ids]
zombie_id = remaining['[SumScore_Work_Check]'].idxmax()
cluster_names[zombie_id] = "Zombie"
cluster_ids.remove(zombie_id)

# Burnout: The last one
burnout_id = cluster_ids[0]
cluster_names[burnout_id] = "High-Tech Burnout"

# 5. DIFFERENCE HUNTER (CHI TIM DIEM KHAC BIET - NORMALIZED)
print("\n" + "="*80)
print(f"{'DIFFERENCE HUNTER (THUAT TOAN TIM DIEM KHAC BIET - CHUAN HOA)':^80}")
print("   -> Da hieu chinh theo thang diem (Scales) cua tung bien.")
print("   -> Chi hien thi nhung khac biet > 10% so voi tong thang diem.")
print("="*80)

# 1. Calculate Data Ranges (Max - Min) for normalization
ranges = {}
for trait in feature_cols:
    val_min = df[trait].min()
    val_max = df[trait].max()
    ranges[trait] = val_max - val_min if (val_max - val_min) > 0 else 1.0 # Avoid div/0
    # print(f"DEBUG: {trait} Range: {val_min}-{val_max} (Size: {ranges[trait]})")

# 2. Find Distinct Traits based on Normalized Variance
normalized_variance = {}
for trait in feature_cols:
    values = grouped_means[trait]
    diff_raw = values.max() - values.min()
    diff_pct = diff_raw / ranges[trait]
    normalized_variance[trait] = diff_pct

# Filter: Keep if max difference across groups is > 10% of the scale
THRESHOLD_PCT = 0.10 
distinct_traits = {k: v for k, v in normalized_variance.items() if v > THRESHOLD_PCT}

print(f"\n[DISTINCT TRAITS] (Cac yeu to co su khac biet > {THRESHOLD_PCT*100}% thang do):")
print("-" * 80)

for c_id in [0, 1, 2]:
    name = cluster_names[c_id]
    print(f"\n>>> GROUP: {name.upper()}")
    
    this_mean = grouped_means.loc[c_id]
    other_mean = grouped_means.drop(c_id).mean()
    diff = this_mean - other_mean
    
    # Filter for distinct only
    relevant_traits = list(distinct_traits.keys())
    
    # Sort by Normalized Impact (Diff / Range)
    # We create a temp list to sort
    trait_impacts = []
    for trait in relevant_traits:
        norm_diff = diff[trait] / ranges[trait]
        trait_impacts.append((trait, norm_diff))
    
    # Sort descending by absolute normalized difference
    trait_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for trait, norm_diff in trait_impacts:
        val = this_mean[trait]
        raw_diff = diff[trait]
        avg_others = other_mean[trait]
        
        # Display Logic
        if norm_diff > 0:
            status = "HIGHEST / CAO HON"
        else:
            status = "LOWEST / THAP HON"
            
        print(f"  * {trait:<30}: {val:<5.2f} ({status:<18} | Diff: {norm_diff*100:+.1f}%)")

print("\n" + "="*80)
print("Analysis Completed.")
