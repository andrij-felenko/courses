# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox at center, returns (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: два роди методів — команда і запит; заборонений гібрид ──────────
def two_kinds():
    W, H = 940, 480
    parts = []
    parts.append(text(W / 2, 34, "Метод — рівно одного роду", size=18, bold=True))

    # ---- лівий стовп: КОМАНДА ----
    cx = 230
    hc, hcw, hch = box_at(cx, 96, "КОМАНДА", size=15, bold=True,
                          fill="#fdecea", stroke=POS, min_w=250)
    parts.append(hc)
    parts.append(mtext(cx, 150, ["міняє стан", "нічого не повертає"],
                       size=13, color=INK, lh=1.4))
    parts.append(mtext(cx, 214, ["withdraw(200)", "save()", "shutdown()"],
                       size=13, color=POS, lh=1.5, bold=True))
    parts.append(text(cx, 312, "«зроби це»", size=13, italic=True, color=MUTED))

    # ---- правий стовп: ЗАПИТ ----
    qx = 710
    hq, hqw, hqh = box_at(qx, 96, "ЗАПИТ", size=15, bold=True,
                          fill="#eaf0fd", stroke=NEG, min_w=250)
    parts.append(hq)
    parts.append(mtext(qx, 150, ["повертає значення", "стан не чіпає"],
                       size=13, color=INK, lh=1.4))
    parts.append(mtext(qx, 214, ["balance()", "isEmpty()", "size()"],
                       size=13, color=NEG, lh=1.5, bold=True))
    parts.append(text(qx, 312, "«скажи мені»", size=13, italic=True, color=MUTED))

    # ---- середина: заборонений гібрид ----
    # «НІ»-значок ЛІВОРУЧ від рамки (кружок із діагоналлю), сам напис — чистий,
    # жодна лінія не перетинає текст (svgcheck v6).
    mx = W / 2
    gy = 372
    bx = 250          # центр значка-заборони, лівіше за рамку
    parts.append(circle(bx, gy, 22, fill="#fdecea", stroke=POS, sw=3))
    parts.append(line(bx - 15, gy + 15, bx + 15, gy - 15, color=POS, sw=3))
    g, gw, gh = box_at(mx + 40, gy,
                       ["один метод, що й повертає,",
                        "і потайки міняє стан"],
                       size=13, bold=True, fill=FILL, stroke=MUTED, min_w=420)
    parts.append(g)
    parts.append(text(W / 2, 448, "питання не має міняти відповідь",
                      size=13, italic=True, color=INK))

    render(os.path.join(IMG, "two-kinds.svg"), W, H, *parts)


# ── Фігура 2: прихований побічний ефект у запиті ламає безпечну перестановку ──
def hidden_effect():
    W, H = 1060, 560
    parts = []
    parts.append(text(W / 2, 34, "Запит із прихованою зміною: ту саму дію двічі — різні відповіді",
                      size=17, bold=True))

    # два сценарії поруч: чистий запит (можна кликати вільно) і брудний
    # ── ЛІВОРУЧ: чистий запит ──
    lx = 270
    parts.append(text(lx, 82, "ЧИСТИЙ ЗАПИТ", size=14, bold=True, color=NEG))
    steps_ok = [
        ("nextId()", "→ 7"),
        ("nextId()", "→ 7"),
        ("nextId()", "→ 7"),
    ]
    y = 128
    for call, res in steps_ok:
        b, bw, bh = box_at(lx - 60, y, call, size=13, fill="#eaf0fd", stroke=NEG, min_w=180)
        parts.append(b)
        parts.append(text(lx + 90, y + 5, res, size=14, bold=True, color=NEG, anchor="start"))
        y += 62
    parts.append(mtext(lx, y + 8, ["та сама відповідь щоразу —", "клич скільки хоч, у будь-якому порядку"],
                       size=12.5, color=MUTED, lh=1.4))

    # роздільник
    parts.append(line(W / 2, 70, W / 2, H - 120, color=MUTED, sw=1, dash="6 6"))

    # ── ПРАВОРУЧ: брудний запит (тихо інкрементує) ──
    rx = 800
    parts.append(text(rx, 82, "ЗАПИТ, ЩО ТИХО МІНЯЄ", size=14, bold=True, color=POS))
    steps_bad = [
        ("nextId()", "→ 7"),
        ("nextId()", "→ 8"),
        ("nextId()", "→ 9"),
    ]
    y = 128
    for call, res in steps_bad:
        b, bw, bh = box_at(rx - 60, y, call, size=13, fill="#fdecea", stroke=POS, min_w=180)
        parts.append(b)
        parts.append(text(rx + 90, y + 5, res, size=14, bold=True, color=POS, anchor="start"))
        y += 62
    parts.append(mtext(rx, y + 8, ["кожен виклик посуває лічильник —", "порядок і кількість тепер важать"],
                       size=12.5, color=MUTED, lh=1.4))

    # висновок унизу
    parts.append(text(W / 2, H - 74,
                      "зайвий журнал-запит, кеш, повтор після збою — усе це переставляє й дублює виклики",
                      size=13, color=INK))
    parts.append(text(W / 2, H - 44,
                      "поки запит нічого не міняє — це безпечно; щойно міняє — тихо ламається",
                      size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "hidden-effect.svg"), W, H, *parts)


# ── Фігура 3: що купуєш поділом — три властивості запиту ───────────────────────
def what_you_buy():
    W, H = 1000, 430
    parts = []
    parts.append(text(W / 2, 34, "Що дає поділ: запит стає безпечним, команда лишається однією точкою зміни",
                      size=16, bold=True))

    # три плитки-властивості запиту
    props = [
        (200, "переставляй", ["виклики запитів", "у будь-якому", "порядку"]),
        (500, "повторюй", ["клич той самий", "запит скільки хоч —", "відповідь та сама"]),
        (800, "кешуй", ["запам'ятай раз,", "віддавай багато —", "нічого не зіпсуєш"]),
    ]
    for px, title, body in props:
        hb, hbw, hbh = box_at(px, 110, title, size=14, bold=True,
                              fill="#eaf0fd", stroke=NEG, min_w=230)
        parts.append(hb)
        parts.append(mtext(px, 165, body, size=12.5, color=INK, lh=1.4))

    # спільна умова під ними
    parts.append(line(120, 250, W - 120, 250, color=MUTED, sw=1, dash="5 5"))
    parts.append(text(W / 2, 285, "усе це чинне рівно доти, доки запит НІЧОГО не міняє",
                      size=13.5, bold=True, color=NEG))

    # команда — окремим рядком
    cb, cbw, cbh = box_at(W / 2, 350,
                          ["КОМАНДА — навпаки: жодної з цих вольностей.",
                           "Зате зміна стану зібрана в одну точку, а не розлита по запитах."],
                          size=13, bold=True, fill="#fdecea", stroke=POS, min_w=760)
    parts.append(cb)

    render(os.path.join(IMG, "what-you-buy.svg"), W, H, *parts)


# ── Фігура 4 (вставка proj): лінивий кеш прийнятний / зіпсований кеш — баг ─────
def lazy_vs_buggy():
    W, H = 1080, 560
    parts = []
    parts.append(text(W / 2, 34,
                      "Той самий «get», а різниця вирішальна: чи зсуває виклик відповідь",
                      size=17, bold=True))

    # роздільник посередині
    parts.append(line(W / 2, 66, W / 2, H - 118, color=MUTED, sw=1, dash="6 6"))

    # ── ЛІВОРУЧ: лінивий кеш — усі виклики бачать одне ──
    lx = 270
    parts.append(text(lx, 88, "ЛІНИВИЙ КЕШ — прийнятно", size=14, bold=True, color=NEG))
    steps_ok = [
        ("getConfig()", "→ A", "перший: читає з диска"),
        ("getConfig()", "→ A", "віддає кеш"),
        ("getConfig()", "→ A", "віддає кеш"),
    ]
    y = 138
    for call, res, note in steps_ok:
        b, bw, bh = box_at(lx - 70, y, call, size=13, fill="#eaf0fd", stroke=NEG, min_w=190)
        parts.append(b)
        parts.append(text(lx + 78, y + 5, res, size=15, bold=True, color=NEG, anchor="start"))
        parts.append(text(lx, y + 34, note, size=11, color=MUTED))
        y += 76
    parts.append(mtext(lx, y + 6,
                       ["та сама відповідь щоразу —", "викликач різниці НЕ бачить"],
                       size=12.5, color=INK, lh=1.4, bold=True))

    # ── ПРАВОРУЧ: зіпсований кеш — відповідь зсувається ──
    rx = 810
    parts.append(text(rx, 88, "КЕШ ІЗ МІТКОЮ ЧАСУ — баг", size=14, bold=True, color=POS))
    steps_bad = [
        ("getConfig()", "→ A₁", "домішує lastAccess"),
        ("getConfig()", "→ A₂", "інша мітка часу"),
        ("getConfig()", "→ A₃", "знову інша"),
    ]
    y = 138
    for call, res, note in steps_bad:
        b, bw, bh = box_at(rx - 70, y, call, size=13, fill="#fdecea", stroke=POS, min_w=190)
        parts.append(b)
        parts.append(text(rx + 78, y + 5, res, size=15, bold=True, color=POS, anchor="start"))
        parts.append(text(rx, y + 34, note, size=11, color=MUTED))
        y += 76
    parts.append(mtext(rx, y + 6,
                       ["кожен виклик зсуває відповідь —", "ефект тече в результат: розчепи"],
                       size=12.5, color=INK, lh=1.4, bold=True))

    # висновок унизу
    parts.append(text(W / 2, H - 68,
                      "межа не «чи є присвоєння», а «чи зсуває виклик наступну відповідь»",
                      size=13.5, color=INK))
    parts.append(text(W / 2, H - 40,
                      "невидима зміна — лишай; зміна, що тече у відповідь, — прихована команда",
                      size=13.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "lazy-vs-buggy.svg"), W, H, *parts)


if __name__ == "__main__":
    two_kinds()
    hidden_effect()
    what_you_buy()
    lazy_vs_buggy()
    print("figures written to", IMG)
