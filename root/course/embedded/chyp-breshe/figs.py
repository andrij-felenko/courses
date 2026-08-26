# -*- coding: utf-8 -*-
"""Фігури до теми «Чип бреше: правдоподібні хибні дані».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Перевернутий порядок байтів (MSB/LSB swap) ───────────────────────────
def fig_endianness_sawtooth():
    W, H = 780, 420
    f = [text(W / 2, 26, "Перевернутий порядок байтів: як спотворюється сигнал", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "плавне нагрівання давача (24 °C → 25.5 °C) при помилці MSB/LSB перетворюється на пилку",
                  size=11, color=MUTED, italic=True))

    PW = 340
    # ── Ліва панель: Коректне читання (Big-Endian зібрано правильно) ──
    lx = 30
    f.append(rect(lx, 70, PW, 250, fill=BG, stroke="#dddddd", sw=1.2))
    f.append(text(lx + PW / 2, 92, "Коректне збирання: (hi << 8) | lo", size=12, color=FIELD, bold=True))
    f.append(text(lx + PW / 2, 108, "MSB=0x01, LSB зростає: 0x80 → 0x98 (384 → 408)", size=9.5, color=MUTED))

    # Осі лівого графіка
    oxL, oyL = lx + 45, 270
    gwL, ghL = 270, 130
    f.append(line(oxL, oyL, oxL + gwL, oyL, color=INK, sw=1.4))
    f.append(line(oxL, oyL, oxL, oyL - ghL, color=INK, sw=1.4))
    f.append(text(oxL + gwL, oyL + 16, "час (t)", size=9, color=MUTED, anchor="end", italic=True))
    f.append(text(oxL - 8, oyL - ghL + 10, "°C", size=9.5, color=MUTED, anchor="end", bold=True))

    # Плавна лінія 24.0 -> 25.5 °C
    ptsL = []
    for i in range(25):
        px = oxL + (i / 24.0) * (gwL - 20)
        py = oyL - 20 - (i / 24.0) * 80
        ptsL.append("%.1f %.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsL), FIELD))
    f.append(text(oxL - 6, oyL - 20, "24.0", size=9, color=MUTED, anchor="end"))
    f.append(text(oxL - 6, oyL - 100, "25.5", size=9, color=MUTED, anchor="end"))
    f.append(text(lx + PW / 2, 304, "Плавний монотоний відгук давача", size=10, color=FIELD, bold=True))

    # ── Права панель: Помилка MSB/LSB swap ──
    rx = 410
    f.append(rect(rx, 70, PW, 250, fill=BG, stroke="#dddddd", sw=1.2))
    f.append(text(rx + PW / 2, 92, "Помилка swap: (lo << 8) | hi", size=12, color=POS, bold=True))
    f.append(text(rx + PW / 2, 108, "молодший байт потрапляє на місце старшого", size=9.5, color=MUTED))

    # Осі правого графіка
    oxR, oyR = rx + 45, 270
    gwR, ghR = 270, 130
    f.append(line(oxR, oyR, oxR + gwR, oyR, color=INK, sw=1.4))
    f.append(line(oxR, oyR, oxR, oyR - ghR, color=INK, sw=1.4))
    f.append(text(oxR + gwR, oyR + 16, "час (t)", size=9, color=MUTED, anchor="end", italic=True))
    f.append(text(oxR - 8, oyR - ghR + 10, "значення", size=9.5, color=MUTED, anchor="end", bold=True))

    # Пилкоподібні стрибки: кожен крок LSB на +1 збільшує число на 256!
    ptsR = []
    # 5 сходинок пилки
    for step in range(5):
        x_start = oxR + step * 48
        for j in range(10):
            px = x_start + j * 4.5
            val = (step * 256 + j * 25) % 250
            py = oyL - 15 - (val / 250.0) * 95
            ptsR.append("%.1f %.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(ptsR), POS))
    f.append(text(rx + PW / 2, 304, "Дикі стрибки на 256 відліків на кожен крок LSB", size=10, color=POS, bold=True))

    f.append(fitbox(30, 336, W - 60, 68,
                    ["Коли старший і молодший байти переплутані місцями, кожна зміна молодшого біта фізичної величини",
                     "примножується у 256 разів (зсув на 8 позицій). Сигнал не зникає і не стає нулем — він перетворюється",
                     "на характерну «пилку», де прилад нібито реагує на вплив, але показує хаотичні гігантські стрибки."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "endianness-sawtooth.svg"), W, H, *f)


# ── 2. Пастка знакового розширення (Sign Extension) ─────────────────────────
def fig_sign_extension_trap():
    W, H = 780, 400
    f = [text(W / 2, 26, "Пастка знакового розширення: 12-бітний додатковий код у 16-бітному слові", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "від'ємне число −1 (0xFFF у 12 бітах) без розмноження знакового біта стає +4095",
                  size=11, color=MUTED, italic=True))

    def draw_bit_row(x0, y0, bits, colors, label, sublabel):
        cell_w = 28
        cell_h = 24
        f.append(text(x0 - 12, y0 + 16, label, size=10.5, color=INK, anchor="end", bold=True))
        for i in range(16):
            bx = x0 + i * cell_w
            bit_val = bits[i]
            col = colors[i]
            bg_col = "#fdecea" if col == POS else ("#eafaf1" if col == FIELD else BG)
            f.append(rect(bx, y0, cell_w, cell_h, fill=bg_col, stroke=col, sw=1.2, rx=2))
            f.append(text(bx + cell_w / 2, y0 + 16, str(bit_val), size=11, color=col, bold=True))
            # Номери бітів над першим рядком
            if y0 == 90:
                f.append(text(bx + cell_w / 2, y0 - 6, str(15 - i), size=9, color=MUTED))
        f.append(text(x0 + 16 * cell_w + 12, y0 + 16, sublabel, size=10, color=INK, anchor="start"))

    # 1) Сирий 12-бітний вихід АЦП для значення -1: b11=1 (знаковий біт), b10..b0=1 (0xFFF)
    # У 16-бітному просторі старші 4 біти заповнені нулями: 0000 1111 1111 1111
    bits_raw = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    cols_raw = [MUTED]*4 + [POS] + [INK]*11
    draw_bit_row(140, 90, bits_raw, cols_raw, "Сирий пакет 12 біт:", "0x0FFF (знаковий біт b11=1)")

    # 2) Наївне збереження у uint16/int16 без розширення (zero extension)
    bits_zero = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    cols_zero = [POS]*4 + [POS] + [INK]*11
    draw_bit_row(140, 160, bits_zero, cols_zero, "Наївне читання uint16:", "= +4095 (замість −1!)")
    f.append(text(140 + 2 * 28, 148, "старші 4 біти лишилися 0 → втрачено від'ємний знак", size=9, color=POS, italic=True))

    # 3) Коректне знакове розширення (Sign Extension)
    bits_sign = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    cols_sign = [FIELD]*4 + [FIELD] + [INK]*11
    draw_bit_row(140, 230, bits_sign, cols_sign, "Знакове розширення:", "= 0xFFFF = −1 (коректно)")
    f.append(text(140 + 2 * 28, 218, "знаковий біт (b11=1) скопійовано у біти 15..12", size=9, color=FIELD, italic=True))

    f.append(fitbox(30, 290, W - 60, 90,
                    ["У додатковому коді (Two's Complement) знак числа визначається його найстаршим бітом.",
                     "Якщо давач 12-бітний, його знаковий біт — це біт 11. Перенесення числа у 16-бітний `int16_t` процесора",
                     "вимагає розмноження (копіювання) біта 11 на позиції 12, 13, 14 та 15. Якщо цього не зробити,",
                     "будь-яке навіть крихітне від'ємне число (−0.1 °C або −0.05 g) перетворюється на колосальне додатне."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "sign-extension-trap.svg"), W, H, *f)


# ── 3. Розрив когерентності при читанні (Torn Read / Rollover) ───────────────
def fig_torn_read_rollover():
    W, H = 780, 420
    f = [text(W / 2, 26, "Розрив когерентності: читання байтів під час переповнення", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "значення 0x00FF змінюється на 0x0100 між читанням старшого та молодшого байтів",
                  size=11, color=MUTED, italic=True))

    timeline_y = 110
    t1, t2, t3 = 240, 420, 600
    f.append(line(70, timeline_y, 710, timeline_y, color=INK, sw=2))
    f.append(text(715, timeline_y + 4, "t", size=11, color=INK, italic=True, anchor="start"))

    # Подія 1: t1 - MCU читає MSB
    f.append(circle(t1, timeline_y, 6, fill=FIELD, stroke=FIELD, sw=1))
    f.append(line(t1, timeline_y, t1, timeline_y - 30, color=FIELD, sw=1.5))
    f.append(rect(t1 - 65, timeline_y - 62, 130, 30, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(t1, timeline_y - 47, "1. Читання MSB = 0x00", size=9.5, color=FIELD, bold=True))
    f.append(text(t1, timeline_y + 22, "t₁: стан давача 0x00FF (255)", size=9, color=MUTED))

    # Подія 2: t2 - АЦП завершує вибірку і оновлює регістри!
    f.append(circle(t2, timeline_y, 6, fill=POS, stroke=POS, sw=1))
    f.append(line(t2, timeline_y, t2, timeline_y + 35, color=POS, sw=1.5))
    f.append(rect(t2 - 80, timeline_y + 35, 160, 34, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text(t2, timeline_y + 50, "2. АЦП оновив регістри:", size=9.5, color=POS, bold=True))
    f.append(text(t2, timeline_y + 63, "0x00FF  →  0x0100 (256)", size=9, color=POS))

    # Подія 3: t3 - MCU читає LSB
    f.append(circle(t3, timeline_y, 6, fill=FIELD, stroke=FIELD, sw=1))
    f.append(line(t3, timeline_y, t3, timeline_y - 30, color=FIELD, sw=1.5))
    f.append(rect(t3 - 65, timeline_y - 62, 130, 30, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(t3, timeline_y - 47, "3. Читання LSB = 0x00", size=9.5, color=FIELD, bold=True))
    f.append(text(t3, timeline_y + 22, "t₃: прочитано новий LSB", size=9, color=MUTED))

    # Підсумок катастрофи
    f.append(rect(140, 210, 500, 56, fill="#fff5f5", stroke=POS, sw=1.8, rx=6))
    f.append(text(390, 230, "Результат зшивання: (0x00 << 8) | 0x00 = 0x0000 (0 відліків замість 256!)",
                  size=11, color=POS, bold=True))
    f.append(text(390, 252, "Помилка розриву когерентності дає миттєвий хибний нульовий провал на графіку",
                  size=9.5, color=INK))

    f.append(fitbox(30, 290, W - 60, 110,
                    ["Як запобігти розриву когерентності:",
                     "1. Пакетне зчитування (Burst Read / Auto-Increment): вичитування обох регістрів за одну I2C/SPI транзакцію.",
                     "2. Тіньові регістри / Block Data Update (BDU): апаратне заморожування оновлення LSB до завершення читання MSB.",
                     "3. Синхронізація з Data Ready (DRDY): зчитування тільки в інтервалах, коли АЦП не проводить перезапис даних."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "torn-read-rollover.svg"), W, H, *f)


# ── 4. Зсув бітів через невідповідність SPI CPOL/CPHA ────────────────────────
def fig_spi_cpha_shift():
    W, H = 780, 420
    f = [text(W / 2, 26, "Невідповідність фази тактування SPI (CPHA): зсув потоку на 1 біт", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "вибірка на передньому фронті замість заднього призводить до втрати MSB і зсуву вліво",
                  size=11, color=MUTED, italic=True))

    x0 = 120
    bw = 64
    bits = [1, 0, 1, 1, 0, 0, 1, 0]  # 0xB2

    # Такт SCK (Mode 0: CPOL=0)
    ytk = 110
    tk_pts = ["M %.1f %.1f" % (x0 - 20, ytk)]
    for i in range(8):
        bx = x0 + i * bw
        tk_pts.append("L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f"
                      % (bx, ytk, bx, ytk - 28, bx + bw / 2, ytk - 28, bx + bw / 2, ytk))
        tk_pts.append("L %.1f %.1f" % (bx + bw, ytk))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(tk_pts), NEG))
    f.append(text(x0 - 30, ytk - 12, "SCK", size=11, color=NEG, anchor="end", bold=True))

    # Лінія даних MISO (передається байт 0xB2 = 10110010)
    yd = 175
    f.append(text(x0 - 30, yd - 10, "MISO", size=11, color=INK, anchor="end", bold=True))
    d_pts = ["M %.1f %.1f" % (x0 - 20, yd - bits[0] * 26)]
    for i, b in enumerate(bits):
        bx = x0 + i * bw
        y = yd - b * 26
        d_pts.append("L %.1f %.1f L %.1f %.1f" % (bx, y, bx + bw, y))
        f.append(text(bx + bw / 2, yd - 32, "D%d=%d" % (7 - i, b), size=9.5, color=INK, bold=True))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(d_pts), INK))

    # Семпли при правильному CPHA=0 (на висхідному фронті в центрі біта)
    for i in range(8):
        bx = x0 + i * bw
        f.append(line(bx + bw / 4, ytk - 28, bx + bw / 4, yd + 8, color=FIELD, sw=1.2, dash="3,2"))
        f.append(circle(bx + bw / 4, yd - bits[i] * 26, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(x0 + 8 * bw + 15, yd - 14, "Правильно (Mode 0): 0xB2", size=10, color=FIELD, anchor="start", bold=True))

    # Семпли при неправильному CPHA=1 (на фронті перемикання даних)
    for i in range(8):
        bx = x0 + i * bw
        f.append(line(bx, ytk, bx, yd + 24, color=POS, sw=1.4, dash="2,2"))
        f.append(circle(bx, yd + 24, 3, fill=POS, stroke=POS, sw=1))
    f.append(text(x0 + 8 * bw + 15, yd + 24, "Помилка (Mode 1): 0x64 (зсув << 1)", size=10, color=POS, anchor="start", bold=True))

    f.append(fitbox(30, 250, W - 60, 150,
                    ["Симптоми неузгодженості CPOL/CPHA в SPI:",
                     "• Зсув на 1 біт вліво (<< 1): старший біт D7 втрачається, усі значення подвоюються, а молодший біт читає шум.",
                     "• Зсув на 1 біт вправо (>> 1): затримка на півтакту змушує прочитати попередній стан шини як старший біт.",
                     "• Ідентифікатор WHO_AM_I замість очікуваного 0x68 читається як 0xD0 (0x68 << 1) або 0x34 (0x68 >> 1).",
                     "• Діагностика: перевірте в даташиті, за яким саме фронтом такту (Rising/Falling) давач защіпає та змінює дані."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "spi-cpha-shift.svg"), W, H, *f)


# ── 5. Дзвоніння та хибні тактові імпульси (Ringing & Glitches) ───────────────
def fig_ringing_false_clock():
    W, H = 780, 420
    f = [text(W / 2, 26, "Дзвоніння на лінії такту: генерація хибних імпульсів", size=15.5, bold=True)]
    f.append(text(W / 2, 46, "індуктивність довгих дротів створює коливання на крутому фронті, що перетинають поріг логіки",
                  size=11, color=MUTED, italic=True))

    # Осі графіка
    ox, oy = 80, 240
    gw, gh = 620, 170
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.6))
    f.append(text(ox + gw, oy + 16, "час (t)", size=9.5, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 10, oy - gh + 10, "Напруга (V)", size=9.5, color=MUTED, anchor="end", bold=True))

    y_vcc = oy - 140
    y_gnd = oy
    y_vih = oy - 140 * 0.7  # Поріг V_IH (0.7 Vcc)
    y_vil = oy - 140 * 0.3  # Поріг V_IL (0.3 Vcc)

    f.append(line(ox, y_vcc, ox + gw, y_vcc, color=MUTED, sw=0.8, dash="4,3"))
    f.append(text(ox - 6, y_vcc + 4, "3.3 В", size=9, color=MUTED, anchor="end"))
    f.append(line(ox, y_vih, ox + gw, y_vih, color=POS, sw=1, dash="3,3"))
    f.append(text(ox + gw + 6, y_vih + 4, "V_IH (поріг 1)", size=9.5, color=POS, anchor="start"))
    f.append(line(ox, y_vil, ox + gw, y_vil, color=NEG, sw=1, dash="3,3"))
    f.append(text(ox + gw + 6, y_vil + 4, "V_IL (поріг 0)", size=9.5, color=NEG, anchor="start"))

    import math
    # 1. Сигнал із дзвонінням (Undamped / Ringing)
    pts_ring = []
    t_step = 160
    for x in range(0, t_step):
        pts_ring.append("%.1f %.1f" % (ox + x, y_gnd))
    # Фронт з коливанням
    for x in range(0, 300):
        t = x / 20.0
        # Затухаюча синусоїда поверх сходинки
        v = 1.0 - math.exp(-t * 0.45) * math.cos(t * 3.2)
        py = y_gnd - v * 140
        pts_ring.append("%.1f %.1f" % (ox + t_step + x, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts_ring), POS))
    f.append(text(ox + 220, y_vcc - 16, "Дзвоніння (ringing) без демпфування", size=10.5, color=POS, bold=True))

    # Позначення хибних перетинів порогу
    crossings = [182, 202, 222]
    for cx in crossings:
        f.append(circle(ox + cx, y_vih, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(ox + 202, y_vih - 14, "3 перетини V_IH = 3 такти замість 1!", size=9, color=POS, bold=True))

    # 2. Узгоджений сигнал із резистором демпфування (Damped with Series Resistor 33-100 Ohm)
    pts_clean = []
    for x in range(0, t_step + 40):
        pts_clean.append("%.1f %.1f" % (ox + x, y_gnd))
    for x in range(0, 260):
        t = x / 35.0
        v = 1.0 - math.exp(-t)
        py = y_gnd - v * 140
        pts_clean.append("%.1f %.1f" % (ox + t_step + 40 + x, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' % (" ".join(pts_clean), FIELD))
    f.append(text(ox + 380, y_vcc + 28, "Чистий узгоджений фронт (з резистором 33–50 Ом)", size=9.5, color=FIELD, bold=True))

    f.append(fitbox(30, 260, W - 60, 140,
                    ["Чому дзвоніння спотворює пакети:",
                     "1. Кожен паразитний перетин порогу V_IH сприймається апаратним тригером як повноцінний такт SCK/SCL.",
                     "2. Приймач зсуває у свій регістр зайвий біт — весь подальший потік даних десинхронізується.",
                     "3. Засоби усунення: послідовний резистор (Series Termination 33–100 Ом) біля виводу передавача,",
                     "   зменшення швидкості наростання фронту (GPIO Slew Rate = Low/Medium) та скорочення довжини шлейфів."],
                    size=10.5, color=INK, fill=FILL, stroke="#e0e0e0", sw=1))
    render(os.path.join(IMG, "ringing-false-clock.svg"), W, H, *f)


if __name__ == "__main__":
    fig_endianness_sawtooth()
    fig_sign_extension_trap()
    fig_torn_read_rollover()
    fig_spi_cpha_shift()
    fig_ringing_false_clock()
    print("OK: 5 figures ->", IMG)
