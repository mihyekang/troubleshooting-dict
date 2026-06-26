"""Jira/Confluence 연동 클라이언트 (PoC).

실 운영 연동 전까지는 자격증명 미설정 시 모의(Mock) 응답을 반환하여
API 흐름을 검증할 수 있도록 함. 운영 전환 시 JIRA_*/CONFLUENCE_* 환경변수만
채우면 실제 호출로 전환됨.
"""

import os
import httpx

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "TSD")

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "TSD")


def jira_configured() -> bool:
    return bool(JIRA_BASE_URL and JIRA_API_TOKEN and JIRA_EMAIL)


def confluence_configured() -> bool:
    return bool(CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN and CONFLUENCE_EMAIL)


def create_jira_issue(issue: dict) -> str:
    """이슈를 Jira 티켓으로 생성하고 발급된 이슈 키를 반환."""
    if not jira_configured():
        return f"MOCK-{JIRA_PROJECT_KEY}-{issue['id']}"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[{issue['service']}] {issue['title']}",
            "description": (
                f"현상: {issue['symptom']}\n"
                f"문제: {issue['problem']}\n"
                f"영향도: {issue['impact']}\n"
                f"해결방안: {issue['solution']}\n"
                f"조치결과: {issue['result']}"
            ),
            "issuetype": {"name": "Task"},
            "labels": issue.get("labels", []),
        }
    }
    resp = httpx.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue",
        json=payload,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["key"]


def create_confluence_page(issue: dict) -> str:
    """이슈를 Confluence 페이지로 발행하고 발급된 페이지 ID를 반환."""
    if not confluence_configured():
        return f"MOCK-PAGE-{issue['id']}"

    body_html = (
        f"<h2>{issue['title']}</h2>"
        f"<p><b>서비스:</b> {issue['service']}</p>"
        f"<p><b>현상:</b> {issue['symptom']}</p>"
        f"<p><b>문제:</b> {issue['problem']}</p>"
        f"<p><b>영향도:</b> {issue['impact']}</p>"
        f"<p><b>해결방안:</b> {issue['solution']}</p>"
        f"<p><b>조치결과:</b> {issue['result']}</p>"
    )
    payload = {
        "type": "page",
        "title": f"[{issue['service']}] {issue['title']}",
        "space": {"key": CONFLUENCE_SPACE_KEY},
        "body": {"storage": {"value": body_html, "representation": "storage"}},
    }
    resp = httpx.post(
        f"{CONFLUENCE_BASE_URL}/rest/api/content",
        json=payload,
        auth=(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN),
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.json()["id"]
