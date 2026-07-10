# -*- coding: utf-8 -*-
"""Фігури до статті «В'ю розгортання і динамічні в'ю»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ══ Фігури для вставки «Розгортання як код» ══════════════════════════════════

# ── Фігура P1: один маніфест — кілька читачів того самого тексту ─────────────
def fig_iac_one_source():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 30, "Один маніфест — кілька читачів того самого тексту",
                  size=15, bold=True, color=MUTED))
    p.append(text(W / 2, 52, "той самий опис піднімає інфраструктуру, малює діаграму й проходить лінтер",
                  size=12, italic=True, color=MUTED))

    # джерело — маніфест
    p.append(fitbox(48, 178, 180, 78, "prod.yaml\n(маніфест топології)",
                    size=13, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(text(138, 274, "єдине джерело істини", size=11, italic=True, color=MUTED))

    # три читачі — дієслово вже в рамці, тож стрілки без написів
    p.append(fitbox(470, 78, 278, 72, "kubectl apply →\nжива інфраструктура",
                    size=13, bold=True, fill="#f7fdf9", stroke=FIELD))
    p.append(fitbox(470, 186, 278, 72, "рендер →\nдіаграма розгортання",
                    size=13, bold=True, fill="#fff6e6", stroke="#b8860b"))
    p.append(fitbox(470, 294, 278, 72, "аналізатор →\nвердикт у CI",
                    size=13, bold=True, fill="#fdecea", stroke=POS))

    sx, sy = 228, 217
    p.append(arrow(sx, sy, 466, 114, color=INK, sw=1.8))
    p.append(arrow(sx, sy, 466, 222, color=INK, sw=1.8))
    p.append(arrow(sx, sy, 466, 330, color=INK, sw=1.8))

    render(os.path.join(IMG, 'iac-one-source.svg'), W, H, *p)


# ── Фігура P2: однозонна надлишковість проти рознесення по зонах ─────────────
def fig_single_zone_trap():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 30, "Що позначає аналізатор: однозонна надлишковість проти рознесення",
                  size=14, bold=True, color=MUTED))

    # ліва панель: worker — 3 копії в ОДНІЙ зоні (антипатерн)
    p.append(fitbox(36, 58, 330, 40, "worker — копій: 3, зон: 1",
                    size=13, bold=True, fill="#fdecea", stroke=POS))
    p.append(rect(56, 116, 290, 120, fill="#f7fdf9", stroke=FIELD, sw=1.4))
    p.append(text(70, 138, "зона eu-central-1a", size=12, bold=True, color=FIELD, anchor="start"))
    for cx in (110, 201, 292):
        p.append(rect(cx - 34, 158, 68, 56, fill="#eef2ff", stroke=NEG, sw=1.3))
        p.append(text(cx, 190, "worker", size=11, bold=True, color=NEG))
    p.append(text(201, 264, "зона падає → усі 3 мертві", size=12, bold=True, color=POS))
    p.append(fitbox(149, 284, 104, 36, "FAIL", size=15, bold=True,
                    fill=POS, stroke=POS, color="#ffffff"))

    # права панель: api — 2+2 у ДВОХ зонах (правильно)
    p.append(fitbox(414, 58, 330, 40, "api — копій: 4, зон: 2",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD))
    for zx, zlab in ((430, "eu-central-1a"), (596, "eu-central-1b")):
        p.append(rect(zx, 116, 148, 120, fill="#f7fdf9", stroke=FIELD, sw=1.4))
        p.append(text(zx + 74, 138, "зона " + zlab, size=11, bold=True, color=FIELD))
        for cx in (zx + 40, zx + 108):
            p.append(rect(cx - 30, 158, 60, 56, fill="#eef2ff", stroke=NEG, sw=1.3))
            p.append(text(cx, 190, "api", size=11, bold=True, color=NEG))
    p.append(text(586, 264, "зона A падає → 2 живі в зоні B", size=12, bold=True, color=FIELD))
    p.append(fitbox(534, 284, 104, 36, "OK", size=15, bold=True,
                    fill=FIELD, stroke=FIELD, color="#ffffff"))

    render(os.path.join(IMG, 'single-zone-trap.svg'), W, H, *p)


# ── Фігура 1: те саме логічне → на реальному залізі ─────────────────────────
def fig_static_to_deploy():
    W, H = 760, 470
    p = []
    # ліворуч: статичний контейнер (один прямокутник)
    p.append(text(180, 62, "Що в статичному в'ю", size=15, bold=True, color=MUTED))
    p.append(fitbox(95, 90, 170, 78, "API\n(один контейнер)",
                    size=14, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(fitbox(95, 210, 170, 78, "База даних\n(один контейнер)",
                    size=14, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(arrow(180, 168, 180, 210, color=NEG))

    # стрілка-перехід
    p.append(text(380, 150, "розгортання", size=13, italic=True, color=MUTED))
    p.append(arrow(300, 165, 460, 165, color=INK, sw=2.2))

    # праворуч: інфраструктура
    p.append(text(590, 62, "Що у в'ю розгортання", size=15, bold=True, color=MUTED))
    # рамка «дата-центр» велика
    p.append(rect(470, 78, 270, 372, fill="#f7fdf9", stroke=FIELD, sw=1.6))
    p.append(text(605, 98, "Дата-центр (prod)", size=13, bold=True, color=FIELD))

    # балансувальник
    p.append(fitbox(520, 112, 170, 44, "Балансувальник",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))
    # три вузли з інстансами API
    xs = [485, 570, 655]
    for i, x in enumerate(xs):
        p.append(rect(x - 5, 176, 78, 66, fill="#eef7f0", stroke=FIELD, sw=1.3))
        p.append(text(x + 34, 194, "вузол", size=10, color=FIELD))
        p.append(fitbox(x, 200, 68, 34, "API",
                        size=11, bold=True, fill="#eef2ff", stroke=NEG))
        p.append(arrow(605, 156, x + 34, 176, color="#b8860b", sw=1.3))
    # база — одна репліка окремо
    p.append(rect(560, 300, 96, 66, fill="#eef7f0", stroke=FIELD, sw=1.3))
    p.append(text(608, 318, "вузол", size=10, color=FIELD))
    p.append(fitbox(566, 324, 84, 34, "БД",
                    size=11, bold=True, fill="#eef2ff", stroke=NEG))
    for x in xs:
        p.append(line(x + 34, 242, 608, 300, color=MUTED, sw=1.0, dash="4 3"))
    p.append(text(605, 392, "три копії API за одним", size=11, color=INK))
    p.append(text(605, 408, "балансувальником — одна", size=11, color=INK))
    p.append(text(605, 424, "«коробка» стала трьома", size=11, color=INK))

    render(os.path.join(IMG, 'static-to-deploy.svg'), W, H, *p)


# ── Фігура 2: статичний бік проти динамічного (нумеровані взаємодії) ─────────
def fig_static_vs_dynamic():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 30, "Ті самі контейнери — але показано ПОРЯДОК викликів",
                  size=14, bold=True, color=MUTED))
    # чотири вузли рядком, з великими проміжками
    BW, BH, BY = 140, 58, 130
    xs = {"web": 30, "api": 220, "auth": 410, "db": 600}
    labels = {"web": "Веб-\nзастосунок", "api": "API",
              "auth": "Сервіс\nавторизації", "db": "База даних"}
    cx = {k: xs[k] + BW / 2 for k in xs}
    top, bot = BY, BY + BH
    for k in xs:
        p.append(fitbox(xs[k], BY, BW, BH, labels[k], size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))

    def numbadge(mx, my, n):
        return (circle(mx, my, 12, fill="#fdecea", stroke=POS, sw=1.6) +
                text(mx, my + 4, n, size=12, bold=True, color=POS))

    # прямі виклики над рамками зліва направо — стрілки НАД коробками, підписи вище
    def top_arrow(a, b, n, up=42):
        y = BY - up
        p.append(line(cx[a], top, cx[a], y, color=POS, sw=1.6))
        p.append(arrow(cx[a], y, cx[b], y, color=POS, sw=1.8))
        p.append(line(cx[b], y, cx[b], top, color=POS, sw=1.6))
        p.append(numbadge((cx[a] + cx[b]) / 2, y, n))

    # виклики під рамками справа наліво — стрілки ПІД коробками
    def bot_arrow(a, b, n, down=42):
        y = bot + down
        p.append(line(cx[a], bot, cx[a], y, color=POS, sw=1.6))
        p.append(arrow(cx[a], y, cx[b], y, color=POS, sw=1.8))
        p.append(line(cx[b], y, cx[b], bot, color=POS, sw=1.6))
        p.append(numbadge((cx[a] + cx[b]) / 2, y, n))

    top_arrow("web", "api", "1", up=42)      # запит логіну
    top_arrow("api", "auth", "2", up=78)     # перевірка (вище, щоб не збігтися з 1)
    top_arrow("auth", "db", "3", up=42)      # читання
    bot_arrow("api", "web", "4", down=44)    # відповідь назад

    p.append(text(W / 2, 322,
                  "1 запит логіну   2 перевірка облікових даних   "
                  "3 читання з бази   4 відповідь користувачу",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'static-vs-dynamic.svg'), W, H, *p)


# ── Фігура 3: де стоять ці два в'ю серед решти ──────────────────────────────
def fig_view_map():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 34, "Статична будова — окремо, поведінка й залізо — окремо",
                  size=14, bold=True, color=MUTED))

    # ліва колона — статичні рівні (стос)
    p.append(rect(70, 70, 250, 230, fill="#f7fdf9", stroke=FIELD, sw=1.4))
    p.append(text(195, 92, "Статичні рівні (з чого)", size=12, bold=True, color=FIELD))
    labels = ["Контекст", "Контейнери", "Компоненти", "Код"]
    for i, lb in enumerate(labels):
        y = 108 + i * 46
        p.append(fitbox(100, y, 190, 36, lb, size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))

    # права зона — два доповняльні в'ю
    p.append(text(535, 92, "Доповняльні в'ю", size=12, bold=True, color="#b8860b"))
    p.append(fitbox(430, 112, 210, 66,
                    "Динамічний в'ю\n(як працює в часі)",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))
    p.append(fitbox(430, 208, 210, 66,
                    "В'ю розгортання\n(на яке залізо лягає)",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))

    # зв'язки: обидва спираються на «контейнери»
    p.append(arrow(290, 154, 430, 145, color=MUTED, sw=1.4))
    p.append(arrow(290, 154, 430, 241, color=MUTED, sw=1.4))
    p.append(text(360, 128, "ті самі", size=10, italic=True, color=MUTED))
    p.append(text(360, 143, "контейнери", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG, 'view-map.svg'), W, H, *p)


# ── Помічники для детальної статті: пунктирна стрілка (повернення UML) ───────
def _dhead(x, y, dirn, color=MUTED, s=8):
    if dirn == 'l':
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x, y, x + s, y - s * 0.55, x + s, y + s * 0.55)
    elif dirn == 'r':
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x, y, x - s, y - s * 0.55, x - s, y + s * 0.55)
    elif dirn == 'u':
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x, y, x - s * 0.55, y + s, x + s * 0.55, y + s)
    else:
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x, y, x - s * 0.55, y - s, x + s * 0.55, y - s)
    return '<polygon points="%s" fill="%s"/>' % (pts, color)


def _darrow(x1, y1, x2, y2, color=MUTED, sw=1.5):
    seg = line(x1, y1, x2, y2, color=color, sw=sw, dash="6 4")
    if abs(y1 - y2) < 0.5:
        d = 'l' if x2 < x1 else 'r'
    else:
        d = 'u' if y2 < y1 else 'd'
    return seg + _dhead(x2, y2, d, color)


# ── Фігура D1: анатомія діаграми послідовності ──────────────────────────────
def fig_seq_anatomy():
    W, H = 720, 470
    p = []
    p.append(text(W / 2, 28, "Діаграма послідовності: лінії життя, смуги активності, виклики й повернення",
                  size=13, bold=True, color=MUTED))

    xs = {"web": 150, "api": 385, "svc": 600}
    heads = {"web": "Веб", "api": "API", "svc": "Сервіс\nавторизації"}
    for k, x in xs.items():
        p.append(fitbox(x - 62, 46, 124, 44, heads[k], size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))
        p.append(line(x, 90, x, 432, color=MUTED, sw=1.0, dash="4 4"))

    # вісь часу ліворуч
    p.append(text(44, 104, "час", size=11, italic=True, color=MUTED))
    p.append(_darrow(44, 116, 44, 408, color=MUTED, sw=1.4))

    # смуги активності (учасник зайнятий)
    p.append(rect(xs["api"] - 6, 150, 12, 214, fill="#fff2df", stroke="#b8860b", sw=1.1, rx=2))
    p.append(rect(xs["svc"] - 6, 214, 12, 84, fill="#fff2df", stroke="#b8860b", sw=1.1, rx=2))

    # 1: синхронний виклик web → api
    p.append(arrow(xs["web"], 150, xs["api"] - 6, 150, color=INK, sw=1.8))
    p.append(text((xs["web"] + xs["api"]) / 2, 142, "1: login()", size=12, color=INK))
    # 2: синхронний виклик api → svc
    p.append(arrow(xs["api"] + 6, 214, xs["svc"] - 6, 214, color=INK, sw=1.8))
    p.append(text((xs["api"] + xs["svc"]) / 2, 206, "2: перевірити()", size=12, color=INK))
    # повернення svc → api
    p.append(_darrow(xs["svc"] - 6, 298, xs["api"] + 6, 298, color=MUTED, sw=1.5))
    p.append(text((xs["api"] + xs["svc"]) / 2, 290, "дані", size=11, italic=True, color=MUTED))
    # повернення api → web
    p.append(_darrow(xs["api"] - 6, 364, xs["web"], 364, color=MUTED, sw=1.5))
    p.append(text((xs["web"] + xs["api"]) / 2, 356, "ok / токен", size=11, italic=True, color=MUTED))

    # легенда — три елементи в ряд, із запасом
    ly = 424
    p.append(arrow(64, ly, 104, ly, color=INK, sw=1.8))
    p.append(text(110, ly + 4, "синхронний виклик (той, хто кличе, чекає)", size=11,
                  color=INK, anchor="start"))
    p.append(rect(64, 440, 12, 16, fill="#fff2df", stroke="#b8860b", sw=1.1, rx=2))
    p.append(text(84, 452, "смуга активності — учасник зайнятий", size=11,
                  color=INK, anchor="start"))
    p.append(_darrow(430, 440 + 8, 470, 440 + 8, color=MUTED, sw=1.5))
    p.append(text(476, 452, "пунктир — повернення", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'seq-anatomy.svg'), W, H, *p)


# ── Фігура D2: комбінований фрагмент (alt / par) ────────────────────────────
def fig_combined_fragments():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 28, "Комбінований фрагмент: гілки й паралелізм усередині ОДНІЄЇ взаємодії",
                  size=13, bold=True, color=MUTED))

    def frame(x, y, w, h, tag, tagcolor):
        f = [rect(x, y, w, h, fill="#fbfcff", stroke=INK, sw=1.6)]
        f.append(rect(x, y, 56, 26, fill=tagcolor, stroke=INK, sw=1.2, rx=3))
        f.append(text(x + 28, y + 18, tag, size=13, bold=True, color="#ffffff"))
        return f

    # alt — вибір
    ax, ay, aw, ah = 40, 60, 320, 300
    p += frame(ax, ay, aw, ah, "alt", "#2457d6")
    p.append(text(ax + 14, ay + 62, "[облікові дані вірні]", size=12, color=POS, anchor="start"))
    p.append(arrow(ax + 28, ay + 96, ax + aw - 24, ay + 96, color=INK, sw=1.7))
    p.append(text(ax + aw / 2, ay + 88, "200 + токен", size=12, color=INK))
    p.append(line(ax, ay + 150, ax + aw, ay + 150, color=MUTED, sw=1.2, dash="7 5"))
    p.append(text(ax + 14, ay + 190, "[інакше]", size=12, color=POS, anchor="start"))
    p.append(arrow(ax + 28, ay + 224, ax + aw - 24, ay + 224, color=INK, sw=1.7))
    p.append(text(ax + aw / 2, ay + 216, "401 відмова", size=12, color=INK))
    p.append(text(ax + aw / 2, ay + ah + 28, "вибір: рівно одна гілка", size=11,
                  italic=True, color=MUTED))

    # par — паралельно
    bx, by, bw, bh = 420, 60, 300, 300
    p += frame(bx, by, bw, bh, "par", "#27ae60")
    p.append(arrow(bx + 28, by + 96, bx + bw - 24, by + 96, color=INK, sw=1.7))
    p.append(text(bx + bw / 2, by + 88, "виклик сервісу A", size=12, color=INK))
    p.append(line(bx, by + 150, bx + bw, by + 150, color=MUTED, sw=1.2, dash="7 5"))
    p.append(arrow(bx + 28, by + 224, bx + bw - 24, by + 224, color=INK, sw=1.7))
    p.append(text(bx + bw / 2, by + 216, "виклик сервісу B", size=12, color=INK))
    p.append(text(bx + bw / 2, by + bh + 28, "разом — потім чекаємо на всіх", size=11,
                  italic=True, color=MUTED))

    render(os.path.join(IMG, 'combined-fragments.svg'), W, H, *p)


# ── Фігура D3: вкладені вузли розгортання ───────────────────────────────────
def fig_node_nesting():
    W, H = 730, 470
    p = []
    p.append(text(W / 2, 26, "Вузли розгортання вкладаються одне в одне — «де саме живе копія»",
                  size=13, bold=True, color=MUTED))

    p.append(rect(30, 46, 670, 400, fill="#f7fdf9", stroke=FIELD, sw=1.6))
    p.append(text(45, 70, "Регіон eu-central-1  ·  зовнішній вузол", size=12, bold=True,
                  color=FIELD, anchor="start"))

    # Зона A — глибокий стос
    p.append(rect(52, 86, 386, 344, fill="#eef7f0", stroke=FIELD, sw=1.3))
    p.append(text(66, 108, "Зона доступності A", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(rect(74, 124, 342, 290, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    p.append(text(88, 146, "Хост (bare-metal або VM)", size=11, bold=True, color=INK, anchor="start"))
    p.append(rect(96, 162, 298, 234, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(110, 184, "Рушій контейнерів (Docker)", size=11, bold=True, color=INK, anchor="start"))
    p.append(rect(118, 200, 254, 178, fill="#eef2ff", stroke=NEG, sw=1.2))
    p.append(text(132, 222, "Контейнер", size=11, bold=True, color=NEG, anchor="start"))
    p.append(rect(140, 238, 210, 122, fill="#e9f1ff", stroke=NEG, sw=1.2))
    p.append(text(245, 262, "процес: копія «api»", size=12, bold=True, color=INK))
    p.append(rect(160, 286, 170, 52, fill="#fff6e6", stroke="#b8860b", sw=1.2))
    p.append(text(245, 308, "артефакт", size=11, color="#8a6d0b"))
    p.append(text(245, 326, "api.bin (те, що розгорнуто)", size=10, color="#8a6d0b"))

    # Зона B — сестра
    p.append(rect(452, 86, 232, 344, fill="#eef7f0", stroke=FIELD, sw=1.3, ))
    p.append(text(466, 108, "Зона доступності B", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(rect(474, 150, 188, 240, fill="#f4f6f8", stroke=MUTED, sw=1.2, ))
    p.append(text(568, 250, "…той самий стос:", size=12, color=MUTED))
    p.append(text(568, 274, "друга копія «api»", size=12, bold=True, color=INK))
    p.append(text(568, 298, "на власному хості", size=12, color=MUTED))

    render(os.path.join(IMG, 'node-nesting.svg'), W, H, *p)


# ── Фігура D4: топологія задає доступність (послідовно / паралельно) ─────────
def fig_availability_topology():
    W, H = 740, 440
    p = []
    p.append(text(W / 2, 28, "Топологія розгортання диктує доступність системи",
                  size=14, bold=True, color=MUTED))

    # послідовно
    p.append(text(40, 72, "Послідовно — на критичному шляху мусить жити КОЖНА ланка:",
                  size=12, bold=True, color=INK, anchor="start"))
    xs = [56, 176, 296, 416, 536]
    for i, x in enumerate(xs, 1):
        p.append(fitbox(x, 88, 92, 46, "сервіс %d" % i, size=11, bold=True,
                        fill="#eef2ff", stroke=NEG))
        if i < 5:
            p.append(arrow(x + 92, 111, x + 120, 111, color=INK, sw=1.7))
    p.append(text(376, 168, "A = a·a·a·a·a = a⁵ = 0.99⁵ ≈ 0.951", size=13, color=INK))
    p.append(text(376, 190, "нижче за будь-яку окрему ланку — послідовність відбирає доступність",
                  size=11, italic=True, color=POS))

    # паралельно
    p.append(text(40, 244, "Паралельно — досить, щоб жила ХОЧ ОДНА копія:",
                  size=12, bold=True, color=INK, anchor="start"))
    for j, y in enumerate([262, 306, 350]):
        p.append(fitbox(70, y, 128, 34, "копія «api»", size=11, bold=True,
                        fill="#eef2ff", stroke=NEG))
        p.append(arrow(198, y + 17, 250, 306 + 17, color=INK, sw=1.4))
    p.append(fitbox(250, 306, 118, 34, "балансувальник", size=11, bold=True,
                    fill="#fff6e6", stroke="#b8860b"))
    p.append(text(470, 300, "A = 1 − (1−a)³ = 1 − 0.01³", size=13, color=INK, anchor="start"))
    p.append(text(470, 322, "≈ 0.999999 — надлишковість підіймає доступність",
                  size=11, italic=True, color=FIELD, anchor="start"))
    p.append(text(470, 352, "(за умови НЕЗАЛЕЖНИХ відмов копій)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'availability-topology.svg'), W, H, *p)


# ── Фігура D5: розгалуження підсилює хвіст затримки ──────────────────────────
def fig_tail_amplification():
    W, H = 720, 440
    p = []
    p.append(text(W / 2, 28, "Віяловий запит підсилює хвіст: P(зачепили повільний листок) = 1 − (1−p)ᴺ",
                  size=13, bold=True, color=MUTED))

    ox, oy = 92, 366          # початок осей
    ex, ty = 664, 78          # кінець осі X, верх осі Y
    def X(n): return ox + (ex - ox) * n / 100.0
    def Y(v): return oy - (oy - ty) * v

    # сітка й підписи Y
    for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
        yy = Y(v)
        p.append(line(ox, yy, ex, yy, color="#e5e7eb", sw=1.0))
        p.append(text(ox - 12, yy + 4, ("%.2f" % v).rstrip('0').rstrip('.') or "0",
                      size=11, color=MUTED, anchor="end"))
    # осі
    p.append(line(ox, ty, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ex, oy, color=INK, sw=1.6))
    for n in [0, 25, 50, 75, 100]:
        p.append(text(X(n), oy + 20, str(n), size=11, color=MUTED))
    p.append(text((ox + ex) / 2, oy + 42, "N — скільки листків опитуємо паралельно",
                  size=12, color=INK))

    # крива 1 − 0.99^N
    pts = []
    n = 0
    while n <= 100:
        pts.append("%.1f,%.1f" % (X(n), Y(1 - 0.99 ** n)))
        n += 2
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), POS))

    # ключова точка N=100
    xk, yk = X(100), Y(1 - 0.99 ** 100)
    p.append(line(ox, yk, xk, yk, color=POS, sw=1.0, dash="5 4"))
    p.append(circle(xk, yk, 5, fill=POS, stroke=POS, sw=1))
    p.append(text(xk - 10, yk - 14, "N=100 → 63%", size=12, bold=True, color=POS, anchor="end"))
    # контраст N=1
    p.append(circle(X(1), Y(0.01), 4, fill=NEG, stroke=NEG, sw=1))
    p.append(text(X(1) + 12, Y(0.01) - 8, "N=1 → 1%", size=11, color=NEG, anchor="start"))

    render(os.path.join(IMG, 'tail-amplification.svg'), W, H, *p)


# ══ Фігури для вставки «Математика доступності» ══════════════════════════════
import math


# ── Фігура M1: стеля кореляції — дев'ятки vs N, незалежні проти спільної зони ─
def fig_corr_floor():
    W, H = 720, 460
    p = []
    p.append(text(W / 2, 26, "Копії в ОДНІЙ зоні впираються в стелю β·u; у різних зонах — ні",
                  size=13, bold=True, color=MUTED))
    ox, ex, oy, ty = 92, 560, 392, 70

    def X(n): return ox + (ex - ox) * (n - 1) / 4.0
    def Y(v): return oy - (oy - ty) * v / 10.0

    for v in [0, 2, 4, 6, 8, 10]:
        yy = Y(v)
        p.append(line(ox, yy, ex, yy, color="#e5e7eb", sw=1.0))
        p.append(text(ox - 12, yy + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 26, ty - 20, "↑ дев'ятки доступності (−log₁₀ U)", size=11,
                  color=MUTED, anchor="start"))
    p.append(line(ox, ty, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ex, oy, color=INK, sw=1.6))
    for n in [1, 2, 3, 4, 5]:
        p.append(text(X(n), oy + 20, str(n), size=11, color=MUTED))
    p.append(text((ox + ex) / 2, oy + 42, "N — скільки надлишкових копій", size=12, color=INK))

    # незалежні (різні зони): nines = 2N  (бо u = 0.01 ⇒ uᴺ = 10^(−2N))
    ind = [(X(n), Y(2 * n)) for n in range(1, 6)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % pt for pt in ind), NEG))
    for pt in ind:
        p.append(circle(pt[0], pt[1], 4, fill=NEG, stroke=NEG, sw=1))

    # спільна зона (β-модель): U = β·u + ((1−β)·u)^N
    def nines_cm(N):
        U = 0.05 * 0.01 + (0.95 * 0.01) ** N
        return -math.log10(U)
    cm = [(X(n), Y(nines_cm(n))) for n in range(1, 6)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % pt for pt in cm), POS))
    for pt in cm:
        p.append(circle(pt[0], pt[1], 4, fill=POS, stroke=POS, sw=1))

    yf = Y(nines_cm(5))
    p.append(line(ox, yf, ex, yf, color=POS, sw=1.0, dash="5 4"))

    p.append(text(X(1.35), Y(9.4), "незалежні копії (різні зони):", size=11, color=NEG, anchor="start"))
    p.append(text(X(1.35), Y(8.8), "+2 дев'ятки на кожну копію", size=11, color=NEG, anchor="start"))
    p.append(text(X(2.3), Y(1.5), "одна зона (β = 0.05):", size=11, color=POS, anchor="start"))
    p.append(text(X(2.3), Y(0.9), "стеля ≈ 3.3 дев'ятки — далі копії марні", size=11, color=POS, anchor="start"))

    render(os.path.join(IMG, 'math-corr-floor.svg'), W, H, *p)


# ── Фігура M2: спектр «k з n» — від паралелі (k=1) до послідовності (k=n) ─────
def fig_k_of_n():
    W, H = 720, 460
    p = []
    p.append(text(W / 2, 26, "n = 5 копій, доступність за різних порогів «k з 5»",
                  size=14, bold=True, color=MUTED))
    ox, by, ty = 92, 350, 70

    def Y(v): return by - (by - ty) * v / 10.0

    for v in [0, 2, 4, 6, 8, 10]:
        yy = Y(v)
        p.append(line(ox, yy, 660, yy, color="#eef0f2", sw=1.0))
        p.append(text(ox - 12, yy + 4, str(v), size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 26, ty - 18, "↑ дев'ятки доступності", size=11, color=MUTED, anchor="start"))
    p.append(line(ox, ty, ox, by, color=INK, sw=1.6))
    p.append(line(ox, by, 660, by, color=INK, sw=1.6))

    nines = {1: 10.0, 2: 7.30, 3: 5.01, 4: 3.01, 5: 1.31}
    fills = {1: ("#eef7f0", FIELD), 2: ("#eef2ff", NEG), 3: ("#fff6e6", "#b8860b"),
             4: ("#eef2ff", NEG), 5: ("#fdecea", POS)}
    cx = {1: 150, 2: 262, 3: 374, 4: 486, 5: 598}
    for k in range(1, 6):
        v = nines[k]
        top = Y(v)
        f, s = fills[k]
        p.append(rect(cx[k] - 36, top, 72, by - top, fill=f, stroke=s, sw=1.4))
        p.append(text(cx[k], top - 8, ("%.1f" % v).rstrip('0').rstrip('.'), size=12, bold=True, color=INK))
        p.append(text(cx[k], by + 20, "k=%d" % k, size=12, bold=True, color=INK))

    p.append(text(cx[1], by + 40, "паралель", size=11, color=FIELD))
    p.append(text(cx[1], by + 56, "(будь-яка 1)", size=11, color=FIELD))
    p.append(text(cx[3], by + 40, "більшість", size=11, color="#b8860b"))
    p.append(text(cx[3], by + 56, "2f+1, f=2", size=11, color="#b8860b"))
    p.append(text(cx[5], by + 40, "послідовно", size=11, color=POS))
    p.append(text(cx[5], by + 56, "(усі 5)", size=11, color=POS))
    p.append(text(W / 2, 442, "поріг k росте — доступність падає; більшість (2f+1) — компроміс заради узгодженості",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'math-k-of-n.svg'), W, H, *p)


# ── Фігура M3: надлишок місткості N+k залежно від числа зон ──────────────────
def fig_zone_overhead():
    W, H = 680, 400
    p = []
    p.append(text(W / 2, 26, "Пережити втрату однієї зони: більше зон — менший надлишок",
                  size=14, bold=True, color=MUTED))
    p.append(text(W / 2, 48, "надлишок місткості = 1/(Z−1);  кожна зона несе N/(Z−1)",
                  size=12, color=MUTED))
    by, ty = 300, 78

    def Y(pct): return by - (by - ty) * pct / 100.0

    p.append(line(70, by, 630, by, color=INK, sw=1.5))
    over = {2: 100, 3: 50, 4: 33, 5: 25}
    share = {2: "кожна: N", 3: "кожна: N/2", 4: "кожна: N/3", 5: "кожна: N/4"}
    fills = {2: ("#fdecea", POS), 3: ("#fff6e6", "#b8860b"), 4: ("#eef2ff", NEG), 5: ("#eef7f0", FIELD)}
    cx = {2: 150, 3: 290, 4: 430, 5: 570}
    for z in [2, 3, 4, 5]:
        pct = over[z]
        top = Y(pct)
        f, s = fills[z]
        p.append(rect(cx[z] - 46, top, 92, by - top, fill=f, stroke=s, sw=1.4))
        p.append(text(cx[z], top - 10, "+%d%%" % pct, size=13, bold=True, color=INK))
        p.append(text(cx[z], by + 22, ("%d зони" % z) if z < 5 else "5 зон", size=12, bold=True, color=INK))
        p.append(text(cx[z], by + 40, share[z], size=11, color=MUTED))
    p.append(text(W / 2, 380, "дві зони коштують удвічі; три — лише +50% за ту саму гарантію",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'math-zone-overhead.svg'), W, H, *p)


# ══ Фігура для вставки «Звідки взялися діаграми взаємодії й розгортання» ══════
# ── Фігура H1: дві телеком-вкорінені лінії сходяться в UML ────────────────────
def fig_lineage_timeline():
    W, H = 820, 690
    p = []
    p.append(text(W / 2, 30,
                  "Дві телеком-вкорінені лінії сходяться в UML — і знову даються взнаки у версії 2.0",
                  size=13, bold=True, color=MUTED))

    # — Ліва колона: лінія стандартів телекому —
    p.append(text(200, 60, "Лінія стандартів телекому", size=12, bold=True, color=FIELD))
    p.append(fitbox(50, 74, 300, 46, "SDL · Z.100  (1976)",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD))
    p.append(fitbox(50, 148, 300, 46, "MSC · Z.120  (1992)",
                    size=13, bold=True, fill="#eef7f0", stroke=FIELD))
    p.append(fitbox(50, 222, 300, 46, "MSC'96 — alt · par · loop · opt",
                    size=12, bold=True, fill="#eef7f0", stroke=FIELD))
    p.append(arrow(200, 120, 200, 148, color=FIELD))
    p.append(arrow(200, 194, 200, 222, color=FIELD))

    # — Права колона: лінія об'єктних методів —
    p.append(text(620, 60, "Лінія об'єктних методів", size=12, bold=True, color=NEG))
    p.append(fitbox(470, 74, 300, 52, "Ericsson · Jacobson\nдіаграми взаємодії → OOSE",
                    size=12, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(fitbox(470, 154, 300, 52, "Booch (дизайн)  ·  Rumbaugh — OMT",
                    size=12, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(arrow(620, 126, 620, 154, color=NEG))

    # — Злиття: три амігос / UML Partners —
    p.append(fitbox(220, 300, 380, 54, "UML Partners · «три амігос»  (1996)",
                    size=13, bold=True, fill="#fff6e6", stroke="#b8860b"))
    p.append(arrow(200, 268, 300, 300, color=MUTED, sw=1.6))   # від MSC'96
    p.append(arrow(620, 206, 520, 300, color=MUTED, sw=1.6))   # від методів

    # — Спина версій —
    p.append(fitbox(220, 380, 380, 46, "UML 1.0 → подано в OMG · 13 січня 1997",
                    size=12, bold=True, fill="#fbfcff", stroke=INK))
    p.append(arrow(410, 354, 410, 380, color=INK))
    p.append(fitbox(220, 448, 380, 46, "UML 1.1 ухвалено OMG · листопад 1997",
                    size=12, bold=True, fill="#fbfcff", stroke=INK))
    p.append(arrow(410, 426, 410, 448, color=INK))

    # — UML 2.0 —
    p.append(fitbox(300, 522, 220, 50, "UML 2.0  (2005)",
                    size=14, bold=True, fill="#fdecea", stroke=POS))
    p.append(arrow(410, 494, 410, 522, color=INK))

    # — Наслідки 2.0 —
    p.append(fitbox(40, 606, 330, 60, "Комбіновані фрагменти:\nalt · opt · loop · par",
                    size=12, bold=True, fill="#eef7f0", stroke=FIELD))
    p.append(fitbox(450, 606, 330, 60, "Новий рід вузла —\n«середовище виконання»",
                    size=12, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(arrow(350, 572, 300, 606, color=INK, sw=1.5))
    p.append(arrow(470, 572, 520, 606, color=INK, sw=1.5))

    # — тонкий пунктирний слід: оператори MSC → комбіновані фрагменти —
    p.append(line(46, 246, 46, 598, color=FIELD, sw=1.4, dash="6 5"))
    p.append(_dhead(46, 598, 'd', color=FIELD))
    p.append(text(54, 430, "оператори MSC", size=10, italic=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, 'lineage-timeline.svg'), W, H, *p)


if __name__ == '__main__':
    fig_static_to_deploy()
    fig_static_vs_dynamic()
    fig_view_map()
    fig_seq_anatomy()
    fig_combined_fragments()
    fig_node_nesting()
    fig_availability_topology()
    fig_tail_amplification()
    fig_corr_floor()
    fig_k_of_n()
    fig_zone_overhead()
    fig_lineage_timeline()
    fig_iac_one_source()
    fig_single_zone_trap()
    print("done")
