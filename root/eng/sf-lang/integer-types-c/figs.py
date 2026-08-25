# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── types-map: дві осі — знаковість × ширина ─────────────────────────────────
# Ідея: цілий тип задається ДВОМА незалежними виборами — скільки бітів (ширина)
# і як тлумачити старший біт (знаковий/беззнаковий). Таблиця 2×4 з діапазонами.
def fig_types_map():
    W, H = 720, 340
    p = []
    # заголовки стовпців — ширина
    widths = ["8 біт", "16 біт", "32 біти", "64 біти"]
    x0, y0 = 150, 78
    cw, ch = 132, 96
    for j, w in enumerate(widths):
        p.append(text(x0 + j * cw + cw / 2, y0 - 14, w, size=13, bold=True, color=INK))
    # підписи рядків — знаковість
    p.append(text(x0 - 16, y0 + ch / 2 + 5, "беззнак.", size=12, bold=True, color=NEG, anchor="end"))
    p.append(text(x0 - 16, y0 + ch + ch / 2 + 5, "знакові", size=12, bold=True, color=POS, anchor="end"))

    # беззнакові діапазони
    uns = ["uint8_t\n0…255", "uint16_t\n0…65 535", "uint32_t\n0…~4.3·10⁹", "uint64_t\n0…~1.8·10¹⁹"]
    sig = ["int8_t\n−128…127", "int16_t\n−32 768\n…32 767", "int32_t\n±~2.1·10⁹", "int64_t\n±~9.2·10¹⁸"]
    for j in range(4):
        p.append(fitbox(x0 + j * cw + 4, y0 + 2, cw - 8, ch - 6, uns[j],
                        size=12, fill="#eef4ff", stroke=NEG, sw=1.5))
        p.append(fitbox(x0 + j * cw + 4, y0 + ch + 2, cw - 8, ch - 6, sig[j],
                        size=12, fill="#fdecea", stroke=POS, sw=1.5))

    p.append(text(W / 2, H - 34, "той самий біт-візерунок; різниця лише в тлумаченні старшого біта",
                  size=12, color=INK, italic=True))
    p.append(text(W / 2, H - 14, "ширина = скільки значень влазить · знаковість = чи буває від'ємне",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "types-map.svg"), W, H, *p,
           title="Цілий тип — два незалежні вибори: ширина й знаковість")


# ── sizes-not-fixed: sizeof(int)/sizeof(long) гуляє між моделями ──────────────
# Ідея: «звичайні» типи не мають сталого розміру — він залежить від моделі даних
# платформи; тому переносний код бере фіксовану ширину.
def fig_sizes_not_fixed():
    W, H = 720, 352
    p = []
    models = [
        ("16-біт DOS", "16", "32", "16", "#8a5fb0", "#f2ecf8"),
        ("ILP32 (32-біт)", "32", "32", "32", NEG, "#eef4ff"),
        ("LP64 (Linux/Mac)", "32", "64", "64", FIELD, "#eafaf0"),
        ("LLP64 (Win64)", "32", "32", "64", POS, "#fdecea"),
    ]
    # шапка
    hx = [250, 380, 510]
    heads = ["int", "long", "pointer"]
    for x, h in zip(hx, heads):
        p.append(text(x, 66, h, size=13, bold=True, color=INK))
    y = 84
    rh = 52
    for name, i, l, ptr, col, fill in models:
        p.append(rect(40, y, W - 80, rh - 8, fill=fill, stroke=col, sw=1.5))
        p.append(text(56, y + 28, name, size=12, bold=True, color=col, anchor="start"))
        for x, val in zip(hx, (i, l, ptr)):
            p.append(text(x, y + 28, val + " біт", size=12, color=INK))
        y += rh

    p.append(text(W / 2, y + 20, "int майже всюди 32; а long — то 32, то 64: на нього НЕ покладаються",
                  size=12, color=INK, italic=True))
    p.append(text(W / 2, y + 42, "той самий код, різні розміри → різні межі → тихі баги при переносі",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "sizes-not-fixed.svg"), W, H, *p,
           title="«Звичайні» типи не мають сталого розміру")


# ── stdint-families: три родини — exact / least / fast ───────────────────────
# Ідея: <stdint.h> дає три відповіді на «скільки бітів» — рівно стільки,
# щонайменше стільки (ощадливо), щонайменше стільки але найшвидше.
def fig_stdint_families():
    W, H = 720, 330
    p = []
    cards = [
        (40, "int32_t", "РІВНО N бітів",
         "точна ширина на всіх\nплатформах, де є;\nдля протоколів і регістрів", NEG, "#eef4ff"),
        (256, "int_least16_t", "≥ N, найменший",
         "щонайменше N бітів,\nале якнайощадливіше\nпо пам'яті", FIELD, "#eafaf0"),
        (472, "int_fast16_t", "≥ N, найшвидший",
         "щонайменше N бітів,\nале найшвидший для ЦП\n(часто ширший)", POS, "#fdecea"),
    ]
    cw, chh = 208, 168
    for x, name, tag, body, col, fill in cards:
        p.append(rect(x, 66, cw, chh, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, 96, name, size=15, bold=True, color=col))
        p.append(text(x + cw / 2, 120, tag, size=12, bold=True, color=INK))
        p.append(mtext(x + cw / 2, 146, body, size=11, color=INK, lh=1.35))

    p.append(text(W / 2, 262, "приклад ARMv4: int_least16_t = 16 біт (ощадливо),  int_fast16_t = 32 біти (швидко)",
                  size=12, color=INK, italic=True))
    p.append(text(W / 2, 286, "усі — з <stdint.h> (C99); суфікс u дає беззнакові (uint32_t, uint_fast8_t)",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "stdint-families.svg"), W, H, *p,
           title="<stdint.h>: три родини на питання «скільки бітів»")


# ── unsigned-trap: змішування знакового й беззнакового ───────────────────────
# Ідея: при змішуванні знакове мовчки стає беззнаковим; звідси дві класичні
# пастки — порівняння −1 з розміром і зворотний цикл на беззнаковому лічильнику.
def fig_unsigned_trap():
    W, H = 720, 340
    p = []
    # ліворуч — порівняння
    p.append(text(190, 62, "−1 < sizeof(x) ?", size=14, bold=True, color=POS))
    steps = [
        ("int −1  vs  size_t", "різні знаки", INK),
        ("−1 стає беззнаковим", "правила C", POS),
        ("−1 → 0xFFFFFFFF", "≈ 4.3 млрд", POS),
        ("отже −1 > будь-що", "умова бреше", POS),
    ]
    y = 84
    for lab, note, col in steps:
        p.append(fitbox(40, y, 300, 40, lab, size=12, fill="#fdecea", stroke=col, sw=1.5,
                        color=INK, bold=True))
        p.append(text(346, y + 24, note, size=10, color=MUTED, anchor="start"))
        y += 50

    # праворуч — зворотний цикл
    p.append(text(540, 62, "for(u = n; u >= 0; u--)", size=13, bold=True, color=NEG))
    p.append(fitbox(400, 84, 300, 66,
                    "u — беззнаковий\nдійшло до 0, u-- дає\nне −1, а найбільше число",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.5))
    p.append(fitbox(400, 162, 300, 62,
                    "u >= 0 — завжди істина\n(беззнакове ніколи < 0)\n→ нескінченний цикл",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.5))

    p.append(line(60, 300, W - 60, 300, color=MUTED, sw=1, dash="5 4"))
    p.append(text(W / 2, 322, "у виразі змішали знакове й беззнакове → знакове мовчки стало беззнаковим",
                  size=12, color=INK, italic=True))
    render(os.path.join(OUT, "unsigned-trap.svg"), W, H, *p,
           title="Пастка знак/беззнак: тихе перетворення все псує")


if __name__ == "__main__":
    fig_types_map()
    fig_sizes_not_fixed()
    fig_stdint_families()
    fig_unsigned_trap()
    print("OK: figures written to", OUT)
