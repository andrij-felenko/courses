# -*- coding: utf-8 -*-
"""Фігури до вставки «🧮 Стеля частоти» теми «Синхронний лічильник».
Окремий генератор (щоб не конфліктувати з figs.py при паралельному письмі);
стиль і помічники — зі спільного svgkit, вивід у ту саму ./img/.
Запуск:  python figs_math.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Критичний шлях: три відрізки затримки в один період такту ────────────
def fig_criticalpath():
    """Один період такту як лінійка; на ній три відрізки — t_pd, t_carry, t_su —
    що мусять уміститися між двома фронтами. Це і є виведення f_макс."""
    W, H = 780, 400
    parts = [text(W / 2, 30, "Критичний шлях за один період такту", size=17, bold=True)]

    # два фронти такту — вертикальні червоні лінії
    x0, x1 = 95, 690           # фронт N і фронт N+1
    baseY = 250
    for xx, lab in ((x0, "фронт N"), (x1, "фронт N+1")):
        parts.append(line(xx, 82, xx, baseY + 26, color=POS, sw=2.4))
        parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                     % (xx, 80, xx - 7, 68, xx + 7, 68, POS))
        parts.append(text(xx, 60, lab, size=12, color=POS, bold=True))

    # горизонтальна вісь-час між фронтами
    parts.append(line(x0, baseY, x1, baseY, color=INK, sw=2.0))
    # дужка періоду під віссю
    parts.append(line(x0, baseY + 20, x0, baseY + 30, color=INK, sw=1.4))
    parts.append(line(x1, baseY + 20, x1, baseY + 30, color=INK, sw=1.4))
    parts.append(line(x0, baseY + 30, x1, baseY + 30, color=INK, sw=1.4))
    parts.append(text((x0 + x1) / 2, baseY + 46, "T_такту  (один період)", size=13, bold=True))

    # три відрізки затримки, що складаються один за одним
    seg = [("t_pd",    0.34, "#c0392b", ["тригер видав", "новий Q"]),
           ("t_carry", 0.30, "#8e44ad", ["ланцюг AND", "порахував T"]),
           ("t_su",    0.19, "#2457d6", ["дані усталились", "до фронту"])]
    span = (x1 - x0)
    cx = x0
    barY = 148
    for name, frac, col, expl in seg:
        w = span * frac
        parts.append(rect(cx, barY, w, 34, fill=col, stroke=col, sw=1.2, rx=4))
        parts.append(text(cx + w / 2, barY + 22, name, size=13, color="#ffffff", bold=True))
        parts.append(mtext(cx + w / 2, barY + 58, expl, size=10.5, color=col, lh=1.25))
        parts.append(line(cx + w, barY + 34, cx + w, baseY, color=col, sw=1.0, dash="3,3"))
        cx += w
    # лишок = запас до фронту
    if cx < x1 - 1:
        parts.append(rect(cx, barY, x1 - cx, 34, fill="#eef2f7", stroke=MUTED, sw=1.2, rx=4))
        parts.append(text((cx + x1) / 2, barY + 22, "запас", size=11, color=MUTED))

    # формула-висновок
    note, nw, nh = textbox(W / 2, 342,
                           "T_такту ≥ t_pd + t_carry + t_su    ⇒    f_макс = 1 / (t_pd + t_carry + t_su)",
                           size=13, fill="#f4f6f8", color=INK, bold=True, pad=11)
    parts.append(note)
    return render(os.path.join(IMG, "critical-path.svg"), W, H, *parts)


# ── 2. Затримка проти розрядності: ланцюговий росте, синхронний — плаский ────
def fig_scaling():
    """Дві криві бюджету затримки vs число розрядів N: ланцюговий ~ N·t_pd (пряма
    вгору), синхронний ≈ const (горизонталь). Точка перетину — де синхронний виграє."""
    W, H = 760, 450
    parts = [text(W / 2, 30, "Затримка критичного шляху проти числа розрядів", size=17, bold=True)]

    ox, oy = 120, 350          # початок координат (лівий-нижній)
    axw, axh = 540, 262
    parts.append(line(ox, oy, ox + axw, oy, color=INK, sw=2.0))          # X
    parts.append(line(ox, oy, ox, oy - axh, color=INK, sw=2.0))          # Y
    parts.append(arrow(ox + axw, oy, ox + axw + 8, oy, color=INK))
    parts.append(arrow(ox, oy - axh, ox, oy - axh - 8, color=INK))
    parts.append(text(ox + axw - 4, oy + 32, "число розрядів N →", size=12, anchor="end", bold=True))
    parts.append(mtext(ox - 12, oy - axh - 6, ["затримка", "шляху ↑"], size=12, anchor="start", bold=True))

    Nmax = 16
    for N in (4, 8, 12, 16):
        xx = ox + axw * (N / Nmax)
        parts.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.2))
        parts.append(text(xx, oy + 20, str(N), size=11, color=MUTED))

    # синхронний: горизонталь на сталому рівні
    sy = oy - axh * 0.23
    parts.append(line(ox, sy, ox + axw, sy, color=NEG, sw=3.0))
    lab1, w1, h1 = textbox(ox + axw - 122, sy - 24,
                           "синхронний ≈ стала", size=12, fill="#eaf0fd",
                           stroke=NEG, color=NEG, bold=True, pad=7)
    parts.append(lab1)

    # ланцюговий: пряма з нуля вгору, нахил ~ t_pd на розряд
    def rip_y(N):
        return oy - (axh * 0.92) * (N / Nmax)
    parts.append(line(ox, oy, ox + axw, rip_y(Nmax), color=POS, sw=3.0))
    lab2, w2, h2 = textbox(ox + 178, rip_y(6) - 16,
                           "ланцюговий ~ N · t_pd", size=12, fill="#fdecea",
                           stroke=POS, color=POS, bold=True, pad=7)
    parts.append(lab2)

    # точка перетину: rip_y(N*) = sy
    Nx = Nmax * (oy - sy) / (axh * 0.92)
    xX = ox + axw * (Nx / Nmax)
    parts.append(line(xX, sy, xX, oy, color=MUTED, sw=1.0, dash="4,3"))
    parts.append(circle(xX, sy, 5.5, fill="#ffffff", stroke=INK, sw=2.0))
    parts.append(mtext(xX + 4, oy - 40, ["звідси синхронний", "вже швидший"],
                       size=10.5, color=MUTED, anchor="start"))

    note, nw, nh = textbox(W / 2, 418,
                           ["У ланцюгового затримки складаються вздовж розрядів; у синхронного — ні.",
                            "Тому f_макс синхронного не падає зі зростанням ширини."],
                           size=12, fill="#f4f6f8", color=INK, pad=10)
    parts.append(note)
    return render(os.path.join(IMG, "scaling.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_criticalpath()
    fig_scaling()
    print("OK: 2 SVG (math insert) ->", IMG)
