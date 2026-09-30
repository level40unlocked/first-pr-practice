# 캐릭터 아이덴티티 (초안 v1)

대본 생성기와 목소리 디자인의 기준. 개그는 성격에서 나오고, 국적이나 특정 집단을 웃음거리로 삼지 않는다.

## 앵커: Master K (마스터 케이) · A6 ✅ 이름 확정

| 항목 | 내용 |
|---|---|
| 한 줄 | 모든 뉴스를 숫자로 설명할 수 있다고 믿는, 스타일 좋은 데이터 덕후 앵커 |
| 이름 | 공식 이름 **Master K** (발음 "마스터 케이"). **K는 KOR(한국)를 뜻함**. 본명은 방송에서 밝히지 않음 |
| 애칭 | Dr. Kangfree와 패널들은 **"Core"(코어)**라고 부름. K → KOR → "코어"로 한국과 핵심(core)의 의미가 한 번에 담김 |
| 애칭의 유래 (확정) | 첫 방송 날 데스크 명찰이 **"MASTER KOR"**로 잘못 인쇄됨. 다들 "코어"로 읽어서 그대로 별명이 됨. 본인은 매번 "It's *K*."라고 정정하지만 아무도 안 들어줌 |
| 나이, 배경 | 31세. 서울 출신, 해외에서 공부하고 돌아옴(그래서 영어가 유창함). 통계 연구원으로 일하다가 "숫자를 사람 말로 번역하는 사람"이 되고 싶어 앵커가 됨 |
| 성격 | 차분함, 무표정 유머(deadpan), 정확성 집착. 겉은 쿨하지만 사소한 것에 크게 흔들림 |
| 말버릇 | "Let's look at the numbers." / "Technically…" / 이상하게 정확한 숫자 ("fifty-one point six percent") / 괄호 속 TMI |
| 오프닝 | ✅ **"Hello, world."** 고정 (프로그래밍 첫 출력 문장 + 세계 시청자에게 하는 인사, 시간대를 타지 않음) → 이번 회 한 줄(선택) → "I'm Master K, and this is the Four Eyes Report." → 오늘의 메뉴("Coming up: …"). 아래 "오프닝 한 줄 후보" 참고 |
| 클로징 | "Stay curious. Keep your lenses clean." ✅ 확정 |
| 반복 개그 | ① "Core" 정정 ("It's K. It has always been K.") ② "This is a serious news program." (아무도 안 믿음) ③ 팩트를 말하기 전에 안경을 고쳐 씀 ④ 몰래 K-드라마를 보고 우는데 절대 인정 안 함 |
| 역할 | 사실 전달, 진행, 꼭지 마무리. 운영자의 관점은 **"K's Take"** 코너로 전함 |
| 약점 | 요리를 못함, 즉흥 상황에 약함, Dr. Kangfree의 에너지에 늘 밀림 |
| 목소리 | ✅ **Miles** (ElevenLabs, `e18664a7-ee4f-5273-acf8-533eb24cd366`). 목표 느낌: 30대 초반 남성. 맑고 약간 빠른 말투, 또박또박한 자음, 건조한 톤. 데이터 얘기가 나오면 살짝 높아지고 빨라짐. 자연스러운 북미 영어 |
| 표기·발음 규칙 | 대본·자막·이름표는 **Master K** / 패널 대사는 **Core** / 음성 생성 때 "Master K"는 자동으로 "Master Kay"로 바뀜 (`config/channel.toml`의 `[pronunciation]`) |

## 패널: Dr. Kangfree (캉프리 박사) · C ✅ 이름 확정

| 항목 | 내용 |
|---|---|
| 이름 | 방송 이름 **Dr. Kangfree**. 이름표 **DR. KANGFREE**. 성 강(Kang) + free. 토크쇼의 여왕 오프라 윈프리(Winfrey)를 떠올리게 하는 심슨식 패러디이고, "free"는 자유분방한 성격을 뜻함. 외모, 말투, 유명 멘트는 원조를 따라 하지 않음 |
| 호칭 | 모두 **"Dr. Kangfree"**라고 부름. 덤 개그: "-free"는 "~가 없는"이라는 뜻 (sugar-free처럼). 예: Kangfree "Let's make this a Core-free zone!" / K "…You're literally named Kang-free." |
| 한 줄 | 한국 사람들의 일상을 연구하는데, 연구할 때마다 새삼 놀라는 흥분형 사회학자 |
| 나이, 배경 | 34세. 한국에서 태어나 어릴 때 해외로 이민 간 교포. 해외 대학에서 "일상 문화"를 연구. 한국을 **안과 밖에서 동시에** 보는 사람이라 외국인 시청자의 놀라움을 대신 표현함 |
| 성격 | 호기심 폭발, 과한 리액션, 즉흥적. 통계만 보면 신남. 따뜻하고 공감을 잘함 |
| 말버릇 | "Wait. WAIT." / "That is SO Korean. I love it." / "I have a chart for this!" |
| 반복 개그 | ① 어디선가 차트를 꺼냄 ② 머리에 꽂은 연필을 찾다가 못 찾음 ③ 흥분하면 바로 "I'm booking a flight to Seoul!" |
| 역할 | 리액션, 사람 이야기와 맥락 보충, 외국인 시청자 입장에서 질문 |
| 목소리 | ✅ **Chloe** (ElevenLabs, `e9cfbbf0-4476-46be-b396-596eb774b165`, 2026-09-29 운영자 선택). 목표 느낌: 30대 여성. 밝고 빠르고 표정이 풍부한 톤, 잘 웃음, 흥분하면 목소리가 커짐. 자연스러운 북미 영어. 변경 이력: Skye(Seed Speech, 억양이 너무 평평함) → Juno → Chloe(후보 13개 비교 후 운영자가 고름). 음량은 줄마다 앵커 평균에 맞춘다 |

## 데스크 전문가: Whistle Joe (휘슬 조) · KOREA VS WORLD + 스포츠 ✅ 이름 확정

| 항목 | 내용 (이름 외에는 초안) |
|---|---|
| 이름 | **Whistle Joe**. 이름표 **WHISTLE JOE**. 다들 "Joe"라고 부름 |
| 한 줄 | 세상 모든 걸 경기로 보고 판정해야 직성이 풀리는 열혈 심판 |
| 담당 | 스포츠 + KOREA VS WORLD 비교 |
| 배경 | 29세. 동네 유소년 리그 심판 출신. 경기가 없는 날에도 호루라기를 목에 걸고 다님 |
| 성격 | 에너지 넘침, 공정함에 집착, 승부욕. 판정은 늘 칭찬으로 끝나는 착한 사람 |
| 말버릇 | "Let's go to the replay!" / "And the point goes to… KOREA!" / "That's a foul." |
| 반복 개그 | ① 흥분하면 말보다 호루라기가 먼저. K: "Joe. Indoors." ② K가 TMI를 말하면 판정 패들을 들며 "Offside!" ③ 비기면 본인이 더 괴로워함 |
| 목소리 방향 | 20대 후반 남성. 스포츠 중계 톤, 빠르고 크게, 판정할 때 한 박자 멈춤. 자연스러운 북미 영어 |
| 리그 설정 | `"shoulders": 520, "head_ratio": 0.68, "chin_drop": 0.16, "white_lens": true` (원본은 `show_bible.md`) |

## 데스크 전문가: Garden Clamsay (가든 클램지) · K-FOOD & LIFE ✅ 이름 확정 (2026-09-29)

| 항목 | 내용 |
|---|---|
| 이름 | **Garden Clamsay**. 이름표 **CHEF CLAMSAY**. 첫 등장 때 Master K가 풀네임으로 소개. 셰프 고든 램지(Gordon Ramsay)를 비튼 심슨식 이름 패러디: Garden(텃밭, 채소) + Clam(조개, 해산물) |
| 외모 | 기존 K-푸드 셰프 원본 그대로: 50대 통통한 셰프, 주황 반다나, 큰 둥근 안경(흰 안경알), 흰 셰프복 + 주황 스카프. 원본 링크는 `show_bible.md` "데스크 전문가 7명" 표. 설정 `"head_ratio": 0.74, "chin_drop": 0.16, "white_lens": true` |
| 표정 | **기본은 인상 쓴 얼굴** (`"mood": "frown"`: 비스듬한 눈꺼풀, 굵은 눈썹, 입꼬리 내림). 음식에 무너지는 순간만 대사에 `"mood": {"chef": "neutral"}`로 풀어 줌 |
| 성격·개그 | 독설가인 척하지만 **한국 음식 앞에서는 한 번도 화를 못 냄**. 매번 "This is going to be terrible..."처럼 엄하게 시작 → 한 입 먹고 감동해서 무너짐. 요리 못하는 Master K와 붙으면 자연스러운 대립 |
| 조심할 것 | 원조를 따라 하지 않음: 금발·원조 얼굴 특징 금지, 원조 유명 대사("It's RAW!", "idiot sandwich" 등)와 방송 포맷(Hell's Kitchen 등) 사용 금지, 원조가 보증·관련된 것처럼 보이게 하지 않음 |
| 목소리 | 미정 (남성, 50대, 굵고 거친 톤 → 감동할 때 떨리는 목소리가 잘 나오는 목소리로 고를 것) |

## 데스크 전문가: Billie Dusk (빌리 더스크) · TECH ✅ 이름 확정 (2026-09-30)

| 항목 | 내용 |
|---|---|
| 이름 | **Billie Dusk**. 이름표 **BILLIE DUSK**. 빌 게이츠(Bill → Billie) + 일론 머스크(Musk → Dusk) 패러디. Dusk(해 질 녘)는 스튜디오 배경인 서울 노을, 밤새 코딩하는 천재 느낌과도 연결 |
| 외모 | 기존 테크 전문가 원본 그대로: 젊은 여성, 청록 브릿지 픽시컷, 굵은 청록테 안경, 하이넥 테크웨어, 어깨 위 작은 로봇. 설정 `"shoulders": 520, "head_ratio": 0.68, "chin_drop": 0.08, "white_lens": true` |
| 성격·개그 | 무표정 천재. 본인은 반응이 없고 **어깨 위 로봇이 대신 리액션**. 로봇 이름 후보 "Kimbot" (미확정) |
| 조심할 것 | 이름만 비틈. 원조 두 사람의 말투, 정치적 발언, 사업 이슈를 개그로 쓰지 않음 |
| 목소리 | 미정 |

## 두 사람의 관계
- 대학원 시절 같은 연구실 선후배. K는 "정리하는 사람", Dr. Kangfree는 "어지르는 사람". Dr. Kangfree가 "Core" 별명을 가장 열심히 퍼뜨림
- K는 Dr. Kangfree를 진정시키려 하지만 결국 같이 흥분함 (쇼의 기본 개그 구조: **무표정 vs 폭주**)
- 서로 진심으로 존중함. 말싸움은 하되 비꼬거나 무시하지 않음

## 오프닝 한 줄 후보 ("Hello, world." 뒤에 붙임, 매회 바꿈)
1. Some news is big. Some news is weird. Tonight, most of it is both. (EP.1 사용)
2. The world keeps asking, "What is going on in Korea?" We have answers. And graphs.
3. From Seoul, where the news is fast, the internet is faster, and we are... thorough.
4. Korea made a lot of headlines this week. We read all of them. Including the footnotes.
5. If it happened in Korea this week and made us say "wait, what?", it's on tonight's show.
6. You bring the curiosity. We bring the glasses.
7. We've cleaned our lenses, checked our facts, and hidden Dr. Kangfree's coffee. (Kangfree: "You did WHAT?")
8. We're not the fastest news in Korea. But we do have the thickest glasses.
9. Other channels bring you the news first. We bring it second, with charts.
10. Tonight I've prepared forty-one charts. We will use three.
- 가끔 변주 (에피소드당 한 번): "Hello, world. And hello, Bukang-i." 같은 주제 인사 / Kangfree: "Why do you always say it like a computer booting up?" K: "Because I am fully loaded."

## 잡담 규칙
- 꼭지 사이 연결, 무거운 꼭지 뒤 분위기 전환, 클로징 뒤 한마디에 넣음. 한 번에 10~20초, 에피소드당 3~5번
- 쇼츠 구간 밖에만. 앞 꼭지의 개그를 이어받는 콜백이면 가장 좋음

## 반복 개그 사용 규칙
- 고정 개그(Core ↔ "It's K" 정정, "This is a serious news program", "Wait. WAIT.", "I'm booking a flight to Seoul!", Joe의 호루라기 등)는 **한 에피소드에 각각 한 번**까지. 자주 나오면 뻔해짐 (EP.2 초안 피드백)
- 말버릇("Let's look at the numbers", "Technically…")은 한 에피소드에 두 번까지, 서로 다른 꼭지에
- 고정 개그는 가능하면 쇼츠로 잘리는 구간 안에 둠. 쇼츠만 보는 시청자도 캐릭터를 알 수 있게
- 호칭 "Core"도 개그가 나오는 장면에서만 씀. 평소에는 이름 없이 말함

## 에피소드 속 역할 흐름 (기본형)
1. K: 오프닝, 뉴스 사실 전달 (설명 화면)
2. Dr. Kangfree: 놀람, 리액션, 사람 이야기 덧붙이기
3. 둘의 짧은 티키타카 (개그)
4. K: "K's Take" (운영자의 한 줄 관점) + 다음 꼭지로

## 정해야 할 것
- ~~패널 이름~~ → Dr. Kangfree 확정, 해외 거주(교포) 설정 유지
- 기존 녹음 대사 "Doctor Jiyoung, please stay calm."은 다음 녹음 때 "Dr. Kangfree, please stay calm."으로 교체
- ~~클로징 멘트~~ → 확정
- ~~목소리~~ → Master K = Miles, Dr. Kangfree = Chloe 확정 (Skye → Juno → Chloe) (`config/channel.toml`의 `[cast.*]`). 캐릭터 느낌은 대사와 연출로 살리고, 채널이 자리 잡으면 전용 목소리 검토
- 전문가 8명의 아이덴티티 (확정된 캐릭터부터)
