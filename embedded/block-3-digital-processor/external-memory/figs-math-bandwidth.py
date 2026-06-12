# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🧮-вставки «Пропускна здатність пам'яті» (до §3.8.3, Модуль 3).
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів — з токеном "r08-s3m", щоб не конфліктувати з фігурами теми.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif; єдиний вигляд з рештою розділів.
Нумерація підписів у тексті — Рис. 3.8.3m.k (на диску імена не перенумеровуються).
Хелпери — копія зі спільного набору розділу (за §9 кожен скрипт самодостатній).
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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.8.3m.1 — формула пропускної здатності й «×2» наочно:
# зверху три множники (такт × ширина × 2), знизу — епюри тактового сигналу
# й шини даних, де SDR кладе слово на один фронт, а DDR — на обидва.
# ═══════════════════════════════════════════════════════════════════════════
def fig_formula():
    W, H = 920, 588
    s = header(W, H)
    s += text(W / 2, 34, "Пікова пропускна здатність = частота такту × ширина шини × 2",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "три незалежні множники; «×2» — це DDR: одне слово на КОЖЕН фронт такту, а не на один",
              12.5, GREY, "middle", style="italic")

    # ── три множники-блоки ──
    cols = [
        (185, RED, "частота такту", ["f, мегагерци", "(тактів за секунду)"],
         ["скільки разів на секунду", "шина «цокає»; межу ставить", "критичний шлях (§3.1.5)"]),
        (460, BLUE, "ширина шини", ["W, бітів за такт", "(скільки ліній даних)"],
         ["8 / 16 / 32 / 64 лінії", "паралельно; що ширша —", "то більше бітів за раз"]),
        (735, GREEN, "× 2  (DDR)", ["множник передач", "на такт"],
         ["SDR: 1 слово/такт", "DDR: 2 слова/такт —", "на обидва фронти"]),
    ]
    boxw, boxh = 240, 150
    by = 74
    for cx, col, head, mid, who in cols:
        bx = cx - boxw / 2
        s += rect(bx, by, boxw, boxh, "#ffffff", col, 2.4, 12)
        s += rect(bx, by, boxw, 34, col, col, 0, 12)
        s += rect(bx, by + 22, boxw, 12, col, col, 0, 0)
        s += text(cx, by + 23, head, 15.5, "#ffffff", "middle", "bold")
        yy = by + 56
        for ln in mid:
            s += text(cx, yy, ln, 12.5, INK, "middle"); yy += 18
        yy += 6
        s += line(bx + 16, yy - 6, bx + boxw - 16, yy - 6, FAINT, 1.4)
        for ln in who:
            s += text(bx + 16, yy + 10, ln, 11.5, GREY, "start"); yy += 16
    # знаки множення між блоками
    s += text(322, by + 84, "×", 26, INK, "middle", "bold")
    s += text(597, by + 84, "×", 26, INK, "middle", "bold")

    # ── приклад-рядок під блоками ──
    ey = 258
    s += rect(70, ey, W - 140, 30, "#f5f7fb", BLUE, 0, 6)
    s += mono(W / 2, ey + 20,
              "DDR4-3200, 64-бітний модуль:  1600 МГц × 64 біт × 2  =  3200 МТ/с × 8 байт  =  25.6 ГБ/с",
              13.5, INK, "middle", "bold")

    # ── епюри: SDR проти DDR ──
    base = 320
    s += text(80, base - 6, "Звідки береться «×2»: дані на фронтах такту", 14, INK, "start", "bold")

    clk_lo, clk_hi = 0, 0  # placeholders
    x0, x1 = 150, 860
    period = (x1 - x0) / 8.0  # 8 півперіодів = 4 повні такти

    def clock_row(yc, label, color):
        s_ = text(95, yc + 4, label, 12.5, color, "start", "bold")
        amp = 18
        pts = []
        x = x0
        hi = True
        # half-period square wave
        for i in range(8):
            ytop = yc - amp if hi else yc + amp
            pts.append((x, ytop))
            pts.append((x + period, ytop))
            x += period
            hi = not hi
        # connect vertical edges via polyline of (x,y) including verticals
        full = []
        x = x0
        hi = True
        for i in range(8):
            ylvl = yc - amp if hi else yc + amp
            full.append((x, ylvl))
            full.append((x + period, ylvl))
            hi = not hi
            x += period
        s_ += polyline(full, color, 2.2)
        return s_, amp

    # тактовий сигнал
    cy = base + 34
    row, amp = clock_row(cy, "CLK", INK)
    s += row
    # позначки фронтів: висхідні (зелені) й спадні (бурштинові) тонкі тики донизу
    rising = [x0 + period * k for k in (0, 2, 4, 6)]
    falling = [x0 + period * k for k in (1, 3, 5, 7)]
    for xr in rising:
        s += line(xr, cy - amp - 4, xr, cy + amp + 14, GREEN, 1.4, "2 2")
    for xf in falling:
        s += line(xf, cy - amp - 4, xf, cy + amp + 14, AMBER, 1.4, "2 2")
    s += text(x0 - 4, cy + amp + 30, "↑ висхідні фронти (зелені)", 10.5, GREEN, "start")
    s += text(x0 + period * 4 + 8, cy + amp + 30, "↓ спадні фронти — DDR ловить і їх (бурштинові)", 10.5, AMBER, "start")

    # шина SDR: слово лише на висхідних фронтах
    def data_eye(xc, w, yc, h, color, lbl):
        # «око» даних — паралелограм-комірка з підписом
        ss = path(f"M{xc - w/2:.1f},{yc:.1f} L{xc - w/2 + 8:.1f},{yc - h/2:.1f} "
                  f"L{xc + w/2 - 8:.1f},{yc - h/2:.1f} L{xc + w/2:.1f},{yc:.1f} "
                  f"L{xc + w/2 - 8:.1f},{yc + h/2:.1f} L{xc - w/2 + 8:.1f},{yc + h/2:.1f} Z",
                  "#ffffff", color, 1.8)
        ss += text(xc, yc + 4, lbl, 11, color, "middle", "bold")
        return ss

    sdr_y = cy + 108
    s += text(88, sdr_y + 4, "SDR", 12.5, BLUE, "start", "bold")
    s += text(88, sdr_y + 18, "шина", 9.5, GREY, "start")
    s += line(x0, sdr_y, x1, sdr_y, FAINT, 1.2)
    for k, xr in enumerate(rising):
        s += data_eye(xr, period * 0.9, sdr_y, 30, BLUE, f"D{k}")
    s += text(x1 + 6, sdr_y + 4, "4 слова", 11, BLUE, "start", "bold")

    # шина DDR: слово на кожному фронті (8 за ті самі 4 такти)
    ddr_y = cy + 168
    s += text(88, ddr_y + 4, "DDR", 12.5, GREEN, "start", "bold")
    s += text(88, ddr_y + 18, "шина", 9.5, GREY, "start")
    s += line(x0, ddr_y, x1, ddr_y, FAINT, 1.2)
    all_edges = sorted(rising + falling)
    for k, xe in enumerate(all_edges):
        s += data_eye(xe, period * 0.78, ddr_y, 30, GREEN, f"D{k}")
    s += text(x1 + 6, ddr_y + 4, "8 слів", 11, GREEN, "start", "bold")

    # підсумкова стрічка
    s += rect(70, H - 30, W - 140, 22, "#f2f8f4", GREEN, 0, 6)
    s += text(W / 2, H - 15,
              "За ті самі 4 такти DDR передає вдвічі більше слів — звідси «×2». Частоту такту це НЕ підвищує.",
              12, INK, "middle")
    save("fig-r08-s3m-1-formula.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.8.3m.2 — «водоспад»: чому стала (sustained) здатність нижча за пікову.
# Від 100% піку послідовно віднімаємо втрати: регенерація, відкриття рядка,
# CAS-латентність на випадковому доступі, накладні витрати команд.
# ═══════════════════════════════════════════════════════════════════════════
def fig_waterfall():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 34, "Пік — це стеля, якої майже не дістати: куди дівається пропускна здатність",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "формула дає ПІКОВЕ число; реальний (sustained) потік нижчий — і вузьке горло тут, а не в множниках",
              12.5, GREY, "middle", style="italic")

    # вісь
    ax, ay = 90, 90
    aw, ah = 560, 360
    s += line(ax, ay, ax, ay + ah, GREY, 1.6)
    s += line(ax, ay + ah, ax + aw, ay + ah, GREY, 1.6)
    # сітка %
    for p in range(0, 101, 20):
        yg = ay + ah * (1 - p / 100.0)
        s += line(ax - 5, yg, ax + aw, yg, FAINT, 1.0)
        s += text(ax - 10, yg + 4, f"{p}%", 11.5, GREY, "end")

    # каскад: (підпис, від%, до%, колір)
    steps = [
        ("піковий\nрозрахунок", 100, 100, BLUE),
        ("−регенерація\n(refresh)", 100, 96, AMBER),
        ("−відкриття\nрядка (RAS)", 96, 84, AMBER),
        ("−CAS-латентність\n(випадк. доступ)", 84, 62, RED),
        ("−накладні\nкоманди/шина", 62, 55, RED),
        ("реально\n(sustained)", 0, 55, GREEN),
    ]
    n = len(steps)
    bw = aw / (n + 0.6)
    gap = bw * 0.28
    prev_top = None
    for i, (lbl, frm, to, col) in enumerate(steps):
        xc = ax + bw * (i + 0.5) + gap * i
        bx = xc - bw / 2
        ytop = ay + ah * (1 - to / 100.0)
        if i == 0 or i == n - 1:
            # суцільний стовпець від 0 до to
            ybot = ay + ah
            s += rect(bx, ytop, bw, ybot - ytop, col, col, 0, 3)
            s += text(xc, ytop - 8, f"{to}%", 13, INK, "middle", "bold")
        else:
            # «плаваючий» сегмент втрати від frm до to
            ytop_f = ay + ah * (1 - frm / 100.0)
            seg_h = ytop - ytop_f
            s += rect(bx, ytop_f, bw, seg_h, col, col, 0, 3)
            s += text(xc, ytop_f - 6, f"−{frm - to}%", 12, col, "middle", "bold")
            # пунктир-з'єднувач від попередньої вершини
            if prev_top is not None:
                s += line(prev_top[0], prev_top[1], bx, ytop_f, GREY, 1.2, "4 3")
        # підпис під віссю (дворядковий)
        for j, part in enumerate(lbl.split("\n")):
            s += text(xc, ay + ah + 18 + j * 13, part, 10.5, INK, "middle")
        prev_top = (bx + bw, ytop)

    # дужка «втрати» праворуч від піку
    s += text(ax + 6, ay - 6, "↑ більше = краще", 10.5, GREY, "start", style="italic")

    # ── права колонка: словник причин ──
    rx = ax + aw + 40
    s += rect(rx, ay - 4, W - rx - 30, ah + 8, "#fbfbfb", FAINT, 1.4, 10)
    s += text(rx + 16, ay + 22, "Чому пік недосяжний", 14, INK, "start", "bold")
    notes = [
        (AMBER, "Регенерація.", ["рядки DRAM треба раз у раз", "освіжати — у цей час доступу", "до них нема (див. §3.8.2m)."]),
        (AMBER, "Відкриття рядка (RAS→CAS).", ["щоб прочитати комірку, банк", "спершу «відкриває» цілий рядок;", "це десятки нс простою."]),
        (RED, "Латентність ≠ пропускна.", ["широка труба, але з довгим", "стартом: перше слово йде", "довго, потік — лише далі."]),
        (RED, "Накладні витрати.", ["команди, перемикання банків,", "розвороти шини читання↔запис", "з'їдають частину тактів."]),
    ]
    yy = ay + 46
    for col, head, body in notes:
        s += circle(rx + 22, yy - 4, 5, col, col, 0)
        s += text(rx + 36, yy, head, 12, INK, "start", "bold")
        yy += 17
        for ln in body:
            s += text(rx + 36, yy, ln, 11, GREY, "start"); yy += 14
        yy += 9

    # висновок
    s += rect(ax, H - 34, aw, 24, "#fdf3f2", RED, 0, 6)
    s += text(ax + aw / 2, H - 18,
              "Вузьке горло — латентність і випадковий доступ, а не множники формули.",
              12, INK, "middle")
    save("fig-r08-s3m-2-waterfall.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.8.3m.3 — масштаб: ПК-модуль DDR4 проти варіантів пам'яті МК.
# Лог-смуги ГБ/с + колонка «де реальне горло»; внизу — кадр дисплея як приклад.
# ═══════════════════════════════════════════════════════════════════════════
def fig_scale():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Той самий закон, інший масштаб: чому в МК горло — сама шина",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пік = такт × ширина × множник; у ПК шина широка й швидка, у МК — вузька й послідовна",
              12.5, GREY, "middle", style="italic")

    # таблиця-смуги: (назва, колір, опис множників, ГБ/с)
    import math
    rows = [
        ("DDR4-3200, ПК-модуль", BLUE,  "64 біт × 1600 МГц × 2 (DDR)", 25.6),
        ("Паралельна SDR-SDRAM у МК", GREEN, "16 біт × 100 МГц × 1 (SDR)", 0.20),
        ("Octal-PSRAM (OPI), 8 ліній", AMBER, "8 біт × 100 МГц × 2 (DDR)", 0.20),
        ("Quad-SPI флеш/PSRAM, 4 лінії", RED,  "4 біт × 80 МГц × 1 (SDR)", 0.040),
    ]
    # лог-шкала від 0.02 до 32 ГБ/с
    lo, hi = 0.02, 32.0
    bx0 = 360
    bxmax = W - 70
    span = bxmax - bx0

    def xof(v):
        return bx0 + span * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    ty = 86
    rh = 70
    # сітка лог-поділок
    for gv in (0.02, 0.1, 1, 10, 32):
        xg = xof(gv)
        s += line(xg, ty - 6, xg, ty + rh * len(rows) + 4, FAINT, 1.0)
        lbl = (f"{gv:g} ГБ/с" if gv >= 1 else f"{int(gv*1000)} МБ/с")
        s += text(xg, ty - 12, lbl, 10.5, GREY, "middle")

    for i, (name, col, formula, gbs) in enumerate(rows):
        ry = ty + i * rh
        # підпис ліворуч
        s += text(56, ry + 22, name, 13.5, INK, "start", "bold")
        s += text(56, ry + 40, formula, 11, GREY, "start")
        # смуга (лог)
        xend = xof(gbs)
        s += rect(bx0, ry + 14, max(2.0, xend - bx0), 30, col, col, 0, 5)
        val = (f"{gbs:.1f} ГБ/с" if gbs >= 1 else f"{int(round(gbs*1000))} МБ/с")
        s += text(xend + 8, ry + 34, val, 12.5, INK, "start", "bold")

    # відношення-виноска
    s += text(bx0, ty + rh * len(rows) + 22,
              "Розрив із quad-SPI — сотні разів: 64 лінії проти 4 (×16), такт 1600 проти 80 МГц (×20), та ще ×2 за DDR.",
              11.5, INK, "start", style="italic")

    # ── нижній блок: приклад кадру дисплея ──
    yb = ty + rh * len(rows) + 44
    s += rect(50, yb, W - 100, 96, "#f7f9fc", BLUE, 1.6, 10)
    s += text(70, yb + 24, "Що це означає на практиці: кадр дисплея",
              13.5, INK, "start", "bold")
    s += mono(70, yb + 48, "кадр 320×240×2 байт = 153.6 КБ;  60 кадрів/с → 9.2 МБ/с потрібно",
              12, INK, "start")
    s += mono(70, yb + 70, "quad-SPI @ 40 МБ/с → стелі вистачає; 800×480 RGB @60 → 46 МБ/с → вже впритул",
              12, INK, "start")
    s += text(W - 70, yb + 70, "горло — шина, не формула", 11.5, RED, "end", "bold")

    save("fig-r08-s3m-3-scale.svg", s)


if __name__ == "__main__":
    fig_formula()
    fig_waterfall()
    fig_scale()
    print("r08-s3-m bandwidth figures done.")
