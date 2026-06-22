# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер і частота комутації».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Підписи до фігур живуть у Markdown статті, не всередині SVG."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#caa24a"   # третій акцент (готовий модуль / орієнтир)


# ── Три рівні інтеграції ─────────────────────────────────────────────────────
def fig_levels():
    W, H = 900, 330
    f = []
    cols = [
        (35,  NEG,   "Контролер + зовнішні MOSFET", "ключі окремо, контролер ними керує",
         "будь-яка потужність, гнучко, дешеві ключі", "найбільше роботи й місця, складне розведення"),
        (330, FIELD, "Інтегрований switcher", "ключі всередині чипа",
         "просто, компактно, мало деталей", "стеля за струмом (кілька ампер)"),
        (625, GOLD,  "Готовий power-модуль", "контролер, ключі й котушка в корпусі",
         "найпростіше й найшвидше, мала площа", "найдорожче, менш гнучко"),
    ]
    for x, col, head, what, plus_t, minus_t in cols:
        f.append(rect(x, 40, 270, 230, fill=BG, stroke=col, sw=2))
        f.append(text(x + 135, 68, head, size=12.5, color=col, bold=True))
        f.append(line(x + 18, 82, x + 252, 82, color=MUTED, sw=1))
        f.append(text(x + 18, 112, what, size=10.5, anchor="start"))
        f.append(text(x + 18, 152, "+ " + plus_t, size=10.5, color=FIELD, anchor="start", bold=True))
        f.append(text(x + 18, 184, "− " + minus_t, size=10.5, color=POS, anchor="start", bold=True))
    f.append(arrow(60, 300, 850, 300, color=MUTED, sw=2))
    f.append(text(455, 290, "більше інтеграції → простіше, але дорожче й менш гнучко",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "levels.svg"), W, H, *f,
           title="Три рівні: від контролера до готового модуля")


# ── Компроміс частоти: дві тенденції та долина ──────────────────────────────
def fig_freq_tradeoff():
    W, H = 900, 340
    x0, x1, ybot, ytop = 110, 800, 300, 70
    f = [line(x0, ybot, x1, ybot, color=INK, sw=1.6),
         line(x0, ybot, x0, ytop - 5, color=INK, sw=1.6),
         text(x1 + 4, ybot + 4, "частота f →", size=11, anchor="start", bold=True),
         text(x0 - 8, ytop + 6, "вартість", size=11, anchor="end", bold=True)]
    n = 40

    def poly(pts, col, sw=3):
        s = " ".join("%.1f,%.1f" % p for p in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round" stroke-linecap="round"/>' % (s, col, sw))

    # котушка ∝ 1/f (спадає), втрати ∝ f (росте), сума — долина
    coil, loss, tot = [], [], []
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        coil.append((xx, ytop + 40 + 150 * (1 / (1 + 6 * t))))
        loss.append((xx, ybot - 20 - 200 * t))
        # сума двох → опукла донизу крива з мінімумом ближче до лівої третини
        s = 150 * (1 / (1 + 6 * t)) + 200 * t * 0.7
        tot.append((xx, ytop + 30 + s * 0.55))
    f.append(poly(coil, NEG))
    f.append(poly(loss, POS))
    f.append(poly(tot, FIELD))
    f.append(text(x0 + 130, ytop + 95, "котушка й C ∝ 1/f", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(x0 + 410, ytop + 70, "втрати на перемиканні ∝ f", size=11, color=POS, anchor="start", bold=True))
    f.append(text(x0 + 205, ytop + 165, "сукупно", size=11, color=FIELD, anchor="start", bold=True))
    # мінімум суми
    xm = min(tot, key=lambda p: p[1])[0]
    f.append(line(xm, ybot, xm, ytop + 30, color=GOLD, sw=1.6, dash="5,5"))
    f.append(text(xm, ytop + 20, "розумна частота", size=11, color=GOLD, bold=True))
    for xx, lab in [(x0 + 60, "100 кГц"), (xm, "0.5–1 МГц"), (x1 - 110, "кілька МГц")]:
        f.append(text(xx, ybot + 20, lab, size=9.5, color=MUTED))
    render(os.path.join(IMG, "freq-tradeoff.svg"), W, H, *f,
           title="Частота: менша магнетика проти більших втрат")


# ── Анатомія втрат на перемиканні: перекриття V×I ───────────────────────────
def fig_switching_loss():
    W, H = 900, 330
    x0, ybot, ytop = 110, 250, 90
    f = [line(x0, ytop - 10, x0, ybot + 10, color=INK, sw=1.5),
         line(x0, ybot, 700, ybot, color=INK, sw=1.5),
         text(704, ybot + 4, "t", size=12, anchor="start", bold=True)]
    # напруга росте, струм спадає — перехрест у вікні переходу
    f.append('<polyline points="110,240 300,240 360,100 680,100" fill="none" '
             'stroke="%s" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>' % POS)
    f.append(text(560, 90, "напруга на ключі V", size=11, color=POS, bold=True))
    f.append('<polyline points="110,100 300,100 360,240 680,240" fill="none" '
             'stroke="%s" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>' % NEG)
    f.append(text(200, 90, "струм ключа I", size=11, color=NEG, bold=True))
    # вікно перекриття
    f.append('<polygon points="300,250 300,100 360,240 360,250" fill="%s" fill-opacity="0.35"/>' % GOLD)
    f.append(text(420, 178, "перекриття V×I", size=11, color=GOLD, anchor="start", bold=True))
    f.append(text(420, 196, "= енергія в тепло", size=10, anchor="start"))
    f.append(arrow(415, 188, 345, 178, color=GOLD, sw=1.6))
    # формула в рамці
    box = fitbox(80, 280, 740, 40,
                 "Pперемик ≈ ½·Vвх·Iнаван·(tвкл+tвикл)·fsw   +   Qg·Vкер·fsw",
                 size=14, fill=FILL, stroke=MUTED, bold=True)
    f.append(box)
    render(os.path.join(IMG, "switching-loss.svg"), W, H, *f,
           title="Звідки втрати: перекриття V та I на кожному перемиканні")


# ── Частота й завади: гармоніки, чутлива смуга, спред-спектрум ──────────────
def fig_emi_harmonics():
    W, H = 900, 330
    x0, ybot, ytop = 100, 250, 80
    f = [line(x0, ybot, 820, ybot, color=INK, sw=1.6),
         line(x0, ybot, x0, ytop - 5, color=INK, sw=1.6),
         text(822, ybot + 4, "частота", size=11, anchor="start", bold=True),
         text(x0 - 10, ytop + 6, "амплітуда", size=11, anchor="end", bold=True)]
    # чутлива смуга
    f.append('<rect x="380" y="90" width="120" height="160" fill="%s" fill-opacity="0.10"/>' % POS)
    f.append(text(440, 104, "чутлива смуга", size=10, color=POS, bold=True))
    f.append(text(440, 118, "(напр. радіо)", size=9, color=POS))
    # гребінь гармонік (спадає)
    for xx, h, lab in [(160, 150, "f"), (250, 96, "2·f"), (340, 64, "3·f"),
                       (430, 44, "4·f"), (520, 30, "5·f")]:
        f.append(line(xx, ybot, xx, ybot - h, color=NEG, sw=3))
        f.append(text(xx, ybot + 16, lab, size=9.5, color=MUTED))
    # спред-спектрум
    f.append(text(650, 150, "спред-спектрум:", size=11, color=FIELD, bold=True))
    f.append(text(650, 168, "тремтіння f розмазує піки", size=10))
    f.append(text(650, 184, "в ширшу смугу (нижчі)", size=10))
    f.append('<polyline points="600,212 620,205 640,209 660,203 680,210 700,204" '
             'fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % FIELD)
    render(os.path.join(IMG, "emi-harmonics.svg"), W, H, *f,
           title="Частота і завади: гармоніки та чутливі смуги")


# ── Струмова стеля: інтегрований / модуль / зовнішні ключі ─────────────────
def fig_current_ceiling():
    W, H = 880, 300
    x0, ybot = 120, 250
    f = [line(x0, ybot, 820, ybot, color=INK, sw=1.6),
         text(822, ybot + 4, "Iвих", size=11, anchor="start", bold=True)]
    for xx, lab in [(139, "1 А"), (177, "3 А"), (234, "6 А"),
                    (310, "10 А"), (500, "20 А"), (690, "30 А")]:
        f.append(line(xx, ybot, xx, ybot + 5, color=MUTED, sw=1))
        f.append(text(xx, ybot + 20, lab, size=9.5, color=MUTED))
    bars = [(110, 104.5, FIELD, "інтегрований switcher"),
            (160, 218.5, GOLD,  "power-модуль"),
            (210, 551.0, NEG,   "контролер + зовн. MOSFET")]
    for y, w, col, lab in bars:
        f.append(rect(130, y, w, 32, fill=BG, stroke=col, sw=2))
        f.append(text(140, y + 21, lab, size=11, color=col, anchor="start", bold=True))
    render(os.path.join(IMG, "current-ceiling.svg"), W, H, *f,
           title="Скільки струму: стеля інтегрованого проти зовнішніх ключів")


# ── Режим керування: за напругою / за струмом ──────────────────────────────
def fig_control_mode():
    W, H = 900, 300
    f = []
    f.append(rect(50, 50, 380, 220, fill="#eef3fb", stroke=NEG, sw=1.8))
    f.append(text(240, 78, "За напругою (voltage-mode)", size=12.5, color=NEG, bold=True))
    for i, t in enumerate(["міряє лише вихідну напругу", "простіша ідея"]):
        f.append(text(72, 108 + i * 28, t, size=11, anchor="start"))
    for i, t in enumerate(["немає вбудованого ліміту струму", "повільніша реакція", "складніше стабілізувати"]):
        f.append(text(72, 170 + i * 28, "− " + t, size=11, color=POS, anchor="start"))
    f.append(rect(470, 50, 380, 220, fill="#eef8ef", stroke=FIELD, sw=1.8))
    f.append(text(660, 78, "За струмом (current-mode)", size=12.5, color=FIELD, bold=True))
    f.append(text(492, 108, "міряє ще й струм котушки", size=11, anchor="start"))
    for i, t in enumerate(["поцикловий ліміт струму (захист)", "швидша реакція на вхід", "простіша компенсація"]):
        f.append(text(492, 140 + i * 28, "+ " + t, size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(492, 248, "майже всі сучасні контролери", size=11, anchor="start"))
    render(os.path.join(IMG, "control-mode.svg"), W, H, *f,
           title="Режим керування: за напругою чи за струмом")


# ── Що всередині power-модуля (для вставки comp-power-modules) ───────────────
def fig_inside_module():
    W, H = 760, 380
    f = [text(W / 2, 30, "Power-модуль: усе живлення зведено в один корпус",
              size=16, bold=True)]
    f.append(text(195, 64, "дискретно: купа деталей", size=14, bold=True, color=MUTED))
    f.append(rect(40, 80, 310, 250, fill="#fbfcfd", stroke=LINE, sw=1.4))
    spots = [
        (95, 120, "контролер"), (235, 120, "верх.\nключ"),
        (95, 185, "котушка"), (235, 185, "нижн.\nключ"),
        (95, 250, "Cвх"), (165, 250, "Cвих"),
        (245, 250, "Rдоб."), (300, 185, "Rзвор."),
    ]
    for x, y, lab in spots:
        f.append(fitbox(x - 42, y - 22, 84, 44, lab, size=11, fill=FILL))
    for a, b in [((137, 120), (193, 120)), ((95, 142), (95, 163)),
                 ((137, 185), (193, 185)), ((95, 207), (95, 228)),
                 ((137, 250), (123, 250)), ((207, 250), (203, 250)),
                 ((235, 142), (235, 163)), ((277, 185), (258, 185))]:
        f.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(195, 318, "розводити, добирати, паяти — все вручну",
                  size=11, color=MUTED))
    f.append(arrow(360, 200, 405, 200, color=FIELD, sw=2.4))
    f.append(text(575, 64, "модуль: один корпус", size=14, bold=True, color=FIELD))
    f.append(rect(420, 80, 300, 250, fill="#f1faf4", stroke=FIELD, sw=2.2))
    f.append(fitbox(445, 110, 120, 40, "контролер", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(575, 110, 120, 40, "обидва\nключі", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(445, 165, 250, 46, "котушка (усередині корпусу)",
                    size=12, fill="#eaf4ff", stroke=NEG))
    f.append(fitbox(445, 225, 120, 38, "Cвх", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(575, 225, 120, 38, "звор. зв'язок", size=11, fill=BG, stroke=LINE))
    pins = ["VIN", "EN", "FB", "VOUT", "PG", "GND"]
    px = 440
    for p in pins:
        f.append(rect(px, 332, 6, 14, fill=INK, stroke=INK, sw=1))
        f.append(text(px + 3, 360, p, size=10, color=INK))
        px += 47
    f.append(text(570, 300, "лишилось підвести живлення й 2-3 деталі",
                  size=11, color=FIELD))
    render(os.path.join(IMG, "inside-module.svg"), W, H, *f)


if __name__ == "__main__":
    fig_levels()
    fig_freq_tradeoff()
    fig_switching_loss()
    fig_emi_harmonics()
    fig_current_ceiling()
    fig_control_mode()
    fig_inside_module()
    print("OK: figs written to", IMG)
