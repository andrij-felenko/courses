# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_F = "#dfe8fc"
GREEN_F = "#dff0e6"
WARM_F = "#fff4e0"
RED_F = "#fbe6e3"
GREY_F = "#eef1f4"
WHITE = "#ffffff"
WARM = "#b8860b"


def panel(x, y, w, head, rows, stroke=LINE, head_fill=GREY_F,
          head_h=44, row_h=38, gap=10, head_size=14.5, row_size=13.5):
    """Картка: шапка + рядки, кожен рядок у власній рамці."""
    h = head_h + gap + len(rows) * row_h + gap
    out = rect(x, y, w, h, fill=WHITE, stroke=stroke, sw=1.8)
    out += fitbox(x, y, w, head_h, head, size=head_size, bold=True,
                  fill=head_fill, stroke=stroke, sw=1.6, pad=12)
    for i, r in enumerate(rows):
        ry = y + head_h + gap + i * row_h
        fill = WHITE
        st = MUTED
        col = INK
        if isinstance(r, tuple):
            r, kind = r
            if kind == "bad":
                fill, st, col = RED_F, POS, POS
            elif kind == "ok":
                fill, st, col = GREEN_F, FIELD, FIELD
            elif kind == "warn":
                fill, st, col = WARM_F, WARM, WARM
        out += fitbox(x + 12, ry, w - 24, row_h - 6, r, size=row_size,
                      fill=fill, stroke=st, sw=1.2, pad=10, color=col)
    return out, h


# ── 1. Одне виділення — три незалежні рахунки ───────────────────────────────
def fig_three_ledgers():
    W, H = 1220, 660
    p = [text(W / 2, 44, "одне виділення блоків — три незалежні рахунки",
              size=17, bold=True, color=INK)]

    # ліворуч: сам файл
    src, hsrc = panel(60, 110, 320, "файл, у який зараз пишуть",
                      ["inode 918 274",
                       "uid = 1042  (olena)",
                       "gid = 200  (video)",
                       "projid = 7  (/srv/proj-a)",
                       ("потрібно ще 8 блоків", "warn")],
                      stroke=NEG, head_fill=BLUE_F)
    p.append(src)

    # праворуч: три рахунки
    cards = [
        ("рахунок користувача 1042",
         ["зайнято 3 120 → 3 128 блоків",
          "м'яка 4 000 · жорстка 5 000",
          ("є запас", "ok")], FIELD, GREEN_F),
        ("рахунок групи 200",
         ["зайнято 48 800 → 48 808 блоків",
          "м'яка 40 000 · жорстка 50 000",
          ("м'яку перейдено, строк іде", "warn")], WARM, WARM_F),
        ("рахунок проєкту 7",
         ["зайнято 20 476 → 20 484 блоків",
          "жорстка межа 20 480 блоків",
          ("не влазить", "bad")], POS, RED_F),
    ]
    CX, CW = 500, 380
    ys = []
    for i, (head, rows, st, fl) in enumerate(cards):
        cy = 110 + i * 180
        ys.append(cy)
        c, hc = panel(CX, cy, CW, head, rows, stroke=st, head_fill=fl)
        p.append(c)
        p.append(arrow(390, 240, CX - 12, cy + hc / 2, color=MUTED, sw=1.6))

    # праворуч: підсумок
    res, hres = panel(960, 290, 210, "що поверне write()",
                      [("EDQUOT", "bad"), "решта рахунків", "значення не має"],
                      stroke=POS, head_fill=RED_F)
    p.append(res)
    p.append(arrow(CX + CW + 8, 470 + 70, 950, 400, color=POS, sw=1.8))

    p.append(text(W / 2, 630,
                  "перевірку проходять усі три рахунки, відмову дає найтісніший",
                  size=14, color=MUTED))
    return render(os.path.join(IMG, 'three-ledgers.svg'), W, H, *p)


# ── 2. М'яка межа, жорстка межа й пільговий строк ──────────────────────────
def fig_soft_hard_grace():
    W, H = 1240, 620
    p = [text(W / 2, 44, "дві межі й пільговий строк", size=17, bold=True, color=INK)]

    PW = 540
    for pi, px in enumerate([70, 660]):
        base_y, top_y = 460, 150
        p.append(rect(px, 90, PW, 430, fill=WHITE, stroke=MUTED, sw=1.2))
        # осі
        p.append(line(px + 60, base_y, px + PW - 30, base_y, color=INK, sw=1.6))
        p.append(line(px + 60, base_y, px + 60, top_y - 20, color=INK, sw=1.6))
        p.append(text(px + PW - 30, base_y + 26, "час", size=12.5, color=MUTED, anchor="end"))
        p.append(text(px + 60, top_y - 32, "зайнято", size=12.5, color=MUTED, anchor="middle"))

        hard_y, soft_y = 190, 300
        p.append(line(px + 60, hard_y, px + PW - 30, hard_y, color=POS, sw=1.6, dash="7,5"))
        p.append(line(px + 60, soft_y, px + PW - 30, soft_y, color=WARM, sw=1.6, dash="7,5"))
        p.append(text(px + 66, hard_y - 12, "жорстка межа", size=12.5, color=POS, anchor="start"))
        p.append(text(px + 66, soft_y - 12, "м'яка межа", size=12.5, color=WARM, anchor="start"))

        if pi == 0:
            pts = [(px + 60, 430), (px + 150, 360), (px + 240, 275),
                   (px + 330, 262), (px + 420, 340), (px + 505, 400)]
            head = "повернувся під м'яку межу"
            note = "строк скинуто, відмови не було"
            note_kind = FIELD
        else:
            pts = [(px + 60, 430), (px + 150, 360), (px + 240, 275),
                   (px + 330, 258), (px + 420, 250), (px + 430, 250)]
            head = "не повернувся до кінця строку"
            note = "м'яка межа діє як жорстка: EDQUOT"
            note_kind = POS

        for a, b in zip(pts, pts[1:]):
            p.append(line(a[0], a[1], b[0], b[1], color=NEG, sw=2.4))

        # позначка перетину м'якої межі
        p.append(circle(px + 240, 275, 6, fill=WHITE, stroke=WARM, sw=2))
        p.append(text(px + 240, 348, "строк пішов", size=12.5, color=WARM, anchor="middle"))

        # дужка пільгового строку
        gy = 500
        gx1, gx2 = px + 240, px + 430
        p.append(line(gx1, gy - 10, gx1, gy, color=MUTED, sw=1.4))
        p.append(line(gx2, gy - 10, gx2, gy, color=MUTED, sw=1.4))
        p.append(line(gx1, gy, gx2, gy, color=MUTED, sw=1.4))
        p.append(text((gx1 + gx2) / 2, gy + 20, "пільговий строк (типово 7 діб)",
                      size=12.5, color=MUTED, anchor="middle"))

        p.append(fitbox(px + 20, 100, PW - 40, 34, head, size=13.5, bold=True,
                        fill=GREY_F, stroke=MUTED, sw=1.2, pad=10))
        p.append(fitbox(px + 20, 552, PW - 40, 36, note, size=13.5,
                        fill=(GREEN_F if note_kind == FIELD else RED_F),
                        stroke=note_kind, color=note_kind, sw=1.4, pad=10))

    return render(os.path.join(IMG, 'soft-hard-grace.svg'), W, H, *p)


# ── 3. Лічильник усередині транзакції й поза нею ────────────────────────────
def fig_counter_and_journal():
    W, H = 1240, 640
    p = [text(W / 2, 44, "чому лічильник має правитися разом із самим виділенням",
              size=17, bold=True, color=INK)]

    left, hl = panel(70, 100, 520, "запис квоти всередині транзакції журналу",
                     ["бітова мапа: 8 блоків зайнято",
                      "inode 918 274: новий екстент, розмір",
                      "запис квоти uid=1042: +8 блоків",
                      ("коміт — або все, або нічого", "ok")],
                     stroke=FIELD, head_fill=GREEN_F)
    p.append(left)
    p.append(fitbox(70, 100 + hl + 40, 520, 96,
                    "раптове вимкнення живлення\nпісля перезавантаження лічильник дорівнює дійсності\nповний обхід не потрібен",
                    size=13.5, fill=GREEN_F, stroke=FIELD, sw=1.6, pad=12, color=FIELD))

    right, hr = panel(650, 100, 520, "запис квоти в окремому файлі поза журналом",
                      ["бітова мапа: 8 блоків зайнято  (журнал)",
                       "inode 918 274: новий екстент  (журнал)",
                       ("aquota.user: правка ще в кеші", "warn"),
                       ("коміт журналу без запису квоти", "bad")],
                      stroke=POS, head_fill=RED_F)
    p.append(right)
    p.append(fitbox(650, 100 + hr + 40, 520, 96,
                    "раптове вимкнення живлення\nлічильник розійшовся з дійсністю\nquotacheck: обхід усіх inode файлової системи",
                    size=13.5, fill=RED_F, stroke=POS, sw=1.6, pad=12, color=POS))

    p.append(arrow(330, 100 + hl + 12, 330, 100 + hl + 34, color=MUTED, sw=1.6))
    p.append(arrow(910, 100 + hr + 12, 910, 100 + hr + 34, color=MUTED, sw=1.6))

    p.append(text(W / 2, 612,
                  "лічильник — таке саме метадане, як бітова мапа: або він у тій самій транзакції, або після збою його доводиться рахувати заново",
                  size=13.5, color=MUTED))
    return render(os.path.join(IMG, 'counter-and-journal.svg'), W, H, *p)


# ── 4. Кодування слова команди quotactl() ──────────────────────────────────
def fig_qcmd_encoding():
    W, H = 1240, 670
    p = [text(W / 2, 44, "як складається перший аргумент quotactl()",
              size=17, bold=True, color=INK)]

    p.append(fitbox(70, 78, 1100, 54,
                    "quotactl( QCMD(підкоманда, тип),  \"/dev/sda1\",  id,  addr )",
                    size=15.5, bold=True, fill=BLUE_F, stroke=NEG, sw=1.8, pad=14))

    left, hl = panel(140, 175, 420, "підкоманда",
                     ["Q_GETQUOTA = 0x800007",
                      "Q_SETQUOTA = 0x800008",
                      "Q_XGETQUOTA = 0x005803"],
                     stroke=MUTED, head_fill=GREY_F)
    p.append(left)

    right, hr = panel(680, 175, 420, "тип рахунку",
                      ["USRQUOTA = 0",
                       "GRPQUOTA = 1",
                       "PRJQUOTA = 2"],
                      stroke=WARM, head_fill=WARM_F)
    p.append(right)

    res, hres = panel(350, 415, 540, "QCMD(підкоманда, тип)",
                      ["(підкоманда << 8) | (тип & 0xff)",
                       ("Q_GETQUOTA + GRPQUOTA → 0x80000701", "ok"),
                       ("Q_XGETQUOTA + PRJQUOTA → 0x00580302", "ok")],
                      stroke=FIELD, head_fill=GREEN_F)
    p.append(res)

    p.append(arrow(350, 175 + hl + 6, 545, 405, color=MUTED, sw=1.6))
    p.append(arrow(890, 175 + hr + 6, 695, 405, color=MUTED, sw=1.6))

    p.append(text(W / 2, 640,
                  "в одному числі зашиті дві різні речі: що робити і за чиїм рахунком",
                  size=14, color=MUTED))
    return render(os.path.join(IMG, 'qcmd-encoding.svg'), W, H, *p)


if __name__ == '__main__':
    fig_three_ledgers()
    fig_soft_hard_grace()
    fig_counter_and_journal()
    fig_qcmd_encoding()
    print("ok")
