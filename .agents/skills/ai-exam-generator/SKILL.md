---
name: ai-exam-generator
description: >-
  Use this skill when creating, updating, or validating practice and solution notebooks
  for the ai_exam platform and exam_app from raw educational training notebooks
  (e.g., Language_raw_source, vision_raw_source, ondevice_raw_source, data_raw_source, rag_raw_source).
---

# AI Exam Generator & Authoring Runbook

이 스킬은 교육 차수의 원본 소스 코드(`*_raw_source`)와 공통 기반 문서(`평가체크포인트.xlsx`, `AI인증시험_문제출제방식_공지사항.md`, `시험문제_제작_프롬프트.md`)를 바탕으로 `exam_app`에서 사용할 수 있는 `practices/` 및 `solutions/` 노트북을 제작하고 검증하는 표준 워크플로우를 제공합니다.

---

## 0. 공통 기반 자료 및 최우선 원칙

문제 제작 시 반드시 작업공간 루트의 다음 세 문서를 먼저 확인하고 기준을 적용합니다.

| 기반 자료 | 역할 및 적용 기준 |
| :--- | :--- |
| **`평가체크포인트.xlsx`** | 각 분야(LLM, RAG, DATA, VISION, On-Device)에서 무엇을 이해하고 구현할 수 있어야 하는지 확인하고, 문항의 주제와 우선순위를 정합니다. |
| **`AI인증시험_문제출제방식_공지사항.md`** | 코드 빈칸 채우기 방식(`### 작성 필요 ###`), 제공 코드 유지, 문항 번호(`a-1`, `a-2`), 요구사항 작성 방식 등 시험 형식을 확인합니다. |
| **`시험문제_제작_프롬프트.md`** | 실습 파일당 최대 20문항 상한, 핵심 문항 선별 기준(우선순위 높음/중간/낮음), 원본 코드 변형 금지, 논리적인 해설 및 각 줄 주석 제공 규칙을 준수합니다. |

### 핵심 출제 원칙 요약
1. **원본 코드 절대 유지 (변형·모의 구현 금지)**:
   - 원본 실습(`*_raw_source`)의 변수명·함수명·인자·import·수치·입력 크기·모델·데이터·연산 순서를 임의로 바꾸지 않습니다.
   - 별도 예제 모델이나 자체 제작한 모의 함수로 원본 코드를 대체하지 않습니다.
2. **독립 채점 가능한 단일 코드 셀 구성**:
   - 원본 코드와 변수/스켈레톤은 절대 변형하지 않되, `exam_app`에서 랜덤 추출 시 개별 문항 단위로 독립 채점(AST 비교)이 가능하도록 각 문항마다 원본의 해당 코드 블록(1개 코드 셀)을 담아 구성합니다.
3. **실습 파일당 최대 20문항 상한 및 핵심 선별**:
   - 각 원본 실습 파일(`.ipynb`)당 최대 20문항 이내에서 `평가체크포인트.xlsx`와 직결되는 핵심 문항(우선순위 높음/중간)만 엄선합니다. 단순 설치·다운로드·반복 조회 등 낮은 우선순위 문항으로 수를 채우지 않습니다.
   - `exam_app`에서는 과목 통합 노트북으로부터 시험 세션당 **10~15문항 내외(기본 12문항)**를 랜덤 추출하여 제공합니다.

---

## 1. 시험 문제 표준 규격 (Standard Exam Spec)

### A. 3단 레이아웃 및 문항 번호 병기 규격 (방안 A)
파서(`exam_app/parser.py`) 호환성을 위해 마크다운 헤딩에는 정수 일련번호(`1~N`)를 유지하고, 제목과 `[문제]` 본문에 원본 실습 순서에 맞춘 세부 번호(`a-1`, `a-2`, `b-1` 등)를 병기합니다.

```markdown
## 문제 1. (a-1) BPE Tokenizer 로드 및 인코딩

[문제]
Q a-1) gemma-2b 모델의 토크나이저를 불러옵니다.

[요구사항]
- `BASE_MODEL` 변수를 사용하여 사전 학습된 토크나이저를 로드하시오.
- ※ 사전 정의 컴포넌트: {코드 셀에 정의되어 있지 않은 외부/선행 헬퍼 클래스나 함수가 필요한 경우 반드시 명시}
```

```python
# [코드]
from transformers import AutoTokenizer

BASE_MODEL = 'google/gemma-2b'
tokenizer = ### 작성 필요 ###
```

### B. 표준 마커 규격

| 구분 | 마커 형식 | 용도 및 규칙 |
| :--- | :--- | :--- |
| **연습 빈칸** | `### 작성 필요 ###` | 응시자가 채워야 하는 빈칸 자리에 직접 배치 (`...`를 사용하지 않음). 미작성 시 자연스럽게 `SyntaxError`를 유발하도록 우변이나 인자 위치에 배치 |
| **솔루션 인라인 정답** | `### <answer> ### 작성 필요 ###` | Solution 코드 내에서 답안을 명시하고 파서 및 변환 스크립트가 정답을 자동 추출할 수 있도록 지정 |
| **공개 제한 (레퍼런스)** | `# ### 공개 제한 ###` | 정답을 유추할 수 있거나 참고 코드로 인해 답이 노출될 수 있는 선행/보조 코드 블록을 가릴 때 사용 |

---

## 2. [요구사항] 및 [해설] 작성 핵심 원칙

> [!IMPORTANT]
> **1. 요구사항 내 정답 코드 직접 노출 절대 금지**
> - 요구사항에 실제 채워야 할 정답 코드 스니펫(예: 특정 슬라이싱 문법 `x[i:i+len]`, 수식 `-ln(sigmoid(x))`, 정답 API 호출문 그대로 등)을 적지 마십시오.
> - 대신 **"작업 목적, 사용할 변수명, 입출력 텐서 형상/축(axis), 제약 조건"**으로 명확히 기술하되, 답을 그대로 옮겨 적는 문항이 되지 않도록 합니다.
>
> **2. 미정의 외부/로컬 함수 명시 의무**
> - 현재 코드 셀 내에 정의되어 있지 않은 선행 함수, 이전 단계 컴포넌트, 또는 외부 헬퍼를 빈칸에 채우거나 호출해야 하는 경우, 반드시 `[요구사항]` 하단에 `※ 사전 정의 컴포넌트/함수: ...` 형태로 시그니처와 역할을 명시하십시오.
>
> **3. 풍부한 핵심 원리 해설 및 정답 코드 줄별 주석 제공**
> - Solution 마크다운 해설에는 해당 코드가 **무엇을 하는지, 왜 필요한지, 앞뒤 처리와 어떻게 연결되는지**, 그리고 **`🎯 빈칸(### 작성 필요 ###)별 출제 포인트 & 파라미터 역할`**을 상세히 기술합니다.
> - Solution 코드 셀의 주요 실행 라인과 정답 라인에는 **각 코드의 역할과 주요 파라미터의 의미를 설명하는 한국어 인라인 주석(`# ...`)**을 충실히 추가합니다. (주석은 AST 정규화 시 자동 제거되므로 채점에 영향을 주지 않으며, UI의 정답 코드 보기에서 학습 효과를 높입니다.)

---

## 3. 시험 앱 및 5대 과목 출제 규격

- **과목 키 및 파일 매핑** (`exam_app/parser.py` & `exam_app/session.py`):
  - `total`: **종합 (전체 영역)** - 5개 전 과목(Vision, Data, On-Device, LLM, RAG)에서 골고루 총 **12문항**(10~15문항 내외) 균등 랜덤 출제 (각 과목 2문항 기본 + 무작위 2개 과목 각 1문항 추가)
  - `vision`: `practices/vision_practice.ipynb` / `solutions/vision_practice_solution.ipynb` (12문항 랜덤 추출)
  - `data`: `practices/data_practice.ipynb` / `solutions/data_practice_solution.ipynb` (12문항 랜덤 추출)
  - `ondevice`: `practices/ondevice_practice.ipynb` / `solutions/ondevice_practice_solution.ipynb` (12문항 랜덤 추출)
  - `llm`: `practices/llm_practice.ipynb` / `solutions/llm_practice_solution.ipynb` (12문항 랜덤 추출)
  - `rag`: `practices/rag_practice.ipynb` / `solutions/rag_practice_solution.ipynb` (12문항 랜덤 추출)

---

## 4. 문제 및 정답 제작 단계별 워크플로우

### 1단계: 공통 기반 확인 및 원본 소스 분석
1. `평가체크포인트.xlsx`, `AI인증시험_문제출제방식_공지사항.md`, `시험문제_제작_프롬프트.md`를 먼저 읽습니다.
2. 대상 `*_raw_source` 디렉터리 내의 원본 `.ipynb` 실습 파일들을 순회합니다.
3. 실습 파일별 최대 20문항 상한 내에서 출제포인트와 직접 연결되는 핵심 계산·변환·처리 블록을 선별하고 `a-1`, `a-2`, `b-1`... 번호를 매깁니다.

### 2단계: Solution 노트북 구성
1. Markdown 셀에 `## 핵심 개념 {N}. ({세부번호}) {제목}` 또는 `## 문제 {N}. ({세부번호}) {제목}` 형식으로 레벨 2 헤딩을 작성합니다.
2. **해설 작성**:
   - 핵심 원리(무엇을 하는지, 왜 필요한지, 앞뒤 단계 연결, 텐서 shape/축/인자 의미)를 설명합니다.
   - `🎯 빈칸(### 작성 필요 ###)별 출제 포인트 & 파라미터 역할` 섹션을 작성합니다.
3. 바로 뒤따르는 Code 셀 상단에 `# [코드]`를 추가하고, 원본 코드를 변형 없이 유지하되 정답 위치에 `### <answer> ### 작성 필요 ###` 인라인 마커와 상세 한국어 주석을 작성합니다.

### 3단계: Practice 노트북 자동 생성 및 정제
1. Solution 노트북으로부터 [generate_practice_from_solution.py](./scripts/generate_practice_from_solution.py) 스크립트를 실행하거나 생성 스크립트를 통해 Practice 노트북을 생성합니다:
   ```bash
   python .agents/skills/ai-exam-generator/scripts/generate_practice_from_solution.py solutions/<과목>_practice_solution.ipynb practices/<과목>_practice.ipynb
   ```
2. 생성된 Practice 노트북에서:
   - 미작성 시 자연스럽게 `SyntaxError`가 발생하도록 `### 작성 필요 ###` 위치를 확인합니다.
   - 앞뒤에 정답을 쉽게 유추할 수 있는 참조 코드가 있는 경우 `# ### 공개 제한 ###` 마커를 적용합니다.

### 4단계: 무결성 및 자동 채점 검증 (필수)
제작 후 반드시 검증 스크립트를 실행하여 모든 과목의 모든 문항이 문법 오류 없이 통과하는지 확인합니다:

```bash
python .agents/skills/ai-exam-generator/scripts/validate_exam.py
```

**통과 기준**:
- ✅ 모든 과목(`vision`, `data`, `ondevice`, `llm`, `rag`)의 모든 문항 AST 채점 결과가 `status="correct"` 이어야 함.
- ✅ 모든 문항에 빈칸 마커(`### 작성 필요 ###`)가 1개 이상 존재해야 함.
- ✅ 미작성 상태의 `problem_code` 제출 시 `status="syntax_error"`가 반환되어야 함.
- ❌ 검증 실패 문항이 0건이어야 함.

### 5단계: Streamlit UI 및 Playwright 검증
```bash
# Playwright 자동화 테스트 실행 (스크린샷 및 UI 무결성 확인)
python scratch/test_ui_playwright.py
```
- 좌측 사이드바에서 `종합 (전체 영역)` 및 5개 개별 과목이 정상 로드되는지 확인합니다.
- `[문제]` 카드, `[요구사항]` 카드, 빈칸 배지, 그리고 오답 제출 시 자동 펼쳐지는 빈칸별 정답 대조표 및 주석 포함 정답 코드가 정상 작동하는지 확인합니다.
