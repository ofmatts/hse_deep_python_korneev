"""Асинхронная обкачка урлов из файла.

Запуск (оба варианта работают):
    python fetcher.py -c 10 urls.txt
    python fetcher.py 10 urls.txt

В файле один урл на строку. Пустые строки и строки с # в начале
пропускаю, чтобы можно было комментировать список.

Одновременность ограничиваю семафором: задач создается сразу много,
но внутрь запроса пускает только N штук.
"""

import argparse
import asyncio
import sys

import aiohttp

# сколько секунд ждем один урл, потом сдаемся
TIMEOUT = 10
DEFAULT_COUNT = 10


def read_urls(filename):
    """читает файл и возвращает список урлов"""
    urls = []
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


async def fetch(session, url):
    """качает один урл, возвращает словарь с результатом.

    Исключения наружу не выпускаю - иначе один битый урл завалит gather
    и остальные результаты потеряются.
    """
    try:
        async with session.get(url) as resp:
            body = await resp.read()
            return {"url": url, "status": resp.status, "size": len(body), "error": None}
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        # у таймаута текст ошибки пустой, поэтому подставляю имя класса
        text = str(err) or type(err).__name__
        return {"url": url, "status": None, "size": 0, "error": text}


async def fetch_all(urls, count=DEFAULT_COUNT):
    """качает все урлы, одновременно не больше count штук.

    Порядок результатов такой же как порядок урлов.
    """
    if count < 1:
        raise ValueError("count должен быть больше нуля")

    sem = asyncio.Semaphore(count)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        async def limited(url):
            async with sem:
                return await fetch(session, url)

        tasks = [limited(url) for url in urls]
        return await asyncio.gather(*tasks)


def parse_args(argv=None):
    """разбирает аргументы, возвращает (количество, имя файла)"""
    parser = argparse.ArgumentParser(description="асинхронная обкачка урлов из файла")
    parser.add_argument("-c", "--count", type=int, help="сколько запросов одновременно")
    parser.add_argument("items", nargs="+", metavar="[N] файл")
    ns = parser.parse_args(argv)

    items = ns.items
    count = DEFAULT_COUNT if ns.count is None else ns.count
    filename = None
    if len(items) == 2 and items[0].isdigit():
        # вариант "fetcher.py 10 urls.txt"
        if ns.count is not None:
            parser.error("количество указано два раза")
        count = int(items[0])
        filename = items[1]
    elif len(items) == 1:
        filename = items[0]
    else:
        parser.error("нужно передать файл с урлами (и, если хочется, количество)")

    if count < 1:
        parser.error("количество запросов должно быть больше нуля")
    return count, filename


def print_results(results):
    for res in results:
        if res["error"] is None:
            print(res["status"], res["size"], res["url"])
        else:
            print("ERR", res["error"], res["url"])


def main(argv=None):
    count, filename = parse_args(argv)

    try:
        urls = read_urls(filename)
    except OSError as err:
        print("не могу прочитать файл:", err, file=sys.stderr)
        return 1

    results = asyncio.run(fetch_all(urls, count))
    print_results(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
