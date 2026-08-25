# -*- coding: utf-8 -*-
"""Фігури до теми «eMMC і SSD» та її вставки про FTL.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
STALE = "#b9770e"     # застаріла сторінка (тепле)
VALID = "#27ae60"     # чинна сторінка (= FIELD)
FREE  = "#6b7280"     # вільна стерта сторінка (= MUTED)


# ── 1. FTL — прошарок, що вдає диск (стаття) ─────────────────────────────────
def fig_ftl_layer():
    W, H = 760, 430
    f = [text(W / 2, 26, "FTL вдає диск: бруд NAND нагору не просочується",
              size=15, bold=True)]

    # Верх: рівний диск, який бачить ОС
    f.append(rect(40, 50, 680, 86, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(60, 72, "операційна система бачить рівний диск", size=12.5,
                  color=NEG, anchor="start", bold=True))
    for i in range(8):
        x = 64 + i * 82
        f.append(rect(x, 88, 72, 36, fill=BG, stroke=NEG, sw=1.3))
        f.append(text(x + 36, 111, "сектор %d" % (1000 + i), size=9.5, color=NEG))
    f.append(text(W / 2, 132, "кожен сектор читають, пишуть і перезаписують на місці",
                  size=9.5, color=MUTED, italic=True))

    # Середина: контролер із FTL
    f.append(rect(140, 166, 480, 96, fill="#e9f7ef", stroke=FIELD, sw=2))
    f.append(text(W / 2, 188, "контролер · FTL", size=13, color=FIELD, bold=True))
    f.append(text(W / 2, 208, "таблиця: логічний сектор → фізична сторінка",
                  size=11, color=INK))
    for label, cx in (("ховає\nдефекти", 230), ("розкидає\nзнос", 380),
                      ("прибирає\nсміття", 530)):
        f.append(mtext(cx, 230, label, size=9.5, color=MUTED))

    # стрілки між шарами (двобічний обмін)
    f.append(arrow(W / 2 - 60, 138, W / 2 - 60, 164, color=NEG, sw=1.8))
    f.append(arrow(W / 2 + 60, 164, W / 2 + 60, 138, color=NEG, sw=1.8))
    f.append(arrow(W / 2 - 60, 264, W / 2 - 60, 296, color=FIELD, sw=1.8))
    f.append(arrow(W / 2 + 60, 296, W / 2 + 60, 264, color=FIELD, sw=1.8))

    # Низ: реальна NAND
    f.append(rect(40, 298, 680, 96, fill="#fdf3f2", stroke=POS, sw=1.8))
    f.append(text(60, 320, "реальна NAND", size=12.5, color=POS, anchor="start",
                  bold=True))
    notes = ["доступ\nсторінками", "стирання\nблоками", "дефектні\nкомірки",
             "обмежений\nресурс"]
    for i, nt in enumerate(notes):
        cx = 150 + i * 160
        f.append(rect(cx - 66, 332, 132, 50, fill=BG, stroke=POS, sw=1.3))
        f.append(mtext(cx, 352, nt, size=10, color=POS))

    f.append(text(W / 2, 414,
                  "уся незручність NAND замкнена у FTL — нагору видно лише рівний диск",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "ftl-layer.svg"), W, H, *f)


# ── 2. Одна ідea в трьох масштабах: SD · eMMC · SSD (стаття) ─────────────────
def fig_emmc_ssd():
    W, H = 780, 360
    f = [text(W / 2, 26, "Одна ідея «NAND + контролер» у трьох масштабах",
              size=15, bold=True)]

    cards = [
        ("SD-картка", FIELD, "знімна", "1 контролер · кілька кристалів",
         "шина SD / SPI", "десятки МБ/с", "знімне сховище"),
        ("eMMC", NEG, "впаяна одним корпусом", "контролер + NAND у BGA",
         "ширша паралельна шина", "сотні МБ/с", "телефони, IoT"),
        ("SSD", POS, "окремий накопичувач", "потужний контролер + кеш",
         "шина SATA / NVMe", "тисячі МБ/с", "ПК і сервери"),
    ]
    x = 24
    cw = 236
    for title_, col, kind, guts, bus, speed, use in cards:
        f.append(rect(x, 50, cw, 252, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + cw / 2, 78, title_, size=15, color=col, bold=True))
        f.append(line(x + 16, 90, x + cw - 16, 90, color="#dddddd", sw=1.2))
        # внутрішнє «NAND + контролер»
        f.append(rect(x + 28, 104, cw - 56, 30, fill=BG, stroke=col, sw=1.3))
        f.append(text(x + cw / 2, 124, "NAND + FTL", size=11.5, color=col, bold=True))
        rows = [("корпус", kind), ("нутрощі", guts), ("шина", bus),
                ("швидкість", speed), ("де живе", use)]
        ry = 158
        for k, v in rows:
            f.append(text(x + 18, ry, k, size=10, color=MUTED, anchor="start"))
            f.append(fitbox(x + 18, ry + 6, cw - 36, 22, v, size=10.5, color=INK,
                            bold=True, fill=FILL, stroke="none", sw=0))
            ry += 28
        x += 252

    f.append(text(W / 2, 332,
                  "росте лише потужність контролера й ширина шини — серце скрізь те саме",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "emmc-ssd.svg"), W, H, *f)


# ── 2b. Той самий рушій — різні інтерфейси до системи (стаття, detailed) ─────
def fig_interfaces():
    W, H = 900, 372
    f = [text(W / 2, 26, "Та сама «NAND + FTL» — різні інтерфейси до системи",
              size=15, bold=True)]
    cards = [
        ("SD-картка",   NEG,   "SD, 1–4 біт",    "одна команда", "~100 МБ/с", "камери, дрібне"),
        ("eMMC",        NEG,   "8 біт, паралель", "одна команда", "~400 МБ/с", "телефони, IoT"),
        ("UFS",         FIELD, "серійна, M-PHY",  "черга на 32",  "~2–4 ГБ/с", "нові телефони"),
        ("SATA · AHCI", MUTED, "SATA, серійна",   "одна на 32",   "~0.5 ГБ/с", "спадок дисків"),
        ("NVMe · PCIe", POS,   "PCIe, ×4 лінії",  "тисячі черг",  "~3–7 ГБ/с", "ПК і сервери"),
    ]
    x, cw, gap = 18, 160, 16
    for name, col, bus, q, speed, use in cards:
        f.append(rect(x, 50, cw, 262, fill=FILL, stroke=col, sw=1.8))
        f.append(fitbox(x + 10, 60, cw - 20, 26, name, size=14, color=col, bold=True,
                        fill=FILL, stroke="none", sw=0))
        f.append(line(x + 14, 94, x + cw - 14, 94, color="#dddddd", sw=1.2))
        for i, (k, v) in enumerate((("шина", bus), ("черга команд", q),
                                    ("стеля", speed), ("де живе", use))):
            ry = 116 + i * 44
            f.append(text(x + 16, ry, k, size=10, color=MUTED, anchor="start"))
            f.append(fitbox(x + 16, ry + 6, cw - 32, 24, v, size=11, color=INK,
                            bold=True, fill=FILL, stroke="none", sw=0))
        x += cw + gap
    f.append(text(W / 2, 344,
                  "що глибша й численніша черга, то повніше виходить назовні паралелізм кристалів NAND",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "interfaces.svg"), W, H, *f)


# ── 3. Один рівень непрямості: LBA → таблиця → фізична сторінка (вставка) ─────
def _nand_block(f, x, y, label, pages, col=INK):
    """Блок NAND із 4 сторінок; pages = список (підпис, колір рамки)."""
    f.append(rect(x, y, 150, 132, fill="#fcfcfd", stroke="#cfcfd6", sw=1.4))
    f.append(text(x + 75, y + 18, label, size=10.5, color=col, bold=True))
    for i, (cap, c) in enumerate(pages):
        py = y + 28 + i * 24
        f.append(rect(x + 12, py, 126, 20, fill=BG, stroke=c, sw=1.4))
        f.append(text(x + 75, py + 14, cap, size=9.5, color=c))


def fig_indirection():
    W, H = 760, 320
    f = [text(W / 2, 26, "FTL — один рівень непрямості", size=15, bold=True)]

    # Хост: рівні LBA
    f.append(rect(24, 70, 150, 180, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(99, 92, "хост: LBA", size=12, color=NEG, bold=True))
    for i, n in enumerate((7, 8, 9, 10)):
        py = 104 + i * 34
        f.append(rect(36, py, 126, 26, fill=BG, stroke=NEG, sw=1.3))
        f.append(text(99, py + 17, "сектор %d" % n, size=10.5, color=NEG))

    # Таблиця відображення
    f.append(rect(258, 70, 230, 180, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    f.append(text(373, 92, "таблиця в RAM контролера", size=11, color=FIELD, bold=True))
    rows = [("сектор 7", "блок 0 · стор. 2"), ("сектор 8", "блок 2 · стор. 0"),
            ("сектор 9", "блок 0 · стор. 3"), ("сектор 10", "блок 2 · стор. 1")]
    for i, (a, b) in enumerate(rows):
        py = 108 + i * 32
        f.append(text(276, py + 4, a, size=10, color=INK, anchor="start"))
        f.append(text(284, py + 4, "→", size=10, color=MUTED))
        f.append(text(470, py + 4, b, size=10, color=INK, anchor="end"))
        if i < 3:
            f.append(line(270, py + 14, 478, py + 14, color="#d6e8dd", sw=1))

    # Фізична NAND: блок 0 (тут лежать сектори 7 і 9)
    _nand_block(f, 560, 92, "блок 0", [("стор.0", FREE), ("стор.1", FREE),
                                       ("с.7 (стор.2)", NEG), ("с.9 (стор.3)", NEG)])

    f.append(arrow(176, 160, 254, 160, color=INK, sw=2))
    f.append(arrow(490, 145, 556, 150, color=INK, sw=1.8))

    f.append(text(W / 2, 306,
                  "логічний номер відв'язано від місця — завтра той самий сектор у іншому блоці",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "indirection.svg"), W, H, *f)


# ── 4. Запис «не на місці» плодить застарілі сторінки (вставка) ──────────────
def fig_oop_write():
    W, H = 760, 300
    f = [text(W / 2, 26, "Запис «не на місці»: оновлення йде в нову сторінку",
              size=15, bold=True)]

    # ДО запису
    f.append(text(150, 64, "до запису в сектор 9", size=11.5, color=INK, bold=True))
    _nand_block(f, 75, 78, "блок 0",
                [("с.9 = v1", VALID), ("стор.1", FREE), ("стор.2", FREE),
                 ("стор.3", FREE)])
    f.append(text(150, 232, "таблиця: с.9 → стор.0", size=10, color=MUTED, italic=True))

    f.append(arrow(245, 150, 330, 150, color=INK, sw=2))
    f.append(text(287, 138, "пиши с.9 = v2", size=9.5, color=NEG, italic=True))

    # ПІСЛЯ запису
    f.append(text(560, 64, "після запису", size=11.5, color=INK, bold=True))
    _nand_block(f, 485, 78, "блок 0",
                [("с.9 = v1", STALE), ("с.9 = v2", VALID), ("стор.2", FREE),
                 ("стор.3", FREE)])
    f.append(text(560, 232, "таблиця: с.9 → стор.1", size=10, color=MUTED, italic=True))

    # легенда
    lx = 95
    for cap, c in (("чинна", VALID), ("застаріла", STALE), ("вільна", FREE)):
        f.append(rect(lx, 256, 14, 14, fill=BG, stroke=c, sw=1.6))
        f.append(text(lx + 20, 268, cap, size=10, color=c, anchor="start"))
        lx += 130

    f.append(text(W / 2, 292,
                  "жоден біт не переписано «на місці» — стара версія просто стає сміттям",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "oop-write.svg"), W, H, *f)


# ── 5. Garbage collection: зібрати чинне, стерти блок (вставка) ──────────────
def fig_gc():
    W, H = 780, 320
    f = [text(W / 2, 26, "Прибирання сміття: чинне в інший блок, жертву — стерти",
              size=15, bold=True)]

    # блок-жертва (до)
    f.append(text(110, 64, "блок-жертва (до)", size=11, color=INK, bold=True))
    _nand_block(f, 35, 78, "блок 0",
                [("чинна A", VALID), ("застаріла", STALE), ("чинна B", VALID),
                 ("застаріла", STALE)])

    # цільовий блок (до)
    f.append(text(330, 64, "вільний блок", size=11, color=INK, bold=True))
    _nand_block(f, 255, 78, "блок 5",
                [("стор.0", FREE), ("стор.1", FREE), ("стор.2", FREE),
                 ("стор.3", FREE)])

    # копіювання чинних
    f.append(arrow(190, 110, 252, 108, color=VALID, sw=1.8))
    f.append(arrow(190, 158, 252, 132, color=VALID, sw=1.8))
    f.append(text(222, 92, "копіюй чинне", size=9, color=VALID, italic=True))

    # результат: стертий блок
    f.append(arrow(410, 130, 470, 130, color=INK, sw=2))
    f.append(text(440, 118, "стерти", size=9.5, color=POS, italic=True))
    f.append(text(560, 64, "жертву стерто", size=11, color=INK, bold=True))
    _nand_block(f, 485, 78, "блок 0",
                [("стор.0", FREE), ("стор.1", FREE), ("стор.2", FREE),
                 ("стор.3", FREE)])
    f.append(text(560, 232, "+ таблицю A,B → блок 5", size=9.5, color=MUTED,
                  italic=True))

    # легенда
    lx = 90
    for cap, c in (("чинна", VALID), ("застаріла", STALE), ("вільна", FREE)):
        f.append(rect(lx, 256, 14, 14, fill=BG, stroke=c, sw=1.6))
        f.append(text(lx + 20, 268, cap, size=10, color=c, anchor="start"))
        lx += 150

    f.append(text(W / 2, 300,
                  "ціна — «зайвий» перезапис чинних сторінок (підсилення запису)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gc.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ftl_layer()
    fig_emmc_ssd()
    fig_interfaces()
    fig_indirection()
    fig_oop_write()
    fig_gc()
    print("OK: 6 figures ->", IMG)
