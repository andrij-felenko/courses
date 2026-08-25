# -*- coding: utf-8 -*-
"""Фігури до теми «ESP-Hosted».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CODE_BG = "#1b1f24"      # темна заливка код-панелі
CODE_FG = "#cfe8cf"      # світло-зелений код
AMBER   = "#b08900"      # тепле виділення (лінія-транспорт)


# ── 1. Суть: хост без радіо бере радіо сусіда ─────────────────────────────────
# Ідея: ліворуч — потужний хост БЕЗ антени; праворуч — дешевий ESP із радіо;
# між ними дріт-транспорт. Радіо фізично в сусіда, а хост ним користується.
def fig_idea():
    W, H = 760, 290
    f = [text(W / 2, 26, "ESP-Hosted: хост бере радіо сусіднього чипа", size=15, bold=True)]

    by, bh = 92, 92
    # хост (без радіо)
    hx, hw = 56, 250
    f.append(rect(hx, by, hw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(hx + hw / 2, by + 26, "ХОСТ (ведучий)", size=12, color=NEG, bold=True))
    f.append(mtext(hx + hw / 2, by + 50, ["ESP32-P4 / Linux / STM32", "рахує, але радіо НЕ має"],
                   size=10, color=INK))
    f.append(text(hx + hw / 2, by + bh + 18, "✗ без власної антени", size=10, color=POS, italic=True))

    # ведений (з радіо)
    sx, sw = 454, 250
    f.append(rect(sx, by, sw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(sx + sw / 2, by + 26, "ВЕДЕНИЙ (радіо-чип)", size=12, color=FIELD, bold=True))
    f.append(mtext(sx + sw / 2, by + 50, ["ESP32-C6 / C3 / 32", "увесь Wi-Fi і Bluetooth"],
                   size=10, color=INK))
    f.append(text(sx + sw / 2, by + bh + 18, "((•)) має радіо", size=10, color=FIELD, italic=True))

    # лінія-транспорт між ними, обидва напрямки
    midy = by + bh / 2
    f.append(arrow(hx + hw + 4, midy - 12, sx - 4, midy - 12, color=AMBER, sw=2.4))
    f.append(arrow(sx - 4, midy + 12, hx + hw + 4, midy + 12, color=AMBER, sw=2.4))
    f.append(text((hx + hw + sx) / 2, midy - 18, "SDIO / SPI / UART", size=9, color=AMBER, bold=True))

    f.append(text(W / 2, H - 14,
                  "радіо фізично в сусіда — а хост користується ним, наче власним",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ── 2. Лінія-транспорт: три способи з'єднати чипи ──────────────────────────────
# Ідея: між хостом і веденим — одна з трьох шин; різна швидкість, та сама роль.
def fig_transport():
    W, H = 760, 300
    f = [text(W / 2, 26, "Лінія між чипами: одна з трьох шин", size=15, bold=True)]

    rows = [
        ("SDIO", "найшвидша; типовий вибір під Wi-Fi-потік (на P4-платі — 4 лінії, 40 МГц)", FIELD),
        ("SPI",  "простіша й невибаглива до ніжок; повний або половинний дуплекс", NEG),
        ("UART", "найпростіша, для скромного трафіку та Bluetooth-HCI", MUTED),
    ]
    nx, nw = 60, 130
    dx, dw = nx + nw + 24, 510
    y = 64
    for name, note, col in rows:
        f.append(rect(nx, y, nw, 54, fill="#fbfbfb", stroke=col, sw=1.8, rx=9))
        f.append(text(nx + nw / 2, y + 32, name, size=14, color=col, bold=True))
        f.append(arrow(nx + nw + 4, y + 27, dx - 4, y + 27, color=INK, sw=1.6))
        f.append(rect(dx, y, dw, 54, fill="#f7f7f7", stroke=col, sw=1.2, rx=9))
        f.append(fitbox(dx + 8, y + 8, dw - 16, 38, note, size=10.5, color=INK,
                        fill="#f7f7f7", stroke="none", sw=0))
        y += 70

    f.append(text(W / 2, H - 12,
                  "роль однакова — змінюється лише швидкість і скільки ніжок коштує",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "transport.svg"), W, H, *f)


# ── 3. Дві дороги по лінії: керування і дані ──────────────────────────────────
# Ідея: команди (під'єднайся, скануй) їдуть як упаковані RPC; самі мережеві
# пакети течуть напряму, без упакування — щоб не гальмувати потік.
def fig_paths():
    W, H = 760, 300
    f = [text(W / 2, 26, "Дві дороги однією лінією: керування й дані", size=15, bold=True)]

    hx, hw = 40, 200
    sx, sw = 520, 200
    by, bh = 70, 170
    f.append(rect(hx, by, hw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(hx + hw / 2, by + 26, "ХОСТ", size=12.5, color=NEG, bold=True))
    f.append(mtext(hx + hw / 2, by + 52, ["твій код:", "esp_wifi_… як завжди"], size=10, color=INK))

    f.append(rect(sx, by, sw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(sx + sw / 2, by + 26, "ВЕДЕНИЙ", size=12.5, color=FIELD, bold=True))
    f.append(mtext(sx + sw / 2, by + 52, ["справжній", "радіо-стек + антена"], size=10, color=FIELD))

    # верхня дорога — керування (RPC, упаковане)
    y1 = by + 50
    f.append(arrow(hx + hw + 4, y1, sx - 4, y1, color=AMBER, sw=2.2))
    f.append(text((hx + hw + sx) / 2, y1 - 10, "КЕРУВАННЯ: «під'єднайся», «скануй»",
                  size=10, color=AMBER, bold=True))
    f.append(text((hx + hw + sx) / 2, y1 + 16, "упаковане в RPC (protobuf)", size=9, color=MUTED, italic=True))

    # нижня дорога — дані (напряму)
    y2 = by + 130
    f.append(arrow(hx + hw + 4, y2, sx - 4, y2, color=POS, sw=2.6))
    f.append(arrow(sx - 4, y2 + 20, hx + hw + 4, y2 + 20, color=POS, sw=2.6))
    f.append(text((hx + hw + sx) / 2, y2 - 8, "ДАНІ: самі мережеві пакети",
                  size=10, color=POS, bold=True))
    f.append(text((hx + hw + sx) / 2, y2 + 38, "течуть напряму, БЕЗ упакування", size=9, color=MUTED, italic=True))

    f.append(text(W / 2, H - 12,
                  "команди можна впакувати, а потік даних — ні: інакше радіо гальмувало б",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "paths.svg"), W, H, *f)


# ── 4. Ініціалізація транспорту: що відбувається на старті ─────────────────────
# Ідея: послідовність кроків від увімкнення до «маю IP» — і де саме радіо.
def fig_init():
    W, H = 760, 300
    f = [text(W / 2, 26, "Старт: від увімкнення до «маю адресу в мережі»", size=15, bold=True)]

    steps = [
        ("1", "хост піднімає\nлінію (SDIO/SPI)", NEG),
        ("2", "рукостискання\nз веденим", AMBER),
        ("3", "esp_wifi_remote:\nрадіо «своє»", FIELD),
        ("4", "connect → ведений\nкрутить радіо", FIELD),
        ("5", "пакети течуть,\nхост має IP", POS),
    ]
    n = len(steps)
    cw, gap = 122, 20
    x = (W - (cw * n + gap * (n - 1))) / 2
    cy, ch = 80, 130
    prev = None
    for num, label, col in steps:
        f.append(rect(x, cy, cw, ch, fill="#fbfbfb", stroke=col, sw=1.8, rx=12))
        f.append(circle(x + cw / 2, cy + 28, 15, fill="#fbfbfb", stroke=col, sw=2))
        f.append(text(x + cw / 2, cy + 33, num, size=13, color=col, bold=True))
        f.append(mtext(x + cw / 2, cy + 66, label.split("\n"), size=9.6, color=INK))
        if prev is not None:
            f.append(arrow(prev, cy + ch / 2, x - 4, cy + ch / 2, color=INK, sw=1.6))
        prev = x + cw
        x += cw + gap

    f.append(text(W / 2, H - 14,
                  "для коду це звичайний Wi-Fi — лиш перший крок (підняти лінію) новий",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "init.svg"), W, H, *f)


# ── 5. Коли ESP-Hosted, а коли одночиповий ESP32 ──────────────────────────────
# Ідея: дві колонки тригерів — два чипи доречні, коли «мозок» сам без радіо;
# один чип кращий, коли він і рахує, і має радіо «з коробки».
def fig_when():
    W, H = 760, 318
    f = [text(W / 2, 26, "ESP-Hosted (два чипи) чи одночиповий ESP32", size=15, bold=True)]

    lx, lw = 40, 330
    rx, rw = 410, 330
    by, bh = 60, 210
    f.append(rect(lx, by, lw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, by + 26, "ESP-Hosted: ведучий + ведений", size=12, color=FIELD, bold=True))
    for i, s in enumerate(["• «мозок» без радіо (ESP32-P4, STM32, Linux)",
                           "• потрібен Wi-Fi 6 / BLE, а чип його не має",
                           "• радіо доточуємо рівно тоді, коли треба",
                           "• одне сертифіковане радіо на різні плати"]):
        f.append(text(lx + 16, by + 56 + i * 34, s, size=10.2, color=INK, anchor="start"))

    f.append(rect(rx, by, rw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(rx + rw / 2, by + 26, "Одночиповий ESP32 (S3/C3/C6)", size=12, color=NEG, bold=True))
    for i, s in enumerate(["• чип і рахує, і має радіо «з коробки»",
                           "• проста, дешева, масова річ — один корпус",
                           "• не треба ні зайвої плати, ні другої шини",
                           "• обчислень рівно стільки, скільки чип тягне"]):
        f.append(text(rx + 16, by + 56 + i * 34, s, size=10.2, color=INK, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "питання не «скільки чипів», а «чи має той, хто рахує, власне радіо»",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "when.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_transport()
    fig_paths()
    fig_init()
    fig_when()
    print("OK: 5 figures ->", IMG)
