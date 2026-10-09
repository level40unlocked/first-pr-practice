# EP.5 업로드 인계 (YouTube 토큰이 살아 있는 세션/컴퓨터에서 올릴 때)

이 클라우드 세션의 토큰은 만료(invalid_grant). 토큰은 채팅에 붙여넣지 않는다.

## 파일 (이 채팅에 첨부로 전달)
- 롱폼 1080p 조각 10개 `ep05_part00~09.mp4` + `list.txt` + `sha256.txt`. 합치기: `ffmpeg -f concat -safe 0 -i list.txt -c copy ep05_long_final.mp4` (길이 6:40.8)
- 쇼츠 4편 `ep05_short_turtle / nate / biff / michelle.mp4`
- 썸네일 `thumb_A.jpg`(제 선택), `thumb_B.jpg`, `thumb_C.jpg`
- 영어 자막 `ep05_en.srt` (108줄)
- 제목·설명·태그·쇼츠 제목: `episodes/ep05/upload_meta.md` (브랜치 `claude/happy-hawking-cgmcjm`)

## 일정
- 롱폼: 동부 금요일 10/9 17:57 = 한국 토요일 10/10 06:57
- 쇼츠: 한국 10/10 18:57 (turtle), 10/11 06:57 (nate), 10/11 18:57 (biff), 10/12 18:57 (michelle). 비공개 + 예약.

## 다른 세션에 붙여넣을 지시문
```
EP.5를 유튜브에 비공개 + 예약 공개로 올려줘. 공개는 내가 따로 승인하기 전까지 하지 마.
- 브랜치 claude/happy-hawking-cgmcjm pull. episodes/ep05/upload_meta.md에 제목, 설명, 태그, 쇼츠 제목, 일정이 있어.
- 파일은 내가 [폴더 경로]에 둠: 롱폼 조각 합친 mp4, thumb_A.jpg, 쇼츠 4개, ep05_en.srt
- 롱폼: 2026-10-10T06:57+09:00 예약, 썸네일 thumb_A 첨부
- 쇼츠: turtle 10/10 18:57, nate 10/11 06:57, biff 10/11 18:57, michelle 10/12 18:57 (KST)
- 자막은 youtube.force-ssl 범위가 없으면 올리지 말고 알려줘 (내가 Studio에서 올림)
- 올리기 전에 --dry-run으로 보낼 내용을 먼저 보여주고 내가 확인한 뒤에 올려줘
```

## 확인할 것 (공개 당일)
- 자라섬(10/9~11), 부산영화제(10/6~15) 일정이 바뀌지 않았는지
- 네이트 스미스·미셸 여·장이머우 사진은 출처 문구 없음(운영자 제공)
