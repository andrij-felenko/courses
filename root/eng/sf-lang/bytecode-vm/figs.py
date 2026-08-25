# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Темні заливки для «машинного» боку (числа/код) — контраст «людина / машина».
DARK   = "#13202a"
DARKMC = "#101418"
GREENT = "#7fe0a0"   # моноширинні числа/команди на темному
GREYT  = "#6f8fa0"   # коментарі на темному
PAPER  = "#f6f4ec"   # «серединний» байткод — теплий папір


# ── three-levels: текст / байткод / рідний код — три щаблі ──────────────────────
def fig_three_levels():
    W, H = 760, 300
    p = []
    y, bh = 90, 150

    # ліворуч — вихідний текст (людина)
    lx, lw = 30, 210
    p.append(rect(lx, y, lw, bh, fill=DARK, stroke=INK, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, y + 28, "вихідний текст", size=12, color="#8fcf9f", bold=True))
    p.append(text(lx + lw / 2, y + 66, "x = a + b * 2", size=14, color="#eaf6ee", bold=True))
    p.append(text(lx + lw / 2, y + 96, "// зручно людині", size=11, color="#7a9a86", italic=True))
    p.append(text(lx + lw / 2, y + bh + 22, "розбирати щоразу — повільно", size=10, color=MUTED, italic=True))

    # посередині — байткод (вигадана машина)
    cx = W / 2
    mw = 220
    mx = cx - mw / 2
    p.append(rect(mx, y - 8, mw, bh + 16, fill=PAPER, stroke="#a98a2a", sw=2.4, rx=10))
    p.append(text(cx, y + 22, "БАЙТКОД", size=13, color="#7a6312", bold=True))
    p.append(text(cx, y + 40, "вигадана машина", size=10, color="#7a6312", italic=True))
    for i, s in enumerate(("PUSH a", "PUSH b", "PUSH 2", "MUL", "ADD")):
        p.append(text(cx, y + 66 + i * 17, s, size=12, color="#3a2c0e", bold=True))

    # праворуч — рідний код (один чіп)
    rx = W - 210 - 30
    rw = 210
    p.append(rect(rx, y, rw, bh, fill=DARKMC, stroke="#000000", sw=1.5, rx=8))
    p.append(text(rx + rw / 2, y + 28, "рідний машинний код", size=11, color="#7fa6bf", bold=True))
    for i, s in enumerate(("2B 01 04", "0C 1A 7C", "3A 41 00")):
        p.append(text(rx + rw / 2, y + 62 + i * 24, s, size=13, color=GREENT, bold=True))
    p.append(text(rx + rw / 2, y + bh + 22, "швидко, та лише для ОДНОГО ядра", size=10, color=MUTED, italic=True))

    # стрілки-містки
    p.append(arrow(lx + lw + 2, y + bh / 2, mx - 4, y + bh / 2, color=INK, sw=2.2))
    p.append(text((lx + lw + mx) / 2, y + bh / 2 - 10, "раз", size=9, color=FIELD, bold=True))
    p.append(arrow(mx + mw + 2, y + bh / 2, rx - 4, y + bh / 2, color=INK, sw=2.2))
    p.append(text((mx + mw + rx) / 2, y + bh / 2 - 10, "або/чи", size=9, color=MUTED))

    render(os.path.join(OUT, "three-levels.svg"), W, H, *p,
           title="Байткод — спільний місток між текстом і рідними числами")


# ── stack-eval: обчислення a + b*2 на стековій машині ───────────────────────────
def fig_stack_eval():
    W, H = 760, 340
    p = []
    steps = [
        ("PUSH a", ["a"]),
        ("PUSH b", ["a", "b"]),
        ("PUSH 2", ["a", "b", "2"]),
        ("MUL",    ["a", "b*2"]),
        ("ADD",    ["a+b*2"]),
    ]
    n = len(steps)
    colw = (W - 40) / n
    base_y = 250          # рівень «підлоги» стека
    cell = 30
    cw = 74
    for i, (cmd, st) in enumerate(steps):
        cx = 20 + colw * i + colw / 2
        # команда згори
        box, bw, bh = textbox(cx, 78, cmd, size=13, bold=True, fill=DARK,
                              stroke=INK, color="#eaf6ee", pad=10, min_w=84)
        p.append(box)
        # стек знизу вгору
        for j, v in enumerate(st):
            cyc = base_y - j * cell
            top = (j == len(st) - 1)
            p.append(rect(cx - cw / 2, cyc - cell + 4, cw, cell - 4,
                          fill=("#eef6ef" if top else FILL),
                          stroke=(FIELD if top else LINE),
                          sw=(2.2 if top else 1.4), rx=5))
            p.append(text(cx, cyc - 8, v, size=13, color=(FIELD if top else INK), bold=top))
        # підлога стека
        p.append(line(cx - cw / 2 - 6, base_y + 4, cx + cw / 2 + 6, base_y + 4, color=INK, sw=2.0))
        p.append(text(cx, base_y + 22, "верхівка ↑" if len(st) else "", size=9, color=MUTED))
        # стрілка до наступного
        if i < n - 1:
            p.append(arrow(cx + cw / 2 + 6, 150, cx + colw - cw / 2 - 6, 150, color=INK, sw=2.0))

    p.append(text(W / 2, H - 16,
                  "Кожна команда чіпає лише верхівку — тому команди короткі й без операндів",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "stack-eval.svg"), W, H, *p,
           title="Стекова машина рахує a + b*2")


# ── two-stages: переклад раз наперед / виконання щоразу ─────────────────────────
def fig_two_stages():
    W, H = 760, 320
    p = []

    # ── ліва панель: переклад (раз) ──
    p.append(rect(24, 58, 350, 232, fill="none", stroke="#dfeede", sw=2, rx=12))
    p.append(text(199, 84, "Переклад — РАЗ наперед", size=12, color=FIELD, bold=True))
    p.append(rect(60, 112, 120, 50, fill=DARK, stroke=INK, sw=1.8, rx=6))
    p.append(text(120, 142, "вихідний текст", size=11, color="#eaf6ee", bold=True))
    p.append(arrow(182, 137, 214, 137, color=INK, sw=2.2))
    box, bw, bh = textbox(268, 137, "компі-\nлятор", size=11, bold=True, fill=PAPER,
                          stroke="#a98a2a", color="#7a6312", pad=11)
    p.append(box)
    p.append(arrow(268, 162, 268, 200, color=FIELD, sw=2.4))
    p.append(rect(200, 202, 136, 52, fill=PAPER, stroke="#a98a2a", sw=2.2, rx=8))
    p.append(text(268, 226, "БАЙТКОД", size=12, color="#7a6312", bold=True))
    p.append(text(268, 244, "(можна зберегти)", size=9, color=MUTED))
    p.append(text(199, 278, "важкий розбір мови — тут, і лише раз", size=10, color=INK, bold=True))

    # ── права панель: виконання (щоразу) ──
    p.append(rect(390, 58, 350, 232, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(565, 84, "Виконання — ЩОРАЗУ при запуску", size=12, color=NEG, bold=True))
    p.append(rect(420, 108, 130, 52, fill=PAPER, stroke="#a98a2a", sw=2.0, rx=8))
    p.append(text(485, 138, "БАЙТКОД", size=12, color="#7a6312", bold=True))
    p.append(arrow(552, 134, 590, 134, color=NEG, sw=2.2))
    box2, bw2, bh2 = textbox(660, 134, "віртуальна\nмашина", size=11, bold=True,
                             fill="#eaf0fd", stroke=NEG, color=NEG, pad=12)
    p.append(box2)
    p.append(arrow(660, 134 + bh2 / 2 + 2, 660, 210, color=NEG, sw=2.4))
    p.append(rect(596, 212, 128, 44, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(660, 239, "результат", size=12, color=FIELD, bold=True))
    p.append(text(565, 278, "у гарячому циклі — лише дешеве виконання", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "two-stages.svg"), W, H, *p,
           title="Переклад і виконання розділені в часі")


# ── lineage: п-машина Вірта → UCSD Pascal / Smalltalk → JVM (винаходили заново) ──
def fig_lineage():
    W, H = 780, 300
    p = []
    axis_y = 210

    # горизонтальна вісь часу
    p.append(line(40, axis_y, W - 40, axis_y, color=INK, sw=2.0))
    p.append(arrow(W - 60, axis_y, W - 34, axis_y, color=INK, sw=2.0))
    p.append(text(W - 40, axis_y + 22, "час", size=10, color=MUTED, italic=True))

    # чотири віхи: (x, рік, назва, підпис)
    marks = [
        (120, "1972", "Smalltalk", "Xerox PARC\nоб'єкти + байткод"),
        (300, "1973", "Pascal-P", "ETH, група Вірта\nп-машина, стек"),
        (480, "1974", "UCSD Pascal", "К. Боулз\nна багато мікро-ЕОМ"),
        (680, "1991→96", "JVM / Java", "Green Project\n«написав раз…»"),
    ]
    for x, yr, name, sub in marks:
        p.append(line(x, axis_y - 6, x, axis_y + 6, color=INK, sw=2.0))
        p.append(text(x, axis_y + 22, yr, size=11, color=INK, bold=True))
        box, bw, bh = textbox(x, 96, name + "\n" + sub, size=11, bold=True,
                              fill=PAPER, stroke="#a98a2a", color="#3a2c0e", pad=9, min_w=118)
        p.append(box)
        p.append(line(x, 96 + bh / 2, x, axis_y - 8, color=LINE, sw=1.3, dash="3,3"))

    # наскрізна думка: та сама ідея, винайдена заново
    p.append(text(W / 2, 40, "Одна ідея — переносність через ВИГАДАНУ машину — визрівала заново",
                  size=13, color=FIELD, bold=True))
    p.append(text(W / 2, H - 14,
                  "щоразу той самий хід: не рідні числа чипа, а команди уявного процесора + тлумач-VM",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід ідеї байткоду: від п-машини до JVM")


if __name__ == "__main__":
    fig_three_levels()
    fig_stack_eval()
    fig_two_stages()
    fig_lineage()
    print("OK: figures written to", OUT)
