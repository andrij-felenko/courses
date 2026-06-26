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


if __name__ == "__main__":
    fig_duty_cycle_profile()
    fig_two_levers()
    print("OK: 2 figures ->", IMG)
