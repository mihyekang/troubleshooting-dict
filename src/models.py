from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IssueCreate(BaseModel):
    service: str = Field(..., description="이슈 발생 서비스명")
    title: str = Field(..., description="이슈 제목")
    symptom: str = Field(..., description="현상")
    problem: str = Field(..., description="문제(원인)")
    impact: str = Field(..., description="영향도")
    solution: str = Field(..., description="해결방안")
    result: str = Field(..., description="조치결과")
    labels: List[str] = Field(default_factory=list, description="라벨(검색용 키워드)")
    reporter: Optional[str] = Field(None, description="등록자")


class IssueUpdate(BaseModel):
    symptom: Optional[str] = None
    problem: Optional[str] = None
    impact: Optional[str] = None
    solution: Optional[str] = None
    result: Optional[str] = None
    labels: Optional[List[str]] = None


class Issue(IssueCreate):
    id: int
    created_at: datetime
    jira_issue_key: Optional[str] = None
    confluence_page_id: Optional[str] = None
