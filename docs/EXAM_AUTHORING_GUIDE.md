# AI 시험 문제 및 솔루션 제작 가이드 (Exam Authoring Guide)

이 문서는 교육 차수가 변경되거나 새로운 원본 소스 코드(`*_raw_source`)가 추가되었을 때, 공통 기반(`평가체크포인트.xlsx`, `AI인증시험_문제출제방식_공지사항.md`, `시험문제_제작_프롬프트.md`)에 맞춰 `practices/` 및 `solutions/` 노트북을 제작하고 `exam_app`과 연동하는 표준 절차와 규칙을 안내합니다.

---

## 1. 전체 제작 워크플로우

```mermaid
flowchart TD
    A["공통 기반(평가체크포인트.xlsx, 공지사항, 제작 프롬프트) 및 신규 원본 소스(*_raw_source) 확인"] --> B["실습 파일당 최대 20문항 이내 핵심 후보 선별 (a-1, a-2, b-1...)"]
    B --> C["원본 코드 유지 + 단일 셀 독립 채점 구조로 솔루션 노트북 생성 (solutions/*_practice_solution.ipynb)"]
    C --> D["표준 3단 구조 및 빈칸 변환 (practices/*_practice.ipynb)"]
    D --> E["AST 채점 및 마커 무결성 자동 검증 (validate_exam.py)"]
    E -->|오류 발생| C
    E -->|검증 성공 (100%)| F["exam_app 5대 과목 연동 및 Playwright UI 테스트"]
```

---

## 2. 노트북 작성 규칙

### A. Markdown 셀 3단 표준 규격 및 문항 번호 병기 (`parser.py` 연동)
각 문제는 레벨 2 헤딩(`##`)으로 시작하며, 파서 호환을 위한 일련번호(`1~N`)와 원본 실습 흐름에 따른 세부 번호(`a-1`, `a-2`, `b-1`...)를 함께 표기합니다.

* **Practice 노트북 헤딩 및 본문 예시**:
  ```markdown
  ## 문제 1. (a-1) BPE Tokenizer encode / decode

  [문제]
  Q a-1) BPE 토크나이저를 사용하여 입력 문자열을 정수 토큰 ID 리스트로 인코딩하고 다시 텍스트로 디코딩합니다.

  [요구사항]
  - `tokenizer` 객체의 인코딩 메서드를 호출하여 특별 토큰 허용 옵션(`allowed_special`)과 함께 인코딩하시오.
  - 인코딩된 정수 리스트(`integers`)를 다시 원본 문자열로 복원하시오.
  - ※ 사전 정의 컴포넌트: {코드 셀에 정의되지 않은 외부 객체/함수가 사용되는 경우 명시}
  ```

> [!IMPORTANT]
> **핵심 출제 및 [요구사항] 작성 규칙**:
> 1. **원본 코드 절대 유지**: 원본 실습 코드의 변수명·함수명·인자·스켈레톤·수치를 임의로 변형하거나 모의 함수로 대체하지 않습니다.
> 2. **단일 코드 셀 독립 채점**: 각 문항마다 원본의 해당 코드 블록(1개 셀)을 담아 랜덤 추출 시에도 독립적인 AST 채점이 가능하도록 구성합니다.
> 3. **정답 코드 직접 노출 금지**: 슬라이싱 문법(`x[i:i+len]`), 수식 계산식(`-ln(sigmoid(x))`), 정답 API 호출문을 요구사항에 그대로 적지 않고, 달성해야 할 작업 목적과 조건으로 서술합니다.
> 4. **미정의 외부 컴포넌트 명시**: 코드 셀에 정의되지 않은 헬퍼 함수나 클래스가 필요한 경우 반드시 `※ 사전 정의 컴포넌트/함수: ...` 형태로 명시합니다.

---

### B. 코드 셀 작성 및 빈칸 마커 규격

코드 셀 상단에는 `# [코드]` 주석을 명시합니다.

#### 1. Practice 코드 셀
채워야 할 빈칸 자리에 **`### 작성 필요 ###`**를 직접 배치합니다 (`...`를 사용하지 않음). 미작성 상태에서 자연스럽게 `SyntaxError`가 발생하도록 우변이나 인자 위치에 지정합니다.

```python
# [코드]
tokenizer = tiktoken.get_encoding("gpt2")
integers = tokenizer.### 작성 필요 ###(text, allowed_special={"<|endoftext|>"})
strings = tokenizer.### 작성 필요 ###(integers)
```

#### 2. Solution 코드 셀
인라인 정답 마커 형식(`### <정답 코드> ### 작성 필요 ###`)을 사용하며, 학습자가 각 줄과 파라미터의 역할을 이해할 수 있도록 한국어 인라인 주석(`# ...`)을 함께 작성합니다.

```python
# [코드]
# GPT-2용 BPE 토크나이저 인코딩 로드
tokenizer = tiktoken.get_encoding("gpt2")
# allowed_special로 지정한 특수 토큰을 허용하며 텍스트를 정수 토큰 ID 리스트로 인코딩
integers = tokenizer.### encode ### 작성 필요 ###(text, allowed_special={"<|endoftext|>"})
# 정수 토큰 ID 리스트를 다시 원본 문자열로 디코딩
strings = tokenizer.### decode ### 작성 필요 ###(integers)
```

#### 3. 정답 유추 방지 (공개 제한)
문제 풀이 과정에서 정답을 바로 유추할 수 있는 선행 클래스나 참조 코드는 `# ### 공개 제한 ###` 마커를 적용하여 가립니다.

---

## 3. 시험 앱 및 5대 과목 출제 규격

- **과목 키 및 파일 매핑** (`exam_app/parser.py` & `exam_app/session.py`):
  - `total`: **종합 (전체 영역)** - Vision, Data, On-Device, LLM, RAG 5개 영역에서 골고루 총 **12문항**(10~15문항 내외) 균등 출제 (각 과목 2문항 + 무작위 2개 과목 각 1문항)
  - `vision`: `practices/vision_practice.ipynb` / `solutions/vision_practice_solution.ipynb` (12문항 랜덤 추출)
  - `data`: `practices/data_practice.ipynb` / `solutions/data_practice_solution.ipynb` (12문항 랜덤 추출)
  - `ondevice`: `practices/ondevice_practice.ipynb` / `solutions/ondevice_practice_solution.ipynb` (12문항 랜덤 추출)
  - `llm`: `practices/llm_practice.ipynb` / `solutions/llm_practice_solution.ipynb` (12문항 랜덤 추출)
  - `rag`: `practices/rag_practice.ipynb` / `solutions/rag_practice_solution.ipynb` (12문항 랜덤 추출)

---

## 4. 검증 명령어 및 도구

### A. 자동 변환 스크립트
```bash
python .agents/skills/ai-exam-generator/scripts/generate_practice_from_solution.py solutions/<과목>_practice_solution.ipynb practices/<과목>_practice.ipynb
```

### B. 무결성 및 AST 채점 검증
```bash
python .agents/skills/ai-exam-generator/scripts/validate_exam.py
```
모든 문항의 상태가 `status="correct"`이고 빈칸 마커가 정상 확인되어야 통과합니다.

### C. UI 자동화 검증
```bash
python scratch/test_ui_playwright.py
```
Streamlit 랜덤 문항 로드, 3단 레이아웃 카드, 빈칸 뱃지 렌더링, 해설 및 빈칸 대조표를 헤드리스 브라우저로 최종 검증합니다.
