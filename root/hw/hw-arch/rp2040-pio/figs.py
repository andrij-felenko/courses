# -*- coding: utf-8 -*-
"""Фігури до теми «RP2040 і PIO».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
ACCENT = "#8e44ad"   # PIO-автомат (фіолетовий — третій шлях)
GOLD   = "#b9770e"   # такти/час


# ── 1. Три способи смикати ніжку: біт-бенгінг / блок / PIO ────────────────────
def fig_three_ways():
    W, H = 760, 360
    f = [text(W / 2, 28, "Три способи керувати виводом", size=16, bold=True)]

    colx = [40, 290, 540]
    cw = 200
    titles = ["біт-бенгінг", "апаратний блок", "PIO"]
    cols = [INK, NEG, ACCENT]
    # ядро / автомат
    core = [
        ("ядро смикає\nніжку саме",   "ядро ЗАЙНЯТЕ\nна 100%",       "джитер від\nпереривань"),
        ("готовий блок\n(SPI/I²C)",   "ядро ВІЛЬНЕ,\nтаймінг точний", "функцію\nне змінити"),
        ("міні-автомат\nсмикає сам",  "ядро ВІЛЬНЕ,\nтаймінг точний", "функцію\nпишеш сам"),
    ]
    verdict = ["гнучко, та\nядро в'язне", "точно, та\nнегнучко", "гнучко І\nядро вільне"]
    for i, x in enumerate(colx):
        f.append(rect(x, 56, cw, 270, fill=BG, stroke=cols[i], sw=2))
        f.append(text(x + cw / 2, 80, titles[i], size=14, bold=True, color=cols[i]))
        f.append(fitbox(x + 14, 96, cw - 28, 46, core[i][0], size=12, fill=FILL, stroke=cols[i]))
        f.append(fitbox(x + 14, 150, cw - 28, 46, core[i][1], size=12, fill=FILL, stroke=MUTED))
        f.append(fitbox(x + 14, 204, cw - 28, 46, core[i][2], size=12, fill="#fdf3e7", stroke=GOLD))
        f.append(fitbox(x + 14, 262, cw - 28, 50, verdict[i], size=12.5,
                        fill=("#eef7f0" if i == 2 else FILL),
                        stroke=(FIELD if i == 2 else MUTED), bold=(i == 2)))
    return render(os.path.join(IMG, "three-ways.svg"), W, H, *f)


# ── 2. PIO як «DMA для протоколів»: ядро вільне, автомати смикають ────────────
def fig_pio_vs_bitbang():
    W, H = 760, 380
    f = [text(W / 2, 28, "PIO — як DMA, тільки для протоколів", size=16, bold=True)]

    # ядро
    f.append(rect(40, 70, 150, 100, fill=FILL, stroke=INK, sw=2))
    f.append(text(115, 110, "ядро", size=14, bold=True))
    f.append(text(115, 132, "Cortex-M0+", size=11, color=MUTED))
    f.append(text(115, 152, "×2", size=11, color=MUTED))

    # FIFO
    f.append(rect(250, 92, 110, 56, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(305, 116, "FIFO", size=13, bold=True, color=FIELD))
    f.append(text(305, 136, "4 слова", size=10.5, color=MUTED))
    f.append(arrow(190, 120, 248, 120, color=INK))
    f.append(text(219, 110, "байти", size=10, color=MUTED, italic=True))

    # PIO-автомат
    f.append(rect(420, 70, 150, 100, fill="#f4eefa", stroke=ACCENT, sw=2.2))
    f.append(text(495, 104, "PIO-автомат", size=13, bold=True, color=ACCENT))
    f.append(text(495, 126, "крихітна", size=10.5, color=MUTED))
    f.append(text(495, 142, "програма", size=10.5, color=MUTED))
    f.append(arrow(360, 120, 418, 120, color=ACCENT))

    # ніжка / сигнал
    f.append(arrow(570, 120, 628, 120, color=ACCENT))
    f.append(text(599, 110, "пін", size=10, color=MUTED, italic=True))
    # сигнал-меандр з точним таймінгом
    sx, sy = 636, 120
    pts = [(sx, sy), (sx, sy - 22), (sx + 20, sy - 22), (sx + 20, sy),
           (sx + 40, sy), (sx + 40, sy - 22), (sx + 60, sy - 22), (sx + 60, sy),
           (sx + 80, sy), (sx + 80, sy - 22), (sx + 95, sy - 22)]
    d = "M " + " L ".join("%.0f %.0f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, ACCENT))
    f.append(text(683, 152, "точний такт", size=10, color=ACCENT, italic=True))

    # підпис «ядро вільне»
    f.append(rect(40, 220, 530, 56, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(305, 244, "Ядро лише кладе байти у FIFO і йде у свої справи.", size=13, bold=True, color=FIELD))
    f.append(text(305, 264, "Автомат жене протокол сам — навантаження ядра ≈ 0%.", size=12, color=INK))

    # рядок порівняння з біт-бенгінгом
    f.append(text(305, 312, "Біт-бенгінг натомість тримав би ядро в петлі весь час передачі.",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(IMG, "pio-vs-bitbang.svg"), W, H, *f)


# ── 3. Бюджет тактів: біт-бенгінг росте, PIO лишається біля нуля ──────────────
def fig_cpu_budget():
    W, H = 760, 420
    f = [text(W / 2, 28, "Частка ядра на WS2812: біт-бенгінг проти PIO", size=15.5, bold=True)]

    # осі
    ox, oy = 90, 350
    aw, ah = 600, 280
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))         # X
    f.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))         # Y
    f.append(text(ox + aw / 2, 398, "кількість пікселів", size=12, color=MUTED))
    f.append(text(28, oy - ah / 2, "% ядра", size=12, color=MUTED))

    # точки (N, %) для біт-бенгінгу при 30 к/с, ~10 тактів/біт @125 МГц
    data = [(1, 0.06), (30, 1.7), (144, 8.3), (300, 17.0)]
    maxN, maxP = 320.0, 20.0
    def px(n): return ox + (n / maxN) * aw
    def py(p): return oy - (p / maxP) * ah

    # сітка %
    for p in (5, 10, 15, 20):
        yy = py(p)
        f.append(line(ox, yy, ox + aw, yy, color="#e5e7eb", sw=1))
        f.append(text(ox - 10, yy + 4, "%d" % p, size=10, color=MUTED, anchor="end"))

    # крива біт-бенгінгу
    dd = "M " + " L ".join("%.1f %.1f" % (px(n), py(p)) for n, p in data)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dd, POS))
    for n, p in data:
        f.append(circle(px(n), py(p), 4, fill=POS, stroke=POS))
        f.append(text(px(n), py(p) - 12, "%g%%" % p, size=10.5, color=POS, bold=True))
        f.append(text(px(n), oy + 16, "%d" % n, size=10, color=MUTED))
    f.append(text(px(300) - 6, py(17) - 28, "біт-бенгінг", size=12.5, color=POS, bold=True, anchor="end"))

    # лінія PIO ≈ 0
    f.append(line(ox, py(0.2), ox + aw, py(0.2), color=ACCENT, sw=2.6))
    f.append(text(ox + aw - 6, py(0.2) - 8, "PIO ≈ 0% при будь-якому N", size=12.5,
                  color=ACCENT, bold=True, anchor="end"))
    return render(os.path.join(IMG, "cpu-budget.svg"), W, H, *f)


# ── 4. Анатомія одного PIO-автомата ──────────────────────────────────────────
def fig_state_machine():
    W, H = 780, 400
    f = [text(W / 2, 28, "Анатомія одного PIO-автомата", size=16, bold=True)]

    # ядро/DMA зліва
    f.append(rect(30, 160, 110, 80, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(85, 196, "ядро", size=12.5, bold=True))
    f.append(text(85, 216, "або DMA", size=10.5, color=MUTED))

    # TX FIFO -> OSR -> пін
    f.append(rect(170, 80, 110, 50, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(225, 100, "TX FIFO", size=12, bold=True, color=FIELD))
    f.append(text(225, 118, "4 слова", size=10, color=MUTED))
    f.append(rect(320, 80, 120, 50, fill="#f4eefa", stroke=ACCENT, sw=1.8))
    f.append(text(380, 100, "OSR", size=12, bold=True, color=ACCENT))
    f.append(text(380, 118, "зсув назовні", size=10, color=MUTED))

    # RX FIFO <- ISR <- пін
    f.append(rect(170, 270, 110, 50, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(225, 290, "RX FIFO", size=12, bold=True, color=FIELD))
    f.append(text(225, 308, "4 слова", size=10, color=MUTED))
    f.append(rect(320, 270, 120, 50, fill="#f4eefa", stroke=ACCENT, sw=1.8))
    f.append(text(380, 290, "ISR", size=12, bold=True, color=ACCENT))
    f.append(text(380, 308, "зсув усередину", size=10, color=MUTED))

    # програма + дільник у центрі
    f.append(rect(490, 150, 150, 100, fill="#f4eefa", stroke=ACCENT, sw=2.2))
    f.append(text(565, 178, "програма", size=12.5, bold=True, color=ACCENT))
    f.append(text(565, 197, "9 інструкцій", size=10.5, color=MUTED))
    f.append(text(565, 214, "1 такт кожна", size=10.5, color=MUTED))
    f.append(rect(505, 222, 120, 22, fill="#fdf3e7", stroke=GOLD, sw=1.5))
    f.append(text(565, 237, "дільник такту", size=10, color=GOLD, bold=True))

    # піни справа
    f.append(rect(680, 160, 70, 80, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(715, 196, "GPIO", size=12, bold=True))
    f.append(text(715, 216, "вивід", size=10, color=MUTED))

    # стрілки потоку
    f.append(arrow(140, 190, 168, 130, color=FIELD))     # ядро -> TX
    f.append(arrow(168, 290, 142, 215, color=FIELD))     # RX -> ядро
    f.append(arrow(280, 105, 318, 105, color=ACCENT))    # TX -> OSR
    f.append(arrow(318, 295, 282, 295, color=ACCENT))    # ISR -> RX
    f.append(arrow(440, 105, 700, 165, color=ACCENT))    # OSR -> пін
    f.append(arrow(700, 235, 440, 295, color=ACCENT))    # пін -> ISR

    f.append(text(W / 2, 372, "Дані течуть FIFO ⇄ зсувні регістри ⇄ виводи; темп задає власний дільник такту.",
                  size=11.5, color=MUTED))
    return render(os.path.join(IMG, "state-machine.svg"), W, H, *f)


# ── 5. WS2812: один біт = вікно тактів, фронти від side-set ───────────────────
def fig_ws2812_timing():
    W, H = 760, 360
    f = [text(W / 2, 28, "Один біт WS2812 = вікно тактів автомата", size=15.5, bold=True)]

    baseY = 150
    hi = 60
    # «1»: довгий HIGH
    x0 = 70
    f.append(text(x0, baseY - hi - 14, "біт «1»", size=12.5, bold=True, color=ACCENT))
    seg1 = [(x0, baseY), (x0, baseY - hi), (x0 + 150, baseY - hi), (x0 + 150, baseY), (x0 + 220, baseY)]
    d1 = "M " + " L ".join("%.0f %.0f" % p for p in seg1)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d1, ACCENT))
    f.append(line(x0, baseY + 24, x0 + 150, baseY + 24, color=GOLD, sw=1.4))
    f.append(text(x0 + 75, baseY + 40, "T1H ≈ 800 нс", size=11, color=GOLD, anchor="middle"))

    # «0»: короткий HIGH
    x1 = 430
    f.append(text(x1, baseY - hi - 14, "біт «0»", size=12.5, bold=True, color=NEG))
    seg0 = [(x1, baseY), (x1, baseY - hi), (x1 + 75, baseY - hi), (x1 + 75, baseY), (x1 + 220, baseY)]
    d0 = "M " + " L ".join("%.0f %.0f" % p for p in seg0)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d0, NEG))
    f.append(line(x1, baseY + 24, x1 + 75, baseY + 24, color=GOLD, sw=1.4))
    f.append(text(x1 + 37, baseY + 40, "T0H ≈ 400 нс", size=11, color=GOLD, anchor="middle"))

    # повне вікно біта
    f.append(line(70, baseY + 70, 290, baseY + 70, color=MUTED, sw=1.2, dash="4 3"))
    f.append(text(180, baseY + 86, "1 біт = 25 тактів ≈ 1.25 мкс", size=11, color=MUTED, anchor="middle"))
    f.append(line(430, baseY + 70, 650, baseY + 70, color=MUTED, sw=1.2, dash="4 3"))
    f.append(text(540, baseY + 86, "1 біт = 25 тактів ≈ 1.25 мкс", size=11, color=MUTED, anchor="middle"))

    # пояснення
    f.append(rect(70, 280, 620, 52, fill="#f4eefa", stroke=ACCENT, sw=1.6))
    f.append(text(380, 302, "Довжину HIGH задає не пауза в коді, а кількість тактів (інструкція + затримка [n]).",
                  size=12, color=INK, anchor="middle"))
    f.append(text(380, 322, "Тривалість «1» і «0» різниться тільки тим, де автомат опускає ніжку через side-set.",
                  size=11.5, color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, "ws2812-timing.svg"), W, H, *f)


# ── 6. Коли брати RP2040/PIO, а коли ні ──────────────────────────────────────
def fig_when_pio():
    W, H = 760, 330
    f = [text(W / 2, 28, "Коли PIO — правильний вибір", size=16, bold=True)]

    # ліворуч: за PIO
    f.append(rect(40, 60, 330, 240, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(205, 86, "брати PIO", size=14, bold=True, color=FIELD))
    yes = ["нестандартний цифровий протокол",
           "жорсткий субмікросекундний таймінг",
           "кілька каналів того самого протоколу",
           "блока в доступних чіпах немає",
           "ядро треба лишити вільним"]
    for i, s in enumerate(yes):
        yy = 116 + i * 34
        f.append(plus(64, yy - 4, r=7))
        f.append(text(82, yy, s, size=11.5, anchor="start"))

    # праворуч: не PIO
    f.append(rect(400, 60, 320, 240, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(560, 86, "не варто PIO", size=14, bold=True, color=POS))
    no = ["стандартний SPI/I²C/UART вистачає",
          "потрібна складна логіка чи математика",
          "протокол має жити на різних МК",
          "потрібні точки зупину для відладки",
          "автоматів треба більше ніж вісім"]
    for i, s in enumerate(no):
        yy = 116 + i * 34
        f.append(minus(424, yy - 4, r=7))
        f.append(text(442, yy, s, size=11.5, anchor="start"))
    return render(os.path.join(IMG, "when-pio.svg"), W, H, *f)


# ── 7. (hist) Від освітньої місії до власного кремнію ─────────────────────────
def fig_foundation_to_chip():
    W, H = 760, 360
    f = [text(W / 2, 28, "Від освітньої мети — до власного чипа", size=16, bold=True)]

    steps = [
        ("освітня\nблагодійність", "навчити дітей\nкодувати", FIELD),
        ("дешева плата\nдля шкіл", "Raspberry Pi\n(2012)", INK),
        ("власний чип\nза $1", "масовість +\nдоступність", GOLD),
        ("PIO: гнучкий\nI/O задешево", "відсутній блок\nпишеш сам", ACCENT),
    ]
    x = 30
    bw = 165
    gap = 18
    for i, (top, bot, col) in enumerate(steps):
        f.append(rect(x, 110, bw, 110, fill=BG, stroke=col, sw=2))
        f.append(fitbox(x + 12, 124, bw - 24, 44, top, size=13, fill=FILL, stroke=col, bold=True))
        f.append(fitbox(x + 12, 174, bw - 24, 38, bot, size=11, fill=BG, stroke=MUTED, color=MUTED))
        if i < 3:
            f.append(arrow(x + bw, 165, x + bw + gap, 165, color=INK))
        x += bw + gap
    f.append(text(W / 2, 280, "Кожен щабель випливає з мети навчати, а не з гонитви за мегагерцами.",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "foundation-to-chip.svg"), W, H, *f)


# ── 8. (hist) Що в RP2040 чуже, а що своє ────────────────────────────────────
def fig_borrowed_vs_built():
    W, H = 760, 330
    f = [text(W / 2, 28, "RP2040: що ліцензоване, а що своє", size=16, bold=True)]

    f.append(rect(40, 60, 330, 240, fill=FILL, stroke=NEG, sw=2))
    f.append(text(205, 86, "ліцензоване в Arm", size=14, bold=True, color=NEG))
    borrowed = ["ядро Cortex-M0+ (×2)", "архітектура ARMv6-M", "система команд ядра", "готовий Cortex-M RTL"]
    for i, s in enumerate(borrowed):
        yy = 122 + i * 40
        f.append(circle(66, yy - 4, 6, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(84, yy, s, size=12, anchor="start"))

    f.append(rect(400, 60, 320, 240, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(560, 86, "внесок Raspberry Pi", size=14, bold=True, color=FIELD))
    built = ["компонування SoC і шини", "264 КБ SRAM банками", "відсутній флеш (QSPI зовні)", "PIO — програмований I/O"]
    for i, s in enumerate(built):
        yy = 122 + i * 40
        col = ACCENT if i == 3 else FIELD
        f.append(circle(424, yy - 4, 6, fill="#eef7f0", stroke=col, sw=1.8))
        f.append(text(442, yy, s, size=12, anchor="start", bold=(i == 3),
                      color=(ACCENT if i == 3 else INK)))
    return render(os.path.join(IMG, "borrowed-vs-built.svg"), W, H, *f)


# ── 9. (hist) Маховик: чип служить освітній місії ────────────────────────────
def fig_mission_loop():
    W, H = 620, 440
    f = [text(W / 2, 28, "Маховик: чип служить місії", size=16, bold=True)]

    cx, cy, r = 310, 245, 150
    nodes = [
        ("освітня мета\nфундації", FIELD),
        ("дешевий\nвідкритий чип", ACCENT),
        ("багато виробників\nплат", INK),
        ("ширша спільнота\n+ прибуток", GOLD),
    ]
    import math
    pts = []
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i, ((px_, py_), (lbl, col)) in enumerate(zip(pts, nodes)):
        bx, bw, bh = px_, 168, 56
        f.append(fitbox(bx - bw / 2, py_ - bh / 2, bw, bh, lbl, size=12.5,
                        fill=BG, stroke=col, bold=True, color=col))
    # стрілки по колу
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 4]
        # вкоротити до країв
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        f.append(arrow(x1 + ux * 92, y1 + uy * 40, x2 - ux * 92, y2 - uy * 40, color=MUTED))
    f.append(text(cx, cy + 4, "→", size=22, color=MUTED))
    f.append(text(W / 2, 420, "Продати чип конкурентам — для благодійності раціонально: ширше навчання.",
                  size=11.5, color=MUTED))
    return render(os.path.join(IMG, "mission-loop.svg"), W, H, *f)


# ── 10. (comp) Анатомія плати Pico-класу ─────────────────────────────────────
def fig_anatomy():
    W, H = 760, 380
    f = [text(W / 2, 28, "Анатомія плати Pico-класу", size=16, bold=True)]

    # плата
    f.append(rect(60, 70, 640, 230, fill="#fafbfc", stroke=MUTED, sw=2, rx=14))

    # RP2040 у центрі
    f.append(rect(330, 150, 130, 90, fill="#f4eefa", stroke=ACCENT, sw=2.2))
    f.append(text(395, 184, "RP2040", size=14, bold=True, color=ACCENT))
    f.append(text(395, 204, "Cortex-M0+", size=10.5, color=MUTED))
    f.append(text(395, 220, "×2", size=10.5, color=MUTED))

    # QSPI-Flash поруч
    f.append(rect(500, 165, 120, 60, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(560, 188, "QSPI-Flash", size=12, bold=True, color=FIELD))
    f.append(text(560, 207, "~2 МБ, окремо", size=10, color=MUTED))
    f.append(arrow(500, 195, 462, 195, color=FIELD))

    # USB
    f.append(rect(90, 165, 90, 60, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(135, 188, "USB", size=12, bold=True))
    f.append(text(135, 207, "напряму", size=10, color=MUTED))
    f.append(arrow(180, 195, 328, 195, color=INK))
    f.append(text(254, 184, "без USB-UART", size=10, color=MUTED, italic=True))

    # SMPS
    f.append(rect(330, 256, 130, 34, fill="#fdf3e7", stroke=GOLD, sw=1.8))
    f.append(text(395, 278, "buck-boost → 3.3 В", size=11, bold=True, color=GOLD))

    # BOOTSEL
    f.append(rect(90, 256, 130, 34, fill=FILL, stroke=POS, sw=1.8))
    f.append(text(155, 278, "кнопка BOOTSEL", size=11, bold=True, color=POS))

    # гребінки GPIO
    for gx in range(80, 690, 36):
        f.append(rect(gx, 78, 14, 12, fill="#d4af37", stroke=MUTED, sw=0.8, rx=2))
    f.append(text(W / 2, 116, "гребінка GPIO — рівні 3.3 В", size=11, color=MUTED))
    f.append(text(W / 2, 340, "USB іде прямо до чипа; флеш — окремою мікросхемою по QSPI; живлення стабілізує buck-boost.",
                  size=11.5, color=MUTED))
    return render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 11. (comp) Прошивка перетягуванням UF2 ───────────────────────────────────
def fig_uf2_flow():
    W, H = 760, 320
    f = [text(W / 2, 28, "Прошивка перетягуванням (UF2)", size=16, bold=True)]

    steps = [
        ("утримуєш\nBOOTSEL", "+ підключаєш USB", POS),
        ("з'являється диск\nRPI-RP2", "як звичайна флешка", FIELD),
        ("перетягуєш\nfirmware.uf2", "drag-and-drop", ACCENT),
        ("bootrom пише\nу QSPI-Flash", "плата стартує сама", INK),
    ]
    x = 30
    bw = 165
    gap = 18
    for i, (top, bot, col) in enumerate(steps):
        f.append(rect(x, 110, bw, 110, fill=BG, stroke=col, sw=2))
        f.append(text(x + bw / 2, 132, str(i + 1), size=13, bold=True, color=col))
        f.append(fitbox(x + 12, 142, bw - 24, 42, top, size=12.5, fill=FILL, stroke=col, bold=True))
        f.append(fitbox(x + 12, 190, bw - 24, 22, bot, size=10.5, fill=BG, stroke=MUTED, color=MUTED))
        if i < 3:
            f.append(arrow(x + bw, 165, x + bw + gap, 165, color=INK))
        x += bw + gap
    f.append(text(W / 2, 280, "Нуль інструментів і нуль драйверів — контраст із esptool + міст + DTR/RTS у ESP32.",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "uf2-flow.svg"), W, H, *f)


if __name__ == "__main__":
    # базова стаття
    fig_three_ways()
    fig_pio_vs_bitbang()
    fig_cpu_budget()
    fig_state_machine()
    fig_ws2812_timing()
    fig_when_pio()
    # вставка 📜 hist-rp2040
    fig_foundation_to_chip()
    fig_borrowed_vs_built()
    fig_mission_loop()
    # вставка 🔌 comp-pico-board
    fig_anatomy()
    fig_uf2_flow()
    print("OK: figs written to", IMG)
