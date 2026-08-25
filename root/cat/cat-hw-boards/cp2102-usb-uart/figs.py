# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: що всередині — блок-схема адаптера ─────────────────────────────
def fig_block():
    W, H = 760, 380
    f = []

    # рамка-плата
    f.append(rect(24, 54, W - 48, H - 90, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(W / 2, 44, "Плата адаптера CP2102", size=15, bold=True))

    # роз'єм Micro-USB (ліворуч)
    f.append(fitbox(48, 150, 96, 74, "Micro-USB\nроз'єм", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(text(96, 244, "до ПК", size=12, color=MUTED))

    # мікросхема CP2102
    cx0 = 300
    f.append(rect(cx0 - 84, 120, 168, 140, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx0, 146, "CP2102", size=16, bold=True))
    f.append(text(cx0, 168, "USB 2.0 FS", size=11, color=MUTED))
    f.append(text(cx0, 186, "трансивер", size=11, color=MUTED))
    f.append(text(cx0, 210, "LDO 3.3 В", size=11, color=MUTED))
    f.append(text(cx0, 228, "осцилятор", size=11, color=MUTED))
    f.append(text(cx0, 246, "EEPROM 1 КБ", size=11, color=MUTED))

    # USB D+/D- пара від роз'єму до чипа
    f.append(line(144, 176, cx0 - 84, 176, color=NEG, sw=2))
    f.append(line(144, 200, cx0 - 84, 200, color=NEG, sw=2))
    f.append(text((144 + cx0 - 84) / 2, 168, "D+ / D−", size=11, color=NEG))

    # гребінка виводів (праворуч)
    gx = 560
    pins = [
        ("5V", POS, "з USB, ~500 мА"),
        ("3V3", POS, "з LDO, ≤100 мА"),
        ("TXD", INK, "вихід → RX"),
        ("RXD", INK, "вхід ← TX"),
        ("GND", INK, "спільна земля"),
    ]
    row_h = 42
    top = 96
    for i, (name, col, note) in enumerate(pins):
        y = top + i * row_h
        f.append(circle(gx, y, 9, fill="#ffffff", stroke=col, sw=2))
        f.append(text(gx + 22, y + 5, name, size=13, bold=True, color=col, anchor="start"))
        f.append(text(gx + 78, y + 5, note, size=11, color=MUTED, anchor="start"))
        # лінія від чипа до виводу
        f.append(line(cx0 + 84, y, gx - 9, y, color="#9aa2ac", sw=1.4))

    # підпис лінії живлення TTL-рівня
    f.append(text(cx0 + 84 + 40, top - 18, "TTL-serial (рівень 3.3 В)", size=12, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, 'block.svg'), W, H, *f)


# ── Фігура 2: розводка пін-у-пін — прошивка голої STM32 через UART-bootloader ─
def fig_wiring():
    W, H = 780, 430
    f = []

    # ліва плата — адаптер
    ax, aw = 60, 150
    f.append(rect(ax, 70, aw, 300, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(text(ax + aw / 2, 58, "CP2102", size=15, bold=True))
    f.append(text(ax + aw / 2, 92, "USB → ПК", size=11, color=MUTED))

    # права плата — STM32
    bx, bw = 570, 150
    f.append(rect(bx, 70, bw, 300, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(bx + bw / 2, 58, "плата на STM32", size=15, bold=True))

    # виводи адаптера (праворуч від лівої плати)
    a_pins = {
        "3V3": 130,
        "GND": 180,
        "TXD": 250,
        "RXD": 310,
    }
    for name, y in a_pins.items():
        f.append(circle(ax + aw, y, 8, fill="#ffffff", stroke=INK, sw=1.8))
        f.append(text(ax + aw - 14, y + 5, name, size=13, bold=True, anchor="end"))

    # виводи STM32 (ліворуч від правої плати)
    b_pins = {
        "3V3": 130,
        "GND": 180,
        "RX": 250,   # PA10 / USART RX
        "TX": 310,   # PA9  / USART TX
        "BOOT0": 372,
    }
    b_note = {
        "RX": "PA10",
        "TX": "PA9",
        "BOOT0": "→ 3V3 = bootloader",
    }
    for name, y in b_pins.items():
        f.append(circle(bx, y, 8, fill="#ffffff", stroke=INK, sw=1.8))
        f.append(text(bx + 14, y + 5, name, size=13, bold=True, anchor="start"))
        if name in b_note:
            f.append(text(bx + 60, y + 5, b_note[name], size=11, color=MUTED, anchor="start"))

    # з'єднання
    x1 = ax + aw + 8
    x2 = bx - 8
    # 3V3 -- 3V3 (пряме, живлення від адаптера, малий струм)
    f.append(line(x1, 130, x2, 130, color=POS, sw=2))
    f.append(text((x1 + x2) / 2, 122, "живлення 3.3 В (мало струму!)", size=11, color=POS))
    # GND -- GND
    f.append(line(x1, 180, x2, 180, color=INK, sw=2))
    f.append(text((x1 + x2) / 2, 172, "спільна земля", size=11, color=MUTED))

    # ПЕРЕХРЕСТЯ TX/RX — через проміжні точки, щоб лінії не лягали одна на одну
    midx = (x1 + x2) / 2
    # TXD адаптера (y=250) -> RX STM32 (y=250) горизонтально прямо
    f.append(line(x1, 250, x2, 250, color=FIELD, sw=2.2))
    # RXD адаптера (y=310) -> TX STM32 (y=310)
    f.append(line(x1, 310, x2, 310, color=FIELD, sw=2.2))
    f.append(text(midx, 242, "TXD → RX", size=12, color=FIELD, bold=True))
    f.append(text(midx, 302, "RXD ← TX", size=12, color=FIELD, bold=True))
    f.append(text(midx, 340, "(перехрестя даних)", size=11, color=MUTED))

    # напис-нагадування знизу
    warn = ("BOOT0 на 3.3 В у мить скидання -> STM32 стартує у вбудований завантажувач "
            "і приймає прошивку по USART.")
    f.append(fitbox(60, 392, W - 120, 30, warn, size=12, fill="#fff8e1", stroke="#c9a227"))

    return render(os.path.join(OUT, 'wiring.svg'), W, H, *f)


# ── Фігура 3 (для вставки proj): часова стрічка прошивання через BOOT0 ────────
def fig_flash_timeline():
    W, H = 820, 470
    f = []

    f.append(text(W / 2, 34, "Часова стрічка одного прошивання STM32 по serial", size=15, bold=True))

    # дві доріжки-сигнали: BOOT0 і RESET
    lane_x0 = 190           # де починаються доріжки
    lane_x1 = W - 40
    hi_y = 96               # рівень «високо»
    lo_y = 132              # рівень «низько»
    boot_top = hi_y
    boot_bot = lo_y
    rst_hi = 176
    rst_lo = 212

    # підписи доріжок ліворуч (поза лініями)
    f.append(text(lane_x0 - 16, (hi_y + lo_y) / 2 + 4, "BOOT0", size=13, bold=True, anchor="end"))
    f.append(text(lane_x0 - 16, (rst_hi + rst_lo) / 2 + 4, "RESET", size=13, bold=True, anchor="end"))

    # осі рівнів (пунктир, світлі), не перетинають написи
    for yy in (hi_y, lo_y, rst_hi, rst_lo):
        f.append(line(lane_x0, yy, lane_x1, yy, color="#dfe3e8", sw=1))

    # чотири моменти часу (вертикальні орієнтири)
    t = [lane_x0 + 60, lane_x0 + 210, lane_x0 + 360, lane_x0 + 500]
    labels = ["t1", "t2", "t3", "t4"]
    for i, tx in enumerate(t):
        f.append(line(tx, 84, tx, 236, color="#c8ccd2", sw=1, dash="4,4"))
        f.append(text(tx, 78, labels[i], size=11, color=MUTED))

    # BOOT0: високо від t1 до t3, потім падає
    f.append(line(lane_x0, boot_bot, t[0], boot_bot, color=POS, sw=2.4))
    f.append(line(t[0], boot_bot, t[0], boot_top, color=POS, sw=2.4))
    f.append(line(t[0], boot_top, t[2], boot_top, color=POS, sw=2.4))
    f.append(line(t[2], boot_top, t[2], boot_bot, color=POS, sw=2.4))
    f.append(line(t[2], boot_bot, lane_x1, boot_bot, color=POS, sw=2.4))

    # RESET: короткий провал у t2 (скидання) і ще один у t3 (фінальний рестарт)
    f.append(line(lane_x0, rst_hi, t[1] - 12, rst_hi, color=NEG, sw=2.4))
    f.append(line(t[1] - 12, rst_hi, t[1] - 12, rst_lo, color=NEG, sw=2.4))
    f.append(line(t[1] - 12, rst_lo, t[1] + 12, rst_lo, color=NEG, sw=2.4))
    f.append(line(t[1] + 12, rst_lo, t[1] + 12, rst_hi, color=NEG, sw=2.4))
    f.append(line(t[1] + 12, rst_hi, t[2] - 12, rst_hi, color=NEG, sw=2.4))
    f.append(line(t[2] - 12, rst_hi, t[2] - 12, rst_lo, color=NEG, sw=2.4))
    f.append(line(t[2] - 12, rst_lo, t[2] + 12, rst_lo, color=NEG, sw=2.4))
    f.append(line(t[2] + 12, rst_lo, t[2] + 12, rst_hi, color=NEG, sw=2.4))
    f.append(line(t[2] + 12, rst_hi, lane_x1, rst_hi, color=NEG, sw=2.4))

    # позначка «читається рівень BOOT0» на скиданнях
    f.append(text(t[1], rst_lo + 22, "рівень BOOT0", size=10, color=MUTED))
    f.append(text(t[1], rst_lo + 36, "читається тут", size=10, color=MUTED))
    f.append(text(t[2], rst_lo + 22, "і тут", size=10, color=MUTED))

    # чотири картки-кроки внизу — з широким запасом, щоб текст не накладався
    card_y = 268
    card_h = 150
    gap = 14
    n = 4
    card_w = (W - 80 - gap * (n - 1)) / n
    steps = [
        ("1. BOOT0 → 3V3", "притиснути ніжку\nвибору до високого\n(перемичка / дріт)"),
        ("2. Скинути плату", "кнопкою RESET або\nзняти-подати живлення;\nчип бачить BOOT0=1\nі йде в завантажувач"),
        ("3. Залити прошивку", "на ПК: stm32flash\n-w firmware.bin\nпорт і швидкість;\nчип пише флеш"),
        ("4. BOOT0 → GND,\n    скинути ще раз", "повернути вибір\nдо низького й\nрестарт — тепер\nстартує ВАШ код"),
    ]
    fills = ["#fdecea", "#eaf0fd", "#eef7f0", "#fff8e1"]
    strokes = [POS, NEG, FIELD, "#c9a227"]
    for i, (head, body) in enumerate(steps):
        x = 40 + i * (card_w + gap)
        f.append(rect(x, card_y, card_w, card_h, fill=fills[i], stroke=strokes[i], sw=1.8))
        f.append(mtext(x + card_w / 2, card_y + 24, head, size=12, bold=True, color=strokes[i], lh=1.25))
        # тіло — нижче заголовка, з відступом, щоб не налізло
        head_lines = head.count("\n") + 1
        f.append(mtext(x + card_w / 2, card_y + 24 + head_lines * 17 + 8, body, size=11, color="#333333", lh=1.3))

    # прив'язка карток до моментів часу (тонкі напрямні, повз написи)
    anchor = [t[0], t[1], (t[1] + t[2]) / 2 + 20, t[2]]
    for i in range(n):
        x = 40 + i * (card_w + gap) + card_w / 2
        f.append(line(x, card_y - 4, x, 244, color="#c8ccd2", sw=1, dash="3,4"))

    f.append(text(W / 2, H - 16,
                  "Ключ: BOOT0 має бути високим САМЕ в мить скидання (t2), а не після нього.",
                  size=12, color=MUTED))
    return render(os.path.join(OUT, 'flash-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    p1 = fig_block()
    p2 = fig_wiring()
    p3 = fig_flash_timeline()
    print("wrote:", p1)
    print("wrote:", p2)
    print("wrote:", p3)
