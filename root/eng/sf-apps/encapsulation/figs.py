# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: капсула — тверда оболонка з вузьким портом, м'які нутрощі всередині ──
def capsule():
    W, H = 760, 430
    f = []

    # Оболонка капсули (тверда межа)
    cap_x, cap_y, cap_w, cap_h = 250, 60, 380, 320
    f.append(rect(cap_x, cap_y, cap_w, cap_h, fill="#eef7f0", stroke=FIELD, sw=3, rx=22))
    f.append(text(cap_x + cap_w / 2, cap_y - 22, "капсула (об'єкт / модуль / сервіс)",
                  size=16, color=FIELD, bold=True))

    # Публічний контракт — вузька смуга-порт на межі (єдиний прохід усередину)
    port_w, port_h = 236, 40
    port_x = cap_x + (cap_w - port_w) / 2
    port_y = cap_y - port_h / 2
    f.append(rect(port_x, port_y, port_w, port_h, fill="#ffffff", stroke=INK, sw=2, rx=10))
    f.append(text(cap_x + cap_w / 2, port_y + port_h / 2 + 5,
                  "публічний контракт (вхід)", size=14, color=INK, bold=True))

    # Приховані нутрощі — три «м'які» блоки, до яких ззовні не дотягнутися
    ins = [("стан", "balance, історія"),
           ("правила", "інваріанти"),
           ("як саме", "формат, алгоритм")]
    bx = cap_x + 40
    by = cap_y + 90
    bw, bh, gap = 300, 58, 20
    for i, (a, b) in enumerate(ins):
        y = by + i * (bh + gap)
        f.append(rect(bx, y, bw, bh, fill="#fdf6ec", stroke=MUTED, sw=1.5, rx=8))
        f.append(text(bx + 16, y + bh / 2 - 4, a, size=15, color=INK, anchor="start", bold=True))
        f.append(text(bx + 16, y + bh / 2 + 16, b, size=12, color=MUTED, anchor="start"))
    f.append(text(cap_x + cap_w / 2, cap_y + cap_h - 20,
                  "приховане — деталі, що можуть змінитися", size=13, color=MUTED))

    # Клієнт зовні — говорить лише через порт
    cli_x, cli_y = 40, 150
    body, cw, ch = textbox(cli_x + 80, cli_y + 40, "клієнт\n(інший код)", size=15, bold=True,
                           fill="#eef2fb", stroke=NEG, min_w=150)
    f.append(body)
    # Дозволена стрілка: клієнт → порт
    f.append(arrow(cli_x + 158, cli_y + 40, port_x - 6, port_y + port_h / 2, color=NEG, sw=2.4))
    f.append(text((cli_x + 158 + port_x) / 2, cli_y + 18, "виклик", size=12, color=NEG))

    # Заборонений прямий доступ у нутрощі — перекреслена стрілка
    fx1, fy1 = cli_x + 158, cli_y + 96
    fx2, fy2 = bx - 6, by + bh + gap + bh / 2
    f.append(line(fx1, fy1, fx2, fy2, color=POS, sw=2.2, dash="7,6"))
    # хрестик-заборона на середині
    mx, my = (fx1 + fx2) / 2, (fy1 + fy2) / 2
    f.append(circle(mx, my, 15, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(line(mx - 8, my - 8, mx + 8, my + 8, color=POS, sw=2.6))
    f.append(line(mx - 8, my + 8, mx + 8, my - 8, color=POS, sw=2.6))
    f.append(text(mx, fy2 + 26, "прямо в нутрощі — не можна", size=12, color=POS))

    render(os.path.join(OUT, 'capsule.svg'), W, H, *f)


# ── Фігура 2: хвиля зміни — формат назовні (тече всюди) проти сховано за контрактом ──
def ripple():
    W, H = 820, 470
    f = []
    mid = W / 2

    # роздільник
    f.append(line(mid, 40, mid, H - 30, color="#d1d5db", sw=1.5, dash="4,6"))
    f.append(text(mid / 2, 34, "деталь відкрита назовні", size=16, color=POS, bold=True))
    f.append(text(mid + mid / 2, 34, "деталь схована за контрактом", size=16, color=FIELD, bold=True))

    def clients(cx_center, col_stroke, col_fill, tainted):
        ys = [90, 165, 240]
        boxes = []
        for i, y in enumerate(ys):
            fill = "#fdecea" if tainted else col_fill
            stroke = POS if tainted else col_stroke
            body, w, h = textbox(cx_center, y, "клієнт %d" % (i + 1), size=14,
                                 fill=fill, stroke=stroke, min_w=132)
            boxes.append((cx_center, y, w, h))
            f.append(body)
        return boxes

    # ── ЛІВОРУЧ: кожен клієнт зчеплений із деталлю; зміна фарбує всіх ──
    lcx = 130
    lboxes = clients(lcx, NEG, "#eef2fb", tainted=True)
    # «деталь» — вузол унизу, до якого всі тягнуться напряму
    det_body, dw, dh = textbox(lcx + 150, 370, "деталь\n(формат дати)", size=14, bold=True,
                               fill="#fdecea", stroke=POS, min_w=160)
    f.append(det_body)
    for (cx, cy, w, h) in lboxes:
        f.append(line(cx + w / 2, cy, lcx + 150 - dw / 2, 370 - dh / 2 + 8,
                      color=POS, sw=2, dash="6,5"))
    f.append(text(lcx + 60, 430, "зміна б'є в кожного", size=13, color=POS, bold=True))

    # ── ПРАВОРУЧ: клієнти знають лише контракт; зміна замкнена в капсулі ──
    rcx = mid + 110
    rboxes = clients(rcx, NEG, "#eef2fb", tainted=False)
    # контракт — стабільний фасад
    con_body, conw, conh = textbox(rcx + 165, 165, "контракт\nfmtDate()", size=14, bold=True,
                                   fill="#ffffff", stroke=INK, min_w=150)
    f.append(con_body)
    for (cx, cy, w, h) in rboxes:
        f.append(arrow(cx + w / 2, cy, rcx + 165 - conw / 2 - 4, 165, color=NEG, sw=2))
    # за контрактом — капсульована деталь, лише вона червона
    cap_body, capw, caph = textbox(rcx + 165, 370, "деталь\n(формат дати)", size=14, bold=True,
                                   fill="#fdecea", stroke=POS, min_w=160)
    f.append(cap_body)
    f.append(arrow(rcx + 165, 165 + conh / 2, rcx + 165, 370 - caph / 2, color=INK, sw=2))
    # рамка «капсула» довкола контракту+деталі
    f.append(rect(rcx + 165 - capw / 2 - 24, 165 - conh / 2 - 16,
                  capw + 48, (370 + caph / 2) - (165 - conh / 2) + 30,
                  fill="none", stroke=FIELD, sw=2, rx=14))
    f.append(text(rcx + 60, 430, "зміна замкнена всередині", size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, 'ripple.svg'), W, H, *f)


# ── Фігура 3 (hist): дві модуляризації KWIC Парнаса — за кроками vs за прихованим ──
def kwic():
    W, H = 900, 560
    f = []
    mid = W / 2

    # роздільник двох світів
    f.append(line(mid, 70, mid, H - 30, color="#d1d5db", sw=1.5, dash="4,6"))
    f.append(text(mid / 2, 40, "Різати за КРОКАМИ роботи", size=17, color=POS, bold=True))
    f.append(text(mid / 2, 62, "(як тече потік даних)", size=13, color=MUTED))
    f.append(text(mid + mid / 2, 40, "Різати за ПРИХОВАНИМИ рішеннями", size=17, color=FIELD, bold=True))
    f.append(text(mid + mid / 2, 62, "(що найімовірніше зміниться)", size=13, color=MUTED))

    # ── ЛІВОРУЧ: конвеєр кроків, кожен знає спільний формат сховища ──
    steps = ["Ввід", "Обертання рядка", "Упорядкування", "Вивід"]
    lcx = mid / 2
    ly0, lh, lgap = 100, 52, 26
    lboxes = []
    for i, s in enumerate(steps):
        y = ly0 + i * (lh + lgap)
        body, w, h = textbox(lcx, y + lh / 2, s, size=14, bold=True,
                             fill="#eef2fb", stroke=NEG, min_w=210)
        f.append(body)
        lboxes.append((lcx, y + lh / 2, w, h))
        if i > 0:
            py = ly0 + (i - 1) * (lh + lgap) + lh
            f.append(arrow(lcx, py, lcx, y, color=NEG, sw=2))

    # спільне рішення про сховище, до якого прив'язані ВСІ кроки
    dec_y = ly0 + len(steps) * (lh + lgap) + 6
    dbody, dw, dh = textbox(lcx, dec_y + 26, "рішення: рядки лежать у МАСИВІ",
                            size=13, bold=True, fill="#fdecea", stroke=POS, min_w=300)
    f.append(dbody)
    # кожен крок прив'язаний до спільного рішення через ЛІВИЙ рейл (повз усі написи)
    box_w = lboxes[0][2]
    rail_x = lcx - box_w / 2 - 24
    for (cx, cy, w, h) in lboxes:
        f.append(line(cx - w / 2, cy, rail_x, cy, color=POS, sw=1.6, dash="5,5"))
    f.append(line(rail_x, lboxes[0][1], rail_x, dec_y + 26, color=POS, sw=1.6, dash="5,5"))
    f.append(line(rail_x, dec_y + 26, lcx - dw / 2, dec_y + 26, color=POS, sw=1.6, dash="5,5"))
    f.append(text(lcx, dec_y + 70, "зміна сховища б'є в КОЖЕН крок", size=13, color=POS, bold=True))

    # ── ПРАВОРУЧ: модулі за рішеннями; сховище — окремий модуль, що ховає масив ──
    rcx = mid + mid / 2
    # Модуль «Сховище рядків» — за ним замкнене рішення про масив
    stor_y = 110
    sbody, sw, sh = textbox(rcx, stor_y, "Сховище рядків\n(ховає: масив)", size=14, bold=True,
                            fill="#eef7f0", stroke=FIELD, min_w=250)
    f.append(sbody)

    # інші модулі говорять зі сховищем лише через його контракт (get/set)
    users = ["Ввід", "Обертач", "Упорядник", "Вивід"]
    uy0, uh, ugap = 200, 48, 22
    for i, u in enumerate(users):
        y = uy0 + i * (uh + ugap)
        body, w, h = textbox(rcx, y + uh / 2, u, size=14, bold=True,
                             fill="#ffffff", stroke=INK, min_w=200)
        f.append(body)
        f.append(arrow(rcx, y - ugap + 2, rcx, y, color=INK, sw=1.6) if i > 0
                 else arrow(rcx, stor_y + sh / 2, rcx, y, color=INK, sw=1.6))
    # підпис збоку від стрілкового стовпця (праворуч), щоб лінія його не різала
    f.append(text(rcx + 118, uy0 + 4, "лише через", size=12, color=MUTED, anchor="start"))
    f.append(text(rcx + 118, uy0 + 20, "контракт", size=12, color=MUTED, anchor="start"))

    # рамка-капсула довкола сховища
    f.append(rect(rcx - sw / 2 - 16, stor_y - sh / 2 - 14, sw + 32, sh + 24,
                  fill="none", stroke=FIELD, sw=2, rx=12))
    last_y = uy0 + (len(users) - 1) * (uh + ugap) + uh
    f.append(text(rcx, last_y + 40, "зміна масиву замкнена в ОДНОМУ модулі", size=13, color=FIELD, bold=True))

    render(os.path.join(OUT, 'kwic-parnas.svg'), W, H, *f)


# ── Фігура 4 (hist): дві нитки сходяться — Парнас (рішення) + Кей (стан у об'єкті) ──
def twothreads():
    W, H = 860, 420
    f = []

    # ліва нитка — Парнас
    lx = 190
    p_body, pw, ph = textbox(lx, 90, "Девід Парнас · 1972\nПриховування ІНФОРМАЦІЇ",
                             size=15, bold=True, fill="#eef2fb", stroke=NEG, min_w=300)
    f.append(p_body)
    f.append(fitbox(lx - 170, 150, 340, 92,
                    "ховай РІШЕННЯ, що зміниться;\nмодуль знає його один,\nрешта про нього не здогадується",
                    size=13, fill="#f4f6f8", stroke=MUTED))

    # права нитка — Кей / Smalltalk
    rx = 670
    k_body, kw, kh = textbox(rx, 90, "Алан Кей · Smalltalk\nстан ЗАМКНЕНО в об'єкті",
                             size=15, bold=True, fill="#eef7f0", stroke=FIELD, min_w=300)
    f.append(k_body)
    f.append(fitbox(rx - 170, 150, 340, 92,
                    "об'єкт береже свій стан-процес;\nззовні — лише повідомлення,\nвнутрішнє приховане й захищене",
                    size=13, fill="#f4f6f8", stroke=MUTED))

    # сходяться в одну ідею
    cx, cy = W / 2, 340
    c_body, cw, ch = textbox(cx, cy, "МЕЖА: назовні — обіцянка, всередині — свобода змінити",
                             size=15, bold=True, fill="#fdf6ec", stroke=INK, min_w=560)
    f.append(c_body)
    f.append(arrow(lx, 242, cx - cw / 2 + 40, cy - ch / 2 - 4, color=NEG, sw=2.2))
    f.append(arrow(rx, 242, cx + cw / 2 - 40, cy - ch / 2 - 4, color=FIELD, sw=2.2))

    render(os.path.join(OUT, 'two-threads.svg'), W, H, *f)


if __name__ == '__main__':
    capsule()
    ripple()
    kwic()
    twothreads()
    print("ok: capsule.svg, ripple.svg, kwic-parnas.svg, two-threads.svg")
