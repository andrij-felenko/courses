# -*- coding: utf-8 -*-
"""Фігури до теми «Регістр» і до вставки «74HC165».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до теми «Регістр»
# ════════════════════════════════════════════════════════════════════════════

def _ff(f, x, y, w=66, h=72, label="D", q="Q", din="D", clk_y=None):
    """Намалювати один тригер: рамка, вхід D зверху, вихід Q знизу, мітка ◁ такту."""
    f.append(rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(x + w / 2, y + h / 2 - 4, label, size=12, bold=True))
    # мітка фронту такту (трикутник) на лівій грані
    cy = y + h - 16 if clk_y is None else clk_y
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6"/>' % (x, cy - 7, x + 11, cy, x, cy + 7, LINE))
    return x + w / 2  # центр по X (для виводів)


# ── Паралельний регістр: 8 тригерів зі спільним тактом = байт ────────────────
def fig_parallel_register():
    W, H = 760, 320
    f = []
    n = 8
    w = 66
    gap = 18
    x0 = (W - (n * w + (n - 1) * gap)) / 2
    yb = 110
    h = 76
    for i in range(n):
        x = x0 + i * (w + gap)
        cx = _ff(f, x, yb, w=w, h=h, label="тр")
        # вхід Di зверху
        f.append(line(cx, yb - 28, cx, yb, color=INK, sw=1.6))
        f.append(text(cx, yb - 34, "D%d" % i, size=11, bold=True))
        # вихід Qi знизу
        f.append(line(cx, yb + h, cx, yb + h + 24, color=FIELD, sw=1.6))
        f.append(text(cx, yb + h + 38, "Q%d" % i, size=11, color=FIELD, bold=True))

    # спільна шина такту (червона), знизу до міток фронту
    clk_y = yb + h - 16
    bus_y = yb + h + 58
    f.append(line(x0 - 24, bus_y, x0 + n * w + (n - 1) * gap + 8, bus_y, color=POS, sw=2.2))
    f.append(text(x0 - 30, bus_y + 4, "такт", size=12, color=POS, bold=True, anchor="end"))
    for i in range(n):
        x = x0 + i * (w + gap)
        f.append(line(x, clk_y, x, bus_y, color=POS, sw=1.4))
        f.append(circle(x, bus_y, 3.0, fill=POS, stroke=POS, sw=1))

    f.append(text(W / 2, 36, "Вісім тригерів зі спільним тактом — це 8-бітний регістр",
                  size=15, bold=True))
    f.append(text(W / 2, H - 16,
                  "Один фронт спільного такту — і всі вісім бітів записано разом, як один байт.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "parallel-register.svg"), W, H, *f)


# ── Дозвіл запису: MUX обирає «нові дані» або «власний Q» ────────────────────
def fig_load_enable():
    W, H = 620, 300
    f = []
    # MUX (трапеція)
    mx, my = 200, 90
    mw, mh = 70, 120
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
             'fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (mx, my, mx + mw, my + 26, mx + mw, my + mh - 26, mx, my + mh, FILL, LINE))
    f.append(text(mx + mw / 2 - 2, my + mh / 2 + 4, "MUX", size=12, bold=True))
    # два входи MUX
    f.append(arrow(70, my + 24, mx, my + 24, color=INK, sw=1.8))
    f.append(text(66, my + 20, "нові дані", size=11, bold=True, anchor="end"))
    f.append(arrow(70, my + mh - 24, mx, my + mh - 24, color=FIELD, sw=1.8))
    f.append(text(66, my + mh - 28, "Q (зворотний зв'язок)", size=11, color=FIELD, bold=True, anchor="end"))
    # керування load
    f.append(arrow(mx + mw / 2, my + mh + 40, mx + mw / 2, my + mh, color=POS, sw=1.8))
    f.append(text(mx + mw / 2, my + mh + 56, "load", size=12, color=POS, bold=True))

    # тригер
    tx, ty = 360, my + 14
    tw, th = 90, mh - 28
    f.append(rect(tx, ty, tw, th, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(tx + tw / 2, ty + th / 2 + 4, "тригер", size=12, bold=True))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6"/>' % (tx, ty + th - 18 - 7, tx + 11, ty + th - 18, tx, ty + th - 18 + 7, LINE))
    # MUX → D
    f.append(arrow(mx + mw, my + mh / 2, tx, ty + th / 2, color=INK, sw=1.8))
    f.append(text((mx + mw + tx) / 2, my + mh / 2 - 8, "D", size=11, bold=True))
    # Q вихід
    f.append(line(tx + tw, ty + th / 2, tx + tw + 70, ty + th / 2, color=FIELD, sw=1.8))
    f.append(text(tx + tw + 78, ty + th / 2 + 4, "Q", size=12, color=FIELD, bold=True, anchor="start"))
    # зворотний зв'язок Q → нижній вхід MUX
    fb_y = my + mh + 14
    f.append(line(tx + tw + 50, ty + th / 2, tx + tw + 50, fb_y, color=FIELD, sw=1.4))
    f.append(line(tx + tw + 50, fb_y, 50, fb_y, color=FIELD, sw=1.4))
    f.append(line(50, fb_y, 50, my + mh - 24, color=FIELD, sw=1.4))
    f.append(line(50, my + mh - 24, 70, my + mh - 24, color=FIELD, sw=1.4))

    f.append(text(W / 2, 34, "Дозвіл запису: MUX обирає, чим годувати тригер", size=15, bold=True))
    f.append(text(W / 2, H - 14,
                  "load=1 — записати нові дані; load=0 — повернути власний Q, тобто триматися без змін.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "load-enable.svg"), W, H, *f)


# ── Зсувний регістр: ланцюжок тригерів + три типи (SIPO/PISO/SISO) ───────────
def fig_shift_register():
    W, H = 720, 340
    f = []
    n = 4
    w = 76
    gap = 34
    x0 = 110
    yb = 96
    h = 70
    centers = []
    for i in range(n):
        x = x0 + i * (w + gap)
        cx = _ff(f, x, yb, w=w, h=h, label="тр %d" % i)
        centers.append((x, cx))
    # послідовний вхід зліва
    f.append(arrow(x0 - 56, yb + h / 2, x0, yb + h / 2, color=INK, sw=1.8))
    f.append(text(x0 - 60, yb + h / 2 - 6, "вхід", size=11, bold=True, anchor="end"))
    # ланцюг: Q одного → D наступного
    for i in range(n - 1):
        x, cx = centers[i]
        nx = centers[i + 1][0]
        f.append(arrow(x + w, yb + h / 2, nx, yb + h / 2, color=FIELD, sw=1.8))
    # вихід справа
    lastx = centers[-1][0]
    f.append(arrow(lastx + w, yb + h / 2, lastx + w + 50, yb + h / 2, color=FIELD, sw=1.8))
    f.append(text(lastx + w + 56, yb + h / 2 + 4, "вихід", size=11, color=FIELD, bold=True, anchor="start"))
    # спільний такт
    bus_y = yb + h + 34
    f.append(line(x0 - 24, bus_y, lastx + w + 8, bus_y, color=POS, sw=2.2))
    f.append(text(x0 - 30, bus_y + 4, "такт", size=12, color=POS, bold=True, anchor="end"))
    for i in range(n):
        x = centers[i][0]
        f.append(line(x, yb + h - 16, x, bus_y, color=POS, sw=1.4))
        f.append(circle(x, bus_y, 3.0, fill=POS, stroke=POS, sw=1))

    # три типи — три рядки знизу
    rows = [
        ("SIPO", "вхід послідовний (1 дріт) → виходи всі Q разом"),
        ("PISO", "завантажили все паралельно → виводимо по 1 дроту"),
        ("SISO", "вхід і вихід послідовні — проста лінія затримки"),
    ]
    ry = bus_y + 34
    for name, desc in rows:
        f.append(text(x0 - 30, ry + 4, name, size=12, color=NEG, bold=True, anchor="start"))
        f.append(text(x0 + 56, ry + 4, desc, size=11, color=MUTED, anchor="start"))
        ry += 24

    f.append(text(W / 2, 34, "Зсувний регістр: вихід кожного тригера — на вхід наступного",
                  size=15, bold=True))
    render(os.path.join(IMG, "shift-register.svg"), W, H, *f)


# ── Серійно ↔ паралельно ─────────────────────────────────────────────────────
def fig_serial_parallel():
    W, H = 720, 320
    f = []
    # ліворуч: один дріт із бітами по черзі
    sx = 70
    sy = 150
    f.append(line(sx, sy, sx + 150, sy, color=INK, sw=2.0))
    bits = "10110010"
    for i, b in enumerate(bits):
        bx = sx + 14 + i * 17
        f.append(text(bx, sy - 10, b, size=12, bold=True,
                      color=POS if b == "1" else NEG))
    f.append(text(sx + 75, sy + 22, "по одному дроту,", size=11, color=MUTED))
    f.append(text(sx + 75, sy + 38, "біти по черзі в часі", size=11, color=MUTED))

    # регістр SIPO у центрі
    rx, ry, rw, rh = 250, 100, 150, 110
    f.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(rx + rw / 2, ry + rh / 2 - 6, "зсувний", size=13, bold=True))
    f.append(text(rx + rw / 2, ry + rh / 2 + 12, "регістр (SIPO)", size=12, bold=True))
    f.append(arrow(sx + 150, sy, rx, sy, color=INK, sw=2.0))

    # праворуч: 8 паралельних виходів
    n = 8
    oy0 = ry + 8
    ostep = (rh - 16) / (n - 1)
    for i in range(n):
        yy = oy0 + i * ostep
        f.append(arrow(rx + rw, yy, rx + rw + 60, yy, color=FIELD, sw=1.6))
    f.append(text(rx + rw + 66, ry + rh / 2 + 4, "8 бітів разом", size=11, color=FIELD, bold=True, anchor="start"))

    f.append(text(W / 2, 34, "Серійно ↔ паралельно: серце послідовного зв'язку", size=15, bold=True))
    f.append(text(W / 2, H - 14,
                  "SIPO збирає байт із потоку бітів; PISO робить зворотне — це і є нутро UART, SPI, USB.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "serial-parallel.svg"), W, H, *f)


# ── Регістри в процесорі: регістровий файл ↔ АЛП ─────────────────────────────
def fig_registers_in_processor():
    W, H = 700, 360
    f = []
    # регістровий файл зліва
    rx, ry, rw, rh = 70, 90, 170, 180
    f.append(rect(rx, ry, rw, rh, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(rx + rw / 2, ry - 10, "регістровий файл", size=12, bold=True))
    for i in range(4):
        yy = ry + 22 + i * 38
        f.append(rect(rx + 18, yy, rw - 36, 26, fill="#eef2f7", stroke=LINE, sw=1.2))
        f.append(text(rx + rw / 2, yy + 18, "R%d" % i, size=11, bold=True))

    # АЛП праворуч (характерна форма ALU)
    ax, ay, aw, ah = 420, 110, 150, 140
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f '
             'L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, ay, ax + aw, ay, ax + aw, ay + ah, ax, ay + ah,
                ax, ay + ah * 0.62, ax + aw * 0.18, ay + ah / 2, ax, ay + ah * 0.38,
                "#eaf3ec", FIELD))
    f.append(text(ax + aw / 2 + 6, ay + ah / 2 + 5, "АЛП", size=15, bold=True))

    # два операнди: рег.файл → АЛП
    f.append(arrow(rx + rw, ry + 50, ax, ay + 30, color=INK, sw=1.8))
    f.append(text((rx + rw + ax) / 2, ry + 32, "операнд A", size=10, bold=True))
    f.append(arrow(rx + rw, ry + 130, ax, ay + ah - 30, color=INK, sw=1.8))
    f.append(text((rx + rw + ax) / 2, ry + 150, "операнд B", size=10, bold=True))

    # результат: АЛП → назад у рег.файл (дугою зверху)
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (ax + aw / 2, ay, ax + aw / 2, ay - 60, rx + rw / 2, ry - 60, rx + rw / 2, ry,
                POS))
    f.append(text((ax + rx + rw) / 2, ry - 66, "результат", size=10, color=POS, bold=True))

    # спеціальні регістри — підпис знизу
    f.append(text(W / 2, ry + rh + 36,
                  "Окремо — спеціальні регістри: лічильник команд (PC), регістр інструкції, прапорці.",
                  size=11, color=MUTED))
    f.append(text(W / 2, ry + rh + 58,
                  "Регістри + АЛП = тракт даних; додати керування — і це вже процесор.",
                  size=11, color=MUTED))

    f.append(text(W / 2, 36, "Регістри тримають числа, АЛП їх обробляє", size=15, bold=True))
    render(os.path.join(IMG, "registers-in-processor.svg"), W, H, *f)


# ── Фігура 1: 8 кнопок → 3 лінії МК (навіщо потрібен PISO) ──────────────────
def fig_buttons_to_three_lines():
    W, H = 780, 470
    f = [text(W / 2, 28, "Вісім кнопок крізь 74HC165 — лише три дроти до мікроконтролера",
              size=15, bold=True)]

    # вісім кнопок ліворуч
    bx = 60
    top = 70
    gap = 42
    for i in range(8):
        cy = top + i * gap
        f.append(circle(bx, cy, 9, fill="#eef2f7", stroke=LINE, sw=1.4))
        f.append(text(bx - 22, cy + 4, "D%d" % i, size=11, color=MUTED, anchor="end"))
        f.append(line(bx + 9, cy, 250, cy, color=MUTED, sw=1.3))

    # корпус 74HC165
    cx0, cy0, cw, ch = 250, top - 14, 150, 7 * gap + 28
    f.append(rect(cx0, cy0, cw, ch, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(cx0 + cw / 2, cy0 + ch / 2 - 8, "74HC165", size=15, bold=True))
    f.append(text(cx0 + cw / 2, cy0 + ch / 2 + 12, "PISO", size=12, color=MUTED))
    f.append(text(cx0 + cw / 2, cy0 - 8, "8 паралельних входів D0..D7", size=10, color=MUTED))

    # три лінії праворуч до МК
    mx = 560
    mcu_y = top + 3 * gap
    sigs = [("PL  (защіпка)", mcu_y - gap, POS),
            ("CP  (такт)",    mcu_y,       INK),
            ("Q7  (дані)",    mcu_y + gap, FIELD)]
    for name, yy, col in sigs:
        f.append(arrow(cx0 + cw, yy, mx, yy, color=col, sw=2.0))
        f.append(text((cx0 + cw + mx) / 2, yy - 8, name, size=11, color=col, bold=True))

    # МК
    f.append(rect(mx, top - 14, 150, 7 * gap + 28, fill="#eef2f7", stroke=LINE, sw=1.8))
    f.append(text(mx + 75, mcu_y - 4, "Мікро-", size=14, bold=True))
    f.append(text(mx + 75, mcu_y + 16, "контролер", size=14, bold=True))
    f.append(text(mx + 75, top + 7 * gap + 6, "3 піни", size=11, color=MUTED))

    # підсумок унизу
    f.append(text(W / 2, H - 18,
                  "8 входів коштують 8 пінів навпростець — або 3 піни через регістр (і так само для 16, 24, 32...).",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "buttons-to-three-lines.svg"), W, H, *f)


# ── Фігура 2: защіпнути, тоді висунути — часова діаграма ─────────────────────
def fig_load_then_shift():
    W, H = 820, 430
    f = [text(W / 2, 28, "Один цикл читання: PL защіпає вісім входів, потім CP висуває їх по одному в Q7",
              size=14, bold=True)]

    # геометрія доріжок
    x0 = 130           # початок осі часу
    x1 = 780           # кінець
    hi = 22            # висота рівня «1» над базовою лінією
    rows = [("PL", 90, POS),
            ("CP", 170, INK),
            ("Q7", 250, FIELD)]
    for name, yb, col in rows:
        f.append(text(x0 - 14, yb - hi / 2 + 4, name, size=13, color=col, bold=True, anchor="end"))
        f.append(line(x0, yb, x1, yb, color=MUTED, sw=1.0))  # базова лінія «0»

    # часові межі: фаза LOAD, тоді 8 тактів SHIFT
    load_w = 90
    n = 8
    clk_w = (x1 - (x0 + load_w) - 20) / n   # ширина одного такту

    # ── PL: спадає в LOW на час завантаження, далі HIGH ──
    yb = 90
    # старт HIGH
    f.append(line(x0, yb - hi, x0 + 16, yb - hi, color=POS, sw=2.4))
    f.append(line(x0 + 16, yb - hi, x0 + 16, yb, color=POS, sw=2.4))      # ↓ в LOW
    f.append(line(x0 + 16, yb, x0 + load_w, yb, color=POS, sw=2.4))       # LOW = load
    f.append(line(x0 + load_w, yb, x0 + load_w, yb - hi, color=POS, sw=2.4))  # ↑ назад
    f.append(line(x0 + load_w, yb - hi, x1, yb - hi, color=POS, sw=2.4))
    f.append(text(x0 + (16 + load_w) / 2, yb + 18, "PL=0: захопити D0..D7", size=10, color=POS))
    f.append(text(x0 + (load_w + x1) / 2, yb - hi - 8, "PL=1: режим зсуву", size=10, color=POS))

    # ── CP: тихо під час load, тоді 8 імпульсів ──
    yb = 170
    cx = x0
    f.append(line(x0, yb, x0 + load_w, yb, color=INK, sw=2.4))  # тихо
    cx = x0 + load_w
    for i in range(n):
        # імпульс: ↑ half, ↓ half
        f.append(line(cx, yb, cx + clk_w * 0.25, yb, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.25, yb, cx + clk_w * 0.25, yb - hi, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.25, yb - hi, cx + clk_w * 0.75, yb - hi, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.75, yb - hi, cx + clk_w * 0.75, yb, color=INK, sw=2.4))
        f.append(line(cx + clk_w * 0.75, yb, cx + clk_w, yb, color=INK, sw=2.4))
        cx += clk_w
    f.append(text(x0 + load_w + (x1 - x0 - load_w) / 2, yb + 18, "8 фронтів CP — по одному на біт", size=10, color=INK))

    # ── Q7: показує D0, потім D1... на кожному фронті ──
    yb = 250
    bits = [1, 0, 1, 1, 0, 0, 1, 0]   # приклад зчитаних бітів
    f.append(line(x0, yb, x0 + load_w, yb, color=FIELD, sw=2.4))  # D0 вже на виході після load? показуємо з 1-го такту
    cx = x0 + load_w
    prev = None
    for i in range(n):
        lvl = yb - hi if bits[i] else yb
        if prev is not None and prev != lvl:
            f.append(line(cx, prev, cx, lvl, color=FIELD, sw=2.4))  # перехід
        f.append(line(cx, lvl, cx + clk_w, lvl, color=FIELD, sw=2.4))
        f.append(text(cx + clk_w / 2, yb + 18, "D%d" % i, size=10, color=FIELD))
        prev = lvl
        cx += clk_w

    # легенда рівнів
    f.append(text(x1 + 0, 90 - hi - 8, "", size=10))
    f.append(text(W / 2, H - 20,
                  "Перший фронт CP виставляє найстарший защіпнутий біт у Q7; кожен наступний фронт зсуває низку далі.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "load-then-shift.svg"), W, H, *f)


if __name__ == "__main__":
    # тема «Регістр»
    fig_parallel_register()
    fig_load_enable()
    fig_shift_register()
    fig_serial_parallel()
    fig_registers_in_processor()
    # вставка «74HC165»
    fig_buttons_to_three_lines()
    fig_load_then_shift()
    print("OK: figures written to", IMG)
