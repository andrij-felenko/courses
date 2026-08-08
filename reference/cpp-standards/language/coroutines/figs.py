# -*- coding: utf-8 -*-
"""Фігури до теми «Корутини: призупинення функції й час життя кадру»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

DIE  = "#fdecea"   # те, що гине разом із кадром
LIVE = "#e8f6ee"   # те, що лишається живим
COLD = "#eef2fb"   # нейтральне
WARN = "#fff4d6"   # місце, де вирішується доля


# ── 1. Кадр на стеку проти кадру поза стеком ────────────────────────────────
def fig_frame_vs_stack():
    W, H = 1240, 480
    f = []

    # ліворуч: звичайний виклик
    f.append(text(280, 58, "звичайний виклик", size=15, bold=True))
    f.append(text(180, 94, "стек", size=12, color=MUTED))
    f.append(fitbox(120, 110, 320, 50, "кадр caller()", size=12, fill=LIVE, stroke=FIELD))
    f.append(fitbox(120, 176, 320, 66, "кадр read_numbers()\nлокальні змінні", size=12,
                    fill=DIE, stroke=POS))
    f.append(text(280, 292, "return знімає кадр зі стека —", size=12, color=POS))
    f.append(text(280, 318, "локальні змінні гинуть разом із ним", size=12, color=MUTED))
    f.append(text(280, 384, "спинитися посередині, віддати керування", size=12, color=MUTED))
    f.append(text(280, 410, "й лишитися живою — нема як", size=12, color=MUTED))

    f.append(line(560, 44, 560, 440, color=MUTED, sw=1, dash="6 5"))

    # праворуч: виклик корутини
    f.append(text(900, 58, "виклик корутини", size=15, bold=True))
    f.append(text(700, 94, "стек", size=12, color=MUTED))
    f.append(fitbox(600, 110, 200, 50, "кадр caller()", size=12, fill=LIVE, stroke=FIELD))
    f.append(fitbox(615, 176, 170, 44, "власник g", size=12, fill=LIVE, stroke=FIELD))

    f.append(text(1030, 94, "поза стеком", size=12, color=MUTED))
    f.append(fitbox(880, 110, 300, 200,
                    "кадр корутини\n\nоб'єкт promise\nкопії параметрів\nіндекс точки відновлення\nживі локальні",
                    size=12, fill=COLD, stroke=NEG))

    f.append(text(832, 182, "handle", size=11, color=MUTED))
    f.append(arrow(788, 200, 874, 200))

    f.append(text(900, 384, "кадр живе, поки його хтось не знищить,", size=12, color=MUTED))
    f.append(text(900, 410, "а стек caller() тим часом вільний", size=12, color=MUTED))

    render(os.path.join(OUT, 'frame-vs-stack.svg'), W, H, *f,
           title="Кадр звичайного виклику й кадр корутини")


# ── 2. Що лежить у кадрі й навіщо там індекс ───────────────────────────────
def fig_frame_layout():
    W, H = 1240, 500
    f = []

    f.append(text(300, 56, "тіло, розрізане точками призупинення", size=15, bold=True))
    f.append(fitbox(90, 88, 420, 54, "сегмент 0:  відкрити файл, прочитати рядок",
                    size=12, fill=COLD))
    f.append(text(300, 164, "co_yield x", size=12, color=POS))
    f.append(fitbox(90, 182, 420, 54, "сегмент 1:  прочитати наступний рядок",
                    size=12, fill=COLD))
    f.append(text(300, 258, "co_yield y", size=12, color=POS))
    f.append(fitbox(90, 276, 420, 54, "сегмент 2:  закрити файл, завершитися",
                    size=12, fill=COLD))

    f.append(text(900, 56, "кадр корутини", size=15, bold=True))
    f.append(rect(690, 80, 440, 300, fill=BG, stroke=NEG))
    f.append(fitbox(712, 100, 396, 44, "об'єкт promise", size=12, fill=LIVE, stroke=FIELD))
    f.append(fitbox(712, 156, 396, 44, "копії параметрів", size=12, fill=COLD))
    f.append(fitbox(712, 212, 396, 44, "індекс точки відновлення:  1", size=12,
                    fill=WARN, stroke=POS))
    f.append(fitbox(712, 268, 396, 44, "локальні, що живуть через призупинення",
                    size=12, fill=COLD))
    f.append(fitbox(712, 324, 396, 44, "вказівники resume / destroy", size=12, fill=COLD))

    f.append(text(610, 196, "куди повертати керування", size=11, color=MUTED))
    f.append(arrow(708, 234, 516, 214))

    f.append(text(620, 442,
                  "у кадрі лежить лише те, що переживає призупинення;",
                  size=12, color=MUTED))
    f.append(text(620, 468,
                  "решта живе у звичайному кадрі виклику resume()",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'frame-layout.svg'), W, H, *f,
           title="Вміст кадру корутини")


# ── 3. Протокол очікувача ──────────────────────────────────────────────────
def fig_await_protocol():
    W, H = 1180, 550
    f = []

    f.append(text(590, 50, "що насправді робить co_await e", size=15, bold=True))

    f.append(fitbox(310, 76, 560, 46,
                    "з e добувають очікувача a (await_transform, operator co_await)",
                    size=11, fill=COLD))
    f.append(arrow(590, 122, 590, 146))
    f.append(fitbox(310, 148, 560, 46,
                    "a.await_ready() → true: керування нікуди не віддають",
                    size=12, fill=LIVE, stroke=FIELD))
    f.append(arrow(590, 194, 590, 218))
    f.append(fitbox(310, 220, 560, 60,
                    "інакше: індекс точки відновлення записано в кадр —\nкорутина призупинена, кадр цілий",
                    size=12, fill=WARN, stroke=POS))
    f.append(arrow(590, 280, 590, 304))
    f.append(fitbox(310, 306, 560, 62,
                    "a.await_suspend(h) — єдина мить, коли віддають handle\nvoid або false: назад до того, хто відновлював\nінший handle: керування прямо в ту корутину",
                    size=11, fill=COLD))
    f.append(arrow(590, 368, 590, 392))
    f.append(fitbox(310, 394, 560, 46, "… чекання … аж поки хтось покличе h.resume()",
                    size=12, fill=COLD, stroke=MUTED))
    f.append(arrow(590, 440, 590, 464))
    f.append(fitbox(310, 466, 560, 46,
                    "a.await_resume() — її результат і є значення виразу co_await",
                    size=12, fill=LIVE, stroke=FIELD))

    render(os.path.join(OUT, 'await-protocol.svg'), W, H, *f,
           title="Протокол co_await")


# ── 4. Розвилка на final_suspend ───────────────────────────────────────────
def fig_final_suspend():
    W, H = 1180, 440
    f = []

    f.append(text(590, 50, "тіло дійшло кінця: co_await promise.final_suspend()",
                  size=14, bold=True))
    f.append(fitbox(430, 72, 320, 46, "кінець тіла корутини", size=12, fill=COLD))

    f.append(arrow(560, 118, 340, 166))
    f.append(arrow(620, 118, 840, 166))

    f.append(fitbox(120, 170, 440, 50, "повертає suspend_never", size=12,
                    fill=DIE, stroke=POS))
    f.append(fitbox(120, 238, 440, 92,
                    "кадр знищує сам себе\nhandle одразу висячий\nрезультат із promise вже не прочитати",
                    size=12, fill=DIE, stroke=POS))

    f.append(fitbox(620, 170, 440, 50, "повертає suspend_always", size=12,
                    fill=LIVE, stroke=FIELD))
    f.append(fitbox(620, 238, 440, 92,
                    "кадр лишається живим\nзначення й виняток у promise доступні\nхтось мусить покликати h.destroy()",
                    size=12, fill=LIVE, stroke=FIELD))

    f.append(text(590, 384,
                  "саме тут вирішується, хто володіє кадром — і саме тут беруться витоки",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'final-suspend.svg'), W, H, *f,
           title="Розвилка на final_suspend")


if __name__ == '__main__':
    fig_frame_vs_stack()
    fig_frame_layout()
    fig_await_protocol()
    fig_final_suspend()
    print("ok")
