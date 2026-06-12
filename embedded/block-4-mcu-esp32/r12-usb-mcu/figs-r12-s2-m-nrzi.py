# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 4.12.2m — «NRZI і біт-стафінг».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r12-2m-1-nrzi.svg      — часова діаграма NRZI: біт 0 перемикає, біт 1 лишає
  fig-r12-2m-2-stuffing.svg  — порівняння без стафінгу і зі стафінгом
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

ACCENT  = "#e67e22"   # помаранчевий для службового стаф-біта
DANGER  = "#c0392b"   # червоний для «втрата такту»
OK      = "#27ae60"   # зелений для «є перехід»
BIT_BG  = "#eaf0fd"   # фон рядка бітів
WAVE_J  = "#2457d6"   # рівень J (NEG)
WAVE_K  = "#c0392b"   # рівень K (POS)


# ── Фігура 1: NRZI часова діаграма ──────────────────────────────────────────

def fig1_nrzi():
    W, H = 860, 320
    frags = []

    # Заголовок
    tb, _, _ = textbox(W // 2, 26,
                       "NRZI: біт 0 → перемикання лінії, біт 1 → стан не змінюється",
                       size=13, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    # Бітовий рядок для діаграми (індекси: 0=ліво)
    # Рядок: 1  0  0  1  1  1  0
    bits = [1, 0, 0, 1, 1, 1, 0]
    n = len(bits)

    LEFT  = 80    # ліво осі (де починається діаграма)
    RIGHT = W - 40
    TOP_BITS = 65   # y-середина рядка бітів
    TOP_WAVE = 180  # y-середина хвилі
    BIT_H  = 34
    WAVE_H = 70    # амплітуда хвилі (від середини до краю)

    cell_w = (RIGHT - LEFT) / n

    # ── Рядок бітів ─────────────────────────────────────────────────────────
    # Фон рядка
    frags.append(rect(LEFT, TOP_BITS - BIT_H // 2 - 2, RIGHT - LEFT, BIT_H + 4,
                      fill=BIT_BG, stroke=MUTED, sw=1, rx=4))
    frags.append(text(LEFT - 8, TOP_BITS + 5, "біти:", size=13, color=INK, anchor="end"))

    for i, b in enumerate(bits):
        cx = LEFT + (i + 0.5) * cell_w
        col = WAVE_K if b == 0 else WAVE_J
        frags.append(text(cx, TOP_BITS + 5, str(b), size=17, color=col, bold=True))

    # ── Часова вісь (горизонтальна лінія) ───────────────────────────────────
    frags.append(arrow(LEFT, TOP_WAVE, RIGHT + 10, TOP_WAVE, color=MUTED, sw=1.2))
    frags.append(text(RIGHT + 18, TOP_WAVE + 4, "t", size=13, color=MUTED, anchor="start", italic=True))

    # ── Лінії роздільників бітів (вертикальні) ──────────────────────────────
    for i in range(n + 1):
        x = LEFT + i * cell_w
        frags.append(line(x, TOP_BITS - BIT_H // 2 - 2,
                          x, TOP_WAVE + WAVE_H + 20,
                          color=MUTED, sw=0.8, dash="3,3"))

    # ── Ступінчаста хвиля NRZI ──────────────────────────────────────────────
    # Стартовий рівень: J (вище = менше y)
    J_Y = TOP_WAVE - WAVE_H // 2   # J = вище
    K_Y = TOP_WAVE + WAVE_H // 2   # K = нижче
    level = J_Y   # старт у J

    segments = []  # список (x1, y, x2)  горизонтальних відрізків
    transitions = []  # x де є перехід

    x = LEFT
    for i, b in enumerate(bits):
        x_end = LEFT + (i + 1) * cell_w
        segments.append((x, level, x_end, level))
        if b == 0:
            # перехід на межі наступного біта
            transitions.append((x_end, level, J_Y if level == K_Y else K_Y))
            level = J_Y if level == K_Y else K_Y
        x = x_end

    # Малювати горизонтальні відрізки хвилі
    for (x1, y1, x2, y2) in segments:
        frags.append(line(x1, y1, x2, y1, color=WAVE_J, sw=2.5))

    # Малювати вертикальні переходи
    for (xv, y_from, y_to) in transitions:
        frags.append(line(xv, y_from, xv, y_to, color=WAVE_K, sw=2.5))

    # ── Підписи J / K ────────────────────────────────────────────────────────
    frags.append(text(LEFT - 8, J_Y + 4, "J", size=13, color=WAVE_J, anchor="end", bold=True))
    frags.append(text(LEFT - 8, K_Y + 4, "K", size=13, color=WAVE_K, anchor="end", bold=True))
    # горизонтальні штрихові еталонні лінії
    frags.append(line(LEFT - 4, J_Y, RIGHT, J_Y, color=WAVE_J, sw=0.6, dash="4,4"))
    frags.append(line(LEFT - 4, K_Y, RIGHT, K_Y, color=WAVE_K, sw=0.6, dash="4,4"))

    # ── Мітки «перехід» / «без переходу» ────────────────────────────────────
    for i, b in enumerate(bits):
        cx = LEFT + (i + 0.5) * cell_w
        if b == 0:
            frags.append(text(cx, TOP_WAVE + WAVE_H // 2 + 28,
                               "перехід", size=11, color=OK, anchor="middle"))
        else:
            frags.append(text(cx, TOP_WAVE + WAVE_H // 2 + 28,
                               "тиша", size=11, color=MUTED, anchor="middle"))

    # ── Виноска «проблема: три 1 підряд = рівна ділянка» ───────────────────
    # Позначити три одиниці (позиції 3,4,5) дужкою
    x_b3 = LEFT + 3 * cell_w
    x_b6 = LEFT + 6 * cell_w
    brace_y = TOP_WAVE - WAVE_H // 2 - 28
    frags.append(line(x_b3, brace_y + 6, x_b3, brace_y, color=DANGER, sw=1.5))
    frags.append(line(x_b3, brace_y, x_b6, brace_y, color=DANGER, sw=1.5))
    frags.append(line(x_b6, brace_y, x_b6, brace_y + 6, color=DANGER, sw=1.5))
    tb2, _, _ = textbox((x_b3 + x_b6) / 2, brace_y - 16,
                         "3 одиниці підряд — лінія не змінюється",
                         size=11, fill="#fdecea", stroke=DANGER, pad=6, color=DANGER)
    frags.append(tb2)

    render(os.path.join(OUT, "fig-r12-2m-1-nrzi.svg"), W, H, *frags,
           title=None)
    print("  fig-r12-2m-1-nrzi.svg — OK")


# ── Фігура 2: біт-стафінг (два waveform-доріжки) ────────────────────────────

def fig2_stuffing():
    W, H = 900, 400
    frags = []

    # Заголовок
    tb, _, _ = textbox(W // 2, 26,
                       "Біт-стафінг: вставлений 0 після 6 одиниць гарантує перехід",
                       size=13, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    LEFT  = 90
    RIGHT = W - 50
    cell_w_base = (RIGHT - LEFT) / 10  # базова ширина під 9 бітів + трохи

    # Бітовий вміст: 6 одиниць, потім один нуль (стаф), потім 1
    # (а) без стафінгу: 1 1 1 1 1 1 1   — сім одиниць
    # (б) зі стафінгом: 1 1 1 1 1 1 [0] 1 — шість одиниць, стаф-0, потім 1
    bits_raw     = [1, 1, 1, 1, 1, 1, 1]   # без стафінгу (7 одиниць)
    bits_stuffed = [1, 1, 1, 1, 1, 1, 0, 1] # зі стафінгом (6+стаф+1)

    TRACK_H = 72    # висота однієї доріжки
    WAVE_AMP = 24   # амплітуда від середини
    Y_A = 105       # середина верхньої доріжки
    Y_B = 255       # середина нижньої доріжки

    def draw_waveform(bits, y_center, start_J=True, stuf_idx=None):
        """Намалювати NRZI waveform для списку бітів.
        stuf_idx — індекс службового стаф-біта (виділяється кольором)."""
        n = len(bits)
        cell_w = (RIGHT - LEFT) / n
        J_Y = y_center - WAVE_AMP
        K_Y = y_center + WAVE_AMP
        level = J_Y if start_J else K_Y
        segs = []
        trans = []
        x = LEFT
        for i, b in enumerate(bits):
            x_end = LEFT + (i + 1) * cell_w
            segs.append((x, level, x_end, i))
            if b == 0:
                new_level = J_Y if level == K_Y else K_Y
                trans.append((x_end, level, new_level, i))
                level = new_level
            x = x_end

        # горизонтальні відрізки
        for (x1, y1, x2, idx) in segs:
            col = ACCENT if stuf_idx is not None and idx == stuf_idx else WAVE_J
            frags.append(line(x1, y1, x2, y1, color=col, sw=2.5))

        # вертикальні переходи
        for (xv, y_from, y_to, idx) in trans:
            col = ACCENT if stuf_idx is not None and idx == stuf_idx else WAVE_K
            frags.append(line(xv, y_from, xv, y_to, color=col, sw=2.5))

        # роздільники
        for i in range(n + 1):
            x = LEFT + i * (RIGHT - LEFT) / n
            frags.append(line(x, y_center - WAVE_AMP - 10,
                               x, y_center + WAVE_AMP + 10,
                               color=MUTED, sw=0.7, dash="3,3"))

        # рядок бітів
        for i, b in enumerate(bits):
            cx = LEFT + (i + 0.5) * (RIGHT - LEFT) / n
            if stuf_idx is not None and i == stuf_idx:
                col2 = ACCENT
                label = "0*"
            else:
                col2 = WAVE_K if b == 0 else WAVE_J
                label = str(b)
            frags.append(text(cx, y_center - WAVE_AMP - 22,
                               label, size=16, color=col2, bold=True))

        return J_Y, K_Y

    # ── Доріжка (а): без стафінгу ───────────────────────────────────────────
    frags.append(text(LEFT - 8, Y_A - WAVE_AMP - 30,
                      "(а) без стафінгу:", size=13, color=INK, anchor="end", bold=True))
    J_A, K_A = draw_waveform(bits_raw, Y_A)

    # Фон доріжки (а) — рожева небезпечна зона
    frags.append(rect(LEFT, Y_A - TRACK_H // 2 + 6,
                      RIGHT - LEFT, TRACK_H - 6,
                      fill="#fff5f5", stroke=DANGER, sw=1, rx=4))
    # Перемалювати хвилю поверх фону
    draw_waveform(bits_raw, Y_A)

    # Підпис «приймач втрачає такт»
    tb_a, _, _ = textbox(RIGHT - 95, Y_A,
                          "рівна лінія —\nприймач губить такт",
                          size=11, fill="#fdecea", stroke=DANGER, pad=6, color=DANGER)
    frags.append(tb_a)

    # ── Доріжка (б): зі стафінгом ───────────────────────────────────────────
    frags.append(text(LEFT - 8, Y_B - WAVE_AMP - 30,
                      "(б) зі стафінгом:", size=13, color=INK, anchor="end", bold=True))
    # Фон доріжки (б) — зелена безпечна зона
    frags.append(rect(LEFT, Y_B - TRACK_H // 2 + 6,
                      RIGHT - LEFT, TRACK_H - 6,
                      fill="#f0faf4", stroke=OK, sw=1, rx=4))
    J_B, K_B = draw_waveform(bits_stuffed, Y_B, stuf_idx=6)

    # Підпис стаф-біта (виноска)
    n_s = len(bits_stuffed)
    cx_stuf = LEFT + 6.5 * (RIGHT - LEFT) / n_s
    tb_s, _, _ = textbox(cx_stuf, Y_B + WAVE_AMP + 34,
                          "вставлений 0*\n(викидається\nприймачем)",
                          size=11, fill="#fff8ec", stroke=ACCENT, pad=6, color=ACCENT)
    frags.append(tb_s)
    # стрілка вгору до стаф-біта
    frags.append(arrow(cx_stuf, Y_B + WAVE_AMP + 8, cx_stuf, Y_B + WAVE_AMP + 2,
                       color=ACCENT, sw=1.4))

    # ── Числовий блок 7 × 83.3 нс ────────────────────────────────────────────
    info_x = W - 15
    info_y = H - 55
    tb_n, _, _ = textbox(info_x - 85, info_y,
                          "FS: 12 Мбіт/с\n1 біт ≈ 83.3 нс\n7 біт ≈ 583 нс (макс. тиша)",
                          size=11, fill=FILL, stroke=MUTED, pad=7, color=INK)
    frags.append(tb_n)

    render(os.path.join(OUT, "fig-r12-2m-2-stuffing.svg"), W, H, *frags,
           title=None)
    print("  fig-r12-2m-2-stuffing.svg — OK")


# ── Точка входу ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Генерую фігури NRZI / біт-стафінг…")
    fig1_nrzi()
    fig2_stuffing()
    print("Готово.")
