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


# ── 1. Дорога одного буфера: гість → гіпервізор → гість ─────────────────────
def fig_one_buffer():
    W, H = 1320, 900
    p = []
    lx, rx = 320, 1000

    p.append(text(lx, 66, "ГОСТЬОВЕ ЯДРО", size=15, bold=True))
    p.append(text(rx, 66, "ГІПЕРВІЗОР", size=15, bold=True))
    p.append(line(660, 92, 660, 762, color=MUTED, sw=1.4, dash="7 6"))

    def box(cx, cy, lines, fill):
        frag, w, h = textbox(cx, cy, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        return w, h

    w1, h1 = box(lx, 150, ["виділяє буфер у власній пам'яті",
                           "й позначає його «сюди пише пристрій»"], GREEN_FILL)
    w2, h2 = box(lx, 285, ["кладе номер дескриптора в доступне кільце",
                           "й торкає регістр сповіщення"], GREEN_FILL)
    w3, h3 = box(rx, 440, ["бачить сповіщення, читає дескриптор",
                           "і бере байти з власного джерела:",
                           "getrandom() господаря"], WARM_FILL)
    w4, h4 = box(rx, 610, ["пише байти просто в пам'ять гостя,",
                           "в ужите кільце кладе номер буфера",
                           "і скільки байтів записав"], WARM_FILL)
    w5, h5 = box(lx, 775, ["обробник переривання забирає буфер;",
                           "довжина — єдине, що приїхало назад"], BLUE_FILL)

    p.append(arrow(lx, 150 + h1 / 2 + 12, lx, 285 - h2 / 2 - 12))
    p.append(arrow(lx + w2 / 2 + 14, 285 + 24, rx - w3 / 2 - 14, 440 - 34))
    p.append(arrow(rx, 440 + h3 / 2 + 12, rx, 610 - h4 / 2 - 12))
    p.append(arrow(rx - w4 / 2 - 14, 610 + 30, lx + w5 / 2 + 14, 775 - 26))

    frag, _, _ = textbox(660, 860, ["Назад не йде нічого, крім довжини:",
                                    "буфер описано як придатний лише для запису пристроєм."],
                         size=12.5, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'one-buffer.svg'), W, H, *p,
           title="Обмін одним буфером між драйвером virtio-rng і гіпервізором")


# ── 2. Шлях байтів усередині гостьового ядра ────────────────────────────────
def fig_kernel_path():
    W, H = 1200, 900
    p = []
    cx, nx = 400, 960

    ys = [90, 210, 335, 460, 590, 710, 820]
    cells = [
        (["пристрій virtio-rng на шині", "(PCI або MMIO)"], GREY_FILL),
        (["драйвер virtio-rng:", "реєструє себе в каркасі hwrng"], WARM_FILL),
        (["ядро hwrng: /dev/hwrng для програм", "і потік hwrng_fillfn для самого ядра"], WARM_FILL),
        (["add_hwgenerator_randomness(буфер, байти, біти)"], BLUE_FILL),
        (["накопичувач: стан BLAKE2s на 256 бітів", "плюс лічильник зарахованих бітів"], GREEN_FILL),
        (["генератор ChaCha20"], GREEN_FILL),
        (["getrandom(), /dev/urandom, ключі всередині ядра"], GREY_FILL),
    ]
    geo = []
    for y, (lines, fill) in zip(ys, cells):
        frag, w, h = textbox(cx, y, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        geo.append((y, w, h))
    for (y1, _, hh1), (y2, _, hh2) in zip(geo, geo[1:]):
        p.append(arrow(cx, y1 + hh1 / 2 + 12, cx, y2 - hh2 / 2 - 12))

    def note(idx, lines, fill=GREY_FILL):
        y, w, _ = geo[idx]
        frag, nw, _ = textbox(nx, y, lines, size=12.5, pad=12, fill=fill,
                              stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + w / 2 + 12, y, nx - nw / 2 - 14, y,
                      color=MUTED, sw=1.1, dash="5 4"))

    note(2, ["цю роботу колись", "виконував rngd", "у просторі користувача"])
    note(3, ["перший аргумент — усе,", "що прийшло;", "третій — скільки з того", "зараховувати"], WARM_FILL)
    note(4, ["стеля лічильника — 256:", "стільки важить ключ,", "більше зараховувати нікуди"])

    render(os.path.join(IMG, 'kernel-path.svg'), W, H, *p,
           title="Від пристрою до getrandom(): шлях байтів у гостьовому ядрі")


# ── 3. Коли надходить кожне джерело непередбачності ─────────────────────────
def fig_boot_timeline():
    W, H = 1260, 900
    p = []
    axis_y = 430

    p.append(arrow(60, axis_y, 1210, axis_y, sw=2))
    p.append(text(1150, axis_y - 18, "час роботи", size=13, color=MUTED))

    def mark(x, cy, lines, fill):
        frag, w, h = textbox(x, cy, lines, size=12.5, pad=12, fill=fill,
                             stroke=LINE, sw=1.4)
        p.append(frag)
        if cy < axis_y:
            p.append(line(x, cy + h / 2 + 8, x, axis_y - 10, color=MUTED, sw=1.2, dash="5 4"))
        else:
            p.append(line(x, axis_y + 10, x, cy - h / 2 - 8, color=MUTED, sw=1.2, dash="5 4"))
        p.append(circle(x, axis_y, 6, fill=INK, stroke=INK, sw=1))

    mark(230, 630, ["мить першої інструкції ядра",
                    "зерно від прошивки: SETUP_RNG_SEED,",
                    "EFI RNG або rng-seed у дереві пристроїв"], GREEN_FILL)
    mark(470, 250, ["перебір шини й probe драйвера",
                    "з'являється virtio-rng, і каркас hwrng",
                    "робить його поточним джерелом"], WARM_FILL)
    mark(720, 640, ["сплеск",
                    "потік качає буфер за буфером без пауз,",
                    "поки не набереться 256 зарахованих бітів"], BLUE_FILL)
    mark(950, 255, ["ядро вважає себе готовим",
                    "getrandom() перестає блокувати"], WARM_FILL)
    mark(1140, 645, ["далі — крапельниця", "одне читання раз на ≤60 с"], BLUE_FILL)

    frag, _, _ = textbox(630, 810, ["Окремою колією: клон або відновлення знімка повертає ядро в минулий стан.",
                                    "virtio-rng цього не помічає — тривогу б'є пристрій VM Generation ID."],
                         size=12.5, pad=13, fill=RED_FILL, stroke=POS, sw=1.3)
    p.append(frag)

    render(os.path.join(IMG, 'boot-timeline.svg'), W, H, *p,
           title="Коли яке джерело непередбачності доходить до гостьового ядра")


# ── 4. Життя одного буфера в драйвері: прохання завжди в польоті ────────────
def fig_driver_cycle():
    W, H = 1340, 600
    p = []
    ROW = 210
    x1, x2, x3 = 240, 670, 1100

    def state(cx, head, lines, fill):
        frag, w, h = textbox(cx, ROW, [head] + lines, size=13, pad=15,
                             fill=fill, stroke=LINE, sw=1.6)
        p.append(frag)
        return w, h

    w1, h1 = state(x1, "У ПОЛЬОТІ", ["буфер стоїть у віртчерзі",
                                     "avail = 0; читач спить"], BLUE_FILL)
    w2, h2 = state(x2, "ПОВНИЙ", ["зворотний виклик забрав буфер",
                                  "avail = min(len, розмір буфера)"], GREEN_FILL)
    w3, h3 = state(x3, "РОЗДАЄТЬСЯ", ["read() віддає шматки",
                                      "idx росте до avail"], WARM_FILL)

    p.append(arrow(x1 + w1 / 2 + 12, ROW, x2 - w2 / 2 - 12, ROW))
    p.append(arrow(x2 + w2 / 2 + 12, ROW, x3 - w3 / 2 - 12, ROW))

    frag, _, _ = textbox((x1 + x2) / 2, 96, ["переривання від пристрою",
                                             "virtqueue_get_buf() дає довжину"],
                         size=12, pad=10, fill=GREY_FILL, stroke=MUTED, sw=1.1)
    p.append(frag)
    frag, _, _ = textbox((x2 + x3) / 2, 96, ["complete(&filled)",
                                             "читач прокинувся"],
                         size=12, pad=10, fill=GREY_FILL, stroke=MUTED, sw=1.1)
    p.append(frag)

    # зворотна дуга: буфер вичерпано → нове прохання
    back = 420
    p.append(line(x3, ROW + h3 / 2 + 12, x3, back, color=LINE, sw=1.7))
    p.append(line(x3, back, x1, back, color=LINE, sw=1.7))
    p.append(arrow(x1, back, x1, ROW + h1 / 2 + 12))

    frag, _, _ = textbox(x2, back, ["буфер вичерпано (idx == avail) → krng_arm()",
                                    "sg_init_one · virtqueue_add_inbuf · virtqueue_kick"],
                         size=12.5, pad=12, fill=FILL, stroke=LINE, sw=1.3)
    p.append(frag)

    frag, _, _ = textbox(x1, 40, ["probe: virtio_device_ready(),",
                                  "потім перший krng_arm()"],
                         size=12, pad=10, fill=GREY_FILL, stroke=MUTED, sw=1.1)
    p.append(frag)

    frag, _, _ = textbox(x2, 540, ["У черзі стоїть рівно одне прохання й ніколи — жодного:",
                                   "наступні байти вже їдуть, поки читач розбирає попередні."],
                         size=12.5, pad=13, fill=GREEN_FILL, stroke=FIELD, sw=1.3)
    p.append(frag)

    render(os.path.join(IMG, 'driver-cycle.svg'), W, H, *p,
           title="Цикл одного буфера в драйвері virtio-rng")


if __name__ == '__main__':
    fig_one_buffer()
    fig_kernel_path()
    fig_boot_timeline()
    fig_driver_cycle()
    print("ok")
