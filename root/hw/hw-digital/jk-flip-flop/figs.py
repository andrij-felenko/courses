# -*- coding: utf-8 -*-
"""Фігури до теми «JK-тригер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальна геометрія (не текстові рамки) ──────────────────────────────────
def wire(x1, y1, x2, y2, color=INK, sw=1.8):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, color, sw))


def node(cx, cy, r=3.0):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s"/>'
            % (cx, cy, r, INK, INK))


def and_gate(x, y, w=34, h=40, label=None):
    """Вентиль AND: пласка спинка ліворуч + півколо праворуч. Повертає (svg, out_x, out_y)."""
    r = h / 2.0
    sx = x + w - r
    d = ('<path d="M %.1f,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L %.1f,%.1f Z" '
         'fill="%s" stroke="%s" stroke-width="2"/>'
         % (x, y, sx, y, r, r, sx, y + h, x, y + h, FILL, INK))
    if label:
        d += text(x + w * 0.42, y + r + 4, label, size=11, bold=True)
    return d, x + w, y + r


def clk_triangle(cx, cy):
    """Знак «по фронту»: маленький трикутник «❯» на тактовому вході."""
    return ('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
            'stroke-width="1.8"/>' % (cx - 6, cy - 7, cx + 6, cy, cx - 6, cy + 7, INK))


def caption(W, sub):
    return text(W / 2, 50, sub, size=12, color=MUTED, italic=True)


# ── Фіг.1: JK = SR + зворотний зв'язок виходів на входи ──────────────────────
def fig_from_sr():
    W, H = 900, 380
    f = [caption(W, "заводимо Q̄ на верхній AND, а Q — на нижній: за J=K=1 щоразу набігає команда «перекинутися»")]

    # входи J, такт, K
    f.append(text(96, 138, "J", size=14, color=POS, anchor="end", bold=True))
    f.append(wire(102, 134, 210, 134))
    f.append(text(96, 288, "K", size=14, color=NEG, anchor="end", bold=True))
    f.append(wire(102, 284, 210, 284))
    f.append(text(96, 211, "такт", size=12, anchor="end", bold=True))
    f.append(wire(102, 207, 150, 207))
    f.append(node(150, 207))
    f.append(wire(150, 207, 150, 150)); f.append(wire(150, 150, 210, 150))
    f.append(wire(150, 207, 150, 268)); f.append(wire(150, 268, 210, 268))

    # два AND з трьома входами (третій — зворотний зв'язок)
    g1, ox1, oy1 = and_gate(210, 118, h=44); f.append(g1)
    f.append(text(232, 112, "J·такт·Q̄", size=9, color=MUTED))
    g2, ox2, oy2 = and_gate(210, 262, h=44); f.append(g2)
    f.append(text(232, 320, "K·такт·Q", size=9, color=MUTED))
    f.append(wire(ox1, oy1, 330, 168)); f.append(wire(ox2, oy2, 330, 252))

    # засувка SR
    f.append(rect(330, 165, 130, 90, fill="#eef7ee", stroke=INK, sw=2, rx=8))
    f.append(text(395, 205, "SR-засувка", size=12.5, bold=True))
    f.append(text(395, 224, "(S=верх, R=низ)", size=9.5, color=MUTED))
    # виходи Q, Q̄
    f.append(wire(460, 185, 540, 185)); f.append(text(546, 189, "Q", size=14, color=FIELD, anchor="start", bold=True))
    f.append(wire(460, 235, 540, 235)); f.append(text(546, 239, "Q̄", size=13, color=FIELD, anchor="start", bold=True))

    # зворотний зв'язок: Q̄ → верхній AND, Q → нижній AND
    f.append(node(520, 235))                       # Q̄ вниз-ліворуч на верхній AND
    f.append(wire(520, 235, 520, 96)); f.append(wire(520, 96, 175, 96))
    f.append(wire(175, 96, 175, 122)); f.append(wire(175, 122, 210, 122))
    f.append(text(300, 90, "Q̄ → верхній AND", size=9.5, color=MUTED))
    f.append(node(505, 185))                        # Q вниз на нижній AND
    f.append(wire(505, 185, 505, 344)); f.append(wire(505, 344, 175, 344))
    f.append(wire(175, 344, 175, 296)); f.append(wire(175, 296, 210, 296))
    f.append(text(300, 340, "Q → нижній AND", size=9.5, color=MUTED))

    box = fitbox(610, 118, 270, 174,
                 "хитрість: заборона зникає сама\n"
                 "S=J·такт·Q̄, R=K·такт·Q\n"
                 "коли Q=1 → нижній AND дозволено,\n"
                 "верхній — ні (бо Q̄=0)\n"
                 "тож S і R НЕ бувають 1 разом\n"
                 "а J=K=1 щоразу шле «перекинути»",
                 size=10.8, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10)
    f.append(box)
    render(os.path.join(IMG, "from-sr.svg"), W, H, *f,
           title="JK з SR: зворотний зв'язок прибирає заборонений стан")


# ── Фіг.2: чотири режими, наголос на toggle ─────────────────────────────────
def fig_cases():
    W, H = 900, 330
    f = [caption(W, "три режими — як у SR (тримати / set / reset); четвертий, J=K=1, — новий: перекинутися")]

    cells = [
        ("J=0  K=0", "тримати", "Q лишається", "#f4f6f8", INK),
        ("J=1  K=0", "set", "Q → 1", "#eef7ee", FIELD),
        ("J=0  K=1", "reset", "Q → 0", "#eef4ff", NEG),
        ("J=1  K=1", "перекинути", "Q → Q̄", "#fdf0ea", POS),
    ]
    x0, w, gap = 70, 180, 20
    for i, (inp, name, eff, bg, col) in enumerate(cells):
        x = x0 + i * (w + gap)
        f.append(rect(x, 90, w, 150, fill=bg, stroke=col, sw=2, rx=10))
        f.append(text(x + w / 2, 122, inp, size=14, bold=True))
        f.append(line(x + 18, 134, x + w - 18, 134, color=col, sw=1))
        f.append(text(x + w / 2, 168, name, size=15, color=col, bold=True))
        f.append(text(x + w / 2, 200, eff, size=13))
    # підкреслити toggle як новизну
    f.append(text(x0 + 3 * (w + gap) + w / 2, 228, "★ новий режим", size=10.5, color=POS, italic=True))
    f.append(text(W / 2, 288,
                  "toggle (перекинути) — те, чого SR-засувка не вміла: за J=K=1 вихід щотакту міняється на протилежний",
                  size=12, bold=True))
    render(os.path.join(IMG, "cases.svg"), W, H, *f,
           title="Чотири режими JK-тригера: тримати · set · reset · перекинути")


# ── Фіг.3: race-around на широкому імпульсі такту ───────────────────────────
def fig_race():
    W, H = 900, 380
    f = [caption(W, "поки такт високий і J=K=1, майстер-слейв не рятує «прозорий» тригер: вихід перекидається знову й знову")]

    x0, x1 = 130, 850
    # такт — один довгий високий імпульс (ширший за час перемикання)
    f.append(text(96, 118, "такт", size=13, anchor="end", bold=True))
    f.append(line(x0, 130, x1, 130, color="#e4e4e4", sw=1))
    clk = "130,130 260,130 260,96 620,96 620,130 850,130"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (clk, INK))
    f.append(line(260, 92, 260, 300, color=MUTED, sw=1, dash="3 3"))
    f.append(line(620, 92, 620, 300, color=MUTED, sw=1, dash="3 3"))
    f.append(text(440, 88, "такт високий увесь цей час, J=K=1", size=10.5, color=POS, italic=True))

    # J=K=1 (обидва в 1)
    f.append(text(96, 200, "J=K", size=13, color=NEG, anchor="end", bold=True))
    f.append(line(x0, 212, x1, 212, color="#e4e4e4", sw=1))
    f.append('<polyline points="130,212 130,180 850,180" fill="none" stroke="%s" stroke-width="2.4"/>' % NEG)

    # Q — багаторазово перекидається, поки такт високий (осциляція)
    f.append(text(96, 292, "Q", size=13, color=FIELD, anchor="end", bold=True))
    f.append(line(x0, 304, x1, 304, color="#e4e4e4", sw=1))
    # осциляція між 260 і 620
    q = "130,304 260,304 260,272 320,272 320,304 380,304 380,272 440,272 440,304 500,304 500,272 560,272 560,304 620,304 620,272 850,272"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (q, FIELD))
    f.append(text(440, 262, "Q скаче туди-сюди — скільки встигне за час імпульсу", size=10.5, color=POS, italic=True))

    box = fitbox(150, 318, 620, 52,
                 "«гонитва по колу» (race-around): вихід біжить назад на вхід і за широкий\n"
                 "рівень такту перекидається кілька разів — кінцевий стан невизначений.\n"
                 "Лік: захоплення по ФРОНТУ (справжній edge-тригер)",
                 size=11, fill="#fdf0ea", stroke=POS, sw=1.6, rx=10)
    f.append(box)
    render(os.path.join(IMG, "race-around.svg"), W, H, *f,
           title="Проблема «гонитви по колу»: чому JK будують по фронту, а не по рівню")


# ── Фіг.4: символ + застосування (÷2 з toggle) ──────────────────────────────
def fig_symbol_divide():
    W, H = 900, 360
    f = [caption(W, "символ: входи J, K, тактовий трикутник, виходи Q і Q̄; J=K=1 робить дільник частоти на 2")]

    # символ JK
    f.append(rect(150, 110, 120, 150, fill=FILL, stroke=INK, sw=2, rx=6))
    f.append(text(166, 142, "J", size=14, anchor="start", color=POS, bold=True))
    f.append(text(166, 232, "K", size=14, anchor="start", color=NEG, bold=True))
    f.append(text(254, 142, "Q", size=14, color=FIELD, anchor="end", bold=True))
    f.append(text(254, 232, "Q̄", size=13, color=FIELD, anchor="end", bold=True))
    f.append(clk_triangle(156, 187))
    f.append(text(170, 191, "clk", size=10.5, anchor="start"))
    f.append(text(210, 100, "JK-тригер", size=12.5, bold=True))
    # виводи
    f.append(wire(90, 142, 150, 142)); f.append(text(84, 146, "J", size=14, color=POS, anchor="end", bold=True))
    f.append(wire(90, 187, 150, 187)); f.append(text(84, 191, "clk", size=13, anchor="end", bold=True))
    f.append(wire(90, 232, 150, 232)); f.append(text(84, 236, "K", size=14, color=NEG, anchor="end", bold=True))
    f.append(wire(270, 142, 330, 142)); f.append(text(336, 146, "Q", size=14, color=FIELD, anchor="start", bold=True))
    f.append(text(210, 288, "J=K=1 → щофронт Q перекидається", size=10.5, color=MUTED, italic=True))

    # маленька часова діаграма праворуч: clk удвічі частіший за Q
    bx0, bx1 = 470, 850
    f.append(text(438, 132, "clk", size=12, anchor="end", bold=True))
    f.append(line(bx0, 144, bx1, 144, color="#e4e4e4", sw=1))
    clk = "470,144 500,144 500,116 545,116 545,144 590,144 590,116 635,116 635,144 680,144 680,116 725,116 725,144 770,144 770,116 815,116 815,144 850,144"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (clk, INK))
    # робочі фронти
    for ex in (500, 590, 680, 770):
        f.append(text(ex, 110, "▲", size=9, color=POS, bold=True))

    f.append(text(438, 216, "Q", size=12, color=FIELD, anchor="end", bold=True))
    f.append(line(bx0, 228, bx1, 228, color="#e4e4e4", sw=1))
    # Q перемикається на кожному ▲ → удвічі повільніший
    q = "470,228 500,228 500,200 590,200 590,228 680,228 680,200 770,200 770,228 850,228"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (q, FIELD))
    f.append(text(660, 258, "Q удвічі повільніший за такт — це дільник частоти ÷2", size=11, bold=True))

    render(os.path.join(IMG, "symbol-divide.svg"), W, H, *f,
           title="Символ JK і його коронний фокус: перемикач-дільник частоти")


# ── Фіг.5 (до історичної вставки): дорога від прозорого тригера до фронту ────
def fig_timeline_ms():
    W, H = 860, 470
    f = [text(W / 2, 30, "Як тригер навчився клацати рівно раз за такт", size=17, bold=True),
         text(W / 2, 51,
              "ланцюг рішень: зворотний зв'язок прибирає заборону, але породжує гонитву — її гасить майстер-слейв",
              size=11, color=MUTED, italic=True)]
    ax = 250
    f.append(line(ax, 86, ax, 430, color=MUTED, sw=3))
    nodes = [
        ("крок 1", "SR-засувка", "S=set, R=reset — але пара S=R=1 заборонена: суперечлива команда ламає комірку", False),
        ("крок 2", "зворотний зв'язок → JK", "виходи заведено назад на входи через AND: S і R ніколи не разом — заборона зникає", False),
        ("халепа", "гонитва по колу", "та сама петля: за J=K=1 прозорий тригер біжить сам за собою, поки такт високий", True),
        ("лік #1", "майстер-слейв", "дві засувки в протифазі; відкрита завжди одна → за такт рівно одне оновлення", False),
        ("лік #2", "прямий edge-тригер", "ловить лише коротку мить фронту; майстер-слейв стає необов'язковим (та лишається в старих IC)", False),
    ]
    y = 120
    dy = 74
    for when, title, desc, hot in nodes:
        col = POS if hot else INK
        if hot:
            f.append(circle(ax, y, 10, fill=BG, stroke=POS, sw=3.2))
            f.append(circle(ax, y, 4.5, fill=POS, stroke=POS, sw=1))
        else:
            f.append(circle(ax, y, 7, fill=BG, stroke=INK, sw=2.6))
        f.append(text(ax - 22, y + 5, when, size=12, color=MUTED, anchor="end", bold=True))
        f.append(text(ax + 24, y - 4, title, size=14.5, color=col, anchor="start", bold=True))
        f.append(text(ax + 24, y + 15, desc, size=11, color=INK, anchor="start", italic=True))
        y += dy
    render(os.path.join(IMG, "timeline-ms.svg"), W, H, *f)


if __name__ == "__main__":
    fig_from_sr()
    fig_cases()
    fig_race()
    fig_symbol_divide()
    fig_timeline_ms()
    print("OK: 5 figures ->", IMG)
