import pandas as pd
import numpy as np
import sys
import os

# Redirect stdout to a file as well
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
sys.stdout = DualLogger(os.path.join(BASE_DIR, "outputs", "centroid_analysis_results.txt"))

print("--- SCALE-AWARE CENTROID ANALYSIS (UNSUPERVISED) ---")
print("Identifying distinctive features based on specific Likert scales.")

# 1. LOAD DATA
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found. Run clustering script first.")
    sys.exit(1)

try:
    df = pd.read_excel(input_file, sheet_name='Clustered_Users')
    print(f"Loaded {len(df)} records.")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# 2. DEFINE SCALES (Based on Research_from_data_set_2526.docx)
# Format: 'ColumnName': (Min, Max)
# Assumed Min=1 for most unless specified otherwise.
SCALE_MAP = {
    # 5-point Likert (Addiction, Obsession)
    '[SumScore_Work_Check]': (1, 5),
    '[SumScore_Sleep_Loss]': (1, 5),
    '[SumScore_Fatigue]': (1, 5),
    '[SumScore_Escapism]': (1, 5),
    '[SumScore_Control_Time]': (1, 5),
    '[SumScore_Obsess_Loop]': (1, 5),
    '[SumScore_Obsess_Debate]': (1, 5),
    '[SumScore_Obsess_Celeb]': (1, 5),
    
    # 4-point Scales (Frequency, Skills)
    '[SumScore_AI_Freq]': (1, 4),
    '[SumScore_Deepfake_Detect]': (1, 4),
    '[SumScore_Crowd_Pressure]': (1, 4),
    '[SumScore_Deep_Reading]': (1, 4), # Assumed based on Skill group
    '[SumScore_Source_Check]': (1, 4), # Assumed based on Skill group
    '[SumScore_Clickbait_Aware]': (1, 4), # Assumed based on Skill group
    
    # 3-point Scales (Trust, Reaction)
    '[SumScore_AI_Trust]': (1, 3),
    '[SumScore_FOMO_Reaction]': (1, 3),
}

feature_cols = list(SCALE_MAP.keys())

# Validate cols exist
missing = [c for c in feature_cols if c not in df.columns]
if missing:
    print(f"Warning: Columns in Scale Map not found in Data: {missing}")
    # Remove missing
    feature_cols = [c for c in feature_cols if c in df.columns]

# 3. CALCULATE CENTROIDS (MEANS)
cluster_means = df.groupby('Cluster_ID')[feature_cols].mean()
global_means = df[feature_cols].mean()

# 4. FIND DISTINCTIVE FEATURES (Scale-Aware Deviation)
print("\n" + "="*80)
print(f"{'DISTINCTIVE FEATURE ANALYSIS':^80}")
print("="*80)
print("Method: Comparing Cluster Centroid to Global Centroid.")
print("Key: (+/- Score) shows raw deviation. (% Range) shows impact relative to scale.")
print("Thresholds considered: >10% scale deviation or >0.5 raw score.")

counts = df['Cluster_ID'].value_counts().sort_index()

for cluster_id in counts.index:
    print(f"\n>>> CLUSTER {cluster_id} (n={counts[cluster_id]})")
    print("-" * 70)
    print(f"{'Feature':<30} | {'Scale':<5} | {'Cluster':<6} | {'Global':<6} | {'Diff':<6} | {'% Range'}")
    print("-" * 70)
    
    distinctions = []
    
    for col in feature_cols:
        c_mean = cluster_means.loc[cluster_id, col]
        g_mean = global_means[col]
        diff = c_mean - g_mean
        
        min_s, max_s = SCALE_MAP[col]
        scale_range = max_s - min_s
        pct_diff = (diff / scale_range) * 100
        
        # Store for sorting
        distinctions.append({
            'feature': col,
            'scale': f"{min_s}-{max_s}",
            'c_mean': c_mean,
            'g_mean': g_mean,
            'diff': diff,
            'pct_diff': pct_diff,
            'abs_pct': abs(pct_diff)
        })
    
    # Sort by magnitude of percentage difference (most distinctive first)
    distinctions.sort(key=lambda x: x['abs_pct'], reverse=True)
    
    # Display all features
    for item in distinctions:
        sign = "+" if item['diff'] > 0 else ""
        print(f"{item['feature']:<30} | {item['scale']:<5} | {item['c_mean']:.2f}   | {item['g_mean']:.2f}   | {sign}{item['diff']:.2f}   | {sign}{item['pct_diff']:.1f}%")

print("\nAnalysis Complete. Results saved to 'centroid_analysis_results.txt'.")
