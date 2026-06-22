# -*- coding: utf-8 -*-
"""Фігури до теми «Компаратор» та її компонентної вставки «LM393-клас».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def opamp_tri(cx, cy, w=90, h=96, plus_top=False):
    """Трикутник підсилювача вістрям праворуч. Вхідні вузли — на лівій грані,
    вихід — на вістрі. Повертає (svg, in_top, in_bot, out) із координатами виводів."""
    left = cx - w / 2
    tipx = cx + w / 2
    top, bot = cy - h / 2, cy + h / 2
    body = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
            'fill="#fbfbfb" stroke="%s" stroke-width="1.8"/>'
            % (left, top, left, bot, tipx, cy, INK))
    in_top = (left, cy - h / 4)
    in_bot = (left, cy + h / 4)
    s_top = ("+", POS) if plus_top else ("−", NEG)
    s_bot = ("−", NEG) if plus_top else ("+", POS)
    body += text(left + 14, in_top[1] + 5, s_top[0], size=15, color=s_top[1], bold=True)
    body += text(left + 14, in_bot[1] + 5, s_bot[0], size=14, color=s_bot[1], bold=True)
    return body, in_top, in_bot, (tipx, cy)


def ground(x, y):
    return (line(x - 13, y, x + 13, y, color=INK, sw=2) +
            line(x - 8, y + 5, x + 8, y + 5, color=INK, sw=1.6) +
            line(x - 4, y + 10, x + 4, y + 10, color=INK, sw=1.3))


def npn(cx, cy):
    """Маленький NPN-символ у колі: база ліворуч, колектор угору, емітер униз."""
    out = [circle(cx, cy, 22, fill="#fff", stroke=INK, sw=1.6)]
    out.append(line(cx - 6, cy - 12, cx - 6, cy + 12, color=INK, sw=2.4))   # база-планка
    out.append(line(cx - 18, cy, cx - 6, cy, color=INK, sw=1.6))            # вивід бази
    out.append(line(cx - 6, cy - 6, cx + 12, cy - 16, color=INK, sw=1.6))   # до колектора
    out.append(line(cx - 6, cy + 6, cx + 12, cy + 16, color=INK, sw=1.6))   # до емітера
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
               % (cx + 4, cy + 9, cx + 12, cy + 16, cx + 2, cy + 16, INK))
    return "".join(out)


# ══ Фігури теми ══════════════════════════════════════════════════════════════

# ── 1. Базовий компаратор: котра напруга більша ──────────────────────────────
def fig_comparator_basic():
    W, H = 700, 300
    tri, it, ib, out = opamp_tri(285, 150, plus_top=False)
    f = [text(W / 2, 30, "Компаратор: котра напруга більша?", size=16, bold=True),
         tri]
    # входи: V₊ (верхній — мінус намальований зверху? plus_top=False → top=«−»)
    # тримаємо: top = «−» = V₋, bot = «+» = V₊  → підпишемо лінії відповідно
    f.append(line(it[0], it[1], 150, it[1], color=INK, sw=2))
    f.append(text(144, it[1] + 4, "V₋", size=11, color=NEG, bold=True, anchor="end"))
    f.append(line(ib[0], ib[1], 150, ib[1], color=INK, sw=2))
    f.append(text(144, ib[1] + 4, "V₊", size=11, color=POS, bold=True, anchor="end"))
    # вихід
    f.append(line(out[0], out[1], out[0] + 75, out[1], color=INK, sw=2))
    f.append(text(out[0] + 80, out[1] + 4, "вихід", size=10, anchor="start", bold=True))
    # панель правил
    f.append(rect(440, 96, 220, 110, fill="#fbfbfb", stroke="#c9d3dc", sw=1.3, rx=8))
    f.append(text(550, 124, "V₊ > V₋  →", size=12, bold=True))
    f.append(text(550, 144, "вихід ВИСОКИЙ ▲", size=12, color=FIELD, bold=True))
    f.append(line(460, 160, 640, 160, color="#e4e4e4", sw=1))
    f.append(text(550, 180, "V₊ < V₋  →", size=12, bold=True))
    f.append(text(550, 200, "вихід НИЗЬКИЙ ▼", size=12, color=NEG, bold=True))
    f.append(text(W / 2, 282,
                  "Вихід — повністю на одній із рейок, залежно лише від того, "
                  "котрий вхід переважив. Відповідь «так/ні».",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "comparator-basic.svg"), W, H, *f)


# ── 2. Розімкнений ОП: велетенське A робить криву сходинкою ───────────────────
def fig_open_loop():
    W, H = 720, 440
    f = [text(W / 2, 30, "Велетенське підсилення робить передатну криву сходинкою",
              size=16, bold=True)]
    ox, oy = 360, 235          # центр координат
    half_w = 250
    hi_y, lo_y = 80, 390       # рейки
    f.append(line(ox - half_w, oy, ox + half_w, oy, color=INK, sw=2))
    f.append(arrow(ox + half_w, oy, ox + half_w + 16, oy, color=INK, sw=2))
    f.append(text(ox + half_w + 4, oy + 22, "V₊ − V₋", size=13, anchor="end"))
    f.append(line(ox, lo_y, ox, hi_y - 14, color=INK, sw=2))
    f.append(arrow(ox, hi_y - 14, ox, hi_y - 30, color=INK, sw=2))
    f.append(text(ox - 12, hi_y - 18, "Vвих", size=13, anchor="end"))
    f.append(line(ox - half_w, hi_y, ox + half_w, hi_y, color=MUTED, sw=1, dash="4,4"))
    f.append(line(ox - half_w, lo_y, ox + half_w, lo_y, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox - half_w + 4, hi_y - 8, "+Vрейки  («1»)", size=12, color=MUTED, anchor="start"))
    f.append(text(ox - half_w + 4, lo_y + 18, "−Vрейки  («0»)", size=12, color=MUTED, anchor="start"))
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="3"/>'
             % (ox - half_w, lo_y, ox - 6, lo_y, ox + 6, hi_y, ox + half_w, hi_y, POS))
    f.append(text(ox + 12, oy - 30, "лінійна зона —", size=12, color=NEG, anchor="start"))
    f.append(text(ox + 12, oy - 12, "лише мікровольти завширшки", size=12, color=NEG, anchor="start"))
    f.append(text(ox - half_w / 2, lo_y - 14, "V₋ більший → вихід унизу", size=12, color=INK))
    f.append(text(ox + half_w / 2, hi_y + 22, "V₊ більший → вихід угорі", size=12, color=INK))
    f.append(text(W / 2, 426,
                  "Між рейками — майже вертикальна стінка: трохи переважив один вхід — "
                  "і вихід уже на рейці", size=12, color=INK))
    return render(os.path.join(IMG, "open-loop.svg"), W, H, *f)


# ── 3. Поріг: плавний сигнал → двійкове «вище/нижче» ──────────────────────────
def fig_threshold():
    W, H = 720, 430
    f = [text(W / 2, 30, "Поріг: плавний сигнал → двійкове «вище/нижче»",
              size=16, bold=True)]
    ox, ax_w = 80, 560
    base1, amp = 150, 60
    f.append(line(ox, base1, ox + ax_w, base1, color=MUTED, sw=1))
    f.append(text(ox - 8, base1 - amp - 4, "Vвх", size=12, anchor="end"))
    th_y = base1 - 18
    f.append(line(ox, th_y, ox + ax_w, th_y, color=NEG, sw=1.6, dash="6,4"))
    f.append(text(ox + ax_w, th_y - 6, "поріг", size=12, color=NEG, anchor="end"))
    pts = []
    for i in range(0, ax_w + 1, 6):
        t = i / ax_w
        y = base1 - amp * math.sin(math.pi * t) * 1.15
        pts.append("%.1f %.1f" % (ox + i, y))
    f.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" L".join(pts), POS))

    def cross_x(rising):
        s = 18.0 / (amp * 1.15)
        t = math.asin(s) / math.pi
        if not rising:
            t = 1 - t
        return ox + t * ax_w
    cx1, cx2 = cross_x(True), cross_x(False)
    for cx in (cx1, cx2):
        f.append(line(cx, base1 - amp - 10, cx, base1 + 150, color=MUTED, sw=1, dash="3,4"))
        f.append(circle(cx, th_y, 4, fill=POS, stroke=POS, sw=1))
    base2 = 360
    lo, hi = base2, base2 - 70
    f.append(text(ox - 8, hi - 4, "Vвих", size=12, anchor="end"))
    f.append(text(ox + ax_w + 2, lo + 4, "«0»", size=11, color=MUTED, anchor="start"))
    f.append(text(ox + ax_w + 2, hi + 4, "«1»", size=11, color=MUTED, anchor="start"))
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f L%.0f %.0f" '
             'fill="none" stroke="%s" stroke-width="2.8"/>'
             % (ox, lo, cx1, lo, cx1, hi, cx2, hi, cx2, lo, ox + ax_w, lo, NEG))
    f.append(text((cx1 + cx2) / 2, hi - 10, "сигнал вище порога", size=11, color=NEG))
    f.append(text(ox + (cx1 - ox) / 2, lo + 18, "нижче", size=11, color=MUTED))
    f.append(text(W / 2, 414,
                  "Доки сигнал вище порога — вихід «1»; нижче — «0». "
                  "Аналогова крива стала чітким рішенням", size=12, color=INK))
    return render(os.path.join(IMG, "threshold.svg"), W, H, *f)


# ── 4. Детектор темряви: фоторезистор у дільнику проти порога ─────────────────
def fig_light_detector():
    W, H = 700, 300
    f = [text(W / 2, 28, "Детектор темряви: фоторезистор проти порога → ліхтар",
              size=14, bold=True)]
    # дільник ліворуч: +5В → фоторезистор → вузол → 20к → земля
    dx = 70
    f.append(line(dx, 66, dx, 92, color=POS, sw=2))
    f.append(text(dx, 60, "+5В", size=10, color=POS, bold=True))
    f.append(rect(dx - 14, 92, 28, 38, fill="#fff", stroke="#e0a32e", sw=1.6, rx=0))
    f.append(text(dx + 24, 108, "фоторез.", size=10, anchor="start", bold=True))
    node_y = 146
    f.append(line(dx, 130, dx, node_y, color=INK, sw=2))
    f.append(circle(dx, node_y, 3, fill=INK, stroke=INK, sw=2))
    f.append(rect(dx - 14, node_y, 28, 38, fill="#fff", stroke=INK, sw=1.4, rx=0))
    f.append(text(dx + 24, node_y + 22, "20к", size=10, anchor="start"))
    f.append(line(dx, node_y + 38, dx, 206, color=INK, sw=2))
    f.append(ground(dx, 206))
    # компаратор
    tri, it, ib, out = opamp_tri(300, 150, plus_top=False)
    f.append(tri)
    # сигнал із вузла дільника на «+» (нижній вхід ib)
    f.append(line(dx, node_y, 210, node_y, color=INK, sw=2))
    f.append(line(210, node_y, 210, ib[1], color=INK, sw=2))
    f.append(line(210, ib[1], it[0], ib[1], color=INK, sw=2))
    f.append(text(150, node_y - 8, "сигнал", size=10, color=MUTED))
    # поріг 2.5 В на «−» (верхній вхід it)
    f.append(line(it[0], it[1], 235, it[1], color=INK, sw=2))
    f.append(text(229, it[1] + 3, "2.5В", size=10, color=POS, bold=True, anchor="end"))
    f.append(text(205, it[1] - 13, "поріг", size=9, color=MUTED))
    # вихід → резистор → ліхтар → земля
    f.append(line(out[0], out[1], 392, out[1], color=INK, sw=2))
    f.append(rect(392, out[1] - 10, 30, 20, fill="#fff", stroke=INK, sw=1.3, rx=0))
    f.append(text(407, out[1] + 4, "R", size=10))
    f.append(line(422, out[1], 452, out[1], color=INK, sw=2))
    # ліхтар-діод
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#fff3b0" '
             'stroke="%s" stroke-width="1.4"/>' % (452, out[1] - 10, 452, out[1] + 10, 470, out[1], INK))
    f.append(line(470, out[1] - 10, 470, out[1] + 10, color=INK, sw=2))
    f.append(text(502, out[1] - 14, "ліхтар", size=10, anchor="start", bold=True))
    f.append(line(470, out[1], 502, out[1], color=INK, sw=2))
    f.append(line(502, out[1], 502, out[1] + 30, color=INK, sw=2))
    f.append(ground(502, out[1] + 30))
    f.append(text(W / 2, 288,
                  "Стемніло → опір фоторезистора зріс → напруга впала нижче 2.5 В → "
                  "вихід перекинувся → ліхтар світить.", size=9, color=MUTED, italic=True))
    return render(os.path.join(IMG, "light-detector.svg"), W, H, *f)


# ── 5. Галерея застосувань компаратора ───────────────────────────────────────
def fig_applications():
    W, H = 720, 360
    f = [text(W / 2, 30, "Скрізь, де треба порівняти рівні: те саме «вище/нижче»",
              size=16, bold=True)]
    cards = [
        ("світло / темрява", "фоторезистор проти порога"),
        ("поріг температури", "термістор → вентилятор"),
        ("розряд батареї", "дільник проти опорного"),
        ("перехід через нуль", "синус → прямокутник"),
        ("сигналізація", "перевищило межу → тривога"),
        ("вхід АЦП", "драбина порогів → код"),
    ]
    cw, ch, gx, gy = 200, 96, 24, 24
    x0, y0 = 36, 70
    for i, (ttl, sub) in enumerate(cards):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + gx)
        y = y0 + row * (ch + gy)
        f.append(rect(x, y, cw, ch, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=10))
        f.append(text(x + cw / 2, y + 36, ttl, size=14, bold=True))
        f.append(text(x + cw / 2, y + 64, sub, size=11, color=MUTED))
    f.append(text(W / 2, 344,
                  "Кожен випадок — той самий компаратор: один вхід — сигнал, другий — поріг.",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "applications.svg"), W, H, *f)


# ── 6. Брязкіт: шум біля єдиного порога розгойдує вихід ───────────────────────
def fig_chatter():
    W, H = 720, 420
    f = [text(W / 2, 30, "Брязкіт: шум біля єдиного порога розгойдує вихід",
              size=16, bold=True)]
    ox, ax_w = 80, 560
    base1, amp = 150, 36
    f.append(line(ox, base1, ox + ax_w, base1, color=MUTED, sw=1))
    f.append(text(ox - 8, base1 - amp - 18, "Vвх", size=12, anchor="end"))
    th_y = base1
    f.append(line(ox, th_y, ox + ax_w, th_y, color=NEG, sw=1.6, dash="6,4"))
    f.append(text(ox + ax_w, th_y - 6, "поріг", size=12, color=NEG, anchor="end"))
    # сигнал, що завис на порозі, з дрібним шумом — багато перетинів у середині
    import random
    random.seed(7)
    pts = []
    crossings = []
    prev_sign = None
    for i in range(0, ax_w + 1, 4):
        t = i / ax_w
        slow = -amp * 0.7 * math.cos(math.pi * t)       # повільний дрейф крізь поріг
        noise = (random.random() - 0.5) * 16 if 0.30 < t < 0.70 else (random.random() - 0.5) * 3
        v = slow + noise
        y = base1 - v
        pts.append("%.1f %.1f" % (ox + i, y))
        sign = v >= 0
        if prev_sign is not None and sign != prev_sign:
            crossings.append(ox + i)
        prev_sign = sign
    f.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" L".join(pts), POS))
    # цифровий вихід — перекидається на кожному перетині
    base2 = 350
    lo, hi = base2, base2 - 70
    f.append(text(ox - 8, hi - 4, "Vвих", size=12, anchor="end"))
    f.append(text(ox + ax_w + 2, lo + 4, "«0»", size=11, color=MUTED, anchor="start"))
    f.append(text(ox + ax_w + 2, hi + 4, "«1»", size=11, color=MUTED, anchor="start"))
    seg = [ox] + crossings + [ox + ax_w]
    state_lo = True   # старт унизу (сигнал під порогом)
    dpath = ["M%.0f %.0f" % (ox, lo)]
    cur_y = lo
    for k in range(1, len(seg)):
        x = seg[k]
        dpath.append("L%.0f %.0f" % (x, cur_y))     # горизонталь до перекиду
        cur_y = hi if cur_y == lo else lo            # перекид
        dpath.append("L%.0f %.0f" % (x, cur_y))      # вертикаль
    dpath.append("L%.0f %.0f" % (ox + ax_w, cur_y))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(dpath), NEG))
    f.append(text(ox + ax_w / 2, hi - 12, "вихід скажено тремтить", size=11, color=NEG))
    f.append(text(W / 2, 404,
                  "Сигнал завис біля єдиного порога; шум совгає його туди-сюди — "
                  "вихід перекидається десятки разів. Лікує гістерезис: два пороги.",
                  size=12, color=INK))
    return render(os.path.join(IMG, "chatter-problem.svg"), W, H, *f)


# ══ Фігури компонентної вставки (LM393-клас) ═════════════════════════════════

# ── 7. Відкритий колектор: транзистор лише стягує вниз ───────────────────────
def fig_open_collector():
    W, H = 720, 420
    f = [text(W / 2, 30, "Відкритий колектор: вихід уміє лише СТЯГУВАТИ вниз",
              size=16, bold=True)]
    f.append(rect(60, 80, 250, 290, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=10))
    f.append(text(185, 104, "усередині компаратора", size=12, color=MUTED, bold=True))
    out_y, out_x = 230, 310
    tx, ty = 185, 250
    f.append(npn(tx, ty))
    f.append(text(tx, ty + 40, "вихідний NPN", size=11, color=MUTED))
    f.append(line(tx + 12, ty - 16, tx + 12, out_y, color=LINE, sw=1.8))
    f.append(line(tx + 12, out_y, out_x, out_y, color=LINE, sw=1.8))
    f.append(line(tx + 12, ty + 16, tx + 12, 350, color=LINE, sw=1.8))
    f.append(ground(tx + 12, 350))
    f.append(text(tx + 12, 380, "GND", size=11, color=MUTED))
    f.append(line(120, ty, tx - 18, ty, color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(116, ty + 4, "рішення", size=10, color=MUTED, anchor="end"))
    f.append(line(out_x, out_y, 470, out_y, color=LINE, sw=2))
    f.append(circle(470, out_y, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(out_x + 6, out_y - 12, "OUT", size=12, bold=True, anchor="start"))
    pull_x = 470
    f.append(line(pull_x, out_y, pull_x, 150, color=LINE, sw=1.8))
    rb, _, _ = textbox(pull_x, 175, "Rпідт", size=12, fill="#fff7e6", stroke="#b8860b", min_w=40)
    f.append(rb)
    f.append(line(pull_x, 150, pull_x, 120, color=POS, sw=2))
    f.append(text(pull_x, 110, "+Vпідт (3.3 чи 5 В)", size=12, color=POS, bold=True))
    f.append(line(pull_x, out_y, 560, out_y, color=LINE, sw=2))
    f.append(arrow(560, out_y, 600, out_y, color=LINE, sw=2))
    b, _, _ = textbox(652, out_y, "до логіки\n/ MCU", size=12, fill="#eef2fc", stroke=NEG)
    f.append(b)
    f.append(text(W / 2, 408,
                  "«0»: транзистор відкритий, садить OUT на землю    •    "
                  "«1»: транзистор закритий, OUT підтягує резистор", size=12, color=INK))
    return render(os.path.join(IMG, "open-collector.svg"), W, H, *f)


# ── 8. Монтажне «І»: кілька відкритих колекторів на одній підтяжці ───────────
def fig_wired_and():
    W, H = 720, 430
    f = [text(W / 2, 30, "Монтажне «І»: один тягне вниз — уся лінія внизу",
              size=16, bold=True)]
    line_x, top_y, bot_y = 470, 90, 360
    f.append(line(line_x, top_y, line_x, 70, color=POS, sw=2))
    f.append(text(line_x, 58, "+Vпідт", size=12, color=POS, bold=True))
    rb, _, _ = textbox(line_x, 110, "Rпідт", size=12, fill="#fff7e6", stroke="#b8860b", min_w=44)
    f.append(rb)
    f.append(line(line_x, 132, line_x, bot_y, color=INK, sw=2.4))
    f.append(text(line_x + 14, (132 + bot_y) / 2, "спільна лінія", size=12, bold=True, anchor="start"))
    f.append(text(line_x + 14, (132 + bot_y) / 2 + 18, "(«1» лише коли ВСІ мовчать)",
                  size=11, color=MUTED, anchor="start"))
    ys = [165, 245, 325]
    labels = ["комп. A", "комп. B", "комп. C"]
    states = ["закр.", "ВІДКР.", "закр."]
    colors = [MUTED, POS, MUTED]
    for y, lab, st, col in zip(ys, labels, states, colors):
        f.append(rect(70, y - 26, 150, 52, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
        f.append(text(145, y - 4, lab, size=12, bold=True))
        f.append(text(145, y + 14, "транз. " + st, size=11, color=col))
        f.append(line(220, y, line_x, y, color=col, sw=2 if col == POS else 1.6))
        f.append(circle(line_x, y, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(text(300, ys[1] - 12, "тягне ↓", size=11, color=POS, bold=True))
    f.append(line(line_x, bot_y, 560, bot_y, color=INK, sw=2))
    f.append(arrow(560, bot_y, 600, bot_y, color=INK, sw=2))
    b, _, _ = textbox(652, bot_y, "1 вхід\nMCU", size=12, fill="#eef2fc", stroke=NEG)
    f.append(b)
    f.append(text(W / 2, 414,
                  "Будь-який спрацьований вихід садить спільний провід на землю — "
                  "логіка без жодного вентиля", size=12, color=INK))
    return render(os.path.join(IMG, "wired-and.svg"), W, H, *f)


# ── 9. Зовнішній гістерезис: додатний зв'язок розсуває поріг на два ──────────
def fig_external_hysteresis():
    W, H = 720, 400
    f = [text(W / 2, 30, "Зовнішній гістерезис: один поріг → два, із «мертвою зоною»",
              size=16, bold=True)]
    ox, oy = 110, 320
    axw, axh = 480, 210
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    f.append(arrow(ox + axw, oy, ox + axw + 16, oy, color=INK, sw=2))
    f.append(text(ox + axw + 6, oy + 22, "Vвх", size=12, anchor="end"))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    f.append(arrow(ox, oy - axh, ox, oy - axh - 16, color=INK, sw=2))
    f.append(text(ox - 10, oy - axh - 6, "Vвих", size=12, anchor="end"))
    hi_y, lo_y = oy - axh + 20, oy - 20
    f.append(text(ox - 10, hi_y + 4, "«1»", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 10, lo_y + 4, "«0»", size=12, color=MUTED, anchor="end"))
    th_lo, th_hi = ox + 200, ox + 300
    # мертва зона (під осями — малюємо першою, щоб лінії були поверх)
    f.append(rect(th_lo, oy - axh, th_hi - th_lo, axh, fill="#eef6ef", stroke="none", sw=0, rx=0))
    f.append(text((th_lo + th_hi) / 2, oy - axh - 4, "мертва зона", size=11, color=FIELD, bold=True))
    f.append(line(th_lo, oy, th_lo, oy - axh, color=NEG, sw=1.2, dash="5,4"))
    f.append(line(th_hi, oy, th_hi, oy - axh, color=POS, sw=1.2, dash="5,4"))
    f.append(text(th_lo, oy + 22, "Vн", size=12, color=NEG, bold=True))
    f.append(text(th_hi, oy + 22, "Vв", size=12, color=POS, bold=True))
    f.append(line(ox + 8, lo_y, th_hi, lo_y, color=INK, sw=2.6))
    f.append(arrow(th_hi, lo_y, th_hi, hi_y, color=POS, sw=2.6))
    f.append(line(th_hi, hi_y, ox + axw - 10, hi_y, color=INK, sw=2.6))
    f.append(line(th_lo, hi_y, th_hi, hi_y, color=INK, sw=2.6))
    f.append(arrow(th_lo, hi_y, th_lo, lo_y, color=NEG, sw=2.6))
    f.append(line(ox + 8, lo_y, th_lo, lo_y, color=INK, sw=2.6))
    f.append(text((th_lo + th_hi) / 2, hi_y - 10, "→ вгору тільки на Vв", size=10, color=POS))
    f.append(text((th_lo + th_hi) / 2, lo_y + 18, "← вниз тільки на Vн", size=10, color=NEG))
    return render(os.path.join(IMG, "external-hysteresis.svg"), W, H, *f)


if __name__ == "__main__":
    fig_comparator_basic()
    fig_open_loop()
    fig_threshold()
    fig_light_detector()
    fig_applications()
    fig_chatter()
    fig_open_collector()
    fig_wired_and()
    fig_external_hysteresis()
    print("OK: figures ->", IMG)
