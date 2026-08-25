# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Дві площини: дані течуть крізь буфер, керування йде повз нього ────────
def fig_two_planes():
    W, H = 920, 400
    p = []

    # процес
    p.append(fitbox(40, 132, 150, 108, ["процес"], size=15, bold=True,
                    fill=FILL, stroke=LINE, sw=1.8, rx=10))

    # драйвер
    p.append(rect(430, 62, 280, 282, fill="#ffffff", stroke=LINE, sw=1.8, rx=12))
    p.append(text(570, 92, "драйвер", size=15, bold=True))
    p.append(fitbox(455, 132, 230, 55, ["буфер потоку"], size=13.5,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6, rx=8))
    p.append(fitbox(455, 245, 230, 66, ["налаштування", "швидкість · режим · формат"],
                    size=13, fill=RED_FILL, stroke=POS, sw=1.6, rx=8))

    # залізо
    p.append(fitbox(780, 132, 110, 55, ["залізо"], size=14, bold=True,
                    fill=FILL, stroke=LINE, sw=1.8, rx=8))

    # площина даних
    p.append(text(322, 118, "площина даних", size=13.5, bold=True, color=NEG))
    p.append(text(322, 139, "read · write — самі байти", size=12, color=MUTED))
    p.append(arrow(196, 160, 450, 160, color=NEG, sw=2))
    p.append(arrow(712, 160, 776, 160, color=NEG, sw=2))

    # площина керування
    p.append(arrow(196, 272, 450, 272, color=POS, sw=2))
    p.append(text(322, 302, "площина керування", size=13.5, bold=True, color=POS))
    p.append(text(322, 323, "ioctl — число повз потік", size=12, color=MUTED))

    # налаштування керують потоком
    p.append(line(570, 243, 570, 191, color=POS, sw=1.4, dash="5 4"))
    p.append(text(584, 219, "керує потоком", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'two-planes.svg'), W, H, *p)


# ── 2. Будова номера команди ────────────────────────────────────────────────
def fig_ioc_encoding():
    W, H = 980, 440
    p = []

    x0, total = 60.0, 860.0
    by, bh = 95.0, 52.0
    fields = [
        ("напрям", 2, "31–30", RED_FILL, POS),
        ("розмір", 14, "29–16", BLUE_FILL, NEG),
        ("тип", 8, "15–8", GREEN_FILL, FIELD),
        ("номер", 8, "7–0", WARM_FILL, WARM),
    ]

    x = x0
    for name, bits, rng, fill, stroke in fields:
        w = total * bits / 32.0
        p.append(rect(x, by, w, bh, fill=fill, stroke=stroke, sw=1.8, rx=6))
        p.append(text(x + w / 2, by + bh / 2 + 6, str(bits), size=17, bold=True))
        p.append(text(x + w / 2, by - 14, rng, size=11.5, color=MUTED))
        p.append(text(x + w / 2, by + bh + 24, name, size=12.5, bold=True, color=stroke))
        x += w

    p.append(text(70, 208, "як складається число", size=12.5, color=MUTED, anchor="start"))

    rows = [
        ("напрям", "_IOC_READ = 2", "2 << 30  =  0x80000000", POS),
        ("розмір", "sizeof(int) = 4", "4 << 16  =  0x00040000", NEG),
        ("тип", "'R' = 0x52", "0x52 << 8  =  0x00005200", FIELD),
        ("номер", "0x00", "0 << 0  =  0x00000000", WARM),
    ]
    ry = 244.0
    for name, val, res, color in rows:
        p.append(text(70, ry, name, size=13.5, bold=True, color=color, anchor="start"))
        p.append(text(250, ry, val, size=13, anchor="start"))
        p.append(text(560, ry, res, size=13, color=MUTED, anchor="start"))
        ry += 38

    p.append(line(60, 372, 920, 372, color=LINE, sw=1.2))
    p.append(text(490, 404, "RNDGETENTCNT = _IOR('R', 0x00, int) = 0x80045200",
                  size=15, bold=True))

    render(os.path.join(IMG, 'ioc-encoding.svg'), W, H, *p)


# ── 3. Шлях команди: ядро комутує, зміст живе в драйвері ────────────────────
def fig_dispatch():
    W, H = 1000, 490
    p = []

    p.append(fitbox(50, 40, 330, 56, ["ioctl(fd, 0x80045200, &n)"], size=14, bold=True,
                    fill=FILL, stroke=LINE, sw=1.8, rx=8))

    p.append(line(20, 118, 980, 118, color=MUTED, sw=1.3, dash="7 5"))
    p.append(text(966, 111, "межа ядра", size=12, color=MUTED, anchor="end"))

    p.append(arrow(215, 100, 215, 141, color=LINE, sw=1.8))
    p.append(fitbox(50, 145, 330, 56, ["ядро: sys_ioctl"], size=14, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))

    p.append(arrow(384, 173, 464, 173, color=MUTED, sw=1.6))
    p.append(fitbox(470, 140, 400, 66,
                    ["ядро розбирає саме лише кілька:", "FIONBIO · FIOCLEX · FIONCLEX"],
                    size=12.5, fill=FILL, stroke=MUTED, sw=1.4, rx=8))

    p.append(arrow(215, 205, 215, 246, color=LINE, sw=1.8))
    p.append(fitbox(50, 250, 330, 56, ["f_op->unlocked_ioctl(file, cmd, arg)"],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8, rx=8))

    p.append(arrow(215, 310, 215, 351, color=LINE, sw=1.8))
    p.append(fitbox(50, 355, 330, 56, ["switch (cmd) — код драйвера"], size=13.5, bold=True,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))

    outs = [
        (270, "відома команда → робота, 0", FIELD, GREEN_FILL),
        (340, "чужа команда → −ENOTTY", POS, RED_FILL),
        (410, "погана адреса → −EFAULT", POS, RED_FILL),
    ]
    for oy, label, color, fill in outs:
        p.append(fitbox(560, oy, 380, 48, [label], size=13, fill=fill, stroke=color,
                        sw=1.5, rx=8))
        p.append(arrow(384, 383, 554, oy + 24, color=color, sw=1.5))

    render(os.path.join(IMG, 'dispatch.svg'), W, H, *p)


# ── 4. Розкладка структури-аргументу на двох ABI ────────────────────────────
def fig_burst_layout():
    W, H = 1000, 460
    p = []
    CELL = 30.0
    x0 = 230.0
    RH = 38.0
    NOTE_X = 730.0

    def strip(y, label, spans, note, note_color):
        p.append(text(x0 - 20, y + RH / 2 + 5, label, size=12.5, bold=True, anchor="end"))
        x = x0
        for nb, t, fill, stroke in spans:
            w = CELL * nb
            p.append(rect(x, y, w, RH, fill=fill, stroke=stroke, sw=1.6, rx=4))
            p.append(text(x + w / 2, y + RH / 2 + 5, t, size=11.5))
            x += w
        p.append(text(NOTE_X, y + RH / 2 + 5, note, size=12.5, bold=True,
                      color=note_color, anchor="start"))

    WANT = (4, "want · 4 Б", BLUE_FILL, NEG)
    ISSUED = (8, "issued · 8 Б", GREEN_FILL, FIELD)

    p.append(text(50, 46, "без явного доповнення:   __u32 want;  __u64 issued;",
                 size=14, bold=True, anchor="start"))
    strip(70, "32-бітний x86", [WANT, ISSUED], "sizeof 12  →  0xC00C4203", POS)
    strip(128, "x86-64",
          [WANT, (4, "дірка · 4 Б", RED_FILL, POS), ISSUED],
          "sizeof 16  →  0xC0104203", POS)

    p.append(text(50, 226, "з явним доповненням:   __u32 want;  __u32 __pad;  __u64 issued;",
                 size=14, bold=True, anchor="start"))
    strip(250, "обидва ABI",
          [WANT, (4, "__pad · 4 Б", WARM_FILL, WARM), ISSUED],
          "sizeof 16  →  0xC0104203", FIELD)

    p.append(line(50, 330, 950, 330, color=LINE, sw=1.2))

    concl = [
        "Розмір структури вкладено в саме число команди — це поле «розмір», біти 29–16.",
        "Інший sizeof дає інше число, switch у драйвері його не впізнає й віддає −ENOTTY —",
        "хоч програма й драйвер зібрані з одного заголовка.",
    ]
    yy = 366.0
    for s in concl:
        p.append(text(50, yy, s, size=13, anchor="start"))
        yy += 30

    render(os.path.join(IMG, 'burst-layout.svg'), W, H, *p)


fig_two_planes()
fig_ioc_encoding()
fig_dispatch()
fig_burst_layout()
print("ok")
