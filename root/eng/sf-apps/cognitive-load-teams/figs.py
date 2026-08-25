# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три види навантаження в одному «відрі» пам'яті команди ──────────
def fig_three_loads():
    W, H = 900, 470
    frags = []

    frags.append(text(W / 2, 44, "Стеля уваги команди — одна на всі три види навантаження",
                      size=15, bold=True, anchor="middle"))

    # відро/склянка: три шари, що складаються до стелі
    bx, bw = 200, 300
    top_y = 90          # рівень стелі
    bot_y = 420
    cap_h = bot_y - top_y

    # частки шарів (сума = 1)
    parts = [
        ("Стороннє", 0.42, POS, "збірка, деплой,\nнезадокументовані примхи"),
        ("Внутрішнє", 0.38, NEG, "сама складність\nпредметної області"),
        ("Корисне", 0.20, FIELD, "будувати добру\nмодель у голові"),
    ]
    yy = bot_y
    for nm, frac, col, desc in parts:
        h = cap_h * frac
        frags.append(rect(bx, yy - h, bw, h, fill=col, stroke=INK, sw=1.4, rx=0))
        frags.append(text(bx + bw / 2, yy - h / 2 - 6, nm, size=15, bold=True,
                          color="#ffffff", anchor="middle"))
        frags.append(mtext(bx + bw / 2, yy - h / 2 + 12, desc, size=11,
                           color="#ffffff", anchor="middle", lh=1.15))
        yy -= h

    # лінія стелі
    frags.append(line(bx - 30, top_y, bx + bw + 30, top_y, color=INK, sw=2.5, dash="7,5"))
    frags.append(text(bx + bw + 40, top_y + 5, "СТЕЛЯ", size=13, bold=True,
                      color=INK, anchor="start"))

    # права підказка: зменшуй стороннє → звільняється місце під корисне
    ax = bx + bw + 40
    frags.append(arrow(ax + 60, bot_y - 20, ax + 60, top_y + cap_h * 0.42 + 20, color=FIELD, sw=2.4))
    tb, tw, th = textbox(ax + 150, (bot_y + top_y) / 2 + 40,
                         "зріж стороннє —\nзвільниш місце\nпід корисне", size=12,
                         fill="#eafaf1", stroke=FIELD, sw=1.6, pad=9)
    frags.append(tb)

    render(os.path.join(IMG, 'three-loads.svg'), W, H, *frags,
           title="Три види когнітивного навантаження ділять одну стелю")


# ── Фігура 2: розмір сервісу впирається в стелю, а не в залізо ────────────────
def fig_ceiling():
    W, H = 900, 430
    frags = []

    frags.append(text(W / 2, 42, "Що обмежує розмір сервісу", size=16, bold=True, anchor="middle"))

    # ЛІВА панель: команда під стелею тримає рівно стільки, скільки влазить
    lx = 60
    frags.append(text(lx + 160, 84, "Одна команда — одна стеля", size=13, bold=True, anchor="middle"))
    # стеля
    cap_y = 110
    frags.append(line(lx, cap_y, lx + 320, cap_y, color=INK, sw=2.5, dash="7,5"))
    frags.append(text(lx + 320, cap_y - 8, "стеля", size=11, bold=True, color=INK, anchor="end"))
    # три стовпчики сервісів під стелею
    svc = [("Сервіс A", 150, FIELD), ("Сервіс B", 110, FIELD), ("Сервіс C", 90, POS)]
    base_y = 380
    x0 = lx + 30
    for nm, hh, col in svc:
        bw = 78
        over = (base_y - hh) < cap_y
        fill = "#fdecea" if over else "#eafaf1"
        stroke = POS if over else FIELD
        frags.append(rect(x0, base_y - hh, bw, hh, fill=fill, stroke=stroke, sw=1.8, rx=6))
        frags.append(text(x0 + bw / 2, base_y - hh - 10, nm, size=11, bold=True,
                          color=stroke, anchor="middle"))
        x0 += bw + 26
    frags.append(line(lx, base_y, lx + 320, base_y, color=INK, sw=2))
    frags.append(text(lx + 160, base_y + 24, "C вилазить за стелю → якість падає",
                      size=11, color=POS, anchor="middle"))

    # роздільник
    frags.append(line(W / 2, 66, W / 2, H - 24, color="#d0d5db", sw=1.2, dash="5,5"))

    # ПРАВА панель: залізо масштабується вгору, голова — ні
    rx = W / 2 + 50
    frags.append(text(rx + 150, 84, "Залізо росте, голова — ні", size=13, bold=True, anchor="middle"))
    # дві осі-стовпчики
    frags.append(text(rx + 70, 130, "ЗАЛІЗО", size=12, bold=True, color=NEG, anchor="middle"))
    frags.append(arrow(rx + 70, 360, rx + 70, 150, color=NEG, sw=2.4))
    frags.append(mtext(rx + 70, 380, "додай вузлів —\nмасштабується", size=11,
                       color=NEG, anchor="middle", lh=1.15))
    frags.append(text(rx + 230, 130, "ГОЛОВА", size=12, bold=True, color=POS, anchor="middle"))
    frags.append(line(rx + 230, 360, rx + 230, 240, color=POS, sw=2.4))
    frags.append(text(rx + 230, 232, "стеля", size=11, bold=True, color=POS, anchor="middle"))
    frags.append(mtext(rx + 230, 380, "місткість —\nмайже стала", size=11,
                       color=POS, anchor="middle", lh=1.15))

    render(os.path.join(IMG, 'ceiling.svg'), W, H, *frags,
           title="Розмір сервісу впирається в стелю уваги, не в залізо")


# ── Фігура 3: важелі — зменшити стороннє, розрізати по межі області ───────────
def fig_levers():
    W, H = 900, 380
    frags = []

    frags.append(text(W / 2, 42, "Два способи влізти під стелю", size=16, bold=True, anchor="middle"))

    # ЛІВА: зрізати стороннє (одна область, менше сміття)
    lx = 60
    frags.append(text(lx + 170, 82, "1. Зрізати стороннє", size=14, bold=True, anchor="middle"))
    b1, w1, h1 = textbox(lx + 170, 150, "Платформа бере на себе\nзбірку, деплой, моніторинг",
                         size=12, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=11, min_w=300)
    frags.append(b1)
    frags.append(arrow(lx + 170, 150 + h1 / 2 + 6, lx + 170, 236, color=FIELD, sw=2.2))
    b2, w2, h2 = textbox(lx + 170, 270, "Команда думає лише про\nсвою предметну область",
                         size=12, fill=FILL, stroke=FIELD, sw=1.6, pad=11, min_w=300)
    frags.append(b2)

    # роздільник
    frags.append(line(W / 2, 66, W / 2, H - 24, color="#d0d5db", sw=1.2, dash="5,5"))

    # ПРАВА: розрізати по межі області
    rx = W / 2 + 50
    frags.append(text(rx + 170, 82, "2. Розрізати по межі області", size=14, bold=True, anchor="middle"))
    # один великий блок -> два по межі
    big, bw3, bh3 = textbox(rx + 170, 150, "Одна команда тримає\nдві незв'язані області",
                            size=12, fill="#fdecea", stroke=POS, sw=1.8, pad=11, min_w=300)
    frags.append(big)
    frags.append(arrow(rx + 170, 150 + bh3 / 2 + 6, rx + 170, 236, color=NEG, sw=2.2))
    s1 = fitbox(rx + 24, 250, 140, 46, "Команда «Оплата»", size=11,
                fill=FILL, stroke=FIELD, sw=1.6)
    s2 = fitbox(rx + 178, 250, 140, 46, "Команда «Каталог»", size=11,
                fill=FILL, stroke=FIELD, sw=1.6)
    frags.append(s1)
    frags.append(s2)

    render(os.path.join(IMG, 'levers.svg'), W, H, *frags,
           title="Два важелі: зрізати стороннє або розрізати по межі області")


if __name__ == "__main__":
    fig_three_loads()
    fig_ceiling()
    fig_levers()
    print("figures written to", IMG)
