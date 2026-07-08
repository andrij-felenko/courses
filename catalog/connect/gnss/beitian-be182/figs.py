# -*- coding: utf-8 -*-
"""Фігури об'єкта «Beitian BE-182» (catalog/connect/gnss). Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що всередині модуля — блок-схема ──────────────────────────────
# Антена ловить сигнал → LNA підсилює → чип M10 рахує координати → UART віддає
# рядок мікроконтролеру. Живлення 5 В.  Показуємо поділ праці «плата все робить».
def fig_block():
    W, H = 780, 380
    parts = []

    # підпис-джерело сигналу (окремим рядком, високо, з великим відступом)
    parts.append(text(390, 52, "сигнали супутників (GPS · BeiDou · Galileo · QZSS)",
                      12, MUTED, "middle"))
    # три «промені» до однієї точки над антеною — повз усі написи
    ant_top_x, ant_top_y = 195, 132
    for sx in (120, 195, 270):
        parts.append(line(sx, 66, ant_top_x, ant_top_y, color=MUTED, sw=1.0, dash="3,4"))

    # межа модуля — пунктирна рамка (нижче, щоб промені не чіпали заголовок)
    parts.append(rect(120, 134, 470, 190, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(355, 154, "модуль BE-182 (одна плата)", 12, MUTED, "middle"))

    # антена (керамічна латка)
    parts.append(fitbox(140, 190, 110, 66, "керамічна\nлатка-антена\n+ LNA",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.6, color=INK, bold=True))
    # чип M10
    parts.append(fitbox(300, 188, 150, 74, "чип u-blox M10\n(UBX-M10050)\nрахує координати",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.8, color=INK, bold=True))
    parts.append(arrow(250, 223, 300, 223, color=NEG, sw=1.8))

    # UART назовні
    parts.append(fitbox(500, 198, 74, 54, "UART\nTX / RX",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.4, color=INK))
    parts.append(arrow(450, 225, 500, 225, color=NEG, sw=1.8))

    # MCU праворуч, за межею плати
    parts.append(fitbox(630, 190, 120, 66, "Ваш MCU /\nполітний\nконтролер",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
    parts.append(arrow(574, 216, 630, 216, color=NEG, sw=1.8))
    parts.append(arrow(630, 236, 574, 236, color=NEG, sw=1.8))
    parts.append(text(690, 278, "готові рядки\nз координатами", 10, MUTED, "middle"))

    # живлення знизу
    parts.append(line(175, 344, 545, 344, color=POS, sw=2.2))
    parts.append(text(355, 338, "живлення 3.6–5.5 В (типово 5 В)", 11, POS, "middle", bold=True))

    render(os.path.join(IMG, "block.svg"), W, H, *parts,
           title="Що всередині BE-182: чип сам рахує координати й віддає їх по UART")


# ── Фігура 2: підключення пін-у-пін (4 дроти) з перехрестям TX↔RX ───────────
# Головна пастка початківця: TX модуля йде на RX контролера, а не «однаково».
def fig_wiring():
    W, H = 720, 360
    parts = []

    # модуль зліва — 4 виводи
    mx, my, mw, mh = 90, 90, 150, 200
    parts.append(rect(mx, my, mw, mh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(mx + mw / 2, my - 14, "BE-182 (роз'єм)", 12, INK, "middle", bold=True))

    # контролер справа — 4 виводи
    cx, cy, cw, ch = 480, 90, 150, 200
    parts.append(rect(cx, cy, cw, ch, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(cx + cw / 2, cy - 14, "MCU / UART", 12, INK, "middle", bold=True))

    # ряди виводів: (модуль, колір-дроту, контролер, як з'єднати)
    ys = [my + 34, my + 88, my + 142, my + 190]

    def pin_left(y, label, col):
        parts.append(line(mx + mw, y, mx + mw + 16, y, color=col, sw=2.4))
        parts.append(circle(mx + mw + 16, y, 3.5, fill=col, stroke=INK, sw=1))
        parts.append(text(mx + mw - 10, y + 4, label, 12, col, "end", bold=True))

    def pin_right(y, label, col):
        parts.append(line(cx - 16, y, cx, y, color=col, sw=2.4))
        parts.append(circle(cx - 16, y, 3.5, fill=col, stroke=INK, sw=1))
        parts.append(text(cx + 12, y + 4, label, 12, col, "start", bold=True))

    # VCC — червоний, прямо
    pin_left(ys[0], "VCC", POS); pin_right(ys[0], "5V", POS)
    parts.append(line(mx + mw + 16, ys[0], cx - 16, ys[0], color=POS, sw=2.0))

    # GND — чорний, прямо
    pin_left(ys[1], "GND", INK); pin_right(ys[1], "GND", INK)
    parts.append(line(mx + mw + 16, ys[1], cx - 16, ys[1], color=INK, sw=2.0))

    # TX модуля → RX контролера (перехрест)
    pin_left(ys[2], "TX", NEG); pin_right(ys[3], "RX", NEG)
    parts.append(line(mx + mw + 16, ys[2], 360, ys[2], color=NEG, sw=2.0))
    parts.append(line(360, ys[2], 360, ys[3], color=NEG, sw=2.0))
    parts.append(line(360, ys[3], cx - 16, ys[3], color=NEG, sw=2.0))

    # RX модуля → TX контролера (перехрест)
    pin_left(ys[3], "RX", NEG); pin_right(ys[2], "TX", NEG)
    parts.append(line(mx + mw + 16, ys[3], 330, ys[3], color=NEG, sw=2.0))
    parts.append(line(330, ys[3], 330, ys[2], color=NEG, sw=2.0))
    parts.append(line(330, ys[2], cx - 16, ys[2], color=NEG, sw=2.0))

    # напис-пастка знизу
    parts.append(fitbox(230, 306, 260, 44,
                        "TX модуля → RX контролера,\nRX модуля → TX контролера.\nПереплутати = тиша.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Підключення 4 дротами: живлення прямо, TX і RX — навхрест")


# ── Фігура 3: холодний і гарячий старт — навіщо чисте небо ──────────────────
# Читач має зрозуміти, ЧОМУ перший fix довгий і чому в приміщенні нема координат.
def fig_startup():
    W, H = 720, 340
    parts = []

    # вісь-стрічка часу
    axis_y = 270
    parts.append(line(70, axis_y, 650, axis_y, color=INK, sw=2.0))
    parts.append(text(360, 308, "час від увімкнення →", 12, MUTED, "middle"))

    # холодний старт — довгий блок
    parts.append(rect(70, 160, 300, 42, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    parts.append(text(220, 186, "холодний старт ≈ 27 с", 12, POS, "middle", bold=True))
    parts.append(text(220, 130, "нема даних про супутники\n— модуль шукає з нуля",
                      11, INK, "middle"))
    # межові пунктири — тільки в проміжку між блоком і віссю, повз написи
    parts.append(line(70, 202, 70, axis_y, color=MUTED, sw=1.0, dash="3,4"))
    parts.append(line(370, 202, 370, axis_y, color=MUTED, sw=1.0, dash="3,4"))

    # гарячий старт — короткий блок
    parts.append(rect(430, 160, 42, 42, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=6))
    parts.append(text(451, 186, "1 с", 11, FIELD, "middle", bold=True))
    parts.append(text(560, 130, "гарячий старт: дані ще свіжі\n→ fix майже миттєвий",
                      11, INK, "middle"))
    parts.append(line(430, 202, 430, axis_y, color=MUTED, sw=1.0, dash="3,4"))

    # позначка «перший fix» — маркер НА осі, підпис ПІД віссю (не на пунктирі)
    parts.append(circle(370, axis_y, 5, fill=POS, stroke=INK, sw=1.2))
    parts.append(text(410, axis_y + 22, "← перший fix (холодний)", 10, POS, "start", bold=True))

    render(os.path.join(IMG, "startup.svg"), W, H, *parts,
           title="Перший fix довгий: модулю треба зловити супутники й прочитати їх орбіти")


# ── Фігура 4 (для вставки hist): як приймач усихав — від цеглини до чипа ─────
# Три віхи цивільного GPS: 1989 ручний прилад ($3000, ~700 г, 6 батарейок) →
# 2004 однокристальний SiRFstarIII (десятки $) → 2020 платформа u-blox M10
# (12 мВт, чип 35% менший). Наскрізна думка вставки: усихання ціни й споживання.
def fig_shrink():
    W, H = 820, 400
    parts = []

    # вісь-стрічка часу (роки), з великим запасом під написи
    axis_y = 320
    parts.append(line(70, axis_y, 760, axis_y, color=INK, sw=2.0))
    # підпис осі — праворуч від її кінця, щоб не сів на цифри-віхи знизу
    parts.append(text(766, axis_y - 10, "рік →", 12, MUTED, "end"))

    # три віхи: (x, рік, назва-заголовок, розмір-блоку, підпис-цифри)
    # розмір блоку навмисно спадає — око бачить «усихання»
    milestones = [
        (150, "1989", "ручний\nприлад",   118, "≈ 3000 $\n≈ 700 г · 6 батарейок\nтільки GPS"),
        (415, "2004", "один\nкристал",      78, "40–50 $\nодин чип\nмасовий ринок"),
        (680, "2020", "u-blox M10",         48, "12 мВт стеження\nчип на 35 % менший\n4 сузір'я разом"),
    ]

    for x, year, head, sz, note in milestones:
        # блок-«приймач» — квадрат, що зменшується зліва направо
        bx, by = x - sz / 2, axis_y - 30 - sz
        parts.append(fitbox(bx, by, sz, sz, head, size=11,
                            fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
        # позначка року НА осі
        parts.append(circle(x, axis_y, 5, fill=NEG, stroke=INK, sw=1.2))
        parts.append(line(x, by + sz, x, axis_y - 8, color=MUTED, sw=1.0, dash="3,4"))
        parts.append(text(x, axis_y + 22, year, 13, NEG, "middle", bold=True))
        # цифри-підпис ПІД віссю, з відступом, кожна віха у своїй колонці
        parts.append(text(x, axis_y + 46, note, 10, MUTED, "middle"))

    # стрілка «дешевшає й ощадливішає» над рядом, повз блоки
    parts.append(arrow(150, 70, 680, 70, color=FIELD, sw=2.0))
    parts.append(text(415, 58, "дешевше · ощадливіше · дрібніше", 12, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "shrink.svg"), W, H, *parts,
           title="Як цивільний приймач усихав: від приладу за 3000 $ до чипа за десятки")


fig_block()
fig_wiring()
fig_startup()
fig_shrink()
print("Done. SVG in", IMG)
