# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── sram-area: чому стеля SRAM саме така — 6 транзисторів на біт ────────────────
# Ідея: показати кількісно, чому SRAM дорога до площі. Один біт = 6T; сотні КБ =
# мільйони транзисторів лише під пам'ять, і кожен бере площу кристала.

def fig_sram_area():
    W, H = 820, 360
    p = []

    # ліворуч — одна комірка SRAM: 6 квадратиків-транзисторів у решітці
    lx, ly = 150, 150
    p.append(text(lx, 70, "1 біт SRAM = 6 транзисторів", size=13, color=INK, bold=True))
    s = 22
    gap = 6
    coords = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0)]
    fills = ["#eef4ff", "#eef4ff", "#eafaf0", "#eafaf0", "#fdecea", "#fdecea"]
    for (gx, gy), fl in zip(coords, fills):
        x = lx + gx * (s + gap) - s / 2
        y = ly + gy * (s + gap) - s / 2
        p.append(rect(x, y, s, s, fill=fl, stroke=INK, sw=1.4, rx=3))
        p.append(text(x + s / 2, y + s / 2 + 4, "T", size=11, color=INK, bold=True))
    p.append(mtext(lx, ly + 70, "дві навхрест-зчеплені засувки\n(4T) + два ключі доступу (2T)",
                   size=9, color=MUTED))

    # стрілка «×»
    p.append(text(W / 2 - 30, 150, "×", size=26, color=INK, bold=True))

    # праворуч — множення до реальної ємності
    calc_x = W / 2 + 20
    p.append(fitbox(calc_x, 88, 260, 34, "256 КБ пам'яті", size=13, fill="#f6f4ec",
                    stroke=INK, sw=2, bold=True))
    rows = [
        ("256 КБ", "= 2 097 152 біт"),
        ("× 6 T/біт", "≈ 12.6 млн транзисторів"),
        ("самі лише", "клітинки пам'яті"),
    ]
    ry = 150
    cols = [FIELD, POS, MUTED]
    for i, (a, b) in enumerate(rows):
        p.append(text(calc_x + 6, ry, a, size=13, color=INK, anchor="start", bold=True))
        p.append(text(calc_x + 118, ry, b, size=12, color=cols[i], anchor="start"))
        ry += 36
    p.append(mtext(calc_x + 6, ry + 8, "кожен транзистор — площа кремнію,\nа площа — гроші; тому SRAM дають скупо",
                   size=10, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 16, "стеля SRAM — не примха: сотні КБ уже коштують мільйони транзисторів самої пам'яті",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sram-area.svg"), W, H, *p,
           title="Чому вбудованої SRAM мало: шість транзисторів на кожен біт")


# ── tradeoff: три осі — швидкість, ємність-на-ціну, нелеткість ─────────────────
# Ідея: жодна пам'ять не тримає всі три вершини. SRAM — швидка, але не ємна;
# DRAM/PSRAM — швидка й ємна, але летка; Flash — ємна й нелетка, але повільна на запис.

def fig_tradeoff():
    W, H = 780, 500
    p = []
    cx, cy = W / 2, 250
    R = 138

    # три вершини трикутника
    verts = {
        "top":   (cx,           cy - R),
        "left":  (cx - R * 0.94, cy + R * 0.60),
        "right": (cx + R * 0.94, cy + R * 0.60),
    }
    # ребра трикутника
    p.append(line(*verts["top"],  *verts["left"],  color="#d7dbe2", sw=1.6))
    p.append(line(*verts["top"],  *verts["right"], color="#d7dbe2", sw=1.6))
    p.append(line(*verts["left"], *verts["right"], color="#d7dbe2", sw=1.6))

    # підписи вершин (три бажані властивості) — винесені ЗА вершину назовні
    p.append(textbox(verts["top"][0], verts["top"][1] - 22,
                     "ШВИДКІСТЬ\n(миттєвий доступ)", size=11, bold=True,
                     color=NEG, fill="#eef4ff", stroke=NEG, sw=1.6)[0])
    p.append(textbox(verts["left"][0] - 4, verts["left"][1] + 40,
                     "ЄМНІСТЬ на ціну\n(дешевий біт)", size=11, bold=True,
                     color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)[0])
    p.append(textbox(verts["right"][0] + 4, verts["right"][1] + 40,
                     "НЕЛЕТКІСТЬ\n(переживає збій)", size=11, bold=True,
                     color=POS, fill="#fdecea", stroke=POS, sw=1.6)[0])

    # три реальні пам'яті — кожна на РЕБРІ між двома вершинами (тримає лише дві)
    def mid(a, b, t=0.5):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    sram = mid(verts["top"], verts["left"], 0.46)    # швидка, не дуже ємна
    dram = mid(verts["top"], verts["right"], 0.46)   # PSRAM/DRAM — швидка+ємна, летка
    flsh = mid(verts["left"], verts["right"], 0.5)    # Flash — ємна+нелетка, повільний запис

    # SRAM — підпис ліворуч від точки; DRAM — праворуч; Flash — під ребром
    p.append(circle(*sram, 7, fill=NEG, stroke=NEG, sw=2))
    p.append(mtext(sram[0] - 58, sram[1] - 4, "SRAM\nшвидка,\nНЕ ємна", size=10, color=INK, bold=True))
    p.append(circle(*dram, 7, fill=FIELD, stroke=FIELD, sw=2))
    p.append(mtext(dram[0] + 60, dram[1] - 4, "DRAM/\nPSRAM\nшвидка+ємна,\nлетка", size=10, color=INK, bold=True))
    p.append(circle(*flsh, 7, fill=POS, stroke=POS, sw=2))
    p.append(mtext(flsh[0], flsh[1] + 46, "Flash\nємна+нелетка,\nповільний запис", size=10, color=INK, bold=True))

    # центр трикутника — коротко
    p.append(mtext(cx, cy - 4, "усі три вершини\nводночас —\nфізика не дозволяє",
                   size=11, color=MUTED, bold=True))

    p.append(text(W / 2, H - 16, "кожна пам'ять тримає лише ДВІ вершини з трьох — тому під різні задачі беруть різні пам'яті",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p,
           title="Трикутник неможливого: швидкість · ємність · нелеткість")


# ── erase-write: чому у Flash не можна «просто перезаписати» байт ──────────────
# Ідея: програмування лише гасить біти 1→0; повернути 0→1 можна тільки стиранням
# цілого блоку. Звідси erase-before-write і підсилення запису.

def fig_erase_write():
    W, H = 800, 420
    p = []

    def byte_row(x, y, bits, label, col):
        out = []
        cell = 26
        out.append(text(x - 14, y + cell * 0.7, label, size=10, color=col,
                        anchor="end", bold=True))
        for i, b in enumerate(bits):
            fx = x + i * cell
            fill = "#eafaf0" if b == "1" else "#fdecea"
            out.append(rect(fx, y, cell - 3, cell - 3, fill=fill, stroke=INK, sw=1.2, rx=2))
            out.append(text(fx + (cell - 3) / 2, y + (cell - 3) / 2 + 5, b,
                            size=12, color=INK, bold=True))
        return out

    x0 = 250
    # крок 1: стерто → усе 1 (0xFF)
    p += byte_row(x0, 80, "11111111", "стерто (0xFF):", FIELD)
    p.append(text(x0 + 8 * 26 + 20, 96, "усі біти = 1", size=10, color=FIELD, anchor="start"))
    p.append(arrow(x0 + 100, 108, x0 + 100, 138, color=INK, sw=1.8))
    p.append(text(x0 + 110, 128, "програмування: 1 → 0 (можна)", size=10, color=INK, anchor="start"))

    # крок 2: записали значення (частина бітів погашена в 0)
    p += byte_row(x0, 148, "10110010", "записали A:", INK)
    p.append(arrow(x0 + 100, 176, x0 + 100, 206, color=POS, sw=1.8))
    p.append(text(x0 + 110, 196, "хочемо інше значення B…", size=10, color=POS, anchor="start"))

    # крок 3: спроба дописати 0→1 — заборонено
    p += byte_row(x0, 216, "10110010", "маємо:", MUTED)
    p.append(text(x0 + 8 * 26 + 20, 232, "0 назад у 1 —", size=10, color=POS, anchor="start"))
    p.append(text(x0 + 8 * 26 + 20, 248, "НЕ можна записом", size=10, color=POS, anchor="start"))

    # висновок-стрілка вниз до блоку
    p.append(arrow(x0 + 100, 250, x0 + 100, 286, color=NEG, sw=2))
    p.append(text(x0 + 110, 272, "єдиний шлях 0→1:", size=10, color=NEG, anchor="start"))

    # крок 4: стерти можна лише цілим блоком
    p.append(fitbox(x0 - 40, 296, 380, 56,
                    "СТЕРТИ цілий блок (4 КБ) → знову всі 1 → аж тоді писати B\n"
                    "звідси: підсилення запису (щоб змінити 1 байт — стерти 4 КБ)",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.8, bold=True, color=NEG))

    p.append(text(W / 2, H - 14, "запис у Flash лише гасить біти 1→0; повернути 0→1 можна тільки стиранням цілого блоку",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "erase-write.svg"), W, H, *p,
           title="Чому Flash не можна «просто перезаписати»: стирання перед записом")


# ── window: зовнішня RAM — не безмежна поличка, а вузьке вікно крізь кеш ────────
# Ідея: CPU бачить велику PSRAM у адресному просторі, та фізично ходить туди
# крізь вузьку шину + кеш; попадання в кеш — швидко, промах — довга дорога.

def fig_window():
    W, H = 820, 380
    p = []

    # CPU зліва
    p.append(fitbox(60, 150, 110, 70, "CPU\nядро", size=13, fill="#eef4ff",
                    stroke=NEG, sw=2, bold=True, color=NEG))

    # кеш посередині (маленький, швидкий)
    p.append(fitbox(230, 140, 130, 90, "КЕШ\nмаленький,\nшвидкий", size=12,
                    fill="#eafaf0", stroke=FIELD, sw=2, bold=True, color=FIELD))
    p.append(arrow(170, 185, 228, 185, color=INK, sw=1.8))
    p.append(text(199, 176, "адреса", size=9, color=MUTED))

    # вузька шина до зовнішнього чипа
    p.append(arrow(360, 185, 500, 185, color=POS, sw=2.4))
    p.append(text(430, 172, "вузька шина", size=10, color=POS, bold=True))
    p.append(text(430, 202, "SPI/QSPI, такти", size=9, color=MUTED))

    # зовнішня PSRAM справа (велика)
    p.append(fitbox(500, 110, 260, 150,
                    "зовнішня PSRAM\n(8 МБ)\n\nвелика й дешева,\nАЛЕ фізично далеко",
                    size=12, fill="#f6f4ec", stroke=INK, sw=2, bold=True))

    # дві дороги: попадання (коротка) vs промах (довга)
    p.append(fitbox(230, 270, 250, 44,
                    "ПОПАДАННЯ в кеш → відповідь миттєва\n(дані вже поруч із CPU)",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.5, color=FIELD, bold=True))
    p.append(fitbox(500, 270, 260, 44,
                    "ПРОМАХ → довга дорога по шині\n(десятки тактів очікування)",
                    size=10, fill="#fdecea", stroke=POS, sw=1.5, color=POS, bold=True))

    p.append(text(W / 2, H - 14, "зовнішня RAM у адресному просторі виглядає як поличка, та фізично це вузьке вікно крізь кеш",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "window.svg"), W, H, *p,
           title="Зовнішня RAM: велика на позір, вузька фізично")


if __name__ == "__main__":
    fig_sram_area()
    fig_tradeoff()
    fig_erase_write()
    fig_window()
    print("OK: detailed figures written to", OUT)
