# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: керувати входом і бачити вихід ─────────────────────────────────
def fig_control_observe():
    W, H = 940, 380
    frags = []
    frags.append(text(W / 2, 60, "Тест мусить мати два важелі: задати вхід і побачити вихід",
                      size=15, bold=True))

    # центральний компонент
    comp_cx, comp_cy = W / 2, 210
    comp, cw, ch = textbox(comp_cx, comp_cy, "Компонент\n(логіка, яку перевіряємо)",
                           size=14, bold=True, fill="#eef4ff", stroke=NEG, sw=2.4,
                           pad=18, min_w=260)
    # ЛІВОРУЧ: керування (control) — ставимо вхід і стан
    ctrl, ctw, cth = textbox(150, comp_cy, "КЕРУВАННЯ\nзадати вхід\nі стан",
                             size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2, pad=12,
                             min_w=170)
    frags.append(ctrl)
    frags.append(arrow(150 + ctw / 2, comp_cy, comp_cx - cw / 2 - 6, comp_cy,
                       color=FIELD, sw=2.6))
    frags.append(text((150 + ctw / 2 + comp_cx - cw / 2) / 2, comp_cy - 16,
                      "стимул", size=11, italic=True, color=MUTED))

    # ПРАВОРУЧ: спостереження (observe) — читаємо вихід і стан
    obs, obw, obh = textbox(W - 150, comp_cy, "СПОСТЕРЕЖЕННЯ\nпрочитати вихід\nі стан",
                            size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2, pad=12,
                            min_w=170)
    frags.append(obs)
    frags.append(arrow(comp_cx + cw / 2 + 6, comp_cy, W - 150 - obw / 2, comp_cy,
                       color=FIELD, sw=2.6))
    frags.append(text((comp_cx + cw / 2 + W - 150 - obw / 2) / 2, comp_cy - 16,
                      "реакція", size=11, italic=True, color=MUTED))

    frags.append(comp)

    # висновок унизу
    frags.append(text(W / 2, 330,
                      "Тестовність = наскільки легко дотягтися до обох важелів.",
                      size=13, bold=True, color=NEG))
    render(os.path.join(IMG, 'control-observe.svg'), W, H, *frags,
           title="Що взагалі потрібно, щоб протестувати шматок системи")


# ── Фігура 2: дерево тактик тестовності (дві родини) ─────────────────────────
def fig_tactics_tree():
    W, H = 980, 660
    frags = []
    # корінь
    root, rw, rh = textbox(W / 2, 60, "Полегшити перевірку системи",
                           size=16, bold=True, fill="#eef4ff", stroke=NEG, sw=2.2, pad=14)
    frags.append(root)

    box_w = 268
    # родина, задана лівим краєм колонки боксів
    fam = [
        (60, "Керувати станом\nі спостерігати його", NEG,
         ["Спеціальні тестові інтерфейси",
          "Абстрагувати джерела даних",
          "Пісочниця (ізоляція)",
          "Запис / відтворення",
          "Локалізувати зберігання стану",
          "Виконувані твердження"]),
        (W - 60 - box_w, "Обмежити\nскладність", FIELD,
         ["Обмежити структурну складність",
          "Обмежити недетермінізм"]),
    ]
    head_y = 190
    for left, head, col, items in fam:
        hcx = left + box_w / 2
        frags.append(line(W / 2, 60 + rh / 2, hcx, head_y - 34, color=MUTED, sw=1.5))
        hb, hw, hh = textbox(hcx, head_y, head, size=14.5, bold=True, fill="#fbfbfb",
                             stroke=col, sw=2.2, pad=12, min_w=box_w)
        frags.append(hb)
        # вертикальна «жила» ліворуч від колонки боксів
        spine_x = left - 20
        item_h = 46
        gap = 12
        top_y = head_y + hh / 2 + 26
        centers = [top_y + item_h / 2 + i * (item_h + gap) for i in range(len(items))]
        # жила від низу заголовка до останнього бокса
        frags.append(line(hcx, head_y + hh / 2, hcx, top_y - 10, color=col, sw=1.4))
        frags.append(line(spine_x, top_y - 10, spine_x, centers[-1], color=col, sw=1.4))
        frags.append(line(hcx, top_y - 10, spine_x, top_y - 10, color=col, sw=1.4))
        for it, cyc in zip(items, centers):
            frags.append(line(spine_x, cyc, left, cyc, color=col, sw=1.3))
            frags.append(fitbox(left, cyc - item_h / 2, box_w, item_h, it, size=12.5,
                                fill=FILL, stroke=col, sw=1.5, pad=8))
    render(os.path.join(IMG, 'tactics-tree.svg'), W, H, *frags,
           title="Тактики тестовності: дві родини за спільною метою")


# ── Фігура 3: смуга переходу пари через чотири світи ──────────────────────────
def fig_testability_lineage():
    W, H = 1000, 560
    frags = []
    frags.append(text(W / 2, 34,
                      "Одна пара «керованість / спостережуваність» — чотири світи",
                      size=16, bold=True))

    # вертикальна вісь часу ліворуч; віхи йдуть згори вниз
    axis_x = 250
    top_y = 90
    bot_y = 520
    frags.append(line(axis_x, top_y, axis_x, bot_y, color=MUTED, sw=2.2))

    # (рік, підпис-віха, колір рамки, текст праворуч)
    stops = [
        ("1959–60", "Теорія керування", NEG,
         "Калман уводить керованість\nі спостережуваність як\nвластивості стану системи"),
        ("1979–80", "Апаратне тестування", NEG,
         "SCOAP (Сандія): перший алгоритм,\nщо рахує ці міри для кожної\nлінії кристала"),
        ("1990", "Плати (JTAG)", NEG,
         "IEEE 1149.1: граничний скан\nвбудовує доступ у залізо, коли\nщупом уже не дотягтися"),
        ("1991", "Програмне забезпечення", FIELD,
         "Фрідман переносить пару в код\n(доменна тестовність); Біндер, ~1994:\n«керуй входом — спостерігай вихід»"),
        ("2012", "Канон тактик", FIELD,
         "Бас, Клементс, Казман: пара стає\nкоренем дерева тактик тестовності\n(розділ якісних атрибутів)"),
    ]
    n = len(stops)
    span = bot_y - top_y
    ys = [top_y + span * i / (n - 1) for i in range(n)]

    yr_x = 150            # центр рамки-року (ліворуч від осі)
    box_left = axis_x + 60  # ліва межа рамки-опису (праворуч від осі)
    box_w = 640
    for (yr, milestone, col, desc), cy in zip(stops, ys):
        # вузол на осі
        frags.append(circle(axis_x, cy, 7, fill=BG, stroke=col, sw=2.6))
        # рік + віха ліворуч
        yb, yw, yh = textbox(yr_x, cy, yr + "\n" + milestone, size=12.5, bold=True,
                             fill="#eef4ff" if col == NEG else "#eafaf1",
                             stroke=col, sw=2, pad=9, min_w=150)
        frags.append(line(yr_x + yw / 2, cy, axis_x, cy, color=col, sw=1.6))
        frags.append(yb)
        # опис праворуч
        lines = desc.split("\n")
        bh = len(lines) * 12.5 * 1.3 + 18
        frags.append(line(axis_x, cy, box_left, cy, color=col, sw=1.6))
        frags.append(fitbox(box_left, cy - bh / 2, box_w, bh, desc, size=12.5,
                            fill=FILL, stroke=col, sw=1.5, pad=10))
    render(os.path.join(IMG, 'testability-lineage.svg'), W, H, *frags,
           title=None)


# ── Фігура 4: чотири ворота дефекту (PIE / RIPR) ─────────────────────────────
def fig_pie_gates():
    W, H = 1120, 500
    frags = []
    frags.append(text(W / 2, 30,
                      "Дефект стає видимим, лише коли пройде всі чотири ворота",
                      size=16, bold=True))

    gates = [
        ("Досяжність", "reach",
         "Керування: обрати\nвхід, що доводить\nвиконання до\nхворого місця", NEG),
        ("Зараження", "infect",
         "Керування: вхід має\nзіпсувати внутрішній\nстан, а не проскочити\nповз хибний рядок", NEG),
        ("Поширення", "propagate",
         "Мала DRR: не дати\nвиходу проковтнути\nзіпсоване значення\n(інформація не гине)", FIELD),
        ("Виявність", "reveal",
         "Спостереження: оракул\nчи асерт мусить\nдивитися саме туди,\nде виліз дефект", FIELD),
    ]
    xs = [180, 450, 720, 990]
    gy = 128
    boxes = []
    for (name, eng, _, col), x in zip(gates, xs):
        b, w, h = textbox(x, gy, name + "\n(" + eng + ")", size=14, bold=True,
                          fill="#eef4ff" if col == NEG else "#eafaf1",
                          stroke=col, sw=2.2, pad=12, min_w=200)
        boxes.append((b, w, h, x, col))
    # стрілки між воротами
    for i in range(len(xs) - 1):
        x1 = xs[i] + boxes[i][1] / 2
        x2 = xs[i + 1] - boxes[i + 1][1] / 2
        frags.append(arrow(x1, gy, x2, gy, color=MUTED, sw=2.4))
    frags.append(text(180, gy - boxes[0][2] / 2 - 13, "дефект у коді",
                      size=12, italic=True, color=POS))
    for b, w, h, x, col in boxes:
        frags.append(b)
    # підписи-важелі під воротами
    capy = gy + boxes[0][2] / 2 + 8
    for (name, eng, lever, col), x in zip(gates, xs):
        frags.append(fitbox(x - 115, capy, 230, 76, lever, size=11,
                             fill="#fbfbfb", stroke=col, sw=1.4, pad=8))
    # смуга: скільки дефектів доживає (кумулятивний добуток імовірностей)
    p = [0.90, 0.63, 0.44, 0.24]
    base, scale = 432, 122
    frags.append(text(45, 300, "доживає до кроку:", size=11, italic=True,
                      color=MUTED, anchor="start"))
    frags.append(line(40, base, W - 40, base, color=MUTED, sw=1.2))
    for val, x in zip(p, xs):
        hgt = val * scale
        frags.append(rect(x - 32, base - hgt, 64, hgt, fill="#eaf0fd",
                           stroke=NEG, sw=1.6))
        frags.append(text(x, base - hgt - 8, "%d%%" % round(val * 100),
                          size=12, bold=True, color=NEG))
    fb, fw, fh = textbox(W / 2, 472,
                         "тестовність = p(досяг) · p(зарази) · p(пошир) · p(вияви)   —   "
                         "будь-який ≈ 0 робить добуток ≈ 0: дефект ховається",
                         size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10)
    frags.append(fb)
    render(os.path.join(IMG, 'pie-gates.svg'), W, H, *frags, title=None)


# ── Фігура 5: DRR-лійка — стискання ковтає дефект ─────────────────────────────
def fig_drr_funnel():
    W, H = 1020, 545
    frags = []
    frags.append(text(W / 2, 30,
                      "Велика DRR: різні входи зливаються в однаковий вихід — і ховають дефект",
                      size=15, bold=True))
    frags.append(text(455, 78, "функція стискає: багато внутрішніх станів → мало виходів",
                      size=12, italic=True, color=MUTED))
    frags.append(text(200, 120, "Внутрішні стани (багато)", size=12, bold=True))

    dot_x = 200
    dys = [162, 207, 252, 297, 342, 387, 432]
    # призначення точок у бакети: 0,1→A ; 2,3,4→B ; 5,6→C
    buckets = {"A": 180, "B": 292, "C": 404}
    assign = ["A", "A", "B", "B", "B", "C", "C"]
    special = {2: NEG, 4: POS}          # 2 — правильний стан, 4 — зіпсований дефектом
    bx_left = 720
    # спершу лінії (щоб точки й бакети лягли зверху)
    for i, dy in enumerate(dys):
        bcy = buckets[assign[i]]
        col = special.get(i, MUTED)
        sw = 3.0 if i in special else 1.2
        frags.append(line(dot_x, dy, bx_left, bcy, color=col, sw=sw))
    # точки
    for i, dy in enumerate(dys):
        if i in special:
            frags.append(circle(dot_x, dy, 9, fill=BG, stroke=special[i], sw=3))
        else:
            frags.append(circle(dot_x, dy, 6, fill=FILL, stroke=MUTED, sw=1.5))
    # бакети
    for name, bcy in buckets.items():
        b, w, h = textbox(795, bcy, "вихід " + name, size=14, bold=True,
                          fill="#eef4ff", stroke=NEG, sw=2, pad=12, min_w=150)
        frags.append(b)
    frags.append(text(885, 286, "той самий", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(885, 304, "вихід!", size=12, bold=True, color=POS, anchor="start"))
    # низ: легенда + формула
    fb, fw, fh = textbox(W / 2, 500,
                         "Синій — правильний стан; червоний — стан, зіпсований дефектом. Обидва дають вихід B → дефект не видно.\n"
                         "DRR = |домен| / |діапазон|: велика DRR → сильне стискання → мала ймовірність, що дефект дотягнеться до виходу.",
                         size=12, fill="#fbfbfb", stroke=FIELD, sw=1.6, pad=10)
    frags.append(fb)
    render(os.path.join(IMG, 'drr-funnel.svg'), W, H, *frags, title=None)


# ── Фігура 6: додавання проти множення (простір станів) ──────────────────────
def _grid(x, y, w, h, n=8, col="#c9d6ea"):
    out = [rect(x, y, w, h, fill="#eef4ff", stroke=NEG, sw=2)]
    for i in range(1, n):
        out.append(line(x + i * w / n, y, x + i * w / n, y + h, color=col, sw=0.8))
        out.append(line(x, y + i * h / n, x + w, y + i * h / n, color=col, sw=0.8))
    return "".join(out)


def fig_state_blowup():
    W, H = 1020, 480
    frags = []
    frags.append(text(W / 2, 32, "Зчеплення перетворює додавання на множення",
                      size=16, bold=True))

    # ЛІВОРУЧ: два маленькі квадрати
    frags.append(text(165, 138, "Модуль A", size=12, bold=True))
    frags.append(text(300, 138, "Модуль B", size=12, bold=True))
    frags.append(_grid(120, 152, 90, 90))
    frags.append(_grid(255, 152, 90, 90))
    frags.append(text(232, 205, "+", size=26, bold=True, color=INK))
    lb, lw, lh = textbox(232, 300, "нарізно (розчеплені):\n2¹⁰ + 2¹⁰ = 2048 тестів",
                         size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10)
    frags.append(lb)

    # роздільник
    frags.append(text(500, 200, "vs", size=16, bold=True, color=MUTED))
    frags.append(line(500, 218, 500, 352, color=MUTED, sw=1.4, dash="6 5"))

    # ПРАВОРУЧ: один великий квадрат
    frags.append(text(740, 108, "Модулі A і B, перевірені разом", size=13, bold=True))
    frags.append(_grid(620, 120, 240, 240, n=16))
    rb, rw, rh = textbox(740, 400, "разом (зчеплені):\n2²⁰ ≈ 1 048 576 тестів",
                         size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=10)
    frags.append(rb)

    frags.append(text(W / 2, 452,
                      "Тут різниця — 512-кратна: тому складність обмежують, а тести штовхають до одиниць.",
                      size=13, bold=True, color=NEG))
    render(os.path.join(IMG, 'state-blowup.svg'), W, H, *frags, title=None)


# ── Вставка proj-test-doubles ────────────────────────────────────────────────
# Фігура A: сходинка п'яти дублерів (таксономія Мезароша)
def fig_double_ladder():
    W, H = 1220, 525
    frags = []
    cols = [
        (30, 165, "Дублер"),
        (199, 402, "Роль — навіщо підставляють"),
        (605, 118, "Відповідає\nна запит?"),
        (727, 118, "Записує\nвиклики?"),
        (849, 132, "Несе\nочікування?"),
        (985, 205, "Звіряє через"),
    ]
    head_top, head_h = 44, 56
    row_h, gap = 72, 6
    body_top = head_top + head_h + 4
    for left, w, head in cols:
        frags.append(fitbox(left, head_top, w, head_h, head, size=13, bold=True,
                            fill="#eef4ff", stroke=NEG, sw=1.6, pad=7))
    rows = [
        ("Пустушка\n(dummy)",
         "Тільки щоб заповнити список\nпараметрів; у ділі не працює",
         "—", "—", "—", "нічого\n(не звіряють)"),
        ("Заглушка\n(stub)",
         "Готова відповідь на запит:\nподає вхід, який SUT прочитає",
         "так", "—", "—", "стан"),
        ("Фейк\n(fake)",
         "Спрощена, але РОБОЧА реалізація\n(напр. сховище в пам'яті)",
         "так", "—", "—", "стан"),
        ("Шпигун\n(spy)",
         "Заглушка, що ще й ЗАПИСУЄ\nвиклики — звіряєш їх після",
         "так", "так", "—", "взаємодію\n(після факту)"),
        ("Мок\n(mock)",
         "Озброєний ОЧІКУВАННЯМИ\nнаперед; звіряє себе сам",
         "так", "так", "так", "взаємодію\n(вбудовано)"),
    ]
    for i, (name, role, a, r, e, v) in enumerate(rows):
        top = body_top + i * (row_h + gap)
        frags.append(fitbox(cols[0][0], top, cols[0][1], row_h, name, size=13.5,
                            bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, pad=7))
        frags.append(fitbox(cols[1][0], top, cols[1][1], row_h, role, size=13.5,
                            fill=FILL, stroke=MUTED, sw=1.3, pad=8))
        for (left, w, _), val in zip(cols[2:5], (a, r, e)):
            frags.append(fitbox(left, top, w, row_h, val, size=17, bold=True,
                                fill=BG, stroke=MUTED, sw=1.3, pad=6,
                                color=(FIELD if val == "так" else MUTED)))
        vcol = FIELD if "взаєм" in v else (NEG if "стан" in v else MUTED)
        frags.append(fitbox(cols[5][0], top, cols[5][1], row_h, v, size=13,
                            bold=True, fill=FILL, stroke=vcol, sw=1.4, pad=7, color=vcol))
    render(os.path.join(IMG, 'double-ladder.svg'), W, H, *frags,
           title="П'ять тестових дублерів: сходинка спроможності")


# Фігура B: перевірка стану проти перевірки взаємодії (Фаулер)
def fig_state_vs_interaction():
    W, H = 1060, 560
    frags = []
    frags.append(rect(24, 112, 330, 300, fill="#f0f5ff", stroke="#dfe8fb", sw=1.4, rx=14))
    frags.append(rect(706, 112, 330, 300, fill="#f0fbf4", stroke="#d8f0e2", sw=1.4, rx=14))
    frags.append(text(189, 98, "Перевірка стану", size=15, bold=True, color=NEG))
    frags.append(text(871, 98, "Перевірка взаємодії", size=15, bold=True, color=FIELD))

    sut, sw_, sh_ = textbox(530, 250, "Сервіс замовлень\n(SUT): placeOrder()",
                            size=14, bold=True, fill="#fffbea", stroke=INK, sw=2.2,
                            pad=16, min_w=210)

    a, aw, ah = textbox(189, 172, "Каталог цін\n(заглушка)", size=13, bold=True,
                        fill=FILL, stroke=NEG, sw=2, pad=11, min_w=170)
    b, bw, bh = textbox(189, 302, "Сховище\n(фейк у пам'яті)", size=13, bold=True,
                        fill=FILL, stroke=NEG, sw=2, pad=11, min_w=170)
    frags += [a, b]
    frags.append(arrow(189 + aw / 2, 172, 530 - sw_ / 2, 212, color=NEG, sw=2.2))
    frags.append(text((189 + aw / 2 + 530 - sw_ / 2) / 2, 176, "повертає ціну",
                      size=11, italic=True, color=MUTED))
    frags.append(arrow(530 - sw_ / 2, 292, 189 + bw / 2, 302, color=NEG, sw=2.2))
    frags.append(text((530 - sw_ / 2 + 189 + bw / 2) / 2, 276, "save(order)",
                      size=11, italic=True, color=MUTED))
    frags.append(sut)
    frags.append(fitbox(39, 346, 300, 54,
                        "Після виклику читаємо стан фейка:\nчи замовлення справді збережене",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, pad=8))

    c, cw_, ch_ = textbox(871, 228, "Сповіщувач\n(мок / шпигун)", size=13, bold=True,
                          fill=FILL, stroke=FIELD, sw=2, pad=11, min_w=170)
    frags.append(arrow(530 + sw_ / 2, 240, 871 - cw_ / 2, 232, color=FIELD, sw=2.2))
    frags.append(text((530 + sw_ / 2 + 871 - cw_ / 2) / 2, 214, "sendConfirmation(...)",
                      size=11, italic=True, color=MUTED))
    frags.append(c)
    frags.append(fitbox(721, 300, 300, 72,
                        "Після: чи SUT покликав\nsendConfirmation(email, сума)\n— саме раз і з тими даними",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, pad=8))

    fb, fw, fh = textbox(530, 502,
                         "За Фаулером: заглушка ВІДПОВІДАЄ на запит (звіряєш стан) · "
                         "мок ЗВІРЯЄ команду (звіряєш взаємодію)",
                         size=13, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8, pad=11)
    frags.append(fb)
    render(os.path.join(IMG, 'state-vs-interaction.svg'), W, H, *frags,
           title="Дві перевірки однієї дії")


# Фігура C: мок на швах, а не на внутрішніх співавторах; скромний об'єкт
def fig_seams():
    W, H = 1100, 540
    frags = []
    frags.append(rect(50, 70, 560, 330, fill="#f5f8ff", stroke=NEG, sw=2.6, rx=16))
    frags.append(text(330, 96, "Ваш код — усередині шва", size=14, bold=True, color=NEG))
    for label, cx in [("Калькулятор\nсуми", 165), ("Політика\nзнижки", 330),
                      ("Валідатор\nзамовлення", 495)]:
        rb, rw, rh = textbox(cx, 190, label, size=12.5, bold=True, fill="#eafaf1",
                             stroke=FIELD, sw=1.8, pad=10, min_w=140)
        frags.append(rb)
    frags.append(fitbox(70, 300, 520, 54,
                        "Це свій код: мок тут зайвий і шкідливий — бери справжні, звіряй стан.",
                        size=12.5, fill=BG, stroke=FIELD, sw=1.4, pad=9))
    frags.append(text(800, 86, "Зовнішні шви — мокай ТУТ", size=14, bold=True, color=POS))
    for label, cy in [("База даних", 130), ("Платіжний шлюз", 230), ("Пошта / SMS", 330)]:
        sb, sbw, sbh = textbox(800, cy, label, size=13, bold=True, fill="#fdecea",
                               stroke=POS, sw=2, pad=11, min_w=170)
        frags.append(arrow(612, cy, 800 - sbw / 2 - 4, cy, color=POS, sw=2))
        frags.append(sb)
    frags.append(fitbox(50, 440, 1000, 66,
                        "Скромний об'єкт (humble object): на крайньому адаптері (напр. SmtpNotifier) лишай МІНІМУМ коду —\n"
                        "усю логіку винеси всередину, у чисту тестовану частину; оболонка лише делегує їй.",
                        size=13, fill="#eef4ff", stroke=NEG, sw=1.6, pad=10))
    render(os.path.join(IMG, 'seams.svg'), W, H, *frags,
           title="Мокай на архітектурних швах, не на внутрішніх співавторах")


# ── Вставка proj-deterministic-simulation ───────────────────────────────────
# Фігура A: система як чиста функція від (входи, зерно)
def fig_sim_purefunc():
    W, H = 920, 440
    f = []
    a, _, _ = textbox(115, 135, "входи\n(сценарій,\nнавантаження)", size=13)
    f.append(a)
    b, _, _ = textbox(115, 275, "зерно\n(одне число)", size=13, stroke=FIELD, sw=2.2)
    f.append(b)
    f.append(text(115, 324, "єдина ручка", size=11, color=FIELD))
    # контейнер-симулятор
    f.append(rect(310, 70, 380, 320, fill=BG, stroke=LINE, sw=1.8))
    f.append(text(500, 97, "детермінований симулятор", size=14, bold=True))
    f.append(fitbox(330, 116, 340, 42, "віртуальний годинник — не time.Now()", size=12))
    f.append(fitbox(330, 168, 340, 42, "засіяний PRNG — не глобальний rand()", size=12))
    f.append(fitbox(330, 220, 340, 42, "симульовані мережа й диск", size=12))
    f.append(fitbox(330, 300, 340, 66,
                    "ОДИН потік · подієвий цикл\nсимулятор тасує порядок і впорскує збої",
                    size=12, fill="#eef2fb"))
    c, _, _ = textbox(805, 200, "результат\n— біт-у-біт\nтой самий", size=13)
    f.append(c)
    f.append(mtext(805, 262, ["відтворюється", "з того самого зерна"], size=11, color=MUTED))
    f.append(arrow(172, 135, 305, 132))
    f.append(arrow(172, 273, 305, 250))
    f.append(arrow(692, 200, 752, 200))
    render(os.path.join(IMG, 'sim-purefunc.svg'), W, H, *f,
           title="Система як чиста функція від (входи, зерно)")


# Фігура B: збій = число; перебір зерен стискає час, повтор відтворює
def fig_sim_seedspace():
    W, H = 920, 360
    f = []
    f.append(text(360, 62, "прогін по зернах 0…N — роки збоїв за хвилини", size=13))
    x0, y0, cell, pitch = 60, 84, 40, 50
    red = {(0, 3), (1, 8)}
    for r in range(2):
        for cidx in range(12):
            cx = x0 + cidx * pitch
            cy = y0 + r * pitch
            if (r, cidx) in red:
                f.append(rect(cx, cy, cell, cell, fill="#fdecea", stroke=POS, sw=2))
            else:
                f.append(rect(cx, cy, cell, cell, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(rect(690, 86, 26, 22, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(724, 103, "інваріант цілий", size=12, anchor="start"))
    f.append(rect(690, 128, 26, 22, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(724, 145, "інваріант порушено", size=12, anchor="start"))
    bx, _, _ = textbox(360, 272, "повтор із тим самим зерном →\nтой самий збій, крок за кроком",
                       size=13, min_w=520)
    f.append(bx)
    hx = x0 + 8 * pitch
    hy = y0 + 1 * pitch
    f.append(arrow(hx + 10, hy + cell + 2, 400, 246))
    render(os.path.join(IMG, 'sim-seedspace.svg'), W, H, *f,
           title="Збій повністю описується зерном")


if __name__ == "__main__":
    fig_sim_purefunc()
    fig_sim_seedspace()
    fig_control_observe()
    fig_tactics_tree()
    fig_testability_lineage()
    fig_pie_gates()
    fig_drr_funnel()
    fig_state_blowup()
    fig_double_ladder()
    fig_state_vs_interaction()
    fig_seams()
    print("figures written to", IMG)


# ── Вставка math-testability-pie: додано окремим блоком (паралельні агенти) ────
def fig_pie_tests_curve():
    import math
    W, H = 900, 520
    frags = []
    frags.append(text(W / 2, 30,
                      "Скільки тестів треба, щоб зловити дефект із упевненістю C",
                      size=16, bold=True))
    frags.append(text(W / 2, 52,
                      "крива для C = 90%;  n — кількість незалежних тестів",
                      size=12, italic=True, color=MUTED))
    x0, x1 = 120, 830
    y0, y1 = 430, 100
    tmin, tmax, nmax = 0.02, 0.6, 120.0

    def px(t):
        return x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)

    def py(n):
        return y0 + min(n, nmax) / nmax * (y1 - y0)

    frags.append(line(x0, y0, x1, y0, color=INK, sw=1.8))
    frags.append(line(x0, y0, x0, y1, color=INK, sw=1.8))
    for tv in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        xx = px(tv)
        frags.append(line(xx, y0, xx, y0 + 6, color=INK, sw=1.3))
        frags.append(text(xx, y0 + 22, "%.1f" % tv, size=12))
    frags.append(text((x0 + x1) / 2, y0 + 46,
                      "тестовність t  (шанс, що один тест бачить дефект)",
                      size=13, bold=True))
    for nv in [30, 60, 90, 120]:
        yy = py(nv)
        frags.append(line(x0 - 6, yy, x0, yy, color=INK, sw=1.3))
        frags.append(text(x0 - 12, yy + 4, str(nv), size=12, anchor="end"))
    frags.append(text(x0 + 8, y1 - 12, "n", size=14, bold=True, anchor="start"))

    lnC = math.log(1 - 0.9)
    pts = []
    t = tmin
    while t <= tmax + 1e-9:
        pts.append("%.1f,%.1f" % (px(t), py(lnC / math.log(1 - t))))
        t += 0.004
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), NEG))

    for tv, nv, dx, dy, anc in [(0.5, 4, 0, -14, "middle"),
                                (0.22, 10, 12, -10, "start"),
                                (0.1, 22, 14, 2, "start"),
                                (0.05, 45, 14, 2, "start")]:
        frags.append(circle(px(tv), py(nv), 5, fill=BG, stroke=NEG, sw=2.2))
        frags.append(text(px(tv) + dx, py(nv) + dy, "%.2g → %d" % (tv, nv),
                          size=11, color=NEG, anchor=anc))

    b, _, _ = textbox(605, 178,
                      "мала t:  n ≈ 2.3 / t   (C = 90%)\n"
                      "правило трьох:  n ≈ 3 / t   (C = 95%)",
                      size=12.5, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=11)
    frags.append(b)
    render(os.path.join(IMG, 'pie-tests-curve.svg'), W, H, *frags, title=None)


def fig_pie_masking_floor():
    W, H = 940, 530
    frags = []
    frags.append(text(W / 2, 30,
                      "Стискання ковтає щонайменше 1/|R| зіпсованих станів",
                      size=15.5, bold=True))
    base, barmax = 380, 205

    def bars(x_left, ps, col):
        bw, gap = 46, 14
        out = []
        x = x_left
        for p in ps:
            h = p * barmax
            out.append(rect(x, base - h, bw, h, fill="#eaf0fd", stroke=col, sw=1.8))
            out.append(text(x + bw / 2, base - h - 8, "%.2f" % p, size=11, bold=True, color=col))
            x += bw + gap
        return out

    frags.append(text(215, 96, "Рівномірний вихід (|R| = 4)", size=13, bold=True))
    frags += bars(122, [0.25, 0.25, 0.25, 0.25], NEG)
    frags.append(text(700, 96, "Перекошений вихід (|R| = 4)", size=13, bold=True))
    frags += bars(607, [0.70, 0.10, 0.10, 0.10], POS)
    frags.append(line(100, base, 860, base, color=INK, sw=1.5))

    b1, _, _ = textbox(215, 432,
                       "m = Σpₒ² = 0.25 = 1/|R|\n(МІНІМУМ: зіткнень найменше)",
                       size=12, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.6, pad=9)
    frags.append(b1)
    b2, _, _ = textbox(700, 432,
                       "m = 0.49 + 3·0.01 = 0.52 > 0.25\n(перекіс лише ПІДВИЩУЄ маскування)",
                       size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=9)
    frags.append(b2)
    fb, _, _ = textbox(W / 2, 500,
                       "m = Σ pₒ² ≥ 1/|R| = DRR/|D|      ⟹      p_пош ≤ 1 − 1/|R|",
                       size=13.5, bold=True, fill="#fbfbfb", stroke=NEG, sw=1.8, pad=10)
    frags.append(fb)
    render(os.path.join(IMG, 'pie-masking-floor.svg'), W, H, *frags, title=None)


def fig_pie_mutation():
    W, H = 1040, 480
    frags = []
    frags.append(text(W / 2, 30, "Мутаційне тестування міряє множники PIE прямо",
                      size=16, bold=True))
    y = 145
    pipe = [
        (120, "вхід x", "#eef4ff", NEG, 90),
        (340, "мутований\nрядок", "#fdecea", POS, 120),
        (560, "стан\nпісля рядка", "#fbfbfb", INK, 130),
        (740, "…решта\nобчислення…", "#fbfbfb", MUTED, 130),
        (920, "вихід", "#eef4ff", NEG, 90),
    ]
    meta = []
    for cx, s, fill, col, mw in pipe:
        b, w, h = textbox(cx, y, s, size=12.5, bold=True, fill=fill, stroke=col,
                          sw=2, pad=11, min_w=mw)
        meta.append((cx, w, h, b))
    for i in range(len(pipe) - 1):
        x1 = meta[i][0] + meta[i][1] / 2
        x2 = meta[i + 1][0] - meta[i + 1][1] / 2
        frags.append(arrow(x1, y, x2, y, color=MUTED, sw=2.2))
    for cx, w, h, b in meta:
        frags.append(b)

    wprobe, ww, wh = textbox(560, 305,
                             "слабке вбивство\nстан P ≠ стан M ?\nзасвідчує R · I",
                             size=12, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10)
    sprobe, sw2, sh = textbox(920, 305,
                              "сильне вбивство\nвихід P ≠ вихід M ?\nзасвідчує R · I · P",
                              size=12, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10)
    frags.append(arrow(560, 305 - wh / 2, 560, y + meta[2][2] / 2 + 4, color=FIELD, sw=2))
    frags.append(arrow(920, 305 - sh / 2, 920, y + meta[4][2] / 2 + 4, color=FIELD, sw=2))
    frags.append(wprobe)
    frags.append(sprobe)

    eb, _, _ = textbox(W / 2, 430,
                       "частка слабких ≈ p_досяг·p_зар      частка сильних ≈ p_досяг·p_зар·p_пош\n"
                       "⟹   p_пош = (частка сильних) / (частка слабких)",
                       size=12.5, bold=True, fill="#fbfbfb", stroke=NEG, sw=1.8, pad=10)
    frags.append(eb)
    render(os.path.join(IMG, 'pie-mutation.svg'), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_pie_tests_curve()
    fig_pie_masking_floor()
    fig_pie_mutation()
    print("math-testability-pie figures written to", IMG)
