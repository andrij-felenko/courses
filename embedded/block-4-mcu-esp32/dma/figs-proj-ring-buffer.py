# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки ⚙️ r09-s4-a-ring-buffer.md
«Кільцевий буфер з нуля: індекси, межі, переповнення»

Рис. 4.9.4a.1  fig-r09-4a-1-ring-indices.svg
Рис. 4.9.4a.2  fig-r09-4a-2-full-empty.svg

Запуск: python figs-r09-s4-a-ring-buffer.py
Вивід: ./img/*.svg
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольорові акценти ───────────────────────────────────────────────────────
OCCUPIED = "#d0e8ff"    # зайнятий сектор (голубий)
OCC_STR  = "#2457d6"    # обведення зайнятого (синє)
FREE_CLR = "#f4f6f8"    # вільна комірка
ARROW_H  = "#c0392b"    # стрілка head (червона)
ARROW_T  = "#27ae60"    # стрілка tail (зелена)
ZERO_CLR = "#fff3cd"    # підсвічена комірка 0 (жовта)
ZERO_STR = "#b7861b"

# ──────────────────────────────────────────────────────────────────────────────
# Рис. 4.9.4a.1 — Кільцевий буфер: масив із N комірок, замкнений у коло
# ──────────────────────────────────────────────────────────────────────────────
def draw_ring_indices():
    W, H = 700, 430
    frags = []

    N = 10          # кількість комірок для ілюстрації
    cx, cy = 280, 210
    R_outer = 140   # зовнішній радіус клітинок
    R_inner = 90    # внутрішній (товщина сектора)
    label_r = (R_outer + R_inner) / 2  # мітки у середині сектора

    # індекси head і tail
    HEAD = 7
    TAIL = 2

    def cell_angle(i):
        """Кут центру i-ї комірки (у радіанах, 0 — нагорі, за годинниковою)."""
        return math.pi * (-0.5 + (i + 0.5) / N * 2)

    def sector_path(i, ri, ro):
        a0 = math.pi * (-0.5 + i / N * 2)
        a1 = math.pi * (-0.5 + (i + 1) / N * 2)
        gap = 0.02
        x0i, y0i = cx + ri * math.cos(a0 + gap), cy + ri * math.sin(a0 + gap)
        x1i, y1i = cx + ri * math.cos(a1 - gap), cy + ri * math.sin(a1 - gap)
        x0o, y0o = cx + ro * math.cos(a0 + gap), cy + ro * math.sin(a0 + gap)
        x1o, y1o = cx + ro * math.cos(a1 - gap), cy + ro * math.sin(a1 - gap)
        return (f'<path d="M{x0i:.1f},{y0i:.1f} L{x0o:.1f},{y0o:.1f} '
                f'A{ro:.1f},{ro:.1f} 0 0,1 {x1o:.1f},{y1o:.1f} '
                f'L{x1i:.1f},{y1i:.1f} '
                f'A{ri:.1f},{ri:.1f} 0 0,0 {x0i:.1f},{y0i:.1f} Z" ')

    # комірки
    for i in range(N):
        occupied = (TAIL <= i < HEAD)
        fill = OCCUPIED if occupied else FREE_CLR
        stroke = OCC_STR if occupied else LINE
        sw = 2.2 if occupied else 1.4

        # особливий акцент на комірку 0
        if i == 0:
            fill = ZERO_CLR
            stroke = ZERO_STR

        frags.append(sector_path(i, R_inner, R_outer) +
                     f'fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>')

        # числовий підпис
        a = cell_angle(i)
        lx = cx + label_r * math.cos(a)
        ly = cy + label_r * math.sin(a)
        frags.append(text(lx, ly + 5, str(i), size=13, bold=(i == 0), color=INK))

    # внутрішня пояснювальна рамка
    inner_box, _iw, _ih = textbox(cx, cy, "buf[N]", size=13,
                                  fill=FILL, stroke=MUTED, color=MUTED)
    frags.append(inner_box)

    # стрілки head і tail із кола
    def arm_arrow(idx, label, color, side):
        """Стрілка від комірки назовні (або всередину)."""
        a = cell_angle(idx)
        tip_x  = cx + (R_outer + 4)  * math.cos(a)
        tip_y  = cy + (R_outer + 4)  * math.sin(a)
        far_x  = cx + (R_outer + 50) * math.cos(a)
        far_y  = cy + (R_outer + 50) * math.sin(a)
        # лінія від комірки назовні
        frags.append(f'<line x1="{tip_x:.1f}" y1="{tip_y:.1f}" '
                     f'x2="{far_x:.1f}" y2="{far_y:.1f}" '
                     f'stroke="{color}" stroke-width="2.2" '
                     f'marker-end="url(#arrow)"/>')
        # підпис
        lbx = cx + (R_outer + 70) * math.cos(a)
        lby = cy + (R_outer + 70) * math.sin(a)
        frags.append(text(lbx, lby + 5, label, size=13, color=color, bold=True))

    arm_arrow(HEAD, "head", ARROW_H, 1)
    arm_arrow(TAIL, "tail",  ARROW_T, -1)

    # пояснення «зайнятий» ←→
    frags.append(text(cx, cy - R_outer - 18, "← зайнятий (tail → head) →",
                      size=12, color=OCC_STR))

    # позначка «після N−1 іде 0»
    a_n1 = cell_angle(N - 1)
    a_0  = cell_angle(0)
    mx   = cx + (R_outer + 28) * math.cos((a_n1 + a_0) / 2 - 0.2)
    my   = cy + (R_outer + 28) * math.sin((a_n1 + a_0) / 2 - 0.2)
    b0x, _w0, _h0 = textbox(mx, my, "N−1 → 0", size=11,
                             fill=ZERO_CLR, stroke=ZERO_STR, color=ZERO_STR)
    frags.append(b0x)

    # правий блок: формули обернення
    fx, fy = 510, 120
    frags.append(text(fx, fy, "Обернення індексу:", size=13, bold=True,
                      anchor="start", color=INK))
    formula_box = (
        '<rect x="470" y="130" width="210" height="86" rx="6" '
        'fill="#f4f6f8" stroke="#aaa" stroke-width="1.2"/>'
        + text(475, 150, "head = (head + 1) % N",      size=11, anchor="start", color=INK)
        + text(475, 168, "     // загальний дільник",  size=10, anchor="start", color=MUTED)
        + text(475, 188, "head = (head + 1) & (N−1)", size=11, anchor="start", color=INK)
        + text(475, 206, "     // N — степінь двійки", size=10, anchor="start", color=MUTED)
    )
    frags.append(formula_box)

    frags.append(text(fx, 240, "& (N−1) — один такт:", size=12, anchor="start", color=INK))
    frags.append(text(fx, 256, "% N — ділення (~30 тактів)", size=11, anchor="start", color=MUTED))
    frags.append(text(fx, 272, "Тому N беруть степенем 2.", size=11, anchor="start", color=INK))

    # підпис
    cap = "Рис. 4.9.4a.1. Кільцевий буфер: масив із N комірок, замкнений у коло."
    cap2 = "head — куди писати, tail — звідки читати. За N−1 іде 0 (обернення)."
    frags.append(text(W / 2, H - 28, cap,  size=11, color=MUTED))
    frags.append(text(W / 2, H - 13, cap2, size=11, color=MUTED))

    render(os.path.join(OUT, "fig-r09-4a-1-ring-indices.svg"), W, H, *frags)
    print("fig-r09-4a-1-ring-indices.svg OK")


# ──────────────────────────────────────────────────────────────────────────────
# Рис. 4.9.4a.2 — Фундаментальна неоднозначність head==tail: порожньо vs повно
# ──────────────────────────────────────────────────────────────────────────────
def draw_full_empty():
    W, H = 740, 430
    frags = []

    N = 8
    R_o = 110
    R_i = 68
    label_r = (R_o + R_i) / 2

    def cell_angle(i):
        return math.pi * (-0.5 + (i + 0.5) / N * 2)

    def sector_path(cx, cy, i, ri, ro):
        a0 = math.pi * (-0.5 + i / N * 2)
        a1 = math.pi * (-0.5 + (i + 1) / N * 2)
        g = 0.03
        x0i, y0i = cx + ri * math.cos(a0 + g), cy + ri * math.sin(a0 + g)
        x1i, y1i = cx + ri * math.cos(a1 - g), cy + ri * math.sin(a1 - g)
        x0o, y0o = cx + ro * math.cos(a0 + g), cy + ro * math.sin(a0 + g)
        x1o, y1o = cx + ro * math.cos(a1 - g), cy + ro * math.sin(a1 - g)
        return (f'<path d="M{x0i:.1f},{y0i:.1f} L{x0o:.1f},{y0o:.1f} '
                f'A{ro:.1f},{ro:.1f} 0 0,1 {x1o:.1f},{y1o:.1f} '
                f'L{x1i:.1f},{y1i:.1f} '
                f'A{ri:.1f},{ri:.1f} 0 0,0 {x0i:.1f},{y0i:.1f} Z" ')

    def draw_ring(cx, cy, occupied_all, title_text, title_color):
        # заголовок
        frags.append(text(cx, cy - R_o - 28, title_text, size=14, bold=True,
                           color=title_color))
        for i in range(N):
            fill = OCCUPIED if occupied_all else FREE_CLR
            stroke = OCC_STR if occupied_all else LINE
            sw = 2.0 if occupied_all else 1.4
            frags.append(sector_path(cx, cy, i, R_i, R_o) +
                         f'fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>')
            a = cell_angle(i)
            lx = cx + label_r * math.cos(a)
            ly = cy + label_r * math.sin(a)
            frags.append(text(lx, ly + 5, str(i), size=12, color=INK))

        # центральна мітка
        inner_b, _bw, _bh = textbox(cx, cy, "buf[N]", size=12,
                                     fill=FILL, stroke=MUTED, color=MUTED)
        frags.append(inner_b)

        # head і tail стрілки (обидва на index 0)
        HEAD_IDX = 0
        a = cell_angle(HEAD_IDX)
        # head (червона) трохи лівіше від tail (зелена)
        offset_h = -0.15
        offset_t = +0.15
        def ext_arrow(angle_offset, label, color):
            a2 = a + angle_offset
            tip_x = cx + (R_o + 4)  * math.cos(a2)
            tip_y = cy + (R_o + 4)  * math.sin(a2)
            far_x = cx + (R_o + 46) * math.cos(a2)
            far_y = cy + (R_o + 46) * math.sin(a2)
            frags.append(f'<line x1="{tip_x:.1f}" y1="{tip_y:.1f}" '
                         f'x2="{far_x:.1f}" y2="{far_y:.1f}" '
                         f'stroke="{color}" stroke-width="2.2" '
                         f'marker-end="url(#arrow)"/>')
            lbx = cx + (R_o + 64) * math.cos(a2)
            lby = cy + (R_o + 64) * math.sin(a2)
            frags.append(text(lbx, lby + 5, label, size=12, color=color, bold=True))

        ext_arrow(offset_h, "head", ARROW_H)
        ext_arrow(offset_t, "tail",  ARROW_T)

    # ─── Ліве кільце: ПОРОЖНЬО ───
    CX1, CY1 = 185, 210
    draw_ring(CX1, CY1, occupied_all=False,
              title_text="ПОРОЖНЬО",
              title_color="#888")

    frags.append(text(CX1, CY1 + R_o + 48, "head == tail == 0", size=12, color=INK))
    frags.append(text(CX1, CY1 + R_o + 65, "нічого не клали", size=11, color=MUTED))

    # ─── Роздільник ───
    MIDX = W // 2
    frags.append(f'<line x1="{MIDX}" y1="40" x2="{MIDX}" y2="{H - 80}" '
                 f'stroke="#ddd" stroke-width="2" stroke-dasharray="6,4"/>')
    frags.append(text(MIDX, H // 2, "vs", size=22, bold=True, color=MUTED))

    # ─── Праве кільце: ПОВНО ───
    CX2, CY2 = 560, 210
    draw_ring(CX2, CY2, occupied_all=True,
              title_text="ПОВНО",
              title_color=ARROW_H)

    frags.append(text(CX2, CY2 + R_o + 48, "head == tail == 0", size=12, color=INK))
    frags.append(text(CX2, CY2 + R_o + 65, "writer наздогнав reader", size=11, color=POS))

    # ─── Нижній блок «два виходи» ───
    bx = 50
    by = H - 72
    sol1, w1, h1 = textbox(200, by,
                             "−1 комірка:\nповно = next(head) == tail",
                             size=11, fill="#eef6ee", stroke="#27ae60",
                             color="#1a5c1a", pad=9)
    frags.append(sol1)

    sol2, w2, h2 = textbox(540, by,
                             "лічильник count:\nповно = count == N",
                             size=11, fill="#fdf0f0", stroke=POS,
                             color="#7a1a1a", pad=9)
    frags.append(sol2)

    # заголовок «два виходи»
    frags.append(text(W / 2, by - 22,
                       "Два класичні виходи:", size=12, bold=True, color=INK))

    # загальний підпис
    cap = ("Рис. 4.9.4a.2. head==tail — і «порожньо», і «повно»: "
           "однакові індекси, протилежний зміст.")
    frags.append(text(W / 2, H - 8, cap, size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r09-4a-2-full-empty.svg"), W, H, *frags)
    print("fig-r09-4a-2-full-empty.svg OK")


if __name__ == "__main__":
    draw_ring_indices()
    draw_full_empty()
    print("Usi figury zghenerovano ->", OUT)
