# -*- coding: utf-8 -*-
"""Фігури до статті «Послідовне з'єднання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # колір дроту в усіх кадрах (тепла мідь)


# ── Локальні символи кола ────────────────────────────────────────────────────
def resistor(cx, cy, w=64, h=20, top=None, bot=None):
    """Прямокутний резистор із центром (cx,cy). top/bot — підписи над/під ним."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill=BG, stroke=INK, sw=2, rx=3)]
    if top:
        out.append(text(cx, cy - h / 2 - 8, top, size=13, bold=True, italic=True))
    if bot:
        out.append(text(cx, cy + h / 2 + 16, bot, size=11, color=MUTED))
    return "".join(out)


def battery(cx, cy, half=70, label=None):
    """Символ батареї (довга+коротка планка) вертикально, центр (cx,cy).
    Повертає (svg, y_top, y_bot) — точки приєднання дротів зверху й знизу."""
    out = [line(cx, cy - half, cx, cy - 12, color=INK, sw=2.4),     # верхній вивід
           line(cx - 18, cy - 12, cx + 18, cy - 12, color=INK, sw=3),   # довга планка (+)
           line(cx - 10, cy + 4, cx + 10, cy + 4, color=INK, sw=6),     # коротка планка (−)
           line(cx, cy + 4, cx, cy + half, color=INK, sw=2.4)]      # нижній вивід
    if label:
        out.append(text(cx - 24, cy - 4, label, size=12, color=POS, bold=True, anchor="end"))
    return "".join(out), cy - half, cy + half


def cur_arrow(x, y, color=POS, dx=22):
    """Маленька стрілка струму вправо вздовж дроту на висоті y."""
    return arrow(x, y, x + dx, y, color=color, sw=1.8)


# ── 1. Два факти: спільний струм, сума напруг ───────────────────────────────
def fig_two_facts():
    W, H = 760, 360
    top_y, bot_y = 140, 290
    left_x, right_x = 120, 660
    f = [text(W / 2, 30, "Послідовно: струм один, напруги додаються", size=17, bold=True),
         text(W / 2, 52, "обидва факти — прямі наслідки законів Кірхгофа",
              size=12, color=MUTED, italic=True)]

    # батарея ліворуч між верхньою та нижньою шинами
    bat, _, _ = battery(left_x, (top_y + bot_y) / 2, half=(bot_y - top_y) / 2, label="V")
    f.append(bat)
    # верхня й нижня шини
    f.append(line(left_x, top_y, right_x, top_y, color=WIRE, sw=2.4))
    f.append(line(left_x, bot_y, right_x, bot_y, color=WIRE, sw=2.4))
    f.append(line(right_x, top_y, right_x, bot_y, color=INK, sw=2.4))

    # три резистори на верхній шині
    xs = [225, 385, 545]
    for i, x in enumerate(xs, 1):
        f.append(resistor(x, top_y, w=70))
        f.append(text(x, top_y - 28, "R%d" % i, size=12.5, bold=True, italic=True))
        f.append(text(x, top_y - 42, "V%d" % i, size=11, color=NEG, bold=True))

    # стрілки струму між елементами
    for x in (150, 305, 465, 600):
        f.append(cur_arrow(x, top_y))
    f.append(text(648, top_y + 18, "I — один і той самий", size=11, color=POS, bold=True, anchor="start"))

    # підсумкова смужка з двома фактами
    f.append(fitbox(150, 322, 460, 30, "①  I однаковий у кожному     ②  V = V₁ + V₂ + V₃",
                    size=13, fill="#eaf0fb", stroke=NEG, bold=True))
    render(os.path.join(IMG, "series-two-facts.svg"), W, H, *f)


# ── 2. Чому опори додаються (виведення) ──────────────────────────────────────
def fig_req_derivation():
    W, H = 800, 340
    top_y, bot_y = 150, 280
    left_x, right_x = 100, 340
    f = [text(W / 2, 30, "Чому опори додаються: R_екв = R₁ + R₂ + R₃", size=17, bold=True),
         text(W / 2, 52, "спільний струм + закон Ома на кожному → опори складаються",
              size=12, color=MUTED, italic=True)]

    bat, _, _ = battery(left_x, (top_y + bot_y) / 2, half=(bot_y - top_y) / 2, label="V")
    f.append(bat)
    f.append(line(left_x, top_y, right_x, top_y, color=WIRE, sw=2.2))
    f.append(line(left_x, bot_y, right_x, bot_y, color=WIRE, sw=2.2))
    f.append(line(right_x, top_y, right_x, bot_y, color=INK, sw=2.2))
    for i, x in enumerate((156, 236, 314), 1):
        f.append(resistor(x, top_y, w=52, h=16))
        f.append(text(x, top_y - 22, "R%d" % i, size=12.5, bold=True, italic=True))
    f.append(cur_arrow(118, top_y))
    f.append(text(118, top_y - 12, "I", size=11, color=POS, bold=True, italic=True))

    # права панель з виведенням
    px, py, pw, ph = 400, 96, 390, 188
    f.append(rect(px, py, pw, ph, fill="#f6f8fc", stroke=INK, sw=1.6, rx=12))
    f.append(text(px + 20, py + 32, "спільний струм I (однаковий скрізь)",
                  size=12, anchor="start"))
    f.append(text(px + 20, py + 62, "V₁ = I·R₁,   V₂ = I·R₂,   V₃ = I·R₃",
                  size=12.5, bold=True, anchor="start"))
    f.append(text(px + 20, py + 96, "V = V₁ + V₂ + V₃ = I·(R₁+R₂+R₃)",
                  size=12.5, bold=True, anchor="start"))
    f.append(fitbox(px + 20, py + 120, pw - 40, 46, "R_екв = R₁ + R₂ + R₃",
                    size=15, fill="#eef7f0", stroke=FIELD, color=FIELD, bold=True))
    render(os.path.join(IMG, "req-derivation.svg"), W, H, *f)


# ── 3. Три резистори = один еквівалентний ────────────────────────────────────
def fig_equivalent():
    W, H = 800, 320
    y = 150
    f = [text(W / 2, 30, "Три послідовні резистори = один еквівалентний", size=17, bold=True),
         text(W / 2, 52, "для джерела немає різниці — важить лише сума опорів",
              size=12, color=MUTED, italic=True)]

    # ліва трійка
    f.append(line(70, y, 100, y, color=WIRE, sw=2.4))
    for i, x in enumerate((125, 190, 255), 1):
        f.append(resistor(x, y, w=50, h=18))
        f.append(text(x, y - 20, "R%d" % i, size=12.5, bold=True, italic=True))
    f.append(line(280, y, 320, y, color=WIRE, sw=2.4))
    f.append(text(190, y + 46, "100 + 220 + 330 Ω", size=11, color=MUTED, italic=True))

    # знак тотожності
    f.append(text(410, y + 12, "≡", size=36, bold=True))

    # правий еквівалент
    f.append(line(500, y, 560, y, color=WIRE, sw=2.4))
    f.append(fitbox(560, y - 16, 120, 32, "R_екв = 650 Ω", size=12.5, bold=True))
    f.append(line(680, y, 740, y, color=WIRE, sw=2.4))

    # нижня смужка-висновок
    f.append(fitbox(150, 250, 500, 50,
                    "Послідовне з'єднання ЗАВЖДИ збільшує опір:\nR_екв більший за будь-який окремий у ланцюжку",
                    size=12.5, fill="#fff3e8", stroke="#e08030", bold=True))
    render(os.path.join(IMG, "equivalent.svg"), W, H, *f)


# ── 4. Worked-приклад ────────────────────────────────────────────────────────
def fig_worked():
    W, H = 800, 340
    top_y, bot_y = 130, 280
    left_x, right_x = 100, 430
    f = [text(W / 2, 30, "Приклад: розрахувати послідовне коло", size=17, bold=True),
         text(W / 2, 52, "R₁=100, R₂=220, R₃=330 Ω під 12 В — знайти струм і спади",
              size=12, color=MUTED, italic=True)]

    bat, _, _ = battery(left_x, (top_y + bot_y) / 2, half=(bot_y - top_y) / 2, label="12 В")
    f.append(bat)
    f.append(line(left_x, top_y, right_x, top_y, color=WIRE, sw=2.4))
    f.append(line(left_x, bot_y, right_x, bot_y, color=WIRE, sw=2.4))
    f.append(line(right_x, top_y, right_x, bot_y, color=INK, sw=2.4))
    for i, x in enumerate((175, 275, 380), 1):
        f.append(resistor(x, top_y, w=70, h=18))
        f.append(text(x, top_y - 22, "R%d" % i, size=12.5, bold=True, italic=True))
    f.append(cur_arrow(118, top_y))

    # права панель розрахунку
    px, py, pw, ph = 470, 92, 320, 204
    f.append(rect(px, py, pw, ph, fill="#f6f8fc", stroke=INK, sw=1.6, rx=12))
    rows = ["R_екв = 100+220+330 = 650 Ω",
            "I = V / R_екв = 12 / 650 ≈ 18.5 мА",
            "V₁ = I·R₁ ≈ 1.85 В",
            "V₂ = I·R₂ ≈ 4.07 В",
            "V₃ = I·R₃ ≈ 6.08 В"]
    for i, r in enumerate(rows):
        f.append(text(px + 18, py + 36 + i * 30, r, size=12.5,
                      bold=(i < 2), anchor="start"))
    f.append(fitbox(px + 18, py + 168, pw - 36, 26,
                    "перевірка: 1.85+4.07+6.08 ≈ 12 В ✓",
                    size=11, fill="#eef7f0", stroke=FIELD, color=FIELD, bold=True))
    render(os.path.join(IMG, "worked.svg"), W, H, *f)


# ── 5. Де працює послідовне з'єднання ────────────────────────────────────────
def fig_applications():
    W, H = 860, 380
    f = [text(W / 2, 30, "Де працює послідовне з'єднання", size=17, bold=True),
         text(W / 2, 52, "обмеження струму, складання опорів — і слабке місце ланцюжка",
              size=12, color=MUTED, italic=True)]

    # ── панель 1: резистор перед світлодіодом ──
    y = 130
    f.append(text(150, 92, "Обмеження струму", size=12.5, bold=True))
    f.append(line(70, y, 110, y, color=WIRE, sw=2.2))
    f.append(resistor(138, y, w=56, h=18))
    f.append(text(138, y - 20, "R", size=12.5, bold=True, italic=True))
    f.append(line(166, y, 200, y, color=WIRE, sw=2.2))
    # символ світлодіода (трикутник + планка)
    f.append('<polygon points="200,120 200,142 222,131" fill="%s"/>' % INK)
    f.append(line(222, 118, 222, 144, color=INK, sw=2.6))
    f.append(line(222, y, 256, y, color=WIRE, sw=2.2))
    f.append(text(150, 178, "R послідовно з LED", size=10, color=MUTED))
    f.append(text(150, 194, "тримає струм у нормі", size=10, color=MUTED))

    # ── панель 2: гірлянда зі згаслою лампою ──
    f.append(text(490, 92, "Гірлянда (слабке місце)", size=12.5, bold=True))
    f.append(line(360, y, 620, y, color="#bdbdbd", sw=2))
    bulbs = [384, 424, 464, 504, 544, 584]
    for cx in bulbs:
        f.append(circle(cx, y, 9, fill="#bdbdbd", stroke="#8f8f8f", sw=1.5))
    # хрестик на одній лампі
    bx = 504
    f.append(line(bx - 7, y - 7, bx + 7, y + 7, color=POS, sw=2.4))
    f.append(line(bx - 7, y + 7, bx + 7, y - 7, color=POS, sw=2.4))
    f.append(text(490, 178, "одна лампа перегоріла —", size=10, color=POS, bold=True))
    f.append(text(490, 194, "коло розірване, усі згасли", size=10, color=MUTED, italic=True))

    # ── панель 3: як один довший провідник ──
    f.append(text(740, 92, "Як один довший", size=12.5, bold=True))
    f.append(rect(666, 122, 50, 16, fill=WIRE, stroke="#9c6b48", sw=1.4, rx=3))
    f.append(rect(720, 122, 50, 16, fill=WIRE, stroke="#9c6b48", sw=1.4, rx=3))
    f.append(text(742, 158, "=", size=16, bold=True))
    f.append(rect(666, 176, 104, 16, fill=WIRE, stroke="#9c6b48", sw=1.4, rx=3))
    f.append(text(740, 214, "довше → більший опір", size=10, color=MUTED))
    f.append(text(740, 230, "(R = ρL/A)", size=9.5, color=MUTED, italic=True))

    # нижня смужка
    f.append(fitbox(120, 300, 620, 50,
                    "Послідовно ставлять, щоб обмежити струм, скласти опір чи напругу —\nта пам'ятають: розрив у будь-якій ланці гасить усе коло",
                    size=11.5, fill="#f6f8fc", stroke=INK, bold=True))
    render(os.path.join(IMG, "applications.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_facts()
    fig_req_derivation()
    fig_equivalent()
    fig_worked()
    fig_applications()
    print("OK: 5 SVG -> img/")
