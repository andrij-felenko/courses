# -*- coding: utf-8 -*-
"""Фігури до кроку «Мапа контекстів Digital Homes»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CORE = "#eafaf0"    # заливка контекстів-ядра
BELT = "#eef2fb"    # заливка поясу служб
EXT = "#fdecea"     # заливка зовнішніх систем
KERN = "#fff8e1"    # спільне ядро / токен / ACL-маркер


def _box(cx, cy, label, fill=FILL, stroke=LINE, sw=1.6, min_w=120, size=14,
         bold=False, dash=None):
    """Рамка з текстом; повертає (frag, left, right, top, bottom)."""
    lines = label.split("\n")
    tw = max(text_width(ln, size, bold) for ln in lines)
    w = max(min_w, tw + 20)
    h = len(lines) * size * 1.3 + 20 - size * 0.3
    x, y = cx - w / 2, cy - h / 2
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    body = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" '
            'fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (x, y, w, h, fill, stroke, sw, d))
    ty = cy - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
    body += mtext(cx, ty, lines, size=size, color=INK, bold=bold)
    return body, x, x + w, y, y + h


def chip(cx, cy, s, fill=KERN, stroke=MUTED, size=12):
    b, _, _ = textbox(cx, cy, s, size=size, fill=fill, stroke=stroke, sw=1.5, min_w=48)
    return b


def fig_hub_acl():
    """ACL на краю: зоопарк вендорських протоколів → чистий факт домом."""
    W, H = 1020, 440
    f = []

    # ── ліворуч: сирі вендорські протоколи ──
    protos = ["Zigbee\nattr 0x0101", "Z-Wave\ncmd class",
              "Matter\ncluster", "хмарне API\nвендора"]
    ys = [95, 185, 275, 365]
    edges = []
    for s, y in zip(protos, ys):
        b, l, r, t, bt = _box(150, y, s, fill=EXT, stroke=POS, sw=1.6,
                              min_w=150, size=12)
        f.append(b)
        edges.append((r, y))
    f.append(text(150, 45, "чужі мови (кожен вендор свій)", size=12, color=MUTED))

    # ── посередині: антикорупційний шар ──
    ab, al, ar, at, ab2 = _box(510, 230, "Антикорупційний\nшар (у хабі)\n— перекладач",
                               fill=KERN, stroke=INK, sw=2.4, min_w=200, size=14, bold=True)
    for r, y in edges:
        f.append(arrow(r + 6, y, al - 8, 230, color=POS, sw=1.7))
    f.append(ab)

    # ── праворуч: чиста модель дому ──
    cb, cl, cr, ct, cb2 = _box(850, 230, "модель дому\n«замок гаража → Locked»\nLock · стан · кімната",
                               fill=CORE, stroke=FIELD, sw=2.2, min_w=230, size=13)
    f.append(arrow(ar + 8, 230, cl - 8, 230, color=FIELD, sw=2.2))
    f.append(cb)

    f.append(text(W / 2, 415,
                  "чужу радіо-мову лишаємо зовні — усередину входить лише чистий факт",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "hub-acl.svg"), W, H, *f,
           title="Антикорупційний шар на краю заліза")


def fig_identity_ohs():
    """Ідентичність як відкрита служба: один токен, усі конформляться."""
    W, H = 1040, 560
    f = []

    # ліворуч — контекст ідентичності
    ib, il, ir, it, ib2 = _box(165, 285, "Ідентичність\n(відкрита\nслужба)",
                               fill=FILL, stroke=INK, sw=2.2, min_w=150, size=14, bold=True)
    f.append(ib)

    # центр — токен як опублікована мова
    tb, tl, tr, tt, tb2 = _box(445, 285, "токен · JWT\nопублікована\nмова",
                               fill=KERN, stroke=POS, sw=2.0, min_w=150, size=13)
    f.append(arrow(ir + 8, 285, tl - 8, 285, color=INK, sw=2.0))
    f.append(text((ir + tl) / 2, 250, "публікує", size=12, color=MUTED))
    f.append(tb)

    # праворуч — усі споживачі конформляться
    ctx = ["Керування", "Твін", "Автоматизації", "Телеметрія", "Сповіщення", "Білінг"]
    ys = [80, 165, 250, 335, 420, 505]
    for s, y in zip(ctx, ys):
        b, l, r, t, bt = _box(870, y, s, fill=BELT, stroke=NEG, sw=1.5, min_w=160, size=13)
        f.append(arrow(tr + 8, 285, l - 8, y, color=NEG, sw=1.4))
        f.append(b)
    f.append(text(672, 45, "конформіст (усі приймають як є)", size=12, color=NEG))

    f.append(text(W / 2, 540,
                  "один відкритий вхід і одна опублікована мова замість десятка домовленостей",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "identity-ohs.svg"), W, H, *f,
           title="Ідентичність — відкрита служба з опублікованою мовою")


def fig_context_map():
    """Повна мапа контекстів Digital Homes: коробки + підписані стрілки."""
    W, H = 1200, 840
    f = []

    # ── коробки ──
    ven = _box(110, 300, "вендорські\nзалізяки", fill=EXT, stroke=POS, sw=1.5,
               min_w=120, size=12, dash="5,4")
    hub = _box(300, 300, "Хаб\n(край)", fill=CORE, stroke=FIELD, sw=2.0, min_w=120)
    ker = _box(560, 150, "Керування\nпристроями", fill=CORE, stroke=FIELD, sw=2.4, min_w=155)
    twn = _box(560, 300, "Твін\n(дзеркало)", fill=CORE, stroke=FIELD, sw=2.4, min_w=155)
    aut = _box(560, 450, "Автоматизації", fill=CORE, stroke=FIELD, sw=2.4, min_w=155)
    tel = _box(835, 120, "Телеметрія", fill=BELT, stroke=NEG, sw=1.8, min_w=150)
    ntf = _box(835, 275, "Сповіщення", fill=BELT, stroke=NEG, sw=1.8, min_w=150)
    vid = _box(835, 425, "Відео", fill=BELT, stroke=MUTED, sw=1.8, min_w=150, dash="6,4")
    bil = _box(835, 575, "Білінг", fill=BELT, stroke=NEG, sw=1.8, min_w=150)
    pay = _box(1085, 575, "платіжний\nпровайдер", fill=EXT, stroke=POS, sw=1.5, min_w=120, size=12, dash="5,4")
    psh = _box(1085, 275, "пуш-\nпровайдери", fill=EXT, stroke=POS, sw=1.5, min_w=120, size=12, dash="5,4")

    # мітки зон
    f.append(text(110, 210, "залізо", size=12, color=MUTED))
    f.append(text(560, 70, "ЯДРО в хмарі", size=13, color=FIELD, bold=True))
    f.append(text(835, 62, "пояс служб", size=13, color=NEG, bold=True))
    f.append(text(1085, 200, "зовнішні", size=12, color=POS))

    # ── стрілки й підписи ──
    # 1. вендори → хаб : ACL
    f.append(arrow(ven[2] + 6, 300, hub[1] - 8, 300, color=POS, sw=1.8))
    f.append(chip(205, 268, "ACL", fill=KERN, stroke=POS))
    # 2. хаб ↔ твін : партнерство
    f.append(arrow(hub[2] + 6, 293, twn[1] - 8, 293, color=INK, sw=1.8))
    f.append(arrow(twn[1] - 8, 309, hub[2] + 6, 309, color=INK, sw=1.8))
    f.append(text(423, 272, "партнерство", size=12, color=INK, bold=True))
    # 3. керування → твін : замовник-постачальник
    f.append(arrow(560, ker[4] + 4, 560, twn[3] - 6, color=INK, sw=1.7))
    f.append(text(487, 228, "зам.→", size=11, color=MUTED))
    f.append(text(487, 242, "пост.", size=11, color=MUTED))
    # 4. твін → автоматизації : замовник-постачальник
    f.append(arrow(560, twn[4] + 4, 560, aut[3] - 6, color=INK, sw=1.7))
    f.append(text(487, 378, "зам.→", size=11, color=MUTED))
    f.append(text(487, 392, "пост.", size=11, color=MUTED))

    # 5. потік подій (опублікована мова) : керування → шина → телеметрія, сповіщення
    bx = 690
    f.append(line(bx, 118, bx, 300, color=NEG, sw=1.6, dash="4,4"))
    f.append(text(bx, 100, "події ·", size=11, color=NEG))
    f.append(text(bx, 114, "опубл. мова", size=11, color=NEG))
    f.append(arrow(ker[2] + 6, 150, bx - 3, 150, color=NEG, sw=1.5))
    f.append(arrow(bx + 3, 120, tel[1] - 8, 120, color=NEG, sw=1.5))
    f.append(arrow(bx + 3, 275, ntf[1] - 8, 275, color=NEG, sw=1.5))

    # 6. сповіщення → пуш : ACL на вихід
    f.append(arrow(ntf[2] + 6, 275, psh[1] - 8, 275, color=POS, sw=1.7))
    f.append(chip(962, 245, "ACL", fill=KERN, stroke=POS))
    # 7. білінг ↔ платіжний : ACL
    f.append(arrow(bil[2] + 6, 575, pay[1] - 8, 575, color=POS, sw=1.7))
    f.append(chip(962, 545, "ACL", fill=KERN, stroke=POS))
    # керування → білінг : зам.-пост. (довга, збоку від ядра)
    f.append(arrow(ker[2] + 6, 165, 745, 560, color=MUTED, sw=1.3))
    f.append(text(742, 470, "зам.→пост.", size=11, color=MUTED, anchor="end"))

    # 8. відео — окремі шляхи
    f.append(text(835, vid[4] + 22, "окремі шляхи", size=12, color=MUTED, italic=True))

    # ── ідентичність: широка смуга-фундамент, усі конформляться ──
    f.append(rect(180, 700, 800, 66, fill=FILL, stroke=INK, sw=2.2))
    f.append(text(580, 728, "Ідентичність", size=15, bold=True, color=INK))
    f.append(text(580, 748, "відкрита служба + опубл. мова (токен) — усі конформляться",
                  size=12, color=MUTED))
    # два представницькі конформіст-пунктири
    f.append(arrow(560, aut[4] + 6, 560, 698, color=MUTED, sw=1.2))
    f.append(arrow(835, bil[4] + 6, 835, 698, color=MUTED, sw=1.2))
    f.append(text(568, 620, "конформіст", size=11, color=MUTED, anchor="start"))

    # ── спільне ядро: крихітний чип ──
    f.append(chip(150, 620, "спільне ядро:\nDeviceId · HomeId", fill=KERN, stroke=FIELD, size=11))

    # коробки — поверх стрілок
    for b in (ven, hub, ker, twn, aut, tel, ntf, vid, bil, pay, psh):
        f.append(b[0])

    render(os.path.join(IMG, "context-map.svg"), W, H, *f,
           title="Мапа контекстів Digital Homes")


def fig_one_source():
    """Одне джерело (мапа-дані) — троє споживачів: ворота, картинка, легенда."""
    W, H = 1000, 560
    f = []

    sb, sl, sr, st, sbo = _box(
        250, 280,
        "МАПА DH — дані\nmap.ts / map.py\n9 контекстів + шина + ядро\nребра · види зв'язку",
        fill=KERN, stroke=INK, sw=2.6, min_w=290, size=13, bold=True)

    top = _box(775, 128, "Фітнес-функція\nворота CI · exit 1\nловить заборонене ребро",
               fill=EXT, stroke=POS, sw=2.0, min_w=280, size=13)
    mid = _box(775, 300, "SVG-мапа\nта сама картинка\nз тих самих даних",
               fill=CORE, stroke=FIELD, sw=2.0, min_w=280, size=13)
    bot = _box(775, 472, "Легенда-таблиця\nтой самий довідник\nрядками",
               fill=BELT, stroke=NEG, sw=2.0, min_w=280, size=13)

    f.append(arrow(sr + 6, 268, top[1] - 8, 128, color=POS, sw=1.9))
    f.append(arrow(sr + 6, 280, mid[1] - 8, 300, color=FIELD, sw=1.9))
    f.append(arrow(sr + 6, 292, bot[1] - 8, 472, color=NEG, sw=1.9))
    f.append(text(560, 182, "стереже", size=13, color=POS, bold=True))
    f.append(text(560, 286, "малює", size=13, color=FIELD, bold=True))
    f.append(text(560, 404, "друкує", size=13, color=NEG, bold=True))

    f.extend([sb, top[0], mid[0], bot[0]])
    f.append(text(W / 2, 544,
                  "змінив ребро в мапі — зрушились усі троє; розійтися нічому",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "map-one-source.svg"), W, H, *f,
           title="Одне джерело — троє споживачів")


def fig_published_wall():
    """Ребро дозволене, але лише в published; у нутрощі (domain/Device) — стіна."""
    W, H = 1000, 500
    f = []

    bl, bll, blr, blt, blb = _box(160, 250, "Білінг\n(billing)",
                                  fill=BELT, stroke=NEG, sw=2.0, min_w=150, size=14, bold=True)

    f.append(rect(560, 108, 388, 304, fill="#fbfdff", stroke=FIELD, sw=2.2))
    f.append(text(754, 136, "Керування (control)", size=14, color=FIELD, bold=True))
    pub = _box(770, 208, "published/\nDeviceRegistered\n(опублікований факт)",
               fill=KERN, stroke=FIELD, sw=2.0, min_w=250, size=12)
    dom = _box(770, 348, "domain/Device\n(живий агрегат,\nінваріанти)",
               fill=FILL, stroke=INK, sw=2.0, min_w=250, size=12)

    f.append(arrow(blr + 6, 232, pub[1] - 8, 208, color=FIELD, sw=2.2))
    f.append(text(430, 188, "дозволено: у published", size=12, color=FIELD, bold=True))

    wall_x = 600
    f.append(line(wall_x, 300, wall_x, 396, color=POS, sw=5))
    f.append(line(blr + 6, 286, wall_x - 4, 348, color=POS, sw=2.0, dash="7,5"))
    f.append(text(wall_x + 8, 353, "✗", size=22, color=POS, bold=True, anchor="start"))
    f.append(text(420, 306, "заборонено: у нутрощі", size=12, color=POS, bold=True))
    f.append(text(wall_x, 414, "стіна", size=12, color=POS))

    f.extend([bl, pub[0], dom[0]])
    f.append(text(W / 2, 478,
                  "ребро billing→control оголошене — та ЛИШЕ у published; Device лежить у domain → збірка червона",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "published-wall.svg"), W, H, *f,
           title="Дозволене ребро — але лише в опубліковану поверхню")


if __name__ == "__main__":
    fig_hub_acl()
    fig_identity_ohs()
    fig_context_map()
    fig_one_source()
    fig_published_wall()
    print("OK: hub-acl, identity-ohs, context-map, map-one-source, published-wall")
