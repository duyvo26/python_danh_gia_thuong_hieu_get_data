from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re  # noqa: E401, F401


class CompareTitles:
    def __init__(self) -> None:
        pass

    def preprocess(self, text):
        # Chuyển về chữ thường
        text = text.lower()
        # Loại bỏ dấu câu và ký tự đặc biệt
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def calculate_similarity(self, brand, titles):
        # Tiền xử lý tên thương hiệu và tiêu đề bài viết
        brand = self.preprocess(brand)
        processed_titles = [self.preprocess(title) for title in titles]
        # Tính TF-IDF
        vectorizer = TfidfVectorizer().fit([brand] + processed_titles)
        brand_vector = vectorizer.transform([brand])
        titles_vector = vectorizer.transform(processed_titles)
        # Tính cosine similarity
        similarities = cosine_similarity(brand_vector, titles_vector).flatten()
        # Chuyển đổi thành phần trăm
        percentages = similarities * 100
        return percentages

    def compare_text(self, brand_name, article_titles_):
        try:
            percentages = self.calculate_similarity(brand_name, [article_titles_])
            for title, percentage in zip([article_titles_], percentages):
                return percentage
        except Exception as e:
            print("CompareTitles: compare_text", e)
            return 0
