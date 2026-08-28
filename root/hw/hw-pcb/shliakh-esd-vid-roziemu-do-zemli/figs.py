# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Шлях ESD від роз'єму до землі'."""

import os
import sys

# Підключення svgkit із кореневої теки scripts (4 рівні вгору від root/hw/hw-pcb/shliakh-esd-vid-roziemu-do-zemli)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_iec_waveform():
    """Фігура 1: Еталонний імпульс струму ESD за стандартом IEC 61000-4-2 (8 кВ контактний розряд)."""
    w, h = 840, 480
    frags = []

    # Тло
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 38, "Еталонна форма імпульсу розрядного струму IEC 61000-4-2 (8 кВ)", size=16, bold=True))

    # Область графіка
    gx, gy, gw, gh = 90, 80, 700, 260
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))

    # y-scale: 0 A -> gy+gh (340), 35 A -> gy+20 (100).
    def y_amp(a):
        return gy + gh - (a / 35.0) * (gh - 25)

    # x-scale: шкала часу (0..100 нс)
    def x_time(t):
        if t <= 0:
            return gx + 30
        elif t <= 2.0:
            return gx + 30 + (t / 2.0) * 150
        elif t <= 10.0:
            return gx + 180 + ((t - 2.0) / 8.0) * 130
        elif t <= 30.0:
            return gx + 310 + ((t - 10.0) / 20.0) * 140
        elif t <= 60.0:
            return gx + 450 + ((t - 30.0) / 30.0) * 130
        else:
            return gx + 580 + (min(t - 60.0, 40.0) / 40.0) * 120

    # Горизонтальні лінії сітки
    for amp in [0, 8, 16, 20, 30]:
        yy = y_amp(amp)
        frags.append(line(gx, yy, gx + gw, yy, color="#e2e8f0", sw=1, dash="3,3" if amp > 0 else None))
        frags.append(text(gx - 12, yy + 4, f"{amp} А", size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії ключових точок часу
    key_times = [
        (0.9, "0.9 нс (t_r)", "#dc2626"),
        (30.0, "30 нс", "#2563eb"),
        (60.0, "60 нс", "#059669"),
        (100.0, "100 нс", MUTED),
    ]
    for kt, label, col in key_times:
        xx = x_time(kt)
        frags.append(line(xx, gy, xx, gy + gh, color="#e2e8f0", sw=1, dash="3,3"))
        frags.append(text(xx, gy + gh + 18, label, size=11, color=col, anchor="middle", bold=(kt < 70)))

    # Крива розряду IEC 61000-4-2
    pts = [
        (0.0, 0.0), (0.2, 5.0), (0.5, 18.0), (0.9, 30.0), (1.4, 25.5),
        (2.5, 21.0), (5.0, 18.2), (10.0, 17.0), (20.0, 16.5), (30.0, 16.0),
        (45.0, 11.8), (60.0, 8.0), (80.0, 4.2), (100.0, 1.8)
    ]
    path_d = ["M"]
    for i, (pt_t, pt_a) in enumerate(pts):
        px = x_time(pt_t)
        py = y_amp(pt_a)
        if i == 0:
            path_d.append(f"{px:.1f} {py:.1f}")
        else:
            path_d.append(f"L {px:.1f} {py:.1f}")

    # Заливка під кривою
    fill_d = list(path_d)
    fill_d.append(f"L {x_time(100.0):.1f} {y_amp(0):.1f} L {x_time(0.0):.1f} {y_amp(0):.1f} Z")
    frags.append(f'<path d="{" ".join(fill_d)}" fill="#fee2e2" opacity="0.4"/>')
    frags.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="{POS}" stroke-width="2.8"/>')

    # Маркери на ключових точках
    # 1. Перший пік (0.9 нс, 30 А)
    p1x, p1y = x_time(0.9), y_amp(30.0)
    frags.append(circle(p1x, p1y, 4.5, fill=POS, stroke="#991b1b", sw=1.5))
    frags.append(arrow(p1x + 70, p1y - 15, p1x + 8, p1y - 3, color=POS, sw=1.5))
    frags.append(text(p1x + 75, p1y - 18, "I_peak = 30 A (фронт t_r ≤ 1.0 нс)", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(p1x + 75, p1y - 3, "Швидкий струм ємнісного розряду наконечника", size=10, color=MUTED, anchor="start"))

    # 2. Другий пік (30 нс, 16 А)
    p2x, p2y = x_time(30.0), y_amp(16.0)
    frags.append(circle(p2x, p2y, 4, fill=NEG, stroke="#1e40af", sw=1.5))
    frags.append(arrow(p2x + 40, p2y - 25, p2x + 6, p2y - 5, color=NEG, sw=1.5))
    frags.append(text(p2x + 45, p2y - 28, "I_30ns = 16 A (±30%)", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(text(p2x + 45, p2y - 14, "Розряд основної ємності тіла (150 пФ)", size=10, color=MUTED, anchor="start"))

    # 3. Хвіст (60 нс, 8 А)
    p3x, p3y = x_time(60.0), y_amp(8.0)
    frags.append(circle(p3x, p3y, 4, fill=FIELD, stroke="#166534", sw=1.5))
    frags.append(text(p3x + 10, p3y - 10, "I_60ns = 8 A (±30%)", size=11, color=FIELD, bold=True, anchor="start"))

    # Нижній блок параметрів стандарту
    pbox, _, _ = textbox(w / 2, 415,
                         "Параметри стандарту IEC 61000-4-2 (Рівень 4, контактний розряд 8 кВ / повітряний 15 кВ):\n"
                         "• Піковий струм I_peak = 30 А ± 10% · Час наростання t_r = 0.7–1.0 нс (di/dt ≈ 30–40 А/нс)\n"
                         "• Еквівалент генератора: C_esd = 150 пФ, R_esd = 330 Ом · Спектр імпульсу: від DC до 1.5 ГГц\n"
                         "• Внутрішній захист чипів (HBM 2 кВ) витримує лише 1.3 А — необхідний зовнішній TVS на платі!",
                         size=11, pad=10, fill="#f8fafc", stroke="#cbd5e1", min_w=780)
    frags.append(pbox)

    render(os.path.join(IMG_DIR, "iec-61000-4-2-waveform.svg"), w, h, *frags)


def fig_tvs_routing():
    """Фігура 2: Порівняння топології трасування TVS: небезпечне відгалуження (Stub) проти прохідного трасування."""
    w, h = 840, 520
    frags = []

    # Тло
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Топологія трасування TVS-діода: небезпечний Stub проти прохідного шляху", size=16, bold=True))

    # Ліва панель: НЕПРАВИЛЬНО (Stub-трасування)
    lx, ly, lw, lh = 30, 65, 375, 330
    frags.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(rect(lx, ly, lw, 30, fill="#fee2e2", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(lx + lw / 2, ly + 20, "НЕПРАВИЛЬНО: Т-подібний Stub і довга земля", size=12, color="#991b1b", bold=True))

    # Роз'єм ліворуч
    frags.append(rect(lx + 20, ly + 60, 55, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    frags.append(text(lx + 47, ly + 95, "Роз'єм", size=11, bold=True))

    # Сигнальна лінія йде прямо до мікроконтролера
    frags.append(rect(lx + 280, ly + 60, 75, 75, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(lx + 317, ly + 95, "MCU / IC", size=11, bold=True))
    frags.append(text(lx + 317, ly + 112, "Вхід I/O", size=10, color=MUTED))

    # Пряма доріжка від роз'єму до MCU
    frags.append(line(lx + 75, ly + 90, lx + 280, ly + 90, color="#ea580c", sw=3.5))

    # Т-подібне відгалуження (Stub) вниз до TVS
    frags.append(line(lx + 160, ly + 90, lx + 160, ly + 180, color=POS, sw=2.5, dash="4,2"))
    frags.append(text(lx + 200, ly + 135, "Stub (L_stub ≈ 4 нГн)", size=10, color=POS, bold=True))

    # TVS-діод унизу
    frags.append(rect(lx + 135, ly + 180, 50, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(lx + 160, ly + 205, "TVS", size=11, bold=True, color="#92400e"))

    # Довга тонка доріжка до одного перехідного отвору GND
    frags.append(line(lx + 160, ly + 220, lx + 160, ly + 270, color=POS, sw=2, dash="3,2"))
    frags.append(circle(lx + 160, ly + 275, 5, fill="#94a3b8", stroke="#475569", sw=1.5))
    frags.append(text(lx + 225, ly + 278, "1 Via (L_via ≈ 1.2 нГн)", size=10, color=POS))

    # Стрілка струму ESD, що пробиває в MCU
    frags.append(arrow(lx + 80, ly + 78, lx + 270, ly + 78, color=POS, sw=2.5))
    frags.append(text(lx + 175, ly + 70, "I_ESD проривається в MCU!", size=10, color=POS, bold=True))
    frags.append(text(lx + lw / 2, ly + 315, "V_peak = V_clamp + (L_stub + L_via)·(di/dt) > 150 В!", size=11, color=POS, bold=True))

    # Права панель: ПРАВИЛЬНО (Прохідне трасування)
    rx, ry, rw, rh = 435, 65, 375, 330
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    frags.append(rect(rx, ry, rw, 30, fill="#dcfce7", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(rx + rw / 2, ry + 20, "ПРАВИЛЬНО: Прохідне трасування (Feedthrough)", size=12, color="#166534", bold=True))

    # Роз'єм праворуч
    frags.append(rect(rx + 20, ry + 60, 55, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    frags.append(text(rx + 47, ry + 95, "Роз'єм", size=11, bold=True))

    # TVS прямо на шляху сигналу (Pad 1 вхід, Pad 2 вихід)
    frags.append(rect(rx + 115, ry + 70, 50, 40, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=3))
    frags.append(text(rx + 140, ry + 95, "TVS", size=11, bold=True, color="#15803d"))

    # Вхідна доріжка (коротка, широка)
    frags.append(line(rx + 75, ry + 90, rx + 115, ry + 90, color="#16a34a", sw=4))

    # Кілька паралельних via прямо з контактної площадки GND діода
    frags.append(rect(rx + 115, ry + 125, 50, 45, fill="#cbd5e1", stroke="#475569", sw=1, rx=2))
    frags.append(circle(rx + 127, ry + 140, 4, fill="#475569", stroke="#1e293b", sw=1))
    frags.append(circle(rx + 153, ry + 140, 4, fill="#475569", stroke="#1e293b", sw=1))
    frags.append(circle(rx + 127, ry + 158, 4, fill="#475569", stroke="#1e293b", sw=1))
    frags.append(circle(rx + 153, ry + 158, 4, fill="#475569", stroke="#1e293b", sw=1))
    frags.append(text(rx + 225, ry + 148, "4x Via на суцільний GND", size=10, color=FIELD, bold=True))
    frags.append(text(rx + 225, ry + 162, "L_gnd < 0.25 нГн", size=10, color=MUTED))

    # Послідовний резистор (R_series) для розв'язки
    frags.append(rect(rx + 200, ry + 80, 40, 20, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    frags.append(text(rx + 220, ry + 94, "R_s", size=10, bold=True, color="#92400e"))

    # Доріжка від TVS через R_s до MCU
    frags.append(line(rx + 165, ry + 90, rx + 200, ry + 90, color="#16a34a", sw=2.5))
    frags.append(line(rx + 240, ry + 90, rx + 285, ry + 90, color="#16a34a", sw=2.5))

    # MCU
    frags.append(rect(rx + 285, ry + 60, 75, 75, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(rx + 322, ry + 95, "MCU / IC", size=11, bold=True))
    frags.append(text(rx + 322, ry + 112, "Вхід I/O", size=10, color=MUTED))

    # Струм ESD скидається в полігон GND без перенапруги
    frags.append(arrow(rx + 85, ry + 82, rx + 135, ry + 130, color=FIELD, sw=2.8))
    frags.append(text(rx + rw / 2, ry + 315, "V_peak = V_clamp + L_gnd·(di/dt) ≈ 12–15 В (Безпечно!)", size=11, color=FIELD, bold=True))

    # Нижній підсумок
    box_rule, _, _ = textbox(w / 2, 455,
                             "Золоті правила трасування шляху ESD від роз'єму:\n"
                             "1. Розміщувати TVS впритул до контактів роз'єму — до будь-яких резисторів, феритів або мікросхем.\n"
                             "2. Трасувати сигнал КРІЗЬ площадки TVS (нульова довжина Stub L_stub = 0 нГн).\n"
                             "3. Мінімум 2–4 перехідні отвори прямо на виводі GND діода до суцільного шару землі шасі / GND.",
                             size=11, pad=10, fill="#f8fafc", stroke="#cbd5e1", min_w=780)
    frags.append(box_rule)

    render(os.path.join(IMG_DIR, "tvs-routing-topology.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_iec_waveform()
    fig_tvs_routing()
    print("Згенеровано фігури для теми 'Шлях ESD від роз'єму до землі'.")
