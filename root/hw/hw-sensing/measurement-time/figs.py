# -*- coding: utf-8 -*-
# Фігури до статті «Час вимірювання» (book/communications/synchronization/measurement-time).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Три виміри часу в радіофізиці ──────────────────────────────────
def fig_time_domains():
    W, H = 720, 480
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Секція 1: Фазовий час
    parts.append(rect(30, 35, W - 60, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(45, 58, "1. Фазовий час (Phase Delay, \u03c4\u209a = -\u03c6 / \u03c9\u2080)", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(45, 78, "Зсув фази високочастотної несучої хвилі. Точність \u2264 1 мм, але неоднозначність у кожному циклі (\u03bb \u2248 19 см на 1.5 ГГц).", size=11, color=MUTED, anchor="start"))
    
    sine_pts = []
    for i in range(260):
        t = i / 259.0
        x = 45 + t * 450
        y = 115 - 18 * math.sin(t * 10 * math.pi)
        sine_pts.append((x, y))
    for i in range(len(sine_pts) - 1):
        parts.append(line(sine_pts[i][0], sine_pts[i][1], sine_pts[i+1][0], sine_pts[i+1][1], color=NEG, sw=1.8))
    
    parts.append(line(45, 115, 495, 115, color="#94a3b8", sw=1, dash="3 3"))
    parts.append(line(90, 88, 90, 142, color=POS, sw=1.2, dash="2 2"))
    parts.append(line(135, 88, 135, 142, color=POS, sw=1.2, dash="2 2"))
    parts.append(arrow(90, 95, 135, 95, color=POS, sw=1.3))
    parts.append(text(112, 90, "T\u2080 \u2248 0.67 нс", size=10, color=POS, anchor="middle", bold=True))

    b1, _, _ = textbox(595, 90, "Точність: частки мм\nНеоднозначність: \u03bb", size=11, fill="#eff6ff", stroke=NEG, pad=8)
    parts.append(b1)

    # Секція 2: Груповий час
    parts.append(rect(30, 155, W - 60, 115, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(45, 178, "2. Груповий час поширення (Group Delay, \u03c4\u1d4d = -d\u03c6 / d\u03c9)", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(45, 198, "Затримка обвідної сигналу (імпульсу, кодового чипу). Однозначна, але обмежена смугою B (метри / дециметри).", size=11, color=MUTED, anchor="start"))
    
    pulse_pts = []
    for i in range(260):
        t = (i - 130) / 30.0
        x = 45 + (i / 259.0) * 450
        y = 248 - 32 * math.exp(-t*t * 0.5)
        pulse_pts.append((x, y))
    for i in range(len(pulse_pts) - 1):
        parts.append(line(pulse_pts[i][0], pulse_pts[i][1], pulse_pts[i+1][0], pulse_pts[i+1][1], color=FIELD, sw=2.2))
    
    parts.append(line(45, 248, 495, 248, color="#94a3b8", sw=1, dash="3 3"))
    parts.append(line(270, 210, 270, 260, color=POS, sw=1.2, dash="2 2"))
    parts.append(text(270, 206, "\u03c4\u1d4d (час приходу піку)", size=10, color=POS, anchor="middle", bold=True))

    b2, _, _ = textbox(595, 212, "Точність: 0.1–10 м\nОднозначність: повна", size=11, fill="#ecfdf5", stroke=FIELD, pad=8)
    parts.append(b2)

    # Секція 3: Час вимірювання
    parts.append(rect(30, 280, W - 60, 140, fill="#fffbeb", stroke="#fcd34d", sw=1.2, rx=6))
    parts.append(text(45, 303, "3. Час вимірювання (Measurement / Integration Time, T_meas)", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(45, 323, "Макроінтервал накопичення енергії приймачем (тисячі чипів / імпульсів) для придушення шуму.", size=11, color=MUTED, anchor="start"))

    for k in range(5):
        bx = 55 + k * 85
        parts.append(rect(bx, 340, 75, 42, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
        parts.append(text(bx + 37, 357, "T_coh #%d" % (k + 1), size=11, color=INK, bold=True))
        parts.append(text(bx + 37, 372, "1–20 мс", size=9, color=MUTED))
    
    parts.append(arrow(55, 396, 470, 396, color=POS, sw=1.8))
    parts.append(arrow(470, 396, 55, 396, color=POS, sw=1.8))
    parts.append(text(262, 412, "Повний час вимірювання T_meas = M \u00d7 T_coh (10 мс – 1 с)", size=11, color=POS, anchor="middle", bold=True))

    b3, _, _ = textbox(595, 350, "Керує SNR та CRLB\nВизначає затримку", size=11, fill="#fef3c7", stroke="#d97706", pad=8)
    parts.append(b3)

    cap = "Три рівні часу: фазовий (довжина хвилі), груповий (затримка імпульсу) та час вимірювання (інтервал накопичення)."
    parts.append(fitbox(30, H - 42, W - 60, 26, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'time-domains.svg'), W, H,
                  *parts, title='Три виміри часу в радіофізиці')


# ── Фігура 2: Когерентне проти некогерентного накопичення ─────────────────────
def fig_coherent_vs_noncoherent():
    W, H = 720, 440
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Ліва колонка: Когерентне накопичення
    parts.append(rect(30, 35, 315, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(187, 58, "Когерентне накопичення (T_coh)", size=13, color=NEG, bold=True))
    parts.append(text(187, 76, "Додавання комплексних відліків I + jQ", size=11, color=MUTED))

    vx0, vy0 = 70, 160
    vecs = [(40, -10), (38, -8), (42, -12), (39, -9)]
    cx, cy = vx0, vy0
    for i, (dx, dy) in enumerate(vecs):
        parts.append(arrow(cx, cy, cx + dx, cy + dy, color=NEG, sw=1.8))
        cx += dx
        cy += dy
    
    parts.append(arrow(vx0, vy0 + 35, cx, cy + 35, color=POS, sw=2.5))
    parts.append(text(vx0 + (cx - vx0)/2, vy0 + 58, "Сигнал: V = N \u00d7 v\u2080 (потужність N\u00b2)", size=11, color=POS, bold=True))
    parts.append(text(187, 245, "Шум додається випадково: \u03c3\u00b2_noise = N \u00d7 \u03c3\u2080\u00b2", size=11, color=INK))
    parts.append(text(187, 270, "Виграш SNR: +10 lg(N) дБ (ідеальний)", size=12, color=FIELD, bold=True))

    parts.append(fitbox(45, 300, 285, 60,
                         "Обмеження: доплерівський зсув \u0394f,\nманіпуляція навігаційних бітів (20 мс),\nфазовий шум генератора.",
                         size=10, fill="#eff6ff", stroke=NEG))

    # Права колонка: Некогерентне накопичення
    parts.append(rect(375, 35, 315, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(532, 58, "Некогерентне накопичення (M блоків)", size=13, color=POS, bold=True))
    parts.append(text(532, 76, "Додавання потужностей: \u2211 |I_m + jQ_m|\u00b2", size=11, color=MUTED))

    for k in range(4):
        bx = 405 + k * 68
        parts.append(rect(bx, 120, 56, 36, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
        parts.append(text(bx + 28, 137, "|S_%d|\u00b2" % (k + 1), size=11, color=INK, bold=True))
        if k < 3:
            parts.append(text(bx + 62, 142, "+", size=14, color=POS, bold=True))
    
    parts.append(text(532, 185, "Фазова чутливість відсутня (\u03c6 знищується)", size=11, color=INK))
    parts.append(text(532, 215, "При низькому вхідному SNR (SNR < 1):", size=11, color=MUTED))
    parts.append(text(532, 235, "Шум \u00d7 шум домінує \u2192 втрати квадратування", size=11, color=POS, bold=True))
    parts.append(text(532, 270, "Виграш SNR \u2248 +5 lg(M) дБ (\u223c \u221aM)", size=12, color="#d97706", bold=True))

    parts.append(fitbox(390, 300, 285, 60,
                         "Перевага: проходить крізь межі бітів,\nстійке до нескомпенсованого Доплера,\nдозволяє нарощувати час T_meas.",
                         size=10, fill="#fef2f2", stroke=POS))

    cap = "Когерентне накопичення дає виграш N завдяки фазовій узгодженості, некогерентне додає потужності з виграшем близько \u221aM."
    parts.append(fitbox(30, H - 42, W - 60, 26, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'coherent-vs-noncoherent.svg'), W, H,
                  *parts, title='Когерентне проти некогерентного накопичення')


# ── Фігура 3: Час когерентності каналу та доплерівське розширення ────────────
def fig_coherence_time_doppler():
    W, H = 720, 420
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    parts.append(rect(30, 35, 300, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(180, 58, "Динамічний канал з розсіювачами", size=13, color=INK, bold=True))

    parts.append(rect(60, 150, 48, 28, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    parts.append(text(84, 168, "Rx (v)", size=11, color=NEG, bold=True))
    parts.append(arrow(108, 164, 150, 164, color=POS, sw=2))
    parts.append(text(130, 154, "швидкість v", size=10, color=POS))

    parts.append(circle(270, 100, 12, fill="#fef2f2", stroke=POS, sw=1.5))
    parts.append(text(270, 126, "Tx", size=11, color=POS, bold=True))

    parts.append(rect(230, 220, 32, 24, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    parts.append(text(246, 236, "відбивач", size=9, color=MUTED))

    parts.append(line(260, 106, 108, 155, color=FIELD, sw=1.8))
    parts.append(text(190, 120, "прямий промінь (f\u2080 + f_d1)", size=9, color=FIELD))

    parts.append(line(265, 112, 246, 220, color="#d97706", sw=1.5, dash="4 3"))
    parts.append(line(246, 220, 108, 170, color="#d97706", sw=1.5, dash="4 3"))
    parts.append(text(190, 205, "відбитий (f\u2080 - f_d2)", size=9, color="#d97706"))

    parts.append(fitbox(45, 270, 270, 70,
                         "Доплерівський розкид:\nB_d = 2 \u00d7 f_{d,max} = 2 \u00d7 (v / \u03bb)\nЧас когерентності каналу:\nT_c \u2248 1 / B_d \u2248 \u03bb / (2 v)",
                         size=10, fill="#ffffff", stroke="#cbd5e1"))

    parts.append(rect(350, 35, 340, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(520, 58, "Межа когерентного накопичення", size=13, color=INK, bold=True))

    parts.append(arrow(370, 220, 665, 220, color=LINE, sw=1.5))
    parts.append(text(640, 236, "Час T_int", size=10, color=MUTED))

    parts.append(line(500, 75, 500, 235, color=POS, sw=1.8, dash="4 4"))
    parts.append(text(500, 252, "T_int = T_c (час когерентності)", size=11, color=POS, bold=True))

    parts.append(rect(375, 80, 120, 130, fill="#ecfdf5", stroke="none", rx=0))
    parts.append(text(435, 110, "Зона 1: T_int < T_c", size=11, color=FIELD, bold=True))
    parts.append(text(435, 130, "Фаза стабільна", size=10, color=MUTED))
    parts.append(text(435, 150, "Виграш SNR \u223c T_int", size=10, color=FIELD))
    parts.append(text(435, 175, "Конструктивна\nінтерференція", size=10, color=INK))

    parts.append(rect(505, 80, 150, 130, fill="#fef2f2", stroke="none", rx=0))
    parts.append(text(580, 110, "Зона 2: T_int > T_c", size=11, color=POS, bold=True))
    parts.append(text(580, 130, "Фази променів обертаються", size=10, color=MUTED))
    parts.append(text(580, 150, "Вектори віднімаються!", size=10, color=POS))
    parts.append(text(580, 175, "SNR падає,\nсигнал гасне", size=10, color=POS, bold=True))

    parts.append(fitbox(365, 275, 310, 65,
                         "Правило проектування:\nКогерентне вікно T_coh НЕ повинно перевищувати T_c.\nДля більшого T_meas застосовують некогерентні блоки.",
                         size=10, fill="#ffffff", stroke="#cbd5e1"))

    cap = "Час когерентності каналу T_c обмежує тривалість неперервного когерентного накопичення в динамічному середовищі."
    parts.append(fitbox(30, H - 42, W - 60, 26, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'coherence-time-doppler.svg'), W, H,
                  *parts, title='Час когерентності каналу та доплерівське розширення')


# ── Фігура 4: Компроміс Крамера–Рао: Точність проти Динаміки ─────────────────
def fig_crlb_tradeoff():
    W, H = 720, 440
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    parts.append(text(W / 2, 42, "Компроміс межі Крамера–Рао: Шум проти Динамічного запізнення", size=14, color=INK, bold=True))

    ox, oy = 80, 330
    gw, gh = 580, 250
    parts.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    parts.append(arrow(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    parts.append(text(ox + gw - 40, oy + 25, "Час вимірювання T_meas", size=12, color=INK, bold=True))
    parts.append(text(ox - 10, oy - gh + 15, "Похибка \u03c3_\u03c4", size=12, color=INK, anchor="end", bold=True))

    crlb_pts = []
    for i in range(20, 520, 5):
        t = i / 50.0
        val = 180.0 / math.sqrt(t + 0.2) + 20
        crlb_pts.append((ox + i, oy - val))
    for i in range(len(crlb_pts) - 1):
        parts.append(line(crlb_pts[i][0], crlb_pts[i][1], crlb_pts[i+1][0], crlb_pts[i+1][1], color=NEG, sw=2.2))
    
    parts.append(text(ox + 120, oy - 180, "Шумова похибка (CRLB \u223c 1/\u221aT_meas)", size=11, color=NEG, bold=True))

    dyn_pts = []
    for i in range(20, 520, 5):
        t = i / 50.0
        val = 2.2 * (t ** 2) + 15
        dyn_pts.append((ox + i, oy - val))
    for i in range(len(dyn_pts) - 1):
        parts.append(line(dyn_pts[i][0], dyn_pts[i][1], dyn_pts[i+1][0], dyn_pts[i+1][1], color=POS, sw=2.2))
    
    parts.append(text(ox + 460, oy - 190, "Динамічне запізнення (\u223c a\u00b7T\u00b2)", size=11, color=POS, bold=True))

    tot_pts = []
    for i in range(20, 520, 5):
        t = i / 50.0
        v_crlb = 180.0 / math.sqrt(t + 0.2) + 20
        v_dyn = 2.2 * (t ** 2) + 15
        v_tot = math.sqrt(v_crlb**2 + v_dyn**2) - 15
        tot_pts.append((ox + i, oy - v_tot))
    for i in range(len(tot_pts) - 1):
        parts.append(line(tot_pts[i][0], tot_pts[i][1], tot_pts[i+1][0], tot_pts[i+1][1], color=FIELD, sw=2.8))
    
    parts.append(text(ox + 270, oy - 235, "Повна похибка (RMSE)", size=12, color=FIELD, bold=True))

    opt_x = ox + 225
    opt_y = oy - 110
    parts.append(line(opt_x, oy, opt_x, opt_y, color=LINE, sw=1.2, dash="3 3"))
    parts.append(circle(opt_x, opt_y, 5, fill=FIELD, stroke=INK, sw=1.5))
    
    b_opt, _, _ = textbox(opt_x, opt_y - 25, "Оптимум T_meas,opt", size=11, fill="#ecfdf5", stroke=FIELD, pad=6)
    parts.append(b_opt)

    parts.append(text(ox + 80, oy + 18, "Малий T (швидке оновлення)", size=10, color=MUTED))
    parts.append(text(ox + 420, oy + 18, "Великий T (висока чутливість)", size=10, color=MUTED))

    cap = "Компроміс між тепловим шумом і динамічним запізненням визначає оптимальний час вимірювання для заданого прискорення."
    parts.append(fitbox(30, H - 42, W - 60, 26, cap, size=11, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'crlb-tradeoff.svg'), W, H,
                  *parts, title='Компроміс межі Крамера–Рао')


if __name__ == '__main__':
    fig_time_domains()
    fig_coherent_vs_noncoherent()
    fig_coherence_time_doppler()
    fig_crlb_tradeoff()
    print("All figures generated successfully.")
