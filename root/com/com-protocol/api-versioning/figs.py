# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: адитивна зміна проти зламної ──────────────────────────────────
def fig_breaking_vs_additive():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 32, "Адитивна зміна проти зламної", size=17, bold=True))

    # дві панелі
    frags.append(rect(30, 60, 345, 315, fill=BG, stroke=MUTED, sw=1.3))
    frags.append(rect(405, 60, 345, 315, fill=BG, stroke=MUTED, sw=1.3))
    Lcx, Rcx = 202, 577

    # заголовки-бейджі
    b, w, h = textbox(Lcx, 98, "Сервер ДОДАВ поле", size=13, bold=True, pad=8,
                      fill="#eaf7ef", stroke=FIELD, color="#1e7a44")
    frags.append(b)
    b, w, h = textbox(Rcx, 98, "Сервер ПЕРЕЙМЕНУВАВ поле", size=13, bold=True, pad=8,
                      fill="#fdecea", stroke=POS, color="#a02419")
    frags.append(b)

    # тіло відповіді, що прийшло клієнтові
    b, w, h = textbox(Lcx, 158, "amount: 500\ncurrency: usd", size=13, pad=9, fill=FILL, stroke=MUTED)
    frags.append(b)
    frags.append(text(Lcx, 200, "+ дописано currency", size=11, color="#1e7a44", italic=True))

    b, w, h = textbox(Rcx, 158, "total: 500\ncurrency: usd", size=13, pad=9, fill=FILL, stroke=MUTED)
    frags.append(b)
    frags.append(text(Rcx, 200, "amount зник", size=11, color="#a02419", italic=True))

    # стрілка вниз до клієнта
    frags.append(arrow(Lcx, 214, Lcx, 242, color=MUTED))
    frags.append(arrow(Rcx, 214, Rcx, 242, color=MUTED))

    # що читає старий клієнт
    b, w, h = textbox(Lcx, 272, "старий клієнт\nчитає res.amount → 500", size=12, pad=9, fill=BG, stroke=LINE)
    frags.append(b)
    b, w, h = textbox(Rcx, 272, "старий клієнт\nчитає res.amount → ∅", size=12, pad=9, fill=BG, stroke=LINE)
    frags.append(b)

    # стрілка вниз до вироку
    frags.append(arrow(Lcx, 302, Lcx, 326, color=MUTED))
    frags.append(arrow(Rcx, 302, Rcx, 326, color=MUTED))

    # вирок
    b, w, h = textbox(Lcx, 352, "✓ працює", size=14, bold=True, pad=8,
                      fill="#eaf7ef", stroke=FIELD, color="#1e7a44")
    frags.append(b)
    b, w, h = textbox(Rcx, 352, "✗ падає", size=14, bold=True, pad=8,
                      fill="#fdecea", stroke=POS, color="#a02419")
    frags.append(b)

    render(os.path.join(IMG, 'breaking-vs-additive.svg'), W, H, *frags)


# ── Фігура 2: три місця для позначки версії ─────────────────────────────────
def fig_version_placement():
    W, H = 840, 310
    frags = []
    frags.append(text(W / 2, 32, "Три місця для позначки версії", size=17, bold=True))

    lx, rqx, tx = 115, 445, 725
    rows = [
        (100, "Шлях URL", "#eaf7ef", FIELD, "#1e7a44",
         "GET /v2/orders/42",
         "видно й просто", FILL, LINE, INK),
        (178, "Заголовок", "#eaf0fd", NEG, INK,
         "GET /orders/42\nAPI-Version: 2",
         "чиста адреса,\nверсії не видно", FILL, LINE, INK),
        (256, "Тип медіа", "#fdf3e7", "#c98a2b", "#8a5a12",
         "GET /orders/42\nAccept: application/vnd.shop.v2+json",
         "канонічний REST,\nважче тестувати", "#fdecea", POS, "#a02419"),
    ]
    for y, lab, lf, ls, lc, req, tag, tf, ts, tc in rows:
        b, w, h = textbox(lx, y, lab, size=13, bold=True, pad=8, fill=lf, stroke=ls, color=lc, min_w=155)
        frags.append(b)
        b, w, h = textbox(rqx, y, req, size=13, pad=10, fill=BG, stroke=MUTED)
        frags.append(b)
        b, w, h = textbox(tx, y, tag, size=12, pad=8, fill=tf, stroke=ts, color=tc, min_w=150)
        frags.append(b)

    render(os.path.join(IMG, 'version-placement.svg'), W, H, *frags)


# ── Фігура 3: шар перекладу версій (upcast / downcast) ──────────────────────
def fig_version_transform():
    W, H = 820, 362
    frags = []
    frags.append(text(W / 2, 32, "Шар перекладу версій: ядро чисте, краї перекладають", size=16, bold=True))

    # чотири вузли (фіксовані рамки — щоб точно чіпляти стрілки до країв)
    frags.append(fitbox(40, 150, 150, 70, "Клієнт\n(прив'язаний до v1)", size=13,
                        fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True))
    frags.append(fitbox(280, 80, 205, 56, "Підняття (upcast)\nзапит v1 → поточна", size=13,
                        fill="#eaf7ef", stroke=FIELD, sw=1.8))
    frags.append(fitbox(575, 142, 205, 88, "Ядро\nлише поточна версія\nне знає про старі", size=13,
                        fill=FILL, stroke=INK, sw=2.2, bold=True))
    frags.append(fitbox(280, 240, 205, 56, "Опускання (downcast)\nвідповідь поточна → v1", size=13,
                        fill="#eaf7ef", stroke=FIELD, sw=1.8))

    # шлях запиту (верх): клієнт → підняття → ядро
    frags.append(arrow(190, 168, 278, 110, color=NEG, sw=2))
    frags.append(arrow(485, 108, 573, 162, color=NEG, sw=2))
    # шлях відповіді (низ): ядро → опускання → клієнт
    frags.append(arrow(575, 208, 487, 266, color=POS, sw=2))
    frags.append(arrow(280, 268, 192, 206, color=POS, sw=2))

    # підписи напрямків
    frags.append(text(232, 118, "запит", size=11, color=NEG, anchor="middle"))
    frags.append(text(232, 250, "відповідь", size=11, color=POS, anchor="middle"))

    # висновок унизу
    b, w, h = textbox(W / 2, 336,
                      "кожна зламна зміна — одне перетворення в ланцюжку, а не if по всьому коду",
                      size=12, bold=True, pad=9, fill="#fdf3e7", stroke="#c98a2b", color="#8a5a12")
    frags.append(b)

    render(os.path.join(IMG, 'version-transform.svg'), W, H, *frags)


# ── Фігура 4: ланцюжок перетворень — запит уперед, відповідь назад ───────────
def fig_transform_chain():
    W, H = 980, 380
    frags = []
    frags.append(text(W / 2, 30, "Ланцюжок перетворень: запит уперед, відповідь назад", size=16, bold=True))
    frags.append(text(W / 2, 58,
                      "запит підіймають уперед у часі (стара форма → нова); відповідь опускають назад (нова → стара)",
                      size=12, color=MUTED))

    # чотири колони (VC-боксы навмисно високі — одна зміна живе в обох смугах)
    frags.append(fitbox(20, 100, 132, 188, "Клієнт v1\n\n2023-05-10", size=13,
                        fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True))
    frags.append(fitbox(300, 100, 120, 188, "VC_rename\n\namount ⇄ total\n\n2024-02-20", size=12,
                        fill=FILL, stroke=INK, sw=1.6, bold=True))
    frags.append(fitbox(560, 100, 120, 188, "VC_cents\n\n$ ⇄ ¢  ×100\n\n2024-11-05", size=12,
                        fill=FILL, stroke=INK, sw=1.6, bold=True))
    frags.append(fitbox(828, 100, 132, 188, "Ядро\n\nлише\nпоточна", size=13,
                        fill="#eaf7ef", stroke=FIELD, sw=2.0, bold=True))

    # смуга запиту (згори): стрілки праворуч, синій
    yq = 150
    for x1, x2 in [(152, 300), (420, 560), (680, 828)]:
        frags.append(arrow(x1, yq, x2, yq, color=NEG, sw=2))
    for x, s in [(226, "{amount:500}"), (490, "{total:500}"), (754, "{total:50000}")]:
        b, _, _ = textbox(x, yq - 26, s, size=11, pad=5, fill=BG, stroke=NEG, color=NEG)
        frags.append(b)

    # смуга відповіді (знизу): стрілки ліворуч, червоний
    yr = 238
    for x1, x2 in [(828, 680), (560, 420), (300, 152)]:
        frags.append(arrow(x1, yr, x2, yr, color=POS, sw=2))
    for x, s in [(754, "{total:50000}"), (490, "{total:500}"), (226, "{amount:500}")]:
        b, _, _ = textbox(x, yr + 26, s, size=11, pad=5, fill=BG, stroke=POS, color=POS)
        frags.append(b)

    # висновок унизу
    b, _, _ = textbox(W / 2, 350,
                      "той самий набір змін, зворотний порядок — переплутаєш напрям, і числа тихо псуються",
                      size=12, bold=True, pad=9, fill="#fdf3e7", stroke="#c98a2b", color="#8a5a12")
    frags.append(b)

    render(os.path.join(IMG, 'transform-chain.svg'), W, H, *frags)


# ── Фігура 5 (вставка hist): драбина датованих версій Stripe ─────────────────
def fig_stripe_version_ladder():
    W, H = 860, 500
    frags = []
    frags.append(text(W / 2, 50,
                      "червоні стрілки — спуск відповіді ядра щаблями до пришпиленої версії",
                      size=12, color=MUTED))

    spine_x = 210
    # чотири датовані щаблі (згори найновіший)
    rungs = [
        (68, "2017-05-25\nсьогоднішнє ядро", FILL, INK, 2.2, True),
        (171, "2016-06-15", BG, MUTED, 1.5, False),
        (274, "2015-09-08", BG, MUTED, 1.5, False),
        (377, "2014-08-20", BG, MUTED, 1.5, False),
    ]
    rx0, rw, rh = 100, 220, 50
    centers = []
    for y, lab, f, st, sw, bold in rungs:
        frags.append(fitbox(rx0, y, rw, rh, lab, size=13, fill=f, stroke=st, sw=sw, bold=bold))
        centers.append(y + rh / 2)

    # спуск відповіді: червоні стрілки між щаблями
    for i in range(3):
        y1 = rungs[i][0] + rh
        y2 = rungs[i + 1][0]
        frags.append(arrow(spine_x, y1, spine_x, y2, color=POS, sw=2.2))

    # модулі-перетворення в проміжках + тонкий конектор до хребта
    gaps = [
        ("CollapseEventRequest", (rungs[0][0] + rh + rungs[1][0]) / 2),
        ("AccountTypes",          (rungs[1][0] + rh + rungs[2][0]) / 2),
        ("verified → status",     (rungs[2][0] + rh + rungs[3][0]) / 2),
    ]
    for lab, gy in gaps:
        b, w, h = textbox(450, gy, lab, size=12, pad=9, fill="#eef2f7", stroke=MUTED)
        frags.append(line(spine_x, gy, 450 - w / 2, gy, color=MUTED, sw=1.1, dash="3,3"))
        frags.append(b)

    # праворуч — два акаунти, пришпилені до різних щаблів
    bn, wn, hn = textbox(715, centers[0],
                         "Новий акаунт\nпришпилений 2017-05-25\nбез перетворень",
                         size=12, pad=10, fill="#eaf7ef", stroke=FIELD)
    frags.append(arrow(rx0 + rw, centers[0], 715 - wn / 2, centers[0], color=FIELD, sw=1.8))
    frags.append(bn)

    bo, wo, ho = textbox(715, centers[3],
                         "Стара інтеграція\nпришпилена 2014-08-20",
                         size=12, pad=10, fill="#eaf0fd", stroke=NEG)
    frags.append(arrow(rx0 + rw, centers[3], 715 - wo / 2, centers[3], color=NEG, sw=1.8))
    frags.append(bo)

    # висновок унизу
    b, w, h = textbox(W / 2, 472,
                      "ядро пише лише під верхній щабель · старому клієнту відповідь спускають по модулю на щабель",
                      size=12, bold=True, pad=9, fill="#fdf3e7", stroke="#c98a2b", color="#8a5a12")
    frags.append(b)

    render(os.path.join(IMG, 'stripe-version-ladder.svg'), W, H, *frags,
           title="Драбина датованих версій Stripe")


if __name__ == "__main__":
    fig_breaking_vs_additive()
    fig_version_placement()
    fig_version_transform()
    fig_transform_chain()
    fig_stripe_version_ladder()
    print("figures written")
