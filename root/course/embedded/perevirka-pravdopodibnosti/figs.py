# -*- coding: utf-8 -*-
"""Фігури до теми «Перевірка правдоподібності».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

GOLD = "#b9770e"
BLUE = "#2457d6"
GREEN = "#27ae60"
RED = "#c0392b"
PURPLE = "#8e44ad"
BORDER = "#d0d4dc"


def _poly(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % q for q in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (p, color, sw, d))


# ── 1. Конвеєр перевірки правдоподібності ──────────────────────────────────
def fig_pipeline():
    W, H = 820, 310
    f = [
        text(W / 2, 24, "Конвеєр багаторівневої валідації правдоподібності сенсорних даних", size=14, bold=True)
    ]

    stages = [
        ("Електричні межі", "АЦП / NAMUR NE43", "Обрив лінії, КЗ,", "захисні зони живлення", RED),
        ("Динамічний темп", "Slew-Rate Limiter", "Теплова / механічна", "інерція (dT/dt, dw/dt)", GOLD),
        ("Перехресна модель", "Cross-Correlation", "Фізичний зв'язок каналів", "(V-I просідання, az/баро)", PURPLE),
        ("Інтегратор довіри", "Leaky Bucket", "Накопичення штрафів,", "гістерезис відновлення", BLUE)
    ]

    bw, bh = 154, 150
    start_x = 75
    gap = 36
    y = 65

    # Вхідний потік
    f.append(arrow(15, y + bh / 2, start_x - 6, y + bh / 2, color=LINE, sw=1.8))
    f.append(text(42, y + bh / 2 - 14, "Сирі", size=11, bold=True))
    f.append(text(42, y + bh / 2 - 2, "відліки", size=11, bold=True))
    f.append(text(42, y + bh / 2 + 12, "з АЦП", size=10, color=MUTED))

    for i, (title1, title2, desc1, desc2, col) in enumerate(stages):
        bx = start_x + i * (bw + gap)
        # Рамка блоку
        f.append(rect(bx, y, bw, bh, fill="#fafbfc", stroke=col, sw=1.8, rx=6))
        # Шапка етапу
        f.append(rect(bx, y, bw, 32, fill=col, stroke="none", rx=6))
        f.append(rect(bx, y + 20, bw, 12, fill=col, stroke="none"))
        f.append(text(bx + bw / 2, y + 14, "Етап %d" % (i + 1), size=10, color="#ffffff", bold=True))
        f.append(text(bx + bw / 2, y + 26, title1, size=11, color="#ffffff", bold=True))

        # Тіло
        f.append(text(bx + bw / 2, y + 54, title2, size=11, color=col, bold=True))
        f.append(line(bx + 12, y + 68, bx + bw - 12, y + 68, color="#e5e7eb", sw=1.0))
        f.append(text(bx + bw / 2, y + 88, desc1, size=10, color=INK))
        f.append(text(bx + bw / 2, y + 104, desc2, size=10, color=INK))

        # Стрілка браку (донизу)
        f.append(arrow(bx + bw / 2, y + bh, bx + bw / 2, y + bh + 36, color=RED, sw=1.4))
        f.append(text(bx + bw / 2, y + bh + 48, "Брак / Збій", size=9.5, color=RED, bold=True))

        # Стрілка до наступного етапу
        if i < len(stages) - 1:
            next_bx = start_x + (i + 1) * (bw + gap)
            f.append(arrow(bx + bw, y + bh / 2, next_bx - 6, y + bh / 2, color=LINE, sw=1.6))
            f.append(text(bx + bw + gap / 2, y + bh / 2 - 8, "OK", size=9, color=GREEN, bold=True))

    # Вихідний потік
    last_bx = start_x + 3 * (bw + gap) + bw
    f.append(arrow(last_bx, y + bh / 2, W - 20, y + bh / 2, color=GREEN, sw=2.2))
    f.append(text(W - 48, y + bh / 2 - 14, "Очищені", size=11, color=GREEN, bold=True))
    f.append(text(W - 48, y + bh / 2 - 2, "достовірні", size=11, color=GREEN, bold=True))
    f.append(text(W - 48, y + bh / 2 + 12, "дані", size=11, color=GREEN, bold=True))

    # Загальна лінія аварії внизу
    f.append(line(start_x + bw / 2, y + bh + 58, start_x + 3 * (bw + gap) + bw / 2, y + bh + 58, color=RED, sw=1.2, dash="3,3"))
    f.append(arrow(start_x + 3 * (bw + gap) + bw / 2, y + bh + 58, W - 70, y + bh + 58, color=RED, sw=1.4))
    f.append(text(W - 35, y + bh + 58, "Failsafe", size=10.5, color=RED, bold=True))

    render(os.path.join(IMG, "plausibility-pipeline.svg"), W, H, *f)


# ── 2. Фільтрація темпу наростання (Slew-Rate Limiting) ─────────────────────
def fig_slew_rate():
    W, H = 780, 360
    f = [
        text(W / 2, 22, "Динамічний коридор швидкості наростання сигналу (Slew-Rate Envelope)", size=14, bold=True)
    ]

    gx, gy, gw, gh = 80, 50, 640, 250
    f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=BORDER, sw=1.2))

    # Сітка
    for step_y in range(gy + 40, gy + gh, 40):
        f.append(line(gx, step_y, gx + gw, step_y, color="#eef0f4", sw=1.0))
    for step_x in range(gx + 60, gx + gw, 60):
        f.append(line(step_x, gy, step_x, gy + gh, color="#eef0f4", sw=1.0))

    # Осі
    f.append(arrow(gx, gy + gh, gx + gw + 20, gy + gh, color=INK, sw=1.5))
    f.append(arrow(gx, gy + gh, gx, gy - 15, color=INK, sw=1.5))
    f.append(text(gx + gw + 28, gy + gh + 4, "t", size=13, italic=True))
    f.append(text(gx - 18, gy - 8, "T, °C", size=12, bold=True))

    # Фізичний сигнал (повільне реальне нагрівання)
    real_pts = [
        (gx + 20, gy + 190),
        (gx + 90, gy + 185),
        (gx + 160, gy + 175),
        (gx + 230, gy + 155),
        (gx + 300, gy + 130),
        (gx + 370, gy + 105),
        (gx + 440, gy + 85),
        (gx + 510, gy + 75),
        (gx + 580, gy + 70),
        (gx + 620, gy + 68),
    ]
    f.append(_poly(real_pts, GREEN, sw=2.5))

    # Фізичний динамічний коридор навколо точки (t_k)
    tk_x, tk_y = gx + 230, gy + 155
    # Коридор вперед на наступний відлік
    tk1_x = gx + 300
    slew_up = 40
    slew_down = 30
    corridor_poly = [
        (tk_x, tk_y),
        (tk1_x, tk_y - slew_up),
        (tk1_x, tk_y + slew_down),
        (tk_x, tk_y)
    ]
    f_corridor = " ".join("%.1f,%.1f" % p for p in corridor_poly)
    f.append('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (f_corridor, GOLD, GOLD))
    f.append(text(tk1_x + 72, tk_y - slew_up + 6, "+S_max · dt (допустимо)", size=9.5, color=GOLD))
    f.append(text(tk1_x + 72, tk_y + slew_down - 2, "-S_max · dt (допустимо)", size=9.5, color=GOLD))

    # Глітч АЦП (неможливий стрибок вгору на 50 градусів)
    glitch_x, glitch_y = gx + 160, gy + 45
    raw_glitch_pts = [(gx + 90, gy + 185), (glitch_x, glitch_y), (gx + 230, gy + 155)]
    f.append(_poly(raw_glitch_pts, RED, sw=1.8, dash="4,3"))
    f.append(circle(glitch_x, glitch_y, 4.5, fill=RED, stroke="#ffffff", sw=1.5))
    f.append(text(glitch_x, glitch_y - 12, "Глітч АЦП / Наводка (+45°C)", size=10, color=RED, bold=True))
    f.append(text(glitch_x, glitch_y + 16, "ВІДСІКАЄТЬСЯ", size=9, color=RED, bold=True))

    # Точка затискання (clamped point)
    clamped_y = gy + 175 - 18
    f.append(circle(glitch_x, clamped_y, 4, fill=GOLD, stroke="#ffffff", sw=1.5))
    f.append(text(glitch_x + 65, clamped_y + 4, "Затиснуте значення", size=9, color=GOLD, italic=True))

    # Пояснення ліній
    leg_x, leg_y = gx + 360, gy + gh - 45
    f.append(rect(leg_x - 10, leg_y - 14, 275, 48, fill="#ffffff", stroke=BORDER, sw=1.0, rx=4))
    f.append(line(leg_x, leg_y, leg_x + 24, leg_y, color=GREEN, sw=2.5))
    f.append(text(leg_x + 32, leg_y + 4, "Істинна теплова динаміка процесу", size=9.5, anchor="start"))
    f.append(line(leg_x, leg_y + 20, leg_x + 24, leg_y + 20, color=RED, sw=1.8, dash="4,3"))
    f.append(text(leg_x + 32, leg_y + 24, "Сирі виміри з перешкодами", size=9.5, anchor="start"))

    f.append(text(W / 2, H - 12, "Швидкість зміни фізичного сигналу обмежена тепловою інертністю: dT/dt ≤ P_loss / C_th", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "slew-rate-limiting.svg"), W, H, *f)


# ── 3. Перехресна кореляція фізичних каналів ────────────────────────────────
def fig_cross_correlation():
    W, H = 820, 350
    f = [
        text(W / 2, 22, "Багатофакторна перехресна кореляція фізичних каналів", size=14, bold=True)
    ]

    pw, ph = 360, 270
    p1_x, p2_x = 35, 425
    py = 50

    # ── Панель 1: Батарея (Напруга vs Струм) ──
    f.append(rect(p1_x, py, pw, ph, fill="#fafbfc", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(p1_x + pw / 2, py + 20, "1. Енергосистема: V_bat проти I_load", size=12, bold=True, color=BLUE))
    f.append(text(p1_x + pw / 2, py + 36, "Закон Ома: V = E_ocv - I · R_int", size=10, color=MUTED, italic=True))

    # Графік струму і напруги
    g1_x, g1_y, g1_w, g1_h = p1_x + 30, py + 55, pw - 55, 170
    f.append(rect(g1_x, g1_y, g1_w, g1_h, fill="#ffffff", stroke="#e5e7eb", sw=1.0))
    f.append(line(g1_x, g1_y + g1_h / 2, g1_x + g1_w, g1_y + g1_h / 2, color="#f0f2f5", sw=1.0))

    # Струм (стрибок вгору)
    i_pts = [(g1_x + 15, g1_y + 60), (g1_x + 90, g1_y + 60), (g1_x + 110, g1_y + 20), (g1_x + 220, g1_y + 20), (g1_x + 240, g1_y + 60), (g1_x + 290, g1_y + 60)]
    f.append(_poly(i_pts, GOLD, sw=2.0))
    f.append(text(g1_x + 160, g1_y + 14, "Струм I (пуск мотора)", size=9.5, color=GOLD, bold=True))

    # Напруга фізична (просідання донизу)
    v_pts_phys = [(g1_x + 15, g1_y + 100), (g1_x + 90, g1_y + 100), (g1_x + 110, g1_y + 145), (g1_x + 220, g1_y + 145), (g1_x + 240, g1_y + 100), (g1_x + 290, g1_y + 100)]
    f.append(_poly(v_pts_phys, GREEN, sw=2.0))
    f.append(text(g1_x + 160, g1_y + 160, "Напруга V (фізичне просідання)", size=9.5, color=GREEN, bold=True))

    # Неможлива аномалія (напруга росте зі струмом)
    v_pts_bad = [(g1_x + 90, g1_y + 100), (g1_x + 110, g1_y + 80), (g1_x + 220, g1_y + 80)]
    f.append(_poly(v_pts_bad, RED, sw=2.0, dash="3,3"))
    f.append(text(g1_x + 235, g1_y + 88, "Неможливо!", size=9, color=RED, bold=True))
    f.append(text(p1_x + pw / 2, py + ph - 12, "Якщо I росте, V не може зростати", size=10, color=RED, bold=True))

    # ── Панель 2: Барометр vs Акселерометр IMU ──
    f.append(rect(p2_x, py, pw, ph, fill="#fafbfc", stroke=BORDER, sw=1.2, rx=6))
    f.append(text(p2_x + pw / 2, py + 20, "2. Навігація: Барометр проти IMU az", size=12, bold=True, color=PURPLE))
    f.append(text(p2_x + pw / 2, py + 36, "Кінематика: d2h/dt2 ≈ az - g", size=10, color=MUTED, italic=True))

    g2_x, g2_y, g2_w, g2_h = p2_x + 30, py + 55, pw - 55, 170
    f.append(rect(g2_x, g2_y, g2_w, g2_h, fill="#ffffff", stroke="#e5e7eb", sw=1.0))
    f.append(line(g2_x, g2_y + g2_h / 2, g2_x + g2_w, g2_y + g2_h / 2, color="#f0f2f5", sw=1.0))

    # Прискорення az вгору (+2g)
    az_pts = [(g2_x + 15, g2_y + 60), (g2_x + 80, g2_y + 60), (g2_x + 100, g2_y + 25), (g2_x + 200, g2_y + 25), (g2_x + 220, g2_y + 60), (g2_x + 290, g2_y + 60)]
    f.append(_poly(az_pts, BLUE, sw=2.0))
    f.append(text(g2_x + 150, g2_y + 18, "IMU az (+2g вгору)", size=9.5, color=BLUE, bold=True))

    # Висота барометра (повинна рости)
    h_pts_phys = [(g2_x + 15, g2_y + 140), (g2_x + 80, g2_y + 140), (g2_x + 150, g2_y + 115), (g2_x + 220, g2_y + 95), (g2_x + 290, g2_y + 90)]
    f.append(_poly(h_pts_phys, GREEN, sw=2.0))
    f.append(text(g2_x + 240, g2_y + 108, "Баро h (росте)", size=9, color=GREEN, bold=True))

    # Барометр падає через аеродинамічний тиск
    h_pts_bad = [(g2_x + 80, g2_y + 140), (g2_x + 150, g2_y + 155), (g2_x + 220, g2_y + 160)]
    f.append(_poly(h_pts_bad, RED, sw=2.0, dash="3,3"))
    f.append(text(g2_x + 160, g2_y + 164, "Баро падає (динамічний підпір)", size=9, color=RED, bold=True))
    f.append(text(p2_x + pw / 2, py + ph - 12, "При az > g висота h не може падати", size=10, color=RED, bold=True))

    render(os.path.join(IMG, "cross-channel-correlation.svg"), W, H, *f)


# ── 4. Накопичувач дефектів (Leaky Bucket) та рівні довіри ──────────────────
def fig_trust_bucket():
    W, H = 800, 330
    f = [
        text(W / 2, 22, "Автомат оцінки довіри на основі інтегратора штрафів (Leaky Bucket)", size=14, bold=True)
    ]

    # Стан 1: TRUSTED
    s1_x, s1_y = 60, 80
    sw, sh = 180, 100
    f.append(rect(s1_x, s1_y, sw, sh, fill="#f2fbf5", stroke=GREEN, sw=2.0, rx=8))
    f.append(text(s1_x + sw / 2, s1_y + 24, "TRUSTED", size=13, color=GREEN, bold=True))
    f.append(text(s1_x + sw / 2, s1_y + 44, "Повна довіра (100%)", size=10.5, color=INK))
    f.append(line(s1_x + 10, s1_y + 54, s1_x + sw - 10, s1_y + 54, color="#d1fae5", sw=1.0))
    f.append(text(s1_x + sw / 2, s1_y + 70, "Штрафний рахунок < 25", size=9.5, color=MUTED))
    f.append(text(s1_x + sw / 2, s1_y + 86, "Сигнал іде в регулятор", size=9.5, color=GREEN, bold=True))

    # Стан 2: DEGRADED
    s2_x, s2_y = 310, 80
    f.append(rect(s2_x, s2_y, sw, sh, fill="#fefdf3", stroke=GOLD, sw=2.0, rx=8))
    f.append(text(s2_x + sw / 2, s2_y + 24, "DEGRADED", size=13, color=GOLD, bold=True))
    f.append(text(s2_x + sw / 2, s2_y + 44, "Під підозрою (вага 20%)", size=10.5, color=INK))
    f.append(line(s2_x + 10, s2_y + 54, s2_x + sw - 10, s2_y + 54, color="#fef3c7", sw=1.0))
    f.append(text(s2_x + sw / 2, s2_y + 70, "Штрафний рахунок 25..80", size=9.5, color=MUTED))
    f.append(text(s2_x + sw / 2, s2_y + 86, "Знижена вага / Затискання", size=9.5, color=GOLD, bold=True))

    # Стан 3: ISOLATED / FAULT
    s3_x, s3_y = 560, 80
    f.append(rect(s3_x, s3_y, sw, sh, fill="#fdf4f4", stroke=RED, sw=2.0, rx=8))
    f.append(text(s3_x + sw / 2, s3_y + 24, "ISOLATED", size=13, color=RED, bold=True))
    f.append(text(s3_x + sw / 2, s3_y + 44, "Відмова / Ізоляція (0%)", size=10.5, color=INK))
    f.append(line(s3_x + 10, s3_y + 54, s3_x + sw - 10, s3_y + 54, color="#fee2e2", sw=1.0))
    f.append(text(s3_x + sw / 2, s3_y + 70, "Штрафний рахунок ≥ 80", size=9.5, color=MUTED))
    f.append(text(s3_x + sw / 2, s3_y + 86, "Failsafe / Резерв / Зупинка", size=9.5, color=RED, bold=True))

    # Стрілки переходів вгорі (штрафи)
    f.append(arrow(s1_x + sw, s1_y + 30, s2_x - 6, s1_y + 30, color=GOLD, sw=1.6))
    f.append(text((s1_x + sw + s2_x) / 2, s1_y + 20, "+20 (збій)", size=9, color=GOLD, bold=True))

    f.append(arrow(s2_x + sw, s2_y + 30, s3_x - 6, s2_y + 30, color=RED, sw=1.6))
    f.append(text((s2_x + sw + s3_x) / 2, s2_y + 20, "+20 (серія збоїв)", size=9, color=RED, bold=True))

    # Стрілки переходів внизу (відновлення з гістерезисом)
    f.append(arrow(s3_x, s3_y + 70, s2_x + sw + 6, s3_y + 70, color=MUTED, sw=1.4))
    f.append(text((s2_x + sw + s3_x) / 2, s3_y + 84, "-1 (за відлік)", size=9, color=MUTED))

    f.append(arrow(s2_x, s2_y + 70, s1_x + sw + 6, s2_y + 70, color=GREEN, sw=1.4))
    f.append(text((s1_x + sw + s2_x) / 2, s2_y + 84, "-1 (N чистих)", size=9, color=GREEN, bold=True))

    # Пояснення механізму Leaky Bucket унизу
    bx, by, bw, bh = 60, 215, 680, 95
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=BORDER, sw=1.0, rx=6))
    f.append(text(bx + 18, by + 20, "Принцип роботи інтегратора (Leak Rate vs Penalty):", size=11, bold=True, anchor="start"))
    f.append(text(bx + 18, by + 40, "• Миттєвий збій (1 глітч) додає +20 балів штрафу: сигнал відкидається, але система НЕ падає у Failsafe.", size=10, color=INK, anchor="start"))
    f.append(text(bx + 18, by + 58, "• Кожен валідний відлік зменшує штраф на -1 бал: через 20 чистих кроків довіра повністю відновлюється.", size=10, color=INK, anchor="start"))
    f.append(text(bx + 18, by + 76, "• Серія з 4 збоїв поспіль досягає порогу 80: сенсор миттєво маркується як ISOLATED для захисту регулятора.", size=10, color=RED, bold=True, anchor="start"))

    render(os.path.join(IMG, "trust-bucket-transitions.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pipeline()
    fig_slew_rate()
    fig_cross_correlation()
    fig_trust_bucket()
    print("All figures generated successfully.")
