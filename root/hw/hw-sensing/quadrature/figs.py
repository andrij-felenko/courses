# -*- coding: utf-8 -*-
"""Фігури до теми «Квадратура».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Фізика формування квадратурного сигналу: Оптика та Магнетизм ──────────
def fig_generation():
    W, H = 820, 480
    f = [text(W / 2, 26, "Фізичне формування квадратурного сигналу: фазовий зсув 90° e", size=15, bold=True)]

    # --- Лівий блок: Оптичний растровий диск ---
    box_opt, bw, bh = textbox(210, 56, "Оптичний растровий диск (зсув маски на p/4)", size=11, bold=True, fill="#f0f4fa", stroke=NEG)
    f.append(box_opt)

    cx_opt, cy_opt = 110, 160
    # Диск
    f.append(circle(cx_opt, cy_opt, 62, fill="#ffffff", stroke=INK, sw=1.5))
    f.append(circle(cx_opt, cy_opt, 40, fill="#f8fafc", stroke=MUTED, sw=1.0))
    # Сектори щілин
    n_sl = 16
    for i in range(n_sl):
        if i % 2 == 0:
            continue
        a0 = math.radians(i * 360.0 / n_sl)
        a1 = math.radians((i + 1) * 360.0 / n_sl)
        x0o, y0o = cx_opt + 62 * math.cos(a0), cy_opt + 62 * math.sin(a0)
        x1o, y1o = cx_opt + 62 * math.cos(a1), cy_opt + 62 * math.sin(a1)
        x1i, y1i = cx_opt + 40 * math.cos(a1), cy_opt + 40 * math.sin(a1)
        x0i, y0i = cx_opt + 40 * math.cos(a0), cy_opt + 40 * math.sin(a0)
        d = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z"
             % (x0o, y0o, 62, 62, x1o, y1o, x1i, y1i, 40, 40, x0i, y0i))
        f.append('<path d="%s" fill="%s" stroke="none"/>' % (d, INK))
    f.append(circle(cx_opt, cy_opt, 12, fill="#cbd5e1", stroke=INK, sw=1.2))

    # Сенсори фотодіодів A і B
    box_pd_a, _, _ = textbox(250, 130, "Фотодіод A", size=10, fill="#e8f4fd", stroke=NEG, pad=6)
    box_pd_b, _, _ = textbox(250, 190, "Фотодіод B (зсув 90° e)", size=10, fill="#e8f4fd", stroke=NEG, pad=6)
    f.append(box_pd_a)
    f.append(box_pd_b)
    f.append(line(cx_opt + 48, cy_opt - 25, 195, 130, color=NEG, sw=1.2, dash="3 2"))
    f.append(line(cx_opt + 48, cy_opt + 25, 175, 190, color=NEG, sw=1.2, dash="3 2"))

    # --- Правий блок: Магнітне кільце з полюсами ---
    box_mag, _, _ = textbox(610, 56, "Магнітне кільце (N-S полюси, зсув Холла на λ/4)", size=11, bold=True, fill="#fdf2f2", stroke=POS)
    f.append(box_mag)

    cx_mag, cy_mag = 510, 160
    f.append(circle(cx_mag, cy_mag, 62, fill="#ffffff", stroke=INK, sw=1.5))
    f.append(circle(cx_mag, cy_mag, 40, fill="#f8fafc", stroke=MUTED, sw=1.0))
    n_poles = 8
    for i in range(n_poles):
        a0 = math.radians(i * 360.0 / n_poles)
        a1 = math.radians((i + 1) * 360.0 / n_poles)
        x0o, y0o = cx_mag + 62 * math.cos(a0), cy_mag + 62 * math.sin(a0)
        x1o, y1o = cx_mag + 62 * math.cos(a1), cy_mag + 62 * math.sin(a1)
        x1i, y1i = cx_mag + 40 * math.cos(a1), cy_mag + 40 * math.sin(a1)
        x0i, y0i = cx_mag + 40 * math.cos(a0), cy_mag + 40 * math.sin(a0)
        d = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z"
             % (x0o, y0o, 62, 62, x1o, y1o, x1i, y1i, 40, 40, x0i, y0i))
        col = "#ffcdd2" if (i % 2 == 0) else "#bbdefb"
        f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.8"/>' % (d, col, MUTED))
        am = (a0 + a1) / 2.0
        txt = "N" if (i % 2 == 0) else "S"
        tcol = POS if (i % 2 == 0) else NEG
        f.append(text(cx_mag + 51 * math.cos(am), cy_mag + 51 * math.sin(am) + 4, txt, size=9.5, color=tcol, bold=True))
    f.append(circle(cx_mag, cy_mag, 12, fill="#cbd5e1", stroke=INK, sw=1.2))

    box_h_a, _, _ = textbox(670, 130, "Датчик Холла A", size=10, fill="#fdf2f2", stroke=POS, pad=6)
    box_h_b, _, _ = textbox(670, 190, "Датчик Холла B (зсув 90° e)", size=10, fill="#fdf2f2", stroke=POS, pad=6)
    f.append(box_h_a)
    f.append(box_h_b)
    f.append(line(cx_mag + 48, cy_mag - 25, 605, 130, color=POS, sw=1.2, dash="3 2"))
    f.append(line(cx_mag + 48, cy_mag + 25, 575, 190, color=POS, sw=1.2, dash="3 2"))

    # --- Нижня частина: Часові діаграми каналів A і B ---
    sep_y = 240
    f.append(line(40, sep_y, W - 40, sep_y, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(W / 2, 260, "Прямокутні квадратурні сигнали (A випереджає B на 90° при прямому обертанні)", size=12.5, bold=True))

    # Вісь часу
    t_x0, t_x1 = 120, 720
    y_a, y_b = 310, 390
    amp = 30

    # Сітка квадрантів (кроків станів)
    step_w = 65
    f.append(text(70, y_a - 10, "Канал A", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(70, y_b - 10, "Канал B", size=12, color=POS, bold=True, anchor="start"))

    # Рівні: A: 0, 1, 1, 0, 0, 1, 1, 0
    #        B: 0, 0, 1, 1, 0, 0, 1, 1
    states = ["00", "01", "11", "10", "00", "01", "11", "10"]
    labels_a = [0, 1, 1, 0, 0, 1, 1, 0]
    labels_b = [0, 0, 1, 1, 0, 0, 1, 1]

    # Вертикальні роздільники станів
    for k in range(9):
        gx = t_x0 + k * step_w
        f.append(line(gx, y_a - amp - 10, gx, y_b + 20, color="#e2e8f0", sw=1.2))
        if k < 8:
            # підпис стану пари (A,B)
            f.append(text(gx + step_w / 2, y_b + 38, states[k], size=11, bold=True, color=INK))

    f.append(text(t_x0 - 15, y_b + 38, "Стан (AB):", size=10.5, bold=True, color=MUTED, anchor="end"))

    # Хвиля A
    pa = []
    curr_x = t_x0
    curr_y = y_a - labels_a[0] * amp
    pa.append("M %.1f %.1f" % (curr_x, curr_y))
    for k in range(8):
        ny = y_a - labels_a[k] * amp
        if ny != curr_y:
            pa.append("L %.1f %.1f" % (curr_x, ny))
            curr_y = ny
        curr_x += step_w
        pa.append("L %.1f %.1f" % (curr_x, curr_y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pa), NEG))

    # Хвиля B
    pb = []
    curr_x = t_x0
    curr_y = y_b - labels_b[0] * amp
    pb.append("M %.1f %.1f" % (curr_x, curr_y))
    for k in range(8):
        ny = y_b - labels_b[k] * amp
        if ny != curr_y:
            pb.append("L %.1f %.1f" % (curr_x, ny))
            curr_y = ny
        curr_x += step_w
        pb.append("L %.1f %.1f" % (curr_x, curr_y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pb), POS))

    # Позначення періоду 360° e та зсуву 90° e
    f.append(line(t_x0 + step_w, y_a - amp - 8, t_x0 + step_w * 2, y_a - amp - 8, color=INK, sw=1.2))
    f.append(line(t_x0 + step_w, y_a - amp - 13, t_x0 + step_w, y_a - amp - 3, color=INK, sw=1.2))
    f.append(line(t_x0 + step_w * 2, y_a - amp - 13, t_x0 + step_w * 2, y_a - amp - 3, color=INK, sw=1.2))
    f.append(text(t_x0 + step_w * 1.5, y_a - amp - 16, "90° e (чверть)", size=10, bold=True, color=INK))

    f.append(line(t_x0, y_b + 18, t_x0 + step_w * 4, y_b + 18, color=MUTED, sw=1.2))
    f.append(line(t_x0, y_b + 13, t_x0, y_b + 23, color=MUTED, sw=1.2))
    f.append(line(t_x0 + step_w * 4, y_b + 13, t_x0 + step_w * 4, y_b + 23, color=MUTED, sw=1.2))
    f.append(text(t_x0 + step_w * 2, y_b + 14, "Повний період сигналу 360° e (1 крок растра)", size=9.5, color=MUTED))

    render(os.path.join(IMG, "quadrature-generation.svg"), W, H, *f)


# ── 2. Діаграма станів і режими декодування (1X, 2X, 4X) ─────────────────────
def fig_states_modes():
    W, H = 820, 470
    f = [text(W / 2, 26, "Кільце станів FSM квадратури та кратність декодування (1X, 2X, 4X)", size=15, bold=True)]

    # --- Ліва частина: Граф станів FSM (Gray Code) ---
    cx, cy = 200, 230
    R = 95
    # Позиції 4 станів: 00 (верх), 01 (право), 11 (низ), 10 (ліво)
    pts = {
        "00": (cx, cy - R),
        "01": (cx + R, cy),
        "11": (cx, cy + R),
        "10": (cx - R, cy)
    }

    # Коло обходу CW
    f.append(text(cx, cy - 14, "Код Грея", size=12, bold=True, color=INK))
    f.append(text(cx, cy + 6, "CW: +1 крок", size=10.5, bold=True, color=FIELD))
    f.append(text(cx, cy + 22, "CCW: -1 крок", size=10.5, bold=True, color=POS))

    # Стрілки між сусідніми станами
    # 00 -> 01
    f.append(arrow(pts["00"][0] + 18, pts["00"][1] + 6, pts["01"][0] - 6, pts["01"][1] - 18, color=FIELD, sw=2.0))
    # 01 -> 11
    f.append(arrow(pts["01"][0] - 6, pts["01"][1] + 18, pts["11"][0] + 18, pts["11"][1] - 6, color=FIELD, sw=2.0))
    # 11 -> 10
    f.append(arrow(pts["11"][0] - 18, pts["11"][1] - 6, pts["10"][0] + 6, pts["10"][1] + 18, color=FIELD, sw=2.0))
    # 10 -> 00
    f.append(arrow(pts["10"][0] + 6, pts["10"][1] - 18, pts["00"][0] - 18, pts["00"][1] + 6, color=FIELD, sw=2.0))

    # Діагональні заборонені переходи (Червоний пунктир: 00 <-> 11 та 01 <-> 10)
    f.append(line(pts["00"][0], pts["00"][1] + 20, pts["11"][0], pts["11"][1] - 20, color=POS, sw=1.8, dash="4 3"))
    f.append(line(pts["10"][0] + 20, pts["10"][1], pts["01"][0] - 20, pts["01"][1], color=POS, sw=1.8, dash="4 3"))

    box_err1, _, _ = textbox(cx + 42, cy - 42, "ПОМИЛКА\n(пропуск)", size=9, fill="#fdf2f2", stroke=POS, pad=3)
    box_err2, _, _ = textbox(cx - 42, cy + 42, "ПОМИЛКА\n(пропуск)", size=9, fill="#fdf2f2", stroke=POS, pad=3)
    f.append(box_err1)
    f.append(box_err2)

    # Кружечки станів
    for st, (px, py) in pts.items():
        f.append(circle(px, py, 22, fill="#f0fdf4", stroke=FIELD, sw=2.0))
        f.append(text(px, py + 5, st, size=13, bold=True, color=INK))

    f.append(text(cx, cy + R + 44, "При валідному кроці змінюється рівно 1 біт", size=10.5, color=MUTED))

    # --- Права частина: Порівняння режимів 1X, 2X, 4X ---
    rx0, ry0 = 420, 75
    rw = 360
    f.append(text(rx0 + rw / 2, ry0 - 15, "Кратність підрахунку подій за один період (360° e)", size=12.5, bold=True))

    seg_w = rw / 4.0
    sig_y_a, sig_y_b = ry0 + 25, ry0 + 75
    f.append(text(rx0 - 10, sig_y_a - 5, "A", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(rx0 - 10, sig_y_b - 5, "B", size=11, bold=True, color=POS, anchor="end"))

    # Намалювати 1 період A і B
    f.append(line(rx0, sig_y_a, rx0 + seg_w, sig_y_a, color=NEG, sw=2.0))
    f.append(line(rx0 + seg_w, sig_y_a, rx0 + seg_w, sig_y_a - 20, color=NEG, sw=2.0))
    f.append(line(rx0 + seg_w, sig_y_a - 20, rx0 + seg_w * 3, sig_y_a - 20, color=NEG, sw=2.0))
    f.append(line(rx0 + seg_w * 3, sig_y_a - 20, rx0 + seg_w * 3, sig_y_a, color=NEG, sw=2.0))
    f.append(line(rx0 + seg_w * 3, sig_y_a, rx0 + rw, sig_y_a, color=NEG, sw=2.0))

    f.append(line(rx0, sig_y_b, rx0 + seg_w * 2, sig_y_b, color=POS, sw=2.0))
    f.append(line(rx0 + seg_w * 2, sig_y_b, rx0 + seg_w * 2, sig_y_b - 20, color=POS, sw=2.0))
    f.append(line(rx0 + seg_w * 2, sig_y_b - 20, rx0 + rw, sig_y_b - 20, color=POS, sw=2.0))

    # Пунктири подій фронтів
    edges = [seg_w, seg_w * 2, seg_w * 3, rw]
    for ex in edges:
        f.append(line(rx0 + ex, sig_y_a - 25, rx0 + ex, ry0 + 330, color="#e2e8f0", sw=1.0, dash="3 3"))

    # Режим 1X
    y_1x = ry0 + 135
    f.append(rect(rx0, y_1x - 18, rw, 50, fill="#f8fafc", stroke=MUTED, sw=1.0))
    f.append(text(rx0 + 10, y_1x, "Режим 1X (1 імпульс / період)", size=11, bold=True, anchor="start"))
    f.append(text(rx0 + 10, y_1x + 18, "Захоплення: лише передній фронт каналу A", size=9.5, color=MUTED, anchor="start"))
    f.append(circle(rx0 + seg_w, y_1x + 8, 5, fill=NEG, stroke=INK, sw=1.0))
    f.append(arrow(rx0 + seg_w, y_1x + 22, rx0 + seg_w, y_1x + 14, color=NEG, sw=1.8))

    # Режим 2X
    y_2x = ry0 + 200
    f.append(rect(rx0, y_2x - 18, rw, 50, fill="#f8fafc", stroke=MUTED, sw=1.0))
    f.append(text(rx0 + 10, y_2x, "Режим 2X (2 імпульси / період)", size=11, bold=True, anchor="start"))
    f.append(text(rx0 + 10, y_2x + 18, "Захоплення: обидва фронти (Rising + Falling) каналу A", size=9.5, color=MUTED, anchor="start"))
    f.append(circle(rx0 + seg_w, y_2x + 8, 5, fill=NEG, stroke=INK, sw=1.0))
    f.append(circle(rx0 + seg_w * 3, y_2x + 8, 5, fill=NEG, stroke=INK, sw=1.0))
    f.append(arrow(rx0 + seg_w, y_2x + 22, rx0 + seg_w, y_2x + 14, color=NEG, sw=1.8))
    f.append(arrow(rx0 + seg_w * 3, y_2x + 22, rx0 + seg_w * 3, y_2x + 14, color=NEG, sw=1.8))

    # Режим 4X
    y_4x = ry0 + 265
    f.append(rect(rx0, y_4x - 18, rw, 56, fill="#f0fdf4", stroke=FIELD, sw=1.5))
    f.append(text(rx0 + 10, y_4x, "Режим 4X (4 імпульси / період) — повне декодування", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(rx0 + 10, y_4x + 18, "Захоплення: усі фронти каналів A та B (учетверення CPR)", size=9.5, color=MUTED, anchor="start"))
    for ex in edges:
        f.append(circle(rx0 + ex, y_4x + 24, 5, fill=FIELD, stroke=INK, sw=1.0))
        f.append(arrow(rx0 + ex, y_4x + 36, rx0 + ex, y_4x + 30, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "quadrature-states-and-modes.svg"), W, H, *f)


# ── 3. Архітектура обробки: Фільтр → FSM LUT проти Апаратного QEI ───────────
def fig_pipeline():
    W, H = 820, 440
    f = [text(W / 2, 26, "Тракт обробки квадратури: від фізичного сигналу до лічильника", size=15, bold=True)]

    # 1. Вхідний фізичний рівень
    b_in, _, _ = textbox(110, 110, "Сенсор A, B\n(Оптика / Холл)", size=11, bold=True, fill="#f8fafc", stroke=INK, min_w=120)
    f.append(b_in)

    # 2. Диференційний приймач
    b_diff, _, _ = textbox(270, 110, "Диференційний приймач\nRS-422 (AM26LV32)\n+ Тригер Шмітта", size=10, fill="#f0f4fa", stroke=NEG, min_w=150)
    f.append(b_diff)
    f.append(arrow(170, 110, 195, 110, color=INK, sw=1.5))

    # Розгалуження на 2 шляхи: Програмний та Апаратний
    f.append(arrow(345, 110, 400, 110, color=INK, sw=1.5))

    # --- Верхня гілка: Програмний LUT декодер ---
    box_sw_head, _, _ = textbox(580, 70, "Програмне декодування (EXTI / Polling FSM)", size=11, bold=True, fill="#fefce8", stroke="#ca8a04")
    f.append(box_sw_head)

    b_deb, _, _ = textbox(470, 140, "Цифровий фільтр\n(Дебаунсинг 2-3 вибірки)", size=10, fill="#ffffff", stroke=MUTED, min_w=130)
    f.append(b_deb)
    f.append(line(370, 110, 370, 140, color=INK, sw=1.5))
    f.append(arrow(370, 140, 405, 140, color=INK, sw=1.5))

    b_lut, _, _ = textbox(630, 140, "Таблиця станів LUT[16]\nindex=(prev<<2)|curr\nΔpos ∈ {-1, 0, +1, ERR}", size=10, fill="#fefce8", stroke="#ca8a04", min_w=150)
    f.append(b_lut)
    f.append(arrow(535, 140, 555, 140, color=INK, sw=1.5))

    b_pos_sw, _, _ = textbox(760, 140, "Позиція\n+ Лічильник\nпомилок", size=10, bold=True, fill="#f0fdf4", stroke=FIELD, min_w=80)
    f.append(b_pos_sw)
    f.append(arrow(705, 140, 720, 140, color=INK, sw=1.5))

    # --- Нижня гілка: Апаратний таймер (QEI) ---
    box_hw_head, _, _ = textbox(580, 250, "Апаратний таймерний енкодер (Hardware QEI / TIMx Encoder Mode)", size=11, bold=True, fill="#f0fdf4", stroke=FIELD)
    f.append(box_hw_head)

    b_hw_flt, _, _ = textbox(470, 320, "Апаратний фільтр\n(TIMx_CCMR ICxF)", size=10, fill="#ffffff", stroke=MUTED, min_w=130)
    f.append(b_hw_flt)
    f.append(line(370, 110, 370, 320, color=INK, sw=1.5))
    f.append(arrow(370, 320, 405, 320, color=INK, sw=1.5))

    b_hw_qei, _, _ = textbox(630, 320, "Апаратна логіка декодування\n(Керування напрямом DIR\nта тактуванням лічильника)", size=10, fill="#f0fdf4", stroke=FIELD, min_w=150)
    f.append(b_hw_qei)
    f.append(arrow(535, 320, 555, 320, color=INK, sw=1.5))

    b_pos_hw, _, _ = textbox(760, 320, "Регістр CNT\n(0% CPU load,\nдо 20-50 МГц)", size=10, bold=True, fill="#f0fdf4", stroke=FIELD, min_w=80)
    f.append(b_pos_hw)
    f.append(arrow(705, 320, 720, 320, color=INK, sw=1.5))

    # Порівняльна плашка внизу
    b_cmp, _, _ = textbox(W / 2, 405, "Висновок: Програмний LUT — для низьких швидкостей та HMI (<5 кГц); Апаратний QEI — для сервоприводів та ЧПК (>100 кГц)", size=10.5, bold=True, fill="#f1f5f9", stroke=INK, min_w=740)
    f.append(b_cmp)

    render(os.path.join(IMG, "quadrature-decoder-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_generation()
    fig_states_modes()
    fig_pipeline()
    print("Згенеровано 3 фігури у", IMG)
