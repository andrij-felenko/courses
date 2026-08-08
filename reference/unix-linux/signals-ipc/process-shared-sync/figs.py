# -*- coding: utf-8 -*-
"""Фігури до теми «Синхронізація між процесами: POSIX-семафори й спільні м'ютекси»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_futex_key():
    """Чому потрібен атрибут pshared: приватний ключ рахується від адреси, спільний — від сторінки."""
    W, H = 980, 600
    f = []

    # ── верхній ряд: два адресні простори й одна фізична сторінка ──
    f.append(text(150, 46, "Процес A", size=15, bold=True))
    f.append(rect(50, 62, 200, 210, fill="#ffffff"))
    f.append(text(150, 258, "адресний простір A", size=12, color=MUTED))

    f.append(text(830, 46, "Процес B", size=15, bold=True))
    f.append(rect(730, 62, 200, 210, fill="#ffffff"))
    f.append(text(830, 258, "адресний простір B", size=12, color=MUTED))

    b, bw, bh = textbox(150, 110, "замок @ 0x7f2a1000", size=13,
                        fill="#eaf0fd", stroke=NEG, min_w=176)
    f.append(b)
    b, bw2, bh2 = textbox(830, 210, "замок @ 0x55c17000", size=13,
                          fill="#eaf0fd", stroke=NEG, min_w=176)
    f.append(b)

    pb, pw, ph = textbox(490, 160, ["одна фізична", "сторінка"], size=14,
                         fill="#eafaf0", stroke=FIELD, bold=True, min_w=180)
    f.append(pb)

    f.append(arrow(150 + bw / 2, 112, 490 - pw / 2 - 6, 148))
    f.append(arrow(830 - bw2 / 2, 208, 490 + pw / 2 + 6, 175))

    # ── нижній ряд: дві схеми ключа ──
    f.append(rect(50, 330, 400, 210, fill="#fdf6f5", stroke=POS))
    f.append(text(250, 362, "Приватний ключ", size=15, bold=True, color=POS))
    f.append(text(250, 388, "(адресний простір, адреса)", size=13, color=MUTED))
    f.append(text(250, 424, "A  →  (mm_A, 0x7f2a1000)", size=13))
    f.append(text(250, 452, "B  →  (mm_B, 0x55c17000)", size=13))
    f.append(line(80, 472, 420, 472, color=POS, sw=1.2, dash="5,4"))
    f.append(text(250, 500, "дві різні черги:", size=13, color=POS, bold=True))
    f.append(text(250, 522, "пробудження не доходить", size=13, color=POS, bold=True))

    f.append(rect(530, 330, 400, 210, fill="#f2fbf6", stroke=FIELD))
    f.append(text(730, 362, "Спільний ключ", size=15, bold=True, color=FIELD))
    f.append(text(730, 388, "(сторінка, зсув у ній)", size=13, color=MUTED))
    f.append(text(730, 424, "A  →  (сторінка, +0x40)", size=13))
    f.append(text(730, 452, "B  →  (сторінка, +0x40)", size=13))
    f.append(line(560, 472, 900, 472, color=FIELD, sw=1.2, dash="5,4"))
    f.append(text(730, 500, "одна черга на обох:", size=13, color=FIELD, bold=True))
    f.append(text(730, 522, "PTHREAD_PROCESS_SHARED", size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, 'futex-key.svg'), W, H, *f,
           title="Приватний і спільний ключ черги очікування")


def fig_robust_states():
    """Життєвий шлях живучого м'ютекса після смерті власника."""
    W, H = 1000, 500
    f = []

    free_x, free_y = 130, 90
    held_x, held_y = 380, 90
    dead_x, dead_y = 720, 90
    eod_x, eod_y = 720, 250
    cons_x, cons_y = 380, 250
    nrec_x, nrec_y = 720, 400

    b, w_free, h_free = textbox(free_x, free_y, "вільний", size=14, bold=True,
                                fill="#f2fbf6", stroke=FIELD, min_w=140)
    f.append(b)
    b, w_held, h_held = textbox(held_x, held_y, "захоплений", size=14, min_w=150)
    f.append(b)
    b, w_dead, h_dead = textbox(dead_x, dead_y, ["слово позначене", "FUTEX_OWNER_DIED"],
                                size=13, fill="#fdf6f5", stroke=POS, min_w=210)
    f.append(b)
    b, w_eod, h_eod = textbox(eod_x, eod_y, ["lock повертає", "EOWNERDEAD"],
                              size=13, fill="#fdf6f5", stroke=POS, bold=True, min_w=210)
    f.append(b)
    b, w_cons, h_cons = textbox(cons_x, cons_y, ["стан полагоджено:", "pthread_mutex_consistent()"],
                                size=13, fill="#f2fbf6", stroke=FIELD, min_w=250)
    f.append(b)
    b, w_nrec, h_nrec = textbox(nrec_x, nrec_y, ["ENOTRECOVERABLE:", "лишається тільки destroy"],
                                size=13, fill="#fdf6f5", stroke=POS, bold=True, min_w=250)
    f.append(b)

    # вільний → захоплений
    f.append(arrow(free_x + w_free / 2, free_y, held_x - w_held / 2 - 4, free_y))
    f.append(text((free_x + w_free / 2 + held_x - w_held / 2) / 2, free_y - 18,
                  "lock", size=13, color=MUTED))

    # захоплений → мертве слово
    f.append(arrow(held_x + w_held / 2, held_y, dead_x - w_dead / 2 - 4, held_y))
    f.append(text((held_x + w_held / 2 + dead_x - w_dead / 2) / 2, held_y - 34,
                  "власник помер;", size=13, color=POS))
    f.append(text((held_x + w_held / 2 + dead_x - w_dead / 2) / 2, held_y - 14,
                  "ядро проходить робустний список", size=13, color=POS))

    # мертве слово → EOWNERDEAD
    f.append(arrow(dead_x, dead_y + h_dead / 2, eod_x, eod_y - h_eod / 2 - 4))
    f.append(text(dead_x + 24, (dead_y + h_dead / 2 + eod_y - h_eod / 2) / 2 + 5,
                  "наступний lock", size=13, color=MUTED, anchor="start"))

    # EOWNERDEAD → полагоджено
    f.append(arrow(eod_x - w_eod / 2, eod_y, cons_x + w_cons / 2 + 4, eod_y))
    f.append(text((eod_x - w_eod / 2 + cons_x + w_cons / 2) / 2, eod_y - 18,
                  "код відновлення", size=13, color=FIELD))

    # полагоджено → вільний
    f.append(line(cons_x - w_cons / 2, cons_y, free_x, cons_y))
    f.append(arrow(free_x, cons_y, free_x, free_y + h_free / 2 + 4))
    f.append(text(free_x + 96, cons_y + 28, "unlock — і замок звичайний",
                  size=13, color=FIELD))

    # EOWNERDEAD → ENOTRECOVERABLE
    f.append(arrow(eod_x, eod_y + h_eod / 2, nrec_x, nrec_y - h_nrec / 2 - 4))
    f.append(text(nrec_x + 24, (eod_y + h_eod / 2 + nrec_y - h_nrec / 2) / 2 + 5,
                  "unlock без підтвердження", size=13, color=POS, anchor="start"))

    render(os.path.join(OUT, 'robust-states.svg'), W, H, *f,
           title="Стани живучого м'ютекса після смерті власника")


def fig_death_compare():
    """Що дає володіння: м'ютекс віддається наступному, семафор мовчки втрачає дозвіл."""
    W, H = 980, 470
    f = []

    def panel(x0, title, color, steps):
        out = [rect(x0, 50, 420, 380, fill="#ffffff", stroke=color, sw=2)]
        out.append(text(x0 + 210, 82, title, size=15, bold=True, color=color))
        cx = x0 + 210
        ys = [128, 200, 272, 358]
        boxes = []
        for i, (txt, fill, stroke, bold) in enumerate(steps):
            b, bw, bh = textbox(cx, ys[i], txt, size=13, fill=fill, stroke=stroke,
                                bold=bold, min_w=300)
            out.append(b)
            boxes.append((ys[i], bh))
        for i in range(len(boxes) - 1):
            y1 = boxes[i][0] + boxes[i][1] / 2
            y2 = boxes[i + 1][0] - boxes[i + 1][1] / 2 - 4
            out.append(arrow(cx, y1, cx, y2))
        return out

    f += panel(40, "М'ютекс: власник є", FIELD, [
        ("A захопив замок", FILL, LINE, False),
        ("A вбито посеред зміни", "#fdf6f5", POS, False),
        (["ядро ставить у слові", "FUTEX_OWNER_DIED"], "#fdf6f5", POS, False),
        (["B: lock → EOWNERDEAD", "стан можна полагодити"], "#f2fbf6", FIELD, True),
    ])

    f += panel(520, "Семафор: власника немає", POS, [
        ("A зробив sem_wait: 1 → 0", FILL, LINE, False),
        ("A вбито посеред зміни", "#fdf6f5", POS, False),
        (["лічильник лишився 0;", "ядро не має кого позначити"], "#fdf6f5", POS, False),
        (["B: sem_wait спить вічно,", "коду помилки немає"], "#fdf6f5", POS, True),
    ])

    render(os.path.join(OUT, 'death-compare.svg'), W, H, *f,
           title="Смерть власника: м'ютекс проти семафора")


def fig_recovery_windows():
    """Вікна смерті під час укладання запису й вирок відновлювача для кожного."""
    W, H = 1060, 580
    f = []

    f.append(text(230, 38, "Кроки вкладання (усе під замком)", size=15, bold=True))
    f.append(text(780, 38, "Що бачить відновлювач", size=15, bold=True))

    steps = [
        (80,  "1 · намір: op = PUSH, index = T"),
        (160, "2 · slot.gen++  →  непарне"),
        (240, "3 · копіюємо дані в слот"),
        (320, "4 · slot.gen++  →  парне"),
        (400, "5 · tail = T + 1   (публікація)"),
        (480, "6 · op = NONE"),
    ]
    for y, s in steps:
        b, _, _ = textbox(230, y, s, size=13, min_w=360)
        f.append(b)

    verdicts = [
        (110, FIELD, "#f2fbf6", ["помер до кроку 2:",
                                 "gen парне, tail == T",
                                 "→ нічого не сталося, знімаємо намір"]),
        (250, POS,   "#fdf6f5", ["помер на кроці 3:",
                                 "gen НЕПАРНЕ — дані рвані",
                                 "→ ВІДКІТ: gen++, tail лишається T"]),
        (390, NEG,   "#eaf0fd", ["помер після кроку 4:",
                                 "gen парне, tail == T",
                                 "→ ДОКОЧУВАННЯ: tail = T + 1"]),
        (500, FIELD, "#f2fbf6", ["помер після кроку 5:",
                                 "tail == T + 1 — уже опубліковано",
                                 "→ знімаємо намір"]),
    ]
    for y, col, bg, lines in verdicts:
        b, _, _ = textbox(780, y, lines, size=12, fill=bg, stroke=col, min_w=430)
        f.append(b)

    for (sy, vy) in ((80, 110), (240, 250), (330, 390), (412, 500)):
        f.append(line(412, sy, 563, vy, color=MUTED, sw=1.1, dash="4,4"))

    render(os.path.join(OUT, 'recovery-windows.svg'), W, H, *f,
           title="Вікна смерті виробника й вирок відновлювача")


if __name__ == '__main__':
    fig_futex_key()
    fig_robust_states()
    fig_death_compare()
    fig_recovery_windows()
    print("ok:", os.listdir(OUT))
