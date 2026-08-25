# -*- coding: utf-8 -*-
"""Фігури до теми «Розв'язувальний конденсатор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def cap(cx, cy, w=18, gap=6, sw=2.6, color=INK):
    """Символ конденсатора (дві планки) із центром (cx,cy), вертикальні виводи."""
    return (line(cx - w / 2, cy - gap / 2, cx + w / 2, cy - gap / 2, color=color, sw=sw) +
            line(cx - w / 2, cy + gap / 2, cx + w / 2, cy + gap / 2, color=color, sw=sw))


def gnd(cx, cy, color=INK):
    """Символ землі під точкою (cx, cy)."""
    return (line(cx - 11, cy, cx + 11, cy, color=color, sw=2.4) +
            line(cx - 7, cy + 5, cx + 7, cy + 5, color=color, sw=2.4) +
            line(cx - 3, cy + 10, cx + 3, cy + 10, color=color, sw=2.4))


def head(cx, cy, ang_deg, color, size=8):
    """Трикутна стрілка-вістря в точці (cx,cy), напрям ang_deg (град, 0 = вправо)."""
    import math
    a = math.radians(ang_deg)
    bx, by = math.cos(a), math.sin(a)
    px, py = -by, bx  # перпендикуляр
    x1, y1 = cx - bx * size + px * size * 0.55, cy - by * size + py * size * 0.55
    x2, y2 = cx - bx * size - px * size * 0.55, cy - by * size - py * size * 0.55
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
            % (cx, cy, x1, y1, x2, y2, color))


# ── Фігура 1: площа петлі струму (далеко проти впритул) ─────────────────────
def fig_loop():
    W, H = 820, 500
    P = []
    P.append(text(W / 2, 56, "ривок струму біжить петлею «конденсатор → ніжка → чип → земля → конденсатор»",
                  size=12.5, color=MUTED, italic=True))

    def panel(x0, label, ok, cap_x):
        # рамка-плата
        out = rect(x0, 96, 350, 330, fill=BG, stroke="#c9d3dc", sw=1.4)
        out += text(x0 + 175, 90, label, size=12.5, bold=True)
        # чип
        chip_x = x0 + 25
        out += rect(chip_x, 160, 100, 90, fill="#f3f3f3", stroke=INK, sw=1.8)
        out += text(chip_x + 50, 200, "чип", size=13, bold=True)
        vdd_x = chip_x + 100
        out += text(vdd_x + 8, 152, "VDD", size=10.5, color=INK, anchor="start")
        out += text(vdd_x + 8, 332, "GND", size=10.5, color=INK, anchor="start")
        # площа петлі (заливка)
        loop_w = cap_x - vdd_x
        fill = "#eef6ef" if ok else "#fbecec"
        out += rect(vdd_x, 170, loop_w, 150, fill=fill, stroke="none", sw=0)
        # верхня й нижня рейки
        out += line(vdd_x, 170, cap_x, 170, color=INK, sw=2.4)
        out += line(vdd_x, 320, cap_x, 320, color=INK, sw=2.4)
        # конденсатор праворуч
        out += line(cap_x, 170, cap_x, 240, color=INK, sw=2.2)
        out += line(cap_x, 250, cap_x, 320, color=INK, sw=2.2)
        out += cap(cap_x, 245, w=36)
        out += text(cap_x + 26, 250, "100 нФ", size=11.5, color=INK, anchor="start", bold=True)
        # стрілки струму петлею
        col = FIELD if ok else POS
        midx = (vdd_x + cap_x) / 2
        out += line(cap_x - 6, 170, vdd_x + 12, 170, color=col, sw=2)
        out += head(vdd_x + 12, 170, 180, col)
        out += line(vdd_x + 12, 320, cap_x - 6, 320, color=col, sw=2)
        out += head(cap_x - 6, 320, 0, col)
        # підпис під панеллю
        cap_col = "#1f6e33" if ok else "#9a2b22"
        msg = (["крихітна петля: запас доходить", "за наносекунди, без викидів"] if ok
               else ["велика петля = великий «опір» швидкій", "зміні струму — викид на кожному фронті"])
        out += text(x0 + 175, 388, msg[0], size=11.5, color=cap_col, bold=True)
        out += text(x0 + 175, 404, msg[1], size=11.5, color=cap_col, bold=True)
        return out

    P.append(panel(50, "погано: конденсатор «десь на платі»", False, 380))
    P.append(panel(430, "добре: впритул до ніжки", True, 595))
    P.append(text(W / 2, 452, "довгий провідник опирається швидкій зміні струму (це його індуктивність);",
                  size=12, color=MUTED, italic=True))
    P.append(text(W / 2, 470, "тому важлива не відстань сама собою, а замкнена ПЛОЩА шляху струму",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "loop.svg"), W, H,
           *P, title="Чому «впритул»: рахується площа петлі струму")


# ── Фігура 2: ієрархія запасів (три рубежі) ────────────────────────────────
def fig_hierarchy():
    W, H = 820, 440
    P = []
    P.append(text(W / 2, 56, "ближчий до чипа — менший, але швидший; дальній — більший, але повільніший",
                  size=12.5, color=MUTED, italic=True))
    # шина живлення
    P.append(line(70, 160, 700, 160, color=INK, sw=2.6))
    P.append(text(72, 150, "шина живлення", size=11.5, color=MUTED, anchor="start"))

    def rail(x, name, val, scale, role):
        out = line(x, 160, x, 222, color=INK, sw=2.2)
        out += cap(x, 230, w=40)
        out += line(x, 240, x, 296, color=INK, sw=2.2)
        out += gnd(x, 300)
        out += text(x, 340, name, size=12.5, bold=True)
        out += text(x, 358, val, size=11.5, color=MUTED)
        out += text(x, 384, scale, size=11.5, color=FIELD, bold=True)
        out += text(x, 400, role, size=11.5, color=FIELD, bold=True)
        return out

    P.append(rail(110, "електроліт на вході", "100–1000 мкФ", "мілісекунди:", "провали джерела"))
    P.append(rail(360, "кераміка на групу", "1–10 мкФ", "мікросекунди:", "перемикання вузлів"))
    P.append(rail(590, "100 нФ біля ніжки", "кожному виводу", "наносекунди:", "фронти логіки"))
    # чип
    P.append(rect(700, 130, 95, 60, fill="#f3f3f3", stroke=INK, sw=1.8))
    P.append(text(747, 165, "чип", size=13, bold=True))
    # стрілки «повільніший доряджає швидший»
    P.append(line(165, 205, 300, 205, color=MUTED, sw=1.6))
    P.append(head(300, 205, 0, MUTED, size=7))
    P.append(line(415, 205, 525, 205, color=MUTED, sw=1.6))
    P.append(head(525, 205, 0, MUTED, size=7))
    P.append(text(360, 198, "повільніший доряджає швидший", size=10.5, color=MUTED, italic=True))
    P.append(line(645, 150, 700, 150, color=MUTED, sw=1.4))
    P.append(head(700, 150, 0, MUTED, size=7))
    render(os.path.join(IMG, "hierarchy.svg"), W, H,
           *P, title="Три рубежі живлення: кожен запас закриває свій масштаб часу")


if __name__ == "__main__":
    fig_loop()
    fig_hierarchy()
    print("written:", IMG)
