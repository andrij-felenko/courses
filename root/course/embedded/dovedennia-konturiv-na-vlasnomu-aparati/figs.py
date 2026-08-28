# -*- coding: utf-8 -*-
"""Фігури до статті «Доведення контурів на власному апараті: порядок, автотюн, ознаки перетюну»
(root/course/embedded/dovedennia-konturiv-na-vlasnomu-aparati).
Чистий Python, без зовнішніх бібліотек; svgkit — зі scripts/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ієрархія каскадних контурів керування: Position -> Velocity -> Angle -> Rate -> Motors
# ─────────────────────────────────────────────────────────────────────────────
def fig_cascade_loops():
    W, H = 940, 540
    frags = [
        text(W / 2, 36, "Ієрархія каскадних контурів керування дрона", size=15, bold=True, color=INK),
        text(W / 2, 58, "Налаштування виконують суворо зсередини назовні: від найшвидшого контуру до найповільнішого", size=12, color=MUTED)
    ]

    # 4 каскадні блоки (зліва направо)
    blocks = [
        {"name": "Позиція (Position)", "rate": "20–50 Гц", "bw": "Смуга: ~0.5–1 Гц", "in": "Цільова точка (X, Y, Z)", "out": "Цільова швидкість (V_x, V_y, V_z)", "type": "P-регулятор", "color": "#e8f4f8", "stroke": NEG},
        {"name": "Швидкість (Velocity)", "rate": "50–100 Гц", "bw": "Смуга: ~2–4 Гц", "in": "Помилка швидкості (ΔV)", "out": "Цільовий кут і тяга (θ_des, T)", "type": "PID-регулятор", "color": "#eafaf0", "stroke": FIELD},
        {"name": "Кут (Attitude Angle)", "rate": "250–500 Гц", "bw": "Смуга: ~5–10 Гц", "in": "Помилка орієнтації (Δθ)", "out": "Цільова кутова швидкість (ω_des)", "type": "P / PI-регулятор", "color": "#fef9e7", "stroke": "#d4ac0d"},
        {"name": "Кутова швидкість (Rate)", "rate": "1000–8000 Гц", "bw": "Смуга: ~30–60 Гц", "in": "Помилка гіроскопа (Δω)", "out": "Командний момент (Torque)", "type": "PID + D-Term Filter", "color": "#fdedec", "stroke": POS}
    ]

    bw = 195
    bh = 175
    gap = 26
    start_x = (W - (4 * bw + 3 * gap)) / 2
    y_box = 85

    for i, b in enumerate(blocks):
        bx = start_x + i * (bw + gap)
        frags.append(f'<rect x="{bx:.1f}" y="{y_box:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="8" fill="{b["color"]}" stroke="{b["stroke"]}" stroke-width="2"/>')
        frags.append(text(bx + bw / 2, y_box + 26, b["name"], size=12, bold=True, color=INK))
        frags.append(text(bx + bw / 2, y_box + 48, f"Частота: {b['rate']}", size=11, bold=True, color=b["stroke"]))
        frags.append(text(bx + bw / 2, y_box + 68, b["bw"], size=11, color=MUTED))
        frags.append(f'<line x1="{bx + 12:.1f}" y1="{y_box + 80:.1f}" x2="{bx + bw - 12:.1f}" y2="{y_box + 80:.1f}" stroke="{b["stroke"]}" stroke-width="1" stroke-opacity="0.3"/>')
        frags.append(text(bx + bw / 2, y_box + 102, b["type"], size=11, bold=True, color=INK))
        frags.append(text(bx + bw / 2, y_box + 124, "Вхід: " + b["in"], size=9.5, color=MUTED))
        frags.append(text(bx + bw / 2, y_box + 144, "Вихід: " + b["out"], size=9.5, color=MUTED))

        if i < 3:
            ax1 = bx + bw
            ax2 = bx + bw + gap
            ay = y_box + bh / 2
            frags.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    # Виконавчий блок (Праворуч знизу від Rate): Мікшер -> ESC -> Мотори
    y_act = 295
    x_act = start_x + 3 * (bw + gap)
    frags.append(arrow(x_act + bw / 2, y_box + bh, x_act + bw / 2, y_act, color=POS, sw=1.8))
    frags.append(f'<rect x="{x_act:.1f}" y="{y_act:.1f}" width="{bw:.1f}" height="95" rx="8" fill="#f4f6f8" stroke="{LINE}" stroke-width="1.5"/>')
    frags.append(text(x_act + bw / 2, y_act + 24, "Мікшер та ESC", size=12, bold=True, color=INK))
    frags.append(text(x_act + bw / 2, y_act + 46, "DShot600 / DShot300", size=11, color=MUTED))
    frags.append(text(x_act + bw / 2, y_act + 70, "4× БК-мотори + гвинти", size=11, bold=True, color=POS))

    # Картка послідовності тюнінгу (ліворуч від блоку моторів)
    w_tune = 3 * bw + 2 * gap
    frags.append(f'<rect x="{start_x:.1f}" y="{y_act:.1f}" width="{w_tune:.1f}" height="95" rx="8" fill="#fcfdfe" stroke="{POS}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    frags.append(text(start_x + w_tune / 2, y_act + 26, "Порядок практичного доведення контурів (зсередини назовні):", size=11.5, bold=True, color=POS))
    frags.append(text(start_x + w_tune / 2, y_act + 50, "1. Rate PID (Кутова швидкість)  ➔  2. Angle P (Кутове положення)", size=11, bold=True, color=INK))
    frags.append(text(start_x + w_tune / 2, y_act + 74, "3. Velocity PID (Лінійна швидкість)  ➔  4. Position P (Координати)", size=11, bold=True, color=INK))

    # Зворотний зв'язок: Сенсорні шини
    y_fb = 435
    frags.append(f'<rect x="{start_x:.1f}" y="{y_fb:.1f}" width="{4 * bw + 3 * gap:.1f}" height="50" rx="6" fill="#ffffff" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4,4"/>')
    frags.append(text(W / 2, y_fb + 22, "Зворотний зв'язок давачів на автопілот", size=11.5, bold=True, color=INK))
    frags.append(text(W / 2, y_fb + 40, "Гіроскоп 8 кГц (Rate) · Акселерометр/EKF (Angle) · Оптичний потік/GNSS (Velocity) · GNSS/RTK (Position)", size=10.5, color=MUTED))

    # Стрілка від моторів до зворотного зв'язку
    frags.append(arrow(x_act + bw / 2, y_act + 95, x_act + bw / 2, y_fb, color=LINE, sw=1.5))
    
    # Відгалуження зворотного зв'язку вгору до блоків
    for i in range(3):
        bx = start_x + i * (bw + gap) + bw / 2
        frags.append(arrow(bx, y_fb, bx, y_act + 95, color=LINE, sw=1.5))

    render(os.path.join(IMG, "cascade-loops.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Перехідна характеристика (Step Response) для різних налаштувань PID
# ─────────────────────────────────────────────────────────────────────────────
def fig_step_response_pid():
    W, H = 940, 480
    frags = [
        text(W / 2, 38, "Відгук кутової швидкості на сходинку команди (Step Response)", size=15, bold=True, color=INK),
        text(W / 2, 60, "Порівняння ідеального демпфування з типовими помилками налаштування коефіцієнтів", size=12, color=MUTED)
    ]

    gx, gy, gw, gh = 90, 95, 780, 290
    frags.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#fcfdfe" stroke="{MUTED}" stroke-width="1"/>')

    y_0 = gy + gh - 35
    y_1 = gy + 90
    y_mid = (y_0 + y_1) / 2
    y_over = y_1 - 45

    for y_pos, val, lbl in [(y_0, 0, "0.0 (Спокій)"), (y_mid, 0.5, "0.5"), (y_1, 1.0, "1.0 (Цільова швидкість)"), (y_over, 1.3, "1.3")]:
        frags.append(f'<line x1="{gx}" y1="{y_pos:.1f}" x2="{gx + gw}" y2="{y_pos:.1f}" stroke="#e0e4e8" stroke-width="1" stroke-dasharray="3,3"/>')
        frags.append(text(gx - 8, y_pos + 4, lbl, size=10.5, color=MUTED, anchor="end"))

    frags.append(arrow(gx, y_0, gx + gw - 15, y_0, color=INK, sw=1.5))
    frags.append(text(gx + gw - 10, y_0 + 20, "Час t (мс)", size=11, bold=True, color=INK, anchor="end"))
    frags.append(arrow(gx, y_0, gx, gy + 15, color=INK, sw=1.5))
    frags.append(text(gx - 10, gy + 15, "Кутова швидкість ω (deg/s)", size=11, bold=True, color=INK, anchor="end"))

    # Сходинка завдання (SetPoint)
    x_step = gx + 60
    sp_path = f"M {gx} {y_0} L {x_step} {y_0} L {x_step} {y_1} L {gx + gw} {y_1}"
    frags.append(f'<path d="{sp_path}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5,4"/>')
    frags.append(text(x_step + 60, y_1 - 10, "Задана сходинка (Setpoint)", size=11, bold=True, color=MUTED))

    # 1. Ідеальний відгук
    pts_ideal = []
    for t in range(0, 720, 5):
        tx = x_step + t
        if tx > gx + gw: break
        tau = t / 45.0
        val = 1.0 - (1.0 + tau) * math.exp(-tau)
        py = y_0 - val * (y_0 - y_1)
        pts_ideal.append(f"{tx:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_ideal)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # 2. Недодемпування / Завеликий P / Замалий D
    pts_under = []
    for t in range(0, 720, 5):
        tx = x_step + t
        if tx > gx + gw: break
        tau = t / 35.0
        val = 1.0 - math.exp(-0.4 * tau) * math.cos(1.8 * tau)
        py = y_0 - val * (y_0 - y_1)
        pts_under.append(f"{tx:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_under)}" fill="none" stroke="{POS}" stroke-width="2"/>')

    # 3. Передемпування / Замалий P
    pts_slow = []
    for t in range(0, 720, 5):
        tx = x_step + t
        if tx > gx + gw: break
        tau = t / 140.0
        val = 1.0 - math.exp(-tau)
        py = y_0 - val * (y_0 - y_1)
        pts_slow.append(f"{tx:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_slow)}" fill="none" stroke="{NEG}" stroke-width="2"/>')

    # 4. Завеликий D (ВЧ шум)
    pts_dnoise = []
    for t in range(0, 720, 5):
        tx = x_step + t
        if tx > gx + gw: break
        tau = t / 40.0
        base_val = 1.0 - (1.0 + tau) * math.exp(-tau)
        noise = 0.08 * math.sin(t * 0.45) * math.exp(-t / 300.0) if t > 10 else 0
        val = base_val + noise
        py = y_0 - val * (y_0 - y_1)
        pts_dnoise.append(f"{tx:.1f},{py:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_dnoise)}" fill="none" stroke="#e67e22" stroke-width="1.8" stroke-dasharray="2,1"/>')

    # Легенда знизу
    ly = gy + gh + 40
    legends = [
        {"color": FIELD, "dash": "none", "title": "Ідеальний тюнінг", "desc": "Швидкий вихід (~45 мс), нульовий переліт (Overshoot = 0%)"},
        {"color": POS, "dash": "none", "title": "Надлишок P / Брак D", "desc": "Переліт > 30%, затяжний низькочастотний дзвін (3–8 Гц)"},
        {"color": NEG, "dash": "none", "title": "Брак P (Лінивий)", "desc": "Затягнуте наростання (> 200 мс), ватне керування, знос вітром"},
        {"color": "#e67e22", "dash": "2,1", "title": "Надлишок D (Шум)", "desc": "ВЧ тремтіння (100–300 Гц), перегрів моторів, падіння тяги"}
    ]

    for i, leg in enumerate(legends):
        lx = gx + 10 + i * 195
        frags.append(f'<line x1="{lx}" y1="{ly + 6}" x2="{lx + 28}" y2="{ly + 6}" stroke="{leg["color"]}" stroke-width="2.5" stroke-dasharray="{leg["dash"]}"/>')
        frags.append(text(lx + 34, ly + 10, leg["title"], size=11, bold=True, color=INK, anchor="start"))
        frags.append(text(lx, ly + 26, leg["desc"], size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "step-response-pid.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Тракт D-терма та каскад фільтрації шуму
# ─────────────────────────────────────────────────────────────────────────────
def fig_dterm_noise_filter():
    W, H = 940, 430
    frags = [
        text(W / 2, 38, "Тракт формування D-складової та каскад фільтрації шуму", size=15, bold=True, color=INK),
        text(W / 2, 60, "Диференціювання множить амплітуду шуму на частоту: фільтри мають прибрати піки вібрацій без фазової затримки", size=12, color=MUTED)
    ]

    steps = [
        {"title": "Сирий гіроскоп", "sub": "IMU SPI (8 кГц)", "note": "Сигнал руху (0–30 Гц) + шум гвинтів (150–400 Гц)", "fill": "#f4f6f8", "stroke": INK},
        {"title": "Динамічний Notch", "sub": "RPM / FFT Tracking", "note": "Вирізає вузькі піки обертання моторів (Q ≈ 4–8)", "fill": "#eafaf0", "stroke": FIELD},
        {"title": "Фільтр НЧ (LPF)", "sub": "PT1 / Bi-quad (100 Гц)", "note": "Пригнічує залишковий високочастотний спектр", "fill": "#e8f4f8", "stroke": NEG},
        {"title": "Диференціатор", "sub": "d(Gyro)/dt · K_d", "note": "Обчислення демпфувального моменту за виміром", "fill": "#fef9e7", "stroke": "#d4ac0d"},
        {"title": "Вихід D-терма", "sub": "У мікшер моторів", "note": "Чисте гальмування без мікротремтіння та перегріву", "fill": "#fdedec", "stroke": POS}
    ]

    bw = 154
    bh = 130
    gap = 26
    start_x = (W - (5 * bw + 4 * gap)) / 2
    y_box = 100

    for i, s in enumerate(steps):
        bx = start_x + i * (bw + gap)
        frags.append(f'<rect x="{bx:.1f}" y="{y_box:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="8" fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="2"/>')
        frags.append(text(bx + bw / 2, y_box + 26, s["title"], size=12, bold=True, color=INK))
        frags.append(text(bx + bw / 2, y_box + 46, s["sub"], size=10.5, bold=True, color=s["stroke"]))
        frags.append(f'<line x1="{bx + 10:.1f}" y1="{y_box + 58:.1f}" x2="{bx + bw - 10:.1f}" y2="{y_box + 58:.1f}" stroke="{s["stroke"]}" stroke-width="1" stroke-opacity="0.3"/>')
        
        words = s["note"].split(" ")
        line1 = " ".join(words[:len(words)//2 + 1])
        line2 = " ".join(words[len(words)//2 + 1:])
        frags.append(text(bx + bw / 2, y_box + 80, line1, size=9.5, color=MUTED))
        frags.append(text(bx + bw / 2, y_box + 98, line2, size=9.5, color=MUTED))

        if i < 4:
            ax1 = bx + bw
            ax2 = bx + bw + gap
            ay = y_box + bh / 2
            frags.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    y_spec = 270
    h_spec = 120
    w_spec = (W - start_x * 2 - gap) / 2

    # Лівий спектр: Без фільтрації
    x_s1 = start_x
    frags.append(f'<rect x="{x_s1}" y="{y_spec}" width="{w_spec}" height="{h_spec}" rx="6" fill="#fdedec" stroke="{POS}" stroke-width="1.5"/>')
    frags.append(text(x_s1 + w_spec / 2, y_spec + 22, "Спектр D-складової БЕЗ достатньої фільтрації", size=11.5, bold=True, color=POS))
    pts_s1 = [f"{x_s1 + 20},{y_spec + 100}", f"{x_s1 + 80},{y_spec + 90}", f"{x_s1 + 140},{y_spec + 85}",
              f"{x_s1 + 200},{y_spec + 35}", f"{x_s1 + 230},{y_spec + 92}", f"{x_s1 + 300},{y_spec + 40}",
              f"{x_s1 + 330},{y_spec + 95}", f"{x_s1 + w_spec - 20},{y_spec + 98}"]
    frags.append(f'<polyline points="{" ".join(pts_s1)}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(x_s1 + 200, y_spec + 30, "Пік вібрації мотора (250 Гц)", size=10, bold=True, color=POS))
    frags.append(text(x_s1 + w_spec / 2, y_spec + h_spec - 10, "Наслідок: гарячі мотори (> 80°C), тремтіння, просідання АКБ", size=10, bold=True, color=INK))

    # Правий спектр: З фільтрацією
    x_s2 = start_x + w_spec + gap
    frags.append(f'<rect x="{x_s2}" y="{y_spec}" width="{w_spec}" height="{h_spec}" rx="6" fill="#eafaf0" stroke="{FIELD}" stroke-width="1.5"/>')
    frags.append(text(x_s2 + w_spec / 2, y_spec + 22, "Спектр D-складової З динамічним фільтром (RPM Notch + PT1)", size=11.5, bold=True, color=FIELD))
    pts_s2 = [f"{x_s2 + 20},{y_spec + 100}", f"{x_s2 + 80},{y_spec + 90}", f"{x_s2 + 140},{y_spec + 92}",
              f"{x_s2 + 200},{y_spec + 96}", f"{x_s2 + 230},{y_spec + 97}", f"{x_s2 + 300},{y_spec + 99}",
              f"{x_s2 + w_spec - 20},{y_spec + 100}"]
    frags.append(f'<polyline points="{" ".join(pts_s2)}" fill="none" stroke="{FIELD}" stroke-width="2"/>')
    frags.append(text(x_s2 + 200, y_spec + 60, "Режектор вирізав гармоніку", size=10, bold=True, color=FIELD))
    frags.append(text(x_s2 + w_spec / 2, y_spec + h_spec - 10, "Результат: холодні мотори, чіткий відгук, збереження фази", size=10, bold=True, color=INK))

    render(os.path.join(IMG, "dterm-noise-filter.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Імпульсний тест AutoTune: серія збурень та розрахунок параметрів
# ─────────────────────────────────────────────────────────────────────────────
def fig_autotune_pulse_sequence():
    W, H = 940, 460
    frags = [
        text(W / 2, 38, "Принцип роботи алгоритму AutoTune (вимірювання імпульсного відгуку)", size=15, bold=True, color=INK),
        text(W / 2, 60, "Автопілот генерує серію каліброваних імпульсів (Step Doublets) і визначає межі стійкості", size=12, color=MUTED)
    ]

    gx, gy, gw, gh = 90, 95, 780, 240
    frags.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#fcfdfe" stroke="{MUTED}" stroke-width="1"/>')

    y_mid = gy + gh / 2
    frags.append(f'<line x1="{gx}" y1="{y_mid}" x2="{gx + gw}" y2="{y_mid}" stroke="#cbd5e1" stroke-width="1.5"/>')
    frags.append(text(gx - 8, y_mid + 4, "0 deg/s", size=10.5, color=MUTED, anchor="end"))

    frags.append(arrow(gx, y_mid, gx + gw - 15, y_mid, color=INK, sw=1.5))
    frags.append(text(gx + gw - 10, y_mid + 20, "Час (с)", size=11, bold=True, color=INK, anchor="end"))

    # Сигнал завдання
    t1_s = gx + 60
    t1_e = t1_s + 70
    t2_s = t1_e + 140
    t2_e = t2_s + 70
    t3_s = t2_e + 140
    t3_e = t3_s + 80

    sp_cmd = f"M {gx} {y_mid} L {t1_s} {y_mid} L {t1_s} {y_mid - 65} L {t1_e} {y_mid - 65} L {t1_e} {y_mid} " \
             f"L {t2_s} {y_mid} L {t2_s} {y_mid + 65} L {t2_e} {y_mid + 65} L {t2_e} {y_mid} " \
             f"L {t3_s} {y_mid} L {t3_s} {y_mid - 85} L {t3_e} {y_mid - 85} L {t3_e} {y_mid} L {gx + gw} {y_mid}"
    frags.append(f'<path d="{sp_cmd}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4,4"/>')
    frags.append(text(t1_s + 35, y_mid - 75, "Тестовий імпульс (+)", size=10, bold=True, color=MUTED))
    frags.append(text(t2_s + 35, y_mid + 82, "Тестовий імпульс (−)", size=10, bold=True, color=MUTED))

    # Реальний відгук
    r_pts = [
        f"{gx},{y_mid}", f"{t1_s + 14},{y_mid}",
        f"{t1_s + 35},{y_mid - 40}", f"{t1_s + 65},{y_mid - 72}", f"{t1_s + 85},{y_mid - 78}",
        f"{t1_s + 110},{y_mid - 30}", f"{t1_s + 135},{y_mid + 6}", f"{t1_s + 160},{y_mid}",
        f"{t2_s + 14},{y_mid}",
        f"{t2_s + 35},{y_mid + 40}", f"{t2_s + 65},{y_mid + 72}", f"{t2_s + 85},{y_mid + 78}",
        f"{t2_s + 110},{y_mid + 30}", f"{t2_s + 135},{y_mid - 6}", f"{t2_s + 160},{y_mid}",
        f"{t3_s + 12},{y_mid}",
        f"{t3_s + 35},{y_mid - 55}", f"{t3_s + 75},{y_mid - 94}", f"{t3_s + 95},{y_mid - 100}",
        f"{t3_s + 125},{y_mid - 40}", f"{t3_s + 155},{y_mid + 12}", f"{t3_s + 180},{y_mid - 3}", f"{t3_s + 200},{y_mid}",
        f"{gx + gw},{y_mid}"
    ]
    frags.append(f'<path d="M {" L ".join(r_pts)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(text(t1_s + 85, y_mid - 90, "Виміряний кутовий відгук ω(t)", size=11, bold=True, color=POS))

    # Вимірювані величини: маркер затримки знизу осі, щоб не перетинати графік
    frags.append(f'<line x1="{t1_s}" y1="{y_mid + 20}" x2="{t1_s + 14}" y2="{y_mid + 20}" stroke="{NEG}" stroke-width="1.5"/>')
    frags.append(f'<line x1="{t1_s}" y1="{y_mid}" x2="{t1_s}" y2="{y_mid + 24}" stroke="{NEG}" stroke-width="1" stroke-dasharray="2,2"/>')
    frags.append(f'<line x1="{t1_s + 14}" y1="{y_mid}" x2="{t1_s + 14}" y2="{y_mid + 24}" stroke="{NEG}" stroke-width="1" stroke-dasharray="2,2"/>')
    frags.append(text(t1_s + 7, y_mid + 36, "Затримка τ", size=9.5, bold=True, color=NEG))

    # Маркер перерегулювання
    frags.append(f'<line x1="{t1_s + 70}" y1="{y_mid - 65}" x2="{t1_s + 85}" y2="{y_mid - 65}" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="2,2"/>')
    frags.append(text(t1_s + 105, y_mid - 65, "ΔOvershoot", size=9.5, bold=True, color=FIELD, anchor="start"))

    # Пояснювальні картки знизу
    y_card = gy + gh + 22
    cards = [
        {"title": "1. Оцінка затримки та тяги", "desc": "Визначає транспортне запізнення τ контуру і максимальне прискорення α_max (dω/dt).", "stroke": NEG},
        {"title": "2. Пошук граничного підсилення", "desc": "Підвищує P та D до виникнення фіксованого перерегулювання (Overshoot ~10–15%).", "stroke": FIELD},
        {"title": "3. Запас стійкості (Safety Margin)", "desc": "Знижує знайдені критичні коефіцієнти на 30–40% для гарантії стійкості при просіданні АКБ.", "stroke": POS}
    ]

    cw = 246
    for i, c in enumerate(cards):
        cx = gx + i * (cw + 21)
        frags.append(f'<rect x="{cx}" y="{y_card}" width="{cw}" height="80" rx="6" fill="#f8fafc" stroke="{c["stroke"]}" stroke-width="1.5"/>')
        frags.append(text(cx + cw / 2, y_card + 22, c["title"], size=11, bold=True, color=INK))
        frags.append(text(cx + cw / 2, y_card + 44, c["desc"].split(" і ")[0], size=9.5, color=MUTED))
        frags.append(text(cx + cw / 2, y_card + 62, "і " + c["desc"].split(" і ")[1] if " і " in c["desc"] else c["desc"][len(c["desc"])//2:], size=9.5, color=MUTED))

    render(os.path.join(IMG, "autotune-pulse-sequence.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_cascade_loops()
    fig_step_response_pid()
    fig_dterm_noise_filter()
    fig_autotune_pulse_sequence()
    print("Всі 4 фігури успішно згенеровано.")
