"""샘플 이슈 시딩 스크립트: curl 명령어 실패 시 조치 방안."""

from . import db

SAMPLE_ISSUE = {
    "service": "API-Gateway",
    "title": "curl 명령어로 외부 API 호출 시 연결 실패 (Connection refused / SSL 오류)",
    "symptom": (
        "curl -X GET https://api.example.com/v1/health 실행 시 "
        "'curl: (7) Failed to connect to api.example.com port 443: Connection refused' "
        "또는 'curl: (60) SSL certificate problem' 오류 발생"
    ),
    "problem": (
        "1) 대상 서버 방화벽/보안그룹에서 호출 IP 미허용 "
        "2) 사내망에서 외부 HTTPS 아웃바운드 차단 "
        "3) 사내 proxy 미경유로 인증서 체인 검증 실패"
    ),
    "impact": "해당 API 연동 기능 전체 장애, 의존 서비스 응답 지연 또는 실패 (HIGH)",
    "solution": (
        "1) -v 옵션으로 상세 로그 확인: curl -v https://api.example.com/v1/health\n"
        "2) Connection refused → 보안그룹/방화벽에 호출 서버 Outbound IP 등록 요청\n"
        "3) SSL 오류 → 사내 proxy 경유 설정: curl --proxy http://proxy.internal:8080 ...\n"
        "4) 인증서 문제 임시 확인용(운영 사용 금지): curl -k 로 우회 가능 여부만 확인 후 "
        "정식 인증서 체인 등록으로 해결"
    ),
    "result": "보안그룹에 Outbound IP 등록 후 정상 응답(200 OK) 확인, 재발 방지를 위해 모니터링 알람 추가",
    "labels": ["curl", "network", "SSL", "방화벽", "API-Gateway"],
    "reporter": "코어",
}


def main() -> None:
    db.init_db()
    issue_id = db.insert_issue(SAMPLE_ISSUE)
    print(f"샘플 이슈 등록 완료: id={issue_id}")


if __name__ == "__main__":
    main()
