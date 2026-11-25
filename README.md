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
- **같이 보기 (실시간 동기화)**: 무료 Firebase 프로젝트 하나를 연결하면, 한쪽이 기록을 남기자마자 상대방 화면에도 바로 나타남 (아래 설정 방법 참고)

## 같이 보기 설정 (실시간 동기화)

사진과 메모는 기본적으로 **그 폰 안에만** 저장돼. 두 사람이 실시간으로 같이 보려면 무료 Firebase 프로젝트를 하나 만들어서 앱에 연결하면 돼. 5분 정도 걸리고, 한 번만 해두면 돼 (보통 커플 중 한 명만 설정하고, 나온 정보를 상대방 폰에도 똑같이 입력하면 됨).

1. https://console.firebase.google.com 접속해서 구글 계정으로 로그인.
2. **프로젝트 추가** → 이름은 아무거나 (예: `ourrailmap`) → Google Analytics는 꺼도 됨 → **만들기**.
3. 왼쪽 메뉴 **빌드(Build) → Firestore Database** → **데이터베이스 만들기** → 위치는 `asia-northeast3 (서울)` 추천 → **테스트 모드에서 시작**.
4. Firestore 화면 위쪽 **규칙(Rules)** 탭에서 아래 내용으로 전체를 바꾸고 **게시(Publish)**:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /rooms/{roomId}/{document=**} {
         allow read, write: if true;
       }
     }
   }
   ```
   (방 코드를 아는 사람만 그 방 데이터에 접근할 수 있는 간단한 규칙이야. 개인 용도로는 충분하지만, 방 코드는 비밀번호처럼 다른 사람에게 알려주지 않는 게 좋아.)
5. 왼쪽 위 톱니바퀴 → **프로젝트 설정** → **일반** 탭 맨 아래 **내 앱** → `</>` (웹) 아이콘 클릭 → 닉네임 아무거나 입력 → **앱 등록** (Firebase Hosting은 건너뛰어도 됨).
6. 나오는 `firebaseConfig` 객체에서 `apiKey` 값과 `projectId` 값을 복사.
7. 앱의 **우리의 노선도 → 같이 보기** 설정에서 **Firebase 프로젝트 ID**와 **API 키**를 붙여넣고, **코드 만들기**로 우리 방 코드를 만든 뒤 **연결하기**.
8. 여자친구(또는 남자친구) 폰에서도 같은 앱을 열고, 같은 **프로젝트 ID · API 키 · 방 코드**를 넣고 **연결하기**를 누르면 끝. 그 순간부터 기록·사진·설정이 서로 실시간으로 동기화돼.

Firebase 무료 요금제(Spark 플랜)는 하루 읽기 5만 회, 쓰기 2만 회까지 공짜라서 커플 둘이 쓰기엔 충분해.

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
