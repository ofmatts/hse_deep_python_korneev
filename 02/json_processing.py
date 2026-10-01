"""Функция которая разбирает json и ищет токены в значениях нужных ключей."""

import json
from typing import Any, Callable


def process_json(
    json_str: str,
    required_keys: list[str] | None = None,
    tokens: list[str] | None = None,
    callback: Callable[[str, str], Any] | None = None,
) -> None:
    """Ищет в json нужные ключи и токены в их значениях.

    Ключи сравниваю строго по регистру, токены без учета регистра.
    Значения - строки со словами через произвольное число
    пробелов (знаков препинания в дз нет), так что просто режу
    значение на слова. Токен должен совпасть с целым словом, часть
    слова это не вхождение. Для каждого найденного токена вызываю
    callback с ключом и токеном, токен отдаю в том же виде в котором
    его передали.
    """
    if required_keys is None or tokens is None or callback is None:
        # хоть чего-то не хватает, значит обрабатывать нечего
        return

    data = json.loads(json_str)

    for key, value in data.items():
        if key not in required_keys:
            continue

        # пробелов между словами может быть сколько угодно,
        # split() без аргументов такое пережевывает нормально
        words = value.lower().split()
        for token in tokens:
            if token.lower() in words:
                callback(key, token)
