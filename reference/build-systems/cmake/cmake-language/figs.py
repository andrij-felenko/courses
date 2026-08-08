# -*- coding: utf-8 -*-
"""Фігури до теми «Мова CMakeLists: змінні, області, потік керування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

WARN_FILL = "#fdecea"


def chips(x0, cy, items, size=14, pad=11, gap=16, stroke=LINE, fill=FILL):
    """Ряд рамок-«аргументів» ліворуч направо від x0. Повертає (фрагмент, кінцевий x)."""
    out, x = [], x0
    for s in items:
        w = text_width(s, size) + 2 * pad
        body, _, _ = textbox(x + w / 2, cy, s, size=size, pad=pad, stroke=stroke, fill=fill)
        out.append(body)
        x += w + gap
    return "".join(out), x


# ── 1. Що дістає команда ────────────────────────────────────────────────────
def fig_args():
    W, H = 1000, 580
    frags = []
    frags.append(text(40, 66, "set(SRC main.cpp util.cpp)  →  SRC = «main.cpp;util.cpp»",
                      size=13, color=MUTED, anchor="start"))
    frags.append(text(40, 88, "set(EMPTY \"\")  →  EMPTY = «»",
                      size=13, color=MUTED, anchor="start"))

    panels = [
        ("add_library(app ${SRC})",
         ["app", "main.cpp", "util.cpp"], LINE, FILL,
         "крапка з комою у значенні ділить його на окремі аргументи — саме так і працюють списки"),
        ("add_library(app \"${SRC}\")",
         ["app", "main.cpp;util.cpp"], LINE, FILL,
         "лапки склеюють: другий аргумент — одне «ім'я файлу» з крапкою з комою всередині"),
        ("if(${EMPTY} STREQUAL \"x\")",
         ["STREQUAL", "x"], POS, WARN_FILL,
         "порожнє значення не стає порожнім аргументом, воно зникає — if дістає два аргументи замість трьох"),
    ]
    y0 = 140
    for src, items, st, fl, note in panels:
        frags.append(text(40, y0, src, size=15, anchor="start", bold=True))
        frags.append(text(40, y0 + 34, "команда дістає аргументи:", size=12, color=MUTED, anchor="start"))
        body, _ = chips(56, y0 + 72, items, stroke=st, fill=fl)
        frags.append(body)
        frags.append(text(40, y0 + 118, note, size=12.5, color=MUTED, anchor="start"))
        y0 += 150

    render(os.path.join(IMG, "args.svg"), W, H, *frags,
           title="Що насправді дістає команда")


# ── 2. Куди дивиться ${X} ───────────────────────────────────────────────────
def fig_lookup():
    W, H = 940, 560
    cx, bw = 300, 320
    frags = []
    frags.append(text(140, 76, "${X} шукається згори вниз:", size=13, color=MUTED, anchor="start"))

    steps = [
        (90, 66, "області викликаних функцій\n(зсередини назовні по стеку)"),
        (210, 52, "область поточного каталогу"),
        (310, 52, "кеш — CMakeCache.txt"),
    ]
    for y, h, label in steps:
        frags.append(fitbox(cx - bw / 2, y, bw, h, label, size=14))
    frags.append(arrow(cx, 158, cx, 206))
    frags.append(arrow(cx, 264, cx, 306))
    frags.append(text(128, 186, "нема — далі", size=12, color=MUTED, anchor="end"))
    frags.append(text(128, 290, "нема — далі", size=12, color=MUTED, anchor="end"))

    rx, rw = 700, 250
    frags.append(fitbox(rx - rw / 2, 90, rw, 46, "$ENV{X}", size=15, bold=True))
    frags.append(arrow(rx, 140, rx, 194))
    frags.append(fitbox(rx - rw / 2, 198, rw, 46, "змінні оточення процесу", size=13))
    frags.append(text(rx, 272, "окремий простір імен —", size=12, color=MUTED))
    frags.append(text(rx, 292, "жодного зв'язку з ${X}", size=12, color=MUTED))

    frags.append(fitbox(rx - rw / 2, 320, rw, 46, "$CACHE{X}", size=15, bold=True))
    frags.append(arrow(rx - rw / 2 - 10, 343, cx + bw / 2 + 8, 336))
    frags.append(text(rx, 396, "одразу в кеш, повз усе", size=12, color=MUTED))
    frags.append(text(rx, 416, "інше (з CMake 3.13)", size=12, color=MUTED))

    frags.append(fitbox(60, 456, 820, 66,
                        "виграє перша знайдена ланка — тому звичайна змінна ЗАТІНЮЄ\n"
                        "однойменний запис кешу, і зміна в кеші не дає жодного ефекту",
                        size=14))
    render(os.path.join(IMG, "lookup.svg"), W, H, *frags,
           title="Куди дивиться ${X}")


# ── 3. Області як копії ─────────────────────────────────────────────────────
def fig_scopes():
    W, H = 980, 540
    frags = []
    frags.append(fitbox(60, 90, 340, 84,
                        "CMakeLists.txt у корені\nобласть каталогу «/»", size=14))
    frags.append(fitbox(60, 300, 340, 84,
                        "src/CMakeLists.txt\nобласть каталогу «/src»", size=14))

    frags.append(arrow(170, 178, 170, 296))
    frags.append(mtext(196, 224, ["копія ВСІХ змінних", "на момент виклику"],
                       size=12.5, color=MUTED, anchor="start"))
    frags.append(arrow(340, 296, 340, 178, color=MUTED))
    frags.append(mtext(366, 262, ["назад — лише", "set(V … PARENT_SCOPE)"],
                       size=12.5, color=MUTED, anchor="start"))

    frags.append(fitbox(640, 90, 300, 294,
                        "КЕШ\nодин на все дерево збірки\nі на всі прогони", size=15))
    frags.append(line(400, 120, 640, 120, color=MUTED, dash="5 4"))
    frags.append(line(400, 354, 640, 354, color=MUTED, dash="5 4"))
    frags.append(text(520, 148, "видно з будь-якої області", size=12, color=MUTED))

    frags.append(fitbox(60, 430, 880, 62,
                        "include() області НЕ створює: його рядки виконуються там само, де стоїть виклик",
                        size=14))
    render(os.path.join(IMG, "scopes.svg"), W, H, *frags,
           title="Область — це копія, а не посилання")


# ── 4. Пріоритет операторів if() (до вставки api-if-and-lists) ───────────────
def fig_if_precedence():
    W, H = 1000, 560
    frags = []
    frags.append(text(60, 62, "if(<умова>) згортає аргументи згори вниз:",
                      size=14, color=MUTED, anchor="start"))

    levels = [
        "1 · дужки ( … ) — усе всередині обчислюється першим",
        "2 · унарні перевірки: DEFINED, COMMAND, TARGET, TEST, POLICY,\nEXISTS, IS_DIRECTORY, IS_SYMLINK, IS_ABSOLUTE, IS_READABLE …",
        "3 · бінарні перевірки: STREQUAL, EQUAL, VERSION_LESS, MATCHES,\nIN_LIST, PATH_EQUAL, IS_NEWER_THAN …",
        "4 · NOT",
        "5 · AND і OR — РІВНІ між собою, зліва направо, без короткого замикання",
    ]
    y = 88
    for i, s in enumerate(levels):
        h = 64 if "\n" in s else 46
        frags.append(fitbox(60, y, 880, h, s, size=14))
        y += h + 18

    frags.append(line(60, y + 6, 940, y + 6, color=MUTED, dash="5 4"))
    frags.append(text(60, y + 42, "приклад: if(NOT A AND B OR C)",
                      size=15, bold=True, anchor="start"))
    frags.append(text(60, y + 72,
                      "читається як  ((NOT A) AND B) OR C  —  а не як  (NOT A) AND (B OR C)",
                      size=13.5, color=MUTED, anchor="start"))
    frags.append(text(60, y + 100,
                      "AND не «сильніший» за OR: обидва йдуть у порядку запису, тож дужки ставлять руками",
                      size=12.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "if-precedence.svg"), W, H, *frags,
           title="Пріоритет операторів if()")


# ── 5. Історія: мова доростала латками ──────────────────────────────────────
def fig_history():
    W, H = 1060, 720
    frags = []
    frags.append(text(W / 2, 56, "кожен рядок — окрема добудова вже випущеної мови",
                      size=13.5, color=MUTED))

    axis_x = 250
    y0, step = 108, 96
    rows = [
        ("31 серпня 2000",
         "оголошення в списку розсилки ITK: вхідний файл — набір ключових слів\nSOURCE_FILES, LIBRARY, SUBDIRS. Ні змінних, ні умов, ні власних команд"),
        ("2 січня 2001",
         "cmIfCommand: умова стає ЗВИЧАЙНОЮ командою, а не синтаксисом —\nїї аргументи приходять уже готовими рядками"),
        ("13 серпня 2002",
         "cmMacroCommand: макрос — підстановка тексту у вже наявний розбір,\nбез власної області значень"),
        ("грудень 2007 → 2.6",
         "function() і PARENT_SCOPE: власна область з'являється\nна сім років пізніше за макроси"),
        ("2.6, травень 2008",
         "політики CMP: кожна зміна поведінки дістає номер,\nстаре й нове співіснують у тому самому виконуваному файлі"),
        ("3.1, 2014",
         "CMP0054: аргумент у лапках більше не розіменовується вдруге —\nстару поведінку прибрати не можна, лише перемкнути"),
        ("4.0, 2025",
         "сумісність із версіями нижче 3.5 прибрано: cmake_minimum_required(VERSION 3.4)\nтепер помилка збірки, а не попередження"),
    ]

    frags.append(line(axis_x, y0 - 30, axis_x, y0 + (len(rows) - 1) * step + 34,
                      color=MUTED, sw=1.5))
    for i, (when, what) in enumerate(rows):
        cy = y0 + i * step
        frags.append(text(axis_x - 26, cy + 5, when, size=14, bold=True, anchor="end"))
        frags.append(circle(axis_x, cy, 7, fill=BG, stroke=LINE, sw=2))
        frags.append(fitbox(axis_x + 26, cy - 32, 760, 64, what, size=13))

    render(os.path.join(IMG, "history.svg"), W, H, *frags,
           title="Мова CMakeLists: сім добудов замість одного проєкту")


# ── 6. Як cmake_parse_arguments розкладає виклик (до вставки proj-) ──────────
def fig_parse():
    W, H = 980, 700
    frags = []
    frags.append(text(60, 42, "виклик із помилкою в імені ключового слова і забутим значенням",
                      size=12.5, color=MUTED, anchor="start"))
    frags.append(text(60, 70, "add_project_library(NAME core  SOURCES a.cpp b.cpp",
                      size=14, anchor="start"))
    frags.append(text(96, 94, "PUBLIC_DEPENDS fmt::fmt  PRIVATE_DEPS  NO_INSTALL)",
                      size=14, anchor="start"))

    frags.append(arrow(250, 130, 250, 182))
    frags.append(text(282, 152, "cmake_parse_arguments(PARSE_ARGV 0 ARG …)",
                      size=12.5, color=MUTED, anchor="start"))

    rows = [
        ("ARG_NAME", "core", LINE, FILL),
        ("ARG_SOURCES", "a.cpp;b.cpp", LINE, FILL),
        ("ARG_NO_INSTALL", "TRUE", LINE, FILL),
        ("ARG_PUBLIC_HEADERS", "не визначена", MUTED, BG),
        ("ARG_PUBLIC_DEPS", "не визначена", MUTED, BG),
        ("ARG_UNPARSED_ARGUMENTS", "PUBLIC_DEPENDS;fmt::fmt", POS, WARN_FILL),
        ("ARG_KEYWORDS_MISSING_VALUES", "PRIVATE_DEPS", POS, WARN_FILL),
    ]
    y = 194
    for name, value, st, fl in rows:
        frags.append(fitbox(60, y, 380, 44, name, size=14, stroke=st, fill=fl))
        frags.append(fitbox(470, y, 380, 44, value, size=14, stroke=st, fill=fl))
        y += 56

    frags.append(fitbox(60, 606, 790, 64,
                        "два останні рядки — єдиний захист від друкарської помилки:\n"
                        "без явної перевірки PUBLIC_DEPENDS і PRIVATE_DEPS зникнуть мовчки",
                        size=14))
    render(os.path.join(IMG, "parse.svg"), W, H, *frags,
           title="Як cmake_parse_arguments розкладає виклик")


fig_args()
fig_lookup()
fig_scopes()
fig_if_precedence()
fig_history()
fig_parse()
print("ok")
