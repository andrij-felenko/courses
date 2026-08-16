# -*- coding: utf-8 -*-
"""Фігури до теми «Фібриляція шлуночків».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"

# ── Фігура 1: Нормальна провідність vs Фібриляція шлуночків ─────────────────
def fig_propagation_vs_fibrillation():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Синхронна провідність серця vs Автохвильовий хаос (Фібриляція)", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Нормальна провідність ---
    f.append(text(midx / 2, 54, "Нормальний синусовий ритм (один фронт)", size=13, bold=True, color=COLOR_GREEN))

    # Джерела та шлях
    b1, _, _ = textbox(100, 100, "SA-вузол\n(пейсмейкер)", size=11, pad=6, fill="#eafaf1", stroke=COLOR_GREEN)
    f.append(b1)

    f.append(arrow(100, 125, 100, 160, color=COLOR_GREEN, sw=1.8))

    b2, _, _ = textbox(100, 180, "AV-вузол &\nволокна Пуркіньє", size=11, pad=6, fill="#eafaf1", stroke=COLOR_GREEN)
    f.append(b2)

    # Плоский чистий фронт хвилі
    f.append(arrow(150, 180, 210, 180, color=COLOR_GREEN, sw=2))

    # Тканина шлуночків із синхронним фронтом
    f.append(rect(220, 90, 140, 180, fill="#f4fbf7", stroke=COLOR_GREEN, sw=1.5, rx=6))
    f.append(text(290, 110, "Міокард шлуночків", size=11, bold=True, color=COLOR_GREEN))

    # Фронт збудження (вертикальні лінії)
    f.append(line(240, 130, 240, 250, color=COLOR_GREEN, sw=3))
    f.append(arrow(241, 190, 275, 190, color=COLOR_GREEN, sw=1.5))
    f.append(line(280, 130, 280, 250, color="#82e0aa", sw=2, dash="3,3"))
    f.append(arrow(281, 190, 315, 190, color="#82e0aa", sw=1.5))

    b3, _, _ = textbox(midx / 2, 310, "Синхронне скорочення:\nЕфективний насосний викид крові", size=12, pad=8, fill="#eafaf1", stroke=COLOR_GREEN)
    f.append(b3)

    # --- ПРАВА ЧАСТИНА: Фібриляція шлуночків ---
    f.append(text(midx + midx / 2, 54, "Фібриляція шлуночків ( спіральні ротори )", size=13, bold=True, color=COLOR_RED))

    # Тканина міокарда з кількома спіральними роторами
    f.append(rect(midx + 40, 90, 300, 180, fill="#fdf2e9", stroke=COLOR_RED, sw=1.5, rx=6))

    # Ротор 1 (Спіральна хвиля)
    f.append(circle(midx + 110, 150, 8, fill=COLOR_RED, stroke=COLOR_RED))
    f.append(text(midx + 110, 130, "Фазова сигулярність", size=10, bold=True, color=COLOR_RED))
    # Дуги спіралі
    f.append('<path d="M %d %d Q %d %d %d %d T %d %d" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (midx + 110, 158, midx + 140, 160, midx + 140, 190, midx + 80, 190, COLOR_RED))
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' %
             (midx + 80, 190, midx + 70, 140, midx + 110, 138, COLOR_ORANGE))

    # Ротор 2 (Другий дрібний ротор re-entry)
    f.append(circle(midx + 240, 200, 6, fill=COLOR_PURPLE, stroke=COLOR_PURPLE))
    f.append(text(midx + 240, 183, "Re-entry ротор", size=10, bold=True, color=COLOR_PURPLE))
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2"/>' %
             (midx + 240, 206, midx + 270, 220, midx + 260, 240, COLOR_PURPLE))

    b4, _, _ = textbox(midx + midx / 2, 310, "Хаотичне тріпотіння (300-500 хв⁻¹):\nЗупинка гемодинаміки, гемодинамічний нуль", size=12, pad=8, fill="#fdf2e9", stroke=COLOR_RED)
    f.append(b4)

    render(os.path.join(IMG, "cardiac-propagation-vs-fibrillation.svg"), W, H, *f)

# ── Фігура 2: Вразливий період ЕКГ (Зубець T) ──────────────────────────────
def fig_vulnerable_period():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Вразливе вікно серцевого циклу (Vulnerable Period on T-Wave)", size=16, bold=True))

    # ЕКГ ізолінія
    y0 = 220
    ecg_path = [
        "M 50 %d" % y0,
        "L 130 %d" % y0,
        # P wave
        "Q 150 %d 170 %d" % (y0 - 25, y0),
        "L 210 %d" % y0,
        # QRS complex
        "L 220 %d" % (y0 + 15), # Q
        "L 235 %d" % (y0 - 110), # R
        "L 250 %d" % (y0 + 35), # S
        "L 260 %d" % y0,
        "L 330 %d" % y0,
        # T wave
        "Q 380 %d 430 %d" % (y0 - 65, y0),
        "L 710 %d" % y0
    ]

    # Вразлива зона під зубцем T (вертикальна смуга з прозорим фоном)
    f.append(rect(340, 80, 80, 180, fill="#fdecea", stroke=COLOR_RED, sw=1.5, rx=4))

    # Пояснення вразливої зони
    b1, _, _ = textbox(380, 56, "ВРАЗЛИВИЙ ПЕРІОД (15-30 мс)\nНеоднорідна реполяризація", size=11, pad=6, fill="#ffffff", stroke=COLOR_RED, bold=True, color=COLOR_RED)
    f.append(b1)

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(ecg_path), INK))

    # Написи зубців ЕКГ
    f.append(text(160, y0 - 32, "P", size=14, bold=True, color=COLOR_BLUE))
    f.append(text(235, y0 - 118, "R", size=16, bold=True, color=COLOR_RED))
    f.append(text(380, y0 - 72, "T", size=16, bold=True, color=COLOR_PURPLE))

    # Імпульс електричного удару
    f.append(arrow(380, 140, 380, 185, color=COLOR_RED, sw=2.5))
    f.append(text(490, 155, "Зовнішній електричний імпульс\n(наприклад струм 50 Гц)", size=11, bold=True, color=COLOR_RED))

    # Підпис стадій
    f.append(text(235, 275, "Деполяризація", size=11, color=MUTED))
    f.append(text(380, 275, "Реполяризація", size=11, color=MUTED))

    b_summary, _, _ = textbox(W / 2, 325, "Електричний удар під час зубця T викликає локальний блок проведення та ініціює re-entry спіраль", size=12, pad=6, fill="#f4f6f8", stroke=LINE)
    f.append(b_summary)

    render(os.path.join(IMG, "vulnerable-period-t-wave.svg"), W, H, *f)

# ── Фігура 3: Криві Далзіла та зони IEC 60479-1 ────────────────────────────
def fig_dalziel_iec_curves():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Зони впливу змінного струму (50 Гц) за стандартом IEC 60479-1", size=16, bold=True))

    # Вісі координат
    ox, oy = 80, 310
    w_ax, h_ax = 620, 240
    f.append(arrow(ox, oy, ox + w_ax + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - h_ax - 15, color=LINE, sw=1.8))

    f.append(text(ox + w_ax, oy + 25, "Тривалість проходження t (мс)", size=12, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - h_ax - 5, "Струм I (мА)", size=12, bold=True, anchor="start"))

    # Поділки X (час: 10, 50, 100, 500, 1000, 5000 мс)
    times = [(10, "10"), (100, "100"), (500, "500"), (1000, "1000"), (5000, "5000")]
    for t_val, t_str in times:
        import math
        x_p = ox + (math.log10(t_val) - 1.0) / 2.7 * w_ax
        f.append(line(x_p, oy, x_p, oy + 5, color=LINE, sw=1.2))
        f.append(text(x_p, oy + 20, t_str, size=10))

    # Зони IEC 60479-1
    # AC-1: I < 0.5 mA
    f.append(rect(ox + 2, oy - 35, w_ax - 4, 33, fill="#eafaf1", stroke="none"))
    f.append(text(ox + 140, oy - 18, "Зона AC-1: Невідчутний струм (< 0.5 мА)", size=11, color=COLOR_GREEN, bold=True))

    # AC-2: 0.5 mA - 10 mA
    f.append(rect(ox + 2, oy - 100, w_ax - 4, 63, fill="#eef6ff", stroke="none"))
    f.append(text(ox + 200, oy - 65, "Зона AC-2: Відчутний струм, без мимовільних судом (0.5 – 10 мА)", size=11, color=COLOR_BLUE, bold=True))

    # AC-3: 10 mA до кривої c1 (поріг невідпускання)
    f.append(rect(ox + 2, oy - 180, w_ax - 4, 78, fill="#fef9e7", stroke="none"))
    f.append(text(ox + 240, oy - 130, "Зона AC-3: Обратимі судоми м'язів, поріг невідпускання (> 10 мА)", size=11, color=COLOR_ORANGE, bold=True))

    # AC-4: Понад криву c1 (Ризик фібриляції шлуночків)
    f.append(rect(ox + 2, oy - h_ax, w_ax - 4, 58, fill="#fdecea", stroke="none"))
    f.append(text(ox + 300, oy - 210, "Зона AC-4: ВИСОКИЙ РИЗИК ФІБРИЛЯЦІЇ ШЛУНОЧКІВ (AC-4.1 ... AC-4.3)", size=11, color=COLOR_RED, bold=True))

    # Крива c1 (поріг фібриляції)
    curve_pts = []
    import math
    for tv in range(10, 5001, 50):
        xp = ox + (math.log10(tv) - 1.0) / 2.7 * w_ax
        i_val = 50.0 / math.sqrt(tv / 1000.0) if tv > 100 else 150.0
        yp = oy - max(35.0, min(h_ax - 10, i_val * 1.2))
        curve_pts.append("%.1f,%.1f" % (xp, yp))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(curve_pts), COLOR_RED))
    f.append(text(ox + w_ax - 90, oy - 170, "Крива c1 (поріг ФШ)", size=11, bold=True, color=COLOR_RED))

    render(os.path.join(IMG, "dalziel-iec-curves.svg"), W, H, *f)

# ── Фігура 4: Схема та форма імпульсу дефібрилятора (Двофазний імпульс) ────
def fig_defibrillator_waveform():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Фізична схема дефібрилятора та форма двофазного імпульсу (BTE)", size=16, bold=True))

    midx = 340
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Схема LC + H-міст ---
    f.append(text(midx / 2, 54, "Схема розряду конденсатора", size=13, bold=True, color=COLOR_BLUE))

    # Конденсатор C
    f.append(line(50, 100, 50, 130, color=LINE, sw=1.8))
    f.append(line(35, 130, 65, 130, color=COLOR_BLUE, sw=3.0))
    f.append(line(35, 140, 65, 140, color=COLOR_BLUE, sw=3.0))
    f.append(line(50, 140, 50, 170, color=LINE, sw=1.8))
    f.append(text(25, 138, "C", size=14, bold=True, color=COLOR_BLUE))

    # Індуктивність L (формувач)
    f.append(line(50, 100, 90, 100, color=LINE, sw=1.8))
    f.append('<path d="M 90 100 Q 95 90 100 100 Q 105 90 110 100 Q 115 90 120 100" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    f.append(text(105, 83, "L", size=12, bold=True))
    f.append(line(120, 100, 150, 100, color=LINE, sw=1.8))

    # H-міст комутації (ключі)
    f.append(rect(150, 85, 60, 100, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(180, 135, "H-міст\nключів", size=11, bold=True, anchor="middle"))

    # Нагрузка (тіло людини R_body)
    f.append(line(210, 115, 250, 115, color=LINE, sw=1.8))
    f.append(line(210, 155, 250, 155, color=LINE, sw=1.8))
    f.append(rect(250, 105, 45, 60, fill="#fdecea", stroke=COLOR_RED, sw=1.8, rx=4))
    f.append(text(272, 135, "R_тіла\n~50 Ом", size=10, bold=True, color=COLOR_RED, anchor="middle"))

    f.append(line(50, 170, 180, 170, color=LINE, sw=1.8))
    f.append(line(180, 170, 180, 185, color=LINE, sw=1.8))

    b_lc, _, _ = textbox(midx / 2, 260, "Накопичення: E = ½ C·V² (150-360 Дж)\nКомутація H-мостом змінює полярність", size=11, pad=6, fill="#eef6ff", stroke=COLOR_BLUE)
    f.append(b_lc)

    # --- ПРАВА ЧАСТИНА: Форма двофазного імпульсу BTE ---
    f.append(text(midx + (W - midx) / 2, 54, "Двофазний зрізаний експоненційний імпульс (BTE)", size=13, bold=True, color=COLOR_GREEN))

    ox_w, oy_w = midx + 50, 200
    f.append(arrow(ox_w, oy_w, ox_w + 320, oy_w, color=LINE, sw=1.5))
    f.append(arrow(ox_w, oy_w, ox_w, oy_w - 110, color=LINE, sw=1.5))
    f.append(line(ox_w, oy_w, ox_w, oy_w + 60, color=LINE, sw=1.5))

    f.append(text(ox_w + 310, oy_w + 20, "t (мс)", size=11, bold=True))
    f.append(text(ox_w - 10, oy_w - 100, "V, I", size=11, bold=True))

    # Фаза 1 (Пряма полярність - деполяризація)
    p1 = "M %d %d Q %d %d %d %d L %d %d" % (ox_w, oy_w - 90, ox_w + 40, oy_w - 60, ox_w + 100, oy_w - 35, ox_w + 100, oy_w)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p1, COLOR_GREEN))
    f.append(rect(ox_w, oy_w - 90, 100, 90, fill="#eafaf1", stroke="none"))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p1, COLOR_GREEN))
    f.append(text(ox_w + 50, oy_w - 45, "Фаза 1 (пряма)\nДеполяризація", size=10, bold=True, color=COLOR_GREEN))

    # Перемикання фази
    f.append(line(ox_w + 100, oy_w, ox_w + 100, oy_w + 40, color=COLOR_RED, sw=2, dash="2,2"))

    # Фаза 2 (Зворотна полярність - зняття залишкового заряду)
    p2 = "M %d %d Q %d %d %d %d L %d %d" % (ox_w + 100, oy_w + 40, ox_w + 140, oy_w + 25, ox_w + 180, oy_w + 12, ox_w + 180, oy_w)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p2, COLOR_RED))
    f.append(text(ox_w + 140, oy_w + 30, "Фаза 2 (зворотна)", size=10, bold=True, color=COLOR_RED))

    b_bte, _, _ = textbox(midx + (W - midx) / 2, 305, "Перевага BTE: Фаза 2 знімає залишковий заряд клітин,\nзнижує поріг дефібриляції та запобігає опікам", size=11, pad=6, fill="#f4f6f8", stroke=LINE)
    f.append(b_bte)

    render(os.path.join(IMG, "defibrillator-waveform-biphasic.svg"), W, H, *f)

if __name__ == "__main__":
    fig_propagation_vs_fibrillation()
    fig_vulnerable_period()
    fig_dalziel_iec_curves()
    fig_defibrillator_waveform()
    print("Фігури успішно згенеровано у ./img/")
