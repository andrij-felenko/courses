# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — P-V діаграма циклу Карно
# ════════════════════════════════════════════════════════════════════════════
def fig_pv_diagram():
    W, H = 780, 520
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 30, "P-V діаграма прямого циклу Карно (ідеальний газ)", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 90, 440
    f.append(line(ox, oy, 720, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(720, oy - 5), (732, oy), (720, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(730, oy + 24, "Об'єм V", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 15, 52, "Тиск P", size=12.5, bold=True, color=DARK, anchor="end"))

    p1 = (180, 110)
    p2 = (400, 170)
    p3 = (630, 390)
    p4 = (310, 330)

    path_w = "M %d %d C 250 130 330 150 %d %d C 480 250 560 330 %d %d C 510 375 400 355 %d %d C 250 240 210 170 %d %d Z" % (
        p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], p1[0], p1[1]
    )
    f.append(svg_path(path_w, stroke="none", sw=0, fill="#ebf5fb"))

    f.append(text(370, 245, "Корисна робота W", size=13, bold=True, color="#1b4f72", anchor="middle"))
    f.append(text(370, 265, "W = Q_H - |Q_C|", size=11, color="#2874a6", anchor="middle"))

    f.append(svg_path("M %d %d C 250 130 330 150 %d %d" % (p1[0], p1[1], p2[0], p2[1]), stroke="#c0392b", sw=3.0))
    f.append(svg_path("M %d %d C 480 250 560 330 %d %d" % (p2[0], p2[1], p3[0], p3[1]), stroke="#2980b9", sw=3.0))
    f.append(svg_path("M %d %d C 510 375 400 355 %d %d" % (p3[0], p3[1], p4[0], p4[1]), stroke="#8e44ad", sw=3.0))
    f.append(svg_path("M %d %d C 250 240 210 170 %d %d" % (p4[0], p4[1], p1[0], p1[1]), stroke="#27ae60", sw=3.0))

    f.append(polygon([(295, 137), (307, 143), (295, 149)], fill="#c0392b"))
    f.append(polygon([(515, 282), (525, 294), (513, 298)], fill="#2980b9"))
    f.append(polygon([(455, 368), (443, 362), (455, 356)], fill="#8e44ad"))
    f.append(polygon([(233, 218), (225, 206), (237, 204)], fill="#27ae60"))

    f.append(line(p1[0], p1[1], p1[0], oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(p2[0], p2[1], p2[0], oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(p4[0], p4[1], p4[0], oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(p3[0], p3[1], p3[0], oy, color=MUTED, sw=1.0, dash="3 3"))

    f.append(text(p1[0], oy + 16, "V_1", size=11, color=MUTED, anchor="middle"))
    f.append(text(p4[0], oy + 16, "V_4", size=11, color=MUTED, anchor="middle"))
    f.append(text(p2[0], oy + 16, "V_2", size=11, color=MUTED, anchor="middle"))
    f.append(text(p3[0], oy + 16, "V_3", size=11, color=MUTED, anchor="middle"))

    f.append(line(230, 65, 275, 120, color="#c0392b", sw=2.5))
    f.append(polygon([(275, 110), (280, 125), (266, 121)], fill="#c0392b"))
    f.append(text(210, 60, "Q_H (від нагрівача T_H)", size=11.5, bold=True, color="#c0392b", anchor="end"))

    f.append(line(460, 368, 510, 415, color="#8e44ad", sw=2.5))
    f.append(polygon([(505, 405), (515, 420), (500, 416)], fill="#8e44ad"))
    f.append(text(525, 448, "Q_C (до холодильника T_C)", size=11.5, bold=True, color="#8e44ad", anchor="start"))

    for px, py, label, align_x, align_y in [
        (p1[0], p1[1], "1 (P_1, V_1, T_H)", -15, -12),
        (p2[0], p2[1], "2 (P_2, V_2, T_H)", 15, -12),
        (p3[0], p3[1], "3 (P_3, V_3, T_C)", 15, 18),
        (p4[0], p4[1], "4 (P_4, V_4, T_C)", -15, 18)
    ]:
        f.append(circle(px, py, 5, fill=DARK, stroke="#ffffff", sw=1.5))
        anchor_val = "end" if align_x < 0 else "start"
        f.append(text(px + align_x, py + align_y, label, size=11, bold=True, color=INK, anchor=anchor_val))

    f.append(rect(490, 60, 240, 110, fill="#f8f9f9", stroke=MUTED, sw=1.0, rx=4))
    f.append(line(505, 78, 530, 78, color="#c0392b", sw=2.5))
    f.append(text(540, 82, "1-2: Ізотерма T_H", size=10.5, color=INK))
    f.append(line(505, 98, 530, 98, color="#2980b9", sw=2.5))
    f.append(text(540, 102, "2-3: Адіабата (dS=0)", size=10.5, color=INK))
    f.append(line(505, 118, 530, 118, color="#8e44ad", sw=2.5))
    f.append(text(540, 122, "3-4: Ізотерма T_C", size=10.5, color=INK))
    f.append(line(505, 138, 530, 138, color="#27ae60", sw=2.5))
    f.append(text(540, 142, "4-1: Адіабата (dS=0)", size=10.5, color=INK))

    render(os.path.join(OUT, "carnot-pv-diagram.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — T-S діаграма циклу Карно
# ════════════════════════════════════════════════════════════════════════════
def fig_ts_diagram():
    W, H = 760, 480
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 30, "T-S діаграма циклу Карно (геометрія ентропії)", size=15, bold=True, color=INK, anchor="middle"))

    ox, oy = 100, 410
    f.append(line(ox, oy, 700, oy, color=DARK, sw=2.0))
    f.append(line(ox, oy, ox, 60, color=DARK, sw=2.0))

    f.append(polygon([(700, oy - 5), (712, oy), (700, oy + 5)], fill=DARK))
    f.append(polygon([(ox - 5, 60), (ox, 48), (ox + 5, 60)], fill=DARK))

    f.append(text(710, oy + 24, "Ентропія S", size=12.5, bold=True, color=DARK, anchor="end"))
    f.append(text(ox - 15, 52, "Температура T", size=12.5, bold=True, color=DARK, anchor="end"))

    s1, s2 = 220, 540
    th_y, tc_y = 120, 290

    f.append(rect(s1, th_y, s2 - s1, tc_y - th_y, fill="#ebf5fb", stroke="none"))
    f.append(text((s1 + s2) // 2, (th_y + tc_y) // 2 - 5, "Корисна робота W", size=13, bold=True, color="#1b4f72", anchor="middle"))
    f.append(text((s1 + s2) // 2, (th_y + tc_y) // 2 + 15, "W = (T_H - T_C) · ΔS", size=11, color="#2874a6", anchor="middle"))

    f.append(rect(s1, tc_y, s2 - s1, oy - tc_y, fill="#f4ecf7", stroke="none"))
    f.append(text((s1 + s2) // 2, (tc_y + oy) // 2, "Q_C = T_C · ΔS", size=12, bold=True, color="#6c3483", anchor="middle"))

    f.append(line(s1, th_y, s2, th_y, color="#c0392b", sw=3.0))
    f.append(line(s2, th_y, s2, tc_y, color="#2980b9", sw=3.0))
    f.append(line(s2, tc_y, s1, tc_y, color="#8e44ad", sw=3.0))
    f.append(line(s1, tc_y, s1, th_y, color="#27ae60", sw=3.0))

    f.append(polygon([(380, th_y - 5), (392, th_y), (380, th_y + 5)], fill="#c0392b"))
    f.append(polygon([(s2 - 5, 200), (s2, 212), (s2 + 5, 200)], fill="#2980b9"))
    f.append(polygon([(390, tc_y + 5), (378, tc_y), (390, tc_y - 5)], fill="#8e44ad"))
    f.append(polygon([(s1 + 5, 210), (s1, 198), (s1 - 5, 210)], fill="#27ae60"))

    f.append(line(ox, th_y, s1, th_y, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(ox, tc_y, s1, tc_y, color=MUTED, sw=1.0, dash="3 3"))

    f.append(line(s1, tc_y, s1, oy, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(s2, tc_y, s2, oy, color=MUTED, sw=1.0, dash="3 3"))

    f.append(text(ox - 12, th_y + 4, "T_H", size=12, bold=True, color="#c0392b", anchor="end"))
    f.append(text(ox - 12, tc_y + 4, "T_C", size=12, bold=True, color="#8e44ad", anchor="end"))

    f.append(text(s1, oy + 18, "S_1 = S_4", size=11.5, bold=True, color=DARK, anchor="middle"))
    f.append(text(s2, oy + 18, "S_2 = S_3", size=11.5, bold=True, color=DARK, anchor="middle"))

    f.append(line(s1, oy + 32, s2, oy + 32, color=DARK, sw=1.5))
    f.append(line(s1, oy + 26, s1, oy + 38, color=DARK, sw=1.5))
    f.append(line(s2, oy + 26, s2, oy + 38, color=DARK, sw=1.5))
    f.append(text((s1 + s2) // 2, oy + 46, "ΔS = S_2 - S_1", size=11, bold=True, color=DARK, anchor="middle"))

    for px, py, label, ax, ay in [
        (s1, th_y, "1", -12, -10),
        (s2, th_y, "2", 12, -10),
        (s2, tc_y, "3", 12, 16),
        (s1, tc_y, "4", -12, 16)
    ]:
        f.append(circle(px, py, 5, fill=DARK, stroke="#ffffff", sw=1.5))
        anchor_val = "end" if ax < 0 else "start"
        f.append(text(px + ax, py + ay, label, size=12, bold=True, color=INK, anchor=anchor_val))

    render(os.path.join(OUT, "carnot-ts-diagram.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Прямий та зворотний цикл Карно (енергетична схема)
# ════════════════════════════════════════════════════════════════════════════
def fig_reverse_scheme():
    W, H = 820, 450
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    f.append(text(W // 2, 28, "Порівняння прямого та зворотного циклу Карно", size=15, bold=True, color=INK, anchor="middle"))

    f.append(line(410, 50, 410, 420, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Прямий цикл ──
    cx1 = 205
    f.append(text(cx1, 58, "Прямий цикл (Тепловий двигун)", size=13.5, bold=True, color=INK, anchor="middle"))

    f.append(rect(cx1 - 110, 85, 220, 45, fill="#fadbd8", stroke="#c0392b", sw=1.5, rx=6))
    f.append(text(cx1, 112, "Нагрівач T_H", size=12.5, bold=True, color="#78281f", anchor="middle"))

    f.append(circle(cx1, 230, 42, fill="#ebf5fb", stroke="#2980b9", sw=2.0))
    f.append(text(cx1, 224, "Робоче", size=11, bold=True, color="#1b4f72", anchor="middle"))
    f.append(text(cx1, 240, "тіло", size=11, bold=True, color="#1b4f72", anchor="middle"))

    f.append(rect(cx1 - 110, 335, 220, 45, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=6))
    f.append(text(cx1, 362, "Холодильник T_C", size=12.5, bold=True, color="#145a32", anchor="middle"))
    f.append(line(cx1, 130, cx1, 188, color="#c0392b", sw=3.0))
    f.append(polygon([(cx1 - 6, 188), (cx1, 198), (cx1 + 6, 188)], fill="#c0392b"))
    f.append(text(cx1 + 12, 162, "Q_H", size=12, bold=True, color="#c0392b", anchor="start"))

    f.append(line(cx1 + 42, 230, cx1 + 125, 230, color="#d35400", sw=3.0))
    f.append(polygon([(cx1 + 125, 224), (cx1 + 137, 230), (cx1 + 125, 236)], fill="#d35400"))
    f.append(text(cx1 + 80, 218, "Робота W", size=11.5, bold=True, color="#d35400", anchor="middle"))
    f.append(text(cx1 + 80, 246, "(виходить)", size=10.5, color=MUTED, anchor="middle"))

    f.append(line(cx1, 272, cx1, 335, color="#8e44ad", sw=3.0))
    f.append(polygon([(cx1 - 6, 325), (cx1, 335), (cx1 + 6, 325)], fill="#8e44ad"))
    f.append(text(cx1 + 12, 306, "Q_C", size=12, bold=True, color="#8e44ad", anchor="start"))

    f.append(text(cx1, 410, "ККД η = W / Q_H = 1 - T_C / T_H", size=11.5, bold=True, color=INK, anchor="middle"))

    # ── Права панель: Зворотний цикл ──
    cx2 = 615
    f.append(text(cx2, 58, "Зворотний цикл (Тепловий насос)", size=13.5, bold=True, color=INK, anchor="middle"))

    f.append(rect(cx2 - 110, 85, 220, 45, fill="#fadbd8", stroke="#c0392b", sw=1.5, rx=6))
    f.append(text(cx2, 112, "Приміщення / Нагрівач T_H", size=12, bold=True, color="#78281f", anchor="middle"))

    f.append(circle(cx2, 230, 42, fill="#f4ecf7", stroke="#8e44ad", sw=2.0))
    f.append(text(cx2, 224, "Робоче", size=11, bold=True, color="#512e5f", anchor="middle"))
    f.append(text(cx2, 240, "тіло", size=11, bold=True, color="#512e5f", anchor="middle"))

    f.append(rect(cx2 - 110, 335, 220, 45, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=6))
    f.append(text(cx2, 362, "Довкілля / Камера T_C", size=12, bold=True, color="#145a32", anchor="middle"))

    f.append(line(cx2, 188, cx2, 130, color="#c0392b", sw=3.0))
    f.append(polygon([(cx2 - 6, 140), (cx2, 130), (cx2 + 6, 140)], fill="#c0392b"))
    f.append(text(cx2 + 12, 162, "Q_H", size=12, bold=True, color="#c0392b", anchor="start"))

    f.append(line(cx2 - 125, 230, cx2 - 42, 230, color="#d35400", sw=3.0))
    f.append(polygon([(cx2 - 54, 224), (cx2 - 42, 230), (cx2 - 54, 236)], fill="#d35400"))
    f.append(text(cx2 - 80, 218, "Робота W", size=11.5, bold=True, color="#d35400", anchor="middle"))
    f.append(text(cx2 - 80, 246, "(затрачується)", size=10.5, color=MUTED, anchor="middle"))

    f.append(line(cx2, 335, cx2, 272, color="#8e44ad", sw=3.0))
    f.append(polygon([(cx2 - 6, 282), (cx2, 272), (cx2 + 6, 282)], fill="#8e44ad"))
    f.append(text(cx2 + 12, 306, "Q_C", size=12, bold=True, color="#8e44ad", anchor="start"))

    f.append(text(cx2, 404, "COP_ref = Q_C / W = T_C / (T_H - T_C)", size=10.5, bold=True, color=INK, anchor="middle"))
    f.append(text(cx2, 422, "COP_heat = Q_H / W = T_H / (T_H - T_C)", size=10.5, bold=True, color=INK, anchor="middle"))

    render(os.path.join(OUT, "reverse-carnot-scheme.svg"), W, H, *f)


if __name__ == '__main__':
    fig_pv_diagram()
    fig_ts_diagram()
    fig_reverse_scheme()
    print("Figures generated successfully.")
