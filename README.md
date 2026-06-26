# 문제해결 사전 (Troubleshooting Dictionary) - PoC

서비스 단위 이슈·리스크를 등록·검색하고, 필요 시 Jira/Confluence로 연동·전사 공지할 수 있는 PoC.

## 기능

- 이슈 등록/조회/수정 API (FastAPI + SQLite)
- 키워드/라벨/서비스명 기반 검색
- 이슈 필수항목: 현상, 문제, 영향도, 해결방안, 조치결과
- Jira/Confluence 연동 (자격증명 미설정 시 Mock 응답으로 동작, `.env` 설정 시 실제 호출로 전환)

## 설치 및 실행

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt

# 샘플 데이터 등록 (curl 실패 조치 사례)
python -m src.seed

# 서버 실행
uvicorn src.main:app --port 8000
```

API 문서: http://127.0.0.1:8000/docs

## 환경변수

`.env.example`을 `.env`로 복사 후 Jira/Confluence 자격증명 입력 (미설정 시 Mock 응답).

## API 예시

```bash
# 등록
curl -X POST http://127.0.0.1:8000/api/v1/issues -H "Content-Type: application/json" -d '{...}'

# 검색
curl "http://127.0.0.1:8000/api/v1/issues?keyword=curl"
curl "http://127.0.0.1:8000/api/v1/issues?label=SSL"

# Jira/Confluence 연동
curl -X POST http://127.0.0.1:8000/api/v1/issues/1/jira
curl -X POST http://127.0.0.1:8000/api/v1/issues/1/confluence
```

## 검증 결과

- 샘플 이슈(curl 연결 실패/SSL 오류) 등록 및 조회 확인
- 키워드 검색(`curl`) 1건, 라벨 검색(`SSL`) 1건 매칭 확인
- Jira 연동 호출 시 `MOCK-TSD-1` 발급 확인 (Mock)
- Confluence 연동 호출 시 `MOCK-PAGE-1` 발급 확인 (Mock)

## 향후 작업

- 전사 공지 발행 API (`/broadcast`) 및 메신저/이메일 채널 연동
- API Key 인증 적용
- PostgreSQL 등 운영 DB 전환
