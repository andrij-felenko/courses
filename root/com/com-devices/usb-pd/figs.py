# -*- coding: utf-8 -*-
"""Фігури до теми «USB Power Delivery».
Імпортує спільний svgkit зі scripts/ (НЕ переписувати тут). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

SINK = FIELD          # пристрій (sink) — зелений
SRC = POS             # джерело (source) — гарячий


# ── 1. Рукостискання: меню → запит → згода → нова напруга ────────────────────
def fig_handshake():
    W, H = 760, 430
    parts = []
    # дві колонки-учасники
    sx, dx = 175, 585
    parts.append(rect(sx - 80, 56, 160, 30, fill="#fdecea", stroke=SRC, sw=2))
    parts.append(text(sx, 76, "джерело", size=13, bold=True, color=SRC))
    parts.append(rect(dx - 80, 56, 160, 30, fill="#eaf3ea", stroke=SINK, sw=2))
    parts.append(text(dx, 76, "пристрій (sink)", size=13, bold=True, color=SINK))
    # лінії життя
    parts.append(line(sx, 86, sx, 392, color=MUTED, sw=1.4, dash="4 4"))
    parts.append(line(dx, 86, dx, 392, color=MUTED, sw=1.4, dash="4 4"))
    # під'єднання
    parts.append(text(W / 2, 112, "під'єднання (резистори CC) → на VBUS лише 5 В",
                      size=11.5, color=MUTED, italic=True))
    # повідомлення
    def msg(y, x1, x2, label, color):
        parts.append(line(x1, y, x2, y, color=color, sw=2.2))
        parts.append(arrow(x2 - 18, y, x2, y, color=color))
        parts.append(text((x1 + x2) / 2, y - 9, label, size=12, color=color, bold=True))
    msg(160, sx, dx, "Source_Capabilities — меню PDO", SRC)
    msg(205, dx, sx, "Request — «хочу профіль, напр. 20 В / 3 А»", SINK)
    msg(250, sx, dx, "Accept", SRC)
    parts.append(text(W / 2, 286, "VBUS плавно піднімається до 20 В", size=11.5,
                      color=MUTED, italic=True))
    msg(322, sx, dx, "PS_RDY — нова напруга стоїть", SRC)
    # контракт
    b, w, h = textbox(W / 2, 366, "КОНТРАКТ діє — і його можна переукласти будь-коли",
                      size=12.5, fill="#eaf3ea", stroke=SINK, bold=True, color=SINK)
    parts.append(b)
    render(os.path.join(IMG, "handshake.svg"), W, H, *parts,
           title="Рукостискання PD: меню → запит → згода → напруга")


# ── 2. Меню джерела: список PDO ──────────────────────────────────────────────
def fig_pdos():
    W, H = 720, 380
    parts = []
    parts.append(text(W / 2, 54, "Source_Capabilities — це список рядків PDO",
                      size=13, color=MUTED))
    rows = [
        ("5 В", "3 А", "обов'язковий — є завжди", "#eef2f7"),
        ("9 В", "3 А", "телефон", "#eef2f7"),
        ("15 В", "3 А", "", "#eef2f7"),
        ("20 В", "5 А", "ноутбук · стеля SPR 100 Вт", "#fdecea"),
        ("3.3–11 В", "≤ 3 А", "APDO — це PPS (діапазон)", "#eaf3ea"),
    ]
    x, y0, rw, rh = 90, 78, 540, 44
    for i, (v, a, note, col) in enumerate(rows):
        y = y0 + i * (rh + 8)
        parts.append(rect(x, y, rw, rh, fill=col, stroke=LINE, sw=1.4))
        parts.append(text(x + 70, y + rh / 2 + 5, v, size=14, bold=True, anchor="middle"))
        parts.append(line(x + 140, y + 8, x + 140, y + rh - 8, color=MUTED, sw=1))
        parts.append(text(x + 200, y + rh / 2 + 5, "до " + a, size=12.5, anchor="middle"))
        parts.append(line(x + 260, y + 8, x + 260, y + rh - 8, color=MUTED, sw=1))
        if note:
            parts.append(text(x + 275, y + rh / 2 + 5, note, size=11.5,
                              color=MUTED, anchor="start"))
    b, w, h = textbox(W / 2, 354,
                      "Пристрій читає меню й вибирає ОДИН профіль під свою потребу",
                      size=12.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "pdos.svg"), W, H, *parts,
           title="Меню джерела: кожен рядок PDO — напруга й ліміт струму")


# ── 3. Фіксовані сходинки проти PPS-діапазону ────────────────────────────────
def fig_fixed_vs_pps():
    W, H = 760, 380
    parts = []
    # ліва панель: фіксовані сходинки
    lx, ly, lw, lh = 40, 70, 330, 250
    parts.append(rect(lx, ly, lw, lh, fill="#eef2fb", stroke=NEG, sw=1.8))
    parts.append(text(lx + lw / 2, ly + 26, "Фіксовані профілі", size=13, bold=True, color=NEG))
    ax, ay = lx + 40, ly + 210
    parts.append(line(ax, ay, lx + lw - 20, ay, color=INK, sw=1.4))
    parts.append(line(ax, ay, ax, ly + 50, color=INK, sw=1.4))
    bars = [("5", 26), ("9", 56), ("15", 104), ("20", 150)]
    bx = ax + 24
    for lab, hgt in bars:
        parts.append(rect(bx, ay - hgt, 30, hgt, fill="none", stroke=NEG, sw=2))
        parts.append(text(bx + 15, ay - hgt - 7, lab + " В", size=10, color=NEG, bold=True))
        bx += 62
    parts.append(text(lx + lw / 2, ay + 30, "лише щаблі: 5 / 9 / 15 / 20", size=11, color=INK))
    # права панель: PPS пандус
    rx, ry, rw, rh = 390, 70, 330, 250
    parts.append(rect(rx, ry, rw, rh, fill="#eaf3ea", stroke=SINK, sw=1.8))
    parts.append(text(rx + rw / 2, ry + 26, "PPS (програмована)", size=13, bold=True, color=SINK))
    bx0, by0 = rx + 40, ry + 210
    parts.append(line(bx0, by0, rx + rw - 20, by0, color=INK, sw=1.4))
    parts.append(line(bx0, by0, bx0, ry + 50, color=INK, sw=1.4))
    pts = []
    for i in range(17):
        px = bx0 + 16 * i
        py = by0 - 12 - 8.5 * i
        pts.append("%.1f,%.1f" % (px, py))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), SINK))
    parts.append(text(rx + rw / 2, ry + 120, "плавно, кроком ~20 мВ", size=11, color=SINK, bold=True))
    parts.append(text(rx + rw / 2, by0 + 30, "будь-яка напруга в діапазоні + ліміт струму",
                      size=10.5, color=INK))
    # підсумок
    b, w, h = textbox(W / 2, 352,
                      ["Фіксовані — швидко, але грубо. PPS точна дрібним кроком:",
                       "нею заряджають батарею НАПРЯМУ (зарядка стає CC/CV-джерелом)."],
                      size=11.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "fixed-vs-pps.svg"), W, H, *parts,
           title="Фіксовані сходинки проти програмованої PPS")


# ── 4. Контракт: до згоди — лише 5 В ─────────────────────────────────────────
def fig_contract():
    W, H = 720, 320
    parts = []
    # вісь напруги в часі: 5 В до контракту, стрибок після
    x0, x1, y0 = 80, 660, 240
    parts.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    parts.append(line(x0, y0, x0, 70, color=INK, sw=1.6))
    parts.append(text(x0 - 10, 80, "В", size=12, color=MUTED, anchor="end"))
    # рівень 5 В
    xm = 380
    y5 = y0 - 40
    y20 = y0 - 150
    parts.append(line(x0, y5, xm, y5, color=NEG, sw=3))
    parts.append(text((x0 + xm) / 2, y5 - 12, "5 В — безпечний мінімум", size=12, color=NEG, bold=True))
    # стрибок
    parts.append(line(xm, y5, xm, y20, color=SRC, sw=3))
    parts.append(line(xm, y20, x1 - 10, y20, color=SRC, sw=3))
    parts.append(text((xm + x1) / 2, y20 - 12, "20 В × 5 А — лише за згодою", size=12, color=SRC, bold=True))
    # позначка моменту контракту
    parts.append(line(xm, y0 + 6, xm, 90, color=MUTED, sw=1.2, dash="4 3"))
    parts.append(text(xm, 84, "контракт укладено", size=11, color=MUTED, italic=True))
    parts.append(text(x0 + 6, y0 + 22, "під'єднання", size=10.5, color=MUTED, anchor="start"))
    parts.append(text(x1 - 10, y0 + 22, "час →", size=11, color=MUTED, anchor="end"))
    # аварійний хід
    b, w, h = textbox(W / 2, 292,
                      "Збій посеред контракту → hard reset: різко назад на 5 В і переговори з нуля",
                      size=12, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "contract.svg"), W, H, *parts,
           title="До контракту — лише 5 В; вище — тільки за згодою")


# ── 5. EPR: три умови й стеля 240 Вт ─────────────────────────────────────────
def fig_epr():
    W, H = 720, 350
    parts = []
    # сходи потужності SPR → EPR
    x0, y0 = 70, 250
    parts.append(line(x0, y0, 660, y0, color=INK, sw=1.4))
    parts.append(line(x0, y0, x0, 70, color=INK, sw=1.4))
    steps = [("5", 18, NEG), ("9", 34, NEG), ("15", 56, NEG), ("20", 78, NEG),
             ("28", 110, SRC), ("36", 142, SRC), ("48", 175, SRC)]
    bx = x0 + 26
    for lab, hgt, col in steps:
        parts.append(rect(bx, y0 - hgt, 34, hgt, fill="none", stroke=col, sw=2))
        parts.append(text(bx + 17, y0 - hgt - 7, lab, size=10, color=col, bold=True))
        bx += 50
    parts.append(text(x0 + 130, y0 + 20, "SPR ≤ 100 Вт", size=11.5, color=NEG, bold=True))
    parts.append(text(x0 + 460, y0 + 20, "EPR ≤ 240 Вт", size=11.5, color=SRC, bold=True))
    parts.append(text(x0 + 17, 84, "В", size=11, color=MUTED))
    # три умови
    b, w, h = textbox(W / 2, 300,
                      ["EPR (28/36/48 В, до 240 Вт) вмикається лише коли готові ВСІ троє:",
                       "джерело · пристрій · кабель з e-marker. Бракує когось — лишаються SPR-щаблі."],
                      size=11.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "epr.svg"), W, H, *parts,
           title="EPR: до 48 В і 240 Вт — за згоди всіх трьох")


# ── 6. Три шляхи дати пристрою PD ────────────────────────────────────────────
def fig_implement():
    W, H = 760, 320
    parts = []
    cards = [
        ("«Тригер»", ["просить ОДНУ", "фіксовану напругу", "(напр. 12 В)", "— без коду"], SINK),
        ("PD-контролер", ["окремий чип веде", "переговори;", "МК командує", "по шині"], NEG),
        ("МК + PD-стек", ["процесор сам", "говорить PD", "(потрібні PHY", "і програма)"], SRC),
    ]
    cw, gap = 220, 25
    x = (W - 3 * cw - 2 * gap) / 2
    for title_, lines, col in cards:
        parts.append(rect(x, 70, cw, 170, fill="#f7f9fb", stroke=col, sw=2))
        parts.append(text(x + cw / 2, 98, title_, size=14, bold=True, color=col))
        parts.append(line(x + 20, 110, x + cw - 20, 110, color=col, sw=1))
        for i, ln in enumerate(lines):
            parts.append(text(x + cw / 2, 138 + i * 22, ln, size=12, color=INK))
        x += cw + gap
    # вісь складності
    parts.append(text(W / 2, 268, "← простіше    ·    складність і гнучкість    ·    гнучкіше →",
                      size=12, color=MUTED, italic=True))
    b, w, h = textbox(W / 2, 298,
                      "Не ускладнюй без потреби: кожен зайвий рівень розуму — ще щось, що може зламатися",
                      size=12, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "implement.svg"), W, H, *parts,
           title="Три шляхи дати пристрою PD")


if __name__ == "__main__":
    fig_handshake()
    fig_pdos()
    fig_fixed_vs_pps()
    fig_contract()
    fig_epr()
    fig_implement()
    print("done")
