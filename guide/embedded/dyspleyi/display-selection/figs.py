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


# ── 8. Граничні умови: клас × (температура, статика) ──────────────────────────
def fig_limits():
    W, H = 780, 380
    f = [text(W / 2, 28, "Граничні умови розводять класи інакше за кімнату", size=15.5, bold=True)]

    # три колонки-класи
    cols = [
        (40, EINK, "e-ink", "#eef2f5"),
        (290, OLED, "OLED", "#f4ecf7"),
        (540, TFT, "TFT-LCD", "#eaf2f8"),
    ]
    colw = 210
    for x, col, name, fillc in cols:
        f.append(rect(x, 56, colw, 44, fill=fillc, stroke=col, sw=2))
        f.append(text(x + colw / 2, 84, name, size=14, color=col, bold=True))

    # три ряди-межі
    rows = [
        ("мороз", 120, [
            ("кольоровий не оживе < 0 °C;\nмонохром — широкотемп.", GOLD),
            ("тримає холод\nкраще за LCD", FIELD),
            ("вʼязкість росте —\nкартинка розмазується", POS),
        ]),
        ("спека", 210, [
            ("здебільшого\nстерпно", FIELD),
            ("крадe ресурс —\nорганіка старіє швидше", POS),
            ("падає контраст,\nросте старіння", GOLD),
        ]),
        ("роки статики", 300, [
            ("ідеально —\nстатика для нього", FIELD),
            ("вигоряння: диференційне\nстаріння пікселів", POS),
            ("статики не\nбоїться зовсім", FIELD),
        ]),
    ]
    for label, ry, cells in rows:
        f.append(text(28, ry + 26, label, size=11, color=MUTED, bold=True, anchor="start"))
        for (x, col, name, fillc), (note, ncol) in zip(cols, cells):
            f.append(fitbox(x, ry, colw, 66, note, size=10, color=ncol,
                            fill=FILL, stroke=ncol, sw=1.3))

    f.append(text(W / 2, 360,
                  "прилад для країв діапазону часто вимагає іншого класу, ніж той самий для кімнати",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "limits.svg"), W, H, *f)


# ── Вставка comp-memory-lcd ───────────────────────────────────────────────────
MIP = "#0e7c7b"      # memory-in-pixel: бірюзовий, окремий клас


# ── 9. Піксель MIP: комірка SRAM + відбивна РК-заслінка ──────────────────────
def fig_mip_pixel():
    W, H = 760, 380
    f = [text(W / 2, 28, "Один піксель MIP: біт памʼяті сидить під самою заслінкою",
              size=15.5, bold=True)]

    # Ліворуч: звичайний TFT-піксель — конденсатор, що тече
    f.append(text(190, 62, "звичайний TFT-піксель", size=12, color=TFT, bold=True))
    f.append(rect(60, 78, 260, 210, fill="#eef4f8", stroke=TFT, sw=1.8))
    f.append(fitbox(80, 100, 220, 40, "транзистор доступу", size=10.5, color=TFT,
                    fill=FILL, stroke=TFT, sw=1.3))
    f.append(fitbox(80, 150, 220, 44, "конденсатор тримає\nАНАЛОГОВУ напругу", size=10.5,
                    color=INK, fill=FILL, stroke=MUTED, sw=1.3))
    f.append(text(190, 214, "заряд стікає за мілісекунди", size=9.5, color=POS, italic=True))
    f.append(fitbox(80, 226, 220, 40, "→ мусить оновлюватись\nдесятки разів на секунду",
                    size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.3))

    # Праворуч: MIP-піксель — цифровий біт SRAM
    f.append(text(560, 62, "піксель MIP", size=12, color=MIP, bold=True))
    f.append(rect(430, 78, 270, 210, fill="#e8f6f5", stroke=MIP, sw=2))
    f.append(fitbox(450, 100, 230, 44, "1-бітна комірка SRAM\n(два інвертори-засувка)",
                    size=10.5, color=MIP, fill=FILL, stroke=MIP, sw=1.3))
    f.append(fitbox(450, 154, 230, 40, "біт тримає стан САМ,\nпоки є живлення", size=10.5,
                    color=INK, fill=FILL, stroke=MIP, sw=1.3))
    f.append(text(565, 214, "нічого не стікає — нема що оновлювати", size=9, color=FIELD,
                  italic=True))
    f.append(fitbox(450, 226, 230, 40, "→ картинка стоїть даром,\nоновлення — лише коли хочеш",
                    size=10, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.3))

    # Спільний низ: відбивна РК-заслінка над дзеркалом-відбивачем
    f.append(line(60, 306, 700, 306, color=MUTED, sw=1, dash="3 3"))
    f.append(text(W / 2, 330,
                  "над кожним пікселем — та сама відбивна РК-заслінка: біт лише каже їй «пропускати світло чи ні»",
                  size=10.5, color=INK))
    f.append(text(W / 2, 356,
                  "підсвітки немає — екран світиться відбитим навколишнім світлом, як папір",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "mip-pixel.svg"), W, H, *f)


# ── 10. «Перший байт»: кадр запису рядків по SPI ─────────────────────────────
def fig_mip_frame():
    W, H = 860, 360
    f = [text(W / 2, 28, "Кадр запису: командний байт → адреса рядка → пікселі → нулі",
              size=15, bold=True)]

    # Стрічка байтів
    y = 74
    cells = [
        ("CS↑", "SCS стає\nВИСОКИМ", MIP, 78),
        ("0x80", "команда\n«писати рядок»", TFT, 96),
        ("addr", "номер рядка\n(з 1)", GOLD, 96),
        ("D0…Dn", "біти пікселів\nрядка (LSB-first)", INK, 130),
        ("0x00", "фіктивний\nбайт-кінець рядка", MUTED, 108),
        ("…", "далі наступні\nрядки так само", MUTED, 90),
        ("0x0000", "два нулі —\nкінець кадру", MUTED, 108),
        ("CS↓", "SCS стає\nНИЗЬКИМ", MIP, 78),
    ]
    x = 30
    for head, note, col, w in cells:
        f.append(rect(x, y, w, 54, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + w / 2, y + 24, head, size=12, color=col, bold=True))
        f.append(mtext(x + w / 2, y + 78, note, size=8.8, color=MUTED, lh=1.15))
        if x > 30:
            f.append(line(x - 4, y + 27, x, y + 27, color=INK, sw=1.2))
        x += w + 4

    # Три застороги під стрічкою
    f.append(rect(40, 190, 780, 44, fill="#fdf3f2", stroke=POS, sw=1.5))
    f.append(text(W / 2, 208, "CS активний ВИСОКИМ рівнем — навпаки до звичайного SPI",
                  size=11, color=POS, bold=True))
    f.append(text(W / 2, 226,
                  "тримати CS високим весь кадр і опустити наприкінці; забудеш опустити — панель не зафіксує запис",
                  size=9.5, color=MUTED, italic=True))

    f.append(rect(40, 244, 780, 44, fill="#fff8e6", stroke=GOLD, sw=1.5))
    f.append(text(W / 2, 262, "Біти йдуть МОЛОДШИМ уперед (LSB-first)", size=11,
                  color=GOLD, bold=True))
    f.append(text(W / 2, 280,
                  "командний байт, адресу й пікселі шлють дзеркально до звичного MSB-first — або перевертай байти в коді",
                  size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 320,
                  "весь кадр — це командний байт, тоді пари «адреса + рядок пікселів + нуль», і два нулі під кінець",
                  size=10.5, color=INK))
    f.append(text(W / 2, 344,
                  "малюєш лише змінені рядки — решту не чіпаєш, і панель тримає їх сама",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "mip-frame.svg"), W, H, *f)


# ── 11. Чому потрібна інверсія COM: DC-зміщення руйнує РК ─────────────────────
def fig_mip_vcom():
    W, H = 780, 400
    f = [text(W / 2, 28, "Інверсія COM: постійна напруга на РК — повільна отрута",
              size=15.5, bold=True)]

    # Ліворуч: постійна полярність → іони збираються → мертвий піксель
    f.append(text(200, 60, "БЕЗ інверсії", size=12, color=POS, bold=True))
    f.append(rect(60, 74, 280, 120, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(200, 98, "напруга завжди одного знаку", size=10.5, color=INK))
    # заряди дрейфують до одного боку
    for i in range(6):
        f.append(text(90 + i * 20, 128, "+", size=13, color=POS, bold=True))
        f.append(text(300 - i * 6, 158, "−", size=13, color=NEG, bold=True))
    f.append(text(200, 182, "іони дрейфують і осідають на електроді", size=9.5,
                  color=MUTED, italic=True))
    f.append(fitbox(60, 202, 280, 40, "→ електрохімічний розклад,\nзалишкова поляризація, мертві пікселі",
                    size=10, color=POS, fill=FILL, stroke=POS, sw=1.3))

    # Праворуч: змінна полярність → нульове середнє → живий піксель
    f.append(text(580, 60, "З інверсією COM", size=12, color=FIELD, bold=True))
    f.append(rect(440, 74, 280, 120, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(580, 98, "знак періодично перевертається", size=10.5, color=INK))
    # хвиля-меандр
    pts = "460,150 490,150 490,120 550,120 550,150 610,150 610,120 670,120 670,150 700,150"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, FIELD))
    f.append(text(580, 178, "середня напруга на РК = 0", size=9.5, color=MUTED, italic=True))
    f.append(fitbox(440, 202, 280, 40, "→ іони не встигають осісти,\nрідкий кристал живе роками",
                    size=10, color=FIELD, fill=FILL, stroke=FIELD, sw=1.3))

    # Низ: два способи давати інверсію
    f.append(text(W / 2, 274, "Два способи вмикати інверсію (вибирає вивід EXTMODE):",
                  size=12, bold=True))

    f.append(rect(60, 292, 320, 80, fill="#e8f6f5", stroke=MIP, sw=1.8))
    f.append(text(220, 314, "апаратний  ·  EXTMODE = 1", size=11, color=MIP, bold=True))
    f.append(mtext(220, 336, "окремий вивід EXTCOMIN;\nмікроконтролер (чи RC/лічильник) смикає\nйого 1–60 Гц навіть без оновлень",
                   size=9.3, color=MUTED, lh=1.2))

    f.append(rect(400, 292, 320, 80, fill="#eef4f8", stroke=TFT, sw=1.8))
    f.append(text(560, 314, "програмний  ·  EXTMODE = 0", size=11, color=TFT, bold=True))
    f.append(mtext(560, 336, "окремого виводу нема; біт інверсії\nїде в командному байті кожного кадру —\nтреба слати кадр регулярно",
                   size=9.3, color=MUTED, lh=1.2))
    render(os.path.join(IMG, "mip-vcom.svg"), W, H, *f)


# ── 12. Ламбертів перехід «люкси → кд/м²» і множник π (для math-вставки) ──────
def fig_lambert_pi():
    import math
    W, H = 820, 380
    f = [text(W / 2, 26, "Звідки π у переході освітленість → яскравість", size=16, bold=True)]

    # ── Ліва панель: падаюче світло, косинусна пелюстка, інтеграл ────────────
    cx, base = 210, 250              # точка на поверхні / рівень поверхні
    surf_l, surf_r = 70, 350
    f.append(text(210, 56, "Ламбертів розсіювач", size=12.5, color=EINK, bold=True))
    # поверхня
    f.append(line(surf_l, base, surf_r, base, color=INK, sw=2.6))
    f.append(text(surf_r, base + 18, "скло, відбивність ρ", size=10, color=MUTED, anchor="end"))
    # падаюча освітленість E — пучок стрілок згори
    for dx in (-42, 0, 42):
        f.append(arrow(cx + dx - 24, 78, cx + dx, base - 4, color=GOLD, sw=1.8))
    f.append(text(cx - 74, 92, "E", size=15, color=GOLD, bold=True, italic=True))
    f.append(text(cx - 74, 108, "лк", size=9.5, color=MUTED))

    # косинусна пелюстка сили світла I(θ)=I₀·cosθ — коло, дотичне до поверхні
    R = 92
    pts = []
    steps = 40
    for i in range(steps + 1):
        th = -math.pi / 2 + math.pi * i / steps      # −90°..+90° від вертикалі
        r = R * math.cos(th)                          # I₀·cosθ
        px = cx + r * math.sin(th)
        py = base - r * math.cos(th)
        pts.append("%.1f,%.1f" % (px, py))
    f.append('<polygon points="%s" fill="#7d3c9822" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), OLED))
    # нормаль і зразковий промінь під кутом
    f.append(line(cx, base, cx, base - R - 6, color=INK, sw=1.3, dash="4,3"))
    f.append(text(cx + 8, base - R - 2, "нормаль", size=9, color=MUTED, anchor="start"))
    th0 = math.radians(38)
    rr = R * math.cos(th0)
    f.append(arrow(cx, base, cx + rr * math.sin(th0), base - rr * math.cos(th0),
                   color=OLED, sw=1.8))
    f.append(text(cx + 40, base - 30, "I(θ) = I₀·cos θ", size=10.5, color=OLED, anchor="start"))

    # інтеграл по півсфері → π
    box = textbox(210, base + 78,
                  "Φ = ∫ I₀·cos θ dΩ = π·I₀\n⇒  L = Φ/π = ρ·E / π",
                  size=11.5, color=INK, fill="#eef4f8", stroke=TFT, sw=1.6, pad=10)
    f.append(box[0])

    # роздільник
    f.append(line(W / 2, 48, W / 2, H - 40, color="#d7dde3", sw=1.4, dash="5,4"))

    # ── Права панель: два косинуси скорочуються → яскравість стала ───────────
    rx = 600
    f.append(text(rx, 56, "Чому яскравість не залежить від кута", size=12.5, color=EINK, bold=True))
    ry = 176
    # поверхня-відрізок, який дивимось згори і збоку
    f.append(line(rx - 120, ry, rx + 120, ry, color=INK, sw=2.6))
    # око прямо згори
    f.append(circle(rx, ry - 90, 12, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(rx, ry - 86, "око", size=8.5, color=FIELD))
    f.append(arrow(rx, ry - 76, rx, ry - 6, color=FIELD, sw=1.6))
    f.append(text(rx - 26, ry - 44, "прямо", size=9.5, color=MUTED, anchor="end"))
    # око під кутом
    ang = math.radians(50)
    ex, ey = rx + 132 * math.sin(ang), ry - 132 * math.cos(ang)
    f.append(circle(ex, ey, 12, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(ex + 16, ey + 2, "око", size=8.5, color=FIELD, anchor="start"))
    f.append(arrow(ex - 2, ey + 8, rx + 5, ry - 5, color=FIELD, sw=1.6))
    f.append(text(rx + 40, ry - 42, "збоку", size=9.5, color=MUTED, anchor="start"))

    b1 = textbox(rx, ry + 66,
                 "менше світла:  ∝ cos θ\nвужча проекція:  ∝ cos θ",
                 size=11, color=INK, fill="#fff8e6", stroke=GOLD, sw=1.5, pad=9)
    f.append(b1[0])
    b2 = textbox(rx, ry + 128,
                 "два cos θ скорочуються ⇒ L = стала",
                 size=11.5, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=9)
    f.append(b2[0])

    f.append(text(W / 2, H - 16,
                  "весь відбитий потік ρ·E збирається в π·I₀ — тому яскравість відблиску дорівнює ρ·E/π",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "lambert-pi.svg"), W, H, *f)


if __name__ == "__main__":
    fig_funnel()
    fig_environment()
    fig_energy()
    fig_cost()
    fig_footprint()
    fig_decision_tree()
    fig_scorecard()
    fig_limits()
    fig_mip_pixel()
    fig_mip_frame()
    fig_mip_vcom()
    fig_lambert_pi()
    print("OK: 12 figures ->", IMG)
