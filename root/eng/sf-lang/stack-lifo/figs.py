# -*- coding: utf-8 -*-
"""Фігури до теми «Стек» (виклик функції, LIFO) та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"     # тепле виділення (g(), high-water mark)


# ── Допоміжне: клітинка кадру/байта ──────────────────────────────────────────
def cell(x, y, w, h, label, color, fill=FILL, sw=1.5, size=12):
    return (rect(x, y, w, h, fill=fill, stroke=color, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + size * 0.35, label, size=size, color=color, bold=True))


# ── 1. Проблема: виклики вкладаються ─────────────────────────────────────────
def fig_problem():
    W, H = 760, 380
    f = [text(W / 2, 26, "Виклики вкладаються — а розкручуються навпаки", size=15, bold=True)]

    # сходи викликів углиб
    steps = [("main", 60, INK), ("f", 250, NEG), ("g", 440, GOLD)]
    for name, x, col in steps:
        f.append(rect(x, 70, 230, 60, fill=FILL, stroke=col, sw=2))
        f.append(text(x + 115, 96, "%s()" % name, size=14, color=col, bold=True))
        f.append(text(x + 115, 116, "адреса повернення + локальні", size=9.5, color=MUTED, italic=True))
    f.append(arrow(290, 100, 248, 100, color=INK, sw=2))      # main викликає f
    f.append(text(269, 64, "викликає", size=9.5, color=MUTED, italic=True))
    f.append(arrow(480, 100, 438, 100, color=INK, sw=2))      # f викликає g
    f.append(text(459, 64, "викликає", size=9.5, color=MUTED, italic=True))

    # повернення у зворотному порядку
    f.append(text(W / 2, 188, "хто ввійшов останнім — виходить першим", size=13, color=POS, bold=True))
    order = [("g завершується", 60, GOLD), ("потім f", 300, NEG), ("потім main", 520, INK)]
    x_prev = None
    for label, x, col in order:
        f.append(rect(x, 212, 180, 44, fill=BG, stroke=col, sw=1.8))
        f.append(text(x + 90, 239, label, size=12, color=col, bold=True))
        if x_prev is not None:
            f.append(arrow(x_prev, 234, x - 6, 234, color=POS, sw=1.8))
        x_prev = x + 180

    f.append(text(W / 2, 300,
                  "як дужки в математиці: остання відкрита закривається першою",
                  size=11, color=INK))
    f.append(text(W / 2, 322, "( main ( f ( g ) ) )", size=15, color=MUTED, bold=True))
    f.append(text(W / 2, 360,
                  "кожен виклик мусить запам'ятати, куди повертатись, і мати місце під свої змінні",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "problem.svg"), W, H, *f)


# ── 2. Стек = LIFO (стос тарілок) ────────────────────────────────────────────
def fig_lifo():
    W, H = 760, 360
    f = [text(W / 2, 26, "Стек: кладеш зверху, береш зверху (LIFO)", size=15, bold=True)]

    # стос «тарілок»
    cx, base = 230, 300
    plates = [("перша", MUTED), ("друга", MUTED), ("третя", NEG), ("четверта", GOLD)]
    pw, ph = 220, 36
    for i, (lab, col) in enumerate(plates):
        y = base - (i + 1) * (ph + 6)
        f.append(rect(cx - pw / 2, y, pw, ph, fill=FILL, stroke=col, sw=2 if i == len(plates) - 1 else 1.4))
        f.append(text(cx, y + ph / 2 + 4, lab, size=12, color=col, bold=(i == len(plates) - 1)))
    # підлога
    f.append(line(cx - pw / 2 - 14, base, cx + pw / 2 + 14, base, color=INK, sw=2.5))

    # стрілки push / pop до вершини
    top_y = base - len(plates) * (ph + 6)
    f.append(arrow(cx + pw / 2 + 70, top_y - 20, cx + pw / 2 + 14, top_y + 4, color=FIELD, sw=2))
    f.append(text(cx + pw / 2 + 78, top_y - 26, "push: кладемо наверх", size=11, color=FIELD, anchor="start", bold=True))
    f.append(arrow(cx + pw / 2 + 14, top_y + ph + 2, cx + pw / 2 + 70, top_y + ph + 26, color=POS, sw=2))
    f.append(text(cx + pw / 2 + 78, top_y + ph + 30, "pop: знімаємо з верху", size=11, color=POS, anchor="start", bold=True))

    # дві операції
    f.append(rect(560, 150, 180, 56, fill="#eef7f0", stroke=FIELD, sw=1.6))
    f.append(text(650, 174, "push", size=13, color=FIELD, bold=True))
    f.append(text(650, 194, "увійшли — додали кадр", size=9.5, color=MUTED, italic=True))
    f.append(rect(560, 216, 180, 56, fill="#fdf0ee", stroke=POS, sw=1.6))
    f.append(text(650, 240, "pop", size=13, color=POS, bold=True))
    f.append(text(650, 260, "вийшли — зняли кадр", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 344,
                  "лише вершина — ні пошуку, ні доступу до середини; тому стек блискавично швидкий",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "lifo.svg"), W, H, *f)


# ── 3. Стековий кадр ─────────────────────────────────────────────────────────
def fig_frame():
    W, H = 720, 360
    f = [text(W / 2, 26, "Що кладе на стек один виклик: кадр", size=15, bold=True)]

    parts = [
        ("адреса повернення", "куди продовжити того, хто викликав → у PC при return", POS),
        ("збережені регістри", "значення, які треба відновити після виклику", NEG),
        ("параметри", "аргументи функції", FIELD),
        ("локальні змінні", "власні змінні функції", GOLD),
    ]
    x, y, w, rh = 60, 64, 360, 56
    for i, (label, note, col) in enumerate(parts):
        yy = y + i * (rh + 8)
        f.append(rect(x, yy, w, rh, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 16, yy + 24, label, size=13, color=col, anchor="start", bold=True))
        f.append(text(x + 16, yy + 43, note, size=9.5, color=MUTED, anchor="start", italic=True))

    # фігурна дужка «один кадр»
    bx = x + w + 18
    f.append(line(bx, y, bx, y + 4 * (rh + 8) - 8, color=INK, sw=2))
    f.append(text(bx + 12, (y + y + 4 * (rh + 8) - 8) / 2 - 8, "один", size=12, color=INK, anchor="start", bold=True))
    f.append(text(bx + 12, (y + y + 4 * (rh + 8) - 8) / 2 + 10, "кадр", size=12, color=INK, anchor="start", bold=True))

    # push/pop
    f.append(rect(bx + 70, 90, 168, 50, fill="#eef7f0", stroke=FIELD, sw=1.5))
    f.append(text(bx + 154, 112, "вхід → push", size=12, color=FIELD, bold=True))
    f.append(text(bx + 154, 130, "кадр ліг на стек", size=9.5, color=MUTED, italic=True))
    f.append(rect(bx + 70, 156, 168, 50, fill="#fdf0ee", stroke=POS, sw=1.5))
    f.append(text(bx + 154, 178, "вихід → pop", size=12, color=POS, bold=True))
    f.append(text(bx + 154, 196, "пам'ять умить вільна", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 344,
                  "локальні «автоматичні»: з'являються при вході, зникають при виході — без ручного керування",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "frame.svg"), W, H, *f)


# ── 4. Серце механізму: адреса повернення ────────────────────────────────────
def fig_returnaddr():
    W, H = 760, 340
    f = [text(W / 2, 26, "Виклик зберігає адресу повернення; return її дістає", size=15, bold=True)]

    # ліворуч: код main із адресами
    f.append(rect(40, 70, 250, 150, fill="#fbfbfc", stroke="#e6e6ea", sw=1.4))
    f.append(text(165, 92, "код main", size=12, color=INK, bold=True))
    f.append(text(56, 120, "0x44:  call f", size=12, color=INK, anchor="start"))
    f.append(text(56, 146, "0x45:  ... (далі)", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(56, 172, "0x46:  ...", size=11, color=MUTED, anchor="start"))
    f.append(text(165, 204, "PC ← початок f", size=10.5, color=GOLD, italic=True))

    # стрілка call вниз у f
    f.append(arrow(290, 120, 420, 120, color=GOLD, sw=2))
    f.append(text(355, 110, "call: стрибок", size=9.5, color=GOLD, italic=True))

    # праворуч: стек із покладеною адресою 0x45
    f.append(rect(440, 70, 200, 150, fill=FILL, stroke=NEG, sw=1.8))
    f.append(text(540, 92, "стек під час f", size=12, color=NEG, bold=True))
    f.append(cell(470, 110, 140, 30, "0x45", NEG, fill="#eef3fb", size=12))
    f.append(text(540, 158, "адреса повернення", size=10, color=MUTED, italic=True))
    f.append(text(540, 176, "лежить тут, доки f працює", size=9.5, color=MUTED, italic=True))

    # return: стрілка назад зі стека в PC
    f.append(arrow(440, 250, 165, 250, color=POS, sw=2))
    f.append(text(300, 240, "return: 0x45 зі стека → у PC", size=11, color=POS, italic=True, bold=True))
    f.append(text(165, 276, "main продовжується з 0x45", size=11, color=NEG, bold=True))

    f.append(text(W / 2, 324,
                  "виклик — це стрибок із запам'ятовуванням; повернення — стрибок за збереженою адресою",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "return-address.svg"), W, H, *f)


# ── 5. Наскрізний прохід: main → f → g ───────────────────────────────────────
def fig_trace():
    W, H = 820, 430
    f = [text(W / 2, 26, "Стек росте при викликах, спадає при поверненнях", size=15, bold=True)]

    cols = [
        ("main працює", [("main", INK)], 1),
        ("main → f", [("main", INK), ("f", NEG)], 1),
        ("f → g", [("main", INK), ("f", NEG), ("g", GOLD)], 1),
        ("g: return", [("main", INK), ("f", NEG)], -1),
        ("f: return", [("main", INK)], -1),
    ]
    n = len(cols)
    colw, x0 = 150, 24
    base = 360                    # дно (нижчі адреси) — намальоване внизу
    ch = 34
    for i, (caption, frames, dirn) in enumerate(cols):
        x = x0 + i * colw
        f.append(text(x + colw / 2 - 12, 70, caption, size=11, color=INK, bold=True))
        for k, (name, col) in enumerate(frames):
            y = base - (k + 1) * ch
            top = (k == len(frames) - 1)
            f.append(cell(x + 10, y, 110, ch - 4, "%s()" % name, col,
                          sw=2.2 if top else 1.3, size=11))
            if top:
                f.append(text(x + 126, y + ch / 2 + 3, "←SP", size=9, color=POS, anchor="start", bold=True))
        # стрілка push/pop між стовпцями
        midy = base - 150
        if dirn > 0:
            f.append(text(x + colw - 16, midy, "push ↑", size=9, color=FIELD, bold=True))
        else:
            f.append(text(x + colw - 16, midy, "pop ↓", size=9, color=POS, bold=True))
    f.append(line(x0, base, x0 + n * colw - 20, base, color=INK, sw=2))     # дно

    f.append(text(W / 2, 392,
                  "g (доданий останнім) знімається першим, тоді f — вершину стежить покажчик стека SP",
                  size=10.5, color=INK))
    f.append(text(W / 2, 414,
                  "пам'ять виділяється й звільняється сама — лише рухом SP (у пам'яті стек росте до нижчих адрес)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "trace.svg"), W, H, *f)


# ── 6. Властивості стека: переваги й межі ────────────────────────────────────
def fig_props():
    W, H = 760, 320
    f = [text(W / 2, 26, "Стек: переваги й межі", size=15, bold=True)]

    # переваги
    f.append(rect(30, 56, 340, 230, fill="#f1f8f3", stroke=FIELD, sw=1.8))
    f.append(text(200, 80, "✓ переваги", size=13, color=FIELD, bold=True))
    pros = [
        "швидко — виділення це рух SP на крок",
        "само — вхід виділяє, вихід звільняє",
        "локальні «автоматичні», без керування",
        "ідеально лягає на вкладені виклики",
    ]
    for i, p in enumerate(pros):
        f.append(text(50, 112 + i * 32, "• " + p, size=11, color=INK, anchor="start"))

    # межі
    f.append(rect(390, 56, 340, 230, fill="#fdf3f2", stroke=POS, sw=1.8))
    f.append(text(560, 80, "✗ межі", size=13, color=POS, bold=True))
    cons = [
        ("обмежений за розміром", "глибока рекурсія → переповнення"),
        ("локальні зникають при поверненні", "не повертати покажчик на локальну"),
        ("лише тимчасове", "для довговічного — купа"),
    ]
    for i, (head, note) in enumerate(cons):
        yy = 112 + i * 52
        f.append(text(410, yy, "• " + head, size=11, color=INK, anchor="start", bold=True))
        f.append(text(424, yy + 18, note, size=9.5, color=MUTED, anchor="start", italic=True))

    f.append(text(W / 2, 308,
                  "сила стека — у тимчасовому: те, що живе рівно стільки, скільки триває виклик",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "props.svg"), W, H, *f)


# ════════════════════════ ВСТАВКИ ════════════════════════════════════════════

def _stack_column(f, x, top, dno, cw, ch, cells):
    """Малює вертикальну колонку байтів стека (cells: список (label, color, fill))."""
    y = top
    for label, col, fill in cells:
        f.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.2, rx=3))
        f.append(text(x + cw / 2, y + ch / 2 + 4, label, size=10.5, color=col, bold=True))
        y += ch


# ── Вставка proj/hist, фіг.1: заливка 0xA5 ───────────────────────────────────
def fig_paint():
    W, H = 760, 440
    f = [text(W / 2, 26, "Крок 1: щойно створений стек заливають патерном", size=15, bold=True)]

    x, top, cw, ch = 210, 60, 150, 22
    nrows = 15
    cells = [("0xA5", POS, "#fdecea")] * nrows
    _stack_column(f, x, top, top + nrows * ch, cw, ch, cells)
    bot = top + nrows * ch
    f.append(line(x - 8, top, x + cw + 8, top, color=INK, sw=2))
    f.append(line(x - 8, bot, x + cw + 8, bot, color=INK, sw=2))
    f.append(text(x - 14, top + 12, "вершина", size=10, color=MUTED, anchor="end", bold=True))
    f.append(text(x - 14, bot, "межа (дно)", size=10, color=MUTED, anchor="end", bold=True))

    f.append(text(x + cw + 24, top + 130, "увесь стек —", size=12, color=POS, anchor="start", bold=True))
    f.append(text(x + cw + 24, top + 148, "суцільний 0xA5", size=12, color=POS, anchor="start", bold=True))
    f.append(text(x + cw + 24, top + 168, "(жоден байт ще не торкнутий)", size=9.5, color=MUTED, anchor="start", italic=True))

    # чому 0xA5
    f.append(rect(480, 250, 250, 130, fill="#f1f8f3", stroke=FIELD, sw=1.6))
    f.append(text(605, 274, "Чому саме 0xA5?", size=12.5, color=FIELD, bold=True))
    for i, ln in enumerate([
        "рідкісне в реальних даних",
        "1010 0101 — помітне оком у дампі",
        "у коді: tskSTACK_FILL_BYTE",
        "(інші РТОС беруть 0xAA, 0x99)",
    ]):
        f.append(text(496, 300 + i * 20, "• " + ln, size=10, color=INK, anchor="start"))

    f.append(text(W / 2, 424,
                  "наче засипати порожнечу свіжим снігом, щоб потім читати на ньому сліди",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "paint.svg"), W, H, *f)


# ── Вставка, фіг.2: скан і high-water mark ───────────────────────────────────
def fig_scan():
    W, H = 760, 440
    f = [text(W / 2, 26, "Крок 2: скануємо знизу, шукаємо межу фарби", size=15, bold=True)]

    x, top, cw, ch = 230, 60, 150, 22
    used = ["0x3F", "0x00", "0x12", "0xE4", "0x44", "0x45", "0x7A", "0x01"]
    cells = [(v, NEG, "#eaf0fd") for v in used] + [("0xA5", POS, "#fdecea")] * 7
    nrows = len(cells)
    _stack_column(f, x, top, top + nrows * ch, cw, ch, cells)
    bot = top + nrows * ch
    mark_y = top + len(used) * ch        # межа стертого
    f.append(line(x - 8, top, x + cw + 8, top, color=INK, sw=2))
    f.append(line(x - 8, bot, x + cw + 8, bot, color=INK, sw=2))
    f.append(text(x - 14, top + 12, "вершина", size=10, color=MUTED, anchor="end", bold=True))
    f.append(text(x - 14, bot, "дно (звідси скан)", size=10, color=MUTED, anchor="end", bold=True))

    # скан знизу вгору
    f.append(arrow(x + cw + 30, bot - 4, x + cw + 30, mark_y + 4, color=FIELD, sw=2.4))
    f.append(text(x + cw + 40, (bot + mark_y) / 2, "скан знизу", size=10.5, color=FIELD, anchor="start", bold=True))

    # лінія high-water mark
    f.append(line(x - 20, mark_y, x + cw + 120, mark_y, color=GOLD, sw=2.2, dash="6 4"))
    f.append(text(x + cw + 130, mark_y - 4, "high-water mark", size=11, color=GOLD, anchor="start", bold=True))
    f.append(text(x + cw + 130, mark_y + 12, "(найглибша точка)", size=9.5, color=MUTED, anchor="start", italic=True))

    # дужки макс. використано / вільний запас
    f.append(line(x - 24, top, x - 24, mark_y, color=NEG, sw=2))
    f.append(text(x - 30, (top + mark_y) / 2, "макс. ужито", size=10, color=NEG, anchor="end", bold=True))
    f.append(line(x - 24, mark_y, x - 24, bot, color=POS, sw=2))
    f.append(text(x - 30, (mark_y + bot) / 2, "вільний запас", size=10, color=POS, anchor="end", bold=True))

    f.append(text(W / 2, 414,
                  "uxTaskGetStackHighWaterMark повертає вцілілі 0xA5 — найменший вільний запас за весь час",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "scan.svg"), W, H, *f)


# ── Вставка, фіг.3: пастка — непрочитаний буфер лишає 0xA5 ───────────────────
def fig_trap():
    W, H = 760, 420
    f = [text(W / 2, 26, "Пастка: діра 0xA5 всередині використаної зони", size=15, bold=True)]

    x, top, cw, ch = 250, 60, 150, 22
    cells = (
        [("0x3F", NEG, "#eaf0fd"), ("0x44", NEG, "#eaf0fd")] +
        [("0xA5", GOLD, "#fdf6e3")] * 3 +                 # «діра» в буфері
        [("0x7A", NEG, "#eaf0fd"), ("0x01", NEG, "#eaf0fd"), ("0xC8", NEG, "#eaf0fd")] +
        [("0xA5", POS, "#fdecea")] * 6                    # справжній вільний запас
    )
    nrows = len(cells)
    _stack_column(f, x, top, top + nrows * ch, cw, ch, cells)
    bot = top + nrows * ch
    f.append(line(x - 8, top, x + cw + 8, top, color=INK, sw=2))
    f.append(line(x - 8, bot, x + cw + 8, bot, color=INK, sw=2))
    f.append(text(x - 14, top + 12, "вершина", size=10, color=MUTED, anchor="end", bold=True))
    f.append(text(x - 14, bot, "дно (звідси скан)", size=10, color=MUTED, anchor="end", bold=True))

    # позначка «діра»
    hole_y = top + 2 * ch
    f.append(line(x + cw + 16, hole_y, x + cw + 16, hole_y + 3 * ch, color=GOLD, sw=2))
    f.append(text(x + cw + 24, hole_y + 1.5 * ch - 6, "буфер заповнили", size=10, color=GOLD, anchor="start", bold=True))
    f.append(text(x + cw + 24, hole_y + 1.5 * ch + 10, "не повністю → діра 0xA5", size=9.5, color=MUTED, anchor="start", italic=True))

    # справжня межа скану — перший 0xA5 від дна
    mark_y = top + 8 * ch
    f.append(line(x - 20, mark_y, x + cw + 12, mark_y, color=POS, sw=2.2, dash="6 4"))
    f.append(text(x - 26, mark_y + 4, "скан чесно бачить", size=9.5, color=POS, anchor="end", bold=True))
    f.append(text(x - 26, mark_y + 18, "перший 0xA5 від дна", size=9.5, color=MUTED, anchor="end", italic=True))

    f.append(text(W / 2, 404,
                  "діра скан не дурить, та через такі ефекти watermark — обережна нижня оцінка (запас ×1.5–2)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "trap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_problem()
    fig_lifo()
    fig_frame()
    fig_returnaddr()
    fig_trace()
    fig_props()
    fig_paint()
    fig_scan()
    fig_trap()
    print("OK: 9 figures ->", IMG)
