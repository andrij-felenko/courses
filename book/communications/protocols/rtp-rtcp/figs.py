# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AUD = "#b08900"   # аудіопотік — тепле
VID = "#2457d6"   # відеопотік — холодне


# ── rtp-header: розкладка дванадцяти байтів заголовка ─────────────────────────
# Ідея: кожне поле заголовка — матеріальний слід одного питання, на яке приймач
# інакше не має відповіді. Тому поруч із бітовою розкладкою стоїть питання.

def fig_header():
    W, H = 820, 372
    x0, x1 = 60, 760
    bit = (x1 - x0) / 32.0
    rowh = 44
    p = []

    # бітова лінійка згори
    for b in (0, 8, 16, 24, 31):
        p.append(text(x0 + b * bit, 52, str(b), size=10, color=MUTED))

    def cell(y, bstart, bwidth, label, size=12, pad=4, fill=FILL, bold=False):
        return fitbox(x0 + bstart * bit, y, bwidth * bit, rowh, label,
                      size=size, pad=pad, fill=fill, bold=bold)

    y = 66
    p.append(cell(y, 0, 2, "V", pad=2))
    p.append(cell(y, 2, 1, "P", pad=1))
    p.append(cell(y, 3, 1, "X", pad=1))
    p.append(cell(y, 4, 4, "CC", pad=2))
    p.append(cell(y, 8, 1, "M", pad=1, fill="#fdecea"))
    p.append(cell(y, 9, 7, "PT", pad=2, fill="#fdecea"))
    p.append(cell(y, 16, 16, "номер пакета (seq)", fill="#eaf0fd", bold=True))

    y += rowh + 6
    p.append(cell(y, 0, 32, "мітка часу (timestamp)", fill="#eaf0fd", bold=True))

    y += rowh + 6
    p.append(cell(y, 0, 32, "SSRC — хто джерело потоку", fill="#eaf6ee", bold=True))

    y += rowh + 6
    p.append(fitbox(x0, y, x1 - x0, rowh - 8,
                    "далі, якщо CC > 0: CSRC × CC     потім — саме медіа",
                    size=12, fill=BG, stroke=MUTED, sw=1.2))

    # пояснення полів — окремим стовпчиком під розкладкою
    lines = [
        "seq — росте на одиницю з кожним пакетом: відновити порядок, побачити діру",
        "timestamp — момент у годиннику медіа: КОЛИ показувати, а не коли прийшло",
        "SSRC — випадковий номер потоку: аудіо й відео одного джерела мають різні",
        "PT — тип навантаження: який кодек і яка частота годинника міток",
        "M — маркер: у відео означає останній пакет кадру",
    ]
    ty = y + rowh + 18
    for ln in lines:
        p.append(text(x0, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    render(os.path.join(OUT, "rtp-header.svg"), W, H, *p)


# ── frame-packets: дві осі — номер і час — незалежні одна від одної ───────────
# Ідея: один кадр даємо кількома пакетами з ОДНАКОВОЮ міткою часу; номер біжить
# по пакетах, мітка стоїть на місці й стрибає лише на межі кадру.

def fig_frame_packets():
    W, H = 900, 330
    p = []
    pw, ph = 148, 84
    ytop = 108

    p.append(text(50, 76, "кадр N — три пакети", size=13, color=INK,
                  anchor="start", bold=True))
    p.append(text(586, 76, "кадр N+1", size=13, color=INK, anchor="start", bold=True))

    g1 = [("seq 1000", "ts 7 200 000", "M = 0"),
          ("seq 1001", "ts 7 200 000", "M = 0"),
          ("seq 1002", "ts 7 200 000", "M = 1")]
    for i, (a, b, c) in enumerate(g1):
        x = 50 + i * (pw + 14)
        fill = "#eaf0fd" if c == "M = 0" else "#fdecea"
        p.append(fitbox(x, ytop, pw, ph, "%s\n%s\n%s" % (a, b, c), size=12, fill=fill))

    g2 = [("seq 1003", "ts 7 203 000", "M = 0"),
          ("seq 1004", "ts 7 203 000", "M = 1")]
    for i, (a, b, c) in enumerate(g2):
        x = 586 + i * (pw + 14)
        fill = "#eaf0fd" if c == "M = 0" else "#fdecea"
        p.append(fitbox(x, ytop, pw, ph, "%s\n%s\n%s" % (a, b, c), size=12, fill=fill))

    lines = [
        "усі пакети одного кадру несуть ту саму мітку часу — це один момент показу",
        "номер росте на кожному пакеті: за ним ловлять переставляння й діри",
        "M = 1 на останньому пакеті кадру: декодер знає, що кадр зібрано повністю",
        "наступний кадр: +3000 тіків 90-кілогерцового годинника — рівно 1/30 секунди",
    ]
    ty = ytop + ph + 30
    for ln in lines:
        p.append(text(50, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    render(os.path.join(OUT, "frame-packets.svg"), W, H, *p)


# ── rtcp-loop: два боки й три потоки між ними ────────────────────────────────
# Ідея: сам RTP — односторонній; знання про те, ЩО дійшло, з'являється лише
# завдяки зустрічним звітам RTCP.

def fig_rtcp_loop():
    W, H = 880, 470
    p = []
    bx, by, bw, bh = 40, 92, 190, 268
    p.append(fitbox(bx, by, bw, bh, "джерело\n(відправник)", size=14,
                    fill="#eaf6ee", bold=True))
    p.append(fitbox(W - bx - bw, by, bw, bh, "приймач", size=14,
                    fill="#eaf6ee", bold=True))

    xl, xr = bx + bw + 16, W - bx - bw - 16

    # RTP — уперед
    p.append(text((xl + xr) / 2, 138, "RTP: пакети медіа — seq, timestamp, PT, SSRC",
                  size=12, color=INK))
    p.append(arrow(xl, 158, xr, 158, color=FIELD, sw=2.6))

    # RR — назад
    p.append(arrow(xr, 236, xl, 236, color=NEG, sw=2.2))
    p.append(text((xl + xr) / 2, 260, "RTCP RR: частка втрат, джитер, LSR і DLSR",
                  size=12, color=NEG))

    # SR — уперед
    p.append(arrow(xl, 316, xr, 316, color=POS, sw=2.2))
    p.append(text((xl + xr) / 2, 340, "RTCP SR: скільки надіслано + пара «час NTP ↔ мітка RTP»",
                  size=12, color=POS))

    lines = [
        "RR каже відправникові те, чого той не бачить сам: скільки пакетів дійшло,",
        "наскільки нерівно вони приходили і скільки триває оберт туди-назад.",
        "SR дає приймачеві єдиний місток між годинником медіа й справжнім часом.",
    ]
    ty = by + bh + 34
    for ln in lines:
        p.append(text(bx, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    render(os.path.join(OUT, "rtcp-loop.svg"), W, H, *p)


# ── lip-sync: два медіа-годинники зводяться до одного справжнього часу ───────
# Ідея: мітки RTP різних потоків непорівнянні між собою; спільною одиницею їх
# робить лише пара NTP↔RTP зі звіту відправника.

def fig_lip_sync():
    W, H = 900, 432
    p = []
    ax0, ax1 = 40, 840

    def axis(y, color, caption, capcolor):
        out = [text(ax0, y - 32, caption, size=12, color=capcolor,
                    anchor="start", bold=True),
               line(ax0, y, ax1, y, color=color, sw=2.0)]
        for k in range(9):
            x = ax0 + k * (ax1 - ax0) / 8.0
            out.append(line(x, y - 5, x, y + 5, color=color, sw=1.2))
        return out

    ya, yv, yn = 110, 220, 330
    p += axis(ya, AUD, "аудіо · SSRC 0x4F2A · годинник 48 000 Гц", AUD)
    p += axis(yv, VID, "відео · SSRC 0x91C3 · годинник 90 000 Гц", VID)
    p += axis(yn, INK, "справжній час (NTP), спільний для обох", INK)

    xa, xv = 400, 560
    p.append(circle(xa, ya, 7, fill=AUD, stroke=AUD))
    p.append(text(xa, ya - 14, "SR: ts 1 248 500", size=12, color=AUD))
    p.append(circle(xv, yv, 7, fill=VID, stroke=VID))
    p.append(text(xv, yv - 14, "SR: ts 55 090 000", size=12, color=VID))

    p.append(line(xa, ya + 8, xa, yn - 8, color=AUD, sw=1.4, dash="5,5"))
    p.append(line(xv, yv + 8, xv, yn - 8, color=VID, sw=1.4, dash="5,5"))
    p.append(circle(xa, yn, 6, fill=AUD, stroke=INK, sw=1.0))
    p.append(circle(xv, yn, 6, fill=VID, stroke=INK, sw=1.0))
    p.append(text(xa, yn + 26, "12:00:03.400", size=12, color=AUD))
    p.append(text(xv, yn + 26, "12:00:03.500", size=12, color=VID))

    lines = [
        "Бази міток обрано випадково, тож 1 248 500 і 55 090 000 самі по собі непорівнянні.",
        "Кожен звіт відправника прибиває одну точку своєї осі до спільного часу —",
        "і тільки після цього приймач знає, який зразок звуку йде з яким кадром.",
    ]
    ty = 384
    for ln in lines:
        p.append(text(ax0, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    render(os.path.join(OUT, "lip-sync.svg"), W, H, *p)


# ── rtp-lineage: родовід протоколу від інструментів до стандарту ─────────────
# Ідея: RTP не вигадали за столом — його спочатку написали двічі, у vat і nv,
# а комітет лише зафіксував те, що вже працювало на дроті.

def fig_lineage():
    W, H = 1060, 440
    axy = 250
    TOOL = "#eef7ee"
    RFC  = "#eaf0fd"
    IDEA = "#fdf3e0"
    p = []

    p.append(text(24, 36, "порядок подій — зліва направо; вісь не в масштабі часу",
                  size=12, color=MUTED, anchor="start"))

    items = [
        (["1990", "ALF: кадрує застосунок", "(Clark, Tennenhouse)"], IDEA),
        (["1991", "vat на DARTnet", "(McCanne, Jacobson, LBL)"], TOOL),
        (["березень 1992", "перший аудіокаст IETF", "Сан-Дієго, ~20 майданчиків"], TOOL),
        (["листопад 1992", "nv на IETF", "(Ron Frederick, Xerox PARC)"], TOOL),
        (["15 грудня 1992", "перша чернетка AVT", "(Schulzrinne, Casner)"], RFC),
        (["січень 1996", "RFC 1889 + профіль 1890", "версія 2 на дроті"], RFC),
        (["липень 2003", "RFC 3550 — STD 64", "ті самі дванадцять байтів"], RFC),
    ]

    x0, x1 = 140, 930
    step = (x1 - x0) / (len(items) - 1.0)
    p.append(line(60, axy, 1000, axy, color=LINE, sw=2))

    for i, (lines, fill) in enumerate(items):
        cx = x0 + i * step
        up = (i % 2 == 0)
        cy = 150 if up else 350
        body, bw, bh = textbox(cx, cy, lines, size=12, pad=10, fill=fill, min_w=218)
        edge = cy + bh / 2 if up else cy - bh / 2
        p.append(line(cx, edge, cx, axy - (6 if up else -6), color=MUTED, sw=1.2, dash="4,4"))
        p.append(body)
        p.append(circle(cx, axy, 6, fill=fill, stroke=INK, sw=1.4))

    render(os.path.join(OUT, "rtp-lineage.svg"), W, H, *p)


# ── depack-pipeline: п'ять сходинок приймача й що кожна відсіює ──────────────
# Ідея: приймач — не «розбір заголовка», а конвеєр рішень; на кожній сходинці
# щось відсіюється, і саме перелік відсіяного пояснює, навіщо сходинка потрібна.

def fig_depack_pipeline():
    W, H = 940, 452
    p = []
    bx, bw, bh = 30, 214, 62
    tx = 274

    stages = [
        ("1 · розбір заголовка",
         "12 байтів із мережевого порядку: seq, ts, PT, M, SSRC",
         "відсіюємо: не другу версію й обрізані датаграми"),
        ("2 · розгортання номера",
         "16 біт → монотонні 64: кола переповнення рахуємо самі",
         "відсіюємо: дублікат і пакет, що відстав більше за вікно"),
        ("3 · вікно пересортування",
         "кільце на N слотів; віддаємо суцільний ряд від голови",
         "здаємось на дірі: тисне вікно або вийшов бюджет часу"),
        ("4 · збирання кадру",
         "усі пакети зі спільною міткою часу — до маркерного включно",
         "діра всередині кадру → кадр іде позначений як пошкоджений"),
        ("5 · віддача декодерові",
         "кадр, мітка часу й прапорець цілості — далі декодер",
         "коли саме показувати — вирішує вже буфер джитера"),
    ]

    y = 40
    for i, (name, what, drop) in enumerate(stages):
        p.append(fitbox(bx, y, bw, bh, name, size=13, fill="#eaf0fd", bold=True))
        p.append(text(tx, y + 26, what, size=12, color=INK, anchor="start"))
        p.append(text(tx, y + 47, drop, size=12, color=MUTED, anchor="start"))
        if i + 1 < len(stages):
            p.append(arrow(bx + bw / 2, y + bh + 2, bx + bw / 2, y + bh + 14,
                           color=MUTED, sw=1.6))
        y += 78

    render(os.path.join(OUT, "depack-pipeline.svg"), W, H, *p)


# ── reorder-window: кільце пересортування в мить застрягання на дірі ─────────
# Ідея: черга не «сортує», а тримає голову; уся її поведінка зводиться до
# одного питання — коли перестати чекати на порожній слот.

def fig_reorder_window():
    W, H = 920, 400
    p = []
    x0, y0, cw, ch = 70, 104, 70, 58

    p.append(text(46, 42,
                  "Вікно пересортування: кільце слотів, індекс = розгорнутий номер за модулем N",
                  size=13, color=INK, anchor="start", bold=True))

    got = {4183, 4184, 4186}
    for k in range(10):
        ext = 4182 + k
        if k == 0:
            fill = "#fdecea"
        elif ext in got:
            fill = "#eaf0fd"
        else:
            fill = BG
        p.append(fitbox(x0 + k * cw, y0, cw, ch, str(ext),
                        size=12, fill=fill, stroke=MUTED, sw=1.2))

    xh = x0 + cw / 2
    xt = x0 + 4 * cw + cw / 2
    p.append(arrow(xh, y0 + ch + 34, xh, y0 + ch + 8, color=POS, sw=2.0))
    p.append(arrow(xt, y0 + ch + 34, xt, y0 + ch + 8, color=NEG, sw=2.0))
    p.append(text(xh, y0 + ch + 56, "голова черги", size=12, color=POS))
    p.append(text(xh, y0 + ch + 74, "стоїть на дірі", size=12, color=POS))
    p.append(text(xt, y0 + ch + 56, "найдалі отриманий", size=12, color=NEG))
    p.append(text(xt, y0 + ch + 74, "випередив голову на 4", size=12, color=NEG))

    lines = [
        "Синє — пакет уже в кільці й чекає; біле — ще не прийшов; червоне — на ньому стоїть голова.",
        "Поки голова стоїть, віддавати нічого не можна: 4183 без 4182 — це переставлений порядок.",
        "Здаємось і оголошуємо втрату за одним із двох порогів: найдалі отриманий випередив голову",
        "більше ніж на глибину вікна, або голова простояла довше за відведений бюджет часу.",
        "Пакет із номером ПОЗАДУ голови викидаємо мовчки: його місце в потоці вже проїхало.",
    ]
    ty = 284
    for ln in lines:
        p.append(text(46, ty, ln, size=12, color=INK, anchor="start"))
        ty += 22

    render(os.path.join(OUT, "reorder-window.svg"), W, H, *p)


fig_header()
fig_frame_packets()
fig_rtcp_loop()
fig_lip_sync()
fig_lineage()
fig_depack_pipeline()
fig_reorder_window()
print("ok")
