# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «STM32F072B-DISCO (Discovery, Cortex-M0)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія плати: дві половини — програматор і цільовий чип з периферією ──
def fig_anatomy():
    W, H = 900, 620
    f = [text(W / 2, 30, "STM32F072B-DISCO — програматор і цільовий чип на одній платі",
              size=16, bold=True)]

    # Контур плати
    bx, by, bw, bh = 55, 55, W - 110, 500
    f.append(rect(bx, by, bw, bh, fill="#eaf3f4", stroke=FIELD, sw=2.2, rx=16))

    # Пунктирна межа: верхня третина — ST-LINK, решта — цільова частина
    split_y = by + 150
    f.append(line(bx + 12, split_y, bx + bw - 12, split_y, color=MUTED, sw=1.6, dash="7,6"))
    f.append(text(bx + 20, split_y - 10, "частина ST-LINK/V2 (програматор+дебагер)",
                  size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(text(bx + 20, split_y + 20, "цільова частина (твоя прошивка тут)",
                  size=10.5, color=FIELD, anchor="start", italic=True))

    # ── Mini-USB ST-LINK (ліворуч угорі, виступає) ──
    su_y = by + 70
    f.append(rect(bx - 26, su_y - 18, 40, 44, fill="#cfd6da", stroke=INK, sw=1.6, rx=4))
    f.append(text(bx - 6, su_y - 26, "Mini-USB", size=10, bold=True))
    f.append(text(bx - 6, su_y + 40, "ПК ↔ ST-LINK", size=9, color=MUTED))

    # ST-LINK чип
    b, sw_, sh_ = textbox(bx + 150, su_y + 2, "ST-LINK/V2\n(другий STM32)",
                          size=11.5, bold=True, fill="#eef1f5", stroke=INK, sw=1.8, pad=10)
    f.append(b)
    f.append(arrow(bx + 14, su_y + 2, bx + 150 - sw_ / 2, su_y + 2, color=INK, sw=2.0))

    # ── Цільовий чип STM32F072RBT6 — центр нижньої частини ──
    chx, chy = bx + bw * 0.44, by + bh * 0.60
    chw, chh = 200, 104
    f.append(rect(chx - chw / 2, chy - chh / 2, chw, chh, fill="#20242a", stroke=INK, sw=2, rx=8))
    f.append(text(chx, chy - 14, "STM32F072RBT6", size=14.5, bold=True, color="#ffffff"))
    f.append(text(chx, chy + 6, "Cortex-M0 · 48 МГц", size=10.5, color="#c9ccd1"))
    f.append(text(chx, chy + 24, "128 КБ Flash · 16 КБ SRAM · LQFP64", size=9.5, color="#c9ccd1"))
    # «ніжки» по всіх чотирьох боках (LQFP)
    for i in range(9):
        lx = chx - chw / 2 + 20 + i * (chw - 40) / 8
        f.append(line(lx, chy - chh / 2, lx, chy - chh / 2 - 7, color=INK, sw=1.2))
        f.append(line(lx, chy + chh / 2, lx, chy + chh / 2 + 7, color=INK, sw=1.2))
    for i in range(5):
        ly = chy - chh / 2 + 18 + i * (chh - 36) / 4
        f.append(line(chx - chw / 2, ly, chx - chw / 2 - 7, ly, color=INK, sw=1.2))
        f.append(line(chx + chw / 2, ly, chx + chw / 2 + 7, ly, color=INK, sw=1.2))

    # SWD від ST-LINK у цільовий чип (унутрішня дротівка, пунктир вертикально в коридорі ліворуч)
    swd_x = chx - chw / 2 - 40
    f.append(line(bx + 150, su_y + sh_ / 2, bx + 150, su_y + sh_ / 2 + 26, color=INK, sw=1.6))
    f.append(line(bx + 150, su_y + sh_ / 2 + 26, swd_x, su_y + sh_ / 2 + 26, color=INK, sw=1.6))
    f.append(arrow(swd_x, su_y + sh_ / 2 + 26, swd_x, chy - 14, color=INK, sw=1.6))
    f.append(arrow(swd_x, chy - 14, chx - chw / 2 - 7, chy - 14, color=INK, sw=1.6))
    f.append(mtext(swd_x - 8, chy - 56,
                   ["SWD — 2 дроти:", "SWCLK (PA14),", "SWDIO (PA13)"],
                   size=9.5, color=INK, anchor="end"))

    # ── Периферія навколо цільового чипа: gyro, touch, RF-EEPROM, USB, LED, кнопка ──
    def periph(cx, cy, s, fill, stroke, edge_x, edge_y):
        b, pw, ph = textbox(cx, cy, s, size=10.5, bold=True, fill=fill, stroke=stroke, sw=1.7, pad=9)
        f.append(b)
        f.append(line(edge_x, edge_y, cx, cy, color=stroke, sw=1.5))
        return pw, ph

    # L3GD20 гіроскоп (праворуч угорі від чипа) — SPI
    periph(bx + bw * 0.82, split_y + 60, "L3GD20\nгіроскоп (SPI)",
           "#eef6ef", FIELD, chx + chw / 2, chy - 30)
    # Touch (праворуч посередині)
    periph(bx + bw * 0.83, chy - 4, "лінійний touch\n+ touch-кнопки",
           "#fef6e7", "#b8860b", chx + chw / 2, chy - 6)
    # RF-EEPROM (праворуч знизу)
    periph(bx + bw * 0.82, chy + bh * 0.20, "рознім RF-EEPROM\n(M24LR / NFC)",
           "#eef1f5", NEG, chx + chw / 2, chy + 28)
    # USB пристрою (ліворуч знизу) — Mini-B, PA11/PA12
    f.append(rect(bx - 26, chy + 70 - 18, 40, 44, fill="#cfd6da", stroke=INK, sw=1.6, rx=4))
    f.append(text(bx - 6, chy + 70 - 26, "Mini-B", size=10, bold=True))
    periph(bx + bw * 0.16, chy + bh * 0.24, "USB пристрою\n(PA11/PA12)",
           "#eef1f5", INK, chx - chw / 2, chy + 20)
    f.append(line(bx + 14, chy + 70, bx + bw * 0.16 - 40, chy + 70, color=INK, sw=1.5))

    # 4 LED + кнопка B1 (низ, під чипом)
    ledy = by + bh - 34
    labels = [("PC6", "#ffb84d", "жовтогар."), ("PC8", "#2ecc71", "зелен."),
              ("PC9", "#e74c3c", "черв."), ("PC7", "#3d7bd6", "синій")]
    lx0 = chx - 120
    for i, (pin, col, nm) in enumerate(labels):
        cx = lx0 + i * 46
        f.append(circle(cx, ledy, 8, fill=col, stroke=INK, sw=1.4))
        f.append(text(cx, ledy + 24, pin, size=9, color=MUTED))
    f.append(text(lx0 + 3 * 46 / 2, ledy - 20, "4 світлодіоди навколо гіроскопа",
                  size=10, color=INK))
    # кнопка B1
    bxk = lx0 + 3 * 46 + 70
    f.append(rect(bxk - 22, ledy - 14, 44, 28, fill=BG, stroke=INK, sw=1.6, rx=5))
    f.append(text(bxk, ledy + 4, "B1", size=11, bold=True))
    f.append(text(bxk, ledy + 30, "USER · PA0", size=9, color=MUTED))

    return render(os.path.join(IMG, "disco-anatomy.svg"), W, H, *f)


# ── 2. Підключення: SWD-дебаг уже на платі; серійну консоль веде окремий CP2102 ─
def fig_wiring():
    W, H = 880, 560
    f = [text(W / 2, 30, "Дебаг — уже на платі (ST-LINK). Серійну консоль додає окремий CP2102",
              size=15, bold=True)]

    # ── ПК ──
    pcx, pcy, pcw, pch = 55, 150, 150, 90
    f.append(rect(pcx, pcy, pcw, pch, fill="#eef1f5", stroke=INK, sw=2, rx=12))
    f.append(text(pcx + pcw / 2, pcy + 34, "ПК", size=14, bold=True))
    f.append(text(pcx + pcw / 2, pcy + 58, "(Qt Creator,\ngdb, консоль)", size=10, color=MUTED))
    # багаторядок: перезапишемо коректно одним mtext
    f[-1] = mtext(pcx + pcw / 2, pcy + 56, ["Qt Creator, gdb,", "термінал"], size=10, color=MUTED)

    # ── Плата DISCO ──
    dbx, dby, dbw, dbh = W - 300, 90, 240, 400
    f.append(rect(dbx, dby, dbw, dbh, fill="#eaf3f4", stroke=FIELD, sw=2.2, rx=14))
    f.append(text(dbx + dbw / 2, dby + 26, "STM32F072B-DISCO", size=13, bold=True, color=FIELD))

    # ST-LINK блок на платі (верх)
    b, slw, slh = textbox(dbx + dbw / 2, dby + 78, "ST-LINK/V2\n(Mini-USB на платі)",
                          size=11, bold=True, fill="#eef1f5", stroke=INK, sw=1.7, pad=9)
    f.append(b)
    # цільовий чип на платі (низ)
    tcx, tcy = dbx + dbw / 2, dby + 250
    tcw, tch = 190, 90
    f.append(rect(tcx - tcw / 2, tcy - tch / 2, tcw, tch, fill="#20242a", stroke=INK, sw=2, rx=8))
    f.append(text(tcx, tcy - 12, "STM32F072RB", size=12.5, bold=True, color="#ffffff"))
    f.append(text(tcx, tcy + 8, "USART1:", size=10, color="#c9ccd1"))
    f.append(text(tcx, tcy + 24, "PA9=TX · PA10=RX", size=10, bold=True, color="#ffd24d"))
    # SWD усередині плати (ST-LINK → чип) — коротка внутрішня стрілка
    f.append(arrow(tcx, dby + 78 + slh / 2, tcx, tcy - tch / 2, color=INK, sw=1.8))
    f.append(text(tcx + 12, (dby + 78 + slh / 2 + tcy - tch / 2) / 2 + 4,
                  "SWD (на платі)", size=9.5, color=INK, anchor="start", italic=True))

    # ── USB1: ПК → ST-LINK (прошивка+дебаг) ──
    f.append(arrow(pcx + pcw, pcy + 20, dbx, dby + 78, color=INK, sw=2.2))
    f.append(text((pcx + pcw + dbx) / 2, pcy + 6, "USB①  прошивка + дебаг",
                  size=10.5, color=INK, italic=True))

    # ── CP2102 адаптер (внизу посередині) ──
    adx, ady = (pcx + pcw + dbx) / 2 - 40, H - 120
    b, aw, ah = textbox(adx, ady, "CP2102\nUSB→UART", size=11.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.8, pad=10)
    f.append(b)

    # USB2: ПК → CP2102
    f.append(arrow(pcx + 40, pcy + pch, adx - aw / 2 + 8, ady - ah / 2, color=POS, sw=2.0))
    f.append(text(pcx + 6, pcy + pch + 40, "USB②  серійний порт",
                  size=10.5, color=POS, anchor="start", italic=True))

    # три дроти CP2102 ↔ чип: TX→RX, RX→TX, GND↔GND (коридором праворуч від адаптера, у чип знизу)
    corr_x = adx + aw / 2 + 60
    ty0 = tcy + tch / 2
    # горизонталь від адаптера праворуч
    f.append(line(adx + aw / 2, ady - 10, corr_x, ady - 10, color=INK, sw=1.8))
    f.append(line(corr_x, ady - 10, corr_x, ty0 + 40, color=INK, sw=1.8))
    f.append(arrow(corr_x, ty0 + 40, tcx + 20, ty0 + 40, color=INK, sw=1.8))
    f.append(arrow(tcx + 20, ty0 + 40, tcx + 20, ty0, color=INK, sw=1.8))
    # підпис трьох дротів — у чистій зоні праворуч від коридору
    f.append(mtext(corr_x + 14, ty0 + 6,
                   ["3 дроти:", "TX→PA10 (RX)", "RX→PA9 (TX)", "GND ↔ GND"],
                   size=9.5, color=INK, anchor="start"))

    # застереження про рівні
    b, _, _ = textbox(W / 2, H - 26,
                      "CP2102 має віддавати 3.3 В логіку (перемичка/варіант 3V3) — 5 В на вивід STM32 небезпечні.",
                      size=10.5, fill=FILL, stroke=MUTED, sw=1.4, pad=9)
    f.append(b)

    return render(os.path.join(IMG, "disco-wiring.svg"), W, H, *f)


# ── 3. Порядок старту прошивки: від скидання до блимання (проєкт-довідник) ────
def fig_boot():
    W, H = 940, 300
    f = [text(W / 2, 30, "Порядок старту прошивки: що робить main() від скидання до блимання",
              size=15, bold=True)]

    steps = [
        ("Reset", "ядро на HSI\n8 МГц", "#eef1f5", INK),
        ("Flash: 1 wait", "перш ніж 48 МГц —\nдозволь Flash чекати", "#fdecea", POS),
        ("PLL ×12", "HSI/2 · 4 МГц\n→ 48 МГц", "#eef6ef", FIELD),
        ("SW = PLL", "перемкнути\nсистемний такт", "#eef6ef", FIELD),
        ("такт GPIOC", "RCC->AHBENR\n(без нього — німо)", "#fef6e7", "#b8860b"),
        ("PC6 = вихід", "MODER[6] = 01", "#eef1f5", INK),
        ("блимай", "ODR ^= (1<<6)\nу циклі", "#eef1f5", INK),
    ]
    n = len(steps)
    bw, gap = 108, 14
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 150
    for i, (t, sub, fill, stroke) in enumerate(steps):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - 42, bw, 84, fill=fill, stroke=stroke, sw=1.9, rx=9))
        f.append(text(x + bw / 2, cy - 22, t, size=11.5, bold=True, color=stroke))
        f.append(mtext(x + bw / 2, cy - 2, sub, size=9.2, color=INK))
        if i < n - 1:
            f.append(arrow(x + bw, cy, x + bw + gap, cy, color=MUTED, sw=1.8))

    # виноска про найчастішу пастку
    b, _, _ = textbox(W / 2, H - 34,
                      "Забув «такт GPIOC» — вивід ніби налаштований, а світлодіод мовчить: периферія без тактування мертва.",
                      size=10.5, fill=FILL, stroke=MUTED, sw=1.4, pad=9)
    f.append(b)
    return render(os.path.join(IMG, "disco-boot.svg"), W, H, *f)


# ── 4. SPI-транзакція читання L3GD20: командний байт (біти R/W та AI) + дані ───
def fig_spi_read():
    W, H = 900, 430
    f = [text(W / 2, 30, "Читання гіроскопа по SPI: перший байт — команда, далі течуть дані",
              size=15, bold=True)]

    # CS ↓ рамка транзакції
    csx0, csx1 = 70, W - 60
    csy = 78
    f.append(text(csx0 - 6, csy + 4, "CS (PC0)", size=11, bold=True, anchor="end"))
    # CS високий → падає → низький упродовж обміну → піднімається
    f.append(line(csx0, csy - 12, csx0 + 20, csy - 12, color=NEG, sw=2.4))          # high
    f.append(line(csx0 + 20, csy - 12, csx0 + 20, csy + 10, color=NEG, sw=2.4))     # fall
    f.append(line(csx0 + 20, csy + 10, csx1 - 20, csy + 10, color=NEG, sw=2.4))     # low (active)
    f.append(line(csx1 - 20, csy + 10, csx1 - 20, csy - 12, color=NEG, sw=2.4))     # rise
    f.append(line(csx1 - 20, csy - 12, csx1, csy - 12, color=NEG, sw=2.4))          # high
    f.append(text(csx0 + 20, csy + 30, "↓ тягнемо в 0 — «слухай мене»", size=9.5,
                  color=NEG, anchor="start", italic=True))
    f.append(text(csx1 - 20, csy - 20, "↑ у 1 — кінець", size=9.5, color=NEG,
                  anchor="end", italic=True))

    # Байти на шині: командний, тоді 6 байтів даних (X,Y,Z по 2)
    by = 150
    bh = 52
    cell = [
        ("команда\n1 1 101000", "#fdecea", POS, "R=1 · AI=1\nадреса 0x28"),
        ("XL", "#eef6ef", FIELD, "OUT_X_L"),
        ("XH", "#eef6ef", FIELD, "OUT_X_H"),
        ("YL", "#eef1f5", NEG, "OUT_Y_L"),
        ("YH", "#eef1f5", NEG, "OUT_Y_H"),
        ("ZL", "#fef6e7", "#b8860b", "OUT_Z_L"),
        ("ZH", "#fef6e7", "#b8860b", "OUT_Z_H"),
    ]
    n = len(cell)
    cw, gap = 108, 8
    total = n * cw + (n - 1) * gap
    x0 = (W - total) / 2
    for i, (t, fill, stroke, note) in enumerate(cell):
        x = x0 + i * (cw + gap)
        f.append(rect(x, by, cw, bh, fill=fill, stroke=stroke, sw=1.9, rx=7))
        f.append(mtext(x + cw / 2, by + bh / 2 - 4, t, size=10.5, bold=True, color=stroke))
        f.append(mtext(x + cw / 2, by + bh + 16, note, size=9, color=MUTED))
        # напрям: MOSI віддає лише команду; решта — MISO віддає чип
        if i == 0:
            f.append(text(x + cw / 2, by - 10, "MOSI (ти→чип)", size=9, color=POS))
        elif i == 1:
            f.append(text(x + cw / 2, by - 10, "◄──────────  MISO (чип→ти)  ──────────►",
                          size=9, color=FIELD, anchor="start"))

    # пояснення двох бітів команди
    exp_y = by + bh + 58
    f.append(mtext(x0, exp_y,
                   ["Старший байт команди — це два прапорці + 6-бітна адреса:"],
                   size=10.5, color=INK, anchor="start"))
    b1, _, _ = textbox(x0 + 150, exp_y + 40, "біт7 = R/W\n1 = читаю",
                       size=10, fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    b2, _, _ = textbox(x0 + 360, exp_y + 40, "біт6 = AI\n1 = адреса\nсама росте",
                       size=10, fill="#eef6ef", stroke=FIELD, sw=1.6, pad=8)
    b3, _, _ = textbox(x0 + 600, exp_y + 40, "біти5..0 = 0x28\nстарт: OUT_X_L",
                       size=10, fill="#eef1f5", stroke=INK, sw=1.6, pad=8)
    f.append(b1); f.append(b2); f.append(b3)

    b, _, _ = textbox(W / 2, H - 26,
                      "Без AI=1 адреса не росте — прочитаєш той самий байт шість разів. Це найчастіша причина «сміття» з гіроскопа.",
                      size=10.5, fill=FILL, stroke=MUTED, sw=1.4, pad=9)
    f.append(b)
    return render(os.path.join(IMG, "disco-spi-read.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_wiring()
    fig_boot()
    fig_spi_read()
    print("OK: disco-anatomy.svg, disco-wiring.svg, disco-boot.svg, disco-spi-read.svg")
