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


if __name__ == '__main__':
    fig_decorator_wrapping()
    fig_inherit_vs_decorate()
    fig_java_io_explosion()
    print("figs done")
