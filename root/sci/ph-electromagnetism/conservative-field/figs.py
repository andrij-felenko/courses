# -*- coding: utf-8 -*-
"""Фігури до теми «Потенціальне поле й циркуляція».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path_tag(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{dash_attr}/>'

# ── Фігура 1: Незалежність роботи від шляху в потенціальному полі ───────────
def fig_path_independence():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Незалежність роботи від траєкторії в потенціальному полі", size=16, bold=True))

    # Рамка фону силового поля
    f.append(rect(20, 48, W - 40, H - 74, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=12))

    # Світлі фонові силові лінії поля E (слабо викривлені для наочності)
    for y_start in range(80, H - 60, 45):
        f.append(path_tag(f"M 30 {y_start} Q 360 {y_start - 15} 690 {y_start + 10}", stroke="#e2e8f0", sw=1.2, fill="none", dash="4,4"))

    ax, ay = 120, 220
    bx, by = 600, 160

    # Траєкторія 1 (верхня)
    f.append(path_tag(f"M {ax} {ay} C 240 80, 480 90, {bx} {by}", stroke=POS, sw=2.5, fill="none"))
    # Стрілка напрямку на L1
    f.append(arrow(340, 102, 360, 104, color=POS, sw=2.5))
    f.append(text(350, 84, "Траєкторія L₁", size=14, bold=True, color=POS))
    f.append(text(350, 68, "робота W₁", size=12, color=POS))

    # Траєкторія 2 (нижня)
    f.append(path_tag(f"M {ax} {ay} C 220 320, 460 310, {bx} {by}", stroke=NEG, sw=2.5, fill="none"))
    # Стрілка напрямку на L2
    f.append(arrow(340, 292, 360, 290, color=NEG, sw=2.5))
    f.append(text(350, 316, "Траєкторія L₂", size=14, bold=True, color=NEG))
    f.append(text(350, 332, "робота W₂", size=12, color=NEG))

    # Точка A
    f.append(circle(ax, ay, 8, fill=INK, stroke=INK, sw=1))
    f.append(text(ax - 20, ay + 6, "A", size=16, bold=True, color=INK, anchor="end"))
    f.append(text(ax - 20, ay + 24, "початкова точка", size=11, color=MUTED, anchor="end"))

    # Точка B
    f.append(circle(bx, by, 8, fill=INK, stroke=INK, sw=1))
    f.append(text(bx + 20, by + 6, "B", size=16, bold=True, color=INK, anchor="start"))
    f.append(text(bx + 20, by + 24, "кінцева точка", size=11, color=MUTED, anchor="start"))

    # Нижній плашка-висновок
    b, w, h = textbox(W / 2, H - 22, "W₁ = W₂   ⇒   ∮ E · dl = 0   (циркуляція по замкненому контуру дорівнює нулю)", size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "path-independence.svg"), W, H, *f)


# ── Фігура 2: Теорема Стокса — розбиття контуру на мікропетлі ─────────────
def fig_circulation_micro_loop():
    W, H = 700, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Теорема Стокса: циркуляція як сума локальних вихорів", size=16, bold=True))

    # Зовнішній контур C
    cx, cy = 350, 190
    rx_c, ry_c = 260, 120

    # Підкладка поверхні S
    f.append(path_tag(f"M {cx-rx_c} {cy} C {cx-rx_c} {cy-ry_c}, {cx+rx_c} {cy-ry_c}, {cx+rx_c} {cy} C {cx+rx_c} {cy+ry_c}, {cx-rx_c} {cy+ry_c}, {cx-rx_c} {cy}", fill="#f4f7fb", stroke=LINE, sw=2.2))

    # Сітка внутрішніх комірок (мікроконтурів)
    gx0, gy0 = cx - 180, cy - 80
    cell_w, cell_h = 60, 40
    cols, rows = 6, 4

    for r in range(rows):
        for c in range(cols):
            x = gx0 + c * cell_w
            y = gy0 + r * cell_h
            f.append(rect(x, y, cell_w, cell_h, fill="none", stroke="#cbd5e1", sw=1.2))
            # Маленькі колові стрілки всередині комірок (напрямок обходу)
            f.append(path_tag(f"M {x+12} {y+cell_h/2} A 12 12 0 1 1 {x+cell_w-12} {y+cell_h/2}", fill="none", stroke=POS, sw=1.2))
            f.append(arrow(x+cell_w-12, y+cell_h/2, x+cell_w-12, y+cell_h/2+4, color=POS, sw=1.2))

    # Пояснення взаємного знищення внутрішніх ребер
    f.append(line(gx0 + 2*cell_w, gy0 + cell_h, gx0 + 2*cell_w, gy0 + 2*cell_h, color=NEG, sw=2.8))
    f.append(arrow(gx0 + 2*cell_w - 2, gy0 + cell_h + 10, gx0 + 2*cell_w - 2, gy0 + 2*cell_h - 10, color=NEG, sw=1.8))
    f.append(arrow(gx0 + 2*cell_w + 2, gy0 + 2*cell_h - 10, gx0 + 2*cell_w + 2, gy0 + cell_h + 10, color=POS, sw=1.8))

    # Зовнішній контур C зі стрілками
    f.append(path_tag(f"M {cx-rx_c} {cy} C {cx-rx_c} {cy-ry_c}, {cx+rx_c} {cy-ry_c}, {cx+rx_c} {cy}", fill="none", stroke=FIELD, sw=2.8))
    f.append(path_tag(f"M {cx+rx_c} {cy} C {cx+rx_c} {cy+ry_c}, {cx-rx_c} {cy+ry_c}, {cx-rx_c} {cy}", fill="none", stroke=FIELD, sw=2.8))
    f.append(arrow(cx, cy - ry_c, cx + 20, cy - ry_c, color=FIELD, sw=3.0))

    f.append(text(cx, cy - ry_c - 14, "Зовнішній контур C", size=14, bold=True, color=FIELD))
    f.append(text(cx, cy + 8, "Поверхня S", size=13, bold=True, color=MUTED))

    # Виносний підпис про скасування суміжних ребер
    b_cancel, w_c, h_c = textbox(gx0 + 5*cell_w + 50, cy + 30, "Внутрішні суміжні ребра\nобходяться в протилежних\nнапрямках і взаємно знищуються!", size=11, pad=6, fill="#fff5f5", stroke=NEG, sw=1.2)
    f.append(b_cancel)

    # Підсумкова плашка
    b, w, h = textbox(W / 2, H - 20, "∮ [C] E · dl = ∬ [S] (∇ × E) · dS   (сума циркуляцій мікроелементів)", size=13, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "circulation-micro-loop.svg"), W, H, *f)


# ── Фігура 3: Еквіпотенціальні поверхні та лінії напруженості ───────────────
def fig_potential_surfaces():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Еквіпотенціальні поверхні та вектори напруженості E = −∇φ", size=16, bold=True))

    # Центр точкового позитивного заряду
    q_x, q_y = 200, 195
    f.append(circle(q_x, q_y, 20, fill="#ffebee", stroke=POS, sw=2.5))
    f.append(text(q_x, q_y + 6, "+Q", size=15, bold=True, color=POS))

    # Еквіпотенціальні кола φ1, φ2, φ3
    radii = [45, 85, 125, 160]
    potentials = ["φ₁ = 100 В", "φ₂ = 50 В", "φ₃ = 33 В", "φ₄ = 25 В"]
    for i, r in enumerate(radii):
        f.append(circle(q_x, q_y, r, fill="none", stroke=FIELD, sw=1.5))
        f.append(text(q_x + r * 0.707 + 8, q_y - r * 0.707 - 2, potentials[i], size=11, bold=True, color=FIELD))

    # Лінії напруженості E (ортогональні еквіпотенціалям)
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    import math
    for deg in angles:
        rad = math.radians(deg)
        x1 = q_x + 24 * math.cos(rad)
        y1 = q_y + 24 * math.sin(rad)
        x2 = q_x + 180 * math.cos(rad)
        y2 = q_y + 180 * math.sin(rad)
        f.append(arrow(x1, y1, x2, y2, color=POS, sw=1.8))
        f.append(text(q_x + 192 * math.cos(rad), q_y + 192 * math.sin(rad) + 4, "E", size=12, bold=True, color=POS))

    # Права частина: пояснення ортогональності та градієнта
    px = 540
    f.append(rect(px - 110, 55, 230, 240, fill="#fcfdff", stroke=LINE, sw=1.4, rx=10))
    f.append(text(px, 80, "Властивості потенціалу:", size=13, bold=True, color=INK))

    info_lines = [
        "1. Вектор E ⊥ φ = const",
        "   у кожній точці простору.",
        "2. E напрямлений у бік",
        "   найшвидшого спадання φ.",
        "3. Робота вздовж екві-",
        "   потенціалі дорівнює 0:",
        "   W = q · (φ − φ) = 0."
    ]
    for idx, line_str in enumerate(info_lines):
        color = POS if "E ⊥" in line_str or "spadannia" in line_str else INK
        bold = True if idx in [0, 2, 4] else False
        f.append(text(px - 95, 110 + idx * 22, line_str, size=11, anchor="start", bold=bold, color=color))

    # Плашка знизу
    b, w, h = textbox(W / 2, H - 20, "E = −grad φ = −(∂φ/∂x i + ∂φ/∂y j + ∂φ/∂z k)", size=13, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "potential-surfaces.svg"), W, H, *f)


# ── Фігура 4: Неконсервативне вихорове електричне поле (індукція) ───────────
def fig_non_conservative_loop():
    W, H = 700, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Неконсервативне вихорове поле: ∇ × E = −∂B/∂t ≠ 0", size=16, bold=True))

    cx, cy = 250, 185

    # Соленоїд (змінне магнітне поле в центрі)
    f.append(circle(cx, cy, 75, fill="#fff5f5", stroke=NEG, sw=2.2))
    # Магнітний потік dB/dt (вектор направлений на нас / від нас)
    f.append(circle(cx, cy, 28, fill=NEG, stroke=NEG, sw=1.5))
    f.append(text(cx, cy + 5, "⊗ B(t)", size=14, bold=True, color="#ffffff"))
    f.append(text(cx, cy - 90, "Змінний магнітний потік dB/dt", size=12, bold=True, color=NEG))

    # Замкнені колові силові лінії індукованого електричного поля E_ind
    for r_ind in [110, 150, 190]:
        f.append(circle(cx, cy, r_ind, fill="none", stroke=POS, sw=2.0))
        # Стрілка вихору за годинниковою стрілкою
        import math
        arr_x = cx + r_ind * math.cos(math.radians(45))
        arr_y = cy + r_ind * math.sin(math.radians(45))
        f.append(arrow(arr_x - 5, arr_y - 5, arr_x + 5, arr_y + 5, color=POS, sw=2.5))
        f.append(text(cx + r_ind + 12, cy + 4, "E_ind", size=12, bold=True, color=POS))

    # Права частина: Порівняльне пояснення
    px = 540
    f.append(rect(px - 110, 50, 230, 240, fill="#fcfdff", stroke=LINE, sw=1.4, rx=10))
    f.append(text(px, 76, "Вихорове поле E_ind:", size=14, bold=True, color=NEG))

    text_rows = [
        "• Силові лінії замкнені",
        "  (не мають початку/кінця).",
        "• Циркуляція по контуру:",
        "  ∮ E · dl = −dΦ/dt = ЕРС",
        "• Робота на замкненому",
        "  шляху НЕ дорівнює нулю!",
        "• Скалярного потенціалу",
        "  φ для такого поля НЕ існує."
    ]
    for idx, tr in enumerate(text_rows):
        is_bold = "НЕ" in tr or "ЕРС" in tr or "замкнені" in tr
        c_val = NEG if is_bold else INK
        f.append(text(px - 95, 106 + idx * 22, tr, size=11, anchor="start", bold=is_bold, color=c_val))

    # Нижній плашка-підсумок
    b, w, h = textbox(W / 2, H - 18, "Закон індукції Фарадея: ∮ [C] E · dl = −dΦ[B]/dt  (поле НЕ є потенціальним)", size=13, pad=7, fill="#fff5f5", stroke=NEG, sw=1.4, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "non-conservative-loop.svg"), W, H, *f)


# ── Фігура 5: Парадокс двох вольтметрів у неконсервативному полі ────────────
def fig_two_voltmeters_paradox():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Інженерний парадокс двох вольтметрів у неконсервативному полі", size=16, bold=True))

    cx, cy = 370, 185

    # Соленоїд у центрі зі змінним потоком
    f.append(circle(cx, cy, 55, fill="#fff3ed", stroke=NEG, sw=2.0))
    f.append(text(cx, cy + 4, "dΦ/dt", size=14, bold=True, color=NEG))

    # Кільце з двома резисторами R1 та R2
    f.append(circle(cx, cy, 110, fill="none", stroke=LINE, sw=2.5))

    # Вузли X та Y
    x_top, y_top = cx, cy - 110
    x_bot, y_bot = cx, cy + 110
    f.append(circle(x_top, y_top, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(x_top, y_top - 12, "Вузол X", size=13, bold=True, color=INK))

    f.append(circle(x_bot, y_bot, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(x_bot, y_bot + 22, "Вузол Y", size=13, bold=True, color=INK))

    # Резистор R1 (ліворуч)
    rx1, ry1 = cx - 110, cy
    f.append(rect(rx1 - 12, ry1 - 25, 24, 50, fill="#ffffff", stroke=POS, sw=2.0))
    f.append(text(rx1 - 32, ry1 + 4, "R₁", size=14, bold=True, color=POS))

    # Резистор R2 (праворуч)
    rx2, ry2 = cx + 110, cy
    f.append(rect(rx2 - 12, ry2 - 25, 24, 50, fill="#ffffff", stroke=POS, sw=2.0))
    f.append(text(rx2 + 32, ry2 + 4, "R₂", size=14, bold=True, color=POS))

    # Вольтметр V1 (ліворуч, охоплює ліву петлю поза соленоїдом)
    f.append(path_tag(f"M {x_top} {y_top} C {x_top-180} {y_top}, {x_top-240} {y_bot}, {x_bot} {y_bot}", stroke=FIELD, sw=1.8, dash="5,4"))
    vx1, vy1 = cx - 210, cy
    f.append(circle(vx1, vy1, 20, fill="#eef6ef", stroke=FIELD, sw=2.0))
    f.append(text(vx1, vy1 + 6, "V₁", size=14, bold=True, color=FIELD))
    f.append(text(vx1 - 60, vy1 + 4, "Показує V₁ = −I·R₁", size=11, bold=True, color=FIELD))

    # Вольтметр V2 (праворуч, охоплює соленоїд разом із колом)
    f.append(path_tag(f"M {x_top} {y_top} C {x_top+180} {y_top}, {x_top+240} {y_bot}, {x_bot} {y_bot}", stroke=NEG, sw=1.8, dash="5,4"))
    vx2, vy2 = cx + 210, cy
    f.append(circle(vx2, vy2, 20, fill="#fff5f5", stroke=NEG, sw=2.0))
    f.append(text(vx2, vy2 + 6, "V₂", size=14, bold=True, color=NEG))
    f.append(text(vx2 + 60, vy2 + 4, "Показує V₂ = +I·R₂", size=11, bold=True, color=NEG))

    # Пояснювальний плашка-підсумок
    b, w, h = textbox(W / 2, H - 20, "Обидва прилади підключені до одних точок X і Y, але V₁ ≠ V₂ через магнітний потік у петлі V₂!", size=12, pad=7, fill="#fff8e7", stroke="#d97706", sw=1.4, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "two-voltmeters-paradox.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_path_independence()
    p2 = fig_circulation_micro_loop()
    p3 = fig_potential_surfaces()
    p4 = fig_non_conservative_loop()
    p5 = fig_two_voltmeters_paradox()
    print("written:")
    for p in (p1, p2, p3, p4, p5):
        print("  ", p)
