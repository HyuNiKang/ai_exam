from __future__ import annotations

import random
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from parser import Problem

TEST_PROBLEM_COUNT = 12


def _pick_balanced_total_sample(problems: list[Problem], count: int = TEST_PROBLEM_COUNT) -> list[str]:
    """5개 영역(Vision, Data, On-Device, LLM, RAG)에서 골고루 랜덤으로 총 count(기본 12)개를 선택합니다.

    - 기본 배분: 5개 과목에서 각 2문제씩 추출 (10문제)
    - 추가 배분: 5개 과목 중 랜덤 2개 과목에서 각 1문제씩 추가 추출 (총 12문제)
    - 최종 12문제를 셔플하여 순서가 고르게 섞이도록 반환
    """
    by_subj: dict[str, list[Problem]] = {}
    for p in problems:
        by_subj.setdefault(p.subject, []).append(p)

    subjects = list(by_subj.keys())
    selected_ids: list[str] = []

    # 1) 각 과목에서 2문제씩 추출
    base_per_subj = 2
    for s in subjects:
        pool = by_subj[s]
        k = min(base_per_subj, len(pool))
        chosen = random.sample(pool, k)
        selected_ids.extend([p.id for p in chosen])

    # 2) 나머지 필요한 개수(예: 10 - 8 = 2개)는 과목들을 랜덤 셔플하여 1개씩 추가 추출
    remaining_count = count - len(selected_ids)
    if remaining_count > 0:
        extra_subjects = random.sample(subjects, min(remaining_count, len(subjects)))
        for s in extra_subjects:
            pool = by_subj[s]
            # 이미 선택되지 않은 문제 중에서 선택
            available = [p for p in pool if p.id not in selected_ids]
            if available:
                selected_ids.append(random.choice(available).id)

    random.shuffle(selected_ids)
    return selected_ids


def _pick_random_sample(problems: list[Problem], count: int = TEST_PROBLEM_COUNT) -> list[str]:
    """과목 전체 문제 중 count개(기본 10개)를 랜덤으로 추출합니다."""
    all_ids = [p.id for p in problems]
    k = min(count, len(all_ids))
    return random.sample(all_ids, k)


def _init_subject(subject: str, problems: list[Problem]) -> None:
    """과목 최초 선택 시 10문제 랜덤 세션을 생성합니다."""
    order_key = f"order::{subject}"
    if order_key not in st.session_state:
        if subject == "total":
            st.session_state[order_key] = _pick_balanced_total_sample(problems, TEST_PROBLEM_COUNT)
        else:
            st.session_state[order_key] = _pick_random_sample(problems, TEST_PROBLEM_COUNT)
        st.session_state[f"cursor::{subject}"] = 0
        st.session_state[f"answers::{subject}"] = {}
        st.session_state[f"results::{subject}"] = {}
        st.session_state[f"reset_ver::{subject}"] = {}


def ensure_subject(subject: str, problems: list[Problem]) -> None:
    _init_subject(subject, problems)


def reshuffle(subject: str, problems: list[Problem]) -> None:
    """새로운 랜덤 10문제를 다시 추출하여 세션을 재구성합니다."""
    if subject == "total":
        st.session_state[f"order::{subject}"] = _pick_balanced_total_sample(problems, TEST_PROBLEM_COUNT)
    else:
        st.session_state[f"order::{subject}"] = _pick_random_sample(problems, TEST_PROBLEM_COUNT)
    st.session_state[f"cursor::{subject}"] = 0


def reset_order(subject: str, problems: list[Problem], full: bool = False) -> None:
    """문제 번호 순서대로 정렬합니다 (기본: 처음 10문제, full=True: 전체 문제)."""
    all_ids = [p.id for p in problems]
    if full:
        st.session_state[f"order::{subject}"] = all_ids
    else:
        st.session_state[f"order::{subject}"] = all_ids[:min(TEST_PROBLEM_COUNT, len(all_ids))]
    st.session_state[f"cursor::{subject}"] = 0


def get_order(subject: str) -> list[str]:
    return st.session_state[f"order::{subject}"]


def get_cursor(subject: str) -> int:
    return st.session_state[f"cursor::{subject}"]


def set_cursor(subject: str, value: int) -> None:
    st.session_state[f"cursor::{subject}"] = value


def move_cursor(subject: str, delta: int, total: int) -> None:
    cur = get_cursor(subject)
    set_cursor(subject, max(0, min(total - 1, cur + delta)))


def get_answer(subject: str, prob_id: str) -> str | None:
    return st.session_state[f"answers::{subject}"].get(prob_id)


def set_answer(subject: str, prob_id: str, code: str) -> None:
    st.session_state[f"answers::{subject}"][prob_id] = code


def get_result(subject: str, prob_id: str):
    return st.session_state[f"results::{subject}"].get(prob_id)


def set_result(subject: str, prob_id: str, result) -> None:
    st.session_state[f"results::{subject}"][prob_id] = result


def correct_count(subject: str) -> int:
    results = st.session_state[f"results::{subject}"]
    order = get_order(subject)
    return sum(1 for pid in order if results.get(pid) and results[pid].status == "correct")


def get_reset_version(subject: str, prob_id: str) -> int:
    vers = st.session_state.setdefault(f"reset_ver::{subject}", {})
    return vers.get(prob_id, 0)


def bump_reset_version(subject: str, prob_id: str) -> int:
    vers = st.session_state.setdefault(f"reset_ver::{subject}", {})
    vers[prob_id] = vers.get(prob_id, 0) + 1
    return vers[prob_id]
