# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── lab-vs-field-gap: розрив між лабораторним столом і реальним полем ─────────
def fig_lab_vs_field():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 34, "розрив надійності: лабораторний стіл проти реального поля", size=15, color=INK, bold=True))

    col_w, col_h, y0 = 370, 310, 60
    x_lab, x_fld = 40, 450

    # Ліва колонка: Лабораторний стіл
    p.append(rect(x_lab, y0, col_w, col_h, fill=GREENBG, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(x_lab + col_w / 2, y0 + 26, "ЛАБОРАТОРНИЙ СТІЛ (ШТУЧНИЙ КОКОН)", size=11.5, color=FIELD, bold=True))
    
    lab_items = [
        ("Живлення:", "стабілізоване ДЖ, нульовий опір, чиста шина"),
        ("Температура:", "термостатовані +22 °C, відсутність градієнтів"),
        ("Вологість:", "сухе приміщення (40% RH), без конденсату"),
        ("Механіка:", "нерухомий стіл, нуль вібрацій та ударів"),
        ("Земля й лінія:", "короткі дроти (L ≈ 0), немає спільних струмів"),
        ("Результат:", "прототип працює «бездоганно», ризики сховані")
    ]
    for i, (head, desc) in enumerate(lab_items):
        iy = y0 + 56 + i * 42
        p.append(rect(x_lab + 14, iy, col_w - 28, 36, fill=BG, stroke=FIELD, sw=1.1, rx=6))
        p.append(text(x_lab + 24, iy + 22, head, size=9.8, color=FIELD, bold=True, anchor="start"))
        p.append(text(x_lab + 115, iy + 22, desc, size=9.2, color=INK, anchor="start"))

    # Права колонка: Польове середовище
    p.append(rect(x_fld, y0, col_w, col_h, fill=REDBG, stroke=POS, sw=1.8, rx=10))
    p.append(text(x_fld + col_w / 2, y0 + 26, "РЕАЛЬНЕ ПОЛЕ (АГРЕСИВНЕ СЕРЕДОВИЩЕ)", size=11.5, color=POS, bold=True))

    fld_items = [
        ("Брудна лінія:", "індуктивні викиди L·di/dt, просадки від моторів"),
        ("Клімат:", "перепади −40 °C..+85 °C, замерзання електролітів"),
        ("Точка роси:", "конденсація, солі, електрохімічні дендрити"),
        ("Вібрації:", "гармоніки 100–1000 Гц, втомні тріщини BGA"),
        ("Брудна земля:", "Ground Bounce, зсув логічних порогів інтерфейсів"),
        ("Результат:", "миттєві brownout-скидання, корозія, відвал пайки")
    ]
    for i, (head, desc) in enumerate(fld_items):
        iy = y0 + 56 + i * 42
        p.append(rect(x_fld + 14, iy, col_w - 28, 36, fill=BG, stroke=POS, sw=1.1, rx=6))
        p.append(text(x_fld + 24, iy + 22, head, size=9.8, color=POS, bold=True, anchor="start"))
        p.append(text(x_fld + 120, iy + 22, desc, size=9.2, color=INK, anchor="start"))

    # Нижній висновок
    p.append(rect(40, 382, 780, 36, fill=FILL, stroke=MUTED, sw=1.3, rx=8))
    p.append(text(W / 2, 404, "відмова в полі — це не «раптовий баг прошивки», а зіткнення схеми з неврахованою фізикою середовища", size=10.4, color=INK, bold=True))

    render(os.path.join(OUT, "lab-vs-field-gap.svg"), W, H, *p, title="")


# ── dendrite-growth: фізика росту дендритів та електроміграції ───────────────
def fig_dendrite_growth():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 32, "електрохімічна міграція: як волога та напруга вирощують коротке замикання", size=15, color=INK, bold=True))

    stages = [
        ("1. КОНДЕНСАЦІЯ ТА СОЛІ",
         "Перепад температур спричиняє\nточку роси (Dew Point).\nПлівка вологи розчиняє залишки\nфлюсу та атмосферні солі.",
         BLUEBG, NEG),
        ("2. АНОДНЕ РОЗЧИНЕННЯ",
         "Під різницею потенціалів U > 0\nметал анода іонізується:\nCu → Cu²⁺ + 2e⁻ (або Ag/Sn).\nІони переходять у розчин.",
         AMBERBG, AMBER),
        ("3. КАТОДНЕ ВІДНОВЛЕННЯ",
         "Катіони металу мігрують до\nкатода й відновлюються:\nCu²⁺ + 2e⁻ → Cu⁰.\nВиростає голчастий дендрит.",
         REDBG, POS),
        ("4. МІКРОШУНТ / ПРОБІЙ",
         "Дендрит дотикається анода.\nВиникає паразитний струм,\nвитік на вході АЦП або повне\nкоротке замикання живлення.",
         FILL, LINE),
    ]

    bw, bh, by = 186, 172, 64
    xs = [32, 238, 444, 650]

    for x, (head, body, fill, col) in zip(xs, stages):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + bw / 2, by + 22, head, size=9.6, color=tagcol, bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + bw / 2, by + 46 + j * 16, ln, size=9.1, color=INK))

    for i in range(3):
        p.append(arrow(xs[i] + bw + 4, by + bh / 2, xs[i+1] - 4, by + bh / 2, color=INK, sw=2))

    # Нижня частина: схема фізичного процесу на платі
    py, ph = 252, 168
    p.append(rect(32, py, 796, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W / 2, py + 22, "Мікроструктура зазору 0.5 мм між пінами QFN під плівкою конденсату", size=11, color=INK, bold=True))

    # Анод і Катод площадки
    p.append(rect(80, py + 48, 120, 70, fill=AMBERBG, stroke=AMBER, sw=2, rx=6))
    p.append(text(140, py + 74, "АНОД (+Vcc)", size=11, color=AMBERTX, bold=True))
    p.append(text(140, py + 98, "Cu → Cu²⁺ + 2e⁻", size=10.2, color=INK))

    p.append(rect(660, py + 48, 120, 70, fill=BLUEBG, stroke=NEG, sw=2, rx=6))
    p.append(text(720, py + 74, "КАТОД (GND)", size=11, color=NEG, bold=True))
    p.append(text(720, py + 98, "Cu²⁺ + 2e⁻ → Cu⁰", size=10.2, color=INK))

    # Плівка електроліту
    p.append(rect(204, py + 62, 452, 42, fill="#e2edf8", stroke=NEG, sw=1.2, rx=4))
    p.append(text(430, py + 78, "водна плівка конденсату + іони електроліту (Cl⁻, SO₄²⁻, залишки флюсу)", size=9.2, color=NEG, italic=True))

    # Дендрити, що ростуть від катода до анода
    p.append(line(660, py + 84, 580, py + 78, color=POS, sw=2.2))
    p.append(line(580, py + 78, 520, py + 90, color=POS, sw=2.0))
    p.append(line(520, py + 90, 430, py + 80, color=POS, sw=1.8))
    p.append(line(430, py + 80, 320, py + 86, color=POS, sw=1.8))
    p.append(line(320, py + 86, 204, py + 82, color=POS, sw=1.6))
    p.append(text(430, py + 96, "← ріст металевих кристалів (дендритів) назустріч аноду ←", size=9.4, color=POS, bold=True))

    p.append(text(W / 2, py + 148, "захист: безвідмивний флюс, очищення в УЗ-ванні та лакування (Conformal Coating)", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "dendrite-growth.svg"), W, H, *p, title="")


# ── halt-operating-limits: методологія HALT/HASS та межі стресу ───────────────
def fig_halt_limits():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 32, "методологія HALT: межі специфікації, роботи та руйнування", size=15, color=INK, bold=True))

    # Три неперекривні рівні карток угорі
    cards = [
        (40, 60, 240, 84, GREENBG, FIELD, "СПЕЦИФІКАЦІЯ (SPEC)",
         "−40 °C ... +85 °C / Vnom ± 5%\nГарантований виробником\nдіапазон стабільної роботи."),
        (310, 60, 240, 84, AMBERBG, AMBER, "РОБОЧІ МЕЖІ (LOL / UOL)",
         "−55 °C ... +110 °C\nЗворотний функціональний збій;\nвідновлення після зняття стресу."),
        (580, 60, 240, 84, REDBG, POS, "МЕЖІ РУЙНУВАННЯ (LDL / UDL)",
         "−70 °C ... +135 °C\nНезворотне фізичне пошкодження:\nпробій кристала, відрив пайки."),
    ]
    for x, y, w, h, fill, col, head, body in cards:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + w / 2, y + 20, head, size=10.5, color=tagcol, bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + w / 2, y + 40 + j * 14, ln, size=9.2, color=INK))

    # Центральна вісь стресу
    ax_y = 205
    p.append(line(40, ax_y, W - 40, ax_y, color=LINE, sw=2.4))
    p.append(arrow(W - 70, ax_y, W - 35, ax_y, color=LINE, sw=2.4))
    p.append(text(W - 35, ax_y - 12, "Стрес (+T, Вібрація, Напруга)", size=10, color=INK, bold=True, anchor="end"))

    # Смуга запасу міцності на осі
    p.append(rect(100, ax_y - 16, 660, 32, fill="#f0f3f6", stroke=MUTED, sw=1.2, rx=4))
    p.append(rect(200, ax_y - 16, 460, 32, fill="#e5edec", stroke=AMBER, sw=1.4, rx=4))
    p.append(rect(300, ax_y - 16, 260, 32, fill=GREENBG, stroke=FIELD, sw=1.8, rx=4))

    # Позначки точок на осі
    points = [
        (100, "LDL", "−70 °C", POS),
        (200, "LOL", "−55 °C", AMBER),
        (300, "Spec Low", "−40 °C", FIELD),
        (560, "Spec High", "+85 °C", FIELD),
        (660, "UOL", "+110 °C", AMBER),
        (760, "UDL", "+135 °C", POS),
    ]
    for px, tag, val, col in points:
        tagcol = AMBERTX if col == AMBER else col
        p.append(circle(px, ax_y, 5, fill=col, stroke=BG, sw=1.6))
        p.append(line(px, ax_y - 24, px, ax_y + 24, color=col, sw=1.5))
        p.append(text(px, ax_y + 40, tag, size=10, color=tagcol, bold=True))
        p.append(text(px, ax_y + 54, val, size=9.2, color=INK))

    # Пояснення запасу внизу
    p.append(rect(40, 290, 780, 116, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W / 2, 314, "Ціль HALT — виявити приховані слабкі місця конструкції та розширити робочий діапазон (Design Margin).", size=10.4, color=INK, bold=True))
    p.append(text(W / 2, 336, "Чим більша відстань між Spec High (+85 °C) та UOL (+110 °C), тим надійніший пристрій у полі при накладанні завад.", size=9.8, color=INK))
    p.append(text(W / 2, 358, "HASS (скринінг партії) застосовує короткий стрес (між Spec та LOL/UOL) для швидкого відсіювання браку пайки.", size=9.8, color=INK))
    p.append(text(W / 2, 384, "HALT ламає прототип заради вдосконалення схеми; HASS перевіряє серію без витрати ресурсу компонентів.", size=9.4, color=MUTED, italic=True))

    render(os.path.join(OUT, "halt-operating-limits.svg"), W, H, *p, title="")


if __name__ == "__main__":
    fig_lab_vs_field()
    fig_dendrite_growth()
    fig_halt_limits()
    print("OK: figures generated successfully.")
