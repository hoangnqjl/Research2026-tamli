import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. CẤU HÌNH TÊN FILE VÀ ĐỌC DỮ LIỆU
# ==========================================
# Hãy đổi tên file bên dưới nếu file của bạn tên khác
ten_file = 'Data.xlsx'
# Lưu ý: Nếu file của bạn là .xlsx chuẩn (Excel), hãy đảm bảo đuôi file đúng.
# Code này sẽ ưu tiên đọc như Excel trước để tránh lỗi mã hóa.

print(f"--- Đang mở file: {ten_file} ---")

df = None
try:
    # CÁCH 1: Đọc bằng engine Excel (openpyxl) - Dành cho file .xlsx
    # Skiprows=2 để bỏ qua 2 dòng tiêu đề phụ nếu có
    df = pd.read_excel(ten_file, skiprows=2, engine='openpyxl')
    print("-> Đã đọc thành công bằng chế độ Excel (.xlsx)!")
except Exception as e_excel:
    print(f"-> Không đọc được bằng chế độ Excel. Lỗi: {e_excel}")
    print("-> Đang thử chuyển sang đọc bằng chế độ CSV...")
    try:
        # CÁCH 2: Đọc bằng engine CSV - Dành cho file .csv thuần
        df = pd.read_csv(ten_file, skiprows=2, encoding='utf-8')
        print("-> Đã đọc thành công bằng chế độ CSV!")
    except Exception as e_csv:
        print(f"-> LỖI: Không thể đọc file. Vui lòng kiểm tra lại file của bạn.")
        print(f"-> Gợi ý: Mở file bằng Excel > Save As > Chọn '.xlsx' rồi chạy lại code.")
        exit()

# ==========================================
# 2. XỬ LÝ DỮ LIỆU & ÁNH XẠ CỘT (QUAN TRỌNG)
# ==========================================
# Xóa khoảng trắng thừa trong tên cột (nếu có) để tránh lỗi không tìm thấy cột
df.columns = [col.strip() for col in df.columns]

# Danh sách các cột bắt buộc phải có (Dựa trên dữ liệu chuẩn của bạn)
col_addiction = '[SumScore_Obsess_Loop]'  # Mức độ Nghiện
col_check = '[SumScore_Source_Check]'  # Kiểm tra nguồn tin
col_detect = '[SumScore_Deepfake_Detect]'  # Phát hiện Deepfake
col_health = '[SumScore_Sleep_Loss]'  # Mất ngủ/Tổn hại sức khỏe

# Kiểm tra xem cột có tồn tại không
missing_cols = [c for c in [col_addiction, col_check, col_detect, col_health] if c not in df.columns]
if missing_cols:
    print(f"\nLỖI TÊN CỘT: Không tìm thấy các cột sau trong file: {missing_cols}")
    print("Hãy kiểm tra lại tên cột trong file Excel của bạn.")
    print("Các cột hiện có:", df.columns.tolist())
    exit()

# Tính toán các chỉ số phân tích
df['Addiction_Score'] = df[col_addiction]
# Năng lực = Trung bình cộng (Kiểm tra + Phát hiện)
df['Competence_Score'] = (df[col_check] + df[col_detect]) / 2
df['Health_Cost'] = df[col_health]

# ==========================================
# 3. PHÂN LOẠI NGƯỜI DÙNG (CLUSTERING LOGIC)
# ==========================================
THRESHOLD = 3.0  # Ngưỡng điểm trung bình (trên thang 5)


def phan_loai(row):
    nghien = row['Addiction_Score']
    nang_luc = row['Competence_Score']

    if nghien >= THRESHOLD:  # Nếu Nghiện cao
        if nang_luc >= THRESHOLD:
            return 'High-Tech Burnout\n(Giỏi - Kiệt sức)'
        else:
            return 'Zombie\n(Nghiện - Thụ động)'
    else:  # Nếu Nghiện thấp
        return 'Healthy\n(Cân bằng)'


df['User_Group'] = df.apply(phan_loai, axis=1)

# Tổng hợp số liệu trung bình để vẽ
summary = df.groupby('User_Group')[['Addiction_Score', 'Competence_Score', 'Health_Cost']].mean().reindex(
    ['Healthy\n(Cân bằng)', 'Zombie\n(Nghiện - Thụ động)', 'High-Tech Burnout\n(Giỏi - Kiệt sức)']
).reset_index()

print("\n--- KẾT QUẢ PHÂN TÍCH ---")
print(summary)

# ==========================================
# 4. VẼ BIỂU ĐỒ (CLUSTERED COLUMN CHART)
# ==========================================
plt.figure(figsize=(14, 8))

# Thiết lập vị trí
x = np.arange(len(summary['User_Group']))
width = 0.25

# Vẽ 3 cột
bar1 = plt.bar(x - width, summary['Addiction_Score'], width, label='Mức độ Nghiện (Addiction)', color='#D90429')  # Đỏ
bar2 = plt.bar(x, summary['Competence_Score'], width, label='Năng lực Tư duy (Competence)', color='#2B9348')  # Xanh lá
bar3 = plt.bar(x + width, summary['Health_Cost'], width, label='Tổn hại Sức khỏe (Health Cost)', color='#FF9F1C')  # Cam

# Trang trí
plt.xlabel('Nhóm Người Dùng', fontsize=12, fontweight='bold')
plt.ylabel('Điểm trung bình (Thang 1-5)', fontsize=12)
plt.title('PHÂN TÍCH SỰ ĐÁNH ĐỔI: NĂNG LỰC SỐ vs SỨC KHỎE', fontsize=16, fontweight='bold', pad=20)
plt.xticks(x, summary['User_Group'], fontsize=11, fontweight='bold')
plt.legend(loc='upper left', fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.ylim(0, 5.5)


# Hàm thêm nhãn số
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        # Chỉ hiện số nếu giá trị không bị NaN
        if not np.isnan(height):
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')


add_labels(bar1)
add_labels(bar2)
add_labels(bar3)

plt.tight_layout()
filename_out = 'Bieu_Do_Phan_Tich_Chi_Phi_Nghien.png'
plt.savefig(filename_out)
print(f"\n-> Đã vẽ xong! Ảnh được lưu tại: {filename_out}")
plt.show()