#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Логинимся и скачиваем HTML страницы записей (visit.php) на сегодня,
чтобы посмотреть структуру и понять, как парсить записи к врачу Ковтик.

Это ВРЕМЕННЫЙ диагностический скрипт (не финальный бот).
Он выведет в лог кусок HTML страницы записей.
"""

import os
import re
import sys
import time
import requests

BASE_URL = "https://luxestetic.mis.aibolit.by"
LOGIN_URL = f"{BASE_URL}/index.php"

USERNAME = os.environ.get("MIS_LOGIN")
PASSWORD = os.environ.get("MIS_PASSWORD")

if not USERNAME or not PASSWORD:
    print("❌ Не заданы переменные окружения MIS_LOGIN и/или MIS_PASSWORD.")
    print("   Задайте их в настройках проекта на bothost.ru и перезапустите.")
    sys.exit(1)


def login(session: requests.Session) -> bool:
    session.get(LOGIN_URL)
    resp = session.post(
        LOGIN_URL,
        data={"user": USERNAME, "pass": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=windows-1251"},
        allow_redirects=True,
    )
    resp.encoding = "windows-1251"
    return 'name="pass"' not in resp.text


def dump_visit_page(session: requests.Session):
    from datetime import date
    today = date.today().strftime("%d.%m.%Y")
    url = f"{BASE_URL}/engine/visit.php?date1={today}&date2={today}"
    resp = session.get(url)
    resp.encoding = "windows-1251"
    html = resp.text

    print(f"===== Длина HTML: {len(html)} символов =====")

    # Ищем упоминания "Ковтик" в тексте, чтобы найти нужный блок
    idxs = [m.start() for m in re.finditer("Ковтик", html)]
    print(f"Найдено упоминаний 'Ковтик': {len(idxs)}")

    if idxs:
        # печатаем контекст вокруг первого упоминания
        i = idxs[0]
        start = max(0, i - 800)
        end = min(len(html), i + 800)
        print("----- КОНТЕКСТ ВОКРУГ 'Ковтик' -----")
        print(html[start:end])
        print("----- КОНЕЦ КОНТЕКСТА -----")
    else:
        # если не нашли - печатаем начало страницы, чтобы понять её структуру
        print("----- НАЧАЛО HTML (т.к. 'Ковтик' не найден) -----")
        print(html[:3000])
        print("----- КОНЕЦ -----")


def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    if not login(session):
        print("❌ Логин не пройден, останавливаюсь.")
        return

    print("✅ Логин пройден.")
    dump_visit_page(session)

    # Держим процесс живым, чтобы bothost не считал бота упавшим,
    # пока мы не соберём достаточно информации для финальной версии.
    print("\nСкрипт диагностики завершён, но процесс будет висеть (для bothost).")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
