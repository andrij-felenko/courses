# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. transient-spikes-vs-hysteresis: імпульсні викиди крізь поріг гістерезису ──
def fig_transient_spikes_vs_hysteresis():
    W, H = 800, 420
    p = []

    p.append(text(W / 2, 25, "Імпульсна завада крізь амплітудний гістерезис і часова кваліфікація", size=13, bold=True))

    # Секція 1: Аналоговий сигнал із шумом і спайком
    ox, oy = 100, 55
    gw, gh = 660, 110

    p.append(rect(ox, oy, gw, gh, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=4))
    p.append(text(ox - 10, oy + 25, "V_high (4.0 В)", size=10, color=POS, anchor="end", bold=True))
    p.append(text(ox - 10, oy + 75, "V_low (3.2 В)", size=10, color=NEG, anchor="end", bold=True))
    p.append(line(ox, oy + 25, ox + gw, oy + 25, color=POS, sw=1.2, dash="4 3"))
    p.append(line(ox, oy + 75, ox + gw, oy + 75, color=NEG, sw=1.2, dash="4 3"))

    # Траєкторія аналогового сигналу
    sig_pts = [
        (ox, oy + 90), (ox + 70, oy + 88), (ox + 140, oy + 92),
        (ox + 190, oy + 90), (ox + 205, oy + 12), (ox + 215, oy + 10), (ox + 230, oy + 90),
        (ox + 300, oy + 88), (ox + 370, oy + 92),
        (ox + 420, oy + 80), (ox + 450, oy + 18), (ox + 520, oy + 16), (ox + 590, oy + 18), (ox + gw, oy + 17)
    ]
    path_d = ["M %.1f %.1f" % sig_pts[0]]
    for x, y in sig_pts[1:]:
        path_d.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_d), INK))

    # Позначення імпульсного спайку
    p.append(rect(ox + 195, oy + 2, 45, gh - 4, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(ox + 217, oy + gh + 14, "Спайк 15 мс", size=9, color=POS, bold=True))

    # Позначення справжнього перегріву
    p.append(rect(ox + 440, oy + 2, 200, gh - 4, fill="#e6fffa", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(ox + 540, oy + gh + 14, "Справжній перегрів (> 500 мс)", size=9, color=FIELD, bold=True))

    # Секція 2: Вихід чистого амплітудного гістерезису
    oy2 = 205
    gh2 = 60
    p.append(rect(ox, oy2, gw, gh2, fill="#fffaf0", stroke="#d0d7de", sw=1.2, rx=4))
    p.append(text(ox - 10, oy2 + 25, "Лише", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy2 + 42, "гістерезис", size=10, color=POS, anchor="end", bold=True))

    hyst_pts = [
        (ox, oy2 + 45), (ox + 205, oy2 + 45), (ox + 205, oy2 + 15), (ox + 230, oy2 + 15),
        (ox + 230, oy2 + 45), (ox + 450, oy2 + 45), (ox + 450, oy2 + 15), (ox + gw, oy2 + 15)
    ]
    path_h = ["M %.1f %.1f" % hyst_pts[0]]
    for x, y in hyst_pts[1:]:
        path_h.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_h), POS))
    p.append(text(ox + 217, oy2 + 55, "Хибний пуск!", size=9, color=POS, bold=True))

    # Секція 3: Вихід із часовою кваліфікацією
    oy3 = 300
    p.append(rect(ox, oy3, gw, gh2, fill="#f0fff4", stroke="#d0d7de", sw=1.2, rx=4))
    p.append(text(ox - 10, oy3 + 25, "Гістерезис +", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy3 + 42, "T_qualify", size=10, color=FIELD, anchor="end", bold=True))

    qual_pts = [
        (ox, oy3 + 45), (ox + 530, oy3 + 45), (ox + 530, oy3 + 15), (ox + gw, oy3 + 15)
    ]
    path_q = ["M %.1f %.1f" % qual_pts[0]]
    for x, y in qual_pts[1:]:
        path_q.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_q), FIELD))

    p.append(circle(ox + 217, oy3 + 45, 5, fill="#dcfce7", stroke=FIELD, sw=1.5))
    p.append(text(ox + 217, oy3 + 55, "Спайк проігноровано", size=9, color=FIELD, bold=True))

    p.append(line(ox + 450, oy3 + 20, ox + 530, oy3 + 20, color=MUTED, sw=1.5))
    p.append(line(ox + 450, oy3 + 15, ox + 450, oy3 + 25, color=MUTED, sw=1.5))
    p.append(line(ox + 530, oy3 + 15, ox + 530, oy3 + 25, color=MUTED, sw=1.5))
    p.append(text(ox + 490, oy3 + 32, "T_qualify", size=9, color=MUTED, bold=True))
    p.append(text(ox + 600, oy3 + 55, "Стійка дія", size=9, color=FIELD, bold=True))

    p.append(text(W / 2, 395, "Часова кваліфікація відсікає короткочасні викиди, на яких помиляється чистий амплітудний поріг",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "transient-spikes-vs-hysteresis.svg"), W, H, *p,
           title="Імпульсна завада крізь амплітудний гістерезис і часова кваліфікація")


# ── 2. dwell-time-protection: захист від частих перемикань (T_min_on, T_min_off) ─
def fig_dwell_time_protection():
    W, H = 820, 420
    p = []

    p.append(text(W / 2, 25, "Мінімальний час перебування в стані (Minimum Dwell Time)", size=13, bold=True))

    ox, oy = 110, 55
    gw, gh = 670, 75

    # 1. Вхідний запит (Demand Signal) із частими перемиканнями
    p.append(rect(ox, oy, gw, gh, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=4))
    p.append(text(ox - 10, oy + 32, "Вхідний", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy + 48, "запит (Demand)", size=10, color=INK, anchor="end", bold=True))

    dem_pts = [
        (ox, oy + 55), (ox + 50, oy + 55), (ox + 50, oy + 20), (ox + 90, oy + 20),
        (ox + 90, oy + 55), (ox + 130, oy + 55), (ox + 130, oy + 20), (ox + 280, oy + 20),
        (ox + 280, oy + 55), (ox + 320, oy + 55), (ox + 320, oy + 20), (ox + 480, oy + 20),
        (ox + 480, oy + 55), (ox + gw, oy + 55)
    ]
    path_dem = ["M %.1f %.1f" % dem_pts[0]]
    for x, y in dem_pts[1:]:
        path_dem.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(path_dem), INK))

    # 2. Небезпечний вихід без Dwell Time (Short-cycling)
    oy2 = 155
    p.append(rect(ox, oy2, gw, gh, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(ox - 10, oy2 + 30, "Без захисту", size=10, color=POS, anchor="end"))
    p.append(text(ox - 10, oy2 + 48, "(Дребезг реле)", size=10, color=POS, anchor="end", bold=True))

    path_bad = ["M %.1f %.1f" % dem_pts[0]]
    for x, y in dem_pts[1:]:
        path_bad.append("L %.1f %.1f" % (x, y + 100))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path_bad), POS))
    p.append(text(ox + 70, oy2 + 65, "Пуск 40 мс!", size=9, color=POS, bold=True))
    p.append(text(ox + 110, oy2 + 65, "Стоп 40 мс!", size=9, color=POS, bold=True))
    p.append(text(ox + 300, oy2 + 65, "Короткий цикл!", size=9, color=POS, bold=True))

    # 3. Вихід із Dwell Time (T_min_on = 150 px, T_min_off = 120 px)
    oy3 = 260
    gh3 = 95
    p.append(rect(ox, oy3, gw, gh3, fill="#f0fff4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(ox - 10, oy3 + 40, "Із захистом", size=10, color=FIELD, anchor="end"))
    p.append(text(ox - 10, oy3 + 58, "Dwell Timers", size=10, color=FIELD, anchor="end", bold=True))

    dwell_pts = [
        (ox, oy3 + 65), (ox + 50, oy3 + 65), (ox + 50, oy3 + 30), (ox + 280, oy3 + 30),
        (ox + 280, oy3 + 65), (ox + 400, oy3 + 65), (ox + 400, oy3 + 30), (ox + 550, oy3 + 30),
        (ox + 550, oy3 + 65), (ox + gw, oy3 + 65)
    ]
    path_dw = ["M %.1f %.1f" % dwell_pts[0]]
    for x, y in dwell_pts[1:]:
        path_dw.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_dw), FIELD))

    # Позначення блоків T_min_on і T_min_off
    p.append(rect(ox + 50, oy3 + 8, 150, 16, fill="#bbf7d0", stroke=FIELD, sw=1, rx=2))
    p.append(text(ox + 125, oy3 + 20, "T_min_on (гарантований хід)", size=9, color="#14532d", bold=True))

    p.append(rect(ox + 280, oy3 + 74, 120, 16, fill="#fed7aa", stroke="#ea580c", sw=1, rx=2))
    p.append(text(ox + 340, oy3 + 86, "T_min_off (вирівнювання тиску)", size=9, color="#7c2d12", bold=True))

    p.append(rect(ox + 400, oy3 + 8, 150, 16, fill="#bbf7d0", stroke=FIELD, sw=1, rx=2))
    p.append(text(ox + 475, oy3 + 20, "T_min_on (утримання)", size=9, color="#14532d", bold=True))

    # Пунктирні лінії зв'язку заборон
    p.append(line(ox + 90, oy + 55, ox + 90, oy3 + 65, color=MUTED, sw=1, dash="2 2"))
    p.append(text(ox + 95, oy3 + 50, "Спад ігноровано", size=9, color=FIELD))

    p.append(line(ox + 320, oy + 20, ox + 320, oy3 + 65, color=MUTED, sw=1, dash="2 2"))
    p.append(text(ox + 325, oy3 + 50, "Пуск відкладено", size=9, color="#ea580c"))

    p.append(text(W / 2, 395, "Dwell-таймери гарантують повне відпрацювання технологічного циклу та захист від частих пусків",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dwell-time-protection.svg"), W, H, *p,
           title="Мінімальний час перебування в стані (Minimum Dwell Time)")


# ── 3. qualification-symmetric-asymmetric: симетрична проти несиметричної кваліфікації ─
def fig_qualification_modes():
    W, H = 800, 390
    p = []

    p.append(text(W / 2, 25, "Симетрична та несиметрична часова кваліфікація подій", size=13, bold=True))

    # Ліва колонка: Симетричний антидребезг (T_on == T_off)
    cx1, cw = 40, 345
    p.append(rect(cx1, 50, cw, 295, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(cx1 + cw / 2, 75, "Симетрична кваліфікація", size=12, bold=True, color=INK))
    p.append(text(cx1 + cw / 2, 94, "T_qualify_on = T_qualify_off = T_deb", size=10, color=MUTED))

    gx1, gy1 = cx1 + 20, 110
    gw1 = cw - 40
    p.append(rect(gx1, gy1, gw1, 48, fill="#ffffff", stroke="#d0d7de", sw=1, rx=3))
    p.append(text(gx1 + 5, gy1 + 16, "Сирий сигнал (кнопка)", size=9, color=MUTED, anchor="start"))
    btn_pts = [
        (gx1, gy1 + 38), (gx1 + 40, gy1 + 38), (gx1 + 43, gy1 + 10), (gx1 + 48, gy1 + 38),
        (gx1 + 52, gy1 + 10), (gx1 + 56, gy1 + 38), (gx1 + 60, gy1 + 10), (gx1 + 160, gy1 + 10),
        (gx1 + 165, gy1 + 38), (gx1 + 170, gy1 + 10), (gx1 + 175, gy1 + 38), (gx1 + gw1, gy1 + 38)
    ]
    pb = ["M %.1f %.1f" % btn_pts[0]]
    for x, y in btn_pts[1:]: pb.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pb), INK))

    gy1_out = gy1 + 65
    p.append(rect(gx1, gy1_out, gw1, 48, fill="#ffffff", stroke="#d0d7de", sw=1, rx=3))
    p.append(text(gx1 + 5, gy1_out + 16, "Очищене рішення", size=9, color=FIELD, anchor="start", bold=True))
    btn_out = [
        (gx1, gy1_out + 38), (gx1 + 90, gy1_out + 38), (gx1 + 90, gy1_out + 10),
        (gx1 + 205, gy1_out + 10), (gx1 + 205, gy1_out + 38), (gx1 + gw1, gy1_out + 38)
    ]
    pbo = ["M %.1f %.1f" % btn_out[0]]
    for x, y in btn_out[1:]: pbo.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pbo), FIELD))

    p.append(line(gx1 + 60, gy1_out + 20, gx1 + 90, gy1_out + 20, color=MUTED, sw=1.2))
    p.append(text(gx1 + 75, gy1_out + 30, "T_on", size=9, color=MUTED))
    p.append(line(gx1 + 175, gy1_out + 20, gx1 + 205, gy1_out + 20, color=MUTED, sw=1.2))
    p.append(text(gx1 + 190, gy1_out + 30, "T_off", size=9, color=MUTED))

    p.append(mtext(cx1 + cw / 2, 258, "Застосування: клавіші HMI, кінцевики.\nОбидва переходи фільтруються однаково\n(типово 20–50 мс).", size=10, lh=1.3))

    # Права колонка: Несиметрична кваліфікація (T_trip << T_recover)
    cx2 = 415
    p.append(rect(cx2, 50, cw, 295, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(cx2 + cw / 2, 75, "Несиметрична кваліфікація", size=12, bold=True, color=INK))
    p.append(text(cx2 + cw / 2, 94, "T_trip (швидко) ≠ T_recover (повільно)", size=10, color=POS, bold=True))

    gx2, gy2 = cx2 + 20, 110
    p.append(rect(gx2, gy2, gw1, 48, fill="#ffffff", stroke="#d0d7de", sw=1, rx=3))
    p.append(text(gx2 + 5, gy2 + 16, "Аварійний сигнал (тиск мастила)", size=9, color=MUTED, anchor="start"))
    oil_pts = [
        (gx2, gy2 + 38), (gx2 + 40, gy2 + 38), (gx2 + 40, gy2 + 10), (gx2 + 130, gy2 + 10),
        (gx2 + 130, gy2 + 38), (gx2 + gw1, gy2 + 38)
    ]
    po = ["M %.1f %.1f" % oil_pts[0]]
    for x, y in oil_pts[1:]: po.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(po), INK))

    gy2_out = gy2 + 65
    p.append(rect(gx2, gy2_out, gw1, 48, fill="#ffffff", stroke="#d0d7de", sw=1, rx=3))
    p.append(text(gx2 + 5, gy2_out + 16, "Статус аварії (FAULT)", size=9, color=POS, anchor="start", bold=True))
    oil_out = [
        (gx2, gy2_out + 38), (gx2 + 55, gy2_out + 38), (gx2 + 55, gy2_out + 10),
        (gx2 + 230, gy2_out + 10), (gx2 + 230, gy2_out + 38), (gx2 + gw1, gy2_out + 38)
    ]
    poo = ["M %.1f %.1f" % oil_out[0]]
    for x, y in oil_out[1:]: poo.append("L %.1f %.1f" % (x, y))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(poo), POS))

    p.append(line(gx2 + 40, gy2_out + 20, gx2 + 55, gy2_out + 20, color=POS, sw=1.2))
    p.append(text(gx2 + 47, gy2_out + 30, "T_trip", size=9, color=POS, bold=True))

    p.append(line(gx2 + 130, gy2_out + 20, gx2 + 230, gy2_out + 20, color=FIELD, sw=1.2))
    p.append(text(gx2 + 180, gy2_out + 30, "T_recover (стабілізація)", size=9, color=FIELD, bold=True))

    p.append(mtext(cx2 + cw / 2, 258, "Застосування: захист двигунів і тиску.\nШвидке відсікання аварії (T_trip = 100 мс),\nале тривала стабілізація (T_recover = 10 с).", size=10, lh=1.3))

    p.append(text(W / 2, 365, "Симетричний фільтр підходить для HMI; несиметричний — стандарт промислової безпеки",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "qualification-symmetric-asymmetric.svg"), W, H, *p,
           title="Симетрична та несиметрична часова кваліфікація подій")


# ── 4. fsm-architecture-time-guards: конвеєр обробки та автомат із таймерами ─────
def fig_fsm_architecture_time_guards():
    W, H = 800, 400
    p = []

    p.append(text(W / 2, 25, "Архітектурний конвеєр: кондиціювання, FSM та охоронні таймери", size=13, bold=True))

    # 1. Блок сенсорів
    bx1, by, bw, bh = 25, 65, 145, 195
    p.append(rect(bx1, by, bw, bh, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(bx1 + bw / 2, by + 22, "1. Сирі сигнали", size=11, bold=True, color=INK))
    p.append(rect(bx1 + 10, by + 40, bw - 20, 32, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(text(bx1 + bw / 2, by + 60, "АЦП / Термістор", size=9, color=INK))
    p.append(rect(bx1 + 10, by + 85, bw - 20, 32, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(text(bx1 + bw / 2, by + 105, "Давач тиску", size=9, color=INK))
    p.append(rect(bx1 + 10, by + 130, bw - 20, 32, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    p.append(text(bx1 + bw / 2, by + 150, "Аварійна кнопка", size=9, color=POS, bold=True))

    p.append(arrow(bx1 + bw, by + 80, bx1 + bw + 35, by + 80, color=INK, sw=1.8))
    p.append(text(bx1 + bw + 18, by + 72, "Сирі", size=9, color=MUTED))

    # 2. Шар кондиціювання (Гістерезис + Time Qualification)
    bx2 = bx1 + bw + 35
    bw2 = 225
    p.append(rect(bx2, by, bw2, bh, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 22, "2. Кондиціювання", size=11, bold=True, color="#0369a1"))

    p.append(rect(bx2 + 12, by + 38, bw2 - 24, 52, fill="#ffffff", stroke="#38bdf8", sw=1, rx=4))
    p.append(text(bx2 + bw2 / 2, by + 56, "Амплітудний поріг", size=9, bold=True, color=INK))
    p.append(text(bx2 + bw2 / 2, by + 72, "V_high / V_low (Шмітт)", size=9, color=MUTED))

    p.append(rect(bx2 + 12, by + 98, bw2 - 24, 75, fill="#ffffff", stroke="#38bdf8", sw=1, rx=4))
    p.append(text(bx2 + bw2 / 2, by + 118, "Часова кваліфікація", size=9, bold=True, color=FIELD))
    p.append(text(bx2 + bw2 / 2, by + 135, "now - t_start >= T_qualify", size=9, color=INK))
    p.append(text(bx2 + bw2 / 2, by + 152, "Фільтрація спайків", size=9, color=MUTED))

    p.append(arrow(bx2 + bw2, by + 100, bx2 + bw2 + 35, by + 100, color=FIELD, sw=2))
    p.append(text(bx2 + bw2 + 18, by + 90, "Події", size=9, color=FIELD, bold=True))

    # 3. Скінченний автомат FSM з Dwell Timers
    bx3 = bx2 + bw2 + 35
    bw3 = 310
    p.append(rect(bx3, by, bw3, bh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(bx3 + bw3 / 2, by + 22, "3. FSM + Dwell Guard Timers", size=11, bold=True, color="#15803d"))

    # Стани всередині FSM
    sx, sy = bx3 + 18, by + 45
    p.append(rect(sx, sy, 120, 52, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=5))
    p.append(text(sx + 60, sy + 22, "STATE_OFF", size=9, bold=True, color=INK))
    p.append(text(sx + 60, sy + 38, "T_min_off guard", size=9, color="#ea580c"))

    sx2, sy2 = bx3 + 170, by + 45
    p.append(rect(sx2, sy2, 120, 52, fill="#ffffff", stroke="#16a34a", sw=1.5, rx=5))
    p.append(text(sx2 + 60, sy2 + 22, "STATE_RUN", size=9, bold=True, color=INK))
    p.append(text(sx2 + 60, sy2 + 38, "T_min_on guard", size=9, color=FIELD))

    # Переходи
    p.append(arrow(sx + 120, sy + 15, sx2, sy + 15, color=FIELD, sw=1.5))
    p.append(text(bx3 + 145, sy + 10, "start", size=9, color=FIELD))

    p.append(arrow(sx2, sy + 37, sx + 120, sy + 37, color=MUTED, sw=1.5))
    p.append(text(bx3 + 145, sy + 47, "stop", size=9, color=MUTED))

    # Аварійний стан
    sy3 = by + 125
    p.append(rect(bx3 + 95, sy3, 125, 48, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    p.append(text(bx3 + 157, sy3 + 22, "STATE_FAULT", size=9, bold=True, color=POS))
    p.append(text(bx3 + 157, sy3 + 38, "T_recover guard", size=9, color=POS))

    # Аварійний обхід (E-Stop bypass)
    p.append(line(bx1 + bw - 10, by + 145, bx1 + bw + 15, by + 245, color=POS, sw=1.8, dash="3 3"))
    p.append(line(bx1 + bw + 15, by + 245, bx3 + 157, by + 245, color=POS, sw=1.8, dash="3 3"))
    p.append(arrow(bx3 + 157, by + 245, bx3 + 157, sy3 + 48, color=POS, sw=1.8))
    p.append(text(bx2 + bw2 / 2, by + 235, "Аварійний обхід (E-Stop миттєво перериває Dwell Time)", size=9, color=POS, bold=True))

    # Нижня панель підсумку
    p.append(rect(25, 275, W - 50, 70, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(45, 300, "• Вхідний рівень (Кваліфікація): захищає від хибних переходів через короткочасні імпульси.", size=9, anchor="start", color=INK))
    p.append(text(45, 320, "• Рівень стану (Dwell Time): захищає фізичний агрегат від занадто частих перемикань.", size=9, anchor="start", color=INK))

    p.append(text(W / 2, 380, "Таймери кваліфікації фільтрують входи, а таймери утримання захищають інваріанти станів автомата",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fsm-architecture-time-guards.svg"), W, H, *p,
           title="Архітектурний конвеєр: кондиціювання, FSM та охоронні таймери")


if __name__ == "__main__":
    fig_transient_spikes_vs_hysteresis()
    fig_dwell_time_protection()
    fig_qualification_modes()
    fig_fsm_architecture_time_guards()
    print("Figures generated successfully in %s" % OUT)
