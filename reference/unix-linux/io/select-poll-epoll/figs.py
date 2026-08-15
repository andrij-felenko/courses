# -*- coding: utf-8 -*-
"""Фігури до теми «select, poll, epoll: чекати на багато джерел»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_ways():
    """Хто й коли з'ясовує готовність: обхід на виклику проти доповіді від джерела."""
    W, H = 1000, 470
    g = []

    LX, LW = 24, 452
    RX, RW = 524, 452

    g.append(fitbox(LX, 20, LW, 44,
                    "select і poll: питаємо на кожному виклику",
                    size=14, bold=True, fill="#fdecea", stroke=POS))
    g.append(fitbox(RX, 20, RW, 44,
                    "epoll: джерело доповідає в мить події",
                    size=14, bold=True, fill="#eaf7ee", stroke=FIELD))

    left = [
        "виклик: увесь список дескрипторів\nперетинає межу в ядро",
        "ядро обходить кожен файл зі списку:\nзапис у чергу очікування + поточна маска",
        "задача спить",
        "пробудження від будь-якого одного —\nі ядро обходить увесь список ще раз",
        "увесь список результатів\nперетинає межу назад",
    ]
    right = [
        "epoll_ctl(ADD), одноразово:\nepitem у червоно-чорному дереві",
        "разом із ним — зворотний виклик,\nвставлений у чергу очікування файлу",
        "задача спить",
        "прийшли байти → драйвер будить чергу →\nзворотний виклик кладе epitem\nу список готових",
        "epoll_wait забирає\nсам лише список готових",
    ]

    y = 80
    for i, (a, b) in enumerate(zip(left, right)):
        h = 62 if i != 2 else 44
        fa = "#eef2f7" if i == 2 else FILL
        g.append(fitbox(LX, y, LW, h, a, size=12, fill=fa))
        g.append(fitbox(RX, y, RW, h, b, size=12, fill=fa))
        if i < len(left) - 1:
            g.append(arrow(LX + LW / 2, y + h + 2, LX + LW / 2, y + h + 16,
                           color=MUTED, sw=1.4))
            g.append(arrow(RX + RW / 2, y + h + 2, RX + RW / 2, y + h + 16,
                           color=MUTED, sw=1.4))
        y += h + 18

    g.append(fitbox(LX, y + 6, LW, 48,
                    "робота ядра ∝ довжині списку,\nа не кількості подій",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(RX, y + 6, RW, 48,
                    "робота ядра ∝ кількості подій,\nа не довжині списку",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'two-ways.svg'), W, H, *g,
           title="Два способи дізнатися, які дескриптори готові")


def fig_cost():
    """Що саме різне в трьох інтерфейсах: не швидкість, а те, де живе список."""
    W, H = 1030, 400
    g = []

    C0, W0 = 20, 268
    C1, W1 = 296, 224
    C2, W2 = 526, 224
    C3, W3 = 756, 254

    head = [(C0, W0, ""), (C1, W1, "select"), (C2, W2, "poll"), (C3, W3, "epoll")]
    for x, w, s in head:
        fill = "#eef2f7" if s else BG
        stroke = LINE if s else BG
        g.append(fitbox(x, 22, w, 40, s, size=14, bold=True, fill=fill, stroke=stroke))

    rows = [
        ("що перетинає межу\nза кожен виклик",
         "три бітові маски\nдовжиною nfds бітів",
         "масив із n записів\nпо 8 байтів",
         "тільки готові події"),
        ("стеля кількості\nдескрипторів",
         "FD_SETSIZE = 1024,\nвшито в тип fd_set",
         "межа — RLIMIT_NOFILE\n(більший nfds → EINVAL)",
         "скільки завгодно\n(ліміт max_user_watches)"),
        ("чи перебудовувати\nсписок щоразу",
         "так: маски\nруйнуються на місці",
         "ні: events і revents —\nокремі поля",
         "ні: список живе в ядрі\nміж викликами"),
        ("робота ядра\nза один виклик",
         "O(n) — обхід усіх",
         "O(n) — обхід усіх",
         "O(готових)"),
        ("звідки береться\nготовність",
         "ядро питає кожен файл\nу мить виклику",
         "ядро питає кожен файл\nу мить виклику",
         "файл сам доповів\nу мить події"),
    ]

    y = 70
    for a, b, c, d in rows:
        g.append(fitbox(C0, y, W0, 58, a, size=12, fill="#eef2f7"))
        g.append(fitbox(C1, y, W1, 58, b, size=12, fill="#fdecea"))
        g.append(fitbox(C2, y, W2, 58, c, size=12, fill="#f7f3e8"))
        g.append(fitbox(C3, y, W3, 58, d, size=12, fill="#eaf7ee"))
        y += 66

    render(os.path.join(IMG, 'cost-model.svg'), W, H, *g,
           title="Три інтерфейси очікування на багато джерел")


def fig_level_edge():
    """Чому фронт вимагає вичитувати до EAGAIN, а рівень — ні."""
    W, H = 1060, 340
    g = []

    LBL, LW = 20, 236
    CW, GAP = 148, 12
    X0 = LBL + LW + GAP

    moments = [
        ("прийшло 300 Б", "300", "готовий", "готовий"),
        ("read узяв 100 Б", "200", "готовий", "мовчить"),
        ("прийшло ще 50 Б", "250", "готовий", "готовий"),
        ("read узяв 250 Б", "0", "мовчить", "мовчить"),
        ("прийшло 80 Б", "80", "готовий", "готовий"),
    ]

    g.append(fitbox(LBL, 22, LW, 42, "що сталося", size=13, bold=True, fill="#eef2f7"))
    for i, (m, _, _, _) in enumerate(moments):
        g.append(fitbox(X0 + i * (CW + GAP), 22, CW, 42, m, size=12, fill="#eef2f7"))

    band = [
        ("байтів у буфері прийому", 1, FILL, LINE),
        ("рівень (типово): epoll_wait", 2, "#eaf7ee", FIELD),
        ("фронт (EPOLLET): epoll_wait", 3, "#f7f3e8", MUTED),
    ]
    y = 78
    for label, idx, fill, stroke in band:
        g.append(fitbox(LBL, y, LW, 52, label, size=12, fill=fill, stroke=stroke))
        for i, m in enumerate(moments):
            v = m[idx]
            f = "#fdecea" if v == "мовчить" else fill
            s = POS if v == "мовчить" else stroke
            g.append(fitbox(X0 + i * (CW + GAP), y, CW, 52, v, size=13, fill=f, stroke=s))
        y += 60

    g.append(fitbox(LBL, y + 8, LW + 5 * (CW + GAP) - GAP, 52,
                    "друга колонка й ціна помилки: у режимі фронту недовичитані 200 байтів "
                    "не породять\nнового сповіщення — з'єднання завмре, доки не прийде "
                    "щось іще ззовні",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'level-vs-edge.svg'), W, H, *g,
           title="Рівень і фронт: коли epoll_wait повертає дескриптор")


def fig_scaling_plot():
    """Форма виміряного результату: дві прямі й одна горизонталь у log–log."""
    import math

    W, H = 960, 500
    g = []

    X0, X1 = 148, 686          # межі поля по осі N
    Y0, Y1 = 408, 84           # низ і верх поля по осі часу
    LN0, LN1 = 2.0, 5.0        # log10(N): 100 … 100 000
    LT0, LT1 = -0.301, 3.699   # log10(мкс): 0.5 … 5000

    def px(n):
        return X0 + (math.log10(n) - LN0) / (LN1 - LN0) * (X1 - X0)

    def py(t):
        return Y0 - (math.log10(t) - LT0) / (LT1 - LT0) * (Y0 - Y1)

    # ── сітка й осі ──────────────────────────────────────────────────────
    for n in (100, 1000, 10000, 100000):
        g.append(line(px(n), Y1, px(n), Y0, color="#e2e6ea", sw=1))
        g.append(text(px(n), Y0 + 22, "{:,}".format(n).replace(",", " "),
                      size=12, color=MUTED))
    for t in (1, 10, 100, 1000):
        g.append(line(X0, py(t), X1, py(t), color="#e2e6ea", sw=1))
        g.append(text(X0 - 12, py(t) + 4, "{:,}".format(t).replace(",", " "),
                      size=12, color=MUTED, anchor="end"))

    g.append(line(X0, Y0, X1, Y0, color=LINE, sw=1.6))
    g.append(line(X0, Y0, X0, Y1, color=LINE, sw=1.6))
    g.append(text(X0, Y1 - 22, "час одного очікування, мкс (логарифм)",
                  size=13, color=INK, anchor="start"))
    g.append(text((X0 + X1) / 2, Y0 + 48, "N — скільки дескрипторів у наборі (логарифм)",
                  size=13, color=INK))

    # ── три криві ────────────────────────────────────────────────────────
    poll_pts = [(100, 2.6), (500, 11.0), (1000, 21.5), (10000, 215.0), (100000, 2180.0)]
    sel_pts = [(100, 3.1), (200, 5.2), (500, 12.4)]
    ep_pts = [(100, 0.90), (1000, 0.92), (10000, 0.95), (100000, 1.02)]

    def curve(pts, color):
        for a, b in zip(pts, pts[1:]):
            g.append(line(px(a[0]), py(a[1]), px(b[0]), py(b[1]), color=color, sw=2.6))
        for n, t in pts:
            g.append(circle(px(n), py(t), 4.5, fill=BG, stroke=color, sw=2.2))

    curve(poll_pts, NEG)
    curve(sel_pts, POS)
    curve(ep_pts, FIELD)

    # ── стеля select ─────────────────────────────────────────────────────
    xcut = px(511)
    g.append(line(xcut, Y1 - 4, xcut, Y0 + 6, color=POS, sw=1.6, dash="6 5"))
    g.append(fitbox(xcut + 24, 104, 232, 74,
                    "далі select не йде: у маску\nвлазять лише fd < 1024, а кожна\n"
                    "пара з'їдає два — стеля N ≈ 510",
                    size=12, fill="#fdecea", stroke=POS))

    # ── підпис нахилу в порожній зоні між poll і epoll ───────────────────
    g.append(fitbox(468, 296, 218, 62,
                    "нахил 1: удесятеро більше\nдескрипторів — удесятеро довше",
                    size=12, fill="#eef2f7", stroke=MUTED))

    # ── легенда ──────────────────────────────────────────────────────────
    LX, LW = 716, 226
    g.append(fitbox(LX, 104, LW, 62, "select\nпряма, обірвана стелею",
                    size=12, fill="#fdecea", stroke=POS))
    g.append(fitbox(LX, 182, LW, 62, "poll\nпряма без стелі",
                    size=12, fill="#eaf0fd", stroke=NEG))
    g.append(fitbox(LX, 260, LW, 62, "epoll\nгоризонталь",
                    size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(LX, 338, LW, 74,
                    "абсолютні числа в кожного\nсвої — важить форма\nтрьох ліній",
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'scaling-shape.svg'), W, H, *g,
           title="Форма виміру: час очікування проти числа дескрипторів")


if __name__ == '__main__':
    fig_two_ways()
    fig_cost()
    fig_level_edge()
    fig_scaling_plot()
    print("ok")
