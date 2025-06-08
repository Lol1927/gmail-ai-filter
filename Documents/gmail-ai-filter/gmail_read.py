import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# 데이터 불러오기
df = pd.read_csv("gmail_training_data.csv")
df["text"] = df["subject"].fillna('') + " " + df["body"].fillna('')
X_raw = df["text"]
y = df["importance"]

# 벡터라이저
vectorizer = TfidfVectorizer(ngram_range=(1,2), token_pattern=r'(?u)\b\w+\b')
X = vectorizer.fit_transform(X_raw)

# 모델 학습
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X, y)

# 저장
joblib.dump(model, "importance_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ 모델 학습 완료! importance_model.pkl, vectorizer.pkl 저장됨.")
