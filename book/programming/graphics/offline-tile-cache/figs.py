# -*- coding: utf-8 -*-
"""Фігури до теми «Офлайн-карти й кеш тайлів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREY = "#dfe4ea"
DARK = "#8e99a6"


# ── 1. Піраміда тайлів: 4ᶻ і частка найглибшого рівня ───────────────────────
def fig_pyramid():
    W, H = 900, 570
    out = []

    grids = [(0, 1), (1, 4), (2, 16), (3, 64)]
    gx = [60, 270, 480, 690]
    gy, gs = 62, 150

    for (z, n), x in zip(grids, gx):
        side = 2 ** z
        step = gs / float(side)
        out.append(rect(x, gy, gs, gs, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
        for i in range(1, side):
            out.append(line(x + i * step, gy, x + i * step, gy + gs, color=DARK, sw=0.7))
            out.append(line(x, gy + i * step, x + gs, gy + i * step, color=DARK, sw=0.7))
        if z == 3:
            out.append(rect(x, gy, gs, gs, fill="none", stroke=POS, sw=3, rx=4))
        out.append(text(x + gs / 2, gy + gs + 30, "рівень %d" % z, size=15, bold=True))
        out.append(text(x + gs / 2, gy + gs + 52, "%d тайлів" % n, size=14, color=MUTED))

    out.append(line(60, 300, 840, 300, color=GREY, sw=1.2))

    # смуга часток
    bx, by, bw, bh = 60, 340, 520, 46
    total = 85.0
    parts = [(1, GREY), (4, GREY), (16, "#c9d3dd"), (64, "#f6cfc9")]
    cur = bx
    for val, col in parts:
        w = bw * val / total
        edge = POS if val == 64 else LINE
        sw = 2.4 if val == 64 else 1.2
        out.append(rect(cur, by, w, bh, fill=col, stroke=edge, sw=sw, rx=3))
        cur += w
    out.append(text(bx + bw / 2, by - 14, "усі 85 тайлів рівнів 0…3", size=13, color=MUTED))

    # легенда
    lx, ly = 640, 336
    legend = [("рівень 0 — 1", GREY),
              ("рівень 1 — 4", GREY),
              ("рівень 2 — 16", "#c9d3dd"),
              ("рівень 3 — 64", "#f6cfc9")]
    for i, (lab, col) in enumerate(legend):
        y = ly + i * 30
        out.append(rect(lx, y - 12, 18, 18, fill=col, stroke=LINE, sw=1.2, rx=3))
        out.append(text(lx + 28, y + 2, lab, size=14, anchor="start"))
    out.append(text(lx, ly + 4 * 30 + 6, "рівень 3 — це ¾ набору", size=14,
                    color=POS, anchor="start", bold=True))

    out.append(text(W / 2, 480, "Сума всіх рівнів до z ледве перевищує сам рівень z", size=16))
    out.append(text(W / 2, 512, "Один зайвий рівень углиб множить увесь набір на 4", size=16, bold=True))

    render(os.path.join(IMG, 'pyramid-cost.svg'), W, H, *out,
           title="Кожен рівень учетверо більший за попередній")


# ── 2. Дві зони одного сховища ──────────────────────────────────────────────
def fig_two_zones():
    W, H = 900, 580
    out = []

    out.append(text(160, 68, "Набори (замовила людина)", size=14, bold=True))
    out.append(text(450, 68, "Тайли у сховищі", size=14, bold=True))
    out.append(text(735, 68, "Доля при чистці", size=14, bold=True))

    sets = [("Аеродром", "рівні 13–18", 96), ("Полігон", "рівні 14–17", 200)]
    set_y = []
    for name, sub, y in sets:
        out.append(fitbox(40, y, 240, 72, name + "\n" + sub, size=15,
                          fill="#eaf6ee", stroke=FIELD, sw=2, bold=False))
        set_y.append(y + 36)
    out.append(text(160, 316, "видаляє лише людина", size=13, color=FIELD))

    tiles = ["17 / 76648 / 44194",
             "17 / 76649 / 44194",
             "17 / 76650 / 44194",
             "17 / 76651 / 44194",
             "14 / 9581 / 5524",
             "16 / 38320 / 22096"]
    ty0, th, tg = 96, 46, 14
    tile_y = []
    for i, lab in enumerate(tiles):
        y = ty0 + i * (th + tg)
        tile_y.append(y + th / 2)
        pinned = i < 4
        out.append(fitbox(340, y, 220, th, lab, size=14,
                          fill="#f7f9fb" if pinned else "#ffffff",
                          stroke=LINE if pinned else DARK, sw=1.6))

    verdicts = [("імунітет", FIELD),
                ("імунітет", FIELD),
                ("імунітет · 2 посилання", FIELD),
                ("імунітет", FIELD),
                ("можна витіснити", POS),
                ("можна витіснити", POS)]
    for (lab, col), y in zip(verdicts, tile_y):
        out.append(text(600, y + 5, lab, size=14, color=col, anchor="start"))

    links = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)]
    for si, ti in links:
        out.append(line(280, set_y[si], 340, tile_y[ti], color=FIELD, sw=1.6))

    out.append(text(W / 2, 536,
                    "Тайл видаляють, лише коли на нього не посилається жоден набір",
                    size=16, bold=True))

    render(os.path.join(IMG, 'two-zones.svg'), W, H, *out,
           title="Одне сховище, дві зони з різними правами")


# ── 3. Файл на тайл проти контейнера ────────────────────────────────────────
def fig_files_vs_container():
    W, H = 900, 500
    out = []

    out.append(rect(40, 48, 390, 352, fill="#fbfcfd", stroke=GREY, sw=1.5, rx=8))
    out.append(rect(470, 48, 390, 352, fill="#fbfcfd", stroke=GREY, sw=1.5, rx=8))

    out.append(text(235, 76, "Файл на кожен тайл", size=16, bold=True))
    out.append(text(665, 76, "Один контейнер", size=16, bold=True))

    # ліворуч: блок файлової системи
    out.append(rect(70, 150, 330, 80, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    out.append(rect(70, 150, 56, 80, fill="#c9d3dd", stroke=LINE, sw=1.8, rx=4))
    out.append(text(98, 262, "тайл 700 Б", size=13, bold=True))
    out.append(text(263, 262, "3.4 КіБ порожньо", size=13, color=MUTED))
    out.append(text(235, 128, "один блок файлової системи — 4 КіБ", size=13, color=MUTED))

    left_notes = ["56 327 тайлів = 56 327 файлів",
                  "кожне читання: open() і close()",
                  "видалити набір = 56 327 викликів"]
    for i, s in enumerate(left_notes):
        out.append(text(235, 304 + i * 28, s, size=14))

    # праворуч: покажчик і щільно спакований контейнер
    out.append(fitbox(500, 118, 330, 32, "покажчик: ключ → зсув і довжина",
                      size=13, fill="#eef3f8", stroke=LINE, sw=1.4))
    widths = [26, 41, 18, 55, 33, 24, 47, 30, 38, 18]
    cur = 500.0
    scale = 330.0 / float(sum(widths))
    for i, wv in enumerate(widths):
        w = wv * scale
        out.append(rect(cur, 168, w, 62, fill="#c9d3dd" if i % 2 == 0 else "#dbe3ea",
                        stroke=LINE, sw=1.2, rx=2))
        cur += w
    out.append(text(665, 262, "тайли лежать упритул, без хвостів", size=13, color=MUTED))

    right_notes = ["1 файл на все сховище",
                   "один відкритий дескриптор",
                   "видалити набір = один запит"]
    for i, s in enumerate(right_notes):
        out.append(text(665, 304 + i * 28, s, size=14))

    out.append(text(W / 2, 444,
                    "Дрібні блоби у базі: ≈20 % менше місця й ≈35 % швидше читання",
                    size=16, bold=True))
    out.append(text(W / 2, 470, "(виміряно розробниками SQLite)", size=13, color=MUTED))

    render(os.path.join(IMG, 'files-vs-container.svg'), W, H, *out,
           title="Півмільйона дрібних файлів проти одного контейнера")


# ── 4. Підстановка предка ───────────────────────────────────────────────────
def fig_ancestor():
    W, H = 840, 470
    out = []

    ax, ay, sz = 60, 92, 240
    cell = sz / 4.0
    out.append(rect(ax, ay, sz, sz, fill="#ffffff", stroke=LINE, sw=2, rx=3))
    for i in range(1, 4):
        out.append(line(ax + i * cell, ay, ax + i * cell, ay + sz, color=DARK, sw=0.9))
        out.append(line(ax, ay + i * cell, ax + sz, ay + i * cell, color=DARK, sw=0.9))
    # підквадрат (x&3)=0, (y&3)=2
    out.append(rect(ax, ay + 2 * cell, cell, cell, fill="#f6cfc9", stroke=POS, sw=2.6, rx=2))

    for i, lab in enumerate(["0", "64", "128", "192"]):
        out.append(text(ax + i * cell, ay - 12, lab, size=12, color=MUTED))
        out.append(text(ax - 12, ay + i * cell + 5, lab, size=12, color=MUTED, anchor="end"))

    out.append(text(ax + sz / 2, ay + sz + 34, "предок рівня 15", size=15, bold=True))
    out.append(text(ax + sz / 2, ay + sz + 56, "19162 / 11048", size=14, color=MUTED))

    body, bw, bh = textbox(420, 138, "вирізати 64×64\nу точці (0, 128)\nі розтягнути ×4",
                           size=13, fill="#eef3f8", stroke=LINE, sw=1.4)
    out.append(body)
    out.append(arrow(320, 212, 530, 212, color=LINE, sw=2.2))

    bx = 540
    out.append(rect(bx, ay, sz, sz, fill="#f6cfc9", stroke=POS, sw=2.4, rx=3))
    for i in range(1, 4):
        out.append(line(bx + i * cell, ay, bx + i * cell, ay + sz, color="#e0b3ab", sw=1.6))
        out.append(line(bx, ay + i * cell, bx + sz, ay + i * cell, color="#e0b3ab", sw=1.6))
    out.append(text(bx + sz / 2, ay + sz + 34, "показуємо замість", size=15, bold=True))
    out.append(text(bx + sz / 2, ay + sz + 56, "17 / 76648 / 44194", size=14, color=MUTED))

    out.append(text(W / 2, 430,
                    "Піраміда вкладена рівно, тож перераховувати проєкцію не треба",
                    size=16, bold=True))

    render(os.path.join(IMG, 'ancestor-substitute.svg'), W, H, *out,
           title="Відсутній тайл заміняє чверть-чверті його предка")


# ── 5. Звідки в Меркаторі береться логарифм (вставка math-tile-budget) ──────
def _poly(pts, fill=FILL, stroke=LINE, sw=1.4):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, stroke, sw))


def fig_mercator_stretch():
    import math
    W, H = 960, 650
    out = []

    lats = [0, 15, 30, 45, 60, 75]
    K = 170.0                      # пікселів на одиницю y/R
    BASE = 590.0                   # екватор на обох панелях
    LX, RX = 260.0, 720.0          # центри панелей
    HW = 140.0                     # піврозмах панелі на екваторі

    arc = [K * math.radians(p) for p in lats]                       # R·φ
    mer = [K * math.log(math.tan(math.radians(p)) + 1 / math.cos(math.radians(p)))
           if p else 0.0 for p in lats]                             # R·∫sec
    cs = [math.cos(math.radians(p)) for p in lats]

    out.append(text(LX, 62, "На глобусі", size=16, bold=True))
    out.append(text(LX, 86, "висота смуги однакова: R·Δφ", size=13, color=MUTED))
    out.append(text(RX, 62, "На карті Меркатора", size=16, bold=True))
    out.append(text(RX, 86, "висота смуги росте: R·Δy", size=13, color=MUTED))

    shades = ["#eef3f8", "#e3ebf3", "#d8e3ee", "#ccdae9", "#c0d2e4"]

    # ліворуч: паралель коротшає як cos φ, смуги рівновисокі
    for i in range(5):
        yb, yt = BASE - arc[i], BASE - arc[i + 1]
        wb, wt = HW * cs[i], HW * cs[i + 1]
        out.append(_poly([(LX - wb, yb), (LX + wb, yb),
                          (LX + wt, yt), (LX - wt, yt)],
                         fill=shades[i], stroke=DARK, sw=1.3))
    # праворуч: паралелі на всю ширину, смуги різновисокі
    for i in range(5):
        yb, yt = BASE - mer[i], BASE - mer[i + 1]
        out.append(rect(RX - HW, yt, 2 * HW, yb - yt,
                        fill=shades[i], stroke=DARK, sw=1.3, rx=0))
        k = (mer[i + 1] - mer[i]) / (arc[i + 1] - arc[i])
        out.append(text(RX, (yb + yt) / 2 + 5, "×%.2f" % k, size=15, bold=True,
                        color=POS if k > 2 else INK))

    for i, p in enumerate(lats):
        out.append(text(105, BASE - arc[i] + 5, "%d°" % p, size=14, color=MUTED, anchor="end"))
        out.append(text(880, BASE - mer[i] + 5, "%d°" % p, size=14, color=MUTED, anchor="start"))

    body, bw, bh = textbox(LX, 250,
                           "паралель на широті φ\nкоротша за екватор\nу cos φ разів,\n"
                           "а карта малює її\nна всю ширину",
                           size=14, fill="#fbfcfd", stroke=GREY, sw=1.4)
    out.append(body)

    out.append(text(RX, 190, "ті самі 15° широти", size=14, color=MUTED))
    out.append(arrow(RX, 205, RX, 232, color=DARK, sw=1.6))

    out.append(text(W / 2, 624,
                    "розтяг ушир = 1/cos φ  ⟹  такий самий розтяг увись  ⟹  y = R·∫ sec φ dφ",
                    size=16, bold=True))

    render(os.path.join(IMG, 'mercator-stretch.svg'), W, H, *out,
           title="Чому в номері рядка тайла з'являється логарифм")


# ── 6. Скільки стовпців тайлів чіпає район (вставка math-tile-budget) ───────
def fig_tile_cover():
    W, H = 940, 530
    out = []

    CW, X0, NC = 68.0, 80.0, 10
    L = 6.36

    out.append(text(W / 2, 48, "приклад: район D = 20 км, рівень 13, S = 3144.6 м, "
                               "тож L = D / S = 6.36 тайла", size=13, color=MUTED))

    def row(y_head, head, y_lab, y_arr, y_cells, off, y_idx, y_verd):
        out.append(text(W / 2, y_head, head, size=15, bold=True))
        x1 = X0 + off * CW
        x2 = x1 + L * CW
        first, last = int(off), int(off + L)
        for i in range(NC):
            cx = X0 + i * CW
            hit = first <= i <= last
            out.append(rect(cx, y_cells, CW, 70,
                            fill="#f6cfc9" if hit else "#ffffff",
                            stroke=LINE if hit else DARK,
                            sw=1.6 if hit else 1.0, rx=0))
            out.append(text(cx + CW / 2, y_idx, str(i), size=13,
                            color=INK if hit else MUTED))
        out.append(rect(x1, y_cells, x2 - x1, 70, fill="none", stroke=POS, sw=3, rx=0))
        out.append(line(x1, y_arr - 7, x1, y_arr + 7, color=POS, sw=2))
        out.append(line(x2, y_arr - 7, x2, y_arr + 7, color=POS, sw=2))
        out.append(line(x1, y_arr, x2, y_arr, color=POS, sw=2))
        out.append(text((x1 + x2) / 2, y_lab, "L = 6.36 тайла", size=14, color=POS, bold=True))
        n = last - first + 1
        out.append(text(W / 2, y_verd, "район чіпає %d стовпців" % n, size=15, bold=True))

    row(76, "Ліва межа збігається з межею тайла", 98, 110, 122, 0.0, 210, 238)
    row(288, "Та сама межа, зсунута на 0.7 тайла", 310, 322, 334, 0.7, 422, 450)

    out.append(text(W / 2, 496,
                    "хай як ляже район: стовпців не більше ⌈L⌉ + 1 = 8",
                    size=16, bold=True))

    render(os.path.join(IMG, 'tile-cover.svg'), W, H, *out,
           title="Звідки в формулі береться «плюс один»")


# ── 7. Дві осі однієї сітки: XYZ згори, TMS знизу (до вставки hist) ─────────
def fig_tile_axes():
    W, H = 900, 512
    out = []
    S, CELL = 4, 58
    GS = S * CELL
    GY = 128
    HL_C, HL_R = 1, 1          # виділений тайл у рядковій нумерації згори

    def grid(gx, caption, flip):
        frag = []
        for r in range(S):
            for c in range(S):
                lab_y = (S - 1 - r) if flip else r
                x, y = gx + c * CELL, GY + r * CELL
                hit = (c == HL_C and r == HL_R)
                frag.append(rect(x, y, CELL, CELL,
                                 fill="#fdecea" if hit else "#f4f6f8",
                                 stroke=DARK, sw=0.8, rx=0))
                frag.append(text(x + CELL / 2, y + CELL / 2 + 5, "%d,%d" % (c, lab_y),
                                 size=13, color=POS if hit else MUTED, bold=hit))
        frag.append(rect(gx, GY, GS, GS, fill="none", stroke=LINE, sw=2, rx=2))
        frag.append(text(gx + GS / 2, GY - 52, caption, size=16, bold=True))

        oy = GY + GS if flip else GY
        frag.append(circle(gx, oy, 7, fill=NEG, stroke=NEG, sw=1))
        frag.append(text(gx, oy + (30 if flip else -18), "початок 0,0",
                         size=13, color=NEG, bold=True, anchor="start"))

        ax = gx + GS + 26
        if flip:
            frag.append(arrow(ax, GY + GS - 6, ax, GY + 8, color=DARK, sw=1.8))
        else:
            frag.append(arrow(ax, GY + 8, ax, GY + GS - 6, color=DARK, sw=1.8))
        frag.append(text(ax + 16, GY + GS / 2 + 5, "y", size=16, bold=True,
                         color=DARK, anchor="start"))
        return frag

    out += grid(88, "XYZ (slippy map): рядки вниз", False)
    out += grid(516, "TMS і MBTiles: рядки вгору", True)

    body, bw, bh = textbox(W / 2, 448,
                           "той самий тайл: у посиланні 2/1/1  →  у базі tile_row = 2² − 1 − 1 = 2\n"
                           "загальне правило: tile_row = 2ᶻ − 1 − y",
                           size=15, bold=True, fill="#fbfcfd", stroke=POS, sw=2)
    out.append(body)

    render(os.path.join(IMG, 'tile-axes.svg'), W, H, *out,
           title="Одна сітка, дві нумерації рядків")


# ── 8. Чотири контейнери й припущення про читача (до вставки hist) ──────────
def fig_containers_timeline():
    W, H = 980, 424
    out = []

    cols = [
        (145, "2005→", "тека z/x/y", GREY,
         ["один тайл —", "один файл", "індекс — сама", "файлова система"],
         ["читає", "веб-сервер"]),
        (375, "2011", "MBTiles", "#f6cfc9",
         ["SQLite: tiles", "плюс metadata", "рядок від низу", "(вісь TMS)"],
         ["читає процес", "на тій самій машині"]),
        (605, "2014", "GeoPackage", "#d6e4f5",
         ["SQLite за", "стандартом OGC", "рядок від верху", "(вісь WMTS)"],
         ["читає чужа", "програма"]),
        (835, "2021", "PMTiles", "#d8efdc",
         ["архів із власним", "покажчиком", "порядок Гільберта", "діапазони HTTP"],
         ["читає браузер", "через мережу"]),
    ]

    out.append(line(60, 104, 920, 104, color=DARK, sw=1.6))
    for cx, year, name, col, lines, reader in cols:
        out.append(circle(cx, 104, 8, fill=col, stroke=LINE, sw=1.8))
        out.append(text(cx, 82, year, size=16, bold=True))

        out.append(rect(cx - 105, 136, 210, 40, fill=col, stroke=LINE, sw=1.8, rx=6))
        out.append(text(cx, 162, name, size=17, bold=True))

        for i, ln in enumerate(lines):
            out.append(text(cx, 208 + i * 22, ln, size=13, color=MUTED))

        out.append(rect(cx - 105, 312, 210, 56, fill="#ffffff", stroke=GREY, sw=1.6, rx=6))
        out.append(mtext(cx, 336, reader, size=13, color=INK, bold=True))

    out.append(text(W / 2, 398,
                    "формат кодує припущення про те, ХТО й ЗВІДКИ читає тайл",
                    size=16, bold=True))

    render(os.path.join(IMG, 'containers-timeline.svg'), W, H, *out,
           title="Чотири відповіді на те саме питання")


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── Ключ тайла: рядковий проти мортонового (вставка proj-tile-store) ────────
def fig_key_layout():
    W, H = 980, 762
    out = []

    BX, BW = 56, 868
    unit = BW / 61.0

    def field(x, bits, label, fill, y, h=42, size=14):
        w = bits * unit
        out.append(fitbox(x, y, w, h, label, size=size, fill=fill, stroke=LINE, sw=1.6, rx=3))
        return x + w

    out.append(text(BX, 76, "рядковий ключ:  (джерело, z, y, x)", size=15, bold=True, anchor="start"))
    cx = BX
    cx = field(cx, 8,  "джерело · 8", "#eef3f8", 86)
    cx = field(cx, 5,  "z · 5",       "#e3ebf3", 86)
    cx = field(cx, 24, "y · 24 біти", "#dbe3ea", 86)
    cx = field(cx, 24, "x · 24 біти", "#c9d3dd", 86)
    out.append(text(BX, 150,
                    "сусід ліворуч — ключ поруч, а сусід згори — ключ за 2²⁴ = 16 777 216 одиниць",
                    size=14, color=MUTED, anchor="start"))

    out.append(text(BX, 186, "мортонів ключ:  біти y та x по черзі", size=15, bold=True, anchor="start"))
    cx = BX
    cx = field(cx, 8, "джерело · 8", "#eef3f8", 196)
    cx = field(cx, 5, "z · 5",       "#e3ebf3", 196)
    cx = field(cx, 48, "48 бітів чергування: y₂₃ x₂₃  y₂₂ x₂₂  …  y₁ x₁  y₀ x₀", "#c9d3dd", 196, size=15)

    out.append(text(BX, 280, "молодші 8 бітів зблизька:", size=14, anchor="start"))
    zx, zw = 400, 68
    for i, lab in enumerate(["y₃", "x₃", "y₂", "x₂", "y₁", "x₁", "y₀", "x₀"]):
        out.append(fitbox(zx + i * zw, 256, zw, 36, lab, size=15,
                          fill="#dbe3ea" if i % 2 == 0 else "#f2f5f8", stroke=LINE, sw=1.4, rx=3))
    out.append(text(BX, 318,
                    "сусід у будь-якому напрямку відрізняється лише молодшими бітами — отже, лежить поруч",
                    size=14, color=MUTED, anchor="start"))

    out.append(fitbox(BX, 340, BW, 40,
                      "зайнято 61 біт із 64: rowid у SQLite — ЗНАКОВЕ ціле, тож біт 63 мусить лишатися нулем",
                      size=14, fill="#fdecea", stroke=POS, sw=1.8))

    def grid(gx, gy, order, title, sub1, sub2, col):
        cs = 52.0
        out.append(text(gx + 2 * cs, gy - 16, title, size=15, bold=True))
        for r in range(4):
            for c in range(4):
                n = order[r][c]
                out.append(rect(gx + c * cs, gy + r * cs, cs, cs,
                                fill=_mix("#f7f9fb", "#9fb0c0", (n - 1) / 15.0),
                                stroke=DARK, sw=1.0, rx=2))
                out.append(text(gx + c * cs + cs / 2, gy + r * cs + cs / 2 + 6, str(n), size=15))
        out.append(text(gx + 2 * cs, gy + 4 * cs + 32, sub1, size=14, bold=True, color=col))
        out.append(text(gx + 2 * cs, gy + 4 * cs + 56, sub2, size=13, color=MUTED))

    grid(130, 430, [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]],
         "порядок ключів — рядковий", "4 суміжні пробіги",
         "розкид ключів у латці — 50 331 652", NEG)
    grid(610, 430, [[1, 2, 5, 6], [3, 4, 7, 8], [9, 10, 13, 14], [11, 12, 15, 16]],
         "порядок ключів — мортонів", "1 суміжний пробіг",
         "розкид ключів у латці — 16", FIELD)

    out.append(text(W / 2, 730,
                    "Екран просить квадратну латку — мортонів ключ кладе її у дві-три суміжні сторінки",
                    size=16, bold=True))

    render(os.path.join(IMG, 'key-layout.svg'), W, H, *out,
           title="61 біт ключа тайла: порядок полів вирішує, що лежатиме поруч")


# ── Розмір сторінки проти розміру тайла (вставка proj-tile-store) ───────────
def fig_page_vs_blob():
    W, H = 980, 700
    out = []

    out.append(rect(40, 52, 430, 300, fill="#fbfcfd", stroke=GREY, sw=1.5, rx=8))
    out.append(rect(510, 52, 430, 300, fill="#fbfcfd", stroke=GREY, sw=1.5, rx=8))
    out.append(text(255, 80, "сторінка 4 КіБ", size=16, bold=True))
    out.append(text(725, 80, "сторінка 32 КіБ", size=16, bold=True))

    out.append(fitbox(70, 100, 180, 62, "аркуш b-дерева\n1048 Б тайла",
                      size=13, fill="#c9d3dd", stroke=LINE, sw=1.8))
    out.append(text(360, 124, "решта 24 552 Б —", size=13, color=MUTED))
    out.append(text(360, 146, "у ланцюг сторінок", size=13, color=MUTED))
    out.append(arrow(160, 170, 160, 196, color=LINE, sw=2))

    ox, oy, ow, oh, og = 62, 200, 56, 52, 10
    for i in range(6):
        x = ox + i * (ow + og)
        out.append(rect(x, oy, ow, oh, fill="#f6cfc9", stroke=POS, sw=1.6, rx=3))
        out.append(text(x + ow / 2, oy + oh / 2 + 5, str(i + 1), size=14, color=POS, bold=True))
        if i < 5:
            out.append(arrow(x + ow, oy + oh / 2, x + ow + og, oy + oh / 2, color=POS, sw=1.6))
    out.append(text(255, 298, "6 переходів ланцюгом", size=14, bold=True, color=POS))
    out.append(text(255, 324, "адресу наступної сторінки видно лише з попередньої",
                    size=13, color=MUTED))

    px, py, pw, ph = 540, 128, 370, 96
    fw = pw * 25600.0 / 32768.0
    out.append(rect(px, py, pw, ph, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    out.append(rect(px, py, fw, ph, fill="#c9d3dd", stroke=LINE, sw=1.6, rx=4))
    out.append(text(px + fw / 2, py + ph / 2 + 6, "тайл 25 600 Б", size=15, bold=True))
    out.append(text(px + fw + (pw - fw) / 2, py + ph / 2 + 6, "7 КіБ", size=13, color=POS))
    out.append(text(725, 262, "0 переходів", size=14, bold=True, color=FIELD))
    out.append(text(725, 288, "другий такий тайл на аркуш уже не влазить,", size=13, color=MUTED))
    out.append(text(725, 310, "тож хвіст сторінки гине намарне", size=13, color=MUTED))
    out.append(text(725, 336, "розплата — 7 168 Б, тобто 22 %", size=14, bold=True, color=POS))

    tx, ty, cw, rh = 60, 400, 215, 38
    heads = ["розмір сторінки", "у комірці аркуша", "сторінок переповнення", "читань на тайл"]
    rows = [("4 КіБ", "1 048 Б", "6", "7", False),
            ("8 КіБ", "1 036 Б", "3", "4", False),
            ("16 КіБ", "9 220 Б", "1", "2", False),
            ("32 КіБ", "увесь тайл", "0", "1", True),
            ("64 КіБ", "увесь тайл", "0", "1", False)]

    for c, hlab in enumerate(heads):
        out.append(fitbox(tx + c * cw, ty, cw, rh, hlab, size=13,
                          fill="#e3ebf3", stroke=LINE, sw=1.4, bold=True))
    for r, row in enumerate(rows):
        y = ty + (r + 1) * rh
        good = row[4]
        for c in range(4):
            out.append(fitbox(tx + c * cw, y, cw, rh, row[c], size=14,
                              fill="#eaf6ee" if good else "#ffffff",
                              stroke=FIELD if good else LINE,
                              sw=1.8 if good else 1.1))

    out.append(text(W / 2, 646, "Доки сторінка коротша за тайл, хвіст тайла лежить у ланцюгу",
                    size=16, bold=True))
    out.append(text(W / 2, 674,
                    "тайл 25 600 Б, SQLite 3.49.1: числа зняті з PRAGMA page_count після вставки одного тайла",
                    size=13, color=MUTED))

    render(os.path.join(IMG, 'page-vs-blob.svg'), W, H, *out,
           title="Розмір сторінки проти розміру тайла: платиш або переходами, або місцем")


if __name__ == '__main__':
    fig_pyramid()
    fig_two_zones()
    fig_files_vs_container()
    fig_ancestor()
    fig_mercator_stretch()
    fig_tile_cover()
    fig_tile_axes()
    fig_containers_timeline()
    fig_key_layout()
    fig_page_vs_blob()
    print("ok:", os.listdir(IMG))
