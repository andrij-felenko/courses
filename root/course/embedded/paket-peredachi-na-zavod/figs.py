# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Чотири складові виробничого пакета передачі на завод ─────────────
def fig_data_package_layers():
    W, H = 840, 430
    frags = []
    frags.append(text(W / 2, 28, "Анатомія повного пакета передачі виробу на контрактне виробництво",
                      size=15, bold=True))

    # Загальний вхідний архів
    frags.append(rect(40, 58, 760, 48, fill="#edf2f7", stroke=INK, sw=1.8))
    frags.append(text(W / 2, 80, "RELEASE_PACKAGE_v2.1.0_PROD.ZIP (Цифровий контракт із заводом)",
                      size=13, bold=True, color=INK))
    frags.append(text(W / 2, 96, "Єдиний самодостатній архів: версія зафіксована, контрольні суми SHA-256 пораховані",
                      size=11, color=MUTED))

    # 4 кошики даних
    cols = [
        ("1. Гола плата (PCB Fab)", [
            "• Gerber (RS-274X / X2)",
            "• Excellon Drill (PTH/NPTH)",
            "• Специфікація стекапу",
            "• Креслення обробки (Fab Notes)",
            "• Покриття: ENIG / HASL / OSP"
        ], "#eaf4ec", FIELD),
        ("2. Монтаж (SMT / THT)", [
            "• BOM (список деталей, MPN)",
            "• Pick-and-Place (координати CPL)",
            "• Трафарет (Paste Gerber)",
            "• Складальне креслення (Assy)",
            "• Орієнтація полярності й ключів"
        ], "#eaf0fd", NEG),
        ("3. Прошивання (Firmware)", [
            "• Бінарні образи (.bin / .hex)",
            "• Карта пам'яті й розділи",
            "• Конфігурація fuse / lock bits",
            "• Скрипти прошивання станції",
            "• Пул серійників / сертифікатів"
        ], "#fdf3e7", "#d97706"),
        ("4. Тестування й контроль", [
            "• Інструкція тестування (SOP)",
            "• Специфікація тест-точок (ICT)",
            "• Прошивка/стенд FCT джига",
            "• Критерії придатності (Pass/Fail)",
            "• Еталонний зразок (Golden Unit)"
        ], "#fdecea", POS)
    ]

    cw = 178
    gap = 16
    x0 = 40
    y0 = 138
    ch = 220

    for i, (title_col, items, fill_col, border_col) in enumerate(cols):
        cx = x0 + i * (cw + gap)
        frags.append(rect(cx, y0, cw, ch, fill=fill_col, stroke=border_col, sw=1.6))
        frags.append(rect(cx, y0, cw, 34, fill=border_col, stroke=border_col, sw=1.6, rx=4))
        frags.append(text(cx + cw / 2, y0 + 22, title_col, size=11, bold=True, color="#ffffff"))
        
        for j, itm in enumerate(items):
            frags.append(text(cx + 10, y0 + 58 + j * 32, itm, size=10, color=INK, anchor="start"))

        # Стрілка вниз від верхнього архіву до кожного кошика
        frags.append(arrow(cx + cw / 2, 106, cx + cw / 2, y0 - 4, color=border_col, sw=1.4))

    # Нижній висновок
    frags.append(fitbox(40, H - 54, 760, 38,
                        "Жодного сирого файлу САПР (.kicad_pcb чи .PrjPcb): кожен кошик містить лише верстатні інструкції та однозначні специфікації.",
                        size=11, fill="#f8fafc", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'data-package-layers.svg'), W, H, *frags)


# ── Фігура 2: Розбіжність BOM та Pick-and-Place координат ──────────────────────
def fig_bom_cpl_discrepancy():
    W, H = 840, 400
    frags = []
    frags.append(text(W / 2, 28, "Два потоки даних монтажу: де виникає фатальна розбіжність",
                      size=15, bold=True))

    # Лівий блок: BOM
    bw, bh = 340, 160
    bx, by = 50, 70
    frags.append(rect(bx, by, bw, bh, fill="#f0f7ff", stroke=NEG, sw=1.6))
    frags.append(text(bx + bw / 2, by + 24, "BOM (Відомість матеріалів)", size=13, bold=True, color=NEG))
    frags.append(text(bx + bw / 2, by + 44, "Відповідає на питання: «ЩО ЗАКУПИТИ ТА ВСТАНОВИТИ»", size=10, color=MUTED))
    frags.append(line(bx + 14, by + 56, bx + bw - 14, by + 56, color=NEG, sw=1))
    frags.append(text(bx + 16, by + 78, "• D1: 1N4148WS (Діод SOD-323)", size=11, color=INK, anchor="start"))
    frags.append(text(bx + 16, by + 102, "• U3: STM32G030F6P6 (TSSOP-20)", size=11, color=INK, anchor="start"))
    frags.append(text(bx + 16, by + 126, "• R12: 10k 0402 1% [DNP / Не монтувати]", size=11, color=INK, anchor="start"))
    frags.append(text(bx + 16, by + 148, "• C5: 100nF 0402 16V X7R", size=11, color=INK, anchor="start"))

    # Правий блок: CPL / Pick-and-Place
    px, py = 450, 70
    frags.append(rect(px, py, bw, bh, fill="#f3faf5", stroke=FIELD, sw=1.6))
    frags.append(text(px + bw / 2, py + 24, "Pick-and-Place (CPL / Centroid)", size=13, bold=True, color=FIELD))
    frags.append(text(px + bw / 2, py + 44, "Відповідає на питання: «ДЕ Й ЯК РОЗМІСТИТИ НА ПЛАТІ»", size=10, color=MUTED))
    frags.append(line(px + 14, py + 56, px + bw - 14, py + 56, color=FIELD, sw=1))
    frags.append(text(px + 16, py + 78, "• D1: X=14.25, Y=22.80, Rot=180.0°, Top", size=11, color=INK, anchor="start"))
    frags.append(text(px + 16, py + 102, "• U3: X=45.10, Y=30.00, Rot=90.0°, Top", size=11, color=INK, anchor="start"))
    frags.append(text(px + 16, py + 126, "• R12: (присутній у файлі з кутом 0°)", size=11, color=INK, anchor="start"))
    frags.append(text(px + 16, py + 148, "• C5: X=48.20, Y=32.50, Rot=0.0°, Top", size=11, color=INK, anchor="start"))

    # Центральний блок: Точки критичних конфліктів
    my = 252
    frags.append(rect(50, my, 740, 84, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(W / 2, my + 22, "КРИТИЧНІ МІСЦЯ РОЗБІЖНОСТІ (Автоматичний брак під час монтажу)", size=12, bold=True, color=POS))
    
    frags.append(text(70, my + 46, "1. Поворот 0° у CAD проти стрічки живильника: діод запаяно катодом навпаки (180° mismatch).", size=10.5, color=INK, anchor="start"))
    frags.append(text(70, my + 66, "2. Відсутність синхронізації DNP: PnP автомат шукає котушку для R12 або змонтує непотрібний резистор.", size=10.5, color=INK, anchor="start"))

    frags.append(arrow(bx + bw / 2, by + bh + 4, bx + bw / 2, my - 4, color=NEG, sw=1.5))
    frags.append(arrow(px + bw / 2, py + bh + 4, px + bw / 2, my - 4, color=FIELD, sw=1.5))

    frags.append(fitbox(50, H - 48, 740, 36,
                        "Рішення: автоматична перехресна валідація BOM і CPL скриптом до відправки + складальне креслення з чіткими мітками полярності.",
                        size=11, fill="#f8fafc", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'bom-cpl-discrepancy.svg'), W, H, *frags)


# ── Фігура 3: Життєвий цикл інженерної зміни ECN / ECO ────────────────────────
def fig_change_control_ecn_flow():
    W, H = 840, 380
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл інженерної зміни: від дефекту до зміни на конвеєрі",
                      size=15, bold=True))

    steps = [
        ("1. Ініціація (ECR)", "Виявлено дефект,\nдефіцит чіпа або\nзапит на поліпшення", "#fff8e6", "#b07a35"),
        ("2. Оцінка впливу", "Аналіз залишків складу,\nсумісності прошивки,\nсобівартості та термінів", "#eef2f7", INK),
        ("3. Наказ ECO", "Затвердження нової\nревізії: PCB Rev B\nабо PCBA Rev 1.2", "#eaf4ec", FIELD),
        ("4. Випуск пакета", "Повна перегенерація\nGerber, BOM, CPL,\nSHA-256 та архіву", "#eaf0fd", NEG),
        ("5. Впровадження", "Акт зрізу партії (Cutoff),\nутилізація/доробка,\nстарт нової серії", "#fdecea", POS)
    ]

    bw = 132
    bh = 110
    gap = 20
    x0 = 40
    y0 = 74

    for i, (st_title, st_desc, bg_col, brd_col) in enumerate(steps):
        bx = x0 + i * (bw + gap)
        frags.append(rect(bx, y0, bw, bh, fill=bg_col, stroke=brd_col, sw=1.6))
        frags.append(text(bx + bw / 2, y0 + 22, st_title, size=11, bold=True, color=brd_col))
        frags.append(line(bx + 8, y0 + 32, bx + bw - 8, y0 + 32, color=brd_col, sw=0.8))
        frags.append(mtext(bx + bw / 2, y0 + 52, st_desc, size=9.5, color=INK, lh=1.3))

        if i < len(steps) - 1:
            frags.append(arrow(bx + bw + 2, y0 + bh / 2, bx + bw + gap - 4, y0 + bh / 2, color=LINE, sw=1.5))

    # Нижній блок: Розділення ревізій
    ry = 210
    frags.append(rect(40, ry, 760, 110, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(text(W / 2, ry + 22, "Розділення ревізій: Гола плата (PCB) проти Зібраного вузла (PCBA)", size=12, bold=True, color=INK))

    frags.append(rect(60, ry + 36, 340, 60, fill="#eaf4ec", stroke=FIELD, sw=1.2))
    frags.append(text(230, ry + 54, "PCB Revision (напр. Rev A → Rev B)", size=11, bold=True, color=FIELD))
    frags.append(text(230, ry + 74, "Зміна міді, шарів, перехідних отворів чи форми. Вимагає нового трафарету й оснастки.", size=9.5, color=INK))

    frags.append(rect(440, ry + 36, 340, 60, fill="#eaf0fd", stroke=NEG, sw=1.2))
    frags.append(text(610, ry + 54, "PCBA Revision (напр. Rev 1.0 → Rev 1.1)", size=11, bold=True, color=NEG))
    frags.append(text(610, ry + 74, "Зміна номіналу деталей чи MPN на тій самій платі. Трафарет і мідь лишаються незмінними.", size=9.5, color=INK))

    frags.append(fitbox(40, H - 44, 760, 32,
                        "Правило ECO: релізний пакет перегенеровується цілком під новим ревізійним номером; заборонено виправляти окремі файли вручну.",
                        size=10.5, fill="#f8fafc", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'change-control-ecn-flow.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_data_package_layers()
    fig_bom_cpl_discrepancy()
    fig_change_control_ecn_flow()
    print("Figures generated successfully in ./img/")
