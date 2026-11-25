"""Декоратор, который профилирует (cProfile) все вызовы функции.

У каждой декорированной функции свой Profile, он копит статистику со
всех вызовов, а print_stat() печатает одну общую таблицу.
"""

import cProfile
import functools
import pstats

# Начиная с python 3.12 два профайлера одновременно включить нельзя
# (ValueError). Это случится если одна декорированная функция вызывает
# другую. Поэтому помню кто сейчас включен, а вложенную функцию просто
# вызываю как есть - ее все равно видно в таблице той, что снаружи.
_active = []


def profile_deco(func):
    profiler = cProfile.Profile()
    depth = 0  # для рекурсии: выключать профайлер надо только на самом верхнем вызове

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal depth

        if depth == 0 and _active:
            return func(*args, **kwargs)

        if depth == 0:
            _active.append(profiler)
            profiler.enable()
        depth += 1
        try:
            return func(*args, **kwargs)
        finally:
            depth -= 1
            if depth == 0:
                profiler.disable()
                _active.remove(profiler)

    def print_stat():
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative").print_stats()

    wrapper.print_stat = print_stat
    return wrapper
