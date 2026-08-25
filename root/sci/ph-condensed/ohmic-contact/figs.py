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
# Фігура 1 — Зонні діаграми: Бар'єр Шотткі vs Ідеальний омічний vs Тунельний
# ════════════════════════════════════════════════════════════════════════════
def fig_band_diagrams():
    W, H = 880, 420
    f = []

    # Тло та межі трьох панелей
    f.append(line(290, 25, 290, 395, color=MUTED, sw=1.5, dash="4 4"))
    f.append(line(580, 25, 580, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Панель А: Випрямний контакт Шотткі (n-тип, Phi_m > Phi_s) ──
    f.append(text(145, 45, "А: Контакт Шотткі", size=14, bold=True, color=INK))
    f.append(text(145, 65, "Випрямний бар'єр (Phi_m > Phi_s)", size=11, color=MUTED))

    # Метал (ліворуч: 30..100) та напівпровідник (праворуч: 100..270)
    f.append(rect(30, 95, 70, 260, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(65, 115, "Метал", size=12, bold=True, color=DARK))
    f.append(line(30, 220, 100, 220, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(65, 212, "E_Fm", size=11, bold=True, color="#8e44ad"))

    # Зони напівпровідника
    f.append(svg_path("M 100 130 C 130 130 170 230 270 230", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 100 230 C 130 230 170 330 270 330", stroke="#2980b9", sw=2.5, fill="none")) # Ev
    f.append(line(100, 220, 270, 220, color="#8e44ad", sw=1.5, dash="3 3")) # E_Fs

    f.append(text(240, 222, "E_c", size=11, bold=True, color="#c0392b"))
    f.append(text(240, 322, "E_v", size=11, bold=True, color="#2980b9"))
    f.append(text(240, 212, "E_F", size=11, bold=True, color="#8e44ad"))

    # Бар'єр Phi_B та збіднена зона W
    f.append(line(100, 130, 100, 220, color="#d35400", sw=1.5))
    f.append(text(115, 175, "Phi_B", size=11, bold=True, color="#d35400"))
    f.append(line(100, 360, 200, 360, color=DARK, sw=1.5))
    f.append(line(100, 355, 100, 365, color=DARK, sw=1.5))
    f.append(line(200, 355, 200, 365, color=DARK, sw=1.5))
    f.append(text(150, 380, "W (широке)", size=11, bold=True, color=DARK))

    # ── Панель Б: Ідеальний омічний контакт (n-тип, Phi_m < Phi_s) ──
    f.append(text(435, 45, "Б: Накопичувальний омічний", size=14, bold=True, color=INK))
    f.append(text(435, 65, "Безбар'єрний контакт (Phi_m < Phi_s)", size=11, color=MUTED))

    # Метал (320..390)
    f.append(rect(320, 95, 70, 260, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(355, 115, "Метал", size=12, bold=True, color=DARK))
    f.append(line(320, 180, 390, 180, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(355, 172, "E_Fm", size=11, bold=True, color="#8e44ad"))

    # Зони з вигином вдолу (накопичення електронів)
    f.append(svg_path("M 390 180 C 420 180 450 140 560 140", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 390 280 C 420 280 450 240 560 240", stroke="#2980b9", sw=2.5, fill="none")) # Ev
    f.append(line(390, 180, 560, 180, color="#8e44ad", sw=1.5, dash="3 3")) # E_Fs

    f.append(text(530, 132, "E_c", size=11, bold=True, color="#c0392b"))
    f.append(text(530, 232, "E_v", size=11, bold=True, color="#2980b9"))
    f.append(text(530, 172, "E_F", size=11, bold=True, color="#8e44ad"))
    f.append(text(450, 205, "накопичення e⁻", size=11, bold=True, color="#27ae60"))

    # ── Панель В: Практичний тунельний омічний контакт (n++) ──
    f.append(text(730, 45, "В: Тунельний омічний (n++)", size=14, bold=True, color=INK))
    f.append(text(730, 65, "Ультравузький бар'єр (N_D > 10¹⁹ см⁻³)", size=11, color=MUTED))

    # Метал (610..680)
    f.append(rect(610, 95, 70, 260, fill="#eaeded", stroke=MUTED, sw=1))
    f.append(text(645, 115, "Метал", size=12, bold=True, color=DARK))
    f.append(line(610, 220, 680, 220, color="#8e44ad", sw=2, dash="4 2"))
    f.append(text(645, 212, "E_Fm", size=11, bold=True, color="#8e44ad"))

    # Зони з різким вигином на дуже короткій відстані
    f.append(svg_path("M 680 130 C 695 130 710 210 850 210", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 680 230 C 695 230 710 310 850 310", stroke="#2980b9", sw=2.5, fill="none")) # Ev
    f.append(line(680, 220, 850, 220, color="#8e44ad", sw=1.5, dash="3 3")) # E_Fs

    f.append(text(820, 202, "E_c", size=11, bold=True, color="#c0392b"))
    f.append(text(820, 302, "E_v", size=11, bold=True, color="#2980b9"))

    # Тунелювання крізь тонкий бар'єр
    f.append(line(650, 220, 715, 220, color="#27ae60", sw=2.5, dash="3 3"))
    f.append(polygon([(715, 216), (725, 220), (715, 224)], fill="#27ae60"))
    f.append(circle(645, 220, 4, fill="#27ae60", stroke="#1e8449", sw=1))
    f.append(circle(732, 220, 4, fill="#27ae60", stroke="#1e8449", sw=1))
    f.append(text(750, 190, "FE тунелювання", size=11, bold=True, color="#27ae60"))

    # Вузький бар'єр W < 2 нм
    f.append(line(680, 360, 710, 360, color=DARK, sw=1.5))
    f.append(line(680, 355, 680, 365, color=DARK, sw=1.5))
    f.append(line(710, 355, 710, 365, color=DARK, sw=1.5))
    f.append(text(725, 380, "W < 2 нм", size=11, bold=True, color=DARK))

    render(os.path.join(OUT, "fig1-band-diagrams.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Механізми переносу заряду та залежність опору від легування
# ════════════════════════════════════════════════════════════════════════════
def fig_transport_mechanisms():
    W, H = 820, 400
    f = []

    # Розподіл на 2 панелі: Ліва (схема TE, TFE, FE) та Права (Графік log(rho_c) vs 1/sqrt(N_D))
    f.append(line(410, 25, 410, 380, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: 3 шляхи проходження носіїв ──
    f.append(text(205, 40, "Механізми подолання бар'єра", size=14, bold=True, color=INK))

    # Зонний бар'єр
    f.append(svg_path("M 50 110 C 100 110 160 270 360 270", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(line(50, 260, 360, 260, color="#8e44ad", sw=1.5, dash="3 3")) # E_F

    # Шлях 1: Термоелектронна емісія (TE) — понад бар'єром
    f.append(svg_path("M 50 95 C 100 95 130 95 180 130 C 210 150 250 260 300 260", stroke="#d35400", sw=2, dash="3 3"))
    f.append(polygon([(180, 93), (190, 95), (180, 97)], fill="#d35400"))
    f.append(text(120, 80, "1. TE (понад бар'єром)", size=11, bold=True, color="#d35400"))

    # Шлях 2: Термоелектронно-польова емісія (TFE) — термоактивоване тунелювання
    f.append(svg_path("M 50 170 L 135 170", stroke="#f39c12", sw=2, dash="3 3"))
    f.append(polygon([(135, 167), (143, 170), (135, 173)], fill="#f39c12"))
    f.append(text(150, 165, "2. TFE", size=11, bold=True, color="#f39c12"))

    # Шлях 3: Польова емісія (FE) — пряме тунелювання біля E_F
    f.append(svg_path("M 50 255 L 175 255", stroke="#27ae60", sw=2.5, dash="3 3"))
    f.append(polygon([(175, 251), (185, 255), (175, 259)], fill="#27ae60"))
    f.append(text(195, 250, "3. FE (квантове тунелювання)", size=11, bold=True, color="#27ae60"))

    # ── Права панель: Залежність rho_c від легування N_D ──
    f.append(text(615, 40, "Залежність rho_c від легування", size=14, bold=True, color=INK))

    # Осі координат
    f.append(line(460, 330, 780, 330, color=DARK, sw=1.5)) # N_D або 1/sqrt(N_D)
    f.append(line(460, 330, 460, 80, color=DARK, sw=1.5))  # log(rho_c)

    f.append(polygon([(780, 326), (790, 330), (780, 334)], fill=DARK))
    f.append(polygon([(456, 80), (460, 70), (464, 80)], fill=DARK))

    f.append(text(760, 355, "N_D (см⁻³)", size=11, bold=True, color=DARK))
    f.append(text(415, 70, "log(rho_c)", size=11, bold=True, color=DARK))

    # Позначки легування на осі X
    f.append(text(500, 350, "10¹⁶", size=10, color=MUTED))
    f.append(text(600, 350, "10¹⁸", size=10, color=MUTED))
    f.append(text(720, 350, "10²⁰", size=10, bold=True, color="#27ae60"))

    # Крива опору log(rho_c): плато у режимі TE, стрімке падіння у режимах TFE та FE
    f.append(svg_path("M 470 110 L 530 110 C 580 115 620 160 740 310", stroke="#2980b9", sw=2.5, fill="none"))

    # Режими на графіку
    f.append(text(480, 95, "Область TE (Thermionic)", size=10.5, color="#d35400"))
    f.append(text(560, 140, "Область TFE", size=10.5, color="#f39c12"))
    f.append(text(660, 240, "Область FE (Tunneling)", size=10.5, bold=True, color="#27ae60"))
    f.append(text(660, 260, "rho_c ~ exp(const / sqrt(N_D))", size=10, color="#27ae60"))

    render(os.path.join(OUT, "fig2-transport-mechanisms.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Структура та геометрія вимірювання за методом TLM
# ════════════════════════════════════════════════════════════════════════════
def fig_tlm_method():
    W, H = 840, 480
    f = []

    # Розподіл на 2 рівні: Верхній (схема контактів TLM) та Нижній (графік R_T від відстані d)
    f.append(line(30, 220, 810, 220, color=MUTED, sw=1.5, dash="4 4"))

    # ── Верхній рівень: Топологія контактних площадок TLM ──
    f.append(text(420, 30, "Топологія тест-структури TLM (Transfer Line Method)", size=14, bold=True, color=INK))

    # Напівпровідникова меза (основа) від y=55 до y=125 (висота 70)
    f.append(rect(60, 55, 720, 70, fill="#f9ebea", stroke="#c0392b", sw=1.5))
    f.append(text(640, 115, "Легований шар (меза)", size=10, bold=True, color="#c0392b"))

    # Металеві площадки з наростаючими зазорами
    pads_x = [80, 150, 240, 370, 530]
    spacings = ["d₁", "d₂", "d₃", "d₄"]

    for idx, px in enumerate(pads_x):
        f.append(rect(px, 55, 50, 45, fill="#bdc3c7", stroke="#2c3e50", sw=1.5))
        f.append(text(px + 25, 82, "Контакт", size=9.5, color=DARK))

    # Розміри зазорів d_i під мезою
    for idx in range(len(pads_x) - 1):
        x1 = pads_x[idx] + 50
        x2 = pads_x[idx + 1]
        mid = (x1 + x2) / 2
        f.append(line(x1, 150, x2, 150, color="#8e44ad", sw=1.5))
        f.append(line(x1, 144, x1, 156, color="#8e44ad", sw=1.5))
        f.append(line(x2, 144, x2, 156, color="#8e44ad", sw=1.5))
        f.append(text(mid, 172, spacings[idx], size=11, bold=True, color="#8e44ad"))

    # ── Нижній рівень: Графік залежності R_T(d) ──
    f.append(text(420, 242, "Графік екстраполяції опору R_T від відстані d", size=14, bold=True, color=INK))

    # Осі координат для R_T від d
    ox, oy = 260, 410
    f.append(line(120, oy, 760, oy, color=DARK, sw=1.5)) # d
    f.append(line(ox, oy, ox, 265, color=DARK, sw=1.5))  # R_T

    f.append(polygon([(760, oy - 4), (770, oy), (760, oy + 4)], fill=DARK))
    f.append(polygon([(ox - 4, 265), (ox, 255), (ox + 4, 265)], fill=DARK))

    f.append(text(740, oy + 25, "Відстань d", size=11, bold=True, color=DARK))
    f.append(text(ox - 70, 265, "Опір R_T", size=11, bold=True, color=DARK))

    # Пряма регресії R_T = (R_sh / W) * d + 2 R_c
    f.append(svg_path("M 170 410 L 700 280", stroke="#27ae60", sw=2.5, fill="none"))

    # Точки вимірювань на лінії
    pts = [(320, 365), (410, 340), (520, 310), (660, 270)]
    for px, py in pts:
        f.append(circle(px, py, 4, fill="#c0392b", stroke="#7b241c", sw=1.5))

    # Перетин з віссю Y: 2 R_c
    f.append(circle(ox, 385, 5, fill="#8e44ad", stroke="#5b2c6f", sw=1.5))
    f.append(line(ox - 10, 385, ox + 10, 385, color="#8e44ad", sw=1, dash="2 2"))
    f.append(text(ox + 90, 390, "2 R_c (відсічка на Y)", size=11, bold=True, color="#8e44ad"))

    # Перетин з віссю X: -2 L_T
    f.append(circle(170, oy, 5, fill="#d35400", stroke="#a04000", sw=1.5))
    f.append(text(170, oy + 25, "-2 L_T", size=11, bold=True, color="#d35400"))

    # Похил прямої: R_sh / W
    f.append(text(540, 315, "нахил = R_sh / W", size=11, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "fig3-tlm-method.svg"), W, H, *f)


if __name__ == '__main__':
    fig_band_diagrams()
    fig_transport_mechanisms()
    fig_tlm_method()
    print("Figures for ohmic-contact generated successfully.")
