# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір дисплея».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
EINK = "#5b6b7a"     # e-ink: відбивний, нейтрально-сірий
OLED = "#7d3c98"     # OLED: глибокий чорний/контраст
TFT  = "#1f78b4"     # TFT-LCD: кольорова панель
GOLD = "#b9770e"     # застереження / тепле виділення


# ── 1. Лійка вибору: сценарій → обмеження → кандидати ────────────────────────
def fig_funnel():
    W, H = 760, 360
    f = [text(W / 2, 28, "Напрям вибору — згори вниз, від сценарію", size=16, bold=True)]

    # три яруси лійки, що звужуються
    f.append(rect(60, 60, 640, 62, fill="#eef4f8", stroke=INK, sw=1.8))
    f.append(text(380, 86, "СЦЕНАРІЙ", size=13.5, color=TFT, bold=True))
    f.append(text(380, 108, "хто? де? що показує? як часто? скільки живе? почім? у якому корпусі?",
                  size=11, color=MUTED))

    f.append(rect(150, 152, 460, 62, fill="#fff8e6", stroke=INK, sw=1.8))
    f.append(text(380, 178, "ТВЕРДІ ОБМЕЖЕННЯ", size=13.5, color=GOLD, bold=True))
    f.append(text(380, 200, "сонце · енергія · вартість · кабель · розмір · дотик",
                  size=11, color=MUTED))

    f.append(rect(240, 244, 280, 62, fill="#eafaf0", stroke=INK, sw=1.8))
    f.append(text(380, 270, "КАНДИДАТИ", size=13.5, color=FIELD, bold=True))
    f.append(text(380, 292, "e-ink · OLED · TFT-LCD", size=11, color=MUTED))

    f.append(arrow(380, 122, 380, 150, color=INK, sw=2.2))
    f.append(text(440, 142, "вивести", size=10, color=MUTED, anchor="start", italic=True))
    f.append(arrow(380, 214, 380, 242, color=INK, sw=2.2))
    f.append(text(440, 234, "відсіяти", size=10, color=MUTED, anchor="start", italic=True))

    # зустрічна стрілка-антипатерн збоку
    f.append(arrow(700, 300, 700, 64, color=POS, sw=1.6))
    f.append(text(690, 180, "хто йде знизу — впирається", size=9.5, color=POS,
                  anchor="end", italic=True))

    f.append(text(W / 2, 344,
                  "обмеження викидають більшість технологій — і лише тоді порівнюють деталі",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "funnel.svg"), W, H, *f)


# ── 2. Світлове середовище як перший фільтр ──────────────────────────────────
def fig_environment():
    W, H = 760, 300
    f = [text(W / 2, 28, "Світло довкола вирішує клас екрана", size=16, bold=True)]

    # горизонтальна шкала яскравости довкілля
    y = 96
    f.append(line(60, y, 700, y, color=INK, sw=2))
    f.append(arrow(680, y, 702, y, color=INK, sw=2))
    f.append(text(60, y - 14, "темрява", size=11, color=MUTED, anchor="start", italic=True))
    f.append(text(700, y - 14, "пряме сонце", size=11, color=MUTED, anchor="end", italic=True))

    bands = [
        (60, 215, OLED, "OLED", "ідеальний чорний"),
        (215, 385, TFT, "TFT-LCD", "універсал кімнати"),
        (385, 540, GOLD, "яскравий TFT", "+ антивідблиск"),
        (540, 700, EINK, "e-ink / трансфлектив", "відбиває світло"),
    ]
    for x0, x1, col, name, note in bands:
        cx = (x0 + x1) / 2
        f.append(line(x0, y - 6, x0, y + 6, color=INK, sw=1.5))
        f.append(rect(x0 + 6, 132, x1 - x0 - 12, 56, fill=FILL, stroke=col, sw=1.8))
        f.append(fitbox(x0 + 10, 138, x1 - x0 - 20, 24, name, size=11.5, color=col,
                        bold=True, fill=FILL, stroke="none", sw=0))
        f.append(text(cx, 180, note, size=9.5, color=MUTED, italic=True))
    f.append(line(700, y - 6, 700, y + 6, color=INK, sw=1.5))

    f.append(text(W / 2, 232,
                  "там, де темно, виграє той, хто світить сам; де яскраво — той, хто відбиває",
                  size=11, color=INK))
    f.append(text(W / 2, 268,
                  "тисяча нітів підсвітки тоне в полудневому світлі — нітами сонце не переб'єш",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "environment.svg"), W, H, *f)


# ── 3. Енергія: живлення × вміст як рішення 2×2 ──────────────────────────────
def fig_energy():
    W, H = 720, 360
    f = [text(W / 2, 28, "Енергія: живлення × вміст", size=16, bold=True)]

    gx, gy, cw, ch = 200, 70, 230, 110     # сітка 2×2
    # підписи осей
    f.append(text(gx + cw, 56, "статичний вміст", size=11, color=MUTED, bold=True))
    f.append(text(gx + cw + cw, 56, "динамічний вміст", size=11, color=MUTED, bold=True))
    f.append(text(180, gy + ch / 2, "батарея", size=11, color=MUTED, bold=True, anchor="end"))
    f.append(text(180, gy + ch + ch / 2, "мережа", size=11, color=MUTED, bold=True, anchor="end"))

    cells = [
        (gx, gy, EINK, "e-ink", "у спокої не їсть\nнічого — тижні й місяці"),
        (gx + cw, gy, OLED, "OLED, темна тема", "світло лише там,\nде треба"),
        (gx, gy + ch, FIELD, "будь-що зручне", "енергія не тисне"),
        (gx + cw, gy + ch, FIELD, "будь-що зручне", "бери за іншими\nкритеріями"),
    ]
    for x, yy, col, name, note in cells:
        f.append(rect(x + 6, yy + 6, cw - 12, ch - 12, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + cw / 2, yy + 38, name, size=12.5, color=col, bold=True))
        f.append(mtext(x + cw / 2, yy + 60, note, size=9.5, color=MUTED, lh=1.25))

    f.append(text(W / 2, 318,
                  "найжорсткіший кут — батарея плюс статика: тут e-ink поза конкуренцією",
                  size=11, color=INK))
    f.append(text(W / 2, 344,
                  "важить не лише який екран, а й робочий цикл — яку частку часу він світить",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "energy.svg"), W, H, *f)


# ── 4. Справжня ціна дисплея — цілий стос ────────────────────────────────────
def fig_cost():
    W, H = 720, 380
    f = [text(W / 2, 28, "Справжня ціна — це весь стос, а не цифра з прайса", size=15.5, bold=True)]

    # ліворуч: «видима ціна» — сама панель
    f.append(rect(70, 150, 200, 50, fill=FILL, stroke=TFT, sw=2))
    f.append(text(170, 180, "панель", size=13, color=TFT, bold=True))
    f.append(text(170, 130, "видима ціна", size=11, color=MUTED, italic=True))

    f.append(arrow(280, 175, 330, 175, color=INK, sw=2.2))

    # праворуч: стос статей витрат, що чіпляються
    f.append(text(540, 56, "справжня ціна", size=11, color=MUTED, italic=True))
    stack = [
        ("панель", TFT),
        ("контролер дисплея + RAM", OLED),
        ("драйвер підсвітки", GOLD),
        ("контролер дотику", FIELD),
        ("розʼєм + шлейф FPC", EINK),
        ("потужніший МК (кадровий буфер)", POS),
        ("більша батарея", POS),
    ]
    x, y0, w, h = 350, 70, 330, 38
    for i, (label, col) in enumerate(stack):
        yy = y0 + i * (h + 4)
        f.append(rect(x, yy, w, h, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + w / 2, yy + 24, label, size=11, color=col, bold=True))

    f.append(text(W / 2, 360,
                  "дешева панель, що вимагає вдвічі дорожчого МК, — насправді найдорожча",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "cost.svg"), W, H, *f)


# ── 5. Фізичний слід: шлейф, розʼєм, контакти, кріплення ─────────────────────
def fig_footprint():
    W, H = 720, 320
    f = [text(W / 2, 28, "Фізичний слід дисплея — приземлені слабкі місця", size=15.5, bold=True)]

    # панель
    f.append(rect(70, 80, 200, 130, fill="#eef4f8", stroke=TFT, sw=2))
    f.append(text(170, 150, "панель", size=13, color=TFT, bold=True))

    # шлейф FPC до розʼєму на платі
    f.append('<path d="M270 150 C 320 150, 330 240, 380 240" fill="none" '
             'stroke="%s" stroke-width="6" stroke-linecap="round"/>' % GOLD)
    f.append(text(322, 205, "шлейф FPC", size=10.5, color=GOLD, bold=True, anchor="middle"))

    # плата з розʼємом
    f.append(rect(380, 220, 270, 56, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(515, 244, "плата", size=11, color=MUTED))
    f.append(rect(396, 232, 90, 32, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(441, 252, "розʼєм FPC", size=10, color=POS, bold=True))
    # контакти
    for i in range(7):
        cx = 404 + i * 12
        f.append(line(cx, 234, cx, 262, color=POS, sw=1.4))

    # стос зі склом і сенсором (товщина)
    f.append(text(170, 240, "стос: панель + дотик + скло", size=10, color=MUTED, italic=True))
    f.append(line(70, 252, 270, 252, color=MUTED, sw=1.2, dash="4 3"))

    # три застороги
    notes = [
        ("розʼєм FPC", "часта точка відмови", POS),
        ("число контактів", "видає тип інтерфейсу", TFT),
        ("товщина стосу", "мусить улізти в корпус", GOLD),
    ]
    x = 40
    for head, why, col in notes:
        f.append(textbox(x + 105, 296, head, size=10.5, color=col, bold=True,
                         fill=FILL, stroke=col, sw=1.4, min_w=200)[0])
        x += 220

    render(os.path.join(IMG, "footprint.svg"), W, H, *f)


# ── 6. Дерево вибору (worked-приклад): осі сценарію → клас дисплея ────────────
def fig_decision_tree():
    W, H = 800, 470
    f = [text(W / 2, 28, "Дерево вибору: осі сценарію ведуть до класу екрана", size=15.5, bold=True)]

    # корінь
    f.append(rect(40, 210, 150, 56, fill=FILL, stroke=INK, sw=2))
    f.append(text(115, 236, "сценарій", size=12.5, bold=True))
    f.append(text(115, 254, "виробу", size=12.5, bold=True))

    # вузол 1: вміст (статика / динаміка)
    f.append(arrow(190, 238, 232, 238, color=INK, sw=2))
    f.append(rect(232, 208, 150, 60, fill="#fff8e6", stroke=GOLD, sw=1.8))
    f.append(text(307, 232, "вміст?", size=12, color=GOLD, bold=True))
    f.append(text(307, 252, "статика / динаміка", size=9.5, color=MUTED, italic=True))

    # гілка статика → сонце? → живлення?
    f.append(line(382, 222, 430, 130, color=EINK, sw=1.8))
    f.append(text(396, 168, "статика", size=10, color=EINK, anchor="start", italic=True))
    f.append(rect(430, 104, 150, 54, fill=FILL, stroke=EINK, sw=1.6))
    f.append(text(505, 126, "сонце / батарея?", size=10.5, color=EINK, bold=True))
    f.append(text(505, 144, "рідкі оновлення", size=9, color=MUTED, italic=True))
    f.append(arrow(580, 131, 622, 131, color=EINK, sw=1.8))
    f.append(rect(622, 104, 150, 54, fill="#eef2f5", stroke=EINK, sw=2))
    f.append(text(697, 128, "e-ink", size=13, color=EINK, bold=True))
    f.append(text(697, 146, "нуль у спокої", size=9, color=MUTED, italic=True))

    # гілка динаміка → колір? → сонце/контраст?
    f.append(line(382, 254, 430, 330, color=TFT, sw=1.8))
    f.append(text(396, 300, "динаміка", size=10, color=TFT, anchor="start", italic=True))
    f.append(rect(430, 250, 150, 60, fill=FILL, stroke=TFT, sw=1.6))
    f.append(text(505, 274, "колір + швидкість?", size=10.5, color=TFT, bold=True))
    f.append(text(505, 294, "відео, жести, мапа", size=9, color=MUTED, italic=True))

    # під-гілка: темно/контраст → OLED
    f.append(line(580, 268, 622, 210, color=OLED, sw=1.6))
    f.append(text(592, 230, "темно, контраст", size=9, color=OLED, anchor="start", italic=True))
    f.append(rect(622, 182, 150, 46, fill="#f4ecf7", stroke=OLED, sw=2))
    f.append(text(697, 210, "OLED", size=13, color=OLED, bold=True))

    # під-гілка: кімната/живлення є → TFT-LCD
    f.append(line(580, 292, 622, 350, color=TFT, sw=1.6))
    f.append(text(592, 330, "кімната, мережа", size=9, color=TFT, anchor="start", italic=True))
    f.append(rect(622, 326, 150, 50, fill="#eaf2f8", stroke=TFT, sw=2))
    f.append(text(697, 348, "TFT-LCD", size=12.5, color=TFT, bold=True))
    f.append(text(697, 366, "+ ємнісний дотик", size=9, color=MUTED, italic=True))

    # рядок про бюджет МК як наскрізну межу
    f.append(rect(40, 404, 720, 40, fill="#fdf3f2", stroke=POS, sw=1.5))
    f.append(text(W / 2, 423, "наскрізна межа — бюджет МК: кадровий буфер та інтерфейс",
                  size=11, color=POS, bold=True))
    f.append(text(W / 2, 438,
                  "SPI з внутрішньою памʼяттю панелі тримає малий МК; RGB просить кадровий буфер у RAM хоста",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 7. Той самий метод — дві різні відповіді під два вироби ───────────────────
def fig_scorecard():
    W, H = 800, 320
    f = [text(W / 2, 28, "Той самий метод — дві різні відповіді", size=16, bold=True)]

    def card(x, title_, rows, verdict, vcol, vfill):
        f.append(rect(x, 56, 340, 200, fill="#fbfbfc", stroke=INK, sw=1.6))
        f.append(text(x + 170, 82, title_, size=13, bold=True))
        y = 108
        for k, v in rows:
            f.append(text(x + 18, y, k, size=10.5, color=MUTED, anchor="start"))
            f.append(text(x + 322, y, v, size=10.5, bold=True, anchor="end"))
            y += 22
        f.append(rect(x + 50, 218, 240, 30, fill=vfill, stroke=vcol, sw=1.8))
        f.append(text(x + 170, 238, verdict, size=12, color=vcol, bold=True))

    card(40, "Польовий лічильник",
         [("середовище", "вулиця, сонце"), ("живлення", "батарея, роки"),
          ("вміст", "число раз на хв"), ("ввід", "кнопки"), ("ціна", "низька")],
         "→ e-ink", EINK, "#eef2f5")
    card(420, "Кухонний прилад",
         [("середовище", "кімната"), ("живлення", "мережа"),
          ("вміст", "анімація, жести"), ("ввід", "мультитач"), ("ціна", "середня")],
         "→ TFT-LCD + дотик", TFT, "#eaf2f8")

    f.append(text(W / 2, 290,
                  "жодна відповідь не «правильніша» — кожна випливає зі свого сценарію",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "scorecard.svg"), W, H, *f)


if __name__ == "__main__":
    fig_funnel()
    fig_environment()
    fig_energy()
    fig_cost()
    fig_footprint()
    fig_decision_tree()
    fig_scorecard()
    print("OK: 7 figures ->", IMG)
