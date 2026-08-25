# -*- coding: utf-8 -*-
"""Фігури до теми «Диференційна пара».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Одна лінія проти пари: де живе сигнал ─────────────────────────────────
def fig_single_vs_diff():
    W, H = 760, 430
    f = [text(W / 2, 28, "Одна лінія міряє від спільної землі; пара міряє сама від себе",
              size=16, bold=True)]

    # --- ліворуч: однопровідна (single-ended) ---
    f.append(text(190, 62, "Однопровідна лінія", size=14, bold=True, color=MUTED))
    f.append(line(70, 110, 320, 110, color=INK, sw=2.4))            # сигнальний дріт
    f.append(text(70, 100, "TX", size=12, bold=True, anchor="start"))
    f.append(text(320, 100, "RX", size=12, bold=True, anchor="end"))
    f.append(line(70, 175, 320, 175, color=MUTED, sw=2.0))          # спільна земля
    f.append(text(195, 192, "спільна земля (GND)", size=11, color=MUTED))
    # стрілка «що міряє приймач»
    f.append(arrow(300, 110, 300, 173, color=NEG))
    f.append(text(308, 145, "V лінії", size=11, color=NEG, anchor="start"))
    # завада б'є по сигналу відносно землі
    f.append(text(195, 84, "завада", size=11, color=POS))
    for sx in (150, 175, 200, 225):
        f.append(line(sx, 90, sx, 108, color=POS, sw=1.4, dash="2,2"))
    f.append(text(195, 240, "рівень міряється ВІД землі:", size=12, anchor="middle"))
    f.append(text(195, 258, "завада на дроті чи зсув земель", size=12, anchor="middle", color=POS))
    f.append(text(195, 276, "→ прямо псує відлік", size=12, anchor="middle", color=POS))

    # --- праворуч: диференційна пара ---
    f.append(text(575, 62, "Диференційна пара", size=14, bold=True, color=FIELD))
    f.append(line(450, 100, 700, 100, color=POS, sw=2.4))           # A
    f.append(text(450, 90, "A", size=12, bold=True, anchor="start", color=POS))
    f.append(line(450, 150, 700, 150, color=NEG, sw=2.4))           # B
    f.append(text(450, 142, "B", size=12, bold=True, anchor="start", color=NEG))
    # приймач міряє різницю A−B
    f.append(arrow(680, 150, 680, 102, color=FIELD))
    f.append(text(688, 128, "A − B", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(575, 240, "рівень — це РІЗНИЦЯ двох дротів:", size=12, anchor="middle"))
    f.append(text(575, 258, "спільної опорної землі не треба,", size=12, anchor="middle", color=FIELD))
    f.append(text(575, 276, "сигнал «носить опору з собою»", size=12, anchor="middle", color=FIELD))

    # розділювач
    f.append(line(380, 70, 380, 300, color="#d0d4d8", sw=1.2, dash="4,4"))

    box = fitbox(120, 340, 600, 78, [
                 "Однопровідна лінія беззахисна: її «1» і «0» визначені тільки",
                 "відносно спільної землі, тож будь-яка завада на дроті чи зсув земель",
                 "одразу псує відлік. Пара ж кодує біт у різниці двох дротів — і ця",
                 "різниця не залежить від того, що коїться зі «спільним» рівнем."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "single-vs-diff.svg"), W, H, *f)


# ── 2. Серце ідеї: синфазна завада гаситься різницею ─────────────────────────
def fig_common_mode():
    W, H = 780, 470
    f = [text(W / 2, 28, "Завада сідає на ОБИДВА дроти однаково — і зникає в різниці",
              size=16, bold=True)]

    # три панелі: A, B, та A−B
    x0 = 70
    panW = 210
    gap = 20

    def panel(px, title, base, label_color, show_noise=True):
        # осі
        ax = px
        ay = 110
        h = 120
        f.append(text(px + panW / 2, ay - 16, title, size=13, bold=True, color=label_color))
        f.append(line(ax, ay, ax, ay + h, color=MUTED, sw=1.2))       # вісь V
        f.append(line(ax, ay + h, ax + panW, ay + h, color=MUTED, sw=1.2))  # вісь t
        f.append(text(ax - 6, ay + 6, "V", size=10, color=MUTED, anchor="end"))
        f.append(text(ax + panW, ay + h + 14, "t", size=10, color=MUTED, anchor="end"))
        return ax, ay, h

    # корисний сигнал: меандр; рівні всередині панелі
    def square(ax, ay, h, hi, lo, color, noise_amp=0.0, noise_color=POS, sw=2.4):
        # 4 півперіоди
        seg = panW / 4.0
        ys_hi = ay + h - hi
        ys_lo = ay + h - lo
        levels = [ys_hi, ys_lo, ys_hi, ys_lo]
        pts = []
        x = ax
        prev = None
        for i, yl in enumerate(levels):
            if prev is not None and prev != yl:
                f.append(line(x, prev, x, yl, color=color, sw=sw))
            f.append(line(x, yl, x + seg, yl, color=color, sw=sw))
            prev = yl
            x += seg
        # хвиляста завада поверх (спільна для A і B)
        if noise_amp > 0:
            import math
            path = []
            steps = 60
            for k in range(steps + 1):
                xx = ax + panW * k / steps
                yy = (ay + h * 0.30) + noise_amp * math.sin(k * 0.9)
                path.append("%s%.1f,%.1f" % ("M" if k == 0 else "L", xx, yy))
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                     'stroke-dasharray="3,2"/>' % (" ".join(path), noise_color))

    # --- Панель A = сигнал + завада ---
    ax, ay, h = panel(x0, "Дріт A  =  сигнал + завада", 0, POS)
    square(ax, ay, h, hi=88, lo=30, color=POS, noise_amp=14, noise_color="#e67e22")

    # --- Панель B = протифаза + ТА САМА завада ---
    ax, ay, h = panel(x0 + panW + gap, "Дріт B  =  протифаза + завада", 0, NEG)
    square(ax, ay, h, hi=30, lo=88, color=NEG, noise_amp=14, noise_color="#e67e22")

    # --- Панель A−B = чистий подвоєний сигнал ---
    ax, ay, h = panel(x0 + 2 * (panW + gap), "Різниця A − B", 0, FIELD)
    square(ax, ay, h, hi=100, lo=18, color=FIELD, noise_amp=0)

    # позначка завади
    f.append(text(x0 + panW / 2, 250, "завада ↑", size=11, color="#e67e22"))
    f.append(text(x0 + panW + gap + panW / 2, 250, "та сама завада ↑", size=11, color="#e67e22"))
    f.append(text(x0 + 2 * (panW + gap) + panW / 2, 250, "завади немає!", size=11, bold=True, color=FIELD))

    # стрілки «віднімаємо»
    f.append(text(x0 + panW + 4, 175, "−", size=26, bold=True, color=INK))
    f.append(text(x0 + 2 * panW + gap + 4, 175, "=", size=24, bold=True, color=INK))

    box = fitbox(70, 290, 640, 116, [
                 "Обидва дроти лежать поруч, тож наведена завада (синфазна, common-mode) сідає",
                 "на них майже однаково:  A = +s + n,  B = −s + n.  Приймач рахує різницю",
                 "A − B = (+s + n) − (−s + n) = 2s.  Доданок n входить з однаковим знаком у обидва",
                 "дроти й при відніманні скорочується дощенту, а корисний сигнал, що стоїть у дротах",
                 "протифазно, навпаки — подвоюється. Ось чому пара тиха там, де одна лінія",
                 "вже захлинулася б завадою."],
                 size=12.5, fill="#eef7f0", stroke=FIELD)
    f.append(box)
    render(os.path.join(IMG, "common-mode.svg"), W, H, *f)


# ── 3. Контрольований імпеданс пари й узгодження довжин ──────────────────────
def fig_impedance_skew():
    W, H = 770, 470
    f = [text(W / 2, 28, "Виту пару тримають сталого імпедансу й однакової довжини",
              size=16, bold=True)]

    # --- ліворуч: вита пара з Z0 і термінатором ---
    f.append(text(210, 62, "Контрольований імпеданс", size=14, bold=True, color=MUTED))
    # драйвер
    db = textbox(95, 150, "драйвер", size=12, fill="#eef2f7")
    f.append(db[0])
    # дві звивисті лінії (вита пара) — синусоїдні, у протифазі
    import math
    def wavy(y_mid, color, phase):
        steps = 80
        x1, x2 = 150, 300
        path = []
        for k in range(steps + 1):
            xx = x1 + (x2 - x1) * k / steps
            yy = y_mid + 9 * math.sin(k * 0.6 + phase)
            path.append("%s%.1f,%.1f" % ("M" if k == 0 else "L", xx, yy))
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path), color))
    wavy(132, POS, 0)
    wavy(168, NEG, math.pi)        # протифаза → переплетення
    f.append(text(225, 110, "вита пара", size=11, color=INK))
    # термінатор Z0
    f.append(line(300, 132, 320, 132, color=POS, sw=2.2))
    f.append(line(300, 168, 320, 168, color=NEG, sw=2.2))
    f.append(rect(320, 128, 14, 44, fill="#fff7e6", stroke="#e67e22", sw=1.8, rx=3))
    f.append(text(355, 145, "R = Z₀", size=12, color="#e67e22", anchor="start", bold=True))
    f.append(text(355, 162, "≈ 100–120 Ω", size=11, color=MUTED, anchor="start"))
    f.append(text(210, 215, "стала відстань між дротами →", size=11.5, anchor="middle"))
    f.append(text(210, 232, "сталий хвильовий опір Z₀", size=11.5, anchor="middle", color=MUTED))

    # розділювач
    f.append(line(420, 70, 420, 250, color="#d0d4d8", sw=1.2, dash="4,4"))

    # --- праворуч: перекіс довжин ---
    f.append(text(595, 62, "Узгодження довжин", size=14, bold=True, color=MUTED))
    # дріт A прямий
    f.append(line(470, 120, 700, 120, color=POS, sw=2.4))
    f.append(text(465, 116, "A", size=12, bold=True, anchor="end", color=POS))
    # дріт B з «гачком» (довший)
    f.append('<path d="M470,168 L560,168 L575,150 L590,186 L605,168 L700,168" '
             'fill="none" stroke="%s" stroke-width="2.4"/>' % NEG)
    f.append(text(465, 164, "B", size=12, bold=True, anchor="end", color=NEG))
    f.append(text(585, 205, "B довший → його фронт спізнюється", size=11, color=POS, anchor="middle"))
    # позначка Δt на приймачі
    f.append(line(700, 110, 700, 180, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(595, 232, "розбіг фронтів Δt = перекіс (skew)", size=11.5, anchor="middle", color=POS))

    box = fitbox(70, 290, 640, 116, [
                 "Швидкий фронт на парі — це хвиля, тож пара поводиться як лінія з власним хвильовим",
                 "опором Z₀ (диференційний, типово 90–120 Ω). Тримаючи сталу відстань між дротами,",
                 "ми тримаємо Z₀ сталим по всій довжині; на дальньому кінці ставимо резистор R = Z₀,",
                 "щоб хвиля поглиналася, а не відбивалася назад відлунням. А коли дроти різної",
                 "довжини, протифазні фронти приходять не одночасно (skew): у мить переходу різниця",
                 "A − B на мить хибна — на високій швидкості це помилка. Тому пари ведуть рівними."],
                 size=12.5, fill="#f4f6f8")
    f.append(box)
    render(os.path.join(IMG, "impedance-skew.svg"), W, H, *f)


# ── 4. Де працюють пари: карта інтерфейсів ──────────────────────────────────
def fig_where():
    W, H = 770, 430
    f = [text(W / 2, 28, "Майже всі швидкі й далекобійні лінії — диференційні пари",
              size=16, bold=True)]

    # дві колонки: однопровідні vs диференційні
    f.append(text(200, 64, "Однопровідні (single-ended)", size=14, bold=True, color=NEG))
    f.append(text(560, 64, "Диференційні пари", size=14, bold=True, color=FIELD))
    f.append(line(385, 75, 385, 360, color="#d0d4d8", sw=1.2, dash="4,4"))

    se = [
        ("UART / RS-232", "коротко, повільно, проста плата"),
        ("I²C", "у межах плати, кілька пристроїв"),
        ("SPI", "у межах плати, висока швидкість"),
    ]
    diff = [
        ("USB (D+ / D−)", "периферія, метри кабелю"),
        ("Ethernet (вита пара)", "десятки–сотні метрів"),
        ("CAN (CAN_H / CAN_L)", "авто, шум двигуна, шина"),
        ("RS-485 (A / B)", "сотні метрів, промисловість"),
        ("LVDS", "дисплеї, дуже швидкі дані"),
    ]
    y = 100
    for name, note in se:
        b = textbox(200, y, name, size=12.5, fill="#eaf0fd", stroke=NEG, min_w=180)
        f.append(b[0])
        f.append(text(200, y + 22, note, size=10.5, color=MUTED))
        y += 60

    y = 100
    for name, note in diff:
        b = textbox(560, y, name, size=12.5, fill="#eef7f0", stroke=FIELD, min_w=210)
        f.append(b[0])
        f.append(text(560, y + 20, note, size=10.5, color=MUTED))
        y += 53

    f.append(text(200, 330, "коротко й повільно —", size=11.5, anchor="middle", color=NEG))
    f.append(text(200, 347, "одного дроту досить", size=11.5, anchor="middle", color=NEG))

    render(os.path.join(IMG, "where.svg"), W, H, *f)


if __name__ == "__main__":
    fig_single_vs_diff()
    fig_common_mode()
    fig_impedance_skew()
    fig_where()
    print("OK: figures written to", IMG)
