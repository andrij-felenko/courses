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
GREY_FILL = "#f0f0f2"


# ── 1. Три рівні: номер — опис — inode ───────────────────────────────────────
def fig_three_levels():
    W, H = 1180, 600
    p = []

    TX, TW, RH = 40, 200, 36           # таблиці дескрипторів
    DX, DW, DH = 470, 280, 86          # описи відкритого файлу
    IX, IW, IH = 920, 220, 86          # inode

    p.append(text(TX + TW / 2, 56, "таблиця дескрипторів", size=13, bold=True, color=MUTED))
    p.append(text(DX + DW / 2, 56, "опис відкритого файлу", size=13, bold=True, color=MUTED))
    p.append(text(IX + IW / 2, 56, "inode", size=13, bold=True, color=MUTED))

    def table(y0, label, rows):
        out = [text(TX + TW / 2, y0 - 14, label, size=14, bold=True)]
        for i, (txt, hue, fillc) in enumerate(rows):
            y = y0 + i * RH
            out.append(fitbox(TX, y, TW, RH - 4, [txt], size=12.5,
                              fill=fillc, stroke=hue, sw=1.5, rx=5,
                              color=MUTED if hue is MUTED else INK))
        return out

    yA, yB = 96, 356
    p += table(yA, "процес A", [
        ("0, 1, 2 → термінал", MUTED, GREY_FILL),
        ("fd 3", FIELD, GREEN_FILL),
        ("fd 4", FIELD, GREEN_FILL),
        ("fd 5", WARM, WARM_FILL),
    ])
    p += table(yB, "процес B (нащадок A)", [
        ("0, 1, 2 → термінал", MUTED, GREY_FILL),
        ("fd 3", NEG, BLUE_FILL),
        ("fd 4 — вільний", MUTED, GREY_FILL),
        ("fd 5", WARM, WARM_FILL),
    ])

    descs = [
        (96, ["опис 1", "позиція 8192 · O_RDONLY"], FIELD, GREEN_FILL),
        (300, ["опис 2", "позиція 0 · O_RDONLY"], NEG, BLUE_FILL),
        (452, ["опис 3", "позиція 512 · O_WRONLY"], WARM, WARM_FILL),
    ]
    for y, lines, hue, fillc in descs:
        p.append(fitbox(DX, y, DW, DH, lines, size=13, fill=fillc, stroke=hue, sw=1.8, rx=9))

    inodes = [
        (150, ["inode", "/etc/hostname"], LINE, FILL),
        (452, ["inode", "/var/log/app"], LINE, FILL),
    ]
    for y, lines, hue, fillc in inodes:
        p.append(fitbox(IX, y, IW, IH, lines, size=13, fill=fillc, stroke=hue, sw=1.8, rx=9))

    # номер → опис
    links = [
        (yA + 1 * RH + (RH - 4) / 2, 96 + 30, FIELD),
        (yA + 2 * RH + (RH - 4) / 2, 96 + 58, FIELD),
        (yA + 3 * RH + (RH - 4) / 2, 452 + 28, WARM),
        (yB + 1 * RH + (RH - 4) / 2, 300 + 43, NEG),
        (yB + 3 * RH + (RH - 4) / 2, 452 + 58, WARM),
    ]
    for y1, y2, hue in links:
        p.append(arrow(TX + TW + 6, y1, DX - 6, y2, color=hue))

    # опис → inode
    for y1, y2, hue in [(139, 180, FIELD), (343, 208, NEG), (495, 495, WARM)]:
        p.append(arrow(DX + DW + 6, y1, IX - 6, y2, color=hue))

    p.append(text(W / 2, 578,
                  "спільними бувають опис і inode — але ніколи сам номер",
                  size=14, bold=True, color=MUTED))

    render(os.path.join(IMG, 'three-levels.svg'), W, H, *p)


# ── 2. Перенаправлення: чотири правки в таблиці до exec ──────────────────────
def fig_redirect_steps():
    W, H = 1200, 470
    p = []

    TERM = ("термінал", LINE, FILL)
    FILEO = ("out.txt", FIELD, GREEN_FILL)
    FREE = ("вільний", MUTED, GREY_FILL)

    panels = [
        ("1 · після fork", [TERM, TERM, TERM, FREE],
         ["таблиця — точна копія", "батьківської"]),
        ("2 · open(\"out.txt\")", [TERM, TERM, TERM, FILEO],
         ["правило найменшого", "вільного дало номер 3"]),
        ("3 · dup2(3, 1)", [TERM, FILEO, TERM, FILEO],
         ["запис 1 переставлено", "на той самий опис"]),
        ("4 · close(3)", [TERM, FILEO, TERM, FREE],
         ["номер 3 звільнено;", "лишилося викликати exec"]),
    ]

    for k, (title, rows, note) in enumerate(panels):
        px = 25 + k * 293
        p.append(text(px + 135, 72, title, size=14.5, bold=True))
        for i, (tgt, hue, fillc) in enumerate(rows):
            y = 106 + i * 48
            hot = (tgt == "out.txt")
            p.append(fitbox(px, y, 62, 40, ["fd %d" % i], size=13, bold=hot,
                            fill=fillc if hot else FILL,
                            stroke=hue if hot else LINE, sw=1.7 if hot else 1.3, rx=6))
            if tgt == "вільний":
                p.append(text(px + 100, y + 25, "·  ·  ·", size=13, color=MUTED))
            else:
                p.append(arrow(px + 70, y + 20, px + 108, y + 20, color=hue))
            p.append(fitbox(px + 114, y, 156, 40, [tgt], size=12.5,
                            fill=fillc, stroke=hue, sw=1.7 if hot else 1.3, rx=6,
                            color=MUTED if hue is MUTED else INK))
        p.append(mtext(px + 135, 332, note, size=12.5, color=MUTED))

    for k in range(3):
        p.append(line(25 + k * 293 + 278, 96, 25 + k * 293 + 278, 300,
                      color=MUTED, sw=1.1, dash="4 5"))

    p.append(text(W / 2, 424,
                  "усі чотири правки зроблено до exec — програма прокидається "
                  "з уже готовою таблицею",
                  size=14, bold=True, color=MUTED))

    render(os.path.join(IMG, 'redirect-steps.svg'), W, H, *p)


# ── 3. Перевикористання номера: тиха біда ────────────────────────────────────
def fig_reuse_hazard():
    W, H = 1200, 460
    p = []

    BW = 520
    ROWY = [130, 190, 250]

    def block(x0, title, hue, rows, verdict, vhue, vfill):
        out = [text(x0 + BW / 2, 74, title, size=15, bold=True, color=hue)]
        out.append(text(x0 + 130, 112, "потік A", size=13, bold=True, color=MUTED))
        out.append(text(x0 + 390, 112, "потік B", size=13, bold=True, color=MUTED))
        for y, (a, b, ahue, afill, bhue, bfill) in zip(ROWY, rows):
            for cx, cell, chue, cfill in ((x0 + 10, a, ahue, afill),
                                          (x0 + 270, b, bhue, bfill)):
                if cell is None:
                    out.append(text(cx + 120, y + 30, "—", size=15, color=MUTED))
                else:
                    out.append(fitbox(cx, y, 240, 46, [cell], size=13,
                                      fill=cfill, stroke=chue, sw=1.6, rx=7,
                                      color=MUTED if chue is MUTED else INK))
        out.append(fitbox(x0, 322, BW, 62, verdict, size=13.5, bold=True,
                          fill=vfill, stroke=vhue, sw=2, rx=10))
        # вісь часу
        out.append(text(x0 - 20, 116, "час", size=12, color=MUTED))
        out.append(arrow(x0 - 20, 132, x0 - 20, 288, color=MUTED, sw=1.4))
        return out

    p += block(70, "як буває", POS, [
        ("close(7)", None, POS, RED_FILL, MUTED, GREY_FILL),
        (None, "open(…) → 7", MUTED, GREY_FILL, NEG, BLUE_FILL),
        ("write(7, …)", None, POS, RED_FILL, MUTED, GREY_FILL),
    ], ["write повернув успіх:", "байти лягли у файл, який відкрив потік B"],
        POS, RED_FILL)

    p += block(650, "як треба", FIELD, [
        ("close(fd); fd = −1", None, FIELD, GREEN_FILL, MUTED, GREY_FILL),
        (None, "open(…) → 7", MUTED, GREY_FILL, NEG, BLUE_FILL),
        ("write(fd, …)", None, FIELD, GREEN_FILL, MUTED, GREY_FILL),
    ], ["fd == −1 → EBADF:", "помилка спіймана, чужого файлу не зачеплено"],
        FIELD, GREEN_FILL)

    p.append(line(600, 90, 600, 390, color=MUTED, sw=1.2, dash="5 5"))
    p.append(text(W / 2, 432,
                  "закритий номер не стає недійсним — він стає вільним, "
                  "і його негайно забирає наступний open",
                  size=14, bold=True, color=MUTED))

    render(os.path.join(IMG, 'reuse-hazard.svg'), W, H, *p)


# ── 4. Порядок кроків усередині close() ──────────────────────────────────────
def fig_close_order():
    W, H = 1280, 470
    p = []

    BX, BW, GAP = 50, 262, 44
    xs = [BX + k * (BW + GAP) for k in range(4)]
    BY, BH = 150, 112

    p.append(text(W / 2, 40, "close(fd): порядок кроків усередині виклику",
                  size=16, bold=True))

    p.append(fitbox(BX, 86, BW * 4 + GAP * 3, 42,
                    ["з цієї миті номер вільний — його негайно забирає "
                     "наступний open у цьому процесі"],
                    size=13, fill=RED_FILL, stroke=POS, sw=1.6, rx=8, color=POS))

    steps = [
        (["1 · номер вилучено", "з таблиці процесу"], POS, RED_FILL),
        (["2 · лічильник посилань", "на опис −1"], MUTED, GREY_FILL),
        (["3 · якщо став 0:", "скинути дані,", "звільнити опис"], WARM, WARM_FILL),
        (["4 · повернути", "0 або −1"], FIELD, GREEN_FILL),
    ]
    for x, (lines, hue, fillc) in zip(xs, steps):
        p.append(fitbox(x, BY, BW, BH, lines, size=13.5,
                        fill=fillc, stroke=hue, sw=1.8, rx=9))

    for k in range(3):
        p.append(arrow(xs[k] + BW + 5, BY + BH / 2, xs[k + 1] - 5, BY + BH / 2,
                       color=MUTED))

    notes = [
        (xs[0], ["EBADF — номера", "в таблиці не було;", "решти кроків немає"], POS, RED_FILL),
        (xs[2], ["EIO, ENOSPC, EINTR —", "номер уже втрачено,", "повторювати нічого"], WARM, WARM_FILL),
    ]
    for x, lines, hue, fillc in notes:
        p.append(line(x + BW / 2, BY + BH + 6, x + BW / 2, 282,
                      color=hue, sw=1.2, dash="4 4"))
        p.append(fitbox(x, 288, BW, 84, lines, size=12.5,
                        fill=fillc, stroke=hue, sw=1.4, rx=8))

    p.append(text(W / 2, 428,
                  "код помилки приходить, коли номера вже нема — "
                  "тому fsync() роблять ДО close()",
                  size=14, bold=True, color=MUTED))

    render(os.path.join(IMG, 'close-order.svg'), W, H, *p)


if __name__ == '__main__':
    fig_three_levels()
    fig_redirect_steps()
    fig_reuse_hazard()
    fig_close_order()
    print("ok:", sorted(os.listdir(IMG)))
