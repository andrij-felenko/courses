# -*- coding: utf-8 -*-
"""Фігури до теми «Передавальний вентиль (CMOS transmission gate)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Деградація порогової напруги в одиночних NMOS та PMOS ключах ────────
def fig_weak_rails():
    W, H = 840, 360
    f = []

    # Лівий блок: NMOS пропускає "1"
    f.append(rect(20, 20, 385, 320, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(212, 48, "Одиночний NMOS-ключ: передача логічної «1»", size=13, bold=True, color="#1f2328"))

    # Схема NMOS
    f.append(line(35, 110, 85, 110, color=LINE, sw=2))
    f.append(textbox(75, 80, "Vin = Vdd (3.3 В)", size=11, pad=5, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])

    # Транзистор NMOS символ
    f.append(line(85, 110, 125, 110, color=LINE, sw=2))
    f.append(line(125, 90, 125, 130, color=LINE, sw=3))
    f.append(line(117, 90, 117, 130, color=LINE, sw=2.5))
    f.append(line(117, 110, 117, 65, color=LINE, sw=2))
    f.append(line(117, 65, 140, 65, color=LINE, sw=2))
    f.append(textbox(195, 65, "Vgate = Vdd (3.3 В)", size=10, pad=4, fill="#f6f8fa", stroke=MUTED, color=INK)[0])

    f.append(line(125, 110, 175, 110, color=LINE, sw=2))
    f.append(line(175, 110, 220, 110, color=LINE, sw=2))

    # Вихідний конденсатор C_load
    f.append(circle(220, 110, 4, fill=LINE, stroke=LINE))
    f.append(line(220, 110, 220, 145, color=LINE, sw=1.8))
    f.append(line(205, 145, 235, 145, color=LINE, sw=2.5))
    f.append(line(205, 152, 235, 152, color=LINE, sw=2.5))
    f.append(line(220, 152, 220, 180, color=LINE, sw=1.8))
    f.append(line(210, 180, 230, 180, color=LINE, sw=2))
    f.append(text(250, 150, "C_load", size=10, color=MUTED))

    # Вихід Vout
    f.append(arrow(220, 110, 275, 110, color=POS, sw=2))
    f.append(textbox(335, 110, "Vout = Vdd − Vth\n(квола «1» ≈ 2.5 В)", size=10, pad=5, fill="#fdedec", stroke=POS, color=POS, bold=True)[0])

    # Пояснювальний текст знизу лівого блоку
    f.append(textbox(212, 255, 
                     "Коли Vout піднімається до (Vdd − Vth),\n"
                     "напруга Vgs падає точно до порогу Vth.\n"
                     "Канал NMOS самозакривається:\n"
                     "транзистор НЕ здатний дотягти вихід до Vdd.\n"
                     "Втрата амплітуди: ΔV = Vth (з урахуванням підкладки)", 
                     size=11, pad=6, fill="#fcfcfc", stroke="#e1e4e8", color=INK)[0])

    # Правий блок: PMOS пропускає "0"
    f.append(rect(435, 20, 385, 320, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(627, 48, "Одиночний PMOS-ключ: передача логічного «0»", size=13, bold=True, color="#1f2328"))

    # Вхід Vin = 0
    f.append(line(450, 110, 500, 110, color=LINE, sw=2))
    f.append(textbox(490, 80, "Vin = 0 В (земля)", size=11, pad=5, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])

    # Транзистор PMOS символ
    f.append(line(500, 110, 540, 110, color=LINE, sw=2))
    f.append(line(540, 90, 540, 130, color=LINE, sw=3))
    f.append(line(532, 90, 532, 130, color=LINE, sw=2.5))
    f.append(circle(527, 110, 3.5, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(line(523, 110, 523, 65, color=LINE, sw=2))
    f.append(line(523, 65, 545, 65, color=LINE, sw=2))
    f.append(textbox(600, 65, "Vgate = 0 В (земля)", size=10, pad=4, fill="#f6f8fa", stroke=MUTED, color=INK)[0])

    f.append(line(540, 110, 590, 110, color=LINE, sw=2))
    f.append(line(590, 110, 635, 110, color=LINE, sw=2))

    # Вихідний конденсатор C_load
    f.append(circle(635, 110, 4, fill=LINE, stroke=LINE))
    f.append(line(635, 110, 635, 145, color=LINE, sw=1.8))
    f.append(line(620, 145, 650, 145, color=LINE, sw=2.5))
    f.append(line(620, 152, 650, 152, color=LINE, sw=2.5))
    f.append(line(635, 152, 635, 180, color=LINE, sw=1.8))
    f.append(line(625, 180, 645, 180, color=LINE, sw=2))
    f.append(text(665, 150, "C_load", size=10, color=MUTED))

    # Вихід Vout
    f.append(arrow(635, 110, 690, 110, color=POS, sw=2))
    f.append(textbox(750, 110, "Vout = |Vthp|\n(кволий «0» ≈ 0.7 В)", size=10, pad=5, fill="#fdedec", stroke=POS, color=POS, bold=True)[0])

    # Пояснювальний текст знизу правого блоку
    f.append(textbox(627, 255, 
                     "Коли Vout спадає до |Vthp| відносно землі,\n"
                     "напруга |Vgs| падає точно до порогу |Vthp|.\n"
                     "Канал PMOS передчасно закривається:\n"
                     "транзистор НЕ здатний розрядити вихід у чистий 0.\n"
                     "Залишковий рівень: Vout,min = |Vthp|", 
                     size=11, pad=6, fill="#fcfcfc", stroke="#e1e4e8", color=INK)[0])

    render(os.path.join(IMG, 'tg-concept-weak-rails.svg'), W, H, *f)


# ── 2. Схемотехнічна будова CMOS передавального вентиля ─────────────────────
def fig_switch_structure():
    W, H = 840, 420
    f = []

    f.append(rect(20, 20, 800, 380, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(W/2, 48, "Електрична схема передавального вентиля (CMOS Transmission Gate)", size=16, bold=True, color="#1f2328"))

    # Клема A (ліворуч)
    f.append(circle(70, 210, 6, fill="#eaf2fd", stroke=NEG, sw=2))
    f.append(textbox(70, 170, "Клема A\n(Вхід/Вихід)", size=11, pad=5, fill="#f6f8fa", stroke=MUTED, bold=True)[0])
    f.append(line(76, 210, 210, 210, color=LINE, sw=2.5))

    # Розгалуження на PMOS (вгору) та NMOS (вниз)
    f.append(circle(210, 210, 4, fill=LINE, stroke=LINE))
    f.append(line(210, 210, 210, 130, color=LINE, sw=2.5)) # До PMOS
    f.append(line(210, 130, 320, 130, color=LINE, sw=2.5))

    f.append(line(210, 210, 210, 290, color=LINE, sw=2.5)) # До NMOS
    f.append(line(210, 290, 320, 290, color=LINE, sw=2.5))

    # PMOS транзистор (вгорі)
    f.append(line(320, 130, 370, 130, color=LINE, sw=2.5))
    f.append(line(370, 115, 370, 145, color=LINE, sw=3))   # канал
    f.append(line(378, 115, 378, 145, color=LINE, sw=2.5)) # затвор
    f.append(circle(383, 130, 3.5, fill="#ffffff", stroke=LINE, sw=1.5)) # інверсія
    f.append(line(387, 130, 430, 130, color=LINE, sw=2))
    f.append(line(430, 130, 430, 70, color=LINE, sw=2))   # відвід керування PMOS
    f.append(line(370, 130, 470, 130, color=LINE, sw=2.5))
    f.append(text(495, 120, "PMOS (проводить при високих Vin)", size=11, bold=True, color="#7d6608", anchor="start"))
    
    # Підкладка PMOS до Vdd
    f.append(line(370, 115, 370, 60, color=POS, sw=1.5, dash="2,2"))
    f.append(text(370, 50, "N-Well -> Vdd", size=9, color=POS, bold=True, anchor="middle"))

    # NMOS транзистор (внизу)
    f.append(line(320, 290, 370, 290, color=LINE, sw=2.5))
    f.append(line(370, 275, 370, 305, color=LINE, sw=3))   # канал
    f.append(line(378, 275, 378, 305, color=LINE, sw=2.5)) # затвор
    f.append(line(378, 290, 430, 290, color=LINE, sw=2))
    f.append(line(430, 290, 430, 340, color=LINE, sw=2))   # відвід керування NMOS
    f.append(line(370, 290, 470, 290, color=LINE, sw=2.5))
    f.append(text(495, 280, "NMOS (проводить при низьких Vin)", size=11, bold=True, color=NEG, anchor="start"))
    
    # Підкладка NMOS до Vss
    f.append(line(370, 305, 370, 360, color=NEG, sw=1.5, dash="2,2"))
    f.append(text(370, 375, "P-Sub -> Vss", size=9, color=NEG, bold=True, anchor="middle"))

    # З'єднання стоків PMOS і NMOS на праву клему B
    f.append(line(470, 130, 560, 130, color=LINE, sw=2.5))
    f.append(line(470, 290, 560, 290, color=LINE, sw=2.5))
    f.append(line(560, 130, 560, 290, color=LINE, sw=2.5))
    f.append(circle(560, 210, 4, fill=LINE, stroke=LINE))
    f.append(line(560, 210, 720, 210, color=LINE, sw=2.5))

    # Клема B (праворуч)
    f.append(circle(720, 210, 6, fill="#eaf2fd", stroke=NEG, sw=2))
    f.append(textbox(720, 170, "Клема B\n(Вихід/Вхід)", size=11, pad=5, fill="#f6f8fa", stroke=MUTED, bold=True)[0])

    # Схема парафазного керування з інвертором
    f.append(textbox(120, 340, "Сигнал EN", size=11, pad=5, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True)[0])
    f.append(line(165, 340, 430, 340, color=FIELD, sw=2)) # До затвора NMOS
    f.append(circle(240, 340, 4, fill=FIELD, stroke=FIELD))
    f.append(line(240, 340, 240, 70, color=FIELD, sw=2))

    # Інвертор на лінії до PMOS
    f.append('<polygon points="230,82 230,58 254,70" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % LINE)
    f.append(circle(258, 70, 3.5, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(line(262, 70, 430, 70, color=POS, sw=2))
    f.append(text(285, 55, "EN_bar (інвертований)", size=10, color=POS, bold=True))

    # Стан вентиля у рамці
    f.append(textbox(685, 90, 
                     "EN = 1 (EN_bar = 0):\n"
                     "Ключ ВІДКРИТИЙ (R_on)\n"
                     "Повний розмах 0...Vdd", 
                     size=10, pad=5, fill="#eafaf1", stroke=FIELD, color="#1e8449", bold=True)[0])

    f.append(textbox(685, 310, 
                     "EN = 0 (EN_bar = 1):\n"
                     "Ключ ЗАКРИТИЙ (R_off)\n"
                     "Високий імпеданс (Hi-Z)", 
                     size=10, pad=5, fill="#fdedec", stroke=POS, color=POS, bold=True)[0])

    render(os.path.join(IMG, 'tg-cmos-switch-structure.svg'), W, H, *f)


# ── 3. Графік сумарного динамічного опору Ron(Vin) ──────────────────────────
def fig_ron_curves():
    W, H = 840, 400
    f = []

    f.append(rect(20, 20, 800, 360, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(W/2, 45, "Еквівалентний динамічний опір відкритого ключа R_on(Vin)", size=16, bold=True, color="#1f2328"))

    # Осі координат
    ox, oy = 110, 310
    gw, gh = 620, 230

    # Вісь X (Vin від 0 до Vdd)
    f.append(arrow(ox, oy, ox + gw + 30, oy, color=LINE, sw=2))
    f.append(text(ox + gw + 40, oy + 5, "Vin", size=13, bold=True, color=INK))
    f.append(text(ox, oy + 20, "0 В", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox + gw/2, oy + 20, "Vdd / 2", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox + gw, oy + 20, "Vdd (3.3 В)", size=11, color=MUTED, anchor="middle"))

    # Вісь Y (Опір Ron)
    f.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))
    f.append(text(ox - 10, oy - gh - 25, "R_on (Ом)", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - 40, "100", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 90, "200", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 140, "400", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - 190, "800+", size=10, color=MUTED, anchor="end"))

    # Допоміжна сітка
    for y_val in [oy - 40, oy - 90, oy - 140, oy - 190]:
        f.append(line(ox, y_val, ox + gw, y_val, color="#e1e4e8", sw=1, dash="3,3"))

    # Побудова кривих:
    pts_nmos = []
    pts_pmos = []
    pts_tg = []

    steps = 100
    for i in range(steps + 1):
        v = i / steps # 0 .. 1 ( Vin / Vdd )
        x = ox + v * gw

        # Наближена модель опорів (з урахуванням підкладки)
        vgs_n = 1.0 - v
        vth_n = 0.20 + 0.12 * math.sqrt(v + 0.1) # зсув через body effect
        if vgs_n <= vth_n:
            rn = 5000.0
        else:
            rn = 80.0 / (vgs_n - vth_n)

        # PMOS:
        vsg_p = v
        vth_p = 0.22 + 0.14 * math.sqrt((1.0 - v) + 0.1)
        if vsg_p <= vth_p:
            rp = 5000.0
        else:
            rp = 95.0 / (vsg_p - vth_p) # при підібраній геометрії Wp ≈ 2.5 Wn

        # Паралельне з'єднання:
        rtg = (rn * rp) / (rn + rp)

        def scale_y(r_val):
            val = min(r_val, 900.0)
            return oy - (val / 4.2)

        pts_nmos.append((x, scale_y(rn)))
        pts_pmos.append((x, scale_y(rp)))
        pts_tg.append((x, scale_y(rtg)))

    # NMOS
    nmos_path = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_nmos])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (nmos_path, NEG))

    # PMOS
    pmos_path = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_pmos])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % (pmos_path, "#d35400"))

    # TG Composite
    tg_path = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in pts_tg])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (tg_path, FIELD))

    # Підписи ліній та виноски
    f.append(textbox(ox + 120, oy - 195, "R_NMOS (зростає при Vin -> Vdd)", size=11, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])
    f.append(textbox(ox + gw - 130, oy - 195, "R_PMOS (зростає при Vin -> 0)", size=11, pad=4, fill="#fdf2e9", stroke="#d35400", color="#d35400", bold=True)[0])
    
    # Виноска для підсумкового Ron
    peak_x = ox + gw / 2
    peak_y = pts_tg[int(steps/2)][1]
    f.append(circle(peak_x, peak_y, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(line(peak_x, peak_y, peak_x, peak_y - 45, color=FIELD, sw=1.5))
    f.append(textbox(peak_x, peak_y - 65, "R_on,TG = R_NMOS || R_PMOS\n(Майже сталий опір ~160...220 Ом)", size=12, pad=6, fill="#eafaf1", stroke=FIELD, color="#1e8449", bold=True)[0])

    render(os.path.join(IMG, 'tg-ron-composite-curves.svg'), W, H, *f)


# ── 4. Динамічні паразити: інжекція заряду та clock feedthrough ────────────
def fig_parasitics():
    W, H = 840, 390
    f = []

    f.append(rect(20, 20, 800, 350, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(W/2, 45, "Паразитна інжекція заряду та взаємна компенсація перемикання", size=16, bold=True, color="#1f2328"))

    # Схема ключа з паразитними ємностями та зарядом каналу
    top_y = 100
    bot_y = 230

    # Вхідний сигнал Vin
    f.append(line(60, 165, 160, 165, color=LINE, sw=2))
    f.append(textbox(100, 140, "Вхідний сигнал Vin", size=11, pad=5, fill="#f6f8fa", stroke=MUTED, bold=True)[0])

    # Розгалуження на затвори
    f.append(line(160, 165, 160, top_y, color=LINE, sw=2))
    f.append(line(160, top_y, 220, top_y, color=LINE, sw=2))
    f.append(line(160, 165, 160, bot_y, color=LINE, sw=2))
    f.append(line(160, bot_y, 220, bot_y, color=LINE, sw=2))

    # PMOS верхній блок
    f.append(textbox(280, top_y, "PMOS\nQ_ch,p > 0 (дірки)", size=11, pad=4, fill="#fdf2e9", stroke="#d35400", color="#d35400", bold=True)[0])
    f.append(line(340, top_y, 450, top_y, color=LINE, sw=2))
    f.append(textbox(280, top_y - 45, "Керування: 0 -> Vdd (↑)", size=10, pad=4, fill="#fdedec", stroke=POS, color=POS)[0])
    f.append(textbox(400, top_y - 25, "C_ov,p (+ΔQ)", size=10, pad=4, fill="#fef9e7", stroke="#f1c40f", color="#7d6608")[0])

    # NMOS нижній блок
    f.append(textbox(280, bot_y, "NMOS\nQ_ch,n < 0 (електрони)", size=11, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])
    f.append(line(340, bot_y, 450, bot_y, color=LINE, sw=2))
    f.append(textbox(280, bot_y + 45, "Керування: Vdd -> 0 (↓)", size=10, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG)[0])
    f.append(textbox(400, bot_y + 25, "C_ov,n (−ΔQ)", size=10, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG)[0])

    # Спільний вихідний вузол вибірки
    f.append(line(450, top_y, 450, bot_y, color=LINE, sw=2))
    f.append(circle(450, 165, 5, fill=LINE, stroke=LINE))
    f.append(line(450, 165, 540, 165, color=LINE, sw=2.5))

    # Конденсатор зберігання C_H
    f.append(circle(540, 165, 4, fill=LINE, stroke=LINE))
    f.append(line(540, 165, 540, 205, color=LINE, sw=2))
    f.append(line(520, 205, 560, 205, color=LINE, sw=3))
    f.append(line(520, 213, 560, 213, color=LINE, sw=3))
    f.append(line(540, 213, 540, 240, color=LINE, sw=2))
    f.append(line(530, 240, 550, 240, color=LINE, sw=2))
    f.append(textbox(595, 210, "C_H\n(Ємність вибірки)", size=10, pad=4, fill="#f6f8fa", stroke=MUTED)[0])

    # Вихід Vout
    f.append(arrow(540, 165, 640, 165, color=FIELD, sw=2.5))
    f.append(textbox(715, 165, "V_hold = Vin + ΔV_err", size=11, pad=5, fill="#eafaf1", stroke=FIELD, color="#1e8449", bold=True)[0])

    # Механізм компенсації у рамці праворуч внизу
    f.append(textbox(W/2, 325, 
                     "Взаємне гасіння зарядів при закриванні ключа:\n"
                     "NMOS вкидає негативний заряд інжекції (−Q_ch,n / 2) та спадну наводку (−ΔV_clk).\n"
                     "PMOS одночасно вкидає позитивний заряд (+Q_ch,p / 2) та висхідну наводку (+ΔV_clk).\n"
                     "Залишковий п'єдестал помилки: ΔV_err = (Q_inj,p − Q_inj,n) / (2·C_H) ≈ 0 (за умови підбору Wp/Wn)", 
                     size=11, pad=6, fill="#fcfcfc", stroke="#d0d7de", color=INK)[0])

    render(os.path.join(IMG, 'tg-parasitics-charge-injection.svg'), W, H, *f)


# ── 5. Топологія на кристалі: суміщення активних ділянок дифузії ─────────────
def fig_silicon_layout():
    W, H = 840, 380
    f = []

    f.append(rect(20, 20, 800, 340, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(W/2, 45, "Топологічне розміщення на кристалі: спільна дифузія (Diffusion Sharing)", size=16, bold=True, color="#1f2328"))

    # N-Well область (верхня половина для PMOS)
    f.append(rect(50, 70, 500, 120, fill="none", stroke="#f39c12", sw=1.5, rx=4))
    f.append(text(140, 92, "N-Well (Карман PMOS) -> Vdd", size=10, color="#b9770e", bold=True))

    # P+ дифузія PMOS розділена затвором
    f.append(rect(140, 110, 165, 60, fill="#f5b7b1", stroke="#c0392b", sw=1.5, rx=2))
    f.append(text(175, 145, "p⁺ дифузія", size=10, color="#922b21", bold=True))
    f.append(rect(360, 110, 165, 60, fill="#f5b7b1", stroke="#c0392b", sw=1.5, rx=2))
    f.append(text(495, 145, "p⁺ дифузія", size=10, color="#922b21", bold=True))

    # P-підкладка область (нижня половина для NMOS)
    f.append(rect(50, 210, 500, 120, fill="none", stroke="#3498db", sw=1.5, rx=4))
    f.append(text(150, 232, "P-Substrate (Підкладка NMOS) -> Vss", size=10, color="#1f618d", bold=True))

    # N+ дифузія NMOS розділена затвором
    f.append(rect(140, 250, 165, 60, fill="#aed6f1", stroke="#2471a3", sw=1.5, rx=2))
    f.append(text(175, 285, "n⁺ дифузія", size=10, color="#1a5276", bold=True))
    f.append(rect(360, 250, 165, 60, fill="#aed6f1", stroke="#2471a3", sw=1.5, rx=2))
    f.append(text(495, 285, "n⁺ дифузія", size=10, color="#1a5276", bold=True))

    # Полікремнієві затвори (вертикальні смуги)
    f.append(rect(310, 95, 45, 90, fill="#d5dbdb", stroke="#7f8c8d", sw=2, rx=2))
    f.append(textbox(332, 80, "Gate (EN_bar)", size=9, pad=3, fill="#f2f3f4", stroke=MUTED, bold=True)[0])

    f.append(rect(310, 235, 45, 90, fill="#d5dbdb", stroke="#7f8c8d", sw=2, rx=2))
    f.append(textbox(332, 340, "Gate (EN)", size=9, pad=3, fill="#f2f3f4", stroke=MUTED, bold=True)[0])

    # Металізація контактів
    f.append(line(225, 105, 225, 315, color="#2e86c1", sw=8))
    f.append(circle(225, 140, 6, fill="#34495e", stroke="#1a252f", sw=1.5))
    f.append(text(225, 144, "X", size=10, color="#ffffff", bold=True, anchor="middle"))
    f.append(circle(225, 280, 6, fill="#34495e", stroke="#1a252f", sw=1.5))
    f.append(text(225, 284, "X", size=10, color="#ffffff", bold=True, anchor="middle"))
    f.append(textbox(225, 60, "Metal 1: Клема A", size=10, pad=4, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True)[0])

    f.append(line(445, 105, 445, 315, color="#2e86c1", sw=8))
    f.append(circle(445, 140, 6, fill="#34495e", stroke="#1a252f", sw=1.5))
    f.append(text(445, 144, "X", size=10, color="#ffffff", bold=True, anchor="middle"))
    f.append(circle(445, 280, 6, fill="#34495e", stroke="#1a252f", sw=1.5))
    f.append(text(445, 284, "X", size=10, color="#ffffff", bold=True, anchor="middle"))
    f.append(textbox(445, 60, "Metal 1: Клема B", size=10, pad=4, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True)[0])

    # Підпис переваг топології праворуч
    f.append(textbox(680, 200, "Суміщення контактів:\n\n• Зменшення площі на ~40%\n• Зниження паразитної ємності C_j\n• Симетричний двосторонній зв'язок\n• Захисні кільця проти Latch-up", size=11, pad=8, fill="#fcfcfc", stroke="#bdc3c7", color=INK)[0])

    render(os.path.join(IMG, 'tg-silicon-layout-sharing.svg'), W, H, *f)


# ── 6. Схемотехнічні застосування: MUX 2:1 та Master-Slave D-Flip-Flop ──────
def fig_applications():
    W, H = 860, 440
    f = []

    f.append(rect(20, 15, 820, 410, fill="none", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(text(W/2, 40, "Застосування у цифрових ІС: MUX 2:1 та Master-Slave TG D-Flip-Flop", size=16, bold=True, color="#1f2328"))

    # Ліва половина: Мультиплексор 2:1 на 2-х передавальних вентилях
    f.append(rect(35, 60, 360, 345, fill="none", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(215, 85, "Мультиплексор 2:1 (MUX 2:1)", size=14, bold=True, color="#1f2328"))

    # Вхід D0
    f.append(line(55, 130, 120, 130, color=LINE, sw=2))
    f.append(textbox(80, 110, "Вхід D0", size=10, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])

    # TG0 (пропускає D0 при Sel = 0)
    f.append(rect(120, 110, 70, 40, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(155, 135, "TG 0", size=11, bold=True, color=FIELD))
    f.append(text(155, 100, "Sel_bar / Sel", size=9, color=MUTED))

    # Вхід D1
    f.append(line(55, 230, 120, 230, color=LINE, sw=2))
    f.append(textbox(80, 210, "Вхід D1", size=10, pad=4, fill="#eaf2fd", stroke=NEG, color=NEG, bold=True)[0])

    # TG1 (пропускає D1 при Sel = 1)
    f.append(rect(120, 210, 70, 40, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(155, 235, "TG 1", size=11, bold=True, color=FIELD))
    f.append(text(155, 200, "Sel / Sel_bar", size=9, color=MUTED))

    # Об'єднання виходів TG0 та TG1
    f.append(line(190, 130, 250, 130, color=LINE, sw=2))
    f.append(line(190, 230, 250, 230, color=LINE, sw=2))
    f.append(line(250, 130, 250, 230, color=LINE, sw=2))
    f.append(circle(250, 180, 4, fill=LINE, stroke=LINE))
    
    # Вихідний буфер/інвертор
    f.append(line(250, 180, 280, 180, color=LINE, sw=2))
    f.append('<polygon points="280,195 280,165 310,180" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % LINE)
    f.append(circle(314, 180, 3.5, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(arrow(318, 180, 360, 180, color=POS, sw=2))
    f.append(textbox(355, 155, "Вихід OUT", size=10, pad=4, fill="#fdedec", stroke=POS, color=POS, bold=True)[0])

    # Пояснення MUX
    f.append(textbox(215, 335, 
                     "Усього 4 транзистори ключів + 2 на інвертор Sel.\n"
                     "Разом: 6 транзисторів (проти 12 у класичному CMOS AND-OR).\n"
                     "Нульове статичне споживання та затримка одного ключа.", 
                     size=10, pad=5, fill="#f8f9fa", stroke="#e1e4e8", color=INK)[0])

    # Права половина: Master-Slave Transmission-Gate D-Flip-Flop
    f.append(rect(415, 60, 420, 345, fill="none", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(625, 85, "Master-Slave TG D-тригер (16 транзисторів)", size=14, bold=True, color="#1f2328"))

    # Схема D-FF
    # Вхід D
    f.append(line(430, 150, 460, 150, color=LINE, sw=2))
    f.append(text(442, 140, "D", size=11, bold=True, color=NEG))

    # TG1 (Master input)
    f.append(rect(460, 135, 40, 30, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(480, 155, "TG1", size=10, bold=True, color=FIELD))
    f.append(text(480, 125, "CLK_b", size=9, color=MUTED))

    # Inv1
    f.append(line(500, 150, 520, 150, color=LINE, sw=2))
    f.append('<polygon points="520,162 520,138 545,150" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    f.append(circle(548, 150, 3, fill="#ffffff", stroke=LINE, sw=1.2))

    # Вузол зворотного зв'язку Master (Inv2 + TG2)
    f.append(circle(560, 150, 3, fill=LINE, stroke=LINE))
    f.append(line(551, 150, 620, 150, color=LINE, sw=2))
    
    # Петля зворотного зв'язку Master вниз
    f.append(line(560, 150, 560, 205, color=LINE, sw=1.5))
    f.append('<polygon points="560,205 535,217 535,193" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    f.append(circle(532, 205, 3, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(line(529, 205, 510, 205, color=LINE, sw=1.5))
    f.append(rect(470, 190, 40, 30, fill="#fef9e7", stroke="#f1c40f", sw=1.5, rx=3))
    f.append(text(490, 210, "TG2", size=10, bold=True, color="#7d6608"))
    f.append(text(490, 230, "CLK", size=9, color=MUTED))
    f.append(line(470, 205, 455, 205, color=LINE, sw=1.5))
    f.append(line(455, 205, 455, 150, color=LINE, sw=1.5))

    # TG3 (Slave input)
    f.append(rect(620, 135, 40, 30, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(640, 155, "TG3", size=10, bold=True, color=FIELD))
    f.append(text(640, 125, "CLK", size=9, color=MUTED))

    # Inv3
    f.append(line(660, 150, 680, 150, color=LINE, sw=2))
    f.append('<polygon points="680,162 680,138 705,150" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    f.append(circle(708, 150, 3, fill="#ffffff", stroke=LINE, sw=1.2))

    # Петля зворотного зв'язку Slave (Inv4 + TG4)
    f.append(circle(720, 150, 3, fill=LINE, stroke=LINE))
    f.append(line(711, 150, 770, 150, color=LINE, sw=2))
    f.append(arrow(770, 150, 805, 150, color=POS, sw=2))
    f.append(textbox(795, 130, "Q", size=11, pad=4, fill="#fdedec", stroke=POS, color=POS, bold=True)[0])

    f.append(line(720, 150, 720, 205, color=LINE, sw=1.5))
    f.append('<polygon points="720,205 695,217 695,193" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % LINE)
    f.append(circle(692, 205, 3, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(line(689, 205, 670, 205, color=LINE, sw=1.5))
    f.append(rect(630, 190, 40, 30, fill="#fef9e7", stroke="#f1c40f", sw=1.5, rx=3))
    f.append(text(650, 210, "TG4", size=10, bold=True, color="#7d6608"))
    f.append(text(650, 230, "CLK_b", size=9, color=MUTED))
    f.append(line(630, 205, 615, 205, color=LINE, sw=1.5))
    f.append(line(615, 205, 615, 150, color=LINE, sw=1.5))

    # Пояснення D-FF
    f.append(textbox(625, 335, 
                     "Двофазне Master-Slave тактування:\n"
                     "CLK = 0: Master слухає вхід D (TG1 відкритий, TG2 закритий),\n"
                     "         Slave тримає стан Q (TG3 закритий, TG4 відкритий).\n"
                     "CLK = 1: Master фіксує біт (TG1 закр., TG2 відкр.),\n"
                     "         Slave передає записаний стан на вихід Q (TG3 відкр., TG4 закр.).", 
                     size=10, pad=5, fill="#f8f9fa", stroke="#e1e4e8", color=INK)[0])

    render(os.path.join(IMG, 'tg-mux-and-dff-circuits.svg'), W, H, *f)


if __name__ == "__main__":
    fig_weak_rails()
    fig_switch_structure()
    fig_ron_curves()
    fig_parasitics()
    fig_silicon_layout()
    fig_applications()
    print("Всі 6 фігур згенеровано успішно.")
