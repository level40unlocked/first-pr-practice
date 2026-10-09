# 클라우드 환경 네트워크 허용 도메인

Claude Code 클라우드 환경 설정(세션 제목 표시줄의 환경 메뉴 → Edit → Network access)에 추가할 도메인.
쇼 바이블에 "이미 추가해 둠"으로 적힌 것(upload.higgsfield.ai, cloudfront 두 곳, 뉴스 RSS, 네이버, 구글 API)은 제외.

## 무료 이미지·영상 (설명 화면)
| 도메인 | 용도 |
|---|---|
| commons.wikimedia.org, upload.wikimedia.org | 위키미디어 커먼즈 CC0·CC BY 사진 검색과 다운로드 |
| api.openverse.org | CC 라이선스 이미지 통합 검색 (여러 사이트를 한 번에) |
| api.pexels.com, images.pexels.com, videos.pexels.com | Pexels 무료 사진·**무료 영상** (API 키 필요, 무료) |
| pixabay.com, cdn.pixabay.com | Pixabay 무료 사진·영상·효과음 (API 키 필요, 무료) |
| api.unsplash.com, images.unsplash.com | Unsplash 무료 사진 (API 키 필요, 무료) |
| www.flickr.com, api.flickr.com, live.staticflickr.com | Flickr CC 사진 (Korea.net 공식 계정 포함) |

## 한국 공공 저작물 (공공누리)
| 도메인 | 용도 |
|---|---|
| www.kogl.or.kr | 공공누리 저작물 통합 검색 |
| www.korea.kr | 대한민국 정책브리핑 사진 |
| www.korea.net | 해외홍보원 사진 |
| photo.visitkorea.or.kr, korean.visitkorea.or.kr, english.visitkorea.or.kr | 한국관광공사 관광사진 갤러리 |
| www.data.go.kr, apis.data.go.kr | 공공데이터포털 (관광사진 API, 각종 통계 API) |
| www.busan.go.kr, www.visitbusan.net | 부산시 보도사진, 부산 관광 사진 |
| www.seoul.go.kr, news.seoul.go.kr | 서울시 보도사진 |
| www.gangnam.go.kr | 강남구 보도자료 (대부분 4유형이라 확인용) |
| www.gyeongnam.go.kr | 경남도 보도자료 (양식장 등) |
| www.mof.go.kr | 해양수산부 |
| www.mcst.go.kr | 문화체육관광부 |

## 위성·날씨·지도 (움직이는 그래픽 재료)
| 도메인 | 용도 |
|---|---|
| science.nasa.gov, earthobservatory.nasa.gov, eoimages.gsfc.nasa.gov | NASA 위성 사진 (상업 이용 가능, 출처 NASA) |
| images-api.nasa.gov, images-assets.nasa.gov | NASA 이미지 라이브러리 검색·다운로드 |
| worldview.earthdata.nasa.gov, gibs.earthdata.nasa.gov | 날짜별 위성 영상 타일 (태풍 이동 애니메이션) |
| www.kma.go.kr, data.kma.go.kr, apihub.kma.go.kr, nmsc.kma.go.kr | 기상청 자료, 천리안 위성 영상 |
| www.jma.go.jp, www.data.jma.go.jp | 일본 기상청 태풍 경로 |
| www.ncei.noaa.gov | IBTrACS 전 세계 태풍 경로 데이터 |
| tile.openstreetmap.org, nominatim.openstreetmap.org | 지도 타일, 지명 좌표 (출처 표기 필요) |
| www.naturalearthdata.com, naciscdn.org | 퍼블릭 도메인 세계 지도 데이터 (지도 애니메이션 배경) |

## 통계·팩트체크
| 도메인 | 용도 |
|---|---|
| kosis.kr | 통계청 KOSIS |
| ecos.bok.or.kr | 한국은행 경제통계 |
| www.yna.co.kr | 연합뉴스 한국어판 (사실 확인) |
| koreajoongangdaily.joins.com, www.koreatimes.co.kr | 영문 신문 (사실 확인, 주제 수집) |
| v.daum.net, n.news.naver.com | 포털 뉴스 원문 (사실 확인) |
| en.wikipedia.org, ko.wikipedia.org | 배경 지식 확인 |

## 기업 보도자료 (사실 확인용, 사진은 조건 확인 후)
| 도메인 | 용도 |
|---|---|
| news.samsung.com | 삼성 뉴스룸 |
| www.lgnewsroom.com | LG 뉴스룸 |

## 소리·글꼴
| 도메인 | 용도 |
|---|---|
| freesound.org, cdn.freesound.org | 효과음 (CC0 필터로만 사용) |
| fonts.googleapis.com, fonts.gstatic.com | 무료 글꼴 (OFL) |
| raw.githubusercontent.com, github.com | 오픈소스 글꼴·도구 다운로드 |

## 유튜브
| 도메인 | 용도 |
|---|---|
| youtubeanalytics.googleapis.com | 대사별 시청 지속률 분석 (Analytics API) |
| youtube.googleapis.com | YouTube Data API (www.googleapis.com이 이미 있으면 보조) |

## 참고
- Reddit은 도메인을 허용해도 클라우드 IP를 Reddit 쪽에서 막음(403). 해결하려면 Reddit 공식 API(OAuth) 등록 필요
- API 키가 필요한 곳: Pexels, Pixabay, Unsplash, Flickr, 공공데이터포털, 기상청 API허브. 모두 무료 가입
