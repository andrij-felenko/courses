# -*- coding: utf-8 -*-
# Фігура для вставки hist-microservices-term.md.
# Окремий файл, щоб не конфліктувати з паралельним редагуванням figs.py;
# вивід — у ту саму теку ./img.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Шлях народження терміна «мікросервіси» (2005 → 2014) ─────────────────────
def term_birth_timeline():
    # Вертикальна вісь часу: практика ліворуч, назва — праворуч.
    W, H = 1160, 760
    parts = []
    parts.append(text(W / 2, 34, "Річ старша за назву: як визрівав термін «мікросервіси»",
                      size=18, bold=True))

    ax = W / 2
    top, bot = 92, H - 40
    parts.append(line(ax, top, ax, bot, color=MUTED, sw=2))

    parts.append(text(ax - 300, 68, "ПРАКТИКА · річ уже роблять",
                      size=12, bold=True, color=FIELD))
    parts.append(text(ax + 300, 68, "НАЗВА · річ дістає ім'я",
                      size=12, bold=True, color=NEG))

    # (рік, підпис, бік: -1 ліворуч практика / +1 праворуч назва, колір)
    rows = [
        ("2005", "Пітер Роджерс кидає\n«Micro-Web-Services»\n(REST + пайпи Unix)", -1, FIELD),
        ("бл. 2010", "Netflix, Едрієн Кокрофт:\n«fine-grained SOA» —\nстиль уже в проді", -1, FIELD),
        ("травень 2011", "Воркшоп під Венецією:\nслово «microservice»\nвперше обговорили", +1, NEG),
        ("березень 2012", "Доповіді Льюїса (Краків)\nі Джорджа — стиль\nпоказують публіці", -1, FIELD),
        ("травень 2012", "Та сама група ухвалює\nім'я «microservices»", +1, NEG),
        ("25 бер. 2014", "Стаття Фаулера й Льюїса —\nтермін іде у широкий світ", +1, NEG),
    ]

    n = len(rows)
    y0, y1 = top + 46, bot - 32
    step = (y1 - y0) / (n - 1)
    for i, (year, label, side, col) in enumerate(rows):
        cy = y0 + i * step
        parts.append(circle(ax, cy, 6, fill=col, stroke=col, sw=1.5))
        # рік — з протилежного до підпису боку осі, з відступом, щоб не налазив
        yx = ax + (-side) * 78
        yanchor = "end" if side > 0 else "start"
        parts.append(text(yx, cy + 4, year, size=12, bold=True, color=INK,
                          anchor=yanchor))
        # коробка-підпис — на своєму боці, далеко від осі
        bx = ax + side * 330
        fill = "#eaf7ef" if col == FIELD else "#eaf0fd"
        b, bw, bh = box_at(bx, cy, label, size=12, fill=fill, stroke=col, min_w=270)
        parts.append(b)
        # конектор від осі до краю коробки; стартує за написом року
        edge = bx - side * bw
        parts.append(line(ax + side * 118, cy, edge, cy, color=col, sw=1.4))

    render(os.path.join(IMG, "term-birth-timeline.svg"), W, H, *parts)


if __name__ == "__main__":
    term_birth_timeline()
    print("figure written to", IMG)
