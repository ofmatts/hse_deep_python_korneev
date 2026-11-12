"""Тесты для fetcher.

В интернет не хожу, вместо этого поднимаю маленький локальный сервер
из aiohttp. pytest-asyncio в зависимостях нет, поэтому корутины
запускаю через asyncio.run.
"""

import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

import fetcher


def make_app(stats=None):
    stats = stats if stats is not None else {"now": 0, "max": 0}

    async def ok(_request):
        return web.Response(text="hello")

    async def not_found(_request):
        return web.Response(status=404, text="no")

    async def slow(_request):
        stats["now"] += 1
        stats["max"] = max(stats["max"], stats["now"])
        await asyncio.sleep(0.05)
        stats["now"] -= 1
        return web.Response(text="slow")

    async def very_slow(_request):
        await asyncio.sleep(1)
        return web.Response(text="zzz")

    app = web.Application()
    app.router.add_get("/ok", ok)
    app.router.add_get("/404", not_found)
    app.router.add_get("/slow", slow)
    app.router.add_get("/very_slow", very_slow)
    return app


@pytest.fixture
def urls_file(tmp_path):
    path = tmp_path / "urls.txt"
    path.write_text("# комментарий\nhttp://a.com\n\n   http://b.com  \n#http://c.com\n")
    return path


# ---------- read_urls ----------


def test_read_urls(urls_file):
    assert fetcher.read_urls(urls_file) == ["http://a.com", "http://b.com"]


def test_read_urls_empty_file(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("")
    assert fetcher.read_urls(path) == []


def test_read_urls_no_file(tmp_path):
    with pytest.raises(OSError):
        fetcher.read_urls(tmp_path / "nothing.txt")


# ---------- fetch / fetch_all ----------


def test_fetch_all_ok():
    async def run():
        async with TestServer(make_app()) as server:
            url = str(server.make_url("/ok"))
            return url, await fetcher.fetch_all([url], 1)

    url, results = asyncio.run(run())
    assert results == [{"url": url, "status": 200, "size": 5, "error": None}]


def test_fetch_all_bad_status_is_not_error():
    async def run():
        async with TestServer(make_app()) as server:
            return await fetcher.fetch_all([str(server.make_url("/404"))], 2)

    res = asyncio.run(run())[0]
    assert res["status"] == 404
    assert res["error"] is None


def test_fetch_all_keeps_order():
    async def run():
        async with TestServer(make_app()) as server:
            urls = [str(server.make_url(p)) for p in ("/slow", "/ok", "/404", "/ok")]
            return urls, await fetcher.fetch_all(urls, 4)

    urls, results = asyncio.run(run())
    assert [r["url"] for r in results] == urls
    assert [r["status"] for r in results] == [200, 200, 404, 200]


def test_fetch_all_empty_list():
    assert asyncio.run(fetcher.fetch_all([], 3)) == []


def test_connection_error():
    # на 1 порту никто не слушает
    results = asyncio.run(fetcher.fetch_all(["http://127.0.0.1:1/"], 1))
    assert results[0]["status"] is None
    assert results[0]["error"]


def test_broken_url_does_not_break_others():
    async def run():
        async with TestServer(make_app()) as server:
            urls = ["http://127.0.0.1:1/", str(server.make_url("/ok"))]
            return await fetcher.fetch_all(urls, 2)

    bad, good = asyncio.run(run())
    assert bad["error"]
    assert good["status"] == 200


def test_timeout(monkeypatch):
    monkeypatch.setattr(fetcher, "TIMEOUT", 0.1)

    async def run():
        async with TestServer(make_app()) as server:
            return await fetcher.fetch_all([str(server.make_url("/very_slow"))], 1)

    res = asyncio.run(run())[0]
    assert res["status"] is None
    assert res["error"]


@pytest.mark.parametrize("count", [0, -1])
def test_fetch_all_wrong_count(count):
    with pytest.raises(ValueError):
        asyncio.run(fetcher.fetch_all(["http://a.com"], count))


@pytest.mark.parametrize("count", [1, 3, 5])
def test_concurrency_limit(count):
    stats = {"now": 0, "max": 0}

    async def run():
        async with TestServer(make_app(stats)) as server:
            urls = [str(server.make_url("/slow"))] * 10
            return await fetcher.fetch_all(urls, count)

    results = asyncio.run(run())
    assert len(results) == 10
    # больше count не было ни разу, и до count доходило
    assert stats["max"] == count


# ---------- parse_args ----------


def test_parse_args_with_flag():
    assert fetcher.parse_args(["-c", "7", "urls.txt"]) == (7, "urls.txt")


def test_parse_args_long_flag():
    assert fetcher.parse_args(["--count", "3", "urls.txt"]) == (3, "urls.txt")


def test_parse_args_positional():
    assert fetcher.parse_args(["10", "urls.txt"]) == (10, "urls.txt")


def test_parse_args_default_count():
    assert fetcher.parse_args(["urls.txt"]) == (fetcher.DEFAULT_COUNT, "urls.txt")


def test_parse_args_count_twice():
    with pytest.raises(SystemExit):
        fetcher.parse_args(["-c", "5", "10", "urls.txt"])


def test_parse_args_no_args():
    with pytest.raises(SystemExit):
        fetcher.parse_args([])


def test_parse_args_too_many():
    with pytest.raises(SystemExit):
        fetcher.parse_args(["a", "b", "c"])


def test_parse_args_two_files_without_number():
    with pytest.raises(SystemExit):
        fetcher.parse_args(["a.txt", "b.txt"])


@pytest.mark.parametrize("argv", [["-c", "0", "urls.txt"], ["0", "urls.txt"]])
def test_parse_args_zero(argv):
    with pytest.raises(SystemExit):
        fetcher.parse_args(argv)


# ---------- main ----------


def test_main(monkeypatch, capsys, urls_file):
    got = {}

    async def fake_fetch_all(urls, count):
        got["urls"] = urls
        got["count"] = count
        return [
            {"url": urls[0], "status": 200, "size": 12, "error": None},
            {"url": urls[1], "status": None, "size": 0, "error": "boom"},
        ]

    monkeypatch.setattr(fetcher, "fetch_all", fake_fetch_all)

    code = fetcher.main(["-c", "4", str(urls_file)])

    assert code == 0
    assert got == {"urls": ["http://a.com", "http://b.com"], "count": 4}
    out = capsys.readouterr().out.splitlines()
    assert out == ["200 12 http://a.com", "ERR boom http://b.com"]


def test_main_positional(monkeypatch, urls_file):
    got = {}

    async def fake_fetch_all(_urls, count):
        got["count"] = count
        return []

    monkeypatch.setattr(fetcher, "fetch_all", fake_fetch_all)

    assert fetcher.main(["6", str(urls_file)]) == 0
    assert got["count"] == 6


def test_main_no_file(tmp_path, capsys):
    code = fetcher.main([str(tmp_path / "nothing.txt")])
    assert code == 1
    assert "не могу прочитать файл" in capsys.readouterr().err
