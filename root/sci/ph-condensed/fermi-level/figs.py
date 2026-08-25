# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path(d_str, stroke=INK, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Функція розподілу Фермі — Дірака при різних температурах
# ════════════════════════════════════════════════════════════════════════════
def fig_fermi_distribution():
    W, H = 760, 420
    f = []

    # Фон та заголовок
    f.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1.0))
    f.append(text(W / 2, 32, "Функція розподілу Фермі — Дірака f(E) при різних температурах", size=15, bold=True, color=INK))

    # Вісі координат
    ox, oy = 100, 350
    xw, yh = 580, 270

    # Сітка та вісі
    f.append(line(ox, oy, ox + xw, oy, color=INK, sw=2.0))
    f.append(line(ox, oy, ox, oy - yh, color=INK, sw=2.0))

    # Стрілки осей
    f.append(polygon([(ox + xw, oy - 4), (ox + xw + 10, oy), (ox + xw, oy + 4)], fill=INK))
    f.append(polygon([(ox - 4, oy - yh), (ox, oy - yh - 10), (ox + 4, oy - yh)], fill=INK))

    # Підписи осей
    f.append(text(ox + xw + 15, oy + 5, "Енергія E", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(ox - 15, oy - yh - 15, "Ймовірність f(E)", size=13, bold=True, color=INK, anchor="middle"))

    # Позначки на осі y (0, 0.5, 1.0)
    f.append(line(ox - 6, oy, ox, oy, color=INK, sw=1.5))
    f.append(text(ox - 12, oy + 4, "0", size=12, color=INK, anchor="end"))

    y_half = oy - yh * 0.5
    f.append(line(ox - 6, y_half, ox + xw, y_half, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(ox - 12, y_half + 4, "0.5", size=12, color=INK, anchor="end"))

    y_one = oy - yh * 0.9
    f.append(line(ox - 6, y_one, ox, y_one, color=INK, sw=1.5))
    f.append(text(ox - 12, y_one + 4, "1.0", size=12, color=INK, anchor="end"))

    # Позначка рівня Фермі EF на осі x
    x_ef = ox + xw * 0.5
    f.append(line(x_ef, oy, x_ef, oy - yh, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(x_ef, oy, x_ef, oy + 6, color=INK, sw=1.5))
    f.append(text(x_ef, oy + 22, "E_F", size=14, bold=True, color=POS, anchor="middle"))

    # Точка 1/2 на рівні EF
    f.append(circle(x_ef, y_half, r=4, fill=POS, stroke=INK, sw=1.0))

    # 1. T = 0 K (ступенева функція)
    pts_t0 = []
    pts_t0.append("M %d %d" % (ox, y_one))
    pts_t0.append("L %d %d" % (x_ef, y_one))
    pts_t0.append("L %d %d" % (x_ef, oy))
    pts_t0.append("L %d %d" % (ox + xw - 20, oy))
    f.append(path(" ".join(pts_t0), stroke="#16a085", sw=3.0, dash=None))

    # 2. T = 100 K (помірний розмив)
    pts_t1 = []
    for px in range(0, int(xw) - 20, 4):
        x = ox + px
        e_rel = (px - xw * 0.5) / 25.0
        val = 1.0 / (math.exp(e_rel) + 1.0) if abs(e_rel) < 20 else (1.0 if e_rel < 0 else 0.0)
        py = oy - yh * 0.9 * val
        pts_t1.append("%s %.1f %.1f" % ("M" if px == 0 else "L", x, py))
    f.append(path(" ".join(pts_t1), stroke=NEG, sw=2.5))

    # 3. T = 500 K (широкий розмив)
    pts_t2 = []
    for px in range(0, int(xw) - 20, 4):
        x = ox + px
        e_rel = (px - xw * 0.5) / 75.0
        val = 1.0 / (math.exp(e_rel) + 1.0) if abs(e_rel) < 20 else (1.0 if e_rel < 0 else 0.0)
        py = oy - yh * 0.9 * val
        pts_t2.append("%s %.1f %.1f" % ("M" if px == 0 else "L", x, py))
    f.append(path(" ".join(pts_t2), stroke=POS, sw=2.5))

    # Легенда
    lx, ly = ox + xw - 210, oy - yh + 30
    f.append(rect(lx, ly, 195, 95, fill=FILL, stroke=MUTED, sw=1.0))
    f.append(line(lx + 15, ly + 25, lx + 45, ly + 25, color="#16a085", sw=3.0))
    f.append(text(lx + 55, ly + 29, "T = 0 K", size=12, bold=True, color=INK, anchor="start"))

    f.append(line(lx + 15, ly + 50, lx + 45, ly + 50, color=NEG, sw=2.5))
    f.append(text(lx + 55, ly + 54, "T = 100 K", size=12, bold=True, color=INK, anchor="start"))

    f.append(line(lx + 15, ly + 75, lx + 45, ly + 75, color=POS, sw=2.5))
    f.append(text(lx + 55, ly + 79, "T = 500 K", size=12, bold=True, color=INK, anchor="start"))

    # Пояснення теплового розмиву ~ kBT
    f.append(line(x_ef - 40, oy - 25, x_ef + 40, oy - 25, color=FIELD, sw=1.5))
    f.append(polygon([(x_ef - 40, oy - 28), (x_ef - 48, oy - 25), (x_ef - 40, oy - 22)], fill=FIELD))
    f.append(polygon([(x_ef + 40, oy - 28), (x_ef + 48, oy - 25), (x_ef + 40, oy - 22)], fill=FIELD))
    f.append(text(x_ef, oy - 35, "~ k_B · T", size=11, bold=True, color=FIELD, anchor="middle"))

    render(os.path.join(OUT, "fermi-distribution.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Положення рівня Фермі в різних класах речовин
# ════════════════════════════════════════════════════════════════════════════
def fig_band_diagrams_materials():
    W, H = 820, 390
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1.0))
    f.append(text(W / 2, 30, "Положення рівня Фермі в зонах різних матеріалів при T > 0 K", size=15, bold=True, color=INK))

    col_w = 175
    gap = 20
    start_x = 30
    y_top = 70
    h_band = 260

    panels = [
        {"title": "Метал", "type": "metal"},
        {"title": "Власний (i-Si)", "type": "intrinsic"},
        {"title": "n-напівпровідник", "type": "n-type"},
        {"title": "p-напівпровідник", "type": "p-type"}
    ]

    for idx, p in enumerate(panels):
        px = start_x + idx * (col_w + gap)
        # Панель
        f.append(rect(px, y_top, col_w, h_band, fill=FILL, stroke=MUTED, sw=1.0))
        f.append(text(px + col_w / 2, y_top + 25, p["title"], size=13, bold=True, color=INK))

        if p["type"] == "metal":
            y_ec = y_top + 60
            y_ev = y_top + 230
            y_ef = y_top + 140

            f.append(rect(px + 25, y_ef, col_w - 50, y_ev - y_ef, fill="#d6eaf8", stroke="none"))
            f.append(rect(px + 25, y_ec, col_w - 50, y_ev - y_ec, fill="none", stroke=LINE, sw=1.8))

            f.append(line(px + 15, y_ef, px + col_w - 15, y_ef, color=POS, sw=2.5))
            f.append(text(px + col_w / 2, y_ef - 8, "E_F (перетинає зону)", size=11, bold=True, color=POS))
            f.append(text(px + col_w / 2, y_ev - 25, "Заповнені стани", size=11, color=NEG))
            f.append(text(px + col_w / 2, y_ec + 30, "Вільні стани", size=11, color=MUTED))

        elif p["type"] == "intrinsic":
            y_ec = y_top + 65
            y_ev = y_top + 215
            y_ef = (y_ec + y_ev) / 2

            f.append(rect(px + 25, y_top + 45, col_w - 50, 35, fill="#fadbd8", stroke=POS, sw=1.5))
            f.append(text(px + col_w / 2, y_top + 67, "E_c (зона провідності)", size=10, bold=True, color=POS))

            f.append(rect(px + 25, y_ev, col_w - 50, 35, fill="#d6eaf8", stroke=NEG, sw=1.5))
            f.append(text(px + col_w / 2, y_ev + 22, "E_v (валентна зона)", size=10, bold=True, color=NEG))

            f.append(line(px + 15, y_ef, px + col_w - 15, y_ef, color=FIELD, sw=2.0, dash="5 3"))
            f.append(text(px + col_w / 2, y_ef - 7, "E_F ≈ E_i (середина E_g)", size=10, bold=True, color=FIELD))

        elif p["type"] == "n-type":
            y_ec = y_top + 65
            y_ev = y_top + 215
            y_ed = y_ec + 35
            y_ef = y_ec + 20

            f.append(rect(px + 25, y_top + 45, col_w - 50, 35, fill="#fadbd8", stroke=POS, sw=1.5))
            f.append(text(px + col_w / 2, y_top + 67, "E_c", size=10, bold=True, color=POS))

            f.append(rect(px + 25, y_ev, col_w - 50, 35, fill="#d6eaf8", stroke=NEG, sw=1.5))
            f.append(text(px + col_w / 2, y_ev + 22, "E_v", size=10, bold=True, color=NEG))

            f.append(line(px + 30, y_ed, px + col_w - 30, y_ed, color=POS, sw=1.5, dash="3 2"))
            f.append(text(px + col_w - 25, y_ed + 4, "E_d", size=10, bold=True, color=POS, anchor="start"))

            f.append(line(px + 15, y_ef, px + col_w - 15, y_ef, color=FIELD, sw=2.0, dash="5 3"))
            f.append(text(px + col_w / 2, y_ef - 6, "E_F (поблизу E_c)", size=10, bold=True, color=FIELD))

        elif p["type"] == "p-type":
            y_ec = y_top + 65
            y_ev = y_top + 215
            y_ea = y_ev - 35
            y_ef = y_ev - 20

            f.append(rect(px + 25, y_top + 45, col_w - 50, 35, fill="#fadbd8", stroke=POS, sw=1.5))
            f.append(text(px + col_w / 2, y_top + 67, "E_c", size=10, bold=True, color=POS))

            f.append(rect(px + 25, y_ev, col_w - 50, 35, fill="#d6eaf8", stroke=NEG, sw=1.5))
            f.append(text(px + col_w / 2, y_ev + 22, "E_v", size=10, bold=True, color=NEG))

            f.append(line(px + 30, y_ea, px + col_w - 30, y_ea, color=NEG, sw=1.5, dash="3 2"))
            f.append(text(px + col_w - 25, y_ea + 4, "E_a", size=10, bold=True, color=NEG, anchor="start"))

            f.append(line(px + 15, y_ef, px + col_w - 15, y_ef, color=FIELD, sw=2.0, dash="5 3"))
            f.append(text(px + col_w / 2, y_ef + 15, "E_F (поблизу E_v)", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "band-diagrams-materials.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Вирівнювання рівнів Фермі при контакті двох матеріалів
# ════════════════════════════════════════════════════════════════════════════
def fig_contact_potential():
    W, H = 820, 410
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1.0))
    f.append(text(W / 2, 30, "Формування контактної різниці потенціалів та вирівнювання EF", size=15, bold=True, color=INK))

    f.append(line(W / 2, 50, W / 2, H - 20, color=MUTED, sw=1.2, dash="4 4"))

    # --- Зліва: До контакту ---
    f.append(text(W / 4, 55, "1. До контакту (ізольовані)", size=13, bold=True, color=INK))

    f.append(line(30, 85, 370, 85, color=MUTED, sw=1.5, dash="3 3"))
    f.append(text(375, 89, "E_vac", size=11, color=MUTED, anchor="start"))

    f.append(rect(40, 230, 130, 130, fill="#eaecee", stroke="#7f8c8d", sw=1.5))
    f.append(line(40, 230, 170, 230, color=POS, sw=2.5))
    f.append(text(105, 260, "Метал 1", size=12, bold=True, color=INK))
    f.append(text(105, 280, "E_F1", size=12, bold=True, color=POS))

    f.append(line(105, 85, 105, 230, color=POS, sw=1.5))
    f.append(polygon([(102, 95), (105, 85), (108, 95)], fill=POS))
    f.append(polygon([(102, 220), (105, 230), (108, 220)], fill=POS))
    f.append(text(115, 160, "qΦ_1", size=11, bold=True, color=POS, anchor="start"))

    f.append(rect(230, 160, 130, 200, fill="#d5f5e3", stroke="#27ae60", sw=1.5))
    f.append(line(230, 160, 360, 160, color=NEG, sw=2.5))
    f.append(text(295, 190, "Метал 2", size=12, bold=True, color=INK))
    f.append(text(295, 210, "E_F2", size=12, bold=True, color=NEG))

    f.append(line(295, 85, 295, 160, color=NEG, sw=1.5))
    f.append(polygon([(292, 95), (295, 85), (298, 95)], fill=NEG))
    f.append(polygon([(292, 150), (295, 160), (298, 150)], fill=NEG))
    f.append(text(305, 125, "qΦ_2", size=11, bold=True, color=NEG, anchor="start"))

    # --- Справа: Після контакту (Рівновага) ---
    f.append(text(3 * W / 4, 55, "2. Рівноважний контакт (E_F1 = E_F2)", size=13, bold=True, color=INK))

    f.append(line(430, 210, 780, 210, color=FIELD, sw=2.0, dash="6 3"))
    f.append(text(785, 214, "E_F", size=12, bold=True, color=FIELD, anchor="start"))

    f.append(rect(440, 210, 140, 150, fill="#eaecee", stroke="#7f8c8d", sw=1.5))
    f.append(text(510, 260, "Метал 1 (-q)", size=12, bold=True, color=INK))

    f.append(rect(580, 210, 140, 150, fill="#d5f5e3", stroke="#27ae60", sw=1.5))
    f.append(text(650, 260, "Метал 2 (+q)", size=12, bold=True, color=INK))

    f.append(path("M 440 100 L 530 100 C 560 100 600 170 630 170 L 720 170", stroke=MUTED, sw=1.8, dash="3 3"))
    f.append(text(725, 174, "E_vac", size=11, color=MUTED, anchor="start"))

    f.append(line(750, 100, 750, 170, color=POS, sw=1.5))
    f.append(polygon([(747, 110), (750, 100), (753, 110)], fill=POS))
    f.append(polygon([(747, 160), (750, 170), (753, 160)], fill=POS))
    f.append(line(530, 100, 755, 100, color=MUTED, sw=1.0, dash="2 2"))
    f.append(line(630, 170, 755, 170, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text(760, 138, "qV_CD = q(Φ_1 - Φ_2)", size=10, bold=True, color=POS, anchor="start"))

    f.append(line(590, 195, 530, 195, color=NEG, sw=2.0))
    f.append(polygon([(535, 191), (525, 195), (535, 199)], fill=NEG))
    f.append(text(560, 185, "Перехід e⁻", size=11, bold=True, color=NEG, anchor="middle"))

    render(os.path.join(OUT, "contact-potential.svg"), W, H, *f)

if __name__ == "__main__":
    fig_fermi_distribution()
    fig_band_diagrams_materials()
    fig_contact_potential()
    print("Figures generated successfully.")
