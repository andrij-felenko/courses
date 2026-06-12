# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 3.7 — «Програмована логіка: ПЛІС/FPGA» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; поле зелене; стрілки через marker.
Підписи у тексті — за темою (Рис. 3.7.T.k). Імена SVG: fig-3-7-T-k-*.svg.
Допоміжні функції — спільні з рештою розділів (копія), щоб вигляд був єдиний.
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
DARKAMBER = "#9a7322"
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber", GREY: "aGrey"}


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


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def caption_box(s, W, lines, y0, col=GREEN, bg="#f4f7f4"):
    """Зелена рамка-висновок унизу фігури з кількома рядками (перший — жирний)."""
    h = 18 + 24 * len(lines)
    s += rect(60, y0, W - 120, h, bg, col, 1.7, 10)
    for i, (t, bold) in enumerate(lines):
        s += text(W / 2, y0 + 26 + i * 24, t,
                  11.5 if bold else 10.5, INK if bold else GREY,
                  "middle", "bold" if bold else "normal",
                  "normal" if bold else "italic")
    return s


# ── загальні цеглинки FPGA ──────────────────────────────────────────────────
def _ff(x, y, w=34, h=40, col=BLUE, lab="DFF"):
    """Маленький D-тригер."""
    out = rect(x, y, w, h, "#f3f5fd", col, 1.8, 4)
    out += text(x + w / 2, y + h / 2 + 4, lab, 9, col, "middle", "bold")
    # позначка фронту такту
    out += polyline([(x + 4, y + h - 6), (x + 9, y + h - 12), (x + 9, y + h - 6)], col, 1.4)
    return out


def _lut(x, y, w=58, h=46, n="4", col=GREEN):
    """Блок LUT."""
    out = rect(x, y, w, h, "#eef7ee", col, 1.8, 5)
    out += text(x + w / 2, y + h / 2 - 2, f"LUT-{n}", 11, col, "middle", "bold")
    out += text(x + w / 2, y + h / 2 + 13, "таблиця", 8, GREY, "middle")
    return out


def _cell(x, y, w=104, h=58, hl=False):
    """Логічна клітинка = LUT + тригер."""
    col = RED if hl else INK
    out = rect(x, y, w, h, "#fdf4f4" if hl else "#fbfbfb", col, 2 if hl else 1.4, 6)
    out += _lut(x + 6, y + 7, 52, 30, "4")
    out += _ff(x + 66, y + 10, 30, 36)
    out += arrow(x + 58, y + 22, x + 66, y + 22, INK, 1.5)
    return out


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.1 — Навіщо програмована логіка: паралельність у залізі
# ═══════════════════════════════════════════════════════════════════════════

def fig_371_1_serial_bottleneck():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Корінь проблеми: процесор робить усе ПО ЧЕРЗІ", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одне ядро виконує одну команду за такт — 100 однакових дій займають 100 тактів, одна за одною",
              11.5, GREY, "middle", style="italic")
    # процесор — серійний конвеєр у часі
    s += text(230, 96, "ПРОЦЕСОР: одна АЛП, час іде вправо", 12.5, BLUE, "middle", "bold")
    y = 120
    for i in range(8):
        x = 90 + i * 92
        lab = f"крок {i+1}" if i < 7 else "…крок N"
        s += rect(x, y, 80, 36, "#f3f5fd", BLUE, 1.5, 5)
        s += text(x + 40, y + 23, lab, 9.5, INK, "middle", "bold")
        if i < 7:
            s += arrow(x + 80, y + 18, x + 92, y + 18, BLUE, 1.6)
    s += text(W / 2, y + 60, "такт 1 → такт 2 → … → такт N   (затрачено N тактів — послідовно)", 11, BLUE, "middle", "bold")
    # FPGA — паралельно у просторі
    s += text(230, 250, "FPGA: N окремих схем, усі працюють РАЗОМ", 12.5, GREEN, "middle", "bold")
    y2 = 274
    for i in range(8):
        x = 90 + i * 92
        lab = f"блок {i+1}" if i < 7 else "блок N"
        s += rect(x, y2, 80, 40, "#eef7ee", GREEN, 1.6, 5)
        s += text(x + 40, y2 + 18, lab, 9.5, INK, "middle", "bold")
        s += text(x + 40, y2 + 33, "своя логіка", 8, GREEN, "middle")
        s += arrow(x + 40, y2 - 12, x + 40, y2 - 1, GREEN, 1.5)
    s += text(W / 2, y2 - 18, "усі входи приходять одночасно", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, y2 + 60, "усі N результатів — за ОДИН такт (паралельно у просторі, а не в часі)", 11, GREEN, "middle", "bold")
    s = caption_box(s, W, [
        ("Процесор розкладає роботу в ЧАСІ (швидко перемикає одну АЛП); FPGA розкладає її у ПРОСТОРІ (багато схем нараз).", True),
        ("Коли дій багато й вони однотипні, послідовний процесор просто не встигає по тактах — а паралельне залізо встигає.", False),
    ], 396)
    save("fig-3-7-1-1-serial-bottleneck.svg", s)


def fig_371_2_throughput_math():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Коли «не встигає по тактах» — це проста арифметика", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "приклад: обробити 200 млн відліків за секунду, по 10 операцій на кожен",
              11.5, GREY, "middle", style="italic")
    # ліворуч — процесор
    s += rect(70, 90, 360, 230, "#f3f5fd", BLUE, 2, 12)
    s += text(250, 116, "ПРОЦЕСОР @ 200 МГц", 13, BLUE, "middle", "bold")
    rowsP = [
        "потрібно: 200·10⁶ × 10 = 2·10⁹ оп/с",
        "має: ~1 оп/такт × 2·10⁸ такт/с",
        "         = 2·10⁸ оп/с",
        "дефіцит: у 10 разів замало!",
    ]
    for i, t in enumerate(rowsP):
        col = RED if i == 3 else INK
        s += text(90, 150 + i * 30, t, 11.5, col, "start", "bold" if i == 3 else "normal")
    s += text(250, 296, "одна АЛП фізично не дає 2 млрд оп/с на 200 МГц", 9.5, GREY, "middle", style="italic")
    # праворуч — FPGA
    s += rect(470, 90, 360, 230, "#eef7ee", GREEN, 2, 12)
    s += text(650, 116, "FPGA @ 200 МГц", 13, GREEN, "middle", "bold")
    rowsF = [
        "ставимо 10 обчислювачів поряд",
        "кожен: 1 операція за такт",
        "разом: 10 оп/такт × 2·10⁸",
        "         = 2·10⁹ оп/с ✓",
    ]
    for i, t in enumerate(rowsF):
        col = GREEN if i == 3 else INK
        s += text(490, 150 + i * 30, t, 11.5, col, "start", "bold" if i == 3 else "normal")
    s += text(650, 296, "та сама частота, але в 10 разів більше роботи за такт", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Швидкодія = (операцій за такт) × (тактів за секунду). Підняти частоту важко; додати паралельних блоків — легко.", True),
    ], 348)
    save("fig-3-7-1-2-throughput-math.svg", s)


def fig_371_3_latency():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Друга перевага: детермінована МАЛА затримка від входу до дії", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "скільки наносекунд від «сигнал змінився» до «вихід відреагував»",
              11.5, GREY, "middle", style="italic")
    # процесор: переривання + код
    s += text(230, 92, "Процесор (через переривання)", 12, BLUE, "middle", "bold")
    chainP = ["сигнал", "перерив.", "збереж.\nконтекст", "код-\nобробник", "вихід"]
    x = 80
    for i, t in enumerate(chainP):
        s += rect(x, 110, 66, 44, "#f3f5fd", BLUE, 1.5, 5)
        for j, ln in enumerate(t.split("\n")):
            s += text(x + 33, 130 + j * 14 - (7 if "\n" in t else 0), ln, 9, INK, "middle", "bold")
        if i < len(chainP) - 1:
            s += arrow(x + 66, 132, x + 78, 132, BLUE, 1.5)
        x += 78
    s += text(230, 178, "десятки–сотні тактів + джитер (затримка «плаває»)", 10, RED, "middle", "bold")
    # FPGA: пряма логіка
    s += text(230, 230, "FPGA (пряма логіка)", 12, GREEN, "middle", "bold")
    s += rect(120, 248, 80, 44, "#eef7ee", GREEN, 1.6, 5)
    s += text(160, 274, "вхід", 10, INK, "middle", "bold")
    s += arrow(200, 270, 320, 270, GREEN, 2)
    s += rect(320, 248, 150, 44, "#eef7ee", GREEN, 1.6, 5)
    s += text(395, 268, "комбінаційна логіка", 9.5, GREEN, "middle", "bold")
    s += text(395, 283, "кілька вентилів", 8.5, GREY, "middle")
    s += arrow(470, 270, 560, 270, GREEN, 2)
    s += rect(560, 248, 80, 44, "#eef7ee", GREEN, 1.6, 5)
    s += text(600, 274, "вихід", 10, INK, "middle", "bold")
    s += text(230, 312, "одиниці–десятки наносекунд, СТАЛО (без джитера)", 10, GREEN, "middle", "bold")
    s = caption_box(s, W, [
        ("FPGA реагує за час проходження сигналу крізь кілька вентилів — швидко й ПЕРЕДБАЧУВАНО, такт у такт однаково.", True),
        ("Процесорові ж треба перервати поточну роботу, зберегти стан і виконати код — повільніше, і затримка «плаває».", False),
    ], 344)
    save("fig-3-7-1-3-latency.svg", s)


def fig_371_4_where_used():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Де паралельність вирішує: типові задачі для FPGA", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "спільна риса — потік даних надто швидкий або реакція потрібна надто рання для одного ядра",
              11.5, GREY, "middle", style="italic")
    items = [
        ("Цифрова обробка сигналу", "тисячі множень-додавань на кожен відлік потоку (фільтри, FFT)", GREEN),
        ("Відео й зображення", "мільйони пікселів за кадр × десятки кадрів — конвеєр на льоту", GREEN),
        ("Швидкі інтерфейси", "розбір потоку на сотні Мбіт/с біт за бітом, без запасу на код", BLUE),
        ("Точний таймінг керування", "багатофазний ШІМ, реакція за наносекунди, паралельні канали", BLUE),
        ("Багато однакових каналів", "сотні лічильників/АЛП, кожен — своя апаратна копія", AMBER),
    ]
    for i, (k, v, col) in enumerate(items):
        y = 90 + i * 52
        s += rect(70, y, 760, 44, "#fafafa", col, 1.6, 8)
        s += text(90, y + 27, k, 12.5, col, "start", "bold")
        s += text(360, y + 27, v, 10.5, INK, "start")
    s = caption_box(s, W, [
        ("Усюди тут робота надто широка для послідовного ядра — її розкладають у простір: багато апаратних блоків нараз.", True),
    ], 360)
    save("fig-3-7-1-4-where-used.svg", s)


def fig_371_5_spectrum():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Місце FPGA у світі обчислень: гнучкість проти швидкості", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "від «усе вирішує програма» до «усе зашито в кремній» — FPGA посередині",
              11.5, GREY, "middle", style="italic")
    # горизонтальна вісь
    y = 150
    s += line(90, y, 810, y, GREY, 2)
    s += text(90, y + 150, "", 9, GREY)
    nodes = [
        (150, "Процесор / МК", "будь-яка програма,\nале послідовно", BLUE, "гнучкий, повільніший"),
        (380, "GPU", "тисячі ядер,\nдані-паралельно", AMBER, ""),
        (560, "FPGA", "своя СХЕМА під\nзадачу, паралельно", GREEN, "← наш герой"),
        (770, "ASIC", "схема назавжди\nвипалена в чип", RED, "найшвидший, негнучкий"),
    ]
    for x, k, d, col, note in nodes:
        s += circle(x, y, 8, "#fff", col, 3)
        s += rect(x - 70, y - 78, 140, 56, "#fafafa", col, 1.6, 8)
        s += text(x, y - 58, k, 12.5, col, "middle", "bold")
        for j, ln in enumerate(d.split("\n")):
            s += text(x, y - 42 + j * 14, ln, 9, INK, "middle")
        if note:
            ncol = GREEN if "герой" in note else GREY
            s += text(x, y + 30, note, 9.5, ncol, "middle", "bold" if "герой" in note else "normal",
                      "normal" if "герой" in note else "italic")
    s += arrow(110, y + 70, 250, y + 70, INK, 1.8)
    s += text(180, y + 64, "більше ГНУЧКОСТІ", 10, BLUE, "middle", "bold")
    s += arrow(790, y + 70, 650, y + 70, INK, 1.8)
    s += text(720, y + 64, "більше ШВИДКОСТІ й ефективності", 10, RED, "middle", "bold")
    s = caption_box(s, W, [
        ("Процесор гнучкий, бо програмований, але послідовний; ASIC — найшвидший, та схема в ньому застигла назавжди.", True),
        ("FPGA бере найкраще від обох: справжню паралельну СХЕМУ під задачу, яку до того ж можна переписати.", False),
    ], 318)
    save("fig-3-7-1-5-spectrum.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.2 — Від PAL до FPGA: еволюція програмованих чипів
# ═══════════════════════════════════════════════════════════════════════════

def fig_372_1_and_or_plane():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Ідея PAL: програмована матриця AND, фіксована матриця OR", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "будь-яка булева функція — це сума добутків (§3.2.1); пропалюємо потрібні з'єднання — отримуємо функцію",
              11.5, GREY, "middle", style="italic")
    # входи зліва
    ins = ["a", "b", "c"]
    ix = 110
    for i, nm in enumerate(ins):
        y = 120 + i * 28
        s += text(ix - 18, y + 4, nm, 12, BLUE, "end", "bold")
        s += line(ix, y, 760, y, FAINT, 1.4)         # пряма лінія входу
        s += text(ix, y - 6, "", 9, GREY)
    # вертикальні «добуткові» лінії (AND)
    prods = [(260, [(0, 1), (1, 1)], "a·b"),
             (340, [(1, 1), (2, 0)], "b·c̄"),
             (420, [(0, 1), (2, 1)], "a·c")]
    for px, conns, lab in prods:
        s += line(px, 110, px, 230, INK, 1.6)
        s += text(px, 248, lab, 11, INK, "middle", "bold")
        # AND-вентиль унизу
        s += text(px, 268, "(AND)", 8.5, GREY, "middle")
        for (row, on) in conns:
            y = 120 + row * 28
            col = RED if on else BLUE
            s += circle(px, y, 4.5, col, col, 1)     # пропалена точка з'єднання
    s += text(150, 90, "програмована матриця AND (точки = пропалені зв'язки)", 10.5, RED, "start", "bold")
    # OR-частина
    s += text(620, 90, "фіксована матриця OR", 10.5, GREEN, "start", "bold")
    s += rect(560, 110, 150, 70, "#eef7ee", GREEN, 1.8, 8)
    s += text(635, 138, "OR", 13, GREEN, "middle", "bold")
    s += text(635, 160, "сума добутків", 9.5, GREY, "middle")
    for px, _, _ in prods:
        s += arrow(px, 230, 558, 145, GREY, 1.2)
    s += arrow(710, 145, 790, 145, GREEN, 2)
    s += text(770, 132, "вихід", 10, GREEN, "middle", "bold")
    s += text(770, 165, "F = a·b + b·c̄ + a·c", 9.5, INK, "middle", "bold")
    s = caption_box(s, W, [
        ("PAL (programmable array logic): входи йдуть у матрицю AND, де користувач ПРОПАЛЮЄ потрібні добутки,", True),
        ("а ті додаються фіксованою матрицею OR. Так у дрібну мікросхему «вшивали» будь-яку логіку — замість купи 74-х корпусів.", False),
    ], 360)
    save("fig-3-7-2-1-and-or-plane.svg", s)


def fig_372_2_pal_pla_gal():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Сімейство SPLD: PROM, PAL, PLA, GAL — хто що програмує", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі три — матриці AND та OR; різниця лише в тому, ЯКА з матриць програмована",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("PROM", "AND — фікс.", "OR — програм.", "повний дешифратор;\nдобре для таблиць", GREY),
        ("PAL", "AND — програм.", "OR — фікс.", "дешево й швидко;\nнайпопулярніший", GREEN),
        ("PLA", "AND — програм.", "OR — програм.", "найгнучкіший,\nале повільніший", BLUE),
        ("GAL", "як PAL, але", "СТИРАЄТЬСЯ", "перепрограмовний\n(EEPROM), не «прах»", AMBER),
    ]
    for i, (k, a, o, d, col) in enumerate(cards):
        x = 60 + i * 205
        s += rect(x, 88, 185, 200, "#fafafa", col, 1.8, 10)
        s += text(x + 92, 116, k, 15, col, "middle", "bold")
        s += line(x + 16, 128, x + 169, 128, FAINT, 1.4)
        s += text(x + 92, 150, a, 10.5, INK, "middle", "bold")
        s += text(x + 92, 172, o, 10.5, INK, "middle", "bold")
        s += line(x + 16, 186, x + 169, 186, FAINT, 1.4)
        for j, ln in enumerate(d.split("\n")):
            s += text(x + 92, 210 + j * 16, ln, 9.5, GREY, "middle", style="italic")
        if k == "PAL":
            s += text(x + 92, 268, "★ робоча конячка", 9.5, GREEN, "middle", "bold")
        if k == "GAL":
            s += text(x + 92, 268, "★ багаторазовий", 9.5, DARKAMBER, "middle", "bold")
    save("fig-3-7-2-2-pal-pla-gal.svg", s)


def fig_372_3_macrocell():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Крок до пам'яті стану: макрокомірка з тригером на виході", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "сама лиш матриця AND-OR дає тільки комбінаційну логіку; додамо тригер (§3.3.3) — і з'явиться стан",
              11.5, GREY, "middle", style="italic")
    s += rect(80, 120, 170, 120, "#eef7ee", GREEN, 1.8, 10)
    s += text(165, 150, "матриця", 12, GREEN, "middle", "bold")
    s += text(165, 168, "AND-OR", 12, GREEN, "middle", "bold")
    s += text(165, 192, "(сума добутків)", 9.5, GREY, "middle")
    s += text(165, 214, "комбінаційна F", 9.5, INK, "middle", "bold")
    s += arrow(250, 180, 330, 180, INK, 2)
    s += _ff(330, 158, 50, 48, BLUE, "DFF")
    s += text(355, 224, "тригер", 9.5, BLUE, "middle", "bold")
    s += arrow(380, 180, 470, 180, INK, 2)
    # мультиплексор вибору: рег. чи комб.
    s += path(f"M470,150 L510,162 L510,198 L470,210 Z", "#fff8e8", AMBER, 1.8)
    s += text(490, 184, "MUX", 9, DARKAMBER, "middle", "bold")
    s += text(490, 232, "рег. чи комб.?", 8.5, GREY, "middle")
    s += arrow(510, 180, 600, 180, AMBER, 2)
    s += text(640, 184, "вихідний пін", 10.5, INK, "middle", "bold")
    # зворотний зв'язок
    s += polyline([(355, 206), (355, 280), (60, 280), (60, 165), (78, 165)], GREY, 1.6, "4 3")
    s += text(210, 296, "зворотний зв'язок: вихід тригера повертається у матрицю → можна будувати автомати (§3.3.9)", 10, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Макрокомірка = матриця AND-OR + тригер + мультиплексор вибору «реєстровий чи комбінаційний вихід».", True),
        ("Це той самий тригер із Розділу 3.3, тільки тепер його кладуть біля кожного виходу — так з'являється послідовнісна логіка.", False),
    ], 322)
    save("fig-3-7-2-3-macrocell.svg", s)


def fig_372_4_cpld_vs_fpga():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "CPLD проти FPGA: дві різні архітектури програмованої логіки", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "CPLD — кілька великих PAL-блоків через центральну матрицю; FPGA — море дрібних клітинок у сітці",
              11.5, GREY, "middle", style="italic")
    # CPLD ліворуч
    s += rect(60, 86, 360, 300, "#fbfbfb", BLUE, 1.6, 12)
    s += text(240, 110, "CPLD", 14, BLUE, "middle", "bold")
    s += text(240, 128, "кілька «жирних» блоків", 9.5, GREY, "middle")
    s += rect(170, 200, 140, 50, "#f3f5fd", BLUE, 1.6, 8)
    s += text(240, 230, "центральна матриця", 9.5, BLUE, "middle", "bold")
    for i in range(4):
        ang = i
        coords = [(95, 150), (315, 150), (95, 300), (315, 300)]
        bx, by = coords[i]
        s += rect(bx, by, 90, 56, "#eef7ee", GREEN, 1.6, 6)
        s += text(bx + 45, by + 26, "PAL-блок", 9, GREEN, "middle", "bold")
        s += text(bx + 45, by + 42, "+ макрокоміp.", 7.5, GREY, "middle")
        s += line(bx + 45, by + (56 if by < 200 else 0), 240, 222 if by < 200 else 200, FAINT, 1.4)
    s += text(240, 360, "мало блоків, але кожен потужний;", 9.5, INK, "middle")
    s += text(240, 376, "затримка передбачувана, вмикається миттєво", 9.5, GREEN, "middle", "bold")
    # FPGA праворуч
    s += rect(480, 86, 360, 300, "#fbfbfb", GREEN, 1.6, 12)
    s += text(660, 110, "FPGA", 14, GREEN, "middle", "bold")
    s += text(660, 128, "море дрібних клітинок", 9.5, GREY, "middle")
    gx, gy, st = 520, 150, 50
    for r in range(4):
        for c in range(5):
            x, y = gx + c * st, gy + r * st
            s += rect(x, y, 30, 30, "#eef7ee", GREEN, 1.3, 4)
            # маршрутні лінії
            if c < 4:
                s += line(x + 30, y + 15, x + st, y + 15, FAINT, 1.2)
            if r < 3:
                s += line(x + 15, y + 30, x + 15, y + st, FAINT, 1.2)
    s += text(660, 360, "тисячі–мільйони дрібних LUT-клітинок;", 9.5, INK, "middle")
    s += text(660, 376, "величезна ємність, гнучка маршрутизація", 9.5, GREEN, "middle", "bold")
    s = caption_box(s, W, [
        ("CPLD = жменя великих PAL-блоків + центральна матриця: невелика ємність, миттєвий старт, дуже передбачувана затримка.", True),
        ("FPGA = регулярна сітка тисяч ДРІБНИХ клітинок з програмованою маршрутизацією: на порядки більша, гнучкіша — про неї весь розділ.", False),
    ], 392)
    save("fig-3-7-2-4-cpld-vs-fpga.svg", s)


def fig_372_5_ladder():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Сходинки еволюції: від однієї матриці до мільйонів клітинок", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен крок додавав ємності й гнучкості, не змінюючи головної ідеї — «логіка, яку задають після випуску чипа»",
              11.5, GREY, "middle", style="italic")
    steps = [
        ("PROM/PAL", "1970-ті", "одна матриця AND-OR; десятки вентилів; пропалюється один раз", GREY, 360),
        ("GAL", "1980-ті", "те саме, але СТИРАЄТЬСЯ (EEPROM) — можна переписати", AMBER, 300),
        ("CPLD", "кін. 1980-х", "багато PAL-блоків + матриця; сотні–тисячі вентилів; нелеткий", BLUE, 240),
        ("FPGA", "1985 →", "сітка LUT-клітинок + маршрутизація + RAM/DSP; до мільйонів LUT", GREEN, 180),
    ]
    bx = 120
    for i, (k, yr, d, col, w) in enumerate(steps):
        y = 360 - i * 64
        s += rect(bx, y, w, 50, "#fafafa", col, 1.8, 8)
        s += text(bx + 14, y + 22, k, 13, col, "start", "bold")
        s += text(bx + 14, y + 40, yr, 9.5, GREY, "start", "bold")
        s += text(bx + 96, y + 31, d, 9.8, INK, "start")
        if i < 3:
            s += arrow(bx + 20, y, bx + 20, y - 14, INK, 1.8)
    s += text(bx - 20, 120, "більше ємності й гнучкості ↑", 10.5, GREEN, "start", "bold")
    s = caption_box(s, W, [
        ("Наскрізна ідея незмінна від 1970-х: чип, чию логіку задають ПІСЛЯ виготовлення. Змінювалися лише ємність і зручність.", True),
        ("PAL і GAL досі живі для дрібної «клейової» логіки; CPLD — для невеликого керування; FPGA — коли треба багато й паралельно.", False),
    ], 392)
    save("fig-3-7-2-5-ladder.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.3 — LUT: таблиця істинності замість вентилів
# ═══════════════════════════════════════════════════════════════════════════

def fig_373_1_truth_to_lut():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Головна ідея LUT: зберегти СТОВПЕЦЬ відповідей таблиці істинності", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "будь-яку функцію задає її таблиця істинності (§3.2.1); LUT просто запам'ятовує стовпець виходів у крихітній пам'яті",
              11.5, GREY, "middle", style="italic")
    # таблиця істинності 2 входів
    s += text(200, 92, "функція F(a,b) = a XOR b", 12, INK, "middle", "bold")
    hdr = ["a", "b", "F"]
    rows = [("0", "0", "0"), ("0", "1", "1"), ("1", "0", "1"), ("1", "1", "0")]
    tx, ty = 110, 110
    for j, h in enumerate(hdr):
        s += rect(tx + j * 50, ty, 50, 26, "#eef0f4", INK, 1.3, 0)
        s += text(tx + j * 50 + 25, ty + 18, h, 12, INK, "middle", "bold")
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            col = (RED if v == "1" else BLUE) if j == 2 else INK
            bg = ("#fdf4f4" if v == "1" else "#f3f5fd") if j == 2 else "#ffffff"
            s += rect(tx + j * 50, ty + 26 + i * 30, 50, 30, bg, GREY, 1, 0)
            s += text(tx + j * 50 + 25, ty + 26 + i * 30 + 20, v, 12, col, "middle", "bold")
    s += text(tx + 125, ty + 26 + 4 * 30 + 18, "↑ цей стовпець і є «зміст» LUT", 10, GREEN, "middle", "bold")
    # стрілка
    s += arrow(290, 200, 420, 200, GREEN, 2.2)
    s += text(355, 190, "записуємо", 10, GREEN, "middle", "bold")
    # LUT = маленька пам'ять
    s += text(620, 92, "LUT-2 = пам'ять на 2² = 4 комірки", 12, GREEN, "middle", "bold")
    addrs = ["00", "01", "10", "11"]
    vals = ["0", "1", "1", "0"]
    lx, ly = 540, 110
    s += text(lx + 30, ly - 4, "адреса", 9.5, GREY, "middle", "bold")
    s += text(lx + 120, ly - 4, "біт", 9.5, GREY, "middle", "bold")
    for i, (a, v) in enumerate(zip(addrs, vals)):
        s += rect(lx, ly + i * 34, 60, 30, "#ffffff", GREY, 1.2, 4)
        s += text(lx + 30, ly + i * 34 + 20, a, 11, INK, "middle", "bold")
        col = RED if v == "1" else BLUE
        s += rect(lx + 90, ly + i * 34, 60, 30, "#fdf4f4" if v == "1" else "#f3f5fd", col, 1.4, 4)
        s += text(lx + 120, ly + i * 34 + 20, v, 12, col, "middle", "bold")
    s += text(lx + 75, ly + 4 * 34 + 18, "входи (a,b) = АДРЕСА у цю пам'ять", 9.5, INK, "middle", "bold")
    s = caption_box(s, W, [
        ("LUT (look-up table) не «обчислює» функцію вентилями — він ЗБЕРІГАЄ її таблицю істинності й читає готову відповідь.", True),
        ("Входи функції стають адресою в крихітну пам'ять; вихід — це біт, що там лежить. Логіка перетворилась на читання з пам'яті.", False),
    ], 396)
    save("fig-3-7-3-1-truth-to-lut.svg", s)


def fig_373_2_mux_tree():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Як LUT влаштований усередині: SRAM-біти + дерево мультиплексорів", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "входи керують мультиплексорами (§3.2.6), що обирають один із збережених бітів — це і є «читання за адресою»",
              11.5, GREY, "middle", style="italic")
    # 4 SRAM-біти зліва (для LUT-2)
    bits = ["0", "1", "1", "0"]
    bx, by = 100, 110
    for i, b in enumerate(bits):
        col = RED if b == "1" else BLUE
        s += rect(bx, by + i * 64, 56, 40, "#fdf4f4" if b == "1" else "#f3f5fd", col, 1.6, 5)
        s += text(bx + 28, by + i * 64 + 25, b, 14, col, "middle", "bold")
        s += text(bx - 8, by + i * 64 + 25, f"m{i}", 9, GREY, "end", "bold")
    s += text(bx + 28, by - 12, "SRAM-біти", 10, GREY, "middle", "bold")
    s += text(bx + 28, 430, "(завантажені бітстрімом)", 9, GREY, "middle", style="italic")
    # перший рівень мультиплексорів (керує b)
    def mux(x, y, lab):
        out = path(f"M{x},{y} L{x+34},{y+12} L{x+34},{y+44} L{x},{y+56} Z", "#fff8e8", AMBER, 1.7)
        out += text(x + 17, y + 32, lab, 8, DARKAMBER, "middle", "bold")
        return out
    m1y = [134, 262]
    for k, my in enumerate(m1y):
        s += mux(250, my, "MUX")
        s += arrow(156, by + (k * 2) * 64 + 20, 248, my + 16, GREY, 1.4)
        s += arrow(156, by + (k * 2 + 1) * 64 + 20, 248, my + 40, GREY, 1.4)
    s += text(267, 122, "обирає b", 8.5, DARKAMBER, "middle", "bold")
    s += text(267, 250, "обирає b", 8.5, DARKAMBER, "middle", "bold")
    # другий рівень (керує a)
    s += mux(420, 198, "MUX")
    s += arrow(284, 162, 418, 214, GREY, 1.4)
    s += arrow(284, 290, 418, 240, GREY, 1.4)
    s += text(437, 186, "обирає a", 8.5, DARKAMBER, "middle", "bold")
    s += arrow(454, 226, 560, 226, GREEN, 2.2)
    s += text(620, 222, "вихід F", 12, GREEN, "middle", "bold")
    s += text(620, 244, "= обраний біт", 9.5, GREY, "middle")
    # входи-керування
    s += arrow(300, 380, 300, 320, BLUE, 1.8)
    s += text(300, 396, "вхід b", 10, BLUE, "middle", "bold")
    s += arrow(437, 320, 437, 256, BLUE, 1.8)
    s += text(437, 336, "вхід a", 10, BLUE, "middle", "bold")
    s = caption_box(s, W, [
        ("LUT — це маленька SRAM (її біти заливає бітстрім, §3.7.6) плюс дерево мультиплексорів, кероване входами.", True),
        ("Входи a,b обирають шлях крізь дерево до ОДНОГО біта — змінив зміст SRAM і та сама схема рахує вже іншу функцію.", False),
    ], 396)
    save("fig-3-7-3-2-mux-tree.svg", s)


def fig_373_3_any_function():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому 4-входова LUT реалізує БУДЬ-ЯКУ функцію 4 змінних", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у функції 4 змінних рівно 2⁴ = 16 рядків таблиці; LUT-4 має рівно 16 бітів — по біту на рядок",
              11.5, GREY, "middle", style="italic")
    s += rect(80, 92, 330, 250, "#eef7ee", GREEN, 1.8, 12)
    s += text(245, 118, "LUT-4 = 16 комірок SRAM", 12.5, GREEN, "middle", "bold")
    # 4x4 сітка бітів
    gx, gy = 150, 140
    pattern = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
    for i in range(16):
        r, c = i // 4, i % 4
        x, y = gx + c * 48, gy + r * 38
        b = pattern[i]
        col = RED if b else BLUE
        s += rect(x, y, 40, 30, "#fdf4f4" if b else "#f3f5fd", col, 1.4, 4)
        s += text(x + 20, y + 20, str(b), 11, col, "middle", "bold")
    s += text(245, 312, "будь-який із 2¹⁶ візерунків бітів", 10, INK, "middle", "bold")
    s += text(245, 330, "= будь-яка з 2¹⁶ функцій 4 змінних", 10, GREEN, "middle", "bold")
    # пояснення праворуч
    s += rect(450, 92, 380, 250, "#fbfbfb", INK, 1.5, 12)
    s += text(640, 118, "Ключ — відповідність ОДИН-В-ОДИН", 11.5, INK, "middle", "bold")
    pts = [
        "• функція 4 змінних = таблиця з 2⁴ = 16 рядків",
        "• кожен рядок дає 0 або 1 на виході",
        "• LUT-4 зберігає рівно 16 бітів — по біту на рядок",
        "• який завгодно набір 16 бітів задає LUT",
        "• отже, будь-яка з 2¹⁶ = 65 536 функцій — реальна",
        "",
        "AND, OR, XOR, мажоритар, дешифратор —",
        "усе це лише різні 16-бітні візерунки в тій",
        "самій LUT. Схема одна, зміст різний.",
    ]
    for i, t in enumerate(pts):
        col = GREEN if i == 4 else INK
        s += text(470, 146 + i * 21, t, 10.2, col, "start", "bold" if i in (4,) else "normal")
    s = caption_box(s, W, [
        ("LUT універсальна не дивом, а арифметикою: 16 рядків таблиці ↔ 16 бітів пам'яті, будь-який візерунок дозволено.", True),
    ], 360)
    save("fig-3-7-3-3-any-function.svg", s)


def fig_373_4_lut_vs_gates():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Та сама клітинка — різні функції: гнучкість замість фіксованих вентилів", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "у звичайній логіці кожна функція — свій набір вентилів; у LUT функцію міняє лише зміст пам'яті",
              11.5, GREY, "middle", style="italic")
    funcs = [
        ("AND", "0001", "1 лише коли всі входи 1"),
        ("OR", "0111", "1 коли хоч один вхід 1"),
        ("XOR", "0110", "1 коли входи різні"),
        ("F = ab̄+c", "1011", "довільна суміш — теж легко"),
    ]
    for i, (nm, bits, d) in enumerate(funcs):
        x = 70 + i * 200
        s += rect(x, 92, 180, 200, "#fafafa", GREEN, 1.7, 10)
        s += text(x + 90, 118, nm, 13, GREEN, "middle", "bold")
        s += text(x + 90, 140, "та сама LUT-2", 9, GREY, "middle", style="italic")
        # 4 біти змісту
        for j, b in enumerate(bits):
            bx = x + 36 + j * 28
            col = RED if b == "1" else BLUE
            s += rect(bx, 154, 24, 30, "#fdf4f4" if b == "1" else "#f3f5fd", col, 1.3, 4)
            s += text(bx + 12, 174, b, 11, col, "middle", "bold")
        s += text(x + 90, 204, "зміст: " + bits, 10, INK, "middle", "bold")
        for k, ln in enumerate(_wrap(d, 22)):
            s += text(x + 90, 230 + k * 16, ln, 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Жодного перепаювання: щоб AND став XOR, достатньо залити інші чотири біти в ту саму LUT.", True),
        ("Ось чому FPGA «програмована»: схему задає не залізо, а вміст тисяч таких таблиць (плюс маршрутизація, §3.7.4).", False),
    ], 360)
    save("fig-3-7-3-4-lut-vs-gates.svg", s)


def fig_373_5_lut_size():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Скільки коштує LUT: біти ростуть як 2ⁿ, функції — як 2 у степені 2ⁿ", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен доданий вхід ПОДВОЮЄ кількість бітів пам'яті у LUT — тому реальні LUT мають лише 4–6 входів",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("LUT-2", "2² = 4", "2⁴ = 16", "дрібно", BLUE),
        ("LUT-4", "2⁴ = 16", "2¹⁶ ≈ 65 тис.", "класика 1990-х", GREEN),
        ("LUT-6", "2⁶ = 64", "2⁶⁴ ≈ 1.8·10¹⁹", "сучасні FPGA", GREEN),
        ("LUT-8", "2⁸ = 256", "2²⁵⁶ — астрономія", "надто дорого", RED),
    ]
    y0 = 96
    s += text(150, y0 - 6, "LUT", 10.5, GREY, "start", "bold")
    s += text(330, y0 - 6, "бітів пам'яті", 10.5, GREY, "middle", "bold")
    s += text(560, y0 - 6, "скільки функцій уміщує", 10.5, GREY, "middle", "bold")
    for i, (k, b, f, note, col) in enumerate(rows):
        y = y0 + i * 58
        s += rect(120, y, 120, 46, "#fafafa", col, 1.7, 8)
        s += text(180, y + 29, k, 12.5, col, "middle", "bold")
        s += rect(260, y, 150, 46, "#ffffff", col, 1.2, 8)
        s += text(335, y + 29, b, 12, INK, "middle", "bold")
        s += rect(430, y, 230, 46, "#ffffff", col, 1.2, 8)
        s += text(545, y + 29, f, 11.5, INK, "middle", "bold")
        s += text(690, y + 29, note, 10.5, col, "start", "bold")
    s = caption_box(s, W, [
        ("Більша LUT уміщує складнішу функцію без додаткових клітинок — але її пам'ять росте як 2ⁿ, тож вісім входів уже непідйомні.", True),
        ("Компроміс осів на 4–6 входах: достатньо, щоб ловити типові шматки логіки, і ще дешево. Деталі — у вставці 🧮 до §3.7.3.", False),
    ], 360)
    save("fig-3-7-3-5-lut-size.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.4 — Усередині FPGA: логічні блоки, маршрутизація, BRAM, DSP
# ═══════════════════════════════════════════════════════════════════════════

def fig_374_1_logic_cell():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Базова клітинка FPGA: LUT + тригер (плюс трохи обв'язки)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "LUT рахує комбінаційну функцію (§3.7.3), тригер (§3.3.3) зберігає її результат до наступного такту",
              11.5, GREY, "middle", style="italic")
    # входи
    for i in range(4):
        y = 120 + i * 30
        s += arrow(70, y, 150, y, BLUE, 1.8)
        s += text(60, y + 4, f"in{i}", 10, BLUE, "end", "bold")
    s += _lut(150, 120, 110, 110, "4")
    s += text(205, 250, "будь-яка функція 4 входів", 9.5, GREEN, "middle", style="italic")
    s += arrow(260, 175, 330, 175, INK, 2)
    s += text(295, 165, "комб.", 8.5, GREY, "middle")
    # мультиплексор вибору
    s += path("M330,150 L368,162 L368,188 L330,200 Z", "#fff8e8", AMBER, 1.7)
    s += text(349, 178, "MUX", 8.5, DARKAMBER, "middle", "bold")
    # тригер
    s += _ff(410, 152, 56, 50, BLUE, "DFF")
    s += arrow(368, 175, 408, 175, INK, 1.8)
    s += text(438, 218, "тригер", 9.5, BLUE, "middle", "bold")
    # вибір рег/комб обхід
    s += polyline([(349, 162), (349, 100), (520, 100)], GREY, 1.5, "4 3")
    s += text(440, 92, "обхід тригера (комбінаційний вихід)", 9, GREY, "middle", style="italic")
    s += arrow(466, 175, 540, 175, GREEN, 2)
    s += path("M540,150 L578,162 L578,188 L540,200 Z", "#fff8e8", AMBER, 1.7)
    s += text(559, 178, "MUX", 8.5, DARKAMBER, "middle", "bold")
    s += arrow(578, 175, 650, 175, GREEN, 2)
    s += text(700, 178, "вихід клітинки", 10.5, INK, "middle", "bold")
    # такт
    s += arrow(438, 260, 438, 204, RED, 1.8)
    s += text(438, 276, "такт (clk)", 9.5, RED, "middle", "bold")
    s = caption_box(s, W, [
        ("Логічна клітинка поєднує дві речі, які ми вже знаємо: LUT для функції (§3.7.3) і тригер для стану (§3.3.3).", True),
        ("Мультиплексор обирає, віддати комбінаційний результат чи його зафіксовану тактом копію. З таких клітинок складено всю FPGA.", False),
    ], 344)
    save("fig-3-7-4-1-logic-cell.svg", s)


def fig_374_2_clb_cluster():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Клітинки збирають у блоки (CLB/LAB), а ті — у регулярну сітку", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кілька LUT-тригерних клітинок ділять спільні лінії переносу й локальні зв'язки — це логічний блок",
              11.5, GREY, "middle", style="italic")
    # один CLB зблизька
    s += rect(80, 90, 280, 250, "#fbfbfb", GREEN, 1.8, 12)
    s += text(220, 114, "логічний блок (CLB / LAB)", 12, GREEN, "middle", "bold")
    for i in range(4):
        y = 130 + i * 50
        s += _cell(110, y, 110, 42, hl=(i == 0))
        s += text(245, y + 26, f"клітинка {i+1}", 9, INK, "start")
    s += polyline([(95, 130), (95, 322)], RED, 2)
    s += text(76, 230, "ланцюг", 9, RED, "middle", "bold")
    s += text(76, 244, "переносу", 9, RED, "middle", "bold")
    s += text(220, 332, "спільні швидкі лінії всередині блока", 9, GREY, "middle", style="italic")
    # сітка блоків праворуч
    s += text(640, 114, "уся мікросхема — сітка таких блоків", 11.5, GREEN, "middle", "bold")
    gx, gy, st = 470, 140, 64
    for r in range(3):
        for c in range(5):
            x, y = gx + c * st, gy + r * st
            s += rect(x, y, 44, 44, "#eef7ee", GREEN, 1.4, 5)
            s += text(x + 22, y + 27, "CLB", 8.5, GREEN, "middle", "bold")
            if c < 4:
                s += line(x + 44, y + 22, x + st, y + 22, FAINT, 1.4)
            if r < 2:
                s += line(x + 22, y + 44, x + 22, y + st, FAINT, 1.4)
    s += text(640, 350, "між блоками — програмована маршрутизація (далі)", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Окрема клітинка дрібна, тож їх групують у логічні блоки (CLB у Xilinx, LAB в Altera) зі спільними швидкими лініями переносу.", True),
        ("Блоки викладені регулярною сіткою по всьому кристалу — однорідне «полотно» логіки, яке лишилось тільки з'єднати.", False),
    ], 344)
    save("fig-3-7-4-2-clb-cluster.svg", s)


def fig_374_3_routing():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Програмована маршрутизація: канали проводів і комутаційні матриці", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "між блоками тягнуться дроти; на перетинах сидять перемикачі, що з'єднують відрізки потрібним чином",
              11.5, GREY, "middle", style="italic")
    gx, gy, st = 120, 96, 116
    # канали проводів (горизонт/вертикаль) — під блоками
    for c in range(3):
        x = gx + c * st
        for k in range(3):
            s += line(x + k * 7, gy - 8, x + k * 7, gy + 2 * st + 8, FAINT, 1.3)
    for r in range(3):
        y = gy + r * st
        for k in range(3):
            s += line(gx - 8, y + k * 7, gx + 2 * st + 8, y + k * 7, FAINT, 1.3)
    # логічні блоки (між каналами)
    for r in range(2):
        for c in range(2):
            x, y = gx + c * st + 26, gy + r * st + 26
            s += rect(x, y, 64, 64, "#eef7ee", GREEN, 1.7, 6)
            s += text(x + 32, y + 37, "CLB", 10, GREEN, "middle", "bold")
    # комутаційні матриці на перетинах
    for r in range(3):
        for c in range(3):
            x, y = gx + c * st, gy + r * st
            s += rect(x - 6, y - 6, 26, 26, "#fff8e8", AMBER, 1.6, 4)
            s += text(x + 7, y + 11, "×", 12, DARKAMBER, "middle", "bold")
    # підсвічений маршрут (з верхнього лівого блока у нижній правий)
    routex = gx + 7
    s += line(routex, gy + 30, routex, gy + st, RED, 3)
    s += line(routex, gy + st, gx + st + 7, gy + st, RED, 3)
    s += line(gx + st + 7, gy + st, gx + st + 7, gy + st + 30, RED, 3)
    # пояснення праворуч
    lx = gx + 2 * st + 40
    s += text(lx, gy + 30, "комутаційна матриця", 11, DARKAMBER, "start", "bold")
    s += text(lx, gy + 47, "(switch box):", 11, DARKAMBER, "start", "bold")
    s += text(lx, gy + 67, "перемикачі з'єднують", 9.5, GREY, "start")
    s += text(lx, gy + 83, "відрізки дротів у", 9.5, GREY, "start")
    s += text(lx, gy + 99, "потрібний шлях", 9.5, GREY, "start")
    s += text(lx, gy + 138, "зелене — логіка (CLB)", 10, GREEN, "start", "bold")
    s += text(lx, gy + 170, "сіре — канали проводів", 10, GREY, "start", "bold")
    s += text(lx, gy + 202, "червоне — один реальний", 10, RED, "start", "bold")
    s += text(lx, gy + 218, "зв'язок між двома блоками", 9.5, RED, "start")
    s = caption_box(s, W, [
        ("Логіка — лише пів-FPGA; друга половина — МАРШРУТИЗАЦІЯ: канали проводів і програмовані перемикачі на перетинах.", True),
        ("Саме перемикачі вирішують, який вихід куди йде. На великих чипах маршрутизація займає більше площі, ніж сама логіка.", False),
    ], 366)
    save("fig-3-7-4-3-routing.svg", s)


def fig_374_4_island():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "«Острівна» структура: логіка в морі проводів, по краях — введення-виведення", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "класичний острівний (island-style) план: блоки логіки оточені каналами маршрутизації, периметр — піни I/O",
              11.5, GREY, "middle", style="italic")
    # рамка вводу-виводу
    s += rect(110, 86, 540, 250, "#fbfbfb", INK, 1.4, 10)
    # пади I/O по периметру
    for c in range(8):
        x = 140 + c * 64
        s += rect(x, 90, 30, 14, "#f3f5fd", BLUE, 1.2, 3)
        s += rect(x, 318, 30, 14, "#f3f5fd", BLUE, 1.2, 3)
    for r in range(4):
        y = 120 + r * 54
        s += rect(114, y, 14, 26, "#f3f5fd", BLUE, 1.2, 3)
        s += rect(632, y, 14, 26, "#f3f5fd", BLUE, 1.2, 3)
    s += text(380, 80, "піни вводу-виводу по периметру", 10, BLUE, "middle", "bold")
    # острови логіки
    gx, gy, st = 170, 130, 92
    for r in range(2):
        for c in range(5):
            x, y = gx + c * st, gy + r * st
            s += rect(x, y, 50, 50, "#eef7ee", GREEN, 1.5, 5)
            s += text(x + 25, y + 30, "CLB", 9, GREEN, "middle", "bold")
    # канали між островами
    for r in range(2):
        for c in range(4):
            x = gx + 50 + c * st
            y = gy + r * st
            for k in range(2):
                s += line(x + k * 6, y - 6, x + k * 6, y + 56, FAINT, 1.2)
    s += text(380, 354, "острови = логіка; проміжки = маршрутизація", 9.5, GREY, "middle", style="italic")
    # підпис праворуч
    s += text(700, 130, "Три «шари»:", 11.5, INK, "start", "bold")
    for i, (t, col) in enumerate([("• логічні блоки (острови)", GREEN),
                                  ("• канали проводів (море)", GREY),
                                  ("• кільце I/O (береги)", BLUE)]):
        s += text(670, 156 + i * 24, t, 10, col, "start", "bold")
    s += text(670, 240, "Спеціальні блоки (RAM,", 9.5, INK, "start")
    s += text(670, 256, "DSP) вставлені стовпцями", 9.5, INK, "start")
    s += text(670, 272, "просто серед островів — далі.", 9.5, INK, "start")
    s = caption_box(s, W, [
        ("Острівний план — канон FPGA: однорідні острови логіки в морі програмованих проводів, по берегах — піни I/O.", True),
    ], 364)
    save("fig-3-7-4-4-island.svg", s)


def fig_374_5_bram():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Блочна пам'ять (BRAM): готові кілобіти RAM просто у тканині", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "тримати буфери на самих тригерах марнотратно; тому в чип вбудовано стовпці справжніх блоків RAM",
              11.5, GREY, "middle", style="italic")
    # ліворуч — погано: на тригерах
    s += rect(70, 92, 360, 220, "#fdf6f6", RED, 1.7, 12)
    s += text(250, 116, "буфер на тригерах клітинок", 12, RED, "middle", "bold")
    for i in range(4):
        for j in range(8):
            s += rect(110 + j * 30, 140 + i * 30, 22, 22, "#f3f5fd", BLUE, 1, 3)
    s += text(250, 290, "1 тригер = 1 біт → з'їдає тисячі клітинок", 10, RED, "middle", "bold")
    s += text(250, 306, "(дорого, і логіки не лишається)", 9.5, GREY, "middle", style="italic")
    # праворуч — добре: BRAM
    s += rect(470, 92, 360, 220, "#eef7ee", GREEN, 1.8, 12)
    s += text(650, 116, "блочна RAM (BRAM)", 12, GREEN, "middle", "bold")
    s += rect(540, 140, 220, 110, "#ffffff", GREEN, 1.8, 8)
    s += text(650, 168, "напр. 18–36 кбіт", 11, INK, "middle", "bold")
    s += text(650, 190, "один компактний блок", 10, GREEN, "middle", "bold")
    s += text(650, 214, "два порти: чит.+зап.", 9.5, GREY, "middle")
    s += text(650, 232, "одночасно й незалежно", 9.5, GREY, "middle")
    s += arrow(520, 165, 538, 165, BLUE, 1.8)
    s += text(508, 168, "A", 9, BLUE, "end", "bold")
    s += arrow(762, 225, 782, 225, GREEN, 1.8)
    s += text(792, 228, "B", 9, GREEN, "start", "bold")
    s += text(650, 296, "десятки–тисячі таких блоків розкидані стовпцями", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Робити пам'ять із тригерів логічних клітинок — розкіш: біт на клітинку. Тому FPGA має вбудовані блоки RAM (BRAM).", True),
        ("Це готові кілобіти з двома незалежними портами — ідеальні під буфери, черги (FIFO) й таблиці; логіку вони не з'їдають.", False),
    ], 348)
    save("fig-3-7-4-5-bram.svg", s)


def fig_374_6_dsp():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "DSP-блоки: апаратні множники-суматори для важкої арифметики", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "множення на LUT громіздке; тому в чип вбудовано готові блоки «помножити й додати» (MAC)",
              11.5, GREY, "middle", style="italic")
    # DSP-блок
    s += rect(280, 100, 340, 150, "#fff8e8", AMBER, 2, 12)
    s += text(450, 124, "DSP-блок (MAC)", 13, DARKAMBER, "middle", "bold")
    # множник
    s += circle(370, 175, 26, "#ffffff", AMBER, 1.8)
    s += text(370, 181, "×", 18, DARKAMBER, "middle", "bold")
    s += arrow(296, 160, 344, 168, BLUE, 1.8)
    s += text(286, 158, "A", 10, BLUE, "end", "bold")
    s += arrow(296, 196, 344, 184, BLUE, 1.8)
    s += text(286, 198, "B", 10, BLUE, "end", "bold")
    # суматор
    s += arrow(396, 175, 444, 175, INK, 1.8)
    s += circle(470, 175, 24, "#ffffff", AMBER, 1.8)
    s += text(470, 181, "+", 18, DARKAMBER, "middle", "bold")
    s += arrow(470, 232, 470, 200, GREEN, 1.8)
    s += text(470, 248, "акумулятор", 9, GREEN, "middle", "bold")
    s += arrow(494, 175, 600, 175, GREEN, 2.2)
    s += text(640, 178, "A×B + сума", 10.5, INK, "middle", "bold")
    s += text(450, 280, "усе це — один такт, у спеціальному блоці, а не на десятках LUT", 10, DARKAMBER, "middle", "bold")
    s += text(450, 300, "сотні–тисячі DSP-блоків працюють паралельно — звідси сила FPGA у фільтрах і нейромережах", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Множення-з-накопиченням (A×B+сума) — серце обробки сигналу; складати його з LUT і дорого, і повільно.", True),
        ("Тому FPGA несе сотні готових DSP-блоків. BRAM і DSP — це «спеціалізовані острови», вкраплені в однорідну логіку.", False),
    ], 348)
    save("fig-3-7-4-6-dsp.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.5 — HDL: описуємо залізо, а не пишемо програму
# ═══════════════════════════════════════════════════════════════════════════

def fig_375_1_describe_vs_program():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Головний злам у голові: HDL ОПИСУЄ схему, а не задає кроки", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "програма для процесора — це послідовність дій у часі; код HDL — це креслення залізяки, що існує цілком одразу",
              11.5, GREY, "middle", style="italic")
    # ліворуч — програма
    s += rect(70, 90, 360, 240, "#f3f5fd", BLUE, 2, 12)
    s += text(250, 114, "ПРОГРАМА (C для МК)", 12.5, BLUE, "middle", "bold")
    lines = ["a = read();", "b = read();", "c = a + b;", "write(c);"]
    for i, t in enumerate(lines):
        s += rect(110, 134 + i * 38, 280, 30, "#ffffff", BLUE, 1.2, 5)
        s += text(124, 154 + i * 38, t, 11, INK, "start")
        if i < 3:
            s += arrow(250, 164 + i * 38, 250, 172 + i * 38, BLUE, 1.6)
    s += text(250, 304, "виконується ПО ЧЕРЗІ, рядок за рядком у часі", 9.5, BLUE, "middle", "bold")
    # праворуч — опис заліза
    s += rect(470, 90, 360, 240, "#eef7ee", GREEN, 2, 12)
    s += text(650, 114, "ОПИС ЗАЛІЗА (Verilog)", 12.5, GREEN, "middle", "bold")
    s += text(650, 136, "assign c = a + b;", 11, INK, "middle", "bold")
    # фізичний суматор
    s += rect(540, 150, 70, 40, "#ffffff", BLUE, 1.5, 5)
    s += text(575, 175, "a", 11, BLUE, "middle", "bold")
    s += rect(540, 200, 70, 40, "#ffffff", BLUE, 1.5, 5)
    s += text(575, 225, "b", 11, BLUE, "middle", "bold")
    s += arrow(610, 170, 660, 188, INK, 1.8)
    s += arrow(610, 220, 660, 202, INK, 1.8)
    s += circle(688, 195, 26, "#fff8e8", AMBER, 1.8)
    s += text(688, 201, "+", 16, DARKAMBER, "middle", "bold")
    s += arrow(714, 195, 770, 195, GREEN, 2)
    s += text(760, 178, "c", 11, GREEN, "middle", "bold")
    s += text(650, 286, "існує ЦІЛКОМ і ВОДНОЧАС — це фізичний суматор", 9.5, GREEN, "middle", "bold")
    s += text(650, 304, "(рядок не «виконується» — він описує дроти й вентилі)", 9, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Та сама на вигляд стрічка означає різне: у C це КРОК, який колись виконається; у Verilog це ОПИС постійно існуючого суматора.", True),
        ("HDL (hardware description language) не програмують — ним КРЕСЛЯТЬ залізо. Усі рядки «працюють» одночасно, бо це й є схема.", False),
    ], 348)
    save("fig-3-7-5-1-describe-vs-program.svg", s)


def fig_375_2_module():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Будівельний блок Verilog: модуль як «чорна скринька» з виводами", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "module оголошує входи/виходи (ніби корпус мікросхеми), а тіло описує, що всередині",
              11.5, GREY, "middle", style="italic")
    # код ліворуч
    s += rect(60, 90, 380, 250, "#fbfbfb", INK, 1.5, 10)
    code = [
        ("module adder(", INK),
        ("  input  [7:0] a,", BLUE),
        ("  input  [7:0] b,", BLUE),
        ("  output [8:0] sum", GREEN),
        (");", INK),
        ("  assign sum = a + b;", DARKAMBER),
        ("endmodule", INK),
    ]
    for i, (t, col) in enumerate(code):
        s += text(80, 122 + i * 30, t, 12, col, "start", "bold" if col != INK else "normal")
    s += text(250, 330, "оголошення виводів + тіло (логіка)", 9.5, GREY, "middle", style="italic")
    # схема праворуч
    s += rect(560, 120, 220, 160, "#eef7ee", GREEN, 2, 12)
    s += text(670, 110, "що це означає фізично:", 10.5, GREEN, "middle", "bold")
    s += text(670, 200, "adder", 14, GREEN, "middle", "bold")
    s += text(670, 222, "(8-бітний суматор)", 9.5, GREY, "middle")
    s += arrow(500, 160, 558, 160, BLUE, 2)
    s += text(490, 163, "a[7:0]", 10, BLUE, "end", "bold")
    s += arrow(500, 240, 558, 240, BLUE, 2)
    s += text(490, 243, "b[7:0]", 10, BLUE, "end", "bold")
    s += arrow(782, 200, 840, 200, GREEN, 2)
    s += text(850, 203, "sum[8:0]", 10, GREEN, "start", "bold")
    s += text(670, 300, "input/output = ніжки корпусу", 9, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Модуль — основна одиниця опису: рядок input/output задає його «ніжки», а тіло — внутрішню схему.", True),
        ("[7:0] означає 8-бітну шину (§3.4.7). Модулі вкладають один в одного, як корпуси на платі — так будують велику систему.", False),
    ], 360)
    save("fig-3-7-5-2-module.svg", s)


def fig_375_3_comb_vs_seq():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Два роди опису: комбінаційний (без такту) і реєстровий (по такту)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "assign описує чисту логіку, що міняється миттєво; always @(posedge clk) описує тригери, що ловлять фронт (§3.3.4)",
              11.5, GREY, "middle", style="italic")
    # ліворуч — комбінаційний
    s += rect(70, 90, 360, 250, "#eef7ee", GREEN, 1.9, 12)
    s += text(250, 114, "КОМБІНАЦІЙНИЙ", 12.5, GREEN, "middle", "bold")
    s += text(250, 136, "assign y = a & b;", 11, INK, "middle", "bold")
    s += rect(150, 156, 200, 60, "#ffffff", GREEN, 1.6, 8)
    s += text(250, 192, "вентиль AND", 11, GREEN, "middle", "bold")
    s += text(250, 240, "виходить ЛИШЕ з входів,", 10, INK, "middle", "bold")
    s += text(250, 258, "міняється МИТТЄВО за ними", 10, INK, "middle", "bold")
    s += text(250, 282, "→ дроти й вентилі (§3.2)", 9.5, GREEN, "middle", "bold")
    s += text(250, 302, "немає пам'яті, немає такту", 9.5, GREY, "middle", style="italic")
    # праворуч — реєстровий
    s += rect(470, 90, 360, 250, "#f3f5fd", BLUE, 1.9, 12)
    s += text(650, 114, "РЕЄСТРОВИЙ (по такту)", 12.5, BLUE, "middle", "bold")
    s += text(650, 136, "always @(posedge clk)", 10.5, INK, "middle", "bold")
    s += text(650, 154, "  q <= d;", 11, INK, "middle", "bold")
    s += _ff(590, 174, 120, 60, BLUE, "D    Q")
    s += text(650, 252, "значення ОНОВЛЮЄТЬСЯ лише", 10, INK, "middle", "bold")
    s += text(650, 270, "на фронті такту (§3.3.4)", 10, INK, "middle", "bold")
    s += text(650, 294, "→ тригери, регістри (§3.3.5)", 9.5, BLUE, "middle", "bold")
    s += text(650, 314, "має пам'ять стану", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Це не «стилі коду», а два різні роди заліза: assign дає комбінаційну логіку (§3.2), always @(posedge clk) — тригери (§3.3).", True),
        ("Розрізняти їх критично: написане під такт стане регістром, а решта — мережею вентилів, що відгукується миттєво.", False),
    ], 360)
    save("fig-3-7-5-3-comb-vs-seq.svg", s)


def fig_375_4_synth_not_exec():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Синтез ≠ виконання: код не «біжить», його ПЕРЕТВОРЮЮТЬ на схему", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "компілятор C дає інструкції, які процесор виконає; синтезатор HDL дає СХЕМУ, яку залізо втілить",
              11.5, GREY, "middle", style="italic")
    # верхня доріжка — софт
    s += rect(70, 90, 200, 70, "#f3f5fd", BLUE, 1.7, 10)
    s += text(170, 120, "код C", 12, BLUE, "middle", "bold")
    s += text(170, 140, "for, if, a+b", 9.5, GREY, "middle")
    s += arrow(270, 125, 360, 125, BLUE, 2)
    s += text(315, 113, "компілятор", 9, BLUE, "middle", "bold")
    s += rect(360, 90, 200, 70, "#f3f5fd", BLUE, 1.7, 10)
    s += text(460, 120, "інструкції", 12, BLUE, "middle", "bold")
    s += text(460, 140, "LD, ADD, ST", 9.5, GREY, "middle")
    s += arrow(560, 125, 650, 125, BLUE, 2)
    s += text(605, 113, "виконує", 9, BLUE, "middle", "bold")
    s += rect(650, 90, 180, 70, "#f3f5fd", BLUE, 1.7, 10)
    s += text(740, 120, "процесор", 12, BLUE, "middle", "bold")
    s += text(740, 140, "крок за кроком", 9, GREY, "middle")
    # нижня доріжка — HDL
    s += rect(70, 220, 200, 70, "#eef7ee", GREEN, 1.7, 10)
    s += text(170, 250, "код Verilog", 12, GREEN, "middle", "bold")
    s += text(170, 270, "assign, always", 9.5, GREY, "middle")
    s += arrow(270, 255, 360, 255, GREEN, 2)
    s += text(315, 243, "СИНТЕЗ", 9, GREEN, "middle", "bold")
    s += rect(360, 220, 200, 70, "#eef7ee", GREEN, 1.7, 10)
    s += text(460, 250, "схема (вентилі,", 11, GREEN, "middle", "bold")
    s += text(460, 270, "тригери, дроти)", 11, GREEN, "middle", "bold")
    s += arrow(560, 255, 650, 255, GREEN, 2)
    s += text(605, 243, "втілює", 9, GREEN, "middle", "bold")
    s += rect(650, 220, 180, 70, "#eef7ee", GREEN, 1.7, 10)
    s += text(740, 250, "тканина FPGA", 11, GREEN, "middle", "bold")
    s += text(740, 270, "усе нараз", 9, GREY, "middle")
    s += text(W / 2, 192, "однакові на вигляд мови — геть різна доля коду", 11, INK, "middle", "bold")
    s = caption_box(s, W, [
        ("Софт: компілятор перекладає код на ІНСТРУКЦІЇ, процесор їх виконує в часі. HDL: синтезатор перекладає код на СХЕМУ.", True),
        ("Тому «оптимізація швидкості» в HDL — це не менше команд, а коротший КРИТИЧНИЙ ШЛЯХ у схемі (§3.7.7).", False),
    ], 348)
    save("fig-3-7-5-4-synth-not-exec.svg", s)


def fig_375_5_same_code_diff_hw():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Те саме «c = a + b» розгортається в різне залізо за контекстом", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "синтезатор дивиться, скільки разів і де потрібна операція, і будує стільки заліза, скільки треба",
              11.5, GREY, "middle", style="italic")
    # один суматор
    s += rect(70, 92, 250, 210, "#fbfbfb", GREEN, 1.7, 10)
    s += text(195, 116, "один assign", 12, GREEN, "middle", "bold")
    s += circle(195, 190, 30, "#fff8e8", AMBER, 1.8)
    s += text(195, 197, "+", 18, DARKAMBER, "middle", "bold")
    s += text(195, 250, "→ ОДИН суматор", 10.5, INK, "middle", "bold")
    s += text(195, 272, "у залізі", 9.5, GREY, "middle")
    # цикл/масив -> багато суматорів
    s += rect(340, 92, 250, 210, "#fbfbfb", GREEN, 1.7, 10)
    s += text(465, 116, "той самий вираз ×8", 12, GREEN, "middle", "bold")
    for i in range(8):
        x = 360 + (i % 4) * 56
        y = 150 + (i // 4) * 60
        s += circle(x + 20, y, 18, "#fff8e8", AMBER, 1.5)
        s += text(x + 20, y + 5, "+", 12, DARKAMBER, "middle", "bold")
    s += text(465, 272, "→ ВІСІМ суматорів паралельно", 10, INK, "middle", "bold")
    # під такт -> регістр+суматор
    s += rect(610, 92, 240, 210, "#fbfbfb", GREEN, 1.7, 10)
    s += text(730, 116, "у always @clk", 12, GREEN, "middle", "bold")
    s += circle(700, 175, 22, "#fff8e8", AMBER, 1.6)
    s += text(700, 181, "+", 14, DARKAMBER, "middle", "bold")
    s += arrow(722, 175, 752, 175, INK, 1.6)
    s += _ff(752, 153, 44, 44, BLUE, "REG")
    s += text(730, 250, "→ суматор + РЕГІСТР", 10, INK, "middle", "bold")
    s += text(730, 272, "(результат фіксується тактом)", 9, GREY, "middle")
    s = caption_box(s, W, [
        ("HDL описує НАМІР, а скільки заліза з нього виросте — вирішує контекст: один вираз, вісім копій чи вираз під тактом.", True),
        ("Звідси й сила, і пастка: необережний опис легко «намножить» десятки суматорів або породить небажаний регістр.", False),
    ], 348)
    save("fig-3-7-5-5-same-code-diff-hw.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.6 — Потік розробки: синтез → розміщення → трасування → бітстрім
# ═══════════════════════════════════════════════════════════════════════════

def fig_376_1_flow():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Шлях від коду до працюючого чипа: чотири головні кроки", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "інструменти крок за кроком перетворюють опис HDL на потік бітів, що налаштовує кожну клітинку й перемикач",
              11.5, GREY, "middle", style="italic")
    steps = [
        ("HDL-код", "Verilog/VHDL\n(опис схеми)", BLUE, "#f3f5fd"),
        ("СИНТЕЗ", "→ список вентилів\nі тригерів (netlist)", GREEN, "#eef7ee"),
        ("РОЗМІЩЕННЯ", "кожен елемент → у\nконкретну клітинку", AMBER, "#fff8e8"),
        ("ТРАСУВАННЯ", "прокласти дроти\nкрізь перемикачі", RED, "#fdf4f4"),
        ("БІТСТРІМ", "файл бітів для\nусіх SRAM-комірок", INK, "#f0f0f0"),
    ]
    bw = 150
    for i, (k, d, col, bg) in enumerate(steps):
        x = 40 + i * 168
        y = 110
        s += rect(x, y, bw, 90, bg, col, 1.9, 10)
        s += text(x + bw / 2, y + 28, k, 12.5, col, "middle", "bold")
        for j, ln in enumerate(d.split("\n")):
            s += text(x + bw / 2, y + 50 + j * 16, ln, 9, INK, "middle")
        if i < 4:
            s += arrow(x + bw, y + 45, x + 168, y + 45, INK, 2)
    # завантаження у чип
    s += arrow(40 + 4 * 168 + bw / 2, 200, 40 + 4 * 168 + bw / 2, 270, INK, 2)
    s += text(40 + 4 * 168 + bw / 2 + 10, 240, "завантажити", 9.5, INK, "start", "bold")
    s += rect(620, 270, 220, 90, "#eef7ee", GREEN, 2, 12)
    s += text(730, 300, "FPGA НАЛАШТОВАНА", 11.5, GREEN, "middle", "bold")
    s += text(730, 322, "клітинки й перемикачі", 9.5, INK, "middle")
    s += text(730, 340, "набули потрібного стану", 9.5, INK, "middle")
    # підпис під кроками
    s += text(W / 2, 400, "Аналогія з софтом: синтез ≈ «компіляція», а розміщення+трасування — суто апаратні кроки, яких у софті немає.", 11, INK, "middle", "bold")
    s += text(W / 2, 424, "Перші два схожі на компілятор; останні два — це фізичне «вкладання» схеми в конкретний кристал.", 10.5, GREY, "middle", style="italic")
    save("fig-3-7-6-1-flow.svg", s)


def fig_376_2_synthesis():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Синтез: від тексту HDL до списку вентилів і тригерів (netlist)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "інструмент «розуміє» опис і будує еквівалентну схему з примітивів — поки що без прив'язки до місця на чипі",
              11.5, GREY, "middle", style="italic")
    # код
    s += rect(70, 100, 240, 150, "#fbfbfb", BLUE, 1.6, 10)
    s += text(190, 124, "HDL-код", 12, BLUE, "middle", "bold")
    for i, t in enumerate(["assign y =", "  (a & b)", "  | (c & d);"]):
        s += text(90, 152 + i * 26, t, 11, INK, "start")
    s += arrow(310, 175, 380, 175, GREEN, 2.2)
    s += text(345, 163, "синтез", 9.5, GREEN, "middle", "bold")
    # netlist — схема з вентилів
    s += rect(380, 90, 450, 200, "#eef7ee", GREEN, 1.8, 10)
    s += text(605, 114, "netlist: з'єднані примітиви", 11.5, GREEN, "middle", "bold")
    # два AND і один OR
    def andg(x, y):
        out = path(f"M{x},{y} L{x},{y+44} L{x+22},{y+44} A22,22 0 0 0 {x+22},{y} Z", "#ffffff", INK, 1.6)
        out += text(x + 12, y + 28, "&", 12, INK, "middle", "bold")
        return out
    def org(x, y):
        out = path(f"M{x},{y} Q{x+14},{y+22} {x},{y+44} Q{x+30},{y+40} {x+44},{y+22} Q{x+30},{y+4} {x},{y} Z", "#ffffff", INK, 1.6)
        out += text(x + 18, y + 28, "≥1", 10, INK, "middle", "bold")
        return out
    s += andg(440, 130)
    s += text(430, 126, "a", 9, BLUE, "end")
    s += text(430, 168, "b", 9, BLUE, "end")
    s += andg(440, 200)
    s += text(430, 196, "c", 9, BLUE, "end")
    s += text(430, 238, "d", 9, BLUE, "end")
    s += org(600, 165)
    s += arrow(462, 152, 598, 178, INK, 1.5)
    s += arrow(462, 222, 598, 198, INK, 1.5)
    s += arrow(644, 187, 720, 187, GREEN, 2)
    s += text(740, 190, "y", 11, GREEN, "middle", "bold")
    s += text(605, 270, "поки що це «схема взагалі» — без місця на кристалі", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Синтез — найближче до звичної «компіляції»: текст HDL стає списком конкретних вентилів і тригерів та зв'язків між ними.", True),
        ("Він уже відкидає зайве й розпізнає, де комбінаційна логіка, а де регістр, — але ще не знає, у яку клітинку що покласти.", False),
    ], 338)
    save("fig-3-7-6-2-synthesis.svg", s)


def fig_376_3_place_route():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Розміщення й трасування: вкладаємо схему у конкретний кристал", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "розміщення обирає, в яку клітинку сяде кожен елемент; трасування прокладає між ними дроти крізь перемикачі",
              11.5, GREY, "middle", style="italic")
    # сітка клітинок
    gx, gy, st = 150, 100, 70
    occupied = {(0, 1): "A", (1, 3): "B", (2, 0): "C", (3, 2): "D"}
    for r in range(4):
        for c in range(5):
            x, y = gx + c * st, gy + r * st
            lab = occupied.get((r, c))
            if lab:
                s += rect(x, y, 44, 44, "#eef7ee", GREEN, 2, 6)
                s += text(x + 22, y + 28, lab, 12, GREEN, "middle", "bold")
            else:
                s += rect(x, y, 44, 44, "#fbfbfb", FAINT, 1.2, 6)
            if c < 4:
                s += line(x + 44, y + 22, x + st, y + 22, FAINT, 1.2)
            if r < 3:
                s += line(x + 22, y + 44, x + 22, y + st, FAINT, 1.2)
    # трасований зв'язок A->B
    ax, ay = gx + 1 * st + 44, gy + 0 * st + 22
    s += polyline([(ax, ay), (ax + 30, ay), (ax + 30, gy + 3 * st + 22), (gx + 3 * st, gy + 3 * st + 22)], RED, 3)
    s += text(640, 130, "РОЗМІЩЕННЯ:", 11.5, GREEN, "start", "bold")
    s += text(640, 152, "обрати клітинку", 10, INK, "start")
    s += text(640, 168, "для кожного A,B,C,D", 10, INK, "start")
    s += text(640, 168 + 8, "", 9, GREY)
    s += text(640, 210, "ТРАСУВАННЯ:", 11.5, RED, "start", "bold")
    s += text(640, 232, "червоне — реальний", 10, RED, "start")
    s += text(640, 248, "дріт A→B крізь", 10, RED, "start")
    s += text(640, 264, "комутаційні матриці", 10, RED, "start")
    s += text(640, 300, "мета — все вмістити", 9.5, GREY, "start", style="italic")
    s += text(640, 316, "й уложитись у таймінг", 9.5, GREY, "start", style="italic")
    s = caption_box(s, W, [
        ("Цих двох кроків у софті немає: схему треба фізично ВКЛАСТИ в кристал. Розміщення садить елементи в клітинки…", True),
        ("…а трасування з'єднує їх реальними дротами крізь перемикачі (§3.7.4). Від їх якості залежить, чи влізе дизайн і чи встигне за тактом.", False),
    ], 366)
    save("fig-3-7-6-3-place-route.svg", s)


def fig_376_4_bitstream():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Бітстрім: один великий файл, що налаштовує КОЖНУ комірку конфігурації", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "результат потоку — потік бітів; він заповнює всі SRAM-комірки LUT і всі перемикачі маршрутизації",
              11.5, GREY, "middle", style="italic")
    # потік бітів
    s += rect(70, 100, 200, 80, "#f0f0f0", INK, 1.7, 10)
    s += text(170, 130, "бітстрім", 12.5, INK, "middle", "bold")
    s += text(170, 152, "010110100…", 11, GREEN, "middle", "bold")
    s += text(170, 170, "(сотні кбіт–десятки Мбіт)", 8.5, GREY, "middle")
    s += arrow(270, 140, 360, 140, INK, 2.2)
    s += text(315, 128, "заливаємо", 9, INK, "middle", "bold")
    # чип із комірками
    s += rect(360, 92, 470, 230, "#fbfbfb", GREEN, 1.8, 12)
    s += text(595, 114, "FPGA: усі комірки конфігурації", 11.5, GREEN, "middle", "bold")
    gx, gy = 390, 130
    cnt = 0
    pattern = [1,0,1,1,0,1,0,0,1,1,0,1,1,0,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,1,0,1]
    for r in range(4):
        for c in range(8):
            x, y = gx + c * 52, gy + r * 40
            b = pattern[cnt % len(pattern)]
            cnt += 1
            col = RED if b else BLUE
            s += rect(x, y, 44, 30, "#fdf4f4" if b else "#f3f5fd", col, 1.2, 4)
            s += text(x + 22, y + 20, str(b), 11, col, "middle", "bold")
    s += text(595, 308, "кожен біт = стан однієї LUT-комірки або одного перемикача", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Бітстрім — це остаточний «образ» схеми: послідовність бітів, що задає вміст усіх LUT і положення всіх перемикачів.", True),
        ("Оскільки тканина FPGA на SRAM ЛЕТКА (§3.6.3), бітстрім зазвичай тримають у зовнішній флеші й заливають при кожному старті.", False),
    ], 366)
    save("fig-3-7-6-4-bitstream.svg", s)


def fig_376_5_config_flash():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Звідки береться конфігурація: летка тканина + зовнішня флеш-пам'ять", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "більшість FPGA забуває схему при вимкненні (SRAM), тож бітстрім вантажиться з флеші при кожному старті",
              11.5, GREY, "middle", style="italic")
    # флеш
    s += rect(90, 130, 180, 90, "#eef7ee", GREEN, 1.9, 12)
    s += text(180, 162, "флеш-пам'ять", 12, GREEN, "middle", "bold")
    s += text(180, 184, "(нелетка)", 9.5, GREY, "middle")
    s += text(180, 204, "тримає бітстрім", 9.5, INK, "middle", "bold")
    # старт
    s += arrow(270, 175, 380, 175, AMBER, 2.4)
    s += text(325, 160, "при ввімкненні", 9.5, DARKAMBER, "middle", "bold")
    s += text(325, 192, "(configuration)", 8.5, GREY, "middle", style="italic")
    # fpga
    s += rect(380, 110, 220, 130, "#f3f5fd", BLUE, 1.9, 12)
    s += text(490, 138, "FPGA", 13, BLUE, "middle", "bold")
    s += text(490, 162, "тканина на SRAM", 10, INK, "middle", "bold")
    s += text(490, 182, "ЛЕТКА — порожня", 10, RED, "middle", "bold")
    s += text(490, 200, "після вимкнення", 9.5, GREY, "middle")
    s += text(490, 222, "вантажить себе з флеші", 9.5, BLUE, "middle", "bold")
    s += arrow(600, 175, 700, 175, GREEN, 2.4)
    s += text(760, 172, "схема готова", 11, GREEN, "middle", "bold")
    s += text(760, 192, "за частки секунди", 9, GREY, "middle")
    s = caption_box(s, W, [
        ("Більшість FPGA побудована на SRAM: гнучко й безкінечно перезаписувано, але ЛЕТКО — схема зникає без живлення (§3.6.3).", True),
        ("Тому поряд кладуть малу флеш із бітстрімом, і чип «завантажує себе» при кожному ввімкненні. Окремий клас FPGA має флеш усередині.", False),
    ], 326)
    save("fig-3-7-6-5-config-flash.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.7 — Таймінг у FPGA: критичний шлях і обмеження
# ═══════════════════════════════════════════════════════════════════════════

def fig_377_1_path():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Що обмежує частоту: шлях від тригера до тригера крізь логіку", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "між двома фронтами такту сигнал має встигнути вийти з регістра, пройти логіку й усістися на вході наступного (§3.3.8)",
              11.5, GREY, "middle", style="italic")
    # тригер A
    s += _ff(90, 160, 70, 60, BLUE, "REG A")
    s += text(125, 234, "джерело", 9.5, BLUE, "middle", "bold")
    s += arrow(160, 190, 230, 190, INK, 2)
    s += text(195, 178, "t_cq", 9, GREY, "middle")
    # логіка між ними
    s += rect(230, 160, 360, 60, "#eef7ee", GREEN, 1.8, 8)
    s += text(410, 184, "комбінаційна логіка", 12, GREEN, "middle", "bold")
    s += text(410, 204, "(кілька LUT + дроти між ними)", 9, GREY, "middle")
    s += arrow(590, 190, 660, 190, INK, 2)
    s += text(625, 178, "t_logic", 9, GREY, "middle")
    # тригер B
    s += _ff(660, 160, 70, 60, BLUE, "REG B")
    s += text(695, 234, "приймач", 9.5, BLUE, "middle", "bold")
    # такт
    s += line(125, 270, 695, 270, RED, 1.6)
    s += arrow(125, 270, 125, 224, RED, 1.6)
    s += arrow(695, 270, 695, 224, RED, 1.6)
    s += text(410, 286, "спільний такт (clk): обидва тригери ловлять один фронт (§3.3.6)", 10, RED, "middle", "bold")
    s += text(410, 130, "критичний шлях = t_cq + t_logic + t_setup", 11.5, INK, "middle", "bold")
    s += text(410, 110, "(найдовший такий шлях у всьому дизайні)", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Один «крок» роботи FPGA — це політ сигналу від регістра до регістра: вийти (t_cq), пройти логіку (t_logic), устигнути (t_setup).", True),
        ("Сума цих часів на НАЙДОВШОМУ такому шляху і є критичний шлях — він диктує, наскільки коротким може бути такт.", False),
    ], 332)
    save("fig-3-7-7-1-path.svg", s)


def fig_377_2_fmax():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Від критичного шляху — до максимальної частоти Fmax", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "період такту не може бути коротшим за критичний шлях; звідси стеля частоти дизайну",
              11.5, GREY, "middle", style="italic")
    s += rect(120, 100, 660, 70, "#eef0f4", INK, 1.6, 10)
    s += text(450, 132, "T_такт  ≥  t_cq + t_logic + t_setup   =   критичний шлях", 14, INK, "middle", "bold")
    s += text(450, 154, "(інакше приймач не встигне зафіксувати правильне значення → метастабільність, §3.3.8)", 9.5, GREY, "middle", style="italic")
    s += arrow(450, 178, 450, 206, INK, 2)
    s += rect(250, 210, 400, 56, "#fff8e8", AMBER, 1.8, 10)
    s += text(450, 244, "Fmax = 1 / критичний шлях", 15, DARKAMBER, "middle", "bold")
    # приклад
    s += rect(120, 286, 660, 56, "#eef7ee", GREEN, 1.6, 10)
    s += text(450, 310, "Приклад: критичний шлях 8 нс  →  Fmax = 1 / 8нс = 125 МГц.", 12, INK, "middle", "bold")
    s += text(450, 330, "Скоротити шлях (менше логіки між регістрами) → вища Fmax. Подовжити → нижча.", 10, GREEN, "middle", "bold")
    save("fig-3-7-7-2-fmax.svg", s)


def fig_377_3_slack():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Slack: запас (або борг) часу проти заданої цілі", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "інструмент порівнює потрібний шлях із доступним періодом; різниця — slack: додатний = встигаємо, від'ємний = ні",
              11.5, GREY, "middle", style="italic")
    # ціль періоду
    Tbar = 560
    s += text(110, 110, "ціль: такт 100 МГц → період 10 нс", 11, INK, "start", "bold")
    s += line(150, 130, 150 + Tbar, 130, GREY, 2)
    s += line(150, 124, 150, 136, GREY, 2)
    s += line(150 + Tbar, 124, 150 + Tbar, 136, GREY, 2)
    s += text(150 + Tbar + 10, 134, "10 нс", 10, GREY, "start", "bold")
    # випадок A — встигаємо
    s += text(110, 175, "шлях A = 8 нс", 11, GREEN, "start", "bold")
    s += rect(150, 160, Tbar * 0.8, 26, "#eef7ee", GREEN, 1.6, 4)
    s += text(150 + Tbar * 0.8 / 2, 178, "логіка 8 нс", 9.5, GREEN, "middle", "bold")
    s += rect(150 + Tbar * 0.8, 160, Tbar * 0.2, 26, "#f0f0f0", GREY, 1.3, 4)
    s += text(150 + Tbar * 0.9, 178, "+2 нс", 9.5, GREEN, "middle", "bold")
    s += text(150 + Tbar + 10, 178, "slack = +2 нс ✓", 11, GREEN, "start", "bold")
    # випадок B — не встигаємо
    s += text(110, 245, "шлях B = 12 нс", 11, RED, "start", "bold")
    s += rect(150, 230, Tbar * 1.2, 26, "#fdf4f4", RED, 1.6, 4)
    s += text(150 + Tbar * 0.6, 248, "логіка 12 нс (задовга!)", 9.5, RED, "middle", "bold")
    s += line(150 + Tbar, 224, 150 + Tbar, 262, INK, 1.6, "3 3")
    s += text(150 + Tbar + 10, 248, "slack = −2 нс ✗", 11, RED, "start", "bold")
    s += text(450, 296, "Від'ємний slack означає: дизайн НЕ працюватиме на цій частоті — треба коротший шлях або нижчий такт.", 10.5, INK, "middle", "bold")
    s = caption_box(s, W, [
        ("Slack = період такту − потрібний час шляху. Додатний — є запас; рівно нуль — на межі; від'ємний — таймінг ПРОВАЛЕНО.", True),
        ("Перший обов'язок після трасування — перевірити, що найгірший slack невід'ємний. Деталі розрахунку — у вставці 🧮 до §3.7.7.", False),
    ], 314)
    save("fig-3-7-7-3-slack.svg", s)


def fig_377_4_pipeline_fix():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Як лікують довгий шлях: розрізати логіку регістрами (конвеєр)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "вставимо тригер посередині — кожна половина коротша, такт можна підняти (ціною +1 такту затримки, §3.5.6)",
              11.5, GREY, "middle", style="italic")
    # до
    s += text(110, 96, "БУЛО: уся логіка між двома регістрами", 11, RED, "start", "bold")
    s += _ff(110, 110, 50, 46, BLUE, "REG")
    s += rect(170, 110, 540, 46, "#fdf4f4", RED, 1.7, 6)
    s += text(440, 138, "довга логіка — 12 нс", 11, RED, "middle", "bold")
    s += _ff(710, 110, 50, 46, BLUE, "REG")
    s += text(440, 176, "критичний шлях ≈ 12 нс → Fmax ≈ 83 МГц", 10, RED, "middle", "bold")
    # після
    s += text(110, 240, "СТАЛО: посередині додано регістр (конвеєрний щабель)", 11, GREEN, "start", "bold")
    s += _ff(110, 254, 50, 46, BLUE, "REG")
    s += rect(170, 254, 250, 46, "#eef7ee", GREEN, 1.7, 6)
    s += text(295, 282, "пів-логіки — 6 нс", 10, GREEN, "middle", "bold")
    s += _ff(420, 254, 50, 46, BLUE, "REG")
    s += text(445, 318, "новий", 8.5, GREEN, "middle", "bold")
    s += rect(480, 254, 230, 46, "#eef7ee", GREEN, 1.7, 6)
    s += text(595, 282, "пів-логіки — 6 нс", 10, GREEN, "middle", "bold")
    s += _ff(710, 254, 50, 46, BLUE, "REG")
    s += text(440, 348, "критичний шлях ≈ 6 нс → Fmax ≈ 166 МГц (удвічі вище!)", 10.5, GREEN, "middle", "bold")
    s = caption_box(s, W, [
        ("Конвеєризація — головний прийом таймінгу: розрізати довгий шлях регістром, і кожна частина стане коротшою, а Fmax — вищою.", True),
        ("Платою є зайвий такт латентності (§3.5.6): результат з'являється на такт пізніше — але потік даних іде вдвічі швидше.", False),
    ], 366)
    save("fig-3-7-7-4-pipeline-fix.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.8 — FPGA чи мікроконтролер: чесні критерії вибору
# ═══════════════════════════════════════════════════════════════════════════

def fig_378_1_criteria():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чесне порівняння: де виграє мікроконтролер, а де FPGA", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "це не «що краще», а «що пасує задачі»: у кожного є царина, де він явно сильніший",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 84, 200, 30, "#eef0f4", INK, 1.3, 6)
    s += text(90, 105, "критерій", 11.5, INK, "start", "bold")
    s += text(450, 105, "мікроконтролер", 11.5, BLUE, "middle", "bold")
    s += text(700, 105, "FPGA", 11.5, GREEN, "middle", "bold")
    rows = [
        ("Справжня паралельність", "ні (одне ядро по черзі)", "так (своя схема на канал)", BLUE, GREEN),
        ("Затримка реакції", "такти + джитер", "наносекунди, стало", BLUE, GREEN),
        ("Складна послідовна логіка", "легко (код, бібліотеки)", "громіздко й дорого", GREEN, BLUE),
        ("Поріг входу / швидкість", "низький, годинами", "крутий, тижнями", GREEN, BLUE),
        ("Ціна за просту задачу", "копійки", "дорожче + флеш", GREEN, BLUE),
        ("Енергія на ват логіки", "залежить", "часто ефективніша", BLUE, GREEN),
    ]
    for i, (k, mc, fp, wmc, wfp) in enumerate(rows):
        y = 122 + i * 46
        s += rect(70, y, 200, 40, "#fafafa", INK, 1.2, 6)
        s += text(90, y + 25, k, 10.8, INK, "start", "bold")
        s += rect(280, y, 320, 40, "#f3f5fd" if wmc == GREEN else "#ffffff", BLUE, 1.1, 6)
        s += text(440, y + 25, mc, 10, INK, "middle", "bold" if wmc == GREEN else "normal")
        s += rect(610, y, 220, 40, "#eef7ee" if wfp == GREEN else "#ffffff", GREEN, 1.1, 6)
        s += text(720, y + 25, fp, 9.5, INK, "middle", "bold" if wfp == GREEN else "normal")
    s += text(W / 2, 426, "Зелена клітинка = сторона, що тут явно сильніша. Жодна колонка не виграє скрізь — вибір диктує конкретна задача.",
              10.5, INK, "middle", "bold")
    save("fig-3-7-8-1-criteria.svg", s)


def fig_378_2_latency_bars():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Один наочний приклад: затримка «вхід змінився → вихід відреагував»", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "груба ілюстрація порядків (конкретика залежить від задачі) — де FPGA на голову швидша",
              11.5, GREY, "middle", style="italic")
    bars = [
        ("МК: опитування у циклі", 600, BLUE, "сотні нс–мкс: поки дійде черга до перевірки"),
        ("МК: переривання", 360, BLUE, "десятки–сотні тактів на вхід у обробник"),
        ("FPGA: пряма логіка", 70, GREEN, "одиниці–десятки нс: лише крізь кілька вентилів"),
    ]
    y0 = 110
    x0 = 260
    for i, (k, w, col, note) in enumerate(bars):
        y = y0 + i * 80
        s += text(x0 - 14, y + 24, k, 11, col, "end", "bold")
        s += rect(x0, y, w, 38, "#eef7ee" if col == GREEN else "#f3f5fd", col, 1.8, 6)
        s += text(x0 + w + 12, y + 24, note, 9.5, INK, "start")
    s += text(x0, y0 + 3 * 80 + 4, "→ більша затримка", 10, GREY, "start", style="italic")
    s += arrow(x0, y0 + 3 * 80 - 6, x0 + 600, y0 + 3 * 80 - 6, GREY, 1.4)
    s = caption_box(s, W, [
        ("Коли важливі саме НАНОСЕКУНДИ реакції (швидке керування, захист, обробка фронтів), FPGA виграє з великим відривом.", True),
        ("Якщо ж достатньо «зреагувати за мікросекунди» — мікроконтролер простіший і дешевший, і цього вистачає.", False),
    ], 326)
    save("fig-3-7-8-2-latency-bars.svg", s)


def fig_378_3_decision():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Орієнтовне дерево рішень: МК, FPGA чи обидва разом", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кілька запитань, що зазвичай вирішують справу (не догма, а здоровий глузд)",
              11.5, GREY, "middle", style="italic")

    def node(x, y, t, col, bg, w=240, h=46):
        out = rect(x - w / 2, y, w, h, bg, col, 1.8, 8)
        for j, ln in enumerate(t.split("\n")):
            out += text(x, y + (26 if len(t.split("\n")) == 1 else 19) + j * 16, ln, 10.5, INK, "middle", "bold")
        return out

    s += node(450, 84, "Потрібна жорстка паралельність\nабо реакція за наносекунди?", INK, "#eef0f4", 320)
    # ні -> МК
    s += arrow(310, 107, 200, 150, BLUE, 2)
    s += text(230, 128, "ні", 11, BLUE, "middle", "bold")
    s += node(180, 150, "потік даних поміщається\nв одне ядро по тактах?", INK, "#eef0f4", 260)
    s += arrow(180, 196, 180, 240, GREEN, 2)
    s += text(196, 220, "так", 10, GREEN, "start", "bold")
    s += node(180, 240, "МІКРОКОНТРОЛЕР", BLUE, "#f3f5fd", 220)
    s += text(180, 296, "дешево, швидко в розробці", 9.5, GREY, "middle", style="italic")
    # так -> FPGA гілка
    s += arrow(590, 107, 700, 150, GREEN, 2)
    s += text(670, 128, "так", 11, GREEN, "middle", "bold")
    s += node(720, 150, "багато складної ПОСЛІДОВНОЇ\nлогіки / меню / мережі теж?", INK, "#eef0f4", 280)
    s += arrow(720, 196, 720, 240, AMBER, 2)
    s += text(736, 220, "так", 10, DARKAMBER, "start", "bold")
    s += node(720, 240, "FPGA + м'яке/тверде ядро", AMBER, "#fff8e8", 250)
    s += text(720, 296, "softcore поряд зі схемою (§3.7.9)", 9.5, GREY, "middle", style="italic")
    s += arrow(620, 173, 360, 240, GREEN, 1.8, "4 3")
    s += text(470, 200, "ні → чиста FPGA", 10, GREEN, "middle", "bold")
    s += node(360, 330, "FPGA", GREEN, "#eef7ee", 200)
    s += text(360, 386, "паралельність і таймінг у залізі", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Грубо: немає жорсткої паралельності й реакція не критична — беріть МК. Потрібні наносекунди й багато каналів — FPGA.", True),
        ("А коли поряд із швидкою схемою треба ще й «звичайне» керування — кладуть процесор УСЕРЕДИНІ FPGA (softcore, §3.7.9).", False),
    ], 410)
    save("fig-3-7-8-3-decision.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# §3.7.9 — М'яке ядро: процесор усередині FPGA (softcore)
# ═══════════════════════════════════════════════════════════════════════════

def fig_379_1_soft_vs_hard():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Тверде ядро vs м'яке ядро: де «живе» процесор", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "тверде ядро — готовий кремнієвий блок поряд із тканиною; м'яке — процесор, ЗІБРАНИЙ із LUT і тригерів",
              11.5, GREY, "middle", style="italic")
    # тверде ядро
    s += rect(70, 90, 360, 250, "#fbfbfb", BLUE, 1.8, 12)
    s += text(250, 114, "ТВЕРДЕ ядро (hard core)", 12, BLUE, "middle", "bold")
    s += rect(110, 140, 130, 160, "#f3f5fd", BLUE, 1.9, 8)
    s += text(175, 220, "CPU", 16, BLUE, "middle", "bold")
    s += text(175, 244, "у кремнії", 9.5, GREY, "middle")
    s += rect(260, 140, 130, 160, "#eef7ee", GREEN, 1.6, 8)
    s += text(325, 215, "тканина", 10, GREEN, "middle", "bold")
    s += text(325, 231, "FPGA", 10, GREEN, "middle", "bold")
    s += text(250, 320, "швидкий, малий, але фіксований", 9.5, INK, "middle", "bold")
    # м'яке ядро
    s += rect(470, 90, 360, 250, "#fbfbfb", GREEN, 1.8, 12)
    s += text(650, 114, "М'ЯКЕ ядро (soft core)", 12, GREEN, "middle", "bold")
    gx, gy = 510, 140
    # позначаємо клітинки, з яких "складено" CPU
    cpu_cells = {(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,2),(2,3),(2,4),(3,1),(3,2)}
    for r in range(4):
        for c in range(6):
            x, y = gx + c * 48, gy + r * 36
            if (r, c) in cpu_cells:
                s += rect(x, y, 40, 28, "#f3f5fd", BLUE, 1.5, 4)
            else:
                s += rect(x, y, 40, 28, "#eef7ee", GREEN, 1, 4)
    s += text(650, 300, "процесор «намальований» у тканині з LUT", 9.5, INK, "middle", "bold")
    s += text(650, 320, "гнучкий і переписуваний, але повільніший і більший", 9.5, GREY, "middle", style="italic")
    s = caption_box(s, W, [
        ("Тверде ядро — справжній CPU, випалений у кремнії поряд із логікою: швидкий і компактний, але незмінний.", True),
        ("М'яке ядро — той самий процесор, але ЗІБРАНИЙ із звичайних LUT і тригерів FPGA: повільніший, зате гнучкий і додається коли треба.", False),
    ], 350)
    save("fig-3-7-9-1-soft-vs-hard.svg", s)


def fig_379_2_soft_system():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Сила softcore: процесор поряд із власною апаратною периферією", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "у тій самій тканині — м'яке ядро для «повільної» логіки й окремі швидкі блоки для «гарячих» задач",
              11.5, GREY, "middle", style="italic")
    s += rect(80, 86, 740, 250, "#fbfbfb", GREEN, 1.6, 12)
    s += text(450, 110, "усе це — одна FPGA", 11, GREEN, "middle", "bold")
    # softcore
    s += rect(110, 130, 170, 110, "#f3f5fd", BLUE, 1.9, 10)
    s += text(195, 158, "м'яке ядро CPU", 11, BLUE, "middle", "bold")
    s += text(195, 180, "веде меню, мережу,", 9, INK, "middle")
    s += text(195, 196, "налаштування,", 9, INK, "middle")
    s += text(195, 212, "повільні рішення", 9, INK, "middle")
    # шина
    s += line(280, 185, 360, 185, INK, 2.5)
    s += text(320, 176, "шина", 9, GREY, "middle", "bold")
    s += rect(360, 150, 30, 70, "#eef0f4", INK, 1.5, 4)
    s += text(375, 250, "комутатор", 8.5, GREY, "middle")
    # апаратні прискорювачі
    accel = [("DSP-фільтр", 150), ("швидкий I/O", 210), ("ШІМ-канали", 270)]
    for i, (nm, y) in enumerate(accel):
        s += line(390, 185, 470, y + 20, GREY, 1.6)
        s += rect(470, y, 150, 40, "#fff8e8", AMBER, 1.7, 8)
        s += text(545, y + 25, nm, 10, DARKAMBER, "middle", "bold")
    s += text(545, 322, "апаратні блоки: паралельно, наносекунди", 9.5, DARKAMBER, "middle", "bold")
    s += text(640, 150, "← кожен", 9, GREY, "start")
    s += text(640, 166, "  робить своє", 9, GREY, "start")
    s += text(640, 182, "  паралельно", 9, GREY, "start")
    s = caption_box(s, W, [
        ("Ось навіщо softcore: рутину (меню, протоколи, конфігурацію) пише процесор, а «гарячі» потоки беруть на себе апаратні блоки.", True),
        ("М'яке ядро + власні прискорювачі на одній мікросхемі — це рішення для §3.7.8, коли потрібні і зручність коду, і швидкість заліза.", False),
    ], 366)
    save("fig-3-7-9-2-soft-system.svg", s)


def fig_379_3_when():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Коли м'яке ядро доречне, а коли краще окремий мікроконтролер", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "softcore коштує клітинок і тактів — тож має сенс лише за певних умов",
              11.5, GREY, "middle", style="italic")
    # доречно
    s += rect(70, 88, 370, 230, "#eef7ee", GREEN, 1.8, 12)
    s += text(255, 112, "✓ доречно", 13, GREEN, "middle", "bold")
    good = [
        "FPGA вже в системі з іншої причини",
        "потрібна гнучка послідовна логіка ПОРЯД",
        "хочемо власні інструкції/периферію",
        "зручно тримати все на одному чипі",
        "потрібна переносимість між FPGA",
    ]
    for i, t in enumerate(good):
        s += text(90, 142 + i * 32, "• " + t, 10, INK, "start")
    # недоречно
    s += rect(460, 88, 370, 230, "#fdf6f6", RED, 1.8, 12)
    s += text(645, 112, "✗ зайве", 13, RED, "middle", "bold")
    bad = [
        "потрібен лише процесор (без логіки)",
        "критичні максимальна частота / ціна",
        "вистачає дешевого готового МК",
        "немає потреби в паралельних блоках",
        "тверде ядро в цій FPGA вже є",
    ]
    for i, t in enumerate(bad):
        s += text(480, 142 + i * 32, "• " + t, 10, INK, "start")
    s = caption_box(s, W, [
        ("Правило просте: softcore виправданий, коли FPGA вже потрібна заради паралельного заліза, а поряд зручно мати «звичайний» CPU.", True),
        ("Якщо ж треба ЛИШЕ процесор — окремий мікроконтролер майже завжди дешевший, швидший і простіший (§3.7.8).", False),
    ], 326)
    save("fig-3-7-9-3-when.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
def main():
    # §3.7.1
    fig_371_1_serial_bottleneck()
    fig_371_2_throughput_math()
    fig_371_3_latency()
    fig_371_4_where_used()
    fig_371_5_spectrum()
    # §3.7.2
    fig_372_1_and_or_plane()
    fig_372_2_pal_pla_gal()
    fig_372_3_macrocell()
    fig_372_4_cpld_vs_fpga()
    fig_372_5_ladder()
    # §3.7.3
    fig_373_1_truth_to_lut()
    fig_373_2_mux_tree()
    fig_373_3_any_function()
    fig_373_4_lut_vs_gates()
    fig_373_5_lut_size()
    # §3.7.4
    fig_374_1_logic_cell()
    fig_374_2_clb_cluster()
    fig_374_3_routing()
    fig_374_4_island()
    fig_374_5_bram()
    fig_374_6_dsp()
    # §3.7.5
    fig_375_1_describe_vs_program()
    fig_375_2_module()
    fig_375_3_comb_vs_seq()
    fig_375_4_synth_not_exec()
    fig_375_5_same_code_diff_hw()
    # §3.7.6
    fig_376_1_flow()
    fig_376_2_synthesis()
    fig_376_3_place_route()
    fig_376_4_bitstream()
    fig_376_5_config_flash()
    # §3.7.7
    fig_377_1_path()
    fig_377_2_fmax()
    fig_377_3_slack()
    fig_377_4_pipeline_fix()
    # §3.7.8
    fig_378_1_criteria()
    fig_378_2_latency_bars()
    fig_378_3_decision()
    # §3.7.9
    fig_379_1_soft_vs_hard()
    fig_379_2_soft_system()
    fig_379_3_when()
    print("DONE")


if __name__ == "__main__":
    main()
