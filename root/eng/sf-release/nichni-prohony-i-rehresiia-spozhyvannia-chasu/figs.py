# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def polyline(pts, stroke=LINE, sw=1.5, fill='none'):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# -- Figura 1: PR Fast Gate vs. Nightly Soak Pipeline --
def fig_pr_vs_nightly_pipeline():
    W, H = 1040, 540
    frags = []

    # Fast PR Gate Track
    frags.append(rect(30, 40, 980, 190, fill='#f8fafc', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(50, 70, 'Швидкі ворота PR (PR Gate: 5–10 хвилин на віртуальній машині)', size=13, bold=True, color='#1e293b', anchor='start'))
    frags.append(text(50, 90, 'Швидкий зворотний зв\'язок для розробника: ізольовані модулі та логіка', size=11, color=MUTED, anchor='start'))

    b_pr_src, _, _ = textbox(140, 150, 'Код PR / Commit\n(Trunk / Feature)', size=11, bold=True, fill='#ffffff', stroke=LINE, sw=1.5, pad=8)
    frags.append(b_pr_src)

    b_pr_lint, _, _ = textbox(370, 150, 'Статичний аналіз\n(Linters, SAST, Clang-Tidy)', size=11, bold=True, fill='#ffffff', stroke=NEG, sw=1.5, pad=8)
    frags.append(b_pr_lint)

    b_pr_unit, _, _ = textbox(620, 150, 'Модульні тести\n(GoogleTest, PyTest, Моки)', size=11, bold=True, fill='#ffffff', stroke=NEG, sw=1.5, pad=8)
    frags.append(b_pr_unit)

    b_pr_merge, _, _ = textbox(880, 150, 'Злиття в Main\n(Fast Gate Passed)', size=11, bold=True, fill='#ecfdf5', stroke=FIELD, sw=1.8, pad=8)
    frags.append(b_pr_merge)

    frags.append(arrow(225, 150, 265, 150, color=LINE, sw=1.5))
    frags.append(arrow(475, 150, 515, 150, color=LINE, sw=1.5))
    frags.append(arrow(725, 150, 785, 150, color=FIELD, sw=1.8))

    # Downward arrow to nightly run
    frags.append(arrow(880, 190, 880, 265, color='#6366f1', sw=2))
    frags.append(text(890, 230, 'Нічний тригер (02:00)', size=10, bold=True, color='#6366f1', anchor='start'))

    # Nightly Soak Track
    frags.append(rect(30, 270, 980, 240, fill='#f5f3ff', stroke='#c4b5fd', sw=1.5, rx=8))
    frags.append(text(50, 300, 'Автоматизований нічний стенд (Nightly Soak & Profiling: 6–10 годин на фізичному залізі / HIL)', size=13, bold=True, color='#4338ca', anchor='start'))
    frags.append(text(50, 320, 'Глибокий регресійний аналіз апаратних та часових характеристик системи', size=11, color=MUTED, anchor='start'))

    b_pwr, _, _ = textbox(150, 415, 'Power Profiler (HIL)\nСтрум сну (uA), сплески (mA)\nІнтеграл енергії (Дж)', size=10, bold=True, fill='#ffffff', stroke='#d97706', sw=1.5, pad=8)
    frags.append(b_pwr)

    b_mem, _, _ = textbox(400, 415, 'Heap Soak (6–8 год)\nВитоки купи, фрагментація\nmax_free_block динаміка', size=10, bold=True, fill='#ffffff', stroke='#dc2626', sw=1.5, pad=8)
    frags.append(b_mem)

    b_lat, _, _ = textbox(650, 415, 'Latency Benchmarks\np95/p99 хвіст затримки\nКонтеншн блокувань', size=10, bold=True, fill='#ffffff', stroke='#2563eb', sw=1.5, pad=8)
    frags.append(b_lat)

    b_stat, _, _ = textbox(890, 415, 'Статистичний CUSUM\nВиявлення регресій\nАвто-bisect до коміту', size=10, bold=True, fill='#ffffff', stroke=POS, sw=1.8, pad=8)
    frags.append(b_stat)

    frags.append(arrow(250, 415, 295, 415, color=LINE, sw=1.3))
    frags.append(arrow(505, 415, 545, 415, color=LINE, sw=1.3))
    frags.append(arrow(755, 415, 795, 415, color=POS, sw=1.6))

    render(os.path.join(IMG, 'pr-vs-nightly-pipeline.svg'), W, H, *frags,
           title='Порівняння конвеєра швидких воріт PR та тривалого нічного стенду')


# -- Figura 2: Power Profiling States --
def fig_power_profiling_states():
    W, H = 1000, 500
    frags = []

    frags.append(rect(30, 30, 940, 440, fill='#ffffff', stroke='#e2e8f0', sw=1.5, rx=8))
    frags.append(text(50, 60, 'Осцилограма профілю споживання струму: Еталон vs Регресія в прошивці', size=13, bold=True, color='#1e293b', anchor='start'))
    frags.append(text(50, 80, 'Фіксація витоку струму сну, затягнутого активного стану та паразитних пробуджень', size=11, color=MUTED, anchor='start'))

    ox, oy = 90, 400
    frags.append(line(ox, oy, ox + 830, oy, color='#94a3b8', sw=1.5))
    frags.append(line(ox, oy, ox, 110, color='#94a3b8', sw=1.5))

    frags.append(text(ox - 10, oy + 5, '0', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 70, '1 mA', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 160, '20 mA', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 240, '50 mA', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, 115, 'Струм I(t)', size=11, bold=True, color='#334155', anchor='end'))
    frags.append(text(ox + 820, oy + 25, 'Час t (мс)', size=11, bold=True, color='#334155', anchor='end'))

    for y_val in [oy - 70, oy - 160, oy - 240]:
        frags.append(line(ox, y_val, ox + 830, y_val, color='#f1f5f9', sw=1, dash='4,4'))

    pts_baseline = [
        (ox, oy - 4), (ox + 180, oy - 4),
        (ox + 185, oy - 230), (ox + 215, oy - 230), (ox + 220, oy - 4),
        (ox + 500, oy - 4),
        (ox + 505, oy - 230), (ox + 535, oy - 230), (ox + 540, oy - 4),
        (ox + 830, oy - 4)
    ]
    frags.append(polyline(pts_baseline, stroke=FIELD, sw=2.5))

    pts_regressed = [
        (ox, oy - 75), (ox + 180, oy - 75),
        (ox + 185, oy - 248), (ox + 310, oy - 248), (ox + 315, oy - 75),
        (ox + 390, oy - 75), (ox + 395, oy - 170), (ox + 425, oy - 170), (ox + 430, oy - 75),
        (ox + 500, oy - 75), (ox + 505, oy - 248), (ox + 630, oy - 248), (ox + 635, oy - 75),
        (ox + 830, oy - 75)
    ]
    frags.append(polyline(pts_regressed, stroke=POS, sw=2))

    b_leg1, _, _ = textbox(280, 140, 'Еталон: Глибокий сон 18 мкА\nКороткий активний цикл (30 мс, 45 мА)\nСередня потужність: 1.2 мВт', size=9, bold=True, fill='#ecfdf5', stroke=FIELD, sw=1.2, pad=6)
    frags.append(b_leg1)

    b_leg2, _, _ = textbox(700, 140, 'Регресія: Витік струму сну (1.8 мА)\nЗатягнута обробка (130 мс) + Паразитне пробудження\nСередня потужність: 14.8 мВт (+1130%)', size=9, bold=True, fill='#fff5f5', stroke=POS, sw=1.2, pad=6)
    frags.append(b_leg2)

    frags.append(arrow(340, 260, ox + 250, oy - 245, color=POS, sw=1.2))
    frags.append(text(345, 255, 'Завислий WakeLock / Тривалий I2C polling', size=9, color=POS, anchor='start'))

    frags.append(arrow(410, oy - 40, ox + 410, oy - 75, color=POS, sw=1.2))
    frags.append(text(420, oy - 35, 'Плаваючий GPIO пін / Unclocked domain', size=9, color=POS, anchor='start'))

    render(os.path.join(IMG, 'power-profiling-states.svg'), W, H, *frags,
           title='Профілювання споживання струму: виявлення регресій у sleep та active режимах')


# -- Figura 3: Heap Fragmentation & Soak --
def fig_heap_fragmentation_soak():
    W, H = 1000, 500
    frags = []

    frags.append(rect(30, 30, 940, 440, fill='#ffffff', stroke='#e2e8f0', sw=1.5, rx=8))
    frags.append(text(50, 60, 'Динаміка пам\'яті під час 8-годинного нічного тесту (Soak Test)', size=13, bold=True, color='#1e293b', anchor='start'))
    frags.append(text(50, 80, 'Колапс найбільшого неперервного блоку (max_free_block) при збереженні вільної пам\'яті', size=11, color=MUTED, anchor='start'))

    ox, oy = 90, 400
    frags.append(line(ox, oy, ox + 830, oy, color='#94a3b8', sw=1.5))
    frags.append(line(ox, oy, ox, 110, color='#94a3b8', sw=1.5))

    frags.append(text(ox - 10, oy + 5, '0 KB', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 70, '32 KB', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 140, '64 KB', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 210, '96 KB', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, oy - 270, '128 KB', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, 115, 'Пам\'ять RAM', size=11, bold=True, color='#334155', anchor='end'))

    frags.append(text(ox + 5, oy + 20, '0 год', size=10, color=MUTED, anchor='start'))
    frags.append(text(ox + 200, oy + 20, '2 год', size=10, color=MUTED))
    frags.append(text(ox + 400, oy + 20, '4 год', size=10, color=MUTED))
    frags.append(text(ox + 600, oy + 20, '6 год', size=10, color=MUTED))
    frags.append(text(ox + 820, oy + 20, '8 год (Тривалість тесту)', size=10, color=MUTED, anchor='end'))

    for y_val in [oy - 70, oy - 140, oy - 210, oy - 270]:
        frags.append(line(ox, y_val, ox + 830, y_val, color='#f1f5f9', sw=1, dash='4,4'))

    pts_free_heap = [
        (ox, oy - 235), (ox + 200, oy - 220), (ox + 400, oy - 200), (ox + 600, oy - 180), (ox + 830, oy - 160)
    ]
    frags.append(polyline(pts_free_heap, stroke='#d97706', sw=2.5))

    pts_leak = [
        (ox, oy - 10), (ox + 200, oy - 25), (ox + 400, oy - 45), (ox + 600, oy - 65), (ox + 830, oy - 85)
    ]
    frags.append(polyline(pts_leak, stroke=POS, sw=2))

    pts_max_block = [
        (ox, oy - 220), (ox + 100, oy - 200), (ox + 200, oy - 150), (ox + 350, oy - 90),
        (ox + 500, oy - 45), (ox + 620, oy - 18), (ox + 830, oy - 12)
    ]
    frags.append(polyline(pts_max_block, stroke='#7c3aed', sw=2.5))

    frags.append(circle(ox + 620, oy - 18, 5, fill=POS, stroke='#ffffff', sw=1.5))
    b_crash, _, _ = textbox(ox + 620, oy - 85, 'OOM Crash на 6.2 год:\nmalloc(16 KB) повернув NULL,\nхоча сумарно вільно 78 KB!', size=9, bold=True, fill='#fff5f5', stroke=POS, sw=1.2, pad=6)
    frags.append(b_crash)
    frags.append(arrow(ox + 620, oy - 55, ox + 620, oy - 26, color=POS, sw=1.5))

    b_l1, _, _ = textbox(240, 140, 'Загальна вільна пам\'ять (Free Heap, ~75 KB)', size=9, bold=True, fill='#fffbeb', stroke='#d97706', sw=1.2, pad=5)
    frags.append(b_l1)
    b_l2, _, _ = textbox(520, 140, 'Найбільший неперервний блок (max_free_block)', size=9, bold=True, fill='#f5f3ff', stroke='#7c3aed', sw=1.2, pad=5)
    frags.append(b_l2)
    b_l3, _, _ = textbox(790, 140, 'Накопичений витік пам\'яті (Leak)', size=9, bold=True, fill='#fff5f5', stroke=POS, sw=1.2, pad=5)
    frags.append(b_l3)

    render(os.path.join(IMG, 'heap-fragmentation-soak.svg'), W, H, *frags,
           title='Динаміка пам\'яті та фрагментація купи під час тривалого нічного тестування')


# -- Figura 4: Latency Distribution Shift --
def fig_latency_distribution_shift():
    W, H = 1000, 500
    frags = []

    frags.append(rect(30, 30, 940, 440, fill='#ffffff', stroke='#e2e8f0', sw=1.5, rx=8))
    frags.append(text(50, 60, 'Деградація розподілу часу відгуку (Tail Latency Shift під навантаженням)', size=13, bold=True, color='#1e293b', anchor='start'))
    frags.append(text(50, 80, 'Непомітність регресії на медіані (p50) при катастрофічному вибуху 99-го перцентиля (p99)', size=11, color=MUTED, anchor='start'))

    ox, oy = 90, 400
    frags.append(line(ox, oy, ox + 830, oy, color='#94a3b8', sw=1.5))
    frags.append(line(ox, oy, ox, 110, color='#94a3b8', sw=1.5))

    frags.append(text(ox - 10, oy + 5, '0', size=10, color=MUTED, anchor='end'))
    frags.append(text(ox - 10, 115, 'Щільність ймовірності P(t)', size=11, bold=True, color='#334155', anchor='end'))
    frags.append(text(ox + 820, oy + 25, 'Час відгуку (мс)', size=11, bold=True, color='#334155', anchor='end'))

    frags.append(text(ox + 80, oy + 15, '1 мс', size=9, color=MUTED))
    frags.append(text(ox + 160, oy + 15, '2.5 мс (p50)', size=9, bold=True, color=FIELD))
    frags.append(text(ox + 280, oy + 15, '5 мс (p95 еталон)', size=9, color=MUTED))
    frags.append(text(ox + 420, oy + 15, '12 мс', size=9, color=MUTED))
    frags.append(text(ox + 580, oy + 15, '25 мс (p95 регресія)', size=9, color=POS))
    frags.append(text(ox + 750, oy + 15, '60 мс (p99 хвіст)', size=9, bold=True, color=POS))

    pts_base_dist = [
        (ox + 40, oy - 2), (ox + 100, oy - 30), (ox + 130, oy - 120),
        (ox + 160, oy - 250), (ox + 190, oy - 120), (ox + 230, oy - 40),
        (ox + 280, oy - 12), (ox + 350, oy - 2), (ox + 800, oy - 2)
    ]
    frags.append(polyline(pts_base_dist, stroke=FIELD, sw=2.5))

    pts_reg_dist = [
        (ox + 40, oy - 2), (ox + 100, oy - 25), (ox + 130, oy - 95),
        (ox + 160, oy - 190), (ox + 190, oy - 95), (ox + 250, oy - 45),
        (ox + 380, oy - 40), (ox + 480, oy - 65), (ox + 550, oy - 55),
        (ox + 650, oy - 30), (ox + 750, oy - 10), (ox + 800, oy - 2)
    ]
    frags.append(polyline(pts_reg_dist, stroke=POS, sw=2))

    frags.append(line(ox + 160, oy, ox + 160, oy - 260, color=FIELD, sw=1.2, dash='4,4'))
    frags.append(line(ox + 750, oy, ox + 750, oy - 120, color=POS, sw=1.5, dash='4,4'))

    b_p50, _, _ = textbox(ox + 160, oy - 285, 'p50 не змінився:\n2.4 мс -> 2.5 мс\n(CI вважає все зеленим)', size=9, bold=True, fill='#ecfdf5', stroke=FIELD, sw=1.2, pad=5)
    frags.append(b_p50)

    b_p99, _, _ = textbox(ox + 670, oy - 160, 'p99 хвіст зріс у 12 разів:\n5.2 мс -> 60.4 мс\n(Контеншн черги / GC pauses)', size=9, bold=True, fill='#fff5f5', stroke=POS, sw=1.2, pad=5)
    frags.append(b_p99)

    render(os.path.join(IMG, 'latency-distribution-shift.svg'), W, H, *frags,
           title='Деградація розподілу затримок та вибух важкого хвоста p99 під тривалим навантаженням')


if __name__ == '__main__':
    fig_pr_vs_nightly_pipeline()
    fig_power_profiling_states()
    fig_heap_fragmentation_soak()
    fig_latency_distribution_shift()
    print("All figures generated successfully.")
