
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# ==========================================
# 0. SETUP
# ==========================================
print("--- VISUALIZE CENTROID DEVIATION (SHARED Y-AXIS) ---")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 1. LOAD DATA
# ==========================================
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')
if not os.path.exists(input_file):
    csv_file = os.path.join(BASE_DIR, 'data', 'processed', 'clustered_users_final.csv')
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        if 'Cluster_Group' in df.columns and 'Cluster_ID' not in df.columns:
            df.rename(columns={'Cluster_Group': 'Cluster_ID'}, inplace=True)
    else:
        sys.exit(1)
else:
    try:
        df = pd.read_excel(input_file, sheet_name='Clustered_Users')
    except Exception:
        sys.exit(1)

if 'Cluster_ID' not in df.columns and 'Cluster_Group' in df.columns:
    df['Cluster_ID'] = df['Cluster_Group']

if 'Cluster_Name' in df.columns:
    cluster_names_map = df[['Cluster_ID', 'Cluster_Name']].drop_duplicates().set_index('Cluster_ID')['Cluster_Name'].to_dict()
else:
    cluster_names_map = {}

# ==========================================
# 2. DEFINE SCALES & MAPPING (13 FEATURES)
# ==========================================
# Scale Map (Min, Max)
SCALE_MAP = {
    '[SumScore_Work_Check]': (1, 5),
    '[SumScore_Sleep_Loss]': (1, 5),
    '[SumScore_Fatigue]': (1, 5),
    '[SumScore_Escapism]': (1, 5),
    '[SumScore_Control_Time]': (1, 5),
    '[SumScore_Obsess_Loop]': (1, 5),
    '[SumScore_Obsess_Debate]': (1, 5),
    '[SumScore_Obsess_Celeb]': (1, 5),
    '[SumScore_FOMO_Reaction]': (1, 3),
    '[SumScore_Deepfake_Detect]': (1, 4),
    '[SumScore_Crowd_Pressure]': (1, 4),
    '[SumScore_AI_Trust]': (1, 3),
    '[SumScore_AI_Freq]': (1, 4),
}

# Number Map (Based on User Table)
NUMBER_MAP = {
    '[SumScore_Work_Check]': 1,
    'Label_Work_Check': 'Addict Work Check',
    
    '[SumScore_Source_Check]': 2, # Excluded
    
    '[SumScore_Sleep_Loss]': 3,
    'Label_Sleep_Loss': 'Sleep Loss',
    
    '[SumScore_Obsess_Loop]': 4,
    'Label_Obsess_Loop': 'Brainrot Loop',
    
    '[SumScore_Obsess_Debate]': 5,
    'Label_Obsess_Debate': 'Obsessive Debate',
    
    '[SumScore_Obsess_Celeb]': 6,
    'Label_Obsess_Celeb': 'Celeb Obsession',
    
    '[SumScore_FOMO_Reaction]': 7,
    'Label_FOMO_Reaction': 'FOMO Resilience',
    
    '[SumScore_Fatigue]': 8,
    'Label_Fatigue': 'Digital Fatigue',
    
    '[SumScore_Escapism]': 9,
    'Label_Escapism': 'Escapism',
    
    '[SumScore_Deepfake_Detect]': 10,
    'Label_Deepfake_Detect': 'Deepfake Detect',
    
    '[SumScore_Deep_Reading]': 11, # Excluded
    
    '[SumScore_Crowd_Pressure]': 12,
    'Label_Crowd_Pressure': 'Crowd Pressure',
    
    '[SumScore_Control_Time]': 13,
    'Label_Control_Time': 'Time Control',
    
    '[SumScore_Clickbait_Aware]': 14, # Excluded
    
    '[SumScore_AI_Trust]': 15,
    'Label_AI_Trust': 'AI Thinking',
    
    '[SumScore_AI_Freq]': 16,
    'Label_AI_Freq': 'AI Frequency',
}

feature_cols = [c for c in SCALE_MAP.keys() if c in df.columns]

# ==========================================
# 3. STATISTICS & PREP
# ==========================================
cluster_means = df.groupby('Cluster_ID')[feature_cols].mean()
global_means = df[feature_cols].mean()

data_for_plot = []

for cluster_id in cluster_means.index:
    c_name = cluster_names_map.get(cluster_id, f"Cluster {cluster_id}")
    
    for col in feature_cols:
        c_mean = cluster_means.loc[cluster_id, col]
        g_mean = global_means[col]
        diff = c_mean - g_mean
        min_s, max_s = SCALE_MAP.get(col, (1, 5))
        scale_range = max_s - min_s
        pct_diff = (diff / scale_range) * 100
        
        # Create Label "No. Name"
        num = NUMBER_MAP[col]
        clean_name = NUMBER_MAP.get(f"Label_{col[10:-1]}", col) # rudimentary parsing
        # better manual mapping
        if col == '[SumScore_Work_Check]': clean_name = 'Addict Work Check'
        if col == '[SumScore_Sleep_Loss]': clean_name = 'Sleep Loss'
        if col == '[SumScore_Fatigue]': clean_name = 'Digital Fatigue'
        if col == '[SumScore_Escapism]': clean_name = 'Escapism'
        if col == '[SumScore_Control_Time]': clean_name = 'Time Control'
        if col == '[SumScore_Obsess_Loop]': clean_name = 'Brainrot Loop'
        if col == '[SumScore_Obsess_Debate]': clean_name = 'Obsessive Debate'
        if col == '[SumScore_Obsess_Celeb]': clean_name = 'Celeb Obsession'
        if col == '[SumScore_FOMO_Reaction]': clean_name = 'FOMO Resilience'
        if col == '[SumScore_Deepfake_Detect]': clean_name = 'Deepfake Detect'
        if col == '[SumScore_Crowd_Pressure]': clean_name = 'Crowd Pressure'
        if col == '[SumScore_AI_Trust]': clean_name = 'AI Thinking'
        if col == '[SumScore_AI_Freq]': clean_name = 'AI Frequency'
        
        full_label = str(num)
        
        data_for_plot.append({
            'Cluster_ID': cluster_id,
            'Cluster_Name': c_name,
            'Feature_Col': col,
            'Feature_Num': num,
            'Feature_Label': full_label,
            'Pct_Diff': pct_diff
        })

plot_df = pd.DataFrame(data_for_plot)

# Sort strictly by Feature Number (descending so 1 is at top in barh)
plot_df = plot_df.sort_values(by='Feature_Num', ascending=False)

# ==========================================
# 4. PLOTTING (SHARED Y-AXIS)
# ==========================================
unique_clusters = sorted(plot_df['Cluster_ID'].unique())
num_clusters = len(unique_clusters)

# ShareY ensures aligned rows
fig, axes = plt.subplots(1, num_clusters, figsize=(15, 10), sharey=True)
if num_clusters == 1:
    axes = [axes]
    
# Adjust spacing
plt.subplots_adjust(wspace=0.05)

sns.set_context("talk")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

for i, cluster_id in enumerate(unique_clusters):
    ax = axes[i]
    subset = plot_df[plot_df['Cluster_ID'] == cluster_id]
    
    # Ensure order matches across subplots
    # Pivot or reindex to ensure all features are present in correct order
    # (Though we constructed plot_df to have all features for all clusters)
    
    subset['Color'] = subset['Pct_Diff'].apply(lambda x: '#d73027' if x < 0 else '#4575b4')
    
    # Plot
    bars = ax.barh(subset['Feature_Label'], subset['Pct_Diff'], color=subset['Color'], edgecolor='none', height=0.6)
    
    c_name = subset['Cluster_Name'].iloc[0]
    ax.set_title(f"{c_name}", fontsize=16, fontweight='bold', pad=20)
    
    # Only set Y-label on the first plot
    if i == 0:
        ax.set_ylabel('Features', fontsize=12)
    else:
        ax.set_ylabel('')
        ax.tick_params(left=False) # Hide ticks on internal plots
    
    ax.set_xlabel('% Deviation', fontsize=12)
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if i == 0:
        ax.spines['left'].set_visible(True) # Keep left spine for labels
    else:
        ax.spines['left'].set_visible(False) # Hide left spine for others
        
    ax.grid(False) # No grid as requested previously
    
    ax.set_xlim(-75, 35)
    ax.axvline(0, color='black', linewidth=0.8, linestyle='-')
    
    # Values
    for bar in bars:
        width = bar.get_width()
        # Smart positioning
        label_x_pos = width + 2 if width > 0 else width - 12
        value_text = f'{width:+.1f}%'
        
        align = 'left' if width > 0 else 'right'
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, value_text, 
                va='center', ha=align, fontsize=10, color='#333333')

# Final layout
fig.suptitle('Distinctive Features by Cluster (Compared to Global Mean)', fontsize=16, y=0.98)
plt.tight_layout() # This might break sharey wspace, check
plt.subplots_adjust(top=0.90, wspace=0.1) # Manual adjust

output_path = os.path.join(OUTPUT_DIR, 'cluster_deviation_shared.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {output_path}")
