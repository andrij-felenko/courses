# -*- coding: utf-8 -*-
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зонна діаграма гетероструктури GaAs/AlGaAs з 2DEG
# ════════════════════════════════════════════════════════════════════════════
def fig_heterostructure_band():
    W, H = 820, 440
    f = []

    # Тло та роздільні ділянки матеріалів
    f.append(rect(60, 40, 260, 340, fill="#ebf5fb", stroke="none"))
    f.append(rect(320, 40, 80, 340, fill="#e8f8f5", stroke="none"))
    f.append(rect(400, 40, 370, 340, fill="#ffeaea", stroke="none"))

    # Вертикальні межі розділу
    f.append(line(320, 40, 320, 380, color="#a9cce3", sw=1.2, dash="3 3"))
    f.append(line(400, 40, 400, 380, color="#a3e4d7", sw=1.5))

    # Підписи матеріальних шарів
    f.append(text(190, 65, "n-Al₀.₃Ga₀.₇As", size=13, bold=True, color="#1b4f72"))
    f.append(text(190, 83, "(допований Si, N_D = 10¹⁸ см⁻³)", size=10.5, color="#2874a6"))

    f.append(text(360, 65, "Spacer", size=12, bold=True, color="#117864"))
    f.append(text(360, 83, "AlGaAs (d=10 нм)", size=10.5, color="#16a085"))

    f.append(text(585, 65, "i-GaAs (чистий буфер)", size=13, bold=True, color="#922b21"))
    f.append(text(585, 83, "незадопований напівпровідник", size=10.5, color="#c0392b"))

    # Рівень Фермі E_F (горизонтальна штрихова лінія)
    ef_y = 230
    f.append(line(60, ef_y, 770, ef_y, color="#7d3c98", sw=1.8, dash="6 4"))
    f.append(text(720, ef_y - 8, "E_F (рівень Фермі)", size=11.5, bold=True, color="#7d3c98"))

    # Дно зони провідності E_c(z)
    pts_ec = []
    for x in range(60, 320, 4):
        y = 130 + 60 * ((x - 60) / 260.0)**1.5
        pts_ec.append((x, y))
    for x in range(320, 401, 2):
        y = 190 + 20 * ((x - 320) / 80.0)
        pts_ec.append((x, y))
    path_ec1 = "M " + " L ".join("%.1f %.1f" % p for p in pts_ec)
    f.append(svg_path(path_ec1, stroke="#2980b9", sw=2.5, fill="none"))

    f.append(line(400, 210, 400, 295, color="#2980b9", sw=2.5))

    pts_ec2 = []
    for x in range(400, 770, 2):
        dz = x - 400
        if dz < 40:
            y = 295 - 80 * (dz / 40.0)**0.7
        else:
            y = 215 - 5 * math.exp(-(dz - 40) / 80.0)
        pts_ec2.append((x, y))
    path_ec2 = "M " + " L ".join("%.1f %.1f" % p for p in pts_ec2)
    f.append(svg_path(path_ec2, stroke="#2980b9", sw=2.5, fill="none"))

    f.append(text(120, 120, "E_c (AlGaAs)", size=12, bold=True, color="#2980b9"))
    f.append(text(460, 195, "E_c (GaAs)", size=12, bold=True, color="#2980b9"))

    # Заповнена квантова яма (2DEG)
    pts_well_fill = [(400, 295)]
    for x in range(400, 440, 2):
        dz = x - 400
        y = 295 - 80 * (dz / 40.0)**0.7
        pts_well_fill.append((x, y))
    pts_well_fill.append((440, ef_y))
    pts_well_fill.append((400, ef_y))
    f.append(polygon(pts_well_fill, fill="#f5b041"))

    # Квантований рівень E₀ у ямі
    e0_y = 250
    f.append(line(400, e0_y, 423, e0_y, color="#c0392b", sw=2.0))
    f.append(text(430, e0_y + 4, "E₀ (основна підзона)", size=11, bold=True, color="#c0392b"))

    # Хвильова функція |ψ₀(z)|²
    pts_psi = []
    for dz in range(0, 50, 1):
        x = 400 + dz
        norm_z = dz / 12.0
        psi_sq = (norm_z**2) * math.exp(-norm_z) * 1.8
        y = e0_y - psi_sq * 25.0
        pts_psi.append((x, y))
    path_psi = "M " + " L ".join("%.1f %.1f" % p for p in pts_psi)
    f.append(svg_path(path_psi, stroke="#d35400", sw=2.2, fill="none"))
    f.append(text(445, e0_y - 28, "|ψ₀(z)|² (густість електронів)", size=10.5, bold=True, color="#d35400"))

    f.append(text(408, 275, "2DEG", size=13, bold=True, color="#900c3f"))

    # Позначка розриву зон ΔE_c
    f.append(line(385, 210, 385, 295, color="#e74c3c", sw=1.2))
    f.append(line(380, 210, 390, 210, color="#e74c3c", sw=1.2))
    f.append(line(380, 295, 390, 295, color="#e74c3c", sw=1.2))
    f.append(text(300, 255, "ΔE_c ≈ 0.3 еВ", size=11, bold=True, color="#e74c3c"))

    # Позначка позитивних іонізованих донорів (Si+) у n-AlGaAs
    for dx in [100, 150, 200, 250]:
        f.append(circle(dx, 160, 8, fill="#fadbd8", stroke="#e74c3c", sw=1.2))
        f.append(text(dx - 4, 164, "+", size=12, bold=True, color="#e74c3c"))
    f.append(text(120, 190, "Іонізовані донори Si⁺", size=10.5, color="#c0392b"))

    # Стрілка просторового розділення
    f.append(line(260, 205, 410, 265, color="#27ae60", sw=1.8))
    f.append(polygon([(410, 265), (400, 258), (402, 268)], fill="#27ae60"))
    f.append(text(210, 235, "Просторове розділення", size=10.5, bold=True, color="#27ae60"))
    f.append(text(210, 248, "запобігає розсіюванню!", size=10, color="#1e8449"))

    # Осі z та енергії E
    f.append(line(60, 380, 770, 380, color=DARK, sw=1.5))
    f.append(polygon([(770, 376), (780, 380), (770, 384)], fill=DARK))
    f.append(text(740, 400, "Координата z (поперек гетероінтерфейсу)", size=11, bold=True, color=DARK))

    f.append(line(60, 380, 60, 40, color=DARK, sw=1.5))
    f.append(polygon([(56, 40), (60, 30), (64, 40)], fill=DARK))
    f.append(text(15, 35, "Енергія E", size=11.5, bold=True, color=DARK))

    render(os.path.join(OUT, "2deg-heterostructure-band.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Густість станів g(E): 3D bulk проти 2DEG
# ════════════════════════════════════════════════════════════════════════════
def fig_density_of_states():
    W, H = 800, 420
    f = []

    f.append(line(390, 25, 390, 390, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: 3D Bulk ──
    f.append(text(195, 45, "Тривимірний об'ємний напівпровідник (3D)", size=13.5, bold=True, color=INK))
    f.append(text(195, 65, "Параболічна густість станів g₃D(E) ∝ √(E)", size=11.5, color=MUTED))

    ox1, oy1 = 60, 340
    f.append(line(ox1, oy1, 360, oy1, color=DARK, sw=1.5))
    f.append(line(ox1, oy1, ox1, 90, color=DARK, sw=1.5))
    f.append(polygon([(360, oy1-4), (370, oy1), (360, oy1+4)], fill=DARK))
    f.append(polygon([(ox1-4, 90), (ox1, 80), (ox1+4, 90)], fill=DARK))

    f.append(text(340, oy1 + 25, "Енергія E", size=11.5, bold=True, color=DARK))
    f.append(text(15, 82, "g₃D(E)", size=11.5, bold=True, color=DARK))

    pts_3d = []
    for x in range(ox1, 350, 2):
        de = (x - ox1) / 290.0
        val = math.sqrt(de)
        y = oy1 - int(val * 210)
        pts_3d.append((x, y))
    path_3d = "M " + " L ".join("%d %d" % p for p in pts_3d)
    f.append(svg_path(path_3d, stroke="#2980b9", sw=2.5, fill="none"))

    ef_x1 = ox1 + 180
    pts_fill1 = [(ox1, oy1)]
    for p in pts_3d:
        if p[0] <= ef_x1:
            pts_fill1.append(p)
    pts_fill1.append((ef_x1, oy1))
    f.append(polygon(pts_fill1, fill="#3498db"))

    f.append(line(ef_x1, oy1, ef_x1, 120, color="#7d3c98", sw=1.5, dash="4 3"))
    f.append(text(ef_x1 - 15, oy1 + 20, "E_F", size=11.5, bold=True, color="#7d3c98"))
    f.append(text(120, 240, "Заповнені стани", size=10.5, color="#2980b9"))

    # ── Права панель: 2DEG ──
    f.append(text(595, 45, "Двовимірний електронний газ (2DEG)", size=13.5, bold=True, color=INK))
    f.append(text(595, 65, "Східчаста густість станів g₂D(E) = m* / (π ħ²)", size=11.5, color=MUTED))

    ox2, oy2 = 440, 340
    f.append(line(ox2, oy2, 750, oy2, color=DARK, sw=1.5))
    f.append(line(ox2, oy2, ox2, 90, color=DARK, sw=1.5))
    f.append(polygon([(750, oy2-4), (760, oy2), (750, oy2+4)], fill=DARK))
    f.append(polygon([(ox2-4, 90), (ox2, 80), (ox2+4, 90)], fill=DARK))

    f.append(text(730, oy2 + 25, "Енергія E", size=11.5, bold=True, color=DARK))
    f.append(text(395, 82, "g₂D(E)", size=11.5, bold=True, color=DARK))

    e0_x = ox2 + 60
    e1_x = ox2 + 170
    e2_x = ox2 + 270
    d0_h = 70

    ef_x2 = ox2 + 130
    f.append(rect(e0_x, oy2 - d0_h, ef_x2 - e0_x, d0_h, fill="#e74c3c", stroke="none"))

    f.append(line(ox2, oy2, e0_x, oy2, color="#c0392b", sw=2.5))
    f.append(line(e0_x, oy2, e0_x, oy2 - d0_h, color="#c0392b", sw=2.5))
    f.append(line(e0_x, oy2 - d0_h, e1_x, oy2 - d0_h, color="#c0392b", sw=2.5))
    f.append(line(e1_x, oy2 - d0_h, e1_x, oy2 - 2*d0_h, color="#c0392b", sw=2.5))
    f.append(line(e1_x, oy2 - 2*d0_h, e2_x, oy2 - 2*d0_h, color="#c0392b", sw=2.5))
    f.append(line(e2_x, oy2 - 2*d0_h, e2_x, oy2 - 3*d0_h, color="#c0392b", sw=2.5))
    f.append(line(e2_x, oy2 - 3*d0_h, 740, oy2 - 3*d0_h, color="#c0392b", sw=2.5))

    f.append(line(e0_x, oy2, e0_x, 110, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(e1_x, oy2, e1_x, 110, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(e2_x, oy2, e2_x, 110, color=MUTED, sw=1.2, dash="3 3"))

    f.append(text(e0_x - 10, oy2 + 20, "E₀", size=11.5, bold=True, color="#c0392b"))
    f.append(text(e1_x - 10, oy2 + 20, "E₁", size=11.5, bold=True, color="#c0392b"))
    f.append(text(e2_x - 10, oy2 + 20, "E₂", size=11.5, bold=True, color="#c0392b"))

    f.append(line(ox2 - 15, oy2 - d0_h, ox2 + 5, oy2 - d0_h, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(text(445, oy2 - d0_h - 8, "g₀ = m* / (π·ħ²)", size=11, bold=True, color="#c0392b"))

    f.append(line(ef_x2, oy2, ef_x2, 110, color="#7d3c98", sw=1.8, dash="4 3"))
    f.append(text(ef_x2 - 12, oy2 + 20, "E_F", size=11.5, bold=True, color="#7d3c98"))
    f.append(text(465, oy2 - 25, "Лише 1 підзона", size=10.5, bold=True, color="#d35400"))
    f.append(text(465, oy2 - 10, "заповнена!", size=10.5, bold=True, color="#d35400"))

    render(os.path.join(OUT, "2deg-density-of-states.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Ландау-рівні 2DEG
# ════════════════════════════════════════════════════════════════════════════
def fig_landau_levels():
    W, H = 820, 440
    f = []

    f.append(line(410, 25, 410, 400, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: B = 0 ──
    f.append(text(205, 45, "Без магнітного поля (B = 0)", size=13.5, bold=True, color=INK))
    f.append(text(205, 65, "Неперервний 2D спектр підзони E₀", size=11.5, color=MUTED))

    ox1, oy1 = 60, 350
    f.append(line(ox1, oy1, 370, oy1, color=DARK, sw=1.5))
    f.append(line(ox1, oy1, ox1, 90, color=DARK, sw=1.5))
    f.append(polygon([(370, oy1-4), (380, oy1), (370, oy1+4)], fill=DARK))
    f.append(polygon([(ox1-4, 90), (ox1, 80), (ox1+4, 90)], fill=DARK))

    f.append(text(350, oy1 + 25, "Енергія E", size=11.5, bold=True, color=DARK))
    f.append(text(15, 82, "g₂D(E)", size=11.5, bold=True, color=DARK))

    g0_y = oy1 - 160
    f.append(line(ox1 + 40, g0_y, 360, g0_y, color="#2980b9", sw=2.5))
    f.append(line(ox1 + 40, oy1, ox1 + 40, g0_y, color="#2980b9", sw=2.5))

    ef1_x = ox1 + 180
    f.append(rect(ox1 + 40, g0_y, ef1_x - (ox1 + 40), 160, fill="#3498db", stroke="none"))
    f.append(line(ef1_x, oy1, ef1_x, 100, color="#7d3c98", sw=1.5, dash="4 3"))
    f.append(text(ef1_x - 12, oy1 + 20, "E_F", size=11.5, bold=True, color="#7d3c98"))
    f.append(text(110, oy1 - 80, "Неперервний континуум", size=11, color="#1f618d"))

    # ── Права панель: B > 0 ──
    f.append(text(615, 45, "Сильне магнітне поле (B > 0)", size=13.5, bold=True, color=INK))
    f.append(text(615, 65, "Квантування Ландау: дельта-піки з уширенням", size=11.5, color=MUTED))

    ox2, oy2 = 450, 350
    f.append(line(ox2, oy2, 770, oy2, color=DARK, sw=1.5))
    f.append(line(ox2, oy2, ox2, 90, color=DARK, sw=1.5))
    f.append(polygon([(770, oy2-4), (780, oy2), (770, oy2+4)], fill=DARK))
    f.append(polygon([(ox2-4, 90), (ox2, 80), (ox2+4, 90)], fill=DARK))

    f.append(text(750, oy2 + 25, "Енергія E", size=11.5, bold=True, color=DARK))
    f.append(text(405, 82, "g₂D(E, B)", size=11.5, bold=True, color=DARK))

    l_centers = [ox2 + 70, ox2 + 170, ox2 + 270]
    labels = ["N = 0", "N = 1", "N = 2"]

    for i, cx in enumerate(l_centers):
        pts_g = []
        for x in range(cx - 45, cx + 46, 2):
            dx = (x - cx) / 14.0
            val = math.exp(-dx**2)
            y = oy2 - int(val * 180)
            pts_g.append((x, y))
        path_g = "M " + " L ".join("%d %d" % p for p in pts_g)
        f.append(svg_path(path_g, stroke="#c0392b", sw=2.2, fill="none"))

        if i == 0:
            pts_fill_l = [(cx - 45, oy2)] + pts_g + [(cx + 45, oy2)]
            f.append(polygon(pts_fill_l, fill="#e74c3c"))
        elif i == 1:
            pts_fill_l = [(cx - 45, oy2)]
            for p in pts_g:
                if p[0] <= ox2 + 180:
                    pts_fill_l.append(p)
            pts_fill_l.append((ox2 + 180, oy2))
            f.append(polygon(pts_fill_l, fill="#e74c3c"))

        f.append(line(cx, oy2, cx, oy2 - 185, color=MUTED, sw=1.0, dash="2 2"))
        f.append(text(cx - 16, oy2 + 20, labels[i], size=11, bold=True, color="#c0392b"))

    f.append(line(l_centers[0], oy2 - 120, l_centers[1], oy2 - 120, color="#d35400", sw=1.5))
    f.append(line(l_centers[0], oy2 - 115, l_centers[0], oy2 - 125, color="#d35400", sw=1.5))
    f.append(line(l_centers[1], oy2 - 115, l_centers[1], oy2 - 125, color="#d35400", sw=1.5))
    f.append(text(l_centers[0] + 25, oy2 - 130, "ħ·ω_c", size=11.5, bold=True, color="#d35400"))

    ef2_x = ox2 + 180
    f.append(line(ef2_x, oy2, ef2_x, 100, color="#7d3c98", sw=1.8, dash="4 3"))
    f.append(text(ef2_x - 12, oy2 + 20, "E_F", size=11.5, bold=True, color="#7d3c98"))
    f.append(text(ef2_x + 10, 115, "Фактор заповнення", size=10.5, bold=True, color="#7d3c98"))
    f.append(text(ef2_x + 10, 130, "ν = n_s / n₀ = 2", size=11, bold=True, color="#7d3c98"))

    f.append(text(460, 395, "Ємність одного рівня (виродження): n₀ = e·B / h", size=11, bold=True, color=DARK))

    render(os.path.join(OUT, "2deg-landau-levels.svg"), W, H, *f)


if __name__ == '__main__':
    fig_heterostructure_band()
    fig_density_of_states()
    fig_landau_levels()
    print("All 2DEG figures generated successfully.")
