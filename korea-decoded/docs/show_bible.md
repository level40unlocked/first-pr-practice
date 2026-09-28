# 쇼 바이블 (작업 중)

2D 애니메이션 병맛 뉴스쇼. 외국인이 흥미를 가질 한국 이야기를 너드 아나운서가 진지하게 브리핑하고, 가끔 패널 대화와 토론이 붙는 형식.

- 채널 이름: **Four Eyes Report** (핸들 `@FourEyesReport`). 앵커와 전문가 전원이 안경을 쓰는 방송국이라는 자기 개그. 카테고리는 "K-POP Desk"처럼 Desk로 부름
- 로고: 노란 원 안에 남색 동그란 안경 (코드로 그림: `prototypes/newsrig.py`의 `glasses_logo`)
- 태그라인: **Through our lenses.** 브랜드(이름, 로고, 배너 문구)에는 Korea를 넣지 않고, 영상 제목·썸네일·채널 설명에서 한국을 강조한다. 나중에 방향이 바뀌면 데스크를 추가하는 식으로 확장
- 대외 문구(배너, 채널 설명, 영상 속 멘트)에서는 "nerd"라는 말을 쓰지 않는다. 안경 캐릭터로 보여주면 충분
- 프로필 사진: 앵커(A6) 얼굴
- 배너(확정): 단체샷. 업로드용 2560×1440 파일: [다운로드](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/d9fec721-91b1-43b5-bf7a-151aa04349be.png) (원본 job `7aa944cd-4ae7-469c-82bf-7f847001db55`)
- 영상 로고: **미니멀 배너의 노란 원 안경 마크를 잘라낸 것** (배경 투명 PNG): [fer_logo_mark.png](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/ce946036-9821-419d-aae2-d107a3aef417.png). 렌더러는 `prototypes/fer_logo_mark.png` 또는 환경변수 `FER_LOGO`의 파일을 붙이고, 없으면 같은 모양을 코드로 그림. 유튜브 브랜딩 워터마크에도 이 파일을 사용
- 인트로·엔딩 카드용 미니멀 배너 (1920×1080): [fer_title_card_1920x1080.png](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/866e97c9-3565-4b49-8ecf-279d89e6710b.png)
- 쇼츠 하단 배너: `prototypes/fer_promo_strip.png` (미니멀 배너에서 로고·이름·태그라인·스카이라인 부분)
- **"LIVE" 표시는 쓰지 않는다** (라이브가 아닌데 라이브처럼 보이면 오해를 부르는 메타데이터 문제). 영상 왼쪽 위는 에피소드 태그 `EP.n` + 카테고리 배지. 시계 없음. 제목·썸네일에도 LIVE 금지
- 미니멀 배너 원본(참고): job `53397e26-5652-4dee-b59c-8eb542b9f7c4`
- 애니메이션 방식: `claude/2d-image-animation-automation-xzu38n` 브랜치의 연구 참고 (Plan A: 몸 고정 + 머리 독립 레이어, 입 모양 교체, 캐릭터 디자인 10원칙)

## 제작 구조

- **롱폼이 원본** (16:9, 1920×1080). 에피소드 8~12분, 5~7개 꼭지.
- **쇼츠는 롱폼에서 잘라냄** (9:16, 1080×1920). 가운데에 영상, 위 여백에 클립별 훅 제목, 아래 여백에 채널 홍보(로고, 채널명, 전체 에피소드 안내, 구독 유도).
- 대본을 꼭지 단위로 설계하고 꼭지마다 따로 봐도 이해되는 30~60초 구성과 훅 제목을 붙인다. 렌더링 때 꼭지별 시간을 기록해서 쇼츠를 자동으로 잘라낸다.
- 롱폼 화면은 아나운서와 설명 화면을 가운데 쪽에 모아 배치한다. 쇼츠에서 좌우를 잘라 더 크게 보여줄 수 있게.
- 쇼츠에는 전체 에피소드를 관련 영상으로 연결한다.

## 롱폼 화면 구성

```
┌───────────────────────────────────────────────┐
│ [EP.12] [카테고리]                                │
│  ┌─────────────────┐                          │
│  │   설명 화면       │         아나운서           │
│  │ (영상/AI이미지/   │     ▄▄▄▄▄▄▄▄▄▄▄▄         │
│  │  숫자 카드)       │      (뉴스 데스크)        │
│  └─────────────────┘                          │
│ ▌BREAKING  헤드라인                             ▐ │
└───────────────────────────────────────────────┘
```

## ✅ 메인 아나운서: A6 = Master K

A 캐릭터의 가장 멋진 버전. 굵은 검은 원형 안경, 볼륨 있게 넘긴 머리, 검은 터틀넥(목을 가림)에 차콜 블레이저, 옷깃 핀, 테크 발표자 같은 여유.
[컨셉 이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073946_281fc82c-c07b-4983-b2c2-67f29bc8c322.png)

## 캐릭터 풀 (나머지 11개 모두 보관: 패널, 게스트, 특별 코너 등에 활용)

모든 이미지는 Higgsfield 생성 기록에도 남아 있습니다.

### 원래 아나운서 후보

| | 이름 | 외모 | 성격, 개그 장치 | 컨셉 이미지 |
|---|---|---|---|---|
| A | 민수 박 (Minsu Park) | 테이프 붙인 뿔테 안경, 바가지 머리, 뻐드렁니, 빨간 나비넥타이, 주머니에 펜 세 자루 | 사소한 뉴스를 가장 심각하게 전함. "Statistically speaking…". 숫자를 말하면 안경알이 하얗게 번쩍 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073036_97d2433a-76a1-45ab-aacc-43ceed3cdc3f.png) |
| B | 감자 앵커 | 대머리 감자 몸통, 작은 정장과 넥타이, 가운데 몰린 이목구비, 작은 동그란 안경 | 무표정하게 진지한데 생긴 게 감자라는 부조화 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073036_e6d43c8a-6558-4abc-a4d3-627bc83dbdf0.png) |
| C | 지영 박사 (Dr. Jiyoung) | 거대한 동그란 안경, 연필 꽂은 똥머리, 터틀넥 | 통계만 나오면 과하게 신남. A와 반대 에너지 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073036_298846a8-8aef-45ac-a7f5-835510f983dd.png) |

### A 변형 (A 이미지를 참조로 같은 인물을 조금씩 바꿈)

| | 변화 | 컨셉 이미지 |
|---|---|---|
| A1 | 조금 더 멋있게: 결 있는 버섯머리, 뻐드렁니 제거, 자신감 있는 표정. 테이프 안경과 빨간 나비넥타이는 유지 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073711_0f2a177f-15b6-4b61-af77-b28fb9613379.png) |
| A2 | 색 변경: 남색 가디건, 노란 나비넥타이 (영상 자막의 남색·노랑과 맞춤), 펜 주머니 제거 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073711_b220736f-ea84-4018-9cde-bc96a40de6ff.png) |
| A3 | 더 병맛: 눈이 거대해 보이는 더 큰 안경, 정수리에 삐죽 솟은 머리카락 한 가닥, 진지한 굵은 눈썹 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073713_a774b41d-dad9-49a9-bc40-3b9f75ffa526.png) |

### A 멋진 버전 (A와 A1을 참조로, 같은 인물을 더 멋있게)

| | 멋 단계 | 바뀐 점 | 컨셉 이미지 |
|---|---|---|---|
| A4 | ★ | 테이프 없는 세련된 검은 사각 안경, 옆 가르마의 결 있는 머리, 짙은 빨강 니트 타이, 남색 수트 재킷, 차분하고 똑똑한 미소 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073946_2faa2e6f-4551-4a2c-ba12-da7b7c8ee746.png) |
| A5 | ★★ | 두꺼운 검은 안경은 유지하되 세련되게, 살짝 헝클어진 버섯머리, 느슨하게 맨 노란 나비넥타이, 남색 가디건, 한쪽 눈썹을 올린 영리한 미소 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073947_71ee645f-b9a3-4623-89d7-26f9638c48e0.png) |
| A6 | ★★★ | 굵은 검은 원형 안경, 볼륨 있게 넘긴 머리, 검은 터틀넥에 차콜 블레이저, 옷깃 핀, 테크 발표자 같은 여유 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073946_281fc82c-c07b-4983-b2c2-67f29bc8c322.png) |

### 멋진 너드 후보 (전형적인 너드 대신 "똑똑한데 스타일 좋은" 방향)

| | 컨셉 | 외모 | 성격 | 컨셉 이미지 |
|---|---|---|---|---|
| D | 비밀을 아는 남자 | 언더컷 머리, 얇은 금테 원형 안경, 검은 터틀넥에 차콜 블레이저 | 여유로운 반쯤 미소, 한쪽 눈썹을 올리며 "사실 이건 말이죠…" | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073318_c7dba179-93f3-4804-b404-d3b4ebad94ac.png) |
| E | 해커 | 헝클어진 검은 머리, 투명 뿔테 사각 안경, 큰 후드티, 목에 헤드폰 | 무표정 시크, 태블릿으로 데이터를 띄움 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073318_d1358a3d-cffb-43a0-8361-dc1e45e92b4e.png) |
| F | 샤프한 브리퍼 | 매끈한 단발, 대모갑 캣아이 안경, 모크넥 위에 크림색 오버핏 블레이저 | 자신만만한 미소, 안경을 고쳐 쓰며 팩트 투척 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_073318_0a9641f0-8f64-4584-875f-2194bdcc7a25.png) |

## 고정 패널 아이디어

| 패널 | 캐릭터 | 역할 |
|---|---|---|
| 순자 할머니 | 한국 할머니 현장 기자, 한마디 팩폭 | 한국인의 진짜 반응 |
| 인턴 준호 | 아이스 아메리카노를 달고 사는 잠 못 잔 인턴 | 시청자 대신 기초 질문 |
| 해외 특파원 | 주제에 따라 바뀌는 비교 대상 나라 특파원 | "한국 vs 우리나라" 토론 상대, 과장된 리액션 |

## 개그 원칙

- 개그는 국적이 아니라 캐릭터 성격에서 나온다. 한국을 비하하거나 특정 나라를 고정관념으로 웃기지 않는다.
- 초반에는 사람이 대본의 개그를 다듬는다. 좋은 대본을 예시로 쌓아 AI 대본의 질을 올린다.

## 캐릭터 움직임 (아나운서, 패널 공통)

입(소리에 맞춰 모양 교체), 눈 깜빡임, 눈동자 미세 이동(설명 화면이 나오면 그쪽을 봄), 고개 방향 살짝. 부품 순서: 몸통 → 머리(눈, 입 없는 얼굴) → 흰자 → 눈동자 → 눈꺼풀 → 안경 → 입.

## ✅ 애니메이션 방식 검증 (프로토타입)

### 아나운서 단독 (`prototypes/newsrig.py`): "거의 완벽" 평가
- AI 원본 3장: 머리(눈과 입이 없는 얼굴, 목 없음), 몸통(머리와 목 없음. 손은 책상에 가려짐), 정면 참고 이미지(머리와 몸 비율 계산용)
- 코드가 안경알 두 개, 코, 턱 위치를 찾아서 눈, 눈동자, 눈꺼풀, 입을 직접 그림
- A6 원본: 머리 `497d2899-66fc-40ea-8b60-1d4815c18eb6`, 몸통 `480e7f2e-bde1-49fe-ad18-dfc5d2599626`, 참고 `5d746f9a-6b07-4adb-9eec-3936cf68fecf` (Higgsfield job)
- 샘플: [롱폼](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/5ca55bff-bbd0-400b-8ee3-fdcb9ca9b3b5.mp4), [쇼츠](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/0210d11e-6202-42d2-803a-986a4bf0e7c7.mp4)

### 아나운서 + 패널 대화 (`prototypes/dialog.py`)
- 패널: C(지영 박사). 원본: 머리 `c67fcd43-9c73-473c-b29f-4be8a1cd81e5`, 몸통 `ec8bd826-58a3-4d75-bff3-18cce3c5a521`, 참고 `2a93c3aa-974e-40fb-b63a-26662d2f9796`
- 음성: 아나운서 Miles(ElevenLabs), 지영 박사 Skye(Seed Speech)
- 한 책상에 두 명. 말하는 사람 쪽으로 카메라가 당겨지고, 듣는 사람은 말하는 사람을 보며 끄덕임. 방송 그래픽은 고정
- 샘플: [롱폼](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/68a5d7d8-53e6-4b3a-81ce-838923ebbed9.mp4), [쇼츠](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/b93ed0b0-1212-4586-8a97-5892d5dcfda8.mp4)

## 뉴스 데스크 (세부 카테고리)

모든 꼭지에 카테고리 배지를 붙입니다. 롱폼은 왼쪽 위 에피소드 태그 옆 (쇼츠는 롱폼을 잘라서 같은 위치에 보임). 하단 자막바 태그도 카테고리 색을 따릅니다.
데스크마다 전문가 캐릭터를 둡니다 (아래 후보).

| 키 | 배지 | 색 | 비고 |
|---|---|---|---|
| current_affairs | CURRENT AFFAIRS (시사) | 빨강 | 민감도 ⚠️ 검토 대상이 많음 |
| kpop | K-POP & ENTERTAINMENT | 핑크 | 뮤직비디오·방송 영상 사용 금지 (저작권). 그래픽으로 재구성 |
| hidden_korea | HIDDEN KOREA (한국의 숨겨진 비밀) | 보라 | |
| korea_vs_world | KOREA VS WORLD | 파랑 | 비교 포맷 |
| money_business | MONEY & BUSINESS | 초록 | 광고 단가 높음 |
| tech | TECH | 청록 | |
| food_life | K-FOOD & LIFE | 주황 | |
| travel | TRAVEL | 틸 | |

패널 크기 확정: head_ratio 0.74, shoulders 500 (지영 박사 기준, 사용자 OK)

### 데스크별 전문가 후보 (1차 컨셉)

리그가 안경알 안에 눈을 그리므로 모두 안경을 쓰고, 목은 옷깃으로 가리고, 코는 선명하게 그리도록 요청했습니다. 그림체는 A6를 참고했습니다.

| 데스크 | 역할 | 외모 | 성격, 개그 장치 | 컨셉 이미지 |
|---|---|---|---|---|
| current_affairs | 시사 베테랑 특파원 | 50대 후반 여성. 은발 단발, 얇은 사각 돋보기 안경, 진홍 블레이저 + 검은 터틀넥, 포스트잇 붙은 서류 더미 | 모든 스캔들을 다 봐서 무심함. 건조한 한마디 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094129_c4a8bc6c-056f-4293-8608-8e5a3ff4a8c1.png) |
| kpop | K-POP 분석가 | 전 아이돌 연습생 청년. 파스텔 핑크 머리, 큰 투명테 원형 안경, 하이넥 무대 재킷, 하트 응원봉 | 과몰입 팬보이. 컴백 얘기만 나오면 폭주 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094130_975942f9-8016-45b9-91bf-ddc2871896dd.png) |
| hidden_korea | 비밀 기록 연구가 | 30대 여성. 비녀로 묶은 긴 머리, 작은 금테 원형 안경, 보라색 한복풍 재킷, 두루마리 | 음모론 폭로하듯 속삭이며 "사실은…" | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094130_5aabf690-98af-4b1f-b6b6-98ac98eb843e.png) |
| korea_vs_world | 비교 심판 | 갈색 피부 청년. 곱슬머리, 파란 사각 안경, 파란 하프집업, 심판 호루라기, 점수판 | 스포츠 중계처럼 한국 vs 세계 판정 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094130_d2d5cb84-8332-485d-8a9f-df2405c4d4d4.png) |
| money_business | 머니 애널리스트 | 40대 남성. 올백 머리, 얇은 금테 사각 안경, 초록 조끼 + 크림 터틀넥, 행커치프, 복고 계산기 | 모든 주제를 결국 돈 얘기로 끌고 감 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094129_b35c18d3-ba65-4127-82d5-0321defeb384.png) |
| tech | 테크·로봇 전문가 | 젊은 여성. 청록 브릿지 픽시컷, 굵은 청록테 안경, 하이넥 테크웨어, 어깨 위 작은 로봇 | 무표정 천재. 로봇이 대신 리액션 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094128_35bc69bf-8144-48e8-8632-7b5e6d0d057b.png) |
| food_life | 푸드 셰프 | 50대 통통한 셰프. 주황 반다나, 큰 검은 원형 안경, 하이넥 셰프복 + 주황 스카프, 쇠젓가락, 라면 그릇 | 음식 얘기에 황홀. 항상 배고픔 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094128_6068923f-3ebd-4b71-bbc2-60fcf7b9a9eb.png) |
| travel | 여행 백패커 | 활발한 젊은 여성. 웨이브 머리에 머스터드 비니, 대모갑 원형 안경, 턱까지 채운 틸색 바람막이, 카메라, 지도 | "저 거기 가봤어요!" 현장파 | [이미지](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_094128_0672aa18-1557-4d65-bb85-efe2500ff30c.png) |

### 스포츠 겸임 비교 심판: 애니메이션용 원본 (2026-09-28)
- KOREA VS WORLD 비교 심판을 스포츠 담당으로 겸임하는 안. 컨셉 `d2d5cb84-8332-485d-8a9f-df2405c4d4d4`를 참조로 gpt_image_2_5, 1:1, 회색 배경
- 원본: [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_165107_c5e59c4d-2984-453a-91ca-ccf2153ac3b4.png) `c5e59c4d-2984-453a-91ca-ccf2153ac3b4`, [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_165106_2fa7ec12-1a53-4cb8-bd68-810fb8ddb92b.png) `2fa7ec12-1a53-4cb8-bd68-810fb8ddb92b`, [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_165107_7d92559c-197b-48c5-8466-b9bda1657d77.png) `7d92559c-197b-48c5-8466-b9bda1657d77`
- `newsrig.analyze_head`로 확인: 안경알 두 개 안에 눈, 코 아래 입, 눈 깜빡임 정상. 원본 해상도 1024 (Kangfree는 2048)
- 목 위치: 스탠드업 칼라가 높아서 기본값(턱을 칼라 위 3%)이면 칼라가 긴 목처럼 보여 얼굴이 떠 보임 → 캐릭터 설정 `"chin_drop": 0.16` (턱을 머리 높이의 16%만큼 칼라 안으로. `dialog.py`, 기본 0.03)
- 눈: 컨셉 이미지처럼 **안경알 안쪽 전체를 흰색**으로 채우고 검은 눈동자 (`"white_lens": true`, `newsrig.draw_white_lenses`). 깜빡이면 피부가 위에서 덮고, 다 감으면 선이 안경테 위에 보임. 기존 캐릭터는 기본값(작은 흰 눈)을 유지
- 심판 캐릭터 설정 (사용자 OK): `"shoulders": 520, "head_ratio": 0.68, "chin_drop": 0.16, "white_lens": true`. 참고 이미지 자동 비율(0.58)은 Master K보다 작아 보여서 키움. 흰 안경알은 당분간 심판에게만
- 판정 패들은 손이 책상에 가려져서 몸통에서 뺌. 필요하면 설명 화면 그래픽으로
- 남은 것: 이름·성격·말버릇, 목소리, 실제 대사로 렌더링 테스트

### 데스크 전문가 7명: 애니메이션용 원본 (2026-09-28)
- 각 컨셉 이미지를 참조로 gpt_image_2_5, 1:1, 회색 배경. 공통 설정 `"shoulders": 520, "white_lens": true` (흰 안경알은 데스크 전문가 전원 + Whistle Joe에 적용, Master K·Dr. Kangfree는 기존 방식)
- 리그 확인: 7명 모두 안경알·코·턱 인식, 눈 뜸/반쯤/감기 정상, Master K 옆에 앉혀 머리 크기 비교
- 다시 뽑은 것: 시사 베테랑 머리(가는 돋보기 안경이라 안경알 인식 실패 → 중간 크기 사각 안경), K-POP 머리(입이 그려져 있었음)
- 시사 베테랑의 ref는 가는 돋보기 안경 그대로 (크기 비율 계산에만 쓰므로 문제없음)
- 리그 수정: 안경알 가로세로 비율 허용 1.5 → 1.8 (`newsrig.analyze_head`), 칼라 위치를 몸통 가운데에서만 잼 (`dialog.Puppet`, 테크 전문가 어깨 로봇 때문). 기존 캐릭터 결과는 그대로

| 데스크 | head | body | ref | 추가 설정 |
|---|---|---|---|---|
| 시사 베테랑 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_172010_98ee6a07-7734-4753-96e6-0b5a91fde7f6.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_54cc1983-d650-4b56-a2e3-90463392b6fd.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171718_8d457ae0-b9ec-4ace-9d67-ec5b28ae22d2.png) | "head_ratio" 자동(0.72) |
| K-POP 분석가 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_172010_d4b4123a-4902-4444-bfdf-8765f698db2d.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171719_f3663c92-2286-4259-bfab-6e1f6805358e.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_4cffa2cb-d2e4-4ddd-833c-0797fdb0dcdb.png) | 자동(0.69) |
| 비밀 기록 연구가 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_e1cc0cfa-b1c4-4ac3-a9c4-ef07c7d09d49.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_a7ab925d-7875-472e-b1eb-7c393c5fb22e.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_d3176932-0ab2-4cff-9de7-194e23534230.png) | 자동(0.66) |
| 머니 애널리스트 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_26dfccdd-4424-4ea7-825c-ed2c250642dc.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_94549376-7493-4a34-a337-93751110c81e.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171717_74bdfdab-b788-4cc4-b816-ac961492bd97.png) | "head_ratio": 0.68 |
| 테크·로봇 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_e03fc864-ae7f-4f00-a0cf-bd654a896fba.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_318c95ef-dae2-4a30-977e-f5a4b2f1f8ab.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_cea28273-31a5-4b36-b0d5-3dac4b1ebcdf.png) | "head_ratio": 0.68, "chin_drop": 0.08 |
| K-푸드 셰프 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_0bd12c40-1b8c-4b10-a8eb-5cfd71abb7a1.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_8f82a8f8-16f4-4463-81c1-dc2a894701b9.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171817_fb596434-ab49-4e73-94fd-962ea517bfad.png) | "head_ratio": 0.74, "chin_drop": 0.16 |
| 여행 백패커 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_ba5318d0-494b-4d31-b8ba-bf2f109d7cf6.png) | [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171849_209a0f95-d747-44fb-b7c3-1fd811e83c7d.png) | [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_171816_94e6999f-cd85-4a0b-ac2b-818200c55a79.png) | 자동(0.73) |

## 샷 자동 편집 (`prototypes/episode.py`)

줄마다 샷을 자동으로 정하고, 대본 줄에 `"shot"`을 적으면 그게 우선한다.

| 샷 | 화면 | 자동 규칙 |
|---|---|---|
| anchor_solo | 앵커 클로즈업 | 꼭지 첫 줄, 자료 없는 앵커 멘트 |
| anchor_screen | 왼쪽 설명 화면 + 오른쪽 앵커 | 앵커 줄에 `screen`이 있을 때 |
| screen_full | 설명 화면을 크게 | `screen` + `"big": true` |
| two_shot | 앵커와 패널 함께 (설명 화면 없음) | 패널의 첫 대사 |
| speaker_close | 말하는 사람 쪽으로 줌 | 대화 중 |
| wide | 데스크 전체 | 직접 지정할 때 |

- 앵커 단독 카메라(solo, screen, full)와 데스크 카메라(two_shot, close, wide)를 오갈 때는 컷, 같은 카메라 안에서는 부드러운 이동
- 같은 샷이 4초를 넘으면 천천히 줌인
- 롱폼 전용: 오른쪽 위 로고, 맨 아래 UP NEXT 티커 (쇼츠 크롭 밖)
- 예시 대본: `prototypes/segment_example.json` (꼭지 하나), `prototypes/episode_example.json` (에피소드)

### 에피소드 렌더링 (`prototypes/render_episode.py`)
- 에피소드 파일 = 공통(episode, characters, anchor) + `segments` 목록. 꼭지마다 category, desk, headline, hook, screens, lines, `short`
- `short`: `{"from": 줄번호, "to": 줄번호}`이면 그 구간만 쇼츠로, `false`면 쇼츠 없음, 생략하면 꼭지 전체
- TOPIC n/N, UP NEXT 티커(남은 꼭지 제목), 파일 이름은 자동. 꼭지별로 동시에 렌더링하고 롱폼은 이어 붙임 (재인코딩 없음)
- 속도: 최적화 후 영상 길이의 약 4배(로컬 4코어, 쇼츠 포함). 3꼭지 병렬이면 한 꼭지 시간과 비슷. 샌드박스 백그라운드 작업은 15분 제한이 있으니 에피소드가 길면 꼭지를 몇 개씩 나눠 실행

## 이어받기 메모 (2026-09-28 기준)

### 확정된 것
- 채널: **Four Eyes Report** (`@FourEyesReport`), 태그라인 "Through our lenses.", 브랜드에는 Korea를 넣지 않음. 대외 문구에 "nerd", "LIVE", "BREAKING" 금지
- 방향: 실제 한국 뉴스를 모아 외국인이 흥미를 갖도록 각색하고 **채널 운영자의 관점(한 줄 코멘트)**을 더한 병맛 애니메이션 뉴스쇼. 롱폼(5꼭지, TOPIC n/5)이 원본이고 꼭지별로 쇼츠를 잘라냄
- 앵커 A6 (**Master K**, 애칭 "Core", `docs/characters.md` 참고, 목소리 Miles/ElevenLabs `e18664a7-ee4f-5273-acf8-533eb24cd366`), 패널 **Dr. Kangfree** (이름표 DR. KANGFREE, 목소리 Skye/Seed Speech `1fb253b8-928b-4d29-a349-f242a71eaddf`, head_ratio 0.74, shoulders 500)
- 글꼴: Poppins Bold (`assets/fonts/Poppins-Bold.ttf`, OFL). 쇼츠 배경은 브랜드 남색 (4, 39, 87)
- 쇼츠: 위 여백은 훅 제목만, 가운데 영상(롱폼 중앙 1440×1080을 1080×810으로), 자막은 영상 안 아래쪽(y=1235), 아래 여백은 배너 띠(`prototypes/fer_promo_strip.png`) + 핸들
- 롱폼: 왼쪽 위 EP.n + 카테고리, 오른쪽 위 로고(쇼츠 영역 밖), TOPIC n/N 자막바, 맨 아래 UP NEXT 티커(쇼츠 영역 밖), 설명 화면 아래 출처 표기
- 샷은 `prototypes/episode.py`가 자동으로 정함 (위 "샷 자동 편집" 표)

### 첫 완성본 재료 (`prototypes/segment_example.json` 순서대로)
| 파일명 | 내용 | 주소 |
|---|---|---|
| a_head / a_body / a_ref.png | A6 머리·몸통·참고 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_074351_497d2899-66fc-40ea-8b60-1d4815c18eb6.png), [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_074350_480e7f2e-bde1-49fe-ad18-dfc5d2599626.png), [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_074351_5d746f9a-6b07-4adb-9eec-3936cf68fecf.png) |
| p_head / p_body / p_ref.png | 지영 박사 | [head](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084541_c67fcd43-9c73-473c-b29f-4be8a1cd81e5.png), [body](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084541_ec8bd826-58a3-4d75-bff3-18cce3c5a521.png), [ref](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084541_2a93c3aa-974e-40fb-b63a-26662d2f9796.png) |
| store_street.png / ramen_station.png | 설명 화면 | [s1](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_022533_b7aa6412-3dcd-4be2-9e45-87b4aa9cdeff.png), [s2](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_022533_547434ab-132c-4cc7-ac68-689e57cedf8d.png) |
| l1.mp3 | 앵커: Good evening. This is the Four Eyes Report… | [l1](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_121054_9749dded-0bfd-4b90-b7f6-ece59757dd9d.mp3) |
| l2.mp3 | 앵커: Korea has over fifty thousand of them… | [l2](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_121055_a108a222-c44e-42cb-b12f-7fab30207b6d.mp3) |
| l3.mp3 | 앵커: And inside some of them… a ramen cooking machine. | [l3](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_121054_02b3b80d-3194-4ff2-80b3-c6c8648cb8b8.mp3) |
| l4.mp3 | 지영: Wait. A machine? That cooks ramen? For you?! | [l4](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084544_89293f8a-e36f-43d7-a216-7d35bfdf62b5.mp3) |
| l5.mp3 | 앵커: Statistically speaking, yes. You press one button. | [l5](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084544_09e71b4f-0099-4c8c-abb7-d68abb0c1694.mp3) |
| l6.mp3 | 지영: I have been boiling water like a caveman… | [l6](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084545_37b38a26-8df5-4523-a364-f8f57041a35c.mp3) |
| l7.mp3 | 앵커: Doctor Jiyoung, please stay calm. This is a serious news program. | [l7](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_121053_a1a7739a-97b8-4ea5-90da-176b0069116c.mp3) |
| l8.mp3 | 지영: I am NOT calm! I'm booking a flight to Seoul! | [l8](https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/hf_20260928_084543_d08a3703-8f79-43e7-bceb-a2f0b404eb4a.mp3) |
| fer_logo_mark.png | 영상 로고 | [logo](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/ce946036-9821-419d-aae2-d107a3aef417.png) |

### 렌더링 방법
Higgsfield 샌드박스(`sandbox_exec`, ffmpeg·faster-whisper 있음)에서 돌린다.
1. `episode.py`, `dialog.py`, `newsrig.py`, `fer_promo_strip.png`, `Poppins-Bold.ttf`를 `media_upload`로 올리고, 로컬에서 PUT(`If-None-Match: *` 헤더 포함) 후 `media_confirm`
2. 샌드박스에서 위 파일과 재료를 curl로 받아 같은 폴더에 두고 `python3 episode.py segment_example.json` (긴 작업은 `background: true`)
3. 결과 mp4를 `media_upload` 주소로 PUT해서 공유
- 파일을 base64나 텍스트 조각으로 샌드박스에 넘기지 않는다
- 클라우드 환경 네트워크 허용 목록에 `upload.higgsfield.ai`, cloudfront 두 곳, 뉴스·Reddit·네이버·구글 API 도메인을 추가해 둠

### 첫 완성본 (2026-09-28)
- [롱폼 41초](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/4cf5b49b-fd01-4044-ac99-e63d9dd12e1d.mp4), [쇼츠](https://d2ol7oe51mr4n9.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU/bda8278b-31d1-4456-87a3-d23c218f70fe.mp4). 샷: 앵커 단독 → 앵커+화면 → 화면 크게 → 투샷 → 화자 클로즈업 ×4. 렌더링 약 5분
- 샌드박스를 재시작하면 `pip install opencv-python-headless`가 먼저 필요

### YouTube 업로드 설정 현황 (2026-09-28)
- Google Cloud 프로젝트 "Four Eyes Report", YouTube Data API v3 사용 설정, OAuth 앱 "Four Eyes Report Uploader" (테스트 상태, 범위 youtube / youtube.readonly / youtube.upload)
- 환경 변수 `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` 등록 후 새 세션에서 테스트
- ⚠️ **2026-10-05 전후:** refresh token 7일 만료 → OAuth Playground에서 재발급. 이때 **클라이언트 보안 비밀번호도 재설정** (첫 발급 때 캡처로 노출됨)
- ✅ 첫 업로드 테스트 성공 (2026-09-28): 첫 완성본 롱폼 41초를 **비공개**로 올림 → https://youtu.be/zCXqmUFMBKQ (채널 FourEyesReport, privacyStatus private, 처리 중). 명령: `pip install -r requirements.txt` 후 `PYTHONPATH=src python -m korea_decoded upload <mp4> --title ... --description <txt> --tags ... --privacy private`. 썸네일은 아직 테스트 안 함

### 채널 설정 (2026-09-28, API로 적용)
- 대상: 영미권 시청자. 유튜브 추천은 운영자 국적이 아니라 영상 언어·메타데이터·초반 시청자로 정해짐
- 적용함: 채널 설명(영어), 키워드, 채널 기본 언어 `en`, 국가 `KR`(거주 국가. 수익화·세금용이라 노출 지역과 무관, 미국으로 바꾸지 않음). 배너는 유지 확인
- 업로드 코드가 영상마다 언어 `en`, 카테고리 News & Politics, 아동용 아님을 넣음 → Studio 업로드 기본 설정은 안 바꿔도 됨
- 설명 원문: "Korea's stories, decoded for the rest of the world. / Four Eyes Report is an animated news show where a very serious anchor and a panel of experts break down what's happening in Korea — from convenience stores that cook your ramen to the numbers behind K-pop — so you get the context without the homework. / Through our lenses." (업로드 주기가 정해지면 "New episodes every week" 추가)
- 운영자가 직접 할 일: 채널 이름 `FourEyesReport` → `Four Eyes Report` (API로 못 바꿈, Studio → 맞춤설정 → 기본 정보)
- 아직: 브랜딩 워터마크(`fer_logo_mark.png`), 영어 자막 업로드(토큰에 `youtube.force-ssl` 범위 필요. 현재 토큰은 403. 재발급 때 Playground 범위에 추가)
- 운영 원칙: 첫 영상들은 한국 지인·커뮤니티보다 영어권 커뮤니티에 먼저 공유. 공개 시간은 KST 오전 8~10시(미 동부 전날 저녁)

### 다음 할 일 (순서대로)
1. 첫 완성본 연출 피드백 반영
2. 전문가 8명 중 확정 → 애니메이션용 원본(머리·몸통·참고) 제작
3. **뉴스 데스크 모듈**: 한국 뉴스·Reddit·트렌드 수집 → 같은 사건 묶기 → 외국인 관심도 채점 → 민감도(⚠️) → 아침 브리핑(후보 10개 + 추천 각도) → 운영자가 선택하고 "내 생각 한 줄" 입력
4. 에피소드 대본 형식(앵커·패널 대화, 꼭지별 screen/big/shot 지시)으로 대본 생성기 확장
5. 썸네일, 제목·설명 자동 생성, 유튜브 업로드(비공개 → 확인 후 공개), Google API 감사 신청
6. 새 저장소 `level40unlocked/four-eyes-report`로 이전 (운영자가 GitHub에서 빈 비공개 저장소를 만든 뒤)
7. 쇼츠의 가짜 SUBSCRIBE 그림을 "New episodes every week" 같은 문구로 바꿀지 결정 대기
