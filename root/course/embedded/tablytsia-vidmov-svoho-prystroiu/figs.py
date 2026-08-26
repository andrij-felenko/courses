# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"
GRAYBG  = "#f4f6f8"


def fig_fmea_matrix_structure():
    W, H = 880, 400
    p = []
    p.append(text(W / 2, 34, "Анатомія інженерної матриці FMEA для вбудованої системи", size=15, color=INK, bold=True))

    # Стовпці матриці
    cols = [
        ("ВУЗОЛ / КОМПОНЕНТ", "Схемний блок,\nпідсистема, деталь", BLUEBG, NEG, 130),
        ("ВИД ВІДМОВИ", "Як саме відмовляє\n(обрив, замикання)", AMBERBG, AMBERTX, 135),
        ("ПРИЧИНА", "Фізичний механізм\n(ESD, перегрів, баг)", REDBG, POS, 135),
        ("НАСЛІДОК", "Локальний ефект і\nвплив на систему", REDBG, POS, 140),
        ("ОЦІНКИ", "S · O · D\nRPN / AP", GRAYBG, INK, 100),
        ("КОНТРЗАХІД", "Апаратний захист / діагностика в коді", GREENBG, FIELD, 140),
    ]

    bx = 30
    by = 65
    bh = 82
    xs = []
    for head, sub, fill, col, w in cols:
        p.append(rect(bx, by, w, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(bx + w / 2, by + 22, head, size=10.5, color=col, bold=True))
        for j, ln in enumerate(sub.split("\n")):
            p.append(text(bx + w / 2, by + 44 + j * 16, ln, size=9.5, color=INK))
        xs.append((bx, w))
        bx += w + 8

    # Стрілка наскрізного ланцюга
    p.append(arrow(35, 168, W - 35, 168, color=LINE, sw=2.0))
    p.append(text(W / 2, 186, "Наскрізний інженерний ланцюг: від фізики відмови до коду захисту", size=11, color=MUTED, italic=True))

    # Приклад конкретного рядка
    ex_y = 210
    ex_h = 110
    p.append(rect(30, ex_y, W - 60, ex_h, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(45, ex_y + 24, "Приклад рядка:", size=11.5, color=INK, bold=True, anchor="start"))

    row_data = [
        ("Силовий MOSFET\nклапана 24 В", xs[0][0], xs[0][1]),
        ("Залипання у\nвідкритому стані", xs[1][0], xs[1][1]),
        ("Індуктивний викид,\nпробій стоку", xs[2][0], xs[2][1]),
        ("Некероване\nзатоплення бака", xs[3][0], xs[3][1]),
        ("S=9, O=4, D=8\nRPN=288 (High)", xs[4][0], xs[4][1]),
        ("Снабер + TVS діод;\nструмовий шунт + ADC", xs[5][0], xs[5][1]),
    ]

    for body, x, w in row_data:
        p.append(rect(x, ex_y + 34, w, 66, fill=FILL, stroke=LINE, sw=1.0, rx=6))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + w / 2, ex_y + 55 + j * 17, ln, size=9.5, color=INK))

    p.append(rect(30, 335, W - 60, 48, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=8))
    p.append(text(W / 2, 354, "Головний принцип: FMEA проєктує захист ДО випуску плати й коду,", size=11, color=AMBERTX, bold=True))
    p.append(text(W / 2, 372, "перетворюючи кожен виявлений ризик на вимогу до схеми або рядок прошивки.", size=10.2, color=INK))

    render(os.path.join(OUT, "fmea-matrix-structure.svg"), W, H, *p,
           title="Структура інженерної матриці FMEA")


def fig_rpn_vs_ap_matrix():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 32, "Матриця пріоритету дій (Action Priority) проти пастки чистого RPN", size=15, color=INK, bold=True))

    # Лівий блок: 2D площина S × O
    gw = 380
    gh = 300
    gx = 50
    gy = 60

    p.append(rect(gx, gy, gw, gh, fill=BG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(gx + gw / 2, gy + 24, "Розподіл пріоритетів (S × O)", size=12.5, color=INK, bold=True))

    # Зони
    # High zone (S=9..10)
    p.append(rect(gx + 18, gy + 42, gw - 36, 68, fill=REDBG, stroke=POS, sw=1.5, rx=6))
    p.append(text(gx + gw / 2, gy + 68, "S = 9..10: Високий пріоритет (High Priority)", size=11, color=POS, bold=True))
    p.append(text(gx + gw / 2, gy + 90, "Катастрофічний наслідок: захист обов'язковий", size=9.8, color=INK))

    # Medium zone (S=7..8 або S=5..6 при високому O)
    p.append(rect(gx + 18, gy + 120, gw - 36, 76, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=6))
    p.append(text(gx + gw / 2, gy + 146, "S = 7..8 (або S=5..6 та O≥5): Середній (Medium)", size=10.8, color=AMBERTX, bold=True))
    p.append(text(gx + gw / 2, gy + 168, "Суттєва деградація: потрібні заходи в коді й схемі", size=9.8, color=INK))

    # Low zone (S=1..4 або низькі O і D)
    p.append(rect(gx + 18, gy + 206, gw - 36, 80, fill=GREENBG, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(gx + gw / 2, gy + 232, "S = 1..4: Низький пріоритет (Low Priority)", size=10.8, color=FIELD, bold=True))
    p.append(text(gx + gw / 2, gy + 254, "Незначний вплив або надійно ізольована відмова", size=9.8, color=INK))
    p.append(text(gx + gw / 2, gy + 272, "Достатньо штатного моніторингу та логування", size=9.4, color=MUTED, italic=True))

    # Правий блок: Порівняння однакових RPN
    rx = 460
    rw = 370
    p.append(rect(rx, gy, rw, gh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, gy + 24, "Пастка множення RPN = S · O · D", size=12.5, color=INK, bold=True))

    # Кейс 1
    p.append(rect(rx + 15, gy + 45, rw - 30, 102, fill=BG, stroke=POS, sw=1.8, rx=6))
    p.append(text(rx + rw / 2, gy + 70, "Випадок А: Відмова клапана (пробій ключа)", size=11, color=INK, bold=True))
    p.append(text(rx + rw / 2, gy + 92, "S = 10,  O = 2,  D = 9", size=11.5, color=INK))
    p.append(text(rx + rw / 2, gy + 115, "RPN = 180  →  Action Priority = HIGH", size=12, color=POS, bold=True))
    p.append(text(rx + rw / 2, gy + 134, "Смертельний ризик. Лагодити першим!", size=9.6, color=POS, italic=True))

    # Кейс 2
    p.append(rect(rx + 15, gy + 158, rw - 30, 102, fill=BG, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(rx + rw / 2, gy + 183, "Випадок Б: Згас додатковий LED індикації", size=11, color=INK, bold=True))
    p.append(text(rx + rw / 2, gy + 205, "S = 3,  O = 6,  D = 10", size=11.5, color=INK))
    p.append(text(rx + rw / 2, gy + 228, "RPN = 180  →  Action Priority = LOW", size=12, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, gy + 247, "Косметичний збій. Не зупиняє проєкт.", size=9.6, color=FIELD, italic=True))

    p.append(text(rx + rw / 2, gy + 282, "Однаковий RPN=180 приховує протилежну критичність!", size=10, color=POS, bold=True))

    p.append(rect(50, 375, W - 100, 32, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(W / 2, 396, "Методологія AIAG & VDA оцінює логіку пріоритетів за S, O, D послідовно, а не сліпим множенням.", size=10, color=INK))

    render(os.path.join(OUT, "rpn-vs-ap-matrix.svg"), W, H, *p,
           title="Матриця Action Priority проти чистого RPN")


def fig_embedded_failure_taxonomy():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 32, "Класифікація типових відмов у вбудованих системах", size=15, color=INK, bold=True))

    cols = [
        ("Електричні та фізичні", REDBG, POS, [
            ("ESD latch-up", "Паразитний тиристор замикає\nлінію живлення на землю"),
            ("Тепловий розгін", "Зростання струму випалює\nкристал LDO чи ключа"),
            ("Індуктивний викид", "Котушка реле пробиває стік\nтранзистора при розмиканні"),
            ("Тріщини MLCC", "Вигин друкованої плати закорочує\nкерамічний конденсатор"),
            ("Втома пайки", "Олов'яні вуса та мікротріщини\nпід BGA/QFN корпусами"),
        ]),
        ("Програмні та системні", BLUEBG, NEG, [
            ("Stack Overflow", "Переповнення затирає Task\nControl Block у FreeRTOS"),
            ("Зависання I2C шини", "Slave тримає лінію SDA в LOW\nпісля ресету мікроконтролера"),
            ("Deadlock потоків", "Взаємне блокування задач\nна захищених м'ютексах"),
            ("Brownout Flash Write", "Зникнення живлення під час\nзапису сектору пам'яті"),
            ("Watchdog Starvation", "Головний цикл завис, сторож\nне скинуто вчасно"),
        ]),
        ("Механічні та середовищні", AMBERBG, AMBERTX, [
            ("Фретинг роз'ємів", "Мікровібрація стирає позолоту\nконтактів і викликає окислення"),
            ("Обрив жили джгута", "Втома металу біля кабельного\nвводу або притиску"),
            ("Брязкіт кнопок", "Окислення мембрани, хибні\nсерійні спрацьовування"),
            ("Конденсат під лаком", "Волога накопичується під\nпошкодженим конформним лаком"),
            ("Зрив тактування кварцу", "Вібрація або паразитна ємність\nбруду зриває генерацію"),
        ]),
    ]

    col_w = 264
    col_h = 375
    bx = 28
    by = 52

    for head, fill, stroke_col, items in cols:
        p.append(rect(bx, by, col_w, col_h, fill=fill, stroke=stroke_col, sw=1.8, rx=8))
        p.append(text(bx + col_w / 2, by + 24, head, size=12.5, color=stroke_col, bold=True))

        iy = by + 40
        for title_it, desc_it in items:
            p.append(rect(bx + 8, iy, col_w - 16, 58, fill=BG, stroke=stroke_col, sw=1.0, rx=5))
            p.append(text(bx + 16, iy + 18, title_it, size=10.5, color=stroke_col, bold=True, anchor="start"))
            for j, ln in enumerate(desc_it.split("\n")):
                p.append(text(bx + 16, iy + 34 + j * 14, ln, size=9.2, color=INK, anchor="start"))
            iy += 64

        bx += col_w + 16

    render(os.path.join(OUT, "embedded-failure-taxonomy.svg"), W, H, *p,
           title="Класифікація типових відмов у вбудованих пристроях")


def fig_mitigation_hierarchy():
    W, H = 880, 400
    p = []
    p.append(text(W / 2, 32, "Ієрархія інженерних контрзаходів FMEA (що впроваджувати першим)", size=15, color=INK, bold=True))

    levels = [
        ("1. Усунення на рівні схемотехніки", "Зміна топології, вибір компонентів із запасом (derating), ізоляція вразливого вузла", GREENBG, FIELD, 780),
        ("2. Апаратні захисні бар'єри", "TVS-діоди, самовідновні запобіжники PTC, зовнішній супервізор живлення, eFuse", BLUEBG, NEG, 700),
        ("3. Надлишковість і резервування", "Дублювання давачів (барометр + GPS), резервне живлення, аварійний канал зв'язку", AMBERBG, AMBERTX, 620),
        ("4. Активна самодіагностика прошивки", "Watchdog, відновлення I2C (9 тактів SCL), валідація діапазонів, перехід у Failsafe", GRAYBG, INK, 540),
        ("5. Пасивне сповіщення та інструкції", "Світлодіодна індикація помилки, запис коду відмови в Flash-лог, регламентний огляд", REDBG, POS, 460),
    ]

    by = 65
    lh = 56
    for i, (title_l, desc_l, fill, col, w) in enumerate(levels):
        x = (W - w) / 2
        p.append(rect(x, by, w, lh, fill=fill, stroke=col, sw=1.6, rx=7))
        p.append(text(W / 2, by + 22, title_l, size=11.5, color=col, bold=True))
        p.append(text(W / 2, by + 42, desc_l, size=9.8, color=INK))
        by += lh + 8

    # Стрілка ефективності зліва
    p.append(arrow(35, 350, 35, 75, color=FIELD, sw=2.2))
    p.append(text(30, 210, "Ефективність захисту", size=10.5, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "mitigation-hierarchy.svg"), W, H, *p,
           title="Ієрархія інженерних контрзаходів FMEA")


if __name__ == "__main__":
    fig_fmea_matrix_structure()
    fig_rpn_vs_ap_matrix()
    fig_embedded_failure_taxonomy()
    fig_mitigation_hierarchy()
    print("Всі фігури згенеровано успішно.")
