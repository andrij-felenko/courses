# -*- coding: utf-8 -*-
"""Фігури до теми «Регістри пристрою в пам'яті: ioremap і readl/writel»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_BG = "#eaf0fd"
GREEN_BG = "#e6f5ec"
WARM_BG = "#fff4e0"
GREY_BG = "#eef0f3"
RED_BG = "#fdecea"


# ── 1. Від числа в документації до вказівника в драйвері ────────────────────
def fig_two_spaces():
    W, H = 1360, 690
    P = [text(W / 2, 40, "Число з документації живе не в тому просторі, у якому працює код",
              size=18, bold=True)]

    LX, RX, BW = 60, 760, 540

    P.append(fitbox(LX, 70, BW, 50, "ФІЗИЧНІ АДРЕСИ — те, що їде дротами шини",
                    size=15, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(RX, 70, BW, 50, "ВІРТУАЛЬНІ АДРЕСИ — те, що бачить код ядра",
                    size=15, bold=True, fill=BLUE_BG, stroke=NEG, sw=2))

    # фізичний простір
    P.append(fitbox(LX, 150, BW, 78,
                    "0x00000000 – 0x7fffffff\nоперативна пам'ять",
                    size=14, fill=GREY_BG))
    P.append(fitbox(LX, 250, BW, 78,
                    "0xe0001000 – 0xe0001fff\nвікно регістрів контролера",
                    size=14, fill=WARM_BG, stroke=POS, sw=2))
    P.append(fitbox(LX, 350, BW, 78,
                    "решта — дірки, куди ніхто не відповідає",
                    size=14, fill=GREY_BG))

    # віртуальний простір
    P.append(fitbox(RX, 150, BW, 78,
                    "пряма карта: уся оперативна пам'ять,\nвідображена ядром наперед",
                    size=14, fill=GREY_BG))
    P.append(fitbox(RX, 250, BW, 78,
                    "область vmalloc: сюди ioremap кладе\nсвіжий запис таблиці сторінок",
                    size=14, fill=WARM_BG, stroke=POS, sw=2))
    P.append(fitbox(RX, 350, BW, 78,
                    "адреси процесів — інша половина,\nдо заліза стосунку не мають",
                    size=14, fill=GREY_BG))

    # зв'язки
    P.append(arrow(LX + BW, 189, RX, 189))
    P.append(text((LX + BW + RX) / 2, 178, "готове", size=13, color=MUTED))

    P.append(arrow(LX + BW, 289, RX, 289, color=POS, sw=2.2))
    P.append(text((LX + BW + RX) / 2, 278, "ioremap()", size=13, bold=True, color=POS))

    P.append(fitbox(230, 470, 900, 88,
                    "ioremap робить дві речі одним ходом: заводить запис у таблиці сторінок ядра\n"
                    "на потрібні фізичні кадри — і ставить у ньому тип пам'яті «пристрій»",
                    size=15, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(arrow(LX + BW / 2, 430, 500, 466))
    P.append(arrow(RX + BW / 2, 430, 860, 466))

    P.append(fitbox(230, 590, 900, 64,
                    "повернений вказівник має тип void __iomem * — і розіменовувати його не можна",
                    size=15, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(arrow(680, 560, 680, 586))
    return render(os.path.join(OUT, "two-spaces.svg"), W, H, *P)


# ── 2. Чотири припущення про пам'ять і регістр ──────────────────────────────
def fig_four_assumptions():
    W, H = 1420, 640
    P = [text(W / 2, 40, "Що процесор вважає правдою про пам'ять — і чого з цього не можна робити з регістром",
              size=18, bold=True)]

    CX = [50, 520, 990]
    CW = [440, 440, 380]
    heads = ["ПРИПУЩЕННЯ ПРО ПАМ'ЯТЬ", "ЩО НАСПРАВДІ З РЕГІСТРОМ", "ЩО МАЄ ЗАБОРОНИТИ КАРТА"]
    bgs = [GREY_BG, WARM_BG, GREEN_BG]
    strokes = [LINE, POS, FIELD]

    for i in range(3):
        P.append(fitbox(CX[i], 70, CW[i], 50, heads[i], size=14, bold=True,
                        fill=bgs[i], stroke=strokes[i], sw=2))

    rows = [
        ("читання повертає те,\nщо було записано останнім",
         "біт стану міняє саме залізо,\nа кеш віддає стару копію",
         "кешування"),
        ("зайве читання нікому\nне шкодить",
         "читання регістра черги\nвиймає з неї слово",
         "випереджальне читання"),
        ("два записи поспіль можна\nзлити в один ширший",
         "кожен запис — окрема команда;\nзлиті — це вже інша команда",
         "об'єднання записів"),
        ("порядок доступів видно\nлише за залежностями даних",
         "пристрій бачить порядок\nі діє на кожному кроці",
         "перестановку"),
    ]

    ys = [140, 250, 360, 470]
    for i, y in enumerate(ys):
        for c in range(3):
            P.append(fitbox(CX[c], y, CW[c], 86, rows[i][c], size=14,
                            bold=(c == 2), fill=bgs[c], stroke=strokes[c],
                            sw=(2 if c == 2 else 1.5)))

    P.append(fitbox(320, 580, 800, 50,
                    "усе це — не властивість адреси, а тип пам'яті в записі таблиці сторінок",
                    size=15, bold=True, fill=BLUE_BG, stroke=NEG, sw=2))
    return render(os.path.join(OUT, "four-assumptions.svg"), W, H, *P)


# ── 3. Дзвінок: чому запис відкладений і чим це кінчається ──────────────────
def fig_posted_write():
    W, H = 1380, 700
    P = [text(W / 2, 40, "Запис до пристрою відкладений: writel повертається раніше, ніж пристрій щось побачив",
              size=18, bold=True)]

    LX, RX, BW = 55, 720, 600

    P.append(fitbox(LX, 70, BW, 50, "БЕЗ ЗУСТРІЧНОГО ЧИТАННЯ", size=15, bold=True,
                    fill=RED_BG, stroke=POS, sw=2))
    P.append(fitbox(RX, 70, BW, 50, "ІЗ ЗУСТРІЧНИМ ЧИТАННЯМ", size=15, bold=True,
                    fill=GREEN_BG, stroke=FIELD, sw=2))

    left = [
        "writel(cause, REG_IRQ_CAUSE)\nміст прийняв запис і відпустив процесор",
        "обробник повернув IRQ_HANDLED\nчерез вісімдесят наносекунд",
        "лінія переривання досі притиснута —\nпристрій запису ще не бачив",
        "контролер заводить обробник\nудруге, втретє, вчетверте",
    ]
    right = [
        "writel(cause, REG_IRQ_CAUSE)\nміст прийняв запис і відпустив процесор",
        "readl(REG_IRQ_CAUSE)\nчитання не можна відкласти: чекає відповіді",
        "відповідь повернулася —\nотже, запис уже позаду неї",
        "обробник виходить, коли лінія\nвже відпущена",
    ]

    ys = [140, 252, 364, 476]
    for i, y in enumerate(ys):
        P.append(fitbox(LX, y, BW, 90, left[i], size=14, fill=WARM_BG))
        P.append(fitbox(RX, y, BW, 90, right[i], size=14, fill=GREY_BG))
        if i < 3:
            P.append(arrow(LX + BW / 2, y + 90, LX + BW / 2, ys[i + 1] - 2))
            P.append(arrow(RX + BW / 2, y + 90, RX + BW / 2, ys[i + 1] - 2))

    P.append(fitbox(LX, 600, BW, 70, "шторм холостих переривань",
                    size=16, bold=True, fill=RED_BG, stroke=POS, sw=2.2))
    P.append(fitbox(RX, 600, BW, 70, "одна затримка на переривання",
                    size=16, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2.2))
    P.append(arrow(LX + BW / 2, 566, LX + BW / 2, 596))
    P.append(arrow(RX + BW / 2, 566, RX + BW / 2, 596))
    return render(os.path.join(OUT, "posted-write.svg"), W, H, *P)


# ── 4. До вставки: кільце, дзвінок і дві адреси однієї речі ─────────────────
def fig_ring_and_doorbell():
    W, H = 1340, 700
    P = [text(W / 2, 38, "Записи в кільце, стіна, дзвінок — і те саме кільце під двома різними адресами",
              size=18, bold=True)]

    AX, AW = 60, 420
    WX, WW = 530, 150
    BX, BW = 730, 550

    P.append(fitbox(AX, 72, AW, 128,
                    "ЗАПИСИ В КІЛЬЦЕ\n"
                    "ring[i].addr  = cpu_to_le64(buf)\n"
                    "ring[i].len   = cpu_to_le32(len)\n"
                    "ring[i].flags = DESC_OWN",
                    size=15, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(WX, 72, WW, 128,
                    "БАР'ЄР\nусередині\nwritel",
                    size=15, bold=True, fill=RED_BG, stroke=POS, sw=2.2))
    P.append(fitbox(BX, 72, BW, 128,
                    "ДЗВІНОК\n"
                    "writel(i, regs + REG_TX_KICK)\n"
                    "одна транзакція завширшки чотири байти",
                    size=15, fill=BLUE_BG, stroke=NEG, sw=2))
    P.append(arrow(AX + AW, 136, WX - 4, 136))
    P.append(arrow(WX + WW, 136, BX - 4, 136))

    P.append(fitbox(BX, 250, BW, 96,
                    "КОНТРОЛЕР\nпобачив дзвінок і сам іде читати кільце",
                    size=15, fill=WARM_BG, stroke=POS, sw=2))
    P.append(arrow(BX + BW / 2, 200, BX + BW / 2, 246))

    P.append(fitbox(AX, 250, AW, 96,
                    "читає за адресою ring_dma\nі бачить готовий прапорець DESC_OWN",
                    size=15, fill=GREY_BG))
    P.append(arrow(BX - 4, 298, AX + AW + 4, 298))

    P.append(text(W / 2, 410, "Одна річ — дві адреси", size=17, bold=True))

    LX, RX, CW = 60, 690, 590
    P.append(fitbox(LX, 434, CW, 92,
                    "кільце для процесора: p->ring\n"
                    "віртуальна адреса ядра, яку дав dma_alloc_coherent",
                    size=15, fill=GREEN_BG))
    P.append(fitbox(RX, 434, CW, 92,
                    "кільце для пристрою: p->ring_dma\n"
                    "число, яке контролер виставить на шину",
                    size=15, fill=WARM_BG))
    P.append(fitbox(LX, 560, CW, 92,
                    "регістр для процесора: p->regs + 0x18\n"
                    "віртуальна адреса ядра, яку дав ioremap",
                    size=15, fill=BLUE_BG))
    P.append(fitbox(RX, 560, CW, 92,
                    "регістр для пристрою: 0xe0001018\n"
                    "фізична адреса з опису плати",
                    size=15, fill=GREY_BG))
    return render(os.path.join(OUT, "ring-and-doorbell.svg"), W, H, *P)


if __name__ == "__main__":
    for f in (fig_two_spaces, fig_four_assumptions, fig_posted_write,
              fig_ring_and_doorbell):
        print(f())
