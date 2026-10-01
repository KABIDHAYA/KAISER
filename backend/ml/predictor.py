import os
import re
import joblib
import numpy as np

class SentimentPredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'model', 'sentiment_model.joblib')
        vec_path = os.path.join(current_dir, 'model', 'tfidf_vectorizer.joblib')
        
        if not os.path.exists(model_path) or not os.path.exists(vec_path):
            raise FileNotFoundError(
                "Model or vectorizer not found. "
                "Please run train.py first to generate the models in ml/model/."
            )
            
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vec_path)
        
    def _preprocess(self, text: str) -> str:
        text = str(text).lower()
        text = re.sub(r'[^a-z\s]', '', text)
        return text
        
    def predict(self, text: str) -> dict:
        clean_text = self._preprocess(text)
        vec_text = self.vectorizer.transform([clean_text])
        
        pred_class = self.model.predict(vec_text)[0]
        probas = self.model.predict_proba(vec_text)[0]
        confidence = float(np.round(np.max(probas) * 100, 1))
        
        feature_names = self.vectorizer.get_feature_names_out()
        class_idx = np.where(self.model.classes_ == pred_class)[0][0]
        
        coef = self.model.coef_[class_idx]
        feature_indices = vec_text.nonzero()[1]
        
        keywords = []
        for idx in feature_indices:
            keywords.append({
                'word': feature_names[idx],
                'weight': round(abs(float(coef[idx])), 3)
            })
            
        keywords.sort(key=lambda x: x['weight'], reverse=True)
        top_keywords = keywords[:5]
        
        return {
            'sentiment': pred_class,
            'confidence': confidence,
            'keywords': top_keywords
        }
        
    def predict_batch(self, texts: list[str]) -> list[dict]:
        return [self.predict(text) for text in texts]
