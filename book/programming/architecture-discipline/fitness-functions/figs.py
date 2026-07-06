# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_rule_vs_gate():
    """Ліва панель: правило на діаграмі — зміна проходить наскрізь.
       Права панель: правило як фітнес-функція — ворота зупиняють порушення."""
    W, H = 860, 400
    frags = []

    # ── ліва панель ────────────────────────────────────────────
    lx = 40
    frags.append(text(lx + 170, 56, "Правило лише на діаграмі", size=16, bold=True))
    # діаграма-малюнок
    b, w, h = textbox(lx + 170, 150, "домен → репозиторій → база\n(намальоване правило)",
                      size=13, fill="#eef2f7", stroke=MUTED)
    frags.append(b)
    # зміна-порушник входить і проходить наскрізь
    frags.append(text(lx + 170, 235, "зміна-порушник", size=12, color=POS, bold=True))
    frags.append(arrow(lx + 170, 250, lx + 170, 320, color=POS, sw=2.2))
    b, w, h = textbox(lx + 170, 350, "проходить вільно", size=13,
                      fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(b)

    # розділювач
    frags.append(line(W / 2, 80, W / 2, H - 30, color=MUTED, sw=1.2, dash="5,5"))

    # ── права панель ───────────────────────────────────────────
    rx = 490
    frags.append(text(rx + 170, 56, "Правило як фітнес-функція", size=16, bold=True))
    frags.append(text(rx + 170, 110, "зміна-порушник", size=12, color=POS, bold=True))
    frags.append(arrow(rx + 170, 124, rx + 170, 168, color=POS, sw=2.2))
    # ворота автоперевірки
    b, w, h = textbox(rx + 170, 200, "автоперевірка у складанні\n(fitness function)",
                      size=13, fill=FILL, stroke=INK, bold=True)
    frags.append(b)
    # блок: не проходить
    frags.append(text(rx + 170, 262, "×", size=26, color=POS, bold=True))
    frags.append(arrow(rx + 170, 278, rx + 170, 320, color=INK, sw=2.2))
    b, w, h = textbox(rx + 170, 350, "складання падає", size=13,
                      fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'rule-vs-gate.svg'), W, H, *frags)


def fig_axes():
    """Три незалежні осі фітнес-функцій; унизу — приклад, розкладений за ними."""
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 34, "Три осі, за якими різняться фітнес-функції", size=17, bold=True))

    ax_x = 90            # ліва межа підписів осей
    end_x = W - 60
    ys = [110, 185, 260]
    labels = ["Обсяг", "Ритм", "Результат"]
    left_pole = ["атомарна\n(одна властивість)",
                 "запускана\n(на подію)",
                 "статична\n(фіксований поріг)"]
    right_pole = ["цілісна\n(поєднання властивостей)",
                  "неперервна\n(на живій системі)",
                  "динамічна\n(поріг за контекстом)"]

    for y, lab, lp, rp in zip(ys, labels, left_pole, right_pole):
        frags.append(text(50, y + 5, lab, size=14, bold=True, anchor="start"))
        # вісь
        frags.append(line(ax_x + 130, y, end_x - 130, y, color=MUTED, sw=1.4))
        # ліва рамка
        b, w, h = textbox(ax_x + 95, y, lp, size=12, fill="#eaf0fd", stroke=NEG)
        frags.append(b)
        # права рамка
        b, w, h = textbox(end_x - 95, y, rp, size=12, fill="#fdecea", stroke=POS)
        frags.append(b)

    # приклад унизу
    frags.append(line(60, 320, W - 60, 320, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(text(W / 2, 352, "Приклад: «95-й перцентиль часу відповіді під бюджетом»",
                      size=14, bold=True))
    b, w, h = textbox(W / 2, 415, "цілісна  ·  неперервна  ·  статична або динамічна",
                      size=13, fill="#eafaf0", stroke=FIELD, bold=True)
    frags.append(b)

    render(os.path.join(IMG, 'axes.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_rule_vs_gate()
    fig_axes()
    print("figs done")
