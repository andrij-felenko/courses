# -*- coding: utf-8 -*-
"""Фігури до теми «Архітектура BMS: монітор комірок, ізоляція, контактор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_OK   = FIELD     # норма — зелений
C_BAD  = POS       # за межею — червоний/гарячий
C_LOW  = NEG       # просіла комірка — синій
GOLD   = "#caa24a"


# ── 1. Чому міряти кожну комірку, а не пакет ─────────────────────────────────
def fig_why_monitor():
    """Сума по пакету «в нормі», та всередині одна комірка перезаряджена,
    інша висаджена. Середнє по стеку — сліпе до окремої комірки."""
    W, H = 760, 430
    f = [text(W / 2, 30, "Чому пакет «у нормі», а батарея в небезпеці", size=16, bold=True)]
    # чотири комірки послідовно, напруги різні
    cells = [3.7, 4.3, 3.7, 3.0]      # друга перезаряджена, остання висаджена
    states = [C_OK, C_BAD, C_OK, C_LOW]
    notes = ["норма", "перезаряд!", "норма", "висаджена!"]
    cw, ch = 120, 150
    gap = 30
    x0 = (W - 4 * cw - 3 * gap) / 2
    cy = 80
    for i, (v, col, nt) in enumerate(zip(cells, states, notes)):
        cx = x0 + i * (cw + gap)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2.2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="6" fill="%s" fill-opacity="0.16"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 23, "комірка %d" % (i + 1), size=12, color=col, bold=True))
        f.append(text(cx + cw / 2, cy + 80, "%.1f В" % v, size=26, color=col, bold=True))
        f.append(text(cx + cw / 2, cy + 122, nt, size=11, color=col, bold=True))
        if i < 3:
            f.append(line(cx + cw, cy + ch / 2, cx + cw + gap, cy + ch / 2, color=INK, sw=2))
    # сумарна напруга пакета
    total = sum(cells)
    sy = cy + ch + 56
    f.append(fitbox(x0, sy, 4 * cw + 3 * gap, 30,
                    "Сума по пакету: %.1f В — «середня» комірка 3.675 В, наче все гаразд."
                    % total, size=11, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(fitbox(x0, sy + 42, 4 * cw + 3 * gap, 30,
                    "Та комірка 2 вже за межею (загроза розгону), а комірка 4 вбита глибоким розрядом.",
                    size=11, fill="#fdf3f2", stroke=C_BAD, sw=1.4))
    render(os.path.join(IMG, "why-monitor.svg"), W, H, *f)


# ── 2. Вимір послідовного стеку: комірки на різних потенціалах ───────────────
def fig_monitor_stack():
    """Кожна комірка «висить» на своєму рівні потенціалу. Монітор міряє
    різницю на кінцях КОЖНОЇ комірки, дані йдуть ізольованою стрічкою до МК."""
    W, H = 780, 470
    f = [text(W / 2, 30, "Вимір комірки в стеку: різниця, а не потенціал від землі", size=15, bold=True)]
    # стек із 4 комірок ліворуч, із позначеними потенціалами вузлів
    sx = 150
    top = 70
    cellh = 74
    nodes = [12.4, 9.3, 6.2, 3.1, 0.0]   # потенціали вузлів (грубо) згори вниз
    cw = 70
    for i in range(4):
        y = top + i * cellh
        col = C_OK
        f.append(rect(sx, y + 8, cw, cellh - 16, fill="#fff", stroke=col, sw=1.8))
        f.append(text(sx + cw / 2, y + cellh / 2 + 4, "3.1 В", size=12, color=col, bold=True))
    # підписи потенціалів вузлів зліва від стеку
    for i, p in enumerate(nodes):
        y = top + i * cellh + 8
        f.append(line(sx, y, sx + cw, y, color=MUTED, sw=1, dash="3 3"))
        f.append(text(sx - 12, y + 4, "%.1f В" % p, size=10, color=MUTED, anchor="end"))
    f.append(text(sx + cw / 2, top - 14, "стек", size=11, color=INK, bold=True))
    f.append(text(sx - 12, top + 4 * cellh + 26, "потенціал\nвузла від «−»", size=9, color=MUTED, anchor="end"))
    # монітор — блок праворуч, по парі дротів до кожного вузла
    mx, my = 430, top + 20
    mw, mh = 150, 4 * cellh - 40
    f.append(rect(mx, my, mw, mh, fill="#fff", stroke=NEG, sw=2))
    f.append(mtext(mx + mw / 2, my + mh / 2 - 18, "монітор\nкомірок", size=13, color=NEG, bold=True))
    f.append(mtext(mx + mw / 2, my + mh / 2 + 26, "(AFE +\nдиф. АЦП)", size=10, color=MUTED))
    for i in range(5):
        y = top + i * cellh + 8
        f.append(line(sx + cw, y, mx, my + 18 + i * (mh - 36) / 4, color=GOLD, sw=1.6))
    # ізольована стрічка до МК
    ix = mx + mw + 70
    f.append(rect(ix, my + mh / 2 - 34, 120, 68, fill="#fff", stroke=INK, sw=2))
    f.append(mtext(ix + 60, my + mh / 2 - 6, "МК\n(логіка 3.3 В)", size=12, color=INK, bold=True))
    # бар'єр ізоляції
    bx = mx + mw + 34
    f.append(line(bx, my - 6, bx, my + mh + 6, color=C_BAD, sw=2, dash="6 5"))
    f.append(text(bx, my - 14, "ізоляція", size=10, color=C_BAD, bold=True))
    f.append(arrow(mx + mw, my + mh / 2, ix, my + mh / 2, color=INK, sw=1.8))
    f.append(text((mx + mw + ix) / 2, my + mh / 2 - 8, "цифра", size=9, color=MUTED))
    f.append(fitbox(40, top + 4 * cellh + 44, W - 80, 28,
                    "Верхня комірка «висить» на 9 В над «−»: її 3.1 В видно лише як різницю на кінцях, а не як потенціал від землі.",
                    size=10.5, fill=FILL, stroke=MUTED, sw=1.3))
    render(os.path.join(IMG, "monitor-stack.svg"), W, H, *f)


# ── 3. Дві незалежні лінії захисту ───────────────────────────────────────────
def fig_protection_layers():
    """Розумний монітор (1-ша лінія) + незалежний вторинний захист (2-га лінія).
    Будь-яка з них рве коло — як запобіжник за запобіжником."""
    W, H = 780, 400
    f = [text(W / 2, 30, "Дві незалежні лінії захисту: одна страхує іншу", size=16, bold=True)]
    # комірки -> два монітори паралельно -> АБО -> ключ
    cellx = 60
    cy = 150
    f.append(rect(cellx, cy - 40, 90, 110, fill="#fff", stroke=C_OK, sw=2))
    f.append(mtext(cellx + 45, cy + 6, "комірки\nстеку", size=12, color=C_OK, bold=True))
    # 1-ша лінія
    l1x = 230
    f.append(rect(l1x, 80, 200, 70, fill="#fff", stroke=NEG, sw=2))
    f.append(mtext(l1x + 100, 108, "1-ша лінія:\nрозумний монітор + МК", size=11.5, color=NEG, bold=True))
    f.append(text(l1x + 100, 142, "точні пороги, балансування, лог", size=9, color=MUTED))
    # 2-га лінія
    f.append(rect(l1x, 210, 200, 70, fill="#fff", stroke=C_BAD, sw=2))
    f.append(mtext(l1x + 100, 238, "2-га лінія:\nнезалежний вторинний захист", size=11.5, color=C_BAD, bold=True))
    f.append(text(l1x + 100, 272, "грубі «жорсткі» пороги, власне живлення", size=9, color=MUTED))
    # дроти від комірок до обох ліній
    f.append(line(cellx + 90, cy - 10, l1x, 115, color=GOLD, sw=1.6))
    f.append(line(cellx + 90, cy + 30, l1x, 245, color=GOLD, sw=1.6))
    # вузол АБО
    orx, ory = 500, 180
    f.append(circle(orx, ory, 26, fill="#fff", stroke=INK, sw=2))
    f.append(text(orx, ory + 6, "АБО", size=12, color=INK, bold=True))
    f.append(arrow(l1x + 200, 115, orx - 24, ory - 10, color=NEG, sw=1.8))
    f.append(arrow(l1x + 200, 245, orx - 24, ory + 10, color=C_BAD, sw=1.8))
    f.append(text(orx + 2, ory - 36, "будь-яка вимикає", size=9, color=MUTED))
    # ключ розриву
    kx = 600
    f.append(rect(kx, ory - 40, 130, 80, fill="#fff", stroke=INK, sw=2))
    f.append(mtext(kx + 65, ory - 8, "ключ розриву\n(MOSFET /", size=12, color=INK, bold=True))
    f.append(text(kx + 65, ory + 28, "контактор)", size=12, color=INK, bold=True))
    f.append(arrow(orx + 26, ory, kx, ory, color=INK, sw=2))
    f.append(fitbox(60, 320, W - 120, 28,
                    "Якщо МК зависне чи монітор збреше, груба 2-га лінія однаково розірве коло — відмова однієї не лишає батарею без нагляду.",
                    size=10, fill="#fdf3f2", stroke=C_BAD, sw=1.4))
    render(os.path.join(IMG, "protection-layers.svg"), W, H, *f)


# ── 4. Контактор і передзаряд: чому не можна вмикати «в лоб» ─────────────────
def fig_contactor_precharge():
    """Порожня ємність навантаження = коротке для джерела. Передзарядний
    резистор м'яко заряджає її, тоді вмикається головний контактор."""
    W, H = 780, 430
    f = [text(W / 2, 28, "Передзаряд: чому головний контактор не вмикають одразу", size=15, bold=True)]
    # схема: батарея — (− контактор) … (+ контактор || передзаряд R+контактор) — ємність
    by = 95
    # батарея
    f.append(rect(60, by, 96, 90, fill="#fff", stroke=C_OK, sw=2))
    f.append(mtext(108, by + 38, "батарея\nпакета", size=12, color=C_OK, bold=True))
    f.append(text(108, by + 74, "напр. 48 В", size=10, color=MUTED))
    # верхня вітка: головний + контактор
    topy = by + 6
    f.append(line(156, topy, 250, topy, color=INK, sw=2))
    f.append(text(300, topy - 10, "головний «+» контактор", size=10, color=INK, bold=True))
    # символ розімкненого контактора
    f.append(line(250, topy, 280, topy, color=INK, sw=2))
    f.append(line(290, topy - 16, 330, topy, color=INK, sw=2))   # розімкнений важіль
    f.append(line(340, topy, 470, topy, color=INK, sw=2))
    # нижня вітка: передзаряд — контактор + R
    pchy = by + 56
    f.append(line(156, pchy, 200, pchy, color=GOLD, sw=2))
    f.append(line(156, topy, 156, pchy, color=INK, sw=2))
    f.append(text(255, pchy + 22, "передзарядний контактор + R", size=10, color=GOLD, bold=True))
    f.append(line(200, pchy, 220, pchy, color=GOLD, sw=2))
    f.append(line(230, pchy - 14, 250, pchy, color=GOLD, sw=2))   # розімкнений
    # резистор (зиґзаґ)
    rx = 260
    zig = "M%d %d l 8 -8 l 8 16 l 8 -16 l 8 16 l 8 -8" % (rx, pchy)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (zig, GOLD))
    f.append(line(rx + 40, pchy, 470, pchy, color=GOLD, sw=2))
    f.append(line(470, topy, 470, pchy, color=INK, sw=2))
    # ємність навантаження
    capx = 500
    f.append(line(470, (topy + pchy) / 2, capx, (topy + pchy) / 2, color=INK, sw=2))
    f.append(line(capx, (topy + pchy) / 2 - 26, capx, (topy + pchy) / 2 + 26, color=NEG, sw=3))
    f.append(line(capx + 12, (topy + pchy) / 2 - 26, capx + 12, (topy + pchy) / 2 + 26, color=NEG, sw=3))
    f.append(mtext(capx + 6, (topy + pchy) / 2 + 52, "вхідна\nємність", size=11, color=NEG, bold=True))
    f.append(text(capx + 6, (topy + pchy) / 2 - 36, "порожня = коротке!", size=9.5, color=C_BAD, bold=True))
    # графік кидка струму нижче
    gx, gy = 110, 320
    gw, gh = 300, 80
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.4))   # t
    f.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.4))   # I
    f.append(text(gx + gw + 8, gy + 4, "час", size=9, color=MUTED, anchor="start"))
    f.append(text(gx - 8, gy - gh, "струм", size=9, color=MUTED, anchor="end"))
    # без передзаряду — гострий пік
    f.append('<polyline points="%d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (gx, gy, gx + 6, gy - gh, gx + 40, gy - 6, gx + gw, gy - 4, C_BAD))
    f.append(text(gx + 70, gy - gh + 6, "без передзаряду: різкий кидок", size=9.5, color=C_BAD, bold=True, anchor="start"))
    # з передзарядом — пологий
    f.append('<path d="M%d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (gx, gy - 34, gx + 120, gy - 6, gx + gw, gy - 4, C_OK))
    f.append(text(gx + 120, gy - 30, "з передзарядом: плавно", size=9.5, color=C_OK, bold=True, anchor="start"))
    # послідовність праворуч
    seqx = 450
    f.append(fitbox(seqx, 300, W - seqx - 30, 96,
                    "Порядок (частки секунди):\n1. замкнути «−» контактор\n2. замкнути передзарядний — R заряджає ємність\n3. коли ΔU мала — замкнути головний «+»\n4. розімкнути передзарядний",
                    size=10, fill=FILL, stroke=GOLD, sw=1.4))
    render(os.path.join(IMG, "contactor-precharge.svg"), W, H, *f)


# ── 5. Родовід BMS: від одного захисного чипа до розподіленого ланцюжка ──────
def fig_bms_lineage():
    """Історична дуга (вставка hist-bms-origins): захист народився згори —
    в аероспейсі й електромобілях, де стек великий, — і поступово спустився
    в кишеню. Праворуч — три щаблі складності монітора."""
    W, H = 820, 470
    f = [text(W / 2, 30, "Родовід керованої батареї: згори вниз і від простого до складного", size=15, bold=True)]

    # ── ліва колонка: «звідки спустилося» (масштаб і ціна помилки) ──
    lx, lw = 40, 250
    rungs = [
        ("Аероспейс (з 1970-х)", "великі послідовні стеки;\nспершу NiCd/NiH2, Li-ion\nу космосі з 2001 (PROBA-1)", NEG),
        ("Електромобілі (1996→2008)", "EV1 — пакет із наглядом;\nRoadster — нагляд за кожною\nланкою з 6831 комірок", GOLD),
        ("Побутова електроніка", "ноутбук, телефон, дрон,\nповербанк — той самий\nзахист у мініатюрі", C_OK),
    ]
    f.append(text(lx + lw / 2, 62, "звідки спустилася технологія", size=11, color=MUTED, bold=True))
    ry, rh, rgap = 80, 96, 18
    for i, (ttl, body, col) in enumerate(rungs):
        y = ry + i * (rh + rgap)
        f.append(rect(lx, y, lw, rh, fill="#fff", stroke=col, sw=2))
        f.append(text(lx + lw / 2, y + 22, ttl, size=11.5, color=col, bold=True))
        f.append(mtext(lx + lw / 2, y + 42, body, size=9.5, color=INK))
        if i < len(rungs) - 1:
            f.append(arrow(lx + lw / 2, y + rh, lx + lw / 2, y + rh + rgap, color=MUTED, sw=2))
    f.append(text(lx + lw / 2, ry + 3 * (rh + rgap) + 4, "ціна помилки падає, обсяг — росте", size=9, color=MUTED))

    # ── права колонка: три щаблі складності монітора ──
    rx, rw = 330, 450
    f.append(text(rx + rw / 2, 62, "як ріс сам монітор", size=11, color=MUTED, bold=True))
    stages = [
        ("1. Дискретний захист", "купка транзисторів і компараторів;\nстереже одну комірку, грубо", C_LOW),
        ("2. Захисний чип (AFE)", "одна мікросхема на 1 комірку:\nперезаряд / глибокий розряд / надструм\n(Ricoh RS5VG, 1995; далі Seiko, Mitsumi)", NEG),
        ("3. Стековий монітор", "одна IC міряє 12 комірок диференційно;\nланцюжок крізь ізоляцію на весь стек\n(Linear LTC6802, 2008)", C_OK),
    ]
    sy, sh, sgap = 80, 96, 18
    for i, (ttl, body, col) in enumerate(stages):
        y = sy + i * (sh + sgap)
        f.append(rect(rx, y, rw, sh, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="34" height="%.1f" rx="6" fill="%s" fill-opacity="0.14"/>'
                 % (rx, y, sh, col))
        f.append(text(rx + 17, y + sh / 2 + 7, "%d" % (i + 1), size=20, color=col, bold=True))
        f.append(text(rx + 52, y + 24, ttl.split(". ", 1)[1], size=12, color=col, bold=True, anchor="start"))
        f.append(mtext(rx + 52, y + 44, body, size=9.5, color=INK, anchor="start"))
        if i < len(stages) - 1:
            f.append(arrow(rx + rw / 2, y + sh, rx + rw / 2, y + sh + sgap, color=MUTED, sw=2))

    render(os.path.join(IMG, "bms-lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_monitor()
    fig_monitor_stack()
    fig_protection_layers()
    fig_contactor_precharge()
    fig_bms_lineage()
    print("OK: 5 figures ->", IMG)
