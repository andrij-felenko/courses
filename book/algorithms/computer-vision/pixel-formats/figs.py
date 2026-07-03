# -*- coding: utf-8 -*-
"""Фігури до теми «Формати пікселів і буферів зображення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

R = "#cc2c20"      # червоний канал
G = "#1f9d4d"      # зелений канал
B = "#2457d6"      # синій канал
Y = "#5b6570"      # яскравість Y (сіре)
CB = "#2457d6"     # синьо-різницева хрома U/Cb
CR = "#cc2c20"     # червоно-різницева хрома V/Cr
BYTE = "#eef1f4"   # клітинка байта
PURPLE = "#7c3aed" # осередок кольору (де взято хрому)


def bytecell(x, y, w, label, fill=BYTE, tcol=INK, sub=None, h=30):
    """Клітинка одного байта в стрічці пам'яті: підпис усередині, опц. дрібний під ним."""
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.3, rx=3)
    out += text(x + w / 2, y + h / 2 + 4, label, size=12, color=tcol, bold=True)
    if sub:
        out += text(x + w / 2, y + h + 12, sub, size=9, color=MUTED)
    return out


# ── 1. Той самий піксель — різні розкладки байтів (planar vs packed) ─────────
# Ідея: одні й ті самі числа R,G,B чотирьох пікселів можна покласти в пам'ять
# двома способами; від вибору залежить, як їх читати й яке залізо швидше.
def fig_planar_packed():
    W, H = 720, 430
    f = [text(W / 2, 26, "Ті самі пікселі — дві розкладки байтів у пам'яті", size=16, bold=True)]

    # маленький кадр 2×2 з чотирма пікселями (умовні кольори)
    px = [("P0", "#d94a3d"), ("P1", "#2e8b57"), ("P2", "#3a6fd0"), ("P3", "#c9a227")]
    f.append(text(120, 62, "кадр 2×2", size=12, color=INK, bold=True))
    s = 40
    gx, gy = 78, 74
    for i, (lab, col) in enumerate(px):
        cx = gx + (i % 2) * s
        cy = gy + (i // 2) * s
        f.append(rect(cx, cy, s, s, fill=col, stroke=INK, sw=1.4, rx=4))
        f.append(text(cx + s / 2, cy + s / 2 + 4, lab, size=11, color="#ffffff", bold=True))
    f.append(text(120, gy + 2 * s + 18, "кожен піксель = R,G,B", size=10, color=MUTED))

    # ── PACKED (interleaved): RGBRGBRGB… ─────────────────────────────────────
    f.append(text(430, 70, "Пакетно (packed): R G B поряд, піксель за пікселем", size=12.5, color=INK, bold=True))
    seq = [("R0", R), ("G0", G), ("B0", B), ("R1", R), ("G1", G), ("B1", B),
           ("R2", R), ("G2", G), ("B2", B), ("R3", R), ("G3", G), ("B3", B)]
    bw = 46
    x0, yb = 40, 118
    for i, (lab, col) in enumerate(seq):
        f.append(bytecell(x0 + i * bw, yb, bw, lab, fill=col, tcol="#ffffff"))
    # дужки-групи по пікселю
    for p in range(4):
        gx0 = x0 + p * 3 * bw
        f.append(line(gx0, yb + 40, gx0 + 3 * bw, yb + 40, color=MUTED, sw=1.2))
        f.append(text(gx0 + 1.5 * bw, yb + 54, "P%d" % p, size=10, color=MUTED, bold=True))

    # ── PLANAR: усі R, потім усі G, потім усі B ──────────────────────────────
    f.append(text(430, 210, "Площинно (planar): спершу всі R, тоді всі G, тоді всі B", size=12.5, color=INK, bold=True))
    planar = ([("R%d" % i, R) for i in range(4)] +
              [("G%d" % i, G) for i in range(4)] +
              [("B%d" % i, B) for i in range(4)])
    yb2 = 258
    for i, (lab, col) in enumerate(planar):
        f.append(bytecell(x0 + i * bw, yb2, bw, lab, fill=col, tcol="#ffffff"))
    for pl, (name, cc) in enumerate((("площина R", R), ("площина G", G), ("площина B", B))):
        gx0 = x0 + pl * 4 * bw
        f.append(line(gx0, yb2 + 40, gx0 + 4 * bw, yb2 + 40, color=cc, sw=1.6))
        f.append(text(gx0 + 2 * bw, yb2 + 54, name, size=10, color=cc, bold=True))

    box = fitbox(60, 340, W - 120, 68,
                 "Числа ті самі — інша лише ПОСЛІДОВНІСТЬ байтів. Пакетно зручно показувати (піксель\n"
                 "цілий поряд) і брати випадковий піксель; площинно зручно обробляти окремий канал\n"
                 "(наприклад, лише яскравість) суцільним прогоном і живити SIMD/GPU. Формат каже, як читати.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "planar-packed.svg"), W, H, *f)


# ── 2. Субдискретизація хроми: 4:4:4 → 4:2:2 → 4:2:0 ─────────────────────────
# Ідея: око гостре на яскравість, тупе на колір; тож Y лишаємо в кожній точці,
# а колір (хрому) беремо рідше — і байтів менше без видимої втрати.
def fig_chroma_subsampling():
    W, H = 720, 400
    f = [text(W / 2, 26, "Субдискретизація хроми: яскравість щільна, колір — рідший", size=16, bold=True)]

    s = 26
    modes = [
        ("4:4:4", 70, "колір у кожному пікселі", "повний"),
        ("4:2:2", 300, "колір на 2 пікселі по гориз.", "−33% байтів"),
        ("4:2:0", 530, "колір на блок 2×2", "−50% байтів"),
    ]
    for name, ox, cap, save in modes:
        f.append(text(ox + 2 * s, 60, name, size=14, color=INK, bold=True))
        gy = 74
        # 4×4 сітка: крапки Y скрізь; клітинки хроми — залежно від режиму
        for r in range(4):
            for c in range(4):
                cx = ox + c * s
                cy = gy + r * s
                # хрома-осередок (велике кільце) — де стоїть відлік кольору
                has_chroma = False
                if name == "4:4:4":
                    has_chroma = True
                elif name == "4:2:2":
                    has_chroma = (c % 2 == 0)
                else:  # 4:2:0
                    has_chroma = (c % 2 == 0 and r % 2 == 0)
                if has_chroma:
                    # осередок кольору покриває блок, до якого він застосований
                    span_w = s if name == "4:4:4" else 2 * s
                    span_h = s if name != "4:2:0" else 2 * s
                    f.append(rect(cx - s / 2 + 2, cy - s / 2 + 2, span_w - 4, span_h - 4,
                                  fill="#efe3f7", stroke=PURPLE, sw=1.3, rx=3))
        # Y-точки поверх (щільні скрізь)
        for r in range(4):
            for c in range(4):
                cx = ox + c * s
                cy = gy + r * s
                f.append(circle(cx, cy, 3.0, fill=Y, stroke=BG, sw=0.8))
        f.append(text(ox + 2 * s - s / 2, gy + 4 * s + 8, cap, size=9.5, color=MUTED))
        f.append(text(ox + 2 * s - s / 2, gy + 4 * s + 24, save, size=10.5, color=POS, bold=True))

    # легенда
    f.append(circle(150, 300, 3.0, fill=Y, stroke=BG, sw=0.8))
    f.append(text(164, 304, "відлік яскравості Y (у кожному пікселі)", size=10.5, color=INK, anchor="start"))
    f.append(rect(150, 316, 14, 12, fill="#efe3f7", stroke="#7c3aed", sw=1.3, rx=2))
    f.append(text(172, 326, "один відлік кольору (U,V) на позначену область", size=10.5, color=INK, anchor="start"))

    box = fitbox(60, 344, W - 120, 46,
                 "Запис J:a:b описує блок J×2 пікселі: a — скільки відліків кольору в верхньому рядку, b — у нижньому.\n"
                 "4:2:0 (b=0) — колір спільний на квадрат 2×2: удвічі менше даних, а око різниці майже не бачить.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "chroma-subsampling.svg"), W, H, *f)


# ── 3. Два формати камери: YUYV (packed 4:2:2) vs NV12 (planar 4:2:0) ────────
# Ідея: показати РЕАЛЬНУ розкладку байтів двох найчастіших форматів з камери.
def fig_yuyv_nv12():
    W, H = 720, 440
    f = [text(W / 2, 26, "Два формати з камери: як лежать байти", size=16, bold=True)]

    # ── YUYV: Y0 U0 Y1 V0 Y2 U2 Y3 V2 … ──────────────────────────────────────
    f.append(text(360, 62, "YUYV (packed, 4:2:2): 2 пікселі = 4 байти", size=12.5, color=INK, bold=True))
    seq = [("Y0", Y, "#fff"), ("U0", CB, "#fff"), ("Y1", Y, "#fff"), ("V0", CR, "#fff"),
           ("Y2", Y, "#fff"), ("U2", CB, "#fff"), ("Y3", Y, "#fff"), ("V2", CR, "#fff")]
    bw = 60
    x0, yb = 90, 96
    for i, (lab, col, tc) in enumerate(seq):
        f.append(bytecell(x0 + i * bw, yb, bw, lab, fill=col, tcol=tc))
    # дужки: пара пікселів ділить одну U та одну V
    for k in range(2):
        gx0 = x0 + k * 4 * bw
        f.append(line(gx0, yb + 40, gx0 + 4 * bw, yb + 40, color=MUTED, sw=1.2))
        f.append(text(gx0 + 2 * bw, yb + 54, "пікселі %d,%d ← спільні U,V" % (2 * k, 2 * k + 1),
                      size=9.5, color=MUTED))

    # ── NV12: площина Y, далі площина UV (перемежована), удвічі нижча ────────
    f.append(text(360, 178, "NV12 (planar, 4:2:0): площина Y, тоді півплощина UVUV…", size=12.5, color=INK, bold=True))
    yy = 196
    # площина Y (16 клітинок = 4×4 пікселі, тут стрічкою)
    f.append(text(x0 - 8, yy + 20, "Y", size=13, color=Y, bold=True, anchor="end"))
    for i in range(8):
        f.append(bytecell(x0 + i * bw, yy, bw, "Y%d" % i, fill=Y, tcol="#fff"))
    f.append(text(x0 + 8 * bw + 8, yy + 20, "… (усі Y, повний розмір)", size=10, color=MUTED, anchor="start"))
    # площина UV — удвічі коротша, U та V перемежовані
    yv = yy + 58
    f.append(text(x0 - 8, yv + 20, "UV", size=13, color="#7c3aed", bold=True, anchor="end"))
    uv = [("U0", CB), ("V0", CR), ("U1", CB), ("V1", CR), ("U2", CB), ("V2", CR), ("U3", CB), ("V3", CR)]
    for i, (lab, col) in enumerate(uv):
        f.append(bytecell(x0 + i * bw, yv, bw, lab, fill=col, tcol="#fff"))
    f.append(text(x0 + 8 * bw + 8, yv + 20, "← удвічі менше рядків", size=10, color=MUTED, anchor="start"))

    box = fitbox(60, 338, W - 120, 92,
                 "YUYV кладе все підряд одним потоком — зручно тягти по одному дроту (USB-камера), піксель\n"
                 "дістаєш одразу, але U та V повторюються в кожному парному рядку. NV12 тримає яскравість\n"
                 "окремою суцільною площиною (готово для кодека й GPU, часто просто «дивишся» на Y як на\n"
                 "сіре зображення), а колір — окремою вдвічі меншою півплощиною. Обидва несуть ті самі\n"
                 "числа Y,U,V — різниця лише в порядку й у тому, як часто взято колір.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "yuyv-nv12.svg"), W, H, *f)


# ── 4. RGB565: як 16 біт діляться на 5-6-5 ───────────────────────────────────
# Ідея: щоб піксель займав рівно 2 байти (зручно для дисплея), колір тиснуть у
# 16 біт: 5 біт червоному, 6 зеленому, 5 синьому — зеленому більше, бо око гостріше.
def fig_rgb565():
    W, H = 720, 330
    f = [text(W / 2, 26, "RGB565: колір у рівно 2 байти (16 біт)", size=16, bold=True)]

    # смуга 16 біт, розбита 5-6-5
    total_w = 560
    x0 = (W - total_w) / 2
    yb = 84
    bh = 46
    groups = [("R", 5, R), ("G", 6, G), ("B", 5, B)]
    bit_w = total_w / 16
    xi = x0
    for name, nbits, col in groups:
        gw = nbits * bit_w
        f.append(rect(xi, yb, gw, bh, fill=col, stroke=INK, sw=1.6, rx=4))
        f.append(text(xi + gw / 2, yb + bh / 2 - 2, name, size=15, color="#fff", bold=True))
        f.append(text(xi + gw / 2, yb + bh / 2 + 15, "%d біт" % nbits, size=10, color="#fff"))
        # позначки окремих бітів
        for b in range(nbits):
            f.append(line(xi + b * bit_w, yb, xi + b * bit_w, yb + bh, color="#ffffff", sw=0.6))
        xi += gw
    f.append(text(x0, yb - 8, "біт 15 (старший)", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x0 + total_w, yb - 8, "біт 0 (молодший)", size=9.5, color=MUTED, anchor="end"))

    # приклад: скільки рівнів на канал
    yb2 = yb + bh + 40
    f.append(text(W / 2, yb2, "рівнів на канал:  R,B → 2⁵ = 32     G → 2⁶ = 64", size=13, color=INK, bold=True))
    f.append(text(W / 2, yb2 + 22, "проти 256 у 8-бітному каналі — грубше, зате піксель удвічі легший (2 Б замість 3)",
                  size=11, color=MUTED))

    box = fitbox(70, yb2 + 44, W - 140, 56,
                 "16 біт діляться 5-6-5: зеленому дають зайвий біт, бо до нього око найгостріше (він несе\n"
                 "більшу частину яскравості). Такий піксель — рівно 2 байти: ідеально лягає у пам'ять\n"
                 "малих дисплеїв і економить удвічі проти RGB888, ціною видимих сходинок на плавних градієнтах.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "rgb565.svg"), W, H, *f)


# ── 5. Родовід: як аналоговий компроміс став записом 4:2:0 і кодом FourCC ─────
# Ідея (для hist-вставки): дві історичні нитки. Верхня — «колір рідше»:
# Валансі 1938 → NTSC 1953 (вужча смуга кольору) → Rec.601 1982 (4:2:2) →
# споживче 4:2:0. Нижня — чотирилітерний код: Apple OSType 1984 → EA IFF 1985
# → MS RIFF/AVI ~1991-92 → V4L2. Обидві сходяться в сучасному YUV-буфері.
def fig_lineage():
    W, H = 760, 470
    f = [text(W / 2, 26, "Родовід двох звичок: «колір рідше» і чотирилітерний код", size=16, bold=True)]

    node_fill = "#eef2ff"
    def node(cx, cy, w, h, lines, fill=node_fill, stroke="#4f5bd5", tcol=INK, sub=None):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=1.6, rx=7)
        ls = lines if isinstance(lines, list) else [lines]
        n = len(ls)
        y0 = cy - (n - 1) * 15 / 2 + 5
        for i, ln in enumerate(ls):
            out += text(cx, y0 + i * 15, ln, size=11.5, color=tcol, bold=(i == 0))
        return out

    def flow(x1, y, x2):
        return arrow(x1, y, x2, y, color="#8a8f98", sw=1.8)

    # ── НИТКА А: колір рідше (яскравість щільно) ──────────────────────────────
    yA = 96
    f.append(text(46, yA - 34, "Нитка А — «яскравість щільно, колір рідше»", size=12.5,
                  color="#c0392b", anchor="start", bold=True))
    ax = [118, 300, 486, 668]
    aw = 150
    f.append(node(ax[0], yA, aw, 52, ["Валансі · 1938", "поділ: яскравість +", "колір-різниці"],
                  fill="#fdecea", stroke="#c0392b"))
    f.append(node(ax[1], yA, aw, 52, ["NTSC · 1953", "колір вужчою смугою", "піднесучої"],
                  fill="#fdecea", stroke="#c0392b"))
    f.append(node(ax[2], yA, aw, 52, ["Rec. 601 · 1982", "4:2:2 — колір удвічі", "рідше (горизонталь)"],
                  fill="#fdecea", stroke="#c0392b"))
    f.append(node(ax[3], yA, aw, 52, ["споживче · далі", "4:2:0 — ще й удвічі", "по вертикалі"],
                  fill="#fdecea", stroke="#c0392b"))
    for i in range(3):
        f.append(flow(ax[i] + aw / 2, yA, ax[i + 1] - aw / 2))

    # анотація «звідки 4»
    f.append(text(ax[2], yA + 40, "«4» = привид частоти 4·f_sc, не 13.5 МГц", size=9.5,
                  color=MUTED, italic=True))

    # ── НИТКА Б: чотирилітерний код ───────────────────────────────────────────
    yB = 232
    f.append(text(46, yB - 34, "Нитка Б — формат як рівно чотири ASCII-байти", size=12.5,
                  color="#2457d6", anchor="start", bold=True))
    bx = [118, 300, 486, 668]
    bw = 150
    f.append(node(bx[0], yB, bw, 52, ["Apple · 1984", "OSType: 4-байтна", "мітка типу файла"],
                  fill="#eaf0fd", stroke="#2457d6"))
    f.append(node(bx[1], yB, bw, 52, ["EA IFF · 1985", "chunk під 4-байтним", "ідентифікатором"],
                  fill="#eaf0fd", stroke="#2457d6"))
    f.append(node(bx[2], yB, bw, 52, ["MS RIFF/AVI", "~1991-92 · назва", "«FourCC»"],
                  fill="#eaf0fd", stroke="#2457d6"))
    f.append(node(bx[3], yB, bw, 52, ["V4L2 (Linux)", "свій набір кодів,", "інша традиція"],
                  fill="#eaf0fd", stroke="#2457d6"))
    for i in range(3):
        f.append(flow(bx[i] + bw / 2, yB, bx[i + 1] - bw / 2))

    # ── Сходяться в сучасному буфері ──────────────────────────────────────────
    yC = 372
    f.append(node(W / 2, yC, 430, 46,
                  ["Сучасний YUV-буфер камери: код 'NV12' (нитка Б) + 4:2:0 (нитка А)",
                   "індекс кольору для пікселя (x, y) → (x/2, y/2)"],
                  fill="#eafaf0", stroke="#27ae60", tcol=INK))
    # стрілки-злиття від правих кінців обох ниток донизу
    f.append(arrow(ax[3], yA + 26, W / 2 + 120, yC - 23, color="#8a8f98", sw=1.6))
    f.append(arrow(bx[3], yB + 26, W / 2 + 120, yC - 23, color="#8a8f98", sw=1.6))

    # підпис-висновок
    f.append(text(W / 2, yC + 44, "кожна цифра й літера в коді має свою дату народження",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_planar_packed()
    fig_chroma_subsampling()
    fig_yuyv_nv12()
    fig_rgb565()
    fig_lineage()
    print("OK: 5 SVG у", IMG)
