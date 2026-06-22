# -*- coding: utf-8 -*-
"""Фігури до теми «Демозаїка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори фільтрів понад палітру svgkit (насичені, як на сенсорі)
R = "#cc2c20"      # червоний фільтр
G = "#1f9d4d"      # зелений фільтр
B = "#2457d6"      # синій фільтр (= NEG)
GRAY = "#9aa0a6"   # «лише яскравість», без кольору
PURPLE = "#7c3aed" # повний колір (R+G+B зведені)


def cell(x, y, s, color, label=None, lsize=12, lcolor="#ffffff"):
    """Кольорова клітинка фільтра з опційною літерою всередині."""
    out = rect(x, y, s, s, fill=color, stroke=BG, sw=1.4, rx=4)
    if label:
        out += text(x + s / 2, y + s / 2 + lsize * 0.36, label, size=lsize,
                    color=lcolor, bold=True)
    return out


# ── 1. Піксель сліпий до кольору → дамо йому скельце ──────────────────────────
# Ідея: сам піксель лічить усі фотони (лише яскравість, сірий); кольорове
# скельце згори пропускає тільки свою смугу — і піксель починає міряти колір.
def fig_colorblind():
    W, H = 720, 360
    f = [text(W / 2, 28, "Колір додає фільтр, не сам піксель", size=16, bold=True)]

    # ЛІВОРУЧ: без фільтра — усе світло, на виході лише яскравість (сіра)
    f.append(text(180, 70, "БЕЗ фільтра", size=13, color=MUTED, bold=True))
    for dx, c in ((-26, R), (0, G), (26, B)):
        f.append(arrow(180 + dx, 92, 180 + dx * 0.7, 132, color=c, sw=2.0))
    f.append(rect(140, 134, 80, 56, fill=GRAY, stroke=INK, sw=1.8, rx=4))
    f.append(text(180, 166, "усе світло", size=10.5, color="#ffffff", bold=True))
    f.append(rect(140, 206, 80, 40, fill=GRAY, stroke=INK, sw=1.6, rx=4))
    f.append(text(180, 224, "яскравість", size=10, color="#ffffff", bold=True))
    f.append(text(180, 239, "(колір ?)", size=9, color="#ffffff"))
    f.append(arrow(180, 192, 180, 204, color=INK, sw=1.6))

    # ПРАВОРУЧ: три пікселі, кожен зі своїм скельцем
    f.append(text(500, 70, "ЗІ скельцем", size=13, color=MUTED, bold=True))
    cols = ((400, R, "R", "червоне"), (500, G, "G", "зелене"), (600, B, "B", "синє"))
    for cx, c, lab, word in cols:
        # три промені падають, фільтр пропускає лише свій
        for dx, cc in ((-22, R), (0, G), (22, B)):
            faded = cc if cc == c else "#d7dbe0"
            f.append(line(cx + dx, 92, cx + dx * 0.6, 122, color=faded, sw=2.0,
                          dash=None if cc == c else "2,3"))
        f.append(rect(cx - 28, 122, 56, 16, fill=c, stroke=INK, sw=1.4, rx=3))   # скельце
        f.append(text(cx, 134, "скельце", size=9, color="#ffffff", bold=True))
        f.append(rect(cx - 26, 150, 52, 48, fill=GRAY, stroke=INK, sw=1.6, rx=4))  # піксель
        f.append(text(cx, 178, "піксель", size=9.5, color="#ffffff"))
        f.append(arrow(cx, 200, cx, 214, color=c, sw=1.8))
        f.append(rect(cx - 26, 216, 52, 30, fill=c, stroke=INK, sw=1.4, rx=4))
        f.append(text(cx, 235, lab, size=13, color="#ffffff", bold=True))

    f.append(text(W / 2, 300, "Без фільтра піксель ловить усе світло й знає лише яскравість.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 320, "Кольорове скельце згори пропускає тільки свою смугу — і кожен піксель міряє СВІЙ колір.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "colorblind.svg"), W, H, *f)


# ── 2. Баєрівська мозаїка RGGB ───────────────────────────────────────────────
# Ідея: повторюваний квадрат R G / G B по всій матриці; зеленого вдвічі більше,
# бо око бере з нього найбільше різкості (яскравість).
def fig_bayer():
    W, H = 720, 430
    f = [text(W / 2, 28, "Баєрівська мозаїка: квадрат R G / G B по всій сітці", size=16, bold=True)]

    s = 34
    nx, ny = 8, 6
    gx = (W - nx * s) / 2
    gy = 56
    # патерн RGGB: парний рядок R,G,R,G…; непарний G,B,G,B…
    for r in range(ny):
        for c in range(nx):
            if r % 2 == 0:
                col = R if c % 2 == 0 else G
            else:
                col = G if c % 2 == 0 else B
            f.append(cell(gx + c * s, gy + r * s, s, col))

    # виділити один квадрат 2×2 рамкою
    f.append(rect(gx - 2, gy - 2, 2 * s + 4, 2 * s + 4, fill="none", stroke=INK, sw=2.6, rx=3))
    f.append(text(gx + s, gy + 2 * s + 18, "квадрат 2×2", size=10, color=INK, bold=True, anchor="middle"))

    # пропорції під сіткою — три рядки-смуги
    by = gy + ny * s + 30
    f.append(text(W / 2, by, "Скільки кожного фільтра на сенсорі:", size=12, bold=True))
    bars = ((G, "зелений", 50, 220), (R, "червоний", 25, 110), (B, "синій", 25, 110))
    rowy = by + 14
    for col, lab, pct, wlen in bars:
        f.append(rect(180, rowy, wlen, 20, fill=col, stroke=INK, sw=1.2, rx=3))
        f.append(text(180 + wlen + 8, rowy + 14, "%s — %d%%" % (lab, pct), size=11,
                      color=INK, anchor="start"))
        rowy += 26

    f.append(text(W / 2, H - 26, "Зеленого вдвічі більше (50%): з нього око бере найбільше різкості — яскравість.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 10, "Червоного й синього по 25% — вони несуть тонший відтінок (колірність), до якого око м'якше.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "bayer-mosaic.svg"), W, H, *f)


# ── 3. Демозаїка: одна складова виміряна, дві — з сусідів ─────────────────────
# Ідея: червоний піксель знає лише R; зелене й синє інтерполюють із сусідів,
# щоб у кожній точці став повний R+G+B.
def fig_demosaic():
    W, H = 720, 360
    f = [text(W / 2, 28, "Демозаїка: одну складову виміряно, дві — з сусідів", size=16, bold=True)]

    s = 46
    gx, gy = 150, 70
    # сітка 3×3 з центром-червоним: рядки R,G,R / G,B,G / R,G,R
    grid = [[R, G, R], [G, B, G], [R, G, R]]
    for r in range(3):
        for c in range(3):
            f.append(cell(gx + c * s, gy + r * s, s, grid[r][c]))
    cx0 = gx + s + s / 2
    cy0 = gy + s + s / 2
    # рамка центру + підпис «лише R»
    f.append(rect(gx + s - 2, gy + s - 2, s + 4, s + 4, fill="none", stroke=INK, sw=2.8, rx=4))
    f.append(text(cx0, gy - 10, "цей піксель: лише R", size=11, color=R, bold=True))

    # стрілки від сусідів-зелених і сусідів-синіх до центру
    for dx, dy, col in ((0, -s, G), (-s, 0, G), (0, s, G), (s, 0, G)):
        f.append(line(cx0 + dx, cy0 + dy, cx0 + dx * 0.32, cy0 + dy * 0.32,
                      color=col, sw=1.8, dash="3,2"))
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        f.append(line(cx0 + dx, cy0 + dy, cx0 + dx * 0.32, cy0 + dy * 0.32,
                      color=B, sw=1.8, dash="3,2"))
    f.append(text(cx0, gy + 3 * s + 20, "позичає G і B у сусідів", size=10, color=MUTED))

    # стрілка «демозаїка» до картки повного кольору
    ax = gx + 3 * s + 12
    f.append(arrow(ax, cy0, ax + 56, cy0, color=INK, sw=2.0))
    f.append(text(ax + 28, cy0 - 10, "демозаїка", size=9.5, color=MUTED))
    bx = ax + 64
    f.append(rect(bx, cy0 - 52, 150, 104, fill=PURPLE, stroke=INK, sw=1.8, rx=6))
    f.append(text(bx + 75, cy0 - 30, "повний колір", size=12, color="#ffffff", bold=True))
    f.append(text(bx + 16, cy0 - 6, "R — виміряно", size=10.5, color="#ffffff", anchor="start"))
    f.append(text(bx + 16, cy0 + 14, "G — вгадано", size=10.5, color="#ffffff", anchor="start"))
    f.append(text(bx + 16, cy0 + 34, "B — вгадано", size=10.5, color="#ffffff", anchor="start"))

    f.append(text(W / 2, H - 26, "У сирій мозаїці кожна точка має лише одну складову; демозаїка інтерполює дві відсутні з сусідів.",
                  size=12, color=MUTED))
    f.append(text(W / 2, H - 10, "На виході — повноколірний кадр, де в кожному пікселі є R, G і B. Але дві з трьох — обчислена гадка.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "demosaic.svg"), W, H, *f)


# ── 4. Ціна: артефакти на тонких деталях + що таке RAW ───────────────────────
# Ідея: на чітких смужках інтерполяція схибить → несправжній колір, муар;
# RAW — це сира мозаїка до демозаїки (найбільше «чесних» даних).
def fig_artifacts():
    W, H = 720, 360
    f = [text(W / 2, 28, "Ціна вгадування: артефакти й нижча кольорова роздільність", size=16, bold=True)]

    # ЛІВОРУЧ: справжні чорно-білі смужки
    f.append(text(180, 64, "справжня деталь", size=12, color=INK, bold=True))
    f.append(text(180, 80, "(тонкі смужки)", size=10, color=MUTED))
    bx, by, bw, bh = 110, 92, 18, 110
    for i in range(8):
        col = INK if i % 2 == 0 else "#f0f1f3"
        f.append(rect(bx + i * bw, by, bw, bh, fill=col, stroke="none", sw=0))
    f.append(rect(bx, by, 8 * bw, bh, fill="none", stroke=INK, sw=1.4))

    # стрілка
    f.append(arrow(bx + 8 * bw + 8, by + bh / 2, bx + 8 * bw + 48, by + bh / 2, color=INK, sw=2.0))
    f.append(text(bx + 8 * bw + 28, by + bh / 2 - 10, "демозаїка", size=9.5, color=MUTED))

    # ПРАВОРУЧ: ті самі смужки беруться хибним кольором (муар / «застібка»)
    f.append(text(500, 64, "після демозаїки", size=12, color=INK, bold=True))
    f.append(text(500, 80, "(несправжній колір, муар)", size=10, color=MUTED))
    fx = bx + 8 * bw + 56
    fake = [INK, "#f0f1f3", R, "#f0f1f3", G, "#f0f1f3", B, "#f0f1f3"]
    for i in range(8):
        f.append(rect(fx + i * bw, by, bw, bh, fill=fake[i], stroke="none", sw=0))
    f.append(rect(fx, by, 8 * bw, bh, fill="none", stroke=INK, sw=1.4))
    f.append(text(fx + 4 * bw, by + bh + 18, "колір, якого в сцені не було", size=10,
                  color=POS, bold=True))

    # рамка про RAW (явні рядки, щоб шрифт лишився читабельним)
    ry = 248
    box = fitbox(80, ry, W - 160, 60,
                 "RAW — сира мозаїка ДО демозаїки: одна складова на піксель, найбільше «чесних» даних\n"
                 "(кадр ще треба «проявити»). JPEG із камери — уже ПІСЛЯ демозаїки й обробки.",
                 size=12, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    f.append(text(W / 2, H - 16, "«12 МП» = 6 млн зелених точок + по 3 млн червоних і синіх; решту кольору домальовано.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "artifacts.svg"), W, H, *f)


if __name__ == "__main__":
    fig_colorblind()
    fig_bayer()
    fig_demosaic()
    fig_artifacts()
    print("OK: 4 SVG у", IMG)
