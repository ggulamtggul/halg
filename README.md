# LG ThinQ Web Dashboard Custom Integration for Home Assistant (HACS)

이 통합 구성요소는 `https://my.lgthinq.com/` 웹 대시보드 포털의 로그인 세션 및 내부 API를 에뮬레이션하여 LG ThinQ 로봇청소기를 홈어시스턴트(Home Assistant)에 연동하고 제어합니다.

## 주요 특징
* **웹앱 에뮬레이션**: 공식 Open API의 제한된 기능 대신, 씽큐 웹 대시보드 내부 API를 시뮬레이션하여 보다 풍부한 연동 가능성을 열어줍니다.
* **로봇청소기(Vacuum) 제어**: 청소 시작/일시정지/복귀(충전) 기능 지원
* **센서(Sensor) 연동**: 로봇청소기 배터리 잔량(%), 현재 동작 상태, 작업 모드 데이터 조회

## 설치 방법 (HACS Custom Repository 등록)
1. Home Assistant에서 **HACS > 통합(Integrations)** 메뉴로 이동합니다.
2. 우측 상단의 점 세 개(⋮) 버튼을 누르고 **사용자 지정 저장소(Custom repositories)**를 선택합니다.
3. 이 깃허브 저장소(Repository) URL을 복사하여 주소창에 넣고, 범주(Category)를 **통합 구성요소(Integration)**로 선택한 후 추가합니다.
4. 다운로드 목록에 나타나면 설치를 누릅니다.
5. Home Assistant를 **재시작**합니다.

## 설정 방법
1. **설정 > 기기 및 서비스 > 통합 구성요소 추가**로 이동합니다.
2. **LG ThinQ Web Control (Custom)**을 검색하여 선택합니다.
3. LG 씽큐 앱 로그인에 사용하는 **이메일 ID**와 **비밀번호**, **국가 코드(KR)**를 입력하고 로그인을 마칩니다.
