"""Метакласс CustomMeta - вешает префикс custom_ на все атрибуты класса.

Идея такая: при создании класса прохожусь по его namespace и переименовываю
каждый атрибут (кроме магических методов, их трогать нельзя иначе питон
откажется вызывать __init__ и все сломается).
Чтобы атрибуты ЭКЗЕМПЛЯРА тоже переименовывались, подсовываю классу
свой __setattr__ - он срабатывает и в __init__, и на dynами attribute.
"""

# вынес префикс в константу чтобы не копипастить
PREFIX = "custom_"


def add_prefix(name):
    """возвращает имя с префиксом, магические не трогаем"""
    if name.startswith("__") and name.endswith("__"):
        return name
    if name.startswith(PREFIX):
        # уже с префиксом, второй раз не добавляю (а то custom_custom_...)
        return name
    return PREFIX + name


class CustomMeta(type):
    """метакласс который добавляет custom_ ко всем именам"""

    def __new__(mcs, name, bases, namespace, **kwargs):
        new_namespace = {}
        for attr_name, attr_value in namespace.items():
            new_name = add_prefix(attr_name)
            if new_name != attr_name and new_name in namespace:
                # маловероятно но вдруг в классе есть и x и custom_x
                raise ValueError(
                    "конфликт имен в классе: " + attr_name + " и " + new_name
                )
            new_namespace[new_name] = attr_value

        # если автор класса сам написал __setattr__ - не лезу, он главный
        if "__setattr__" not in namespace:
            def custom_setattr(self, attr, value):
                object.__setattr__(self, add_prefix(attr), value)
            # имя мегическое чтобы питон сам его нашел
            new_namespace["__setattr__"] = custom_setattr

        return super().__new__(mcs, name, bases, new_namespace, **kwargs)

    def __setattr__(cls, attr, value):
        # атрибуты класса добавленные уже ПОСЛЕ создания класса тоже подменяю
        super().__setattr__(add_prefix(attr), value)
