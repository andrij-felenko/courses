# -*- coding: utf-8 -*-
"""Фігури до теми «E-ink дисплей».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# локальні відтінки, що доповнюють палітру svgkit
WHITEP = "#f3f5f7"   # біла частинка
WHITEE = "#9aa6b2"   # обведення білої
BLACKP = "#1a1a1a"   # чорна частинка
FLUID  = "#dfe7ee"   # рідина в капсулі
GLASS  = "#5d7e93"   # прозорий електрод/скло
LAMP   = "#caa24a"   # світло (тепле)
LAMPF  = "#fff4c2"


def ray(x1, y1, x2, y2, color=LAMP, sw=2.0):
    """Промінь світла зі стрілкою на кінці (свій маркер у defs нижче)."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#aLamp)"/>' % (x1, y1, x2, y2, color, sw))


def particle(cx, cy, r, white):
    if white:
        return circle(cx, cy, r, fill=WHITEP, stroke=WHITEE, sw=1.0)
    return circle(cx, cy, r, fill=BLACKP, stroke=BLACKP, sw=1.0)


def capsule(cx, top, w, h, white_up):
    """Одна мікрокапсула в розрізі. white_up=True → білі частинки вгорі."""
    out = []
    left, right = cx - w / 2, cx + w / 2
    bot = top + h
    # прозорий верхній електрод (скло) — смужка над капсулою
    out.append(rect(left - 6, top - 20, w + 12, 14, fill="#eaf1f6", stroke=GLASS, sw=1.4, rx=3))
    out.append(text(cx, top - 9.5, "прозорий електрод", size=9.5, color=GLASS))
    # тіло капсули (овал)
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
               'stroke-width="1.8"/>' % (cx, (top + bot) / 2, w / 2, h / 2, FLUID, GLASS))
    # частинки: 7 білих + 7 чорних, розкладені вгорі/внизу за станом
    yr_up = top + h * 0.30
    yr_dn = bot - h * 0.30
    xs = [cx - w * 0.30, cx - w * 0.15, cx, cx + w * 0.15, cx + w * 0.30,
          cx - w * 0.22, cx + w * 0.22]
    y_white = yr_up if white_up else yr_dn
    y_black = yr_dn if white_up else yr_up
    for i, x in enumerate(xs):
        jw = (i % 2) * 3.0
        out.append(particle(x, y_white + jw, 6.5, white=True))
    for i, x in enumerate(xs):
        jb = (i % 2) * 3.0
        out.append(particle(x, y_black - jb, 5.0, white=False))
    # нижній електрод
    out.append(rect(left - 6, bot + 6, w + 12, 12, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=3))
    return "".join(out), (top + bot) / 2


def field_arrow(cx, y_from, y_to, label):
    """Вертикальна стрілка поля збоку від капсули + підпис."""
    return (line(cx, y_from, cx, y_to, color=FIELD, sw=2.6, dash="1")
            + '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6" '
              'marker-end="url(#aField)"/>' % (cx, (y_from + y_to) / 2 + 1, cx, y_to, FIELD)
            + text(cx, y_to + 16, label, size=10, color=FIELD, bold=True))


def fig_capsule():
    W, H = 760, 430
    f = [text(W / 2, 30, "Мікрокапсула e-ink: поле піднімає до ока білі або чорні частинки",
              size=16, bold=True)]

    cap_w, cap_h = 150, 150
    top = 120
    cxL, cxR = 210, 550

    # — ліва панель: білий стан —
    f.append(text(cxL, 66, "поле згори вниз → БІЛИЙ", size=12.5, bold=True))
    # промені світла, що падають і відбиваються
    f.append(ray(cxL - 70, 78, cxL - 24, top - 24))
    f.append(ray(cxL - 24, top - 24, cxL + 60, 80))
    body, mid = capsule(cxL, top, cap_w, cap_h, white_up=True)
    f.append(body)
    f.append(field_arrow(cxL + cap_w / 2 + 34, top, top + cap_h, "E"))
    f.append(text(cxL, top + cap_h + 50, "білі (+) угорі, відбивають світло", size=10.5, color=INK))
    f.append(text(cxL, top + cap_h + 67, "чорні (−) сховані на дні", size=10.5, color=MUTED))

    # — права панель: чорний стан —
    f.append(text(cxR, 66, "поле знизу вгору → ЧОРНИЙ", size=12.5, bold=True))
    f.append(ray(cxR - 70, 78, cxR - 24, top - 24))
    # відбитого променя нема — світло поглинається; покажемо «гасне»
    f.append(text(cxR + 40, 92, "світло поглинається", size=9.5, color=MUTED, anchor="start"))
    body, mid = capsule(cxR, top, cap_w, cap_h, white_up=False)
    f.append(body)
    f.append(field_arrow(cxR + cap_w / 2 + 34, top + cap_h, top, "E"))
    f.append(text(cxR, top + cap_h + 50, "чорні (−) угорі, поглинають світло", size=10.5, color=INK))
    f.append(text(cxR, top + cap_h + 67, "білі (+) сховані на дні", size=10.5, color=MUTED))

    # — нижній підпис про бістабільність —
    f.append(text(W / 2, H - 16,
                  "Прибрати поле — частинки лишаються на місці: цятка тримає колір без струму.",
                  size=11.5, color=INK, italic=True))

    # власні маркери (лампа-жовта, поле-зелене) додаємо в defs через прямий рядок
    extra_defs = (
        '<defs>'
        '<marker id="aLamp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '<marker id="aField" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '</defs>' % (LAMP, FIELD))

    render(os.path.join(IMG, 'capsule.svg'), W, H, extra_defs, *f)


if __name__ == "__main__":
    fig_capsule()
    print("OK: img/capsule.svg")
