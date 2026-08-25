# -*- coding: utf-8 -*-
"""Фігури до теми «Умова генерації» (hw-analog / umova-heneratsii).

Фігури:
  1. barkhausen-loop.svg          — Канонічна замкнена петля автогенератора (A та β) з подвійним критерієм Баркгаузена
  2. noise-to-sine-startup.svg    — Процес самозбудження в часі: тепловий шум -> експоненційне наростання -> насичення -> стабільна синусоїда
  3. root-locus-poles.svg         — Комплексна s-площина (Re/Im): пара полюсів у правій півплощині при запуску та перехід на уявну вісь jω
  4. amplitude-stabilization.svg  — Механізми стабілізації амплітуди: нелінійне насичення (компресія підсилення) проти АРП / термостабілізації
  5. oscillator-topologies.svg    — Порівняльна матриця 4 класичних топологій (міст Віна, фазозсувний RC, Колпітц, Хартлі)

Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_barkhausen_loop():
    """Канонічна замкнена петля автогенератора з підсилювачем A(jω) та ланкою β(jω)."""
    W, H = 760, 360
    p = []

    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))

    # Вузол сумування (позитивний зворотний зв'язок)
    sum_cx, sum_cy = 130, 120
    p.append(circle(sum_cx, sum_cy, 18, fill="#ffffff", stroke=LINE, sw=2))
    p.append(text(sum_cx, sum_cy + 5, "+", size=18, color=POS, bold=True))
    p.append(text(sum_cx - 30, sum_cy - 12, "v_вх = 0", size=11, color=MUTED, anchor="end"))
    p.append(arrow(sum_cx - 45, sum_cy, sum_cx - 18, sum_cy, color=MUTED, sw=1.5))

    # Блок прямого підсилення A(jω)
    amp_x, amp_y, amp_w, amp_h = 240, 80, 180, 80
    b_amp, _, _ = textbox(amp_x + amp_w / 2, amp_y + amp_h / 2,
                          "Підсилювач\nA(jω) = |A| · e^(j φ_A)",
                          size=13, pad=12, fill="#f4f8fd", stroke=NEG, sw=2, bold=True)
    p.append(b_amp)

    # Зв'язок суматор -> підсилювач
    p.append(arrow(sum_cx + 18, sum_cy, amp_x, sum_cy, color=INK, sw=2))
    p.append(text((sum_cx + 18 + amp_x) / 2, sum_cy - 8, "v_d", size=12, color=INK, italic=True))

    # Вихідний вузол
    node_x = 510
    p.append(line(amp_x + amp_w, sum_cy, node_x, sum_cy, color=INK, sw=2))
    p.append(circle(node_x, sum_cy, 4.5, fill=INK, stroke=INK))
    p.append(arrow(node_x, sum_cy, node_x + 90, sum_cy, color=INK, sw=2))
    p.append(text(node_x + 100, sum_cy + 5, "v_вих(t)", size=13, color=INK, bold=True, anchor="start"))

    # Блок зворотного зв'язку β(jω)
    fb_x, fb_y, fb_w, fb_h = 240, 220, 180, 80
    b_fb, _, _ = textbox(fb_x + fb_w / 2, fb_y + fb_h / 2,
                         "Вибіркова ланка\nβ(jω) = |β| · e^(j φ_β)",
                         size=13, pad=12, fill="#eef8f2", stroke=FIELD, sw=2, bold=True)
    p.append(b_fb)

    # Зв'язок вихід -> β
    p.append(line(node_x, sum_cy, node_x, fb_y + fb_h / 2, color=INK, sw=2))
    p.append(arrow(node_x, fb_y + fb_h / 2, fb_x + fb_w, fb_y + fb_h / 2, color=INK, sw=2))

    # Зв'язок β -> суматор (+)
    p.append(line(fb_x, fb_y + fb_h / 2, sum_cx, fb_y + fb_h / 2, color=INK, sw=2))
    p.append(arrow(sum_cx, fb_y + fb_h / 2, sum_cx, sum_cy + 18, color=INK, sw=2))
    p.append(text(sum_cx + 12, fb_y - 15, "v_зз = β·v_вих", size=12, color=FIELD, anchor="start"))

    # Рамка критеріїв Баркгаузена
    crit_box, _, _ = textbox(W / 2 + 190, 260,
                             "Критерій Баркгаузена:\n"
                             "1. Баланс амплітуд: |A(jω₀) · β(jω₀)| = 1\n"
                             "2. Баланс фаз: φ_A + φ_β = 2·π·n (0°)",
                             size=12, pad=10, fill="#fff8e7", stroke="#d48806", sw=1.8, bold=False)
    p.append(crit_box)

    render(os.path.join(OUT, 'barkhausen-loop.svg'), W, H, *p,
           title="Канонічна замкнена петля автогенератора та критерій Баркгаузена")


def fig_noise_to_sine_startup():
    """Еволюція сигналу в часі: шум -> наростання -> насичення -> стаціонарний режим."""
    W, H = 760, 360
    p = []

    ox, oy = 70, 200
    gw, gh = 640, 140

    # Осі
    p.append(line(ox, oy, ox + gw, oy, color=MUTED, sw=1.2, dash="3 3"))  # нульова лінія
    p.append(line(ox, oy + gh, ox + gw, oy + gh, color=INK, sw=1.8))      # вісь t
    p.append(line(ox, oy - gh, ox, oy + gh, color=INK, sw=1.8))           # вісь v(t)
    p.append(text(ox + gw - 10, oy + gh + 22, "Час t", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 8, oy - gh + 10, "v_вих(t)", size=12, color=INK, bold=True, anchor="end"))

    # Зони на графіку
    z1_end = ox + 140
    z2_end = ox + 380
    z3_end = ox + 520
    z4_end = ox + gw

    p.append(line(z1_end, oy - gh, z1_end, oy + gh, color=MUTED, sw=1, dash="4 4"))
    p.append(line(z2_end, oy - gh, z2_end, oy + gh, color=MUTED, sw=1, dash="4 4"))
    p.append(line(z3_end, oy - gh, z3_end, oy + gh, color=MUTED, sw=1, dash="4 4"))

    p.append(text((ox + z1_end) / 2, oy - gh + 18, "I. Тепловий шум", size=11, color=MUTED, bold=True))
    p.append(text((z1_end + z2_end) / 2, oy - gh + 18, "II. Наростання (e^(σ·t))", size=11, color=NEG, bold=True))
    p.append(text((z2_end + z3_end) / 2, oy - gh + 18, "III. Компресія", size=11, color=POS, bold=True))
    p.append(text((z3_end + z4_end) / 2, oy - gh + 18, "IV. Стаціонарний режим", size=11, color=FIELD, bold=True))

    # Обвідна наростання (пунктир)
    env_top = []
    env_bot = []

    # Генерація сигналу хвилі
    pts = []
    N = 400
    for i in range(N + 1):
        x = ox + (gw * i) / N

        if x < z1_end:
            # Зона 1: чистий мікрошум
            amp = 3.5
            val = amp * math.sin(i * 0.9) + 2.0 * math.cos(i * 1.7) - 1.5 * math.sin(i * 2.8)
        elif x < z2_end:
            # Зона 2: експоненційне наростання
            t_loc = (x - z1_end) / (z2_end - z1_end)
            amp = 4.0 * math.exp(2.8 * t_loc)
            val = amp * math.sin((x - ox) * 0.22)
            env_top.append((x, oy - amp))
            env_bot.append((x, oy + amp))
        elif x < z3_end:
            # Зона 3: нелінійне гальмування / насичення
            t_loc = (x - z2_end) / (z3_end - z2_end)
            amp = 65.0 + (100.0 - 65.0) * (1.0 - math.exp(-3.0 * t_loc))
            val = amp * math.sin((x - ox) * 0.22)
            env_top.append((x, oy - amp))
            env_bot.append((x, oy + amp))
        else:
            # Зона 4: стабільна амплітуда (граничний цикл)
            amp = 100.0
            val = amp * math.sin((x - ox) * 0.22)
            env_top.append((x, oy - amp))
            env_bot.append((x, oy + amp))

        y = oy - val
        pts.append((x, y))

    # Пунктирні лінії обвідної
    if env_top:
        d_top = "M" + " L".join("%.1f %.1f" % q for q in env_top)
        d_bot = "M" + " L".join("%.1f %.1f" % q for q in env_bot)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>' % (d_top, POS))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>' % (d_bot, POS))

    # Синусоїда
    d_wave = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_wave, NEG))

    # Рейки насичення
    p.append(line(z2_end, oy - 100, z4_end, oy - 100, color=POS, sw=1.5, dash="5 4"))
    p.append(line(z2_end, oy + 100, z4_end, oy + 100, color=POS, sw=1.5, dash="5 4"))
    p.append(text(z4_end - 10, oy - 106, "+V_нас (або поріг АРП)", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(z4_end - 10, oy + 118, "−V_нас", size=11, color=POS, bold=True, anchor="end"))

    render(os.path.join(OUT, 'noise-to-sine-startup.svg'), W, H, *p,
           title="Еволюція коливань автогенератора від теплового шуму до стабільного синуса")


def fig_root_locus_poles():
    """Комплексна s-площина (σ, jω) з траєкторією полюсів замкненої системи."""
    W, H = 760, 420
    p = []

    cx, cy = 340, 210
    gw, gh = 280, 180

    # Фон півплощин
    p.append(rect(cx - gw, cy - gh, gw, 2 * gh, fill="#f4f7fb", stroke="none"))  # Ліва (стійка)
    p.append(rect(cx, cy - gh, gw, 2 * gh, fill="#fdf6f5", stroke="none"))        # Права (нестійка/генерація)

    # Осі s-площини
    p.append(line(cx - gw, cy, cx + gw, cy, color=INK, sw=1.8))  # Вісь σ (Real)
    p.append(line(cx, cy - gh, cx, cy + gh, color=INK, sw=2.2))  # Вісь jω (Imag)

    p.append(text(cx + gw - 10, cy - 10, "Дійсна вісь σ (Re)", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(cx + 10, cy - gh + 18, "Уявна вісь jω (Im)", size=12, color=INK, bold=True, anchor="start"))

    # Позначки площин
    p.append(text(cx - gw / 2, cy - gh + 25, "Ліва півплощина (LHP, σ < 0)\nЗатухаючі коливання",
                  size=12, color=NEG, bold=True))
    p.append(text(cx + gw / 2, cy - gh + 25, "Права півплощина (RHP, σ > 0)\nЕкспоненційне самозбудження",
                  size=12, color=POS, bold=True))

    # Полюси на етапі запуску (RHP, σ > 0)
    w0_px = 100
    sigma_start = 120
    p1_x, p1_y = cx + sigma_start, cy - w0_px
    p2_x, p2_y = cx + sigma_start, cy + w0_px

    # Хрестики полюсів запуску
    def draw_pole(x, y, col, lbl, anchor="start", dx=10):
        sz = 7
        out = []
        out.append(line(x - sz, y - sz, x + sz, y + sz, color=col, sw=2.6))
        out.append(line(x - sz, y + sz, x + sz, y - sz, color=col, sw=2.6))
        if lbl:
            out.append(text(x + dx, y - 6, lbl, size=11, color=col, bold=True, anchor=anchor))
        return "".join(out)

    p.append(draw_pole(p1_x, p1_y, POS, "s₁,₂ запуску (σ > 0)\n|A·β| > 1"))
    p.append(draw_pole(p2_x, p2_y, POS, ""))

    # Полюси в усталеному режимі (jω вісь, σ = 0)
    ss_x1, ss_y1 = cx, cy - w0_px
    ss_x2, ss_y2 = cx, cy + w0_px

    p.append(draw_pole(ss_x1, ss_y1, FIELD, "s₁,₂ стаціонарні (σ = 0)\n|A_eff · β| = 1", anchor="end", dx=-12))
    p.append(draw_pole(ss_x2, ss_y2, FIELD, ""))

    # Траєкторія руху полюсів (стрілки з RHP на jω)
    p.append(arrow(p1_x - 12, p1_y, ss_x1 + 10, ss_y1, color=POS, sw=2.2))
    p.append(arrow(p2_x - 12, p2_y, ss_x2 + 10, ss_y2, color=POS, sw=2.2))
    p.append(text((p1_x + ss_x1) / 2, p1_y - 14, "Стиснення підсилення зі зростанням V_вих", size=11, color=POS, italic=True))

    # Позначки частоти ±jω₀
    p.append(text(cx + 8, cy - w0_px + 4, "+jω₀", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 8, cy + w0_px + 4, "−jω₀", size=12, color=FIELD, bold=True, anchor="start"))

    # Пояснювальний блок унизу
    info_box, _, _ = textbox(W / 2, cy + gh + 15,
                             "При увімкненні: |A·β| > 1 → полюси в RHP (амплітуда росте як e^(σ·t)).\n"
                             "При стабілізації: нелінійність знижує підсилення до |A_eff·β| = 1 → полюси сідають на вісь jω.",
                             size=12, pad=10, fill="#fffbe6", stroke="#d48806", sw=1.5)
    p.append(info_box)

    render(os.path.join(OUT, 'root-locus-poles.svg'), W, H, *p,
           title="Траєкторія полюсів автогенератора на комплексній s-площині")


def fig_amplitude_stabilization():
    """Порівняння двох підходів до стабілізації: жорстке насичення проти плавної АРП / лампи."""
    W, H = 760, 420
    p = []

    # Ліва колонка: жорстке обмеження (насичення)
    col1_cx = 200
    p.append(rect(30, 20, 330, 380, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    p.append(text(col1_cx, 48, "1. Насичення транзистора / ОП", size=14, color=POS, bold=True))
    p.append(text(col1_cx, 68, "(Природне амплітудне обмеження)", size=11, color=MUTED))

    # Графік насичення V_out від V_in
    gx1, gy1 = 110, 95
    p.append(line(gx1, gy1 + 50, gx1 + 180, gy1 + 50, color=INK, sw=1.2))  # вісь x
    p.append(line(gx1 + 90, gy1, gx1 + 90, gy1 + 100, color=INK, sw=1.2))  # вісь y

    # Крива обмеження
    p.append('<path d="M %d %d L %d %d Q %d %d %d %d L %d %d Q %d %d %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (gx1 + 10, gy1 + 90, gx1 + 45, gy1 + 90, gx1 + 65, gy1 + 85, gx1 + 80, gy1 + 60,
              gx1 + 100, gy1 + 40, gx1 + 115, gy1 + 15, gx1 + 135, gy1 + 10, gx1 + 170, gy1 + 10, POS))

    p.append(text(gx1 + 90, gy1 + 118, "Характеристика передачі (кліпінг)", size=11, color=INK))

    b_sat, _, _ = textbox(col1_cx, 305,
                          "• Підсилення падає через зрізання верхівок\n"
                          "• Проста схема без додаткових компонентів\n"
                          "• Високий рівень спотворень (THD 3–15%)\n"
                          "• Багатий спектр паразитних гармонік",
                          size=11, pad=10, fill="#ffffff", stroke=POS, sw=1, color=INK)
    p.append(b_sat)

    # Права колонка: плавна стабілізація (лампа / АРП на JFET)
    col2_cx = 560
    p.append(rect(390, 20, 340, 380, fill="#f4fbf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(col2_cx, 48, "2. Активна АРП / Лампа розжарення", size=14, color=FIELD, bold=True))
    p.append(text(col2_cx, 68, "(Параметричне регулювання підсилення)", size=11, color=MUTED))

    # Схема ділителя в ООС з регульованим елементом
    gx2, gy2 = 470, 95
    p.append(rect(gx2, gy2, 180, 80, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(gx2 + 90, gy2 + 25, "Петля від'ємного ЗЗ", size=12, color=FIELD, bold=True))
    p.append(text(gx2 + 90, gy2 + 48, "R_зз(V_rms) або r_ds(U_з)", size=12, color=INK))
    p.append(text(gx2 + 90, gy2 + 68, "A = 1 + R2 / R_керов", size=11, color=MUTED, italic=True))

    b_agc, _, _ = textbox(col2_cx, 305,
                          "• Підсилювач працює в лінійному режимі\n"
                          "• Опір підлаштовується середнім розмахом\n"
                          "• Наднизькі спотворення (THD < 0.05%)\n"
                          "• Ідеально чиста вихідна синусоїда",
                          size=11, pad=10, fill="#ffffff", stroke=FIELD, sw=1, color=INK)
    p.append(b_agc)

    render(os.path.join(OUT, 'amplitude-stabilization.svg'), W, H, *p,
           title="Порівняння методів стабілізації амплітуди автогенератора")


def fig_oscillator_topologies():
    """Порівняльна матриця 4 базових топологій автогенераторів."""
    W, H = 760, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    p.append(text(W / 2, 36, "Класичні топології гармонійних автогенераторів", size=16, color=INK, bold=True))

    # 4 блоки сітки 2x2
    bw, bh = 345, 160
    xs = [30, 390]
    ys = [60, 235]

    cards = [
        ("Міст Віна (Wien Bridge)",
         "• Ланка: RC-міст (смуговий фільтр)\n"
         "• Фаза ланки: φ_β(ω₀) = 0° (синфазно)\n"
         "• Коефіцієнт передачі: β(ω₀) = 1/3\n"
         "• Підсилювач: неінвертуючий, A = +3\n"
         "• Застосування: звукові генератори (10 Гц – 1 МГц)",
         "#eef5fc", NEG),

        ("Фазозсувний RC-генератор",
         "• Ланка: 3 послідовні RC-ланцюжки\n"
         "• Фаза ланки: φ_β(ω₀) = 180° (60° на ланку)\n"
         "• Коефіцієнт передачі: β(ω₀) = 1/29\n"
         "• Підсилювач: інвертуючий, A = −29 (180°)\n"
         "• Застосування: прості низькочастотні схеми",
         "#fdf7ee", "#d48806"),

        ("Генератор Колпітца (Ємнісна триточка)",
         "• Ланка: LC-контур + ємнісний дільник C1/C2\n"
         "• Фаза ланки: φ_β(ω₀) = 180°\n"
         "• Коефіцієнт передачі: β = C1 / (C1 + C2)\n"
         "• Підсилювач: інвертуючий каскад (180°)\n"
         "• Застосування: радіочастоти (100 кГц – 500 МГц)",
         "#eef8f2", FIELD),

        ("Генератор Хартлі (Індуктивна триточка)",
         "• Ланка: LC-контур + котушка з відведенням L1/L2\n"
         "• Фаза ланки: φ_β(ω₀) = 180°\n"
         "• Коефіцієнт передачі: β = L1 / (L1 + L2 + 2M)\n"
         "• Підсилювач: інвертуючий каскад (180°)\n"
         "• Застосування: радіодіапазони з плавним налаштуванням",
         "#fdf4f8", "#a82470")
    ]

    idx = 0
    for row in range(2):
        for col in range(2):
            bx, by = xs[col], ys[row]
            title_text, desc_text, bg_col, stroke_col = cards[idx]
            p.append(rect(bx, by, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
            p.append(text(bx + 16, by + 26, title_text, size=13, color=stroke_col, bold=True, anchor="start"))
            p.append(line(bx + 14, by + 36, bx + bw - 14, by + 36, color=stroke_col, sw=1, dash="3 3"))

            lines = desc_text.split("\n")
            for li, line_str in enumerate(lines):
                p.append(text(bx + 16, by + 56 + li * 20, line_str, size=11, color=INK, anchor="start"))
            idx += 1

    render(os.path.join(OUT, 'oscillator-topologies.svg'), W, H, *p,
           title="Порівняння класичних топологій гармонійних автогенераторів")


if __name__ == '__main__':
    fig_barkhausen_loop()
    fig_noise_to_sine_startup()
    fig_root_locus_poles()
    fig_amplitude_stabilization()
    fig_oscillator_topologies()
    print("Усі фігури успішно згенеровано.")
