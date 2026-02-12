# PHƯƠNG PHÁP VÀ CÔNG THỨC TOÁN HỌC TRONG PHÂN TÍCH CỤM
*(Bản giải thích chi tiết & trực quan)*

Tài liệu này giải thích các công thức toán học được sử dụng, **tại sao lại dùng chúng**, và minh họa bằng **dữ liệu thực tế** từ dự án của bạn.

---

## 1. Phân Tích ANOVA (Kiểm định sự khác biệt)

Chúng ta dùng ANOVA để trả lời câu hỏi: *"Các cụm này có thực sự khác nhau không, hay chỉ là do chia ngẫu nhiên mà thành?"*

### Công Thức Cốt Lõi (F-Statistic)
Chỉ số quan trọng nhất là **F**, được tính bằng tỷ lệ giữa "Độ tách biệt giữa các nhóm" và "Độ lộn xộn trong nội bộ nhóm".

```text
       Phương sai GIỮA các nhóm (Signal)
F  =  -----------------------------------
       Phương sai TRONG nội bộ nhóm (Noise)
```

**Tại sao tính như vậy?**
*   Hãy tưởng tượng **Signal (Tử số)** là khoảng cách giữa các tâm cụm. Càng xa càng tốt.
*   Hãy tưởng tượng **Noise (Mẫu số)** là độ rộng của mỗi cụm. Càng nhỏ (gọn) càng tốt.
*   Nếu **F cao**, nghĩa là khoảng cách giữa các cụm rất lớn so với độ lộn xộn bên trong chúng => Các cụm này là "thật" và rất rõ ràng.

### Ví Dụ Dữ Liệu Thực Tế: Biến `SumScore_FOMO_Reaction`
Biến này có chỉ số **F = 1322.06** (Rất khổng lồ).

1.  **Tính Trung Bình (Mean):**
    *   Trung bình chung cả nhóm Gen Z: **2.83**
    *   Cụm 0 (Zombie): **2.97**
    *   Cụm 2 (Healthy): **1.56**

2.  **Sự Khác Biệt (Signal):**
    *   Khoảng cách từ Cụm 2 đến trung bình chung là $|1.56 - 2.83| = 1.27$. Đây là khoảng cách rất lớn trên thang điểm 1-3.
    *   Điều này làm cho tử số (Signal) rất lớn.

3.  **Kết Luận:**
    Vì F quá lớn (1322), xác suất để sự khác biệt này là ngẫu nhiên (**P-value**) chỉ là $2.31 \times 10^{-228}$ (gần như bằng 00).
    -> **Chứng minh:** Cụm Healthy thực sự "miễn nhiễm" với FOMO so với 2 cụm còn lại.

---

## 2. Tâm Cụm (Centroids)

Tâm cụm là "người đại diện" điển hình nhất cho nhóm đó.

### Công Thức
Tâm cụm đơn giản là **giá trị trung bình cộng** của tất cả thành viên trong cụm đó.

```text
Tâm Cụm (C) = Tổng điểm của tất cả thành viên / Số lượng thành viên
```

**Tại sao dùng trung bình cộng?**
Trong toán học, giá trị trung bình là giá trị giúp **tối thiểu hóa tổng sai số** (khoảng cách) đến các điểm khác. Dùng trung bình giúp ta tìm ra điểm "ở giữa nhất" của đám đông.

### Ví Dụ: Biến `SumScore_Work_Check` (Check việc liên tục)
*   **Cụm 1 (Nghiện/Zombie):** Trung bình là **3.78** (Gần 4 điểm - Rất Thường Xuyên).
*   **Trung bình xã hội:** Là **3.28**.
*   **So sánh:** Cụm 1 cao hơn xã hội **+12.5%**.

-> Điều này định nghĩa "tính cách" của Cụm 1: Đây là những người bị ám ảnh bởi công việc và check tin nhắn liên tục.

---

## 3. Thuật Toán K-Means & Elbow Method

Chúng ta dùng K-Means để chia 645 người thành các nhóm, sao cho những người trong cùng một nhóm thì giống nhau nhất có thể.

### Công Thức Hàm Mục Tiêu (WCSS)
K-Means cố gắng làm cho chỉ số **WCSS** (Tổng bình phương sai số) càng nhỏ càng tốt.

```text
WCSS = Tổng khoảng cách từ mỗi người đến Tâm Cụm của họ
```

**Tại sao tính như vậy?**
*   Nếu WCSS lớn: Nghĩa là các thành viên đang ở rất xa "người đại diện" của họ -> Nhóm chưa tốt, còn lộn xộn.
*   Nếu WCSS nhỏ: Nghĩa là mọi thành viên đều vây quanh rất sát "người đại diện" -> Nhóm rất chặt chẽ, đặc trưng rõ ràng.

### Tại sao chọn K=3 (Elbow Method)?
Trong biểu đồ bạn đã vẽ:
1.  Khi chia 1 nhóm (k=1) thành 2 nhóm (k=2): WCSS giảm cực mạnh (Vì ta tách được nhóm Healthy ra khỏi nhóm Nghiện).
2.  Khi chia 2 nhóm thành 3 nhóm (k=3): WCSS tiếp tục giảm mạnh (Vì ta tách tiếp nhóm Nghiện thành Nghiện Công Việc và Nghiện Giải Trí/MXH).
3.  Khi chia 3 nhóm thành 4 nhóm (k=4): WCSS giảm rất ít (Không đáng kể).

-> **Kết luận:** Dừng ở **3** là tối ưu nhất ("Khuỷu tay" của đồ thị).

---

## TỔNG KẾT DÀNH CHO BÁO CÁO KHOA HỌC

1.  Chúng ta dùng **K-Means** để gom nhóm sao cho nội bộ đồng nhất nhất (WCSS thấp nhất).
2.  Chúng ta xác nhận lại bằng **ANOVA (F-test)** để chứng minh sự khác biệt giữa các nhóm là có ý nghĩa thống kê (F cực lớn, p < 0.05).
3.  Chúng ta dùng **Centroids** để gọi tên và mô tả đặc điểm hành vi của từng nhóm.
