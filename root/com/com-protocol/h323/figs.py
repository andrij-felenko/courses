# -*- coding: utf-8 -*-
"""Фігури до теми «H.323: телефонна сигналізація ITU-T поверх пакетних мереж»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eefaf1"


def box(cx, cy, s, size=13, fill=FILL, bold=False):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Один виклик — три окремі канали сигналізації плюс медіа повз воротаря.
# ─────────────────────────────────────────────────────────────────────────────
def fig_channels():
    W, H = 1060, 620
    f = []

    f.append(rect(30, 150, 1000, 440, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=12))
    f.append(text(52, 180, "Зона одного воротаря", size=13, color=MUTED,
                  anchor="start", bold=True))

    gk, gkw, gkh = box(530, 68,
                       "Воротар (gatekeeper): хто зареєстрований у зоні,\n"
                       "скільки смуги вже роздано, чи можна ще один виклик",
                       size=13, fill=WARM)
    f.append(gk)

    f.append(fitbox(70, 250, 170, 250, "Термінал A", size=15, fill="#ffffff", bold=True))
    f.append(fitbox(820, 250, 170, 250, "Термінал B", size=15, fill="#ffffff", bold=True))

    # RAS — до воротаря, окремим протоколом і окремим транспортом
    f.append(arrow(160, 244, 480, 68 + gkh + 6, color=NEG))
    f.append(arrow(905, 244, 580, 68 + gkh + 6, color=NEG))
    f.append(text(250, 152, "RAS · UDP 1719", size=12, color=NEG, anchor="start"))
    f.append(text(810, 152, "RAS · UDP 1719", size=12, color=NEG, anchor="end"))

    lanes = [
        (300, "H.225.0 — сигналізація виклику, повідомлення Q.931", "TCP, порт 1720", INK),
        (390, "H.245 — можливості сторін і відкриття логічних каналів",
         "TCP, порт домовляють у Connect", INK),
        (480, "RTP і RTCP — власне звук і відео",
         "UDP, пари портів, кожен напрям окремо", FIELD),
    ]
    for y, top, bottom, color in lanes:
        sw = 2.6 if color == FIELD else 1.8
        f.append(arrow(530, y, 248, y, color=color, sw=sw))
        f.append(arrow(530, y, 812, y, color=color, sw=sw))
        f.append(text(530, y - 14, top, size=13, color=color, bold=(color == FIELD)))
        f.append(text(530, y + 26, bottom, size=11, color=MUTED))

    f.append(text(530, 556, "воротар медіа не бачить: потік іде найкоротшим шляхом",
                  size=12, color=FIELD, italic=True))

    render(os.path.join(OUT, 'three-channels.svg'), W, H, *f,
           title="Три канали сигналізації H.323 і медіа повз воротаря")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Скільки обігів мережею коштує з'єднання: повна процедура і Fast Connect.
# ─────────────────────────────────────────────────────────────────────────────
def _ladder(f, x_left, x_right, y0, step, rows):
    """Малює драбину повідомлень між двома вертикалями. rows: (напрям, підпис, колір)."""
    y = y0
    for direction, label, color in rows:
        if direction == 0:                       # ремарка без стрілки
            f.append(text((x_left + x_right) / 2.0, y, label, size=11,
                          color=MUTED, italic=True))
        elif direction == 2:                     # потік в обидва боки
            mid = (x_left + x_right) / 2.0
            f.append(arrow(mid, y, x_left + 4, y, color=color, sw=2.6))
            f.append(arrow(mid, y, x_right - 4, y, color=color, sw=2.6))
            f.append(text(mid, y - 13, label, size=12, color=color, bold=True))
        else:
            a, b = (x_left, x_right) if direction > 0 else (x_right, x_left)
            f.append(arrow(a, y, b, y, color=color))
            f.append(text((x_left + x_right) / 2.0, y - 13, label, size=11, color=color))
        y += step
    return y


def fig_setup_cost():
    W, H = 1100, 810
    f = []

    # ── ліва панель: повна процедура ─────────────────────────────────────
    f.append(rect(30, 50, 520, 720, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=12))
    f.append(text(52, 82, "Повна процедура: H.225.0, потім H.245", size=14,
                  color=INK, anchor="start", bold=True))

    xa, xb = 145, 440
    f.append(box(xa, 122, "Термінал A")[0])
    f.append(box(xb, 122, "Термінал B")[0])
    f.append(line(xa, 146, xa, 726, color=MUTED, dash="5,5"))
    f.append(line(xb, 146, xb, 726, color=MUTED, dash="5,5"))

    rows_full = [
        (+1, "TCP-з'єднання на порт 1720", INK),
        (+1, "Setup", INK),
        (-1, "Call Proceeding", INK),
        (-1, "Alerting — у неї дзвонить", INK),
        (-1, "Connect + адреса для H.245", INK),
        (+1, "друге TCP-з'єднання, для H.245", POS),
        (+1, "TerminalCapabilitySet", INK),
        (-1, "TerminalCapabilitySet", INK),
        (+1, "MasterSlaveDetermination", INK),
        (-1, "MasterSlaveDeterminationAck", INK),
        (+1, "OpenLogicalChannel", INK),
        (-1, "OpenLogicalChannelAck", INK),
        (0, "…і те саме для зворотного каналу", MUTED),
        (2, "RTP", FIELD),
    ]
    y_end = _ladder(f, xa, xb, 186, 38, rows_full)
    f.append(box(290, y_end + 14, "близько шести обігів мережею\nдо першого пакета звуку",
                 size=12, fill=WARM)[0])

    # ── права панель: Fast Connect ───────────────────────────────────────
    f.append(rect(580, 50, 490, 400, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=12))
    f.append(text(602, 82, "Fast Connect: канали — вже в Setup", size=14,
                  color=INK, anchor="start", bold=True))

    xc, xd = 690, 960
    f.append(box(xc, 122, "Термінал A")[0])
    f.append(box(xd, 122, "Термінал B")[0])
    f.append(line(xc, 146, xc, 406, color=MUTED, dash="5,5"))
    f.append(line(xd, 146, xd, 406, color=MUTED, dash="5,5"))

    rows_fast = [
        (+1, "TCP-з'єднання на порт 1720", INK),
        (+1, "Setup + fastStart: пропозиція", INK),
        (-1, "Alerting", INK),
        (-1, "Connect + fastStart: вибір", INK),
        (2, "RTP", FIELD),
    ]
    y_fast = _ladder(f, xc, xd, 186, 42, rows_fast)
    f.append(box(825, y_fast + 12, "близько двох обігів", size=12, fill=COOL)[0])

    f.append(box(825, 560,
                 "H.245-тунелювання прибирає й друге з'єднання:\n"
                 "повідомлення H.245 їдуть усередині\n"
                 "того самого повідомлення Q.931",
                 size=12, fill=SOFT)[0])

    render(os.path.join(OUT, 'setup-cost.svg'), W, H, *f,
           title="Вартість з'єднання в обігах мережею: повна процедура і Fast Connect")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Дві доріжки стандартизації: ITU-T і IETF, 1995–2005 (вставка hist).
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 1180, 620
    f = []

    y_axis = 310
    x0, x1 = 90, 1110
    y0, y1 = 1995.0, 2006.0

    def X(year):
        return x0 + (year - y0) * (x1 - x0) / (y1 - y0)

    f.append(line(x0, y_axis, x1, y_axis, color=MUTED, sw=2))

    for yr in (1995, 1996, 1998, 1999, 2000, 2002, 2005):
        x = X(yr)
        f.append(line(x, y_axis - 8, x, y_axis + 8, color=MUTED, sw=1.6))
        f.append(text(x, y_axis + 30, str(yr), size=13, color=MUTED, bold=True))

    f.append(text(x0, y_axis - 250, "ITU-T · оператори, виробники АТС",
                  size=14, color=INK, anchor="start", bold=True))
    f.append(text(x0, y_axis + 240, "IETF · спільнота інтернету",
                  size=14, color=INK, anchor="start", bold=True))

    def event(year, dy, s, fill):
        x = X(year)
        body, hw, hh = box(x, y_axis + dy, s, size=12, fill=fill)
        edge = y_axis + dy + (hh if dy < 0 else -hh)
        f.append(line(x, y_axis, x, edge, color=MUTED, sw=1.2, dash="4,4"))
        f.append(body)

    event(1996, -80, "листопад 1996\nH.323 версія 1", WARM)
    event(1998, -190, "січень 1998\nверсія 2: Fast Connect", WARM)
    event(2000, -80, "листопад 2000\nверсія 4", WARM)

    event(1996, 80, "1996\nперші чернетки SIP\nу групі MMUSIC", COOL)
    event(1999, 185, "березень 1999\nRFC 2543", COOL)
    event(2000, 80, "листопад 2000\n3GPP бере SIP\nдля IMS", COOL)
    event(2002, 185, "червень 2002\nRFC 3261 + RFC 3264", COOL)
    event(2005, 80, "липень 2005\nRFC 4123: як\nстикувати два світи", SOFT)

    render(os.path.join(OUT, 'timeline-h323-sip.svg'), W, H, *f,
           title="Дві доріжки стандартизації сигналізації: ITU-T і IETF")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Байти одного повідомлення сигналізації на TCP 1720 (вставка api).
# ─────────────────────────────────────────────────────────────────────────────
def fig_wire_layout():
    W, H = 1120, 500
    f = []

    X0, X1 = 210, 1050
    HS = 54

    def strip(top, cells, height=HS):
        x = X0
        for w, s, fill in cells:
            f.append(fitbox(x, top, w, height, s, size=13, fill=fill))
            x += w
        return x

    def label(top, s, height=HS):
        f.append(text(195, top + height / 2.0 + 5, s, size=12,
                      color=MUTED, anchor="end", bold=True))

    def expand(top, x_from, next_top):
        """Пунктир від «тіла» смуги до повної ширини наступної смуги."""
        y = top + HS
        f.append(line(x_from, y, X0, next_top, color=MUTED, sw=1.1, dash="4,4"))
        f.append(line(X1, y, X1, next_top, color=MUTED, sw=1.1, dash="4,4"))

    label(90, "кадр TPKT")
    strip(90, [(70, "03", SOFT), (70, "00", SOFT),
               (160, "довжина, 2 байти", SOFT),
               (540, "тіло — повідомлення Q.931", "#ffffff")])
    expand(90, 510, 190)

    label(190, "заголовок Q.931")
    strip(190, [(70, "08", WARM), (90, "довж. CRV", WARM), (70, "CRV", WARM),
                (140, "тип 05 = Setup", WARM),
                (470, "інформаційні елементи", "#ffffff")])
    expand(190, 580, 290)

    label(290, "елементи Q.931")
    strip(290, [(160, "04 bearer capability", COOL),
                (160, "6C calling party number", COOL),
                (160, "70 called party number", COOL),
                (360, "7E user-user", "#ffffff")])
    expand(290, 690, 390)

    label(390, "тіло H.225.0", height=70)
    f.append(fitbox(X0, 390, X1 - X0, 70,
                    "H323-UserInformation → h323-uu-pdu → h323-message-body = Setup-UUIE\n"
                    "стиснуто за правилами PER: без імен полів і без роздільників",
                    size=13, fill=SOFT))

    render(os.path.join(OUT, 'wire-layout.svg'), W, H, *f,
           title="Шари одного повідомлення сигналізації H.225.0 на TCP 1720")


if __name__ == '__main__':
    fig_channels()
    fig_setup_cost()
    fig_timeline()
    fig_wire_layout()
    print("ok")
