from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from fastapi.responses import StreamingResponse
import io
import csv
from app.database import get_db
from app.models import AnalysisHistory, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("")
def get_history(
    search: Optional[str] = None,
    sentiment: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id)
    
    if search:
        query = query.filter(AnalysisHistory.review_text.ilike(f"%{search}%"))
    if sentiment:
        query = query.filter(AnalysisHistory.sentiment.ilike(sentiment))
        
    total = query.count()
    pages = (total + per_page - 1) // per_page
    items = query.order_by(AnalysisHistory.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.delete("/{id}")
def delete_history(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == id, AnalysisHistory.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found")
    
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}

@router.delete("")
def delete_all_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "All history deleted successfully"}

@router.get("/export")
def export_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).order_by(AnalysisHistory.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "review_text", "sentiment", "confidence", "keywords", "analysis_type", "created_at"])
    
    for item in history:
        writer.writerow([item.id, item.review_text, item.sentiment, item.confidence, item.keywords, item.analysis_type, item.created_at.isoformat()])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history_export.csv"}
    )
