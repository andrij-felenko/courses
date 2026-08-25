# -*- coding: utf-8 -*-
"""Фігури до теми «Ультразвуковий далекомір» (book/electronics/sensors).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Геометрія виміру: звук туди-й-назад, тому ділимо на два ───────────────
def fig_measure():
    W, H = 720, 340
    f = [text(W / 2, 28, "Звук долає відстань двічі — тому в формулі ділимо на два", size=16, bold=True)]

    # давач ліворуч
    dx, dy = 70, 175
    f.append(rect(dx - 26, dy - 34, 52, 68, fill="#e9edf2", stroke=LINE, sw=2, rx=6))
    f.append(circle(dx, dy, 17, fill="#dfe6ee", stroke=MUTED, sw=1.6))
    f.append(text(dx, dy + 52, "далекомір", size=11, color=MUTED))

    # ціль праворуч
    tx = 600
    f.append(rect(tx, dy - 70, 18, 140, fill="#cfd8e2", stroke=LINE, sw=2))
    f.append(text(tx + 9, dy + 92, "ціль", size=11, color=MUTED))

    # промінь туди (вгорі) і назад (внизу)
    f.append(arrow(dx + 30, dy - 16, tx - 6, dy - 16, color=POS, sw=2.4))
    f.append(text((dx + tx) / 2, dy - 26, "пакет туди", size=12, color=POS, bold=True))
    f.append(arrow(tx - 6, dy + 16, dx + 30, dy + 16, color=NEG, sw=2.4))
    f.append(text((dx + tx) / 2, dy + 34, "відлуння назад", size=12, color=NEG, bold=True))

    # позначка відстані d
    f.append(line(dx, dy + 72, dx, dy + 96, color=MUTED, sw=1.2))
    f.append(line(tx, dy + 72, tx, dy + 96, color=MUTED, sw=1.2))
    f.append(line(dx, dy + 88, tx, dy + 88, color=INK, sw=1.4, dash="5,4"))
    f.append(text((dx + tx) / 2, dy + 82, "відстань d", size=12, color=INK))

    # формула
    b, _, _ = textbox(W / 2, 300, "d = v · t / 2     (t — повний час; шлях = 2d)",
                      size=14, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)
    render(os.path.join(IMG, "measure.svg"), W, H, *f)


# ── 2. Інтерфейс trigger/echo очима прошивки (фронт→захоплення→спад) ─────────
def fig_trigger_echo():
    W, H = 720, 380
    f = [text(W / 2, 28, "Що ловить прошивка: ширина echo дорівнює часу польоту", size=16, bold=True)]

    ox = 70
    span = 580
    # три доріжки сигналів
    def track(y, label, color):
        f.append(text(ox - 8, y + 4, label, size=12, color=INK, anchor="end", bold=True))
        f.append(line(ox, y, ox + span, y, color="#d6dde6", sw=1.0))  # базова лінія
        return y

    yt = track(80, "trigger", POS)
    yp = track(190, "п'єзо", MUTED)
    ye = track(300, "echo", NEG)

    amp = 34
    # TRIGGER: короткий імпульс на старті
    t0 = ox + 30
    t1 = ox + 60
    f.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (ox, yt, t0, yt, t0, yt - amp, t1, yt - amp, t1, yt, POS))
    f.append('<polyline points="%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (t1, yt, ox + span, yt, POS))
    f.append(text((t0 + t1) / 2, yt - amp - 8, "≈10 мкс «пни»", size=10.5, color=POS))

    # П'ЄЗО: пакет на старті + слабке відлуння згодом
    burst_x = t1 + 14
    pts = []
    for i in range(16):
        x = burst_x + i * 3.4
        sign = -1 if i % 2 == 0 else 1
        env = 1.0 - i / 20.0
        pts.append("%.1f,%.1f" % (x, yp + sign * amp * 0.7 * env))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), POS))
    f.append(text(burst_x + 26, yp - amp - 2, "пакет ≈8×40 кГц", size=10.5, color=POS))
    # відлуння (слабше) пізніше
    echo_x = ox + 360
    pts2 = []
    for i in range(14):
        x = echo_x + i * 3.4
        sign = -1 if i % 2 == 0 else 1
        env = 0.5 - i / 40.0
        pts2.append("%.1f,%.1f" % (x, yp + sign * amp * env))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts2), NEG))
    f.append(text(echo_x + 22, yp + amp + 14, "слабке відлуння", size=10.5, color=NEG))

    # ECHO: високий рівень від кінця пакета до приходу відлуння
    rise = burst_x + 4
    fall = echo_x + 6
    f.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox, ye, rise, ye, rise, ye - amp, fall, ye - amp, fall, ye, NEG))
    f.append('<polyline points="%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (fall, ye, ox + span, ye, NEG))
    # фронт і спад — точки захоплення
    f.append(circle(rise, ye - amp, 4, fill=BG, stroke=INK, sw=1.6))
    f.append(circle(fall, ye - amp, 4, fill=BG, stroke=INK, sw=1.6))
    f.append(text(rise, ye - amp - 8, "фронт→t₁", size=10, color=INK))
    f.append(text(fall, ye - amp - 8, "спад→t₂", size=10, color=INK))
    # ширина = час польоту
    f.append(line(rise, ye + 18, fall, ye + 18, color=INK, sw=1.4, dash="5,4"))
    f.append(text((rise + fall) / 2, ye + 34, "t = t₂ − t₁  →  d = t / 58  (см)", size=12, color=INK, bold=True))
    render(os.path.join(IMG, "trigger-echo.svg"), W, H, *f)


# ── 3. Робоче вікно: сліпа зона зблизька, тайм-аут удалині ───────────────────
def fig_window():
    W, H = 720, 300
    f = [text(W / 2, 28, "Робоче вікно: між сліпою зоною та межею дальності", size=16, bold=True)]

    ox, oy = 60, 150
    span = 600
    f.append(line(ox, oy, ox + span, oy, color=INK, sw=2))
    f.append(arrow(ox + span, oy, ox + span + 18, oy, color=INK, sw=2))
    f.append(text(ox + span + 8, oy + 26, "відстань", size=11, color=MUTED, anchor="end"))

    # давач у нулі
    f.append(rect(ox - 18, oy - 16, 30, 32, fill="#e9edf2", stroke=LINE, sw=1.8, rx=5))
    f.append(text(ox - 3, oy + 40, "0", size=11, color=MUTED))

    blind_end = ox + 90
    max_end = ox + 510

    # сліпа зона — заштрихована
    f.append(rect(ox, oy - 26, blind_end - ox, 52, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text((ox + blind_end) / 2, oy - 36, "сліпа зона", size=11.5, color=POS, bold=True))
    f.append(text((ox + blind_end) / 2, oy + 44, "пластина ще дзвенить — глуха", size=10.5, color=MUTED))

    # робоче вікно — зелене
    f.append(rect(blind_end, oy - 26, max_end - blind_end, 52, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    f.append(text((blind_end + max_end) / 2, oy - 36, "робоче вікно", size=12.5, color=FIELD, bold=True))
    f.append(text((blind_end + max_end) / 2, oy + 44, "чесний вимір тут", size=10.5, color=MUTED))

    # за межею — тайм-аут
    f.append(rect(max_end, oy - 26, ox + span - 30 - max_end, 52, fill="#f1f1f1", stroke=MUTED, sw=1.4, rx=4))
    f.append(text((max_end + ox + span - 30) / 2, oy - 36, "тайм-аут", size=11.5, color=MUTED, bold=True))
    f.append(text((max_end + ox + span - 30) / 2, oy + 44, "відлуння тоне в шумі", size=10.5, color=MUTED))

    # типові числа
    f.append(text(blind_end, oy + 70, "≈ 2 см", size=11, color=POS, bold=True))
    f.append(text(max_end, oy + 70, "кілька метрів", size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── 4. Чому коса/м'яка поверхня зриває ехо (дзеркальне відбиття) ─────────────
def fig_surface():
    W, H = 760, 360
    f = [text(W / 2, 28, "Тверда пласка ціль вертає луну; коса й м'яка — ні", size=16, bold=True)]

    def panel(cx, title, ok):
        f.append(text(cx, 60, title, size=12.5, bold=True, color=(FIELD if ok else POS)))
        # давач
        f.append(rect(cx - 30, 100, 30, 30, fill="#e9edf2", stroke=LINE, sw=1.6, rx=5))
        return cx

    # A: пласка перпендикулярна — луна повертається
    cxa = panel(120, "пласка, прямо", True)
    f.append(line(cxa + 110, 80, cxa + 110, 230, color=INK, sw=4))
    f.append(arrow(cxa - 4, 112, cxa + 106, 112, color=POS, sw=2.2))
    f.append(arrow(cxa + 106, 124, cxa - 4, 124, color=NEG, sw=2.2))
    f.append(text(cxa, 270, "луна назад → бачить", size=11, color=FIELD, bold=True))

    # B: коса — луна летить убік повз приймач
    cxb = panel(380, "коса (дзеркало)", False)
    f.append(line(cxb + 60, 90, cxb + 130, 220, color=INK, sw=4))
    f.append(arrow(cxb - 4, 115, cxb + 92, 150, color=POS, sw=2.2))
    # відбита вбік (закон дзеркала)
    f.append(arrow(cxb + 92, 150, cxb + 138, 72, color=NEG, sw=2.2))
    f.append(text(cxb, 270, "відбилась убік → повз", size=11, color=POS, bold=True))

    # C: м'яка — поглинає
    cxc = panel(640, "м'яка (поролон)", False)
    f.append(rect(cxc + 86, 90, 32, 140, fill="#e5d4c4", stroke=MUTED, sw=1.4, rx=4))
    # хвиля входить і гасне (затухаючі дуги)
    f.append(arrow(cxc - 4, 130, cxc + 82, 130, color=POS, sw=2.2))
    for rr in (10, 7, 4):
        f.append(circle(cxc + 102, 130, rr, fill="none", stroke=MUTED, sw=1.2))
    f.append(text(cxc, 270, "поглинула → тиша", size=11, color=POS, bold=True))

    f.append(text(W / 2, 322, "далекомір міряє не «об'єкт», а перше сильне відлуння, що повернулось",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, "surface.svg"), W, H, *f)


# ── 5. Промінь-конус: широко «накриває», точно не вказує ─────────────────────
def fig_beam():
    W, H = 720, 330
    f = [text(W / 2, 28, "Промінь — конус: накриває сектор, відповідає найближча ціль", size=16, bold=True)]

    dx, dy = 70, 175
    f.append(rect(dx - 22, dy - 26, 36, 52, fill="#e9edf2", stroke=LINE, sw=2, rx=6))
    f.append(text(dx - 4, dy + 50, "давач", size=11, color=MUTED))

    # конус ≈25°
    far = 560
    half = 130
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#eef6ef" stroke="%s" stroke-width="1.4" opacity="0.85"/>'
             % (dx + 14, dy, dx + far, dy - half, dx + far, dy + half, FIELD))
    f.append(line(dx + 14, dy, dx + far, dy - half, color=FIELD, sw=1.4))
    f.append(line(dx + 14, dy, dx + far, dy + half, color=FIELD, sw=1.4))
    f.append(text(dx + 150, dy - 70, "конус 15–30°", size=12, color=FIELD, bold=True))

    # дві цілі в секторі: ближча відповідає
    near_x, near_y = dx + 250, dy - 40
    far_x, far_y = dx + 430, dy + 55
    f.append(circle(near_x, near_y, 13, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(near_x, near_y - 22, "ближча", size=11, color=POS, bold=True))
    f.append(circle(far_x, far_y, 13, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(far_x, far_y + 26, "дальша", size=11, color=NEG, bold=True))

    # ехо приходить від ближчої
    f.append(arrow(dx + 16, dy - 4, near_x - 12, near_y + 6, color=POS, sw=2.2))
    f.append(arrow(near_x - 12, near_y + 12, dx + 16, dy + 6, color=POS, sw=2.2))
    f.append(text(dx + 150, dy + 92, "чує лише ближчу — її луна перша й найгучніша",
                  size=11, color=INK))
    render(os.path.join(IMG, "beam.svg"), W, H, *f)


if __name__ == "__main__":
    fig_measure()
    fig_trigger_echo()
    fig_window()
    fig_surface()
    fig_beam()
    print("OK: 5 figures ->", IMG)
