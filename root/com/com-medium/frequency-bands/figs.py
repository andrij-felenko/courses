# -*- coding: utf-8 -*-
"""Фігури теми «Діапазони частот». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: головний компроміс — одна стрілка частоти міняє чотири властивості
# Горизонтальна вісь частоти. Ліворуч (низька f) виграє дальність і проникність,
# програє антену й швидкість; праворуч (висока f) — навпаки. Видно, що чотири
# властивості жорстко зв'язані одним рухом по осі.
def fig_tradeoff():
    W, H = 700, 380
    ax_y = 150
    x0, x1 = 90, 610
    parts = []
    parts.append(arrow(x0 - 30, ax_y, x1 + 30, ax_y, color=INK, sw=2.2))
    parts.append(text((x0 + x1) / 2, ax_y - 22, "частота", 13, INK, "middle", bold=True))
    parts.append(text(x0 - 30, ax_y + 22, "низька", 12, NEG, "start"))
    parts.append(text(x1 + 30, ax_y + 22, "висока", 12, POS, "end"))
    # ліва пара виграшів (зелене), права пара виграшів (зелене); програші — приглушено
    left_win = ["дальність", "крізь стіни"]
    left_lose = ["велика антена", "повільно"]
    right_win = ["мала антена", "швидко"]
    right_lose = ["мала дальність", "лише пряма видимість"]
    ly = ax_y + 70
    for i, s in enumerate(left_win):
        parts.append(plus(x0 + 6, ly + i * 30))
        parts.append(text(x0 + 22, ly + i * 30 + 5, s, 13, FIELD, "start", bold=True))
    for i, s in enumerate(left_lose):
        parts.append(minus(x0 + 6, ly + 70 + i * 30))
        parts.append(text(x0 + 22, ly + 70 + i * 30 + 5, s, 12, MUTED, "start"))
    for i, s in enumerate(right_win):
        parts.append(plus(x1 - 6, ly + i * 30))
        parts.append(text(x1 - 22, ly + i * 30 + 5, s, 13, FIELD, "end", bold=True))
    for i, s in enumerate(right_lose):
        parts.append(minus(x1 - 6, ly + 70 + i * 30))
        parts.append(text(x1 - 22, ly + 70 + i * 30 + 5, s, 12, MUTED, "end"))
    # підпис-суть посередині
    box = fitbox(W / 2 - 150, ax_y + 78, 300, 56,
                 "Немає «найкращої» частоти:\n«далеко й крізь усе» ПРОТИ «швидко й компактно».",
                 size=12, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK)
    parts.append(box)
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *parts,
           title="Один рух по осі частоти міняє всі чотири властивості разом")


# ── Фігура 2: дальність і проникність — низька f «бере» далі й крізь стіни ─────
# Дві сцени з передавачем біля перешкоди (стіни). Зліва низька частота: широке
# розпливчасте коло огинає стіну й проходить крізь неї. Справа висока частота:
# вузький промінь по прямій, за стіною — чітка тінь.
def fig_range():
    W, H = 700, 360
    parts = []
    for px0, title2, low in [(40, "низька частота", True), (380, "висока частота", False)]:
        cx, cy = px0 + 60, 200
        wall_x = px0 + 175
        # передавач
        parts.append(circle(cx, cy, 8, fill=INK, stroke=INK, sw=1))
        parts.append(text(cx, cy + 26, "передавач", 10, MUTED, "middle"))
        # стіна
        parts.append(rect(wall_x, 120, 12, 160, fill="#d7dbe0", stroke=LINE, sw=1.2, rx=2))
        parts.append(text(wall_x + 6, 110, "стіна", 10, MUTED, "middle"))
        if low:
            # широкі дуги, що огинають і проходять крізь
            for r in (55, 95, 135):
                parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                             'stroke="%s" stroke-width="2" opacity="0.55"/>' % (cx, cy, r, NEG))
            # проходить крізь стіну (приглушена дуга за стіною)
            parts.append('<circle cx="%.1f" cy="%.1f" r="170" fill="none" stroke="%s" '
                         'stroke-width="2" stroke-dasharray="5 5" opacity="0.5"/>' % (cx, cy, NEG))
            parts.append(mtext(cx + 205, cy + 64, ["огинає й", "проходить крізь"], 11, NEG, "middle"))
        else:
            # вузький промінь-ліхтарик прямо, за стіною — тінь
            parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" opacity="0.18"/>'
                         % (cx, cy, wall_x, cy - 40, wall_x, cy + 40, POS))
            parts.append(line(cx, cy, wall_x, cy, color=POS, sw=2.6))
            # тінь за стіною
            parts.append(rect(wall_x + 12, 150, 120, 100, fill="#1a1a1a", stroke="none", sw=0, rx=4))
            parts.append('<rect x="%.1f" y="150" width="120" height="100" fill="#1a1a1a" opacity="0.12"/>'
                         % (wall_x + 12))
            parts.append(mtext(wall_x + 72, 205, ["чітка", "тінь"], 11, INK, "middle"))
        parts.append(text(px0 + 150, 320, title2, 12, INK, "middle", bold=True))
    render(os.path.join(IMG, "range.svg"), W, H, *parts,
           title="Низька частота огинає й проходить; висока — лише пряма видимість")


# ── Фігура 3: швидкість даних — однаковий відсоток спектра дає різну смугу ─────
# Дві осі частоти: біля 100 МГц і біля 5 ГГц. На кожній — однакова частка (1%),
# але абсолютна смуга різна: 1 МГц проти 50 МГц. Видно, чому високо = більше місця.
def fig_datarate():
    W, H = 700, 360
    parts = []
    rows = [(110, "біля 100 МГц", "1 МГц", 30, NEG),
            (240, "біля 5 ГГц", "50 МГц", 230, POS)]
    bx0 = 150
    full = 380
    for y, label, abs_bw, w, col in rows:
        parts.append(text(bx0 - 16, y + 18, label, 12, INK, "end", bold=True))
        # повна доступна шкала (тонка)
        parts.append(rect(bx0, y, full, 30, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
        # виділена частка 1%
        parts.append(rect(bx0, y, w, 30, fill="#eafaf1" if col == POS else "#eaf0fd",
                          stroke=col, sw=2.2, rx=4))
        parts.append(text(bx0 + max(w, 40) + 10, y + 20, "1% = " + abs_bw, 12, col, "start", bold=True))
    # стрілка-порівняння
    parts.append(text(W / 2, 320,
                      "однакова частка спектра — у 50 разів більша абсолютна смуга → більше даних",
                      12, MUTED, "middle"))
    render(os.path.join(IMG, "datarate.svg"), W, H, *parts,
           title="На вищій частоті той самий відсоток спектра дає ширшу смугу")


# ── Фігура 4: розмір антени ∝ довжина хвилі ───────────────────────────────────
# Чотири вертикальні «вуса» антен спадної довжини для 433/868/2400/5000 МГц.
# Поряд — обчислена чвертьхвильова довжина. Видно, як антена тане з частотою.
def fig_antenna():
    W, H = 700, 360
    parts = []
    bands = [("433 МГц", 17.3, "≈17 см"), ("868 МГц", 8.6, "≈9 см"),
             ("2.4 ГГц", 3.1, "≈3 см"), ("5 ГГц", 1.5, "≈1.5 см")]
    base_y = 290
    x = 130
    step = 150
    scale = 11.0  # px на см
    for name, cm, lab in bands:
        h = cm * scale
        parts.append(line(x, base_y, x, base_y - h, color=POS, sw=3.4))
        parts.append(circle(x, base_y, 5, fill=INK, stroke=INK, sw=1))  # точка кріплення
        parts.append(text(x, base_y + 22, name, 12, INK, "middle", bold=True))
        parts.append(text(x, base_y - h - 10, lab, 11, MUTED, "middle"))
        x += step
    parts.append(line(90, base_y, x - step + 40, base_y, color=MUTED, sw=1.3))
    parts.append(text(W / 2, 330,
                      "що вища частота, то коротша антена — тим легше сховати її в чіп",
                      12, MUTED, "middle"))
    render(os.path.join(IMG, "antenna.svg"), W, H, *parts,
           title="Антена сумірна з довжиною хвилі: висока частота — крихітна антена")


# ── Фігура 5: карта діапазонів — вертикальна шкала від низів до верхів ─────────
# Знизу вгору росте частота. Кожен діапазон — рядок: назва, частота, характер.
# Ліворуч стрілки «дальність ↓», праворуч «дані ↑», щоб видно було наскрізний тренд.
def fig_bandmap():
    W, H = 700, 470
    parts = []
    rows = [
        ("AM/MF ~1 МГц", "величезна дальність, крихта даних (радіо)"),
        ("HF/КХ 3–30 МГц", "відбивається від іоносфери — дістає глобально"),
        ("VHF/UHF", "FM, ТБ, рації — помірно"),
        ("433/868/915 МГц", "далеко й крізь стіни, мало даних (LoRa)"),
        ("2.4 ГГц", "помірна дальність і дані (Wi-Fi, BT)"),
        ("5 ГГц", "багато даних, мала дальність"),
        ("мм-хвилі 24–60 ГГц", "гігабіти лише в межах кімнати (5G, радари)"),
    ]
    bx, bw = 150, 360
    rh, gap = 44, 8
    y = 70
    n = len(rows)
    for i, (band, desc) in enumerate(rows):
        # колір від низької (синя) до високої (червона)
        t = i / (n - 1)
        col = NEG if t < 0.34 else (FIELD if t < 0.67 else POS)
        yy = y + i * (rh + gap)
        parts.append(rect(bx, yy, bw, rh, fill="#f4f6f8", stroke=col, sw=2.0, rx=5))
        parts.append(text(bx + 10, yy + 19, band, 12, col, "start", bold=True))
        parts.append(text(bx + 10, yy + 36, desc, 10.5, INK, "start"))
    top, bot = y, y + n * (rh + gap) - gap
    # вісь частоти праворуч
    parts.append(arrow(bx + bw + 28, bot, bx + bw + 28, top, color=INK, sw=2.0))
    parts.append(mtext(bx + bw + 44, (top + bot) / 2, ["частота", "↑"], 11, INK, "start"))
    # тренди ліворуч
    parts.append(arrow(bx - 30, top, bx - 30, bot, color=NEG, sw=2.0))
    parts.append(mtext(bx - 46, (top + bot) / 2, ["дальність", "↑"], 11, NEG, "end"))
    render(os.path.join(IMG, "bandmap.svg"), W, H, *parts,
           title="Карта діапазонів: угору за частотою — менше дальності, більше даних")


# ── Фігура 6: обирай за потребою — від потреби до діапазону ────────────────────
# Чотири картки-потреби зліва, стрілка, відповідний діапазон справа.
def fig_pick():
    W, H = 700, 360
    parts = []
    pairs = [
        ("далеко + мало даних\n(давач у полі)", "433/868 МГц (LoRa)", FIELD),
        ("крізь стіни в домі,\nпомірні дані", "2.4 ГГц (Wi-Fi/BT)", NEG),
        ("багато даних,\nпристрій поруч", "5 ГГц", POS),
        ("глобально, без\nінфраструктури", "HF або супутник", MUTED),
    ]
    y = 60
    lh = 68
    lx, lw = 60, 230
    rx, rw = 410, 230
    for need, band, col in pairs:
        parts.append(fitbox(lx, y, lw, 54, need, size=11, fill="#f4f6f8", stroke=LINE, sw=1.4, color=INK))
        parts.append(arrow(lx + lw + 8, y + 27, rx - 8, y + 27, color=col, sw=2.2))
        parts.append(fitbox(rx, y, rw, 54, band, size=12,
                            fill="#eafaf1" if col == FIELD else ("#eaf0fd" if col == NEG else
                                  ("#fdecea" if col == POS else "#eef2f7")),
                            stroke=col, sw=2.0, color=INK, bold=True))
        y += lh
    render(os.path.join(IMG, "pick.svg"), W, H, *parts,
           title="Спершу потреба — частота випливає сама")


# ── Фігура 7: єдиний континуум — одна вісь, два краї ───────────────────────────
# Горизонтальна вісь частоти; під кожним краєм — повний «портрет» (4 риси).
def fig_continuum():
    W, H = 700, 320
    parts = []
    ax_y = 110
    x0, x1 = 110, 590
    # градієнтна вісь (імітуємо сегментами синій→червоний)
    segs = 24
    for i in range(segs):
        xa = x0 + (x1 - x0) * i / segs
        xb = x0 + (x1 - x0) * (i + 1) / segs
        t = i / (segs - 1)
        # лінійна суміш NEG→POS
        col = NEG if t < 0.5 else POS
        parts.append(line(xa, ax_y, xb, ax_y, color=col, sw=5.0))
    parts.append(arrow(x1, ax_y, x1 + 26, ax_y, color=POS, sw=3.0))
    parts.append(text((x0 + x1) / 2, ax_y - 20, "частота", 13, INK, "middle", bold=True))
    # лівий портрет
    parts.append(mtext(x0, ax_y + 40, ["низька f", "далеко", "повільно", "велика антена", "крізь стіни"],
                       12, NEG, "start", lh=1.45))
    parts.append(mtext(x1, ax_y + 40, ["висока f", "близько", "швидко", "крихітна антена", "лише пряма видимість"],
                       12, POS, "end", lh=1.45))
    render(os.path.join(IMG, "continuum.svg"), W, H, *parts,
           title="Усе радіо — рух по одній осі: кожен крок міняє чотири риси разом")


fig_tradeoff()
fig_range()
fig_datarate()
fig_antenna()
fig_bandmap()
fig_pick()
fig_continuum()
print("Done. SVG in", IMG)
