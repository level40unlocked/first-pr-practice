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

## YouTube Data API 설정 순서 (3번)

1. **Google Cloud 프로젝트 만들기:** console.cloud.google.com → 상단 프로젝트 선택 → 새 프로젝트 (예: `four-eyes-report`)
2. **API 켜기:** API 및 서비스 → 라이브러리 → "YouTube Data API v3" → 사용
3. **OAuth 동의 화면 (Google 인증 플랫폼):** 사용자 유형 **외부** → 앱 이름 "Four Eyes Report Uploader", 지원 이메일 입력 → 범위에 `youtube.upload`, `youtube.readonly`, `youtube`(채널 설정 관리) 추가. **앱 로고는 올리지 않기** (올리면 구글 인증 심사 대상) → 테스트 사용자에 채널 소유 구글 계정 추가
4. **게시 상태:** "테스트" 상태에서는 refresh token이 7일마다 만료됨. 게시(프로덕션)하려면 브랜딩에 홈페이지와 개인정보처리방침이 필요할 수 있고, 그 주소의 도메인을 승인된 도메인으로 등록해야 함 (우리 소유 도메인만. youtube.com 같은 남의 도메인 금지). 도메인이 생기기 전까지는 테스트 상태 + 테스트 사용자(채널 계정)로 운영하고 7일마다 토큰 재발급
5. **OAuth 클라이언트 만들기:** 사용자 인증 정보 → OAuth 클라이언트 ID → 유형 **웹 애플리케이션** → 승인된 리디렉션 URI에 `https://developers.google.com/oauthplayground` 추가 → 클라이언트 ID와 보안 비밀 복사
6. **refresh token 받기 (브라우저만으로):** developers.google.com/oauthplayground → 오른쪽 위 톱니바퀴 → "Use your own OAuth credentials" 체크 → 5번의 ID와 비밀 입력 → 왼쪽 입력칸에 `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube` 입력 → Authorize APIs → **채널 계정으로 로그인** (브랜드 계정 채널이면 해당 채널 선택) → "Exchange authorization code for tokens" → **Refresh token** 복사
7. **클라우드 환경에 등록:** `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` (채팅에 붙여넣지 않기)
8. **API 감사 신청:** "YouTube API Services Audit and Quota Extension Form" 제출. 통과 전에는 API로 올린 영상이 비공개로 고정됨. 몇 주 걸릴 수 있으니 빨리 신청
9. **채널 전화번호 인증:** YouTube 스튜디오에서. 커스텀 썸네일과 15분 넘는 영상에 필요

업로드 명령:
```bash
python -m korea_decoded upload ep12_long.mp4 --title "..." --description desc.txt --tags korea news \
    --publish-at 2026-10-02T18:00+09:00 --thumbnail thumb.png     # 예약 공개 (그 전까지 비공개)
python -m korea_decoded upload ep12_long.mp4 --title "..." --dry-run   # 보낼 내용만 확인
```

## 코드 준비 상태
- 이미 연결됨: 1 (대본), 2 (음성, 이미지), 3 (업로드: `src/korea_decoded/youtube.py`), 4, 6
- 코드 추가 필요: 5 (OAuth 방식으로 교체), 7
- 키가 없으면 해당 단계만 건너뛰고 나머지는 계속 동작한다
