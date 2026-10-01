from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Dict, Optional, Any

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AnalyzeRequest(BaseModel):
    review: str = Field(..., min_length=3)

class Keyword(BaseModel):
    word: str
    weight: float

class AnalyzeResponse(BaseModel):
    sentiment: str
    confidence: str
    keywords: List[Keyword]

class SummaryStats(BaseModel):
    total: int
    positive: int
    negative: int
    neutral: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float

class BulkAnalyzeResponse(BaseModel):
    results: List[Dict[str, Any]]
    summary: SummaryStats

class HistoryResponse(BaseModel):
    id: int
    review_text: str
    sentiment: str
    confidence: str
    keywords: str
    analysis_type: str
    created_at: datetime
    class Config:
        from_attributes = True

class KeywordCount(BaseModel):
    word: str
    count: int

class DashboardResponse(BaseModel):
    sentiment_distribution: Dict[str, int]
    top_positive_words: List[KeywordCount]
    top_negative_words: List[KeywordCount]
    total_analyses: int
    recent_analyses: List[HistoryResponse]
