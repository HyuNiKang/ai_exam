from __future__ import annotations

import random

import streamlit as st

from parser import Problem


def _init_subject(subject: str, problems: list[Problem]) -> None:
    """Create session entries for a subject the first time it's selected."""
    order_key = f"order::{subject}"
    if order_key not in st.session_state:
        st.session_state[order_key] = _new_order(problems)
        st.session_state[f"cursor::{subject}"] = 0
        st.session_state[f"answers::{subject}"] = {}
        st.session_state[f"results::{subject}"] = {}


def _new_order(problems: list[Problem]) -> list[int]:
    order = [p.number for p in problems]
    random.shuffle(order)
    return order


def ensure_subject(subject: str, problems: list[Problem]) -> None:
    _init_subject(subject, problems)


def reshuffle(subject: str, problems: list[Problem]) -> None:
    st.session_state[f"order::{subject}"] = _new_order(problems)
    st.session_state[f"cursor::{subject}"] = 0


def get_order(subject: str) -> list[int]:
    return st.session_state[f"order::{subject}"]


def get_cursor(subject: str) -> int:
    return st.session_state[f"cursor::{subject}"]


def set_cursor(subject: str, value: int) -> None:
    st.session_state[f"cursor::{subject}"] = value


def move_cursor(subject: str, delta: int, total: int) -> None:
    cur = get_cursor(subject)
    set_cursor(subject, max(0, min(total - 1, cur + delta)))


def get_answer(subject: str, number: int) -> str | None:
    return st.session_state[f"answers::{subject}"].get(number)


def set_answer(subject: str, number: int, code: str) -> None:
    st.session_state[f"answers::{subject}"][number] = code


def get_result(subject: str, number: int):
    return st.session_state[f"results::{subject}"].get(number)


def set_result(subject: str, number: int, result) -> None:
    st.session_state[f"results::{subject}"][number] = result


def correct_count(subject: str) -> int:
    results = st.session_state[f"results::{subject}"]
    return sum(1 for r in results.values() if r and r.status == "correct")
