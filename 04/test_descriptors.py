"""Тесты дескрипторов из descriptors.py"""

import pytest

from descriptors import BaseDescriptor, Coffee, Integer, PositiveInteger, String


def test_coffee_ok():
    # happy path
    order = Coffee(3, "latte", 250)
    assert order.num == 3
    assert order.name == "latte"
    assert order.price == 250


def test_integer_rejects_not_int():
    with pytest.raises(TypeError):
        Coffee("three", "latte", 250)
    with pytest.raises(TypeError):
        Coffee(3.5, "latte", 250)


def test_integer_rejects_bool():
    # True это int, но числом в заказе быть не должно
    with pytest.raises(TypeError):
        Coffee(True, "latte", 250)


def test_string_rejects_not_str():
    with pytest.raises(TypeError):
        Coffee(3, 42, 250)


def test_string_rejects_empty():
    with pytest.raises(ValueError):
        Coffee(3, "", 250)
    # из одних пробелов тоже не пропускаю
    with pytest.raises(ValueError):
        Coffee(3, "   ", 250)


def test_positive_integer_rejects_zero_and_negative():
    with pytest.raises(ValueError):
        Coffee(3, "latte", 0)
    with pytest.raises(ValueError):
        Coffee(3, "latte", -250)


def test_positive_integer_rejects_not_int():
    with pytest.raises(TypeError):
        Coffee(3, "latte", "250")
    with pytest.raises(TypeError):
        Coffee(3, "latte", 250.0)
    with pytest.raises(TypeError):
        Coffee(3, "latte", True)


def test_set_value_after_creation():
    # дескриптор работает и после создания объекта
    order = Coffee(1, "cappuchino", 200)
    order.price = 300
    assert order.price == 300
    with pytest.raises(ValueError):
        order.price = -1


def test_get_from_class_returns_descriptor():
    # если читать атрибут у класса, а не у объекта - получаю сам дескриптор
    assert isinstance(Coffee.name, String)
    assert isinstance(Coffee.price, PositiveInteger)
    assert isinstance(Coffee.num, Integer)


def test_cant_create_descriptor_without_validate():
    # класс без validate не создастся - абстрактный метод!
    class Bad(BaseDescriptor):  # pylint: disable=unused-variable
        pass  # validate не реализовал

    with pytest.raises(TypeError):
        Bad()  # pylint: disable=abstract-class-instantiated
        # создать экземпляр нельзя пока validate не реализован

    class Good(Integer):
        def validate(self, value):
            pass
    Good()  # ок
