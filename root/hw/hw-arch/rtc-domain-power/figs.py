# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RTC_FILL = "#eafaf1"   # світло-зелений острівець RTC
RTC_EDGE = FIELD
OFF_FILL = "#eef0f2"   # сіре «вимкнене»


# ── Фігура 1: кордон домену RTC ─────────────────────────────────────────────
def fig_domain_boundary():
    W, H = 720, 400
    p = []

    # Зовнішня рамка кристала
    p.append(rect(20, 50, W - 40, H - 70, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(W / 2, 40, "Кристал SoC", size=15, bold=True, color=MUTED))

    # Ліворуч: решта чипа (вимикається), сіра
    p.append(rect(45, 80, 300, 285, fill=OFF_FILL, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(195, 104, "Решта кристала", size=14, bold=True, color=MUTED))
    p.append(text(195, 124, "живлення VDD — гасне при вимкненні", size=11, color=MUTED))
    for i, (lbl) in enumerate(["Ядро процесора", "Оперативна пам'ять (ОЗП)",
                                "Шини й контролери", "USB · SPI · UART · таймери",
                                "Високочастотні генератори"]):
        y = 150 + i * 40
        p.append(fitbox(70, y, 250, 30, lbl, size=12, fill=BG, stroke=MUTED, color=MUTED))

    # Праворуч: домен RTC (острівець), зелений
    p.append(rect(400, 80, 290, 285, fill=RTC_FILL, stroke=RTC_EDGE, sw=2.5, rx=8))
    p.append(text(545, 104, "Домен RTC", size=14, bold=True, color=FIELD))
    p.append(text(545, 124, "живлення VBAT — живий завжди", size=11, color=FIELD))
    for i, lbl in enumerate(["Кварц 32768 Гц (LSE)",
                              "Ланцюг подільників ÷2¹⁵",
                              "Лічильники: с · хв · год · дата",
                              "Резервні регістри",
                              "Перемикач джерел"]):
        y = 150 + i * 40
        p.append(fitbox(420, y, 250, 30, lbl, size=12, fill=BG, stroke=RTC_EDGE, color=INK))

    # Живлення знизу
    p.append(text(195, 388, "VDD (мережа / акумулятор)", size=12, color=NEG, bold=True))
    p.append(text(545, 388, "VBAT (батарейка) — вічний", size=12, color=POS, bold=True))

    render(os.path.join(OUT, "domain-boundary.svg"), W, H, *p)


# ── Фігура 2: автоматичний перемикач джерел ─────────────────────────────────
def fig_power_switch():
    W, H = 720, 380
    p = []

    # Два джерела ліворуч
    p.append(fitbox(40, 70, 150, 56, "VDD\n≈ 3.3 В\n(поки живлення є)",
                    size=13, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    p.append(fitbox(40, 250, 150, 56, "VBAT\n≈ 2.9 В\n(батарейка)",
                    size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Компаратор-перемикач у центрі
    cx, cy = 360, 190
    p.append(rect(cx - 95, cy - 70, 190, 140, fill=FILL, stroke=INK, sw=2, rx=10))
    p.append(mtext(cx, cy - 34, ["Перемикач", "джерел"], size=15, bold=True))
    p.append(mtext(cx, cy + 8, ["живи від того,", "де напруга ВИЩА"], size=12, color=MUTED))
    p.append(text(cx, cy + 52, "VDD ⋛ VBAT", size=14, bold=True, color=INK))

    # Стрілки джерел -> перемикач
    p.append(arrow(190, 98, cx - 95, cy - 40, color=NEG))
    p.append(arrow(190, 278, cx - 95, cy + 40, color=POS))

    # Вихід -> домен
    p.append(arrow(cx + 95, cy, 560, cy, color=INK, sw=2.2))
    p.append(fitbox(560, cy - 45, 130, 90,
                    "Домен RTC\nживиться\nбез розриву\nтакту",
                    size=13, fill=RTC_FILL, stroke=RTC_EDGE, color=INK, bold=True))

    # Підпис-логіка внизу
    p.append(text(W / 2, 350, "VDD є → домен їсть VDD, батарейка недоторкана    ·    "
                              "VDD зникло → миттєвий перескок на VBAT",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "power-switch.svg"), W, H, *p)


# ── Фігура 3: драбина рівнів живлення (домен RTC — дно) ──────────────────────
def fig_power_ladder():
    W, H = 720, 400
    p = []
    p.append(text(W / 2, 34, "Рівні живлення кристала: домен RTC — найглибше дно",
                  size=15, bold=True))

    rungs = [
        ("Усе ввімкнено", "ядро + пам'ять + периферія працюють", "десятки мА", OFF_FILL, MUTED),
        ("Сон", "ядро стоїть, пам'ять зберігається", "міліампери", "#f3f0ff", "#6d5bd0"),
        ("Глибокий сон", "живі лише область RTC та її пам'ять/ULP", "частка мА · мкА", "#fff4e6", "#c77d16"),
        ("Живий лише домен RTC", "кварц + лічильники часу від VBAT", "одиниці мкА", RTC_FILL, FIELD),
    ]
    x, w = 90, 540
    y0, bh, gap = 70, 62, 14
    for i, (title, desc, cur, fill, edge) in enumerate(rungs):
        y = y0 + i * (bh + gap)
        # чим глибше — тим вужче, натяк на «дно»
        shrink = i * 18
        p.append(rect(x + shrink, y, w - 2 * shrink, bh, fill=fill, stroke=edge, sw=2, rx=8))
        p.append(text(x + shrink + 16, y + 26, title, size=14, bold=True,
                      color=edge, anchor="start"))
        p.append(text(x + shrink + 16, y + 46, desc, size=11, color=INK, anchor="start"))
        p.append(text(x + w - shrink - 16, y + 36, cur, size=12, bold=True,
                      color=edge, anchor="end"))

    # Стрілка «глибше = менше струму»
    p.append(arrow(50, y0 + 6, 50, y0 + 3 * (bh + gap) + bh - 6, color=INK))
    p.append(text(30, H / 2, "глибше · менше струму", size=12, color=MUTED, anchor="middle"))
    # повертаємо вертикальний підпис
    render_rot(p, 30, H / 2, "глибше · менше струму")

    render(os.path.join(OUT, "power-ladder.svg"), W, H, *p)


def render_rot(plist, x, y, s):
    # прибрати попередній горизонтальний підпис (останній text) і додати повернутий
    plist.pop()
    plist.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
                 % (x, y, FONT, MUTED, x, y, esc(s)))


# ── Фігура 4 (hist): лінія — куди переїжджав годинник ────────────────────────
def fig_hist_timeline():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 34, "Куди переїжджав годинник: від рук користувача в кристал",
                  size=15, bold=True))

    # горизонтальна вісь часу
    axy = 96
    p.append(line(50, axy, W - 40, axy, color=MUTED, sw=2))
    p.append(arrow(W - 60, axy, W - 40, axy, color=MUTED))
    p.append(text(W - 44, axy - 10, "час", size=11, color=MUTED, anchor="end"))

    steps = [
        (110, "до 1984",  "IBM PC / XT",
         ["годинника нема;", "DATE/TIME при", "кожному старті", "рук користувача"], OFF_FILL, MUTED),
        (300, "1984",     "MC146818",
         ["окрема мікросхема +", "батарея + кварц;", "50 байт CMOS;", "перший ПК веде час"], "#eaf0fd", NEG),
        (490, "кін. 1980-х", "DS1287 / DS12887",
         ["кварц і літій —", "в одному корпусі;", "10+ років;", "сумісний з 146818A"], "#fff4e6", "#c77d16"),
        (680, "сьогодні",  "домен у кристалі",
         ["RTC прямо в MCU;", "STM32 VBAT,", "ESP32 RTC;", "зовнішня мікра зайва"], RTC_FILL, FIELD),
    ]
    for cx, when, name, lines, fill, edge in steps:
        # позначка на осі
        p.append(circle(cx, axy, 6, fill=edge, stroke=edge, sw=1))
        p.append(text(cx, axy - 16, when, size=11, bold=True, color=edge))
        # картка під віссю
        bw, bh = 168, 250
        p.append(rect(cx - bw / 2, axy + 24, bw, bh, fill=fill, stroke=edge, sw=2, rx=8))
        p.append(text(cx, axy + 50, name, size=13, bold=True, color=edge))
        for i, ln in enumerate(lines):
            p.append(text(cx, axy + 78 + i * 22, ln, size=11, color=INK))
        # тонка вертикаль від осі до картки
        p.append(line(cx, axy + 6, cx, axy + 24, color=edge, sw=1.5))

    p.append(text(W / 2, H - 12,
                  "щоразу все менше окремих деталей — годинник дедалі глибше всередині чипа",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p)


# ── Фігура 5 (hist): що поглинав корпус — від розсипу до одного кристала ─────
def fig_hist_integration():
    W, H = 740, 360
    p = []
    p.append(text(W / 2, 32, "Що поглинав корпус: розсип → мікра+розсип → усе в одному",
                  size=15, bold=True))

    cols = [
        (135, "MC146818 (1984)", OFF_FILL, MUTED,
         [("мікросхема RTC", True), ("кварц 32768 Гц", False),
          ("батарея (окремо)", False), ("резистори/кола", False)]),
        (370, "DS1287 (кін. 80-х)", "#fff4e6", "#c77d16",
         [("мікросхема RTC", True), ("кварц — всередині", True),
          ("літій — всередині", True), ("один корпус DIP-24", True)]),
        (605, "домен у MCU (нині)", RTC_FILL, FIELD,
         [("RTC — на кристалі", True), ("кварц — зовні, малий", False),
          ("батарея — зовні, VBAT", False), ("окремої мікри нема", True)]),
    ]
    for cx, title, fill, edge, items in cols:
        bw = 205
        p.append(rect(cx - bw / 2, 56, bw, 268, fill=fill, stroke=edge, sw=2, rx=10))
        p.append(text(cx, 82, title, size=13, bold=True, color=edge))
        for i, (lbl, inside) in enumerate(items):
            y = 116 + i * 46
            mc = edge if inside else MUTED
            p.append(fitbox(cx - bw / 2 + 16, y, bw - 32, 34, lbl,
                            size=12, fill=BG, stroke=mc,
                            color=(INK if inside else MUTED), bold=inside))

    # стрілки між колонками
    p.append(arrow(240, 190, 265, 190, color=INK, sw=2))
    p.append(arrow(475, 190, 500, 190, color=INK, sw=2))

    render(os.path.join(OUT, "hist-integration.svg"), W, H, *p)


if __name__ == "__main__":
    fig_domain_boundary()
    fig_power_switch()
    fig_power_ladder()
    fig_hist_timeline()
    fig_hist_integration()
    print("figs done")
