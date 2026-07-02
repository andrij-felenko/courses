# -*- coding: utf-8 -*-
"""Фігури теми «USB PD sink» (як пристрій безпечно бере живлення як стік).
  usb-pd-sink.md  →  sink-gate.svg  (три бар'єри: Rd → контракт → ключ VBUS)
                     vbus-timeline.svg  (напруга VBUS у часі: 5 В → контракт → 12 В)
  comp-pd-trigger.md → trigger-block.svg (блок-схема й розпіновка тригера)
                       trigger-nvm.svg   (список PDO у пам'яті з відкатом)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED   = "#c0392b"
BLUE  = "#2457d6"
GREEN = "#27ae60"
GOLD  = "#b8860b"


# ── Фігура 1: три бар'єри на шляху високої напруги до пристрою ──────────────
def fig_sink_gate():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 30, "Три бар'єри стіка: висока напруга доходить лише в кінці",
                  size=16, bold=True))

    # Роз'єм ліворуч
    f.append(rect(40, 150, 70, 150, fill="#fbfbf8", stroke=INK, sw=1.8))
    f.append(text(75, 140, "USB-C", size=11, bold=True))
    # піни
    f.append(circle(110, 180, 3.5, fill=RED, stroke=RED, sw=0))
    f.append(text(103, 184, "VBUS", size=8, color=RED, anchor="end", bold=True))
    f.append(circle(110, 225, 3.5, fill=GOLD, stroke=GOLD, sw=0))
    f.append(text(103, 229, "CC", size=8, color=GOLD, anchor="end", bold=True))
    f.append(circle(110, 270, 3.5, fill=INK, stroke=INK, sw=0))
    f.append(text(103, 274, "GND", size=8, color=INK, anchor="end", bold=True))

    # Бар'єр 1: Rd на CC
    b1, w1, h1 = textbox(230, 225, ["Бар'єр 1", "Rd = 5.1 кОм", "«я стік»"],
                         size=10, fill="#fff7e6", stroke=GOLD, color=INK, bold=True, pad=9)
    f.append(b1)
    f.append(line(110, 225, 230 - w1 / 2, 225, color=GOLD, sw=2))

    # Бар'єр 2: контракт PD (цифровий діалог по CC)
    b2, w2, h2 = textbox(420, 225, ["Бар'єр 2", "контракт PD", "по CC"],
                         size=10, fill="#eef8ef", stroke=GREEN, color=INK, bold=True, pad=9)
    f.append(b2)
    f.append(arrow(230 + w1 / 2, 225, 420 - w2 / 2, 225, color=GREEN, sw=2))
    f.append(text(325, 213, "діалог", size=8.5, color=GREEN, bold=True))

    # Бар'єр 3: ключ у лінії VBUS
    f.append(rect(360, 155, 80, 46, fill="#fdecea", stroke=RED, sw=1.8))
    f.append(text(400, 174, "Бар'єр 3", size=9.5, color=RED, bold=True))
    f.append(text(400, 190, "ключ VBUS", size=8.5, color=INK))

    # VBUS від роз'єму крізь ключ до пристрою
    f.append(line(110, 180, 360, 180, color=RED, sw=2.4))
    f.append(line(440, 180, 610, 180, color=RED, sw=2.4))

    # POWER_OK від контракту керує ключем
    f.append(line(420, 225 - h2 / 2, 420, 205, color=GREEN, sw=1.8, dash="4,3"))
    f.append(line(420, 205, 400, 205, color=GREEN, sw=1.8, dash="4,3"))
    f.append(line(400, 205, 400, 201, color=GREEN, sw=1.8, dash="4,3"))
    f.append(text(465, 218, "POWER_OK", size=8, color=GREEN, bold=True))

    # Пристрій праворуч
    f.append(rect(610, 150, 120, 70, fill="#eef3fb", stroke=BLUE, sw=1.8))
    f.append(text(670, 178, "пристрій", size=11.5, color=BLUE, bold=True))
    f.append(text(670, 196, "12 В по контракту", size=8, color=INK))

    # Підпис знизу — послідовність
    cap = ("Доки не пройдені всі три бар'єри, на ключі — розрив, а на пристрої — нуль вольтів. "
           "Rd лише представляє стіка; контракт домовляється про 12 В; і аж коли контракт дійсний, "
           "сигнал POWER_OK замикає ключ — тоді напруга доходить до навантаження.")
    f.append(fitbox(50, 330, 660, 66, cap, size=10, fill="#f6f6f6", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, "sink-gate.svg"), W, H, *f)


# ── Фігура 2: напруга VBUS у часі ──────────────────────────────────────────
def fig_vbus_timeline():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 28, "Напруга на VBUS у часі: 5 В за замовчуванням, 12 В — лише після контракту",
                  size=14, bold=True))

    # осі
    ox, oy = 90, 300           # початок координат
    ax_r = 700                 # правий край осі часу
    ax_t = 70                  # верх осі напруги
    f.append(line(ox, oy, ax_r, oy, color=INK, sw=1.6))          # час →
    f.append(line(ox, oy, ox, ax_t, color=INK, sw=1.6))          # напруга ↑
    f.append(text(ax_r, oy + 22, "час", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 12, ax_t + 4, "VBUS", size=10, color=MUTED, anchor="end"))

    # рівні напруги (0, 5, 12)
    y0 = oy
    y5 = 230
    y12 = 110
    for yy, lab in [(y5, "5 В"), (y12, "12 В")]:
        f.append(line(ox, yy, ax_r, yy, color="#dddddd", sw=1))
        f.append(text(ox - 12, yy + 4, lab, size=9.5, color=MUTED, anchor="end"))

    # фази по часу
    t0 = ox            # під'єднання
    t1 = 230           # 5 В стоїть, іде діалог
    t2 = 330           # контракт укладено, джерело піднімає напругу
    t3 = 400           # 12 В стоїть (PS_RDY)
    t4 = ax_r

    # крива VBUS
    f.append(line(t0, y0, t0, y5, color=RED, sw=2.6))            # стрибок до 5 В
    f.append(line(t0, y5, t2, y5, color=RED, sw=2.6))           # тримається 5 В
    f.append(line(t2, y5, t3, y12, color=RED, sw=2.6))          # плавно вгору до 12 В
    f.append(line(t3, y12, t4, y12, color=RED, sw=2.6))         # тримається 12 В

    # вертикальні межі фаз
    for tx in (t1, t2, t3):
        f.append(line(tx, oy, tx, ax_t + 20, color="#cccccc", sw=1, dash="3,3"))

    # підписи подій
    f.append(text(t0 + 4, y0 + 20, "під'єднання", size=8.5, color=MUTED, anchor="start"))
    f.append(text((t0 + t2) / 2, y5 - 12, "діалог PD по CC (VBUS = 5 В)", size=9, color=GREEN, bold=True))
    f.append(text(t2 - 6, y12 - 14, "Accept: джерело", size=8.5, color=INK, anchor="end"))
    f.append(text(t2 - 6, y12 - 3, "піднімає напругу", size=8.5, color=INK, anchor="end"))
    f.append(text((t3 + t4) / 2, y12 - 12, "PS_RDY: 12 В стоїть", size=9, color=RED, bold=True))

    # зона «вмикати ключ можна ЛИШЕ тут»
    f.append(rect(t3, ax_t + 26, t4 - t3, 16, fill="#eef8ef", stroke=GREEN, sw=1.2, rx=4))
    f.append(text((t3 + t4) / 2, ax_t + 38, "тут ключ можна замикати", size=8.5, color=GREEN, bold=True))
    f.append(rect(t0, ax_t + 26, t3 - t0, 16, fill="#fdecea", stroke=RED, sw=1.2, rx=4))
    f.append(text((t0 + t3) / 2, ax_t + 38, "ключ РОЗІМКНЕНО (на пристрої 0 В)", size=8.5, color=RED, bold=True))

    render(os.path.join(IMG, "vbus-timeline.svg"), W, H, *f)


# ── Фігура 3: блок-схема й розпіновка тригера ───────────────────────────────
def fig_trigger_block():
    W, H = 780, 470
    f = []
    f.append(text(W / 2, 30, "Тригер PD зсередини: три блоки й типові ніжки",
                  size=16, bold=True))

    # ── Корпус чипа ──
    cx0, cy0, cw, ch = 250, 90, 280, 250
    f.append(rect(cx0, cy0, cw, ch, fill="#fbfbfb", stroke=INK, sw=2))
    f.append(text(cx0 + cw / 2, cy0 - 10, "тригер PD (sink-контролер)", size=12, bold=True))

    # три внутрішні блоки
    f.append(fitbox(cx0 + 20, cy0 + 24, cw - 40, 46,
                    "PD-рушій: рукостискання по CC (BMC, 300 кбод)",
                    size=10, fill="#eef8ef", stroke=GREEN, bold=True))
    f.append(fitbox(cx0 + 20, cy0 + 90, cw - 40, 46,
                    "пам'ять PDO: список бажаних напруг з відкатом",
                    size=10, fill="#fff7e6", stroke=GOLD, bold=True))
    f.append(fitbox(cx0 + 20, cy0 + 156, cw - 40, 46,
                    "керування ключем: POWER_OK лише за контрактом",
                    size=10, fill="#fdecea", stroke=RED, bold=True))

    # ── Ліві ніжки: до роз'єму ──
    def lpin(y, lab, col):
        f.append(line(cx0 - 26, y, cx0, y, color=col, sw=2))
        f.append(circle(cx0 - 26, y, 3, fill=col, stroke=col, sw=0))
        f.append(text(cx0 - 32, y + 4, lab, size=9, color=col, anchor="end", bold=True))
    lpin(cy0 + 40, "CC1", GOLD)
    lpin(cy0 + 66, "CC2", GOLD)
    lpin(cy0 + 110, "VBUS-sense", RED)
    lpin(cy0 + 210, "GND", INK)
    f.append(text(cx0 - 118, cy0 - 6, "до роз'єму USB-C", size=10, color=MUTED, bold=True))

    # ── Праві ніжки: до плати ──
    def rpin(y, lab, col, dash=None):
        f.append(line(cx0 + cw, y, cx0 + cw + 26, y, color=col, sw=2, dash=dash))
        f.append(circle(cx0 + cw + 26, y, 3, fill=col, stroke=col, sw=0))
        f.append(text(cx0 + cw + 32, y + 4, lab, size=9, color=col, anchor="start", bold=True))
    rpin(cy0 + 178, "POWER_OK", GREEN)
    rpin(cy0 + 40, "I2C  (опц.)", BLUE, dash="4,3")
    rpin(cy0 + 66, "ALERT (опц.)", BLUE, dash="4,3")
    rpin(cy0 + 92, "RESET (опц.)", BLUE, dash="4,3")
    f.append(text(cx0 + cw + 120, cy0 - 6, "до плати", size=10, color=MUTED, bold=True))

    # ── POWER_OK → зовнішній ключ VBUS ──
    kx, ky = cx0 + cw + 150, cy0 + 178
    f.append(rect(kx, ky - 20, 70, 40, fill="#fff", stroke=RED, sw=1.8))
    f.append(text(kx + 35, ky - 3, "ключ", size=10, color=RED, bold=True))
    f.append(text(kx + 35, ky + 12, "VBUS", size=9, color=INK))
    f.append(arrow(cx0 + cw + 90, ky, kx, ky, color=GREEN, sw=1.8))

    # підпис
    cap = ("Обов'язкові ніжки — CC1/CC2 (по них розмова), VBUS-sense (бачити реальну напругу), "
           "GND і POWER_OK (сказати ключу «контракт є»). I2C/ALERT/RESET — опційні: для прошивання "
           "пам'яті чи діагностики. POWER_OK керує зовнішнім ключем у лінії VBUS.")
    f.append(fitbox(45, 400, 690, 52, cap, size=10, fill="#f6f6f6", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, "trigger-block.svg"), W, H, *f)


# ── Фігура 4: список PDO у пам'яті з відкатом ───────────────────────────────
def fig_trigger_nvm():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 30, "Список бажаних PDO з відкатом: бери перший, що є в меню",
                  size=15, bold=True))

    # Ліворуч: список у пам'яті чипа (пріоритет згори вниз)
    lx = 70
    f.append(text(lx + 80, 66, "пам'ять тригера", size=11, color=GOLD, bold=True))
    prefs = [("20 В", "хочу найперше"), ("15 В", "як нема 20"),
             ("9 В", "як нема 15"), ("5 В", "гарантований відкат")]
    for i, (v, note) in enumerate(prefs):
        yy = 90 + i * 56
        f.append(rect(lx, yy, 160, 42, fill="#fff7e6", stroke=GOLD, sw=1.5))
        f.append(text(lx + 16, yy + 26, "%d." % (i + 1), size=13, color=INK, anchor="start", bold=True))
        f.append(text(lx + 58, yy + 19, v, size=13, color=INK, anchor="start", bold=True))
        f.append(text(lx + 58, yy + 34, note, size=8, color=MUTED, anchor="start"))
    f.append(text(lx - 6, 90, "вищий", size=8, color=MUTED, anchor="end"))
    f.append(text(lx - 6, 90 + 3 * 56 + 40, "нижчий", size=8, color=MUTED, anchor="end"))
    f.append(line(lx - 14, 96, lx - 14, 90 + 3 * 56 + 34, color=MUTED, sw=1.2))

    # Праворуч: реальне меню слабкої зарядки
    rx = 470
    f.append(text(rx + 70, 66, "меню цієї зарядки", size=11, color=BLUE, bold=True))
    menu = [("20 В", False), ("15 В", False), ("9 В", True), ("5 В", True)]
    y9 = None
    for i, (v, has) in enumerate(menu):
        yy = 90 + i * 56
        if v == "9 В":
            y9 = yy
        col = BLUE if has else "#cccccc"
        fillc = "#eef3fb" if has else "#f3f3f3"
        f.append(rect(rx, yy, 140, 42, fill=fillc, stroke=col, sw=1.5))
        lab = v + ("" if has else "  (нема)")
        f.append(text(rx + 70, yy + 26, lab, size=12, color=(INK if has else MUTED), bold=has))

    # Стрілка «взято»: 9 В зі списку співпало з меню
    f.append(arrow(lx + 160, 90 + 2 * 56 + 21, rx, y9 + 21, color=GREEN, sw=2.4))
    f.append(text((lx + 160 + rx) / 2, 90 + 2 * 56 - 2, "перше збіжне →", size=10, color=GREEN, bold=True))
    f.append(rect(rx - 4, y9 - 4, 148, 50, fill="none", stroke=GREEN, sw=2.2, rx=8))
    f.append(text(rx + 70, y9 + 60, "взято 9 В", size=11, color=GREEN, bold=True))

    # підпис
    cap = ("Задали `[20, 15, 9, 5]`. Ця зарядка не має 20 і 15 — тригер спускається списком і "
           "бере перший наявний профіль, 9 В. Без відкату (лише «20») пристрій лишився б на 5 В.")
    f.append(fitbox(45, 350, 670, 40, cap, size=10, fill="#f6f6f6", stroke=MUTED, sw=1.3))

    render(os.path.join(IMG, "trigger-nvm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sink_gate()
    fig_vbus_timeline()
    fig_trigger_block()
    fig_trigger_nvm()
    print("OK: sink-gate.svg, vbus-timeline.svg, trigger-block.svg, trigger-nvm.svg")
