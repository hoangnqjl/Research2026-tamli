import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 1. LOAD DATA
print("Loading data from Data.xlsx...")
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# 2. PREPARE VARIABLES (BLIND TEST - REMOVED ADDICTION & THINKING)
# Only using Health and Distraction metrics
model_data = pd.DataFrame()
model_data['Fatigue'] = df['[SumScore_Fatigue]']
model_data['SleepLoss'] = df['[SumScore_Sleep_Loss]']
model_data['Distraction'] = df['[SumScore_Work_Check]']

# Drop missing values
model_data = model_data.dropna()
print(f"Data ready for analysis (Blind Test). Samples: {len(model_data)}")

# 3. K-MEANS CLUSTERING (K=3)
# Normalize data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# Run KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init=20)
clusters = kmeans.fit_predict(data_scaled)
model_data['Cluster'] = clusters

# 4. CLUSTER IDENTIFICATION
means = model_data.groupby('Cluster').mean()
print("\nCluster Profiles (Average Scores):")
print(means)

# NAMING LOGIC (Without Addiction/Thinking)
# 1. Healthy: Lowest Fatigue
# 2. Zombie: Highest Distraction (Work_Check)
# 3. High-Tech Burnout: The remaining one (High Fatigue/Sleep but Moderate Distraction)

cluster_ids = means.index.tolist()
cluster_map = {}

# Find Healthy
healthy_id = means['Fatigue'].idxmin()
cluster_map[healthy_id] = "C: Healthy"
cluster_ids.remove(healthy_id)

# Find Zombie (Max Distraction among remaining)
remaining = means.loc[cluster_ids]
zombie_id = remaining['Distraction'].idxmax()
cluster_map[zombie_id] = "A: Zombie"
cluster_ids.remove(zombie_id)

# Find Burnout (Last one)
burnout_id = cluster_ids[0]
cluster_map[burnout_id] = "B: High-Tech Burnout"

model_data['Label'] = model_data['Cluster'].map(cluster_map)
print(f"\nMapped Clusters: {cluster_map}")

# 5. VISUALIZATION (BLIND TEST Version)
plot_df = model_data.groupby('Label').mean().reset_index()
counts = model_data['Label'].value_counts()

# Add counts to labels
plot_df['Label_Count'] = plot_df['Label'].apply(lambda x: f"{x} (n={counts[x]})")

# MinMax Scale for visualization (1-10)
plot_scaler = MinMaxScaler(feature_range=(1, 10))
cols_to_plot = ['Fatigue', 'SleepLoss', 'Distraction']
plot_df[cols_to_plot] = plot_scaler.fit_transform(plot_df[cols_to_plot])

# Melt for bar chart
df_melt = plot_df.melt(id_vars="Label_Count", value_vars=cols_to_plot, var_name="Metric", value_name="Relative Score (1-10)")

# Translate Metrics
metric_map = {
    'Fatigue': 'Kiệt sức (Fatigue)',
    'SleepLoss': 'Mất ngủ (Sleep Loss)',
    'Distraction': 'Xao nhãng (Distraction)'
}
df_melt['Metric'] = df_melt['Metric'].map(metric_map)

plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

# Define Palette safely
# Check which labels exist in plot_df to match colors
unique_labels = sorted(plot_df['Label_Count'].unique())
# A: Zombie -> Red
# B: Burnout -> Orange
# C: Healthy -> Green
palette = []
for label in unique_labels:
    if "Zombie" in label:
        palette.append("#e74c3c") # Red
    elif "Burnout" in label:
        palette.append("#f39c12") # Orange
    elif "Healthy" in label:
        palette.append("#2ecc71") # Green
    else:
        palette.append("gray")

chart = sns.barplot(data=df_melt, x="Metric", y="Relative Score (1-10)", hue="Label_Count", palette=palette)

plt.title("Phân loại 3 nhóm (Blind Test - Chỉ dùng Chỉ số Sức khỏe)", fontsize=16, fontweight='bold')
plt.ylabel("Mức độ (Quy đổi 1-10)", fontsize=13)
plt.xlabel("Các chỉ số sức khỏe & hành vi", fontsize=13)
plt.legend(title="Nhóm người dùng", fontsize=11)
plt.tight_layout()

# Save
output_file = 'problem1_analysis_vi.png'
plt.savefig(output_file, dpi=300)
print(f"\nBieu do da duoc luu: {output_file}")

# 6. SIMPLE TEXT SUMMARY
print("\n--- SUMMARY OF FINDINGS ---")
for label in ['A: Zombie', 'B: High-Tech Burnout', 'C: Healthy']:
    # Find matching key in cluster_map
    original_id = [k for k, v in cluster_map.items() if label in v][0]
    row = means.loc[original_id]
    
    print(f"[{label}]")
    print(f"  - Fatigue  : {row['Fatigue']:.2f}")
    print(f"  - SleepLoss: {row['SleepLoss']:.2f}")
    print(f"  - Distraction: {row['Distraction']:.2f}")
    print("")
