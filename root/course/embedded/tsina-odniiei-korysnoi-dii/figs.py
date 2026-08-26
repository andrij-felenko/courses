# -*- coding: utf-8 -*-
"""Фігури до теми «Ціна однієї корисної дії: мілліджоулі на вимір і на пакет».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _shaded_rect(x, y, w, h, fill, stroke, op=0.30, sw=1.4, rx=4):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (x, y, w, h, rx, fill, op, stroke, sw))


# ── 1. Джоулі проти кулонів: струм, напруга та миттєва потужність ──────────────
def fig_joule_vs_coulomb():
    W, H = 820, 500
    f = [text(W / 2, 28,
              "Джоулі проти кулонів: чому облік лише за струмом спотворює баланс",
              size=15, bold=True)]

    col_w = 340
    top = 80
    oy = 340

    def draw_panel(px, title, regulator_type, note, is_buck=False):
        f.append(text(px + col_w / 2, top - 15, title, size=13, bold=True))
        ox = px + 40
        span_x = col_w - 60
        f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.3))
        f.append(line(ox, oy, ox, top + 15, color=MUTED, sw=1.3))
        f.append(text(ox + span_x, oy + 20, "розряд батареї (час) →", size=10, color=MUTED, anchor="end"))
        f.append(text(ox - 10, top + 20, "V, I, P", size=10.5, color=MUTED, anchor="end"))

        # Крива напруги V_bat(t) — спадає від 4.2 В до 3.0 В (синій)
        v_pts = []
        for i in range(0, int(span_x) + 1, 5):
            t = i / span_x
            v_val = 4.2 - 1.2 * t - 0.2 * (t ** 3)
            yy = oy - (v_val / 5.0) * (oy - top - 30)
            v_pts.append("%.1f,%.1f" % (ox + i, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(v_pts), NEG))
        f.append(text(ox + 45, oy - 195, "V_bat (падає)", size=10.5, color=NEG, bold=True))

        # Крива струму I_bat(t) (червоний)
        i_pts = []
        for i in range(0, int(span_x) + 1, 5):
            t = i / span_x
            if not is_buck:
                i_val = 2.0
            else:
                v_cur = 4.2 - 1.2 * t - 0.2 * (t ** 3)
                i_val = (3.3 * 2.0 / 0.90) / v_cur
            yy = oy - (i_val / 5.0) * (oy - top - 30)
            i_pts.append("%.1f,%.1f" % (ox + i, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="%s"/>'
                 % (" ".join(i_pts), POS, "none" if not is_buck else "5,3"))
        if not is_buck:
            f.append(text(ox + span_x - 10, oy - 80, "I_bat ≈ const (LDO)", size=10.5, color=POS, bold=True, anchor="end"))
        else:
            f.append(text(ox + span_x - 10, oy - 120, "I_bat РОСТЕ! (Buck)", size=10.5, color=POS, bold=True, anchor="end"))

        # Крива потужності P(t) = V(t) * I(t) (зелена лінія)
        p_pts = []
        for i in range(0, int(span_x) + 1, 5):
            t = i / span_x
            v_cur = 4.2 - 1.2 * t - 0.2 * (t ** 3)
            if not is_buck:
                p_val = v_cur * 2.0 / 4.0
            else:
                p_val = 7.33 / 4.0
            yy = oy - (p_val / 5.0) * (oy - top - 30)
            p_pts.append("%.1f,%.1f" % (ox + i, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(p_pts), FIELD))
        f.append(text(ox + 70, oy - 145 if not is_buck else oy - 150,
                      "P_bat = V·I", size=10.5, color=FIELD, bold=True))

        b, _, _ = textbox(px + col_w / 2, 400, note, size=10.5, pad=8,
                          fill="#f8f9fa", stroke=MUTED)
        f.append(b)

    draw_panel(40, "(а) Лінійний регулятор (LDO)", "LDO",
               "Q = ∫ I dt однаковий, але корисна\nенергія тане: різниця (V_bat - V_out)·I\nскидається LDO у чисте тепло.", is_buck=False)

    draw_panel(430, "(б) Імпульсний Buck (DC-DC)", "DC-DC",
               "P_навантаження = const → при розряді\nструм від батареї зростає! Рахувати\nлише за початковим I_bat — фатальна похибка.", is_buck=True)

    b, _, _ = textbox(W / 2, 470,
                      "Справжня вартість дії — не міліампер-секунди (Q), а джоулі: E = ∫ V(t)·I(t) dt. Тільки інтеграл потужності дає точний бюджет.",
                      size=11, fill="#eef4ff", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "joule-vs-coulomb.svg"), W, H, *f)


# ── 2. Енергетична анатомія пробудження мікроконтролера ───────────────────────
def fig_wakeup_energy_breakdown():
    W, H = 840, 480
    f = [text(W / 2, 28,
              "Анатомія пробудження: невидимі витрати енергії до першої інструкції",
              size=15, bold=True)]

    ox, oy = 80, 360
    span_x = 700
    top = 70

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 26, "час (мкс / мс) →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 65, top + 10, "струм (мА)", size=11, color=MUTED, anchor="start"))

    phases = [
        ("Глибокий сон\n(1-2 мкА)", 0.05, 60, NEG),
        ("Старт HSI\n(RC 2-5 мкс)", 4.0, 70, MUTED),
        ("Розгойдування кварцу HSE\n(кристал 0.8-2.5 мс)", 6.5, 180, POS),
        ("Синхронізація\nPLL (lock)", 14.0, 100, POS),
        ("Стабілізація\nVREF / Bandgap", 16.0, 90, FIELD),
        ("Виконання коду\n(CPU 80 МГц)", 24.0, 180, FIELD),
    ]

    def y_curr(ma):
        return oy - (ma / 28.0) * (oy - top)

    x = ox
    for i, (pname, ma, w, col) in enumerate(phases):
        ty = y_curr(ma)
        f.append(_shaded_rect(x, ty, w, oy - ty, col, col, op=0.25, sw=1.4))
        f.append(line(x, ty, x + w, ty, color=col, sw=2))
        f.append(mtext(x + w / 2, ty - 22 if ma > 10 else ty - 26, pname, size=10, bold=True, color=INK))
        x += w

    overhead_w = 70 + 180 + 100 + 90
    f.append(line(ox + 60, oy + 12, ox + 60 + overhead_w, oy + 12, color=POS, sw=1.8))
    f.append(line(ox + 60, oy + 8, ox + 60, oy + 16, color=POS, sw=1.8))
    f.append(line(ox + 60 + overhead_w, oy + 8, ox + 60 + overhead_w, oy + 16, color=POS, sw=1.8))
    f.append(text(ox + 60 + overhead_w / 2, oy + 30,
                  "Накладна енергія старту E_boot (50–250 мкДж без жодної корисної інструкції!)",
                  size=11, bold=True, color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, 445,
                      "Розгойдування кварцу (HSE) та захоплення PLL забирають до 80% енергії пробудження. Якщо замір швидкий — вигідніше працювати на швидкому RC (HSI).",
                      size=11, fill="#fdf0ef", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "wakeup-energy-breakdown.svg"), W, H, *f)


# ── 3. Енергетична декомпозиція радіопередачі ──────────────────────────────────
def fig_radio_packet_energy():
    W, H = 860, 500
    f = [text(W / 2, 28,
              "Анатомія радіопакета: куди йдуть міліджоулі від синтезатора до ACK",
              size=15, bold=True)]

    ox, oy = 70, 360
    span_x = 740
    top = 70

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 26, "час (мс) →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 55, top + 10, "струм (мА)", size=11, color=MUTED, anchor="start"))

    def y_rf(ma):
        import math
        return oy - (math.log10(ma + 1) / math.log10(121)) * (oy - top)

    rf_phases = [
        ("Підготовка\n(CRC, AES)", 8.0, 65, MUTED),
        ("RF PLL Lock\n(синтезатор)", 18.0, 75, POS),
        ("PA ramp", 38.0, 40, POS),
        ("TX On-Air: випромінювання\n(+14 dBm, 90 мА)", 95.0, 210, POS),
        ("RX turn", 16.0, 45, MUTED),
        ("RX Window\n(слухання ACK)", 22.0, 115, NEG),
        ("Прийом ACK\nкадру", 26.0, 65, FIELD),
        ("Сон", 0.02, 65, NEG),
    ]

    x = ox
    for pname, ma, w, col in rf_phases:
        ty = y_rf(ma)
        f.append(_shaded_rect(x, ty, w, oy - ty, col, col, op=0.28, sw=1.4))
        f.append(line(x, ty, x + w, ty, color=col, sw=2))
        f.append(mtext(x + w / 2, ty - 22 if ma > 20 else ty - 26, pname, size=9.5, bold=True, color=INK))
        x += w

    f.append(text(ox + 65 + 75 + 40 + 105, y_rf(95) + 35, "E_tx = V · I_tx · t_air",
                  size=11, bold=True, color=INK, anchor="middle"))
    f.append(text(ox + 65 + 75 + 40 + 210 + 45 + 57, y_rf(22) + 25, "E_rx (ACK)",
                  size=10.5, bold=True, color=INK, anchor="middle"))
    f.append(text(ox + 100, y_rf(18) + 30, "холостий хід PLL", size=9.5, color=POS, bold=True, anchor="middle"))

    b, _, _ = textbox(W / 2, 450,
                      "Прийом ACK та стабілізація синтезатора можуть коштувати до 40% енергії сесії. Збільшення бітрейту (наприклад, BLE 2M замість 1M) скорочує t_air удвічі.",
                      size=11, fill="#eef4ff", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "radio-packet-energy-breakdown.svg"), W, H, *f)


# ── 4. Зчитування давача: Polling проти Sleep-on-Exit проти DMA ───────────────
def fig_sensor_read_energy():
    W, H = 820, 480
    f = [text(W / 2, 28,
              "Ціна зчитування давача: блокуючий цикл проти DMA та сну ядра",
              size=15, bold=True)]

    def draw_scenario(py, title, phases, total_energy_label, col_box):
        f.append(text(60, py - 12, title, size=12, bold=True, anchor="start"))
        x = 60
        for name, ma, w, col in phases:
            f.append(_shaded_rect(x, py, w, 32, col, col, op=0.30, sw=1.3))
            f.append(text(x + w / 2, py + 20, name, size=9.5, bold=True, color=INK))
            x += w
        b, _, _ = textbox(700, py + 16, total_energy_label, size=11, pad=6,
                          fill=col_box, stroke=LINE, bold=True)
        f.append(b)

    draw_scenario(80, "(а) Блокуючий полінг CPU: while(!I2C_Ready) на 80 МГц",
                  [("Старт", 15, 45, MUTED),
                   ("CPU Active Polling I2C (15 мА)", 15, 340, POS),
                   ("Обробка", 15, 60, MUTED)],
                  "E = 22.5 мкДж (100%)", "#fdf0ef")

    draw_scenario(190, "(б) Переривання + WFI сон ядра під час очікування шини",
                  [("Старт", 15, 35, MUTED),
                   ("WFI сон", 1.8, 110, FIELD),
                   ("ISR", 15, 20, MUTED),
                   ("WFI сон", 1.8, 110, FIELD),
                   ("ISR", 15, 20, MUTED),
                   ("WFI сон", 1.8, 110, FIELD),
                   ("Обробка", 15, 40, MUTED)],
                  "E = 6.8 мкДж (-70%)", "#eef4ff")

    draw_scenario(300, "(в) Автономний DMA потік: ядро в глибокому сні",
                  [("Тригер", 15, 25, MUTED),
                   ("DMA апаратне перенесення в RAM (ядро спить у Stop/Sleep)", 0.6, 380, FIELD),
                   ("Wakeup", 15, 40, FIELD)],
                  "E = 1.9 мкДж (-91%)", "#eafaf1")

    b, _, _ = textbox(W / 2, 420,
                      "Очікування повільної периферії (I2C 100 кГц, прогрів АЦП) у циклі CPU спалює до 90% енергії давача. DMA та сон ядра опускають ціну до фізичного мінімуму.",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "sensor-read-energy.svg"), W, H, *f)


# ── 5. Методики вимірювання: шунт проти автодіапазонного профілювальника ──────
def fig_current_measurement_schemes():
    W, H = 840, 500
    f = [text(W / 2, 28,
              "Апаратні схеми вимірювання: проблема падіння тягаря (Burden Voltage)",
              size=15, bold=True)]

    col_w = 360
    top = 75

    def draw_left():
        px = 40
        f.append(text(px + col_w / 2, top + 10, "(а) Фіксований шунт + осцилограф", size=13, bold=True))

        f.append(_shaded_rect(px + 20, top + 45, 65, 50, NEG, NEG, op=0.15))
        f.append(mtext(px + 52, top + 70, "Батарея\n3.3 В", size=10, bold=True))

        f.append(line(px + 85, top + 70, px + 140, top + 70, color=LINE, sw=1.8))

        f.append(_shaded_rect(px + 140, top + 55, 60, 30, POS, POS, op=0.25))
        f.append(mtext(px + 170, top + 72, "R_sense\n10 Ом", size=9.5, bold=True))

        f.append(line(px + 200, top + 70, px + 250, top + 70, color=LINE, sw=1.8))

        f.append(_shaded_rect(px + 250, top + 45, 75, 50, FIELD, FIELD, op=0.20))
        f.append(mtext(px + 287, top + 70, "MCU\n(Навантаж.)", size=10, bold=True))

        f.append(line(px + 140, top + 55, px + 140, top + 30, color=MUTED, sw=1.2, dash="3,2"))
        f.append(line(px + 200, top + 55, px + 200, top + 30, color=MUTED, sw=1.2, dash="3,2"))
        f.append(line(px + 140, top + 30, px + 200, top + 30, color=MUTED, sw=1.2))
        f.append(text(px + 170, top + 22, "V_drop на осцилограф", size=9.5, color=MUTED))

        b1, _, _ = textbox(px + col_w / 2, top + 155,
                           "Пастка Burden Voltage:\n• При сні (1 мкА): V_drop = 10 мкВ (шум осцилографа!)\n• При TX (100 мА): V_drop = 1.0 В!\n  Напруга MCU падає з 3.3 В до 2.3 В → Brown-Out Reset!",
                           size=10, pad=8, fill="#fdf0ef", stroke=POS)
        f.append(b1)

    def draw_right():
        px = 430
        f.append(text(px + col_w / 2, top + 10, "(б) Профілювальник з авто-шунтами (PPK2)", size=13, bold=True))

        f.append(_shaded_rect(px + 20, top + 45, 60, 50, NEG, NEG, op=0.15))
        f.append(mtext(px + 50, top + 70, "Джерело\nживлення", size=10, bold=True))

        f.append(_shaded_rect(px + 115, top + 35, 130, 75, FIELD, FIELD, op=0.15, sw=1.6))
        f.append(text(px + 180, top + 52, "Auto-Ranging Shunts", size=10, bold=True))

        f.append(_shaded_rect(px + 125, top + 62, 54, 22, MUTED, MUTED, op=0.2))
        f.append(text(px + 152, top + 77, "0.05 Ом", size=9.5, bold=True))
        f.append(_shaded_rect(px + 185, top + 62, 54, 22, POS, POS, op=0.2))
        f.append(text(px + 212, top + 77, "47 Ом", size=9.5, bold=True))
        f.append(text(px + 180, top + 100, "Швидкий FET-bypass < 1 мкс", size=9.5, color=MUTED))

        f.append(line(px + 245, top + 70, px + 275, top + 70, color=LINE, sw=1.8))
        f.append(_shaded_rect(px + 275, top + 45, 65, 50, FIELD, FIELD, op=0.20))
        f.append(mtext(px + 307, top + 70, "MCU\n(DUT)", size=10, bold=True))

        b2, _, _ = textbox(px + col_w / 2, top + 155,
                           "Динамічне перемикання діапазонів:\n• 100 нА..500 мА безперервно (6 порядків!)\n• Падіння напруги компенсується зворотним зв'язком\n• Одночасне оцифрування V(t) та I(t) → інтеграл Джоулів",
                           size=10, pad=8, fill="#eafaf1", stroke=FIELD)
        f.append(b2)

    draw_left()
    draw_right()

    b_bot, _, _ = textbox(W / 2, 420,
                          "Звичайний шунт не здатен одночасно охопити струм глибокого сну (мкА) та імпульс передавача (сотні мА). Для чесного аудиту використовують спеціалізовані цифрові вимірювачі потужності (PPK2, Joulescope, Otii).",
                          size=11, fill="#eef4ff", stroke=NEG)
    f.append(b_bot)

    render(os.path.join(IMG, "current-measurement-schemes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_joule_vs_coulomb()
    fig_wakeup_energy_breakdown()
    fig_radio_packet_energy()
    fig_sensor_read_energy()
    fig_current_measurement_schemes()
    print("OK: 5 figures generated in", IMG)
