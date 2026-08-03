# -*- coding: utf-8 -*-
"""Фігури до теми «Мережеві джерела: RTSP, UDP і депейлоадинг RTP»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Ланцюг відновлення: що приходить і хто що лагодить ───────────────────
def fig_chain():
    W, H = 900, 700
    frags = []

    states = [
        "датаграми UDP,\nяк їх віддало ядро",
        "буфери конвеєра:\nодна датаграма — один буфер",
        "RTP-пакети за порядком,\nвидані рівномірно в часі",
        "цілі NAL-одиниці з PTS,\nключові кадри позначені",
        "декодовані кадри\nу форматі пікселів",
    ]
    elems = [
        "udpsrc  /  rtspsrc\nдістати з сокета, оголосити caps",
        "rtpjitterbuffer\nпорядок, рівний темп, облік втрат",
        "rtph264depay\nзібрати кадр із пакетів",
        "avdec_h264  /  v4l2h264dec\nдекодувати",
    ]

    SX, SW, SH = 90, 340, 54
    EX, EW, EH = 480, 340, 64
    ys = [70, 200, 330, 460, 590]

    for y, s in zip(ys, states):
        frags.append(fitbox(SX, y, SW, SH, s, size=13))

    for i, e in enumerate(elems):
        y0 = ys[i] + SH                 # низ верхньої рамки
        y1 = ys[i + 1]                  # верх нижньої рамки
        mid = (y0 + y1) / 2.0
        frags.append(arrow(SX + SW / 2, y0 + 4, SX + SW / 2, y1 - 6))
        ey = mid - EH / 2
        frags.append(fitbox(EX, ey, EW, EH, e, size=13))
        frags.append(line(SX + SW / 2 + 6, mid, EX - 2, mid, color=MUTED, sw=1.2, dash="5 4"))

    return render(out('repair-chain.svg'), W, H, *frags,
                  title="Мережеве джерело: чотири роботи, які треба зробити")


# ── 2. Один кадр — багато RTP-пакетів ──────────────────────────────────────
def fig_packetization():
    W, H = 1000, 500
    frags = []

    # верх: закодований кадр (access unit)
    frags.append(fitbox(70, 60, 110, 44, "SPS", size=13))
    frags.append(fitbox(190, 60, 110, 44, "PPS", size=13))
    frags.append(fitbox(310, 60, 620, 44, "IDR-зріз: 40 КБ", size=13))
    frags.append(text(500, 126, "один момент відліку — один access unit", size=13, color=MUTED))

    frags.append(arrow(500, 140, 500, 174))

    # середина: три пакети
    pk = [
        ["FU-A   S=1  E=0", "seq 1000", "TS 6 300 000", "marker = 0"],
        ["FU-A   S=0  E=0", "seq 1001", "TS 6 300 000", "marker = 0"],
        ["FU-A   S=0  E=1", "seq 1002", "TS 6 300 000", "marker = 1"],
    ]
    for i, lines in enumerate(pk):
        x = 80 + i * 290
        frags.append(fitbox(x, 182, 260, 90, "\n".join(lines), size=13))

    frags.append(text(500, 302, "будова кожного такого пакета", size=13, color=MUTED))

    # низ: байтова смуга
    cells = [(70, 240, "RTP-заголовок 12 Б"),
             (310, 150, "FU indicator 1 Б"),
             (460, 150, "FU header 1 Б"),
             (610, 320, "шматок NAL-одиниці")]
    for x, w, s in cells:
        frags.append(fitbox(x, 318, w, 50, s, size=12))

    frags.append(line(385, 368, 385, 392, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(535, 368, 535, 392, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(fitbox(272, 392, 210, 62, "тип 28 —\nозначає «це шматок»", size=12))
    frags.append(fitbox(502, 392, 240, 62, "S = перший шматок\nE = останній шматок", size=12))

    return render(out('packetization.svg'), W, H, *frags,
                  title="Кадр більший за MTU — його ріжуть на пакети")


# ── 3. Буфер джитера: що він виправляє ─────────────────────────────────────
def fig_jitter():
    W, H = 980, 500
    frags = []

    frags.append(text(490, 66, "як прийшло з мережі — порядок і моменти довільні",
                      size=13, color=MUTED))
    arr = ["seq 1", "seq 2", "seq 4", "seq 3", "seq 6", "seq 7\nзапізно"]
    for i, s in enumerate(arr):
        frags.append(fitbox(90 + i * 124, 84, 110, 54, s, size=12))

    for x in (145, 461, 777):
        frags.append(arrow(x, 142, x, 194))

    frags.append(fitbox(90, 200, 730, 84,
                        "буфер джитера: тримає пакети рівно latency\n"
                        "за цей час спізнюваний ще встигає стати на своє місце",
                        size=13))

    for x in (145, 461, 777):
        frags.append(arrow(x, 288, x, 340))

    outp = ["seq 1", "seq 2", "seq 3", "seq 4", "seq 5\n✕ втрата", "seq 6"]
    for i, s in enumerate(outp):
        frags.append(fitbox(90 + i * 124, 346, 110, 54, s, size=12))
    frags.append(text(490, 428, "на вихід — за номерами й рівним темпом",
                      size=13, color=MUTED))
    frags.append(fitbox(90, 444, 730, 44,
                        "seq 7 прийшов уже після вікна — його викинуто так само, як загублений",
                        size=12))

    return render(out('jitter-window.svg'), W, H, *frags,
                  title="Вікно очікування: порядок і рівний темп ціною затримки")


# ── 4. RTSP: керування окремо, медіа окремо ────────────────────────────────
def fig_rtsp():
    W, H = 1000, 520
    frags = []

    frags.append(fitbox(60, 84, 200, 90, "клієнт\nrtspsrc", size=14))
    frags.append(fitbox(740, 84, 200, 90, "сервер\nкамера з RTSP", size=14))

    frags.append(fitbox(300, 70, 400, 118,
                        "керувальний канал — TCP, порт 554\n"
                        "OPTIONS · DESCRIBE → SDP\n"
                        "SETUP (транспорт і порти) · PLAY · TEARDOWN", size=13))
    frags.append(arrow(264, 108, 296, 108))
    frags.append(arrow(736, 150, 704, 150))

    frags.append(fitbox(300, 216, 400, 60, "RTP — UDP, порт p", size=13))
    frags.append(arrow(736, 246, 704, 246))
    frags.append(arrow(296, 246, 264, 246))

    frags.append(fitbox(300, 300, 400, 60, "RTCP — UDP, порт p+1", size=13))
    frags.append(arrow(736, 330, 704, 330))
    frags.append(arrow(264, 330, 296, 330))

    frags.append(fitbox(60, 396, 880, 88,
                        "UDP не проходить крізь NAT або фаєрвол — rtspsrc переходить на interleaved:\n"
                        "ті самі RTP-пакети йдуть усередині вже відкритого керувального TCP-з'єднання,\n"
                        "кожен із префіксом «$ номер каналу довжина»", size=13))

    return render(out('rtsp-channels.svg'), W, H, *frags,
                  title="RTSP: канал керування й канал медіа — різні канали")


# ── 5. SDP → caps: який рядок дає яке поле (вставка api-) ──────────────────
def fig_sdp_caps():
    W, H = 1080, 660
    frags = []

    frags.append(text(285, 62, "SDP: відповідь сервера на DESCRIBE", size=14, color=MUTED))
    frags.append(text(820, 62, "caps application/x-rtp", size=14, color=MUTED))

    rows = [
        ("m=video 0 RTP/AVP 96",
         "media=(string)video\npayload=(int)96"),
        ("a=rtpmap:96 H264/90000",
         "encoding-name=(string)H264\nclock-rate=(int)90000"),
        ("a=fmtp:96 packetization-mode=1;\nsprop-parameter-sets=Z0LgHtoCgPRA,aM4wpIA=",
         "packetization-mode=(string)1\nsprop-parameter-sets=(string)Z0Lg…"),
        ("a=framerate:30",
         "a-framerate=(string)30"),
        ("c=IN IP4 0.0.0.0\nпорти — з відповіді на SETUP",
         "у caps не потрапляє:\nце адреса й порт udpsrc"),
    ]

    LX, LW = 50, 470
    RX, RW = 610, 420
    y, BH = 84, 74
    for l, r in rows:
        frags.append(fitbox(LX, y, LW, BH, l, size=13))
        frags.append(fitbox(RX, y, RW, BH, r, size=13))
        frags.append(arrow(LX + LW + 10, y + BH / 2, RX - 10, y + BH / 2))
        y += BH + 22

    frags.append(fitbox(50, y + 8, 980, 54,
                        "числоподібні значення з a=fmtp мусять лишитися рядками:\n"
                        "packetization-mode=(string)1, а не packetization-mode=1",
                        size=13))

    return render(out('sdp-to-caps.svg'), W, H, *frags,
                  title="Кожне поле caps приходить із конкретного рядка SDP")


# ── 6. Той самий RTP-пакет: у датаграмі й усередині TCP-з'єднання ───────────
def fig_interleaved():
    W, H = 1020, 400
    frags = []

    frags.append(text(510, 66, "RTP/AVP/UDP — пакет їде власною датаграмою",
                      size=14, color=MUTED))
    for x, w, s in [(60, 230, "заголовки IP + UDP\n28 Б"),
                    (300, 190, "RTP-заголовок\n12 Б"),
                    (500, 460, "корисне навантаження")]:
        frags.append(fitbox(x, 84, w, 62, s, size=13))

    frags.append(text(510, 196, "RTP/AVP/TCP — той самий пакет усередині керувального з'єднання",
                      size=14, color=MUTED))
    for x, w, s in [(60, 110, "$\n0x24"),
                    (180, 150, "канал\n1 Б"),
                    (340, 210, "довжина 2 Б,\nстарший байт перший"),
                    (560, 150, "RTP-заголовок\n12 Б"),
                    (720, 240, "корисне навантаження")]:
        frags.append(fitbox(x, 214, w, 62, s, size=13))

    frags.append(fitbox(60, 306, 900, 66,
                        "Transport: RTP/AVP/TCP;unicast;interleaved=0-1 — канал 0 везе RTP, канал 1 везе RTCP\n"
                        "два байти довжини обмежують пакет 65535 байтами; межу датаграми заміняє саме це поле",
                        size=13))

    return render(out('interleaved-frame.svg'), W, H, *frags,
                  title="Межу пакета в TCP доводиться позначати самому")


# ══ Фігури до вставки math-jitter-latency.md ════════════════════════════════

# ── 7. Звідки береться D і чому невідомий зсув годинників скорочується ──────
def fig_d_algebra():
    W, H = 1020, 730
    frags = []

    PX = 14.0          # пікселів на мілісекунду у верхній панелі
    X0 = 150.0
    ys, yr = 140.0, 262.0

    def tick(x, y, color=INK):
        return line(x, y - 12, x, y + 12, color=color, sw=2.4)

    # ── панель A: пара через межу кадрів
    frags.append(text(60, 66, "A. Пара пакетів через межу кадрів",
                      size=15, bold=True, anchor="start"))
    frags.append(line(90, ys, 960, ys, color=MUTED, sw=1.4))
    frags.append(line(90, yr, 960, yr, color=MUTED, sw=1.4))
    frags.append(text(90, ys - 22, "шкала відправника: мітка RTP S",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(90, yr + 26, "шкала приймача: час прибуття R у тактах",
                      size=12, color=MUTED, anchor="start"))

    xs1, xs2 = X0, X0 + 33.33 * PX
    xr1, xr2 = X0 + 21.25 * PX, X0 + 41.33 * PX
    frags.append(tick(xs1, ys, NEG)); frags.append(tick(xs2, ys, NEG))
    frags.append(tick(xr1, yr, POS)); frags.append(tick(xr2, yr, POS))
    frags.append(text(xs1, ys - 44, "S = 300 000", size=12, color=NEG))
    frags.append(text(xs2, ys - 44, "S = 303 000", size=12, color=NEG))
    frags.append(text(xr1, yr + 52, "R = 301 913", size=12, color=POS))
    frags.append(text(xr2, yr + 52, "R = 303 720", size=12, color=POS))
    frags.append(arrow(xs1, ys + 14, xr1, yr - 14, color=INK, sw=1.6))
    frags.append(arrow(xs2, ys + 14, xr2, yr - 14, color=INK, sw=1.6))
    frags.append(text((xs1 + xr1) / 2 - 70, (ys + yr) / 2 + 4,
                      "проліт 1913", size=12, color=MUTED, anchor="end"))
    frags.append(text((xs2 + xr2) / 2 + 70, (ys + yr) / 2 + 4,
                      "проліт 720", size=12, color=MUTED, anchor="start"))

    frags.append(fitbox(130, 348, 520, 62,
                        "D = 720 − 1913 = −1193 такти = −13.3 мс\n"
                        "останній пакет кадру відстояв у черзі вузького місця",
                        size=12.5))

    # ── панель B: пара всередині кадру
    frags.append(text(60, 456, "B. Пара пакетів усередині одного кадру "
                               "(шкалу часу розтягнуто)",
                      size=15, bold=True, anchor="start"))
    ys2, yr2 = 520.0, 616.0
    frags.append(line(90, ys2, 560, ys2, color=MUTED, sw=1.4))
    frags.append(line(90, yr2, 560, yr2, color=MUTED, sw=1.4))
    xs = 220.0
    frags.append(tick(xs, ys2, NEG))
    frags.append(text(xs, ys2 - 22, "S = 303 000 в обох", size=12, color=NEG))
    xa, xb = 330.0, 470.0
    frags.append(tick(xa, yr2, POS)); frags.append(tick(xb, yr2, POS))
    frags.append(text(xa, yr2 + 30, "R", size=12, color=POS))
    frags.append(text(xb, yr2 + 30, "R + 52", size=12, color=POS))
    frags.append(arrow(xs - 4, ys2 + 14, xa, yr2 - 14, color=INK, sw=1.6))
    frags.append(arrow(xs + 4, ys2 + 14, xb, yr2 - 14, color=INK, sw=1.6))

    frags.append(fitbox(620, 486, 380, 96,
                        "S не змінилася, тому D дорівнює\n"
                        "самій паузі між прибуттями:\n"
                        "D = +52 такти = 0.58 мс — це час\n"
                        "серіалізації на вузькому місці",
                        size=12.5))
    frags.append(fitbox(620, 600, 380, 62,
                        "Обидва прольоти містять той самий\n"
                        "невідомий зсув годинників —\n"
                        "у різниці він скорочується",
                        size=12.5))

    return render(out('jitter-d-algebra.svg'), W, H, *frags,
                  title="D — це зміна прольоту, а не сам проліт")


# ── 8. Ваги експоненційного фільтра з коефіцієнтом 1/16 ────────────────────
def fig_ema_weights():
    W, H = 1000, 470
    frags = []
    a = 1.0 / 16.0
    n = 48
    x0, bw, gap = 70.0, 15.0, 2.5
    base, hmax = 390.0, 300.0

    frags.append(line(x0 - 12, base, x0 + n * (bw + gap) + 12, base,
                      color=LINE, sw=1.6))
    for k in range(n):
        h = hmax * (1 - a) ** k
        x = x0 + k * (bw + gap)
        frags.append(rect(x, base - h, bw, h, fill="#dbe4f5", stroke=NEG,
                          sw=1.0, rx=1))
    for k in (0, 10, 20, 30, 40):
        x = x0 + k * (bw + gap) + bw / 2
        frags.append(line(x, base, x, base + 7, color=LINE, sw=1.4))
        frags.append(text(x, base + 26, str(k), size=12, color=MUTED))
    frags.append(text(x0 + n * (bw + gap) / 2, base + 52,
                      "k — скільки пар тому прийшло значення |D|",
                      size=12.5, color=MUTED))

    for k, lab in ((11, "11"), (47, "47")):
        x = x0 + k * (bw + gap) + bw / 2
        frags.append(line(x, base, x, base + 44, color=POS, sw=1.6, dash="5 4"))
        frags.append(text(x, base + 62, lab, size=12, color=POS, bold=True))

    frags.append(fitbox(560, 78, 400, 76,
                        "w(k) = α·(1 − α)ᵏ,   α = 1/16\n"
                        "сума всіх ваг дорівнює одиниці",
                        size=13))
    frags.append(fitbox(560, 172, 400, 96,
                        "останні 11 пар несуть половину ваги\n"
                        "останні 47 пар — 95 % ваги\n"
                        "стала пам'яті 1/α = 16 пар",
                        size=13))

    return render(out('jitter-ema-weights.svg'), W, H, *frags,
                  title="Скільки минулого пам'ятає оцінка джитера")


# ── 9. Крива «частка запізнілих проти вікна очікування» ────────────────────
def fig_late_curve():
    import math
    W, H = 1020, 640
    frags = []

    XL, XR = 130.0, 950.0
    WMAX = 270.0
    sx = lambda w: XL + w * (XR - XL) / WMAX
    sy = lambda p: 90.0 + 100.0 * math.log10(0.1 / p)

    # сітка декад
    for dec, lab in ((0.1, "10 %"), (0.01, "1 %"), (0.001, "0.1 %"),
                     (1e-4, "0.01 %"), (1e-5, "0.001 %")):
        y = sy(dec)
        frags.append(line(XL, y, XR, y, color="#d6dbe2", sw=1.0, dash="4 5"))
        frags.append(text(XL - 14, y + 4, lab, size=12, color=MUTED, anchor="end"))

    frags.append(line(XL, 70, XL, 560, color=LINE, sw=1.6))
    frags.append(line(XL, 560, XR, 560, color=LINE, sw=1.6))
    for w in (0, 50, 100, 150, 200, 250):
        x = sx(w)
        frags.append(line(x, 560, x, 568, color=LINE, sw=1.4))
        frags.append(text(x, 590, str(w), size=12, color=MUTED))
    frags.append(text((XL + XR) / 2, 616, "вікно очікування W, мс",
                      size=13, color=MUTED))
    frags.append(text(XL - 14, 60, "частка запізнілих", size=12.5,
                      color=MUTED, anchor="end"))

    pts = [(5, 0.079), (10, 0.0211), (20, 0.00779), (30, 0.00290),
           (40, 0.001106), (50, 4.45e-4), (60, 2.02e-4), (80, 7.91e-5),
           (100, 6.26e-5), (150, 6.00e-5), (200, 3.00e-5)]
    poly = " ".join("%.1f,%.1f" % (sx(w), sy(p)) for w, p in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" '
                 'stroke-width="2.6"/>' % (poly, NEG))
    for w, p in pts:
        frags.append(circle(sx(w), sy(p), 4.5, fill=BG, stroke=NEG, sw=2.0))
    # обрив після 250 мс
    frags.append(line(sx(200), sy(3.0e-5), sx(250), 548, color=NEG, sw=2.6))
    frags.append(text(sx(250) + 4, 566, "0", size=12, color=NEG, anchor="start"))

    # стеля бюджету
    xb = sx(104)
    frags.append(line(xb, 300, xb, 560, color=POS, sw=1.8, dash="6 5"))

    frags.append(fitbox(560, 96, 400, 62,
                        "коліно ≈ 80 мс: далі кожні\n"
                        "10 мс вікна майже нічого не купують", size=12.5))
    frags.append(line(700, 158, 620, 196, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(fitbox(560, 200, 400, 88,
                        "полиця 80…150 мс — друга мода:\n"
                        "26 пакетів із 432 000 спізнилися\n"
                        "на 150…250 мс. Це не черга,\n"
                        "а окрема рідкісна подія", size=12.5))
    frags.append(fitbox(560, 316, 400, 84,
                        "стеля бюджету: 200 мс наскрізно\n"
                        "мінус 96 мс сталих доданків —\n"
                        "на вікно лишається 104 мс", size=12.5))
    frags.append(line(560, 358, xb + 4, 358, color=POS, sw=1.2, dash="4 4"))

    return render(out('jitter-late-curve.svg'), W, H, *frags,
                  title="Скільки пакетів не встигає у вікно завширшки W")


# ── 8. Байтова хірургія FU-A: звідки береться заголовок NAL-одиниці ────────
def fig_nal_surgery():
    W, H = 900, 480
    frags = []

    CW, CH = 42, 52
    KEEP_A = "#e8eefc"     # біти, що йдуть у вихідний заголовок з індикатора
    KEEP_B = "#e9f7ee"     # біти, що йдуть у вихідний заголовок із заголовка FU
    DROP = "#f2f2f2"       # службові біти, які нікуди не йдуть

    def byte_row(x, y, cells, fills):
        outp = []
        for i, (c, f) in enumerate(zip(cells, fills)):
            outp.append(fitbox(x + i * CW, y, CW, CH, c, size=12, pad=3, fill=f))
            outp.append(text(x + i * CW + CW / 2.0, y - 8, str(7 - i), size=10, color=MUTED))
        return outp

    ax = 40
    frags.append(text(ax + 4 * CW, 78, "індикатор фрагмента  p[0]", size=13, bold=True))
    frags += byte_row(ax, 100, ["F", "NRI", "NRI", "1", "1", "1", "0", "0"],
                      [KEEP_A] * 3 + [DROP] * 5)
    frags.append(fitbox(ax, 176, 8 * CW, 48,
                        "молодші п'ять бітів = 28: «це фрагмент»\nу вихідний заголовок вони не йдуть",
                        size=11))

    bx = 524
    frags.append(text(bx + 4 * CW, 78, "заголовок фрагмента  p[1]", size=13, bold=True))
    frags += byte_row(bx, 100, ["S", "E", "R", "t", "t", "t", "t", "t"],
                      [DROP] * 3 + [KEEP_B] * 5)
    frags.append(fitbox(bx, 176, 8 * CW, 48,
                        "S і E — прапорці збирання\nп'ять молодших бітів — тип вихідної одиниці",
                        size=11))

    rx = 282
    frags.append(text(rx + 4 * CW, 300, "заголовок вихідної NAL-одиниці", size=13, bold=True))
    frags += byte_row(rx, 320, ["F", "NRI", "NRI", "t", "t", "t", "t", "t"],
                      [KEEP_A] * 3 + [KEEP_B] * 5)

    frags.append(arrow(ax + 1.5 * CW, 230, rx + 1.5 * CW, 312))
    frags.append(arrow(bx + 5.5 * CW, 230, rx + 5.5 * CW, 312))

    frags.append(fitbox(220, 408, 460, 44,
                        "hdr = (p[0] & 0xE0) | (p[1] & 0x1F)", size=14))

    return render(out('nal-header-surgery.svg'), W, H, *frags,
                  title="FU-A: два службові байти містять усі біти заголовка")


# ── 9. Машина станів приймача: нижній поверх (одна NAL-одиниця) ────────────
def fig_fu_state():
    W, H = 1080, 590
    frags = []

    frags.append(fitbox(90, 150, 300, 80, "поза фрагментом\nin_fu = 0", size=14))
    frags.append(fitbox(690, 150, 300, 80, "збираю фрагмент\nin_fu = 1", size=14))

    frags.append(arrow(394, 172, 686, 172))
    frags.append(fitbox(430, 86, 220, 54, "FU-A з S=1\nвідкрити одиницю", size=12))

    frags.append(arrow(686, 208, 394, 208))
    frags.append(fitbox(430, 240, 220, 54, "E=1\nодиниця зібралася", size=12))

    frags.append(line(240, 232, 240, 338, color=MUTED, sw=1.2, dash="5 4"))
    frags.append(fitbox(50, 340, 380, 110,
                        "тип 1–23 — ціла одиниця, кладемо\n"
                        "тип 24 STAP-A — кілька дрібних поспіль\n"
                        "FU-A без S — хвіст чужої, викидаємо", size=12))

    frags.append(line(840, 232, 840, 338, color=MUTED, sw=1.2, dash="5 4"))
    frags.append(fitbox(650, 340, 380, 110,
                        "FU-A, S=0, E=0,\n"
                        "номер = попередній + 1 —\n"
                        "дописати шматок у кінець", size=12))

    frags.append(arrow(840, 454, 840, 486))
    frags.append(fitbox(430, 490, 600, 82,
                        "аварійний вихід: розрив номерів · новий S без E ·\n"
                        "інша мітка часу · переповнення накопичувача\n"
                        "len ← nal_start, кадр позначено як битий", size=12))

    return render(out('fu-state-machine.svg'), W, H, *frags,
                  title="Збирання однієї NAL-одиниці: два стани й чотири виходи")


# ── 10. Три сигнали, що закривають access unit ─────────────────────────────
def fig_au_close():
    W, H = 1060, 520
    frags = []

    PW, GAP, PH = 128, 12, 70
    X0 = 190
    HOT = "#fdecea"     # пакет, що закриває кадр
    GONE = "#f2f2f2"    # пакет, якого не було

    def row(y, label, cells, caption):
        outp = [fitbox(20, y, 150, PH, label, size=12)]
        for i, (txt, fill) in enumerate(cells):
            outp.append(fitbox(X0 + i * (PW + GAP), y, PW, PH, txt, size=11, pad=5, fill=fill))
        outp.append(fitbox(X0, y + PH + 8, 6 * PW + 5 * GAP, 40, caption, size=12))
        return outp

    frags += row(80, "усе на місці", [
        ("seq 41\nts T\nFU S=1", FILL),
        ("seq 42\nts T\nFU", FILL),
        ("seq 43\nts T\nFU E=1", FILL),
        ("seq 44\nts T\nзріз S=1", FILL),
        ("seq 45\nts T\nFU E=1, M=1", HOT),
        ("seq 46\nts T+3000\nFU S=1", FILL),
    ], "кадр закриває біт marker — тим самим пакетом, що його завершив")

    frags += row(230, "marker загублено", [
        ("seq 41\nts T\nFU S=1", FILL),
        ("seq 42\nts T\nFU E=1", FILL),
        ("seq 43\nts T\nFU S=1", FILL),
        ("seq 44\nts T\nFU E=1", FILL),
        ("seq 45\nts T+3000\nFU S=1", HOT),
        ("seq 46\nts T+3000\nFU", FILL),
    ], "кадр закриває зміна мітки часу — на один пакет пізніше, зате завжди")

    frags += row(380, "пакет із E зник", [
        ("seq 41\nts T\nFU S=1", FILL),
        ("seq 42\nts T\nFU", FILL),
        ("✕ немає\nseq 43\nFU E=1", GONE),
        ("seq 44\nts T\nFU S=1", HOT),
        ("seq 45\nts T\nFU E=1, M=1", FILL),
        ("seq 46\nts T+3000\nFU S=1", FILL),
    ], "новий S відрізає недозібрану одиницю; решта кадру лишається цілою")

    return render(out('au-close-signals.svg'), W, H, *frags,
                  title="Що насправді закриває кадр, коли прапорця E замало")

if __name__ == '__main__':
    for f in (fig_chain,
              fig_packetization,
              fig_jitter,
              fig_rtsp,
              fig_sdp_caps,
              fig_interleaved,
              fig_d_algebra,
              fig_ema_weights,
              fig_late_curve,
              fig_nal_surgery,
              fig_fu_state,
              fig_au_close):
        print(f())
