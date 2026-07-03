# -*- coding: utf-8 -*-
"""figs-math.py — фігури до вставки «math-delay-margin».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Окремий від figs.py / figs-d.py, щоб не чіпати їх.

Дві фігури:
  M1 predictor-loop  — предиктор Сміта: модель + затримка виносять лаг за контур.
  M2 phantom-display — предиктивний дисплей: миттєвий фантом поверх запізнілого відео.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура M1: предиктор Сміта — винести затримку за контур ───────────────────
# Ідея: контролер бачить не запізнілий реальний вихід, а МИТТЄВИЙ вихід моделі
# (predictor), і лише повільно звіряється з реальністю через різницю
# (запізніла модель − запізніле залізо). Регулятор замикається на швидку модель,
# затримка йде в зовнішню, повільну корекцію.
def fig_predictor_loop():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 34, "Предиктор Сміта: контролер замикається на модель, не на лаг",
                  size=17.5, bold=True))

    yb = 150          # рядок головного тракту
    bh = 56           # висота блоків

    # блоки головного тракту: регулятор → модель апарата → затримка → «залізо»
    def blk(cx, s, fill=FILL, stroke=LINE, color=INK, w=None):
        fr, bw, bhh = textbox(cx, yb, s, size=12.5, pad=12, fill=fill, stroke=stroke,
                              color=color, bold=True, min_w=(w or 0))
        return fr, cx - bw / 2, cx + bw / 2

    x_reg = 175
    reg, reg_l, reg_r = blk(x_reg, "Регулятор\n(контролер)", fill="#eef2f7")
    x_mod = 420
    mod, mod_l, mod_r = blk(x_mod, "МОДЕЛЬ апарата\n(миттєва, без лагу)", fill="#eafbf0", stroke=FIELD, color=FIELD)
    x_del = 660
    dely, del_l, del_r = blk(x_del, "затримка\ne^(−sτ)", fill="#fdecea", stroke=POS, color=POS)
    x_out = 858
    out, out_l, out_r = blk(x_out, "апарат\n(залізо)")

    # вузол зведення на вході (де віднімається зворотний зв'язок)
    sx = 95
    P.append(minus(sx, yb, r=11))
    P.append(text(sx, yb - 26, "ціль", size=12, color=INK, bold=True))
    P.append(arrow(sx + 11, yb, reg_l, yb, color=INK))

    # головний прямий тракт
    P.append(reg); P.append(mod); P.append(dely); P.append(out)
    P.append(arrow(reg_r, yb, mod_l, yb, color=INK))
    P.append(text((reg_r + mod_l) / 2, yb - 10, "команда u", size=11, color=MUTED))
    P.append(arrow(mod_r, yb, del_l, yb, color=INK))
    P.append(arrow(del_r, yb, out_l, yb, color=INK))

    # ШВИДКА петля: миттєвий вихід моделі повертається одразу на вхід.
    # Лінію ведемо на висоті ym_fb, а ПІДПИС ставимо нижче лінії (щоб лінія не різала напис).
    ym_fb = yb + 90
    P.append(line(mod_r + 6, yb, mod_r + 6, ym_fb, color=FIELD, sw=2))
    P.append(line(mod_r + 6, ym_fb, sx, ym_fb, color=FIELD, sw=2))
    P.append(arrow(sx, ym_fb, sx, yb + 11, color=FIELD, sw=2))
    fr, w, h = textbox((sx + mod_r) / 2, ym_fb + 26, "миттєвий вихід моделі → швидка петля",
                       size=11, pad=6, fill="#eafbf0", stroke=FIELD, color=FIELD, bold=True)
    P.append(fr)

    # ПОВІЛЬНА корекція: (реальний запізнілий вихід) − (запізніла модель) = похибка моделі.
    # Лінію ведемо нижче за швидку петлю; підпис — знову нижче своєї лінії.
    ye_fb = yb + 165
    cx_corr = (x_del + x_out) / 2
    P.append(circle(cx_corr, yb + 6, 4, fill=INK, stroke=INK))  # відгалуження реального виходу
    P.append(line(cx_corr, yb + 6, cx_corr, ye_fb, color=INK, sw=1.8))
    P.append(line(cx_corr, ye_fb, sx, ye_fb, color=INK, sw=1.8))
    P.append(arrow(sx, ye_fb, sx, yb + 11, color=INK, sw=1.8))
    fr, w, h = textbox((sx + cx_corr) / 2, ye_fb + 26,
                       "повільна звірка: реальність − запізніла модель  (корекція дрейфу)",
                       size=11, pad=6, fill=FILL, stroke=INK, color=INK)
    P.append(fr)

    # висновок
    fr, w, h = textbox(W / 2, H - 30,
                       "Регулятор «відчуває» апарат БЕЗ затримки (через модель); "
                       "лаг лишається тільки в повільній фоновій корекції.",
                       size=12.5, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/predictor-loop.svg", W, H, *P)


# ── Фігура M2: предиктивний дисплей / фантомний робот ─────────────────────────
# Ідея: на екрані два образи. Запізнілий РЕАЛЬНИЙ апарат (де він був τ тому) —
# блідий, позаду. Миттєвий ФАНТОМ (де він буде за командою) — яскравий, попереду.
# Око оператора замикає петлю на фантом → лаг зникає для очей; реальність
# наздоганяє фантом за час τ.
def fig_phantom_display():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 32, "Предиктивний дисплей: око замикає петлю на миттєвий фантом",
                  size=17.5, bold=True))

    # рамка «екран оператора»
    sx, sy, sw_, sh = 70, 60, 560, 320
    P.append(rect(sx, sy, sw_, sh, fill="#0f1620", stroke=INK, sw=2, rx=10))
    P.append(text(sx + 14, sy + 24, "екран оператора", size=12, color="#9fb0c0", anchor="start"))

    # «доріжка» в перспективі — межі проїзду
    gnd = sy + sh - 30
    P.append(line(sx + 120, gnd, sx + sw_ - 120, gnd, color="#3a4a5a", sw=2))
    P.append(line(sx + 60, gnd, sx + 210, sy + 120, color="#33414f", sw=1.6))
    P.append(line(sx + sw_ - 60, gnd, sx + sw_ - 210, sy + 120, color="#33414f", sw=1.6))

    # перешкода-камінь попереду
    rock_x, rock_y = sx + sw_ / 2 + 8, sy + 150
    P.append(circle(rock_x, rock_y, 20, fill="#5a4633", stroke="#8a6a44", sw=2))
    P.append(text(rock_x, rock_y + 40, "камінь", size=11, color="#c8a06a"))

    # РЕАЛЬНИЙ (запізнілий) ровер — блідий, нижче/позаду
    def rover(cx, cy, body, edge, label, lcol, sub):
        f = []
        f.append(rect(cx - 34, cy - 20, 68, 40, fill=body, stroke=edge, sw=2, rx=6))
        f.append(circle(cx - 22, cy + 22, 9, fill="#222", stroke=edge, sw=2))
        f.append(circle(cx + 22, cy + 22, 9, fill="#222", stroke=edge, sw=2))
        f.append(circle(cx, cy - 4, 6, fill=edge, stroke=edge))   # камера
        f.append(text(cx, cy - 34, label, size=12, color=lcol, bold=True))
        f.append(text(cx, cy + 46, sub, size=10.5, color=lcol))
        return "".join(f)

    real_x, real_y = sx + sw_ / 2 - 6, gnd - 46
    P.append(rover(real_x, real_y, "#1c2733", "#5c6b7a",
                   "реальний (запізнілий)", "#8fa0b0", "де апарат був τ тому"))

    # ФАНТОМ — яскравий, попереду по курсу (ближче до каменя)
    ph_x, ph_y = rock_x - 4, rock_y + 70
    P.append(rover(ph_x, ph_y, "#123a24", FIELD,
                   "фантом (миттєвий)", "#57e08e", "де апарат буде за командою"))

    # стрілка руху фантома вперед
    P.append(arrow(real_x + 20, real_y - 10, ph_x - 20, ph_y + 12, color=FIELD, sw=2.2))

    # праворуч — петля ока
    ex = sx + sw_ + 70
    eye_y = 150
    fr, w, h = textbox(ex + 110, eye_y, "око оператора", size=12.5, pad=10,
                       fill="#eef2f7", stroke=INK, bold=True)
    P.append(fr)
    fr, w, h = textbox(ex + 110, eye_y + 80, "рука → команда\n(миттєво рухає фантом)",
                       size=11.5, pad=9, fill="#eafbf0", stroke=FIELD, color=FIELD, bold=True)
    P.append(fr)
    fr, w, h = textbox(ex + 110, eye_y + 190, "реальний апарат\nназдоганяє фантом\nчерез час τ",
                       size=11.5, pad=9, fill="#fdecea", stroke=POS, color=POS, bold=True)
    P.append(fr)

    # стрілки петлі: екран → око → команда → фантом
    P.append(arrow(sx + sw_ + 6, eye_y, ex + 40, eye_y, color=INK))
    P.append(arrow(ex + 110, eye_y + 22, ex + 110, eye_y + 56, color=FIELD, sw=2))
    P.append(arrow(ex + 110, eye_y + 104, ex + 110, eye_y + 166, color=POS, sw=2))

    # висновок
    fr, w, h = textbox(W / 2, H - 26,
                       "Петля для ОЧЕЙ замикається без лагу: оператор веде фантом, "
                       "реальність тягнеться слідом.",
                       size=12.5, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/phantom-display.svg", W, H, *P)


if __name__ == "__main__":
    fig_predictor_loop()
    fig_phantom_display()
    print("OK: predictor-loop.svg, phantom-display.svg")
