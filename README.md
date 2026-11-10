# AI Specialist Exam Practice Platform (`ai_exam`)

AI 스페셜리스트 자격/역량 시험 대비를 위한 인터랙티브 학습 및 모의고사 플랫폼입니다.  
교육 차수별 원본 소스 코드로부터 핵심 실습 문제를 생성하고, Streamlit 기반의 **`exam_app`**을 통해 웹 환경에서 문제를 풀고 실시간 자동 채점 및 코드 diff를 확인할 수 있습니다.

---

## 📁 프로젝트 구조

```text
ai_exam/
├── exam_app/                    # Streamlit 기반 문제 풀이 및 자동 채점 웹 앱
│   ├── app.py                   # 웹 앱 엔트리포인트 (UI)
│   ├── parser.py                # .ipynb 문제/정답 파싱 엔진
│   ├── grader.py                # Python AST 정규화 및 Diff 비교 채점 엔진
│   ├── session.py               # 세션 상태 관리 (진행도, 정오답 기록)
│   ├── pyproject.toml           # 앱 패키지 및 의존성 설정
│   └── README.md                # exam_app 상세 설명서
│
├── practices/                   # 수험자용 실습 문제 노트북 (빈칸 포함)
│   ├── llm_practice.ipynb       # LLM 실습 문제 (19문항)
│   ├── vision_practice.ipynb    # Vision 실습 문제 (23문항)
│   ├── data_practice.ipynb      # Data/Time Series 실습 문제 (11문항)
│   └── ondevice_practice.ipynb  # On-Device AI 실습 문제 (16문항)
│
├── solutions/                   # 정답 및 해설 노트북
│   ├── llm_practice_solution.ipynb
│   ├── vision_practice_solution.ipynb
│   ├── data_practice_solution.ipynb
│   └── ondevice_practice_solution.ipynb
│
├── Language_raw_source/         # [이번 차수] LLM 분야 원본 교육 소스 (Chapter 1~7)
├── vision_raw_source/           # [이번 차수] Vision 분야 원본 교육 소스 (ResNet, ViT, DETR, U-Net)
├── ondevice_raw_source/         # On-Device 분야 원본 교육 소스
│
├── docs/                        # 다음 차수 문제 제작 및 유지보수 문서
│   └── EXAM_AUTHORING_GUIDE.md  # 차수별 문제/솔루션 제작 및 검증 가이드
│
├── .agents/skills/              # Antigravity 에이전트 자동화 스킬
│   └── ai-exam-generator/       # 다음 차수 소스 변환 및 검증 자동화 스킬
│
└── .gitignore                   # 불필요한 캐시/체크포인트 차단 설정
```

---

## 🎯 지원 과목 및 문항 구성

| 과목 키 | 과목명 | 문항 수 | 원본 교육 소스 및 주요 출제 범위 |
|:---:|:---|:---:|:---|
| **`llm`** | Large Language Model | **19문항** | `Language_raw_source/` (BPE 토크나이저, Next-Token, Dataset, Causal Attention, MHA, LayerNorm, FeedForward, TransformerBlock, GPTModel, Pretraining Loss, Train Loop, LoRA Layer & Injection, 분류 Fine-tuning, SFT Collate, DPO Loss) |
| **`vision`** | Computer Vision | **23문항** | `vision_raw_source/` (CIFAR-10 Augmentation, Top-1 Accuracy, Confusion Matrix, Train Loop 3단계, SGD Momentum, ViT PreNorm/FeedForward/inner_dim/Einsum Attention/Patch Embedding/CLS+Pos, DETR 전처리/Box 변환/픽셀 복원/신뢰도 필터링, U-Net DoubleConv/Down/Up/Skip Connection Concat) |
| **`data`** | Data / Time Series | **11문항** | Sliding Window, LSTM, Conv1D, Encoder-Decoder, NCF, Precision/Recall@k, NGCF, BPR Loss |
| **`ondevice`** | On-Device AI | **16문항** | Magnitude Pruning (Fine-grained/Channel/Kernel/Global/LLM), Wanda Pruning, Linear/K-means Quantization, Knowledge Distillation (KL/Cosine/MSE) |

---

## 🚀 빠른 시작 (`exam_app` 실행)

### 1. 요구 사항
- Python 3.10 이상
- 패키지 의존성: `streamlit`, `streamlit-code-editor`, `nbformat`

### 2. 실행 방법

#### 방법 A: 기본 Python 환경에서 실행
```bash
cd exam_app
pip install -r requirements.txt
streamlit run app.py
```

#### 방법 B: `uv` 가상환경 도구 사용 시
```bash
cd exam_app
uv sync
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 좌측 사이드바에서 원하는 과목을 선택하고 문제를 풀이합니다.

---

## ⚙️ 채점 및 문제 작성 메커니즘

### 1. 문제-정답 파싱 규칙 (`parser.py`)
- **헤딩 규칙**: Markdown 셀에 `## 문제 {번호}. {제목}` (또는 `## 핵심 개념 {번호}. {제목}`) 형태로 레벨 2 헤딩 작성
- **문제 코드 (`practices/`)**: 수험자가 채워야 하는 빈칸에 `## Write Answer` 마커 삽입
- **정답 코드 (`solutions/`)**:
  - 인라인 마커: `### <정답코드> ## Write Answer` 형태 (파서가 정답 코드를 자동 추출)
  - 완성형 코드: 마커 없이 순수 정답 코드가 작성되어 있는 경우 그대로 채점 코드로 사용

### 2. AST 정규화 채점 엔진 (`grader.py`)
- Python의 `ast.parse` 및 `ast.unparse`를 사용하여 공백, 주석, 줄바꿈, 괄호 스타일의 차이로 인한 오답 처리를 방지하고 문법적/의미적 동일성을 검증합니다.
- 제출 코드가 정답과 다를 경우 `difflib` 기반의 Unified Diff를 수험자에게 직관적으로 보여줍니다.

---

## 🛠️ 다음 차수 교육 소스 반영 방법

새로운 교육 차수 소스가 추가되었을 때 손쉽게 `practices/` 및 `solutions/`를 갱신할 수 있도록 제작 가이드와 자동화 스킬을 제공합니다:
- **상세 가이드**: [docs/EXAM_AUTHORING_GUIDE.md](file:///c:/Doc_Back/ai_exam/docs/EXAM_AUTHORING_GUIDE.md)
- **에이전트 스킬**: [.agents/skills/ai-exam-generator/SKILL.md](file:///c:/Doc_Back/ai_exam/.agents/skills/ai-exam-generator/SKILL.md)
- **자동 검증 도구**: `python .agents/skills/ai-exam-generator/scripts/validate_exam.py`

