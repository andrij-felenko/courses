#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схем для теми «Терміновий випуск: коротка дорога, яку готують заздалегідь»."""

import os
import sys

# Підключаємо svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_fast_track_vs_full_pipeline():
    """Порівняння повного релізного циклу та екстреного fast-track конвеєра."""
    w, h = 980, 520
    frags = []

    # Заголовок секції 1: Повний регулярний конвеєр
    frags.append(rect(20, 40, 940, 210, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(40, 68, "Регулярний плановий випуск (тривалість: 1–3 тижні)", size=15, color=INK, anchor="start", bold=True))
    frags.append(text(40, 88, "Мета: випуск нового функціоналу, планова стабілізація, повне вичерпне покриття", size=12, color=MUTED, anchor="start"))

    # Блоки регулярного конвеєра
    stages_reg = [
        ("Гілка develop\n(усі нові фічі)", 120, 150, 160, 54, FILL, LINE),
        ("Повна збірка\n(усі конфігурації)", 310, 150, 160, 54, FILL, LINE),
        ("Повний HIL-регрес\n(72 год, кліматика)", 500, 150, 160, 54, "#fcf3cf", "#b7950b"),
        ("Ручний аудит\nі погодження", 690, 150, 160, 54, FILL, LINE),
        ("Планова черга\nпідпису HSM", 870, 150, 140, 54, FILL, LINE),
    ]

    for label, cx, cy, bw, bh, f_col, s_col in stages_reg:
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, label, size=13, fill=f_col, stroke=s_col, bold=True))

    # Стрілки між регулярними блоками
    frags.append(arrow(200, 150, 222, 150, color=LINE, sw=1.5))
    frags.append(arrow(390, 150, 412, 150, color=LINE, sw=1.5))
    frags.append(arrow(580, 150, 602, 150, color=LINE, sw=1.5))
    frags.append(arrow(770, 150, 792, 150, color=LINE, sw=1.5))

    # Заголовок секції 2: Екстрений fast-track конвеєр
    frags.append(rect(20, 275, 940, 225, fill="#f4faf6", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(40, 303, "Екстрений fast-track випуск (тривалість: 1–4 години)", size=15, color=FIELD, anchor="start", bold=True))
    frags.append(text(40, 323, "Мета: ліквідація критичної 0-day дірки, мінімальний дифф, ізольована перевірка, терміновий підпис", size=12, color=INK, anchor="start"))

    # Блоки екстреного конвеєра
    stages_fast = [
        ("Тег prod-релізу\nv2.4.0 (hotfix branch)", 120, 395, 160, 56, "#ebf5fb", "#2980b9"),
        ("Атомарний патч\n(тільки дефект)", 310, 395, 160, 56, "#ebf5fb", "#2980b9"),
        ("Цільовий Sanity HIL\n(smoke, живлення, OTA)", 500, 395, 160, 56, "#d5f5e3", FIELD),
        ("Екстрений HSM підпис\n(dual-authorization)", 690, 395, 160, 56, "#fadbd8", POS),
        ("Канарковий rollout\n1% → 10% → 100%", 870, 395, 140, 56, "#d5f5e3", FIELD),
    ]

    for label, cx, cy, bw, bh, f_col, s_col in stages_fast:
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, label, size=13, fill=f_col, stroke=s_col, bold=True))

    # Стрілки між екстреними блоками
    frags.append(arrow(200, 395, 222, 395, color=FIELD, sw=1.8))
    frags.append(arrow(390, 395, 412, 395, color=FIELD, sw=1.8))
    frags.append(arrow(580, 395, 602, 395, color=FIELD, sw=1.8))
    frags.append(arrow(770, 395, 792, 395, color=FIELD, sw=1.8))

    # Нижня анотація
    frags.append(text(490, 480, "Ключова різниця: скорочення досягається звуженням диффу й фокусом тестів, а не відмовою від гарантій", size=12, color=INK, bold=True))

    render(os.path.join(OUT_DIR, "fast-track-vs-full-pipeline.svg"), w, h, *frags)


def fig_hotfix_branching_and_rollback():
    """Топологія гілкування для hotfix та механізм захисту від відкату (anti-rollback counter)."""
    w, h = 980, 460
    frags = []

    # Верхня частина: Git гілкування
    frags.append(rect(20, 20, 940, 210, fill=FILL, stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(40, 48, "Ізоляція гілки: походження від підтвердженого тегу експлуатації", size=15, color=INK, anchor="start", bold=True))

    # Лінія main / develop
    frags.append(line(70, 95, 910, 95, color=MUTED, sw=2, dash="4,4"))
    frags.append(text(80, 85, "Гілка develop / main (нестабільні зміни наступної версії)", size=11, color=MUTED, anchor="start"))

    # Вузли main
    frags.append(circle(200, 95, 9, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(text(200, 118, "v2.4.0", size=11, color=INK, bold=True))

    frags.append(circle(400, 95, 9, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(text(400, 118, "feat: A", size=10, color=MUTED))

    frags.append(circle(600, 95, 9, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(text(600, 118, "feat: B", size=10, color=MUTED))

    frags.append(circle(800, 95, 9, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(text(800, 118, "merge hotfix", size=10, color=FIELD, bold=True))

    # Гілка Hotfix
    frags.append(line(200, 95, 290, 165, color=FIELD, sw=2))
    frags.append(line(290, 165, 680, 165, color=FIELD, sw=2))
    frags.append(line(680, 165, 800, 95, color=FIELD, sw=2, dash="3,3"))

    frags.append(circle(480, 165, 11, fill="#d5f5e3", stroke=FIELD, sw=2))
    frags.append(text(480, 190, "hotfix/v2.4.1 (лише фікс CVE)", size=12, color=FIELD, bold=True))

    frags.append(fitbox(640, 138, 220, 48, "Cherry-pick / Merge\nназад у розробку", size=11, fill="#e8f8f5", stroke=FIELD))

    # Нижня частина: Апаратний лічильник захисту від відкату (Anti-Rollback Counter)
    frags.append(rect(20, 245, 940, 200, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(40, 273, "Апаратний бар'єр відкату: блокування вразливих версій у eFuse / OTP", size=15, color=INK, anchor="start", bold=True))

    # Стан 1: До патчу
    frags.append(rect(50, 300, 400, 125, fill="#fadbd8", stroke=POS, sw=1.5, rx=6))
    frags.append(text(250, 325, "Версія v2.4.0 (наявна вразливість)", size=13, color=POS, bold=True))
    frags.append(text(250, 350, "eFuse Monotonic Counter = 4", size=12, color=INK))
    frags.append(text(250, 375, "Заголовок образу: Security Version = 4", size=12, color=INK))
    frags.append(text(250, 402, "Статус: Дозволено завантаження v2.4.0", size=11, color=POS, bold=True))

    # Стрілка оновлення
    frags.append(arrow(465, 362, 515, 362, color=FIELD, sw=2.5))
    frags.append(text(490, 345, "OTA", size=12, color=FIELD, bold=True))

    # Стан 2: Після застосування hotfix v2.4.1
    frags.append(rect(530, 300, 410, 125, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(735, 325, "Версія v2.4.1 (hotfix застосовано)", size=13, color=FIELD, bold=True))
    frags.append(text(735, 350, "eFuse Monotonic Counter спалено в 5", size=12, color=INK, bold=True))
    frags.append(text(735, 375, "Заголовок образу: Security Version = 5", size=12, color=INK))
    frags.append(text(735, 402, "Старий образ v2.4.0 блокується апаратно Secure Boot", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "hotfix-branching-and-rollback.svg"), w, h, *frags)


def fig_emergency_canary_rollout():
    """Схема канаркового розгортання екстреного випуску та двобанковий захист Dual-Bank."""
    w, h = 980, 450
    frags = []

    # Ліва колонка: Фази канаркового оновлення
    frags.append(rect(20, 20, 530, 410, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(40, 48, "Фазоване канаркове розгортання (Canary Rollout)", size=15, color=INK, anchor="start", bold=True))

    steps = [
        ("Фаза 1: Canary 1% (тестовий парк)", 285, 95, 470, 48, "#ebf5fb", "#2980b9", "Швидка телеметрія, контроль першого старту"),
        ("Фаза 2: Вікно витримки (Soak 1–2 год)", 285, 175, 470, 48, "#fcf3cf", "#b7950b", "Моніторинг перезапусків watchdog, асертів, каналу"),
        ("Фаза 3: Розширення 10% → 50%", 285, 255, 470, 48, "#e8f8f5", FIELD, "Контроль навантаження на OTA-сервери та мережу"),
        ("Фаза 4: Повний парк 100%", 285, 335, 470, 48, "#d5f5e3", FIELD, "Завершення міграції, спалювання eFuse лічильника"),
    ]

    for label, cx, cy, bw, bh, f_col, s_col, sub in steps:
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, label, size=13, fill=f_col, stroke=s_col, bold=True))
        frags.append(text(cx, cy + 34, sub, size=11, color=MUTED))

    frags.append(arrow(285, 120, 285, 148, color=LINE, sw=1.5))
    frags.append(arrow(285, 200, 285, 228, color=LINE, sw=1.5))
    frags.append(arrow(285, 280, 285, 308, color=LINE, sw=1.5))

    # Права колонка: Двобанковий захист (Dual-Bank A/B Bootloader)
    frags.append(rect(570, 20, 390, 410, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(590, 48, "Апаратний захист від цеглини (Dual-Bank)", size=14, color=FIELD, anchor="start", bold=True))

    # Flash Bank A
    frags.append(rect(600, 80, 330, 95, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    frags.append(text(765, 105, "Flash Bank A (Поточна версія v2.4.0)", size=12, color=INK, bold=True))
    frags.append(text(765, 128, "Працює стабільно, але має вразливість", size=11, color=MUTED))
    frags.append(text(765, 150, "Стан: АКТИВНИЙ ДО ПІДТВЕРДЖЕННЯ", size=11, color="#2980b9", bold=True))

    # Flash Bank B
    frags.append(rect(600, 200, 330, 110, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(765, 225, "Flash Bank B (Hotfix v2.4.1)", size=12, color=INK, bold=True))
    frags.append(text(765, 248, "Запис нового образу в пасивний банк", size=11, color=MUTED))
    frags.append(text(765, 270, "Пробний запуск (Trial Boot) + самотест", size=11, color=FIELD, bold=True))
    frags.append(text(765, 292, "Якщо збій → автоповернення в Bank A", size=11, color=POS))

    # Правило транзакційності
    frags.append(rect(600, 330, 330, 80, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(765, 355, "Правило підтвердження (Commit):", size=11, color=INK, bold=True))
    frags.append(text(765, 375, "Лише після проходження самодіагностики", size=10, color=INK))
    frags.append(text(765, 393, "і зв'язку з бекендом Bank B стає постійним", size=10, color=INK))

    render(os.path.join(OUT_DIR, "emergency-canary-rollout.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_fast_track_vs_full_pipeline()
    fig_hotfix_branching_and_rollback()
    fig_emergency_canary_rollout()
    print("Всі фігури згенеровано успішно.")
