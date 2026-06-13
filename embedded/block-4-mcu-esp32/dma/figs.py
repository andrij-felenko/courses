# -*- coding: utf-8 -*-
"""
figs.py — Розділ 4.9 DMA: дані без участі ядра
Генерує всі фігури теми 4.9.x у ./img/
НЕ перевизначає примітиви svgkit — лише генерує специфічні для теми SVG.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def out(name):
    return os.path.join(OUT, name)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.1.1 — вартість переривання на один байт
# ══════════════════════════════════════════════════════════════════════════════
def fig_911_event_cost():
    W, H = 760, 380
    parts = []

    # заголовок
    parts.append(text(W/2, 32, "Рис. 4.9.1.1 — Накладні витрати переривання на байт", size=15, bold=True))

    # --- Ліва смуга (низька частота, 1 подія) ---
    LX = 60
    bar_y = 70
    # вхід в ISR / збереження контексту
    ctx_w = 200
    parts.append(rect(LX, bar_y, ctx_w, 60, fill="#f8d7da", stroke=POS, sw=1.5))
    parts.append(text(LX + ctx_w/2, bar_y + 35, "вхід ISR\nзбереження\nконтексту", size=11, color=POS, anchor="middle"))
    # корисна робота
    useful_w = 60
    parts.append(rect(LX + ctx_w, bar_y, useful_w, 60, fill="#d4edda", stroke=FIELD, sw=1.5))
    parts.append(text(LX + ctx_w + useful_w/2, bar_y + 35, "корисна\nробота", size=11, color=FIELD))
    # вихід ISR
    exit_w = 180
    parts.append(rect(LX + ctx_w + useful_w, bar_y, exit_w, 60, fill="#f8d7da", stroke=POS, sw=1.5))
    parts.append(text(LX + ctx_w + useful_w + exit_w/2, bar_y + 35, "відновлення\nконтексту\nвихід ISR", size=11, color=POS))

    label_box, _, _ = textbox(LX + (ctx_w+useful_w+exit_w)/2, bar_y + 85, "Одна подія (низька частота): сервіс ≫ корисна робота", size=12, fill=FILL, stroke=MUTED)
    parts.append(label_box)

    # --- Права смуга (висока частота — суцільна стіна) ---
    RX = 420
    rep = 6
    slot = 74
    for i in range(rep):
        bx = RX + i * slot
        # контекст
        parts.append(rect(bx, bar_y, 55, 60, fill="#f8d7da", stroke=POS, sw=0.8))
        # мікро-робота
        parts.append(rect(bx + 55, bar_y, 8, 60, fill="#d4edda", stroke=FIELD, sw=0.8))
        # вихід
        parts.append(rect(bx + 63, bar_y, 11, 60, fill="#f8d7da", stroke=POS, sw=0.8))

    wall_w = rep * slot
    wall_box, _, _ = textbox(RX + wall_w/2, bar_y + 85, "Висока частота: корисна робота\nтоне у службових тактах", size=12, fill="#fff3cd", stroke="#e0a800")
    parts.append(wall_box)

    # Стрілки-легенди знизу
    parts.append(text(LX + 30, H - 40, "← низька частота подій", size=12, color=MUTED, anchor="start"))
    parts.append(text(RX + wall_w - 20, H - 40, "висока частота подій →", size=12, color=MUTED, anchor="end"))

    # Легенда кольорів
    LEG_Y = H - 20
    parts.append(rect(LX, LEG_Y - 12, 18, 14, fill="#f8d7da", stroke=POS, sw=1))
    parts.append(text(LX + 24, LEG_Y, "службові такти (ISR overhead)", size=11, color=INK, anchor="start"))
    parts.append(rect(LX + 240, LEG_Y - 12, 18, 14, fill="#d4edda", stroke=FIELD, sw=1))
    parts.append(text(LX + 264, LEG_Y, "корисна робота", size=11, color=INK, anchor="start"))

    render(out("fig-4-9-1-1-event-cost.svg"), W, H, *parts)
    print("fig-4-9-1-1-event-cost.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.1.2 — частка CPU vs частота подій
# ══════════════════════════════════════════════════════════════════════════════
def fig_912_cpu_budget():
    W, H = 680, 400
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.1.2 — Частка CPU на обслуговування подій", size=15, bold=True))

    # Вісь Y (CPU %)
    AX, AY = 80, 50
    BX, BY = 80, 330
    EX = 620
    parts.append(arrow(AX, AY, AX, BY + 10))
    parts.append(text(AX - 12, BY + 10, "0%", size=11, color=MUTED, anchor="end"))
    parts.append(text(AX - 12, AY, "100%", size=11, color=MUTED, anchor="end"))
    parts.append(text(AX - 40, (AY+BY)//2, "CPU\n%", size=12, color=INK))

    # Вісь X (частота, лог)
    parts.append(arrow(BX, BY, EX + 10, BY))
    parts.append(text((AX+EX)//2, BY + 28, "Частота подій (байт/с, лог-шкала)", size=12, color=INK))

    # Мітки X
    x_labels = ["10 к", "100 к", "1 М", "10 М", "100 М"]
    x_positions = [140, 230, 340, 450, 560]
    for lbl, xp in zip(x_labels, x_positions):
        parts.append(text(xp, BY + 14, lbl, size=10, color=MUTED))
        parts.append(line(xp, BY - 4, xp, BY + 4, color=MUTED, sw=1))

    # Крива переривань (квадратична → 100%)
    # Наближуємо поліномом: 10к→2%, 100к→20%, 1М→100%
    # Малюємо точками-поліліній
    pts_irq = [(140, 316), (230, 268), (340, BY), (450, BY), (560, BY)]
    # Крива через polyline
    poly = " ".join(f"{x},{y}" for x, y in pts_irq)
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="none"/>')

    # Зона "ядро захлинулось"
    parts.append(f'<rect x="{340}" y="{BY - 0}" width="{EX - 340}" height="4" fill="{POS}" opacity="0.25"/>')
    saturation_box, _, _ = textbox(470, BY - 20, "ядро\nзахлинулось", size=11, fill="#fdecea", stroke=POS)
    parts.append(saturation_box)

    # Лінія DMA (майже горизонтальна близько нуля)
    pts_dma = [(140, 326), (230, 324), (340, 322), (450, 320), (560, 318)]
    poly_dma = " ".join(f"{x},{y}" for x, y in pts_dma)
    parts.append(f'<polyline points="{poly_dma}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Легенда
    LGY = H - 35
    parts.append(rect(AX, LGY - 10, 28, 12, fill="#fdecea", stroke=POS, sw=1.5))
    parts.append(text(AX + 36, LGY + 1, "переривання-на-байт", size=12, color=INK, anchor="start"))
    parts.append(rect(AX + 220, LGY - 10, 28, 12, fill="#d4edda", stroke=FIELD, sw=1.5))
    parts.append(text(AX + 256, LGY + 1, "DMA (ядро поза гарячим шляхом)", size=12, color=INK, anchor="start"))

    # Мітка 100%
    parts.append(line(AX, AY, EX, AY, color=MUTED, sw=1, dash="4 4"))

    render(out("fig-4-9-1-2-cpu-budget.svg"), W, H, *parts)
    print("fig-4-9-1-2-cpu-budget.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.2.1 — DMA на спільній шині
# ══════════════════════════════════════════════════════════════════════════════
def fig_921_dma_on_bus():
    W, H = 700, 380
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.2.1 — DMA-контролер на спільній шині", size=15, bold=True))

    # Шина (горизонтальна смуга посередині)
    BUS_Y = 200
    parts.append(rect(60, BUS_Y - 18, 580, 36, fill="#eaf4fb", stroke=NEG, sw=2, rx=4))
    parts.append(text(350, BUS_Y + 6, "Системна шина (AHB / AXI)", size=13, color=NEG, bold=True))

    # Арбітр
    arb_box, _, _ = textbox(350, BUS_Y - 60, "Арбітр шини", size=12, fill="#fff9e6", stroke="#e0a800", sw=2)
    parts.append(arb_box)
    parts.append(line(350, BUS_Y - 42, 350, BUS_Y - 18, color="#e0a800", sw=2))

    # Ядро CPU
    cpu_box, cw, ch = textbox(140, 90, "Ядро CPU\n(Xtensa LX7)", size=13, fill=FILL, stroke=LINE, sw=2)
    parts.append(cpu_box)
    parts.append(arrow(140, 90 + ch//2, 140, BUS_Y - 18))

    # DMA-контролер
    dma_box, dw, dh = textbox(350, 90, "DMA-контролер", size=13, fill="#d4edda", stroke=FIELD, sw=2)
    parts.append(dma_box)
    parts.append(arrow(350, 90 + dh//2, 350, BUS_Y - 78))  # до арбітра

    # RAM
    ram_box, rw, rh = textbox(560, 90, "SRAM / PSRAM", size=13, fill=FILL, stroke=LINE, sw=2)
    parts.append(ram_box)
    parts.append(arrow(560, 90 + rh//2, 560, BUS_Y - 18))

    # Периферія (знизу)
    per_box, pw, ph = textbox(350, 310, "Периферія\n(АЦП / шина)", size=13, fill="#f8d7da", stroke=POS, sw=2)
    parts.append(per_box)
    parts.append(line(350, BUS_Y + 18, 350, 310 - ph//2, color=POS, sw=2))

    # Жирна стрілка: периферія → DMA → RAM (обхід ядра)
    # Дані ідуть: периферія → шина → DMA → RAM
    parts.append(f'<path d="M350,{310 - ph//2 - 5} L350,{BUS_Y+18}" stroke="{POS}" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')
    # DMA → RAM по шині
    parts.append(f'<path d="M{350+dw//2},{BUS_Y} Q460,{BUS_Y-10} {560-rw//2},{BUS_Y}" stroke="{FIELD}" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')

    # Тонка стрілка: ядро "налаштування + одне переривання"
    ctrl_label, _, _ = textbox(210, 145, "налаштування\n+ 1 переривання", size=10, fill="#fff9e6", stroke=MUTED, sw=1)
    parts.append(ctrl_label)

    # Легенда
    LGY = H - 25
    parts.append(f'<line x1="60" y1="{LGY}" x2="100" y2="{LGY}" stroke="{FIELD}" stroke-width="3"/>')
    parts.append(text(108, LGY + 4, "шлях даних (DMA)", size=11, color=INK, anchor="start"))
    parts.append(f'<line x1="250" y1="{LGY}" x2="290" y2="{LGY}" stroke="{POS}" stroke-width="3"/>')
    parts.append(text(298, LGY + 4, "DMA-запит від периферії", size=11, color=INK, anchor="start"))
    parts.append(f'<line x1="480" y1="{LGY}" x2="520" y2="{LGY}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    parts.append(text(528, LGY + 4, "команди ядра", size=11, color=INK, anchor="start"))

    render(out("fig-4-9-2-1-dma-on-bus.svg"), W, H, *parts)
    print("fig-4-9-2-1-dma-on-bus.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.2.2 — без DMA vs з DMA (діаграма послідовності)
# ══════════════════════════════════════════════════════════════════════════════
def fig_922_with_without_dma():
    W, H = 700, 400
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.2.2 — Без DMA (ліворуч) vs З DMA (праворуч)", size=15, bold=True))

    # --- Ліва частина: без DMA ---
    LX = 60
    parts.append(text(LX + 120, 55, "Без DMA", size=14, bold=True, color=POS))

    # Смуги
    label_w = 70
    cpu_y = 80
    per_y = 170

    parts.append(text(LX, cpu_y + 20, "Ядро", size=12, color=INK, anchor="end"))
    parts.append(text(LX, per_y + 20, "Переф.", size=12, color=INK, anchor="end"))
    parts.append(line(LX, cpu_y, LX + 260, cpu_y, color=MUTED, sw=1, dash="2 2"))
    parts.append(line(LX, per_y, LX + 260, per_y, color=MUTED, sw=1, dash="2 2"))

    # Багато маленьких ISR-блоків на ядрі
    for i in range(8):
        bx = LX + 10 + i * 30
        parts.append(rect(bx, cpu_y - 1, 22, 40, fill="#f8d7da", stroke=POS, sw=0.8, rx=2))
    parts.append(text(LX + 125, cpu_y + 55, "постійні переривання→копіювання", size=10, color=POS))

    # Дані в периферії — маленькі смуги
    for i in range(8):
        bx = LX + 10 + i * 30
        parts.append(rect(bx, per_y - 1, 22, 30, fill="#eaf0fd", stroke=NEG, sw=0.8, rx=2))

    # Стрілки ISR
    for i in range(8):
        cx = LX + 21 + i * 30
        parts.append(arrow(cx, per_y - 1, cx, cpu_y + 40))

    # --- Права частина: з DMA ---
    RX = 380
    parts.append(text(RX + 140, 55, "З DMA", size=14, bold=True, color=FIELD))

    parts.append(text(RX, cpu_y + 20, "Ядро", size=12, color=INK, anchor="end"))
    parts.append(text(RX, per_y + 20, "DMA", size=12, color=INK, anchor="end"))
    parts.append(text(RX, 260 + 20, "RAM", size=12, color=INK, anchor="end"))
    parts.append(line(RX, cpu_y, RX + 260, cpu_y, color=MUTED, sw=1, dash="2 2"))
    parts.append(line(RX, per_y, RX + 260, per_y, color=MUTED, sw=1, dash="2 2"))
    parts.append(line(RX, 260, RX + 260, 260, color=MUTED, sw=1, dash="2 2"))

    # Ядро: маленький "старт", велика вільна зона, маленький "done"
    parts.append(rect(RX + 10, cpu_y - 1, 30, 40, fill="#d4edda", stroke=FIELD, sw=1.2, rx=2))
    parts.append(text(RX + 25, cpu_y + 25, "start", size=9, color=FIELD))
    # вільна зона
    parts.append(rect(RX + 45, cpu_y + 4, 160, 28, fill="#f0f0f0", stroke=MUTED, sw=0.8, rx=2))
    parts.append(text(RX + 125, cpu_y + 22, "вільне ядро (обчислення / сон)", size=10, color=MUTED))
    # done
    parts.append(rect(RX + 210, cpu_y - 1, 30, 40, fill="#d4edda", stroke=FIELD, sw=1.2, rx=2))
    parts.append(text(RX + 225, cpu_y + 25, "done", size=9, color=FIELD))

    # DMA: суцільна смуга копіювання
    parts.append(rect(RX + 45, per_y - 1, 195, 30, fill="#d4edda", stroke=FIELD, sw=1.5, rx=2))
    parts.append(text(RX + 142, per_y + 20, "DMA копіює блок", size=11, color=FIELD))

    # RAM: заповнення
    parts.append(rect(RX + 45, 259, 195, 20, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    parts.append(text(RX + 142, 273, "буфер наповнюється", size=10, color=NEG))

    # Одна стрілка "done"
    parts.append(arrow(RX + 225, per_y + 30, RX + 225, cpu_y + 40))
    done_box, _, _ = textbox(RX + 225, 155, "1 переривання\n«готово»", size=10, fill="#d4edda", stroke=FIELD)
    parts.append(done_box)

    render(out("fig-4-9-2-2-with-without-dma.svg"), W, H, *parts)
    print("fig-4-9-2-2-with-without-dma.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.3.1 — канали DMA
# ══════════════════════════════════════════════════════════════════════════════
def fig_931_channels():
    W, H = 680, 380
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.3.1 — Один DMA-контролер, кілька каналів", size=15, bold=True))

    # DMA-контролер у центрі
    dma_box, dw, dh = textbox(340, 200, "DMA-контролер\n(GDMA ESP32)", size=14, fill="#d4edda", stroke=FIELD, sw=2, min_w=160)
    parts.append(dma_box)

    # Канал 0 — АЦП (ліворуч зверху)
    ch0_box, c0w, c0h = textbox(120, 100, "Канал 0\nДжерело: АЦП\nПризначення: SRAM\nСтан: 4096 / 8192", size=11, fill=FILL, stroke=NEG, sw=1.5, min_w=150)
    parts.append(ch0_box)
    parts.append(arrow(120 + c0w//2, 100 + c0h//2, 340 - dw//2, 200 - 20))

    # Канал 1 — дисплей (праворуч зверху)
    ch1_box, c1w, c1h = textbox(560, 100, "Канал 1\nДжерело: SRAM\nПризначення: SPI-шина\nСтан: 102400 / 153600", size=11, fill=FILL, stroke=POS, sw=1.5, min_w=160)
    parts.append(ch1_box)
    parts.append(arrow(560 - c1w//2, 100 + c1h//2, 340 + dw//2, 200 - 20))

    # Канал 2 — аудіо (знизу)
    ch2_box, c2w, c2h = textbox(340, 330, "Канал 2 / Аудіо\nДжерело: I2S RX FIFO  Призначення: SRAM\nПріоритет: HIGH (1)", size=11, fill="#fff9e6", stroke="#e0a800", sw=1.5, min_w=260)
    parts.append(ch2_box)
    parts.append(arrow(340, 330 - c2h//2, 340, 200 + dh//2))

    # Підписи
    parts.append(text(120, 155, "АЦП\n(вхідний потік)", size=11, color=NEG))
    parts.append(text(560, 155, "Дисплей\n(вихідний потік)", size=11, color=POS))

    render(out("fig-4-9-3-1-channels.svg"), W, H, *parts)
    print("fig-4-9-3-1-channels.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.3.2 — анатомія дескриптора і кільцевий список
# ══════════════════════════════════════════════════════════════════════════════
def fig_932_descriptor_list():
    W, H = 760, 420
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.3.2 — Дескриптор і зв'язаний список (scatter-gather)", size=15, bold=True))

    desc_fields = ["owner / eof", "length", "buf_ptr →", "next_ptr →"]
    field_h = 34
    desc_w = 140
    desc_total_h = len(desc_fields) * field_h

    # Три дескриптори
    desc_cx = [170, 390, 610]
    for di, cx in enumerate(desc_cx):
        dy = 80
        for fi, fname in enumerate(desc_fields):
            fill_c = "#eaf0fd" if fi == 3 else FILL
            parts.append(rect(cx - desc_w//2, dy + fi * field_h, desc_w, field_h,
                               fill=fill_c, stroke=LINE, sw=1.2, rx=3))
            parts.append(text(cx, dy + fi * field_h + field_h * 0.6, fname, size=11, color=INK))
        parts.append(text(cx, dy - 12, f"desc[{di}]", size=13, bold=True, color=FIELD))

    # Стрілки next_ptr: desc0→desc1→desc2→desc0 (кільце)
    arrow_y = 80 + 3 * field_h + field_h * 0.5
    # desc0 → desc1
    parts.append(arrow(desc_cx[0] + desc_w//2, arrow_y, desc_cx[1] - desc_w//2 - 5, arrow_y))
    # desc1 → desc2
    parts.append(arrow(desc_cx[1] + desc_w//2, arrow_y, desc_cx[2] - desc_w//2 - 5, arrow_y))
    # desc2 → desc0 (дуга знизу)
    ring_y = 80 + desc_total_h + 50
    parts.append(f'<path d="M{desc_cx[2]+desc_w//2},{arrow_y} '
                 f'Q{desc_cx[2]+80},{ring_y+30} {(desc_cx[0]+desc_cx[2])//2},{ring_y+60} '
                 f'Q{desc_cx[0]-80},{ring_y+30} {desc_cx[0]-desc_w//2},{arrow_y}" '
                 f'fill="none" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="6 3" '
                 f'marker-end="url(#arrow)"/>')
    ring_lbl, _, _ = textbox(390, ring_y + 60, "кільце (circular)", size=12, fill="#d4edda", stroke=FIELD)
    parts.append(ring_lbl)

    # buf_ptr → розкидані буфери (scatter-gather) — вниз
    buf_y = 290
    buf_cx = [100, 390, 660]
    for di, (dcx, bcx) in enumerate(zip(desc_cx, buf_cx)):
        buf_ptr_y = 80 + 2 * field_h + field_h * 0.5
        parts.append(arrow(dcx, 80 + 2*field_h + field_h, bcx, buf_y - 20))
        parts.append(rect(bcx - 55, buf_y - 20, 110, 30, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
        parts.append(text(bcx, buf_y - 2, f"buf[{di}] (в SRAM)", size=10, color=POS))

    parts.append(text(390, H - 20, "buf_ptr вказують на РІЗНІ ділянки пам'яті (scatter-gather)", size=12, color=MUTED))

    render(out("fig-4-9-3-2-descriptor-list.svg"), W, H, *parts)
    print("fig-4-9-3-2-descriptor-list.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.3.3 — арбітраж шини і пропускна здатність
# ══════════════════════════════════════════════════════════════════════════════
def fig_933_bus_arbitration():
    W, H = 700, 400
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.3.3 — Арбітраж шини: пріоритети каналів", size=15, bold=True))

    # Два запити
    aud_box, aw, ah = textbox(150, 100, "Канал 2: Аудіо\nПріоритет: HIGH", size=12, fill="#fff9e6", stroke="#e0a800", sw=2)
    parts.append(aud_box)
    disp_box, dw, dh = textbox(550, 100, "Канал 1: Дисплей\nПріоритет: LOW", size=12, fill=FILL, stroke=MUTED, sw=2)
    parts.append(disp_box)

    # Арбітр
    arb_cx, arb_cy = 350, 200
    parts.append(f'<polygon points="{arb_cx},{arb_cy-40} {arb_cx+50},{arb_cy} {arb_cx},{arb_cy+40} {arb_cx-50},{arb_cy}" '
                 f'fill="#eaf4fb" stroke="{NEG}" stroke-width="2"/>')
    parts.append(text(arb_cx, arb_cy + 5, "Арбітр", size=12, color=NEG, bold=True))

    # Стрілки від каналів до арбітра
    parts.append(arrow(150 + aw//2, 100 + ah//2, arb_cx - 50, arb_cy))
    parts.append(arrow(550 - dw//2, 100 + dh//2, arb_cx + 50, arb_cy))

    # Переможець — аудіо (потрапляє на шину)
    bus_box, bw, bh = textbox(350, 300, "Шина (80 МБ/с)\n✓ Аудіо передається зараз", size=13, fill="#d4edda", stroke=FIELD, sw=2)
    parts.append(bus_box)
    parts.append(arrow(arb_cx, arb_cy + 40, arb_cx, 300 - bh//2))

    # Дисплей чекає
    wait_box, _, _ = textbox(550, 200, "Дисплей\nчекає…", size=12, fill="#f8d7da", stroke=POS, sw=1.5)
    parts.append(wait_box)
    parts.append(f'<path d="M{550},{100 + dh//2} L{550},{200 - 30}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#arrow)"/>')

    # Смуга пропускної здатності
    BW_Y = H - 65
    parts.append(text(60, BW_Y - 8, "Шина 80 МБ/с:", size=12, color=INK, anchor="start"))
    # Ядро
    parts.append(rect(180, BW_Y, 100, 28, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    parts.append(text(230, BW_Y + 18, "Ядро 20 МБ/с", size=10, color=NEG))
    # Аудіо
    parts.append(rect(280, BW_Y, 25, 28, fill="#fff9e6", stroke="#e0a800", sw=1.2, rx=3))
    parts.append(text(292, BW_Y + 18, "Аудіо", size=8, color="#8a6200"))
    # Дисплей
    parts.append(rect(305, BW_Y, 120, 28, fill="#f0f0f0", stroke=MUTED, sw=1.2, rx=3))
    parts.append(text(365, BW_Y + 18, "Дисплей 24 МБ/с", size=10, color=MUTED))
    # Запас
    parts.append(rect(425, BW_Y, 115, 28, fill="#d4edda", stroke=FIELD, sw=1.2, rx=3))
    parts.append(text(482, BW_Y + 18, "Запас ≈16 МБ/с", size=10, color=FIELD))

    render(out("fig-4-9-3-3-bus-arbitration.svg"), W, H, *parts)
    print("fig-4-9-3-3-bus-arbitration.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.4.1 — ping-pong фази
# ══════════════════════════════════════════════════════════════════════════════
def fig_941_pingpong_phases():
    W, H = 760, 360
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.4.1 — Подвійна буферизація (ping-pong): чотири фази", size=15, bold=True))

    phase_w = 170
    phase_h = 120
    phases = [
        {"t": "Фаза 1", "dma": "A", "cpu": "B", "dma_fill": "#d4edda", "cpu_fill": "#eaf0fd"},
        {"t": "Фаза 2", "dma": "B", "cpu": "A", "dma_fill": "#d4edda", "cpu_fill": "#eaf0fd"},
        {"t": "Фаза 3", "dma": "A", "cpu": "B", "dma_fill": "#d4edda", "cpu_fill": "#eaf0fd"},
        {"t": "…", "dma": "…", "cpu": "…", "dma_fill": FILL, "cpu_fill": FILL},
    ]

    for i, ph in enumerate(phases):
        px = 30 + i * (phase_w + 10)
        py = 65

        # Рамка фази
        parts.append(rect(px, py, phase_w, phase_h, fill="#fafafa", stroke=MUTED, sw=1, rx=8))
        parts.append(text(px + phase_w//2, py + 18, ph["t"], size=13, bold=True, color=INK))

        # DMA пише буфер X
        dma_lbl = f'DMA пише: буфер {ph["dma"]}'
        dma_b, dw, dh = textbox(px + phase_w//2, py + 52, dma_lbl, size=11, fill=ph["dma_fill"], stroke=FIELD, sw=1.5)
        parts.append(dma_b)

        # Ядро читає буфер Y
        cpu_lbl = f'Ядро читає: буфер {ph["cpu"]}'
        cpu_b, cw, ch = textbox(px + phase_w//2, py + 88, cpu_lbl, size=11, fill=ph["cpu_fill"], stroke=NEG, sw=1.5)
        parts.append(cpu_b)

        # Стрілка між фазами
        if i < len(phases) - 1:
            parts.append(arrow(px + phase_w + 2, py + phase_h//2, px + phase_w + 10, py + phase_h//2))
            swap_box, _, _ = textbox(px + phase_w + 6, py + phase_h//2 - 22, "своп", size=10, fill="#fff9e6", stroke="#e0a800", sw=1)
            parts.append(swap_box)

    # Легенда
    LGY = 215
    parts.append(text(40, LGY + 15, "Ключове:", size=13, bold=True, color=INK, anchor="start"))
    parts.append(text(40, LGY + 36, "Поки DMA заповнює один буфер — ядро безпечно читає інший.", size=12, color=INK, anchor="start"))
    parts.append(text(40, LGY + 56, "Конфлікту немає: кожен буфер у будь-який момент належить комусь одному.", size=12, color=INK, anchor="start"))

    # Кольорова легенда
    parts.append(rect(40, LGY + 75, 18, 14, fill="#d4edda", stroke=FIELD, sw=1))
    parts.append(text(64, LGY + 87, "DMA пише (зайнятий DMA)", size=11, color=INK, anchor="start"))
    parts.append(rect(300, LGY + 75, 18, 14, fill="#eaf0fd", stroke=NEG, sw=1))
    parts.append(text(324, LGY + 87, "Ядро читає (безпечний доступ)", size=11, color=INK, anchor="start"))

    render(out("fig-4-9-4-1-pingpong-phases.svg"), W, H, *parts)
    print("fig-4-9-4-1-pingpong-phases.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.4.2 — кільцевий буфер
# ══════════════════════════════════════════════════════════════════════════════
def fig_942_ring_buffer():
    W, H = 640, 420
    import math
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.4.2 — Кільцевий буфер: DMA пише, ядро читає", size=15, bold=True))

    cx, cy, R, r = 320, 220, 150, 50
    N = 16  # секторів
    angle_start = -math.pi / 2

    # Намалювати N секторів
    dma_write = 10   # DMA поточна позиція
    cpu_read = 4     # ядро поточна позиція
    half_pos = 8     # half-transfer

    for i in range(N):
        a0 = angle_start + i * 2 * math.pi / N
        a1 = angle_start + (i + 1) * 2 * math.pi / N
        # Визначити стан сектора
        if i >= cpu_read and i < dma_write:
            fill_c = "#d4edda"  # заповнений, готовий для ядра
            stroke_c = FIELD
        elif i >= dma_write or i < cpu_read:
            fill_c = "#f0f0f0"  # вільний
            stroke_c = MUTED
        else:
            fill_c = FILL
            stroke_c = LINE

        # Шлях сектора
        x0 = cx + R * math.cos(a0)
        y0 = cy + R * math.sin(a0)
        x1 = cx + R * math.cos(a1)
        y1 = cy + R * math.sin(a1)
        xi0 = cx + r * math.cos(a0)
        yi0 = cy + r * math.sin(a0)
        xi1 = cx + r * math.cos(a1)
        yi1 = cy + r * math.sin(a1)
        parts.append(f'<path d="M{xi0:.1f},{yi0:.1f} L{x0:.1f},{y0:.1f} '
                     f'A{R},{R} 0 0,1 {x1:.1f},{y1:.1f} '
                     f'L{xi1:.1f},{yi1:.1f} '
                     f'A{r},{r} 0 0,0 {xi0:.1f},{yi0:.1f} Z" '
                     f'fill="{fill_c}" stroke="{stroke_c}" stroke-width="1.5"/>')

    # Вказівник DMA (write)
    a_dma = angle_start + dma_write * 2 * math.pi / N
    xd = cx + (R + 25) * math.cos(a_dma)
    yd = cy + (R + 25) * math.sin(a_dma)
    xd_r = cx + R * math.cos(a_dma)
    yd_r = cy + R * math.sin(a_dma)
    parts.append(arrow(xd, yd, xd_r, yd_r))
    dma_ptr_box, _, _ = textbox(xd, yd - 18, "DMA write", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(dma_ptr_box)

    # Вказівник ядра (read)
    a_cpu = angle_start + cpu_read * 2 * math.pi / N
    xc = cx + (R + 25) * math.cos(a_cpu)
    yc = cy + (R + 25) * math.sin(a_cpu)
    xc_r = cx + R * math.cos(a_cpu)
    yc_r = cy + R * math.sin(a_cpu)
    parts.append(arrow(xc, yc, xc_r, yc_r))
    cpu_ptr_box, _, _ = textbox(xc + 10, yc + 15, "ядро read", size=11, fill="#eaf0fd", stroke=NEG)
    parts.append(cpu_ptr_box)

    # Позначення half-transfer і transfer-complete
    a_half = angle_start + half_pos * 2 * math.pi / N
    xh = cx + (r - 15) * math.cos(a_half)
    yh = cy + (r - 15) * math.sin(a_half)
    half_box, _, _ = textbox(xh, yh, "½", size=13, fill="#fff9e6", stroke="#e0a800", sw=2)
    parts.append(half_box)

    # Центр — назва
    parts.append(text(cx, cy + 5, "ring\nbuffer", size=14, color=INK, bold=True))

    # Легенда
    LGY = H - 70
    parts.append(rect(40, LGY, 18, 14, fill="#d4edda", stroke=FIELD, sw=1))
    parts.append(text(64, LGY + 12, "заповнено DMA, готово до обробки", size=11, color=INK, anchor="start"))
    parts.append(rect(40, LGY + 22, 18, 14, fill="#f0f0f0", stroke=MUTED, sw=1))
    parts.append(text(64, LGY + 34, "вільно (вже оброблено)", size=11, color=INK, anchor="start"))
    parts.append(text(40, LGY + 52, "½ — переривання half-transfer (оброби першу половину, DMA пише другу)", size=11, color="#8a6200", anchor="start"))

    render(out("fig-4-9-4-2-ring-buffer.svg"), W, H, *parts)
    print("fig-4-9-4-2-ring-buffer.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.4.3 — overrun timing
# ══════════════════════════════════════════════════════════════════════════════
def fig_943_overrun_timing():
    W, H = 700, 380
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.4.3 — Часова шкала: вчасно vs overrun", size=15, bold=True))

    # ---- Верхній рядок (ОК) ----
    TY_OK = 90
    parts.append(text(60, TY_OK - 10, "Норма (встигаємо):", size=13, bold=True, color=FIELD, anchor="start"))
    # DMA fill блоки (рівні, темпові)
    fill_w = 140
    gap = 10
    for i in range(3):
        bx = 80 + i * (fill_w + gap)
        parts.append(rect(bx, TY_OK, fill_w, 36, fill="#d4edda", stroke=FIELD, sw=1.5, rx=4))
        parts.append(text(bx + fill_w//2, TY_OK + 22, f"DMA заповнює блок {i+1}", size=11, color=FIELD))
    # CPU обробка
    cpu_h = 28
    for i in range(2):
        bx = 80 + i * (fill_w + gap)
        parts.append(rect(bx, TY_OK + 45, fill_w - 20, cpu_h, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
        parts.append(text(bx + (fill_w-20)//2, TY_OK + 63, f"CPU обробляє {i+1}", size=11, color=NEG))
    parts.append(text(560, TY_OK + 22, "✓ ОК", size=14, bold=True, color=FIELD))

    # ---- Нижній рядок (OVERRUN) ----
    TY_OV = 220
    parts.append(text(60, TY_OV - 10, "Overrun (не встигаємо):", size=13, bold=True, color=POS, anchor="start"))
    for i in range(3):
        bx = 80 + i * (fill_w + gap)
        parts.append(rect(bx, TY_OV, fill_w, 36, fill="#d4edda", stroke=FIELD, sw=1.5, rx=4))
        parts.append(text(bx + fill_w//2, TY_OV + 22, f"DMA блок {i+1}", size=11, color=FIELD))
    # CPU обробляє повільно (виходить за межу блоку)
    long_w = fill_w + 80
    bx = 80
    parts.append(rect(bx, TY_OV + 45, long_w, cpu_h, fill="#f8d7da", stroke=POS, sw=1.5, rx=4))
    parts.append(text(bx + long_w//2, TY_OV + 63, "CPU обробляє (довго!)", size=11, color=POS))

    # Стрілка «наповзання»
    overlap_x = 80 + fill_w + gap
    parts.append(f'<line x1="{overlap_x}" y1="{TY_OV + 36}" x2="{overlap_x}" y2="{TY_OV + 45 + cpu_h + 5}" '
                 f'stroke="{POS}" stroke-width="2.5" stroke-dasharray="none"/>')
    ov_box, _, _ = textbox(overlap_x + 55, TY_OV + 85, "DMA пише\nтуди, де ще читає CPU\n→ OVERRUN, втрата даних", size=11, fill="#fdecea", stroke=POS)
    parts.append(ov_box)

    # Правило
    rule_box, _, _ = textbox(350, H - 30, "Правило: час заповнення буфера ≥ часу обробки", size=12, fill="#d4edda", stroke=FIELD, sw=2)
    parts.append(rule_box)

    render(out("fig-4-9-4-3-overrun-timing.svg"), W, H, *parts)
    print("fig-4-9-4-3-overrun-timing.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.5.1 — ланцюг АЦП + DMA
# ══════════════════════════════════════════════════════════════════════════════
def fig_951_adc_dma_chain():
    W, H = 780, 280
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.5.1 — Ланцюг: Таймер → АЦП → DMA → Буфер → Задача RTOS", size=15, bold=True))

    blocks = [
        ("Таймер\n(темп вибірки)", NEG, "#eaf0fd"),
        ("АЦП\n(перетворення)", "#8a6200", "#fff9e6"),
        ("DMA\n(складає семпли)", FIELD, "#d4edda"),
        ("Кільцевий\nбуфер у SRAM", MUTED, FILL),
        ("Задача RTOS\n(обробка блоку)", NEG, "#eaf0fd"),
    ]
    BX = 60
    BY = 130
    bw = 110
    bh = 65
    gap = 28

    prev_x = None
    for i, (lbl, stroke_c, fill_c) in enumerate(blocks):
        cx = BX + i * (bw + gap) + bw // 2
        bx = cx - bw // 2
        parts.append(rect(bx, BY - bh//2, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        parts.append(mtext(cx, BY - 8, lbl, size=11, color=INK))
        if prev_x is not None:
            parts.append(arrow(prev_x + bw//2 + 2, BY, cx - bw//2 - 2, BY))
        prev_x_center = cx

    # Сигнали під блоками
    signals = ["тік\n(1/f_s)", "DMA-запит\nна кожен семпл", "completion\nISR", "семафор /\nчерга"]
    for i, sig in enumerate(signals):
        ax = BX + i * (bw + gap) + bw + gap // 2
        parts.append(text(ax, BY + 52, sig, size=10, color=MUTED))

    # Completion ISR — ядро прокидається раз на блок
    last_cx = BX + (len(blocks)-1) * (bw + gap) + bw // 2
    wake_box, _, _ = textbox(last_cx, BY + 90, "пробудження ядра:\nраз на блок (напр. кожні 20 мс)", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(wake_box)
    parts.append(arrow(last_cx, BY + bh//2 + 5, last_cx, BY + 66))

    render(out("fig-4-9-5-1-adc-dma-chain.svg"), W, H, *parts)
    print("fig-4-9-5-1-adc-dma-chain.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.5.2 — формат елемента потоку АЦП
# ══════════════════════════════════════════════════════════════════════════════
def fig_952_sample_element():
    W, H = 700, 320
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.5.2 — Формат елемента потоку АЦП і розпакування", size=15, bold=True))

    # Слово 32 біти
    WORD_X = 60
    WORD_Y = 70
    WORD_W = 400
    WORD_H = 50

    # Поля: [31:16 зарезервовано] [15:12 channel] [11:0 val]
    fields = [
        (0, 200, "#f0f0f0", MUTED, "зарезервовано [31:16]"),
        (200, 80, "#fff9e6", "#8a6200", "канал [15:12]"),
        (280, 120, "#d4edda", FIELD, "val (12-бітний код) [11:0]"),
    ]
    for fx, fw, fill_c, stroke_c, lbl in fields:
        parts.append(rect(WORD_X + fx, WORD_Y, fw, WORD_H, fill=fill_c, stroke=stroke_c, sw=1.5, rx=3))
        parts.append(text(WORD_X + fx + fw//2, WORD_Y + 30, lbl, size=10, color=INK))

    parts.append(text(WORD_X - 8, WORD_Y + 30, "32 біт:", size=12, color=INK, anchor="end"))

    # Стрілка до формули
    parts.append(arrow(WORD_X + WORD_W//2, WORD_Y + WORD_H + 5, WORD_X + WORD_W//2, WORD_Y + WORD_H + 40))

    # Формула розпакування
    formula_box = fitbox(WORD_X, WORD_Y + WORD_H + 42, WORD_W, 50,
                         "channel = (word >> 12) & 0xF\nVin = val × Vref / (2¹² − 1)",
                         size=13, fill="#eaf0fd", stroke=NEG, sw=1.5)
    parts.append(formula_box)

    # Приклад числового розпакування
    example_y = WORD_Y + WORD_H + 110
    ex_box, _, _ = textbox(WORD_X + WORD_W//2, example_y,
                            "word = 0x00001800 → val=1800₁₆=6144, ch=0\nVin = 6144 × 3.3 / 4095 ≈ 4.95 В (не реальне, для ілюстрації)",
                            size=11, fill=FILL, stroke=MUTED, sw=1)
    parts.append(ex_box)

    # Масив семплів праворуч
    ARR_X = 510
    parts.append(text(ARR_X + 80, WORD_Y - 12, "Масив у буфері:", size=12, color=INK))
    for i in range(5):
        fy = "#d4edda" if i % 2 == 0 else "#fff9e6"
        parts.append(rect(ARR_X, WORD_Y + i * 30, 160, 28, fill=fy, stroke=MUTED, sw=1, rx=3))
        parts.append(text(ARR_X + 80, WORD_Y + i * 30 + 18, f"semple[{i}]: ch={i%2}, val=…", size=10, color=INK))

    render(out("fig-4-9-5-2-sample-element.svg"), W, H, *parts)
    print("fig-4-9-5-2-sample-element.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.5.3 — частота пробудження ядра
# ══════════════════════════════════════════════════════════════════════════════
def fig_953_wakeup_rate():
    W, H = 700, 340
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.5.3 — Частота пробудження ядра: analogRead vs DMA", size=15, bold=True))

    TL = 80  # часова лінія X-start
    TR = 660
    timeline_w = TR - TL

    # --- analogRead (20000/с) ---
    AR_Y = 100
    parts.append(text(TL - 10, AR_Y + 12, "analogRead\n(20 кГц)", size=12, color=POS, anchor="end"))
    parts.append(line(TL, AR_Y, TR, AR_Y, color=MUTED, sw=1))
    # Густа гребінка
    tick_count = 40
    for i in range(tick_count):
        tx = TL + i * (timeline_w / tick_count)
        parts.append(line(tx, AR_Y, tx, AR_Y - 22, color=POS, sw=1.5))
    parts.append(text(TR + 5, AR_Y + 4, "↑ 20000 ISR/с", size=10, color=POS, anchor="start"))

    # --- DMA (раз на блок) ---
    DMA_Y = 210
    parts.append(text(TL - 10, DMA_Y + 12, "АЦП+DMA\n(20 кГц)", size=12, color=FIELD, anchor="end"))
    parts.append(line(TL, DMA_Y, TR, DMA_Y, color=MUTED, sw=1))
    block_count = 5
    for i in range(block_count):
        tx = TL + (i + 0.5) * (timeline_w / block_count)
        parts.append(line(tx, DMA_Y, tx, DMA_Y - 30, color=FIELD, sw=3))
        blk_box, _, _ = textbox(tx, DMA_Y - 46, f"блок {i+1}", size=9, fill="#d4edda", stroke=FIELD, sw=1)
        parts.append(blk_box)
    parts.append(text(TR + 5, DMA_Y + 4, "↑ ~24 ISR/с", size=10, color=FIELD, anchor="start"))

    # Порівняльна стрілка
    ratio_box, _, _ = textbox((TL+TR)//2, 280,
                               "DMA: у 20000/24 ≈ 800 разів рідше пробуджує ядро\n(той самий потік 20 кГц)",
                               size=13, fill="#d4edda", stroke=FIELD, sw=2)
    parts.append(ratio_box)

    render(out("fig-4-9-5-3-wakeup-rate.svg"), W, H, *parts)
    print("fig-4-9-5-3-wakeup-rate.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.6.1 — буфер → шина через DMA
# ══════════════════════════════════════════════════════════════════════════════
def fig_961_block_to_bus():
    W, H = 720, 300
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.6.1 — DMA виливає блок із RAM у швидку послідовну шину", size=15, bold=True))

    # RAM буфер
    ram_box, rw, rh = textbox(130, 150, "Буфер у SRAM\n(кадр / аудіоблок)\n320×240×2 = 150 кБ", size=13, fill=FILL, stroke=LINE, sw=2, min_w=160)
    parts.append(ram_box)

    # DMA
    dma_box, dw, dh = textbox(360, 150, "DMA-канал\n(передача блоку)", size=13, fill="#d4edda", stroke=FIELD, sw=2, min_w=150)
    parts.append(dma_box)
    parts.append(arrow(130 + rw//2 + 2, 150, 360 - dw//2 - 2, 150))

    # Шина (права)
    bus_box, bw, bh = textbox(570, 150, "Послідовна\nшина\n(швидка)", size=13, fill="#eaf0fd", stroke=NEG, sw=2, min_w=110)
    parts.append(bus_box)
    parts.append(arrow(360 + dw//2 + 2, 150, 570 - bw//2 - 2, 150))

    # DMA-запит від шини
    req_box, _, _ = textbox(465, 200, "DMA-запит\n(готово до слова)", size=11, fill="#fff9e6", stroke="#e0a800", sw=1.5)
    parts.append(req_box)
    parts.append(arrow(570 - bw//2, 175, 465 + 20, 190))

    # Ядро вільне (внизу)
    cpu_box, _, _ = textbox(360, 258, "Ядро вільне — рахує наступний кадр / інші задачі", size=12, fill="#f0f0f0", stroke=MUTED, sw=1.5)
    parts.append(cpu_box)
    parts.append(f'<line x1="360" y1="{150+dh//2+4}" x2="360" y2="242" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3"/>')

    # Пояснення
    parts.append(text(W//2, H - 15, "Шина автоматично смикає DMA-запит на кожне готове слово — ядро не бере участь", size=11, color=MUTED))

    render(out("fig-4-9-6-1-block-to-bus.svg"), W, H, *parts)
    print("fig-4-9-6-1-block-to-bus.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.6.2 — jitter vs smooth frame
# ══════════════════════════════════════════════════════════════════════════════
def fig_962_frame_jitter():
    W, H = 720, 380
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.6.2 — Виливання кадру: ривками (без DMA) vs рівно (з DMA)", size=15, bold=True))

    TL, TR = 80, 660
    tw = TR - TL

    # === Без DMA ===
    ND_Y = 110
    parts.append(text(TL - 10, ND_Y + 12, "Без DMA", size=13, bold=True, color=POS, anchor="end"))
    parts.append(line(TL, ND_Y, TR, ND_Y, color=MUTED, sw=1))

    # Блоки передачі (ривками — з паузами)
    nd_segs = [(0, 60), (80, 50), (150, 70), (240, 40), (300, 65), (390, 55), (465, 75)]
    for start, dur in nd_segs:
        bx = TL + start
        parts.append(rect(bx, ND_Y - 30, dur, 28, fill="#f8d7da", stroke=POS, sw=1.2, rx=3))
    # Паузи
    parts.append(text(TL + 145, ND_Y - 40, "провали (ядро пішло на ISR)", size=10, color=POS))

    # FPS нерівний
    fps_box, _, _ = textbox(TR - 60, ND_Y + 20, "нерівний FPS\n«смикається»", size=11, fill="#fdecea", stroke=POS)
    parts.append(fps_box)

    # === З DMA ===
    DMA_Y = 240
    parts.append(text(TL - 10, DMA_Y + 12, "З DMA", size=13, bold=True, color=FIELD, anchor="end"))
    parts.append(line(TL, DMA_Y, TR, DMA_Y, color=MUTED, sw=1))

    # Безперервна смуга DMA
    parts.append(rect(TL, DMA_Y - 30, tw - 10, 28, fill="#d4edda", stroke=FIELD, sw=1.5, rx=3))
    parts.append(text(TL + (tw-10)//2, DMA_Y - 14, "DMA рівний потік (шина завантажена рівномірно)", size=11, color=FIELD))

    # Ядро рахує паралельно
    parts.append(rect(TL, DMA_Y + 10, tw - 10, 24, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    parts.append(text(TL + (tw-10)//2, DMA_Y + 26, "Ядро: рахує наступний кадр паралельно", size=11, color=NEG))

    fps_box2, _, _ = textbox(TR - 60, DMA_Y + 52, "рівний FPS\nплавна картинка", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(fps_box2)

    # Підсумок
    sum_box, _, _ = textbox(W//2, H - 28,
                             "Без DMA: кадр залежить від завантаженості ядра → тряска. "
                             "З DMA: шина не чекає на ядро → плавно.",
                             size=12, fill=FILL, stroke=MUTED)
    parts.append(sum_box)

    render(out("fig-4-9-6-2-frame-jitter.svg"), W, H, *parts)
    print("fig-4-9-6-2-frame-jitter.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.7.1 — когерентність кешу
# ══════════════════════════════════════════════════════════════════════════════
def fig_971_cache_coherency():
    W, H = 720, 440
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.7.1 — Пастка когерентності кешу (обидва напрями)", size=15, bold=True))

    # Три шари: ядро+кеш, RAM, DMA
    LAYER_X = [100, 360, 580]
    LAYER_LABELS = ["Ядро + Кеш\n(Xtensa)", "SRAM\n(фізична пам'ять)", "DMA-контролер"]
    LAYER_COLORS = [("#eaf0fd", NEG), (FILL, LINE), ("#d4edda", FIELD)]

    for i, (lx, lbl, (fill_c, stroke_c)) in enumerate(zip(LAYER_X, LAYER_LABELS, LAYER_COLORS)):
        b, bw, bh = textbox(lx, 100, lbl, size=12, fill=fill_c, stroke=stroke_c, sw=2, min_w=130)
        parts.append(b)

    # ---- Випадок 1: DMA записав нове → ядро читає старе (invalidate) ----
    C1_Y = 190
    parts.append(text(100, C1_Y - 15, "Читання (DMA → RAM → Ядро):", size=12, bold=True, color=INK, anchor="start"))

    # DMA записав у RAM
    parts.append(arrow(580, C1_Y + 10, 360 + 65, C1_Y + 10))
    new_box, _, _ = textbox(470, C1_Y + 10, "нові дані", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(new_box)

    # Кеш: стара копія
    stale_box, _, _ = textbox(100, C1_Y + 10, "стара копія\n(stale)", size=11, fill="#fdecea", stroke=POS)
    parts.append(stale_box)

    # Ядро читає стале
    parts.append(f'<line x1="165" y1="{C1_Y+10}" x2="295" y2="{C1_Y+10}" stroke="{POS}" stroke-width="2" stroke-dasharray="4 3" marker-end="url(#arrow)"/>')
    danger_box, _, _ = textbox(230, C1_Y + 50, "ядро бачить СТАЛЕ → треба INVALIDATE перед читанням", size=11, fill="#fdecea", stroke=POS)
    parts.append(danger_box)

    # ---- Випадок 2: Ядро поклало нове в кеш → RAM стара → DMA повіз старе (flush) ----
    C2_Y = 300
    parts.append(text(100, C2_Y - 15, "Запис (Ядро → кеш → RAM, DMA читає):", size=12, bold=True, color=INK, anchor="start"))

    new2_box, _, _ = textbox(100, C2_Y + 10, "нові дані\n(в кеші)", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(new2_box)

    stale2_box, _, _ = textbox(360, C2_Y + 10, "RAM ще стара\n(не скинуто)", size=11, fill="#fdecea", stroke=POS)
    parts.append(stale2_box)

    # DMA бере старе з RAM
    parts.append(arrow(360 + 65, C2_Y + 10, 580 - 65, C2_Y + 10))
    dma2_box, _, _ = textbox(470, C2_Y + 10, "DMA бере\nСТАРЕ!", size=11, fill="#fdecea", stroke=POS)
    parts.append(dma2_box)

    flush_box, _, _ = textbox(W//2, C2_Y + 60, "треба WRITE-BACK / FLUSH перед стартом DMA", size=12, fill="#fff9e6", stroke="#e0a800", sw=2)
    parts.append(flush_box)

    # Підсумок
    sum_box, _, _ = textbox(W//2, H - 28, "DMA обходить кеш — мінімум два виклики: flush (до DMA) + invalidate (після DMA)", size=12, fill=FILL, stroke=MUTED)
    parts.append(sum_box)

    render(out("fig-4-9-7-1-cache-coherency.svg"), W, H, *parts)
    print("fig-4-9-7-1-cache-coherency.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.7.2 — вирівнювання і розміщення буфера
# ══════════════════════════════════════════════════════════════════════════════
def fig_972_buffer_alignment():
    W, H = 740, 400
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.7.2 — Вирівнювання й розміщення DMA-буфера", size=15, bold=True))

    # ---- Ліворуч: ПОГАНО ----
    LX = 60
    parts.append(text(LX + 140, 58, "ПОГАНО", size=14, bold=True, color=POS))

    # Стек задачі (прямокутник)
    stack_box = fitbox(LX, 75, 280, 200, "Стек задачі\n(4–8 кБ)", size=12, fill="#f8d7da", stroke=POS, sw=2)
    parts.append(stack_box)

    # Буфер всередині стека
    buf_box, _, _ = textbox(LX + 140, 175, "uint8_t buf[1024];\n(невирівняний, на стеку)", size=11, fill="#fdecea", stroke=POS)
    parts.append(buf_box)

    # Сусідні дані (пошкоджені)
    parts.append(rect(LX + 60, 240, 160, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    parts.append(text(LX + 140, 256, "сусідні змінні → пошкоджені!", size=10, color=POS))

    # PSRAM (небезпечна)
    psram_box, _, _ = textbox(LX + 140, 310, "або: у PSRAM без flush/invalidate\n→ DMA бере старе / пише повз кеш", size=11, fill="#f8d7da", stroke=POS)
    parts.append(psram_box)

    # ---- Праворуч: ДОБРЕ ----
    RX = 400
    parts.append(text(RX + 140, 58, "ДОБРЕ", size=14, bold=True, color=FIELD))

    # Internal SRAM (безпечна)
    sram_box = fitbox(RX, 75, 280, 200, "Internal SRAM\n(DMA-придатна)", size=12, fill="#d4edda", stroke=FIELD, sw=2)
    parts.append(sram_box)

    # Атрибут вирівнювання
    attr_box, _, _ = textbox(RX + 140, 145, "DMA_ATTR\nstatic uint8_t buf[1024];", size=11, fill="#eaf0fd", stroke=NEG)
    parts.append(attr_box)

    # Вирівнювання на межу рядка кешу
    align_box, _, _ = textbox(RX + 140, 210, "вирівняно по 32/64 байти\n(cache-line boundary)", size=11, fill="#d4edda", stroke=FIELD)
    parts.append(align_box)

    # Static (довгий час життя)
    parts.append(text(RX + 140, 265, "static: час життя = весь рантайм", size=11, color=FIELD))

    # Результат
    ok_box, _, _ = textbox(RX + 140, 310, "flush + invalidate на місці\n→ DMA завжди бачить актуальне", size=11, fill="#d4edda", stroke=FIELD, sw=1.5)
    parts.append(ok_box)

    # Роздільна лінія
    parts.append(line(W//2 - 2, 65, W//2 - 2, H - 20, color=MUTED, sw=2, dash="6 4"))

    render(out("fig-4-9-7-2-buffer-alignment.svg"), W, H, *parts)
    print("fig-4-9-7-2-buffer-alignment.svg")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.9.7.3 — чек-лист DMA (блок-схема рішень)
# ══════════════════════════════════════════════════════════════════════════════
def fig_973_dma_checklist():
    W, H = 700, 500
    parts = []
    parts.append(text(W/2, 28, "Рис. 4.9.7.3 — Чек-лист DMA-буфера (схема прийняття рішень)", size=15, bold=True))

    checks = [
        ("Буфер вирівняний по межі\nрядка кешу (cache-line)?", "#fff9e6", "#e0a800"),
        ("Буфер у DMA-придатній пам'яті\n(internal SRAM, статичний)?", "#fff9e6", "#e0a800"),
        ("Flush/invalidate\nна місці?", "#fff9e6", "#e0a800"),
        ("Власник буфера зараз —\nлише ядро АБО лише DMA?", "#fff9e6", "#e0a800"),
    ]
    bugs = [
        "пошкодження\nсусідніх даних",
        "DMA відмовляє /\nHardFault / PSRAM-глюк",
        "stale дані /\nDMA повіз старе",
        "гонка → навзамін\nпошкоджений буфер",
    ]

    CX = 280
    START_Y = 70
    STEP_Y = 95
    YES_X = CX + 180
    NO_X = CX - 130

    for i, ((q, fill_c, stroke_c), bug) in enumerate(zip(checks, bugs)):
        qy = START_Y + i * STEP_Y
        # Ромб
        d = 34
        parts.append(f'<polygon points="{CX},{qy-d} {CX+90},{qy} {CX},{qy+d} {CX-90},{qy}" '
                     f'fill="{fill_c}" stroke="{stroke_c}" stroke-width="2"/>')
        q_b = fitbox(CX - 85, qy - d + 5, 170, d * 2 - 10, q, size=10, fill=fill_c, stroke="none")
        parts.append(q_b)

        # "ТАК" → продовжити вниз
        if i < len(checks) - 1:
            parts.append(arrow(CX, qy + d, CX, qy + STEP_Y - d - 2))
            yes_b, _, _ = textbox(CX + 18, qy + d + 18, "ТАК", size=11, fill="#d4edda", stroke=FIELD, sw=1)
            parts.append(yes_b)

        # "НІ" → баг
        bug_x = NO_X - 80
        parts.append(arrow(CX - 90, qy, bug_x + 80, qy))
        no_b, _, _ = textbox(CX - 90 - 18, qy - 14, "НІ", size=11, fill="#fdecea", stroke=POS, sw=1)
        parts.append(no_b)
        bug_b, _, _ = textbox(bug_x, qy, bug, size=10, fill="#fdecea", stroke=POS, sw=1.5)
        parts.append(bug_b)

    # Фінальний блок "SAFE"
    fin_y = START_Y + len(checks) * STEP_Y - 10
    fin_b, fw, fh = textbox(CX, fin_y, "✓ DMA-буфер безпечний\nможна запускати передачу", size=13, fill="#d4edda", stroke=FIELD, sw=2.5)
    parts.append(fin_b)
    parts.append(arrow(CX, START_Y + (len(checks)-1)*STEP_Y + 34, CX, fin_y - fh//2 - 2))
    parts.append(text(CX + 18, START_Y + (len(checks)-1)*STEP_Y + 50, "ТАК", size=11, color=FIELD))

    render(out("fig-4-9-7-3-dma-checklist.svg"), W, H, *parts)
    print("fig-4-9-7-3-dma-checklist.svg")


# ══════════════════════════════════════════════════════════════════════════════
# ЗАПУСК УСІХ ФУНКЦІЙ
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_911_event_cost()
    fig_912_cpu_budget()
    fig_921_dma_on_bus()
    fig_922_with_without_dma()
    fig_931_channels()
    fig_932_descriptor_list()
    fig_933_bus_arbitration()
    fig_941_pingpong_phases()
    fig_942_ring_buffer()
    fig_943_overrun_timing()
    fig_951_adc_dma_chain()
    fig_952_sample_element()
    fig_953_wakeup_rate()
    fig_961_block_to_bus()
    fig_962_frame_jitter()
    fig_971_cache_coherency()
    fig_972_buffer_alignment()
    fig_973_dma_checklist()
    print("Усі фігури згенеровано.")
