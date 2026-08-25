# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CTRL  = "#2457d6"      # керувальний канал — холодне
MEDIA = "#b08900"      # медіа — тепле
CTRLF = "#eaf0fd"
MEDF  = "#fdf6e3"
HDRF  = "#fdecea"


def codepanel(x, y, w, lines, size=12, lh=19, pad=14, fill=FILL, stroke=LINE):
    """Панель із рядками опису, вирівняними ліворуч. Повертає (фрагмент, висота)."""
    h = pad * 2 + len(lines) * lh
    out = rect(x, y, w, h, fill=fill, stroke=stroke)
    ty = y + pad + size
    for ln in lines:
        out += text(x + pad, ty, ln, size=size, anchor="start")
        ty += lh
    return out, h


# ── sdp-anatomy: два рівні опису сеансу ───────────────────────────────────────
# Ідея: опис поділено рівно на дві категорії — спільне на весь сеанс і те, що
# стосується однієї доріжки. Кожен блок відповідає на своє питання приймача.

def fig_sdp():
    W, H = 980, 470
    LX, LW = 30, 520
    RX, RW = 590, 360
    p = []

    labels = [("рівень сеансу", 34), ("рівень медіа: відео", 196), ("рівень медіа: звук", 339)]
    for s, y in labels:
        p.append(text(LX, y, s, size=11, color=MUTED, anchor="start", bold=True))

    sess = [
        "v=0",
        "o=- 1109162014219182 1 IN IP4 192.168.1.64",
        "s=Media Presentation",
        "c=IN IP4 0.0.0.0",
        "t=0 0",
        "a=control:*",
    ]
    vid = [
        "m=video 0 RTP/AVP 96",
        "a=rtpmap:96 H264/90000",
        "a=fmtp:96 packetization-mode=1;",
        "   sprop-parameter-sets=Z0LgHtoCgPRA,aM4wpIA=",
        "a=control:trackID=1",
    ]
    aud = [
        "m=audio 0 RTP/AVP 8",
        "a=rtpmap:8 PCMA/8000",
        "a=control:trackID=2",
    ]

    fa, ha = codepanel(LX, 44, LW, sess, fill=CTRLF)
    fb, hb = codepanel(LX, 206, LW, vid, fill=MEDF)
    fc, hc = codepanel(LX, 349, LW, aud, fill=MEDF)
    p += [fa, fb, fc]

    notes = [
        (70, 92, ["Спільне на весь сеанс:", "хто оголошує й під якою назвою,",
                  "чи має показ кінець у часі."]),
        (212, 110, ["Відеодоріжка:", "номер 96 означає H.264,", "годинник міток — 90 кГц,",
                    "параметри декодера наперед,", "власна адреса для SETUP."]),
        (356, 72, ["Звукова доріжка:", "свій номер, свій годинник,", "своя адреса."]),
    ]
    for y, h, lines in notes:
        p.append(fitbox(RX, y, RW, h, "\n".join(lines), size=12, pad=12, fill=BG))
        cy = y + h / 2
        p.append(arrow(LX + LW + 6, cy, RX - 8, cy, color=MUTED))

    render(os.path.join(OUT, "sdp-anatomy.svg"), W, H, *p)


# ── session-flow: розмова, що передує першому кадрові ─────────────────────────
# Ідея: керувальний канал і медіапотік — різні дроти; стан сеансу живе на сервері
# і рухається рівно тими командами, що позначені праворуч.

def fig_flow():
    W, H = 940, 600
    CX, SX = 140, 620
    p = []

    b1, _, _ = textbox(CX, 70, "Плеєр\n(клієнт)", size=13, fill=CTRLF)
    b2, _, _ = textbox(SX, 70, "Камера\n(сервер RTSP)", size=13, fill=CTRLF)
    p += [b1, b2]
    p.append(line(CX, 100, CX, 562, color=MUTED, sw=1.2, dash="4 5"))
    p.append(line(SX, 100, SX, 562, color=MUTED, sw=1.2, dash="4 5"))

    rows = [
        ("r", "OPTIONS rtsp://cam/stream", CTRL, None),
        ("l", "200 OK · Public: DESCRIBE, SETUP, PLAY, PAUSE, TEARDOWN", CTRL, None),
        ("r", "DESCRIBE · Accept: application/sdp", CTRL, None),
        ("l", "200 OK · тіло — SDP: доріжки, кодеки, control-адреси", CTRL, None),
        ("r", "SETUP trackID=1 · Transport: client_port=5000-5001", CTRL, None),
        ("l", "200 OK · Session: 12AF6C · server_port=6970-6971", CTRL, "Ready"),
        ("r", "SETUP trackID=2 · Session: 12AF6C", CTRL, None),
        ("r", "PLAY · Session: 12AF6C · Range: npt=0-", CTRL, None),
        ("l", "200 OK · RTP-Info: seq=9810092;rtptime=3450012", CTRL, "Playing"),
        ("l", "RTP: медіа з порту 6970 на 5000 — повз керувальний канал", MEDIA, None),
        ("d", "RTCP ⇄ звіти відправника й приймача", MEDIA, None),
        ("r", "GET_PARAMETER · Session: 12AF6C — тримає сеанс живим", CTRL, None),
        ("r", "TEARDOWN · Session: 12AF6C", CTRL, "Init"),
    ]

    y = 132
    p.append(fitbox(790, 118, 120, 28, "Init", size=12, pad=4, fill="#eafaf0"))
    for kind, label, col, state in rows:
        if kind == "r":
            p.append(arrow(CX + 6, y, SX - 6, y, color=col, sw=1.8))
        elif kind == "l":
            p.append(arrow(SX - 6, y, CX + 6, y, color=col, sw=2.2 if col == MEDIA else 1.8))
        else:
            p.append(line(CX + 6, y, SX - 6, y, color=col, sw=1.8, dash="6 4"))
        p.append(text((CX + SX) / 2, y - 9, label, size=11, color=INK))
        if state:
            p.append(fitbox(790, y - 14, 120, 28, state, size=12, pad=4, fill="#eafaf0"))
        y += 34

    render(os.path.join(OUT, "session-flow.svg"), W, H, *p)


# ── interleaved: медіа й керування в одному TCP-потоці ────────────────────────
# Ідея: межі задає лише поле довжини — шукати «$» у байтах не можна.

def fig_interleaved():
    W, H = 920, 344
    p = []
    p.append(text(448, 52, "один TCP-потік, порт 554 — керування й медіа впереміш",
                  size=13, bold=True))
    p.append(arrow(20, 82, 876, 82, color=MUTED, sw=1.4))

    y, h = 110, 64
    segs = [
        (20, 170, "RTSP-текст\nSETUP …", CTRLF, 12),
        (190, 34, "$", HDRF, 14),
        (224, 34, "0x00", HDRF, 11),
        (258, 50, "0x0410", HDRF, 11),
        (308, 180, "RTP-пакет · 1040 байтів", MEDF, 12),
        (488, 34, "$", HDRF, 14),
        (522, 34, "0x01", HDRF, 11),
        (556, 50, "0x0034", HDRF, 11),
        (606, 110, "RTCP RR · 52 б", MEDF, 11),
        (716, 160, "RTSP-текст\n200 OK …", CTRLF, 12),
    ]
    for x, w, s, fill, size in segs:
        p.append(fitbox(x, y, w, h, s, size=size, pad=5, fill=fill))

    by = y + h + 8
    p.append(line(190, by, 190, by + 14, color=MUTED))
    p.append(line(190, by + 14, 308, by + 14, color=MUTED))
    p.append(line(308, by, 308, by + 14, color=MUTED))
    p.append(text(249, by + 34,
                  "чотири байти обгортки: «$» · номер каналу · довжина (16 біт, старший байт перший)",
                  size=11, color=MUTED))

    p.append(fitbox(20, 254, 880, 74,
                    "Довжина — єдиний орієнтир на межі блоків.\n"
                    "Байт «$» трапляється й усередині стисненого відео, тож шукати його в потоці не можна:\n"
                    "розбирач відлічує рівно стільки байтів, скільки сказано, і аж тоді читає наступний байт як початок обгортки.",
                    size=12, pad=12, fill=BG))

    render(os.path.join(OUT, "interleaved.svg"), W, H, *p)


# ── reader: як клієнт читає одну одиницю з керувального сокета ────────────────
# Ідея: обидві гілки читають рівно за оголошеною довжиною, а не за пошуком
# роздільника; саме тут ламається більшість саморобних клієнтів.

def fig_reader():
    W, H = 940, 512
    p = []
    p.append(text(470, 30, "одна одиниця з керувального сокета: дві гілки, обидві — за довжиною",
                  size=13, bold=True))

    p.append(fitbox(320, 48, 300, 48, "зазирнути в один байт\n(recv із MSG_PEEK)",
                    size=12, pad=8, fill=CTRLF))

    LX, RX, CW = 40, 520, 380

    left = [
        (136, 76, "байт «$» → двійковий блок\nще три байти обгортки: номер каналу\nі довжина (16 біт, старший байт перший)", MEDF),
        (236, 60, "прочитати РІВНО «довжина» байтів —\nце пакет RTP або RTCP", MEDF),
    ]
    right = [
        (136, 76, "будь-який інший байт → текстова відповідь\nчитати рядки, доки не трапиться порожній:\nце рядок стану й заголовки", CTRLF),
        (236, 60, "узяти Content-Length: N\n(заголовка немає → тіла немає)", CTRLF),
        (320, 60, "прочитати РІВНО N байтів тіла —\nце SDP", CTRLF),
    ]

    for y, h, s, fill in left:
        p.append(fitbox(LX, y, CW, h, s, size=12, pad=10, fill=fill))
    for y, h, s, fill in right:
        p.append(fitbox(RX, y, CW, h, s, size=12, pad=10, fill=fill))

    p.append(arrow(420, 96, 240, 130, color=MUTED))
    p.append(arrow(520, 96, 700, 130, color=MUTED))
    p.append(arrow(LX + CW / 2, 212, LX + CW / 2, 232, color=MUTED))
    p.append(arrow(RX + CW / 2, 212, RX + CW / 2, 232, color=MUTED))
    p.append(arrow(RX + CW / 2, 296, RX + CW / 2, 316, color=MUTED))

    p.append(fitbox(LX, 408, 860, 88,
                    "Обидві гілки відлічують стільки байтів, скільки обіцяно, і жодним більше.\n"
                    "Зайвий прочитаний байт з'їдає початок наступної одиниці, недочитаний лишається в сокеті\n"
                    "й зсуває все подальше — а роздільник шукати нема за чим: «$» вільно трапляється в стисненому відео.",
                    size=12, pad=12, fill=BG))

    render(os.path.join(OUT, "client-reader.svg"), W, H, *p)


fig_sdp()
fig_flow()
fig_interleaved()
fig_reader()
print("ok")
