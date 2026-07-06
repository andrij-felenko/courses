# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Вибух класів (спадкування) проти набору деталей (композиція) ─────────────
def fig_explosion_vs_composition():
    W, H = 1040, 552
    frags = []

    # роздільник посередині
    frags.append(line(W / 2, 84, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВОРУЧ: дерево-вибух ──────────────────────────────────────────────
    lcx = W / 4
    frags.append(text(lcx, 66, "Спадкування: клас на кожну комбінацію",
                      size=15, bold=True, color=POS))

    # корінь
    root, rw, rh = textbox(lcx, 118, "Ворог", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, min_w=110)
    frags.append(root)

    # рівень 1 — вибір зброї (2 гілки)
    weap = [("Меч", lcx - 150), ("Лук", lcx + 150)]
    for nm, wx in weap:
        frags.append(line(lcx, 138, wx, 176, color=POS, sw=1.4))
        b, _, _ = textbox(wx, 196, nm, size=12, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.4, min_w=88)
        frags.append(b)

    # рівень 2 — ще й броня (×3) → 6 листків
    armor = ["легка", "важка", "магічна"]
    leaf_y = 300
    slot = 158  # ширина, відведена під один блок листків
    for wi, (wnm, wx) in enumerate(weap):
        base_x = wx - slot / 2 + 26
        for ai, anm in enumerate(armor):
            lx = base_x + ai * 52
            frags.append(line(wx, 216, lx, leaf_y - 30, color=POS, sw=1.0))
            frags.append(circle(lx, leaf_y, 15, fill="#fdecea", stroke=POS, sw=1.6))
    # підпис під купою листків — окремо, щоб не накладався
    frags.append(text(lcx, leaf_y + 52, "2 зброї × 3 броні = 6 класів",
                      size=13, bold=True, color=POS))
    frags.append(text(lcx, leaf_y + 74, "+ отрута → 12, + політ → 24 …",
                      size=12, color=MUTED))
    frags.append(text(lcx, leaf_y + 96, "кожна вісь МНОЖИТЬ кількість",
                      size=12, italic=True, color=INK))

    # ── ПРАВОРУЧ: одна сутність + змінні деталі ────────────────────────────
    rcx = 3 * W / 4
    frags.append(text(rcx, 66, "Композиція: одна сутність, змінні деталі",
                      size=15, bold=True, color=FIELD))

    ent, ew, eh = textbox(rcx, 150, ["Ворог", "тримає: зброю + броню"],
                          size=13, bold=True, fill="#eafaf0", stroke=FIELD,
                          sw=1.8, min_w=230)
    frags.append(ent)

    # два «слоти» деталей нижче
    col1_x = rcx - 118
    col2_x = rcx + 118
    top_parts = 240
    frags.append(text(col1_x, top_parts - 14, "Зброя", size=12, bold=True, color=INK))
    for i, nm in enumerate(["Меч", "Лук"]):
        yy = top_parts + i * 46
        b = fitbox(col1_x - 62, yy, 124, 34, nm, size=12, bold=True,
                   fill=FILL, stroke=FIELD, sw=1.4)
        frags.append(b)
        frags.append(line(rcx, 176, col1_x, yy + 17, color=FIELD, sw=1.0, dash="3,3"))

    frags.append(text(col2_x, top_parts - 14, "Броня", size=12, bold=True, color=INK))
    for i, nm in enumerate(["легка", "важка", "магічна"]):
        yy = top_parts + i * 46
        b = fitbox(col2_x - 62, yy, 124, 34, nm, size=12, bold=True,
                   fill=FILL, stroke=FIELD, sw=1.4)
        frags.append(b)
        frags.append(line(rcx, 176, col2_x, yy + 17, color=FIELD, sw=1.0, dash="3,3"))

    frags.append(text(rcx, 476, "2 + 3 = 5 деталей покривають усі 6 комбінацій",
                      size=13, bold=True, color=FIELD))
    frags.append(text(rcx, 498, "нова вісь ДОДАЄ, а не множить",
                      size=12, italic=True, color=INK))
    frags.append(text(rcx, 520, "комбінацію збирають під час роботи",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'explosion-vs-composition.svg'), W, H, *frags,
           title="Чому спадкування вздовж кількох осей вибухає, а композиція — ні")


# ── is-a (успадкувати) проти has-a (тримати всередині) ──────────────────────
def fig_isa_vs_hasa():
    W, H = 1000, 470
    frags = []
    frags.append(line(W / 2, 78, W / 2, H - 26, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВОРУЧ: Stack IS-A Vector (тече зайве) ────────────────────────────
    lcx = W / 4
    frags.append(text(lcx, 60, "is-a: Stack успадковує Vector", size=15, bold=True, color=POS))

    vec, vw, vh = textbox(lcx, 126, ["Vector", "get(i) insert(i) remove(i) …"],
                          size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.7, min_w=290)
    frags.append(vec)
    stk, sw_, sh = textbox(lcx, 262, ["Stack", "push()  pop()"],
                           size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.7, min_w=290)
    frags.append(stk)
    # трикутник-стрілка спадкування (порожній наконечник — намалюємо лінією+«▷» текстом)
    frags.append(line(lcx, 238, lcx, 168, color=POS, sw=2.0))
    frags.append(text(lcx, 166, "▷", size=18, bold=True, color=POS))
    frags.append(text(lcx + 66, 205, "is-a", size=12, italic=True, color=POS))

    # витік: усе публічне Vector протікає крізь Stack
    frags.append(text(lcx, 312, "успадкував УСЕ публічне Vector:", size=11, color=INK))
    frags.append(text(lcx, 332, "s.get(2) лізе в середину — LIFO зламано",
                      size=12, bold=True, color=POS))
    frags.append(text(lcx, 352, "база змінилась → Stack може впасти",
                      size=11, color=MUTED))

    # ── ПРАВОРУЧ: Stack HAS-A Vector (сховано) ─────────────────────────────
    rcx = 3 * W / 4
    frags.append(text(rcx, 60, "has-a: Stack тримає Vector усередині",
                      size=15, bold=True, color=FIELD))

    stk2, s2w, s2h = textbox(rcx, 150, ["Stack", "push()  pop()   ← лише це назовні"],
                             size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=320)
    frags.append(stk2)
    # приватне поле всередині — менша рамка нижче, з'єднана «має»
    vec2, v2w, v2h = textbox(rcx, 268, ["private Vector v", "(схований, назовні не видно)"],
                             size=11, bold=True, fill=FILL, stroke=FIELD, sw=1.4, min_w=250)
    frags.append(vec2)
    frags.append(arrow(rcx, 176, rcx, 244, color=FIELD, sw=1.8))
    frags.append(text(rcx + 52, 212, "has-a", size=12, italic=True, color=FIELD))

    frags.append(text(rcx, 330, "get(i) НЕ видно — контракт цілий",
                      size=12, bold=True, color=FIELD))
    frags.append(text(rcx, 350, "Vector можна підмінити — клієнт не помітить",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'isa-vs-hasa.svg'), W, H, *frags,
           title="Успадкувати — і протекло зайве; тримати всередині — і видно лише потрібне")


# ── Підрахунок класів: добуток (спадкування) проти суми (композиція) ─────────
def fig_class_count_growth():
    """Скільки типів дає кожна нова вісь: спадкування множить, композиція додає."""
    W, H = 1060, 620
    frags = []
    frags.append(line(W / 2, 92, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВОРУЧ: матриця комбінацій = добуток ──────────────────────────────
    lcx = W / 4
    frags.append(text(lcx, 70, "Спадкування: клас на клітину", size=15, bold=True, color=POS))
    frags.append(text(lcx, 90, "кількість = ДОБУТОК осей", size=12, italic=True, color=INK))

    cols = ["Меч", "Лук"]                 # 2 зброї
    rows = ["легка", "важка", "магічна"]  # 3 броні
    cw, ch = 96, 40
    gx = lcx - (len(cols) * cw) / 2 + 34  # зсув під підпис рядків
    gy = 130
    # шапка колонок
    for ci, c in enumerate(cols):
        frags.append(text(gx + ci * cw + cw / 2, gy - 12, c, size=12, bold=True, color=INK))
    # клітини-класи
    for ri, r in enumerate(rows):
        frags.append(text(gx - 12, gy + ri * ch + ch / 2 + 4, r,
                          size=12, bold=True, color=INK, anchor="end"))
        for ci in range(len(cols)):
            x = gx + ci * cw
            y = gy + ri * ch
            frags.append(fitbox(x + 3, y + 3, cw - 6, ch - 6,
                                "%s+%s" % (cols[ci][:3], r[:3]),
                                size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.3))
    grid_bottom = gy + len(rows) * ch
    frags.append(text(lcx, grid_bottom + 30, "2 × 3 = 6 класів", size=15, bold=True, color=POS))
    # сходинка зростання
    steps_l = [
        "+ отрута (×2):   6 × 2 = 12",
        "+ політ  (×2):  12 × 2 = 24",
        "+ ранг   (×3):  24 × 3 = 72",
    ]
    for i, s in enumerate(steps_l):
        frags.append(text(lcx, grid_bottom + 58 + i * 22, s, size=12, color=MUTED))
    frags.append(text(lcx, grid_bottom + 58 + 3 * 22 + 8,
                      "кожна вісь МНОЖИТЬ усе дерево", size=12, italic=True, color=POS))

    # ── ПРАВОРУЧ: два стовпчики деталей = сума ──────────────────────────────
    rcx = 3 * W / 4
    frags.append(text(rcx, 70, "Композиція: клас на деталь", size=15, bold=True, color=FIELD))
    frags.append(text(rcx, 90, "кількість = СУМА осей", size=12, italic=True, color=INK))

    col1 = rcx - 92
    col2 = rcx + 92
    top = 130
    bh = 34
    frags.append(text(col1, top - 12, "Зброя (2)", size=12, bold=True, color=INK))
    for i, nm in enumerate(cols):
        frags.append(fitbox(col1 - 60, top + i * (bh + 8), 120, bh, nm,
                            size=12, bold=True, fill=FILL, stroke=FIELD, sw=1.4))
    frags.append(text(col2, top - 12, "Броня (3)", size=12, bold=True, color=INK))
    for i, nm in enumerate(rows):
        frags.append(fitbox(col2 - 60, top + i * (bh + 8), 120, bh, nm,
                            size=12, bold=True, fill=FILL, stroke=FIELD, sw=1.4))
    parts_bottom = top + 3 * (bh + 8)
    frags.append(text(rcx, parts_bottom + 22, "2 + 3 = 5 деталей", size=15, bold=True, color=FIELD))
    steps_r = [
        "+ отрута (+1):   5 + 1 = 6",
        "+ політ  (+1):   6 + 1 = 7",
        "+ ранг   (+3):   7 + 3 = 10",
    ]
    for i, s in enumerate(steps_r):
        frags.append(text(rcx, parts_bottom + 50 + i * 22, s, size=12, color=MUTED))
    frags.append(text(rcx, parts_bottom + 50 + 3 * 22 + 8,
                      "нова вісь лише ДОДАЄ рядок", size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, 'class-count-growth.svg'), W, H, *frags,
           title="Той самий ворог: спадкування рахує добуток, композиція — суму")


# ── Анатомія ціни делегування: зайвий рівень непрямості на виклик ────────────
def fig_delegation_cost():
    """Що саме коштує композиція: обгортка + стрибок через vtable до реалізації."""
    W, H = 1000, 470
    frags = []

    frags.append(text(W / 2, 58, "Один виклик attack() — куди він насправді йде",
                      size=15, bold=True, color=INK))

    # ланцюг блоків зліва направо
    y = 150
    bw, bh = 190, 66
    xs = [40, 300, 560, 820 - 40]  # ліві краї блоків (останній трохи ближче)
    # 1. клієнт
    frags.append(fitbox(xs[0], y, bw, bh, ["клієнт", "enemy.attack()"],
                        size=12, bold=True, fill=FILL, stroke=INK, sw=1.5))
    # 2. обгортка Enemy
    frags.append(fitbox(xs[1], y, bw, bh, ["Enemy::attack()", "{ return weapon->hit(); }"],
                        size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6))
    # 3. vtable
    frags.append(fitbox(xs[2], y, bw, bh, ["vtable зброї", "знайти адресу hit()"],
                        size=11, bold=True, fill="#fff6e6", stroke="#d08a1e", sw=1.6))
    # 4. реалізація
    frags.append(fitbox(xs[3], y, bw, bh, ["Sword::hit()", "{ return 10; }"],
                        size=11, bold=True, fill=FILL, stroke=INK, sw=1.5))

    # стрілки між блоками з підписами витрат
    labels = ["виклик обгортки", "віртуальний виклик", "стрибок за адресою"]
    for i in range(3):
        x1 = xs[i] + bw
        x2 = xs[i + 1]
        frags.append(arrow(x1 + 2, y + bh / 2, x2 - 2, y + bh / 2, color=MUTED, sw=1.8))
        frags.append(text((x1 + x2) / 2, y - 16, labels[i], size=10, italic=True, color=MUTED))

    # що з цього ціна — рамка-висновок
    frags.append(text(W / 2, y + bh + 60, "Ціна проти прямого поля-об'єкта:",
                      size=13, bold=True, color=INK))
    costs = [
        "+ рядок делегування у власника (обгортка на кожен метод, що прокидається)",
        "+ один рівень непрямості: щоб знати результат, треба знати, ЩО зараз у полі",
        "+ віртуальний виклик: ≈ 1–5 нс, і головне — компілятор НЕ вбудує (inline) тіло",
    ]
    for i, c in enumerate(costs):
        frags.append(text(W / 2, y + bh + 86 + i * 24, c, size=12, color=INK))

    frags.append(text(W / 2, y + bh + 86 + 3 * 24 + 10,
                      "На холодному коді — тоне; на мільйони викликів/с гарячого циклу — міряй",
                      size=12, italic=True, color=POS))

    render(os.path.join(IMG, 'delegation-cost.svg'), W, H, *frags,
           title="Чесна ціна композиції на один виклик")


# ── Дві нитки історії: принцип GoF і проблема крихкої бази ───────────────────
def fig_two_threads_timeline():
    """Часова вісь: як паралельно визрівали принцип 'композиція над спадкуванням'
    (нитка ідеї) і проблема крихкого базового класу (нитка болю), і де вони збіглися.
    Кожну подію ставимо в СВІЙ стовпчик (рівні кроки) — щоб рамки не тислися,
    а рік підписуємо ПІД стовпчиком, осторонь від ліній-виносок."""
    W, H = 1120, 590
    frags = []

    axis_y = H / 2

    # головна вісь
    frags.append(line(60, axis_y, W - 40, axis_y, color=INK, sw=2.0))

    # заголовок
    frags.append(text(W / 2, 34, "Дві нитки, що зійшлися: принцип згори, крихка база знизу",
                      size=16, bold=True, color=INK))

    # шість подій у власних рівновіддалених стовпчиках; поле thread: +1 угору, -1 униз
    #   (col, year, thread, [рядки])
    events = [
        (0, "1986", -1, ["перші описи", "ламкості спадкування", "(ще без назви)"]),
        (1, "1990", +1, ["OOPSLA, сесія", "«Towards an", "Architecture Handbook»", "Gamma + Helm"]),
        (2, "1994", +1, ["Design Patterns", "(Банда чотирьох):", "«надавай перевагу", "композиції»"]),
        (3, "1994", -1, ["названо «fragile", "base class problem»", "у компонентних", "системах"]),
        (4, "1995", +1, ["друк, копірайт 1995:", "принцип №2 у вступі,", "курсивом"]),
        (5, "1995", -1, ["Java: символьні", "посилання в байткоді —", "зсуви звіряються", "при завантаженні"]),
    ]
    ncol = len(events)
    xL, xR = 130, W - 100
    step = (xR - xL) / (ncol - 1)
    def CX(col):
        return xL + col * step

    for col, yr, thread, lines in events:
        xx = CX(col)
        green = thread > 0
        fill = "#eafaf0" if green else "#fdecea"
        stroke = FIELD if green else POS
        # рамка — центр над/під віссю; висота від кількості рядків
        cy = axis_y - 118 if green else axis_y + 118
        b, bw, bh = textbox(xx, cy, lines, size=11, bold=True,
                            fill=fill, stroke=stroke, sw=1.6, min_w=170)
        frags.append(b)
        # виноска від рамки до вузла на осі — ПРЯМА в тому самому X (рік підпишемо збоку)
        if green:
            frags.append(line(xx, cy + bh / 2, xx, axis_y - 7, color=stroke, sw=1.4, dash="4,3"))
        else:
            frags.append(line(xx, axis_y + 7, xx, cy - bh / 2, color=stroke, sw=1.4, dash="4,3"))
        frags.append(circle(xx, axis_y, 6, fill=fill, stroke=stroke, sw=2.0))
        # рік — маленькою міткою збоку від вузла (не під ним, де йде виноска протилежної нитки),
        # праворуч від точки, трохи вище осі для нижніх і трохи нижче для верхніх — завжди в «чистій» зоні
        ylbl_y = axis_y - 12 if not green else axis_y + 20
        frags.append(text(xx + 16, ylbl_y, yr, size=12, bold=True, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'two-threads-timeline.svg'), W, H, *frags,
           title=None)


if __name__ == "__main__":
    fig_explosion_vs_composition()
    fig_isa_vs_hasa()
    fig_class_count_growth()
    fig_delegation_cost()
    fig_two_threads_timeline()
    print("figures written to", IMG)
