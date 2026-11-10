---
name: ai-exam-generator
description: >-
  Use this skill when creating, updating, or validating practice and solution notebooks
  for the ai_exam platform and exam_app from raw educational training notebooks (e.g., Language_raw_source, vision_raw_source, ondevice_raw_source).
---

# AI Exam Generator & Authoring Runbook

이 스킬은 교육 차수의 소스 코드(`*_raw_source`)로부터 `exam_app`에서 사용할 수 있는 `practices/` 및 `solutions/` 노트북을 제작하고 검증하는 완전한 표준 워크플로우를 제공합니다.

---

## 1. 시험 문제 표준 규격 (Standard Exam Spec)

실제 시험 환경과 동일하게 응시자가 명확하게 문제를 파악하고 풀 수 있도록 다음 3단 구조와 마커 표준을 엄격히 준수합니다.

### A. 3단 레이아웃 구조
각 문제는 마크다운 셀과 코드 셀에 걸쳐 아래의 3개 표준 섹션으로 구성됩니다.

```markdown
## 문제 {N}. {문제 제목}

[문제]
Q {N}) {문제의 주제와 명확한 수행 목표를 기술합니다.}

[요구사항]
- {전제조건, 입출력 텐서 형상, 제약사항 등을 기술합니다.}
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
| **연습 빈칸** | `### 작성 필요 ###` | 응시자가 채워야 하는 빈칸. 미작성 시 자연스럽게 `SyntaxError`를 유발하도록 우변이나 인자 위치에 배치 |
| **솔루션 인라인 정답** | `### <answer> ### 작성 필요 ###` | Solution 코드 내에서 답안을 명시하고 파서가 정답을 자동 추출할 수 있도록 지정 |
| **공개 제한 (레퍼런스)** | `# ### 공개 제한 ###` | 정답을 유추할 수 있거나 문제 풀이에 직접 필요하지 않은 헬퍼/참조 코드 블록을 가릴 때 사용 |

---

## 2. [요구사항] 작성 핵심 원칙 (Authoring Rules)

> [!IMPORTANT]
> **1. 정답 코드 직접 노출 절대 금지**
> - 요구사항에 실제 채워야 할 정답 코드 스니펫(예: 특정 슬라이싱 문법 `x[i:i+len]`, 수식 `-ln(sigmoid(x))`, 함수 호출문 등)을 그대로 적지 마십시오.
> - 대신 **"수행해야 할 논리/수학적 목표, 텐서 차원/축(axis), 입출력 규격 및 전제조건"**으로 기술해야 합니다.
>
> **2. 미정의 외부/로컬 함수 명시 의무**
> - 현재 코드 셀 내에 정의되어 있지 않은 선행 함수, 이전 단계 컴포넌트, 또는 외부 헬퍼를 빈칸에 채우거나 호출해야 하는 경우, 응시자는 무엇이 주어져 있는지 알 수 없습니다.
> - 반드시 `[요구사항]` 하단에 `※ 사전 정의 컴포넌트: ...` 또는 `※ 사전 정의 함수: ...` 형태로 시그니처와 함께 명시하십시오.
>
> **3. 문제 완결성 보장**
> - `[문제]`, `[요구사항]`, `[코드]` 영역 외의 알 수 없는 전역 변수나 임의의 객체가 `### 작성 필요 ###`의 대상이 되지 않도록 독립적이고 완결된 문맥을 제공하십시오.

---

## 3. 시험 앱 및 출제 규격

- **과목 키 및 파일 매핑** (`exam_app/parser.py`):
  - `total`: **종합 (전체 영역)** - 4개 과목 전체에서 골고루 총 10문항 균등 출제 (각 과목 2문항 + 무작위 2개 과목 각 1문항)
  - `vision`: `practices/vision_practice.ipynb` / `solutions/vision_practice_solution.ipynb` (10문항 랜덤 추출)
  - `llm`: `practices/llm_practice.ipynb` / `solutions/llm_practice_solution.ipynb` (10문항 랜덤 추출)
  - `data`: `practices/data_practice.ipynb` / `solutions/data_practice_solution.ipynb` (10문항 랜덤 추출)
  - `ondevice`: `practices/ondevice_practice.ipynb` / `solutions/ondevice_practice_solution.ipynb` (10문항 랜덤 추출)

---

## 4. 문제 및 정답 제작 단계별 워크플로우

### 1단계: 원본 소스 분석
1. 새로 제공된 `*_raw_source` 디렉터리 내의 `.ipynb` 파일들을 순회합니다.
2. 각 노트북의 `# TODO`, `????`, 또는 핵심 모델 블록(Layer, Attention, Loss, Training Loop)을 파악합니다.
3. 독립적으로 동작하고 채점 가능한 단위 코드를 선별합니다.

### 2단계: Solution 노트북 구성
1. Markdown 셀에 `## 핵심 개념 {N}. {제목}` 또는 `## 문제 {N}. {제목}` 형식으로 레벨 2 헤딩을 작성합니다.
2. **해설 작성 원칙**:
   - 해당 문제의 **핵심 원리**(정의, 수식, 입출력 텐서 흐름)를 설명합니다.
   - **빈칸(`### 작성 필요 ###`)별 출제 포인트 및 원리**를 번호별로 명시하여, 틀린 응시자가 왜 그 코드가 들어가야 하는지 스스로 이해하고 넘어갈 수 있도록 보강합니다.
3. 바로 뒤따르는 Code 셀 상단에 `# [코드]`를 추가하고, 정답 코드를 인라인 마커 형식으로 작성합니다:
   ```python
   # [코드]
   def accuracy_top1(logits, targets):
       preds = ### logits.argmax(dim=1) ### 작성 필요 ###
       return (preds == targets).float().mean().item()
   ```

### 3단계: Practice 노트북 자동 생성 및 정제
1. Solution 노트북으로부터 [generate_practice_from_solution.py](./scripts/generate_practice_from_solution.py) 스크립트를 실행하여 Practice 노트북을 자동 변환합니다:
   ```bash
   python .agents/skills/ai-exam-generator/scripts/generate_practice_from_solution.py solutions/<과목>_practice_solution.ipynb practices/<과목>_practice.ipynb
   ```
2. 생성된 Practice 노트북을 열어:
   - 미작성 시 자연스럽게 `SyntaxError`가 발생하도록 빈칸 위치를 점검합니다.
   - 앞뒤에 정답을 쉽게 유추할 수 있는 참조 코드가 있는 경우 `# ### 공개 제한 ###` 마커를 적용합니다.

### 4단계: 무결성 및 자동 채점 검증 (필수)
제작 후 반드시 검증 스크립트를 실행하여 모든 문항이 문법 오류 없이 통과하는지 확인합니다:

```bash
python .agents/skills/ai-exam-generator/scripts/validate_exam.py
```

**통과 기준**:
- ✅ 모든 문항의 AST 채점 결과가 `status="correct"` 이어야 함.
- ✅ 모든 문항에 빈칸 마커(`### 작성 필요 ###`)가 1개 이상 존재해야 함.
- ❌ 검증 실패 문항이 0건이어야 함.

### 5단계: Streamlit UI 및 Playwright 검증
```bash
# 앱 실행 확인
streamlit run exam_app/app.py

# Playwright 자동화 테스트 실행 (스크린샷 및 UI 무결성 확인)
python scratch/test_ui_playwright.py
```
- 좌측 사이드바에서 `종합 (전체 영역)` 및 개별 과목이 10문제 단위로 정상 로드되는지 확인합니다.
- `[문제]` 카드, `[요구사항]` 카드, 붉은색 빈칸 배지 및 접을 수 있는 위치 카드가 정상 작동하는지 확인합니다.
