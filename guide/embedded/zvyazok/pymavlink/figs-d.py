# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ теми «pymavlink» (pymavlink-d.md).
Запуск:  python figs-d.py   → пише SVG у ./img/  (окремі імена від базових).
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CODE_BG = "#1b1f24"
CODE_FG = "#cfe8cf"
AMBER   = "#b08900"


# ── 1. Кадр на дроті: MAVLink 1 проти MAVLink 2 ───────────────────────────────
# Ідея: те, що ховається під .pack() — байти в лінії; порівняти два заголовки.
def fig_wire_frame():
    W, H = 820, 340
    f = [text(W / 2, 26, "Кадр на дроті: що ховає .pack()", size=16, bold=True)]

    def field(x, y, w, label, sub, col, sw=1.6):
        out = rect(x, y, w, 46, fill="#fbfbfb", stroke=col, sw=sw, rx=5)
        out += fitbox(x + 2, y + 4, w - 4, 24, label, size=10, color=col, bold=True,
                      fill="none", stroke="none", sw=0)
        out += text(x + w / 2, y + 40, sub, size=8.5, color=MUTED)
        return out

    # v1
    f.append(text(60, 70, "MAVLink 1  (STX = 0xFE)", size=12, color=NEG, bold=True, anchor="start"))
    x, y = 60, 84
    v1 = [("STX", "1", NEG), ("LEN", "1", INK), ("SEQ", "1", INK),
          ("SYS", "1", INK), ("COMP", "1", INK), ("MSGID", "1", AMBER),
          ("PAYLOAD", "0..255", FIELD), ("CRC", "2", POS)]
    ws = [46, 46, 46, 46, 52, 60, 150, 52]
    for (lab, sub, col), w in zip(v1, ws):
        f.append(field(x, y, w, lab, sub, col))
        x += w + 4
    f.append(text(60, y + 66, "заголовок 6 байтів · MSGID 8-біт (0..255) · кадр 8..263 Б",
                  size=9.5, color=MUTED, anchor="start"))

    # v2
    f.append(text(60, 190, "MAVLink 2  (STX = 0xFD)", size=12, color=FIELD, bold=True, anchor="start"))
    x, y = 60, 204
    v2 = [("STX", "1", FIELD), ("LEN", "1", INK), ("INCOMP", "1", POS),
          ("COMPAT", "1", MUTED), ("SEQ", "1", INK), ("SYS", "1", INK),
          ("COMP", "1", INK), ("MSGID", "3", AMBER), ("PAYLOAD", "0..255", FIELD),
          ("CRC", "2", POS), ("SIG", "0/13", NEG)]
    ws = [40, 40, 54, 54, 40, 40, 46, 54, 130, 44, 50]
    for (lab, sub, col), w in zip(v2, ws):
        f.append(field(x, y, w, lab, sub, col))
        x += w + 3
    f.append(text(60, y + 66, "заголовок 10 Б · MSGID 24-біт (до 16 777 215) · SIG лише коли IFLAG=0x01 · кадр 12..280 Б",
                  size=9.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 10,
                  "той самий payload, але v2 дає 24-бітний ID, прапорці й підпис — і врізає хвостові нулі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "wire-frame.svg"), W, H, *f)


# ── 2. CRC_EXTRA: рукостискання про формат ────────────────────────────────────
# Ідея: контрольна сума домішує байт, похідний від ОПИСУ повідомлення. Збіг
# опису → збіг CRC_EXTRA → кадр прийнято; різні описи → мовчазне відкидання.
def fig_crc_extra():
    W, H = 780, 330
    f = [text(W / 2, 26, "CRC_EXTRA: рукостискання про формат", size=16, bold=True)]

    # відправник
    b, w1, h1 = textbox(160, 96, "XML-опис\nATTITUDE", size=11, color=NEG,
                        fill="#eef2fd", stroke=NEG, sw=1.6, bold=True)
    f.append(b)
    b, _, _ = textbox(160, 176, "CRC_EXTRA = 39", size=11, color=INK,
                     fill="#fbfbfb", stroke=NEG, sw=1.5, bold=True)
    f.append(b)
    f.append(arrow(160, 118, 160, 156, color=NEG, sw=1.8))
    f.append(text(160, 220, "відправник", size=10, color=NEG, italic=True))

    # приймач
    b, _, _ = textbox(620, 96, "XML-опис\nATTITUDE", size=11, color=FIELD,
                     fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True)
    f.append(b)
    b, _, _ = textbox(620, 176, "CRC_EXTRA = 39", size=11, color=INK,
                     fill="#fbfbfb", stroke=FIELD, sw=1.5, bold=True)
    f.append(b)
    f.append(arrow(620, 118, 620, 156, color=FIELD, sw=1.8))
    f.append(text(620, 220, "приймач", size=10, color=FIELD, italic=True))

    # середина — контрольна сума
    b, wc, hc = textbox(390, 176, "CRC-16 над кадром\n+ домішаний CRC_EXTRA", size=10.5,
                       color=INK, fill="#fff8e6", stroke=AMBER, sw=1.8, bold=True)
    f.append(b)
    f.append(arrow(160 + 90, 176, 390 - wc / 2, 176, color=INK, sw=1.6))
    f.append(arrow(620 - 90, 176, 390 + wc / 2, 176, color=INK, sw=1.6))

    f.append(text(390, 250, "39 = 39  →  суми збіглися  →  кадр прийнято",
                  size=11, color=FIELD, bold=True))
    f.append(text(390, 276, "інший опис (додали поле) →  CRC_EXTRA інший →  сума не зійшлась →  мовчки відкинуто",
                  size=9.5, color=POS))
    f.append(text(W / 2, H - 8,
                  "версії описів у двох кінцях мусять збігатися — інакше кадр просто не пройде",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "crc-extra.svg"), W, H, *f)


# ── 3. Розбирач як автомат: байт за байтом ────────────────────────────────────
# Ідея: parse_char годують по одному байту; він переходить станами, а кадр
# віддає лише коли зійшлася CRC. recv_match — обгортка над цим циклом.
def fig_parser_fsm():
    W, H = 800, 300
    f = [text(W / 2, 26, "Розбирач як автомат: байт за байтом", size=16, bold=True)]

    states = [
        ("чекаю\nSTX", NEG),
        ("читаю\nзаголовок", INK),
        ("читаю\npayload", FIELD),
        ("звіряю\nCRC", AMBER),
        ("готовий\nкадр", POS),
    ]
    n = len(states)
    x0, gap, bw = 44, 40, 118
    y = 118
    cxs = []
    for i, (lab, col) in enumerate(states):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        cxs.append(cx)
        fill = "#eef6ef" if col == POS else "#fbfbfb"
        f.append(fitbox(x, y, bw, 58, lab, size=11, color=col, bold=True,
                        fill=fill, stroke=col, sw=1.8, rx=9))
    for i in range(n - 1):
        f.append(arrow(cxs[i] + bw / 2, y + 29, cxs[i + 1] - bw / 2, y + 29, color=INK, sw=1.7))

    # підписи над переходами
    labels = ["є 0xFD", "усі поля", "n байтів", "сума ОК"]
    for i, lab in enumerate(labels):
        f.append(text((cxs[i] + cxs[i + 1]) / 2, y - 6, lab, size=9, color=MUTED))

    # петля «сума не зійшлася → відкинути, знову чекаю STX»
    f.append(text(cxs[3], y + 96, "сума не зійшлась →", size=9.5, color=POS))
    f.append(text(cxs[3], y + 112, "байт викинуто, шукаю STX знову", size=9.5, color=POS))
    f.append(line(cxs[3], y + 58, cxs[3], y + 80, color=POS, sw=1.4, dash="4,3"))
    f.append(arrow(cxs[3], y + 80, cxs[0], y + 80, color=POS, sw=1.4))
    f.append(line(cxs[0], y + 80, cxs[0], y + 58, color=POS, sw=1.4, dash="4,3"))

    f.append(text(cxs[4], y + 92, "recv_match() крутить\nцей цикл і фільтрує\nза type/condition", size=9))
    f.append(text(W / 2, H - 8,
                  "mav.parse_char(byte) веде цей автомат; кадр з'являється лише коли CRC зійшлася",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "parser-fsm.svg"), W, H, *f)


# ── 4. Команда → ACK → повтор: часова діаграма ────────────────────────────────
# Ідея: надійність команди — на плечах відправника: нема ACK → повтор із
# більшим confirmation; приймач ловить дублі за confirmation; IN_PROGRESS.
def fig_command_ack():
    W, H = 800, 350
    f = [text(W / 2, 26, "Команда → ACK → повтор: хто відповідає за надійність", size=15.5, bold=True)]

    lx, rx = 150, 650
    top, bot = 66, 300
    f.append(line(lx, top, lx, bot, color=INK, sw=1.5))
    f.append(line(rx, top, rx, bot, color=INK, sw=1.5))
    f.append(text(lx, top - 10, "відправник (pymavlink)", size=10.5, color=NEG, bold=True))
    f.append(text(rx, top - 10, "апарат (автопілот)", size=10.5, color=FIELD, bold=True))

    def send(y, lab, col, dash=None):
        f.append(arrow(lx + 4, y, rx - 4, y, color=col, sw=1.8))
        f.append(text((lx + rx) / 2, y - 6, lab, size=9.5, color=col))

    def ack(y, lab, col):
        f.append(arrow(rx - 4, y, lx + 4, y, color=col, sw=1.8))
        f.append(text((lx + rx) / 2, y - 6, lab, size=9.5, color=col))

    send(96, "COMMAND_LONG  confirmation=0", NEG)
    f.append(text(lx - 8, 112, "старт таймера", size=8.5, color=MUTED, anchor="end"))
    f.append(text(rx + 8, 112, "(пакет загубився)", size=8.5, color=POS, anchor="start"))

    send(150, "повтор:  confirmation=1", AMBER)
    ack(186, "COMMAND_ACK  IN_PROGRESS  progress=40%", FIELD)
    ack(224, "COMMAND_ACK  IN_PROGRESS  progress=80%", FIELD)
    ack(262, "COMMAND_ACK  ACCEPTED", POS)
    f.append(text(rx + 8, 150, "дубль? той самий\nconfirmation — не роблю\nдвічі", size=8, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "нема ACK за таймаут → повтори з більшим confirmation; приймач за ним відсіює дублі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "command-ack.svg"), W, H, *f)


# ── 5. Один UART, багато споживачів: маршрутизатор ────────────────────────────
# Ідея: серійна лінія до контролера — одна, а їсти потік хочуть кілька програм.
# Розв'язка — мультиплексор (mavlink-router/MAVProxy), що роздає копії по UDP.
def fig_routing():
    W, H = 800, 320
    f = [text(W / 2, 26, "Один UART, багато споживачів", size=16, bold=True)]

    # контролер зліва
    f.append(fitbox(40, 130, 150, 60, "польотний\nконтролер", size=11, color=POS, bold=True,
                    fill="#fbfbfb", stroke=POS, sw=1.8, rx=9))
    # маршрутизатор у центрі
    b, wc, hc = textbox(390, 160, "маршрутизатор\n(mavlink-router /\nMAVProxy)", size=10.5,
                       color=INK, fill="#fff8e6", stroke=AMBER, sw=1.9, bold=True)
    f.append(b)
    f.append(arrow(190, 160, 390 - wc / 2, 160, color=INK, sw=2))
    f.append(text((190 + 390 - wc / 2) / 2, 150, "1 UART", size=9, color=INK, bold=True))

    # споживачі справа
    cons = [("наземна станція\n(UDP :14550)", NEG, 70),
            ("твій pymavlink-код\n(UDP :14551)", FIELD, 160),
            ("логер / MAVROS\n(UDP :14552)", MUTED, 250)]
    for lab, col, y in cons:
        f.append(fitbox(600, y, 170, 54, lab, size=9.5, color=col, bold=True,
                        fill="#fbfbfb", stroke=col, sw=1.6, rx=9))
        f.append(arrow(390 + wc / 2, 160, 600, y + 27, color=col, sw=1.6))

    f.append(text(W / 2, H - 10,
                  "лінія до борту фізично одна; маршрутизатор роздає копії потоку кожному клієнту по UDP",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "routing.svg"), W, H, *f)


# ── 6. Бюджет швидкостей: чим заповнений канал ────────────────────────────────
# Ідея (math-вставка): корисна місткість лінії — смуга; кожен потік з'їдає
# «розмір кадру × частота», причому кадр = payload + 12 Б службового оверхеду.
# Показати наочно: здоровий план тримає телеметрію під половиною каналу,
# лишаючи решту на команди; а на кожному кадрі оверхед — окремим кольором.
def fig_rate_budget():
    W, H = 820, 360
    f = [text(W / 2, 26, "Бюджет швидкостей: чим заповнений канал 4000 Б/с", size=15.5, bold=True)]

    C = 4000.0                       # корисна місткість лінії, Б/с
    x0, x1 = 70, 750                 # межі шкали каналу
    scale = (x1 - x0) / C            # px на 1 Б/с
    ytop, bh = 84, 44                # верх смуги й висота

    # три потоки здорового плану: (назва, payload, оверхед, частота, колір)
    streams = [
        ("ATTITUDE @25 Гц",            28, 12, 25, FIELD),
        ("GLOBAL_POSITION_INT @4 Гц",  28, 12,  4, NEG),
        ("HEARTBEAT @1 Гц",             9, 12,  1, AMBER),
    ]

    # рамка всього каналу
    f.append(rect(x0, ytop, x1 - x0, bh, fill="#fbfbfb", stroke=INK, sw=1.6, rx=5))
    f.append(text(x0, ytop - 10, "телеметрія", size=10.5, color=INK, bold=True, anchor="start"))

    # укладаємо потоки зліва; кожен — payload-частина + overhead-частина
    x = x0
    total = 0.0
    for name, P, ovh, hz, col in streams:
        r_pl = P * hz * scale        # ширина корисної частини
        r_ov = ovh * hz * scale      # ширина службової частини
        f.append(rect(x, ytop, r_pl, bh, fill=col, stroke="none", sw=0, rx=0))
        f.append(rect(x + r_pl, ytop, r_ov, bh, fill="#c9ccd1", stroke="none", sw=0, rx=0))
        total += (P + ovh) * hz
        x += r_pl + r_ov

    # межа зайнятого / запас
    f.append(line(x, ytop - 4, x, ytop + bh + 4, color=INK, sw=1.8))
    f.append(text((x + x1) / 2, ytop + bh / 2 + 4, "запас на команди", size=10, color=MUTED))
    f.append(text((x + x1) / 2, ytop + bh / 2 + 20, "й службу", size=10, color=MUTED))

    load = total / C * 100
    f.append(text(x1, ytop - 10,
                  "зайнято %d Б/с  (%.0f%%)" % (int(total), load),
                  size=10.5, color=INK, bold=True, anchor="end"))

    # легенда: корисне vs службове
    ly = ytop + bh + 40
    f.append(rect(x0, ly, 22, 14, fill=FIELD, stroke="none", sw=0, rx=2))
    f.append(text(x0 + 30, ly + 12, "корисний payload", size=10, color=INK, anchor="start"))
    f.append(rect(x0 + 200, ly, 22, 14, fill="#c9ccd1", stroke="none", sw=0, rx=2))
    f.append(text(x0 + 230, ly + 12, "службовий оверхед (12 Б/кадр)", size=10, color=INK, anchor="start"))

    # маленька панель: розклад по потоках
    px, py = x0, ly + 40
    rows = [
        "ATTITUDE:             40 Б × 25 = 1000 Б/с   (28 корисних + 12 служб.)",
        "GLOBAL_POSITION_INT:  40 Б ×  4 =  160 Б/с",
        "HEARTBEAT:            21 Б ×  1 =   21 Б/с   (9 корисних + 12 служб. — оверхед > даних!)",
        "разом 1181 Б/с ≈ 30% каналу → 70% лишається на команди, повтори, службу",
    ]
    f.append(rect(px, py, x1 - x0, 96, fill=CODE_BG, stroke="none", sw=0, rx=6))
    for i, r in enumerate(rows):
        col = CODE_FG if i < 3 else "#ffd479"
        f.append(text(px + 14, py + 22 + i * 21, r, size=10.5, color=col,
                      anchor="start"))

    f.append(text(W / 2, H - 8,
                  "кожен потік їсть «розмір кадру × частота»; сірим — службовий оверхед, що на дрібних кадрах більший за дані",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "rate-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wire_frame()
    fig_crc_extra()
    fig_parser_fsm()
    fig_command_ack()
    fig_routing()
    fig_rate_budget()
    print("OK: 6 detailed figures ->", IMG)
