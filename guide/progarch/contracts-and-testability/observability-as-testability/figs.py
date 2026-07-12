# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RED_TINT = "#fdecea"
BLUE_TINT = "#eaf0fd"
GREEN_TINT = "#eaf7ef"
CODE_FILL = "#eef2f7"


# ── Figure 1: два життя одного твердження ────────────────────────────────────
def fig_two_lives():
    W, H = 780, 300
    p = []
    # панелі
    p.append(rect(40, 52, 310, 212, fill=FILL, stroke=LINE, sw=1.5))
    p.append(rect(430, 52, 310, 212, fill=FILL, stroke=LINE, sw=1.5))
    # лінія деплою
    p.append(line(390, 60, 390, 250, color=MUTED, sw=1.6, dash="5 5"))
    p.append(text(390, 285, "деплой", size=13, color=MUTED))
    # ліва панель — CI
    b, _, _ = textbox(195, 80, "До релізу · CI", size=14, bold=True,
                      fill=BG, stroke=MUTED)
    p.append(b)
    b, _, _ = textbox(195, 134, 'assert apply(cmd) == "ok"', size=13,
                      fill=CODE_FILL, stroke=MUTED, color=INK)
    p.append(b)
    p.append(mtext(195, 200, ["виконується 1 раз", "на входах, що ти вигадав"],
                   size=12, color=MUTED))
    # права панель — прод
    b, _, _ = textbox(585, 80, "Після релізу · прод", size=14, bold=True,
                      fill=BG, stroke=MUTED)
    p.append(b)
    b, _, _ = textbox(585, 134, "alert: command_errors > 1%", size=13,
                      fill=RED_TINT, stroke=MUTED, color=INK)
    p.append(b)
    # пульси на живому трафіку (кола не перевіряються на накладання)
    p.append(line(452, 198, 718, 198, color=MUTED, sw=1.2))
    x = 462
    while x <= 712:
        p.append(circle(x, 198, 4, fill=FIELD, stroke=FIELD, sw=1))
        x += 25
    p.append(mtext(585, 232, ["виконується без упину", "на справжньому трафіку"],
                   size=12, color=MUTED))
    render(os.path.join(OUT, 'two-lives.svg'), W, H, *p,
           title="Два життя одного твердження")


# ── Figure 2: ті самі шви ────────────────────────────────────────────────────
def fig_seams():
    W, H = 840, 290
    p = []
    boxes = [
        (40, "запит"),
        (200, "API-межа"),
        (360, "ядро\n(домен)"),
        (520, "адаптер\nпристрою"),
        (680, "зовн.\nсервіс"),
    ]
    bw, by, bh = 120, 74, 52
    for bx, label in boxes:
        p.append(fitbox(bx, by, bw, bh, label, size=14, bold=False,
                        fill=FILL, stroke=LINE))
    yc = by + bh / 2
    # стрілки потоку запиту між боксами
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + bw
        x2 = boxes[i + 1][0]
        p.append(arrow(x1, yc, x2, yc, color=LINE, sw=1.8))
    # шви з подвійним підписом (внутрішні межі)
    for gx in (340, 500, 660):
        p.append(line(gx, 132, gx, 158, color=FIELD, sw=1.4, dash="4 4"))
        b, _, _ = textbox(gx, 188, "CI: дублер\nпрод: сигнал", size=11,
                          fill=GREEN_TINT, stroke=FIELD, color=INK)
        p.append(b)
    render(os.path.join(OUT, 'seams.svg'), W, H, *p,
           title="Ті самі шви: у тесті — дублер, у проді — сигнал")


# ── Figure 3: бюджет помилок згорає ──────────────────────────────────────────
def fig_budget_burn():
    W, H = 780, 300
    p = []
    # осі
    p.append(line(90, 60, 90, 250, color=LINE, sw=1.5))
    p.append(line(90, 250, 720, 250, color=LINE, sw=1.5))
    p.append(text(80, 76, "43 хв", size=12, color=MUTED, anchor="end"))
    p.append(text(80, 253, "0", size=12, color=MUTED, anchor="end"))
    p.append(text(150, 272, "початок місяця", size=11, color=MUTED))
    p.append(text(670, 272, "кінець", size=11, color=MUTED))
    # східчаста лінія згоряння бюджету
    pts = [(90, 72), (230, 72), (230, 118), (400, 118),
           (400, 150), (540, 150)]
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=INK, sw=2.2))
    # великий обрив — поганий деплій (червоним)
    p.append(line(540, 150, 540, 242, color=POS, sw=2.6))
    p.append(line(540, 242, 690, 242, color=INK, sw=2.2))
    p.append(circle(540, 242, 4.5, fill=POS, stroke=POS, sw=1))
    # підписи в порожніх зонах (не перетнуті лінією)
    p.append(text(175, 168, "штатна робота", size=12, color=MUTED))
    p.append(mtext(628, 108, ["поганий деплій", "−45 хв за раз"],
                   size=12, color=POS))
    p.append(mtext(612, 205, ["бюджет вичерпано", "→ стоп фічам"],
                   size=12, color=INK))
    render(os.path.join(OUT, 'budget-burn.svg'), W, H, *p,
           title="Бюджет помилок згорає: 99.9% ≈ 43 хв на місяць")


# ── Figure 4: один ендпоінт → пʼять сигналів, кожен = тест ────────────────────
def fig_signals_as_tests():
    W, H = 940, 470
    p = []
    # підзаголовки колонок
    p.append(text(465, 48, "сигнал у проді", size=13, color=MUTED))
    p.append(text(775, 48, "тест, який він заміняє", size=13, color=MUTED))
    # ендпоінт-хендлер
    p.append(fitbox(40, 175, 150, 120,
                    "один ендпоінт\nPOST /devices\n/{id}/commands",
                    size=13, bold=True, fill=CODE_FILL, stroke=LINE))
    p.append(arrow(18, 235, 40, 235, color=MUTED, sw=1.6))
    p.append(text(29, 226, "запит", size=11, color=MUTED))
    rows = [78, 154, 230, 306, 382]
    signals = [
        "структурована\nподія",
        "лічильник\nR + E",
        "гістограма D\n→ p99",
        "лічильник\nінваріанта",
        "readiness\n/readyz",
    ]
    twins = [
        "приклад-тест\nвхід → вихід",
        "assert, що\nрахує провали",
        "властивість\nна популяції",
        "assert 0..100\nу проді",
        "передумова\n(setUp, smoke)",
    ]
    for cy, sig, tw in zip(rows, signals, twins):
        p.append(arrow(190, 235, 360, cy, color=MUTED, sw=1.5))
        p.append(fitbox(360, cy - 28, 210, 56, sig, size=13,
                        fill=FILL, stroke=LINE))
        p.append(text(610, cy + 6, "↔", size=20, color=MUTED))
        p.append(fitbox(650, cy - 28, 250, 56, tw, size=13,
                        fill=GREEN_TINT, stroke=FIELD))
    render(os.path.join(OUT, 'signals-as-tests.svg'), W, H, *p,
           title="Кожен сигнал — це тест, що не спиняється")


# ── Figure 5: мітка device_id — бомба кардинальності ─────────────────────────
def fig_cardinality():
    W, H = 880, 380
    p = []
    # ліва панель — обмежені мітки
    p.append(rect(40, 70, 360, 260, fill=BG, stroke=FIELD, sw=1.8))
    p.append(text(220, 100, "{command, outcome}", size=14, bold=True, color=INK))
    p.append(text(220, 124, "обмежені множини", size=12, color=MUTED))
    for cx in (140, 185, 230, 275, 320):
        for cy in (165, 200, 235):
            p.append(circle(cx, cy, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(220, 300, "≈ десятки серій", size=13, bold=True, color=FIELD))
    p.append(text(220, 320, "дешево й назавжди", size=11, color=MUTED))
    # права панель — device як мітка
    p.append(rect(460, 70, 380, 260, fill=RED_TINT, stroke=POS, sw=1.8))
    p.append(text(650, 100, "{command, outcome, device}", size=14, bold=True, color=INK))
    p.append(text(650, 124, "device_id — без меж", size=12, color=POS))
    cx = 490
    while cx <= 810:
        cy = 150
        while cy <= 268:
            p.append(circle(cx, cy, 2.5, fill=POS, stroke=POS, sw=0.6))
            cy += 18
        cx += 20
    p.append(text(650, 300, "серій: мільйони", size=14, bold=True, color=POS))
    p.append(text(650, 320, "Prometheus падає (OOM)", size=11, color=POS))
    render(os.path.join(OUT, 'cardinality.svg'), W, H, *p,
           title="Мітка device_id — це бомба кардинальності")


# ── Figure 6: подорож слова «спостережність» (для hist-вставки) ──────────────
def fig_term_journey():
    W, H = 960, 360
    p = []
    # ── ліва панель: теорія керування ────────────────────────────────
    p.append(rect(40, 64, 300, 258, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(190, 96, "Теорія керування", size=15, bold=True))
    p.append(text(190, 124, "1960 · IFAC, Москва", size=13, color=MUTED))
    p.append(text(190, 152, "Рудольф Кальман", size=14, bold=True))
    p.append(fitbox(58, 178, 264, 116,
                    "система СПОСТЕРЕЖНА,\nякщо її внутрішній стан\nвідновлюється лише\nз того, що вона\nвидає назовні",
                    size=12, fill=BLUE_TINT, stroke=MUTED))
    # ── стрілка запозичення через прірву ─────────────────────────────
    p.append(arrow(345, 193, 555, 193, sw=2.2))
    p.append(mtext(450, 150, ["позичено", "через ≈ пів століття"],
                   size=12, color=INK))
    p.append(text(450, 216, "(2010-ті)", size=12, color=MUTED))
    # ── права панель: розробка софту ─────────────────────────────────
    p.append(rect(560, 64, 360, 258, fill=BG, stroke=LINE, sw=1.6))
    p.append(text(740, 96, "Розробка софту", size=15, bold=True))
    rows = [
        (134, "2013 — Twitter: команда «Observability»"),
        (174, "2016 — Honeycomb: поняття ≠ моніторинг"),
        (214, "2017–18 — гасло «три стовпи»"),
        (254, "~2020 — бунт: широкі події vs метрики"),
    ]
    for y, s in rows:
        p.append(circle(582, y - 4, 4, fill=FIELD, stroke=FIELD, sw=1))
        p.append(text(596, y, s, size=12, color=INK, anchor="start"))
    render(os.path.join(OUT, 'term-journey.svg'), W, H, *p,
           title="Спостережність: із теорії керування — в розподілені системи")


if __name__ == '__main__':
    fig_two_lives()
    fig_seams()
    fig_budget_burn()
    fig_signals_as_tests()
    fig_cardinality()
    fig_term_journey()
    print("ok")
