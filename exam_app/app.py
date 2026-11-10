from __future__ import annotations

import html
import re
import streamlit as st

import session as sess
from grader import grade
from parser import SUBJECT_LABELS, SUBJECTS, Problem, load_subject

st.set_page_config(page_title="AI 시험 연습", page_icon="🧠", layout="wide")

# ==============================================================================
# CSS Injection: IDE 스타일 폰트, 자동 줄바꿈, 붉은색 빈칸 & 제한 마커 하이라이트
# ==============================================================================
st.markdown(
    """
    <style>
    /* 에디터 텍스트 영역을 IDE 스타일 모노스페이스 폰트 및 자동 줄바꿈으로 설정 */
    textarea[data-testid="stTextArea"] {
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
        font-size: 14px !important;
        line-height: 1.55 !important;
        background-color: #fbfcfe !important;
        color: #1e293b !important;
        border-radius: 6px !important;
        border: 1px solid #cbd5e1 !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        overflow-y: auto !important;
    }
    textarea[data-testid="stTextArea"]:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    /* 빈칸 강조 뱃지 스타일 */
    .blank-badge-red {
        color: #dc2626 !important;
        background-color: #fee2e2 !important;
        font-weight: 800 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        border: 1px solid #f87171 !important;
        font-family: 'Consolas', monospace !important;
        letter-spacing: -0.2px;
    }
    /* 공개 제한 뱃지 스타일 */
    .restriction-badge-gray {
        color: #475569 !important;
        background-color: #f1f5f9 !important;
        font-weight: 700 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        border: 1px dashed #94a3b8 !important;
        font-family: 'Consolas', monospace !important;
    }
    /* 코드 뷰어 프리 포맷 및 자동 줄바꿈 */
    .code-viewer-container {
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 13.5px;
        line-height: 1.6;
        background-color: #0f172a;
        color: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .code-viewer-container pre {
        margin: 0 !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        font-family: inherit !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def _load(subject: str) -> list[Problem]:
    return load_subject(subject)


def _problem_by_id(problems: list[Problem], prob_id: str) -> Problem:
    for p in problems:
        if p.id == prob_id:
            return p
    # Fallback by number if legacy int was passed
    for p in problems:
        if str(p.number) == str(prob_id):
            return p
    raise KeyError(prob_id)


def _calculate_editor_height(code: str, max_height: int = 460, min_height: int = 140) -> int:
    """코드 라인 수에 맞춰 에디터 높이를 동적으로 조절합니다 (여백 방지 및 상한 고정)."""
    lines = len(code.splitlines())
    calculated = lines * 24 + 40
    return max(min_height, min(max_height, calculated))


def _render_highlighted_code(code: str) -> str:
    """코드 내 ### 작성 필요 ### 및 ### 공개 제한 ### 부분을 시각적으로 강조 변환합니다."""
    blank_pattern = re.compile(r"###\s*작성\s*필요\s*###|##\s*Write\s*Answer")
    restrict_pattern = re.compile(r"###\s*공개\s*제한\s*###")

    lines = code.splitlines()
    rendered_lines = []
    for idx, line in enumerate(lines, 1):
        leading_spaces = len(line) - len(line.lstrip(" "))
        content = "&nbsp;" * leading_spaces + html.escape(line.lstrip(" "))

        # 붉은색 빈칸 치환
        content = blank_pattern.sub(
            '<span style="color: #ef4444; font-weight: 900; background-color: #fee2e2; padding: 1px 7px; border-radius: 4px; border: 1.5px solid #dc2626; box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);">### 작성 필요 ###</span>',
            content,
        )
        # 공개 제한 치환
        content = restrict_pattern.sub(
            '<span style="color: #64748b; font-weight: 700; background-color: #334155; padding: 1px 7px; border-radius: 4px; border: 1px dashed #64748b;">🔒 ### 공개 제한 ###</span>',
            content,
        )

        rendered_lines.append(
            f'<div style="line-height: 1.6; display: flex; font-family: Consolas, monospace; font-size: 13.5px;">'
            f'<span style="width: 36px; color: #64748b; user-select: none; text-align: right; margin-right: 14px; flex-shrink: 0;">{idx}</span>'
            f'<span style="flex-grow: 1; color: #f8fafc;">{content}</span>'
            f'</div>'
        )
    body = "".join(rendered_lines)
    return f'<div class="code-viewer-container" style="max-height: 480px; overflow-y: auto;">{body}</div>'


def _analyze_blanks(problem_code: str, user_code: str) -> dict:
    """코드에서 빈칸(### 작성 필요 ###) 위치와 실시간 잔여 개수를 분석합니다."""
    pattern = re.compile(r"###\s*작성\s*필요\s*###|##\s*Write\s*Answer")
    lines = problem_code.splitlines()
    blank_lines = []
    for idx, line in enumerate(lines, 1):
        if pattern.search(line):
            blank_lines.append((idx, line.strip()))

    remaining = len(pattern.findall(user_code))
    return {
        "total": len(blank_lines),
        "lines": blank_lines,
        "remaining": remaining,
    }


def _sidebar(subject_keys: list[str]) -> tuple[str, bool]:
    st.sidebar.title("🧠 AI 시험 연습")
    subject = st.sidebar.radio(
        "과목 선택",
        options=subject_keys,
        format_func=lambda s: SUBJECT_LABELS.get(s, s),
        key="subject",
    )
    problems = _load(subject)
    sess.ensure_subject(subject, problems)

    order = sess.get_order(subject)
    total = len(order)
    correct = sess.correct_count(subject)
    cursor = sess.get_cursor(subject)

    st.sidebar.markdown(f"**테스트 문항:** {total}문제 (랜덤 추출)")
    st.sidebar.markdown(f"**현재 진도:** {cursor + 1} / {total}")
    st.sidebar.markdown(f"**정답 수:** {correct} / {total}")
    st.sidebar.progress((cursor + 1) / total)

    col_prev, col_next = st.sidebar.columns(2)
    with col_prev:
        if st.button("← 이전", width="stretch", disabled=(cursor == 0)):
            sess.move_cursor(subject, -1, total)
            st.rerun()
    with col_next:
        if st.button("다음 →", width="stretch", disabled=(cursor >= total - 1)):
            sess.move_cursor(subject, +1, total)
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎲 문제 출제 모드**")

    col_shuffle, col_seq = st.sidebar.columns(2)
    with col_shuffle:
        if st.button("🔀 다시 섞기", width="stretch", help="새로운 10문제를 랜덤으로 다시 뽑습니다 (종합은 4개 영역 균등 추출)."):
            sess.reshuffle(subject, problems)
            st.toast("🔀 새로운 10문제가 랜덤으로 추출되었습니다!", icon="🎲")
            st.rerun()
    with col_seq:
        if st.button("🔢 순서대로", width="stretch", help="앞부분 10문제를 순서대로 정렬합니다."):
            sess.reset_order(subject, problems, full=False)
            st.rerun()

    if st.sidebar.button("📚 전체 문제 학습 모드", width="stretch", help="과목의 모든 문제를 순서대로 확인합니다."):
        sess.reset_order(subject, problems, full=True)
        st.toast(f"📚 전체 {len(problems)}개 문제를 로드했습니다.", icon="📖")
        st.rerun()

    with st.sidebar.expander(f"📋 현재 테스트 문제 ({total}문항)", expanded=True):
        for idx, pid in enumerate(order):
            result = sess.get_result(subject, pid)
            prob = _problem_by_id(problems, pid)
            icon = "✅" if result and result.status == "correct" else ("❌" if result else "⬜")
            subj_tag = f"[{prob.subject_label}] " if subject == "total" else ""
            label = f"{icon} {idx + 1}. {subj_tag}Q{prob.number}"
            if st.button(label, key=f"jump-{subject}-{pid}", width="stretch"):
                sess.set_cursor(subject, idx)
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚙️ UX 뷰 설정**")
    split_view = st.sidebar.checkbox(
        "🖥️ 화면 분할 모드 (스플릿 뷰)",
        value=False,
        help="좌측에 '빈칸 강조 코드 뷰'를 두고, 우측에서 바로 '코드 수정 에디터'를 볼 수 있는 나란히 보기 모드입니다.",
    )

    return subject, split_view


def _main(subject: str, split_view: bool) -> None:
    problems = _load(subject)
    order = sess.get_order(subject)
    cursor = sess.get_cursor(subject)
    prob_id = order[cursor]
    problem = _problem_by_id(problems, prob_id)

    # 상단 헤더
    subj_prefix = f"[{problem.subject_label}] " if subject == "total" else ""
    st.header(f"{subj_prefix}문제 {cursor + 1} / {len(order)} — Q{problem.number}. {problem.title}")
    st.caption(f"과목: {problem.subject_label} | 문제 번호: Q{problem.number} | 식별자: {problem.id}")

    # ==========================================================================
    # 1) [문제] 및 [요구사항] 카드 UI 구성
    # ==========================================================================
    col_q, col_r = st.columns([1, 1], gap="medium")
    with col_q:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #3b82f6; padding: 12px 16px; border-radius: 6px; min-height: 110px;">
                <div style="color: #1e3a8a; font-weight: 800; font-size: 1.02em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                    <span>📌</span> [문제]
                </div>
                <div style="color: #1e293b; font-size: 0.94em; line-height: 1.55; white-space: pre-wrap;">{html.escape(problem.question)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_r:
        req_content = problem.requirements or "제시된 코드의 함수 시그니처 및 빈칸 요구사항을 정확히 준수하여 구현하세요."
        st.markdown(
            f"""
            <div style="background-color: #fffbeb; border: 1px solid #fde68a; border-left: 5px solid #f59e0b; padding: 12px 16px; border-radius: 6px; min-height: 110px;">
                <div style="color: #92400e; font-weight: 800; font-size: 1.02em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                    <span>📋</span> [요구사항]
                </div>
                <div style="color: #451a03; font-size: 0.94em; line-height: 1.55; white-space: pre-wrap;">{html.escape(req_content)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Reset version counter to force text_area widget regeneration when reset
    reset_ver = sess.get_reset_version(subject, problem.id)
    editor_key = f"editor-{subject}-{problem.id}-v{reset_ver}"

    initial_code = sess.get_answer(subject, problem.id)
    if initial_code is None:
        initial_code = problem.problem_code

    user_current_code = st.session_state.get(editor_key, initial_code)
    blank_info = _analyze_blanks(problem.problem_code, user_current_code)

    total_blanks = blank_info["total"]
    remaining = blank_info["remaining"]

    # ==========================================================================
    # 2) 답변 작성 필수 위치 Card Section (폴딩 지원 expander)
    # ==========================================================================
    expander_title = f"🎯 답변 작성 필수 위치 (총 {total_blanks}곳) | 미완성 빈칸: {remaining}개 남음"

    table_rows = []
    blank_pattern = re.compile(r"###\s*작성\s*필요\s*###|##\s*Write\s*Answer")
    for line_no, content in blank_info["lines"]:
        escaped_content = html.escape(content)
        row_highlighted = blank_pattern.sub(
            '<span class="blank-badge-red">### 작성 필요 ###</span>',
            escaped_content,
        )
        table_rows.append(
            f'<tr><td style="padding: 6px 12px; font-weight: bold; color: #dc2626; border-bottom: 1px solid #fee2e2; width: 90px; text-align: center;">Line {line_no}</td>'
            f'<td style="padding: 6px 12px; font-family: Consolas, monospace; border-bottom: 1px solid #fee2e2; background-color: #fffaf0;">{row_highlighted}</td></tr>'
        )
    table_html = "".join(table_rows)

    with st.expander(expander_title, expanded=(remaining > 0)):
        st.markdown(
            f"""
            <div style="font-size: 0.92em; color: #475569; margin-bottom: 10px; line-height: 1.5;">
                아래 코드 에디터에서 <span class="blank-badge-red">### 작성 필요 ###</span> 로 표시된 <b>굵은 붉은색</b> 부분을 문제 [요구사항]에 맞는 실제 코드로 채워 넣으세요.<br/>
                <span style="color: #64748b; font-size: 0.88em;">※ 붉은색 마커 외의 뼈대 코드나 <span class="restriction-badge-gray">🔒 ### 공개 제한 ###</span> 블록은 임의로 수정하지 마세요.</span>
            </div>
            <div style="background-color: #ffffff; border: 1px solid #fecaca; border-radius: 6px; overflow: hidden; margin-top: 8px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                    <thead>
                        <tr style="background-color: #fee2e2; color: #991b1b; font-weight: bold; text-align: left;">
                            <th style="padding: 6px 12px; width: 90px; text-align: center;">위치</th>
                            <th style="padding: 6px 12px;">수정 대상 코드 스니펫 (붉은색 표기)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_html}
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 실시간 작성 상태 피드백
    if remaining > 0:
        st.markdown(
            f"""
            <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #1e40af; font-size: 0.93em; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.1em;">✏️</span>
                <span>아직 작성하지 않은 <span class="blank-badge-red">### 작성 필요 ###</span> 가 <b>{remaining}개</b> 남아 있습니다.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #22c55e; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #166534; font-size: 0.93em; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.1em;">✨</span>
                <span>모든 빈칸에 코드가 작성되었습니다! 아래 <b>✅ 제출</b> 버튼을 눌러 채점해 보세요.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 동적 에디터 높이 계산
    editor_height = _calculate_editor_height(initial_code, max_height=480, min_height=140)

    # ==========================================================================
    # 3) [코드] 에디터 및 스플릿/탭 뷰어
    # ==========================================================================
    if split_view:
        col_left, col_right = st.columns([1, 1], gap="medium")

        with col_left:
            st.markdown("#### 🔍 빈칸 강조 코드 전체 뷰")
            st.caption("붉은색 빈칸과 전후 문맥을 확인하세요.")
            st.markdown(_render_highlighted_code(problem.problem_code), unsafe_allow_html=True)

        with col_right:
            st.markdown("#### ✍️ [코드] 수정 에디터")
            st.caption("아래 에디터에서 빈칸을 채워 완성된 코드를 작성하세요.")
            user_code = st.text_area(
                label="code editor",
                value=initial_code,
                key=editor_key,
                height=editor_height,
                label_visibility="collapsed",
            )
            col_submit, col_reset = st.columns([1, 1])
            with col_submit:
                submitted = st.button("✅ 제출", type="primary", width="stretch", key=f"sub-{problem.id}")
            with col_reset:
                reset = st.button("↺ 문제 초기화", width="stretch", key=f"rst-{problem.id}")

    else:
        tab_edit, tab_view = st.tabs(["✍️ [코드] 수정 에디터", "🔍 붉은색 빈칸 강조 전체 뷰어"])

        with tab_view:
            st.caption("코드 전체에서 ### 작성 필요 ### 가 위치한 문맥을 한눈에 확인하세요:")
            st.markdown(_render_highlighted_code(problem.problem_code), unsafe_allow_html=True)

        with tab_edit:
            user_code = st.text_area(
                label="code editor",
                value=initial_code,
                key=editor_key,
                height=editor_height,
                label_visibility="collapsed",
            )
            col_submit, col_reset = st.columns([1, 1])
            with col_submit:
                submitted = st.button("✅ 제출", type="primary", width="stretch", key=f"sub-{problem.id}")
            with col_reset:
                reset = st.button("↺ 문제 초기화", width="stretch", key=f"rst-{problem.id}")

    # ==========================================================================
    # 4) 초기화 및 채점 처리
    # ==========================================================================
    if reset:
        sess.bump_reset_version(subject, problem.id)
        sess.set_answer(subject, problem.id, problem.problem_code)
        sess.set_result(subject, problem.id, None)
        new_ver = sess.get_reset_version(subject, problem.id)
        st.session_state[f"editor-{subject}-{problem.id}-v{new_ver}"] = problem.problem_code
        st.toast("↺ 코드가 초기 상태로 깨끗하게 초기화되었습니다.", icon="🔄")
        st.rerun()

    if submitted:
        sess.set_answer(subject, problem.id, user_code)
        result = grade(user_code, problem.solution_code)
        sess.set_result(subject, problem.id, result)
    else:
        if user_code != initial_code:
            sess.set_answer(subject, problem.id, user_code)

    # 채점 결과 출력
    result = sess.get_result(subject, problem.id)
    if result is not None:
        if result.status == "correct":
            st.success("🎉 정답입니다! 축하합니다.")
        elif result.status == "wrong":
            st.error("❌ 정답과 일치하지 않습니다.")
            if result.diff:
                with st.expander("내 답안 vs 정답 diff 보기", expanded=True):
                    st.code(result.diff, language="diff")
        elif result.status == "syntax_error":
            st.warning(f"⚠️ {result.message}")

    with st.expander("📖 정답 & 핵심 개념 해설 보기", expanded=False):
        if problem.explanation:
            st.markdown(problem.explanation)
            st.markdown("---")
        st.markdown("**정답 코드:**")
        st.code(problem.solution_code, language="python")


def main() -> None:
    # 'total' (종합)을 첫 번째 옵션으로 제공
    subjects = ["total", "vision", "data", "ondevice", "llm"]
    subject, split_view = _sidebar(subjects)
    _main(subject, split_view)


if __name__ == "__main__":
    main()
