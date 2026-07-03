# -*- coding: utf-8 -*-
"""Фігури до статті «Dead-time у напівмості» (book/electronics/power-electronics/dead-time):
  - overlap.svg    — чому кінцевий час вимкнення дає вікно перекриття (наскрізний струм)
  - polarity.svg   — куди тягне вихід у паузі: знак струму навантаження задає похибку напруги
  - corridor.svg   — вузький коридор: замало → пробій, забагато → втрати й спотворення
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── фіг. 1. Вікно перекриття: кінцевий час вимкнення ──────────────────────────
def fig_overlap():
    W, H = 780, 430
    f = [text(W / 2, 28, "Чому потрібна пауза: ключ закривається не миттєво", size=16, bold=True)]

    # три часові доріжки: команда, стан нижнього, стан верхнього
    x0, x1 = 230, 730        # межі осі часу (лишаємо ліворуч місце під підписи доріжок)
    tsw = 380                # момент команди «перекинути плече»
    trow = [120, 215, 310]   # y базових ліній трьох доріжок
    labels = ["команда ШІМ", "нижній ключ", "верхній ключ"]
    for y, lab in zip(trow, labels):
        f.append(line(x0, y, x1, y, color="#d9dee4", sw=1.0))        # ледь помітна база доріжки
        f.append(text(x0 - 16, y + 4, lab, size=12, anchor="end", bold=True))

    hi = 34   # висота логічного рівня

    # НЕБЕЗПЕЧНЕ вікно перекриття (малюємо ПЕРШИМ, як фон-смугу — без бічних ліній)
    rise_end = tsw + 46          # верхній піднявся
    fall_end = tsw + 96          # нижній догас
    ov0, ov1 = rise_end - 12, fall_end - 10
    f.append(rect(ov0, 98, ov1 - ov0, 236, fill="#fdecea", stroke="none", sw=0, rx=0))

    # доріжка 1: команда — миттєвий перепад «низ→верх» у момент tsw
    f.append(line(x0, trow[0], tsw, trow[0], color=NEG, sw=2.6))
    f.append(line(tsw, trow[0], tsw, trow[0] - hi, color=NEG, sw=2.6))
    f.append(line(tsw, trow[0] - hi, x1, trow[0] - hi, color=POS, sw=2.6))
    f.append(text(tsw + 8, trow[0] - hi - 8, "команда перекинути плече", size=11,
                  color=INK, anchor="start", bold=True))

    # доріжка 2: нижній був відкритий, після команди СПАДАЄ повільно (розряд затвора)
    f.append(line(x0, trow[1] - hi, tsw, trow[1] - hi, color=FIELD, sw=2.6))     # відкритий
    f.append('<path d="M %.0f,%.0f L %.0f,%.0f" stroke="%s" stroke-width="2.6" fill="none"/>'
             % (tsw, trow[1] - hi, fall_end, trow[1], FIELD))                    # похилий спад
    f.append(line(fall_end, trow[1], x1, trow[1], color=FIELD, sw=2.6))
    f.append(text(x1, trow[1] - hi - 8, "спорожнення Qg → повільний спад",
                  size=10, color=FIELD, anchor="end", bold=True))

    # доріжка 3: верхній ПІДІЙМАЄТЬСЯ одразу за командою (якщо БЕЗ паузи)
    f.append(line(x0, trow[2], tsw, trow[2], color=POS, sw=2.6))
    f.append('<path d="M %.0f,%.0f L %.0f,%.0f" stroke="%s" stroke-width="2.6" fill="none"/>'
             % (tsw, trow[2], rise_end, trow[2] - hi, POS))
    f.append(line(rise_end, trow[2] - hi, x1, trow[2] - hi, color=POS, sw=2.6))
    f.append(text(x1, trow[2] + 18, "верхній уже відкривається",
                  size=10, color=POS, anchor="end", bold=True))

    # підпис вікна — під доріжками, у своїй рамці (стрілки з рамки вгору в смугу)
    body, bw, bh = textbox((ov0 + ov1) / 2, 372,
                           ["обидва прочинені →", "наскрізний струм"],
                           size=11, fill="#fdecea", stroke=POS, sw=1.4, color=POS, bold=True)
    f.append(body)

    f.append(text(W / 2, 414,
                  "Команда миттєва, та нижній ключ гасне повільно (стікає заряд затвора) — і на мить обидва відкриті.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "overlap.svg"), W, H, *f)


# ── фіг. 2. Знак струму навантаження задає похибку напруги в паузі ────────────
def fig_polarity():
    W, H = 820, 520
    f = [text(W / 2, 28, "Куди тягне вихід у мертву паузу: вирішує знак струму", size=16, bold=True)]

    def leg(cx, iout_sign, title):
        """Малює одне плече; iout_sign = +1 (струм витікає з вузла у навантаження)
        або −1 (струм втікає у вузол). Показує, який body-діод веде й куди сяде SW."""
        top = 92          # шина +Vbus
        bot = 372         # GND
        # шина й земля
        f.append(line(cx - 66, top, cx + 66, top, color=POS, sw=2.4))
        f.append(text(cx, top - 10, "+Vbus", size=11, color=POS, bold=True))
        f.append(line(cx - 66, bot, cx + 66, bot, color=INK, sw=1.8))
        f.append(text(cx - 40, bot + 17, "GND", size=10, anchor="middle", bold=True))

        # верхній і нижній ключі (обидва ЗАКРИТІ — мертва пауза)
        f.append(rect(cx - 32, top + 40, 64, 42, fill="#eef2f7", stroke="#9aa7b4", sw=1.6))
        f.append(text(cx, top + 58, "верх", size=10, bold=True))
        f.append(text(cx, top + 74, "OFF", size=9, color=MUTED))
        f.append(rect(cx - 32, bot - 82, 64, 42, fill="#eef2f7", stroke="#9aa7b4", sw=1.6))
        f.append(text(cx, bot - 64, "низ", size=10, bold=True))
        f.append(text(cx, bot - 48, "OFF", size=9, color=MUTED))

        sw_y = (top + bot) / 2
        # з'єднання шина-верх, верх-SW, SW-низ, низ-GND
        f.append(line(cx, top, cx, top + 40, color=INK, sw=2))
        f.append(line(cx, top + 82, cx, sw_y, color=INK, sw=2))
        f.append(line(cx, sw_y, cx, bot - 82, color=INK, sw=2))
        f.append(line(cx, bot - 40, cx, bot, color=INK, sw=2))
        f.append(circle(cx, sw_y, 3.4, fill=INK, stroke=INK, sw=1))
        f.append(text(cx - 12, sw_y - 7, "SW", size=10, anchor="end", bold=True))

        # вихід SW → навантаження ліворуч (щоб не вийти за полотно на правому плечі)
        f.append(line(cx, sw_y, cx - 74, sw_y, color=INK, sw=2))
        f.append(text(cx - 78, sw_y - 7, "навантаження", size=10, anchor="end"))
        f.append(text(cx - 78, sw_y + 8, "← струм", size=10, anchor="end") if iout_sign > 0
                 else text(cx - 78, sw_y + 8, "струм →", size=10, anchor="end"))

        # body-діод, що веде, підсвітимо зеленим (праворуч від колонки), і стрілку струму
        if iout_sign > 0:
            # струм ВИТІКАЄ з SW у навантаження → у паузі його тягне НИЖНІЙ body-діод
            f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f Z" fill="#eafaf0" stroke="%s" stroke-width="1.8"/>'
                     % (cx + 44, bot - 68, cx + 44, bot - 50, cx + 60, bot - 59, FIELD))
            f.append(line(cx + 44, bot - 72, cx + 60, bot - 72, color=FIELD, sw=2.4))
            f.append(line(cx + 52, bot - 59, cx + 52, bot - 40, color=FIELD, sw=2))
            f.append(line(cx + 52, bot - 82, cx + 52, bot - 72, color=FIELD, sw=2))
            f.append(arrow(cx + 52, bot - 18, cx + 52, sw_y + 8, color=FIELD, sw=2.2))
            f.append(text(cx + 66, sw_y + 4, "веде НИЖНІЙ", size=10, color=FIELD, anchor="start", bold=True))
            f.append(text(cx + 66, sw_y + 20, "body-діод", size=10, color=FIELD, anchor="start"))
            f.append(text(cx, bot + 44, "SW сідає до GND (−0.7 В)", size=11, color=NEG, bold=True))
            f.append(text(cx, bot + 62, "вихід НИЖЧИЙ за бажаний", size=10, color=MUTED))
        else:
            # струм ВТІКАЄ у SW із навантаження → його приймає ВЕРХНІЙ body-діод
            f.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f Z" fill="#eafaf0" stroke="%s" stroke-width="1.8"/>'
                     % (cx + 44, top + 50, cx + 44, top + 68, cx + 60, top + 59, FIELD))
            f.append(line(cx + 44, top + 46, cx + 60, top + 46, color=FIELD, sw=2.4))
            f.append(line(cx + 52, top + 59, cx + 52, top + 82, color=FIELD, sw=2))
            f.append(line(cx + 52, top + 40, cx + 52, top + 46, color=FIELD, sw=2))
            f.append(arrow(cx + 52, sw_y - 8, cx + 52, top + 90, color=FIELD, sw=2.2))
            f.append(text(cx + 66, sw_y + 4, "веде ВЕРХНІЙ", size=10, color=FIELD, anchor="start", bold=True))
            f.append(text(cx + 66, sw_y + 20, "body-діод", size=10, color=FIELD, anchor="start"))
            f.append(text(cx, bot + 44, "SW злітає до +Vbus (+0.7 В)", size=11, color=POS, bold=True))
            f.append(text(cx, bot + 62, "вихід ВИЩИЙ за бажаний", size=10, color=MUTED))

        f.append(text(cx, 66, title, size=12, bold=True))

    leg(240, +1, "струм ТЕЧЕ у навантаження")
    leg(600, -1, "струм ТЕЧЕ з навантаження")

    # роздільник між двома плечима (посередині вільного проміжку, повз усі написи)
    f.append(line(420, 80, 420, 452, color="#d9dee4", sw=1.2, dash="5,5"))

    body, bw, bh = textbox(W / 2, 492,
                           ["У паузі обидва ключі закриті, тож вузол SW тягне body-діод —",
                            "а який саме, задає напрямок струму. Тому похибка напруги міняє знак разом зі струмом."],
                           size=11, fill="#f6f8fb", stroke="#c9d3dc", sw=1.2, pad=9)
    f.append(body)
    render(os.path.join(IMG, "polarity.svg"), W, H, *f)


# ── фіг. 3. Вузький коридор вибору мертвого часу ──────────────────────────────
def fig_corridor():
    W, H = 760, 300
    f = [text(W / 2, 28, "Мертвий час — вузький коридор між двома бідами", size=16, bold=True)]

    x0, x1 = 90, 690
    axy = 150
    f.append(arrow(x0, axy, x1 + 8, axy, color=INK, sw=2))
    f.append(text(x1 + 12, axy + 5, "t_dead", size=12, anchor="start", bold=True))

    # зона «замало» (ліворуч, червона), «коридор» (посередині, зелена), «забагато» (праворуч, помаранч)
    a = x0 + 170     # межа «замало|ок»
    b = x0 + 360     # межа «ок|забагато»
    f.append(rect(x0, axy - 40, a - x0, 80, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(rect(a, axy - 40, b - a, 80, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(rect(b, axy - 40, x1 - b, 80, fill="#fef3e2", stroke="#c78a2c", sw=1.4))

    f.append(text((x0 + a) / 2, axy - 4, "ЗАМАЛО", size=13, color=POS, bold=True))
    f.append(text((x0 + a) / 2, axy + 18, "наскрізний струм", size=10, color=POS))
    f.append(text((a + b) / 2, axy - 4, "коридор", size=13, color=FIELD, bold=True))
    f.append(text((a + b) / 2, axy + 18, "надійно й точно", size=10, color=FIELD))
    f.append(text((b + x1) / 2, axy - 4, "ЗАБАГАТО", size=13, color="#b5732e", bold=True))
    f.append(text((b + x1) / 2, axy + 18, "втрати + спотворення", size=10, color="#b5732e"))

    # нижня межа коридору = найгірший час вимкнення
    f.append(line(a, axy + 40, a, axy + 74, color=INK, sw=1.4, dash="3,3"))
    lo, lw, lh = textbox(a, 236, ["t_вимк(макс)", "+ розкид драйвера"],
                         size=10, fill=BG, stroke=INK, sw=1.2, pad=7)
    f.append(lo)

    # верхня межа = коли втрати/спотворення стають нестерпні
    f.append(line(b, axy + 40, b, axy + 74, color=INK, sw=1.4, dash="3,3"))
    hi_, hw, hh = textbox(b, 236, ["межа за втратами", "й спотворенням"],
                          size=10, fill=BG, stroke=INK, sw=1.2, pad=7)
    f.append(hi_)

    f.append(text(W / 2, 284,
                  "Бери трохи більше за найгірший час вимкнення — і не більше, ніж дозволяють втрати.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "corridor.svg"), W, H, *f)


if __name__ == "__main__":
    fig_overlap()
    fig_polarity()
    fig_corridor()
    print("Готово: 3 фігури статті у", IMG)
