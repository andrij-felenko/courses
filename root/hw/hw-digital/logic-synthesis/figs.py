# -*- coding: utf-8 -*-
"""Фігури до статті «Логічний синтез: від HDL до вентилів» та її вставок.
  synth-vs-compile.svg — два перекладачі: компілятор→інструкції, синтезатор→схема
  inference.svg        — таблиця «зразок коду → апаратна цеглинка»
  latch-infer.svg      — неповний if → засувка ; повний → мультиплексор
  tech-map.svg         — одна логіка → стандартні клітинки (ASIC) або LUT (FPGA)
  netlist.svg          — RTL → нетлист (граф клітинок і з'єднань)
  karnaugh.svg         — [hist] карта Карно 4 змінних, блок і зайва змінна
  timeline.svg         — [hist] смуга віх: Карно → Квайн-Мак-Класкі → Espresso → Design Compiler
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#eef1f4"
MONO = "'Consolas', 'DejaVu Sans Mono', monospace"
GATE = "#eaf0fd"     # заливка апаратних блоків
CODEFILL = "#f4f6f8"


def codebox(x, y, w, h, lines, size=13, color=INK, title=None):
    """Прямокутник із моноширинним кодом (ліворуч), рядки — список."""
    out = rect(x, y, w, h, fill=CODEBG, stroke=MUTED, sw=1.3, rx=6)
    ty = y + (26 if title else 20)
    if title:
        out += text(x + w / 2, y + 17, title, size=12, color=MUTED, bold=True)
    for i, ln in enumerate(lines):
        out += ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" '
                'fill="%s" text-anchor="start">%s</text>'
                % (x + 12, ty + i * (size + 6), MONO, size, color, esc(ln)))
    return out


def hwblock(cx, cy, w, h, label, sub=None, fill=GATE, stroke=NEG):
    """Апаратна цеглинка з підписом (за потреби у два рядки)."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=7)
    if sub:
        out += text(cx, cy - 3, label, size=14, color=INK, bold=True)
        out += text(cx, cy + 15, sub, size=11, color=MUTED)
    else:
        out += text(cx, cy + 5, label, size=14, color=INK, bold=True)
    return out


# ── 1. synth-vs-compile ─────────────────────────────────────────────────────
def fig_synth_vs_compile():
    W, H = 720, 420
    els = []
    els.append(text(W / 2, 30, "Два перекладачі з тексту", size=17, bold=True))

    # верхня гілка: софт
    els.append(text(150, 66, "СОФТ", size=13, color=MUTED, bold=True))
    els.append(codebox(40, 80, 220, 66, ["int c = a + b;",
                                         "// текст на C"], size=13, color=NEG))
    els.append(arrow(268, 113, 322, 113, color=INK, sw=2))
    b, w, h = textbox(390, 113, "компілятор", size=13, fill=CODEFILL,
                      stroke=INK, bold=True)
    els.append(b)
    els.append(arrow(462, 113, 516, 113, color=INK, sw=2))
    els.append(codebox(524, 80, 168, 66, ["LD  a", "ADD b", "ST  c"],
                       size=12, color=INK, title="інструкції"))
    els.append(text(608, 168, "процесор виконує ПО ЧЕРЗІ в часі",
                    size=12, color=MUTED))
    els.append(arrow(548, 158, 668, 158, color=MUTED, sw=1.5))

    # роздільник
    els.append(line(40, 210, 680, 210, color=MUTED, sw=1, dash="5 5"))

    # нижня гілка: залізо
    els.append(text(150, 250, "ЗАЛІЗО", size=13, color=FIELD, bold=True))
    els.append(codebox(40, 264, 220, 66, ["assign c = a + b;",
                                          "// текст на HDL"], size=13, color=FIELD))
    els.append(arrow(268, 297, 322, 297, color=INK, sw=2))
    b, w, h = textbox(390, 297, "синтезатор", size=13, fill=CODEFILL,
                      stroke=FIELD, bold=True)
    els.append(b)
    els.append(arrow(462, 297, 516, 297, color=INK, sw=2))
    # маленька схема-суматор
    els.append(hwblock(600, 297, 130, 52, "суматор", "(вентилі)"))
    els.append(line(524, 285, 535, 285, color=INK, sw=2))
    els.append(line(524, 309, 535, 309, color=INK, sw=2))
    els.append(line(665, 297, 685, 297, color=INK, sw=2))
    els.append(text(600, 358, "працює вся НАРАЗ, одночасно",
                    size=12, color=MUTED))

    els.append(text(W / 2, 400,
                    "«швидше»: у софті — менше інструкцій · у синтезі — коротший ланцюг логіки",
                    size=12, color=INK))
    render(os.path.join(OUT, "synth-vs-compile.svg"), W, H, *els)


# ── 2. inference ────────────────────────────────────────────────────────────
def fig_inference():
    W, H = 720, 430
    els = []
    els.append(text(W / 2, 30, "Зразок опису → апаратна цеглинка (інференс)",
                    size=17, bold=True))
    els.append(text(180, 58, "у коді пишеш", size=12, color=MUTED, bold=True))
    els.append(text(560, 58, "синтезатор ставить", size=12, color=MUTED, bold=True))

    rows = [
        (["a + b"], "суматор", None),
        (["if (s) y=a;", "else   y=b;"], "мультиплексор", "(вибір гілки)"),
        (["always @(posedge", "         clk) q<=d;"], "регістр", "(тригери, пам'ять)"),
        (["a * b"], "помножувач", None),
    ]
    y = 88
    for code, lab, sub in rows:
        ch = 44 if len(code) == 1 else 60
        els.append(codebox(48, y, 260, ch, code, size=13, color=NEG))
        my = y + ch / 2
        els.append(arrow(320, my, 402, my, color=INK, sw=2))
        els.append(hwblock(560, my, 200, 48, lab, sub))
        y += ch + 20

    els.append(text(W / 2, 412,
                    "той самий вираз ПІД тактом і БЕЗ такту дає різне залізо: регістр ↔ миттєва логіка",
                    size=12, color=INK))
    render(os.path.join(OUT, "inference.svg"), W, H, *els)


# ── 3. latch-infer ──────────────────────────────────────────────────────────
def fig_latch_infer():
    W, H = 720, 400
    els = []
    els.append(text(W / 2, 30, "Ненавмисна засувка: неповний вибір = пам'ять",
                    size=17, bold=True))

    # ліворуч: неповний if → засувка
    els.append(text(185, 62, "НЕПОВНО — вихід не заданий для всіх умов",
                    size=12, color=POS, bold=True))
    els.append(codebox(30, 78, 330, 78,
                       ["always @(*)",
                        "  if (en) y = data;",
                        "  // а якщо en==0 ?  мовчить"],
                       size=13, color=INK))
    els.append(arrow(195, 168, 195, 208, color=POS, sw=2.2))
    els.append(hwblock(195, 250, 210, 62, "ЗАСУВКА (latch)",
                       "мусить тримати старе y", fill="#fdecea", stroke=POS))
    b, w, h = textbox(195, 330, "небажана пам'ять\nу комбінаційнім блоці",
                      size=12, fill="#fdecea", stroke=POS, color=POS)
    els.append(b)

    # роздільник
    els.append(line(370, 60, 370, 356, color=MUTED, sw=1, dash="5 5"))

    # праворуч: повний if → мультиплексор
    els.append(text(545, 62, "ПОВНО — вихід заданий для всіх умов",
                    size=12, color=FIELD, bold=True))
    els.append(codebox(385, 78, 320, 78,
                       ["always @(*)",
                        "  if (en) y = data;",
                        "  else    y = 8'h00;   // else!"],
                       size=13, color=INK))
    els.append(arrow(545, 168, 545, 208, color=FIELD, sw=2.2))
    els.append(hwblock(545, 250, 200, 62, "мультиплексор",
                       "без пам'яті", fill="#eafaf0", stroke=FIELD))
    b, w, h = textbox(545, 330, "чиста комбінаційна\nлогіка — то й треба",
                      size=12, fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(b)

    render(os.path.join(OUT, "latch-infer.svg"), W, H, *els)


# ── 4. tech-map ─────────────────────────────────────────────────────────────
def fig_tech_map():
    W, H = 720, 400
    els = []
    els.append(text(W / 2, 30, "Один RTL — дві прив'язки до заліза",
                    size=17, bold=True))

    # центр: абстрактна логіка
    els.append(hwblock(360, 110, 240, 66, "абстрактна логіка",
                       "AND · OR · NOT · суматори", fill=CODEFILL, stroke=INK))
    els.append(text(360, 66, "(родове дерево, без прив'язки до чипа)",
                    size=12, color=MUTED))

    # ліва гілка: ASIC
    els.append(arrow(300, 148, 195, 208, color=INK, sw=2))
    els.append(text(150, 200, "ASIC — фабрика", size=13, color=NEG, bold=True))
    for i, (lx, lab) in enumerate([(80, "NAND"), (160, "NOR"), (240, "тригер")]):
        els.append(hwblock(lx, 250, 70, 40, lab, fill=GATE, stroke=NEG))
    b, w, h = textbox(160, 318, "стандартні клітинки:\nготові вентилі з бібліотеки",
                      size=12, fill=CODEFILL, stroke=NEG)
    els.append(b)

    # права гілка: FPGA
    els.append(arrow(420, 148, 545, 208, color=INK, sw=2))
    els.append(text(560, 200, "FPGA — програмовна", size=13, color=FIELD, bold=True))
    for i, lx in enumerate([490, 560, 630]):
        els.append(hwblock(lx, 250, 62, 40, "LUT", fill="#eafaf0", stroke=FIELD))
    b, w, h = textbox(560, 318, "таблиці LUT:\nодна комірка — будь-яка функція",
                      size=12, fill="#eafaf0", stroke=FIELD)
    els.append(b)

    els.append(text(W / 2, 384,
                    "тіло синтезу спільне — різниться лише останній крок: на які клітинки накласти",
                    size=12, color=INK))
    render(os.path.join(OUT, "tech-map.svg"), W, H, *els)


# ── 5. netlist ──────────────────────────────────────────────────────────────
def fig_netlist():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 30, "Вихід синтезу — нетлист (елементи + з'єднання)",
                    size=17, bold=True))

    # ліворуч: RTL
    els.append(codebox(30, 70, 280, 100,
                       ["always @(posedge clk)",
                        "  acc <= acc + x;",
                        "assign sum = acc;"],
                       size=13, color=NEG, title="RTL (намір)"))
    els.append(arrow(316, 130, 384, 130, color=INK, sw=2.2))
    els.append(text(350, 116, "синтез", size=11, color=MUTED))

    # праворуч: граф нетлиста
    els.append(rect(400, 66, 296, 210, fill=BG, stroke=MUTED, sw=1.3, rx=8))
    els.append(text(548, 88, "нетлист: клітинки й дроти", size=12,
                    color=MUTED, bold=True))
    # вхід x
    els.append(text(430, 138, "x", size=13, color=INK, bold=True))
    els.append(line(440, 133, 470, 133, color=INK, sw=2))
    # суматор
    els.append(hwblock(510, 140, 78, 46, "+", "суматор", fill=GATE, stroke=NEG))
    # регістр
    els.append(hwblock(628, 140, 78, 52, "рег.", "тригери", fill=GATE, stroke=NEG))
    els.append(line(549, 140, 589, 140, color=INK, sw=2))
    # вихід sum
    els.append(line(667, 140, 690, 140, color=INK, sw=2))
    els.append(text(683, 128, "sum", size=12, color=INK, bold=True))
    # петля зворотного зв'язку acc → суматор
    els.append(line(628, 166, 628, 236, color=FIELD, sw=2))
    els.append(line(628, 236, 490, 236, color=FIELD, sw=2))
    els.append(line(490, 236, 490, 163, color=FIELD, sw=2))
    els.append(arrow(490, 200, 490, 165, color=FIELD, sw=2))
    els.append(text(548, 252, "зворотний зв'язок: acc назад у суматор",
                    size=11, color=FIELD))
    # такт
    els.append(text(628, 108, "clk", size=11, color=MUTED))
    els.append(line(628, 112, 628, 116, color=MUTED, sw=1.5))

    els.append(text(W / 2, 320,
                    "уже не поведінка, а структура: список елементів і що з чим з'єднано",
                    size=12, color=INK))
    els.append(text(W / 2, 342,
                    "далі — фізична реалізація: розкладання по чипу й маршрути",
                    size=11, color=MUTED))
    render(os.path.join(OUT, "netlist.svg"), W, H, *els)


# ── 6. karnaugh (вставка hist) ──────────────────────────────────────────────
def fig_karnaugh():
    W, H = 620, 430
    els = []
    els.append(text(W / 2, 30, "Карта Карно: мінімізація як розглядання картинки",
                    size=16, bold=True))

    gray = ["00", "01", "11", "10"]          # порядок коду Ґрея
    # одиниці в карті (row, col); суміжна пара 1 у стовпці "11" (col=2) — її обведемо
    ones = {(0, 2), (1, 2), (0, 0), (3, 3)}
    box_cells = [(0, 2), (1, 2)]             # блок із двох сусідніх одиниць

    cell = 62
    gx, gy = 150, 92                          # лівий-верхній кут сітки 4×4
    # підписи осей
    els.append(text(gx + 2 * cell, gy - 40, "ab", size=13, color=MUTED, bold=True))
    els.append(text(gx - 46, gy + 2 * cell, "cd", size=13, color=MUTED, bold=True))
    # заголовки стовпців (ab) та рядків (cd) у коді Ґрея
    for j, g in enumerate(gray):
        els.append(text(gx + j * cell + cell / 2, gy - 12, g, size=13,
                        color=NEG, bold=True))
    for i, g in enumerate(gray):
        els.append(text(gx - 16, gy + i * cell + cell / 2 + 5, g, size=13,
                        color=NEG, bold=True))
    # клітинки
    for i in range(4):
        for j in range(4):
            x, y = gx + j * cell, gy + i * cell
            filled = (i, j) in ones
            els.append(rect(x, y, cell, cell,
                            fill="#eaf0fd" if filled else BG,
                            stroke=MUTED, sw=1.2, rx=0))
            els.append(text(x + cell / 2, y + cell / 2 + 6,
                            "1" if filled else "0", size=16,
                            color=INK if filled else MUTED,
                            bold=filled))
    # обведення блоку з двох сусідніх одиниць (стовпець "11", рядки 00 і 01)
    bx = gx + 2 * cell
    by = gy + 0 * cell
    els.append(rect(bx + 5, by + 5, cell - 10, 2 * cell - 10,
                    fill="none", stroke=POS, sw=3, rx=10))
    # стрілка й підпис: змінна, що змінюється всередині блоку, — зайва
    els.append(arrow(bx + cell + 8, by + cell, gx + 4 * cell + 30, by + cell,
                     color=POS, sw=2.2))
    b, w, h = textbox(gx + 4 * cell + 118, by + cell,
                      "усередині блоку\nміняється лиш c →\nвона зайва",
                      size=12, fill="#fdecea", stroke=POS, color=POS)
    els.append(b)

    els.append(text(W / 2, gy + 4 * cell + 40,
                    "сусідні клітинки різняться ОДНИМ входом (код Ґрея);",
                    size=12, color=INK))
    els.append(text(W / 2, gy + 4 * cell + 60,
                    "злиплі одиниці → той вхід зникає з формули",
                    size=12, color=INK))
    els.append(text(W / 2, gy + 4 * cell + 84,
                    "стеля методу — око людини читає блоки лише до ~4–5 входів",
                    size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "karnaugh.svg"), W, H, *els)


# ── 7. timeline (вставка hist) ──────────────────────────────────────────────
def fig_timeline():
    W, H = 760, 400
    els = []
    els.append(text(W / 2, 30, "Дорога до синтезу: віха за віхою знімає стелю",
                    size=16, bold=True))

    axis_y = 150
    x0, x1 = 60, 700
    els.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    els.append(arrow(x1 - 4, axis_y, x1 + 30, axis_y, color=INK, sw=2.5))

    # чотири віхи: (x, рік, назва, що зняла, у що вперлася)
    miles = [
        (150, "1953", "карта Карно",
         "рутина ока", "стеля ~4–5 входів"),
        (330, "1956", "Квайн–Мак-Класкі",
         "стеля ока", "обчислювальний вибух"),
        (510, "1982–84", "Espresso",
         "вибух", "лише два яруси"),
        (660, "1987", "Design Compiler",
         "усе решту", "— перелом"),
    ]
    for x, yr, name, gone, wall in miles:
        els.append(circle(x, axis_y, 8, fill=NEG, stroke=INK, sw=2))
        els.append(text(x, axis_y - 44, yr, size=15, color=NEG, bold=True))
        els.append(text(x, axis_y - 24, name, size=12, color=INK, bold=True))
        # знизу — «зняла» (зелене) і «вперлася» (сіре)
        els.append(text(x, axis_y + 34, "зняла:", size=10, color=MUTED))
        els.append(text(x, axis_y + 50, gone, size=12, color=FIELD, bold=True))
        els.append(text(x, axis_y + 74, "→ уперлась:", size=10, color=MUTED))
        els.append(text(x, axis_y + 90, wall, size=11, color=POS))

    # нижня стрілка-вектор
    els.append(arrow(x0 + 20, axis_y + 128, x1 - 10, axis_y + 128,
                     color=MUTED, sw=2))
    els.append(text(W / 2, axis_y + 122,
                    "щораз менше ручної праці   ·   щораз більший масштаб",
                    size=13, color=INK, bold=True))
    els.append(text(W / 2, axis_y + 152,
                    "від опису поведінки — до готової багатоярусної схеми під будь-яку технологію",
                    size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *els)


if __name__ == "__main__":
    fig_synth_vs_compile()
    fig_inference()
    fig_latch_infer()
    fig_tech_map()
    fig_netlist()
    fig_karnaugh()
    fig_timeline()
    print("OK: 7 SVG in", OUT)
