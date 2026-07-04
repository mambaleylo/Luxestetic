#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт: проверяет, что логин в LuxEstetic MIS проходит успешно.
Запуск: python3 test_login.py
"""

import requests

BASE_URL = "https://luxestetic.mis.aibolit.by"
LOGIN_URL = f"{BASE_URL}/index.php"

# ==== ЗАПОЛНИТЕ СВОИМИ ДАННЫМИ ====
USERNAME = "Kovtik"
PASSWORD = "375(29)866-71-34As"  # проверьте, это ли реально пароль -
                                  # на скриншоте это выглядит как логин(телефон)+хвост
# ===================================


def login(session: requests.Session) -> bool:
    """
    Логинимся на сайте. Сайт отдаёт windows-1251, поэтому кодируем
    данные формы в этой кодировке, а не в utf-8 (иначе кириллица
    в логине/ответе может побиться).
    """
    # Сначала открываем страницу логина, чтобы получить куки сессии
    resp = session.get(LOGIN_URL)
    resp.encoding = "windows-1251"

    payload = {
        "user": USERNAME,
        "pass": PASSWORD,
    }

    resp = session.post(
        LOGIN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=windows-1251"},
        allow_redirects=True,
    )
    resp.encoding = "windows-1251"

    # Признаки успешного логина нужно будет уточнить -
    # пока проверяем по отсутствию формы логина на странице ответа
    if 'name="pass"' in resp.text:
        print("❌ Логин НЕ пройден — форма логина всё ещё на странице.")
        print("---- Первые 500 символов ответа ----")
        print(resp.text[:500])
        return False
    else:
        print("✅ Похоже, логин пройден (формы логина в ответе нет).")
        print(f"URL после редиректа: {resp.url}")
        print(f"Код ответа: {resp.status_code}")
        return True


def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    ok = login(session)

    if ok:
        # Сохраняем куки сессии, чтобы потом переиспользовать в основном боте
        print("\nКуки сессии:")
        for c in session.cookies:
            print(f"  {c.name} = {c.value}")


if __name__ == "__main__":
    main()
