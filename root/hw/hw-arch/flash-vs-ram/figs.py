# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра-підсилення під цю тему: жовте = «обережно/незручно» (запис у Flash).
WARN  = "#9a7322"
WARNF = "#fff8e8"
WARNS = "#caa24a"
BLUEF = "#f3f5fd"
GREENF = "#eef7ee"


# ── volatile: летка RAM проти нелеткої Flash ─────────────────────────────────
# Ідея: одне питання — «чи пам'ятає без живлення?» — розводить дві технології.
def fig_volatile():
    W, H = 760, 360
    p = [text(W/2, 30, "Чи пам'ятає пам'ять дані без живлення?", size=17, bold=True),
         text(W/2, 50, "RAM забуває все при вимкненні; Flash зберігає", size=11.5, color=MUTED, italic=True)]

    # ліва панель — RAM (летка)
    p.append(rect(40, 76, 330, 224, fill=BLUEF, stroke=NEG, sw=2, rx=12))
    p.append(text(205, 100, "RAM — летка (volatile)", size=13, color=NEG, bold=True))
    p.append(fitbox(64, 118, 130, 58, "живлення є\nдані: 0x41", size=11, fill=BG, stroke=FIELD, bold=True, color=INK))
    p.append(arrow(200, 147, 232, 147, color=INK, sw=2))
    p.append(fitbox(240, 118, 106, 58, "вимкнули\nпусто", size=11, fill="#fdecea", stroke=POS, bold=True, color=POS))
    p.append(text(205, 206, "як напис на дошці: згасло світло — стерлось", size=10, color=MUTED, italic=True))
    p.append(text(205, 230, "тримає біт зворотним зв'язком, як тригер", size=10.5, color=INK, bold=True))
    p.append(text(205, 252, "без струму петля рветься — біт забутий", size=10, color=MUTED, italic=True))
    p.append(text(205, 278, "робоча пам'ять: змінні, стек, купа", size=10.5, color=NEG, bold=True))

    # права панель — Flash (нелетка)
    p.append(rect(390, 76, 330, 224, fill=GREENF, stroke=FIELD, sw=2, rx=12))
    p.append(text(555, 100, "Flash — нелетка (non-volatile)", size=13, color=FIELD, bold=True))
    p.append(fitbox(414, 118, 130, 58, "живлення є\nдані: код", size=11, fill=BG, stroke=FIELD, bold=True, color=INK))
    p.append(arrow(550, 147, 582, 147, color=INK, sw=2))
    p.append(fitbox(590, 118, 106, 58, "вимкнули\nкод цілий", size=11, fill=GREENF, stroke=FIELD, bold=True, color=FIELD))
    p.append(text(555, 206, "як чорнило на папері: лишається без живлення", size=10, color=MUTED, italic=True))
    p.append(text(555, 230, "пам'ятає фізично: заряд у плавучому затворі", size=10.5, color=INK, bold=True))
    p.append(text(555, 252, "заряд нікуди не дівається без струму", size=10, color=MUTED, italic=True))
    p.append(text(555, 278, "постійна пам'ять: програма, сталі", size=10.5, color=FIELD, bold=True))

    p.append(text(W/2, 326, "Тому прошита програма лишається у Flash після вимкнення,", size=11.5, color=INK, bold=True))
    p.append(text(W/2, 346, "а змінна в RAM обнуляється при кожному ввімкненні.", size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "volatile.svg"), W, H, *p)


# ── split: що куди — код і сталі у Flash, змінні в RAM ───────────────────────
# Ідея: властивість даних (мінливі/тимчасові vs ні) диктує, у якій пам'яті жити.
def fig_split():
    W, H = 760, 372
    p = [text(W/2, 30, "Що куди: незмінне — у Flash, мінливе — в RAM", size=17, bold=True),
         text(W/2, 50, "властивість даних диктує, у якій пам'яті їм жити", size=11.5, color=MUTED, italic=True)]

    p.append(rect(40, 76, 330, 200, fill=GREENF, stroke=FIELD, sw=2, rx=12))
    p.append(text(205, 100, "Flash (нелетка, повільний запис)", size=12, color=FIELD, bold=True))
    p.append(fitbox(64, 116, 282, 40, ".text — код (інструкції програми)", size=11, fill=BG, stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(64, 162, 282, 40, ".rodata — сталі (рядки, таблиці)", size=11, fill=BG, stroke=FIELD, color=INK, bold=True))
    p.append(text(205, 226, "сюди — бо:", size=10.5, color=INK, bold=True))
    p.append(text(205, 246, "не міняються під час роботи", size=10, color=INK))
    p.append(text(205, 264, "мусять пережити вимкнення", size=10, color=INK))

    p.append(rect(390, 76, 330, 200, fill=BLUEF, stroke=NEG, sw=2, rx=12))
    p.append(text(555, 100, "RAM (летка, швидка, побайтно)", size=12, color=NEG, bold=True))
    p.append(fitbox(414, 116, 282, 40, ".data / .bss — глобальні змінні", size=11, fill=BG, stroke=NEG, color=INK, bold=True))
    p.append(fitbox(414, 162, 282, 40, "стек і купа — локальні, динамічні", size=11, fill=BG, stroke=NEG, color=INK, bold=True))
    p.append(text(555, 226, "сюди — бо:", size=10.5, color=INK, bold=True))
    p.append(text(555, 246, "міняються постійно (треба швидкий запис)", size=10, color=INK))
    p.append(text(555, 264, "тимчасові — не шкода, що зникнуть", size=10, color=INK))

    p.append(text(W/2, 312, "Незмінне й цінне (код, сталі) — у нелетку Flash;", size=11.5, color=INK, bold=True))
    p.append(text(W/2, 332, "мінливе й тимчасове (змінні) — у швидку RAM.", size=11.5, color=INK, bold=True))
    p.append(text(W/2, 356, "На МК RAM мізерна (кілобайти), Flash більша — великі сталі таблиці тримають у Flash, щоб берегти RAM.", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "split.svg"), W, H, *p)


# ── quirks: чому Flash не для частих змін (блоки, стерти→писати, знос) ────────
# Ідея: читати з Flash легко, а писати — лише блоками, повільно й зі зносом.
def fig_quirks():
    W, H = 760, 388
    p = [text(W/2, 30, "Чому Flash не годиться для частих змін", size=17, bold=True),
         text(W/2, 50, "читати легко й швидко, а ПИСАТИ — лише блоками, повільно, обмежену кількість разів", size=11, color=MUTED, italic=True)]

    p.append(rect(40, 74, 330, 132, fill=BLUEF, stroke=NEG, sw=1.8, rx=12))
    p.append(text(205, 98, "RAM — пише легко", size=13, color=NEG, bold=True))
    for i, s in enumerate(["будь-який окремий байт — одразу",
                           "швидко (за такти)",
                           "скільки завгодно разів"]):
        p.append(text(60, 124 + i*24, "• " + s, size=10.5, color=INK, anchor="start"))

    p.append(rect(390, 74, 330, 132, fill=WARNF, stroke=WARNS, sw=1.8, rx=12))
    p.append(text(555, 98, "Flash — пише важко", size=13, color=WARN, bold=True))
    for i, s in enumerate(["лише цілими блоками (не байтом)",
                           "спершу стерти блок (усе → 1), тоді 0",
                           "повільно; знос ~10–100 тис. циклів"]):
        p.append(text(410, 124 + i*24, "• " + s, size=10, color=INK, anchor="start"))

    # стрічка «стерти → записати»
    p.append(text(230, 244, "запис у Flash:", size=11, color=WARN, bold=True, anchor="start"))
    p.append(text(300, 270, "стерти весь блок", size=10, color=POS, bold=True))
    p.append(fitbox(220, 280, 160, 26, "1 1 1 1 1 1 1 1", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, rx=4))
    p.append(arrow(388, 293, 448, 293, color=INK, sw=2))
    p.append(text(560, 270, "тоді записати потрібні 0", size=10, color=FIELD, bold=True))
    p.append(fitbox(480, 280, 160, 26, "1 0 1 1 0 0 1 0", size=11, fill=GREENF, stroke=FIELD, color=INK, bold=True, rx=4))

    p.append(rect(40, 322, 680, 50, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W/2, 343, "Код записують раз при прошивці — читають мільйони разів. А лічильник, що пише у Flash щосекунди,", size=10.5, color=INK, bold=True))
    p.append(text(W/2, 362, "зносить блок за лічені дні — тож часті зміни робить RAM. Так само зношуються SSD і флешки.", size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "quirks.svg"), W, H, *p)


# ── startup: копія .data з Flash у RAM при старті ────────────────────────────
# Ідея: ініціалізована глобальна мусить і пережити вимкнення, і бути мінливою —
# розв'язок: зразок у Flash, робоча копія в RAM щостарту; .bss просто обнуляють.
def fig_startup():
    W, H = 760, 388
    p = [text(W/2, 30, "Звідки глобальні беруть початкові значення", size=17, bold=True),
         text(W/2, 50, "значення мусить пережити вимкнення (отже, Flash), та змінна мінлива (отже, RAM) — розв'язок: копія при старті", size=10, color=MUTED, italic=True)]

    p.append(rect(40, 80, 300, 184, fill=GREENF, stroke=FIELD, sw=2, rx=12))
    p.append(text(190, 104, "Flash (нелетка)", size=12.5, color=FIELD, bold=True))
    p.append(fitbox(62, 118, 256, 32, ".text — код (виконується тут)", size=10.5, fill=BG, stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(62, 156, 256, 32, ".rodata — сталі (читаються тут)", size=10.5, fill=BG, stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(62, 194, 256, 32, "початкові значення .data", size=10.5, fill=WARNF, stroke=WARNS, color=WARN, bold=True))
    p.append(text(190, 246, "усе це пережило вимкнення", size=9.5, color=MUTED, italic=True))

    p.append(rect(420, 80, 300, 184, fill=BLUEF, stroke=NEG, sw=2, rx=12))
    p.append(text(570, 104, "RAM (летка)", size=12.5, color=NEG, bold=True))
    p.append(fitbox(442, 156, 256, 32, ".data (вже з копією значень)", size=10.5, fill=WARNF, stroke=WARNS, color=WARN, bold=True))
    p.append(fitbox(442, 194, 256, 32, ".bss → обнулено", size=10.5, fill=BLUEF, stroke=NEG, color=NEG, bold=True))

    # копія .data Flash→RAM
    p.append(arrow(322, 210, 438, 172, color=WARN, sw=2.4))
    p.append(text(380, 182, "копія при старті", size=10, color=WARN, bold=True))
    # обнулення .bss
    p.append(line(570, 244, 570, 228, color=NEG, sw=2, dash="3 3"))
    p.append(text(570, 258, "обнуляється на старті", size=9, color=NEG))

    p.append(rect(40, 286, 680, 86, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W/2, 310, "Перед main() крихітний стартовий код копіює початкові значення .data з Flash у RAM і обнуляє .bss.", size=11, color=INK, bold=True))
    p.append(text(W/2, 332, "Тому глобальна щоразу стартує зі свого початкового значення — воно зберігалось у Flash і скопіювалось у RAM.", size=11, color=INK, bold=True))
    p.append(text(W/2, 356, ".bss (нульові) місця в прошивці не займають: навіщо зберігати тисячу нулів — досить сказати «обнули цей шмат RAM».", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "startup.svg"), W, H, *p)


# ── zoo: родина пам'ятей таблицею (летка? · особливості · де) ─────────────────
# Ідея: видів багато, та все — варіації на дві фізичні теми; для МК головні дві.
def fig_zoo():
    W, H = 760, 372
    p = [text(W/2, 30, "Родина пам'ятей: хто летка, де яку вживають", size=17, bold=True),
         text(W/2, 50, "видів багато, та для мікроконтролера головні дві — Flash (програма) і SRAM (змінні)", size=11, color=MUTED, italic=True)]

    cols = [70, 230, 470, 700]
    p.append(text(cols[0], 80, "тип", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(cols[1], 80, "летка?", size=11, color=INK, bold=True))
    p.append(text(cols[2], 80, "особливості", size=11, color=INK, bold=True))
    p.append(text(cols[3], 80, "де вживають", size=11, color=INK, bold=True, anchor="end"))

    rows = [
        ("SRAM",   "летка",   NEG,   FIELD, "дуже швидка; комірка ≈ тригер",           "робоча RAM МК, кеші"),
        ("DRAM",   "летка",   NEG,   FIELD, "щільна; потребує освіження (заряд стікає)", "головна пам'ять ПК"),
        ("Flash",  "нелетка", FIELD, FIELD, "читання швидке; запис блоками, знос",      "програма МК, SSD, флешки"),
        ("EEPROM", "нелетка", FIELD, FIELD, "повільна, зате побайтна",                  "малі налаштування на МК"),
        ("ROM",    "нелетка", FIELD, WARNS, "тільки читання, вшите назавжди",           "заводський код, незмінні дані"),
    ]
    y = 96
    for name, vol, vc, sc, feat, use in rows:
        p.append(fitbox(60, y, 110, 40, name, size=12, fill="#fafafa", stroke=sc, color=sc, bold=True))
        volf = "#fdecea" if vol == "летка" else GREENF
        p.append(fitbox(180, y, 100, 40, vol, size=10.5, fill=volf, stroke=vc, color=vc, bold=True))
        p.append(rect(290, y, 280, 40, fill=BG, stroke=MUTED, sw=1, rx=6))
        p.append(text(300, y + 24, feat, size=10, color=INK, anchor="start"))
        p.append(rect(580, y, 140, 40, fill=BG, stroke=MUTED, sw=1, rx=6))
        p.append(text(650, y + 24, use, size=9, color=INK))
        y += 48

    p.append(text(W/2, 352, "Вся родина — варіації на дві фізичні теми: летку (біт тримає струм) і нелетку (стан застрягає фізично).", size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "zoo.svg"), W, H, *p)


# ── insert: блок-схема SoC + зовнішній чип Flash ─────────────────────────────
def fig_blockdiagram():
    W, H = 760, 400
    p = [text(W/2, 30, "Прошивка живе в окремому чипі поруч із SoC", size=17, bold=True),
         text(W/2, 50, "у ESP32 ядро та RAM на кристалі, а програму тримає сусідній флеш-чип через шину SPI", size=11, color=MUTED, italic=True)]

    p.append(rect(40, 90, 300, 220, fill=BLUEF, stroke=NEG, sw=2.2, rx=12))
    p.append(text(190, 114, "SoC (ESP32)", size=15, color=NEG, bold=True))
    p.append(text(190, 132, "усе на одному кристалі", size=10, color=MUTED, italic=True))
    p.append(fitbox(62, 144, 120, 50, "ядро CPU\nвиконує код", size=10.5, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(fitbox(198, 144, 120, 50, "SRAM\nзмінні (летка)", size=10.5, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(fitbox(62, 202, 120, 50, "кеш\nгарячий код", size=10.5, fill=GREENF, stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(198, 202, 120, 50, "контролер\nSPI-флеші", size=10.5, fill=WARNF, stroke=WARNS, color=WARN, bold=True))
    p.append(text(190, 280, "вбудованої Flash тут крихітна частка або нема —", size=9.5, color=MUTED, italic=True))
    p.append(text(190, 296, "на цілу програму місця бракує", size=9.5, color=MUTED, italic=True))

    # шина SPI
    for i, (yy, col) in enumerate([(218, INK), (232, INK), (246, POS), (260, NEG)]):
        p.append(line(340, yy, 480, yy, color=col, sw=2))
    p.append(arrow(404, 246, 426, 246, color=POS, sw=2))
    p.append(arrow(426, 260, 404, 260, color=NEG, sw=2))
    p.append(text(410, 206, "шина SPI · 4 дроти", size=11, color=INK, bold=True))

    p.append(rect(480, 110, 240, 180, fill="#fdf4f4", stroke=POS, sw=2.2, rx=12))
    p.append(text(600, 134, "зовнішній чип SPI-NOR-флеші", size=11.5, color=POS, bold=True))
    p.append(text(600, 152, "клас W25Q · корпус SOIC-8", size=10, color=MUTED, italic=True))
    p.append(fitbox(502, 166, 196, 52, "прошивка (код + сталі)\n.text · .rodata · ресурси", size=10, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(text(600, 240, "нелетка: лишається після вимкнення", size=9.5, color=MUTED, italic=True))
    p.append(text(600, 258, "об'єм — мегабайти, недорого", size=9.5, color=MUTED, italic=True))
    p.append(text(600, 278, "як читає й пише — NOR і XIP, нижче", size=9.5, color=FIELD, bold=True))

    p.append(rect(40, 330, 680, 56, fill=GREENF, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(W/2, 352, "Поділ той самий: змінні — у швидкій леткій SRAM на кристалі; код і сталі — у місткій нелеткій флеші.", size=11, color=INK, bold=True))
    p.append(text(W/2, 374, "Лише тепер флеш — не всередині мікросхеми процесора, а окремим чипом поруч, через шину SPI.", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "blockdiagram.svg"), W, H, *p)


# ── insert: розпіновка SOIC-8 ────────────────────────────────────────────────
def fig_pinout():
    W, H = 760, 412
    p = [text(W/2, 30, "Розпіновка SOIC-8 і чотири дроти до контролера", size=17, bold=True),
         text(W/2, 50, "вісім ніжок: чотири — шина SPI, ще чотири — живлення та дві службові лінії (тримати високими)", size=10.5, color=MUTED, italic=True)]

    # корпус
    p.append(rect(300, 96, 160, 220, fill="#fafafa", stroke=INK, sw=2.2, rx=10))
    p.append(circle(322, 120, 6, fill=BG, stroke=INK, sw=1.8))
    p.append(text(380, 134, "SPI-NOR", size=14, color=INK, bold=True))
    p.append(text(380, 154, "флеш", size=13, color=INK, bold=True))
    p.append(text(380, 176, "(W25Q-клас)", size=10.5, color=MUTED, italic=True))
    p.append(text(380, 300, "вид зверху", size=10, color=MUTED, italic=True))

    left = [("1", "CS#", "вибір чипа (низький = слухай)", INK),
            ("2", "DO (MISO)", "дані від чипа до контролера", NEG),
            ("3", "WP#", "захист запису — тримати високим", MUTED),
            ("4", "GND", "земля", INK)]
    right = [("8", "VCC", "живлення 3.3 В", POS),
             ("7", "HOLD#", "пауза — тримати високим", MUTED),
             ("6", "CLK", "такт від контролера", INK),
             ("5", "DI (MOSI)", "команда від контролера до чипа", POS)]
    ys = [148, 198, 248, 298]
    for (num, name, desc, col), y in zip(left, ys):
        p.append(line(270, y, 300, y, color=col, sw=2))
        p.append(rect(272, y - 9, 18, 18, fill=BG, stroke=col, sw=1.6, rx=3))
        p.append(text(281, y + 4, num, size=11, color=col, bold=True))
        p.append(text(262, y - 1, name, size=12, color=col, bold=True, anchor="end"))
        p.append(text(262, y + 14, desc, size=9, color=MUTED, anchor="end"))
    for (num, name, desc, col), y in zip(right, ys):
        p.append(line(460, y, 490, y, color=col, sw=2))
        p.append(rect(470, y - 9, 18, 18, fill=BG, stroke=col, sw=1.6, rx=3))
        p.append(text(479, y + 4, num, size=11, color=col, bold=True))
        p.append(text(498, y - 1, name, size=12, color=col, bold=True, anchor="start"))
        p.append(text(498, y + 14, desc, size=9, color=MUTED, anchor="start"))

    p.append(rect(40, 336, 680, 60, fill=BLUEF, stroke=NEG, sw=1.8, rx=10))
    p.append(text(W/2, 360, "Чотири лінії SPI — серце підключення: CS# (обрати), CLK (такт),", size=11.5, color=INK, bold=True))
    p.append(text(W/2, 382, "DI/MOSI (команда → чип), DO/MISO (дані → контролер). Решта — VCC, GND і WP#/HOLD# (високі).", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "pinout.svg"), W, H, *p)


# ── insert: XIP через кеш ─────────────────────────────────────────────────────
def fig_xip():
    W, H = 760, 388
    p = [text(W/2, 30, "XIP: код «живе» у флеші, виконується наче з RAM", size=17, bold=True),
         text(W/2, 50, "контролер сам підкачує шматки коду з повільної флеші у швидкий кеш; ядро бачить суцільні адреси", size=10.5, color=MUTED, italic=True)]

    p.append(fitbox(80, 130, 150, 90, "ядро CPU\nпросить байт коду\nза його адресою", size=10.5, fill=BLUEF, stroke=NEG, color=NEG, bold=True))
    p.append(fitbox(305, 130, 150, 90, "кеш\nшвидкий, малий\nкопія гарячого коду", size=10.5, fill=GREENF, stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(540, 130, 180, 90, "SPI-NOR-флеш\nуся прошивка\nповільна, але містка", size=10.5, fill="#fdf4f4", stroke=POS, color=POS, bold=True))

    p.append(arrow(230, 158, 305, 158, color=INK, sw=2))
    p.append(text(267, 150, "адреса", size=10, color=INK, bold=True))
    p.append(arrow(305, 192, 230, 192, color=FIELD, sw=2))
    p.append(text(267, 210, "є в кеші → миттєво", size=9.5, color=FIELD, bold=True))

    p.append(line(455, 158, 540, 158, color=WARNS, sw=2, dash="5 4"))
    p.append(arrow(530, 158, 540, 158, color=WARNS, sw=2))
    p.append(text(497, 150, "промах →", size=9.5, color=WARN, bold=True))
    p.append(line(540, 192, 465, 192, color=POS, sw=2, dash="5 4"))
    p.append(arrow(475, 192, 465, 192, color=POS, sw=2))
    p.append(text(500, 210, "блок коду по SPI", size=9.5, color=POS))

    p.append(rect(40, 240, 680, 60, fill=BLUEF, stroke=NEG, sw=1.6, rx=10))
    p.append(text(W/2, 264, "Execute-In-Place: процесор виконує код прямо «на місці» — не копіюючи всю програму в RAM наперед.", size=11, color=INK, bold=True))
    p.append(text(W/2, 286, "Потрібен байт — кеш або вже має його (миттєво), або підкачує блок із флеші по SPI (рідше, повільніше).", size=10, color=MUTED, italic=True))

    p.append(rect(40, 312, 680, 60, fill=GREENF, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(W/2, 336, "Це лягає на природу флеші: код читають мільйони разів і майже не пишуть —", size=11, color=INK, bold=True))
    p.append(text(W/2, 358, "тож читати його прямо з нелеткої флеші саме те, для чого вона добра.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "xip.svg"), W, H, *p)


if __name__ == "__main__":
    fig_volatile()
    fig_split()
    fig_quirks()
    fig_startup()
    fig_zoo()
    fig_blockdiagram()
    fig_pinout()
    fig_xip()
    print("figs.py: 8 SVG записано в", OUT)
