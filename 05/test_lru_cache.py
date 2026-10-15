"""Тесты для LRUCache."""

import pytest

from lru_cache import LRUCache


def test_example_from_homework():
    # пример из задания, он же главный тест
    cache = LRUCache(2)

    cache.set("k1", "val1")
    cache.set("k2", "val2")

    assert cache.get("k3") is None
    assert cache.get("k2") == "val2"
    assert cache.get("k1") == "val1"

    cache.set("k3", "val3")

    assert cache.get("k3") == "val3"
    assert cache.get("k2") is None
    assert cache.get("k1") == "val1"


def test_get_from_empty_cache():
    cache = LRUCache(5)
    assert cache.get("nothing") is None


def test_set_and_get():
    cache = LRUCache(5)
    cache.set("answer", 42)
    assert cache.get("answer") == 42


def test_update_existing_key():
    cache = LRUCache(3)
    cache.set("a", 1)
    cache.set("a", 2)
    assert cache.get("a") == 2
    # обновление занимает то же самое место, нового не появляется
    assert len(cache) == 1


def test_update_counts_as_usage():
    # обновленный ключ считается свежим и не вылетает первым
    cache = LRUCache(2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("a", 10)  # теперь залежался b
    cache.set("c", 3)  # вылетает b, а не a
    assert cache.get("b") is None
    assert cache.get("a") == 10
    assert cache.get("c") == 3


def test_evicts_least_recently_used():
    # трогаю ключи вразнобой и смотрю кто именно вылетит
    cache = LRUCache(3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") == 1  # a теперь свежий, b - самый залежавшийся
    cache.set("d", 4)  # вылетает b
    assert cache.get("b") is None
    assert cache.get("d") == 4
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_insert_more_than_limit():
    # заполняю через край, живыми остаются последние ключи
    cache = LRUCache(3)
    for number in range(5):
        cache.set(number, number * 100)
    assert cache.get(0) is None
    assert cache.get(1) is None
    assert cache.get(2) == 200
    assert cache.get(3) == 300
    assert cache.get(4) == 400
    assert len(cache) == 3


def test_limit_one():
    cache = LRUCache(1)
    cache.set("only", 1)
    assert cache.get("only") == 1
    cache.set("another", 2)
    assert cache.get("only") is None
    assert cache.get("another") == 2


def test_default_limit_is_42():
    # из сигнатуры в задании
    cache = LRUCache()
    for number in range(100):
        cache.set(number, number)
    assert len(cache) == 42
    assert cache.get(57) is None
    assert cache.get(58) == 58
    assert cache.get(99) == 99


def test_bad_limit_raises():
    # нулевой и отрицательный лимит смысла не имеют
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-10)


def test_dict_style_access():
    # в задании было "можно сделать по аналогии с dict", вот проверка
    cache = LRUCache(2)
    cache["k1"] = "val1"
    assert cache["k1"] == "val1"
    assert cache["nope"] is None  # как у get, просто None
    cache["k2"] = "val2"
    cache["k3"] = "val3"  # вылетает k1, он самый старый
    assert cache["k1"] is None
    assert cache["k2"] == "val2"
    assert cache["k3"] == "val3"


def test_dict_style_refreshes_too():
    # и чтение через [] тоже должно обновлять порядок
    cache = LRUCache(2)
    cache["a"] = 1
    cache["b"] = 2
    assert cache.get("a") == 1  # тронул a, залежался b
    cache["c"] = 3
    assert cache.get("b") is None
    assert cache.get("a") == 1


def test_same_key_many_times():
    # один ключ можно дергать хоть бесконечно, место он держит одно
    cache = LRUCache(2)
    for attempt in range(10):
        cache.set("x", attempt)
    cache.set("y", 0)
    assert len(cache) == 2
    assert cache.get("x") == 9


def test_none_value():
    # тонкость: значение None от "ключа нет" никак не отличить, get и
    # в том и в другом случае вернет None. в задании про это ни слова,
    # так что хотя бы фиксирую поведение тестом
    cache = LRUCache(2)
    cache.set("void", None)
    assert cache.get("void") is None
    assert cache.get("missing") is None
    # но ключ при этом живой и место занимает
    assert len(cache) == 1


def test_unhashable_key():
    # внутри лежит dict, так что список вместо ключа отвергается сразу
    cache = LRUCache(2)
    with pytest.raises(TypeError):
        cache.set(["нельзя", "хэшировать"], 1)


def test_round_and_round():
    # гоняю ключи по кругу, смотрю что список не путается в ссылках.
    # честно проверять O(1) замерами в тесте - себе дороже, так что
    # хотя бы прогоняю много перестановок подряд
    cache = LRUCache(3)
    for step in range(20):
        cache.set(step % 5, step)
    # последними заходили 2, 3 и 4 (на 19м шаге - ключ 4)
    assert len(cache) == 3
    assert cache.get(0) is None
    assert cache.get(1) is None
    assert cache.get(2) == 17
    assert cache.get(3) == 18
    assert cache.get(4) == 19
