import json
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AnalysisHistory, User
from app.auth import get_current_user
from app.schemas import DashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).all()
    
    total = len(history)
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    pos_words = Counter()
    neg_words = Counter()
    
    for item in history:
        sent = item.sentiment.capitalize()
        if sent in sentiment_dist:
            sentiment_dist[sent] += 1
        else:
            if sent == "Neutral":
                sentiment_dist["Neutral"] += 1
            else:
                sentiment_dist.setdefault(sent, 0)
                sentiment_dist[sent] += 1
            
        try:
            keywords = json.loads(item.keywords)
            words = [kw["word"] if isinstance(kw, dict) and "word" in kw else kw for kw in keywords]
            if sent == "Positive":
                for w in words: pos_words[w] += 1
            elif sent == "Negative":
                for w in words: neg_words[w] += 1
        except Exception:
            pass
            
    recent = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id)\
               .order_by(AnalysisHistory.created_at.desc()).limit(5).all()
               
    top_pos = [{"word": w, "count": c} for w, c in pos_words.most_common(5)]
    top_neg = [{"word": w, "count": c} for w, c in neg_words.most_common(5)]
    
    return DashboardResponse(
        sentiment_distribution=sentiment_dist,
        top_positive_words=top_pos,
        top_negative_words=top_neg,
        total_analyses=total,
        recent_analyses=recent
    )
