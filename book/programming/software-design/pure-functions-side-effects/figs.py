# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Чиста проти нечистої: приховані канали ───────────────────────────────────
def fig_pure_vs_impure():
    W, H = 1040, 560
    frags = []

    # ── ЛІВА половина: ЧИСТА ──
    lcx = 250
    frags.append(text(lcx, 62, "Чиста функція", size=18, bold=True, color=FIELD))

    bw, bh = 190, 110
    bx, by = lcx - bw / 2, 235
    frags.append(rect(bx, by, bw, bh, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(lcx, by + bh / 2 + 11, "f", size=34, bold=True, color=FIELD))

    # єдиний вхід згори
    frags.append(text(lcx, 132, "аргументи", size=13, bold=True, color=INK))
    frags.append(arrow(lcx, 146, lcx, by - 6, color=INK, sw=2.4))

    # єдиний вихід знизу
    frags.append(arrow(lcx, by + bh + 6, lcx, by + bh + 60, color=INK, sw=2.4))
    frags.append(text(lcx, by + bh + 82, "значення", size=13, bold=True, color=INK))

    frags.append(text(lcx, H - 30, "один вхід · один вихід · усе видно",
                      size=12, color=FIELD, bold=True))

    # ── роздільник ──
    frags.append(line(W / 2, 46, W / 2, H - 46, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ПРАВА половина: НЕЧИСТА ──
    rcx = 790
    frags.append(text(rcx, 62, "Нечиста функція", size=18, bold=True, color=POS))

    bx2, by2 = rcx - bw / 2, 235
    frags.append(rect(bx2, by2, bw, bh, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(rcx, by2 + bh / 2 + 11, "f", size=34, bold=True, color=POS))

    # оголошений вхід згори
    frags.append(text(rcx, 132, "аргументи", size=13, bold=True, color=INK))
    frags.append(arrow(rcx, 146, rcx, by2 - 6, color=INK, sw=2.4))

    # оголошений вихід знизу
    frags.append(arrow(rcx, by2 + bh + 6, rcx, by2 + bh + 60, color=INK, sw=2.4))
    frags.append(text(rcx, by2 + bh + 82, "значення", size=13, bold=True, color=INK))

    # ПРИХОВАНІ входи зліва — коробки стоять у лівій колонці правої половини
    in_cx = 600
    ins = ["годинник", "глобальний стан", "файл"]
    for i, lab in enumerate(ins):
        yy = by2 + 14 + i * 36
        tb, tw, th = textbox(in_cx, yy, lab, size=11, pad=6,
                             fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        frags.append(tb)
        frags.append(arrow(in_cx + tw / 2 + 4, yy, bx2 - 4, yy, color=POS, sw=1.8))

    # ПРИХОВАНІ виходи справа — коробки стоять у правій колонці
    out_cx = 965
    outs = ["запис у лог", "мутація входу", "посилка в мережу"]
    for i, lab in enumerate(outs):
        yy = by2 + 14 + i * 36
        tb, tw, th = textbox(out_cx, yy, lab, size=11, pad=6,
                             fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        # спершу знаємо ширину — стрілка до лівого краю коробки
        frags.append(arrow(bx2 + bw + 4, yy, out_cx - tw / 2 - 4, yy, color=POS, sw=1.8))
        frags.append(tb)

    frags.append(text(rcx, H - 30, "приховані канали з боків — у сигнатурі їх не видно",
                      size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'pure-vs-impure.svg'), W, H, *frags,
           title="Що видно в сигнатурі, а що сховано збоку")


# ── Ефекти на край: чисте ядро в брудній оболонці ────────────────────────────
def fig_core_shell():
    W, H = 860, 620
    frags = []

    cx, cy = W / 2, 330

    # зовнішнє кільце — оболонка (брудна)
    frags.append(circle(cx, cy, 210, fill="#fdecea", stroke=POS, sw=2.0))
    # внутрішнє коло — ядро (чисте)
    frags.append(circle(cx, cy, 110, fill="#f2faf5", stroke=FIELD, sw=2.4))

    # підписи кілець (обидва в порожніх місцях)
    frags.append(text(cx, cy - 60, "ЧИСТЕ ЯДРО", size=15, bold=True, color=FIELD))
    frags.append(text(cx, cy - 40, "уся логіка й рішення", size=11, color=MUTED))
    frags.append(text(cx, cy + 40, "той самий вхід", size=11, color=FIELD))
    frags.append(text(cx, cy + 56, "→ той самий вихід", size=11, color=FIELD))

    frags.append(text(cx, cy - 178, "ІМПЕРАТИВНА ОБОЛОНКА (тонка)",
                      size=14, bold=True, color=POS))

    # ефекти — стрілки крізь оболонку до/від ядра, підписи ЗА межами великого кола
    # приносять дані (зліва, всередину)
    frags.append(arrow(cx - 300, cy - 40, cx - 116, cy - 24, color=POS, sw=2.0))
    tb, tw, th = textbox(cx - 300, cy - 66, "читання з БД", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)
    frags.append(arrow(cx - 300, cy + 40, cx - 116, cy + 24, color=POS, sw=2.0))
    tb, tw, th = textbox(cx - 300, cy + 66, "читання конфіга", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)

    # виносять ефекти (справа, назовні)
    frags.append(arrow(cx + 116, cy - 24, cx + 300, cy - 40, color=POS, sw=2.0))
    tb, tw, th = textbox(cx + 300, cy - 66, "запис у БД", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)
    frags.append(arrow(cx + 116, cy + 24, cx + 300, cy + 40, color=POS, sw=2.0))
    tb, tw, th = textbox(cx + 300, cy + 66, "вивід у лог", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)

    # нижній підпис-висновок
    cap, cw, ch = textbox(cx, H - 40,
                          "Бруд приносить дані в ядро й виносить його рішення — "
                          "рішень у ньому нема",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'core-shell.svg'), W, H, *frags,
           title="Ефекти — на край: чисте всередині, брудне зовні")


if __name__ == "__main__":
    fig_pure_vs_impure()
    fig_core_shell()
    print("figures written to", IMG)
