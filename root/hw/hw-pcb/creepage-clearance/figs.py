# -*- coding: utf-8 -*-
"""Фігури для теми creepage-clearance (зазори на платі).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER      = "#b5763a"
COPPER_FILL = "#e8c9a3"
CORE        = "#dfe6ee"
PREPREG     = "#eef1e6"
MASK        = "#2d6a4f"
MASK_FILL   = "#d8f3dc"


# ── 1. Clearance проти Creepage: повітряний зазор і шлях витоку ───────────────
def fig_clearance_creepage():
    W, H = 780, 420
    frags = []

    # Заголовок / шапка схеми
    frags.append(rect(10, 10, 760, 400, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))

    # Ліва сцена: Пласка поверхня
    x0, y0 = 40, 60
    frags.append(text(x0 + 150, y0 + 15, "Пласка плата", size=13, color=INK, bold=True))

    # Текстоліт FR-4
    frags.append(rect(x0, y0 + 140, 300, 50, fill=CORE, stroke="#94a3b8", sw=1.5, rx=3))
    frags.append(text(x0 + 150, y0 + 170, "Діелектрик плати (FR-4)", size=11, color=MUTED))

    # Мідні провідники
    frags.append(rect(x0 + 20, y0 + 120, 60, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=2))
    frags.append(text(x0 + 50, y0 + 112, "Провідник 1", size=11, color=POS, bold=True))
    frags.append(text(x0 + 50, y0 + 134, "HV (+400 В)", size=9, color=POS))

    frags.append(rect(x0 + 220, y0 + 120, 60, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=2))
    frags.append(text(x0 + 250, y0 + 112, "Провідник 2", size=11, color=NEG, bold=True))
    frags.append(text(x0 + 250, y0 + 134, "GND (0 В)", size=9, color=NEG))

    # Clearance стрілка (по повітрю, пряма)
    frags.append(line(x0 + 80, y0 + 100, x0 + 220, y0 + 100, color=POS, sw=2.0, dash="5,4"))
    frags.append(circle(x0 + 80, y0 + 100, 3, fill=POS, stroke=POS))
    frags.append(circle(x0 + 220, y0 + 100, 3, fill=POS, stroke=POS))
    frags.append(text(x0 + 150, y0 + 92, "Clearance: по повітрю", size=11, color=POS, bold=True))

    # Creepage стрілка (по поверхні)
    frags.append(line(x0 + 80, y0 + 140, x0 + 220, y0 + 140, color=NEG, sw=2.2))
    frags.append(circle(x0 + 80, y0 + 140, 3, fill=NEG, stroke=NEG))
    frags.append(circle(x0 + 220, y0 + 140, 3, fill=NEG, stroke=NEG))
    frags.append(text(x0 + 150, y0 + 130, "Creepage: по поверхні", size=11, color=NEG, bold=True))

    b1, _, _ = textbox(x0 + 150, y0 + 255,
                       ["На пласкій поверхні без ребер і пазів:",
                        "Clearance = Creepage (однакова довжина)."],
                       size=11, fill="#f8fafc", stroke="#cbd5e1", pad=8)
    frags.append(b1)

    # Розділювальна лінія
    frags.append(line(390, 40, 390, 370, color="#e2e8f0", sw=1.5))

    # Права сцена: Поверхня з рельєфом / бар'єром
    x1 = 430
    frags.append(text(x1 + 150, y0 + 15, "Плата з ізоляційним бар'єром", size=13, color=INK, bold=True))

    # Текстоліт FR-4
    frags.append(rect(x1, y0 + 140, 300, 50, fill=CORE, stroke="#94a3b8", sw=1.5, rx=3))
    frags.append(text(x1 + 150, y0 + 170, "Діелектрик плати (FR-4)", size=11, color=MUTED))

    # Ізоляційний бар'єр (ребро) посередині
    frags.append(rect(x1 + 135, y0 + 60, 30, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(x1 + 150, y0 + 50, "Бар'єр", size=10, color="#d97706", bold=True))

    # Мідні провідники
    frags.append(rect(x1 + 20, y0 + 120, 60, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=2))
    frags.append(text(x1 + 50, y0 + 112, "Провідник 1", size=11, color=POS, bold=True))
    frags.append(text(x1 + 50, y0 + 134, "HV (+400 В)", size=9, color=POS))

    frags.append(rect(x1 + 220, y0 + 120, 60, 20, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=2))
    frags.append(text(x1 + 250, y0 + 112, "Провідник 2", size=11, color=NEG, bold=True))
    frags.append(text(x1 + 250, y0 + 134, "GND (0 В)", size=9, color=NEG))

    # Clearance стрілка (через повітря по верхівці бар'єра)
    frags.append(line(x1 + 80, y0 + 120, x1 + 135, y0 + 60, color=POS, sw=1.8, dash="5,4"))
    frags.append(line(x1 + 165, y0 + 60, x1 + 220, y0 + 120, color=POS, sw=1.8, dash="5,4"))
    frags.append(circle(x1 + 80, y0 + 120, 3, fill=POS, stroke=POS))
    frags.append(circle(x1 + 220, y0 + 120, 3, fill=POS, stroke=POS))
    frags.append(text(x1 + 85, y0 + 80, "Clearance", size=10, color=POS, bold=True))

    # Creepage ламана лінія (вздовж контуру ребра)
    frags.append(line(x1 + 80, y0 + 140, x1 + 135, y0 + 140, color=NEG, sw=2.2))
    frags.append(line(x1 + 135, y0 + 140, x1 + 135, y0 + 60, color=NEG, sw=2.2))
    frags.append(line(x1 + 135, y0 + 60, x1 + 165, y0 + 60, color=NEG, sw=2.2))
    frags.append(line(x1 + 165, y0 + 60, x1 + 165, y0 + 140, color=NEG, sw=2.2))
    frags.append(line(x1 + 165, y0 + 140, x1 + 220, y0 + 140, color=NEG, sw=2.2))
    frags.append(circle(x1 + 80, y0 + 140, 3, fill=NEG, stroke=NEG))
    frags.append(circle(x1 + 220, y0 + 140, 3, fill=NEG, stroke=NEG))
    frags.append(text(x1 + 215, y0 + 95, "Creepage", size=10, color=NEG, bold=True))

    b2, _, _ = textbox(x1 + 150, y0 + 255,
                       ["Бар'єр подовжує шлях по поверхні:",
                        "Creepage значно більший за Clearance."],
                       size=11, fill="#f8fafc", stroke="#cbd5e1", pad=8)
    frags.append(b2)

    # Загальний підсумок знизу
    b_bot, _, _ = textbox(390, 365,
                          ["Clearance: найкоротший шлях через повітря (захист від іскрового пробою газу).",
                           "Creepage: найкоротший шлях уздовж діелектрика (захист від поверхневого трекінгу)."],
                          size=11, fill="#f0fdf4", stroke=FIELD, pad=8)
    frags.append(b_bot)

    render(os.path.join(OUT, "clearance-vs-creepage.svg"), W, H, *frags,
           title="Геометрія Clearance та Creepage на друкованій платі")


# ── 2. Механізм утворення поверхневого трекінгу (Tracking) ────────────────────
def fig_tracking_stages():
    W, H = 840, 480
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))
    frags.append(text(420, 35, "4 стадії поверхневого пробою діелектрика (Carbon Tracking)",
                      size=14, color=INK, bold=True))

    stages = [
        ("1. Забруднення й волога",
         "Пил, солі та конденсат утворюють",
         "тонку електропровідну плівку",
         "#eff6ff", "#3b82f6"),
        ("2. Струм витоку й суха зона",
         "Джоулів нагрів випаровує вологу;",
         "утворюється суха щілина (dry band)",
         "#fefce8", "#eab308"),
        ("3. Мікродуги (сцинтиляції)",
         "Поле в щілині стрибає до кВ/мм;",
         "спалахують іскри, піроліз смоли",
         "#fff7ed", "#f97316"),
        ("4. Вугільний місток",
         "Виділяється струмопровідний",
         "вуглець; незворотне КЗ діелектрика",
         "#fef2f2", "#ef4444"),
    ]

    gw, gh = 190, 350
    y_top = 65

    for i, (title, l1, l2, bg_col, brd_col) in enumerate(stages):
        x_st = 25 + i * 200
        frags.append(rect(x_st, y_top, gw, gh, fill=bg_col, stroke=brd_col, sw=1.4, rx=6))
        frags.append(text(x_st + gw/2, y_top + 25, title, size=11, color=brd_col, bold=True))

        # Текстоліт в розрізі
        py = y_top + 130
        frags.append(rect(x_st + 15, py, gw - 30, 40, fill=CORE, stroke="#94a3b8", sw=1.2, rx=2))
        frags.append(text(x_st + gw/2, py + 25, "FR-4", size=10, color=MUTED))

        # Електроди зліва і справа
        frags.append(rect(x_st + 15, py - 12, 32, 12, fill=COPPER_FILL, stroke=COPPER, sw=1.2, rx=1))
        frags.append(text(x_st + 31, py - 16, "+HV", size=9, color=POS, bold=True))

        frags.append(rect(x_st + gw - 47, py - 12, 32, 12, fill=COPPER_FILL, stroke=COPPER, sw=1.2, rx=1))
        frags.append(text(x_st + gw - 31, py - 16, "GND", size=9, color=NEG, bold=True))

        # Специфіка для кожної стадії
        if i == 0:
            # Плівка вологи
            frags.append(rect(x_st + 47, py - 4, gw - 94, 4, fill="#60a5fa", stroke="#3b82f6", sw=0.8))
            frags.append(text(x_st + gw/2, py - 8, "плівка вологи", size=9, color="#1d4ed8"))
        elif i == 1:
            # Плівка з сухою зоною посередині
            frags.append(rect(x_st + 47, py - 4, 30, 4, fill="#60a5fa", stroke="#3b82f6", sw=0.8))
            frags.append(rect(x_st + gw - 77, py - 4, 30, 4, fill="#60a5fa", stroke="#3b82f6", sw=0.8))
            # суха зона
            frags.append(rect(x_st + 80, py - 4, 30, 4, fill="#ffffff", stroke="#eab308", sw=1.0))
            frags.append(text(x_st + gw/2, py - 8, "Dry Band", size=9, color="#b45309", bold=True))
            # стрілки струму
            frags.append(line(x_st + 48, py + 6, x_st + 78, py + 6, color="#eab308", sw=1.5, dash="2,2"))
        elif i == 2:
            # Іскри над сухою зоною
            frags.append(rect(x_st + 47, py - 4, 25, 4, fill="#60a5fa", stroke="#3b82f6", sw=0.8))
            frags.append(rect(x_st + gw - 72, py - 4, 25, 4, fill="#60a5fa", stroke="#3b82f6", sw=0.8))
            # іскра / мікродуга
            frags.append(circle(x_st + gw/2, py - 2, 7, fill="#ffedd5", stroke="#ea580c", sw=1.2))
            frags.append(text(x_st + gw/2, py - 10, "Мікродуга!", size=9, color="#c2410c", bold=True))
            frags.append(text(x_st + gw/2, py + 12, ">1000 °C", size=9, color="#c2410c"))
        elif i == 3:
            # Чорний вугільний місток
            frags.append(rect(x_st + 47, py - 4, gw - 94, 5, fill="#18181b", stroke="#000000", sw=1.2))
            frags.append(text(x_st + gw/2, py - 8, "Вугільний трек (С)", size=9, color="#000000", bold=True))
            frags.append(text(x_st + gw/2, py + 12, "R -> 0 Ом (КЗ)", size=9, color=POS, bold=True))

        # Опис внизу картки через mtext
        frags.append(mtext(x_st + gw/2, y_top + 270, [l1, l2], size=10, color=INK))

        # Стрілка переходу між стадіями
        if i < 3:
            frags.append(arrow(x_st + gw + 2, y_top + 140, x_st + gw + 8, y_top + 140, color=MUTED, sw=2.0))

    b_info, _, _ = textbox(420, 440,
                           ["CTI (Comparative Tracking Index) визначає стійкість смоли до мікродуг.",
                            "FR-4 (Group IIIa, CTI 175...250 В) схильний до швидкого обвуглення у вологому середовищі."],
                           size=10, fill="#f8fafc", stroke=MUTED, pad=6)
    frags.append(b_info)

    render(os.path.join(OUT, "tracking-mechanism.svg"), W, H, *frags,
           title="Механізм розвитку поверхневого трекінгу та карбонізації діелектрика")


# ── 3. Ізоляційний паз (Isolation Slot) під оптопарою ─────────────────────────
def fig_isolation_slot():
    W, H = 800, 460
    frags = []

    frags.append(rect(10, 10, 780, 440, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))
    frags.append(text(400, 35, "Ізоляційний паз (Slot) у платі: подовження Creepage під оптопарою",
                      size=13, color=INK, bold=True))

    # Ліва частина: оптопара на пласкій платі
    x0 = 40
    y0 = 60
    frags.append(text(x0 + 160, y0 + 20, "Без прорізу (пласка плата)", size=12, color=POS, bold=True))

    # Корпус оптопари DIP-4
    frags.append(rect(x0 + 100, y0 + 45, 120, 55, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=3))
    frags.append(text(x0 + 160, y0 + 76, "Оптопара DIP-4", size=11, color="#f8fafc", bold=True))

    # Виводи
    frags.append(rect(x0 + 70, y0 + 75, 30, 8, fill="#94a3b8", stroke="#475569", sw=1.0))
    frags.append(rect(x0 + 220, y0 + 75, 30, 8, fill="#94a3b8", stroke="#475569", sw=1.0))

    # Плата FR-4
    frags.append(rect(x0 + 30, y0 + 130, 260, 45, fill=CORE, stroke="#94a3b8", sw=1.5, rx=2))
    frags.append(text(x0 + 60, y0 + 155, "FR-4", size=10, color=MUTED))

    # Контактні площадки
    frags.append(rect(x0 + 65, y0 + 124, 30, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(text(x0 + 80, y0 + 115, "HV", size=10, color=POS, bold=True))

    frags.append(rect(x0 + 225, y0 + 124, 30, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(text(x0 + 240, y0 + 115, "SELV", size=10, color=NEG, bold=True))

    # Creepage шлях
    frags.append(line(x0 + 95, y0 + 127, x0 + 225, y0 + 127, color=NEG, sw=2.2))
    frags.append(circle(x0 + 95, y0 + 127, 3, fill=NEG, stroke=NEG))
    frags.append(circle(x0 + 225, y0 + 127, 3, fill=NEG, stroke=NEG))
    frags.append(text(x0 + 160, y0 + 120, "Creepage = 6.0 мм", size=10, color=NEG, bold=True))

    t1, _, _ = textbox(x0 + 160, y0 + 230,
                       ["Шлях витоку обмежений відстанню",
                        "між контактними майданчиками (6.0 мм).",
                        "Недостатньо для посиленої ізоляції (>=8.0 мм)!"],
                       size=10, fill="#fef2f2", stroke=POS, pad=6)
    frags.append(t1)

    # Розділювач
    frags.append(line(380, 50, 380, 370, color="#e2e8f0", sw=1.5))

    # Права частина: оптопара з наскрізним пазом
    x1 = 420
    frags.append(text(x1 + 170, y0 + 20, "З фрезерованим пазом (Slot)", size=12, color=FIELD, bold=True))

    # Корпус оптопари DIP-4
    frags.append(rect(x1 + 110, y0 + 45, 120, 55, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=3))
    frags.append(text(x1 + 170, y0 + 76, "Оптопара DIP-4", size=11, color="#f8fafc", bold=True))

    # Виводи
    frags.append(rect(x1 + 80, y0 + 75, 30, 8, fill="#94a3b8", stroke="#475569", sw=1.0))
    frags.append(rect(x1 + 230, y0 + 75, 30, 8, fill="#94a3b8", stroke="#475569", sw=1.0))

    # Плата FR-4 з наскрізним вирізом
    frags.append(rect(x1 + 40, y0 + 130, 100, 45, fill=CORE, stroke="#94a3b8", sw=1.5, rx=2))
    frags.append(rect(x1 + 200, y0 + 130, 100, 45, fill=CORE, stroke="#94a3b8", sw=1.5, rx=2))
    # Виріз (паз)
    frags.append(rect(x1 + 140, y0 + 130, 60, 45, fill="#ffffff", stroke="#64748b", sw=1.5))
    frags.append(text(x1 + 170, y0 + 155, "Паз (Slot)", size=10, color="#64748b", bold=True))
    frags.append(text(x1 + 170, y0 + 168, "ширина 2.0 мм", size=9, color=MUTED))

    # Контактні площадки
    frags.append(rect(x1 + 75, y0 + 124, 30, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(text(x1 + 90, y0 + 115, "HV", size=10, color=POS, bold=True))

    frags.append(rect(x1 + 235, y0 + 124, 30, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(text(x1 + 250, y0 + 115, "SELV", size=10, color=NEG, bold=True))

    # Creepage ламана лінія (вниз по стінці, через повітря/зворотний бік і вгору)
    frags.append(line(x1 + 105, y0 + 127, x1 + 140, y0 + 127, color=FIELD, sw=2.2))
    frags.append(line(x1 + 140, y0 + 127, x1 + 140, y0 + 175, color=FIELD, sw=2.2))
    frags.append(line(x1 + 140, y0 + 175, x1 + 200, y0 + 175, color=FIELD, sw=2.2))
    frags.append(line(x1 + 200, y0 + 175, x1 + 200, y0 + 127, color=FIELD, sw=2.2))
    frags.append(line(x1 + 200, y0 + 127, x1 + 235, y0 + 127, color=FIELD, sw=2.2))
    frags.append(circle(x1 + 105, y0 + 127, 3, fill=FIELD, stroke=FIELD))
    frags.append(circle(x1 + 235, y0 + 127, 3, fill=FIELD, stroke=FIELD))

    t2, _, _ = textbox(x1 + 170, y0 + 230,
                       ["Шлях витоку змушений огинати паз:",
                        "Creepage = 6.0 мм + 2 * (товщина 1.6 мм) = 9.2 мм!",
                        "Вимогу посиленої ізоляції виконано без зміни деталі."],
                       size=10, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(t2)

    # Правило мінімальної ширини паза
    b_rule, _, _ = textbox(400, 395,
                           ["Правило IEC 60664-1: паз шириною < 1.0 мм (PD 2) або < 1.5 мм (PD 3) не зараховується,",
                            "бо може бути перекритий пилом і вологою. Стандартна фреза — 1.5...2.0 мм."],
                           size=10, fill="#fffbeb", stroke="#d97706", pad=8)
    frags.append(b_rule)

    render(os.path.join(OUT, "isolation-slot-geometry.svg"), W, H, *frags,
           title="Конструкція ізоляційного паза та розрахунок збільшення Creepage")


# ── 4. Бар'єр ізоляції на платі живлення (Mains vs SELV) ──────────────────────
def fig_isolation_barrier():
    W, H = 840, 470
    frags = []

    frags.append(rect(10, 10, 820, 450, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))
    frags.append(text(420, 35, "Розподіл зон безпеки на платі блоку живлення (Primary Mains vs Secondary SELV)",
                      size=13, color=INK, bold=True))

    # Зона первинного кола (Primary HV) - зліва
    x_pri = 30
    w_pri = 320
    y_b = 60
    h_b = 320
    frags.append(rect(x_pri, y_b, w_pri, h_b, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=6))
    frags.append(text(x_pri + w_pri/2, y_b + 25, "ПЕРВИННЕ КОЛО (Primary HV)", size=12, color=POS, bold=True))
    frags.append(text(x_pri + w_pri/2, y_b + 42, "230 В AC / 400 В DC (Небезпечно для життя)", size=10, color=POS))

    # Компоненти первинного кола
    frags.append(rect(x_pri + 20, y_b + 65, 80, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    frags.append(text(x_pri + 60, y_b + 95, "Вхід 230 В", size=10, color=POS, bold=True))

    frags.append(rect(x_pri + 120, y_b + 65, 80, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    frags.append(text(x_pri + 160, y_b + 95, "EMI фільтр", size=10, color=POS))

    frags.append(rect(x_pri + 220, y_b + 65, 85, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    frags.append(text(x_pri + 262, y_b + 95, "Міст + 400 В", size=10, color=POS))

    frags.append(rect(x_pri + 60, y_b + 140, 100, 60, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    frags.append(text(x_pri + 110, y_b + 175, "ШІМ + Ключ", size=10, color=POS))

    frags.append(rect(x_pri + 20, y_b + 220, 280, 80, fill="#fca5a5", stroke=POS, sw=1.2, rx=3))
    frags.append(text(x_pri + 160, y_b + 255, "Полігон Primary GND", size=11, color=POS, bold=True))
    frags.append(text(x_pri + 160, y_b + 275, "Заборонено наближати до бар'єра менше 6.4 мм", size=9, color="#991b1b"))

    # Межі ізоляційного бар'єра (без суцільного прямокутника-тла, щоб не було перекриття з деталями)
    x_bar_l = 350
    x_bar_r = 490
    frags.append(line(x_bar_l, y_b, x_bar_l, y_b + h_b, color="#64748b", sw=1.5, dash="5,4"))
    frags.append(line(x_bar_r, y_b, x_bar_r, y_b + h_b, color="#64748b", sw=1.5, dash="5,4"))
    frags.append(text(420, y_b + 20, "Ізоляційний", size=10, color="#475569", bold=True))
    frags.append(text(420, y_b + 34, "бар'єр (Moat)", size=10, color="#475569", bold=True))

    # Компоненти, що перетинають бар'єр
    # 1. Трансформатор
    frags.append(rect(330, y_b + 60, 180, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(420, y_b + 90, "Імпульсний трансформатор", size=10, color="#92400e", bold=True))
    frags.append(text(420, y_b + 107, "Потрійна ізоляція (TIW) / Split Bobbin", size=9, color="#92400e"))

    # 2. Оптопара зворотного зв'язку
    frags.append(rect(370, y_b + 150, 100, 45, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=3))
    frags.append(text(420, y_b + 175, "Оптопара", size=10, color="#f8fafc", bold=True))
    frags.append(rect(405, y_b + 195, 30, 20, fill="#ffffff", stroke="#64748b", sw=1.2))
    frags.append(text(420, y_b + 209, "Паз", size=9, color="#64748b"))

    # 3. Y-конденсатор безпеки
    frags.append(rect(375, y_b + 235, 90, 45, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=3))
    frags.append(text(420, y_b + 258, "Y1 Конденсатор", size=10, color="#1d4ed8", bold=True))
    frags.append(text(420, y_b + 272, "Safety Class", size=9, color="#1d4ed8"))

    # Зона вторинного кола (Secondary SELV) - справа
    x_sec = 490
    w_sec = 320
    frags.append(rect(x_sec, y_b, w_sec, h_b, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(x_sec + w_sec/2, y_b + 25, "ВТОРИННЕ КОЛО (Secondary SELV)", size=12, color=FIELD, bold=True))
    frags.append(text(x_sec + w_sec/2, y_b + 42, "5 В / 12 В DC (Безпечно для дотику людини)", size=10, color=FIELD))

    # Компоненти вторинного кола
    frags.append(rect(x_sec + 25, y_b + 65, 80, 50, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(x_sec + 65, y_b + 95, "Випрямляч", size=10, color=FIELD))

    frags.append(rect(x_sec + 120, y_b + 65, 80, 50, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(x_sec + 160, y_b + 95, "LC фільтр", size=10, color=FIELD))

    frags.append(rect(x_sec + 215, y_b + 65, 85, 50, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(x_sec + 257, y_b + 95, "USB / клеми", size=10, color=FIELD, bold=True))

    frags.append(rect(x_sec + 50, y_b + 140, 100, 50, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(x_sec + 100, y_b + 170, "TL431 опора", size=10, color=FIELD))

    frags.append(rect(x_sec + 20, y_b + 220, 280, 80, fill="#bbf7d0", stroke=FIELD, sw=1.2, rx=3))
    frags.append(text(x_sec + 160, y_b + 255, "Полігон Secondary GND", size=11, color=FIELD, bold=True))
    frags.append(text(x_sec + 160, y_b + 275, "Гальванічно ізольована від вхідної мережі", size=9, color="#166534"))

    # Розмірна стрілка бар'єра
    frags.append(line(x_bar_l, y_b + 310, x_bar_r, y_b + 310, color="#dc2626", sw=2.0))
    frags.append(circle(x_bar_l, y_b + 310, 3, fill="#dc2626", stroke="#dc2626"))
    frags.append(circle(x_bar_r, y_b + 310, 3, fill="#dc2626", stroke="#dc2626"))
    frags.append(text(420, y_b + 302, "Посилена ізоляція >= 6.4...8.0 мм", size=10, color="#dc2626", bold=True))

    # Інженерне правило внизу
    b_bar, _, _ = textbox(420, 415,
                          ["У зоні бар'єра суворо заборонено мідні полігони, сигнальні доріжки та звичайні перехідні отвори (via).",
                           "Єдині компоненти, дозволені на кордоні — сертифіковані елементи гальванорозв'язки (Safety Approved)."],
                          size=10, fill="#f8fafc", stroke=MUTED, pad=6)
    frags.append(b_bar)

    render(os.path.join(OUT, "pollution-and-isolation-zones.svg"), W, H, *frags,
           title="Правила трасування ізоляційного бар'єра та зон безпеки")


def main():
    fig_clearance_creepage()
    fig_tracking_stages()
    fig_isolation_slot()
    fig_isolation_barrier()
    print("Всі фігури для creepage-clearance згенеровано успішно.")


if __name__ == "__main__":
    main()
