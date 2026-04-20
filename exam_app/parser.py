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

# Inline solution marker used in data/ondevice/llm solution code cells:
#   `### <answer code> ## Write Answer`         (data, llm)
#   `### <answer code> ### ## Write Answer`     (ondevice)
# Captures the answer between the opening `###` and the `## Write Answer`
# marker, tolerating an optional closing `###` before the marker.
INLINE_SOLUTION_RE = re.compile(
    r"###\s*(.+?)\s*(?:###\s*)?##\s*Write\s*Answer",
    re.DOTALL,
)


@dataclass
class Problem:
    number: int
    title: str
    problem_code: str
    solution_code: str
    explanation: str


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

        explanation_parts = []
        if sg.intro_md:
            explanation_parts.append(sg.intro_md)
        between = _markdown_before_code(sg.cells)
        if between:
            explanation_parts.append(between)
        explanation = "\n\n".join(explanation_parts).strip()

        problems.append(
            Problem(
                number=num,
                title=title,
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
