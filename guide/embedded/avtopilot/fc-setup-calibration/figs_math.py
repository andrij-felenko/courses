# -*- coding: utf-8 -*-
"""Фігури до вставки «math-declination-model.md»
(guide/embedded/avtopilot/fc-setup-calibration).
Всесвітня магнітна модель: вектор поля Землі, його розклад на схилення/нахилення,
і чому схилення втрачає сенс біля магнітного полюса.
Чистий Python; svgkit — зі scripts/ (не переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── допоміжне: дуга кола (svgkit не має arc) ─────────────────────────────────
def _arc(cx, cy, r, a0_deg, a1_deg, color=INK, sw=2):
    """Дуга від a0 до a1 (градуси, 0 = напрям +x, за годинниковою в екранних координатах)."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0)
    y0 = cy + r * math.sin(a0)
    x1 = cx + r * math.cos(a1)
    y1 = cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    return ('<path d="M%.1f %.1f A%.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Розклад вектора поля Землі на кути: схилення D (у горизонтальній площині,
#    від істинної півночі) і нахилення I (вниз від горизонту). H — горизонтальна
#    проєкція, Z — вертикальна, F — повний вектор. Модель WMM видає саме F,
#    з нього рахуються всі кути.  Дві панелі широко рознесені, підписи з запасом.
# ─────────────────────────────────────────────────────────────────────────────
def fig_declination_frame():
    W, H = 1000, 560
    frags = [text(W / 2, 34, "Вектор поля Землі F та його кути: схилення D і нахилення I",
                  size=16, bold=True)]

    # ── Ліва панель: вид ЗГОРИ на горизонтальну площину (схилення D) ──────────
    cx, cy = 250, 320
    R = 140
    frags.append(text(cx, 92, "вид згори · горизонтальна площина", size=12.5, bold=True, color=MUTED))

    # осі N–S, E–W
    frags.append(line(cx, cy - R, cx, cy + R, color=MUTED, sw=1.3))
    frags.append(line(cx - R, cy, cx + R, cy, color=MUTED, sw=1.3))
    frags.append(text(cx, cy - R - 14, "істинна Пн", size=12, bold=True, color=INK))
    frags.append(text(cx, cy + R + 24, "Пд", size=11, color=MUTED))
    frags.append(text(cx + R + 22, cy + 4, "Сх", size=11, color=MUTED))
    frags.append(text(cx - R - 22, cy + 4, "Зх", size=11, color=MUTED))

    # горизонтальна проєкція поля H під кутом D на схід від істинної півночі
    Dang = math.radians(24)
    hx = cx + R * 0.9 * math.sin(Dang)
    hy = cy - R * 0.9 * math.cos(Dang)
    frags.append(arrow(cx, cy, hx, hy, color=POS, sw=2.6))
    frags.append(text(hx + 12, hy + 6, "H → магнітна Пн", size=12, bold=True, color=POS, anchor="start"))

    # дуга кута D між істинною Пн і H (у верхньому секторі, підпис вище дуги)
    ar = 60
    frags.append(_arc(cx, cy, ar, -90, -66, color=INK, sw=2))
    frags.append(text(cx + 30, cy - ar - 8, "D — схилення", size=11.5, bold=True, color=INK, anchor="start"))

    # ── Права панель: вертикальний зріз (нахилення I) ─────────────────────────
    vx, vy = 660, 250           # точка спостерігача (початок вектора), вище центру
    L = 190
    frags.append(text(vx + 60, 92, "вертикальний зріз · площина поля", size=12.5, bold=True, color=MUTED))

    # горизонт (управо) і вертикаль вниз
    frags.append(line(vx - 20, vy, vx + L + 40, vy, color=MUTED, sw=1.3))
    frags.append(line(vx, vy - 20, vx, vy + L + 20, color=MUTED, sw=1.3, dash="4,4"))
    frags.append(text(vx + L + 44, vy - 8, "горизонт", size=11, color=MUTED, anchor="start"))
    frags.append(text(vx - 8, vy - 22, "вгору", size=10, color=MUTED, anchor="end"))

    # повний вектор F — вниз під кутом I від горизонту
    Iang = math.radians(56)
    fx = vx + L * math.cos(Iang)
    fy = vy + L * math.sin(Iang)
    frags.append(arrow(vx, vy, fx, fy, color=FIELD, sw=2.8))
    frags.append(text(fx + 12, fy + 6, "F — повне поле", size=12.5, bold=True, color=FIELD, anchor="start"))

    # проєкції: Z по вертикалі (пунктир від кінця F до горизонту), H по горизонту
    frags.append(line(fx, fy, fx, vy, color=NEG, sw=1.6, dash="3,3"))
    frags.append(line(vx, vy, fx, vy, color=POS, sw=2.6))
    frags.append(text((vx + fx) / 2, vy - 10, "H", size=12.5, bold=True, color=POS))
    frags.append(text(fx + 14, (vy + fy) / 2 + 6, "Z", size=12.5, bold=True, color=NEG, anchor="start"))

    # дуга кута I між горизонтом і F (підпис під дугою, праворуч)
    ir = 50
    frags.append(_arc(vx, vy, ir, 0, 56, color=INK, sw=2))
    frags.append(text(vx + ir + 14, vy + 34, "I — нахилення", size=11.5, bold=True, color=INK, anchor="start"))

    # ── Нижня рамка: що дає WMM (короткі рядки, з запасом під шириною) ─────────
    body, bw, bh = textbox(W / 2, 512,
                           "WMM видає повний вектор F(широта, довгота, висота, дата).\n"
                           "Звідси H = F·cos I,  Z = F·sin I,  а D — кут H від істинної півночі.\n"
                           "Компас без поправки показує вздовж H (магнітна Пн); різницю D додає автопілот.",
                           size=12, pad=13, fill="#f4f8f4", stroke=FIELD, sw=1.6)
    frags.append(body)
    render(os.path.join(IMG, 'declination-frame.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Чому схилення «гуляє» біля магнітного полюса: горизонтальна складова H
#    стискається до нуля (поле стає майже прямовисним, I→90°), і напрям H —
#    а отже й D — стає невизначеним. Ліворуч середні широти (довгий H, D певне),
#    праворуч приполюсна зона (H крихітний, D безладно крутиться).
# ─────────────────────────────────────────────────────────────────────────────
def fig_pole_blowup():
    W, H = 1000, 500
    frags = [text(W / 2, 34, "Чому схилення різко гуляє біля магнітного полюса", size=16, bold=True)]

    def panel(cx, title, sub, Hlen, jitter, foot, foot_col):
        f = [text(cx, 82, title, size=13.5, bold=True),
             text(cx, 102, sub, size=11, color=MUTED)]
        cy = 260
        R = 120
        f.append(circle(cx, cy, R, fill="#ffffff", stroke=MUTED, sw=1.2))
        f.append(line(cx, cy - R, cx, cy + R, color=MUTED, sw=1.0, dash="4,4"))
        f.append(line(cx - R, cy, cx + R, cy, color=MUTED, sw=1.0, dash="4,4"))
        f.append(text(cx, cy - R - 12, "істинна Пн", size=10.5, color=MUTED))

        if jitter is None:
            ang = math.radians(18)
            hx = cx + Hlen * math.sin(ang)
            hy = cy - Hlen * math.cos(ang)
            f.append(arrow(cx, cy, hx, hy, color=POS, sw=3))
            f.append(text(hx + 12, hy, "H", size=13, bold=True, color=POS, anchor="start"))
        else:
            for a_deg in jitter:
                a = math.radians(a_deg)
                hx = cx + Hlen * math.sin(a)
                hy = cy - Hlen * math.cos(a)
                f.append(arrow(cx, cy, hx, hy, color=POS, sw=2))
            f.append(circle(cx, cy, 4, fill=POS, stroke=POS, sw=1))
        f.append(text(cx, cy + R + 30, foot, size=11, bold=True, color=foot_col))
        return f

    frags += panel(255, "середні широти", "поле нахилене, H великий",
                   Hlen=96, jitter=None,
                   foot="H довгий → напрям чіткий → D певне", foot_col=FIELD)
    frags += panel(745, "приполюсна зона", "поле майже прямовисне, I → 90°",
                   Hlen=24, jitter=[-70, -30, 5, 40, 80, 120, -120],
                   foot="H крихітний → напрям стрибає → D невизначене", foot_col=POS)

    frags.append(line(500, 70, 500, 400, color="#dddddd", sw=1.2))

    body, bw, bh = textbox(W / 2, 462,
                           "H = F·cos I.  Біля полюса I → 90°, тож cos I → 0 і H → 0.\n"
                           "Мала похибка вектора обертає крихітний H на десятки градусів —\n"
                           "тому в приполюсній зоні (H < 2000 нТ) схилення WMM ненадійне.",
                           size=12, pad=13, fill="#fdf2f0", stroke=POS, sw=1.6)
    frags.append(body)
    render(os.path.join(IMG, 'pole-blowup.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_declination_frame()
    fig_pole_blowup()
    print("OK: declination-frame.svg, pole-blowup.svg")
