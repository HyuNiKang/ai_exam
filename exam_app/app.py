from __future__ import annotations

import streamlit as st

import session as sess
from grader import grade
from parser import SUBJECT_LABELS, SUBJECTS, Problem, load_subject

st.set_page_config(page_title="AI 시험 연습", page_icon="🧠", layout="wide")


@st.cache_data(show_spinner=False)
def _load(subject: str) -> list[Problem]:
    return load_subject(subject)


def _problem_by_number(problems: list[Problem], number: int) -> Problem:
    for p in problems:
        if p.number == number:
            return p
    raise KeyError(number)


def _sidebar(subjects: list[str]) -> str:
    st.sidebar.title("🧠 AI 시험 연습")
    subject = st.sidebar.radio(
        "과목 선택",
        options=subjects,
        format_func=lambda s: SUBJECT_LABELS.get(s, s),
        key="subject",
    )
    problems = _load(subject)
    sess.ensure_subject(subject, problems)

    total = len(problems)
    correct = sess.correct_count(subject)
    cursor = sess.get_cursor(subject)

    st.sidebar.markdown(f"**진도:** {cursor + 1} / {total}")
    st.sidebar.markdown(f"**정답 수:** {correct} / {total}")
    st.sidebar.progress((cursor + 1) / total)

    col_prev, col_next = st.sidebar.columns(2)
    with col_prev:
        if st.button("← 이전", use_container_width=True, disabled=(cursor == 0)):
            sess.move_cursor(subject, -1, total)
            st.rerun()
    with col_next:
        if st.button("다음 →", use_container_width=True, disabled=(cursor >= total - 1)):
            sess.move_cursor(subject, +1, total)
            st.rerun()

    col_seq, col_shuffle = st.sidebar.columns(2)
    with col_seq:
        if st.button("🔢 순서대로", use_container_width=True):
            sess.reset_order(subject, problems)
            st.rerun()
    with col_shuffle:
        if st.button("🔀 다시 섞기", use_container_width=True):
            sess.reshuffle(subject, problems)
            st.rerun()

    with st.sidebar.expander("문제 바로가기"):
        order = sess.get_order(subject)
        for idx, number in enumerate(order):
            result = sess.get_result(subject, number)
            icon = "✅" if result and result.status == "correct" else ("❌" if result else "⬜")
            label = f"{icon} {idx + 1}. Q{number}"
            if st.button(label, key=f"jump-{subject}-{number}", use_container_width=True):
                sess.set_cursor(subject, idx)
                st.rerun()

    return subject


def _main(subject: str) -> None:
    problems = _load(subject)
    order = sess.get_order(subject)
    cursor = sess.get_cursor(subject)
    number = order[cursor]
    problem = _problem_by_number(problems, number)

    st.header(f"문제 {cursor + 1} / {len(order)} — Q{problem.number}. {problem.title}")
    st.caption(f"과목: {SUBJECT_LABELS[subject]}")

    initial_code = sess.get_answer(subject, problem.number)
    if initial_code is None:
        initial_code = problem.problem_code

    st.markdown("**코드를 작성하세요** (빈칸(`### !!!코드를 작성하세요!!!`)을 채워 넣고 제출):")
    user_code = st.text_area(
        label="code editor",
        value=initial_code,
        key=f"editor-{subject}-{problem.number}",
        height=420,
        label_visibility="collapsed",
    )

    col_submit, col_reset = st.columns([1, 1])
    with col_submit:
        submitted = st.button("✅ 제출", type="primary", use_container_width=True)
    with col_reset:
        reset = st.button("↺ 문제 초기화", use_container_width=True)

    if reset:
        sess.set_answer(subject, problem.number, problem.problem_code)
        sess.set_result(subject, problem.number, None)
        st.rerun()

    if submitted:
        sess.set_answer(subject, problem.number, user_code)
        result = grade(user_code, problem.solution_code)
        sess.set_result(subject, problem.number, result)
    else:
        # Persist edits even without submission
        if user_code != initial_code:
            sess.set_answer(subject, problem.number, user_code)

    result = sess.get_result(subject, problem.number)
    if result is not None:
        if result.status == "correct":
            st.success("🎉 정답입니다!")
        elif result.status == "wrong":
            st.error("❌ 정답과 일치하지 않습니다.")
            if result.diff:
                with st.expander("내 답안 vs 정답 diff 보기", expanded=True):
                    st.code(result.diff, language="diff")
        elif result.status == "syntax_error":
            st.warning(f"⚠️ {result.message}")

    with st.expander("🔍 정답 & 해설 보기", expanded=False):
        if problem.explanation:
            st.markdown(problem.explanation)
            st.markdown("---")
        st.markdown("**정답 코드:**")
        st.code(problem.solution_code, language="python")


def main() -> None:
    subject = _sidebar(list(SUBJECTS.keys()))
    _main(subject)


if __name__ == "__main__":
    main()
