# -*- coding: utf-8 -*-
# Фігури теми «Мікрокод». svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED_F, RED = "#fdf4f4", POS          # складна / гаряча гілка, мікрокод-ROM
GRN_F, GRN = "#f4f7f4", FIELD        # проста / швидка гілка
GLD_F, GLD = "#fbf3df", "#a9842f"    # мікрокод, сховище, патч
BLU_F, BLU = "#eef2fd", NEG          # вхід / машинна команда


# ── micro-decode: одна машинна команда → потік внутрішніх мікрооперацій ───────
# Ідея: проста команда йде крізь ЗАШИТИЙ декодер (миттєво, 1 µop); складна —
# ловиться в мікрокод-ROM, звідки виходить готова ПОСЛІДОВНІСТЬ µops.
def fig_micro_decode():
    W, H = 780, 430
    p = []

    # вхід: машинна команда
    p.append(rect(300, 46, 180, 46, fill=BLU_F, stroke=BLU, sw=1.9, rx=8))
    p.append(text(390, 66, "машинна команда", size=11, color=BLU, bold=True))
    p.append(text(390, 83, "напр. ADD [mem], EAX", size=10.5, color=INK))
    p.append(arrow(390, 94, 390, 122, color=INK, sw=1.9))

    # розгалуження — декодер розбирає опкод
    p.append(rect(250, 124, 280, 40, fill=BG, stroke=INK, sw=1.6, rx=8))
    p.append(text(390, 149, "декодер: проста чи складна?", size=11.5, color=INK, bold=True))

    # ── ліва гілка: проста → зашитий декодер → 1 µop ──
    p.append(arrow(320, 166, 200, 210, color=GRN, sw=1.9))
    p.append(rect(60, 212, 280, 66, fill=GRN_F, stroke=GRN, sw=2, rx=10))
    p.append(text(200, 234, "ЗАШИТИЙ декодер", size=12, color=GRN, bold=True))
    p.append(text(200, 252, "проста часта команда —", size=10, color=MUTED, italic=True))
    p.append(text(200, 267, "µop виходить одразу з вентилів", size=10, color=MUTED, italic=True))
    p.append(arrow(200, 280, 200, 306, color=GRN, sw=1.9))
    p.append(rect(96, 308, 208, 30, fill=BG, stroke=GRN, sw=1.6, rx=6))
    p.append(text(200, 328, "1 µop:  add r, [t]", size=11, color=INK, bold=True))

    # ── права гілка: складна → мікрокод-ROM → послідовність µops ──
    p.append(arrow(460, 166, 580, 210, color=RED, sw=1.9))
    p.append(rect(440, 212, 300, 66, fill=RED_F, stroke=RED, sw=2, rx=10))
    p.append(text(590, 234, "МІКРОКОД-ROM", size=12, color=RED, bold=True))
    p.append(text(590, 252, "складна/рідкісна команда —", size=10, color=MUTED, italic=True))
    p.append(text(590, 267, "ROM видає готовий рецепт µops", size=10, color=MUTED, italic=True))
    p.append(arrow(590, 280, 590, 306, color=RED, sw=1.9))
    seq = ["µop1:  load  t, [mem]",
           "µop2:  add   t, EAX",
           "µop3:  store [mem], t"]
    sy = 308
    for i, ln in enumerate(seq):
        p.append(rect(456, sy, 268, 26, fill=BG, stroke=RED, sw=1.3, rx=5))
        p.append(text(462, sy + 17, ln, size=10.5, color=INK, anchor="start"))
        sy += 30

    p.append(text(W / 2, H - 16,
                  "усередині процесор виконує лише прості µop-и; мікрокод — це рецепт, "
                  "як розкласти складну команду на них",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "micro-decode.svg"), W, H, *p,
           title="Одна машинна команда розкладається на потік мікрооперацій")


# ── microinstruction-bits: один рядок мікрокоду як поле бітів на керувальні лінії ─
# Ідея: горизонтальна мікрокоманда — майже кожен біт напряму вмикає одну лінію
# (широко, швидко). Вертикальна — стиснене поле-код, яке ще треба РОЗКОДУВАТИ.
def fig_microinstruction_bits():
    W, H = 780, 420
    p = []

    # ── зверху: ГОРИЗОНТАЛЬНА мікрокоманда ──
    p.append(text(W / 2, 52, "ГОРИЗОНТАЛЬНА: біт = лінія (широка, швидка)",
                  size=12.5, color=GLD, bold=True))
    bits = [("1", "ALU=+", RED), ("0", "ALU=−", RED), ("1", "чит.RA", GRN),
            ("1", "чит.RB", GRN), ("0", "чит.mem", GRN), ("1", "зап.Rd", BLU),
            ("0", "шина W", BLU), ("1", "PC++", GLD)]
    n = len(bits)
    cw = 84
    x0 = (W - n * cw) / 2
    by = 66
    for i, (b, lab, col) in enumerate(bits):
        x = x0 + i * cw
        fillc = GLD_F if b == "1" else BG
        p.append(rect(x, by, cw - 6, 38, fill=fillc, stroke=col, sw=1.7, rx=5))
        p.append(text(x + (cw - 6) / 2, by + 26, b, size=16, color=INK, bold=True))
        # лінія вниз до «дроту»
        active = (b == "1")
        yline = by + 38
        p.append(line(x + (cw - 6) / 2, yline, x + (cw - 6) / 2, yline + 30,
                      color=(col if active else MUTED), sw=2 if active else 1,
                      dash=None if active else "3,3"))
        p.append(text(x + (cw - 6) / 2, yline + 46, lab, size=9,
                      color=(col if active else MUTED), bold=active))
    p.append(text(W / 2, by + 104, "кожен біт іде ПРЯМО на свою керувальну лінію — жодного проміжного декодування",
                  size=10, color=MUTED, italic=True))

    # роздільник
    p.append(line(60, 224, W - 60, 224, color=MUTED, sw=1, dash="5,4"))

    # ── знизу: ВЕРТИКАЛЬНА мікрокоманда ──
    p.append(text(W / 2, 258, "ВЕРТИКАЛЬНА: стиснений код, який ще треба розкодувати (вужча, повільніша)",
                  size=12.5, color=RED, bold=True))
    # компактне поле
    p.append(rect(150, 274, 200, 40, fill=RED_F, stroke=RED, sw=1.9, rx=6))
    p.append(text(250, 299, "код  0 1 1", size=15, color=INK, bold=True))
    p.append(text(250, 268, "3 біти", size=9.5, color=MUTED))
    p.append(arrow(352, 294, 420, 294, color=INK, sw=1.8))
    # маленький декодер
    p.append(rect(424, 274, 130, 40, fill=BG, stroke=INK, sw=1.6, rx=7))
    p.append(text(489, 299, "декодер", size=11.5, color=INK, bold=True))
    p.append(arrow(556, 294, 620, 294, color=GLD, sw=1.8))
    p.append(rect(624, 276, 120, 36, fill=GLD_F, stroke=GLD, sw=1.6, rx=6))
    p.append(text(684, 299, "1 лінія", size=11, color=GLD, bold=True))
    p.append(text(W / 2, 352,
                  "менше бітів у сховищі, але зайвий крок розкодування коду в лінію — "
                  "економія пам'яті ціною швидкості",
                  size=10, color=MUTED, italic=True))
    p.append(text(W / 2, H - 18,
                  "розмін той самий, що всюди в мікрокоді: ширше й швидше проти щільніше й повільніше",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "microinstruction-bits.svg"), W, H, *p,
           title="Що таке один рядок мікрокоду: поле бітів на керувальні лінії")


# ── patch-flow: чому мікрокод оновлюваний і як латають помилку процесора ──────
# Ідея: у кристалі — незмінний ROM-мікрокод. На КОЖНОМУ старті BIOS/ОС заливає
# підписаний патч у on-chip SRAM (patch RAM); лічильник помилкового рецепта
# перенаправляється на виправлений. Вимкнув живлення — патч зник, ллється знову.
def fig_patch_flow():
    W, H = 780, 430
    p = []

    # кристал процесора
    p.append(rect(40, 70, 340, 300, fill="#fafafa", stroke=INK, sw=1.8, rx=14))
    p.append(text(210, 92, "КРИСТАЛ ПРОЦЕСОРА", size=12.5, color=INK, bold=True))

    # ROM-мікрокод (незмінний)
    p.append(rect(70, 110, 130, 120, fill=RED_F, stroke=RED, sw=1.9, rx=9))
    p.append(text(135, 132, "ROM", size=12, color=RED, bold=True))
    p.append(text(135, 148, "мікрокод", size=10.5, color=RED, bold=True))
    p.append(text(135, 172, "вшитий,", size=9.5, color=MUTED, italic=True))
    p.append(text(135, 186, "незмінний", size=9.5, color=MUTED, italic=True))
    p.append(text(135, 210, "тут живе", size=9, color=MUTED))
    p.append(text(135, 222, "помилковий рецепт", size=9, color=POS))

    # patch RAM (SRAM)
    p.append(rect(220, 110, 130, 120, fill=GLD_F, stroke=GLD, sw=2, rx=9))
    p.append(text(285, 132, "patch RAM", size=11.5, color=GLD, bold=True))
    p.append(text(285, 148, "(SRAM)", size=10, color=GLD, bold=True))
    p.append(text(285, 172, "порожня після", size=9.5, color=MUTED, italic=True))
    p.append(text(285, 186, "вмикання", size=9.5, color=MUTED, italic=True))
    p.append(text(285, 210, "сюди лягає", size=9, color=MUTED))
    p.append(text(285, 222, "виправлений рецепт", size=9, color=FIELD))

    # перенаправлення: ROM-рецепт → патч
    p.append(arrow(200, 250, 285, 234, color=INK, sw=1.7))
    p.append(rect(90, 250, 230, 40, fill=BG, stroke=INK, sw=1.5, rx=7))
    p.append(text(205, 267, "збіг адреси рецепта →", size=10, color=INK, bold=True))
    p.append(text(205, 282, "брати рядки з patch RAM, не з ROM", size=9.5, color=INK))
    p.append(text(210, 320, "виконавчі блоки бачать уже", size=10, color=MUTED, italic=True))
    p.append(text(210, 336, "виправлений мікрокод", size=10, color=FIELD, bold=True))
    p.append(text(210, 356, "вимкнув живлення → patch RAM чиста", size=9.5, color=POS, italic=True))

    # зовнішнє джерело патча
    p.append(rect(470, 96, 260, 60, fill=BLU_F, stroke=BLU, sw=1.9, rx=10))
    p.append(text(600, 118, "BIOS / ОС на старті", size=12, color=BLU, bold=True))
    p.append(text(600, 138, "тримають підписаний патч", size=10, color=MUTED, italic=True))

    p.append(rect(470, 176, 260, 50, fill=BG, stroke=BLU, sw=1.5, rx=8))
    p.append(text(600, 197, "перевірити підпис Intel/AMD", size=10.5, color=INK, bold=True))
    p.append(text(600, 213, "(чужий мікрокод не залити)", size=9.5, color=MUTED, italic=True))

    p.append(arrow(600, 156, 600, 174, color=BLU, sw=1.7))
    p.append(arrow(468, 201, 352, 175, color=GLD, sw=2.2))
    p.append(text(468, 158, "залити в patch RAM", size=10, color=GLD, bold=True))

    # цикл «на кожен старт»
    p.append(text(600, 262, "НА КОЖНЕ ВВІМКНЕННЯ:", size=11, color=INK, bold=True))
    steps = ["1. живлення → patch RAM порожня",
             "2. firmware перевіряє й заливає патч",
             "3. рецепти помилок перенаправлені",
             "4. далі процесор працює виправлений"]
    sy = 280
    for s in steps:
        p.append(text(475, sy, s, size=10, color=MUTED, anchor="start"))
        sy += 22

    p.append(text(W / 2, H - 14,
                  "саме так апаратну помилку готового процесора латають без нового кристала",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "patch-flow.svg"), W, H, *p,
           title="Оновлюваний мікрокод: як латають помилку процесора на старті")


if __name__ == "__main__":
    fig_micro_decode()
    fig_microinstruction_bits()
    fig_patch_flow()
    print("OK: figures written to", OUT)
