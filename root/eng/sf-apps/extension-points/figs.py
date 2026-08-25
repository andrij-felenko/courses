# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def inner_vs_outer():
    """Дві межі поруч: внутрішня (обидва боки твої, збираються разом, одне репо)
    проти зовнішньої (по той бік — чужі, окремі релізи, контракт заморожений).
    Широкі колонки й окремі рядки-властивості, щоб написи не накладалися."""
    W, H = 900, 470
    f = []

    # ── ліва панель: ВНУТРІШНЯ межа ──
    lx = 30
    panel_w = 400
    f.append(rect(lx, 60, panel_w, 380, fill="#f7f9fb", stroke=MUTED, sw=1.4, rx=12))
    f.append(text(lx + panel_w / 2, 90, "Внутрішня межа", size=18, bold=True))
    f.append(text(lx + panel_w / 2, 112, "модуль за інтерфейсом", size=12, color=MUTED, italic=True))

    # твій-твій: два блоки і тонка риса між ними
    ycore = 175
    bw, bh = 150, 64
    f.append(rect(lx + 30, ycore, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    f.append(text(lx + 30 + bw / 2, ycore + 30, "твоє ядро", size=13.5, bold=True))
    f.append(text(lx + 30 + bw / 2, ycore + 50, "твоє репо", size=11, color=MUTED))
    f.append(rect(lx + panel_w - 30 - bw, ycore, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    f.append(text(lx + panel_w - 30 - bw / 2, ycore + 30, "твій модуль", size=13.5, bold=True))
    f.append(text(lx + panel_w - 30 - bw / 2, ycore + 50, "те саме репо", size=11, color=MUTED))
    # межа-риса
    mid = lx + panel_w / 2
    f.append(line(mid, ycore - 8, mid, ycore + bh + 8, color=INK, sw=1.6, dash="4 4"))
    f.append(line(lx + 30 + bw, ycore + bh / 2, lx + panel_w - 30 - bw, ycore + bh / 2, color=INK, sw=1.6))

    props_in = [
        "обидва боки — твої",
        "збираються разом",
        "зламав межу — полагодив сам",
        "міняй будь-коли",
    ]
    py = 290
    for p in props_in:
        f.append(minus(lx + 30, py, r=7))  # синій — «легко/дешево»
        f.append(text(lx + 48, py + 5, p, size=13, color=INK, anchor="start"))
        py += 34

    # ── права панель: ЗОВНІШНЯ межа ──
    rx = 470
    f.append(rect(rx, 60, panel_w, 380, fill="#fffaf9", stroke=POS, sw=1.6, rx=12))
    f.append(text(rx + panel_w / 2, 90, "Зовнішня межа", size=18, bold=True, color="#a02419"))
    f.append(text(rx + panel_w / 2, 112, "точка розширення назовні", size=12, color=MUTED, italic=True))

    f.append(rect(rx + 30, ycore, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    f.append(text(rx + 30 + bw / 2, ycore + 30, "твій продукт", size=13.5, bold=True))
    f.append(text(rx + 30 + bw / 2, ycore + 50, "твоє репо", size=11, color=MUTED))
    f.append(rect(rx + panel_w - 30 - bw, ycore, bw, bh, fill="#fdecea", stroke=POS, sw=2, rx=8))
    f.append(text(rx + panel_w - 30 - bw / 2, ycore + 30, "чужий код", size=13.5, bold=True, color="#a02419"))
    f.append(text(rx + panel_w - 30 - bw / 2, ycore + 50, "не бачиш, не збираєш", size=10.5, color=MUTED))
    # заморожений публічний контракт — товста рамка-стіна посередині
    midr = rx + panel_w / 2
    f.append(rect(midr - 9, ycore - 14, 18, bh + 28, fill="#c0392b", stroke="#7d1710", sw=1.4, rx=3))
    f.append(text(midr, ycore - 24, "контракт", size=11, bold=True, color="#a02419"))
    f.append(line(lx if False else rx + 30 + bw, ycore + bh / 2, midr - 9, ycore + bh / 2, color=INK, sw=1.6))
    f.append(line(midr + 9, ycore + bh / 2, rx + panel_w - 30 - bw, ycore + bh / 2, color=POS, sw=1.6))

    props_out = [
        "по той бік — чужі, невідомі",
        "релізяться окремо, у своєму часі",
        "зламав контракт — зламав усім",
        "заморожений: майже не змінити",
    ]
    py = 290
    for p in props_out:
        f.append(plus(rx + 30, py, r=7))  # червоний — «важко/дорого»
        f.append(text(rx + 48, py + 5, p, size=13, color="#a02419", anchor="start"))
        py += 34

    return W, H, f


def four_surfaces():
    """Чотири канонічні поверхні розширення назовні навколо продукту, кожна —
    зі СВОЇМ напрямом керування (хто кого гукає / де виконується код).
    Стрілки показують напрям; підписи рознесені, щоб не перетинались."""
    W, H = 900, 560
    f = []

    cx, cy = W / 2, H / 2 + 10
    core_w, core_h = 200, 96
    # ядро-продукт у центрі
    f.append(rect(cx - core_w / 2, cy - core_h / 2, core_w, core_h,
                  fill="#eef2f7", stroke=INK, sw=2.4, rx=12))
    f.append(text(cx, cy - 8, "ТВІЙ ПРОДУКТ", size=17, bold=True))
    f.append(text(cx, cy + 16, "стабільне ядро", size=12, color=MUTED, italic=True))

    bw, bh = 250, 92

    # верх: публічний API (вони тягнуть — стрілка ЗОВНІ → продукт)
    tx, ty = cx, 78
    f.append(rect(tx - bw / 2, ty - bh / 2, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    f.append(text(tx, ty - 22, "Публічний API", size=15, bold=True, color="#1c3fa8"))
    f.append(text(tx, ty - 2, "вони питають — ти відповідаєш", size=11.5, color=MUTED))
    f.append(text(tx, ty + 18, "чужий код тягне (pull)", size=11.5, color=MUTED, italic=True))
    f.append(arrow(tx, ty + bh / 2 + 6, tx, cy - core_h / 2 - 6, color=NEG, sw=2.4))
    f.append(text(tx + 118, (ty + bh / 2 + cy - core_h / 2) / 2, "запит →", size=11, color=NEG))

    # низ: вебхуки / події (ти штовхаєш — стрілка продукт → ЗОВНІ)
    bx, by = cx, H - 78
    f.append(rect(bx - bw / 2, by - bh / 2, bw, bh, fill="#eaf6ee", stroke=FIELD, sw=2, rx=10))
    f.append(text(bx, by - 22, "Вебхуки / події", size=15, bold=True, color="#1e7a43"))
    f.append(text(bx, by - 2, "сталося щось — ти сам гукаєш їх", size=11.5, color=MUTED))
    f.append(text(bx, by + 18, "продукт штовхає (push)", size=11.5, color=MUTED, italic=True))
    f.append(arrow(bx, cy + core_h / 2 + 6, bx, by - bh / 2 - 6, color=FIELD, sw=2.4))
    f.append(text(bx + 118, (cy + core_h / 2 + by - bh / 2) / 2, "подія →", size=11, color=FIELD))

    # ліво: вбудований SDK / застосунок (їхній код виконується У ТВОЄМУ середовищі)
    lx2, ly = 165, cy
    f.append(rect(lx2 - bw / 2, ly - bh / 2, bw, bh, fill="#fdf6e3", stroke="#b9770e", sw=2, rx=10))
    f.append(text(lx2, ly - 22, "Вбудований SDK", size=15, bold=True, color="#8a5a08"))
    f.append(text(lx2, ly - 2, "їхній код живе всередині твого", size=11, color=MUTED))
    f.append(text(lx2, ly + 18, "виконується у твоєму середовищі", size=10.5, color=MUTED, italic=True))
    f.append(line(lx2 + bw / 2, ly, cx - core_w / 2, cy, color="#b9770e", sw=2.2))
    f.append(circle((lx2 + bw / 2 + cx - core_w / 2) / 2, cy, 6, fill="#fdf6e3", stroke="#b9770e", sw=2))

    # право: маркетплейс / екосистема (багато чужих авторів)
    rx2, ry = W - 165, cy
    f.append(rect(rx2 - bw / 2, ry - bh / 2, bw, bh, fill="#f3eafc", stroke="#7a3fb0", sw=2, rx=10))
    f.append(text(rx2, ry - 22, "Маркетплейс", size=15, bold=True, color="#5f2e8c"))
    f.append(text(rx2, ry - 2, "багато незнайомих авторів", size=11.5, color=MUTED))
    f.append(text(rx2, ry + 18, "екосистема поверх межі", size=11.5, color=MUTED, italic=True))
    # три «чужі» значки-автори праворуч від маркетплейсу
    for i, dy in enumerate((-24, 0, 24)):
        f.append(circle(rx2 + bw / 2 + 24, ry + dy, 7, fill="#f3eafc", stroke="#7a3fb0", sw=2))
    f.append(line(cx + core_w / 2, cy, rx2 - bw / 2, ry, color="#7a3fb0", sw=2.2))

    return W, H, f


def edge_became_product():
    """Хронологія «край продукту став самим продуктом»: чотири віхи на осі часу,
    кожна показує, яку саме зовнішню поверхню зробили головним товаром.
    Написи рознесені по вертикалі (над/під віссю почергово), щоб не накладалися."""
    W, H = 940, 560
    f = []

    # вісь часу
    axy = 300
    x0, x1 = 70, W - 40
    f.append(line(x0, axy, x1, axy, color=INK, sw=2.4))
    f.append(text(x1 - 6, axy - 12, "час →", size=12, color=MUTED, anchor="end", italic=True))

    # чотири віхи: (частка осі 0..1, рік, заголовок, поверхня, деталь, вгору?)
    milestones = [
        (0.06, "2005", "Salesforce AppExchange", "маркетплейс", "крамниця чужих застосунків;\nGA 14 січ. 2006", True),
        (0.36, "2007", "webhook (Дж. Ліндсей)", "вебхуки", "«user-defined\nHTTP callbacks»", False),
        (0.63, "2008", "Twilio", "публічний API", "дзвінки як REST-виклик;\nAPI — перший товар", True),
        (0.90, "2010", "Stripe (брати Коллісони)", "публічний API", "оплати як «встав тег\nscript»", False),
    ]

    colw = 220
    for frac, year, title, surface, detail, up in milestones:
        cx = x0 + frac * (x1 - x0)
        # точка на осі
        f.append(circle(cx, axy, 8, fill=BG, stroke=POS, sw=3))
        # рік — біля точки з протилежного боку від картки
        f.append(text(cx, axy + (34 if up else -22), year, size=15, bold=True, color="#a02419"))

        # картка з підписом — над або під віссю, з добрим відступом
        bw, bh = colw, 96
        bx = cx - bw / 2
        # тримати картку в межах полотна
        if bx < 8:
            bx = 8
        if bx + bw > W - 8:
            bx = W - 8 - bw
        by = axy - 40 - bh if up else axy + 40
        f.append(rect(bx, by, bw, bh, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
        f.append(text(bx + bw / 2, by + 24, title, size=13.5, bold=True))
        f.append(text(bx + bw / 2, by + 44, "поверхня: " + surface, size=11.5, color="#1e7a43"))
        # деталь (може бути 2 рядки)
        dl = detail.split("\n")
        for i, ln in enumerate(dl):
            f.append(text(bx + bw / 2, by + 64 + i * 15, ln, size=10.5, color=MUTED, italic=True))

        # тонкий поводок від осі до картки
        ly1 = axy - 8 if up else axy + 8
        ly2 = by + bh if up else by
        f.append(line(cx, ly1, cx, ly2, color=MUTED, sw=1.1, dash="3 3"))

    # підпис-мораль знизу
    f.append(text(W / 2, H - 18,
                  "усі троє зробили ГОЛОВНИМ товаром саме точку розширення назовні",
                  size=13, bold=True, color=INK))
    return W, H, f


def webhook_pipeline():
    """Шлях однієї доставки: подія → черга → чотири застави (підпис, ключ,
    ізольована спроба з тайм-аутом, повтор із наростанням паузи) → успіх
    або вичерпані спроби → dead-letter. Широкі клітини, підписи рознесено."""
    W, H = 940, 620
    f = []

    # ── подія зверху ──
    ex, ey = W / 2, 50
    ew, eh = 230, 56
    f.append(rect(ex - ew / 2, ey - eh / 2, ew, eh, fill="#eef2f7", stroke=INK, sw=2.2, rx=10))
    f.append(text(ex, ey - 4, "Подія сталася", size=15, bold=True))
    f.append(text(ex, ey + 16, "«нотатку створено»", size=11, color=MUTED, italic=True))

    # ── черга доставок: одна подія → багато незалежних одиниць ──
    qy = 148
    qw, qh = 320, 52
    f.append(rect(ex - qw / 2, qy - qh / 2, qw, qh, fill="#f3eafc", stroke="#7a3fb0", sw=2, rx=10))
    f.append(text(ex, qy - 3, "Черга доставки", size=14, bold=True, color="#5f2e8c"))
    f.append(text(ex, qy + 16, "по одній одиниці на підписника", size=10.5, color=MUTED))
    f.append(arrow(ex, ey + eh / 2 + 4, ex, qy - qh / 2 - 4, color=INK, sw=2.2))

    # три «одиниці-доставки» — паралельні цятки (натяк на ізоляцію в пулі)
    lane_top = qy + qh / 2 + 24
    for lx in (ex - 120, ex, ex + 120):
        f.append(circle(lx, lane_top, 6, fill="#f3eafc", stroke="#7a3fb0", sw=2))
        f.append(arrow(ex, qy + qh / 2 + 4, lx, lane_top - 6, color="#7a3fb0", sw=1.5))
    f.append(text(ex + 250, lane_top - 6, "незалежні,", size=10.5, color=MUTED, anchor="start"))
    f.append(text(ex + 250, lane_top + 10, "у пулі робітників", size=10.5, color=MUTED, anchor="start"))

    # ── чотири застави для ОДНІЄЇ доставки (середня доріжка) ──
    steps = [
        ("1 · Підпис тіла", "HMAC-SHA256 + мітка часу", "#1e7a43", "#eaf6ee", FIELD),
        ("2 · Ключ проти повтору", "той самий на всіх спробах", "#1c3fa8", "#eaf0fd", NEG),
        ("3 · Спроба з тайм-аутом", "жорсткий — мрець не висне", "#8a5a08", "#fdf6e3", "#b9770e"),
        ("4 · Повтор із паузою", "1→2→4→8… + тремтіння", "#a02419", "#fdecea", POS),
    ]
    sx = ex
    step_w, step_h = 360, 52
    sy = 248
    gap = 68
    prev_bottom = lane_top + 6
    for title, sub, tcol, fill, stroke in steps:
        f.append(arrow(sx, prev_bottom, sx, sy - step_h / 2 - 4, color=INK, sw=1.8))
        f.append(rect(sx - step_w / 2, sy - step_h / 2, step_w, step_h, fill=fill, stroke=stroke, sw=1.8, rx=9))
        f.append(text(sx, sy - 4, title, size=13.5, bold=True, color=tcol))
        f.append(text(sx, sy + 15, sub, size=10.5, color=MUTED))
        prev_bottom = sy + step_h / 2 + 4
        sy += gap

    # ── розвилка внизу: успіх / dead-letter ──
    fork_y = sy + 6
    ok_x = ex - 170
    dl_x = ex + 170
    ow, oh = 250, 54
    f.append(rect(ok_x - ow / 2, fork_y - oh / 2, ow, oh, fill="#eaf6ee", stroke=FIELD, sw=2, rx=9))
    f.append(text(ok_x, fork_y - 4, "2xx — доставлено", size=13, bold=True, color="#1e7a43"))
    f.append(text(ok_x, fork_y + 15, "одиницю завершено", size=10.5, color=MUTED))
    f.append(arrow(sx, prev_bottom, ok_x, fork_y - oh / 2 - 4, color=FIELD, sw=1.8))
    f.append(rect(dl_x - ow / 2, fork_y - oh / 2, ow, oh, fill="#fdecea", stroke=POS, sw=2, rx=9))
    f.append(text(dl_x, fork_y - 4, "спроби вичерпано", size=13, bold=True, color="#a02419"))
    f.append(text(dl_x, fork_y + 15, "→ мертві листи", size=10.5, color=MUTED))
    f.append(arrow(sx, prev_bottom, dl_x, fork_y - oh / 2 - 4, color=POS, sw=1.8))

    return W, H, f


if __name__ == "__main__":
    W, H, frags = inner_vs_outer()
    render(os.path.join(OUT, "inner-vs-outer.svg"), W, H, *frags)
    print("inner-vs-outer.svg written")

    W, H, frags = four_surfaces()
    render(os.path.join(OUT, "four-surfaces.svg"), W, H, *frags)
    print("four-surfaces.svg written")

    W, H, frags = edge_became_product()
    render(os.path.join(OUT, "edge-became-product.svg"), W, H, *frags)
    print("edge-became-product.svg written")

    W, H, frags = webhook_pipeline()
    render(os.path.join(OUT, "webhook-pipeline.svg"), W, H, *frags)
    print("webhook-pipeline.svg written")
