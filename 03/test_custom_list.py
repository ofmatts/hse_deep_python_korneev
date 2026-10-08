"""Тесты для CustomList."""

import pytest

from custom_list import CustomList


def test_add_two_custom_lists():
    result = CustomList([5, 1, 3, 7]) + CustomList([1, 2, 7])
    assert isinstance(result, CustomList)
    assert list(result) == [6, 3, 10, 7]


def test_add_custom_list_with_plain_list():
    result = CustomList([10]) + [2, 5]
    assert isinstance(result, CustomList)
    assert list(result) == [12, 5]


def test_plain_list_plus_custom_list():
    # тут работает __radd__, и главное чтобы вернулся CustomList,
    # а не обычный list - питон такое любит подсовывать
    result = [2, 5] + CustomList([10])
    assert isinstance(result, CustomList)
    assert list(result) == [12, 5]


def test_add_with_number():
    assert list(CustomList([2, 5]) + 10) == [12, 15]
    assert list(10 + CustomList([2, 5])) == [12, 15]


def test_add_with_negative_number():
    assert list(CustomList([1, 2]) + (-3)) == [-2, -1]
    assert list(-3 + CustomList([1, 2])) == [-2, -1]


def test_add_different_lengths():
    # короткому списку не хватает элементов, считаю что там нули
    assert list(CustomList([1, 2, 3]) + CustomList([10])) == [11, 2, 3]
    assert list(CustomList([10]) + CustomList([1, 2, 3])) == [11, 2, 3]
    assert list(CustomList() + CustomList([1, 2])) == [1, 2]
    assert list(CustomList([7]) + []) == [7]
    assert list([] + CustomList([7])) == [7]


def test_add_returns_new_object():
    first = CustomList([1, 2])
    second = CustomList([3, 4])
    assert first + second is not first
    assert first + second is not second


def test_sub_two_custom_lists():
    result = CustomList([5, 1, 3, 7]) - CustomList([1, 2, 7])
    assert isinstance(result, CustomList)
    assert list(result) == [4, -1, -4, 7]


def test_sub_custom_list_with_plain_list():
    assert list(CustomList([10]) - [2, 5]) == [8, -5]


def test_plain_list_minus_custom_list():
    assert list([2, 5] - CustomList([10])) == [-8, 5]


def test_sub_with_number():
    assert list(CustomList([2, 5]) - 10) == [-8, -5]
    assert list(10 - CustomList([2, 5])) == [8, 5]


def test_sub_different_lengths():
    assert list(CustomList([1, 2, 3]) - CustomList([10])) == [-9, 2, 3]
    assert list(CustomList([10]) - CustomList([1, 2, 3])) == [9, -2, -3]
    assert list(CustomList() - CustomList([1, 2])) == [-1, -2]


def test_originals_are_not_changed():
    first = CustomList([1, 2])
    second = CustomList([10, 20, 30])
    plain = [5, 5]

    # наговорил всякого, главное чтобы списки после этого остались живы
    _ = first + second
    _ = second + first
    _ = first - second
    _ = second - first
    _ = first + plain
    _ = plain + first
    _ = first - plain
    _ = plain - first
    _ = first + 100
    _ = 100 - first

    assert list(first) == [1, 2]
    assert list(second) == [10, 20, 30]
    assert plain == [5, 5]


def test_add_with_garbage():
    with pytest.raises(TypeError):
        _ = CustomList([1]) + "abc"
    with pytest.raises(TypeError):
        _ = "abc" + CustomList([1])


def test_sub_with_garbage():
    with pytest.raises(TypeError):
        _ = CustomList([1]) - "abc"
    with pytest.raises(TypeError):
        _ = "abc" - CustomList([1])


def test_eq_compares_sums():
    # именно суммы, а не сами элементы. поэтому в остальных тестах
    # проверяю элементы через list(), а не через ==
    assert CustomList([1, 2, 3]) == CustomList([6])
    assert CustomList([0]) == CustomList([])
    assert CustomList([-1, 1]) == CustomList([])


def test_ne():
    assert CustomList([1, 2, 3]) != CustomList([7])
    # при равных суммах != обязан вернуть False. pylint предлагает
    # переписать на ==, но тогда проверится __eq__, а не __ne__
    assert not CustomList([1, 2]) != CustomList([3])  # pylint: disable=unnecessary-negation
    # с обычным списком сравнение в задании не просили, но узнавал
    # ради интереса: питон сам зовет list.__eq__ и сравнивает элементы
    assert CustomList([1, 2]) == [1, 2]


def test_eq_with_not_a_list():
    # с числами и прочим сравнение не задумано, но и не падает
    assert not CustomList([1, 2]) == 10  # pylint: disable=unnecessary-negation
    assert CustomList([1, 2]) != 10


def test_greater_less():
    big = CustomList([5, 1, 3, 7])  # сумма 16
    small = CustomList([1, 2, 7])  # сумма 10

    assert big > small
    assert small < big
    # в обратную сторону сравнения не срабатывают. pylint предлагает
    # вместо not > написать <=, но так проверится совсем другой метод
    assert not small > big  # pylint: disable=unnecessary-negation
    assert not big < small  # pylint: disable=unnecessary-negation


def test_greater_equal_less_equal():
    ten = CustomList([10])
    also_ten = CustomList([4, 6])
    twenty = CustomList([20])

    assert twenty >= ten
    assert ten <= twenty
    assert ten >= also_ten
    assert ten <= also_ten
    # суммы равные: >= и <= срабатывают, а строгие сравнения - нет
    assert not ten > also_ten  # pylint: disable=unnecessary-negation
    assert not ten < also_ten  # pylint: disable=unnecessary-negation


def test_order_with_stranger_raises():
    with pytest.raises(TypeError):
        _ = CustomList([1, 2]) > 10
    with pytest.raises(TypeError):
        _ = 10 > CustomList([1, 2])


def test_order_with_plain_list_surprise():
    # неожиданность: с обычным списком сравнение не падает. мой
    # NotImplemented передает эстафету list.__gt__ и компании, а те
    # сравнивают списки по элементам, примерно как кортежи. задание
    # такого не просило, но пусть будет задокументировано
    assert CustomList([1, 2]) <= [1, 2]
    assert CustomList([1, 2]) >= [1, 2]
    assert CustomList([1, 0]) < [1, 2]
    assert CustomList([1, 2]) > [1, 0]


def test_str_shows_items_and_sum():
    assert str(CustomList([1, 2, 3])) == "[1, 2, 3] сумма = 6"
    assert str(CustomList([])) == "[] сумма = 0"
    assert str(CustomList([-5, 5])) == "[-5, 5] сумма = 0"


def test_usual_list_methods_still_work():
    # наследование должно быть честным, а не "я решил переопределить все"
    items = CustomList([1, 2])
    items.append(3)
    items.extend([4, 5])
    assert items.count(3) == 1
    assert items.index(4) == 3
    assert list(items) == [1, 2, 3, 4, 5]
    assert items.pop() == 5
    assert list(items[:-1]) == [1, 2, 3]
