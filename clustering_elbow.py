import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.stats import f_oneway

# ==========================================
# 1. SETUP & DATA LOAD
# ==========================================
print("--- [MASTER SCRIPT] PHAN TICH PHAN CUM GEN Z (ALL-IN-ONE) ---")
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
    print("Included Data.xlsx successfully.")
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    exit()

# ==========================================
# 2. FEATURE SELECTION (17 VARIABLES)
# ==========================================
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

# Check columns
missing = [c for c in feature_cols if c not in df.columns]
if missing:
    print(f"Missing columns: {missing}")
    exit()

model_data = df[feature_cols].dropna()
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# ==========================================
# 3. ELBOW METHOD (VE BIEU DO)
# ==========================================
wcss = []
K_range = range(1, 11)
print("\n[STEP 1] Calculating Elbow Curve...")
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
    kmeans.fit(data_scaled)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(K_range, wcss, marker='o', linestyle='--', color='b')
plt.title('Phuong phap Elbow (Tat ca thuoc tinh diem so)', fontsize=14)
plt.xlabel('So luong cum (k)', fontsize=12)
plt.ylabel('WCSS', fontsize=12)
plt.xticks(K_range)
plt.grid(True)
plt.annotate('Elbow Point (k=3)', xy=(3, wcss[2]), xytext=(4, wcss[2]+500),
             arrowprops=dict(facecolor='red', shrink=0.05))
plt.savefig('elbow_diagram.png', dpi=300)
print("-> Saved Elbow Diagram to: elbow_diagram.png")

# ==========================================
# 4. RUN CLUSTERING (K=3)
# ==========================================
print("\n[STEP 2] Running K-Means Clustering (k=3)...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
clusters = kmeans.fit_predict(data_scaled)

# ==========================================
# 5. NAMING LOGIC
# ==========================================
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

# Map to DF
df['Cluster_Group'] = np.nan
df.loc[model_data.index, 'Cluster_Group'] = clusters
df['Cluster_Name'] = df['Cluster_Group'].map(cluster_names)

# Export Data
output_csv = 'clustered_users_final.csv'
export_cols = feature_cols + ['Cluster_Group', 'Cluster_Name']
df[export_cols].to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"-> Saved Clustered Data to: {output_csv}")

# ==========================================
# 6. CHARACTERISTICS REPORT (TOP 3 TRAITS)
# ==========================================
print("\n" + "="*60)
print(f"{'CLUSTER PROFILE REPORT (DAC DIEM CUM)':^60}")
print("="*60)

for c_id in [0, 1, 2]:
    name = cluster_names.get(c_id, "Unknown")
    
    # Calculate Distinctions
    this_mean = grouped_means.loc[c_id]
    other_mean = grouped_means.drop(c_id).mean()
    diff = this_mean - other_mean
    sorted_diff = diff.abs().sort_values(ascending=False)
    top_3 = sorted_diff.head(3).index.tolist()
    
    print(f"\n>>> GROUP: {name.upper()}")
    for i, trait in enumerate(top_3, 1):
        actual = this_mean[trait]
        others = other_mean[trait]
        status = "HIGHEST" if diff[trait] > 0 else "LOWEST"
        
        print(f"   {i}. {trait}")
        print(f"      - {status} vs others (Val: {actual:.2f} | Others: {others:.2f})")

# ==========================================
# 7. SUMMARY STATISTICS (SO LUONG)
# ==========================================
print("\n" + "="*60)
print(f"{'SUMMARY STATISTICS (THONG KE SO LUONG)':^60}")
print("="*60)

counts = df['Cluster_Name'].value_counts()
total = len(model_data)

print(f"{'Cluster Name':<25} | {'Count':<10} | {'Percentage':<10}")
print("-" * 50)

for name in ["High-Tech Burnout", "Healthy", "Zombie"]:
    count = counts.get(name, 0)
    pct = (count / total) * 100
    print(f"{name:<25} | {count:<10} | {pct:.1f}%")

print("-" * 50)
print(f"{'TOTAL':<25} | {total:<10} | 100%")
print("="*60)
print("Analysis Complete.")
