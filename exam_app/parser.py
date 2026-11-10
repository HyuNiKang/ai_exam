from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
PRACTICE_DIR = ROOT / "practices"
SOLUTION_DIR = ROOT / "solutions"

SUBJECTS = {
    "vision": ("vision_practice.ipynb", "vision_practice_solution.ipynb"),
    "data": ("data_practice.ipynb", "data_practice_solution.ipynb"),
    "ondevice": ("ondevice_practice.ipynb", "ondevice_practice_solution.ipynb"),
    "llm": ("llm_practice.ipynb", "llm_practice_solution.ipynb"),
}

SUBJECT_LABELS = {
    "total": "종합 (전체 영역)",
    "vision": "Vision",
    "data": "Data / Time Series",
    "ondevice": "On-Device AI",
    "llm": "LLM",
}

# Match problem headings (level 2 only). Keyword can be:
#   문제 / Problem            (both practice and vision solution)
#   핵심 개념 / 개념 / 📌 개념 (data / ondevice solution)
HEADING_RE = re.compile(
    r"^\s*##\s+[^\n]*?(?:문제|Problem|개념)\s+(\d+)\.?\s*(.*?)\s*$",
    re.MULTILINE,
)

# Inline solution marker used in solution code cells:
#   `### <answer code> ### 작성 필요 ###`     (신규 표준)
#   `### <answer code> ## Write Answer`         (기존 레거시)
#   `### <answer code> ### ## Write Answer`     (ondevice 레거시)
INLINE_SOLUTION_RE = re.compile(
    r"###\s*(.+?)\s*(?:###\s*)?(?:###\s*작성\s*필요\s*###|##\s*Write\s*Answer)",
    re.DOTALL,
)


@dataclass
class Problem:
    id: str
    subject: str
    subject_label: str
    number: int
    title: str
    question: str
    requirements: str
    problem_code: str
    solution_code: str
    explanation: str


def _parse_sections(text: str, fallback_title: str = "") -> tuple[str, str]:
    """[문제] 와 [요구사항] 영역을 파싱합니다. 태그가 없으면 텍스트 전체를 문제로 취급합니다."""
    text_clean = text.strip()
    q_match = re.search(r"\[문제\]\s*(.*?)(?=\[요구사항\]|\Z)", text_clean, re.DOTALL)
    r_match = re.search(r"\[요구사항\]\s*(.*)", text_clean, re.DOTALL)

    question = q_match.group(1).strip() if q_match else ""
    requirements = r_match.group(1).strip() if r_match else ""

    if not question and not requirements:
        question = text_clean or fallback_title

    return question, requirements


@dataclass
class _Group:
    number: int
    title: str
    intro_md: str = ""   # text that followed the heading inside the heading cell
    cells: list = field(default_factory=list)


def _iter_cells_with_problems(nb) -> list[_Group]:
    groups: list[_Group] = []
    current: _Group | None = None
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            m = HEADING_RE.search(cell.source)
            if m:
                if current is not None:
                    groups.append(current)
                # Content of the heading cell after the heading line itself
                intro = HEADING_RE.sub("", cell.source, count=1).strip()
                current = _Group(
                    number=int(m.group(1)),
                    title=m.group(2).strip(),
                    intro_md=intro,
                )
                continue
        if current is not None:
            current.cells.append(cell)
    if current is not None:
        groups.append(current)
    return groups


def _first_code(cells) -> str:
    for c in cells:
        if c.cell_type == "code":
            return c.source
    return ""


def _markdown_before_code(cells) -> str:
    parts = []
    for c in cells:
        if c.cell_type == "code":
            break
        if c.cell_type == "markdown":
            parts.append(c.source)
    return "\n\n".join(parts).strip()


def _clean_solution_code(raw_code: str) -> str:
    """Replace inline `### answer ## Write Answer` markers with the answer.

    - Vision solutions have clean code and no markers → unchanged.
    - Data/ondevice/llm solutions embed the answer after `###` → extracted.
    """
    return INLINE_SOLUTION_RE.sub(r"\1", raw_code)


def load_subject(subject: str) -> list[Problem]:
    if subject == "total":
        # 4개 전 과목의 문제를 합쳐서 반환
        total_problems: list[Problem] = []
        for s in ("vision", "data", "ondevice", "llm"):
            total_problems.extend(load_subject(s))
        return total_problems

    practice_name, solution_name = SUBJECTS[subject]
    practice_nb = nbformat.read(PRACTICE_DIR / practice_name, as_version=4)
    solution_nb = nbformat.read(SOLUTION_DIR / solution_name, as_version=4)

    practice_groups = {g.number: g for g in _iter_cells_with_problems(practice_nb)}
    solution_groups = {g.number: g for g in _iter_cells_with_problems(solution_nb)}

    problems: list[Problem] = []
    for num in sorted(practice_groups):
        if num not in solution_groups:
            continue
        pg = practice_groups[num]
        sg = solution_groups[num]

        # Title comes from the practice notebook (user-facing)
        title = pg.title or sg.title

        problem_code = _first_code(pg.cells)
        solution_code_raw = _first_code(sg.cells)
        solution_code = _clean_solution_code(solution_code_raw)

        # [문제], [요구사항] 파싱
        combined_intro = pg.intro_md or ""
        question, requirements = _parse_sections(combined_intro, fallback_title=title)

        explanation_parts = []
        if sg.intro_md:
            explanation_parts.append(sg.intro_md)
        between = _markdown_before_code(sg.cells)
        if between:
            explanation_parts.append(between)
        explanation = "\n\n".join(explanation_parts).strip()

        problem_id = f"{subject}_{num}"
        label = SUBJECT_LABELS.get(subject, subject.upper())

        problems.append(
            Problem(
                id=problem_id,
                subject=subject,
                subject_label=label,
                number=num,
                title=title,
                question=question,
                requirements=requirements,
                problem_code=problem_code,
                solution_code=solution_code,
                explanation=explanation,
            )
        )
    return problems


def load_all() -> dict[str, list[Problem]]:
    return {subject: load_subject(subject) for subject in SUBJECTS}


if __name__ == "__main__":
    for subject, problems in load_all().items():
        print(f"{subject}: {len(problems)} problems")
        if problems:
            p = problems[0]
            print(f"  sample Q{p.number}. {p.title}")
            print("  solution_code preview:")
            for line in p.solution_code.splitlines()[:5]:
                print(f"    {line}")
