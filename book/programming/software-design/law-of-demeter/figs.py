# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Фігура: «крізь незнайомців» проти «лише з другом» ───────────────────────
W, H = 860, 470
parts = []

# заголовки двох панелей
parts.append(text(215, 62, "Крізь незнайомців", size=16, bold=True, color=POS))
parts.append(text(645, 62, "Лише з другом", size=16, bold=True, color=FIELD))

# роздільник
parts.append(line(430, 80, 430, H - 24, color=MUTED, sw=1.2, dash="5 6"))

# --- ЛІВА панель: ланцюг вагонів (клієнт лізе вглиб) ---
cli_l = textbox(90, 130, "клієнт", size=14, bold=True, fill="#fdecea", stroke=POS)
parts.append(cli_l[0])

# чотири рівні устрою один під одним
levels = [
    (215, 130, "order",    "об'єкт"),
    (215, 205, "customer", "чужий устрій"),
    (215, 280, "address",  "чужий устрій"),
    (215, 355, "city",     "чужий устрій"),
]
boxes = []
for cx, cy, name, tag in levels:
    b = textbox(cx, cy, name, size=14, bold=True, min_w=130)
    parts.append(b[0])
    boxes.append((cx, cy, b[2]))
    parts.append(text(cx, cy + 27, tag, size=10, color=MUTED))

# стрілка від клієнта до order (права грань клієнта → ліва грань order)
left_cli_right = 90 + cli_l[1] / 2
parts.append(arrow(left_cli_right + 4, 130, 215 - boxes[0][2] / 2 - 4, 130, color=POS))

# стрілки вглиб між рівнями
for i in range(len(boxes) - 1):
    cx, cy, hh = boxes[i]
    parts.append(arrow(cx, cy + hh / 2 + 4, cx, boxes[i + 1][1] - boxes[i + 1][2] / 2 - 4, color=POS))

# останній вагон щось робить
parts.append(text(215, 355 + 44, ".toUpperCase()", size=12, color=INK, italic=True))

# підпис ліворуч унизу
parts.append(text(215, H - 12, "4 крапки — 4 факти про чужий устрій", size=11, color=POS))

# --- ПРАВА панель: клієнт знає лише order ---
cli_r = textbox(520, 200, "клієнт", size=14, bold=True, fill="#eafaf1", stroke=FIELD)
parts.append(cli_r[0])

# великий order з захованою глибиною
ord_x, ord_y, ord_w, ord_h = 620, 110, 190, 250
parts.append(rect(ord_x, ord_y, ord_w, ord_h, fill="#f4f6f8", stroke=FIELD, sw=2))
parts.append(text(ord_x + ord_w / 2, ord_y + 24, "order", size=15, bold=True, color=FIELD))
# сіра рамка «уся глибина захована»
gx, gy, gw, gh = ord_x + 22, ord_y + 44, ord_w - 44, ord_h - 66
parts.append(rect(gx, gy, gw, gh, fill="#eceff1", stroke=MUTED, sw=1.2, rx=6))
parts.append(fitbox(gx + 6, gy + 8, gw - 12, 58,
                    "customer\naddress\ncity", size=11, color=MUTED,
                    fill="#eceff1", stroke="#eceff1", sw=0))
parts.append(text(ord_x + ord_w / 2, gy + gh - 12, "уся глибина захована",
                  size=10, color=MUTED, italic=True))

# стрілка клієнт -> order з одним запитом
parts.append(arrow(520 + cli_r[1] / 2 + 4, 200, ord_x - 6, 200, color=FIELD))
parts.append(text((520 + cli_r[1] / 2 + ord_x) / 2 + 6, 188, "shipToCity()", size=11, color=FIELD, bold=True))

# підпис праворуч унизу
parts.append(text(645, H - 12, "1 друг — 1 запитання", size=11, color=FIELD))

render(os.path.join(OUT, 'train-vs-friend.svg'), W, H, *parts)
print("wrote train-vs-friend.svg")


# ── Фігура (hist): звідки взялося ім'я — родовід Zeus → Demeter → закон ──────
W2, H2 = 900, 470
p2 = []

# --- ВЕРХНІЙ ряд: міфологія ---
p2.append(text(W2 / 2, 40, "Міфологія: брат і сестра", size=14, bold=True, color=MUTED))

zeus_myth = textbox(230, 92, "Зевс", size=15, bold=True, min_w=150,
                    fill="#eef2f7", stroke=MUTED)
p2.append(zeus_myth[0])
p2.append(text(230, 92 + 30, "бог-громовержець", size=10, color=MUTED))

dem_myth = textbox(670, 92, "Деметра", size=15, bold=True, min_w=150,
                   fill="#eafaf1", stroke=FIELD)
p2.append(dem_myth[0])
p2.append(text(670, 92 + 30, "сестра, богиня хліба", size=10, color=MUTED))

# зв'язок «сестра» між ними (по верхньому ряду, повз написи)
p2.append(line(230 + zeus_myth[1] / 2 + 6, 92, 670 - dem_myth[1] / 2 - 6, 92,
              color=MUTED, sw=1.2, dash="4 5"))
p2.append(text(450, 82, "сестра", size=11, color=MUTED, italic=True))

# роздільна лінія міф / софт
p2.append(line(40, 150, W2 - 40, 150, color=MUTED, sw=1, dash="2 6"))
p2.append(text(W2 / 2, 172, "Софт у Northeastern (Ліберхер і група)", size=14, bold=True, color=INK))

# --- НИЖНІЙ ряд: інструменти, названі за богами ---
# підписи-пояснення СТОЯТЬ ПІД боксами, зсунуті вбік від осей вертикальних стрілок
zeus_sw = textbox(230, 236, "Zeus", size=16, bold=True, min_w=200)
p2.append(zeus_sw[0])
p2.append(text(120, 274, "мова опису заліза", size=11, color=MUTED, anchor="start"))
p2.append(text(120, 290, "(VLSI-чипи)", size=11, color=MUTED, anchor="start"))

dem_sw = textbox(670, 236, "Demeter", size=16, bold=True, min_w=200,
                 fill="#eafaf1", stroke=FIELD)
p2.append(dem_sw[0])
p2.append(text(780, 274, "інструмент, щоб", size=11, color=MUTED, anchor="end"))
p2.append(text(780, 290, "спростити Zeus", size=11, color=MUTED, anchor="end"))

# вертикальні стрілки: бог → однойменний інструмент (осі x=230 та x=670 вільні від написів)
p2.append(arrow(230, 92 + zeus_myth[2] / 2 + 30 + 6, 230, 236 - zeus_sw[2] / 2 - 6, color=MUTED))
p2.append(arrow(670, 92 + dem_myth[2] / 2 + 30 + 6, 670, 236 - dem_sw[2] / 2 - 6, color=FIELD))
p2.append(text(246, 190, "названо на честь", size=9, color=MUTED, anchor="start"))

# горизонтальна стрілка Zeus → Demeter (шукали ім'я, споріднене із Zeus)
p2.append(arrow(230 + zeus_sw[1] / 2 + 6, 236, 670 - dem_sw[1] / 2 - 6, 236, color=INK))
p2.append(text(450, 224, "шукали споріднену назву", size=11, color=INK, italic=True))

# --- НИЗ: із проєкту Demeter народився закон ---
law = textbox(670, 384, "закон Деметри", size=15, bold=True, min_w=230,
              fill="#fff8e1", stroke="#c9a227")
p2.append(law[0])
p2.append(text(670, 384 + 29, "правило стилю, помічене в роботі", size=10, color=MUTED))

# вертикальна стрілка Demeter → закон; підпис зсунено праворуч від осі x=670
p2.append(arrow(670, 236 + dem_sw[2] / 2 + 6, 670, 384 - law[2] / 2 - 6, color="#c9a227"))
p2.append(text(686, 332, "1987 — Ієн Голланд", size=10, color=MUTED, anchor="start"))

# підсумковий рядок унизу ліворуч
p2.append(fitbox(70, 360, 300, 52,
                "Ім'я — випадковість родоводу:\nдо змісту закону стосунку не має",
                size=11, color=MUTED, fill="#f4f6f8", stroke=MUTED, sw=1))

render(os.path.join(OUT, 'zeus-demeter-lineage.svg'), W2, H2, *p2)
print("wrote zeus-demeter-lineage.svg")
