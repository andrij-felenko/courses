# -*- coding: utf-8 -*-
"""Фігури до теми «Цикл і середній струм».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _shaded_bar(x, w, base_y, top_y, fill, stroke):
    """Заштрихований прямокутник-фаза (заряд = площа): від базової лінії вгору."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
            'fill-opacity="0.30" stroke="%s" stroke-width="1.6"/>'
            % (x, top_y, w, base_y - top_y, fill, stroke))


# ── Анатомія циклу: профіль струму в часі, площа кожної фази = її заряд ───────
def fig_duty_cycle_profile():
    W, H = 760, 470
    f = [text(W / 2, 28,
              "Анатомія циклу: висота — струм, ширина — час, площа фази — її заряд",
              size=15, bold=True)]

    ox, oy = 80, 360                 # початок осей (низ-ліво)
    span_x = 600                     # вісь часу
    top = 70                         # верх осі струму
    # осі
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 26, "час →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 60, top + 6, "струм (мА)", size=11, color=MUTED, anchor="start"))

    # рівні струму (висоти від базової лінії), у px
    def y_of(ma):                    # 200 мА → майже верх; лог-подібне стиснення
        import math
        return oy - (math.log10(ma + 1) / math.log10(201)) * (oy - top)

    # фази: (підпис, струм_мА, ширина_px, колір)
    phases = [
        ("сон",   0.01, 70,  NEG),
        ("boot",  60,   60,  POS),
        ("вимір", 22,   38,  FIELD),
        ("TX",    185,  70,  POS),
        ("сон",   0.01, 290, NEG),
    ]
    x = ox
    for name, ma, w, col in phases:
        ty = y_of(ma)
        f.append(_shaded_bar(x, w, oy, ty, col, col))
        # підпис фази над стовпчиком (для сну — лише над першим вузьким)
        if name != "сон" or w < 100:
            f.append(text(x + w / 2, ty - 7, name, size=11, bold=True, color=INK))
        x += w

    # підпис довгого сну всередині останнього (широкого) блоку
    f.append(text(ox + span_x - 145, oy - 14, "глибокий сон (мкА)",
                  size=11, color=NEG, anchor="middle"))

    # пунктир середнього струму — помітно вище плато сну, нижче піків
    avg_y = y_of(0.35)
    f.append(line(ox, avg_y, ox + span_x, avg_y, color=INK, sw=1.6, dash="7,4"))
    f.append(text(ox + 6, avg_y - 6, "I_сер", size=11.5, bold=True,
                  color=INK, anchor="start"))

    # позначка періоду T під віссю
    f.append(line(ox, oy + 12, ox, oy + 18, color=MUTED, sw=1.2))
    f.append(line(ox + span_x, oy + 12, ox + span_x, oy + 18, color=MUTED, sw=1.2))
    f.append(line(ox, oy + 15, ox + span_x, oy + 15, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(ox + span_x / 2, oy + 44, "період циклу T",
                  size=11, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 446,
                      "TX короткий, але площа найбільша — висота × ширина; сон забирає час, не заряд. I_сер = сумарна площа / T",
                      size=11.5, fill="#eef4ff", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "duty-cycle-profile.svg"), W, H, *f)


# ── Два важелі: зрізати заряд активної фази або розтягнути період ─────────────
def fig_two_levers():
    W, H = 760, 470
    f = [text(W / 2, 28,
              "Два важелі середнього струму: менший заряд за цикл або довший період",
              size=15, bold=True)]

    import math

    def panel(px, title, active_w, period_w, tx_h_ma, sub):
        """Маленький профіль у колонці px..px+col_w."""
        col_w = 210
        oy = 300
        top = 92
        ox = px + 14
        span = col_w - 28
        f.append(text(px + col_w / 2, 58, title, size=12.5, bold=True))
        f.append(line(ox, oy, ox + span, oy, color=MUTED, sw=1.2))
        f.append(line(ox, oy, ox, top, color=MUTED, sw=1.2))

        def y_of(ma):
            return oy - (math.log10(ma + 1) / math.log10(201)) * (oy - top)

        # активна частина зліва (boot+вимір+TX злиті у два стовпчики), сон — решта
        # boot
        bw = active_w * 0.45
        f.append(_shaded_bar(ox, bw, oy, y_of(60), POS, POS))
        # TX (висота — параметр сценарію)
        txw = active_w * 0.55
        f.append(_shaded_bar(ox + bw, txw, oy, y_of(tx_h_ma), POS, POS))
        f.append(text(ox + bw + txw / 2, y_of(tx_h_ma) - 6, "акт.",
                      size=10, bold=True, color=INK))
        # сон
        f.append(_shaded_bar(ox + active_w, period_w - active_w, oy,
                             y_of(0.01), NEG, NEG))
        # межа періоду
        f.append(line(ox + period_w, oy + 8, ox + period_w, oy + 14,
                      color=MUTED, sw=1.2))
        f.append(text(ox + period_w / 2, oy + 30, sub, size=10.5,
                      color=MUTED, anchor="middle"))
        return oy, top, ox, span

    # (а) базовий
    panel(40,  "(а) базовий",            active_w=70, period_w=150, tx_h_ma=185,
          sub="T")
    # (б) коротша передача — менший заряд активної фази (нижчий TX, вужча активна)
    panel(275, "(б) коротша передача",   active_w=44, period_w=150, tx_h_ma=120,
          sub="той самий T")
    # (в) рідші прокидання — довший період (ширший сон)
    panel(510, "(в) рідші прокидання",   active_w=70, period_w=200, tx_h_ma=185,
          sub="довший T")

    # стрілки-висновки під кожною панеллю
    f.append(text(145, 350, "↓ менший заряд/цикл", size=10.5, bold=True,
                  color=FIELD, anchor="middle"))
    f.append(text(380, 350, "↓ заряд активної фази", size=10.5, bold=True,
                  color=FIELD, anchor="middle"))
    f.append(text(615, 350, "↑ період → ↓ I_сер", size=10.5, bold=True,
                  color=FIELD, anchor="middle"))

    b, _, _ = textbox(W / 2, 446,
                      "(б) зменшує чисельник — заряд за цикл; (в) збільшує знаменник — T. Обидва тиснуть I_сер униз різними важелями",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "two-levers.svg"), W, H, *f)


# ── Розклад середнього струму на постійне дно + амортизований фікс + змінне ────
def fig_fixed_variable():
    """Стовпчик I_сер розкладено на три внески; поряд — як кожен поводиться з T."""
    W, H = 780, 490
    f = [text(W / 2, 28,
              "Три внески в середній струм: дно сну, амортизований фікс, змінне",
              size=15, bold=True)]

    # --- лівий стовпчик-розклад ---
    bx, bw = 90, 120
    base_y, top_y = 380, 90
    total_px = base_y - top_y
    # частки (умовні, для метеостанції: сон ~4 %, фікс/boot ~70 %, змінне ~26 %)
    seg = [("дно сну\nI_сон", 0.06, NEG),
           ("амортизований\nфікс  Q_фікс/T", 0.68, POS),
           ("змінне\nf · q_роб", 0.26, FIELD)]
    y = base_y
    for name, frac, col in seg:
        h = total_px * frac
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                 'fill-opacity="0.28" stroke="%s" stroke-width="1.6"/>'
                 % (bx, y - h, bw, h, col, col))
        f.append(mtext(bx + bw / 2, y - h / 2 - 6, name, size=10.5, bold=True, color=INK))
        y -= h
    f.append(text(bx + bw / 2, base_y + 20, "I_сер", size=12.5, bold=True))
    f.append(line(bx - 10, base_y, bx + bw + 10, base_y, color=MUTED, sw=1.2))

    # --- права панель: поведінка з періодом T ---
    ox, oy = 340, 380
    span_x, top = 380, 90
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 22, "період T →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + 4, top - 6, "внесок у I_сер", size=11, color=MUTED, anchor="start"))

    import math
    # дно сну — горизонталь
    sleep_y = oy - 0.10 * (oy - top)
    f.append(line(ox, sleep_y, ox + span_x, sleep_y, color=NEG, sw=2))
    f.append(text(ox + span_x - 4, sleep_y - 6, "I_сон — стала", size=10.5,
                  color=NEG, anchor="end"))
    # амортизований фікс — гіпербола Q/T, спадає до нуля
    pts = []
    for i in range(0, span_x + 1, 6):
        t = 0.12 + (i / span_x) * 3.0            # T у відн. одиницях
        val = 0.80 / t                            # Q_фікс/T
        yy = oy - min(val, 0.86) * (oy - top)
        pts.append("%.1f,%.1f" % (ox + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), POS))
    f.append(text(ox + 120, top + 30, "Q_фікс/T — спадає як 1/T", size=10.5,
                  color=POS, anchor="start", bold=True))
    # змінне — стала висота (не залежить від T)
    var_y = oy - 0.30 * (oy - top)
    f.append(line(ox, var_y, ox + span_x, var_y, color=FIELD, sw=2, dash="6,4"))
    f.append(text(ox + span_x - 4, var_y - 6, "f·q_роб — стала", size=10.5,
                  color=FIELD, anchor="end"))

    b, _, _ = textbox(W / 2, 466,
                      "Розтягуєш T — тане лише амортизований фікс (1/T); дно сну й змінне стоять. Звідси й дно кривої життя",
                      size=11, fill="#eef4ff", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "fixed-variable.svg"), W, H, *f)


# ── Крива віддачі: час життя проти періоду, з коліном насичення ───────────────
def fig_returns_knee():
    W, H = 760, 470
    f = [text(W / 2, 28,
              "Спадна віддача: час життя росте з періодом, тоді впирається в дно",
              size=15, bold=True)]
    import math
    ox, oy = 80, 370
    span_x, top = 610, 80
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 24, "період циклу T →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 2, top - 8, "час життя", size=11, color=MUTED, anchor="start"))

    # життя = k / I_сер, I_сер = I_сон + Q_фікс/T  → життя росте, насичується на k/I_сон
    Isleep, Qfix = 0.10, 0.40
    tmin, tmax = 0.05, 8.0
    def life(t):
        return 1.0 / (Isleep + Qfix / t)
    Lmax = 1.0 / Isleep
    ymax_frac = 0.92                      # верхівка кривої трохи нижче за верх осі
    pts = []
    for i in range(0, span_x + 1, 5):
        t = tmin + (i / span_x) * (tmax - tmin)
        val = life(t) / Lmax
        yy = oy - val * ymax_frac * (oy - top)
        pts.append("%.1f,%.1f" % (ox + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))

    # асимптота — стеля k/I_сон (дно струму = сон)
    ceil_y = oy - ymax_frac * (oy - top)
    f.append(line(ox, ceil_y, ox + span_x, ceil_y, color=NEG, sw=1.6, dash="7,4"))
    f.append(text(ox + span_x - 4, ceil_y - 7,
                  "стеля: усе дно = сам сон (Q_фікс/T → 0)", size=10.5,
                  color=NEG, anchor="end"))

    # «коліно» — позначка де крутість різко падає (тут Q_фікс/T ≈ I_сон)
    tk = Qfix / Isleep                    # T, де амортизований фікс зрівнявся зі сном
    ik = ox + (tk - tmin) / (tmax - tmin) * span_x
    yk = oy - life(tk) / Lmax * ymax_frac * (oy - top)
    f.append(circle(ik, yk, 5, fill="#fff", stroke=INK, sw=2))
    f.append(text(ik + 12, yk + 20, "коліно: далі майже дарма", size=10.5,
                  bold=True, color=INK, anchor="start"))
    # ліва крута ділянка
    f.append(mtext(ox + 118, oy - 96,
                   ["крутий приріст:", "кожне подвоєння T", "майже подвоює життя"],
                   size=10, color=FIELD, anchor="middle"))

    b, _, _ = textbox(W / 2, 446,
                      "Поки фікс домінує (T мале), життя ~ T; коли фікс/T падає під I_сон, крива лягає — знаменник більше не зменшити періодом",
                      size=10.5, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "returns-knee.svg"), W, H, *f)


# ── Батчинг: один boot на N замірів проти N окремих boot ──────────────────────
def fig_batching():
    W, H = 770, 430
    f = [text(W / 2, 28,
              "Батчинг: один дорогий старт ділиться на N корисних замірів",
              size=15, bold=True)]

    def strip(px, py, title, boots, meas_per_boot, note):
        """Смуга подій: boot (широкий червоний) + заміри (вузькі зелені)."""
        f.append(text(px, py - 26, title, size=12.5, bold=True, anchor="start"))
        x = px
        unit = 26
        for _b in range(boots):
            # boot-блок
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="26" fill="%s" '
                     'fill-opacity="0.30" stroke="%s" stroke-width="1.4"/>'
                     % (x, py, unit * 1.6, POS, POS))
            f.append(text(x + unit * 0.8, py + 17, "boot", size=9.5, bold=True,
                          color=INK))
            x += unit * 1.6 + 4
            for _m in range(meas_per_boot):
                f.append('<rect x="%.1f" y="%.1f" width="14" height="26" fill="%s" '
                         'fill-opacity="0.35" stroke="%s" stroke-width="1.2"/>'
                         % (x, py, FIELD, FIELD))
                x += 16
            x += 10
        f.append(text(px, py + 48, note, size=10.5, color=MUTED, anchor="start"))
        return x

    strip(60, 90, "(а) без батчингу: boot на кожен замір",
          boots=4, meas_per_boot=1,
          note="4 замори → 4 дорогі старти; фікс платиться 4 рази")
    strip(60, 210, "(б) батчинг: один boot на 4 замори",
          boots=1, meas_per_boot=4,
          note="4 замори → 1 старт; фікс поділено на 4 (амортизація)")

    # формула-висновок
    f.append(text(60, 310,
                  "заряд на корисний замір  =  Q_фікс / N  +  q_замір", size=12,
                  bold=True, color=INK, anchor="start"))
    f.append(text(60, 334,
                  "N ↑  →  частка старту на замір падає як 1/N  →  дно = сам q_замір",
                  size=10.5, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 400,
                      "Батчинг не прибирає дорогий старт — він ділить його на N замірів; платня — свіжість (заміри лежать до спільної передачі)",
                      size=10.5, fill="#fdf0ef", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "batching.svg"), W, H, *f)


if __name__ == "__main__":
    fig_duty_cycle_profile()
    fig_two_levers()
    fig_fixed_variable()
    fig_returns_knee()
    fig_batching()
    print("OK: 5 figures ->", IMG)
