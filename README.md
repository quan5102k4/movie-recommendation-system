# 🎬 CineMatch - Hệ thống đề xuất phim dựa trên nội dung

<p align="center">
  <img src="Pic/giaodien1.png" alt="CineMatch Giao diện" width="800"/>
</p>

---

## 📌 Giới thiệu

**CineMatch** là một hệ thống đề xuất phim thông minh sử dụng các thuật toán trí tuệ nhân tạo để phân tích nội dung phim và đưa ra những đề xuất phù hợp nhất với sở thích của bạn.

---

## 🚀 Tính năng chính

- 🔍 **Tìm kiếm phim theo tên** với gợi ý thông minh
- 🎞️ **Đề xuất phim tương tự** dựa trên nội dung của phim đã chọn
- 🌟 **Danh sách phim nổi bật** được đánh giá cao
- 📈 **Phim xu hướng** đang được quan tâm
- 💻 **Giao diện người dùng hiện đại** phong cách Netflix, responsive trên mọi thiết bị

---

## 🎨 Giao diện ứng dụng

<p align="center">
  <img src="Pic/giaodien1.png" alt="Trang chủ CineMatch" width="800"/>
  <br/><em>Trang chủ - Tìm kiếm và khám phá phim</em>
</p>

<p align="center">
  <img src="Pic/giaodien2.png" alt="Trang đề xuất phim" width="800"/>
  <br/><em>Trang đề xuất phim tương tự</em>
</p>

<p align="center">
  <img src="Pic/giaodien3.png" alt="Trang phim xu hướng" width="800"/>
  <br/><em>Trang phim xu hướng & đánh giá cao</em>
</p>

---

## 🧠 Công nghệ sử dụng

### 🔧 Back-end
- **Python 3.8+**: Ngôn ngữ chính
- **Flask**: Web framework
- **Pandas, NumPy**: Xử lý dữ liệu
- **Scikit-learn**: Thuật toán TF-IDF & Cosine Similarity
- **SciPy**: Sparse matrix để tối ưu RAM
- **Gunicorn**: WSGI server cho production

### 🎨 Front-end
- **HTML/CSS**, **JavaScript**
- **Bootstrap 5**, **Font Awesome**, **Google Fonts**
- **AOS**: Hiệu ứng cuộn trang

---

## 📁 Cấu trúc dự án

```
Movie_Recommendation_System/
├── .gitattributes                         # Cấu hình Git attributes
├── data_preprocessing.ipynb               # Notebook xử lý dữ liệu
├── fix_matrix.py                          # Script tối ưu ma trận tương đồng
├── requirements.txt                       # Danh sách thư viện cần thiết
├── render.yaml                            # Cấu hình deploy Render
├── Data/                                  # Thư mục chứa dữ liệu gốc
│   ├── Data_Movies_ok.csv                 # Dữ liệu phim đã xử lý
│   ├── Data_Movies.csv                    # Dữ liệu phim gốc
│   └── similarity_matrix.npz             # Ma trận tương đồng gốc (352MB)
└── movie_recomender/                      # Thư mục chứa mã nguồn chính
    ├── app.py                             # Flask application chính
    ├── recommender.py                     # Module xử lý đề xuất phim
    ├── matrix_loader.py                   # Module tải ma trận tương đồng
    ├── Procfile                           # Cấu hình Gunicorn cho Railway
    ├── requirements.txt                   # Thư viện cho production
    ├── data/                              # Dữ liệu cho ứng dụng
    │   ├── Data_Movies_ok.csv             # Dữ liệu phim
    │   └── similarity_matrix.npz         # Ma trận sparse đã tối ưu (12.8MB)
    ├── static/                            # Tài nguyên tĩnh
    │   ├── style.css
    │   ├── data/
    │   │   └── movie-poster.json
    │   ├── images/
    │   └── posters/
    └── templates/                         # Template HTML
        ├── index.html
        ├── recommendations.html
        ├── trending.html
        ├── top_rated.html
        └── about.html
```

---

## 🧩 Quy trình hoạt động

### Tổng quan hệ thống

<p align="center">
  <img src="Pic/pic0.jpg" alt="Tổng quan hệ thống" width="700"/>
  <br/><em>Tổng quan kiến trúc hệ thống CineMatch</em>
</p>

1. **Tiền xử lý dữ liệu**
   - Làm sạch, loại bỏ giá trị thiếu, chuẩn hóa

2. **Xây dựng mô hình**
   - Vector hóa nội dung bằng **TF-IDF**
   - Tính **Cosine Similarity** giữa các phim
   - Lưu ma trận dạng **Sparse** để tối ưu RAM (352MB → 12.8MB)

3. **Đề xuất**
   - Trả về danh sách phim có nội dung gần nhất với phim được chọn

### Workflow tải ma trận tương đồng

```
Khởi động app
    ↓
1. Tìm file local: data/similarity_matrix.npz  → Có? Load ngay ✅
    ↓ Không có
2. Tải từ Google Drive (12.8MB sparse)         → Thành công? Lưu local ✅
    ↓ Thất bại
3. Tự tính toán lại (toàn bộ 11.756 phim)     → Lưu sparse local ✅
```

---

## 📐 Thuật toán Cosine Similarity

<p align="center">
  <img src="Pic/pic_cosine.png" alt="Cosine Similarity" width="600"/>
  <br/><em>Minh họa độ tương đồng Cosine</em>
</p>

Hệ thống sử dụng **Cosine Similarity** để đo độ tương đồng giữa các phim dựa trên vector TF-IDF của mô tả nội dung:

$$\text{similarity}(A, B) = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$$

---

## ⚙️ Cài đặt và chạy ứng dụng

### ✅ Yêu cầu
- Python 3.8+
- Pip

### 🔨 Các bước triển khai

```bash
# 1. Clone repo
git clone <repository-url>
cd Movie_Recommendation_System

# 2. Cài đặt thư viện
pip install -r movie_recomender/requirements.txt

# 3. Chạy ứng dụng
cd movie_recomender
python3 app.py
```

➡️ Mở trình duyệt và truy cập: `http://localhost:6789`

---

## 🌟 Tính năng nổi bật

### 1. Hệ thống đề xuất nội dung
- Sử dụng **TF-IDF** và **Cosine Similarity** để tìm phim tương tự
- Toàn bộ **11.756 phim** đều được tính toán

### 2. Tối ưu bộ nhớ
- Ma trận lưu dạng **Sparse Matrix** — giảm từ 352MB → 12.8MB
- Chỉ load **1 hàng** khi tìm kiếm, không load toàn bộ ma trận
- RAM sử dụng: ~50-100MB thay vì ~1.5GB

### 3. Tìm kiếm thông minh
- Tìm kiếm realtime với hình ảnh minh họa rõ ràng
- Hỗ trợ fuzzy matching

### 4. UI hiện đại
- Thiết kế kiểu **Netflix**
- Sử dụng AOS cho hiệu ứng mượt
- Responsive toàn diện

---

## 📊 Thống kê dữ liệu

| Thông tin             | Giá trị              |
|----------------------|----------------------|
| Số lượng phim        | 11.756               |
| Giai đoạn phát hành  | 1085 - 2020          |
| Điểm đánh giá TB     | 6.3/10               |
| Lượt đánh giá TB     | 396/phim             |
| Kích thước ma trận   | 12.8MB (sparse)      |
| RAM sử dụng          | ~50-100MB            |

---

## 👤 Tác giả

- **Đỗ Ngọc Phi** - MSSV: 2221050848
- **Nguyễn Minh Quân** - MSSV: 2221050125
- **Đào Anh Tú** - MSSV: 2221050231
- **GVHD**: Thầy Đặng Văn Nam, Cô Dương Thị Hiền Thanh  
  _Khoa CNTT - Trường ĐH Mỏ - Địa chất_

---

## 📚 Tài liệu tham khảo

- Bài giảng "Machine Learning - Chương 5: Recommender Systems"
- Tài liệu chính thức của Scikit-learn
- Nguồn học thuật về TF-IDF & Cosine Similarity

---

## 📝 Ghi chú cuối

Dự án **CineMatch** là ví dụ tiêu biểu về việc tích hợp học máy và phát triển web. Các yếu tố như cấu trúc rõ ràng, hiệu suất tối ưu, giao diện thân thiện giúp dự án không chỉ tốt về mặt kỹ thuật mà còn hoàn thiện về trải nghiệm người dùng.

---

⭐ Nếu bạn thấy dự án hữu ích, hãy ⭐ trên GitHub nhé!