# AI 시험 연습 (exam_app)

Streamlit 기반의 AI 시험 문제 풀이 연습 앱입니다. `practices/`의 빈칸 문제를 코드 에디터에 채워 제출하면, `solutions/`의 정답과 비교해 채점·diff를 보여줍니다.

## 요구 사항

- [uv](https://docs.astral.sh/uv/) (패키지·가상환경 관리)
- Python 3.10 이상 (uv가 자동 설치)

### uv 설치

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 확인:

```bash
uv --version
```

## 환경 설정

`exam_app` 디렉터리로 이동 후 `uv sync`로 가상환경과 의존성을 한 번에 준비합니다.

```bash
cd exam_app
uv sync
```

- `.venv/`가 생성되고 `pyproject.toml` / `uv.lock`에 정의된 패키지(Streamlit, nbformat 등)가 설치됩니다.
- 별도의 `activate` 불필요 — 이후 명령은 `uv run ...`으로 실행합니다.

## 실행

```bash
cd exam_app
uv run streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시된 `Local URL` (기본 http://localhost:8501) 을 열어 주세요.

포트를 바꾸거나 외부에서 접속해야 한다면:

```bash
uv run streamlit run app.py --server.port 8502 --server.address 0.0.0.0
```

## 사용 방법

1. 좌측 사이드바에서 과목(`종합 (전체 영역)` / `Vision` / `Data / Time Series` / `On-Device AI` / `LLM` / `RAG`)을 선택합니다.
2. 각 과목 선택 시 **12문제가 랜덤으로 추출**되어 모의 테스트 세션이 구성됩니다 (`종합` 선택 시 5개 영역에서 골고루 균등 추출).
3. 상단의 `[문제]` 및 `[요구사항]` 카드와 **🎯 답변 작성 필수 위치**를 확인하고, `### 작성 필요 ###` 영역을 올바른 코드로 채워 **✅ 제출**을 누르면 정답과 비교하여 자동 채점 및 빈칸별 정답 대조·해설을 보여줍니다.
4. **↺ 문제 초기화**를 누르면 에디터의 작성 내용이 문제의 초기 코드로 즉시 깨끗하게 초기화됩니다.
5. **🔀 다시 섞기**: 과목 전체 풀에서 새로운 12문제를 다시 무작위로 추출하여 새 테스트를 진행합니다.
6. **🔢 순서대로**: 앞선 12문제를 번호 순서대로 확인합니다.
7. **📚 전체 문제 학습 모드**: 시험 전 과목의 모든 문제를 순서대로 학습하고자 할 때 사용합니다.

## 디렉터리 구조

```
ai_exam/
├── exam_app/              # 본 Streamlit 앱
│   ├── app.py             # 엔트리포인트
│   ├── parser.py          # .ipynb 문제/정답 파싱
│   ├── grader.py          # 코드 채점 및 diff 생성
│   ├── session.py         # Streamlit 세션 상태 관리
│   ├── pyproject.toml     # uv 프로젝트 메타 / 의존성
│   └── uv.lock
├── practices/             # 빈칸 문제 notebook
└── solutions/             # 정답 notebook
```

`parser.py`는 `exam_app`의 상위 디렉터리에 있는 `practices/`, `solutions/`를 참조합니다. 실행은 반드시 `ai_exam/exam_app`에서 수행해 주세요.

## 의존성 관리

새 패키지를 추가하려면:

```bash
cd exam_app
uv add <package-name>
```

의존성만 동기화하고 싶다면 `uv sync`, 업그레이드는 `uv lock --upgrade && uv sync`를 사용합니다.
