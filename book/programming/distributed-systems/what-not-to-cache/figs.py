# -*- coding: utf-8 -*-
"""Фігури теми «Що НЕ кешувати і чому». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#eaf0fd"
WARN_F  = "#fef9e7"
WARN_S  = "#f39c12"


# ── break-even: ефективна затримка та точка беззбитковості ───────────────────
def fig_break_even():
    W, H = 1000, 480
    f = []

    # Заголовок / пояснення моделі
    f.append(text(W / 2, 36, "Ефективна затримка запиту залежно від частки влучань (Hit Ratio)",
                  size=16, bold=True))
    f.append(text(W / 2, 60, "База даних (Origin): T_origin = 10.0 мс  ·  Кеш: T_cache = 1.0 мс",
                  size=13, color=MUTED))

    # Базова лінія (без кешу)
    b_no, _, _ = textbox(160, 115, "Без кешу (прямо в базу)\nЗатримка = 10.0 мс (еталон)",
                         size=13, bold=True, min_w=240, pad=10, fill=FILL, stroke=LINE)
    f.append(b_no)

    # 4 сценарії частки влучань
    scenarios = [
        ("Влучань: 90 % (h = 0.90)",
         "0.90 · 1.0 + 0.10 · 11.0 = 2.0 мс\nУ 5 разів швидше за базу",
         GREEN_F, FIELD, "Висока ефективність"),
        ("Влучань: 50 % (h = 0.50)",
         "0.50 · 1.0 + 0.50 · 11.0 = 6.0 мс\nУ 1.7 раза швидше за базу",
         BLUE_F, NEG, "Помірний виграш"),
        ("Влучань: 10 % (h = 0.10) — Точка зламу",
         "0.10 · 1.0 + 0.90 · 11.0 = 10.0 мс\nНульовий виграш, зайва пам'ять",
         WARN_F, WARN_S, "Межа беззбитковості"),
        ("Влучань: 2 % (h = 0.02) — Зона збитків",
         "0.02 · 1.0 + 0.98 · 11.0 = 10.8 мс\nНа 8 % повільніше за прямий запит!",
         RED_F, POS, "Кеш сповільнює систему"),
    ]

    for i, (title, math_txt, fill, stroke, verdict) in enumerate(scenarios):
        y = 190 + i * 66
        # Лівий блок: частка влучань
        f.append(fitbox(40, y - 26, 280, 54, title, size=13, bold=True,
                        fill=fill, stroke=stroke))
        # Середній блок: розрахунок затримки
        f.append(fitbox(340, y - 26, 380, 54, math_txt, size=12,
                        fill=FILL, stroke=LINE))
        # Правий блок: висновок
        f.append(fitbox(740, y - 26, 220, 54, verdict, size=13, bold=True,
                        fill=fill, stroke=stroke, color=stroke))

    f.append(text(W / 2, 460,
                  "Формула: E[T] = h · T_cache + (1 − h) · (T_cache + T_origin). При h < T_cache / T_origin кеш шкідливий.",
                  size=12, color=MUTED))

    render(out("break-even.svg"), W, H, *f,
           title="Ефективна затримка: коли кеш прискорює, а коли сповільнює систему")


# ── cache-pollution: засмічення кешу під час сканування ──────────────────────
def fig_cache_pollution():
    W, H = 1020, 520
    f = []

    f.append(text(W / 2, 34, "Анатомія засмічення кешу (Cache Pollution / Thrashing)",
                  size=16, bold=True))

    # Стан 1: Нормальний режим
    f.append(fitbox(40, 60, 220, 110,
                    "1. Нормальна робота\n\nЧастка влучань: 95 %\nНавантаження на БД: 5 %",
                    size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(fitbox(280, 60, 460, 110,
                    "Кеш LRU заповнений гарячими ключами:\n[ Профіль U1 ] [ Товар P42 ] [ Сесія S7 ] [ Баланс B3 ]\nКористувачі отримують миттєві відповіді з RAM.",
                    size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(760, 60, 220, 110,
                    "Первинна БД:\n\nCPU: 12 %\nIOPS: низький\nЧерги відсутні",
                    size=12, fill=GREEN_F, stroke=FIELD))

    # Стан 2: Пакетний скан / аналітичне вивантаження
    f.append(fitbox(40, 195, 220, 110,
                    "2. Одноразовий скан\n\nBatch Export / ETL\n10 000 унікальних ключів",
                    size=13, fill=WARN_F, stroke=WARN_S, bold=True))
    f.append(fitbox(280, 195, 460, 110,
                    "Потік холодних одноразових запитів:\nK101 → K102 → K103 → ... → K9999\nКожен запис вибиває гарячий ключ із черги LRU!",
                    size=12, fill=WARN_F, stroke=WARN_S))
    f.append(fitbox(760, 195, 220, 110,
                    "Проблема:\n\nХолодні ключі більше\nніколи не запитають,\nале вони витіснили гарячі!",
                    size=12, fill=RED_F, stroke=POS, bold=True))

    # Стан 3: Колапс після сканування
    f.append(fitbox(40, 330, 220, 110,
                    "3. Колапс (Thrashing)\n\nЧастка влучань: 3 %\nЛавина промахів",
                    size=13, fill=RED_F, stroke=POS, bold=True))
    f.append(fitbox(280, 330, 460, 110,
                    "Кеш забитий мертвими ключами скану:\n[ K9996 ] [ K9997 ] [ K9998 ] [ K9999 ]\nЗвернення до профілів та товарів ідуть у БД (Cache Stampede).",
                    size=12, fill=RED_F, stroke=POS))
    f.append(fitbox(760, 330, 220, 110,
                    "Первинна БД:\n\nCPU: 100 % (Перевантаження)\nIOPS: полиця дисків\nКаскадні таймаути",
                    size=12, fill=RED_F, stroke=POS, bold=True))

    # Підсумок
    f.append(text(W / 2, 485,
                  "Висновок: об'ємні скани, звіти та бекапи повинні читати БД в обхід кешу (Bypass / Direct I/O).",
                  size=13, color=MUTED, bold=True))

    render(out("cache-pollution.svg"), W, H, *f,
           title="Засмічення кешу під час пакетного сканування")


# ── decision-tree: 5 бар'єрів перед кешуванням ───────────────────────────────
def fig_decision_tree():
    W, H = 1040, 540
    f = []

    f.append(text(W / 2, 34, "Чекліст архітектора: 5 фільтрів для перевірки доцільності кешу",
                  size=16, bold=True))

    checks = [
        ("1. Частота змін",
         "Мутацій більше ніж читань (W >= R)?\nTTL менший за інтервал читання?",
         "НЕ КЕШУВАТИ\nНульова користь, витрата CPU"),
        ("2. Узгодженість",
         "Потрібна миттєва точність (нуль застарілості)?\nФінансовий баланс чи залишок товару?",
         "НЕ КЕШУВАТИ\nРизик подвійних списань"),
        ("3. Вартість обчислень",
         "Локальне обчислення дешевше за сокет кешу?\nT_compute < T_cache_lookup (нс проти мс)?",
         "НЕ КЕШУВАТИ\nЗвернення до кешу сповільнить CPU"),
        ("4. Безпека та контекст",
         "Приватні сесії, токени CSRF, персональні PII\nбез строгої ізоляції в ключі кешу?",
         "НЕ КЕШУВАТИ\nРизик витоку (Cache Deception)"),
        ("5. Локальність даних",
         "Одноразовий скан, аналітичний звіт,\nдовгий хвіст унікальних пошукових рядків?",
         "НЕ КЕШУВАТИ\nЗасмічення LRU (Thrashing)"),
    ]

    for i, (name, question, bad_action) in enumerate(checks):
        y = 70 + i * 86
        # Ліва колонка: Крок перевірки
        f.append(fitbox(30, y, 200, 72, name, size=13, bold=True, fill=BLUE_F, stroke=NEG))
        # Середня колонка: Питання
        f.append(fitbox(245, y, 470, 72, question, size=12, fill=FILL, stroke=LINE))
        # Права колонка: Якщо ТАК -> Не кешувати
        f.append(fitbox(730, y, 280, 72, "Якщо ТАК -> " + bad_action,
                        size=11, bold=True, fill=RED_F, stroke=POS, color=POS))

    f.append(text(W / 2, 518,
                  "Лише якщо на ВСІ 5 запитань відповідь «НІ» — сутність підлягає безпечному та вигідному кешуванню.",
                  size=13, color=FIELD, bold=True))

    render(out("decision-tree.svg"), W, H, *f,
           title="5 фільтрів перевірки доцільності кешування")


if __name__ == "__main__":
    fig_break_even()
    fig_cache_pollution()
    fig_decision_tree()
