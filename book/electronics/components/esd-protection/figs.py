# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_esd_threat_waveform():
    """Порівняння імпульсів: надшвидкий ESD (IEC 61000-4-2) проти енергетичного Surge (IEC 61000-4-5)."""
    W, H = 820, 400
    p = []

    # ── Ліворуч: ESD-розряд (IEC 61000-4-2) ──
    ox1, oy1 = 70, 310
    ax1, ay1 = 380, 70
    p.append(line(ox1, oy1, ax1, oy1, sw=2))
    p.append(line(ox1, oy1, ox1, ay1, sw=2))
    p.append(text(ax1 - 10, oy1 + 25, "час (нс)", size=11, anchor="end", color=MUTED))
    p.append(text(ox1 - 10, ay1 + 10, "струм (А)", size=11, anchor="end", color=MUTED))
    p.append(text(210, 45, "ESD-розряд (IEC 61000-4-2)", size=13.5, bold=True, color=POS))

    # Шкала ESD
    p.append(text(ox1 - 8, 105, "30", size=10.5, anchor="end", color=MUTED))
    p.append(text(ox1 - 8, 195, "15", size=10.5, anchor="end", color=MUTED))
    p.append(text(ox1 - 8, oy1 + 4, "0", size=10.5, anchor="end", color=MUTED))
    p.append(line(ox1 - 4, 105, ox1, 105, color=MUTED, sw=1.5))
    p.append(line(ox1 - 4, 195, ox1, 195, color=MUTED, sw=1.5))

    # Мітки часу ESD
    p.append(text(105, oy1 + 18, "1", size=10, anchor="middle", color=MUTED))
    p.append(text(195, oy1 + 18, "30", size=10, anchor="middle", color=MUTED))
    p.append(text(300, oy1 + 18, "60", size=10, anchor="middle", color=MUTED))

    # Форма хвилі ESD (перший пік 0.7-1 нс до 30 А, спад, плато на 30 нс 16 А, спад на 60 нс)
    esd_pts = [
        (ox1, oy1),
        (ox1 + 15, oy1 - 80),
        (ox1 + 28, 105),       # 1 нс -> 30 А
        (ox1 + 42, 175),       # спад після голки
        (ox1 + 75, 190),       # 15-20 нс
        (ox1 + 125, 205),      # 30 нс -> 16 А
        (ox1 + 230, 260),      # 60 нс -> 8 А
        (ox1 + 295, oy1 - 6),  # 100 нс
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % q for q in esd_pts), POS))

    # Анотації ESD
    p.append(fitbox(130, 85, 170, 24, "t_rise < 1 нс (dI/dt = 30 А/нс)", size=9.5, fill="#fdecea", stroke=POS))
    p.append(fitbox(160, 225, 160, 22, "загроза: пробій діелектрика", size=9.5, fill=FILL, stroke=MUTED))

    # ── Роздільник ──
    p.append(line(410, 50, 410, 350, color=MUTED, sw=1, dash="4,4"))

    # ── Праворуч: Surge-імпульс (IEC 61000-4-5) ──
    ox2, oy2 = 470, 310
    ax2, ay2 = 780, 70
    p.append(line(ox2, oy2, ax2, oy2, sw=2))
    p.append(line(ox2, oy2, ox2, ay2, sw=2))
    p.append(text(ax2 - 10, oy2 + 25, "час (мкс)", size=11, anchor="end", color=MUTED))
    p.append(text(ox2 - 10, ay2 + 10, "струм (кА)", size=11, anchor="end", color=MUTED))
    p.append(text(615, 45, "Surge-імпульс 8/20 мкс (IEC 61000-4-5)", size=13.5, bold=True, color=NEG))

    # Шкала Surge
    p.append(text(ox2 - 8, 105, "2.0", size=10.5, anchor="end", color=MUTED))
    p.append(text(ox2 - 8, 205, "1.0", size=10.5, anchor="end", color=MUTED))
    p.append(text(ox2 - 8, oy2 + 4, "0", size=10.5, anchor="end", color=MUTED))
    p.append(line(ox2 - 4, 105, ox2, 105, color=MUTED, sw=1.5))
    p.append(line(ox2 - 4, 205, ox2, 205, color=MUTED, sw=1.5))

    # Мітки часу Surge
    p.append(text(ox2 + 75, oy2 + 18, "8", size=10, anchor="middle", color=MUTED))
    p.append(text(ox2 + 190, oy2 + 18, "20", size=10, anchor="middle", color=MUTED))

    # Форма хвилі Surge (наростання 8 мкс, спад до 50% на 20 мкс)
    surge_pts = [
        (ox2, oy2),
        (ox2 + 25, oy2 - 90),
        (ox2 + 55, oy2 - 180),
        (ox2 + 75, 105),       # 8 мкс -> 100%
        (ox2 + 115, 140),
        (ox2 + 155, 180),
        (ox2 + 190, 205),      # 20 мкс -> 50%
        (ox2 + 245, 260),
        (ox2 + 295, oy2 - 8),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % q for q in surge_pts), NEG))

    # Анотації Surge
    p.append(fitbox(550, 85, 175, 24, "t_rise = 8 мкс, тривалість 20 мкс", size=9.5, fill="#eaf2fd", stroke=NEG))
    p.append(fitbox(550, 225, 175, 22, "загроза: теплове плавлення (Дж)", size=9.5, fill=FILL, stroke=MUTED))

    # Підсумок унизу
    p.append(fitbox(100, 355, 620, 28,
                    "ESD вбиває швидкістю напруги (dI/dt, пробій затвора), Surge — масою енергії (джоулі, вигорання)",
                    size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'esd-threat-waveform.svg'), W, H, *p,
           title="Порівняння часових та енергетичних профілів ESD і Surge")


def fig_suppressor_mechanisms():
    """Фізична структура трьох класів компонентів: кремній (TVS), кераміка ZnO (MOV), полімер (PVVM)."""
    W, H = 820, 390
    p = []

    # Три колонки
    cols = [
        {"x": 40, "w": 230, "title": "TVS-діод (Кремній)", "sub": "p-n лавинний перехід", "color": POS},
        {"x": 295, "w": 230, "title": "MOV (Кераміка ZnO)", "sub": "межі зерен (бар'єри)", "color": FIELD},
        {"x": 550, "w": 230, "title": "PVVM (Полімер)", "sub": "наночастинки в матриці", "color": NEG},
    ]

    for c in cols:
        cx = c["x"]
        cw = c["w"]
        p.append(rect(cx, 40, cw, 290, rx=8, fill="#ffffff", stroke=c["color"], sw=2))
        p.append(text(cx + cw / 2, 65, c["title"], size=13, bold=True, color=c["color"]))
        p.append(text(cx + cw / 2, 85, c["sub"], size=10.5, color=MUTED))
        p.append(line(cx + 15, 95, cx + cw - 15, 95, color=MUTED, sw=1, dash="2,2"))

    # 1. TVS: кристал кремнію
    p.append(rect(65, 115, 180, 50, fill="#fdecea", stroke=POS, rx=4))
    p.append(text(155, 135, "p+ шар (високолегований)", size=10, bold=True, color=POS))
    p.append(line(65, 140, 245, 140, color=POS, sw=1.5))
    p.append(text(155, 155, "n- епітаксійний шар (лавина)", size=10, color=INK))
    p.append(fitbox(55, 180, 200, 42, "Лавинне множення носіїв\nЧас реакції: < 100 пс\nR_dyn: 0.1…0.5 Ом", size=10, fill=FILL, stroke=LINE))
    p.append(fitbox(55, 235, 200, 36, "Паразитна ємність:\n0.1…500 пФ (потрібен міст)", size=10, fill=FILL, stroke=MUTED))
    p.append(fitbox(55, 280, 200, 36, "Ресурс:\nМільйони ударів без втоми", size=10, fill="#eef7f0", stroke=FIELD))

    # 2. MOV: зерна ZnO
    # Малюємо сітку зерен
    import math
    for gx, gy in [(325, 125), (370, 125), (415, 125), (460, 125),
                   (345, 150), (390, 150), (435, 150), (480, 150)]:
        p.append(circle(gx, gy, 14, fill="#eef7f0", stroke=FIELD, sw=1.5))
    p.append(text(410, 140, "зерна ZnO (~3 В)", size=9.5, bold=True, color=FIELD))
    p.append(fitbox(310, 180, 200, 42, "Тунелювання крізь межі зерен\nЧас реакції: 1…5 нс\nR_dyn: 0.5…2 Ом", size=10, fill=FILL, stroke=LINE))
    p.append(fitbox(310, 235, 200, 36, "Паразитна ємність:\n5…2000 пФ (велика площа)", size=10, fill=FILL, stroke=MUTED))
    p.append(fitbox(310, 280, 200, 36, "Ресурс:\nДеградація (старіння меж)", size=10, fill="#fdecea", stroke=POS))

    # 3. PVVM: наночастинки в полімерній матриці
    p.append(rect(575, 115, 180, 50, fill="#eaf2fd", stroke=NEG, rx=4))
    for px, py in [(595, 130), (630, 145), (665, 128), (700, 145), (730, 130),
                   (615, 150), (650, 132), (685, 152), (715, 150)]:
        p.append(circle(px, py, 4, fill=INK, stroke=NEG, sw=1))
    p.append(text(665, 140, "наночастинки Ni/Ag", size=9.5, bold=True, color=NEG))
    p.append(fitbox(565, 180, 200, 42, "Польова емісія та мікроіскри\nЧас реакції: < 1 нс\nV_clamp: 25…40 В (висока)", size=10, fill=FILL, stroke=LINE))
    p.append(fitbox(565, 235, 200, 36, "Паразитна ємність:\n0.05…0.15 пФ (наднизька)", size=10, fill="#eef7f0", stroke=FIELD))
    p.append(fitbox(565, 280, 200, 36, "Ресурс:\nПомірна стійкість (струм малий)", size=10, fill=FILL, stroke=MUTED))

    # Підсумок унизу
    p.append(fitbox(100, 345, 620, 30,
                    "TVS — точний швидкий затискач; MOV — поглинач великої енергії; PVVM — наднизькоємнісний бар'єр для НВЧ",
                    size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'suppressor-mechanisms.svg'), W, H, *p,
           title="Фізика і внутрішня мікроструктура захисних компонентів")


def fig_clamping_iv_curves():
    """Вольт-амперні характеристики та динаміка затискання: лавинний TVS, Snapback-TVS, MOV та PVVM."""
    W, H = 820, 420
    p = []

    ox, oy = 90, 320
    ax, ay = 760, 50
    p.append(line(ox, oy, ax, oy, sw=2))
    p.append(line(ox, oy, ox, ay, sw=2))
    p.append(text(ax - 10, oy + 25, "напруга V (В)", size=11.5, anchor="end", color=MUTED))
    p.append(text(ox - 10, ay + 10, "струм I (А)", size=11.5, anchor="end", color=MUTED))

    # Рівні напруг на осі V
    p.append(text(190, oy + 18, "V_RWM", size=10, anchor="middle", color=MUTED))
    p.append(text(270, oy + 18, "V_BR", size=10, anchor="middle", color=MUTED))
    p.append(text(390, oy + 18, "V_CL (TVS)", size=10, anchor="middle", color=POS))
    p.append(text(520, oy + 18, "V_CL (MOV)", size=10, anchor="middle", color=FIELD))
    p.append(text(650, oy + 18, "V_trig (PVVM)", size=10, anchor="middle", color=NEG))

    p.append(line(190, oy - 4, 190, oy + 4, color=MUTED, sw=1.5))
    p.append(line(270, oy - 4, 270, oy + 4, color=MUTED, sw=1.5))
    p.append(line(390, oy - 4, 390, oy + 4, color=POS, sw=1.5))
    p.append(line(520, oy - 4, 520, oy + 4, color=FIELD, sw=1.5))
    p.append(line(650, oy - 4, 650, oy + 4, color=NEG, sw=1.5))

    # Зона робочої напруги (Standoff)
    p.append(rect(ox, ay + 20, 100, oy - ay - 20, fill="#f4f6f8", stroke="none"))
    p.append(text(140, 190, "Робоча зона\n(струм витоку\n< 1 мкА)", size=9.5, color=MUTED))

    # 1. Крива звичайного TVS (лавинний пробій: вертикальний підйом із малим нахилом R_dyn)
    tvs_pts = [
        (ox, oy),
        (190, oy - 2),
        (270, oy - 10),
        (320, 190),
        (365, 110),
        (390, ay + 25)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in tvs_pts), POS))
    p.append(text(340, 75, "TVS (лавина)", size=11, bold=True, color=POS))

    # 2. Крива Snapback SCR TVS (пробій на V_trig, відкат назад до V_hold, далі жорсткий підйом)
    snap_pts = [
        (ox, oy),
        (190, oy - 2),
        (290, oy - 12),
        (315, oy - 35),      # V_trig
        (220, oy - 85),      # Snapback до V_hold
        (245, 125),
        (275, ay + 25)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="4,3"/>'
             % (" ".join("%.1f,%.1f" % q for q in snap_pts), POS))
    p.append(text(240, 55, "TVS Snapback", size=10.5, bold=True, color=POS))

    # 3. Крива MOV (степенева, більш пологий нахил через вищий R_dyn)
    mov_pts = [
        (ox, oy),
        (220, oy - 3),
        (310, oy - 15),
        (410, 220),
        (475, 145),
        (520, ay + 25)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % q for q in mov_pts), FIELD))
    p.append(text(525, 75, "MOV (ZnO)", size=11, bold=True, color=FIELD))

    # 4. Крива PVVM (високий тригерний поріг ~200 В, далі зрив провідності)
    pvvm_pts = [
        (ox, oy),
        (300, oy - 1),
        (650, oy - 10),      # V_trig ~ 200 В
        (450, oy - 75),      # зрив у дуговий/польовий провідний стан
        (475, 125),
        (505, ay + 25)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,4"/>'
             % (" ".join("%.1f,%.1f" % q for q in pvvm_pts), NEG))
    p.append(text(670, 230, "PVVM (полімер)", size=10.5, bold=True, color=NEG))

    # Пояснення внизу (не перетинає вісь V)
    p.append(fitbox(100, 360, 620, 38,
                    "Динамічний опір R_dyn = ΔV / ΔI задає нахил кривої: малий опір TVS забезпечує мінімальну V_CL",
                    size=10.5, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'clamping-iv-curves.svg'), W, H, *p,
           title="Вольт-амперні характеристики TVS, Snapback-TVS, MOV та PVVM")


def fig_hybrid_coordination_cascade():
    """Трирівневий каскад захисту: GDT (грубий) + дросель розв'язки + MOV (середній) + TVS (тонкий)."""
    W, H = 820, 420
    p = []

    y_line = 110
    y_gnd = 280
    x_in = 60
    x_out = 760

    # Головні шини
    p.append(line(x_in, y_line, x_out, y_line, sw=3))
    p.append(line(x_in, y_gnd, x_out, y_gnd, color=FIELD, sw=3))
    p.append(text(x_in - 5, y_line - 12, "Лінія (Вхід від роз'єму)", size=11, anchor="start", bold=True))
    p.append(text(x_in - 5, y_gnd + 22, "Земля (GND / PE)", size=11, anchor="start", color=FIELD, bold=True))
    p.append(text(x_out + 5, y_line - 12, "До входу IC", size=11, anchor="end", color=POS, bold=True))

    # Ступінь 1: GDT
    x_gdt = 170
    p.append(line(x_gdt, y_line, x_gdt, y_gnd, color=NEG, sw=2.5))
    p.append(circle(x_gdt, 195, 24, fill="#eaf2fd", stroke=NEG, sw=2))
    p.append(text(x_gdt, 190, "GDT", size=11.5, bold=True, color=NEG))
    p.append(text(x_gdt, 206, "1-й ступінь", size=9.5, color=NEG))
    p.append(fitbox(x_gdt - 65, 310, 130, 42, "Скидає 90-95% енергії\n(кілоампери в дугу)\nt_resp ≈ 50-100 нс", size=9.5, fill=FILL, stroke=NEG))

    # Елемент координації 1: L1 / R1
    x_l1 = 285
    p.append(rect(x_l1 - 25, y_line - 14, 50, 28, fill="#ffffff", stroke=LINE, rx=4, sw=1.8))
    p.append(text(x_l1, y_line + 4, "L_коорд", size=10, bold=True))
    p.append(text(x_l1, y_line - 20, "ΔV = L·(dI/dt)", size=9.5, color=MUTED))

    # Ступінь 2: MOV
    x_mov = 400
    p.append(line(x_mov, y_line, x_mov, y_gnd, color=FIELD, sw=2.5))
    p.append(rect(x_mov - 18, 175, 36, 40, fill="#eef7f0", stroke=FIELD, rx=4, sw=2))
    p.append(text(x_mov, 192, "MOV", size=11.5, bold=True, color=FIELD))
    p.append(text(x_mov, 206, "2-й ступінь", size=9.5, color=FIELD))
    p.append(fitbox(x_mov - 65, 310, 130, 42, "Поглинає залишок сплеску\n(джоулі, V_cl ≈ 100-300 В)\nt_resp ≈ 1-5 нс", size=9.5, fill=FILL, stroke=FIELD))

    # Елемент координації 2: R_розв'язки
    x_r2 = 515
    p.append(rect(x_r2 - 22, y_line - 12, 44, 24, fill="#ffffff", stroke=LINE, rx=4, sw=1.8))
    p.append(text(x_r2, y_line + 4, "R_розв", size=10, bold=True))
    p.append(text(x_r2, y_line - 20, "1…5 Ом", size=9.5, color=MUTED))

    # Ступінь 3: TVS
    x_tvs = 630
    p.append(line(x_tvs, y_line, x_tvs, y_gnd, color=POS, sw=2.5))
    p.append(rect(x_tvs - 18, 175, 36, 40, fill="#fdecea", stroke=POS, rx=4, sw=2))
    p.append(text(x_tvs, 192, "TVS", size=11.5, bold=True, color=POS))
    p.append(text(x_tvs, 206, "3-й ступінь", size=9.5, color=POS))
    p.append(fitbox(x_tvs - 65, 310, 130, 42, "Точний жорсткий затиск\n(V_cl < V_max логіки)\nt_resp < 1 нс", size=9.5, fill=FILL, stroke=POS))

    # Напрямок струму та затримки
    p.append(arrow(110, y_line - 28, 160, y_line - 28, color=POS, sw=2))
    p.append(text(135, y_line - 36, "I_surge", size=10, color=POS, bold=True))

    p.append(fitbox(150, 368, 520, 32,
                    "Механізм взаємодії: TVS фіксує фронт наносекунд -> L_коорд створює спад напруги -> запалює GDT",
                    size=10.5, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'hybrid-coordination-cascade.svg'), W, H, *p,
           title="Багаторівневий каскад захисту GDT + MOV + TVS з елементами координації")


def fig_highspeed_layout_rules():
    """Правила трасування ESD-захисту на швидких шинах: пряме проходження vs паразитні відгалуження (stubs)."""
    W, H = 820, 380
    p = []

    # Ліворуч: Неправильно (Stub layout)
    lx = 50
    p.append(rect(lx, 40, 340, 280, rx=8, fill="#fff", stroke=POS, sw=2))
    p.append(text(lx + 170, 65, "НЕПРАВИЛЬНО: Т-подібний Stub", size=13, bold=True, color=POS))

    # Головна лінія
    p.append(line(lx + 30, 130, lx + 310, 130, sw=2.8))
    p.append(text(lx + 30, 115, "Роз'єм", size=10.5, anchor="start", color=MUTED))
    p.append(text(lx + 310, 115, "До IC PHY", size=10.5, anchor="end", color=MUTED))

    # Відгалуження (stub) до TVS
    p.append(line(lx + 170, 130, lx + 170, 210, color=POS, sw=2.5, dash="3,3"))
    p.append(rect(lx + 150, 210, 40, 30, fill="#fdecea", stroke=POS, rx=4))
    p.append(text(lx + 170, 228, "TVS", size=10.5, bold=True, color=POS))
    p.append(line(lx + 170, 240, lx + 170, 270, color=MUTED, sw=2))
    p.append(text(lx + 170, 285, "довгий GND-провід", size=9.5, color=POS))

    p.append(fitbox(lx + 15, 145, 140, 34, "L_stub ~ 5-10 нГн\nΔV = L·(dI/dt) = 150 В!", size=9.5, fill=FILL, stroke=POS))

    # Праворуч: Правильно (Flow-through package)
    rx = 430
    p.append(rect(rx, 40, 340, 280, rx=8, fill="#fff", stroke=FIELD, sw=2))
    p.append(text(rx + 170, 65, "ПРАВИЛЬНО: Flow-Through (без відгалужень)", size=13, bold=True, color=FIELD))

    # Лінія проходить прямо крізь виводи TVS
    p.append(line(rx + 30, 140, rx + 140, 140, sw=2.8))
    p.append(rect(rx + 140, 120, 60, 40, fill="#eef7f0", stroke=FIELD, rx=4))
    p.append(text(rx + 170, 144, "TVS", size=11, bold=True, color=FIELD))
    p.append(line(rx + 200, 140, rx + 310, 140, sw=2.8))

    p.append(text(rx + 30, 115, "Роз'єм", size=10.5, anchor="start", color=MUTED))
    p.append(text(rx + 310, 115, "До IC PHY", size=10.5, anchor="end", color=MUTED))

    # Прямі перехідні отвори на суцільний полігон землі (Kelvin GND)
    p.append(line(rx + 170, 160, rx + 170, 200, color=FIELD, sw=3))
    p.append(circle(rx + 170, 210, 6, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(rx + 170, 235, "Via прямо під падом в GND-полігон", size=9.5, bold=True, color=FIELD))
    p.append(fitbox(rx + 20, 250, 300, 26, "L_parasitic < 0.2 нГн, узгоджений імпеданс 90/100 Ом", size=9.5, fill=FILL, stroke=FIELD))

    # Підсумок унизу
    p.append(fitbox(100, 335, 620, 30,
                    "На швидкостях USB4/PCIe навіть 2 мм відгалуження спотворюють імпеданс і пропускають індуктивний сплеск на IC",
                    size=10.5, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'highspeed-layout-rules.svg'), W, H, *p,
           title="Правила розведення ESD-захисту на швидкісних лініях друкованої плати")


if __name__ == '__main__':
    fig_esd_threat_waveform()
    fig_suppressor_mechanisms()
    fig_clamping_iv_curves()
    fig_hybrid_coordination_cascade()
    fig_highspeed_layout_rules()
    print("ok")
