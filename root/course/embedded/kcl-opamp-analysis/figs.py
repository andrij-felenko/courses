# -*- coding: utf-8 -*-
"""Фігури кроку курсу «KCL у вузлах схем на ОП»
(root/course/embedded/kola/kcl-opamp-analysis).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми в ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, plus, minus, INK, MUTED, POS, NEG, FIELD, FILL,
                    LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── допоміжне ───────────────────────────────────────────────────────────────
def opamp(cx, cy, size=70, vminus_top=True):
    """Трикутник ОП. Повертає (svg, in_minus_xy, in_plus_xy, out_xy).
    Вершина дивиться праворуч (вихід справа). Входи зліва."""
    half = size / 2
    apex_x = cx + half
    top = (cx - half, cy - half)
    bot = (cx - half, cy + half)
    apex = (apex_x, cy)
    s = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" '
         'fill="#fff" stroke="%s" stroke-width="2"/>'
         % (top[0], top[1], bot[0], bot[1], apex[0], apex[1], INK))
    # позиції входів на лівій грані
    y_up = cy - half * 0.45
    y_dn = cy + half * 0.45
    if vminus_top:
        in_minus = (cx - half, y_up)
        in_plus = (cx - half, y_dn)
        s += text(cx - half + 12, y_up + 5, "−", size=18, color=NEG, bold=True)
        s += text(cx - half + 12, y_dn + 6, "+", size=18, color=POS, bold=True)
    else:
        in_plus = (cx - half, y_up)
        in_minus = (cx - half, y_dn)
        s += text(cx - half + 12, y_up + 6, "+", size=18, color=POS, bold=True)
        s += text(cx - half + 12, y_dn + 5, "−", size=18, color=NEG, bold=True)
    out_xy = apex
    return s, in_minus, in_plus, out_xy


def res_h(cx, cy, label, w=58, h=18, lab_dy=-9, italic=True, color=INK):
    s = rect(cx - w / 2, cy - h / 2, w, h, fill="#fff", stroke=INK, sw=2, rx=3)
    s += text(cx, cy + lab_dy - h / 2, label, size=13, bold=True, italic=italic, color=color)
    return s


def node_dot(cx, cy, r=4.5):
    return circle(cx, cy, r, fill=INK, stroke=INK, sw=1)


def gnd(cx, cy, w=18):
    s = line(cx, cy, cx, cy + 8)
    s += line(cx - w / 2, cy + 8, cx + w / 2, cy + 8, sw=2)
    s += line(cx - w / 2 + 4, cy + 12, cx + w / 2 - 4, cy + 12, sw=2)
    s += line(cx - w / 2 + 8, cy + 16, cx + w / 2 - 8, cy + 16, sw=2)
    return s


# ── Фігура 1: вузол «−» як вузол KCL (summing junction) ──────────────────────
def fig_summing_node():
    W, H = 760, 430
    op_cx, op_cy = 470, 200
    s, vm, vp, vo = opamp(op_cx, op_cy, size=86)

    node_x, node_y = vm[0] - 70, vm[1]      # підсумовувальний вузол лівіше входу
    # три входи зліва
    ys = [node_y - 78, node_y, node_y + 78]
    labels = ["V₁", "V₂", "V₃"]
    rlabs = ["R₁", "R₂", "R₃"]
    body = ""
    for i, (yy, vl, rl) in enumerate(zip(ys, labels, rlabs)):
        sx = 70
        body += text(sx - 8, yy + 5, vl, size=15, bold=True, anchor="end")
        body += line(sx, yy, sx + 40, yy, sw=2)
        body += res_h(sx + 40 + 29, yy, rl)
        body += line(sx + 40 + 58, yy, node_x, yy, sw=2)
        # стрілка струму всередину вузла
        body += arrow(node_x - 96, yy, node_x - 60, yy, color=POS, sw=2)
        body += text(node_x - 78, yy - 9, "I%d" % (i + 1), size=12, color=POS, italic=True)
    # звести всі три на вузол
    body += line(node_x, ys[0], node_x, ys[2], sw=2)
    body += line(node_x, node_y, vm[0], vm[1], sw=2)
    body += node_dot(node_x, node_y)
    body += text(node_x - 8, node_y + 42, "вузол «−»", size=13, bold=True, anchor="middle")
    body += text(node_x - 8, node_y + 60, "(V₋ = 0)", size=12, color=NEG, anchor="middle")

    # зворотний зв'язок Rf
    fb_y = node_y - 130
    body += line(node_x, node_y, node_x, fb_y, sw=2)
    body += line(node_x, fb_y, op_cx + 110, fb_y, sw=2)
    body += res_h((node_x + op_cx + 110) / 2, fb_y, "Rf")
    body += line(op_cx + 110, fb_y, op_cx + 110, vo[1], sw=2)
    body += arrow(node_x + 120, fb_y, node_x + 84, fb_y, color=NEG, sw=2)
    body += text(node_x + 102, fb_y - 9, "If", size=12, color=NEG, italic=True)

    # вхід «+» на землю
    body += line(vp[0], vp[1], vp[0] - 40, vp[1], sw=2)
    body += gnd(vp[0] - 40, vp[1])

    # вихід
    body += line(vo[0], vo[1], op_cx + 110, vo[1], sw=2)
    body += node_dot(op_cx + 110, vo[1])
    body += line(op_cx + 110, vo[1], op_cx + 150, vo[1], sw=2)
    body += text(op_cx + 158, vo[1] + 5, "Vout", size=15, bold=True, anchor="start")

    # рамка з рівнянням балансу
    eqbody, ew, eh = textbox(W / 2, H - 52,
                             "KCL у вузлі «−»:   I1 + I2 + I3 = If\n"
                             "у вхід струму нема  →  весь струм іде у Rf",
                             size=14, fill="#eef7f0", stroke=FIELD, sw=1.5)

    render(out("summing-node.svg"), W, H, s, body, eqbody)


# ── Фігура 2: універсальний рецепт ──────────────────────────────────────────
def fig_recipe():
    W, H = 760, 430
    steps = [
        ("1", "Перевір зв'язок", "петля йде на «−» → правила діють"),
        ("2", "Постав V₋", "V₋ = V₊ (віртуальне коротке)"),
        ("3", "Признач струми", "кожен резистор: I = ΔV / R"),
        ("4", "Один KCL у «−»", "Σ струмів = 0 (у вхід — нуль)"),
        ("5", "Розв'яжи", "один рядок → Vout"),
    ]
    body = ""
    x = 40
    bw = (W - 2 * 40 - 4 * 16) / 5
    by = 96
    bh = 210
    for i, (n, t, d) in enumerate(steps):
        bx = x + i * (bw + 16)
        col = FIELD if i == 3 else LINE
        fill = "#eef7f0" if i == 3 else FILL
        body += rect(bx, by, bw, bh, fill=fill, stroke=col, sw=2 if i == 3 else 1.5)
        body += circle(bx + bw / 2, by + 30, 16, fill="#fff", stroke=col, sw=2)
        body += text(bx + bw / 2, by + 36, n, size=17, bold=True, color=col)
        body += fitbox(bx + 8, by + 56, bw - 16, 56, t, size=13, bold=True,
                       fill="none", stroke="none")
        body += fitbox(bx + 6, by + 116, bw - 12, 80, d, size=11, color=MUTED,
                       fill="none", stroke="none")
        if i < 4:
            ax = bx + bw + 2
            body += arrow(ax, by + bh / 2, ax + 12, by + bh / 2, sw=2)

    note, nw, nh = textbox(W / 2, by + bh + 56,
                           "Жодних формул напам'ять: одне рівняння у вузлі «−»\n"
                           "розкриває інвертуючий, суматор, інтегратор — будь-яку схему",
                           size=13, fill="#fbf7e9", stroke="#caa83a", sw=1.5)
    render(out("recipe.svg"), W, H, body, note,
           title="Один рецепт на всі схеми з від'ємним зв'язком")


# ── Фігура 3: інтегратор — ємнісний струм у тому самому балансі ──────────────
def fig_integrator():
    W, H = 720, 380
    op_cx, op_cy = 430, 170
    s, vm, vp, vo = opamp(op_cx, op_cy, size=80)
    node_x, node_y = vm[0] - 70, vm[1]

    body = ""
    # вхід через R
    sx = 60
    body += text(sx - 8, node_y + 5, "Vin", size=15, bold=True, anchor="end")
    body += line(sx, node_y, sx + 34, node_y, sw=2)
    body += res_h(sx + 34 + 29, node_y, "R")
    body += line(sx + 34 + 58, node_y, node_x, node_y, sw=2)
    body += arrow(node_x - 92, node_y, node_x - 58, node_y, color=POS, sw=2)
    body += text(node_x - 75, node_y - 9, "I_R", size=12, color=POS, italic=True)

    body += line(node_x, node_y, vm[0], vm[1], sw=2)
    body += node_dot(node_x, node_y)
    body += text(node_x - 4, node_y + 40, "вузол «−»  (0 В)", size=12, bold=True)

    # зворотний зв'язок — конденсатор C
    fb_y = node_y - 108
    body += line(node_x, node_y, node_x, fb_y, sw=2)
    # символ конденсатора горизонтально
    cap_cx = (node_x + op_cx + 100) / 2
    body += line(node_x, fb_y, cap_cx - 9, fb_y, sw=2)
    body += line(cap_cx - 9, fb_y - 14, cap_cx - 9, fb_y + 14, sw=2.5)
    body += line(cap_cx + 9, fb_y - 14, cap_cx + 9, fb_y + 14, sw=2.5)
    body += line(cap_cx + 9, fb_y, op_cx + 100, fb_y, sw=2)
    body += text(cap_cx, fb_y - 22, "C", size=14, bold=True, italic=True)
    body += line(op_cx + 100, fb_y, op_cx + 100, vo[1], sw=2)
    body += arrow(node_x + 118, fb_y, node_x + 84, fb_y, color=NEG, sw=2)
    body += text(node_x + 101, fb_y - 9, "I_C", size=12, color=NEG, italic=True)

    # «+» на землю
    body += line(vp[0], vp[1], vp[0] - 36, vp[1], sw=2)
    body += gnd(vp[0] - 36, vp[1])

    # вихід
    body += line(vo[0], vo[1], op_cx + 100, vo[1], sw=2)
    body += node_dot(op_cx + 100, vo[1])
    body += line(op_cx + 100, vo[1], op_cx + 140, vo[1], sw=2)
    body += text(op_cx + 148, vo[1] + 5, "Vout", size=15, bold=True, anchor="start")

    eqbody, ew, eh = textbox(W / 2, H - 46,
                             "той самий вузол:  I_R = I_C\n"
                             "Vin/R = −C·(dVout/dt)   →   інтегратор",
                             size=14, fill="#eef7f0", stroke=FIELD, sw=1.5)
    render(out("integrator-node.svg"), W, H, s, body, eqbody)


if __name__ == "__main__":
    fig_summing_node()
    fig_recipe()
    fig_integrator()
    print("ok: 3 figures")
