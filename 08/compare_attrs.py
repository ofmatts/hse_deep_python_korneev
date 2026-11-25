"""Замеры: сколько времени уходит на создание пачки объектов и на
чтение/изменение их атрибутов для PlainPoint, SlotsPoint и WeakPoint.

Запуск: python compare_attrs.py
"""

import time

from attr_types import Owner, PlainPoint, SlotsPoint, WeakPoint

COUNT = 500_000
OWNERS_COUNT = 100
REPEATS = 5  # беру лучшее из нескольких, иначе числа сильно скачут

CLASSES = [PlainPoint, SlotsPoint, WeakPoint]


def make_owners(count=OWNERS_COUNT):
    return [Owner(i) for i in range(count)]


def create_batch(cls, owners, count=COUNT):
    batch = []
    owners_len = len(owners)
    for i in range(count):
        batch.append(cls("p" + str(i), i, i * 2, owners[i % owners_len]))
    return batch


def read_batch(batch):
    total = 0
    for point in batch:
        total += point.x + point.y + len(point.name) + point.owner.owner_id
    return total


def change_batch(batch, owners):
    owners_len = len(owners)
    for i, point in enumerate(batch):
        point.x += 1
        point.y = point.x * 2
        point.name = "q"
        point.owner = owners[(i + 1) % owners_len]


def best_time(func, repeats=REPEATS):
    best = None
    for _ in range(repeats):
        start = time.perf_counter()
        func()
        spent = time.perf_counter() - start
        if best is None or spent < best:
            best = spent
    return best


def measure(cls, count=COUNT, repeats=REPEATS):
    """возвращает (время создания, время чтения, время изменения)"""
    owners = make_owners()

    create_time = best_time(lambda: create_batch(cls, owners, count), repeats)

    # для чтения и изменения пачка нужна одна и та же, поэтому создаю ее отдельно
    batch = create_batch(cls, owners, count)
    read_time = best_time(lambda: read_batch(batch), repeats)
    change_time = best_time(lambda: change_batch(batch, owners), repeats)

    return create_time, read_time, change_time


def main():
    print("объектов в пачке:", COUNT)
    print(f"{'класс':<12}{'создание':>12}{'чтение':>12}{'изменение':>12}")

    for cls in CLASSES:
        create_time, read_time, change_time = measure(cls)
        print(f"{cls.__name__:<12}{create_time:>11.3f}s{read_time:>11.3f}s{change_time:>11.3f}s")


if __name__ == "__main__":
    main()
