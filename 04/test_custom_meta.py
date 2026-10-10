"""Тесты для CustomMeta - гоняю пример из задания целиком."""

import pytest

from custom_meta import CustomMeta


class CustomClass(metaclass=CustomMeta):
    x = 50

    def __init__(self, val=99):
        self.val = val

    def line(self):
        return 100

    def __str__(self):
        return "Custom_by_metaclass"


def test_class_attributes_have_prefix():
    assert CustomClass.custom_x == 50


def test_class_attribute_without_prefix_not_found():
    with pytest.raises(AttributeError):
        CustomClass.x


def test_instance_attributes():
    inst = CustomClass()
    assert inst.custom_x == 50
    assert inst.custom_val == 99
    assert inst.custom_line() == 100
    assert str(inst) == "Custom_by_metaclass"


def test_instance_attributes_without_prefix_fail():
    inst = CustomClass()
    # питон вроде бы иногда умеет подсовывать атрибуты из класса,
    # тут они переименованы так что все должно упасть
    with pytest.raises(AttributeError):
        inst.x
    with pytest.raises(AttributeError):
        inst.val
    with pytest.raises(AttributeError):
        inst.line()
    with pytest.raises(AttributeError):
        inst.yyy


def test_dynamic_attribute_added_later():
    inst = CustomClass()
    inst.dynamic = "added later"
    assert inst.custom_dynamic == "added later"
    with pytest.raises(AttributeError):
        inst.dynamic


def test_init_with_argument():
    inst = CustomClass(10)
    assert inst.custom_val == 10


def test_magic_methods_still_work():
    # проверяю что магические методы не переименовались
    inst = CustomClass()
    assert str(inst) == "Custom_by_metaclass"
    assert "Custom_by_metaclass" == str(inst)


def test_class_attribute_set_after_creation():
    # атрибуты добавленные классу после создания тоже подменяются
    CustomClass.extra = 1
    assert CustomClass.custom_extra == 1
    with pytest.raises(AttributeError):
        CustomClass.extra


def test_double_prefix_not_added():
    # чтобы не получилось custom_custom_x
    inst = CustomClass()
    inst.custom_foo = 5
    assert inst.custom_foo == 5
    assert inst.__dict__["custom_foo"] == 5


def test_name_conflict_raises():
    # редкий случай: в классе есть и a, и custom_a - непонятно что оставить
    with pytest.raises(ValueError):
        class Broken(metaclass=CustomMeta):  # pylint: disable=unused-variable
            a = 1
            custom_a = 2


def test_own_setattr_is_not_replaced():
    # если в классе уже есть __setattr__ - метакласс его не трогает
    class WithOwnSetattr(metaclass=CustomMeta):
        def __setattr__(self, attr, value):
            object.__setattr__(self, attr + "_mine", value)

    inst = WithOwnSetattr()
    inst.qqq = 3
    assert inst.qqq_mine == 3
