# Desktop Cat Widget & Server (MVP)

목적
- Plan A: 데스크톱 고양이 위젯과 서버 기반(향후 VTuber 피치용) 토대를 마련.
- 배포는 GitHub Releases 사용, MVP 단계는 수동 업데이트 알림만 제공(자동 업데이트 없음).

리포 구조
- `/desktopcat` – PyQt6 위젯 라이브러리(프레임리스·항상 위·투명, 활성 창 기반 컨텍스트 전환).
- `/app` – (예약) 앱 통합/엔트리포인트.
- `/server` – FastAPI 백엔드(MVP 로그인/토큰, 공지 조회).
- `/assets` – 카테고리별 고양이 미디어.
- `/config` – JSON 설정(`asset_mapping.json`, `context_rules.json`).
- `/scripts` – 스크립트/유틸.

로컬 실행
### 서버(FastAPI)
1) 가상환경 생성/활성화: `python -m venv .venv` → `.\.venv\Scripts\Activate.ps1`
2) 의존성 설치(`/server`): `pip install -r requirements.txt`
3) 실행: `uvicorn server.main:app --reload`

### 클라이언트(데스크톱 위젯)
- 제품 엔트리포인트(트레이+대시보드 포함): `python -m app.main`
- 빠른 실행/데모: `python -m desktopcat.main`  
  특정 자산 사용: `python -m desktopcat.main path/to/cat.gif` (이 경우 컨텍스트 전환 비활성)
- 앱 코드에서 사용할 때: `from desktopcat.ui.widget import CatWidget`으로 임포트해 라이브러리처럼 사용. `desktopcat.main`은 데모/수동 실행용.

### 로그인/토큰 (MVP)
- 서버: `POST /auth/login`(email 기반 find-or-create → 토큰 발급), `GET /me`(토큰 인증).
- 대시보드: 이메일 로그인 UI, 성공 시 토큰을 로컬(`%APPDATA%/MeowBuddy/tokens/access_token.json`)에 저장하고 자동 로그인 시도. `GET /me`로 사용자 정보 표시(user_id, equipped_items).

### 공지(Notice) (MVP)
- 서버: `GET /notices`(토큰 인증)로 최신 공지 목록 반환, `POST /notices`(간단 입력)로 공지 추가 가능.
- 대시보드 Home: 공지 리스트 + 내용 표시, 로그인 시 자동 로드.
- 위젯: 새 공지가 있으면 작은 배지 표시, 배지 클릭 시 대시보드 Home 열기.
- 관리자 페이지: 서버에서 `/admin` HTML 제공(동일 오리진이라 CORS 이슈 최소). 브라우저에서 접속 후 Admin Secret, 제목, 내용을 입력해 공지 게시 가능.

### 관리자 공지 작성 사용법
1) `server/.env`에 `ADMIN_SECRET` 설정.
2) 서버 실행: `uvicorn server.main:app --reload`
3) 브라우저에서 `http://127.0.0.1:8000/admin` 접속 → Admin Secret/제목/내용 입력 → Publish.
4) 대시보드 Home/위젯에서 새 공지 확인(폴링 주기 기본 60초, 필요 시 조정).

설정 개요
- `config/asset_mapping.json`: 카테고리 → `/assets/cats` 하위 폴더/파일 매핑.
- `config/context_rules.json`: 활성 창 프로세스/제목 규칙 → 카테고리 매핑(폴링 주기, 기본 카테고리 포함).

배포/업데이트
- GitHub Releases로 배포.
- MVP는 수동 업데이트 알림만 표시(파일 자동 교체 없음).  
