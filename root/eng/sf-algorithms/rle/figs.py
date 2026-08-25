# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── idea: довгий повтор → (символ, лічильник) ─────────────────────────────────
# Ідея: показати сам прийом у найчистішому вигляді — низка однакових клітинок
# згортається в одну пару. Це «душа» RLE одним поглядом.

def fig_idea():
    W, H = 720, 250
    p = []
    y = 80
    cell = 26
    seq = "WWWWWWWWWWWWBWWWWWWWWWWWW"
    x0 = 40
    for i, ch in enumerate(seq):
        col = "#eef4ff" if ch == "W" else "#1a1a1a"
        tc = INK if ch == "W" else "#ffffff"
        p.append(rect(x0 + i * cell, y, cell, cell, fill=col, stroke=INK, sw=1))
        p.append(text(x0 + i * cell + cell / 2, y + cell / 2 + 5, ch, size=11, color=tc, bold=True))
    p.append(text(x0, y - 12, "24 символи вхідних (рядок піксельного «сканування»)", size=11, color=MUTED, anchor="start"))

    p.append(arrow(W / 2, y + cell + 14, W / 2, y + cell + 40, color=INK, sw=1.8))

    # вихід: три пари (символ × лічильник)
    yo = y + cell + 66
    pairs = [("W", 12, "#eef4ff", INK), ("B", 1, "#1a1a1a", "#ffffff"), ("W", 11, "#eef4ff", INK)]
    xp = 210
    for ch, n, col, _tc in pairs:
        b, bw, bh = textbox(xp, yo, "%d×%s" % (n, ch), size=13, bold=True, fill=col, stroke=INK, sw=1.4,
                            color=(INK if col == "#eef4ff" else "#ffffff"))
        p.append(b)
        xp += bw + 18
    p.append(text(xp - 8, yo + 4, "→ 3 пари замість 24", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "idea.svg"), W, H, *p,
           title="RLE: низка однакового → (лічильник, символ)")


# ── good-vs-bad: де RLE виграє, а де роздуває ─────────────────────────────────
# Ідея: дві стрічки поруч. Угорі — довгі повтори (RLE тисне різко). Унизу —
# усе різне (RLE РОЗДУВАЄ: на кожен символ ще й лічильник). Це головна пастка.

def fig_good_vs_bad():
    W, H = 720, 320
    p = []
    cell = 22

    # ── добрий випадок ────────────────────────────────────────────────
    yg = 70
    p.append(text(40, yg - 14, "довгі повтори — RLE тисне різко", size=12, color=FIELD, bold=True, anchor="start"))
    seqg = "AAAAAAAAAAAABBBBBBBB"
    for i, ch in enumerate(seqg):
        col = "#eafaf0" if ch == "A" else "#d8f0e2"
        p.append(rect(40 + i * cell, yg, cell, cell, fill=col, stroke=FIELD, sw=1))
        p.append(text(40 + i * cell + cell / 2, yg + cell / 2 + 4, ch, size=10, color=INK))
    p.append(text(40 + len(seqg) * cell + 14, yg + cell / 2 + 4, "20 Б", size=11, color=MUTED, anchor="start"))
    # вихід
    b, bw, bh = textbox(220, yg + 64, "12×A · 8×B", size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD)
    p.append(b)
    p.append(text(220 + bw / 2 + 16, yg + 64 + 4, "→ ~4 Б  (5× менше)", size=11, color=FIELD, anchor="start", bold=True))

    p.append(line(40, 190, W - 40, 190, color=MUTED, sw=1, dash="4 4"))

    # ── поганий випадок ───────────────────────────────────────────────
    yb = 226
    p.append(text(40, yb - 14, "усе різне — RLE РОЗДУВАЄ", size=12, color=POS, bold=True, anchor="start"))
    seqb = "ABCDEFGHIJKLMNOPQRST"
    for i, ch in enumerate(seqb):
        p.append(rect(40 + i * cell, yb, cell, cell, fill="#fdecea", stroke=POS, sw=1))
        p.append(text(40 + i * cell + cell / 2, yb + cell / 2 + 4, ch, size=9, color=INK))
    p.append(text(40 + len(seqb) * cell + 14, yb + cell / 2 + 4, "20 Б", size=11, color=MUTED, anchor="start"))
    b2, bw2, bh2 = textbox(260, yb + 60, "1×A 1×B 1×C 1×D …", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6, color=POS)
    p.append(b2)
    p.append(text(260 + bw2 / 2 + 16, yb + 60 + 4, "→ ~40 Б  (удвічі більше!)", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "good-vs-bad.svg"), W, H, *p,
           title="RLE: блискучий на повторах — згубний на «шумі»")


# ── escape: прапорець відрізняє «лічильник» від «сирих байтів» ─────────────────
# Ідея: схема PackBits. Керівний байт: 0..127 → стільки+1 сирих далі; від'ємний
# → повторити наступний байт. Так короткі несхожі ділянки не роздувають.

def fig_escape():
    W, H = 740, 300
    p = []
    # два режими — дві гілки від «керівного байта»
    cx, cy = W / 2, 70
    core, cw, ch = textbox(cx, cy, "керівний байт", size=13, bold=True, fill="#f6f4ec",
                           stroke=INK, sw=2, color=INK)
    p.append(core)

    # ліва гілка — повтор
    lx, ly = 200, 200
    bl, bwl, bhl = textbox(lx, ly, "лічильник ≥ 0\n→ повтор", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(line(cx - cw / 4, cy + ch / 2, lx, ly - bhl / 2, color=MUTED, sw=1.4))
    p.append(bl)
    p.append(mtext(lx, ly + bhl / 2 + 22, "«далі 1 байт,\nповтори 12 разів»", size=10, color=INK))

    # права гілка — сирі байти
    rx, ry = 540, 200
    br, bwr, bhr = textbox(rx, ry, "прапорець «сирі»\n→ копіюй як є", size=12, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8, color=NEG)
    p.append(line(cx + cw / 4, cy + ch / 2, rx, ry - bhr / 2, color=MUTED, sw=1.4))
    p.append(br)
    p.append(mtext(rx, ry + bhr / 2 + 22, "«далі 5 байтів,\nбери дослівно»", size=10, color=INK))

    p.append(text(W / 2, H - 18,
                  "сирий режим обмежує роздування: несхоже не множиться на лічильники",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "escape.svg"), W, H, *p,
           title="Прапорець-перемикач: повтор або «сирі» байти (як у PackBits)")


# ── where: де RLE сяє ─────────────────────────────────────────────────────────
# Ідея: чотири картки-приклади з великими гладкими зонами — там, де серії довгі.

def fig_where():
    W, H = 740, 250
    p = []
    cw, ch, gap = 160, 130, 20
    x0 = (W - (4 * cw + 3 * gap)) / 2
    y0 = 64
    cards = [
        ("факс", NEG, "#eef4ff", "чорні літери\nна білому —\nдовгі білі серії"),
        ("палітрові\nзображення", FIELD, "#eafaf0", "великі зони\nодного індексу\nкольору"),
        ("спрайти,\nіконки", "#8a5fb0", "#f2ecf8", "суцільне тло,\nпрозорі поля"),
        ("маски,\nкреслення", "#d98a00", "#fdf6e3", "два кольори,\nширокі плоскі\nділянки"),
    ]
    for i, (title, col, fill, what) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(mtext(x + cw / 2, y0 + 26, title, size=12, color=col, bold=True))
        p.append(line(x + 18, y0 + 60, x + cw - 18, y0 + 60, color=col, sw=1, dash="4 3"))
        p.append(mtext(x + cw / 2, y0 + 82, what, size=9.5, color=INK))
    p.append(text(W / 2, y0 + ch + 30,
                  "спільне одне: довгі серії однакового — там RLE й мешкає",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "where.svg"), W, H, *p,
           title="Де RLE справді сяє: великі однотонні зони")


if __name__ == "__main__":
    fig_idea()
    fig_good_vs_bad()
    fig_escape()
    fig_where()
    print("OK: figures written to", OUT)
