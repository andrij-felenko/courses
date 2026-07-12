# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір стилю саги» (хореографія проти оркестрації)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENF = "#eafaf0"
BLUEF  = "#eaf0fd"
REDF   = "#fdecea"
AMBERF = "#fdf3e3"


def fig_choreo_vs_orchestr():
    """Ліворуч хореографія (кільце подій, порожній центр), праворуч оркестрація (центр-диригент, спиці)."""
    W, H = 1140, 560
    frags = []

    # розділювач двох панелей
    frags.append(line(570, 44, 570, 516, color=MUTED, sw=1, dash="4,6"))

    # ── ЛІВОРУЧ: ХОРЕОГРАФІЯ ────────────────────────────────────────────────
    frags.append(text(285, 74, "Хореографія · без диригента", size=17, bold=True))

    # чотири рівні учасники по діаманту
    ring = [(285, 185, "реєстр"), (435, 300, "хаб"),
            (285, 415, "білінг"), (135, 300, "сповіщення")]
    for cx, cy, lbl in ring:
        frags.append(textbox(cx, cy, lbl, size=13, fill=FILL, stroke=LINE, min_w=104)[0])

    # кільце подій-стрілок (за годинниковою) — по краях діаманта, повз центр
    frags.append(arrow(325, 201, 393, 286, color=INK, sw=1.7))   # реєстр → хаб
    frags.append(arrow(393, 314, 325, 399, color=INK, sw=1.7))   # хаб → білінг
    frags.append(arrow(245, 399, 177, 314, color=INK, sw=1.7))   # білінг → сповіщення
    frags.append(arrow(177, 286, 245, 201, color=INK, sw=1.7))   # сповіщення → реєстр
    frags.append(text(372, 232, "подія", size=11, color=MUTED, italic=True))
    frags.append(text(198, 372, "подія", size=11, color=MUTED, italic=True))

    # порожній центр із написом
    frags.append(mtext(285, 285, "потік живе\nу дротах між рівними,\nніде не зібраний",
                       size=12, color=MUTED, lh=1.3))

    frags.append(text(285, 500, "щоб зрозуміти сагу — прочитай усіх і склади в голові",
                      size=12, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: ОРКЕСТРАЦІЯ ───────────────────────────────────────────────
    frags.append(text(855, 74, "Оркестрація · з диригентом", size=17, bold=True))

    OX, OY = 855, 300
    parts = [(855, 168, "реєстр"), (1025, 300, "хаб"),
             (855, 432, "білінг"), (685, 300, "сповіщення")]
    for cx, cy, lbl in parts:
        frags.append(textbox(cx, cy, lbl, size=13, fill=FILL, stroke=LINE, min_w=104)[0])

    # спиці-команди від оркестратора до кожного учасника
    frags.append(arrow(OX, OY - 20, 855, 190, color=INK, sw=1.7))   # ↑ реєстр
    frags.append(arrow(OX + 88, OY, 971, 300, color=INK, sw=1.7))   # → хаб
    frags.append(arrow(OX, OY + 20, 855, 410, color=INK, sw=1.7))   # ↓ білінг
    frags.append(arrow(OX - 88, OY, 739, 300, color=INK, sw=1.7))   # ← сповіщення

    # сам оркестратор — поверх спиць
    frags.append(textbox(OX, OY, "оркестратор", size=14, bold=True,
                         fill=BLUEF, stroke=NEG, min_w=150)[0])

    frags.append(text(855, 500, "щоб зрозуміти сагу — прочитай один оркестратор",
                      size=12, color=MUTED, italic=True))
    frags.append(text(855, 520, "команди — до учасників, відповіді — назад",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "choreo-vs-orchestr.svg"), W, H, *frags)


def fig_sensitivity_axis():
    """Вісь: мало кроків → хореографія; багато кроків + видимість → оркестрація; поріг зсуває рушій."""
    W, H = 1140, 410
    frags = []
    AXY = 205

    # підкладка-градієнт під віссю
    band = [(105, 400, "#eef7f1"), (400, 720, "#eef1f6"), (720, 1015, "#e6ecf5")]
    for x0, x1, col in band:
        frags.append(rect(x0, AXY - 16, x1 - x0, 32, fill=col, stroke=col, sw=0.5, rx=0))
    frags.append(arrow(105, AXY, 1015, AXY, color=INK, sw=2))

    # зони (осторонь від колонок-прикладів x=250 / x=855)
    frags.append(text(400, 172, "Хореографія", size=16, bold=True, color=FIELD))
    frags.append(text(745, 172, "Оркестрація", size=16, bold=True, color=NEG))

    # поріг — чутлива точка
    frags.append(line(575, 110, 575, 300, color=POS, sw=1.6, dash="5,5"))
    frags.append(text(575, 100, "чутлива точка", size=12.5, bold=True, color=POS))

    # кінцеві ярлики під віссю
    frags.append(mtext(180, AXY + 42, "мало кроків,\nніхто не мусить\nбачити потік",
                       size=12, color=MUTED, lh=1.25))
    frags.append(mtext(945, AXY + 42, "багато кроків,\nрозгалуження,\nхтось володіє потоком",
                       size=12, color=MUTED, lh=1.25))

    # приклади DH на осі
    frags.append(circle(250, AXY, 7, fill=GREENF, stroke=FIELD, sw=2))
    frags.append(line(250, AXY - 7, 250, 132, color=MUTED, sw=1))
    frags.append(textbox(250, 108, "рух → світло\n1 крок · не сага",
                         size=12, fill=GREENF, stroke=FIELD, min_w=190)[0])

    frags.append(circle(855, AXY, 7, fill=BLUEF, stroke=NEG, sw=2))
    frags.append(line(855, AXY - 7, 855, 132, color=MUTED, sw=1))
    frags.append(textbox(855, 108, "сім'я продає дім\n6 кроків · компенсації · статус",
                         size=12, fill=BLUEF, stroke=NEG, min_w=190)[0])

    # рушій зсуває поріг ліворуч
    frags.append(arrow(690, 322, 500, 322, color=MUTED, sw=1.6))
    frags.append(text(595, 374, "довговічний рушій зсуває поріг ліворуч — оркестрація дешевшає",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "sensitivity-axis.svg"), W, H, *frags)


def fig_saga_lineage():
    """Часова смуга: дві притоки (сага 1987; два слова 2002–05) зливаються в мікросервісах (2015–18)."""
    W, H = 1180, 500
    frags = []
    AXY = 300

    def X(year):
        return 90 + (year - 1985) * (1000.0 / 35.0)

    # вісь часу (стрілка → час тече праворуч)
    frags.append(arrow(80, AXY, 1115, AXY, color=INK, sw=2))
    for yr in (1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020):
        frags.append(line(X(yr), AXY - 5, X(yr), AXY + 5, color=MUTED, sw=1.2))
        frags.append(text(X(yr), AXY + 22, str(yr), size=11, color=MUTED))

    # велика прогалина «майже 30 років» між народженням і переосмисленням —
    # брекет у порожній верхній смузі, щоб нічого не перетинати
    frags.append(line(X(1987), 46, X(2015), 46, color=MUTED, sw=1, dash="4,5"))
    frags.append(line(X(1987), 40, X(1987), 52, color=MUTED, sw=1))
    frags.append(line(X(2015), 40, X(2015), 52, color=MUTED, sw=1))
    frags.append(text((X(1987) + X(2015)) / 2, 32,
                      "≈ 28 років: до розподілу сагу приклали аж тут",
                      size=12, color=MUTED, italic=True))

    # ── ПРИТОКА 1: САГА (над віссю, зелена) ─────────────────────────────────
    frags.append(circle(X(1987), AXY, 5, fill=GREENF, stroke=FIELD, sw=2))
    frags.append(line(185, 205, X(1987), AXY - 4, color=MUTED, sw=1, dash="3,4"))
    frags.append(textbox(215, 165,
                         "1987 · ACM SIGMOD\nГарсія-Моліна й Салем\nсага для ОДНІЄЇ бази",
                         size=13, fill=GREENF, stroke=FIELD, min_w=250)[0])

    # ── ПРИТОКА 2: ДВА СЛОВА (під віссю, синя) ──────────────────────────────
    for yr in (2002, 2003, 2005):
        frags.append(circle(X(yr), AXY, 5, fill=BLUEF, stroke=NEG, sw=2))
        # лінія стартує ПІСЛЯ смуги річних підписів під віссю (щоб не різати «2005»)
        frags.append(line(X(yr), AXY + 36, X(yr), 388, color=MUTED, sw=1, dash="3,4"))
    frags.append(textbox(600, 425,
                         "2002–2005 · вебсервіси й SOA\n"
                         "оркестрація (BPEL)  ·  хореографія (WS-CDL)\n"
                         "Пельц 2003 · Гопе й Вулф: Process Manager / Routing Slip",
                         size=12, fill=BLUEF, stroke=NEG, min_w=560)[0])

    # ── ЗЛИТТЯ: МІКРОСЕРВІСИ (над віссю, бурштин) ───────────────────────────
    for yr in (2015, 2018):
        frags.append(circle(X(yr), AXY, 5, fill=AMBERF, stroke=POS, sw=2))
        frags.append(line(X(yr), 213, X(yr), AXY - 4, color=MUTED, sw=1, dash="3,4"))
    frags.append(textbox(958, 160,
                         "2015–2018 · мікросервіси\n"
                         "сагу приклали до розподілу,\n"
                         "а стилі назвали двома старими словами\n"
                         "Маккефрі · Річардсон",
                         size=12.5, fill=AMBERF, stroke=POS, min_w=340)[0])

    # ── ДВІ ПРИТОКИ ЗЛИВАЮТЬСЯ В ОДНУ РІЧКУ ─────────────────────────────────
    frags.append(arrow(342, 168, 786, 165, color=INK, sw=2))     # сага → мікросервіси
    frags.append(arrow(882, 392, 892, 208, color=INK, sw=2))     # слова → мікросервіси

    render(os.path.join(IMG, "saga-lineage-timeline.svg"), W, H, *frags)


def fig_vocab_map():
    """Дві форми координації — три вбрання (EIP / SOA / мікросервіси)."""
    W, H = 1160, 430
    frags = []
    cols = [(360, "Повідомлення · EIP\n2003"),
            (620, "Вебсервіси · SOA\n2002–05"),
            (900, "Мікросервіси\n2015+")]
    for cx, head in cols:
        frags.append(mtext(cx, 60, head, size=14, bold=True, lh=1.25))
    frags.append(line(250, 88, 1030, 88, color=MUTED, sw=1))
    frags.append(line(255, 96, 255, 400, color=MUTED, sw=1, dash="4,6"))

    # рядок 1 — «мозок у центрі» (оркестрація)
    r1 = 190
    frags.append(mtext(135, r1 - 6, "мозок —\nу центрі", size=13, bold=True,
                       color=NEG, lh=1.2))
    for cx, txt in ((360, "Process Manager"), (620, "оркестрація\nBPEL"),
                    (900, "оркестрація\n(оркестратор)")):
        frags.append(textbox(cx, r1, txt, size=13, fill=BLUEF, stroke=NEG, min_w=210)[0])

    # рядок 2 — «мозку немає, крок їде з листом» (хореографія)
    r2 = 320
    frags.append(mtext(135, r2 - 12, "мозку немає:\nкрок їде\nз листом", size=13, bold=True,
                       color=FIELD, lh=1.2))
    for cx, txt in ((360, "Routing Slip"), (620, "хореографія\nWS-CDL"),
                    (900, "хореографія\n(події)")):
        frags.append(textbox(cx, r2, txt, size=13, fill=GREENF, stroke=FIELD, min_w=210)[0])

    frags.append(text(W / 2, 412,
                      "дві форми старші за всі три назви — питання завжди те саме: де живе мозок процесу",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "vocab-map.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_choreo_vs_orchestr()
    fig_sensitivity_axis()
    fig_saga_lineage()
    fig_vocab_map()
    print("OK: choreo-vs-orchestr.svg, sensitivity-axis.svg, "
          "saga-lineage-timeline.svg, vocab-map.svg")


# ── Фігури до вставки proj-saga-two-ways (додано окремо, щоб не чіпати блок вище) ──
def fig_crash_mid_saga():
    """Збій посеред саги: наївний тримає undo в RAM (гине), довговічний — крок на диску (відроджується)."""
    W, H = 1240, 620
    frags = []

    frags.append(text(W / 2, 34, "Збій посеред саги — де живе стан", size=18, bold=True))

    # вертикальна лінія «процес помер тут»
    CX = 600
    frags.append(line(CX, 96, CX, 566, color=POS, sw=1.7, dash="6,6"))
    frags.append(text(CX, 84, "процес помер тут", size=13.5, bold=True, color=POS))

    # роздільник смуг
    frags.append(line(70, 330, 1170, 330, color=MUTED, sw=1, dash="3,7"))

    # ── ВЕРХНЯ СМУГА: наївний оркестратор ───────────────────────────────
    TY = 200
    frags.append(textbox(140, TY, "наївний\nоркестратор", size=13, bold=True,
                         fill=FILL, stroke=LINE, min_w=150)[0])
    frags.append(textbox(350, TY, "reserve ✓", size=13, fill=GREENF, stroke=FIELD, min_w=130)[0])
    frags.append(textbox(350, TY + 92, "undo = [ unreserve ]\nу пам'яті процесу", size=11.5,
                         fill=BG, stroke=MUTED, min_w=215)[0])
    frags.append(arrow(442, TY + 66, 554, TY + 22, color=MUTED, sw=1.4))
    frags.append(text(516, TY + 60, "губиться разом із процесом", size=11, color=MUTED, italic=True))
    frags.append(textbox(908, TY, "реєстр: { dev-42 } — назавжди\nнема кому відкотити\nнема статусу саги",
                         size=12.5, fill=REDF, stroke=POS, min_w=345)[0])
    frags.append(arrow(CX + 6, TY, 730, TY, color=POS, sw=1.6))

    # ── НИЖНЯ СМУГА: довговічний рушій ──────────────────────────────────
    BY = 455
    frags.append(textbox(140, BY, "довговічний\nрушій", size=13, bold=True,
                         fill=FILL, stroke=LINE, min_w=150)[0])
    frags.append(textbox(350, BY, "reserve ✓", size=13, fill=GREENF, stroke=FIELD, min_w=130)[0])
    frags.append(textbox(350, BY + 88, "диск: cursor = 1", size=12, bold=True,
                         fill=BLUEF, stroke=NEG, min_w=205)[0])
    frags.append(arrow(457, BY + 88, 707, BY + 88, color=NEG, sw=1.6))
    frags.append(text(584, BY + 78, "переживає смерть процесу", size=11, color=NEG, italic=True))
    frags.append(textbox(808, BY, "новий процес\nчитає диск → cursor = 1", size=12.5,
                         fill=BLUEF, stroke=NEG, min_w=255)[0])
    frags.append(arrow(CX + 6, BY, 678, BY, color=NEG, sw=1.6))
    frags.append(arrow(808, BY + 34, 808, BY + 66, color=NEG, sw=1.6))
    frags.append(textbox(1048, BY, "доробляє config ✓ → meter ✓\nсага committed", size=12,
                         fill=GREENF, stroke=FIELD, min_w=300)[0])
    frags.append(arrow(940, BY, 974, BY, color=INK, sw=1.5))

    render(os.path.join(IMG, "crash-mid-saga.svg"), W, H, *frags)


def fig_choreo_sprawl():
    """Додати крок: оркестрація — одна правка; хореографія — правки в кількох сервісах + діра компенсації."""
    W, H = 1200, 560
    frags = []

    frags.append(line(600, 44, 600, 516, color=MUTED, sw=1, dash="4,6"))

    # ── ЛІВОРУЧ: ОРКЕСТРАЦІЯ ────────────────────────────────────────────
    frags.append(text(300, 74, "Оркестрація · одна правка", size=16.5, bold=True))
    frags.append(textbox(300, 172, "enrollDevice()\nsteps = [ reserve, config, meter ]", size=12.5,
                         fill=FILL, stroke=LINE, min_w=345)[0])
    frags.append(text(300, 254, "+ вставив один крок:  tax", size=14, bold=True, color=FIELD))
    frags.append(textbox(300, 352, "компенсація — зворотним порядком,\nвключає tax ДАРМА\nтест повного відкоту лишається зелений",
                         size=12, fill=GREENF, stroke=FIELD, min_w=390)[0])
    frags.append(text(300, 476, "статус саги — store.status(id)", size=12, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: ХОРЕОГРАФІЯ ───────────────────────────────────────────
    frags.append(text(895, 74, "Хореографія · правки розповзаються", size=16.5, bold=True))

    edits = [
        (775, 160, "on Configured →\ntax.register", "правка 1"),
        (1030, 160, "billing слухає\nтепер DeviceTaxed", "правка 2"),
        (775, 302, "on MeterFailed →\nтеж undo tax", "правка 3"),
    ]
    for cx, cy, body, tag in edits:
        frags.append(textbox(cx, cy, body, size=12, fill=BG, stroke=POS, min_w=215)[0])
        frags.append(text(cx, cy - 42, tag, size=11, bold=True, color=POS))

    frags.append(textbox(1030, 302, "компенсаційна\nмережа — окремо", size=12,
                         fill=FILL, stroke=MUTED, min_w=205)[0])

    frags.append(textbox(895, 422, "забув гілку компенсації →  tax тече,\nсага рветься у шві — і ніхто не бачить",
                         size=12.5, fill=REDF, stroke=POS, min_w=440)[0])
    frags.append(text(895, 500, "статусу саги — ніде", size=12, bold=True, color=POS, italic=True))

    render(os.path.join(IMG, "choreo-sprawl.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_crash_mid_saga()
    fig_choreo_sprawl()
    print("OK (saga-two-ways): crash-mid-saga.svg, choreo-sprawl.svg")
