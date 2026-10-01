"""Тесты для retry_deco."""

import pytest

from retry_deco import retry_deco


def test_logs_positional_args_and_result(capsys):
    @retry_deco(3)
    def add(a, b):
        return a + b

    assert add(4, 2) == 6

    out = capsys.readouterr().out
    assert out == 'run "add" with positional args = (4, 2), attempt = 1, result = 6\n'


def test_logs_kwargs(capsys):
    @retry_deco(3)
    def add(a, b=1):
        return a + b

    assert add(4, b=3) == 7

    out = capsys.readouterr().out
    assert "positional args = (4,)" in out
    assert "keyword kwargs = {'b': 3}" in out
    assert "attempt = 1, result = 7" in out


def test_without_args_at_all(capsys):
    @retry_deco(2)
    def get_answer():
        return 42

    assert get_answer() == 42

    out = capsys.readouterr().out
    assert 'run "get_answer" with attempt = 1, result = 42' in out


def test_restarts_until_lucky(capsys):
    # два раза падает и только на третий раз отвечает
    tries = []

    @retry_deco(5)
    def flaky():
        tries.append(1)
        if len(tries) < 3:
            raise ValueError("опять сломалось")
        return "наконец-то"

    assert flaky() == "наконец-то"
    assert len(tries) == 3

    out = capsys.readouterr().out
    assert out.count("exception = ValueError") == 2
    assert "attempt = 3, result = наконец-то" in out


def test_gives_up_after_all_attempts(capsys):
    # как в дз: retry_deco(3) это три попытки, после третьей сдаюсь
    counter = []

    @retry_deco(3)
    def always_bad():
        counter.append("упал")
        raise KeyError("нет такого ключа")

    with pytest.raises(KeyError):
        always_bad()

    assert len(counter) == 3
    assert capsys.readouterr().out.count("exception = KeyError") == 3


def test_expected_error_is_not_retried(capsys):
    # пример с check_int: ValueError для него нормальный режим работы,
    # значит перезапускать не надо
    calls = []

    @retry_deco(2, [ValueError])
    def check_int(value=None):
        calls.append(1)
        if value is None:
            raise ValueError
        return isinstance(value, int)

    assert check_int(value=1) is True

    with pytest.raises(ValueError):
        check_int(value=None)

    assert len(calls) == 2
    assert capsys.readouterr().out.count("exception = ValueError") == 1


def test_other_errors_still_retried():
    # если в списке только ValueError, то KeyError все равно поломка
    how_many = []

    @retry_deco(3, [ValueError])
    def weird():
        how_many.append(1)
        raise KeyError("ой")

    with pytest.raises(KeyError):
        weird()

    assert len(how_many) == 3


def test_with_empty_call():
    # retry_deco() с пустыми скобками тоже работает, попытки по умолчанию
    attempts = []

    @retry_deco()
    def always_bad():
        attempts.append(1)
        raise ValueError

    with pytest.raises(ValueError):
        always_bad()

    assert len(attempts) == 3


def test_wraps_keeps_the_name():
    # имя функции не должно потеряться за декоратором
    def add(a, b):
        return a + b

    wrapped = retry_deco(3)(add)

    assert wrapped.__name__ == "add"
    assert wrapped(4, 2) == 6
