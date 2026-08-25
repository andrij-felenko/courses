# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: два шляхи від тексту до картинки й до реальності ───────────────
# Ліворуч — намальована мишкою діаграма: живе окремо, відстає від коду.
# Праворуч — діаграма з тексту: той самий текст → картинка, текст живе поруч із кодом.
def fig_two_paths():
    W, H = 820, 470
    f = []
    f.append(text(W / 2, 30, "Малюнок мишкою проти опису текстом", size=17, bold=True))

    # роздільна лінія посередині
    f.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1.2, dash="5,5"))

    # ── ЛІВА колонка: намальована діаграма ──
    lx = W / 4
    f.append(text(lx, 74, "Намальовано в редакторі", size=13, bold=True, color=NEG))
    b, bw, bh = textbox(lx, 118, "код у git", size=12, min_w=150,
                        fill="#eaf0fd", stroke=NEG); f.append(b)
    b2, _, _ = textbox(lx, 200, ".png / .vsdx\nу редакторі", size=12, min_w=150,
                       fill=FILL, stroke=MUTED); f.append(b2)
    # код змінюється — картинка ні
    f.append(arrow(lx - 40, 150, lx - 40, 176, color=MUTED))
    f.append(text(lx - 96, 168, "хто згадає\nоновити?", size=10, color=NEG))
    b3, _, _ = textbox(lx, 300, "картинка бреше:\nкод пішов уперед", size=12,
                       min_w=180, fill="#fdecea", stroke=POS); f.append(b3)
    f.append(arrow(lx, 232, lx, 274, color=POS))
    f.append(text(lx, 388, "два джерела правди,\nщо розходяться", size=12,
                  color=POS, bold=True))

    # ── ПРАВА колонка: діаграма як код ──
    rx = 3 * W / 4
    f.append(text(rx, 74, "Описано текстом", size=13, bold=True, color=FIELD))
    b4, _, _ = textbox(rx, 118, "diagram.dot\nу git, поруч із кодом", size=12,
                       min_w=210, fill="#eafaf1", stroke=FIELD); f.append(b4)
    f.append(arrow(rx, 150, rx, 186, color=INK))
    f.append(text(rx + 78, 172, "рушій\nмалює", size=10, color=INK))
    b5, _, _ = textbox(rx, 220, "diagram.svg\n(згенеровано)", size=12,
                       min_w=190, fill=FILL, stroke=LINE); f.append(b5)
    b6, _, _ = textbox(rx, 300, "правиш текст →\nкартинка сама нова", size=12,
                       min_w=210, fill="#eafaf1", stroke=FIELD); f.append(b6)
    f.append(arrow(rx, 252, rx, 274, color=FIELD))
    f.append(text(rx, 388, "одне джерело правди —\nтекст", size=12,
                  color=FIELD, bold=True))

    render(os.path.join(IMG, "two-paths.svg"), W, H, *f)


# ── Фігура 2: два рівні «як код» — розкладка проти моделі ────────────────────
# Верх — опис РОЗКЛАДКИ (вузли+лінії, одна картинка).
# Низ — опис МОДЕЛІ (сутності+звʼязки → багато в'ю з однієї моделі).
def fig_layout_vs_model():
    W, H = 820, 500
    f = []
    f.append(text(W / 2, 30, "Два рівні «як код»: розкладка й модель", size=17, bold=True))

    # ── ВЕРХ: розкладка як код ──
    f.append(text(180, 66, "Рівень розкладки", size=13, bold=True))
    f.append(text(180, 86, "(DOT, Mermaid, PlantUML)", size=11, color=MUTED))
    b, _, _ = textbox(180, 150, 'A -> B\nB -> C', size=13, min_w=150,
                      fill=FILL, stroke=LINE); f.append(b)
    f.append(text(180, 214, "текст описує ЦЕЙ малюнок", size=11, color=MUTED))
    f.append(arrow(300, 150, 372, 150, color=INK))
    # одна картинка праворуч
    for i, (cx, cy, lb) in enumerate([(440, 120, "A"), (520, 150, "B"), (600, 180, "C")]):
        f.append(circle(cx, cy, 20, fill="#eafaf1", stroke=FIELD, sw=2))
        f.append(text(cx, cy + 5, lb, size=13, bold=True))
    f.append(arrow(460, 128, 500, 143, color=LINE))
    f.append(arrow(540, 158, 580, 173, color=LINE))
    f.append(text(520, 218, "одна діаграма", size=11, color=MUTED))

    # роздільник
    f.append(line(60, 258, W - 60, 258, color=MUTED, sw=1))

    # ── НИЗ: модель як код ──
    f.append(text(180, 296, "Рівень моделі", size=13, bold=True))
    f.append(text(180, 316, "(Structurizr / C4)", size=11, color=MUTED))
    b2, _, _ = textbox(180, 384, 'user -> web\nweb -> db\nweb -> pay', size=12,
                       min_w=170, fill="#eafaf1", stroke=FIELD); f.append(b2)
    f.append(text(180, 442, "текст описує СИСТЕМУ", size=11, color=MUTED))
    f.append(arrow(300, 384, 372, 384, color=INK))
    # три різні в'ю з однієї моделі
    views = [(440, 360, "контекст"), (560, 360, "контейнери"), (680, 360, "розгортання")]
    for cx, cy, lb in views:
        bb = fitbox(cx - 52, cy - 20, 104, 40, lb, size=11,
                    fill=FILL, stroke=LINE); f.append(bb)
    f.append(text(560, 442, "багато в'ю з ОДНІЄЇ моделі", size=11,
                  color=FIELD, bold=True))

    render(os.path.join(IMG, "layout-vs-model.svg"), W, H, *f)


# ── Фігура 3: діаграма в конвеєрі — гейт, що ловить розходження ──────────────
def fig_pipeline_gate():
    W, H = 800, 250
    f = []
    f.append(text(W / 2, 30, "Діаграма в конвеєрі — гейт проти дрейфу", size=17, bold=True))

    y = 130
    steps = [
        ("правка\ntext-опису", "#eafaf1", FIELD),
        ("git commit\n+ push", FILL, LINE),
        ("CI малює\nSVG", FILL, LINE),
        ("порівняти з\nвкладеним", "#eaf0fd", NEG),
    ]
    xs = [110, 270, 430, 600]
    prev = None
    for (lb, fl, st), cx in zip(steps, xs):
        b, bw, _ = textbox(cx, y, lb, size=12, min_w=120, fill=fl, stroke=st)
        f.append(b)
        if prev is not None:
            f.append(arrow(prev, y, cx - bw / 2 - 6, y, color=INK))
        prev = cx + bw / 2 + 6

    # розгалуження результату
    f.append(text(700, y - 22, "збіг →", size=11, color=FIELD))
    f.append(text(700, y + 4, "зелено", size=12, color=FIELD, bold=True))
    f.append(text(700, y + 34, "різниця →", size=11, color=POS))
    f.append(text(700, y + 54, "збірка падає", size=12, color=POS, bold=True))

    f.append(text(W / 2, 210,
                  "картинка не може відстати від тексту — CI не пропустить розходження",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "pipeline-gate.svg"), W, H, *f)


# ── Фігура 4 (вставка comp): один граф трьома мовами → одна картинка ─────────
# Три різні написи (DOT / Mermaid / PlantUML) описують ТОЙ САМИЙ граф;
# рушій кожної розкладає його сам → однакова структура вузол→стрілка.
def fig_three_langs():
    W, H = 880, 560
    f = []
    f.append(text(W / 2, 30, "Один граф — три мови — та сама картинка", size=17, bold=True))

    # три колонки коду
    cols = [
        (150, "DOT", NEG,
         'digraph {\n  a -> b\n  a -> c\n  b -> d\n  c -> d\n}'),
        (440, "Mermaid", FIELD,
         'graph TD\n  a --> b\n  a --> c\n  b --> d\n  c --> d'),
        (730, "PlantUML", POS,
         '@startuml\n(a) --> (b)\n(a) --> (c)\n(b) --> (d)\n(c) --> (d)\n@enduml'),
    ]
    for cx, name, clr, code in cols:
        f.append(text(cx, 66, name, size=13, bold=True, color=clr))
        b, _, _ = textbox(cx, 152, code, size=12, min_w=210,
                          fill=FILL, stroke=clr); f.append(b)

    # три короткі вертикальні стрілки вниз (кожна від свого блоку, не перетинаються)
    for cx, _, clr, _ in cols:
        f.append(arrow(cx, 236, cx, 268, color=clr, sw=1.6))
    # підпис-місток — окремим рядком, під стрілками, поза їхніми шляхами
    f.append(text(W / 2, 292, "різний синтаксис — той самий зміст", size=11,
                  color=MUTED))

    # спільна намальована картинка: ромб-граф a→b,c→d
    gy = 342
    nodes = {"a": (W / 2, gy), "b": (W / 2 - 110, gy + 78),
             "c": (W / 2 + 110, gy + 78), "d": (W / 2, gy + 156)}
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    for u, v in edges:
        x1, y1 = nodes[u]; x2, y2 = nodes[v]
        f.append(arrow(x1, y1 + 20, x2, y2 - 20, color=LINE, sw=1.6))
    for lb, (cx, cy) in nodes.items():
        f.append(circle(cx, cy, 20, fill="#eafaf1", stroke=FIELD, sw=2))
        f.append(text(cx, cy + 5, lb, size=14, bold=True))
    f.append(text(W / 2, gy + 196,
                  "розкладку рахує рушій — ти пишеш лише зв'язки", size=12,
                  color=FIELD, bold=True))

    render(os.path.join(IMG, "three-langs.svg"), W, H, *f)


# ── Фігура 5 (вставка comp): де природно живе кожна мова ─────────────────────
# DOT — низькорівневий рушій (на ньому стоять інші); PlantUML — UML-нотації;
# Mermaid — легкі схеми прямо в markdown/GitHub.
def fig_where_each_lives():
    W, H = 900, 470
    f = []
    f.append(text(W / 2, 30, "Де природно живе кожна мова", size=17, bold=True))

    # підпис-мораль угорі
    f.append(text(W / 2, 60,
                  "та сама ідея «вузол → стрілка» — різні ніші застосування",
                  size=12, color=MUTED))

    # два стовпи — кожен окремою рамкою з назвою + двома рядками ролі всередині
    b1 = fitbox(90, 110, 340, 130,
                "PlantUML\n\nUML-нотації: класи, послідовності,\n"
                "компоненти, стани, розгортання",
                size=13, fill="#fdecea", stroke=POS)
    f.append(b1)
    b2 = fitbox(W - 430, 110, 340, 130,
                "Mermaid\n\nлегкі схеми прямо в markdown;\n"
                "GitHub рендерить у тексті .md",
                size=13, fill="#eafaf1", stroke=FIELD)
    f.append(b2)

    # стрілки вниз до спільної плити-рушія
    f.append(arrow(200, 246, 200, 344, color=POS, sw=1.6))
    f.append(text(600, 246, "власний рушій у браузері", size=11, color=FIELD,
                  anchor="middle"))
    f.append(text(390, 300, "спирається на рушій нижче", size=11, color=MUTED,
                  anchor="middle"))

    # низ: DOT як фундамент-рушій (широка плита)
    base = fitbox(90, 350, W - 180, 78,
                  "DOT / Graphviz — низькорівневий рушій розкладки\n"
                  "(інші інструменти часто будують картинку на ньому)",
                  size=13, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(base)

    render(os.path.join(IMG, "where-each-lives.svg"), W, H, *f)


# ── Фігура 6 (вставка hist): родовід рушіїв від AT&T до опису системи ─────────
# dag (1988) → dot (1991) / алгоритм (1993) → Graphviz відкритий (~2000)
# → на ньому виросли PlantUML / Mermaid / Structurizr.
def fig_hist_lineage():
    W, H = 900, 440
    f = []
    f.append(text(W / 2, 32, "Родовід: від графового рушія AT&T до опису системи",
                  size=17, bold=True))
    f.append(text(W / 2, 60, "AT&T Bell Labs — розкладку рахує машина", size=12,
                  color=MUTED))

    # ── Верхня нитка: три покоління рушія в AT&T ──
    ty = 122
    b1, w1, _ = textbox(160, ty, "dag · 1988\nҐанснер·Норт·Во\nпрограма малює граф",
                        size=12, min_w=210, fill=FILL, stroke=LINE)
    f.append(b1)
    b2, w2, _ = textbox(460, ty, "dot · 1991\nКуцофіос·Норт\nоптимальна розкладка",
                        size=12, min_w=210, fill=FILL, stroke=LINE)
    f.append(b2)
    b3, w3, _ = textbox(760, ty, "Graphviz · ~2000\nвідкритий код\nрушій для всіх",
                        size=12, min_w=210, fill="#eafaf1", stroke=FIELD)
    f.append(b3)
    f.append(arrow(160 + w1 / 2 + 8, ty, 460 - w2 / 2 - 8, ty, color=INK))
    f.append(arrow(460 + w2 / 2 + 8, ty, 760 - w3 / 2 - 8, ty, color=INK))

    # роздільник
    f.append(line(70, 216, W - 70, 216, color=MUTED, sw=1, dash="5,5"))

    # ── Нижня нитка: що виросло на відкритому рушії ──
    f.append(text(W / 2, 250, "виросло поверх відкритого рушія", size=12, color=MUTED))
    downs = [
        (185, "PlantUML · 2009\nАрно Рок (фр.)\nUML текстом,\nрозкладка — dot", "#eaf0fd", NEG),
        (460, "Mermaid · 2014\nК.Свейдквіст (швед)\nдіаграма прямо\nв тексті .md", "#eaf0fd", NEG),
        (735, "Structurizr / C4\nСаймон Браун (брит.)\nопис СИСТЕМИ →\nбагато в'ю", "#eafaf1", FIELD),
    ]
    dy = 326
    for cx, lb, fl, st in downs:
        bb, _, _ = textbox(cx, dy, lb, size=11, min_w=200, fill=fl, stroke=st)
        f.append(bb)
    # стрілка від Graphviz вниз до нитки нащадків
    f.append(arrow(760, ty + 36, 760, 274, color=MUTED))
    f.append(text(W / 2, 410, "рух один: щоразу з-під людини забирають чергову ручну роботу",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "hist-lineage.svg"), W, H, *f)


# ═══ Фігури вставки comp-structurizr-c4.md ═══════════════════════════════════

# ── S1: розкладка (три незалежні тексти) проти моделі (один опис → три в'ю) ───
def fig_model_fanout():
    W, H = 880, 470
    f = []
    f.append(text(W / 2, 30, "Три незалежні картинки проти однієї моделі", size=17, bold=True))
    f.append(line(W / 2, 58, W / 2, H - 24, color=MUTED, sw=1.2, dash="5,5"))

    # ── ЛІВА: розкладка як код — три окремі тексти → три картинки ──
    lx = 175
    f.append(text(lx, 76, "Розкладка як код", size=13, bold=True, color=POS))
    f.append(text(lx, 94, "(Mermaid, PlantUML)", size=10, color=MUTED))
    ty = 140
    for lb in ["текст діаграми 1", "текст діаграми 2", "текст діаграми 3"]:
        b, bw, _ = textbox(lx - 20, ty, lb, size=11, min_w=150, fill=FILL, stroke=MUTED)
        f.append(b)
        f.append(arrow(lx - 20 + bw / 2 + 6, ty, lx + 118, ty, color=LINE))
        f.append(circle(lx + 140, ty, 15, fill="#fdecea", stroke=POS, sw=1.8))
        ty += 60
    f.append(text(lx, 404, "три джерела —\nтихо розходяться", size=12, color=POS, bold=True))

    # ── ПРАВА: модель як код — один опис → три узгоджені в'ю ──
    rx = 660
    f.append(text(rx, 76, "Модель як код", size=13, bold=True, color=FIELD))
    f.append(text(rx, 94, "(Structurizr)", size=10, color=MUTED))
    b, bw, bh = textbox(rx - 75, 200, "один опис\nсистеми\n(сутності +\nзв'язки)", size=12,
                        min_w=130, fill="#eafaf1", stroke=FIELD, bold=True); f.append(b)
    for cy, lb in [(140, "контекст"), (200, "контейнери"), (260, "розгортання")]:
        f.append(arrow(rx - 75 + bw / 2 + 6, 200, rx + 40, cy, color=INK))
        bb = fitbox(rx + 40, cy - 17, 120, 34, lb, size=11, fill=FILL, stroke=LINE)
        f.append(bb)
    f.append(text(rx, 404, "одне джерело —\nв'ю не розійдуться", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "model-fanout.svg"), W, H, *f)


# ── S2: три частини рушія модель→в'ю ─────────────────────────────────────────
def fig_three_parts():
    W, H = 900, 340
    f = []
    f.append(text(W / 2, 30, "Будова рушія «модель → в'ю»", size=17, bold=True))

    y = 155
    b1, w1, h1 = textbox(170, y, "ОПИС МОДЕЛІ\n\nсутності й зв'язки\nджерело правди",
                         size=12, min_w=220, fill="#eafaf1", stroke=FIELD)
    f.append(b1)
    f.append(text(170, y - h1 / 2 - 16, "1", size=15, bold=True, color=FIELD))
    b2, w2, h2 = textbox(450, y, "ОПИС В'Ю\n\nзамовлення-вибірки\n«покажи контекст…»",
                         size=12, min_w=220, fill="#eaf0fd", stroke=NEG)
    f.append(b2)
    f.append(text(450, y - h2 / 2 - 16, "2", size=15, bold=True, color=NEG))
    b3, w3, h3 = textbox(730, y, "РУШІЙ РОЗКЛАДКИ\n\nмалює діаграму\nз кожного замовлення",
                         size=12, min_w=220, fill=FILL, stroke=LINE)
    f.append(b3)
    f.append(text(730, y - h3 / 2 - 16, "3", size=15, bold=True, color=MUTED))

    f.append(arrow(170 + w1 / 2 + 6, y, 450 - w2 / 2 - 6, y, color=INK))
    f.append(arrow(450 + w2 / 2 + 6, y, 730 - w3 / 2 - 6, y, color=INK))

    f.append(text(W / 2, 288,
                  "межа між моделлю (1) і в'ю (2) дає багато діаграм з одного джерела",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "three-parts.svg"), W, H, *f)


# ── S3: одна модель у центрі → чотири в'ю C4 ─────────────────────────────────
def fig_one_model_four_views():
    import math
    W, H = 840, 500
    f = []
    f.append(text(W / 2, 32, "Одна модель — чотири в'ю C4", size=17, bold=True))

    cx, cy = W / 2, H / 2 + 12
    b, bw, bh = textbox(cx, cy, "МОДЕЛЬ\nсутності +\nзв'язки", size=13, min_w=150,
                        fill="#eafaf1", stroke=FIELD, bold=True); f.append(b)

    views = [
        (cx - 265, cy - 135, "Контекст", "система серед сусідів", NEG),
        (cx + 265, cy - 135, "Контейнери", "нутрощі системи", NEG),
        (cx - 265, cy + 135, "Компоненти", "нутрощі контейнера", NEG),
        (cx + 265, cy + 135, "Розгортання", "контейнери на залізі", POS),
    ]
    for vx, vy, title_, sub, col in views:
        bb, vbw, vbh = textbox(vx, vy, title_, size=13, min_w=150,
                               fill="#eaf0fd" if col == NEG else "#fdecea",
                               stroke=col, bold=True)
        f.append(bb)
        f.append(text(vx, vy + vbh / 2 + 16, sub, size=10, color=MUTED))
        dx, dy = vx - cx, vy - cy
        d = math.hypot(dx, dy)
        sx = cx + dx / d * (bw / 2 + 4);  sy = cy + dy / d * (bh / 2 + 4)
        ex = vx - dx / d * (vbw / 2 + 8); ey = vy - dy / d * (vbh / 2 + 8)
        f.append(arrow(sx, sy, ex, ey, color=INK))

    render(os.path.join(IMG, "one-model-four-views.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_paths()
    fig_layout_vs_model()
    fig_pipeline_gate()
    fig_three_langs()
    fig_where_each_lives()
    fig_hist_lineage()
    fig_model_fanout()
    fig_three_parts()
    fig_one_model_four_views()
    print("figs written to", IMG)
