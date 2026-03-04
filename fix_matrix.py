import numpy as np
from scipy import sparse
import os

print("Đang đọc file similarity_matrix.npz gốc...")
matrix = sparse.load_npz('Data/similarity_matrix.npz')
print(f"Shape: {matrix.shape}, dtype: {matrix.dtype}")
print(f"Non-zero elements gốc: {matrix.nnz}")

# Chuyển float64 → float32 (giảm 50% kích thước)
matrix = matrix.astype(np.float32)

# Dùng ngưỡng 0.05 - cân bằng giữa kích thước và chất lượng
print("\nDùng ngưỡng 0.05...")
matrix = matrix.multiply(matrix >= 0.05)
matrix.eliminate_zeros()
print(f"Non-zero elements sau lọc: {matrix.nnz:,}")

# Lưu
output_path = 'movie_recomender/data/similarity_matrix.npz'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
sparse.save_npz(output_path, matrix)

size = os.path.getsize(output_path) / (1024*1024)
print(f"\n✅ Kích thước file mới: {size:.1f} MB")

test = sparse.load_npz(output_path)
print(f"✅ Shape: {test.shape}")
print(f"✅ Non-zero: {test.nnz:,}")
print(f"✅ dtype: {test.dtype}")