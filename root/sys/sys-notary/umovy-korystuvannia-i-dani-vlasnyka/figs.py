#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми: Умови користування й дані власника: що збираємо, навіщо, як відмовитися."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від кореня теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_gdpr_iot_data_pipeline():
    """Архітектура конвеєра обробки телеметрії та захисту приватності на вбудованому пристрої."""
    w, h = 980, 480
    frags = []

    # Заголовок / фонова сітка
    frags.append(rect(15, 15, 950, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Секція 1: Джерела сирих даних на пристрої (Зліва)
    s1_x, s1_y, s1_w, s1_h = 35, 45, 210, 395
    frags.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    frags.append(text(s1_x + s1_w / 2, s1_y + 26, "Джерела сирих даних", size=14, color=NEG, bold=True))
    frags.append(line(s1_x + 12, s1_y + 40, s1_x + s1_w - 12, s1_y + 40, color=NEG, sw=1))

    sources = [
        ("Технічна діагностика", ["Напруга Vdd, частота CPU", "Використання Heap / стек", "Flash write cycles, скидання", "Дампи помилок / панік"]),
        ("Контекстні дані / PII", ["MAC-адреси, серійний номер", "BSSID сканування Wi-Fi", "Координати GNSS (широта/довгота)", "Логи дій користувача"])
    ]

    curr_y = s1_y + 60
    for grp_title, items in sources:
        frags.append(text(s1_x + 14, curr_y, grp_title, size=12, color=INK, bold=True, anchor="start"))
        curr_y += 18
        for itm in items:
            frags.append(text(s1_x + 22, curr_y, "• " + itm, size=10.5, color=MUTED, anchor="start"))
            curr_y += 18
        curr_y += 12

    # Стрілка 1 -> 2
    frags.append(arrow(s1_x + s1_w, 240, s1_x + s1_w + 35, 240, color=LINE, sw=2))

    # Секція 2: Класифікатор і перевірка згоди (Центр-ліво)
    s2_x, s2_y, s2_w, s2_h = 285, 45, 220, 395
    frags.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#fdfbf7", stroke="#d97706", sw=2, rx=8))
    frags.append(text(s2_x + s2_w / 2, s2_y + 26, "Класифікатор і політика", size=14, color="#b45309", bold=True))
    frags.append(line(s2_x + 12, s2_y + 40, s2_x + s2_w - 12, s2_y + 40, color="#d97706", sw=1))

    c_items = [
        "1. Категоризація полів:",
        " • Технічні: Art. 6(1)(f) GDPR",
        " • Функціональні: Opt-in (Рівень 2)",
        " • Персональні (PII): Opt-in (Рівень 3)",
        "",
        "2. Перевірка NVS Consent:",
        " • Читання бітової маски дозволів",
        " • Валідація версії політики",
        " • Відкидання заблокованих полів",
        "",
        "3. Реагування на Opt-Out:",
        " • Миттєве скидання буферів черг"
    ]
    for i, itm in enumerate(c_items):
        bold = (i in [0, 5, 9])
        col = INK if not bold else ("#b45309" if bold else INK)
        frags.append(text(s2_x + 14, s2_y + 65 + i * 21, itm, size=11, color=col, bold=bold, anchor="start"))

    # Стрілка 2 -> 3
    frags.append(arrow(s2_x + s2_w, 240, s2_x + s2_w + 35, 240, color=LINE, sw=2))

    # Секція 3: Модуль анонімізації та фільтрації (Центр-право)
    s3_x, s3_y, s3_w, s3_h = 545, 45, 220, 395
    frags.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(s3_x + s3_w / 2, s3_y + 26, "Privacy Guard (Анонімізація)", size=14, color=FIELD, bold=True))
    frags.append(line(s3_x + 12, s3_y + 40, s3_x + s3_w - 12, s3_y + 40, color=FIELD, sw=1))

    p_items = [
        "1. Огрублення координат:",
        " • GNSS округлення: 0.01° (~1.1 км)",
        "",
        "2. Псевдонімізація MAC/ID:",
        " • HMAC-SHA256(UID, Ephemeral Salt)",
        " • Видалення BSSID-списків мереж",
        "",
        "3. Агрегація метрик на Edge:",
        " • Квантування та гістограми",
        " • Шумування (Differential Privacy)",
        "",
        "4. Захист пам'яті (Crypto-Shred):",
        " • Знищення ключів NVS при Erasure"
    ]
    for i, itm in enumerate(p_items):
        bold = (i in [0, 3, 6, 9])
        col = INK if not bold else (FIELD if bold else INK)
        frags.append(text(s3_x + 14, s3_y + 65 + i * 21, itm, size=11, color=col, bold=bold, anchor="start"))

    # Стрілка 3 -> 4
    frags.append(arrow(s3_x + s3_w, 240, s3_x + s3_w + 35, 240, color=LINE, sw=2))

    # Секція 4: Захищена передача та хмара (Справа)
    s4_x, s4_y, s4_w, s4_h = 805, 45, 140, 395
    frags.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#fdf2f8", stroke=POS, sw=2, rx=8))
    frags.append(text(s4_x + s4_w / 2, s4_y + 26, "Експорт", size=14, color=POS, bold=True))
    frags.append(line(s4_x + 10, s4_y + 40, s4_x + s4_w - 10, s4_y + 40, color=POS, sw=1))

    out_items = [
        "TLS 1.3 / mTLS",
        "Cert Pinning",
        "Очищений",
        "CBOR / JSON",
        "пакет",
        "---",
        "Cloud Ingest",
        "API без PII",
        "---",
        "Zero Raw Log",
        "на UART/SWD"
    ]
    for i, itm in enumerate(out_items):
        bold = (i in [0, 6, 9])
        col = INK if not bold else (POS if bold else INK)
        frags.append(text(s4_x + s4_w / 2, s4_y + 70 + i * 24, itm, size=11, color=col, bold=bold, anchor="middle"))

    path = os.path.join(OUT_DIR, "gdpr-iot-data-pipeline.svg")
    render(path, w, h, *frags, title="Конвеєр обробки телеметрії та захисту приватності на вбудованому пристрої")
    print(f"Згенеровано: {path}")


def fig_consent_level_state_machine():
    """Скінченний автомат рівнів користувацької згоди та механізм відкликання / забуття."""
    w, h = 960, 470
    frags = []

    frags.append(rect(15, 15, 930, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Стан 0: STATE_UNCONFIGURED (Фабричний дефолт)
    s0_x, s0_y, s0_w, s0_h = 40, 50, 240, 110
    frags.append(rect(s0_x, s0_y, s0_w, s0_h, fill="#f1f5f9", stroke="#475569", sw=2, rx=8))
    frags.append(text(s0_x + s0_w / 2, s0_y + 24, "Рівень 0: За замовчуванням", size=13, color="#1e293b", bold=True))
    frags.append(text(s0_x + s0_w / 2, s0_y + 44, "STATE_UNCONFIGURED / OFFLINE", size=10.5, color=MUTED))
    frags.append(text(s0_x + s0_w / 2, s0_y + 68, "Повна заборона телеметрії.", size=11, color=INK))
    frags.append(text(s0_x + s0_w / 2, s0_y + 88, "Тільки локальні базові функції.", size=11, color=INK))

    # Стан 1: STATE_LEVEL_1_DIAGNOSTICS (Технічна діагностика)
    s1_x, s1_y, s1_w, s1_h = 360, 50, 240, 110
    frags.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(s1_x + s1_w / 2, s1_y + 24, "Рівень 1: Діагностика", size=13, color=NEG, bold=True))
    frags.append(text(s1_x + s1_w / 2, s1_y + 44, "STATE_LEVEL_1_DIAGNOSTICS", size=10.5, color=MUTED))
    frags.append(text(s1_x + s1_w / 2, s1_y + 68, "Законний інтерес (Art. 6(1)(f)).", size=11, color=INK))
    frags.append(text(s1_x + s1_w / 2, s1_y + 88, "Паніки, Vdd, помилки без PII/IP.", size=11, color=INK))

    # Стан 2: STATE_LEVEL_2_ANALYTICS (Функціональна аналітика)
    s2_x, s2_y, s2_w, s2_h = 680, 50, 240, 110
    frags.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#fefce8", stroke="#ca8a04", sw=2, rx=8))
    frags.append(text(s2_x + s2_w / 2, s2_y + 24, "Рівень 2: Аналітика (Opt-in)", size=13, color="#a16207", bold=True))
    frags.append(text(s2_x + s2_w / 2, s2_y + 44, "STATE_LEVEL_2_ANALYTICS", size=10.5, color=MUTED))
    frags.append(text(s2_x + s2_w / 2, s2_y + 68, "Агреговані метрики використання.", size=11, color=INK))
    frags.append(text(s2_x + s2_w / 2, s2_y + 88, "Огрублені координати, хешований ID.", size=11, color=INK))

    # Стан 3: STATE_LEVEL_3_PERSONALISED (Хмарна синхронізація / Персональні дані)
    s3_x, s3_y, s3_w, s3_h = 680, 280, 240, 110
    frags.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(s3_x + s3_w / 2, s3_y + 24, "Рівень 3: Повна згода (Opt-in)", size=13, color=FIELD, bold=True))
    frags.append(text(s3_x + s3_w / 2, s3_y + 44, "STATE_LEVEL_3_PERSONALISED", size=10.5, color=MUTED))
    frags.append(text(s3_x + s3_w / 2, s3_y + 68, "Хмарна телеметрія, профілі.", size=11, color=INK))
    frags.append(text(s3_x + s3_w / 2, s3_y + 88, "Точна телеметрія прив'язана до акаунта.", size=11, color=INK))

    # Стан 4: STATE_OPT_OUT_REVOCATION (Скидання згоди / Відкликання)
    s4_x, s4_y, s4_w, s4_h = 360, 280, 240, 110
    frags.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#fff1f2", stroke=POS, sw=2, rx=8))
    frags.append(text(s4_x + s4_w / 2, s4_y + 24, "Відкликання: Opt-Out", size=13, color=POS, bold=True))
    frags.append(text(s4_x + s4_w / 2, s4_y + 44, "STATE_OPT_OUT_PENDING", size=10.5, color=MUTED))
    frags.append(text(s4_x + s4_w / 2, s4_y + 68, "Очищення черг RAM і буферів Flash.", size=11, color=INK))
    frags.append(text(s4_x + s4_w / 2, s4_y + 88, "Миттєве блокування відправки PII.", size=11, color=INK))

    # Стан 5: STATE_RIGHT_TO_ERASURE (Право на забуття / Crypto-Shredding)
    s5_x, s5_y, s5_w, s5_h = 40, 280, 240, 110
    frags.append(rect(s5_x, s5_y, s5_w, s5_h, fill="#fdf4ff", stroke="#9333ea", sw=2, rx=8))
    frags.append(text(s5_x + s5_w / 2, s5_y + 24, "Право на забуття (Art. 17)", size=13, color="#7e22ce", bold=True))
    frags.append(text(s5_x + s5_w / 2, s5_y + 44, "STATE_RIGHT_TO_ERASURE", size=10.5, color=MUTED))
    frags.append(text(s5_x + s5_w / 2, s5_y + 68, "Crypto-shredding ключів шифрування.", size=11, color=INK))
    frags.append(text(s5_x + s5_w / 2, s5_y + 88, "Повне стирання NVS і відв'язка UID.", size=11, color=INK))

    # Переходи (Стрілки)
    # 0 -> 1: Активація базової діагностики
    frags.append(arrow(s0_x + s0_w, 95, s1_x, 95, color=LINE, sw=1.8))
    frags.append(text((s0_x + s0_w + s1_x) / 2, 85, "Активація", size=10.5, color=LINE, bold=True))

    # 1 -> 2: Надання згоди на аналітику (Opt-in)
    frags.append(arrow(s1_x + s1_w, 95, s2_x, 95, color=LINE, sw=1.8))
    frags.append(text((s1_x + s1_w + s2_x) / 2, 85, "Opt-in Consent", size=10.5, color=LINE, bold=True))

    # 2 -> 3: Розширення згоди на хмару
    frags.append(arrow(s2_x + s2_w / 2, s2_y + s2_h, s3_x + s3_w / 2, s3_y, color=LINE, sw=1.8))
    frags.append(text(s2_x + s2_w / 2 + 55, (s2_y + s2_h + s3_y) / 2, "Хмарна згода", size=10.5, color=LINE, bold=True))

    # 3 -> 4 або 2 -> 4: Відкликання згоди (Opt-out)
    frags.append(arrow(s3_x, 335, s4_x + s4_w, 335, color=POS, sw=1.8))
    frags.append(text((s3_x + s4_x + s4_w) / 2, 325, "Opt-Out (Відкликання)", size=10.5, color=POS, bold=True))

    # 4 -> 1: Повернення до базової діагностики після очищення
    frags.append(arrow(s4_x + s4_w / 2, s4_y, s1_x + s1_w / 2, s1_y + s1_h, color=NEG, sw=1.8))
    frags.append(text(s4_x + s4_w / 2 - 50, (s4_y + s1_y + s1_h) / 2, "Очищено -> Рівень 1", size=10.5, color=NEG, bold=True))

    # 4 -> 5 або 1 -> 5: Команда повного видалення даних
    frags.append(arrow(s4_x, 335, s5_x + s5_w, 335, color="#7e22ce", sw=1.8))
    frags.append(text((s4_x + s5_x + s5_w) / 2, 325, "Команда стирання", size=10.5, color="#7e22ce", bold=True))

    # 5 -> 0: Завершення стирання, повернення до фабричного стану
    frags.append(arrow(s5_x + s5_w / 2, s5_y, s0_x + s0_w / 2, s0_y + s0_h, color="#475569", sw=1.8))
    frags.append(text(s5_x + s5_w / 2 - 55, (s5_y + s0_y + s0_h) / 2, "Заводський стан", size=10.5, color="#475569", bold=True))

    path = os.path.join(OUT_DIR, "consent-level-state-machine.svg")
    render(path, w, h, *frags, title="Скінченний автомат рівнів користувацької згоди та механізм відкликання")
    print(f"Згенеровано: {path}")


if __name__ == '__main__':
    fig_gdpr_iot_data_pipeline()
    fig_consent_level_state_machine()
