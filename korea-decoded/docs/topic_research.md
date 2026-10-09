# 주제 리서치: 레딧 (2026-09-29)

## 방법
- 레딧 본 사이트·우회 사이트는 클라우드에서 차단 → 레딧 아카이브 **Arctic Shift API** (`arctic-shift.photon-reddit.com/api/posts/search`, Higgsfield 샌드박스에서 접속)
- 대상: r/korea, r/Living_in_Korea, r/koreatravel, r/AskAKorean, r/hanguk, r/southkorea, r/seoul
- 제목에 why / normal / weird / true that / culture / how do koreans / strange / shock / explain 가 들어간 글, 2021-01 ~ 2026-08 (최근 한 달 글은 점수가 아직 안 쌓여서 제외)
- 1,589개 글 → 점수 + 댓글×3 순 정렬 → 주제별로 묶음
- 다시 돌리기: 이 문서 아래 "스크립트" 참고

## 결과: 반응 큰 질문 유형

| 주제 묶음 | 대표 글 (점수 / 댓글) | 에버그린 | 채널 적합 |
|---|---|---|---|
| **나이·호칭 언어** | "Why do Koreans say 'our' wife instead of 'my' wife?" (323/98), "Why do Koreans care so much about age?" (339/60) | ◎ | ◎ 개그·설명 둘 다 좋음 |
| **팁 문화 없음** | "Tipping culture fails to take hold in Korea" (1229/69, 179/41) | ◎ | ◎ 미국 시청자 공감 폭발 |
| **"이거 한국에서 정상이야?"** | 연애 1주 만에 "사랑해" (256/89), 아저씨가 지하철에서 아이에게 사탕 (94/95), 지하철에서 밀기 (39/73), 걷는 속도 (207/28), 모르는 사람이 말 걸기 (162/88) | ◎ | ◎ **고정 코너 후보** |
| **혼밥** | "How can I politely explain to my Korean colleagues that I enjoy eating alone?" (484/146) | ◎ | ◎ |
| **음주 문화 (그리고 변화)** | "Guide to Korean drinking culture" (401/34), "drinking culture is definitely changing" (301/80), 밤문화 쇠퇴 (266/48) | ○ | ◎ |
| **음식 나눠 먹기** | "Food sharing culture in Korea" (274/65) | ◎ | ◎ 푸드 캐릭터(Garden Clamsay) 데뷔용 |
| **이순신** | "Why is Admiral Yi Sun-sin ... still so little known?" (443/157) | ◎ | ○ 역사 스토리텔링, 한 편 통째로 가능 |
| **MBTI 집착** | "MBTI culture in Korea goes too far" (207/89) | ○ | ◎ 짧은 꼭지·쇼츠 |
| **결혼식 비용** | "72 Million Won in Wedding Costs Normal?" (127/50), 신라호텔 결혼식 (74/85) | ○ | ○ |
| **아파트** | "What is inside a high rise apartment in Korea?" (453/90), 아파트 이름 | ◎ | ◎ |
| **다이소·편의점 물건** | "Can someone explain to me what I bought at Daiso" (345/29), 밀키스 속 알갱이 (278/40) | ◎ | ◎ 쇼츠 |
| **인터넷 속 한국 이미지 왜곡** | (701/308) | ○ | △ 논쟁 많음 |

제외: 정치, 성소수자 행사, 인종·국가 갈등, 성(性) 관련 질문 → 댓글 싸움이 크고 광고 적합성·채널 톤과 안 맞음.

## 인사이트
1. 가장 반응 큰 형식은 **"Is this normal in Korea?"** (한국에서 이게 정상이야?). 외국인이 겪은 장면 + 설명. 매 편 고정 코너로 쓰기 좋음 (시청자 제보로 이어짐)
2. **언어·예절** 질문(나이, "우리", 호칭)은 오래 검색되고 댓글이 많음 → Korea Explained 설명편의 핵심
3. **돈·생활**(팁 없음, 결혼 비용, 아파트)은 미국 시청자가 자기 나라와 비교하며 댓글을 닮
4. 역사(이순신)는 반응이 크지만 제작이 무거움 → 나중에 특집

## EP.2 추천 구성 (8분+, 전부 에버그린)

제목 예: **"Things That Confuse Every Foreigner in Korea, Explained"** (한국에서 외국인이 다 헷갈리는 것들, 설명해 드림)

1. **Why Koreans ask your age first** (왜 한국인은 나이부터 물을까): 나이 → 존댓말, "형·언니", 한국 나이 폐지(2023)까지. "Our wife" 개그로 마무리
2. **No tipping in Korea** (한국엔 팁이 없다): 미국과 비교 숫자, 왜 자리 잡지 못했는지
3. **Is this normal? 코너**: 지하철 아저씨 사탕, 걷는 속도, 모르는 아주머니가 옷 정리해 줌 등 2~3개 속사포
4. **Eating alone (honbap)** (혼밥): 예전엔 이상하게 봤는데 지금은 1인 식당·혼밥 메뉴까지. K's Take로 마무리

쇼츠 4개: 꼭지별 하나씩 (나이·팁·정상?·혼밥)
뉴스 훅: 최신 통계가 있으면 한 줄만 ("As of 2026..."), 대본에 "this week / tonight" 쓰지 않음

## 스크립트 (Higgsfield 샌드박스에서)
```python
# GET https://arctic-shift.photon-reddit.com/api/posts/search
#   ?subreddit=korea&title=why&limit=100&after=2021-01-01&before=<epoch>&sort=desc
#   &fields=id,title,score,num_comments,subreddit,created_utc
# title 검색은 subreddit 또는 author가 꼭 있어야 함. 이전 페이지 마지막 created_utc를 before로 넘겨 페이지 넘김
```
