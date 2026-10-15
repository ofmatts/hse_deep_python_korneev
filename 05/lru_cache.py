"""LRU-кэш - хранилище ключей со значениями и лимитом на их количество.

Когда место заканчивается, выкидывается ключ к которому дольше всего
не обращались (Least Recently Used, отсюда и название). Все операции
в среднем за O(1) - амортизированная сложность, кажется так это
называлось на паре.

OrderedDict из задания запрещен. Можно было бы выкрутиться тем что
обычный dict и так помнит порядок вставки, но список я в этот раз
решил написать руками: значения лежат в dict, а порядок хранит
двусвязный список. Узлы-заглушки по краям - из конспекта лекции.
"""


class _ListNode:
    """звено двусвязного списка.

    key храню чтобы при выкидывании узла понять какой ключ удалять из
    словаря - по самому узлу этого не узнать.
    """

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """кэш с лимитом, выкидывает самое залежавшееся значение."""

    def __init__(self, limit=42):
        if limit <= 0:
            # с нулевым лимитом кэш превращается в тыкву: каждый set
            # сразу выкидывает все что сам же и записал. лучше упасть сразу
            raise ValueError("limit должен быть больше нуля, а был " + str(limit))
        self._limit = limit
        self._nodes = {}  # key -> _ListNode

        # список держу между двумя узлами-пустышками, тогда у всех
        # настоящих узлов всегда есть соседи и на None проверять нечего.
        # head.next - самый свежий ключ, tail.prev - кандидат на вылет
        self._head = _ListNode()
        self._tail = _ListNode()
        self._head.next = self._tail
        self._tail.prev = self._head

    def get(self, key):
        """значение по ключу или None, ключ становится свежим"""
        node = self._nodes.get(key)
        if node is None:
            return None
        # любое обращение обновляет очередь: вынул и вставил в начало
        self._unlink(node)
        self._add_to_front(node)
        return node.value

    def set(self, key, value):
        """записывает значение, при переполнении выкидывает самый старый ключ"""
        node = self._nodes.get(key)
        if node is not None:
            # ключ уже внутри, место под него уже занято - ничего не выкидываю
            node.value = value
            self._unlink(node)
            self._add_to_front(node)
            return

        if len(self._nodes) >= self._limit:
            self._evict_oldest()

        node = _ListNode(key, value)
        self._nodes[key] = node
        self._add_to_front(node)

    def _unlink(self, node):
        """вырезает узел из списка, соседей склеивает между собой"""
        node.prev.next = node.next
        node.next.prev = node.prev
        # у самого узла ссылки подчищаю, чтобы не висели битые - так
        # при дебаге в списке не остаются призраки
        node.prev = None
        node.next = None

    def _add_to_front(self, node):
        """вставляет узел сразу после head, то есть делает его свежим"""
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node
        self._head.next = node

    def _evict_oldest(self):
        """убирает ключ у tail - к нему дольше всего не обращались"""
        oldest = self._tail.prev
        self._unlink(oldest)
        del self._nodes[oldest.key]

    # в задании была ремарка что get/set можно сделать по аналогии
    # с dict. сделал оба варианта сразу, так надежнее

    def __getitem__(self, key):
        # обычный dict при отсутствующем ключе кидает KeyError, но раз
        # мой get молчит и отдает None, [] тоже молчит - для единообразия
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __len__(self):
        # в основном для тестов, но пусть будет
        return len(self._nodes)
