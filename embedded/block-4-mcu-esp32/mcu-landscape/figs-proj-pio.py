# -*- coding: utf-8 -*-
"""
Фігури для вставки r11-s5-a-pio.md  (⚙️ PIO зсередини)
  Рис. 4.11.5a.1 — Анатомія одного PIO-автомата
  Рис. 4.11.5a.2 — Три способи говорити з ніжками

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.5a.1 — Анатомія одного PIO-автомата
#   Потік зліва направо:  Ядро/DMA → TX FIFO → OSR → GPIO (out/side-set)
#   Зворотній шлях:       GPIO → ISR → RX FIFO → Ядро
#   Збоку: блок «програма (9 інструкцій)» і «дільник такту (clock divider)»
# ══════════════════════════════════════════════════════════════════════════════
def fig1_state_machine():
    W, H = 860, 420
    frags = []

    # ── Кольори для ролей ───────────────────────────────────────────────────
    C_CORE  = "#d6e4ff"   # ядро/DMA — синювате
    C_FIFO  = "#fff3cd"   # FIFO — жовтувате
    C_REG   = "#d4edda"   # зсувні регістри — зеленкувате
    C_GPIO  = "#f8d7da"   # GPIO — рожеве
    C_PROG  = "#e8d5f5"   # програма — фіолетове
    C_DIV   = "#fde8ce"   # дільник — помаранчеве
    STROKE  = "#555555"

    # ── Вертикальні центри двох шляхів ─────────────────────────────────────
    Y_FWD  = 155    # прямий шлях (TX)
    Y_BACK = 285    # зворотній шлях (RX)
    BH     = 68     # висота блоків

    # ── X-координати центрів (5 стовпців) ──────────────────────────────────
    XC = [80, 220, 380, 530, 690]   # Ядро/DMA | TX FIFO | OSR | GPIO | label
    # Для зворотнього: GPIO → ISR → RX FIFO → Ядро (зеркально)
    XC_B = [690, 570, 400, 245, 80]  # центри блоків назад (GPIO вже є, ISR, RX-FIFO, Ядро)
    # Нові X-центри для зворотнього рядка (не дублюємо GPIO і Ядро):
    X_ISR    = 560
    X_RXFIFO = 400

    # ─── ПРЯМИЙ ШЛЯХ ────────────────────────────────────────────────────────

    # 1. Ядро / DMA
    b, _, _ = textbox(XC[0], Y_FWD, "Ядро / DMA\n(TX-дані)", size=12,
                      fill=C_CORE, stroke=STROKE, sw=1.8, min_w=110)
    frags.append(b)

    # 2. TX FIFO
    b, _, _ = textbox(XC[1], Y_FWD, "TX FIFO\n(4 слова)", size=12,
                      fill=C_FIFO, stroke=STROKE, sw=1.8, min_w=110)
    frags.append(b)

    # 3. OSR (вихідний зсувний регістр)
    b, _, _ = textbox(XC[2], Y_FWD, "OSR\n(зсувний регістр,\nout shift reg)", size=12,
                      fill=C_REG, stroke=STROKE, sw=1.8, min_w=130)
    frags.append(b)

    # 4. GPIO (out + side-set pins)
    b, _, _ = textbox(XC[3], Y_FWD, "GPIO\nout / side-set\npins", size=12,
                      fill=C_GPIO, stroke=STROKE, sw=1.8, min_w=110)
    frags.append(b)

    # Стрілки прямого шляху
    frags.append(arrow(XC[0]+58, Y_FWD, XC[1]-58, Y_FWD, color=INK, sw=2))
    frags.append(arrow(XC[1]+58, Y_FWD, XC[2]-68, Y_FWD, color=INK, sw=2))
    frags.append(arrow(XC[2]+68, Y_FWD, XC[3]-58, Y_FWD, color=INK, sw=2))
    # до зовнішнього
    frags.append(arrow(XC[3]+58, Y_FWD, XC[3]+100, Y_FWD, color=INK, sw=2))
    frags.append(text(XC[3]+108, Y_FWD+4, "→ ніжки\nмікросхеми", size=11, anchor="start", color=MUTED))

    # ─── ЗВОРОТНІЙ ШЛЯХ (знизу, справа наліво) ───────────────────────────

    # GPIO (загальне з прямим — малюємо тільки заголовок знизу)
    frags.append(text(XC[3], Y_BACK - 12, "GPIO\nin pins", size=12, anchor="middle", color=INK, bold=True))
    frags.append(arrow(XC[3]+100, Y_BACK, XC[3]+58, Y_BACK, color=MUTED, sw=2))
    frags.append(text(XC[3]+108, Y_BACK+4, "← ніжки\n(вхід)", size=11, anchor="start", color=MUTED))

    # ISR (вхідний зсувний регістр)
    b, _, _ = textbox(X_ISR, Y_BACK, "ISR\n(зсувний регістр,\nin shift reg)", size=12,
                      fill=C_REG, stroke=STROKE, sw=1.8, min_w=130)
    frags.append(b)

    # RX FIFO
    b, _, _ = textbox(X_RXFIFO, Y_BACK, "RX FIFO\n(4 слова)", size=12,
                      fill=C_FIFO, stroke=STROKE, sw=1.8, min_w=110)
    frags.append(b)

    # Ядро (окремий прямокутник для RX-боку)
    b, _, _ = textbox(XC[0], Y_BACK, "Ядро / DMA\n(RX-дані)", size=12,
                      fill=C_CORE, stroke=STROKE, sw=1.8, min_w=110)
    frags.append(b)

    # Стрілки зворотнього шляху (справа наліво)
    frags.append(arrow(XC[3]-58, Y_BACK, X_ISR+68, Y_BACK, color=MUTED, sw=2))
    frags.append(arrow(X_ISR-68, Y_BACK, X_RXFIFO+58, Y_BACK, color=MUTED, sw=2))
    frags.append(arrow(X_RXFIFO-58, Y_BACK, XC[0]+58, Y_BACK, color=MUTED, sw=2))

    # ─── БІЧНІ БЛОКИ: програма і дільник такту ───────────────────────────

    # Блок «програма (9 інструкцій)» — зверху по центру
    b, _, _ = textbox(W//2 - 60, 52, "програма\n(9 інструкцій,\nside-set + затримки [n])", size=12,
                      fill=C_PROG, stroke="#7b4fa6", sw=1.8, min_w=180)
    frags.append(b)
    # Стрілка від програми до OSR (вниз)
    frags.append(arrow(W//2 - 60, 90, XC[2], Y_FWD - 36, color="#7b4fa6", sw=1.6))
    frags.append(text(W//2 + 20, 104, "керує зсувами\nі ніжками", size=10, anchor="start", color="#7b4fa6"))

    # Блок «дільник такту (clock divider)» — праворуч зверху
    b, _, _ = textbox(W - 90, 60, "дільник такту\n(clock divider)\n16.8-bit fractional", size=11,
                      fill=C_DIV, stroke="#b85c00", sw=1.8, min_w=170)
    frags.append(b)
    # Стрілка від дільника вниз (до GPIO-зони — показує незалежний темп)
    frags.append(arrow(W - 90, 98, XC[3], Y_FWD - 36, color="#b85c00", sw=1.6))
    frags.append(text(W - 92, 110, "задає темп бітів\n(незалежно від ядра)", size=10, anchor="end", color="#b85c00"))

    # ─── Горизонтальний роздільник між прямим і зворотнім шляхами ─────────
    frags.append(line(30, (Y_FWD + Y_BACK) // 2, W - 20, (Y_FWD + Y_BACK) // 2,
                      color=MUTED, sw=1.0, dash="6,4"))

    # ─── Підписи шляхів ───────────────────────────────────────────────────
    frags.append(text(18, Y_FWD, "TX →", size=11, anchor="start", color=INK, bold=True))
    frags.append(text(18, Y_BACK, "← RX", size=11, anchor="start", color=MUTED, bold=True))

    # ─── Висновок-тезис внизу ─────────────────────────────────────────────
    conclusion = ("Один автомат перетворює потік байтів із FIFO на точну послідовність "
                  "станів ніжок — ядро не бере участі")
    b_c = fitbox(20, H - 42, W - 40, 36, conclusion, size=12,
                 fill="#f0f4ff", stroke="#3a6bd4", sw=1.5)
    frags.append(b_c)

    render(os.path.join(OUT, "fig-r11-s5a-1-state-machine.svg"), W, H, *frags,
           title="Рис. 4.11.5a.1. Анатомія одного PIO-автомата (state machine)")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.5a.2 — Три способи говорити з ніжками
#   Три колонки × два критерії (осі вертикальні): гнучкість / зайнятість ядра
# ══════════════════════════════════════════════════════════════════════════════
def fig2_three_ways():
    W, H = 780, 460
    frags = []

    # ── Заголовки колонок ───────────────────────────────────────────────────
    COL = [160, 390, 620]   # X-центри трьох колонок
    COL_W = 200
    COL_H = 300
    COL_Y = 95              # верх прямокутників колонок

    C_BANG  = "#fff3cd"   # біт-бенгінг — жовтий
    C_HW    = "#d4edda"   # апаратний блок — зелений
    C_PIO   = "#d6e4ff"   # PIO — синій
    STROKE  = "#444444"

    titles = ["Біт-бенгінг\n(§4.4.7)", "Апаратний блок\n(SPI/I²C/UART)", "PIO\n(RP2040)"]
    fills  = [C_BANG, C_HW, C_PIO]
    stroke_colors = ["#b8860b", "#1f6b3a", "#1a55a0"]

    for i, (cx, title, fill, sc) in enumerate(zip(COL, titles, fills, stroke_colors)):
        # Рамка колонки
        frags.append(rect(cx - COL_W//2, COL_Y, COL_W, COL_H,
                          fill=fill, stroke=sc, sw=2.2, rx=10))
        # Заголовок
        b, _, _ = textbox(cx, COL_Y + 30, title, size=14,
                          fill=fill, stroke=sc, sw=0, bold=True, color=sc, min_w=COL_W - 20)
        frags.append(b)

    # ── Критерії (рядки порівняння) ─────────────────────────────────────────
    criteria = [
        # (текст критерію,  [знак_кол0, знак_кол1, знак_кол2], [пояснення])
        ("Гнучкість протоколу\n(довільний протокол)",
         ["✓", "✗", "✓"],
         ["будь-який", "лише зашита функція", "будь-який"]),
        ("Ядро вільне\n(без CPU overhead)",
         ["✗", "✓", "✓"],
         ["100% зайняте", "вільне", "вільне (з DMA — повністю)"]),
        ("Точний таймінг\n(без тремтіння від переривань)",
         ["✗", "✓", "✓"],
         ["тремтить", "апаратно точний", "детермінований (свій такт)"]),
    ]

    SIGN_COLORS = {"✓": "#1a6b3a", "✗": "#b01010"}
    ROW_Y = [COL_Y + 75, COL_Y + 155, COL_Y + 235]

    for ri, (crit, signs, expl) in enumerate(criteria):
        ry = ROW_Y[ri]
        # Підпис критерію ліворуч
        frags.append(mtext(24, ry - 6, crit, size=11, color=INK, anchor="start"))
        # Горизонтальна лінія-розділювач (крім першого)
        if ri > 0:
            frags.append(line(COL[0] - COL_W//2 + 8, ry - 32, COL[2] + COL_W//2 - 8, ry - 32,
                              color=MUTED, sw=0.8, dash="4,4"))
        for ci, (cx, sign, exp) in enumerate(zip(COL, signs, expl)):
            sc = SIGN_COLORS.get(sign, INK)
            # Знак (великий)
            frags.append(text(cx, ry + 2, sign, size=22, color=sc, anchor="middle", bold=True))
            # Пояснення (маленький)
            b, _, _ = textbox(cx, ry + 26, exp, size=10,
                              fill="white", stroke=sc, sw=1.0, color=sc, min_w=COL_W - 30)
            frags.append(b)

    # ── Виноска для PIO: межа ───────────────────────────────────────────────
    note_y = COL_Y + COL_H - 22
    b_note = fitbox(COL[2] - COL_W//2 + 8, note_y, COL_W - 16, 34,
                    "але: лічені інструкції\n(~32 на блок, 2 блоки)", size=10,
                    fill="#fff8e0", stroke="#b85c00", sw=1.2, color="#b85c00")
    frags.append(b_note)

    # ── Підпис висновку ─────────────────────────────────────────────────────
    b_fin = fitbox(20, H - 50, W - 40, 40,
                   "PIO — третя точка: знімає компроміс «гнучкість АБО вільне ядро» (§4.4.7)",
                   size=13, fill="#e8f0ff", stroke="#1a55a0", sw=1.8, color="#1a55a0", bold=True)
    frags.append(b_fin)

    render(os.path.join(OUT, "fig-r11-s5a-2-three-ways.svg"), W, H, *frags,
           title="Рис. 4.11.5a.2. Три способи говорити з ніжками: біт-бенгінг / апаратний блок / PIO")


if __name__ == "__main__":
    fig1_state_machine()
    print("OK: img/fig-r11-s5a-1-state-machine.svg")
    fig2_three_ways()
    print("OK: img/fig-r11-s5a-2-three-ways.svg")
