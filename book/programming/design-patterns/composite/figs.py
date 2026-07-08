# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_tree():
    """Дерево частина-ціле: тека тримає теки й файли; операція рекурсивно спускається."""
    W, H = 780, 430
    frags = []

    # вузли: (cx, cy, підпис, тип) ; тип 'comp' = композит (тека), 'leaf' = лист (файл)
    nodes = {
        'root':  (390,  70, "проєкт/", 'comp'),
        'src':   (200, 190, "src/",    'comp'),
        'docs':  (585, 190, "docs/",   'comp'),
        'main':  ( 95, 320, "main.ts", 'leaf'),
        'util':  (270, 320, "util.ts", 'leaf'),
        'ui':    (200, 320, "ui/",     'comp'),   # ще один композит під src
        'guide': (500, 320, "guide.md",'leaf'),
        'api':   (670, 320, "api.md",  'leaf'),
    }
    edges = [('root','src'), ('root','docs'),
             ('src','main'), ('src','ui'), ('src','util'),
             ('docs','guide'), ('docs','api')]

    boxes = {}
    for key, (cx, cy, label, kind) in nodes.items():
        fill = "#eaf3ff" if kind == 'comp' else "#f4f6f8"
        stroke = NEG if kind == 'comp' else LINE
        body, w, h = textbox(cx, cy, label, size=15, pad=11, fill=fill,
                             stroke=stroke, sw=2 if kind == 'comp' else 1.5, min_w=86)
        boxes[key] = (cx, cy, w, h, body)

    # лінії зв'язку (від низу батька до верху дитини) — під рамками
    for a, b in edges:
        ax, ay, aw, ah, _ = boxes[a]
        bx, by, bw, bh, _ = boxes[b]
        frags.append(line(ax, ay + ah / 2, bx, by - bh / 2, color=MUTED, sw=1.6))

    for key in nodes:
        frags.append(boxes[key][4])

    # легенда — праворуч угорі, з запасом від дерева
    lx, ly = 40, 40
    frags.append(circle(lx, ly, 7, fill="#eaf3ff", stroke=NEG, sw=2))
    frags.append(text(lx + 16, ly + 5, "композит (тримає дітей)", size=13,
                      color=INK, anchor="start"))
    frags.append(circle(lx, ly + 26, 7, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(lx + 16, ly + 31, "лист (кінцевий, без дітей)", size=13,
                      color=INK, anchor="start"))

    render(os.path.join(IMG, 'composite-tree.svg'), W, H, *frags)


def fig_interface():
    """Спільний інтерфейс Component; Leaf і Composite реалізують; Composite тримає список Component."""
    W, H = 760, 440
    frags = []

    # Component — угорі, зсунутий уліво, щоб праворуч лишилося місце на петлю
    comp_body, cw, ch = textbox(300, 70, ["Component", "+ operation()"],
                                size=15, pad=14, fill="#f0f0f0", stroke=INK, sw=2,
                                min_w=210)
    # Leaf — ліворуч знизу
    leaf_body, lw, lh = textbox(170, 260, ["Leaf", "+ operation()"],
                                size=15, pad=14, fill="#f4f6f8", stroke=LINE, min_w=180)
    # Composite — праворуч знизу
    scx, scy = 470, 260
    csite_body, sw_, sh = textbox(scx, scy,
                                  ["Composite", "+ operation()", "+ add(Component)",
                                   "+ remove(Component)"],
                                  size=14, pad=14, fill="#eaf3ff", stroke=NEG, sw=2,
                                  min_w=210)

    # стрілки реалізації (звичайні стрілки до Component)
    frags.append(arrow(170, 260 - lh / 2, 260, 70 + ch / 2, color=MUTED, sw=1.8))
    frags.append(arrow(scx - 30, scy - sh / 2, 340, 70 + ch / 2, color=MUTED, sw=1.8))
    frags.append(text(195, 165, "реалізує", size=12, color=MUTED, anchor="middle"))
    frags.append(text(430, 165, "реалізує", size=12, color=MUTED, anchor="middle"))

    frags.append(comp_body)
    frags.append(leaf_body)
    frags.append(csite_body)

    # ключова петля: Composite тримає СПИСОК Component (рекурсивне самопосилання).
    # Ведемо далеко праворуч (x=690), повз усі рамки й написи, і заходимо в Component
    # згори (вертикальний відрізок над рамкою) — жодна лінія не перетинає тексту.
    RX = 690
    frags.append(line(scx + sw_ / 2, scy, RX, scy, color=POS, sw=2))   # з Composite праворуч
    frags.append(line(RX, scy, RX, 30, color=POS, sw=2))                # угору повз усе
    frags.append(line(RX, 30, 300, 30, color=POS, sw=2))               # уліво над Component
    frags.append(arrow(300, 30, 300, 70 - ch / 2, color=POS, sw=2))    # униз у Component згори
    # підпис петлі — у зоні праворуч унизу, під горизонтальним відрізком, ліва грань
    # рамки не дотикає вертикалі x=690 (перевірено запасом). Лінії його не перетинають.
    lbl, lblw, lblh = textbox(585, 155, ["тримає", "children:", "List<Component>"],
                              size=13, pad=9, fill="#fdecea", stroke=POS, sw=1.6)
    frags.append(lbl)

    render(os.path.join(IMG, 'composite-structure.svg'), W, H, *frags)


def fig_recursion_vs_stack():
    """Два способи обійти дерево: неявний стек викликів (рекурсія) vs явний стек (цикл)."""
    W, H = 820, 470
    frags = []

    # ── Ліва колонка: рекурсія — кадри системного стека ростуть, тоді згортаються ──
    lx = 210
    frags.append(text(lx, 40, "Рекурсія", size=17, color=INK, bold=True))
    frags.append(text(lx, 62, "кадри системного стека", size=12, color=MUTED))

    # стос кадрів (кожен виклик traverse(вузол) — свій кадр); найглибший унизу
    frames = ["traverse(root)", "traverse(src)", "traverse(ui)", "traverse(a.ts)"]
    fy0 = 92
    fh = 46
    for i, fr in enumerate(frames):
        y = fy0 + i * (fh + 8)
        shade = "#eaf0fd" if i < len(frames) - 1 else "#fdecea"
        st = NEG if i < len(frames) - 1 else POS
        frags.append(fitbox(lx - 105, y, 210, fh, fr, size=14,
                            fill=shade, stroke=st, sw=1.6))
    # стрілка «глибше» вниз, ліворуч від стосу — повз рамки
    dax = lx - 135
    frags.append(arrow(dax, fy0 + 4, dax, fy0 + 3 * (fh + 8) + fh - 4,
                       color=MUTED, sw=1.8))
    frags.append(text(dax - 12, (fy0 + fy0 + 3 * (fh + 8) + fh) / 2,
                      "глибше", size=12, color=MUTED, anchor="middle"))
    # підпис під стосом
    frags.append(text(lx, fy0 + 4 * (fh + 8) + 20,
                      "дно листка → кадри згортаються вгору", size=12, color=MUTED))

    # ── Розділювач ──
    frags.append(line(W / 2, 34, W / 2, H - 26, color="#d0d5dd", sw=1.4, dash="5,5"))

    # ── Права колонка: явний стек у купі — вузли на обробку ──
    rx = 610
    frags.append(text(rx, 40, "Явний стек (цикл)", size=17, color=INK, bold=True))
    frags.append(text(rx, 62, "власний список — у купі, не в стеку викликів", size=11, color=MUTED))

    # поточний стан контейнера (те, що ще чекає обробки): [ui, docs]
    items = ["ui", "docs"]
    iy0 = 110
    ih = 46
    for i, it in enumerate(items):
        y = iy0 + i * (ih + 8)
        frags.append(fitbox(rx - 90, y, 180, ih, it, size=15,
                            fill="#eef7ee", stroke=FIELD, sw=1.6))
    # рамка-контейнер навколо елементів
    frags.append(rect(rx - 104, iy0 - 14, 208, len(items) * (ih + 8) + 16,
                      fill="none", stroke=FIELD, sw=1.4, rx=10))
    frags.append(text(rx, iy0 - 22, "stack = [...]", size=12, color=FIELD, bold=True))

    # операції pop/push збоку
    ops_y = iy0 + len(items) * (ih + 8) + 30
    frags.append(text(rx, ops_y, "цикл: node = stack.pop()", size=13, color=INK))
    frags.append(text(rx, ops_y + 22, "для кожної дитини → stack.push(child)", size=13, color=INK))
    frags.append(text(rx, ops_y + 52, "глибина дерева не чіпає стек викликів →", size=12, color=MUTED))
    frags.append(text(rx, ops_y + 70, "переповнення неможливе", size=12, color=MUTED))

    render(os.path.join(IMG, 'recursion-vs-stack.svg'), W, H, *frags)


def fig_lineage():
    """Родовід компонувальника: від View у Smalltalk-80 через каркаси кінця 1980-х
    до формулювання в 23 патернах банди чотирьох. Час тече згори вниз."""
    W, H = 860, 540
    frags = []

    # три яруси зверху вниз; у кожному — рамка-система з датою й тим, що там уже було
    # ярус 1 — корінь (Smalltalk-80 View)
    root_body, rw, rh = textbox(430, 70,
        ["Smalltalk-80  ·  1980", "клас View був складеним:",
         "CompositeView тримає підвиди"],
        size=14, pad=13, fill="#eef7ee", stroke=FIELD, sw=2, min_w=330)
    frags_root = root_body

    # ярус 2 — два каркаси кінця 1980-х (ET++ і InterViews), поруч
    et_body, ew, eh = textbox(215, 255,
        ["ET++  ·  1988", "VObjects: візуальний об'єкт", "містить візуальні об'єкти"],
        size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=290)
    iv_body, iw, ih = textbox(645, 255,
        ["InterViews  ·  1988–91", "Scene → Glyph: елемент", "містить елементи"],
        size=13, pad=12, fill="#eaf3ff", stroke=NEG, sw=1.8, min_w=290)

    # ярус 3 — формулювання патерна
    gof_body, gw, gh = textbox(430, 445,
        ["«Композит»  ·  ECOOP 1993 → книжка 1994", "названо, узагальнено, покладено",
         "до структурних патернів"],
        size=14, pad=13, fill="#fdecea", stroke=POS, sw=2, min_w=430)

    # стрілки успадкування ідеї (згори вниз): корінь → обидва каркаси
    frags.append(arrow(430 - 80, 70 + rh / 2, 215 + 40, 255 - eh / 2, color=MUTED, sw=1.8))
    frags.append(arrow(430 + 80, 70 + rh / 2, 645 - 40, 255 - ih / 2, color=MUTED, sw=1.8))
    # каркаси → формулювання патерна
    frags.append(arrow(215 + 60, 255 + eh / 2, 430 - 90, 445 - gh / 2, color=MUTED, sw=1.8))
    frags.append(arrow(645 - 60, 255 + ih / 2, 430 + 90, 445 - gh / 2, color=MUTED, sw=1.8))

    # вісь часу — тонка стрілка ліворуч, повз усі рамки (x=40), згори вниз;
    # підпис «час» — вертикально, ліворуч від осі, щоб не торкати саму лінію
    tax = 40
    frags.append(arrow(tax, 55, tax, H - 40, color="#c0c5cd", sw=1.6))
    frags.append('<text x="20" y="%d" font-size="12" fill="%s" text-anchor="middle" '
                 'transform="rotate(-90 20 %d)">час</text>'
                 % ((55 + H - 40) // 2, MUTED, (55 + H - 40) // 2))

    frags.append(frags_root)
    frags.append(et_body)
    frags.append(iv_body)
    frags.append(gof_body)

    render(os.path.join(IMG, 'composite-lineage.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_tree()
    fig_interface()
    fig_recursion_vs_stack()
    fig_lineage()
    print("figures written")
