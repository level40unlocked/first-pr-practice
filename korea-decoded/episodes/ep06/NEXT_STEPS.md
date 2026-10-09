# EP.6 진행 메모 (2026-10-09)

## 완료
- 대본 v3 105줄 확정: `script.md` (EN+KO+화면 열). 화면 열이 곧 화면 설계표 초안.
- 음성 105줄 확정: `audio/v1/ep06_001~105.mp3`, `audio/urls.txt`, `audio/durations_v1.json` (음성만 약 10분 43초). 25·59번 줄은 "Ree Jeh-myung"으로 재생성. 발음 샘플 운영자 확인 완료("나머지 오케이").
- 도구: `parse_script.py`(script.md → L 리스트), `audio/prep.py`(TTS 철자), `audio/dl.py`.

## 남은 일 (EP.5 방식 그대로)
1. `make_cards.py` / `screens.py` : script.md 화면 열 기준 카드·도식·타임라인·큰 글자. 사진 없이 자체 그래픽만 (저작권 부담 없음). 도식: SCAN→WEAK SPOT→ENTER, BOOSTER→SEPARATE→GLIDE, 탄도 포물선 vs 활공, HGV vs HyCore 비교, 한글날 타임라인(1446/1926/2026, 90년대 초/2000년대 중반/2013), 막대(50.9%/37%).
2. `build_episode.py` : 게스트 Dusk(해킹, 6~34) / Nonfic(35~72) / Dr. H(73~98). 게스트 좌석 2560. docs/camera_framing.md 규칙(k_screen, 말하는 사람 단독+화면) 준수.
3. 렌더(`run_segments.sh`, 3구간 권장: 1~34 / 35~72 / 73~105) → 합본 → 720p 점검본.
4. 자막 SRT(`make_srt.py`), 쇼츠 4개, 썸네일 3안, `upload_meta.md`, `upload_handoff.md`.
5. 업로드 직전 사실 재확인(대본 하단 VERIFY 목록). 업로드는 운영자 승인 후.

## 공개 목표
한국 10/13(화) 06:57 = 미 동부 10/12(월) 17:57.

## 남은 결정
- 길이 약 11분 30초 유지 vs 하이코어(66~71번 줄) 삭제.
- 사진 없이 그래픽만으로 갈지.

## 이미지 결정 (2026-10-09, 운영자)
- 이미지 폴더(깃 제외): `assets/stock/ep06/` (+ `CREDITS.txt`, `cards/`)
- 미사일: 언론·유출 사진은 쓰지 않고 Higgsfield `gpt_image_2_5` 일러스트 4장(16:9, 1344×752, 글자·로고 없음, 허구 설계):
  - missile_1_launch (36·40번 줄 부근, 바지선 발사) job bf4418ba-07e7-4674-9973-bfd99d98f2b0
  - missile_2_separation_glide (40·42·56번) job a0d42a7d-48ab-47d0-9d50-01da3f4e0258
  - missile_3_arc_vs_glide (40·46~47번 탄도 포물선 vs 활공) job fa21f234-6767-4d0d-afc8-9592f1a88e86
  - missile_4_scramjet (67·69번 하이코어/스크램제트) job ae9d298f-1843-4f5e-8002-fd20c344263a
  - 일러스트는 "실제 무기 사진이 아닌 개념도"임을 영상에서 오해 없게 쓸 것(현재 기본 방침: 카드 배경으로 사용, 실제 무기 외형 주장 없음)
- 한글날: 운영자 첨부에서 사용 가능한 6장만 사용: 76 해례본(PD), 83 포스터, 88 발표(이름 연결 금지, "결선 참가자"만), 88 단체사진, 89 선비복장 글쓰기, 98 세종대왕 동상(하단 전화번호 잘라냄) + 98 광화문 야경(CC 출처표기). 74는 저해상도·한글 박힌 홍보물이라 제외, 78 자모표는 자체 카드로 대체.
- 출처 표기(Wikimedia 2장)는 영상 설명란 credits에 넣을 것.
