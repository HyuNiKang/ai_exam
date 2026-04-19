from __future__ import annotations

import ast
import difflib
import re
from dataclasses import dataclass


@dataclass
class GradeResult:
    status: str  # "correct" | "wrong" | "syntax_error"
    message: str = ""
    diff: str = ""


def _strip_placeholder_comments(code: str) -> str:
    """Remove the `### !!!!!!!!!!!!코드를 작성하세요!!!!!!!!!!!!` marker lines.

    These markers may appear as whole-line comments or inline after a value.
    If the user submits the problem unchanged we want them to fail grading (not
    parse error), so only strip when the line has no other content.
    """
    cleaned = []
    for line in code.splitlines():
        if re.fullmatch(r"\s*###\s*!+\s*코드를\s*작성하세요\s*!+\s*", line):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def normalize(code: str) -> str:
    """Normalize Python code for equivalence comparison.

    - Parse to AST then unparse: removes comments/docstrings, canonicalizes
      whitespace, quote style, redundant parentheses, etc.
    - Collapse remaining whitespace to single spaces for strict equality.
    """
    code = _strip_placeholder_comments(code)
    tree = ast.parse(code)
    canonical = ast.unparse(tree)
    canonical = re.sub(r"\s+", " ", canonical).strip()
    return canonical


def _render_diff(user_code: str, solution_code: str) -> str:
    user_lines = user_code.splitlines(keepends=True)
    sol_lines = solution_code.splitlines(keepends=True)
    diff = difflib.unified_diff(
        user_lines, sol_lines, fromfile="your answer", tofile="solution", n=2
    )
    return "".join(diff)


def grade(user_code: str, solution_code: str) -> GradeResult:
    try:
        user_norm = normalize(user_code)
    except SyntaxError as e:
        return GradeResult(
            status="syntax_error",
            message=f"제출한 코드에 문법 오류가 있습니다: {e.msg} (line {e.lineno})",
        )

    try:
        sol_norm = normalize(solution_code)
    except SyntaxError as e:
        return GradeResult(
            status="syntax_error",
            message=f"정답 파싱 실패(내부 오류): {e.msg}",
        )

    if user_norm == sol_norm:
        return GradeResult(status="correct", message="정답입니다!")

    return GradeResult(
        status="wrong",
        message="정답과 일치하지 않습니다.",
        diff=_render_diff(user_code, solution_code),
    )


if __name__ == "__main__":
    from parser import load_subject

    for subject in ("vision", "data", "ondevice"):
        problems = load_subject(subject)
        print(f"\n=== {subject} ===")
        for p in problems[:3]:
            # positive: feed the solution itself
            r1 = grade(p.solution_code, p.solution_code)
            # negative: mangle the solution a little
            mangled = p.solution_code.replace("dim=1", "dim=0").replace("0.5", "0.9")
            r2 = grade(mangled, p.solution_code)
            print(f"  Q{p.number}  self={r1.status}  mangled={r2.status}")
