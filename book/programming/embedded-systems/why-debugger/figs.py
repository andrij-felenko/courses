# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── print-vs-halt: друк опитує живе на ходу; halt зупиняє час ──────────────────
# Ідея: ліворуч CPU біжить — встигаємо спитати лише те, що самі заклали в друк;
# праворуч CPU завмер між командами — читаємо все, що захочемо.

def fig_print_vs_halt():
    W, H = 760, 360
    p = []
    midx = W / 2

    # ── ліва панель: друк ──
    p.append(rect(20, 50, 330, 280, fill="#fff8f0", stroke=POS, sw=2, rx=10))
    p.append(text(185, 80, "ДРУК (Serial.print)", size=15, color=POS, bold=True))
    p.append(circle(120, 175, 26, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(120, 180, "CPU", size=13, color=POS, bold=True))
    p.append(arrow(150, 175, 215, 175, color=POS, sw=2))
    p.append(text(255, 179, "біжить →", size=12, color=POS))
    p.append(line(185, 205, 185, 235, color=MUTED, sw=1.5, dash="4 3"))
    p.append(fitbox(140, 240, 90, 30, "? де ти ?", size=12, fill="#fff3e0", stroke=POS, sw=1.5, bold=True, color=POS))
    p.append(text(185, 292, "видно лише те,", size=11, color=MUTED))
    p.append(text(185, 307, "що сам заклав у друк", size=11, color=MUTED))

    # ── права панель: halt ──
    p.append(rect(410, 50, 330, 280, fill="#f0f8ff", stroke=NEG, sw=2, rx=10))
    p.append(text(575, 80, "ВІДЛАГОДЖУВАЧ (halt)", size=15, color=NEG, bold=True))
    p.append(circle(490, 175, 26, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(490, 180, "CPU", size=13, color=NEG, bold=True))
    p.append(fitbox(450, 213, 80, 30, "завмер", size=12, fill="#eaf0fd", stroke=NEG, sw=1.5, bold=True, color=NEG))
    p.append(text(615, 165, "читаємо:", size=12, color=INK))
    p.append(text(615, 185, "• будь-який регістр", size=11, color=FIELD))
    p.append(text(615, 205, "• будь-яку пам'ять", size=11, color=FIELD))
    p.append(text(615, 225, "• весь стек викликів", size=11, color=FIELD))
    p.append(fitbox(440, 285, 270, 30, "час зупинено — читаємо все", size=11, fill="#e8f8f0", stroke=FIELD, sw=1.2, bold=True, color=FIELD))

    p.append(line(midx, 60, midx, 320, color=MUTED, sw=1.0, dash="6 4"))

    render(os.path.join(OUT, "print-vs-halt.svg"), W, H, *p,
           title="Друк опитує на ходу; відлагоджувач зупиняє час і оглядає нерухоме")


# ── print-vs-debugger: таблиця порівняння двох інструментів ───────────────────
# Ідея: п'ять рядків-критеріїв; видно, що це не «краще/гірше», а різні сили —
# друк для потоку, відлагоджувач для локалізації.

def fig_print_vs_debugger():
    W, H = 820, 380
    p = []
    # колонки
    c0x, c0w = 30, 200       # критерій
    c1x, c1w = 240, 270      # друк
    c2x, c2w = 520, 270      # відлагоджувач
    hy, hh = 48, 46          # шапка
    ry, rh = hy + hh, 50     # рядки

    # шапка
    for x, w, lab in [(c0x, c0w, "Критерій"), (c1x, c1w, "Serial.print"), (c2x, c2w, "Відлагоджувач")]:
        p.append(rect(x, hy, w, hh, fill="#2d3e50", stroke=LINE, sw=1.2, rx=6))
        p.append(text(x + w / 2, hy + 29, lab, size=13, color="#ffffff", bold=True))

    rows = [
        ("Що бачить?", "лише надруковане\nнаперед", "всю пам'ять,\nрегістри, стек"),
        ("Вплив на час", "малий\n(якщо рядок короткий)", "зупиняє ядро —\nрве реальний час"),
        ("Потрібен зонд?", "ні — лише UART", "так — зонд\nабо USB-JTAG"),
        ("Сильний у", "потоковому\nспостереженні", "локалізації збою\nй аналізі стану"),
        ("Heisenbug", "може приховати\n(змінює час)", "не ховає —\nядро завмерло"),
    ]
    for i, (crit, a, b) in enumerate(rows):
        y = ry + i * rh
        shade = "#f4f6f8" if i % 2 == 0 else "#edf2f7"
        p.append(fitbox(c0x, y, c0w, rh, crit, size=12, fill=shade, stroke=LINE, sw=1.5, rx=4))
        p.append(fitbox(c1x, y, c1w, rh, a, size=12, fill=shade, stroke=LINE, sw=1.5, rx=4))
        p.append(fitbox(c2x, y, c2w, rh, b, size=12, fill=shade, stroke=LINE, sw=1.5, rx=4))

    render(os.path.join(OUT, "print-vs-debugger.svg"), W, H, *p,
           title="Друк і відлагоджувач не змагаються — це різні сили")


# ── boundary-scan: «цвяхи» всередині кремнію ──────────────────────────────────
# Ідея: біля кожного виводу — реєстрова клітинка; усі зшиті в один ланцюг, тож
# стан ніжки читається/задається без фізичного дотику (рятує під BGA).

def fig_boundary_scan():
    W, H = 760, 380
    p = []
    # ядро в центрі
    kx, ky, kw, kh = 280, 130, 200, 120
    p.append(rect(kx, ky, kw, kh, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(kx + kw / 2, ky + kh / 2 + 5, "ЯДРО", size=16, color=NEG, bold=True))

    # клітинки навколо ядра (по периметру) + зовнішні «ніжки»
    cells = []  # (cx, cy) центр клітинки
    # верх і низ
    for i in range(4):
        cx = kx + 30 + i * (kw - 60) / 3
        cells.append((cx, ky - 28, cx, ky - 70))          # клітинка зверху, ніжка вище
        cells.append((cx, ky + kh + 28, cx, ky + kh + 70))  # знизу
    # боки
    for i in range(2):
        cy = ky + 35 + i * (kh - 70)
        cells.append((kx - 28, cy, kx - 70, cy))           # ліворуч
        cells.append((kx + kw + 28, cy, kx + kw + 70, cy)) # праворуч

    for (cx, cy, px, py) in cells:
        # ніжка
        p.append(circle(px, py, 6, fill=FILL, stroke=LINE, sw=1.4))
        # лінія ніжка→клітинка
        p.append(line(px, py, cx, cy, color=MUTED, sw=1.2))
        # клітинка-реєстр
        p.append(rect(cx - 11, cy - 8, 22, 16, fill="#fff3e0", stroke=POS, sw=1.4, rx=3))

    # послідовний ланцюг крізь клітинки (схематично — пунктир по колу)
    order = sorted(cells, key=lambda c: (c[1], c[0]))
    chain = []
    for (cx, cy, _, _) in order:
        chain.append("%.1f,%.1f" % (cx, cy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="5 3"/>' % (" ".join(chain), FIELD))

    p.append(text(W / 2, H - 24, "клітинки зшиті в один ланцюг — стан ніжки читається без дотику",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "boundary-scan.svg"), W, H, *p,
           title="Межовий скан: «цвяхи» переїхали всередину кремнію")


# ── tap-scan-chain: 4 дроти, кілька чипів у спільному ланцюгу ──────────────────
# Ідея: назовні лише TCK/TMS/TDI/TDO; усередині дані біжать по біту ланцюгом
# клітинок; чипи зшиваються послідовно (TDO→TDI) і живуть на тих самих 4 дротах.

def fig_tap_scan_chain():
    W, H = 780, 360
    p = []
    # три чипи в ряд
    cw, ch, gap = 150, 130, 60
    y = 120
    x0 = 70
    chips = []
    for i in range(3):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y, cw, ch, fill="#eef4ff", stroke=NEG, sw=1.8, rx=8))
        p.append(text(x + cw / 2, y + 24, "чип %d" % (i + 1), size=12, color=NEG, bold=True))
        # TAP-блок усередині
        p.append(fitbox(x + cw / 2 - 34, y + 40, 68, 28, "TAP", size=12, fill="#fff3e0", stroke=POS, sw=1.4, bold=True, color=POS))
        # клітинки ланцюга навколо ядра (схематично — 3 квадратики)
        for j in range(3):
            bx = x + 22 + j * 38
            p.append(rect(bx, y + ch - 26, 20, 14, fill=FILL, stroke=MUTED, sw=1.1, rx=2))
        chips.append((x, x + cw))

    # спільні TCK/TMS — паралельно всім (зверху)
    busy = y - 56
    p.append(line(x0 - 30, busy, chips[-1][1] + 20, busy, color=INK, sw=1.8))
    p.append(line(x0 - 30, busy + 16, chips[-1][1] + 20, busy + 16, color=INK, sw=1.8))
    p.append(text(x0 - 34, busy - 4, "TCK", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 34, busy + 20, "TMS", size=11, color=INK, anchor="end", bold=True))
    for (xa, xb) in chips:
        mid = (xa + xb) / 2
        p.append(line(mid, busy, mid, y, color=MUTED, sw=1.2, dash="3 3"))
        p.append(line(mid + 20, busy + 16, mid + 20, y, color=MUTED, sw=1.2, dash="3 3"))

    # TDI → ланцюг → TDO: послідовно крізь чипи (знизу)
    chainy = y + ch + 40
    p.append(text(x0 - 34, chainy + 4, "TDI", size=11, color=FIELD, anchor="end", bold=True))
    prev = x0 - 30
    for k, (xa, xb) in enumerate(chips):
        p.append(arrow(prev, chainy, xa, chainy, color=FIELD, sw=2))
        # лінія всередину чипа й назад (схематично)
        p.append(line(xa, chainy, xa, y + ch, color=FIELD, sw=1.4, dash="3 3"))
        p.append(line(xb, y + ch, xb, chainy, color=FIELD, sw=1.4, dash="3 3"))
        if k < len(chips) - 1:
            p.append(text((xb + chips[k + 1][0]) / 2, chainy - 8, "TDO→TDI", size=9, color=FIELD))
        prev = xb
    p.append(arrow(chips[-1][1], chainy, chips[-1][1] + 30, chainy, color=FIELD, sw=2))
    p.append(text(chips[-1][1] + 34, chainy + 4, "TDO", size=11, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, H - 18, "скільки б ніжок не мав чип — назовні завжди ті самі чотири дроти",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "tap-scan-chain.svg"), W, H, *p,
           title="Порт TAP і скан-ланцюг: чотири дроти на будь-яку кількість чипів")


if __name__ == "__main__":
    fig_print_vs_halt()
    fig_print_vs_debugger()
    fig_boundary_scan()
    fig_tap_scan_chain()
    print("OK: figures written to", OUT)
