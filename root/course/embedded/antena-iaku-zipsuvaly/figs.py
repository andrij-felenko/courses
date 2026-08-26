# -*- coding: utf-8 -*-
"""Фігури до теми «Антена, яку зіпсували» (Antenna Detuning & VSWR Degradation).
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os

# 4 рівні вгору від root/course/embedded/antena-iaku-zipsuvaly до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COPPER = "#b9770e"
HOT    = "#c0392b"
COLD   = "#2457d6"
GREEN  = "#27ae60"
BODY   = "#8e44ad"
PLASTIC= "#d35400"

# ── 1. Зсув резонансної частоти антени (S11 Return Loss) ───────────────────
def fig_enclosure_detuning():
    W, H = 960, 480
    f = [
        text(W / 2, 28, "Діелектричний зсув резонансу: вільний простір проти корпусу й руки", size=17, bold=True),
        text(W / 2, 50, "висока проникність діелектрика (ABS εr≈3.0, тіло εr≈80) зміщує мінімум S11 вниз за межі робочої смуги",
             size=11.5, color=MUTED, italic=True)
    ]

    ox, oy = 110, 390
    gw, gh = 780, 300

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=4))

    # Горизонтальні лінії рівнів S11 (0, -5, -10, -15, -20, -25 дБ)
    for db, y_rel in [(0, 0), (-5, 50), (-10, 100), (-15, 150), (-20, 200), (-25, 250)]:
        y = oy - gh + y_rel + 20
        f.append(line(ox, y, ox + gw, y, color="#e5e7eb", sw=1, dash="4,4" if db != -10 else None))
        f.append(text(ox - 10, y + 4, f"{db} дБ", size=10.5, color=MUTED, anchor="end"))
        if db == -10:
            f.append(text(ox + gw - 8, y - 6, "поріг придатності (S11 ≤ -10 дБ, КСВ ≤ 1.92)", size=10, color=GREEN, anchor="end", bold=True))

    # Вертикальні лінії частоти (2.1 ... 2.6 ГГц)
    freqs = [2.1, 2.2, 2.3, 2.4, 2.44, 2.5, 2.6]
    for fr in freqs:
        x = ox + (fr - 2.1) / 0.5 * (gw - 40) + 20
        f.append(line(x, oy - gh, x, oy, color="#e5e7eb", sw=1))
        lbl = f"{fr:.2f}" if fr == 2.44 else f"{fr:.1f}"
        f.append(text(x, oy + 20, f"{lbl} ГГц", size=10.5, color=INK if fr != 2.44 else HOT, bold=(fr == 2.44)))

    # Виділення дозволеної смуги ISM 2.40 - 2.48 ГГц
    x_ism1 = ox + (2.40 - 2.1) / 0.5 * (gw - 40) + 20
    x_ism2 = ox + (2.4835 - 2.1) / 0.5 * (gw - 40) + 20
    f.append(rect(x_ism1, oy - gh + 20, x_ism2 - x_ism1, gh - 20, fill="#e8f8f0", stroke=GREEN, sw=1.2, rx=0))
    f.append(text((x_ism1 + x_ism2) / 2, oy - gh + 35, "Робоча смуга ISM (2.40-2.48 ГГц)", size=10, color=GREEN, bold=True))

    # Крива 1: Вільний простір (налаштована антена, мінімум на 2.44 ГГц, S11 = -24 дБ)
    # y = oy - gh + 20 + (-S11)*10
    pts_air = [
        (2.10, -1.0), (2.20, -2.5), (2.30, -5.5), (2.36, -9.5), (2.40, -15.0),
        (2.44, -24.0), (2.48, -14.5), (2.52, -8.0), (2.56, -4.0), (2.60, -2.0)
    ]
    path_air = []
    for fr, s11 in pts_air:
        px = ox + (fr - 2.1) / 0.5 * (gw - 40) + 20
        py = oy - gh + 20 + (-s11) * 10
        path_air.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(path_air)}" fill="none" stroke="{GREEN}" stroke-width="3"/>')

    # Крива 2: У пластиковому корпусі (ABS, зсув на 2.30 ГГц, на 2.44 ГГц S11 = -3.5 дБ)
    pts_box = [
        (2.10, -2.5), (2.18, -5.0), (2.24, -9.5), (2.30, -21.0), (2.36, -11.0),
        (2.40, -6.0), (2.44, -3.5), (2.48, -2.0), (2.54, -1.0), (2.60, -0.6)
    ]
    path_box = []
    for fr, s11 in pts_box:
        px = ox + (fr - 2.1) / 0.5 * (gw - 40) + 20
        py = oy - gh + 20 + (-s11) * 10
        path_box.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(path_box)}" fill="none" stroke="{PLASTIC}" stroke-width="3" stroke-dasharray="6,4"/>')

    # Крива 3: У руці оператора (потужне поглинання + сильний зсув на 2.18 ГГц, на 2.44 ГГц S11 = -1.8 дБ)
    pts_hand = [
        (2.10, -7.0), (2.18, -11.5), (2.24, -7.5), (2.30, -5.0), (2.36, -3.5),
        (2.40, -2.5), (2.44, -1.8), (2.48, -1.2), (2.54, -0.8), (2.60, -0.5)
    ]
    path_hand = []
    for fr, s11 in pts_hand:
        px = ox + (fr - 2.1) / 0.5 * (gw - 40) + 20
        py = oy - gh + 20 + (-s11) * 10
        path_hand.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(path_hand)}" fill="none" stroke="{BODY}" stroke-width="2.6" stroke-dasharray="3,3"/>')

    # Стрілка зсуву
    x_air_min = ox + (2.44 - 2.1) / 0.5 * (gw - 40) + 20
    x_box_min = ox + (2.30 - 2.1) / 0.5 * (gw - 40) + 20
    f.append(arrow(x_air_min - 10, oy - 30, x_box_min + 10, oy - 30, color=HOT, sw=2))
    f.append(text((x_air_min + x_box_min) / 2, oy - 42, "Δf = -140 МГц (зсув)", size=11, color=HOT, bold=True))

    # Легенда внизу
    leg_y = oy + 54
    f.append(line(ox + 40, leg_y, ox + 80, leg_y, color=GREEN, sw=3))
    f.append(text(ox + 90, leg_y + 4, "Вільний простір: узгоджено на 2.44 ГГц (S11 = -24 дБ, КСВ ≈ 1.1)", size=11, color=INK, anchor="start"))

    f.append(line(ox + 40, leg_y + 22, ox + 80, leg_y + 22, color=PLASTIC, sw=3, dash="6,4"))
    f.append(text(ox + 90, leg_y + 26, "У пластиковому корпусі: зсув на 2.30 ГГц (на 2.44 ГГц S11 = -3.5 дБ, КСВ ≈ 5.1)", size=11, color=INK, anchor="start"))

    f.append(line(ox + 40, leg_y + 44, ox + 80, leg_y + 44, color=BODY, sw=2.6, dash="3,3"))
    f.append(text(ox + 90, leg_y + 48, "Хват рукою: розладнання + поглинання водою (на 2.44 ГГц S11 = -1.8 дБ, КСВ ≈ 9.7)", size=11, color=INK, anchor="start"))

    return render(os.path.join(IMG, 'enclosure-detuning-shift.svg'), W, H, *f)


# ── 2. Ближнє реактивне поле та зони взаємодії ─────────────────────────────
def fig_reactive_near_field():
    W, H = 940, 470
    f = [
        text(W / 2, 28, "Зони електромагнітного поля антени та взаємодія з оточенням", size=17, bold=True),
        text(W / 2, 50, "реактивна зона накопичує енергію; будь-який діелектрик чи провідник у ній змінює власну ємність та індуктивність антени",
             size=11.5, color=MUTED, italic=True)
    ]

    cx, cy = 340, 260

    # Зони поля (концентричні кола навколо антени)
    # Дальня зона (Фраунгофера) r > 2D^2 / lambda
    f.append(f'<circle cx="{cx}" cy="{cy}" r="180" fill="#f4f6f8" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="6,6"/>')
    # Зона Френеля (ближня випромінювальна)
    f.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="#e8f0fe" stroke="{COLD}" stroke-width="1.6" stroke-dasharray="4,4"/>')
    # Реактивна ближня зона r < lambda / (2*pi) ≈ 20 мм на 2.4 ГГц
    f.append(circle(cx, cy, 65, fill="#fdecea", stroke=HOT, sw=2.2))

    # Антена в центрі
    f.append(rect(cx - 15, cy - 25, 30, 50, fill="#fff", stroke=COPPER, sw=2.5, rx=3))
    # Меандр на платі
    f.append(f'<path d="M {cx-8},{cy+18} v -10 h 16 v -8 h -16 v -8 h 16" fill="none" stroke="{COPPER}" stroke-width="2.2"/>')
    f.append(text(cx, cy + 38, "Антена", size=10, color=COPPER, bold=True))

    # Пояснення зон
    f.append(text(cx, cy - 72, "Реактивна ближня зона", size=11, color=HOT, bold=True))
    f.append(text(cx, cy - 86, "r < λ / 2π (≈ 20 мм на 2.4 ГГц)", size=10, color=HOT))

    f.append(text(cx, cy - 130, "Зона випромінювання (Френеля)", size=10.5, color=COLD, bold=True))
    f.append(text(cx, cy - 192, "Дальня зона випромінювання (Фраунгофера: r >> λ)", size=11, color=MUTED, bold=True))

    # Зовнішні об'єкти, що вторгаються в реактивну зону
    # 1. Стінка корпусу (ABS)
    wall_x = cx + 45
    f.append(rect(wall_x, cy - 100, 18, 200, fill="#faebd7", stroke=PLASTIC, sw=2, rx=2))
    f.append(text(wall_x + 9, cy - 110, "Стінка ABS", size=10.5, color=PLASTIC, bold=True))
    f.append(text(wall_x + 9, cy - 124, "εr ≈ 3.0", size=10, color=PLASTIC))

    # 2. LiPo батарея знизу
    bat_y = cy + 48
    f.append(rect(cx - 90, bat_y, 110, 45, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    f.append(text(cx - 35, bat_y + 22, "LiPo Батарея", size=10.5, color="#1e293b", bold=True))
    f.append(text(cx - 35, bat_y + 36, "(метал / екран)", size=9.5, color=MUTED))

    # 3. Рука оператора праворуч від пластику
    hand_x = wall_x + 24
    f.append(rect(hand_x, cy - 70, 35, 140, fill="#f3e8ff", stroke=BODY, sw=2, rx=8))
    f.append(text(hand_x + 17, cy - 80, "Палець / Рука", size=10.5, color=BODY, bold=True))
    f.append(text(hand_x + 17, cy - 94, "εr ≈ 80, σ ≈ 1.5 См/м", size=9.5, color=BODY))

    # Права інформаційна панель
    px, py, pw = 580, 80, 330
    f.append(rect(px, py, pw, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(px + pw / 2, py + 26, "Що відбувається в реактивній зоні:", size=13, color=INK, bold=True))

    items = [
        ("Пластик корпусу (εr = 2.5–3.5):", HOT),
        ("Концентрує електричне поле E.", INK),
        ("Збільшує еквівалентну ємність C_ant.", INK),
        ("Наслідок: зсув резонансу вниз на 50–200 МГц.", PLASTIC),
        ("", INK),
        ("Метал / Батарея / Дисплей:", HOT),
        ("Гранична умова: E_тангенційне = 0.", INK),
        ("Закорочує лінії E, спотворює діаграму.", INK),
        ("Наслідок: глуха тіньова зона до -25 дБ.", "#c0392b"),
        ("", INK),
        ("Тіло / Рука оператора (εr ≈ 80):", HOT),
        ("Висока ємність + провідність тканин.", INK),
        ("Поглинає до 85% енергії у вигляді тепла.", BODY),
        ("Наслідок: катастрофічне падіння ККД антени.", BODY),
    ]

    cur_y = py + 54
    for it_text, col in items:
        if not it_text:
            cur_y += 6
            continue
        is_b = col in (HOT, PLASTIC, BODY, "#c0392b") and ("(" in it_text or "Наслідок" in it_text)
        f.append(text(px + 16, cur_y, it_text, size=11, color=col, anchor="start", bold=is_b))
        cur_y += 18

    return render(os.path.join(IMG, 'reactive-near-field-zones.svg'), W, H, *f)


# ── 3. Стояча хвиля, КСВ та відбиття потужності в PA ───────────────────────
def fig_vswr_power():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Хвильові процеси в лінії передачі та перегрів вихідного каскаду PA", size=17, bold=True),
        text(W / 2, 50, "неузгоджена антена відбиває частину енергії назад; інтерференція створює пучності напруги та перевантажує транзистор",
             size=11.5, color=MUTED, italic=True)
    ]

    # Ліва частина: Передавач PA -> Лінія 50 Ом -> Розладнана антена
    pa_x, pa_y, pa_w, pa_h = 60, 110, 140, 130
    f.append(rect(pa_x, pa_y, pa_w, pa_h, fill="#fee2e2", stroke=HOT, sw=2, rx=6))
    f.append(text(pa_x + pa_w / 2, pa_y + 30, "Вихідний каскад", size=12, color=HOT, bold=True))
    f.append(text(pa_x + pa_w / 2, pa_y + 48, "PA (Транзистор)", size=12, color=HOT, bold=True))
    f.append(text(pa_x + pa_w / 2, pa_y + 80, "P_вых = +20 дБм", size=11, color=INK))
    f.append(text(pa_x + pa_w / 2, pa_y + 98, "(100 мВт)", size=10.5, color=MUTED))

    # Антена праворуч
    ant_x, ant_y, ant_w, ant_h = 440, 110, 140, 130
    f.append(rect(ant_x, ant_y, ant_w, ant_h, fill="#fef3c7", stroke=COPPER, sw=2, rx=6))
    f.append(text(ant_x + ant_w / 2, ant_y + 30, "Розладнана антена", size=12, color=COPPER, bold=True))
    f.append(text(ant_x + ant_w / 2, ant_y + 50, "Z_L ≠ 50 Ом", size=12, color=HOT, bold=True))
    f.append(text(ant_x + ant_w / 2, ant_y + 80, "P_випр = 15 мВт", size=11, color=GREEN, bold=True))
    f.append(text(ant_x + ant_w / 2, ant_y + 98, "(КСВ = 5.8, втрати 8.2 дБ)", size=10, color=HOT))

    # Лінія передачі між ними
    line_y1 = pa_y + 45
    line_y2 = pa_y + 85
    f.append(rect(pa_x + pa_w, line_y1, ant_x - (pa_x + pa_w), line_y2 - line_y1, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=0))
    f.append(text((pa_x + pa_w + ant_x) / 2, line_y1 + 16, "Лінія 50 Ом", size=10.5, color="#475569", bold=True))

    # Стрілка прямої хвилі (Forward Power)
    f.append(arrow(pa_x + pa_w + 20, line_y1 - 18, ant_x - 20, line_y1 - 18, color=GREEN, sw=2.5))
    f.append(text((pa_x + pa_w + ant_x) / 2, line_y1 - 28, "Пряма хвиля P_fwd = 100 мВт (100%)", size=11, color=GREEN, bold=True))

    # Стрілка відбитої хвилі (Reflected Power)
    f.append(arrow(ant_x - 20, line_y2 + 22, pa_x + pa_w + 20, line_y2 + 22, color=HOT, sw=2.5))
    f.append(text((pa_x + pa_w + ant_x) / 2, line_y2 + 38, "Відбита хвиля P_refl = 50 мВт (50%) -> в PA!", size=11, color=HOT, bold=True))

    # Нижня частина: Стояча хвиля напруги (Інтерференція)
    wv_x, wv_y, wv_w, wv_h = 60, 275, 520, 180
    f.append(rect(wv_x, wv_y, wv_w, wv_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(wv_x + wv_w / 2, wv_y + 24, "Профіль напруги вздовж лінії при КСВ = 5.8", size=12.5, color=INK, bold=True))

    # Базова вісь
    mid_y = wv_y + 105
    f.append(line(wv_x + 30, mid_y, wv_x + wv_w - 30, mid_y, color="#94a3b8", sw=1, dash="4,4"))

    # Обвідна стоячої хвилі
    pts_env_top = []
    pts_env_bot = []
    import math
    for i in range(101):
        x_norm = i / 100.0
        theta = x_norm * 4 * math.pi
        v_env = math.sqrt(1 + 0.5 + 2 * 0.707 * math.cos(theta))
        px = wv_x + 40 + x_norm * (wv_w - 80)
        py_top = mid_y - v_env * 32
        py_bot = mid_y + v_env * 32
        pts_env_top.append(f"{px:.1f},{py_top:.1f}")
        pts_env_bot.append(f"{px:.1f},{py_bot:.1f}")

    f.append(f'<polyline points="{" ".join(pts_env_top)}" fill="none" stroke="{HOT}" stroke-width="2.5"/>')
    f.append(f'<polyline points="{" ".join(pts_env_bot)}" fill="none" stroke="{COLD}" stroke-width="1.8" stroke-dasharray="3,3"/>')

    # Позначки V_max та V_min
    f.append(text(wv_x + 130, mid_y - 62, "V_max = V_fwd · (1 + |Γ|)", size=10.5, color=HOT, bold=True))
    f.append(text(wv_x + 225, mid_y + 24, "V_min", size=10, color=COLD, bold=True))
    f.append(text(wv_x + wv_w / 2, wv_y + wv_h - 12, "КСВ = V_max / V_min = 1.707 / 0.293 ≈ 5.8", size=11, color=HOT, bold=True))

    # Права таблиця: Наслідки різного КСВ для виробу
    tx, ty, tw, th = 605, 110, 315, 345
    f.append(rect(tx, ty, tw, th, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(tx + tw / 2, ty + 24, "Співвідношення КСВ, S11 та втрат", size=12.5, color=INK, bold=True))

    rows = [
        ("КСВ", "S11 (дБ)", "P_відб", "Стан тракту"),
        ("1.05", "-32 дБ", "0.06%", "Ідеально (лабораторія)"),
        ("1.30", "-17.7 дБ", "1.7%", "Відмінно для пристрою"),
        ("1.92", "-10.0 дБ", "10.0%", "Гранично допустимо"),
        ("3.00", "-6.0 дБ", "25.0%", "Втрата 50% дальності"),
        ("5.83", "-3.0 дБ", "50.0%", "Перегрів PA, зрив лінка"),
        ("10.0", "-1.7 дБ", "67.0%", "Загроза пробою PA"),
    ]

    r_y = ty + 54
    for i, (c1, c2, c3, c4) in enumerate(rows):
        is_head = (i == 0)
        bg_c = "#f1f5f9" if is_head else ("#fee2e2" if i >= 5 else "#ffffff")
        if is_head or i >= 5:
            f.append(rect(tx + 8, r_y - 14, tw - 16, 24, fill=bg_c, stroke="none", rx=3))
        col = INK if not is_head else "#0f172a"
        if i >= 5:
            col = HOT
        f.append(text(tx + 28, r_y + 3, c1, size=10.5, color=col, bold=(is_head or i >= 5)))
        f.append(text(tx + 82, r_y + 3, c2, size=10, color=col, bold=is_head))
        f.append(text(tx + 138, r_y + 3, c3, size=10, color=col, bold=(is_head or i >= 5)))
        f.append(text(tx + tw - 16, r_y + 3, c4, size=9.5, color=col, anchor="end", bold=(is_head or i >= 5)))
        r_y += 28

    f.append(text(tx + tw / 2, ty + th - 18, "При КСВ > 5 транзистор розсіює відбиту хвилю як тепло", size=9.5, color=HOT, italic=True))

    return render(os.path.join(IMG, 'vswr-power-reflection.svg'), W, H, *f)


# ── 4. Узгоджувальний Pi-контур і трансформація імпедансу ─────────────────
def fig_matching_network():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Узгоджувальний Pi-контур (Matching Network) та компенсація детьюнінгу", size=17, bold=True),
        text(W / 2, 50, "триелементна ланка C-L-C трансформує довільний розладнаний імпеданс Z_ant у 50 Ом з компенсацією реактивності",
             size=11.5, color=MUTED, italic=True)
    ]

    # Ліва частина: Електрична схема Pi-контуру
    sx, sy, sw, sh = 60, 85, 450, 345
    f.append(rect(sx, sy, sw, sh, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(sx + sw / 2, sy + 26, "Принципова схема узгоджувальної Pi-ланки", size=13, color=INK, bold=True))

    # Лінія RF від трансивера
    rf_in_x = sx + 40
    rf_out_x = sx + sw - 40
    bus_y = sy + 110
    gnd_y = sy + 250

    # Джерело RF 50 Ом
    f.append(circle(rf_in_x, bus_y, 6, fill=COLD, stroke=COLD, sw=0))
    f.append(text(rf_in_x, bus_y - 14, "Від чипа (50 Ом)", size=10.5, color=COLD, bold=True))

    # Антена
    f.append(circle(rf_out_x, bus_y, 6, fill=COPPER, stroke=COPPER, sw=0))
    f.append(text(rf_out_x, bus_y - 14, "До антени (Z_L)", size=10.5, color=COPPER, bold=True))

    # Послідовний індуктор/конденсатор L_s (Series)
    comp_c1_x = sx + 130
    comp_ls_x = sx + 225
    comp_c2_x = sx + 320

    # Горизонтальні провідники
    f.append(line(rf_in_x, bus_y, comp_c1_x, bus_y, color=LINE, sw=2))
    f.append(line(comp_c1_x, bus_y, comp_ls_x - 25, bus_y, color=LINE, sw=2))
    f.append(line(comp_ls_x + 25, bus_y, comp_c2_x, bus_y, color=LINE, sw=2))
    f.append(line(comp_c2_x, bus_y, rf_out_x, bus_y, color=LINE, sw=2))

    # Послідовний елемент L_s
    f.append(rect(comp_ls_x - 25, bus_y - 14, 50, 28, fill="#ffffff", stroke=HOT, sw=2, rx=4))
    f.append(text(comp_ls_x, bus_y + 4, "L_series", size=11, color=HOT, bold=True))
    f.append(text(comp_ls_x, bus_y - 20, "SMD 0402", size=9.5, color=MUTED))

    # Паралельний елемент 1 (C_shunt1)
    f.append(line(comp_c1_x, bus_y, comp_c1_x, bus_y + 45, color=LINE, sw=2))
    f.append(rect(comp_c1_x - 18, bus_y + 45, 36, 45, fill="#ffffff", stroke=COLD, sw=2, rx=4))
    f.append(text(comp_c1_x, bus_y + 72, "C_sh1", size=11, color=COLD, bold=True))
    f.append(line(comp_c1_x, bus_y + 90, comp_c1_x, gnd_y, color=LINE, sw=2))

    # Паралельний елемент 2 (C_shunt2)
    f.append(line(comp_c2_x, bus_y, comp_c2_x, bus_y + 45, color=LINE, sw=2))
    f.append(rect(comp_c2_x - 18, bus_y + 45, 36, 45, fill="#ffffff", stroke=COLD, sw=2, rx=4))
    f.append(text(comp_c2_x, bus_y + 72, "C_sh2", size=11, color=COLD, bold=True))
    f.append(line(comp_c2_x, bus_y + 90, comp_c2_x, gnd_y, color=LINE, sw=2))

    # Шина землі
    f.append(line(sx + 80, gnd_y, sx + sw - 80, gnd_y, color=COPPER, sw=3))
    for gx in range(int(sx + 90), int(sx + sw - 80), 25):
        f.append(line(gx, gnd_y, gx - 8, gnd_y + 12, color=COPPER, sw=1.5))
    f.append(text(sx + sw / 2, gnd_y + 24, "Суцільна земля GND (RF Ground Plane)", size=10.5, color=COPPER, bold=True))

    # Текстова примітка внизу лівої панелі
    f.append(text(sx + sw / 2, sy + sh - 22, "Pi-контур дозволяє зсувати імпеданс як вгору, так і вниз по опору", size=10, color=MUTED, italic=True))

    # Права частина: Траєкторія на діаграмі Сміта (концептуальна візуалізація)
    dx, dy, dw, dh = 540, 85, 340, 345
    f.append(rect(dx, dy, dw, dh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(dx + dw / 2, dy + 26, "Траєкторія узгодження (Smith Chart)", size=13, color=INK, bold=True))

    sm_cx, sm_cy, sm_r = dx + dw / 2, dy + 160, 95
    # Коло діаграми Сміта
    f.append(circle(sm_cx, sm_cy, sm_r, fill="#f8fafc", stroke="#94a3b8", sw=1.8))
    # Горизонтальна дійсна вісь (Real Axis)
    f.append(line(sm_cx - sm_r, sm_cy, sm_cx + sm_r, sm_cy, color="#94a3b8", sw=1.2))
    # Внутрішнє коло активного опору R = 50 Ом (r=1)
    f.append(circle(sm_cx + sm_r / 2, sm_cy, sm_r / 2, fill="none", stroke="#cbd5e1", sw=1.2))
    # Коло провідності g = 1
    f.append(f'<circle cx="{sm_cx - sm_r / 2}" cy="{sm_cy}" r="{sm_r / 2}" fill="none" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3,3"/>')

    # Центр (50 Ом, ідеал)
    f.append(circle(sm_cx, sm_cy, 5, fill=GREEN, stroke=GREEN, sw=0))
    f.append(text(sm_cx, sm_cy - 12, "50 Ом (Ціль)", size=10.5, color=GREEN, bold=True))

    # Початкова точка A: Розладнана антена в корпусі Z = 15 - j35 Ом
    pt_a_x, pt_a_y = sm_cx - 55, sm_cy + 45
    f.append(circle(pt_a_x, pt_a_y, 6, fill=HOT, stroke=HOT, sw=0))
    f.append(text(pt_a_x - 10, pt_a_y + 16, "A: Z_ant (в корпусі)", size=10, color=HOT, bold=True))

    # Крок 1: C_shunt2 рухає по колу провідності вниз
    pt_b_x, pt_b_y = sm_cx - 15, sm_cy + 65
    f.append(arrow(pt_a_x, pt_a_y, pt_b_x, pt_b_y, color=COLD, sw=2))
    f.append(text(pt_b_x - 8, pt_b_y + 16, "1) +C_sh2", size=9.5, color=COLD, bold=True))

    # Крок 2: L_series рухає по колу опору вгору до кола g=1
    pt_c_x, pt_c_y = sm_cx - 20, sm_cy - 35
    f.append(arrow(pt_b_x, pt_b_y, pt_c_x, pt_c_y, color=HOT, sw=2))
    f.append(text(pt_c_x - 22, pt_c_y - 6, "2) +L_ser", size=9.5, color=HOT, bold=True))

    # Крок 3: C_shunt1 докручує точно в центр 50 Ом
    f.append(arrow(pt_c_x, pt_c_y, sm_cx - 2, sm_cy - 2, color=GREEN, sw=2.2))
    f.append(text(sm_cx + 25, sm_cy - 26, "3) +C_sh1", size=9.5, color=GREEN, bold=True))

    # Пояснення кроків під діаграмою
    f.append(text(dx + dw / 2, dy + dh - 48, "Кроки: 1) Shunt C -> 2) Series L -> 3) Shunt C", size=10.5, color=INK, bold=True))
    f.append(text(dx + dw / 2, dy + dh - 26, "Результат: КСВ знижується з 6.2 до 1.15 у зібраному корпусі", size=10, color=GREEN, bold=True))

    return render(os.path.join(IMG, 'matching-pi-network.svg'), W, H, *f)


if __name__ == '__main__':
    fig_enclosure_detuning()
    fig_reactive_near_field()
    fig_vswr_power()
    fig_matching_network()
    print("Всі 4 фігури згенеровано у ./img/")
