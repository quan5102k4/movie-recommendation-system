import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import time
import re
from scipy import sparse
import requests
import io
import gdown

class MovieRecommender:
    def __init__(self, csv_path='data/Data_Movies_ok.csv', similarity_matrix_path='data/similarity_matrix.npz'):
        self.csv_path = csv_path
        self.similarity_matrix_path = similarity_matrix_path
        self.gdrive_id = '1Q73cP4_n_aVEUn8hKLJPyeepfcLipDCm'
        
        # Đọc dữ liệu phim
        self.movies_df = self._load_data()
        
        # Tính toán/nạp ma trận tương đồng
        self.similarity_matrix = self._load_or_compute_similarity_matrix()
    
    def _load_data(self):
        """Đọc và chuẩn hóa dữ liệu phim từ CSV"""
        try:
            df = pd.read_csv(self.csv_path)
            df['overview'] = df['overview'].fillna('')
            
            if 'release_date' in df.columns:
                df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
            
            required_columns = ['id', 'original_title', 'overview', 'vote_average', 'vote_count']
            for col in required_columns:
                if col not in df.columns:
                    print(f"Warning: Missing required column '{col}' in dataset")
            
            if 'poster_path' not in df.columns:
                df['poster_path'] = "/static/images/no-poster.jpg"
            else:
                df['poster_path'] = df['poster_path'].apply(
                    lambda x: f"https://image.tmdb.org/t/p/w500{x}" if pd.notna(x) and x else "/static/images/no-poster.jpg"
                )
            
            print(f"Loaded {len(df)} movies from {self.csv_path}")
            return df
            
        except Exception as e:
            print(f"Error loading movie data: {str(e)}")
            return pd.DataFrame(columns=['id', 'original_title', 'overview', 'vote_average', 'vote_count'])
    
    def _compute_similarity_matrix(self):
        """Tính toán ma trận tương đồng dựa trên overview của phim - giới hạn RAM"""
        start_time = time.time()
        print("Computing similarity matrix...")

        # Tạo TF-IDF vectorizer với giới hạn features để tiết kiệm RAM
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = tfidf.fit_transform(self.movies_df['overview'])

        # Tính ma trận tương đồng cosine theo batch để tiết kiệm RAM
        n = tfidf_matrix.shape[0]
        batch_size = 500
        
        rows = []
        for i in range(0, n, batch_size):
            end = min(i + batch_size, n)
            batch_similarity = cosine_similarity(tfidf_matrix[i:end], tfidf_matrix)
            batch_sparse = sparse.csr_matrix(
                np.where(batch_similarity > 0.05, batch_similarity, 0),
                dtype=np.float32
            )
            rows.append(batch_sparse)
            print(f"Progress: {end}/{n}")
            del batch_similarity

        similarity_sparse = sparse.vstack(rows)
        
        print(f"Similarity matrix computation completed in {time.time() - start_time:.2f} seconds")
        return similarity_sparse  # Trả về sparse matrix
    
    def _save_similarity_matrix(self, similarity_matrix):
        """Lưu ma trận tương đồng vào file để tái sử dụng"""
        os.makedirs(os.path.dirname(self.similarity_matrix_path), exist_ok=True)
        
        # Nếu là dense array thì chuyển sang sparse trước khi lưu
        if isinstance(similarity_matrix, np.ndarray):
            similarity_matrix = sparse.csr_matrix(similarity_matrix.astype(np.float32))
        
        sparse.save_npz(self.similarity_matrix_path, similarity_matrix)
        print(f"Similarity matrix saved to {self.similarity_matrix_path}")
    
    def _load_similarity_matrix(self):
        """Đọc ma trận tương đồng từ file local - GIỮ DẠNG SPARSE"""
        if os.path.exists(self.similarity_matrix_path):
            try:
                # ✅ GIỮ DẠNG SPARSE - KHÔNG gọi .toarray()
                sparse_matrix = sparse.load_npz(self.similarity_matrix_path)
                print(f"Similarity matrix loaded from local file: {self.similarity_matrix_path}")
                return sparse_matrix
            except Exception as e:
                print(f"Error loading local similarity matrix: {str(e)}")
        
        return self._load_from_gdrive()
    
    def _load_from_gdrive(self):
        """Tải ma trận tương đồng từ Google Drive - GIỮ DẠNG SPARSE"""
        print("Attempting to download similarity matrix from Google Drive...")
        
        try:
            # Phương pháp 1: Sử dụng gdown
            temp_file = '/tmp/temp_similarity_matrix.npz'
            url = f'https://drive.google.com/uc?id={self.gdrive_id}'
            
            gdown.download(url, temp_file, quiet=False)
            
            if os.path.exists(temp_file):
                # ✅ GIỮ DẠNG SPARSE - KHÔNG gọi .toarray()
                sparse_matrix = sparse.load_npz(temp_file)
                
                # Lưu vào vị trí chính thức để lần sau dùng lại
                os.makedirs(os.path.dirname(self.similarity_matrix_path), exist_ok=True)
                import shutil
                shutil.copy(temp_file, self.similarity_matrix_path)
                os.remove(temp_file)
                
                print("Successfully loaded similarity matrix from Google Drive")
                return sparse_matrix
            
        except Exception as e:
            print(f"Error using gdown: {str(e)}")
            print("Trying alternative download method...")
            
            try:
                # Phương pháp 2: Sử dụng requests
                direct_url = f"https://drive.google.com/uc?export=download&id={self.gdrive_id}"
                response = requests.get(direct_url, stream=True)
                
                if response.status_code == 200:
                    temp_file = '/tmp/temp_similarity_matrix.npz'
                    with open(temp_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # ✅ GIỮ DẠNG SPARSE
                    sparse_matrix = sparse.load_npz(temp_file)
                    
                    os.makedirs(os.path.dirname(self.similarity_matrix_path), exist_ok=True)
                    import shutil
                    shutil.copy(temp_file, self.similarity_matrix_path)
                    os.remove(temp_file)
                    
                    print("Successfully loaded similarity matrix using requests")
                    return sparse_matrix
                else:
                    print(f"Failed to download file: {response.status_code}")
            except Exception as e:
                print(f"Error with alternative download method: {str(e)}")
        
        print("Failed to download similarity matrix.")
        return None
    
    def _load_or_compute_similarity_matrix(self):
        """Kiểm tra nếu ma trận đã tồn tại thì load, nếu không thì tính và lưu"""
        similarity = self._load_similarity_matrix()
        
        if similarity is not None and similarity.shape[0] == len(self.movies_df):
            return similarity
        
        # Tính toán lại nếu không tải được
        similarity = self._compute_similarity_matrix()
        self._save_similarity_matrix(similarity)
        return similarity
    
    def get_recommendations(self, movie_title, top_n=10):
        """
        Tìm các phim tương tự dựa trên tên phim
        Trả về danh sách top_n phim có điểm tương đồng cao nhất
        """
        movie_idx = self.movies_df[self.movies_df['original_title'] == movie_title].index
        
        if len(movie_idx) == 0:
            similar_titles = self.search_movies(movie_title, limit=1)
            if len(similar_titles) > 0:
                movie_title = similar_titles.iloc[0]['original_title']
                movie_idx = self.movies_df[self.movies_df['original_title'] == movie_title].index
            else:
                print(f"Movie '{movie_title}' not found in dataset")
                return None, None
        
        movie_idx = movie_idx[0]
        
        # ✅ Chỉ lấy 1 hàng từ sparse matrix thay vì toàn bộ dense matrix
        similarity_scores = self.similarity_matrix[movie_idx].toarray().flatten()
        similarity_scores = list(enumerate(similarity_scores))
        
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_similar = similarity_scores[1:top_n+1]
        
        movie_indices = [i[0] for i in top_similar]
        similarity_values = [i[1] for i in top_similar]
        
        return self.movies_df.iloc[movie_indices], similarity_values
    
    def search_movies(self, query, limit=10):
        """
        Tìm kiếm phim theo tên sử dụng các kỹ thuật fuzzy matching
        """
        if not query or len(query) < 2:
            return pd.DataFrame()
        
        query = re.sub(r'[^a-zA-Z0-9\s]', '', query.lower())
        
        self.movies_df['title_lower'] = self.movies_df['original_title'].str.lower()
        
        results = self.movies_df[self.movies_df['title_lower'].str.contains(query, na=False)]
        
        starts_with = results[results['title_lower'].str.startswith(query, na=False)]
        contains = results[~results['title_lower'].str.startswith(query, na=False)]
        
        results = pd.concat([starts_with, contains])
        results = results.sort_values(by=['vote_count', 'vote_average'], ascending=False)
        
        results = results.drop(columns=['title_lower'])
        
        return results.head(limit)
    
    def get_popular_movies(self, min_votes=1000, top_n=10):
        """Lấy danh sách phim được đánh giá cao nhất (có ít nhất min_votes lượt đánh giá)"""
        popular = self.movies_df[self.movies_df['vote_count'] >= min_votes]
        return popular.sort_values('vote_average', ascending=False).head(top_n)
    
    def get_most_voted_movies(self, top_n=10):
        """Lấy danh sách phim có nhiều lượt đánh giá nhất"""
        return self.movies_df.sort_values('vote_count', ascending=False).head(top_n)

    def get_trending_movies(self, min_votes=500, top_n=20):
        """Lấy danh sách phim xu hướng dựa trên đánh giá cao và lượt vote nhiều"""
        df = self.movies_df.copy()
        df['trending_score'] = df['vote_average'] * np.log1p(df['vote_count'])
        trending = df[df['vote_count'] >= min_votes]
        return trending.sort_values('trending_score', ascending=False).head(top_n)
    
    def get_top_rated_movies(self, min_votes=1000, top_n=20):
        """Lấy danh sách phim đánh giá cao, mở rộng hơn get_popular_movies"""
        return self.get_popular_movies(min_votes=min_votes, top_n=top_n)
    
    def get_stats(self):
        """Lấy thống kê cơ bản về dữ liệu phim"""
        stats = {
            'total_movies': len(self.movies_df),
            'avg_rating': round(self.movies_df['vote_average'].mean(), 1),
            'avg_votes': f"{int(self.movies_df['vote_count'].mean()):,}",
            'oldest_movie': self.movies_df['release_date'].min().year if 'release_date' in self.movies_df.columns else 'N/A',
            'newest_movie': self.movies_df['release_date'].max().year if 'release_date' in self.movies_df.columns else 'N/A',
        }
        return stats