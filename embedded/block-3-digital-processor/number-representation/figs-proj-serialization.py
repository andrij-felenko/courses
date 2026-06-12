# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.4.7 — «Серіалізація чисел у байти».
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1»/попередження червоний, «0»/межа синій;
«безпечно/переносно» зелене; стрілки через marker; шрифт sans-serif.
Підписи — Рис. 3.4.7a.k. Допоміжні функції скопійовані з figs.py розділу
(щоб скрипти не ділили файлів і loop'и не конфліктували).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# колір одного байта-«фарби» — щоб простежити, куди він переїхав
B_COL = {0: "#c0271e", 1: "#caa24a", 2: "#1f8a3b", 3: "#1f47b5"}   # MSB→LSB
B_TINT = {0: "#fdeceb", 1: "#fbf4e3", 2: "#eaf6ec", 3: "#eaeffb"}


def _bytebox(x, y, w, h, label, idx, sub=None):
    """Одна байтова комірка з кольоровою рамкою-«фарбою» байта idx."""
    out = rect(x, y, w, h, B_TINT[idx], B_COL[idx], 2.0, 6)
    out += mono(x + w / 2, y + h * 0.6, label, 16, INK, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h - 7, sub, 10.5, GREY, "middle")
    return out


# ── Рис. 3.4.7a.1 — серіалізація int32 у 4 байти (мережевий, big-endian) ─────
def fig_pack_int32():
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 34, "Серіалізація int32 у байтовий буфер явними зсувами (без union, без приведення вказівника)",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "число 0x12345678 → 4 байти в мережевому порядку (big-endian); код дає той самий буфер на будь-якій машині",
              12, GREY, "middle", style="italic")

    # ── джерело: 32-бітне число у регістрі
    rx, ry, rw, rh = 300, 84, 360, 56
    s += rect(rx, ry, rw, rh, "#f4f4f4", INK, 2.0, 8)
    s += text(rx + rw / 2, ry + 21, "значення в регістрі (uint32_t)", 13, INK, "middle", "bold")
    s += mono(rx + rw / 2, ry + 43, "v = 0x12345678", 16, INK, "middle", "bold")
    # підписи MSB/LSB над hex-парами
    hx = rx + 70
    labels = [("12", "MSB", 0), ("34", "", 1), ("56", "", 2), ("78", "LSB", 3)]

    # ── чотири маски-зсуви (ідея: дістаємо кожен байт окремо)
    s += text(60, 176, "крок 1 — дістаємо кожен байт зсувом і маскою:", 13, INK, "start", "bold")
    ops = [
        ("(v >> 24) & 0xFF", "= 0x12", 0),
        ("(v >> 16) & 0xFF", "= 0x34", 1),
        ("(v >>  8) & 0xFF", "= 0x56", 2),
        ("(v >>  0) & 0xFF", "= 0x78", 3),
    ]
    ow, oh = 200, 40
    oy = 190
    for i, (expr, val, idx) in enumerate(ops):
        ox = 60 + i * (ow + 18)
        s += rect(ox, oy, ow, oh, B_TINT[idx], B_COL[idx], 1.8, 6)
        s += mono(ox + 10, oy + 18, expr, 12.5, INK)
        s += mono(ox + ow - 10, oy + 33, val, 12.5, B_COL[idx], "end", "bold")
        # стрілка вниз до буфера
        s += arrow(ox + ow / 2, oy + oh + 6, ox + ow / 2, oy + oh + 40, B_COL[idx], 2.0)

    # ── буфер big-endian (мережевий): MSB за найменшою адресою
    s += text(60, oy + oh + 66, "крок 2 — кладемо в буфер старшим байтом уперед (мережевий порядок):",
              13, INK, "start", "bold")
    by = oy + oh + 76
    bw, bh = 200, 56
    addrs = ["buf[0]", "buf[1]", "buf[2]", "buf[3]"]
    vals = ["0x12", "0x34", "0x56", "0x78"]
    for i in range(4):
        bx = 60 + i * (bw + 18)
        s += _bytebox(bx, by, bw, bh, vals[i], i, addrs[i])
    # підпис «менша адреса → більша»
    s += arrow(60, by + bh + 28, 60 + 4 * (bw + 18) - 18, by + bh + 28, GREY, 1.6)
    s += text(60, by + bh + 22, "найменша адреса", 11, GREY, "start")
    s += text(60 + 4 * (bw + 18) - 18, by + bh + 22, "найбільша", 11, GREY, "end")

    # ── підсумкова стрічка: чому це переносно
    s += rect(60, H - 78, W - 120, 56, "#eef9ee", GREEN, 1.8, 10)
    s += text(W / 2, H - 54, "Код НЕ залежить від ендіанності машини: ми самі диктуємо порядок зсувами.",
              13, INK, "middle", "bold")
    s += text(W / 2, H - 34, "Розпакування — дзеркальне: v = (buf[0]<<24)|(buf[1]<<16)|(buf[2]<<8)|buf[3].  Хочеш little-endian — поміняй buf[0..3] місцями.",
              11.5, GREY, "middle", style="italic")
    save("fig-17-7a-1-pack-int32.svg", s)


# ── Рис. 3.4.7a.2 — union vs memcpy для роз-типування float у байти ──────────
def fig_union_vs_memcpy():
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 34, "Дістати байти float: union проти memcpy", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва читають ті самі 4 байти IEEE-754, але стандарт C дозволяє лише один із них",
              12, GREY, "middle", style="italic")

    # спільний підпис зверху: що серіалізуємо
    s += rect(330, 78, 300, 46, "#f4f4f4", INK, 1.8, 8)
    s += text(480, 98, "float f = 1.0f", 14, INK, "middle", "bold")
    s += mono(480, 117, "біти IEEE-754: 0x3F800000", 12, GREY, "middle")

    # ── ліва колонка: union (популярно, але формально UB у C++/строго)
    lx, lw = 60, 400
    s += rect(lx, 150, lw, 300, "#fdf4f4", RED, 1.9, 12)
    s += text(lx + lw / 2, 176, "union — спільна пам'ять", 15, RED, "middle", "bold")
    s += mono(lx + 22, 206, "union { float f;", 13, INK)
    s += mono(lx + 22, 226, "        uint8_t b[4]; } u;", 13, INK)
    s += mono(lx + 22, 250, "u.f = 1.0f;", 13, INK)
    s += mono(lx + 22, 270, "u.b[0] ... u.b[3]  // читаємо байти", 12.5, INK)
    # схема: одна комірка пам'яті, два «вікна»
    cy = 300
    s += rect(lx + 70, cy, 260, 34, "#ffffff", INK, 1.6, 4)
    for i in range(4):
        cxx = lx + 70 + i * 65
        s += line(cxx, cy, cxx, cy + 34, FAINT, 1.2) if i else ""
        s += mono(cxx + 32, cy + 22, ["3F", "80", "00", "00"][i], 12, INK, "middle")
    s += text(lx + 200, cy - 8, "ті самі 4 байти", 11, GREY, "middle", style="italic")
    s += text(lx + 200, cy + 54, "f і b[] — два «вікна» в одну комірку", 11.5, INK, "middle")
    # вирок
    s += rect(lx + 20, 380, lw - 40, 56, "#ffffff", RED, 1.5, 8)
    s += text(lx + lw / 2, 401, "У C — поширена практика й зазвичай працює.", 11.5, INK, "middle", "bold")
    s += text(lx + lw / 2, 420, "У C++ читати НЕ той член union — формально UB.", 11.5, RED, "middle", "bold")

    # ── права колонка: memcpy (завжди визначено)
    rxx, rw2 = 500, 400
    s += rect(rxx, 150, rw2, 300, "#eef9ee", GREEN, 1.9, 12)
    s += text(rxx + rw2 / 2, 176, "memcpy — байтова копія", 15, GREEN, "middle", "bold")
    s += mono(rxx + 22, 210, "uint8_t b[4];", 13, INK)
    s += mono(rxx + 22, 234, "memcpy(b, &f, 4);  // байт-у-байт", 12.5, INK)
    s += mono(rxx + 22, 258, "// b[] тепер копія байтів f", 12, GREEN)
    # схема: f → копія
    s += rect(rxx + 60, 290, 120, 34, "#ffffff", INK, 1.6, 4)
    s += text(rxx + 120, 284, "f (float)", 10.5, GREY, "middle")
    s += mono(rxx + 120, 312, "3F 80 00 00", 12, INK, "middle")
    s += arrow(rxx + 185, 307, rxx + 235, 307, GREEN, 2.2)
    s += text(rxx + 210, 297, "копія", 10.5, GREEN, "middle")
    s += rect(rxx + 240, 290, 120, 34, "#ffffff", GREEN, 1.6, 4)
    s += text(rxx + 300, 284, "b[4] (uint8_t)", 10.5, GREY, "middle")
    s += mono(rxx + 300, 312, "3F 80 00 00", 12, GREEN, "middle")
    # вирок
    s += rect(rxx + 20, 380, rw2 - 40, 56, "#ffffff", GREEN, 1.5, 8)
    s += text(rxx + rw2 / 2, 401, "Визначено і в C, і в C++. Компілятор оптимізує", 11.5, INK, "middle", "bold")
    s += text(rxx + rw2 / 2, 420, "memcpy сталого розміру в той самий код — без накладних.", 11.5, GREEN, "middle", "bold")

    # ── нижня стрічка: спільне попередження
    s += rect(60, H - 70, W - 120, 46, "#fff6e6", AMBER, 1.8, 10)
    s += text(W / 2, H - 47, "Спільна засторога: байти float переносні між машинами ЛИШЕ якщо обидві — IEEE-754 і однакової ендіанності.",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 29, "Перетинаєш мережу — домовся про формат: 4 байти IEEE-754 у фіксованому (зазвичай мережевому) порядку.",
              11.5, GREY, "middle", style="italic")
    save("fig-17-7a-2-union-vs-memcpy.svg", s)


if __name__ == "__main__":
    fig_pack_int32()
    fig_union_vs_memcpy()
    print("ch17 s7a (serialization) figures done.")
