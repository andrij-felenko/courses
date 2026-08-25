# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
BLUE_FILL  = "#eaf0fd"
LOCK_FILL  = "#eef1f4"
LOCK_LINE  = "#9aa3ad"
CHK_FILL   = "#f3ecfb"
CHK_LINE   = "#8b5cc7"
RED_FILL   = "#fdecea"


# ── 1. Каркас із дірками ─────────────────────────────────────────────────────
def fig_skeleton_holes():
    W, H = 1120, 660
    frags = []
    frags.append(text(W / 2, 40, "Каркас із дірками", size=18, bold=True))
    frags.append(text(W / 2, 62,
                      "незмінний порядок кроків, а два кроки — залишені нащадку",
                      size=12.5, color=MUTED))

    # рамка каркаса (лівий стовпчик)
    fx, fw = 84, 440
    fy, fh = 96, 452
    frags.append(rect(fx, fy, fw, fh, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(fx + fw / 2, fy + 26, "importFile(path)  —  шаблонний метод",
                      size=13, bold=True, color=NEG))
    frags.append(text(fx + fw / 2, fy + 45, "нащадок його НЕ підмінює", size=11, color=MUTED))

    cx = fx + fw / 2
    steps = [
        ("1   readFile(path)",           "спільний крок · замкнено",      LOCK_FILL, LOCK_LINE, False),
        ("2   parse(text) → записи",     "абстрактний · МУСИТЬ нащадок",  GREEN_FILL, FIELD,    True),
        ("3   лишити валідні [isValid]", "гачок · МОЖЕ підмінити",        BLUE_FILL,  NEG,      True),
        ("4   saveAll(записи)",          "спільний крок · замкнено",      LOCK_FILL, LOCK_LINE, False),
        ("5   log(скільки)",             "спільний крок · замкнено",      LOCK_FILL, LOCK_LINE, False),
    ]
    y0 = fy + 96
    dy = 70
    parse_y = parse_right = 0
    for i, (label, note, fill, stroke, bold) in enumerate(steps):
        y = y0 + i * dy
        b, bw, bh = textbox(cx, y, [label], size=12.5, bold=bold,
                            fill=fill, stroke=stroke, sw=(2.0 if bold else 1.5), min_w=340)
        frags.append(b)
        frags.append(text(cx, y + 24, note, size=10.5, color=MUTED))
        if i == 1:
            parse_y = y
            parse_right = cx + max(340, bw) / 2

    # праворуч — два нащадки, що дають свій parse
    frags.append(text(W * 0.83, fy + 26, "нащадки", size=14, bold=True, color=FIELD))
    subs = [("CsvImport", "parse: split(',')", 250),
            ("JsonImport", "parse: JSON.parse", 392)]
    for name, body, sy in subs:
        b, bw, bh = textbox(W * 0.83, sy, [name, body], size=12, bold=False,
                            fill=GREEN_FILL, stroke=FIELD, sw=1.6, min_w=230)
        frags.append(b)
        frags.append(arrow(W * 0.83 - bw / 2 - 6, sy, parse_right + 10, parse_y,
                           color=FIELD, sw=1.7))
    frags.append(text((parse_right + W * 0.83) / 2 + 6, 196,
                      "дають свій крок parse", size=11.5, bold=True, color=FIELD))

    by = H - 32
    frags.append(line(60, by - 24, W - 60, by - 24, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, by,
                      "каркас пишемо ОДИН раз; кожен нащадок дає лише свій крок і вставляє його в дірку",
                      size=12.5, bold=True))

    render(os.path.join(IMG, 'skeleton-holes.svg'), W, H, *frags)


# ── 2. Хто кого кличе: бібліотека проти каркаса ──────────────────────────────
def fig_inverted_control():
    W, H = 1100, 520
    frags = []
    frags.append(text(W / 2, 40, "Хто кого кличе", size=18, bold=True))
    frags.append(text(W / 2, 62,
                      "у каркасі керування перевернуте: не ти кличеш його — він кличе тебе",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 96, W / 2, H - 84, color="#d0d5db", sw=1.2, dash="4,6"))

    def panel(px, head, head_col, top_lines, top_fill, top_stroke,
              bot_lines, bot_fill, bot_stroke, arrow_col, arrow_note, foot):
        f = []
        f.append(text(px, 122, head, size=15, bold=True, color=head_col))
        top, tw, th = textbox(px, 188, top_lines, size=12.5, bold=True,
                              fill=top_fill, stroke=top_stroke, sw=1.9, min_w=270)
        bot, bw, bh = textbox(px, 338, bot_lines, size=12.5, bold=True,
                              fill=bot_fill, stroke=bot_stroke, sw=1.9, min_w=270)
        f.append(top)
        f.append(bot)
        f.append(arrow(px, 188 + th / 2, px, 338 - bh / 2, color=arrow_col, sw=1.9))
        f.append(text(px + max(270, tw) / 2 + 14, 265, arrow_note,
                      size=11.5, color=arrow_col, anchor="start"))
        f.append(text(px, H - 100, foot, size=12, color=MUTED))
        return f

    frags += panel(W * 0.26, "Бібліотека", NEG,
                   ["твій код", "керує потоком"], BLUE_FILL, NEG,
                   ["sort(), parse(), …", "бібліотека — служить"], LOCK_FILL, LOCK_LINE,
                   INK, "ти кличеш ↓", "ти вгорі — ти в керуванні")

    frags += panel(W * 0.74, "Каркас (шаблонний метод)", FIELD,
                   ["каркас: importFile()", "керує потоком"], LOCK_FILL, LOCK_LINE,
                   ["твій крок: parse()", "служить — заповнена дірка"], GREEN_FILL, FIELD,
                   FIELD, "каркас кличе ↓", "твій код унизу — тебе кличуть")

    frags.append(line(60, H - 64, W - 60, H - 64, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 36,
                      "«не телефонуй нам — ми зателефонуємо тобі»: керування переходить від твого коду до каркаса",
                      size=12.5, bold=True))

    render(os.path.join(IMG, 'inverted-control.svg'), W, H, *frags)


# ── 3. Шаблонний метод (спадкування) проти стратегії (композиція) ────────────
def fig_template_vs_strategy():
    W, H = 1160, 580
    frags = []
    frags.append(text(W / 2, 40, "Та сама змінність — двома способами", size=18, bold=True))
    frags.append(text(W / 2, 62,
                      "шаблонний метод веде варіант ВГОРУ спадкуванням; стратегія — ВБІК композицією",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 92, W / 2, H - 78, color="#d0d5db", sw=1.2, dash="4,6"))

    # ── ліворуч: шаблонний метод (спадкування) ──────────────────────────────
    lx = W * 0.26
    frags.append(text(lx, 118, "Шаблонний метод · спадкування", size=14, bold=True, color=NEG))
    base, bw, bh = textbox(lx, 188,
                           ["Importer  (предок)", "importFile(): каркас", "parse(): абстрактний"],
                           size=12, bold=True, fill="#ffffff", stroke=NEG, sw=1.9, min_w=310)
    frags.append(base)
    subL, slw, slh = textbox(lx - 112, 348, ["CsvImporter", "parse = …"],
                             size=11.5, fill=BLUE_FILL, stroke=NEG, sw=1.5, min_w=170)
    subR, srw, srh = textbox(lx + 112, 348, ["JsonImporter", "parse = …"],
                             size=11.5, fill=BLUE_FILL, stroke=NEG, sw=1.5, min_w=170)
    frags.append(subL)
    frags.append(subR)
    frags.append(arrow(lx - 112, 348 - slh / 2, lx - 40, 188 + bh / 2, color=NEG, sw=1.6))
    frags.append(arrow(lx + 112, 348 - srh / 2, lx + 40, 188 + bh / 2, color=NEG, sw=1.6))
    frags.append(text(lx, 250, "є-як (is-a)", size=11, color=MUTED))
    frags.append(text(lx, 420, "варіант = ПІДТИП", size=12.5, bold=True, color=NEG))
    frags.append(text(lx, 440, "обрано при створенні · цілий об'єкт", size=11, color=MUTED))

    # ── праворуч: стратегія (композиція) ────────────────────────────────────
    rx = W * 0.74
    frags.append(text(rx, 118, "Стратегія · композиція", size=14, bold=True, color=FIELD))
    ctx, cw, ch = textbox(rx - 36, 200,
                          ["Importer  (контекст)", "parser: Parser   ← поле",
                           "importFile(): parser.parse()"],
                          size=12, bold=True, fill="#ffffff", stroke=FIELD, sw=1.9, min_w=300)
    frags.append(ctx)
    strat, stw, sth = textbox(rx + 60, 360,
                              ["CsvParser / JsonParser", "підставний об'єкт"],
                              size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.6, min_w=250)
    frags.append(strat)
    frags.append(arrow(rx - 36, 200 + ch / 2, rx + 60, 360 - sth / 2, color=FIELD, sw=1.7))
    frags.append(text(rx - 150, 300, "тримає в полі (has-a)", size=11, color=MUTED, anchor="start"))
    frags.append(text(rx, 430, "варіант = ОБ'ЄКТ у полі", size=12.5, bold=True, color=FIELD))
    frags.append(text(rx, 450, "підставний у рантаймі · можна змінити", size=11, color=MUTED))

    frags.append(line(60, H - 62, W - 60, H - 62, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 34,
                      "жорсткість спадкування  ↔  гнучкість композиції: той самий вибір, різна ціна зміни",
                      size=12.5, bold=True))

    render(os.path.join(IMG, 'template-vs-strategy.svg'), W, H, *frags)


# ── 4. Родовід шаблонного методу (для hist-вставки) ─────────────────────────
def fig_lineage():
    W, H = 1080, 892
    cx = 668           # центр карток
    sx = 250           # вертикальна вісь часу
    frags = []
    frags.append(text(W / 2, 42, "Родовід шаблонного методу", size=18, bold=True))
    frags.append(text(W / 2, 65,
                      "спершу механізм і практика — патерн уже працює в каркасах; лише потім слова, а тоді й імʼя",
                      size=12.5, color=MUTED))
    frags.append(line(sx, 104, sx, 820, color="#cfd4da", sw=2.2))

    # (рік, [заголовок-жирний, опис], заливка, обвід)
    entries = [
        ("1951", ["Бібліотека підпрограм (EDSAC)",
                  "Вілкс · Вілер · Ґілл: повторно вживаний код, який кличеш ТИ"],
                 LOCK_FILL, LOCK_LINE),
        ("1967", ["Simula 67 — віртуальні процедури + спадкування",
                  "Даль і Нюгор дають механізм: предок «провалюється» в крок нащадка"],
                 FILL, MUTED),
        ("1983", ["«Не телефонуй нам — ми зателефонуємо тобі»",
                  "Річард Світ (Mesa / Tajo, Xerox PARC) — «закон Голлівуда»"],
                 BLUE_FILL, NEG),
        ("1985", ["MacApp (Apple) — перший великий каркас застосунку",
                  "каркас володіє циклом подій і сам кличе твої кроки"],
                 GREEN_FILL, FIELD),
        ("1988", ["ET++ (Цюрих): Вайнанд · Гамма · Марті — каркас у C++",
                  "Джонсон і Фут називають явище: «інверсія керування»"],
                 GREEN_FILL, FIELD),
        ("1994", ["«Банда чотирьох» називає атом: Шаблонний метод",
                  "і відносить його до ПОВЕДІНКОВИХ патернів"],
                 BG, NEG),
    ]
    y0, dy = 152, 130
    for i, (year, lines, fill, stroke) in enumerate(entries):
        y = y0 + i * dy
        l1, l2 = lines
        fs = 12.5
        w = max(770, max(text_width(l1, fs, True), text_width(l2, 11.5)) + 26)
        x = cx - w / 2
        h = 56
        frags.append(rect(x, y - h / 2, w, h, fill=fill, stroke=stroke, sw=1.9))
        frags.append(text(x + 15, y - 5, l1, size=fs, bold=True, anchor="start"))
        frags.append(text(x + 15, y + 16, l2, size=11.5, color=MUTED, anchor="start"))
        frags.append(line(sx + 11, y, x, y, color=stroke, sw=1.5))
        frags.append(circle(sx, y, 11, fill=fill, stroke=stroke, sw=2.6))
        frags.append(text(sx - 30, y + 5, year, size=16, bold=True, anchor="end"))

    frags.append(line(60, H - 58, W - 60, H - 58, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 30,
                      "патерн працював у каркасах ще до того, як дістав імʼя: механізм → практика → «інверсія керування» → «Шаблонний метод»",
                      size=12.5, bold=True))

    render(os.path.join(IMG, 'lineage.svg'), W, H, *frags)


# ── 5. NVI: ворота й дірка (для proj-nvi-idiom) ──────────────────────────────
def fig_nvi_gate():
    W, H = 1180, 760
    frags = []
    frags.append(text(W / 2, 40, "NVI: ворота й дірка", size=18, bold=True))
    frags.append(text(W / 2, 63,
                      "публічний невіртуальний каркас охоплює приватну віртуальну дірку — і перевірки навколо неї",
                      size=12.5, color=MUTED))

    # ворота — великий невіртуальний прямокутник
    gx, gy, gw, gh = 80, 100, 600, 600
    frags.append(rect(gx, gy, gw, gh, fill="#fbfcfd", stroke=NEG, sw=2.6))
    cx = gx + gw / 2   # 380
    frags.append(text(cx, gy + 28, "std::string render(fields) const", size=13.5, bold=True, color=NEG))
    frags.append(text(cx, gy + 50, "публічний · НЕвіртуальний — не перевизначити, не переставити",
                      size=11, color=MUTED))

    bands = [
        (["① передумова: fields не порожні"],                              CHK_FILL,  CHK_LINE,  False),
        (["② header() — спільний крок"],                                   LOCK_FILL, LOCK_LINE, False),
        (["③ renderBody(fields)   ← дірка", "приватна ВІРТУАЛЬНА · заповнює нащадок"], GREEN_FILL, FIELD, True),
        (["④ післяумова + інваріант результату"],                          CHK_FILL,  CHK_LINE,  False),
        (["⑤ footer() — спільний крок"],                                   LOCK_FILL, LOCK_LINE, False),
    ]
    y0, dy = 205, 92
    hole_y = hole_right = 0
    for i, (lines, fill, stroke, bold) in enumerate(bands):
        y = y0 + i * dy
        b, bw, bh = textbox(cx, y, lines, size=12.5, bold=bold, fill=fill, stroke=stroke,
                            sw=(2.2 if bold else 1.5), min_w=480)
        frags.append(b)
        if i == 2:
            hole_y = y
            hole_right = cx + max(480, bw) / 2
    frags.append(text(cx, gy + gh - 28, "порядок кроків зафіксовано у воротах — згори вниз",
                      size=11, color=MUTED))

    # нащадки праворуч, дотягуються лише до дірки
    frags.append(text(960, 300, "нащадки", size=14, bold=True, color=FIELD))
    subs = [("JsonReport", "renderBody → {…}", 350),
            ("TextReport", "renderBody → k: v", 430)]
    for name, body, sy in subs:
        b, bw, bh = textbox(960, sy, [name, body], size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.6, min_w=210)
        frags.append(b)
        frags.append(arrow(960 - bw / 2 - 8, sy, hole_right + 10, hole_y, color=FIELD, sw=1.7))
    frags.append(text(735, 358, "лише у дірку", size=11.5, bold=True, color=FIELD))

    by = H - 26
    frags.append(line(60, by - 22, W - 60, by - 22, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, by,
                      "нащадок дістає тільки дірку; каркас і перевірки виконуються неминуче",
                      size=12.5, bold=True))
    render(os.path.join(IMG, 'nvi-gate.svg'), W, H, *frags)


# ── 6. Публічний віртуальний проти NVI (для proj-nvi-idiom) ──────────────────
def fig_nvi_vs_public_virtual():
    W, H = 1180, 580
    frags = []
    frags.append(text(W / 2, 40, "Публічний віртуальний  проти  NVI", size=18, bold=True))
    frags.append(text(W / 2, 63,
                      "різниця не в іменах, а в тому, до чого нащадок фізично дотягується",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 92, W / 2, H - 84, color="#d0d5db", sw=1.2, dash="4,6"))

    # ── ліворуч: публічний віртуальний (крихко) ──
    lx = W * 0.27   # ~319
    frags.append(text(lx, 116, "публічний віртуальний render()", size=14, bold=True, color=POS))
    base, bw, bh = textbox(lx, 182, ["Report", "virtual render(){ header; …; footer }"],
                           size=12, bold=True, fill="#ffffff", stroke=LOCK_LINE, sw=1.7, min_w=330)
    frags.append(base)
    der, dw, dh = textbox(lx, 330, ["BrokenReport : Report", "render() override { return body; }"],
                          size=12, fill=RED_FILL, stroke=POS, sw=1.8, min_w=330)
    frags.append(der)
    frags.append(arrow(lx, 330 - dh / 2, lx, 182 + bh / 2, color=POS, sw=1.7))
    frags.append(text(lx + 12, 262, "override — заміняє ВЕСЬ метод", size=11, color=POS, anchor="start"))
    frags.append(text(lx, 430, "✗  забув header()/footer() → каркас зник", size=12, bold=True, color=POS))
    frags.append(text(lx, 452, "компілятор мовчить", size=11.5, color=MUTED))

    # ── праворуч: NVI (міцно) ──
    rx = W * 0.73   # ~861
    frags.append(text(rx, 116, "NVI — ворота невіртуальні", size=14, bold=True, color=FIELD))
    gate, gaw, gah = textbox(rx, 182, ["Report", "render() НЕвіртуальний · веде кроки"],
                             size=12, bold=True, fill="#ffffff", stroke=NEG, sw=1.9, min_w=330)
    frags.append(gate)
    hole, hw, hh = textbox(rx, 330, ["Good : Report", "renderBody() override — лише дірка"],
                           size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=330)
    frags.append(hole)
    frags.append(arrow(rx, 330 - hh / 2, rx, 182 + gah / 2, color=FIELD, sw=1.7))
    frags.append(text(rx - 12, 262, "заповнює лише приватну дірку", size=11, color=FIELD, anchor="end"))
    frags.append(text(rx, 430, "✓  каркас і перевірки виконуються завжди", size=12, bold=True, color=FIELD))
    frags.append(text(rx, 452, "немає super, який можна забути", size=11.5, color=MUTED))

    frags.append(line(60, H - 60, W - 60, H - 60, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 32,
                      "невіртуальні ворота не замінити: нащадок дістає тільки дірку",
                      size=12.5, bold=True))
    render(os.path.join(IMG, 'nvi-vs-public-virtual.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_skeleton_holes()
    fig_inverted_control()
    fig_template_vs_strategy()
    fig_lineage()
    fig_nvi_gate()
    fig_nvi_vs_public_virtual()
    print("figs done")
