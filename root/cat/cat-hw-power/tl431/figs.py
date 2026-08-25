# -*- coding: utf-8 -*-
"""Фігури до теми «TL431».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def zener(cx, top, bot, color=INK, sw=2.0):
    """Символ стабілітрона (катод угорі) між y=top та y=bot, вістрям донизу."""
    midy = (top + bot) / 2
    th = 14          # половина ширини трикутника
    out = [line(cx, top, cx, midy - 13, color=color, sw=sw)]
    # трикутник вістрям донизу
    out.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#fbf3df" '
               'stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>'
               % (cx - th, midy - 13, cx + th, midy - 13, cx, midy + 13, color, sw))
    # планка катода з «вусами» (стабілітрон)
    out.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
               'fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round" '
               'stroke-linecap="round"/>'
               % (cx - th - 4, midy + 19, cx - th, midy + 13,
                  cx + th, midy + 13, cx + th + 4, midy + 7, color))
    out.append(line(cx, midy + 13, cx, bot, color=color, sw=sw))
    return "".join(out)


def coil(x, y0, y1, color=INK, sw=2.0, w=8, n=4):
    """Котушка/резистор-зигзаг по вертикалі від y0 до y1."""
    pts = [(x, y0)]
    seg = (y1 - y0) / (2 * n)
    yy = y0 + seg / 2
    s = 1
    for _ in range(2 * n):
        pts.append((x + s * w, yy))
        yy += seg
        s = -s
    pts.append((x, y1))
    p = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (p, color, sw))


def fig_inside():
    """Нутро TL431 (опора + підсилювач + ключ) та як його бачить схема."""
    W, H = 780, 430
    f = [text(W / 2, 26, "Усередині TL431: підсилювач похибки рівняє REF до 2.5 В",
              size=17, bold=True)]

    # ── рамка «всередині» ──
    f.append(rect(70, 60, 360, 320, fill="#fcfcfc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(82, 82, "TL431 (всередині)", size=13, color=MUTED, anchor="start", bold=True))

    # опора 2.5 В
    f.append(rect(106, 224, 88, 52, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(150, 246, "опора", size=13, color=FIELD, bold=True))
    f.append(text(150, 265, "2.5 В", size=14, color=FIELD, bold=True))

    # підсилювач похибки (трикутник вістрям праворуч)
    f.append('<path d="M 246,139 L 246,211 L 324,175 Z" fill="#fff" stroke="%s" '
             'stroke-width="2" stroke-linejoin="round"/>' % INK)
    f.append(text(232, 162, "+", size=18, color=POS, bold=True))
    f.append(text(232, 198, "−", size=18, color=NEG, bold=True))
    f.append(text(281, 150, "підсилювач", size=11))
    f.append(text(281, 168, "похибки", size=11))

    # вхід REF на «+»
    f.append(line(70, 157, 246, 157, color=INK, sw=2))
    f.append(circle(70, 157, 3.2, fill=INK, stroke=INK))
    f.append(text(60, 162, "REF", size=13, anchor="end", bold=True))
    # опора на «−»
    f.append(line(150, 224, 150, 193, color=FIELD, sw=2))
    f.append(line(150, 193, 246, 193, color=FIELD, sw=2))
    f.append(line(150, 276, 150, 350, color=FIELD, sw=2))

    # вихідний ключ (транзистор як планка) між виходом підсилювача і катодом
    f.append(line(324, 175, 350, 175, color=INK, sw=2))
    f.append(line(350, 159, 350, 191, color=INK, sw=3))
    f.append(text(388, 150, "вих. ключ", size=11, anchor="start"))
    f.append(line(350, 175, 372, 175, color=INK, sw=2))
    f.append(line(372, 90, 372, 350, color=INK, sw=2))
    # катод
    f.append(line(372, 90, 430, 90, color=INK, sw=2))
    f.append(circle(430, 90, 3.2, fill=INK, stroke=INK))
    f.append(text(440, 95, "CATHODE (K)", size=13, anchor="start", bold=True))
    # анод (нижня шина)
    f.append(line(150, 350, 430, 350, color=INK, sw=2))
    f.append(circle(430, 350, 3.2, fill=INK, stroke=INK))
    f.append(text(440, 355, "ANODE (A)", size=13, anchor="start", bold=True))

    f.append(text(250, 372, "REF > 2.5 В → ключ відкривається → K сідає до A",
                  size=11.5, color=POS, italic=True))

    # ── права частина: «як це бачить схема» ──
    f.append(text(640, 84, "Як це бачить схема:", size=13, bold=True))
    f.append(text(640, 104, "регульований стабілітрон", size=12, color=MUTED))
    f.append(zener(640, 120, 300, color=INK))
    f.append(text(656, 116, "K", size=14, anchor="start", bold=True))
    f.append(text(656, 312, "A", size=14, anchor="start", bold=True))
    f.append(line(566, 200, 624, 200, color=FIELD, sw=2))
    f.append(text(560, 205, "REF", size=13, color=FIELD, anchor="end", bold=True))
    f.append(text(640, 338, "поріг = 2.5 В", size=12, color=FIELD))
    f.append(text(640, 356, "(не фіксований!)", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "inside.svg"), W, H, *f)


def fig_feedback():
    """TL431 + оптопара у зворотному зв'язку ізольованого імпульсного БЖ."""
    W, H = 820, 440
    f = [text(W / 2, 24,
              "TL431 у зворотному зв'язку зарядного: два резистори задають напругу, "
              "оптопара несе сигнал крізь ізоляцію", size=14, bold=True)]

    # бар'єр ізоляції
    f.append(line(300, 50, 300, 410, color=MUTED, sw=1.5, dash="7 6"))
    f.append(text(300, 404, "бар'єр ізоляції", size=11.5, color=MUTED, italic=True))
    f.append(text(286, 70, "первинна сторона", size=11.5, color=MUTED, anchor="end"))
    f.append(text(314, 70, "вторинна сторона (вихід)", size=11.5, color=MUTED, anchor="start"))

    # шини виходу
    f.append(line(330, 96, 800, 96, color=POS, sw=2.6))
    f.append(line(330, 372, 800, 372, color=NEG, sw=2.6))
    f.append(text(796, 87, "Vout = 5.0 В", size=13, color=POS, anchor="end", bold=True))
    f.append(text(796, 391, "земля вторинки", size=12, color=NEG, anchor="end"))

    # дільник R1/R2 праворуч
    f.append(line(720, 96, 720, 128, color=INK, sw=2))
    f.append(coil(720, 128, 186, color=INK, sw=2))   # R1
    f.append(text(733, 158, "R1", size=14, anchor="start", bold=True))
    f.append(circle(720, 250, 3.4, fill=INK, stroke=INK))
    f.append(text(732, 243, "REF", size=11.5, color=MUTED, anchor="start"))
    f.append(coil(720, 256, 314, color=INK, sw=2))   # R2
    f.append(text(733, 290, "R2", size=14, anchor="start", bold=True))
    f.append(line(720, 314, 720, 372, color=INK, sw=2))

    # TL431 (як стабілітрон) у центрі
    f.append(text(560, 118, "TL431", size=14, bold=True))
    f.append(zener(560, 150, 372, color=INK))
    f.append(text(573, 241, "K", size=12, anchor="start", bold=True))
    f.append(text(547, 241, "A", size=12, anchor="end", bold=True))
    # REF від вузла дільника на TL431
    f.append(line(720, 250, 578, 236, color=FIELD, sw=2))
    f.append(text(644, 227, "REF", size=12, color=FIELD, bold=True))

    # верх TL431 на світлодіод оптопари (вторинний бік)
    f.append(line(560, 150, 430, 150, color=INK, sw=2))
    f.append(circle(560, 150, 3.0, fill=INK, stroke=INK))
    # світлодіод оптопари (вторинний бік) + баласт
    f.append(line(430, 96, 430, 128, color=INK, sw=2))
    f.append(coil(430, 128, 178, color="#b5732e", sw=2, w=7, n=3))   # баласт R
    f.append(text(442, 162, "R", size=12, color="#b5732e", anchor="start", bold=True))
    f.append('<path d="M 421,159 L 439,159 L 430,177 Z" fill="#fbecec" stroke="%s" '
             'stroke-width="2" stroke-linejoin="round"/>' % POS)
    f.append(line(420, 177, 440, 177, color=POS, sw=2.4))
    f.append(line(430, 177, 430, 150, color=POS, sw=2))
    f.append(line(442, 214, 454, 206, color="#e0a32e", sw=1.6))
    f.append(line(442, 224, 454, 216, color="#e0a32e", sw=1.6))
    f.append(text(414, 132, "оптопара", size=11, color=MUTED, anchor="end"))

    # фототранзистор (первинний бік)
    f.append(circle(180, 220, 26, fill="#fff", stroke=INK, sw=2))
    f.append(line(172, 200, 172, 240, color=INK, sw=2))
    f.append(line(172, 210, 194, 198, color=INK, sw=2))
    f.append(arrow(172, 230, 194, 242, color=INK, sw=2))
    f.append(arrow(220, 205, 198, 213, color="#e0a32e", sw=1.8))
    f.append(arrow(220, 215, 198, 223, color="#e0a32e", sw=1.8))
    f.append(text(180, 262, "фототранзистор", size=11, color=MUTED))

    # ШІМ-контролер
    f.append(rect(70, 120, 70, 80, fill="#e9eefb", stroke=NEG, sw=2))
    f.append(text(105, 150, "ШІМ-", size=12, color=NEG, bold=True))
    f.append(text(105, 166, "контро-", size=12, color=NEG, bold=True))
    f.append(text(105, 182, "лер", size=12, color=NEG, bold=True))
    f.append(line(194, 198, 194, 160, color=INK, sw=2))
    f.append(line(194, 160, 140, 160, color=INK, sw=2))
    f.append(text(150, 154, "FB", size=11, color=NEG, anchor="start"))
    f.append(line(194, 242, 194, 300, color=INK, sw=2))
    f.append(line(70, 300, 194, 300, color=INK, sw=2))
    f.append(line(70, 300, 70, 200, color=INK, sw=2))
    f.append(text(66, 320, "первинна земля", size=11, color=MUTED, anchor="start"))

    f.append(text(335, 408,
                  "Поріг:  Vout = 2.5 · (1 + R1/R2)   —   міняєш R1/R2, міняєш напругу заряду",
                  size=12.5, color=FIELD, anchor="start", bold=True))
    f.append(text(560, 52,
                  "Vout ↑ → REF > 2.5 В → TL431 тягне струм → світлодіод яскравіше "
                  "→ ШІМ зменшує → Vout вниз",
                  size=10.5, color=POS, italic=True))

    render(os.path.join(IMG, "feedback.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_feedback()
    print("OK: inside.svg, feedback.svg")
