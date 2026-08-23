# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

VAL_FILL = "#e9f7ef"   # світло-зелений — об'єкт-значення
ENT_FILL = "#eef4ff"   # світло-синій  — сутність


# ── Фігура 1: іменники DH → сутності проти об'єктів-значень ──────────────────
def fig_entity_value_sort():
    W, H = 900, 520
    frags = []

    div_x = 452
    frags.append(line(div_x, 92, div_x, 452, color=MUTED, sw=1.3, dash="5 6"))

    # Ліва колонка — сутності
    lcx = 232
    frags.append(text(lcx, 74, "Сутності", size=18, bold=True, color=NEG))
    frags.append(text(lcx, 96, "тотожність — стежимо крізь зміни", size=12, color=MUTED))
    entities = ["Дім", "Кімната", "Пристрій (замок)", "Власник"]
    ey = 148
    for label in entities:
        body, w, h = textbox(lcx, ey, label, size=15, bold=True, pad=13,
                             fill=ENT_FILL, stroke=NEG, sw=2, min_w=250)
        frags.append(body)
        ey += 74
    frags.append(text(lcx, 476, "два однакові — усе одно різні речі",
                      size=12, italic=True, color=NEG))

    # Права колонка — об'єкти-значення
    rcx = 672
    frags.append(text(rcx, 74, "Об'єкти-значення", size=18, bold=True, color=FIELD))
    frags.append(text(rcx, 96, "вміст — визначає повністю", size=12, color=MUTED))
    values = ["Вимір  20.1 °C", "Поріг опалення", "Стан замка", "DeviceId", "Локація «кухня»"]
    vy = 132
    for label in values:
        body, w, h = textbox(rcx, vy, label, size=15, pad=12,
                             fill=VAL_FILL, stroke=FIELD, sw=2, min_w=230)
        frags.append(body)
        vy += 64
    frags.append(text(rcx, 476, "два однакові — те саме, взаємозамінні",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, 'entity-value-sort.svg'), W, H, *frags,
           title="Іменники дому, розкладені на два роди")


# ── Фігура 2: межа агрегата — великий Home проти малих агрегатів ─────────────
def fig_aggregate_boundaries():
    W, H = 980, 560
    frags = []

    # ЛІВОРУЧ: спокуса — один великий Home
    frags.append(text(240, 74, "Спокуса: один великий Home", size=16, bold=True, color=POS))
    lx, ly, lw, lh = 66, 100, 350, 350
    frags.append(rect(lx, ly, lw, lh, fill="#fdf0ee", stroke=POS, sw=2.4, rx=18))

    root, rw, rh = textbox(lx + lw / 2, ly + 56, "КОРІНЬ: Home", size=15, bold=True,
                           pad=13, fill="#fdecea", stroke=POS, sw=2.2, min_w=180)
    frags.append(root)
    inner = [("Кімнати ×N", lx + 108, ly + 178),
             ("Замки й пристрої ×N", lx + lw / 2 + 20, ly + 272)]
    for lab, cx, cy in inner:
        b, bw, bh = textbox(cx, cy, lab, size=13, pad=11, fill=FILL, stroke=MUTED, sw=1.5)
        frags.append(b)
        frags.append(arrow(lx + lw / 2, ly + 56 + rh / 2, cx, cy - bh / 2 - 4,
                           color=MUTED, sw=1.5))
    frags.append(text(lx + lw / 2, ly + lh + 30, "будь-яка зміна тягне весь дім",
                      size=13, bold=True, color=POS))

    # ПРАВОРУЧ: розкрій — малі агрегати + посилання за id
    frags.append(text(730, 74, "Розкрій: малі агрегати + id", size=16, bold=True, color=NEG))

    # маленький Home
    hcx, hcy = 610, 250
    hb, hbw, hbh = textbox(hcx, hcy, ["Home", "режим · кімнати · члени"],
                           size=14, bold=True, pad=13, fill="#fdecea", stroke=POS,
                           sw=2.2, min_w=190)
    frags.append(rect(hcx - hbw / 2 - 16, hcy - hbh / 2 - 30, hbw + 32, hbh + 46,
                      fill="#eef4ff", stroke=NEG, sw=2.2, rx=14))
    frags.append(hb)

    # два пристрої-агрегати
    dev = [("Замок", "інваріант усередині", 866, 150),
           ("Термостат", "свій корінь", 866, 350)]
    for name, sub, cx, cy in dev:
        b, bw, bh = textbox(cx, cy, [name, sub], size=13, bold=True, pad=12,
                            fill="#fdecea", stroke=POS, sw=2, min_w=170)
        frags.append(rect(cx - bw / 2 - 14, cy - bh / 2 - 14, bw + 28, bh + 28,
                          fill="#eef4ff", stroke=NEG, sw=2, rx=12))
        frags.append(b)
        # тонка стрілка за id
        ax1, ay1 = hcx + hbw / 2 + 18, hcy
        ax2, ay2 = cx - bw / 2 - 16, cy
        frags.append(arrow(ax1, ay1, ax2, ay2, color=INK, sw=1.4))
        # підпис deviceId — ЗБОКУ від лінії (перпендикулярний відступ), а не НА ній
        dx, dy = ax2 - ax1, ay2 - ay1
        seglen = (dx * dx + dy * dy) ** 0.5
        px, py = -dy / seglen, dx / seglen          # одиничний перпендикуляр
        # відступ назовні (від центральної осі hcy), щоб два підписи розійшлися одне від одного
        outward = -1 if py * (cy - hcy) < 0 else 1
        off = 34 * outward
        lx, ly = ax1 + dx * 0.42 + px * off, ay1 + dy * 0.42 + py * off
        frags.append(text(lx, ly, "deviceId", size=12, bold=True, color=INK))
    frags.append(text(736, 496, "кожна зміна локальна · своя транзакція",
                      size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, 'aggregate-boundaries.svg'), W, H, *frags,
           title="Де провести межу агрегата дому")


# ── Фігура 3: «нікого немає» — бажане проти справжнього, зведення з часом ────
def fig_away_eventual():
    W, H = 960, 470
    frags = []

    # Дім із бажаним режимом
    hcx, hcy = 175, 230
    hb, hbw, hbh = textbox(hcx, hcy, ["Дім", "бажаний режим:", "«нікого немає»"],
                           size=15, bold=True, pad=15, fill=ENT_FILL, stroke=NEG,
                           sw=2.2, min_w=210)
    frags.append(hb)
    frags.append(text(hcx, hcy + hbh / 2 + 26, "хочу: усі замкнені", size=12,
                      italic=True, color=MUTED))

    # три замки праворуч
    locks = [("Замок · гараж", "Locked  ✓", FIELD, VAL_FILL, 700, 96),
             ("Замок · вхід", "Locked  ✓", FIELD, VAL_FILL, 700, 226),
             ("Замок · чорний хід", "OFFLINE · Unlocked", POS, "#fdf0ee", 700, 356)]
    for name, state, col, fill, cx, cy in locks:
        b, bw, bh = textbox(cx, cy, [name, state], size=14, bold=True, pad=13,
                            fill=fill, stroke=col, sw=2.1, min_w=250)
        frags.append(b)
        frags.append(arrow(hcx + hbw / 2 + 12, hcy + (cy - hcy) * 0.10,
                           cx - bw / 2 - 8, cy, color=MUTED, sw=1.5))

    frags.append(text(410, 122, "команда «замкнись»", size=12, bold=True, color=INK))
    # чесний розрив для офлайн-замка
    frags.append(text(700, 402, "наздоженемо, щойно з'явиться", size=12,
                      italic=True, color=POS))

    frags.append(text(W / 2, 448,
                      "розрив «хочу» проти «є» — не баг, а чесна модель фізичного світу",
                      size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, 'away-eventual.svg'), W, H, *frags,
           title="«Нікого немає»: бажане й справжнє зводяться з часом")


# ── Фігура 4: цикл зведення — бажане доганяє справжнє за проходи ─────────────
def fig_reconcile_loop():
    W, H = 980, 620
    frags = []

    # Панель А — цикл зведення (не транзакція)
    frags.append(text(W / 2, 52,
                      "Цикл зведення: бажане → команда → правда з поля → звіт → повтори",
                      size=15, bold=True, color=MUTED))

    D, dw, dh = textbox(150, 130, ["Дім", "бажаю: Away"], size=14, bold=True, pad=13,
                        fill=ENT_FILL, stroke=NEG, sw=2.2, min_w=170)
    C, cw, ch = textbox(430, 130, ["Хаб → замкам", "«замкнись»"], size=13, pad=13,
                        fill=FILL, stroke=INK, sw=1.8, min_w=210)
    O, ow, oh = textbox(760, 130, ["Відповідь заліза:", "Locked / Offline / Jammed"], size=13,
                        pad=13, fill=FILL, stroke=INK, sw=1.8, min_w=250)
    R, rw, rh = textbox(760, 250, ["Онови справжнє", "+ чесний звіт"], size=13, pad=13,
                        fill=VAL_FILL, stroke=FIELD, sw=2, min_w=250)
    for b in (D, C, O, R):
        frags.append(b)

    frags.append(arrow(150 + dw / 2, 130, 430 - cw / 2 - 6, 130, color=INK, sw=1.6))   # D→C
    frags.append(arrow(430 + cw / 2, 130, 760 - ow / 2 - 6, 130, color=INK, sw=1.6))   # C→O
    frags.append(arrow(760, 130 + oh / 2, 760, 250 - rh / 2 - 6, color=INK, sw=1.6))   # O→R
    # повтір: R униз, ліворуч, угору в C
    frags.append(line(760, 250 + rh / 2, 760, 322, color=POS, sw=1.6))
    frags.append(line(760, 322, 430, 322, color=POS, sw=1.6))
    frags.append(arrow(430, 322, 430, 130 + ch / 2 + 4, color=POS, sw=1.6))
    frags.append(text(595, 342, "повтори для офлайн — доки розрив не зникне",
                      size=12, bold=True, color=POS))

    # Панель Б — два проходи в часі
    frags.append(line(60, 374, W - 60, 374, color=MUTED, sw=1.2, dash="4 6"))
    frags.append(text(W / 2, 402, "Два проходи в часі: розрив тане, а не зникає транзакцією",
                      size=15, bold=True, color=MUTED))

    s1, s1w, s1h = textbox(240, 470, ["Прохід 1", "9 / 10 замкнено", "зведено: ні"],
                           size=14, bold=True, pad=14, fill=FILL, stroke=INK, sw=1.8, min_w=230)
    s2, s2w, s2h = textbox(740, 470, ["Прохід 2", "10 / 10 замкнено", "зведено: так"],
                           size=14, bold=True, pad=14, fill=VAL_FILL, stroke=FIELD, sw=2, min_w=230)
    frags.append(s1)
    frags.append(s2)

    # стрілка «згодом» між картками
    frags.append(arrow(240 + s1w / 2 + 10, 470, 740 - s2w / 2 - 10, 470, color=INK, sw=1.6))
    frags.append(text(490, 450, "гараж повернувся на зв'язок", size=12, bold=True, color=INK))

    # ряди точок: 9 зелених + 1 червона (гараж) → усі 10 зелених
    g, dotr = 28, 8
    row_y1 = 470 + s1h / 2 + 32
    for i in range(10):
        red = (i == 2)
        frags.append(circle(240 - 9 * g / 2 + i * g, row_y1, dotr,
                            fill=("#fdecea" if red else "#e9f7ef"),
                            stroke=(POS if red else FIELD), sw=2))
    frags.append(text(240, row_y1 + 30, "офлайн: garage", size=12, italic=True, color=POS))

    row_y2 = 470 + s2h / 2 + 32
    for i in range(10):
        frags.append(circle(740 - 9 * g / 2 + i * g, row_y2, dotr,
                            fill="#e9f7ef", stroke=FIELD, sw=2))
    frags.append(text(740, row_y2 + 30, "усі двері замкнені", size=12, italic=True, color=FIELD))

    render(os.path.join(IMG, 'reconcile-loop.svg'), W, H, *frags,
           title="Зведення «нікого немає»: розрив закривається проходами, не транзакцією")


if __name__ == "__main__":
    fig_entity_value_sort()
    fig_aggregate_boundaries()
    fig_away_eventual()
    fig_reconcile_loop()
    print("figures written to", IMG)
