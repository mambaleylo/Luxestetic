#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Логинимся и скачиваем страницу расписания конкретно врача Ковтик
(specialist_id=1), сохраняем HTML таблицы в result.txt для анализа структуры.
"""

import os
import sys
import time
import requests

BASE_URL = "https://luxestetic.mis.aibolit.by"
LOGIN_URL = f"{BASE_URL}/index.php"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = os.path.join(SCRIPT_DIR, "result.txt")

output_lines = []


def log(msg: str):
    output_lines.append(msg)
    print(msg)


def save_result():
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))


CANDIDATE_PATHS = [
    os.path.join(SCRIPT_DIR, "credentials.txt"),
    "/app/credentials.txt",
    "credentials.txt",
]

USERNAME = None
PASSWORD = None

for path in CANDIDATE_PATHS:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f.readlines()]
        if len(lines) >= 2:
            USERNAME, PASSWORD = lines[0], lines[1]
            break

if not USERNAME or not PASSWORD:
    log("❌ Не найден credentials.txt")
    save_result()
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


def dump_kovtik_schedule(session: requests.Session):
    from datetime import date, timedelta
    today = date.today()
    end = today + timedelta(days=30)
    d1 = today.strftime("%d.%m.%Y")
    d2 = end.strftime("%d.%m.%Y")

    url = (f"{BASE_URL}/engine/visit.php?date1={d1}&date2={d2}"
           f"&viewmethod=&specialist_id_list=&specialization=0&specialist_id=1&status=0")

    resp = session.get(url)
    resp.encoding = "windows-1251"
    html = resp.text

    log(f"===== URL: {url} =====")
    log(f"===== Длина HTML: {len(html)} символов =====")

    idx = html.find('id="base"')
    if idx == -1:
        log("Тег с id='base' не найден, ищем 'Время' 'Пациент'")
        idx = html.find("Пациент")

    if idx != -1:
        start = max(0, idx - 200)
        end_i = min(len(html), idx + 6000)
        log("----- ФРАГМЕНТ ТАБЛИЦЫ -----")
        log(html[start:end_i])
        log("----- КОНЕЦ ФРАГМЕНТА -----")
    else:
        log("Не нашли таблицу, показываю начало HTML")
        log(html[:3000])


def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    if not login(session):
        log("❌ Логин не пройден.")
    else:
        log("✅ Логин пройден.")
        dump_kovtik_schedule(session)

    save_result()
    log("\nГотово, процесс висит (для bothost).")
    save_result()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
