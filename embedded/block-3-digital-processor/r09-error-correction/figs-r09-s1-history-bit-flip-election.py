# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки §3.9.1i
«4096 зайвих голосів: перевернутий біт на виборах у Бельгії (2003)».
Розділ 3.9 «Коди виявлення й корекції помилок» (Модуль 3).
Чистий Python, без залежностей. Вивід → ./img/.
Головний figs.py розділу НЕ чіпаємо — це самодостатній скрипт.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — копія спільних,
щоб вигляд збігався з рештою розділів.

Нумерація підписів — за темою/вставкою: «Рис. 3.9.1i.k».
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = "Cascadia Mono, Consolas, monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.9.1i.1 — як зловили: неможливе число ════════════════════
def fig_caught():
    """Санітарна перевірка, що викрила збій: преференційні голоси одного
    кандидата перевищили підсумок усього списку — логічно неможливо."""
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Як збій викрив сам себе: число, якого не може бути", 20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "машина не «впала» й не видала помилки — вона тихо віддала більше голосів, ніж узагалі існувало; зрадила збій АРИФМЕТИКА",
              11.5, GREY, "middle", style="italic")

    # ── ліва колонка: що нарахувала машина ──────────────────────────────────
    lx = 70
    s += rect(lx, 92, 360, 252, "#fdf4f4", RED, 1.8, 12)
    s += text(lx + 180, 118, "Що нарахувала машина (Схарбек)", 13, RED, "middle", "bold")

    rows = [
        ("Голоси за список (партію) загалом:", "≈ 4 000", INK),
        ("з них — за одну кандидатку:", "4 610", RED),
    ]
    yy = 152
    for lab, val, col in rows:
        s += text(lx + 22, yy, lab, 11, INK, "start")
        s += text(lx + 338, yy, val, 14, col, "end", "bold", mono=True)
        yy += 30

    # власне суперечність
    s += line(lx + 22, 200, lx + 338, 200, FAINT, 1.4)
    s += text(lx + 180, 228, "ПЕРСОНАЛЬНИХ голосів за одну особу —", 11, INK, "middle", "bold")
    s += text(lx + 180, 248, "БІЛЬШЕ, ніж голосів за весь її список", 11, RED, "middle", "bold")
    # знак неможливості
    s += text(lx + 180, 286, "частина > цілого", 13, RED, "middle", "bold")
    s += text(lx + 180, 312, "це АРИФМЕТИЧНО неможливо", 12, RED, "middle", "bold")
    s += text(lx + 180, 332, "→ отже, у даних помилка", 11, GREY, "middle", style="italic")

    # ── стрілка-зв'язка ─────────────────────────────────────────────────────
    s += arrow(lx + 366, 218, lx + 432, 218, INK, 2.4)
    s += text(lx + 399, 210, "сигнал", 9.5, GREY, "middle", "bold")
    s += text(lx + 399, 236, "тривоги", 9.5, GREY, "middle", "bold")

    # ── права колонка: що зробила перевірка ─────────────────────────────────
    rx = 472
    s += rect(rx, 92, 358, 252, "#eef7ee", GREEN, 1.8, 12)
    s += text(rx + 179, 118, "Що врятувало результат", 13, GREEN, "middle", "bold")

    steps = [
        ("1", "Закладена перевірка здорового глузду:", "«сума частин не може перевищувати ціле»"),
        ("2", "Голоси збереглися й на МАГНІТНИХ КАРТКАХ", "(паперово-магнітний слід кожного бюлетеня)"),
        ("3", "Ручний перерахунок за картками:", "у всіх інших — без змін, у неї −4 096"),
    ]
    yy = 146
    for n, a, b in steps:
        s += circle(rx + 28, yy - 4, 11, GREEN, GREEN, 0)
        s += text(rx + 28, yy, n, 12, "#ffffff", "middle", "bold")
        s += text(rx + 48, yy - 7, a, 10.5, INK, "start", "bold")
        s += text(rx + 48, yy + 9, b, 9.5, GREY, "start", style="italic")
        yy += 56
    s += text(rx + 179, yy + 4, "правильний підсумок відновлено", 11.5, GREEN, "middle", "bold")

    # нижня плашка-мораль
    s += rect(70, 360, W - 140, 92, "#f6f6f6", GREY, 1.4, 10)
    s += text(W / 2, 386, "Головний урок наперед: помилку зловила не «магія», а проста ПЕРЕВІРКА на несуперечність + збережена копія даних.",
              12, INK, "middle", "bold")
    s += text(W / 2, 410, "Якби результат лише «виглядав правдоподібно» (скажімо, +40, а не +4096), його могли б і не помітити.",
              11, INK, "middle")
    s += text(W / 2, 432, "Саме тому Розділ 3.9 не лише виявляє помилки парністю чи CRC, а вчить ще й закладати такі перевірки в систему.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-9-1i-1-caught.svg", s)


# ════════════ Рис. 3.9.1i.2 — двійковий «відбиток пальця» ════════════════════
def _bits16(val):
    return [(val >> i) & 1 for i in range(15, -1, -1)]  # старший → молодший


def fig_fingerprint():
    """Чому САМЕ 4096: один біт у позиції 2^12 перекинувся 0→1.
    Показуємо 514 і 4610 у двійковому — різниця рівно в одному біті."""
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 34, "Чому саме 4096, а не якесь «брудне» число: двійковий відбиток одного біта", 19, INK, "middle", "bold")
    s += text(W / 2, 56,
              "4096 = 2¹² — рівно степінь двійки; різниця між правильним і хибним числом — В ОДНОМУ-ЄДИНОМУ біті (позиція 13, рахуючи з 1)",
              11, GREY, "middle", style="italic")

    correct = 514     # правильний результат
    wrong = 4610      # що показала машина (514 + 4096)
    bits_c = _bits16(correct)
    bits_w = _bits16(wrong)
    flip_idx = bits_c.index(1) if False else None
    # індекс біта, що відрізняється (це біт 12 → у масиві 15..0 позиція 15-12=3)
    diff_pos = next(i for i in range(16) if bits_c[i] != bits_w[i])

    n = 16
    cell = 46
    x0 = (W - n * cell) / 2
    yC = 150   # рядок правильного
    yW = 250   # рядок хибного

    # підписи рядків
    s += text(x0 - 14, yC + 30, "правильно", 12, INK, "end", "bold")
    s += text(x0 - 14, yC + 46, "514", 13, INK, "end", "bold", mono=True)
    s += text(x0 - 14, yW + 30, "показала", 12, RED, "end", "bold")
    s += text(x0 - 14, yW + 46, "4610", 13, RED, "end", "bold", mono=True)

    # підписи розрядів зверху (степені двійки)
    for i in range(n):
        p = 15 - i
        cx = x0 + i * cell + cell / 2
        s += text(cx, 92, f"2", 9.5, GREY, "middle")
        s += text(cx + 6, 88, f"{p}", 7.5, GREY, "start")
        if p == 12:
            s += text(cx, 108, "= 4096", 8.5, RED, "middle", "bold")

    # клітинки
    def draw_row(bits, y, lit_color):
        out = ""
        for i in range(n):
            b = bits[i]
            cx = x0 + i * cell
            hit = (i == diff_pos)
            fill = "#ffffff"
            stroke = FAINT
            sw = 1.4
            if b == 1:
                fill = "#fdecec" if lit_color == RED else "#f3f5fd"
                stroke = lit_color
                sw = 2
            if hit:
                stroke = AMBER
                sw = 3
            out += rect(cx, y, cell - 6, 56, fill, stroke, sw, 6)
            col = (RED if lit_color == RED else BLUE) if b == 1 else GREY
            out += text(cx + (cell - 6) / 2, y + 36, str(b), 20, col, "middle", "bold", mono=True)
        return out

    s += draw_row(bits_c, yC, BLUE)
    s += draw_row(bits_w, yW, RED)

    # рамка-підсвітка біта, що перекинувся (наскрізна)
    cxd = x0 + diff_pos * cell
    s += rect(cxd - 4, yC - 6, cell - 6 + 8, (yW + 56) - (yC - 6) + 6, "none", AMBER, 2.4, 9)
    # стрілка 0 → 1
    s += text(cxd + (cell - 6) / 2, yC - 14, "0", 13, BLUE, "middle", "bold", mono=True)
    s += arrow(cxd + (cell - 6) / 2, yC + 64, cxd + (cell - 6) / 2, yW - 8, AMBER, 2.6)
    s += text(cxd + (cell - 6) / 2 + 14, (yC + yW) / 2 + 30, "0 → 1", 12, "#9a7322", "start", "bold")
    s += text(cxd + (cell - 6) / 2 + 14, (yC + yW) / 2 + 46, "один біт", 9.5, "#9a7322", "start", style="italic")

    # арифметика збоку/знизу
    s += text(W / 2, 348, "4610 − 514 = 4096 = 2¹²   —   додалося рівно «одне коліщатко» дванадцятого розряду", 13, INK, "middle", "bold")

    # плашка: чому це «відбиток пальця»
    s += rect(70, 372, W - 140, 102, "#fff8ec", AMBER, 1.6, 10)
    s += text(W / 2, 398, "Саме степінь двійки — головна «прикмета» одиничного бітового збою:", 12.5, "#8a6d1f", "middle", "bold")
    clues = [
        "• помилка, рівна 2ᵏ (2, 4, 8 … 4096 …), означає: перекинувся РІВНО ОДИН біт у розряді k — дуже характерний слід;",
        "• «людські» помилки (описка, подвійний підрахунок, зсув коми) дають інші числа, не круглі степені двійки;",
        "• тому експерти впевнено сказали: «перекинувся один біт». А ОСЬ ЧОМУ він перекинувся — це вже окреме питання (Рис. 3.9.1i.3).",
    ]
    for i, c in enumerate(clues):
        s += text(92, 422 + i * 18, c, 10.2, INK, "start")
    save("fig-3-9-1i-2-fingerprint.svg", s)


# ═══════ Рис. 3.9.1i.3 — доведений факт vs правдоподібна, але недоведена причина ═══
def fig_proven_vs_hypothesis():
    """Чесний поділ: ЩО доведено (один біт перекинувся) і ЩО лишилось
    гіпотезою (космічна частинка). Альтернативні причини не виключені."""
    W, H = 940, 520
    s = header(W, H)
    s += text(W / 2, 34, "Доведений факт vs правдоподібна, але НЕдоведена причина", 20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "офіційний висновок був стриманим: у програмі помилки не знайшли → «імовірно, спонтанна інверсія біта». ЧИМ її спричинено — не встановлено",
              10.8, GREY, "middle", style="italic")

    # ── верх: спостереження ─────────────────────────────────────────────────
    obsx = W / 2
    s += rect(obsx - 230, 80, 460, 52, "#f6f6f6", INK, 1.6, 10)
    s += text(obsx, 102, "СПОСТЕРЕЖЕННЯ (факт):", 12, INK, "middle", "bold")
    s += text(obsx, 122, "у пам'яті комірка дала +4096 = перекинувся один біт (поз. 13)", 11.5, INK, "middle")

    # роздвоєння вниз
    s += arrow(obsx - 60, 134, obsx - 200, 168, GREEN, 2.2)
    s += arrow(obsx + 60, 134, obsx + 200, 168, AMBER, 2.2)

    # ── ліва гілка: ДОВЕДЕНЕ ────────────────────────────────────────────────
    Lx = 60
    s += rect(Lx, 172, 380, 150, "#eef7ee", GREEN, 1.8, 12)
    s += text(Lx + 190, 196, "✓ ДОВЕДЕНО (зафіксовано в звіті)", 13, GREEN, "middle", "bold")
    proven = [
        "• у програмному коді помилки не виявили;",
        "• інші кандидати при перерахунку — без змін;",
        "• у неї рівно −4096 = одиничний бітовий збій;",
        "• офіційне формулювання: «спонтанна",
        "  інверсія двійкового розряду».",
    ]
    for i, p in enumerate(proven):
        s += text(Lx + 22, 222 + i * 19, p, 10.5, INK, "start")

    # ── права гілка: ГІПОТЕЗА ───────────────────────────────────────────────
    Rx = 500
    s += rect(Rx, 172, 380, 150, "#fff8ec", AMBER, 1.8, 12)
    s += text(Rx + 190, 196, "? ГІПОТЕЗА (правдоподібна, не доведена)", 12.5, "#8a6d1f", "middle", "bold")
    hypo = [
        "• популярне пояснення: космічна частинка",
        "  (одиничний збій, SEU) перекинула біт;",
        "• фізично можливо й співзвучно фактам,",
        "  АЛЕ прямого доказу немає:",
        "• ту частинку ніхто не «упіймав».",
    ]
    for i, p in enumerate(hypo):
        s += text(Rx + 22, 222 + i * 19, p, 10.5, INK, "start")

    # ── низ: критика / інші підозрювані ─────────────────────────────────────
    s += text(W / 2, 352, "Чому варто бути обережним: «не знайшли помилки в коді» ≠ «помилки не було».", 12.5, INK, "middle", "bold")
    s += text(W / 2, 372, "Той самий слід (+4096) могли б лишити й інші причини, які теж НЕ виключені до кінця:", 11, GREY, "middle", style="italic")

    others = [
        ("збій ПАМ'ЯТІ", "дефект комірки,\nнаведення, перешкода", BLUE),
        ("збій ЖИВЛЕННЯ", "просадка/викид\nнапруги в момент запису", BLUE),
        ("рідкісний БАГ", "помилку в коді\nпросто не помітили", BLUE),
        ("космічна\nЧАСТИНКА", "правдоподібно,\nале не доведено", AMBER),
    ]
    bw = 200
    gap = 16
    total = len(others) * bw + (len(others) - 1) * gap
    bx = (W - total) / 2
    for name, why, col in others:
        s += rect(bx, 388, bw, 84, "#fbfbfb", col, 1.6, 9)
        # назва (може бути дворядкова)
        nm = name.split("\n")
        for j, ln in enumerate(nm):
            s += text(bx + bw / 2, 410 + j * 16 - (len(nm) - 1) * 8, ln, 12, col, "middle", "bold")
        wl = why.split("\n")
        baseY = 438 if len(nm) == 1 else 446
        for j, ln in enumerate(wl):
            s += text(bx + bw / 2, baseY + j * 14, ln, 9.3, GREY, "middle")
        bx += bw + gap

    # підсумкова мораль
    s += rect(60, 484, W - 120, 30, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 504,
              "Як подавати таке чесно: «один біт перекинувся» — ФАКТ; «винна космічна частинка» — ПРАВДОПОДІБНА, але НЕдоведена версія.",
              11, INK, "middle", "bold")
    save("fig-3-9-1i-3-proven-vs-hypothesis.svg", s)


if __name__ == "__main__":
    fig_caught()
    fig_fingerprint()
    fig_proven_vs_hypothesis()
    print("OK — 3 SVG згенеровано у", OUT)
