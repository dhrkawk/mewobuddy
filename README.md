# Desktop Cat Widget

작은 고양이 위젯이 바탕화면 상단에 떠서 이미지/GIF/MP4를 보여주는 PyQt6 앱입니다. 컨텍스트(활성 창) 기반으로 자산을 바꿀 수 있도록 2단계 MVP를 구현했습니다.

## 실행
```bash
python -m desktopcat.main                # 기본 설정/자산 사용
python -m desktopcat.main path/to/cat.gif # 특정 파일 지정 시 컨텍스트 전환은 비활성화
```

## 구조
```
desktopcat/
  core/
    asset_manager.py      # 자산 해석/미디어 타입 판별
    config_loader.py      # asset_mapping.json 로더
    context_config.py     # context_rules.json 로더
    context_manager.py    # 활성 창 정보 기반 카테고리 전환
    window_info.py        # Windows 활성 창 프로세스/제목 조회(Win32)
  ui/
    widget.py             # 투명·프레임리스 위젯, 이미지/GIF/MP4 재생
assets/
  cats/
    idle/                 # 기본 자산 위치 (GIF/PNG/MP4 등)
config/
  asset_mapping.json      # 카테고리→폴더/파일 매핑
  context_rules.json      # 컨텍스트 매칭 규칙(프로세스/제목→카테고리)
```

## 컨텍스트 전환 (2단계)
- `config/context_rules.json`에 프로세스명 + 창 제목 키워드 기반 규칙을 정의합니다.
  - 예: VS Code/IntelliJ/Cursor → `coding`, Chrome/Edge에서 제목에 "YouTube"/"유튜브" → `youtube`, 그 외 브라우저 → `browsing`, 매칭 실패 시 `idle`.
- 앱 실행 시 타이머(기본 1000ms)로 활성 창 정보를 읽어 규칙을 매칭하고 카테고리가 바뀌면 자산을 교체합니다.
- 실행 시 파일 경로를 직접 넘기면 컨텍스트 전환 없이 해당 파일만 표시합니다.

## 규칙 설정 예시 (`config/context_rules.json`)
```json
{
  "poll_interval_ms": 1000,
  "default_category": "idle",
  "rules": [
    { "name": "coding_vscode", "process": ["code.exe"], "title_contains": [], "category": "coding" },
    { "name": "coding_intellij_family", "process": ["idea64.exe", "idea.exe", "pycharm64.exe", "pycharm.exe", "clion64.exe", "rider64.exe"], "title_contains": [], "category": "coding" },
    { "name": "coding_cursor", "process": ["cursor.exe"], "title_contains": [], "category": "coding" },
    { "name": "browser_youtube_music", "process": ["chrome.exe", "msedge.exe"], "title_contains": ["youtube music", "music.youtube", "유튜브 뮤직"], "category": "music" },
    { "name": "browser_youtube", "process": ["chrome.exe", "msedge.exe"], "title_contains": ["youtube", "유튜브"], "category": "youtube" },
    { "name": "browser_general", "process": ["chrome.exe", "msedge.exe", "firefox.exe"], "title_contains": [], "category": "browsing" }
  ]
}
```

## 자산 매핑 예시 (`config/asset_mapping.json`)
```json
{
  "assets_base": "assets/cats",
  "default_category": "idle",
  "categories": {
    "idle": { "folder": "idle", "preferred_file": "cat_idle.gif" },
    "coding": { "folder": "coding", "preferred_file": "cat_coding.gif" },
    "music": { "folder": "music", "preferred_file": "검정고양이음악.gif" },
    "youtube": { "folder": "youtube", "preferred_file": "cat_youtube.gif" },
    "browsing": { "folder": "browsing", "preferred_file": "cat_browsing.gif" }
  }
}
```

## 새 자산 추가
1) `assets/cats/<카테고리>/` 폴더를 만들고 GIF/PNG/MP4를 넣습니다. 여러 개면 `preferred_file`로 지정하거나 사전순 첫 파일이 사용됩니다.
2) `config/asset_mapping.json`에 해당 카테고리를 등록합니다.
3) 컨텍스트 전환에 쓰려면 `config/context_rules.json`의 규칙에서 `category` 이름을 매핑하세요.

## 유의사항
- 활성 창 정보는 Windows Win32 API를 사용합니다. 다른 OS 지원은 후순위입니다.
- MP4는 알파 채널을 지원하지 않습니다. 투명 배경을 원하면 GIF/PNG 시퀀스 등으로 변환해 사용하세요.
