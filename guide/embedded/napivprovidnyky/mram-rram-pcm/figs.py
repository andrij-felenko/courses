# -*- coding: utf-8 -*-
"""Фігури до теми «MRAM, RRAM і PCM: нові нелеткі пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN = FIELD        # «добре», нелеткість/перевага
RED   = POS          # «гаряче»/обмеження
BLUE  = NEG          # холодне
AMBER = "#b9770e"    # тепле застереження
PURPLE = "#7a3fb0"   # окремий акцент


# ── 1. Спільна ідея: біт як ОПІР, не заряд ───────────────────────────────────
def fig_resistance_bit():
    W, H = 1000, 430
    f = [text(W / 2, 32, "Спільна ідея трьох нових пам'ятей: біт — це ОПІР комірки",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Flash і DRAM кодують біт ЗАРЯДОМ; MRAM, RRAM і PCM кодують його "
                  "СТАНОМ ОПОРУ — і читають, міряючи струм",
                  size=12.5, color=MUTED, italic=True))

    # ліворуч: старий спосіб — заряд
    f.append(rect(40, 95, 410, 290, fill="#fbfbfb", stroke="#dddddd", sw=1.4, rx=8))
    f.append(text(245, 122, "Старий спосіб: біт = ЗАРЯД", size=14, color=BLUE, bold=True))
    f.append(text(245, 144, "(Flash — у плавучому затворі, DRAM — на конденсаторі)",
                  size=10.5, color=MUTED, italic=True))
    # заряджена комірка
    f.append(rect(80, 175, 150, 95, fill="#eaf0fd", stroke=BLUE, sw=1.6, rx=6))
    for i, (dx, dy) in enumerate([(-30, -15), (0, -22), (30, -12), (-18, 12), (18, 8), (0, -2)]):
        f.append(minus(155 + dx, 222 + dy, 7))
    f.append(text(155, 290, "є заряд → «0»", size=11, color=BLUE, bold=True))
    # порожня комірка
    f.append(rect(260, 175, 150, 95, fill=BG, stroke="#bbbbbb", sw=1.4, rx=6))
    f.append(text(335, 226, "(порожньо)", size=11, color=MUTED, italic=True))
    f.append(text(335, 290, "нема заряду → «1»", size=11, color=MUTED, bold=True))
    f.append(text(245, 332, "крихкий: заряд стікає, тоне в шумі,", size=10.5, color=AMBER))
    f.append(text(245, 350, "комірку треба заряджати крізь ізолятор", size=10.5, color=AMBER))
    f.append(text(245, 372, "(звідси знос і повільний запис)", size=10, color=MUTED, italic=True))

    # праворуч: новий спосіб — опір
    f.append(rect(550, 95, 410, 290, fill="#f3faf5", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(755, 122, "Новий спосіб: біт = ОПІР", size=14, color=GREEN, bold=True))
    f.append(text(755, 144, "(MRAM, RRAM, PCM — стан самої речовини комірки)",
                  size=10.5, color=MUTED, italic=True))
    # низький опір — струм тече
    f.append(rect(590, 175, 150, 95, fill="#eaf7ee", stroke=GREEN, sw=1.6, rx=6))
    f.append(line(600, 222, 730, 222, color=GREEN, sw=3))
    f.append(arrow(610, 222, 720, 222, color=GREEN, sw=3))
    f.append(text(665, 210, "струм тече", size=10.5, color=GREEN, bold=True))
    f.append(text(665, 290, "низький опір → «1»", size=11, color=GREEN, bold=True))
    # високий опір — струм заблоковано
    f.append(rect(770, 175, 150, 95, fill="#fdecea", stroke=RED, sw=1.6, rx=6))
    f.append(line(780, 222, 845, 222, color=RED, sw=3))
    f.append(line(852, 214, 868, 230, color=RED, sw=2.4))
    f.append(line(852, 230, 868, 214, color=RED, sw=2.4))
    f.append(text(845, 210, "майже не тече", size=10.5, color=RED, bold=True))
    f.append(text(845, 290, "високий опір → «0»", size=11, color=RED, bold=True))
    f.append(text(755, 332, "стан тримає сама речовина (магніт, місток,", size=10.5, color=GREEN))
    f.append(text(755, 350, "фаза кристала) — стоїть без живлення й роками", size=10.5, color=GREEN))
    f.append(text(755, 372, "читати — лише пустити крізь комірку слабкий струм", size=10, color=MUTED, italic=True))

    f.append(text(W / 2, 412, "Читання однакове для всіх трьох: пропусти крихітний струм і зміряй — "
                  "тече вільно чи ні. Різниця лише в тому, ЩО саме створює два рівні опору.",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "resistance-bit.svg"), W, H, *f)


# ── 2. Три механізми поряд: MRAM, RRAM, PCM ──────────────────────────────────
def fig_three_mechanisms():
    W, H = 1020, 520
    f = [text(W / 2, 32, "Три способи зробити «низький опір» і «високий опір»",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "MRAM — напрямком магніту; RRAM — містком атомних дефектів; "
                  "PCM — впорядкованістю самих атомів",
                  size=12.5, color=MUTED, italic=True))

    col_w = 320
    xs = [20, 350, 680]
    top = 80
    panel_h = 410

    # ── MRAM ──
    x = xs[0]
    f.append(rect(x, top, col_w, panel_h, fill="#f3faf5", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(x + col_w / 2, top + 28, "MRAM", size=16, color=GREEN, bold=True))
    f.append(text(x + col_w / 2, top + 48, "магнітний тунельний перехід", size=11, color=MUTED, italic=True))

    def mtj(cx, cy, free_up, label, rcolor):
        out = []
        # закріплений шар (стрілка завжди вправо)
        out.append(rect(cx - 70, cy + 22, 140, 26, fill="#e7e7ef", stroke=LINE, sw=1.3, rx=3))
        out.append(arrow(cx - 30, cy + 35, cx + 30, cy + 35, color=INK, sw=2.4))
        out.append(text(cx, cy + 64, "закріплений", size=9.5, color=MUTED))
        # бар'єр
        out.append(rect(cx - 70, cy + 8, 140, 12, fill="#fff3cd", stroke=AMBER, sw=1.2, rx=2))
        out.append(text(cx + 96, cy + 18, "бар'єр", size=9, color=AMBER, anchor="start"))
        # вільний шар
        out.append(rect(cx - 70, cy - 18, 140, 26, fill="#eaf7ee", stroke=GREEN, sw=1.6, rx=3))
        if free_up:
            out.append(arrow(cx - 30, cy - 5, cx + 30, cy - 5, color=GREEN, sw=2.6))
        else:
            out.append(arrow(cx + 30, cy - 5, cx - 30, cy - 5, color=RED, sw=2.6))
        out.append(text(cx, cy - 30, "вільний", size=9.5, color=MUTED))
        out.append(text(cx, cy + 92, label, size=11, color=rcolor, bold=True))
        return out

    f += mtj(x + 85, top + 130, True, "паралельно → НИЗ. опір → «1»", GREEN)
    f += mtj(x + 230, top + 130, False, "антипаралельно → ВИС. → «0»", RED)
    f.append(text(x + col_w / 2, top + 268, "Біт — це НАПРЯМОК магніту", size=12, color=INK, bold=True))
    f.append(text(x + col_w / 2, top + 288, "у тонкому «вільному» шарі.", size=11, color=INK))
    f.append(text(x + col_w / 2, top + 312, "Збігається з нижнім → струм", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 328, "тунелює легко; протилежний", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 344, "→ опір зростає в рази.", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 372, "Пишемо: спін-поляризований", size=10.5, color=BLUE))
    f.append(text(x + col_w / 2, top + 388, "струм ПЕРЕВЕРТАЄ вільний шар.", size=10.5, color=BLUE))

    # ── RRAM ──
    x = xs[1]
    f.append(rect(x, top, col_w, panel_h, fill="#f3faf5", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(x + col_w / 2, top + 28, "RRAM (ReRAM)", size=16, color=GREEN, bold=True))
    f.append(text(x + col_w / 2, top + 48, "місток у діелектрику", size=11, color=MUTED, italic=True))

    def rram_cell(cx, cy, bridged, label, rcolor):
        out = []
        # електроди
        out.append(rect(cx - 55, cy - 40, 110, 16, fill="#cfcfcf", stroke=LINE, sw=1.2, rx=2))
        out.append(rect(cx - 55, cy + 40, 110, 16, fill="#cfcfcf", stroke=LINE, sw=1.2, rx=2))
        # діелектрик
        out.append(rect(cx - 55, cy - 24, 110, 64, fill="#eef0f4", stroke=MUTED, sw=1.2, rx=2))
        # ланцюжок дефектів
        ys = [cy - 22, cy - 11, cy, cy + 11, cy + 22, cy + 33]
        n = len(ys) if bridged else 3
        for i in range(n):
            out.append(circle(cx, ys[i], 5, fill="#fdecea" if bridged else "#fbe9c7",
                              stroke=rcolor, sw=1.6))
        out.append(text(cx, cy + 80, label, size=10.5, color=rcolor, bold=True))
        return out

    f += rram_cell(x + 85, top + 120, True, "місток замкнено → НИЗ. → «1»", GREEN)
    f += rram_cell(x + 230, top + 120, False, "розірвано → ВИС. → «0»", RED)
    f.append(text(x + col_w / 2, top + 232, "Біт — чи ЗАМКНЕНО тонку", size=12, color=INK, bold=True))
    f.append(text(x + col_w / 2, top + 252, "нитку-місток крізь ізолятор.", size=11, color=INK))
    f.append(text(x + col_w / 2, top + 276, "Місток — ланцюжок кисневих", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 292, "вакансій (місць без атома O).", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 316, "Зібрався → струм тече;", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 332, "розірвався → опір злітає.", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 360, "Пишемо: напруга РОСТИТЬ або", size=10.5, color=BLUE))
    f.append(text(x + col_w / 2, top + 376, "РВЕ місток (полярністю).", size=10.5, color=BLUE))
    f.append(text(x + col_w / 2, top + 396, "Перший раз — «формувальний» імпульс.", size=9.5, color=MUTED, italic=True))

    # ── PCM ──
    x = xs[2]
    f.append(rect(x, top, col_w, panel_h, fill="#f3faf5", stroke=GREEN, sw=1.6, rx=8))
    f.append(text(x + col_w / 2, top + 28, "PCM", size=16, color=GREEN, bold=True))
    f.append(text(x + col_w / 2, top + 48, "фазозмінна речовина (GST)", size=11, color=MUTED, italic=True))

    def pcm_cell(cx, cy, crystal, label, rcolor):
        out = []
        out.append(rect(cx - 50, cy - 30, 100, 60, fill="#f7f7f7", stroke=MUTED, sw=1.2, rx=4))
        import random
        random.seed(1 if crystal else 7)
        if crystal:
            # впорядкована решітка
            for r in range(4):
                for c in range(5):
                    out.append(circle(cx - 40 + c * 20, cy - 22 + r * 16, 3.2,
                                      fill="#eaf7ee", stroke=GREEN, sw=1.2))
        else:
            # хаос
            for _ in range(18):
                rx = cx - 44 + random.random() * 88
                ry = cy - 26 + random.random() * 52
                out.append(circle(rx, ry, 3.2, fill="#fdecea", stroke=RED, sw=1.2))
        out.append(text(cx, cy + 56, label, size=10.5, color=rcolor, bold=True))
        return out

    f += pcm_cell(x + 85, top + 112, True, "кристал → НИЗ. опір → «1»", GREEN)
    f += pcm_cell(x + 230, top + 112, False, "аморф → ВИС. опір → «0»", RED)
    f.append(text(x + col_w / 2, top + 200, "Біт — чи атоми РІВНО", size=12, color=INK, bold=True))
    f.append(text(x + col_w / 2, top + 220, "вишикувані, чи в хаосі.", size=11, color=INK))
    f.append(text(x + col_w / 2, top + 244, "Кристал проводить добре;", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 260, "аморфне скло — погано.", size=10.5, color=MUTED))
    f.append(text(x + col_w / 2, top + 288, "RESET: розплавити імпульсом", size=10.5, color=RED))
    f.append(text(x + col_w / 2, top + 304, "і РІЗКО остудити → хаос «0».", size=10.5, color=RED))
    f.append(text(x + col_w / 2, top + 328, "SET: підігріти м'якше й дати", size=10.5, color=GREEN))
    f.append(text(x + col_w / 2, top + 344, "охолонути → кристал «1».", size=10.5, color=GREEN))
    f.append(text(x + col_w / 2, top + 372, "Пишемо ТЕПЛОМ від струму —", size=10.5, color=BLUE))
    f.append(text(x + col_w / 2, top + 388, "тому запис гарячий і жадібний.", size=10.5, color=BLUE))

    f.append(text(W / 2, top + panel_h + 26, "Усі три дають два чіткі рівні опору — лиш фізика різна: "
                  "магнетизм, рух атомних дефектів, плавлення-кристалізація.",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "three-mechanisms.svg"), W, H, *f)


# ── 3. Порівняння зі знайомими пам'ятями ─────────────────────────────────────
def fig_compare_table():
    W, H = 1080, 470
    f = [text(W / 2, 30, "Нові нелеткі пам'яті поряд зі знайомими",
              size=18, bold=True)]
    f.append(text(W / 2, 52, "MRAM, RRAM і PCM ціляться у «святий грааль»: швидкі, нелеткі, "
                  "побайтові й майже без зносу — але кожна зі своїм «але»",
                  size=12, color=MUTED, italic=True))

    x0 = 30
    col_axis = 150
    cols = ["SRAM", "DRAM", "Flash", "FRAM", "MRAM", "RRAM", "PCM"]
    col_colors = [MUTED, MUTED, RED, BLUE, GREEN, GREEN, GREEN]
    cw = 124
    y0 = 78
    rh = 44

    # шапка
    f.append(rect(x0, y0, col_axis, rh, fill="#eef0f4", stroke=MUTED, sw=1.4, rx=0))
    f.append(text(x0 + col_axis / 2, y0 + 28, "Вісь", size=12, color=INK, bold=True))
    for j, c in enumerate(cols):
        cx = x0 + col_axis + j * cw
        f.append(rect(cx, y0, cw, rh, fill="#eef0f4", stroke=MUTED, sw=1.4, rx=0))
        f.append(text(cx + cw / 2, y0 + 28, c, size=13, color=col_colors[j], bold=True))

    rows = [
        ("Що тримає біт", ["петля", "заряд", "заряд", "поляр.", "магніт", "місток", "фаза"],
         [MUTED, BLUE, BLUE, INK, INK, INK, INK]),
        ("Нелетка?", ["ні", "ні", "так", "так", "так", "так", "так"],
         [RED, RED, GREEN, GREEN, GREEN, GREEN, GREEN]),
        ("Запис побайтово?", ["так", "так", "блоки", "так", "так", "так", "так"],
         [GREEN, GREEN, RED, GREEN, GREEN, GREEN, GREEN]),
        ("Ресурс (циклів)", ["∞", "∞", "10⁴–10⁵", "10¹⁴", "10¹⁵+", "10⁶–10⁹", "10⁸–10⁹"],
         [GREEN, GREEN, RED, GREEN, GREEN, AMBER, AMBER]),
        ("Швидкість запису", ["нс", "нс", "мкс–мс", "нс", "нс", "~10нс", "~50нс"],
         [GREEN, GREEN, RED, GREEN, GREEN, GREEN, AMBER]),
        ("Щільність", ["низька", "висока", "висока", "низька", "середня", "висока", "висока"],
         [RED, GREEN, GREEN, RED, AMBER, GREEN, GREEN]),
        ("Зрілість", ["масово", "масово", "масово", "ніша", "є чипи", "рання", "була в Optane"],
         [GREEN, GREEN, GREEN, AMBER, GREEN, AMBER, MUTED]),
    ]
    for i, (axis, vals, vcolors) in enumerate(rows):
        y = y0 + rh * (i + 1)
        band = BG if i % 2 == 0 else "#fafafa"
        f.append(rect(x0, y, col_axis, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(text(x0 + 12, y + 28, axis, size=11.5, color=INK, anchor="start"))
        for j, v in enumerate(vals):
            cx = x0 + col_axis + j * cw
            f.append(rect(cx, y, cw, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
            fs = fit_font(v, cw - 12, 11.5, True)
            f.append(text(cx + cw / 2, y + 28, v, size=fs, color=vcolors[j], bold=True))

    # рамка
    f.append(rect(x0, y0, col_axis + len(cols) * cw, rh * (len(rows) + 1),
                  fill="none", stroke=MUTED, sw=1.6, rx=0))

    f.append(text(W / 2, y0 + rh * (len(rows) + 1) + 26,
                  "Три праві колонки — нові: усі нелеткі, побайтові й швидкі. MRAM уже в чипах; "
                  "RRAM пробивається; PCM сяйнула в Optane і згасла на ринку.",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "compare-new-memory.svg"), W, H, *f)


if __name__ == "__main__":
    fig_resistance_bit()
    fig_three_mechanisms()
    fig_compare_table()
    print("OK: figs у", IMG)
