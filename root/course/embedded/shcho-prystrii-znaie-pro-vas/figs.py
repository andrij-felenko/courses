# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми 'Що пристрій знає про вас'.
Запуск: python figs.py
Вивід: ./img/*.svg
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_flash_retention():
    """Фігура 1: Фрагментація Flash та залишкові дані при оновленні секретів у NVS/LittleFS."""
    w, h = 980, 520
    frags = []

    frags.append(rect(20, 45, 940, 455, fill="#fcfdfd", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(490, 72, "Фізичний сектор NOR Flash (4 КБ) під керуванням Log-Structured NVS / LittleFS", size=15, bold=True))

    # Колонка 1: Початковий стан (Запис v1)
    x1, y1, bw, bh = 45, 95, 275, 385
    frags.append(rect(x1, y1, bw, bh, fill="#f4f6f8", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(fitbox(x1 + 10, y1 + 10, bw - 20, 32, "Крок 1: Початковий стан", size=13, bold=True, fill="#e2e8f0", stroke="#64748b"))

    frags.append(fitbox(x1 + 15, y1 + 55, bw - 30, 65, "Сторінка 0 [Свіжий запис]\nСтатус: ВАЛІДНИЙ (0xFE)\nwifi_pass = \"AlphaPass2026\"", size=11, fill="#e8f8f0", stroke=FIELD))
    frags.append(fitbox(x1 + 15, y1 + 130, bw - 30, 65, "Сторінка 1 [Свіжий запис]\nСтатус: ВАЛІДНИЙ (0xFE)\ncloud_jwt = \"eyJhbGciOi...\"", size=11, fill="#e8f8f0", stroke=FIELD))
    frags.append(fitbox(x1 + 15, y1 + 205, bw - 30, 65, "Сторінка 2 [Свіжий запис]\nСтатус: ВАЛІДНИЙ (0xFE)\ngps_home = \"50.4501, 30.5234\"", size=11, fill="#e8f8f0", stroke=FIELD))
    frags.append(fitbox(x1 + 15, y1 + 280, bw - 30, 85, "Сторінки 3..15 [Чисті]\nСтатус: ВІЛЬНО (0xFF)\nФізичний стан: усі біти 1\nГотові до запису 1 → 0", size=11, fill="#ffffff", stroke="#cbd5e1"))

    # Колонка 2: Оновлення пароля та видалення токена
    x2 = 350
    frags.append(rect(x2, y1, bw, bh, fill="#f4f6f8", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(fitbox(x2 + 10, y1 + 10, bw - 20, 32, "Крок 2: Зміна пароля та «видалення»", size=13, bold=True, fill="#e2e8f0", stroke="#64748b"))

    frags.append(fitbox(x2 + 15, y1 + 55, bw - 30, 65, "Сторінка 0 [Стара версія]\nСтатус: ЗАСТАРІЛИЙ (0xFC)\nwifi_pass = \"AlphaPass2026\"", size=11, fill="#fee2e2", stroke=POS))
    frags.append(fitbox(x2 + 15, y1 + 130, bw - 30, 65, "Сторінка 1 [«Видалений» токен]\nСтатус: ВИДАЛЕНО (0xF8)\ncloud_jwt = \"eyJhbGciOi...\"", size=11, fill="#fee2e2", stroke=POS))
    frags.append(fitbox(x2 + 15, y1 + 205, bw - 30, 65, "Сторінка 2 [Незмінний]\nСтатус: ВАЛІДНИЙ (0xFE)\ngps_home = \"50.4501, 30.5234\"", size=11, fill="#e8f8f0", stroke=FIELD))
    frags.append(fitbox(x2 + 15, y1 + 280, bw - 30, 85, "Сторінка 3 [Нова версія]\nСтатус: ВАЛІДНИЙ (0xFE)\nwifi_pass = \"NewSecureKey99\"\nЗаписано у наступні комірки", size=11, fill="#e8f8f0", stroke=FIELD))

    frags.append(arrow(x1 + bw + 4, y1 + 180, x2 - 4, y1 + 180, color=LINE, sw=2))

    # Колонка 3: Дамп Flash програматором
    x3 = 655
    frags.append(rect(x3, y1, bw, bh, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=6))
    frags.append(fitbox(x3 + 10, y1 + 10, bw - 20, 32, "Крок 3: Дамп Flash програматором", size=13, bold=True, fill="#ffedd5", stroke="#ea580c", color="#9a3412"))

    frags.append(fitbox(x3 + 15, y1 + 55, bw - 30, 75, "Пряме читання SPI Flash (ROM Reader)\nЗчитано з комірок плаваючого затвора:\n→ Старий пароль: \"AlphaPass2026\"\n→ Повний JWT: \"eyJhbGciOi...\"", size=11, fill="#fee2e2", stroke=POS, bold=True))
    frags.append(fitbox(x3 + 15, y1 + 140, bw - 30, 65, "Координати бази та історія треків:\n→ gps_home = \"50.4501, 30.5234\"\n→ Логи маршруту за всі сесії", size=11, fill="#fee2e2", stroke=POS))
    frags.append(fitbox(x3 + 15, y1 + 215, bw - 30, 65, "Новий дійсний пароль:\n→ wifi_pass = \"NewSecureKey99\"\nНападник має всю історію змін!", size=11, fill="#fee2e2", stroke=POS))
    frags.append(fitbox(x3 + 15, y1 + 290, bw - 30, 75, "Підсумок:\n«Видалення» у файловій системі\nлише змінило біти заголовка,\nтіло секрету лишилося в кремнії!", size=11, fill="#ffffff", stroke="#ea580c", color="#7c2d12"))

    frags.append(arrow(x2 + bw + 4, y1 + 180, x3 - 4, y1 + 180, color=POS, sw=2))

    render(os.path.join(OUT_DIR, "flash-retention-fragmentation.svg"), w, h, *frags)


def fig_tamper_sensors():
    """Фігура 2: Багаторівневий захист корпусу та виявлення фізичного проникнення."""
    w, h = 980, 480
    frags = []

    frags.append(text(490, 28, "Апаратні сенсори анти-темпер моніторингу в захищеному корпусі", size=16, bold=True))

    # Зовнішній корпус пристрою
    frags.append(rect(30, 50, 920, 400, fill="#f8fafc", stroke="#334155", sw=2.5, rx=10))
    frags.append(text(120, 75, "Герметичний корпус виробу", size=12, bold=True, color="#475569"))

    # Сенсор 1: Верхня кришка з активною струмопровідною сіткою (Active Mesh)
    frags.append(rect(50, 95, 270, 160, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(fitbox(60, 105, 250, 30, "1. Активна струмопровідна сітка", size=12, bold=True, fill="#fee2e2", stroke=POS, color=POS))
    frags.append(fitbox(60, 145, 250, 95, "Звивиста мікродоріжка на кришці\nКонтроль опору містом Уїтстона\nСвердління / розрізання:\n→ Обірвання або закорочення\n→ Миттєва апаратна тривога", size=11, fill="#fef2f2", stroke="#fca5a5"))

    # Сенсор 2: Кінцевики розкриття (Tamper Switches)
    frags.append(rect(355, 95, 270, 160, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(fitbox(365, 105, 250, 30, "2. Кінцевики розкриття кришки", size=12, bold=True, fill="#e0e7ff", stroke=NEG, color=NEG))
    frags.append(fitbox(365, 145, 250, 95, "Позолочені мікроперемикачі\nПідпружинені ребрами кришки\nСтрумова петля із підтяжкою\nЗняття кришки / відкручування:\n→ Розмикання контактів за 50 мкс", size=11, fill="#eef2ff", stroke="#a5b4fc"))

    # Сенсор 3: Оптичний детектор у темній порожнині
    frags.append(rect(660, 95, 270, 160, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(fitbox(670, 105, 250, 30, "3. Оптичний сенсор у порожнині", size=12, bold=True, fill="#dcfce7", stroke=FIELD, color="#166534"))
    frags.append(fitbox(670, 145, 250, 95, "Фотодіод / фототранзистор на PCB\nПовна темрява у закритому боксі\nСтрум витоку: < 100 пА\nПоява світла (розкриття / щілина):\n→ Фотострум підриває компаратор", size=11, fill="#f0fdf4", stroke="#86efac"))

    # Центральний вузол: RTC / Backup SRAM / Battery Domain на платі
    frags.append(rect(180, 290, 620, 140, fill="#ffffff", stroke="#0f172a", sw=2, rx=8))
    frags.append(fitbox(200, 305, 580, 34, "Апаратний захищений домен МК (STM32 TAMP / ESP32 RTC Power Domain)", size=13, bold=True, fill="#f1f5f9", stroke="#334155"))
    frags.append(fitbox(200, 348, 280, 68, "Резервне живлення (VBAT):\nЛітієва таблетка або іоністор.\nСтеження за сенсорами 24/7\nпри струмі менше 1 мкА.", size=11, fill="#f8fafc", stroke="#94a3b8"))
    frags.append(fitbox(500, 348, 280, 68, "Регістри ключів (Backup SRAM):\nАпаратне самоочищення за 1 такт.\nПри тривозі живлення вимикається,\nключ розсіюється назавжди.", size=11, fill="#fee2e2", stroke=POS, bold=True))

    # Стрілки від сенсорів до домену
    frags.append(arrow(185, 257, 280, 288, color=POS, sw=2))
    frags.append(arrow(490, 257, 490, 288, color=NEG, sw=2))
    frags.append(arrow(795, 257, 700, 288, color=FIELD, sw=2))

    render(os.path.join(OUT_DIR, "anti-tamper-sensors-enclosure.svg"), w, h, *frags)


def fig_zeroization_cascade():
    """Фігура 3: Часовий каскад гарантованого стирання Zeroization."""
    w, h = 980, 520
    frags = []

    frags.append(text(490, 28, "Хронологія та каскад гарантованого знешкодження (Zeroization Cascade)", size=16, bold=True))

    # Горизонтальна часова шкала
    frags.append(line(50, 75, 910, 75, color="#475569", sw=3))
    frags.append(arrow(890, 75, 940, 75, color="#475569", sw=3))
    frags.append(text(915, 60, "Час (t)", size=12, bold=True, color="#475569", anchor="middle"))

    # Подія 0: Тригер тривоги
    frags.append(circle(70, 75, 8, fill=POS, stroke="#991b1b", sw=2))
    frags.append(text(70, 55, "t = 0", size=12, bold=True, color=POS))
    frags.append(fitbox(20, 95, 130, 60, "Спрацювання\nсенсора тампера\n(Mesh / Pin / Light)", size=11, bold=True, fill="#fee2e2", stroke=POS))

    # Рівень 1: Апаратне знищення ключів (Hardware TAMP Wipe)
    frags.append(circle(230, 75, 8, fill=POS, stroke="#991b1b", sw=2))
    frags.append(text(230, 55, "t < 100 нс", size=12, bold=True, color=POS))
    frags.append(fitbox(165, 95, 175, 140, "Рівень 1: Апаратний Wipe\n- Скидання Backup SRAM\n- Розмикання ключа VBAT\n- Майстер-ключ знищено!\n\nКриптографічне стирання:\nувесь Flash миттєво стає\nнерозшифровним сміттям.", size=11, fill="#fee2e2", stroke=POS))

    # Рівень 2: Очищення RAM ядра та деструктори
    frags.append(circle(440, 75, 8, fill=NEG, stroke="#1e40af", sw=2))
    frags.append(text(440, 55, "t ≈ 50 мкс", size=12, bold=True, color=NEG))
    frags.append(fitbox(360, 95, 175, 140, "Рівень 2: Затирання RAM\n- NMI / Tamper ISR\n- explicit_bzero() стеків\n- Очищення буферів mbedTLS\n- Скидання регістрів R0-R12\n\nЗахист від оптимізацій\nкомпілятора (Dead Store).", size=11, fill="#e0e7ff", stroke=NEG))

    # Рівень 3: Фізичне стирання Flash
    frags.append(circle(650, 75, 8, fill=FIELD, stroke="#166534", sw=2))
    frags.append(text(650, 55, "t ≈ 50 мс", size=12, bold=True, color=FIELD))
    frags.append(fitbox(565, 95, 185, 140, "Рівень 3: Затирання Flash\n- Chip Erase (0xC7 / 0x60)\n- Перезапис секторів 0x00\n- Знищення таблиць файлів\n- Скидання журналу NVS\n\nФізичне перезаряджання\nплаваючих затворів NOR.", size=11, fill="#dcfce7", stroke=FIELD))

    # Рівень 4: Незворотне перетворення на «цеглину» (Permanent Brick)
    frags.append(circle(855, 75, 8, fill="#475569", stroke="#0f172a", sw=2))
    frags.append(text(855, 55, "t ≈ 200 мс", size=12, bold=True, color="#0f172a"))
    frags.append(fitbox(770, 95, 180, 140, "Рівень 4: Спалювання eFuse\n- Спалювання бітів JTAG/SWD\n- Постійне блокування наладки\n- Security Level 3 / Permanent\n\nЧип назавжди ізольовано:\nнавіть на заводі його не можна\nперепрошити чи прочитати.", size=11, fill="#f1f5f9", stroke="#334155"))

    # Нижня узагальнююча панель
    frags.append(rect(40, 260, 900, 235, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 285, "Принцип ешелонованого знищення секретів (Crypto-Shredding First)", size=14, bold=True))

    frags.append(fitbox(60, 305, 410, 170, "Чому знищення ключа за 100 нс вирішує все:\n\nЯкщо нападник встигне висмикнути живлення\nчерез 5 мс після розкриття корпусу, Flash\nне встигне затертися. Але якщо Flash було\nзашифровано, а ключ із Backup SRAM зник\nза 100 нс — збережений дамп пам'яті лишається\nматематично нерозшифровним білим шумом.", size=11, fill="#ffffff", stroke="#94a3b8"))

    frags.append(fitbox(500, 305, 420, 170, "Чому обов'язкові наступні рівні:\n\nЯкщо частина Flash лишалася відкритою\n(відкритий завантажувач або конфігурація Wi-Fi),\nподальші кроки (RAM Scrubbing, Sector Erase,\neFuse Blow) гарантовано затирають відкриті\nбайти та назавжди блокують апаратні інтерфейси\nчипа від зворотного інжинірингу.", size=11, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT_DIR, "zeroization-cascade.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_flash_retention()
    fig_tamper_sensors()
    fig_zeroization_cascade()
    print("Всі фігури згенеровано успішно.")
