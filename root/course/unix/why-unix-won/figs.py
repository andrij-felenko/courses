#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми why-unix-won."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_narrow_waist():
    """Ілюстрація принципу вузького пояса (narrow waist) та моделі пісочного годинника."""
    w, h = 860, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Модель «пісочного годинника»: чому універсальний вузький пояс перемагає", size=16, bold=True))

    # Ліва колонка: Багатотипна система (N x M зв'язків)
    frags.append(rect(30, 55, 370, 400, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(215, 82, "Складна система з типізованими підсистемами", size=13, color=POS, bold=True))
    frags.append(text(215, 100, "(OS/360, VMS, CORBA-моделі: N × M зв'язків)", size=11, color=MUTED, italic=True))

    # Програми зліва
    apps_l = ["Текстовий редактор", "СКБД / База даних", "Служба журналів", "Утиліта аналізу"]
    for i, app in enumerate(apps_l):
        y = 135 + i * 40
        b, _, _ = textbox(115, y, app, size=11, pad=6, fill="#f8fafc", stroke="#64748b", min_w=140)
        frags.append(b)

    # Джерела зліва
    devs_l = ["Блоковий диск", "Стрічковий накопичувач", "Термінал / TTY", "Мережевий потік"]
    for i, dev in enumerate(devs_l):
        y = 310 + i * 36
        b, _, _ = textbox(115, y, dev, size=11, pad=6, fill="#f8fafc", stroke="#64748b", min_w=140)
        frags.append(b)

    # Плутанина зв'язків і конвертерів посередині лівого блоку
    frags.append(rect(205, 125, 180, 160, fill="#fff1f2", stroke="#fda4af", sw=1.2, rx=6))
    frags.append(text(295, 150, "Окремі методи доступу:", size=11, color=POS, bold=True))
    frags.append(text(295, 172, "• DCB / Record format", size=10, color=INK))
    frags.append(text(295, 192, "• ISAM / VSAM індекси", size=10, color=INK))
    frags.append(text(295, 212, "• Специфічні RPC-схеми", size=10, color=INK))
    frags.append(text(295, 232, "• Власні драйверні API", size=10, color=INK))
    frags.append(text(295, 262, "Кожен новий тип ламає код!", size=10, color=POS, italic=True))

    # Стрілки зліва (багато зв'язків)
    for y1 in [135, 175, 215, 255]:
        frags.append(line(185, y1, 205, 190, color="#94a3b8", sw=1.2))
    for y2 in [310, 346, 382, 418]:
        frags.append(line(295, 285, 185, y2, color="#94a3b8", sw=1.2))

    frags.append(text(215, 442, "Складність зростає квадратично: N програм × M пристроїв", size=11, color=POS, bold=True))

    # Права колонка: Модель Unix (Вузький пояс, N + M зв'язків)
    frags.append(rect(450, 55, 380, 400, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(640, 82, "Модель Unix / Linux: «Вузький пояс»", size=13, color=FIELD, bold=True))
    frags.append(text(640, 100, "(Універсальний потік байтів: N + M зв'язків)", size=11, color=MUTED, italic=True))

    # Верхній шар: Довільні програми
    apps_r = ["grep / sort / awk", "Веб-сервер / API", "Контейнер / Daemon", "Будь-яка нова програма"]
    for i, app in enumerate(apps_r):
        x = 475 + (i % 2) * 175
        y = 135 + (i // 2) * 38
        b, _, _ = textbox(x + 75, y, app, size=11, pad=6, fill="#f0fdf4", stroke=FIELD, min_w=155)
        frags.append(b)

    # Стрілки вниз до пояса
    frags.append(arrow(550, 188, 590, 220, color=FIELD, sw=1.6))
    frags.append(arrow(725, 188, 680, 220, color=FIELD, sw=1.6))

    # ВУЗЬКИЙ ПОЯС (The Narrow Waist)
    frags.append(rect(490, 225, 300, 75, fill="#e0f2fe", stroke=NEG, sw=2, rx=6))
    frags.append(text(640, 248, "ВУЗЬКИЙ ПОЯС ІНТЕРФЕЙСУ", size=12, color=NEG, bold=True))
    frags.append(text(640, 268, "Потік байтів без схеми · Дескриптор (int)", size=11, color=INK, bold=True))
    frags.append(text(640, 286, "open() · read() · write() · close() · pipe()", size=11, color="#1e3a8a"))

    # Стрілки від пояса вниз
    frags.append(arrow(590, 300, 550, 335, color=FIELD, sw=1.6))
    frags.append(arrow(680, 300, 725, 335, color=FIELD, sw=1.6))

    # Нижній шар: Довільні джерела та пристрої
    devs_r = ["NVMe / SSD / Файли", "TCP/IP сокети", "TTY / USB-порти", "Псевдо-ФС (/proc, /sys)"]
    for i, dev in enumerate(devs_r):
        x = 475 + (i % 2) * 175
        y = 345 + (i // 2) * 38
        b, _, _ = textbox(x + 75, y, dev, size=11, pad=6, fill="#eff6ff", stroke=NEG, min_w=155)
        frags.append(b)

    frags.append(text(640, 442, "Складність зростає лінійно: N програм + M джерел", size=11, color=FIELD, bold=True))

    out_path = os.path.join(OUT_DIR, "narrow-waist-evolution.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_worse_is_better():
    """Порівняння підходів 'The Right Thing' (Multics/MIT) та 'Worse is Better' (Unix/NJ)."""
    w, h = 860, 450
    frags = []

    frags.append(text(w / 2, 28, "«Гірше — це краще»: еволюційний вибір простоти над повнотою", size=16, bold=True))

    # Таблиця порівняння з 4 критеріїв Річарда Ґебріела
    col_w = [160, 320, 320]
    x_starts = [30, 200, 530]

    # Шапка таблиці
    frags.append(rect(x_starts[0], 55, col_w[0], 40, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4))
    frags.append(text(x_starts[0] + col_w[0] / 2, 80, "Критерій", size=12, bold=True))

    frags.append(rect(x_starts[1], 55, col_w[1], 40, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=4))
    frags.append(text(x_starts[1] + col_w[1] / 2, 73, "«Правильний шлях» (MIT / Multics)", size=12, color=POS, bold=True))
    frags.append(text(x_starts[1] + col_w[1] / 2, 88, "Теоретична досконалість і чистота", size=10, color=MUTED, italic=True))

    frags.append(rect(x_starts[2], 55, col_w[2], 40, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=4))
    frags.append(text(x_starts[2] + col_w[2] / 2, 73, "«Гірше — це краще» (Unix / New Jersey)", size=12, color=FIELD, bold=True))
    frags.append(text(x_starts[2] + col_w[2] / 2, 88, "Простота реалізації та виживання", size=10, color=MUTED, italic=True))

    rows_data = [
        ("Простота\n(Simplicity)",
         "Інтерфейс мусить бути простим для\nкористувача, навіть якщо реалізація\nвсередині ядра буде надскладною.",
         "Простота РЕАЛІЗАЦІЇ ядра — понад усе.\nІнтерфейс може бути грубим, а роботу\n(повтор циклу, перевірки) перекладено нагору.",
         "#fef2f2", "#f0fdf4"),
        ("Коректність\n(Correctness)",
         "Абсолютна в усіх аспектах. Некоректність\nчи часткове виконання категорично\nзаборонені архітектурою.",
         "Коректність бажана, але простота важливіша.\nЯдро може повернути помилку або частину\nбайтів (short read), знявши із себе клопіт.",
         "#fef2f2", "#f0fdf4"),
        ("Узгодженість\n(Consistency)",
         "Повна однорідність концепцій. Жодних\nвинятків чи аварійних виходів; уся\nсистема розмовляє однією мовою.",
         "Добра, але допускаються компроміси.\nЯкщо уніфікація ускладнює ядро — додають\nioctl або простий прапорець.",
         "#fef2f2", "#f0fdf4"),
        ("Повнота\n(Completeness)",
         "Система мусить покривати 100% відомих\nі можливих крайових ситуацій наперед.",
         "Покрити ~80% типових випадків просто.\nРідкісні крайові випадки віддають на відкуп\nкористувацькому простору.",
         "#fef2f2", "#f0fdf4"),
    ]

    y_cur = 102
    for crit, mit, nj, f_mit, f_nj in rows_data:
        h_row = 70
        frags.append(rect(x_starts[0], y_cur, col_w[0], h_row, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
        frags.append(mtext(x_starts[0] + col_w[0] / 2, y_cur + 28, crit, size=11, bold=True))

        frags.append(rect(x_starts[1], y_cur, col_w[1], h_row, fill=f_mit, stroke="#fca5a5", sw=1.2, rx=4))
        frags.append(mtext(x_starts[1] + 12, y_cur + 20, mit, size=10.5, anchor="start", color=INK))

        frags.append(rect(x_starts[2], y_cur, col_w[2], h_row, fill=f_nj, stroke="#86efac", sw=1.2, rx=4))
        frags.append(mtext(x_starts[2] + 12, y_cur + 20, nj, size=10.5, anchor="start", color=INK))

        y_cur += h_row + 6

    # Підсумок знизу
    frags.append(rect(30, 408, 820, 32, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(w / 2, 428, "Результат: «Правильний шхід» гине від складності та ваги; «Гірше — це краще» легко портується і захоплює світ.", size=11, color="#0f172a", bold=True))

    out_path = os.path.join(OUT_DIR, "worse-is-better-matrix.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_mechanism_vs_policy():
    """Ілюстрація поділу механізму та політики між ядром і простором користувача."""
    w, h = 860, 450
    frags = []

    frags.append(text(w / 2, 28, "Поділ механізму й політики: чому ядро не знає правил застосування", size=16, bold=True))

    # Верхній блок: Простір користувача (ПОЛІТИКА)
    frags.append(rect(40, 55, 780, 160, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(430, 80, "ПРОСТІР КОРИСТУВАЧА — ПОЛІТИКА (ЩО і НАВІЩО робити)", size=13, color=FIELD, bold=True))
    frags.append(text(430, 98, "Політики легко змінюються, замінюються й пишуться під кожну задачу наново", size=11, color=MUTED, italic=True))

    policies = [
        ("Оболонка (Shell)", "Вирішує, як з'єднати\nпрограми в конвеєр\n(|, >, <, pipefail)"),
        ("systemd / init", "Вирішує, у якому\nпорядку й за якими\nумовами запускати служби"),
        ("Контейнерний рушій", "Вирішує, які ресурси\nі простори імен виділити\nпід мікросервіс"),
        ("Веб-сервер / База", "Вирішує, як розбирати\nбайти, кешувати дані\nй формувати відповіді"),
    ]

    for i, (title, desc) in enumerate(policies):
        x = 60 + i * 188
        frags.append(rect(x, 115, 175, 85, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
        frags.append(text(x + 87, 134, title, size=11, color=FIELD, bold=True))
        frags.append(mtext(x + 87, 153, desc, size=9.5, color=INK))

    # Розділювальна межа: Системні виклики
    frags.append(rect(220, 226, 420, 32, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(430, 247, "МЕЖА СИСТЕМНИХ ВИКЛИКІВ (Syscalls ABI)", size=12, color="#1e293b", bold=True))

    frags.append(arrow(300, 215, 300, 226, color="#475569", sw=2))
    frags.append(arrow(560, 215, 560, 226, color="#475569", sw=2))
    frags.append(arrow(300, 258, 300, 270, color="#475569", sw=2))
    frags.append(arrow(560, 258, 560, 270, color="#475569", sw=2))

    # Нижній блок: Ядро (МЕХАНІЗМ)
    frags.append(rect(40, 272, 780, 160, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(430, 297, "ЯДРО ОПЕРАЦІЙНОЇ СИСТЕМИ — МЕХАНІЗМ (ЯК технічно виконати дію)", size=13, color=NEG, bold=True))
    frags.append(text(430, 315, "Нічого не знає про мету користувача; надає мінімальні примітиви", size=11, color=MUTED, italic=True))

    mechanisms = [
        ("fork() та execve()", "Клонувати процес та\nзамінити образ коду.\nНе знає, ХТО запускається."),
        ("pipe() та VFS", "Передати байти між деск-\nрипторами. Не знає,\nЯКИЙ формат у байтів."),
        ("cgroups & namespaces", "Ізолювати таблиці та\nобмежити CPU/RAM.\nНе знає про «контейнери»."),
        ("Планувальник & MMU", "Виділити сторінки пам'яті\nй віддати квант часу.\nНе знає логіки програми."),
    ]

    for i, (title, desc) in enumerate(mechanisms):
        x = 60 + i * 188
        frags.append(rect(x, 332, 175, 85, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
        frags.append(text(x + 87, 351, title, size=11, color=NEG, bold=True))
        frags.append(mtext(x + 87, 370, desc, size=9.5, color=INK))

    out_path = os.path.join(OUT_DIR, "mechanism-vs-policy.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_narrow_waist()
    fig_worse_is_better()
    fig_mechanism_vs_policy()
