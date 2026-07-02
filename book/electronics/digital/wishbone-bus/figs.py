# -*- coding: utf-8 -*-
"""Фігури до теми «Шина Wishbone».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

MST = "#c0392b"   # ведучий — теплий
SLV = "#2457d6"   # ведений — холодний
CLK = "#6b7280"   # такт — сірий
OK  = "#27ae60"   # готово / підтвердження


# ── helper: прямокутний цифровий сигнал по точках (індекс_такту, рівень 0/1) ─
def wave(x0, ybase, hi, unit, samples, color=INK, sw=2.4):
    out = []
    for k in range(len(samples) - 1):
        i1, l1 = samples[k]
        i2, l2 = samples[k + 1]
        x1 = x0 + i1 * unit
        x2 = x0 + i2 * unit
        y1 = ybase - (hi if l1 else 0)
        y2 = ybase - (hi if l2 else 0)
        if y1 != y2:
            out.append(line(x1, y1, x1, y2, color=color, sw=sw))
        out.append(line(x1, y2, x2, y2, color=color, sw=sw))
    return "".join(out)


# ── 1. Анатомія інтерфейсу: роздвоєні шляхи → «дужка» ────────────────────────
def fig_anatomy():
    W, H = 760, 470
    f = [text(W / 2, 30, "Роздільні вхід і вихід даних сходяться Y-подібно — звідси й назва",
              size=16, bold=True)]

    # два блоки
    mx, my, mw, mh = 70, 120, 200, 250
    sx, sy, sw2, sh = 490, 120, 200, 250
    f.append(rect(mx, my, mw, mh, fill="#fdece9", stroke=MST, sw=2, rx=12))
    f.append(rect(sx, sy, sw2, sh, fill="#eaf0fd", stroke=SLV, sw=2, rx=12))
    f.append(text(mx + mw / 2, my - 14, "ВЕДУЧИЙ (master)", size=14, color=MST, bold=True))
    f.append(text(sx + sw2 / 2, sy - 14, "ВЕДЕНИЙ (slave)", size=14, color=SLV, bold=True))

    # ряди сигналів: (підпис, y, напрям 'r'=до веденого / 'l'=до ведучого, колір)
    rows = [
        ("CLK  (такт)",        155, 'r', CLK),
        ("ADR  (адреса)",      190, 'r', INK),
        ("DAT_O → (запис)",    225, 'r', MST),
        ("WE, SEL, STB, CYC",  260, 'r', INK),
        ("← DAT_I (читання)",  300, 'l', SLV),
        ("← ACK (готово)",     335, 'l', OK),
    ]
    xl, xr = mx + mw, sx
    for name, y, d, col in rows:
        if d == 'r':
            f.append(arrow(xl, y, xr, y, color=col, sw=2))
        else:
            f.append(arrow(xr, y, xl, y, color=col, sw=2))
        f.append(text((xl + xr) / 2, y - 7, name, size=12, color=col, bold=True))

    # «дужка»: вихід і вхід даних роздвоюються з однієї точки
    yk = 405
    f.append(text(W / 2, yk - 22, "два роздільні шляхи даних, що розходяться з вузла:", size=12, color=MUTED))
    node = (W / 2, yk + 40)
    f.append(line(node[0], node[1], node[0] - 70, yk, color=MST, sw=3))
    f.append(line(node[0], node[1], node[0] + 70, yk, color=SLV, sw=3))
    f.append(circle(node[0], node[1], 5, fill=INK, stroke=INK))
    f.append(text(node[0] - 78, yk - 4, "вихід", size=12, color=MST, anchor="end", bold=True))
    f.append(text(node[0] + 78, yk - 4, "вхід", size=12, color=SLV, anchor="start", bold=True))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Класичний цикл читання: рукостискання STB↔ACK ────────────────────────
def fig_read_cycle():
    W, H = 780, 440
    f = [text(W / 2, 28, "Класичне читання: ведучий тримає STB, ведений відповідає ACK",
              size=16, bold=True)]

    x0, unit, n = 150, 78, 7
    hi = 34
    # такт: меандр, фронт на кожному цілому t
    clk = []
    for i in range(n + 1):
        clk.append((i, 0)); clk.append((i, 1)); clk.append((i + 0.5, 1)); clk.append((i + 0.5, 0))
    # CYC і STB: підняті з t=1 до t=4 (ведучий просить читання)
    cyc = [(0, 0), (1, 0), (1, 1), (4, 1), (4, 0), (n, 0)]
    stb = [(0, 0), (1, 0), (1, 1), (4, 1), (4, 0), (n, 0)]
    # ACK: ведений піднімає на t=3, знімає на t=4 (одне слово віддано)
    ack = [(0, 0), (3, 0), (3, 1), (4, 1), (4, 0), (n, 0)]

    rows = [("CLK",  95, clk, CLK),
            ("CYC_O", 160, cyc, MST),
            ("STB_O", 220, stb, MST),
            ("ACK_I", 285, ack, OK)]
    for name, yb, s, col in rows:
        f.append(line(x0, yb, x0 + n * unit, yb, color="#d0d5da", sw=0.8))
        f.append(wave(x0, yb, hi, unit, s, color=col))
        f.append(text(x0 - 12, yb - hi / 2 + 4, name, size=13, color=col, anchor="end", bold=True))

    # DAT_I рядок: дані дійсні лише в такті ACK (t=3..4)
    yb = 350
    f.append(text(x0 - 12, yb - hi / 2 + 4, "DAT_I", size=13, color=SLV, anchor="end", bold=True))
    f.append(line(x0, yb, x0 + n * unit, yb, color="#d0d5da", sw=0.8))
    dx1, dx2 = x0 + 3 * unit, x0 + 4 * unit
    f.append(line(x0, yb - hi, dx1, yb - hi, color="#c7ccd1", sw=1.6, dash="4 4"))
    f.append(rect(dx1, yb - hi, dx2 - dx1, hi, fill="#eef4ff", stroke=SLV, sw=1.6, rx=4))
    f.append(text((dx1 + dx2) / 2, yb - hi / 2 + 5, "дані", size=12, color=SLV, bold=True))
    f.append(line(dx2, yb - hi, x0 + n * unit, yb - hi, color="#c7ccd1", sw=1.6, dash="4 4"))

    # позначка робочого фронту, де знято рукостискання
    xf = x0 + 4 * unit
    f.append(line(xf, 80, xf, 388, color=INK, sw=1.1, dash="2 4"))
    f.append(text(xf, 408, "фронт, де взято ACK → STB знято, слово прийнято",
                  size=12, color=INK, bold=True))

    render(os.path.join(IMG, "read-cycle.svg"), W, H, *f)


# ── 3. Топології з'єднання того самого інтерфейсу ───────────────────────────
def fig_topologies():
    W, H = 780, 330
    f = [text(W / 2, 28, "Той самий інтерфейс — різні способи зв'язати ведучих і ведених",
              size=16, bold=True)]

    def blk(cx, cy, s, col):
        b, w, h = textbox(cx, cy, s, size=12, pad=8, stroke=col, min_w=64)
        return b

    # (а) точка-точка
    ax = 130
    f.append(text(ax, 66, "точка-точка", size=13, bold=True))
    f.append(blk(ax - 46, 140, "M", MST))
    f.append(blk(ax + 46, 140, "S", SLV))
    f.append(arrow(ax - 30, 140, ax + 30, 140, color=INK, sw=2))
    f.append(text(ax, 210, "один до одного,\nнайпростіше", size=11, color=MUTED))

    # (б) спільна шина
    bx = 400
    f.append(text(bx, 66, "спільна шина", size=13, bold=True))
    busY = 140
    f.append(line(bx - 80, busY, bx + 80, busY, color=INK, sw=3))
    f.append(blk(bx - 60, 100, "M", MST)); f.append(line(bx - 60, 116, bx - 60, busY, color=MST, sw=1.6))
    f.append(blk(bx, 195, "S", SLV));      f.append(line(bx, 179, bx, busY, color=SLV, sw=1.6))
    f.append(blk(bx + 60, 195, "S", SLV)); f.append(line(bx + 60, 179, bx + 60, busY, color=SLV, sw=1.6))
    f.append(text(bx, 250, "усі на одній лінії,\nадреса обирає веденого", size=11, color=MUTED))

    # (в) перехрестя (crossbar)
    cx = 660
    f.append(text(cx, 66, "перехрестя", size=13, bold=True))
    f.append(blk(cx - 40, 100, "M", MST)); f.append(blk(cx + 40, 100, "M", MST))
    f.append(rect(cx - 46, 130, 92, 34, fill="#f0fff4", stroke=OK, sw=1.8, rx=6))
    f.append(text(cx, 151, "комутатор", size=11, color=OK, bold=True))
    f.append(blk(cx - 40, 195, "S", SLV)); f.append(blk(cx + 40, 195, "S", SLV))
    for dx in (-40, 40):
        f.append(line(cx + dx, 116, cx + dx * 0.35, 130, color=MST, sw=1.4))
        f.append(line(cx + dx * 0.35, 164, cx + dx, 179, color=SLV, sw=1.4))
    f.append(text(cx, 250, "кілька пар говорять\nводночас", size=11, color=MUTED))

    render(os.path.join(IMG, "topologies.svg"), W, H, *f)


# ── 4. Звідки назва: «Y» з роздільних шляхів даних ↔ виделкова кісточка ───────
def fig_name_origin():
    BONE = "#b08968"  # кістка — теплий беж
    W, H = 760, 400
    f = [text(W / 2, 30, "Форма схеми, що дала ім'я: роздвоєні дані → «Y» → виделка", size=16, bold=True)]
    f.append(line(W / 2, 60, W / 2, H - 30, color="#d1d5db", sw=1.2, dash="5 6"))

    # ── ЛІВОРУЧ: інженерна причина ────────────────────────────────────────────
    lx = 190
    f.append(text(lx, 70, "інженерна причина", size=13, bold=True, color=MUTED))
    # вузол, з якого розходяться вхід і вихід; спільна тристабільна лінія веде вгору
    node = (lx, 250)
    top = (lx, 120)                    # спільна лінія — вертикальна ніжка «Y»
    outp = (lx - 95, 330)              # вихідна гілка
    inp = (lx + 95, 330)               # вхідна гілка
    f.append(line(node[0], node[1], top[0], top[1], color=INK, sw=3.4))       # ніжка
    f.append(line(node[0], node[1], outp[0], outp[1], color=MST, sw=3.4))     # вихід
    f.append(line(node[0], node[1], inp[0], inp[1], color=SLV, sw=3.4))       # вхід
    f.append(circle(node[0], node[1], 6, fill=INK, stroke=INK))
    # тристабільний буфер на спільній лінії (трикутник) + підпис
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#fff" stroke="%s" stroke-width="2"/>'
             % (lx - 13, 150, lx + 13, 150, lx, 176, INK))
    f.append(text(lx + 20, 152, "тристабільний", size=11, color=INK, anchor="start"))
    f.append(text(lx + 20, 168, "буфер", size=11, color=INK, anchor="start"))
    f.append(text(lx, 108, "спільний провід", size=11, color=MUTED))
    f.append(text(outp[0] - 6, outp[1] + 18, "вихід", size=12, color=MST, bold=True, anchor="middle"))
    f.append(text(inp[0] + 6, inp[1] + 18, "вхід", size=12, color=SLV, bold=True, anchor="middle"))
    f.append(text(lx, H - 22, "два роздільні шляхи даних", size=12, color=MUTED))

    # ── ПРАВОРУЧ: сама кісточка ───────────────────────────────────────────────
    rx = 560
    f.append(text(rx, 70, "форма в природі", size=13, bold=True, color=MUTED))
    # виделкова кісточка: дві дуги, що сходяться донизу, з невеликою ніжкою
    ax, ay = rx, 300                   # нижня вершина
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="8" stroke-linecap="round"/>'
             % (ax, ay, rx - 78, 150, rx - 58, 118, BONE))   # ліва гілка
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="8" stroke-linecap="round"/>'
             % (ax, ay, rx + 78, 150, rx + 58, 118, BONE))   # права гілка
    f.append(line(ax, ay, ax, ay + 30, color=BONE, sw=8))    # коротка ніжка
    f.append(circle(ax, ay, 6, fill=BONE, stroke=BONE))
    f.append(text(rx, H - 22, "виделкова кісточка (англ. wishbone)", size=12, color=MUTED))

    render(os.path.join(IMG, "name-origin.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_read_cycle()
    fig_topologies()
    fig_name_origin()
    print("figs written to", IMG)
