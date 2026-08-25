# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зонні діаграми: Шотткі-Мотт та Бардін
# ════════════════════════════════════════════════════════════════════════════
def fig_schottky_bardeen_models():
    W, H = 880, 420
    f = []

    # Тло та межі трьох панелей
    f.append(line(290, 25, 290, 395, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(580, 25, 580, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Панель А: Ізольовані матеріали до контакту ──
    f.append(text(145, 45, "А: До контакту (у вакуумі)", size=13, bold=True, color=INK))
    f.append(text(145, 63, "Ізольовані фази (qPhi_m > qPhi_s)", size=10, color=MUTED))

    # Рівень вакууму
    f.append(line(20, 95, 270, 95, color="#7f8c8d", sw=2))
    f.append(text(250, 87, "E_vac", size=10, bold=True, color="#7f8c8d"))

    # Метал (ліворуч: 30..100)
    f.append(rect(30, 160, 70, 200, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(65, 178, "Метал", size=11, bold=True, color=DARK))
    f.append(line(30, 260, 100, 260, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(65, 252, "E_Fm", size=10, bold=True, color="#8e44ad"))

    # Робота виходу металу qPhi_m
    f.append(line(85, 95, 85, 260, color="#2980b9", sw=1.2))
    f.append(text(60, 175, "qPhi_m", size=10, bold=True, color="#2980b9"))

    # Напівпровідник (праворуч: 150..260)
    f.append(rect(150, 140, 110, 220, fill="#fdfefe", stroke=MUTED, sw=1))
    f.append(text(205, 155, "n-напівпровідник", size=10, bold=True, color=DARK))
    f.append(line(150, 190, 260, 190, color="#c0392b", sw=2)) # Ec
    f.append(line(150, 210, 260, 210, color="#8e44ad", sw=1.5, dash="3 3")) # E_Fs
    f.append(line(150, 310, 260, 310, color="#2980b9", sw=2)) # Ev

    f.append(text(245, 182, "E_c", size=10, bold=True, color="#c0392b"))
    f.append(text(245, 204, "E_Fs", size=10, bold=True, color="#8e44ad"))
    f.append(text(245, 304, "E_v", size=10, bold=True, color="#2980b9"))

    # Електронна спорідненість qChi
    f.append(line(170, 95, 170, 190, color="#d35400", sw=1.2))
    f.append(text(182, 140, "qChi", size=10, bold=True, color="#d35400"))

    # ── Панель Б: Рівноважний контакт Шотткі-Мотта ──
    f.append(text(435, 45, "Б: Модель Шотткі-Мотта", size=13, bold=True, color=INK))
    f.append(text(435, 63, "Атомарно чиста межа (D_it = 0)", size=10, color=MUTED))

    # Метал (320..390)
    f.append(rect(320, 160, 70, 200, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(355, 178, "Метал", size=11, bold=True, color=DARK))
    f.append(line(320, 260, 390, 260, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(355, 252, "E_F", size=10, bold=True, color="#8e44ad"))

    # Зони напівпровідника з вигином вгору
    f.append(svg_path("M 390 170 C 420 170 450 210 550 210", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 390 290 C 420 290 450 330 550 330", stroke="#2980b9", sw=2.5, fill="none")) # Ev
    f.append(line(390, 260, 550, 260, color="#8e44ad", sw=1.5, dash="3 3")) # E_F

    f.append(text(535, 202, "E_c", size=10, bold=True, color="#c0392b"))
    f.append(text(535, 322, "E_v", size=10, bold=True, color="#2980b9"))

    # Бар'єр Phi_Bn та збіднена зона W
    f.append(line(390, 170, 390, 260, color="#d35400", sw=1.5))
    f.append(text(408, 215, "qPhi_Bn", size=10, bold=True, color="#d35400"))

    f.append(line(390, 365, 480, 365, color=DARK, sw=1.2))
    f.append(line(390, 360, 390, 370, color=DARK, sw=1.2))
    f.append(line(480, 360, 480, 370, color=DARK, sw=1.2))
    f.append(text(435, 383, "W (ОПЗ)", size=10, bold=True, color=DARK))

    # ── Панель В: Модель Бардіна з пиннингом ──
    f.append(text(730, 45, "В: Модель Бардіна (пиннинг)", size=13, bold=True, color=INK))
    f.append(text(730, 63, "Поверхневі стани (D_it >> 0)", size=10, color=MUTED))

    # Метал (610..680)
    f.append(rect(610, 160, 70, 200, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(645, 178, "Метал", size=11, bold=True, color=DARK))
    f.append(line(610, 260, 680, 260, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(645, 252, "E_F", size=10, bold=True, color="#8e44ad"))

    # Шар поверхневих станів на межі x=680
    f.append(rect(678, 160, 4, 200, fill="#e74c3c", stroke="none"))
    f.append(text(720, 165, "Поверхневі стани", size=9, bold=True, color="#e74c3c"))

    # Нейтральний рівень E_0
    f.append(line(680, 245, 840, 245, color="#27ae60", sw=1.2, dash="2 2"))
    f.append(text(820, 237, "E_0", size=10, bold=True, color="#27ae60"))

    # Вигин зон із закріпленням рівня Фермі на E_0
    f.append(svg_path("M 680 180 C 700 180 730 210 840 210", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 680 300 C 700 300 730 330 840 330", stroke="#2980b9", sw=2.5, fill="none")) # Ev
    f.append(line(680, 260, 840, 260, color="#8e44ad", sw=1.5, dash="3 3")) # E_F

    f.append(text(820, 202, "E_c", size=10, bold=True, color="#c0392b"))
    f.append(text(820, 322, "E_v", size=10, bold=True, color="#2980b9"))
    f.append(text(710, 280, "зафіксовано на E_0", size=9, bold=True, color="#e74c3c"))

    body = "".join(f)
    render(os.path.join(OUT, "schottky-bardeen-models.svg"), W, H, body)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Механізми переносу зарядучерез бар'єр
# ════════════════════════════════════════════════════════════════════════════
def fig_transport_mechanisms():
    W, H = 880, 380
    f = []

    f.append(text(440, 30, "Механізми переносу носіїв заряду через межу метал–напівпровідник", size=14, bold=True, color=INK))

    # Метал (ліворуч: 80..220)
    f.append(rect(80, 70, 140, 270, fill="#eaeded", stroke=MUTED, sw=1.5))
    f.append(text(150, 100, "МЕТАЛ", size=13, bold=True, color=DARK))
    f.append(line(80, 240, 220, 240, color="#8e44ad", sw=2.5, dash="4 2"))
    f.append(text(150, 230, "Рівень Фермі E_F", size=11, bold=True, color="#8e44ad"))

    # Напівпровідник: Зони з параболічним вигином (220..780)
    # Зона провідності Ec
    f.append(svg_path("M 220 120 C 260 120 360 220 780 220", stroke="#c0392b", sw=3, fill="none"))
    # Валентна зона Ev
    f.append(svg_path("M 220 240 C 260 240 360 340 780 340", stroke="#2980b9", sw=2.5, fill="none"))
    # Рівень Фермі в напівпровіднику
    f.append(line(220, 240, 780, 240, color="#8e44ad", sw=1.5, dash="3 3"))

    f.append(text(750, 210, "E_c", size=12, bold=True, color="#c0392b"))
    f.append(text(750, 330, "E_v", size=12, bold=True, color="#2980b9"))
    f.append(text(750, 232, "E_F", size=11, bold=True, color="#8e44ad"))

    # Позначення висоти бар'єра qPhi_Bn
    f.append(line(220, 120, 220, 240, color="#d35400", sw=2))
    f.append(text(245, 175, "qPhi_Bn", size=12, bold=True, color="#d35400"))

    # 1. Термоелектронна емісія TE (над вершиною)
    f.append(svg_path("M 550 215 C 450 210 320 80 180 110", stroke="#27ae60", sw=3, fill="none"))
    f.append(polygon([(185, 102), (170, 112), (187, 118)], fill="#27ae60"))
    f.append(circle(550, 215, 6, fill="#27ae60", stroke="#1e8449", sw=1))
    f.append(text(480, 85, "1. Термоелектронна емісія (TE)", size=11, bold=True, color="#27ae60"))
    f.append(text(480, 100, "E > qPhi_Bn (тепловий кидок)", size=10, color=MUTED))

    # 2. Термопольова емісія TFE (через середню частину)
    f.append(svg_path("M 500 218 C 440 218 360 185 280 185", stroke="#d35400", sw=2.5, fill="none", dash="4 3"))
    f.append(arrow(280, 185, 180, 185, color="#d35400", sw=2.5))
    f.append(circle(500, 218, 5, fill="#d35400", stroke="#a04000", sw=1))
    f.append(text(480, 145, "2. Термопольова емісія (TFE)", size=11, bold=True, color="#d35400"))
    f.append(text(480, 160, "Теплове збудження + тунелювання", size=10, color=MUTED))

    # 3. Польова емісія FE (тунелювання біля основи)
    f.append(arrow(400, 235, 180, 235, color="#2980b9", sw=2.5))
    f.append(circle(400, 235, 5, fill="#2980b9", stroke="#1b4f72", sw=1))
    f.append(text(480, 260, "3. Польова емісія (FE)", size=11, bold=True, color="#2980b9"))
    f.append(text(480, 275, "Квантове тунелювання (N_d > 10¹⁹ см⁻³)", size=10, color=MUTED))

    body = "".join(f)
    render(os.path.join(OUT, "transport-mechanisms.svg"), W, H, body)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Залежність питомого опору rho_c від N_d
# ════════════════════════════════════════════════════════════════════════════
def fig_contact_resistance_doping():
    W, H = 840, 380
    f = []

    f.append(text(420, 30, "Залежність питомого опору контакту rho_c від концентрації допування N_d", size=14, bold=True, color=INK))

    # Осі координат
    x0, y0 = 100, 320
    x_len, y_len = 680, 250
    f.append(arrow(x0, y0, x0 + x_len + 20, y0, color=DARK, sw=2))
    f.append(arrow(x0, y0, x0, y0 - y_len - 20, color=DARK, sw=2))

    f.append(text(x0 + x_len + 15, y0 + 30, "N_d (см⁻³)", size=12, bold=True, color=DARK))
    f.append(text(x0 - 55, y0 - y_len - 15, "rho_c (Ом·см²)", size=12, bold=True, color=DARK))

    # Поділки по осі X (N_d: 10^15 .. 10^20)
    x_ticks = [
        (x0 + 50, "10¹⁵"),
        (x0 + 170, "10¹⁶"),
        (x0 + 290, "10¹⁷"),
        (x0 + 410, "10¹⁸"),
        (x0 + 530, "10¹⁹"),
        (x0 + 650, "10²⁰")
    ]
    for xt, label in x_ticks:
        f.append(line(xt, y0, xt, y0 + 6, color=DARK, sw=1.5))
        f.append(text(xt, y0 + 22, label, size=11, color=DARK))
        f.append(line(xt, y0 - y_len, xt, y0, color="#eaeded", sw=1, dash="2 2"))

    # Поділки по осі Y (rho_c: 10^-8 .. 10^2)
    y_ticks = [
        (y0 - 30, "10⁻⁸"),
        (y0 - 80, "10⁻⁶"),
        (y0 - 130, "10⁻⁴"),
        (y0 - 180, "10⁻²"),
        (y0 - 230, "10⁰")
    ]
    for yt, label in y_ticks:
        f.append(line(x0 - 6, yt, x0, yt, color=DARK, sw=1.5))
        f.append(text(x0 - 25, yt + 4, label, size=11, color=DARK))
        f.append(line(x0, yt, x0 + x_len, yt, color="#eaeded", sw=1, dash="2 2"))

    # Області режимів переносу
    f.append(line(x0 + 290, y0 - y_len, x0 + 290, y0, color="#e74c3c", sw=1.2, dash="4 3"))
    f.append(line(x0 + 530, y0 - y_len, x0 + 530, y0, color="#e74c3c", sw=1.2, dash="4 3"))

    f.append(text(x0 + 170, y0 - y_len + 20, "Режим TE", size=11, bold=True, color="#27ae60"))
    f.append(text(x0 + 170, y0 - y_len + 36, "(випрямний бар'єр)", size=9, color=MUTED))

    f.append(text(x0 + 410, y0 - y_len + 20, "Режим TFE", size=11, bold=True, color="#d35400"))
    f.append(text(x0 + 410, y0 - y_len + 36, "(змішаний)", size=9, color=MUTED))

    f.append(text(x0 + 600, y0 - y_len + 20, "Режим FE", size=11, bold=True, color="#2980b9"))
    f.append(text(x0 + 600, y0 - y_len + 36, "(тунельний омічний)", size=9, color=MUTED))

    # Криві залежності для різних висот бар'єра qPhi_Bn
    # 1. High barrier: 0.8 eV (Червона)
    f.append(svg_path("M 150 110 L 390 115 C 450 120 530 200 650 285", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(660, 275, "qPhi_Bn = 0.8 еВ", size=10, bold=True, color="#c0392b"))

    # 2. Medium barrier: 0.6 eV (Синя)
    f.append(svg_path("M 150 150 L 390 155 C 450 160 530 240 650 305", stroke="#2980b9", sw=2.5, fill="none"))
    f.append(text(660, 300, "qPhi_Bn = 0.6 еВ", size=10, bold=True, color="#2980b9"))

    # 3. Low barrier: 0.4 eV (Зелена)
    f.append(svg_path("M 150 190 L 390 195 C 450 200 530 270 650 315", stroke="#27ae60", sw=2.5, fill="none"))
    f.append(text(660, 318, "qPhi_Bn = 0.4 еВ", size=10, bold=True, color="#27ae60"))

    body = "".join(f)
    render(os.path.join(OUT, "contact-resistance-doping.svg"), W, H, body)

if __name__ == "__main__":
    fig_schottky_bardeen_models()
    fig_transport_mechanisms()
    fig_contact_resistance_doping()
    print("Всі фігури згенеровано у folder img/")
