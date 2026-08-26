# -*- coding: utf-8 -*-
"""Фігури до теми «Енкодерний режим таймера» (квадратурне декодування, фільтри, переповнення).
Запуск:  python figs.py   → створює SVG у теці ./img/
Стиль і примітиви — зі спільного svgkit.
"""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#b9851f"
AMBER_FILL = "#fdf6e3"
GREEN_FILL = "#eef6ef"
BLUE_FILL = "#eaf2fd"
RED_FILL = "#fdecea"


# ── 1. Квадратурний сигнал: зсув фаз 90° та напрямок обертання ────────────────
def fig_quadrature_signals():
    W, H = 840, 420
    f = [text(W / 2, 26, "Квадратурні сигнали каналів A (TI1) та B (TI2): зсув фаз 90°", size=16, bold=True)]
    f.append(text(W / 2, 48, "порядок чергування фронтів однозначно визначає напрямок обертання вала", size=12, color=MUTED, italic=True))

    # Секція 1: Обертання вперед (CW) — A випереджає B
    f.append(fitbox(30, 70, 780, 155, "", fill=FILL, stroke=MUTED, sw=1))
    f.append(text(45, 92, "Обертання за годинниковою стрілкою (CW): Канал A випереджає Канал B на 90° (DIR = 0, рахунок UP)", size=12, color=INK, bold=True, anchor="start"))

    # Сигнали CW
    x_start = 140
    cw_w = 40  # ширина чверті періоду (90 deg)
    y_a = 120
    y_b = 165
    hi_a, lo_a = y_a - 15, y_a + 15
    hi_b, lo_b = y_b - 15, y_b + 15

    f.append(text(x_start - 25, y_a + 4, "Канал A", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(x_start - 25, y_b + 4, "Канал B", size=11, bold=True, color=NEG, anchor="end"))

    dA = ["M %d,%d" % (x_start, lo_a)]
    dB = ["M %d,%d" % (x_start, lo_b)]
    
    # 3 повних періоди (12 чвертей)
    for q in range(14):
        x0 = x_start + q * cw_w
        x1 = x0 + cw_w
        state_A = 1 if (q % 4) in [0, 1] else 0
        val_a = hi_a if state_A == 1 else lo_a
        dA.append("V %d H %d" % (val_a, x1))
        
        state_B = 1 if (q % 4) in [1, 2] else 0
        val_b = hi_b if state_B == 1 else lo_b
        dB.append("V %d H %d" % (val_b, x1))

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dA), POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dB), NEG))

    # Стан (A, B) під графіком CW
    for q in range(12):
        xc = x_start + q * cw_w + cw_w / 2
        st_A = "1" if (q % 4) in [0, 1] else "0"
        st_B = "1" if (q % 4) in [1, 2] else "0"
        f.append(text(xc, y_b + 34, f"({st_A},{st_B})", size=10, color=MUTED, bold=True))
        f.append(line(x_start + q * cw_w, hi_a - 6, x_start + q * cw_w, y_b + 38, color=MUTED, sw=0.8, dash="2,3"))

    # Секція 2: Обертання назад (CCW) — B випереджає A
    f.append(fitbox(30, 240, 780, 155, "", fill=FILL, stroke=MUTED, sw=1))
    f.append(text(45, 262, "Обертання проти годинникової стрілки (CCW): Канал B випереджає Канал A на 90° (DIR = 1, рахунок DOWN)", size=12, color=INK, bold=True, anchor="start"))

    y_a2 = 290
    y_b2 = 335
    hi_a2, lo_a2 = y_a2 - 15, y_a2 + 15
    hi_b2, lo_b2 = y_b2 - 15, y_b2 + 15

    f.append(text(x_start - 25, y_a2 + 4, "Канал A", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(x_start - 25, y_b2 + 4, "Канал B", size=11, bold=True, color=NEG, anchor="end"))

    dA2 = ["M %d,%d" % (x_start, lo_a2)]
    dB2 = ["M %d,%d" % (x_start, lo_b2)]

    for q in range(14):
        x0 = x_start + q * cw_w
        x1 = x0 + cw_w
        state_A2 = 1 if (q % 4) in [1, 2] else 0
        val_a2 = hi_a2 if state_A2 == 1 else lo_a2
        dA2.append("V %d H %d" % (val_a2, x1))

        state_B2 = 1 if (q % 4) in [0, 1] else 0
        val_b2 = hi_b2 if state_B2 == 1 else lo_b2
        dB2.append("V %d H %d" % (val_b2, x1))

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dA2), POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dB2), NEG))

    # Стан (A, B) під графіком CCW
    for q in range(12):
        xc = x_start + q * cw_w + cw_w / 2
        st_A2 = "1" if (q % 4) in [1, 2] else "0"
        st_B2 = "1" if (q % 4) in [0, 1] else "0"
        f.append(text(xc, y_b2 + 34, f"({st_A2},{st_B2})", size=10, color=MUTED, bold=True))
        f.append(line(x_start + q * cw_w, hi_a2 - 6, x_start + q * cw_w, y_b2 + 38, color=MUTED, sw=0.8, dash="2,3"))

    render(os.path.join(IMG, "quadrature-signals.svg"), W, H, *f)


# ── 2. Режими рахунку енкодера X1, X2, X4 ─────────────────────────────────────
def fig_encoder_modes_x1_x2_x4():
    W, H = 840, 430
    f = [text(W / 2, 26, "Порівняння режимів підрахунку: X1, X2 та X4", size=16, bold=True)]
    f.append(text(W / 2, 48, "множення роздільної здатності датчика апаратним фіксуванням фронтів", size=12, color=MUTED, italic=True))

    # Вхідні сигнали A та B зверху
    f.append(fitbox(30, 68, 780, 95, "", fill=FILL, stroke=MUTED, sw=1))
    f.append(text(45, 86, "Вхідні квадратурні сигнали (1 повний електричний період T = 4 чверті):", size=11, bold=True, color=INK, anchor="start"))

    x_start = 130
    qw = 50  # 1 чверть періоду
    y_a = 108
    y_b = 138
    hi_a, lo_a = y_a - 10, y_a + 10
    hi_b, lo_b = y_b - 10, y_b + 10

    f.append(text(x_start - 20, y_a + 4, "Канал A", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(x_start - 20, y_b + 4, "Канал B", size=11, bold=True, color=NEG, anchor="end"))

    dA = ["M %d,%d" % (x_start, lo_a)]
    dB = ["M %d,%d" % (x_start, lo_b)]
    for q in range(12):
        x1 = x_start + (q + 1) * qw
        st_A = 1 if (q % 4) in [0, 1] else 0
        st_B = 1 if (q % 4) in [1, 2] else 0
        dA.append("V %d H %d" % (hi_a if st_A else lo_a, x1))
        dB.append("V %d H %d" % (hi_b if st_B else lo_b, x1))

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dA), POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(dB), NEG))

    # Позначки періодів зверху
    for p in range(3):
        px0 = x_start + p * 4 * qw
        px1 = px0 + 4 * qw
        f.append(line(px0, 95, px0, 410, color=MUTED, sw=1, dash="3,3"))
        if p == 2:
            f.append(line(px1, 95, px1, 410, color=MUTED, sw=1, dash="3,3"))

    # Секція X1
    f.append(fitbox(30, 172, 780, 75, "", fill=AMBER_FILL, stroke=GOLD, sw=1.2))
    f.append(text(45, 192, "Режим X1 (SMS = 001, лише ↑ на A): 1 інкремент на період T", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(x_start - 20, 224, "Лічильник CNT", size=10, bold=True, color=INK, anchor="end"))
    cnt_x1 = 0
    for q in range(12):
        xp = x_start + q * qw
        if q % 4 == 0:  # rising edge of A
            cnt_x1 += 1
            f.append(circle(xp, 220, 4, fill=GOLD, stroke=GOLD, sw=0))
            f.append(arrow(xp, 208, xp, 216, color=GOLD, sw=1.5))
        f.append(text(xp + qw/2, 224, str(cnt_x1), size=12, bold=True, color=INK))

    # Секція X2
    f.append(fitbox(30, 254, 780, 75, "", fill=BLUE_FILL, stroke=NEG, sw=1.2))
    f.append(text(45, 274, "Режим X2 (SMS = 001/010, ↑ та ↓ на A): 2 інкременти на період T", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(x_start - 20, 306, "Лічильник CNT", size=10, bold=True, color=INK, anchor="end"))
    cnt_x2 = 0
    for q in range(12):
        xp = x_start + q * qw
        if q % 4 == 0 or q % 4 == 2:  # rising and falling edge of A
            cnt_x2 += 1
            f.append(circle(xp, 302, 4, fill=NEG, stroke=NEG, sw=0))
            f.append(arrow(xp, 290, xp, 298, color=NEG, sw=1.5))
        f.append(text(xp + qw/2, 306, str(cnt_x2), size=12, bold=True, color=INK))

    # Секція X4
    f.append(fitbox(30, 336, 780, 75, "", fill=GREEN_FILL, stroke=FIELD, sw=1.2))
    f.append(text(45, 356, "Режим X4 (SMS = 011, усі фронти A та B): 4 інкременти на період T (максимальна точність)", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(x_start - 20, 388, "Лічильник CNT", size=10, bold=True, color=INK, anchor="end"))
    cnt_x4 = 0
    for q in range(12):
        xp = x_start + q * qw
        cnt_x4 += 1
        f.append(circle(xp, 384, 4, fill=FIELD, stroke=FIELD, sw=0))
        f.append(arrow(xp, 372, xp, 380, color=FIELD, sw=1.5))
        f.append(text(xp + qw/2, 388, str(cnt_x4), size=12, bold=True, color=INK))

    render(os.path.join(IMG, "encoder-modes-x1-x2-x4.svg"), W, H, *f)


# ── 3. Апаратний тракт таймера (Hardware Pipeline) ────────────────────────────
def fig_encoder_hardware_pipeline():
    W, H = 840, 380
    f = [text(W / 2, 26, "Апаратний конвеєр обробки енкодерних сигналів у таймері МК", size=16, bold=True)]
    f.append(text(W / 2, 48, "від виводів GPIO через цифрову фільтрацію до реверсивного лічильника CNT", size=12, color=MUTED, italic=True))

    # Входи GPIO
    f.append(fitbox(25, 90, 85, 45, "Вхід CH1\n(TI1 / Pin A)", size=10, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(25, 230, 85, 45, "Вхід CH2\n(TI2 / Pin B)", size=10, bold=True, fill=FILL, stroke=LINE))

    # Стрілки від GPIO до фільтрів
    f.append(arrow(110, 112, 145, 112, color=LINE, sw=1.8))
    f.append(arrow(110, 252, 145, 252, color=LINE, sw=1.8))

    # Цифрові фільтри IC1F / IC2F
    f.append(fitbox(145, 80, 135, 65, "Цифровий фільтр\nIC1F[3:0]\n(N-вибірок fDTS)", size=10, bold=True, fill=AMBER_FILL, stroke=GOLD, sw=1.3))
    f.append(fitbox(145, 220, 135, 65, "Цифровий фільтр\nIC2F[3:0]\n(N-вибірок fDTS)", size=10, bold=True, fill=AMBER_FILL, stroke=GOLD, sw=1.3))

    # Сигнали після фільтрів
    f.append(arrow(280, 112, 325, 112, color=LINE, sw=1.8))
    f.append(text(302, 104, "TI1F", size=10, color=MUTED, bold=True))
    f.append(arrow(280, 252, 325, 252, color=LINE, sw=1.8))
    f.append(text(302, 244, "TI2F", size=10, color=MUTED, bold=True))

    # Інверсія / Селектор полярності CC1P / CC2P
    f.append(fitbox(325, 80, 125, 65, "Вибір полярності\nCC1P / CC1NP\n(Інверсія каналу A)", size=10, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(325, 220, 125, 65, "Вибір полярності\nCC2P / CC2NP\n(Інверсія каналу B)", size=10, bold=True, fill=FILL, stroke=LINE))

    # Сигнали TI1FP1 та TI2FP2
    f.append(arrow(450, 112, 500, 155, color=LINE, sw=1.8))
    f.append(text(475, 124, "TI1FP1", size=10, color=POS, bold=True))
    f.append(arrow(450, 252, 500, 210, color=LINE, sw=1.8))
    f.append(text(475, 240, "TI2FP2", size=10, color=NEG, bold=True))

    # Блок декодера енкодера (Encoder Interface / Slave Mode Controller)
    f.append(fitbox(500, 125, 145, 115, "Інтерфейс енкодера\n(TIMx_SMCR)\n\nЛогіка SMS[2:0]\nВизначення DIR", size=10, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    # Виходи з декодера до лічильника
    f.append(arrow(645, 155, 695, 155, color=FIELD, sw=2.0))
    f.append(text(670, 145, "CK_CNT", size=10, color=FIELD, bold=True))
    f.append(arrow(645, 210, 695, 210, color=POS, sw=2.0))
    f.append(text(670, 200, "DIR (0/1)", size=10, color=POS, bold=True))

    # Основне ядро лічильника CNT
    f.append(fitbox(695, 115, 120, 135, "Реверсивний\nлічильник CNT\n(16 / 32 біти)\n\nРегістр ARR\nПрапорець UIF", size=10, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    # Підказка знизу
    f.append(fitbox(25, 305, 790, 52, "Повна апаратна автономність: імпульси з виводів безпосередньо керують лічильником CNT.\nПроцесор не витрачає жодного такту на підрахунок кроків та визначення напрямку обертання.", size=11, bold=True, fill=FILL, stroke=MUTED, sw=1))

    render(os.path.join(IMG, "encoder-hardware-pipeline.svg"), W, H, *f)


# ── 4. Граф станів квадратурного декодера та захист від брязкоту ───────────────
def fig_encoder_state_transitions():
    W, H = 840, 400
    f = [text(W / 2, 26, "Діаграма станів квадратурного коду Грея та захист від джитеру", size=16, bold=True)]
    f.append(text(W / 2, 48, "кожен фізичний крок змінює рівно один біт; вібрація на межі не накопичує похибки", size=12, color=MUTED, italic=True))

    cx, cy = 250, 220
    r = 110

    # 4 вершини станів у формі ромба: (0,0), (1,0), (1,1), (0,1)
    nodes = {
        "S0": (cx, cy - r, "Стан 00\n(A=0, B=0)"),
        "S1": (cx + r, cy, "Стан 10\n(A=1, B=0)"),
        "S2": (cx, cy + r, "Стан 11\n(A=1, B=1)"),
        "S3": (cx - r, cy, "Стан 01\n(A=0, B=1)"),
    }

    # Малюємо стрілки переходів CW (Зелені стрілки)
    # S0 -> S1
    f.append(arrow(cx + 25, cy - r + 15, cx + r - 15, cy - 25, color=FIELD, sw=2.0))
    f.append(text(cx + 75, cy - 75, "+1 (CW)", size=10, bold=True, color=FIELD))

    # S1 -> S2
    f.append(arrow(cx + r - 15, cy + 25, cx + 25, cy + r - 15, color=FIELD, sw=2.0))
    f.append(text(cx + 75, cy + 75, "+1 (CW)", size=10, bold=True, color=FIELD))

    # S2 -> S3
    f.append(arrow(cx - 25, cy + r - 15, cx - r + 15, cy + 25, color=FIELD, sw=2.0))
    f.append(text(cx - 75, cy + 75, "+1 (CW)", size=10, bold=True, color=FIELD))

    # S3 -> S0
    f.append(arrow(cx - r + 15, cy - 25, cx - 25, cy - r + 15, color=FIELD, sw=2.0))
    f.append(text(cx - 75, cy - 75, "+1 (CW)", size=10, bold=True, color=FIELD))

    # Зворотні стрілки CCW (Сині стрілки)
    # S1 -> S0
    f.append(arrow(cx + r - 35, cy - 10, cx + 10, cy - r + 35, color=NEG, sw=1.5))
    f.append(text(cx + 30, cy - 35, "−1 (CCW)", size=9, bold=True, color=NEG))

    # S2 -> S1
    f.append(arrow(cx + 10, cy + r - 35, cx + r - 35, cy + 10, color=NEG, sw=1.5))
    f.append(text(cx + 30, cy + 35, "−1 (CCW)", size=9, bold=True, color=NEG))

    # S3 -> S2
    f.append(arrow(cx - r + 35, cy + 10, cx - 10, cy + r - 35, color=NEG, sw=1.5))
    f.append(text(cx - 30, cy + 35, "−1 (CCW)", size=9, bold=True, color=NEG))

    # S0 -> S3
    f.append(arrow(cx - 10, cy - r + 35, cx - r + 35, cy - 10, color=NEG, sw=1.5))
    f.append(text(cx - 30, cy - 35, "−1 (CCW)", size=9, bold=True, color=NEG))

    # Заборонені переходи: розбиті лінії, що не перетинають центральний напис
    f.append(line(cx, cy - r + 30, cx, cy - 22, color=POS, sw=1.5, dash="3,3"))
    f.append(line(cx, cy + 22, cx, cy + r - 30, color=POS, sw=1.5, dash="3,3"))
    f.append(line(cx - r + 30, cy, cx - 22, cy, color=POS, sw=1.5, dash="3,3"))
    f.append(line(cx + 22, cy, cx + r - 30, cy, color=POS, sw=1.5, dash="3,3"))

    f.append(circle(cx, cy, 18, fill=RED_FILL, stroke=POS, sw=1.5))
    f.append(text(cx, cy + 4, "ERR", size=10, bold=True, color=POS))

    # Вузли
    for k, (nx, ny, lbl) in nodes.items():
        f.append(fitbox(nx - 48, ny - 24, 96, 48, lbl, size=10, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    # Права панель: Пояснення властивостей
    f.append(fitbox(460, 80, 350, 285, "", fill=FILL, stroke=MUTED, sw=1))
    f.append(text(475, 104, "Властивості коду Грея:", size=12, bold=True, color=INK, anchor="start"))
    
    txt_info = [
        "1. Дистанція Геммінга = 1:",
        "   Між будь-якими сусідніми станами",
        "   змінюється рівно 1 біт сигналу.",
        "",
        "2. Абсолютна стійкість до джитеру:",
        "   Вібрація на межі перемикання (00 ↔ 10)",
        "   породжує взаємно компенсовані кроки",
        "   (+1 та −1). Похибка не накопичується.",
        "",
        "3. Заборонені діагональні переходи (ERR):",
        "   Зміна 2 бітів одночасно (00 ↔ 11 або 01 ↔ 10)",
        "   фізично неможлива при справному датчику.",
        "   Це ознака шуму або перевищення швидкості."
    ]
    f.append(mtext(475, 126, txt_info, size=10, color=INK, anchor="start", lh=1.25))

    render(os.path.join(IMG, "encoder-state-transitions.svg"), W, H, *f)


# ── 5. Обробка переповнення 16-бітного лічильника ──────────────────────────────
def fig_overflow_tracking_timeline():
    W, H = 840, 420
    f = [text(W / 2, 26, "Безперервний облік 64-бітної позиції при переповненні 16-бітного таймера", size=16, bold=True)]
    f.append(text(W / 2, 48, "поєднання апаратного регістра TIMx_CNT та програмного лічильника переповнень", size=12, color=MUTED, italic=True))

    # Секція 1: Апаратний лічильник TIMx_CNT (Sawtooth)
    f.append(fitbox(30, 70, 780, 150, "", fill=FILL, stroke=MUTED, sw=1))
    f.append(text(45, 90, "Апаратний регістр TIMx_CNT (16-бітний діапазон 0 ... 65535, ARR = 0xFFFF):", size=11, bold=True, color=INK, anchor="start"))

    x0 = 90
    w_ramp = 120
    y_top = 130
    y_bot = 190

    f.append(text(x0 - 10, y_top + 4, "65535", size=9, color=MUTED, bold=True, anchor="end"))
    f.append(text(x0 - 10, y_bot + 4, "0", size=9, color=MUTED, bold=True, anchor="end"))
    f.append(line(x0, y_top, x0 + 3 * w_ramp + 80, y_top, color=MUTED, sw=0.8, dash="2,3"))
    f.append(line(x0, y_bot, x0 + 3 * w_ramp + 80, y_bot, color=MUTED, sw=0.8, dash="2,3"))

    # Зубці пили (Upcounting overflow)
    # Ramp 1: 0 -> 65535
    f.append(line(x0, y_bot, x0 + w_ramp, y_top, color=POS, sw=2.2))
    f.append(line(x0 + w_ramp, y_top, x0 + w_ramp, y_bot, color=POS, sw=1.5, dash="2,2"))
    f.append(circle(x0 + w_ramp, y_top, 4, fill=POS, stroke=POS, sw=0))
    f.append(arrow(x0 + w_ramp, y_top - 18, x0 + w_ramp, y_top - 5, color=POS, sw=1.8))
    f.append(text(x0 + w_ramp, y_top - 22, "UIF (UP)", size=9, bold=True, color=POS))

    # Ramp 2: 0 -> 65535
    f.append(line(x0 + w_ramp, y_bot, x0 + 2 * w_ramp, y_top, color=POS, sw=2.2))
    f.append(line(x0 + 2 * w_ramp, y_top, x0 + 2 * w_ramp, y_bot, color=POS, sw=1.5, dash="2,2"))
    f.append(circle(x0 + 2 * w_ramp, y_top, 4, fill=POS, stroke=POS, sw=0))
    f.append(arrow(x0 + 2 * w_ramp, y_top - 18, x0 + 2 * w_ramp, y_top - 5, color=POS, sw=1.8))
    f.append(text(x0 + 2 * w_ramp, y_top - 22, "UIF (UP)", size=9, bold=True, color=POS))

    # Ramp 3: 0 -> 40000 -> reverse to 20000
    f.append(line(x0 + 2 * w_ramp, y_bot, x0 + 2.7 * w_ramp, y_top - 25, color=POS, sw=2.2))
    f.append(line(x0 + 2.7 * w_ramp, y_top - 25, x0 + 3.4 * w_ramp, y_top + 10, color=NEG, sw=2.2))
    f.append(text(x0 + 2.7 * w_ramp, y_top - 32, "Реверс (DIR=1)", size=9, bold=True, color=NEG))

    # Права панель для секції 1 (пояснення переповнення)
    f.append(fitbox(530, 85, 265, 120, "Переповнення (UP):\nПри переході 65535 → 0\nвиникає Update Interrupt (UIF).\n\nНедоповнення (DOWN):\nПри переході 0 → 65535\nвиникає Update Interrupt (UIF).", size=9, bold=True, fill=FILL, stroke=MUTED, sw=1))

    # Секція 2: Програмна 64-бітна позиція (Unwrapped Absolute Position)
    f.append(fitbox(30, 235, 780, 165, "", fill=GREEN_FILL, stroke=FIELD, sw=1.2))
    f.append(text(45, 255, "Розгорнута неперервна абсолютна позиція total_position (int64_t):", size=11, bold=True, color=INK, anchor="start"))

    # Неперервна монотонна лінія
    y_pos_base = 370
    f.append(text(x0 - 10, y_pos_base, "0", size=9, color=MUTED, bold=True, anchor="end"))
    f.append(text(x0 - 10, y_pos_base - 35, "65536", size=9, color=MUTED, bold=True, anchor="end"))
    f.append(text(x0 - 10, y_pos_base - 70, "131072", size=9, color=MUTED, bold=True, anchor="end"))

    f.append(line(x0, y_pos_base, x0 + w_ramp, y_pos_base - 35, color=FIELD, sw=2.5))
    f.append(circle(x0 + w_ramp, y_pos_base - 35, 4, fill=FIELD, stroke=FIELD, sw=0))
    f.append(line(x0 + w_ramp, y_pos_base - 35, x0 + 2 * w_ramp, y_pos_base - 70, color=FIELD, sw=2.5))
    f.append(circle(x0 + 2 * w_ramp, y_pos_base - 70, 4, fill=FIELD, stroke=FIELD, sw=0))
    f.append(line(x0 + 2 * w_ramp, y_pos_base - 70, x0 + 2.7 * w_ramp, y_pos_base - 95, color=FIELD, sw=2.5))
    f.append(line(x0 + 2.7 * w_ramp, y_pos_base - 95, x0 + 3.4 * w_ramp, y_pos_base - 70, color=FIELD, sw=2.5))

    # Права панель для секції 2: Формули
    f.append(fitbox(530, 250, 265, 135, "Обчислення повної позиції:\n\n1. Метод акумулятора переповнень:\npos = (overflow_count << 16) + CNT\n\n2. Дельта-метод (без переривань):\ndelta = (int16_t)(CNT - last_CNT)\ntotal_pos += delta", size=9, bold=True, fill=FILL, stroke=LINE, sw=1))

    render(os.path.join(IMG, "overflow-tracking-timeline.svg"), W, H, *f)


def main():
    fig_quadrature_signals()
    fig_encoder_modes_x1_x2_x4()
    fig_encoder_hardware_pipeline()
    fig_encoder_state_transitions()
    fig_overflow_tracking_timeline()
    print("Усі 5 фігур успішно згенеровано у img/")


if __name__ == "__main__":
    main()
