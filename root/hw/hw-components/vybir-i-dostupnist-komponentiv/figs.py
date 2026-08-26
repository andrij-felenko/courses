# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#d97706"
AMBERBG = "#fef3c7"
REDBG   = "#fee2e2"
GRNBG   = "#dcfce7"
BLUEBG  = "#dbeafe"
PURPLE  = "#7c3aed"
PURPLEBG= "#ede9fe"
GRAYBG  = "#f3f4f6"

def svg_polyline(pts, color=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (pts_str, color, sw)


# ── 1. lifecycle-timeline: Життєвий цикл компонента і фази сповіщень ─────────
def fig_lifecycle_timeline():
    W, H = 760, 390
    p = []

    # Заголовок зверху
    p.append(text(380, 26, "ФАЗИ ЖИТТЄВОГО ЦИКЛУ ТА СПОВІЩЕННЯ ВИРОБНИКА", size=13, color=INK, bold=True))

    # Стрічка фаз (Preview -> Active -> NRND -> EOL / LTB -> Obsolete)
    phases = [
        ("Preview", "Зразки, ризик зміни", 40, 130, BLUEBG, NEG),
        ("Active (Серійний)", "Масове виробництво", 175, 150, GRNBG, FIELD),
        ("NRND", "Не для нових плат", 330, 130, AMBERBG, AMBER),
        ("EOL / LTB", "Останній викуп чипа", 465, 140, REDBG, POS),
        ("Obsolete", "Знято з лінійки", 610, 110, GRAYBG, MUTED)
    ]

    for title, desc, x, w, bg, border in phases:
        p.append(rect(x, 50, w, 82, fill=bg, stroke=border, sw=1.8, rx=6))
        p.append(text(x + w/2, 78, title, size=11, color=border, bold=True))
        p.append(text(x + w/2, 104, desc, size=9, color=INK))

    # Стрілка прогресу внизу стрічки
    p.append(arrow(40, 150, 720, 150, color=LINE, sw=2))
    p.append(text(380, 168, "Часова шкала доступності компонента на ринку (роки)", size=10, color=MUTED, italic=True))

    # Нижня частина: Розбір ключових подій сповіщень (PCN vs PDN/PTN)
    p.append(rect(40, 190, 330, 175, fill="#ffffff", stroke=AMBER, sw=1.5, rx=6))
    p.append(rect(40, 190, 330, 30, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=6))
    p.append(text(205, 210, "PCN (Product Change Notification)", size=11, color=AMBER, bold=True))
    p.append(text(55, 238, "• Стандарт: JEDEC JESD46", size=10, color=INK, anchor="start"))
    p.append(text(55, 262, "• Причини: зміна фабрики, маски кристала,", size=10, color=INK, anchor="start"))
    p.append(text(55, 284, "  матеріалу виводів або пакування", size=10, color=INK, anchor="start"))
    p.append(text(55, 310, "• Термін сповіщення: мінімум за 90 днів", size=10, color=INK, anchor="start"))
    p.append(text(55, 336, "• Дія: інженерна верифікація зразків нової ревізії", size=9, color=POS, bold=True, anchor="start"))

    p.append(rect(390, 190, 330, 175, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(rect(390, 190, 330, 30, fill=REDBG, stroke=POS, sw=1.5, rx=6))
    p.append(text(555, 210, "PDN / PTN (Product Discontinuance)", size=11, color=POS, bold=True))
    p.append(text(405, 238, "• Стандарт: JEDEC JESD48", size=10, color=INK, anchor="start"))
    p.append(text(405, 262, "• LTB (Last Time Buy): термін замовлення", size=10, color=INK, anchor="start"))
    p.append(text(405, 284, "  (зазвичай 6 місяців від публікації)", size=10, color=INK, anchor="start"))
    p.append(text(405, 310, "• LTS (Last Time Ship): дата фінальної поставки", size=10, color=INK, anchor="start"))
    p.append(text(405, 336, "• Дія: терміновий редизайн або викуп буфера на роки", size=9, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "lifecycle-timeline.svg"), W, H, *p,
           title="Життєвий цикл компонентів та сповіщення")


# ── 2. sourcing-risk-pyramid: Піраміда ризиків постачання ───────────────────
def fig_sourcing_risk_pyramid():
    W, H = 760, 390
    p = []

    p.append(text(380, 24, "СТРАТЕГІЇ ПОСТАЧАННЯ ТА ІЄРАРХІЯ РИЗИКІВ", size=13, color=INK, bold=True))

    levels = [
        ("РІВЕНЬ 1: Single-Source Proprietary (Критичний ризик)",
         "Унікальний кремній без прямої заміни (MCU, SoC, PMIC). Зупинка постачання зупиняє виробництво.",
         40, 48, 680, 62, REDBG, POS),
        ("РІВЕНЬ 2: Dual-Source Compatible (Помірний ризик)",
         "Мікросхема має 1 аналог з сумісною розпіновкою (Pin-to-Pin), але потребує узгодження дільників чи софту.",
         40, 118, 680, 62, AMBERBG, AMBER),
        ("РІВЕНЬ 3: Multi-Source Drop-in Replacement (Низький ризик)",
         "Повна пряма заміна (Pin-to-Pin, напруги, ESR). Стандартні LDO (1117, 7805), операційні підсилювачі, RS-485.",
         40, 188, 680, 62, BLUEBG, NEG),
        ("РІВЕНЬ 4: Commodity Industry Standards (Мінімальний ризик)",
         "Повна взаємозамінність за EIA/JEDEC: резистори 0603 1%, MLCC-конденсатори, діоди, типові польові транзистори.",
         40, 258, 680, 62, GRNBG, FIELD)
    ]

    for title, desc, x, y, w, h, bg, border in levels:
        p.append(rect(x, y, w, h, fill=bg, stroke=border, sw=1.5, rx=6))
        p.append(text(x + 16, y + 24, title, size=11, color=border, bold=True, anchor="start"))
        p.append(text(x + 16, y + 47, desc, size=9, color=INK, anchor="start"))

    p.append(rect(40, 332, 680, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(380, 357, "Золоте правило DFM: для пасивних компонентів та LDO вказувати мінімум 2-3 схвалені MPN (AML)", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "sourcing-risk-pyramid.svg"), W, H, *p,
           title="Ієрархія ризиків постачання компонентів")


# ── 3. dc-bias-derating: Падіння ємності MLCC під DC Bias ────────────────────
def fig_dc_bias_derating():
    W, H = 760, 390
    p = []

    p.append(text(380, 24, "ЕФЕКТ ПОСТІЙНОЇ НАПРУГИ ЗМІЩЕННЯ (DC BIAS) ДЛЯ КЕРАМІЧНИХ КОНДЕНСАТОРІВ", size=12, color=INK, bold=True))

    # Графік зліва (осі)
    gx, gy, gw, gh = 70, 52, 350, 240
    p.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))

    # Горизонтальні сітки (% ємності)
    for i, pct in enumerate([100, 80, 60, 40, 20, 0]):
        y = gy + i * (gh / 5)
        p.append(line(gx, y, gx + gw, y, color="#e5e7eb", sw=1))
        p.append(text(gx - 8, y + 4, "%d%%" % pct, size=9, color=MUTED, anchor="end"))

    # Вертикальні сітки (Напруга В)
    for i, v in enumerate([0, 2, 4, 6, 8, 10, 12, 14, 16]):
        x = gx + i * (gw / 8)
        p.append(line(x, gy, x, gy + gh, color="#e5e7eb", sw=1))
        p.append(text(x, gy + gh + 15, "%dВ" % v, size=9, color=MUTED))

    p.append(text(gx + gw/2, gy + gh + 34, "Постійна напруга зміщення на конденсаторі (V_dc)", size=10, color=INK))
    p.append(text(gx - 38, gy + gh/2, "Залишкова ємність", size=10, color=INK, anchor="middle"))

    # Крива C0G / NP0 (ідеальна горизонталь на 100%)
    p.append(line(gx, gy, gx + gw, gy, color=FIELD, sw=2.5))
    p.append(text(gx + 230, gy + 16, "C0G / NP0 (0% втрат)", size=10, color=FIELD, bold=True))

    # Крива X7R 0805 10uF 25V (помірне падіння)
    pts_x7r_0805 = [(0, 1.0), (2, 0.98), (4, 0.93), (6, 0.86), (8, 0.78), (10, 0.70), (12, 0.62), (14, 0.55), (16, 0.48)]
    coords1 = []
    for v, f in pts_x7r_0805:
        cx = gx + (v / 16.0) * gw
        cy = gy + (1.0 - f) * gh
        coords1.append((cx, cy))
    p.append(svg_polyline(coords1, color=NEG, sw=2.2))
    p.append(text(gx + 200, gy + 82, "X7R 0805 10мкФ 25В", size=10, color=NEG, bold=True))

    # Крива X7R 0402 10uF 6.3V (катастрофічне падіння)
    pts_x7r_0402 = [(0, 1.0), (1, 0.75), (2, 0.50), (3.3, 0.32), (5, 0.20), (6.3, 0.14), (8, 0.10), (12, 0.06), (16, 0.04)]
    coords2 = []
    for v, f in pts_x7r_0402:
        cx = gx + (v / 16.0) * gw
        cy = gy + (1.0 - f) * gh
        coords2.append((cx, cy))
    p.append(svg_polyline(coords2, color=POS, sw=2.2))
    p.append(text(gx + 120, gy + 192, "X7R 0402 10мкФ 6.3В (втрата 80% на 5В!)", size=9, color=POS, bold=True))

    # Права панель з поясненнями
    rx = 445
    p.append(rect(rx, 52, 285, 280, fill="#ffffff", stroke=AMBER, sw=1.5, rx=6))
    p.append(rect(rx, 52, 285, 30, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=6))
    p.append(text(rx + 142, 72, "Чому ємність падає?", size=11, color=AMBER, bold=True))

    p.append(text(rx + 12, 102, "• Сегнетоелектричний ефект:", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 12, 120, "  У діелектриках BaTiO3 (Class II: X5R/X7R)", size=9, color=INK, anchor="start"))
    p.append(text(rx + 12, 138, "  домени насичуються сильним полем.", size=9, color=INK, anchor="start"))

    p.append(text(rx + 12, 166, "• Вплив типорозміру SMD:", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 12, 184, "  Чим менший корпус (0402 проти 0805),", size=9, color=INK, anchor="start"))
    p.append(text(rx + 12, 202, "  тим тонші шари і тим вища напруженість.", size=9, color=INK, anchor="start"))

    p.append(text(rx + 12, 230, "• Інженерне правило вибору:", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(rx + 12, 248, "  Для живлення 5В обирати номінал на", size=9, color=POS, anchor="start"))
    p.append(text(rx + 12, 266, "  16В/25В у корпусі 0603/0805 (запас >100%).", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(rx + 12, 292, "  Для аналогових кіл — виключно C0G/NP0.", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(text(380, 365, "Конденсатор 10 мкФ 6.3В під напругою 5В перетворюється на 2 мкФ, що зриває стабільність LDO/DCDC", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "dc-bias-derating.svg"), W, H, *p,
           title="Падіння ємності MLCC під напругою зміщення DC Bias")


# ── 4. temperature-grades: Температурні класи та AEC-Q ──────────────────────
def fig_temperature_grades():
    W, H = 760, 390
    p = []

    p.append(text(380, 24, "ТЕМПЕРАТУРНІ КЛАСИ ТА КВАЛІФІКАЦІЯ НАДІЙНОСТІ", size=13, color=INK, bold=True))

    # Горизонтальна вісь температур
    ox, oy, ow = 60, 75, 640
    p.append(line(ox, oy, ox + ow, oy, color=LINE, sw=2))

    t_marks = [
        (-55, 0),
        (-40, 70),
        (0, 220),
        (70, 420),
        (85, 470),
        (105, 530),
        (125, 590),
        (150, 640)
    ]

    for t, pos_x in t_marks:
        x = ox + pos_x
        p.append(line(x, oy - 6, x, oy + 6, color=LINE, sw=1.5))
        p.append(text(x, oy - 12, "%+d°C" % t if t != 0 else "0°C", size=10, color=INK, bold=True))

    ranges = [
        ("Commercial (Споживчий: ПК, офісна техніка)", 0, 70, 110, BLUEBG, NEG),
        ("Industrial (Промисловий: автоматика, телеком)", -40, 85, 155, GRNBG, FIELD),
        ("Automotive AEC-Q100 Grade 2 (Салон, панель)", -40, 105, 200, AMBERBG, AMBER),
        ("Automotive AEC-Q100 Grade 1 (Підкапотний простір)", -40, 125, 245, REDBG, POS),
        ("Automotive AEC-Q100 Grade 0 / Mil-Spec (Екстремальний)", -55, 150, 290, PURPLEBG, PURPLE)
    ]

    for label, t_start, t_end, y, bg, border in ranges:
        def t_to_x(temp):
            for i in range(len(t_marks)-1):
                t1, x1 = t_marks[i]
                t2, x2 = t_marks[i+1]
                if t1 <= temp <= t2:
                    return ox + x1 + (temp - t1)/(t2 - t1) * (x2 - x1)
            return ox

        x_start = t_to_x(t_start)
        x_end = t_to_x(t_end)
        w_box = x_end - x_start

        p.append(rect(x_start, y, w_box, 32, fill=bg, stroke=border, sw=1.5, rx=4))
        p.append(text(x_start + w_box/2, y + 20, label, size=9, color=border, bold=True))

    p.append(rect(40, 338, 680, 36, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(380, 360, "AEC-Q100: чипи | AEC-Q101: дискретні напівпровідники | AEC-Q200: пасивні деталі (R, C, L, кварци)", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "temperature-grades.svg"), W, H, *p,
           title="Температурні класи компонентів та кваліфікація AEC-Q")


# ── 5. bom-audit-flow: Етапи інженерного аудиту специфікації (BOM) ───────────
def fig_bom_audit_flow():
    W, H = 760, 390
    p = []

    p.append(text(380, 24, "КОНВЕЄР ІНЖЕНЕРНОГО АУДИТУ BOM ПЕРЕД ЗАПУСКОМ У СЕРІЮ", size=13, color=INK, bold=True))

    steps = [
        ("1. Життєвий цикл", "Виключення NRND/EOL,\nперевірка PCN/PDN\nстатусів дистриб'юторів", 40, BLUEBG, NEG),
        ("2. Lead Time", "Перевірка складів,\nтермінів поставки (>16т),\nMOQ та пакування", 175, BLUEBG, NEG),
        ("3. Multi-Sourcing", "AML: 100% пасиву та LDO\nмають 2+ схвалені MPN;\nперевірка Pin-to-Pin", 310, GRNBG, FIELD),
        ("4. Електрозпас", "Derating напруги (50-100%),\nпотужність резисторів,\nнасичення індуктивностей", 445, AMBERBG, AMBER),
        ("5. SMT Монтаж", "Уніфікація номіналів,\nмінімізація фідерів,\nперевірка Tape & Reel", 580, PURPLEBG, PURPLE)
    ]

    for title, desc, x, bg, border in steps:
        p.append(rect(x, 52, 130, 250, fill=bg, stroke=border, sw=1.8, rx=6))
        p.append(rect(x, 52, 130, 36, fill=border, stroke=border, sw=1, rx=4))
        p.append(text(x + 65, 74, title, size=10, color="#ffffff", bold=True))
        lines = desc.split("\n")
        y = 118
        for l in lines:
            p.append(text(x + 65, y, l, size=9, color=INK))
            y += 26

        if x < 580:
            p.append(arrow(x + 130, 175, x + 145, 175, color=LINE, sw=1.8))

    p.append(rect(40, 318, 680, 50, fill=GRNBG, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(380, 338, "РЕЗУЛЬТАТ АУДИТУ: Затверджений виробничий BOM (Frozen Golden BOM)", size=11, color=FIELD, bold=True))
    p.append(text(380, 356, "Гарантія безперервності виробництва, надійності пристрою та мінімальної собівартості монтажу", size=9, color=INK))

    render(os.path.join(OUT, "bom-audit-flow.svg"), W, H, *p,
           title="Конвеєр аудиту BOM перед запуском виробництва")


if __name__ == "__main__":
    fig_lifecycle_timeline()
    fig_sourcing_risk_pyramid()
    fig_dc_bias_derating()
    fig_temperature_grades()
    fig_bom_audit_flow()
    print("All figures generated successfully.")
