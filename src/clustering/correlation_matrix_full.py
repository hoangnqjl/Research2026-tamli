import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

print("--- FULL CORRELATION MATRIX ANALYSIS ---")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. LOAD DATA
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    sys.exit(1)

try:
    df = pd.read_excel(input_file, sheet_name='Clustered_Users')
    print(f"Loaded {len(df)} records.")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# 2. DEFINE VARIABLES & LABELS
# Include all 16 relevant variables
SCALE_MAP = {
    '[SumScore_Work_Check]': 'Compulsive Checking',
    '[SumScore_Sleep_Loss]': 'Sleep Loss',
    '[SumScore_Fatigue]': 'Fatigue',
    '[SumScore_Escapism]': 'Escapism',
    '[SumScore_Control_Time]': 'Loss of Control',
    '[SumScore_Obsess_Loop]': 'Obsessive Looping',
    '[SumScore_Obsess_Debate]': 'Obsessive Debate',
    '[SumScore_Obsess_Celeb]': 'Celebrity Obsession',
    
    '[SumScore_AI_Freq]': 'AI Frequency',
    '[SumScore_Deepfake_Detect]': 'Deepfake Detection',
    '[SumScore_Crowd_Pressure]': 'Crowd Pressure',
    '[SumScore_Deep_Reading]': 'Deep Reading',
    '[SumScore_Source_Check]': 'Source Checking',
    '[SumScore_Clickbait_Aware]': 'Clickbait Awareness',
    
    '[SumScore_AI_Trust]': 'AI Trust',
    '[SumScore_FOMO_Reaction]': 'FOMO Reaction',
}

feature_cols = list(SCALE_MAP.keys())
labels = [SCALE_MAP[c] for c in feature_cols]

# 3. COMPUTE CORRELATION
corr_matrix = df[feature_cols].corr(method='pearson')

# Rename columns/index for plotting
corr_matrix.columns = labels
corr_matrix.index = labels

# 4. PLOT HEATMAP
plt.figure(figsize=(14, 12))
sns.set_context("notebook", font_scale=1.0)

# Mask upper triangle (optional, but makes it cleaner)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

ax = sns.heatmap(
    corr_matrix, 
    annot=True, 
    fmt=".2f", 
    cmap="RdBu_r", # Red = Negative, Blue = Positive
    vmax=1, 
    vmin=-1,
    center=0,
    square=True,
    linewidths=.5,
    cbar_kws={"shrink": .8, "label": "Pearson Correlation Coefficient"}
)

plt.title("Correlation Matrix of All Behavioral Features", fontsize=16, pad=20, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

plt.tight_layout()
output_path = os.path.join(BASE_DIR, 'outputs', 'correlation_matrix_full.png')
plt.savefig(output_path, dpi=300)
print(f"Heatmap saved to {output_path}")
