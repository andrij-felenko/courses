# -*- coding: utf-8 -*-
"""Фігури до ВСТАВОК теми «H-міст»:
  - api-h-bridge-board.md  → board-anatomy.svg, pinout-wiring.svg
  - proj-shoot-through.md   → deadtime-timing.svg, tradeoff.svg
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
(Сім фігур самої статті h-bridge мають окреме походження; цей генератор їх не чіпає.)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def motor(cx, cy, r=30):
    return (circle(cx, cy, r, fill="#eef2f7", stroke=LINE, sw=2) +
            text(cx, cy + 6, "M", size=18, bold=True, color=INK))


def pin(x, y, label, side="left", color=INK):
    """Виввід плати: коротка ніжка з кружком і підписом."""
    out = []
    if side == "left":          # ніжка ліворуч від рамки, підпис праворуч
        out.append(line(x - 16, y, x, y, color=color, sw=2))
        out.append(circle(x - 16, y, 3, fill=color, stroke=color, sw=1))
        out.append(text(x + 8, y + 4, label, size=11, anchor="start", bold=True))
    else:                       # ніжка праворуч, підпис ліворуч
        out.append(line(x, y, x + 16, y, color=color, sw=2))
        out.append(circle(x + 16, y, 3, fill=color, stroke=color, sw=1))
        out.append(text(x - 8, y + 4, label, size=11, anchor="end", bold=True))
    return "".join(out)


# ── comp 1. Блок-схема плати: чип ховає весь H-міст ──────────────────────────
def fig_board_anatomy():
    W, H = 760, 380
    f = [text(W / 2, 28, "Плата драйвера мотора: один чип ховає весь H-міст", size=16, bold=True)]

    # ліворуч: логіка / МК
    f.append(rect(34, 130, 150, 140, fill="#eef2f7", stroke=LINE, sw=1.6))
    f.append(text(109, 124, "логіка / МК", size=12, bold=True))
    f.append(text(109, 178, "3.3 – 5 В", size=12))
    f.append(text(109, 204, "кілька мА", size=11, color=MUTED))

    # центр: мікросхема-драйвер з чотирма рядками-блоками
    cx0, cy0, cw, ch = 244, 96, 268, 240
    f.append(rect(cx0, cy0, cw, ch, fill="#eef2f7", stroke="#7f93a8", sw=2.2))
    f.append(text(cx0 + cw / 2, cy0 + 22, "мікросхема-драйвер", size=14, bold=True))
    rows = ["2 півмости = 4 MOSFET-ключі",
            "драйвери затворів (і верхніх!)",
            "логіка напрямку + мертвий час",
            "захист: струм · перегрів · КЗ"]
    for i, r in enumerate(rows):
        ry = cy0 + 40 + i * 46
        f.append(fitbox(cx0 + 16, ry, cw - 32, 36, r, size=12, fill=BG, stroke="#c9d3dc", sw=1.4))

    # входи логіки → чип
    for label, y in (("IN1", 150), ("IN2", 196), ("EN (ШІМ)", 242)):
        f.append(arrow(184, y, 244, y, color=INK, sw=2))
        f.append(text(214, y - 8, label, size=10, bold=True))

    # +VM зверху, GND знизу
    f.append(arrow(cx0 + cw / 2, 64, cx0 + cw / 2, 96, color=POS, sw=2.4))
    f.append(text(cx0 + cw / 2, 56, "+VM (живлення мотора, 6–36 В)", size=11, color=POS, bold=True))
    f.append(line(cx0 + cw / 2, 336, cx0 + cw / 2, 352, color=INK, sw=1.6))
    f.append(line(cx0 + cw / 2 - 26, 352, cx0 + cw / 2 + 26, 352, color=INK, sw=1.6))
    f.append(text(cx0 + cw / 2, 368, "GND", size=10, bold=True))

    # виходи на мотор
    f.append(arrow(cx0 + cw, 150, 600, 150, color=INK, sw=2))
    f.append(text(580, 142, "OUT1", size=10.5, bold=True))
    f.append(arrow(cx0 + cw, 250, 600, 250, color=INK, sw=2))
    f.append(text(580, 242, "OUT2", size=10.5, bold=True))
    f.append(line(600, 150, 690, 150, color=INK, sw=2))
    f.append(line(690, 150, 690, 172, color=INK, sw=2))
    f.append(line(600, 250, 690, 250, color=INK, sw=2))
    f.append(line(690, 250, 690, 228, color=INK, sw=2))
    f.append(motor(690, 200))

    render(os.path.join(IMG, "board-anatomy.svg"), W, H, *f)


# ── comp 2. Розпіновка й підключення: спільна земля ─────────────────────────
def fig_pinout_wiring():
    W, H = 760, 372
    f = [text(W / 2, 28, "Як підключити: логічний і силовий бік — спільна земля", size=16, bold=True)]

    # центральний модуль-драйвер
    bx, by, bw, bh = 300, 80, 170, 220
    f.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke="#7f93a8", sw=2.2))
    f.append(text(bx + bw / 2, by + bh / 2 - 8, "драйвер", size=14, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 12, "мотора", size=14, bold=True))

    # ліві ніжки (логіка)
    f.append(pin(bx, 110, "VCC", "left", FIELD))
    f.append(pin(bx, 150, "IN1", "left"))
    f.append(pin(bx, 190, "IN2", "left"))
    f.append(pin(bx, 230, "EN",  "left"))
    f.append(pin(bx, 280, "GND", "left", FIELD))
    # праві ніжки (сила)
    f.append(pin(bx + bw, 110, "VM",   "right", POS))
    f.append(pin(bx + bw, 160, "OUT1", "right"))
    f.append(pin(bx + bw, 200, "OUT2", "right"))
    f.append(pin(bx + bw, 280, "GND",  "right", FIELD))

    # МК ліворуч
    f.append(rect(40, 150, 150, 130, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(115, 144, "МК", size=12, bold=True))
    f.append(text(115, 220, "3.3 / 5 В", size=11))
    f.append(arrow(115, 150, 115, 110, color=FIELD, sw=2))
    f.append(line(115, 110, bx - 16, 110, color=FIELD, sw=2))
    f.append(arrow(190, 150, bx - 16, 150, color=INK, sw=2))
    f.append(arrow(190, 190, bx - 16, 190, color=INK, sw=2))
    f.append(arrow(190, 230, bx - 16, 230, color=INK, sw=2))
    f.append(text(248, 138, "напрямок", size=9))
    f.append(text(240, 246, "ШІМ → швидкість", size=9))

    # спільна земля (пунктир)
    f.append(line(115, 280, 115, 320, color=FIELD, sw=2, dash="4 3"))
    f.append(line(bx - 16, 280, bx - 16, 320, color=FIELD, sw=2, dash="4 3"))
    f.append(line(bx + bw + 16, 280, bx + bw + 16, 320, color=FIELD, sw=2, dash="4 3"))
    f.append(line(115, 320, bx + bw + 16, 320, color=FIELD, sw=2, dash="4 3"))
    f.append(text((115 + bx + bw + 16) / 2, 338, "спільна земля — обов'язково з'єднати!",
                  size=11, color=FIELD, bold=True))

    # живлення мотора + мотор праворуч
    f.append(fitbox(560, 86, 180, 48, "+ живлення мотора\n(акумулятор, окремо)",
                    size=10, fill="#fbecec", stroke="#d8a0a0", sw=1.6, color=POS))
    f.append(arrow(560, 110, bx + bw + 16, 110, color=POS, sw=2.4))
    f.append(motor(660, 200, r=32))
    f.append(line(bx + bw + 16, 160, 626, 160, color=INK, sw=2))
    f.append(line(626, 160, 660, 160, color=INK, sw=2))
    f.append(line(660, 160, 660, 168, color=INK, sw=2))
    f.append(line(bx + bw + 16, 200, 600, 200, color=INK, sw=2))
    f.append(line(600, 200, 600, 244, color=INK, sw=2))
    f.append(line(600, 244, 660, 244, color=INK, sw=2))

    render(os.path.join(IMG, "pinout-wiring.svg"), W, H, *f)


# ── proj 1. Комплементарний ШІМ із мертвим часом ────────────────────────────
def fig_deadtime_timing():
    W, H = 720, 360
    f = [text(W / 2, 26, "Комплементарний ШІМ із мертвим часом", size=16, bold=True)]

    x0, x1 = 130, 660          # межі осей часу
    yPWM, yHO, yLO = 92, 178, 264
    amp = 30                   # висота імпульсу
    e1, e2 = 250, 470          # положення фронтів ШІМ (вгору на e1, вниз на e2)
    dt = 26                    # ширина мертвого часу в пікселях

    # рожеві смуги мертвого часу (вертикальні, крізь HO/LO)
    for ex in (e1, e2):
        f.append(rect(ex, 70, dt, 224, fill="#fdeeee", stroke="none", sw=0, rx=0))

    # підписи рядів
    for label, y in (("ШІМ", yPWM), ("HO (верх)", yHO), ("LO (низ)", yLO)):
        f.append(text(x0 - 12, y + 4, label, size=12, anchor="end", bold=True))

    # ШІМ: високий між e1..e2
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, yPWM + amp, e1, yPWM + amp, e1, yPWM - amp, e2, yPWM - amp, e2, yPWM + amp, x1, yPWM + amp, NEG))
    # HO: відкритий після паузи від e1, закритий на e2 (повторює ШІМ, але фронт угору зсунутий праворуч)
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, yHO + amp, e1 + dt, yHO + amp, e1 + dt, yHO - amp, e2, yHO - amp, e2, yHO + amp, x1, yHO + amp, FIELD))
    # LO: інверсний; високий поза інтервалом ШІМ, фронт угору (після e2) зсунутий праворуч
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, yLO - amp, e1, yLO - amp, e1, yLO + amp, e2 + dt, yLO + amp, e2 + dt, yLO - amp, x1, yLO - amp, POS))

    # підписи мертвого часу
    for ex in (e1, e2):
        f.append(text(ex + dt / 2, 64, "мертвий час", size=11, color=POS, bold=True, anchor="middle"))
        f.append(text(ex + dt / 2, 312, "обидва закриті", size=11, anchor="middle"))

    f.append(text(W / 2, 344,
                  "На кожному фронті ШІМ спершу ЗАКРИВАЮТЬ один ключ, чекають паузу, аж тоді відкривають інший.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "deadtime-timing.svg"), W, H, *f)


# ── proj 2. Компроміс мертвого часу: замало / якраз / забагато ──────────────
def fig_tradeoff():
    W, H = 700, 300
    f = [text(W / 2, 28, "Мертвий час: замало небезпечно, забагато марнотратно", size=16, bold=True)]

    bx, by, bw, bh = 80, 150, 540, 44
    seg = bw / 3.0
    # три зони
    f.append(rect(bx, by, seg, bh, fill="#fdeeee", stroke="none", sw=0, rx=0))
    f.append(rect(bx + seg, by, seg, bh, fill="#eef6ef", stroke="none", sw=0, rx=0))
    f.append(rect(bx + 2 * seg, by, seg, bh, fill="#fff3e0", stroke="none", sw=0, rx=0))
    f.append(rect(bx, by, bw, bh, fill="none", stroke=INK, sw=1.4))

    f.append(text(bx + seg / 2, by + 28, "ЗАМАЛО", size=12, color=POS, bold=True))
    f.append(text(bx + seg * 1.5, by + 28, "ЯКРАЗ", size=12, color=FIELD, bold=True))
    f.append(text(bx + seg * 2.5, by + 28, "ЗАБАГАТО", size=12, color="#c98a14", bold=True))

    # вісь зростання мертвого часу
    f.append(arrow(bx, 214, bx + bw, 214, color=INK, sw=1.6))
    f.append(text(bx + bw + 6, 218, "мертвий час →", size=10, anchor="start", bold=True))

    # пояснення над зонами
    f.append(text(bx + seg / 2, 134, "обидва прочинені → наскрізний струм", size=10, color=POS, anchor="middle"))
    f.append(text(bx + seg * 1.5, 134, "трохи більше за час вимикання", size=10, color=FIELD, anchor="middle"))
    f.append(text(bx + seg * 2.5, 134, "body-діод гріється, спотворення", size=10, color="#c98a14", anchor="middle"))

    f.append(text(W / 2, 256, "Правило: мертвий час трохи довший за найгірший час вимикання ключа (Qgd, Rg, темп.).",
                  size=11, anchor="middle"))
    f.append(text(W / 2, 280, "На практиці — апаратний комплементарний ШІМ із програмованим мертвим часом, не дві ніжки вручну.",
                  size=10, color=MUTED, italic=True, anchor="middle"))
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_board_anatomy()
    fig_pinout_wiring()
    fig_deadtime_timing()
    fig_tradeoff()
    print("Готово: 4 фігури вставок у", IMG)
