# -*- coding: utf-8 -*-
"""Фігури до теми «Вектор Пойнтінга».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"  # зелений (вектор Пойнтінга S)
DARK   = "#0f172a"  # темний синій/вугільний
LINK   = "#2563eb"  # синій (електричне поле E)
POS    = "#dc2626"  # червоний (магнітне поле H / позитивний заряд)
NEG    = "#2563eb"
MUTED  = "#64748b"
WHITE  = "#ffffff"
BG     = "#ffffff"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Перенесення енергії у циліндричному резисторі ──────────────────
def fig_poynting_resistor():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 26, "Перенесення енергії у циліндричному резисторі (Вектор Пойнтінга)", size=15, bold=True))

    # Корпус резистора
    rx0, ry0, rw, rh = 240, 130, 300, 160
    f.append(rect(rx0, ry0, rw, rh, fill="#f8fafc", stroke=DARK, sw=2, rx=6))
    f.append(text(rx0 + rw / 2, ry0 + rh / 2, "Резистор (опір R, питомий опір ρ)", size=13, color=MUTED, bold=True))

    # Підвідні провідники
    f.append(line(70, ry0 + rh / 2, rx0, ry0 + rh / 2, color=DARK, sw=3.5))
    f.append(line(rx0 + rw, ry0 + rh / 2, 710, ry0 + rh / 2, color=DARK, sw=3.5))

    # Струм провідності I
    f.append(arrow(110, ry0 + rh / 2 - 14, 180, ry0 + rh / 2 - 14, color=LINK, sw=2))
    f.append(text(145, ry0 + rh / 2 - 28, "Струм I", size=12, color=LINK, bold=True))

    f.append(arrow(600, ry0 + rh / 2 - 14, 670, ry0 + rh / 2 - 14, color=LINK, sw=2))
    f.append(text(635, ry0 + rh / 2 - 28, "Струм I", size=12, color=LINK, bold=True))

    # Аксиальне електричне поле E всередині резистора
    f.append(arrow(rx0 + 20, ry0 + 40, rx0 + 280, ry0 + 40, color=LINK, sw=2))
    f.append(text(rx0 + 150, ry0 + 26, "Електричне поле E = V / L", size=12, color=LINK, bold=True))

    # Магнітне поле H на поверхні (позначки ⊙ зверху і ⊗ знизу)
    # Верхня межа
    for hx in range(270, 520, 70):
        f.append(circle(hx, ry0 - 12, 8, fill="#fef2f2", stroke=POS, sw=1.5))
        f.append(circle(hx, ry0 - 12, 2.5, fill=POS, stroke='none', sw=0))
    f.append(text(rx0 + rw / 2, ry0 - 28, "Магнітне поле H (направлене з дошки ⊙)", size=11, color=POS, bold=True))

    # Нижня межа
    for hx in range(270, 520, 70):
        f.append(circle(hx, ry0 + rh + 12, 8, fill="#fef2f2", stroke=POS, sw=1.5))
        f.append(line(hx - 5, ry0 + rh + 7, hx + 5, ry0 + rh + 17, color=POS, sw=1.5))
        f.append(line(hx - 5, ry0 + rh + 17, hx + 5, ry0 + rh + 7, color=POS, sw=1.5))
    f.append(text(rx0 + rw / 2, ry0 + rh + 32, "Магнітне поле H (направлене у дошку ⊗)", size=11, color=POS, bold=True))

    # Вектор Пойнтінга S = E × H (радіально всередину)
    # Зверху вниз
    for sx in range(270, 520, 70):
        f.append(arrow(sx, ry0 - 45, sx, ry0 - 2, color=ACCENT, sw=2.5))
    f.append(text(120, ry0 + 15, "Вектор Пойнтінга\nS = E × H\n(входить всередину)", size=11, color=ACCENT, bold=True))

    # Знизу вгору
    for sx in range(270, 520, 70):
        f.append(arrow(sx, ry0 + rh + 45, sx, ry0 + rh + 2, color=ACCENT, sw=2.5))

    # Інформаційна панель підсумку
    b_sum, w_s, h_s = textbox(W / 2, 380, "Повний потік енергії крізь бічну поверхню A = 2πaL:\nP = ∮ S · dA = S · (2πaL) = (E) · (I / 2πa) · (2πaL) = (E·L) · I = V · I = I²R", size=11, pad=6, fill="#ecfdf5", stroke=ACCENT, sw=1.5)
    f.append(b_sum)

    return render(os.path.join(IMG, "poynting-resistor.svg"), W, H, *f)


# ── Фігура 2: Розподіл полів та вектора Пойнтінга у коаксіальному кабелі ─────
def fig_poynting_coaxial():
    W, H = 780, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 26, "Розподіл полів та вектора Пойнтінга у коаксіальному кабелі", size=15, bold=True))

    # Ліва панель: поздовжній переріз
    f.append(rect(30, 55, 350, 320, fill="#f8fafc", stroke=MUTED, sw=1, rx=6))
    f.append(text(205, 75, "Поздовжній переріз лінії", size=13, bold=True))

    # Центральна жила (радіус a, потенціал +V, струм +I)
    f.append(rect(60, 195, 290, 30, fill="#dbeafe", stroke=LINK, sw=1.8, rx=2))
    f.append(text(205, 210, "Внутрішній провідник (+V, струм +I)", size=11, color=LINK, bold=True))

    # Зовнішній екран (радіус b, потенціал 0V, струм -I)
    f.append(rect(60, 100, 290, 20, fill="#e2e8f0", stroke=DARK, sw=1.8, rx=2))
    f.append(rect(60, 300, 290, 20, fill="#e2e8f0", stroke=DARK, sw=1.8, rx=2))
    f.append(text(205, 112, "Зовнішній екран (0V, струм −I)", size=11, color=DARK, bold=True))
    f.append(text(205, 312, "Зовнішній екран (0V, струм −I)", size=11, color=DARK, bold=True))

    # Радіальне E-поле між жилою та екраном
    for ex in (100, 180, 260, 320):
        f.append(arrow(ex, 195, ex, 122, color=LINK, sw=1.8))
        f.append(arrow(ex, 225, ex, 298, color=LINK, sw=1.8))
    f.append(text(125, 160, "E(r)", size=11, color=LINK, bold=True))

    # Вектор Пойнтінга S у діелектрику (зліва направо)
    for sx in (120, 220, 300):
        f.append(arrow(sx - 30, 160, sx + 30, 160, color=ACCENT, sw=2.2))
        f.append(arrow(sx - 30, 260, sx + 30, 260, color=ACCENT, sw=2.2))
    f.append(text(270, 150, "S = E × H", size=11, color=ACCENT, bold=True))

    # Права панель: поперечний переріз
    f.append(rect(400, 55, 350, 320, fill="#f8fafc", stroke=MUTED, sw=1, rx=6))
    f.append(text(575, 75, "Поперечний переріз (вектори S ⊙)", size=13, bold=True))

    cx, cy = 575, 215
    ra, rb = 30, 100

    # Екран та жила
    f.append(circle(cx, cy, rb + 10, fill="#e2e8f0", stroke=DARK, sw=1.8))
    f.append(circle(cx, cy, rb, fill="#ffffff", stroke=DARK, sw=1.5))
    f.append(circle(cx, cy, ra, fill="#dbeafe", stroke=LINK, sw=1.8))
    f.append(text(cx, cy, "+I", size=12, color=LINK, bold=True))

    # Магнітні лінії H (кола навколо жили)
    f.append('<circle cx="%.1f" cy="%.1f" r="65" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (cx, cy, POS))
    f.append(arrow(cx + 65, cy, cx + 65, cy - 8, color=POS, sw=1.5))
    f.append(text(cx + 72, cy - 20, "H(r)", size=11, color=POS, bold=True))

    # Радіальні вдобутки E(r)
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        x1 = cx + ra * math.cos(rad)
        y1 = cy + ra * math.sin(rad)
        x2 = cx + (rb - 5) * math.cos(rad)
        y2 = cy + (rb - 5) * math.sin(rad)
        f.append(arrow(x1, y1, x2, y2, color=LINK, sw=1.6))
    f.append(text(cx + 40, cy + 30, "E(r)", size=11, color=LINK, bold=True))

    # Позначка вектора S у діелектрику (з дошки на читача ⊙)
    for ang in (45, 135, 225, 315):
        rad = math.radians(ang)
        sx = cx + 65 * math.cos(rad)
        sy = cy + 65 * math.sin(rad)
        f.append(circle(sx, sy, 7, fill="#ecfdf5", stroke=ACCENT, sw=1.5))
        f.append(circle(sx, sy, 2, fill=ACCENT, stroke='none', sw=0))
    f.append(text(cx - 30, cy + 78, "S = E × H ⊙", size=11, color=ACCENT, bold=True))

    # Підсумок знизу
    b_sum, w_s, h_s = textbox(W / 2, 405, "Енергія передається виключно в діелектричному просторі: P = ∫ S · dA = V · I", size=11, pad=5, fill="#ecfdf5", stroke=ACCENT, sw=1.2)
    f.append(b_sum)

    return render(os.path.join(IMG, "poynting-coaxial.svg"), W, H, *f)


# ── Фігура 3: Вектор Пойнтінга у плоскій електромагнітній хвилі ───────────────
def fig_poynting_wave():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 26, "Вектор Пойнтінга у плоскій електромагнітній хвилі", size=15, bold=True))

    # Вісі координат
    ox, oy = 90, 230
    f.append(arrow(ox, oy, ox + 630, oy, color=DARK, sw=2))  # Вісь Z (поширення)
    f.append(text(ox + 645, oy + 4, "Z", size=13, bold=True))

    f.append(arrow(ox, oy, ox, oy - 160, color=LINK, sw=2))  # Вісь Y (E-поле)
    f.append(text(ox - 15, oy - 155, "Y (E)", size=13, color=LINK, bold=True))

    f.append(arrow(ox, oy, ox - 60, oy + 110, color=POS, sw=2))  # Вісь X (H-поле)
    f.append(text(ox - 80, oy + 120, "X (H)", size=13, color=POS, bold=True))

    # Намалюємо синусоїду E(z) та H(z)
    length = 540
    steps = 100
    pts_e = []
    pts_h = []
    pts_s = []

    for i in range(steps + 1):
        z = i / steps * length
        pz = ox + z
        # E(z) вздовж Y
        ey = 120 * math.sin(2 * math.pi * z / 270)
        py_e = oy - ey
        pts_e.append((pz, py_e))

        # H(z) вздовж X (похила вісь)
        hx = 70 * math.sin(2 * math.pi * z / 270)
        px_h = pz - hx * 0.5
        py_h = oy + hx * 0.8
        pts_h.append((px_h, py_h))

        # S(z) = E^2 / Z0 (завжди невід'ємний вздовж Z)
        sz = 80 * (math.sin(2 * math.pi * z / 270) ** 2)
        py_s = oy - sz
        pts_s.append((pz, py_s))

    # Лінії полів E та H
    path_e = "M " + " L ".join("%.1f,%.1f" % p for p in pts_e)
    path_h = "M " + " L ".join("%.1f,%.1f" % p for p in pts_h)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_e, LINK))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (path_h, POS))

    # Вертикальні стрілочки амплітуд E та H у деяких точках
    for i in range(12, steps, 25):
        pz, py_e = pts_e[i]
        f.append(line(pz, oy, pz, py_e, color=LINK, sw=1.5))
        px_h, py_h = pts_h[i]
        f.append(line(pz, oy, px_h, py_h, color=POS, sw=1.5))

    # Огинаюча вектора Пойнтінга S(z) (зелений пук)
    path_s = "M " + " L ".join("%.1f,%.1f" % p for p in pts_s)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_s, ACCENT))

    for i in range(6, steps, 12):
        pz, py_s = pts_s[i]
        if abs(py_s - oy) > 10:
            f.append(arrow(pz, oy, pz, py_s, color=ACCENT, sw=1.8))

    f.append(text(ox + 210, oy - 100, "Густина потоку S(z,t) = E(z,t) × H(z,t)", size=12, color=ACCENT, bold=True))
    f.append(text(ox + 460, oy - 50, "Середня інтенсивність <S> = ½ E₀ H₀", size=12, color=ACCENT, bold=True))

    # Інформаційна картка
    b_info, w_i, h_i = textbox(W / 2, 385, "Вектор Пойнтінга S пульсує з подвійною частотою 2ω, але завжди має строго додатний напрямок +Z", size=11, pad=5, fill="#ecfdf5", stroke=ACCENT, sw=1.2)
    f.append(b_info)

    return render(os.path.join(IMG, "poynting-wave.svg"), W, H, *f)


if __name__ == '__main__':
    fig_poynting_resistor()
    fig_poynting_coaxial()
    fig_poynting_wave()
    print("Згенеровано 3 фігури у ./img/")
