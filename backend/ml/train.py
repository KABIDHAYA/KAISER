import os
import re

# Ensure Matplotlib config directory is within writable workspace before importing matplotlib
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
mpl_dir = os.path.join(backend_dir, '.mplconfig')
os.makedirs(mpl_dir, exist_ok=True)
os.environ['MPLCONFIGDIR'] = mpl_dir

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def map_rating(rating):
    if rating <= 2:
        return 'Negative'
    elif rating == 3:
        return 'Neutral'
    else:
        return 'Positive'

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def main():
    data_path = os.path.join(backend_dir, 'data', 'reviews.csv')
    model_dir = os.path.join(current_dir, 'model')
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
        
    os.makedirs(model_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_csv(data_path)
    
    print(f"Total reviews loaded: {len(df)}")
    print("Preprocessing data...")
    df['sentiment'] = df['rating'].apply(map_rating)
    df['clean_review'] = df['review'].apply(preprocess_text)
    
    X = df['clean_review']
    y = df['sentiment']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print("Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, C=1.0)
    model.fit(X_train_vec, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test_vec)
    print("\nClassification Report (Accuracy, Precision, Recall, F1):")
    print(classification_report(y_test, y_pred))
    
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=model.classes_, yticklabels=model.classes_)
    plt.title('ReviewSense - Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    cm_path = os.path.join(model_dir, 'confusion_matrix.png')
    plt.savefig(cm_path)
    plt.close()
    print(f"Saved confusion matrix heatmap to: {cm_path}")
    
    model_path = os.path.join(model_dir, 'sentiment_model.joblib')
    vec_path = os.path.join(model_dir, 'tfidf_vectorizer.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)
    print(f"Saved model to {model_path} and vectorizer to {vec_path}")
    print("Training successfully completed!")

if __name__ == '__main__':
    main()
