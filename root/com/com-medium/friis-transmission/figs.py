# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path_el(d, fill="none", stroke=LINE, sw=1.5, stroke_dasharray=None):
    sd = f' stroke-dasharray="{stroke_dasharray}"' if stroke_dasharray else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{sd}/>'


# ── Фігура 1: Геометрія передачі електромагнітної хвилі за Рівнянням Фріїса ───────

def fig_geometry():
    W, H = 800, 320
    p = []

    # Передавач (ліворуч)
    p.append(rect(40, 100, 110, 80, fill="#e6f2ff", stroke="#0066cc", sw=1.8, rx=6))
    p.append(text(95, 130, "Передавач", size=13, color="#0066cc", bold=True))
    p.append(text(95, 152, "Pₜ (Вт)", size=12, color=INK))

    # Передавальна антена (трикутник/рупор)
    p.append(path_el("M 150,140 L 190,110 L 190,170 Z", fill="#d9e6f2", stroke="#004080", sw=1.5))
    p.append(text(170, 95, "Tx антена", size=11, color=MUTED, bold=True))
    p.append(text(170, 190, "Підсилення Gₜ", size=12, color=POS, bold=True))

    # Сферична хвиля / простір розповсюдження
    # Напрямні промені
    p.append(line(190, 140, 610, 80, color="#b3cde0", sw=1.2, dash="4 4"))
    p.append(line(190, 140, 610, 200, color="#b3cde0", sw=1.2, dash="4 4"))
    
    # Фронт хвилі
    p.append(path_el("M 400,105 A 220,220 0 0 1 400,175", fill="none", stroke="#3385ff", sw=2))
    p.append(path_el("M 580,85 A 400,400 0 0 1 580,195", fill="none", stroke="#0052cc", sw=2.2))

    # Текст про густину потужності вгорі (поза променями)
    b_dens = fitbox(395, 52, 230, 40,
                    "Густина потужності: S = (Pₜ · Gₜ) / (4 · π · d²)",
                    size=11, color=INK, fill="#f0f7ff", stroke="#b3cde0", rx=4)
    p.append(b_dens)

    # Лінія відстані d
    p.append(line(190, 230, 610, 230, color=INK, sw=1.5))
    p.append(arrow(210, 230, 190, 230, color=INK, sw=1.5))
    p.append(arrow(590, 230, 610, 230, color=INK, sw=1.5))
    p.append(text(400, 248, "Відстань d (м)", size=12, color=INK, bold=True))

    # Приймальна антена (праворуч)
    p.append(path_el("M 610,110 L 610,170 L 650,140 Z", fill="#d9e6f2", stroke="#004080", sw=1.5))
    p.append(text(630, 95, "Rx антена", size=11, color=MUTED, bold=True))
    p.append(text(630, 190, "Підсилення Gᵣ", size=12, color=POS, bold=True))

    # Приймач
    p.append(rect(650, 100, 110, 80, fill="#e6ffe6", stroke="#009933", sw=1.8, rx=6))
    p.append(text(705, 130, "Приймач", size=13, color="#009933", bold=True))
    p.append(text(705, 152, "Pᵣ = S · Aₑ", size=12, color=INK, bold=True))

    # Нижня підсумкова формульна рамка
    b = fitbox(160, 265, 480, 44,
               "Рівняння Фріїса:  Pᵣ = Pₜ · Gₜ · Gᵣ · ( λ / (4·π·d) )²",
               size=13, color="#004080", fill="#f0f5fa", stroke="#99c2ff")
    p.append(b)

    render(os.path.join(OUT, "friis-geometry.svg"), W, H, *p,
           title="Геометрія передачі електромагнітної хвилі за Рівнянням Фріїса")


# ── Фігура 2: Межі застосовності Рівняння Фріїса (Дальня зона Фраунгофера) ─────────

def fig_far_field():
    W, H = 800, 320
    p = []

    # Ліва вісь / антена розміром D
    p.append(rect(30, 80, 20, 140, fill="#d9d9d9", stroke="#595959", sw=1.5, rx=3))
    p.append(line(40, 50, 40, 80, color=MUTED, sw=1))
    p.append(line(40, 220, 40, 250, color=MUTED, sw=1))
    p.append(arrow(40, 65, 40, 50, color=MUTED, sw=1))
    p.append(arrow(40, 235, 40, 250, color=MUTED, sw=1))
    p.append(text(40, 38, "Апертура D", size=12, color=INK, bold=True))

    # Вісь відстані
    p.append(line(50, 150, 760, 150, color=INK, sw=1.8))
    p.append(arrow(740, 150, 760, 150, color=INK, sw=1.8))
    p.append(text(745, 170, "d", size=13, color=INK, bold=True))

    # Кордони зон
    x1 = 200  # межа реактивної зони
    x2 = 440  # межа дальньої зони (Fraunhofer)

    p.append(line(x1, 70, x1, 230, color="#cc0000", sw=1.5, dash="4 4"))
    p.append(line(x2, 70, x2, 230, color="#008000", sw=2, dash="5 5"))

    # Зона 1: Реактивна ближня
    p.append(rect(55, 75, x1 - 60, 65, fill="#ffe6e6", stroke="none"))
    p.append(text((55 + x1) / 2, 95, "Реактивна ближня", size=11, color="#990000", bold=True))
    p.append(text((55 + x1) / 2, 115, "d < 0.62·√(D³/λ)", size=10, color=MUTED))

    # Зона 2: Ближня зона Френеля
    p.append(rect(x1 + 5, 75, x2 - x1 - 10, 65, fill="#fff7e6", stroke="none"))
    p.append(text((x1 + x2) / 2, 95, "Радіаційна Френеля", size=11, color="#b37700", bold=True))
    p.append(text((x1 + x2) / 2, 115, "0.62·√(D³/λ) ≤ d < 2·D²/λ", size=10, color=MUTED))

    # Зона 3: Дальня зона Фраунгофера
    p.append(rect(x2 + 5, 75, 730 - x2, 65, fill="#e6ffe6", stroke="none"))
    p.append(text((x2 + 735) / 2, 95, "Дальня зона Фраунгофера", size=12, color="#006600", bold=True))
    p.append(text((x2 + 735) / 2, 115, "d ≥ 2·D² / λ", size=11, color="#008000", bold=True))

    # Позначення межі Фраунгофера
    p.append(text(x2, 248, "d_far = 2·D² / λ", size=12, color="#008000", bold=True))

    # Інформаційна рамка піднизу
    b = fitbox(100, 260, 600, 48,
               "Рівняння Фріїса ДІЙСНЕ ТІЛЬКИ у дальній зоні (d ≥ d_far)!\n"
               "У ближній зоні хвильовий фронт викривлений, і формула дає помилкові результати.",
               size=12, color=INK, fill="#f9f9f9", stroke="#cccccc")
    p.append(b)

    render(os.path.join(OUT, "far-field-boundary.svg"), W, H, *p,
           title="Зони випромінювання антени та межа застосовності рівняння Фріїса")


# ── Фігура 3: Бюджет радіолінії за рівнянням Фріїса у децибелах ───────────────────

def fig_decibel_budget():
    W, H = 800, 340
    p = []

    x0, y0 = 70, 260
    def to_y(val):
        return y0 - (val - (-100)) * 1.5

    p.append(line(x0, 40, x0, y0 + 20, color=INK, sw=1.5))
    p.append(arrow(x0, 40, x0, 25, color=INK, sw=1.5))
    p.append(text(x0 - 15, 30, "дБм", size=12, color=INK, bold=True))

    # Поділки осі Y
    for dbm in [30, 0, -30, -60, -90]:
        y = to_y(dbm)
        p.append(line(x0 - 5, y, x0 + 5, y, color=MUTED, sw=1))
        p.append(text(x0 - 25, y + 4, f"{dbm:+d}", size=10, color=MUTED))
        p.append(line(x0 + 5, y, 750, y, color="#ebebeb", sw=1, dash="2 2"))

    # Стовпчики бюджету (каскад)
    x1, w1 = 110, 85
    y_pt = to_y(20)
    p.append(rect(x1, y_pt, w1, y0 - y_pt, fill="#cce6ff", stroke="#0066cc", sw=1.5, rx=3))
    p.append(text(x1 + w1/2, y_pt - 10, "+20 дБм", size=11, color="#0066cc", bold=True))
    p.append(text(x1 + w1/2, y0 - 15, "Pₜ (100 мВт)", size=10, color=INK))

    x2, w2 = 220, 85
    y_eirp = to_y(30)
    p.append(rect(x2, y_eirp, w2, y0 - y_eirp, fill="#b3daff", stroke="#004080", sw=1.5, rx=3))
    p.append(text(x2 + w2/2, y_eirp - 10, "+30 дБм", size=11, color="#004080", bold=True))
    p.append(text(x2 + w2/2, y0 - 15, "EIRP (+10 dBi)", size=10, color=INK))

    x3, w3 = 340, 85
    y_fspl = to_y(-70)
    p.append(rect(x3, y_eirp, w3, y_fspl - y_eirp, fill="#ffe6e6", stroke="#cc0000", sw=1.5, rx=3))
    p.append(text(x3 + w3/2, (y_eirp + y_fspl)/2, "−100 дБ", size=11, color="#cc0000", bold=True))
    p.append(text(x3 + w3/2, y0 - 15, "Втрати FSPL", size=10, color=INK))

    x4, w4 = 460, 85
    y_pr = to_y(-64)
    p.append(rect(x4, y_pr, w4, y0 - y_pr, fill="#d9f2e6", stroke="#00994d", sw=1.5, rx=3))
    p.append(text(x4 + w4/2, y_pr - 10, "−64 дБм", size=11, color="#00994d", bold=True))
    p.append(text(x4 + w4/2, y0 - 15, "+Gᵣ (+6 dBi)", size=10, color=INK))

    x5, w5 = 580, 80
    y_rx = to_y(-67)
    p.append(rect(x5, y_rx, w5, y0 - y_rx, fill="#e6ffe6", stroke="#008000", sw=1.5, rx=3))
    p.append(text(x5 + w5/2, y_rx - 10, "−67 дБм", size=11, color="#008000", bold=True))
    p.append(text(x5 + w5/2, y0 - 15, "Сигнал Pᵣₓ", size=10, color=INK))

    # Лінія чутливості приймача S_rx = -95 dBm (зупиняємо перед вертикальним стрілочним підписом)
    y_sens = to_y(-95)
    p.append(line(x0 + 10, y_sens, 660, y_sens, color="#990000", sw=1.8, dash="6 3"))
    p.append(text(570, y_sens + 14, "Чутливість Sᵣₓ = −95 дБм", size=11, color="#990000", bold=True))

    # Запас лінка (Link Margin = 28 dB) у прямокутній рамці fitbox праворуч
    p.append(line(675, y_rx, 675, y_sens, color=POS, sw=1.5))
    p.append(arrow(675, y_rx + 15, 675, y_rx, color=POS, sw=1.5))
    p.append(arrow(675, y_sens - 15, 675, y_sens, color=POS, sw=1.5))

    b_margin = fitbox(685, (y_rx + y_sens)/2 - 12, 105, 30,
                      "Запас +28 дБ", size=11, color=POS, fill="#fff0f0", stroke=POS, bold=True)
    p.append(b_margin)

    render(os.path.join(OUT, "friis-decibel-budget.svg"), W, H, *p,
           title="Бюджет потужності радіолінії за рівнянням Фріїса")


if __name__ == "__main__":
    fig_geometry()
    fig_far_field()
    fig_decibel_budget()
    print("Figures generated successfully!")
