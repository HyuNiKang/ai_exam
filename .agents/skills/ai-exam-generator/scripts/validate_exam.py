"""AI Exam Practice and Solution AST Validation Script

This script validates all problem and solution pairs across subjects
to ensure they parse correctly and achieve status="correct" under grader.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from exam_app.grader import grade
from exam_app.parser import load_all


def main() -> int:
    print("=" * 65)
    print("AI EXAM INTEGRITY AND AST VALIDATION REPORT")
    print("=" * 65)

    all_subjects = load_all()
    total_problems = 0
    total_failures = 0

    for subject, problems in all_subjects.items():
        print(f"\n📂 [과목: {subject.upper()}] 총 {len(problems)} 문항")
        subj_failed = 0

        for p in problems:
            total_problems += 1
            has_marker = "### 작성 필요 ###" in p.problem_code or "## Write Answer" in p.problem_code
            result = grade(p.solution_code, p.solution_code)

            if result.status != "correct":
                subj_failed += 1
                total_failures += 1
                print(f"  ❌ Q{p.number:02d}. {p.title}")
                print(f"     채점 실패: status={result.status}, msg={result.message}")
            elif not has_marker:
                subj_failed += 1
                total_failures += 1
                print(f"  ⚠️ Q{p.number:02d}. {p.title}")
                print("     경고: 문제 코드에 '### 작성 필요 ###' 빈칸 마커가 없습니다.")
            else:
                print(f"  ✅ Q{p.number:02d}. {p.title}")

        if subj_failed == 0:
            print(f"  🎯 {subject.upper()} 모든 문항 정상 검증 완료!")
        else:
            print(f"  ⚠️ {subject.upper()} {subj_failed}개 문항에서 이상 발견!")

    print("\n" + "=" * 65)
    if total_failures == 0:
        print(f"🎉 전체 검증 성공: 총 {total_problems}개 문항 모두 정상입니다.")
        return 0
    else:
        print(f"❌ 전체 검증 실패: 총 {total_failures}개 문제 확인이 필요합니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
