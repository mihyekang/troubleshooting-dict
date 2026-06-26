from fastapi import FastAPI, HTTPException, Query
from typing import Optional

from . import db, integrations
from .models import Issue, IssueCreate, IssueUpdate

app = FastAPI(title="문제해결 사전 PoC", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.post("/api/v1/issues", response_model=Issue, status_code=201)
def create_issue(payload: IssueCreate):
    issue_id = db.insert_issue(payload.model_dump())
    return db.get_issue(issue_id)


@app.get("/api/v1/issues", response_model=list[Issue])
def list_issues(
    keyword: Optional[str] = Query(None, description="제목/현상/문제/해결방안 키워드 검색"),
    label: Optional[str] = Query(None, description="라벨로 검색"),
    service: Optional[str] = Query(None, description="서비스명으로 필터"),
):
    return db.search_issues(keyword=keyword, label=label, service=service)


@app.get("/api/v1/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: int):
    issue = db.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="이슈를 찾을 수 없음")
    return issue


@app.patch("/api/v1/issues/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, payload: IssueUpdate):
    updated = db.update_issue(issue_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="이슈를 찾을 수 없음")
    return updated


@app.post("/api/v1/issues/{issue_id}/jira", response_model=Issue)
def sync_jira(issue_id: int):
    issue = db.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="이슈를 찾을 수 없음")
    jira_key = integrations.create_jira_issue(issue)
    return db.set_external_refs(issue_id, jira_issue_key=jira_key)


@app.post("/api/v1/issues/{issue_id}/confluence", response_model=Issue)
def sync_confluence(issue_id: int):
    issue = db.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="이슈를 찾을 수 없음")
    page_id = integrations.create_confluence_page(issue)
    return db.set_external_refs(issue_id, confluence_page_id=page_id)
