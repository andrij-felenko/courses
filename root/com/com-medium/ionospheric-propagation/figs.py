# -*- coding: utf-8 -*-
"""Фігури теми «Іоносферне поширення». Запуск: python figs.py → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Шари іоносфери D, E, F1, F2 та денний/нічний профіль ─────────────
def fig_layers():
    W, H = 760, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    parts.append(text(220, 30, "Вдень (максимум іонізації)", 14, INK, "middle", bold=True))
    parts.append(text(580, 30, "Вночі (рекомбінація)", 14, INK, "middle", bold=True))
    parts.append(line(420, 15, 420, 380, color="#d0d7de", sw=1.5, dash="4 4"))

    parts.append(arrow(60, 380, 60, 45, color=INK, sw=2.0))
    parts.append(text(50, 40, "Висота, км", 12, INK, "end", bold=True))

    def y_h(h):
        return 360 - h * (290.0 / 400.0)

    parts.append(rect(20, 360, 720, 40, fill="#e1f5fe", stroke="#0288d1", sw=1.5))
    parts.append(text(390, 385, "Поверхня Землі (0 км)", 13, "#01579b", "middle", bold=True))

    # Шар D
    y_d1, y_d2 = y_h(90), y_h(60)
    parts.append(rect(90, y_d1, 260, y_d2 - y_d1, fill="#ffe0b2", stroke="#f57c00", sw=1.2, rx=4))
    parts.append(text(220, (y_d1 + y_d2)/2 + 4, "Шар D (60–90 км): поглинання НЧ/СЧ", 12, "#e65100", "middle", bold=True))
    parts.append(text(580, (y_d1 + y_d2)/2 + 4, "Зникає повністю", 11, MUTED, "middle", italic=True))

    # Шар E
    y_e1, y_e2 = y_h(150), y_h(90)
    parts.append(rect(90, y_e1, 260, y_e2 - y_e1, fill="#fff9c4", stroke="#fbc02d", sw=1.2, rx=4))
    parts.append(text(220, (y_e1 + y_e2)/2 + 4, "Шар E (90–150 км): відбиття СЧ / низьких ВЧ", 12, "#f57f17", "middle", bold=True))
    parts.append(rect(450, y_e1, 260, y_e2 - y_e1, fill="#fffde7", stroke="#fbc02d", sw=1.0, rx=4))
    parts.append(text(580, (y_e1 + y_e2)/2 + 4, "Слабкий залишковий шар E", 11, MUTED, "middle"))

    # Шар F1
    y_f1_1, y_f1_2 = y_h(250), y_h(150)
    parts.append(rect(90, y_f1_1, 260, y_f1_2 - y_f1_1, fill="#e1bee7", stroke="#8e24aa", sw=1.2, rx=4))
    parts.append(text(220, (y_f1_1 + y_f1_2)/2 + 4, "Шар F1 (150–250 км)", 12, "#4a148c", "middle", bold=True))

    # Шар F2
    y_f2_1, y_f2_2 = y_h(400), y_h(250)
    parts.append(rect(90, y_f2_1, 260, y_f2_2 - y_f2_1, fill="#ce93d8", stroke="#7b1fa2", sw=1.2, rx=4))
    parts.append(text(220, (y_f2_1 + y_f2_2)/2 + 4, "Шар F2 (250–400 км): максимум N_e", 12, "#4a148c", "middle", bold=True))

    # Шар F вночі
    y_fn_1, y_fn_2 = y_h(350), y_h(200)
    parts.append(rect(450, y_fn_1, 260, y_fn_2 - y_fn_1, fill="#d1c4e9", stroke="#512da8", sw=1.5, rx=4))
    parts.append(text(580, (y_fn_1 + y_fn_2)/2 + 4, "Єдиний шар F (~300 км)", 13, "#311b92", "middle", bold=True))

    for h in [60, 90, 150, 250, 400]:
        yh = y_h(h)
        parts.append(line(55, yh, 65, yh, color=INK, sw=1.2))
        parts.append(text(50, yh + 4, str(h), 11, INK, "end"))

    render(os.path.join(IMG, "layers.svg"), W, H, *parts,
           title="Шари іоносфери D, E, F1, F2 та їхня денна й нічна структура")


# ── Фігура 2: Заломлення, критична частота та MUF ─────────────────────────────
def fig_refraction():
    W, H = 760, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    parts.append(rect(40, 360, 680, 40, fill="#eceff1", stroke="#455a64", sw=1.5))
    parts.append(text(380, 385, "Поверхня Землі", 13, "#263238", "middle", bold=True))

    parts.append(rect(40, 100, 680, 80, fill="#f3e5f5", stroke="#ab47bc", sw=1.5, rx=6))
    parts.append(text(680, 125, "Шар F2 (максимум N_e)", 12, "#6a1b9a", "end", bold=True))
    parts.append(text(680, 150, "n < 1 (плазма)", 12, "#8e24aa", "end", italic=True))

    tx_x, tx_y = 120, 360
    parts.append(circle(tx_x, tx_y, 6, fill=POS, stroke=INK, sw=1.5))
    parts.append(text(tx_x, tx_y + 22, "TX (Передавач)", 12, POS, "middle", bold=True))

    parts.append(line(tx_x, tx_y, tx_x, 140, color="#2e7d32", sw=2.0))
    parts.append(arrow(tx_x, 140, tx_x, tx_y - 10, color="#2e7d32", sw=2.0))
    b1, _, _ = textbox(tx_x + 75, 240, "f ≤ f_c (зеніт):\nвідбиття від F2", size=11, pad=6, fill="#e8f5e9", stroke="#2e7d32", sw=1.0, color="#1b5e20")
    parts.append(b1)

    tx2_x = 260
    parts.append(circle(tx2_x, tx_y, 6, fill=POS, stroke=INK, sw=1.5))
    parts.append(arrow(tx2_x, tx_y, tx2_x, 40, color="#c62828", sw=2.0))
    b2, _, _ = textbox(tx2_x + 75, 240, "f > f_c (зеніт):\nпробиває у космос", size=11, pad=6, fill="#ffebee", stroke="#c62828", sw=1.0, color="#b71c1c")
    parts.append(b2)

    tx3_x = 420
    rx3_x = 700
    parts.append(circle(tx3_x, tx_y, 6, fill=POS, stroke=INK, sw=1.5))
    parts.append(circle(rx3_x, tx_y, 6, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(rx3_x, tx_y + 22, "RX (Приймач)", 12, NEG, "middle", bold=True))
    
    mid_x = (tx3_x + rx3_x) / 2
    parts.append(line(tx3_x, tx_y, mid_x - 40, 130, color="#1565c0", sw=2.2))
    parts.append(line(mid_x - 40, 130, mid_x + 40, 130, color="#1565c0", sw=2.2))
    parts.append(arrow(mid_x + 40, 130, rx3_x, tx_y, color="#1565c0", sw=2.2))
    b3, _, _ = textbox(mid_x, 230, "f = MUF = f_c · sec(θ):\nповернення на відстані D", size=11, pad=6, fill="#e3f2fd", stroke="#1565c0", sw=1.0, color="#0d47a1")
    parts.append(b3)

    parts.append(line(tx3_x, tx_y, tx3_x + 120, 130, color="#d84315", sw=1.5, dash="4 3"))
    parts.append(arrow(tx3_x + 120, 130, tx3_x + 200, 30, color="#d84315", sw=1.5))
    b4, _, _ = textbox(tx3_x + 140, 90, "f > MUF:\nвиліт у космос", size=10, pad=5, fill="#fbe9e7", stroke="#d84315", sw=1.0, color="#bf360c")
    parts.append(b4)

    render(os.path.join(IMG, "refraction-reflection.svg"), W, H, *parts,
           title="Поведінка радіохвиль залежно від частоти та кута падіння")


# ── Фігура 3: Мертва зона (Skip distance) та зондування ───────────────────────
def fig_skip_distance():
    W, H = 760, 420
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    # Поверхня Землі
    parts.append(rect(20, 340, 720, 50, fill="#eceff1", stroke="#455a64", sw=1.5))

    # Іоносферний шар F
    parts.append(rect(20, 70, 720, 50, fill="#f3e5f5", stroke="#ab47bc", sw=1.5, rx=6))
    parts.append(text(380, 100, "Відбивальний шар іоносфери (F шар, h ≈ 300 км)", 13, "#6a1b9a", "middle", bold=True))

    # Передавач TX
    tx_x, tx_y = 80, 340
    parts.append(circle(tx_x, tx_y, 7, fill=POS, stroke=INK, sw=1.5))
    parts.append(text(tx_x, 375, "Передавач TX", 12, POS, "middle", bold=True))

    # Межа поверхневої хвилі
    gw_limit = 210
    parts.append(rect(tx_x + 8, 345, gw_limit - tx_x - 16, 38, fill="#c8e6c9", stroke="#388e3c", sw=1.0, rx=4))
    parts.append(text((tx_x + gw_limit)/2, 368, "Поверхнева хвиля", 11, "#1b5e20", "middle", bold=True))

    # Промінь з критичним кутом
    parts.append(line(tx_x, tx_y, 200, 95, color="#c62828", sw=1.5, dash="4 3"))
    parts.append(arrow(200, 95, 270, 20, color="#c62828", sw=1.5))

    # Граничний промінь (D_skip)
    rx_skip = 480
    mid_skip = (tx_x + rx_skip) / 2
    parts.append(line(tx_x, tx_y, mid_skip, 95, color="#1565c0", sw=2.2))
    parts.append(arrow(mid_skip, 95, rx_skip, tx_y, color="#1565c0", sw=2.2))
    parts.append(circle(rx_skip, tx_y, 7, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(rx_skip, 375, "Приймач RX1", 12, NEG, "middle", bold=True))

    # Промінь під пологішим кутом
    rx_far = 680
    mid_far = (tx_x + rx_far) / 2
    parts.append(line(tx_x, tx_y, mid_far, 95, color="#0d47a1", sw=1.8))
    parts.append(arrow(mid_far, 95, rx_far, tx_y, color="#0d47a1", sw=1.8))
    parts.append(circle(rx_far, tx_y, 6, fill=NEG, stroke=INK, sw=1.5))
    parts.append(text(rx_far, 375, "Приймач RX2", 11, NEG, "middle"))

    # Мертва зона (Skip zone / Silent zone)
    parts.append(rect(gw_limit + 5, 345, rx_skip - gw_limit - 10, 38, fill="#ffe0b2", stroke="#f57c00", sw=1.0, rx=4))
    parts.append(text((gw_limit + rx_skip)/2, 368, "МЕРТВА ЗОНА (мовчання)", 12, "#e65100", "middle", bold=True))

    # Стрілка відстані D_skip
    parts.append(line(tx_x, 280, rx_skip, 280, color="#1565c0", sw=1.5))
    parts.append(line(tx_x, 273, tx_x, 287, color="#1565c0", sw=1.5))
    parts.append(line(rx_skip, 273, rx_skip, 287, color="#1565c0", sw=1.5))
    parts.append(text((tx_x + rx_skip)/2, 273, "Відстань стрибка (D_skip)", 12, "#1565c0", "middle", bold=True))

    render(os.path.join(IMG, "skip-distance.svg"), W, H, *parts,
           title="Структура мертвої зони та формування відстані стрибка D_skip")


if __name__ == "__main__":
    fig_layers()
    fig_refraction()
    fig_skip_distance()
    print("Фігури успішно згенеровано у ./img/")
