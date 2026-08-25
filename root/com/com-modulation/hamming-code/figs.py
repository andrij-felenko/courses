# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PFILL = "#eef4ff"   # клітинка парності
PSTRK = "#2457d6"
DFILL = "#eafaf0"   # клітинка даних
DSTRK = "#27ae60"


# ── layout: де парності, де дані, і чому набори саме такі ─────────────────────
# Ідея: семибітне слово як ряд клітинок; під кожною — двійковий номер позиції;
# три рядки внизу показують, що кожна парність накриває позиції, де її розряд = 1.

def fig_layout():
    W, H = 720, 360
    p = []
    n = 7
    cw, ch = 64, 56
    x0 = (W - n * cw) / 2
    top = 64

    # позиції 1..7: 1,2,4 — парність; 3,5,6,7 — дані
    par = {1, 2, 4}
    names = {1: "P1", 2: "P2", 4: "P4", 3: "D1", 5: "D2", 6: "D3", 7: "D4"}
    cx = []
    for i in range(1, n + 1):
        x = x0 + (i - 1) * cw
        cx.append(x + cw / 2)
        isp = i in par
        p.append(rect(x, top, cw, ch, fill=PFILL if isp else DFILL,
                      stroke=PSTRK if isp else DSTRK, sw=2.0, rx=6))
        p.append(text(x + cw / 2, top + ch / 2 - 2, names[i], size=16,
                      color=PSTRK if isp else DSTRK, bold=True))
        # номер позиції над клітинкою
        p.append(text(x + cw / 2, top - 12, "поз. %d" % i, size=11, color=MUTED))
        # двійковий номер під клітинкою
        p.append(text(x + cw / 2, top + ch + 18, format(i, "03b"), size=13, color=INK, bold=True))

    p.append(text(x0 - 10, top - 12, "", size=11))
    p.append(text(W / 2, top + ch + 40, "двійковий номер позиції (старший · середній · молодший)",
                  size=11, color=MUTED, italic=True))

    # три рядки покриття
    rows = [
        ("P1 накриває", 1, "молодший біт = 1", [1, 3, 5, 7]),
        ("P2 накриває", 2, "середній біт = 1", [2, 3, 6, 7]),
        ("P4 накриває", 4, "старший біт = 1", [4, 5, 6, 7]),
    ]
    ry = top + ch + 64
    lblx = x0 - 6
    for label, owner, why, cover in rows:
        col = PSTRK
        p.append(text(lblx, ry + 6, label, size=12, color=col, bold=True, anchor="end"))
        for i in range(1, n + 1):
            on = i in cover
            cxx = cx[i - 1]
            p.append(circle(cxx, ry, 9, fill=PFILL if on else BG,
                            stroke=col if on else "#d0d4da", sw=2.0 if on else 1.2))
            if on:
                p.append(text(cxx, ry + 4, "1", size=11, color=col, bold=True))
        p.append(text(x0 + n * cw + 12, ry + 5, why, size=10.5, color=MUTED, anchor="start"))
        ry += 34

    render(os.path.join(OUT, "layout.svg"), W, H, *p,
           title="Розкладка (7,4): парності — на степенях двійки, кожна стереже свій розряд номера")


# ── syndrome: три перевірки складають двійкову адресу битого біта ─────────────
# Ідея: перевернувся біт на позиції 5 (=101); P4 і P1 не сходяться, P2 сходиться;
# три результати, виписані як c4 c2 c1, дають 101 = 5 — точну адресу.

def fig_syndrome():
    W, H = 720, 340
    p = []
    n = 7
    cw, ch = 64, 52
    x0 = (W - n * cw) / 2
    top = 70
    bad = 5

    names = {1: "P1", 2: "P2", 4: "P4", 3: "D1", 5: "D2", 6: "D3", 7: "D4"}
    par = {1, 2, 4}
    bits = {1: 0, 2: 1, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1}   # прийняте слово (з помилкою на 5)
    cx = []
    for i in range(1, n + 1):
        x = x0 + (i - 1) * cw
        cx.append(x + cw / 2)
        flipped = (i == bad)
        isp = i in par
        fill = "#fdecea" if flipped else (PFILL if isp else DFILL)
        strk = POS if flipped else (PSTRK if isp else DSTRK)
        p.append(rect(x, top, cw, ch, fill=fill, stroke=strk, sw=2.6 if flipped else 2.0, rx=6))
        p.append(text(x + cw / 2, top + ch / 2 - 5, names[i], size=12,
                      color=strk, bold=True))
        p.append(text(x + cw / 2, top + ch / 2 + 13, str(bits[i]), size=13, color=INK, bold=True))
        p.append(text(x + cw / 2, top - 10, "поз. %d" % i, size=10, color=MUTED))
    p.append(text(cx[bad - 1], top + ch + 18, "перевернутий біт", size=11, color=POS, bold=True))

    # три перевірки → результат
    checks = [
        ("P4: набір 4,5,6,7", [4, 5, 6, 7], 1, "c4"),
        ("P2: набір 2,3,6,7", [2, 3, 6, 7], 0, "c2"),
        ("P1: набір 1,3,5,7", [1, 3, 5, 7], 1, "c1"),
    ]
    ry = top + ch + 52
    lblx = x0 - 6
    resx = x0 + n * cw + 30
    for label, cover, res, name in checks:
        col = POS if res else FIELD
        p.append(text(lblx, ry + 5, label, size=11.5, color=INK, bold=True, anchor="end"))
        for i in range(1, n + 1):
            if i in cover:
                cxx = cx[i - 1]
                p.append(circle(cxx, ry, 8, fill="#fdecea" if i == bad else FILL,
                                stroke=POS if i == bad else MUTED, sw=1.6))
        verdict = "не сходиться → 1" if res else "сходиться → 0"
        p.append(text(resx, ry + 5, "%s   %s = %d" % (verdict, name, res),
                      size=11.5, color=col, anchor="start", bold=True))
        ry += 36

    # підсумок-синдром
    sy = ry + 8
    box, bw, bh = textbox(W / 2, sy, "синдром  c4 c2 c1 = 101₂ = 5   →   перевернути біт на позиції 5",
                          size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "syndrome.svg"), W, H, *p,
           title="Синдром = адреса: три перевірки складають двійковий номер битого біта")


# ── proj-encode: дані по позиціях, парності як XOR груп (вставка) ─────────────

def fig_proj_encode():
    W, H = 720, 320
    p = []
    n = 7
    cw, ch = 64, 54
    x0 = (W - n * cw) / 2
    top = 70

    # контрольний приклад d1 d2 d3 d4 = 1 0 1 1 → слово 0110011
    word = {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 1, 7: 1}
    names = {1: "p1", 2: "p2", 4: "p4", 3: "d1", 5: "d2", 6: "d3", 7: "d4"}
    par = {1, 2, 4}
    cx = []
    for i in range(1, n + 1):
        x = x0 + (i - 1) * cw
        cx.append(x + cw / 2)
        isp = i in par
        p.append(rect(x, top, cw, ch, fill=PFILL if isp else DFILL,
                      stroke=PSTRK if isp else DSTRK, sw=2.0, rx=6))
        p.append(text(x + cw / 2, top + ch / 2 - 5, names[i], size=12,
                      color=PSTRK if isp else DSTRK, bold=True))
        p.append(text(x + cw / 2, top + ch / 2 + 13, str(word[i]), size=13, color=INK, bold=True))
        p.append(text(x + cw / 2, top - 10, "поз. %d" % i, size=10, color=MUTED))

    p.append(text(W / 2, top + ch + 26, "дані 1 0 1 1 → кодове слово 0 1 1 0 0 1 1",
                  size=12, color=INK, bold=True))

    eqs = [
        "p1 = d1 ⊕ d2 ⊕ d4 = 1 ⊕ 0 ⊕ 1 = 0",
        "p2 = d1 ⊕ d3 ⊕ d4 = 1 ⊕ 1 ⊕ 1 = 1",
        "p4 = d2 ⊕ d3 ⊕ d4 = 0 ⊕ 1 ⊕ 1 = 0",
    ]
    ey = top + ch + 56
    for e in eqs:
        p.append(text(W / 2, ey, e, size=13, color=PSTRK))
        ey += 26
    p.append(text(W / 2, ey + 8, "кожна парність — це XOR своєї групи позицій",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "proj-encode.svg"), W, H, *p,
           title="Кодер (7,4): дані по позиціях, парності як XOR трьох груп")


# ── proj-syndrome: декодер — перевірки складають адресу, один XOR лагодить ────

def fig_proj_syndrome():
    W, H = 720, 320
    p = []
    n = 7
    cw, ch = 64, 52
    x0 = (W - n * cw) / 2
    top = 70
    bad = 5

    recv = {1: 0, 2: 1, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1}   # 0110011 з помилкою на 5
    names = {1: "p1", 2: "p2", 4: "p4", 3: "d1", 5: "d2", 6: "d3", 7: "d4"}
    par = {1, 2, 4}
    cx = []
    for i in range(1, n + 1):
        x = x0 + (i - 1) * cw
        cx.append(x + cw / 2)
        flipped = (i == bad)
        isp = i in par
        fill = "#fdecea" if flipped else (PFILL if isp else DFILL)
        strk = POS if flipped else (PSTRK if isp else DSTRK)
        p.append(rect(x, top, cw, ch, fill=fill, stroke=strk, sw=2.6 if flipped else 2.0, rx=6))
        p.append(text(x + cw / 2, top + ch / 2 - 5, names[i], size=12, color=strk, bold=True))
        p.append(text(x + cw / 2, top + ch / 2 + 13, str(recv[i]), size=13, color=INK, bold=True))
        p.append(text(x + cw / 2, top - 10, "поз. %d" % i, size=10, color=MUTED))
    p.append(text(cx[bad - 1], top + ch + 18, "збій у каналі", size=11, color=POS, bold=True))

    checks = [
        ("перевірка p4", 1, "s4"),
        ("перевірка p2", 0, "s2"),
        ("перевірка p1", 1, "s1"),
    ]
    ry = top + ch + 50
    for label, res, name in checks:
        col = POS if res else FIELD
        p.append(text(W / 2 - 150, ry + 5, label, size=12, color=INK, bold=True, anchor="end"))
        p.append(text(W / 2 - 120, ry + 5, "%s = %d" % (name, res), size=12.5, color=col,
                      anchor="start", bold=True))
        ry += 30

    sy = ry + 6
    box, bw, bh = textbox(W / 2, sy, "синдром  s4 s2 s1 = 101₂ = 5   →   w ^= 1<<(5−1)   →   дані 1011",
                          size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(box)
    p.append(text(W / 2, sy + bh / 2 + 22, "синдром 000 означав би: чіпати нічого не треба",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "proj-syndrome.svg"), W, H, *p,
           title="Декодер: перевірки складають адресу, один XOR виправляє біт")


# ── proj-code-walk: рядок матриці = бітова маска = ітерація циклу ─────────────

def fig_proj_code_walk():
    W, H = 760, 400
    p = []

    # ліворуч — матриця покриття 3×7
    n = 7
    cw, chh = 46, 40
    mx, my = 70, 90
    rows = [
        ("p1", [1, 0, 1, 0, 1, 0, 1], "0x55"),
        ("p2", [0, 1, 1, 0, 0, 1, 1], "0x66"),
        ("p4", [0, 0, 0, 1, 1, 1, 1], "0x78"),
    ]
    # шапка з номерами позицій
    for j in range(n):
        p.append(text(mx + j * cw + cw / 2, my - 10, "%d" % (j + 1), size=11, color=MUTED))
    p.append(text(mx - 12, my - 10, "поз.", size=10, color=MUTED, anchor="end"))
    for r, (label, bitsrow, mask) in enumerate(rows):
        ry = my + r * chh
        p.append(text(mx - 12, ry + chh / 2 + 4, label, size=13, color=PSTRK, bold=True, anchor="end"))
        for j in range(n):
            on = bitsrow[j]
            x = mx + j * cw
            p.append(rect(x, ry, cw, chh, fill=PFILL if on else BG,
                          stroke=PSTRK if on else "#d0d4da", sw=1.8 if on else 1.0, rx=4))
            p.append(text(x + cw / 2, ry + chh / 2 + 4, str(on), size=13,
                          color=PSTRK if on else "#c0c4ca", bold=on))
        # маска праворуч від рядка
        p.append(text(mx + n * cw + 16, ry + chh / 2 + 4, "= маска %s" % mask,
                      size=12, color=INK, anchor="start", bold=True))

    # стовпець читається як адреса
    p.append(text(mx + n * cw / 2, my + 3 * chh + 26,
                  "стовпець (знизу вгору) = двійкова адреса позиції → тому синдром = номер збою",
                  size=10.5, color=MUTED, italic=True))

    # праворуч — три застосування тих самих масок
    bx = 70
    by = my + 3 * chh + 64
    steps = [
        "кодер:  parity(w & MASK[k]) кладе три парності",
        "декодер:  з тих самих трьох перевірок складає синдром",
        "виправлення:  один XOR  w ^= 1<<(s−1)",
    ]
    for s in steps:
        b, bw, bh = textbox(W / 2, by, s, size=12, bold=True, fill=DFILL, stroke=DSTRK, sw=1.6, pad=10)
        p.append(b)
        by += bh + 12

    render(os.path.join(OUT, "proj-code-walk.svg"), W, H, *p,
           title="Один об'єкт у трьох поданнях: рядок матриці = бітова маска = крок коду")


if __name__ == "__main__":
    fig_layout()
    fig_syndrome()
    fig_proj_encode()
    fig_proj_syndrome()
    fig_proj_code_walk()
    print("OK: figures written to", OUT)
