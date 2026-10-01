"""Тесты для line_filter."""

from line_filter import filter_lines


def write_file(tmp_path, lines):
    # маленький хэлпер чтобы не писать одно и то же в каждом тесте
    path = tmp_path / "input.txt"
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def test_homework_example(tmp_path):
    # из условия: роза ищется, но со стоп-словом азора строка выкидывается
    path = write_file(tmp_path, ["а Роза упала на лапу Азора"])

    assert list(filter_lines(path, ["роза"], [])) == [
        "а Роза упала на лапу Азора"
    ]
    assert list(filter_lines(path, ["роза"], ["азора"])) == []


def test_case_does_not_matter(tmp_path):
    # и в поиске и в стоп-словах регистр не важен
    path = write_file(tmp_path, ["роза и азора"])

    assert list(filter_lines(path, ["РОЗА"], [])) == ["роза и азора"]
    assert list(filter_lines(path, ["роза"], ["АЗОРА"])) == []


def test_word_must_be_full(tmp_path):
    # роз это не роза- часть слова не считается совпадением
    path = write_file(tmp_path, ["а Роза упала на лапу Азора"])

    assert list(filter_lines(path, ["роз", "розан", "оза"], [])) == []


def test_line_comes_out_once(tmp_path):
    # два совпадения в одной строке не дублируют результат
    path = write_file(tmp_path, ["роза и еще раз роза"])

    assert list(filter_lines(path, ["роза"], [])) == ["роза и еще раз роза"]


def test_picks_only_matching_lines(tmp_path):
    path = write_file(
        tmp_path,
        ["роза цветет", "просто текст", "у розы шипы", "совсем не то"],
    )

    assert list(filter_lines(path, ["роза", "шипы"], [])) == [
        "роза цветет",
        "у розы шипы",
    ]


def test_no_matches(tmp_path):
    path = write_file(tmp_path, ["кот сидит", "собака спит"])

    assert list(filter_lines(path, ["роза"], [])) == []


def test_empty_file(tmp_path):
    path = write_file(tmp_path, [])

    assert list(filter_lines(path, ["роза"], [])) == []


def test_path_as_string(tmp_path):
    # путь можно передать и просто строкой
    path = write_file(tmp_path, ["тут роза"])

    assert list(filter_lines(str(path), ["роза"], [])) == ["тут роза"]


def test_open_file_object(tmp_path):
    # а можно уже открытый файл
    path = write_file(tmp_path, ["первая роза", "вторая строка"])

    with open(path, encoding="utf-8") as f:
        assert list(filter_lines(f, ["роза"], [])) == ["первая роза"]


def test_last_line_without_newline(tmp_path):
    # у последней строки перевода строки может и не быть
    path = tmp_path / "no_newline.txt"
    path.write_text("роза без перевода строки", encoding="utf-8")

    assert list(filter_lines(path, ["роза"], [])) == [
        "роза без перевода строки"
    ]
