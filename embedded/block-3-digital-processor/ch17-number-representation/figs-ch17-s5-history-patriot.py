# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до §3.4.5 (Розділ 17, Модуль 3):
«Patriot у Дахрані (1991): 0.1 секунди, якої немає у двійковій системі».

Окремий скрипт (AUTHORING §9): головний figs.py розділу не чіпаємо, вивід → ./img/.
Спільні допоміжні функції скопійовано з figs.py, щоб тримати єдиний вигляд.
Підписи фігур — за темою: «Рис. 3.4.5i.k» (історія до теми 3.4.5).
Чистий Python, без сторонніх залежностей.
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.4.5i.1 — як 1/10 «не вміщується» у 24 двійкові розряди ───────────
def fig_chop():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 36, "Корінь біди: 0.1 не записати точно у двійковій", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "годинник лічить десяті частки секунди; щоб дістати секунди, число множать на 1/10 — а 1/10 у двійковій нескінченне",
              12.5, GREY, "middle", style="italic")

    # десяткова сторона
    s += text(150, 104, "У десятковій — рівно:", 15, INK, "middle", "bold")
    s += rect(40, 120, 220, 46, "#f4f7ff", BLUE, 2, 6)
    s += text(150, 149, "1/10 = 0.1", 22, BLUE, "middle", "bold")
    s += text(150, 188, "одна цифра — і кінець", 12.5, GREY, "middle", style="italic")

    # двійкова сторона — нескінченний періодичний дріб
    s += text(660, 104, "У двійковій — нескінченне (період 1001…):", 15, INK, "middle", "bold")
    s += rect(360, 120, 600, 46, "#fff5f5", RED, 2, 6)
    s += text(660, 149, "0.0 0011 0011 0011 0011 …", 20, RED, "middle", "bold")
    s += text(660, 188, "група «0011» повторюється довіку — як 1/3 = 0.333… у десятковій", 12.5, GREY, "middle", style="italic")

    # реальна сітка: 24 біти після коми, далі обрив
    gy = 250
    s += text(W / 2, gy - 18, "Регістр Patriot тримав лише 24 розряди після коми — решту «відрубали»:", 14.5, INK, "middle", "bold")
    bits = "00011001100110011001100"  # 23 значущих після першого 0 -> показуємо 24 комірки
    full = "0" + bits  # 24 біти після коми
    n = 24
    cw = 30
    x0 = (W - n * cw) / 2
    for i, b in enumerate(full):
        x = x0 + i * cw
        col = RED if b == "1" else BLUE
        s += rect(x, gy, cw - 3, 34, "#fff", col, 1.8, 3)
        s += text(x + (cw - 3) / 2, gy + 23, b, 15, col, "middle", "bold")
    # межа обриву
    cutx = x0 + n * cw + 4
    s += line(cutx, gy - 8, cutx, gy + 42, RED, 2.6, "5 4")
    s += text(cutx + 8, gy + 16, "тут обрив", 13, RED, "start", "bold")
    s += text(cutx + 8, gy + 33, "усе далі — втрачено", 11.5, GREY, "start", style="italic")
    s += text(W / 2, gy + 64, "збережене 24-бітне значення ≈ 0.0999999046  (трохи МЕНШЕ за справжню 0.1)", 14, INK, "middle", "bold")

    # величина похибки одного кроку
    ey = gy + 110
    s += rect(W / 2 - 330, ey, 660, 96, "#fbf7ee", AMBER, 2, 8)
    s += text(W / 2, ey + 28, "Похибка на КОЖНІЙ десятій секунди:", 15, INK, "middle", "bold")
    s += text(W / 2, ey + 56, "0.1 − 0.0999999046  ≈  0.0000000954  с  (≈ 9.5 · 10⁻⁸)", 16.5, RED, "middle", "bold")
    s += text(W / 2, ey + 82, "крихітна — та вона накопичується щотика, годинами поспіль (див. Рис. 3.4.5i.2)", 12.5, GREY, "middle", style="italic")
    save("fig-17-5i-1-chop.svg", s)


# ── Рис. 3.4.5i.2 — як крихітна похибка накопичується за годинами роботи ────
def fig_drift():
    W, H = 900, 540
    s = header(W, H)
    s += text(W / 2, 36, "Чому фатальним став час РОБОТИ, а не сам дріб", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "похибка лінійно росте з кількістю тиків від увімкнення: чим довше батарея не перезавантажувалась, тим гірше",
              12.5, GREY, "middle", style="italic")

    # осі
    ox, oy = 110, 420          # початок координат
    ax, ay = 830, 120          # кінці осей
    s += arrow(ox, oy, ax + 6, oy, INK, 2.4)       # вісь X
    s += arrow(ox, oy, ox, ay - 6, INK, 2.4)       # вісь Y
    s += text(ax + 2, oy + 30, "час роботи, год", 13, INK, "end")
    s += text(ox - 8, ay - 8, "похибка часу, с", 13, INK, "end")

    Hmax = 120.0               # годин на осі X
    Emax = 0.40                # секунд на осі Y
    # коефіцієнт: ~0.34 с за 100 год  →  0.0034 с/год
    k = 0.34 / 100.0

    def X(h):
        return ox + (ax - ox) * (h / Hmax)

    def Y(e):
        return oy - (oy - ay) * (e / Emax)

    # сітка X
    for h in range(0, 121, 20):
        gx = X(h)
        s += line(gx, oy, gx, oy + 5, GREY, 1.6)
        s += text(gx, oy + 22, str(h), 12, GREY, "middle")
    # сітка Y
    for e10 in range(0, 5):
        e = e10 * 0.1
        gy = Y(e)
        s += line(ox - 5, gy, ox, gy, GREY, 1.6)
        s += text(ox - 10, gy + 4, f"{e:.1f}", 12, GREY, "end")

    # пряма похибки
    s += line(X(0), Y(0), X(Hmax), Y(k * Hmax), RED, 3)

    # допустима межа (півкомірки range gate ~ еквівалент похибки, де ще ловиться ціль)
    # позначимо орієнтовний поріг «втрати цілі»
    thr = 0.10  # умовний поріг для ілюстрації порядку
    s += line(ox, Y(thr), ax, Y(thr), GREEN, 2, "6 5")
    s += text(ax, Y(thr) - 8, "орієнтовний поріг надійного захоплення", 11.5, GREEN, "end", style="italic")

    # маркер 8 год (ізраїльське попередження)
    h8 = 8
    s += circle(X(h8), Y(k * h8), 5, "#fff", AMBER, 2.4)
    s += line(X(h8), Y(k * h8), X(h8) + 60, Y(k * h8) - 70, GREY, 1.6, "3 3")
    s += text(X(h8) + 64, Y(k * h8) - 80, "8 год: ізраїльтяни помітили", 12, AMBER, "start", "bold")
    s += text(X(h8) + 64, Y(k * h8) - 64, "помітну втрату точності (11.02.1991)", 11.5, GREY, "start", style="italic")

    # маркер 100 год (момент трагедії)
    h100 = 100
    s += circle(X(h100), Y(k * h100), 6.5, "#fff", RED, 3)
    s += circle(X(h100), Y(k * h100), 3, RED, RED, 1)
    s += line(X(h100), Y(k * h100), X(h100) - 30, Y(k * h100) - 95, RED, 1.8, "3 3")
    s += text(X(h100) - 28, Y(k * h100) - 108, "≈100 год роботи →", 13, RED, "start", "bold")
    s += text(X(h100) - 28, Y(k * h100) - 92, "похибка ≈ 0.34 с", 13, RED, "start", "bold")

    # підпис під трагедійною точкою — на що це перетворюється у відстані
    s += rect(W / 2 - 300, H - 70, 600, 50, "#fff5f5", RED, 1.8, 8)
    s += text(W / 2, H - 50, "0.34 с × швидкість Scud (≈1676 м/с) ≈ 570 м зміщення", 14.5, RED, "middle", "bold")
    s += text(W / 2, H - 32, "більш ніж півкілометра — далеко за межами «вікна», де система шукала ціль", 12, GREY, "middle", style="italic")
    save("fig-17-5i-2-drift.svg", s)


# ── Рис. 3.4.5i.3 — зміщене «вікно дальності» (range gate) ──────────────────
def fig_rangegate():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 36, "Наслідок: «вікно дальності» з'їхало повз ціль", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "за першим відбиттям радар прогнозує, ДЕ ракета буде далі (швидкість × час), і дивиться лише у вузьке вікно навколо прогнозу",
              12.5, GREY, "middle", style="italic")

    # траєкторія Scud (зліва направо, вниз)
    ty = 150
    s += text(70, ty - 18, "напрямок руху Scud", 12.5, INK, "start", "bold")
    s += arrow(70, ty, 830, ty + 120, GREY, 2.2)

    # перше виявлення (правильне)
    d1x, d1y = 230, ty + 17
    s += circle(d1x, d1y, 7, GREEN, GREEN, 1)
    s += text(d1x, d1y - 16, "1) перше виявлення", 12.5, GREEN, "middle", "bold")
    s += text(d1x, d1y + 26, "тут радар реально побачив ціль", 11, GREY, "middle", style="italic")

    # справжнє наступне положення
    truex, truey = 560, ty + 70
    s += circle(truex, truey, 9, "#fff", RED, 3)
    s += circle(truex, truey, 3.5, RED, RED, 1)
    s += text(truex, truey + 30, "2) де Scud НАСПРАВДІ", 12.5, RED, "middle", "bold")

    # прогнозоване (зі зміщенням через похибку часу) — зсунуте вперед по траєкторії
    predx, predy = 720, ty + 95
    # вікно навколо прогнозу
    gw, gh = 96, 70
    s += rect(predx - gw / 2, predy - gh / 2, gw, gh, "none", BLUE, 2.4, 8)
    s += text(predx, predy - gh / 2 - 10, "вікно дальності (range gate)", 12.5, BLUE, "middle", "bold")
    s += text(predx, predy + gh / 2 + 18, "система дивиться ЛИШЕ сюди", 11, BLUE, "middle", style="italic")
    s += circle(predx, predy, 4, BLUE, BLUE, 1)
    s += text(predx, predy + 4, "", 1)

    # стрілка-промах: справжнє положення поза вікном
    s += line(truex, truey, predx - gw / 2, predy, RED, 1.8, "5 4")
    midx = (truex + predx - gw / 2) / 2
    s += text(midx, (truey + predy) / 2 - 8, "≈ 570 м", 13, RED, "middle", "bold")
    s += text(midx, (truey + predy) / 2 + 9, "розрив", 11, GREY, "middle", style="italic")

    # підсумкова рамка
    by = 360
    s += rect(70, by, 760, 84, "#fbf7ee", AMBER, 1.8, 8)
    s += text(90, by + 26, "Похибка часу зсунула прогноз уперед по траєкторії — справжня ціль опинилася ПОЗА вікном.", 13.5, INK, "start", "bold")
    s += text(90, by + 50, "Радар «не побачив» цілі там, де шукав, вирішив, що тривоги нема, і перехоплення не відбулося.", 13, INK, "start")
    s += text(90, by + 71, "Парадокс: що ДОВШЕ й «надійніше» працювала батарея без перезапуску, то більший зсув — і то сліпіша вона ставала.", 12, GREY, "start", style="italic")
    save("fig-17-5i-3-rangegate.svg", s)


# ── Рис. 3.4.5i.4 — пастка часткового виправлення: похибки не скоротились ───
def fig_partialfix():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 36, "Чому навіть «частина виправлень» не врятувала", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "однакова похибка в ОБОХ місцях скоротилась би при відніманні часів; виправили ж її лише в одному — і вони перестали гаситись",
              12.5, GREY, "middle", style="italic")

    colw = 410
    lx, rx = 40, 470
    cy = 92
    ch = 320

    # ЛІВА колонка: однаково «криво» в обох місцях → скорочується
    s += rect(lx, cy, colw, ch, "#f3faf4", GREEN, 2, 10)
    s += text(lx + colw / 2, cy + 28, "Якби похибка була ОДНАКОВА скрізь", 15, GREEN, "middle", "bold")
    s += text(lx + colw / 2, cy + 50, "(стара версія коду в усіх викликах)", 11.5, GREY, "middle", style="italic")
    s += rect(lx + 30, cy + 70, colw - 60, 40, "#fff", INK, 1.6, 6)
    s += text(lx + colw / 2, cy + 95, "t₁ = (крива 0.1) × n₁", 14, INK, "middle")
    s += rect(lx + 30, cy + 120, colw - 60, 40, "#fff", INK, 1.6, 6)
    s += text(lx + colw / 2, cy + 145, "t₂ = (крива 0.1) × n₂", 14, INK, "middle")
    s += text(lx + colw / 2, cy + 188, "Δt = t₂ − t₁", 15, INK, "middle", "bold")
    s += rect(lx + 30, cy + 206, colw - 60, 56, "#eefaf0", GREEN, 2, 8)
    s += text(lx + colw / 2, cy + 230, "однакова «кривизна» зникає при відніманні", 12.5, GREEN, "middle", "bold")
    s += text(lx + colw / 2, cy + 250, "→ інтервал Δt вийшов би майже точним", 12.5, INK, "middle")

    # ПРАВА колонка: виправили лише одне місце → НЕ скорочується
    s += rect(rx, cy, colw, ch, "#fff5f5", RED, 2, 10)
    s += text(rx + colw / 2, cy + 28, "Що сталося НАСПРАВДІ", 15, RED, "middle", "bold")
    s += text(rx + colw / 2, cy + 50, "оновлення внесли в одну частину коду, не в усі", 11.5, GREY, "middle", style="italic")
    s += rect(rx + 30, cy + 70, colw - 60, 40, "#fff", GREEN, 1.8, 6)
    s += text(rx + colw / 2, cy + 95, "t₁ = (точна 0.1) × n₁", 14, GREEN, "middle", "bold")
    s += rect(rx + 30, cy + 120, colw - 60, 40, "#fff", RED, 1.8, 6)
    s += text(rx + colw / 2, cy + 145, "t₂ = (крива 0.1) × n₂", 14, RED, "middle", "bold")
    s += text(rx + colw / 2, cy + 188, "Δt = t₂ − t₁", 15, INK, "middle", "bold")
    s += rect(rx + 30, cy + 206, colw - 60, 56, "#fdecec", RED, 2, 8)
    s += text(rx + colw / 2, cy + 230, "різні «кривизни» вже не гасять одна одну", 12.5, RED, "middle", "bold")
    s += text(rx + colw / 2, cy + 250, "→ повний зсув ≈ 0.34 с лишився", 12.5, RED, "middle")

    # мораль
    s += text(W / 2, H - 24, "Урок: половинчасте виправлення буває гіршим за жодного — воно ламає симетрію, що досі рятувала.",
              13, INK, "middle", "bold")
    save("fig-17-5i-4-partialfix.svg", s)


if __name__ == "__main__":
    fig_chop()
    fig_drift()
    fig_rangegate()
    fig_partialfix()
    print("OK: 4 figures")
