# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Куди подіти зайві байти: розкладка носія й коротший пристрій ────────
def fig_device_layout():
    W, H = 1460, 760
    p = []

    p.append(text(70, 60, "справжній розділ — те, що лежить на носії",
                  size=15, bold=True, anchor="start"))

    y_phys = 165
    segs = [(["суперблок", "4 КіБ"], GREY_FILL, 160),
            (["журнал"], WARM_FILL, 200),
            (["теги"], BLUE_FILL, 120),
            (["дані — 16 МіБ"], GREEN_FILL, 300),
            (["теги"], BLUE_FILL, 120),
            (["дані — 16 МіБ"], GREEN_FILL, 300),
            (["…"], GREY_FILL, 90)]

    x = 70
    data_centers = []
    for lines, fill, wseg in segs:
        p.append(fitbox(x, y_phys, wseg, 86, lines, size=13, pad=10,
                        fill=fill, stroke=LINE, sw=1.5))
        if fill is GREEN_FILL:
            data_centers.append(x + wseg / 2)
        x += wseg + 12

    x_end = x - 12

    p.append(text(70, 300, "що ціль показує нагору",
                  size=15, bold=True, anchor="start"))

    y_log = 390
    p.append(fitbox(70, y_log, x_end - 70, 86,
                    ["суцільний масив секторів — лише дані, підряд, без розривів"],
                    size=14, pad=12, fill=GREEN_FILL, stroke=NEG, sw=2))

    for cx in data_centers:
        p.append(line(cx, y_phys + 43 + 6, cx, y_log - 43 - 6,
                      color=MUTED, sw=1.2, dash="6 5"))

    n1, _, _ = textbox(390, 590,
                       ["теги не зібрані однією таблицею на початку:",
                        "тег і його сектор розділяє кілька мегабайтів,",
                        "тож читання не бігає через увесь носій"],
                       size=13, pad=16, fill=GREY_FILL, stroke=MUTED, sw=1.3)
    p.append(n1)

    n2, _, _ = textbox(1080, 590,
                       ["крок чергування типово 32768 секторів (16 МіБ);",
                        "задається при форматуванні й далі незмінний,",
                        "як і розмір блока та алгоритм"],
                       size=13, pad=16, fill=GREY_FILL, stroke=MUTED, sw=1.3)
    p.append(n2)

    p.append(text(x_end, 460, "пристрій нагорі коротший приблизно на 0.8 %",
                  size=13, color=POS, anchor="end"))

    render(os.path.join(IMG, 'device-layout.svg'), W, H, *p,
           title="Розкладка носія під dm-integrity і коротший пристрій нагорі")


# ── 2. Дані і тег мусять змінитися разом: три відповіді на цю задачу ───────
def fig_write_modes():
    W, H = 1700, 940
    p = []

    p.append(text(70, 58, "запис одного сектора змінює два місця на носії — і кожен режим по-своєму зводить їх докупи",
                  size=15, bold=True, anchor="start"))

    label_x = 165
    step_x0 = 400
    verdict_x = 1470

    def row(cy, label, label_fill, steps, verdict, verdict_fill, verdict_stroke, note):
        lfrag, lw, lh = textbox(label_x, cy, label, size=14, pad=14,
                                fill=label_fill, stroke=LINE, sw=1.6, min_w=200)
        p.append(lfrag)

        x = step_x0
        prev_right = None
        for lines, fill in steps:
            frag, w, h = textbox(x + 130, cy, lines, size=13, pad=13,
                                 fill=fill, stroke=LINE, sw=1.4, min_w=260)
            p.append(frag)
            if prev_right is not None:
                p.append(arrow(prev_right + 8, cy, x + 130 - w / 2 - 8, cy))
            prev_right = x + 130 + w / 2
            x += 300

        vfrag, vw, vh = textbox(verdict_x, cy, verdict, size=13, pad=14,
                                fill=verdict_fill, stroke=verdict_stroke, sw=1.8,
                                min_w=330)
        p.append(vfrag)
        p.append(text(step_x0 - 20, cy + 118, note, size=12.5, color=POS,
                      anchor="start"))

    p.append(text(verdict_x, 118, "що лишається після обриву живлення",
                  size=13, bold=True))

    row(215,
        ["прямий запис", "(режим D)"], GREY_FILL,
        [(["дані — на своє місце"], GREEN_FILL),
         (["тег — на своє місце"], BLUE_FILL)],
        ["сектор цілий, тег описує",
         "інший вміст — і не збіжиться",
         "вже назавжди"],
        RED_FILL, POS,
        "аварія між двома записами лишає добрий сектор із чужим тегом")

    row(505,
        ["журнал", "(режим J)"], GREEN_FILL,
        [(["дані й тег — у журнал"], WARM_FILL),
         (["коміт секції"], WARM_FILL),
         (["копіювання на місця"], GREEN_FILL)],
        ["до коміту — старе й узгоджене,",
         "після коміту журнал програють",
         "наново; кожен байт іде двічі"],
        GREEN_FILL, NEG,
        "неподільність купують подвійним записом: спершу в журнал, потім на місце")

    row(790,
        ["бітова мапа", "(режим B)"], WARM_FILL,
        [(["позначити ділянку в мапі"], WARM_FILL),
         (["дані й тег — прямо на місця"], GREEN_FILL)],
        ["позначені ділянки перерахують:",
         "який вміст там є, такий і",
         "засвідчать новим тегом"],
        WARM_FILL, POS,
        "запис один раз, зате псування саме в мить аварії буде освячене, а не викрите")

    render(os.path.join(IMG, 'write-modes.svg'), W, H, *p,
           title="Прямий запис, журнал і бітова мапа після обриву живлення")


# ── 3. Що змінює шар цілісності під дзеркалом ─────────────────────────────
def fig_under_mirror():
    W, H = 1460, 880
    p = []

    p.append(line(730, 90, 730, 800, color=MUTED, sw=1.2, dash="7 6"))

    lx, rx = 380, 1090

    p.append(text(lx, 100, "дзеркало саме по собі", size=15, bold=True))
    p.append(text(rx, 100, "шар цілісності під кожною ногою", size=15, bold=True))

    # ── ліворуч ──
    lfrag, _, lh = textbox(lx, 190, ["md raid1: читаю сектор 9000"],
                           size=13, pad=13, fill=GREY_FILL, stroke=LINE, sw=1.5,
                           min_w=430)
    p.append(lfrag)

    a1, _, ha1 = textbox(lx - 165, 340, ["диск A", "правильні байти"],
                         size=13, pad=12, fill=GREEN_FILL, stroke=LINE, sw=1.4,
                         min_w=230)
    p.append(a1)
    b1, _, hb1 = textbox(lx + 165, 340, ["диск B", "тихо зіпсований"],
                         size=13, pad=12, fill=RED_FILL, stroke=POS, sw=1.6,
                         min_w=230)
    p.append(b1)
    p.append(arrow(lx - 60, 190 + lh / 2, lx - 165, 340 - ha1 / 2))
    p.append(arrow(lx + 60, 190 + lh / 2, lx + 165, 340 - hb1 / 2))

    r1, _, _ = textbox(lx, 520, ["обидві ноги кажуть «прочитано успішно»,",
                                 "а байти різні"],
                       size=13, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.4,
                       min_w=430)
    p.append(r1)

    r2, _, _ = textbox(lx, 680, ["вибрати правильну нема за чим:",
                                 "перевірка масиву лише порахує",
                                 "розбіжності, не вкаже винного"],
                       size=13, pad=14, fill=RED_FILL, stroke=POS, sw=1.8,
                       min_w=430)
    p.append(r2)

    # ── праворуч ──
    rfrag, _, rh = textbox(rx, 190, ["md raid1: читаю сектор 9000"],
                           size=13, pad=13, fill=GREY_FILL, stroke=LINE, sw=1.5,
                           min_w=430)
    p.append(rfrag)

    a2, _, ha2 = textbox(rx - 165, 340, ["integrity над A", "тег збігся"],
                         size=13, pad=12, fill=GREEN_FILL, stroke=LINE, sw=1.4,
                         min_w=230)
    p.append(a2)
    b2, _, hb2 = textbox(rx + 165, 340, ["integrity над B", "тег не збігся"],
                         size=13, pad=12, fill=RED_FILL, stroke=POS, sw=1.6,
                         min_w=230)
    p.append(b2)
    p.append(arrow(rx - 60, 190 + rh / 2, rx - 165, 340 - ha2 / 2))
    p.append(arrow(rx + 60, 190 + rh / 2, rx + 165, 340 - hb2 / 2))

    r3, _, _ = textbox(rx, 520, ["нога B віддає не байти, а помилку EILSEQ —",
                                 "тихе псування стало явною відмовою"],
                       size=13, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.4,
                       min_w=430)
    p.append(r3)

    r4, _, _ = textbox(rx, 680, ["з відмовою на читанні RAID працює здавна:",
                                 "віддає копію з A нагору",
                                 "й перезаписує нею зіпсоване місце на B"],
                       size=13, pad=14, fill=GREEN_FILL, stroke=NEG, sw=1.8,
                       min_w=430)
    p.append(r4)

    p.append(text(730, 830, "порядок складання важить: шар цілісності стоїть під масивом, а не над ним",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'under-mirror.svg'), W, H, *p,
           title="Дзеркало без шару цілісності та з ним")


# ── 4. Стос кешів у досліді: де ховаються байти й чим кожен шар спорожнити ──
def fig_cache_stack():
    W, H = 1620, 1010
    p = []

    p.append(text(80, 60, "між командою «прочитати файл» і байтом у файлі-образі стоїть чотири схованки",
                  size=15, bold=True, anchor="start"))

    lx, rx = 470, 1240
    p.append(text(lx, 128, "шар, який може віддати старі байти", size=14, bold=True))
    p.append(text(rx, 128, "чим його спорожнити", size=14, bold=True))

    rows = [
        (200, ["сторінковий кеш файла", "/mnt/int/probe.txt"], BLUE_FILL,
         ["umount — або sync,", "а тоді drop_caches"]),
        (355, ["кеш блокового пристрою", "/dev/mapper/int0"], BLUE_FILL,
         ["blockdev --flushbufs", "на самому /dev/mapper/int0"]),
        (510, ["журнал dm-integrity:", "дані й теги ще не на місцях"], WARM_FILL,
         ["integritysetup close —", "журнал догравається до кінця"]),
        (665, ["сторінковий кеш файла-образу", "int0.img"], GREEN_FILL,
         ["нічого не треба: loop читає", "саме звідси, куди пише наш dd"]),
        (830, ["файл int0.img", "на справжньому диску"], GREY_FILL,
         ["", ""]),
    ]

    prev_bottom = None
    for cy, lines, fill, cure in rows:
        frag, w, h = textbox(lx, cy, lines, size=13.5, pad=15,
                             fill=fill, stroke=LINE, sw=1.6, min_w=560)
        p.append(frag)
        if prev_bottom is not None:
            p.append(arrow(lx, prev_bottom + 6, lx, cy - h / 2 - 6, color=MUTED))
        prev_bottom = cy + h / 2

        if cure[0]:
            cfrag, cw, ch = textbox(rx, cy, cure, size=13, pad=14,
                                    fill=GREY_FILL, stroke=MUTED, sw=1.3,
                                    min_w=520)
            p.append(cfrag)

    p.append(text(lx, 118, "cat /mnt/int/probe.txt", size=13.5, color=MUTED))

    warn, ww, wh = textbox(rx, 830,
                           ["losetup --direct-io=on прибирає четвертий шар —",
                            "і тоді буферизований dd у файл стає для loop невидимим:",
                            "або обидва через кеш, або обидва повз нього"],
                           size=13, pad=15, fill=RED_FILL, stroke=POS, sw=1.7,
                           min_w=520)
    p.append(warn)

    p.append(text(80, 950,
                  "drop_caches викидає лише чисті сторінки — брудні спершу треба записати, тому sync завжди йде першим",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(IMG, 'cache-stack.svg'), W, H, *p,
           title="Кеші між читанням файла і байтом у файлі-образі")


if __name__ == '__main__':
    fig_device_layout()
    fig_write_modes()
    fig_under_mirror()
    fig_cache_stack()
    print("ok")
