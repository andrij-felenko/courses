# -*- coding: utf-8 -*-
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke=LINE, sw=2.0, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Схема реактора Чохральського
# ════════════════════════════════════════════════════════════════════════════
def fig_czochralski_furnace_scheme():
    W, H = 840, 620
    f = []

    f.append(text(420, 25, "Конструктивна схема установки витягування монокристалів Чохральського", size=15, bold=True, color=INK))

    # Зовнішня герметична камера (водяне охолодження)
    f.append(rect(140, 45, 560, 550, fill="#f8fafc", stroke=LINE, sw=2.0, rx=10))
    f.append(text(420, 65, "Герметична вакуумна камера (інертна атмосфера Ar, 10–50 мбар)", size=11, bold=True, color=MUTED))

    # Нагрівальний блок і тигель у групі
    f.append('<g transform="translate(0,0)">')

    # Графітовий нагрівач (опору / індукційний)
    f.append(rect(230, 260, 30, 260, fill="#566573", stroke=LINE, sw=1.5, rx=4))
    f.append(rect(580, 260, 30, 260, fill="#566573", stroke=LINE, sw=1.5, rx=4))
    f.append(text(210, 390, "Графітовий", size=11, bold=True, color="#2c3e50"))
    f.append(text(210, 408, "нагрівач", size=11, bold=True, color="#2c3e50"))

    # Теплоізоляція
    f.append(rect(180, 220, 35, 340, fill="#eaeded", stroke=LINE, sw=1.5, rx=3))
    f.append(rect(625, 220, 35, 340, fill="#eaeded", stroke=LINE, sw=1.5, rx=3))

    # Графітовий тигелетримач (susceptor)
    f.append(rect(275, 340, 290, 180, fill="#34495e", stroke=LINE, sw=1.5, rx=6))
    f.append(text(420, 505, "Графітовий підтигельник (susceptor)", size=11, bold=True, color="#ffffff"))

    # Кварцовий тигель SiO2
    f.append(rect(285, 330, 270, 160, fill="#ebf5fb", stroke="#2980b9", sw=2.0, rx=6))
    f.append(text(330, 475, "Кварцовий тигель (SiO₂)", size=10, bold=True, color="#1b4f72"))

    # Розплав кремнію Si (1420 °C)
    f.append(rect(295, 380, 250, 100, fill="#fadbd8", stroke=POS, sw=1.5, rx=4))
    f.append(text(420, 430, "Розплав кремнію Si (T ≈ 1420 °C)", size=12, bold=True, color=POS))

    # Нижній вал обертання тигля (контр-обертання)
    f.append(rect(410, 520, 20, 65, fill="#7f8c8d", stroke=LINE, sw=1.5))
    f.append(arrow(360, 550, 390, 550, color=NEG, sw=2.0))
    f.append(text(340, 554, "ω_t (1–5 об/хв)", size=11, bold=True, color=NEG))

    # Верхній шток витягування
    f.append(rect(415, 80, 10, 120, fill="#7f8c8d", stroke=LINE, sw=1.5))
    f.append(arrow(470, 110, 440, 110, color=POS, sw=2.0))
    f.append(text(520, 114, "ω_c (10–20 об/хв)", size=11, bold=True, color=POS))

    # Затравочний кристал (Seed)
    f.append(rect(414, 200, 12, 30, fill="#a3e4d7", stroke="#117a65", sw=1.5, rx=1))
    f.append(text(495, 205, "Затравка <100> або <111>", size=10, bold=True, color="#117a65"))

    # Тонка шийка Деша (Dash neck)
    f.append(rect(417, 230, 6, 25, fill="#d5f5e3", stroke="#117a65", sw=1.0))
    f.append(text(505, 240, "Шийка Деша (Ø 3-4 мм)", size=10, color="#117a65"))

    # Монокристальний зливок (бульба кремнію)
    p_ingot = "M 417 255 L 360 295 L 360 375 L 480 375 L 480 295 L 423 255 Z"
    f.append(svg_path(p_ingot, stroke="#16a085", sw=2.0, fill="#d4efdf"))
    f.append(text(420, 320, "Монокристальний зливок Si", size=12, bold=True, color="#0e6251"))
    f.append(text(420, 338, "(бульба монокристала)", size=10, color="#0e6251"))

    # Рідкий меніск на межі фаз
    f.append(svg_path("M 360 375 C 350 378, 330 380, 295 380", stroke=POS, sw=2.0))
    f.append(svg_path("M 480 375 C 490 378, 510 380, 545 380", stroke=POS, sw=2.0))
    f.append(text(540, 365, "Меніск рідкої фази", size=10, bold=True, color=POS))

    # Стрілка витягування (рух вгору)
    f.append(arrow(340, 200, 340, 110, color=POS, sw=2.5))
    f.append(text(280, 150, "Швидкість", size=11, bold=True, color=POS))
    f.append(text(280, 166, "витягування v_p", size=11, bold=True, color=POS))
    f.append(text(280, 182, "(1–3 мм/хв)", size=10, color=POS))

    # Оптична система
    f.append(circle(640, 340, 16, fill="#f9e79f", stroke="#b9770e", sw=1.5))
    f.append(text(640, 344, "CCD", size=9, bold=True, color=INK))
    f.append(line(625, 340, 485, 375, color="#b9770e", sw=1.2, dash="3 2"))
    f.append(text(685, 335, "Оптична камера", size=10, bold=True, color="#b9770e"))
    f.append(text(685, 350, "контролю діаметра", size=10, color="#b9770e"))

    f.append('</g>')

    render(os.path.join(OUT, "czochralski-furnace-scheme.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Стадії технологічного процесу
# ════════════════════════════════════════════════════════════════════════════
def fig_czochralski_growth_stages():
    W, H = 840, 480
    f = []

    f.append(text(420, 25, "Технологічні стадії вирощування монокристала за методом Чохральського", size=15, bold=True, color=INK))

    stages = [
        ("1. Занурення", "Опускання затравки\nу розплав Si;\nприплавлення та\nтермічна рівновага."),
        ("2. Шийка Деша", "Витягування тонкої\nшийки (3-4 мм)\nдля протравлення\nдислокацій."),
        ("3. Корона (плечі)", "Зниження v_p;\nрозширення конуса\nдо цільового\nдіаметра."),
        ("4. Тіло зливка", "Стаціонарне\nвитягування\nмонокристалічного\nциліндра."),
        ("5. Хвіст (Tail-off)", "Звуження конуса\nперед відривом\nдля уникнення\nтермошоку.")
    ]

    for i, (title, desc) in enumerate(stages):
        x = 25 + i * 160
        y = 60
        w = 150
        h = 390

        f.append('<g transform="translate(0,0)">')
        f.append(rect(x, y, w, h, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=6))
        f.append(rect(x, y, w, 40, fill="#ebf5fb" if i%2==0 else "#e8f8f5", stroke=LINE, sw=1.0, rx=6))
        f.append(text(x + w/2, y + 25, title, size=11, bold=True, color="#1b4f72" if i%2==0 else "#117a65"))

        # Мініатюра стадії
        my = y + 50
        # Розплав на дні
        f.append(rect(x + 10, my + 150, w - 20, 60, fill="#fadbd8", stroke=POS, sw=1.0, rx=2))

        if i == 0:
            f.append(rect(x + 68, my + 40, 14, 112, fill="#a3e4d7", stroke="#117a65", sw=1.5))
        elif i == 1:
            f.append(rect(x + 68, my + 20, 14, 30, fill="#a3e4d7", stroke="#117a65", sw=1.5))
            f.append(rect(x + 72, my + 50, 6, 102, fill="#d5f5e3", stroke="#117a65", sw=1.0))
        elif i == 2:
            f.append(rect(x + 68, my + 10, 14, 25, fill="#a3e4d7", stroke="#117a65", sw=1.5))
            f.append(rect(x + 72, my + 35, 6, 35, fill="#d5f5e3", stroke="#117a65", sw=1.0))
            p_crown = f"M {x+72} {my+70} L {x+30} {my+151} L {x+120} {my+151} L {x+78} {my+70} Z"
            f.append(svg_path(p_crown, stroke="#16a085", sw=1.5, fill="#d4efdf"))
        elif i == 3:
            f.append(rect(x + 68, my + 5, 14, 20, fill="#a3e4d7", stroke="#117a65", sw=1.5))
            f.append(rect(x + 72, my + 25, 6, 20, fill="#d5f5e3", stroke="#117a65", sw=1.0))
            p_body = f"M {x+72} {my+45} L {x+35} {my+75} L {x+35} {my+151} L {x+115} {my+151} L {x+115} {my+75} L {x+78} {my+45} Z"
            f.append(svg_path(p_body, stroke="#16a085", sw=1.5, fill="#d4efdf"))
        elif i == 4:
            f.append(rect(x + 68, my + 5, 14, 15, fill="#a3e4d7", stroke="#117a65", sw=1.5))
            f.append(rect(x + 72, my + 20, 6, 15, fill="#d5f5e3", stroke="#117a65", sw=1.0))
            p_full = f"M {x+72} {my+35} L {x+35} {my+55} L {x+35} {my+125} L {x+75} {my+148} L {x+115} {my+125} L {x+115} {my+55} Z"
            f.append(svg_path(p_full, stroke="#16a085", sw=1.5, fill="#d4efdf"))

        # Опис під малюнком
        tb_svg, _, _ = textbox(x + w/2, my + 245, desc, size=10, pad=4, fill="#ffffff", stroke="none", color=MUTED)
        f.append(tb_svg)
        f.append('</g>')

    render(os.path.join(OUT, "czochralski-growth-stages.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Конвекційні потоки та MCZ
# ════════════════════════════════════════════════════════════════════════════
def fig_czochralski_convection_mcz():
    W, H = 840, 500
    f = []

    f.append(text(420, 25, "Гідродинаміка розплаву: теплова конвекція, контр-обертання та MCZ", size=15, bold=True, color=INK))

    # Панель 1: Класична конвекція CZ
    f.append('<g transform="translate(0,0)">')
    f.append(rect(30, 55, 375, 415, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(217, 80, "Стандартний процес (CZ)", size=13, bold=True, color="#c0392b"))
    f.append(text(217, 98, "Природна теплова + Марангоні конвекція", size=10, color=MUTED))

    # Кварцовий тигель + розплав
    f.append(rect(75, 180, 285, 230, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    f.append(rect(85, 210, 265, 190, fill="#fadbd8", stroke=POS, sw=1.5, rx=2))

    # Зливок зверху
    f.append(rect(180, 130, 75, 80, fill="#d4efdf", stroke="#16a085", sw=1.5))
    f.append(text(217, 165, "Кристал", size=11, bold=True, color="#0e6251"))

    # Потоки конвекції (підйом по стінках, опускання в центрі)
    f.append(arrow(105, 380, 105, 240, color=POS, sw=2.0))
    f.append(arrow(105, 230, 170, 230, color=POS, sw=2.0))
    f.append(arrow(330, 380, 330, 240, color=POS, sw=2.0))
    f.append(arrow(330, 230, 265, 230, color=POS, sw=2.0))
    f.append(text(130, 310, "Теплий потік", size=10, bold=True, color=POS))

    # Розчинення тигля SiO2
    f.append(text(217, 360, "SiO₂ + Si → 2 SiO ↑", size=11, bold=True, color="#b9770e"))
    f.append(text(217, 380, "Кисень [O_i] захоплюється кристалом", size=10, color="#b9770e"))
    f.append('</g>')

    # Панель 2: Процес у магнітному полі (MCZ)
    f.append('<g transform="translate(0,0)">')
    f.append(rect(435, 55, 375, 415, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(622, 80, "Магнітне поле (MCZ)", size=13, bold=True, color="#117a65"))
    f.append(text(622, 98, "Гальмування сили Лоренца (B = 0.1–0.4 Тл)", size=10, color=MUTED))

    # Кварцовий тигель + розплав
    f.append(rect(480, 180, 285, 230, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    f.append(rect(490, 210, 265, 190, fill="#d5f5e3", stroke="#117a65", sw=1.5, rx=2))

    # Зливок зверху
    f.append(rect(585, 130, 75, 80, fill="#d4efdf", stroke="#16a085", sw=1.5))
    f.append(text(622, 165, "Кристал", size=11, bold=True, color="#0e6251"))

    # Поперечні лінії магнітного поля B
    for y_b in [230, 270, 310, 350, 390]:
        f.append(line(450, y_b, 790, y_b, color=NEG, sw=1.5, dash="6 3"))
    f.append(text(780, 220, "Вектор B", size=11, bold=True, color=NEG))

    # Подавлені ламінарні потоки
    f.append(text(622, 300, "Турбулентність пригнічена", size=11, bold=True, color="#117a65"))
    f.append(text(622, 320, "Низький вміст кисню [O_i]", size=10, bold=True, color="#117a65"))
    f.append(text(622, 340, "Стабільний термічний фронт", size=10, color="#117a65"))
    f.append('</g>')

    render(os.path.join(OUT, "czochralski-convection-mcz.svg"), W, H, *f)

if __name__ == "__main__":
    fig_czochralski_furnace_scheme()
    fig_czochralski_growth_stages()
    fig_czochralski_convection_mcz()
    print("SVG generation complete.")
