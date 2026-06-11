# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 13.2 — «Графічний конвеєр» (Модуль 13).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — «Рис. M.R.T.k».
Допоміжні функції — спільні з рештою розділів курсу (копія, щоб loop'и не ділили файлів).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
GLASS = "#a9c8dd"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# колірні групи рядків (для наочного мапінгу память↔екран)
ROWCOL = ["#dfe7f5", "#dfeede", "#fdeede"]
ROWEDGE = ["#7d93c4", "#7daa86", "#caa24a"]


# ── Рис. 13.2.1.1 — память ↔ екран ───────────────────────────────────────────
def fig_fb_memory_screen():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Кадровий буфер: екран — це масив памʼяті, складений у рядки", 18, INK, "middle", "bold")
    # лінійна память (стрічка 12 комірок)
    mx, my, cw = 70, 96, 56
    s += text(mx, my - 10, "лінійна памʼять (адреси →)", 11, GREY, "start", "bold")
    for i in range(12):
        grp = i // 4
        s += rect(mx + i * cw, my, cw, 30, ROWCOL[grp], ROWEDGE[grp], 1.2)
        s += text(mx + i * cw + cw / 2, my + 20, str(i), 11, INK, "middle")
    # 2D-екран 4×3
    gx, gy, gc = 320, 190, 50
    s += text(gx + 2 * gc, gy - 10, "екран 4×3 (той самий масив)", 11, GREY, "middle", "bold")
    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            s += rect(gx + c * gc, gy + r * gc, gc, gc, ROWCOL[r], ROWEDGE[r], 1.2)
            s += text(gx + c * gc + gc / 2, gy + r * gc + gc / 2 + 5, str(idx), 12, INK, "middle", "bold")
    s += text(gx + 4 * gc + 14, gy + gc / 2 + 5, "← рядок 0", 11, ROWEDGE[0], "start", "bold")
    s += text(gx + 4 * gc + 14, gy + gc + gc / 2 + 5, "← рядок 1", 11, ROWEDGE[1], "start", "bold")
    s += text(gx + 4 * gc + 14, gy + 2 * gc + gc / 2 + 5, "← рядок 2", 11, ROWEDGE[2], "start", "bold")
    s += arrow(mx + 2 * cw, my + 32, gx + 2 * gc, gy - 4, ROWEDGE[0], 1.6, "4 3")
    s += text(W / 2, 344, "Перші W комірок памʼяті = рядок 0 екрана, наступні W = рядок 1, і так далі. Малювати — значить писати в ці комірки.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-1-memory-screen.svg", s)


# ── Рис. 13.2.1.2 — адреса пікселя ───────────────────────────────────────────
def fig_fb_addressing():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Адреса пікселя (x, y): рядок за рядком", 19, INK, "middle", "bold")
    gx, gy, gc = 70, 90, 34
    cols, rows = 8, 6
    for r in range(rows):
        for c in range(cols):
            fill = "#dff0e2" if (c == 3 and r == 2) else "#fbfbfb"
            s += rect(gx + c * gc, gy + r * gc, gc, gc, fill, GREY, 1)
    s += text(gx + 3 * gc + gc / 2, gy + 2 * gc + gc / 2 + 4, "•", 18, GREEN, "middle", "bold")
    s += text(gx + 3 * gc + gc / 2, gy - 8, "x=3", 10, GREEN, "middle", "bold")
    s += text(gx - 8, gy + 2 * gc + gc / 2 + 4, "y=2", 10, GREEN, "end", "bold")
    s += text(gx + cols * gc / 2, gy + rows * gc + 22, "ширина W = 8", 11, GREY, "middle")
    # формула
    fx = 380
    s += text(fx, 120, "зсув у масиві:", 13, INK, "start", "bold")
    s += rect(fx, 132, 380, 40, "#eef4f8", INK, 1.4, 6)
    s += text(fx + 190, 157, "offset = (y·W + x) · байтів_на_піксель", 13, INK, "middle", "bold")
    s += text(fx, 200, "адреса = база + offset", 13, INK, "start")
    s += text(fx, 232, "для (3, 2), W=8, 2 байти/піксель:", 12, GREY, "start")
    s += rect(fx, 244, 380, 36, "#e7f5ea", GREEN, 1.4, 6)
    s += text(fx + 190, 267, "offset = (2·8 + 3)·2 = 38 байтів", 13, INK, "middle", "bold")
    s += text(W / 2, 330, "Рядки інколи доповнюють до межі — тоді в формулі замість W беруть «крок рядка» (stride).",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-2-addressing.svg", s)


# ── Рис. 13.2.1.3 — скільки RAM зʼїдає кадр ──────────────────────────────────
def fig_fb_size():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Скільки RAM зʼїдає один кадр = W × H × (біт/піксель ÷ 8)", 17, INK, "middle", "bold")
    cols = ["роздільність", "1 біт", "8 біт", "16 біт", "24 біти"]
    rows = [
        ("128×64", "1.0 КБ", "8 КБ", "16 КБ", "24 КБ"),
        ("320×240", "9.4 КБ", "75 КБ", "150 КБ", "225 КБ"),
        ("480×272", "16 КБ", "128 КБ", "255 КБ", "383 КБ"),
        ("800×480", "47 КБ", "375 КБ", "750 КБ", "1.1 МБ"),
    ]
    colw = [150, 130, 130, 130, 130]
    x0, y0, rh = 70, 68, 44
    cx = x0
    for j, h in enumerate(cols):
        s += rect(cx, y0, colw[j], 36, "#eef0f2", GREY, 1.2)
        s += text(cx + colw[j] / 2, y0 + 22, h, 12, INK, "middle", "bold")
        cx += colw[j]
    for i, row in enumerate(rows):
        ry = y0 + 36 + i * rh
        cx = x0
        for j, val in enumerate(row):
            fill = "#f6f7f8" if j == 0 else ("#fdeceb" if j >= 3 else "#e7f5ea")
            s += rect(cx, ry, colw[j], rh, fill if j > 0 else "#eef4f8", GREY, 1.1)
            col = INK if j == 0 else (RED if j >= 3 else GREEN)
            s += text(cx + colw[j] / 2, ry + rh / 2 + 5, val, 12, col, "middle", "bold" if j == 0 else "normal")
            cx += colw[j]
    s += text(W / 2, 300, "Глибший колір і більший екран множать памʼять. Часто кадр — найбільший споживач RAM у всьому пристрої.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-3-size.svg", s)


# ── Рис. 13.2.1.4 — малювання = запис у памʼять ──────────────────────────────
def fig_fb_drawing():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Малювання — це послідовність записів у масив", 19, INK, "middle", "bold")
    s += rect(70, 90, 150, 70, "#eef2f5", INK, 1.6, 6)
    s += text(145, 122, "set_pixel(x,y,c)", 12, INK, "middle", "bold")
    s += text(145, 142, "«постав піксель»", 9.5, GREY, "middle")
    s += arrow(220, 125, 280, 125, INK, 2)
    s += rect(280, 90, 160, 70, "#eef4f8", INK, 1.6, 6)
    s += text(360, 118, "адреса =", 11, INK, "middle", "bold")
    s += text(360, 136, "база+(y·W+x)·бпп", 10, GREY, "middle")
    s += arrow(440, 125, 500, 125, INK, 2)
    # масив комірок
    mx, my, cw = 510, 108, 34
    for i in range(8):
        fill = "#dff0e2" if i == 3 else "#ffffff"
        s += rect(mx + i * cw, my, cw, 34, fill, GREY, 1)
    s += text(mx + 3 * cw + cw / 2, my + 22, "c", 12, GREEN, "middle", "bold")
    s += text(mx + 4 * cw, my - 8, "записати колір у комірку", 10, GREY, "middle")
    s += text(W / 2, 230, "Лінія, текст, картинка — усе зводиться до багатьох таких записів. Кадровий буфер дає **довільний доступ**:",
              12, INK, "middle")
    s += text(W / 2, 252, "торкайся будь-якого пікселя будь-коли, склади все в памʼяті — і виштовхни готовий кадр на екран.",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 296, "Саме заради цієї свободи компонувати в памʼяті й тримають кадровий буфер.", 11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-4-drawing.svg", s)


# ── Рис. 13.2.1.5 — пакування біт на піксель ─────────────────────────────────
def fig_fb_packing():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Біт на піксель: коли піксель менший за байт", 19, INK, "middle", "bold")
    # 1bpp: 1 байт = 8 пікселів
    s += text(120, 92, "1 біт/піксель", 13, INK, "middle", "bold")
    bx, by, bw = 60, 104, 16
    for i in range(8):
        bit = [1, 0, 1, 1, 0, 0, 1, 0][i]
        s += rect(bx + i * bw, by, bw, 26, INK if bit else "#ffffff", INK, 1)
        s += text(bx + i * bw + bw / 2, by + 18, str(bit), 9, "#ffffff" if bit else INK, "middle")
    s += rect(bx, by, 8 * bw, 26, "none", RED, 2)
    s += text(120, by + 48, "1 байт = 8 пікселів", 11, RED, "middle", "bold")
    s += text(120, by + 66, "поставити один → читай-міняй-пиши цілий байт", 9.5, GREY, "middle")
    # 16bpp: 1 піксель = 2 байти
    s += text(560, 92, "16 біт/піксель", 13, INK, "middle", "bold")
    px = 470
    for i in range(3):
        s += rect(px + i * 78, 104, 78, 26, ["#dfe7f5", "#dfeede", "#fdeede"][i], ROWEDGE[i], 1.4)
        s += text(px + i * 78 + 39, 122, "піксель", 10, INK, "middle")
        s += text(px + i * 78 + 39, 146, "2 байти", 9, GREY, "middle")
    s += text(560, 170, "1 піксель = 2 байти — проста адресація, пишеш напряму", 10, GREEN, "middle", "bold")
    s += text(W / 2, 250, "Менше за байт (1, 2, 4 біти) — пікселі пакують у байт, і зміна одного вимагає читай-міняй-пиши",
              12, INK, "middle")
    s += text(W / 2, 272, "(згадайте сторінкову памʼять SSD1306). Від 8 біт кожен піксель — цілі байти, адресувати легко.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-5-packing.svg", s)


# ── Рис. 13.2.1.6 — кадр проти RAM мікроконтролера ───────────────────────────
def fig_fb_vs_sram():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Кадр проти RAM мікроконтролера: хто кого", 19, INK, "middle", "bold")
    ax0, ay, ax1 = 90, 280, 760
    s += line(ax0, ay, ax1, ay, INK, 2)

    def xb(kb):
        return ax0 + min(kb, 800) / 800.0 * (ax1 - ax0)

    items = [
        ("кадр 320×240×16", 150, RED, 1),
        ("кадр 480×272×16", 255, RED, 0),
        ("кадр 800×480×16", 750, RED, 1),
        ("малий МК (SRAM)", 20, BLUE, 0),
        ("середній МК", 256, BLUE, 1),
        ("великий МК", 512, BLUE, 0),
    ]
    y = 70
    for (lbl, kb, col, _hi) in items:
        s += rect(ax0, y, xb(kb) - ax0, 22, "#fdeceb" if col == RED else "#e9eefb", col, 1.4)
        s += text(ax0 + 6, y + 16, lbl, 10.5, col, "start", "bold")
        s += text(xb(kb) + 6, y + 16, (str(kb) + " КБ" if kb < 1000 else "0.75 МБ"), 10, GREY, "start")
        y += 32
    for kb in (100, 250, 500, 750):
        s += line(xb(kb), ay - 4, xb(kb), ay + 4, INK, 1.2)
        s += text(xb(kb), ay + 20, str(kb), 9.5, GREY, "middle")
    s += text(ax1, ay + 20, "КБ", 10, INK, "start")
    s += text(W / 2, 318, "Великий кадр легко переростає SRAM навіть пристойного МК — звідси зовнішня памʼять або розумна панель.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1-6-vs-sram.svg", s)


def minibits(x, y, cs, pattern, color=INK):
    out = ""
    for r, row in enumerate(pattern):
        for c, v in enumerate(row):
            if v == "X":
                out += rect(x + c * cs, y + r * cs, cs, cs, color, color, 0.4)
    return out


# ── Рис. 13.2.1і.1 — знаковий проти бітмапного екрана ────────────────────────
def fig_alto_char_vs_bitmap():
    W, H = 820, 372
    s = header(W, H)
    s += text(W / 2, 32, "Знаковий екран проти бітмапного: чому PARC обрав кожен піксель", 17, INK, "middle", "bold")
    gx, gy, gc = 70, 92, 50
    s += text(gx + 3 * gc, 74, "ЗНАКОВИЙ (до Alto)", 13, INK, "middle", "bold")
    letters = "ABCEFHKLMNOPRSTUVWXYZ"
    k = 0
    for r in range(4):
        for c in range(6):
            s += rect(gx + c * gc, gy + r * gc, gc, gc, "#fbfbfb", GREY, 1)
            s += text(gx + c * gc + gc / 2, gy + r * gc + gc / 2 + 8, letters[k % len(letters)], 20, INK, "middle")
            k += 1
    s += text(gx + 3 * gc, gy + 4 * gc + 22, "лише готові символи з ПЗП;", 10.5, GREY, "middle")
    s += text(gx + 3 * gc, gy + 4 * gc + 38, "один шрифт, жодної графіки", 10.5, GREY, "middle")
    rx = 452
    s += text(rx + 150, 74, "БІТМАПНИЙ (Alto)", 13, INK, "middle", "bold")
    s += rect(rx, gy, 300, 200, "#fbfbfb", GREY, 1.2)
    pts = []
    for i in range(0, 44):
        pts.append((rx + 18 + i * 4, gy + 52 + 26 * math.sin(i / 4.5)))
    for i in range(len(pts) - 1):
        s += line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], INK, 2)
    s += line(rx + 36, gy + 158, rx + 86, gy + 112, INK, 2)
    s += line(rx + 86, gy + 112, rx + 86, gy + 158, INK, 2)
    s += line(rx + 36, gy + 158, rx + 86, gy + 158, INK, 2)
    s += text(rx + 150, gy + 145, "Aa fi — пропорційний шрифт", 13, INK, "start")
    s += text(rx + 150, gy + 4 * gc + 22, "кожен піксель вільний:", 10.5, GREEN, "middle", "bold")
    s += text(rx + 150, gy + 4 * gc + 38, "шрифти, графіка, WYSIWYG", 10.5, GREEN, "middle", "bold")
    save("fig-13-2-1i-1-char-vs-bitmap.svg", s)


# ── Рис. 13.2.1і.2 — BitBlt ──────────────────────────────────────────────────
def fig_alto_bitblt():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 32, "BitBlt: копіювати прямокутник пікселів (предок усіх «блітерів»)", 17, INK, "middle", "bold")
    pat = ["..XX..", "..XXX.", "XXXXXX", "XXXXXX", "..XXX.", "..XX.."]
    bs = 120
    cs = bs / 6
    sx, sy = 90, 96
    s += rect(sx, sy, bs, bs, "#fbfbfb", INK, 1.6)
    s += minibits(sx, sy, cs, pat, INK)
    s += text(sx + bs / 2, sy - 10, "джерело", 11, INK, "middle", "bold")
    s += arrow(sx + bs + 12, sy + bs / 2, sx + bs + 92, sy + bs / 2, GREEN, 2.4)
    s += text(sx + bs + 52, sy + bs / 2 - 12, "копіювати", 10, GREEN, "middle", "bold")
    dx = sx + bs + 100
    s += rect(dx, sy, bs, bs, "#eef4f8", INK, 1.6)
    s += minibits(dx, sy, cs, pat, "#3a5e86")
    s += text(dx + bs / 2, sy - 10, "приймач", 11, INK, "middle", "bold")
    s += rect(dx + bs + 36, sy + 18, 226, 84, "#e7f5ea", GREEN, 1.4, 6)
    s += text(dx + bs + 149, sy + 42, "+ логічна операція", 12, INK, "middle", "bold")
    s += text(dx + bs + 149, sy + 62, "AND / OR / XOR", 12, GREEN, "middle", "bold")
    s += text(dx + bs + 149, sy + 82, "→ маска, прозорість", 11, GREY, "middle")
    s += text(W / 2, 288, "Одна операція рухає цілий прямокутник пікселів — і робить швидкими вікна, шрифти й анімацію. Прямий предок 2D-прискорювачів.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-1i-2-bitblt.svg", s)


# ── Рис. 13.2.2.1 — прямий колір проти індексу ───────────────────────────────
def fig_direct_vs_indexed():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 32, "Що означає число в комірці: прямий колір проти індексу", 18, INK, "middle", "bold")
    y1 = 92
    s += text(70, y1 - 12, "ПРЯМИЙ: біти — це самі R, G, B", 12.5, INK, "start", "bold")
    s += rect(70, y1, 130, 40, "#fbfbfb", INK, 1.4)
    s += text(135, y1 + 25, "11001·010110·01010", 10.5, INK, "middle")
    s += arrow(205, y1 + 20, 250, y1 + 20, INK, 2)
    s += rect(250, y1, 38, 40, "#cf4040", INK, 1)
    s += rect(290, y1, 38, 40, "#3aaa4a", INK, 1)
    s += rect(330, y1, 38, 40, "#3a5acf", INK, 1)
    s += text(269, y1 + 56, "R", 10, RED, "middle")
    s += text(309, y1 + 56, "G", 10, GREEN, "middle")
    s += text(349, y1 + 56, "B", 10, BLUE, "middle")
    s += arrow(372, y1 + 20, 418, y1 + 20, INK, 2)
    s += rect(418, y1, 56, 40, "#8a6ab0", INK, 1.4)
    s += text(446, y1 + 56, "колір", 10, INK, "middle")
    y2 = 230
    s += text(70, y2 - 12, "ІНДЕКСОВАНИЙ: число — це індекс у таблицю кольорів", 12.5, INK, "start", "bold")
    s += rect(70, y2, 130, 40, "#fbfbfb", INK, 1.4)
    s += text(135, y2 + 25, "індекс = 5", 12, INK, "middle")
    s += arrow(205, y2 + 20, 252, y2 + 20, INK, 2)
    pal = ["#222222", "#cf4040", "#3aaa4a", "#3a5acf", "#caa24a", "#8a6ab0", "#22aaaa", "#cccccc"]
    for i, col in enumerate(pal):
        yy = y2 - 30 + i * 13
        s += rect(252, yy, 22, 13, col, GREY, 0.6)
        s += text(246, yy + 11, str(i), 8, GREY, "end")
    s += rect(250, y2 - 30 + 5 * 13 - 2, 26, 17, "none", RED, 2)
    s += text(286, y2 - 30 + 4 * 13, "таблиця (палітра)", 9.5, GREY, "start")
    s += arrow(300, y2 + 20, 380, y2 + 20, INK, 2)
    s += rect(380, y2, 56, 40, "#8a6ab0", INK, 1.4)
    s += text(408, y2 + 56, "колір №5", 10, INK, "middle")
    s += text(W / 2, 344, "Прямий — швидко й просто, але по 2–3 байти на піксель. Індекс — економно, та лише N кольорів нараз.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-1-direct-indexed.svg", s)


# ── Рис. 13.2.2.2 — розкладка RGB565 ─────────────────────────────────────────
def fig_rgb565_layout():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 32, "RGB565: 16 біт = 5 червоних + 6 зелених + 5 синіх", 18, INK, "middle", "bold")
    bx, by, bw = 60, 110, 44
    groups = [(5, "#f3c0bd", RED, "5 біт R"), (6, "#cdeccd", GREEN, "6 біт G"), (5, "#cfe0ee", BLUE, "5 біт B")]
    x = bx
    bit = 15
    for (n, fill, col, lab) in groups:
        gx0 = x
        for i in range(n):
            s += rect(x, by, bw, 40, fill, col, 1.2)
            s += text(x + bw / 2, by + 25, str(bit), 11, INK, "middle")
            x += bw
            bit -= 1
        s += text((gx0 + x) / 2, by + 62, lab, 12, col, "middle", "bold")
    s += text(W / 2, 210, "Усього 16 біт = 2 байти на піксель і 65 536 кольорів. Зеленому дають зайвий, 6-й біт —",
              12, INK, "middle")
    s += text(W / 2, 232, "бо око найчутливіше саме до зеленого (чому й як конвертувати — у 🧮-вставці до теми).",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-2-rgb565.svg", s)


# ── Рис. 13.2.2.3 — компроміс глибини ────────────────────────────────────────
def fig_bpp_tradeoff():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 32, "Глибина кольору: кольори проти пам'яті", 19, INK, "middle", "bold")
    cols = ["формат", "біт/пікс", "кольорів", "байт/пікс", "кадр 320×240"]
    rows = [
        ("моно", "1", "2", "—", "9.4 КБ", False),
        ("RGB332", "8", "256", "1", "75 КБ", False),
        ("RGB565", "16", "65 536", "2", "150 КБ", True),
        ("RGB888", "24", "16.7 млн", "3", "225 КБ", False),
    ]
    colw = [130, 110, 130, 110, 150]
    x0, y0, rh = 95, 64, 46
    cx = x0
    for j, h in enumerate(cols):
        s += rect(cx, y0, colw[j], 34, "#eef0f2", GREY, 1.2)
        s += text(cx + colw[j] / 2, y0 + 22, h, 12, INK, "middle", "bold")
        cx += colw[j]
    for i, row in enumerate(rows):
        ry = y0 + 34 + i * rh
        cx = x0
        hi = row[5]
        for j in range(5):
            fill = "#e7f5ea" if hi else ("#f6f7f8" if j == 0 else "#ffffff")
            s += rect(cx, ry, colw[j], rh, fill, GREEN if hi else GREY, 1.4 if hi else 1.1)
            s += text(cx + colw[j] / 2, ry + rh / 2 + 5, row[j], 12, INK, "middle", "bold" if j == 0 or hi else "normal")
            cx += colw[j]
    s += text(W / 2, 284, "RGB565 — золота середина embedded: майже «справжній» колір за половину пам'яті RGB888.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-3-bpp.svg", s)


# ── Рис. 13.2.2.4 — палітра ──────────────────────────────────────────────────
def fig_palette():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 32, "Палітра: малий індекс → колір із таблиці", 19, INK, "middle", "bold")
    idxmap = [[1, 1, 2, 2], [1, 3, 3, 2], [4, 3, 3, 4], [4, 4, 5, 5]]
    pal = ["#ffffff", "#cf4040", "#3a5acf", "#caa24a", "#3aaa4a", "#8a6ab0"]
    gx, gy, gc = 70, 96, 36
    s += text(gx + 2 * gc, gy - 12, "кадр = індекси", 11, INK, "middle", "bold")
    for r in range(4):
        for c in range(4):
            s += rect(gx + c * gc, gy + r * gc, gc, gc, "#fbfbfb", GREY, 1)
            s += text(gx + c * gc + gc / 2, gy + r * gc + gc / 2 + 5, str(idxmap[r][c]), 13, INK, "middle", "bold")
    px, py = 310, 84
    s += text(px + 55, py - 4, "палітра", 11, INK, "middle", "bold")
    for i, col in enumerate(pal):
        yy = py + i * 26
        s += rect(px, yy, 26, 22, col, GREY, 1)
        s += text(px - 8, yy + 16, str(i), 10, GREY, "end")
        s += text(px + 34, yy + 16, ["білий", "червоний", "синій", "жовтий", "зелений", "бузковий"][i], 10, INK, "start")
    rx, ry, rc = 600, 96, 36
    s += text(rx + 2 * rc, ry - 12, "рендер = кольори", 11, INK, "middle", "bold")
    for r in range(4):
        for c in range(4):
            s += rect(rx + c * rc, ry + r * rc, rc, rc, pal[idxmap[r][c]], GREY, 1)
    s += arrow(250, 170, 300, 170, INK, 2)
    s += arrow(470, 170, 596, 170, INK, 2)
    s += text(W / 2, 300, "1 байт індексу на піксель + крихітна таблиця = малий кадр, та будь-які N кольорів. Зміниш таблицю — зміниться вся картинка.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-4-palette.svg", s)


# ── Рис. 13.2.2.5 — альфа й накладання ───────────────────────────────────────
def fig_alpha_blend():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 32, "Альфа: прозорість для накладання", 19, INK, "middle", "bold")
    s += rect(70, 80, 110, 110, "#cfe0ee", INK, 1.4)
    s += text(125, 204, "тло (dst)", 10, INK, "middle")
    s += rect(110, 110, 110, 110, "#cf4040", INK, 1.4)
    s += rect(110, 110, 110, 110, "#cf4040", "none", 0)
    s += text(165, 240, "напівпрозоре (src, α=0.5)", 9.5, RED, "middle")
    s += arrow(245, 150, 305, 150, INK, 2)
    s += rect(320, 80, 110, 110, "#cfe0ee", INK, 1.4)
    s += rect(360, 110, 110, 110, "#9f7090", INK, 1.4)
    s += text(415, 204, "результат накладання", 10, INK, "middle")
    s += rect(520, 96, 250, 56, "#eef4f8", INK, 1.4, 6)
    s += text(645, 120, "out = src·α + dst·(1−α)", 13, INK, "middle", "bold")
    s += text(645, 140, "α=1 непрозоро · α=0 невидимо", 10, GREY, "middle")
    s += rect(520, 176, 250, 70, "#fff8e8", "#b07d18", 1.4, 6)
    s += text(645, 198, "дешева заміна — колірний ключ:", 11, INK, "middle", "bold")
    s += text(645, 218, "один колір (напр. пурпур) = прозорий,", 10, GREY, "middle")
    s += text(645, 234, "решта малюється; без альфа-каналу", 10, GREY, "middle")
    s += text(W / 2, 296, "Альфу беруть під час малювання (накладання шарів), а на екран іде вже змішаний колір — сам екран прозорости не має.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-5-alpha.svg", s)


# ── Рис. 13.2.2.6 — порядок байтів і втрата відтінків ────────────────────────
def fig_byte_order():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 32, "Дрібні пастки: порядок байтів і втрата відтінків", 18, INK, "middle", "bold")
    s += text(190, 76, "16-бітний піксель = 2 байти", 12, INK, "middle", "bold")
    s += rect(80, 92, 100, 36, "#f3c0bd", INK, 1.2)
    s += text(130, 115, "старший", 10, INK, "middle")
    s += rect(180, 92, 100, 36, "#cfe0ee", INK, 1.2)
    s += text(230, 115, "молодший", 10, INK, "middle")
    s += rect(95, 150, 50, 40, "#cf4040", INK, 1.4)
    s += text(120, 204, "вірно", 10, GREEN, "middle", "bold")
    s += arrow(155, 170, 205, 170, GREY, 1.8, "4 3")
    s += text(180, 162, "переплутав байти", 9, GREY, "middle")
    s += rect(215, 150, 50, 40, "#3a5acf", INK, 1.4)
    s += text(240, 204, "синій замість червоного!", 9.5, RED, "middle", "bold")
    s += text(230, 230, "(той самий збій, що RGB↔BGR)", 9.5, GREY, "middle")
    s += text(580, 76, "RGB888 → RGB565: відкидаємо біти", 11.5, INK, "middle", "bold")
    for i in range(40):
        shade = 60 + i * 4
        s += rect(400 + i * 9, 96, 9, 30, f"#{shade:02x}{shade:02x}{shade:02x}", "none", 0)
    s += text(580, 142, "плавний градієнт (24 біти)", 9.5, GREY, "middle")
    for i in range(8):
        shade = 70 + i * 22
        s += rect(400 + i * 45, 160, 45, 30, f"#{shade:02x}{shade:02x}{shade:02x}", "none", 0)
    s += text(580, 206, "смуги (banding) після утиску до 16 біт", 9.5, RED, "middle", "bold")
    s += text(580, 232, "ліки — дизеринг (підмішати шум)", 9.5, GREY, "middle")
    s += text(W / 2, 296, "Перевір порядок байтів пікселя (часта причина «червоне стало синім») і пам'ятай: утиск глибини губить плавність.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-2-6-byte-order.svg", s)


def _grid(gx, gy, gc, cols, rows, color=FAINT):
    out = ""
    for r in range(rows):
        for c in range(cols):
            out += rect(gx + c * gc, gy + r * gc, gc, gc, "none", color, 1)
    return out


def _cell(gx, gy, gc, c, r, fill=INK, stroke=None):
    return rect(gx + c * gc, gy + r * gc, gc, gc, fill, stroke or fill, 0.6)


# ── Рис. 13.2.3.1 — що таке растеризація ─────────────────────────────────────
def fig_rasterization():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 32, "Растеризація: перетворити форму на пікселі сітки", 18, INK, "middle", "bold")
    gx, gy, gc = 70, 84, 26
    s += _grid(gx, gy, gc, 10, 7)
    s += line(gx + 12, gy + 12, gx + 9 * gc + 14, gy + 6 * gc + 14, INK, 2.2)
    s += text(gx + 5 * gc, gy + 7 * gc + 24, "ідеальна лінія (нескінченно тонка)", 10.5, GREY, "middle")
    rx = 470
    s += _grid(rx, gy, gc, 10, 7)
    stair = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 3), (6, 3), (7, 4), (8, 4), (9, 5)]
    for (c, r) in stair:
        s += _cell(rx, gy, gc, c, r, "#2b2f33")
    s += text(rx + 5 * gc, gy + 7 * gc + 24, "растр: які клітинки засвітити", 10.5, GREY, "middle")
    s += text(W / 2, 326, "Форми неперервні, а пікселі — дискретні квадрати. Растеризація — це вибір клітинок, що найкраще передають форму.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-3-1-rasterization.svg", s)


# ── Рис. 13.2.3.2 — прямокутник спанами ──────────────────────────────────────
def fig_rect_spans():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 32, "Прямокутник заливають СПАНАМИ — цілий рядок за раз", 18, INK, "middle", "bold")
    gx, gy, gc = 90, 84, 24
    for r in range(6):
        for c in range(8):
            s += rect(gx + c * gc, gy + r * gc, gc, gc, "#dfe7f5", "#7d93c4", 0.6)
        s += arrow(gx - 6, gy + r * gc + gc / 2, gx + 8 * gc + 4, gy + r * gc + gc / 2, GREEN, 1.6)
    s += text(gx + 4 * gc, gy + 6 * gc + 26, "6 спанів по 8 пікселів — швидко", 11, GREEN, "middle", "bold")
    rx = 500
    for r in range(6):
        for c in range(8):
            s += circle(rx + c * gc + gc / 2, gy + r * gc + gc / 2, 3, INK, INK, 1)
    s += text(rx + 4 * gc, gy + 6 * gc + 26, "48 окремих set_pixel — повільно", 11, RED, "middle")
    s += text(W / 2, 296, "Горизонтальний спан (заповнити рядок одним проходом, як memset) — найшвидший будівельний блок усієї графіки.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-2-3-2-rect-spans.svg", s)


# ── Рис. 13.2.3.3 — растеризація лінії ───────────────────────────────────────
def fig_line_raster():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 32, "Лінія: крокуємо по довшій осі, ціла похибка вирішує зсув", 18, INK, "middle", "bold")
    gx, gy, gc = 80, 80, 30
    s += _grid(gx, gy, gc, 12, 6)
    line_cells = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3), (10, 4), (11, 4)]
    for (c, r) in line_cells:
        s += _cell(gx, gy, gc, c, r, "#dff0e2", GREEN)
    s += line(gx + 8, gy + 8, gx + 11 * gc + 22, gy + 4 * gc + 22, INK, 1.6, "5 3")
    for c in range(12):
        s += line(gx + c * gc + gc / 2, gy + 6 * gc + 4, gx + c * gc + gc / 2, gy + 6 * gc + 12, GREY, 1)
    s += text(gx + 6 * gc, gy + 6 * gc + 28, "крок по X (довша вісь): на кожен X — рівно один піксель", 10.5, GREY, "middle")
    s += text(W / 2, 300, "Похибку «наскільки лінія відійшла від рядка» ведуть ЦІЛИМ числом — без float; коли вона переростає половину, зсувають Y.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 322, "Це й є ідея Брезенхема (повний алгоритм — в ⚙️-вставці до теми).", 11, INK, "middle", "bold")
    save("fig-13-2-3-3-line.svg", s)


# ── Рис. 13.2.3.4 — коло через симетрію ──────────────────────────────────────
def fig_circle_symmetry():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 32, "Коло: порахуй 1/8, відобрази 8 разів", 18, INK, "middle", "bold")
    cx, cy, R = 380, 180, 110
    s += circle(cx, cy, R, "none", FAINT, 1.4)
    s += line(cx - R - 16, cy, cx + R + 16, cy, FAINT, 1)
    s += line(cx, cy - R - 16, cx, cy + R + 16, FAINT, 1)
    s += line(cx, cy, cx + R, cy - R, FAINT, 1)
    s += line(cx, cy, cx - R, cy - R, FAINT, 1)
    s += line(cx, cy, cx + R, cy + R, FAINT, 1)
    s += line(cx, cy, cx - R, cy + R, FAINT, 1)
    # один октант жирно (від верху до 45°)
    import math as _m
    for a in range(248, 271, 3):
        rad = _m.radians(a)
        s += circle(cx + R * _m.cos(rad), cy + R * _m.sin(rad), 4, GREEN, GREEN, 1)
    s += text(cx + 40, cy - R + 6, "порахований октант", 10.5, GREEN, "start", "bold")
    # дзеркальні точки (приклад однієї точки у 8 місцях)
    ex, ey = 0.80, 0.60
    for (sx, sy, swap) in [(1, -1, 0), (-1, -1, 0), (1, 1, 0), (-1, 1, 0), (1, -1, 1), (-1, -1, 1), (1, 1, 1), (-1, 1, 1)]:
        dx = (ey if swap else ex) * R * sx
        dy = (ex if swap else ey) * R * sy
        s += circle(cx + dx, cy + dy, 4, BLUE, BLUE, 1)
    s += text(cx, cy + R + 36, "одна обчислена точка дає вісім — відображенням по осях і діагоналі", 10.5, GREY, "middle")
    s += text(W / 2, 322, "Симетрія кола економить 7/8 роботи; самі точки теж знаходять цілими числами, без тригонометрії на льоту.",
              11, GREY, "middle", style="italic")
    save("fig-13-2-3-4-circle.svg", s)


# ── Рис. 13.2.3.5 — текст як гліфи ───────────────────────────────────────────
def fig_text_glyphs():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 32, "Текст: літера — це маленький бітмап (гліф), що його блітять", 17, INK, "middle", "bold")
    glyphs = {
        "H": ["X..X", "X..X", "XXXX", "X..X", "X..X"],
        "i": [".X..", "....", ".X..", ".X..", ".X.."],
        "!": [".X..", ".X..", ".X..", "....", ".X.."],
    }
    gx, gy, cs = 80, 90, 12
    x = gx
    s += text(gx, 76, "монопростір (однакова ширина)", 11, INK, "start", "bold")
    for ch in "Hi!":
        s += rect(x - 2, gy - 2, 4 * cs + 4, 5 * cs + 4, "none", GREY, 1, 2)
        s += minibits(x, gy, cs, glyphs[ch], "#2b2f33")
        s += text(x + 2 * cs, gy + 5 * cs + 16, ch, 12, GREY, "middle")
        s += arrow(x + 4 * cs + 4, gy + 2.5 * cs, x + 5 * cs + 6, gy + 2.5 * cs, GREEN, 1.4)
        x += 5 * cs + 8
    s += text(x + 8, gy + 2.5 * cs, "курсор →", 10, GREEN, "start")
    s += text(470, 76, "пропорційний (своя ширина в кожної)", 11, INK, "start", "bold")
    px = 470
    widths = {"H": 4, "i": 2, "!": 2}
    for ch in "Hi!":
        s += minibits(px, gy, cs, glyphs[ch], "#2b2f33")
        s += rect(px - 2, gy - 2, widths[ch] * cs + 4, 5 * cs + 4, "none", "#caa24a", 1, 2)
        px += widths[ch] * cs + 8
    s += text(px + 8, gy + 2.5 * cs, "вужчі літери —", 10, "#9a7d2e", "start")
    s += text(px + 8, gy + 2.5 * cs + 15, "менший крок", 10, "#9a7d2e", "start")
    s += text(W / 2, 282, "Намалювати текст = поставити кожен гліф у курсор (це бліт, як BitBlt в Alto) і зсунути курсор на ширину.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 304, "Як саме роблять самі гліфи й згладжують їх — у наступній темі.", 11, GREY, "middle", style="italic")
    save("fig-13-2-3-5-text.svg", s)


# ── Рис. 13.2.3.6 — аліасинг і відсікання ────────────────────────────────────
def fig_alias_clip():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 32, "Сходинки (аліасинг) і відсікання (clipping)", 18, INK, "middle", "bold")
    gx, gy, gc = 70, 84, 22
    s += text(gx + 3 * gc, 74, "аліасинг", 11.5, INK, "middle", "bold")
    s += _grid(gx, gy, gc, 7, 6)
    jag = [(0, 5), (1, 4), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)]
    for (c, r) in jag:
        s += _cell(gx, gy, gc, c, r, "#2b2f33")
    s += text(gx + 3 * gc, gy + 6 * gc + 20, "ступінчасто", 10, RED, "middle")
    ax = 270
    s += _grid(ax, gy, gc, 7, 6)
    for (c, r) in jag:
        s += _cell(ax, gy, gc, c, r, "#2b2f33")
    soft = [(0, 4), (1, 5), (1, 3), (2, 3), (3, 4), (3, 2), (4, 3), (4, 1), (5, 2), (5, 0), (6, 1)]
    for (c, r) in soft:
        s += _cell(ax, gy, gc, c, r, "#b8bcc0")
    s += text(ax + 3 * gc, gy + 6 * gc + 20, "згладжено (сірі краї)", 10, GREEN, "middle")
    # clipping
    clx = 540
    s += text(clx + 110, 74, "відсікання до прямокутника", 11.5, INK, "middle", "bold")
    s += rect(clx, gy, 220, 132, "none", GREY, 1.4, 0)
    s += rect(clx + 40, gy + 30, 90, 70, "#dfe7f5", "#7d93c4", 1.4)
    s += rect(clx + 150, gy + 60, 110, 80, "#f3e0e0", "#caa24a", 1.4, 0)
    s += rect(clx + 150, gy + 60, 70, 72, "#fdeceb", RED, 1.6)
    s += line(clx + 220, gy, clx + 220, gy + 132, RED, 2)
    s += text(clx + 110, gy + 150, "що за межею вікна — відрізають, не малюють", 10, GREY, "middle")
    s += text(W / 2, 312, "Косі лінії й кола неминуче «сходять сходами»; згладжування підмішує сірого по краях. А все за межами екрана чи вікна — відсікають заздалегідь.",
              10.5, GREY, "middle", style="italic")
    save("fig-13-2-3-6-alias-clip.svg", s)


if __name__ == "__main__":
    fig_fb_memory_screen()
    fig_fb_addressing()
    fig_fb_size()
    fig_fb_drawing()
    fig_fb_packing()
    fig_fb_vs_sram()
    # Історія до теми 13.2.1 — Alto
    fig_alto_char_vs_bitmap()
    fig_alto_bitblt()
    # Тема 13.2.2 — колір у пам'яті
    fig_direct_vs_indexed()
    fig_rgb565_layout()
    fig_bpp_tradeoff()
    fig_palette()
    fig_alpha_blend()
    fig_byte_order()
    # Тема 13.2.3 — примітиви
    fig_rasterization()
    fig_rect_spans()
    fig_line_raster()
    fig_circle_symmetry()
    fig_text_glyphs()
    fig_alias_clip()
    print("done.")
