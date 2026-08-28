# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. transition-phases.svg : Фази прямого переходу, розподіл підйомної сили ──
def fig_transition_phases():
    W, H = 840, 520
    fr = []
    fr.append(text(W/2, 28, "Динаміка прямого переходу VTOL (Forward Transition)", size=17, bold=True))

    # Секції за часом / швидкістю: 3 фази
    fr.append(rect(60, 55, 230, 420, fill="#f9fbfe", stroke="#d0d7de", sw=1, rx=4))
    fr.append(rect(290, 55, 280, 420, fill="#fefdf5", stroke="#e1d88a", sw=1, rx=4))
    fr.append(rect(570, 55, 210, 420, fill="#f6fcf8", stroke="#c3e6cb", sw=1, rx=4))

    fr.append(text(175, 76, "Фаза 1: Розгін (Hover / Accel)", size=13, bold=True, color=NEG))
    fr.append(text(430, 76, "Фаза 2: Змішана тяга (Blending)", size=13, bold=True, color="#b08800"))
    fr.append(text(675, 76, "Фаза 3: Літак (Fixed-Wing)", size=13, bold=True, color=FIELD))

    # Позначки швидкостей зверху
    fr.append(line(60, 95, 780, 95, color="#8c959f", sw=1.2, dash="4,4"))
    fr.append(text(60, 112, "0 м/с", size=11, color=MUTED, anchor="start"))
    fr.append(text(290, 112, "V_blend_start (6 м/с)", size=11, color=MUTED, anchor="middle"))
    fr.append(text(470, 112, "V_stall (13 м/с)", size=11, color=POS, bold=True, anchor="middle"))
    fr.append(text(570, 112, "V_trans (16 м/с)", size=11, color=FIELD, bold=True, anchor="middle"))
    fr.append(text(780, 112, "V_cruise (22 м/с)", size=11, color=MUTED, anchor="end"))

    # Лінії порогів вертикальні
    fr.append(line(290, 95, 290, 460, color="#d0d7de", sw=1.2, dash="3,3"))
    fr.append(line(470, 95, 470, 460, color="#f8d7da", sw=1.5, dash="4,4"))
    fr.append(line(570, 95, 570, 460, color="#c3e6cb", sw=1.5, dash="3,3"))

    # Графік 1: Підйомна сила (L крила) та тяга роторів (T_v)
    fr.append(text(75, 145, "Підйомна сила та тяга", size=12, bold=True, color=INK, anchor="start"))
    fr.append(line(80, 270, 770, 270, color=LINE, sw=1.2))
    fr.append(line(80, 160, 770, 160, color="#8c959f", sw=1, dash="2,2"))
    fr.append(text(75, 164, "100% m·g", size=10, color=MUTED, anchor="end"))
    fr.append(text(75, 274, "0 N", size=10, color=MUTED, anchor="end"))

    # Крива тяги роторів T_v
    pts_tv = []
    for px in range(60, 571, 15):
        if px <= 290:
            py = 160.0
        else:
            rel_v = (px - 290.0) / (570.0 - 290.0)
            frac = 1.0 - (rel_v ** 2)
            py = 270.0 - frac * 110.0
        pts_tv.append((px, py))
    pts_tv.append((780, 270.0))
    s_tv = " ".join("%.1f,%.1f" % p for p in pts_tv)
    fr.append(f'<polyline points="{s_tv}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Крива підйомної сили крила L
    pts_l = []
    for px in range(60, 781, 15):
        if px <= 290:
            rel_v = (px - 60.0) / 230.0 * 0.35
        else:
            rel_v = 0.35 + (px - 290.0) / (570.0 - 290.0) * 0.65
        frac = min(1.0, rel_v ** 2)
        py = 270.0 - frac * 110.0
        pts_l.append((px, py))
    s_l = " ".join("%.1f,%.1f" % p for p in pts_l)
    fr.append(f'<polyline points="{s_l}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Підписи ліній сил
    fr.append(text(180, 185, "Тяга роторів (T_v)", size=12, color=NEG, bold=True))
    fr.append(text(650, 180, "Підйомна сила крила (L)", size=12, color=FIELD, bold=True))
    fr.append(text(450, 220, "L + T_v ≈ m·g (баланс ваги)", size=11, color=INK, bold=True))

    # Графік 2: Тяга маршового штовхача та авторитет керма
    fr.append(text(75, 305, "Маршовий двигун і ваговий коефіцієнт (Blending)", size=12, bold=True, color=INK, anchor="start"))
    fr.append(line(80, 430, 770, 430, color=LINE, sw=1.2))
    fr.append(line(80, 330, 770, 330, color="#8c959f", sw=1, dash="2,2"))
    fr.append(text(75, 334, "100%", size=10, color=MUTED, anchor="end"))
    fr.append(text(75, 434, "0%", size=10, color=MUTED, anchor="end"))

    # Маршова тяга T_pusher
    pts_push = [(60, 430), (120, 330), (570, 330), (620, 365), (780, 365)]
    s_push = " ".join("%.1f,%.1f" % p for p in pts_push)
    fr.append(f'<polyline points="{s_push}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="5,3"/>')
    fr.append(text(180, 320, "Тяга штовхача (Pusher)", size=11, color=POS, bold=True))

    # Фактор змішування елеронів B(v)
    pts_b = [(60, 430), (290, 430), (570, 330), (780, 330)]
    s_b = " ".join("%.1f,%.1f" % p for p in pts_b)
    fr.append(f'<polyline points="{s_b}" fill="none" stroke="#2c3e50" stroke-width="2.5"/>')
    fr.append(text(460, 375, "Авторитет елеронів B(v)", size=11, color="#2c3e50", bold=True))

    # Пояснювальний блок знизу
    fr.append(rect(60, 480, 720, 30, fill=FILL, stroke=LINE, sw=1, rx=4))
    fr.append(text(420, 500, "Критична умова успішного переходу: повне вимкнення підйомних роторів лише після V_ias > V_trans", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "transition-phases.svg"), W, H, *fr)


# ── 2. altitude-sinkhole.svg : Механізм провалу висоти при передчасному вимкненні ──
def fig_altitude_sinkhole():
    W, H = 820, 480
    fr = []
    fr.append(text(W/2, 28, "Небезпечна зона «провалу висоти» (Altitude Sink Hole)", size=17, bold=True))

    # Траєкторія нормального переходу vs Передчасне вимкнення
    fr.append(line(70, 80, 70, 410, color=LINE, sw=1.5))
    fr.append(line(70, 410, 770, 410, color=LINE, sw=1.5))
    fr.append(text(70, 70, "Висота H (м)", size=12, color=INK, bold=True, anchor="middle"))
    fr.append(text(770, 430, "Дистанція розгону X (м)", size=12, color=INK, bold=True, anchor="end"))

    # Початкова висота 50 м
    fr.append(line(65, 140, 770, 140, color="#8c959f", sw=1, dash="3,3"))
    fr.append(text(60, 144, "50 м", size=11, color=MUTED, anchor="end"))
    fr.append(text(60, 290, "35 м", size=11, color=MUTED, anchor="end"))
    fr.append(text(60, 414, "0 м", size=11, color=MUTED, anchor="end"))

    # Траєкторія 1: Штатний перехід
    fr.append(line(70, 140, 760, 140, color=FIELD, sw=3))
    fr.append(circle(70, 140, 4, fill=FIELD, stroke=FIELD))
    fr.append(circle(480, 140, 4, fill=FIELD, stroke=FIELD))
    fr.append(circle(760, 140, 4, fill=FIELD, stroke=FIELD))
    fr.append(text(620, 125, "Штатний перехід (L + T_v = m·g)", size=12, color=FIELD, bold=True))

    # Траєкторія 2: Передчасне вимкнення роторів при V < V_stall
    pts_sink = [
        (70, 140), (280, 140), (330, 155), (400, 220), (470, 290),
        (540, 310), (620, 295), (720, 240), (760, 220)
    ]
    s_sink = " ".join("%.1f,%.1f" % p for p in pts_sink)
    fr.append(f'<polyline points="{s_sink}" fill="none" stroke="{POS}" stroke-width="3" stroke-dasharray="6,3"/>')

    # Позначення точки фатальної помилки
    fr.append(circle(280, 140, 6, fill="#fdecea", stroke=POS, sw=2))
    fr.append(arrow(280, 95, 280, 130, color=POS, sw=2))
    fr.append(fitbox(200, 55, 160, 38, "Передчасне вимкнення\nроторів (V = 10 м/с)", size=11, fill="#fdecea", stroke=POS))

    # Зона просідання
    fr.append(arrow(470, 145, 470, 285, color=POS, sw=2))
    fr.append(text(480, 215, "Провал висоти ΔH = 15 м", size=12, color=POS, bold=True, anchor="start"))
    fr.append(text(480, 235, "L(10 м/с) = 0.59 m·g", size=11, color=MUTED, anchor="start"))
    fr.append(text(480, 252, "Дефіцит сили = 0.41 m·g", size=11, color=POS, anchor="start"))

    # Вектори сил у точці просідання (x=400, y=220)
    fr.append(circle(400, 220, 4, fill=POS, stroke=POS))
    fr.append(arrow(400, 220, 400, 175, color=FIELD, sw=2))
    fr.append(text(408, 190, "L_wing (недостатня)", size=10, color=FIELD, bold=True, anchor="start"))
    fr.append(arrow(400, 220, 400, 275, color=LINE, sw=2.2))
    fr.append(text(408, 270, "m·g (вага апарата)", size=10, color=LINE, bold=True, anchor="start"))

    # Блок пояснення фізики
    fr.append(rect(100, 320, 320, 80, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    fr.append(text(260, 338, "Чому виникає Altitude Sink Hole:", size=11, bold=True, color=INK))
    fr.append(text(260, 355, "1. L ∝ V²: при 10 м/с замість 13 м/с крило несе лише 59% ваги", size=10, color=MUTED))
    fr.append(text(260, 372, "2. Прискорення вниз a_z = -g · (1 - L/(m·g)) ≈ -4.0 м/с²", size=10, color=POS, bold=True))
    fr.append(text(260, 389, "3. За 1.5 с розгону апарат втрачає > 10 метрів висоти", size=10, color=MUTED))

    # Відновлення чи катастрофа
    fr.append(fitbox(550, 340, 210, 60, "Аварійний підхват (Failsafe):\nекстрений перезапуск роторів\nпри Vz < -2.5 м/с", size=11, fill="#fef9e7", stroke="#f39c12"))

    render(os.path.join(IMG, "altitude-sinkhole.svg"), W, H, *fr)


# ── 3. control-authority-blending.svg : Перехресне мікшування авторитету керування ──
def fig_control_authority():
    W, H = 820, 460
    fr = []
    fr.append(text(W/2, 28, "Перехресний авторитет керування: ротори vs аеродинамічні рулі", size=17, bold=True))

    # Вісі графіка
    fr.append(line(80, 80, 80, 380, color=LINE, sw=1.5))
    fr.append(line(80, 380, 760, 380, color=LINE, sw=1.5))
    fr.append(text(80, 68, "Авторитет керування (%)", size=12, color=INK, bold=True, anchor="middle"))
    fr.append(text(760, 402, "Приладова швидкість V_ias (м/с)", size=12, color=INK, bold=True, anchor="end"))

    # Рівні 100% і 0%
    fr.append(line(75, 120, 760, 120, color="#8c959f", sw=1, dash="2,2"))
    fr.append(text(70, 124, "100%", size=11, color=MUTED, anchor="end"))
    fr.append(text(70, 250, "50%", size=11, color=MUTED, anchor="end"))
    fr.append(text(70, 384, "0%", size=11, color=MUTED, anchor="end"))

    # Швидкості по X
    fr.append(text(80, 398, "0", size=11, color=MUTED, anchor="middle"))
    fr.append(text(260, 398, "V_start (6 м/с)", size=11, color=MUTED, anchor="middle"))
    fr.append(text(500, 398, "V_trans (16 м/с)", size=11, color=MUTED, anchor="middle"))
    fr.append(text(720, 398, "V_cruise (24 м/с)", size=11, color=MUTED, anchor="middle"))

    # Вертикальні межі зони перекриття
    fr.append(rect(260, 80, 240, 300, fill="#fefdee", stroke="#e6db74", sw=1, rx=2))
    fr.append(text(380, 96, "Зона перекриття (Cross-Fade Blending)", size=11, color="#8a6d3b", bold=True))

    # Крива 1: Мультироторні ротори M_mc
    pts_mc = [(80, 120), (260, 120), (500, 380), (740, 380)]
    s_mc = " ".join("%.1f,%.1f" % p for p in pts_mc)
    fr.append(f'<polyline points="{s_mc}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    fr.append(text(170, 140, "Диференціал моторів (MC)", size=12, color=NEG, bold=True))

    # Крива 2: Аеродинамічні рулі M_fw
    pts_fw = []
    for px in range(80, 741, 15):
        if px <= 260:
            py = 380.0
        elif px >= 500:
            py = 120.0
        else:
            rel = (px - 260.0) / (500.0 - 260.0)
            py = 380.0 - (rel ** 1.5) * 260.0
        pts_fw.append((px, py))
    s_fw = " ".join("%.1f,%.1f" % p for p in pts_fw)
    fr.append(f'<polyline points="{s_fw}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    fr.append(text(620, 140, "Елерони / Елеватор (FW)", size=12, color=FIELD, bold=True))

    # Точка рівного авторитету (50/50)
    fr.append(circle(390, 250, 5, fill="#f39c12", stroke="#b9770e", sw=2))
    fr.append(text(400, 245, "50% MC / 50% FW", size=11, color="#b9770e", bold=True, anchor="start"))

    # Нижній пояснювальний блок
    fr.append(rect(80, 415, 680, 35, fill=FILL, stroke=LINE, sw=1, rx=4))
    fr.append(text(420, 437, "Динамічний тиск q = 0.5 · ρ · V² масштабує підсилення PID літака: K_p(v) = K_p0 · (V_scale / V)²", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "control-authority-blending.svg"), W, H, *fr)


# ── 4. back-transition-flow.svg : Зворотний перехід та затримка розкрутки роторів ──
def fig_back_transition():
    W, H = 820, 480
    fr = []
    fr.append(text(W/2, 28, "Зворотний перехід (Back-Transition) та затримка розкрутки роторів", size=17, bold=True))

    boxes = [
        (50, 60, 170, "1. Гальмування\n(V = 22 → 14 м/с)\nТяга штовхача = 0,\nфларе тангажу θ +5°", NEG),
        (230, 60, 175, "2. Pre-spooling роторів\n(V = 14 → 12 м/с)\nРозкрутка моторів до idle,\nкомпенсація лагу ESC", "#f39c12"),
        (415, 60, 175, "3. Зрив потоку з крила\n(V < V_stall, 10 м/с)\nL стрімко падає до 0,\nротори видають 100% T_v", POS),
        (600, 60, 170, "4. Чисте висіння\n(V < 3 м/с)\nПовний перехід у MC,\nпозиціонування GPS", FIELD),
    ]
    for bx, by, bw, txt, col in boxes:
        fr.append(fitbox(bx, by, bw, 90, txt, size=11, fill=FILL, stroke=col, sw=1.8))

    # Стрілки між етапами зверху
    fr.append(arrow(220, 105, 230, 105, color=LINE, sw=2))
    fr.append(arrow(405, 105, 415, 105, color=LINE, sw=2))
    fr.append(arrow(590, 105, 600, 105, color=LINE, sw=2))

    # Графік порівняння: З передрозкруткою vs Без передрозкрутки
    fr.append(rect(50, 170, 720, 240, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=4))
    fr.append(text(410, 195, "Часова шкала перехоплення тяги під час зриву потоку", size=13, bold=True, color=INK))

    # Осі
    fr.append(line(90, 220, 90, 380, color=LINE, sw=1.2))
    fr.append(line(90, 380, 740, 380, color=LINE, sw=1.2))
    fr.append(text(90, 212, "Тяга роторів T_v / Висота H", size=11, color=INK, bold=True, anchor="middle"))
    fr.append(text(740, 396, "Час гальмування t (секунди)", size=11, color=INK, bold=True, anchor="end"))

    # Момент зриву потоку з крила на t = 2.5 с (x = 380)
    fr.append(line(380, 215, 380, 380, color=POS, sw=1.5, dash="4,4"))
    fr.append(text(380, 210, "Зрив потоку (L → 0)", size=11, color=POS, bold=True))

    # Варіант А: З Pre-spooling (зелений)
    pts_prespool = [(90, 380), (260, 380), (280, 340), (380, 340), (410, 240), (720, 240)]
    s_pre = " ".join("%.1f,%.1f" % p for p in pts_prespool)
    fr.append(f'<polyline points="{s_pre}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    fr.append(text(540, 230, "Штатний підхват з Pre-spool (H = const)", size=11, color=FIELD, bold=True))

    # Варіант Б: Без Pre-spooling (холодний старт роторів, червоний)
    pts_cold = [(90, 380), (380, 380), (470, 240), (720, 240)]
    s_cold = " ".join("%.1f,%.1f" % p for p in pts_cold)
    fr.append(f'<polyline points="{s_cold}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="5,3"/>')
    fr.append(text(540, 275, "Холодний старт роторів (затримка 500 мс)", size=11, color=POS, bold=True))

    # Зона провалу
    fr.append(fitbox(400, 290, 110, 50, "Лаг ESC/мотора:\nдефіцит тяги", size=10, fill="#fdecea", stroke=POS, bold=True))

    # Нижній висновок
    fr.append(rect(50, 425, 720, 40, fill=FILL, stroke=LINE, sw=1, rx=4))
    fr.append(text(410, 450, "Правило зворотного переходу: підйомні ротори запускаються на холостий хід ДО входу в режим звалювання крила", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "back-transition-flow.svg"), W, H, *fr)


if __name__ == "__main__":
    fig_transition_phases()
    fig_altitude_sinkhole()
    fig_control_authority()
    fig_back_transition()
    print("All figures generated successfully.")
