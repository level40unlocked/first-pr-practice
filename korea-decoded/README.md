# Korea Decoded: 자동화 파이프라인

해외 시청자에게 한국을 설명하는 얼굴 없는 유튜브 채널 **Korea Decoded**의 자료 수집 → 대본 생성 파이프라인입니다.
(현재는 `first-pr-practice` 저장소에 임시로 있으며, 나중에 별도 저장소로 옮길 예정입니다. 이 폴더를 통째로 옮기면 됩니다.)

## 지금 되는 것 (Phase 1)

```
[수집] Reddit · 뉴스 RSS · 네이버 뉴스
   ↓
[점수화] 콘텐츠 축(기업·기술 > 경제·돈 > 한국 vs 세계 > 사회 > 여행) 가중치 × 반응도
   ↓   (언급된 나라도 표시 → "한국 vs 미국" 같은 비교 소재)
   ↓
[민감도 분류] 🟢 go → 제작 대기열 / ⚠️ review → 사람이 승인해야 진행
   ↓
[대본 생성] Claude → 영문 대본 + 한국어 번역 + 화면 지시 + 팩트체크 목록 (.md)
   ↓   (모델도 민감하다고 판단하면 다시 ⚠️ review로)
[사람 검수] 팩트체크
   ↓
[음성] 콘텐츠 축별 목소리 자동 배정 (Skye / Miles / Fenrir)
   ↓
[배경] 대본 한 줄 = 이미지 한 장. Claude가 줄마다 출처 결정
       스톡 사진(Pexels, 무료) → AI 이미지(Higgsfield, 유료) → 텍스트 카드(무료, 항상 성공)
   ↓
[편집] 배경 이미지 + 내레이션 + 단어 강조 자막 → 1080×1920 쇼츠 mp4
```

다음 단계(아직 없음): 썸네일·메타데이터 → 유튜브 업로드 → 성과 분석.

## 설치

```bash
cd korea-decoded
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 키 입력 후
set -a && source .env && set +a
export PYTHONPATH=src
```

필요한 키:
- `ANTHROPIC_API_KEY`: 대본 생성 (https://console.anthropic.com)
- `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET`: 네이버 뉴스 검색 (https://developers.naver.com, 선택)
- `REDDIT_USER_AGENT`: Reddit 요청 식별용 문자열

## 사용법

```bash
python -m korea_decoded collect                 # 모든 소스에서 주제 수집
python -m korea_decoded collect --sources reddit # 특정 소스만
python -m korea_decoded topics                  # 점수순 주제 목록
python -m korea_decoded review                  # ⚠️ 검토 대기 주제 보기
python -m korea_decoded approve <uid>           # 검토 주제 승인 → 대본 생성 대상
python -m korea_decoded reject <uid>            # 검토 주제 제외
python -m korea_decoded write --limit 3         # 상위 3개 주제 대본 생성
python -m korea_decoded write --dry-run         # API 호출 없이 프롬프트만 확인
```

### 음성, 편집 (팩트체크가 끝난 대본만)

```bash
pip install -r requirements-media.txt
python -m korea_decoded voice <uid> [<uid> ...]       # 축별 목소리로 내레이션 생성
python -m korea_decoded voice <uid> --voice miles     # 목소리 직접 지정
python -m korea_decoded visuals <uid> [<uid> ...]     # 줄마다 배경 이미지 자동 수집
python -m korea_decoded render <uid>                  # visuals 결과로 영상 렌더링
python -m korea_decoded render <uid> --images <폴더>  # 직접 고른 이미지로 렌더링 (이름순)
```

배경 이미지는 `output/visuals/<uid>/`에 저장되고, 같은 폴더의 `credits.json`에 사진 출처(작가, 링크)가 기록됩니다. 마음에 안 드는 이미지는 같은 번호 파일로 바꿔 넣고 `render`만 다시 돌리면 됩니다.

| 목소리 | 엔진 | 담당 콘텐츠 축 | 비용 |
|---|---|---|---|
| **Skye** (메인) | Higgsfield · Seed Speech | 사회, 여행, 미지정 | 유료 (크레딧) |
| Miles | Higgsfield · ElevenLabs | 경제·돈 | 유료 (크레딧) |
| Fenrir | Kokoro (오픈소스) | 기업·기술 | 무료 |

첫 실행 전 준비:
- **Higgsfield:** `HF_KEY` 환경변수, 그리고 `config/channel.toml`의 `[higgsfield].tts_application`에 음성 생성 API 경로를 넣어야 합니다 (https://docs.higgsfield.ai 에서 확인).
- **Pexels:** `PEXELS_API_KEY` (무료, https://www.pexels.com/api/). 없으면 스톡 사진 대신 AI 이미지나 텍스트 카드를 씁니다.
- **AI 이미지:** `config/channel.toml`의 `[visuals].allow_ai = false`로 두면 크레딧을 쓰지 않습니다.
- **Kokoro:** 모델 파일 2개를 `models/`에 받아두세요 (https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
- **폰트:** Montserrat ExtraBold를 `assets/fonts/`에 넣으면 샘플 영상과 같은 자막이 나옵니다. 없으면 기본 폰트를 씁니다.

생성된 대본은 `output/scripts/`에, DB는 `data/korea_decoded.db`에 저장됩니다.

## 운영 방침 바꾸기 (코드 수정 불필요)

| 바꾸고 싶은 것 | 파일 |
|---|---|
| 콘텐츠 축 비중, 키워드 | `config/channel.toml` → `[pillars.*]` |
| 비교 대상 나라 | `config/channel.toml` → `[countries]` |
| ⚠️ 민감 키워드 | `config/channel.toml` → `[sensitivity]` |
| 수집할 서브레딧, RSS, 네이버 검색어 | `config/channel.toml` → `[sources]` |
| 대본 톤, 구조, 규칙 | `prompts/script_system.md` |
| 톤 기준 예시 대본 | `examples/*.md` (승인한 대본을 추가할수록 톤이 안정됨) |
| 목소리 배정, 엔진 | `config/channel.toml` → `[voice_assignment]`, `[voices.*]` |
| 모델, 사고 강도 | 환경변수 `KD_MODEL` (기본 `claude-opus-5`), `KD_EFFORT` (기본 `high`) |

## 민감도 규칙

- 범죄, 사기, 스캔들, 사건사고, 정치·외교 갈등, 비판적인 사회 문제는 **⚠️ review**로 분류됩니다.
- review 주제는 `approve` 전까지 대본을 만들지 않습니다.
- 키워드 검사를 통과해도 모델이 민감하다고 판단하면 초안은 저장하되 review로 되돌립니다.
- 승인된 주제에 이미 초안이 있으면 그대로 쓰고, `approve <uid> --rewrite`로 다시 생성할 수 있습니다.

## 테스트

```bash
python -m pytest
```
