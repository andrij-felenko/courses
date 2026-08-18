# -*- coding: utf-8 -*-
"""Фігури до теми «Плазма».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"

def polyline(pts, color=LINE, sw=1.5, dash=None):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" fill="none" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'

# ── Фігура 1: Дебаївське екранування ──────────────────────────────────────────
def fig_debye_shielding():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дебаївське екранування заряду у плазмі", size=16, bold=True))

    # Ліва панель: Схема хмари екранування (x=200, y=210)
    cx, cy = 200, 210
    r_debye = 110

    # Сфера Дебая (пунктирне коло)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#eef4ff" stroke="%s" stroke-width="1.6" stroke-dasharray="4,4"/>' % (cx, cy, r_debye, COLOR_BLUE))
    f.append(text(cx, cy - r_debye - 12, "Сфера Дебая (радіус λ_D)", size=12, bold=True, color=COLOR_BLUE))

    # Оточуючі електрони та іони у плазмі
    electrons = [
        (cx - 50, cy - 30), (cx + 40, cy - 50), (cx - 30, cy + 60),
        (cx + 60, cy + 30), (cx - 70, cy + 20), (cx + 20, cy - 80),
        (cx - 80, cy - 40), (cx + 70, cy - 20), (cx + 10, cy + 80),
        (cx - 40, cy - 70)
    ]
    for ex, ey in electrons:
        f.append(circle(ex, ey, 7, fill="#ffebee", stroke=COLOR_RED, sw=1.2))
        f.append(text(ex, ey + 3.5, "−", size=12, bold=True, color=COLOR_RED))

    ions = [
        (cx - 150, cy - 90), (cx + 160, cy - 100), (cx - 140, cy + 120),
        (cx + 150, cy + 110), (cx - 160, cy + 10), (cx + 170, cy - 10)
    ]
    for ix, iy in ions:
        f.append(circle(ix, iy, 8, fill="#e3f2fd", stroke=COLOR_BLUE, sw=1.2))
        f.append(text(ix, iy + 3.5, "+", size=11, bold=True, color=COLOR_BLUE))

    # Центральний пробний додатний заряд
    f.append(circle(cx, cy, 14, fill=COLOR_RED, stroke="#900C3F", sw=2))
    f.append(text(cx, cy + 4, "+Q", size=12, bold=True, color="#ffffff"))

    # Стрелочка радіуса λ_D
    f.append(line(cx, cy, cx + r_debye - 8, cy, color=COLOR_BLUE, sw=1.5))
    f.append(arrow(cx + r_debye - 18, cy, cx + r_debye, cy, color=COLOR_BLUE, sw=1.5))
    f.append(text(cx + r_debye / 2, cy - 8, "λ_D", size=12, bold=True, color=COLOR_BLUE))

    # Права панель: Графік потенціалу Φ(r) (x: 440..710, y: 70..330)
    gx0, gy0 = 440, 330
    gw, gh = 270, 240
    gx_max = gx0 + gw
    gy_max = gy0 - gh

    # Осі координат
    f.append(line(gx0, gy0, gx_max + 15, gy0, color=LINE, sw=1.5))
    f.append(arrow(gx_max, gy0, gx_max + 15, gy0, color=LINE, sw=1.5))
    f.append(text(gx_max + 5, gy0 + 20, "Відстань r", size=11, bold=True))

    f.append(line(gx0, gy0, gx0, gy_max - 15, color=LINE, sw=1.5))
    f.append(arrow(gx0, gy_max, gx0, gy_max - 15, color=LINE, sw=1.5))
    f.append(text(gx0 - 15, gy_max - 10, "Потенціал Φ(r)", size=11, bold=True))

    # Вертикальна пунктирна лінія на r = λ_D
    r_scale = 90
    f.append(line(gx0 + r_scale, gy0, gx0 + r_scale, gy_max, color="#bdc3c7", sw=1.2, dash="3,3"))
    f.append(text(gx0 + r_scale, gy0 + 18, "r = λ_D", size=11, bold=True, color=COLOR_BLUE))

    # Крива вакуумного потенціалу (Кулон ~ 1/r) - червона пунктирна
    pts_coulomb = []
    for i in range(10, 260, 5):
        r_val = i / r_scale
        phi = 0.85 / max(r_val, 0.15)
        y = gy0 - min(phi * 65, gh - 10)
        pts_coulomb.append((gx0 + i, y))
    f.append(polyline(pts_coulomb, color=COLOR_RED, sw=1.8, dash="5,4"))

    # Крива дебаївського потенціалу (Екранований ~ (1/r) e^(-r/λ_D)) - синя суцільна
    import math
    pts_debye = []
    for i in range(10, 260, 5):
        r_val = i / r_scale
        phi = (0.85 / max(r_val, 0.15)) * math.exp(-r_val)
        y = gy0 - min(phi * 65, gh - 10)
        pts_debye.append((gx0 + i, y))
    f.append(polyline(pts_debye, color=COLOR_BLUE, sw=2.5))

    # Легенда графіка
    f.append(line(gx0 + 70, gy_max + 35, gx0 + 100, gy_max + 35, color=COLOR_RED, sw=1.8, dash="5,4"))
    f.append(text(gx0 + 105, gy_max + 39, "Вакуум (1/r)", size=11, color=COLOR_RED))

    f.append(line(gx0 + 70, gy_max + 60, gx0 + 100, gy_max + 60, color=COLOR_BLUE, sw=2.5))
    f.append(text(gx0 + 105, gy_max + 64, "Плазма (екрановано)", size=11, bold=True, color=COLOR_BLUE))

    render(os.path.join(IMG, 'debye-shielding.svg'), W, H, *f)


# ── Фігура 2: Плазмові коливання Ленгмюра ─────────────────────────────────────
def fig_plasma_oscillations():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Механізм плазмових (ленгмюрівських) коливань", size=16, bold=True))

    # Стан 1: Рівноважний квазінейтральний стан (Верхній блок)
    f.append(text(60, 68, "1. Рівновага (квазінейтральність):", size=13, bold=True, color=COLOR_DARK))
    f.append(rect(60, 80, 640, 50, fill="#f8f9fa", stroke="#ced4da", sw=1.5, rx=6))
    
    # Іони та електрони у рівновазі
    for i in range(10):
        x = 90 + i * 60
        f.append(circle(x, 105, 10, fill="#e3f2fd", stroke=COLOR_BLUE, sw=1.2))
        f.append(text(x, 109, "+", size=11, bold=True, color=COLOR_BLUE))
        f.append(circle(x + 16, 105, 8, fill="#ffebee", stroke=COLOR_RED, sw=1.2))
        f.append(text(x + 16, 109, "−", size=11, bold=True, color=COLOR_RED))

    # Стан 2: Зсув електронної хмари (Нижній блок)
    f.append(text(60, 168, "2. Зсув електронного шару на відстань x:", size=13, bold=True, color=COLOR_DARK))
    f.append(rect(60, 180, 640, 90, fill="#fff9db", stroke="#f1c40f", sw=1.5, rx=6))

    # Нерухомі іони
    for i in range(10):
        x = 90 + i * 60
        f.append(circle(x, 210, 10, fill="#e3f2fd", stroke=COLOR_BLUE, sw=1.2))
        f.append(text(x, 214, "+", size=11, bold=True, color=COLOR_BLUE))

    # Зсунуті електрони (зсув на +28px праворуч)
    shift = 28
    for i in range(10):
        x = 90 + i * 60 + shift
        f.append(circle(x, 240, 8, fill="#ffebee", stroke=COLOR_RED, sw=1.2))
        f.append(text(x, 244, "−", size=11, bold=True, color=COLOR_RED))

    # Зона нескомпенсованого додатного заряду ліворуч
    f.append('<rect x="75.0" y="190.0" width="%.1f" height="70.0" rx="6" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (shift + 10, COLOR_BLUE))
    f.append(text(88, 198, "+σ", size=11, bold=True, color=COLOR_BLUE))

    # Зона нескомпенсованого від'ємного заряду праворуч
    f.append('<rect x="625.0" y="190.0" width="%.1f" height="70.0" rx="6" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (shift + 10, COLOR_RED))
    f.append(text(638, 198, "−σ", size=11, bold=True, color=COLOR_RED))

    # Вектор повертального електричного поля E
    f.append(line(615, 225, 460, 225, color=COLOR_PURPLE, sw=2.5))
    f.append(line(280, 225, 125, 225, color=COLOR_PURPLE, sw=2.5))
    f.append(arrow(155, 225, 125, 225, color=COLOR_PURPLE, sw=2.5))
    b_e, w_e, h_e = textbox(370, 225, "Відновлювальне поле E", size=12, pad=5, fill="#f3e5f5", stroke=COLOR_PURPLE, sw=1.2)
    f.append(b_e)

    # Підпис частоти Ленгмюра під схемою
    b_w, w_w, h_w = textbox(W / 2, 315, "Плазмова частота електронних коливань:  ω_pe = √(n_e · e² / (ε₀ · m_e))",
                           size=13, pad=8, fill="#e8f5e9", stroke=COLOR_GREEN, sw=1.4)
    f.append(b_w)

    render(os.path.join(IMG, 'plasma-oscillations.svg'), W, H, *f)


# ── Фігура 3: Дрейф у схрещених полях E × B ───────────────────────────────────
def fig_eb_drift():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дрейф у схрещених полях (E × B дрейф)", size=16, bold=True))

    # Позначення орієнтації полів
    # Поле E спрямоване вниз
    f.append(line(60, 60, 60, 130, color=COLOR_PURPLE, sw=2))
    f.append(arrow(60, 100, 60, 130, color=COLOR_PURPLE, sw=2))
    f.append(text(60, 50, "Електричне поле E (вниз)", size=11, bold=True, color=COLOR_PURPLE))

    # Магнітне поле B спрямоване в картинку (хрестики)
    f.append(circle(60, 180, 12, fill="none", stroke=COLOR_BLUE, sw=1.5))
    f.append(line(52, 172, 68, 188, color=COLOR_BLUE, sw=1.5))
    f.append(line(52, 188, 68, 172, color=COLOR_BLUE, sw=1.5))
    f.append(text(60, 208, "Магнітне поле B (вглиб)", size=11, bold=True, color=COLOR_BLUE))

    # Ліва частина: Рух іона (+q)
    f.append(text(230, 60, "Додатний іон (+q)", size=13, bold=True, color=COLOR_BLUE))
    
    # Траєкторія іона: циклоїда з дрейфом праворуч
    import math
    pts_ion = []
    for t_deg in range(0, 720, 10):
        t = math.radians(t_deg)
        x = 120 + 70 * t - 40 * math.sin(t)
        y = 170 + 40 * (1 - math.cos(t))
        pts_ion.append((x, y))
    f.append(polyline(pts_ion, color=COLOR_BLUE, sw=2))

    # Початкова точкою іона
    f.append(circle(120, 170, 7, fill=COLOR_BLUE, stroke="#1a365d", sw=1.5))
    f.append(text(120, 155, "+q", size=11, bold=True, color=COLOR_BLUE))

    # Напрямок дрейфу v_E праворуч
    f.append(line(180, 260, 320, 260, color=COLOR_GREEN, sw=2.5))
    f.append(arrow(280, 260, 320, 260, color=COLOR_GREEN, sw=2.5))
    f.append(text(250, 280, "Дрейф v_E = (E × B) / B²", size=12, bold=True, color=COLOR_GREEN))

    # Права частина: Рух електрона (-q)
    f.append(text(550, 60, "Від'ємний електрон (−e)", size=13, bold=True, color=COLOR_RED))

    # Траєкторія електрона: закрутка в протилежний бік, але ДРЕЙФ ТАКОЖ ПРАВОРУЧ!
    pts_elec = []
    for t_deg in range(0, 720, 10):
        t = math.radians(t_deg)
        x = 440 + 70 * t + 30 * math.sin(t)
        y = 170 - 30 * (1 - math.cos(t))
        pts_elec.append((x, y))
    f.append(polyline(pts_elec, color=COLOR_RED, sw=2))

    f.append(circle(440, 170, 6, fill=COLOR_RED, stroke="#78281f", sw=1.5))
    f.append(text(440, 155, "−e", size=11, bold=True, color=COLOR_RED))

    # Напрямок дрейфу електрона (теж праворуч!)
    f.append(line(500, 260, 640, 260, color=COLOR_GREEN, sw=2.5))
    f.append(arrow(600, 260, 640, 260, color=COLOR_GREEN, sw=2.5))
    f.append(text(570, 280, "Дрейф v_E (у той самий бік!)", size=12, bold=True, color=COLOR_GREEN))

    # Інформаційна вставка знизу
    b_info, w_i, h_i = textbox(W / 2, 355,
                               "Унікальна властивість E × B дрейфу: швидкість v_E залежить ЛИШЕ від піль (E/B)\nі БАЙДУЖА до маси й знака заряду частинки. Струму немає — плазма дрейфує як єдине ціле!",
                               size=12, pad=8, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.4)
    f.append(b_info)

    render(os.path.join(IMG, 'eb-drift.svg'), W, H, *f)


# ── Фігура 4: Теорема про вмороженість магнітного поля ────────────────────────
def fig_frozen_in_field():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Теорема Альфвена про вмороженість магнітного поля", size=16, bold=True))

    # Лівий стан: Початкові силові лінії у плазмі (t = t1)
    f.append(text(200, 60, "1. Початковий стан плазми (t = t₁)", size=13, bold=True, color=COLOR_DARK))

    # Об'єм плазми (світло-зелена пляма/контур)
    f.append('<ellipse cx="200" cy="180" rx="80" ry="90" fill="#e8f8f5" stroke="%s" stroke-width="2"/>' % COLOR_GREEN)
    f.append(text(200, 180, "Плазмовий\nоб'єм", size=12, bold=True, color=COLOR_GREEN))

    # Прямі силові лінії B
    for y in [110, 150, 190, 230, 270]:
        f.append(line(70, y, 330, y, color=COLOR_RED, sw=1.8))
        f.append(arrow(310, y, 330, y, color=COLOR_RED, sw=1.8))
    f.append(text(340, 190, "B", size=13, bold=True, color=COLOR_RED))

    # Стрілка переходу / руху плазми
    f.append(line(370, 180, 420, 180, color=COLOR_DARK, sw=2.5))
    f.append(arrow(400, 180, 425, 180, color=COLOR_DARK, sw=2.5))
    f.append(text(397, 160, "Рух плазми v", size=11, bold=True, color=COLOR_DARK))

    # Правий стан: Деформовані силові лінії разом із плазмою (t = t2)
    f.append(text(570, 60, "2. Деформація разом із полем (t = t₂)", size=13, bold=True, color=COLOR_DARK))

    # Зсунутий і вигнутий об'єм плазми
    f.append('<ellipse cx="580" cy="180" rx="100" ry="70" fill="#e8f8f5" stroke="%s" stroke-width="2"/>' % COLOR_GREEN)
    f.append(text(580, 180, "Зсунута\nплазма", size=12, bold=True, color=COLOR_GREEN))

    # Зігнуті силові лінії B, захоплені плазмою!
    for y_base in [110, 150, 190, 230, 270]:
        dy = 40 if y_base == 190 else (25 if y_base in [150, 230] else 10)
        pts_line = [(450, y_base), (520, y_base), (580, y_base + dy), (640, y_base), (710, y_base)]
        f.append(polyline(pts_line, color=COLOR_RED, sw=1.8))
        f.append(arrow(690, y_base, 710, y_base, color=COLOR_RED, sw=1.8))
    f.append(text(720, 190, "B", size=13, bold=True, color=COLOR_RED))

    # Текстове пояснення у рамці знизу
    b_mhd, w_m, h_m = textbox(W / 2, 315,
                              "При високій провідності σ → ∞ (магнітне число Рейнольдса R_m >> 1)\nмагнітні силові лінії «вморожені» у плазму: вони рухаються й деформуються разом із рідиною.",
                              size=12, pad=8, fill="#fdfefe", stroke="#bdc3c7", sw=1.4)
    f.append(b_mhd)

    render(os.path.join(IMG, 'frozen-in-field.svg'), W, H, *f)


if __name__ == '__main__':
    fig_debye_shielding()
    fig_plasma_oscillations()
    fig_eb_drift()
    fig_frozen_in_field()
    print("Всі 4 SVG фігури для теми plasma-physics успішно згенеровано!")
