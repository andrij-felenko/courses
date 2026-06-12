# -*- coding: utf-8 -*-
"""
Фігури для 📜 r09-s6-history-soundblaster
(Sound Blaster і канал DMA 1: чому геймери 90-х знали це слово)

Три фігури:
  fig-r09-h1-1-isa-bus.svg      — шина ISA і як Sound Blaster займає канал DMA
  fig-r09-h1-2-dma-flow.svg     — порівняння: CPU-loop vs DMA-loop (звук)
  fig-r09-h1-3-timeline.svg     — хронологія Creative / Sound Blaster 1988–1994

Запуск: python figs-r09-s6-history-soundblaster.py
Вивід → ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.9.Hi.1 — Шина ISA: хто кому ім'я «DMA 1» подарував ────────────────
def fig1_isa_bus():
    W, H = 860, 420

    parts = []
    parts.append(text(W / 2, 28, "Шина ISA і канал DMA 1 Sound Blaster'а", size=17, bold=True))
    parts.append(text(W / 2, 50,
                      "ISA надавала 8 DMA-каналів; SB заліз на канал 1 — і залишився там назавжди",
                      size=11, color=MUTED))

    # ── Шина ISA як горизонтальна смуга ──
    BUS_Y  = 200
    BUS_H  = 28
    BUS_X0 = 60
    BUS_W  = W - 120

    parts.append(rect(BUS_X0, BUS_Y - BUS_H // 2, BUS_W, BUS_H,
                      fill="#e8eef8", stroke="#4a6fa5", sw=2.5, rx=4))
    parts.append(text(W / 2, BUS_Y + 6, "ISA-шина (Industry Standard Architecture, 8 МГц)",
                      size=11, color="#4a6fa5", bold=True))

    # ── Слоти / пристрої над шиною ──
    devices_top = [
        ("IRQ 5\nDMA 1\n0x220", "Sound Blaster", "#c0392b", 160),
        ("IRQ 3\n—", "COM2\n(модем)", LINE, 310),
        ("IRQ 14\nDMA —", "IDE\nконтролер", LINE, 460),
        ("IRQ 12\n—", "PS/2\nмиша", LINE, 610),
        ("IRQ 1\n—", "Клавіатура", LINE, 750),
    ]

    for addr, label, col, cx in devices_top:
        # Вертикальна лінія-штекер
        parts.append(line(cx, BUS_Y - BUS_H // 2, cx, BUS_Y - 90, color=col, sw=2))
        # Картка пристрою
        tb, bw, bh = textbox(cx, BUS_Y - 90 - 36, label, size=12, pad=10,
                              fill="#fafafa" if col == LINE else "#fff0f0",
                              stroke=col, sw=2, bold=False, min_w=90)
        parts.append(tb)
        # Адреси/ресурси
        parts.append(text(cx, BUS_Y - 90 - 36 + bh // 2 + 16, addr,
                          size=9, color=col, anchor="middle"))

    # ── DMA-контролер під шиною ──
    DMA_Y = 290
    tb_dma, dw, dh = textbox(W // 2, DMA_Y,
                              "Intel 8237A\nDMA-контролер\nканали 0–7",
                              size=13, pad=14, fill="#f0fff4",
                              stroke="#27ae60", sw=2, min_w=180)
    parts.append(tb_dma)
    parts.append(line(W // 2, BUS_Y + BUS_H // 2, W // 2, DMA_Y - dh // 2,
                      color="#27ae60", sw=2))
    parts.append(text(W // 2 + 10, (BUS_Y + BUS_H // 2 + DMA_Y - dh // 2) // 2,
                      "DMA-запити\n(DREQ/DACK)", size=9, color="#27ae60", anchor="start"))

    # ── Виноска: чому саме канал 1 ──
    note = "Канал 0 — DRAM-refresh (не чіпай!)\nКанал 1 — вільний у PC/XT → SB взяв перший вільний"
    tb_note, nw, nh = textbox(W // 2, H - 28, note, size=10, pad=10,
                               fill="#fff8e1", stroke="#e08030", sw=1.5, min_w=520)
    parts.append(tb_note)

    render(os.path.join(OUT, "fig-r09-h1-1-isa-bus.svg"), W, H, *parts)
    print("wrote fig-r09-h1-1-isa-bus.svg")


# ── Рис. 4.9.Hi.2 — CPU-loop vs DMA-loop: що насправді робить CPU ────────────
def fig2_dma_flow():
    W, H = 860, 460

    parts = []
    parts.append(text(W / 2, 28, "CPU-loop проти DMA: що робить процесор під час звуку", size=17, bold=True))
    parts.append(text(W / 2, 50,
                      "зліва — CPU тягне кожен байт сам; справа — DMA-канал, CPU вільний",
                      size=11, color=MUTED))

    MID = W // 2

    # ── Ліва колонка: без DMA ──
    parts.append(text(MID // 2, 80, "Без DMA (Covox / порт LPT)", size=13, bold=True, color=POS))

    # CPU-box
    tb_cpu, cw, ch = textbox(MID // 2, 150, "CPU\n(8086 / 286)", size=13, pad=12,
                              fill="#fdecea", stroke=POS, sw=2, min_w=130)
    parts.append(tb_cpu)

    # buffer-box
    tb_buf, bw, bh = textbox(MID // 2, 260, "PCM-буфер\n(RAM)", size=12, pad=10,
                              fill=FILL, stroke=LINE, sw=1.5, min_w=130)
    parts.append(tb_buf)

    # DAC-box
    tb_dac, dw, dh = textbox(MID // 2, 360, "DAC / динамік", size=12, pad=10,
                              fill=FILL, stroke=LINE, sw=1.5, min_w=130)
    parts.append(tb_dac)

    # Стрілки (CPU тягне кожен байт)
    parts.append(arrow(MID // 2, 150 + ch // 2, MID // 2, 260 - bh // 2, color=POS, sw=2))
    parts.append(text(MID // 2 + 8, 205, "читає байт", size=9, color=POS, anchor="start"))
    parts.append(arrow(MID // 2, 260 + bh // 2, MID // 2, 360 - dh // 2, color=POS, sw=2))
    parts.append(text(MID // 2 + 8, 310, "OUT port", size=9, color=POS, anchor="start"))

    # Хмарка «overhead» зверху CPU
    tb_ovh, ow, oh = textbox(MID // 2, 90,
                              "~8 000 циклів/с\n→ 8% CPU @ 10 МГц",
                              size=9, pad=7, fill="#fef9e7",
                              stroke="#e67e22", sw=1.2, min_w=160)
    parts.append(tb_ovh)

    # ── Вертикальний роздільник ──
    parts.append(line(MID, 70, MID, H - 30, color=MUTED, sw=1.5, dash="6,4"))

    # ── Права колонка: DMA ──
    RX = MID + (W - MID) // 2
    parts.append(text(RX, 80, "З DMA (Sound Blaster)", size=13, bold=True, color=FIELD))

    # CPU-box (відпочиває)
    tb_cpu2, cw2, ch2 = textbox(RX, 150, "CPU\n(вільний!)", size=13, pad=12,
                                 fill="#f0fff4", stroke=FIELD, sw=2, min_w=130)
    parts.append(tb_cpu2)

    # DMA-box
    tb_dma, dmw, dmh = textbox(RX, 260, "DMA 8237\nканал 1", size=12, pad=10,
                                fill="#e8f8f5", stroke=FIELD, sw=1.5, min_w=130)
    parts.append(tb_dma)

    # DAC-box
    tb_dac2, dw2, dh2 = textbox(RX, 360, "DAC / динамік", size=12, pad=10,
                                 fill=FILL, stroke=LINE, sw=1.5, min_w=130)
    parts.append(tb_dac2)

    # Стрілки DMA
    parts.append(arrow(RX, 260 + dmh // 2, RX, 360 - dh2 // 2, color=FIELD, sw=2))
    parts.append(text(RX + 8, 310, "DREQ/DACK", size=9, color=FIELD, anchor="start"))

    # CPU → DMA (тільки setup)
    parts.append(line(RX, 150 + ch2 // 2, RX, 260 - dmh // 2, color="#aaaaaa", sw=1.5, dash="4,3"))
    parts.append(text(RX + 8, 205, "програмує\n(один раз)", size=9, color=MUTED, anchor="start"))

    # Хмарка «overhead»
    tb_ovh2, ow2, oh2 = textbox(RX, 90,
                                 "< 1% CPU\n(тільки ISR на кінець буфера)",
                                 size=9, pad=7, fill="#f0fff4",
                                 stroke=FIELD, sw=1.2, min_w=200)
    parts.append(tb_ovh2)

    # ── Нижня рамка ──
    note = "DMA передає байти автономно: CPU отримує переривання ЛИШЕ коли буфер закінчився"
    tb_n, nw, nh = textbox(W // 2, H - 24, note, size=10, pad=10,
                            fill="#f0f4ff", stroke="#4a6fa5", sw=1.5, min_w=660)
    parts.append(tb_n)

    render(os.path.join(OUT, "fig-r09-h1-2-dma-flow.svg"), W, H, *parts)
    print("wrote fig-r09-h1-2-dma-flow.svg")


# ── Рис. 4.9.Hi.3 — Хронологія Sound Blaster 1988–1994 ──────────────────────
def fig3_timeline():
    W, H = 860, 340

    parts = []
    parts.append(text(W / 2, 28, "Еволюція Sound Blaster: 1988–1994", size=17, bold=True))
    parts.append(text(W / 2, 50, "кожне покоління — нова ставка; DMA-канал 1 незмінний",
                      size=11, color=MUTED))

    events = [
        (1988, "Creative\nMusic System\n(прото-SB)"),
        (1989, "Sound Blaster\n1.0\n8-біт моно"),
        (1991, "Sound Blaster\nPro\n8-біт стерео"),
        (1992, "Sound Blaster\n16\n16-біт, 44.1 кГц"),
        (1994, "Sound Blaster\nAWE32\n(банк SF2)"),
    ]

    YEAR_MIN, YEAR_MAX = 1987, 1995
    TL_Y   = 185
    TL_X0  = 80
    TL_X1  = W - 80

    def year_x(yr):
        return TL_X0 + (yr - YEAR_MIN) / (YEAR_MAX - YEAR_MIN) * (TL_X1 - TL_X0)

    # ── Лінія часу ──
    parts.append(arrow(TL_X0, TL_Y, TL_X1, TL_Y, color=LINE, sw=2.5))
    for yr in range(YEAR_MIN + 1, YEAR_MAX + 1):
        x = year_x(yr)
        parts.append(line(x, TL_Y - 6, x, TL_Y + 6, color=LINE, sw=1.5))
        parts.append(text(x, TL_Y + 20, str(yr), size=10, color=MUTED))

    # ── Мітки подій ──
    colors = [NEG, "#2457d6", "#27ae60", "#c0392b", "#8e44ad"]
    for i, (yr, label) in enumerate(events):
        x = year_x(yr)
        col = colors[i % len(colors)]
        # Гілка догори
        parts.append(line(x, TL_Y, x, TL_Y - 60, color=col, sw=2))
        tb, bw, bh = textbox(x, TL_Y - 60 - 38, label, size=10, pad=8,
                              fill=FILL, stroke=col, sw=1.8, min_w=100)
        parts.append(tb)

    # ── Нижня рамка: DMA залишився той самий ──
    note = "У всіх моделях: IRQ 5 + DMA 1 — ці ресурси «заморозились» у DOS-сумісності до кінця епохи ISA"
    tb_n, nw, nh = textbox(W // 2, H - 24, note, size=10, pad=10,
                            fill="#fff8e1", stroke="#e08030", sw=1.5, min_w=640)
    parts.append(tb_n)

    render(os.path.join(OUT, "fig-r09-h1-3-timeline.svg"), W, H, *parts)
    print("wrote fig-r09-h1-3-timeline.svg")


if __name__ == "__main__":
    fig1_isa_bus()
    fig2_dma_flow()
    fig3_timeline()
    print("Done.")
