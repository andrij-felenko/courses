# -*- coding: utf-8 -*-
"""Фігури до теми «p-n ізоляція компонентів на кристалі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Палітра напівпровідникових шарів ──────────────────────────────────────────
SUB_P    = "#e6ddf2"   # підкладка p-типу (світлий лавандовий)
SUB_P_DK = "#7b5ca8"   # контур p-підкладки
WALL_P   = "#c8b0e8"   # важколеговані p⁺ ізоляційні стінки
WALL_P_DK= "#5c3988"   # контур p⁺ стінок
EPI_N    = "#d0e4f7"   # епітаксійний шар / кишеня n-типу
EPI_N_DK = "#3b78b8"   # контур n-кишені
BL_N     = "#9ecbf0"   # прихований шар n⁺ (buried layer)
BL_N_DK  = "#1f5690"   # контур n⁺ прихованого шару
BASE_P   = "#e0cce8"   # p-база транзистора / тіло резистора
EMIT_N   = "#fcd4cf"   # емітер n⁺ / контакт колектора n⁺
EMIT_DK  = "#c0392b"   # контур емітера n⁺
OXID     = "#dbeec0"   # захисний оксид SiO₂
OXID_DK  = "#7a9e3a"   # контур оксиду
METAL    = "#e8b84b"   # алюмінієва металізація
METED    = "#8a5810"   # контур металу
DEP_CLR  = "#fff3b3"   # збіднена область p-n переходу (depletion region)
DEP_DK   = "#bfa010"   # штриховка / межа збіднення


def srect(x, y, w, h, fill, stroke=INK, sw=1.5, dash=None):
    """Прямокутник із прямими кутами для шарів у розрізі."""
    d = (' stroke-dasharray="%s"' % dash) if dash else ''
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" '
            'fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (x, y, w, h, fill, stroke, sw, d))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — pn-isolation-tubs: Поперечний розріз кристала з p-n ізоляцією
# ════════════════════════════════════════════════════════════════════════════
def fig_pn_isolation_tubs():
    W, H = 820, 420
    s = [text(W / 2, 24, "Структура p-n ізоляції монолітної ІС: кишені n-типу в p-підкладці", size=16, bold=True)]

    # Фонова кремнієва підкладка p-типу (повна глибина від поверхні вниз)
    s.append(srect(40, 95, 740, 245, SUB_P, stroke=SUB_P_DK, sw=1.5))
    s.append(text(85, 310, "Підкладка p-Si", size=12, color=SUB_P_DK, bold=True))
    s.append(text(85, 325, "N_A ~ 10¹⁵ см⁻³", size=9, color=SUB_P_DK))

    # Кишеня 1: Епітаксійний шар n-типу (n-epi) для NPN транзистора
    s.append(srect(140, 95, 230, 160, EPI_N, stroke=EPI_N_DK, sw=1.4))
    s.append(text(185, 210, "n-кишеня (n-epi)", size=10, color=EPI_N_DK, bold=True))

    # Прихований шар n⁺ (buried layer / subcollector) для кишені 1
    s.append(srect(155, 215, 200, 32, BL_N, stroke=BL_N_DK, sw=1.3))
    s.append(text(255, 236, "Прихований шар n⁺ (Buried layer)", size=10, color=BL_N_DK, bold=True))

    # Кишеня 2: Епітаксійний шар n-типу для дифузійного резистора
    s.append(srect(430, 95, 220, 160, EPI_N, stroke=EPI_N_DK, sw=1.4))
    s.append(text(600, 210, "n-кишеня (n-epi)", size=10, color=EPI_N_DK, bold=True))

    # Прихований шар n⁺ для кишені 2
    s.append(srect(445, 215, 190, 32, BL_N, stroke=BL_N_DK, sw=1.3))
    s.append(text(540, 236, "Прихований шар n⁺", size=10, color=BL_N_DK, bold=True))

    # Глибокі ізоляційні p⁺ стінки (Isolation walls)
    # Ліва ізоляційна стінка
    s.append(srect(85, 95, 55, 170, WALL_P, stroke=WALL_P_DK, sw=1.4))
    s.append(text(112, 175, "p⁺", size=13, color=WALL_P_DK, bold=True))
    s.append(text(112, 190, "ізоляція", size=9, color=WALL_P_DK))

    # Центральна ізоляційна стінка (між транзистором і резистором)
    s.append(srect(370, 95, 60, 170, WALL_P, stroke=WALL_P_DK, sw=1.4))
    s.append(text(400, 175, "p⁺", size=13, color=WALL_P_DK, bold=True))
    s.append(text(400, 190, "ізоляція", size=9, color=WALL_P_DK))

    # Права ізоляційна стінка
    s.append(srect(650, 95, 55, 170, WALL_P, stroke=WALL_P_DK, sw=1.4))
    s.append(text(677, 175, "p⁺", size=13, color=WALL_P_DK, bold=True))
    s.append(text(677, 190, "ізоляція", size=9, color=WALL_P_DK))

    # Елементи всередині Кишені 1 (NPN транзистор)
    # Дифузійна p-база
    s.append(srect(160, 95, 130, 50, BASE_P, stroke="#6c5088", sw=1.2))
    s.append(text(195, 125, "p-база", size=10, color="#5a4070", bold=True))

    # Дифузійний n⁺-емітер усередині бази
    s.append(srect(215, 95, 45, 24, EMIT_N, stroke=EMIT_DK, sw=1.2))
    s.append(text(237, 112, "n⁺ E", size=9, color=EMIT_DK, bold=True))

    # Глибокий колекторний контакт n⁺
    s.append(srect(310, 95, 45, 50, EMIT_N, stroke=BL_N_DK, sw=1.2))
    s.append(text(332, 125, "n⁺ C", size=9, color=BL_N_DK, bold=True))

    # Елементи всередині Кишені 2 (p-дифузійний резистор)
    s.append(srect(460, 95, 130, 45, BASE_P, stroke="#6c5088", sw=1.2))
    s.append(text(525, 125, "p-резистор (R)", size=10, color="#5a4070", bold=True))

    # Контакт n⁺ до тіла n-кишені резистора (підключення до VCC!)
    s.append(srect(605, 95, 35, 45, EMIT_N, stroke=BL_N_DK, sw=1.2))
    s.append(text(622, 125, "n⁺ Vcc", size=9, color=BL_N_DK, bold=True))

    # Контакт до підкладки (p-sub contact)
    s.append(srect(715, 95, 55, 170, WALL_P, stroke=WALL_P_DK, sw=1.4))
    s.append(text(742, 175, "p⁺ Sub", size=10, color=WALL_P_DK, bold=True))

    # Захисний шар діоксиду SiO₂ з вікнами
    s.append(srect(40, 80, 45, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(130, 80, 35, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(185, 80, 28, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(262, 80, 46, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(357, 80, 100, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(490, 80, 70, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(592, 80, 12, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(642, 80, 70, 15, OXID, stroke=OXID_DK, sw=1.1))
    s.append(srect(772, 80, 8, 15, OXID, stroke=OXID_DK, sw=1.1))

    # Металізація алюмінієм (Al contacts)
    # Контакт B (база)
    s.append(srect(165, 62, 20, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(175, 52, "База (B)", size=9, color=METED, bold=True))

    # Контакт E (емітер)
    s.append(srect(220, 62, 35, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(237, 52, "Емітер (E)", size=9, color=METED, bold=True))

    # Контакт C (колектор)
    s.append(srect(315, 62, 35, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(332, 52, "Колектор (C)", size=9, color=METED, bold=True))

    # Виводи резистора R1 та R2
    s.append(srect(465, 62, 24, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(477, 52, "R_in", size=9, color=METED, bold=True))

    s.append(srect(562, 62, 28, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(576, 52, "R_out", size=9, color=METED, bold=True))

    # Контакт зміщення кишені резистора до VCC
    s.append(srect(606, 62, 34, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(623, 52, "+V_CC", size=9, color=POS, bold=True))

    # Контакт зміщення підкладки до найнижчого потенціалу V_EE / GND
    s.append(srect(725, 62, 45, 20, METAL, stroke=METED, sw=1.2))
    s.append(text(747, 52, "−V_EE / GND", size=9, color=NEG, bold=True))

    # Вказівники на зворотне зміщення ізоляції
    s.append(line(747, 82, 747, 280, color=NEG, sw=1.5, dash="4,2"))
    s.append(arrow(747, 280, 500, 280, color=NEG, sw=1.5))
    s.append(text(620, 298, "Підкладка на −V_EE тримає всі p-n переходи ізоляції замкненими", size=10, color=NEG, bold=True))

    # Підписи кишень знизу
    s.append(text(255, 365, "Острівець 1: NPN транзистор", size=11, color=INK, bold=True))
    s.append(text(540, 365, "Острівець 2: Дифузійний p-резистор", size=11, color=INK, bold=True))
    s.append(text(W / 2, 395, "Глибока p⁺ дифузія змикається з p-підкладкою, утворюючи герметичну ванну навколо кожної n-кишені.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "pn-isolation-tubs.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — isolation-leakage-and-capacitance: Еквівалентна схема паразитів
# ════════════════════════════════════════════════════════════════════════════
def fig_isolation_leakage_and_capacitance():
    W, H = 780, 360
    s = [text(W / 2, 24, "Електрична модель ізоляційного переходу: бар'єрна ємність і струми завад", size=16, bold=True)]

    # Ліва частина: Фізичний розріз переходу кишеня-підкладка
    s.append(rect(30, 48, 345, 292, fill="#fdfbf9", stroke="#d0c8be", sw=1.2, rx=6))
    s.append(text(202, 72, "Фізична межа n-кишеня / p-підкладка", size=12, bold=True, color=INK))

    # n-кишеня зверху
    s.append(srect(60, 95, 285, 55, EPI_N, stroke=EPI_N_DK, sw=1.3))
    s.append(text(202, 125, "n-кишеня (потенціал V_колектора)", size=11, color=EPI_N_DK, bold=True))

    # Збіднена область посередині (діелектрик)
    s.append(srect(60, 150, 285, 45, DEP_CLR, stroke=DEP_DK, sw=1.3, dash="4,2"))
    s.append(text(202, 172, "Збіднений шар (Depletion Region, W_dep)", size=10, color="#8a7000", bold=True))
    s.append(text(202, 187, "Нерухомий просторовий заряд, носіїв нема", size=9, color="#8a7000"))

    # p-підкладка знизу
    s.append(srect(60, 195, 285, 55, SUB_P, stroke=SUB_P_DK, sw=1.3))
    s.append(text(202, 227, "p-підкладка (потенціал V_EE / GND)", size=11, color=SUB_P_DK, bold=True))

    s.append(text(202, 275, "Зворотна напруга V_R = V_n - V_p > 0", size=10, color=POS, bold=True))
    s.append(text(202, 295, "Бар'єрна ємність: C_j = ε_Si · A / W_dep(V_R)", size=10, color=INK))
    s.append(text(202, 315, "Струм витоку: I_s ~ 1-100 пА (подвоюється кожні 8-10 °C)", size=9, color=MUTED))

    # Права частина: Еквівалентна електрична схема та взаємодія кишень
    s.append(rect(400, 48, 350, 292, fill="#f9fbf9", stroke="#bed0be", sw=1.2, rx=6))
    s.append(text(575, 72, "Еквівалентна схема міжкаскадного зв'язку", size=12, bold=True, color=FIELD))

    # Вузол Кишені 1 (Швидкий цифровий каскад dV/dt)
    s.append(circle(460, 110, 5, fill=POS, stroke=INK, sw=1.2))
    s.append(text(460, 95, "Вузол 1 (dV/dt)", size=10, color=POS, bold=True))

    # Вузол Кишені 2 (Чутливий аналоговий вхід)
    s.append(circle(690, 110, 5, fill=NEG, stroke=INK, sw=1.2))
    s.append(text(690, 95, "Вузол 2 (Аналог)", size=10, color=NEG, bold=True))

    # Паразитні елементи Кишені 1 (Діод + Конденсатор C_j1)
    s.append(line(460, 115, 460, 140, color=INK, sw=1.3))
    # Конденсатор C_j1
    s.append(line(445, 140, 475, 140, color=INK, sw=1.8))
    s.append(line(445, 148, 475, 148, color=INK, sw=1.8))
    s.append(text(420, 146, "C_j1", size=10, color=INK, bold=True))
    s.append(line(460, 148, 460, 175, color=INK, sw=1.3))

    # Зворотний діод D1 паралельно
    s.append(line(490, 125, 490, 165, color=MUTED, sw=1.2))
    s.append(text(510, 146, "D_iso1", size=9, color=MUTED))

    # Паразитні елементи Кишені 2 (Конденсатор C_j2)
    s.append(line(690, 115, 690, 140, color=INK, sw=1.3))
    s.append(line(675, 140, 705, 140, color=INK, sw=1.8))
    s.append(line(675, 148, 705, 148, color=INK, sw=1.8))
    s.append(text(725, 146, "C_j2", size=10, color=INK, bold=True))
    s.append(line(690, 148, 690, 175, color=INK, sw=1.3))

    # Спільний опір підкладки R_sub
    s.append(srect(535, 168, 80, 16, "#e4dcf0", stroke=SUB_P_DK, sw=1.2))
    s.append(text(575, 180, "R_підкладки", size=9, color=SUB_P_DK, bold=True))
    s.append(line(460, 175, 535, 175, color=SUB_P_DK, sw=1.5))
    s.append(line(615, 175, 690, 175, color=SUB_P_DK, sw=1.5))

    # Підключення до GND
    s.append(line(575, 184, 575, 215, color=INK, sw=1.3))
    s.append(line(560, 215, 590, 215, color=INK, sw=1.8))
    s.append(line(566, 220, 584, 220, color=INK, sw=1.4))
    s.append(line(572, 225, 578, 225, color=INK, sw=1.0))
    s.append(text(575, 240, "GND / −V_EE", size=10, color=NEG, bold=True))

    # Струм завади i = C_j · dV/dt
    s.append(arrow(460, 120, 460, 138, color=POS, sw=1.5))
    s.append(text(485, 130, "i_зміщ", size=9, color=POS))
    s.append(arrow(530, 175, 470, 175, color=POS, sw=1.3))
    s.append(arrow(575, 175, 675, 175, color=POS, sw=1.3))
    s.append(arrow(690, 170, 690, 125, color=POS, sw=1.3))
    s.append(text(575, 275, "Швидкий фронт dV/dt інжектує ємнісний струм", size=10, color=POS, bold=True))
    s.append(text(575, 293, "через C_j1 у підкладку, створюючи на R_sub сплеск,", size=9, color=INK))
    s.append(text(575, 308, "який крізь C_j2 наводиться на сусідній аналоговий вузол 2.", size=9, color=INK))

    render(os.path.join(IMG, "isolation-leakage-and-capacitance.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — parasitic-scr-latchup: Паразитний тиристор та ефект замикання
# ════════════════════════════════════════════════════════════════════════════
def fig_parasitic_scr_latchup():
    W, H = 800, 390
    s = [text(W / 2, 24, "Паразитна чотиришарова структура p-n-p-n і тиристорне замикання (Latch-up)", size=16, bold=True)]

    # Ліва половина: Фізичне розташування шарів p-n-p-n
    s.append(rect(30, 48, 380, 315, fill="#fdfbf9", stroke="#d0c8be", sw=1.2, rx=6))
    s.append(text(220, 70, "Паразитні транзистори в структурі кристала", size=12, bold=True, color=INK))

    # p-підкладка
    s.append(srect(50, 110, 340, 185, SUB_P, stroke=SUB_P_DK, sw=1.3))
    s.append(text(95, 270, "p-підкладка", size=10, color=SUB_P_DK, bold=True))

    # Дві сусідні n-кишені (вкладені в p-підкладку)
    s.append(srect(70, 110, 140, 95, EPI_N, stroke=EPI_N_DK, sw=1.3))
    s.append(text(125, 190, "n-кишеня 1", size=9, color=EPI_N_DK))

    s.append(srect(240, 110, 130, 95, EPI_N, stroke=EPI_N_DK, sw=1.3))
    s.append(text(305, 190, "n-кишеня 2", size=9, color=EPI_N_DK))

    # p-дифузія в кишені 1
    s.append(srect(90, 110, 60, 40, BASE_P, stroke="#6c5088", sw=1.2))
    s.append(text(120, 135, "p⁺ (Vcc)", size=9, color=POS, bold=True))

    # n⁺ емітер у кишені 2
    s.append(srect(260, 110, 50, 30, EMIT_N, stroke=EMIT_DK, sw=1.2))
    s.append(text(285, 130, "n⁺ (GND)", size=9, color=NEG, bold=True))

    # Вертикальний PNP (Q1)
    s.append(circle(120, 155, 4, fill=POS, stroke=INK, sw=1.2))
    s.append(text(145, 158, "Q1 (pnp)", size=10, color=POS, bold=True))
    s.append(text(220, 310, "Вертикальний PNP: p⁺ (емітер) → n-кишеня (база) → p-підкладка (колектор)", size=9, color=INK))

    # Горизонтальний NPN (Q2)
    s.append(circle(260, 175, 4, fill=NEG, stroke=INK, sw=1.2))
    s.append(text(290, 178, "Q2 (npn)", size=10, color=NEG, bold=True))
    s.append(text(220, 328, "Горизонтальний NPN: n-кишеня (колектор) → p-підкладка (база) → n⁺ (емітер)", size=9, color=INK))
    s.append(text(220, 346, "Умова самопідтримуваного замикання: β_pnp · β_npn ≥ 1", size=10, color=POS, bold=True))

    # Права половина: Еквівалентна тиристорна схема зі зворотним зв'язком
    s.append(rect(430, 48, 340, 315, fill="#f9fbf9", stroke="#bed0be", sw=1.2, rx=6))
    s.append(text(600, 70, "Еквівалентна схема тиристора (SCR)", size=12, bold=True, color=POS))

    # Живлення VCC зверху
    s.append(circle(600, 95, 4, fill=POS, stroke=INK, sw=1.2))
    s.append(text(600, 85, "+V_CC (Анод)", size=10, color=POS, bold=True))
    s.append(line(600, 95, 600, 120, color=INK, sw=1.4))

    # Транзистор Q1 (PNP)
    s.append(line(580, 125, 580, 155, color=INK, sw=2.0))
    s.append(line(600, 120, 580, 132, color=INK, sw=1.4))
    s.append(line(600, 160, 580, 148, color=INK, sw=1.4))
    s.append(arrow(588, 127, 597, 122, color=INK, sw=1.4))
    s.append(line(580, 140, 540, 140, color=INK, sw=1.4))
    s.append(text(615, 140, "Q1 (PNP)", size=10, color=POS, bold=True))

    # Опір R_well між базою Q1 та VCC
    s.append(line(540, 110, 540, 140, color=INK, sw=1.2))
    s.append(srect(532, 110, 16, 25, "#ffffff", stroke=INK, sw=1.2))
    s.append(line(540, 110, 600, 110, color=INK, sw=1.2))
    s.append(text(510, 125, "R_well", size=9, color=MUTED))

    # Транзистор Q2 (NPN)
    s.append(line(560, 185, 560, 215, color=INK, sw=2.0))
    s.append(line(540, 180, 560, 192, color=INK, sw=1.4))
    s.append(line(540, 220, 560, 208, color=INK, sw=1.4))
    s.append(arrow(550, 214, 542, 219, color=INK, sw=1.4))
    s.append(line(560, 200, 600, 200, color=INK, sw=1.4))
    s.append(text(510, 200, "Q2 (NPN)", size=10, color=NEG, bold=True))

    # Перехресні зв'язки (позитивний зворотний зв'язок)
    s.append(line(600, 160, 600, 200, color=POS, sw=1.6))
    s.append(arrow(600, 175, 600, 185, color=POS, sw=1.5))
    s.append(text(625, 180, "I_C1 = I_B2", size=9, color=POS))

    s.append(line(540, 180, 540, 140, color=NEG, sw=1.6))
    s.append(arrow(540, 165, 540, 155, color=NEG, sw=1.5))
    s.append(text(485, 165, "I_C2 = I_B1", size=9, color=NEG))

    # Опір R_sub між базою Q2 та GND
    s.append(line(600, 200, 600, 230, color=INK, sw=1.2))
    s.append(srect(592, 230, 16, 25, "#ffffff", stroke=INK, sw=1.2))
    s.append(line(600, 255, 600, 275, color=INK, sw=1.2))
    s.append(text(630, 245, "R_sub", size=9, color=MUTED))

    # Земля GND знизу
    s.append(line(540, 220, 540, 275, color=INK, sw=1.4))
    s.append(line(540, 275, 600, 275, color=INK, sw=1.4))
    s.append(line(570, 275, 570, 290, color=INK, sw=1.4))
    s.append(line(555, 290, 585, 290, color=INK, sw=1.8))
    s.append(line(561, 295, 579, 295, color=INK, sw=1.4))
    s.append(line(567, 300, 573, 300, color=INK, sw=1.0))
    s.append(text(570, 315, "GND (Катод)", size=10, color=NEG, bold=True))

    s.append(text(600, 342, "Сплеск напруги вмикає лавиноподібне замикання Vcc на GND!", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "parasitic-scr-latchup.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — isolation-evolution-comparison: 4 покоління ізоляції
# ════════════════════════════════════════════════════════════════════════════
def fig_isolation_evolution_comparison():
    W, H = 840, 440
    s = [text(W / 2, 24, "Еволюція методів ізоляції компонентів на кремнієвому кристалі", size=16, bold=True)]

    # 4 панелі в сітці 2x2
    coords = [(35, 48), (435, 48), (35, 240), (435, 240)]
    titles = [
        "1. Дифузійна p-n ізоляція (1959–дотепер)",
        "2. Локальне окиснення LOCOS (1970-ті)",
        "3. Траншейна ізоляція STI / DTI (1980-ті–дотепер)",
        "4. Кремній на ізоляторі SOI (1990-ті–дотепер)"
    ]
    subtitles = [
        "Глибокі дифузійні p⁺ стінки, велика площа",
        "Товстий польовий оксид SiO₂ з пташиним дзьобом",
        "Вертикальні витравлені щілини з SiO₂ (нуль розмиття)",
        "Похований шар діелектрика BOX: повна розв'язка"
    ]

    for i in range(4):
        x, y = coords[i]
        pw, ph = 370, 180
        s.append(rect(x, y, pw, ph, fill="#ffffff", stroke="#d0d6dc", sw=1.1, rx=5))
        s.append(text(x + pw / 2, y + 20, titles[i], size=11, bold=True, color=INK))
        s.append(text(x + pw / 2, y + 34, subtitles[i], size=9, color=MUTED))

        # Основа підкладки
        bx, by, bw, bh = x + 20, y + 70, 330, 95
        s.append(srect(bx, by, bw, bh, SUB_P, stroke=SUB_P_DK, sw=1.1))

        if i == 0:
            # 1. Дифузійна p-n ізоляція
            s.append(srect(bx + 40, by, 100, 55, EPI_N, stroke=EPI_N_DK, sw=1.1))
            s.append(srect(bx + 190, by, 100, 55, EPI_N, stroke=EPI_N_DK, sw=1.1))
            s.append(text(bx + 90, by + 30, "n-кишеня 1", size=9, color=EPI_N_DK))
            s.append(text(bx + 240, by + 30, "n-кишеня 2", size=9, color=EPI_N_DK))

            # Широка p⁺ ізоляційна стінка
            s.append(srect(bx + 140, by, 50, 70, WALL_P, stroke=WALL_P_DK, sw=1.2))
            s.append(text(bx + 165, by + 35, "p⁺", size=11, color=WALL_P_DK, bold=True))
            s.append(text(bx + pw / 2, by + 82, "Ширина стінки ~15-25 мкм (бічна дифузія!)", size=9, color=POS, bold=True))

        elif i == 1:
            # 2. LOCOS
            s.append(srect(bx + 30, by, 115, 60, EPI_N, stroke=EPI_N_DK, sw=1.1))
            s.append(srect(bx + 185, by, 115, 60, EPI_N, stroke=EPI_N_DK, sw=1.1))
            # Польовий оксид з «пташиним дзьобом»
            s.append(srect(bx + 145, by, 40, 20, OXID, stroke=OXID_DK, sw=1.2))
            s.append(text(bx + 165, by + 14, "SiO₂", size=9, color=OXID_DK, bold=True))
            s.append(text(bx + 90, by + 30, "Активна зона", size=9, color=INK))
            s.append(text(bx + 240, by + 30, "Активна зона", size=9, color=INK))
            s.append(text(bx + pw / 2, by + 82, "Дзьоб оксиду обмежує мінімальний розмір", size=9, color=MUTED))

        elif i == 2:
            # 3. STI / DTI
            s.append(srect(bx + 30, by, 115, 60, EPI_N, stroke=EPI_N_DK, sw=1.1))
            s.append(srect(bx + 185, by, 115, 60, EPI_N, stroke=EPI_N_DK, sw=1.1))
            # Вузька вертикальна траншея STI/DTI
            s.append(srect(bx + 152, by, 26, 75, "#cde4c4", stroke="#4a7c38", sw=1.3))
            s.append(text(bx + 165, by + 35, "STI", size=9, color="#2e5c1e", bold=True))
            s.append(text(bx + 90, by + 30, "n-область", size=9, color=EPI_N_DK))
            s.append(text(bx + 240, by + 30, "n-область", size=9, color=EPI_N_DK))
            s.append(text(bx + pw / 2, by + 82, "Ширина траншеї <0.3-1 мкм, вертикальні стінки", size=9, color=FIELD, bold=True))

        elif i == 3:
            # 4. SOI (Silicon on Insulator)
            # Товстий похований шар оксиду BOX
            s.append(srect(bx, by + 40, bw, 20, OXID, stroke=OXID_DK, sw=1.2))
            s.append(text(bx + bw / 2, by + 54, "Похований оксид BOX (SiO₂, діелектрик)", size=9, color=OXID_DK, bold=True))

            # Ізольовані острівці монокристалічного кремнію над оксидом
            s.append(srect(bx + 30, by, 115, 40, EPI_N, stroke=EPI_N_DK, sw=1.1))
            s.append(srect(bx + 185, by, 115, 40, EPI_N, stroke=EPI_N_DK, sw=1.1))
            # Повне діелектричне розділення
            s.append(srect(bx + 152, by, 26, 40, "#cde4c4", stroke="#4a7c38", sw=1.2))
            s.append(text(bx + 90, by + 22, "Si-острівець 1", size=9, color=EPI_N_DK))
            s.append(text(bx + 240, by + 22, "Si-острівець 2", size=9, color=EPI_N_DK))
            s.append(text(bx + pw / 2, by + 82, "Нульова ємність до підкладки, немає Latch-up!", size=9, color=FIELD, bold=True))

    render(os.path.join(IMG, "isolation-evolution-comparison.svg"), W, H, *s)


if __name__ == "__main__":
    fig_pn_isolation_tubs()
    fig_isolation_leakage_and_capacitance()
    fig_parasitic_scr_latchup()
    fig_isolation_evolution_comparison()
    print("OK: pn-isolation-tubs.svg, isolation-leakage-and-capacitance.svg, parasitic-scr-latchup.svg, isolation-evolution-comparison.svg -> ./img/")
