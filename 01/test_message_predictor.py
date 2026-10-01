"""Тесты для message_predictor."""

from unittest import mock

import pytest

from message_predictor import UNKNOWN_WORD, SomeModel, predict_message_mood


def test_homework_examples():
    # эти проверки прямо из условия дз
    assert predict_message_mood("Чапаев и пустота") == "отл"
    assert predict_message_mood("Чапаев и пустота", 0.8, 0.99) == "норм"
    assert predict_message_mood("Вулкан") == "неуд"


@mock.patch("message_predictor.SomeModel.predict")
def test_message_goes_to_model(predict_mock):
    # сообщение должно прийти в модель как есть
    predict_mock.return_value = 0.5

    predict_message_mood("какое-то сообщение")

    predict_mock.assert_called_once_with("какое-то сообщение")


@pytest.mark.parametrize(
    "rate, bad, good, expected",
    [
        (0.5, 0.3, 0.8, "норм"),
        (0.29, 0.3, 0.8, "неуд"),
        (0.81, 0.3, 0.8, "отл"),
        # ровно на пороге это еще норм, границы не включаются
        (0.3, 0.3, 0.8, "норм"),
        (0.8, 0.3, 0.8, "норм"),
        # свои пороги тоже уважаются
        (0.5, 0.6, 0.8, "неуд"),
        (0.5, 0.1, 0.4, "отл"),
    ],
)
@mock.patch("message_predictor.SomeModel.predict")
def test_thresholds(predict_mock, rate, bad, good, expected):
    predict_mock.return_value = rate

    assert predict_message_mood("сообщение", bad, good) == expected


def test_model_trusts_chapaev():
    model = SomeModel()
    assert model.predict("Чапаев и пустота") > 0.8
    assert model.predict("Вулкан") < 0.3


def test_model_ignores_case():
    assert SomeModel().predict("ЧАПАЕВ") == SomeModel().predict("чапаев")


def test_model_empty_message():
    # пустому сообщению модель не доверяет 
    assert SomeModel().predict("") == 0.0


def test_model_unknown_words():
    assert SomeModel().predict("абракадабра") == UNKNOWN_WORD
    assert SomeModel().predict("какието слова") == UNKNOWN_WORD


def test_mood_with_real_model():
    # кот это 0.7, должно быть норм
    assert predict_message_mood("привет кот") == "норм"
    # python это 1.0
    assert predict_message_mood("люблю python") == "отл"
    # незнакомое слово только 0.1
    assert predict_message_mood("абракадабра") == "неуд"
