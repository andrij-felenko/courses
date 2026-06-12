# -*- coding: utf-8 -*-
"""
Фігури до ⚙️-вставки §3.9.3a — «Контрольні суми на практиці: Internet checksum і Флетчер».
Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; «1»/добре/несе вагу — червоний акцент,
синій — нейтральні дані, зелене — результат/висновок, бурштин — те, на що дивимось.
Шрифт sans-serif. Нумерація підписів — за темою-вставкою «Рис. 3.9.3a.k».
Імена SVG містять суфікс s3a, щоб не змішуватися з рисунками тем розділу.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (єдина з figs.py розділу) ───────────────────────────────────────
RED   = "#c0271e"   # акцент / «спіймано» / перенос
BLUE  = "#1f47b5"   # нейтральні дані / байти
GREEN = "#1f8a3b"   # результат / висновок / «ок»
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"   # на що дивимось
PALE_R = "#fbeceb"
PALE_B = "#eef2fb"
PALE_G = "#eef7f0"
PALE_A = "#faf3e0"
MONO  = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="cInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="cRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="cGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = {GREEN: "cGreen", RED: "cRed"}.get(color, "cInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def cell(x, y, w, h, s, fill="none", stroke=FAINT, sw=1.4, rx=4,
         tcol=INK, size=14, weight="bold", mono=True):
    out = rect(x, y, w, h, fill, stroke, sw, rx)
    out += text(x + w / 2, y + h * 0.64, s, size, tcol, "middle", weight, mono=mono)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.3a.1 — Internet checksum (RFC 1071): 16-бітна сума з «загорнутим»
# переносом (end-around carry) + інверсія. Показуємо, ЧОМУ загортають перенос
# і що додавання контрольної суми робить повну суму ~0.
# ════════════════════════════════════════════════════════════════════════════
def fig_internet_checksum():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Internet checksum (RFC 1071): сума 16-бітних слів із загорнутим переносом",
              19, INK, "middle", "bold")
    s += text(W / 2, 53, "перенос за межі 16 біт не викидають, а додають назад знизу — тоді порядок слів неважливий",
              12, GREY, "middle", style="italic")

    # дані: сім 16-бітних слів — як у справжньому заголовку IPv4 (з полем
    # контрольної суми, узятим за нуль). Сума навмисно перевищує 16 біт.
    words = [0x4500, 0x003C, 0x1C46, 0xAC10, 0x0A63, 0xAC10, 0x0A0C]
    x0, y0 = 120, 88
    rw, rh, gap = 150, 26, 5
    s += text(x0, y0 - 8, "слова даних (16 біт):", 13, INK, "start", "bold")
    for i, wd in enumerate(words):
        yy = y0 + i * (rh + gap)
        s += cell(x0, yy, rw, rh, f"0x{wd:04X}", PALE_B, FAINT, 1.4, 5, BLUE, 14)
        s += text(x0 + rw + 14, yy + rh * 0.66, "+", 17, INK, "middle", "bold")
    # «сирий» 32-бітний акумулятор
    raw = sum(words)
    yacc = y0 + len(words) * (rh + gap) + 4
    s += line(x0 - 4, yacc - 2, x0 + rw + 30, yacc - 2, INK, 1.6)
    s += cell(x0, yacc, rw, rh, f"0x{raw:05X}", PALE_A, AMBER, 1.8, 5, INK, 14)
    s += text(x0 + rw + 18, yacc + rh * 0.66,
              "перевищило 16 біт — є перенос", 11.5, RED, "start", "bold")

    # розклад: верхні 16 (перенос) + нижні 16
    hi = (raw >> 16) & 0xFFFF
    lo = raw & 0xFFFF
    yf = yacc + rh + 26
    s += text(x0, yf - 8, "загортаємо перенос (end-around carry):", 13, INK, "start", "bold")
    s += cell(x0, yf, rw, rh, f"0x{lo:04X}", PALE_B, FAINT, 1.4, 5, BLUE, 14)
    s += text(x0 + rw + 14, yf + rh * 0.66, "+", 17, INK, "middle", "bold")
    s += cell(x0, yf + rh + gap, rw, rh, f"0x{hi:04X}", PALE_R, RED, 1.6, 5, RED, 14)
    s += text(x0 + rw + 18, yf + rh + gap + rh * 0.66,
              "↑ перенос, доданий ЗНИЗУ", 11.5, RED, "start", "bold")
    folded = (lo + hi)
    folded = (folded & 0xFFFF) + (folded >> 16)   # на випадок ще одного переносу
    yfold = yf + 2 * (rh + gap) + 2
    s += line(x0 - 4, yfold - 4, x0 + rw + 30, yfold - 4, INK, 1.6)
    s += cell(x0, yfold, rw, rh, f"0x{folded:04X}", PALE_G, GREEN, 1.8, 5, GREEN, 14)
    s += text(x0 + rw + 18, yfold + rh * 0.66, "= згорнута сума (16 біт)", 12, GREEN, "start", "bold")

    # інверсія → контрольна сума
    chk = (~folded) & 0xFFFF
    s += arrow(x0 + rw / 2, yfold + rh + 4, x0 + rw / 2, yfold + rh + 24, INK, 2)
    s += text(x0 + rw + 18, yfold + rh + 22, "інвертуємо біти (~)", 11.5, INK, "start", "bold")
    ychk = yfold + rh + 28
    s += cell(x0, ychk, rw, rh, f"0x{chk:04X}", "#ffffff", INK, 2, 5, RED, 14)
    s += text(x0 + rw + 18, ychk + rh * 0.66,
              "= КОНТРОЛЬНА СУМА (її і шлемо)", 12, RED, "start", "bold")

    # права колонка: перевірка на приймачі
    bx = 600
    s += rect(bx, 88, 300, 472, PALE_G, GREEN, 1.6, 12)
    s += text(bx + 150, 116, "На приймачі — той самий цикл,", 13, INK, "middle", "bold")
    s += text(bx + 150, 134, "але вже з контрольною сумою", 13, INK, "middle", "bold")
    rows = [
        ("сума всіх слів + chk", INK),
        ("→ згортаємо перенос", INK),
        ("→ інвертуємо", INK),
    ]
    for i, (t, c) in enumerate(rows):
        s += text(bx + 22, 168 + i * 26, "• " + t, 12.5, c, "start", "bold", mono=False)
    s += rect(bx + 22, 252, 256, 64, "#ffffff", GREEN, 2, 10)
    s += text(bx + 150, 280, "результат = 0x0000", 16, GREEN, "middle", "bold", mono=True)
    s += text(bx + 150, 302, "⇒ помилки не видно", 12.5, GREEN, "middle", "bold")
    s += text(bx + 22, 348, "Будь-яке ненульове значення —", 12, RED, "start", "bold")
    s += text(bx + 22, 366, "пакет пошкоджено.", 12, RED, "start", "bold")
    s += line(bx + 22, 386, bx + 278, 386, FAINT, 1.4)
    s += text(bx + 22, 412, "Чому загортають перенос:", 12.5, INK, "start", "bold")
    for i, t in enumerate([
        "додавання з end-around carry",
        "комутативне й асоціативне —",
        "сума не залежить від порядку",
        "слів, тож її легко рахувати",
        "хоч уперед, хоч назад по буферу.",
    ]):
        s += text(bx + 22, 434 + i * 21, t, 11.5, INK, "start", mono=False)

    s += rect(60, 568, W - 120, 26, PALE_B, BLUE, 1.4, 8)
    s += text(W / 2, 586,
              "Уся арифметика — у 16 бітах: складай слова, загортай перенос, наприкінці інвертуй.",
              12, INK, "middle", "bold")
    save("fig-r09-s3a-1-internet-checksum.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.3a.2 — Чому проста сума сліпа до перестановки, а Флетчер — ні.
# Дві біжучі суми: sum1 (звичайна) і sum2 (сума часткових сум = ваги за позицією).
# ════════════════════════════════════════════════════════════════════════════
def fig_fletcher():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Чому Флетчер ловить те, що проста сума пропускає",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 53, "друга сума накопичує перші — тож кожен байт зважений своєю позицією, і порядок уже важить",
              12, GREY, "middle", style="italic")

    data = [0x10, 0x20, 0x30]
    swapped = [0x10, 0x30, 0x20]   # переставили два байти

    def run_table(x, ytop, bytes_, title, tcol):
        nonlocal s
        s += text(x, ytop - 10, title, 14, tcol, "start", "bold")
        # шапка
        cw = [70, 90, 110, 130]
        heads = ["байт", "sum1 +=", "sum2 += sum1", "позиц. вага"]
        cx = x
        hy = ytop
        for w, hd in zip(cw, heads):
            s += rect(cx, hy, w, 26, PALE_A, AMBER, 1.4, 4)
            s += text(cx + w / 2, hy + 18, hd, 11.5, INK, "middle", "bold", mono=False)
            cx += w
        sum1 = 0
        sum2 = 0
        n = len(bytes_)
        for i, b in enumerate(bytes_):
            sum1 += b
            sum2 += sum1
            ry = hy + 26 + i * 30
            cx = x
            vals = [f"0x{b:02X}",
                    f"{sum1}",
                    f"{sum2}",
                    f"×{n - i}"]
            cols = [BLUE, INK, RED, GREY]
            for w, v, c in zip(cw, vals, cols):
                s += rect(cx, ry, w, 30, "#ffffff", FAINT, 1.2, 4)
                s += text(cx + w / 2, ry + 20, v, 13, c, "middle", "bold", mono=True)
                cx += w
        # підсумковий рядок
        ry = hy + 26 + n * 30 + 6
        s += rect(x, ry, sum(cw), 30, PALE_G, GREEN, 1.6, 5)
        s += text(x + 8, ry + 20, "разом:", 12, INK, "start", "bold")
        s += text(x + cw[0] + cw[1] / 2 + 4, ry + 20, f"sum1={sum1}", 12.5, INK, "middle", "bold", mono=True)
        s += text(x + cw[0] + cw[1] + cw[2] / 2, ry + 20, f"sum2={sum2}", 12.5, RED, "middle", "bold", mono=True)
        chk = (sum2 << 8) | sum1
        s += text(x + cw[0] + cw[1] + cw[2] + cw[3] / 2, ry + 20,
                  f"→0x{chk:04X}", 12, GREEN, "middle", "bold", mono=True)
        return sum1, sum2

    # ліворуч — оригінал, праворуч — переставлені байти
    a1, a2 = run_table(70, 110, data, "Порядок A:  10 20 30", BLUE)
    b1, b2 = run_table(510, 110, swapped, "Порядок B:  10 30 20  (переставлено 2 байти)", RED)

    # висновок-порівняння
    cy = 360
    s += rect(60, cy, W - 120, 96, "#ffffff", INK, 1.6, 12)
    s += text(W / 2, cy + 26, "Та сама множина байтів, інший порядок:", 14.5, INK, "middle", "bold")
    s += text(250, cy + 56, f"sum1: {a1}  =  {b1}", 14, GREY, "middle", "bold", mono=True)
    s += text(250, cy + 78, "проста сума ОДНАКОВА — перестановки не бачить", 11.5, GREY, "middle", "bold")
    s += line(W / 2, cy + 40, W / 2, cy + 86, FAINT, 1.4)
    s += text(690, cy + 56, f"sum2: {a2}  ≠  {b2}", 14, RED, "middle", "bold", mono=True)
    s += text(690, cy + 78, "друга сума РІЗНА — Флетчер ловить перестановку", 11.5, RED, "middle", "bold")

    # пояснення ваг
    ey = 480
    s += text(70, ey, "Чому так:", 13.5, INK, "start", "bold")
    s += text(70, ey + 22,
              "sum2 = (n·b₀ + (n−1)·b₁ + … + 1·b_{n−1}). Кожен байт входить зі своєю вагою за позицією,",
              12.5, INK, "start", mono=False)
    s += text(70, ey + 42,
              "тож переставивши байти, ми майже завжди змінюємо sum2 — навіть коли sum1 лишилась тією ж.",
              12.5, INK, "start", mono=False)
    s += rect(60, ey + 58, W - 120, 26, PALE_R, RED, 1.4, 8)
    s += text(W / 2, ey + 76,
              "Контрольна сума Флетчера = (sum2 << 8) | sum1 — два байти за один прохід даних.",
              12, INK, "middle", "bold")
    save("fig-r09-s3a-2-fletcher.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.3a.3 — Що ловить кожен метод: матриця «клас помилки × алгоритм».
# Проста сума · Internet checksum · Флетчер-16  (а далі — CRC, §3.9.4, як орієнтир).
# ════════════════════════════════════════════════════════════════════════════
def fig_matrix():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Що ловить кожен метод — і де його сліпа пляма",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 53, "ціна — кілька рядків коду й один-два прохід; «вартість» зростає вниз разом із надійністю",
              12, GREY, "middle", style="italic")

    cols = ["Проста\nсума 8-біт", "Internet\nchecksum 16", "Флетчер-16", "CRC-16\n(→ §3.9.4)"]
    rows = [
        "Один перевернутий біт",
        "Кілька бітів в одному байті",
        "Переставлені байти",
        "Вставлені/зайві нулі",
        "Серія підряд (burst) ≤ 16 біт",
        "Ціна (час/код)",
    ]
    # значення: ✓ повне, ~ частково/слабко, ✗ сліпа пляма; останній рядок — текст
    grid = [
        ["✓", "✓", "✓", "✓"],
        ["~", "✓", "✓", "✓"],
        ["✗", "✗", "✓", "✓"],
        ["~", "~", "✓", "✓"],
        ["~", "~", "~", "✓"],
        ["найдешевше", "дешеве", "дешеве", "дорожче"],
    ]

    x0, y0 = 70, 96
    label_w = 250
    cw = 150
    rh = 46
    # заголовки стовпців
    for j, c in enumerate(cols):
        cx = x0 + label_w + j * cw
        s += rect(cx, y0, cw, 52, PALE_B, BLUE, 1.4, 6)
        for k, part in enumerate(c.split("\n")):
            s += text(cx + cw / 2, y0 + 22 + k * 17, part, 12.5, INK, "middle", "bold", mono=False)
    # рядки
    for i, rname in enumerate(rows):
        ry = y0 + 52 + i * rh
        last = (i == len(rows) - 1)
        s += rect(x0, ry, label_w, rh, PALE_A if last else "#fafafa", AMBER if last else FAINT, 1.4, 6)
        s += text(x0 + 12, ry + rh * 0.62, rname, 12.5, INK, "start", "bold", mono=False)
        for j in range(len(cols)):
            cx = x0 + label_w + j * cw
            v = grid[i][j]
            if last:
                s += rect(cx, ry, cw, rh, "#ffffff", FAINT, 1.2, 6)
                s += text(cx + cw / 2, ry + rh * 0.62, v, 12, INK, "middle", "bold", mono=False)
            else:
                fill = {"✓": PALE_G, "~": PALE_A, "✗": PALE_R}[v]
                stc = {"✓": GREEN, "~": AMBER, "✗": RED}[v]
                s += rect(cx, ry, cw, rh, fill, stc, 1.4, 6)
                s += text(cx + cw / 2, ry + rh * 0.66, v, 19, stc, "middle", "bold")

    # легенда
    ly = y0 + 52 + len(rows) * rh + 18
    items = [("✓", GREEN, "майже завжди ловить"),
             ("~", AMBER, "ловить не все (є сліпі плями)"),
             ("✗", RED, "не бачить узагалі")]
    lx = x0
    for sym, col, txt in items:
        s += text(lx, ly, sym, 18, col, "start", "bold")
        s += text(lx + 22, ly, txt, 12, INK, "start", "bold", mono=False)
        lx += 250
    save("fig-r09-s3a-3-matrix.svg", s)


if __name__ == "__main__":
    fig_internet_checksum()
    fig_fletcher()
    fig_matrix()
    print("r09-s3a (checksums-in-code) figures done.")
