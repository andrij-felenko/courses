# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"
AMBER_D = "#b06d0a"


# ── Фігура 1: гарячий шлях до і після кешу (розвантаження джерела) ────────────
def fig_offload():
    W, H = 1140, 470
    f = []

    # ── лан «Без кешу» ──
    f.append(text(70, 92, "Без кешу", size=15, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 120, 160, 62, "застосунок\n(мобільний)", size=13, fill=BG, stroke=INK))
    f.append(arrow(224, 151, 700, 151, color=INK, sw=2.4))
    f.append(text(462, 135, "6 000 читань/с", size=14, color=INK, bold=True))
    f.append(text(462, 173, "агрегат «дім»: home + device", size=12, color=MUTED))
    f.append(fitbox(706, 116, 320, 72, "сховище DH v3\n(реляційне)", size=14, bold=True,
                    fill=AMBER_T, stroke=AMBER_D))
    f.append(text(866, 210, "70% CPU · p99 повзе вгору", size=12, color=POS, bold=True))

    # ── лан «З першим кешем» ──
    f.append(text(70, 287, "З першим кешем", size=15, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 300, 160, 62, "застосунок", size=13, fill=BG, stroke=INK))
    f.append(arrow(224, 331, 360, 331, color=INK, sw=2.4))
    f.append(text(292, 315, "6 000/с", size=12, color=INK, bold=True))
    f.append(fitbox(366, 296, 270, 72, "кеш у процесі\ncache-aside · TTL 5 хв", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(arrow(642, 331, 806, 331, color=MUTED, sw=2))
    f.append(text(724, 315, "~100/с (промахи)", size=12, color=MUTED))
    f.append(fitbox(812, 300, 268, 62, "сховище DH v3\nспокійне", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))

    # ── підсумковий рядок ──
    f.append(fitbox(60, 400, 1020, 46,
                    "Влучність ≈ 98%: копію читає 5 900 звернень/с, база бачить ~100. "
                    "TTL — прямий регулятор: коротший — свіжіше, довший — легше базі.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "cache-offload.svg"), W, H, *f)


# ── Фігура 2: який зріз читання кешувати ──────────────────────────────────────
def fig_which_slice():
    W, H = 1080, 580
    f = []

    f.append(fitbox(390, 44, 300, 56, "читання «покажи мій дім»", size=14, bold=True,
                    fill=BLUE_T, stroke=NEG))
    f.append(arrow(500, 104, 336, 152, color=INK, sw=2))
    f.append(arrow(580, 104, 744, 152, color=INK, sw=2))

    # ── ліва колонка: реєстр і конфіг → кешувати ──
    f.append(fitbox(120, 156, 360, 54, "Реєстр і конфіг", size=15, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(mtext(300, 250, "• список пристроїв\n• назви й кімнати\n• тариф, поріг опалення",
                   size=13, color=INK, lh=1.45))
    f.append(text(300, 344, "міняється ~раз на день", size=13, color=MUTED, bold=True))
    f.append(fitbox(120, 368, 360, 110,
                    "КЕШУВАТИ\ncache-aside · TTL 5 хв\nскид копії на запис",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))

    # ── права колонка: живий стан → не кешувати ──
    f.append(fitbox(600, 156, 360, 54, "Живий стан пристрою", size=15, bold=True,
                    fill=AMBER_T, stroke=AMBER_D))
    f.append(mtext(780, 250, "• увімкнено / вимкнено\n• поточна температура",
                   size=13, color=INK, lh=1.45))
    f.append(text(780, 344, "міняється щосекунди", size=13, color=MUTED, bold=True))
    f.append(fitbox(600, 368, 360, 110,
                    "НЕ кешувати\nчитати наживо з джерела\n(гейт 3: нуль несвіжості)",
                    size=14, bold=True, fill=RED_T, stroke=POS))

    f.append(fitbox(120, 504, 840, 50,
                    "Перший кеш бере лише ПОВІЛЬНИЙ зріз; швидкий зріз обходить кеш — "
                    "тому копія і безпечна, і вигідна.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "which-slice.svg"), W, H, *f)


# ── Фігура 3: обрив одного процесу (де ламається скид-на-запис) ───────────────
def fig_single_instance_cliff():
    W, H = 1160, 500
    f = []

    # роздільник між сценаріями
    f.append(line(580, 40, 580, 384, color=MUTED, sw=1.4, dash="5 5"))

    # ── ліворуч: один процес — скид долітає ──
    f.append(text(300, 56, "Один процес — скид долітає", size=15, color=INK, bold=True))
    f.append(rect(80, 84, 400, 214, fill=FILL, stroke=INK, sw=1.8))
    f.append(fitbox(150, 118, 260, 54, "кеш · копія реєстру", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(text(280, 214, "запис → цей самий процес скидає копію", size=12, color=INK))
    f.append(text(280, 250, "наступне читання → свіже  ✓", size=13, color=FIELD, bold=True))
    f.append(fitbox(80, 320, 400, 44, "копія і джерело сходяться", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))

    # ── праворуч: два процеси за балансувальником — скид не долітає ──
    f.append(text(862, 56, "Два процеси за балансувальником", size=15, color=INK, bold=True))
    f.append(fitbox(762, 82, 200, 48, "балансувальник", size=13, bold=True,
                    fill=BLUE_T, stroke=NEG))
    f.append(arrow(822, 130, 722, 170, color=INK, sw=2))
    f.append(arrow(902, 130, 1000, 170, color=INK, sw=2))

    # процес A — отримав запис, скинув свою копію
    f.append(rect(620, 174, 200, 122, fill=FILL, stroke=INK, sw=1.6))
    f.append(fitbox(650, 196, 140, 42, "кеш A", size=12, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(text(720, 266, "скинув копію  ✓", size=11, color=FIELD, bold=True))
    f.append(arrow(576, 232, 618, 232, color=INK, sw=2.2))
    f.append(text(568, 228, "запис", size=12, color=INK, anchor="end"))

    # процес B — не знає про запис, тримає стару копію
    f.append(rect(900, 174, 200, 122, fill=FILL, stroke=INK, sw=1.6))
    f.append(fitbox(930, 196, 140, 42, "кеш B", size=12, bold=True, fill=RED_T, stroke=POS))
    f.append(text(1000, 262, "стара копія  ✗", size=11, color=POS, bold=True))
    f.append(text(1000, 282, "живе до свого TTL", size=10, color=MUTED))

    f.append(fitbox(620, 320, 480, 44, "скид не долетів — копії розійшлися", size=13, bold=True,
                    fill=RED_T, stroke=POS))

    # ── банер унизу ──
    f.append(fitbox(80, 410, 1020, 50,
                    "In-process кеш припускає ОДИН процес. Горизонталь ламає скид-на-запис — "
                    "і саме тут починається розподілений кеш.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "single-instance-cliff.svg"), W, H, *f)


# ── Фігура 4: закликання (single-flight) — N промахів у ОДНЕ читання ──────────
def fig_single_flight():
    W, H = 1180, 560
    f = []

    f.append(line(590, 44, 590, 430, color=MUTED, sw=1.4, dash="5 5"))

    # ── ліворуч: без закликання — отара разом у базу ──
    f.append(text(300, 58, "Без закликання — отара", size=16, color=INK, bold=True))
    f.append(fitbox(96, 84, 408, 58, "гарячий ключ протух:\n200 читань промахнулись РАЗОМ",
                    size=13, bold=True, fill=NEUT, stroke=MUTED))
    f.append(text(300, 160, "×200 однакових читань", size=13, color=POS, bold=True))
    for dx in (150, 230, 300, 370, 450):                       # пучок «усі в базу»
        f.append(arrow(dx, 176, 300, 300, color=POS, sw=1.6))
    f.append(fitbox(150, 304, 300, 72, "джерело DH v3\nстампед: 200 читань за мить",
                    size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(text(300, 404, "база бачить увесь сплеск", size=13, color=POS, bold=True))

    # ── праворуч: із закликанням — один рейс, решта чекають ──
    f.append(text(886, 58, "Із закликанням — один рейс", size=16, color=INK, bold=True))
    f.append(fitbox(672, 84, 424, 58, "200 читань промах того самого ключа",
                    size=13, bold=True, fill=NEUT, stroke=MUTED))
    f.append(fitbox(660, 168, 196, 60, "1-й промах\nчитає джерело", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(902, 168, 214, 60, "решта 199\nчекають на той рейс", size=13, bold=True,
                    fill=BLUE_T, stroke=NEG))
    f.append(arrow(898, 198, 860, 198, color=INK, sw=2))       # 199 → await 1-го
    f.append(text(880, 158, "await", size=11, color=MUTED, anchor="middle"))
    f.append(arrow(758, 230, 886, 302, color=FIELD, sw=2.4))   # 1-й → база
    f.append(fitbox(736, 304, 300, 72, "джерело DH v3\nОДНЕ читання", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(text(886, 404, "база бачить один запит", size=13, color=FIELD, bold=True))

    f.append(fitbox(96, 452, 992, 58,
                    "Закликання стискає N однакових промахів в ОДНЕ читання джерела; решта "
                    "отримують ту саму копію, щойно вона повернеться. Пік промахів = один запит, не отара.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "single-flight.svg"), W, H, *f)


# ── Фігура 5: виміряне розвантаження (стенд) — TTL 30 с проти 5 хв ────────────
def fig_measured_offload():
    W, H = 1160, 470
    f = []
    PXPER = 0.10            # 1 читання/с → 0.10 px; 6000→600, 1000→100, 100→10
    x0, floor = 250, 12

    f.append(text(580, 46, "Виміряно стендом · лог: 30 000 домів · полінг 5 с · вікно 600 с",
                  size=15, color=INK, bold=True))

    def row(y, label, hit, qps, tint, edge, factor):
        f.append(text(90, y + 6, label, size=14, color=INK, bold=True, anchor="start"))
        f.append(text(90, y + 26, hit, size=12, color=MUTED, anchor="start"))
        w = max(floor, qps * PXPER)
        f.append(rect(x0, y - 14, w, 30, fill=tint, stroke=edge, sw=1.6))
        f.append(text(x0 + w + 14, y + 6, f"{qps:,} читань/с у базу".replace(",", " "),
                      size=13, color=INK, anchor="start"))
        if factor:
            f.append(text(1030, y + 6, factor, size=15, color=FIELD, bold=True, anchor="end"))

    row(112, "без кешу", "усі звернення — до бази", 6000, RED_T, POS, "×1")
    row(190, "TTL 30 с", "влучність 83 %", 1000, AMBER_T, AMBER_D, "×6")
    row(268, "TTL 5 хв", "влучність 98 %", 100, GREEN_T, FIELD, "×60")

    f.append(fitbox(90, 336, 980, 80,
                    "Довший TTL — менше промахів: 6 000/с → 1 000 (×6) при 30 с і → 100 (×60) при 5 хв. "
                    "Кешуємо лише реєстр, тож щедрий строк безпечний — а живий стан весь час іде повз "
                    "кеш і лишається свіжим. Числа не вгадані: їх дав прогін синтетичного логу.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "measured-offload.svg"), W, H, *f)


if __name__ == "__main__":
    fig_offload()
    fig_which_slice()
    fig_single_instance_cliff()
    fig_single_flight()
    fig_measured_offload()
    print("OK: figures written to", OUT)
