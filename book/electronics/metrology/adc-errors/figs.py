# -*- coding: utf-8 -*-
"""Фігури до статті «Похибки АЦП» (adc-errors.md).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Шість фігур самої статті:
  1) ideal-vs-real.svg — реальна крива проти ідеальної прямої (offset/gain/INL);
  2) offset-gain.svg    — дві «лінійні» похибки поряд (зсув і масштаб);
  3) dnl.svg            — щаблі різної ширини, пропущений код (DNL);
  4) inl.svg            — плавний вигин від прямої, макс. INL;
  5) esp32-curve.svg    — реальна крива АЦП ESP32 із зонами «глухо/середина/насич.»;
  6) calibration.svg    — 1/2/багато точок калібрування.

Плюс одна фігура вставки proj-two-point-cal.md (решта фігур вставок поки зроблені
стороннім інструментом):
  7) calib-nvs-flow.svg — два контури: разовий запис калібрування в NVS і щоразове
                          читання+застосування поправки (перенесено сюди зі svgkit).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#caa24a"   # локальний жовтий акцент (точки «2 точки», підпис gain)


def polyline(pts, color=INK, sw=2.0, dash=None):
    """Сирий <polyline> (svgkit не має хелпера): pts — список (x,y)."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    """Сирий <polygon> (svgkit не має хелпера): pts — список (x,y). Для ромба рішення."""
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (s, fill, stroke, sw))


# ── 1. Ідеальна пряма проти реальної кривої ─────────────────────────────────
def fig_ideal_vs_real():
    W, H = 920, 420
    f = [text(W / 2, 28, "Реальний АЦП відхиляється від ідеальної прямої", size=18, bold=True),
         text(W / 2, 50, "ідеал — рівна лінія «напруга → код»; справжній має зсув, нахил і вигин",
              size=10, color=MUTED, italic=True)]

    # осі
    x0, y0 = 120, 360            # початок координат
    xr, yt = 780, 100           # правий/верхній край корисного поля
    f.append(arrow(x0, y0, x0, 88, color=INK, sw=2))
    f.append(arrow(x0, y0, 794, y0, color=INK, sw=2))
    f.append(text(110, 98, "код", size=11, bold=True, anchor="end"))
    f.append(text(786, 384, "Vin", size=11, bold=True))

    # ідеальна пряма (сіра пунктирна)
    f.append(line(x0, y0, xr, yt, color=MUTED, sw=2, dash="7 4"))
    f.append(text(661, 126, "ідеал", size=11, color=MUTED, bold=True, anchor="start"))

    # реальна крива: зсув нуля + менший нахил + легкий вигин (S-подібний)
    y_off = 339.2               # код при 0 В (зсув угору від нуля осі)
    y_top = 120.8               # верх реальної кривої (нахил < 1 → не дотягує до yt)
    pts = []
    n = 100
    for i in range(n + 1):
        t = i / n
        x = x0 + (xr - x0) * t
        base = y_off + (y_top - y_off) * t            # пряма зсув→верх
        bow = -16 * math.sin(math.pi * t)             # вигин усередині (вгору на графіку = −y)
        pts.append((x, base + bow))
    f.append(polyline(pts, color=POS, sw=2.8))
    f.append(text(526, 219, "реальний", size=11, color=POS, bold=True, anchor="start"))

    # три підписані дефекти
    f.append(circle(x0, y_off, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(128, 333, "зсув нуля (offset)", size=9, color=POS, bold=True, anchor="start"))
    f.append(text(774, 113, "нахил ≠ 1 (gain)", size=9, color=POS, bold=True, anchor="end"))
    f.append(text(458, 206, "вигин (INL)", size=9, color=POS, bold=True, anchor="start"))

    # рамка-висновок
    f.append(fitbox(150, 374, 620, 26,
                    "Ці відхилення СИСТЕМНІ (повторювані) — отже, їх можна виміряти й виправити.",
                    size=10, bold=True, fill="#fff6e0", stroke=GOLD, sw=1.2))
    return render(os.path.join(IMG, "ideal-vs-real.svg"), W, H, *f)


# ── 2. Зсув нуля та похибка масштабу (дві панелі) ───────────────────────────
def fig_offset_gain():
    W, H = 940, 380
    f = [text(W / 2, 28, "Дві «лінійні» похибки: зсув нуля та похибка масштабу", size=17, bold=True),
         text(W / 2, 50, "обидві лишають криву прямою — тому їх виправляє двоточкове калібрування",
              size=10, color=MUTED, italic=True)]

    def panel(ox):
        g = []
        y0, yt = 320, 110
        g.append(arrow(ox, y0, ox, 98, color=INK, sw=2))
        g.append(arrow(ox, y0, ox + 324, y0, color=INK, sw=2))
        g.append(text(ox - 10, 108, "код", size=11, bold=True, anchor="end"))
        g.append(text(ox + 316, 344, "Vin", size=11, bold=True))
        g.append(line(ox, y0, ox + 310, yt, color=MUTED, sw=1.8, dash="6 4"))
        return g

    # ── ліва панель: зсув нуля (пряма паралельно піднята) ──
    f += panel(120)
    f.append(polyline([(120, 282.2), (374.2, 110)], color=POS, sw=2.6))
    f.append(circle(120, 282.2, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(128, 276, "код ≠ 0 при 0 В", size=9, color=POS, bold=True, anchor="start"))
    f.append(text(275, 104, "вся пряма зсунена вгору", size=9))
    f.append(text(275, 92, "Зсув нуля (offset)", size=11, color=POS, bold=True))

    # ── права панель: похибка масштабу (менший нахил) ──
    f += panel(560)
    f.append(polyline([(560, 320), (870, 164.6)], color=POS, sw=2.6))
    f.append(text(715, 112, "нахил не той — повну", size=9))
    f.append(text(715, 126, "шкалу досягнуто не там", size=9))
    f.append(text(715, 92, "Похибка масштабу (gain)", size=11, color=GOLD, bold=True))

    # рамка-висновок
    f.append(fitbox(160, 340, 620, 30,
                    "Зсув — додати/відняти константу; масштаб — домножити. Дві точки задають і те, й те.",
                    size=10, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.3))
    return render(os.path.join(IMG, "offset-gain.svg"), W, H, *f)


# ── 3. DNL: щаблі різної ширини, пропущений код ─────────────────────────────
def fig_dnl():
    W, H = 920, 380
    f = [text(W / 2, 28, "DNL: щаблі різної ширини, аж до пропущеного коду", size=17, bold=True),
         text(W / 2, 50,
              "диференціальна нелінійність — відхилення ширини кожного щабля від рівного 1 LSB",
              size=10, color=MUTED, italic=True)]

    x0, y0 = 120, 330
    f.append(arrow(x0, y0, x0, 98, color=INK, sw=2))
    f.append(arrow(x0, y0, 814, y0, color=INK, sw=2))
    f.append(text(110, 108, "код", size=11, bold=True, anchor="end"))
    f.append(text(806, 354, "Vin", size=11, bold=True))

    # підпис «пропущений код!» над вертикальним щаблем
    f.append(text(494, 212, "пропущений код!", size=9, color=POS, bold=True))
    f.append(circle(494, 220, 3.5, fill=POS, stroke=POS, sw=0))

    # східчаста синя лінія — щаблі різної ширини, один вертикальний (пропуск)
    steps = [
        (120.0, 330.0), (205.0, 330.0),     # вузький рівень (вузький щабель)
        (205.0, 302.5), (341.0, 302.5),     # широкий щабель
        (341.0, 275.0), (392.0, 275.0),
        (392.0, 247.5), (494.0, 247.5),
        (494.0, 220.0), (494.0, 220.0),     # вертикальний щабель (пропущений код)
        (494.0, 192.5), (613.0, 192.5),
        (613.0, 165.0), (689.5, 165.0),
        (689.5, 137.5), (800.0, 137.5),
        (800.0, 110.0),
    ]
    f.append(polyline(steps, color=NEG, sw=2.4))
    # ідеальна пунктирна пряма поверх
    f.append(line(x0, y0, 800, 110, color=MUTED, sw=1.4, dash="5 4"))

    f.append(text(132, 322, "вузький щабель", size=9, color=FIELD, anchor="start"))
    f.append(text(270, 260, "широкий щабель", size=9, color=GOLD, anchor="start"))

    # рамка-висновок (саме «= −1 LSB»)
    f.append(fitbox(160, 346, 600, 26,
                    "Якщо щабель «зник» (DNL = −1 LSB), такий код не з'явиться НІКОЛИ.",
                    size=10, bold=True, fill="#fff6e0", stroke=GOLD, sw=1.2))
    return render(os.path.join(IMG, "dnl.svg"), W, H, *f)


# ── 4. INL: плавний вигин від прямої ────────────────────────────────────────
def fig_inl():
    W, H = 900, 380
    f = [text(W / 2, 28, "INL: крива «вигинається» від ідеальної прямої", size=18, bold=True),
         text(W / 2, 50, "інтегральна нелінійність — накопичене відхилення від прямої лінії",
              size=10, color=MUTED, italic=True)]

    x0, y0 = 120, 330
    xr, yt = 770, 100
    f.append(arrow(x0, y0, x0, 88, color=INK, sw=2))
    f.append(arrow(x0, y0, 784, y0, color=INK, sw=2))
    f.append(text(110, 98, "код", size=11, bold=True, anchor="end"))
    f.append(text(776, 354, "Vin", size=11, bold=True))

    # ідеальна пряма
    f.append(line(x0, y0, xr, yt, color=MUTED, sw=1.8, dash="6 4"))
    f.append(text(640, 132, "ідеал", size=10, color=MUTED, bold=True, anchor="start"))

    # реальна крива: збігається на кінцях, найбільше відхилення посередині (вигин угору)
    pts = []
    n = 100
    for i in range(n + 1):
        t = i / n
        x = x0 + (xr - x0) * t
        base = y0 + (yt - y0) * t
        bow = -27.6 * math.sin(math.pi * t)           # макс. ≈ 27.6 px у середині
        pts.append((x, base + bow))
    f.append(polyline(pts, color=POS, sw=2.6))

    # зелена вертикальна стрілка-розмір «макс. INL» (≈ середина)
    xa = 445.0
    y_ideal = y0 + (yt - y0) * (xa - x0) / (xr - x0)   # пряма в xa
    y_curve = y_ideal - 27.6 * math.sin(math.pi * (xa - x0) / (xr - x0))
    f.append(line(xa, y_ideal, xa, y_curve, color=FIELD, sw=2))
    f.append(line(xa - 5, y_ideal, xa + 5, y_ideal, color=FIELD, sw=2))
    f.append(line(xa - 5, y_curve, xa + 5, y_curve, color=FIELD, sw=2))
    f.append(text(453, 201, "макс. INL", size=9, color=FIELD, bold=True, anchor="start"))

    # рамка-висновок
    f.append(fitbox(150, 346, 600, 26,
                    "INL не виправити прямою — потрібна крива поправки (багатоточкове калібрування).",
                    size=9, bold=True, fill="#e9eefb", stroke=NEG, sw=1.2))
    return render(os.path.join(IMG, "inl.svg"), W, H, *f)


# ── 5. Реальна крива АЦП ESP32 ──────────────────────────────────────────────
def fig_esp32():
    W, H = 920, 400
    f = [text(W / 2, 28, "АЦП ESP32: помітно нелінійний, особливо по краях", size=17, bold=True),
         text(W / 2, 50,
              "біля 0 і біля максимуму крива «завалюється»; надійна — лише середина діапазону",
              size=10, color=MUTED, italic=True)]

    x0, y0 = 110, 340
    xr, yt = 800, 110
    # фонові зони ДО осей/кривої (щоб лінії були поверх)
    # межі зон: «глухо» зліва, «надійна середина», «насич.» справа
    xL = 192.8      # кінець глухої зони
    xR = 731.0      # початок насичення
    f.append(rect(xL, yt, xr - xL, y0 - yt, fill="#eef6ef", stroke="none", sw=0, rx=0))
    f.append(rect(x0, yt, xL - x0, y0 - yt, fill="#fbecec", stroke="none", sw=0, rx=0))
    f.append(rect(xR, yt, xr - xR, y0 - yt, fill="#fbecec", stroke="none", sw=0, rx=0))

    # осі
    f.append(arrow(x0, y0, x0, 98, color=INK, sw=2))
    f.append(arrow(x0, y0, 814, y0, color=INK, sw=2))
    f.append(text(100, 108, "код", size=11, bold=True, anchor="end"))
    f.append(text(806, 364, "Vin", size=11, bold=True))

    # ідеальна пунктирна пряма
    f.append(line(x0, y0, xr, yt, color=MUTED, sw=1.6, dash="6 4"))

    # реальна крива: плеската біля 0, лінійна посередині, насичення вгорі
    pts = []
    n = 100
    full = y0 - yt
    for i in range(n + 1):
        t = i / n
        x = x0 + (xr - x0) * t
        # форма: повільний старт (t^? деад-зона), лінійна, насичення
        if t < 0.12:
            frac = 0.04 * (t / 0.12)                       # майже плеско «глухо»
        elif t > 0.90:
            frac = 0.965 + 0.035 * ((t - 0.90) / 0.10)     # майже плеско «насич.»
        else:
            # лінійна вставка між кінцями плато
            frac = 0.04 + (0.965 - 0.04) * (t - 0.12) / (0.90 - 0.12)
        pts.append((x, y0 - full * frac))
    f.append(polyline(pts, color=POS, sw=2.8))

    # підписи зон
    f.append(text((xL + xR) / 2, 128, "надійна середина", size=10, color=FIELD, bold=True))
    f.append(text((x0 + xL) / 2, 326, "глухо", size=9, color=POS, bold=True))
    f.append(text((xR + xr) / 2, 140, "насич.", size=9, color=POS, bold=True))

    # рамка-висновок
    f.append(fitbox(160, 356, 600, 28,
                    "Тримай сигнал у середині шкали; крайні ~0.1 В і верхівку не довіряй. + розкид між чипами.",
                    size=9, bold=True, fill="#fff6e0", stroke=GOLD, sw=1.3))
    return render(os.path.join(IMG, "esp32-curve.svg"), W, H, *f)


# ── 6. Калібрування: 1 / 2 / багато точок (три панелі) ──────────────────────
def fig_calibration():
    W, H = 960, 380
    f = [text(W / 2, 28, "Калібрування: підігнати виміряну криву під істину", size=18, bold=True),
         text(W / 2, 50, "що більше відомих точок, то складніші похибки можна виправити",
              size=10, color=MUTED, italic=True)]

    def axes(ox):
        g = [arrow(ox, 310, ox, 108, color=INK, sw=2),
             arrow(ox, 310, ox + 224, 310, color=INK, sw=2),
             text(ox + 216, 334, "Vin", size=11, bold=True),
             line(ox, 310, ox + 210, 120, color=MUTED, sw=1.5, dash="5 4")]
        return g

    # ── панель 1: одна точка (лише зсув) ──
    f += axes(100)
    f.append(circle(205, 215, 4.5, fill=POS, stroke=POS, sw=0))
    f.append(text(205, 104, "1 точка", size=11, color=POS, bold=True))
    f.append(text(205, 330, "лише зсув", size=9))

    # ── панель 2: дві точки (зсув + масштаб) — жовті ──
    f += axes(390)
    f.append(circle(442.5, 262.5, 4.5, fill=GOLD, stroke=GOLD, sw=0))
    f.append(circle(568.5, 148.5, 4.5, fill=GOLD, stroke=GOLD, sw=0))
    f.append(text(495, 104, "2 точки", size=11, color=GOLD, bold=True))
    f.append(text(495, 330, "зсув + масштаб", size=9))

    # ── панель 3: багато точок (+ нелінійність) — зелені ──
    f += axes(680)
    for cx, cy in [(711.5, 281.5), (759.8, 237.8), (806.0, 196.0), (852.2, 154.2)]:
        f.append(circle(cx, cy, 4.5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(785, 104, "багато точок", size=11, color=FIELD, bold=True))
    f.append(text(785, 330, "+ нелінійність", size=9))

    # рамка-висновок
    f.append(fitbox(150, 348, 660, 26,
                    "Виміряли відомі напруги → знаєте поправку → виправляєте всі майбутні читання.",
                    size=10, bold=True, fill="#e9eefb", stroke=NEG, sw=1.2))
    return render(os.path.join(IMG, "calibration.svg"), W, H, *f)


# ── 7. (вставка proj-two-point-cal) Два контури калібрування з NVS ───────────
def fig_calib_nvs_flow():
    """Блок-схема вставки proj-two-point-cal.md: ліворуч — разове dev-калібрування
    із записом у NVS; праворуч — кожен старт читає поправку з NVS і застосовує її
    дешево в loop(). Рамки — лише через fitbox (текст гарантовано вкладається),
    полотно з запасом, тож svgcheck дає 0 зауважень."""
    W, H = 680, 500
    GREEN_F, BLUE_F, GOLD_F, RED_F = "#eef6ef", "#e9eefb", "#fff6e0", "#fdecea"

    f = [text(W / 2, 26, "Калібрування АЦП: запис у NVS раз, застосування щоразу",
              size=17, bold=True),
         text(W / 2, 46,
              "dev-сесія кладе поправку у флеш; кожен старт її читає, а loop() застосовує дешево",
              size=10, color=MUTED, italic=True),
         # вертикальний роздільник між двома контурами
         line(340, 58, 340, 486, color=MUTED, sw=1.2, dash="6 4")]

    # ── Лівий контур: DEV-калібрування (один раз) ──
    f.append(fitbox(40, 64, 260, 30, "DEV: калібрування (один раз)",
                    size=13, bold=True, fill=GOLD_F, stroke=GOLD, sw=2))
    left = ["Подати V_lo\n(точне джерело)",
            "analogRead → raw_lo\n(середнє N відліків)",
            "Ввести V_lo з Serial",
            "Повторити для\nV_hi / raw_hi",
            "Зібрати Calib\n{rawLo, rawHi, vLo, vHi}"]
    for i, s in enumerate(left):
        y = 108 + i * 66
        if i:
            f.append(arrow(170, y - 22, 170, y, color=INK))
        f.append(fitbox(50, y, 240, 44, s, size=12))
    # фінальний (зелений) крок — запис у флеш
    f.append(arrow(170, 416, 170, 438, color=INK))
    f.append(fitbox(50, 438, 240, 44, "saveCalib() → NVS\n(Preferences.putInt/putFloat)",
                    size=12, fill=GREEN_F, stroke=FIELD))

    # ── Правий контур: setup() при кожному старті ──
    f.append(fitbox(380, 64, 260, 30, "setup() — кожен старт",
                    size=13, bold=True, fill=BLUE_F, stroke=NEG, sw=2))
    f.append(fitbox(390, 108, 240, 44, "analogSetPinAttenuation\n(ADC_11db)", size=12))
    f.append(arrow(510, 152, 510, 174, color=INK))
    f.append(fitbox(390, 174, 240, 44, "loadCalib() ← NVS", size=12))

    # ромб рішення «є ключі?»
    f.append(arrow(510, 218, 510, 240, color=INK))
    f.append(polygon([(510, 240), (546, 262), (510, 284), (474, 262)]))
    f.append(text(510, 266, "є ключі?", size=11))

    # гілка «Так» → slope/offset у RAM
    f.append(arrow(510, 284, 510, 306, color=INK))
    f.append(text(518, 300, "Так", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(fitbox(390, 306, 240, 44, "slope/offset у RAM\n(дешево, без флешу)",
                    size=12, fill=GREEN_F, stroke=FIELD))

    # гілка «Ні» → fallback (сира заводська шкала)
    f.append(arrow(546, 262, 558, 262, color=POS))
    f.append(text(552, 255, "Ні", size=10, color=POS, bold=True))
    f.append(fitbox(558, 236, 116, 52, "fallback:\nсира шкала\n(raw·3.3/4095)",
                    size=11, fill=RED_F, stroke=POS))

    # ── loop(): застосування поправки щоразу ──
    f.append(arrow(510, 350, 510, 372, color=INK))
    f.append(fitbox(390, 372, 240, 28, "loop() — щоразу",
                    size=13, bold=True, fill=BLUE_F, stroke=NEG, sw=2))
    f.append(fitbox(390, 404, 240, 44, "raw = analogRead(CAL_PIN)\nv = applyCalib(cal, raw)",
                    size=12))

    return render(os.path.join(IMG, "calib-nvs-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ideal_vs_real()
    fig_offset_gain()
    fig_dnl()
    fig_inl()
    fig_esp32()
    fig_calibration()
    fig_calib_nvs_flow()
    print("OK:", IMG)
