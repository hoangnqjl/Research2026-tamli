# CÁCH TÍNH RA CON SỐ F = 1322.06 (PHÉP TÍNH CỤ THỂ)

Đây là các bước **cộng trừ nhân chia** thực tế từ dữ liệu của bạn để ra được con số F khổng lồ kia.

Chúng ta đang tính cho biến: **Phản ứng FOMO (SumScore_FOMO_Reaction)**.

---

## BƯỚC 1: Thu Thập Dữ Liệu Thô
Máy tính đã đếm và tính trung bình cho 3 nhóm như sau:

*   **Tổng số người (N):** 645
*   **Trung bình chung tất cả (`Global Mean`):** **2.83**
*   **Chi tiết từng nhóm:**
    *   **Nhóm 0 (Zombie):** 262 người ($n_0$), Điểm trung bình = **2.97**
    *   **Nhóm 1 (Burnout):** 317 người ($n_1$), Điểm trung bình = **2.99**
    *   **Nhóm 2 (Healthy):** 66 người ($n_2$), Điểm trung bình = **1.56**

---

## BƯỚC 2: Tính "TÍN HIỆU" (Sự khác biệt GIỮA các nhóm)
Công thức: Lấy từng nhóm so với trung bình chung, bình phương lên rồi nhân với số người.

*   Nhóm 0 lệch: $262 \times (2.97 - 2.83)^2 = 5.1$
*   Nhóm 1 lệch: $317 \times (2.99 - 2.83)^2 = 8.1$
*   Nhóm 2 lệch: $66 \times (1.56 - 2.83)^2 = 105.8$ *(Lệch cực nhiều!)*

=> **Tổng độ lệch (SS_between)** = $5.1 + 8.1 + 105.8$ = **119.08**

---

## BƯỚC 3: Tính "NHIỄU" (Sự lộn xộn BÊN TRONG nhóm)
Máy tính đi đo khoảng cách từ mỗi người đến tâm của nhóm họ. Vì mọi người trong nhóm Healthy đều có điểm thấp (1 đến 2) rất giống nhau, và nhóm Nghiện đều điểm cao (3) rất giống nhau, nên độ lệch này rất bé.

=> **Tổng độ lộn xộn (SS_within)** = **28.91** (Con số này máy tính cộng từ 645 người).

---

## BƯỚC 4: CHIA TRUNG BÌNH (Mean Squares)
Trước khi chia nhau, ta phải chia cho "bậc tự do" (giống như chia bình quân).

1.  **Tín hiệu trung bình ($MS_{between}$):**
    *   Có 3 nhóm thì chia cho 2 (3-1).
    *   Calculation: $119.08 : 2$ = **59.54**

2.  **Nhiễu trung bình ($MS_{within}$):**
    *   Có 645 người, 3 nhóm thì chia cho 642 (645-3).
    *   Calculation: $28.91 : 642$ = **0.045** *(Nhiễu siêu nhỏ)*

---

## BƯỚC 5: TÍNH F (KẾT QUẢ CUỐI CÙNG)
Lấy Tín hiệu chia cho Nhiễu.

$$ F = \frac{59.54}{0.045} = 1322.06 $$

**Kết luận:** Tín hiệu (Sự khác biệt) mạnh gấp **1322 lần** so với Nhiễu. Đó là lý do tại sao máy tính khẳng định kết quả này cực kỳ đáng tin cậy.
