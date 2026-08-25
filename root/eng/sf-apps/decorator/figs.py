# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Обгортання шарами: виклик іде всередину, внески складаються назад ────────
def fig_decorator_wrapping():
    W, H = 1120, 560
    frags = []

    frags.append(text(W / 2, 40, "Декоратор: виклик крізь шари, внески назад",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62, "усі шари мають один інтерфейс Beverage",
                      size=12, color=MUTED))

    # Три концентричні шари + ядро. Центр зсунуто ліворуч, праворуч — підрахунок.
    cx, cy = 388, 320
    # зовнішній: Cinnamon (червоний), середній: Milk (зелений), ядро: Coffee
    layers = [
        (210, "Cinnamon", POS, "#fdecea"),   # зовнішня обгортка
        (150, "Milk",     FIELD, "#eaf7ef"),  # середня обгортка
    ]
    # намалюємо від зовнішнього до внутрішнього (великі першими)
    for r, name, color, fill in layers:
        frags.append(rect(cx - r, cy - r * 0.72, 2 * r, 2 * r * 0.72,
                          fill=fill, stroke=color, sw=2, rx=16))
        # підпис шару — угорі всередині рамки, повз інші написи
        frags.append(text(cx, cy - r * 0.72 + 22, name, size=13.5,
                          bold=True, color=color))

    # ядро — Coffee
    core, cw, ch = textbox(cx, cy, ["Coffee", "cost = 20"], size=13,
                           bold=True, fill=FILL, stroke=LINE, sw=1.8, min_w=140)
    frags.append(core)

    # позначки внеску кожного шару (праворуч від ядра, всередині своїх рамок)
    frags.append(text(cx + 96, cy, "+5", size=14, bold=True, color=FIELD))
    frags.append(text(cx + 156, cy, "+3", size=14, bold=True, color=POS))

    # стрілка «виклик іде всередину» — зверху, повз написи шарів (ліворуч від центру)
    frags.append(text(cx - 168, cy - 250 + 8, "cost() ↓ всередину",
                      size=12, color=MUTED, anchor="start"))
    frags.append(arrow(cx - 250, cy - 236, cx - 250, cy - 20, color=MUTED, sw=1.6))

    # ── Праворуч: підрахунок на зворотному шляху ─────────────────────────────
    px = 760
    frags.append(text(px + 130, 118, "На зворотному шляху назовні:",
                      size=13, bold=True, color=INK, anchor="middle"))
    steps = [
        ("Coffee", "20", LINE, 168),
        ("+ Milk", "25", FIELD, 226),
        ("+ Cinnamon", "28", POS, 284),
    ]
    for label, total, color, ry in steps:
        b = fitbox(px, ry, 260, 44,
                   "%s  →  %s" % (label, total),
                   size=13.5, bold=True, fill="#fbfcfd", stroke=color, sw=1.6, pad=10)
        frags.append(b)
        if ry < 280:
            frags.append(arrow(px + 130, ry + 44, px + 130, ry + 58,
                              color="#c4cad2", sw=1.5))

    frags.append(text(px + 130, 366, "разом = 28", size=15, bold=True, color=INK))
    frags.append(text(px + 130, 392,
                     "кожен шар додав своє поверх нижнього",
                     size=11.5, color=MUTED))

    render(os.path.join(IMG, 'decorator-wrapping.svg'), W, H, *frags)


# ── Дерево спадкування (2ⁿ) проти пласких декораторів (n) ────────────────────
def fig_inherit_vs_decorate():
    W, H = 1180, 660
    frags = []

    frags.append(line(W / 2, 88, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════ ЛІВОРУЧ: спадкування — вибух класів ═══════
    lcx = W / 4
    frags.append(text(lcx, 52, "Спадкуванням", size=17, bold=True, color=NEG))
    frags.append(text(lcx, 74, "клас на кожну комбінацію — 2ⁿ", size=12, color=MUTED))

    # корінь
    root, rw, rh = textbox(lcx, 120, "Coffee", size=12.5, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=110)
    frags.append(root)

    # 8 листків комбінацій у два ряди по 4, з широким запасом
    combos = ["+M", "+C", "+S",
              "+M+C", "+M+S", "+C+S",
              "+M+C+S", "(1)"]
    combos[-1] = "Coffee"  # сам корінь як окремий «клас без добавок» для наочності
    # розкладемо 7 реальних комбінацій під коренем
    leaf_labels = ["Coffee+M", "Coffee+C", "Coffee+S", "Coffee+M+C",
                   "Coffee+M+S", "Coffee+C+S", "Coffee+M+C+S"]
    xs = [lcx - 195, lcx - 65, lcx + 65, lcx + 195]
    row1_y, row2_y = 240, 322
    positions = [(xs[0], row1_y), (xs[1], row1_y), (xs[2], row1_y), (xs[3], row1_y),
                 (xs[0] + 65, row2_y), (xs[1] + 65, row2_y), (xs[2] + 65, row2_y)]
    for (lx, ly), lab in zip(positions, leaf_labels):
        frags.append(line(lcx, 120 + rh / 2, lx, ly - 18, color=NEG, sw=1.0))
        b = fitbox(lx - 62, ly - 16, 124, 34, lab, size=10.5,
                   fill="#eaf0fd", stroke=NEG, sw=1.3, pad=5)
        frags.append(b)

    frags.append(text(lcx, 400, "8 класів (2³)", size=15, bold=True, color=NEG))
    frags.append(text(lcx, 424, "застигло на етапі компіляції", size=12, color=MUTED))
    frags.append(text(lcx, 448, "нова добавка — число подвоюється", size=12, color=INK))

    # ═══════ ПРАВОРУЧ: декоратор — n класів ═══════
    rcx = 3 * W / 4
    frags.append(text(rcx, 52, "Декоратором", size=17, bold=True, color=FIELD))
    frags.append(text(rcx, 74, "клас на властивість — n; решта в рантаймі",
                      size=12, color=MUTED))

    # чотири пласкі класи в ряд
    cls = [("Coffee", rcx - 210), ("Milk", rcx - 70),
           ("Cinnamon", rcx + 78), ("Syrup", rcx + 210)]
    cls_y = 150
    for nm, kx in cls:
        col = FIELD if nm != "Coffee" else LINE
        b = fitbox(kx - 62, cls_y - 18, 124, 40, nm, size=12, bold=True,
                   fill="#eaf7ef" if nm != "Coffee" else FILL,
                   stroke=col, sw=1.5, pad=6)
        frags.append(b)
    frags.append(text(rcx, cls_y + 46, "4 класи — по одному на добавку",
                      size=12.5, bold=True, color=FIELD))

    # приклад складання у рантаймі
    frags.append(text(rcx, 264, "будь-яка комбінація — нанизуванням:",
                      size=12.5, color=INK))
    ex = fitbox(rcx - 240, 284, 480, 52,
                "Syrup( Milk( Coffee() ) )",
                size=15, bold=True, fill="#f4fbf7", stroke=FIELD, sw=1.7, pad=12)
    frags.append(ex)
    frags.append(text(rcx, 366, "усі 8 поєднань — без єдиного нового класу",
                      size=12.5, bold=True, color=INK))
    frags.append(text(rcx, 390, "рішення відкладене в рантайм", size=12, color=MUTED))

    # ── нижній рядок: підсумок числа ─────────────────────────────────────────
    band_y = H - 96
    frags.append(line(50, band_y - 16, W - 50, band_y - 16, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, band_y + 6, "n незалежних добавок — скільки класів?",
                      size=14, bold=True, color=INK))
    frags.append(text(lcx, band_y + 34, "2ⁿ  (вибух)", size=14, bold=True, color=NEG))
    frags.append(text(rcx, band_y + 34, "n  (лінійно)", size=14, bold=True, color=FIELD))

    render(os.path.join(IMG, 'inherit-vs-decorate.svg'), W, H, *frags)


# ── java.io: вибух 2ⁿ проти пласкої ієрархії обгорток ────────────────────────
def fig_java_io_explosion():
    W, H = 1220, 772
    frags = []

    frags.append(text(W / 2, 40, "java.io: чому обгортка, а не дерево підкласів",
                      size=17, bold=True, color=INK))

    frags.append(line(W / 2, 74, W / 2, H - 118, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════ ЛІВОРУЧ: спадкування — 2ⁿ ═══════
    lcx = W / 4
    frags.append(text(lcx, 100, "Спадкуванням", size=16, bold=True, color=NEG))
    frags.append(text(lcx, 122, "клас на кожне поєднання можливостей",
                      size=12, color=MUTED))

    # осі поєднання — рядки-множники з широким запасом
    axes = [
        ("джерело", "файл · пам'ять · мережа · труба", "×4"),
        ("буфер", "є / нема", "×2"),
        ("розпакування", "gzip / deflate / нема", "×3"),
        ("типізація", "Data / нема", "×2"),
        ("підрахунок", "рядків / контр.сума / нема", "×3"),
    ]
    ay = 168
    for name, states, mult in axes:
        frags.append(fitbox(lcx - 250, ay - 18, 400, 38,
                            "%s:  %s" % (name, states),
                            size=12, fill="#eef2fb", stroke=NEG, sw=1.2, pad=8))
        frags.append(text(lcx + 208, ay + 4, mult, size=15, bold=True, color=NEG,
                          anchor="middle"))
        ay += 52

    frags.append(line(lcx - 250, ay - 8, lcx + 235, ay - 8, color=NEG, sw=1.3))
    frags.append(text(lcx, ay + 22, "4 · 2 · 3 · 2 · 3  =  144 класи",
                      size=16, bold=True, color=NEG))
    frags.append(text(lcx, ay + 46, "і кожна нова вісь МНОЖИТЬ це число",
                      size=12, color=INK))
    frags.append(text(lcx, ay + 68, "застигло на етапі компіляції",
                      size=11.5, color=MUTED))

    # ═══════ ПРАВОРУЧ: декоратор — пласка ієрархія + нанизування ═══════
    rcx = 3 * W / 4
    frags.append(text(rcx, 100, "Декоратором", size=16, bold=True, color=FIELD))
    frags.append(text(rcx, 122, "компонент · базовий декоратор · обгортки",
                      size=12, color=MUTED))

    # компонент — двома рядками, роль усередині рамки (щоб не було вільних написів під лініями)
    comp, cw, chh = textbox(rcx, 176, ["InputStream", "компонент (абстрактний)"],
                            size=12.5, bold=True, fill="#eef7f1", stroke=INK,
                            sw=1.8, min_w=220)
    frags.append(comp)

    # базовий декоратор — роль теж усередині рамки
    frags.append(arrow(rcx, 176 + chh / 2, rcx, 232, color="#c4cad2", sw=1.5))
    fbase, fw, fh = textbox(rcx, 262,
                            ["FilterInputStream", "базовий декоратор — тримає in, делегує"],
                            size=12, bold=True, fill="#f4fbf7", stroke=FIELD,
                            sw=1.7, min_w=300)
    frags.append(fbase)

    # обгортки в ряд (з широким запасом між ними); лінії стартують нижче рамки — повз написи
    wraps = ["Buffered", "GZIP", "Cipher", "Data"]
    wy = 350
    fan_y = 262 + fh / 2 + 6      # старт нижче нижньої межі рамки FilterInputStream
    wxs = [rcx - 207, rcx - 69, rcx + 69, rcx + 207]
    for nm, wx in zip(wraps, wxs):
        frags.append(line(rcx, fan_y, wx, wy - 18, color=FIELD, sw=1.0))
        frags.append(fitbox(wx - 62, wy - 16, 124, 34, nm, size=11,
                            fill="#f4fbf7", stroke=FIELD, sw=1.3, pad=5))
    frags.append(text(rcx, wy + 40, "по одній обгортці на вісь",
                      size=12, bold=True, color=FIELD))

    # приклад нанизування — стос
    frags.append(text(rcx, wy + 78, "будь-яке з 144 поєднань — нанизуванням:",
                      size=12, color=INK))
    chain = [
        ("new FileInputStream(path)", "джерело", LINE),
        ("new BufferedInputStream(…)", "+ буфер", FIELD),
        ("new GZIPInputStream(…)", "+ розпакування", FIELD),
        ("new DataInputStream(…)", "+ readInt / readUTF", FIELD),
    ]
    ry = wy + 96
    box_l, box_w = rcx - 250, 300
    for code_s, note, col in chain:
        frags.append(fitbox(box_l, ry, box_w, 36, code_s,
                            size=11.5, bold=True, fill="#fbfcfd", stroke=col,
                            sw=1.5, pad=8))
        # підпис — праворуч ВІД рамки, повз неї
        frags.append(text(box_l + box_w + 12, ry + 22, note, size=10.5,
                          color=MUTED, anchor="start"))
        ry += 44

    # ── нижній рядок: підсумок ───────────────────────────────────────────────
    band_y = H - 84
    frags.append(line(50, band_y - 18, W - 50, band_y - 18, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, band_y + 4, "n незалежних осей вводу — скільки класів?",
                      size=14, bold=True, color=INK))
    frags.append(text(lcx, band_y + 34, "2ⁿ  →  сотні (вибух)", size=14,
                      bold=True, color=NEG))
    frags.append(text(rcx, band_y + 34, "n  →  ~11 (лінійно)", size=14,
                      bold=True, color=FIELD))

    render(os.path.join(IMG, 'java-io-explosion.svg'), W, H, *frags)


# ── (детальна) SELF-проблема: відкрита рекурсія проти обірваного self ─────────
def fig_self_problem():
    W, H = 1240, 700
    f = []
    f.append(text(W / 2, 34, "Відкрита рекурсія проти обірваного self",
                  size=18, bold=True, color=INK))
    f.append(text(W / 2, 58, "коли метод усередині кличе this.read()",
                  size=12.5, color=MUTED))
    f.append(line(W / 2, 92, W / 2, H - 44, color="#d0d5db", sw=1.2, dash="6,6"))

    # ── ЛІВОРУЧ: спадкування ─────────────────────────────
    lx = 312
    f.append(text(lx, 122, "Спадкування", size=16, bold=True, color=FIELD))
    f.append(text(lx, 144, "self = весь об'єкт → перекриття виграє",
                  size=11.5, color=MUTED))
    f.append(rect(78, 164, 468, 232, fill="#f4fbf7", stroke=INK, sw=1.6, rx=12))
    f.append(text(lx, 190, "один об'єкт (нащадок)", size=12.5, bold=True, color=INK))
    f.append(fitbox(112, 208, 400, 50, "readAll() { … this.read() … }",
                    size=13, fill=BG, stroke=LINE, sw=1.4))
    f.append(fitbox(112, 300, 400, 50, "read()  ← перекрито: ВЕЛИКА",
                    size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(arrow(528, 258, 528, 300, color=FIELD, sw=1.7))
    f.append(text(lx, 384, "this.read() → перекритий read()", size=11.5, color=INK))
    f.append(text(lx, 438, "✓ readAll() теж дає ВЕЛИКІ", size=13, bold=True, color=FIELD))

    # ── ПРАВОРУЧ: делегування ─────────────────────────────
    rx = 928
    f.append(text(rx, 122, "Делегування (декоратор)", size=16, bold=True, color=POS))
    f.append(text(rx, 144, "self = внутрішній → decorate обійдено",
                  size=11.5, color=MUTED))
    cx = 858
    steps = [
        ("D.readAll()  — делегує вниз", BG, LINE, 178),
        ("C.readAll() { this.read() }", BG, LINE, 268),
        ("this.read() = C.read()", "#eef2f6", MUTED, 358),
        ("→ малі літери  ✗", "#fdecea", POS, 448),
    ]
    for s, fill, col, y in steps:
        f.append(fitbox(cx - 152, y - 24, 304, 48, s, size=12.5,
                        bold=(col == POS), fill=fill, stroke=col, sw=1.5))
    for y in (202, 292, 382):
        f.append(arrow(cx, y, cx, y + 42, color=MUTED, sw=1.6))
    f.append(fitbox(1016, 156, 208, 58, ["D.read() ВЕЛИКА", "не викликана"],
                    size=11.5, bold=True, fill="#fbfcfd", stroke=POS, sw=1.4, rx=8))
    f.append(arrow(1012, 184, 1016, 184, color=POS, sw=1.5))
    f.append(text(rx, 516, "перекритий read() у D — поза шляхом виклику",
                  size=12, color=INK))

    render(os.path.join(IMG, 'self-problem.svg'), W, H, *f)


# ── (детальна) Онієн: що шар робить навколо делегації ────────────────────────
def fig_onion_model():
    W, H = 1180, 600
    f = []
    f.append(text(W / 2, 34, "Що шар декоратора робить навколо делегації",
                  size=18, bold=True, color=INK))
    f.append(text(W / 2, 58, "перед викликом · після · замість — інтерфейс незмінний",
                  size=12.5, color=MUTED))

    # ── ЛІВОРУЧ: онієн ───────────────────────────────────
    ocx = 300
    f.append(rect(120, 150, 360, 300, fill="#fdecea", stroke=POS, sw=1.8, rx=16))
    f.append(text(ocx, 178, "шар-декоратор", size=13, bold=True, color=POS))
    f.append(rect(212, 268, 176, 120, fill=FILL, stroke=LINE, sw=1.6, rx=10))
    f.append(text(ocx, 322, "компонент", size=12.5, bold=True, color=INK))
    f.append(text(ocx, 344, "справжня робота", size=11, color=MUTED))
    f.append(text(ocx, 234, "1 · ДО делегації", size=12, bold=True, color=INK))
    f.append(text(ocx, 424, "3 · ПІСЛЯ делегації", size=12, bold=True, color=INK))
    f.append(arrow(ocx, 116, ocx, 150, color=MUTED, sw=1.7))
    f.append(text(ocx, 108, "виклик", size=11, color=MUTED))
    f.append(arrow(ocx, 450, ocx, 486, color=MUTED, sw=1.7))
    f.append(text(ocx, 506, "результат", size=11, color=MUTED))
    f.append(arrow(168, 250, 168, 268, color=POS, sw=1.4))
    f.append(arrow(432, 388, 432, 406, color=POS, sw=1.4))

    # ── ПРАВОРУЧ: чотири режими ──────────────────────────
    modes = [
        ("ДО", "перевірити вхід, залогувати, старт таймера", FIELD, 148),
        ("ПІСЛЯ", "змінити чи перевірити результат, стоп таймера", FIELD, 224),
        ("НАВКОЛО", "змінити аргументи на вході І відповідь на виході", NEG, 300),
        ("ЗАМІСТЬ (short-circuit)", "не делегувати: кеш-влучення, відмова доступу", POS, 376),
    ]
    for tag, desc, col, y in modes:
        f.append(rect(560, y, 500, 60, fill="#fbfcfd", stroke=col, sw=1.5, rx=8))
        f.append(text(582, y + 26, tag, size=13, bold=True, color=col, anchor="start"))
        f.append(text(582, y + 48, desc, size=11.5, color=INK, anchor="start"))
    f.append(text(810, 474, "усі чотири лишають інтерфейс незмінним",
                  size=12.5, bold=True, color=INK))
    render(os.path.join(IMG, 'onion-model.svg'), W, H, *f)


# ── (детальна) Декоратор серед структурних сусідів ──────────────────────────
def fig_pattern_neighbors():
    W, H = 1260, 560
    f = []
    f.append(text(W / 2, 36, "Декоратор серед структурних сусідів",
                  size=18, bold=True, color=INK))
    f.append(text(W / 2, 60, "однаковий кістяк-обгортка — різний намір",
                  size=12.5, color=MUTED))

    cols = [("Патерн", 168), ("Інтерфейс", 200), ("Скільки обгортає", 244), ("Намір", 560)]
    x0, y0, rowh = 40, 96, 66
    cx = x0
    for name, w in cols:
        f.append(fitbox(cx, y0, w, 44, name, size=13, bold=True,
                        fill="#eef2f6", stroke=INK, sw=1.4))
        cx += w
    rows = [
        ("Декоратор", "зберігає", "один", "додає поведінку, шарами", True),
        ("Проксі", "зберігає", "один", "керує доступом: лінь, права, мережа", False),
        ("Компонувальник", "зберігає", "багато (дерево)", "збирає однотипні в одне ціле", False),
        ("Адаптер", "ЗМІНЮЄ", "один", "конвертує чужий інтерфейс у потрібний", False),
        ("Стратегія", "інша вісь", "вкладений алгоритм", "підмінює нутро, не обгортає", False),
    ]
    ry = y0 + 48
    for pat, iface, card, intent, hot in rows:
        cx = x0
        for (name, w), v in zip(cols, (pat, iface, card, intent)):
            f.append(fitbox(cx, ry, w, rowh - 8, v, size=12,
                            bold=(hot and name == "Патерн"),
                            fill="#f4fbf7" if hot else BG,
                            stroke=FIELD if hot else LINE, sw=1.4 if hot else 1.1))
            cx += w
        ry += rowh
    f.append(text(W / 2, ry + 20,
                  "адаптер міняє інтерфейс; стратегія — плагін нутра; решта — обгортки того самого інтерфейсу",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, 'pattern-neighbors.svg'), W, H, *f)


# ── (proj) Стос HTTP-middleware: виконання онієном і два обриви ─────────────
def fig_middleware_onion():
    W, H = 1260, 482
    f = []
    f.append(text(W / 2, 34, "Стос HTTP-middleware: виконання онієном і два обриви",
                  size=18, bold=True, color=INK))
    f.append(text(W / 2, 58,
                  "кожен шар робить «ДО», делегує глибше, тоді «ПІСЛЯ» — та Auth і Cache можуть обірвати ланцюг",
                  size=12.5, color=MUTED))

    # «до»-стрілка згори
    f.append(arrow(60, 100, 1180, 100, color=FIELD, sw=2))
    f.append(text(60, 90, "запит → всередину: «ДО», тоді next()",
                  size=12, color=FIELD, anchor="start", bold=True))

    names = [
        ("Recover", "паніка → 500", POS),
        ("Logger", "метод, шлях", INK),
        ("Timer", "старт годинника", INK),
        ("Auth", "право? ні → 401", POS),
        ("Gzip", "стиснути тіло", NEG),
        ("Cache", "влучив → віддай", FIELD),
    ]
    bx, by, bw, bh, step = 60, 125, 150, 130, 160
    for i, (nm, role, col) in enumerate(names):
        x = bx + i * step
        f.append(rect(x, by, bw, bh, fill="#fbfcfd", stroke=col, sw=1.8, rx=12))
        f.append(text(x + bw / 2, by + 60, nm, size=15, bold=True, color=col))
        f.append(text(x + bw / 2, by + 84, role, size=11, color=MUTED))
    hx = bx + 6 * step
    f.append(rect(hx, by, bw, bh, fill="#eef2f6", stroke=INK, sw=2, rx=12))
    f.append(text(hx + bw / 2, by + 60, "Діловий", size=14, bold=True, color=INK))
    f.append(text(hx + bw / 2, by + 82, "обробник", size=14, bold=True, color=INK))

    # «після»-стрілка знизу
    f.append(arrow(1180, 285, 60, 285, color=NEG, sw=2))
    f.append(text(1180, 305, "відповідь ← назовні: «ПІСЛЯ»",
                  size=12, color=NEG, anchor="end", bold=True))

    # обрив 1 — Auth (червоний): відвід від коробки + стрілка назад уліво
    ax = bx + 3 * step + bw / 2
    f.append(line(ax, by + bh, ax, 356, color=POS, sw=1.6))
    f.append(arrow(ax, 356, 70, 356, color=POS, sw=1.8))
    f.append(text(80, 336,
                  "Auth: 401 — next() не викликано; Cache, Gzip, обробник запиту не бачать",
                  size=11, color=POS, anchor="start", bold=True))

    # обрив 2 — Cache (зелений)
    kx = bx + 5 * step + bw / 2
    f.append(line(kx, by + bh, kx, 406, color=FIELD, sw=1.6))
    f.append(arrow(kx, 406, 70, 406, color=FIELD, sw=1.8))
    f.append(text(80, 386,
                  "Cache: влучення — тіло з кешу; обробник (похід у базу) не виконується",
                  size=11, color=FIELD, anchor="start", bold=True))

    f.append(text(W / 2, 452,
                  "обрив = шар сам вертає відповідь і не кличе next(); хто зовні — той дістає шанс обірвати першим",
                  size=12, color=INK, bold=True))
    render(os.path.join(IMG, 'middleware-onion.svg'), W, H, *f)


# ── (proj) Порядок шарів важить: Auth зовні/всередині за Cache ──────────────
def fig_order_matters():
    W, H = 1120, 502
    f = []
    f.append(text(W / 2, 34, "Порядок шарів — не смак, а правильність",
                  size=18, bold=True, color=INK))
    f.append(text(W / 2, 58, "той самий набір middleware, дві розстановки Auth і Cache",
                  size=12.5, color=MUTED))

    def stack(cx, head, hcol, layers, hi):
        f.append(text(cx, 92, head, size=15, bold=True, color=hcol))
        y = 112
        for i, nm in enumerate(layers):
            isH = (nm == "Обробник")
            hot = hi.get(i)
            if isH:
                fill, stroke, tcol, bold, sw = "#eef2f6", INK, INK, True, 1.8
            elif hot == "g":
                fill, stroke, tcol, bold, sw = "#f4fbf7", FIELD, FIELD, True, 1.8
            elif hot == "gl":
                fill, stroke, tcol, bold, sw = "#f4fbf7", FIELD, INK, False, 1.8
            elif hot == "r":
                fill, stroke, tcol, bold, sw = "#fdecea", POS, POS, True, 1.8
            elif hot == "rl":
                fill, stroke, tcol, bold, sw = "#fdecea", POS, INK, False, 1.8
            else:
                fill, stroke, tcol, bold, sw = BG, LINE, INK, False, 1.1
            f.append(rect(cx - 130, y, 260, 38, fill=fill, stroke=stroke, sw=sw, rx=8))
            f.append(text(cx, y + 25, nm, size=13.5, bold=bold, color=tcol))
            y += 46

    stack(300, "ПРАВИЛЬНО", FIELD,
          ["Recover", "Logger", "Auth", "Cache", "Обробник"],
          {2: "g", 3: "gl"})
    stack(820, "НЕБЕЗПЕЧНО", POS,
          ["Recover", "Logger", "Cache", "Auth", "Обробник"],
          {2: "r", 3: "rl"})

    f.append(fitbox(140, 366, 320, 82,
                    "Auth зовні за Cache:\nкеш віддає відповідь лише тому,\nкого авторизація вже пропустила.",
                    size=12, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    f.append(fitbox(660, 366, 320, 82,
                    "Cache зовні за Auth: влучення\nповертає збережене ДО перевірки прав —\nчужий бачить чужі дані.",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5))
    render(os.path.join(IMG, 'order-matters.svg'), W, H, *f)


# ── (math) Коли шари комутують: квадрат замикається / гілки розходяться ──────
def fig_commute_square():
    W, H = 1240, 600
    f = []
    f.append(text(W / 2, 38, "Коли два шари можна переставити місцями",
                  size=17, bold=True, color=INK))
    f.append(text(W / 2, 60, "переставні тоді й лише тоді, коли комутують їхні функції-ефекти",
                  size=12.5, color=MUTED))
    f.append(line(W / 2, 92, W / 2, H - 64, color="#d0d5db", sw=1.2, dash="6,6"))

    def node(cx, cy, s, col=LINE, fill=FILL):
        b, w, h = textbox(cx, cy, s, size=13, bold=True, fill=fill,
                          stroke=col, sw=1.6, min_w=66)
        f.append(b)

    # ═══ ЛІВОРУЧ: ціна — квадрат замикається (комутують) ═══
    lcx = 316
    f.append(text(lcx, 122, "Ціна напою", size=15, bold=True, color=FIELD))
    f.append(text(lcx, 143, "(ℤ, +) — комутативна група", size=11.5, color=MUTED))

    TLx, TRx, TYy, BYy = 196, 436, 210, 410
    node(TLx, TYy, "20")
    node(TRx, TYy, "25")
    node(TLx, BYy, "23")
    node(TRx, BYy, "28", col=FIELD, fill="#eaf7ef")
    f.append(arrow(TLx + 33, TYy, TRx - 33, TYy, color=MUTED, sw=1.6))     # верх
    f.append(arrow(TLx + 33, BYy, TRx - 33, BYy, color=MUTED, sw=1.6))     # низ
    f.append(arrow(TLx, TYy + 20, TLx, BYy - 20, color=MUTED, sw=1.6))     # ліворуч
    f.append(arrow(TRx, TYy + 20, TRx, BYy - 20, color=MUTED, sw=1.6))     # праворуч
    f.append(text(lcx, TYy - 22, "+5 (молоко)", size=11, color=INK))
    f.append(text(lcx, BYy + 30, "+5 (молоко)", size=11, color=INK))
    f.append(text(TLx - 14, (TYy + BYy) / 2 + 4, "+3 (кориця)", size=11,
                  color=INK, anchor="end"))
    f.append(text(TRx + 14, (TYy + BYy) / 2 + 4, "+3 (кориця)", size=11,
                  color=INK, anchor="start"))
    f.append(text(lcx, 472, "обидва порядки → 28", size=12.5, bold=True, color=FIELD))
    f.append(text(lcx, 494, "d₁ ∘ d₂ = d₂ ∘ d₁   ✓", size=12.5, bold=True, color=INK))

    # ═══ ПРАВОРУЧ: опис — гілки розходяться (не комутують) ═══
    rcx = 924
    f.append(text(rcx, 122, "Опис напою", size=15, bold=True, color=POS))
    f.append(text(rcx, 143, "Σ*, · — вільний моноїд (некомутативний)",
                  size=11.5, color=MUTED))

    Sx, Sy = 742, 308
    n1x, n1y = 906, 214
    n2x, n2y = 1086, 214
    n3x, n3y = 906, 402
    n4x, n4y = 1086, 402
    node(Sx, Sy, "s")
    node(n1x, n1y, "s·m")
    node(n2x, n2y, "s·m·c", col=POS, fill="#fdecea")
    node(n3x, n3y, "s·c")
    node(n4x, n4y, "s·c·m", col=POS, fill="#fdecea")
    f.append(arrow(Sx + 30, Sy - 12, n1x - 38, n1y + 16, color=MUTED, sw=1.5))
    f.append(arrow(n1x + 38, n1y, n2x - 38, n2y, color=MUTED, sw=1.5))
    f.append(arrow(Sx + 30, Sy + 12, n3x - 38, n3y - 16, color=MUTED, sw=1.5))
    f.append(arrow(n3x + 38, n3y, n4x - 38, n4y, color=MUTED, sw=1.5))
    f.append(text(800, 262, "·m", size=12, bold=True, color=INK))
    f.append(text(996, 196, "·c", size=12, bold=True, color=INK))
    f.append(text(800, 356, "·c", size=12, bold=True, color=INK))
    f.append(text(996, 424, "·m", size=12, bold=True, color=INK))
    f.append(text(n2x, (n2y + n4y) / 2 + 10, "≠", size=30, bold=True, color=POS))
    f.append(text(rcx, 472, "s — опис;  m = « + молоко»,  c = « + кориця»",
                  size=11, color=MUTED))
    f.append(text(rcx, 494, "s·m·c ≠ s·c·m   →   переставити НЕ можна   ✗",
                  size=12.5, bold=True, color=POS))

    render(os.path.join(IMG, 'commute-square.svg'), W, H, *f)


if __name__ == '__main__':
    fig_decorator_wrapping()
    fig_inherit_vs_decorate()
    fig_java_io_explosion()
    fig_self_problem()
    fig_onion_model()
    fig_pattern_neighbors()
    fig_middleware_onion()
    fig_order_matters()
    fig_commute_square()
    print("figs done")
