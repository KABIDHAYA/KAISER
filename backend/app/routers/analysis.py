import json
import pandas as pd
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisHistory, User
from app.auth import get_current_user
from app.schemas import AnalyzeRequest, AnalyzeResponse, BulkAnalyzeResponse
from ml.predictor import SentimentPredictor

router = APIRouter(prefix="/api/analyze", tags=["analysis"])
predictor = SentimentPredictor()

@router.post("", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        prediction = predictor.predict(request.review)
        sentiment = prediction.get("sentiment")
        confidence = str(prediction.get("confidence", 0.0))
        keywords = prediction.get("keywords", [])
        
        history_entry = AnalysisHistory(
            user_id=current_user.id,
            review_text=request.review,
            sentiment=sentiment,
            confidence=confidence,
            keywords=json.dumps([kw for kw in keywords]),
            analysis_type="single"
        )
        db.add(history_entry)
        db.commit()
        
        return AnalyzeResponse(
            sentiment=sentiment,
            confidence=confidence,
            keywords=[{"word": k["word"], "weight": k["weight"]} for k in keywords]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=BulkAnalyzeResponse)
async def bulk_analyze(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    try:
        try:
            df = pd.read_csv(StringIO(content.decode('utf-8', errors='replace')))
        except Exception:
            df = pd.read_csv(StringIO(content.decode('utf-8', errors='replace')), on_bad_lines='skip')
            
        col_map = {str(col).lower().strip(): col for col in df.columns}
        if 'review' not in col_map:
            raise HTTPException(status_code=400, detail="CSV must contain a 'review' column")
        review_col = col_map['review']
        
        results = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total = len(df)
        
        history_entries = []
        
        for index, row in df.iterrows():
            review_text = str(row[review_col])
            prediction = predictor.predict(review_text)
            sentiment = prediction.get("sentiment")
            confidence = str(prediction.get("confidence", 0.0))
            keywords = prediction.get("keywords", [])
            
            if sentiment.lower() == 'positive':
                positive_count += 1
            elif sentiment.lower() == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
                
            results.append({
                "review": review_text,
                "sentiment": sentiment,
                "confidence": confidence,
                "keywords": keywords
            })
            
            history_entries.append(
                AnalysisHistory(
                    user_id=current_user.id,
                    review_text=review_text,
                    sentiment=sentiment,
                    confidence=confidence,
                    keywords=json.dumps(keywords),
                    analysis_type="bulk"
                )
            )
            
        db.add_all(history_entries)
        db.commit()
        
        return BulkAnalyzeResponse(
            results=results,
            summary={
                "total": total,
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "positive_pct": (positive_count / total * 100) if total > 0 else 0.0,
                "negative_pct": (negative_count / total * 100) if total > 0 else 0.0,
                "neutral_pct": (neutral_count / total * 100) if total > 0 else 0.0
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
