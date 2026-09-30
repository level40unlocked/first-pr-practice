# 기술 파이프라인 정리 (다른 채널·컨셉에 재사용용)

2D 애니메이션 쇼(앵커 + 패널, 설명 화면, 롱폼 + 쇼츠)를 대본 → 음성 → 렌더 → 썸네일 → 유튜브 예약 업로드까지 만드는 방법.
캐릭터 설정·쇼 내용은 빼고 **기술만** 정리. 코드 위치는 모두 `korea-decoded/` 기준.
기준: Four Eyes Report EP.1 제작 (2026-09-28 ~ 09-30).

---

## 0. 한눈에 보기

```
[주제 찾기]  레딧 아카이브 API / 뉴스 → 사람이 고름
    ↓
[대본]       build_script.py: 대사 + 한국어 번역 + 화면 계획 → script.json (렌더 입력) + script_ko.md (검수표)
    ↓
[음성]       Higgsfield text2speech_v2 (ElevenLabs 목소리) → 줄마다 mp3
    ↓
[음성 검수]  faster-whisper로 받아쓰기 → 대본과 비교, 단어 시간 → 자막 타이밍
    ↓
[화면 재료]  사진(CC 라이선스) / AI 일러스트 / 숫자 카드 / 지도 → screens/<꼭지>/ + credits.json
    ↓
[렌더]       render_episode.py → 꼭지마다 episode.py 병렬 → 롱폼 1920×1080 + 꼭지별 쇼츠 1080×1920
    ↓
[썸네일]     thumbnail.py (spec JSON → 1280×720 jpg), 2~3안
    ↓
[업로드]     python -m korea_decoded upload ... --publish-at (비공개 예약) + 썸네일, 설명/태그는 API로 수정
    ↓
[사람]       Studio에서만 되는 것: A/B 테스트, 쇼츠 관련 동영상, (토큰 범위 없으면) 자막
```

## 1. 작업 환경 (두 군데를 나눠 씀)

| 어디 | 되는 것 | 안 되는 것 |
|---|---|---|
| **Claude Code 클라우드 컨테이너** (git 저장소) | 코드 수정, 렌더(ffmpeg 링크 후), 유튜브 API 업로드, git push | 한국 사이트·위키미디어 대량 다운로드·레딧·i.ytimg.com 차단 (IP) |
| **Higgsfield 샌드박스** (`sandbox_exec`, 미국 서버) | ffmpeg, faster-whisper, Playwright, 뉴스 사이트·cloudfront 접속, 레딧 아카이브 API | 호출 끝나고 약 10초 뒤 파일 사라짐 (백그라운드 작업은 15분 임대). 호출 하나 60초 제한 → 긴 건 `background: true` 후 폴링 |

- 컨테이너 ↔ 샌드박스 파일 전달: `media_upload`로 업로드 주소 받기 → **로컬에서 curl PUT** (`If-None-Match: *` 헤더) → `media_confirm` → 샌드박스에서 curl로 받기. 반대 방향도 같은 식 (샌드박스 명령 끝에 `curl -f -X PUT --upload-file`)
- **base64나 텍스트 조각으로 파일을 넘기지 않는다** (느리고 깨짐)
- 컨테이너에서 렌더하려면: `pip install imageio-ffmpeg` 후 그 ffmpeg 바이너리를 PATH에 링크
- 키는 채팅에 붙여넣지 않고 **클라우드 환경 설정의 환경 변수**로 (새 세션부터 적용). 목록: `docs/api_setup.md`, 네트워크 허용 도메인: `docs/network_allowlist.md`

## 2. 파일 지도

| 파일 | 역할 |
|---|---|
| `prototypes/newsrig.py` | 기본 부품: 캐릭터 리그(머리 분석, 눈·눈꺼풀·입·표정), 폰트, 로고, 자막, 오디오 엔벨로프, 쇼츠 하단 배너 |
| `prototypes/dialog.py` | `Puppet` (캐릭터 한 명: 몸통+머리, 숨쉬기, 끄덕임, 눈 깜빡임, 시선), 카테고리 배지 색 |
| `prototypes/episode.py` | **꼭지 하나 렌더**: 타임라인, 자동 샷, 카메라, 설명 화면, 오버레이, 자막, 롱폼+쇼츠 동시 출력 |
| `prototypes/render_episode.py` | **에피소드 렌더**: 꼭지로 쪼개 병렬로 episode.py 실행 → 롱폼 이어 붙이기(재인코딩 없음) |
| `prototypes/thumbnail.py` | 썸네일 생성기 |
| `episodes/epNN/build_script.py` | 대본 원본 (대사·번역·메모·화면 계획) → `script.json`, `script_ko.md` |
| `episodes/epNN/cast/fetch.sh` | 캐릭터 원본 이미지 다운로드 (git에는 안 넣음) |
| `episodes/epNN/screens/<꼭지>/` | 화면 재료 + `credits.json` (라이선스·출처 표기) |
| `episodes/epNN/audio/` | 줄별 mp3, `jobs.json`(생성 job ID·TTS 문구·길이), `asr_words.json`(받아쓰기 단어 시간) |
| `src/korea_decoded/youtube.py`, `cli.py` | 유튜브 업로드 (OAuth refresh token) |
| `config/channel.toml` | 목소리 ID, 발음 치환 규칙, 소스, 민감도 키워드 |
| `tests/test_episode_render.py` | 렌더러 테스트 (샷 규칙, 엔드카드, 표정 등) |

## 3. 캐릭터 리그 (이미지 3장으로 움직이는 캐릭터)

- 캐릭터마다 AI 이미지 3장: **머리**(정면, 입 다문 상태), **몸통**(머리 없는 상반신), **참고**(전신). 단색 배경이면 `remove_bg`로 자동 누끼
- `analyze_head`가 머리 그림에서 눈 위치·크기, 입 위치, 피부색을 자동으로 찾음 → 눈동자·눈꺼풀·입을 **코드로 그림** (그림을 여러 장 만들 필요 없음)
- 움직임: 입 = 음성 크기(엔벨로프)로 열림 정도 / 눈 깜빡임 = 랜덤 스케줄 / 시선 = 작은 떨림(saccade) + 말하는 사람 쪽 / 숨쉬기·끄덕임 = 사인파
- 표정: `mood` (예: `"frown"` = 눈꺼풀 사선 + 찡그린 입). 캐릭터 기본값 + **대사 줄마다 덮어쓰기** 가능 (`"mood": {"panel": "neutral"}`)
- Puppet spec 주요 값: `head`, `body`, `x`, `head_ratio`(머리 크기), `shoulders`, `chin_drop`(목 길이 보정: 머리가 몸에서 떠 보이면 올림), `label`(이름표 글자), `mood`(기본 표정), `energy`(움직임 크기), `white_lens`(안경알 하얗게)
- 교훈: 머리-몸 간격은 캐릭터마다 다르게 보정해야 함 (`chin_drop`). 새 캐릭터는 짧은 테스트 렌더로 먼저 확인

## 4. 렌더러 (`episode.py`)

### 입력: 꼭지 JSON
```json
{"episode": 1, "category": "travel", "desk": "BUSAN", "headline": "...", "hook": "쇼츠 위 문구\n두 줄",
 "characters": {"anchor": {...Puppet spec}, "panel": {...}}, "anchor": "anchor",
 "background": {"image": "seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
 "screens": {"s1": {"image": "a.png", "label": "LABEL", "credit": "Photo: ... (CC BY 2.0)"},
             "s2": {"card": {"title": "BY THE NUMBERS", "stats": [...]}, "credit": "Source: ..."}},
 "lines": [{"who": "anchor", "text": "...", "audio": "audio/l1.mp3", "screen": "s1", "big": true,
            "shot": "anchor_solo", "mood": {"panel": "neutral"}}],
 "words": [{"w": "Hello,", "s": 0.5, "e": 0.8}],
 "short": {"from": 0, "to": 12}}
```
- `short`: 구간만 쇼츠 / `false` = 쇼츠 없음 / 생략 = 꼭지 전체. **0부터 세는 줄 번호** (1부터 세서 한 칸 밀린 적 있음)
- `words` 없으면 글자 수로 추정. 있으면 받아쓰기 단어 시간으로 정확한 자막

### 타임라인·오디오
- 줄 사이 간격 0.35초, 앞 0.5초 / 뒤 0.6초 무음
- **16kHz 사본은 타이밍·입모양 계산만**, 실제 사운드트랙은 **48kHz 원음**으로 믹스 (`load_audio_hq`), AAC 192k
- 목소리 두 개 음량은 줄마다 앵커 평균에 맞춤 (EP.1: 둘 다 약 -14.7 dB). 다음부터: EQ + -14 LUFS 마스터링 추가 예정

### 자동 샷 (`plan_shots`)
| 샷 | 규칙 |
|---|---|
| `wide` | 게스트가 있는 꼭지의 첫 앵커 줄 (패널이 처음부터 앉아 있게) |
| `anchor_solo` | 자료 없는 앵커 멘트, 마무리 코멘트 (앵커 전용 카메라) |
| `anchor_screen` | 앵커 줄에 `screen` → 설명 화면이 **앵커 오른쪽**, 패널은 화면에 남음 |
| `screen_full` | `screen` + `"big": true` → 설명 화면 크게 (데스크 중앙 카메라) |
| `two_shot` / `speaker_close` | 패널 첫 대사 / 대화 중 말하는 사람 쪽 줌 |

- 줄에 `"shot"` 적으면 우선. 앵커 카메라 ↔ 데스크 카메라는 컷, 같은 카메라 안은 부드러운 이동, 4초 넘으면 천천히 줌인
- 세트는 화면보다 넓게 (`WORLD_W=2700`) 그려서 카메라가 좌우로 움직일 공간 확보. 주요 좌표: `SCREEN_OTS`, `ANCHOR_VIEW_X`, `SCREEN_FULL`

### 설명 화면
- 사진·일러스트: Ken Burns(7초 동안 천천히 줌/팬), 화면 사이 0.3초 크로스페이드, 아래 라벨 + 출처
- 숫자 카드: 렌더러가 그림, **숫자가 0부터 올라가는 애니메이션**
- 지도: `make_track_map.py`(태풍 경로, NOAA IBTrACS + Natural Earth), `make_route_map.py`(OSM 도로 모양)
- 한 줄에 화면 여러 개 가능, `build_script.py`가 "정의만 되고 안 쓰인 화면", "credits.json에 없는 파일"을 에러로 잡음

### 오버레이
- 롱폼: 왼쪽 위 EP.n + 카테고리 태그(`TAG_X_LONG`), 오른쪽 위 로고, TOPIC n/N 자막바, 맨 아래 UP NEXT 티커(남은 꼭지 제목 자동)
- 로고·티커는 **쇼츠 크롭 밖**에 두어 쇼츠에 안 들어가게
- 배경: 실사 사진을 어둡게(dim) + 살짝 흐리게(blur)

### 쇼츠 (같은 렌더에서 동시에)
- 1080×1920: 위 = 훅 문구(넘치면 글자 자동 축소), 가운데 = 롱폼 가운데 1440×1080을 1080×810으로, 자막 y=1235, 아래 = 배너 띠 + 핸들
- 크롭 위치는 샷마다 따라감 (`SHORT_X`, 부드럽게 이동). 태그는 쇼츠용 위치(`TAG_X_SHORT`)로 따로 붙임
- 끝에 2.5초 엔드카드 ("WANT THE FULL STORY? / Full episode on our channel / @핸들"). 가짜 구독 버튼은 넣지 않음
- **60초 이하**로 맞출 것

### 실행
```bash
cd episodes/ep01
./cast/fetch.sh                                   # 캐릭터 원본
python3 build_script.py                           # script.json, script_ko.md
python3 ../../prototypes/render_episode.py script.json --jobs 4
# → ep01_long.mp4, ep01_s1_short.mp4 ...  (mp4/wav는 git 제외)
```
- 속도: 영상 길이의 약 4배 (4코어). 꼭지 병렬이라 에피소드 전체 ≈ 가장 긴 꼭지
- 렌더러 수정하면 **돌고 있던 렌더 프로세스를 먼저 종료** (옛 코드로 계속 돔)
- 미리보기는 720p로 줄여 `preview/`에 (git 제외)

## 5. 음성 (TTS)

- Higgsfield `text2speech_v2`, ElevenLabs 계열 목소리 (목소리 ID는 `config/channel.toml [voices.*]`)
- 후보 비교: 같은 문장을 목소리 여러 개로 만들어 이어 붙인 비교 영상을 보여 주고 고르게 함
- **발음 치환**: 화면 자막은 원래 철자, TTS에는 발음 철자 (`[pronunciation]`: 예 "K's Take" → "Kay's Take", 고유명사 음차). `jobs.json`의 `tts_text`에 실제 보낸 문장 기록
- **요청 제한**: 한 번에 약 12개 넘으면 429 → **3~6개씩** 나눠 제출, 완료 대기 후 다음 묶음
- 재생성 필요한 줄만 다시 만들고 `jobs.json` 갱신

## 6. 음성 검수 (ASR)

- 샌드박스에서 faster-whisper `small.en`으로 모든 줄 받아쓰기 → 대본과 단어 비교 (일치율)
- 틀리게 들리는 줄 재생성 (EP.1 예: 지명이 다른 단어로 들림, 짧은 고유명사 뭉개짐)
- 받아쓴 단어 시간 → `audio/asr_words.json` → `build_script.py`가 대본 단어와 정렬(`align_words`) → 자막 타이밍
- "뭉개져 들린다" 피드백: 먼저 ASR 일치율·클리핑 확인 → 문제없으면 재생 기기(PC 스피커) 탓일 가능성. 휴대폰으로 확인

## 7. 화면 재료와 저작권

- 우선순위: 퍼블릭 도메인/CC0 → CC BY (출처 표기) → 공공누리 1유형 → AI 일러스트 ("AI-generated illustration" 화면 표기)
- 파일마다 `credits.json`: 작가, 라이선스, 원본 링크, 화면 표기 문구 → 영상 설명의 PHOTO & IMAGE CREDITS로 옮김
- 수익화 영향: CC BY는 출처만 제대로 쓰면 수익 문제 없음. NC(비상업)·ND 라이선스는 쓰지 않음
- 받기: 위키미디어·정부 사이트는 컨테이너에서 막힘 → 샌드박스에서 받아 업로드 경유

## 8. 썸네일 (`thumbnail.py`)

```bash
cd episodes/ep01 && python3 ../../prototypes/thumbnail.py thumbs/thumb_M.json thumbs/thumb_M.jpg
```
spec 주요 키: `background`, `picture`(오른쪽 기울어진 사진 카드), `picture_size`, `character`(리그 + 표정) 또는 `character_image`(포즈 PNG), `character_height/x`, `text`(2~4줄 큰 글자, 노란색 + 검은 테두리, 자동 축소), `badge`(🇰🇷 위치 칩), `tag`(사진 위 이름표, 한글 폰트 Black Han Sans), `stamp`(빨간 도장 "REAL NEWS", 제목 위 자동 배치)
- 규칙: 요소 3개 이하 + 큰 글자 3~4단어, 오른쪽 아래 영상 길이 표시 자리 비우기, 위치 배지로 나라 표시
- 2~3안을 만들어 Studio "테스트 및 비교"(A/B)에 등록. 결과는 1~2주 뒤 확인

## 9. 유튜브 업로드 (API)

### 인증 (한 번)
Google Cloud 프로젝트 → YouTube Data API v3 켜기 → OAuth 동의 화면(외부, 테스트 사용자 = 채널 계정) → OAuth 클라이언트(웹, 리디렉션 `https://developers.google.com/oauthplayground`) → OAuth Playground에서 refresh token 발급 → 환경 변수 `YOUTUBE_CLIENT_ID / _SECRET / _REFRESH_TOKEN`. 자세히: `docs/api_setup.md`
- 범위: `youtube.upload`, `youtube.readonly`, `youtube`, **`youtube.force-ssl`(자막 업로드에 필요, EP.1 땐 빠져 있었음)**
- "테스트" 상태 앱은 **refresh token이 7일마다 만료** → 주기적으로 재발급
- API 감사(audit) 통과 전에는 API 업로드가 비공개로 고정될 수 있음 → 빨리 신청
- 채널 **전화번호 인증** 필요 (커스텀 썸네일, 15분 넘는 영상). 인증 번호는 계정에 저장되지 않음

### 명령
```bash
export PYTHONPATH=src
python -m korea_decoded upload ep01_long.mp4 --title "..." --description youtube_description.txt \
    --tags korea "korean news" --category 24 --publish-at 2026-10-01T03:00+09:00 --thumbnail thumbs/thumb_M.jpg
python -m korea_decoded upload ... --dry-run      # 보낼 내용만 확인
```
- `--publish-at` = 그때까지 비공개, 시간 되면 자동 공개. 카테고리 24 Entertainment / 25 News & Politics
- 제목·설명·태그 수정: `videos.update` (snippet 전체를 PUT, `requests.put`). **태그에 공백 있으면 셸 따옴표 주의** (한 번 태그가 쪼개져서 API로 고침). 수정 후 다시 읽어서 확인
- 썸네일 교체 확인: 컨테이너에서 i.ytimg.com이 막혀 샌드박스에서 받아 이미지 비교

### API로 안 되는 것 (운영자가 Studio에서)
- 제목·썸네일 **A/B 테스트** ("테스트 및 비교", 공개 전엔 "요건 미충족"으로 대기)
- 쇼츠 **관련 동영상**(롱폼 연결)
- 자막 (토큰에 `youtube.force-ssl` 없으면)
- 채널 표시 이름 변경

### 설명 템플릿
훅 1~2문장 → 채널 한 줄 소개 → CHAPTERS(0:00부터, 실제 렌더 시간) → SOURCES → PHOTO & IMAGE CREDITS → AI 표기("Characters are animated; voices are synthetic.") → 해시태그 3개. 자막은 대본 + 단어 시간으로 SRT 자동 생성 (`epNN_en.srt`)

### 공개 일정 (영어권 대상)
- 롱폼: KST 새벽 3~4시 예약 = 미 동부 오후 2~3시 (미국 저녁 피크 2~3시간 전). 서머타임 끝나면 1시간 늦춤
- 쇼츠: 롱폼 **공개 다음 날부터** 하루 1개 (롱폼 전에 올린 쇼츠는 연결할 곳이 없음), KST 08:00 = 미 동부 전날 저녁
- 쇼츠 설명에 롱폼 링크 + `#Shorts`

## 10. 주제 리서치 (레딧)

- 레딧 본 사이트·redlib 계열 우회 사이트: 클라우드 IP 차단 (403 / 봇 검사 / 429)
- **Arctic Shift 아카이브 API**는 됨 (샌드박스에서):
  `https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=korea&title=why&limit=100&after=2021-01-01&before=<epoch>&sort=desc&fields=id,title,score,num_comments,subreddit,created_utc`
  - `title` 검색은 `subreddit` 또는 `author` 필수. 페이지 넘김 = 마지막 글의 `created_utc`를 `before`로
  - 최근 한 달 글은 점수가 1로 고정(수집 시점 값) → 한 달 이상 지난 글로 순위
- 정렬: 점수 + 댓글×3. 결과 예: `docs/topic_research.md`

## 11. 교훈 모음 (다시 겪지 않도록)

- 대본에 "tonight / this week" 같은 날짜 표현 → 영상 수명이 짧아짐. 에버그린 우선, 날짜 걸린 사실은 **올리기 직전 최신 보도와 대조**
- 게스트 캐릭터가 중간에 "뿅" 나타나지 않게: 첫 줄을 wide로
- 설명 화면이 뜰 때 패널이 사라지지 않게: 화면을 앵커 옆에 배치
- 쇼츠 크롭에서 태그·자막이 잘리지 않게: 쇼츠용 오버레이를 따로 붙임
- 엔드카드 뒤로 이전 프레임이 비치지 않게: 영상 영역을 불투명하게 덮기
- 긴 롱폼: 8분 넘기면 중간 광고 가능 → 꼭지 수로 길이 조절
- 사람이 봐야 하는 결과물(미리보기 영상, 썸네일 후보, 목소리 비교)은 파일로 바로 보여 주고 선택받기
