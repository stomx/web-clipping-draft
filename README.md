# Deep Research Agent

LangGraph 기반의 웹 리서치 에이전트 서비스입니다. 사용자가 입력한 주제에 대해 웹(Tavily)과 유튜브 검색을 수행하고, 내용을 추출/요약하여 마크다운 보고서를 생성합니다.

![Screenshot](https://velog.velcdn.com/images/jaymon/post/8a6416e7-0f8b-47e1-b4a1-026049219b1b/image.png)

## 주요 기능

- **실시간 리포트 생성**: Server-Sent Events (SSE)를 통해 검색, 추출, 요약 과정을 실시간으로 스트리밍합니다.
- **멀티 소스 검색**: Tavily(웹 문서)와 YouTube API(비디오 자막)를 모두 활용합니다.
- **기간 필터링**: 최신 트렌드 파악을 위해 검색 기간을 설정할 수 있습니다.
- **자동 요약**: LLM을 사용하여 방대한 검색 결과를 핵심 요약으로 압축합니다.

## 프로젝트 구조

- `agent/`: LangGraph 에이전트 로직 (검색, 추출, 요약, 리포트 생성)
- `server/`: FastAPI 기반 백엔드 서버 (스트리밍 엔드포인트 제공)
- `client/`: Next.js 기반 웹 프론트엔드

## 설치 방법

### 1. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 API 키를 입력하세요.

```bash
cp .env.example .env
```

필요한 키:
- `OPENAI_API_KEY`: LLM 요약용
- `TAVILY_API_KEY`: 웹 검색용
- `YOUTUBE_API_KEY`: 유튜브 검색용

### 2. 의존성 설치 (Python)

```bash
uv sync
# 또는
pip install -r pyproject.toml
```

### 3. 클라이언트 설치 (Node.js)

```bash
cd client
npm install
```

## 실행 방법

### 웹 서비스 실행 (권장)

1. **백엔드 서버 시작**
   ```bash
   uv run server/main.py
   ```
   서버는 `http://localhost:8000`에서 실행됩니다.

2. **프론트엔드 시작**
   ```bash
   cd client
   npm run dev
   ```
   브라우저에서 `http://localhost:3000`으로 접속하세요.

### 터미널(CLI) 실행

웹 인터페이스 없이 터미널에서 바로 에이전트를 실행할 수 있습니다.

```bash
cd agent
uv run python -m main "연구 주제 입력" --count 3 --startDate 2024-01-01
```

**옵션 설명**:
- `--count`: 요약할 소스 개수 (기본값: 5)
- `--startDate / --endDate`: 검색 기간 설정 (YYYY-MM-DD)
- `--lang`: 출력 언어 (기본값: Korean)
- `--format`: 출력 포맷 (markdown / json)

## 라이선스

MIT License
