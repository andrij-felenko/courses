# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=INK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зонні діаграми контакту метал-напівпровідник (до й після контакту)
# ════════════════════════════════════════════════════════════════════════════
def fig_band_diagram():
    W, H = 840, 420
    f = []

    # Розділювальна лінія панелей
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Ізольовані матеріали до контакту ──
    f.append(text(210, 40, "До контакту (в вакуумі)", size=14, bold=True, color=INK))
    
    # Рівень вакууму Evac
    f.append(line(40, 70, 380, 70, color=MUTED, sw=1.5, dash="3 3"))
    f.append(text(385, 74, "E_vac", size=11, color=MUTED, anchor="start"))

    # Метал (ліворуч 40..160)
    f.append(rect(40, 190, 120, 160, fill="#eaecee", stroke="#7f8c8d", sw=1.5))
    f.append(line(40, 190, 160, 190, color=POS, sw=2.5)) # EFm
    f.append(text(100, 210, "Метал", size=12, bold=True, color=INK))
    f.append(text(100, 230, "E_Fm", size=11, bold=True, color=POS))

    # Робота виходу металу Phi_m (від Evac до EFm)
    f.append(line(100, 70, 100, 190, color=POS, sw=1.5))
    f.append(polygon([(96, 80), (100, 70), (104, 80)], fill=POS))
    f.append(polygon([(96, 180), (100, 190), (104, 180)], fill=POS))
    f.append(text(112, 130, "qΦ_m", size=11, bold=True, color=POS, anchor="start"))

    # Напівпровідник n-типу (праворуч 240..380)
    f.append(line(240, 130, 380, 130, color="#c0392b", sw=2)) # Ec
    f.append(line(240, 160, 380, 160, color=NEG, sw=1.5, dash="4 2")) # EFs
    f.append(line(240, 280, 380, 280, color="#2980b9", sw=2)) # Ev

    f.append(text(310, 122, "E_c", size=11, bold=True, color="#c0392b"))
    f.append(text(310, 153, "E_Fs", size=11, bold=True, color=NEG))
    f.append(text(310, 296, "E_v", size=11, bold=True, color="#2980b9"))

    # Спорідненість до електрона chi та робота виходу Phi_s
    f.append(line(260, 70, 260, 130, color=INK, sw=1.5))
    f.append(polygon([(257, 80), (260, 70), (263, 80)], fill=INK))
    f.append(polygon([(257, 120), (260, 130), (263, 120)], fill=INK))
    f.append(text(250, 100, "qχ", size=11, bold=True, color=INK, anchor="end"))

    f.append(line(350, 70, 350, 160, color=NEG, sw=1.5))
    f.append(polygon([(347, 80), (350, 70), (353, 80)], fill=NEG))
    f.append(polygon([(347, 150), (350, 160), (353, 150)], fill=NEG))
    f.append(text(360, 115, "qΦ_s", size=11, bold=True, color=NEG, anchor="start"))


    # ── Права панель: Термодинамічна рівновага після контакту ──
    f.append(text(630, 40, "Термодинамічна рівновага (в контакті)", size=14, bold=True, color=INK))

    # Спільний рівень Фермі EF
    f.append(line(450, 210, 790, 210, color=NEG, sw=1.8, dash="5 3"))
    f.append(text(795, 214, "E_F", size=11, bold=True, color=NEG, anchor="start"))

    # Метал (450..550)
    f.append(rect(450, 210, 100, 140, fill="#eaecee", stroke="#7f8c8d", sw=1.5))
    f.append(text(495, 260, "Метал", size=12, bold=True, color=INK))

    # Вигин зон у напівпровіднику n-типу (550..790)
    # Бар'єр Ec починається з 550 у y=110 і вигинається до 700..790 у y=180
    f.append(svg_path("M 550 110 C 580 110 650 180 700 180 L 790 180", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 550 260 C 580 260 650 330 700 330 L 790 330", stroke="#2980b9", sw=2.5, fill="none")) # Ev

    f.append(text(750, 170, "E_c", size=11, bold=True, color="#c0392b"))
    f.append(text(750, 346, "E_v", size=11, bold=True, color="#2980b9"))

    # Висота бар'єра Шотткі Phi_Bn (від EF до Ec на межі x=550)
    f.append(line(535, 110, 535, 210, color=POS, sw=1.8))
    f.append(polygon([(532, 120), (535, 110), (538, 120)], fill=POS))
    f.append(polygon([(532, 200), (535, 210), (538, 200)], fill=POS))
    f.append(text(525, 160, "qΦ_Bn", size=11, bold=True, color=POS, anchor="end"))

    # Вбудований потенціал Vbi (вигин зоны Ec від 110 до 180)
    f.append(line(715, 110, 715, 180, color=FIELD, sw=1.8))
    f.append(polygon([(712, 120), (715, 110), (718, 120)], fill=FIELD))
    f.append(polygon([(712, 170), (715, 180), (718, 170)], fill=FIELD))
    f.append(line(550, 110, 720, 110, color=MUTED, sw=1, dash="2 2"))
    f.append(text(725, 145, "qV_bi", size=11, bold=True, color=FIELD, anchor="start"))

    # Збіднена область W
    f.append(line(550, 365, 700, 365, color=INK, sw=1.5))
    f.append(line(550, 358, 550, 372, color=INK, sw=1.5))
    f.append(line(700, 358, 700, 372, color=INK, sw=1.5))
    f.append(text(625, 385, "Область просторового заряду (W)", size=11, bold=True, color=INK))

    # Іонізовані донори (+) у збідненій області
    for dx in [580, 620, 660]:
        f.append(plus(dx, 225, r=7))

    render(os.path.join(OUT, "band-diagram.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Ефект Шотткі (зниження бар'єра силами дзеркального відображення)
# ════════════════════════════════════════════════════════════════════════════
def fig_image_force():
    W, H = 760, 420
    f = []

    # Осі координат
    f.append(line(90, 340, 700, 340, color=INK, sw=1.5)) # x (відстань від межі)
    f.append(line(90, 340, 90, 40, color=INK, sw=1.5))   # Потенціальна енергія E

    f.append(polygon([(700, 336), (710, 340), (700, 344)], fill=INK))
    f.append(polygon([(86, 40), (90, 30), (94, 40)], fill=INK))

    f.append(text(715, 344, "Відстань x від металу", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(85, 22, "Потенціальна енергія E(x)", size=11.5, bold=True, color=INK, anchor="start"))

    # Межа метал-напівпровідник x=0
    f.append(rect(40, 40, 50, 300, fill="#eaecee", stroke="#7f8c8d", sw=1.5))
    f.append(text(65, 190, "Метал", size=11.5, bold=True, color=INK))

    # Ідеальний бар'єр без сил дзеркального відображення (трикутний/електричний)
    f.append(svg_path("M 90 80 L 620 310", stroke=MUTED, sw=2, dash="4 4"))
    f.append(text(540, 240, "Ідеальний бар'єр (без дзеркальних сил)", size=11, color=MUTED))

    # Потенціал сил дзеркального відображення -q²/(16п ε x)
    f.append(svg_path("M 95 330 Q 110 90 280 80", stroke=NEG, sw=1.8, dash="3 3"))
    f.append(text(190, 300, "Потенціал дзеркального відображення V_img(x)", size=10.5, color=NEG))

    # Результуючий знижений бар'єр Шотткі
    f.append(svg_path("M 90 140 Q 130 95 180 108 L 620 310", stroke=POS, sw=2.8, fill="none"))
    f.append(text(310, 135, "Результуючий бар'єр Шотткі (з урахуванням ефекту Шотткі)", size=11.5, bold=True, color=POS))

    # Максимум результуючого бар'єра у точці xm
    xm = 180
    ym = 108
    f.append(circle(xm, ym, 4.5, fill=POS, stroke="#7b241c", sw=1.5))
    f.append(line(xm, ym, xm, 340, color=MUTED, sw=1, dash="2 2"))
    f.append(text(xm, 358, "x_m", size=11, bold=True, color=INK))

    # Величина зниження бар'єра Delta Phi
    f.append(line(xm, 80, xm, ym, color=POS, sw=1.5))
    f.append(line(xm - 15, 80, xm + 15, 80, color=MUTED, sw=1, dash="2 2"))
    f.append(polygon([(xm - 3, 90), (xm, 80), (xm + 3, 90)], fill=POS))
    f.append(polygon([(xm - 3, ym - 10), (xm, ym), (xm + 3, ym - 10)], fill=POS))
    f.append(text(xm + 12, 96, "ΔΦ (зниження бар'єра)", size=11, bold=True, color=POS, anchor="start"))

    render(os.path.join(OUT, "image-force-lowering.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Електричні характеристики (ВАХ та вольт-фарадна залежність 1/C²)
# ════════════════════════════════════════════════════════════════════════════
def fig_cv_iv_characteristics():
    W, H = 840, 420
    f = []

    # Лінія розділу
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: ВАХ Діода Шотткі проти p-n діода ──
    f.append(text(210, 40, "Вольт-амперна характеристика (ВАХ)", size=14, bold=True, color=INK))

    # Осі ВАХ
    cx, cy = 160, 240
    f.append(line(40, cy, 380, cy, color=INK, sw=1.5)) # V
    f.append(line(cx, 370, cx, 70, color=INK, sw=1.5))  # I
    f.append(polygon([(380, cy - 3), (388, cy), (380, cy + 3)], fill=INK))
    f.append(polygon([(cx - 3, 70), (cx, 62), (cx + 3, 70)], fill=INK))

    f.append(text(380, cy + 18, "V_F (В)", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(cx + 12, 75, "I_F (мА)", size=11, bold=True, color=INK, anchor="start"))

    # Крива діода Шотткі (нижчий поріг ~0.3 В, вищий витік IR)
    f.append(svg_path("M 50 %d L %d %d C %d %d %d %d %d 80" % (cy + 15, cx, cy + 15, cx + 40, cy + 15, cx + 60, cy - 40, cx + 90), stroke=POS, sw=2.5, fill="none"))
    f.append(text(cx + 40, 75, "Діод Шотткі (V_F ≈ 0.3 В)", size=11, bold=True, color=POS, anchor="start"))

    # Крива кремнієвого p-n діода (поріг ~0.7 В, низький витік)
    f.append(svg_path("M 50 %d L %d %d C %d %d %d %d %d 80" % (cy + 2, cx, cy + 2, cx + 110, cy + 2, cx + 130, cy - 40, cx + 160), stroke=NEG, sw=2.5, fill="none", dash="5 3"))
    f.append(text(cx + 140, 160, "p-n діод (V_F ≈ 0.7 В)", size=11, bold=True, color=NEG, anchor="start"))

    # Позначка прямих напруг VF
    f.append(line(cx + 65, cy - 4, cx + 65, cy + 4, color=POS, sw=1.5))
    f.append(text(cx + 65, cy + 18, "0.3В", size=10.5, color=POS))
    f.append(line(cx + 135, cy - 4, cx + 135, cy + 4, color=NEG, sw=1.5))
    f.append(text(cx + 135, cy + 18, "0.7В", size=10.5, color=NEG))


    # ── Права панель: Вольт-фарадна характеристика 1/C² vs V_R ──
    f.append(text(630, 40, "C-V профіль: Залежність 1/C² від V_R", size=14, bold=True, color=INK))

    # Осі C-V
    cx2, cy2 = 470, 330
    f.append(line(460, cy2, 800, cy2, color=INK, sw=1.5)) # -VR
    f.append(line(cx2, 340, cx2, 70, color=INK, sw=1.5))  # 1/C²
    f.append(polygon([(800, cy2 - 3), (808, cy2), (800, cy2 + 3)], fill=INK))
    f.append(polygon([(cx2 - 3, 70), (cx2, 62), (cx2 + 3, 70)], fill=INK))

    f.append(text(800, cy2 + 18, "Зворотна напруга V_R (В)", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(cx2 + 12, 75, "1 / C² (Ф⁻²)", size=11, bold=True, color=INK, anchor="start"))

    # Лінійна залежність 1/C² від V_R
    # Пряма перетинає вісь напруг ліворуч у точці -Vbi (або Vbi на осі прямої напруги)
    # Зображуємо пряму від лівого відрізка (490, cy2) до (760, 90)
    f.append(svg_path("M 490 %d L 760 90" % cy2, stroke=FIELD, sw=2.5, fill="none"))
    f.append(circle(490, cy2, 4.5, fill=FIELD, stroke="#1e8449", sw=1.5))
    f.append(text(490, cy2 + 18, "V_bi - k_B T / q", size=10.5, bold=True, color=FIELD))

    # Нахил прямої d(1/C²)/dV = 2 / (q εs Nd A²)
    f.append(line(620, 215, 710, 215, color=INK, sw=1.2, dash="3 3"))
    f.append(line(710, 215, 710, 135, color=INK, sw=1.2, dash="3 3"))
    f.append(text(720, 180, "Нахил = 2 / (q ε_s N_d A²)", size=10.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(720, 198, "Визначення N_d", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "cv-iv-characteristics.svg"), W, H, *f)


if __name__ == '__main__':
    fig_band_diagram()
    fig_image_force()
    fig_cv_iv_characteristics()
    print("Schottky barrier figures generated successfully.")
