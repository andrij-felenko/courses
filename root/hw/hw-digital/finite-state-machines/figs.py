# -*- coding: utf-8 -*-
"""Фігури до теми «Скінченні автомати» та її вставок (📜 історія, ⚙️ код).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── helpers ─────────────────────────────────────────────────────────────────
def state(cx, cy, r, label, sub=None, initial=False, fill=FILL, stroke=LINE,
          tcolor=INK, sw=1.8):
    """Кружок-стан із підписом; sub — другий рядок усередині; initial — подвійне кільце."""
    out = ""
    if initial:
        out += circle(cx, cy, r + 5, fill="none", stroke=stroke, sw=sw)
    out += circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)
    if sub:
        out += text(cx, cy - 2, label, size=13, bold=True, color=tcolor)
        out += text(cx, cy + 15, sub, size=11, color=tcolor)
    else:
        out += text(cx, cy + 5, label, size=14, bold=True, color=tcolor)
    return out


def curved(x1, y1, x2, y2, bend, color=LINE, sw=1.8):
    """Дугоподібна стрілка від (x1,y1) до (x2,y2); bend — відхил контрольної точки."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    cx, cy = mx + nx * bend, my + ny * bend
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x1, y1, cx, cy, x2, y2, color, sw))


def self_loop(cx, cy, r, color=LINE, sw=1.8, side="top"):
    """Петля-на-собі над/під кружком стану; повертає (svg, (labx, laby))."""
    if side == "top":
        x1, y1 = cx - r * 0.5, cy - r * 0.87
        x2, y2 = cx + r * 0.5, cy - r * 0.87
        c1x, c1y = cx - r * 0.9, cy - r - 42
        c2x, c2y = cx + r * 0.9, cy - r - 42
        lab = (cx, cy - r - 30)
    else:  # bottom
        x1, y1 = cx + r * 0.5, cy + r * 0.87
        x2, y2 = cx - r * 0.5, cy + r * 0.87
        c1x, c1y = cx + r * 0.9, cy + r + 42
        c2x, c2y = cx - r * 0.9, cy + r + 42
        lab = (cx, cy + r + 44)
    svg = ('<path d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
           'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
           % (x1, y1, c1x, c1y, c2x, c2y, x2, y2, color, sw))
    return svg, lab


def edge_point(cx, cy, r, tx, ty):
    """Точка на колі радіуса r у напрямку до (tx,ty) — щоб стрілка торкалась межі."""
    dx, dy = tx - cx, ty - cy
    L = math.hypot(dx, dy) or 1
    return cx + dx / r0(r, L), cy + dy / r0(r, L)


def r0(r, L):
    return L / r


def code_box(x, y, w, h, lines, title=None, accent=INK, fs=12):
    """Рамка «під код»: моноширинні рядки ліворуч; title — заголовок-стрічка зверху."""
    out = rect(x, y, w, h, fill="#f7f8fa", stroke=accent, sw=1.6, rx=8)
    yy = y + 22
    if title:
        out += text(x + w / 2, yy, title, size=13, bold=True, color=accent)
        yy += 24
    for ln in lines:
        col = MUTED if ln.startswith("//") or ln.startswith("#") else INK
        out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
                'font-size="%d" fill="%s" text-anchor="start">%s</text>'
                % (x + 16, yy, fs, col, esc(ln)))
        yy += fs * 1.5
    return out


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Від лічильника до автомата ────────────────────────────────────────────
def fig_counter_to_fsm():
    W, H = 880, 420
    f = [text(W / 2, 30, "Сліпа лічба проти керування: відв'яжемо жорстке «+1»",
              size=16, bold=True)]

    # ── ліворуч: лічильник ──
    f.append(rect(40, 64, 380, 320, fill="none", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(230, 90, "Лічильник: маршрут зашитий", size=14, bold=True, color=MUTED))
    cx, cy, R = 230, 235, 95
    ring = ["0", "1", "2", "3"]
    pts = []
    for i, lab in enumerate(ring):
        ang = -math.pi / 2 + i * 2 * math.pi / 4
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        pts.append((px, py))
        f.append(state(px, py, 24, lab, fill=FILL, stroke=LINE))
    # стрілки по колу 0→1→2→3→0
    for i in range(4):
        a = pts[i]
        b = pts[(i + 1) % 4]
        ax = a[0] + (b[0] - a[0]) * 0.30
        ay = a[1] + (b[1] - a[1]) * 0.30
        bx = a[0] + (b[0] - a[0]) * 0.70
        by = a[1] + (b[1] - a[1]) * 0.70
        f.append(curved(ax, ay, bx, by, 16, color=MUTED, sw=1.8))
    f.append(text(cx, cy + 4, "+1", size=15, bold=True, color=MUTED))
    f.append(text(cx, cy + 24, "завжди", size=11, color=MUTED))
    f.append(text(230, 372, "крокує по колу однаково, входу не бачить",
                  size=11, color=MUTED, italic=True))

    # ── праворуч: автомат ──
    f.append(rect(460, 64, 380, 320, fill="none", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(650, 90, "Автомат: маршрут обирає вхід", size=14, bold=True, color=FIELD))
    ax, ay = 575, 230
    bx, by = 745, 230
    rr = 34
    f.append(state(ax, ay, rr, "A", fill=FILL, stroke=LINE))
    f.append(state(bx, by, rr, "B", fill=FILL, stroke=LINE))
    # A --вхід=1--> B
    f.append(curved(ax + rr, ay - 8, bx - rr, by - 8, -26, color=FIELD, sw=2.0))
    f.append(text((ax + bx) / 2, ay - 40, "вхід=1", size=12, bold=True, color=FIELD))
    # B --вхід=0--> A (нижня дуга)
    f.append(curved(bx - rr, by + 8, ax + rr, ay + 8, -26, color=NEG, sw=2.0))
    f.append(text((ax + bx) / 2, ay + 52, "вхід=0", size=12, color=NEG))
    # петля «лишитись» на A за входом=0
    lp, lab = self_loop(ax, ay, rr, color=NEG, sw=1.8, side="top")
    f.append(lp)
    f.append(text(lab[0], lab[1], "вхід=0", size=11, color=NEG))
    f.append(text(650, 372, "за входом машина переходить або лишається — рішення",
                  size=11, color=FIELD, italic=True))

    # центральна стрілка-перехід ідеї
    f.append(text(440, 250, "→", size=30, color=INK, bold=True))
    render(os.path.join(IMG, "counter-to-fsm.svg"), W, H, *f)


# ── 2. Діаграма станів приймача байта ───────────────────────────────────────
def fig_state_diagram():
    W, H = 900, 440
    f = [text(W / 2, 30, "Діаграма станів: контролер приймача послідовного байта",
              size=16, bold=True)]
    r = 42
    # чотири стани в ряд
    idle = (130, 220)
    start = (360, 220)
    data = (590, 220)
    stop = (810, 220)

    f.append(state(*idle, r, "IDLE", "спокій", initial=True, stroke=FIELD, tcolor=INK))
    f.append(state(*start, r, "START", "старт"))
    f.append(state(*data, r, "DATA", "біти"))
    f.append(state(*stop, r, "STOP", "стоп"))

    # IDLE self-loop (line=1)
    lp, lab = self_loop(idle[0], idle[1], r, color=NEG, side="top")
    f.append(lp)
    f.append(text(lab[0], lab[1] - 2, "лінія=1", size=11, color=NEG))
    f.append(text(lab[0], lab[1] - 16, "(тиша)", size=10, color=MUTED))

    # IDLE -> START  (line=0 / start)
    f.append(arrow(idle[0] + r, idle[1] - 6, start[0] - r, start[1] - 6, color=INK, sw=2.0))
    f.append(text((idle[0] + start[0]) / 2, idle[1] - 16, "лінія=0", size=11, bold=True, color=INK))
    f.append(text((idle[0] + start[0]) / 2, idle[1] - 2, "(старт-біт)", size=10, color=MUTED))

    # START -> DATA  (wait)
    f.append(arrow(start[0] + r, start[1] - 6, data[0] - r, data[1] - 6, color=INK, sw=2.0))
    f.append(text((start[0] + data[0]) / 2, start[1] - 12, "перечекати", size=11, color=INK))

    # DATA self-loop (bits<8)
    lp2, lab2 = self_loop(data[0], data[1], r, color=NEG, side="top")
    f.append(lp2)
    f.append(text(lab2[0], lab2[1] - 2, "бітів<8", size=11, color=NEG))
    f.append(text(lab2[0], lab2[1] - 16, "(рахувати)", size=10, color=MUTED))

    # DATA -> STOP  (8 bits)
    f.append(arrow(data[0] + r, data[1] - 6, stop[0] - r, stop[1] - 6, color=INK, sw=2.0))
    f.append(text((data[0] + stop[0]) / 2, data[1] - 12, "8 бітів", size=11, bold=True, color=INK))

    # STOP -> IDLE  (back, big bottom arc)
    f.append(curved(stop[0], stop[1] + r, idle[0], idle[1] + r, 130, color=INK, sw=2.0))
    f.append(text((idle[0] + stop[0]) / 2, idle[1] + r + 128, "стоп-біт перевірено → чекати нову посилку",
                  size=11, color=INK))

    # легенда: подвійне кільце = початковий
    f.append(text(130, 372, "подвійне кільце = початковий стан", size=10, color=FIELD, italic=True))
    render(os.path.join(IMG, "state-diagram.svg"), W, H, *f)


# ── 3. Мур проти Мілі ───────────────────────────────────────────────────────
def fig_moore_vs_mealy():
    W, H = 880, 400
    f = [text(W / 2, 30, "Та сама поведінка, два почерки: де «живе» вихід",
              size=16, bold=True)]

    # ── Мур (ліворуч): вихід у кружку ──
    f.append(rect(40, 64, 380, 300, fill="none", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(230, 90, "Мур: вихід — у стані", size=14, bold=True, color=FIELD))
    s0 = (140, 215)
    s1 = (320, 215)
    f.append(state(*s0, 44, "S0", "вих=0", stroke=LINE, tcolor=INK))
    f.append(state(*s1, 44, "S1", "вих=1", stroke=LINE, tcolor=POS))
    # S0 -> S1 (вх=1)
    f.append(curved(s0[0] + 44, s0[1] - 8, s1[0] - 44, s1[1] - 8, -22, color=INK, sw=2.0))
    f.append(text((s0[0] + s1[0]) / 2, s0[1] - 34, "вх=1", size=12, bold=True, color=INK))
    # S1 -> S0 (вх=0)
    f.append(curved(s1[0] - 44, s1[1] + 8, s0[0] + 44, s0[1] + 8, -22, color=NEG, sw=2.0))
    f.append(text((s0[0] + s1[0]) / 2, s0[1] + 44, "вх=0", size=12, color=NEG))
    f.append(text(230, 348, "вихід тримається весь такт — чистий і вирівняний",
                  size=10.5, color=FIELD, italic=True))

    # ── Мілі (праворуч): вихід на стрілці ──
    f.append(rect(460, 64, 380, 300, fill="none", stroke=POS, sw=1.8, rx=12))
    f.append(text(650, 90, "Мілі: вихід — на переході", size=14, bold=True, color=POS))
    m0 = (560, 215)
    m1 = (740, 215)
    f.append(state(*m0, 44, "S0", stroke=LINE, tcolor=INK))
    f.append(state(*m1, 44, "S1", stroke=LINE, tcolor=INK))
    # S0 -> S1  (вх=1 / вих=1)
    f.append(curved(m0[0] + 44, m0[1] - 8, m1[0] - 44, m1[1] - 8, -22, color=POS, sw=2.2))
    f.append(text((m0[0] + m1[0]) / 2, m0[1] - 38, "вх=1 / вих=1", size=12, bold=True, color=POS))
    # S1 -> S0  (вх=0 / вих=0)
    f.append(curved(m1[0] - 44, m1[1] + 8, m0[0] + 44, m0[1] + 8, -22, color=NEG, sw=2.0))
    f.append(text((m0[0] + m1[0]) / 2, m0[1] + 44, "вх=0 / вих=0", size=11, color=NEG))
    f.append(text(650, 348, "реагує того ж такту, та може «мигати» слідом за входом",
                  size=10.5, color=POS, italic=True))
    render(os.path.join(IMG, "moore-vs-mealy.svg"), W, H, *f)


# ── 4. Канонічна реалізація ──────────────────────────────────────────────────
def fig_canonical_implementation():
    W, H = 900, 440
    f = [text(W / 2, 30, "Канонічна схема автомата: регістр стану + дві логіки",
              size=16, bold=True)]

    # блоки
    nx, ny, nw, nh = 120, 110, 200, 90      # next-state logic
    rx, ry, rw, rh = 400, 110, 180, 90      # state register
    ox, oy, ow, oh = 660, 110, 200, 90      # output logic

    f.append(fitbox(nx, ny, nw, nh, "Логіка\nнаступного стану\n(комбінаційна)",
                    size=13, fill=FILL, stroke=NEG, bold=True))
    f.append(fitbox(rx, ry, rw, rh, "Регістр стану\n(тригери)",
                    size=14, fill="#eef7ee", stroke=FIELD, bold=True))
    f.append(fitbox(ox, oy, ow, oh, "Логіка виходу\n(комбінаційна)",
                    size=13, fill=FILL, stroke=POS, bold=True))

    midy = ny + nh / 2
    # входи -> next-state logic
    f.append(arrow(40, midy, nx, midy, color=INK, sw=2.0))
    f.append(text(44, midy - 10, "входи", size=12, bold=True, anchor="start"))
    # next-state -> register
    f.append(arrow(nx + nw, midy, rx, midy, color=INK, sw=2.0))
    f.append(text((nx + nw + rx) / 2, midy - 10, "наст. стан", size=11, color=INK))
    # register -> output logic (поточний стан)
    f.append(arrow(rx + rw, midy, ox, midy, color=INK, sw=2.0))
    f.append(text((rx + rw + ox) / 2, midy - 10, "стан", size=11, bold=True, color=FIELD))
    # output -> виходи
    f.append(arrow(ox + ow, midy, W - 40, midy, color=INK, sw=2.0))
    f.append(text(W - 44, midy - 10, "виходи", size=12, bold=True, anchor="end"))

    # зворотний зв'язок: вихід регістра -> назад у логіку переходу (нижня петля)
    fb = ny + nh + 70
    f.append(line(rx + rw / 2, ry + rh, rx + rw / 2, fb, color=FIELD, sw=2.0))
    f.append(line(rx + rw / 2, fb, nx + nw / 2, fb, color=FIELD, sw=2.0))
    f.append(arrow(nx + nw / 2, fb, nx + nw / 2, ny + nh, color=FIELD, sw=2.0))
    f.append(text((nx + nw / 2 + rx + rw / 2) / 2, fb + 18, "поточний стан вертається (зворотний зв'язок)",
                  size=11, color=FIELD, italic=True))

    # такт у регістр
    f.append(line(rx + rw / 2, ry - 34, rx + rw / 2, ry, color=POS, sw=1.8))
    f.append(text(rx + rw / 2, ry - 40, "такт", size=11, bold=True, color=POS))

    # пунктир Мілі: входи -> логіка виходу
    inx = 70
    topy = ny - 18
    f.append(line(inx, midy, inx, topy, color=MUTED, sw=1.5, dash="5 4"))
    f.append(line(inx, topy, ox + ow / 2, topy, color=MUTED, sw=1.5, dash="5 4"))
    f.append(arrow(ox + ow / 2, topy, ox + ow / 2, oy, color=MUTED, sw=1.5))
    f.append(text((inx + ox) / 2, topy - 8, "пунктир = різниця Мілі: входи заходять і в логіку виходу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "canonical-implementation.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА ⚙️
# ════════════════════════════════════════════════════════════════════════════

# ── 5. switch проти таблиці переходів ───────────────────────────────────────
def fig_code_two_ways():
    W, H = 900, 420
    f = [text(W / 2, 30, "Той самий автомат: switch-код проти таблиці переходів",
              size=16, bold=True)]

    # ── ліворуч: switch ──
    f.append(text(225, 76, "Логіка зашита в код", size=14, bold=True, color=NEG))
    f.append(code_box(40, 92, 380, 268, [
        "switch (state) {",
        "  case LOCKED:",
        "    if (ev == COIN) {",
        "      unlock();",
        "      state = OPEN;",
        "    }",
        "    break;",
        "  case OPEN:",
        "    if (ev == PUSH) {",
        "      lock();",
        "      state = LOCKED;",
        "    }",
        "    break;",
        "}",
    ], accent=NEG, fs=13))

    # ── праворуч: таблиця ──
    f.append(text(665, 76, "Логіка винесена в дані", size=14, bold=True, color=FIELD))
    tx, ty = 470, 100
    cw0, cw, ch = 110, 150, 46
    # шапка
    f.append(rect(tx, ty, cw0, ch, fill="#eef7ee", stroke=FIELD, sw=1.4))
    f.append(text(tx + cw0 / 2, ty + 29, "next[][]", size=12, bold=True, color=FIELD))
    f.append(rect(tx + cw0, ty, cw, ch, fill="#eef7ee", stroke=FIELD, sw=1.4))
    f.append(text(tx + cw0 + cw / 2, ty + 29, "COIN", size=13, bold=True, color=FIELD))
    f.append(rect(tx + cw0 + cw, ty, cw, ch, fill="#eef7ee", stroke=FIELD, sw=1.4))
    f.append(text(tx + cw0 + cw + cw / 2, ty + 29, "PUSH", size=13, bold=True, color=FIELD))
    # рядок LOCKED
    rows = [
        ("LOCKED", [("OPEN", "/unlock"), ("LOCKED", "/—")]),
        ("OPEN", [("OPEN", "/—"), ("LOCKED", "/lock")]),
    ]
    for ri, (name, cells) in enumerate(rows):
        ry = ty + ch + ri * ch
        f.append(rect(tx, ry, cw0, ch, fill=FILL, stroke=LINE, sw=1.3))
        f.append(text(tx + cw0 / 2, ry + 29, name, size=12, bold=True))
        for ci, (ns, act) in enumerate(cells):
            cxp = tx + cw0 + ci * cw
            hot = (name == "LOCKED" and ci == 0)
            f.append(rect(cxp, ry, cw, ch, fill="#fdecea" if hot else FILL, stroke=LINE, sw=1.3))
            f.append(text(cxp + cw / 2, ry + 21, ns, size=12, bold=True,
                          color=POS if hot else INK))
            f.append(text(cxp + cw / 2, ry + 38, act, size=10, color=MUTED))
    f.append(text(665, ty + 3 * ch + 28,
                  "клітинка = (новий стан, дія)", size=11, color=FIELD, italic=True))

    f.append(text(W / 2, H - 14,
                  "Обидва кодують LOCKED + COIN → unlock і перехід в OPEN; таблиця відділяє «що» від «як крутить рушій».",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "code-two-ways.svg"), W, H, *f)


# ── 6. Диспетчеризація події ─────────────────────────────────────────────────
def fig_code_dispatch():
    W, H = 900, 400
    f = [text(W / 2, 30, "Як подія знаходить свій перехід", size=16, bold=True)]

    # ── ліворуч: каскад ──
    f.append(rect(40, 64, 380, 300, fill="none", stroke=NEG, sw=1.6, rx=12))
    f.append(text(230, 90, "if/switch-каскад: лінійний перебір", size=13, bold=True, color=NEG))
    x = 230
    ys = [128, 178, 228, 278]
    labels = ["стан == S0 ?", "стан == S1 ?", "стан == S2 ?", "…далі по черзі"]
    for i, (yy, lb) in enumerate(zip(ys, labels)):
        col = NEG if i < 3 else MUTED
        f.append(fitbox(x - 110, yy - 18, 220, 36, lb, size=12, fill=FILL, stroke=col))
        if i < len(ys) - 1:
            f.append(arrow(x, yy + 18, x, ys[i + 1] - 18, color=NEG, sw=1.6))
            f.append(text(x + 16, (yy + 18 + ys[i + 1] - 18) / 2 + 4, "ні", size=10,
                          color=MUTED, anchor="start"))
    f.append(text(230, 340, "найгірший час росте з числа станів × подій",
                  size=11, color=NEG, italic=True))

    # ── праворуч: прямий індекс ──
    f.append(rect(460, 64, 400, 300, fill="none", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(660, 90, "Таблиця: прямий індекс", size=13, bold=True, color=FIELD))
    f.append(fitbox(560, 130, 200, 44, "(стан, подія)", size=13, fill=FILL, stroke=INK, bold=True))
    f.append(arrow(660, 174, 660, 214, color=FIELD, sw=2.0))
    f.append(text(676, 196, "індекс", size=11, color=FIELD, anchor="start"))
    f.append(fitbox(560, 214, 200, 48, "next[стан][подія]", size=12, fill="#eef7ee",
                    stroke=FIELD, bold=True))
    f.append(arrow(660, 262, 660, 300, color=FIELD, sw=2.0))
    f.append(fitbox(560, 300, 200, 40, "(новий стан, дія)", size=12, fill=FILL, stroke=INK))
    f.append(text(660, 360, "одне читання з пам'яті — O(1), хоч би скільки станів",
                  size=11, color=FIELD, italic=True))
    render(os.path.join(IMG, "code-dispatch.svg"), W, H, *f)


# ── 7. Три пастки ────────────────────────────────────────────────────────────
def fig_code_pitfalls():
    W, H = 920, 420
    f = [text(W / 2, 30, "Три класичні граблі автомата на мікроконтролері",
              size=16, bold=True)]
    bw, bh = 270, 300
    xs = [30, 325, 620]

    # ── (a) діра в таблиці ──
    f.append(rect(xs[0], 64, bw, bh, fill="none", stroke=POS, sw=1.8, rx=12))
    f.append(text(xs[0] + bw / 2, 90, "Діра в таблиці", size=14, bold=True, color=POS))
    tx, ty = xs[0] + 40, 120
    cw, ch = 78, 46
    cells = [("OPEN", FILL), ("???", "#fdecea"), ("LOCK", FILL), ("OPEN", FILL)]
    for i, (lab, fl) in enumerate(cells):
        r_, c_ = divmod(i, 2)
        cxp, cyp = tx + c_ * cw, ty + r_ * ch
        st = POS if lab == "???" else LINE
        f.append(rect(cxp, cyp, cw, ch, fill=fl, stroke=st, sw=1.8 if lab == "???" else 1.3))
        f.append(text(cxp + cw / 2, cyp + 29, lab, size=12, bold=(lab == "???"),
                      color=POS if lab == "???" else INK))
    f.append(arrow(tx + cw + cw / 2, ty + 2 * ch + 14, tx + cw + cw / 2, ty + 2 * ch + 54,
                   color=POS, sw=2.0))
    f.append(text(xs[0] + bw / 2, ty + 2 * ch + 78, "забута клітинка →", size=12, color=POS, bold=True))
    f.append(text(xs[0] + bw / 2, ty + 2 * ch + 96, "провал у невизначеність", size=11, color=INK))
    f.append(text(xs[0] + bw / 2, 348, "лік: заповнити кожен стан × подію",
                  size=10.5, color=MUTED, italic=True))

    # ── (b) дія в стані vs на переході ──
    f.append(rect(xs[1], 64, bw, bh, fill="none", stroke=NEG, sw=1.8, rx=12))
    f.append(text(xs[1] + bw / 2, 90, "Дія: стан чи перехід?", size=14, bold=True, color=NEG))
    sc = (xs[1] + bw / 2, 170)
    f.append(state(*sc, 40, "S", "on_enter", stroke=LINE, tcolor=NEG))
    # петля сам у себе
    lp, lab = self_loop(sc[0], sc[1], 40, color=POS, side="top")
    f.append(lp)
    f.append(text(lab[0], lab[1], "S → S", size=11, color=POS, bold=True))
    f.append(text(xs[1] + bw / 2, 250, "Мур: дія в стані (on_enter/exit)", size=11, color=INK))
    f.append(text(xs[1] + bw / 2, 270, "Мілі: дія на переході", size=11, color=INK))
    f.append(text(xs[1] + bw / 2, 300, "пастка: on_enter спрацює ВДРУГЕ", size=11, color=POS, bold=True))
    f.append(text(xs[1] + bw / 2, 318, "на петлі сам-у-себе", size=11, color=POS, bold=True))
    f.append(text(xs[1] + bw / 2, 348, "лік: дія лише на справжній зміні стану",
                  size=10.5, color=MUTED, italic=True))

    # ── (c) default → safe ──
    f.append(rect(xs[2], 64, bw, bh, fill="none", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(xs[2] + bw / 2, 90, "default → безпечний стан", size=13.5, bold=True, color=FIELD))
    dirt = (xs[2] + bw / 2, 150)
    safe = (xs[2] + bw / 2, 280)
    f.append(fitbox(dirt[0] - 95, dirt[1] - 24, 190, 48, "брудний / чужий\nвхід", size=12,
                    fill="#fdecea", stroke=POS))
    f.append(arrow(dirt[0], dirt[1] + 24, safe[0], safe[1] - 28, color=FIELD, sw=2.2))
    f.append(text(dirt[0] + 14, (dirt[1] + safe[1]) / 2, "default", size=12, color=FIELD,
                  bold=True, anchor="start"))
    f.append(state(safe[0], safe[1], 36, "SAFE", stroke=FIELD, tcolor=FIELD))
    f.append(text(xs[2] + bw / 2, 348, "автомат завжди має куди впасти",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "code-pitfalls.svg"), W, H, *f)


if __name__ == "__main__":
    fig_counter_to_fsm()
    fig_state_diagram()
    fig_moore_vs_mealy()
    fig_canonical_implementation()
    fig_code_two_ways()
    fig_code_dispatch()
    fig_code_pitfalls()
    print("OK figs.py -> img/")
