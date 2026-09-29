"""Builds script.json (render input) and script_ko.md (Korean review sheet) from one source."""
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))

# (who, text, ko, note, extras)  note = why the line should land for an English-speaking viewer
SEGMENTS = [
 {
  "key": "bukang", "category": "travel", "desk": "BUSAN",
  "headline": "A shark moved into a Busan canal and half a million people came to see it",
  "hook": "A shark got stuck in a Busan canal.\nIt refused to leave",
  "sensitivity": "go",
  "screens": {
   "s1": {"image": "bukang_canal.png", "label": "BUSAN NORTH PORT", "credit": "AI-generated image",
          "desc": "부산 북항 친수공원의 좁은 수로, 수로 안에 상어 지느러미, 난간에 몰린 구경꾼들 (AI 이미지, 실제 사진 아님)"},
   "s2": {"image": "bukang_numbers.png", "label": "BY THE NUMBERS", "credit": "Source: Busan Infrastructure Corp. via Yonhap",
          "desc": "숫자 카드: 568,800명(9/19~) / 하루 최다 140,000명 / 평소 휴일 하루 약 2,000명 → x50"},
  },
  "lines": [
   ("anchor", "Hello, world. Some news is big. Some news is weird. Tonight, most of it is both. I'm Master K, and this is the Four Eyes Report.",
    "헬로, 월드. 큰 뉴스가 있고, 이상한 뉴스가 있습니다. 오늘은 대부분 둘 다입니다. 마스터 K, 포 아이즈 리포트입니다.",
    "고정 인사 'Hello, world'(프로그래밍 첫 출력 문장, 세계 시청자에게 하는 인사) + 이번 회 한 줄", {}),
   ("anchor", "Coming up: a shark that won't leave, a typhoon that never came, Psy, and a refrigerator you can date. Let's begin.",
    "오늘은 떠나지 않는 상어, 오지 않은 태풍, 싸이, 그리고 사귈 수 있는 냉장고. 시작하겠습니다.",
    "오늘의 메뉴. 뒤에 나올 꼭지를 미리 알려 끝까지 보게 함", {}),
   ("anchor", "Our top story: a shark. In a canal. In the middle of a city.",
    "오늘의 톱뉴스는… 상어입니다. 도심 한복판 수로에 있는.",
    "진지한 톱뉴스 톤으로 '상어'를 발표하는 것 자체가 개그. 마침표로 끊어 읽는 리듬이 핵심", {}),
   ("anchor", "Ten days ago, a three-and-a-half-meter shark swam into a narrow canal at Busan's North Port. And then it just... stayed.",
    "열흘 전, 3.5미터짜리 상어가 부산 북항의 좁은 수로로 들어왔습니다. 그리고… 그냥 눌러앉았습니다.",
    "'just... stayed' 한 박자 멈춤. 사람처럼 묘사하는 의인화가 이 꼭지 전체의 뼈대", {"screen": "s1"}),
   ("anchor", "Officials tried to guide it back to the sea. The shark declined.",
    "당국이 바다로 돌려보내려 했지만, 상어가 거절했습니다.",
    "'declined(정중히 거절했다)'는 사람이나 회사에 쓰는 말. 상어에게 쓰니 웃김. 영어권에서 잘 먹히는 과장 없는 건조한 개그", {}),
   ("panel", "It DECLINED? Core, a shark cannot decline things.",
    "거절했다고요? 코어, 상어는 뭘 거절할 수가 없어요.",
    "Dr. Kangfree가 시청자 대신 태클. 'Core' 호칭 개그는 이 에피소드에서 여기 한 번만", {}),
   ("anchor", "It's K. And technically, it can. It simply did not leave.",
    "K입니다. 그리고 엄밀히 말하면 할 수 있습니다. 그냥 안 나갔으니까요.",
    "K의 고정 개그 두 개(이름 정정 + 'Technically')를 한 줄에. 반복 시청자에게 보상", {}),
   ("panel", "What kind of shark is it, anyway?",
    "근데 무슨 상어예요?", "", {}),
   ("anchor", "Probably a dusky shark. Or a copper shark. It declined to comment.",
    "아마 흑상어요. 아니면 무태상어. 본인이 답변을 거절했습니다.",
    "5번 'The shark declined' 콜백. 종은 보도상 '추정'이라 Probably로 말함", {}),
   ("anchor", "So Korea did what Korea does. It gave the shark a nickname: Bukang-i. That's 'North Port', plus a cute little 'ee' on the end.",
    "그래서 한국은 한국다운 일을 했습니다. 상어한테 별명을 붙였죠. 부캉이. '북항'에 귀여운 '이'를 붙인 겁니다.",
    "한국어 애칭 접미사 '-이'를 설명하는 '한국 해설' 포인트. 외국인이 몰랐던 걸 알게 되는 만족감", {"screen": "s1"}),
   ("panel", "Wait. WAIT. It has a nickname? Does it have a FANDOM?",
    "잠깐, 잠깐만요. 별명이 있다고요? 팬덤도 있어요?",
    "Kangfree 말버릇 'Wait. WAIT.' + K-POP 팬덤 문화를 아는 시청자용 연결", {}),
   ("anchor", "Let's look at the numbers. Five hundred sixty-eight thousand, eight hundred visitors. Over the Chuseok holiday, one hundred forty thousand people came in a single day.",
    "숫자를 보시죠. 방문객 56만 8,800명. 추석 연휴에는 하루에만 14만 명이 왔습니다.",
    "K가 이상할 만큼 정확한 숫자를 끝까지 읽는 캐릭터 개그. 팬덤 질문에 숫자로 '그렇다'고 답하는 구조", {"screen": "s2", "big": True}),
   ("anchor", "On a normal holiday, this park gets about two thousand. That is a fiftyfold increase. For one shark.",
    "이 공원은 평소 휴일에 2천 명 정도 옵니다. 50배입니다. 상어 한 마리 때문에.",
    "'For one shark.' 짧은 마무리 펀치", {"screen": "s2"}),
   ("panel", "Half a million people in ten days? That's not a shark. That's a stadium tour.",
    "열흘에 50만 명? 그건 상어가 아니라 스타디움 투어예요.",
    "상어를 월드투어 도는 아이돌에 빗댐. 쇼츠 댓글 유도용 한 줄", {}),
   ("anchor", "The good news: scientists say Bukang-i is calm and healthy. Starting Tuesday morning, boats and water pumps will gently guide it back out to sea.",
    "다행히 전문가들은 부캉이가 건강하고 안정적이라고 합니다. 화요일 아침부터 배와 양수기로 조심스럽게 바다로 안내할 예정입니다.",
    "동물이 위험한 상황이라 여기서 개그를 멈추고 안심시키는 정보. 동물 걱정하는 시청자 배려", {}),
   ("panel", "So it's the farewell tour.",
    "그럼 이제 고별 투어네요.",
    "앞의 '스타디움 투어'를 받는 콜백. 짧아서 웃음이 남음", {}),
   ("anchor", "K's Take: Only in Korea does a lost shark get a name, half a million fans, and a proper send-off. Bukang-i, safe travels.",
    "K의 한마디: 길 잃은 상어가 이름, 50만 팬, 제대로 된 배웅까지 받는 건 한국뿐입니다. 부캉이, 잘 가.",
    "[운영자 확인] K's Take는 운영자 관점 자리. 초안이니 바꿔 주세요", {}),
  ],
  "short": {"from": 4, "to": 11},
  "fact_checks": [
   "구조 작전 결과(9/29 화요일 오전 10시 시작 예정): 업로드 전에 결과를 확인하고 11~13번 대사를 과거형이나 결과로 바꿀 것. 연합뉴스 후속 보도",
   "3.5m, 9/18 첫 발견, 9/19부터 568,800명, 추석 4일 483,000명·하루 최다 140,000명, 평소 약 2,000명(부산시설공단 발표, 연합뉴스 2026-09-28)",
   "'부캉이' = 북항 + '-이' (연합뉴스)",
   "종: 무태상어(copper shark) 또는 흑상어(dusky shark)로 추정 (서울신문 등). 확정되면 대사 수정",
   "국립수산과학원 현장 점검: 활동·호흡 안정 (연합뉴스)",
  ],
 },
 {
  "key": "typhoon", "category": "current_affairs", "desk": "WEATHER",
  "headline": "No typhoon hit Korea this summer, and that is not all good news",
  "hook": "Korea had ZERO typhoons this year.\nWhy scientists are worried",
  "sensitivity": "review",
  "sensitivity_reason": "양식장 피해(물고기 773만 마리 폐사, 252억 원 손실)와 가뭄을 다룸. 피해를 웃음 소재로 쓰지 않도록 9~12번은 진지한 톤으로 씀. 운영자 확인 필요",
  "screens": {
   "s1": {"image": "typhoon_map.png", "label": "THE BOUNCERS", "credit": "Illustration based on KIOST report",
          "desc": "동아시아 지도 그래픽: 한반도 주위를 두 고기압(북태평양, 티베트)이 클럽 경비원처럼 막고 있고, 태풍 '돌핀' 화살표가 상하이로 방향을 트는 그림"},
   "s2": {"image": "typhoon_ocean.png", "label": "WHY IT MATTERS", "credit": "Source: KIOST, Korea Herald",
          "desc": "바다 단면 그래픽: 태풍이 차갑고 산소 많은 물을 섞어 올리는 모습 vs 섞이지 않고 뜨거운 표층. 숫자: 3년 평균 2.33개(장기 평균 대비 -28.6%), 강수량 평년의 84.8%"},
  },
  "lines": [
   ("panel", "Okay. A shark that won't leave. What's next, weather that won't arrive?",
    "좋아요. 안 떠나는 상어. 다음은 뭐예요, 안 오는 날씨?",
    "[잡담] 꼭지 사이 연결. Kangfree가 다음 꼭지를 우연히 맞힘", {}),
   ("anchor", "...Did you read my script?",
    "…제 대본 보셨어요?",
    "[잡담] K가 당황하는 짧은 반응", {}),
   ("anchor", "Next: the weather. Or rather, the weather that never showed up.",
    "다음은 날씨입니다. 정확히는, 끝내 오지 않은 날씨요.", "짧은 반전 도입", {}),
   ("anchor", "This year, not a single typhoon has made landfall in Korea. Not one.",
    "올해 한국에 상륙한 태풍은 단 하나도 없습니다. 하나도요.", "", {"screen": "s1"}),
   ("panel", "That's amazing! A free summer! Why do you look worried?",
    "대박! 공짜 여름이네요! 근데 왜 걱정하는 얼굴이에요?", "시청자의 첫 반응을 대신 말함", {}),
   ("anchor", "I always look like this. But yes, I'm worried.",
    "저는 원래 이 얼굴입니다. 하지만 네, 걱정됩니다.",
    "무표정 캐릭터의 자기 개그. 영어권에서 흔히 먹히는 deadpan 셀프 디스", {}),
   ("anchor", "For three summers now, two giant high-pressure systems, one from the Pacific and one from Tibet, have parked around Korea like bouncers outside a club.",
    "3년째 여름마다, 태평양과 티베트에서 온 거대한 고기압 두 개가 클럽 앞 경비원처럼 한반도를 막고 있습니다.",
    "어려운 기상 개념을 '클럽 경비원(bouncer)'으로 바꾼 비유. 이 꼭지의 핵심 이미지", {"screen": "s1", "big": True}),
   ("anchor", "In August, Typhoon Dolphin crossed the Pacific, saw the line at the door, and headed toward Shanghai instead.",
    "8월에는 태풍 돌핀이 태평양을 건너오다가, 입구 줄을 보고는 상하이 쪽으로 방향을 틀었습니다.",
    "경비원 비유를 이어서 태풍을 입장 못 한 손님처럼 묘사", {"screen": "s1"}),
   ("panel", "Rejected at the door. Brutal.",
    "입구컷. 잔인하네요.", "짧은 리액션 펀치", {}),
   ("anchor", "Here's the catch. Typhoons stir up the ocean. They mix cold, oxygen-rich water from below with the warm water on top. Scientists call them the ocean's ventilation system.",
    "문제는 이겁니다. 태풍은 바다를 휘저어서, 아래의 차갑고 산소 많은 물을 위의 따뜻한 물과 섞어 줍니다. 과학자들은 태풍을 바다의 환기 장치라고 부릅니다.",
    "여기서부터 톤 전환. 정보 전달", {"screen": "s2"}),
   ("panel", "So the ocean spent all summer in a stuffy room with the windows shut.",
    "그러니까 바다가 여름 내내 창문 닫힌 답답한 방에 있었던 거네요.",
    "Kangfree가 비유로 정리해 주는 역할. 가벼운 톤은 여기까지", {}),
   ("anchor", "Exactly. And fish farms are feeling it. Along the southern coast, about seven point seven million farmed fish have died this year. Rainfall is down about fifteen percent, and parts of the country are in drought.",
    "맞습니다. 양식장도 피해를 보고 있습니다. 남해안에서 올해 양식 물고기 약 773만 마리가 폐사했고, 강수량은 평년보다 15% 정도 적어 일부 지역은 가뭄입니다.",
    "피해 사실은 개그 없이 전달", {"screen": "s2"}),
   ("panel", "Okay. That's not a free summer at all.",
    "그렇다면… 전혀 공짜 여름이 아니었네요.",
    "3번 대사('free summer')를 뒤집는 콜백. 웃음이 아니라 여운", {}),
   ("anchor", "And experts warn: fewer typhoons can mean stronger ones later. Warm water is fuel.",
    "그리고 전문가들은 태풍이 줄면 나중에 오는 태풍이 더 강해질 수 있다고 경고합니다. 따뜻한 바닷물은 연료니까요.", "", {}),
   ("anchor", "K's Take: A quiet summer isn't always a good summer. Sometimes the calm is the story.",
    "K의 한마디: 조용한 여름이 늘 좋은 여름은 아닙니다. 때로는 그 고요함이 뉴스입니다.",
    "[운영자 확인] 초안", {}),
  ],
  "short": {"from": 4, "to": 11},
  "fact_checks": [
   "'올해 상륙 태풍 0개'는 9/28 기준. 업로드 시점에 태풍이 상륙했으면 꼭지 전체 재검토 (기상청)",
   "3년 평균 2.33개, 장기 평균 대비 28.6% 감소, 북태평양·티베트 고기압, 8월 태풍 돌핀이 상하이 쪽으로 (한국해양과학기술원, 코리아헤럴드 2026-09-28)",
   "IBTrACS 확인: 돌핀은 날짜변경선 부근(178°E)에서 발생해 상하이 남쪽 저장성(27.9°N 119.7°E)에 상륙. 그래서 '상하이로 갔다'가 아니라 '상하이 쪽으로'. 올해 한국에 가장 가까이 온 태풍은 바비(약 376km)",
   "경남 남해안 양식 물고기 773만 마리·전복 109만 마리 폐사, 252억 원 (경남도, 코리아헤럴드). 원인이 태풍 공백만인지는 기사에서도 단정하지 않으므로 '피해를 보고 있다' 수준으로만 표현함",
   "강수량 832.8mm로 평년의 84.8%, 34개 시군 기상 가뭄 (코리아헤럴드 인용 보도)",
  ],
 },
 {
  "key": "gangnam", "category": "kpop", "desk": "SEOUL",
  "headline": "Gangnam wants to be the world's K-festival, and Psy is closing the show",
  "hook": "Gangnam is throwing a street festival.\nGuess who's headlining",
  "sensitivity": "go",
  "screens": {
   "s1": {"image": "gangnam_parade.png", "label": "GANGNAM FESTIVAL", "credit": "AI-generated image",
          "desc": "강남 도산대로의 거리 퍼레이드: 전통 취타대 행렬, 거대한 캐릭터 풍선, 양옆 관중 (AI 이미지. 실제 가수 얼굴이나 뮤직비디오 장면 금지)"},
   "s2": {"image": "gangnam_numbers.png", "label": "BY THE NUMBERS", "credit": "Source: Gangnam-gu Office via Korea Herald",
          "desc": "숫자 카드: 제15회 / 퍼레이드 약 1km / 무료 콘서트 티켓 13,000장 즉시 마감 / 방문객 목표 3만 명+"},
  },
  "lines": [
   ("panel", "Can we please talk about something happy now?",
    "이제 제발 좋은 얘기 하면 안 돼요?",
    "[잡담] 무거운 태풍 꼭지 뒤 분위기 전환", {}),
   ("anchor", "I have Psy.",
    "싸이가 있습니다.", "[잡담]", {}),
   ("panel", "Perfect.",
    "완벽해요.", "[잡담]", {}),
   ("anchor", "Our next story comes from a neighborhood you already know. Even if you think you don't.",
    "다음 소식은 여러분이 이미 아는 동네에서 왔습니다. 모른다고 생각하셔도요.", "궁금증 유발 도입", {}),
   ("anchor", "Gangnam. Yes. That Gangnam.",
    "강남. 네. 그 강남입니다.",
    "전 세계가 아는 '강남스타일'을 이름만으로 떠올리게 함. 노래나 가사는 쓰지 않음(저작권)", {"screen": "s1"}),
   ("panel", "Wait. Is this about the horse dance? Please tell me this is about the horse dance.",
    "잠깐, 말춤 얘기예요? 제발 말춤 얘기라고 해줘요.", "시청자 대부분이 떠올릴 것을 대신 말함", {}),
   ("anchor", "It is about a festival. This weekend is the fifteenth Gangnam Festival: a one-kilometer street parade, giant character balloons, and a traditional Korean marching band leading the way.",
    "축제 얘기입니다. 이번 주말 제15회 강남페스티벌이 열립니다. 1km 거리 퍼레이드, 거대한 캐릭터 풍선, 그리고 맨 앞에는 전통 취타대가 섭니다.",
    "K가 말춤 질문을 무시하고 사실만 읽는 무표정 개그", {"screen": "s1", "big": True}),
   ("anchor", "And on Sunday, a K-pop concert closed out by the man who taught the entire planet to say 'Gangnam'. Psy.",
    "그리고 일요일 K-POP 콘서트의 마지막 무대는, 전 세계에 '강남'이라는 단어를 가르친 사람이 장식합니다. 싸이.",
    "셋리스트는 발표되지 않았으므로 어떤 곡을 부른다고 말하지 않음", {}),
   ("panel", "Psy. In Gangnam. That is the biggest home game in music history!",
    "싸이가 강남에서요? 음악 역사상 최대의 홈경기네요!",
    "스포츠 용어 'home game'을 공연에 씀. 영어권에서 바로 통하는 비유", {}),
   ("anchor", "Thirteen thousand free concert tickets. Gone almost immediately.",
    "무료 콘서트 티켓 1만 3천 장. 거의 즉시 마감됐습니다.", "", {"screen": "s2"}),
   ("panel", "Free?! I would have fought someone for those.",
    "공짜라고요?! 저 같으면 싸워서라도 구했어요.", "", {}),
   ("anchor", "This is a serious news program. We do not fight for tickets. We refresh the page calmly, like adults.",
    "여기는 진지한 뉴스 프로그램입니다. 우리는 티켓 때문에 싸우지 않습니다. 어른답게 차분히 새로고침합니다.",
    "K의 고정 대사 'This is a serious news program' + 티켓팅 새로고침은 K-POP 팬이면 다 아는 경험", {}),
   ("anchor", "Organizers even studied New York's Macy's Thanksgiving Day Parade and Japan's Nebuta Festival. The goal: when people think 'K-festival', they think Gangnam.",
    "주최 측은 뉴욕 메이시스 추수감사절 퍼레이드와 일본 네부타 축제까지 참고했습니다. 목표는 'K-페스티벌' 하면 강남이 떠오르게 하는 것.",
    "미국 시청자가 아는 메이시스 퍼레이드를 넣어 '우리 것과 비교'하는 재미", {"screen": "s1"}),
   ("panel", "Admit it. You're going.",
    "인정하세요. 가실 거죠?", "", {}),
   ("anchor", "I have... prior commitments.",
    "저는… 선약이 있습니다.",
    "뻔한 거짓말로 들리는 한 박자 쉼. K가 몰래 즐기는 캐릭터(K-드라마 보고 우는 설정)와 연결", {}),
   ("anchor", "K's Take: Fourteen years after one song put Gangnam on the world map, Gangnam is still trying to live up to it. Honestly? Respect.",
    "K의 한마디: 노래 한 곡이 강남을 세계 지도에 올린 지 14년. 강남은 아직도 그 이름값을 하려고 노력 중입니다. 솔직히? 존경합니다.",
    "[운영자 확인] 초안", {}),
  ],
  "short": {"from": 5, "to": 12},
  "fact_checks": [
   "업로드 시점에 축제(10/3~10/5 토~월로 보임)가 이미 끝났으면 1·4·5번 대사를 과거형으로. '이번 주말' 날짜 확인 (강남구청, 코리아헤럴드 2026-09-28)",
   "제15회, 도산대로 청담사거리~도산공원사거리 약 1km, 취타대·캐릭터 풍선, 일요일 콘서트 제로베이스원·키키·싸이 마지막, 무료 티켓 13,000장 조기 마감, 메이시스 퍼레이드·아오모리 네부타 참고 (코리아헤럴드)",
   "강남스타일 발표 2012년 → 2026년이면 14년",
   "K-POP 데스크 규칙: 뮤직비디오·방송 화면·가수 실물 사진 사용 금지. 그래픽으로만",
  ],
 },
 {
  "key": "samsung", "category": "money_business", "desk": "MONEY",
  "headline": "In Korea, you can subscribe to your air conditioner",
  "hook": "In Korea you can SUBSCRIBE\nto your air conditioner",
  "sensitivity": "go",
  "screens": {
   "s1": {"image": "samsung_sub.png", "label": "APPLIANCE SUBSCRIPTIONS", "credit": "Illustration",
          "desc": "일러스트: 냉장고·에어컨·세탁기에 스트리밍 앱 같은 '구독' 버튼과 월 요금표가 붙은 모습 (실제 삼성 로고나 앱 화면은 쓰지 않음)"},
   "s2": {"image": "samsung_numbers.png", "label": "BY THE NUMBERS", "credit": "Source: Samsung Electronics via Yonhap, Korea Herald",
          "desc": "숫자 카드: 누적 매출 약 1조 원(약 7억 4천만 달러) / 한국인 94.8%가 구독 서비스 이용 / 1인 평균 5.5개 / 월 41,853원(약 31달러)"},
  },
  "lines": [
   ("anchor", "Speaking of prior commitments...",
    "선약 얘기가 나와서 말인데요…",
    "[잡담] 3꼭지 '선약' 콜백. 뒤의 '6년짜리 연애'로 이어짐", {}),
   ("anchor", "Finally tonight, a money story. In Korea, you can subscribe to... your air conditioner.",
    "마지막은 돈 이야기입니다. 한국에서는 구독할 수 있습니다… 에어컨을요.",
    "'subscribe' 뒤에 뜸 들이고 의외의 대상을 말하는 구조", {}),
   ("panel", "Like Netflix? For an air conditioner?",
    "넷플릭스처럼요? 에어컨을?", "영어권에서 '구독 = 넷플릭스'라는 공통 기준", {}),
   ("anchor", "Sort of. Samsung says its appliance subscription business is now approaching one trillion won in sales. That's about seven hundred forty million dollars.",
    "비슷합니다. 삼성은 가전 구독 사업 매출이 1조 원에 다가가고 있다고 밝혔습니다. 약 7억 4천만 달러입니다.",
    "원화를 달러로 바꿔 말해 줘야 영미권 시청자가 규모를 느낌", {"screen": "s1"}),
   ("anchor", "You pay monthly, and for the whole contract, engineers take care of maintenance, repairs and check-ups. It's less like streaming, and more like a very long rental.",
    "매달 요금을 내면 계약 기간 동안 기사님이 점검, 수리, 관리를 다 해 줍니다. 스트리밍보다는 아주 긴 렌탈에 가깝죠.",
    "넷플릭스와 다른 점을 정확히 짚어 오해를 막음(코리아헤럴드도 같은 설명)", {"screen": "s1"}),
   ("panel", "So I don't own the fridge. The fridge and I are... in a relationship.",
    "그러니까 냉장고를 소유하는 게 아니라… 냉장고랑 사귀는 거네요.",
    "계약을 연애에 빗댄 비유. 영어권 코미디에서 흔하고 잘 통하는 방식", {}),
   ("anchor", "A six-year relationship. With scheduled check-ins.",
    "6년짜리 연애입니다. 정기 점검 포함.",
    "'check-in'은 '점검'과 '연인끼리 안부 확인' 두 뜻. 말장난", {}),
   ("anchor", "Let's look at the numbers. Ninety-four point eight percent of Koreans used a subscription service this year. The average person has five point five.",
    "숫자를 보시죠. 올해 한국인의 94.8%가 구독 서비스를 이용했습니다. 1인당 평균 5.5개입니다.",
    "", {"screen": "s2", "big": True}),
   ("panel", "Five point FIVE? Who has half a subscription?",
    "5.5개요? 누가 구독을 반 개 해요?",
    "평균값을 문자 그대로 받아들이는 고전적인 숫자 개그", {}),
   ("anchor", "Technically, it's an average. Nobody has half a subscription. ...Probably.",
    "엄밀히 말하면 평균입니다. 구독을 반 개 하는 사람은 없습니다. …아마도요.",
    "정확성에 집착하는 K가 끝에 자신 없어지는 반전", {}),
   ("anchor", "Now Samsung wants hotels, hospitals and public offices to subscribe too. There's even a plan for newlyweds and people who move a lot, with cleaning visits at night and on holidays.",
    "이제 삼성은 호텔, 병원, 공공기관까지 구독 고객으로 삼으려 합니다. 신혼부부와 이사가 잦은 사람을 위해 밤이나 휴일에 청소하러 오는 상품도 있습니다.",
    "", {"screen": "s1"}),
   ("panel", "Night cleaning visits? That's not a subscription. That's a love language.",
    "밤에 청소하러 와 준다고요? 그건 구독이 아니라 사랑의 언어예요.",
    "'love language(사랑의 언어)'는 영어권 유행어. 5번의 연애 비유 콜백", {}),
   ("anchor", "K's Take: In Korea, even your washing machine comes with a care plan. We're still deciding whether that's the future, or just very, very organized.",
    "K의 한마디: 한국에선 세탁기에도 케어 플랜이 붙습니다. 이게 미래인지, 그냥 엄청나게 꼼꼼한 건지는 아직 판단 중입니다.",
    "[운영자 확인] 초안", {}),
   ("anchor", "You can also subscribe to this channel. No six-year contract.",
    "이 채널도 구독하실 수 있습니다. 6년 약정은 없습니다.",
    "구독 주제로 채널 구독을 유도하는 마무리. 6년 계약 콜백", {}),
   ("anchor", "That's all for tonight. Stay curious. Keep your lenses clean.",
    "오늘은 여기까지입니다. 계속 궁금해하세요. 렌즈는 깨끗하게.", "확정된 클로징 멘트", {}),
   ("panel", "So what are you doing this weekend?",
    "주말에 뭐 해요?", "[잡담] 클로징 뒤 한마디", {}),
   ("anchor", "Refreshing pages. Calmly.",
    "새로고침합니다. 차분하게.", "[잡담] 3꼭지 티켓팅 개그 콜백. K가 사실 강남 콘서트에 가고 싶다는 암시", {}),
  ],
  "short": {"from": 2, "to": 9},
  "fact_checks": [
   "누적 매출 약 1조 원(연합뉴스 7억 3,400만 달러, 코리아헤럴드 7억 4,000만 달러로 환산이 조금 다름) → '약 7억 4천만 달러'. 삼성 발표 2026-09-28",
   "94.8%, 1인 평균 5.5개, 월 41,853원은 삼성이 인용한 조사 (연합뉴스). 조사 출처명 확인하면 화면 출처에 추가",
   "호텔·병원·공공기관 대상 확대, 신혼·잦은 이사 고객용 야간·휴일 청소 방문, 에어컨 6년 계약 월 92,000원 → 82,000원 옵션 (코리아헤럴드)",
   "'6년'은 에어컨 6년 계약 예시에서 온 숫자. 모든 상품이 6년은 아님. 5·6번 대사는 비유로만 씀",
   "삼성 브랜드 로고, 제품 사진, 앱 화면 사용 금지. 일러스트로만",
  ],
 },
]


# ── explainer screens ─────────────────────────────────────────────────────
# Pictures live in screens/<segment>/ with a credits.json (licence and on-screen credit per file).
# A card is drawn by the renderer and counts its numbers up.
def pic(path, label, **kw):
    return {"file": path, "label": label, **kw}


def card(label, credit, stats, title="BY THE NUMBERS"):
    return {"card": {"title": title, "stats": stats}, "label": label, "credit": credit}


SCREEN_DEFS = {
    "bukang": {
        "menu_shark": pic("bukang/bukang_staycation.png", "TONIGHT"),
        "menu_typhoon": pic("typhoon/bouncers.png", "TONIGHT"),
        "menu_psy": pic("gangnam/gangnam_parade.png", "TONIGHT"),
        "menu_fridge": pic("samsung/fridge_date.png", "TONIGHT"),
        "canal": pic("bukang/bukang_canal.png", "BUSAN NORTH PORT"),
        "requiem": pic("bukang/requiem_shark_underwater.jpg", "FILE PHOTO"),
        "dusky": pic("bukang/dusky_shark_illustration.jpg", "DUSKY SHARK (ILLUSTRATION)", kb="left"),
        "staycation": pic("bukang/bukang_staycation.png", "MEET BUKANG-I"),
        "visitors": card("BY THE NUMBERS", "Source: Busan Infrastructure Corp. via Yonhap",
                         [{"value": 568800, "label": "visitors since Sept. 19"},
                          {"value": 140000, "label": "in a single day over Chuseok"}]),
        "fifty": card("BY THE NUMBERS", "Source: Busan Infrastructure Corp. via Yonhap",
                      [{"value": 2000, "prefix": "about ", "label": "visitors on a normal holiday"},
                       {"value": 50, "prefix": "x", "label": "this Chuseok"}]),
        "farewell": pic("bukang/bukang_farewell.png", "THE PLAN: BACK TO SEA"),
    },
    "typhoon": {
        "tracks": pic("typhoon/track_map.png", "2026 TYPHOON TRACKS", kb="in"),
        "zero": card("KOREA, 2026", "Source: Korea Meteorological Administration",
                     [{"value": 26, "label": "storm tracks in the West Pacific"},
                      {"value": 0, "label": "landfalls in Korea"}], title="THIS YEAR SO FAR"),
        "bouncers": pic("typhoon/bouncers.png", "THE BOUNCERS", kb="in",
                        overlays=[{"text": "TIBETAN HIGH", "x": 0.2, "y": 0.07},
                                  {"text": "NORTH PACIFIC HIGH", "x": 0.72, "y": 0.07}]),
        "dolphin1": pic("typhoon/dolphin_iss_1.jpg", "TYPHOON DOLPHIN, AUG. 2"),
        "dolphin2": pic("typhoon/dolphin_iss_2.jpg", "TYPHOON DOLPHIN, AUG. 2"),
        "stormy": pic("typhoon/stormy_sea.jpg", "WHY IT MATTERS"),
        "calm": pic("typhoon/calm_ocean.jpg", "WHY IT MATTERS"),
        "stuffy": pic("typhoon/stuffy_room.png", "THE OCEAN, THIS SUMMER", kb="in"),
        "seafarms": pic("typhoon/sea_farms_south_korea.jpg", "SEA FARMS, SOUTH COAST"),
        "fish": card("SOUTHERN COAST, 2026", "Source: South Gyeongsang Province, KMA",
                     [{"value": 7730000, "label": "farmed fish died this year"},
                      {"value": 15, "prefix": "-", "suffix": "%", "label": "rainfall vs. normal (Mar.-Sept.)"}],
                     title="THE COST"),
        "drought": pic("typhoon/drought.jpg", "DROUGHT"),
        "hinnamnor": pic("typhoon/hinnamnor_2022_airs.jpg", "TYPHOON HINNAMNOR, 2022"),
    },
    "gangnam": {
        "street": pic("gangnam/gangnam_street_2009.jpg", "GANGNAM, SEOUL"),
        "rodeo": pic("gangnam/apgujeong_rodeo_night.jpg", "GANGNAM, SEOUL"),
        "station": pic("gangnam/gangnam_station_sign.jpg", "YES. THAT GANGNAM.", kb="in"),
        "route": pic("gangnam/gangnam_route.png", "PARADE ROUTE", kb="in"),
        "band": pic("gangnam/korean_marching_band.jpg", "TRADITIONAL MARCHING BAND (FILE PHOTO)"),
        "parade": pic("gangnam/gangnam_parade.png", "GANGNAM FESTIVAL"),
        "psy": card("SUNDAY", "Source: Gangnam-gu Office via Korea Herald",
                    [{"value": "K-POP CONCERT", "label": "with ZEROBASEONE and KiiiKiii"},
                     {"value": "PSY", "label": "closing the show"}], title="SUNDAY NIGHT"),
        "tickets": card("BY THE NUMBERS", "Source: Gangnam-gu Office via Korea Herald",
                        [{"value": 13000, "label": "free concert tickets, gone almost immediately"}]),
        "frenzy": pic("gangnam/ticket_frenzy.png", "TICKETING, CALMLY", kb="in"),
        "nebuta1": pic("gangnam/nebuta_lantern.jpg", "NEBUTA FESTIVAL, JAPAN (FILE PHOTO)"),
        "nebuta2": pic("gangnam/nebuta_float.jpg", "NEBUTA FESTIVAL, JAPAN (FILE PHOTO)"),
        "dosan": pic("gangnam/dosan_park_gate.jpg", "DOSAN PARK, THE FINISH LINE"),
    },
    "samsung": {
        "aircon": pic("samsung/wall_air_conditioner.jpg", "SUBSCRIBE TO... THIS"),
        "trillion": card("BY THE NUMBERS", "Source: Samsung Electronics via Yonhap",
                         [{"value": "1 TRILLION WON", "label": "nearly, in appliance subscription sales"},
                          {"value": 740, "prefix": "$", "suffix": " million", "label": "in US dollars"}]),
        "concept": pic("samsung/appliance_subscriptions.png", "HOW IT WORKS"),
        "repair": pic("samsung/appliance_repairman.jpg", "HOW IT WORKS"),
        "fridge": pic("samsung/refrigerator.jpg", "HOW IT WORKS"),
        "date": pic("samsung/fridge_date.png", "A SIX-YEAR RELATIONSHIP", kb="in"),
        "subs": card("BY THE NUMBERS", "Source: survey cited by Samsung Electronics",
                     [{"value": 94.8, "decimals": 1, "suffix": "%", "label": "of Koreans used a subscription this year"},
                      {"value": 5.5, "decimals": 1, "label": "subscriptions per person, on average"}]),
        "hotel": pic("samsung/hotel_room.jpg", "NEXT: HOTELS"),
        "hospital": pic("samsung/hospital_corridor.jpg", "HOSPITALS"),
        "moving": pic("samsung/moving_boxes.jpg", "NEWLYWEDS AND MOVERS"),
    },
}

# line number (as in script_ko.md, from 1) -> what the renderer shows
LINE_PLAN = {
    "bukang": {2: {"screen": ["menu_shark", "menu_typhoon", "menu_psy", "menu_fridge"], "big": True},
               4: {"screen": "canal"}, 5: {"screen": "requiem"}, 9: {"screen": "dusky"},
               10: {"screen": "staycation", "big": True}, 12: {"screen": "visitors", "big": True},
               13: {"screen": "fifty", "big": True}, 15: {"screen": "farewell"},
               17: {"shot": "anchor_solo"}},
    "typhoon": {4: {"screen": ["tracks", "zero"], "big": True, "screen_split": [0.55]},
                7: {"screen": "bouncers", "big": True}, 8: {"screen": ["dolphin2", "dolphin1"], "big": True},
                10: {"screen": ["stormy", "calm"]}, 11: {"screen": "stuffy"},
                12: {"screen": ["seafarms", "fish", "drought"], "big": True, "screen_split": [0.25, 0.7]},
                14: {"screen": "hinnamnor"}, 15: {"shot": "anchor_solo"}},
    "gangnam": {4: {"screen": ["street", "rodeo"]}, 5: {"screen": "station", "big": True},
                7: {"screen": ["route", "band", "parade"], "big": True}, 8: {"screen": "psy", "big": True},
                10: {"screen": "tickets", "big": True}, 12: {"screen": "frenzy", "big": True},
                13: {"screen": ["nebuta1", "nebuta2", "dosan"]}, 16: {"shot": "anchor_solo"}},
    "samsung": {2: {"screen": "aircon"}, 4: {"screen": "trillion", "big": True},
                5: {"screen": ["concept", "repair", "fridge"]}, 6: {"screen": "date"},
                8: {"screen": "subs", "big": True}, 11: {"screen": ["hotel", "hospital", "moving"]},
                13: {"shot": "anchor_solo"}, 15: {"shot": "wide"}},
}


def screen_specs(key):
    """Renderer screen specs for one segment, with credits pulled from screens/*/credits.json."""
    out = {}
    for name, d in SCREEN_DEFS[key].items():
        if "card" in d:
            out[name] = dict(d)
            continue
        folder, fn = d["file"].split("/")
        credits = json.load(open(os.path.join(OUT, "screens", folder, "credits.json")))
        if fn not in credits:
            raise SystemExit(f"{d['file']}: no entry in screens/{folder}/credits.json")
        spec = {"image": f"screens/{d['file']}", "label": d["label"], "credit": credits[fn]["on_screen_credit"]}
        spec.update({k: v for k, v in d.items() if k in ("kb", "overlays")})
        out[name] = spec
    return out


ASR = {}


def norm(w):
    return "".join(c for c in w.lower() if c.isalnum())


def align_words(text, asr):
    """Script words with times from speech recognition: words the recognizer heard the same get its
    times; the rest (numbers it wrote as digits, names it misheard) share the gap between them."""
    import difflib
    toks = text.split()
    if not asr:
        return None
    a, b = [norm(t) for t in toks], [norm(w[0]) for w in asr]
    times = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = (asr[blk.b + k][1], asr[blk.b + k][2])
    end = asr[-1][2]
    k = 0
    while k < len(toks):
        if times[k] is not None:
            k += 1
            continue
        j = k
        while j < len(toks) and times[j] is None:
            j += 1
        t0 = times[k - 1][1] if k > 0 else 0.0
        t1 = times[j][0] if j < len(toks) else end
        step = max(t1 - t0, 0.05) / (j - k)
        for m in range(k, j):
            times[m] = (t0 + step * (m - k), t0 + step * (m - k + 1))
        k = j
    return [[t, round(s0, 2), round(e0, 2)] for t, (s0, e0) in zip(toks, times)]


def build():
    global ASR
    path = os.path.join(OUT, "audio", "asr_words.json")
    ASR = json.load(open(path)) if os.path.exists(path) else {}
    ep = {
        "episode": 1, "name": "ep01", "anchor": "anchor",
        "outro_ticker": "Thanks for watching. See you next episode",
        "background": {"image": "../../assets/studio/seoul_dusk.jpg", "dim": 0.8, "blur": 1.5},
        "characters": {
            "anchor": {"head": "cast/a_head.png", "body": "cast/a_body.png", "ref": "cast/a_ref.png", "x": 1290,
                       "label": "MASTER K"},
            "panel": {"head": "cast/p_head.png", "body": "cast/p_body.png", "ref": "cast/p_ref.png", "x": 630,
                      "label": "DR. KANGFREE", "energy": 1.8, "head_ratio": 0.74, "shoulders": 500,
                      "chin_drop": 0.12},
        },
        "segments": [],
    }
    md = ["# EP.1 대본 (검토용)", "",
          "- 출연: Master K(앵커), Dr. Kangfree(패널)",
          "- 렌더링 입력: `script.json` (`build_script.py`가 이 파일과 함께 만듦). 경로는 이 폴더 기준",
          "- `[운영자 확인]` = K's Take는 운영자 관점 자리라 초안임. 바꿔 주세요",
          "- 개그 해설은 Claude의 판단입니다. 실제 원어민 반응과 다를 수 있습니다", ""]
    for n, seg in enumerate(SEGMENTS, 1):
        specs, plan = screen_specs(seg["key"]), LINE_PLAN[seg["key"]]
        lines, used = [], set()
        md += [f"## 꼭지 {n}. {seg['headline']}", "",
               f"- 카테고리 `{seg['category']}` · 민감도 **{seg['sensitivity']}**"
               + (f" ({seg['sensitivity_reason']})" if seg.get("sensitivity_reason") else ""),
               f"- 쇼츠 훅: {seg['hook'].replace(chr(10), ' / ')} · 쇼츠 구간: {seg['short']['from']}~{seg['short']['to']}번 줄", "",
               "| # | 누가 | 화면 | 대사 (EN) | 번역 | 왜 웃긴가 / 메모 |", "|---|---|---|---|---|---|"]
        for i, (who, text, ko, note, _old) in enumerate(seg["lines"], 1):
            extra = plan.get(i, {})
            scr = extra.get("screen")
            keys = scr if isinstance(scr, list) else ([scr] if scr else [])
            for k in keys:
                if k not in specs:
                    raise SystemExit(f"{seg['key']} line {i}: unknown screen {k}")
                used.add(k)
            audio = f"ep01_{seg['key']}_{i:02d}.mp3"
            line = {"who": who, "audio": f"audio/{audio}", **extra, "text": text}
            timed = align_words(text, ASR.get(audio))
            if timed:
                line["words"] = timed
            lines.append(line)
            name = "K" if who == "anchor" else "Kangfree"
            shown = " → ".join(keys) + (" (크게)" if extra.get("big") else "") if keys else extra.get("shot", "")
            md.append(f"| {i} | {name} | {shown} | {text} | {ko} | {note} |")
        unused = set(specs) - used
        if unused:
            raise SystemExit(f"{seg['key']}: screens never shown: {sorted(unused)}")
        md += ["", "**설명 화면**", "", "| 키 | 파일 / 카드 | 라벨 | 출처 표기 |", "|---|---|---|---|"]
        for k, v in specs.items():
            what = v.get("image", "숫자 카드: " + " / ".join(str(st["value"]) + " " + st.get("label", "")
                                                        for st in v.get("card", {}).get("stats", [])))
            md.append(f"| `{k}` | {what} | {v['label']} | {v['credit']} |")
        md += ["", "**업로드 전 사실 확인**", ""] + [f"- [ ] {c}" for c in seg["fact_checks"]] + [""]
        ep["segments"].append({
            "category": seg["category"], "desk": seg["desk"], "headline": seg["headline"], "hook": seg["hook"],
            "screens": specs, "lines": lines,
            # the renderer counts lines from 0; the review sheet counts from 1
            "short": {"from": seg["short"]["from"] - 1, "to": seg["short"]["to"] - 1},
        })
    json.dump(ep, open(f"{OUT}/script.json", "w"), ensure_ascii=False, indent=1)
    open(f"{OUT}/script_ko.md", "w").write("\n".join(md) + "\n")
    words = sum(len(l[1].split()) for s in SEGMENTS for l in s["lines"])
    print("segments", len(SEGMENTS), "lines", sum(len(s["lines"]) for s in SEGMENTS), "words", words,
          "≈ minutes at 150wpm", round(words / 150, 1))


if __name__ == "__main__":
    build()
