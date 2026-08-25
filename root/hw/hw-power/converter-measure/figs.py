# -*- coding: utf-8 -*-
"""Фігури теми «Вимірювання перетворювача»: вставки comp-electronic-load
(контур керування, ОБР) та proj-efficiency-sweep (обхід сітки ккд).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Контур керування: ОП тримає струм на заданому рівні ──────────────────
def fig_loop():
    W, H = 720, 360
    f = []
    # джерело під випробуванням (DUT) ліворуч
    f.append(fitbox(30, 130, 120, 90, "Джерело\nпід тестом\n(DUT)",
                    size=14, fill="#eef2f7", bold=True))
    f.append(text(90, 240, "+ V −", size=13, color=MUTED))

    # верхня шина «+» від DUT до стоку MOSFET
    f.append(line(150, 150, 470, 150, color=POS, sw=2.4))
    f.append(plus(150, 150, 8))
    # нижня шина «−» через сенс-резистор назад до DUT
    f.append(line(150, 300, 560, 300, color=NEG, sw=2.4))
    f.append(minus(150, 300, 8))

    # MOSFET (квадрат-ключ у лінійному режимі)
    f.append(rect(430, 150, 80, 90, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(mtext(470, 188, ["MOSFET", "лінійний", "режим"], size=12, color=INK, bold=True))
    f.append(line(470, 240, 470, 270, color=INK, sw=2.4))   # стік→витік вниз

    # сенс-резистор Rs у нижній шині
    f.append(rect(500, 285, 60, 30, fill=FILL, stroke=INK, sw=2))
    f.append(text(530, 305, "Rs", size=13, bold=True))

    # точка вимірювання напруги на Rs
    f.append(circle(530, 285, 4, fill=INK, stroke=INK))
    f.append(line(530, 285, 530, 250, color=MUTED, sw=1.4, dash="4 3"))

    # підсилювач похибки (трикутник-ОП)
    ox, oy = 320, 230
    f.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s" stroke="%s" stroke-width="2"/>'
             % (ox, oy - 38, ox + 78, oy, ox, oy + 38, FILL, INK))
    f.append(text(ox + 26, oy + 5, "ОП", size=15, bold=True))
    f.append(text(ox + 8, oy - 16, "−", size=16, color=NEG, bold=True))
    f.append(text(ox + 8, oy + 22, "+", size=16, color=POS, bold=True))

    # уставка Iset на «+» вхід
    f.append(fitbox(170, 250, 110, 40, "Уставка Iset", size=12, fill="#eafaf0",
                    stroke=FIELD, bold=True))
    f.append(arrow(280, 270, ox - 2, oy + 18, color=FIELD, sw=1.8))

    # зворотний зв'язок: спад на Rs → «−» вхід ОП
    f.append(line(530, 250, 530, 192, color=MUTED, sw=1.4, dash="4 3"))
    f.append(line(530, 192, ox - 60, 192, color=MUTED, sw=1.6))
    f.append(arrow(ox - 60, 192, ox - 2, oy - 18, color=MUTED, sw=1.8))
    f.append(text(430, 184, "U(Rs) ∝ струм", size=11, color=MUTED))

    # вихід ОП → затвор MOSFET
    f.append(arrow(ox + 78, oy, 430, 205, color=INK, sw=2))
    f.append(text(408, 224, "затвор", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "load-loop.svg"), W, H, *f,
           title="Контур керування: ОП підганяє затвор, доки спад на Rs не зрівняється з уставкою")


# ── 2. Межі ОБР і де «живе» лінійний режим ──────────────────────────────────
def fig_soa():
    W, H = 720, 430
    f = []
    L, R, T, B = 90, 660, 70, 360     # межі поля графіка
    f.append(line(L, B, R, B, color=INK, sw=2))   # вісь V (горизонт)
    f.append(line(L, B, L, T, color=INK, sw=2))   # вісь I (вертикаль)
    f.append(text(R, B + 26, "напруга на стоку  Vds (log)", size=13, anchor="end"))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="13" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">струм  Id (log)</text>'
             % (L - 22, (T + B) / 2, FONT, INK, L - 22, (T + B) / 2))

    # межі ОБР (кусково-лінійна обвідна у log-log)
    # 1) горизонталь Imax угорі
    f.append(line(L, T + 18, 250, T + 18, color=POS, sw=2.4))
    f.append(text(150, T + 10, "Imax", size=12, color=POS))
    # 2) межа постійної потужності P = V·I (нахил −1)
    f.append(line(250, T + 18, 470, 200, color=POS, sw=2.4))
    f.append(text(360, 150, "P = V·I  (тепло)", size=12, color=POS))
    # 3) крутіший спад — вторинний пробій / лінійні обмеження
    f.append(line(470, 200, 560, 300, color=POS, sw=2.4, dash="6 4"))
    f.append(text(560, 250, "вторинний", size=11, color=POS))
    f.append(text(560, 265, "пробій", size=11, color=POS))
    # 4) вертикаль Vmax праворуч
    f.append(line(600, B, 600, 300, color=POS, sw=2.4))
    f.append(line(560, 300, 600, 300, color=POS, sw=2.4, dash="6 4"))
    f.append(text(600, B + 16, "Vmax", size=12, color=POS, anchor="middle"))

    # безпечна зона (зелена заливка під обвідною, схематично)
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d L%d %d Z" '
             'fill="#27ae60" fill-opacity="0.10" stroke="none"/>'
             % (L, B, L, T + 18, 250, T + 18, 470, 200, 600, 300, 600, B))
    f.append(text(210, 330, "безпечна зона", size=12, color=FIELD, bold=True))

    # робоча точка навантаження: високе V і чималий I одночасно
    px, py = 430, 230
    f.append(circle(px, py, 6, fill=NEG, stroke=NEG))
    f.append(text(px + 10, py - 8, "точка навантаження:", size=11, color=NEG, anchor="start"))
    f.append(text(px + 10, py + 6, "V і I разом → пік тепла", size=11, color=NEG, anchor="start"))
    f.append(line(px, B, px, py, color=NEG, sw=1.2, dash="3 3"))
    f.append(line(L, py, px, py, color=NEG, sw=1.2, dash="3 3"))

    render(os.path.join(IMG, "load-soa.svg"), W, H, *f,
           title="Область безпечної роботи (ОБР): навантаження сидить там, де V·I найбільше")


# ── 3. Обхід сітки ККД «змійкою»: ліворуч траєкторія, праворуч крок вузла ─────
def fig_sweep():
    W, H = 760, 430
    f = []

    # ── ліва панель: сітка точок Vвх × Iвих, обхід «змійкою» ──
    L, R, T, B = 70, 360, 90, 320     # межі поля графіка
    f.append(line(L, B, R, B, color=INK, sw=2))   # вісь Iвих (горизонт)
    f.append(line(L, B, L, T, color=INK, sw=2))   # вісь Vвх (вертикаль)
    f.append(text(R, B + 22, "Iвих →", size=12, color=INK, anchor="end", bold=True))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 %d %d)">Vвх ↑</text>'
             % (L - 24, (T + B) / 2, FONT, INK, L - 24, (T + B) / 2))

    cols = [120, 180, 240, 300]       # 4 струми Iвих
    rows = [270, 200, 130]            # 3 напруги Vвх (знизу вгору)

    # траєкторія «змійкою»: нижній рядок зліва-направо, далі вгору й назад
    path_pts = []
    for ri, ry in enumerate(rows):
        order = cols if ri % 2 == 0 else list(reversed(cols))
        for cx in order:
            path_pts.append((cx, ry))
    poly = " ".join("%.0f,%.0f" % p for p in path_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="4 3" stroke-linejoin="round"/>' % (poly, FIELD))

    for ry in rows:
        for cx in cols:
            f.append(circle(cx, ry, 4, fill=NEG, stroke=NEG, sw=0))
    f.append(circle(cols[0], rows[0], 7, fill=BG, stroke=FIELD, sw=2.4))   # старт
    f.append(text(cols[0] - 2, rows[0] + 22, "старт", size=10, color=FIELD, bold=True))
    f.append(text((L + R) / 2, B + 40, "Iвих: 0.1 · 0.3 · 1 · 2 · 3 А", size=10, color=MUTED))
    f.append(text(L - 8, T - 8, "Vвх: 12 · 14.4 · 16.8 В", size=10, color=MUTED, anchor="start"))

    # ── права панель: що робимо в КОЖНОМУ вузлі ──
    bx, by, bw, bh = 410, 80, 320, 250
    f.append(rect(bx, by, bw, bh, fill="#f6f8fa", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(bx + bw / 2, by + 26, "У кожному вузлі сітки:", size=13, color=INK, bold=True))
    steps = [
        (POS,   "1", "БЖ: задати Vвх (ліміт струму!)"),
        (POS,   "2", "Навантаження: задати Iвих (CC)"),
        ("#caa24a", "3", "ЧЕКАТИ усталення (електр.+тепло)"),
        (FIELD, "4", "зчитати Vвх,Iвх,Vвих,Iвих (Kelvin)"),
        (INK,   "5", "η = (Vвих·Iвих)/(Vвх·Iвх)·100 %"),
        (MUTED, "6", "записати рядок у таблицю"),
    ]
    sy = by + 56
    for col, n, label in steps:
        f.append(circle(bx + 24, sy, 11, fill=col, stroke=col, sw=0))
        f.append(text(bx + 24, sy + 4, n, size=11, color="#fff", bold=True))
        f.append(text(bx + 44, sy + 4, label, size=10, color=INK, anchor="start"))
        sy += 31

    # ── нижній банер: чому скриптом ──
    f.append(rect(60, 388, 640, 26, fill="#eef8ef", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(380, 405,
                  "Десятки точок руками — години й похибки; скрипт через SCPI знімає криву за хвилини",
                  size=10, color=INK))

    render(os.path.join(IMG, "sweep.svg"), W, H, *f,
           title="Обхід сітки ККД «змійкою»: у кожному вузлі — задати, зачекати, зчитати, порахувати")


if __name__ == "__main__":
    fig_loop()
    fig_soa()
    fig_sweep()
    print("OK: figs -> img/")
