"""Класс CustomList - список который умеет в арифметику.

Наследуюсь от встроенного list чтобы забрать себе все его методы,
а сверху добавляю поэлементное сложение/вычитание (с другими CustomList,
обычными списками и числами) и сравнение по сумме элементов.
Если списки разной длины, короткий добиваю нулями - так в задании.
"""


class CustomList(list):
    """Список с арифметикой, сравнивается по сумме элементов.

    Да, выглядит странно что [1, 2, 3] == [6], но так придумали
    авторы задания, кто я такой чтобы спорить.
    """

    def __add__(self, other):
        if isinstance(other, int):
            # число просто прибавляю к каждому элементу
            return CustomList((item + other) for item in self)

        if isinstance(other, list):
            # сюда попадает и обычный список, и второй CustomList
            # (он же тоже list в конце концов)
            left, right = self._same_size(other)
            return CustomList(a + b for a, b in zip(left, right))

        # с чем попало складываться не умею, честно говорю об этом питону
        return NotImplemented

    def __radd__(self, other):
        # когда я справа: 10 + ... или [2, 5] + ...
        # сложение поэлементное, так что порядок операндов не важен
        return self + other

    def __sub__(self, other):
        if isinstance(other, int):
            return CustomList(item - other for item in self)

        if isinstance(other, list):
            left, right = self._same_size(other)
            return CustomList(a - b for a, b in zip(left, right))

        return NotImplemented

    def __rsub__(self, other):
        # а вот тут порядок уже важен: 10 - CustomList([2, 5]) это [8, 5],
        # а не [-8, -5], поэтому разворачиваю руками
        if isinstance(other, int):
            return CustomList(other - item for item in self)

        if isinstance(other, list):
            # оборачиваю левый список в CustomList и вычитаю как обычно
            return CustomList(other) - self

        return NotImplemented

    def _same_size(self, other):
        """возвращает копии списков добитые нулями до одной длины"""
        size = max(len(self), len(other))
        left = list(self) + [0] * (size - len(self))
        right = list(other) + [0] * (size - len(other))
        return left, right

    # дальше все сравнения одинаковые: смотрю на суммы элементов.
    # с чем-то кроме CustomList сравниваться не умею, отдаю NotImplemented

    def __eq__(self, other):
        if isinstance(other, CustomList):
            return sum(self) == sum(other)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, CustomList):
            return sum(self) != sum(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, CustomList):
            return sum(self) < sum(other)
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, CustomList):
            return sum(self) <= sum(other)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, CustomList):
            return sum(self) > sum(other)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, CustomList):
            return sum(self) >= sum(other)
        return NotImplemented

    def __str__(self):
        # по заданию: печатаю элементы и их сумму
        return f"{list(self)} сумма = {sum(self)}"
