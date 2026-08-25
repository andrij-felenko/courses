# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def block():
    """Пристрій наземного модуля: USB → міст USB-UART → 8051+радіо → узгодження → антена."""
    W, H = 900, 340
    f = []

    # горизонтальний ланцюг блоків, з великими проміжками щоб підписи не наклались
    y = 150
    bh = 84

    # USB-роз'єм
    b, w, h = textbox(90, y, ["Роз'єм", "USB"], size=15, min_w=110, fill="#eef4ff")
    f.append(b)
    ux = 90 + w / 2

    # міст USB-UART
    b, w, h = textbox(280, y, ["Міст USB-UART", "CP210x / CH340", "(→ COM-порт)"], size=14, min_w=180)
    f.append(b)
    m_l, m_r = 280 - w / 2, 280 + w / 2

    # МК + радіо
    b, w, h = textbox(510, y, ["8051-МК + радіо", "Si1000 (Si4432)", "прошивка SiK"], size=14, min_w=180, fill="#eafaf1")
    f.append(b)
    c_l, c_r = 510 - w / 2, 510 + w / 2

    # ланцюг узгодження
    b, w, h = textbox(710, y, ["Узгодження", "+ фільтр"], size=14, min_w=120)
    f.append(b)
    p_l, p_r = 710 - w / 2, 710 + w / 2

    # антена
    ax = 830
    f.append(line(ax, y - 30, ax, y + 18, sw=2))
    f.append(line(ax, y - 30, ax - 12, y - 48, sw=2))
    f.append(line(ax, y - 30, ax + 12, y - 48, sw=2))
    f.append(text(ax, y + 40, "Антена", size=13))

    # з'єднання-стрілки
    f.append(arrow(ux, y, m_l, y))
    f.append(arrow(m_r, y, c_l, y))
    f.append(arrow(c_r, y, p_l, y))
    f.append(arrow(p_r, y, ax, y))

    # підпис даних над мостом→МК: UART 57600
    f.append(text((m_r + c_l) / 2, y - 20, "UART 57600", size=12, color=MUTED))
    # RF праворуч
    f.append(text((p_r + ax) / 2, y - 20, "радіо", size=12, color=MUTED))

    # живлення знизу: USB 5 В → регулятор 3.3 В
    py = 262
    b2, w2, h2 = textbox(280, py, ["Регулятор 3.3 В"], size=13, min_w=150, fill="#fff7e6")
    f.append(b2)
    # від USB вниз до живлення
    f.append(line(ux, y + 42, ux, py, color=MUTED))
    f.append(arrow(ux, py, 280 - w2 / 2, py, color=MUTED))
    f.append(text((ux + 280 - w2 / 2) / 2, py - 10, "5 В із USB", size=11, color=MUTED))
    # від регулятора до чипів угору
    f.append(arrow(280 + w2 / 2, py, 510, py, color=MUTED))
    f.append(line(510, py, 510, y + 42, color=MUTED))
    f.append(text((280 + w2 / 2 + 510) / 2, py - 10, "3.3 В на радіочастину", size=11, color=MUTED))

    render(os.path.join(IMG, 'block.svg'), W, H, *f,
           title="Наземний модуль зсередини: USB живить і несе дані, чип SiK робить радіо")


def wiring():
    """Підключення: наземний модуль у ПК по USB; пара з повітряним — по ефіру за трьома збігами."""
    W, H = 900, 420
    f = []

    # НАЗЕМНА сторона (ліворуч)
    # ноутбук
    f.append(rect(60, 150, 150, 95, fill="#eef4ff"))
    f.append(text(135, 178, "Наземна станція", size=13, bold=True))
    f.append(text(135, 200, "Mission Planner", size=12, color=MUTED))
    f.append(text(135, 220, "/ QGroundControl", size=12, color=MUTED))

    # наземний модуль
    b, w, h = textbox(135, 320, ["Наземний модуль", "(роз'єм USB)"], size=13, min_w=170, fill="#eafaf1")
    f.append(b)
    # USB-кабель — підписи збоку від лінії, щоб не перетинались
    f.append(arrow(135, 297 + 3, 135, 245 + 3, color=INK))
    f.append(text(205, 268, "USB", size=12, color=MUTED, anchor="start"))
    f.append(text(205, 285, "COM 57600", size=11, color=MUTED, anchor="start"))

    # ПОВІТРЯНА сторона (праворуч)
    # політний контролер
    f.append(rect(690, 150, 150, 95, fill="#eef4ff"))
    f.append(text(765, 178, "Політний", size=13, bold=True))
    f.append(text(765, 197, "контролер", size=13, bold=True))
    f.append(text(765, 220, "Pixhawk / ArduPilot", size=11, color=MUTED))

    # повітряний модуль
    b, w, h = textbox(765, 320, ["Повітряний модуль", "(6 пінів, UART)"], size=13, min_w=180, fill="#eafaf1")
    f.append(b)
    f.append(arrow(765, 297 + 3, 765, 245 + 3, color=INK))
    f.append(text(695, 268, "TELEM-порт", size=12, color=MUTED, anchor="end"))
    f.append(text(695, 285, "UART 5 В", size=11, color=MUTED, anchor="end"))

    # РАДІОЛІНК між модулями — мітка ВИЩЕ лінії, з чистим проміжком
    ry = 316
    f.append(text(450, ry - 24, "радіоефір 433 / 915 МГц", size=13, color=POS, bold=True))
    f.append(line(300, ry, 600, ry, color=POS, sw=2, dash="7 6"))

    # умова спарення — рамка по центру знизу, нижче лінії з великим проміжком
    cond = ("Пара працює, лише якщо на ОБОХ модулях збігаються:\n"
            "NetID  ·  швидкість ефіру  ·  вікно частот (min/max)")
    f.append(fitbox(250, 366, 400, 44, cond, size=12, fill="#fff7e6", stroke=FIELD))

    render(os.path.join(IMG, 'wiring.svg'), W, H, *f,
           title="Наземний модуль з'єднує ПК з дроном: USB тут, радіоміст туди")


def command_mode():
    """Дві машини стану модуля: прозорий режим ↔ командний, перехід через +++ з тишею."""
    W, H = 900, 380
    f = []

    # два великих стани — ліворуч прозорий, праворуч командний
    ty = 150
    # прозорий режим
    b1, w1, h1 = textbox(210, ty, ["ПРОЗОРИЙ РЕЖИМ",
                                   "усе з UART → в ефір",
                                   "усе з ефіру → в UART"],
                         size=15, min_w=250, fill="#eafaf1")
    f.append(b1)
    # командний режим
    b2, w2, h2 = textbox(690, ty, ["КОМАНДНИЙ РЕЖИМ",
                                   "модуль слухає AT-команди",
                                   "нічого не йде в ефір"],
                         size=15, min_w=250, fill="#eef4ff")
    f.append(b2)

    r1 = 210 + w1 / 2   # правий край лівого стану
    l2 = 690 - w2 / 2   # лівий край правого стану

    # перехід уперед: +++ з тишею (верхня дуга)
    ay = ty - h1 / 2 - 14
    f.append(arrow(r1, ty - 18, l2, ty - 18))
    f.append(text((r1 + l2) / 2, ty - 46, "+++", size=17, color=POS, bold=True))
    f.append(text((r1 + l2) / 2, ty - 26, "(тиша 1 с до і 1 с після)", size=12, color=MUTED))

    # перехід назад: ATO (нижня дуга)
    f.append(arrow(l2, ty + 18, r1, ty + 18))
    f.append(text((r1 + l2) / 2, ty + 34, "ATO  або  ATZ", size=15, color=NEG, bold=True))

    # у командному режимі — стрічка типових команд знизу праворуч
    cy = 300
    cmds = "ATI5  (усі S-регістри)   ·   ATSn=X  (записати)   ·   AT&W  (зберегти)   ·   ATZ  (перезавантажити)"
    f.append(fitbox(130, cy, 640, 46, cmds, size=12, fill="#fff7e6", stroke=FIELD))
    f.append(text(450, cy - 10, "у командному режимі доступні:", size=12, color=MUTED))

    render(os.path.join(IMG, 'command-mode.svg'), W, H, *f,
           title="Дві машини стану модуля: прозорий потік ↔ командний режим")


def mav_parse():
    """Потоковий розбірник кадру MAVLink v1: STX → LEN → заголовок → дані(LEN) → CRC."""
    W, H = 1000, 380
    f = []

    # стрічка байтів кадру — широкі клітинки, щоб підписи-кроки під ними не наклались
    x0 = 40
    cw = 82          # ширина клітинки
    gap = 8
    yb = 116
    hb = 56

    cells = [
        ("FE", "STX", "#fdecea"),
        ("09", "LEN", "#fff7e6"),
        ("SEQ", "лічильник", FILL),
        ("SYS", "апарат", FILL),
        ("COMP", "вузол", FILL),
        ("ID", "тип", "#eef4ff"),
    ]
    xs = []
    edges = []       # (лівий, правий) кожної клітинки
    x = x0
    for val, lab, fill in cells:
        f.append(rect(x, yb, cw, hb, fill=fill))
        f.append(text(x + cw / 2, yb + 26, val, size=15, bold=True))
        f.append(text(x + cw / 2, yb + 46, lab, size=11, color=MUTED))
        xs.append(x + cw / 2)
        edges.append((x, x + cw))
        x += cw + gap

    # блок даних (payload) — ширший
    pw = 210
    f.append(rect(x, yb, pw, hb, fill="#eafaf1"))
    f.append(text(x + pw / 2, yb + 26, "PAYLOAD", size=15, bold=True))
    f.append(text(x + pw / 2, yb + 46, "рівно LEN байтів (тут 9)", size=11, color=MUTED))
    px = x + pw / 2
    p_l = x
    x += pw + gap

    # CRC — два байти
    crw = 96
    f.append(rect(x, yb, crw, hb, fill="#fff7e6"))
    f.append(text(x + crw / 2, yb + 26, "CRC", size=15, bold=True))
    f.append(text(x + crw / 2, yb + 46, "2 байти", size=11, color=MUTED))
    crx = x + crw / 2

    # кроки розбірника — підписи ПІД стрічкою, кожен під СВОЄЮ ділянкою, з чистими проміжками.
    # Крок 1 і крок 2 рознесено на дві висоти рядка, щоб їхні широкі написи не торкались.
    sy = yb + hb + 40
    # 1 — під STX, окремим верхнім ярусом ліворуч
    f.append(text(xs[0], sy, "1. ловимо 0xFE (старт)", size=12, color=POS, anchor="middle"))
    # 2 — під LEN, НИЖНІМ ярусом, щоб не зіткнутись із широким написом кроку 1
    f.append(text(xs[1], sy + 26, "2. читаємо LEN", size=12, color=INK, anchor="middle"))
    f.append(text(xs[1], sy + 44, "(скільки даних)", size=11, color=MUTED, anchor="middle"))
    # 3 — під чотирма байтами заголовка (SEQ..ID), верхній ярус
    hx = (edges[2][0] + edges[5][1]) / 2
    f.append(text(hx, sy, "3. чотири байти заголовка", size=12, color=INK, anchor="middle"))
    f.append(text(hx, sy + 18, "SEQ · SYS · COMP · ID", size=11, color=MUTED, anchor="middle"))
    # 4 — під даними
    f.append(text(px, sy, "4. рівно LEN байтів даних", size=12, color=FIELD, anchor="middle"))
    f.append(text(px, sy + 18, "(за MSG ID знаємо, що всередині)", size=11, color=MUTED, anchor="middle"))
    # 5 — під CRC, стовпчиком праворуч, зі стрілкою від клітинки CRC
    f.append(arrow(crx, yb + hb + 6, crx, sy + 60))
    f.append(text(crx, sy + 78, "5. звірити CRC", size=12, color=INK, anchor="middle"))
    f.append(text(crx, sy + 96, "зійшлась —", size=11, color=MUTED, anchor="middle"))
    f.append(text(crx, sy + 112, "кадр цілий", size=11, color=MUTED, anchor="middle"))

    # підсумковий рядок: довжина кадру
    f.append(text(W / 2, 336, "Довжина кадру = 1 (STX) + 5 (заголовок) + LEN (дані) + 2 (CRC)",
                  size=13, bold=True))
    f.append(text(W / 2, 358, "версія 2 (0xFD): заголовок 9 байтів, MSG ID — 3 байти, решта — та сама ідея",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'mav-parse.svg'), W, H, *f,
           title="Розбір кадру MAVLink v1 з потоку: крок за кроком по байтах")


def timeline():
    """Хронологія народження SiK: XBee-біль → DIY Drones → SiK 2011 → 3DR 2012 → сумісні."""
    W, H = 900, 660
    f = []

    # вертикальна вісь часу зліва, роки-мітки на ній, події — широкими рамками праворуч
    axis_x = 150
    top = 70
    bot = 620
    f.append(line(axis_x, top, axis_x, bot, color=MUTED, sw=3))

    # рядки: (мітка, [текст події], колір-заливка рамки, колір-контур)
    rows = [
        ("до 2011", ["Дорого й закрито: пара XBee (Digi)", "коштує як половина дрона.",
                     "Спільнота DIY Drones (Кріс Андерсон,", "з 2007) шукає дешеву заміну."], "#fdecea", POS),
        ("залізо", ["Дешевий модуль HopeRF HM-TRP уже є:", "чип Si1000 (8051) + радіо Si4432.",
                    "Але заводська прошивка — слабка."], "#fff7e6", FIELD),
        ("2011", ["Прошивка SiK. Майкл Сміт і", "Ендрю Тріджелл (автор rsync/Samba)",
                  "пишуть вільний код на це залізо:", "ECC, MAVLink, AT-налаштування."], "#eafaf1", FIELD),
        ("2012", ["Продукт «3DR-радіо». 3D Robotics", "кладе SiK у коробку з USB й антеною;",
                  "версії 433 МГц (ЄС) і 915 МГц (США),", "удвічі дешевше за XBee."], "#eef4ff", NEG),
        ("після", ["3DR згорнула напрямок — а SiK ні.", "Відкритий код підхопили інші:",
                   "Holybro, mRo та безліч сумісних.", "Продукт помер — платформа лишилась."], "#eef4ff", NEG),
    ]

    n = len(rows)
    span = bot - top
    step = span / n
    for i, (mark, lines, fill, stroke) in enumerate(rows):
        cy = top + step * (i + 0.5)

        # вузол на осі
        f.append(circle(axis_x, cy, 7, fill=stroke, stroke=stroke, sw=2))

        # мітка ЛІВОРУЧ від осі (окрема рамка, з запасом)
        yb, yw, yh = textbox(axis_x - 80, cy, [mark], size=14, min_w=108,
                             fill="#ffffff", stroke=MUTED, bold=True)
        f.append(yb)

        # подія ПРАВОРУЧ у широкій рамці, з великим відступом від осі
        ev_l = axis_x + 45
        ev_w = W - ev_l - 30
        ev_h = 100
        f.append(fitbox(ev_l, cy - ev_h / 2, ev_w, ev_h, "\n".join(lines),
                        size=14, fill=fill, stroke=stroke, pad=12))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *f,
           title="Як відкритий SiK на дешевому залізі витіснив дорогий XBee")


block()
wiring()
command_mode()
mav_parse()
timeline()
print("ok")
