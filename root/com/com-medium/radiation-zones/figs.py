# -*- coding: utf-8 -*-
"""Фігури до теми «Ближня і далека зони випромінювання».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_zones_overview():
    """Фігура 1: Три зони електромагнітного поля випромінювача та їх порівняльні характеристики."""
    W, H = 820, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 28, "Структура та зони електромагнітного поля випромінювача", size=16, bold=True))

    # Головна панель
    f.append(rect(20, 48, W - 40, H - 76, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    # Вісь відстані r внизу
    y_axis = 340
    f.append(line(50, y_axis, W - 50, y_axis, color=INK, sw=2))
    f.append(arrow(W - 70, y_axis, W - 45, y_axis, color=INK, sw=2))
    f.append(text(W - 40, y_axis + 5, "r", size=15, bold=True, color=INK, anchor="start", italic=True))

    # Антена / джерело зліва
    cx_ant = 70
    f.append(line(cx_ant, 100, cx_ant, 260, color=POS, sw=4))
    f.append(circle(cx_ant, 180, 8, fill="#fef2f2", stroke=POS, sw=2))
    f.append(text(cx_ant, 280, "Антена (D)", size=12, bold=True, color=POS))

    # Межі зон (вертикальні пунктири)
    x_b1 = 260  # r = λ / (2π)
    x_b2 = 510  # r = 2 D² / λ

    f.append(line(x_b1, 60, x_b1, y_axis, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(x_b2, 60, x_b2, y_axis, color=MUTED, sw=1.5, dash="4,4"))

    # Позначки на осі r
    f.append(circle(x_b1, y_axis, 4, fill=INK, stroke='none'))
    f.append(text(x_b1, y_axis + 22, "r = λ / (2π)", size=12, bold=True, color=INK))

    f.append(circle(x_b2, y_axis, 4, fill=INK, stroke='none'))
    f.append(text(x_b2, y_axis + 22, "r = 2D² / λ", size=12, bold=True, color=INK))

    # Зона 1: Ближня реактивна
    cx1 = (85 + x_b1) / 2
    f.append(rect(85, 65, x_b1 - 95, 250, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=8))
    f.append(text(cx1, 90, "Реактивна ближня зона", size=13, bold=True, color="#1e40af"))
    f.append(text(cx1, 108, "(Зона зв'язаного поля)", size=11, color="#1e3a8a", italic=True))
    f.append(mtext(cx1, 138, [
        "• E і H зсунуті на 90°",
        "• Поля 1/r³ та 1/r²",
        "• Реактивний потік LC",
        "• Z = E/H залежить",
        "  від джерела",
        "• Прив'язане поле"
    ], size=11, color=INK))

    # Зона 2: Проміжна (Френеля)
    cx2 = (x_b1 + x_b2) / 2
    f.append(rect(x_b1 + 10, 65, x_b2 - x_b1 - 20, 250, fill="#fefce8", stroke="#fde047", sw=1.2, rx=8))
    f.append(text(cx2, 90, "Проміжна зона", size=13, bold=True, color="#854d0e"))
    f.append(text(cx2, 108, "(Зона Френеля)", size=11, color="#713f12", italic=True))
    f.append(mtext(cx2, 138, [
        "• Перехід від 1/r²",
        "  до радіаційного 1/r",
        "• Зсув фаз зміщується",
        "• Перебудова ДН",
        "• Спадіння статичних",
        "  складових полів"
    ], size=11, color=INK))

    # Зона 3: Далека (Фраунгофера)
    cx3 = (x_b2 + W - 30) / 2
    f.append(rect(x_b2 + 10, 65, W - x_b2 - 40, 250, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=8))
    f.append(text(cx3, 90, "Далека хвильова зона", size=13, bold=True, color="#166534"))
    f.append(text(cx3, 108, "(Зона Фраунгофера)", size=11, color="#14532d", italic=True))
    f.append(mtext(cx3, 138, [
        "• Поле радіаційне 1/r",
        "• E і H строго у фазі",
        "• Поперечна хвиля TEM",
        "• Z = Z₀ = 377 Ом",
        "• Сформована ДН",
        "• Відрив енергії"
    ], size=11, color=INK))

    return render(os.path.join(IMG, "fig1-zones-overview.svg"), W, H, *f)


def fig_dipole_field_components():
    """Фігура 2: Залежність амплітуд полів 1/r³, 1/r² та 1/r від нормалізованої відстані r/λ."""
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Згасання складових поля елементарного випромінювача", size=16, bold=True))
    f.append(rect(20, 46, W - 40, H - 66, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    ox, oy = 90, 320
    w_graph, h_graph = 440, 240

    f.append(line(ox, oy, ox + w_graph, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - h_graph, color=INK, sw=1.8))
    f.append(arrow(ox + w_graph, oy, ox + w_graph + 20, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy - h_graph, ox, oy - h_graph - 15, color=INK, sw=1.8))

    f.append(text(ox + w_graph + 25, oy + 5, "r / λ", size=13, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - h_graph - 10, "|E|, |H|", size=13, bold=True, anchor="end"))

    x_transition = ox + w_graph * 0.45
    f.append(line(x_transition, oy, x_transition, oy - h_graph, color=MUTED, sw=1.2, dash="3,3"))
    f.append(circle(x_transition, oy, 4, fill=INK, stroke='none'))
    f.append(text(x_transition, oy + 20, "r = λ / (2π)", size=12, bold=True, color="#2563eb"))

    f.append('<path d="M %f,%f Q %f,%f %f,%f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ox + 20, oy - 220, ox + 100, oy - 120, ox + 380, oy - 10, POS))
    f.append(text(ox + 70, oy - 200, "1 / r³ (статичне)", size=12, bold=True, color=POS))

    f.append('<path d="M %f,%f Q %f,%f %f,%f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ox + 20, oy - 170, ox + 150, oy - 110, ox + 400, oy - 45, "#d97706"))
    f.append(text(ox + 160, oy - 145, "1 / r² (індукційне)", size=12, bold=True, color="#d97706"))

    f.append('<path d="M %f,%f Q %f,%f %f,%f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ox + 20, oy - 105, ox + 180, oy - 80, ox + 420, oy - 60, FIELD))
    f.append(text(ox + 320, oy - 80, "1 / r (радіаційне)", size=12, bold=True, color=FIELD))

    y_intersect = oy - 95
    f.append(circle(x_transition, y_intersect, 6, fill="#2563eb", stroke="#ffffff", sw=1.5))

    tb, _, _ = textbox(620, 170,
                       "Співвідношення складових:\n\n• r ≪ λ/(2π):\n  Домінує 1/r³ (ближня зона)\n\n• r = λ/(2π):\n  Амплітуди 1/r³ та 1/r рівні\n\n• r ≫ λ/(2π):\n  Домінує 1/r (далека зона)",
                       size=11, pad=10, fill="#ffffff", stroke="#cbd5e1", sw=1.2)
    f.append(tb)

    return render(os.path.join(IMG, "fig2-dipole-field-components.svg"), W, H, *f)


def fig_phase_wave_impedance():
    """Фігура 3: Хвильовий опір полів Z = E/H залежно від відстані для електричного та магнітного джерел."""
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Хвильовий опір випромінювання Z = E / H у ближній та далекій зонах", size=16, bold=True))
    f.append(rect(20, 46, W - 40, H - 66, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    ox, oy = 100, 300
    w_graph, h_graph = 430, 220

    f.append(line(ox, oy, ox + w_graph, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - h_graph, color=INK, sw=1.8))
    f.append(arrow(ox + w_graph, oy, ox + w_graph + 20, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy - h_graph, ox, oy - h_graph - 15, color=INK, sw=1.8))

    f.append(text(ox + w_graph + 25, oy + 5, "r / (λ / 2π)", size=13, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - h_graph - 10, "Z = E / H (Ом)", size=13, bold=True, anchor="end"))

    y_z0 = oy - h_graph / 2
    f.append(line(ox, y_z0, ox + w_graph + 10, y_z0, color="#166534", sw=1.8, dash="5,5"))
    f.append(text(ox - 10, y_z0 + 4, "Z₀ = 377 Ом", size=12, bold=True, color="#166534", anchor="end"))

    f.append('<path d="M %f,%f Q %f,%f %f,%f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ox + 15, oy - 200, ox + 100, oy - y_z0 + 20, ox + w_graph, y_z0, POS))
    f.append(text(ox + 40, oy - 190, "Електричний диполь (Z ≫ Z₀)", size=12, bold=True, color=POS))

    f.append('<path d="M %f,%f Q %f,%f %f,%f" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ox + 15, oy - 15, ox + 100, oy - y_z0 - 20, ox + w_graph, y_z0, NEG))
    f.append(text(ox + 40, oy - 25, "Магнітна рамка (Z ≪ Z₀)", size=12, bold=True, color=NEG))

    x_one = ox + 120
    f.append(line(x_one, oy, x_one, oy - h_graph, color=MUTED, sw=1.2, dash="3,3"))
    f.append(circle(x_one, oy, 4, fill=INK, stroke='none'))
    f.append(text(x_one, oy + 20, "1.0 (Ближня межа)", size=11, color=MUTED))

    tb, _, _ = textbox(620, 160,
                       "Властивості хвильового опору:\n\n• Електричне джерело:\n  E-поле переважає в ближній зоні\n  High Impedance Field\n\n• Магнітне джерело:\n  H-поле переважає в ближній зоні\n  Low Impedance Field\n\n• Далека зона:\n  Z → Z₀ = √(μ₀/ε₀) ≈ 377 Ом",
                       size=11, pad=10, fill="#ffffff", stroke="#cbd5e1", sw=1.2)
    f.append(tb)

    return render(os.path.join(IMG, "fig3-phase-wave-impedance.svg"), W, H, *f)


def fig_fraunhofer_phase_error():
    """Фігура 4: Геометрія апертури D та визначення межі Фраунгофера r = 2D²/λ за фазовою похибкою π/8."""
    W, H = 780, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Геометрія фазового фронту апертурної антени та межа Фраунгофера", size=16, bold=True))
    f.append(rect(20, 46, W - 40, H - 66, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=10))

    x_ant = 80
    y_center = 190
    d_half = 100

    y_top = y_center - d_half
    y_bot = y_center + d_half

    f.append(line(x_ant, y_top, x_ant, y_bot, color=POS, sw=3.5))
    f.append(circle(x_ant, y_top, 5, fill=POS, stroke='none'))
    f.append(circle(x_ant, y_bot, 5, fill=POS, stroke='none'))
    f.append(circle(x_ant, y_center, 4, fill=INK, stroke='none'))

    f.append(line(x_ant - 20, y_top, x_ant - 20, y_bot, color=MUTED, sw=1))
    f.append(arrow(x_ant - 20, y_center - 20, x_ant - 20, y_top, color=MUTED, sw=1.2))
    f.append(arrow(x_ant - 20, y_center + 20, x_ant - 20, y_bot, color=MUTED, sw=1.2))
    f.append(text(x_ant - 35, y_center + 4, "D", size=14, bold=True, color=POS, italic=True))

    px = 580
    py = y_center
    f.append(circle(px, py, 6, fill=INK, stroke='none'))
    f.append(text(px + 15, py + 4, "Точка P(r)", size=13, bold=True, anchor="start"))

    f.append(arrow(x_ant, y_center, px, py, color=INK, sw=2))
    f.append(text((x_ant + px) / 2, y_center - 10, "r (центральний промінь)", size=12, bold=True, color=INK))

    f.append(line(x_ant, y_top, px, py, color="#2563eb", sw=1.8, dash="4,4"))
    f.append(text((x_ant + px) / 2 + 20, (y_top + py) / 2 - 12, "r' = √(r² + (D/2)²)", size=11, bold=True, color="#2563eb"))

    f.append('<path d="M %f,%f A %d,%d 0 0,1 %f,%f" fill="none" stroke="#059669" stroke-width="2" stroke-dasharray="3,3"/>' %
             (x_ant + 280, y_center - d_half + 10, 300, 300, x_ant + 280, y_center + d_half - 10))
    f.append(text(x_ant + 295, y_center + 60, "Сферичний фронт хвилі", size=11, color="#059669"))

    tb, _, _ = textbox(440, 300,
                       "Критерій квазіплоского фронту:\n• Різниця ходу: Δr ≈ D² / (8r)\n• Похибка фази: Δφ = k·Δr = (2π/λ)·(D²/8r) ≤ π/8 (22.5°)\n• Звідси межа Фраунгофера: r ≥ 2D² / λ",
                       size=11, pad=10, fill="#ffffff", stroke="#93c5fd", sw=1.2)
    f.append(tb)

    return render(os.path.join(IMG, "fig4-fraunhofer-phase-error.svg"), W, H, *f)


if __name__ == "__main__":
    fig_zones_overview()
    fig_dipole_field_components()
    fig_phase_wave_impedance()
    fig_fraunhofer_phase_error()
    print("Всі фігури згенеровано успішно в ./img/")
