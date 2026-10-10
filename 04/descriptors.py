"""Дескрипторы с проверками - пример на тему моей (виртуальной) кофейни.

BaseDescriptor - базовый класс с абстрактным методом validate,
наследники обязаны его реализовать иначе их даже не создаст питон.
"""

from abc import ABC, abstractmethod


class BaseDescriptor(ABC):
    """базовый дескриптор, всю проверку отдаю наследникам"""

    def __set_name__(self, owner, name):
        # запоминаю под каким именем дескриптор лежит в классе
        self.attr_name = "_" + name

    def __get__(self, instance, owner):
        # если читать у класса - возвращаю сам дескриптор (так удобнее)
        if instance is None:
            return self
        return instance.__dict__.get(self.attr_name)

    def __set__(self, instance, value):
        # сначала проверка, потом сохранение
        self.validate(value)
        instance.__dict__[self.attr_name] = value

    @abstractmethod
    def validate(self, value):
        """проверяет значение, кидает TypeError/ValueError если что-то не так"""


class Integer(BaseDescriptor):
    """целое число, float не пролезет (я так хочу)"""

    def validate(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            # bool это тоже int на самом деле, но число True быть не должно
            raise TypeError(
                "ожидал int, получили " + type(value).__name__
            )


class String(BaseDescriptor):
    """строка, пустую запрещаю - у кофе всегда есть название"""

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(
                "ожидал str, получили " + type(value).__name__
            )
        if not value.strip():
            # одни пробелы считаю пустой строкой тоже
            raise ValueError("пустое имя нельзя")


class PositiveInteger(BaseDescriptor):
    """положительное целое, цена не может быть отрицательной"""

    def validate(self, value):
        # наследоваться от Integer и звать его проверку было бы красиво,
        # но для наглядности домашки пишу проверку сам
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(
                "ожидал int, получили " + type(value).__name__
            )
        if value <= 0:
            raise ValueError("цена должна быть больше нуля, получили " + str(value))


class Coffee:
    """заказ в кофейне, поля проверяются дескрипторами"""

    num = Integer()
    name = String()
    price = PositiveInteger()

    def __init__(self, num, name, price):
        self.num = num
        self.name = name
        self.price = price
