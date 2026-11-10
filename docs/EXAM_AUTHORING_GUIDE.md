# AI 시험 문제 및 솔루션 제작 가이드 (Exam Authoring Guide)

이 문서는 교육 차수가 변경되거나 새로운 원본 소스 코드(`*_raw_source`)가 추가되었을 때, `practices/` 및 `solutions/` 노트북을 제작하고 `exam_app`과 연동하는 표준 절차와 규칙을 안내합니다.

---

## 1. 전체 제작 워크플로우

```mermaid
flowchart TD
    A["신규 원본 교육 소스 수령 (*_raw_source)"] --> B["핵심 실습 및 TODO 식별"]
    B --> C["솔루션 노트북 생성 (solutions/*_practice_solution.ipynb)"]
    C --> D["표준 3단 구조 및 빈칸 변환 (practices/*_practice.ipynb)"]
    D --> E["AST 채점 및 마커 무결성 자동 검증 (validate_exam.py)"]
    E -->|오류 발생| C
    E -->|검증 성공 (100%)| F["exam_app 연동 및 Playwright UI 테스트"]
```

---

## 2. 노트북 작성 규칙

### A. Markdown 셀 3단 표준 규격 (`parser.py` 연동)
각 문제는 레벨 2 헤딩(`##`)으로 시작하며, `[문제]`와 `[요구사항]` 섹션을 명확히 구분합니다.

* **Practice 노트북 헤딩**:
  ```markdown
  ## 문제 1. BPE Tokenizer encode / decode

  [문제]
  Q 1) BPE 토크나이저를 사용하여 입력 문자열을 정수 토큰 ID 리스트로 인코딩하고 다시 텍스트로 디코딩합니다.

  [요구사항]
  - tokenizer.encode 메서드를 호출하여 특별 토큰 허용 옵션과 함께 인코딩
  - tokenizer.decode 메서드를 호출하여 토큰 ID 시퀀스를 원본 문자열로 복원
  - ※ 사전 정의 컴포넌트: {코드 셀에 정의되지 않은 외부 객체/함수가 사용되는 경우 명시}
  ```

> [!IMPORTANT]
> **[요구사항] 작성 시 준수 규칙**:
> 1. **정답 코드 직접 노출 금지**: 슬라이싱 문법(`x[i:i+len]`), 수식 계산식(`-ln(sigmoid(x))`), 파라미터 리터럴을 그대로 적지 말고, 달성해야 할 논리/수학적 조건으로 서술합니다.
> 2. **미정의 외부 컴포넌트 명시**: 코드 셀에 정의되지 않은 헬퍼 함수나 클래스가 필요한 경우 반드시 `※ 사전 정의 컴포넌트: ...` 또는 `※ 사전 정의 함수: ...` 형태로 명시합니다.
> 3. **문제 완결성**: 응시자가 문제, 요구사항, 코드 영역만으로 의도를 이해하고 풀 수 있어야 합니다.

---

### B. 코드 셀 작성 및 빈칸 마커 규격

코드 셀 상단에는 `# [코드]` 주석을 명시합니다.

#### 1. Practice 코드 셀
채워야 할 빈칸은 **`### 작성 필요 ###`**로 표기합니다. 풀지 않은 상태에서 자연스럽게 `SyntaxError`가 발생하도록 우변이나 인자 위치에 지정합니다.

```python
# [코드]
tokenizer = tiktoken.get_encoding("gpt2")
integers = tokenizer.### 작성 필요 ###(text, allowed_special={"<|endoftext|>"})
strings = tokenizer.### 작성 필요 ###(integers)
```

#### 2. Solution 코드 셀
인라인 정답 마커 형식을 사용합니다: `### <정답 코드> ### 작성 필요 ###`

```python
# [코드]
tokenizer = tiktoken.get_encoding("gpt2")
integers = tokenizer.### encode ### 작성 필요 ###(text, allowed_special={"<|endoftext|>"})
strings = tokenizer.### decode ### 작성 필요 ###(integers)
```

#### 3. 정답 유추 방지 (공개 제한)
문제 풀이 과정에서 정답을 바로 유추할 수 있는 선행 클래스나 헬퍼 함수 블록은 `# ### 공개 제한 ###` 마커를 적용하여 가립니다.

```python
# [참고 모델 정의 - 세부 로직 비공개]
# ### 공개 제한 ###
class EncoderRNN(nn.Module):
    ...
```

---

## 3. 시험 앱 및 출제 규격

- **과목 키 및 파일 매핑** (`exam_app/parser.py`):
  - `total`: **종합 (전체 영역)** - Vision, Data, On-Device, LLM 4개 영역에서 골고루 총 10문항 균등 출제 (각 과목 2문항 + 무작위 2개 과목 각 1문항)
  - `vision`: `practices/vision_practice.ipynb` / `solutions/vision_practice_solution.ipynb` (10문항 랜덤 추출)
  - `llm`: `practices/llm_practice.ipynb` / `solutions/llm_practice_solution.ipynb` (10문항 랜덤 추출)
  - `data`: `practices/data_practice.ipynb` / `solutions/data_practice_solution.ipynb` (10문항 랜덤 추출)
  - `ondevice`: `practices/ondevice_practice.ipynb` / `solutions/ondevice_practice_solution.ipynb` (10문항 랜덤 추출)

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
Streamlit 10문항 로드, 3단 레이아웃 카드, 붉은색 뱃지 렌더링, 스플릿 뷰 동작을 헤드리스 브라우저로 최종 검증합니다.
