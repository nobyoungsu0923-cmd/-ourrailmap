# 우리의 노선도

전국 지하철·전철·기차 노선도 위에 **우리가 함께 간 역**마다 사진과 메모를 남기는 커플 앱.

## 기능
- **전국 54개 노선, 1,116개 역**: 수도권(1~9호선, 수인분당, 신분당, 경의중앙, 공항철도, GTX-A, 경전철들), 부산·김해·울산, 대구(대경선 포함), 대전, 광주, 그리고 KTX·SRT·일반 기차 노선
- **실제 지도 좌표 기반** 노선도: 손가락으로 이동/확대(핀치), 두 번 탭으로 확대
- **역 검색**: 이름 일부나 초성(`ㄱㄴ` → 강남)으로 바로 찾기, 노선 이름 검색하면 그 노선만 강조
- **역마다 추억 기록**: 날짜, 제목, 메모, 사진 여러 장 (사진은 자동으로 작게 줄여서 저장)
- 다녀온 역은 지도에 도장 표시, ⭐ 가고 싶은 역 담기
- **추억 모아보기**: 월별 타임라인, 노선별 정복률, 가고 싶은 역 목록
- **D-day**: 처음 만난 날을 넣으면 기록마다 D+며칠인지 표시
- 🎲 **데이트 역 뽑기**: 화면에 보이는 역 중 아직 안 가 본 곳 랜덤 추천
- **백업/불러오기**: 사진·메모는 폰 안에만 저장되니, 백업 파일로 다른 폰에 옮기거나 합칠 수 있음

## 파일 구조
```
our-railmap/
  index.html            ← 완성된 앱 (한 파일, 인터넷 없이 동작)
  src/app.html          ← 앱 소스 (화면/기능)
  data/network.json     ← 역·노선 데이터 (빌드 결과)
  data/korea.json       ← 해안선
  tools/lines.py        ← ★ 노선별 역 순서 (여기를 고치면 노선 수정)
  tools/build_data.py   ← lines.py + Wikidata 좌표 → network.json
  tools/build_html.py   ← src + data → index.html
```

## 노선/역 고치기
1. `tools/lines.py`에서 역 이름을 추가/수정 (좌표가 없으면 `MANUAL`에 위도·경도 추가)
2. `python3 tools/build_data.py && python3 tools/build_html.py`

## 폰에 설치 (APK)
push 하면 GitHub Actions의 **Build APK** 가 돌고,
Actions 실행 결과의 Artifacts에서 `our-railmap-apk` 를 받아 폰에 설치하면 돼.

역 위치 데이터: Wikidata (CC0) · 해안선: Natural Earth (public domain)
