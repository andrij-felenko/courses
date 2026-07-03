# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «PWM-адаптер для Pixhawk».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що робить адаптер: 10-пін JST-GH → ряд 3-пін серво-гребінок ──────────────
def fig_what_it_does():
    W, H = 940, 470
    f = [text(W / 2, 30, "Що робить адаптер: один тісний роз'єм → ряд стандартних серво-гребінок",
              size=15, bold=True)]

    # ── ліворуч: плата з роз'ємом FMU/IO PWM OUT ──
    bx, by, bw, bh = 40, 120, 150, 200
    f.append(rect(bx, by, bw, bh, fill="#eef2f8", stroke=INK, sw=2.0, rx=10))
    f.append(text(bx + bw / 2, by + 28, "Pixhawk 6C", size=12.5, bold=True))
    f.append(text(bx + bw / 2, by + 48, "FMU / IO", size=10, color=MUTED))
    f.append(text(bx + bw / 2, by + 63, "PWM OUT", size=10, color=MUTED))
    # роз'єм-гніздо (10 контактів у ряд)
    cy = by + bh - 40
    for i in range(10):
        px = bx + 16 + i * ((bw - 32) / 9)
        f.append(circle(px, cy, 2.6, fill=INK, stroke=INK))
    f.append(text(bx + bw / 2, by + bh - 14, "10-пін JST-GH", size=9, italic=True, color=MUTED))

    # ── кабель (стрічка) ──
    cablx0 = bx + bw
    cablx1 = 330
    f.append(line(cablx0, cy, cablx1, 240, color=POS, sw=2.4))
    for k in range(1, 10):
        yy = cy + (240 - cy) * k / 10
        xx = cablx0 + (cablx1 - cablx0) * k / 10
        f.append(line(xx, yy - 6, xx, yy + 6, color=MUTED, sw=1.0))
    f.append(text((cablx0 + cablx1) / 2, 130, "плаский кабель", size=9.5, italic=True, color=MUTED))
    f.append(text((cablx0 + cablx1) / 2, 144, "10 жил", size=9.5, italic=True, color=MUTED))

    # ── адаптер (сама плата) ──
    ax, ay, aw, ah = 330, 100, 250, 300
    f.append(rect(ax, ay, aw, ah, fill="#fff8e6", stroke="#b8860b", sw=2.0, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "PWM-адаптер", size=13, bold=True, color="#8a6d00"))
    f.append(text(ax + aw / 2, ay + 44, "(breakout board)", size=9.5, italic=True, color=MUTED))
    # ряд 3-пін гребінок
    n = 8
    row_y = ay + 78
    for i in range(n):
        gy = row_y + i * ((ah - 100) / (n - 1))
        # три штирі
        for j, (col, lab) in enumerate([(MUTED, "S"), (POS, "+"), (NEG, "−")]):
            gx = ax + 150 + j * 26
            f.append(circle(gx, gy, 4.2, fill=col, stroke=col))
        f.append(text(ax + 40, gy + 4, "канал %d" % (i + 1), size=9.5, color=INK, anchor="start"))
    # шапка над штирями
    f.append(text(ax + 150, row_y - 14, "S", size=10, bold=True, color=MUTED))
    f.append(text(ax + 176, row_y - 14, "+", size=11, bold=True, color=POS))
    f.append(text(ax + 202, row_y - 14, "−", size=11, bold=True, color=NEG))

    # ── праворуч: споживачі ──
    ex = ax + aw + 70
    # ESC / мотор
    f.append(rect(ex, 130, 200, 80, fill=BG, stroke=POS, sw=1.6, rx=8))
    f.append(text(ex + 100, 158, "ESC → мотор", size=11.5, bold=True))
    f.append(text(ex + 100, 178, "читає лише сигнал", size=9.5, color=MUTED))
    f.append(text(ex + 100, 194, "(живиться від батареї)", size=9, italic=True, color=MUTED))
    f.append(arrow(ax + 228, 170, ex, 170, color=POS, sw=2.0))
    # серво
    f.append(rect(ex, 260, 200, 88, fill=BG, stroke=NEG, sw=1.6, rx=8))
    f.append(text(ex + 100, 288, "серворульова машинка", size=10.5, bold=True))
    f.append(text(ex + 100, 308, "тягне струм із «+» рейки", size=9.5, color=MUTED))
    f.append(text(ex + 100, 324, "→ рейку треба живити", size=9, italic=True, color=POS))
    f.append(arrow(ax + 228, 300, ex, 300, color=NEG, sw=2.0))

    b, _, _ = textbox(W / 2, H - 34,
                      "плата нічого не «розумнішає»: вона лише розводить тісний 10-контактний роз'єм у ряд звичних 3-контактних\n"
                      "серво-гребінок (сигнал · плюс · мінус), у які прямо втикаються роз'єми регуляторів моторів і сервомашинок",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "what-it-does.svg"), W, H, *f)


# ── 2. Розпіновка: як 10 жил кабелю лягають на гребінки (спільний «+» і «−») ─────
def fig_pinout():
    W, H = 940, 560
    f = [text(W / 2, 30, "Розпіновка адаптера: 8 сигналів окремі, «+» і «−» — спільні шини",
              size=15, bold=True)]

    # ── зліва: 10-пін роз'єм кабелю (вертикально) ──
    lx = 90
    y0 = 90
    step = 40
    pins = [
        ("1", "VDD_Servo", POS, "спільний «+» (рейка серв)"),
        ("2", "CH1", INK, "сигнал каналу 1"),
        ("3", "CH2", INK, "сигнал каналу 2"),
        ("4", "CH3", INK, "сигнал каналу 3"),
        ("5", "CH4", INK, "сигнал каналу 4"),
        ("6", "CH5", INK, "сигнал каналу 5"),
        ("7", "CH6", INK, "сигнал каналу 6"),
        ("8", "CH7", INK, "сигнал каналу 7"),
        ("9", "CH8", INK, "сигнал каналу 8"),
        ("10", "GND", NEG, "спільний «−» (земля)"),
    ]
    f.append(text(lx, y0 - 24, "роз'єм кабелю", size=10.5, bold=True, color=MUTED))
    f.append(text(lx, y0 - 10, "(10-пін JST-GH)", size=9, italic=True, color=MUTED))
    for i, (num, name, col, desc) in enumerate(pins):
        py = y0 + i * step
        f.append(circle(lx, py, 8, fill=BG, stroke=col, sw=2.0))
        f.append(text(lx, py + 4, num, size=9.5, bold=True, color=col))
        f.append(text(lx + 20, py + 4, name, size=10.5, bold=True, color=col, anchor="start"))
        f.append(text(lx + 118, py + 4, desc, size=9, color=MUTED, anchor="start"))

    # ── праворуч: 8 гребінок S/+/− ──
    gx = 560
    gtop = 96
    gstep = 50
    f.append(text(gx + 40, gtop - 26, "8 серво-гребінок (S · + · −)", size=10.5, bold=True, color=MUTED))
    sig_pins = pins[1:9]  # CH1..CH8
    # спільні шини «+» та «−» — вертикальні лінії праворуч від штирів
    plus_col_x = gx + 44
    minus_col_x = gx + 74
    ytop = gtop
    ybot = gtop + 7 * gstep
    f.append(line(plus_col_x, ytop - 10, plus_col_x, ybot + 10, color=POS, sw=2.6))
    f.append(line(minus_col_x, ytop - 10, minus_col_x, ybot + 10, color=NEG, sw=2.6))
    f.append(text(plus_col_x, ytop - 16, "+", size=12, bold=True, color=POS))
    f.append(text(minus_col_x, ytop - 16, "−", size=12, bold=True, color=NEG))
    f.append(text(gx + 14, gtop - 16, "S", size=11, bold=True, color=MUTED))
    for i in range(8):
        gy = gtop + i * gstep
        # штир сигналу
        f.append(circle(gx + 14, gy, 4.6, fill=MUTED, stroke=MUTED))
        f.append(circle(plus_col_x, gy, 4.6, fill=POS, stroke=POS))
        f.append(circle(minus_col_x, gy, 4.6, fill=NEG, stroke=NEG))
        f.append(text(gx + 96, gy + 4, "канал %d" % (i + 1), size=9.5, color=INK, anchor="start"))

    # ── лінії від сигнальних пінів кабелю до штирів S (окремі) ──
    for i in range(8):
        src_y = y0 + (i + 1) * step
        dst_y = gtop + i * gstep
        f.append(line(lx + 190, src_y, gx + 14, dst_y, color=MUTED, sw=1.2))
    # VDD_Servo → шина «+»
    f.append(line(lx + 190, y0, plus_col_x, gtop - 10, color=POS, sw=2.2))
    # GND → шина «−»
    f.append(line(lx + 190, y0 + 9 * step, minus_col_x, ybot + 10, color=NEG, sw=2.2))

    b, _, _ = textbox(W / 2, H - 32,
                      "у роз'ємі кабелю «+» і «−» приходять РАЗ (пін 1 і пін 10) — на адаптері вони розтікаються шинами до всіх\n"
                      "гребінок; окремий у кожного лише сигнал. Тому живити рейку досить в ОДНОМУ місці — шина спільна",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "pinout.svg"), W, H, *f)


# ── 3. Головна пастка: коли «+» рейку треба живити, а коли ні ────────────────────
def fig_power_rail():
    W, H = 940, 470
    f = [text(W / 2, 30, "Пастка живлення «+» рейки: коптеру не треба, літаку/роверу — обов'язково",
              size=14.5, bold=True)]

    # ── ліва колонка: КОПТЕР (не треба) ──
    lx, lw = 50, 400
    top = 66
    f.append(rect(lx, top, lw, 320, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=12))
    f.append(text(lx + lw / 2, top + 28, "Мультикоптер: рейку живити НЕ треба", size=12.5, bold=True, color=FIELD))
    f.append(text(lx + lw / 2, top + 52, "навантаження — лише ESC моторів", size=10, italic=True, color=MUTED))
    # адаптер
    f.append(rect(lx + 40, top + 80, 120, 180, fill="#fff8e6", stroke="#b8860b", sw=1.8, rx=8))
    f.append(text(lx + 100, top + 104, "адаптер", size=10.5, bold=True, color="#8a6d00"))
    for j, (col, lab) in enumerate([(MUTED, "S"), (POS, "+"), (NEG, "−")]):
        f.append(text(lx + 70 + j * 26, top + 128, lab, size=10, bold=True, color=col))
    # ESC
    f.append(rect(lx + 230, top + 96, 140, 66, fill=BG, stroke=POS, sw=1.6, rx=8))
    f.append(text(lx + 300, top + 122, "ESC", size=11.5, bold=True))
    f.append(text(lx + 300, top + 140, "живиться від", size=9, color=MUTED))
    f.append(text(lx + 300, top + 154, "батареї сам", size=9, color=MUTED))
    # рівна лінія на висоті штирів адаптера, кінці впираються в бокси (не наскрізь)
    f.append(line(lx + 160, top + 128, lx + 230, top + 128, color=MUTED, sw=1.6))
    f.append(text(lx + 195, top + 118, "сигнал + земля", size=8.5, italic=True, color=MUTED))
    # «+» висить у повітрі
    f.append(text(lx + lw / 2, top + 292, "«+» рейка може лишатися ненапоєною —", size=10, color=INK))
    f.append(text(lx + lw / 2, top + 310, "ESC бере струм з батареї, не з рейки", size=10, color=INK))

    # ── права колонка: ЛІТАК/РОВЕР (треба) ──
    rx, rw = 490, 400
    f.append(rect(rx, top, rw, 320, fill="#fdecea", stroke=POS, sw=2.0, rx=12))
    f.append(text(rx + rw / 2, top + 28, "Літак / ровер: рейку живити ТРЕБА", size=12.5, bold=True, color=POS))
    f.append(text(rx + rw / 2, top + 52, "серва тягнуть струм саме з «+» рейки", size=10, italic=True, color=MUTED))
    # адаптер
    f.append(rect(rx + 40, top + 80, 120, 180, fill="#fff8e6", stroke="#b8860b", sw=1.8, rx=8))
    f.append(text(rx + 100, top + 104, "адаптер", size=10.5, bold=True, color="#8a6d00"))
    for j, (col, lab) in enumerate([(MUTED, "S"), (POS, "+"), (NEG, "−")]):
        f.append(text(rx + 70 + j * 26, top + 128, lab, size=10, bold=True, color=col))
    # серво (праворуч угорі)
    f.append(rect(rx + 230, top + 84, 140, 58, fill=BG, stroke=NEG, sw=1.6, rx=8))
    f.append(text(rx + 300, top + 110, "серво", size=11, bold=True))
    f.append(text(rx + 300, top + 128, "їсть з рейки", size=9, color=MUTED))
    f.append(line(rx + 160, top + 113, rx + 230, top + 113, color=NEG, sw=1.6))
    # BEC живить рейку (праворуч нижче)
    f.append(rect(rx + 230, top + 176, 140, 66, fill=BG, stroke=POS, sw=2.0, rx=8))
    f.append(text(rx + 300, top + 202, "BEC / ESC-BEC", size=11, bold=True, color=POS))
    f.append(text(rx + 300, top + 220, "5 В на «+» і «−»", size=9.5, color=INK))
    f.append(text(rx + 300, top + 234, "(або 2S)", size=9, italic=True, color=MUTED))
    # стрілка BEC → адаптер: рівна лінія на висоті нижче штирів, кінець упирається в бокс адаптера
    f.append(arrow(rx + 230, top + 209, rx + 160, top + 209, color=POS, sw=2.2))
    f.append(text(rx + rw / 2, top + 292, "без окремого BEC серва не ворухнуться:", size=10, color=INK))
    f.append(text(rx + rw / 2, top + 310, "автопілот сигнал дає, а СИЛУ на «+» — ні", size=10, color=POS))

    b, _, _ = textbox(W / 2, H - 34,
                      "золоте правило: автопілот кладе на «+» рейку лише слабку логічну напругу — керувати нею серва НЕ можна.\n"
                      "Коптеру байдуже (ESC силові самі), а от серва літака/ровера мовчатимуть, поки «+» рейку не напоїть BEC.",
                      size=10, fill="#fdf0e6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "power-rail.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки proj-pwm-config (налаштування й керування виходами)
# ══════════════════════════════════════════════════════════════════════════════

# ── 4. Прив'язка каналів: PX4 (MAIN/AUX → IO/FMU) та ArduPilot (SERVOn) ──────────
def fig_channel_map():
    W, H = 960, 560
    f = [text(W / 2, 30, "Дві мови про той самий вихід: PX4 (MAIN/AUX) і ArduPilot (SERVOn)",
              size=15, bold=True)]

    # ── ЛІВА панель: PX4 ──
    lx, lw = 40, 430
    top = 66
    f.append(rect(lx, top, lw, 420, fill="#eef2f8", stroke=INK, sw=1.8, rx=12))
    f.append(text(lx + lw / 2, top + 26, "PX4: іменем роз'єму", size=13.5, bold=True))
    f.append(text(lx + lw / 2, top + 46, "MAIN = плата I/O · AUX = плата FMU", size=10, italic=True, color=MUTED))

    # два стовпчики прив'язки
    def px4_col(cx, title, rows, col):
        f.append(text(cx, top + 82, title, size=11.5, bold=True, color=col))
        for i, (a, b) in enumerate(rows):
            ry = top + 112 + i * 34
            f.append(text(cx - 70, ry, a, size=10.5, bold=True, color=INK, anchor="start"))
            f.append(text(cx - 4, ry, "→", size=11, color=MUTED))
            f.append(text(cx + 14, ry, b, size=10, color=MUTED, anchor="start"))

    px4_col(lx + 118, "MAIN → I/O", [("MAIN1", "IO_CH1"), ("MAIN2", "IO_CH2"),
                                     ("MAIN3", "IO_CH3"), ("…", "…")], NEG)
    px4_col(lx + 300, "AUX → FMU", [("AUX1", "FMU_CH1"), ("AUX2", "FMU_CH2"),
                                    ("AUX3", "FMU_CH3"), ("…", "…")], POS)
    f.append(line(lx + 215, top + 96, lx + 215, top + 232, color=MUTED, sw=1.0, dash="4 4"))

    f.append(text(lx + lw / 2, top + 268, "функцію на вихід кладе PWM_MAIN_FUNCn /", size=9.5, color=INK))
    f.append(text(lx + lw / 2, top + 284, "PWM_AUX_FUNCn (напр. FUNC3 = Motor 2)", size=9.5, color=INK))
    b1, _, _ = textbox(lx + lw / 2, top + 344,
                       "AUX (FMU) — з меншою затримкою: мотори\n"
                       "радять вішати саме на нього, а не на MAIN",
                       size=9.5, fill="#fdf0e6", stroke=POS)
    f.append(b1)

    # ── ПРАВА панель: ArduPilot ──
    rx, rw = 490, 430
    f.append(rect(rx, top, rw, 420, fill="#f3f8f3", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(rx + rw / 2, top + 26, "ArduPilot: наскрізним номером", size=13.5, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, top + 46, "виходи 1…N, кожен — свій набір SERVOn_*", size=10, italic=True, color=MUTED))

    params = [
        ("SERVOn_FUNCTION", "що це за вихід (мотор, елерон, вимк.)"),
        ("SERVOn_MIN", "нижня межа ширини, мкс (напр. 1000)"),
        ("SERVOn_MAX", "верхня межа ширини, мкс (напр. 2000)"),
        ("SERVOn_TRIM", "нейтраль / центр, мкс (напр. 1500)"),
        ("SERVOn_REVERSED", "0/1 — перевернути напрям ходу"),
    ]
    for i, (p, d) in enumerate(params):
        ry = top + 96 + i * 40
        f.append(rect(rx + 24, ry - 18, rw - 48, 32, fill=BG, stroke=MUTED, sw=1.0, rx=6))
        f.append(text(rx + 40, ry + 2, p, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(rx + 200, ry + 2, d, size=9, color=MUTED, anchor="start"))

    b2, _, _ = textbox(rx + rw / 2, top + 356,
                       "вхід (RCn_*) і вихід (SERVOn_*) — РІЗНІ:\n"
                       "межі, реверс і трим окремі для того й того",
                       size=9.5, fill="#eef6ef", stroke=FIELD)
    f.append(b2)

    b, _, _ = textbox(W / 2, H - 34,
                      "фізична гребінка адаптера — одна; змінюється лише, як прошивка її НАЗИВАЄ й де кладе межі ширини.\n"
                      "Плутанина I/O↔FMU у PX4 = поїхали номери каналів; у ArduPilot вихід і межі задає свій SERVOn_*.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "channel-map.svg"), W, H, *f)


# ── 5. Безпечні межі ширини PWM: числова вісь 1000…2000 мкс ──────────────────────
def fig_pwm_limits():
    W, H = 940, 430
    f = [text(W / 2, 30, "Безпечні межі ширини імпульсу: 1000 · 1500 · 2000 мкс",
              size=15, bold=True)]

    # вісь
    ax0, ax1 = 130, 810
    ay = 150
    us0, us1 = 1000, 2000
    f.append(line(ax0 - 20, ay, ax1 + 20, ay, color=INK, sw=2.0))

    def xof(us):
        return ax0 + (ax1 - ax0) * (us - us0) / (us1 - us0)

    # головні позначки
    ticks = [(1000, "1000", "MIN\nповний реверс / нуль газу", NEG),
             (1500, "1500", "TRIM\nнейтраль серва", MUTED),
             (2000, "2000", "MAX\nповний хід / повний газ", POS)]
    for us, lab, sub, col in ticks:
        x = xof(us)
        f.append(line(x, ay - 12, x, ay + 12, color=col, sw=2.4))
        f.append(text(x, ay - 22, lab + " мкс", size=11.5, bold=True, color=col))
        # підпис під віссю, кожен своїм рядком, добре рознесені
        lines = sub.split("\n")
        for k, ln in enumerate(lines):
            f.append(text(x, ay + 40 + k * 16, ln, size=9.5,
                          color=(INK if k == 0 else MUTED)))

    # проміжні тонкі позначки кожні 100 мкс
    for us in range(1100, 2000, 100):
        if us == 1500:
            continue
        x = xof(us)
        f.append(line(x, ay - 6, x, ay + 6, color=MUTED, sw=1.0))

    # смуга «робочий діапазон»
    f.append(rect(xof(1000), ay - 3, xof(2000) - xof(1000), 6, fill="#dfe6ef", stroke="none", sw=0))

    # рамка-пастка: реверс — це НЕ від'ємна ширина
    b1, _, _ = textbox(300, ay + 120,
                       "реверс серва НЕ від'ємна ширина: 1000 і 2000 —\n"
                       "ті самі краї, лише міняються місцями (SERVOn_REVERSED)",
                       size=9.5, fill="#eef0fd", stroke=NEG)
    f.append(b1)
    # рамка-пастка: вихід за 1000..2000
    b2, _, _ = textbox(650, ay + 120,
                       "ширше за 1000…2000 — на свій ризик: серво впреться\n"
                       "в упор і гріється, ESC може не зловити калібрування",
                       size=9.5, fill="#fdf0e6", stroke=POS)
    f.append(b2)

    b, _, _ = textbox(W / 2, H - 32,
                      "1 мс = «мало», 2 мс = «багато», 1.5 мс = «посередині» — цей діапазон розуміють майже всі серва й ESC.\n"
                      "MIN/MAX/TRIM лишай у цих межах; калібрування ESC саме «показує» йому, де 1000, а де 2000.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "pwm-limits.svg"), W, H, *f)


# ── 6. Штатне змішування VS примусове керування (bench-only) ─────────────────────
def fig_force_vs_mix():
    W, H = 960, 500
    f = [text(W / 2, 30, "Два шляхи до гребінки: штатне змішування VS примусовий обхід",
              size=15, bold=True)]

    # ── ВЕРХНЯ доріжка: штатний шлях ──
    ty = 96
    f.append(text(60, ty - 18, "Штатно (у польоті):", size=12, bold=True, color=FIELD, anchor="start"))
    boxes = [("команда\nпілота / місії", "#eef6ef", FIELD),
             ("контролер\n+ ЗМІШУВАЧ", "#eef6ef", FIELD),
             ("ширина на\nкожен вихід", "#eef6ef", FIELD),
             ("гребінка\nадаптера", "#fff8e6", "#b8860b")]
    bx = 60
    bw, bh = 170, 62
    gap = 46
    centers = []
    for i, (lab, fill, col) in enumerate(boxes):
        x = bx + i * (bw + gap)
        f.append(rect(x, ty, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(mtext(x + bw / 2, ty + 26, lab, size=10.5, bold=True, color=col))
        centers.append(x + bw)
        if i < len(boxes) - 1:
            f.append(arrow(x + bw + 6, ty + bh / 2, x + bw + gap - 6, ty + bh / 2, color=MUTED, sw=2.0))
    f.append(text(bx + 2 * (bw + gap) + bw / 2, ty + bh + 22,
                  "змішувач враховує режим, тримінг, failsafe — виходи узгоджені", size=9, italic=True, color=MUTED))

    # ── НИЖНЯ доріжка: примусовий обхід ──
    by = 260
    f.append(text(60, by - 18, "Примусово (MAV_CMD_DO_SET_SERVO / DO_MOTOR_TEST):",
                  size=12, bold=True, color=POS, anchor="start"))
    f.append(rect(60, by, bw, bh, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(mtext(60 + bw / 2, by + 26, "твоя програма\n(MAVLink-команда)", size=10.5, bold=True, color=POS))
    # стрілка ОБХОДУ прямо на вихід, повз змішувач
    f.append(rect(60 + 2 * (bw + gap), by, bw, bh, fill="#fff8e6", stroke="#b8860b", sw=1.8, rx=8))
    f.append(mtext(60 + 2 * (bw + gap) + bw / 2, by + 26, "ширина прямо\nна цей вихід", size=10.5, bold=True, color="#b8860b"))
    f.append(rect(60 + 3 * (bw + gap), by, bw, bh, fill="#fff8e6", stroke="#b8860b", sw=1.8, rx=8))
    f.append(mtext(60 + 3 * (bw + gap) + bw / 2, by + 26, "гребінка\nадаптера", size=10.5, bold=True, color="#b8860b"))
    # довга стрілка обходу (проходить розривом, де НЕМА боксу-змішувача)
    gap_cx = 60 + bw + gap + bw / 2
    f.append(arrow(60 + bw + 6, by + bh / 2, 60 + 2 * (bw + gap) - 6, by + bh / 2, color=POS, sw=2.2))
    f.append(arrow(60 + 2 * (bw + gap) + bw + 6, by + bh / 2, 60 + 3 * (bw + gap) - 6, by + bh / 2, color="#b8860b", sw=2.0))
    # «повз змішувач» — підпис у розриві: один рядок над стрілкою, один під нею (текст поза лінією обходу)
    f.append(text(gap_cx, by + bh / 2 - 14, "змішувача тут НЕМА", size=10, bold=True, color=POS))
    f.append(text(gap_cx, by + bh / 2 + 24, "обхід прямо на вихід", size=9.5, italic=True, color=POS))

    b, _, _ = textbox(W / 2, H - 40,
                      "примусова команда кладе ширину ПРЯМО на вихід, минаючи змішувач: годиться для перевірки одного керма чи мотора\n"
                      "на столі, небезпечна в польоті (жодного узгодження). У ArduPilot вона ще й спрацює лише на вихід із\n"
                      "SERVOn_FUNCTION = 0 / RCPassThru — зайнятий льотною функцією вихід команду відхилить.",
                      size=9.5, fill="#fdf0e6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "force-vs-mix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_what_it_does()
    fig_pinout()
    fig_power_rail()
    fig_channel_map()
    fig_pwm_limits()
    fig_force_vs_mix()
    print("OK: 6 figures ->", IMG)
