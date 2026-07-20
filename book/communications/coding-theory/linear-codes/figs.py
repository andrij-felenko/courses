# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# наскрізний код [5,2]: C = {00000, 11010, 01101, 10111}
WORDS = ["00000", "11010", "01101", "10111"]

# колір на кожне кодове слово (зеро — зелене, решта — три спокійні тони)
WCOL = {
    "00000": ("#eafaf0", "#27ae60", "#1e8449"),   # нуль — особливий
    "11010": ("#eef4ff", "#2457d6", "#1c40a0"),
    "01101": ("#fdf1e5", "#c2740f", "#9a5a0b"),
    "10111": ("#f4e9fb", "#7b3fb0", "#5f2f89"),
}
HL = "#fff7d6"


def xor(a, b):
    return "".join("1" if p != q else "0" for p, q in zip(a, b))


def wcell(x, y, w, h, val, sw=1.6, zero_ring=False):
    fill, strk, tc = WCOL[val]
    s = 2.6 if zero_ring else sw
    out = rect(x, y, w, h, fill=fill, stroke=strk, sw=s, rx=5)
    out += text(x + w / 2, y + h / 2 + 5, val, size=14, color=tc, bold=True)
    return out


# ── Fig 1: код замкнений щодо XOR — таблиця 4×4, усі клітини знову слова коду ──
def fig_subspace():
    W, H = 780, 470
    p = []
    cw, ch = 88, 44
    tx = 250            # лівий край стовпця даних
    ty = 150            # верх рядка даних
    hcw = 92            # ширина клітин-заголовків

    # ріг «⊕»
    p.append(rect(tx - hcw, ty - 46, hcw, 46, fill="#f0f2f5", stroke=MUTED, sw=1.4, rx=5))
    p.append(text(tx - hcw / 2, ty - 46 / 2 + 6, "⊕", size=22, color=INK, bold=True))

    # заголовки стовпців (згори) і рядків (зліва)
    for j, wj in enumerate(WORDS):
        fill, strk, tc = WCOL[wj]
        # верхній заголовок
        p.append(rect(tx + j * cw, ty - 46, cw, 46, fill=fill, stroke=strk, sw=1.6, rx=5))
        p.append(text(tx + j * cw + cw / 2, ty - 46 / 2 + 6, wj, size=13.5, color=tc, bold=True))
        # лівий заголовок
        p.append(rect(tx - hcw, ty + j * ch, hcw, ch, fill=fill, stroke=strk, sw=1.6, rx=5))
        p.append(text(tx - hcw / 2, ty + j * ch + ch / 2 + 5, wj, size=13.5, color=tc, bold=True))

    # тіло таблиці
    for i, wi in enumerate(WORDS):
        for j, wj in enumerate(WORDS):
            val = xor(wi, wj)
            x = tx + j * cw
            y = ty + i * ch
            p.append(wcell(x, y, cw, ch, val, zero_ring=(i == j)))

    # підпис під таблицею
    p.append(text(tx + 2 * cw, ty + 4 * ch + 30,
                  "кожна клітина — знову одне з чотирьох слів коду  →  набір замкнений щодо ⊕",
                  size=12.5, color=INK, bold=True))
    p.append(text(tx + 2 * cw, ty + 4 * ch + 52,
                  "діагональ (обведена) — усюди 00000: нуль неминуче в коді",
                  size=11.5, color="#1e8449", italic=True))

    box, bw, bh = textbox(W / 2, 74,
                          "4 слова = усі XOR-и двох твірних 11010 і 01101 — це підпростір",
                          size=13.5, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "subspace.svg"), W, H, *p,
           title="Лінійний код замкнений щодо XOR — тобто є підпростором")


# ── Fig 2: зсув коду на кодове слово переставляє його в себе ───────────────────
def fig_translation():
    W, H = 760, 500
    p = []
    bw, bh = 118, 44
    lx, rx = 190, 560          # центри лівого/правого стовпців
    y0, ystep = 132, 74
    shift = "11010"
    perm = {0: 1, 1: 0, 2: 3, 3: 2}   # куди їде i-те слово (00000↔11010, 01101↔10111)

    # заголовки стовпців
    p.append(text(lx, y0 - 40, "код C", size=14, color=INK, bold=True))
    p.append(text(rx, y0 - 40, "після ⊕ 11010", size=14, color=INK, bold=True))
    p.append(text(rx, y0 - 22, "той самий набір, лише переставлений", size=11, color=MUTED, italic=True))

    def cy(i):
        return y0 + i * ystep + bh / 2

    # ліві й праві клітини (обидва стовпці — той самий набір у тому самому порядку)
    for i, w in enumerate(WORDS):
        y = y0 + i * ystep
        p.append(wcell(lx - bw / 2, y, bw, bh, w))
        p.append(wcell(rx - bw / 2, y, bw, bh, w))

    # стрілки-перестановка: L_i → R_perm(i)
    for i in range(4):
        j = perm[i]
        x1 = lx + bw / 2 + 8
        x2 = rx - bw / 2 - 8
        fill, strk, tc = WCOL[WORDS[i]]
        p.append(arrow(x1, cy(i), x2, cy(j), color=strk, sw=1.8))

    # позначка операції посередині
    p.append(text((lx + rx) / 2, y0 - 6, "⊕ 11010", size=13, color=POS, bold=True))

    # висновок
    box, bwid, bh2 = textbox(W / 2, y0 + 4 * ystep + 10,
                             ["Зсув на кодове слово лише переставив слова — набір не змінився.",
                              "Тож краєвид відстаней з будь-якого слова такий самий, як із нуля:",
                              "мінімальна відстань d = мінімальна вага ненульового слова (тут 3)."],
                             size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=13)
    p.append(box)

    render(os.path.join(OUT, "translation.svg"), W, H, *p,
           title="Код інваріантний до зсуву на своє слово")


# ── Fig 3: родина лінійних кодів — парасоля над блоковими й згортковими ────────
def node(cx, top, w, lines, fill, strk, tc=INK, size=13, h=None):
    """Рамка-вузол із центром по cx, верхом top; повертає (svg, h, bottom_y)."""
    if h is None:
        n = 1 if isinstance(lines, str) else len(lines)
        h = 30 + n * 18
    frag = fitbox(cx - w / 2, top, w, h, lines, size=size, fill=fill, stroke=strk,
                  sw=2.0, bold=True, color=tc)
    return frag, h, top + h


def fig_family():
    W, H = 1040, 620
    p = []

    # парасоля
    uw = 470
    ucx = W / 2
    utop = 60
    frag, uh, ubot = node(ucx, utop, uw,
                          ["ЛІНІЙНІ КОДИ", "код — підпростір над полем GF(q)"],
                          "#f6f4ec", INK, size=14, h=62)
    p.append(frag)

    # дві головні гілки
    lcx, rcx = 300, 760
    btop = 176
    bw = 380
    fL, hL, bbotL = node(lcx, btop, bw,
                         ["Блокові коди", "слова фіксованої довжини"],
                         "#eef4ff", "#2457d6", tc="#1c40a0", size=13.5, h=58)
    fR, hR, bbotR = node(rcx, btop, bw,
                         ["Згорткові коди", "вихід памʼятає попередні блоки"],
                         "#fdf1e5", "#c2740f", tc="#9a5a0b", size=13.5, h=58)
    p.append(fL); p.append(fR)

    # лінії від парасолі до гілок
    p.append(line(ucx, ubot, ucx, btop - 14, color=MUTED, sw=1.8))
    p.append(line(lcx, btop - 14, rcx, btop - 14, color=MUTED, sw=1.8))
    p.append(line(lcx, btop - 14, lcx, btop - 2, color="#2457d6", sw=1.8))
    p.append(line(rcx, btop - 14, rcx, btop - 2, color="#c2740f", sw=1.8))

    # листки блокових кодів (стек під лівою гілкою)
    leaves = [
        "Геммінг · SECDED",
        "Циклічні: CRC · BCH · Рід–Соломон",
        "Рід–Маллер",
        "LDPC · полярні (сучасні)",
    ]
    ltop = 300
    lw = 356
    lh = 40
    lgap = 12
    for k, s in enumerate(leaves):
        y = ltop + k * (lh + lgap)
        p.append(fitbox(lcx - lw / 2, y, lw, lh, s, size=12.5,
                        fill="#f3f7ff", stroke="#5b7fd6", sw=1.5, bold=True, color="#1c40a0"))
    # вертикаль-хребет від лівої гілки до листків + полички
    spine_x = lcx - lw / 2 - 22
    p.append(line(spine_x, bbotL, spine_x, ltop + (len(leaves) - 1) * (lh + lgap) + lh / 2,
                  color="#5b7fd6", sw=1.6))
    p.append(line(lcx, bbotL, spine_x, bbotL, color="#5b7fd6", sw=1.6))
    for k in range(len(leaves)):
        y = ltop + k * (lh + lgap) + lh / 2
        p.append(line(spine_x, y, lcx - lw / 2 - 2, y, color="#5b7fd6", sw=1.6))

    # нотатка під згортковими
    p.append(fitbox(rcx - 356 / 2, 300, 356, 58,
                    ["лінійний фільтр над потоком бітів;",
                     "живуть у Wi-Fi, супутниках, глибокому космосі"],
                    size=12, fill="#fef6ec", stroke="#d79a4e", sw=1.5, color="#9a5a0b"))
    p.append(line(rcx, bbotR, rcx, 300 - 2, color="#c2740f", sw=1.6))

    # вісь поля (спільна для обох гілок)
    p.append(fitbox(rcx - 356 / 2, 384, 356, 44,
                    "двійкові GF(2) — або над більшим полем GF(q)",
                    size=12, fill="#eafaf0", stroke="#27ae60", sw=1.5, color="#1e8449", bold=True))

    # осторонь — нелінійні коди (за пунктирною межею)
    p.append(line(60, 486, W - 60, 486, color=MUTED, sw=1.4, dash="6 5"))
    p.append(text(W / 2, 506, "— межа лінійності —", size=11.5, color=MUTED, italic=True))
    p.append(fitbox(W / 2 - 470 / 2, 520, 470, 58,
                    ["Нелінійні коди — існують і зрідка щільніші (Нордстром–Робінсон:",
                     "256 слів там, де жоден лінійний не вмістить), але без базису й синдрому."],
                    size=12, fill="#fdecea", stroke=POS, sw=1.6, color="#a12b1e"))

    render(os.path.join(OUT, "family.svg"), W, H, *p,
           title="Родина лінійних кодів: одна парасоля над майже всім кодуванням")


# ── Fig 4: дуальна пара — код повторення [3,1] ↔ код парності [3,2] ────────────
def _matcard(cx, top, pw, title, codeset, mat_lines, dim_txt, col, math=None):
    """Картка коду: заголовок, набір слів, матриця в рамці, підпис розмірності."""
    fill, strk, tc = col
    out = []
    out.append(rect(cx - pw / 2, top, pw, 48, fill=fill, stroke=strk, sw=2, rx=7))
    out.append(text(cx, top + 30, title, size=15, color=tc, bold=True))
    out.append(text(cx, top + 78, codeset, size=12.5, color=INK))
    # рамка матриці
    mw = 176
    mh = 26 + len(mat_lines) * 26
    mx, my = cx - mw / 2, top + 98
    out.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=strk, sw=1.6, rx=6))
    out.append(text(mx - 4, my + mh / 2 + 6, "[", size=int(mh * 0.9), color=strk, anchor="end"))
    out.append(text(mx + mw + 4, my + mh / 2 + 6, "]", size=int(mh * 0.9), color=strk, anchor="start"))
    ly = my + 22
    for ln in mat_lines:
        out.append(text(cx, ly, ln, size=15, color=INK, bold=True))
        ly += 26
    out.append(text(cx, my + mh + 24, dim_txt, size=12.5, color=tc, bold=True))
    return out, my + mh + 24


def fig_dual_pair():
    W, H = 940, 560
    p = []
    BLUE = ("#eef4ff", "#2457d6", "#1c40a0")
    ORNG = ("#fdf1e5", "#c2740f", "#9a5a0b")

    box, bw, bh = textbox(W / 2, 70,
                          "G одного коду = H другого — і навпаки; виміри складаються в n = 3",
                          size=13.5, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)

    top = 128
    lcx, rcx = 246, 694
    fragL, botL = _matcard(lcx, top, 320, "код повторення [3,1]",
                           "C = { 000,  111 }", ["1  1  1"], "твірна G   (dim = 1)", BLUE)
    fragR, botR = _matcard(rcx, top, 320, "код парності [3,2]",
                           "C = { 000, 110, 101, 011 }",
                           ["1  0  1", "0  1  1"], "твірна G   (dim = 2)", ORNG)
    p += fragL
    p += fragR

    # дзеркальні стрілки-обмін між картками
    my_mid = top + 150
    p.append(arrow(lcx + 320 / 2 - 6, my_mid - 16, rcx - 320 / 2 + 6, my_mid - 16, color=MUTED, sw=1.8))
    p.append(arrow(rcx - 320 / 2 + 6, my_mid + 16, lcx + 320 / 2 - 6, my_mid + 16, color=MUTED, sw=1.8))
    p.append(text(W / 2, my_mid - 24, "G повторення", size=11, color=BLUE[2], bold=True))
    p.append(text(W / 2, my_mid - 8, "= H парності", size=11, color=ORNG[2], bold=True))
    p.append(text(W / 2, my_mid + 30, "G парності", size=11, color=ORNG[2], bold=True))
    p.append(text(W / 2, my_mid + 46, "= H повторення", size=11, color=BLUE[2], bold=True))

    # нижня стрічка про розмірності
    box2, bw2, bh2 = textbox(W / 2, max(botL, botR) + 70,
                             ["dim C  +  dim C⊥  =  1  +  2  =  3  =  n",
                              "перевірна матриця одного коду — це твірна матриця другого"],
                             size=14, bold=True, fill="#eafaf0", stroke="#1e8449", sw=2, pad=14)
    p.append(box2)

    render(os.path.join(OUT, "dual-pair.svg"), W, H, *p,
           title="Код повторення й код парності — дуальна пара")


# ── Fig 5: межа Синглтона d ≤ n−k+1 як стеля сили (n = 7) ─────────────────────
def fig_singleton():
    W, H = 780, 580
    p = []
    n = 7
    # координатне поле
    LX, RX = 120, 590          # k від 0 до 7
    BY, TY = 452, 96           # d: низ (d=1) → верх (d=7)

    def sx(k):
        return LX + k * (RX - LX) / 7.0

    def sy(d):
        return BY - (d - 1) * (BY - TY) / 6.0

    # заборонена зона над прямою d = 8 − k (верхньо-правий трикутник)
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (sx(1), sy(7), sx(7), sy(7), sx(7), sy(1))
    p.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.75"/>' % tri)
    p.append(text((sx(4) + sx(7)) / 2, sy(6) + 4, "заборонено", size=13, color="#a12b1e", bold=True))
    p.append(text((sx(4) + sx(7)) / 2, sy(6) + 22, "(неможливо за Синглтоном)", size=11, color="#a12b1e", italic=True))

    # осі
    p.append(line(LX, TY - 6, LX, BY, color=INK, sw=1.8))
    p.append(line(LX, BY, RX + 6, BY, color=INK, sw=1.8))
    # поділки й підписи осей
    for k in range(0, 8):
        p.append(line(sx(k), BY, sx(k), BY + 5, color=INK, sw=1.4))
        p.append(text(sx(k), BY + 22, str(k), size=12, color=INK))
    for d in range(1, 8):
        p.append(line(LX - 5, sy(d), LX, sy(d), color=INK, sw=1.4))
        p.append(text(LX - 16, sy(d) + 5, str(d), size=12, color=INK))
    p.append(text((LX + RX) / 2, BY + 46, "k — розмірність (символів даних)", size=12.5, color=INK, bold=True))
    p.append(text(LX - 44, (TY + BY) / 2, "d", size=14, color=INK, bold=True))
    p.append(text(LX - 44, (TY + BY) / 2 + 18, "відстань", size=11, color=MUTED, italic=True))

    # пряма Синглтона d = n − k + 1
    p.append(line(sx(1), sy(7), sx(7), sy(1), color="#c2740f", sw=2.6))
    p.append(text(sx(2) + 30, sy(7) - 2, "межа Синглтона  d = n − k + 1", size=12.5, color="#9a5a0b", bold=True))

    def pt(k, d, label, sub, on_line, dx=12, dy=-10):
        cx, cy = sx(k), sy(d)
        col = ("#eafaf0", "#1e8449") if on_line else ("#eef4ff", "#2457d6")
        p.append(circle(cx, cy, 7, fill=col[0], stroke=col[1], sw=2.4))
        p.append(text(cx + dx, cy + dy, label, size=12.5, color=col[1], bold=True, anchor="start"))
        p.append(text(cx + dx, cy + dy + 15, sub, size=10.5, color=MUTED, anchor="start", italic=True))

    # MDS-коди на прямій
    pt(1, 7, "[7,1,7] повторення", "MDS · GF(2)", True, dx=14, dy=6)
    pt(3, 5, "[7,3,5] Рід–Соломон", "MDS · потрібне GF(8)", True, dx=14, dy=-14)
    pt(6, 2, "[7,6,2] парність", "MDS · GF(2)", True, dx=-150, dy=20)
    # не-MDS під прямою
    pt(4, 3, "[7,4,3] Геммінг", "не MDS (на 1 нижче)", False, dx=14, dy=18)

    # нотатка про поле
    box, bw, bh = textbox(W / 2, H - 42,
                          ["Над GF(2) на прямій — лише кути (повторення й парність).",
                           "Щоб сісти на межу всередині — як Рід–Соломон [7,3,5] — треба велике поле GF(8)."],
                          size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "singleton.svg"), W, H, *p,
           title="Межа Синглтона — стеля сили лінійного коду")


if __name__ == "__main__":
    fig_subspace()
    fig_translation()
    fig_family()
    fig_dual_pair()
    fig_singleton()
    print("OK: figures written to", OUT)
