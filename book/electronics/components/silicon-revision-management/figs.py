# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

REDBG   = "#fdf2f2"
GRNBG   = "#f0fdf4"
BLUEBG  = "#eff6ff"
AMBER   = "#d97706"
AMBERBG = "#fffbeb"
PURPLE  = "#7c3aed"
PURPLEBG= "#f5f3ff"


def fig_stepping_fix_types():
    W, H = 820, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Title
    p.append(text(W / 2, 28, "Типи маскових виправлень кремнієвих кристалів", size=16, color=INK, bold=True))

    # Left Column: Metal-layer ECO Fix (A0 -> A1)
    x1, y1, w1, h1 = 30, 55, 365, 335
    p.append(rect(x1, y1, w1, h1, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(rect(x1 + 15, y1 + 15, w1 - 30, 36, fill="#dbeafe", stroke=NEG, sw=1, rx=4))
    p.append(text(x1 + w1/2, y1 + 38, "Металева ревізія: Metal-Only ECO (A0 → A1)", size=12, color=NEG, bold=True))

    # Stack illustration Left
    sy = y1 + 65
    p.append(rect(x1 + 25, sy, w1 - 50, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(x1 + w1/2, sy + 25, "Верхні шари металізації (M5...M8) — ЗМІНЕНО", size=11, color=POS, bold=True))

    p.append(rect(x1 + 25, sy + 46, w1 - 50, 32, fill="#e2e8f0", stroke=LINE, sw=1, rx=3))
    p.append(text(x1 + w1/2, sy + 66, "Нижні шари металізації (M1...M4) — БЕЗ ЗМІН", size=10, color=MUTED))

    p.append(rect(x1 + 25, sy + 84, w1 - 50, 42, fill="#e2e8f0", stroke=LINE, sw=1, rx=3))
    p.append(text(x1 + w1/2, sy + 102, "Базові шари: кремній, дифузія, полікремній", size=10, color=MUTED))
    p.append(text(x1 + w1/2, sy + 118, "Резервні вентилі (Spare Cells) підключено металом", size=9, color=NEG, italic=True))

    # Attributes Left
    ay = sy + 140
    attrs_l = [
        ("• Маски:", "Заміна лише 2–4 фотошаблонів металу"),
        ("• Вартість:", "Низька (~10–20% вартості повного комплекту)"),
        ("• Час фабрикації:", "3–6 тижнів (заготовки чекають перед металом)"),
        ("• Застосування:", "Логічні баги, переприв'язка на spare cells")
    ]
    for label, val in attrs_l:
        p.append(text(x1 + 20, ay, label, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x1 + 110, ay, val, size=10, color=INK, anchor="start"))
        ay += 26

    # Right Column: Base-layer / All-layer Fix (A1 -> B0)
    x2, y2, w2, h2 = 425, 55, 365, 335
    p.append(rect(x2, y2, w2, h2, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=8))
    p.append(rect(x2 + 15, y2 + 15, w2 - 30, 36, fill="#fef3c7", stroke=AMBER, sw=1, rx=4))
    p.append(text(x2 + w2/2, y2 + 38, "Базова ревізія: All-Layer / Base Tapeout (A1 → B0)", size=12, color=AMBER, bold=True))

    # Stack illustration Right
    sy2 = y2 + 65
    p.append(rect(x2 + 25, sy2, w2 - 50, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(x2 + w2/2, sy2 + 25, "Усі шари металізації (M1...Mn) — ЗМІНЕНО", size=11, color=POS, bold=True))

    p.append(rect(x2 + 25, sy2 + 46, w2 - 50, 32, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(x2 + w2/2, sy2 + 66, "Полікремній, затвори, контакти — ЗМІНЕНО", size=10, color=POS, bold=True))

    p.append(rect(x2 + 25, sy2 + 84, w2 - 50, 42, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(x2 + w2/2, sy2 + 102, "Базові шари: геометрія транзисторів, імплантація", size=10, color=POS, bold=True))
    p.append(text(x2 + w2/2, sy2 + 118, "Повна перебудова топології та розміщення блоків", size=9, color=AMBER, italic=True))

    # Attributes Right
    ay2 = sy2 + 140
    attrs_r = [
        ("• Маски:", "Повний комплект фотошаблонів (30–80+ масок)"),
        ("• Вартість:", "Максимальна ($1M–$15M+ залежно від техпроцесу)"),
        ("• Час фабрикації:", "3–6 місяців (повний цикл вирощування кристала)"),
        ("• Застосування:", "Фізичні вади, аналогові блоки, таймінг, оптимізація")
    ]
    for label, val in attrs_r:
        p.append(text(x2 + 20, ay2, label, size=11, color=INK, anchor="start", bold=True))
        p.append(text(x2 + 110, ay2, val, size=10, color=INK, anchor="start"))
        ay2 += 26

    # Bottom footer note
    p.append(text(W / 2, 408, "Зміна цифри (A0→A1) = металевий фікс; зміна літери (A1→B0) = базова модифікація масок.", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "stepping-fix-types.svg"), W, H, *p,
           title="Типи маскових виправлень кремнієвих кристалів")


def fig_errata_resolution_flow():
    W, H = 840, 430
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Життєвий цикл та способи компенсації апаратних дефектів (Silicon Errata)", size=15, color=INK, bold=True))

    # Top Box: Discovery & Errata Sheet
    bx, by, bw, bh = 220, 50, 400, 60
    p.append(rect(bx, by, bw, bh, fill=REDBG, stroke=POS, sw=1.8, rx=6))
    p.append(text(bx + bw/2, by + 24, "Виявлення дефекту кристала (Silicon Bug)", size=13, color=POS, bold=True))
    p.append(text(bx + bw/2, by + 44, "Документування в Errata Sheet: тригер, зачеплені ревізії, вплив", size=10, color=INK))

    # Arrow Down to Decision/Triage
    arrow_y1 = by + bh
    arrow_y2 = 150
    p.append(line(W/2, arrow_y1, W/2, arrow_y2, color=LINE, sw=1.5))
    p.append(line(100, arrow_y2, 740, arrow_y2, color=LINE, sw=1.5))

    # 4 Columns of Mitigations
    cols = [
        {
            "x": 20, "w": 185, "title": "1. Мікрокод CPU", "sub": "Patch RAM / ROM",
            "bg": PURPLEBG, "stroke": PURPLE,
            "desc": ["• Патч інструкцій", "• Заміна мікрокоду", "• Прозоро для ОС", "• Завантаження BIOS/UEFI"],
            "cost": "Час: дні | Швидкість: 0–5%"
        },
        {
            "x": 225, "w": 185, "title": "2. Chicken Bits", "sub": "MSR / Control Flags",
            "bg": AMBERBG, "stroke": AMBER,
            "desc": ["• Апаратний вимикач", "• Блокування оптимізацій", "• Вимикання спекуляцій", "• Усуває збій схеми"],
            "cost": "Час: хвилини | Падіння: 5–20%"
        },
        {
            "x": 430, "w": 185, "title": "3. Софтверний Workaround", "sub": "OS Driver Quirk Table",
            "bg": BLUEBG, "stroke": NEG,
            "desc": ["• Детекція за REVID", "• Обхідна логіка в коді", "• Програмне скидання FIFO", "• Введення затримок"],
            "cost": "Час: тижні | Витрати CPU"
        },
        {
            "x": 635, "w": 185, "title": "4. Новий Tapeout", "sub": "Metal ECO / Base Stepping",
            "bg": GRNBG, "stroke": FIELD,
            "desc": ["• Апаратне усунення", "• Чистий фікс у кремнії", "• Відновлення швидкості", "• Для нових партій"],
            "cost": "Час: 1–6 міс | Кошти: високі"
        }
    ]

    for col in cols:
        cx, cw = col["x"], col["w"]
        # Downward arrow to box
        p.append(arrow(cx + cw/2, arrow_y2, cx + cw/2, 175, color=LINE, sw=1.5))
        # Box
        p.append(rect(cx, 175, cw, 215, fill=col["bg"], stroke=col["stroke"], sw=1.5, rx=6))
        p.append(text(cx + cw/2, 198, col["title"], size=12, color=col["stroke"], bold=True))
        p.append(text(cx + cw/2, 214, col["sub"], size=9, color=MUTED, italic=True))
        p.append(line(cx + 10, 222, cx + cw - 10, 222, color=col["stroke"], sw=0.8, dash="2,2"))

        dy = 242
        for line_txt in col["desc"]:
            p.append(text(cx + 12, dy, line_txt, size=10, color=INK, anchor="start"))
            dy += 22

        # Cost badge
        p.append(rect(cx + 8, 350, cw - 16, 28, fill="#ffffff", stroke=col["stroke"], sw=1, rx=3))
        p.append(text(cx + cw/2, 368, col["cost"], size=9, color=col["stroke"], bold=True))

    p.append(text(W / 2, 416, "Стратегія захисту: негайний програмний обхід для наявного кремнію + апаратний фікс у наступній ревізії.", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "errata-resolution-flow.svg"), W, H, *p,
           title="Життєвий цикл та способи компенсації апаратних дефектів")


def fig_pcn_pdn_timeline():
    W, H = 840, 390
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Промислове сповіщення про життєвий цикл компонентів (JESD46 / JESD48)", size=15, color=INK, bold=True))

    # Timeline Bar
    axis_y = 170
    p.append(arrow(40, axis_y, 805, axis_y, color=LINE, sw=2.5))

    # Milestones along timeline
    # 1. PCN Issued (x=90)
    # 2. First Ship Rev B (x=270)
    # 3. PDN Issued (x=450)
    # 4. LTB (x=610)
    # 5. LTS / EOL (x=770)

    # Marker 1: PCN
    p.append(circle(90, axis_y, 6, fill=NEG, stroke="#ffffff", sw=2))
    p.append(rect(40, 60, 130, 75, fill=BLUEBG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(105, 80, "PCN Issued", size=11, color=NEG, bold=True))
    p.append(text(105, 96, "JEDEC JESD46", size=9, color=MUTED))
    p.append(text(105, 112, "Зміна ревізії / FAB", size=9, color=INK))
    p.append(text(105, 126, "або зварювання", size=9, color=INK))
    p.append(line(90, 135, 90, axis_y - 6, color=NEG, sw=1.2, dash="3,3"))

    # Range 1: 90 days qualification
    p.append(rect(90, axis_y + 15, 180, 42, fill="#dbeafe", stroke=NEG, sw=1, rx=3))
    p.append(text(180, axis_y + 32, "Кваліфікаційне вікно", size=10, color=NEG, bold=True))
    p.append(text(180, axis_y + 47, "Мінімум 90 днів (JESD46)", size=9, color=INK))
    p.append(line(90, axis_y + 10, 90, axis_y + 60, color=NEG, sw=1))
    p.append(line(270, axis_y + 10, 270, axis_y + 60, color=NEG, sw=1))

    # Marker 2: First Ship
    p.append(circle(270, axis_y, 6, fill=FIELD, stroke="#ffffff", sw=2))
    p.append(rect(205, 60, 130, 75, fill=GRNBG, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(270, 80, "First Shipment", size=11, color=FIELD, bold=True))
    p.append(text(270, 96, "Нова ревізія (Rev B)", size=9, color=MUTED))
    p.append(text(270, 112, "Початок масових", size=9, color=INK))
    p.append(text(270, 126, "поставок замовникам", size=9, color=INK))
    p.append(line(270, 135, 270, axis_y - 6, color=FIELD, sw=1.2, dash="3,3"))

    # Marker 3: PDN Issued
    p.append(circle(450, axis_y, 6, fill=AMBER, stroke="#ffffff", sw=2))
    p.append(rect(385, 60, 130, 75, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=4))
    p.append(text(450, 80, "PDN Issued (EOL)", size=11, color=AMBER, bold=True))
    p.append(text(450, 96, "JEDEC JESD48", size=9, color=MUTED))
    p.append(text(450, 112, "Оголошення про", size=9, color=INK))
    p.append(text(450, 126, "зняття з виробництва", size=9, color=INK))
    p.append(line(450, 135, 450, axis_y - 6, color=AMBER, sw=1.2, dash="3,3"))

    # Range 2: LTB Window (6 months)
    p.append(rect(450, axis_y + 15, 160, 42, fill="#fef3c7", stroke=AMBER, sw=1, rx=3))
    p.append(text(530, axis_y + 32, "LTB Window (6 міс)", size=10, color=AMBER, bold=True))
    p.append(text(530, axis_y + 47, "Last Time Buy замовлення", size=9, color=INK))
    p.append(line(450, axis_y + 10, 450, axis_y + 60, color=AMBER, sw=1))
    p.append(line(610, axis_y + 10, 610, axis_y + 60, color=AMBER, sw=1))

    # Marker 4: LTB Deadline
    p.append(circle(610, axis_y, 6, fill=POS, stroke="#ffffff", sw=2))
    p.append(rect(545, 60, 130, 75, fill=REDBG, stroke=POS, sw=1.2, rx=4))
    p.append(text(610, 80, "LTB Deadline", size=11, color=POS, bold=True))
    p.append(text(610, 96, "Кінець замовлень", size=9, color=MUTED))
    p.append(text(610, 112, "Фінальний розрахунок", size=9, color=INK))
    p.append(text(610, 126, "стратегічного запасу", size=9, color=INK))
    p.append(line(610, 135, 610, axis_y - 6, color=POS, sw=1.2, dash="3,3"))

    # Range 3: LTS Window (6 months from LTB, 12 months total)
    p.append(rect(610, axis_y + 15, 160, 42, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    p.append(text(690, axis_y + 32, "LTS Window (6 міс)", size=10, color=POS, bold=True))
    p.append(text(690, axis_y + 47, "Last Time Ship відвантаження", size=9, color=INK))
    p.append(line(770, axis_y + 10, 770, axis_y + 60, color=POS, sw=1))

    # Marker 5: LTS / Obsolete
    p.append(circle(770, axis_y, 6, fill=INK, stroke="#ffffff", sw=2))
    p.append(rect(705, 60, 125, 75, fill="#f3f4f6", stroke=LINE, sw=1.2, rx=4))
    p.append(text(767, 80, "LTS / Obsolete", size=11, color=INK, bold=True))
    p.append(text(767, 96, "Кінець відвантажень", size=9, color=MUTED))
    p.append(text(767, 112, "Повна зупинка ліній", size=9, color=INK))
    p.append(text(767, 126, "Статус: EOL", size=9, color=INK))
    p.append(line(770, 135, 770, axis_y - 6, color=LINE, sw=1.2, dash="3,3"))

    # Bottom summary box
    p.append(rect(40, 260, 760, 95, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(70, 282, "Критичні часові нормативи JEDEC для інженерних команд:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(70, 304, "1. JESD46 (PCN): постачальник зобов'язаний надати зразки та звіт кваліфікації за 90 днів до впровадження.", size=10, color=INK, anchor="start"))
    p.append(text(70, 324, "2. JESD48 (PDN): мінімум 6 місяців від сповіщення до дедлайну LTB, і ще 6 місяців до фінального відвантаження LTS.", size=10, color=INK, anchor="start"))
    p.append(text(70, 344, "3. Ігнорування PCN призводить до несподіваного зриву виробництва або непротестованих відмов плати в польових умовах.", size=9, color=POS, anchor="start", italic=True))

    render(os.path.join(OUT, "pcn-pdn-timeline.svg"), W, H, *p,
           title="Промислове сповіщення про життєвий цикл компонентів")


if __name__ == "__main__":
    fig_stepping_fix_types()
    fig_errata_resolution_flow()
    fig_pcn_pdn_timeline()
    print("Figures generated successfully.")
