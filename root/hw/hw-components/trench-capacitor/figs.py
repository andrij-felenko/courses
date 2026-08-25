# -*- coding: utf-8 -*-
"""Фігури до теми «Траншейний і стекований конденсатор DRAM».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Локальна палітра матеріалів напівпровідникових структур ─────────────────
SI_SUB    = "#d0dcec"   # кремнієва підкладка p-типу
OXIDE_COL = "#d4e6b5"   # діелектрик SiO2 / польовий оксид
GATE_POLY = "#d0d0d0"   # полікремній затвора
N_PLUS    = "#f5c6cb"   # дифузійні n+-обладі (витік/стік)
METAL_M1  = "#f8d57e"   # метал бітової лінії (W/Cu)
TIN_ELEC  = "#9bb5d6"   # металевий електрод TiN (обкладка)
HIGHK_COL = "#e8b4b8"   # діелектрик High-k (ZrO2 / ZAZ / Al2O3)
PLATE_PL  = "#b8cfe5"   # спільна обкладка (Plate)
SUPPORT_M = "#e0c48c"   # механічна сітка підтримки (Support mesh)

def srect(x, y, w, h, fill, stroke=INK, sw=1.4, rx=0):
    """Прямокутник для шарів напівпровідникової структури."""
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — trench-vs-stacked: Траншейна комірка проти стекованої
# ════════════════════════════════════════════════════════════════════════════
def fig_trench_vs_stacked():
    W, H = 860, 560
    s = [text(W / 2, 26, "Порівняння архітектур комірки 1T1C DRAM у розрізі", size=17, bold=True)]

    # ── Ліва колонка: Траншейний конденсатор (Trench Capacitor) ─────────────
    box_l, _, _ = textbox(215, 54, "Траншейна комірка (Trench)", size=13, bold=True, fill="#e8f0fe", stroke=NEG)
    s.append(box_l)

    # Підкладка кремнію
    s.append(srect(30, 120, 370, 380, SI_SUB, stroke=LINE, sw=1.5))
    s.append(text(75, 480, "p-кремній (підкладка)", size=11, color=MUTED, bold=True))

    # Траншея (глибокий отвір у кремнії)
    tx, ty, tw, th = 70, 180, 90, 280
    # Заглиблена обкладка n+ навколо траншеї
    s.append(srect(tx - 12, ty, tw + 24, th + 12, N_PLUS, stroke=POS, sw=1.2))
    # Діелектрик траншеї (High-k / NO)
    s.append(srect(tx, ty, tw, th, HIGHK_COL, stroke=LINE, sw=1.2))
    # Внутрішній електрод траншеї (n+ poly / TiN)
    s.append(srect(tx + 14, ty, tw - 28, th - 12, TIN_ELEC, stroke=LINE, sw=1.2))

    # Заглиблений ремінець (Buried Strap) — з'єднання внутрішнього вузла з транзистором
    s.append(srect(tx + 40, 145, 45, 35, N_PLUS, stroke=POS, sw=1.2))

    # Транзистор доступу на поверхні
    # Витік і стік
    s.append(srect(145, 120, 45, 25, N_PLUS, stroke=POS, sw=1.2))
    s.append(srect(245, 120, 45, 25, N_PLUS, stroke=POS, sw=1.2))
    s.append(text(167, 137, "стік", size=10, bold=True))
    s.append(text(267, 137, "витік", size=10, bold=True))

    # Затвор (Лінія слова / Wordline)
    s.append(srect(195, 114, 45, 6, OXIDE_COL, stroke=LINE, sw=1.0))
    s.append(srect(195, 92, 45, 22, GATE_POLY, stroke=LINE, sw=1.2))
    s.append(text(217, 107, "WL", size=10, bold=True))

    # Бітова лінія (Bitline) зверху
    s.append(srect(250, 76, 75, 16, METAL_M1, stroke=LINE, sw=1.2))
    s.append(text(287, 88, "BL (зверху)", size=9, bold=True))
    # Контактний стовпчик від бітової лінії до витоку
    s.append(srect(260, 92, 14, 28, GATE_POLY, stroke=LINE, sw=1.2))

    # Підписи деталей траншеї
    s.append(text(115, 310, "Внутрішній", size=10, bold=True))
    s.append(text(115, 325, "електрод", size=10, bold=True))
    s.append(text(115, 340, "(вузол Cs)", size=10, bold=True))

    s.append(line(25, 230, 58, 230, color=POS, sw=1.2))
    s.append(text(22, 225, "n⁺-обкладка", size=10, color=POS, anchor="end", bold=True))

    s.append(line(25, 270, 68, 270, color=LINE, sw=1.2))
    s.append(text(22, 265, "Діелектрик", size=10, color=INK, anchor="end", bold=True))

    s.append(line(125, 160, 175, 160, color=LINE, sw=1.2))
    s.append(text(180, 164, "Заглиблений контакт (Strap)", size=10, anchor="start", bold=True))

    s.append(text(215, 525, "Конденсатор витравлено ВГЛИБ підкладки (5–8 мкм)", size=11, color=NEG, bold=True))

    # ── Права колонка: Стекований циліндричний конденсатор (Stacked COB) ─────
    box_r, _, _ = textbox(645, 54, "Стекована комірка над BL (COB)", size=13, bold=True, fill="#fef3e8", stroke=POS)
    s.append(box_r)

    # Підкладка кремнію
    s.append(srect(460, 390, 370, 110, SI_SUB, stroke=LINE, sw=1.5))
    s.append(text(505, 480, "p-кремній (підкладка)", size=11, color=MUTED, bold=True))

    # Транзистор доступу внизу
    s.append(srect(500, 390, 45, 25, N_PLUS, stroke=POS, sw=1.2))
    s.append(srect(600, 390, 45, 25, N_PLUS, stroke=POS, sw=1.2))
    s.append(text(522, 407, "витік", size=10, bold=True))
    s.append(text(622, 407, "стік", size=10, bold=True))

    # Затвор (Wordline)
    s.append(srect(550, 384, 45, 6, OXIDE_COL, stroke=LINE, sw=1.0))
    s.append(srect(550, 362, 45, 22, GATE_POLY, stroke=LINE, sw=1.2))
    s.append(text(572, 377, "WL", size=10, bold=True))

    # Бітова лінія (BL) ПІД конденсатором (Capacitor Over Bitline)
    s.append(srect(480, 310, 75, 18, METAL_M1, stroke=LINE, sw=1.2))
    s.append(text(517, 323, "BL (під стеком)", size=9, bold=True))
    s.append(srect(510, 328, 14, 62, GATE_POLY, stroke=LINE, sw=1.2))

    # Стекований циліндр / колона над транзистором
    cx, cy, cw, ch = 700, 90, 80, 170
    # Зовнішня спільна обкладка (Plate TiN)
    s.append(srect(cx - 16, cy - 10, cw + 32, ch + 20, PLATE_PL, stroke=LINE, sw=1.2, rx=4))
    # Діелектрик High-k (ZAZ)
    s.append(srect(cx - 6, cy, cw + 12, ch, HIGHK_COL, stroke=LINE, sw=1.2))
    # Внутрішній металевий електрод циліндра (TiN)
    s.append(srect(cx + 4, cy + 10, cw - 8, ch - 10, TIN_ELEC, stroke=LINE, sw=1.2))
    # Порожнина всередині циліндра (заповнена спільною обкладкою)
    s.append(srect(cx + 18, cy + 20, cw - 36, ch - 30, PLATE_PL, stroke=LINE, sw=1.0))

    # Контактний стовпчик (Storage Node Contact) до конденсатора вгору (від стоку до дна циліндра)
    s.append(srect(615, 270, 70, 16, TIN_ELEC, stroke=LINE, sw=1.2))
    s.append(srect(615, 286, 16, 104, GATE_POLY, stroke=LINE, sw=1.2))
    s.append(text(575, 345, "Вузол з'єднання", size=10, anchor="end", bold=True))

    # Механічна сітка підтримки між циліндрами (зліва від зовнішньої обкладки)
    s.append(srect(cx - 30, cy + 70, 14, 12, SUPPORT_M, stroke=LINE, sw=1.0))
    s.append(text(cx - 34, cy + 79, "Сітка підтримки", size=9, anchor="end", bold=True))

    # Підписи правої частини
    s.append(text(740, 140, "Циліндричний", size=10, bold=True))
    s.append(text(740, 155, "MIM-стек", size=10, bold=True))
    s.append(text(740, 170, "(2–3 мкм вгору)", size=10, bold=True))

    s.append(line(805, 115, 835, 115, color=LINE, sw=1.2))
    s.append(text(838, 118, "Зовнішня обкладка", size=10, anchor="start", bold=True))

    s.append(line(805, 195, 835, 195, color=LINE, sw=1.2))
    s.append(text(838, 198, "High-k (ZAZ)", size=10, anchor="start", bold=True))

    s.append(text(645, 525, "Конденсатор вирощено ВГОРУ над транзисторами й BL", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "trench-vs-stacked.svg"), W, H, *s)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — aspect-ratio-evolution: Еволюція 3D геометрії при масштабуванні
# ════════════════════════════════════════════════════════════════════════════
def fig_aspect_ratio_evolution():
    W, H = 820, 440
    s = [text(W / 2, 26, "Еволюція ємнісного вузла DRAM від 1 мкм до суб-15 нм", size=17, bold=True)]

    # 4 етапи масштабування
    # 1. Планарний (1.0 мкм, 1980-ті)
    x1 = 90
    s.append(text(x1, 62, "1. Планарний (1 мкм)", size=12, bold=True))
    s.append(text(x1, 78, "Площа: 1.0 мкм²", size=10, color=MUTED))
    s.append(srect(x1 - 55, 100, 110, 260, SI_SUB, sw=1.2))
    s.append(srect(x1 - 45, 120, 90, 8, HIGHK_COL, stroke=LINE, sw=1.0))
    s.append(srect(x1 - 45, 108, 90, 12, GATE_POLY, stroke=LINE, sw=1.0))
    s.append(text(x1, 145, "SiO₂ (20 нм)", size=9, bold=True))
    s.append(text(x1, 230, "Горизонтальна", size=10, bold=True))
    s.append(text(x1, 245, "пластина", size=10, bold=True))
    s.append(text(x1, 260, "AR ≈ 1 : 1", size=10, color=NEG, bold=True))
    s.append(text(x1, 385, "Cs ≈ 40 фФ", size=11, bold=True))

    # 2. Ранній траншейний / коробковий (250 нм, 1990-ті)
    x2 = 270
    s.append(text(x2, 62, "2. Траншея (250 нм)", size=12, bold=True))
    s.append(text(x2, 78, "Площа: 0.25 мкм²", size=10, color=MUTED))
    s.append(srect(x2 - 55, 100, 110, 260, SI_SUB, sw=1.2))
    # Траншея
    s.append(srect(x2 - 25, 110, 50, 180, HIGHK_COL, stroke=LINE, sw=1.0))
    s.append(srect(x2 - 15, 110, 30, 170, GATE_POLY, stroke=LINE, sw=1.0))
    s.append(text(x2, 200, "ONO-шар", size=9, bold=True))
    s.append(text(x2, 310, "Глибина ~4 мкм", size=10, bold=True))
    s.append(text(x2, 325, "AR ≈ 15 : 1", size=10, color=NEG, bold=True))
    s.append(text(x2, 385, "Cs ≈ 35 фФ", size=11, bold=True))

    # 3. Стекований циліндр / корона (90 нм, 2000-ні)
    x3 = 470
    s.append(text(x3, 62, "3. Циліндр COB (90 нм)", size=12, bold=True))
    s.append(text(x3, 78, "Площа: 0.04 мкм²", size=10, color=MUTED))
    s.append(srect(x3 - 55, 270, 110, 90, SI_SUB, sw=1.2))
    # Циліндр вгору
    s.append(srect(x3 - 22, 100, 44, 160, PLATE_PL, stroke=LINE, sw=1.0))
    s.append(srect(x3 - 16, 105, 32, 155, HIGHK_COL, stroke=LINE, sw=1.0))
    s.append(srect(x3 - 10, 110, 20, 150, TIN_ELEC, stroke=LINE, sw=1.0))
    s.append(srect(x3 - 3, 115, 6, 140, PLATE_PL, stroke=LINE, sw=0.8))
    s.append(text(x3, 180, "Al₂O₃/HfO₂", size=9, bold=True))
    s.append(text(x3, 310, "Висота ~1.2 мкм", size=10, bold=True))
    s.append(text(x3, 325, "AR ≈ 30 : 1", size=10, color=NEG, bold=True))
    s.append(text(x3, 385, "Cs ≈ 28 фФ", size=11, bold=True))

    # 4. Ультрависокий стовпчик з сіткою (1x нм, сучасність)
    x4 = 690
    s.append(text(x4, 62, "4. MIM-колона (1x нм)", size=12, bold=True))
    s.append(text(x4, 78, "Площа: 0.003 мкм²", size=10, color=MUTED))
    s.append(srect(x4 - 65, 310, 130, 50, SI_SUB, sw=1.2))
    # Стовпчик (центральний електрод і шар high-k з боків)
    s.append(srect(x4 - 10, 70, 20, 240, TIN_ELEC, stroke=LINE, sw=1.0))
    # Лівий і правий шар діелектрика
    s.append(srect(x4 - 16, 70, 6, 240, HIGHK_COL, stroke=LINE, sw=0.8))
    s.append(srect(x4 + 10, 70, 6, 240, HIGHK_COL, stroke=LINE, sw=0.8))

    # Сітки підтримки (Support Mesh) — зліва і справа від стовпчика (без перекриття!)
    s.append(srect(x4 - 55, 140, 39, 8, SUPPORT_M, stroke=LINE, sw=1.0, rx=2))
    s.append(srect(x4 + 16, 140, 39, 8, SUPPORT_M, stroke=LINE, sw=1.0, rx=2))
    s.append(srect(x4 - 55, 215, 39, 8, SUPPORT_M, stroke=LINE, sw=1.0, rx=2))
    s.append(srect(x4 + 16, 215, 39, 8, SUPPORT_M, stroke=LINE, sw=1.0, rx=2))
    s.append(text(x4 + 40, 135, "Сітка 1", size=9, bold=True))
    s.append(text(x4 + 40, 210, "Сітка 2", size=9, bold=True))

    s.append(text(x4, 185, "ZAZ (ZrO₂)", size=9, bold=True))
    s.append(text(x4, 325, "Висота ~2.5 мкм, AR > 60:1", size=10, color=POS, bold=True))
    s.append(text(x4, 385, "Cs ≈ 25 фФ (незмінна!)", size=11, color=POS, bold=True))

    # Нижня вісь
    s.append(line(30, 415, 790, 415, color=LINE, sw=1.5))
    s.append(text(410, 432, "Фізичний парадокс: площа комірки впала у 300 разів, а ємність Cs збережена ≥ 25 фФ", size=11, bold=True))

    render(os.path.join(IMG, "aspect-ratio-evolution.svg"), W, H, *s)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — mim-band-diagram: Зонна діаграма структури MIM (TiN / ZAZ / TiN)
# ════════════════════════════════════════════════════════════════════════════
def fig_mim_band_diagram():
    W, H = 800, 460
    s = [text(W / 2, 26, "Зонна діаграма та механізми витоку структури MIM (TiN / ZAZ / TiN)", size=16, bold=True)]

    # Зони лівого металу TiN
    s.append(srect(40, 80, 140, 310, TIN_ELEC, stroke=LINE, sw=1.5))
    s.append(text(110, 110, "Метал (TiN)", size=13, bold=True))
    s.append(text(110, 130, "Електрод 1", size=11, color=MUTED))
    s.append(line(40, 220, 180, 220, color=POS, sw=2.0, dash="5,3"))
    s.append(text(110, 240, "Рівень Фермі Ef", size=11, color=POS, bold=True))

    # Зони діелектрика ZAZ (ZrO2 / Al2O3 / ZrO2)
    # ZrO2 (лівий)
    s.append(srect(180, 130, 130, 260, HIGHK_COL, stroke=LINE, sw=1.2))
    s.append(text(245, 115, "ZrO₂ (k≈35)", size=11, bold=True))
    # Al2O3 (центральний бар'єр з ширшою щілиною Eg)
    s.append(srect(310, 90, 60, 300, OXIDE_COL, stroke=LINE, sw=1.2))
    s.append(text(340, 75, "Al₂O₃", size=11, bold=True))
    # ZrO2 (правий)
    s.append(srect(370, 140, 130, 250, HIGHK_COL, stroke=LINE, sw=1.2))
    s.append(text(435, 125, "ZrO₂ (k≈35)", size=11, bold=True))

    # Зони правого металу TiN (зсув рівня через прикладену напругу V)
    s.append(srect(500, 80, 140, 310, TIN_ELEC, stroke=LINE, sw=1.5))
    s.append(text(570, 110, "Метал (TiN)", size=13, bold=True))
    s.append(text(570, 130, "Обкладка (Plate)", size=11, color=MUTED))
    s.append(line(500, 270, 640, 270, color=POS, sw=2.0, dash="5,3"))
    s.append(text(570, 290, "Рівень Фермі Ef - qV", size=11, color=POS, bold=True))

    # Лінії зон
    s.append(line(180, 130, 310, 145, color=NEG, sw=2.5))  # Ec ZrO2
    s.append(line(310, 90, 370, 95, color=NEG, sw=2.5))    # Ec Al2O3 (вищий бар'єр)
    s.append(line(370, 145, 500, 160, color=NEG, sw=2.5))  # Ec ZrO2

    # Бар'єр Шотткі (Phi_B)
    s.append(line(180, 130, 180, 220, color=INK, sw=1.5))
    s.append(arrow(190, 180, 190, 132, color=INK, sw=1.2))
    s.append(arrow(190, 180, 190, 218, color=INK, sw=1.2))
    s.append(text(210, 180, "Φb ≈ 1.2–1.5 еВ (Бар'єр Шотткі)", size=10, anchor="start", bold=True))

    # Механізми струму витоку (Стрілки)
    # 1. Емісія Шотткі (термоелектронна емісія над бар'єром)
    s.append(arrow(150, 210, 230, 120, color=POS, sw=2.0))
    s.append(text(260, 215, "1. Емісія Шотткі (через бар'єр)", size=10, color=POS, bold=True))

    # 2. Емісія Пула-Френкеля (захоплення на пастках діелектрика)
    s.append(circle(260, 160, 4, fill=POS, stroke=INK, sw=1.0))
    s.append(circle(440, 175, 4, fill=POS, stroke=INK, sw=1.0))
    s.append(arrow(260, 160, 340, 150, color="#d35400", sw=1.8))
    s.append(arrow(340, 150, 440, 175, color="#d35400", sw=1.8))
    s.append(text(340, 190, "2. Пул-Френкель (пастки)", size=10, color="#d35400", bold=True))

    # 3. Пряме або Фаулера-Нордгейма тунелювання
    s.append(arrow(160, 220, 520, 265, color="#8e44ad", sw=2.0))
    s.append(text(340, 255, "3. Квантове тунелювання (FN / Direct)", size=10, color="#8e44ad", bold=True))

    # Текстова панель пояснення вставки Al2O3
    box_p, _, _ = textbox(400, 420, "Шар Al₂O₃ блокує межі зерен кристалічного ZrO₂ і зупиняє струми витоку", size=11, bold=True, fill="#ffffff", stroke=FIELD)
    s.append(box_p)

    render(os.path.join(IMG, "mim-band-diagram.svg"), W, H, *s)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — charge-sharing-timing: Схема розподілу заряду та часова діаграма
# ════════════════════════════════════════════════════════════════════════════
def fig_charge_sharing_timing():
    W, H = 840, 480
    s = [text(W / 2, 26, "Фізика зчитування: розподіл заряду на бітовій лінії (Charge Sharing)", size=16, bold=True)]

    # Ліва частина: Електрична еквівалентна схема
    s.append(text(200, 65, "Еквівалентна схема комірки й BL", size=13, bold=True))
    s.append(srect(30, 85, 340, 350, FILL, stroke=LINE, sw=1.2, rx=6))

    # Вузол бітової лінії BL
    s.append(line(70, 120, 320, 120, color=NEG, sw=2.5))
    s.append(text(330, 124, "BL", size=12, color=NEG, bold=True, anchor="start"))
    s.append(text(120, 110, "Vpre = Vdd / 2", size=10, color=MUTED, bold=True))

    # Паразитна ємність бітової лінії C_BL
    s.append(line(270, 120, 270, 180, color=INK, sw=1.5))
    s.append(line(250, 180, 290, 180, color=INK, sw=2.0))
    s.append(line(250, 192, 290, 192, color=INK, sw=2.0))
    s.append(line(270, 192, 270, 240, color=INK, sw=1.5))
    s.append(line(255, 240, 285, 240, color=INK, sw=2.0)) # земля
    s.append(text(300, 188, "C_BL ≈ 150 фФ", size=10, bold=True, anchor="start"))

    # Транзистор доступу (MOSFET)
    s.append(line(120, 120, 120, 160, color=INK, sw=1.5))
    # Канал
    s.append(line(105, 160, 135, 160, color=INK, sw=2.0))
    # Затвор і Wordline
    s.append(line(105, 172, 135, 172, color=POS, sw=2.0))
    s.append(line(80, 172, 105, 172, color=POS, sw=1.5))
    s.append(text(75, 175, "WL", size=11, color=POS, bold=True, anchor="end"))

    # Ємність зберігання Cs
    s.append(line(120, 160, 120, 220, color=INK, sw=1.5))
    s.append(text(130, 205, "Вузол Cs", size=10, color=MUTED, anchor="start"))
    s.append(line(100, 220, 140, 220, color=INK, sw=2.5))
    s.append(line(100, 232, 140, 232, color=INK, sw=2.5))
    s.append(line(120, 232, 120, 270, color=INK, sw=1.5))
    s.append(line(105, 270, 135, 270, color=INK, sw=2.0)) # спільна обкладка
    s.append(text(150, 228, "Cs ≈ 25 фФ", size=11, color=POS, bold=True, anchor="start"))
    s.append(text(120, 285, "Vplate = Vdd / 2", size=9, color=MUTED))

    # Підсилювач зчитування (Sense Amplifier) внизу
    box_sa, _, _ = textbox(200, 370, "Підсилювач зчитування\n(Sense Amplifier Latch)\nΔV = ±50..70 мВ → 0 або Vdd", size=10, bold=True, fill="#ffffff", stroke=FIELD)
    s.append(box_sa)
    s.append(arrow(200, 335, 200, 345, color=FIELD, sw=1.5))

    # Права частина: Часова діаграма напруг на лініях
    s.append(text(590, 65, "Часова діаграма фаз читання та відновлення", size=13, bold=True))
    s.append(srect(400, 85, 410, 350, FILL, stroke=LINE, sw=1.2, rx=6))

    # Осі
    s.append(line(440, 380, 780, 380, color=LINE, sw=1.5)) # час t
    s.append(text(785, 384, "t", size=12, bold=True, anchor="start"))
    s.append(line(440, 120, 440, 380, color=LINE, sw=1.5)) # Напруга V
    s.append(text(435, 115, "Напруга V", size=10, bold=True, anchor="end"))

    # Рівні Vdd, Vdd/2, 0
    s.append(line(435, 140, 770, 140, color=MUTED, sw=1.0, dash="3,3"))
    s.append(text(430, 144, "Vdd", size=10, color=MUTED, anchor="end"))

    s.append(line(435, 240, 770, 240, color=MUTED, sw=1.0, dash="3,3"))
    s.append(text(430, 244, "Vdd/2", size=10, color=MUTED, anchor="end"))

    s.append(text(430, 380, "0 В", size=10, color=MUTED, anchor="end"))

    # Фази 1..4 (вертикальні розділювачі)
    s.append(line(510, 120, 510, 380, color="#b0bec5", sw=1.0, dash="2,2"))
    s.append(line(610, 120, 610, 380, color="#b0bec5", sw=1.0, dash="2,2"))
    s.append(line(710, 120, 710, 380, color="#b0bec5", sw=1.0, dash="2,2"))

    s.append(text(475, 105, "1. Передзаряд", size=9, bold=True))
    s.append(text(560, 105, "2. Розподіл", size=9, bold=True))
    s.append(text(660, 105, "3. Підсилення", size=9, bold=True))
    s.append(text(745, 105, "4. Запис назад", size=9, bold=True))

    # Сигнал WL (Wordline) - червона лінія
    s.append(line(440, 360, 510, 360, color=POS, sw=2.0))
    s.append(line(510, 360, 520, 150, color=POS, sw=2.0))
    s.append(line(520, 150, 710, 150, color=POS, sw=2.0))
    s.append(line(710, 150, 720, 360, color=POS, sw=2.0))
    s.append(line(720, 360, 770, 360, color=POS, sw=2.0))
    s.append(text(725, 165, "WL (активація)", size=9, color=POS, bold=True))

    # Сигнал BL при читанні '1' - синя лінія
    s.append(line(440, 240, 510, 240, color=NEG, sw=2.2))
    # Стрибок на Delta V_BL
    s.append(line(510, 240, 550, 215, color=NEG, sw=2.2))
    s.append(line(550, 215, 610, 215, color=NEG, sw=2.2))
    # Підсилення до повного Vdd
    s.append(line(610, 215, 670, 140, color=NEG, sw=2.5))
    s.append(line(670, 140, 770, 140, color=NEG, sw=2.5))
    s.append(text(620, 205, "+ΔVBL ≈ 60 мВ", size=9, color=NEG, bold=True))
    s.append(text(730, 130, "BL = Vdd ('1')", size=10, color=NEG, bold=True))

    # Референтна бітова лінія BL_bar при читанні '1' - сіра лінія до 0 В
    s.append(line(440, 240, 610, 240, color=MUTED, sw=1.8))
    s.append(line(610, 240, 670, 380, color=MUTED, sw=1.8))
    s.append(line(670, 380, 770, 380, color=MUTED, sw=1.8))
    s.append(text(730, 370, "BL_bar = 0 В", size=10, color=MUTED, bold=True))

    s.append(text(420, 455, "Без достатньої ємності Cs (≥25 фФ) сигнал ΔVBL тоне у тепловому шумі", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "charge-sharing-timing.svg"), W, H, *s)

if __name__ == "__main__":
    fig_trench_vs_stacked()
    fig_aspect_ratio_evolution()
    fig_mim_band_diagram()
    fig_charge_sharing_timing()
    print("All figures generated successfully.")
