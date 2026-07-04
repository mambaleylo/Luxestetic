#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Логинимся (данные читаем из credentials.txt, лежащего рядом с этим файлом)
и скачиваем HTML страницы записей (visit.php) на сегодня, ищем 'Ковтик'.
"""

import os
import re
import sys
import time
import requests

BASE_URL = "https://luxestetic.mis.aibolit.by"
LOGIN_URL = f"{BASE_URL}/index.php"

# Ищем credentials.txt рядом со скриптом (или в /app, на случай другой рабочей директории)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATE_PATHS = [
    os.path.join(SCRIPT_DIR, "credentials.txt"),
    "/app/credentials.txt",
    "credentials.txt",
]

USERNAME = None
PASSWORD = None
used_path = None

for path in CANDIDATE_PATHS:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f.readlines()]
        if len(lines) >= 2:
            USERNAME, PASSWORD = lines[0], lines[1]
            used_path = path
            break

if not USERNAME or not PASSWORD:
    print("❌ Не найден файл credentials.txt (или в нём меньше 2 строк).")
    print("   Проверенные пути:")
    for p in CANDIDATE_PATHS:
        print(f"     {p}: {'есть' if os.path.isfile(p) else 'нет'}")
    print("   Загрузите credentials.txt рядом с test_login.py через файловый менеджер бота.")
    sys.exit(1)

print(f"✅ Учётные данные прочитаны из: {used_path}")
print(f"   Логин: длина {len(USERNAME)} симв.")
print(f"   Пароль: длина {len(PASSWORD)} симв.")


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

    idxs = [m.start() for m in re.finditer("Ковтик", html)]
    print(f"Найдено упоминаний 'Ковтик': {len(idxs)}")

    if idxs:
        i = idxs[0]
        start = max(0, i - 800)
        end = min(len(html), i + 800)
        print("----- КОНТЕКСТ ВОКРУГ 'Ковтик' -----")
        print(html[start:end])
        print("----- КОНЕЦ КОНТЕКСТА -----")
    else:
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
    else:
        print("✅ Логин пройден.")
        dump_visit_page(session)

    print("\nСкрипт диагностики завершён, процесс висит (для bothost).")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
