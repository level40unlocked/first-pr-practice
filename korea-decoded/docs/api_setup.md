# API 등록 목록

키는 채팅에 붙여넣지 않는다. 클라우드 환경 설정(세션 상단 환경 메뉴 → Edit)의 **API 자격 증명** 또는 환경 변수에 넣고, 새 세션부터 적용된다.

## 필수 (자동화의 핵심)

| # | 서비스 | 용도 | 등록하는 곳 | 비용 | 환경 변수 | 네트워크 허용 |
|---|---|---|---|---|---|---|
| 1 | **Anthropic API** | 브리핑 자동 작성, 사건 묶기·관심도 채점, 대본 생성, 팩트 정리 | console.anthropic.com → API Keys | 사용량 과금 | `ANTHROPIC_API_KEY` | `api.anthropic.com` |
| 2 | **Higgsfield API** | 음성(Miles/Skye), 이미지 생성, 렌더링을 대화 없이 자동으로 | Higgsfield 계정의 API 키 메뉴 | 크레딧 | `HF_KEY` (또는 `HF_API_KEY` + `HF_API_SECRET`) | Higgsfield API 도메인, `upload.higgsfield.ai`, cloudfront 2곳 |
| 3 | **YouTube Data API v3** | 영상, 쇼츠 업로드, 썸네일, 예약 공개 | console.cloud.google.com → 프로젝트 → API 사용 설정 → OAuth 클라이언트(데스크톱) → OAuth Playground로 refresh token 발급 → **API 감사(audit) 신청** | 무료 (하루 할당량) | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` | `www.googleapis.com`, `oauth2.googleapis.com` |

## 뉴스 수집 (소재를 넓힘)

| # | 서비스 | 용도 | 등록하는 곳 | 비용 | 환경 변수 | 네트워크 허용 |
|---|---|---|---|---|---|---|
| 4 | **네이버 검색 API** | 한국어 뉴스 검색 (영문 언론이 안 다루는 생활 뉴스) | developers.naver.com → 애플리케이션 등록 → 검색 API | 무료 (하루 25,000회) | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | `openapi.naver.com` |
| 5 | **Reddit API** | 외국인이 한국에 대해 실제로 궁금해하는 것 (r/korea 등). 클라우드 서버의 비인증 요청은 차단됨 | reddit.com/prefs/apps → "script" 앱 생성 | 비상업 무료. 수익 채널이면 Reddit 데이터 API 약관 확인 필요 | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | `www.reddit.com`, `oauth.reddit.com` |

추가로 네트워크 허용만 필요한 RSS: `feed.koreatimes.co.kr`, `www.koreajoongangdaily.com`

## 설명 화면, 팩트 체크

| # | 서비스 | 용도 | 등록하는 곳 | 비용 | 환경 변수 | 네트워크 허용 |
|---|---|---|---|---|---|---|
| 6 | **Pexels API** | 설명 화면용 무료 스톡 사진·영상 (AI 이미지 크레딧 절약) | pexels.com/api | 무료 | `PEXELS_API_KEY` | `api.pexels.com`, `images.pexels.com` |
| 7 | **KOSIS 국가통계포털 API** (선택) | 출생아 수, 물가 등 숫자를 원자료로 확인 (Master K의 숫자 신뢰도) | kosis.kr/openapi → 인증키 신청 | 무료 | `KOSIS_API_KEY` | `kosis.kr` |

## 코드 준비 상태
- 이미 연결됨: 1 (대본), 2 (음성, 이미지), 4, 6
- 코드 추가 필요: 3 (업로드), 5 (OAuth 방식으로 교체), 7
- 키가 없으면 해당 단계만 건너뛰고 나머지는 계속 동작한다
