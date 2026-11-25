"""Профилирование кода из compare_attrs: вызовы (cProfile) и память (tracemalloc).

Запуск: python profile_attrs.py
"""

import cProfile
import io
import pstats
import tracemalloc

from compare_attrs import (CLASSES, change_batch, create_batch, make_owners,
                           read_batch)

COUNT = 200_000  # тут пачка поменьше, под профайлером все работает в разы медленнее


def run_all(cls, count=COUNT):
    owners = make_owners()
    batch = create_batch(cls, owners, count)
    read_batch(batch)
    change_batch(batch, owners)


def profile_calls(cls, count=COUNT, top=8):
    """прогоняет все три шага под cProfile и возвращает таблицу строкой"""
    profiler = cProfile.Profile()
    profiler.enable()
    run_all(cls, count)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("tottime").print_stats(top)
    return stream.getvalue()


def measure_memory(cls, count=COUNT):
    """сколько памяти (в байтах) занимает пачка и сколько было на пике"""
    owners = make_owners()

    tracemalloc.start()
    batch = create_batch(cls, owners, count)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # batch нужен живым до замера, иначе его сразу бы собрали
    assert len(batch) == count
    return current, peak


def main():
    for cls in CLASSES:
        print("=" * 70)
        print(cls.__name__, "- вызовы")
        print(profile_calls(cls))

    print("=" * 70)
    print("память, пачка из", COUNT, "объектов")
    for cls in CLASSES:
        current, peak = measure_memory(cls)
        cur_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024
        print(f"{cls.__name__:<12} сейчас {cur_mb:>7.1f} MB, пик {peak_mb:>7.1f} MB")


if __name__ == "__main__":
    main()
