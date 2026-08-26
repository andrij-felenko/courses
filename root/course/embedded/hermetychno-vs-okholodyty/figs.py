# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. conflict-sealing-cooling: Конфлікт вимог IP67 та тепловідведення ─────────
def fig_conflict():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 32, "Фундаментальний конфлікт оболонки: захист від середовища vs розсіювання тепла", size=15, color=INK, bold=True))

    # Ліва колонка: Герметичний корпус (IP67/IP68)
    bx1, by, bw, bh = 40, 60, 410, 390
    p.append(rect(bx1, by, bw, bh, fill="#fdf2f2", stroke=POS, sw=2, rx=10))
    p.append(text(bx1 + bw / 2, by + 30, "Герметичний корпус (IP67 / IP68)", size=14, color=POS, bold=True))
    p.append(text(bx1 + bw / 2, by + 52, "Суцільна оболонка без отворів", size=11, color=MUTED))

    # Схема герметичного боксу
    cx1, cy1 = bx1 + bw / 2, by + 160
    p.append(rect(cx1 - 150, cy1 - 70, 300, 140, fill="#ffffff", stroke="#c0392b", sw=2.5, rx=6))
    p.append(rect(cx1 - 144, cy1 - 64, 288, 128, fill="none", stroke="#e74c3c", sw=1.2, rx=4))
    # Гарячий чип
    p.append(rect(cx1 - 50, cy1 - 20, 100, 40, fill="#fadbd8", stroke=POS, sw=1.8, rx=4))
    p.append(text(cx1, cy1 + 4, "SoC (10–15 Вт)", size=11, color=POS, bold=True))
    p.append(text(cx1, cy1 - 40, "Замкнене повітря: k ≈ 0.026 Вт/(м·К)", size=10, color=MUTED, bold=True))
    p.append(text(cx1, cy1 + 50, "Внутрішній перегрів: T_внутр > +85 °C", size=10.5, color=POS, bold=True))

    # Бар'єр для води
    p.append(text(cx1, by + 258, "Вода й пил відсікаються зовні:", size=11, color=FIELD, bold=True))
    p.append(text(cx1, by + 280, "✓ Захист від пилу (IP6X) та занурення (IPX7)", size=10.5, color=INK))
    p.append(text(cx1, by + 302, "✗ Нульова конвекція із зовнішнім повітрям", size=10.5, color=POS, bold=True))
    p.append(text(cx1, by + 324, "✗ Високий внутрішній тепловий опір R_th", size=10.5, color=POS))
    p.append(text(cx1, by + 346, "✗ Термічне розпирання та розрідження", size=10.5, color=POS))

    # Права колонка: Вентильований корпус
    bx2 = 490
    p.append(rect(bx2, by, bw, bh, fill="#eaf2f8", stroke=NEG, sw=2, rx=10))
    p.append(text(bx2 + bw / 2, by + 30, "Вентильований корпус (IP20 / IP30)", size=14, color=NEG, bold=True))
    p.append(text(bx2 + bw / 2, by + 52, "Отвори для вільної або примусової конвекції", size=11, color=MUTED))

    # Схема відкритого боксу
    cx2 = bx2 + bw / 2
    p.append(rect(cx2 - 150, cy1 - 70, 300, 140, fill="#ffffff", stroke="#2457d6", sw=2.5, rx=6))
    for dy in [-40, -20, 0, 20, 40]:
        p.append(line(cx2 - 150, cy1 + dy, cx2 - 138, cy1 + dy, color=NEG, sw=2.5))
        p.append(line(cx2 + 138, cy1 + dy, cx2 + 150, cy1 + dy, color=NEG, sw=2.5))
    # Потік повітря стрілками
    p.append(arrow(cx2 - 130, cy1, cx2 - 60, cy1, color=NEG, sw=2))
    p.append(arrow(cx2 + 60, cy1, cx2 + 130, cy1, color=POS, sw=2))
    # Чип із радіатором
    p.append(rect(cx2 - 50, cy1 - 20, 100, 40, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=4))
    p.append(text(cx2, cy1 + 4, "SoC + Радіатор", size=11, color=NEG, bold=True))
    p.append(text(cx2, cy1 - 40, "Прямий потік: h ≈ 50–150 Вт/(м²·К)", size=10, color=FIELD, bold=True))
    p.append(text(cx2, cy1 + 50, "Ефективне охолодження: T_кристал < +55 °C", size=10.5, color=FIELD, bold=True))

    # Проблема вентильованого
    p.append(text(cx2, by + 258, "Зовнішнє середовище проникає всередину:", size=11, color=POS, bold=True))
    p.append(text(cx2, by + 280, "✓ Відмінне розсіювання тепла (5–50 Вт)", size=10.5, color=FIELD))
    p.append(text(cx2, by + 302, "✗ Пряме проникнення води, конденсату та пилу", size=10.5, color=POS, bold=True))
    p.append(text(cx2, by + 324, "✗ Корозія контактів, сольовий туман, містки бруду", size=10.5, color=POS))
    p.append(text(cx2, by + 346, "✗ Неможливість експлуатації просто неба (Outdoor)", size=10.5, color=POS))

    render(os.path.join(OUT, "conflict-sealing-cooling.svg"), W, H, *p,
           title="Конфлікт між вимогами IP-герметизації та конвективним охолодженням")


# ── 2. pressure-pumping-cycle: «Насосний ефект» та протікання ущільнення ─────────
def fig_pumping():
    W, H = 940, 450
    p = []

    p.append(text(W / 2, 28, "Термодинамічний цикл «насосного ефекту» в закритому корпусі", size=15, color=INK, bold=True))

    # Фаза 1: Розігрів під навантаженням / на сонці
    x1, y1, w, h = 40, 55, 410, 365
    p.append(rect(x1, y1, w, h, fill="#fffaf0", stroke="#d35400", sw=2, rx=8))
    p.append(text(x1 + w / 2, y1 + 26, "ФАЗА 1: Нагрівання (20 °C → 70 °C)", size=13.5, color="#d35400", bold=True))
    p.append(text(x1 + w / 2, y1 + 46, "Робота електроніки + сонячна радіація", size=10.5, color=MUTED))

    # Корпус під тиском
    cx1, cy1 = x1 + w / 2, y1 + 140
    p.append(rect(cx1 - 130, cy1 - 55, 260, 110, fill="#ffffff", stroke="#d35400", sw=2, rx=6))
    p.append(rect(cx1 - 40, cy1 - 15, 80, 30, fill="#fadbd8", stroke=POS, sw=1.5, rx=3))
    p.append(text(cx1, cy1 + 4, "Нагрівач 10 Вт", size=10, color=POS, bold=True))

    # Стрілки випинання та витоку повітря
    p.append(arrow(cx1 + 100, cy1 - 40, cx1 + 145, cy1 - 50, color=POS, sw=2))
    p.append(text(cx1 + 150, cy1 - 55, "Вихід повітря", size=10, color=POS, anchor="start", bold=True))
    p.append(text(cx1, cy1 - 32, "P_внутр = 118 кПа (+17 кПа надлишку)", size=10.5, color=POS, bold=True))
    p.append(text(cx1, cy1 + 38, "F_розпирання ≈ 520 Н на кришку 0.03 м²", size=10, color="#d35400"))

    # Пояснення фази 1
    p.append(text(cx1, y1 + 230, "1. Повітря розширюється за законом Гей-Люссака", size=10.5, color=INK, bold=True))
    p.append(text(cx1, y1 + 252, "2. Надлишковий тиск вигинає стінки та кришку", size=10, color=INK))
    p.append(text(cx1, y1 + 272, "3. Ущільнювач частково розвантажується", size=10, color=INK))
    p.append(text(cx1, y1 + 294, "4. ~15% гарячого сухого повітря стравлюється", size=10.5, color=POS, bold=True))
    p.append(text(cx1, y1 + 314, "   назовні крізь мікропори та нещільності", size=10, color=POS))

    # Стрілка переходу (холодний дощ)
    p.append(arrow(x1 + w + 10, y1 + h / 2, x1 + w + 30, y1 + h / 2, color=NEG, sw=2.5))
    p.append(text(x1 + w + 20, y1 + h / 2 - 12, "Дощ / холод", size=10, color=NEG, bold=True))

    # Фаза 2: Різке охолодження (засмоктування вологи)
    x2 = 490
    p.append(rect(x2, y1, w, h, fill="#f0f7ff", stroke=NEG, sw=2, rx=8))
    p.append(text(x2 + w / 2, y1 + 26, "ФАЗА 2: Охолодження (70 °C → 15 °C)", size=13.5, color=NEG, bold=True))
    p.append(text(x2 + w / 2, y1 + 46, "Злива, вітер, вимкнення приладу", size=10.5, color=MUTED))

    cx2 = x2 + w / 2
    p.append(rect(cx2 - 130, cy1 - 55, 260, 110, fill="#ffffff", stroke=NEG, sw=2, rx=6))
    p.append(rect(cx2 - 40, cy1 - 15, 80, 30, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(cx2, cy1 + 4, "Охолодження", size=10, color=NEG, bold=True))

    # Стрілки засмоктування вологи
    p.append(arrow(cx2 + 145, cy1 - 50, cx2 + 105, cy1 - 40, color=NEG, sw=2.2))
    p.append(text(cx2 + 150, cy1 - 55, "Засмоктування води!", size=10, color=NEG, anchor="start", bold=True))
    p.append(text(cx2, cy1 - 32, "P_внутр = 85 кПа (-16 кПа вакууму)", size=10.5, color=NEG, bold=True))
    p.append(text(cx2, cy1 + 38, "Зовнішній тиск втискає воду всередину", size=10, color=NEG))

    # Пояснення фази 2
    p.append(text(cx2, y1 + 230, "1. Залишкове повітря різко стискається", size=10.5, color=INK, bold=True))
    p.append(text(cx2, y1 + 252, "2. Створюється вакуумне розрідження ΔP ≈ -16 кПа", size=10.5, color=NEG, bold=True))
    p.append(text(cx2, y1 + 272, "3. Прокладка працює як зворотний клапан", size=10, color=INK))
    p.append(text(cx2, y1 + 294, "4. Вода з мокрої поверхні всмоктується на плату", size=10.5, color=POS, bold=True))
    p.append(text(cx2, y1 + 314, "   → Конденсат, корозія та коротке замикання", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "pressure-pumping-cycle.svg"), W, H, *p,
           title="Термодинамічний цикл насосного ефекту та проникнення вологи при охолодженні")


# ── 3. eptfe-membrane-structure: Мікропориста ePTFE мембрана ────────────────────
def fig_eptfe():
    W, H = 940, 470
    p = []

    p.append(text(W / 2, 28, "Мікропориста структура дихальної мембрани ePTFE (Gore / Nitto)", size=15, color=INK, bold=True))

    # Центральний блок мембрани
    mx, my, mw, mh = 360, 60, 220, 370
    p.append(rect(mx, my, mw, mh, fill="#fdfefe", stroke=FIELD, sw=2.5, rx=8))
    p.append(text(mx + mw / 2, my + 26, "МЕМБРАНА ePTFE", size=13, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, my + 46, "Пори: 0.2 – 3.0 мкм", size=11, color=INK, bold=True))

    # Малюнок волокон/фібрил усередині мембрани
    for fy in range(my + 70, my + 340, 35):
        p.append(line(mx + 20, fy, mx + 80, fy + 15, color="#27ae60", sw=1.8))
        p.append(line(mx + 80, fy + 15, mx + 140, fy - 10, color="#27ae60", sw=1.8))
        p.append(line(mx + 140, fy - 10, mx + 200, fy + 12, color="#27ae60", sw=1.8))
        p.append(circle(mx + 80, fy + 15, 3.5, fill=FIELD, stroke=FIELD))
        p.append(circle(mx + 140, fy - 10, 3.5, fill=FIELD, stroke=FIELD))

    p.append(text(mx + mw / 2, my + 355, "Гідрофобні вузли й фібрили", size=10, color=MUTED))

    # Ліва зона: Зовнішнє середовище (Вода, пил)
    lx, ly, lw = 40, 60, 290
    p.append(rect(lx, ly, lw, mh, fill="#edf7fc", stroke="#3498db", sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 26, "ЗОВНІШНЄ СЕРЕДОВИЩЕ", size=13, color="#2980b9", bold=True))

    # Крапля води
    p.append(circle(lx + 80, ly + 110, 30, fill="#aed6f1", stroke="#2980b9", sw=2))
    p.append(text(lx + 80, ly + 114, "Вода", size=11, color="#1b4f72", bold=True))
    p.append(text(lx + 130, ly + 104, "Крапля: 100–2000 мкм", size=10, color=INK, anchor="start", bold=True))
    p.append(text(lx + 130, ly + 122, "В 1000 разів більша за пори!", size=9.5, color=POS, anchor="start"))
    # Бар'єр для краплі
    p.append(line(lx + lw - 15, ly + 80, lx + lw - 15, ly + 145, color=POS, sw=3))
    p.append(text(lx + lw / 2, ly + 160, "Тиск прориву води (WEP) > 60–100 кПа", size=10, color=POS, bold=True))

    # Пил і бруд
    p.append(circle(lx + 60, ly + 220, 10, fill="#d7ccc8", stroke="#5d4037", sw=1.5))
    p.append(circle(lx + 90, ly + 230, 8, fill="#d7ccc8", stroke="#5d4037", sw=1.5))
    p.append(text(lx + 120, ly + 225, "Пил / аерозоль (> 5 мкм)", size=10, color=INK, anchor="start", bold=True))
    p.append(text(lx + 120, ly + 242, "Затримується на 100% (IP6X)", size=9.5, color=FIELD, anchor="start"))

    # Права зона: Внутрішній об'єм корпусу (Гази, пара)
    rx, ry, rw = 610, 60, 290
    p.append(rect(rx, ry, rw, mh, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 26, "ВНУТРІШНІЙ ОБ'ЄМ", size=13, color=INK, bold=True))

    # Молекули повітря (N2, O2)
    p.append(arrow(rx - 25, ry + 100, rx + 40, ry + 100, color=FIELD, sw=2))
    p.append(arrow(rx + 40, ry + 130, rx - 25, ry + 130, color=FIELD, sw=2))
    p.append(text(rx + 55, ry + 105, "Повітря (N₂, O₂): ~0.37 нм", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(rx + 55, ry + 125, "Вільний газообмін: ΔP → 0", size=10, color=FIELD, anchor="start", bold=True))

    # Водяна пара
    p.append(arrow(rx - 25, ry + 210, rx + 40, ry + 210, color="#3498db", sw=2))
    p.append(arrow(rx + 40, ry + 240, rx - 25, ry + 240, color="#3498db", sw=2))
    p.append(text(rx + 55, ry + 215, "Водяна пара: ~0.28 нм", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(rx + 55, ry + 235, "Дифузія молекул вологи", size=10, color="#2980b9", anchor="start"))

    # Підсумок внизу
    p.append(rect(lx, my + 385, W - 80, 45, fill="#f4f6f7", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(W / 2, my + 412, "Результат: постійне вирівнювання тиску (ΔP ≈ 0) без ризику засмоктування рідкої води", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "eptfe-membrane-structure.svg"), W, H, *p,
           title="Фізика проникності дихальної мікропористої ePTFE мембрани")


# ── 4. thermal-enclosure-architectures: Архітектури корпусів з тепловідведенням ─
def fig_architectures():
    W, H = 940, 500
    p = []

    p.append(text(W / 2, 28, "Конструктивні підходи до охолодження герметичної електроніки", size=15, color=INK, bold=True))

    # Варіант А: Суцільнометалевий монолітний корпус-радіатор
    ax, ay, aw, ah = 40, 55, 410, 420
    p.append(rect(ax, ay, aw, ah, fill="#f8f9fa", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(ax + aw / 2, ay + 26, "А: Суцільнометалевий моноліт (Die-Cast/CNC)", size=13, color="#2c3e50", bold=True))
    p.append(text(ax + aw / 2, ay + 46, "Корпус як єдиний тепловідвідний радіатор", size=10.5, color=MUTED))

    # Схема моноліту
    cax, cay = ax + aw / 2, ay + 160
    # Зовнішній алюміній з ребрами
    p.append(rect(cax - 140, cay - 60, 280, 120, fill="#eaeded", stroke="#34495e", sw=2.5, rx=4))
    # Зовнішні ребра зверху
    for r_x in range(int(cax - 130), int(cax + 140), 20):
        p.append(line(r_x, cay - 60, r_x, cay - 85, color="#34495e", sw=3.5))
    p.append(text(cax, cay - 93, "Зовнішнє оребрення (конвекція назовні)", size=9.5, color=INK, bold=True))

    # Внутрішній тепломіст (boss)
    p.append(rect(cax - 30, cay - 60, 60, 45, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5))
    p.append(text(cax, cay - 42, "Термоміст", size=9.5, color=INK))

    # Прокладка TIM (Gap Pad)
    p.append(rect(cax - 28, cay - 15, 56, 8, fill="#f39c12", stroke="#d68910", sw=1))
    p.append(text(cax + 75, cay - 10, "← TIM (Gap Pad)", size=9.5, color="#d68910", bold=True))

    # Плата і чип
    p.append(rect(cax - 90, cay + 15, 180, 6, fill="#27ae60", stroke="#1e8449", sw=1)) # PCB
    p.append(rect(cax - 25, cay - 7, 50, 22, fill="#e74c3c", stroke="#c0392b", sw=1.5, rx=2)) # SoC
    p.append(text(cax, cay + 6, "SoC", size=10, color="#ffffff", bold=True))

    # Ущільнювач і дихальний клапан
    p.append(circle(cax - 120, cay + 40, 7, fill="#f1c40f", stroke="#d4ac0d", sw=1.5))
    p.append(text(cax - 120, cay + 58, "ePTFE клапан", size=9.5, color=INK))

    # Плюси й мінуси
    p.append(text(cax, ay + 260, "Ланцюжок передачі тепла:", size=10.5, color=INK, bold=True))
    p.append(text(cax, ay + 280, "Кристал → Корпус чипа → TIM → Алюмінієвий бобик → Ребра", size=9.5, color=FIELD, bold=True))
    p.append(text(cax, ay + 310, "✓ Повний захист IP67/IP68 без рухомих деталей", size=10, color=FIELD))
    p.append(text(cax, ay + 330, "✓ Розсіювання до 10–25 Вт природною конвекцією", size=10, color=FIELD))
    p.append(text(cax, ay + 350, "✗ Велика вага та висока собівартість литва/ЧПК", size=10, color=POS))
    p.append(text(cax, ay + 370, "✗ Вимоги до жорстких механічних допусків TIM", size=10, color=POS))

    # Варіант Б: Двокамерний корпус (Герметична логіка + Продувна сила)
    bx, by, bw, bh = 490, 55, 410, 420
    p.append(rect(bx, by, bw, bh, fill="#f8f9fa", stroke="#2980b9", sw=2, rx=8))
    p.append(text(bx + bw / 2, by + 26, "Б: Двокамерна архітектура (Dual-Chamber)", size=13, color="#2980b9", bold=True))
    p.append(text(bx + bw / 2, by + 46, "Розділення об'ємів захисту й потужності", size=10.5, color=MUTED))

    # Схема двох камер
    cbx, cby = bx + bw / 2, by + 160
    # Загальний контур
    p.append(rect(cbx - 140, cby - 60, 280, 120, fill="#ffffff", stroke="#7f8c8d", sw=2, rx=4))

    # Відсік 1: Герметичний (IP67)
    p.append(rect(cbx - 135, cby - 55, 125, 110, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=3))
    p.append(text(cbx - 72, cby - 35, "Відсік логіки (IP67)", size=9.5, color="#2980b9", bold=True))
    p.append(rect(cbx - 100, cby - 10, 56, 30, fill="#27ae60", stroke="#1e8449", sw=1.2, rx=2))
    p.append(text(cbx - 72, cby + 9, "MCU / RF", size=9.5, color="#ffffff", bold=True))

    # Герметична теплостінка / трубка
    p.append(rect(cbx - 10, cby - 55, 20, 110, fill="#d5dbdb", stroke="#34495e", sw=1.5))
    p.append(text(cbx, cby + 48, "Гермостінка", size=9, color=INK))

    # Відсік 2: Продувний силовий (IP20/IP30)
    p.append(rect(cbx + 10, cby - 55, 125, 110, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=3))
    p.append(text(cbx + 72, cby - 35, "Силовий відсік", size=9.5, color="#d68910", bold=True))
    p.append(rect(cbx + 40, cby - 10, 64, 30, fill="#e74c3c", stroke="#c0392b", sw=1.2, rx=2))
    p.append(text(cbx + 72, cby + 9, "MOSFET/Транс", size=9.5, color="#ffffff", bold=True))
    # Вентилятор у силовому відсіку
    p.append(circle(cbx + 115, cby + 5, 14, fill="#d4e6f1", stroke="#2980b9", sw=1.2))
    p.append(text(cbx + 115, cby + 9, "Вент", size=9, color="#2980b9", bold=True))

    # Плюси й мінуси
    p.append(text(cbx, by + 260, "Особливості двокамерного поділу:", size=10.5, color=INK, bold=True))
    p.append(text(cbx, by + 280, "Логіка ізольована, сила продувається відкритим вентилятором", size=9.5, color=INK, bold=True))
    p.append(text(cbx, by + 310, "✓ Здатність розсіювати 50–500+ Вт тепла", size=10, color=FIELD))
    p.append(text(cbx, by + 330, "✓ Дешевший пластиковий корпус гермовідсіку", size=10, color=FIELD))
    p.append(text(cbx, by + 350, "✗ Силові компоненти відкриті для вологи й бруду", size=10, color=POS))
    p.append(text(cbx, by + 370, "✗ Більші габарити та складніша збірка приладу", size=10, color=POS))

    render(os.path.join(OUT, "thermal-enclosure-architectures.svg"), W, H, *p,
           title="Порівняння суцільнометалевого моноліту та двокамерного корпусу")


if __name__ == "__main__":
    fig_conflict()
    fig_pumping()
    fig_eptfe()
    fig_architectures()
    print("All figures generated successfully.")
