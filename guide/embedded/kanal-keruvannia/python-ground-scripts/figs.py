# -*- coding: utf-8 -*-
"""Фігури до теми «Python для наземних скриптів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CODE_BG = "#1b1f24"      # темна заливка код-панелі
CODE_FG = "#cfe8cf"      # світло-зелений код
AMBER   = "#b08900"      # тепле виділення


# ── 1. Два світи: борт (C, реальний час) vs земля (Python, скрипт) ────────────
# Ідея: різні правила середовища диктують різну мову. Ліворуч — прошивка на
# борту (обмеження, повільний цикл збірки), праворуч — наземний скрипт (воля,
# миттєвий цикл «зміни → запусти»).
def fig_two_worlds():
    W, H = 760, 340
    f = [text(W / 2, 26, "Борт і земля — два світи, тому й різні мови", size=15, bold=True)]

    # ліва панель — БОРТ
    lx, ly, pw, ph = 34, 54, 330, 246
    f.append(rect(lx, ly, pw, ph, fill="#fbfbfb", stroke=POS, sw=1.8, rx=10))
    f.append(text(lx + pw / 2, ly + 26, "БОРТ — прошивка (C / C++)", size=12.5, color=POS, bold=True))
    left = ["• жорсткий реальний час", "• крихти пам'яті, без malloc",
            "• немає ОС — код керує залізом", "• точний контроль такту й байта"]
    for i, s in enumerate(left):
        f.append(text(lx + 18, ly + 54 + i * 26, s, size=10.5, color=INK, anchor="start"))
    # цикл збірки — повільний
    cyc = ly + 54 + len(left) * 26 + 8
    f.append(rect(lx + 14, cyc, pw - 28, 46, fill="#fdecea", stroke=POS, sw=1.3, rx=8))
    f.append(text(lx + pw / 2, cyc + 19, "зміни → скомпілюй → проший → перевір",
                  size=9.8, color=INK, bold=True))
    f.append(text(lx + pw / 2, cyc + 36, "цикл спроби — повільний", size=9, color=MUTED, italic=True))

    # права панель — ЗЕМЛЯ
    rx = 396
    f.append(rect(rx, ly, pw, ph, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + pw / 2, ly + 26, "ЗЕМЛЯ — скрипт (Python)", size=12.5, color=FIELD, bold=True))
    right = ["• звичайний ПК, ОС, багато пам'яті", "• немає жорстких дедлайнів",
             "• готові бібліотеки (pip)", "• цінується швидкість написання"]
    for i, s in enumerate(right):
        f.append(text(rx + 18, ly + 54 + i * 26, s, size=10.5, color=INK, anchor="start"))
    cyc2 = ly + 54 + len(right) * 26 + 8
    f.append(rect(rx + 14, cyc2, pw - 28, 46, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(rx + pw / 2, cyc2 + 19, "зміни → запусти", size=9.8, color=INK, bold=True))
    f.append(text(rx + pw / 2, cyc2 + 36, "цикл спроби — миттєвий", size=9, color=MUTED, italic=True))

    render(os.path.join(IMG, "two-worlds.svg"), W, H, *f)


# ── 2. Одна лінія — три транспорти ───────────────────────────────────────────
# Ідея: серійний порт / UDP / TCP зводяться до одного рядка з'єднання; далі код
# однаковий. Транспорт — деталь налаштування.
def fig_connection_string():
    W, H = 760, 300
    f = [text(W / 2, 26, "Одна лінія, три транспорти — код той самий", size=15, bold=True)]

    # три джерела ліворуч
    srcs = [("серійний порт", "COM5 / ttyUSB0", NEG),
            ("UDP", "udpin:...:14550", FIELD),
            ("TCP", "tcp:...:5760", AMBER)]
    sx, sw_, sh = 30, 180, 46
    ys = [64, 128, 192]
    for (name, sub, col), y in zip(srcs, ys):
        f.append(rect(sx, y, sw_, sh, fill="#fbfbfb", stroke=col, sw=1.7, rx=8))
        f.append(text(sx + sw_ / 2, y + 20, name, size=11.5, color=col, bold=True))
        f.append(text(sx + sw_ / 2, y + 37, sub, size=9.5, color=INK))

    # вузол «рядок з'єднання»
    nx, ny, nw, nh = 300, 116, 160, 60
    f.append(rect(nx, ny, nw, nh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(nx + nw / 2, ny + 26, "рядок", size=11.5, color=FIELD, bold=True))
    f.append(text(nx + nw / 2, ny + 44, "з'єднання", size=11.5, color=FIELD, bold=True))
    for y in ys:
        f.append(arrow(sx + sw_ + 4, y + sh / 2, nx - 4, ny + nh / 2, color=INK, sw=1.6))

    # спільний код праворуч
    cx, cy, cw, ch = 512, 96, 218, 100
    f.append(rect(cx, cy, cw, ch, fill=CODE_BG, stroke=INK, sw=1.5, rx=8))
    for i, ln in enumerate(["той самий код:", "• дочекатися heartbeat",
                            "• читати потік", "• слати команди"]):
        col = "#9fb0c0" if i == 0 else CODE_FG
        f.append(text(cx + 14, cy + 24 + i * 20, ln, size=10, color=col, anchor="start"))
    f.append(arrow(nx + nw + 4, ny + nh / 2, cx - 4, cy + ch / 2, color=FIELD, sw=2.2))

    f.append(text(W / 2, H - 12,
                  "перемкнути симулятор на реальний модем — це змінити один рядок",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "connection-string.svg"), W, H, *f)


# ── 3. Скелет наземного скрипта ──────────────────────────────────────────────
# Ідея: будь-який наземний скрипт — це та сама послідовність: відкрити лінію →
# дочекатися heartbeat → подієвий цикл читай/вирішуй/командуй.
def fig_ground_loop():
    W, H = 760, 320
    f = [text(W / 2, 26, "Форма будь-якого наземного скрипта", size=15, bold=True)]

    # вступ: два кроки згори
    step_w, step_h = 250, 46
    cx0 = (W - step_w) / 2
    f.append(rect(cx0, 56, step_w, step_h, fill="#fbfbfb", stroke=INK, sw=1.7, rx=8))
    f.append(text(cx0 + step_w / 2, 56 + 28, "1) відкрити лінію (рядок з'єднання)",
                  size=10.5, color=INK, bold=True))
    f.append(arrow(W / 2, 56 + step_h, W / 2, 118, color=INK, sw=2))
    f.append(rect(cx0, 120, step_w, step_h, fill="#fff8e8", stroke=AMBER, sw=1.7, rx=8))
    f.append(text(cx0 + step_w / 2, 120 + 20, "2) дочекатися HEARTBEAT", size=10.5, color=AMBER, bold=True))
    f.append(text(cx0 + step_w / 2, 120 + 37, "(тут узяли адресу апарата)", size=9, color=MUTED, italic=True))

    # рамка циклу
    bx, by, bw, bh = 150, 186, 460, 104
    f.append(rect(bx, by, bw, bh, fill="#f3f7f3", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(bx + 14, by + 20, "3) подієвий цикл:", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(arrow(W / 2, 120 + step_h, W / 2, by, color=INK, sw=2))

    # три кроки циклу в ряд
    inner = [("читай", "повідомлення\nз потоку", NEG),
             ("вирішуй", "за своєю\nлогікою", INK),
             ("командуй", "+ дочекайся\nACK", POS)]
    iw, gap = 128, 22
    ix = bx + (bw - (iw * 3 + gap * 2)) / 2
    iy = by + 30
    centers = []
    for name, sub, col in inner:
        f.append(rect(ix, iy, iw, 58, fill="#ffffff", stroke=col, sw=1.6, rx=8))
        f.append(text(ix + iw / 2, iy + 21, name, size=11, color=col, bold=True))
        f.append(mtext(ix + iw / 2, iy + 37, sub.split("\n"), size=9, color=INK))
        centers.append(ix + iw / 2)
        ix += iw + gap
    f.append(arrow(bx + (bw - (iw * 3 + gap * 2)) / 2 + iw + 2, iy + 29,
                   centers[1] - iw / 2 - 2, iy + 29, color=INK, sw=1.5))
    f.append(arrow(centers[1] + iw / 2 + 2, iy + 29,
                   centers[2] - iw / 2 - 2, iy + 29, color=INK, sw=1.5))

    render(os.path.join(IMG, "ground-loop.svg"), W, H, *f)


# ── 4. Два виходи: без finally (катастрофа) vs із finally (безпечно) ──────────
# Ідея вставки: наївний скрипт, вилетівши, лишає мотори озброєними; той самий
# скрипт із блоком finally при БУДЬ-ЯКОМУ виході гарантовано роззброює.
def fig_two_exits():
    W, H = 770, 360
    f = [text(W / 2, 26, "Той самий виняток — два різні кінці", size=15, bold=True)]

    # спільний старт
    top_w, top_h = 220, 40
    tx = (W - top_w) / 2
    f.append(rect(tx, 46, top_w, top_h, fill="#fff8e8", stroke=AMBER, sw=1.7, rx=8))
    f.append(text(tx + top_w / 2, 46 + 25, "скрипт озброїв мотори", size=11, color=AMBER, bold=True))

    # роздвоєння вниз
    lcx, rcx = 200, 570
    f.append(arrow(W / 2, 46 + top_h, lcx, 108, color=INK, sw=1.7))
    f.append(arrow(W / 2, 46 + top_h, rcx, 108, color=INK, sw=1.7))

    # спільна подія-збій
    ey = 108
    for cx in (lcx, rcx):
        f.append(rect(cx - 108, ey, 216, 38, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
        f.append(text(cx, ey + 24, "Ctrl+C / виняток / kill", size=10, color=POS, bold=True))

    # ── ЛІВА гілка: наївний скрипт ──
    ly = 176
    f.append(rect(lcx - 118, ly, 236, 150, fill="#fdecea", stroke=POS, sw=2, rx=12))
    f.append(text(lcx, ly + 22, "БЕЗ finally (наївно)", size=11.5, color=POS, bold=True))
    naive = ["процес помирає миттєво", "мотори лишаються озброєними",
             "остання команда «лети» — в силі"]
    for i, s in enumerate(naive):
        f.append(text(lcx, ly + 46 + i * 22, s, size=9.7, color=INK))
    f.append(rect(lcx - 100, ly + 112, 200, 30, fill="#ffffff", stroke=POS, sw=1.6, rx=7))
    f.append(text(lcx, ly + 112 + 20, "⚠ апарат небезпечний", size=10.5, color=POS, bold=True))

    # ── ПРАВА гілка: із finally ──
    ry = 176
    f.append(rect(rcx - 118, ry, 236, 150, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(rcx, ry + 22, "з finally (шаблон)", size=11.5, color=FIELD, bold=True))
    safe = ["finally виконується хай там що", "на землі → роззброїти", "лінію закрити, стан безпечний"]
    for i, s in enumerate(safe):
        f.append(text(rcx, ry + 46 + i * 22, s, size=9.7, color=INK))
    f.append(rect(rcx - 100, ry + 112, 200, 30, fill="#ffffff", stroke=FIELD, sw=1.6, rx=7))
    f.append(text(rcx, ry + 112 + 20, "✓ борт у безпеці", size=10.5, color=FIELD, bold=True))

    f.append(arrow(lcx, ey + 38, lcx, ly, color=POS, sw=1.7))
    f.append(arrow(rcx, ey + 38, rcx, ry, color=FIELD, sw=1.7))

    render(os.path.join(IMG, "two-exits.svg"), W, H, *f)


# ── 5. Які виходи ловить finally, а які треба перехопити окремо ───────────────
# Ідея: try/finally покриває Ctrl+C і винятки; SIGTERM (kill) убиває процес до
# finally — треба обробник сигналу; SIGKILL і зникнення живлення не ловить ніхто.
def fig_exit_coverage():
    W, H = 780, 330
    f = [text(W / 2, 26, "finally ловить не все — що ще треба перехопити", size=15, bold=True)]

    rows = [
        ("Ctrl+C (SIGINT)", "→ KeyboardInterrupt", "finally ВИКОНАЄТЬСЯ", FIELD, "✓"),
        ("виняток у коді", "звичайна помилка", "finally ВИКОНАЄТЬСЯ", FIELD, "✓"),
        ("kill (SIGTERM)", "система гасить процес", "потрібен обробник сигналу", AMBER, "!"),
        ("SIGKILL / -9", "процес убито миттєво", "не ловить НІХТО", POS, "✗"),
        ("зникло живлення", "ноут вимкнувся", "рятує лише борт (failsafe)", POS, "✗"),
    ]
    x, y0, rw, rh, gap = 60, 56, 660, 44, 8
    for i, (evt, sub, verdict, col, mark) in enumerate(rows):
        y = y0 + i * (rh + gap)
        f.append(rect(x, y, rw, rh, fill="#fbfbfb", stroke=col, sw=1.7, rx=9))
        # марка
        f.append(circle(x + 26, y + rh / 2, 13, fill="#ffffff", stroke=col, sw=2))
        f.append(text(x + 26, y + rh / 2 + 6, mark, size=15, color=col, bold=True))
        # подія
        f.append(text(x + 52, y + 19, evt, size=11, color=INK, anchor="start", bold=True))
        f.append(text(x + 52, y + 35, sub, size=9, color=MUTED, anchor="start", italic=True))
        # вирок
        f.append(text(x + rw - 16, y + rh / 2 + 5, verdict, size=10.5, color=col, anchor="end", bold=True))

    render(os.path.join(IMG, "exit-coverage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_worlds()
    fig_connection_string()
    fig_ground_loop()
    fig_two_exits()
    fig_exit_coverage()
    print("OK: 5 figures ->", IMG)
