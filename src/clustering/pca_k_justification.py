
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
import sys

# ==========================================
# 0. SETUP
# ==========================================
print("--- PCA ANALYSIS FOR K=3 JUSTIFICATION ---")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 1. LOAD DATA
# ==========================================
data_path = os.path.join(BASE_DIR, 'data', 'raw', 'Data.xlsx')
try:
    df = pd.read_excel(data_path, sheet_name='GenZNCKH1', header=2)
    print(f"Loaded Data.xlsx successfully. Shape: {df.shape}")
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    sys.exit(1)

# ==========================================
# 2. FEATURE SELECTION (16 VARIABLES)
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
]

# Check columns
missing = [c for c in feature_cols if c not in df.columns]
if missing:
    print(f"Missing columns: {missing}")
    sys.exit(1)

model_data = df[feature_cols].dropna()
print(f"Data for PCA: {model_data.shape}")

# Standardize
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# ==========================================
# 3. PCA: SCREE PLOT (Justification for dimensionality)
# ==========================================
pca_full = PCA()
pca_full.fit(data_scaled)

explained_variance = pca_full.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

plt.figure(figsize=(10, 6))
x_axis = range(1, len(explained_variance) + 1)
plt.bar(x_axis, explained_variance, alpha=0.5, align='center', label='Individual explained variance')
plt.step(x_axis, cumulative_variance, where='mid', label='Cumulative explained variance')
plt.ylabel('Explained Variance Ratio')
plt.xlabel('Principal Component Index')
plt.title('PCA Scree Plot')
plt.xticks(x_axis)
plt.legend(loc='best')
plt.grid(True)

# Highlight PC3
plt.axvline(x=3, color='r', linestyle='--', label='k=3 Cutoff')
plt.text(3.1, 0.5, f'PC1-3 Explains: {cumulative_variance[2]*100:.1f}%', color='red')

plt.savefig(os.path.join(OUTPUT_DIR, 'pca_scree_plot.png'), dpi=300)
print("-> Saved pca_scree_plot.png")

# ==========================================
# 4. RUN CLUSTERING (K=3) TO COLOR THE PCA PLOT
# ==========================================
# We use the clusters to show they separate well in PCA space
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
clusters = kmeans.fit_predict(data_scaled)

# ==========================================
# 5. PCA 3D VISUALIZATION (Visual "Reasoning")
# ==========================================
pca_3 = PCA(n_components=3)
components = pca_3.fit_transform(data_scaled)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Color map
colors = ['#FF9999', '#66B2FF', '#99FF99'] # Soft red, blue, green
# Map clusters to colors
c_map = [colors[c] for c in clusters]

scatter = ax.scatter(components[:, 0], components[:, 1], components[:, 2], 
                     c=c_map, s=40, alpha=0.6, edgecolors='w')

ax.set_xlabel('Principal Component 1')
ax.set_ylabel('Principal Component 2')
ax.set_zlabel('Principal Component 3')
ax.set_title('3D PCA Visualization of k=3 Clusters', fontsize=15)

# Create a custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[0], label='Cluster 0', markersize=10),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[1], label='Cluster 1', markersize=10),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[2], label='Cluster 2', markersize=10)
]
ax.legend(handles=legend_elements, loc='upper right')

plt.savefig(os.path.join(OUTPUT_DIR, 'pca_3d_clusters.png'), dpi=300)
print("-> Saved pca_3d_clusters.png")

# ==========================================
# 6. PCA 2D VISUALIZATION (Simpler view)
# ==========================================
plt.figure(figsize=(10, 8))
plt.scatter(components[:, 0], components[:, 1], c=c_map, s=50, alpha=0.6, edgecolors='none')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('2D PCA Visualization (PC1 vs PC2)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(handles=legend_elements, loc='upper right')

plt.savefig(os.path.join(OUTPUT_DIR, 'pca_2d_clusters.png'), dpi=300)
print("-> Saved pca_2d_clusters.png")

print("\nAnalysis Complete.")
