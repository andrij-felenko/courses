# -*- coding: utf-8 -*-
"""Фігура до вставки hist-hls-dash.md — генерується окремо, бо спільний figs.py
у цій теці паралельно редагує інший агент (hist-webrtc). Виводить лише свій SVG
у ./img/. Після злиття гілок цю функцію можна перенести у figs.py як ще одну fig_*.
Ідея фігури: 2008–2010 чотири табори (Microsoft, Apple, Adobe, 3GPP) незалежно
зробили ОДНЕ Й ТЕ САМЕ — сегменти+плейлист+ABR поверх HTTP, але кожен у СВОЇЙ
несумісній обгортці. MPEG 2010 (call for proposals, 87 подань) звела їх в один
нейтральний кодеконезалежний стандарт DASH (2012). Та Apple лишила HLS рідним
на своєму залізі — тож живими лишилися ДВОЄ: HLS + DASH."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


def fig_hls_war_to_dash():
    W, H = 980, 520
    P = []
    P.append(text(W / 2, 30, "Війна форматів → один DASH: чотири обгортки, двоє вижили",
                  size=16.5, bold=True))

    # ── зліва: чотири незалежні табори 2008–2010 (та сама ідея, різні обгортки) ──
    P.append(text(180, 62, "2008–2010: одна ідея, чотири обгортки",
                  size=12, bold=True, color=POS))
    camps = [
        ("Smooth Streaming", "Microsoft · 2008\nfMP4", 115),
        ("HLS", "Apple · 2009\nMPEG-2 TS", 200),
        ("HDS", "Adobe · 2010\nfMP4 (F4F)", 285),
        ("3GPP AHS", "мобільні · 2009\nзамість RTSP/RTP", 370),
    ]
    box_r = []   # правий край+центр кожної картки — для стрілок у лійку
    for name, body, cy in camps:
        fr, w, h = textbox(160, cy, body, size=10, color=MUTED,
                           fill="#fdecea", stroke=POS, min_w=190)
        P.append(fr)
        P.append(text(160, cy - h / 2 - 7, name, size=11.5, color=POS, bold=True))
        box_r.append((160 + w / 2, cy))
    P.append(mtext(180, 422, "усі: сегменти + плейлист + ABR по HTTP,\nта формати НЕсумісні → 4 копії відео",
                   size=10, color=MUTED))

    # ── центр: лійка MPEG ──
    fx = 575
    fr, fw, fh = textbox(fx, 240,
                         "MPEG, 2010\ncall for proposals\n87 подань\n→ звести в один",
                         size=11, color=FIELD, fill="#e9f7ef", stroke=FIELD, sw=2, min_w=190)
    P.append(fr)
    P.append(text(fx, 240 - fh / 2 - 8, "нейтральний суддя", size=11, color=FIELD, bold=True))
    for rx, cy in box_r:
        P.append(arrow(rx + 4, cy, fx - fw / 2 - 4, 240, color=MUTED, sw=1.4))

    # ── праворуч-угорі: один стандарт DASH ──
    dx = 850
    fr, dw, dh = textbox(dx, 185, "MPEG-DASH\nISO/IEC 23009-1\nквітень 2012\nкодеконезалежний",
                         size=11, color=NEG, fill="#eaf0fd", stroke=NEG, sw=2, min_w=175)
    P.append(fr)
    P.append(arrow(fx + fw / 2 + 4, 232, dx - dw / 2 - 4, 192, color=FIELD, sw=2))

    # ── праворуч-унизу: HLS вижив окремо (вперте Apple-залізо) ──
    fr, hw, hh = textbox(dx, 378, "HLS живе далі\nApple не дала DASH\nна свої пристрої\n(мільярди)",
                         size=10.5, color=POS, fill="#fdecea", stroke=POS, sw=2, min_w=175)
    P.append(fr)
    # пунктир: HLS оминає лійку — лишається сам по собі
    P.append(line(box_r[1][0] + 4, camps[1][2], dx - hw / 2 - 4, 360,
                  color=POS, sw=1.6, dash="6 5"))
    P.append(text((box_r[1][0] + dx) / 2 + 20, 322,
                  "HLS оминає злиття", size=10, color=POS, italic=True))

    P.append(text(W / 2, H - 18,
                  "підсумок: зоопарк звівся не до одного, а до ДВОХ — "
                  "DASH для всіх + HLS для Apple-світу",
                  size=12, color=INK))
    render("img/hls-war-to-dash.svg", W, H, *P)


if __name__ == "__main__":
    fig_hls_war_to_dash()
    print("OK: hls-war-to-dash.svg -> img/")
