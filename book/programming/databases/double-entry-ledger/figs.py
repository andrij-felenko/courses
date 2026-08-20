#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми double-entry-ledger.
Стиль та кольори відповідають канону (§5, §9 AUTHORING).
"""

import os
import sys

# Підключення svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_ledger_vs_mutable():
    """Фігура 1: Порівняння мутабельного балансу та гросбуха подвійного запису."""
    w, h = 820, 360
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "ledger-vs-mutable.svg")

    frags = []

    # Ліва колонка: Мутабельний підхід (UPDATE)
    panel_left = rect(20, 45, 375, 300, fill="#fdf2f2", stroke="#e0b4b4", sw=1.5, rx=8)
    frags.append(panel_left)
    frags.append(text(207, 72, "Мутабельний баланс (UPDATE)", size=15, color=POS, bold=True))

    # Блоки лівої колонки
    b1, _, _ = textbox(207, 115, "1. Початковий стан:\naccounts: balance = 500 грн", size=12, fill="#ffffff", stroke="#d9a7a7")
    b2, _, _ = textbox(207, 185, "2. Мутація безпосередньо в комірці:\nUPDATE accounts SET balance = 400\nWHERE id = 42;", size=12, fill="#ffffff", stroke="#d9a7a7")
    b3, _, _ = textbox(207, 275, "Фатальні наслідки:\n• Історія та контекст втрачені\n• Неможливо відновити аудит\n• Ризик втрати коштів при збої", size=12, fill="#fbe8e8", stroke=POS, color=POS, bold=True)
    frags.extend([b1, b2, b3])
    frags.append(arrow(207, 140, 207, 158, color=POS))
    frags.append(arrow(207, 218, 207, 238, color=POS))

    # Права колонка: Подвійний запис (Append-only Ledger)
    panel_right = rect(425, 45, 375, 300, fill="#f0f9f4", stroke="#b2dfdb", sw=1.5, rx=8)
    frags.append(panel_right)
    frags.append(text(612, 72, "Гросбух подвійного запису (Append-Only)", size=15, color=FIELD, bold=True))

    # Блоки правої колонки
    r1, _, _ = textbox(612, 115, "1. Незмінний журнал проводок (Journal):\nTx 101: Списання 100 грн з рахунку A\nTx 101: Зарахування 100 грн на рахунок B", size=12, fill="#ffffff", stroke="#a3d9c9")
    r2, _, _ = textbox(612, 185, "2. Інваріант нульової суми:\nDebit (+100) + Credit (-100) = 0\nЗаборона модифікацій (INSERT ONLY)", size=12, fill="#ffffff", stroke="#a3d9c9")
    r3, _, _ = textbox(612, 275, "Гарантії цілісності:\n• Баланс = математична сума проводок\n• Повний аудиторський слід у часі\n• Відтворюваність стану на будь-яку мить", size=12, fill="#e8f6ef", stroke=FIELD, color="#1b5e20", bold=True)
    frags.extend([r1, r2, r3])
    frags.append(arrow(612, 142, 612, 158, color=FIELD))
    frags.append(arrow(612, 218, 612, 238, color=FIELD))

    render(out_path, w, h, *frags, title="Мутабельний баланс проти гросбуха незмінних проводок")


def make_double_entry_t_account():
    """Фігура 2: Т-подібний рахунок та п'ять класів рахунків із дебетом/кредитом."""
    w, h = 840, 370
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "double-entry-t-account.svg")

    frags = []

    # Головне рівняння зверху
    eq_box, _, _ = textbox(420, 60, "Фундаментальне бухгалтерське рівняння:\nАктиви (Assets) + Витрати (Expenses) = Зобов'язання (Liabilities) + Власний капітал (Equity) + Доходи (Revenue)", size=13, fill="#eef2f7", stroke="#4a6fa5", color="#1c3d5a", bold=True)
    frags.append(eq_box)

    # Ліва колонка: Активи та Витрати (Активні рахунки)
    p_left = rect(30, 105, 370, 240, fill="#f6f9fc", stroke="#cbd5e1", sw=1.5, rx=8)
    frags.append(p_left)
    frags.append(text(215, 130, "Активні рахунки (Активи, Витрати)", size=14, color="#1e3a8a", bold=True))

    # Т-рахунок ліворуч
    frags.append(line(70, 175, 360, 175, color=LINE, sw=2))
    frags.append(line(215, 175, 215, 275, color=LINE, sw=2))
    frags.append(text(142, 165, "Дебет (Debit)", size=13, color=POS, bold=True))
    frags.append(text(287, 165, "Кредит (Credit)", size=13, color=NEG, bold=True))

    frags.append(text(142, 205, "+ Збільшення", size=13, color=POS, bold=True))
    frags.append(text(142, 225, "(Надходження активу /", size=11, color=MUTED))
    frags.append(text(142, 240, "понесення витрат)", size=11, color=MUTED))

    frags.append(text(287, 205, "− Зменшення", size=13, color=NEG, bold=True))
    frags.append(text(287, 225, "(Вибуття активу /", size=11, color=MUTED))
    frags.append(text(287, 240, "зменшення витрат)", size=11, color=MUTED))

    frags.append(fitbox(50, 285, 330, 48, "Нормальний баланс: ДЕБЕТОВИЙ\nБаланс = Сума(Дебет) − Сума(Кредит)", size=12, fill="#ffffff", stroke="#93c5fd", color="#1e40af", bold=True))

    # Права колонка: Зобов'язання, Капітал, Доходи (Пасивні рахунки)
    p_right = rect(440, 105, 370, 240, fill="#fdfbf7", stroke="#e2d9cc", sw=1.5, rx=8)
    frags.append(p_right)
    frags.append(text(625, 130, "Пасивні рахунки (Зобов'язання, Капітал, Доходи)", size=14, color="#854d0e", bold=True))

    # Т-рахунок праворуч
    frags.append(line(480, 175, 770, 175, color=LINE, sw=2))
    frags.append(line(625, 175, 625, 275, color=LINE, sw=2))
    frags.append(text(552, 165, "Дебет (Debit)", size=13, color=NEG, bold=True))
    frags.append(text(697, 165, "Кредит (Credit)", size=13, color=POS, bold=True))

    frags.append(text(552, 205, "− Зменшення", size=13, color=NEG, bold=True))
    frags.append(text(552, 225, "(Погашення зобов'язань /", size=11, color=MUTED))
    frags.append(text(552, 240, "виплата капіталу)", size=11, color=MUTED))

    frags.append(text(697, 205, "+ Збільшення", size=13, color=POS, bold=True))
    frags.append(text(697, 225, "(Зростання зобов'язань /", size=11, color=MUTED))
    frags.append(text(697, 240, "отримання доходу)", size=11, color=MUTED))

    frags.append(fitbox(460, 285, 330, 48, "Нормальний баланс: КРЕДИТОВИЙ\nБаланс = Сума(Кредит) − Сума(Дебет)", size=12, fill="#ffffff", stroke="#fcd34d", color="#92400e", bold=True))

    render(out_path, w, h, *frags, title="Структура Т-рахунків та напрямки дебету й кредиту")


def make_ledger_snapshot_pipeline():
    """Фігура 3: Конвеєр розрахунку балансу через знімки та журнал проводок."""
    w, h = 820, 330
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "ledger-snapshot-pipeline.svg")

    frags = []

    # Блок 1: Незмінний журнал проводок
    b1, _, _ = textbox(130, 90, "Незмінний журнал проводок\n(Append-Only Postings Log)\n• Seq 1..1 000 000\n• Immutable / Read-only\n• Строгий порядок транзакцій", size=12, fill="#eef2f6", stroke="#78909c")
    frags.append(b1)

    # Стрілка до знімка
    frags.append(arrow(245, 90, 315, 90, color=LINE, sw=1.8))
    frags.append(text(280, 75, "Періодично", size=11, color=MUTED))

    # Блок 2: Базовий знімок
    b2, _, _ = textbox(420, 90, "Знімок балансу (Snapshot)\nБаланс на Seq 1 000 000:\n50 000.00 UAH\n(Зафіксована точка відліку)", size=12, fill="#e8f5e9", stroke="#81c784", color="#1b5e20", bold=True)
    frags.append(b2)

    # Блок 3: Дельта проводок після знімка
    b3, _, _ = textbox(420, 235, "Хвіст свіжих проводок (Delta)\nSeq 1 000 001 .. 1 000 015\n(+500.00, -120.00, +80.00...)\nВсього 15 проводок у вибірці", size=12, fill="#fff8e1", stroke="#ffd54f", color="#f57f17")
    frags.append(b3)

    # Стрілка від журналу до дельти проводок
    frags.append(arrow(130, 155, 130, 235, color=LINE, sw=1.5))
    frags.append(arrow(130, 235, 285, 235, color=LINE, sw=1.8))
    frags.append(text(195, 220, "WHERE seq > 1000000", size=11, color=MUTED))

    # Зведення в обчислювач
    frags.append(arrow(535, 90, 620, 150, color=LINE, sw=1.8))
    frags.append(arrow(555, 235, 620, 175, color=LINE, sw=1.8))

    # Блок 4: Обчислення поточного балансу
    b4, _, _ = textbox(710, 160, "Миттєвий запит балансу\nO(k) замість O(N):\nБаланс = Snapshot +\n+ SUM(Delta Postings)\n= 50 460.00 UAH", size=12, fill="#ede7f6", stroke="#b39ddb", color="#4a148c", bold=True)
    frags.append(b4)

    render(out_path, w, h, *frags, title="Розрахунок балансу рахунку через знімки та дельту незмінного журналу")


if __name__ == "__main__":
    make_ledger_vs_mutable()
    make_double_entry_t_account()
    make_ledger_snapshot_pipeline()
    print("SVG figures generated successfully.")
