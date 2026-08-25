# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLACK = "#111111"
WHITE = "#ffffff"


def marker_grid(x, y, cell, bits, border=1):
    """Намалювати мітку: сітка GxG клітинок; bits — матриця 0/1 ДЛЯ ВНУТРІШНЬОЇ частини.
    Зовнішнє кільце (border клітинок) чорне. Повертає SVG-рядок."""
    g = len(bits) + 2 * border
    out = []
    for r in range(g):
        for c in range(g):
            # рамка?
            if r < border or r >= g - border or c < border or c >= g - border:
                fill = BLACK
            else:
                fill = WHITE if bits[r - border][c - border] else BLACK
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                       'stroke="#cccccc" stroke-width="0.5"/>'
                       % (x + c * cell, y + r * cell, cell, cell, fill))
    # зовнішня рамка контуру
    out.append(rect(x, y, g * cell, g * cell, fill="none", stroke=INK, sw=1.5, rx=0))
    return "".join(out), g * cell


# ── ФІГУРА 1: анатомія мітки + ідея словника (відстань Геммінга) ───────────────
def fig_anatomy():
    W, H = 860, 470
    p = []

    # ── ЛІВО: одна мітка 6×6 з підписами рамка/дані ──
    bits_a = [[1, 0, 1, 0],
              [0, 1, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 1]]
    mx, my, cell = 155, 120, 40
    g_svg, side = marker_grid(mx, my, cell, bits_a, border=1)
    p.append(g_svg)
    p.append(text(mx + side / 2, my - 24, "мітка 6×6", size=14, bold=True))

    # підпис рамки (стрілка до зовнішнього кільця)
    p.append(arrow(mx - 12, my + cell / 2, mx + cell * 0.5, my + cell / 2, color=INK, sw=1.6))
    b, bw, bh = textbox(mx - 62, my + cell / 2, "рамка\n(чорна)", size=12, bold=True,
                        fill="#fdecea", stroke=POS)
    p.append(b)
    # підпис даних (стрілка до центру)
    ccx, ccy = mx + side / 2, my + side / 2
    p.append(arrow(ccx + side / 2 + 12, ccy, ccx + cell, ccy, color=INK, sw=1.6))
    b, bw, bh = textbox(ccx + side / 2 + 78, ccy, "дані\n4×4 біти", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    p.append(b)
    p.append(text(mx + side / 2, my + side + 34, "чорний = 0 · білий = 1", size=12, color=MUTED))

    # ── ПРАВО: три коди словника + попарна відстань Геммінга ──
    rx0 = 540
    p.append(text(rx0 + 130, 60, "у словнику — лише далекі один від одного коди", size=13, bold=True))

    # три маленькі мітки, свідомо різні
    codes = [
        [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]],   # A
        [[0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]],   # B
        [[1, 1, 0, 0], [0, 0, 1, 1], [0, 1, 1, 0], [1, 0, 0, 1]],   # C
    ]
    labels = ["ID №7", "ID №12", "ID №20"]
    scell = 15
    ys = 95
    xs_list = [rx0, rx0 + 105, rx0 + 210]
    for xs, cc, lab in zip(xs_list, codes, labels):
        gsvg, sd = marker_grid(xs, ys, scell, cc, border=1)
        p.append(gsvg)
        p.append(text(xs + sd / 2, ys + sd + 18, lab, size=12, bold=True))

    # шкала відстані Геммінга між сусідами
    barY = 250
    p.append(text(rx0 + 130, barY - 4, "відстань між сусідніми кодами велика →", size=12, color=MUTED))
    p.append(line(rx0 + 20, barY + 18, rx0 + 250, barY + 18, color=FIELD, sw=6))
    p.append(text(rx0 + 130, barY + 40, "Δ = 9 бітів різні", size=13, bold=True, color=FIELD))

    # нижче — приклад виправлення
    ey = 320
    p.append(fitbox(rx0 - 10, ey, 300, 120,
                    "камера прочитала з помилкою:\n2 біти перевернуто відблиском\n\n"
                    "зіпсований код усе одно БЛИЖЧИЙ\nдо свого ID №7 (Δ=2), ніж\n"
                    "до будь-якого чужого (Δ≥7)\n→ виправлено правильно",
                    size=11.5, fill="#eafaf0", stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, "marker-anatomy.svg"), W, H, *p)


# ── ФІГУРА 2: конвеєр детектора (5 кроків) ────────────────────────────────────
def fig_pipeline():
    W, H = 900, 430
    p = []
    p.append(text(W / 2, 30, "конвеєр розпізнавання мітки", size=16, bold=True))

    steps = [
        ("1", "у сіре +\nпоріг", "чорно-біле:\nчисті плями"),
        ("2", "знайти\nчотирикутники", "лишити тільки\nопуклі квадрати"),
        ("3", "розпрямити\nперспективу", "косий → рівний\nквадрат «в лоб»"),
        ("4", "прочитати\nсітку бітів", "клітинки →\n0 / 1 (код)"),
        ("5", "звірити зі\nсловником", "виправити або\nвідкинути"),
    ]
    n = len(steps)
    boxW, boxH = 132, 118
    gap = (W - 40 - n * boxW) / (n - 1)
    y = 90
    cx_list = []
    for i, (num, title, sub) in enumerate(steps):
        x = 20 + i * (boxW + gap)
        cx_list.append(x + boxW / 2)
        # номер-кружок
        p.append(circle(x + 18, y - 14, 14, fill="#eef2ff", stroke=NEG, sw=2))
        p.append(text(x + 18, y - 9, num, size=15, bold=True, color=NEG))
        # рамка кроку
        p.append(rect(x, y, boxW, boxH, fill=FILL, stroke=INK, sw=1.6))
        p.append(mtext(x + boxW / 2, y + 34, title, size=14, bold=True))
        p.append(line(x + 12, y + 58, x + boxW - 12, y + 58, color="#dddde3", sw=1))
        p.append(mtext(x + boxW / 2, y + 80, sub, size=11.5, color=MUTED))
        # стрілка до наступного
        if i < n - 1:
            ax = x + boxW
            p.append(arrow(ax + 4, y + boxH / 2, ax + gap - 4, y + boxH / 2, color=INK, sw=2))

    # нижня стрічка-результат
    ry = y + boxH + 46
    b, bw, bh = textbox(W / 2, ry,
                        "на виході: ID мітки  +  чотири кути (субпіксельно)  →  поза 6 DoF",
                        size=13.5, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(b)
    # стрілка від останнього кроку вниз до стрічки
    p.append(arrow(cx_list[-1], y + boxH + 4, cx_list[-1], ry - bh / 2 - 4, color=FIELD, sw=2))

    render(os.path.join(OUT, "detect-pipeline.svg"), W, H, *p)


# ── ФІГУРА 3: ArUco проти AprilTag ────────────────────────────────────────────
def fig_compare():
    W, H = 880, 470
    p = []
    p.append(text(W / 2, 30, "ArUco  vs  AprilTag — спільне коріння, різні акценти", size=15.5, bold=True))

    colW = 380
    y = 60
    # ── ЛІВО: ArUco ──
    lx = 30
    p.append(rect(lx, y, colW, 300, fill="#eef2ff", stroke=NEG, sw=1.8))
    p.append(text(lx + colW / 2, y + 30, "ArUco", size=18, bold=True, color=NEG))
    aruco_lines = [
        "Університет Кордови (Іспанія), 2014",
        "Гаррідо-Хурадо та ін.",
        "вбудований у OpenCV (модуль aruco)",
        "словники генеруються під замовлення",
        "(потрібна кількість + завадостійкість)",
        "найпростіший старт: AR, калібрування,",
        "посадка дрона",
    ]
    for i, ln in enumerate(aruco_lines):
        bold = i in (2, 3)
        p.append(text(lx + colW / 2, y + 66 + i * 30, ln, size=12.5,
                      bold=bold, color=(INK if not bold else NEG)))

    # ── ПРАВО: AprilTag ──
    rx = W - 30 - colW
    p.append(rect(rx, y, colW, 300, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(rx + colW / 2, y + 30, "AprilTag", size=18, bold=True, color=FIELD))
    april_lines = [
        "лабораторія APRIL, Мічиган, 2011",
        "Едвін Олсон (v2 — Ван і Олсон, 2016)",
        "наголос на дальності та стійкості",
        "до розмиття, перекриття, спотворень",
        "детектор трохи важчий",
        "вибір дослідницької робототехніки",
        "",
    ]
    for i, ln in enumerate(april_lines):
        bold = i in (2, 3)
        p.append(text(rx + colW / 2, y + 66 + i * 30, ln, size=12.5,
                      bold=bold, color=(INK if not bold else "#1e8449")))

    # ── НИЗ: спільна основа ──
    by = y + 300 + 24
    b, bw, bh = textbox(W / 2, by,
                        "спільна механіка: квадрат · рамка · сітка бітів · словник із гемінговим захистом",
                        size=13, bold=True, fill=FILL, stroke=INK, sw=1.5)
    p.append(b)
    b2, bw2, bh2 = textbox(W / 2, by + 48,
                           "обидві виросли з ARTag (Марк Фіала, 2005) — перше цифрове виправлення помилок",
                           size=12, fill="#fdf6e3", stroke=MUTED, sw=1.3)
    p.append(b2)

    render(os.path.join(OUT, "aruco-vs-apriltag.svg"), W, H, *p)


# ── ФІГУРА 4: карта декодера (проєкт-вставка) ─────────────────────────────────
def fig_decode_map():
    W, H = 940, 560
    p = []
    p.append(text(W / 2, 30, "декодування ArUco: кроки, гомографія, пастки", size=16, bold=True))

    # ── ЛІВО: 5 кроків вертикальною стрічкою з функціями ──
    steps = [
        ("1", "адаптивний поріг", "adaptive_threshold()"),
        ("2", "контури → квадрати", "approx_quad()"),
        ("3", "гомографія 4 кутів", "homography_to_square()"),
        ("4", "прочитати сітку бітів", "read_grid()"),
        ("5", "звірка: 4 оберти + Гемінг", "identify()"),
    ]
    lx, ly = 30, 70
    bw, bh, vgap = 250, 52, 18
    ccx = lx + bw / 2
    for i, (num, ttl, fn) in enumerate(steps):
        y = ly + i * (bh + vgap)
        p.append(circle(lx + 16, y + bh / 2, 13, fill="#eef2ff", stroke=NEG, sw=2))
        p.append(text(lx + 16, y + bh / 2 + 5, num, size=14, bold=True, color=NEG))
        p.append(rect(lx + 34, y, bw - 34, bh, fill=FILL, stroke=INK, sw=1.5))
        p.append(text(lx + 34 + (bw - 34) / 2, y + 22, ttl, size=12.5, bold=True))
        p.append(text(lx + 34 + (bw - 34) / 2, y + 40, fn, size=11, color=NEG))
        if i < len(steps) - 1:
            p.append(arrow(ccx + 20, y + bh + 2, ccx + 20, y + bh + vgap - 2, color=INK, sw=1.8))

    # ── ПРАВО-ВГОРІ: гомографія — 4 кути → канонічний квадрат ──
    rx = 340
    p.append(text(rx + 275, 60, "гомографія: 4 кути → канонічний квадрат", size=13, bold=True))
    # перекошений чотирикутник (кандидат)
    quad = [(rx + 30, 100), (rx + 150, 82), (rx + 175, 205), (rx + 20, 190)]
    dline = "".join(
        line(quad[i][0], quad[i][1], quad[(i + 1) % 4][0], quad[(i + 1) % 4][1], color=POS, sw=2)
        for i in range(4))
    p.append(dline)
    for i, (qx, qy) in enumerate(quad):
        p.append(circle(qx, qy, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(rx + 95, 225, "кандидат (перекошений)", size=11, color=MUTED))
    # стрілка H
    p.append(arrow(rx + 195, 150, rx + 265, 150, color=INK, sw=2))
    p.append(text(rx + 230, 140, "H", size=15, bold=True, italic=True))
    # рівний квадрат
    sq = rx + 285
    for gy in range(6):
        for gx in range(6):
            fill = BLACK if (gx == 0 or gy == 0 or gx == 5 or gy == 5) else \
                   (WHITE if (gx + gy) % 2 else BLACK)
            p.append('<rect x="%.1f" y="%.1f" width="18" height="18" fill="%s" stroke="#cccccc" stroke-width="0.4"/>'
                     % (sq + gx * 18, 92 + gy * 18, fill))
    p.append(text(sq + 54, 225, "квадрат «в лоб»", size=11, color=MUTED))

    # рівняння під гомографією (два рядки, щоб шрифт лишався ≥ 8px)
    p.append(fitbox(rx, 240, 570, 62,
                    "4 кути → 8 рівнянь на 8 невідомих H (h₈=1): точний розв'язок 8×8 (Гаусс).\n"
                    "читаємо ОБЕРНЕНОЮ H прямо з кадру — без буфера розпрямлення.",
                    size=12, fill="#eef2ff", stroke=NEG, sw=1.4))

    # ── НИЗ: три пастки + запобіжник ──
    py = 320
    p.append(text(W / 2, py + 4, "три пастки — і рядок коду проти кожної", size=13.5, bold=True))
    traps = [
        ("хибний ID під шумом", "поріг виправлення max_correct\n(консервативний): задалеко → −1",
         "#fdecea", POS),
        ("«попливлі» межі клітинок", "відступ IGN=0.13 від краю:\nусереднюємо лише серединку",
         "#fff7e6", "#b8860b"),
        ("стрибки пози на 90°", "циклічний зсув кутів під rot:\ncorner[i]=quad[(i+rot)&3]",
         "#eafaf0", FIELD),
    ]
    tw = 290
    tgap = (W - 40 - 3 * tw) / 2
    for i, (bad, fix, bg, col) in enumerate(traps):
        x = 20 + i * (tw + tgap)
        p.append(rect(x, py + 20, tw, 150, fill=BG, stroke=col, sw=1.8))
        p.append(text(x + tw / 2, py + 46, "⚠ " + bad, size=12.5, bold=True, color=col))
        p.append(line(x + 16, py + 58, x + tw - 16, py + 58, color="#dddde3", sw=1))
        p.append(mtext(x + tw / 2, py + 82, fix, size=11.5, color=INK))
        # маленький підпис-запобіжник
        p.append(rect(x + 20, py + 120, tw - 40, 34, fill=bg, stroke=col, sw=1.2))
        p.append(text(x + tw / 2, py + 141, "запобіжник у коді", size=11, bold=True, color=col))

    render(os.path.join(OUT, "decode-map.svg"), W, H, *p)


if __name__ == "__main__":
    fig_anatomy()
    fig_pipeline()
    fig_compare()
    fig_decode_map()
    print("figs done")
