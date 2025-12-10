# 개발 환경 세팅 가이드 (Development Setup Guide)

이 문서는 Web Clipping Research Agent 프로젝트의 개발 환경을 설정하는 방법을 상세히 안내합니다.

## 전제 조건 (Prerequisites)

- **Python**: 3.11 이상 권장 (UV 패키지 매니저 사용 시 자동 관리 가능)
- **Node.js**: v18.17.0 이상 (Next.js 14 요구사항)
- **Git**: 소스 코드 버전 관리

## 1. 프로젝트 클론 (Clone)

```bash
git clone https://github.com/stomx/web-clipping-draft.git
cd web-clipping-draft
```

## 2. 백엔드 설정 (Backend Setup)

백엔드는 Python과 LangGraph로 구성되어 있습니다.

### 패키지 매니저 설치 (uv 권장)

이 프로젝트는 빠른 속도를 위해 `uv` 패키지 매니저를 사용합니다.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 의존성 설치

프로젝트 루트에서 다음 명령어를 실행하면 가상환경 생성 및 의존성 설치가 자동으로 진행됩니다.

```bash
uv sync
```

만약 `uv`를 사용하지 않는다면 표준 pip를 사용할 수 있습니다:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r pyproject.toml
```

### 환경 변수 (.env) 설정

루트 디렉토리에 `.env` 파일을 생성하고 다음 키를 입력해야 합니다.

```bash
cp .env.example .env
```

**필수 API 키**:
- `OPENAI_API_KEY`: GPT-4o 등 LLM 사용을 위해 필수.
- `TAVILY_API_KEY`: 웹 검색 에이전트 구동을 위해 필수 ([Tavily 가입](https://tavily.com/)).

**선택 API 키**:
- `YOUTUBE_API_KEY`: 유튜브 영상 검색 및 자막 추출 시 할당량 한도 해제를 위해 권장 (없어도 일부 기능 작동 가능하나 제한적).

## 3. 프론트엔드 설정 (Frontend Setup)

프론트엔드는 Next.js + React로 구성되어 `client` 디렉토리에 있습니다.

```bash
cd client
npm install
```

## 4. 로컬 개발 서버 실행

터미널을 2개 열어서 각각 실행하는 것을 권장합니다.

**Terminal 1: 백엔드 API 서버**
```bash
# 루트 디렉토리에서
uv run server/main.py
```
- 서버 상태 확인: `http://localhost:8000/docs` (Swagger UI)

**Terminal 2: 프론트엔드 개발 서버**
```bash
# client 디렉토리에서
cd client
npm run dev
```
- 웹 접속: `http://localhost:3000`

## 5. 트러블슈팅

### 모듈을 찾을 수 없음 (ModuleNotFoundError)
CLI 실행 시 `ModuleNotFoundError: No module named 'agent'` 에러가 발생하면, 실행 명령어를 확인하세요.
반드시 프로젝트 루트에서 실행하거나, `PYTHONPATH`에 루트가 포함되어야 합니다. `agent/main.py`에는 자동으로 루트 경로를 추가하는 코드가 포함되어 있습니다.

```bash
# 올바른 예시
uv run python -m agent.main "주제"
# 또는
cd agent && uv run python -m main "주제"
```

### API 키 오류
실행 중 401/403 에러가 발생하면 `.env` 파일의 API 키가 유효한지, 따옴표("") 공백 등이 잘못 들어가지 않았는지 확인하세요.
