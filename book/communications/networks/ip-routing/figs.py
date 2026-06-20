# -*- coding: utf-8 -*-
"""Фігури до теми «Маршрутизація IP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ідея next hop: кожен знає лише наступний крок, не весь шлях ───────────
def fig_next_hop_idea():
    """Серце теми. Пакет іде з мережі-джерела в далеку мережу-ціль через
    ланцюг маршрутизаторів. Жоден не знає всього шляху — кожен знає лише,
    кому передати ЗАРАЗ. Як водій за знаками, не пам'ятаючи всієї карти."""
    W, H = 780, 360
    f = [text(W / 2, 30, "Кожен вузол знає лише наступний крок — не цілий шлях", size=17, bold=True)]

    y = 175
    # джерело
    f.append(circle(70, y, 34, fill="#eef3ff", stroke=NEG, sw=2))
    f.append(text(70, y + 5, "ти", size=13, bold=True, color=NEG))
    f.append(text(70, y + 52, "мережа A", size=11, color=MUTED))

    # три маршрутизатори посередині
    rxs = [240, 400, 560]
    for i, rx in enumerate(rxs):
        f.append(rect(rx - 38, y - 26, 76, 52, fill="#fff7e6", stroke=MUTED, sw=1.6))
        f.append(text(rx, y - 4, "R%d" % (i + 1), size=14, bold=True))
        f.append(text(rx, y + 16, "next hop?", size=9, color=MUTED))

    # ціль
    f.append(circle(720, y, 34, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(720, y + 5, "ціль", size=12, bold=True, color=FIELD))
    f.append(text(720, y + 52, "мережа Z", size=11, color=MUTED))

    # стрілки-перегони
    xs = [70 + 34] + [r + 38 for r in rxs]
    xe = [r - 38 for r in rxs] + [720 - 34]
    for a, b in zip(xs, xe):
        f.append(arrow(a, y, b, y, color=INK, sw=1.8))

    # підписи «один крок» над кожним перегоном
    for a, b in zip(xs, xe):
        f.append(text((a + b) / 2, y - 36, "крок", size=9, color=MUTED, italic=True))

    f.append(fitbox(150, 268, 480, 42,
                    "Ніхто не тримає карти цілого світу. Кожен R вирішує лише: кому передати ЗАРАЗ,\nщоб пакет став ближче до цілі — і передає сусідові. Разом ведуть пакет будь-куди.",
                    size=11, fill=BG, stroke=LINE, sw=1.2))
    f.append(text(W / 2, 338, "Як водій за дорожніми знаками: знаєш поворот на цьому перехресті, не всю карту.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "next-hop-idea.svg"), W, H, *f)


# ── 2. Маска підмережі: ділить адресу на «мережу» і «вузол» ──────────────────
def fig_subnet_mask():
    """Маска = підряд одиниці, тоді нулі. Побітове «І» адреси з маскою лишає
    номер мережі, обнуляє вузол. Два вузли однієї підмережі → однаковий номер
    мережі; чужий → інший. За цим збігом вирішують: своя ціль чи чужа."""
    W, H = 780, 410
    f = [text(W / 2, 30, "Маска ділить адресу на «номер мережі» і «номер вузла»", size=16, bold=True)]

    # три байти мережі + один байт вузла — кольорова смуга
    bx, by, cellw, ch = 70, 70, 150, 46
    labels = ["192", "168", "1", "42"]
    for i, lab in enumerate(labels):
        is_host = (i == 3)
        fillc = "#eafaf0" if not is_host else "#eef3ff"
        strc = FIELD if not is_host else NEG
        f.append(rect(bx + i * cellw, by, cellw - 6, ch, fill=fillc, stroke=strc, sw=1.6))
        f.append(text(bx + i * cellw + (cellw - 6) / 2, by + 30, lab, size=18, bold=True,
                      color=strc))
    f.append(text(bx + 1.5 * cellw, by - 8, "← номер МЕРЕЖІ (під одиницями маски) →",
                  size=11, color=FIELD))
    f.append(text(bx + 3 * cellw + (cellw - 6) / 2, by + ch + 18, "вузол", size=11, color=NEG))

    # рядок маски
    my = by + ch + 36
    masks = ["11111111", "11111111", "11111111", "00000000"]
    f.append(text(bx - 6, my + 24, "маска /24:", size=12, bold=True, anchor="end"))
    for i, mm in enumerate(masks):
        is_host = (i == 3)
        f.append(fitbox(bx + i * cellw, my, cellw - 6, 34, mm, size=12,
                        fill="#f4f6f8", stroke=FIELD if not is_host else NEG, sw=1.2))
    f.append(text(bx + 2 * cellw, my + 52, "одиниці накривають мережу · нулі — вузол", size=11,
                  color=MUTED))

    # побітове І → результат
    ry = my + 78
    f.append(fitbox(70, ry, 300, 56,
                    "адреса & маска  (побітове «І»):\nде 1 — біт лишається, де 0 — обнуляється",
                    size=11, fill="#fff7e6", stroke=MUTED, sw=1.3))
    f.append(arrow(380, ry + 28, 430, ry + 28, color=LINE))
    f.append(fitbox(440, ry, 280, 56,
                    "→ номер мережі: 192.168.1.0\n(частина вузла обнулена)",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.3, bold=True))

    f.append(text(W / 2, ry + 90,
                  "Свій сусід дає той самий 192.168.1.0 → ціль СВОЯ; чужа адреса — інший номер → ЧУЖА.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "subnet-mask.svg"), W, H, *f)


# ── 3. Найдовший збіг префікса: який рядок виграє ────────────────────────────
def fig_longest_prefix():
    """Для однієї цілі підходить кілька рядків таблиці. Виграє той, чия маска
    довша (вужча, конкретніша мережа). default /0 збігається з усім, але
    програє будь-якому точнішому — ловить лише «решту»."""
    W, H = 780, 400
    f = [text(W / 2, 28, "Вибір рядка: виграє найдовша маска, default — останній рубіж", size=16, bold=True)]

    f.append(fitbox(250, 54, 280, 34, "ціль пакета: 10.0.5.7", size=13,
                    fill="#eef3ff", stroke=NEG, sw=1.4, bold=True))

    rows = [
        ("192.168.1.0", "/24", "192.168.1.0 ≠ 10.0.5.0", "не підходить", False, MUTED),
        ("10.0.5.0",    "/24", "10.0.5.0 = 10.0.5.0",   "ПІДХОДИТЬ  (маска /24)", True, FIELD),
        ("0.0.0.0",     "/0",  "0.0.0.0 = 0.0.0.0",     "підходить  (маска /0)", None, POS),
    ]
    ty, rh = 108, 64
    for i, (net, msk, calc, verdict, win, col) in enumerate(rows):
        yy = ty + i * (rh + 10)
        fillc = "#eafaf0" if win is True else ("#fdecea" if win is False else "#fff7e6")
        f.append(rect(60, yy, 660, rh, fill=fillc, stroke=col, sw=1.6))
        f.append(fitbox(72, yy + 12, 150, 40, "%s %s" % (net, msk), size=13,
                        fill=BG, stroke=col, sw=1.1, bold=True))
        f.append(text(245, yy + 27, "ціль & %s →" % msk, size=11, color=MUTED, anchor="start"))
        f.append(text(245, yy + 46, calc, size=12, anchor="start"))
        f.append(text(530, yy + 38, verdict, size=12, bold=(win is True), color=col, anchor="start"))

    f.append(fitbox(140, ty + 3 * (rh + 10) + 4, 500, 40,
                    "підійшли два рядки → беремо НАЙДОВШУ маску: /24 > /0\n→ next hop = 192.168.1.2",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.4, bold=True))
    f.append(text(W / 2, 384,
                  "default 0.0.0.0/0 (маска завдовжки нуль) збігається з усім, але програє будь-якому точнішому рядку.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "longest-prefix.svg"), W, H, *f)


# ── 4. Той самий механізм на всіх масштабах ─────────────────────────────────
def fig_scales():
    """Від телефона до магістрального маршрутизатора — одне правило (наклади
    маску, порівняй, віддай next hop). Змінюється лише розмір таблиці:
    у телефоні 2 рядки, у провайдера — сотні тисяч і динамічна."""
    W, H = 780, 380
    f = [text(W / 2, 28, "Той самий механізм на всіх масштабах — змінюється лише розмір таблиці",
              size=15, bold=True)]

    cols = [
        ("Телефон / МК", "~2 рядки", ["своя мережа", "default → роутер"], NEG, "#eef3ff"),
        ("Домашній роутер", "кілька рядків", ["своя LAN", "default → провайдер"], FIELD, "#eafaf0"),
        ("Магістраль", "сотні тисяч", ["мережі з усього", "світу · динамічно"], POS, "#fdecea"),
    ]
    bx, bw, gap = 50, 220, 15
    for i, (title_, cnt, lines, col, fillc) in enumerate(cols):
        x = bx + i * (bw + gap)
        f.append(rect(x, 70, bw, 150, fill=fillc, stroke=col, sw=1.6))
        f.append(text(x + bw / 2, 96, title_, size=14, bold=True, color=col))
        f.append(text(x + bw / 2, 118, cnt + " у таблиці", size=11, color=MUTED))
        f.append(mtext(x + bw / 2, 150, lines, size=11, anchor="middle", lh=1.5))
        # розмір таблиці росте зліва направо — стрілка-натяк
        if i < 2:
            f.append(arrow(x + bw + 1, 145, x + bw + gap - 1, 145, color=LINE, sw=1.6))

    # спільне правило — одна стрічка під усіма
    f.append(fitbox(80, 250, 620, 52,
                    "ОДНЕ правило на всіх: наклади маску → порівняй номер мережі →\nвізьми найдовший збіг → віддай пакет на next hop. Код той самий; росте лише кількість рядків.",
                    size=12, fill="#fff7e6", stroke=MUTED, sw=1.4, bold=True))
    f.append(text(W / 2, 338,
                  "У телефоні майже все йде за default; у провайдера рядки живі (динамічна маршрутизація). Логіка незмінна.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "scales.svg"), W, H, *f)


if __name__ == "__main__":
    fig_next_hop_idea()
    fig_subnet_mask()
    fig_longest_prefix()
    fig_scales()
    print("OK: 4 figures ->", IMG)
