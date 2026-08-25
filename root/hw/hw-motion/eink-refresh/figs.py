# -*- coding: utf-8 -*-
"""Фігури до теми «E-ink оновлення» та її історичної вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# локальні кольори, що доповнюють палітру svgkit
PAPER = "#eef2f6"   # тло «паперу» e-ink
DARK  = "#222a33"   # чорний піксель / частинка
COLD  = "#3a6ea5"   # холод
WARM  = "#c0392b"   # тепло


# ── speed: час одного оновлення на логарифмічній шкалі ────────────────────────
# Ідея: світло й заряд перемикаються миттєво, частинки пігменту повзуть —
# звідси розрив у тисячі разів між OLED/LCD та e-ink.

def fig_speed():
    W, H = 720, 280
    ox, oy = 70, 210          # початок осі
    aw = 600                  # довжина осі часу
    p = []

    # логарифмічна вісь часу: 1 мкс … 10 с (7 декад)
    decades = [("1 мкс", 0), ("10 мкс", 1), ("100 мкс", 2), ("1 мс", 3),
               ("10 мс", 4), ("100 мс", 5), ("1 с", 6), ("10 с", 7)]
    span = 7.0
    sx = aw / span
    p.append(arrow(ox, oy, ox + aw + 14, oy, color=INK, sw=1.6))
    for lab, d in decades:
        x = ox + d * sx
        p.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.2))
        p.append(text(x, oy + 20, lab, size=10, color=MUTED))
    p.append(text(ox + aw + 8, oy + 20, "час", size=11, color=INK, anchor="start", italic=True))

    # смуги діапазонів кожної технології
    def band(d0, d1, y, color, fill, label):
        x0, x1 = ox + d0 * sx, ox + d1 * sx
        out = rect(x0, y - 13, x1 - x0, 26, fill=fill, stroke=color, sw=1.6, rx=8)
        out += text((x0 + x1) / 2, y + 4, label, size=11.5, color=color, bold=True)
        return out

    p.append(band(0.0, 1.3, oy - 150, FIELD, "#eafaf0", "OLED  ~мкс"))
    p.append(band(2.7, 4.0, oy - 110, NEG, "#eaf0fd", "LCD  ~мс"))
    p.append(band(5.0, 7.0, oy - 70, POS, "#fdecea", "e-ink  частки секунди"))

    p.append(text(ox + aw / 2, oy + 52,
                  "світло й заряд — миттєво; тверда частинка крізь рідину — на порядки повільніше",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "speed.svg"), W, H, *p,
           title="Час одного оновлення пікселя (логарифмічна шкала)")


# ── waveform: послідовність імпульсів ±15 В, збалансована за зарядом ──────────
# Ідея: не одне «увімкнути», а серія поштовхів туди-сюди; площа «+» = площа «−»
# (DC-баланс), наприкінці 0 В — бістабільність тримає.

def fig_waveform():
    W, H = 720, 320
    ox, oy = 70, 165          # вісь t на рівні 0 В
    aw = 600
    amp = 70                  # піксельна висота для +15 В
    p = []

    # осі
    p.append(line(ox, oy - amp - 18, ox, oy + amp + 18, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + aw + 14, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 8, oy + 18, "час", size=11, color=INK, anchor="start", italic=True))
    p.append(text(ox - 10, oy - amp - 6, "+15 В", size=10, color=POS, anchor="end"))
    p.append(text(ox - 10, oy + amp + 12, "−15 В", size=10, color=NEG, anchor="end"))
    p.append(text(ox - 10, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    # послідовність рівнів (у частках amp): скидання-туди-сюди, тоді в стан, тоді 0
    # підібрано так, щоб сумарна площа «+» дорівнювала площі «−» (DC-баланс)
    seq = [(+1, 2), (-1, 2), (+1, 1), (-1, 3), (+1, 3), (0, 2)]
    unit = aw / sum(d for _, d in seq)
    x = ox
    pts = ["%.1f,%.1f" % (x, oy)]
    for lvl, dur in seq:
        y = oy - lvl * amp
        pts.append("%.1f,%.1f" % (x, y))
        x2 = x + dur * unit
        pts.append("%.1f,%.1f" % (x2, y))
        # затінити площу імпульсу
        if lvl != 0:
            fill = "#fdecea" if lvl > 0 else "#eaf0fd"
            p.append(rect(x, min(oy, y), x2 - x, abs(y - oy), fill=fill, stroke="none", sw=0, rx=0))
        x = x2
    pts.append("%.1f,%.1f" % (x, oy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), INK))

    # підписи зон
    p.append(text(ox + 1.5 * unit, oy - amp - 24, "скидання", size=10, color=MUTED))
    p.append(text(ox + 7.5 * unit, oy + amp + 28, "у новий стан", size=10, color=MUTED))
    p.append(text(x - 1 * unit, oy - 14, "0 В: тримається сам", size=10, color=FIELD, anchor="end"))
    p.append(text(ox + aw / 2, H - 18,
                  "площа «+» = площа «−» за цикл — збалансовано за зарядом, щоб не псувати капсули",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "waveform.svg"), W, H, *p,
           title="Хвилеформа одного переходу: серія імпульсів, а не одне ввімкнення")


# ── full-refresh: спалах інверсій, тоді чистий кадр ───────────────────────────
# Ідея: повне оновлення кілька разів інвертує весь екран (чорне↔біле),
# «перемішуючи» частинки, і лише тоді виставляє кадр — звідси блимання.

def _screen(x, y, w, h, kind):
    """Мала іконка екрана: 'black' | 'white' | 'frame' (текст «АБВ»)."""
    if kind == "black":
        return rect(x, y, w, h, fill=DARK, stroke=INK, sw=1.4, rx=4)
    if kind == "white":
        return rect(x, y, w, h, fill=BG, stroke=INK, sw=1.4, rx=4)
    out = rect(x, y, w, h, fill=PAPER, stroke=INK, sw=1.4, rx=4)
    out += text(x + w / 2, y + h / 2 + 6, "АБВ", size=15, color=DARK, bold=True)
    return out


def fig_full_refresh():
    W, H = 720, 250
    p = []
    y = 70
    sw_, sh = 78, 90
    gap = 30
    seq = [("black", "чорне"), ("white", "біле"), ("black", "чорне"),
           ("white", "біле"), ("frame", "кадр")]
    total = len(seq) * sw_ + (len(seq) - 1) * gap
    x = (W - total) / 2
    centers = []
    for i, (kind, lab) in enumerate(seq):
        p.append(_screen(x, y, sw_, sh, kind))
        col = WARM if kind == "frame" else MUTED
        p.append(text(x + sw_ / 2, y + sh + 22, lab, size=11, color=col,
                      bold=(kind == "frame")))
        centers.append(x + sw_)
        if i > 0:
            p.append(arrow(centers[i - 1] + 4, y + sh / 2, x - 6, y + sh / 2, color=INK, sw=1.7))
        x += sw_ + gap

    p.append(text(W / 2, y - 26,
                  "кілька інверсій усього екрана «перемішують» частинки до однорідности",
                  size=11.5, color=INK))
    p.append(text(W / 2, H - 16,
                  "найдовше й блимає — зате кадр без жодного сліду попереднього",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "full-refresh.svg"), W, H, *p,
           title="Повне оновлення: спалах інверсій, тоді чистий кадр")


# ── partial-ghost: швидко у вікні, та копиться привид ─────────────────────────
# Ідея: часткове оновлення чіпає лише вікно й пропускає скидання — швидко,
# але під новою цифрою лишається блідий слід старої, що міцнішає з кожним разом.

def fig_partial_ghost():
    W, H = 720, 280
    p = []
    y = 70
    sw_, sh = 96, 110
    gap = 46
    # три кадри: «12:00», «12:01», «12:02» з дедалі помітнішим привидом
    frames = [("12:00", 0), ("12:01", 1), ("12:02", 2)]
    total = len(frames) * sw_ + (len(frames) - 1) * gap
    x = (W - total) / 2
    centers = []
    for i, (txt, ghost) in enumerate(frames):
        p.append(rect(x, y, sw_, sh, fill=PAPER, stroke=INK, sw=1.5, rx=6))
        # привид попередніх цифр — щораз густіший
        ghosts = ["12:0%d" % (ghost - k - 1) for k in range(ghost)]
        for k, g in enumerate(ghosts):
            op = 0.10 + 0.10 * (ghost - k - 1) / max(1, ghost)
            p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="22" '
                     'fill="%s" fill-opacity="%.2f" text-anchor="middle" '
                     'font-weight="700">%s</text>'
                     % (x + sw_ / 2, y + sh / 2 + 8, FONT, DARK, op, g))
        # свіжа цифра
        p.append(text(x + sw_ / 2, y + sh / 2 + 8, txt, size=22, color=DARK, bold=True))
        centers.append(x + sw_)
        if i > 0:
            p.append(arrow(centers[i - 1] + 4, y + sh / 2, x - 6, y + sh / 2, color=INK, sw=1.7))
            p.append(text((centers[i - 1] + x) / 2, y + sh / 2 - 12, "часткове",
                          size=9.5, color=MUTED))
        x += sw_ + gap

    p.append(text(W / 2, y - 26,
                  "оновлюється лише вікно цифр, без спалаху — десятки мс, без блимання",
                  size=11.5, color=INK))
    p.append(text(W / 2, H - 16,
                  "платня: під новою цифрою проступають бліді сліди старих — привид копичиться",
                  size=11, color=POS, italic=True))

    render(os.path.join(OUT, "partial-ghost.svg"), W, H, *p,
           title="Часткове оновлення: швидко у вікні, та накопичує привид")


# ── temperature: час оновлення різко росте з холодом ──────────────────────────
# Ідея: рідина на холоді густішає → частинки повзуть ледь-ледь → оновлення в рази
# довше, а нижче нуля часто не вдається зовсім. Звідси LUT за температурою.

def fig_temperature():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 580, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 6, oy + 20, "°C", size=12, color=INK, anchor="start", italic=True))
    p.append(text(ox - 46, oy - ah - 2, "час\nоновлення", size=10.5, color=INK, anchor="start"))

    # вісь температур: −10 … +40
    tmin, tmax = -10.0, 40.0
    sx = aw / (tmax - tmin)
    for tc in range(-10, 41, 10):
        x = ox + (tc - tmin) * sx
        p.append(line(x, oy - 3, x, oy + 3, color=INK, sw=1.1))
        p.append(text(x, oy + 18, str(tc), size=10, color=MUTED))

    # позначка 0 °C — межа, нижче якої оновлення зривається
    xzero = ox + (0 - tmin) * sx
    p.append(line(xzero, oy, xzero, oy - ah, color=COLD, sw=1.2, dash="5 4"))
    p.append(text(xzero, oy - ah - 4, "0 °C", size=10, color=COLD))

    # крива: час оновлення ~ вʼязкість, що різко росте з холодом (експонента)
    pts = []
    for i in range(0, 301):
        tc = tmin + (tmax - tmin) * i / 300.0
        # нормований час: ~1 при 25°C, круто вгору на холоді
        val = math.exp(-0.11 * (tc - 25.0))
        h = min(ah, val * ah * 0.16)
        pts.append("%.1f,%.1f" % (ox + (tc - tmin) * sx, oy - h))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), WARM))

    # зона «нижче нуля — часто не оновлюється зовсім»
    p.append(rect(ox + 1, oy - ah, xzero - ox - 1, ah, fill="#eaf0fd", stroke="none", sw=0, rx=0))
    p.append(text((ox + xzero) / 2, oy - ah * 0.5, "нижче нуля —\nчасто не оновиться",
                  size=10.5, color=COLD))
    p.append(text(ox + (28 - tmin) * sx, oy - ah * 0.18, "у теплі — швидко",
                  size=10.5, color=WARM))

    p.append(text(ox + aw / 2, H - 14,
                  "густа рідина — мляві частинки; тому хвилеформу беруть під поточну температуру",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "temperature.svg"), W, H, *p,
           title="Час оновлення e-ink різко росте з холодом")


# ── driving: поділ праці хост ↔ модуль ────────────────────────────────────────
# Ідея: хост лише шле образ і команду по SPI; вибір хвилеформи за температурою,
# генерацію імпульсів і високу напругу бере на себе контролер у модулі.

def fig_driving():
    W, H = 720, 320
    p = []

    # хост ліворуч
    hx, hy, hw, hh = 40, 120, 150, 80
    p.append(rect(hx, hy, hw, hh, fill=FILL, stroke=INK, sw=1.6, rx=8))
    p.append(text(hx + hw / 2, hy + 30, "мікроконтролер", size=12.5, color=INK, bold=True))
    p.append(text(hx + hw / 2, hy + 52, "(хост)", size=11, color=MUTED))

    # рамка модуля праворуч
    mx, my, mw, mh = 300, 50, 380, 230
    p.append(rect(mx, my, mw, mh, fill="#fafcfe", stroke=NEG, sw=1.8, rx=12))
    p.append(text(mx + mw / 2, my + 22, "e-ink модуль", size=13, color=NEG, bold=True))

    # стрілка SPI: образ + команда
    p.append(arrow(hx + hw + 4, hy + hh / 2, mx - 6, hy + hh / 2, color=INK, sw=2.0))
    p.append(text((hx + hw + mx) / 2, hy + hh / 2 - 12, "SPI: образ", size=10.5, color=INK))
    p.append(text((hx + hw + mx) / 2, hy + hh / 2 + 18, "+ «онови»", size=10.5, color=INK))
    # лінія «готово» назад
    p.append(arrow(mx - 6, hy + hh + 18, hx + hw + 4, hy + hh + 18, color=FIELD, sw=1.7))
    p.append(text((hx + hw + mx) / 2, hy + hh + 14, "«готово»", size=10, color=FIELD))

    # нутрощі модуля — чотири блоки важкої роботи
    bx = mx + 24
    bw, bh = mw - 48, 36
    blocks = [
        ("контролер: генерує хвилеформи", "#eef4ff"),
        ("LUT за температурою  (термодавач)", "#eafaf0"),
        ("±15 В: зарядна помпа / перетворювач", "#fdecea"),
        ("драйвери рядків і стовпців панелі", FILL),
    ]
    by = my + 44
    for lab, fill in blocks:
        p.append(fitbox(bx, by, bw, bh, lab, size=11, fill=fill, stroke=INK, sw=1.3))
        by += bh + 12

    p.append(text(W / 2, H - 14,
                  "хост шле образ і команду; вибір хвилеформи, імпульси й висока напруга — на модулі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "driving.svg"), W, H, *p,
           title="Поділ праці: проста роль хоста, важка робота — у модулі")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури історичної вставки (hist-eink.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── mechanisms: Gyricon (кулька обертається) проти E Ink (частинки рухаються) ──

def fig_mechanisms():
    W, H = 720, 340
    p = []

    # ── ліворуч: Gyricon — двоколірна кулька повертається ──
    cxL = 190
    p.append(text(cxL, 56, "Gyricon (Xerox)", size=13.5, color=INK, bold=True))
    p.append(text(cxL, 76, "кулька в олії повертається", size=11, color=MUTED))
    # кишенька з кулькою
    pocket = rect(cxL - 70, 110, 140, 140, fill="#fff7e6", stroke=LINE, sw=1.5, rx=12)
    p.append(pocket)
    # двоколірна куля: верх білий до глядача, низ чорний
    r = 46
    cy = 180
    p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (cxL - r, cy, r, r, cxL + r, cy, BG, INK))
    p.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (cxL - r, cy, r, r, cxL + r, cy, DARK, INK))
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (cxL, cy, r, INK))
    # стрілка обертання
    p.append('<path d="M %.1f %.1f A 58 58 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (cxL + 58, cy - 12, cxL + 40, cy - 44, FIELD))
    p.append(text(cxL, 270, "білий бік / чорний бік", size=10.5, color=MUTED))

    # ── праворуч: E Ink — частинки рухаються в капсулі ──
    cxR = 530
    p.append(text(cxR, 56, "E Ink (MIT)", size=13.5, color=INK, bold=True))
    p.append(text(cxR, 76, "частинки в капсулі переміщаються", size=11, color=MUTED))
    cap = '<circle cx="%.1f" cy="180" r="70" fill="#eef4ff" stroke="%s" stroke-width="1.6"/>' % (cxR, LINE)
    p.append(cap)
    # білі частинки вгорі (до глядача), чорні внизу
    import random
    random.seed(7)
    for _ in range(14):
        a = random.uniform(0, 2 * math.pi)
        rad = random.uniform(0, 52)
        px, py = cxR + rad * math.cos(a), 180 + rad * math.sin(a)
        if py < 180:   # верх — білі
            p.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="1"/>' % (px, py, BG, INK))
        else:          # низ — чорні
            p.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="1"/>' % (px, py, DARK, INK))
    # поле (стрілки вгору/вниз)
    p.append(arrow(cxR + 88, 200, cxR + 88, 165, color=NEG, sw=1.8))
    p.append(text(cxR + 96, 188, "поле", size=10, color=NEG, anchor="start"))
    p.append(text(cxR, 270, "білі вгору / чорні вниз", size=10.5, color=MUTED))

    # розділювач і висновок
    p.append(line(360, 100, 360, 280, color="#dde3ea", sw=1.4, dash="4 4"))
    p.append(text(W / 2, 312, "обидва бістабільні й паперові на вигляд; у серію пішла капсула",
                  size=11.5, color=INK))

    render(os.path.join(OUT, "mechanisms.svg"), W, H, *p,
           title="Дві мрії про електронний папір: обертати кульку чи переміщати частинки")


# ── timeline: довга дорога електронного паперу від ідеї до Kindle ──────────────

def fig_timeline():
    W, H = 760, 360
    p = []
    ox, oy = 70, 120
    aw = 620
    p.append(arrow(ox - 10, oy, ox + aw + 14, oy, color=INK, sw=1.8))

    # віхи: (рік, підпис, нижче?, колір-акцент)
    miles = [
        (1973, "Ота, Matsushita:\nелектрофорез", True, MUTED, "застряг:\nзлипання"),
        (1974, "Шерідон, Xerox:\nGyricon", False, MUTED, "поклали\nна полицю"),
        (1997, "Коміскі/Альберт/\nДжейкобсон, MIT:\nмікрокапсула", True, WARM, "здогад\nспрацював"),
        (2007, "Amazon Kindle", False, FIELD, "товар\nу руках"),
    ]
    y0, y1 = 1970, 2010
    sx = aw / (y1 - y0)
    for yr, lab, below, col, note in miles:
        x = ox + (yr - y0) * sx
        p.append(circle(x, oy, 7, fill=col, stroke=INK, sw=1.6))
        p.append(text(x, oy - 14, str(yr), size=12, color=INK, bold=True))
        if below:
            ty = oy + 34
            p.append(line(x, oy + 7, x, ty - 8, color=col, sw=1.2))
            p.append(mtext(x, ty, lab, size=10.5, color=INK))
            p.append(mtext(x, ty + 58, note, size=9.5, color=col))
        else:
            ty = oy - 64
            p.append(line(x, oy - 7, x, ty + 30, color=col, sw=1.2))
            p.append(mtext(x, ty, lab, size=10.5, color=INK))
            p.append(mtext(x, ty - 30, note, size=9.5, color=col))

    p.append(text(W / 2, H - 18,
                  "ідея → перший «папір» → подолана фізична біда → продукт: естафета, не спалах",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Майже сорок років: від першої ідеї до читалки в кожних руках")


if __name__ == "__main__":
    fig_speed()
    fig_waveform()
    fig_full_refresh()
    fig_partial_ghost()
    fig_temperature()
    fig_driving()
    fig_mechanisms()
    fig_timeline()
    print("OK: 8 SVG -> img/")
