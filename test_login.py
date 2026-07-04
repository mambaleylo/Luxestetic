#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностический скрипт: печатает ВСЕ переменные окружения, которые видит
процесс, а также проверяет наличие .env файлов в типичных местах.
Это нужно, чтобы понять, почему MIS_LOGIN / MIS_PASSWORD не подхватываются.
"""

import os
import time

print("=" * 60)
print("ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ПРОЦЕССА:")
print("=" * 60)
for key in sorted(os.environ.keys()):
    value = os.environ[key]
    if len(value) > 6:
        shown = value[:3] + "..." + value[-3:]
    else:
        shown = value
    print(f"  {key} = {shown}")

print()
print("=" * 60)
print("ПРОВЕРКА КОНКРЕТНО НУЖНЫХ ПЕРЕМЕННЫХ:")
print("=" * 60)
for name in ["MIS_LOGIN", "MIS_PASSWORD", "TG_BOT_TOKEN", "TOKEN", "TELEGRAM_BOT_TOKEN"]:
    val = os.environ.get(name)
    print(f"  {name}: {'НАЙДЕНА (' + str(len(val)) + ' симв.)' if val else 'НЕ НАЙДЕНА'}")

print()
print("=" * 60)
print("ПОИСК .env ФАЙЛОВ РЯДОМ:")
print("=" * 60)
candidates = [
    "/app/.env",
    "/app/data/.env",
    os.path.join(os.getcwd(), ".env"),
    "/.env",
]
for path in candidates:
    exists = os.path.isfile(path)
    print(f"  {path}: {'ЕСТЬ' if exists else 'нет'}")
    if exists:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            print(f"    Содержимое ({len(content)} симв.):")
            for line in content.splitlines():
                if "=" in line:
                    k, _, v = line.partition("=")
                    print(f"      {k}=***")
                else:
                    print(f"      {line}")
        except Exception as e:
            print(f"    Ошибка чтения: {e}")

print()
print("Текущая рабочая директория:", os.getcwd())
print("Содержимое /app (если доступно):")
try:
    print(" ", os.listdir("/app"))
except Exception as e:
    print("  ошибка:", e)

print()
print("Диагностика завершена. Процесс висит, чтобы bothost не считал его упавшим.")
while True:
    time.sleep(3600)
