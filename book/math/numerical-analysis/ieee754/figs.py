# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# Локальні кольори полів — три поля формату мають читатися окремо.
SIGN = NEG            # знак — холодний синій
EXP  = "#7a3fb0"      # порядок — фіолетовий (окремо від «−»)
MANT = "#b07d1f"      # мантиса — теплий бурштин


# ── Фігура 1: побітове декодування одного float32 ────────────────────────────
# ЯДРО теми. Беремо конкретний запис -3.5 і відновлюємо значення з трьох полів:
# знак дає множник, порядок дає степінь двійки (через зсув 127), мантиса дає
# число в [1,2) (через приховану 1). Унизу — підсумкова формула.

def fig_decode():
    W, H = 980, 600
    parts = []

    # — бітовий рядок: 1 | 10000000 | 11000…0 —
    bits = "1" + "10000000" + "11000000000000000000000"
    fields = [SIGN] + [EXP] * 8 + [MANT] * 23
    bw, x0, y0, bh = 25.0, 90.0, 84.0, 32.0
    for i, ch in enumerate(bits):
        x = x0 + i * bw
        col = fields[i]
        fill = {SIGN: "#eaf0fd", EXP: "#f1e9f7", MANT: "#f7efdf"}[col]
        parts.append(rect(x, y0, bw, bh, fill=fill, stroke=INK, sw=1.3, rx=0))
        parts.append(text(x + bw / 2, y0 + 22, ch, size=14, color=col, bold=True))
    # індекси крайніх бітів (31 — знак, 30…23 — порядок, 22…0 — мантиса)
    for idx, lbl in [(0, "31"), (1, "30"), (8, "23"), (9, "22"), (31, "0")]:
        parts.append(text(x0 + idx * bw + bw / 2, y0 - 8, lbl, size=10, color=MUTED))

    # — фігурні підписи полів під рядком —
    ytick = y0 + bh + 6
    def brace(xa, xb, lbl, col):
        out = line(xa, ytick, xb, ytick, color=col, sw=1.6)
        out += text((xa + xb) / 2, ytick + 16, lbl, size=12, color=col, bold=True)
        return out
    parts.append(brace(x0,            x0 + bw,       "знак", SIGN))
    parts.append(brace(x0 + bw,       x0 + 9 * bw,   "порядок — 8 бітів", EXP))
    parts.append(brace(x0 + 9 * bw,   x0 + 32 * bw,  "мантиса (дробова частина) — 23 біти", MANT))

    # — три картки розбору —
    cy = 250
    s1 = ["біт = 1", "1 → мінус", "(−1)¹ = −1"]
    s2 = ["10000000₂ = 128", "− зсув 127", "128 − 127 = 1", "степінь 2¹"]
    s3 = ["11000…₂ → .11₂", "+ прихована 1", "1.11₂ = 1.75", "(½ + ¼)"]
    cards = [(226.5, "1) Знак", s1, SIGN, "#eaf0fd"),
             (490.0, "2) Порядок", s2, EXP, "#f1e9f7"),
             (760.0, "3) Мантиса", s3, MANT, "#f7efdf")]
    cw, ch2 = 250.0, 150.0
    for ccx, head, lines, col, fill in cards:
        parts.append(rect(ccx - cw / 2, cy - ch2 / 2, cw, ch2, fill=fill, stroke=col, sw=1.6, rx=8))
        parts.append(text(ccx, cy - ch2 / 2 + 22, head, size=14, color=INK, bold=True))
        ly = cy - ch2 / 2 + 48
        for ln in lines:
            parts.append(text(ccx, ly, ln, size=12.5, color=INK))
            ly += 23
        # стрілка від картки до підсумку
        parts.append(arrow(ccx, cy + ch2 / 2, ccx, 366, color=col, sw=1.6))

    # — підсумкова формула —
    parts.append(rect(90, 368, 800, 50, fill="#eaf6ec", stroke=FIELD, sw=2.0, rx=8))
    parts.append(text(490, 390, "значення = (−1)ˢ × 1.мантиса × 2^(порядок − 127)",
                      size=14, color=INK, bold=True))
    parts.append(text(490, 410, "= (−1) × 1.75 × 2¹ = −3.5", size=14, color=FIELD, bold=True))

    # — зворотний хід —
    parts.append(text(490, 470, "Зворотний хід — той самий ланцюг навпаки:",
                      size=12.5, color=INK, bold=True))
    parts.append(text(490, 492, "винести найближчий степінь двійки · відкинути провідну 1 · додати зсув 127",
                      size=12, color=MUTED))

    title = "Один float32 по бітах: як 32 нулі та одиниці стають числом −3.5"
    render(os.path.join(OUT, 'decode.svg'), W, H, *parts, title=title)


# ── Фігура 2: поле порядку як перемикач чотирьох режимів ──────────────────────
# ЯДРО теми про краї. Ті самі 8 бітів задають режим: 0 → нуль/денормаль,
# 1…254 → нормальні, 255 → ∞/NaN. Унизу — числова вісь біля нуля, де денормалі
# рівним кроком «дотягують» від найменшого нормального до нуля.

def fig_exponent_map():
    W, H = 980, 580
    parts = []

    # — три заголовки діапазонів порядку —
    heads = [(137.4, 154.8, "порядок = 0", "(біти 00000000)", EXP),
             (490.0, 550.4, "порядок = 1 … 254", "(звичайний діапазон)", FIELD),
             (842.6, 154.8, "порядок = 255", "(біти 11111111)", POS)]
    hx = {137.4: 60.0, 490.0: 214.8, 842.6: 765.2}
    for cx, w, lbl, sub, col in heads:
        fill = {EXP: "#f1e9f7", FIELD: "#eaf6ec", POS: "#fdecea"}[col]
        parts.append(rect(hx[cx], 84, w, 40, fill=fill, stroke=col, sw=1.8, rx=6))
        parts.append(text(cx, 102, lbl, size=13, color=col, bold=True))
        parts.append(text(cx, 118, sub, size=11, color=MUTED))
        parts.append(arrow(cx, 124, cx, 152, color=col, sw=1.6))

    # — шість карток (2 ряди × 3 стовпці) —
    def card(cx, top, t1, t2, t3, col):
        cw, chh = 250.0, 92.0
        parts.append(rect(cx - cw / 2, top, cw, chh, fill=BG, stroke=col, sw=1.6, rx=8))
        parts.append(text(cx, top + 20, t1, size=12.5, color=col, bold=True))
        parts.append(text(cx, top + 40, t2, size=11.5, color=INK))
        parts.append(text(cx, top + 57, t3, size=11.5, color=INK))

    card(137.4, 154, "мантиса = 0  →  ±0", "рівно нуль", "(є і +0, і −0)", EXP)
    card(137.4, 260, "мантиса ≠ 0  →  денормаль", "0.мантиса × 2⁻¹²⁶", "(приховано 0, не 1)", EXP)
    card(490.0, 154, "будь-яка мантиса", "1.мантиса × 2^(e−127)", "приховано провідну 1", FIELD)
    card(490.0, 260, "майже всі числа формату", "звичайна арифметика", "(широка середина)", FIELD)
    card(842.6, 154, "мантиса = 0  →  ±∞", "переповнення,", "ділення на 0", POS)
    card(842.6, 260, "мантиса ≠ 0  →  NaN", "0/0, √(−1);", "заразний", POS)

    # — числова вісь біля нуля —
    parts.append(text(490, 396, "Числова вісь біля нуля: денормалі рівним кроком «дотягують» до 0",
                      size=12.5, color=INK, bold=True))
    ay = 416
    parts.append(line(60, ay, 920, ay, color=INK, sw=2))
    parts.append(arrow(910, ay, 932, ay, color=INK, sw=2))
    parts.append(text(60, ay + 22, "0", size=13, color=INK, bold=True))
    parts.append(line(60, ay - 7, 60, ay + 7, color=INK, sw=2))

    # денормалі — рівний крок (синій), межа на 2^-126
    x_norm0 = 404.0
    n = 9
    for i in range(1, n + 1):
        x = 60 + (x_norm0 - 60) * i / n
        parts.append(line(x, ay - 6, x, ay + 6, color=EXP, sw=1.6))
    parts.append(text(257.8, 402, "денормалі: рівний крок 2⁻¹⁴⁹", size=11.5, color=EXP, bold=True))
    parts.append(text(257.8, 440, "плавне згасання до нуля", size=11, color=EXP))
    parts.append(text(120, 456, "2⁻¹⁴⁹ (найменше)", size=10.5, color=EXP))

    # нормальні — крок подвоюється (зелений)
    xs = [404.0, 455.6, 530.4, 638.9, 796.2]
    for x in xs:
        parts.append(line(x, ay - 8, x, ay + 8, color=FIELD, sw=1.8))
    parts.append(text(662, 400, "нормальні: крок подвоюється щопорядку", size=11.5, color=FIELD, bold=True))

    parts.append(line(x_norm0, 390, x_norm0, 430, color=MUTED, sw=1.4, dash="4 3"))
    parts.append(text(x_norm0, 446, "2⁻¹²⁶ (найменше нормальне)", size=10.5, color=MUTED))

    # — нижня плашка-висновок —
    parts.append(rect(60, 520, 860, 36, fill="#fdf6e6", stroke=MANT, sw=1.4, rx=8))
    parts.append(text(490, 543,
                      "Без денормалей усе між 0 і 2⁻¹²⁶ різко падало б у нуль — «діра», де віднімання близьких чисел брехало б.",
                      size=12, color=INK))

    title = "Поле порядку — перемикач: ті самі 8 бітів задають чотири режими"
    render(os.path.join(OUT, 'exponent-map.svg'), W, H, *parts, title=title)


if __name__ == '__main__':
    fig_decode()
    fig_exponent_map()
    print('OK: 2 figures ->', OUT)
