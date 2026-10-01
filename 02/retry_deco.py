"""Декоратор, который логирует вызовы и перезапускает функцию если она падает."""

from functools import wraps


def retry_deco(retries=3, expected_exceptions=None):
    """Логирует каждый вызов и результат, при ошибке перезапускает функцию.

    retries - сколько всего попыток запуска, в примере из дз retry_deco(3)
    делает ровно 3 попытки, 1я тоже считается.
    expected_exceptions - исключения которые считаю нормальной работой функции:
    на них даже не пытаюсь перезапускать, сразу отдаю наверх.
    """

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # начало строчки для лога собираю один раз, а номер попытки
            # и результат дописываю уже по ходу дела
            log = f'run "{func.__name__}" with'
            if args:
                log += f" positional args = {args},"
            if kwargs:
                log += f" keyword kwargs = {kwargs},"

            attempt = 1
            while True:
                # ловлю вообще все - функция может кидать что угодно
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    print(f"{log} attempt = {attempt}, exception = {type(exc).__name__}")

                    if expected_exceptions and isinstance(exc, tuple(expected_exceptions)):
                        # нормальный режим работы, перезапускать не надо
                        raise
                    if attempt == retries:
                        # попытки кончились, ошибка летит наверх как есть
                        raise
                    attempt += 1
                else:
                    print(f"{log} attempt = {attempt}, result = {result}")
                    return result

        return wrapper

    return deco
