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

1. 좌측 사이드바에서 과목(Vision / Data / On-Device / LLM)을 선택합니다.
2. 코드 에디터의 `## Write Answer` 빈칸을 채워 **✅ 제출**을 누르면 정답과 비교합니다.
3. **↺ 문제 초기화**로 해당 문제의 코드를 원본으로 되돌릴 수 있습니다.
4. **🔢 순서대로 / 🔀 다시 섞기** 로 문제 순서를 바꿀 수 있으며, **문제 바로가기** 목록에서 정오답 현황을 확인할 수 있습니다.

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
