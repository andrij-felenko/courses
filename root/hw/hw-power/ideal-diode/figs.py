# -*- coding: utf-8 -*-
"""Фігури теми «Ідеальний діод». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def mosfet_body_diode(cx, cy, on, label_top, label_bot):
    """Спрощений N-MOSFET зі стрілкою body-діода source→drain (унизу).
    on=True — канал відкритий (зелений потовщений шлях), False — закритий."""
    parts = []
    # корпус транзистора
    box, w, h = textbox(cx, cy, "MOSFET", size=13, min_w=110)
    parts.append(box)
    # вивід-витік (source, зверху) і стік (drain, знизу)
    parts.append(line(cx, cy - h / 2 - 26, cx, cy - h / 2, sw=2))
    parts.append(line(cx, cy + h / 2, cx, cy + h / 2 + 26, sw=2))
    parts.append(text(cx + 40, cy - h / 2 - 12, label_top, size=11, color=MUTED, anchor="start"))
    parts.append(text(cx + 40, cy + h / 2 + 18, label_bot, size=11, color=MUTED, anchor="start"))
    # канал: відкритий — зелений, закритий — сірий пунктир
    if on:
        parts.append(line(cx - 28, cy, cx + 28, cy, color=FIELD, sw=6))
        parts.append(text(cx, cy - 4, "канал", size=10, color=BG))
    else:
        parts.append(line(cx - 28, cy, cx + 28, cy, color=MUTED, sw=2, dash="4 4"))
    # body-діод збоку: стрілка від витока (вгорі) до стока (внизу) = вперед
    dx = cx + w / 2 + 30
    parts.append(line(cx, cy - h / 2 - 14, dx, cy - h / 2 - 14, color=MUTED, sw=1.4))
    parts.append(line(dx, cy - h / 2 - 14, dx, cy + h / 2 + 14, color=MUTED, sw=1.4))
    parts.append(line(dx, cy + h / 2 + 14, cx, cy + h / 2 + 14, color=MUTED, sw=1.4))
    # символ діода (трикутник + риска) посередині бічної гілки, вістрям униз = source→drain
    dy = cy
    tri = '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        dx - 9, dy - 9, dx + 9, dy - 9, dx, dy + 7, FILL, INK)
    parts.append(tri)
    parts.append(line(dx - 10, dy + 7, dx + 10, dy + 7, color=INK, sw=2))
    parts.append(text(dx + 16, dy + 4, "body", size=10, color=MUTED, anchor="start"))
    return "".join(parts), w, h


def fig_startup_handoff():
    """Двофазний старт: спершу веде body-діод (велике падіння),
    потім контролер відкриває канал і шунтує діод (мікровольти)."""
    W, H = 760, 430
    parts = []

    # ── ліва панель: фаза 1 — канал закритий, струм крізь body-діод ──
    lx = 195
    parts.append(textbox(lx, 60, "Фаза 1 · канал ще закритий", size=14, bold=True, min_w=320)[0])
    # «плюс» входу зверху, навантаження знизу
    parts.append(plus(lx, 110))
    parts.append(text(lx + 22, 114, "вхід / анод", size=11, color=POS, anchor="start"))
    m1, w1, h1 = mosfet_body_diode(lx, 215, on=False,
                                   label_top="витік (source)", label_bot="стік (drain)")
    parts.append(m1)
    parts.append(line(lx, 124, lx, 215 - h1 / 2 - 26, sw=2))
    parts.append(line(lx, 215 + h1 / 2 + 26, lx, 360, sw=2))
    parts.append(fitbox(lx - 70, 360, 140, 34, "навантаження", size=12))
    # підпис струму крізь діод
    parts.append(text(lx - 150, 215, "струм →", size=12, color=POS, anchor="start"))
    parts.append(textbox(lx - 95, 250, "≈ 0.7 В\nна body-діоді", size=11, fill="#fdecea", stroke=POS)[0])

    # ── розділювач + стрілка переходу ──
    parts.append(line(390, 80, 390, 380, color=MUTED, sw=1, dash="3 5"))
    parts.append(arrow(360, 215, 420, 215, color=FIELD, sw=2.4))
    parts.append(text(390, 200, "контролер", size=10, color=FIELD))
    parts.append(text(390, 240, "відкрив канал", size=10, color=FIELD))

    # ── права панель: фаза 2 — канал відкритий, діод зашунтовано ──
    rx = 565
    parts.append(textbox(rx, 60, "Фаза 2 · канал відкритий", size=14, bold=True, min_w=320)[0])
    parts.append(plus(rx, 110))
    parts.append(text(rx + 22, 114, "вхід / анод", size=11, color=POS, anchor="start"))
    m2, w2, h2 = mosfet_body_diode(rx, 215, on=True,
                                   label_top="витік (source)", label_bot="стік (drain)")
    parts.append(m2)
    parts.append(line(rx, 124, rx, 215 - h2 / 2 - 26, color=FIELD, sw=3))
    parts.append(line(rx, 215 + h2 / 2 + 26, rx, 360, color=FIELD, sw=3))
    parts.append(fitbox(rx - 70, 360, 140, 34, "навантаження", size=12))
    parts.append(text(rx - 150, 215, "струм →", size=12, color=FIELD, anchor="start"))
    parts.append(textbox(rx - 95, 250, "≈ 25 мВ\nна каналі", size=11, fill="#eafaf0", stroke=FIELD)[0])

    return render(os.path.join(IMG, "body-diode-handoff.svg"), W, H, *parts)


if __name__ == "__main__":
    print(fig_startup_handoff())
