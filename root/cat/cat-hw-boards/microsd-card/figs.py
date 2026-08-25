# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «microSD-модуль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дві мови картки: SPI (4 лінії) проти SDIO (6 ліній) ────────────────────
def fig_spi_vs_sdio():
    W, H = 780, 430
    f = [text(W / 2, 28, "Те саме гніздо — дві мови: проста SPI або швидка SDIO",
              size=15, bold=True)]

    cw = 330
    lx, rx = 50, W - 50 - cw
    topY = 56
    boxH = 300

    # спільна підпис-картка картки в центрі кожної панелі
    def panel(px, title, sub, accent, fill, lines, foot):
        f.append(rect(px, topY, cw, boxH, fill=fill, stroke=accent, sw=1.8, rx=10))
        f.append(text(px + cw / 2, topY + 26, title, size=13.5, bold=True, color=accent))
        f.append(text(px + cw / 2, topY + 44, sub, size=10.5, color=MUTED))
        # МК ліворуч, картка праворуч, лінії між ними
        mcx = px + 44
        scx = px + cw - 44
        my = topY + 130
        f.append(rect(mcx - 32, my - 40, 64, 80, fill=BG, stroke=INK, sw=1.6, rx=8))
        f.append(text(mcx, my - 4, "МК", size=11, bold=True))
        f.append(rect(scx - 30, my - 40, 60, 80, fill=BG, stroke=INK, sw=1.6, rx=8))
        f.append(text(scx, my - 8, "SD", size=11, bold=True))
        f.append(text(scx, my + 11, "картка", size=9, color=MUTED))
        # лінії
        n = len(lines)
        y0 = my - (n - 1) * 13 / 2
        for i, (lbl, col, bidir) in enumerate(lines):
            ly = y0 + i * 13
            f.append(line(mcx + 32, ly, scx - 30, ly, color=col, sw=2.0))
            f.append(text(px + cw / 2, ly - 4, lbl, size=9, color=col, bold=True))
        # підсумок-стрічка
        f.append(text(px + cw / 2, topY + boxH - 40, foot[0], size=10.5, color=INK))
        f.append(text(px + cw / 2, topY + boxH - 22, foot[1], size=10.5, color=accent, italic=True))

    panel(lx, "SPI — проста й всюдисуща", "є в кожного мікроконтролера", NEG, "#eef2f8",
          [("CS", INK, False), ("SCK", INK, False),
           ("MOSI →", POS, False), ("← MISO", NEG, False)],
          ("одна лінія даних у кожен бік", "просто підключити, швидкість нижча"))

    panel(rx, "SDIO — рідна швидка мова", "потрібен окремий контролер", FIELD, "#eef6ef",
          [("CMD", INK, True), ("CLK", INK, False),
           ("DAT0..DAT3", FIELD, True), ("(4 лінії паралельно)", MUTED, True)],
          ("чотири лінії даних разом", "набагато швидше, складніше"))

    b, _, _ = textbox(W / 2, 410,
                      "режим обирається в перші такти після ввімкнення; дешеві модулі — майже завжди SPI",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "spi-vs-sdio.svg"), W, H, *f)


# ── 2. Анатомія дешевого модуля: гніздо + стабілізатор 3.3В + буфер рівнів ─────
def fig_module_anatomy():
    W, H = 800, 440
    f = [text(W / 2, 28, "Усередині дешевого модуля: посередник, що готує 3.3 В і рівні",
              size=15, bold=True)]

    # межа плати модуля
    bx, by, bw, bh = 250, 60, 300, 300
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(bx + bw / 2, by + 22, "microSD-модуль", size=12, bold=True, color=MUTED))

    # вхід зліва: 5В живлення + сигнали господаря
    inx = 70
    f.append(rect(inx - 40, 90, 90, 110, fill="#eef2f8", stroke=INK, sw=1.6, rx=8))
    f.append(text(inx + 5, 112, "Господар", size=11, bold=True))
    f.append(text(inx + 5, 130, "(МК / Arduino)", size=9, color=MUTED))
    f.append(text(inx + 5, 156, "5 В", size=10, bold=True, color=POS))
    f.append(text(inx + 5, 176, "SCK/MOSI/CS", size=9, color=INK))

    # стабілізатор
    regx, regy = bx + 70, by + 80
    f.append(rect(regx - 55, regy - 26, 110, 52, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(regx, regy - 6, "AMS1117", size=11, bold=True, color=POS))
    f.append(text(regx, regy + 12, "5 В → 3.3 В", size=9.5, color=INK))
    # 5В у стабілізатор
    f.append(line(inx + 50, 156, regx - 55, regy, color=POS, sw=2.2))
    f.append(text((inx + 50 + regx) / 2, 150, "5 В", size=9, color=POS))

    # буфер рівнів
    bufx, bufy = bx + 70, by + 185
    f.append(rect(bufx - 55, bufy - 28, 110, 56, fill="#eaf0fd", stroke=NEG, sw=1.7, rx=8))
    f.append(text(bufx, bufy - 6, "74HC125", size=11, bold=True, color=NEG))
    f.append(text(bufx, bufy + 12, "буфер рівнів", size=9.5, color=INK))
    # сигнали у буфер
    f.append(line(inx + 50, 176, bufx - 55, bufy, color=INK, sw=2.0))
    f.append(text((inx + 50 + bufx) / 2, 198, "сигнали", size=9, color=INK))

    # картка праворуч у модулі
    cardx, cardy = bx + bw - 60, by + bh / 2 + 10
    f.append(rect(cardx - 36, cardy - 55, 72, 110, fill=BG, stroke=INK, sw=1.8, rx=8))
    f.append(text(cardx, cardy - 24, "SD", size=12, bold=True))
    f.append(text(cardx, cardy - 6, "картка", size=9, color=MUTED))
    f.append(text(cardx, cardy + 18, "пам'ять", size=9, color=MUTED))
    f.append(text(cardx, cardy + 36, "+ контролер", size=9, color=MUTED))

    # 3.3В живлення на картку
    f.append(line(regx + 55, regy, cardx - 36, cardy - 30, color=FIELD, sw=2.2))
    f.append(text((regx + 55 + cardx) / 2 + 6, regy - 4, "3.3 В", size=9.5, bold=True, color=FIELD))
    # 3.3В сигнали на картку
    f.append(line(bufx + 55, bufy, cardx - 36, cardy + 20, color=FIELD, sw=2.0))
    f.append(text((bufx + 55 + cardx) / 2 + 4, bufy + 18, "3.3 В сигнали", size=9, color=FIELD))

    b, _, _ = textbox(W / 2, 412,
                      "до картки доходять лише 3.3 В — сама пам'ять у картці; модуль нічого не зберігає",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "module-anatomy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spi_vs_sdio()
    fig_module_anatomy()
    print("OK: 2 figures ->", IMG)
