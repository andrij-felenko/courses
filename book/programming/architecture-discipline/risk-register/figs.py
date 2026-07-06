# -*- coding: utf-8 -*-
"""Фігури до статті «Ризик-реєстр як живий артефакт». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: сітка ризиків (ймовірність × вплив) з чотирма діями ────────────
def fig_grid():
    W, H = 720, 560
    # координати сітки
    gx, gy = 150, 90          # лівий-верхній кут сітки
    gw, gh = 470, 380         # розмір поля
    frags = []

    # осі-підписи
    frags.append(text(gx + gw / 2, gy + gh + 78, "Вплив, якщо станеться  →", size=15, bold=True))
    # вертикальний підпис осі ліворуч
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
                 '↑  Імовірність</text>' % (gx - 82, gy + gh / 2, FONT, INK, gx - 82, gy + gh / 2))

    # чотири клітини 2×2
    cw, ch = gw / 2, gh / 2
    cells = [
        # (col, row, заливка, назва дії, колір рамки)
        (0, 0, "#fdecea", "СТЕЖ І ГОТУЙ ПЛАН\n(висока ймовірн. ×\nвеликий удар)", POS),
        (1, 0, "#fef6e7", "СТЕЖ БЛИЗЬКО\n(рідко, але\nбило б боляче)", "#b8860b"),
        (0, 1, "#eaf3ec", "ПОГЛИНЬ У РОБОТІ\n(часто, але\nдрібно)", FIELD),
        (1, 1, "#eef1f5", "ПРИЙМИ Й ЗАБУДЬ\n(навряд і\nне страшно)", MUTED),
    ]
    for col, row, fill, label, br in cells:
        x = gx + col * cw
        y = gy + row * ch
        frags.append(rect(x, y, cw, ch, fill=fill, stroke=br, sw=2, rx=8))
        frags.append(fitbox(x + 12, y + ch / 2 - 34, cw - 24, 68, label,
                            size=13, fill="none", stroke="none", bold=True, color=INK))

    # мітки країв осей
    frags.append(text(gx + cw / 2, gy + gh + 52, "малий", size=12, color=MUTED))
    frags.append(text(gx + cw + cw / 2, gy + gh + 52, "великий", size=12, color=MUTED))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">низька</text>'
                 % (gx - 40, gy + gh - ch / 2, FONT, MUTED, gx - 40, gy + gh - ch / 2))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">висока</text>'
                 % (gx - 40, gy + ch / 2, FONT, MUTED, gx - 40, gy + ch / 2))

    render(os.path.join(IMG, "grid.svg"), W, H, *frags,
           title="Куди тягнути увагу: ймовірність × вплив")


# ── Фігура 2: живий реєстр (петля станів) проти мертвого ─────────────────────
def fig_living():
    W, H = 760, 470
    frags = []

    # ── зверху: живий цикл ──
    frags.append(text(200, 58, "ЖИВИЙ реєстр — стани течуть", size=15, bold=True, color=FIELD))
    cy = 150
    xs = [110, 300, 490]
    labels = ["ВІДКРИТИЙ\nвиявили, оцінили", "У РОБОТІ\nдіємо, збиваємо", "ЗАКРИТИЙ\nминув або\nстався"]
    bw, bh = 150, 66
    boxes = []
    for x, lab in zip(xs, labels):
        frags.append(fitbox(x - bw / 2, cy - bh / 2, bw, bh, lab, size=12,
                            fill="#eaf3ec", stroke=FIELD, sw=2, bold=True))
        boxes.append((x, cy))
    # стрілки між ними
    frags.append(arrow(xs[0] + bw / 2, cy, xs[1] - bw / 2, cy, color=FIELD, sw=2))
    frags.append(arrow(xs[1] + bw / 2, cy, xs[2] - bw / 2, cy, color=FIELD, sw=2))
    # петля повернення (переоцінка) — дугою зверху
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5 4"/>'
                 % (xs[2], cy - bh / 2, xs[2], cy - 72, xs[0], cy - 72, xs[0], cy - bh / 2, FIELD))
    frags.append(text((xs[0] + xs[2]) / 2, cy - 78, "щотижня перечитуємо: оцінки зсунулись?",
                     size=12, color=FIELD, italic=True))
    # нові ризики вливаються
    frags.append(arrow(xs[0], cy + bh / 2 + 40, xs[0], cy + bh / 2 + 6, color=FIELD, sw=2))
    frags.append(text(xs[0], cy + bh / 2 + 58, "нові ризики", size=12, color=FIELD))
    # закриті йдуть у пам'ять
    frags.append(arrow(xs[2], cy + bh / 2 + 6, xs[2], cy + bh / 2 + 40, color=MUTED, sw=1.8))
    frags.append(text(xs[2], cy + bh / 2 + 58, "в архів, з уроком", size=12, color=MUTED))

    # роздільник
    frags.append(line(40, 300, W - 40, 300, color="#d0d0d0", sw=1.2, dash="4 4"))

    # ── знизу: мертвий реєстр ──
    frags.append(text(230, 348, "МЕРТВИЙ реєстр — таблиця пилюки", size=15, bold=True, color=MUTED))
    dcy = 410
    frags.append(fitbox(90, dcy - 30, 250, 60,
                        "написали раз на старті", size=13, fill=FILL, stroke=MUTED, sw=1.8))
    # перекреслена стрілка — нічого не тече
    frags.append(line(345, dcy, 430, dcy, color="#c0392b", sw=2))
    frags.append(text(388, dcy - 12, "×", size=22, color="#c0392b", bold=True))
    frags.append(fitbox(435, dcy - 30, 250, 60,
                        "більше не відкрили", size=13, fill=FILL, stroke=MUTED, sw=1.8))

    render(os.path.join(IMG, "living.svg"), W, H, *frags)


# ── Фігура 3: анатомія одного рядка реєстру ─────────────────────────────────
def fig_row():
    W, H = 720, 430
    frags = []
    # один рядок як картка з полями
    cols = [
        ("Опис ризику", "«Vendor-API\nвідмовить під\nпіковим навант.»", 172),
        ("Ймовір.", "середня", 92),
        ("Вплив", "великий", 92),
        ("Ознака-тригер", "p95 latency\n> 800 мс", 132),
        ("Хто веде", "Оля,\nдо 12 черв.", 110),
    ]
    x = 40
    top = 120
    rowh = 108
    frags.append(text(W / 2, 58, "Один рядок реєстру: не «страшно», а що робити",
                     size=16, bold=True))
    for head, body, w in cols:
        # шапка
        frags.append(rect(x, top, w, 34, fill="#eef1f5", stroke=LINE, sw=1.5, rx=6))
        frags.append(fitbox(x + 4, top + 3, w - 8, 28, head, size=12, fill="none",
                            stroke="none", bold=True))
        # тіло
        frags.append(fitbox(x, top + 40, w, rowh - 40, body, size=12,
                            fill=FILL, stroke=LINE, sw=1.4))
        x += w + 8

    # пояснення знизу — що робить рядок «живим»
    ey = top + rowh + 60
    frags.append(fitbox(40, ey, 320, 76,
                        "БЕЗ тригера й власника —\nце просто страшилка:\nніхто не знає, коли бити\nна сполох і хто діє",
                        size=13, fill="#fdecea", stroke=POS, sw=1.8, color=INK))
    frags.append(fitbox(390, ey, 290, 76,
                        "З тригером і власником —\nце план: ознака вмикає\nдію, людина відповідає",
                        size=13, fill="#eaf3ec", stroke=FIELD, sw=1.8, color=INK))

    render(os.path.join(IMG, "row.svg"), W, H, *frags)


# ── Фігура 4 (hist): три течії, що сходяться в практику реєстру ──────────────
def fig_timeline():
    W, H = 940, 560
    frags = []

    frags.append(text(W / 2, 32, "Три течії, з яких визрів реєстр ризиків",
                     size=17, bold=True))

    # спільна вісь часу знизу
    ax_y = 470
    x0, x1 = 70, 870
    frags.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.5))
    for yr, xx in [("1987", 150), ("1989", 300), ("1996", 470), ("2003", 640), ("2004", 720)]:
        frags.append(line(xx, ax_y - 5, xx, ax_y + 5, color=MUTED, sw=1.5))
        frags.append(text(xx, ax_y + 22, yr, size=12, color=MUTED, bold=True))
    frags.append(text(x1 - 6, ax_y + 22, "рік →", size=11, color=MUTED, anchor="end"))

    # ── смуга 1: PMBOK (американська методологія) ──
    y1 = 95
    frags.append(text(x0, y1 - 24, "PMBOK — американська методологія (ризик росте до центральної галузі)",
                     size=12, color=NEG, bold=True, anchor="start"))
    steps1 = [
        (150, "білий папір\n1987", "#eaf0fd"),
        (470, "Guide, 1-е вид.\n1996 · ризик — 1 з 9 галузей", "#eaf0fd"),
        (720, "3-є вид. 2004\nризик — центральна галузь", "#eaf0fd"),
    ]
    prev = None
    for xx, lab, fill in steps1:
        body, bw, bh = textbox(xx, y1, lab, size=11, fill=fill, stroke=NEG, sw=1.6)
        if prev is not None:
            frags.append(arrow(prev, y1, xx - bw / 2, y1, color=NEG, sw=1.6))
        frags.append(body)
        prev = xx + bw / 2

    # ── смуга 2: PROMPT → PRINCE → PRINCE2 (британський стандарт) ──
    y2 = 210
    frags.append(text(x0, y2 - 26, "PROMPT → PRINCE → PRINCE2 — британський урядовий стандарт (реєстр = обов'язковий продукт)",
                     size=12, color=POS, bold=True, anchor="start"))
    steps2 = [
        (150, "PROMPT II\n(Simpact)", "#fdecea"),
        (300, "PRINCE\nCCTA, 1989", "#fdecea"),
        (470, "PRINCE2, 1996\nреєстр ризиків —\nуправл. продукт", "#fdecea"),
    ]
    prev = None
    for xx, lab, fill in steps2:
        body, bw, bh = textbox(xx, y2, lab, size=11, fill=fill, stroke=POS, sw=1.6)
        if prev is not None:
            frags.append(arrow(prev, y2, xx - bw / 2, y2, color=POS, sw=1.6))
        frags.append(body)
        prev = xx + bw / 2

    # ── смуга 3: RAID (низова практика) ──
    y3 = 320
    frags.append(text(x0, y3 - 22, "RAID — низова практика без єдиного автора",
                     size=12, color=MUTED, bold=True, anchor="start"))
    body, bw, bh = textbox(150, y3,
                           "журнал R·A·I·D\nризики · припущення ·\nпроблеми · залежності",
                           size=11, fill=FILL, stroke=MUTED, sw=1.6)
    frags.append(body)
    frags.append(text(150 + bw / 2 + 150, y3, "склалося знизу, без дати й патенту",
                     size=11, color=MUTED, italic=True, anchor="middle"))

    # ── смуга 4: «Вальс із ведмедями» (програмна інженерія) ──
    y4 = 400
    body, bw, bh = textbox(640, y4,
                           "«Вальс із ведмедями»\nDeMarco & Lister · Dorset House · 2003\nпетля дій + 5 ядрових ризиків ПЗ",
                           size=11, fill="#eaf3ec", stroke=FIELD, sw=1.8, bold=False)
    frags.append(body)
    frags.append(text(640, y4 - bh / 2 - 10, "мова ризику для програмної інженерії",
                     size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_grid()
    fig_living()
    fig_row()
    fig_timeline()
    print("figs done")
