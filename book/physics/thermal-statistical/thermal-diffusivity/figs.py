# -*- coding: utf-8 -*-
"""Фігури до теми «Температуропровідність (a)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольорова палітра
HOT    = "#c0392b"  # Гаряче / висока T
COLD   = "#2457d6"  # Холодне / низька T
FIELD  = "#27ae60"  # Зелений / поля / заповнення
INK    = "#1a1a1a"  # Основний текст
MUTED  = "#6b7280"  # Другорядне
BORDER = "#333333"
FILL   = "#f8f9fa"
ACCENT = "#8e44ad"  # Фіолетовий акцент

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))

# ── Фігура 1: Фізична сутність (diffusivity-concept.svg) ───────────────────
def fig_diffusivity_concept():
    W, H = 820, 480
    f = [text(W / 2, 28, "Температуропровідність (a) vs Теплопровідність (λ)", size=16, bold=True)]

    # Ліва панель: Низька температуропровідність (Велике ро·c_p)
    p1X, p1Y = 40, 60
    pW, pH = 350, 370
    f.append(rect(p1X, p1Y, pW, pH, fill=FILL, stroke=BORDER, sw=1.5, rx=6))
    f.append(text(p1X + pW/2, p1Y + 25, "Низьке a (напр. Вода / Важкі сплави)", size=13, color=COLD, bold=True))
    f.append(text(p1X + pW/2, p1Y + 45, "Висока об'ємна теплоємність C_v = ρ · c_p", size=11, color=MUTED))

    # Схема тепла: потік уходить на нагрівання об'єму
    sX, sY = p1X + 30, p1Y + 70
    sW, sH = 290, 140
    f.append(rect(sX, sY, sW, sH, fill="#ffffff", stroke="#d0d0d0", sw=1))
    # Тепловий імпульс зліва
    f.append(rect(sX, sY, 25, sH, fill="#fdecea", stroke=HOT, sw=1.5))
    f.append(text(sX + 12, sY + sH/2, "Q", size=14, color=HOT, bold=True))
    
    # Фронт температури (повільний)
    f.append(path(f"M {sX+25} {sY+20} Q {sX+70} {sY+20} {sX+100} {sY+sH-20} L {sX+25} {sY+sH-20} Z", fill="#fadbd8", stroke=HOT, sw=1.5))
    f.append(text(sX + 140, sY + 45, "Температурний фронт", size=11, color=HOT))
    f.append(text(sX + 140, sY + 65, "просувається повільно", size=11, color=HOT, italic=True))
    f.append(arrow(sX + 140, sY + 75, sX + 105, sY + 75, color=HOT, sw=1.5))

    # Блок накопичення
    f.append(rect(sX + 35, sY + 80, 55, 45, fill="#ebf5fb", stroke=COLD, sw=1, rx=4))
    f.append(text(sX + 62, sY + 107, "Поглинання", size=10, color=COLD, bold=True))

    f.append(fitbox(p1X + 25, p1Y + 230, pW - 50, 115, 
                    ["Рівняння: ∂T/∂t = a · ∇²T",
                     "• Енергія витрачається на",
                     "  нагрівання проміжних шарів",
                     "• Поширення тепла запізнюється",
                     "• a ≈ 10⁻⁷ м²/с (теплова інерція)"], size=11, fill="#ffffff", stroke=COLD))

    # Права панель: Висока температуропровідність (Мале ро·c_p або величезне lambda)
    p2X = 430
    f.append(rect(p2X, p1Y, pW, pH, fill=FILL, stroke=BORDER, sw=1.5, rx=6))
    f.append(text(p2X + pW/2, p1Y + 25, "Високе a (напр. Алмаз / Мідь / Графен)", size=13, color=HOT, bold=True))
    f.append(text(p2X + pW/2, p1Y + 45, "Низька теплова інерція відносно λ", size=11, color=MUTED))

    # Схема тепла: потік миттєво пробігає крізь тіло
    s2X = p2X + 30
    f.append(rect(s2X, sY, sW, sH, fill="#ffffff", stroke="#d0d0d0", sw=1))
    f.append(rect(s2X, sY, 25, sH, fill="#fdecea", stroke=HOT, sw=1.5))
    f.append(text(s2X + 12, sY + sH/2, "Q", size=14, color=HOT, bold=True))

    # Фронт температури (швидкий, глибокий)
    f.append(path(f"M {s2X+25} {sY+20} Q {sX+220} {sY+25} {s2X+sW-20} {sY+sH-20} L {s2X+25} {sY+sH-20} Z", fill="#fadbd8", stroke=HOT, sw=1.5))
    f.append(arrow(s2X + 30, sY + 40, s2X + sW - 30, sY + 40, color=HOT, sw=2.5))
    f.append(text(s2X + sW/2, sY + 30, "Стрімкий перенос T(x,t)", size=11, color=HOT, bold=True))

    f.append(fitbox(p2X + 25, p1Y + 230, pW - 50, 115, 
                    ["Формула: a = λ / (ρ · c_p)",
                     "• Енергія швидко передається",
                     "  наступним мікроатомам",
                     "• Швидке вирівнювання T",
                     "• a ≈ 10⁻⁴ м²/с (алмаз 1.1·10⁻³)"], size=11, fill="#ffffff", stroke=HOT))

    # Нижня висновок-рамка
    f.append(fitbox(40, H - 42, W - 80, 32, 
                    ["Висновок: λ визначає ПОТІК тепла (Вт), а a — ШВИДКІСТЬ ЗМІНИ температури (м²/с)"], 
                    size=12, bold=True, fill="#e8f8f5", stroke=FIELD))

    render(os.path.join(IMG, "diffusivity-concept.svg"), W, H, *f)

# ── Фігура 2: Метод Онгстрема (angstrom-waves.svg) ──────────────────────────
def fig_angstrom_waves():
    W, H = 820, 500
    f = [text(W / 2, 28, "Метод Онгстрема: Температурні хвилі у стрижні (1861)", size=16, bold=True)]

    # Схема стрижня
    rX, rY = 60, 70
    rW, rH = 700, 50
    f.append(rect(rX, rY, rW, rH, fill="#e5e7eb", stroke=BORDER, sw=2, rx=4))
    f.append(text(rX + rW/2, rY + rH/2 + 4, "Металевий вимірювальний стрижень", size=13, bold=True))

    # Періодичне джерело тепла зліва
    f.append(rect(rX - 35, rY - 10, 35, rH + 20, fill="#fdecea", stroke=HOT, sw=2, rx=4))
    f.append(text(rX - 17, rY + rH/2 - 8, "T(t)", size=13, color=HOT, bold=True))
    f.append(text(rX - 17, rY + rH/2 + 10, "ω", size=12, color=HOT, italic=True))

    # Термопари X1 та X2
    t1X = rX + 180
    t2X = rX + 480
    f.append(line(t1X, rY, t1X, rY - 25, color=HOT, sw=2))
    f.append(circle(t1X, rY - 25, 5, fill=HOT, stroke=HOT))
    f.append(text(t1X, rY - 32, "Термопара 1 (x₁)", size=12, color=HOT, bold=True))

    f.append(line(t2X, rY, t2X, rY - 25, color=COLD, sw=2))
    f.append(circle(t2X, rY - 25, 5, fill=COLD, stroke=COLD))
    f.append(text(t2X, rY - 32, "Термопара 2 (x₂)", size=12, color=COLD, bold=True))

    # Відстань Delta x
    f.append(arrow(t1X, rY + rH + 15, t2X, rY + rH + 15, color=BORDER, sw=1.5))
    f.append(arrow(t2X, rY + rH + 15, t1X, rY + rH + 15, color=BORDER, sw=1.5))
    f.append(text((t1X + t2X)/2, rY + rH + 32, "Відстань Δx = x₂ - x₁", size=12, color=INK))

    # Графік осциляцій T(t) нижче
    gX, gY = 80, 210
    gW, gH = 660, 190
    f.append(rect(gX, gY, gW, gH, fill="#ffffff", stroke="#d0d0d0", sw=1))

    # Осі
    f.append(line(gX + 40, gY + gH - 30, gX + gW - 20, gY + gH - 30, color=BORDER, sw=1.5)) # t
    f.append(arrow(gX + 40, gY + gH - 30, gX + gW - 10, gY + gH - 30, color=BORDER, sw=1.5))
    f.append(text(gX + gW - 20, gY + gH - 10, "Час t", size=12, color=INK))

    f.append(line(gX + 40, gY + gH - 30, gX + 40, gY + 15, color=BORDER, sw=1.5)) # T
    f.append(arrow(gX + 40, gY + gH - 30, gX + 40, gY + 5, color=BORDER, sw=1.5))
    f.append(text(gX + 15, gY + 20, "Температура T", size=12, color=INK))

    # Синусоїда T1(t) - велика амплітуда A1
    pts1 = []
    pts2 = []
    for px in range(0, 560, 4):
        t_val = px / 40.0
        y1 = (gY + 90) - 60 * math.sin(t_val)
        y2 = (gY + 90) - 25 * math.sin(t_val - 1.2) # Phase lag 1.2, attenuated A2
        pts1.append(f"{gX + 50 + px:.1f},{y1:.1f}")
        pts2.append(f"{gX + 50 + px:.1f},{y2:.1f}")

    f.append(path("M " + " L ".join(pts1), fill="none", stroke=HOT, sw=2.5))
    f.append(path("M " + " L ".join(pts2), fill="none", stroke=COLD, sw=2.5))

    # Позначення A1, A2 та фазового зсуву
    f.append(line(gX + 150, gY + 30, gX + 150, gY + 150, color=MUTED, sw=1, dash="3,3"))
    f.append(line(gX + 198, gY + 30, gX + 198, gY + 150, color=MUTED, sw=1, dash="3,3"))
    f.append(arrow(gX + 150, gY + 60, gX + 198, gY + 60, color=ACCENT, sw=1.5))
    f.append(text(gX + 174, gY + 52, "Зсув фази Δφ", size=11, color=ACCENT, bold=True))

    f.append(text(gX + 320, gY + 45, "Амплітуда A₁ (в x₁)", size=11, color=HOT, bold=True))
    f.append(text(gX + 380, gY + 80, "Амплітуда A₂ (в x₂)", size=11, color=COLD, bold=True))

    # Формула внизу
    f.append(fitbox(gX + 40, H - 55, gW - 80, 40,
                    ["Формула Онгстрема: a = (Δx)² · ω / ( 2 · ln(A₁ / A₂) · Δφ )",
                     "з загасання A(x) = A₀·exp(-x/δ) та глибини проникнення δ = √(2a/ω)"],
                    size=11, bold=True, fill="#f4f6f8", stroke=BORDER))

    render(os.path.join(IMG, "angstrom-waves.svg"), W, H, *f)

# ── Фігура 3: Метод лазерного спалаху (laser-flash-method.svg) ───────────────
def fig_laser_flash_method():
    W, H = 820, 480
    f = [text(W / 2, 28, "Метод світлового спалаху Паркера (Laser Flash Analysis)", size=16, bold=True)]

    # Схема установки зліва
    sX, sY = 40, 70
    sW, sH = 310, 360
    f.append(rect(sX, sY, sW, sH, fill=FILL, stroke=BORDER, sw=1.5, rx=6))
    f.append(text(sX + sW/2, sY + 25, "Схема вимірювальної комірки LFA", size=13, bold=True))

    # Лазерне джерело
    f.append(rect(sX + 20, sY + 160, 60, 40, fill="#fdecea", stroke=HOT, sw=1.5, rx=4))
    f.append(text(sX + 50, sY + 184, "Лазер", size=12, color=HOT, bold=True))
    # Промінь
    f.append(arrow(sX + 80, sY + 180, sX + 140, sY + 180, color=HOT, sw=3))
    f.append(text(sX + 110, sY + 170, "Імпульс", size=10, color=HOT, italic=True))

    # Зразок товщиною L
    sampX = sX + 140
    f.append(rect(sampX, sY + 120, 24, 120, fill="#d5dbdb", stroke=BORDER, sw=2, rx=2))
    f.append(text(sampX + 12, sY + 180, "Зразок", size=11, color=INK, bold=True, anchor="middle"))

    # Позначення товщини L
    f.append(line(sampX, sY + 250, sampX + 24, sY + 250, color=BORDER, sw=1))
    f.append(text(sampX + 12, sY + 268, "L", size=13, color=INK, bold=True))

    # ІЧ-детектор справа
    f.append(rect(sX + 230, sY + 160, 60, 40, fill="#eaf0fd", stroke=COLD, sw=1.5, rx=4))
    f.append(text(sX + 260, sY + 184, "ІЧ-сенсор", size=11, color=COLD, bold=True))
    # Сигнал від задньої поверхні
    f.append(path(f"M {sampX+24} {sY+180} Q {sX+190} {sY+170} {sX+230} {sY+180}", fill="none", stroke=COLD, sw=1.5, dash="3,3"))

    # Опис процесу
    f.append(fitbox(sX + 15, sY + 285, sW - 30, 65,
                    ["1. Короткий спалах нагріває передню грань",
                     "2. Тепловий фронт дифундує крізь товщу L",
                     "3. Сенсор фіксує криву T(L, t) задньої грані"],
                    size=10, fill="#ffffff", stroke="#cccccc"))

    # Графік зростання температури T(L,t) справа
    gX, gY = 380, 70
    gW, gH = 400, 360
    f.append(rect(gX, gY, gW, gH, fill="#ffffff", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(gX + gW/2, gY + 25, "Термограма задньої поверхні T(L, t)", size=13, bold=True))

    # Осі
    f.append(arrow(gX + 45, gY + gH - 40, gX + gW - 20, gY + gH - 40, color=BORDER, sw=1.5))
    f.append(text(gX + gW - 30, gY + gH - 20, "Час t", size=12, color=INK))

    f.append(arrow(gX + 45, gY + gH - 40, gX + 45, gY + 45, color=BORDER, sw=1.5))
    f.append(text(gX + 20, gY + 55, "T / T_max", size=12, color=INK))

    # Рівень T_max = 1.0
    f.append(line(gX + 45, gY + 90, gX + gW - 30, gY + 90, color=MUTED, sw=1, dash="4,4"))
    f.append(text(gX + 35, gY + 94, "1.0", size=11, color=MUTED))

    # Рівень T = 0.5 (напівпідйом)
    f.append(line(gX + 45, gY + 205, gX + gW - 30, gY + 205, color=MUTED, sw=1, dash="4,4"))
    f.append(text(gX + 35, gY + 209, "0.5", size=11, color=HOT, bold=True))

    # Крива Паркера
    pts = []
    for px in range(0, 320, 4):
        t_n = (px + 1) / 80.0
        if t_n < 0.1:
            val = 0
        else:
            val = 1.0 - 1.25 * math.exp(-1.8 * (t_n - 0.1))
            val = max(0, min(1.0, val))
        py = (gY + gH - 40) - val * 230
        pts.append(f"{gX + 45 + px:.1f},{py:.1f}")

    f.append(path("M " + " L ".join(pts), fill="none", stroke=HOT, sw=3))

    # Час півпідйому t_{1/2}
    t_half_px = gX + 45 + 85
    f.append(line(t_half_px, gY + 205, t_half_px, gY + gH - 40, color=HOT, sw=1.5, dash="3,3"))
    f.append(circle(t_half_px, gY + 205, 5, fill=HOT, stroke=HOT))
    f.append(text(t_half_px, gY + gH - 22, "t₁/₂", size=13, color=HOT, bold=True))

    # Головна формула в рамці
    f.append(fitbox(gX + 100, gY + 245, 250, 60,
                    ["Формула Паркера (1961):",
                     "a = 0.1388 · L² / t₁/₂"],
                    size=12, bold=True, fill="#fdecea", stroke=HOT))

    render(os.path.join(IMG, "laser-flash-method.svg"), W, H, *f)

# ── Фігура 4: Безрозмірні числа (transport-numbers-boundary.svg) ────────────
def fig_transport_numbers():
    W, H = 820, 480
    f = [text(W / 2, 28, "Число Прандтля (Pr = ν / a) та пристінкові шари", size=16, bold=True)]

    pW = 230
    pH = 370
    pY = 70

    modes = [
        ("Pr << 1 (Рідкі метали)", "a >> ν (Температурна дифузія домінує)", 
         "#ebf5fb", COLD, 60, 210, "δ_T >> δ_v"),
        ("Pr ≈ 1 (Гази / Повітря)", "a ≈ ν (Солідарний перенос)", 
         "#f4f6f8", BORDER, 140, 140, "δ_T ≈ δ_v"),
        ("Pr >> 1 (В'язкі масла)", "a << ν (Гідродинамічна дифузія)", 
         "#fdecea", HOT, 210, 60, "δ_T << δ_v")
    ]

    for idx, (title, sub, bg_col, main_col, dv_h, dt_h, label) in enumerate(modes):
        pX = 30 + idx * 260
        f.append(rect(pX, pY, pW, pH, fill=bg_col, stroke=BORDER, sw=1.5, rx=6))
        f.append(text(pX + pW/2, pY + 25, title, size=12, color=INK, bold=True))
        f.append(fitbox(pX + 10, pY + 42, pW - 20, 20, sub, size=9, fill="none", stroke="none"))

        # Схема пластини
        bX = pX + 25
        bY = pY + 280
        f.append(rect(bX, bY, 180, 15, fill="#7f8c8d", stroke=BORDER, sw=1))
        f.append(text(bX + 90, bY + 11, "Омивальна стінка", size=10, color="#ffffff", bold=True))

        # Динамічний шар delta_v (блакитна зона)
        path_v = f"M {bX} {bY} Q {bX+60} {bY-dv_h} {bX+170} {bY-dv_h} L {bX+170} {bY} Z"
        f.append(path(path_v, fill="#3498db", stroke="#2980b9", sw=1.5))
        f.append(text(bX + 120, bY - dv_h/2, "δ_v (швидкість)", size=10, color="#ffffff", bold=True))

        # Тепловий шар delta_T (червона пунктирна лінія)
        path_t = f"M {bX} {bY} Q {bX+60} {bY-dt_h} {bX+170} {bY-dt_h}"
        f.append(path(path_t, fill="none", stroke=HOT, sw=2, dash="4,3"))
        f.append(text(bX + 40, bY - dt_h - 8, "δ_T (температура)", size=10, color=HOT, bold=True))

        # Співвідношення внизу
        f.append(fitbox(pX + 20, pY + 310, pW - 40, 45,
                        [f"Результат: {label}",
                         f"Формула: δ_v / δ_T ≈ √Pr"],
                        size=10, bold=True, fill="#ffffff", stroke=main_col))

    render(os.path.join(IMG, "transport-numbers-boundary.svg"), W, H, *f)

# ── Фігура 5: Глибина проникнення в ґрунт (soil-temperature-depth.svg) ─────
def fig_soil_temperature():
    W, H = 820, 500
    f = [text(W / 2, 28, "Сезонні температурні хвилі в ґрунті (a ≈ 10⁻⁶ м²/с)", size=16, bold=True)]

    gX, gY = 80, 60
    gW, gH = 680, 360
    f.append(rect(gX, gY, gW, gH, fill="#ffffff", stroke=BORDER, sw=1.5, rx=6))

    # Осі: X — температура T (°C), Y — глибина z (м, зверху вниз)
    f.append(line(gX + 50, gY + 30, gX + gW - 30, gY + 30, color=BORDER, sw=1.5)) # T axis
    f.append(arrow(gX + 50, gY + 30, gX + gW - 15, gY + 30, color=BORDER, sw=1.5))
    f.append(text(gX + gW - 40, gY + 20, "Температура T (°C)", size=12, color=INK))

    f.append(line(gX + 280, gY + 30, gX + 280, gY + gH - 20, color=BORDER, sw=1.5)) # Depth axis (0 m at z=0)
    f.append(arrow(gX + 280, gY + 30, gX + 280, gY + gH - 10, color=BORDER, sw=1.5))
    f.append(text(gX + 290, gY + gH - 15, "Глибина z (м)", size=12, color=INK))

    # Подземельна лінія средньої T = 10 °C
    f.append(line(gX + 280, gY + 30, gX + 280, gY + gH - 20, color=MUTED, sw=1, dash="2,2"))

    # Шкала глибин (0, 1, 2, 3, 4, 5, 6 метрів)
    for z in range(0, 7):
        zy = gY + 40 + z * 45
        f.append(line(gX + 275, zy, gX + 285, zy, color=BORDER, sw=1))
        f.append(text(gX + 265, zy + 4, f"{z} м", size=11, color=INK, anchor="end"))

    # Температурні позначки на осі X (-10°C, 0°C, +10°C, +20°C, +30°C)
    t_ticks = [(-10, gX + 80), (0, gX + 180), (10, gX + 280), (20, gX + 380), (30, gX + 480)]
    for val, tx in t_ticks:
        f.append(line(tx, gY + 25, tx, gY + 35, color=BORDER, sw=1))
        f.append(text(tx, gY + 15, f"{val}°C", size=10, color=MUTED))

    # Профілі T(z) для Літа (Липень) та Зими (Січень)
    pts_summer = []
    pts_winter = []
    delta = 3.17

    for z_cm in range(0, 600, 5):
        z_m = z_cm / 100.0
        zy = gY + 40 + z_m * 45
        
        amp = 15.0 * math.exp(-z_m / delta)
        
        t_sum = 10.0 + amp * math.cos(-z_m / delta)
        t_win = 10.0 + amp * math.cos(math.pi - z_m / delta)
        
        x_sum = gX + 280 + (t_sum - 10.0) * 10.0
        x_win = gX + 280 + (t_win - 10.0) * 10.0
        
        pts_summer.append(f"{x_sum:.1f},{zy:.1f}")
        pts_winter.append(f"{x_win:.1f},{zy:.1f}")

    f.append(path("M " + " L ".join(pts_summer), fill="none", stroke=HOT, sw=2.5))
    f.append(path("M " + " L ".join(pts_winter), fill="none", stroke=COLD, sw=2.5))

    # Легенда
    f.append(text(gX + 450, gY + 120, "Літо (Липень): поверхня +25°C", size=12, color=HOT, bold=True))
    f.append(text(gX + 110, gY + 120, "Зима (Січень): поверхня -5°C", size=12, color=COLD, bold=True))

    # Зсув фази та згасання на 3 м
    z3_y = gY + 40 + 3.17 * 45
    f.append(line(gX + 60, z3_y, gX + gW - 60, z3_y, color=ACCENT, sw=1, dash="3,3"))
    f.append(text(gX + 510, z3_y - 8, "Глибина згасання δ = 3.17 м", size=11, color=ACCENT, bold=True))
    f.append(text(gX + 510, z3_y + 14, "Протифаза: влітку прохолодно, взимку тепло!", size=10, color=ACCENT, italic=True))

    # Висновок внизу
    f.append(fitbox(gX + 50, H - 50, gW - 100, 35,
                    ["Фізичний ефект: На глибині z > 3·δ (бл. 10 м) температурні коливання повністю гаснуть,",
                     "забезпечуючи сталу середньорічну температуру (основа геотермальних насосів)."],
                    size=10, bold=True, fill="#eaf0fd", stroke=COLD))

    render(os.path.join(IMG, "soil-temperature-depth.svg"), W, H, *f)

# ── Головний блок генерації ──────────────────────────────────────────────────
if __name__ == "__main__":
    fig_diffusivity_concept()
    print("Згенеровано: diffusivity-concept.svg")
    fig_angstrom_waves()
    print("Згенеровано: angstrom-waves.svg")
    fig_laser_flash_method()
    print("Згенеровано: laser-flash-method.svg")
    fig_transport_numbers()
    print("Згенеровано: transport-numbers-boundary.svg")
    fig_soil_temperature()
    print("Згенеровано: soil-temperature-depth.svg")
