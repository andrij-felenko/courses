# -*- coding: utf-8 -*-
"""Фігури до теми «Символ мікросхеми на схемі».
Фігури:
  opamp.svg         — трикутник підсилювача: широка база-входи, вістря-вихід, живлення
  box.svg           — узагальнена рамка-мікросхема: піни, крапка-1, позначка U, групи виводів
  twoways.svg       — той самий чип двома способами: за фізичним порядком ніг vs за функцією
  triangle-flow.svg — (вставка hist-opamp-triangle) чому трикутник, а не квадрат/кружок: напрям у формі
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def pin_stub(x, y, dx, label=None, num=None, side="left"):
    """Короткий вивід від рамки + опц. внутрішня назва й зовнішній номер."""
    out = [line(x, y, x + dx, y, color=INK, sw=1.6)]
    if label is not None:
        lx = x + 6 if side == "left" else x - 6
        anc = "start" if side == "left" else "end"
        out.append(text(lx, y + 4, label, size=12, color=INK, anchor=anc))
    if num is not None:
        nx = x + dx - 4 if side == "left" else x + dx + 4
        anc = "end" if side == "left" else "start"
        out.append(text(nx, y - 5, str(num), size=11, color=MUTED, anchor=anc))
    return "".join(out)


# ── 1. Трикутник підсилювача ────────────────────────────────────────────────
def fig_opamp():
    W, H = 640, 380
    # вершини трикутника
    ax, ay = 250, 110      # лівий-верхній (база)
    bx, by = 250, 290      # лівий-нижній (база)
    cx, cy = 470, 200      # вістря (вихід)
    tri = ('<path d="M%d %d L%d %d L%d %d Z" fill="#f4f6f8" stroke="%s" '
           'stroke-width="2"/>' % (ax, ay, bx, by, cx, cy, INK))

    yin1, yin2 = 145, 255   # рівні двох входів
    parts = [tri]
    # входи від лівого боку
    parts.append(line(120, yin1, ax, yin1, color=INK, sw=1.8))
    parts.append(line(120, yin2, bx, yin2, color=INK, sw=1.8))
    parts.append(plus(ax + 22, yin1, r=10))
    parts.append(minus(ax + 22, yin2, r=10))
    parts.append(text(112, yin1 + 5, "вхід +", size=13, color=POS, anchor="end", bold=True))
    parts.append(text(112, yin2 + 5, "вхід −", size=13, color=NEG, anchor="end", bold=True))
    # вихід від вістря
    parts.append(line(cx, cy, 560, cy, color=INK, sw=1.8))
    parts.append(text(568, cy + 5, "вихід", size=13, color=INK, anchor="start", bold=True))
    # живлення зверху/знизу
    parts.append(line(330, ay + 38, 330, ay - 5, color=POS, sw=1.6))
    parts.append(text(330, ay - 12, "+живлення", size=11, color=POS))
    parts.append(line(330, by - 38, 330, by + 5, color=NEG, sw=1.6))
    parts.append(text(330, by + 18, "−живлення", size=11, color=NEG))
    # підписи «напрям» (унизу, поза дротами)
    parts.append(text(150, 350, "база широка — два входи", size=11,
                      color="#1c6b3a", anchor="middle"))
    parts.append(text(490, 350, "вістря вузьке — один вихід", size=11,
                      color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'opamp.svg'), W, H, *parts,
                  title="Трикутник підсилювача: форма сама показує напрям")


# ── 2. Узагальнена рамка-мікросхема ─────────────────────────────────────────
def fig_box():
    W, H = 620, 420
    bx, by, bw, bh = 230, 70, 160, 300
    parts = [rect(bx, by, bw, bh, fill="#f4f6f8", stroke=INK, sw=2, rx=4)]
    # позначка-власник + крапка піна 1
    parts.append(text(bx + bw / 2, by + 26, "U1", size=18, color=INK, bold=True))
    parts.append(text(bx + bw / 2, by + 46, "таймер", size=12, color=MUTED))
    parts.append(circle(bx + 16, by + 18, 5, fill=POS, stroke=POS, sw=1))
    parts.append(text(bx + 16, by + 40, "1", size=11, color=MUTED))

    # ліві піни (1..4 згори вниз)
    left = [("GND", 1), ("ТРИГ", 2), ("ВИХ", 3), ("СКИД", 4)]
    for i, (lab, n) in enumerate(left):
        y = by + 60 + i * 60
        parts.append(pin_stub(bx, y, -60, label=lab, num=n, side="left"))
    # праві піни (8..5 згори вниз — нумерація проти годинни­ка)
    right = [("Vcc", 8), ("РОЗР", 7), ("ПОРІГ", 6), ("КОНТР", 5)]
    for i, (lab, n) in enumerate(right):
        y = by + 60 + i * 60
        parts.append(pin_stub(bx + bw, y, 60, label=lab, num=n, side="right"))

    # пояснення збоку
    e1, w1, h1 = textbox(110, 95, "крапка/зріз —\nкут піна 1", size=11,
                         fill="#fdecea", stroke=POS, color=POS)
    parts.append(e1)
    e2, w2, h2 = textbox(540, 95, "ім'я виводу —\nщо він робить", size=11,
                         fill="#eef6ef", stroke=FIELD, color="#1c6b3a")
    parts.append(e2)
    parts.append(text(W / 2, 400, "номери йдуть проти годинникової: вниз лівим боком, угору правим",
                      size=11, color=MUTED))
    return render(os.path.join(IMG, 'box.svg'), W, H, *parts,
                  title="Чорна скринька: рамка ховає схему, показує тільки виводи")


# ── 3. Той самий чип двома способами ────────────────────────────────────────
def fig_twoways():
    W, H = 700, 360
    parts = []
    # --- зліва: за фізичним порядком ніг ---
    bx, by, bw, bh = 90, 80, 120, 220
    parts.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=INK, sw=1.8, rx=4))
    parts.append(text(bx + bw / 2, by + 24, "U2", size=15, color=INK, bold=True))
    parts.append(circle(bx + 13, by + 14, 4, fill=POS, stroke=POS, sw=1))
    lp = [("1A", 1), ("1B", 2), ("1Y", 3), ("2A", 4)]
    rp = [("Vcc", 8), ("2Y", 7), ("4B", 6), ("4A", 5)]
    for i, (lab, n) in enumerate(lp):
        parts.append(pin_stub(bx, by + 55 + i * 50, -42, label=lab, num=n, side="left"))
    for i, (lab, n) in enumerate(rp):
        parts.append(pin_stub(bx + bw, by + 55 + i * 50, 42, label=lab, num=n, side="right"))
    parts.append(text(bx + bw / 2 + 5, by + bh + 30, "за порядком ніг", size=12,
                      color=INK, anchor="middle", bold=True))
    parts.append(text(bx + bw / 2 + 5, by + bh + 48, "(як паяти)", size=11,
                      color=MUTED, anchor="middle"))

    # --- роздільник ---
    parts.append(line(350, 70, 350, 310, color=MUTED, sw=1, dash="5,5"))
    parts.append(text(350, 60, "той самий корпус", size=12, color=MUTED, anchor="middle", bold=True))

    # --- справа: за функцією (окремі вентилі) ---
    def gate(gx, gy, a, b, y, pa, pb, py):
        out = [('<path d="M%d %d L%d %d L%d %d Z" fill="#f4f6f8" stroke="%s" '
                'stroke-width="1.8"/>' % (gx, gy, gx, gy + 50, gx + 58, gy + 25, INK))]
        out.append(line(gx - 26, gy + 12, gx, gy + 12, color=INK, sw=1.5))
        out.append(line(gx - 26, gy + 38, gx, gy + 38, color=INK, sw=1.5))
        out.append(line(gx + 58, gy + 25, gx + 90, gy + 25, color=INK, sw=1.5))
        out.append(text(gx - 30, gy + 16, a, size=10, color=INK, anchor="end"))
        out.append(text(gx - 30, gy + 42, b, size=10, color=INK, anchor="end"))
        out.append(text(gx + 94, gy + 29, y, size=10, color=INK, anchor="start"))
        out.append(text(gx - 30, gy + 6, str(pa), size=9, color=MUTED, anchor="end"))
        out.append(text(gx - 30, gy + 52, str(pb), size=9, color=MUTED, anchor="end"))
        out.append(text(gx + 94, gy + 19, str(py), size=9, color=MUTED, anchor="start"))
        return "".join(out)

    parts.append(gate(470, 95, "1A", "1B", "1Y", 1, 2, 3))
    parts.append(gate(470, 200, "2A", "2B", "2Y", 4, 5, 7))
    parts.append(text(540, by + bh + 30, "за функцією", size=12,
                      color=INK, anchor="middle", bold=True))
    parts.append(text(540, by + bh + 48, "(як думати про логіку)", size=11,
                      color=MUTED, anchor="middle"))
    return render(os.path.join(IMG, 'twoways.svg'), W, H, *parts,
                  title="Один чип, два малюнки: символ — це не фото корпусу")


# ── 4. Чому трикутник, а не квадрат/кружок (вставка hist-opamp-triangle) ─────
def fig_triangle_flow():
    W, H = 700, 300
    parts = []

    def in_out(cx, label_dir):
        """Стрілки-входи зліва, стрілка-вихід справа — спільне для всіх фігур."""
        out = []
        out.append(arrow(cx - 86, 120, cx - 52, 120, color=MUTED, sw=1.6))
        out.append(arrow(cx - 86, 160, cx - 52, 160, color=MUTED, sw=1.6))
        out.append(arrow(cx + 52, 140, cx + 92, 140, color=MUTED, sw=1.8))
        return "".join(out)

    # --- квадрат: напрям непомітний ---
    qx = 150
    parts.append(rect(qx - 40, 110, 80, 60, fill=FILL, stroke=INK, sw=1.8, rx=4))
    parts.append(in_out(qx, None))
    parts.append(text(qx - 95, 116, "?", size=15, color=POS, anchor="end", bold=True))
    parts.append(text(qx - 95, 164, "?", size=15, color=POS, anchor="end", bold=True))
    parts.append(text(qx + 96, 144, "?", size=15, color=POS, anchor="start", bold=True))
    parts.append(text(qx, 200, "квадрат", size=13, color=INK, anchor="middle", bold=True))
    parts.append(text(qx, 220, "сторони рівні —", size=11, color=MUTED, anchor="middle"))
    parts.append(text(qx, 236, "де вхід, де вихід?", size=11, color=MUTED, anchor="middle"))

    # --- кружок: те саме ---
    cx0 = 350
    parts.append(circle(cx0, 140, 34, fill=FILL, stroke=INK, sw=1.8))
    parts.append(in_out(cx0, None))
    parts.append(text(cx0 - 95, 116, "?", size=15, color=POS, anchor="end", bold=True))
    parts.append(text(cx0 - 95, 164, "?", size=15, color=POS, anchor="end", bold=True))
    parts.append(text(cx0 + 96, 144, "?", size=15, color=POS, anchor="start", bold=True))
    parts.append(text(cx0, 200, "кружок", size=13, color=INK, anchor="middle", bold=True))
    parts.append(text(cx0, 220, "симетричний —", size=11, color=MUTED, anchor="middle"))
    parts.append(text(cx0, 236, "напрям не видно", size=11, color=MUTED, anchor="middle"))

    # --- трикутник: напрям у формі ---
    tx = 560
    ay = 110
    by = 170
    cx2, cy2 = tx + 48, 140
    parts.append('<path d="M%d %d L%d %d L%d %d Z" fill="#eef6ef" stroke="%s" '
                 'stroke-width="2"/>' % (tx - 40, ay, tx - 40, by, cx2, cy2, INK))
    parts.append(arrow(tx - 86, 120, tx - 40, 120, color=FIELD, sw=1.8))
    parts.append(arrow(tx - 86, 160, tx - 40, 160, color=FIELD, sw=1.8))
    parts.append(arrow(cx2, cy2, cx2 + 44, cy2, color=FIELD, sw=2))
    parts.append(text(tx - 95, 116, "вхід", size=11, color="#1c6b3a", anchor="end", bold=True))
    parts.append(text(tx - 95, 164, "вхід", size=11, color="#1c6b3a", anchor="end", bold=True))
    parts.append(text(cx2 + 50, 144, "вихід", size=11, color="#1c6b3a", anchor="start", bold=True))
    parts.append(text(tx + 4, 200, "трикутник", size=13, color="#1c6b3a", anchor="middle", bold=True))
    parts.append(text(tx + 4, 220, "база — вхід,", size=11, color="#1c6b3a", anchor="middle"))
    parts.append(text(tx + 4, 236, "вістря — вихід", size=11, color="#1c6b3a", anchor="middle"))

    return render(os.path.join(IMG, 'triangle-flow.svg'), W, H, *parts,
                  title="Чому трикутник: напрям сигналу вшито у форму")


if __name__ == "__main__":
    fig_opamp()
    fig_box()
    fig_twoways()
    fig_triangle_flow()
    print("ok: opamp.svg, box.svg, twoways.svg, triangle-flow.svg")
