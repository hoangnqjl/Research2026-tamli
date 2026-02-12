import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import pi
import sys
import os

print("--- RADAR CHART GENERATOR (CENTROIDS ANALYSIS) ---")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. LOAD DATA
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    sys.exit(1)

try:
    df = pd.read_excel(input_file, sheet_name='Clustered_Users')
    print("Loaded data successfully.")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# 2. DEFINE SCALES & VARIABLES
# Must match the scientific analysis
SCALE_MAP = {
    # 5-point
    '[SumScore_Work_Check]': (1, 5),
    '[SumScore_Sleep_Loss]': (1, 5),
    '[SumScore_Fatigue]': (1, 5),
    '[SumScore_Escapism]': (1, 5),
    '[SumScore_Control_Time]': (1, 5),
    '[SumScore_Obsess_Loop]': (1, 5),
    '[SumScore_Obsess_Debate]': (1, 5),
    '[SumScore_Obsess_Celeb]': (1, 5),
    
    # 4-point
    '[SumScore_AI_Freq]': (1, 4),
    '[SumScore_Deepfake_Detect]': (1, 4),
    '[SumScore_Crowd_Pressure]': (1, 4),
    '[SumScore_Deep_Reading]': (1, 4),
    '[SumScore_Source_Check]': (1, 4),
    '[SumScore_Clickbait_Aware]': (1, 4),
    
    # 3-point
    '[SumScore_AI_Trust]': (1, 3),
    '[SumScore_FOMO_Reaction]': (1, 3),
}

# Simplify Labels for Chart (Clean, no scales)
LABEL_MAP = {
    '[SumScore_FOMO_Reaction]': 'FOMO (Ghen tị)',
    '[SumScore_Obsess_Debate]': 'Tranh luận',
    '[SumScore_AI_Trust]': 'Tin AI',
    '[SumScore_Crowd_Pressure]': 'Áp lực đám đông',
    '[SumScore_Work_Check]': 'Check việc',
    '[SumScore_Sleep_Loss]': 'Mất ngủ',
    '[SumScore_Control_Time]': 'Mất kiểm soát',
    '[SumScore_Escapism]': 'Trốn tránh',
}

# ONLY SELECT THE TOP 8 DISTINCTIVE FEATURES (Based on ANOVA & Centroid Analysis)
# This removes noise from variables that are similar across all groups (like Source Check, Reading, etc.)
feature_cols = [
    '[SumScore_FOMO_Reaction]',
    '[SumScore_Obsess_Debate]',
    '[SumScore_AI_Trust]',
    '[SumScore_Crowd_Pressure]',
    '[SumScore_Work_Check]',
    '[SumScore_Sleep_Loss]',
    '[SumScore_Control_Time]',
    '[SumScore_Escapism]'
]


# 3. CALCULATE NORMALIZED MEANS (0-100%)
# Formula: (Mean - Min) / (Max - Min)
df_means = df.groupby('Cluster_ID')[feature_cols].mean()

# Normalize
df_norm = pd.DataFrame(index=df_means.index, columns=feature_cols)

for col in feature_cols:
    min_val, max_val = SCALE_MAP[col]
    df_norm[col] = (df_means[col] - min_val) / (max_val - min_val) 
    # Clip to 0-1 just in case
    df_norm[col] = df_norm[col].clip(0, 1)

# 4. PLOTTING
def make_spider(df_norm, title, output_name):
    categories = [LABEL_MAP[c] for c in feature_cols]
    N = len(categories)
    
    # Angles
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    plt.figure(figsize=(12, 12))
    ax = plt.subplot(111, polar=True)
    
    # Start from top
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    # Draw x-labels
    plt.xticks(angles[:-1], categories, color='black', size=11)
    
    # Draw y-labels
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.5, 0.75, 1.0], ["25%","50%","75%","100%"], color="grey", size=8)
    plt.ylim(0, 1.05)
    
    # Define Styles
    styles = {
        0: {'color': 'green', 'label': 'Cluster 0', 'style': 'solid'},
        1: {'color': 'blue', 'label': 'Cluster 1', 'style': 'solid'},
        2: {'color': 'red', 'label': 'Cluster 2', 'style': 'dashed'}
    }
    
    # Plot each cluster
    for cluster_id in df_norm.index:
        values = df_norm.loc[cluster_id].values.flatten().tolist()
        values += values[:1] # Close loop
        
        s = styles.get(cluster_id, {'color': 'black', 'label': f'Cluster {cluster_id}', 'style': 'solid'})
        
        ax.plot(angles, values, linewidth=2, linestyle=s['style'], label=s['label'], color=s['color'])
        ax.fill(angles, values, s['color'], alpha=0.05)
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(title, size=16, color='black', y=1.05)
    
    plt.tight_layout()
    plt.savefig(output_name, dpi=300)
    print(f"-> Saved chart to {output_name}")

make_spider(df_norm, "Cluster Centroids Analysis (Normalized Patterns)", os.path.join(BASE_DIR, "outputs", "radar_chart_centroids_final.png"))
