# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Розворот стрілки: «природно» ліворуч → «інверсія» праворуч ────────────────
def fig_inversion():
    W, H = 1000, 560
    frags = []

    # роздільник між двома панелями
    frags.append(line(W / 2, 70, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: природний напрямок ──
    lcx = W / 4
    frags.append(text(lcx, 58, "Природно: стрілка тече вниз", size=15, bold=True))

    hi, hw, hh = textbox(lcx, 130, "Модуль високого рівня\n(бізнес-правило)",
                         size=13, bold=True, pad=14, fill="#eef4ff", stroke=INK, sw=1.8)
    frags.append(hi)
    lo, lw, lh = textbox(lcx, 400, "Конкретна деталь\n(база / мережа / пристрій)",
                         size=13, pad=14, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(lo)
    # стрілка залежності зверху вниз
    frags.append(arrow(lcx, 130 + hh / 2 + 6, lcx, 400 - lh / 2 - 6, color=POS, sw=2.6))
    lbl, _, _ = textbox(lcx + 96, 265, "залежить\nвід", size=11, pad=6,
                        fill="#ffffff", stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(lbl)
    frags.append(text(lcx, 470, "важливе прибите до дрібного",
                      size=12, bold=True, color=POS))

    # ── ПРАВА панель: інверсія ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 58, "Інверсія: обидві стрілки — до абстракції",
                      size=15, bold=True))

    hi2, hw2, hh2 = textbox(rcx, 130, "Модуль високого рівня\n(бізнес-правило)",
                            size=13, bold=True, pad=14, fill="#eef4ff", stroke=INK, sw=1.8)
    frags.append(hi2)
    ab, abw, abh = textbox(rcx, 265, "Абстракція\n(інтерфейс, мовою ядра)",
                           size=13, bold=True, pad=14, fill="#f2faf5", stroke=FIELD, sw=2.2)
    frags.append(ab)
    de, dew, deh = textbox(rcx, 400, "Конкретна деталь\n(реалізує інтерфейс)",
                           size=13, pad=14, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(de)

    # стрілка ядро → абстракція (вниз)
    frags.append(arrow(rcx, 130 + hh2 / 2 + 6, rcx, 265 - abh / 2 - 6, color=INK, sw=2.4))
    # стрілка деталь → абстракція (вгору!)
    frags.append(arrow(rcx, 400 - deh / 2 - 6, rcx, 265 + abh / 2 + 6, color=POS, sw=2.4))

    frags.append(text(rcx + 150, 197, "залежить від", size=11, bold=True, color=INK))
    frags.append(text(rcx + 150, 335, "реалізує", size=11, bold=True, color=POS))
    frags.append(text(rcx, 470, "деталь на кінці — замінна",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'inversion.svg'), W, H, *frags,
           title="Інверсія залежностей: розворот природного напрямку стрілки")


# ── Хто кого гукає: бібліотека (ти → неї) проти каркаса (він → тебе) ──────────
def fig_hollywood():
    W, H = 1020, 470
    frags = []

    # роздільник між двома панелями
    frags.append(line(W / 2, 74, W / 2, H - 34, color="#d0d5db", sw=1.2, dash="5,5"))

    top_y, bot_y = 150, 350   # центри верхнього й нижнього блоків

    # ── ЛІВА панель: БІБЛІОТЕКА ──
    lcx = W / 4
    frags.append(text(lcx, 56, "Бібліотека: керування лишається в тебе",
                      size=15, bold=True))

    ta, taw, tah = textbox(lcx, top_y, "Твій код\n(головний хід)",
                           size=13, bold=True, pad=15, fill="#eef4ff",
                           stroke=INK, sw=1.9, min_w=210)
    frags.append(ta)
    ba, baw, bah = textbox(lcx, bot_y, "Бібліотека\n(набір функцій)",
                           size=13, pad=15, fill="#f2faf5",
                           stroke=FIELD, sw=1.9, min_w=210)
    frags.append(ba)

    off = 46   # рознесення двох зустрічних стрілок по горизонталі
    # ти ГУКАЄШ бібліотеку (вниз, ліворуч від центру)
    frags.append(arrow(lcx - off, top_y + tah / 2 + 6,
                       lcx - off, bot_y - bah / 2 - 6, color=INK, sw=2.4))
    # бібліотека ПОВЕРТАЄ керування (вгору, праворуч від центру)
    frags.append(arrow(lcx + off, bot_y - bah / 2 - 6,
                       lcx + off, top_y + tah / 2 + 6, color=FIELD, sw=2.4))

    l1, _, _ = textbox(lcx - off - 66, (top_y + bot_y) / 2, "ти\nгукаєш",
                       size=11, pad=6, fill="#ffffff", stroke=INK, sw=1.1,
                       color=INK, bold=True)
    frags.append(l1)
    l2, _, _ = textbox(lcx + off + 74, (top_y + bot_y) / 2, "керування\nназад",
                       size=11, pad=6, fill="#ffffff", stroke=FIELD, sw=1.1,
                       color=FIELD, bold=True)
    frags.append(l2)

    # ── ПРАВА панель: КАРКАС ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 56, "Каркас: керування тримає він",
                      size=15, bold=True))

    fr, frw, frh = textbox(rcx, top_y, "Каркас\n(головний хід)",
                           size=13, bold=True, pad=15, fill="#f2faf5",
                           stroke=FIELD, sw=1.9, min_w=210)
    frags.append(fr)
    yc, ycw, ych = textbox(rcx, bot_y, "Твій обробник\n(вставлено збоку)",
                           size=13, pad=15, fill="#eef4ff",
                           stroke=INK, sw=1.9, min_w=210)
    frags.append(yc)

    # каркас ГУКАЄ твій код (вниз, ліворуч від центру)
    frags.append(arrow(rcx - off, top_y + frh / 2 + 6,
                       rcx - off, bot_y - ych / 2 - 6, color=POS, sw=2.6))
    # твій обробник ВІДПРАЦЮВАВ — керування назад каркасу (вгору, праворуч)
    frags.append(arrow(rcx + off, bot_y - ych / 2 - 6,
                       rcx + off, top_y + frh / 2 + 6, color=INK, sw=2.2))

    r1, _, _ = textbox(rcx - off - 84, (top_y + bot_y) / 2, "він гукає\nтебе",
                       size=11, pad=6, fill="#ffffff", stroke=POS, sw=1.1,
                       color=POS, bold=True)
    frags.append(r1)
    r2, _, _ = textbox(rcx + off + 66, (top_y + bot_y) / 2, "керування\nназад",
                       size=11, pad=6, fill="#ffffff", stroke=INK, sw=1.1,
                       color=INK, bold=True)
    frags.append(r2)

    frags.append(text(rcx, H - 16, "«не дзвоніть нам — ми подзвонимо вам»",
                      size=12, bold=True, italic=True, color=POS))

    render(os.path.join(IMG, 'hollywood.svg'), W, H, *frags,
           title="Інверсія керування: хто кого гукає в часі виконання")


if __name__ == "__main__":
    fig_inversion()
    fig_hollywood()
    print("figures written to", IMG)
