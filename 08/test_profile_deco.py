"""Тесты для profile_deco."""

import io
from contextlib import redirect_stdout

from profile_deco import profile_deco


def get_stat(func):
    buf = io.StringIO()
    with redirect_stdout(buf):
        func.print_stat()
    return buf.getvalue()


def test_example_from_homework():
    @profile_deco
    def add(a, b):
        return a + b

    @profile_deco
    def sub(a, b):
        return a - b

    assert add(1, 2) == 3
    assert add(4, 5) == 9
    assert sub(4, 5) == -1

    add_stat = get_stat(add)
    sub_stat = get_stat(sub)

    # в таблице add два вызова, в таблице sub один, и друг друга они не видят
    assert "function calls" in add_stat
    assert "add" in add_stat
    assert "sub" not in add_stat
    assert "sub" in sub_stat
    assert "add" not in sub_stat


def test_calls_are_summed():
    @profile_deco
    def work(x):
        return x * 2

    for i in range(5):
        work(i)

    stat = get_stat(work)
    # строка вида "5    0.000 ... test_profile_deco.py:NN(work)"
    work_line = [line for line in stat.splitlines() if "(work)" in line][0]
    assert work_line.split()[0] == "5"


def test_keeps_name_and_docstring():
    @profile_deco
    def documented():
        """вот такая строка"""
        return 1

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "вот такая строка"


def test_args_and_kwargs():
    @profile_deco
    def concat(a, b, sep="-"):
        return a + sep + b

    assert concat("x", "y") == "x-y"
    assert concat("x", b="y", sep="+") == "x+y"


def test_exception_does_not_break_profiler():
    @profile_deco
    def broken():
        raise ValueError("упало")

    for _ in range(2):
        try:
            broken()
        except ValueError:
            pass

    # после исключения профайлер выключен, иначе следующая функция упала бы
    @profile_deco
    def fine():
        return 1

    assert fine() == 1
    assert "(broken)" in get_stat(broken)


def test_recursion():
    @profile_deco
    def fact(n):
        if n <= 1:
            return 1
        return n * fact(n - 1)

    assert fact(5) == 120
    assert "(fact)" in get_stat(fact)


def test_nested_decorated_functions():
    @profile_deco
    def inner():
        return 1

    @profile_deco
    def outer():
        return inner() + 1

    # две включенные профайлера сразу в 3.12+ кидают ValueError
    assert outer() == 2
    assert inner() == 1
    assert "(outer)" in get_stat(outer)
    assert "(inner)" in get_stat(inner)
