# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Допоміжні функції ────────────────────────────────────────────────────────

def axes(x0, y0, w, h, xlabel, ylabel):
    """Осі X та Y з підписами."""
    s = line(x0, y0, x0 + w, y0, color=LINE, sw=1.5)
    s += line(x0, y0, x0, y0 - h, color=LINE, sw=1.5)
    s += text(x0 + w, y0 + 18, xlabel, size=11, color=MUTED, anchor="end")
    s += text(x0 - 8, y0 - h - 8, ylabel, size=11, color=MUTED, anchor="start")
    return s

def draw_grid(x0, y0, w, h, nx=5, ny=4):
    """Сітка для графіків."""
    s = ""
    for i in range(1, nx + 1):
        x = x0 + i * (w / (nx + 1))
        s += line(x, y0, x, y0 - h, color="#e5e7eb", sw=1, dash="3 3")
    for j in range(1, ny + 1):
        y = y0 - j * (h / (ny + 1))
        s += line(x0, y, x0 + w, y, color="#e5e7eb", sw=1, dash="3 3")
    return s


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Три джерела вібрації ротора
# ════════════════════════════════════════════════════════════════════════════
def fig_imbalance_types():
    W, H = 840, 360
    pw = 250
    gap = 25
    x_start = 25
    body = ""

    panels = [
        ("Статичний дисбаланс", [
            ("Центр мас зміщений на e", MUTED),
            ("Сила F = m·e·ω²", POS),
            ("Частота збудження: 1× RPM", INK),
            ("Тягне вал у радіальний бік", MUTED),
        ]),
        ("Динамічний (моментний)", [
            ("Вісь інерції нахилена на α", MUTED),
            ("Пара сил, момент M = F·l", POS),
            ("Частота збудження: 1× RPM", INK),
            ("Розхитує підшипники на згин", MUTED),
        ]),
        ("Аеродинамічний дисбаланс", [
            ("Різний крок/форма лопатей", MUTED),
            ("Різниця тяги ΔT = T₁ − T₂", POS),
            ("Частота збудження: 1× RPM", INK),
            ("Пульсація тяги й перекидання", MUTED),
        ]),
    ]

    for idx, (title, notes) in enumerate(panels):
        px = x_start + idx * (pw + gap)
        py = 50
        ph = 280

        # Рамка панелі
        body += rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8)
        body += text(px + pw / 2, py + 24, title, size=13, color=INK, bold=True)

        # Схематичні малюнки
        cx = px + pw / 2
        cy = py + 95

        if idx == 0:
            # Статичний: коло (ротор), вісь обертання, зміщений центр мас
            body += circle(cx, cy, 40, fill="#ffffff", stroke=LINE, sw=1.5)
            body += line(cx - 48, cy, cx + 48, cy, color="#cbd5e1", sw=1, dash="2 2")
            body += line(cx, cy - 48, cx, cy + 48, color="#cbd5e1", sw=1, dash="2 2")
            # Геометричний центр
            body += circle(cx, cy, 3, fill=INK, stroke=INK, sw=1)
            body += text(cx - 8, cy - 8, "O", size=10, color=INK, bold=True)
            # Зміщений центр мас (важка точка)
            mx = cx + 18
            my = cy - 14
            body += line(cx, cy, mx, my, color=POS, sw=1.5)
            body += circle(mx, my, 6, fill=POS, stroke=POS, sw=1)
            body += text(mx + 8, my - 4, "m (центр мас)", size=10, color=POS, bold=True, anchor="start")
            body += text(cx + 8, cy + 14, "e", size=10, color=POS, italic=True)
            # Вектор відцентрової сили
            body += arrow(mx, my, mx + 24, my - 18, color=POS, sw=2)
            body += text(mx + 28, my - 20, "F_c", size=11, color=POS, bold=True, anchor="start")

        elif idx == 1:
            # Динамічний: похилий вал / дві рознесені важкі точки
            body += line(cx, cy - 45, cx, cy + 45, color=LINE, sw=2) # вісь обертання
            body += text(cx + 8, cy - 42, "вісь обертання", size=9.5, color=MUTED, anchor="start")
            # Нахилена вісь інерції
            body += line(cx - 25, cy - 40, cx + 25, cy + 40, color=NEG, sw=1.5, dash="3 3")
            body += text(cx - 28, cy - 38, "вісь інерції", size=9.5, color=NEG, anchor="end")
            # Важкі точки зверху справа та знизу зліва
            p1x, p1y = cx + 22, cy - 25
            p2x, p2y = cx - 22, cy + 25
            body += circle(p1x, p1y, 5, fill=POS, stroke=POS, sw=1)
            body += circle(p2x, p2y, 5, fill=POS, stroke=POS, sw=1)
            # Сили пари
            body += arrow(p1x, p1y, p1x + 20, p1y, color=POS, sw=1.8)
            body += arrow(p2x, p2y, p2x - 20, p2y, color=POS, sw=1.8)
            body += text(p1x + 23, p1y + 4, "F", size=10, color=POS, bold=True, anchor="start")
            body += text(p2x - 23, p2y + 4, "F", size=10, color=POS, bold=True, anchor="end")
            # Плече моменту l
            body += line(cx - 8, p1y, cx - 8, p2y, color=MUTED, sw=1)
            body += text(cx - 14, cy + 4, "l", size=10, color=MUTED, italic=True, anchor="end")

        else:
            # Аеродинамічний: дві лопаті з різним кутом атаки
            body += circle(cx, cy, 8, fill=INK, stroke=INK, sw=1)
            # Ліва лопать (кут theta 1)
            body += line(cx, cy, cx - 60, cy - 10, color=LINE, sw=4)
            body += arrow(cx - 40, cy - 8, cx - 40, cy - 42, color=FIELD, sw=2)
            body += text(cx - 40, cy - 46, "T₁ (більша)", size=10, color=FIELD, bold=True)
            # Права лопать (кут theta 2 менший)
            body += line(cx, cy, cx + 60, cy + 5, color=LINE, sw=4)
            body += arrow(cx + 40, cy + 3, cx + 40, cy - 20, color=MUTED, sw=1.5)
            body += text(cx + 40, cy - 24, "T₂ (менша)", size=10, color=MUTED, bold=True)
            # Результуючий дисбаланс тяги
            body += text(cx, cy + 35, "ΔT = T₁ − T₂ ≠ 0", size=11, color=POS, bold=True)

        # Текстовий блок із формулами та поясненнями
        ty = py + 180
        for n_title, col in notes:
            body += circle(px + 18, ty - 4, 3, fill=col, stroke=col, sw=1)
            body += text(px + 28, ty, n_title, size=11, color=col, anchor="start")
            ty += 23

    render(os.path.join(OUT, "imbalance-types.svg"), W, H, body,
           title="Три фундаментальні джерела вібрації пропелера й мотора")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Магнітний стенд статичного балансування
# ════════════════════════════════════════════════════════════════════════════
def fig_magnetic_balancer():
    W, H = 800, 340
    body = ""

    # Ліва частина: Горизонтальне балансування (маса лопатей)
    # Права частина: Вертикальне балансування (маточина / hub)
    panels = [
        (40, "1. Горизонтальний тест: маса лопатей", [
            "Вал підвішений у магнітному полі (нульове тертя кочення)",
            "Важча лопать під дією гравітації падає вниз",
            "Усунення: шліфування важкої або скотч на легку лопать",
        ]),
        (430, "2. Вертикальний тест: важка маточина (hub)", [
            "Лопаті виставляються строго вертикально під 90°",
            "Якщо маточина асиметрична — гвинт сповзає вбік",
            "Усунення: крапля клею / скотч на легкий бік маточини",
        ]),
    ]

    for px, title, notes in panels:
        pw = 330
        py = 50
        ph = 270
        body += rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8)
        body += text(px + pw / 2, py + 24, title, size=12, color=INK, bold=True)

        cx = px + pw / 2
        cy = py + 95

        if px == 40:
            # Стенд: дві стійки з неодимовими магнітами
            body += rect(cx - 100, cy - 35, 16, 70, fill="#cbd5e1", stroke=LINE, sw=1.5)
            body += rect(cx + 84, cy - 35, 16, 70, fill="#cbd5e1", stroke=LINE, sw=1.5)
            body += circle(cx - 84, cy, 6, fill=POS, stroke=POS, sw=1) # магніт ліворуч
            body += circle(cx + 84, cy, 6, fill=NEG, stroke=NEG, sw=1) # магніт праворуч
            # Вал на вістрі
            body += line(cx - 78, cy, cx + 78, cy, color=LINE, sw=2.5)
            # Горизонтальний пропелер з нахилом
            body += line(cx - 60, cy - 18, cx + 60, cy + 18, color=INK, sw=4)
            body += circle(cx, cy, 8, fill=INK, stroke=INK, sw=1) # маточина
            # Позначки важка/легка
            body += text(cx + 64, cy + 34, "Важка лопать (падає)", size=10, color=POS, bold=True, anchor="middle")
            body += arrow(cx + 50, cy + 16, cx + 50, cy + 30, color=POS, sw=1.5)
            body += text(cx - 64, cy - 24, "Легка лопать", size=10, color=FIELD, bold=True, anchor="middle")
        else:
            # Вертикальний пропелер
            body += rect(cx - 100, cy - 35, 16, 70, fill="#cbd5e1", stroke=LINE, sw=1.5)
            body += rect(cx + 84, cy - 35, 16, 70, fill="#cbd5e1", stroke=LINE, sw=1.5)
            body += line(cx - 78, cy, cx + 78, cy, color=LINE, sw=2.5)
            # Лопаті вертикально
            body += line(cx, cy - 45, cx, cy + 45, color=INK, sw=4)
            body += circle(cx, cy, 8, fill=INK, stroke=INK, sw=1)
            # Зміщений центр маточини
            body += circle(cx + 10, cy, 4, fill=POS, stroke=POS, sw=1)
            body += text(cx + 18, cy - 8, "Важкий бік", size=9.5, color=POS, bold=True, anchor="start")
            # Стрілка обертання
            body += arrow(cx + 25, cy + 15, cx + 25, cy + 32, color=POS, sw=1.5)
            body += text(cx, cy + 60, "Повертається під вагою маточини", size=10, color=POS, bold=True)

        # Нотатки
        ty = py + 185
        for note in notes:
            body += circle(px + 16, ty - 4, 2.5, fill=LINE, stroke=LINE, sw=1)
            body += text(px + 24, ty, note, size=10.5, color=INK, anchor="start")
            ty += 22

    render(os.path.join(OUT, "magnetic-balancer.svg"), W, H, body,
           title="Статичне балансування на магнітному підвісі з нульовим тертям")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Векторний метод динамічного балансування
# ════════════════════════════════════════════════════════════════════════════
def fig_in_situ_vector_balancing():
    W, H = 820, 380
    body = ""

    # Ліва панель: Комплексна площина та векторна діаграма
    # Права панель: Фізична схема на моторі
    w1 = 440
    body += rect(30, 45, w1, 315, fill=FILL, stroke=LINE, sw=1.5, rx=8)
    body += text(30 + w1 / 2, 68, "Векторний розрахунок у комплексній площині", size=12, color=INK, bold=True)

    # Центр комплексної площини
    ox, oy = 240, 215
    # Осі Re / Im
    body += line(ox - 160, oy, ox + 160, oy, color="#94a3b8", sw=1.2)
    body += line(ox, oy + 120, ox, oy - 120, color="#94a3b8", sw=1.2)
    body += text(ox + 165, oy + 4, "Re", size=11, color=MUTED, anchor="start")
    body += text(ox, oy - 126, "Im", size=11, color=MUTED, anchor="middle")

    # Вектор V0 (базова вібрація)
    v0_x, v0_y = ox + 90, oy - 60
    body += arrow(ox, oy, v0_x, v0_y, color=NEG, sw=2.2)
    body += text(v0_x + 8, v0_y - 4, "V₀ (базова вібрація)", size=10.5, color=NEG, bold=True, anchor="start")

    # Вектор V1 (з пробним вантажем m_t на 0°)
    v1_x, v1_y = ox + 40, oy - 110
    body += arrow(ox, oy, v1_x, v1_y, color=MUTED, sw=1.8)
    body += text(v1_x - 6, v1_y - 8, "V₁ (з пробним вантажем)", size=10.5, color=MUTED, bold=True, anchor="end")

    # Вектор відгуку ΔV = V1 - V0
    body += arrow(v0_x, v0_y, v1_x, v1_y, color=POS, sw=2.2)
    body += text((v0_x + v1_x) / 2 + 10, (v0_y + v1_y) / 2 + 4, "ΔV = V₁ − V₀", size=11, color=POS, bold=True, anchor="start")

    # Вектор коригувального впливу V_corr = -V0
    vc_x, vc_y = ox - 90, oy + 60
    body += arrow(ox, oy, vc_x, vc_y, color=FIELD, sw=2.2)
    body += text(vc_x - 8, vc_y + 14, "−V₀ (мета компенсації)", size=10.5, color=FIELD, bold=True, anchor="end")

    # Формули знизу лівої панелі
    body += text(50, 335, "Маса коригування: m_c = m_t · (|V₀| / |ΔV|)", size=11, color=INK, bold=True, anchor="start")

    # Права панель: Фізичний ротор мотора
    w2 = 300
    px2 = 490
    body += rect(px2, 45, w2, 315, fill=FILL, stroke=LINE, sw=1.5, rx=8)
    body += text(px2 + w2 / 2, 68, "Фізичне розміщення на роторі", size=12, color=INK, bold=True)

    cx2, cy2 = px2 + w2 / 2, 180
    body += circle(cx2, cy2, 65, fill="#ffffff", stroke=LINE, sw=2)
    body += circle(cx2, cy2, 14, fill="#e2e8f0", stroke=LINE, sw=1.5) # вал

    # Мітка 0 градусів (фазовий маркер / оптичний датчик)
    body += line(cx2, cy2, cx2 + 75, cy2, color=LINE, sw=1.5, dash="2 2")
    body += text(cx2 + 82, cy2 + 4, "0° (мітка)", size=10.5, color=LINE, bold=True, anchor="start")

    # Пробний вантаж на 0 град
    body += circle(cx2 + 55, cy2, 7, fill=MUTED, stroke=MUTED, sw=1)
    body += text(cx2 + 55, cy2 - 12, "m_t (пробний)", size=10, color=MUTED, bold=True, anchor="middle")

    # Розрахований кут для m_c
    angle_c = 145 * math.pi / 180
    mc_x = cx2 - 55 * math.cos(angle_c - math.pi)
    mc_y = cy2 - 55 * math.sin(angle_c - math.pi)
    body += line(cx2, cy2, mc_x, mc_y, color=FIELD, sw=1.5, dash="3 3")
    body += circle(mc_x, mc_y, 8, fill=FIELD, stroke=FIELD, sw=1)
    body += text(mc_x - 10, mc_y - 12, "m_c (коригувальний)", size=10.5, color=FIELD, bold=True, anchor="end")

    # Дуга кута
    body += text(cx2, cy2 + 95, "Кут установки θ_c = arg(−V₀) − arg(ΔV)", size=10.5, color=FIELD, bold=True)
    body += text(cx2, 335, "Залишковий дисбаланс падає на 85–95%", size=11, color=POS, bold=True)

    render(os.path.join(OUT, "in-situ-vector-balancing.svg"), W, H, body,
           title="Динамічне балансування ротора за методом пробного вантажу")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Карта шумів Blackbox на спектрограмі
# ════════════════════════════════════════════════════════════════════════════
def fig_blackbox_spectrogram_map():
    W, H = 820, 420
    x0, y0 = 80, 340
    w_ax, h_ax = 680, 260
    body = ""

    # Осі: X — Положення газу (Throttle 0% .. 100%), Y — Частота (0 .. 800 Гц)
    body += axes(x0, y0, w_ax, h_ax, "Положення газу (Throttle, %)", "Частота вібрації (Гц)")
    body += draw_grid(x0, y0, w_ax, h_ax, nx=4, ny=3)

    # Підписи осей
    # По осі X
    for pct in [0, 25, 50, 75, 100]:
        xx = x0 + (pct / 100.0) * w_ax
        body += line(xx, y0, xx, y0 + 5, color=LINE, sw=1)
        body += text(xx, y0 + 18, "%d%%" % pct, size=10, color=MUTED)

    # По осі Y
    for f in [100, 200, 300, 400, 500, 600, 700, 800]:
        yy = y0 - (f / 800.0) * h_ax
        body += line(x0 - 5, yy, x0, yy, color=LINE, sw=1)
        body += text(x0 - 10, yy + 4, str(f), size=10, color=MUTED, anchor="end")

    # 1. Горизонтальна смуга: Механічний резонанс рами (фіксована частота 240 Гц)
    y_res = y0 - (240.0 / 800.0) * h_ax
    body += rect(x0, y_res - 10, w_ax, 20, fill="#fee2e2", stroke=POS, sw=1.5, rx=0)
    body += text(x0 + w_ax - 15, y_res + 4, "Механічний резонанс рами (фіксований пік 240 Гц)", size=11, color=POS, bold=True, anchor="end")

    # 2. Лінія 1x RPM (дисбаланс ротора/гвинта): повзе від 120 Гц до 450 Гц
    pts_1x = []
    for pct in range(0, 101, 5):
        t = pct / 100.0
        # RPM залежить від дроселя: f = 120 + 330 * sqrt(t)
        f_rpm = 120 + 330 * (t ** 0.8)
        xx = x0 + t * w_ax
        yy = y0 - (f_rpm / 800.0) * h_ax
        pts_1x.append("%.1f,%.1f" % (xx, yy))
    body += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="4" '
            'stroke-linecap="round"/>' % (" ".join(pts_1x), NEG))
    # Підпис 1x RPM
    body += text(x0 + 0.65 * w_ax, y0 - (380.0 / 800.0) * h_ax - 12,
                 "1× RPM (дисбаланс мотора/пропелера)", size=11, color=NEG, bold=True, anchor="start")

    # 3. Лінія BPF (Blade Pass Frequency = 3x RPM для 3-лопатевого гвинта): від 360 Гц до >800 Гц
    pts_bpf = []
    for pct in range(0, 75, 5):
        t = pct / 100.0
        f_bpf = 3 * (120 + 330 * (t ** 0.8))
        if f_bpf > 780:
            break
        xx = x0 + t * w_ax
        yy = y0 - (f_bpf / 800.0) * h_ax
        pts_bpf.append("%.1f,%.1f" % (xx, yy))
    body += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
            'stroke-dasharray="6 3" stroke-linecap="round"/>' % (" ".join(pts_bpf), FIELD))
    body += text(x0 + 0.38 * w_ax, y0 - (680.0 / 800.0) * h_ax,
                 "BPF = 3× RPM (лопатева частота)", size=11, color=FIELD, bold=True, anchor="start")

    # Точка збігу (перетин 1x RPM або BPF з резонансом рами)
    # 1x RPM перетинає 240 Гц при дроселі близько 28%
    rx_cross = x0 + 0.28 * w_ax
    body += circle(rx_cross, y_res, 8, fill="none", stroke=POS, sw=2.5)
    body += text(rx_cross + 14, y_res - 16, "Критична зона: 1× RPM збігається з резонансом!", size=10.5, color=POS, bold=True, anchor="start")

    # Легенда
    body += rect(x0 + 15, 45, 14, 14, fill=NEG, stroke=NEG, sw=1, rx=2)
    body += text(x0 + 35, 56, "1× RPM (динамічний пік)", size=10.5, color=INK, anchor="start")
    body += rect(x0 + 220, 45, 14, 14, fill=FIELD, stroke=FIELD, sw=1, rx=2)
    body += text(x0 + 240, 56, "BPF (N_blades × RPM)", size=10.5, color=INK, anchor="start")
    body += rect(x0 + 430, 45, 14, 14, fill="#fee2e2", stroke=POS, sw=1, rx=2)
    body += text(x0 + 450, 56, "Резонанс рами (статичний)", size=10.5, color=INK, anchor="start")

    render(os.path.join(OUT, "blackbox-spectrogram-map.svg"), W, H, body,
           title="Анатомія вібрацій на спектрограмі польотного контролера")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 — Вплив вібрації на D-терм регулятора та RPM-фільтр
# ════════════════════════════════════════════════════════════════════════════
def fig_vibration_to_dterm():
    W, H = 840, 330
    body = ""

    # Ланцюжок: Сирий гіроскоп -> Диференціювання d/dt (множення на 2*pi*f) -> D-терм розжарює мотори -> Порятунок: RPM-фільтр
    stages = [
        (30, "1. Сирий сигнал гіроскопа", [
            "Корисний сигнал керування: 1–20 Гц",
            "Шум дисбалансу мотора: 200–500 Гц",
            "Амплітуда шуму: мала (1–2°/с)",
        ], NEG),
        (290, "2. Диференціювання (D-терм)", [
            "Оператор d/dt = множення на 2πf",
            "Шум 300 Гц підсилюється у 300 разів!",
            "Високочастотний шум забиває керування",
        ], POS),
        (560, "3. RPM-фільтр (DShot Notch)", [
            "ESC віддає точний RPM мотора",
            "Вузький режекторний Notch на 1× і BPF",
            "Шум вирізано без затримки низьких частот",
        ], FIELD),
    ]

    for px, title, notes, col in stages:
        pw = 250
        py = 50
        ph = 250
        body += rect(px, py, pw, ph, fill=FILL, stroke=col, sw=2, rx=8)
        body += text(px + pw / 2, py + 24, title, size=12, color=col, bold=True)

        # Спектральний або часовий ескіз
        cx = px + pw / 2
        cy = py + 95

        if px == 30:
            # Спектр: великий корисний на 5 Гц, маленький шум на 300 Гц
            body += line(cx - 90, cy + 30, cx + 90, cy + 30, color=LINE, sw=1.2)
            # Корисний пік
            body += rect(cx - 70, cy - 20, 16, 50, fill=FIELD, stroke=FIELD, sw=1, rx=2)
            body += text(cx - 62, cy - 26, "Корисний (5 Гц)", size=9, color=FIELD, bold=True)
            # Шум мотора
            body += rect(cx + 40, cy + 15, 12, 15, fill=POS, stroke=POS, sw=1, rx=2)
            body += text(cx + 46, cy + 8, "Шум 300 Гц", size=9, color=POS, bold=True)

        elif px == 290:
            # Спектр D-терма: корисний лишився помірним, а шум зріс удесятеро!
            body += line(cx - 90, cy + 30, cx + 90, cy + 30, color=LINE, sw=1.2)
            # Корисний
            body += rect(cx - 70, cy + 5, 16, 25, fill=FIELD, stroke=FIELD, sw=1, rx=2)
            body += text(cx - 62, cy - 2, "5 Гц", size=9, color=FIELD, bold=True)
            # Роздутий шум D-терма
            body += rect(cx + 40, cy - 35, 16, 65, fill=POS, stroke=POS, sw=1, rx=2)
            body += text(cx + 48, cy - 42, "Шум × 300!", size=10, color=POS, bold=True)
            body += text(cx, cy + 46, "Мотори гріються, батарея тане", size=10, color=POS, bold=True)

        else:
            # Спектр з RPM-фільтром: яма (notch) точно на 300 Гц
            body += line(cx - 90, cy + 30, cx + 90, cy + 30, color=LINE, sw=1.2)
            # Корисний збережено
            body += rect(cx - 70, cy + 5, 16, 25, fill=FIELD, stroke=FIELD, sw=1, rx=2)
            body += text(cx - 62, cy - 2, "5 Гц чистий", size=9, color=FIELD, bold=True)
            # Режекторна вирізка
            body += text(cx + 40, cy - 10, "Notch -40 dB", size=9.5, color=FIELD, bold=True)
            body += line(cx + 40, cy + 28, cx + 40, cy + 5, color=FIELD, sw=2, dash="2 2")
            body += text(cx, cy + 46, "Затримка контуру < 2 мс", size=10, color=FIELD, bold=True)

        # Текстові нотатки
        ty = py + 165
        for note in notes:
            body += circle(px + 16, ty - 4, 2.5, fill=col, stroke=col, sw=1)
            body += text(px + 24, ty, note, size=10.5, color=INK, anchor="start")
            ty += 22

    # З'єднувальні стрілки між блоками
    body += arrow(282, 175, 288, 175, color=LINE, sw=2)
    body += arrow(542, 175, 558, 175, color=LINE, sw=2)

    render(os.path.join(OUT, "vibration-to-dterm.svg"), W, H, body,
           title="Як вібрація розхитує D-терм і як її вирізає RPM-фільтр")


# ════════════════════════════════════════════════════════════════════════════
# Запуск усіх генераторів
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_imbalance_types()
    fig_magnetic_balancer()
    fig_in_situ_vector_balancing()
    fig_blackbox_spectrogram_map()
    fig_vibration_to_dterm()
    print("OK: All vibration balancing figures rendered.")
