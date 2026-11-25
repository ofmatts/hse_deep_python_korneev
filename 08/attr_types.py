"""Три варианта одного и того же класса для сравнения по памяти и времени.

Во всех трех лежит одно и то же: имя, две координаты и ссылка на
владельца (Owner). Отличается только то, как это все хранится:

* PlainPoint - обычные атрибуты, лежат в __dict__ каждого экземпляра;
* SlotsPoint - __slots__, никакого __dict__ нет;
* WeakPoint  - на владельца храним слабую ссылку (weakref), поэтому
  сам экземпляр не удерживает владельца в памяти.
"""

import weakref


class Owner:
    """тот на кого ссылаются точки. Отдельный класс нужен потому что
    на int или str слабую ссылку не повесить"""

    def __init__(self, owner_id):
        self.owner_id = owner_id


class PlainPoint:
    def __init__(self, name, x, y, owner):
        self.name = name
        self.x = x
        self.y = y
        self.owner = owner


class SlotsPoint:
    __slots__ = ("name", "x", "y", "owner")

    def __init__(self, name, x, y, owner):
        self.name = name
        self.x = x
        self.y = y
        self.owner = owner


class WeakPoint:
    def __init__(self, name, x, y, owner):
        self.name = name
        self.x = x
        self.y = y
        self._owner = weakref.ref(owner)

    @property
    def owner(self):
        # если владельца уже собрали GC, ref() вернет None
        return self._owner()

    @owner.setter
    def owner(self, new_owner):
        self._owner = weakref.ref(new_owner)
