# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки «Маркування чіпа: дата-код і ревізія кристала» (до теми 3.10.6).
Окремий скрипт вставки — головний figs.py розділу r10 НЕ чіпаємо (AUTHORING §9).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з розділів Модуля 3 (за §9 — кожен скрипт самодостатній).
Нумерація фігур вставки: Рис. 3.10.6c.k  (файли — з суфіксом -r10-s6c-).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
PKG = "#23272e"       # колір корпуса чіпа (чорна пластмаса)
PKGLT = "#3a4049"
GOLD = "#c9a227"
ORANGE = "#e08030"
PURPLE = "#5a3a8a"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = "Consolas, 'Courier New', monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 3.10.6c.1 — лазерний напис на корпусі, розкладений на поля ────────────
def fig_marking_decode():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 34, "Напис на корпусі чіпа: чотири рядки — чотири різні відомості", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий лазерний штамп розкладаємо на поля — кожне про щось своє",
              12.5, GREY, "middle", style="italic")

    # сам корпус чіпа (чорний прямокутник із лазерним написом)
    px, py, pw, ph = 285, 92, 330, 150
    s += rect(px, py, pw, ph, PKG, "#000000", 2, 10)
    # «крапка-ключ» першого виводу
    s += circle(px + 24, py + ph - 24, 7, "#11141a", "#555a63", 1.5)
    rows = [
        ("ACME MCU32-A", 21, GREEN),
        ("F8 2438 K", 20, BLUE),
        ("L734QH2", 16, ORANGE),
        ("rev C2", 19, RED),
    ]
    ry = py + 40
    row_y = []
    for txt, sz, _ in rows:
        s += text(px + pw / 2, ry, txt, sz, "#f2f2f2", "middle", "bold", mono=True)
        row_y.append(ry)
        ry += 30

    # пояснювальні картки ліворуч і праворуч від корпуса
    # (підпис, рядки опису, колір, бік: -1 ліворуч / +1 праворуч, до якого рядка веде)
    cards = [
        ("Партномер (part number)", ["що це за чіп: родина,", "розрядність, варіант корпуса.", "Дивимось у даташит саме за ним."], GREEN, -1, 0),
        ("Дата-код (date code) F8 2438", ["рік і робочий тиждень випуску:", "24 = 2024 рік, 38 = 38-й тиждень.", "Це коли зроблено, не ревізія!"], BLUE, +1, 1),
        ("Код партії / місця (lot)", ["якого заводу і прогону кристал;", "за ним відстежують брак, але", "для роботи зазвичай не потрібен."], ORANGE, -1, 2),
        ("Ревізія кристала (die rev / stepping)", ["версія самого кремнію.", "Саме до неї прив'язані errata —", "перелік відомих хиб цього кристала."], RED, +1, 3),
    ]
    cw, ch = 252, 96
    lx = 18
    rx = W - cw - 18
    # розставимо картки: дві ліворуч (рядки 0,2), дві праворуч (рядки 1,3)
    left_ys = [88, 300]
    right_ys = [88, 300]
    li = ri = 0
    for title, body, col, side, ridx in cards:
        if side < 0:
            bx, by = lx, left_ys[li]; li += 1
            ax_from = bx + cw
        else:
            bx, by = rx, right_ys[ri]; ri += 1
            ax_from = bx
        s += rect(bx, by, cw, ch, "#ffffff", col, 2.4, 10)
        s += rect(bx, by, cw, 28, col, col, 0, 0)
        s += text(bx + cw / 2, by + 19, title, 12.5, "#ffffff", "middle", "bold")
        yy = by + 46
        for ln in body:
            s += text(bx + 12, yy, ln, 11.8, INK, "start")
            yy += 16
        # стрілка від картки до відповідного рядка напису
        ty = row_y[ridx] - 5
        tx = px - 4 if side < 0 else px + pw + 4
        ay = by + ch / 2 if side < 0 else by + ch / 2
        s += arrow(ax_from, ay, tx, ty, col, 2.2)

    # нижня плашка-висновок
    cy = 478
    s += rect(60, cy - 22, W - 120, 34, "#fff7ef", ORANGE, 1.8, 8)
    s += text(W / 2, cy + 2,
              "Два рядки легко сплутати: дата-код каже КОЛИ зроблено, ревізія — ЯКА це версія кремнію. Errata тримаються ревізії.",
              12.5, INK, "middle", "bold")
    save("fig-r10-s6c-1-marking-decode.svg", s)


# ── Рис. 3.10.6c.2 — як читається дата-код YYWW ───────────────────────────────
def fig_date_code():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Дата-код YYWW: чотири цифри = рік і робочий тиждень", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "найпоширеніший формат; читається зліва направо як «коли зійшов із конвеєра»",
              12.5, GREY, "middle", style="italic")

    # велике поле з цифрами 2 4 3 8
    digits = ["2", "4", "3", "8"]
    dx0, dy = 250, 130
    dw, dh, gap = 80, 78, 16
    cols = [BLUE, BLUE, GREEN, GREEN]
    for i, d in enumerate(digits):
        x = dx0 + i * (dw + gap)
        s += rect(x, dy, dw, dh, "#f6f8fc" if i < 2 else "#f3f9f4", cols[i], 2.4, 10)
        s += text(x + dw / 2, dy + 56, d, 46, cols[i], "middle", "bold", mono=True)

    # дужки-групи під цифрами
    yy_y = dy + dh
    # рік (YY)
    s += line(dx0, yy_y + 14, dx0 + 2 * dw + gap, yy_y + 14, BLUE, 2.4)
    s += line(dx0, yy_y + 9, dx0, yy_y + 14, BLUE, 2.4)
    s += line(dx0 + 2 * dw + gap, yy_y + 9, dx0 + 2 * dw + gap, yy_y + 14, BLUE, 2.4)
    s += text(dx0 + dw + gap / 2, yy_y + 34, "YY = рік", 16, BLUE, "middle", "bold")
    s += text(dx0 + dw + gap / 2, yy_y + 54, "«24» → 2024", 13.5, INK, "middle")
    # тиждень (WW)
    wx0 = dx0 + 2 * (dw + gap)
    s += line(wx0, yy_y + 14, wx0 + 2 * dw + gap, yy_y + 14, GREEN, 2.4)
    s += line(wx0, yy_y + 9, wx0, yy_y + 14, GREEN, 2.4)
    s += line(wx0 + 2 * dw + gap, yy_y + 9, wx0 + 2 * dw + gap, yy_y + 14, GREEN, 2.4)
    s += text(wx0 + dw + gap / 2, yy_y + 34, "WW = тиждень", 16, GREEN, "middle", "bold")
    s += text(wx0 + dw + gap / 2, yy_y + 54, "«38» → 38-й тиждень", 13.5, INK, "middle")

    # стрічка-календар: 52 поділки, 38-та підсвічена
    cal_y = 320
    cal_x0, cal_w = 130, W - 260
    n = 52
    step = cal_w / n
    s += rect(cal_x0, cal_y, cal_w, 26, "#ffffff", GREY, 1.5, 4)
    for w in range(1, n):
        gx = cal_x0 + w * step
        s += line(gx, cal_y, gx, cal_y + 26, FAINT, 1)
    # підсвітити тиждень 38
    hx = cal_x0 + 37 * step
    s += rect(hx, cal_y, step, 26, GREEN, GREEN, 0, 0)
    s += arrow(hx + step / 2, cal_y - 18, hx + step / 2, cal_y - 2, GREEN, 2.2)
    s += text(hx + step / 2, cal_y - 24, "тиждень 38 ≈ кінець вересня", 12.5, GREEN, "middle", "bold")
    s += text(cal_x0, cal_y + 46, "січ", 11.5, GREY, "start")
    s += text(cal_x0 + cal_w, cal_y + 46, "груд", 11.5, GREY, "end")
    s += text(W / 2, cal_y + 46, "рік розбито на 52 робочі тижні", 12, GREY, "middle", style="italic")

    save("fig-r10-s6c-2-date-code.svg", s)


# ── Рис. 3.10.6c.3 — чому errata прив'язані до ревізії ─────────────────────────
def fig_errata_revision():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому errata тримаються ревізії кристала", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ревізія = набір фотомасок; хиба сидить у масках, тож зникає лише з новим набором",
              12.5, GREY, "middle", style="italic")

    # три «кристали»-стовпчики: rev B0 (баг), rev C0 (виправлено), і чому
    cols = [
        ("rev B0", RED, "масковий набір №1", ["баг X живе тут:", "у самому кремнії", "перелічений у errata"], False),
        ("rev C0", GREEN, "масковий набір №2", ["маски змінено →", "баг X прибрано;", "errata X закрито"], True),
    ]
    cw, chh = 230, 180
    cx0 = 70
    cgap = 70
    for i, (name, col, masks, body, fixed) in enumerate(cols):
        bx = cx0 + i * (cw + cgap)
        by = 92
        s += rect(bx, by, cw, chh, "#fbfbfb", col, 2.6, 12)
        s += rect(bx, by, cw, 32, col, col, 0, 0)
        s += text(bx + cw / 2, by + 22, name + "  (stepping)", 15, "#ffffff", "middle", "bold", mono=True)
        # «кристал» усередині
        dx, dy, dw2, dh2 = bx + 30, by + 48, cw - 60, 60
        s += rect(dx, dy, dw2, dh2, "#eef2f6", "#7a8590", 1.8, 4)
        # сітка ліній — натяк на масковані шари
        for k in range(1, 5):
            s += line(dx + k * dw2 / 5, dy, dx + k * dw2 / 5, dy + dh2, FAINT, 1)
        if fixed:
            s += text(dx + dw2 / 2, dy + 36, "✓", 30, GREEN, "middle", "bold")
        else:
            s += text(dx + dw2 / 2, dy + 37, "⚠ X", 22, RED, "middle", "bold")
        s += text(bx + cw / 2, dy + dh2 + 22, masks, 12, INK, "middle", style="italic")
        yy = dy + dh2 + 42
        for ln in body:
            s += text(bx + cw / 2, yy, ln, 12, INK, "middle")
            yy += 17

    # стрілка «новий набір масок» між стовпчиками
    ax = cx0 + cw
    s += arrow(ax + 6, 175, ax + cgap - 6, 175, INK, 2.6)
    s += text(ax + cgap / 2, 160, "новий", 11.5, INK, "middle", "bold")
    s += text(ax + cgap / 2, 196, "набір", 11.5, INK, "middle", "bold")
    s += text(ax + cgap / 2, 210, "масок", 11.5, INK, "middle", "bold")

    # права колонка — що з цим робить програма
    rx, ry, rw, rh = 600, 92, 250, 180
    s += rect(rx, ry, rw, rh, "#f3f0f8", PURPLE, 2.4, 12)
    s += rect(rx, ry, rw, 32, PURPLE, PURPLE, 0, 0)
    s += text(rx + rw / 2, ry + 22, "Як цим користується код", 13.5, "#ffffff", "middle", "bold")
    steps = [
        "1. читаємо регістр ID:",
        "   там лежить номер ревізії",
        "2. дивимось errata саме",
        "   цієї ревізії",
        "3. якщо баг тут — вмикаємо",
        "   обхід (workaround)",
    ]
    yy = ry + 52
    for ln in steps:
        s += text(rx + 14, yy, ln, 12, INK, "start", mono=(ln.strip()[0].isdigit() is False))
        yy += 21

    # нижня плашка: суть
    cy = 360
    s += rect(60, cy, W - 120, 92, "#fff7ef", ORANGE, 1.8, 10)
    s += text(W / 2, cy + 26,
              "Суть: errata — це «паспорт відомих хиб» КОНКРЕТНОЇ ревізії, а не чіпа взагалі.",
              14, INK, "middle", "bold")
    s += text(W / 2, cy + 50,
              "Та сама родина в rev B0 і rev C0 може поводитися по-різному: один список хиб закрито, інший — ще ні.",
              12.6, INK, "middle")
    s += text(W / 2, cy + 72,
              "Тому в errata кожен рядок має колонку «у яких ревізіях є», а драйвер обходить баг лише там, де він справді живе.",
              12.6, INK, "middle")

    save("fig-r10-s6c-3-errata-revision.svg", s)


if __name__ == "__main__":
    fig_marking_decode()
    fig_date_code()
    fig_errata_revision()
    print("done.")
