# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «CJMCU MC33886 — драйвер моторів (5A H-міст)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: чотири ключі H-моста + обвʼязка керування ─────────────────
def fig_inside():
    W, H = 980, 580
    f = [text(W / 2, 30, "Що ховає одна мікросхема MC33886", size=17, bold=True)]

    # Рамка «силова частина» — сам H-міст із 4 ключів
    px, py, pw, ph = 400, 80, 360, 360
    f.append(rect(px, py, pw, ph, fill="#fbfbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(px + pw / 2, py + 22, "H-міст: чотири MOSFET-ключі", size=12.5, bold=True))

    # верхня шина V+ і нижня GND — підписи ставимо ЗБОКУ (поза лінією), не над нею
    railL = px + 95          # ліва стійка (плече OUT1)
    railR = px + pw - 95     # права стійка (плече OUT2)
    top = py + 62
    bot = py + ph - 52
    f.append(line(railL - 30, top, railR + 30, top, color=POS, sw=3))
    f.append(text(px + pw - 14, top - 10, "V+", size=12, color=POS, bold=True, anchor="end"))
    f.append(line(railL - 30, bot, railR + 30, bot, color=NEG, sw=3))
    f.append(text(px + 14, bot + 20, "GND", size=12, color=NEG, bold=True, anchor="start"))

    midY = (top + bot) / 2
    sw, sh = 48, 32   # розмір «ключа»

    def key(cx, cy, label):
        b = rect(cx - sw / 2, cy - sh / 2, sw, sh, fill=BG, stroke=INK, sw=1.6, rx=5)
        b += text(cx, cy + 5, label, size=11, bold=True)
        return b

    def stringer(x, cy_hi, cy_lo):
        """Вертикальні зʼєднання, що НЕ проходять крізь тіло ключа (лінія впирається в край рамки)."""
        parts = []
        parts.append(line(x, top, x, cy_hi - sh / 2, color=INK, sw=2))          # V+ → верх HS
        parts.append(line(x, cy_hi + sh / 2, x, midY, color=INK, sw=2))          # низ HS → вузол OUT
        parts.append(line(x, midY, x, cy_lo - sh / 2, color=INK, sw=2))          # вузол OUT → верх LS
        parts.append(line(x, cy_lo + sh / 2, x, bot, color=INK, sw=2))           # низ LS → GND
        return parts

    # ліва стійка: верхній ключ HS1, нижній LS1, вузол OUT1 посередині
    hi1, lo1 = (top + midY) / 2, (midY + bot) / 2
    f.extend(stringer(railL, hi1, lo1))
    f.append(key(railL, hi1, "HS1"))
    f.append(key(railL, lo1, "LS1"))
    f.append(circle(railL, midY, 4, fill=INK, stroke=INK))
    f.append(text(railL - 34, midY + 4, "OUT1", size=10.5, bold=True, color=INK, anchor="end"))

    # права стійка: HS2 / LS2 / OUT2
    hi2, lo2 = (top + midY) / 2, (midY + bot) / 2
    f.extend(stringer(railR, hi2, lo2))
    f.append(key(railR, hi2, "HS2"))
    f.append(key(railR, lo2, "LS2"))
    f.append(circle(railR, midY, 4, fill=INK, stroke=INK))
    f.append(text(railR + 34, midY + 4, "OUT2", size=10.5, bold=True, color=INK, anchor="start"))

    # мотор між OUT1 і OUT2 (підпис M — усередині кола, лінія йде повз коло, не крізь напис)
    mcx = (railL + railR) / 2
    f.append(line(railL, midY, mcx - 22, midY, color=INK, sw=2))
    f.append(line(mcx + 22, midY, railR, midY, color=INK, sw=2))
    f.append(circle(mcx, midY, 22, fill="#eef2f8", stroke=INK, sw=1.8))
    f.append(text(mcx, midY + 6, "M", size=16, bold=True))

    # ліва колонка — обвʼязка керування (логіка, charge pump, захист). Ширші рамки, короткий текст → шрифт ≥8.
    lx, lw = 40, 300
    blocks = [
        ("Логіка керування", "IN1·IN2 задають плечі; EN тримає міст живим", py + 30, INK),
        ("Заряд-помпа (CCP)", "піднімає напругу, щоб відкрити верхні ключі", py + 118, POS),
        ("Захист", "перегрів, КЗ, просадка → тристейт і флаг FS", py + 206, NEG),
        ("Дзеркало струму (FB)", "віддає ~1/375 струму мотора на вимір", py + 294, FIELD),
    ]
    for title, desc, y, col in blocks:
        f.append(fitbox(lx, y, lw, 64, title + "\n" + desc, size=11,
                        fill=FILL, stroke=col, sw=1.6, bold=False))
        # стрілка від блоку до силової рамки (кінці поза написами; лінія в порожнечі між рамками)
        f.append(arrow(lx + lw, y + 32, px, y + 32, color=col, sw=1.6))

    # підпис-висновок
    b, bw, bh = textbox(W / 2, H - 28,
                        "усе в одному кристалі: ключі, драйвери затворів, заряд-помпа й захист — назовні лишаються тільки логічні входи й вивід на мотор",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: МК → модуль CJMCU → мотор і живлення ────────────────
def fig_wiring():
    W, H = 940, 540
    f = [text(W / 2, 30, "Пін-у-пін: мікроконтролер, модуль, мотор і два живлення",
              size=16, bold=True)]

    # МК ліворуч
    mkx, mky, mkw, mkh = 40, 130, 160, 250
    f.append(rect(mkx, mky, mkw, mkh, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mkx + mkw / 2, mky + 24, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mkx + mkw / 2, mky + 42, "(Arduino / ESP32)", size=10, color=MUTED))
    mk = [("GPIO → IN1", NEG, mky + 90),
          ("GPIO → IN2", NEG, mky + 132),
          ("PWM → EN", POS, mky + 174),
          ("GND", INK, mky + 216)]
    for lbl, col, y in mk:
        f.append(text(mkx + mkw - 12, y, lbl, size=11, bold=True, color=col, anchor="end"))

    # модуль у центрі
    ax, ay, aw, ah = 350, 100, 200, 320
    f.append(rect(ax, ay, aw, ah, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=12))
    f.append(text(ax + aw / 2, ay + 24, "Модуль CJMCU", size=12.5, bold=True))
    f.append(text(ax + aw / 2, ay + 42, "MC33886", size=10.5, color=MUTED))

    # логічний бік (ліворуч на модулі) — дзеркало МК
    lin = [("IN1", NEG, mky + 90),
           ("IN2", NEG, mky + 132),
           ("EN", POS, mky + 174),
           ("GND", INK, mky + 216)]
    for lbl, col, y in lin:
        f.append(text(ax + 12, y, lbl, size=11, bold=True, color=col, anchor="start"))
        f.append(line(mkx + mkw, y, ax, y, color=col, sw=2.0))

    # логічне живлення VCC модуля (5 В логіки)
    f.append(text(ax + 12, ay + 40 + 250, "VCC(лог)", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(ax + aw / 2, ay + ah - 14, "тепловідвід через корпус і землю", size=9, color=MUTED))

    # силовий бік (праворуч на модулі): OUT1/OUT2 і живлення мотора
    rout = [("OUT1", INK, ay + 90),
            ("OUT2", INK, ay + 140),
            ("V+ (мотор)", POS, ay + 210),
            ("PWR GND", NEG, ay + 250)]
    for lbl, col, y in rout:
        f.append(text(ax + aw - 12, y, lbl, size=11, bold=True, color=col, anchor="end"))

    # мотор праворуч
    mtx, mty = 720, 190
    f.append(circle(mtx, mty, 34, fill="#eef2f8", stroke=INK, sw=2))
    f.append(text(mtx, mty + 6, "M", size=20, bold=True))
    f.append(text(mtx, mty + 56, "DC-мотор", size=11, bold=True))
    f.append(line(ax + aw, ay + 90, mtx - 24, mty - 14, color=INK, sw=2.4))
    f.append(line(ax + aw, ay + 140, mtx - 24, mty + 14, color=INK, sw=2.4))

    # окреме силове живлення знизу праворуч
    psx, psy, psw, psh = 660, 330, 210, 90
    f.append(rect(psx, psy, psw, psh, fill="#fdf6e3", stroke=POS, sw=1.7, rx=10))
    f.append(text(psx + psw / 2, psy + 24, "Живлення мотора", size=11.5, bold=True))
    f.append(text(psx + psw / 2, psy + 44, "5 – 28 В, за струмом мотора", size=10, color=INK))
    f.append(text(psx + psw / 2, psy + 64, "БЕЗ нього міст мертвий", size=9.5, color=POS, bold=True))
    f.append(line(psx, psy + 20, ax + aw, ay + 210, color=POS, sw=2.2))    # V+
    f.append(line(psx, psy + 60, ax + aw, ay + 250, color=NEG, sw=2.2))    # PWR GND

    # ключ-нагадування: спільна земля
    f.append(text(W / 2, H - 58, "Спільна земля логіки й силового живлення — обовʼязкова, інакше логіка «не бачить» рівнів",
                  size=11, color=NEG, bold=True))

    b, bw, bh = textbox(W / 2, H - 26,
                        "два джерела: логіка (VCC/GND від МК) і сила (V+/PWR GND від окремого блока); землі зведені разом",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Три «сім'ї» транзисторів на одному кристалі (ідея BCD / SmartMOS) ───────
def fig_three_families():
    W, H = 940, 470
    f = [text(W / 2, 30, "Один кристал — три різні транзистори під різну роль", size=16, bold=True)]

    # спільна підкладка знизу — широка плита
    subx, suby, subw, subh = 60, 360, W - 120, 54
    f.append(rect(subx, suby, subw, subh, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(W / 2, suby + 33, "спільна кремнієва підкладка (один чип)", size=12, bold=True))

    # три колонки — bipolar / CMOS / DMOS. Широкі клітини, короткий текст → шрифт ≥8.
    colw, gap = 258, 24
    x0 = (W - (3 * colw + 2 * gap)) / 2
    cols = [
        ("Біполярний", "точний аналог:\nопори, порівняння,\nдзеркало струму", NEG, "тонка робота"),
        ("CMOS", "цифрова логіка:\nтаблиця режимів,\nмалий струм спокою", FIELD, "мозок"),
        ("DMOS (силовий)", "силові ключі H-моста:\nмалий опір каналу,\nампери струму", POS, "мʼязи"),
    ]
    cy, ch = 92, 210
    for i, (title, desc, col, tag) in enumerate(cols):
        cx = x0 + i * (colw + gap)
        f.append(rect(cx, cy, colw, ch, fill="#fbfbfc", stroke=col, sw=1.8, rx=12))
        f.append(text(cx + colw / 2, cy + 30, title, size=13.5, bold=True, color=col))
        f.append(text(cx + colw / 2, cy + 52, "«" + tag + "»", size=10.5, color=MUTED, italic=True))
        f.append(fitbox(cx + 20, cy + 74, colw - 40, 108, desc, size=11.5,
                        fill=BG, stroke=MUTED, sw=1.3))
        # «ніжка» до спільної підкладки (лінія в порожнечі між клітиною й плитою)
        f.append(line(cx + colw / 2, cy + ch, cx + colw / 2, suby, color=col, sw=2))

    b, bw, bh = textbox(W / 2, H - 24,
                        "SmartMOS зводить усі три в одному техпроцесі: аналог, логіку й силу більше не паяють окремими корпусами",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "three-families.svg"), W, H, *f)


# ── 4. Родовід кремнію: Motorola → Freescale → NXP, і де тут MC33886 ───────────
def fig_lineage():
    # РІВНОМІРНІ слоти (роки стоять близько — рівні клітини прибирають накладання).
    W, H = 1200, 460
    f = [text(W / 2, 30, "Родовід: чий кремній тримає MC33886", size=16, bold=True)]

    axy = 250
    f.append(line(50, axy, W - 50, axy, color=MUTED, sw=2))

    # (рік, підпис, колір): порядок хронологічний, слоти рівні незалежно від відстані років
    marks = [
        (1980, "Motorola: перші\nсилові MOSFET\n(марка TMOS)", NEG),
        (1985, "SGS винаходить BCD:\nаналог+логіка+сила\nна одному кристалі", FIELD),
        (2000, "Motorola SmartMOS 7:\n0.35 мкм, 65 В,\nлогіка + LDMOS", POS),
        (2002, "MC33886:\nмонолітний H-міст\nна SmartMOS", INK),
        (2004, "Motorola виділяє\nFreescale", MUTED),
        (2015, "Freescale\nвходить у NXP", MUTED),
    ]
    n = len(marks)
    slot = (W - 120) / n
    cw = slot - 26            # ширина картки з запасом між слотами
    for i, (yr, lbl, col) in enumerate(marks):
        x = 60 + slot * (i + 0.5)
        f.append(circle(x, axy, 6, fill=col, stroke=col))
        # картки чергуються верх/низ → навіть сусідні не торкаються по вертикалі
        up = (i % 2 == 0)
        f.append(text(x, axy + (26 if up else -16), str(yr), size=12.5, bold=True, color=col))
        if up:
            f.append(fitbox(x - cw / 2, axy - 108, cw, 70, lbl, size=11, fill=BG, stroke=col, sw=1.3))
            f.append(line(x, axy - 38, x, axy - 6, color=col, sw=1.3))
        else:
            f.append(fitbox(x - cw / 2, axy + 40, cw, 70, lbl, size=11, fill=BG, stroke=col, sw=1.3))
            f.append(line(x, axy + 6, x, axy + 40, color=col, sw=1.3))

    b, bw, bh = textbox(W / 2, H - 22,
                        "та сама мікросхема сьогодні: спроєктована в Motorola, випущена під Freescale, продається під NXP",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_three_families()
    fig_lineage()
    print("OK: 4 figures ->", IMG)
