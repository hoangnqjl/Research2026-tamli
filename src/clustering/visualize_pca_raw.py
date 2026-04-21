
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
import sys

# ==========================================
# 0. SETUP
# ==========================================
print("--- RAW PCA VISUALIZATION (PRE-CLUSTERING) ---")
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

model_data = df[feature_cols].dropna()
print(f"Cleaned data for PCA: {model_data.shape}")

# Standardize
scaler = StandardScaler()
data_scaled = scaler.fit_transform(model_data)

# ==========================================
# 3. PCA PROCESSING
# ==========================================
pca = PCA()
pca.fit(data_scaled)
components = pca.transform(data_scaled)

# ==========================================
# 4. VISUALIZATION 1: SCREE PLOT
# ==========================================
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

plt.figure(figsize=(10, 6))
plt.bar(range(1, 17), explained_variance, alpha=0.5, align='center', label='Individual Variance')
plt.step(range(1, 17), cumulative_variance, where='mid', label='Cumulative Variance')
plt.ylabel('Explained Variance Ratio')
plt.xlabel('Principal Component Index')
plt.title('PCA Scree Plot (Raw Data)', fontsize=14)
plt.axhline(y=0.7, color='r', linestyle='--', label='70% Threshold')
plt.legend(loc='best')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(range(1, 17))

scree_path = os.path.join(OUTPUT_DIR, 'pca_raw_scree.png')
plt.savefig(scree_path, dpi=300)
print(f"-> Saved {scree_path}")
plt.close()

# ==========================================
# 5. VISUALIZATION 2: 2D RAW DISTRIBUTION
# ==========================================
plt.figure(figsize=(10, 8))
plt.scatter(components[:, 0], components[:, 1], alpha=0.5, c='darkblue', edgecolors='w', s=50)
plt.xlabel(f'PC1 ({explained_variance[0]*100:.1f}%)')
plt.ylabel(f'PC2 ({explained_variance[1]*100:.1f}%)')
plt.title('Raw PCA Distribution (PC1 vs PC2)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)

dist_path = os.path.join(OUTPUT_DIR, 'pca_raw_2d.png')
plt.savefig(dist_path, dpi=300)
print(f"-> Saved {dist_path}")
plt.close()

# ==========================================
# 6. VISUALIZATION 3: FEATURE LOADINGS (HEATMAP)
# ==========================================
# Look at the first 3 PCs
loadings = pd.DataFrame(
    pca.components_[:3].T, 
    columns=['PC1', 'PC2', 'PC3'], 
    index=feature_cols
)

plt.figure(figsize=(12, 10))
sns.heatmap(loadings, annot=True, cmap='RdBu', center=0, cbar_kws={'label': 'Loading Score'})
plt.title('Feature Loadings for first 3 Principal Components', fontsize=14)
plt.tight_layout()

heat_path = os.path.join(OUTPUT_DIR, 'pca_raw_loadings.png')
plt.savefig(heat_path, dpi=300)
print(f"-> Saved {heat_path}")
plt.close()

print("\nAnalysis Complete.")
