# -*- coding: utf-8 -*-
"""Фігури до теми «Протокол SLIP: кадрування послідовного потоку».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальна палітра кольорів
ENDc  = POS         # 0xC0 (END) — червоне / рубінове (маркер межі)
ESCc  = "#d35400"   # 0xDB (ESC) — помаранчеве (префікс екранування)
ESCDc = "#8e44ad"   # 0xDC / 0xDD — фіолетове (байти підстановки)
DATAc = INK         # звичайні байти даних
CRCc  = FIELD       # зелений / цілість
GREY  = "#7f8c8d"   # лінійне сміття / нейтральне
BOXBG = "#fdfefe"


def _byte_cell(f, x, y, w, h, top_label, val_label, stroke_col, fill_col=BOXBG, val_col=INK):
    """Окремий байт у потоці з підписом поля зверху та hex-значенням усередині."""
    f.append(rect(x, y, w, h, fill=fill_col, stroke=stroke_col, sw=1.6, rx=4))
    if top_label:
        f.append(text(x + w / 2, y - 7, top_label, size=10.5, color=stroke_col, bold=True))
    f.append(text(x + w / 2, y + h / 2 + 5, val_label, size=12.5, color=val_col, bold=True))


# ── 1. Проблема виділення меж у потоці (framing-problem.svg) ────────────────
def fig_framing_problem():
    W, H = 760, 320
    f = [text(W / 2, 24, "Виділення меж пакетів у безперервному потоці UART", size=15, bold=True)]

    # Верхній потік: сирий потік без меж
    f.append(text(40, 60, "1. Сирий потік байтів UART (без меж пакетів):", size=12.5, color=INK, anchor="start", bold=True))
    raw_bytes = ["45", "00", "00", "3C", "1A", "02", "45", "00", "00", "28"]
    x0, y0, w, h, gap = 40, 75, 56, 38, 4
    for i, b in enumerate(raw_bytes):
        _byte_cell(f, x0 + i * (w + gap), y0, w, h, "", "0x" + b, GREY, fill_col="#f5f7fa")

    f.append(line(x0 + 4 * (w + gap) + w / 2, y0 - 10, x0 + 4 * (w + gap) + w / 2, y0 + h + 10, color=POS, sw=1.8, dash="4,3"))
    f.append(text(x0 + 4 * (w + gap) + w / 2, y0 + h + 24, "де закінчується пакет 1 і починається пакет 2?", size=11, color=POS, bold=True))

    # Нижній потік: кадрування SLIP
    y1 = 190
    f.append(text(40, y1 - 15, "2. Потік SLIP з обрамленням маркерами END (0xC0):", size=12.5, color=INK, anchor="start", bold=True))
    slip_stream = [
        ("END", "0xC0", ENDc, "#fdeeed"),
        ("IP Data", "0x45", DATAc, BOXBG),
        ("IP Data", "0x00", DATAc, BOXBG),
        ("IP Data", "0x3C", DATAc, BOXBG),
        ("END", "0xC0", ENDc, "#fdeeed"),
        ("END", "0xC0", ENDc, "#fdeeed"),
        ("IP Data", "0x45", DATAc, BOXBG),
        ("IP Data", "0x28", DATAc, BOXBG),
        ("END", "0xC0", ENDc, "#fdeeed"),
    ]
    for i, (top, val, col, bg) in enumerate(slip_stream):
        _byte_cell(f, x0 + i * (w + gap + 4), y1, w + 4, h, top, val, col, fill_col=bg, val_col=INK)

    # Пояснювальний блок унизу
    f.append(fitbox(40, 260, 680, 46,
                    "Маркер END (0xC0) однозначно позначає завершення поточного пакета. "
                    "Подвійний END на стику скидає завади лінії перед початком наступного кадру.",
                    size=11.5, color=INK, fill=FILL, stroke=GREY, sw=1.2))

    render(os.path.join(IMG, "framing-problem.svg"), W, H, *f)


# ── 2. Механізм байт-стаффінгу (byte-stuffing.svg) ──────────────────────────
def fig_byte_stuffing():
    W, H = 760, 350
    f = [text(W / 2, 24, "Байт-стаффінг SLIP: екранування колізій керуючих символів", size=15, bold=True)]

    # Випадок 1: Байт 0xC0 всередині даних
    y1 = 70
    f.append(text(50, y1, "Випадок 1: Корисні дані містять байт 0xC0 (збіг із маркером END)", size=12, bold=True, anchor="start"))
    _byte_cell(f, 60, y1 + 15, 75, 40, "Дані", "0xC0", ENDc, fill_col="#fdeeed")
    f.append(arrow(150, y1 + 35, 230, y1 + 35, color=INK, sw=1.8))
    f.append(text(190, y1 + 25, "Кодувати", size=10.5, color=MUTED))
    _byte_cell(f, 245, y1 + 15, 70, 40, "ESC", "0xDB", ESCc, fill_col="#fef5e7")
    _byte_cell(f, 325, y1 + 15, 85, 40, "ESC_END", "0xDC", ESCDc, fill_col="#f4ecf7")
    f.append(text(430, y1 + 35, "→ 2 байти в потоці (0xDB 0xDC замість 0xC0)", size=11.5, color=INK, anchor="start"))

    # Випадок 2: Байт 0xDB всередині даних
    y2 = 160
    f.append(text(50, y2, "Випадок 2: Корисні дані містять байт 0xDB (збіг із префіксом ESC)", size=12, bold=True, anchor="start"))
    _byte_cell(f, 60, y2 + 15, 75, 40, "Дані", "0xDB", ESCc, fill_col="#fef5e7")
    f.append(arrow(150, y2 + 35, 230, y2 + 35, color=INK, sw=1.8))
    f.append(text(190, y2 + 25, "Кодувати", size=10.5, color=MUTED))
    _byte_cell(f, 245, y2 + 15, 70, 40, "ESC", "0xDB", ESCc, fill_col="#fef5e7")
    _byte_cell(f, 325, y2 + 15, 85, 40, "ESC_ESC", "0xDD", ESCDc, fill_col="#f4ecf7")
    f.append(text(430, y2 + 35, "→ 2 байти в потоці (0xDB 0xDD замість 0xDB)", size=11.5, color=INK, anchor="start"))

    # Випадок 3: Звичайний байт
    y3 = 250
    f.append(text(50, y3, "Випадок 3: Будь-який інший байт (не 0xC0 і не 0xDB)", size=12, bold=True, anchor="start"))
    _byte_cell(f, 60, y3 + 15, 75, 40, "Дані", "0x45", DATAc, fill_col=BOXBG)
    f.append(arrow(150, y3 + 35, 230, y3 + 35, color=INK, sw=1.8))
    f.append(text(190, y3 + 25, "Без змін", size=10.5, color=MUTED))
    _byte_cell(f, 245, y3 + 15, 75, 40, "Дані", "0x45", DATAc, fill_col=BOXBG)
    f.append(text(340, y3 + 35, "→ 1 байт у потоці без додаткового оверхеду", size=11.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "byte-stuffing.svg"), W, H, *f)


# ── 3. Кінцевий автомат розбору потоку (fsm-decoder.svg) ─────────────────────
def fig_fsm_decoder():
    W, H = 760, 380
    f = [text(W / 2, 24, "Кінцевий автомат (FSM) декодера SLIP", size=15, bold=True)]

    # Стан 1: NORMAL (Очікування даних / збирання пакета)
    cx1, cy1 = 200, 160
    f.append(circle(cx1, cy1, 65, fill="#ebf5fb", stroke=NEG, sw=2.2))
    f.append(text(cx1, cy1 - 10, "STATE_NORMAL", size=12, bold=True, color=NEG))
    f.append(text(cx1, cy1 + 10, "Збирання кадру", size=10.5, color=INK))

    # Стан 2: ESCAPED (Отримано ESC 0xDB)
    cx2, cy2 = 560, 160
    f.append(circle(cx2, cy2, 65, fill="#fef5e7", stroke=ESCc, sw=2.2))
    f.append(text(cx2, cy2 - 10, "STATE_ESCAPED", size=12, bold=True, color=ESCc))
    f.append(text(cx2, cy2 + 10, "Очікування підстановки", size=10.5, color=INK))

    # Перехід: NORMAL -> ESCAPED (прийшов 0xDB)
    f.append(arrow(cx1 + 65, cy1 - 20, cx2 - 65, cy2 - 20, color=ESCc, sw=1.8))
    f.append(text((cx1 + cx2) / 2, cy1 - 32, "байт == 0xDB (ESC)", size=11, color=ESCc, bold=True))

    # Перехід: ESCAPED -> NORMAL (прийшов 0xDC або 0xDD)
    f.append(arrow(cx2 - 65, cy2 + 20, cx1 + 65, cy1 + 20, color=FIELD, sw=1.8))
    f.append(text((cx1 + cx2) / 2, cy1 + 36, "0xDC → додати 0xC0 | 0xDD → додати 0xDB", size=10.5, color=FIELD, bold=True))

    # Петля NORMAL вгору: звичайний байт
    f.append(line(cx1 - 40, cy1 - 50, cx1 - 40, cy1 - 90, color=INK, sw=1.6))
    f.append(line(cx1 - 40, cy1 - 90, cx1 + 40, cy1 - 90, color=INK, sw=1.6))
    f.append(arrow(cx1 + 40, cy1 - 90, cx1 + 40, cy1 - 52, color=INK, sw=1.6))
    f.append(text(cx1, cy1 - 98, "байт != 0xC0, 0xDB → додати в буфер", size=10.5, color=INK))

    # Петля NORMAL вниз: маркер END (0xC0)
    f.append(line(cx1 - 40, cy1 + 50, cx1 - 40, cy1 + 90, color=POS, sw=1.8))
    f.append(line(cx1 - 40, cy1 + 90, cx1 + 40, cy1 + 90, color=POS, sw=1.8))
    f.append(arrow(cx1 + 40, cy1 + 90, cx1 + 40, cy1 + 52, color=POS, sw=1.8))
    f.append(text(cx1, cy1 + 105, "байт == 0xC0 (END) → якщо len > 0: видати пакет", size=10.5, color=POS, bold=True))

    # Нижня плашка: крайові випадки та помилки
    note = ("Крайові випадки: якщо у стані STATE_ESCAPED приходить 0xC0 (порушення послідовності) — "
            "кадр скидається через помилку протоколу. Якщо буфер досягає MTU — надлишок відкидається.")
    f.append(fitbox(40, 318, 680, 48, note, size=11, color=INK, fill=FILL, stroke=GREY, sw=1.2))

    render(os.path.join(IMG, "fsm-decoder.svg"), W, H, *f)


# ── 4. Порівняння оверхеду та роздування (worst-case-bloat.svg) ──────────────
def fig_worst_case_bloat():
    W, H = 760, 360
    f = [text(W / 2, 24, "Оверхед кадрування: типовий випадок проти найгіршого", size=15, bold=True)]

    # Стовпчики порівняння для пакета 1000 байтів
    items = [
        ("SLIP (типовий IP)", 1008, "+0.8% (2x END + ~6x ESC)", FIELD),
        ("SLIP (найгірший: всі 0xC0/0xDB)", 2002, "+100.2% (подвоєння кожного байта)", POS),
        ("COBS (найгірший гарантований)", 1005, "+0.5% (максимум +1 байт на 254)", NEG),
        ("HDLC / PPP (типовий)", 1010, "+1.0% (Flags + Address + Control + CRC)", "#8e44ad"),
    ]

    y0, bar_h, gap = 55, 38, 18
    max_w = 400
    for i, (label, total_bytes, desc, col) in enumerate(items):
        y = y0 + i * (bar_h + gap)
        # Назва
        f.append(text(40, y + 15, label, size=11.5, bold=True, anchor="start", color=INK))
        # Смуга початкового розміру (1000)
        bw_base = (1000 / 2100) * max_w
        f.append(rect(280, y, bw_base, bar_h, fill="#e8eaed", stroke=GREY, sw=1.2, rx=3))
        f.append(text(280 + bw_base / 2, y + 23, "1000 B даних", size=10.5, color=MUTED))

        # Смуга оверхеду
        ov_bytes = total_bytes - 1000
        bw_ov = (ov_bytes / 2100) * max_w
        if bw_ov < 6:
            bw_ov = 6  # мінімальна видимість
        f.append(rect(280 + bw_base, y, bw_ov, bar_h, fill=col, stroke=col, sw=1.2, rx=3))

        # Підпис оверхеду
        f.append(text(280 + bw_base + bw_ov + 10, y + 23, f"{total_bytes} B ({desc})",
                      size=10.5, color=col, bold=True, anchor="start"))

    f.append(fitbox(40, 290, 680, 48,
                    "У найгіршому випадку SLIP подвоює розмір кадру (роздування до 200%), "
                    "тоді як COBS усуває цю залежність, гарантуючи фіксований оверхед ≤ 0.4%.",
                    size=11, color=INK, fill=FILL, stroke=GREY, sw=1.2))

    render(os.path.join(IMG, "worst-case-bloat.svg"), W, H, *f)


# ── 5. Компресія заголовків Van Jacobson CSLIP (cslip-compression.svg) ───────
def fig_cslip_compression():
    W, H = 760, 330
    f = [text(W / 2, 24, "Стиснення заголовків Van Jacobson (CSLIP, RFC 1144)", size=15, bold=True)]

    # Звичайний TCP/IP пакет SLIP
    y1 = 65
    f.append(text(40, y1, "Стандартний пакет SLIP (40 байтів заголовків):", size=12, bold=True, anchor="start"))
    _byte_cell(f, 40, y1 + 15, 70, 38, "SLIP", "END", ENDc, fill_col="#fdeeed")
    _byte_cell(f, 115, y1 + 15, 140, 38, "IP Header", "20 байтів", NEG, fill_col="#ebf5fb")
    _byte_cell(f, 260, y1 + 15, 140, 38, "TCP Header", "20 байтів", "#d35400", fill_col="#fef5e7")
    _byte_cell(f, 405, y1 + 15, 120, 38, "Payload", "Дані (1-100 B)", FIELD, fill_col="#eafaf1")
    _byte_cell(f, 530, y1 + 15, 70, 38, "SLIP", "END", ENDc, fill_col="#fdeeed")
    f.append(text(610, y1 + 38, "Заголовки = 40 байтів", size=11, color=POS, bold=True, anchor="start"))

    # Стиснений пакет CSLIP
    y2 = 175
    f.append(text(40, y2, "Стиснений пакет CSLIP (стиснення до 3–5 байтів):", size=12, bold=True, anchor="start"))
    _byte_cell(f, 40, y2 + 15, 70, 38, "SLIP", "END", ENDc, fill_col="#fdeeed")
    _byte_cell(f, 115, y2 + 15, 95, 38, "Change Mask", "1 байт", FIELD, fill_col="#eafaf1")
    _byte_cell(f, 215, y2 + 15, 80, 38, "Conn ID", "1 байт", FIELD, fill_col="#eafaf1")
    _byte_cell(f, 300, y2 + 15, 110, 38, "Delta Seq/ACK", "1-3 байти", FIELD, fill_col="#eafaf1")
    _byte_cell(f, 415, y2 + 15, 120, 38, "Payload", "Дані (1-100 B)", FIELD, fill_col="#eafaf1")
    _byte_cell(f, 540, y2 + 15, 70, 38, "SLIP", "END", ENDc, fill_col="#fdeeed")
    f.append(text(620, y2 + 38, "Заголовки = 3–5 байтів!", size=11, color=FIELD, bold=True, anchor="start"))

    # Пояснення
    f.append(fitbox(40, 260, 680, 48,
                    "На повільних лініях (9600–19200 бод) CSLIP скорочує затримку інтерактивних сесій (SSH/Telnet) "
                    "у 5–10 разів, передаючи лише дельти полів замість статичних IP/TCP адрес і портів.",
                    size=11, color=INK, fill=FILL, stroke=GREY, sw=1.2))

    render(os.path.join(IMG, "cslip-compression.svg"), W, H, *f)


if __name__ == "__main__":
    fig_framing_problem()
    fig_byte_stuffing()
    fig_fsm_decoder()
    fig_worst_case_bloat()
    fig_cslip_compression()
    print("All figures generated successfully.")
