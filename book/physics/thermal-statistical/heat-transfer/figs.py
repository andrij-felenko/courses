# -*- coding: utf-8 -*-
"""Фігури до теми «Теплопередача».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COL_HOT  = "#c0392b"   # гаряче (червоне)
COL_COLD = "#2457d6"   # холодне (синє)
COL_FLUX = "#e67e22"   # потік тепла (помаранчеве)
COL_FLOW = "#27ae60"   # потік рідини/газу (зелене)

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))

# ── Фігура 1: Три канали теплопередачі ──────────────────────────────────────
def fig_heat_modes():
    W, H = 920, 450
    f = [text(W / 2, 32, "Три базові фізичні механізми перенесення теплової енергії", size=16, bold=True)]

    # 1. Теплопровідність
    f.append(rect(40, 65, 260, 360, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(170, 95, "1. Теплопровідність", size=14, bold=True, color=INK))
    f.append(text(170, 115, "(Conduction)", size=12, italic=True, color=MUTED))
    
    # Тверде тіло з градієнтом
    f.append(rect(65, 140, 210, 100, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(rect(65, 140, 50, 100, fill="#fadbd8", stroke="none"))
    f.append(rect(225, 140, 50, 100, fill="#d4e6f1", stroke="none"))
    # атоми в решітці
    for ax in range(85, 260, 30):
        for ay in range(160, 230, 30):
            r_atom = 8 if ax < 130 else (6 if ax < 200 else 4)
            c_atom = COL_HOT if ax < 130 else (COL_FLUX if ax < 200 else COL_COLD)
            f.append(circle(ax, ay, r_atom, fill=c_atom, stroke=LINE, sw=1))
    f.append(arrow(110, 190, 230, 190, color=COL_FLUX, sw=2.5))
    f.append(text(170, 180, "q (контактний потік)", size=11, bold=True, color=COL_FLUX))

    tb1, _, _ = textbox(170, 320, "Безперервний обмін хаотичним\nкінетичним імпульсом мікрочастинок\nу твердих тілах та середовищах", size=11.5, pad=8, fill="#f8f9f9")
    f.append(tb1)

    # 2. Конвекція
    f.append(rect(330, 65, 260, 360, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(460, 95, "2. Конвекція", size=14, bold=True, color=INK))
    f.append(text(460, 115, "(Convection)", size=12, italic=True, color=MUTED))

    # Стінка + потік
    f.append(rect(355, 140, 30, 100, fill=COL_HOT, stroke=LINE, sw=1.5, rx=2))
    # траєкторії рідини
    f.append(path("M 405 225 Q 435 215 445 185 Q 455 155 495 150", stroke=COL_FLOW, sw=2, dash="4,3"))
    f.append(path("M 405 235 Q 455 230 475 195 Q 495 160 545 155", stroke=COL_FLOW, sw=2))
    f.append(arrow(535, 155, 555, 155, color=COL_FLOW, sw=2))
    f.append(arrow(385, 190, 455, 190, color=COL_FLUX, sw=2.2))
    f.append(text(435, 180, "q_conv", size=11, bold=True, color=COL_FLUX))

    tb2, _, _ = textbox(460, 320, "Макроскопічне перенесення маси\nпідігрітого флюїду (газу чи рідини)\nтечією (примусовою чи природною)", size=11.5, pad=8, fill="#f8f9f9")
    f.append(tb2)

    # 3. Випромінювання
    f.append(rect(620, 65, 260, 360, fill="#fdfefe", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(750, 95, "3. Випромінювання", size=14, bold=True, color=INK))
    f.append(text(750, 115, "(Radiation)", size=12, italic=True, color=MUTED))

    # Гаряче тіло випромінює хвилі у вакуум
    f.append(circle(675, 190, 30, fill=COL_HOT, stroke=LINE, sw=1.5))
    f.append(text(675, 194, "T₁", size=13, bold=True, color="#ffffff"))

    f.append(path("M 715 170 Q 730 160 745 170 T 775 170 T 805 170", stroke=COL_FLUX, sw=2))
    f.append(path("M 715 190 Q 730 180 745 190 T 775 190 T 805 190", stroke=COL_FLUX, sw=2))
    f.append(path("M 715 210 Q 730 200 745 210 T 775 210 T 805 210", stroke=COL_FLUX, sw=2))
    f.append(arrow(805, 190, 825, 190, color=COL_FLUX, sw=2))

    f.append(rect(830, 160, 20, 60, fill=COL_COLD, stroke=LINE, sw=1.5, rx=2))
    f.append(text(840, 233, "T₂", size=11, bold=True, color=COL_COLD))

    tb3, _, _ = textbox(750, 320, "Випромінювання електромагнітних\nфотонів (інфрачервоний спектр),\nне потребує матеріального середовища", size=11.5, pad=8, fill="#f8f9f9")
    f.append(tb3)

    render(os.path.join(IMG, "heat-modes.svg"), W, H, *f)

# ── Фігура 2: Мікроскопічна картина теплопровідності ─────────────────────────
def fig_micro_conduction():
    W, H = 880, 420
    f = [text(W / 2, 30, "Мікроскопічний механізм теплопровідності: фонони та вільні електрони", size=16, bold=True)]

    # Ліва частина — Діелектрики (Фонони)
    f.append(rect(40, 70, 385, 320, fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(text(232, 98, "Діелектрики та ізолятори: фонони", size=14, bold=True, color=INK))
    f.append(text(232, 118, "Тепло переноситься квантами коливань решітки", size=11.5, italic=True, color=MUTED))

    # Кріплення решітки пружинками
    for ix in range(80, 390, 60):
        for iy in range(160, 290, 50):
            f.append(circle(ix, iy, 12, fill="#ebf5fb" if ix > 220 else "#fadbd8", stroke=LINE, sw=1.2))
            if ix < 330:
                f.append(path("M %d %d Q %d %d %d %d T %d %d" % (ix+12, iy, ix+27, iy-6, ix+42, iy, ix+48, iy), stroke=MUTED, sw=1.2))

    # Стрілка поширення хвилі
    f.append(path("M 90 310 Q 150 290 220 310 T 350 310", stroke=COL_HOT, sw=2.2, dash="3,3"))
    f.append(arrow(340, 310, 375, 310, color=COL_HOT, sw=2.2))
    f.append(text(232, 340, "Хвиля решіткового збудження (фонон)", size=12, bold=True, color=COL_HOT))

    # Права частина — Метали (Електрони)
    f.append(rect(455, 70, 385, 320, fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(text(647, 98, "Метали: електронний газ (k = k_e + k_ph)", size=14, bold=True, color=INK))
    f.append(text(647, 118, "Вільні електрони дають ~90-95% теплопровідності", size=11.5, italic=True, color=MUTED))

    # Іони решітки
    for ix in range(495, 820, 70):
        for iy in range(160, 290, 60):
            f.append(circle(ix, iy, 15, fill="#f2f4f4", stroke=LINE, sw=1.5))
            f.append(text(ix, iy+4, "+", size=14, bold=True, color=MUTED))

    # Хаотичні штрихи електронного газу
    e_paths = [
        "M 480 170 Q 510 190 540 160 T 600 210",
        "M 500 250 Q 560 210 610 260 T 710 200",
        "M 520 280 Q 620 270 680 230 T 780 260"
    ]
    for ep in e_paths:
        f.append(path(ep, stroke=COL_HOT, sw=1.5, dash="2,2"))
        
    f.append(arrow(520, 310, 760, 310, color=COL_HOT, sw=2.5))
    f.append(text(647, 340, "Швидкий дифузійний потік електронного газу", size=12, bold=True, color=COL_HOT))

    render(os.path.join(IMG, "micro-conduction.svg"), W, H, *f)

# ── Фігура 3: Закон Фур'є та градієнт температури ───────────────────────────
def fig_fourier_law():
    W, H = 880, 440
    f = [text(W / 2, 30, "Одновимірна теплопровідність та градієнт температури (Закон Фур'є)", size=16, bold=True)]

    # Вісь координат X
    f.append(arrow(100, 330, 780, 330, color=INK, sw=1.8))
    f.append(text(795, 334, "x", size=14, bold=True))

    # Вісь T
    f.append(arrow(140, 350, 140, 80, color=INK, sw=1.8))
    f.append(text(140, 65, "T (°C)", size=14, bold=True))

    # Стінка товщиною L
    x1, x2 = 260, 620
    y_t1, y_t2 = 120, 270

    f.append(rect(x1, 90, x2 - x1, 230, fill="#fafafa", stroke="#d5dbdb", sw=1.2))

    # Гаряча й холодна межі
    f.append(line(x1, 90, x1, 320, color=COL_HOT, sw=2, dash="4,4"))
    f.append(line(x2, 90, x2, 320, color=COL_COLD, sw=2, dash="4,4"))

    f.append(circle(x1, y_t1, 5, fill=COL_HOT, stroke=INK, sw=1))
    f.append(circle(x2, y_t2, 5, fill=COL_COLD, stroke=INK, sw=1))

    f.append(text(x1 - 15, y_t1 - 10, "T₁ (Гаряча)", size=13, bold=True, color=COL_HOT, anchor="end"))
    f.append(text(x2 + 15, y_t2 + 15, "T₂ (Холодна)", size=13, bold=True, color=COL_COLD, anchor="start"))

    # Лінійний профіль T(x)
    f.append(line(x1, y_t1, x2, y_t2, color=COL_HOT, sw=3))
    f.append(text(440, 175, "dT / dx = (T₂ - T₁) / L < 0", size=13, bold=True, color=COL_HOT))

    # Потік тепла q
    f.append(arrow(320, 230, 560, 230, color=COL_FLUX, sw=3.5))
    f.append(text(440, 215, "Тепловий потік q = -k (dT/dx)", size=14, bold=True, color=COL_FLUX))

    # Позначення товщини L
    f.append(arrow(x1, 355, x2, 355, color=INK, sw=1.4))
    f.append(arrow(x2, 355, x1, 355, color=INK, sw=1.4))
    f.append(text((x1 + x2)/2, 375, "Товщина стінки L", size=13))

    tb, _, _ = textbox(W / 2, 410, "Знак мінус показує, що тепло завжди передається у напрямку ЗМЕНШЕННЯ температури", size=12, pad=6, fill="#fef9e7", stroke="#f1c40f")
    f.append(tb)

    render(os.path.join(IMG, "fourier-law.svg"), W, H, *f)

# ── Фігура 4: Ламінарний та турбулентний пристінковий шар при конвекції ─────
def fig_convection_boundary():
    W, H = 900, 430
    f = [text(W / 2, 30, "Тепловий та гідродинамічний пристінкові шари при конвекції", size=16, bold=True)]

    # Гаряча поверхня пластини
    f.append(rect(80, 310, 760, 25, fill="#e74c3c", stroke=LINE, sw=1.5))
    f.append(text(460, 327, "Гаряча поверхня (T_s = const)", size=13, bold=True, color="#ffffff"))

    # Набігаючий потік рідини U_inf, T_inf
    for yf in range(120, 290, 40):
        f.append(arrow(40, yf, 100, yf, color=COL_FLOW, sw=1.8))
    f.append(text(35, 100, "Набігаючий потік: U_∞, T_∞", size=12.5, bold=True, color=COL_FLOW, anchor="start"))

    # Крива пристінкового шару δ(x)
    f.append(path("M 100 310 Q 250 250 450 180 T 840 110", stroke=INK, sw=2, dash="5,4"))
    f.append(text(650, 125, "Границя теплового шару δ_t(x)", size=12, bold=True, color=INK))

    # Профілі швидкостей / температур на різній відстані x
    for x_pos in (240, 480, 720):
        f.append(line(x_pos, 310, x_pos, 140, color="#bdc3c7", sw=1, dash="2,2"))
        f.append(path("M %d 310 Q %d 240 %d 170" % (x_pos, x_pos + 40, x_pos + 70), stroke=COL_HOT, sw=2))
        f.append(text(x_pos + 15, 290, "T(y)", size=11, color=COL_HOT))

    # Зони: ламінарна та турбулентна
    f.append(line(420, 310, 420, 80, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(260, 75, "Ламінарний режим", size=13, bold=True, color=COL_FLOW))
    f.append(text(630, 75, "Турбулентний режим (підвищена віддача h)", size=13, bold=True, color=COL_HOT))

    # Формула Ньютона-Ріхмана
    tb, _, _ = textbox(W / 2, 385, "Закон охолодження Ньютона: q_conv = h · (T_s - T_∞), де h залежить від товщини шару δ_t", size=12.5, pad=8, fill="#eef7f0", stroke=COL_FLOW)
    f.append(tb)

    render(os.path.join(IMG, "convection-boundary.svg"), W, H, *f)

# ── Фігура 5: Спектр теплового випромінювання та Закон Стефана-Больцмана ──────
def fig_radiation_spectrum():
    W, H = 880, 440
    f = [text(W / 2, 30, "Спектр випромінювання абсолютно чорного тіла (Закон Планка)", size=16, bold=True)]

    # Осі
    f.append(arrow(80, 350, 820, 350, color=INK, sw=1.8))
    f.append(text(835, 354, "λ (мкм)", size=13, bold=True))

    f.append(arrow(110, 370, 110, 70, color=INK, sw=1.8))
    f.append(text(110, 55, "Спектральна густина I(λ)", size=13, bold=True))

    # Криві для різних температур T
    f.append(path("M 120 345 Q 180 320 240 270 Q 300 310 700 345", stroke=COL_COLD, sw=2))
    f.append(text(280, 265, "3000 K", size=11.5, bold=True, color=COL_COLD))

    f.append(path("M 120 345 Q 170 250 210 180 Q 270 260 720 345", stroke=COL_FLUX, sw=2.2))
    f.append(text(240, 175, "4000 K", size=12, bold=True, color=COL_FLUX))

    f.append(path("M 120 345 Q 150 170 180 90 Q 230 190 750 345", stroke=COL_HOT, sw=2.5))
    f.append(text(205, 85, "5000 K (Сонце ~5800 K)", size=12.5, bold=True, color=COL_HOT))

    # Лінія зміщення Віна
    f.append(path("M 180 90 Q 210 180 240 270", stroke=MUTED, sw=1.5, dash="3,3"))
    f.append(text(260, 120, "Закон зміщення Віна: λ_max · T = const", size=11, italic=True, color=MUTED, anchor="start"))

    # Формула Стефана-Больцмана
    tb, _, _ = textbox(600, 210, "Закон Стефана-Больцмана:\nE_total = ε · σ · T⁴\n\nПовна потужність пропорційна\nЧЕТВЕРТОМУ ступеню температури!", size=12, pad=10, fill="#fdf2e9", stroke=COL_HOT)
    f.append(tb)

    render(os.path.join(IMG, "radiation-spectrum.svg"), W, H, *f)

# ── Фігура 6: Перехідний тепловий процес та температурна провідність ─────────
def fig_transient_diffusivity():
    W, H = 900, 440
    f = [text(W / 2, 30, "Динаміка нагріву тіла: температурна провідність α = k / (ρ · c_p)", size=16, bold=True)]

    # Графік T(t) для двох матеріалів
    f.append(arrow(80, 350, 800, 350, color=INK, sw=1.8))
    f.append(text(815, 354, "Час t (с)", size=13, bold=True))

    f.append(arrow(110, 370, 110, 70, color=INK, sw=1.8))
    f.append(text(110, 55, "Температура T (°C)", size=13, bold=True))

    # Усталена температура T_final
    f.append(line(110, 120, 780, 120, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(790, 124, "T_усталена", size=12, bold=True, color=MUTED, anchor="start"))

    # Матеріал A: Висока α
    f.append(path("M 110 340 Q 180 140 380 125 L 780 120", stroke=COL_HOT, sw=2.5))
    f.append(text(280, 145, "Високий α (Мідь): швидка хвиля нагріву", size=12, bold=True, color=COL_HOT, anchor="start"))

    # Матеріал B: Низька α
    f.append(path("M 110 340 Q 320 330 520 220 T 780 135", stroke=COL_COLD, sw=2.5))
    f.append(text(540, 235, "Низький α (Ізолятор): повільне прогрівання", size=12, bold=True, color=COL_COLD, anchor="start"))

    # Пояснювальна табличка
    tb, _, _ = textbox(W / 2, 395, "Температуропровідність α = k / (ρ·c_p) визначає ШВИДКІСТЬ вирівнювання температури при перехідних процесах", size=12.5, pad=8, fill="#eef7f0", stroke=COL_FLOW)
    f.append(tb)

    render(os.path.join(IMG, "transient-diffusivity.svg"), W, H, *f)

if __name__ == "__main__":
    fig_heat_modes()
    fig_micro_conduction()
    fig_fourier_law()
    fig_convection_boundary()
    fig_radiation_spectrum()
    fig_transient_diffusivity()
    print("Всі фігури згенеровано успішно.")
