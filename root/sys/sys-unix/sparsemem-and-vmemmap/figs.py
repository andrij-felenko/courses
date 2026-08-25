# -*- coding: utf-8 -*-
"""Фігури для теми «Модель фізичної пам'яті: SPARSEMEM, vmemmap і масив описувачів кадрів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"
GRY_F = "#eceff3"


# ── 1. Плаский масив над дірявим адресним простором ────────────────────────
def fig_flat_waste():
    W, H = 1420, 560
    X0, X1 = 250, 1330
    SPAN = 4096.0  # ГіБ = 4 ТіБ

    def px(g):
        return X0 + (g / SPAN) * (X1 - X0)

    F = []

    # вісь адрес
    F.append(line(X0, 96, X1, 96, color=LINE, sw=1.2))
    for g, lab in ((0, "0"), (1024, "1 ТіБ"), (2048, "2 ТіБ"), (3072, "3 ТіБ"), (4096, "4 ТіБ")):
        F.append(line(px(g), 88, px(g), 104, color=LINE, sw=1.2))
        F.append(text(px(g), 74, lab, size=14, color=MUTED))
    F.append(text((X0 + X1) / 2, 44, "фізичні адреси, які машина здатна адресувати",
                  size=15, color=INK))

    rowh = 54

    # ── справжня пам'ять
    y_ram = 150
    banks = [(0, 32), (1024, 1056)]
    for a, b in banks:
        F.append(rect(px(a), y_ram, max(px(b) - px(a), 9), rowh,
                      fill=GRN_F, stroke=NEG, sw=1.6))
    F.append(text(px(16) + 26, y_ram + rowh + 26, "банк 32 ГіБ", size=14, color=MUTED,
                  anchor="start"))
    F.append(text(px(1040) + 26, y_ram + rowh + 26, "банк 32 ГіБ другого вузла",
                  size=14, color=MUTED, anchor="start"))
    F.append(mtext(30, y_ram + 24, ["є насправді", "64 ГіБ"], size=15, anchor="start", color=INK))

    # ── плаский масив описувачів
    y_map = 320
    F.append(rect(X0, y_map, X1 - X0, rowh, fill=GRY_F, stroke=LINE, sw=1.6))
    for a, b in banks:
        F.append(rect(px(a), y_map, max(px(b) - px(a), 9), rowh,
                      fill=RED_F, stroke=POS, sw=1.6))
    F.append(mtext(30, y_map + 24, ["плаский масив", "mem_map[]"], size=15,
                   anchor="start", color=INK))

    F.append(text(px(1900), y_map + rowh + 34, "описувачі кадрів, яких не існує",
                  size=14, color=MUTED))

    # підсумок числами
    box, bw, bh = textbox((X0 + X1) / 2, 490,
                          ["індекс — номер кадру, тож масив мусить накрити ВЕСЬ проміжок адрес",
                           "4 ТіБ ÷ 4 КіБ × 64 Б = 64 ГіБ описувачів на 64 ГіБ пам'яті"],
                          size=15, pad=16, fill=YEL_F, stroke=POS)
    F.append(box)

    render(os.path.join(IMG, 'flat-waste.svg'), W, H, *F,
           title="Плаский масив описувачів над дірявим адресним простором")


# ── 2. Двоступеневий пошук SPARSEMEM ───────────────────────────────────────
def fig_sparsemem_lookup():
    W, H = 1400, 720
    F = []

    # ── розбір номера кадру
    bx, by, bw, bh = 120, 60, 900, 62
    F.append(rect(bx, by, bw, bh, fill=BLU_F, stroke=LINE, sw=1.6))
    F.append(line(bx + 520, by, bx + 520, by + bh, color=LINE, sw=1.6))
    F.append(text(bx + 260, by + 38, "номер секції = pfn >> 15", size=16, color=INK))
    F.append(text(bx + 710, by + 38, "зсув = pfn & 32767", size=16, color=INK))
    F.append(text(bx, by - 20, "номер кадру (pfn)", size=15, color=INK, anchor="start"))
    F.append(text(bx + 260, by + bh + 26, "секція = 128 МіБ = 32768 кадрів",
                  size=14, color=MUTED))
    F.append(text(bx + 710, by + bh + 26, "місце кадру всередині секції",
                  size=14, color=MUTED))

    # ── каталог секцій
    dx, dy, dw, dh = 150, 230, 300, 52
    rows = [("секція 0", True), ("секція 1", True), ("секція 2", False),
            ("секція 3", False), ("секція 4", True)]
    F.append(text(dx, dy - 26, "каталог mem_section[]", size=15, color=INK, anchor="start"))
    for i, (lab, present) in enumerate(rows):
        y = dy + i * (dh + 16)
        fill = BLU_F if present else GRY_F
        F.append(rect(dx, y, dw, dh, fill=fill, stroke=LINE, sw=1.5))
        F.append(text(dx + 16, y + 33, lab, size=15, color=INK, anchor="start"))
        F.append(text(dx + dw - 16, y + 33, "покажчик" if present else "порожньо",
                      size=14, color=MUTED if present else POS, anchor="end"))

    # ── масиви описувачів справа
    ax, aw, ah = 800, 420, 52
    targets = [(0, 0), (1, 1), (4, 4)]
    for i, (row, _) in enumerate(targets):
        ysrc = dy + row * (dh + 16) + dh / 2
        ydst = dy + i * (dh + 16) * 1.34 + ah / 2
        F.append(rect(ax, ydst - ah / 2, aw, ah, fill=GRN_F, stroke=NEG, sw=1.5))
        F.append(text(ax + aw / 2, ydst + 6, "32768 описувачів = 2 МіБ", size=15, color=INK))
        F.append(arrow(dx + dw + 12, ysrc, ax - 14, ydst, color=LINE, sw=1.6))

    F.append(text(ax + aw / 2, dy - 26, "власний масив кожної наявної секції",
                  size=15, color=INK))

    # ── зворотний бік
    box, _, _ = textbox(W / 2, 640,
                        ["зворотний хід: за покажчиком на описувач не видно, чиєї він секції —",
                         "тому номер секції доводиться тримати в бітах page->flags"],
                        size=15, pad=16, fill=YEL_F, stroke=POS)
    F.append(box)

    render(os.path.join(IMG, 'sparsemem-lookup.svg'), W, H, *F,
           title="Двоступеневий пошук описувача в SPARSEMEM")


# ── 3. vmemmap: суцільність робить MMU ─────────────────────────────────────
def fig_vmemmap():
    W, H = 1400, 700
    X0, X1 = 300, 1320
    F = []

    # ── віртуальне вікно
    y_v = 120
    hv = 58
    F.append(rect(X0, y_v, X1 - X0, hv, fill=BLU_F, stroke=NEG, sw=1.7))
    n = 8
    step = (X1 - X0) / n
    for i in range(1, n):
        F.append(line(X0 + i * step, y_v, X0 + i * step, y_v + hv, color=NEG, sw=1.0, dash="4,4"))
    F.append(mtext(40, y_v + 22, ["віртуальне вікно", "vmemmap"], size=15,
                   anchor="start", color=INK))
    F.append(text((X0 + X1) / 2, y_v - 34,
                  "суцільний масив описувачів у віртуальних адресах: індекс — просто pfn",
                  size=15, color=INK))

    # ── таблиці сторінок
    y_p = 320
    hp = 62
    filled = [True, True, False, False, True, False, True, True]
    for i in range(n):
        x = X0 + i * step
        ok = filled[i]
        F.append(rect(x + 8, y_p, step - 16, hp,
                      fill=GRN_F if ok else GRY_F, stroke=NEG if ok else LINE, sw=1.5))
        F.append(text(x + step / 2, y_p + 38, "PMD" if ok else "нема", size=14,
                      color=INK if ok else MUTED))
        if ok:
            F.append(arrow(x + step / 2, y_v + hv + 10, x + step / 2, y_p - 12,
                           color=NEG, sw=1.5))
    F.append(mtext(40, y_p + 24, ["таблиці сторінок", "ядра"], size=15,
                   anchor="start", color=INK))
    F.append(text((X0 + X1) / 2, y_p + hp + 34,
                  "запис заповнюють лише там, де пам'ять справді є; один запис на 2 МіБ описувачів",
                  size=14, color=MUTED))

    # ── фізичні кадри під описувачі
    y_f = 490
    hf = 58
    spots = [0, 1, 4, 6, 7]
    for k, i in enumerate(spots):
        x = X0 + 40 + k * 168
        F.append(rect(x, y_f, 140, hf, fill=YEL_F, stroke=LINE, sw=1.5))
        F.append(text(x + 70, y_f + 36, "кадр", size=14, color=INK))
        F.append(arrow(X0 + i * step + step / 2, y_p + hp + 54, x + 70, y_f - 12,
                       color=LINE, sw=1.3))
    F.append(mtext(40, y_f + 22, ["фізичні кадри", "де лежать описувачі"], size=15,
                   anchor="start", color=INK))

    box, _, _ = textbox(W / 2, 645,
                        "pfn_to_page(pfn) = vmemmap + pfn     ·     page_to_pfn(page) = page − vmemmap",
                        size=16, pad=14, fill=GRN_F, stroke=NEG)
    F.append(box)

    render(os.path.join(IMG, 'vmemmap.svg'), W, H, *F,
           title="vmemmap: суцільність описувачів забезпечують таблиці сторінок")


# ── 4. Злиття однакових хвостових описувачів (HVO) ─────────────────────────
def fig_hvo():
    W, H = 1360, 620
    F = []

    def column(x0, title, note, share):
        out = []
        out.append(text(x0 + 250, 60, title, size=17, color=INK, bold=True))
        # вісім записів таблиці
        for i in range(8):
            y = 110 + i * 52
            out.append(rect(x0, y, 190, 40, fill=BLU_F, stroke=NEG, sw=1.4))
            out.append(text(x0 + 95, y + 26, "запис %d" % i, size=13, color=INK))
        # кадри
        if share:
            out.append(rect(x0 + 340, 110, 160, 40, fill=GRN_F, stroke=NEG, sw=1.5))
            out.append(text(x0 + 420, 136, "кадр 0", size=13, color=INK))
            for i in range(8):
                y = 110 + i * 52
                out.append(arrow(x0 + 196, y + 20, x0 + 334, 130, color=NEG, sw=1.1))
            out.append(rect(x0 + 340, 220, 160, 250, fill=GRY_F, stroke=LINE, sw=1.4))
            out.append(fitbox(x0 + 348, 228, 144, 234,
                              "сім кадрів\nповернуто\nрозподільнику",
                              size=14, fill=GRY_F, stroke=GRY_F, sw=0.0, color=MUTED))
        else:
            for i in range(8):
                y = 110 + i * 52
                out.append(rect(x0 + 340, y, 160, 40, fill=GRN_F, stroke=NEG, sw=1.4))
                out.append(text(x0 + 420, y + 26, "кадр %d" % i, size=13, color=INK))
                out.append(arrow(x0 + 196, y + 20, x0 + 334, y + 20, color=NEG, sw=1.1))
        out.append(text(x0 + 250, 560, note, size=14, color=MUTED))
        return out

    F += column(90, "звичайно", "8 кадрів під описувачі однієї великої сторінки", False)
    F += column(760, "після злиття", "усі хвостові записи ведуть на той самий кадр", True)

    F.append(text(W / 2, 600,
                  "512 описувачів великої сторінки 2 МіБ займають 32 КіБ = 8 кадрів",
                  size=15, color=INK))

    render(os.path.join(IMG, 'hvo.svg'), W, H, *F,
           title="Злиття однакових описувачів великої сторінки")


# ── 5. Три лінійки над тим самим діапазоном адрес ──────────────────────────
def fig_three_rulers():
    W, H = 1420, 540
    X0, X1 = 210, 1360
    SPAN = 10.0  # ГіБ

    def px(g):
        return X0 + (g / SPAN) * (X1 - X0)

    F = []
    F.append(text(W / 2, 40, "Той самий діапазон адрес трьома лінійками",
                  size=17, color=INK, bold=True))

    # вісь адрес
    ay = 96
    F.append(line(X0, ay, X1, ay, color=LINE, sw=1.2))
    for g in (0, 2, 4, 6, 8, 10):
        F.append(line(px(g), ay - 8, px(g), ay + 8, color=LINE, sw=1.2))
        F.append(text(px(g), ay - 18, "%d ГіБ" % g, size=13, color=MUTED))

    RH = 48
    lab_x = X0 - 24

    # ── лінійка прошивки
    y1 = 140
    F.append(text(lab_x, y1 + 30, "/proc/iomem", size=14, color=INK,
                  anchor="end", bold=True))
    for a, b, lab, fl in ((0, 3, "System RAM", GRN_F),
                          ("hole", 4, "PCI Bus / Reserved", RED_F),
                          (4, 10, "System RAM", GRN_F)):
        a = 3 if a == "hole" else a
        F.append(fitbox(px(a), y1, px(b) - px(a), RH, lab,
                        size=14, fill=fl, stroke=LINE, sw=1.3))

    # ── лінійка секцій
    y2 = 250
    F.append(text(lab_x, y2 + 30, "секції по 128 МіБ", size=14, color=INK,
                  anchor="end", bold=True))
    cw = (X1 - X0) / 80.0
    for s in range(80):
        present = (s < 24) or (s >= 32)
        F.append(rect(X0 + s * cw, y2, cw, RH,
                      fill=(GRN_F if present else GRY_F), stroke=LINE, sw=0.6, rx=0))
    for s, g in ((0, 0.0), (24, 3.0), (32, 4.0), (80, 10.0)):
        F.append(text(px(g), y2 + RH + 22, "секція %d" % s, size=12, color=MUTED))

    # ── лінійка блоків гарячого додавання
    y3 = 366
    F.append(text(lab_x, y3 + 30, "блоки по 2 ГіБ", size=14, color=INK,
                  anchor="end", bold=True))
    for a, b, nm in ((0, 2, "memory0"), (2, 4, "memory1"), (4, 6, "memory2"),
                     (6, 8, "memory3"), (8, 10, "memory4")):
        part = (nm == "memory1")
        F.append(fitbox(px(a), y3, px(b) - px(a), RH, nm, size=14,
                        fill=(YEL_F if part else GRN_F),
                        stroke=(POS if part else LINE), sw=(2.0 if part else 1.3)))

    F.append(text(W / 2, 474,
                  "memory1 накриває і пам'ять (секції 16–23), і діру (секції 24–31)",
                  size=15, color=INK))
    F.append(text(W / 2, 502,
                  "вимкнути його можна лише цілим: дрібнішої одиниці в /sys немає",
                  size=15, color=MUTED))

    render(os.path.join(IMG, 'three-rulers.svg'), W, H, *F,
           title="Прошивка, секції та блоки пам'яті над одним діапазоном адрес")


# ── 6. Слово section_mem_map: два життя одного числа ───────────────────────
def fig_section_word():
    W, H = 1360, 600
    X0, X1 = 150, 1240
    SPLIT = 900
    BH = 66

    F = []
    F.append(text(W / 2, 46, "Запис каталогу: одне слово section_mem_map",
                  size=17, color=INK, bold=True))

    def bar(y, left_lines, left_fill):
        out = []
        out.append(fitbox(X0, y, SPLIT - X0, BH, left_lines,
                          size=15, fill=left_fill, stroke=NEG, sw=1.6))
        out.append(fitbox(SPLIT, y, X1 - SPLIT, BH, "прапорці стану",
                          size=15, fill=YEL_F, stroke=POS, sw=1.6))
        return out

    # ── ранній стан
    y1 = 132
    F.append(text(X0, y1 - 18, "поки пам'ять лише оголошено", size=15,
                  color=INK, anchor="start"))
    F.append(text(X1, y1 - 18, "біт 0 — праворуч", size=13,
                  color=MUTED, anchor="end"))
    F += bar(y1, ["номер вузла NUMA", "nid << SECTION_NID_SHIFT"], BLU_F)

    # ── перехід
    F.append(arrow(360, y1 + BH + 16, 360, y1 + BH + 100, color=LINE, sw=1.7))
    F.append(text(396, y1 + BH + 68,
                  "заведення масиву затирає старші біти; прапорці лишаються",
                  size=15, color=INK, anchor="start"))

    # ── робочий стан
    y2 = 348
    F.append(text(X0, y2 - 18, "після того, як секція дістала масив описувачів",
                  size=15, color=INK, anchor="start"))
    F += bar(y2, ["адреса масиву описувачів,", "зменшена на перший кадр секції"], GRN_F)

    F.append(text((X0 + SPLIT) / 2, y2 + BH + 32, "старші біти: SECTION_MAP_MASK",
                  size=14, color=MUTED))
    F.append(text((SPLIT + X1) / 2, y2 + BH + 32, "молодших SECTION_MAP_LAST_BIT",
                  size=14, color=MUTED))

    box, _, _ = textbox(W / 2, 540,
                        ["масив вирівняний, тож його молодші біти завжди нульові —",
                         "туди й ховають прапорці, а __section_mem_map_addr() зрізає їх маскою"],
                        size=15, pad=16, fill=GRY_F, stroke=LINE)
    F.append(box)

    render(os.path.join(IMG, 'section-word.svg'), W, H, *F,
           title="Два життя слова section_mem_map")


if __name__ == '__main__':
    fig_flat_waste()
    fig_sparsemem_lookup()
    fig_vmemmap()
    fig_hvo()
    fig_three_rulers()
    fig_section_word()
    print("ok")
