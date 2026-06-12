# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.9.6a — «Кодер і декодер Геммінга (7,4) у 30 рядків C».

ОКРЕМИЙ генератор лише цієї вставки (головний figs.py розділу НЕ чіпаємо).
Чистий Python без залежностей. Вивід → ./img/.
Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — §3.9.6a.k → файли fig-r09-s6a-k-*.

Фігури:
  fig-r09-s6a-1-encode.svg     — кодер: нібл d=1011 → розкладка позицій → три XOR-групи → кодове слово
  fig-r09-s6a-2-syndrome.svg   — декодер: збій у позиції 5 → синдром 101 = адреса 5 → інверсія → нібл назад
  fig-r09-s6a-3-code-walk.svg  — 30 рядків C, розкладені по математиці: матриця покриття ↔ маски в коді
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
VIOL  = "#7a3ea8"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOL: "aViol"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def cell(x, y, val, w=34, h=34, kind="data", faint=False, big=16):
    """Клітинка біта позиції коду.
    kind: 'data' (бурштин), 'parity' (фіолет), 'plain' (за значенням 1/0)."""
    if kind == "data":
        col = AMBER
    elif kind == "parity":
        col = VIOL
    else:
        col = RED if val == "1" else BLUE
    if faint:
        col = FAINT
    s = rect(x, y, w, h, "#fff", col, 2 if not faint else 1.4, 5)
    s += text(x + w / 2, y + h * 0.68, val, big, col if not faint else GREY, "middle", "bold")
    return s


# Канонічна розкладка Геммінга (7,4): позиції 1..7, p на степенях двійки.
# 1=p1  2=p2  3=d1  4=p4  5=d2  6=d3  7=d4
POS_KIND = {1: "p", 2: "p", 3: "d", 4: "p", 5: "d", 6: "d", 7: "d"}
POS_LABEL = {1: "p1", 2: "p2", 3: "d1", 4: "p4", 5: "d2", 6: "d3", 7: "d4"}
# Групи покриття: p1→{1,3,5,7}, p2→{2,3,6,7}, p4→{4,5,6,7}
GROUPS = {1: [1, 3, 5, 7], 2: [2, 3, 6, 7], 4: [4, 5, 6, 7]}


def _encode(nibble):
    """nibble = (d1,d2,d3,d4) бітами 0/1 → словник позиція→біт (1..7)."""
    d1, d2, d3, d4 = nibble
    bit = {3: d1, 5: d2, 6: d3, 7: d4}
    bit[1] = d1 ^ d2 ^ d4   # позиції 3,5,7
    bit[2] = d1 ^ d3 ^ d4   # позиції 3,6,7
    bit[4] = d2 ^ d3 ^ d4   # позиції 5,6,7
    return bit


# ── Фігура 1: КОДЕР — нібл → розкладка → три XOR-групи → кодове слово ──────────
def fig1_encode():
    W, H = 940, 712
    b = header(W, H)
    b += text(W / 2, 30,
              "Кодер Геммінга (7,4): чотири біти даних → сім бітів коду",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Приклад: нібл d = 1011 (d1=1, d2=0, d3=1, d4=1). Позиції 1,2,4 — контрольні, решта — дані.",
              11.5, GREY, "middle", style="italic")

    nibble = (1, 0, 1, 1)
    bit = _encode(nibble)

    # ── рядок 1: чотири біти даних окремо ──
    b += text(70, 92, "Дані (4 біти):", 12.5, AMBER, "start", "bold")
    dvals = {"d1": 1, "d2": 0, "d3": 1, "d4": 1}
    dx = 230
    for i, (nm, v) in enumerate(dvals.items()):
        x = dx + i * 70
        b += cell(x, 76, str(v), 34, 34, "data")
        b += text(x + 17, 128, nm, 11, GREY, "middle")

    b += arrow(W / 2, 138, W / 2, 162, INK, 2.2)
    b += text(W / 2 + 14, 156, "розкласти по позиціях + долічити парність", 11, GREY, "start", style="italic")

    # ── рядок 2: сім позицій коду (1..7) ──
    cw = 64
    x0 = (W - 7 * cw) / 2
    ytop = 178
    b += text(x0 - 10, ytop - 8, "Позиція:", 11, GREY, "end")
    for p in range(1, 8):
        x = x0 + (p - 1) * cw
        # номер позиції зверху, у двійковому теж — щоб видно адресу
        b += text(x + (cw - 8) / 2, ytop - 8, f"{p}", 12, INK, "middle", "bold")
        b += text(x + (cw - 8) / 2, ytop - 22, f"{p:03b}", 9.5, GREY, "middle")
        knd = "parity" if POS_KIND[p] == "p" else "data"
        b += cell(x, ytop, str(bit[p]), cw - 8, 40, knd, big=17)
        b += text(x + (cw - 8) / 2, ytop + 62, POS_LABEL[p], 11,
                  VIOL if knd == "parity" else AMBER, "middle", "bold")

    b += text(x0, ytop + 84, "Контрольні біти сидять на позиціях-степенях двійки (1, 2, 4) — далі стане зрозуміло чому.",
              10.5, GREY, "start", style="italic")

    # ── три групи XOR (як рахується кожен контрольний біт) ──
    grp_specs = [
        (1, "p1", VIOL, "p1 = d1 ⊕ d2 ⊕ d4", [3, 5, 7], bit[3] ^ bit[5] ^ bit[7]),
        (2, "p2", VIOL, "p2 = d1 ⊕ d3 ⊕ d4", [3, 6, 7], bit[3] ^ bit[6] ^ bit[7]),
        (4, "p4", VIOL, "p4 = d2 ⊕ d3 ⊕ d4", [5, 6, 7], bit[5] ^ bit[6] ^ bit[7]),
    ]
    gy = 300
    gh = 104
    for i, (p, nm, col, formula, src, val) in enumerate(grp_specs):
        y = gy + i * (gh + 8)
        b += rect(60, y, W - 120, gh, "#fbf7ff", VIOL, 1.6, 9)
        b += text(82, y + 26, f"{nm}: парність своєї групи", 13, VIOL, "start", "bold")
        b += mono(82, y + 50, formula, 13, INK)
        # підставлені значення
        vals = " ⊕ ".join(str(bit[s]) for s in src)
        b += mono(82, y + 74, f"= {vals} = {val}", 13, GREEN if False else INK)
        b += text(82, y + 94, "(позиції " + ", ".join(str(s) for s in src) + ")", 10, GREY, "start")
        # міні-смужка позицій із підсвіченою групою
        mx0 = 470
        for pp in range(1, 8):
            x = mx0 + (pp - 1) * 40
            inset = pp in src or pp == p
            knd = "plain"
            if pp == p:
                b += rect(x, y + 24, 34, 34, "#f0fff2", GREEN, 2, 5)
                b += text(x + 17, y + 46, str(bit[pp]), 14, GREEN, "middle", "bold")
                b += text(x + 17, y + 18, "сюди", 8.5, GREEN, "middle")
            elif pp in src:
                b += cell(x, y + 24, str(bit[pp]), 34, 34,
                          "data" if POS_KIND[pp] == "d" else "parity")
            else:
                b += cell(x, y + 24, str(bit[pp]), 34, 34, "plain", faint=True)
            b += text(x + 17, y + 70, f"{pp}", 9, GREY, "middle")
        b += text(mx0 + 7 * 40 + 6, y + 40, "XOR обраних →", 9.5, GREY, "start")
        b += text(mx0 + 7 * 40 + 6, y + 54, "контрольна клітинка", 9.5, GREY, "start")

    # ── підсумкове кодове слово ──
    by = 300 + 3 * (gh + 8) + 6
    code = "".join(str(bit[p]) for p in range(1, 8))
    b += rect(60, by, W - 120, 54, "#f0fff2", GREEN, 1.8, 9)
    b += text(82, by + 32, "Кодове слово (7 біт, позиції 1→7):", 13, GREEN, "start", "bold")
    b += mono(430, by + 33, code, 18, GREEN, "start", "bold")
    b += text(560, by + 32,
              "= 4 біти даних + 3 контрольні. Надлишковість 7/4 — ціна за виправлення одного збою.",
              10.5, GREY, "start", style="italic")
    save("fig-r09-s6a-1-encode.svg", b)


# ── Фігура 2: ДЕКОДЕР — збій у позиції 5, синдром = адреса помилки ─────────────
def fig2_syndrome():
    W, H = 940, 690
    b = header(W, H)
    b += text(W / 2, 30,
              "Декодер: три перевірки парності складають ДВІЙКОВУ адресу зламаного біта",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Надсилали 0110011; у каналі перевернувся біт на позиції 5. Декодер його сам знайде й полагодить.",
              11.5, GREY, "middle", style="italic")

    sent = _encode((1, 0, 1, 1))                # позиція→біт
    recv = dict(sent)
    recv[5] ^= 1                                # збій у позиції 5

    cw = 70
    x0 = (W - 7 * cw) / 2

    # ── рядок: надіслане ──
    ya = 86
    b += text(x0 - 14, ya + 24, "Надіслано:", 11.5, INK, "end", "bold")
    for p in range(1, 8):
        x = x0 + (p - 1) * cw
        knd = "parity" if POS_KIND[p] == "p" else "data"
        b += cell(x, ya, str(sent[p]), cw - 10, 34, knd)
    # ── рядок: отримане (позиція 5 підсвічена як збій) ──
    yb = ya + 60
    b += text(x0 - 14, yb + 24, "Отримано:", 11.5, INK, "end", "bold")
    for p in range(1, 8):
        x = x0 + (p - 1) * cw
        if p == 5:
            b += rect(x, yb, cw - 10, 34, "#fdeceb", RED, 2.6, 5)
            b += text(x + (cw - 10) / 2, yb + 23, str(recv[p]), 16, RED, "middle", "bold")
            b += text(x + (cw - 10) / 2, yb - 6, "↯ збій", 11, RED, "middle", "bold")
        else:
            knd = "parity" if POS_KIND[p] == "p" else "data"
            b += cell(x, yb, str(recv[p]), cw - 10, 34, knd)
        b += text(x + (cw - 10) / 2, yb + 52, f"поз. {p}", 10, GREY, "middle")

    # ── три перевірки парності → три біти синдрому ──
    b += text(W / 2, yb + 92,
              "Перерахуємо парність тих самих трьох груп. 0 = група ціла, 1 = у групі непарне число одиниць (щось не так).",
              11, INK, "middle", "bold")

    checks = [
        ("s1", [1, 3, 5, 7], 1),  # бере позицію 5 → 1
        ("s2", [2, 3, 6, 7], 4),
        ("s4", [4, 5, 6, 7], 2),
    ]
    # фактичні значення
    syn = {}
    for nm, grp, _w in checks:
        syn[nm] = 0
        for p in grp:
            syn[nm] ^= recv[p]

    gy = yb + 116
    gh = 92
    contains5 = {"s1": True, "s2": False, "s4": True}
    for i, (nm, grp, weight) in enumerate(checks):
        y = gy + i * (gh + 6)
        bad = syn[nm] == 1
        col = RED if bad else GREEN
        b += rect(60, y, 470, gh, "#fdeceb" if bad else "#f0fff2", col, 1.7, 9)
        b += text(82, y + 26, f"{nm} = парність позицій " + ", ".join(str(p) for p in grp),
                  12.5, col, "start", "bold")
        vals = " ⊕ ".join(str(recv[p]) for p in grp)
        b += mono(82, y + 50, f"{vals} = {syn[nm]}", 13, INK)
        verdict = "група ЗЛАМАНА → 1" if bad else "група ціла → 0"
        b += text(82, y + 74, verdict + ("   (а позиція 5 саме в ній)" if contains5[nm] and bad else
                                          ("   (позиції 5 тут немає)" if not contains5[nm] else "")),
                  10.5, col, "start", "bold" if bad else "normal")
        # сам біт синдрому збоку
        b += rect(548, y + gh / 2 - 22, 44, 44, "#fff", col, 2.4, 6)
        b += text(548 + 22, y + gh / 2 + 6, str(syn[nm]), 20, col, "middle", "bold")
        b += text(548 + 22, y + gh / 2 - 28, nm, 10, col, "middle", "bold")

    # ── складання синдрому в число = адреса ──
    sx = 640
    b += rect(sx, gy, W - sx - 60, 3 * (gh + 6) - 6, "#fff7ec", AMBER, 1.8, 10)
    b += text(sx + (W - sx - 60) / 2, gy + 26, "Синдром як двійкове число", 13, AMBER, "middle", "bold")
    b += text(sx + (W - sx - 60) / 2, gy + 46, "Складаємо біти в порядку s4 s2 s1:", 10.5, INK, "middle")
    # три біти в ряд
    triple = f"{syn['s4']}{syn['s2']}{syn['s1']}"
    bx = sx + (W - sx - 60) / 2 - 60
    for j, ch in enumerate(triple):
        x = bx + j * 42
        b += rect(x, gy + 58, 36, 36, "#fff", RED if ch == "1" else BLUE, 2.2, 5)
        b += text(x + 18, gy + 83, ch, 17, RED if ch == "1" else BLUE, "middle", "bold")
    b += text(bx + 18, gy + 108, "s4", 10, GREY, "middle")
    b += text(bx + 42 + 18, gy + 108, "s2", 10, GREY, "middle")
    b += text(bx + 84 + 18, gy + 108, "s1", 10, GREY, "middle")
    dec = int(triple, 2)
    b += text(sx + (W - sx - 60) / 2, gy + 138, f"{triple}₂ = {dec}", 17, GREEN, "middle", "bold")
    b += text(sx + (W - sx - 60) / 2, gy + 160,
              f"→ зламаний біт на позиції {dec}", 12.5, GREEN, "middle", "bold")
    b += text(sx + (W - sx - 60) / 2, gy + 182,
              "(а синдром 000 означав би: помилок немає)", 9.5, GREY, "middle", style="italic")

    # ── фінал: інверсія й витяг даних ──
    by = gy + 3 * (gh + 6) + 6
    b += rect(60, by, W - 120, 50, "#f0fff2", GREEN, 1.8, 9)
    fixed = dict(recv)
    fixed[dec] ^= 1
    nib = f"{fixed[3]}{fixed[5]}{fixed[6]}{fixed[7]}"
    b += text(82, by + 30, f"Лагодимо: інвертуємо біт {dec} → беремо дані з позицій 3,5,6,7 →", 12.5, GREEN, "start", "bold")
    b += mono(700, by + 31, f"d = {nib}", 15, GREEN, "start", "bold")
    b += text(W - 70, by + 30, "(саме те, що відправляли)", 10, GREY, "end", style="italic")
    save("fig-r09-s6a-2-syndrome.svg", b)


# ── Фігура 3: 30 рядків C, розкладені по математиці (матриця ↔ маски) ─────────
def fig3_code_walk():
    W, H = 960, 700
    b = header(W, H)
    b += text(W / 2, 30,
              "Чому код такий короткий: уся математика Геммінга — це три маски покриття",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Кодер, синдром і виправлення — це повторення одного: XOR бітів, які покриває кожна контрольна позиція.",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: матриця покриття H (рядок = контрольна позиція, стовпець = позиція коду) ──
    mx, my = 60, 86
    b += text(mx, my - 8, "Матриця покриття (хто кого перевіряє)", 13, INK, "start", "bold")
    cellw, cellh = 46, 40
    # шапка стовпців: позиції 1..7
    for p in range(1, 8):
        x = mx + 90 + (p - 1) * cellw
        b += text(x + cellw / 2 - 4, my + 18, f"{p}", 12, INK, "middle", "bold")
        b += text(x + cellw / 2 - 4, my + 34, POS_LABEL[p], 9, GREY, "middle")
    rows = [("s1 / p1", 1, GROUPS[1]),
            ("s2 / p2", 2, GROUPS[2]),
            ("s4 / p4", 4, GROUPS[4])]
    for r, (nm, p, grp) in enumerate(rows):
        ry = my + 44 + r * cellh
        b += text(mx, ry + cellh * 0.62, nm, 12, VIOL, "start", "bold")
        for pp in range(1, 8):
            x = mx + 90 + (pp - 1) * cellw
            inset = pp in grp
            fill = "#efe7fa" if inset else "#fff"
            b += rect(x, ry, cellw - 6, cellh - 6, fill, VIOL if inset else FAINT, 1.6 if inset else 1, 5)
            b += text(x + (cellw - 6) / 2, ry + (cellh - 6) * 0.66, "1" if inset else "·",
                      14 if inset else 13, VIOL if inset else GREY, "middle", "bold" if inset else "normal")
    # пояснення матриці
    b += text(mx, my + 44 + 3 * cellh + 22,
              "Кожен рядок — одна група. Одиниці в рядку = позиції, що в неї входять.", 10.5, GREY, "start")
    b += text(mx, my + 44 + 3 * cellh + 38,
              "Стовпець читається як ДВІЙКОВА адреса позиції: тому синдром і дорівнює номеру збою.",
              10.5, INK, "start", "bold")
    # три маски як числа
    msk = {}
    for p in (1, 2, 4):
        v = 0
        for pp in GROUPS[p]:
            v |= 1 << (pp - 1)
        msk[p] = v
    b += text(mx, my + 44 + 3 * cellh + 64, "Ті самі рядки — як бітові маски в коді (біт i ↔ позиція i+1):", 11, AMBER, "start", "bold")
    b += mono(mx, my + 44 + 3 * cellh + 84, f"M1 = 0x{msk[1]:02X}   (біти позицій 1,3,5,7)", 12, INK)
    b += mono(mx, my + 44 + 3 * cellh + 102, f"M2 = 0x{msk[2]:02X}   (біти позицій 2,3,6,7)", 12, INK)
    b += mono(mx, my + 44 + 3 * cellh + 120, f"M4 = 0x{msk[4]:02X}   (біти позицій 4,5,6,7)", 12, INK)

    # ── праворуч: три «фази» коду, кожна спирається на ті самі маски ──
    px = 560
    b += text(px, my - 8, "Куди ці маски йдуть у коді (30 рядків)", 13, INK, "start", "bold")
    phases = [
        ("КОДЕР", GREEN,
         ["для кожної маски Mi:", "  pi = parity( word & Mi )", "  вписати pi у свою позицію"],
         "три XOR-згортки → 3 контрольні біти"),
        ("СИНДРОМ", VIOL,
         ["для кожної маски Mi:", "  si = parity( recv & Mi )", "  syndrome |= si << (адреса pi)"],
         "ті самі три згортки → число-адреса"),
        ("ВИПРАВЛЕННЯ", RED,
         ["if (syndrome != 0)", "  recv ^= 1 << (syndrome - 1)", "дані = біти з позицій 3,5,6,7"],
         "один XOR перевертає зламаний біт"),
    ]
    pw = W - px - 60
    ph = 132
    for i, (nm, col, lines, note) in enumerate(phases):
        y = my + 18 + i * (ph + 14)
        b += rect(px, y, pw, ph, "#fcfcfc", col, 2, 10)
        b += rect(px, y, pw, 26, col, col, 0, 10)
        b += text(px + 14, y + 19, nm, 13, "#fff", "start", "bold")
        for k, ln in enumerate(lines):
            b += mono(px + 16, y + 50 + k * 22, ln, 12.5, INK)
        b += text(px + 16, y + ph - 12, note, 10.5, col, "start", style="italic")
        # стрілка від матриці до фази (тільки від першої — щоб не плутати)
    # спільна підказка зліва-направо
    b += arrow(mx + 90 + 3.5 * cellw, my + 44 + 3 * cellh + 134, px - 14, my + 18 + ph / 2 + 8, GREEN, 2)
    b += text((mx + 90 + 3.5 * cellw + px) / 2, my + 44 + 3 * cellh + 128,
              "ті самі 3 маски", 10, GREEN, "middle", "bold")

    # ── низ: підсумок-висновок ──
    by = H - 70
    b += rect(60, by, W - 120, 52, "#f0fff2", GREEN, 1.8, 9)
    b += text(80, by + 22, "Чому 30 рядків вистачає:", 12.5, GREEN, "start", "bold")
    b += text(80, by + 42,
              "три фази — це триразове застосування трьох масок. Жодних таблиць і циклів пошуку: синдром сам показує адресу. "
              "Розширити до SECDED (§3.9.7) — це один зайвий загальний біт парності.",
              11, INK, "start")
    save("fig-r09-s6a-3-code-walk.svg", b)


if __name__ == "__main__":
    fig1_encode()
    fig2_syndrome()
    fig3_code_walk()
    print("r09-s6-a-hamming-codec figures done.")
