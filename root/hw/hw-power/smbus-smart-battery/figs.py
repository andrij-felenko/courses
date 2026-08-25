# -*- coding: utf-8 -*-
"""Фігури до теми «Smart Battery і SMBus: протокол і команди».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Карта шини SBS: чотири вузли з фіксованими адресами ────────────────────
def fig_bus_map():
    W, H = 820, 430
    f = [text(W / 2, 30, "Одна шина SMBus — чотири ролі з фіксованими адресами", size=16, bold=True)]
    # спільна лінія SDA/SCL
    busy = 250
    x0, x1 = 60, W - 60
    f.append(line(x0, busy, x1, busy, color=INK, sw=3))
    f.append(line(x0, busy + 16, x1, busy + 16, color=INK, sw=3))
    f.append(text(x1 + 2, busy - 8, "SDA", size=12, color=MUTED, anchor="end"))
    f.append(text(x1 + 2, busy + 40, "SCL", size=12, color=MUTED, anchor="end"))
    # підтяжки
    f.append(text(x0 + 8, busy - 26, "+3.3 В ⎓ через 2 підтяжки", size=11, color=MUTED, anchor="start"))
    f.append(line(x0 + 40, busy - 18, x0 + 40, busy, color=MUTED, sw=1.2, dash="4,3"))
    f.append(line(x0 + 70, busy - 18, x0 + 70, busy + 16, color=MUTED, sw=1.2, dash="4,3"))

    nodes = [
        (160, "Хост\n(ноутбук)", "0x10", "майстер: читає, керує", FIELD),
        (350, "Зарядник\n(Charger)", "0x12", "slave: приймає V, I", NEG),
        (540, "Селектор\n(Selector)", "0x14", "перемикає батареї", MUTED),
        (700, "Батарея\n(Battery)", "0x16", "slave: усі дані", POS),
    ]
    for cx, name, addr, role, col in nodes:
        body, w, h = textbox(cx, busy - 78, name, size=13, bold=True, fill="#ffffff", stroke=col, sw=2)
        f.append(body)
        f.append(line(cx, busy - 78 + h / 2, cx, busy, color=col, sw=2))
        f.append(text(cx, busy + 48, "адреса " + addr, size=13, color=col, bold=True))
        f.append(text(cx, busy + 68, role, size=11, color=MUTED))
    # виноска: 0x16 = 0x0B<<1
    f.append(fitbox(W / 2 - 250, H - 58, 500, 40,
                    "Адреса 0x16 — це 8-бітний байт запису: 7-бітна адреса 0x0B, зсунута вліво (0x0B<<1). Читання — 0x17.",
                    size=12, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(IMG, 'sbs-bus-map.svg'), W, H, *f)


# ── 2. Транзакція Read Word: як хост дістає один регістр ─────────────────────
def fig_read_word():
    W, H = 860, 300
    f = [text(W / 2, 30, "Read Word: хост читає регістр Voltage (0x09)", size=16, bold=True)]
    y = 120
    h = 46
    x = 40
    # послідовність байтів на шині
    cells = [
        ("S", 34, MUTED, "старт"),
        ("0x16", 74, POS, "адреса+W"),
        ("0x09", 74, INK, "команда"),
        ("Sr", 40, MUTED, "рестарт"),
        ("0x17", 74, POS, "адреса+R"),
        ("0x24", 74, NEG, "молодший"),
        ("0x1F", 74, NEG, "старший"),
        ("PEC", 60, FIELD, "CRC-8"),
        ("P", 34, MUTED, "стоп"),
    ]
    for label, w, col, sub in cells:
        fill = "#ffffff"
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2))
        f.append(text(x + w / 2, y + h / 2 + 5, label, size=13, color=col, bold=True))
        f.append(text(x + w / 2, y + h + 18, sub, size=10, color=MUTED))
        x += w + 6
    # хто веде лінію
    f.append(text(40, y - 16, "майстер (хост)", size=11, color=INK, anchor="start"))
    f.append(text(x, y - 16, "← веде батарея", size=11, color=MUTED, anchor="end"))
    # підсумок значення
    f.append(fitbox(W / 2 - 260, H - 70, 520, 44,
                    "Два байти приходять молодшим уперед: 0x1F24 = 7972 → напруга 7972 мВ ≈ 7.97 В.",
                    size=13, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(IMG, 'sbs-read-word.svg'), W, H, *f)


# ── 3. SMBus проти I²C: три відмінності, що ламають наївний драйвер ───────────
def fig_smbus_vs_i2c():
    W, H = 820, 340
    f = [text(W / 2, 30, "SMBus — це I²C з трьома жорсткими правилами", size=16, bold=True)]
    cols = [
        ("Таймаут", "I²C: годинник можна\nтримати низько скільки\nзавгодно (clock stretch).",
         "SMBus: тримав SCL\nнизько > 35 мс —\nусі скидають шину.", POS),
        ("Мінімум такту", "I²C: можна й 0 Гц —\nстій між бітами.",
         "SMBus: не повільніше\n10 кГц, інакше\nспрацює таймаут.", NEG),
        ("Пороги рівнів", "I²C: пороги — частка\nвід живлення чипа.",
         "SMBus: пороги фіксовані\n(0.8 В / 2.1 В) —\nрівні збігаються.", FIELD),
    ]
    cw = 250
    gap = 20
    x = (W - (cw * 3 + gap * 2)) / 2
    top = 70
    for title_, a, b, col in cols:
        f.append(rect(x, top, cw, 220, fill="#ffffff", stroke=col, sw=2))
        f.append(text(x + cw / 2, top + 26, title_, size=14, color=col, bold=True))
        f.append(mtext(x + cw / 2, top + 60, a, size=11.5, color=MUTED))
        f.append(line(x + 16, top + 132, x + cw - 16, top + 132, color=col, sw=1, dash="4,3"))
        f.append(mtext(x + cw / 2, top + 156, b, size=11.5, color=INK))
        x += cw + gap
    render(os.path.join(IMG, 'smbus-vs-i2c.svg'), W, H, *f)


# ── 4. Хроніка стандарту: від двох фірм до консорціуму (для hist-вставки) ─────
def fig_sbs_timeline():
    W, H = 860, 500
    f = [text(W / 2, 30, "Від двох фірм до консорціуму: як народився стандарт", size=16, bold=True)]
    # горизонтальна вісь часу
    axy = 175
    x0, x1 = 60, W - 60
    f.append(line(x0, axy, x1, axy, color=INK, sw=2.5))
    f.append(arrow(x1 - 2, axy, x1 + 18, axy, color=INK, sw=2.5))
    f.append(text(x1 + 22, axy + 4, "час", size=11, color=MUTED, anchor="start"))

    # (частка_вздовж_осі, рік, коротко, докладно_багаторядково, колір, вниз?)
    events = [
        (0.03, "1994", "Задум", "Intel + Duracell:\nбатарея має\nговорити цифрою", MUTED, False),
        (0.24, "1995", "Rev 1.0", "15.02: Smart Battery\nData + SMBus 1.0\n(© Intel, Duracell)", POS, True),
        (0.50, "1996", "Передача", "специфікацію віддано\nгрупі з 10 фірм —\nпромоутерів", FIELD, False),
        (0.68, "1997", "SBS-IF", "утворено форум;\nSMBus увійшов\nдо його специфікацій", NEG, True),
        (0.93, "1998", "Rev 1.1", "11.12: разом зі\nSMBus 1.1 додано\nPEC (CRC-8)", POS, False),
    ]
    for frac, year, short, long_, col, down in events:
        cx = x0 + frac * (x1 - x0)
        f.append(circle(cx, axy, 7, fill="#ffffff", stroke=col, sw=2.5))
        f.append(text(cx, axy - 16 if not down else axy + 26, year, size=14, color=col, bold=True))
        # картка: угору або вниз від осі
        if down:
            body, w, h = textbox(cx, axy + 118, short + "\n" + long_, size=11.5,
                                 fill="#ffffff", stroke=col, sw=1.8, bold=False)
            f.append(line(cx, axy + 8, cx, axy + 118 - h / 2, color=col, sw=1.3, dash="4,3"))
        else:
            body, w, h = textbox(cx, axy - 118, short + "\n" + long_, size=11.5,
                                 fill="#ffffff", stroke=col, sw=1.8, bold=False)
            f.append(line(cx, axy - 8, cx, axy - 118 + h / 2, color=col, sw=1.3, dash="4,3"))
        # виділити перший рядок картки жирним поверх (короткий підпис)
        f.append(body)

    # нижня смуга-висновок
    f.append(fitbox(W / 2 - 330, H - 56, 660, 40,
                    "Одна мета крізь усі версії: щоб будь-який ноутбук читав будь-яку батарею тією самою мовою.",
                    size=13, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(IMG, 'sbs-timeline.svg'), W, H, *f)


# ── 5. Три замки прошивки батареї: чому «розблоковано за замовчуванням» ───────
def fig_seal_ladder():
    W, H = 860, 470
    f = [text(W / 2, 30, "Три замки прошивки і чому вони не спрацювали", size=16, bold=True)]

    # три щаблі-двері зліва направо
    rungs = [
        ("Sealed", "запечатано", "Читай дані.\nПрошивку й калібрування\nчіпати не можна.",
         "стан із коробки", FIELD),
        ("Unsealed", "розпечатано", "Ключ 1 (32 біти).\nВідкрито калібрування,\nчастину налаштувань.",
         "ключ = 0x36720414", NEG),
        ("Full access", "повний доступ", "Ключ 2 (32 біти).\nПеретирай прошивку,\nвимикай перевірки.",
         "ключ = 0xffffffff", POS),
    ]
    cw, gap = 236, 24
    x = (W - (cw * 3 + gap * 2)) / 2
    top = 70
    for i, (name, ua, body, key, col) in enumerate(rungs):
        f.append(rect(x, top, cw, 190, fill="#ffffff", stroke=col, sw=2))
        f.append(text(x + cw / 2, top + 28, name, size=15, color=col, bold=True))
        f.append(text(x + cw / 2, top + 47, ua, size=11, color=MUTED))
        f.append(mtext(x + cw / 2, top + 78, body, size=11.5, color=INK))
        f.append(line(x + 16, top + 150, x + cw - 16, top + 150, color=col, sw=1, dash="4,3"))
        f.append(text(x + cw / 2, top + 172, key, size=12, color=col, bold=True))
        if i < 2:
            ax = x + cw + 2
            f.append(arrow(ax, top + 95, ax + gap - 4, top + 95, color=MUTED, sw=2))
        x += cw + gap

    # нижня смуга: суть провалу
    f.append(fitbox(W / 2 - 360, 300, 720, 46,
                    "Замки були — але обидва ключі лишили заводськими з даташита, однаковими на всіх ноутбуках. "
                    "«Запечатано» без свого ключа = навстіж.",
                    size=13, fill="#fdecea", stroke=POS))

    # ремарка: що це відкриває
    f.append(text(W / 2, 372, "За повним доступом прошивка бреше про заряд, глушить тепловий захист "
                              "і виживає після переінсталяції ОС.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 392, "Двонапрямний цифровий порт до силового вузла — це не лише зручність, а й поверхня атаки.",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(IMG, 'seal-ladder.svg'), W, H, *f)


if __name__ == '__main__':
    fig_bus_map()
    fig_read_word()
    fig_smbus_vs_i2c()
    fig_sbs_timeline()
    fig_seal_ladder()
    print('OK: 5 figures written to', IMG)
