import pandas as pd
import numpy as np
import os
import scipy.stats as stats

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_file = os.path.join(BASE_DIR, 'data', 'processed', 'blind_clustering_final.xlsx')

# Load data
df = pd.read_excel(input_file, sheet_name='Clustered_Users')

# Target Variable
col = '[SumScore_FOMO_Reaction]'

# 1. Get Groups
groups = [df[df['Cluster_ID'] == i][col] for i in range(3)]
n = [len(g) for g in groups]
means = [g.mean() for g in groups]
grand_mean = df[col].mean()
N = len(df)
K = 3

print(f"--- DETAILED CALCULATION FOR {col} ---")
print(f"N (Total samples) = {N}")
print(f"K (Groups) = {K}")
print(f"Grand Mean (x_bar) = {grand_mean:.4f}")
for i in range(3):
    print(f"  Cluster {i}: n={n[i]}, mean={means[i]:.4f}")

# 2. Calculate SS_between (Signal)
# Formula: Sum( n_i * (mean_i - grand_mean)^2 )
ss_between = 0
print("\n[STEP 1] Calculate SS_between (Signal):")
print(f"Formula: Sum( n_i * (mean_i - grand_mean)^2 )")
exprs = []
for i in range(3):
    term = n[i] * (means[i] - grand_mean)**2
    ss_between += term
    exprs.append(f"{n[i]} * ({means[i]:.2f} - {grand_mean:.2f})^2")
    print(f"  Cluster {i}: {n[i]} * ({means[i]:.4f} - {grand_mean:.4f})^2 = {term:.4f}")

print(f"SS_between = {ss_between:.4f}")

# 3. Calculate SS_within (Noise)
# Formula: Sum( (x_ij - mean_i)^2 ) for all observations
ss_within = 0
print("\n[STEP 2] Calculate SS_within (Noise):")
print(f"Formula: Sum of squared distances from each point to its cluster center")
for i in range(3):
    # Sum of squared differences for this group
    ssd = np.sum((groups[i] - means[i])**2)
    ss_within += ssd
    print(f"  Cluster {i} (Sum of Squares inside): {ssd:.4f}")

print(f"SS_within = {ss_within:.4f}")

# 4. Calculate Mean Squares (MS)
df_between = K - 1
df_within = N - K

ms_between = ss_between / df_between
ms_within = ss_within / df_within

print("\n[STEP 3] Calculate Mean Squares (Average Signal & Noise):")
print(f"df_between (K-1) = {3} - 1 = {df_between}")
print(f"df_within (N-K) = {645} - 3 = {df_within}")
print(f"MS_between = SS_between / df_between = {ss_between:.4f} / {df_between} = {ms_between:.4f}")
print(f"MS_within = SS_within / df_within = {ss_within:.4f} / {df_within} = {ms_within:.4f}")

# 5. Calculate F
f_stat = ms_between / ms_within
print("\n[STEP 4] Calculate F-Statistic:")
print(f"F = MS_between / MS_within")
print(f"F = {ms_between:.4f} / {ms_within:.4f}")
print(f"F = {f_stat:.4f}")

# Verify with Library
f_lib, p_lib = stats.f_oneway(*groups)
print(f"\n[VERIFICATION] Scipy library result: F = {f_lib:.4f}")
