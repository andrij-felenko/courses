# -*- coding: utf-8 -*-
"""Фігури до теми «Загасання звуку в повітрі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def iso_alpha_db_km(f, T=293.15, p_kPa=101.325, hr=50.0):
    """Розрахунок коефіцієнта поглинання за ISO 9613-1 у дБ/км."""
    p_pr = 101.325
    T_pr = 293.15
    T_01 = 273.16
    p_rel = p_kPa / p_pr
    T_rel = T / T_pr

    # Насичений тиск водяної пари
    exponent = -6.8346 * math.pow(T_01 / T, 1.261) + 4.6151
    p_sat_rel = math.pow(10.0, exponent)
    
    # Молярна концентрація вологи (%)
    h = hr * p_sat_rel / p_rel

    # Частоти релаксації кисню та азоту
    fr_O = p_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h))
    fr_N = p_rel * math.pow(T_rel, -0.5) * (9.0 + 280.0 * h * math.exp(-4.17 * (math.pow(T_rel, -1.0/3.0) - 1.0)))

    # Класичний та молекулярний внески (дБ/м)
    alpha_cl = 1.84e-11 * (1.0 / p_rel) * math.sqrt(T_rel)
    alpha_vib_O = math.pow(T_rel, -2.5) * 0.1068 * math.exp(-3352.0 / T) * (fr_O / (fr_O * fr_O + f * f))
    alpha_vib_N = math.pow(T_rel, -2.5) * 0.01275 * math.exp(-2239.1 / T) * (fr_N / (fr_N * fr_N + f * f))

    alpha_db_m = 8.686 * f * f * (alpha_cl + alpha_vib_O + alpha_vib_N)
    return alpha_db_m * 1000.0  # у дБ/км

# ── Фігура 1: Механізми загасання звуку ───────────────────────────────────────
def fig_attenuation_mechanisms():
    W, H = 840, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Механізми загасання звуку в атмосфері", size=16, bold=True))

    col_w = 240
    gap = 20
    x0 = 40

    # Колонка 1: Геометричне розходження
    x1 = x0
    f.append(rect(x1, 60, col_w, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + col_w/2, 88, "1. Геометричне розходження", size=14, bold=True, color=INK))
    f.append(text(x1 + col_w/2, 110, "Сферичний хвильовий фронт", size=12, color=MUTED))
    
    # Малюнок сферичного розширення
    cx, cy = x1 + col_w/2, 175
    f.append(circle(cx, cy, 8, fill=POS, stroke=POS, sw=1))
    f.append(circle(cx, cy, 25, fill="none", stroke=NEG, sw=1.5))
    f.append('<circle cx="%.1f" cy="%.1f" r="50" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (cx, cy, NEG))
    f.append('<circle cx="%.1f" cy="%.1f" r="75" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="2,4"/>' % (cx, cy, NEG))

    f.append(mtext(x1 + col_w/2, 260, "Інтенсивність  I ∝ 1/r²\nВтрати: −6 дБ за кожне\nподвоєння відстані\n(без втрат енергії середовищем)", size=12, color=INK))

    # Колонка 2: Класичне поглинання
    x2 = x1 + col_w + gap
    f.append(rect(x2, 60, col_w, 270, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x2 + col_w/2, 88, "2. Класичне поглинання", size=14, bold=True, color=FIELD))
    f.append(text(x2 + col_w/2, 110, "Термов'язкі втрати (Стокса–Кірхгофа)", size=12, color=MUTED))

    # Схема в'язкості і теплопровідності
    cy2 = 175
    f.append(rect(x2 + 30, cy2 - 30, col_w - 60, 60, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    f.append(text(x2 + col_w/2, cy2 - 8, "Зсувна в'язкість (η)", size=12, color=INK))
    f.append(text(x2 + col_w/2, cy2 + 14, "Теплопровідність (κ)", size=12, color=INK))

    f.append(mtext(x2 + col_w/2, 260, "Знищення звуку в тепло\nКоефіцієнт  α_cl ∝ f²\nПанує на ультразвуку\n(f > 50 кГц)", size=12, color=INK))

    # Колонка 3: Молекулярна релаксація
    x3 = x2 + col_w + gap
    f.append(rect(x3, 60, col_w, 270, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(x3 + col_w/2, 88, "3. Молекулярна релаксація", size=14, bold=True, color=POS))
    f.append(text(x3 + col_w/2, 110, "Збудження коливальних рівнів", size=12, color=MUTED))

    # Молекулярний перехід
    cy3 = 175
    f.append(circle(x3 + 70, cy3, 18, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x3 + 70, cy3 + 4, "N₂", size=12, bold=True, color=POS))
    f.append(circle(x3 + 170, cy3, 18, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x3 + 170, cy3 + 4, "O₂", size=12, bold=True, color=POS))
    f.append(arrow(x3 + 92, cy3, x3 + 148, cy3, color=POS, sw=1.5))

    f.append(mtext(x3 + col_w/2, 260, "Затримка фази між тиском і густиною\nПіки поглинання на  f_r,O  та  f_r,N\nВологість є каталізатором!", size=12, color=INK))

    return render(os.path.join(IMG, "attenuation-mechanisms.svg"), W, H, *f)

# ── Фігура 2: Залежність поглинання від вологості й частоти ──────────────────
def fig_relax_peaks():
    W, H = 840, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Коефіцієнт поглинання α у повітрі при T = 20°C для різної вологості", size=16, bold=True))

    ox, oy = 80, 330
    rx, ty = 790, 60
    pw = rx - ox
    ph = oy - ty

    # Осі логарифмічні
    def PX(freq):
        lf = math.log10(freq)
        return ox + pw * (lf - 2.0) / (5.0 - 2.0)

    def PY(alpha):
        if alpha < 0.1: alpha = 0.1
        la = math.log10(alpha)
        return oy - ph * (la - (-1.0)) / (3.0 - (-1.0))

    freq_ticks = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    for ft in freq_ticks:
        x = PX(ft)
        f.append(line(x, oy, x, ty, color="#e5e7eb", sw=1.0))
        if ft in [100, 1000, 10000, 100000]:
            lbl = "100 Гц" if ft==100 else ("1 кГц" if ft==1000 else ("10 кГц" if ft==10000 else "100 кГц"))
            f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
            f.append(text(x, oy + 20, lbl, size=11, color=INK))

    alpha_ticks = [0.1, 1.0, 10.0, 100.0, 1000.0]
    for at in alpha_ticks:
        y = PY(at)
        f.append(line(ox, y, rx, y, color="#e5e7eb", sw=1.0))
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        lbl = str(at) if at >= 1 else "0.1"
        f.append(text(ox - 10, y + 4, lbl, size=11, color=INK, anchor="end"))

    f.append(arrow(ox, oy, rx + 10, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 10, color=INK, sw=1.8))
    f.append(text(rx, oy + 36, "Частота f (Гц)", size=12, bold=True, anchor="end"))
    f.append(text(ox - 50, ty - 5, "α (дБ/км)", size=12, bold=True, anchor="start"))

    curves = [
        (10.0, "#dc2626", "10% (сухе)"),
        (30.0, "#d97706", "30%"),
        (50.0, "#2563eb", "50% (норма)"),
        (80.0, "#059669", "80% (вологе)")
    ]

    for hr, color, label in curves:
        pts = []
        for i in range(100):
            lf = 2.0 + 3.0 * i / 99.0
            freq = math.pow(10.0, lf)
            val = iso_alpha_db_km(freq, T=293.15, p_kPa=101.325, hr=hr)
            pts.append((PX(freq), PY(val)))
        
        path_d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_d, color))

    lx, ly = rx - 180, ty + 20
    f.append(rect(lx, ly, 170, 110, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(lx + 85, ly + 20, "Відносна вологість", size=12, bold=True))
    
    idx = 0
    for hr, color, label in curves:
        yy = ly + 40 + idx * 20
        f.append(line(lx + 15, yy, lx + 45, yy, color=color, sw=2.5))
        f.append(text(lx + 55, yy + 4, label, size=11, color=INK, anchor="start"))
        idx += 1

    return render(os.path.join(IMG, "relax-peaks.svg"), W, H, *f)

# ── Фігура 3: Спектральний фільтр атмосфери ──────────────────────────────────
def fig_spectrum_filter():
    W, H = 840, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Атмосфера як ФНЧ: деградація акустичного спектра з відстанню", size=16, bold=True))

    ox, oy = 80, 320
    rx, ty = 790, 60
    pw = rx - ox
    ph = oy - ty

    def PX(freq):
        lf = math.log10(freq)
        return ox + pw * (lf - 2.0) / (4.3 - 2.0)

    def PY(spl):
        return oy - ph * (spl - 0) / 120.0

    f.append(arrow(ox, oy, rx + 10, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 10, color=INK, sw=1.8))
    f.append(text(rx, oy + 32, "Частота f (Гц)", size=12, bold=True, anchor="end"))
    f.append(text(ox - 45, ty - 5, "Рівень SPL (дБ)", size=12, bold=True, anchor="start"))

    for ft, lbl in [(100, "100 Гц"), (500, "500 Гц"), (1000, "1 кГц"), (4000, "4 кГц"), (10000, "10 кГц"), (20000, "20 кГц")]:
        x = PX(ft)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, lbl, size=11, color=INK))

    for spl in [0, 30, 60, 90, 120]:
        y = PY(spl)
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(line(ox, y, rx, y, color="#f3f4f6", sw=1.0))
        f.append(text(ox - 10, y + 4, str(spl), size=11, color=INK, anchor="end"))

    distances = [
        (10, "#1e293b", "10 м (початковий)"),
        (200, "#2563eb", "200 м"),
        (800, "#d97706", "800 м"),
        (2000, "#dc2626", "2000 м (2 км)")
    ]

    for r, color, label in distances:
        pts = []
        for i in range(100):
            lf = 2.0 + 2.3 * i / 99.0
            freq = math.pow(10.0, lf)
            alpha_db_km = iso_alpha_db_km(freq, T=293.15, p_kPa=101.325, hr=50.0)
            alpha_db_m = alpha_db_km / 1000.0
            
            div_loss = 20.0 * math.log10(r / 10.0) if r > 10 else 0.0
            abs_loss = alpha_db_m * (r - 10.0) if r > 10 else 0.0
            
            spl = 100.0 - div_loss - abs_loss
            if spl < 0: spl = 0.0
            pts.append((PX(freq), PY(spl)))

        path_d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.3"/>' % (path_d, color))

    f.append(text(PX(300), PY(25) - 12, "Низькі частоти (гул) доходять далі", size=11, color="#dc2626", bold=True))
    f.append(text(PX(4000), PY(5) + 15, "Високі частоти відфільтровано", size=11, color="#dc2626", bold=True))

    lx, ly = rx - 200, ty + 10
    f.append(rect(lx, ly, 190, 110, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(lx + 95, ly + 20, "Відстань від джерела", size=12, bold=True))
    idx = 0
    for r, color, label in distances:
        yy = ly + 40 + idx * 20
        f.append(line(lx + 15, yy, lx + 45, yy, color=color, sw=2.5))
        f.append(text(lx + 55, yy + 4, label, size=11, color=INK, anchor="start"))
        idx += 1

    return render(os.path.join(IMG, "spectrum-filter.svg"), W, H, *f)

# ── Фігура 4: Декомпозиція складових поглинання ISO 9613-1 ────────────────────
def fig_iso9613_components():
    W, H = 840, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Декомпозиція складових поглинання звуку (ISO 9613-1)", size=16, bold=True))

    ox, oy = 80, 320
    rx, ty = 790, 60
    pw = rx - ox
    ph = oy - ty

    def PX(freq):
        lf = math.log10(freq)
        return ox + pw * (lf - 2.0) / (5.0 - 2.0)

    def PY(alpha):
        if alpha < 0.01: alpha = 0.01
        la = math.log10(alpha)
        return oy - ph * (la - (-2.0)) / (3.0 - (-2.0))

    f.append(arrow(ox, oy, rx + 10, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 10, color=INK, sw=1.8))
    f.append(text(rx, oy + 32, "Частота f (Гц)", size=12, bold=True, anchor="end"))
    f.append(text(ox - 45, ty - 5, "α (дБ/км)", size=12, bold=True, anchor="start"))

    for ft, lbl in [(100, "100 Гц"), (1000, "1 кГц"), (10000, "10 кГц"), (100000, "100 кГц")]:
        x = PX(ft)
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, lbl, size=11, color=INK))

    for at in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
        y = PY(at)
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(line(ox, y, rx, y, color="#f3f4f6", sw=1.0))
        f.append(text(ox - 10, y + 4, str(at), size=11, color=INK, anchor="end"))

    T, p_kPa, hr = 293.15, 101.325, 50.0
    p_pr, T_pr, T_01 = 101.325, 293.15, 273.16
    p_rel, T_rel = p_kPa / p_pr, T / T_pr
    exponent = -6.8346 * math.pow(T_01 / T, 1.261) + 4.6151
    p_sat_rel = math.pow(10.0, exponent)
    h = hr * p_sat_rel / p_rel

    fr_O = p_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h))
    fr_N = p_rel * math.pow(T_rel, -0.5) * (9.0 + 280.0 * h * math.exp(-4.17 * (math.pow(T_rel, -1.0/3.0) - 1.0)))

    pts_cl, pts_O, pts_N, pts_total = [], [], [], []

    for i in range(100):
        lf = 2.0 + 3.0 * i / 99.0
        freq = math.pow(10.0, lf)

        a_cl = 1.84e-11 * (1.0 / p_rel) * math.sqrt(T_rel)
        a_vib_O = math.pow(T_rel, -2.5) * 0.1068 * math.exp(-3352.0 / T) * (fr_O / (fr_O * fr_O + freq * freq))
        a_vib_N = math.pow(T_rel, -2.5) * 0.01275 * math.exp(-2239.1 / T) * (fr_N / (fr_N * fr_N + freq * freq))

        val_cl = 8.686 * freq * freq * a_cl * 1000.0
        val_O = 8.686 * freq * freq * a_vib_O * 1000.0
        val_N = 8.686 * freq * freq * a_vib_N * 1000.0
        val_tot = val_cl + val_O + val_N

        pts_cl.append((PX(freq), PY(val_cl)))
        pts_O.append((PX(freq), PY(val_O)))
        pts_N.append((PX(freq), PY(val_N)))
        pts_total.append((PX(freq), PY(val_tot)))

    def draw_path(pts, color, sw=2.0, dash=None):
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        dash_str = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, dash_str))

    draw_path(pts_cl, "#6b7280", 1.8, "4,4")
    draw_path(pts_O, "#dc2626", 1.8, "6,3")
    draw_path(pts_N, "#2563eb", 1.8, "6,3")
    draw_path(pts_total, "#111827", 2.6)

    f.append(line(PX(fr_O), oy, PX(fr_O), ty, color="#dc2626", sw=1.0, dash="2,3"))
    f.append(text(PX(fr_O) + 5, ty + 20, "f_r,O ≈ %.0f Гц" % fr_O, size=11, color="#dc2626", anchor="start"))

    f.append(line(PX(fr_N), oy, PX(fr_N), ty, color="#2563eb", sw=1.0, dash="2,3"))
    f.append(text(PX(fr_N) - 5, ty + 40, "f_r,N ≈ %.0f Гц" % fr_N, size=11, color="#2563eb", anchor="end"))

    lx, ly = ox + 20, ty + 10
    f.append(rect(lx, ly, 220, 110, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(lx + 110, ly + 20, "Складові за ISO 9613-1", size=12, bold=True))
    
    comp_list = [
        ("#111827", "Сумарний α_total", None),
        ("#dc2626", "Релаксація кисню (O₂)", "6,3"),
        ("#2563eb", "Релаксація азоту (N₂)", "6,3"),
        ("#6b7280", "Класичні втрати (α_cl)", "4,4")
    ]
    idx = 0
    for color, label, dash in comp_list:
        yy = ly + 38 + idx * 18
        f.append(line(lx + 15, yy, lx + 45, yy, color=color, sw=2.0, dash=dash))
        f.append(text(lx + 55, yy + 4, label, size=11, color=INK, anchor="start"))
        idx += 1

    return render(os.path.join(IMG, "iso9613-components.svg"), W, H, *f)

if __name__ == '__main__':
    fig_attenuation_mechanisms()
    fig_relax_peaks()
    fig_spectrum_filter()
    fig_iso9613_components()
    print("Всі 4 фігури успішно згенеровано у ./img/")
