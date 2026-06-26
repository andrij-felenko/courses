# -*- coding: utf-8 -*-
"""Фігури до теми «Керування життєвим циклом дисплея».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # застереження / тепле виділення
COLD = "#5b6b7a"   # «холодні», знеструмлені стани
ACT  = "#1f78b4"   # активний показ
LOW  = "#27ae60"   # економний стан (сон)


# ── 1. Кільце життєвого циклу: стани й переходи ──────────────────────────────
def fig_states():
    W, H = 780, 470
    f = [text(W / 2, 30, "Життєвий цикл дисплея — це машина станів", size=16, bold=True)]

    # вузли: (cx, cy, назва, підпис-енергія, колір)
    nodes = {
        "off":   (130, 250, "OFF",      "нуль",          COLD),
        "pwr":   (300, 110, "POWER-UP", "сплеск",        GOLD),
        "init":  (520, 110, "INIT",     "сплеск",        GOLD),
        "on":    (650, 250, "ACTIVE",   "повний показ",  ACT),
        "idle":  (520, 390, "IDLE",     "приглушено",    LOW),
        "sleep": (300, 390, "SLEEP",    "майже нуль",    LOW),
    }
    order = ["off", "pwr", "init", "on", "idle", "sleep"]
    R = 46
    for k in order:
        cx, cy, name, en, col = nodes[k]
        f.append(circle(cx, cy, R, fill="#ffffff", stroke=col, sw=2.4))
        f.append(text(cx, cy - 4, name, size=12.5, color=col, bold=True))
        f.append(text(cx, cy + 13, en, size=9, color=MUTED, italic=True))

    def edge(a, b, label, lx, ly, col=INK, dash=None):
        ax, ay = nodes[a][0], nodes[a][1]
        bx, by = nodes[b][0], nodes[b][1]
        import math
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        f.append(arrow(ax + ux * R, ay + uy * R, bx - ux * R, by - uy * R, color=col, sw=2.0))
        if label:
            f.append(text(lx, ly, label, size=9.5, color=col, italic=True))

    edge("off", "pwr",  "увімкнули живлення", 205, 168)
    edge("pwr", "init", "скидання → команди", 410, 96)
    edge("init", "on",  "sleep-out, display-on", 640, 162)
    edge("on", "idle",  "бездіяльність",      640, 330, col=LOW)
    edge("idle", "sleep", "час вийшов",        410, 404, col=LOW)
    edge("sleep", "on", "дотик / подія → wake", 470, 300, col=ACT)

    # аварійний/плановий вихід донизу в OFF
    edge("sleep", "off", "вимкнення", 195, 330, col=COLD, dash="5,4")
    f.append(textbox(W / 2, 448,
                     "Ключ: між сусідніми кадрами екран не «вмикають заново» — він живе у станах, "
                     "і код лише переводить його з одного в інший",
                     size=10.5, pad=8, fill="#fff8e6", stroke=GOLD, color=INK)[0])
    render(os.path.join(IMG, "states.svg"), W, H, *f)


# ── 2. Послідовність увімкнення в часі: порядок вирішує ───────────────────────
def fig_powerup():
    W, H = 800, 420
    f = [text(W / 2, 28, "Холодний старт у часі: порядок не можна переплутати", size=16, bold=True)]

    x0, x1 = 150, 760            # вісь часу
    rows = [
        ("VDD (логіка)",  ACT),
        ("RESX (скидання)", GOLD),
        ("команди INIT",  INK),
        ("sleep-out → 120 мс", GOLD),
        ("display-on",    ACT),
        ("підсвітка (ramp)", LOW),
    ]
    y0 = 70
    dy = 52
    for i, (name, col) in enumerate(rows):
        y = y0 + i * dy
        f.append(text(x0 - 12, y + 4, name, size=11, color=col, anchor="end"))
        f.append(line(x0, y + 14, x1, y + 14, color="#e3e7ea", sw=1))  # базова лінія

    # часові мітки (відносні)
    def X(t):  # t у 0..1
        return x0 + (x1 - x0) * t

    # 1. VDD піднімається й тримається
    yV = y0 + 0 * dy
    f.append(line(X(0.04), yV + 14, X(0.10), yV - 18, color=ACT, sw=2.4))
    f.append(line(X(0.10), yV - 18, x1, yV - 18, color=ACT, sw=2.4))
    f.append(text(X(0.11), yV - 24, "стабільна", size=8.5, color=ACT, anchor="start", italic=True))

    # 2. RESX: тримаємо низько, потім відпускаємо після VDD; пауза >120мс
    yR = y0 + 1 * dy
    f.append(line(X(0.0), yR - 18, X(0.16), yR - 18, color=GOLD, sw=2.4))      # утримання low
    f.append(line(X(0.16), yR - 18, X(0.16), yR + 14, color=GOLD, sw=2.4))     # фронт
    f.append(line(X(0.16), yR + 14, x1, yR + 14, color=GOLD, sw=2.4))          # відпущено high
    f.append(text(X(0.0), yR + 30, "тримаємо в скиданні, поки VDD не вляжеться", size=8.5,
                  color=GOLD, anchor="start", italic=True))

    # 3. команди init — пачка коротких імпульсів після reset recovery
    yC = y0 + 2 * dy
    cx = X(0.30)
    for k in range(7):
        xx = cx + k * 14
        f.append(line(xx, yC + 14, xx, yC - 12, color=INK, sw=2.0))
    f.append(text(cx, yC + 30, "конфігурація регістрів", size=8.5, color=INK, anchor="start", italic=True))

    # 4. sleep-out і обовʼязкова пауза 120 мс
    yS = y0 + 3 * dy
    f.append(line(X(0.46), yS + 14, X(0.46), yS - 12, color=GOLD, sw=2.4))     # команда
    f.append(line(X(0.46), yS - 12, X(0.74), yS - 12, color=GOLD, sw=1.8, dash="4,4"))  # очікування
    f.append(line(X(0.74), yS - 12, X(0.74), yS + 14, color=GOLD, sw=2.4))
    f.append(text(X(0.60), yS - 18, "чекаємо: насоси напруги встановлюються", size=8.5,
                  color=GOLD, anchor="middle", italic=True))

    # 5. display-on тільки ПІСЛЯ паузи
    yD = y0 + 4 * dy
    f.append(line(X(0.76), yD + 14, X(0.76), yD - 12, color=ACT, sw=2.4))
    f.append(line(X(0.76), yD - 12, x1, yD - 12, color=ACT, sw=2.4))
    f.append(text(X(0.77), yD - 18, "тепер видно картинку", size=8.5, color=ACT,
                  anchor="start", italic=True))

    # 6. підсвітка наростає плавно ОСТАННЬОЮ
    yB = y0 + 5 * dy
    f.append(line(X(0.80), yB + 14, X(0.92), yB - 16, color=LOW, sw=2.4))      # ramp
    f.append(line(X(0.92), yB - 16, x1, yB - 16, color=LOW, sw=2.4))
    f.append(text(X(0.80), yB + 30, "вмикаємо ОСТАННЬОЮ — щоб не блимнути сміттям", size=8.5,
                  color=LOW, anchor="start", italic=True))

    # вертикальні «такти» — звʼязок порядку
    for t, lab in [(0.16, "reset↑"), (0.46, "sleep-out"), (0.76, "display-on")]:
        f.append(line(X(t), 56, X(t), y0 + 6 * dy - 18, color="#cfd5da", sw=1, dash="2,4"))

    render(os.path.join(IMG, "powerup.svg"), W, H, *f)


# ── 3. Профіль струму за сесію: ціна забути про сон ───────────────────────────
def fig_power():
    W, H = 780, 360
    f = [text(W / 2, 28, "Струм за сесію: де ховається весь заряд", size=16, bold=True)]

    ox, oy = 90, 285           # початок осей
    ax, ay = 740, 60           # кінці
    f.append(arrow(ox, oy, ax, oy, color=INK, sw=1.8))     # час →
    f.append(arrow(ox, oy, ox, ay, color=INK, sw=1.8))     # струм ↑
    f.append(text(ax, oy + 22, "час", size=11, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 12, ay + 4, "струм", size=11, color=MUTED, anchor="end", italic=True))

    base = oy
    lvl_active = oy - 150
    lvl_idle   = oy - 80
    lvl_sleep  = oy - 12
    lvl_spike  = oy - 205

    def X(t):
        return ox + (740 - ox) * t

    # суцільна лінія профілю: спайк init → активний → idle → сон → wake → активний
    pts = [
        (0.00, base), (0.03, base),
        (0.03, lvl_spike), (0.10, lvl_spike),         # init-сплеск (насоси, перший залив кадру)
        (0.10, lvl_active), (0.34, lvl_active),        # активний показ
        (0.34, lvl_idle), (0.46, lvl_idle),            # idle: підсвітку приглушили
        (0.46, lvl_sleep), (0.74, lvl_sleep),          # SLEEP: майже нуль
        (0.74, lvl_active), (0.92, lvl_active),         # wake → знову активний
        (0.92, lvl_idle), (1.0, lvl_idle),
    ]
    d = "M %.1f %.1f" % (X(pts[0][0]), pts[0][1])
    for t, y in pts[1:]:
        d += " L %.1f %.1f" % (X(t), y)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, ACT))

    # рівні-пунктири й підписи
    for y, lab, col in [(lvl_spike, "сплеск старту", GOLD),
                        (lvl_active, "активний показ", ACT),
                        (lvl_idle, "приглушено", LOW),
                        (lvl_sleep, "сон ≈ 0", LOW)]:
        f.append(line(ox, y, X(0.02), y, color=col, sw=1))
        f.append(text(ox - 10, y + 4, lab, size=8.5, color=col, anchor="end"))

    # підписи фаз під віссю
    for t, lab in [(0.06, "INIT"), (0.22, "ACTIVE"), (0.40, "IDLE"),
                   (0.60, "SLEEP"), (0.83, "ACTIVE")]:
        f.append(text(X(t), oy + 18, lab, size=9, color=MUTED))

    # «привид» — те, що було б, якби забули приспати (горизонталь на active)
    gy = lvl_active
    f.append(line(X(0.46), gy, X(0.74), gy, color=POS, sw=1.8, dash="6,4"))
    f.append(text(X(0.60), gy - 8, "забули sleep-in → 4–6 мА весь час", size=8.5,
                  color=POS, anchor="middle", italic=True))
    # заштрихована різниця (втрачений заряд)
    f.append(rect(X(0.46), gy, X(0.74) - X(0.46), lvl_sleep - gy, fill="#fdecea", stroke="none", rx=0))

    f.append(textbox(W / 2, 338,
                     "Площа під кривою — це заряд. Найбільший виграш дає не яскравість, "
                     "а чесний сон: приспана панель майже не їсть",
                     size=10, pad=7, fill="#eafaf0", stroke=LOW, color=INK)[0])
    render(os.path.join(IMG, "power.svg"), W, H, *f)


# ── 4. Плановий сон проти аварійного обриву ──────────────────────────────────
def fig_shutdown():
    W, H = 780, 340
    f = [text(W / 2, 28, "Два виходи зі стану ACTIVE — і вони протилежні", size=16, bold=True)]

    # центральний вузол
    f.append(circle(W / 2, 86, 44, fill="#ffffff", stroke=ACT, sw=2.4))
    f.append(text(W / 2, 82, "ACTIVE", size=12.5, color=ACT, bold=True))
    f.append(text(W / 2, 99, "показ", size=9, color=MUTED, italic=True))

    # ліва гілка: плановий сон (є час)
    lx = 215
    f.append(arrow(W / 2 - 40, 110, lx + 70, 150, color=LOW, sw=2.0))
    f.append(text(330, 128, "є час", size=9.5, color=LOW, italic=True))
    steps_l = ["display-off", "sleep-in (0x10)", "підсвітку погасити", "МК у глибокий сон"]
    yy = 168
    for s in steps_l:
        f.append(textbox(lx, yy, s, size=10.5, pad=7, fill="#eafaf0", stroke=LOW, color=INK)[0])
        yy += 40
    f.append(text(lx, 145, "ПЛАНОВИЙ СОН — по черзі, акуратно", size=10.5, color=LOW, bold=True))

    # права гілка: аварія (часу катма)
    rx = 565
    f.append(arrow(W / 2 + 40, 110, rx - 70, 150, color=POS, sw=2.0))
    f.append(text(450, 128, "напруга падає", size=9.5, color=POS, italic=True))
    steps_r = ["встигнути зберегти стан", "перестати писати в Flash",
               "решта — байдуже: гасне саме", "брудний кадр нікого не турбує"]
    yy = 168
    for s in steps_r:
        f.append(textbox(rx, yy, s, size=10.5, pad=7, fill="#fdecea", stroke=POS, color=INK)[0])
        yy += 40
    f.append(text(rx, 145, "АВАРІЙНИЙ ОБРИВ — лише найважливіше", size=10.5, color=POS, bold=True))

    render(os.path.join(IMG, "shutdown.svg"), W, H, *f)


if __name__ == "__main__":
    fig_states()
    fig_powerup()
    fig_power()
    fig_shutdown()
    print("OK: figures written to", IMG)
