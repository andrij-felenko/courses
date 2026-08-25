# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-021 — міні герконовий давач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Як працює геркон: дві пластинки в колбі намагнічуються й змикаються ──────
def fig_reed_mechanism():
    W, H = 940, 540
    f = [text(W / 2, 30, "Геркон: магніт намагнічує пластинки — вони притягуються й замикають коло",
              size=15, bold=True)]

    # --- Ліворуч: магніту немає, контакт розімкнений ---
    def capsule(cx, cy, closed):
        # скляна колба
        gw, gh = 250, 84
        gx, gy = cx - gw / 2, cy - gh / 2
        f.append(rect(gx, gy, gw, gh, fill="#eaf3fb", stroke=NEG, sw=2.0, rx=42))
        # дві феромагнітні пластинки-язички, що заходять назустріч
        # ліва пластинка (вивід ліворуч)
        f.append(line(gx - 46, cy, gx + 46, cy, color=INK, sw=3.2))
        # права пластинка (вивід праворуч)
        f.append(line(gx + gw + 46, cy, gx + gw - 46, cy, color=INK, sw=3.2))
        # кінчики: у розімкненому — щілина й вигин; у замкненому — торкаються
        if closed:
            f.append(line(gx + 46, cy, cx - 4, cy, color=INK, sw=3.2))
            f.append(line(gx + gw - 46, cy, cx + 4, cy, color=INK, sw=3.2))
            f.append(circle(cx, cy, 3.4, fill=FIELD, stroke=FIELD, sw=1))
        else:
            # верхня й нижня гілки з помітною щілиною посередині
            f.append(line(gx + 46, cy, cx - 28, cy - 11, color=INK, sw=3.2))
            f.append(line(gx + gw - 46, cy, cx + 28, cy + 11, color=INK, sw=3.2))
            f.append(text(cx, cy - 20, "щілина", size=9.5, color=MUTED))
        return gx, gy, gw, gh

    # Ліва сцена: спокій
    lx = 250
    gx, gy, gw, gh = capsule(lx, 150, closed=False)
    b, _, _ = textbox(lx, 250, "магніту немає\nконтакт РОЗІМКНЕНИЙ\nкола немає струму",
                      size=11, fill=FILL, stroke=NEG)
    f.append(b)

    # Права сцена: піднесли магніт
    rx = 690
    gx2, gy2, gw2, gh2 = capsule(rx, 150, closed=True)
    # магніт-брусок збоку/знизу
    mx, my, mw, mh = rx - 60, 214, 120, 34
    f.append(rect(mx, my, mw / 2, mh, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    f.append(text(mx + mw / 4, my + 22, "N", size=14, bold=True, color=POS))
    f.append(rect(mx + mw / 2, my, mw / 2, mh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(mx + 3 * mw / 4, my + 22, "S", size=14, bold=True, color=NEG))
    # силові лінії від магніту до колби (натяк)
    for dx in (-40, 0, 40):
        f.append(line(rx + dx, my, rx + dx * 0.4, 175, color=MUTED, sw=1.0, dash="4,4"))
    b, _, _ = textbox(rx, 300, "піднесли магніт\nпластинки намагнітились →\nрізнойменні кінці ПРИТЯГЛИСЬ →\nконтакт ЗАМКНУВСЯ",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # Нижня підказка про полярність
    b, _, _ = textbox(W / 2, 430, "Байдуже, яким боком магніт: обидві пластинки з мʼякого феромагнетика,\nмагніт робить із них тимчасові N та S — а протилежні полюси завжди тягнуться.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "reed-mechanism.svg"), W, H, *f)


# ── 2. Внутрішня схема KY-021: геркон + підтяжка 10 кОм на S ────────────────────
def fig_ky021_schematic():
    W, H = 880, 470
    f = [text(W / 2, 30, "Що всередині KY-021: геркон і підтяжка 10 кОм до живлення",
              size=15, bold=True)]

    # рамка плати
    bx, by, bw, bh = 120, 66, 640, 300
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-021", size=11, bold=True, color=MUTED, anchor="start"))

    # шина + (VCC) угорі, шина − (GND) внизу
    vcc_y = by + 60
    gnd_y = by + bh - 40
    f.append(line(bx + 40, vcc_y, bx + bw - 40, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 40, vcc_y - 10, "+  (VCC 3.3–5 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(bx + 40, gnd_y, bx + bw - 40, gnd_y, color=NEG, sw=2.2))
    f.append(text(bx + 40, gnd_y + 22, "−  (GND)", size=11, bold=True, color=NEG, anchor="start"))

    # вузол S (посередині) — вертикаль від точки між резистором і герконом до піна S
    node_x = bx + bw / 2
    node_y = (vcc_y + gnd_y) / 2

    # резистор 10к: від VCC до вузла S (підтяжка вгору)
    rx0 = node_x
    f.append(line(rx0, vcc_y, rx0, node_y - 46, color=INK, sw=1.8))
    # символ резистора (прямокутник)
    f.append(rect(rx0 - 16, node_y - 46, 32, 40, fill=BG, stroke=INK, sw=1.6, rx=3))
    f.append(text(rx0 + 26, node_y - 26, "R  10 кОм", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(rx0 + 26, node_y - 11, "(pull-up)", size=9.5, color=MUTED, anchor="start"))
    f.append(line(rx0, node_y - 6, rx0, node_y, color=INK, sw=1.8))

    # вузол-крапка S
    f.append(circle(node_x, node_y, 3.4, fill=INK, stroke=INK, sw=1))

    # геркон: від вузла S до GND (символ — колба з двома язичками)
    reed_top = node_y
    reed_bot = gnd_y
    f.append(line(node_x, reed_top, node_x, reed_top + 22, color=INK, sw=1.8))
    # колба
    cap_y = reed_top + 22
    cap_h = reed_bot - cap_y - 22
    f.append(rect(node_x - 26, cap_y, 52, cap_h, fill="#eaf3fb", stroke=NEG, sw=1.6, rx=20))
    # два язички з щілиною
    midc = cap_y + cap_h / 2
    f.append(line(node_x, cap_y, node_x, midc - 6, color=INK, sw=2.6))
    f.append(line(node_x - 14, midc - 6, node_x + 4, midc - 6, color=INK, sw=2.6))
    f.append(line(node_x, reed_bot - 22, node_x, midc + 6, color=INK, sw=2.6))
    f.append(line(node_x - 4, midc + 6, node_x + 14, midc + 6, color=INK, sw=2.6))
    f.append(line(node_x, reed_bot - 22, node_x, reed_bot, color=INK, sw=1.8))
    f.append(text(node_x + 40, midc, "геркон", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(node_x + 40, midc + 16, "(N/O)", size=9.5, color=MUTED, anchor="start"))

    # вивід S праворуч від вузла
    f.append(line(node_x, node_y, bx + bw - 40, node_y, color=FIELD, sw=1.8))
    f.append(circle(bx + bw - 40, node_y, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(bx + bw - 30, node_y - 8, "S  (сигнал)", size=11, bold=True, color=FIELD, anchor="start"))

    # пояснення станів — праворуч, окремим блоком поза схемою
    b, _, _ = textbox(W / 2, 418, "магніту немає → геркон розімкнений → підтяжка тримає S = «1» (HIGH)\n"
                                  "піднесли магніт → геркон замкнув S на GND → S = «0» (LOW)",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky021-schematic.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: KY-021 ↔ мікроконтролер ──────────────────────────
def fig_ky021_wiring():
    W, H = 900, 430
    f = [text(W / 2, 30, "Підключення KY-021 до плати: три дроти, вихід — прямо на цифровий пін",
              size=15, bold=True)]

    # Модуль ліворуч
    mx, my, mw, mh = 70, 90, 250, 210
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=NEG, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-021", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 48, "міні-геркон", size=10, color=MUTED))
    # три контактні площадки праворуч на модулі
    pads = [("S", FIELD, my + 90), ("+", POS, my + 135), ("−", NEG, my + 180)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    # Плата праворуч
    bx, by, bw, bh = 600, 90, 240, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("D2", FIELD, by + 90, "цифровий вхід"),
            ("3.3–5 В", POS, by + 135, "живлення"),
            ("GND", NEG, by + 180, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # три дроти між ними — прямі, різного кольору, без перетинів
    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    # застереження про рівень — унизу, окремо
    b, _, _ = textbox(W / 2, 372, "Живлення бери під логіку плати: на 5 В вихід S б’є 5-вольтовими рівнями —\n"
                                  "для 3.3-вольтового входу (ESP32) став середній штир на 3.3 В.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky021-wiring.svg"), W, H, *f)


# ── 4. Брязкіт → дебаунс: сирий сигнал дає купу «клац», таймер робить один ──────
def fig_debounce_timeline():
    W, H = 940, 470
    f = [text(W / 2, 30, "Один прохід магніту — а лічильник рахує п'ять: брязкіт і як його давить таймер",
              size=15, bold=True)]

    x0, x1 = 90, 860           # межі осі часу
    hi, lo = 90, 150           # рівні «1» і «0» для верхньої доріжки

    # --- Верхня доріжка: сирий сигнал з геркона (брязкає) ---
    f.append(text(x0 - 10, (hi + lo) / 2, "сирий S", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(x0 - 10, (hi + lo) / 2 + 15, "(геркон)", size=9, color=MUTED, anchor="end"))
    # сегменти рівня: (початок_x, кінець_x, рівень)  — HIGH до підходу, серія брязкоту, стійкий LOW
    segs = [(x0, 250, hi), (250, 262, lo), (262, 274, hi), (274, 286, lo),
            (286, 296, hi), (296, 305, lo), (305, 314, hi), (314, 520, lo),
            (520, 700, hi)]  # відпустив магніт → знову HIGH
    prev = None
    for (a, b, lv) in segs:
        f.append(line(a, lv, b, lv, color=INK, sw=2.4))
        if prev is not None:
            f.append(line(a, prev, a, lv, color=INK, sw=2.4))
        prev = lv
    # позначки «клац» над зоною брязкоту
    for cx in (256, 280, 300, 309):
        f.append(line(cx, lo + 6, cx, lo + 20, color=POS, sw=1.4))
    f.append(text(288, lo + 38, "брязкіт: 4 хибні спрацювання", size=10, bold=True, color=POS))

    # --- Нижня доріжка: що зарахував таймерний дебаунс ---
    hi2, lo2 = 300, 360
    f.append(text(x0 - 10, (hi2 + lo2) / 2, "після", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(text(x0 - 10, (hi2 + lo2) / 2 + 15, "дебаунсу", size=9, color=MUTED, anchor="end"))
    segs2 = [(x0, 314, hi2), (314, 520, lo2), (520, 700, hi2)]
    prev = None
    for (a, b, lv) in segs2:
        f.append(line(a, lv, b, lv, color=FIELD, sw=2.6))
        if prev is not None:
            f.append(line(a, prev, a, lv, color=FIELD, sw=2.6))
        prev = lv
    # вікно спокою після першого краю
    f.append(line(314, hi2 - 14, 314, lo2 + 14, color=MUTED, sw=1.0, dash="4,4"))
    f.append(line(344, hi2 - 14, 344, lo2 + 14, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text(329, hi2 - 22, "чекаємо", size=9, color=MUTED))
    f.append(text(329, hi2 - 10, "~10 мс", size=9, color=MUTED))
    f.append(text(417, lo2 + 34, "1 зарахований імпульс", size=10, bold=True, color=FIELD))

    # осі часу
    f.append(line(x0, lo + 60, x1, lo + 60, color=MUTED, sw=1.2))
    f.append(text(x1, lo + 60 - 8, "час →", size=10, color=MUTED, anchor="end"))

    # висновок унизу окремим блоком
    b, _, _ = textbox(W / 2, 430, "Правило: помітив край — зафіксуй подію ОДИН раз і 10 мс не слухай пін.\n"
                                  "Брязкіт устигне вщухнути всередині цього вікна — лічба стає чесною.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "debounce-timeline.svg"), W, H, *f)


# ── 5. Пробудження зі сну по замиканню геркона (автономний дверний давач) ───────
def fig_wake_on_pin():
    W, H = 900, 470
    f = [text(W / 2, 30, "Автономний давач: МК спить у нулі струму, замикання геркона його будить",
              size=15, bold=True)]

    # три стани по колу: СПИТЬ → (магніт) → ПРОКИНУВСЯ/діло → знову СПИТЬ
    def statebox(cx, cy, lines, col, fill):
        b, w, h = textbox(cx, cy, lines, size=11, fill=fill, stroke=col, bold=False, min_w=210)
        f.append(b)
        return w, h

    # СПИТЬ (ліворуч)
    statebox(190, 150, "МК СПИТЬ (power-down)\nтактовий генератор стоїть\nструм ≈ 0.1 мкА (ATmega)",
             NEG, "#eaf0fd")
    # діло (праворуч)
    statebox(690, 150, "ПРОКИНУВСЯ\nнадіслав тривогу / полічив\nструм — міліампери, коротко",
             POS, "#fdecea")
    # переходи
    f.append(text(440, 120, "геркон замкнувся → пін упав у LOW", size=11, bold=True, color=FIELD))
    f.append(text(440, 138, "рівневе переривання будить МК", size=10, color=MUTED))
    f.append(arrow(300, 150, 578, 150, color=FIELD, sw=2.2))
    f.append(text(440, 250, "діло зроблено → знову в сон", size=11, bold=True, color=NEG))
    f.append(arrow(578, 205, 300, 205, color=NEG, sw=2.2))

    # чому саме рівень, не край — окрема нота
    b, _, _ = textbox(240, 330, "Чому РІВЕНЬ, а не край:\n"
                                 "у power-down тактовий стоїть,\n"
                                 "тож логіка країв не працює —\n"
                                 "будить лише низький РІВЕНЬ на INT0/INT1",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    b, _, _ = textbox(660, 330, "Що дає підтяжка:\n"
                                 "поки двері зачинені — геркон\n"
                                 "тримає пін у LOW, МК спить;\n"
                                 "відчинили — HIGH, край будить одразу",
                      size=10.5, fill="#fdf4ec", stroke=POS)
    f.append(b)

    # висновок
    b, _, _ = textbox(W / 2, 430, "Сам геркон струму не їсть — він лише замикає коло. Тому давач роками живе від «таблетки»:\n"
                                  "99.99% часу МК спить у мікроамперах, прокидаючись на мілісекунду по кожному руху дверей.",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "wake-on-pin.svg"), W, H, *f)


if __name__ == "__main__":
    fig_reed_mechanism()
    fig_ky021_schematic()
    fig_ky021_wiring()
    fig_debounce_timeline()
    fig_wake_on_pin()
    print("KY-021 figs done ->", IMG)
