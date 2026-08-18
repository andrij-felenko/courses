# -*- coding: utf-8 -*-
"""
Генерація SVG-фігур для теми "Де живе правда про гроші: фінансова цілісність"
(money-truth-choice) у guide/progarch/nodes-tenancy-billing-data/money-truth-choice.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, circle, textbox, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, BG, LINE
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_crud_vs_ledger(path):
    """Фігура 1: Порівняння Mutable CRUD balance vs Immutable Double-Entry Ledger."""
    w, h = 800, 360
    elems = []

    elems.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    # Ліва колона: Мутабельний CRUD (Погано / Небезпечно)
    elems.append(rect(20, 20, 360, 320, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    elems.append(text(200, 50, "Мутабельний стан (CRUD)", size=16, bold=True, color=POS))
    elems.append(text(200, 72, "UPDATE accounts SET balance = ...", size=12, color=MUTED, italic=True))

    b1, _, _ = textbox(200, 120, "Таблиця: Accounts\nID: 42  |  Balance: $800", size=13, fill=BG, stroke=POS, pad=8)
    elems.append(b1)

    elems.append(arrow(110, 160, 150, 210, color=POS, sw=1.5))
    elems.append(arrow(290, 160, 250, 210, color=POS, sw=1.5))
    elems.append(text(100, 180, "Списання $100", size=11, color=POS, anchor="end"))
    elems.append(text(300, 180, "Списання $100", size=11, color=POS, anchor="start"))

    b2, _, _ = textbox(200, 240, "Race Condition / Lost Update!\nБаланс стає $700 замість $600\nІсторія операцій втрачена!", size=12, fill="#f8d7da", stroke=POS, color=POS, pad=8)
    elems.append(b2)
    elems.append(text(200, 315, "✖ Немає аудиту, немає інваріанту", size=12, bold=True, color=POS))

    # Права колона: Immutable Ledger (Добре / Безпечно)
    elems.append(rect(420, 20, 360, 320, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    elems.append(text(600, 50, "Незмінний реєстр (Append-Only)", size=16, bold=True, color=FIELD))
    elems.append(text(600, 72, "INSERT INTO ledger_entries ...", size=12, color=MUTED, italic=True))

    entries_text = (
        "Журнал проводжень (Immutable Log):\n"
        "#1: +$1000 (Поповнення)\n"
        "#2: -$100  (Оплата послуги A)\n"
        "#3: -$100  (Оплата послуги B)"
    )
    b3, _, _ = textbox(600, 140, entries_text, size=12, fill=BG, stroke=FIELD, pad=10)
    elems.append(b3)

    b4, _, _ = textbox(600, 240, "Баланс = SUM(Entries) = $800\nТочна історія + Кожен цент відомий", size=12, fill="#d4edda", stroke=FIELD, color=FIELD, pad=8)
    elems.append(b4)
    elems.append(text(600, 315, "✔ Повний аудит, незмінний лог", size=12, bold=True, color=FIELD))

    return render(path, w, h, *elems)


def fig_double_entry_invariant(path):
    """Фігура 2: Інваріант подвійного запису (Дебет = Кредит)."""
    w, h = 760, 320
    elems = []

    elems.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    elems.append(rect(30, 20, 700, 280, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elems.append(text(380, 50, "Транзакція #TX-9402: Поповнення гаманця на $100", size=16, bold=True, color=INK))
    elems.append(text(380, 72, "Інваріант: ∑ Дебет = ∑ Кредит = $100", size=13, color=FIELD, bold=True))

    elems.append(rect(60, 100, 300, 140, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=6))
    elems.append(text(210, 130, "ДЕБЕТ (Debit)", size=14, bold=True, color=NEG))
    b_deb, _, _ = textbox(210, 175, "Рахунок: Assets:Bank:Stripe\nСума: +$100.00", size=13, fill=BG, stroke=NEG, color=INK, pad=8)
    elems.append(b_deb)

    elems.append(line(360, 170, 400, 170, color=LINE, sw=2))
    elems.append(circle(380, 170, 16, fill=BG, stroke=FIELD, sw=2))
    elems.append(text(380, 175, "=", size=16, bold=True, color=FIELD))

    elems.append(rect(400, 100, 300, 140, fill="#fef9e7", stroke=POS, sw=1.5, rx=6))
    elems.append(text(550, 130, "КРЕДИТ (Credit)", size=14, bold=True, color=POS))
    b_cred, _, _ = textbox(550, 175, "Рахунок: Liabilities:User:42\nСума: +$100.00", size=13, fill=BG, stroke=POS, color=INK, pad=8)
    elems.append(b_cred)

    elems.append(text(380, 275, "Гроші не виникають нізвідки: банківський актив зріс = зобов'язання перед користувачем зросло", size=12, color=MUTED, italic=True))

    return render(path, w, h, *elems)


def fig_concurrency_race_locks(path):
    """Фігура 3: Три стратегії захисту від race conditions."""
    w, h = 820, 340
    elems = []

    elems.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    elems.append(rect(20, 20, 240, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elems.append(text(140, 50, "1. Ordered Locking", size=14, bold=True, color=INK))
    elems.append(text(140, 70, "Pessimistic SELECT FOR UPDATE", size=11, color=MUTED))
    t1 = (
        "Блокування рахунків\n"
        "у порядку зростання ID:\n"
        "lock(min(AccA, AccB));\n"
        "lock(max(AccA, AccB));\n\n"
        "✔ Запобігає Deadlocks\n"
        "✖ Блокує потік бази"
    )
    b1, _, _ = textbox(140, 185, t1, size=11, fill=BG, stroke=LINE, pad=8)
    elems.append(b1)

    elems.append(rect(280, 20, 250, 290, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elems.append(text(405, 50, "2. Optimistic Sequence", size=14, bold=True, color=INK))
    text_seq_sub = "CAS / Version per Account"
    elems.append(text(405, 70, text_seq_sub, size=11, color=MUTED))
    t2 = (
        "Кожен рахунок має\n"
        "послідовний sequence_num.\n"
        "INSERT перевіряє:\n"
        "seq == expected_seq\n\n"
        "✔ Без блокувань у БД\n"
        "✖ Retry при конфліктах"
    )
    b2, _, _ = textbox(405, 185, t2, size=11, fill=BG, stroke=LINE, pad=8)
    elems.append(b2)

    elems.append(rect(550, 20, 250, 290, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    elems.append(text(675, 50, "3. Single-Writer Log", size=14, bold=True, color=FIELD))
    elems.append(text(675, 70, "Partitioned Event Loop", size=11, color=MUTED))
    t3 = (
        "Транзакції для рахунку\n"
        "ідуть в один потік.\n"
        "Нуль блокувань!\n"
        "До 100,000+ tx/sec.\n\n"
        "✔ Максимальна швидкість\n"
        "✔ Гарантований порядок"
    )
    b3, _, _ = textbox(675, 185, t3, size=11, fill=BG, stroke=FIELD, pad=8)
    elems.append(b3)

    return render(path, w, h, *elems)


def fig_reconciliation_flow(path):
    """Фігура 4: Потік внутрішньої та зовнішньої звірки (Reconciliation)."""
    w, h = 800, 320
    elems = []

    elems.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    b_int, _, _ = textbox(130, 80, "Внутрішній Ledger\n(Assets:Bank:Pending)", size=13, fill="#ebf5fb", stroke=NEG, pad=10)
    elems.append(b_int)

    b_ext, _, _ = textbox(670, 80, "Зовнішній банк\n(Bank Statement CSV/MT940)", size=13, fill="#fef9e7", stroke=POS, pad=10)
    elems.append(b_ext)

    elems.append(arrow(220, 80, 330, 160, color=NEG, sw=1.5))
    elems.append(arrow(580, 80, 470, 160, color=POS, sw=1.5))

    b_eng, _, _ = textbox(400, 170, "Двигун звірки (Reconciliation Engine)\nСопоставлення за External Ref ID та сумою", size=13, fill=FILL, stroke=LINE, bold=True, pad=10)
    elems.append(b_eng)

    elems.append(arrow(340, 215, 230, 260, color=FIELD, sw=1.8))
    elems.append(arrow(460, 215, 570, 260, color=POS, sw=1.8))

    b_ok, _, _ = textbox(210, 275, "✔ Збіг (Matched)\nПереказ на Assets:Bank:Actual", size=12, fill="#d4edda", stroke=FIELD, color=FIELD, pad=8)
    elems.append(b_ok)

    b_err, _, _ = textbox(590, 275, "✖ Розбіжність (Discrepancy)\nПереказ на Suspense Account + Алерт", size=12, fill="#f8d7da", stroke=POS, color=POS, pad=8)
    elems.append(b_err)

    return render(path, w, h, *elems)


def fig_hash_chain_sealed(path):
    """Фігура 5: Криптографічне запечатування реєстру хеш-ланцюжком."""
    w, h = 800, 280
    elems = []

    elems.append(rect(0, 0, w, h, fill=BG, stroke="none"))

    elems.append(text(400, 35, "Запечатаний ланцюжок проводжень (Hash Chain Audit Trail)", size=15, bold=True, color=INK))

    t1 = "Запис #101\nTx: $100 -> User42\nHash: 8a3f91..."
    b1, _, _ = textbox(130, 110, t1, size=11, fill=FILL, stroke=LINE, pad=8)
    elems.append(b1)

    elems.append(arrow(220, 110, 270, 110, color=FIELD, sw=2))

    t2 = "Запис #102\nPrevHash: 8a3f91...\nTx: -$30 -> SaaS\nHash: f4b21c..."
    b2, _, _ = textbox(400, 110, t2, size=11, fill="#e8f8f5", stroke=FIELD, pad=8)
    elems.append(b2)

    elems.append(arrow(530, 110, 580, 110, color=FIELD, sw=2))

    t3 = "Запис #103\nPrevHash: f4b21c...\nTx: +$500 -> Deposit\nHash: 3e90aa..."
    b3, _, _ = textbox(700, 110, t3, size=11, fill=FILL, stroke=LINE, pad=8)
    elems.append(b3)

    elems.append(arrow(400, 220, 400, 165, color=POS, sw=1.5))
    b_tamper, _, _ = textbox(400, 240, "Спроба непомітно змінити $30 на $50 у Записі #102\nзмінює f4b21c... → 99zz88... і ЛАМАЄ всі наступні хеші!", size=11, fill="#f8d7da", stroke=POS, color=POS, pad=6)
    elems.append(b_tamper)

    return render(path, w, h, *elems)


def main():
    figures = [
        ("crud-vs-ledger.svg", fig_crud_vs_ledger),
        ("double-entry-invariant.svg", fig_double_entry_invariant),
        ("concurrency-race-locks.svg", fig_concurrency_race_locks),
        ("reconciliation-flow.svg", fig_reconciliation_flow),
        ("hash-chain-sealed.svg", fig_hash_chain_sealed),
    ]

    for fname, func in figures:
        path = os.path.join(OUT_DIR, fname)
        func(path)
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
