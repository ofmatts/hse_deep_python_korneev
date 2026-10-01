"""Тесты для json_processing."""

import json

import pytest

from json_processing import process_json


def run_process(json_str, required_keys, tokens):
    # маленький хэлпер: запускаю process_json и собираю все пары
    # (ключ, токен) которые пришли в коллбек
    calls = []
    process_json(json_str, required_keys, tokens, lambda key, token: calls.append((key, token)))
    return calls


def test_homework_example():
    # прямо из условия: KEY2 не совпал с key2, потому что ключи в регистре,
    # зато WORD1 нашелся, хотя в значении написано Word1
    json_str = '{"key1": "Word1 word2", "key2": "word2 word3"}'

    calls = run_process(json_str, ["key1", "KEY2"], ["WORD1", "word2"])

    assert calls == [("key1", "WORD1"), ("key1", "word2")]


def test_keys_are_case_sensitive():
    # ключи ищу как есть, key1 и KEY1 это разные ключи
    json_str = '{"key1": "word1"}'

    assert run_process(json_str, ["key1"], ["WORD1"]) == [("key1", "WORD1")]
    assert run_process(json_str, ["KEY1"], ["word1"]) == []


def test_tokens_ignore_case():
    # токены без регистра, и в коллбек токен приходит в том виде
    # в котором его передали
    json_str = '{"k": "Слово и снова слово"}'

    calls = run_process(json_str, ["k"], ["СЛОВО", "снова"])

    assert calls == [("k", "СЛОВО"), ("k", "снова")]


def test_token_must_be_whole_word():
    # часть слова это не токен
    json_str = '{"k": "word2 word3"}'

    assert run_process(json_str, ["k"], ["word", "ord2", "2"]) == []


def test_survives_any_number_of_spaces():
    # пробелов может быть сколько угодно, и одно слово может встретиться
    # несколько раз - коллбек все равно зову по разу на токен
    json_str = '{"k": "a   b   a"}'

    assert run_process(json_str, ["k"], ["b", "a"]) == [("k", "b"), ("k", "a")]


def test_several_keys():
    json_str = '{"a": "one two", "b": "two", "c": "one"}'

    calls = run_process(json_str, ["a", "b", "c", "d"], ["one", "two"])

    # ключа d в json просто нет, ну и ладно
    assert calls == [("a", "one"), ("a", "two"), ("b", "two"), ("c", "one")]


def test_empty_lists():
    # с пустыми списками делать нечего
    assert run_process('{"k": "word"}', [], ["word"]) == []
    assert run_process('{"k": "word"}', ["k"], []) == []


def test_without_optional_arguments():
    # нет ключей, токенов или коллбека - просто выхожу, без ошибок
    json_str = '{"k": "word"}'

    assert process_json(json_str) is None
    assert process_json(json_str, ["k"]) is None
    assert process_json(json_str, ["k"], ["word"]) is None


def test_broken_json():
    # кривой json пусть падает как падает, ничего выдумывать не буду
    with pytest.raises(json.JSONDecodeError):
        run_process("это точно не json", ["k"], ["word"])
