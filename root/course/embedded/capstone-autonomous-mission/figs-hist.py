# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Дві філософії передачі місії: постріл файлом vs діалог-рукостискання ───
def fig_blast_vs_handshake():
    W, H = 960, 560
    p = []
    p.append(text(W / 2, 30, "дві філософії передачі списку точок по ненадійному радіо", size=14, color=MUTED, bold=True))

    # ── Ліва половина: наївний «постріл файлом» ──
    lx = 40
    lw = 400
    p.append(rect(lx, 60, lw, 460, fill="#fdf1f0", stroke=POS, sw=1.6, rx=12))
    p.append(text(lx + lw / 2, 86, "наївно: вистрілити все одним потоком", size=13.5, color=POS, bold=True))

    gx = lx + 70          # колонка GCS
    bx = lx + lw - 70     # колонка борт
    p.append(text(gx, 116, "GCS", size=13, color=INK, bold=True))
    p.append(text(bx, 116, "борт", size=13, color=INK, bold=True))
    p.append(line(gx, 126, gx, 500, color="#d9b3b0", sw=1.2, dash="3,4"))
    p.append(line(bx, 126, bx, 500, color="#d9b3b0", sw=1.2, dash="3,4"))

    # потік пакетів згори вниз; один губиться
    seqs = [("#0", True), ("#1", True), ("#2", False), ("#3", True), ("#4", True)]
    y = 160
    for seq, ok in seqs:
        if ok:
            p.append(arrow(gx + 8, y, bx - 8, y + 26, color=POS, sw=1.7))
            p.append(text((gx + bx) / 2, y + 6, seq, size=11.5, color=POS, bold=True))
        else:
            # загублений пакет — стрілка обривається на півдорозі
            midx = (gx + bx) / 2 + 8
            p.append(line(gx + 8, y, midx, y + 13, color=MUTED, sw=1.6, dash="4,3"))
            p.append(text(midx + 20, y + 8, "✕ загубився", size=11, color=MUTED, bold=True))
        y += 62

    b, bw, bh = textbox(lx + lw / 2, 470, "борт зібрав місію з ДІРКОЮ (#2 нема)\nі не знає про це — полетить за спотвореним маршрутом",
                        size=11.5, pad=10, fill="#fff", stroke=POS, color=POS)
    p.append(b)

    # ── Права половина: діалог із підтвердженням кожного seq ──
    rx0 = 520
    rw = 400
    p.append(rect(rx0, 60, rw, 460, fill="#eef7ee", stroke=FIELD, sw=1.6, rx=12))
    p.append(text(rx0 + rw / 2, 86, "рукостискання: борт САМ просить кожен seq", size=13.5, color="#1e7d42", bold=True))

    gx2 = rx0 + 70
    bx2 = rx0 + rw - 70
    p.append(text(gx2, 116, "GCS", size=13, color=INK, bold=True))
    p.append(text(bx2, 116, "борт", size=13, color=INK, bold=True))
    p.append(line(gx2, 126, gx2, 500, color="#a9d3b4", sw=1.2, dash="3,4"))
    p.append(line(bx2, 126, bx2, 500, color="#a9d3b4", sw=1.2, dash="3,4"))

    # діалог: COUNT → REQUEST(0) → ITEM(0) → REQUEST(1) → ITEM(1) → … → ACK
    steps = [
        ("g2b", "COUNT = 5"),
        ("b2g", "дай #0"),
        ("g2b", "ITEM #0"),
        ("b2g", "дай #1"),
        ("g2b", "ITEM #1"),
        ("b2g", "дай #2  (втратив — прошу знову)"),
        ("g2b", "ITEM #2"),
        ("b2g", "ACK ✓ прийняв усі 5"),
    ]
    y = 150
    dy = 44
    for kind, lbl in steps:
        if kind == "g2b":
            p.append(arrow(gx2 + 8, y, bx2 - 8, y, color=FIELD, sw=1.7))
            p.append(text((gx2 + bx2) / 2, y - 7, lbl, size=10.8, color="#1e7d42", bold=True))
        else:
            p.append(arrow(bx2 - 8, y, gx2 + 8, y, color=NEG, sw=1.7))
            p.append(text((gx2 + bx2) / 2, y - 7, lbl, size=10.8, color=NEG, bold=True))
        y += dy

    b2, bw2, bh2 = textbox(rx0 + rw / 2, 495, "список НЕ може зібратися з дірками:\nборт добудовує по одному, з підтвердженням у кінці",
                           size=11.5, pad=10, fill="#fff", stroke=FIELD, color="#1e7d42")
    p.append(b2)

    return render(os.path.join(OUT, "hist-blast-vs-handshake.svg"), W, H, *p)


# ── 2. Чому float32 «пливе» біля 180° довготи — і що дає _INT ─────────────────
def fig_float_precision():
    W, H = 960, 520
    p = []
    p.append(text(W / 2, 30, "float32: крок сітки координат РОСТЕ з величиною кута", size=14, color=MUTED, bold=True))

    # координатна вісь довготи 0…180, під нею — крок похибки
    ax0 = 80
    ax1 = W - 80
    ay = 130
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.8))
    for frac, lab in [(0, "0°"), (0.25, "45°"), (0.5, "90°"), (0.75, "135°"), (1.0, "180°")]:
        x = ax0 + frac * (ax1 - ax0)
        p.append(line(x, ay - 5, x, ay + 5, color=INK, sw=1.5))
        p.append(text(x, ay + 22, lab, size=12, color=INK, bold=True))
    p.append(text(ax1, ay - 12, "довгота →", size=12, color=MUTED, anchor="end"))

    # стовпчики: крок сітки в метрах для кількох діапазонів (worst-case в діапазоні)
    # мантиса 23 біт; крок = 2^exp * 2^-23 * 111111 м, exp = floor(log2(кут))
    bands = [
        (0.06, "≈0.4°", "0.006 м", 0.02),    # малий кут
        (0.28, "≈45°",  "0.05 м",  0.10),
        (0.53, "≈90°",  "0.85 м",  0.55),
        (0.78, "≈135°", "0.85 м",  0.55),
        (0.97, "≈179°", "1.7 м",   1.0),     # найгірший випадок
    ]
    baseY = 300
    maxbar = 130
    for frac, ang, err, rel in bands:
        x = ax0 + frac * (ax1 - ax0)
        bw = 66
        bh = maxbar * rel
        col = POS if rel >= 0.9 else ("#e08a1e" if rel >= 0.4 else FIELD)
        fill = "#fdecea" if rel >= 0.9 else ("#fff6e6" if rel >= 0.4 else "#eef7ee")
        p.append(rect(x - bw / 2, baseY - bh, bw, bh, fill=fill, stroke=col, sw=1.8, rx=5))
        p.append(text(x, baseY - bh - 8, err, size=12, color=col, bold=True))
        p.append(text(x, baseY + 18, ang, size=11, color=MUTED))
    p.append(line(ax0, baseY, ax1, baseY, color=INK, sw=1.4))
    p.append(text(ax0 - 8, baseY - maxbar / 2, "крок сітки, м", size=11.5, color=MUTED, anchor="end"))

    # формула найгіршого випадку
    fb, fbw, fbh = textbox(W / 2, 372,
                           "найгірше (біля ±180°):  2⁷ · 2⁻²³ · 111111 м  ≈  1.7 м",
                           size=13, pad=11, fill="#fdf1f0", stroke=POS, color=POS, bold=True)
    p.append(fb)

    # порівняння з _INT
    ib, ibw, ibh = textbox(W / 2, 448,
                           "_INT:  широта/довгота = цілі  (градуси × 10⁷)  →  крок ≈ 1.1 см  СКРІЗЬ, без «плавання»",
                           size=13, pad=11, fill="#eef7ee", stroke=FIELD, color="#1e7d42", bold=True)
    p.append(ib)

    return render(os.path.join(OUT, "hist-float-precision.svg"), W, H, *p)


if __name__ == "__main__":
    fig_blast_vs_handshake()
    fig_float_precision()
    print("ok")
