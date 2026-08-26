# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT    = "#f2f6fd"
GREENBG = "#eafaf0"
REDBG   = "#fdeeec"
GREYBG  = "#f1f2f4"
WARMBG  = "#fdf8ee"
WARN_ST = "#d97706"

# ── 1. Вікно спостереження Деннінга: W(t, Δ) ──────────────────────────────────
def fig_denning_window():
    W, H = 1000, 430
    p = []

    # Заголовок зверху
    p.append(text(500, 32, "Вікно спостереження часової локальності за моделлю Деннінга", size=16, bold=True))

    # Стрічка звернень до сторінок: r(1)...r(14)
    pages = ["P1", "P2", "P1", "P5", "P2", "P3", "P1", "P2", "P1", "P4", "P1", "P2", "P3", "P1"]
    x0, y_row, cell_w, cell_h = 70.0, 95.0, 60.0, 52.0

    p.append(text(x0 - 15, y_row + 30, "Звернення r(t):", size=13, bold=True, anchor="end"))

    # Вікно спостереження: від t=7 до t=12 (Δ = 6 кроків: P2, P1, P2, P1, P4, P1)
    win_start_idx = 6  # t=7 (0-indexed 6)
    win_end_idx = 11   # t=12 (0-indexed 11)
    win_x1 = x0 + win_start_idx * cell_w - 4
    win_x2 = x0 + (win_end_idx + 1) * cell_w + 4
    win_w = win_x2 - win_x1

    # Підсвітка рамки вікна Delta
    p.append(rect(win_x1, y_row - 10, win_w, cell_h + 20, fill=WARMBG, stroke=WARN_ST, sw=2.2, rx=8))
    p.append(text(win_x1 + win_w / 2, y_row - 18, "Вікно спостереження Δ = 6", size=14, color=WARN_ST, bold=True))

    # Комірки звернень
    for i, pg in enumerate(pages):
        cx = x0 + i * cell_w
        is_in_win = win_start_idx <= i <= win_end_idx
        bg = "#fff3d6" if is_in_win else FILL
        st = WARN_ST if is_in_win else LINE
        p.append(rect(cx + 4, y_row, cell_w - 8, cell_h, fill=bg, stroke=st, sw=1.6, rx=5))
        p.append(text(cx + cell_w / 2, y_row + 24, pg, size=15, bold=True, color=INK))
        p.append(text(cx + cell_w / 2, y_row + 43, "t=%d" % (i + 1), size=11, color=MUTED))

    # Стрілка часу
    p.append(arrow(x0, y_row + cell_h + 30, x0 + len(pages) * cell_w, y_row + cell_h + 30, color=LINE, sw=1.8))
    p.append(text(x0 + len(pages) * cell_w + 10, y_row + cell_h + 34, "Час t (інструкції)", size=12, anchor="start", bold=True))

    # Нижній блок: обчислення робочої множини
    p.append(line(win_x1 + win_w / 2, y_row + cell_h + 10, win_x1 + win_w / 2, y_row + cell_h + 75, color=WARN_ST, sw=1.8, dash="4,4"))
    p.append(arrow(win_x1 + win_w / 2, y_row + cell_h + 75, win_x1 + win_w / 2, y_row + cell_h + 95, color=WARN_ST, sw=1.8))

    box_y = y_row + cell_h + 98
    p.append(fitbox(70, box_y, 410, 80,
                    "Сторінки у вікні [t−5 .. t] при t=12:\n"
                    "r(7..12) = { P1, P2, P1, P4, P1, P2 }",
                    size=13, fill=SOFT, stroke=NEG, sw=1.5))

    p.append(arrow(490, box_y + 40, 540, box_y + 40, color=INK, sw=1.8))

    p.append(fitbox(550, box_y, 380, 80,
                    "Робоча множина W(12, 6) = { P1, P2, P4 }\n"
                    "Розмір робочої множини w(12, 6) = |W| = 3",
                    size=14, bold=True, fill=GREENBG, stroke=FIELD, sw=1.8))

    return render(os.path.join(OUT, "denning-window.svg"), W, H, *p)


# ── 2. Характеристична крива робочої множини w(Δ) та темп збоїв m(Δ) ─────────
def fig_working_set_curve():
    W, H = 1000, 490
    p = []

    p.append(text(500, 30, "Характеристична крива розміру робочої множини w(Δ) та частоти збоїв m(Δ)", size=15, bold=True))

    ox, oy = 110.0, 380.0
    gw, gh = 780.0, 300.0

    # Осі координат
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    p.append(text(ox + gw + 10, oy + 5, "Розмір вікна Δ", size=13, bold=True, anchor="start"))
    p.append(text(ox, oy - gh - 15, "Сторінки / Частота збоїв", size=13, bold=True, anchor="middle"))

    # Вертикальні зони
    z1_w = 200.0
    z2_w = 280.0
    z3_w = 300.0

    p.append(rect(ox, oy - gh + 20, z1_w, gh - 20, fill="#f4fbf7", stroke="none"))
    p.append(rect(ox + z1_w, oy - gh + 20, z2_w, gh - 20, fill="#fdfbf4", stroke="none"))
    p.append(rect(ox + z1_w + z2_w, oy - gh + 20, z3_w, gh - 20, fill="#f6f7fb", stroke="none"))

    p.append(line(ox + z1_w, oy, ox + z1_w, oy - gh + 20, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(ox + z1_w + z2_w, oy, ox + z1_w + z2_w, oy - gh + 20, color=MUTED, sw=1.2, dash="3,3"))

    p.append(text(ox + z1_w / 2, oy - gh + 38, "Фаза 1: Внутрішньоциклова", size=12, bold=True, color=FIELD))
    p.append(text(ox + z1_w / 2, oy - gh + 54, "швидке насичення локальності", size=11, color=MUTED))

    p.append(text(ox + z1_w + z2_w / 2, oy - gh + 38, "Фаза 2: Плато стабільності", size=12, bold=True, color=WARN_ST))
    p.append(text(ox + z1_w + z2_w / 2, oy - gh + 54, "оптимальне вікно Δ*", size=11, color=MUTED))

    p.append(text(ox + z1_w + z2_w + z3_w / 2, oy - gh + 38, "Фаза 3: Повний простір (VSS)", size=12, bold=True, color=NEG))
    p.append(text(ox + z1_w + z2_w + z3_w / 2, oy - gh + 54, "захоплення неактивних сторінок", size=11, color=MUTED))

    # Крива w(Δ) - синя суцільна
    # Початок (ox, oy), підйом до (ox+200, oy-180), плато до (ox+480, oy-210), насичення до (ox+750, oy-260)
    w_curve = (
        f'<path d="M {ox} {oy} '
        f'C {ox+60} {oy-120}, {ox+130} {oy-170}, {ox+z1_w} {oy-185} '
        f'C {ox+z1_w+90} {oy-195}, {ox+z1_w+190} {oy-205}, {ox+z1_w+z2_w} {oy-215} '
        f'C {ox+z1_w+z2_w+100} {oy-230}, {ox+z1_w+z2_w+200} {oy-255}, {ox+gw-30} {oy-260}" '
        f'fill="none" stroke="{NEG}" stroke-width="3"/>'
    )
    p.append(w_curve)
    p.append(text(ox + gw - 25, oy - 272, "w(Δ) — розмір множини", size=13, bold=True, color=NEG, anchor="end"))

    # Крива m(Δ) = dw/dΔ - червона пунктирна
    m_curve = (
        f'<path d="M {ox+5} {oy-270} '
        f'C {ox+40} {oy-160}, {ox+100} {oy-50}, {ox+z1_w} {oy-30} '
        f'C {ox+z1_w+100} {oy-18}, {ox+z1_w+200} {oy-12}, {ox+z1_w+z2_w} {oy-8} '
        f'C {ox+z1_w+z2_w+100} {oy-5}, {ox+z1_w+z2_w+200} {oy-3}, {ox+gw-30} {oy-2}" '
        f'fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6,4"/>'
    )
    p.append(m_curve)
    p.append(text(ox + 90, oy - 200, "m(Δ) — частота збоїв", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 90, oy - 182, "m(Δ) = dw/dΔ", size=12, color=POS, italic=True, anchor="start"))

    # Позначка оптимального вікна Δ*
    opt_x = ox + z1_w + 50
    p.append(line(opt_x, oy, opt_x, oy - 198, color=WARN_ST, sw=1.8, dash="4,4"))
    p.append(circle(opt_x, oy - 198, 5, fill=WARN_ST, stroke=INK, sw=1.5))
    p.append(text(opt_x, oy + 20, "Δ* (робоче вікно)", size=12, bold=True, color=WARN_ST))

    # Нижній коментар
    p.append(fitbox(ox, oy + 42, gw, 48,
                    "При перевищенні вікна Δ* розмір w(Δ) майже не зростає, а частота збоїв m(Δ) прямує до нуля.\n"
                    "Утримання саме цього обсягу сторінок у RAM гарантує максимум швидкодії за мінімуму кадрів.",
                    size=12, fill=FILL, stroke=MUTED, sw=1.2))

    return render(os.path.join(OUT, "working-set-curve.svg"), W, H, *p)


# ── 3. Трішинг: катастрофічний колапс продуктивності процесора ────────────────
def fig_thrashing_collapse():
    W, H = 1000, 480
    p = []

    p.append(text(500, 30, "Явище трішингу: колапс корисної роботи CPU при перевантаженні RAM", size=15, bold=True))

    ox, oy = 100.0, 370.0
    gw, gh = 800.0, 290.0

    # Осі координат
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2.0))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2.0))
    p.append(text(ox + gw + 10, oy + 5, "Рівень мультипрограмування (кількість процесів N)", size=13, bold=True, anchor="start"))
    p.append(text(ox, oy - gh - 15, "Завантаження CPU (%)", size=13, bold=True, anchor="middle"))

    # Критична межа N_crit: сума робочих множин перевищує RAM
    crit_x = ox + 430.0
    p.append(rect(ox, oy - gh + 20, crit_x - ox, gh - 20, fill="#f2faf4", stroke="none"))
    p.append(rect(crit_x, oy - gh + 20, ox + gw - crit_x, gh - 20, fill="#fef2f2", stroke="none"))

    p.append(line(crit_x, oy, crit_x, oy - gh + 20, color=POS, sw=2.2, dash="4,4"))

    p.append(text((ox + crit_x) / 2, oy - gh + 38, "Стабільна зона: ∑ w_i ≤ RAM", size=13, bold=True, color=FIELD))
    p.append(text((ox + crit_x) / 2, oy - gh + 54, "CPU виконує обчислення", size=11, color=MUTED))

    p.append(text((crit_x + ox + gw) / 2, oy - gh + 38, "Зона ТРІШИНГУ: ∑ w_i > RAM", size=13, bold=True, color=POS))
    p.append(text((crit_x + ox + gw) / 2, oy - gh + 54, "100% часу в черзі дискового I/O", size=11, color=MUTED))

    # Крива завантаження CPU (зелена/червона лінія з крутим спадом)
    cpu_path = (
        f'<path d="M {ox} {oy-20} '
        f'C {ox+120} {oy-140}, {ox+260} {oy-240}, {crit_x-40} {oy-260} '
        f'C {crit_x} {oy-260}, {crit_x+25} {oy-240}, {crit_x+50} {oy-120} '
        f'C {crit_x+80} {oy-30}, {crit_x+180} {oy-10}, {ox+gw-20} {oy-8}" '
        f'fill="none" stroke="{FIELD}" stroke-width="3.5"/>'
    )
    p.append(cpu_path)

    # Червоний відрізок після обвалу
    thrash_path = (
        f'<path d="M {crit_x-5} {oy-260} '
        f'C {crit_x+25} {oy-240}, {crit_x+50} {oy-120}, {crit_x+80} {oy-30} '
        f'C {crit_x+140} {oy-15}, {crit_x+220} {oy-10}, {ox+gw-20} {oy-8}" '
        f'fill="none" stroke="{POS}" stroke-width="3.5"/>'
    )
    p.append(thrash_path)

    # Пікова точка продуктивності
    p.append(circle(crit_x - 30, oy - 260, 6, fill=FIELD, stroke=INK, sw=1.8))
    p.append(text(crit_x - 30, oy - 275, "Максимум корисної праці", size=12, bold=True, color=FIELD))

    # Точка обвалу
    p.append(circle(crit_x + 55, oy - 100, 6, fill=POS, stroke=INK, sw=1.8))
    p.append(text(crit_x + 75, oy - 100, "Обвал: сторінковий шторм", size=12, bold=True, color=POS, anchor="start"))

    # Нижні пояснювальні блоки
    p.append(fitbox(ox, oy + 32, (crit_x - ox) - 10, 60,
                    "Кожен новий процес збільшує паралелізм,\n"
                    "поки сумарні робочі множини вміщуються в кадрах RAM.",
                    size=12, fill=GREENBG, stroke=FIELD, sw=1.4))

    p.append(fitbox(crit_x + 10, oy + 32, (ox + gw - crit_x) - 10, 60,
                    "Витіснення сторінки процесу A провокує негайний збій;\n"
                    "процеси витісняють дані один одного, черга I/O переповнена.",
                    size=12, fill=REDBG, stroke=POS, sw=1.4))

    return render(os.path.join(OUT, "thrashing-collapse.svg"), W, H, *p)


# ── 4. Архітектура Dual-LRU та Refault Distance у ядрі Linux ─────────────────
def fig_linux_lru_refault():
    W, H = 1040, 520
    p = []

    p.append(text(520, 28, "Оцінка робочої множини в Linux: списки Active/Inactive та Refault Distance", size=15, bold=True))

    # Верхня панель: Двосмуговий LRU
    bx, by, bw, bh = 50.0, 60.0, 940.0, 190.0
    p.append(rect(bx, by, bw, bh, fill=FILL, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(bx + 20, by + 24, "Списки сторінок ядра (per-cgroup / per-NUMA Node LRU)", size=14, bold=True, anchor="start"))

    # Active List
    ax, ay, aw, ah = 80.0, 105.0, 380.0, 120.0
    p.append(rect(ax, ay, aw, ah, fill=GREENBG, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(ax + aw / 2, ay + 24, "Active List (гаряча робоча множина)", size=14, bold=True, color=FIELD))
    p.append(text(ax + aw / 2, ay + 50, "Сторінки з бітом Referenced = 1", size=12, color=INK))
    p.append(text(ax + aw / 2, ay + 72, "Захищені від негайного вилучення", size=12, color=MUTED))
    p.append(text(ax + aw / 2, ay + 96, "Розмір: active_list_size", size=12, bold=True, color=FIELD))

    # Inactive List
    ix, iy, iw, ih = 580.0, 105.0, 380.0, 120.0
    p.append(rect(ix, iy, iw, ih, fill=SOFT, stroke=NEG, sw=1.8, rx=6))
    p.append(text(ix + iw / 2, iy + 24, "Inactive List (кандидати на витіснення)", size=14, bold=True, color=NEG))
    p.append(text(ix + iw / 2, iy + 50, "Сторінки з бітом Referenced = 0", size=12, color=INK))
    p.append(text(ix + iw / 2, iy + 72, "kswapd сканує та готує до скидання", size=12, color=MUTED))
    p.append(text(ix + iw / 2, iy + 96, "shrink_inactive_list()", size=12, bold=True, color=NEG))

    # Стрілки між списками
    # Демоція: Active -> Inactive
    p.append(arrow(ax + aw, ay + 40, ix, iy + 40, color=LINE, sw=1.8))
    p.append(text((ax + aw + ix) / 2, ay + 32, "Демоція (kswapd)", size=11, color=MUTED))

    # Промоція: Inactive -> Active
    p.append(arrow(ix, iy + 85, ax + aw, ay + 85, color=FIELD, sw=1.8))
    p.append(text((ax + aw + ix) / 2, iy + 77, "Повторний доступ", size=11, bold=True, color=FIELD))

    # Нижня панель: Витіснення та Refault Distance (workingset.c)
    ny = 270.0
    p.append(rect(bx, ny, bw, 225.0, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(bx + 20, ny + 24, "Алгоритм Refault Distance (mm/workingset.c)", size=14, bold=True, anchor="start"))

    # Крок 1: Вилучення
    p.append(fitbox(75, ny + 45, 260, 110,
                    "1. Витіснення з Inactive\n"
                    "Сторінка вилучається з RAM.\n"
                    "У Page Cache XArray записується\n"
                    "Тіньовий запис (Shadow Entry):\n"
                    "shadow = eviction_counter",
                    size=12, fill=WARMBG, stroke=WARN_ST, sw=1.5))

    p.append(arrow(340, ny + 100, 385, ny + 100, color=LINE, sw=1.8))

    # Крок 2: Повторний збій
    p.append(fitbox(390, ny + 45, 260, 110,
                    "2. Повторний збій (Refault)\n"
                    "Процес знову звертається до даних.\n"
                    "Обчислення дистанції вилучення:\n"
                    "distance = current_eviction -\n"
                    "           shadow_eviction",
                    size=12, fill=SOFT, stroke=NEG, sw=1.5))

    p.append(arrow(655, ny + 100, 700, ny + 100, color=LINE, sw=1.8))

    # Крок 3: Вердикт і адаптація
    p.append(fitbox(705, ny + 45, 265, 110,
                    "3. Порівняння з Active List\n"
                    "Якщо distance ≤ active_list_size:\n"
                    "• Сторінка була вилучена передчасно!\n"
                    "• Промоція ПРЯМО в Active List\n"
                    "• Розширення списку Active List",
                    size=12, bold=True, fill=GREENBG, stroke=FIELD, sw=1.8))

    p.append(fitbox(75, ny + 165, 895, 45,
                    "Висновок: Refault Distance дозволяє ядру динамічно адаптувати баланс Active/Inactive списків\n"
                    "без ручного налаштування, точно утримуючи активну робочу множину процесу в пам'яті.",
                    size=12, fill=FILL, stroke=MUTED, sw=1.2))

    return render(os.path.join(OUT, "linux-lru-refault.svg"), W, H, *p)


# ── 5. Рівні тиску пам'яті: від фонового kswapd до OOM Killer ─────────────────
def fig_memory_pressure_levels():
    W, H = 1000, 530
    p = []

    p.append(text(500, 28, "Шкала тиску на пам'ять у Linux: механізми реакції ядра", size=15, bold=True))

    levels = [
        ("Рівень 1: Норма",
         "RAM > WMARK_HIGH\n"
         "Фонові алокації проходять без затримок.\n"
         "kswapd спить, усі потоки працюють\n"
         "на штатній швидкості.",
         "PSI some = 0%\nPSI full = 0%", GREENBG, FIELD),
        ("Рівень 2: Фоновий реклейм",
         "RAM < WMARK_LOW\n"
         "Прокидається kswapd у фоні.\n"
         "Звільняє сторінки до WMARK_HIGH.\n"
         "Потоки не блокуються на CPU.",
         "PSI some < 15%\nPSI full = 0%", SOFT, NEG),
        ("Рівень 3: Прямий реклейм",
         "RAM < WMARK_MIN\n"
         "Алокуючий потік блокується.\n"
         "Ядро змушує його власноруч\n"
         "вивільняти пам'ять перед алокацією.",
         "PSI some > 40%\nPSI full > 10%", WARMBG, WARN_ST),
        ("Рівень 4: Трішинг & OOM Killer",
         "RAM вичерпана, реклейм буксує.\n"
         "systemd-oomd / kernel OOM Killer\n"
         "обирає жертву за oom_score\n"
         "і надсилає SIGKILL.",
         "PSI full > 50%\nOOM Trigger", REDBG, POS),
    ]

    x0, y0, col_w, col_h, gap = 45.0, 60.0, 212.0, 370.0, 20.0

    for i, (title, desc, psi, bg, st) in enumerate(levels):
        cx = x0 + i * (col_w + gap)

        # Рамка стовпця
        p.append(rect(cx, y0, col_w, col_h, fill=bg, stroke=st, sw=2.0, rx=8))

        # Заголовок стовпця
        p.append(fitbox(cx + 8, y0 + 12, col_w - 16, 40, title, size=13, bold=True, fill=FILL, stroke=st, sw=1.5))

        # Опис механізму
        p.append(fitbox(cx + 8, y0 + 62, col_w - 16, 185, desc, size=12, fill="#ffffff", stroke=MUTED, sw=1.0))

        # Показник PSI
        p.append(fitbox(cx + 8, y0 + 258, col_w - 16, 95, "Показники PSI:\n" + psi, size=12, bold=True, fill=FILL, stroke=st, sw=1.4))

    # Стрілка наростання дефіциту знизу
    p.append(arrow(x0, y0 + col_h + 30, x0 + 4 * col_w + 3 * gap, y0 + col_h + 30, color=POS, sw=2.2))
    p.append(text(500, y0 + col_h + 52, "Наростання дефіциту фізичної пам'яті (Memory Pressure)", size=13, bold=True, color=POS))

    return render(os.path.join(OUT, "memory-pressure-levels.svg"), W, H, *p)


if __name__ == "__main__":
    fig_denning_window()
    fig_working_set_curve()
    fig_thrashing_collapse()
    fig_linux_lru_refault()
    fig_memory_pressure_levels()
    print("All figures generated successfully.")
