# EP.1 업로드 설정 (초안)

영상: `ep01_long.mp4` (6:54) + 쇼츠 4개 (`ep01_s1~s4_short.mp4`)
공개 시간: **금요일 KST 새벽 3~4시 예약 공개** (미 동부 오후 2~3시). 쇼츠는 다음 날부터 하루 1개

## 1. 제목 (후보, 첫 60자 안에 핵심)

1. **A Shark Moved Into a Busan Canal. Half a Million People Came.** ← 추천
2. Korea Named a Lost Shark. 570,000 Fans Showed Up.
3. Korea's Weirdest Week: A Shark Fandom, Zero Typhoons & Psy

- 에피소드 번호는 제목에 넣지 않음 (처음 보는 사람에게 의미 없음). 설명과 재생목록으로 구분
- 가장 강한 꼭지(상어) 하나로 제목을 잡고, 나머지 꼭지는 설명·챕터에서 보여 줌

## 2. 설명 (영어)

```
A 3.5-meter shark wandered into a canal in Busan, refused to leave, got a nickname — and pulled in more than half a million visitors. Plus: why Korea's typhoon-free summer is worse news than it sounds, Psy headlining Gangnam's new festival, and the appliance you can now subscribe to.

Four Eyes Report is an animated news show about Korea, for everyone who isn't in Korea.

CHAPTERS
0:00 Hello, world
0:21 The shark that refused to leave (Busan)
2:02 No typhoons this summer — and why that's bad
3:37 Gangnam wants to be the world's K-festival (Psy!)
5:07 In Korea, you can subscribe to your air conditioner

SOURCES
Busan North Port shark visitor figures: Busan Infrastructure Corp. via Yonhap
Typhoon tracks: NOAA IBTrACS · Maps: Natural Earth, © OpenStreetMap contributors
(나머지 출처는 대본 사실 확인 목록에서 채움)

PHOTO & IMAGE CREDITS
Satellite images: NASA
Photo: laszlo-photo (CC BY 2.0) · Illustration: Queensland State Archives (public domain)
Photos: Joop, Prayitno, sellyourseoul, sodai gomi, x768, pcamp (CC BY 2.0) · Aspere (CC0)
Photos: Link576, Wonderlane, Joanna Bourne, dejankrsmanovic, espensorvik, DoNotLick (CC BY 2.0) · Kojotisko (CC0)
Photos: SYLFTCunningLinguist, NASA Goddard Photo and Video (CC BY 2.0) · Lionello DelPiccolo, bartoszjanusz (CC0)
CC BY 2.0: https://creativecommons.org/licenses/by/2.0/
Illustrations marked "AI-generated illustration" on screen are AI-generated. Characters are animated; voices are synthetic.

#Korea #KoreaNews #Busan
```

## 3. 기본 설정

| 항목 | 값 | 이유 |
|---|---|---|
| 공개 범위 | 먼저 **비공개** → 확인 후 예약 공개 | |
| 아동용 | 아니요 | 아동용이면 댓글·추천이 막힘 |
| 카테고리 | **Entertainment** (추천) 또는 News & Politics | 개그 뉴스쇼라 엔터테인먼트가 추천 흐름에 더 맞음. 지금 업로드 코드는 News & Politics |
| 영상 언어 / 제목·설명 언어 | 영어 (en) | 영어권 추천의 핵심 신호 |
| 자막 | 영어 자막 파일(SRT) 업로드 | 대본과 단어 타이밍이 있어 정확한 자막을 자동으로 만들 수 있음 |
| 태그 | korea, korean news, busan, shark, typhoon, gangnam, psy, samsung, subscription, animated news | 태그 영향은 작음. 오타·동의어 보완용 |
| 변경된 콘텐츠(AI) 표시 | **아니요** (현재 기준) | 실제로 착각할 만한 사실적 인물·사건 영상이 아님(만화 캐릭터, "AI-generated illustration" 표기). 실존 인물 목소리·얼굴을 만들면 **예** |
| 라이선스 | 표준 YouTube 라이선스 | |
| 댓글 | 켬, 부적절 가능성 있는 댓글 검토 대기 | |
| 재생목록 | "Four Eyes Report — Full Episodes" | |

## 4. 썸네일 ✅ 확정 (2026-09-29)

"테스트 및 비교"(A/B)에 3개 등록. 문구·그림은 같고 캐릭터·포즈만 다름 → 어떤 캐릭터가 클릭을 부르는지 비교
1. `thumbs/thumb_G.jpg` Master K 놀람 + 수로 상어 + **"A SHARK IN THE CITY?!"** (기본)
2. `thumbs/thumb_J.jpg` Kangfree 가리키기 포즈 + 같은 그림·문구
3. `thumbs/thumb_I.jpg` Kangfree 양손 볼 OMG 포즈 + 같은 그림·문구

- 공통: 🇰🇷 BUSAN, KOREA 배지, 상어 위 "부캉이 / BUKANG-I" 이름표(썸네일 그림 속 한글은 필요할 때만), 서울 노을 배경, 오른쪽 위 안경 로고
- 다시 만들기: `cd episodes/ep01 && python3 ../../prototypes/thumbnail.py thumbs/thumb_G.json thumbs/thumb_G.jpg`
- 결과(클릭률)는 1~2주 뒤 확인해서 EP.2 썸네일 기본 캐릭터·포즈 결정

## 5. 최종 화면 · 카드

- 최종 화면(마지막 5~20초): 다음 영상 + 구독 버튼. 지금 영상은 마지막 대사까지 캐릭터가 나와서 가려짐 → **롱폼 끝에 15초짜리 아웃트로 화면을 붙이는 것 추천**
- 카드: 영상이 늘어나면 관련 꼭지 영상으로 연결 (지금은 없음)

## 6. 쇼츠 4개

- 롱폼 공개 뒤 하루 1개씩 올림
- 각 쇼츠의 **관련 동영상**을 이 롱폼으로 지정 (끝 화면 "Full episode on our channel"과 연결)
- 제목은 각 쇼츠 상단 문구를 그대로: "A shark got stuck in a Busan canal. It refused to leave" 등
