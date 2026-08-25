# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Граф об'єктів у композиційному корені: від листя до кореня ────────────────
def fig_graph():
    W, H = 900, 620
    frags = []

    # межа композиційного кореня — велика рамка «на краю програми»
    bx, by, bw, bh = 300, 66, 470, 500
    frags.append(rect(bx, by, bw, bh, fill="#f6faf6", stroke=FIELD, sw=2.2, rx=12))
    frags.append(text(bx + bw / 2, by + 24, "Композиційний корінь (край програми)",
                      size=14, bold=True, color=FIELD))

    cx = bx + bw / 2   # спільна вісь вузлів

    # рівні згори вниз: корінь → середина → листя
    y_root = 150
    y_gate = 250
    y_http = 350
    y_leaf = 470

    # вузол-корінь
    root, rw, rh = textbox(cx, y_root, "PaymentService\n(верхівка задуму)",
                           size=13, bold=True, pad=13, fill="#eef4ff",
                           stroke=INK, sw=2.0, min_w=250)
    frags.append(root)
    # середина
    gate, gw, gh = textbox(cx, y_gate, "StripeGateway",
                           size=13, pad=12, fill="#f2faf5", stroke=FIELD,
                           sw=1.8, min_w=190)
    frags.append(gate)
    http, hw, hh = textbox(cx, y_http, "HttpClient",
                           size=13, pad=12, fill="#f2faf5", stroke=FIELD,
                           sw=1.8, min_w=190)
    frags.append(http)

    # два листки поруч, широко рознесені
    lx1, lx2 = cx - 110, cx + 110
    cfg, cw, ch = textbox(lx1, y_leaf, "Config",
                          size=12, pad=11, fill="#fdf6ec", stroke=MUTED,
                          sw=1.6, min_w=120)
    frags.append(cfg)
    log, lw2, lh2 = textbox(lx2, y_leaf, "Logger",
                            size=12, pad=11, fill="#fdf6ec", stroke=MUTED,
                            sw=1.6, min_w=120)
    frags.append(log)

    # стрілки «мені потрібен ось цей» — від вузла ВНИЗ до його залежності
    def down(y1half, y2half, x1, x2, ytop, ybot, color=INK, sw=2.2):
        frags.append(arrow(x1, ytop, x2, ybot, color=color, sw=sw))

    # PaymentService → StripeGateway
    frags.append(arrow(cx, y_root + rh / 2 + 5, cx, y_gate - gh / 2 - 5, color=INK, sw=2.3))
    # StripeGateway → HttpClient
    frags.append(arrow(cx, y_gate + gh / 2 + 5, cx, y_http - hh / 2 - 5, color=INK, sw=2.3))
    # HttpClient → Config (ліворуч-вниз) і → Logger (праворуч-вниз)
    frags.append(arrow(cx - 8, y_http + hh / 2 + 5, lx1, y_leaf - ch / 2 - 5, color=INK, sw=2.1))
    frags.append(arrow(cx + 8, y_http + hh / 2 + 5, lx2, y_leaf - lh2 / 2 - 5, color=INK, sw=2.1))
    # PaymentService теж прямо просить Logger — довга бічна стрілка праворуч
    frags.append(arrow(cx + rw / 2 + 4, y_root + 6, lx2 + lw2 / 2 - 6, y_leaf - lh2 / 2 - 4,
                       color=MUTED, sw=1.6))

    # підпис зв'язку — у вільній смузі між лівою стінкою рамки й колонкою вузлів
    frags.append(text((bx + (cx - rw / 2)) / 2, (y_root + y_gate) / 2 + 4, "потрібен",
                      size=11, italic=True, color=MUTED, anchor="middle"))

    # напрямок збірки — стрілка-гід ЗЛІВА, поза рамкою кореня
    ax = bx - 46
    frags.append(arrow(ax, y_leaf, ax, y_root, color=POS, sw=2.6))
    frags.append(text(ax - 12, y_leaf + 24, "листя", size=12, bold=True,
                      color=POS, anchor="middle"))
    frags.append(text(ax - 12, y_root - 18, "корінь", size=12, bold=True,
                      color=POS, anchor="middle"))
    # вертикальний підпис напряму збірки
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" '
                 'fill="%s" text-anchor="middle" font-weight="700" '
                 'transform="rotate(-90 %.1f %.1f)">порядок збірки</text>'
                 % (ax - 34, (y_root + y_leaf) / 2, FONT, POS, ax - 34, (y_root + y_leaf) / 2))

    render(os.path.join(IMG, 'graph.svg'), W, H, *frags,
           title="Граф об'єктів: збірка від листя до кореня в композиційному корені")


# ── Контейнер: реєстрація (таблиця) → розв'язання (обхід графа) ───────────────
def fig_container():
    W, H = 1040, 560
    frags = []

    # роздільник панелей
    frags.append(line(W / 2, 74, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: РЕЄСТРАЦІЯ — таблиця відповідностей ──
    lcx = W / 4
    frags.append(text(lcx, 58, "Реєстрація: таблиця «обіцянка → реалізація»",
                      size=14, bold=True))

    rows = [
        ("PaymentService", "PaymentService"),
        ("PaymentGateway", "StripeGateway"),
        ("HttpClient",     "HttpClient"),
        ("Logger",         "FileLogger"),
    ]
    tx, ty, colw, rowh = lcx - 210, 100, 190, 54
    gap = 34   # проміжок між колонками під стрілку
    for i, (iface, impl) in enumerate(rows):
        y = ty + i * (rowh + 12)
        # ліва клітина — обіцянка (інтерфейс)
        frags.append(fitbox(tx, y, colw, rowh, iface, size=13, bold=True,
                            fill="#eef4ff", stroke=INK, sw=1.6))
        # права клітина — реалізація
        frags.append(fitbox(tx + colw + gap, y, colw, rowh, impl, size=13,
                            fill="#fdecea", stroke=POS, sw=1.6))
        # стрілка між ними
        frags.append(arrow(tx + colw + 4, y + rowh / 2,
                           tx + colw + gap - 4, y + rowh / 2, color=MUTED, sw=1.8))

    frags.append(text(lcx, ty + 4 * (rowh + 12) + 12,
                      "bind(обіцянка, реалізація)", size=12, italic=True, color=MUTED))

    # ── ПРАВА панель: РОЗВ'ЯЗАННЯ — обхід графа за таблицею ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 58, "Розв'язання: resolve(верхівка) обходить граф",
                      size=14, bold=True))

    # каскад «сходинками»: resolve спускається до листя й піднімає готове
    steps = [
        ("resolve(PaymentService)", 0,  INK,   "#eef4ff"),
        ("треба PaymentGateway", 1,  FIELD, "#f2faf5"),
        ("треба HttpClient",     2,  FIELD, "#f2faf5"),
        ("треба Logger",         3,  MUTED, "#fdf6ec"),
        ("Logger готовий →",       3,  POS,   "#fdecea"),
        ("HttpClient готовий →",    2,  POS,   "#fdecea"),
        ("StripeGateway готовий →", 1,  POS,   "#fdecea"),
        ("PaymentService готовий",  0,  POS,   "#fdecea"),
    ]
    sx0, sy0, indent, sh = rcx - 210, 96, 40, 42
    for i, (label, depth, col, fill) in enumerate(steps):
        y = sy0 + i * (sh + 6)
        x = sx0 + depth * indent
        w = 300 - depth * indent
        frags.append(fitbox(x, y, w, sh, label, size=12, bold=True,
                            fill=fill, stroke=col, sw=1.5, color=col))

    frags.append(text(rcx, sy0 + 8 * (sh + 6) + 8,
                      "вниз до листя — угору готовий граф", size=12,
                      italic=True, color=INK))

    render(os.path.join(IMG, 'container.svg'), W, H, *frags,
           title="DI-контейнер: реєстрація таблиці й автоматичний обхід графа")


# ── Виявлення циклу: стек «зараз будуються» ловить зворотну стрілку ───────────
def fig_cycle():
    W, H = 1000, 560
    frags = []

    frags.append(text(W / 2, 56, "Виявлення циклу: стек «зараз будуються» ловить зворотну стрілку",
                      size=15, bold=True))

    # ── ЛІВА панель: стек рекурсії resolve, що росте вглиб ──
    lx = 120
    frags.append(text(lx + 120, 100, "стек «resolving»", size=13, bold=True, color=INK))
    frags.append(text(lx + 120, 120, "(хто зараз у процесі збірки)", size=11,
                      italic=True, color=MUTED))

    frames = ["A  (resolve A)", "B  (A просить B)", "C  (B просить C)"]
    fx, fy, fw, fh = lx, 140, 240, 56
    for i, lab in enumerate(frames):
        y = fy + i * (fh + 14)
        frags.append(fitbox(fx, y, fw, fh, lab, size=13, bold=True,
                            fill="#eef4ff", stroke=INK, sw=1.8))
        # стрілка «просить» униз до наступного кадру
        if i < len(frames) - 1:
            frags.append(arrow(fx + fw / 2, y + fh + 2, fx + fw / 2, y + fh + 12,
                               color=MUTED, sw=1.8))

    # C знову просить A — кадр A ВЖЕ у стеку → цикл
    yC = fy + 2 * (fh + 14)
    yA = fy
    # зворотна дуга праворуч від стека: від низу C вгору до A
    ax = fx + fw + 46
    frags.append(line(fx + fw + 4, yC + fh / 2, ax, yC + fh / 2, color=POS, sw=2.4))
    frags.append(line(ax, yC + fh / 2, ax, yA + fh / 2, color=POS, sw=2.4))
    frags.append(arrow(ax, yA + fh / 2, fx + fw + 4, yA + fh / 2, color=POS, sw=2.4))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" '
                 'fill="%s" text-anchor="middle" font-weight="700" '
                 'transform="rotate(-90 %.1f %.1f)">C просить A</text>'
                 % (ax + 20, (yA + yC) / 2 + fh / 2, FONT, POS, ax + 20, (yA + yC) / 2 + fh / 2))

    # ── ПРАВА панель: перевірка на вході resolve ──
    rx = 600
    frags.append(text(rx + 150, 100, "перевірка на вході resolve(T)",
                      size=13, bold=True, color=INK))

    checks = [
        ("T уже в кеші?  → віддати збережене", POS,   "#fdecea"),
        ("T уже у стеку resolving?  → ЦИКЛ!", POS,   "#fdecea"),
        ("інакше: клади T у стек, будуй далі", FIELD, "#f2faf5"),
        ("зібрав T → знімай зі стека, у кеш",   FIELD, "#f2faf5"),
    ]
    cx, cy, cw, chh = rx, 130, 320, 52
    for i, (lab, col, fill) in enumerate(checks):
        y = cy + i * (chh + 14)
        frags.append(fitbox(cx, y, cw, chh, lab, size=12, bold=True,
                            fill=fill, stroke=col, sw=1.6, color=INK))

    frags.append(text(rx + 150, cy + 4 * (chh + 14) + 10,
                      "цикл ловиться раніше, ніж стек переповниться",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, 'cycle.svg'), W, H, *frags,
           title="Виявлення циклічної залежності стеком «зараз будуються»")


# ── Хроніка двох імен: 2004 «dependency injection» → 2011 «composition root» ──
def fig_timeline():
    W, H = 1120, 520
    frags = []

    # ── горизонтальна вісь часу ──
    axis_y = 260
    x0, x1 = 90, W - 60
    frags.append(arrow(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(text(x1 - 6, axis_y - 16, "час", size=13, italic=True,
                      color=MUTED, anchor="end"))

    # позиції двох віх на осі (широко рознесені, щоб написи не зустрілися)
    x2004 = 440
    x2011 = 830

    # засічки-крапки на осі
    for xv in (x2004, x2011):
        frags.append(circle(xv, axis_y, 8, fill=POS, stroke="#8a2820", sw=2))

    # ── ліворуч від першої віхи, ПІД віссю: тло-безлад «розмите IoC» ──
    # (осторонь від осі та від блоку assembler, щоб лінія не перетинала напис)
    ctx, cw, ch = textbox(190, axis_y + 90, "кін. 1990-х – поч. 2000-х\nусе — «інверсія\nкерування (IoC)»",
                          size=12, pad=12, fill="#f3f4f6", stroke=MUTED,
                          sw=1.6, color=MUTED, min_w=210)
    frags.append(ctx)
    # тонка засічка від осі вниз до тла (ліворуч від віхи 2004, повз написи)
    frags.append(line(190, axis_y + 6, 190, axis_y + 90 - ch / 2 - 4,
                      color=MUTED, sw=1.2, dash="4,4"))

    # ── ВІХА 2004 (над віссю) ──
    frags.append(line(x2004, axis_y - 8, x2004, axis_y - 70, color=INK, sw=1.8))
    frags.append(text(x2004, axis_y - 82, "січень 2004", size=14, bold=True, color=INK))
    box04, w04, h04 = textbox(x2004, axis_y - 158,
                              "Мартін Фаулер\n«dependency injection»\n(вужче за IoC)",
                              size=13, bold=True, pad=13, fill="#eef4ff",
                              stroke=INK, sw=2.0, min_w=260)
    frags.append(box04)

    # ── ВІХА 2004 (під віссю): згадка про assembler ──
    frags.append(line(x2004, axis_y + 8, x2004, axis_y + 58, color=MUTED, sw=1.6))
    asm, wa, ha = textbox(x2004, axis_y + 106,
                          "мимохідь — «assembler»:\nокремий складач графа",
                          size=12, pad=12, fill="#fdf6ec", stroke=MUTED,
                          sw=1.6, color=INK, min_w=260)
    frags.append(asm)

    # ── ВІХА 2011 (над віссю) ──
    frags.append(line(x2011, axis_y - 8, x2011, axis_y - 70, color=INK, sw=1.8))
    frags.append(text(x2011, axis_y - 82, "липень 2011", size=14, bold=True, color=INK))
    box11, w11, h11 = textbox(x2011, axis_y - 158,
                              "Марк Симан\n«composition root»\n(єдине місце на краю)",
                              size=13, bold=True, pad=13, fill="#f2faf5",
                              stroke=FIELD, sw=2.0, min_w=260)
    frags.append(box11)

    # ── нитка «складач дозрів у корінь» під віссю, між двома віхами ──
    ay = axis_y + 188
    frags.append(arrow(x2004, ay, x2011, ay, color=POS, sw=1.8))
    frags.append(text((x2004 + x2011) / 2, ay - 12,
                      "сім років практики: «хто зшиває» → «де саме зшивати»",
                      size=12, italic=True, color=POS))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *frags,
           title="Дві дати, два імені: від складача Фаулера до кореня Симана")


if __name__ == "__main__":
    fig_graph()
    fig_container()
    fig_cycle()
    fig_timeline()
    print("figures written to", IMG)
