"""Тесты для attr_types, compare_attrs и profile_attrs."""

import gc
import io
from contextlib import redirect_stdout

import pytest

import compare_attrs
import profile_attrs
from attr_types import Owner, PlainPoint, SlotsPoint, WeakPoint


@pytest.mark.parametrize("cls", [PlainPoint, SlotsPoint, WeakPoint])
def test_attributes(cls):
    owner = Owner(7)
    point = cls("a", 1, 2, owner)

    assert point.name == "a"
    assert point.x == 1
    assert point.y == 2
    assert point.owner is owner

    point.x = 10
    # новый владелец должен жить в переменной, иначе weakref сразу умрет
    new_owner = Owner(8)
    point.owner = new_owner
    assert point.x == 10
    assert point.owner.owner_id == 8


def test_slots_has_no_dict():
    point = SlotsPoint("a", 1, 2, Owner(1))
    assert not hasattr(point, "__dict__")
    with pytest.raises(AttributeError):
        setattr(point, "new_attr", 5)


def test_plain_has_dict():
    point = PlainPoint("a", 1, 2, Owner(1))
    point.new_attr = 5
    assert point.new_attr == 5


def test_weak_owner_dies():
    owner = Owner(1)
    point = WeakPoint("a", 1, 2, owner)
    assert point.owner is owner

    del owner
    gc.collect()
    assert point.owner is None


def test_plain_keeps_owner_alive():
    owner = Owner(1)
    point = PlainPoint("a", 1, 2, owner)
    del owner
    gc.collect()
    assert point.owner.owner_id == 1


def test_create_batch():
    owners = compare_attrs.make_owners(3)
    batch = compare_attrs.create_batch(SlotsPoint, owners, 10)
    assert len(batch) == 10
    assert batch[4].name == "p4"
    assert batch[4].owner is owners[1]


def test_read_batch():
    owners = compare_attrs.make_owners(2)
    batch = compare_attrs.create_batch(PlainPoint, owners, 2)
    # (0 + 0 + len("p0") + 0) + (1 + 2 + len("p1") + 1)
    assert compare_attrs.read_batch(batch) == 2 + 6


def test_change_batch():
    owners = compare_attrs.make_owners(2)
    batch = compare_attrs.create_batch(WeakPoint, owners, 3)
    compare_attrs.change_batch(batch, owners)

    assert batch[1].x == 2
    assert batch[1].y == 4
    assert batch[1].name == "q"
    assert batch[1].owner is owners[0]


def test_best_time():
    assert compare_attrs.best_time(lambda: None, 3) >= 0


@pytest.mark.parametrize("cls", compare_attrs.CLASSES)
def test_measure(cls):
    times = compare_attrs.measure(cls, 100, 2)
    assert len(times) == 3
    assert all(t >= 0 for t in times)


def test_compare_main(monkeypatch):
    monkeypatch.setattr(compare_attrs, "COUNT", 100)
    monkeypatch.setattr(compare_attrs, "REPEATS", 1)
    # значения по умолчанию в measure уже посчитаны, поэтому подменяю целиком
    real_measure = compare_attrs.measure
    monkeypatch.setattr(compare_attrs, "measure", lambda cls: real_measure(cls, 100, 1))

    buf = io.StringIO()
    with redirect_stdout(buf):
        compare_attrs.main()

    out = buf.getvalue()
    for cls in compare_attrs.CLASSES:
        assert cls.__name__ in out


def test_profile_calls():
    table = profile_attrs.profile_calls(PlainPoint, 100, 5)
    assert "function calls" in table
    assert "create_batch" in table or "read_batch" in table


def test_measure_memory():
    current, peak = profile_attrs.measure_memory(SlotsPoint, 100)
    assert current > 0
    assert peak >= current


def test_slots_takes_less_memory():
    plain, _ = profile_attrs.measure_memory(PlainPoint, 2000)
    slots, _ = profile_attrs.measure_memory(SlotsPoint, 2000)
    assert slots < plain


def test_profile_main(monkeypatch):
    monkeypatch.setattr(profile_attrs, "COUNT", 50)
    real_calls = profile_attrs.profile_calls
    real_memory = profile_attrs.measure_memory
    monkeypatch.setattr(profile_attrs, "profile_calls", lambda cls: real_calls(cls, 50))
    monkeypatch.setattr(profile_attrs, "measure_memory", lambda cls: real_memory(cls, 50))

    buf = io.StringIO()
    with redirect_stdout(buf):
        profile_attrs.main()

    assert "WeakPoint" in buf.getvalue()
