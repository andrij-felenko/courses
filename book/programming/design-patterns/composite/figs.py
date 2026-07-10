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


def fig_parent_invariant():
    """Двобічний зв'язок батько-дитина: список дітей униз, посилання .parent угору;
    інваріант — обидва напрями мусять узгоджуватися."""
    W, H = 780, 430
    frags = []

    p_body, pw, ph = textbox(390, 85, ["Composite", "(тека)"], size=15, pad=13,
                             fill="#eaf3ff", stroke=NEG, sw=2, min_w=170)
    la_body, law, lah = textbox(250, 255, ["Leaf A", "(файл)"], size=14, pad=12,
                                fill="#f4f6f8", stroke=LINE, min_w=150)
    cb_body, cbw, cbh = textbox(540, 255, ["Composite B", "(підтека)"], size=14, pad=12,
                                fill="#eaf3ff", stroke=NEG, sw=2, min_w=150)

    # зв'язки ВНИЗ: parent.children (володіння) — суцільні, стрілка до дитини
    frags.append(arrow(390 - 26, 85 + ph / 2, 250, 255 - lah / 2, color=MUTED, sw=1.8))
    frags.append(arrow(390 - 8, 85 + ph / 2, 540, 255 - cbh / 2, color=MUTED, sw=1.8))
    # зв'язки ВГОРУ: child.parent — стрілка до батька, зі зсувом убік
    frags.append(arrow(250 + 32, 255 - lah / 2, 390 + 8, 85 + ph / 2, color=POS, sw=1.6))
    frags.append(arrow(540 + 8, 255 - cbh / 2, 390 + 26, 85 + ph / 2, color=POS, sw=1.6))

    frags.append(p_body)
    frags.append(la_body)
    frags.append(cb_body)

    down_lbl, _, _ = textbox(688, 150, ["вниз:", "children:", "List<Component>"],
                             size=12, pad=9, fill="#f0f0f0", stroke=MUTED)
    up_lbl, _, _ = textbox(92, 150, ["вгору:", "child.parent"],
                           size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(down_lbl)
    frags.append(up_lbl)

    inv_body, _, _ = textbox(390, 378,
                             ["Інваріант двобічного зв'язку:",
                              "child ∈ parent.children   ⇔   child.parent == parent"],
                             size=14, pad=13, fill="#eef7ee", stroke=FIELD, sw=1.8, min_w=560)
    frags.append(inv_body)

    render(os.path.join(IMG, 'composite-parent-invariant.svg'), W, H, *frags)


def fig_cache_invalidation():
    """Зміна в листку робить «брудними» лише вузли на шляху до кореня (O(h));
    сусідні піддерева зберігають чинний кеш."""
    W, H = 840, 470
    frags = []

    nodes = {
        'root':  (420,  80, "root",     'dirty'),
        'src':   (250, 220, "src",      'dirty'),
        'docs':  (600, 220, "docs",     'clean'),
        'main':  (150, 350, "main.ts",  'dirty'),
        'ui':    (340, 350, "ui",       'clean'),
        'guide': (520, 350, "guide.md", 'clean'),
        'api':   (690, 350, "api.md",   'clean'),
    }
    edges = [('root', 'src'), ('root', 'docs'), ('src', 'main'), ('src', 'ui'),
             ('docs', 'guide'), ('docs', 'api')]
    dirty_edges = {('root', 'src'), ('src', 'main')}

    boxes = {}
    for k, (cx, cy, label, st) in nodes.items():
        if st == 'clean':
            fill, stroke, sw = "#eef7ee", FIELD, 1.6
        else:
            fill, stroke, sw = "#fdecea", POS, 2.0
        body, w, h = textbox(cx, cy, label, size=14, pad=10, fill=fill, stroke=stroke,
                             sw=sw, min_w=84)
        boxes[k] = (cx, cy, w, h, body)

    for a, b in edges:
        ax, ay, aw, ah, _ = boxes[a]
        bx, by, bw, bh, _ = boxes[b]
        if (a, b) in dirty_edges:
            frags.append(arrow(bx, by - bh / 2, ax, ay + ah / 2, color=POS, sw=2.2))
        else:
            frags.append(line(ax, ay + ah / 2, bx, by - bh / 2, color=MUTED, sw=1.5))

    for k in nodes:
        frags.append(boxes[k][4])

    tag, _, _ = textbox(150, 412, "змінено значення", size=12, pad=8,
                        fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(tag)

    leg1, _, _ = textbox(112, 52, "брудний → перерахувати", size=12, pad=7,
                         fill="#fdecea", stroke=POS, sw=1.4)
    leg2, _, _ = textbox(112, 88, "кеш чинний", size=12, pad=7,
                         fill="#eef7ee", stroke=FIELD, sw=1.4)
    frags.append(leg1)
    frags.append(leg2)

    dir_lbl, _, _ = textbox(500, 412, "інвалідизація вгору по .parent — O(h)",
                            size=12, pad=8, fill="#f0f0f0", stroke=MUTED)
    frags.append(dir_lbl)

    render(os.path.join(IMG, 'composite-cache-invalidation.svg'), W, H, *frags)


def fig_tree_vs_dag():
    """Дерево (один батько на вузол) проти DAG (спільний листок має двох батьків)."""
    W, H = 860, 440
    frags = []

    frags.append(line(430, 44, 430, 396, color="#d0d5dd", sw=1.4, dash="6,6"))
    frags.append(text(215, 32, "Дерево", size=16, color=INK, bold=True))
    frags.append(text(645, 32, "DAG: спільний листок", size=16, color=INK, bold=True))

    def make(cx, cy, label, kind='leaf', hot=False):
        if hot:
            fill, stroke, sw = "#fdecea", POS, 2.2
        elif kind == 'comp':
            fill, stroke, sw = "#eaf3ff", NEG, 1.8
        else:
            fill, stroke, sw = "#f4f6f8", LINE, 1.5
        return textbox(cx, cy, label, size=14, pad=10, fill=fill, stroke=stroke,
                       sw=sw, min_w=60)

    # ── ліворуч: справжнє дерево ──
    L = {'a': (215, 92, "A", 'comp'), 'b': (140, 212, "B", 'comp'),
         'c': (290, 212, "C", 'comp'), 'x': (95, 332, "x", 'leaf'),
         'y': (185, 332, "y", 'leaf'), 'z': (290, 332, "z", 'leaf')}
    Le = [('a', 'b'), ('a', 'c'), ('b', 'x'), ('b', 'y'), ('c', 'z')]
    Lb = {}
    for k, (cx, cy, lb, kd) in L.items():
        Lb[k] = make(cx, cy, lb, kind=kd)
    for A, B in Le:
        frags.append(line(L[A][0], L[A][1] + Lb[A][2] / 2,
                          L[B][0], L[B][1] - Lb[B][2] / 2, color=MUTED, sw=1.6))
    for k in L:
        frags.append(Lb[k][0])

    # ── праворуч: DAG зі спільним листком ──
    R = {'a': (645, 92, "A", 'comp'), 'b': (575, 212, "B", 'comp'),
         'c': (715, 212, "C", 'comp')}
    Rb = {}
    for k, (cx, cy, lb, kd) in R.items():
        Rb[k] = make(cx, cy, lb, kind=kd)
    s_body, sw_, sh_ = make(645, 348, "s (спільний)", 'leaf', hot=True)
    for A, B in [('a', 'b'), ('a', 'c')]:
        frags.append(line(R[A][0], R[A][1] + Rb[A][2] / 2,
                          R[B][0], R[B][1] - Rb[B][2] / 2, color=MUTED, sw=1.6))
    frags.append(arrow(575, 212 + Rb['b'][2] / 2, 645 - 32, 348 - sh_ / 2, color=POS, sw=2))
    frags.append(arrow(715, 212 + Rb['c'][2] / 2, 645 + 32, 348 - sh_ / 2, color=POS, sw=2))
    for k in R:
        frags.append(Rb[k][0])
    frags.append(s_body)

    l_lbl, _, _ = textbox(215, 408, "один батько → .parent однозначний",
                          size=12, pad=8, fill="#eef7ee", stroke=FIELD)
    r_lbl, _, _ = textbox(648, 408, "два батьки в s → .parent неоднозначний",
                          size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(l_lbl)
    frags.append(r_lbl)

    render(os.path.join(IMG, 'composite-tree-vs-dag.svg'), W, H, *frags)


def fig_expression_problem():
    """Дві осі розширення: додати ТИП (рядок) дешево в ООП / дорого в сум-типі;
    додати ОПЕРАЦІЮ (стовпець) — навпаки."""
    W, H = 900, 560
    frags = []
    frags.append(text(450, 34, "Дві осі розширення: новий тип проти нової операції",
                      size=16, color=INK, bold=True))

    x0, y0 = 250, 122
    cw, ch = 130, 66
    cols = ["size()", "draw()", "+ нова оп."]
    rows = ["Leaf", "Composite", "+ новий тип"]

    for j, cname in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        dashed = (j == 2)
        frags.append(text(cx, y0 - 16, cname, size=13,
                          color=(MUTED if dashed else INK), bold=not dashed))
    for i, rname in enumerate(rows):
        cy = y0 + i * ch + ch / 2
        dashed = (i == 2)
        frags.append(text(x0 - 16, cy + 4, rname, size=13,
                          color=(MUTED if dashed else INK), anchor="end", bold=not dashed))

    for i in range(3):
        for j in range(3):
            x = x0 + j * cw
            y = y0 + i * ch
            ext = (i == 2 or j == 2)
            if ext:
                frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
                             'fill="#fafafa" stroke="#c9ced6" stroke-width="1.2" '
                             'stroke-dasharray="5,4"/>' % (x + 4, y + 4, cw - 8, ch - 8))
            else:
                frags.append(rect(x + 4, y + 4, cw - 8, ch - 8, fill="#f4f6f8",
                                  stroke=LINE, sw=1.4, rx=6))
                frags.append(text(x + cw / 2, y + ch / 2 + 5, "код", size=13, color=INK))

    gy1 = y0 + 3 * ch

    row_note, _, _ = textbox(450, gy1 + 66,
        ["Новий ТИП (рядок у сітці):",
         "ООП — один новий клас, наявне не чіпаємо  ✓",
         "сум-тип — правити match у КОЖНІЙ операції  ✗"],
        size=13, pad=12, fill="#eef2ff", stroke=NEG, sw=1.6, min_w=540)
    frags.append(row_note)

    col_note, _, _ = textbox(x0 + 3 * cw + 128, y0 + ch,
        ["Нова ОПЕРАЦІЯ", "(стовпець у сітці):", "",
         "ООП — метод у", "КОЖЕН клас  ✗", "",
         "сум-тип — одна", "нова функція  ✓"],
        size=12, pad=11, fill="#fdf0ee", stroke=POS, sw=1.6)
    frags.append(col_note)

    render(os.path.join(IMG, 'composite-expression-problem.svg'), W, H, *frags)


def fig_bounds_stale():
    """Кеш межі групи чинний, поки все на місці; зсув ЛИСТКА робить його хибним."""
    W, H = 910, 410
    dx = 470
    frags = []

    def leaf(x, y, w, h, name):
        return (rect(x, y, w, h, fill="#eef2f7", stroke=LINE, sw=1.5, rx=4) +
                text(x + w / 2, y + h / 2 + 5, name, size=13, color=INK))

    def box(x, y, w, h, color, sw, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" '
                'fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (x, y, w, h, color, sw, d))

    # ── Панель А: усе на місці — кеш чинний ──
    frags.append(text(190, 40, "спокій: кеш чинний", size=15, bold=True))
    frags.append(box(83, 96, 214, 119, FIELD, 2.4, "7,5"))          # cached бокс G (зелений)
    frags.append(leaf(95, 108, 70, 55, "r1"))
    frags.append(leaf(215, 148, 70, 55, "r2"))
    frags.append(text(190, 250, "cached G — тісно облягає r1, r2", size=12, color=MUTED))

    # роздільник панелей
    frags.append(line(450, 70, 450, 300, color="#d0d5dd", sw=1.4))

    # ── Панель Б: r2 зсунувся — старий кеш став хибним ──
    frags.append(text(190 + dx, 40, "після r2.moveTo(): кеш хибний", size=15, bold=True))
    frags.append(box(546, 90, 252, 210, FIELD, 1.6))                # правильний бокс (зелений суцільний)
    frags.append(box(83 + dx, 96, 214, 119, POS, 2.4, "7,5"))       # старий кеш (червоний) на старому місці
    frags.append(leaf(95 + dx, 108, 70, 55, "r1"))
    frags.append(leaf(690, 228, 70, 55, "r2"))                      # r2 виїхав за старий кеш
    frags.append(text(190 + dx, 324, "червоний — старий кеш, r2 поза ним", size=12, color=POS))
    frags.append(text(190 + dx, 346, "зелений — правильний бокс після зсуву", size=12, color=FIELD))

    render(os.path.join(IMG, 'composite-bounds-stale.svg'), W, H, *frags)


def fig_descent_termination():
    """Ациклічне дерево: спуск строго меншає за висотою до дна (h=0) → завершується;
    кільце a⇄b: висота не має розв'язку → дна немає, рекурсія не спиняється."""
    W, H = 880, 470
    frags = []

    # розділювач панелей
    frags.append(line(455, 44, 455, H - 40, color="#d0d5dd", sw=1.4, dash="6,6"))
    frags.append(text(230, 34, "Ациклічне дерево: спуск має дно", size=15,
                      color=INK, bold=True))
    frags.append(text(670, 34, "Кільце: дна немає", size=15, color=INK, bold=True))

    # ── ліворуч: дерево з висотами у вузлах (висота — другий рядок рамки) ──
    nodes = {
        'root': (235,  95, ["root", "h = 2"], 'comp'),
        'a':    (145, 225, ["A", "h = 1"],    'comp'),
        'b':    (325, 225, ["B", "h = 0"],    'leaf'),
        'x':    ( 95, 355, ["x", "h = 0"],    'leaf'),
        'y':    (205, 355, ["y", "h = 0"],    'leaf'),
    }
    edges = [('root', 'a'), ('root', 'b'), ('a', 'x'), ('a', 'y')]
    boxes = {}
    for k, (cx, cy, lab, kind) in nodes.items():
        fill = "#eaf3ff" if kind == 'comp' else "#f4f6f8"
        stroke = NEG if kind == 'comp' else LINE
        boxes[k] = (cx, cy) + textbox(cx, cy, lab, size=13, pad=9, fill=fill,
                                      stroke=stroke, sw=1.8 if kind == 'comp' else 1.5,
                                      min_w=74)
    for A, Bk in edges:
        ax, ay, _, aw, ah = boxes[A]
        bx, by, _, bw, bh = boxes[Bk]
        frags.append(arrow(ax, ay + ah / 2, bx, by - bh / 2, color=MUTED, sw=1.7))
    for k in nodes:
        frags.append(boxes[k][2])

    note_l, _, _ = textbox(230, H - 55,
                           ["кожен крок:  h(дитина) < h(вузла)",
                            "h ∈ ℕ  ⇒  спуск упирається в дно (h = 0)"],
                           size=12, pad=10, fill="#eef7ee", stroke=FIELD, sw=1.6,
                           min_w=380)
    frags.append(note_l)

    # ── праворуч: кільце a ⇄ b (дві стрілки, рознесені по горизонталі) ──
    ax_, ay_ = 670, 120
    bx_, by_ = 670, 250
    a_body, aw_, ah_ = textbox(ax_, ay_, "a", size=15, pad=12, fill="#fdecea",
                               stroke=POS, sw=2, min_w=64)
    b_body, bw_, bh_ = textbox(bx_, by_, "b", size=15, pad=12, fill="#fdecea",
                               stroke=POS, sw=2, min_w=64)
    # a → b по лівому боці, b → a по правому боці — стрілки не перетинаються
    frags.append(arrow(ax_ - 18, ay_ + ah_ / 2, bx_ - 18, by_ - bh_ / 2, color=POS, sw=2))
    frags.append(arrow(bx_ + 18, by_ - bh_ / 2, ax_ + 18, ay_ + ah_ / 2, color=POS, sw=2))
    frags.append(a_body)
    frags.append(b_body)

    note_r, _, _ = textbox(670, H - 62,
                           ["h(a) = 1 + h(b)", "h(b) = 1 + h(a)",
                            "⇒  h(a) = 2 + h(a):  без розв'язку"],
                           size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.6,
                           min_w=300)
    frags.append(note_r)

    render(os.path.join(IMG, 'composite-descent-termination.svg'), W, H, *frags)


def fig_height_shapes():
    """Та сама вага n, різна форма: ланцюг h = n−1 = Θ(n) проти
    збалансованого h = Θ(log n). Підйом угору коштує O(h)."""
    W, H = 880, 460
    frags = []

    frags.append(line(430, 44, 430, H - 66, color="#d0d5dd", sw=1.4, dash="6,6"))
    frags.append(text(205, 34, "Ланцюг:  h = n − 1 = Θ(n)", size=15, color=INK, bold=True))
    frags.append(text(650, 34, "Збалансоване:  h = Θ(log n)", size=15, color=INK, bold=True))

    # ── ліворуч: ланцюг із 5 вузлів, висота 4..0 згори вниз ──
    cx = 205
    ys = [80, 150, 220, 290, 360]
    chain = []
    for i, y in enumerate(ys):
        hh = len(ys) - 1 - i
        kind_comp = i < len(ys) - 1
        fill = "#eaf3ff" if kind_comp else "#f4f6f8"
        stroke = NEG if kind_comp else LINE
        body, w, h = textbox(cx, y, "h = %d" % hh, size=13, pad=9, fill=fill,
                             stroke=stroke, sw=1.8 if kind_comp else 1.5, min_w=72)
        chain.append((y, w, h, body))
    for i in range(len(ys) - 1):
        y1, w1, h1, _ = chain[i]
        y2, w2, h2, _ = chain[i + 1]
        frags.append(arrow(cx, y1 + h1 / 2, cx, y2 - h2 / 2, color=MUTED, sw=1.7))
    for _, _, _, body in chain:
        frags.append(body)
    note_l, _, _ = textbox(205, H - 42, "5 вузлів  →  h = 4 = n − 1  (лінійно)",
                           size=12, pad=9, fill="#eef2ff", stroke=NEG, sw=1.5, min_w=320)
    frags.append(note_l)

    # ── праворуч: збалансоване двійкове дерево, 7 вузлів, висота 2 ──
    Bn = {
        'r':  (650,  80, "h = 2", 'comp'),
        'l':  (575, 200, "h = 1", 'comp'),
        'rr': (725, 200, "h = 1", 'comp'),
        'a':  (535, 320, "h = 0", 'leaf'),
        'b':  (615, 320, "h = 0", 'leaf'),
        'c':  (685, 320, "h = 0", 'leaf'),
        'd':  (765, 320, "h = 0", 'leaf'),
    }
    Be = [('r', 'l'), ('r', 'rr'), ('l', 'a'), ('l', 'b'), ('rr', 'c'), ('rr', 'd')]
    Bb = {}
    for k, (bx, by, lab, kind) in Bn.items():
        fill = "#eaf3ff" if kind == 'comp' else "#f4f6f8"
        stroke = NEG if kind == 'comp' else LINE
        Bb[k] = (bx, by) + textbox(bx, by, lab, size=12, pad=7, fill=fill,
                                   stroke=stroke, sw=1.8 if kind == 'comp' else 1.5,
                                   min_w=60)
    for A, C in Be:
        axx, ayy, _, aww, ahh = Bb[A]
        cxx, cyy, _, cww, chh = Bb[C]
        frags.append(line(axx, ayy + ahh / 2, cxx, cyy - chh / 2, color=MUTED, sw=1.5))
    for k in Bn:
        frags.append(Bb[k][2])
    note_r, _, _ = textbox(650, H - 42, "7 вузлів  →  h = 2 ≈ log₂7   (n ≈ 2ʰ)",
                           size=12, pad=9, fill="#fdf0ee", stroke=POS, sw=1.5, min_w=320)
    frags.append(note_r)

    render(os.path.join(IMG, 'composite-height-shapes.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_tree()
    fig_interface()
    fig_recursion_vs_stack()
    fig_lineage()
    fig_parent_invariant()
    fig_cache_invalidation()
    fig_tree_vs_dag()
    fig_expression_problem()
    fig_bounds_stale()
    fig_descent_termination()
    fig_height_shapes()
    print("figures written")
