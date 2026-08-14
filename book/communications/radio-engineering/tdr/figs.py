# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def render(w, h, elements):
    """Скласти підсумковий SVG-документ з оголошенням стрілок та стилів."""
    defs = '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
    <marker id="arrow-pos" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
    <marker id="arrow-neg" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
  </defs>''' % (INK, POS, NEG)
    body = "\n  ".join(elements)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  %s\n  %s\n</svg>' % (w, h, w, h, defs, body))

def save_svg(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Збережено: %s" % path)

# ── Фігура 1: Принцип роботи часового рефлектометра ─────────────────────────
def fig_tdr_principle():
    W, H = 820, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    # Схема приладу
    p.append(rect(20, 20, 240, 320, fill="#f0f4f8", stroke=LINE, sw=1.5, rx=8))
    p.append(text(140, 45, "Часовий рефлектометр (TDR)", size=14, color=INK, bold=True))

    p.append(textbox(140, 95, "Генератор надшвидкого\nперепаду напруги (Step Gen)\nt_r < 30 пс", size=12, fill="#ffffff", stroke=POS, min_w=200)[0])
    p.append(textbox(140, 185, "Швидкісний самплер /\nОсцилограф (Sampler)", size=12, fill="#ffffff", stroke=NEG, min_w=200)[0])
    p.append(textbox(140, 275, "Трійник / Мостовий\nдетектувальний вузол", size=12, fill="#ffffff", stroke=FIELD, min_w=200)[0])

    # З'єднання всередині TDR
    p.append(arrow(140, 125, 140, 155, color=POS, sw=2))
    p.append(arrow(140, 215, 140, 245, color=NEG, sw=2))

    # Вихідний кабель
    p.append(line(240, 275, 310, 275, color=INK, sw=3))
    p.append(text(275, 260, "Z₀ = 50 Ом", size=11, color=MUTED))

    # Лінія передачі (тестований кабель / доріжка)
    p.append(rect(310, 240, 470, 70, fill="#eef6fc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(545, 260, "Досліджувана лінія передачі (довжина L, ε_r)", size=13, color=NEG, bold=True))

    # Падаюча та відбита хвилі в кабелі
    p.append(arrow(330, 280, 490, 280, color=POS, sw=2.5))
    p.append(text(410, 298, "Падаючий перепад V_inc", size=11, color=POS, bold=True))

    p.append(arrow(670, 298, 510, 298, color=FIELD, sw=2.5))
    p.append(text(590, 283, "Відбитий сигнал V_refl", size=11, color=FIELD, bold=True))

    # Неоднорідність на кінці / у середині
    p.append(line(680, 240, 680, 310, color=POS, sw=3, dash="4,4"))
    p.append(textbox(680, 195, "Неоднорідність імпедансу Z_L\n(дефект, роз'єм, обрив, КЗ)\nу точці x = v·Δt / 2", size=11, fill="#fff0f0", stroke=POS, min_w=190)[0])
    p.append(arrow(680, 215, 680, 235, color=POS, sw=1.5))

    # Екран осцилограми (верхня права частина)
    p.append(rect(310, 20, 470, 150, fill="#1e2530", stroke=LINE, sw=1.5, rx=6))
    p.append(text(545, 40, "Рефлектограма на екрані осцилографа: V(t)", size=13, color="#ffffff", bold=True))

    # Вісі екрана
    p.append(arrow(340, 140, 760, 140, color="#8a99ad", sw=1.5))
    p.append(text(765, 144, "t", size=12, color="#8a99ad"))
    p.append(arrow(340, 140, 340, 45, color="#8a99ad", sw=1.5))
    p.append(text(332, 45, "V", size=12, color="#8a99ad"))

    # Сигнал на екрані
    pts = "340,120 370,120 380,80 540,80 550,50 740,50"
    p.append('<polyline points="%s" fill="none" stroke="#00ffcc" stroke-width="2.5"/>' % pts)

    # Позначки часу t=0 та t=Δt
    p.append(line(375, 140, 375, 75, color="#ffcc00", sw=1, dash="2,2"))
    p.append(text(375, 153, "t=0", size=10, color="#ffcc00"))
    p.append(line(545, 140, 545, 55, color="#ffcc00", sw=1, dash="2,2"))
    p.append(text(545, 153, "t = Δt", size=10, color="#ffcc00"))

    # Позначка Δt
    p.append(line(375, 132, 545, 132, color="#ffcc00", sw=1))
    p.append(text(460, 126, "Затримка Δt", size=10, color="#ffcc00"))

    save_svg("tdr-principle.svg", render(W, H, p))

# ── Фігура 2: Форми відбитого сигналу для різних навантажень ───────────────
def fig_discontinuity_waveforms():
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(W/2, 25, "Характерні рефлектограми TDR для різних неоднорідностей", size=15, color=INK, bold=True))

    cases = [
        ("Обрив (Open): Z_L = ∞", "Γ = +1 (напруга подвоюється)", "30,50", [
            ("0,40", "30,40", "35,20", "70,20", "75,0", "150,0")
        ], POS),
        ("Коротке замикання (Short): Z_L = 0", "Γ = -1 (напруга падає до 0)", "30,250", [
            ("0,40", "30,40", "35,20", "70,20", "75,40", "150,40")
        ], NEG),
        ("Більший опір: Z_L > Z_0", "0 < Γ < 1 (позитивний стрибок)", "310,50", [
            ("0,40", "30,40", "35,20", "70,20", "75,10", "150,10")
        ], POS),
        ("Менший опір: Z_L < Z_0", "-1 < Γ < 0 (негативний стрибок)", "310,250", [
            ("0,40", "30,40", "35,20", "70,20", "75,30", "150,30")
        ], NEG),
        ("Послідовна індуктивність L", "Сплеск та експоненціальний спад", "590,50", [
            ("0,40", "30,40", "35,20", "70,20", "72,0", "77,10", "90,18", "150,20")
        ], FIELD),
        ("Паралельна ємність C", "Провал та експоненціальне відновлення", "590,250", [
            ("0,40", "30,40", "35,20", "70,20", "72,40", "77,30", "90,22", "150,20")
        ], FIELD),
    ]

    for title, formula, pos, lines, color in cases:
        x0, y0 = map(int, pos.split(","))
        p.append(rect(x0, y0, 230, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        p.append(text(x0 + 115, y0 + 22, title, size=12, color=INK, bold=True))
        p.append(text(x0 + 115, y0 + 38, formula, size=10, color=MUTED))

        ox, oy = x0 + 30, y0 + 145
        p.append(arrow(ox, oy, ox + 180, oy, color=MUTED, sw=1))
        p.append(arrow(ox, oy, ox, y0 + 55, color=MUTED, sw=1))
        p.append(text(ox + 185, oy + 4, "t", size=10, color=MUTED))
        p.append(text(ox - 8, y0 + 55, "V", size=10, color=MUTED))

        p.append(line(ox, oy - 35, ox + 175, oy - 35, color="#d0d5dd", sw=1, dash="3,3"))
        p.append(text(ox - 15, oy - 33, "V_inc", size=9, color=MUTED))

        poly_pts = []
        for pt in lines[0]:
            px, py = map(int, pt.split(","))
            poly_pts.append("%.1f,%.1f" % (ox + px, oy - 75 + py))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(poly_pts), color))

    save_svg("discontinuity-waveforms.svg", render(W, H, p))

# ── Фігура 3: Просторова роздільна здатність і тривалість фронту ───────────
def fig_spatial_resolution():
    W, H = 780, 330
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(W/2, 25, "Вплив тривалості фронту перепаду (t_r) на просторову роздільну здатність", size=14, color=INK, bold=True))

    # Ліва частина
    p.append(rect(30, 50, 340, 250, fill="#fff8f8", stroke=POS, sw=1.2, rx=8))
    p.append(text(200, 75, "Повільний фронт імпульсу (t_r = 1 нс)", size=13, color=POS, bold=True))
    p.append(text(200, 95, "Роздільна здатність Δx_min ≈ 10 см", size=11, color=MUTED))

    # Осі без перетину старту в ту саму точку
    p.append(line(60, 240, 335, 240, color=MUTED, sw=1.2))
    p.append(arrow(335, 240, 345, 240, color=MUTED, sw=1.2))
    p.append(arrow(60, 240, 60, 115, color=MUTED, sw=1.2))
    p.append(text(355, 244, "t", size=11, color=MUTED))

    pts_slow = "60,200 120,200 150,215 180,215 210,170 320,170"
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_slow, POS))
    p.append(textbox(200, 275, "Дві неоднорідності ЗЛИЛИСЯ у широкий провал\nНеможливо розрізнити деталі плати", size=10, fill="#ffffff", stroke=POS, min_w=280)[0])

    # Права частина
    p.append(rect(410, 50, 340, 250, fill="#f2fdf5", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(580, 75, "Пікосекундний фронт (t_r = 20 пс)", size=13, color=FIELD, bold=True))
    p.append(text(580, 95, "Роздільна здатність Δx_min ≈ 2 мм", size=11, color=MUTED))

    p.append(line(440, 240, 715, 240, color=MUTED, sw=1.2))
    p.append(arrow(715, 240, 725, 240, color=MUTED, sw=1.2))
    p.append(arrow(440, 240, 440, 115, color=MUTED, sw=1.2))
    p.append(text(735, 244, "t", size=11, color=MUTED))

    pts_fast = "440,200 490,200 500,225 515,225 525,200 550,200 560,230 575,230 585,170 700,170"
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts_fast, FIELD))
    p.append(textbox(580, 275, "ЧІТКО РОЗРІЗНЕНІ два піки: контакт ВЧ-роз'єму\nта перехідний отвір (Via) на платі", size=10, fill="#ffffff", stroke=FIELD, min_w=280)[0])

    save_svg("spatial-resolution.svg", render(W, H, p))

# ── Фігура 4: Диференційне TDR вимірювання ─────────────────────────────────
def fig_differential_tdr():
    W, H = 760, 320
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(W/2, 25, "Диференційна часова рефлектометрія (Differential TDR)", size=14, color=INK, bold=True))

    p.append(rect(30, 50, 330, 240, fill="#f5f8ff", stroke=NEG, sw=1.2, rx=8))
    p.append(text(195, 75, "Непарна мода (Odd Mode / Diff)", size=13, color=NEG, bold=True))
    p.append(textbox(195, 115, "Сигнали протифазні: +V/2 та -V/2\nZ_diff = 2 · Z_odd", size=11, fill="#ffffff", stroke=NEG, min_w=240)[0])

    p.append(line(60, 170, 330, 170, color=POS, sw=2))
    p.append(text(50, 173, "+V", size=11, color=POS, bold=True))
    p.append(arrow(100, 160, 290, 160, color=POS, sw=2))

    p.append(line(60, 210, 330, 210, color=NEG, sw=2))
    p.append(text(50, 213, "-V", size=11, color=NEG, bold=True))
    p.append(arrow(290, 220, 100, 220, color=NEG, sw=2))

    p.append(text(195, 250, "Вимірювання диф. імпедансу USB/PCIe", size=11, color=MUTED))

    p.append(rect(400, 50, 330, 240, fill="#fdf8ff", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(565, 75, "Парна мода (Even Mode / Comm)", size=13, color=FIELD, bold=True))
    p.append(textbox(565, 115, "Сигнали синфазні: +V/2 та +V/2\nZ_comm = Z_even / 2", size=11, fill="#ffffff", stroke=FIELD, min_w=240)[0])

    p.append(line(430, 170, 700, 170, color=POS, sw=2))
    p.append(text(420, 173, "+V", size=11, color=POS, bold=True))
    p.append(arrow(470, 160, 660, 160, color=POS, sw=2))

    p.append(line(430, 210, 700, 210, color=POS, sw=2))
    p.append(text(420, 213, "+V", size=11, color=POS, bold=True))
    p.append(arrow(470, 200, 660, 200, color=POS, sw=2))

    p.append(text(565, 250, "Оцінка синфазних наводок і симетрії", size=11, color=MUTED))

    save_svg("differential-tdr.svg", render(W, H, p))

if __name__ == "__main__":
    fig_tdr_principle()
    fig_discontinuity_waveforms()
    fig_spatial_resolution()
    fig_differential_tdr()
