#!/usr/bin/env python3
"""Локальный сервер SmilePlan с SPA-fallback.

В отличие от `python3 -m http.server`, неизвестные пути внутри /smileplan/
(например /smileplan/patients/<id>/estimate/new) отдают index.html,
поэтому обновление страницы и прямые ссылки работают и на телефоне, и на ПК.

Запуск:  python3 serve_smileplan.py [порт]     (по умолчанию 8080)
Открыть: на ПК    http://localhost:8080/smileplan/
         на телефоне (одна сеть Wi-Fi)  http://<IP_компьютера>:8080/smileplan/
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PREFIX = "/smileplan/"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        url_path = self.path.split("?", 1)[0].split("#", 1)[0]
        if url_path == "/":
            self.send_response(302)
            self.send_header("Location", PREFIX)
            self.end_headers()
            return None
        if (
            url_path.startswith(PREFIX)
            and not os.path.exists(path)
            and not os.path.splitext(url_path)[1]
        ):
            # маршрут SPA, а не файл — отдаём оболочку приложения
            self.path = PREFIX + "index.html"
        return super().send_head()

    def end_headers(self):
        # sw.js и html не должны застревать в HTTP-кэше телефона
        if self.path.endswith(("sw.js", ".html", "/")) or self.path.endswith("manifest.json"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"SmilePlan: http://localhost:{port}{PREFIX}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
