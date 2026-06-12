# -*- coding: utf-8 -*-
"""
Фігури для вставки r12-s4-a-frames.md
Рис. 4.12.4a.1 — Часова шкала Full-Speed-шини: фрейми 1 мс, IN-токен раз на bInterval

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.4a.1 — Часова шкала FS-шини: фрейми 1 мс, interrupt-polling раз на 8
# ══════════════════════════════════════════════════════════════════════════════
def fig1_frame_schedule():
    W, H = 880, 390
    frags = []

    # ─── Вісь часу ────────────────────────────────────────────────────────────
    axis_x0 = 50
    axis_x1 = 830
    axis_y  = 200
    frags.append(arrow(axis_x0, axis_y, axis_x1, axis_y, color=INK, sw=2.0))
    frags.append(text(axis_x1 + 10, axis_y + 5, "t", size=15, color=INK, anchor="middle", bold=True))

    # ─── Фрейми (9 штук: 0..8 мс, тобто 8 фреймів + правий край) ─────────────
    n_frames = 8
    frame_w = 90          # ширина одного фрейму у пікселях
    frame_y_top = 108     # верхній край фреймів
    frame_h = 74          # висота блоків

    frame_x0 = axis_x0 + 20   # лівий край фрейму 0

    FRAME_FILL  = "#f0f4fa"
    FRAME_BULK  = "#e8f4ec"    # bulk/control — зеленувата
    FRAME_EMPTY = "#fafafa"    # порожній (для цієї точки)
    INTR_COLOR  = NEG          # interrupt IN-токен
    NAK_COLOR   = MUTED

    for i in range(n_frames):
        fx = frame_x0 + i * frame_w
        # SOF-мітка на межах фреймів
        frags.append(line(fx, axis_y - 8, fx, axis_y + 8, color=INK, sw=1.8))
        frags.append(text(fx, axis_y + 22, "%d мс" % i, size=11, color=MUTED, anchor="middle"))

        # Блок фрейму над віссю
        fill = FRAME_FILL
        frags.append(rect(fx, frame_y_top, frame_w - 2, frame_h,
                          fill=fill, stroke=LINE, sw=1.2, rx=4))

        # У кожному фреймі: SOF-пакет зліва (маленький)
        sof_w = 14
        frags.append(rect(fx + 2, frame_y_top + 4, sof_w, frame_h - 8,
                          fill="#ffe9cc", stroke="#c8802a", sw=1.0, rx=3))
        frags.append(text(fx + 2 + sof_w / 2, frame_y_top + frame_h / 2 - 3,
                          "SOF", size=8, color="#8a5000", anchor="middle"))

        # Заповнення решти фрейму
        if i == 0:
            # Interrupt IN-токен + відповідь пристрою
            in_x = fx + sof_w + 6
            in_w = 34
            frags.append(rect(in_x, frame_y_top + 4, in_w, frame_h - 8,
                              fill="#ddeeff", stroke=INTR_COLOR, sw=1.5, rx=3))
            tb, _, _ = textbox(in_x + in_w / 2, frame_y_top + frame_h / 2 - 3,
                               "IN\n→ DATA", size=9,
                               fill="#ddeeff", stroke=INTR_COLOR, sw=1.2)
            frags.append(tb)
            # Bulk/control доповнення
            bulk_x = in_x + in_w + 4
            frags.append(rect(bulk_x, frame_y_top + 4, frame_w - sof_w - in_w - 16,
                              frame_h - 8, fill=FRAME_BULK, stroke=FIELD, sw=1.0, rx=3))
            frags.append(text(bulk_x + (frame_w - sof_w - in_w - 16) / 2,
                              frame_y_top + frame_h / 2 - 3,
                              "bulk/ctrl", size=8, color=FIELD, anchor="middle"))
        elif i == n_frames - 1:
            # Останній фрейм (8 мс) — знову interrupt IN-токен
            in_x = fx + sof_w + 6
            in_w = 34
            frags.append(rect(in_x, frame_y_top + 4, in_w, frame_h - 8,
                              fill="#ddeeff", stroke=INTR_COLOR, sw=1.5, rx=3))
            tb, _, _ = textbox(in_x + in_w / 2, frame_y_top + frame_h / 2 - 3,
                               "IN\n→ DATA", size=9,
                               fill="#ddeeff", stroke=INTR_COLOR, sw=1.2)
            frags.append(tb)
            bulk_x = in_x + in_w + 4
            frags.append(rect(bulk_x, frame_y_top + 4, frame_w - sof_w - in_w - 16,
                              frame_h - 8, fill=FRAME_BULK, stroke=FIELD, sw=1.0, rx=3))
            frags.append(text(bulk_x + (frame_w - sof_w - in_w - 16) / 2,
                              frame_y_top + frame_h / 2 - 3,
                              "bulk/ctrl", size=8, color=FIELD, anchor="middle"))
        else:
            # Проміжний фрейм: для цієї interrupt-точки — NAK або просто bulk
            # Показуємо або «NAK» (нема даних) або bulk-трафік
            if i % 3 == 1:
                # Показати «хост не питає» — проміжний фрейм порожній для interrupt
                frags.append(rect(fx + sof_w + 6, frame_y_top + 4,
                                  frame_w - sof_w - 12, frame_h - 8,
                                  fill=FRAME_BULK, stroke=FIELD, sw=1.0, rx=3))
                frags.append(text(fx + sof_w + 6 + (frame_w - sof_w - 12) / 2,
                                  frame_y_top + frame_h / 2 - 3,
                                  "bulk/ctrl", size=8, color=FIELD, anchor="middle"))
            else:
                frags.append(rect(fx + sof_w + 6, frame_y_top + 4,
                                  frame_w - sof_w - 12, frame_h - 8,
                                  fill=FRAME_EMPTY, stroke=MUTED, sw=1.0, rx=3, ))
                frags.append(text(fx + sof_w + 6 + (frame_w - sof_w - 12) / 2,
                                  frame_y_top + frame_h / 2 - 3,
                                  "bulk/ctrl", size=8, color=MUTED, anchor="middle"))

    # Права межа 8 мс
    fx_end = frame_x0 + n_frames * frame_w
    frags.append(line(fx_end, axis_y - 8, fx_end, axis_y + 8, color=INK, sw=1.8))
    frags.append(text(fx_end, axis_y + 22, "8 мс", size=11, color=MUTED, anchor="middle"))

    # ─── Стрілки IN-токенів вгорі над фреймами 0 і 8 ─────────────────────────
    arrow_y_tip = frame_y_top - 6
    arrow_y_top = frame_y_top - 48

    for i_frame in (0, n_frames):
        ax = frame_x0 + i_frame * frame_w + 30
        frags.append(arrow(ax, arrow_y_top + 18, ax, arrow_y_tip, color=INTR_COLOR, sw=2.0))
        tb, _, _ = textbox(ax, arrow_y_top,
                           "IN-токен", size=10,
                           fill="#ddeeff", stroke=INTR_COLOR, sw=1.4)
        frags.append(tb)

    # ─── Двостороння стрілка bInterval = 8 мс ────────────────────────────────
    brk_y = frame_y_top - 72
    bx0 = frame_x0 + 2
    bx1 = frame_x0 + n_frames * frame_w - 2
    frags.append(line(bx0, brk_y, bx1, brk_y, color=POS, sw=2.0))
    frags.append(arrow(bx0, brk_y, bx0 - 2, brk_y, color=POS, sw=2.0))
    frags.append(arrow(bx1, brk_y, bx1 + 2, brk_y, color=POS, sw=2.0))
    # Підпис у центрі
    mid_bx = (bx0 + bx1) / 2
    tb_bi, _, _ = textbox(mid_bx, brk_y - 20,
                          "bInterval = 8 фреймів = 8 мс → 125 Гц",
                          size=12, fill="#fdecea", stroke=POS, sw=1.6, bold=True)
    frags.append(tb_bi)

    # ─── Підпис «NAK» між опитуваннями (пояснення) ───────────────────────────
    mid_frame_x = frame_x0 + 4 * frame_w + frame_w / 2
    tb_nak, _, _ = textbox(mid_frame_x, frame_y_top + frame_h + 42,
                           "Проміжні фрейми:\nхост не шле IN цій точці.\nПристрій нічого не відповідає.",
                           size=10, fill=FILL, stroke=MUTED, sw=1.2)
    frags.append(tb_nak)

    # ─── Легенда ──────────────────────────────────────────────────────────────
    leg_x = 56
    leg_y = 312
    items = [
        ("#ffe9cc", "#c8802a", "SOF (Start-of-Frame)"),
        ("#ddeeff", INTR_COLOR, "IN-токен interrupt"),
        (FRAME_BULK, FIELD, "bulk / control трафік"),
    ]
    for j, (lf, ls, lbl) in enumerate(items):
        lx = leg_x + j * 250
        frags.append(rect(lx, leg_y, 18, 14, fill=lf, stroke=ls, sw=1.4, rx=3))
        frags.append(text(lx + 24, leg_y + 11, lbl, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig-r12-s4a-1-frame-schedule.svg"), W, H, *frags,
           title="Рис. 4.12.4a.1. Часова шкала FS-шини: фрейми по 1 мс, опитування раз на bInterval")


if __name__ == "__main__":
    fig1_frame_schedule()
    print("OK: fig-r12-s4a-1-frame-schedule.svg")
