# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── positional: розряд = степінь основи, беремо ваги одиниць ───────────────────
# Ідея: над кожним бітом — його вага (степінь 2); десяткове значення = сума ваг
# тих розрядів, де стоїть 1. Показуємо це на 10110110 = 182.

def fig_positional():
    W, H = 720, 300
    bits = "10110110"
    n = len(bits)
    bw, gap = 60, 8
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    yb = 120                       # верх клітинок
    bh = 54
    p = []

    weights = [2 ** (n - 1 - i) for i in range(n)]
    for i, ch in enumerate(bits):
        x = x0 + i * (bw + gap)
        on = ch == "1"
        col = POS if on else NEG
        fill = "#fdecea" if on else "#eaf0fd"
        # вага-степінь над клітинкою
        p.append(text(x + bw / 2, yb - 26, "2%s" % _sup(n - 1 - i), size=12, color=MUTED))
        p.append(text(x + bw / 2, yb - 11, "=%d" % weights[i], size=11, color=MUTED))
        # сама клітинка з бітом
        p.append(rect(x, yb, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, yb + bh / 2 + 7, ch, size=22, color=col, bold=True))
        # внесок розряду під клітинкою
        contrib = str(weights[i]) if on else "0"
        p.append(text(x + bw / 2, yb + bh + 24, contrib, size=13,
                      color=FIELD if on else MUTED, bold=on))

    # підсумкова сума
    s = " + ".join(str(weights[i]) for i, ch in enumerate(bits) if ch == "1")
    p.append(text(W / 2, yb + bh + 64, "%s = 182" % s, size=17, color=FIELD, bold=True))

    render(os.path.join(OUT, "positional.svg"), W, H, *p,
           title="Читаємо двійкове: сума ваг тих розрядів, де стоїть 1")


# ── dec-to-bin: ділення на 2, остачі знизу вгору ──────────────────────────────
# Ідея: стовпчик послідовних ділень 182 на 2; остача кожного кроку — біт,
# а прочитані знизу вгору остачі дають двійковий запис.

def fig_dec_to_bin():
    W, H = 700, 400
    p = []
    x_div, x_rem = 250, 470
    y0, dy = 70, 36
    steps = []
    v = 182
    while v > 0:
        steps.append((v, v // 2, v % 2))
        v //= 2

    # заголовки стовпців
    p.append(text(x_div, y0 - 24, "ділимо на 2", size=12, color=INK, bold=True))
    p.append(text(x_rem, y0 - 24, "остача (біт)", size=12, color=INK, bold=True))

    for i, (a, q, r) in enumerate(steps):
        y = y0 + i * dy
        p.append(text(x_div, y, "%d ÷ 2 = %d" % (a, q), size=13, color=INK))
        rc = POS if r else NEG
        p.append(text(x_rem, y, str(r), size=14, color=rc, bold=True))

    # стрілка «читати знизу вгору» уздовж стовпця остач
    ytop, ybot = y0 - 6, y0 + (len(steps) - 1) * dy + 6
    ax = x_rem + 60
    p.append(arrow(ax, ybot, ax, ytop, color=FIELD, sw=2))
    p.append(text(ax + 12, (ytop + ybot) / 2, "читати", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(ax + 12, (ytop + ybot) / 2 + 15, "знизу вгору", size=11, color=FIELD, anchor="start", bold=True))

    # результат
    res = "".join(str(r) for _, _, r in reversed(steps))
    p.append(text(W / 2, ybot + 44, "= %s" % res, size=18, color=FIELD, bold=True))

    render(os.path.join(OUT, "dec-to-bin.svg"), W, H, *p,
           title="Десяткове → двійкове: остачі від ділення на 2, знизу вгору")


# ── readability: довга стіна бітів проти короткого hex ────────────────────────
# Ідея: одне 32-бітне значення двома записами — стіна з 32 знаків і ті самі
# вісім hex-цифр; візуально видно, чому hex рятує очі.

def fig_readability():
    W, H = 720, 250
    p = []
    binstr = "11011110101011011011111011101111"   # 0xDEADBEEF
    hexstr = "DE AD BE EF"

    # верх: двійкова стіна — один моноширинний рядок із 32 знаків
    p.append(text(W / 2, 70, "двійково — 32 знаки:", size=12, color=MUTED))
    p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="18" '
             'fill="%s" text-anchor="middle" letter-spacing="1.5">%s</text>'
             % (W / 2, 100, POS, binstr))
    p.append(text(W / 2, 128, "легко збитися й перерахувати", size=11, color=POS, italic=True))

    # стрілка-перехід
    p.append(arrow(W / 2, 150, W / 2, 178, color=INK, sw=2))

    # низ: hex
    p.append(text(W / 2, 200, "те саме шістнадцятково — 8 знаків:", size=12, color=MUTED))
    p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="24" '
             'fill="%s" text-anchor="middle" font-weight="700" letter-spacing="2">0x%s</text>'
             % (W / 2, 230, FIELD, hexstr.replace(" ", "")))

    render(os.path.join(OUT, "readability.svg"), W, H, *p,
           title="Двійкове задовге для ока — рятує шістнадцяткова")


# ── hex-digits: 16 цифр і їхні півбайти ───────────────────────────────────────
# Ідея: таблиця всіх hex-цифр поряд із 4-бітним кодом; видно, що 16 = 2⁴ і кожна
# цифра — рівно чотири біти (півбайт).

def fig_hex_digits():
    W, H = 720, 380
    p = []
    cols, rows = 4, 4
    cw, ch = 150, 56
    gx, gy = 18, 14
    total_w = cols * cw + (cols - 1) * gx
    x0 = (W - total_w) / 2
    y0 = 70
    for v in range(16):
        c = v % cols
        r = v // cols
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        digit = "0123456789ABCDEF"[v]
        col = POS if v >= 10 else INK
        p.append(rect(x, y, cw, ch, fill=FILL, stroke=LINE, sw=1.4))
        p.append(text(x + 34, y + ch / 2 + 7, digit, size=22, color=col, bold=True))
        p.append(line(x + 64, y + 8, x + 64, y + ch - 8, color="#d7dce3", sw=1))
        p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="15" '
                 'fill="%s" text-anchor="start">%s</text>'
                 % (x + 76, y + ch / 2 + 6, INK, format(v, "04b")))

    p.append(text(W / 2, y0 + rows * (ch + gy) + 10,
                  "16 = 2⁴ → одна цифра = чотири біти (півбайт)",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "hex-digits.svg"), W, H, *p,
           title="Шістнадцять цифр (0–9, A–F) і їхні 4-бітні коди")


# ── grouping: байт → дві четвірки → дві hex-цифри ─────────────────────────────
# Ідея: байт 10110110 ділиться рискою на 1011 і 0110; кожна четвірка стає однією
# hex-цифрою (B і 6) → 0xB6. Без жодних обчислень, саме групування.

def fig_grouping():
    W, H = 700, 280
    p = []
    yb = 90
    bw, bh = 46, 50
    groups = [("1011", "B", 11), ("0110", "6", 6)]
    gap_in, gap_out = 6, 40
    group_w = 4 * bw + 3 * gap_in
    total = 2 * group_w + gap_out
    x0 = (W - total) / 2

    hex_centers = []
    for gi, (nib, hd, val) in enumerate(groups):
        gx = x0 + gi * (group_w + gap_out)
        # рамка четвірки
        p.append(rect(gx - 6, yb - 8, group_w + 12, bh + 16, fill="#f6fbff",
                      stroke="#c9d6f0", sw=1.4))
        for i, ch in enumerate(nib):
            x = gx + i * (bw + gap_in)
            on = ch == "1"
            col = POS if on else NEG
            p.append(rect(x, yb, bw, bh, fill="#fdecea" if on else "#eaf0fd", stroke=col, sw=1.8))
            p.append(text(x + bw / 2, yb + bh / 2 + 7, ch, size=20, color=col, bold=True))
        cx = gx + group_w / 2
        hex_centers.append((cx, hd, val))
        # стрілка вниз до hex-цифри
        p.append(arrow(cx, yb + bh + 8, cx, yb + bh + 40, color=INK, sw=1.8))
        p.append(text(cx, yb + bh + 70, hd, size=26, color=FIELD, bold=True))
        p.append(text(cx, yb + bh + 90, "(%d)" % val, size=11, color=MUTED))

    # підсумок 0xB6
    p.append(text(W / 2, yb + bh + 128, "0xB6  =  182", size=18, color=FIELD, bold=True))

    render(os.path.join(OUT, "grouping.svg"), W, H, *p,
           title="Двійкове → hex: групуй по чотири, кожна четвірка — одна цифра")


# ── допоміжне: верхній індекс зі звичайних цифр ───────────────────────────────
_SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
        "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def _sup(n):
    return "".join(_SUP[c] for c in str(n))


if __name__ == "__main__":
    fig_positional()
    fig_dec_to_bin()
    fig_readability()
    fig_hex_digits()
    fig_grouping()
    print("OK: figures written to", OUT)
