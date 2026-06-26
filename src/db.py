import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "troubleshooting.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            title TEXT NOT NULL,
            symptom TEXT NOT NULL,
            problem TEXT NOT NULL,
            impact TEXT NOT NULL,
            solution TEXT NOT NULL,
            result TEXT NOT NULL,
            labels TEXT NOT NULL DEFAULT '[]',
            reporter TEXT,
            jira_issue_key TEXT,
            confluence_page_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def row_to_issue(row: sqlite3.Row) -> dict:
    issue = dict(row)
    issue["labels"] = json.loads(issue["labels"])
    return issue


def insert_issue(data: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO issues
            (service, title, symptom, problem, impact, solution, result, labels, reporter, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["service"],
            data["title"],
            data["symptom"],
            data["problem"],
            data["impact"],
            data["solution"],
            data["result"],
            json.dumps(data.get("labels", []), ensure_ascii=False),
            data.get("reporter"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    issue_id = cur.lastrowid
    conn.close()
    return issue_id


def get_issue(issue_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
    conn.close()
    return row_to_issue(row) if row else None


def search_issues(keyword: str | None, label: str | None, service: str | None) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM issues WHERE 1=1"
    params: list = []
    if service:
        query += " AND service = ?"
        params.append(service)
    if keyword:
        query += " AND (title LIKE ? OR symptom LIKE ? OR problem LIKE ? OR solution LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like, like])
    if label:
        query += " AND labels LIKE ?"
        params.append(f"%\"{label}\"%")
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [row_to_issue(r) for r in rows]


def update_issue(issue_id: int, data: dict) -> dict | None:
    existing = get_issue(issue_id)
    if not existing:
        return None
    fields = {**existing, **{k: v for k, v in data.items() if v is not None}}
    conn = get_connection()
    conn.execute(
        """
        UPDATE issues
        SET symptom = ?, problem = ?, impact = ?, solution = ?, result = ?, labels = ?
        WHERE id = ?
        """,
        (
            fields["symptom"],
            fields["problem"],
            fields["impact"],
            fields["solution"],
            fields["result"],
            json.dumps(fields["labels"], ensure_ascii=False),
            issue_id,
        ),
    )
    conn.commit()
    conn.close()
    return get_issue(issue_id)


def set_external_refs(issue_id: int, jira_issue_key: str | None = None, confluence_page_id: str | None = None) -> dict | None:
    existing = get_issue(issue_id)
    if not existing:
        return None
    conn = get_connection()
    conn.execute(
        "UPDATE issues SET jira_issue_key = COALESCE(?, jira_issue_key), confluence_page_id = COALESCE(?, confluence_page_id) WHERE id = ?",
        (jira_issue_key, confluence_page_id, issue_id),
    )
    conn.commit()
    conn.close()
    return get_issue(issue_id)
