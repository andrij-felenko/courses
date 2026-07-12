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


# ── Фігура 1: топологія твіна — один писар, багато читалень ────────────────────
def fig_topology():
    W, H = 1220, 600
    f = []

    f.append(text(610, 42, "Один писар, багато читалень", size=17, bold=True))

    # ── джерела записів (ліворуч) ──
    f.append(fitbox(60, 152, 190, 56, "хаб\n(доповідає стан)", size=13, fill=BG, stroke=INK))
    f.append(fitbox(60, 246, 190, 56, "команда\nкористувача", size=13, fill=BG, stroke=INK))
    f.append(text(292, 232, "записи", size=12, color=MUTED, bold=True))
    f.append(arrow(250, 180, 330, 208, color=INK, sw=2.2))
    f.append(arrow(250, 274, 330, 246, color=INK, sw=2.2))

    # ── лідер (центр-ліво) ──
    f.append(fitbox(330, 170, 240, 110, "твін · ЛІДЕР\nєдиний писар\nзавжди найсвіжіший",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))

    # ── фоловери (праворуч) ──
    f.append(fitbox(800, 96, 360, 58, "фоловер 1 · копія твіна", size=14, fill=NEUT, stroke=MUTED))
    f.append(fitbox(800, 190, 360, 58, "фоловер 2 · копія твіна", size=14, fill=NEUT, stroke=MUTED))
    f.append(fitbox(800, 284, 360, 58, "фоловер 3 · копія твіна", size=14, fill=NEUT, stroke=MUTED))
    f.append(text(980, 366, "кожна копія позаду на лаг Δ", size=12, color=MUTED))

    # ── асинхронна реплікація: лідер → фоловери ──
    f.append(mtext(690, 66, ["асинхронна реплікація", "(фоловер завжди позаду на лаг Δ)"],
                   size=12, color=MUTED))
    f.append(arrow(570, 200, 800, 126, color=MUTED, sw=2))
    f.append(arrow(570, 222, 800, 220, color=MUTED, sw=2))
    f.append(arrow(570, 244, 800, 314, color=MUTED, sw=2))

    # ── читання: застосунки → фоловери ──
    f.append(fitbox(330, 408, 360, 66, "десятки тисяч застосунків\nчитають «покажи мій дім»",
                    size=13, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(text(510, 396, "читання — на фоловери", size=12, color=NEG, bold=True))
    f.append(arrow(690, 436, 800, 250, color=NEG, sw=2.6))

    # ── банер ──
    f.append(fitbox(60, 512, 1100, 62,
                    "Усі записи сходяться в ОДНОГО лідера; фоловери тримають читабельні копії й "
                    "доганяють його з лагом Δ.\nПотік «покажи мій дім» розсипано по фоловерах — звідси "
                    "масштаб; але кожна копія, яку читає застосунок, — трохи минуле твіна.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "twin-topology.svg"), W, H, *f)


# ── Фігура 2: часова стрічка стейл-читання ────────────────────────────────────
def fig_stale_timeline():
    W, H = 1210, 575
    f = []

    f.append(text(605, 40, "«Вимкнув світло — а застосунок показує ввімкнене»", size=16, bold=True))

    # ── доріжки-підписи (ліворуч) ──
    f.append(fitbox(28, 96, 172, 48, "Користувач /\nзастосунок", size=12, bold=True,
                    fill=NEUT, stroke=MUTED))
    f.append(fitbox(28, 232, 172, 48, "Лідер (твін)", size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(28, 372, 172, 48, "Фоловер (копія)", size=13, bold=True, fill=NEUT, stroke=MUTED))

    # ── часові орієнтири (короткі засічки вгорі, щоб не різати доріжки) ──
    for x, lbl in ((330, "t0"), (560, "+120 мс"), (790, "+300 мс"), (1035, "+Δ (лаг)")):
        f.append(text(x, 76, lbl, size=12, color=MUTED, bold=True))
        f.append(line(x, 82, x, 104, color=MUTED, sw=1.4))

    # ── доріжка лідера: OFF від t0 ──
    f.append(rect(330, 238, 760, 34, fill=GREEN_T, stroke=FIELD, sw=1.6))
    f.append(text(610, 259, "стан: OFF — записано в t0", size=13, color=INK, bold=True))
    f.append(text(400, 300, "запис off ✓", size=12, color=FIELD, bold=True, anchor="middle"))

    # ── доріжка фоловера: ON (застаріле) до +Δ, потім OFF ──
    f.append(rect(205, 378, 830, 34, fill=RED_T, stroke=POS, sw=1.6))
    f.append(text(600, 399, "стан: ON — застаріла копія", size=13, color=POS, bold=True))
    f.append(rect(1035, 378, 150, 34, fill=GREEN_T, stroke=FIELD, sw=1.6))
    f.append(text(1110, 399, "OFF", size=13, color=FIELD, bold=True))

    # ── користувач: дія, перечитування, помилковий результат ──
    f.append(fitbox(252, 96, 156, 48, "тисне\n«вимкнути»", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(712, 96, 150, 48, "перечитує\nекран", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(880, 96, 165, 48, "бачить: ON  ✗", size=13, bold=True, fill=RED_T, stroke=POS))

    # ── реплікація off у дорозі: лідер → фоловер, доїде аж у +Δ ──
    f.append(arrow(345, 274, 1022, 376, color=MUTED, sw=2))
    f.append(mtext(468, 198, ["реплікація «off» у дорозі —", "доїде аж у +Δ"],
                   size=12, color=MUTED))

    # ── читання йде на фоловер (униз) і повертає ON (угору) ──
    f.append(arrow(783, 146, 783, 376, color=NEG, sw=2.2))
    f.append(mtext(748, 196, ["читання", "→ фоловер"], size=11, color=NEG, anchor="end"))
    f.append(arrow(800, 378, 905, 152, color=POS, sw=2))
    f.append(text(918, 210, "віддає ON", size=11, color=POS, bold=True, anchor="start"))

    # ── банер ──
    f.append(fitbox(28, 496, 1158, 56,
                    "Запис «off» живий на лідері з t0, але перечитування о +300 мс попало на фоловер, "
                    "що догнав лідера лише о +Δ.\nЧитання пішло в минуле твіна й показало ON, старший за "
                    "дію користувача. Баг живе рівно у вікні лагу.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "stale-read-timeline.svg"), W, H, *f)


# ── Фігура 3: класифікація читань дому ────────────────────────────────────────
def fig_classification():
    W, H = 1160, 610
    f = []

    f.append(text(580, 40, "Розкол читань: «чи мусить побачити свій свіжий запис?»",
                  size=16, bold=True))

    f.append(fitbox(430, 62, 300, 50, "читання про дім", size=14, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(arrow(540, 112, 300, 156, color=INK, sw=2))
    f.append(arrow(620, 112, 860, 156, color=INK, sw=2))

    f.append(line(580, 150, 580, 476, color=MUTED, sw=1.4, dash="5 5"))

    # ── ліва колонка: на лідера (read-your-writes) ──
    f.append(fitbox(70, 158, 400, 52, "На ЛІДЕРА · read-your-writes", size=14, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(mtext(270, 248, ["• стан пристрою одразу", "  після власної зміни",
                              "• стан замка — безпека"], size=14, color=INK, lh=1.5))
    f.append(text(270, 352, "вузька, дорога купа", size=13, color=MUTED, bold=True))
    f.append(fitbox(70, 374, 400, 92,
                    "ЛІДЕР · липке-після-запису:\nсвіже — лише короткий час\nі лише самому писареві",
                    size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    # ── права колонка: на фоловери (лаг стерпний) ──
    f.append(fitbox(690, 158, 400, 52, "На ФОЛОВЕРИ · лаг стерпний", size=14, bold=True,
                    fill=AMBER_T, stroke=AMBER_D))
    f.append(mtext(890, 242, ["• телеметрія, графіки, історія", "• лічильники й агрегати",
                              "• реєстр (ще й кешований)", "• стан ЧУЖОГО дому"],
                   size=14, color=INK, lh=1.5))
    f.append(text(890, 362, "широка, дешева купа — тримає масштаб", size=13, color=MUTED, bold=True))
    f.append(fitbox(690, 384, 400, 82,
                    "ФОЛОВЕРИ · сесія → та сама копія\n(монотонні читання: час не йде назад)",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER_D))

    # ── банер ──
    f.append(fitbox(70, 502, 1020, 66,
                    "Не «сильно скрізь», а поіменно. Ліва купа — тільки те, де власний свіжий запис чи "
                    "безпека вимагають лідера.\nПрава — усе, що терпить кілька секунд минулого, і саме "
                    "вона через фоловери розвантажує лідера.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "read-classification.svg"), W, H, *f)


# ── Фігура 4 (вставка hist): родовід твіна — від дзеркальних світів до тіні ────
def fig_twin_lineage():
    W, H = 1340, 610
    f = []
    f.append(text(670, 40, "Родовід твіна: від «дзеркальних світів» до тіні пристрою",
                  size=18, bold=True))

    axis_y = 312
    f.append(line(70, axis_y, 1272, axis_y, color=MUTED, sw=2))

    # (x, напрям, рік, текст, заливка, обведення)
    nodes = [
        (150,  'up',   "1991",     "Ґелернтер:\n«дзеркальні світи» —\nідея без слова",        NEUT,    MUTED),
        (390,  'down', "2002",     "Грівз (Мічиган):\nMirrored Spaces /\nInformation Mirroring —\nконцепція без імені", BLUE_T, NEG),
        (620,  'up',   "≈2010–11", "Вікерз (NASA) дає ІМʼЯ\n«Digital Twin»;\nкнига Грівза 2011",  GREEN_T, FIELD),
        (830,  'down', "2012",     "NASA (Ґлессґен,\nСтарджел): строге\nозначення",             NEUT,    MUTED),
        (1035, 'up',   "2015–16",  "AWS Device Shadow,\nAzure device twin —\nтінь пристрою в хмарі", GREEN_T, FIELD),
        (1215, 'down', "сьогодні", "DH: твін дому —\nтой самий патерн",                        GREEN_T, FIELD),
    ]
    for x, d, yr, txt, fill, stroke in nodes:
        f.append(circle(x, axis_y, 7, fill=stroke, stroke=stroke))
        if d == 'up':
            f.append(line(x, axis_y, x, 256, color=MUTED, sw=1.6))
            f.append(fitbox(x - 108, 146, 216, 110, txt, size=13, bold=True, fill=fill, stroke=stroke))
            f.append(text(x, 340, yr, size=14, color=INK, bold=True))
        else:
            f.append(line(x, axis_y, x, 358, color=MUTED, sw=1.6))
            f.append(fitbox(x - 108, 358, 216, 118, txt, size=13, bold=True, fill=fill, stroke=stroke))
            f.append(text(x, 292, yr, size=14, color=INK, bold=True))

    f.append(arrow(1254, axis_y, 1272, axis_y, color=FIELD, sw=2.6))

    # Аполлон — фізичний предок ідеї, збоку-знизу; НЕ цифровий твін
    f.append(fitbox(150, 512, 470, 74,
                    "Аполлон (1960–70-ті): фізичні двійники-кораблі та тренажери.\n"
                    "Предок самої ІДЕЇ дублікату — але це ФІЗИЧНИЙ двійник, не цифровий\n"
                    "(«перший цифровий твін» — популярний міф).",
                    size=12, fill=RED_T, stroke=POS, color=INK))
    f.append(line(385, 510, 385, 478, color=POS, sw=1.6, dash="5 5"))

    render(os.path.join(OUT, "twin-lineage.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): три сходинки твіна — залізо → модель → хмара ──────
def fig_twin_ladder():
    W, H = 1280, 500
    f = []
    f.append(text(640, 40, "Три сходинки твіна: залізо → модель → хмарна копія",
                  size=18, bold=True))

    cols = [210, 640, 1070]
    f.append(arrow(400, 250, 452, 250, color=MUTED, sw=2.6))
    f.append(arrow(830, 250, 882, 250, color=MUTED, sw=2.6))

    # ── 1. фізичний твін ──
    cx = cols[0]
    f.append(fitbox(cx - 180, 74, 360, 56, "ФІЗИЧНИЙ ТВІН\nАполлон · 1960–70-ті",
                    size=14, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(cx - 156, 164, 140, 72, "справжній\nапарат\n(політ)", size=12, fill=NEUT, stroke=MUTED))
    f.append(fitbox(cx + 16, 164, 140, 72, "такий самий\nапарат\n(на Землі)", size=12, fill=NEUT, stroke=MUTED))
    f.append(fitbox(cx - 180, 272, 360, 176,
                    "Дублікат — справжнє залізо,\nодин-в-один. Точно, але\nстрашенно дорого: другий\n"
                    "фізичний корабель. Лише для\nнайкритичніших місій.",
                    size=13, fill=RED_T, stroke=POS, color=INK))

    # ── 2. цифровий твін ──
    cx = cols[1]
    f.append(fitbox(cx - 180, 74, 360, 56, "ЦИФРОВИЙ ТВІН\nГрівз · NASA · 2002–12",
                    size=14, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(cx - 156, 164, 140, 72, "фізичний\nобʼєкт", size=12, fill=NEUT, stroke=MUTED))
    f.append(fitbox(cx + 16, 164, 140, 72, "модель\nданих", size=12, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(text(cx, 156, "телеметрія →", size=11, color=FIELD, bold=True))
    f.append(arrow(cx - 14, 200, cx + 14, 200, color=FIELD, sw=2))
    f.append(fitbox(cx - 180, 272, 360, 176,
                    "Замість другого заліза —\nМОДЕЛЬ. Дані дзеркалять\nобʼєкт; телеметрія тримає\n"
                    "модель живою. Дешевше й\nмасштабується — та сама ідея\nбез другого корпусу.",
                    size=13, fill=BLUE_T, stroke=NEG, color=INK))

    # ── 3. тінь пристрою ──
    cx = cols[2]
    f.append(fitbox(cx - 180, 74, 360, 56, "ТІНЬ ПРИСТРОЮ\nAWS · Azure · DH · 2015→",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(cx - 156, 158, 312, 46, "хмара тримає копію стану", size=13, bold=True,
                    fill=GREEN_T, stroke=FIELD))
    f.append(arrow(cx, 204, cx, 226, color=INK, sw=1.8))
    f.append(fitbox(cx - 156, 226, 312, 46, "застосунок читає копію —\nнавіть коли пристрій офлайн",
                    size=12, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(cx - 180, 292, 360, 156,
                    "Персистентна хмарна копія\nстану. «Бажане ⇄ повідомлене».\n"
                    "Читається незалежно від того,\nонлайн пристрій чи ні.\nЦе і є твін DH.",
                    size=13, fill=GREEN_T, stroke=FIELD, color=INK))

    render(os.path.join(OUT, "twin-ladder.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology()
    fig_stale_timeline()
    fig_classification()
    fig_twin_lineage()
    fig_twin_ladder()
    print("OK: figures written to", OUT)
