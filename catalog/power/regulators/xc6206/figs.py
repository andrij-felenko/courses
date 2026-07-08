# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: цоколівка SOT-23 (вигляд згори) ───────────────────────────────
def fig_pinout():
    W, H = 620, 380
    frags = []

    # корпус чипа
    bx, by, bw, bh = 210, 120, 200, 150
    frags.append(rect(bx, by, bw, bh, fill="#2b2b2b", stroke="#111", sw=2, rx=10))
    frags.append(text(bx + bw / 2, by + bh / 2 - 6, "662K", size=34, color="#f4f6f8", bold=True))
    frags.append(text(bx + bw / 2, by + bh / 2 + 22, "(XC6206 · 3.3 В)", size=13, color="#c9ccd1"))
    # крапка-ключ 1-ї ноги
    frags.append(circle(bx + 20, by + 20, 6, fill="#f4f6f8", stroke="#f4f6f8", sw=1))

    lead = "#9aa0a6"
    # два виводи знизу (pin1 ліворуч, pin2 праворуч), один зверху (pin3)
    # pin 1 — Vss (низ-ліво)
    frags.append(rect(bx + 22, by + bh, 34, 26, fill=lead, stroke="#555", sw=1.2, rx=3))
    frags.append(text(bx + 39, by + bh + 55, "1", size=15, bold=True))
    frags.append(text(bx + 39, by + bh + 78, "Vss", size=17, color=NEG, bold=True))
    frags.append(text(bx + 39, by + bh + 98, "(GND)", size=12, color=MUTED))

    # pin 2 — Vin (низ-право)
    frags.append(rect(bx + bw - 56, by + bh, 34, 26, fill=lead, stroke="#555", sw=1.2, rx=3))
    frags.append(text(bx + bw - 39, by + bh + 55, "2", size=15, bold=True))
    frags.append(text(bx + bw - 39, by + bh + 78, "Vin", size=17, color=POS, bold=True))
    frags.append(text(bx + bw - 39, by + bh + 98, "1.8–6 В", size=12, color=MUTED))

    # pin 3 — Vout (верх-центр)
    frags.append(rect(bx + bw / 2 - 17, by - 26, 34, 26, fill=lead, stroke="#555", sw=1.2, rx=3))
    frags.append(text(bx + bw / 2, by - 36, "3", size=15, bold=True))
    frags.append(text(bx + bw / 2, by - 58, "Vout · 3.3 В", size=17, color=FIELD, bold=True))

    frags.append(text(W / 2, H - 16,
                      "Вигляд згори: крапка — ключ 1-ї ноги. Це стандарт SOT-23, не переплутай Vin і Vout.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "pinout.svg"), W, H, *frags,
           title="XC6206 (662K) у корпусі SOT-23 — розпіновка")


# ── Фігура 2: типове підключення (пін-у-пін) ────────────────────────────────
def fig_wiring():
    W, H = 720, 340
    frags = []

    yrail = 90      # верхня шина Vin
    ygnd = 280      # нижня шина GND
    yout = 90       # вихідна шина на тому ж рівні, що вхід

    # чип посередині
    cx, cy, cw, ch = 320, 150, 90, 80
    frags.append(rect(cx, cy, cw, ch, fill="#2b2b2b", stroke="#111", sw=2, rx=8))
    frags.append(text(cx + cw / 2, cy + ch / 2 - 4, "662K", size=20, color="#f4f6f8", bold=True))
    frags.append(text(cx + cw / 2, cy + ch / 2 + 18, "LDO", size=12, color="#c9ccd1"))

    # виводи чипа: Vin ліворуч зверху, Vout праворуч зверху, GND по центру знизу
    pin_in = (cx, cy + 18)          # ліва грань
    pin_out = (cx + cw, cy + 18)    # права грань
    pin_gnd = (cx + cw / 2, cy + ch)  # низ

    # ── ЛІВОРУЧ: джерело + CIN ──
    srcx = 70
    frags.append(rect(srcx - 34, cy - 6, 68, 52, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(srcx, cy + 12, "Vin", size=14, bold=True))
    frags.append(text(srcx, cy + 30, "3.7–5 В", size=12, color=MUTED))
    frags.append(plus(srcx + 22, cy - 2))
    frags.append(minus(srcx + 22, cy + 44))

    # верхня шина від джерела до Vin-піна
    frags.append(line(srcx, cy - 6, srcx, yrail, color=POS, sw=2))
    frags.append(line(srcx, yrail, pin_in[0], yrail, color=POS, sw=2))
    frags.append(line(pin_in[0], yrail, pin_in[0], pin_in[1], color=POS, sw=2))
    # CIN
    cinx = 180
    frags.append(line(cinx, yrail, cinx, ygnd, color=INK, sw=1.5))
    frags.append(line(cinx - 12, 168, cinx + 12, 168, color=INK, sw=2.5))
    frags.append(line(cinx - 12, 178, cinx + 12, 178, color=INK, sw=2.5))
    frags.append(text(cinx + 40, 176, "CIN 1 мкФ", size=12, color=MUTED))

    # ── ПРАВОРУЧ: CL + навантаження ──
    # верхня вихідна шина
    frags.append(line(pin_out[0], pin_out[1], pin_out[0], yout, color=FIELD, sw=2))
    frags.append(line(pin_out[0], yout, 650, yout, color=FIELD, sw=2))
    # CL
    clx = 500
    frags.append(line(clx, yout, clx, ygnd, color=INK, sw=1.5))
    frags.append(line(clx - 12, 168, clx + 12, 168, color=INK, sw=2.5))
    frags.append(line(clx - 12, 178, clx + 12, 178, color=INK, sw=2.5))
    frags.append(text(clx + 38, 176, "CL 1 мкФ", size=12, color=MUTED))
    # навантаження
    loadx = 645
    frags.append(rect(loadx - 40, cy - 6, 80, 52, fill=FILL, stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(loadx, cy + 12, "3.3 В", size=14, color=FIELD, bold=True))
    frags.append(text(loadx, cy + 30, "МК / логіка", size=11, color=MUTED))
    frags.append(line(loadx, yout, loadx, cy - 6, color=FIELD, sw=2))

    # ── НИЖНЯ ШИНА GND (спільна) ──
    frags.append(line(srcx, cy + 44, srcx, ygnd, color=NEG, sw=2))
    frags.append(line(srcx, ygnd, loadx, ygnd, color=NEG, sw=2))
    frags.append(line(loadx, ygnd, loadx, cy + 46, color=NEG, sw=2))
    # gnd-пін чипа вниз
    frags.append(line(pin_gnd[0], pin_gnd[1], pin_gnd[0], ygnd, color=NEG, sw=2))
    # символ землі
    gx = 360
    frags.append(line(gx, ygnd, gx, ygnd + 14, color=NEG, sw=2))
    frags.append(line(gx - 14, ygnd + 14, gx + 14, ygnd + 14, color=NEG, sw=2.5))
    frags.append(line(gx - 8, ygnd + 20, gx + 8, ygnd + 20, color=NEG, sw=2.5))
    frags.append(line(gx - 3, ygnd + 26, gx + 3, ygnd + 26, color=NEG, sw=2.5))

    # підписи пінів чипа
    frags.append(text(cx - 24, cy + 8, "Vin", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(cx + cw + 26, cy + 8, "Vout", size=12, color=FIELD, bold=True, anchor="middle"))
    frags.append(text(cx + cw / 2 + 34, cy + ch - 6, "GND", size=12, color=NEG, bold=True, anchor="start"))

    frags.append(text(W / 2, H - 12,
                      "Три ноги, дві «кришки». Конденсатори — впритул до чипа.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "wiring.svg"), W, H, *frags,
           title="XC6206 — типове підключення 3.3 В")


# ── Фігура 3 (для hist-вставки): чому CMOS-прохідник б'є біполярний ──────────
def fig_bipolar_vs_cmos():
    W, H = 760, 470
    frags = []

    # заголовок-пояснення під title
    frags.append(text(W / 2, 52,
                      "Той самий прохідний ключ між входом і виходом — два способи його побудувати.",
                      size=13, color=MUTED))

    # дві колонки
    colw = 320
    lx = 40            # ліва колонка (біполяр)
    rx = W - 40 - colw  # права (CMOS)
    top = 80

    # ── ЛІВА: біполярний PNP ──
    frags.append(rect(lx, top, colw, 300, fill="#fbeeee", stroke=POS, sw=1.6, rx=10))
    frags.append(text(lx + colw / 2, top + 26, "Біполярний (PNP)", size=17, color=POS, bold=True))
    frags.append(text(lx + colw / 2, top + 46, "78xx · 1117-клас", size=12, color=MUTED))

    # символ транзистора (спрощено): вхід згори, вихід знизу, база збоку зі струмом
    tcx, tcy = lx + colw / 2, top + 130
    frags.append(line(tcx, top + 62, tcx, tcy - 26, color=POS, sw=2.5))          # Vin вниз
    frags.append(text(lx + colw / 2, top + 74, "Vin", size=12, color=POS, bold=True, anchor="start"))
    frags.append(circle(tcx, tcy, 26, fill="#ffffff", stroke=POS, sw=2))
    frags.append(text(tcx, tcy + 5, "Q", size=18, color=POS, bold=True))
    frags.append(line(tcx, tcy + 26, tcx, tcy + 60, color=FIELD, sw=2.5))        # Vout вниз
    frags.append(text(tcx, tcy + 82, "Vout", size=12, color=FIELD, bold=True))
    # струм бази — постійно тече в керування
    frags.append(arrow(lx + 40, tcy, tcx - 26, tcy, color=NEG, sw=2))
    frags.append(text(lx + 46, tcy - 12, "струм бази", size=12, color=NEG, bold=True, anchor="start"))
    frags.append(text(lx + 46, tcy + 20, "тече завжди", size=11, color=MUTED, anchor="start"))

    # два висновки
    b1 = fitbox(lx + 22, top + 210, colw - 44, 34,
                "I_q ~ міліампери (частина струму йде в базу)",
                size=12, fill="#ffffff", stroke=POS, color=INK)
    frags.append(b1)
    b2 = fitbox(lx + 22, top + 252, colw - 44, 34,
                "Dropout ~ 1 В (V_насичення + опір)",
                size=12, fill="#ffffff", stroke=POS, color=INK)
    frags.append(b2)

    # ── ПРАВА: CMOS (PMOS) ──
    frags.append(rect(rx, top, colw, 300, fill="#eef4ff", stroke=NEG, sw=1.6, rx=10))
    frags.append(text(rx + colw / 2, top + 26, "CMOS (PMOS)", size=17, color=NEG, bold=True))
    frags.append(text(rx + colw / 2, top + 46, "XC6206 · мікропотужний LDO", size=12, color=MUTED))

    mcx, mcy = rx + colw / 2, top + 130
    frags.append(line(mcx, top + 62, mcx, mcy - 26, color=POS, sw=2.5))
    frags.append(text(rx + colw / 2, top + 74, "Vin", size=12, color=POS, bold=True, anchor="start"))
    frags.append(rect(mcx - 26, mcy - 26, 52, 52, fill="#ffffff", stroke=NEG, sw=2, rx=6))
    frags.append(text(mcx, mcy + 5, "M", size=18, color=NEG, bold=True))
    frags.append(line(mcx, mcy + 26, mcx, mcy + 60, color=FIELD, sw=2.5))
    frags.append(text(mcx, mcy + 82, "Vout", size=12, color=FIELD, bold=True))
    # затвор — напруга, струму нема
    frags.append(line(rx + 40, mcy, mcx - 26, mcy, color=NEG, sw=2, dash="6 4"))
    frags.append(text(rx + 46, mcy - 12, "затвор", size=12, color=NEG, bold=True, anchor="start"))
    frags.append(text(rx + 46, mcy + 20, "лише напруга,", size=11, color=MUTED, anchor="start"))
    frags.append(text(rx + 46, mcy + 36, "струму ~0", size=11, color=MUTED, anchor="start"))

    b3 = fitbox(rx + 22, top + 210, colw - 44, 34,
                "I_q ~ 1 мкА (у затвор струм не тече)",
                size=12, fill="#ffffff", stroke=NEG, color=INK)
    frags.append(b3)
    b4 = fitbox(rx + 22, top + 252, colw - 44, 34,
                "Dropout ~ 0.25 В (лише R_on · I)",
                size=12, fill="#ffffff", stroke=NEG, color=INK)
    frags.append(b4)

    # нижній підсумок
    frags.append(text(W / 2, H - 22,
                      "Керувати польовим ключем майже не коштує струму — звідси й мікроамперний спокій, і мале падіння.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "bipolar-vs-cmos.svg"), W, H, *frags,
           title="Прохідний елемент: біполярний проти CMOS")


# ── Фігура 4 (для hist-вставки): лінія часу класу ───────────────────────────
def fig_timeline():
    W, H = 780, 300
    frags = []

    y = 150
    x0, x1 = 60, W - 60
    frags.append(line(x0, y, x1, y, color=INK, sw=2.5))
    frags.append(arrow(x1 - 2, y, x1 + 8, y, color=INK, sw=2.5))

    # вузли: (частка 0..1, рік, підпис-2рядки, зверху?)
    nodes = [
        (0.00, "1967", "μA723\nперший IC-регулятор", True),
        (0.16, "1969", "LM109\nперший 3-вивідний", False),
        (0.30, "1972", "78xx\nфіксовані біполярні", True),
        (0.46, "1977", "перший LDO\n(Р. Добкін)", False),
        (0.66, "1990-ті", "перехід на CMOS\nмікроамперний I_q", True),
        (0.90, "XC6206", "мікропотужний\nCMOS-LDO", False),
    ]
    for frac, yr, lbl, up in nodes:
        x = x0 + (x1 - x0) * frac
        frags.append(circle(x, y, 7, fill=BG, stroke=INK, sw=2.5))
        frags.append(text(x, y + (-18 if up else 26), yr, size=14, bold=True))
        ly = y - 40 if up else y + 44
        frags.append(mtext(x, ly, lbl, size=11, color=MUTED, lh=1.25))

    frags.append(text(W / 2, H - 14,
                      "Не одна людина й не один рік: ідея регулятора визрівала два десятиліття, перш ніж CMOS зробив спокій мікроамперним.",
                      size=11, color=MUTED))

    render(os.path.join(IMG, "ldo-timeline.svg"), W, H, *frags,
           title="Родовід мікропотужного CMOS-LDO")


if __name__ == "__main__":
    fig_pinout()
    fig_wiring()
    fig_bipolar_vs_cmos()
    fig_timeline()
    print("figs done")
