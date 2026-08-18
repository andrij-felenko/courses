# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke=POS, sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Залежність ядерного та електронного гальмування від енергії іона
# ════════════════════════════════════════════════════════════════════════════
def fig_stopping_power():
    W, H = 820, 440
    f = []

    # Осі координат
    f.append(line(90, 360, 760, 360, color=DARK, sw=2.0)) # Енергія E
    f.append(line(90, 360, 90, 50, color=DARK, sw=2.0))   # Гальмівна здатність dE/dx

    # Підписи осей
    f.append(text(420, 395, "Кінетична енергія іона E (кеВ / МеВ)", size=13, bold=True, color=DARK))
    f.append(text(40, 200, "Гальмівна здатність −dE/dx", size=13, bold=True, color=DARK, anchor="middle"))

    # Позначки на осі Енергії E
    f.append(text(90, 375, "0", size=11, color=MUTED))
    f.append(text(280, 375, "E_c (критична)", size=11, bold=True, color=DARK))
    f.append(text(720, 375, "Високі енергії", size=11, color=MUTED))

    # Пунктир критичної енергії Ec (точка перетину Sn і Se)
    f.append(line(280, 70, 280, 360, color=MUTED, sw=1.5, dash="4 4"))

    # Крива ядерного гальмування Sn(E)
    sn_path = "M 90 360 C 130 220 170 120 200 120 C 240 120 280 180 340 230 C 440 290 580 330 740 345"
    f.append(svg_path(sn_path, stroke=POS, sw=2.8))

    # Крива електронного гальмування Se(E)
    se_path = "M 90 360 C 180 300 280 180 400 130 C 520 95 640 85 740 95"
    f.append(svg_path(se_path, stroke=NEG, sw=2.8))

    # Повна гальмівна здатність S_tot = Sn + Se
    stot_path = "M 90 360 C 150 180 200 80 280 100 C 380 90 540 80 740 90"
    f.append(svg_path(stot_path, stroke=FIELD, sw=2.0, dash="6 3"))

    # Точка перетину Ec
    f.append(circle(280, 180, 6, fill=FILL, stroke=INK, sw=2.0))
    f.append(text(295, 175, "S_n = S_e", size=12, bold=True, color=INK, anchor="start"))

    # Підписи кривих
    f.append(text(190, 100, "Ядерне гальмування S_n(E)", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(190, 115, "(пружні зіткнення, дефекти)", size=10, color=POS, anchor="middle"))

    f.append(text(540, 115, "Електронне гальмування S_e(E)", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(text(540, 130, "(неупруге тертя, S_e ∝ √E)", size=10, color=NEG, anchor="middle"))

    f.append(text(460, 65, "Повне гальмування S_tot = S_n + S_e", size=12, bold=True, color=FIELD, anchor="middle"))

    # Області домінування
    f.append(textbox(185, 410, "Домінує ядерне гальмування\n(руйнування ґратки, каскади)", size=11, fill="#fdecea", stroke=POS)[0])
    f.append(textbox(530, 410, "Домінує електронне гальмування\n(іони летять прямо, розсіювання тепла)", size=11, fill="#eaf0fd", stroke=NEG)[0])

    render(os.path.join(OUT, "stopping-power.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Профіль імплантації, проектований пробіг Rp та каналювання
# ════════════════════════════════════════════════════════════════════════════
def fig_implantation_profile():
    W, H = 820, 440
    f = []

    # Осі координат
    f.append(line(90, 360, 760, 360, color=DARK, sw=2.0)) # Глибина x
    f.append(line(90, 360, 90, 50, color=DARK, sw=2.0))   # Концентрація C(x)

    f.append(text(420, 395, "Глибина від поверхні кремнію x (нм)", size=13, bold=True, color=DARK))
    f.append(text(40, 200, "Концентрація C(x) (см⁻³)", size=13, bold=True, color=DARK, anchor="middle"))

    # Поверхня кремнію x = 0
    f.append(line(90, 50, 90, 360, color="#8e44ad", sw=2.5))
    f.append(text(90, 40, "Поверхня x = 0", size=11, bold=True, color="#8e44ad"))

    # Нормальний Гауссів профіль імплантації
    gauss_path = "M 90 280 C 160 270 230 80 320 80 C 410 80 480 270 560 355 L 750 360"
    f.append(svg_path(gauss_path, stroke=NEG, sw=2.8))

    # Профіль з каналюванням
    channel_path = "M 90 280 C 160 270 230 80 320 80 C 390 100 450 180 540 230 C 620 270 700 320 750 340"
    f.append(svg_path(channel_path, stroke=POS, sw=2.0, dash="5 3"))

    # Максимум Гауссового профілю (Rp)
    f.append(line(320, 80, 320, 360, color=DARK, sw=1.5, dash="4 4"))
    f.append(circle(320, 80, 5, fill=NEG, stroke=INK, sw=1.5))
    f.append(text(320, 375, "R_p (проектований пробіг)", size=11, bold=True, color=DARK))

    # Позначення страґлінгу Delta Rp
    f.append(line(240, 180, 400, 180, color=FIELD, sw=2.0))
    f.append(line(240, 173, 240, 187, color=FIELD, sw=2.0))
    f.append(line(400, 173, 400, 187, color=FIELD, sw=2.0))
    f.append(text(320, 168, "2 · ΔR_p (страґлінг)", size=11, bold=True, color=FIELD))

    # Підписи профілів
    f.append(textbox(210, 110, "Гауссів профіль C(x)\n(придушене каналювання)", size=11, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(590, 180, "Хвіст каналювання\n(вздовж осей <110>)", size=11, fill="#fdecea", stroke=POS)[0])

    # Стрілка нахилу пучка 7°
    f.append(line(60, 120, 120, 140, color="#8e44ad", sw=2.0))
    f.append(text(65, 110, "Пучок іонів (Tilt 7°)", size=11, bold=True, color="#8e44ad", anchor="start"))

    render(os.path.join(OUT, "implantation-profile.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Процес руйнування ґратки та відпалу дефектів (3 етапи)
# ════════════════════════════════════════════════════════════════════════════
def fig_crystal_damage_annealing():
    W, H = 840, 380
    f = []

    # 3 панелі
    f.append(line(280, 30, 280, 360, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(560, 30, 560, 360, color=MUTED, sw=1.2, dash="4 4"))

    # --- Панель A: Бомбардування іоном ---
    f.append(text(140, 45, "(а) Імплантація іона", size=13, bold=True, color=INK))

    for ix in range(4):
        for iy in range(4):
            x = 60 + ix * 50
            y = 120 + iy * 50
            f.append(circle(x, y, 10, fill="#e8f8f5", stroke=FIELD, sw=1.5))
            f.append(text(x, y + 3.5, "Si", size=9, color=FIELD, bold=True))

    f.append(line(135, 60, 160, 210, color=POS, sw=2.5, dash="4 2"))
    f.append(circle(160, 210, 11, fill="#fdecea", stroke=POS, sw=2.0))
    f.append(text(160, 213.5, "B⁺", size=10, color=POS, bold=True))

    f.append(textbox(140, 340, "Первинний удар:\nвибивання PKA-атома", size=11, fill=FILL, stroke=LINE)[0])

    # --- Панель B: Аморфізована зона та дефекти ---
    f.append(text(420, 45, "(б) Каскад дефектів", size=13, bold=True, color=INK))

    import math
    for i in range(16):
        angle = i * 0.4
        r = 20 + (i % 4) * 22
        x = 420 + r * math.cos(angle)
        y = 200 + r * math.sin(angle)
        if i % 3 == 0:
            f.append(circle(x, y, 9, fill="#f4f6f8", stroke=MUTED, sw=1.5))
            f.append(text(x, y + 3, "V", size=9, color=MUTED, bold=True))
        else:
            c_fill = "#fdecea" if i == 5 else "#e8f8f5"
            c_strk = POS if i == 5 else FIELD
            txt = "B" if i == 5 else "Si"
            f.append(circle(x, y, 9, fill=c_fill, stroke=c_strk, sw=1.5))
            f.append(text(x, y + 3, txt, size=9, color=c_strk, bold=True))

    f.append(textbox(420, 340, "Пари Френкеля,\nаморфізація, неактивна домішка", size=11, fill="#fdecea", stroke=POS)[0])

    # --- Панель C: Відпалений кристал (активація) ---
    f.append(text(700, 45, "(в) Термічний відпал (RTA)", size=13, bold=True, color=INK))

    for ix in range(4):
        for iy in range(4):
            x = 620 + ix * 50
            y = 120 + iy * 50
            if ix == 2 and iy == 2:
                f.append(circle(x, y, 11, fill="#fdecea", stroke=POS, sw=2.0))
                f.append(text(x, y + 3.5, "B⁻", size=10, color=POS, bold=True))
            else:
                f.append(circle(x, y, 10, fill="#e8f8f5", stroke=FIELD, sw=1.5))
                f.append(text(x, y + 3.5, "Si", size=9, color=FIELD, bold=True))

    f.append(textbox(700, 340, "Ґратка рекристалізована,\nдомішка активна у вузлі", size=11, fill="#e8f8f5", stroke=FIELD)[0])

    render(os.path.join(OUT, "crystal-damage-annealing.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Архітектурна схема промислового іонного імплантера
# ════════════════════════════════════════════════════════════════════════════
def fig_implanter_architecture():
    W, H = 840, 360
    f = []

    beam_path = "M 90 180 L 230 180 C 270 180 300 130 350 130 L 720 130"
    f.append(svg_path(beam_path, stroke=POS, sw=3.5))

    # 1. Іонне джерело
    f.append(rect(40, 135, 100, 90, fill="#fdecea", stroke=POS, sw=2.0, rx=8))
    f.append(text(90, 170, "Джерело іонів", size=12, bold=True, color=POS))
    f.append(text(90, 190, "BF₃ / PH₃ плазма", size=10, color=MUTED))

    f.append(line(140, 180, 180, 180, color=DARK, sw=1.8))

    # 2. Мас-аналізатор
    f.append(circle(240, 180, 42, fill="#eaf0fd", stroke=NEG, sw=2.0))
    f.append(text(240, 175, "Мас-сепаратор", size=11, bold=True, color=NEG))
    f.append(text(240, 193, "Магніт B (m/q)", size=10, color=NEG))

    f.append(line(240, 180, 270, 220, color=MUTED, sw=1.5, dash="3 3"))
    f.append(circle(270, 220, 4, fill=MUTED, stroke="none"))
    f.append(text(285, 230, "побічні іони", size=9, color=MUTED, anchor="start"))

    # 3. Прискорювач
    f.append(rect(340, 95, 120, 70, fill="#e8f8f5", stroke=FIELD, sw=2.0, rx=6))
    f.append(text(400, 125, "Прискорювач", size=12, bold=True, color=FIELD))
    f.append(text(400, 145, "10 кеВ – 3 МеВ", size=10, color=FIELD))

    # 4. Нейтралізатор
    f.append(rect(490, 95, 120, 70, fill="#fef9e7", stroke="#d35400", sw=2.0, rx=6))
    f.append(text(550, 125, "Нейтралізатор", size=11, bold=True, color="#d35400"))
    f.append(text(550, 145, "Plasma Flood Gun", size=10, color="#d35400"))

    # 5. Робоча камера
    f.append(rect(640, 70, 150, 160, fill=FILL, stroke=LINE, sw=2.0, rx=8))
    f.append(text(715, 95, "Робоча камера", size=12, bold=True, color=INK))

    f.append(line(715, 110, 725, 180, color="#8e44ad", sw=4.0))
    f.append(text(735, 145, "Si-пластина", size=11, bold=True, color="#8e44ad", anchor="start"))
    f.append(text(735, 162, "Tilt 7° / Twist 27°", size=9, color="#8e44ad", anchor="start"))

    f.append(rect(705, 185, 40, 30, fill="#eaeded", stroke=MUTED, sw=1.5, rx=4))
    f.append(text(725, 204, "Дозиметр", size=9, color=MUTED))

    f.append(text(420, 310, "Траєкторія чистих іонів заданого ізотопу (B⁺, P⁺, As⁺)", size=12, bold=True, color=POS))
    f.append(text(420, 335, "Високий вакуум (10⁻⁷ – 10⁻⁸ Торр) вздовж усього тракту імплантера", size=11, color=MUTED))

    render(os.path.join(OUT, "implanter-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stopping_power()
    fig_implantation_profile()
    fig_crystal_damage_annealing()
    fig_implanter_architecture()
    print("Всі 4 фігури успішно згенеровано у ./img/")
