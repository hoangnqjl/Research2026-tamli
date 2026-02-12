import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

print("--- CORRELATION ANALYSIS: BEHAVIORS VS CRITICAL THINKING ---")

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

# 2. DEFINE VARIABLES

# The 13 Behaviors from previous analysis
BEHAVIORS_13 = [
    '[SumScore_Work_Check]',
    '[SumScore_Sleep_Loss]',
    '[SumScore_Fatigue]',
    '[SumScore_Escapism]',
    '[SumScore_Control_Time]',
    '[SumScore_Obsess_Loop]',
    '[SumScore_Obsess_Celeb]',
    '[SumScore_Obsess_Debate]',
    '[SumScore_Deepfake_Detect]', # Also in CT
    '[SumScore_Crowd_Pressure]',
    '[SumScore_Deep_Reading]',    # Also in CT
    '[SumScore_AI_Trust]',
    '[SumScore_FOMO_Reaction]'
]

# The 5 Critical Thinking Indicators (mapped from image)
# Diễn giải -> Clickbait_Aware
# Phân tích -> Deep_Reading
# Đánh giá -> Deepfake_Detect
# Suy luận -> Source_Check
# Tự điều chỉnh -> Control_Time
CT_SKILLS = [
    '[SumScore_Clickbait_Aware]',
    '[SumScore_Deep_Reading]',
    '[SumScore_Deepfake_Detect]',
    '[SumScore_Source_Check]',
    '[SumScore_Control_Time]'
]

# Label Mappings (English)
LABEL_MAP = {
    '[SumScore_Work_Check]': 'Work Check',
    '[SumScore_Sleep_Loss]': 'Sleep Loss',
    '[SumScore_Fatigue]': 'Fatigue',
    '[SumScore_Escapism]': 'Escapism',
    '[SumScore_Control_Time]': 'Control Time',
    '[SumScore_Obsess_Loop]': 'Obsessive Looping',
    '[SumScore_Obsess_Celeb]': 'Celebrity Obsession',
    '[SumScore_Obsess_Debate]': 'Obsessive Debate',
    '[SumScore_Deepfake_Detect]': 'Deepfake Detection',
    '[SumScore_Crowd_Pressure]': 'Crowd Pressure',
    '[SumScore_Deep_Reading]': 'Deep Reading',
    '[SumScore_AI_Trust]': 'AI Trust',
    '[SumScore_FOMO_Reaction]': 'FOMO Reaction',
    '[SumScore_Clickbait_Aware]': 'Clickbait Awareness',
    '[SumScore_Source_Check]': 'Source Checking'
}

CT_LABELS = [
    'Interpretation (Clickbait)',
    'Analysis (Reading)',
    'Evaluation (Deepfake)',
    'Inference (Source Check)',
    'Self-Regulation (Control)'
]

# 3. CALCULATE CORRELATION
# We want rows = 13 Behaviors, Cols = 5 CT Skills
# Use Pearson correlation

# subset data
data_13 = df[BEHAVIORS_13]
data_5 = df[CT_SKILLS]

# Compute correlation matrix between the two sets
# We can do this by computing full corr matrix and slicing
full_cols = list(set(BEHAVIORS_13 + CT_SKILLS)) # Unique columns
corr_full = df[full_cols].corr(method='pearson')

# Slice for Heatmap
# Index (Rows): 13 Behaviors
# Columns (Cols): 5 CT Skills
heatmap_data = pd.DataFrame(index=BEHAVIORS_13, columns=CT_SKILLS)

for r in BEHAVIORS_13:
    for c in CT_SKILLS:
        heatmap_data.loc[r, c] = corr_full.loc[r, c]

heatmap_data = heatmap_data.astype(float)

# Rename Indices and Columns for Plotting
heatmap_data.index = [LABEL_MAP.get(x, x) for x in heatmap_data.index]
heatmap_data.columns = CT_LABELS

# 4. PLOT HEATMAP
plt.figure(figsize=(10, 12))
sns.set_context("notebook", font_scale=1.1)

# Mask for exact self-correlations (1.0) if relevant, but here we want to show relationships.
# Since some variables overlap (Control, Reading, Deepfake), they will show 1.0. 
# This is expected and good verification.

ax = sns.heatmap(
    heatmap_data, 
    annot=True, 
    fmt=".2f", 
    cmap="RdBu_r", # Red = Negative, Blue = Positive
    vmax=1, 
    vmin=-1,
    center=0,
    linewidths=.5,
    cbar_kws={"shrink": .8, "label": "Pearson Correlation"}
)

plt.title("Correlation: Behaviors vs. Critical Thinking Skills", fontsize=16, pad=20, fontweight='bold')
plt.ylabel("13 Behaviors (Clustering Features)", fontweight='bold')
plt.xlabel("5 Critical Thinking Skills (Delphi 1990)", fontweight='bold')

plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

plt.tight_layout()
output_path = os.path.join(BASE_DIR, 'outputs', 'correlation_ct_heatmap.png')
plt.savefig(output_path, dpi=300)
print(f"Heatmap saved to {output_path}")
