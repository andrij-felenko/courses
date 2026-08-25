# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Межа агрегата: корінь як єдині двері ─────────────────────────────────────
def fig_aggregate_boundary():
    W, H = 960, 520
    frags = []

    # Головна межа агрегата Order (замкнений контур)
    bx, by, bw, bh = 150, 120, 460, 320
    frags.append(rect(bx, by, bw, bh, fill="#f0f6ff", stroke=NEG, sw=2.2, rx=18))
    frags.append(text(bx + bw / 2, by - 18, "Агрегат «Замовлення»",
                      size=17, bold=True, color=NEG))
    # підпис межі
    frags.append(text(bx + bw / 2, by + bh + 26,
                      "інваріант виконується тут — на кожен погляд ззовні",
                      size=13, bold=True, color=FIELD))

    # Корінь у центрі верху межі
    root_cx, root_cy = bx + bw / 2, by + 70
    rbody, rw, rh = textbox(root_cx, root_cy, "КОРІНЬ: Order",
                            size=15, bold=True, pad=14,
                            fill="#fdecea", stroke=POS, sw=2.4, min_w=180)
    frags.append(rbody)

    # Внутрішні частини (приватні) — нижче кореня
    inner = [
        ("OrderLine ×3", bx + 120, by + 210),
        ("discount", bx + 340, by + 210),
    ]
    for label, cx, cy in inner:
        ibody, iw, ih = textbox(cx, cy, label, size=13, pad=11,
                                fill=FILL, stroke=MUTED, sw=1.5)
        frags.append(ibody)
        # стрілка корінь → внутрішнє (керує зсередини)
        frags.append(arrow(root_cx, root_cy + rh / 2, cx, cy - 22, color=MUTED, sw=1.6))

    # Єдині двері: стрілка ЗЗОВНІ входить у корінь
    frags.append(arrow(bx - 88, root_cy, root_cx - rw / 2, root_cy, color=INK, sw=2.6))
    frags.append(text(12, root_cy - 12, "зовнішній код", size=13, bold=True, anchor="start"))
    frags.append(text(12, root_cy + 8, "стукає лише", size=12, color=MUTED, anchor="start"))
    frags.append(text(12, root_cy + 26, "в корінь", size=12, color=MUTED, anchor="start"))

    # Друга межа — сусідній агрегат Customer
    cbx, cby, cbw, cbh = 690, 150, 250, 200
    frags.append(rect(cbx, cby, cbw, cbh, fill="#f0f6ff", stroke=NEG, sw=2.2, rx=18))
    frags.append(text(cbx + cbw / 2, cby - 18, "Агрегат «Клієнт»",
                      size=15, bold=True, color=NEG))
    ccx, ccy = cbx + cbw / 2, cby + 70
    cbody, ccw, cch = textbox(ccx, ccy, "КОРІНЬ: Customer",
                              size=14, bold=True, pad=13,
                              fill="#fdecea", stroke=POS, sw=2.2, min_w=170)
    frags.append(cbody)

    # Зв'язок між межами — тонка стрілка за ідентифікатором
    frags.append(arrow(bx + bw + 8, root_cy + 4, cbx - 6, ccy, color=INK, sw=1.5))
    frags.append(text((bx + bw + cbx) / 2, root_cy - 26, "customerId",
                      size=13, bold=True, color=INK))
    frags.append(text((bx + bw + cbx) / 2, root_cy - 8, "(лише id)",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'aggregate-boundary.svg'), W, H, *frags,
           title="Межа агрегата: корінь як єдині двері")


# ── Посилання за id: злиплі проти розділених агрегатів ───────────────────────
def fig_reference_by_id():
    W, H = 940, 470
    frags = []

    # ЛІВОРУЧ: злиплі в одну велику межу
    lx, ly, lw, lh = 40, 96, 380, 300
    frags.append(rect(lx, ly, lw, lh, fill="#fdf0ee", stroke=POS, sw=2.2, rx=16))
    frags.append(text(lx + lw / 2, ly - 42, "Прямий об'єкт", size=16, bold=True, color=POS))
    frags.append(text(lx + lw / 2, ly - 22, "одна транзакція тягне все", size=12, color=MUTED))

    o1, ow, oh = textbox(lx + 110, ly + 70, "Order", size=14, bold=True, pad=12,
                         fill="#fdecea", stroke=POS, sw=2, min_w=120)
    frags.append(o1)
    c1, cw, ch = textbox(lx + 270, ly + 70, "Customer", size=14, bold=True, pad=12,
                         fill="#fdecea", stroke=POS, sw=2, min_w=120)
    frags.append(c1)
    o2, o2w, o2h = textbox(lx + 270, ly + 210, "інші Order", size=13, pad=11,
                           fill=FILL, stroke=MUTED, sw=1.5, min_w=120)
    frags.append(o2)
    # жирні стрілки «володіє об'єктом»
    frags.append(arrow(lx + 110 + ow / 2, ly + 70, lx + 270 - cw / 2, ly + 70, color=POS, sw=2.4))
    frags.append(arrow(lx + 270, ly + 70 + ch / 2, lx + 270, ly + 210 - o2h / 2, color=POS, sw=2.4))
    frags.append(text(lx + lw / 2, ly + lh + 24, "усе в одній межі — усе злиплося",
                      size=12, bold=True, color=POS))

    # ПРАВОРУЧ: розділені межі
    r1x, r1y, r1w, r1h = 520, 120, 170, 150
    r2x, r2y, r2w, r2h = 760, 120, 170, 150
    frags.append(rect(r1x, r1y, r1w, r1h, fill="#f0f6ff", stroke=NEG, sw=2.2, rx=16))
    frags.append(rect(r2x, r2y, r2w, r2h, fill="#f0f6ff", stroke=NEG, sw=2.2, rx=16))
    frags.append(text(r1x + r1w / 2, r1y - 42, "Посилання за id", size=16, bold=True, color=NEG))
    frags.append(text((r1x + r2x + r2w) / 2, r1y - 22, "кожна межа — своя транзакція",
                      size=12, color=MUTED))

    ro, row, roh = textbox(r1x + r1w / 2, r1y + 70, "Order", size=14, bold=True, pad=12,
                           fill="#fdecea", stroke=POS, sw=2, min_w=110)
    frags.append(ro)
    rc, rcw, rch = textbox(r2x + r2w / 2, r2y + 70, "Customer", size=14, bold=True, pad=12,
                           fill="#fdecea", stroke=POS, sw=2, min_w=110)
    frags.append(rc)
    # тонка стрілка за ідентифікатором між межами
    frags.append(arrow(r1x + r1w + 4, r1y + 70, r2x - 4, r2y + 70, color=INK, sw=1.5))
    frags.append(text((r1x + r1w + r2x) / 2, r1y + 46, "customerId", size=12, bold=True, color=INK))
    frags.append(text((r1x + r2x + r2w) / 2, r1y + r1h + 24,
                      "межі цілі — зміни локальні", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'reference-by-id.svg'), W, H, *frags,
           title="Посилання за id проти прямого об'єкта")


if __name__ == "__main__":
    fig_aggregate_boundary()
    fig_reference_by_id()
    print("figures written to", IMG)
