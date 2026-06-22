# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── block-diagram: DRAM усередині, SRAM назовні ───────────────────────────────
# Ідея: усередині чипа — масив комірок DRAM (транзистор+конденсатор) і схований
# лічильник самооновлення; назовні — простий інтерфейс, що вдає SRAM. Поряд —
# процесор і флеш на тій самій шині.

def fig_block_diagram():
    W, H = 720, 360
    p = []

    # процесор зліва
    pb, pw, ph = textbox(110, 150, "Процесор\n+ кеш", size=13, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, pad=16)
    p.append(pb)

    # корпус PSRAM справа — велика рамка
    chx, chy, chw, chh = 350, 64, 340, 240
    p.append(rect(chx, chy, chw, chh, fill=BG, stroke=INK, sw=2.2))
    p.append(text(chx + chw / 2, chy + 22, "мікросхема PSRAM", size=13, bold=True))

    # масив комірок DRAM усередині
    p.append(fitbox(chx + 22, chy + 44, 150, 104,
                    "масив комірок DRAM\n(транзистор +\nконденсатор)",
                    size=11, fill="#fdf4f4", stroke=POS, sw=1.6))
    # схований лічильник самооновлення
    p.append(fitbox(chx + 184, chy + 44, 134, 104,
                    "схований\nлічильник\nсамооновлення",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.6))
    # інтерфейс, що вдає SRAM
    p.append(fitbox(chx + 22, chy + 162, 296, 52,
                    "інтерфейс SPI / QSPI —\nназовні поводиться як SRAM",
                    size=11, bold=True, fill="#f6efd6", stroke=INK, sw=1.6))

    # шина процесор → PSRAM
    p.append(arrow(110 + pw / 2, 150, chx - 2, 150, color=INK, sw=2.0))
    p.append(text((110 + pw / 2 + chx) / 2, 138, "SPI / QSPI", size=11, color=MUTED, bold=True))
    p.append(text((110 + pw / 2 + chx) / 2, 168, "(послідовно)", size=10, color=MUTED, italic=True))

    # флеш знизу на тій самій шині
    fb, fw, fh = textbox(110, 280, "Flash\n(код, нелетка)", size=11,
                         fill="#f4f6f8", stroke=MUTED, sw=1.5, pad=12)
    p.append(fb)
    p.append(line(110, 150 + ph / 2, 110, 280 - fh / 2, color=MUTED, sw=1.4, dash="5 4"))

    p.append(text(W / 2, H - 16,
                  "динамічна за фізикою, статична на вигляд: возню з регенерацією чип бере на себе",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "block-diagram.svg"), W, H, *p,
           title="PSRAM: DRAM усередині, SRAM назовні")


# ── shared-bus: PSRAM і Flash на спільних лініях, різний CE# ───────────────────
# Ідея: вісім ніжок SOIC-8; такт і дані спільні в двох чипів, розрізняє лише
# окремий сигнал вибору CE#.

def fig_shared_bus():
    W, H = 720, 320
    p = []

    # контролер ліворуч
    cb, cw, ch = textbox(95, 150, "Контролер\nзовнішньої\nпам'яті", size=12, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, pad=14)
    p.append(cb)

    bx = 95 + cw / 2
    # спільні лінії: SCLK + IO0..IO3
    lines_y = [96, 116, 136, 156, 176]
    labels = ["SCLK", "IO0", "IO1", "IO2", "IO3"]
    rail_x = 470
    for ly, lab in zip(lines_y, labels):
        p.append(line(bx, ly, rail_x, ly, color=INK, sw=1.6))
        p.append(text(bx + 8, ly - 4, lab, size=9, color=MUTED, anchor="start"))

    # два окремі CE#
    p.append(line(bx, 210, rail_x, 210, color=POS, sw=1.8))
    p.append(text(bx + 8, 206, "CE# (PSRAM)", size=9, color=POS, anchor="start"))
    p.append(line(bx, 240, rail_x, 240, color=FIELD, sw=1.8))
    p.append(text(bx + 8, 236, "CE# (Flash)", size=9, color=FIELD, anchor="start"))

    # два чипи праворуч
    p.append(fitbox(rail_x, 86, 150, 100, "PSRAM\nSOIC-8\n(летка RAM)",
                    size=11, bold=True, fill="#fdf4f4", stroke=POS, sw=1.8))
    p.append(fitbox(rail_x, 200, 150, 90, "Flash\nSOIC-8\n(нелеткий код)",
                    size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8))

    # під'єднання CE# до відповідних чипів
    p.append(line(rail_x, 210, rail_x, 136, color=POS, sw=1.6))  # до PSRAM зони
    p.append(circle(rail_x, 136, 3, fill=POS, stroke=POS))
    p.append(circle(rail_x, 240, 3, fill=FIELD, stroke=FIELD))

    p.append(text(W / 2, H - 14,
                  "такт і дані спільні; контролер опускає потрібний CE# — і говорить саме з тим чипом",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "shared-bus.svg"), W, H, *p,
           title="Спільна шина: PSRAM і Flash, різний лише вибір чипа")


# ── latency-ladder: драбина затримки доступу ──────────────────────────────────
# Ідея: сходинки від регістра до промаху в PSRAM; видно, де PSRAM «як SRAM»
# (влучання) і де провалюється (промах по шині).

def fig_latency_ladder():
    W, H = 720, 340
    p = []
    steps = [
        ("регістр у ядрі", 0.4, "0 тактів", NEG, "#eef4ff"),
        ("вбудована SRAM", 1.0, "1–2 такти", FIELD, "#eafaf0"),
        ("влучання в кеш PSRAM", 1.3, "як SRAM", FIELD, "#eafaf0"),
        ("промах у PSRAM", 4.2, "десятки тактів, по шині", POS, "#fdecea"),
    ]
    bx, base_y, bw = 70, 280, 150
    gap = 14
    unit = 46  # px на «такт-висоту»
    x = bx
    for lab, h, note, col, fill in steps:
        bh = h * unit
        p.append(rect(x, base_y - bh, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(fitbox(x, base_y - bh, bw, min(bh, 40), lab, size=10, bold=True,
                        fill="none", stroke="none", color=INK))
        p.append(text(x + bw / 2, base_y + 18, note, size=9, color=col, bold=True))
        x += bw + gap

    p.append(line(bx, base_y, x - gap, base_y, color=INK, sw=1.6))
    p.append(text(W / 2, H - 14,
                  "чим далі вправо — тим довше чекати; PSRAM добра, поки потрібне вже в кеші",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "latency-ladder.svg"), W, H, *p,
           title="Драбина затримки доступу до пам'яті")


# ── what-goes-where: що класти в PSRAM, що лишати у SRAM ───────────────────────
# Ідея: дві колонки — велике й нечасте → PSRAM; гаряче й критичне → вбудована SRAM.

def fig_what_goes_where():
    W, H = 720, 320
    p = []

    # ліва колонка — PSRAM
    p.append(rect(50, 60, 300, 230, fill="#fdf7f0", stroke=POS, sw=1.8))
    p.append(text(200, 86, "У PSRAM: велике й нечасте", size=12, bold=True, color=POS))
    psram_items = ["кадр дисплея (framebuffer)", "буфер звуку", "кеш зображень",
                   "довгий рядок / документ", "великі таблиці й моделі"]
    for i, it in enumerate(psram_items):
        p.append(text(72, 118 + i * 30, "• " + it, size=11, color=INK, anchor="start"))

    # права колонка — SRAM
    p.append(rect(370, 60, 300, 230, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(520, 86, "У вбудованій SRAM: гаряче", size=12, bold=True, color=FIELD))
    sram_items = ["змінні гарячих циклів", "обробники переривань (ISR)",
                  "буфери під DMA периферії", "стек і дрібні часті дані",
                  "усе критичне за часом"]
    for i, it in enumerate(sram_items):
        p.append(text(392, 118 + i * 30, "• " + it, size=11, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "критерій один: повільність губиться лише на великому й рідкому",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "what-goes-where.svg"), W, H, *p,
           title="Куди що класти: PSRAM проти вбудованої SRAM")


# ── address-tells: за адресою видно, де байт ──────────────────────────────────
# Ідея: смуга адресного простору; малий діапазон SRAM (швидко) і великий
# діапазон PSRAM (місткі буфери) — за адресою одразу зрозуміло, де дані.

def fig_address_tells():
    W, H = 720, 250
    p = []
    bx, by, bw, bh = 70, 110, 580, 56

    # вбудована SRAM — вузька швидка смужка
    sram_w = bw * 0.16
    p.append(rect(bx, by, sram_w, bh, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=0))
    p.append(fitbox(bx, by, sram_w, bh, "SRAM\nшвидко", size=10, bold=True,
                    fill="none", stroke="none", color=FIELD))

    # PSRAM — широкий повільний діапазон
    px = bx + sram_w
    p.append(rect(px, by, bw - sram_w, bh, fill="#fdf4f4", stroke=POS, sw=1.8, rx=0))
    p.append(fitbox(px, by, bw - sram_w, bh,
                    "PSRAM — великий діапазон під місткі буфери (до 4 МіБ у вікні адрес)",
                    size=11, bold=True, fill="none", stroke="none", color=POS))

    # підписи адрес
    p.append(text(bx, by - 12, "малі адреси", size=10, color=MUTED, anchor="start"))
    p.append(text(bx + bw, by - 12, "великі адреси", size=10, color=MUTED, anchor="end"))

    p.append(text(W / 2, H - 24,
                  "за адресою байта одразу видно, де він: малий діапазон — гарячі дані, великий — буфери",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "address-tells.svg"), W, H, *p,
           title="Адреса сама каже, у якій пам'яті байт")


if __name__ == "__main__":
    fig_block_diagram()
    fig_shared_bus()
    fig_latency_ladder()
    fig_what_goes_where()
    fig_address_tells()
    print("OK: figures written to", OUT)
