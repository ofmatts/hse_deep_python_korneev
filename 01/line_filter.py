"""Генератор который ищет в файле строки с нужными словами."""

import os
from collections.abc import Iterator
from typing import TextIO


def filter_lines(
    source: str | os.PathLike | TextIO,
    search_words: list[str],
    stop_words: list[str],
) -> Iterator[str]:
    """Отдает строки где встретилось хоть одно слово из search_words.

    Со стоп-словами все строго: если слово из stop_words есть в строке,
    строку выкидываю даже если там нашлось искомое слово. Совпадение
    считается только по целому слову и без учета регистра. В source можно
    дать путь к файлу или уже открытый файл, оба варианта должны работать.
    """
    search = {word.lower() for word in search_words}
    stops = {word.lower() for word in stop_words}

    if isinstance(source, (str, os.PathLike)):
        # путь сам открою и сам закрою
        with open(source, encoding="utf-8") as f:
            for line in f:
                if line_matches(line, search, stops):
                    yield line.rstrip("\n")
    else:
        # а чужой файл закрывать не буду, это не мое дело
        for line in source:
            if line_matches(line, search, stops):
                yield line.rstrip("\n")


def line_matches(line: str, search: set[str], stops: set[str]) -> bool:
    """нужно ли эту строку надо отдать наружу"""
    words = set(line.lower().split())
    if words & stops:
        return False  # стоп-слово, проезжаем мимо
    return bool(words & search)
