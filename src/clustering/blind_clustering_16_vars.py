import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
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

        self.terminal.flush()
        self.log.flush()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = DualLogger(os.path.join(BASE_DIR, "outputs", "analysis_results.txt"))

print("--- BLIND CLUSTERING & ANALYSIS (16 VARIABLES) ---")
# ... (rest of the code runs as normal and prints to both)


# 1. LOAD DATA
# Assuming script is run from project root, or we need to find Data.xlsx
data_path = os.path.join(BASE_DIR, 'data', 'raw', 'Data.xlsx')
if not os.path.exists(data_path):
    print(f"Error: Data.xlsx not found at '{data_path}'")
    sys.exit(1)

try:
    df = pd.read_excel(data_path, sheet_name='GenZNCKH1', header=2)
    print(f"Loaded {data_path} successfully.")
except Exception as e:
    print(f"Error loading Data.xlsx: {e}")
    sys.exit(1)

# 2. FEATURE SELECTION (16 VARIABLES)
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

# Check if columns exist
missing_cols = [col for col in feature_cols if col not in df.columns]
if missing_cols:
    print(f"Error: Missing columns: {missing_cols}")
    sys.exit(1)

# 3. PREPROCESSING
df_clean = df.dropna(subset=feature_cols).copy()
X = df_clean[feature_cols]

# Scale Data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. RUN CLUSTERING (K=3)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
df_clean['Cluster_ID'] = kmeans.fit_predict(X_scaled)

# 5. ANALYSIS & PROFILING (Z-Score Method)
# Scientific Basis:
# - Z-Score = (ClusterMean - GlobalMean) / GlobalStd
# - |Z| > 0.2: Small difference
# - |Z| > 0.5: Medium difference (Visible characteristic)
# - |Z| > 0.8: Large difference (Strong differentiating feature)

# Raw Means
cluster_means = df_clean.groupby('Cluster_ID')[feature_cols].mean().round(2)
# Global Mean
global_mean = df_clean[feature_cols].mean().round(2)

# Z-Scores
df_z = pd.DataFrame(X_scaled, columns=feature_cols, index=df_clean.index)
df_z['Cluster_ID'] = df_clean['Cluster_ID']
cluster_z_scores = df_z.groupby('Cluster_ID').mean().round(2)

# Cluster Counts/Portion
counts = df_clean['Cluster_ID'].value_counts().sort_index()
proportions = (counts / len(df_clean) * 100).round(1)

# --- PRINT REPORT ---
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\n" + "="*80)
print(f"{'CLUSTERING RESULT SUMMARY (K=3)':^80}")
print("="*80)
print(f"Total Samples: {len(df_clean)}")
print("-" * 40)
print(f"{'Cluster ID':<15} | {'Count':<10} | {'Percentage':<10}")
print("-" * 40)
for i in counts.index:
    print(f"Cluster {i:<7} | {counts[i]:<10} | {proportions[i]}%")

print("\n" + "="*80)
print(f"{'DISTINCTIVE FEATURES (Z-Score Analysis)':^80}")
print("="*80)
print("Note: Features with |Z-Score| > 0.5 are considered 'Distinctive'.")
print("      (+) means Higher than Average, (-) means Lower than Average.")

threshold = 0.5 

for cluster_id in cluster_z_scores.index:
    print(f"\n>>> CLUSTER {cluster_id} (n={counts[cluster_id]}, {proportions[cluster_id]}%)")
    print("-" * 60)
    
    # Get Z-scores for this cluster
    z_row = cluster_z_scores.loc[cluster_id]
    
    # Filter for significant features
    # Strong positive features (Highest first)
    pos_features = z_row[z_row > threshold].sort_values(ascending=False)
    # Strong negative features (Lowest first)
    neg_features = z_row[z_row < -threshold].sort_values(ascending=True)
    
    if pos_features.empty and neg_features.empty:
        print("  (No strongly distinctive features found with |Z| > 0.5)")
        print("  Checking smaller differences (> 0.2)...")
        small_diff = z_row[z_row.abs() > 0.2].sort_values(ascending=False)
        print(small_diff if not small_diff.empty else "  (Average Group)")
    else:
        if not pos_features.empty:
            print(f"  [+] PROMINENT (Cao hơn TB):")
            for feat, score in pos_features.items():
                print(f"      - {feat:<30}: Z = +{score}")
        
        if not neg_features.empty:
            print(f"\n  [-] LACKING (Thấp hơn TB):")
            for feat, score in neg_features.items():
                print(f"      - {feat:<30}: Z = {score}")

print("\n" + "="*80)
print(f"{'DETAILED TABLES':^80}")
print("="*80)
print("\n--- GLOBAL MEANS (Nền) ---")
print(global_mean)

print("\n--- RAW CLUSTER MEANS (Giá trị thực) ---")
print(cluster_means.T)

print("\n--- Z-SCORES (Độ lệch chuẩn) ---")
print(cluster_z_scores.T)

# 6. EXPORT TO EXCEL
output_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
print(f"\n[INFO] Extracting full report to {output_file}...")
try:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        export_cols = feature_cols + ['Cluster_ID']
        df_clean[export_cols].to_excel(writer, sheet_name='Clustered_Users', index=False)
        
        writer.sheets['Analysis'] = writer.book.create_sheet('Analysis')
        sheet = writer.book['Analysis']
        
        row_cursor = 1
        sheet.cell(row=row_cursor, column=1, value="DISTINCTIVE FEATURES ANALYSIS")
        row_cursor += 2
        
        # Write Z-Scores
        sheet.cell(row=row_cursor, column=1, value="Z-Scores (Std Deviation from Global Mean)")
        cluster_z_scores.T.to_excel(writer, sheet_name='Analysis', startrow=row_cursor+1)
        
        # Write Raw Means next to it
        sheet.cell(row=row_cursor, column=6, value="Raw Cluster Means")
        cluster_means.T.to_excel(writer, sheet_name='Analysis', startrow=row_cursor+1, startcol=5)
        
    print("-> Export successful!")

except Exception as e:
    print(f"Error exporting Excel: {e}")

print("Analysis Complete.")
