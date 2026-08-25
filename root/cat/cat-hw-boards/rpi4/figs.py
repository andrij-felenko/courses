# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: карта плати — де що фізично сидить ─────────────────────────────
def board_map():
    W, H = 780, 510
    frags = []
    # контур плати
    bx, by, bw, bh = 150, 70, 480, 320
    frags.append(rect(bx, by, bw, bh, fill="#eef6ee", stroke=FIELD, sw=2, rx=10))
    frags.append(text(bx + bw / 2, by - 14, "Плата зверху (85 × 56 мм)", size=13, color=MUTED))

    # SoC у центрі
    b, w_, h_ = textbox(bx + 205, by + 150, "BCM2711\nquad Cortex-A72", size=13,
                        fill="#fdecea", stroke=POS, sw=2, bold=True)
    frags.append(b)

    # чіп памʼяті поряд
    b, _, _ = textbox(bx + 205, by + 250, "LPDDR4\n1/2/4/8 ГБ", size=11,
                     fill=FILL, stroke=LINE)
    frags.append(b)

    # 40-pin гребінка вздовж верхнього краю
    frags.append(rect(bx + 40, by + 8, 300, 18, fill="#111", stroke="#111", sw=1, rx=3))
    frags.append(text(bx + 190, by + 44, "40-pin GPIO", size=11, color=INK, bold=True))

    # праворуч: живлення + 2 micro-HDMI + аудіо (кромка виводів дисплея/HDMI)
    def edge_right(cy, label, col=LINE):
        frags.append(rect(bx + bw - 14, cy - 9, 22, 18, fill=FILL, stroke=col, sw=1.5, rx=3))
        frags.append(text(bx + bw + 16, cy + 4, label, size=10, color=INK, anchor="start"))
    edge_right(by + 40, "USB-C 5 В/3 А", POS)
    edge_right(by + 90, "micro-HDMI 0")
    edge_right(by + 130, "micro-HDMI 1")
    edge_right(by + 175, "аудіо / відео")

    # низ: два блоки USB та Ethernet виступають за край плати
    def edge_bottom(cx, lines, col=LINE, fill=FILL):
        frags.append(rect(cx - 34, by + bh - 6, 68, 34, fill=fill, stroke=col, sw=1.5, rx=4))
        frags.append(mtext(cx, by + bh + 46, lines, size=10, color=INK))
    edge_bottom(bx + 90, ["USB 3.0", "×2 (сині)"], "#2457d6")
    edge_bottom(bx + 210, ["USB 2.0", "×2"])
    edge_bottom(bx + 340, ["Gigabit", "Ethernet"], FIELD)

    # microSD знизу з тильного боку (позначка) — під лівим краєм, у чистому місці
    frags.append(rect(bx - 6, by + bh + 66, 56, 14, fill="#111", stroke="#111", sw=1, rx=2))
    frags.append(text(bx + 22, by + bh + 96, "microSD (тил)", size=10, color=MUTED))

    render(os.path.join(OUT, 'board-map.svg'), W, H, *frags,
           title="Raspberry Pi 4 Model B: що де сидить")


# ── Фігура 2: 40-pin гребінка — живлення й головні шини ──────────────────────
def gpio_header():
    W, H = 620, 760
    frags = []
    frags.append(text(W / 2, 46, "Живлення й ключові виводи 40-pin гребінки",
                     size=13, color=MUTED))

    # два стовпчики по 20 пінів
    cols_x = [200, 420]
    top = 78
    dy = 32
    box_w = 150
    box_h = 24

    # (label_left, color_left, label_right, color_right) для пар 1-2, 3-4, ...
    rows = [
        ("3V3 живл.", FIELD,        "5V живл.", POS),
        ("GPIO2 SDA", LINE,         "5V живл.", POS),
        ("GPIO3 SCL", LINE,         "GND", NEG),
        ("GPIO4", MUTED,            "GPIO14 TXD", LINE),
        ("GND", NEG,                "GPIO15 RXD", LINE),
        ("GPIO17", MUTED,           "GPIO18", MUTED),
        ("GPIO27", MUTED,           "GND", NEG),
        ("GPIO22", MUTED,           "GPIO23", MUTED),
        ("3V3 живл.", FIELD,        "GPIO24", MUTED),
        ("GPIO10 MOSI", LINE,       "GND", NEG),
        ("GPIO9 MISO", LINE,        "GPIO25", MUTED),
        ("GPIO11 SCLK", LINE,       "GPIO8 CE0", LINE),
        ("GND", NEG,                "GPIO7 CE1", LINE),
        ("GPIO0", MUTED,            "GPIO1", MUTED),
        ("GPIO5", MUTED,            "GND", NEG),
        ("GPIO6", MUTED,            "GPIO12", MUTED),
        ("GPIO13", MUTED,           "GND", NEG),
        ("GPIO19", MUTED,           "GPIO16", MUTED),
        ("GPIO26", MUTED,           "GPIO20", MUTED),
        ("GND", NEG,                "GPIO21", MUTED),
    ]

    def pin_box(cx, cy, label, col):
        fill = FILL
        if col == POS:
            fill = "#fdecea"
        elif col == NEG:
            fill = "#eaf0fd"
        elif col == FIELD:
            fill = "#eef6ee"
        frags.append(fitbox(cx - box_w / 2, cy - box_h / 2, box_w, box_h, label,
                            size=11, fill=fill, stroke=col, sw=1.4))

    for i, (ll, lc, rl, rc) in enumerate(rows):
        cy = top + i * dy
        n_left = 2 * i + 1
        n_right = 2 * i + 2
        # номери пінів у центрі
        frags.append(text(W / 2 - 14, cy + 4, str(n_left), size=10, color=MUTED, anchor="end"))
        frags.append(text(W / 2 + 14, cy + 4, str(n_right), size=10, color=MUTED, anchor="start"))
        # маленькі кружечки-піни
        frags.append(circle(W / 2 - 6, cy, 3, fill="#111", stroke="#111", sw=1))
        frags.append(circle(W / 2 + 6, cy, 3, fill="#111", stroke="#111", sw=1))
        pin_box(cols_x[0], cy, ll, lc)
        pin_box(cols_x[1], cy, rl, rc)

    # легенда
    ly = top + len(rows) * dy + 8
    frags.append(fitbox(90, ly, 120, 22, "5 В живлення", size=10, fill="#fdecea", stroke=POS, sw=1.4))
    frags.append(fitbox(230, ly, 120, 22, "3.3 В живлення", size=10, fill="#eef6ee", stroke=FIELD, sw=1.4))
    frags.append(fitbox(370, ly, 90, 22, "земля", size=10, fill="#eaf0fd", stroke=NEG, sw=1.4))
    frags.append(fitbox(478, ly, 60, 22, "сигнал", size=10, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, 'gpio-header.svg'), W, H, *frags,
           title="Гребінка GPIO — рівні лише 3.3 В")


# ── Фігура 3 (вставка proj-gpio): три способи дотягтися до виводу ────────────
def gpio_three_ways():
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 50, "Три способи керувати GPIO з коду під Linux",
                     size=13, color=MUTED))

    col_w = 250
    xs = [40, 325, 610]          # ліва межа кожної колонки
    cx = [x + col_w / 2 for x in xs]
    ax = [c - 78 for c in cx]    # ВІСЬ стрілок — зсунута ліворуч від центру, щоб
    #                              підписи лягали праворуч від лінії, не на неї
    top = 80

    # спільний низ — «вивід гребінки»
    pin_y = 402
    for a in ax:
        frags.append(circle(a, pin_y, 7, fill="#111", stroke="#111", sw=1))
    frags.append(text(W / 2, pin_y + 34, "вивід гребінки (кремній)", size=12,
                     color=INK, bold=True))

    # заголовки колонок
    heads = [
        ("sysfs", "/sys/class/gpio", POS, "застарілий"),
        ("mmap у регістри", "bcm2835", POS, "непереносний"),
        ("libgpiod", "/dev/gpiochipN", FIELD, "живий"),
    ]
    for i, (name, sub, col, tag) in enumerate(heads):
        frags.append(fitbox(xs[i], top, col_w, 40, name, size=15, bold=True,
                            fill=FILL, stroke=col, sw=2))
        frags.append(text(cx[i], top + 60, sub, size=11, color=MUTED))
        # ярлик статусу
        tcol = FIELD if tag == "живий" else POS
        tfill = "#eef6ee" if tag == "живий" else "#fdecea"
        frags.append(fitbox(cx[i] - 55, top + 74, 110, 22, tag, size=11,
                            fill=tfill, stroke=tcol, sw=1.4, color=tcol, bold=True))

    # шар «ядро Linux» — смуга під крайніми колонками (sysfs і libgpiod ідуть крізь);
    # mmap (середня) її ОБХОДИТЬ, тож під нею смуги нема
    ker_y = 250
    ker_h = 34
    frags.append(rect(xs[0] - 4, ker_y, col_w + 8, ker_h, fill="#eef2ff",
                      stroke=NEG, sw=1.5, rx=6))
    frags.append(text(ax[0], ker_y + 22, "ядро Linux", size=12, color=NEG))
    frags.append(rect(xs[2] - 4, ker_y, col_w + 8, ker_h, fill="#eef2ff",
                      stroke=NEG, sw=1.5, rx=6))
    frags.append(text(ax[2], ker_y + 22, "ядро Linux", size=12, color=NEG))

    code_y = top + 108
    lx = 12   # зсув підпису праворуч від осі стрілки

    # sysfs: код → ядро → вивід (через глобальні текст-файли)
    frags.append(arrow(ax[0], code_y, ax[0], ker_y - 4, color=LINE))
    frags.append(text(ax[0] + lx, (code_y + ker_y) / 2 + 4, "текст-файли",
                     size=10, color=MUTED, anchor="start"))
    frags.append(arrow(ax[0], ker_y + ker_h, ax[0], pin_y - 12, color=LINE))
    frags.append(text(ax[0] + lx, pin_y - 40, "вивід нічий,", size=10, color=POS, anchor="start"))
    frags.append(text(ax[0] + lx, pin_y - 26, "«висить»", size=10, color=POS, anchor="start"))

    # mmap: код → ПРЯМО вниз повз ядро
    frags.append(arrow(ax[1], code_y, ax[1], pin_y - 12, color=POS, sw=2))
    frags.append(text(ax[1] + lx, (code_y + pin_y) / 2 - 8, "повз ядро,", size=10, color=POS, anchor="start"))
    frags.append(text(ax[1] + lx, (code_y + pin_y) / 2 + 6, "в регістри", size=10, color=POS, anchor="start"))
    frags.append(text(ax[1] + lx, pin_y - 30, "ядро не знає", size=10, color=POS, anchor="start"))

    # libgpiod: код → ядро → вивід (з власником)
    frags.append(arrow(ax[2], code_y, ax[2], ker_y - 4, color=FIELD, sw=2))
    frags.append(text(ax[2] + lx, (code_y + ker_y) / 2 + 4, "ioctl-запит",
                     size=10, color=FIELD, anchor="start"))
    frags.append(arrow(ax[2], ker_y + ker_h, ax[2], pin_y - 12, color=FIELD, sw=2))
    frags.append(text(ax[2] + lx, pin_y - 40, "власник-процес,", size=10, color=FIELD, anchor="start"))
    frags.append(text(ax[2] + lx, pin_y - 26, "ядро прибере", size=10, color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'gpio-three-ways.svg'), W, H, *frags,
           title="Від коду до виводу: sysfs · mmap · libgpiod")


# ── Фігура 4 (вставка proj-gpio): кнопка — плаваючий вхід vs підтяжка ────────
def pullup_button():
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 50, "Чому цифровому входу-кнопці потрібна підтяжка",
                     size=13, color=MUTED))

    # дві панелі
    def panel(x0, title, col):
        frags.append(rect(x0, 76, 360, 350, fill=BG, stroke=col, sw=1.5, rx=8))
        frags.append(fitbox(x0 + 80, 90, 200, 26, title, size=13, bold=True,
                            fill="#fff", stroke="none", sw=0, color=col))

    panel(40, "без підтяжки: вхід плаває", POS)
    panel(420, "підтяжка до плюса: стабільно", FIELD)

    # ── ліва панель: плаваючий вхід ──
    lx = 220               # вісь входу лівої панелі
    inp_y = 250
    # символ входу МК
    frags.append(fitbox(lx - 55, inp_y - 22, 110, 44, "вхід\nКМОН", size=11,
                        fill=FILL, stroke=LINE, sw=1.4))
    # кнопка вниз до землі (розімкнена)
    frags.append(line(lx, inp_y + 22, lx, inp_y + 70, color=LINE))
    frags.append(text(lx + 60, inp_y + 55, "кнопка", size=10, color=MUTED))
    frags.append(text(lx + 60, inp_y + 69, "розімкнена", size=10, color=MUTED))
    # розрив контакту
    frags.append(line(lx - 12, inp_y + 74, lx + 12, inp_y + 74, color=LINE, sw=2))
    frags.append(line(lx - 12, inp_y + 84, lx + 6, inp_y + 78, color=LINE, sw=2))
    frags.append(line(lx, inp_y + 90, lx, inp_y + 108, color=LINE))
    # земля
    for k, wd in enumerate((22, 14, 6)):
        frags.append(line(lx - wd, inp_y + 108 + k * 6, lx + wd, inp_y + 108 + k * 6,
                          color=NEG, sw=2))
    # «антена» наводок згори
    frags.append(arrow(lx - 60, inp_y - 60, lx - 8, inp_y - 24, color=POS))
    frags.append(text(lx - 70, inp_y - 66, "наводки", size=10, color=POS, anchor="middle"))
    frags.append(fitbox(lx - 45, 386, 150, 26, "читається 0 або 1\nвипадково", size=10,
                        fill="#fdecea", stroke=POS, sw=1.4, color=POS))

    # ── права панель: з підтяжкою ──
    rx = 600
    inp_y2 = 250
    # 3.3 В зверху
    frags.append(text(rx, 130, "3.3 В", size=12, color=FIELD, bold=True))
    frags.append(line(rx, 138, rx, 168, color=FIELD, sw=2))
    # резистор-підтяжка (зигзаг спрощено — прямокутник)
    frags.append(rect(rx - 12, 168, 24, 44, fill="#eef6ee", stroke=FIELD, sw=1.6, rx=3))
    frags.append(text(rx + 66, 194, "підтяжка", size=10, color=FIELD))
    frags.append(text(rx + 66, 208, "(слабка)", size=10, color=FIELD))
    frags.append(line(rx, 212, rx, inp_y2 - 22, color=FIELD, sw=2))
    # вузол входу
    frags.append(circle(rx, inp_y2 - 22, 4, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(fitbox(rx - 55, inp_y2 - 12, 110, 44, "вхід\nКМОН", size=11,
                        fill=FILL, stroke=LINE, sw=1.4))
    # кнопка вниз до землі
    frags.append(line(rx, inp_y2 + 32, rx, inp_y2 + 70, color=LINE))
    frags.append(text(rx + 62, inp_y2 + 55, "кнопка", size=10, color=MUTED))
    # контакт (замкнений показуємо як з'єднаний)
    frags.append(line(rx - 12, inp_y2 + 74, rx + 12, inp_y2 + 74, color=LINE, sw=2))
    frags.append(line(rx, inp_y2 + 74, rx, inp_y2 + 96, color=LINE))
    for k, wd in enumerate((22, 14, 6)):
        frags.append(line(rx - wd, inp_y2 + 96 + k * 6, rx + wd, inp_y2 + 96 + k * 6,
                          color=NEG, sw=2))
    frags.append(fitbox(rx - 70, 386, 200, 26,
                        "відпущено = 1 · натиснуто = 0", size=10,
                        fill="#eef6ee", stroke=FIELD, sw=1.4, color=FIELD))

    render(os.path.join(OUT, 'pullup-button.svg'), W, H, *frags,
           title="Плаваючий вхід проти підтяжки до плюса")


if __name__ == '__main__':
    board_map()
    gpio_header()
    gpio_three_ways()
    pullup_button()
    print("figures written")
