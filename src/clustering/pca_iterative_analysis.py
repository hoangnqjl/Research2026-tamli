import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import scipy.stats as stats
import sys
import os

# Setup Logging
class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = DualLogger(os.path.join(BASE_DIR, "outputs", "pca_analysis_log.txt"))

print("--- ITERATIVE PCA ANALYSIS (NOISE EVALUATION) ---")
print("Objective: Visualize cluster separability (noise) as we increase features from 7 to 16.")

# 1. LOAD DATA
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    sys.exit(1)

df = pd.read_excel(input_file, sheet_name='Clustered_Users')
print(f"Loaded {len(df)} samples.")

# 2. DEFINE ALL 16 VARIABLES
all_features = [
    '[SumScore_Work_Check]', '[SumScore_Source_Check]', '[SumScore_Sleep_Loss]',
    '[SumScore_Obsess_Loop]', '[SumScore_Obsess_Debate]', '[SumScore_Obsess_Celeb]',
    '[SumScore_FOMO_Reaction]', '[SumScore_Fatigue]', '[SumScore_Escapism]',
    '[SumScore_Deepfake_Detect]', '[SumScore_Deep_Reading]', '[SumScore_Crowd_Pressure]',
    '[SumScore_Control_Time]', '[SumScore_Clickbait_Aware]', '[SumScore_AI_Trust]',
    '[SumScore_AI_Freq]'
]

# 3. RANK FEATURES BY IMPORTANCE (ANOVA F-STAT)
# We want to add the most "meaningful" features first, so we reproduce the ranking logic.
print("\n[Ranking Features by F-Statistic...]")
f_scores = []
for col in all_features:
    groups = [df[df['Cluster_ID'] == i][col] for i in range(3)]
    f_stat, _ = stats.f_oneway(*groups)
    f_scores.append((col, f_stat))

# Sort desc
f_scores.sort(key=lambda x: x[1], reverse=True)
ranked_features = [x[0] for x in f_scores]

print("Feature Order:")
for i, f in enumerate(ranked_features):
    print(f"{i+1}. {f} (F={f_scores[i][1]:.1f})")

# 4. ITERATIVE PCA LOOP (7 to 16)
output_dir = os.path.join(BASE_DIR, "outputs")

print("\n[Starting Iterative Analysis]")
for k in range(1, 17):
    print(f"\n>>> Analyzing with Top {k} Features...")
    
    current_features = ranked_features[:k]
    
    # Preprocess
    X = df[current_features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Configure PCA based on k
    if k == 1:
        n_comp = 1
        pca = PCA(n_components=n_comp)
        components = pca.fit_transform(X_scaled)
        
        # For visualization, add random jitter to Y-axis
        jitter = np.random.uniform(-0.1, 0.1, size=components.shape)
        plot_data = np.hstack([components, jitter])
        
        explained_var = pca.explained_variance_ratio_
        total_var = explained_var[0] * 100
        pc1_label = f'PC1 ({total_var:.1f}%)'
        pc2_label = 'Jitter (Visualization only)'
        
    else:
        n_comp = 2
        pca = PCA(n_components=n_comp)
        components = pca.fit_transform(X_scaled)
        plot_data = components
        
        explained_var = pca.explained_variance_ratio_
        total_var = sum(explained_var) * 100
        pc1_label = f'PC1 ({explained_var[0]*100:.1f}%)'
        pc2_label = f'PC2 ({explained_var[1]*100:.1f}%)'
    
    # Silhouette Score
    sil_score = silhouette_score(components, df['Cluster_ID'])
    
    print(f"   Explained Variance: {total_var:.2f}%")
    print(f"   Silhouette Score: {sil_score:.3f}")
    
    # Plot
    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        x=plot_data[:, 0], y=plot_data[:, 1],
        hue=df['Cluster_ID'], palette='viridis', style=df['Cluster_ID'],
        s=100, alpha=0.7
    )
    
    plt.title(f'PCA Visualization - Top {k} Features\nExplained Variance: {total_var:.1f}% | Silhouette: {sil_score:.3f}', fontsize=14)
    plt.xlabel(pc1_label)
    plt.ylabel(pc2_label)
    plt.legend(title='Cluster ID')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Save
    out_name = f"pca_noise_analysis_{k}_features.png"
    out_path = os.path.join(output_dir, out_name)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"   -> Saved: {out_name}")

print("\nAnalysis Complete. Check 'outputs/' for images.")
