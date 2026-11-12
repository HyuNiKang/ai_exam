"""Utility script to generate or update practice notebook from solution notebook.

- Replaces `### <answer> ### 작성 필요 ###` (or legacy `## Write Answer`)
  inline solution markers with `### 작성 필요 ###`.
- Ensures Markdown headings adhere to the standard 3-part layout:
  [문제], [요구사항], [코드].
- Inserts `# [코드]` at the top of practice code cells.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Match both new and legacy solution inline markers
INLINE_SOLUTION_RE = re.compile(
    r"###(?!\s*공개\s*제한)\s*([^\n]+?)\s*(?:###\s*)?(?:###\s*작성\s*필요\s*###|##\s*Write\s*Answer)"
)
HEADING_RE = re.compile(
    r"^\s*##\s+[^\n]*?(?:문제|Problem|개념)\s+(\d+)\.?\s*(.*?)\s*$",
    re.MULTILINE,
)


def ensure_three_part_markdown(source: str, num: int, title: str) -> str:
    """Format markdown into standard [문제] and [요구사항] sections if not present."""
    if "[문제]" in source and "[요구사항]" in source:
        return source

    clean_title = title.strip() or f"문제 {num}"
    body = HEADING_RE.sub("", source, count=1).strip()

    q_text = f"Q {num}) {clean_title}"
    req_text = "- 제시된 입출력 규격 및 전제조건을 만족하도록 구현하세요.\n- 불필요한 외부 라이브러리 사용을 지양하세요."

    if body:
        # If explanation body exists, use it as part of objective
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        if lines:
            q_text = f"Q {num}) {lines[0]}"

    return (
        f"## 문제 {num}. {clean_title}\n\n"
        f"[문제]\n{q_text}\n\n"
        f"[요구사항]\n{req_text}"
    )


def solution_to_practice(solution_path: Path, practice_path: Path) -> None:
    with open(solution_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    current_num = 0
    current_title = ""

    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type")
        raw_source = "".join(cell.get("source", []))

        if cell_type == "markdown":
            m = HEADING_RE.search(raw_source)
            if m:
                current_num = int(m.group(1))
                current_title = m.group(2).strip()
                new_md = ensure_three_part_markdown(raw_source, current_num, current_title)
                cell["source"] = [line + "\n" for line in new_md.splitlines()]
                if cell["source"]:
                    cell["source"][-1] = cell["source"][-1].rstrip("\n")

        elif cell_type == "code":
            # 1. Replace solution markers with standard practice placeholder
            new_source = INLINE_SOLUTION_RE.sub("### 작성 필요 ###", raw_source)
            new_source = re.sub(r"##\s*Write\s*Answer", "### 작성 필요 ###", new_source)

            # 2. Ensure `# [코드]` prefix
            if not new_source.startswith("# [코드]"):
                new_source = "# [코드]\n" + new_source

            cell["source"] = [line + "\n" for line in new_source.splitlines()]
            if cell["source"]:
                cell["source"][-1] = cell["source"][-1].rstrip("\n")

    with open(practice_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"Generated practice notebook: {practice_path} from {solution_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_practice_from_solution.py <solution_nb> <practice_nb>")
        sys.exit(1)
    solution_to_practice(Path(sys.argv[1]), Path(sys.argv[2]))
