# -*- coding: utf-8 -*-
"""Фігури до теми «ECC у пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"   # контрольні біти / spare-зона (тепле, читабельне)


# ── 1. Серверна RAM: 64 даних + 8 контролю = 72-бітне слово ───────────────────
def fig_dimm():
    W, H = 820, 430
    f = [text(W / 2, 28, "Чому ECC-модуль ширший: 64 + 8 = 72", size=16, bold=True)]
    f.append(text(W / 2, 50, "до кожних 64 бітів даних SECDED додає 8 контрольних — слово на шині стає 72-бітним",
                  size=11, color=MUTED, italic=True))

    # стрічка з 64 синіх + 8 бурштинових клітинок
    x0, y0, cw, ch, gap, bgap = 36, 86, 8.0, 24, 1.2, 5
    for i in range(64):
        x = x0 + i * (cw + gap) + (i // 8) * bgap      # пробіл між байтами
        f.append(rect(x, y0, cw, ch, fill="#eaf0fd", stroke=NEG, sw=0.8, rx=1))
    data_end = x0 + 63 * (cw + gap) + (63 // 8) * bgap + cw
    ecc_x0 = data_end + 22
    for i in range(8):
        x = ecc_x0 + i * (cw + gap)
        f.append(rect(x, y0, cw, ch, fill="#fdf3e0", stroke=AMBER, sw=0.8, rx=1))
    ecc_end = ecc_x0 + 7 * (cw + gap) + cw

    f.append(text((x0 + data_end) / 2, y0 - 8, "64 біти даних (8 байтів)", size=12, color=NEG, bold=True))
    f.append(text((ecc_x0 + ecc_end) / 2, y0 - 8, "+8 контролю", size=12, color=AMBER, bold=True))
    # дужка-підсумок під стрічкою
    f.append(line(x0, y0 + ch + 8, ecc_end, y0 + ch + 8, color=INK, sw=1.4))
    f.append(text((x0 + ecc_end) / 2, y0 + ch + 26, "= 72-бітне слово, яке контролер читає за один такт",
                  size=12.5, color=INK, bold=True))

    # дві поведінки SECDED
    b1 = ("1 перевернутий біт\n"
          "ECC знаходить ЯКИЙ\n"
          "і виправляє на льоту —\n"
          "програма нічого не помічає")
    b2 = ("2 перевернуті біти\n"
          "виправити вже не може,\n"
          "але ТОЧНО бачить псування\n"
          "→ зупинка чи перезапуск")
    f.append(fitbox(70, 196, 300, 116, b1, size=12.5, color=INK, bold=True,
                    fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(220, 326, "лічильник виправлень тихо росте", size=10.5, color=MUTED, italic=True))
    f.append(fitbox(390, 196, 300, 116, b2, size=12.5, color=INK, bold=True,
                    fill="#fdeceb", stroke=POS, sw=1.8))
    f.append(text(540, 326, "краще впасти, ніж тихо збрехати", size=10.5, color=MUTED, italic=True))

    f.append(text(W / 2, 366, "SECDED — Single Error Correct, Double Error Detect: виправити один, помітити два",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 404,
                  "вісім зайвих бітів на 64 (≈12.5% пам'яті) — ціна за те, щоб поодинокий збій не валив сервер",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "dimm-72bit.svg"), W, H, *f)


# ── 2. NAND: запасна зона й код, що росте разом із дефектами ───────────────────
def fig_nand():
    W, H = 760, 380
    f = [text(W / 2, 28, "NAND: запасна зона під сильніший код", size=16, bold=True)]
    f.append(text(W / 2, 50, "комірки зношуються й течуть — тому ECC тут не розкіш, а умова роботи",
                  size=11, color=MUTED, italic=True))

    # сторінка: дані + spare
    f.append(text(60, 86, "одна фізична сторінка NAND", size=11, color=MUTED, anchor="start"))
    f.append(rect(60, 96, 470, 56, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(295, 130, "дані сторінки (напр. 2048 байтів)", size=14, color=NEG, bold=True))
    f.append(rect(540, 96, 160, 56, fill="#fdf3e0", stroke=AMBER, sw=1.8, rx=6))
    f.append(text(620, 122, "запасна зона", size=12.5, color=AMBER, bold=True))
    f.append(text(620, 140, "(ECC + службове)", size=10.5, color=AMBER))

    f.append(text(60, 196, "Що більше циклів стирання — то більше бітів «пливе», то сильніший код:",
                  size=12.5, bold=True, anchor="start"))

    # три стадії зносу
    cards = [
        ("свіжа NAND", "1–4 биті/сектор", FIELD),
        ("середина ресурсу", "близько 8/сектор", AMBER),
        ("під кінець ресурсу", "24–40 і більше", POS),
    ]
    x = 70
    for i, (title_, val, col) in enumerate(cards):
        f.append(rect(x, 220, 190, 72, fill=BG, stroke=col, sw=1.8, rx=8))
        f.append(text(x + 95, 246, title_, size=13, color=col, bold=True))
        f.append(text(x + 95, 272, val, size=14, color=INK, bold=True))
        if i < 2:
            f.append(arrow(x + 190, 256, x + 214, 256, color=INK, sw=1.8))
        x += 214

    f.append(text(W / 2, 332,
                  "контролер рахує BCH чи LDPC на стільки бітів; «зношений» накопичувач — це",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 350,
                  "той, де код уже не встигає виправляти більше помилок, ніж народжується",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "nand-spare.svg"), W, H, *f)


# ── 2b. Дев'ять чіпів DRAM → 72-бітне слово (для вставки) ─────────────────────
def fig_nine_chips():
    W, H = 760, 300
    f = [text(W / 2, 28, "Дев'ять однакових чіпів: 8 несуть дані, дев'ятий — контроль", size=15, bold=True)]
    f.append(text(W / 2, 50, "вісім чіпів по 8 ліній складають 64 біти даних, дев'ятий додає 8 — контролер читає 72 біти за такт",
                  size=10.5, color=MUTED, italic=True))

    cw, gap, x0, y0, ch = 70, 6, 40, 78, 58
    for i in range(9):
        x = x0 + i * (cw + gap)
        ecc = (i == 8)
        col = POS if ecc else NEG
        fill = "#fdeceb" if ecc else "#eaf0fd"
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=1.8, rx=7))
        f.append(text(x + cw / 2, y0 + 24, "DRAM", size=11, color=INK, bold=True))
        f.append(text(x + cw / 2, y0 + 44, "ECC" if ecc else "×8", size=13, color=col, bold=True))
    data_end = x0 + 7 * (cw + gap) + cw
    ecc_x = x0 + 8 * (cw + gap)
    # дужки
    by = y0 + ch + 12
    f.append(line(x0, by, data_end, by, color=NEG, sw=2))
    f.append(text((x0 + data_end) / 2, by + 18, "8 чіпів × 8 = 64 біти даних", size=12, color=NEG, bold=True))
    f.append(line(ecc_x, by, ecc_x + cw, by, color=POS, sw=2))
    f.append(text(ecc_x + cw / 2, by + 18, "+8 контролю", size=11.5, color=POS, bold=True))

    f.append(rect(40, 200, 680, 46, fill=BG, stroke=INK, sw=1.6, rx=10))
    f.append(text(380, 229, "64 біти даних  +  8 біт контролю  =  72-бітне слово, яке контролер перевіряє за один такт",
                  size=13, color=INK, bold=True))
    f.append(text(W / 2, 282,
                  "звідси «магічне» число 72 у специфікації серверних модулів і дев'ятий чіп на планці",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "nine-chips.svg"), W, H, *f)


# ── 3. Три домівки ECC і хто рахує контрольні біти ────────────────────────────
def fig_three_homes():
    W, H = 780, 470
    f = [text(W / 2, 28, "Три домівки ECC — і хто рахує контрольні біти", size=16, bold=True)]
    f.append(text(W / 2, 50,
                  "усюди той самий рецепт: до даних кладуть контрольні біти, перевіряє їх окремий блок, не процесор",
                  size=10.5, color=MUTED, italic=True))

    cols = [
        ("Серверна RAM", "контролер пам'яті в CPU",
         ["код: SECDED (Геммінг + парність)", "зерно: 64 біти даних",
          "контроль: +8 біт (9-й чіп)", "вміє: 1 виправити, 2 помітити"], NEG),
        ("Накопичувач NAND", "контролер SSD / eMMC",
         ["код: BCH або LDPC", "зерно: сектор 512 Б … 4 КБ",
          "контроль: десятки–сотні біт", "вміє: виправити багато біт"], POS),
        ("Flash у мікроконтролері", "кеш-контролер флешу",
         ["код: SECDED на слово", "зерно: слово 64–128 біт",
          "контроль: +6…8 біт на слово", "вміє: 1 виправити, 2 помітити"], FIELD),
    ]
    cw, x = 236, 30
    for title_, who, rows, col in cols:
        f.append(rect(x, 78, cw, 350, fill=BG, stroke=col, sw=2, rx=10))
        f.append(rect(x, 78, cw, 40, fill="#f4f6f8", stroke=col, sw=2, rx=10))
        f.append(text(x + cw / 2, 104, title_, size=14, color=col, bold=True))
        # дані + ECC схематично
        f.append(rect(x + 16, 134, cw - 96, 22, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
        f.append(text(x + 16 + (cw - 96) / 2, 150, "дані", size=10.5, color=NEG, bold=True))
        f.append(rect(x + cw - 72, 134, 56, 22, fill="#fdf3e0", stroke=AMBER, sw=1.2, rx=3))
        f.append(text(x + cw - 44, 150, "ECC", size=10.5, color=AMBER, bold=True))
        f.append(text(x + cw / 2, 182, who, size=11.5, color=INK, bold=True))
        f.append(line(x + 16, 196, x + cw - 16, 196, color="#e0e0e0", sw=1.2))
        y = 220
        for r in rows:
            f.append(text(x + 16, y, r, size=11, anchor="start"))
            y += 26
        x += cw + 18

    f.append(text(W / 2, 452,
                  "спільне в усіх трьох: контрольні біти рахує окремий блок, а не ваш код — для програми ECC майже безкоштовний",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "three-homes.svg"), W, H, *f)


# ── 4. «Перший байт»: ескалація CE → UE і де читати лічильники ────────────────
def fig_signals():
    W, H = 780, 410
    f = [text(W / 2, 28, "Як ECC проявляється для інженера", size=16, bold=True)]
    f.append(text(W / 2, 50,
                  "поки виправляється одна помилка, ECC мовчить — голосною подія стає лише тоді, коли код безсилий",
                  size=10.5, color=MUTED, italic=True))

    # ескалація
    stages = [
        ("1 біт → тихо виправлено", "дані для програми чисті;\nслід — лише в лічильнику CE", FIELD),
        ("лічильник CE росте", "багато виправлень з однієї\nадреси — комірка слабне", AMBER),
        ("нескоригована (UE)", "двох+ біт не виправити:\nпрапор, лог, переривання", POS),
    ]
    cw, x = 236, 30
    for i, (head, body, col) in enumerate(stages):
        f.append(rect(x, 80, cw, 96, fill=BG, stroke=col, sw=1.8, rx=10))
        f.append(text(x + cw / 2, 106, head, size=13, color=col, bold=True))
        f.append(line(x + 14, 116, x + cw - 14, 116, color="#e0e0e0", sw=1.2))
        f.append(mtext(x + cw / 2, 138, body, size=11, color=INK))
        if i < 2:
            f.append(arrow(x + cw + 1, 128, x + cw + 17, 128, color=INK, sw=2))
        x += cw + 18

    # де читати
    f.append(text(40, 218, "Де ці лічильники реально читати:", size=12.5, bold=True, anchor="start"))
    homes = [
        ("Сервер (RAM)", "EDAC / mcelog у Linux:", "ce_count, ue_count на канал —\nскільки виправлено й скільки\nфатальних", NEG),
        ("SSD / eMMC", "атрибути S.M.A.R.T.:", "окремі лічильники під\nECC-виправлення й під\nнескориговані сектори", NEG),
        ("МК (вбудований Flash)", "status-регістр контролера:", "біти «сталося виправлення»\nй «двобітна помилка»,\nчасто й адреса збою", NEG),
    ]
    x = 30
    for title_, tool, body, col in homes:
        f.append(rect(x, 230, cw, 150, fill=BG, stroke=INK, sw=1.4, rx=10))
        f.append(text(x + 14, 254, title_, size=12.5, bold=True, anchor="start"))
        f.append(line(x + 14, 262, x + cw - 14, 262, color="#e0e0e0", sw=1.2))
        f.append(text(x + 14, 284, tool, size=11.5, color=col, bold=True, anchor="start"))
        f.append(mtext(x + 14, 306, body, size=10.5, anchor="start"))
        x += cw + 18
    render(os.path.join(IMG, "first-signal.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dimm()
    fig_nand()
    fig_nine_chips()
    fig_three_homes()
    fig_signals()
    print("OK: 5 figures ->", IMG)
