import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# PREDICT USER CLUSTER (Du doan nhom nguoi dung)
# Thuat toan: Logistic Regression (Hoi quy Logistic - Chuyen dung de phan loai)
# Input: 7 Dac diem chinh (nhu trong so do nguoi dung cung cap)
# ==============================================================================

print("--- [PREDICTION TOOL] KHOI TAO MO HINH DU DOAN ---")
print("Dang huan luyen mo hinh tu du lieu goc...")

# 1. LOAD DATA & TRAIN MODEL
try:
    df = pd.read_excel('Data.xlsx', sheet_name='GenZNCKH1', header=2)
except Exception as e:
    print(f"Error: {e}")
    exit()

# 17 Feature chuan de tao nhan (Ground Truth)
all_features = [
    '[SumScore_Work_Check]', '[SumScore_Source_Check]', '[SumScore_Sleep_Loss]',
    '[SumScore_Obsess_Loop]', '[SumScore_Obsess_Debate]', '[SumScore_Obsess_Celeb]',
    '[SumScore_FOMO_Reaction]', '[SumScore_Fatigue]', '[SumScore_Escapism]',
    '[SumScore_Deepfake_Detect]', '[SumScore_Deep_Reading]', '[SumScore_Crowd_Pressure]',
    '[SumScore_Control_Time]', '[SumScore_Clickbait_Aware]', '[SumScore_AI_Trust]',
    '[SumScore_AI_Freq]', '[SumBeh_Study_Score]'
]

# 7 Feature chinh de nguoi dung nhap (Input Model)
input_features = [
    '[SumScore_FOMO_Reaction]',    # 1. FOMO
    '[SumScore_Obsess_Debate]',    # 2. Tranh luan
    '[SumScore_Fatigue]',          # 3. Met moi
    '[SumScore_Escapism]',         # 4. Tron tranh (Escapism)
    '[SumScore_Sleep_Loss]',       # 5. Mat ngu
    '[SumScore_Control_Time]',     # 6. Kiem soat thoi gian
    '[SumScore_AI_Trust]'          # 7. Tin vao AI
]

# Chuan bi du lieu
clean_df = df[all_features].dropna()
X_full = clean_df.values
X_input = clean_df[input_features].values

# A. CLUSTERING (De tao nhan Y)
# Chung ta chay lai K-Means de gan nhan cho tung nguoi trong DB
scaler = StandardScaler()
X_full_scaled = scaler.fit_transform(X_full)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50)
labels = kmeans.fit_predict(X_full_scaled)

# Mapping Labels -> Names (Logic cu)
means = clean_df.copy()
means['Cluster'] = labels
grouped_means = means.groupby('Cluster').mean()

cluster_names = {}
c_ids = grouped_means.index.tolist()
# Healthy: Thap nhat Fatigue
h_id = grouped_means['[SumScore_Fatigue]'].idxmin()
cluster_names[h_id] = "Healthy (Nhom Can bang)"
c_ids.remove(h_id)
# Zombie: Work Check Cao nhat con lai (Hoac Escapism cao nhat)
rem = grouped_means.loc[c_ids]
z_id = rem['[SumScore_Escapism]'].idxmax() # Dung Escapism de match logic
cluster_names[z_id] = "Zombie (Nhom No le)"
c_ids.remove(z_id)
# Burnout
b_id = c_ids[0]
cluster_names[b_id] = "High-Tech Burnout (Nhom Ly tri)"

# B. TRAINING LOGISTIC REGRESSION (MAPPING 7 INPUTS -> CLUSTER)
# Chung ta day may hoc moi quan he giua 7 bien nay va ket qua phan loai
log_reg = LogisticRegression(max_iter=1000) # Removed explicit params to use defaults
log_reg.fit(X_input, labels)

print("-> Huan luyen xong! Do chinh xac mo hinh:", log_reg.score(X_input, labels))
print("="*60)
print("CHAO MUNG DEN VOI CONG CU KIEM TRA SUC KHOE SO")
print("Hay nhap diem so cua ban (Tu 1 den 5 hoaac 1 den 4 tuy cau hoi)")
print("="*60)

# Helper function
def get_score(prompt, min_val=1, max_val=5):
    print(f"\n{prompt}")
    if max_val == 5:
        print("   1: Hoan toan khong (Never)")
        print("   2: Hiem khi (Rarely)")
        print("   3: Thinh thoang (Sometimes)")
        print("   4: Thuong xuyen (Often)")
        print("   5: Rat thuong xuyen (Always)")
    elif max_val == 4:
        print("   1: Hoan toan khong")
        print("   2: Hiem khi")
        print("   3: Thinh thoang")
        print("   4: Thuong xuyen")
    elif max_val == 3:
        print("   1: Khong bao gio")
        print("   2: Thinh thoang")
        print("   3: Thuong xuyen")
        
    while True:
        try:
            val_str = input(f"   -> Lua chon cua ban ({min_val}-{max_val}): ")
            val = float(val_str)
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Vui long nhap so tu {min_val} den {max_val}")
        except ValueError:
            print("Vui long nhap so hop le.")

# USER INPUT - Updated with Natural Language Questions
print("\n" + "="*60)
print("PHAN 1: TAM LY XA HOI")
fomo = get_score("1. Ban co thuong xuyen so bo lo tin tuc (FOMO) khong?", 1, 3)
debate = get_score("2. Ban co thich tranh luan gay gat tren mang khong?", 1, 4)
ai_trust = get_score("3. Muc do tin tuong cua ban vao AI nhu the nao?", 1, 3) # Note: Scale 1-3 based on data

print("\n" + "="*60)
print("PHAN 2: SUC KHOE & KIEM SOAT")
escapism = get_score("4. Ban co dung mang de tron tranh thuc tai (Escapism) khong?", 1, 5)
sleep = get_score("5. Ban co bi mat ngu vi mang xa hoi khong?", 1, 5)
control = get_score("6. Ban co cam thay kho kiem soat thoi gian online khong?", 1, 5)
fatigue = get_score("7. Ban co thay met moi/kiet suc sau khi dung khong?", 1, 4)

# PREDICT
user_data = np.array([[fomo, debate, fatigue, escapism, sleep, control, ai_trust]])
pred_label = log_reg.predict(user_data)[0]
probs = log_reg.predict_proba(user_data)[0]

result_name = cluster_names[pred_label]
confidence = probs[pred_label] * 100

print("\n" + "="*60)
print(f"KET QUA DU DOAN: BAN THUOC NHOM [{result_name.upper()}]")
print(f"Do chac chan: {confidence:.1f}%")
print("-" * 60)
print("Xac suat chi tiet:")
for i in range(3):
    c_name = cluster_names.get(i, f"Cluster {i}")
    print(f" - {c_name:<30}: {probs[i]*100:.1f}%")

print("\nLOI KHUYEN:")
if "Healthy" in result_name:
    print("-> Chuc mung! Ban dang kiem soat cong nghe rat tot.")
elif "Zombie" in result_name:
    print("-> CANH BAO: Ban dang bi le thuoc cam xuc va mat ngu. Hay 'Cai nghien dopamine' ngay!")
elif "Burnout" in result_name:
    print("-> LUU Y: Ban dung mang rat ly tri nhung dang bi cang thang/stress. Hay nghi ngoi nhieu hon.")
    
print("="*60)
input("Nhan Enter de thoat...")
