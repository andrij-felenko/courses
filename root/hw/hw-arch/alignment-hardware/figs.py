# -*- coding: utf-8 -*-
"""Фігури до теми «Вирівнювання даних: апаратні вимоги» (systems).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
PAD_BG   = "#e9ecef"
CELL_BG  = "#f3f5f8"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── 1. Карта апаратних контрактів вирівнювання ───────────────────────────────
def fig_contracts_map():
    """Хто саме вимагає вирівнювання від системного програміста і з якою карою."""
    W, H = 960, 640
    f = []
    f.append(text(W / 2, 54, "Кожен рядок — контракт, який залізо чи рантайм накидають на адресу буфера.",
                  size=12.5, color=MUTED, italic=True))

    cols = [130, 470, 690, 830]  # x-центри колонок
    heads = ["вимагач", "яка кратність", "як карає порушення", "рятунок"]
    ytop = 92
    rowh = 62
    # шапка
    f.append(rect(40, ytop, W - 80, 34, fill=INK, stroke=INK, sw=1.5, rx=8))
    for cx, h in zip(cols, heads):
        f.append(text(cx, ytop + 22, h, size=12.5, color="#ffffff", bold=True))

    rows = [
        ("DMA-буфер", "слово, часто рядок кешу", "не піде або зіпсує дані", "alignas(32)", NEG, BLUE_BG),
        ("Рядок кешу", "розмір рядка (32/64)", "штраф + хибне ділення", "align на рядок", NEG, BLUE_BG),
        ("Атомік / lock-free", "розмір типу (4/8)", "втрата неподільності", "природне вирівн.", POS, RED_BG),
        ("LDREX / STREX", "слово; Normal-память", "HardFault", "не на периферію", POS, RED_BG),
        ("SIMD (MOVAPS)", "16 / 32 / 64", "#GP навіть на x86", "MOVUPS / alignas", POS, RED_BG),
        ("Стек (AAPCS)", "8 на межі виклику", "чужий код падає", "лишає компілятор", FIELD, GREEN_BG),
        ("Сторінка MMU", "розмір сторінки 4 КБ", "mmap/DMA не ляжуть", "aligned_alloc", FIELD, GREEN_BG),
    ]
    y = ytop + 34
    for name, mult, pain, fix, col, bg in rows:
        f.append(rect(40, y, W - 80, rowh, fill=bg, stroke=col, sw=1.3, rx=8))
        f.append(text(cols[0], y + rowh / 2 + 5, name, size=12.5, color=col, bold=True))
        f.append(text(cols[1], y + rowh / 2 + 5, mult, size=11.5, color=INK))
        f.append(text(cols[2], y + rowh / 2 + 5, pain, size=11.5, color=INK))
        f.append(mono(cols[3], y + rowh / 2 + 5, fix, size=11, color=col, anchor="middle", bold=True))
        y += rowh + 6

    out("contracts-map.svg", W, H, *f,
        title="Апаратні контракти вирівнювання, що їх зустрічає системний код")


# ── 2. DMA й рядок кешу: зона, яку бере на себе апаратура ─────────────────────
def fig_dma_cacheline():
    """Чому DMA-буфер хочуть вирівняним на рядок кешу і чому це не бюрократія."""
    W, H = 960, 470
    f = []
    bw = 28            # ширина байта
    line_len = 6       # байтів у рядку кешу (умовно, для наочності)
    x0 = 120
    ytop = 110

    f.append(text(x0, ytop - 26, "пам'ять, розмічена рядками кешу (тут — по 8 байтів):",
                  size=12.5, color=INK, anchor="start", bold=True))

    # ── ВГОРІ: буфер вирівняний на рядок ──
    yA = ytop
    f.append(rect(60, yA - 6, 840, 92, fill=GREEN_BG, stroke=FIELD, sw=1.7, rx=12))
    f.append(text(78, yA + 14, "✓ Буфер вирівняний на рядок кешу — DMA володіє цілими рядками",
                  size=12.5, color=FIELD, anchor="start", bold=True))
    ry = yA + 30
    for c in range(4):
        cx = x0 + c * line_len * bw
        f.append(rect(cx, ry, line_len * bw, 34, fill=BG, stroke=INK, sw=1.3, rx=4))
        f.append(text(cx + line_len * bw / 2, ry + 52, "рядок %d" % c, size=9.5, color=MUTED))
    # DMA-буфер = рядки 1 і 2 повністю
    f.append(rect(x0 + line_len * bw, ry, 2 * line_len * bw, 34, fill=BLUE_BG, stroke=NEG, sw=2.4, rx=4))
    f.append(mono(x0 + 2 * line_len * bw, ry + 22, "DMA-буфер", size=12, color=NEG, anchor="middle", bold=True))

    # ── ВНИЗУ: буфер «сидить верхи» на межах рядків ──
    yB = ytop + 150
    f.append(rect(60, yB - 6, 840, 150, fill=RED_BG, stroke=POS, sw=1.7, rx=12))
    f.append(text(78, yB + 14, "✗ Буфер зсунутий — його краї ділять рядки з чужими даними",
                  size=12.5, color=POS, anchor="start", bold=True))
    ry2 = yB + 30
    for c in range(4):
        cx = x0 + c * line_len * bw
        f.append(rect(cx, ry2, line_len * bw, 34, fill=BG, stroke=INK, sw=1.3, rx=4))
    # буфер зсунутий на 3 байти, займає 12 байтів (від 3 до 15)
    off = 3
    span = 2 * line_len   # 12 байтів
    f.append(rect(x0 + off * bw, ry2, span * bw, 34, fill="#f7c9c0", stroke=POS, sw=2.4, rx=4))
    f.append(mono(x0 + (off + span / 2.0) * bw, ry2 + 22, "DMA-буфер", size=12, color=POS, anchor="middle", bold=True))
    # крайові байти, що діляться з CPU: голова 0..2 і хвіст 15..17
    f.append(rect(x0, ry2, off * bw, 34, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=4))
    tail_start = off + span
    tail_len = line_len - off   # добиває до кінця рядка 2
    f.append(rect(x0 + tail_start * bw, ry2, tail_len * bw, 34, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=4))
    f.append(text(x0 + (off * bw) / 2, ry2 + 52, "чужі", size=9.5, color=AMBER, bold=True))
    f.append(text(x0 + (tail_start + tail_len / 2.0) * bw, ry2 + 52, "чужі", size=9.5, color=AMBER, bold=True))
    # пояснення унизу червоної панелі
    f.append(text(W / 2, yB + 110,
                  "invalidate рядка викидає й чужі байти в ньому: втратиш свіжий запис CPU або отримаєш старе від DMA.",
                  size=11, color=POS, bold=True))
    f.append(text(W / 2, yB + 130,
                  "Той самий рядок кешу не може бути водночас «за CPU» і «за DMA» — межа мусить збігтися з рядком.",
                  size=10.5, color=MUTED, italic=True))

    out("dma-cacheline.svg", W, H, *f,
        title="DMA хоче вирівнювання на рядок кешу — інакше рядок ділиться з CPU")


# ── 3. Контракт вирівнювання стека на межі виклику (AAPCS) ────────────────────
def fig_stack_contract():
    """SP мусить бути кратним 8 на вході в функцію — інакше чужий код падає."""
    W, H = 940, 470
    f = []
    x0 = 130
    top = 96
    slot = 34          # висота 4-байтного слота
    colw = 200

    # ── ЛІВОРУЧ: чесний фрейм — SP кратний 8 ──
    f.append(rect(70, top - 10, 360, 340, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=12))
    f.append(text(250, top + 14, "✓ SP кратний 8 на виклику", size=13.5, color=FIELD, bold=True))
    addrs = [0x2000, 0x1FF8, 0x1FF0, 0x1FE8]
    labels = ["(вище — старе)", "збережені r4..r7", "локальні змінні", "SP → сюди, %#06x" % 0x1FE8]
    y = top + 40
    for a, lab in zip(addrs, labels):
        col = FIELD if a % 8 == 0 else POS
        f.append(rect(x0, y, colw, slot, fill=BG, stroke=INK, sw=1.3, rx=4))
        f.append(mono(x0 - 8, y + 22, "%#06x" % a, size=10.5, color=col, anchor="end", bold=(a % 8 == 0)))
        f.append(text(x0 + colw / 2, y + 22, lab, size=10.5, color=INK))
        y += slot + 6
    f.append(rect(90, y + 4, 320, 46, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(250, y + 24, "0x1FE8 mod 8 = 0 →", size=11.5, color=FIELD, bold=True))
    f.append(text(250, y + 40, "STRD / VSTR / PUSH {d8} у чужій функції — ОК", size=10, color=MUTED))

    # ── ПРАВОРУЧ: зсунутий фрейм — SP кратний лише 4 ──
    f.append(rect(510, top - 10, 360, 340, fill=RED_BG, stroke=POS, sw=1.8, rx=12))
    f.append(text(690, top + 14, "✗ SP кратний лише 4", size=13.5, color=POS, bold=True))
    x1 = 570
    addrs2 = [0x2000, 0x1FF8, 0x1FF4, 0x1FEC]
    labels2 = ["(вище — старе)", "збережені регістри", "непарне число слотів", "SP → сюди, %#06x" % 0x1FEC]
    y = top + 40
    for a, lab in zip(addrs2, labels2):
        col = FIELD if a % 8 == 0 else POS
        f.append(rect(x1, y, colw, slot, fill=BG, stroke=INK, sw=1.3, rx=4))
        f.append(mono(x1 - 8, y + 22, "%#06x" % a, size=10.5, color=col, anchor="end", bold=(a % 8 != 0)))
        f.append(text(x1 + colw / 2, y + 22, lab, size=10.5, color=INK))
        y += slot + 6
    f.append(rect(530, y + 4, 320, 46, fill=BG, stroke=POS, sw=1.5, rx=8))
    f.append(text(690, y + 24, "0x1FEC mod 8 = 4 →", size=11.5, color=POS, bold=True))
    f.append(text(690, y + 40, "STRD за цією SP → HardFault у чужому коді", size=10, color=POS, bold=True))

    f.append(rect(70, 400, 800, 52, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=10))
    f.append(text(W / 2, 422, "Контракт AAPCS: на вході в будь-яку функцію SP кратний 8. Твоя функція мусить лишити його таким для викликаних.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 442, "Компілятор тримає це сам — небезпека лише в асемблері та при ручному перемиканні стеків.",
                  size=10, color=MUTED, italic=True))

    out("stack-contract.svg", W, H, *f,
        title="Стек має контракт вирівнювання на межі виклику (AAPCS: кратно 8)")


if __name__ == "__main__":
    fig_contracts_map()
    fig_dma_cacheline()
    fig_stack_contract()
    print("OK: 3 фігури у", IMG)
