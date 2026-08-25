# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Вольт-амперні характеристики неомічних елементів
# ════════════════════════════════════════════════════════════════════════════
def fig_iv_curves():
    W, H = 840, 460
    f = []

    f.append(text(420, 30, "Вольт-амперні характеристики (ВАХ) неомічних елементів", size=14, bold=True, color=INK))
    f.append(text(420, 50, "Відхилення від лінійного закону Ома під дією напруги, температури та поля", size=11, color=MUTED))

    # Вісь координат (U, I)
    ox, oy = 100, 390
    f.append(arrow(ox, oy, ox + 680, oy, color=INK, sw=1.8))
    f.append(text(ox + 670, oy + 25, "Напруга U (В)", size=11, bold=True, color=INK))

    f.append(arrow(ox, oy, ox, oy - 320, color=INK, sw=1.8))
    f.append(text(ox - 40, oy - 300, "Струм I (А)", size=11, bold=True, color=INK))

    # 1. Омічний резистор (лінійна ВАХ)
    f.append(line(ox, oy, ox + 550, oy - 180, color=MUTED, sw=2, dash="4 4"))
    f.append(text(ox + 565, oy - 185, "Омічний опір (R = const)", size=11, bold=True, color=MUTED))

    # 2. Варистор ZnO (нелінійна ВАХ із гострим коліном)
    f.append(svg_path("M 100 390 L 360 384 Q 400 380 415 320 L 440 90", stroke="#c0392b", sw=2.8, fill="none"))
    f.append(text(455, 110, "Варистор ZnO (α = 30-50)", size=11, bold=True, color="#c0392b"))
    f.append(text(455, 128, "Поріг відмикання U_N", size=10, color="#c0392b"))

    # Позначка напруги спрацювання U_N
    f.append(line(410, oy, 410, oy - 290, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(text(410, oy + 20, "U_N (Клампінг)", size=10, bold=True, color="#c0392b"))

    # 3. NTC термистор (S-подібна ВАХ із негативним диференціальним опором)
    f.append(svg_path("M 100 390 Q 240 330 310 260 Q 360 210 320 150 Q 290 100 340 70", stroke="#2457d6", sw=2.5, fill="none"))
    f.append(text(355, 75, "NTC термистор (Саморозігрів)", size=11, bold=True, color="#2457d6"))
    f.append(text(350, 160, "Область dU/dI < 0", size=10, bold=True, color="#2457d6"))

    # 4. Тунелювання Фаулера — Нордгейма (сильні поля)
    f.append(svg_path("M 100 390 L 480 389 Q 550 388 570 340 L 610 90", stroke="#27ae60", sw=2.5, fill="none"))
    f.append(text(625, 100, "Автоелектронне тунелювання (FN)", size=11, bold=True, color="#27ae60"))
    f.append(text(625, 118, "E > 10⁶ В/см", size=10, color="#27ae60"))

    # Легенда / підказка нижче
    f.append(rect(140, 415, 580, 35, fill="#f8f9fa", stroke="#dcdfe6", sw=1.2, rx=4))
    f.append(text(430, 437, "Неомічність виникає через зміну концентрації або рухливості носіїв під дією поля чи T", size=10, color=INK))

    render(os.path.join(OUT, "nonohmic-iv-curves.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Подвійний бар'єр Шотткі на межі зерен ZnO варистора
# ════════════════════════════════════════════════════════════════════════════
def fig_zno_grain_boundary():
    W, H = 840, 420
    f = []

    f.append(line(420, 20, 420, 400, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: Стан спокою (U = 0) ──
    f.append(text(210, 35, "Рівноважний стан (U = 0 В)", size=13, bold=True, color=INK))
    f.append(text(210, 53, "Симетричний бар'єр Шотткі V_B ≈ 0.8-1.0 еВ", size=11, color=MUTED))

    # Зерно ZnO (ліве) - Межа Bi2O3 - Зерно ZnO (праве)
    f.append(rect(40, 75, 150, 240, fill="#eaf2f8", stroke="#2980b9", sw=1.5))
    f.append(text(115, 95, "Зерно n-ZnO 1", size=11, bold=True, color="#1b4f72"))

    f.append(rect(190, 75, 40, 240, fill="#fdebd0", stroke="#d35400", sw=1.5))
    f.append(text(210, 290, "Bi₂O₃", size=10, bold=True, color="#d35400"))

    f.append(rect(230, 75, 150, 240, fill="#eaf2f8", stroke="#2980b9", sw=1.5))
    f.append(text(305, 95, "Зерно n-ZnO 2", size=11, bold=True, color="#1b4f72"))

    # Симетричний потенціальний бар'єр E_c
    f.append(svg_path("M 50 160 L 120 160 Q 210 260 210 260 Q 210 260 300 160 L 370 160", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(100, 150, "E_c", size=11, bold=True, color="#c0392b"))

    # Захоплені електрони на межі (ловушки O²⁻ / Bi)
    for ty in [130, 160, 190, 220]:
        f.append(circle(210, ty, 4, fill="#c0392b", stroke="#7b241c", sw=1))

    f.append(line(210, 160, 210, 260, color="#8e44ad", sw=1.5, dash="2 2"))
    f.append(text(240, 215, "V_B", size=11, bold=True, color="#8e44ad"))

    f.append(text(210, 345, "Високий опір: R > 10⁹ Ом", size=11, bold=True, color="#c0392b"))
    f.append(text(210, 365, "Термоелектронне перелітання пригнічено", size=10, color=INK))


    # ── Права панель: Сильне поле (U > U_N) ──
    f.append(text(630, 35, "Режим пробою / Клампінгу (U > U_N)", size=13, bold=True, color=INK))
    f.append(text(630, 53, "Сплощення бар'єру + Тунелювання носіїв", size=11, color=MUTED))

    f.append(rect(460, 75, 150, 240, fill="#eaf2f8", stroke="#2980b9", sw=1.5))
    f.append(text(535, 95, "Зерно n-ZnO 1", size=11, bold=True, color="#1b4f72"))

    f.append(rect(610, 75, 40, 240, fill="#fdebd0", stroke="#d35400", sw=1.5))
    f.append(text(630, 290, "Bi₂O₃", size=10, bold=True, color="#d35400"))

    f.append(rect(650, 75, 150, 240, fill="#eaf2f8", stroke="#2980b9", sw=1.5))
    f.append(text(725, 95, "Зерно n-ZnO 2", size=11, bold=True, color="#1b4f72"))

    # Спотворений (похилений) бар'єр під напругою
    f.append(svg_path("M 470 120 L 540 140 Q 630 220 630 220 Q 640 210 700 240 L 790 270", stroke="#c0392b", sw=2.5, fill="none"))

    # Тунелювання електронів крізь звужений бар'єр
    f.append(arrow(520, 160, 660, 160, color="#27ae60", sw=2.5))
    f.append(text(590, 145, "Тунелювання", size=10, bold=True, color="#27ae60"))

    f.append(text(630, 345, "Низький опір: R < 1 Ом", size=11, bold=True, color="#27ae60"))
    f.append(text(630, 365, "Лавинна інжекція та польовий струм", size=10, color=INK))

    render(os.path.join(OUT, "zno-grain-boundary.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Ефект Пуля — Френкеля (зниження бар'єру ловушки)
# ════════════════════════════════════════════════════════════════════════════
def fig_poole_frenkel_barrier():
    W, H = 840, 420
    f = []

    f.append(text(420, 30, "Деформація потенціалу ловушки в сильному полі (Ефект Пуля — Френкеля)", size=14, bold=True, color=INK))
    f.append(text(420, 50, "Електричне поле E знижує висоту кулонівського бар'єру на ΔE = 2·√(e³·E / 4πε)", size=11, color=MUTED))

    # Симетричний кулонівський потенціал без поля E (пунктир)
    f.append(svg_path("M 140 120 Q 380 130 420 340 Q 460 130 700 120", stroke=MUTED, sw=1.8, fill="none", dash="4 4"))
    f.append(text(250, 110, "Потенціал без поля (E = 0)", size=10, color=MUTED))

    # Похилений потенціал під полем E (суцільна лінія)
    f.append(svg_path("M 140 200 Q 380 210 420 340 Q 450 160 700 100", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(580, 90, "Потенціал у полі E > 0", size=11, bold=True, color="#c0392b"))

    # Локалізована ловушка у центрі
    f.append(circle(420, 340, 6, fill="#2457d6", stroke="#1b4f72", sw=1.5))
    f.append(text(420, 365, "Іонізований центр (ловушка)", size=10, bold=True, color="#2457d6"))

    # Початковий бар'єр E_0
    f.append(line(240, 120, 600, 120, color=INK, sw=1, dash="2 2"))
    f.append(text(290, 135, "Дно зони провідності E_c", size=10, color=INK))

    # Зниження бар'єру ΔE
    f.append(line(500, 120, 500, 155, color="#27ae60", sw=1.8))
    f.append(line(493, 120, 507, 120, color="#27ae60", sw=1.8))
    f.append(line(493, 155, 507, 155, color="#27ae60", sw=1.8))
    f.append(text(530, 140, "ΔE = β_PF · √E", size=11, bold=True, color="#27ae60"))

    # Термоемісія електрона крізь знижений вершину
    f.append(arrow(420, 320, 480, 140, color="#2457d6", sw=2))
    f.append(text(495, 230, "Термічний викид", size=10, bold=True, color="#2457d6"))

    # Напрямок поля E
    f.append(arrow(180, 395, 660, 395, color=INK, sw=1.8))
    f.append(text(420, 415, "Напрямок зовнішнього електричного поля E", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "poole-frenkel-barrier.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Залежність R(T) у PTC-кераміці та механізм Хейванга
# ════════════════════════════════════════════════════════════════════════════
def fig_ptc_heywang_barrier():
    W, H = 840, 440
    f = []

    f.append(line(420, 20, 420, 415, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: Графік R(T) PTC термистора ──
    f.append(text(210, 35, "Температурна залежність опору R(T)", size=13, bold=True, color=INK))
    f.append(text(210, 53, "Стрибок опору на 4-6 порядків біля T_c", size=11, color=MUTED))

    # Вісі T та lg(R)
    f.append(arrow(60, 360, 380, 360, color=INK, sw=1.5))
    f.append(text(370, 380, "T (°C)", size=11, bold=True, color=INK))

    f.append(arrow(60, 360, 60, 80, color=INK, sw=1.5))
    f.append(text(20, 95, "lg(R)", size=11, bold=True, color=INK))

    # Крива R(T)
    f.append(svg_path("M 60 280 Q 140 310 180 320 Q 220 325 240 280 Q 270 110 310 100 L 370 100", stroke="#2457d6", sw=2.5, fill="none"))

    # Температура Кюрі T_c
    f.append(line(225, 80, 225, 360, color="#c0392b", sw=1.2, dash="2 2"))
    f.append(text(225, 380, "T_c (Кюрі)", size=10, bold=True, color="#c0392b"))

    f.append(text(120, 345, "NTC область (T < T_c)", size=9, color=MUTED))
    f.append(text(285, 200, "PTC область", size=10, bold=True, color="#2457d6"))
    f.append(text(285, 218, "ΔR ≈ 10⁴-10⁶", size=10, color="#2457d6"))


    # ── Права панель: Механізм Хейванга (Бар'єр на межі зерен) ──
    f.append(text(630, 35, "Модель Хейванга для BaTiO₃", size=13, bold=True, color=INK))
    f.append(text(630, 53, "Екранування бар'єру поляризацією P_s", size=11, color=MUTED))

    # T < Tc: Сегнетоелектрична фаза (Висока епсилон, P_s екранує поверхневі ловушки)
    f.append(rect(460, 80, 330, 140, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    f.append(text(625, 100, "Фаза T < T_c (Сегнетоелектрик)", size=11, bold=True, color="#16a085"))
    f.append(svg_path("M 480 180 Q 625 190 770 180", stroke="#16a085", sw=2, fill="none"))
    f.append(text(625, 140, "Низький бар'єр eΦ_b: P_s компенсує заряд ловушок", size=10, color=INK))
    f.append(text(625, 160, "Висока діелектрична проникність ε_r", size=10, color=INK))

    # T > Tc: Параелектрична фаза (Закон Кюрі-Вейсса, ε_r падає, бар'єр стрімко зростає)
    f.append(rect(460, 240, 330, 140, fill="#fadbd8", stroke="#c0392b", sw=1.5))
    f.append(text(625, 260, "Фаза T > T_c (Параелектрик)", size=11, bold=True, color="#c0392b"))
    f.append(svg_path("M 480 300 Q 625 370 770 300", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(625, 300, "Високий бар'єр eΦ_b ~ 1/ε_r", size=10, bold=True, color="#c0392b"))
    f.append(text(625, 320, "Зникнення P_s → Опір R зростає експоненціально", size=10, color=INK))

    render(os.path.join(OUT, "ptc-heywang-barrier.svg"), W, H, *f)


if __name__ == '__main__':
    fig_iv_curves()
    fig_zno_grain_boundary()
    fig_poole_frenkel_barrier()
    fig_ptc_heywang_barrier()
    print("All nonohmic-resistance figures generated successfully.")
