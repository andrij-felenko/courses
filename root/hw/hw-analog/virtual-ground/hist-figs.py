# -*- coding: utf-8 -*-
"""Фігура до історичної вставки «Народження віртуальної землі»
(book/electronics/analog/virtual-ground/hist-virtual-ground.md).

Одна фігура — родовід вузла-нуля:
  birth-of-node.svg — як «нуль на вході» проходить крізь чотири моменти
                      (Блек 1934/37 · Сворцел 1941/46 · Раджаззіні 1947 · K2-W 1953)
                      і з прийому розрахунку стає наріжним поняттям.

Запуск:  python hist-figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def node_dot(cx, cy, r=7):
    """Жирна точка-вузол із тонким ореолом — «той самий нуль»."""
    return (circle(cx, cy, r + 4, fill="none", stroke=NEG, sw=1.2) +
            circle(cx, cy, r, fill=NEG, stroke=NEG, sw=1.5))


def birth_of_node():
    W, H = 920, 470
    out = []
    out.append(text(W / 2, 30, "Родовід вузла-нуля: той самий вхідний нуль крізь чотири моменти",
                    size=17, bold=True))

    # Наскрізна лінія часу — той самий вузол мандрує зліва направо.
    yline = 150
    x0, x1 = 70, W - 70
    out.append(line(x0, yline, x1, yline, color=MUTED, sw=2))
    out.append(arrow(x1 - 2, yline, x1 + 16, yline, color=MUTED, sw=2))
    out.append(text(x1 + 8, yline - 12, "час", size=12, color=MUTED, anchor="start"))

    # Чотири віхи: (x, рік, хто, що сталося з вузлом)
    cols = [
        (190, "1934 · 1937",
         ["Гарольд Блек", "(Harold Black)", "Bell Labs"],
         ["від'ємний", "зворотний зв'язок:", "велике підсилення", "притискає різницю", "входів до нуля"],
         "ПРИНЦИП", FIELD),
        (400, "1941 · 1946",
         ["Карл Сворцел", "(Karl Swartzel)", "Bell Labs · M-9"],
         ["суматор: вхідний", "вузол стає", "спільною точкою,", "де сходяться", "струми доданків"],
         "ВУЗОЛ", NEG),
        (610, "1947",
         ["Раджаззіні й ін.", "(Ragazzini)", "Columbia"],
         ["назва «operational", "amplifier»: нуль —", "робоче припущення", "для суматорів", "та інтеграторів"],
         "ПРИЙОМ", NEG),
        (810, "1952 · 1953",
         ["GAP/R", "(G. Philbrick)", "K2-W"],
         ["серійна цеглинка:", "нуль на вході —", "наріжне поняття", "всієї аналогової", "схемотехніки"],
         "ПОНЯТТЯ", POS),
    ]

    for x, yr, who, what, tag, tagc in cols:
        # вузол на лінії часу
        out.append(node_dot(x, yline))
        # рік над лінією
        out.append(text(x, yline - 30, yr, size=13, bold=True))
        # хто — трохи нижче року
        out.append(mtext(x, yline - 70, who[:1], size=12, bold=True))
        out.append(mtext(x, yline - 70 + 16, who[1:], size=11, color=MUTED))
        # тег-стадія під вузлом
        bx, bw, bh = textbox(x, yline + 34, tag, size=12, bold=True,
                             fill="#ffffff", stroke=tagc, sw=2, min_w=86)
        out.append(bx)
        # опис унизу — у фіксованій рамці, шрифт сам влізе
        out.append(fitbox(x - 92, yline + 66, 184, 116, "\n".join(what),
                          size=12, fill=FILL, stroke=tagc, sw=1.3))

    # підсумковий рядок: стрілка-«перетворення» від прийому до поняття
    out.append(text(W / 2, H - 16,
                    "один і той самий вузол: спершу зручне припущення інтеграторів і суматорів — згодом окреме поняття",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "birth-of-node.svg"), W, H, *out)


if __name__ == "__main__":
    birth_of_node()
    print("OK hist figs ->", IMG)
