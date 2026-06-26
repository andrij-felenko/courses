# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── one-root: різні назви багів сходяться до одного кореня ─────────────────────
# Ідея: п'ять «знаменитих» вад пам'яті — це не п'ять різних проблем, а одна,
# побачена з різних боків. Усі лінії збігаються в одну рамку-корінь.
def fig_one_root():
    W, H = 720, 380
    p = []
    bugs = [
        "Переповнення\nбуфера",
        "Use-after-free\n(після звільнення)",
        "Висячий\nпокажчик",
        "Витік\nпам'яті",
        "Переповнення\nстека",
    ]
    bx = 40
    bw, bh = 132, 52
    gap = (H - 96 - len(bugs) * bh) / (len(bugs) - 1)
    top = 70
    cy_root = H / 2 + 6
    rootx = W - 250
    # корінь
    root_lines = "ОДИН КОРІНЬ:\nторкаєшся пам'яті,\nякою не володієш —\nабо не в той час"
    rb = fitbox(rootx, cy_root - 62, 230, 124, root_lines, size=15, bold=True,
                fill="#fdecea", stroke=POS, sw=2.4)
    centers = []
    for i, b in enumerate(bugs):
        y = top + i * (bh + gap)
        p.append(fitbox(bx, y, bw, bh, b, size=13, fill=FILL, stroke=LINE))
        centers.append((bx + bw, y + bh / 2))
    # лінії збігаються до лівого краю кореня
    for (sx, sy) in centers:
        p.append(line(sx, sy, rootx - 6, cy_root, color=MUTED, sw=1.6))
    p.append(rb)
    return render(os.path.join(OUT, "one-root.svg"), W, H, *p,
                  title="П'ять назв — одна вада")


# ── three-lines: три лінії оборони пам'яті ────────────────────────────────────
# Ідея: безпека пам'яті будується шарами. Зовнішній — уникнути класу багів
# конструкцією; середній — апаратно/рантайм-вартовий ловить порушення; внутрішній
# — інструменти й тести виявляють рано. Що пройшло крізь усі три — рідкісне.
def fig_three_lines():
    W, H = 720, 470
    p = []
    cx = W / 2
    # три концентричні рамки-бар'єри
    layers = [
        (0,   "1. УНИКНУТИ конструкцією", "статична пам'ять, без malloc,\nперевірка меж, RAII", FIELD, "#eafaf0"),
        (1,   "2. ОХОРОНИТИ в рантаймі",  "MPU, канарки стека,\nbrown-out, watchdog",          NEG,   "#eaf0fd"),
        (2,   "3. СПІЙМАТИ рано",          "санітайзери, статичний аналіз,\nMISRA, тести",       POS,   "#fdecea"),
    ]
    boxw, boxh = 470, 76
    top = 64
    vgap = 36
    for i, (idx, head, sub, col, fill) in enumerate(layers):
        y = top + i * (boxh + vgap)
        p.append(rect(cx - boxw / 2, y, boxw, boxh, fill=fill, stroke=col, sw=2.2, rx=8))
        p.append(text(cx, y + 26, head, size=15, color=col, bold=True))
        p.append(mtext(cx, y + 46, sub, size=12.5, color=INK, lh=1.25))
        if i < len(layers) - 1:
            ay = y + boxh
            p.append(arrow(cx, ay + 4, cx, ay + vgap - 6, color=MUTED, sw=2))
            p.append(text(cx + 150, ay + vgap / 2 + 4, "що прорвалось →", size=11, color=MUTED))
    # хвіст: рідкісний баг, що дійшов до поля
    yb = top + len(layers) * (boxh + vgap)
    p.append(fitbox(cx - 150, yb - 6, 300, 40, "у полі — лише те, що проминуло всі три",
                    size=12, fill="#fff7e6", stroke="#d68910"))
    return render(os.path.join(OUT, "three-lines.svg"), W, H, *p,
                  title="Три лінії оборони пам'яті")


# ── static-vs-heap: статична розкладка проти купи ─────────────────────────────
# Ідея: коли вся пам'ять розподілена на етапі компіляції, цілий клас бід просто
# не може виникнути. Ліворуч — статика (лінкер знає все, помилок-часу-виконання
# нема). Праворуч — купа з її трьома типовими відмовами.
def fig_static_vs_heap():
    W, H = 720, 360
    p = []
    colw = 300
    lx = 50
    rx = W - 50 - colw
    top = 70
    boxh = 210
    # ліво: статика
    p.append(rect(lx, top, colw, boxh, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=8))
    p.append(text(lx + colw / 2, top + 28, "Статична розкладка", size=15, color=FIELD, bold=True))
    p.append(text(lx + colw / 2, top + 50, "лінкер знає все наперед", size=12, color=MUTED, italic=True))
    good = ["+ розмір відомий при збірці",
            "+ не вичерпається у полі",
            "+ нема фрагментації",
            "+ нема use-after-free",
            "+ час доступу сталий"]
    for i, g in enumerate(good):
        p.append(text(lx + 22, top + 86 + i * 24, g, size=12.5, color=INK, anchor="start"))
    # право: купа
    p.append(rect(rx, top, colw, boxh, fill="#fdecea", stroke=POS, sw=2.2, rx=8))
    p.append(text(rx + colw / 2, top + 28, "Купа (malloc/free)", size=15, color=POS, bold=True))
    p.append(text(rx + colw / 2, top + 50, "розмір вирішує рантайм", size=12, color=MUTED, italic=True))
    bad = ["− може повернути NULL",
           "− фрагментація з часом",
           "− подвійне звільнення",
           "− висячі покажчики",
           "− час malloc непевний"]
    for i, b in enumerate(bad):
        p.append(text(rx + 22, top + 86 + i * 24, b, size=12.5, color=INK, anchor="start"))
    # підпис унизу
    p.append(text(W / 2, top + boxh + 36,
                  "Прибрав купу — і цілої правої колонки просто немає",
                  size=13, color=INK, bold=True))
    return render(os.path.join(OUT, "static-vs-heap.svg"), W, H, *p,
                  title="Чому статична пам'ять безпечніша")


# ── awareness-arc: як галузь усвідомлювала проблему (для hist-вставки) ─────────
# Ідея: лінія часу від першого доказу (хробак Морріса, 1988) через дві незалежні
# статистики (Microsoft 2019, Google 2020) до державних рекомендацій (NSA 2022,
# CISA 2023). Видно, що від доказу до дії минуло 30+ років.
def fig_awareness_arc():
    W, H = 760, 430
    p = []
    axis_x = 150
    top = 70
    bot = H - 56
    p.append(line(axis_x, top, axis_x, bot, color=MUTED, sw=2))
    events = [
        ("1988", "Хробак Морріса", "переповнення буфера в fingerd\nспинило ~10% інтернету", POS),
        ("2019", "Microsoft, BlueHat IL", "~70% безпекових латок\nза 12 років — вади пам'яті", NEG),
        ("2020", "Google / Chromium", "~70% серйозних багів з 912;\nполовина — use-after-free", NEG),
        ("2022", "NSA: інформ-лист", "радить переходити на\nmemory-safe мови", FIELD),
        ("2023", "CISA + союзники", "вимагають «дорожні карти»\nбезпечної пам'яті", FIELD),
    ]
    n = len(events)
    step = (bot - top) / (n - 1)
    bx = axis_x + 34
    bw = 470
    for i, (yr, head, sub, col) in enumerate(events):
        y = top + i * step
        p.append(circle(axis_x, y, 7, fill="#fff", stroke=col, sw=2.6))
        p.append(text(axis_x - 16, y + 5, yr, size=14, color=col, bold=True, anchor="end"))
        bh = 56
        p.append(rect(bx, y - bh / 2, bw, bh, fill=FILL, stroke=col, sw=1.8, rx=7))
        p.append(text(bx + 14, y - bh / 2 + 21, head, size=13.5, color=col, bold=True, anchor="start"))
        p.append(mtext(bx + 14, y - bh / 2 + 38, sub, size=11.5, color=INK, anchor="start", lh=1.2))
        p.append(line(axis_x + 7, y, bx, y, color=MUTED, sw=1.4))
    # підпис унизу: розрив у часі
    p.append(text(W / 2, bot + 34,
                  "Від першого доказу до державної дії — понад 30 років",
                  size=12.5, color=INK, italic=True))
    return render(os.path.join(OUT, "awareness-arc.svg"), W, H, *p,
                  title="Як галузь усвідомлювала проблему пам'яті")


# ── free-list: вільний список, прокладений у самих блоках (proj-вставка) ───────
# Ідея: масив однакових блоків. Зайняті тримають дані; вільні переосмислюють свої
# перші байти як покажчик next на наступний вільний. free_list — голова ланцюжка,
# останній вільний → NULL. Окремого сховища під облік немає.
def fig_free_list():
    W, H = 720, 360
    p = []
    n = 6
    bw, bh = 88, 80
    gap = 14
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = 150
    # котрі блоки зайняті (True) / вільні (False)
    busy = [True, False, True, False, False, True]
    cx = []
    for i in range(n):
        x = x0 + i * (bw + gap)
        cx.append(x + bw / 2)
        if busy[i]:
            p.append(rect(x, y, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2))
            p.append(mtext(x + bw / 2, y + bh / 2 - 4, "дані\nкористувача",
                           size=12, color=INK, lh=1.25))
        else:
            p.append(rect(x, y, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2))
            p.append(text(x + bw / 2, y + bh / 2 + 4, "next →", size=13,
                          color=NEG, bold=True))
        p.append(text(x + bw / 2, y + bh + 18, "блок %d" % i, size=11, color=MUTED))
    # голова списку
    p.append(text(x0, y - 40, "free_list", size=14, color=NEG, bold=True, anchor="start"))
    free_idx = [i for i in range(n) if not busy[i]]
    # стрілка від free_list до першого вільного
    fx = cx[free_idx[0]]
    p.append(arrow(x0 + 24, y - 34, fx, y - 6, color=NEG, sw=2))
    # дуги-стрілки між вільними блоками (next), над блоками
    for a, b in zip(free_idx, free_idx[1:]):
        p.append(arrow(cx[a], y - 6, cx[b], y - 6, color=NEG, sw=1.8))
    # останній вільний → NULL
    last = cx[free_idx[-1]]
    p.append(arrow(last, y + bh + 4, last, y + bh + 40, color=NEG, sw=1.8))
    p.append(text(last, y + bh + 54, "NULL", size=12, color=MUTED, bold=True))
    # підпис-висновок
    p.append(text(W / 2, H - 16,
                  "вузол списку й корисний блок — та сама пам'ять, по черзі в двох ролях",
                  size=12.5, color=INK, italic=True))
    return render(os.path.join(OUT, "free-list.svg"), W, H, *p,
                  title="Вільний список живе в самих блоках")


# ── pool-vs-malloc: пул фіксованих блоків проти malloc/free ───────────────────
# Ідея: пул купує детермінованість ціною єдиного розміру блоку. Ліворуч — malloc
# з його трьома вадами; праворуч — пул з трьома виграшами. Внизу — ціна пулу.
def fig_pool_vs_malloc():
    W, H = 720, 360
    p = []
    colw = 300
    lx = 50
    rx = W - 50 - colw
    top = 66
    boxh = 196
    # ліво: malloc/free
    p.append(rect(lx, top, colw, boxh, fill="#fdecea", stroke=POS, sw=2.2, rx=8))
    p.append(text(lx + colw / 2, top + 28, "malloc / free", size=15, color=POS, bold=True))
    p.append(text(lx + colw / 2, top + 50, "будь-який розмір — але…", size=12,
                  color=MUTED, italic=True))
    bad = ["− час пошуку непевний",
           "− фрагментація з часом",
           "− пік невідомий наперед"]
    for i, b in enumerate(bad):
        p.append(text(lx + 22, top + 92 + i * 30, b, size=13, color=INK, anchor="start"))
    # право: пул
    p.append(rect(rx, top, colw, boxh, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=8))
    p.append(text(rx + colw / 2, top + 28, "Пул фіксованих блоків", size=15,
                  color=FIELD, bold=True))
    p.append(text(rx + colw / 2, top + 50, "єдиний розмір — зате…", size=12,
                  color=MUTED, italic=True))
    good = ["+ час сталий (3 присвоєння)",
            "+ нуль фрагментації",
            "+ пік відомий лінкеру"]
    for i, g in enumerate(good):
        p.append(text(rx + 22, top + 92 + i * 30, g, size=13, color=INK, anchor="start"))
    # ціна пулу — внизу через усю ширину
    p.append(fitbox(W / 2 - 250, top + boxh + 18, 500, 40,
                    "Ціна детермінованості — усі блоки одного розміру",
                    size=13, bold=True, fill="#fff7e6", stroke="#d68910"))
    return render(os.path.join(OUT, "pool-vs-malloc.svg"), W, H, *p,
                  title="Детермінованість ціною єдиного розміру")


if __name__ == "__main__":
    fig_one_root()
    fig_three_lines()
    fig_static_vs_heap()
    fig_awareness_arc()
    fig_free_list()
    fig_pool_vs_malloc()
    print("OK: one-root, three-lines, static-vs-heap, awareness-arc, free-list, pool-vs-malloc")
