# -*- coding: utf-8 -*-
"""Фігури до теми «Flash зсередини» (сторінки, сектори, стирання перед записом).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Шість фігур теми (імена-слаги, без номерів):
  erase-write · granularity · hierarchy · update-one-byte · clear-only · why-managers
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CELL = "#e4e4e4"          # межа незайманої комірки
WARN = "#caa24a"          # осторога / «потерте»


def _bits(f, x0, y0, vals, col, fill_on, fill_off):
    """Рядок комірок-бітів. vals — рядок із '1'/'0'; fill_on — для 0 (погашений)."""
    w, gap = 30, 4
    for i, ch in enumerate(vals):
        x = x0 + i * (w + gap)
        fill = fill_off if ch == "1" else fill_on
        f.append(rect(x, y0, w, 34, fill=fill, stroke=col, sw=1.4, rx=3))
        f.append(text(x + w / 2, y0 + 23, ch, size=14, color=col, bold=True))


# ── 1. Головне правило: запис гасить біти, підняти назад — лише стиранням ──────
def fig_erase_write():
    W, H = 920, 412
    f = [text(W / 2, 30, "Головне правило Flash: спершу стерти, тоді писати", size=18, bold=True),
         text(W / 2, 52, "запис уміє лише гасити біти (1→0); підняти 0→1 можна тільки стиранням",
              size=11, color=MUTED, italic=True)]

    f.append(text(80, 104, "1. Стерто — усі одиниці (0xFF):", size=11, color=FIELD, anchor="start", bold=True))
    _bits(f, 80, 116, "11111111", FIELD, "#eef6ef", BG)

    f.append(text(80, 192, "2. Записали 0x52 — погасили частину бітів у 0:", size=11, color=NEG, anchor="start", bold=True))
    _bits(f, 80, 204, "01010010", NEG, "#e9eefb", BG)
    f.append(text(360, 226, "← запис рухає біти ЛИШЕ в один бік: 1→0", size=10, color=MUTED, anchor="start"))

    f.append(text(80, 286, "3. Хочемо 0x53? Треба підняти біт 0→1 — запис НЕ вміє:", size=11, color=POS, anchor="start", bold=True))
    _bits(f, 80, 298, "01010011", POS, "#fdecea", BG)
    f.append(text(360, 320, "← цей біт 0→1 неможливий без стирання", size=10, color=POS, anchor="start", bold=True))

    f.append(fitbox(360, 108, 500, 66,
                    "Запис: тільки 1→0 (гасити).\n"
                    "Стирання: усе назад у 1 — і лише цілим сектором.",
                    size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.6))
    render(os.path.join(IMG, "erase-write.svg"), W, H, *f)


# ── 2. Асиметрія: писати по сторінці, стирати цілим сектором ──────────────────
def fig_granularity():
    W, H = 920, 400
    f = [text(W / 2, 30, "Асиметрія: писати дрібно, стирати гуртом", size=18, bold=True),
         text(W / 2, 52, "запис — по сторінці (~256 Б); стирання — лише цілим сектором (~4 КБ)",
              size=11, color=MUTED, italic=True)]

    f.append(rect(80, 100, 760, 150, fill="#fbfdff", stroke=INK, sw=2.2, rx=12))
    f.append(text(100, 122, "Сектор (~4 КБ) = 16 сторінок", size=11, color=INK, anchor="start", bold=True))
    for i in range(16):
        x = 100 + i * 46
        if i == 5:
            f.append(rect(x, 140, 42, 90, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
        else:
            f.append(rect(x, 140, 42, 90, fill=BG, stroke=CELL, sw=1, rx=4))
    f.append(text(351, 256, "пишемо сюди (1 сторінка)", size=9, color=FIELD, bold=True))

    f.append(arrow(300, 300, 300, 252, color=FIELD, sw=2))
    f.append(text(300, 318, "ЗАПИС торкається однієї сторінки", size=10, color=FIELD, bold=True))
    f.append(arrow(640, 300, 640, 252, color=POS, sw=2))
    f.append(text(640, 318, "СТИРАННЯ змітає весь сектор", size=10, color=POS, bold=True))
    f.append(text(640, 334, "(усі 16 сторінок одразу)", size=9, color=POS))
    render(os.path.join(IMG, "granularity.svg"), W, H, *f)


# ── 3. Ієрархія одиниць: байт → сторінка → сектор → блок ──────────────────────
def fig_hierarchy():
    W, H = 900, 400
    f = [text(W / 2, 30, "Одиниці Flash: від байта до блоку", size=18, bold=True),
         text(W / 2, 52, "орієнтовні розміри для типового NOR-Flash; у NAND вони більші",
              size=11, color=MUTED, italic=True)]

    rows = [
        (270, 360, "#eef0f5", MUTED, "Байт / слово  ·  1–4 Б", "найдрібніше, чим оперуєш"),
        (205, 490, "#e9eefb", NEG,   "Сторінка (page)  ·  ~256 Б", "найменша одиниця ЗАПИСУ"),
        (140, 620, "#eef6ef", FIELD, "Сектор (sector)  ·  ~4 КБ", "найменша одиниця СТИРАННЯ"),
        (75, 750,  "#fff6e0", WARN,  "Блок (block)  ·  ~64 КБ", "більший блок стирання"),
    ]
    y = 96
    for x, w, fill, col, head, sub in rows:
        f.append(rect(x, y, w, 54, fill=fill, stroke=col, sw=1.8, rx=10))
        f.append(text(450, y + 23, head, size=12, color=col, bold=True))
        f.append(text(450, y + 42, sub, size=9.5, color=INK))
        y += 68

    f.append(text(W / 2, 384,
                  "Пишеш сторінками, стираєш секторами — і саме звідси всі примхи поводження з Flash.",
                  size=10, color=INK, bold=True))
    render(os.path.join(IMG, "hierarchy.svg"), W, H, *f)


# ── 4. Зміна одного байта = прочитати-стерти-переписати цілий сектор ──────────
def fig_update_one_byte():
    W, H = 900, 400
    f = [text(W / 2, 30, "Скільки коштує змінити ОДИН байт", size=18, bold=True),
         text(W / 2, 52, "не можна просто перезаписати — доводиться переписати цілий сектор",
              size=11, color=MUTED, italic=True)]

    steps = [
        (1, NEG,   "#e9eefb", "Прочитати весь сектор у RAM", "усі 4 КБ"),
        (2, FIELD, "#eef6ef", "Змінити потрібний байт у RAM", "1 байт"),
        (3, POS,   "#fdecea", "СТЕРТИ сектор у Flash", "усе → 0xFF"),
        (4, NEG,   "#e9eefb", "Записати сектор назад", "4 КБ із правкою"),
    ]
    y = 92
    for n, col, fill, head, sub in steps:
        f.append(circle(110, y + 22, 17, fill=fill, stroke=col, sw=2))
        f.append(text(110, y + 27, str(n), size=14, color=col, bold=True))
        f.append(rect(150, y, 600, 46, fill=fill, stroke=col, sw=1.6, rx=10))
        f.append(text(172, y + 22, head, size=12, color=col, anchor="start", bold=True))
        f.append(text(172, y + 39, sub, size=9.3, color=INK, anchor="start"))
        if n < 4:
            f.append(arrow(110, y + 39, 110, y + 66, color=INK, sw=1.8))
        y += 66

    f.append(fitbox(150, 360, 600, 34,
                    "Змінити 1 байт = переписати 4096. Ще й небезпечно: вимкнення між 3 і 4 = втрата сектора.",
                    size=9.5, bold=True, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(IMG, "update-one-byte.svg"), W, H, *f)


# ── 5. Дописувати й скасовувати, гасячи біти, без стирання ────────────────────
def fig_clear_only():
    W, H = 920, 380
    f = [text(W / 2, 30, "Хитрість зі стирання-в-один-бік: дописувати без стирання", size=18, bold=True),
         text(W / 2, 52, "поки в сторінці лишаються одиниці, можна гасити нові біти — і це безкоштовно",
              size=11, color=MUTED, italic=True)]

    f.append(rect(70, 100, 780, 140, fill="#fbfdff", stroke=INK, sw=2, rx=12))
    f.append(text(90, 124, "Стерта сторінка (усе 1) — пишемо записи один за одним, гасячи біти:",
                  size=10, color=INK, anchor="start"))
    slots = [
        (96,  150, "#eef6ef", FIELD, "запис A"),
        (254, 150, "#fdecea", POS,   "A — недійсний"),
        (412, 150, "#eef6ef", FIELD, "запис B"),
        (570, 150, "#eef6ef", FIELD, "запис C"),
    ]
    for x, w, fill, col, label in slots:
        f.append(rect(x, w, 150, 56, fill=fill, stroke=col, sw=1.6, rx=6))
        f.append(text(x + 75, w + 32, label, size=9.8, color=col, bold=True))
    f.append(rect(728, 150, 160, 56, fill=BG, stroke=CELL, sw=1.6, rx=6))
    f.append(text(808, 182, "вільно (усе 1)", size=9.8, color=MUTED, bold=True))
    f.append(text(90, 226, "«недійсний» = погасили ще один біт-прапорець (1→0), стирати не довелося.",
                  size=9.3, color=MUTED, anchor="start"))

    f.append(fitbox(120, 268, 680, 92,
                    "Звідси два прийоми, що ховаються в NVS і логах:\n"
                    "• новий запис — ДОПИСати в незаймане місце (а не переписувати старе);\n"
                    "• скасувати старий — погасити його прапорець; стерти лише коли сторінка повна.\n"
                    "Так стирання — рідкісне, а отже й знос менший.",
                    size=10, bold=True, fill="#fff6e0", stroke=WARN, sw=1.6))
    render(os.path.join(IMG, "clear-only.svg"), W, H, *f)


# ── 6. Чому пишуть через NVS/ФС, а не в сирий Flash ───────────────────────────
def fig_why_managers():
    W, H = 900, 360
    f = [text(W / 2, 30, "Чому майже ніхто не пише у Flash напряму", size=18, bold=True),
         text(W / 2, 52, "сирі правила легко порушити — тож за вас із ними воює готовий менеджер",
              size=11, color=MUTED, italic=True)]

    f.append(rect(60, 96, 360, 200, fill="#fffafa", stroke=POS, sw=2, rx=12))
    f.append(text(240, 122, "Напряму (сирий Flash)", size=12, color=POS, bold=True))
    for i, ln in enumerate([
        "• сам стирай перед записом",
        "• сам читай-стирай-переписуй сектор",
        "• сам стеж за зносом",
        "• сам рятуйся від вимкнення"]):
        f.append(text(82, 154 + i * 28, ln, size=10, color=INK, anchor="start"))
    f.append(text(82, 266, "• → легко зіпсувати дані", size=10, color=POS, anchor="start", bold=True))

    f.append(rect(480, 96, 360, 200, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    f.append(text(660, 122, "Через NVS / файлову систему", size=11.5, color=FIELD, bold=True))
    for i, ln in enumerate([
        "• просто set(\"ключ\", значення)",
        "• менеджер сам робить весь танець",
        "• сам розкладає знос",
        "• сам береже від збоїв"]):
        f.append(text(502, 154 + i * 28, ln, size=10, color=INK, anchor="start"))
    f.append(text(502, 266, "• → надійно й просто", size=10, color=FIELD, anchor="start", bold=True))

    f.append(arrow(420, 196, 480, 196, color=INK, sw=2.4))
    render(os.path.join(IMG, "why-managers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_erase_write()
    fig_granularity()
    fig_hierarchy()
    fig_update_one_byte()
    fig_clear_only()
    fig_why_managers()
    print("OK: erase-write, granularity, hierarchy, update-one-byte, clear-only, why-managers")
