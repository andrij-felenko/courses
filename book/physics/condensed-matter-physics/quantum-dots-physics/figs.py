# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_str}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"{d_attr}/>'

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    st = f' stroke="{stroke}" stroke-width="{sw:.1f}"' if stroke != "none" else ''
    return f'<polygon points="{pts_str}" fill="{fill}"{st}/>'

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Густина електронних станів g(E) для 3D, 2D, 1D та 0D систем
# ════════════════════════════════════════════════════════════════════════════
def fig_density_of_states():
    W, H = 860, 360
    f = []

    # Заголовок
    f.append(text(W/2, 25, "Еволюція густини електронних станів g(E) від розмірності системи", size=15, bold=True, color=INK))

    panel_w = 190
    panel_gap = 15
    start_x = 25
    base_y = 290
    top_y = 75

    labels = [
        ("3D (Об'ємний кристал)", "g_3D(E) ∝ √E", "#2980b9"),
        ("2D (Квантова яма)", "g_2D(E) = const (східці)", "#27ae60"),
        ("1D (Квантовий дріт)", "g_1D(E) ∝ 1/√E (сингулярності)", "#d35400"),
        ("0D (Квантова точка)", "g_0D(E) = ∑ δ(E - E_n)", "#8e44ad")
    ]

    for idx, (title_str, sub_str, color_code) in enumerate(labels):
        px = start_x + idx * (panel_w + panel_gap)
        
        # Рамка панелі
        f.append(rect(px, top_y - 15, panel_w, 245, fill="#fcfcfc", stroke=MUTED, sw=1.0, rx=4))
        f.append(text(px + panel_w/2, top_y, title_str, size=11, bold=True, color=color_code))
        f.append(text(px + panel_w/2, top_y + 16, sub_str, size=9.5, color=MUTED))

        # Осі координат
        ax_x0 = px + 25
        ax_y0 = base_y - 20
        ax_x1 = px + panel_w - 15
        ax_y1 = top_y + 35

        # Вісь E
        f.append(line(ax_x0, ax_y0, ax_x1, ax_y0, color=DARK, sw=1.5))
        f.append(polygon([(ax_x1, ax_y0 - 3), (ax_x1 + 6, ax_y0), (ax_x1, ax_y0 + 3)], fill=DARK))
        f.append(text(ax_x1 - 5, ax_y0 + 15, "E", size=10, bold=True, color=DARK))

        # Вісь g(E)
        f.append(line(ax_x0, ax_y0, ax_x0, ax_y1, color=DARK, sw=1.5))
        f.append(polygon([(ax_x0 - 3, ax_y1), (ax_x0, ax_y1 - 6), (ax_x0 + 3, ax_y1)], fill=DARK))
        f.append(text(ax_x0 - 12, ax_y1 - 2, "g(E)", size=10, bold=True, color=DARK))

        # Графіки g(E)
        if idx == 0: # 3D — Парабола √E
            pts = []
            for i in range(50):
                t = i / 49.0
                ex = ax_x0 + t * (ax_x1 - ax_x0 - 15)
                ey = ax_y0 - 160 * math.sqrt(t)
                pts.append(f"{ex:.1f},{ey:.1f}")
            f.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color_code}" stroke-width="2.5"/>')
            # Заповнення під кривою
            pts_fill = [f"{ax_x0},{ax_y0}"] + pts + [f"{ax_x1 - 15},{ax_y0}"]
            f.append(f'<polygon points="{" ".join(pts_fill)}" fill="{color_code}" opacity="0.15"/>')

        elif idx == 1: # 2D — Східчастий спектр
            step_w = (ax_x1 - ax_x0 - 20) / 3.0
            step_h = 45
            path_d = f"M {ax_x0} {ax_y0}"
            curr_x = ax_x0
            curr_y = ax_y0
            for s in range(3):
                curr_y -= step_h
                path_d += f" V {curr_y} H {curr_x + step_w}"
                curr_x += step_w
            f.append(svg_path(path_d, stroke=color_code, sw=2.5))

        elif idx == 2: # 1D — Сингулярності 1/√E
            peak_w = (ax_x1 - ax_x0 - 20) / 3.0
            for s in range(3):
                px_start = ax_x0 + s * peak_w
                pts = []
                pts.append(f"{px_start:.1f},{ax_y0}")
                pts.append(f"{px_start + 1:.1f},{ax_y1 + 10}")
                for i in range(1, 30):
                    t = i / 29.0
                    ex = px_start + 1 + t * (peak_w - 1)
                    ey = ax_y0 - 30 - 90 / (1 + 4*t)
                    pts.append(f"{ex:.1f},{ey:.1f}")
                pts.append(f"{px_start + peak_w:.1f},{ax_y0}")
                f.append(f'<polygon points="{" ".join(pts)}" fill="{color_code}" opacity="0.15"/>')
                f.append(f'<polyline points="{" ".join(pts[1:-1])}" fill="none" stroke="{color_code}" stroke-width="2.2"/>')

        elif idx == 3: # 0D — Дискретні дельта-піки
            peaks = [
                (ax_x0 + 35, 170, "1S_e"),
                (ax_x0 + 80, 130, "1P_e"),
                (ax_x0 + 125, 90, "1D_e")
            ]
            for pk_x, pk_h, pk_lbl in peaks:
                f.append(line(pk_x, ax_y0, pk_x, ax_y0 - pk_h, color=color_code, sw=3.0))
                f.append(circle(pk_x, ax_y0 - pk_h, 4.5, fill=color_code, stroke="#4a148c", sw=1.5))
                f.append(text(pk_x, ax_y0 - pk_h - 12, pk_lbl, size=10, bold=True, color="#4a148c"))

    render(os.path.join(OUT, "density-of-states-0d.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Залежність оптичного спектра від радіуса точки та зсув Бруса
# ════════════════════════════════════════════════════════════════════════════
def fig_brus_quantization():
    W, H = 860, 380
    f = []

    f.append(text(W/2, 25, "Зсув Бруса та залежність колірного спектра від радіуса квантової точки", size=15, bold=True, color=INK))

    # Зони для трьох точок: Велика (R=6нм), Середня (R=3.5нм), Мала (R=2нм)
    dots_data = [
        ("Мала точка (R ≈ 2.0 нм)", "#2980b9", "Синій зсув (460 нм)", "E_g = 2.65 еВ", 130, 22),
        ("Середня точка (R ≈ 3.5 нм)", "#f1c40f", "Жовтий колір (570 нм)", "E_g = 2.12 еВ", 430, 38),
        ("Велика точка (R ≈ 6.0 нм)", "#c0392b", "Червоний колір (660 нм)", "E_g = 1.82 еВ", 730, 55)
    ]

    for title_str, col, emiss_str, eg_str, cx, qd_r in dots_data:
        # Рамка для кожного типу
        f.append(rect(cx - 120, 60, 240, 235, fill="#fafafa", stroke=MUTED, sw=1.0, rx=5))
        f.append(text(cx, 80, title_str, size=12, bold=True, color=INK))
        
        # Малюнок сферичної квантової точки
        f.append(circle(cx, 130, qd_r, fill=col, stroke=DARK, sw=1.5))
        f.append(text(cx, 130, f"R", size=10, bold=True, color="#ffffff" if col != "#f1c40f" else DARK))

        # Зонна діаграма (Зона провідності CB та Валентна зона VB)
        band_w = 90
        cb_y = 195 - (55 - qd_r)*0.8
        vb_y = 245 + (55 - qd_r)*0.8
        
        # Зона провідності CB
        f.append(rect(cx - band_w/2, cb_y - 12, band_w, 12, fill="#ebf5fb", stroke="#2980b9", sw=1.5))
        f.append(text(cx, cb_y - 4, "CB (1S_e)", size=9, bold=True, color="#1b4f72"))

        # Зона валентності VB
        f.append(rect(cx - band_w/2, vb_y, band_w, 12, fill="#f9ebea", stroke="#c0392b", sw=1.5))
        f.append(text(cx, vb_y + 9, "VB (1S_h)", size=9, bold=True, color="#7b241c"))

        # Оптичний перехід (Стрілка рекомбінації)
        f.append(line(cx, vb_y, cx, cb_y, color=col, sw=2.0, dash="3 3"))
        f.append(polygon([(cx - 4, cb_y + 6), (cx, cb_y), (cx + 4, cb_y + 6)], fill=col))
        
        # Текст E_g та випромінювання
        f.append(text(cx + 42, (cb_y + vb_y)/2, eg_str, size=10, bold=True, color=INK))
        f.append(text(cx, 280, emiss_str, size=10, bold=True, color=col))

    # Спектральна смуга внизу
    f.append(text(W/2, 312, "Залежність кольору люмінесценції від кінетичного квантування ΔE ∝ 1/R²", size=11, bold=True, color=MUTED))
    spec_x0 = 80
    spec_w = 700
    spec_y = 330
    
    # Градієнтна спектральна лінія
    f.append(rect(spec_x0, spec_y, spec_w, 20, fill="#111111", stroke=DARK, sw=1.0, rx=3))
    
    # Маркери спектра
    colors_spectrum = [
        (spec_x0 + 40, "#8e44ad", "400 нм"),
        (spec_x0 + 160, "#2980b9", "470 нм (R=2нм)"),
        (spec_x0 + 320, "#27ae60", "530 нм"),
        (spec_x0 + 460, "#f1c40f", "580 нм (R=3.5нм)"),
        (spec_x0 + 620, "#c0392b", "660 нм (R=6нм)")
    ]
    for mx, mcol, mlbl in colors_spectrum:
        f.append(circle(mx, spec_y + 10, 6, fill=mcol, stroke="#ffffff", sw=1.0))
        f.append(text(mx, spec_y + 34, mlbl, size=9.5, bold=True, color=INK))

    render(os.path.join(OUT, "brus-size-quantization.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Зонування зон гетероструктур ядро-оболонка: Type-I та Type-II
# ════════════════════════════════════════════════════════════════════════════
def fig_heterostructure_type1_type2():
    W, H = 860, 360
    f = []

    f.append(text(W/2, 25, "Зонування зон у гетероструктурах ядро-оболонка: Type-I та Type-II", size=15, bold=True, color=INK))

    # Розділювач панелей
    f.append(line(W/2, 50, W/2, 340, color=MUTED, sw=1.0, dash="4 4"))

    # ── Ліва панель: Type-I (CdSe/ZnS) ──
    cx1 = 215
    f.append(text(cx1, 55, "Type-I Alignment (CdSe / ZnS)", size=13, bold=True, color="#2980b9"))
    f.append(text(cx1, 73, "Обоє носіїв (e⁻ та h⁺) локалізовані в ядрі", size=10.5, color=MUTED))

    # Зонний профіль Type-I
    # Оболонка (Shell ZnS) -> Ядро (Core CdSe) -> Оболонка (Shell ZnS)
    # CB
    f.append(line(50, 110, 130, 110, color="#2980b9", sw=2.5))
    f.append(line(130, 110, 130, 150, color="#2980b9", sw=2.5))
    f.append(line(130, 150, 300, 150, color="#2980b9", sw=2.5))
    f.append(line(300, 150, 300, 110, color="#2980b9", sw=2.5))
    f.append(line(300, 110, 380, 110, color="#2980b9", sw=2.5))
    f.append(text(215, 138, "Зона провідності CB (Core)", size=10, bold=True, color="#1b4f72"))
    f.append(text(90, 100, "CB (Shell)", size=9.5, color="#2980b9"))

    # VB
    f.append(line(50, 270, 130, 270, color="#c0392b", sw=2.5))
    f.append(line(130, 270, 130, 230, color="#c0392b", sw=2.5))
    f.append(line(130, 230, 300, 230, color="#c0392b", sw=2.5))
    f.append(line(300, 230, 300, 270, color="#c0392b", sw=2.5))
    f.append(line(300, 270, 380, 270, color="#c0392b", sw=2.5))
    f.append(text(215, 245, "Валентна зона VB (Core)", size=10, bold=True, color="#7b241c"))
    f.append(text(90, 285, "VB (Shell)", size=9.5, color="#c0392b"))

    # Заряди e- та h+ у ядрі
    f.append(circle(200, 170, 6, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    f.append(text(200, 170, "e⁻", size=9, bold=True, color="#ffffff"))

    f.append(circle(230, 210, 6, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(text(230, 210, "h⁺", size=9, bold=True, color="#ffffff"))

    # Рекомбінація
    f.append(line(215, 178, 215, 202, color="#27ae60", sw=2.0, dash="2 2"))
    f.append(text(215, 310, "Квантовий вихід фотолюмінесценції > 90%", size=10.5, bold=True, color="#27ae60"))
    f.append(text(215, 328, "Застосування: Дисплеї QLED, біомаркери", size=10, color=DARK))


    # ── Права панель: Type-II (CdTe/CdSe) ──
    cx2 = 645
    f.append(text(cx2, 55, "Type-II Alignment (CdTe / CdSe)", size=13, bold=True, color="#d35400"))
    f.append(text(cx2, 73, "Просторове розділення: e⁻ у Shell, h⁺ у Core", size=10.5, color=MUTED))

    # Зонний профіль Type-II (Східчастий)
    # CB
    f.append(line(480, 160, 560, 160, color="#2980b9", sw=2.5))
    f.append(line(560, 160, 560, 120, color="#2980b9", sw=2.5))
    f.append(line(560, 120, 730, 120, color="#2980b9", sw=2.5))
    f.append(line(730, 120, 730, 160, color="#2980b9", sw=2.5))
    f.append(line(730, 160, 810, 160, color="#2980b9", sw=2.5))
    f.append(text(645, 138, "CB (Shell - e⁻)", size=10, bold=True, color="#1b4f72"))
    f.append(text(520, 175, "CB (Core)", size=9.5, color="#2980b9"))

    # VB
    f.append(line(480, 260, 560, 260, color="#c0392b", sw=2.5))
    f.append(line(560, 260, 560, 210, color="#c0392b", sw=2.5))
    f.append(line(560, 210, 730, 210, color="#c0392b", sw=2.5))
    f.append(line(730, 210, 730, 260, color="#c0392b", sw=2.5))
    f.append(line(730, 260, 810, 260, color="#c0392b", sw=2.5))
    f.append(text(645, 225, "VB (Core - h⁺)", size=10, bold=True, color="#7b241c"))
    f.append(text(520, 275, "VB (Shell)", size=9.5, color="#c0392b"))

    # Заряди розділені
    f.append(circle(520, 145, 6, fill="#2980b9", stroke="#1b4f72", sw=1.5))
    f.append(text(520, 145, "e⁻", size=9, bold=True, color="#ffffff"))

    f.append(circle(645, 195, 6, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(text(645, 195, "h⁺", size=9, bold=True, color="#ffffff"))

    # Перекриття та час життя
    f.append(line(526, 145, 639, 195, color="#d35400", sw=1.8, dash="3 3"))
    f.append(text(cx2, 310, "Довгий час життя носіїв (до мікросекунд)", size=10.5, bold=True, color="#d35400"))
    f.append(text(cx2, 328, "Застосування: Сонячні батареї, фотодетектори", size=10, color=DARK))

    render(os.path.join(OUT, "heterostructure-type1-type2.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Схема одноелектронного транзистора та ромби Кулона
# ════════════════════════════════════════════════════════════════════════════
def fig_coulomb_blockade():
    W, H = 860, 380
    f = []

    f.append(text(W/2, 25, "Однотранзисторна Кулонівська блокада та стабільність ромбів Кулона", size=15, bold=True, color=INK))

    f.append(line(410, 50, 410, 350, color=MUTED, sw=1.0, dash="4 4"))

    # ── Ліва панель: Схема SET та енергетичні рівні ──
    f.append(text(205, 55, "Одноелектронний транзистор (SET)", size=13, bold=True, color="#27ae60"))
    
    # Витік (Source), Затвор (Gate), Стік (Drain)
    # Source
    f.append(rect(30, 140, 70, 70, fill="#d5f5e3", stroke="#27ae60", sw=2.0))
    f.append(text(65, 178, "Source", size=11, bold=True, color="#1e8449"))

    # Drain
    f.append(rect(310, 140, 70, 70, fill="#d5f5e3", stroke="#27ae60", sw=2.0))
    f.append(text(345, 178, "Drain", size=11, bold=True, color="#1e8449"))

    # Квантова точка у центрі
    f.append(circle(205, 175, 45, fill="#ebf5fb", stroke="#2980b9", sw=2.5))
    f.append(text(205, 150, "Квантова точка", size=10, bold=True, color="#1b4f72"))
    f.append(text(205, 168, "E_C = e²/2C_∑", size=9.5, bold=True, color="#c0392b"))

    # Дискретні рівні у точці
    for qy in [182, 192, 202]:
        f.append(line(175, qy, 235, qy, color="#2980b9", sw=1.8))

    # Тунельні бар'єри
    f.append(rect(100, 155, 60, 40, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5))
    f.append(text(130, 178, "Бар'єр 1", size=9.5, color=MUTED))

    f.append(rect(250, 155, 60, 40, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5))
    f.append(text(280, 178, "Бар'єр 2", size=9.5, color=MUTED))

    # Затвор Gate внизу
    f.append(rect(145, 260, 120, 35, fill="#fdebd0", stroke="#d35400", sw=2.0))
    f.append(text(205, 282, "Gate (V_g)", size=11, bold=True, color="#7e5109"))
    f.append(line(205, 260, 205, 220, color="#d35400", sw=1.8, dash="3 3"))
    f.append(text(215, 240, "C_g", size=10, bold=True, color="#d35400"))

    f.append(text(205, 325, "Умова блокади: k_B T ≪ E_C  та  R_T ≫ h/e²", size=10, bold=True, color=DARK))


    # ── Права панель: Діаграма ромбів Кулона (V_ds vs V_g) ──
    cx2 = 635
    f.append(text(cx2, 55, "Діаграма стабільності (Ромби Кулона)", size=13, bold=True, color="#8e44ad"))

    # Осі: V_ds (вертикальна) та V_g (горизонтальна)
    ox0 = 460
    oy0 = 200
    ox1 = 810
    oy1 = 75

    # Горизонтальна вісь V_g
    f.append(line(ox0, oy0, ox1, oy0, color=DARK, sw=1.5))
    f.append(polygon([(ox1, oy0 - 3), (ox1 + 6, oy0), (ox1, oy0 + 3)], fill=DARK))
    f.append(text(ox1 - 10, oy0 + 18, "V_g (Напруга затвора)", size=10, bold=True, color=DARK))

    # Вертикальна вісь V_ds
    f.append(line(ox0 + 30, 310, ox0 + 30, oy1, color=DARK, sw=1.5))
    f.append(polygon([(ox0 + 27, oy1), (ox0 + 30, oy1 - 6), (ox0 + 33, oy1)], fill=DARK))
    f.append(text(ox0 + 40, oy1, "V_ds (Напруга витік-стік)", size=10, bold=True, color=DARK))

    # Ромби Кулона (Області N, N+1, N+2 електронів без струму I=0)
    diamonds = [
        (ox0 + 90, oy0, 50, 60, "N електронів"),
        (ox0 + 190, oy0, 50, 60, "N + 1 електронів"),
        (ox0 + 290, oy0, 50, 60, "N + 2 електронів")
    ]

    for d_cx, d_cy, dw, dh, d_lbl in diamonds:
        pts = [
            (d_cx - dw, d_cy),
            (d_cx, d_cy - dh),
            (d_cx + dw, d_cy),
            (d_cx, d_cy + dh)
        ]
        f.append(polygon(pts, fill="#f4ecf7", stroke="#8e44ad", sw=2.0))
        f.append(text(d_cx, d_cy - 16, d_lbl, size=9.5, bold=True, color="#4a148c"))

    # Текст пояснення
    f.append(text(cx2, 310, "Усередині ромбів: Кулонівська блокада (I = 0)", size=10.5, bold=True, color="#8e44ad"))
    f.append(text(cx2, 330, "На межі ромбів: Послідовне одноелектронне тунелювання", size=10, color=DARK))

    render(os.path.join(OUT, "coulomb-blockade-diamonds.svg"), W, H, *f)

if __name__ == "__main__":
    fig_density_of_states()
    fig_brus_quantization()
    fig_heterostructure_type1_type2()
    fig_coulomb_blockade()
    print("Всі 4 фігури успішно згенеровано у img/")
