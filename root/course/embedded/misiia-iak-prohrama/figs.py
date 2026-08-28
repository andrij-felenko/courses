# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Extended color markers
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrInk" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS, INK)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    """Line with colored arrow head (mid in B/G/R/Ink)."""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))

def cblock(x, y, w, h, lines, fill, stroke, color=INK, size=12, bold=True):
    """Colored rounded box with multi-line text centered."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out


# ── 1. mission-graph.svg: Лінійний список проти графа місії ───────────────────
def fig_mission_graph():
    W, H = 960, 480
    p = [COL_MARKERS]
    
    # Title / Header
    p.append(text(W / 2, 28, "Еволюція структури місії: від статичної траєкторії до графа потоку керування", size=14, bold=True, color=INK))
    
    # Left Column: Linear list
    p.append(rect(30, 50, 420, 410, fill="#fafafa", stroke="#e0e0e0", sw=1.2, rx=10))
    p.append(text(240, 80, "ЛІНІЙНИЙ СПИСОК (БЕЗ РОЗГАЛУЖЕНЬ)", size=12, bold=True, color=MUTED))
    
    linear_steps = [
        (140, 110, 200, 42, ["0: NAV_TAKEOFF (h=30m)"], "#f4f6f8", LINE),
        (140, 175, 200, 42, ["1: NAV_WAYPOINT (A)"], "#f4f6f8", LINE),
        (140, 240, 200, 42, ["2: NAV_WAYPOINT (B)"], "#f4f6f8", LINE),
        (140, 305, 200, 42, ["3: NAV_WAYPOINT (C)"], "#f4f6f8", LINE),
        (140, 370, 200, 42, ["4: NAV_LAND (home)"], "#f4f6f8", LINE),
    ]
    for x, y, w, h, lines, fill, stroke in linear_steps:
        p.append(cblock(x, y, w, h, lines, fill, stroke, size=11, bold=True))
    
    # Down arrows for linear list
    p.append(carrow(240, 152, 240, 173, INK, "Ink"))
    p.append(carrow(240, 217, 240, 238, INK, "Ink"))
    p.append(carrow(240, 282, 240, 303, INK, "Ink"))
    p.append(carrow(240, 347, 240, 368, INK, "Ink"))
    
    p.append(text(240, 442, "Тільки послідовний перехід seq := seq + 1", size=11, italic=True, color=MUTED))

    # Right Column: Graph mission
    p.append(rect(480, 50, 450, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=10))
    p.append(text(705, 80, "ГРАФ ДІЙ (УМОВИ, ЦИКЛИ, ПЕРЕХОДИ)", size=12, bold=True, color=NEG))
    
    # Graph nodes
    p.append(cblock(605, 105, 200, 38, ["0: NAV_TAKEOFF (h=30m)"], "#eef2ff", NEG, size=11))
    p.append(cblock(605, 165, 200, 38, ["1: NAV_WAYPOINT (Сектор)"], "#f4f6f8", LINE, size=11))
    p.append(cblock(605, 225, 200, 38, ["2: NAV_WAYPOINT (Обхід)"], "#f4f6f8", LINE, size=11))
    p.append(cblock(505, 290, 190, 40, ["3: IF Bat &lt; 30% JUMP 6", "(аварійний вихід)"], "#fef2f2", POS, color=POS, size=10))
    p.append(cblock(720, 290, 190, 40, ["4: DO_JUMP (seq 1, N=4)", "(цикл сканування)"], "#eafaef", FIELD, color=FIELD, size=10))
    p.append(cblock(605, 360, 200, 38, ["5: NAV_WAYPOINT (Фінал)"], "#f4f6f8", LINE, size=11))
    p.append(cblock(605, 415, 200, 38, ["6: NAV_RETURN_TO_LAUNCH"], "#fff7ed", "#ea580c", size=11))

    # Connections in graph
    p.append(carrow(705, 143, 705, 163, INK, "Ink"))
    p.append(carrow(705, 203, 705, 223, INK, "Ink"))
    
    # Branching from 2
    p.append(carrow(660, 263, 600, 288, POS, "R"))
    p.append(carrow(750, 263, 815, 288, FIELD, "G"))
    
    # Loop back from 4 to 1
    p.append('<path d="M 850 290 L 850 184 L 807 184" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrG)"/>' % FIELD)
    p.append(text(880, 235, "repeat &gt; 0", size=10, bold=True, color=FIELD))
    
    # Exit loop from 4 to 5
    p.append(carrow(815, 330, 755, 358, INK, "Ink"))
    
    # Battery jump from 3 to 6
    p.append('<path d="M 550 330 L 550 434 L 603 434" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrR)"/>' % POS)
    p.append(text(515, 385, "тривога", size=10, bold=True, color=POS))
    
    # Regular advance from 5 to 6
    p.append(carrow(705, 398, 705, 413, INK, "Ink"))

    render(os.path.join(OUT, "mission-graph.svg"), W, H, *p)


# ── 2. do-jump-state.svg: Механіка DO_JUMP і таблиця лічильників у RAM ────────
def fig_do_jump_state():
    W, H = 960, 460
    p = [COL_MARKERS]
    
    p.append(text(W / 2, 28, "Внутрішній стан DO_JUMP: статичний Flash проти лічильників у RAM", size=14, bold=True, color=INK))
    
    # Left box: Static Storage (Flash)
    p.append(rect(40, 55, 410, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=8))
    p.append(text(245, 82, "FLASH / EEPROM (Статичний масив місії)", size=12, bold=True, color=INK))
    
    flash_rows = [
        ("seq 0", "NAV_TAKEOFF (alt=40m)", "#f1f5f9"),
        ("seq 1", "NAV_WAYPOINT (lat1, lon1)", "#eef2ff"),
        ("seq 2", "NAV_WAYPOINT (lat2, lon2)", "#eef2ff"),
        ("seq 3", "DO_SET_SERVO (ch=5, pwm=1900)", "#f1f5f9"),
        ("seq 4", "DO_JUMP (target=1, repeats=3)", "#fef3c7"),
        ("seq 5", "NAV_LAND (lat0, lon0)", "#f1f5f9"),
    ]
    ry = 105
    for s_label, s_cmd, s_bg in flash_rows:
        p.append(rect(55, ry, 70, 42, fill="#e2e8f0", stroke="#cbd5e1", rx=4))
        p.append(text(90, ry + 26, s_label, size=11, bold=True, color=INK))
        p.append(rect(130, ry, 305, 42, fill=s_bg, stroke="#cbd5e1", rx=4))
        p.append(text(282, ry + 26, s_cmd, size=11, color=INK))
        ry += 52

    # Right box: RAM Runtime State
    p.append(rect(490, 55, 430, 380, fill="#ffffff", stroke=NEG, sw=1.4, rx=8))
    p.append(text(705, 82, "ОЗП / RAM (Динамічний контекст виконання)", size=12, bold=True, color=NEG))
    
    # Program counter indicator
    p.append(rect(510, 105, 390, 55, fill="#eff6ff", stroke="#bfdbfe", rx=6))
    p.append(text(705, 126, "Поточний вказівник: current_seq = 4", size=12, bold=True, color=NEG))
    p.append(text(705, 146, "Автопілот зустрів DO_JUMP (target=1, repeats=3)", size=10.5, color=MUTED))
    
    # Jump Table Box
    p.append(rect(510, 175, 390, 165, fill="#fafafa", stroke="#e5e7eb", rx=6))
    p.append(text(705, 198, "Таблиця лічильників циклів (RAM Jump Table)", size=11.5, bold=True, color=INK))
    
    table_headers = ["Пункт місії", "Початково", "Залишилось", "Дія на ітерації"]
    th_x = [560, 640, 720, 820]
    for i, htitle in enumerate(table_headers):
        p.append(text(th_x[i], 220, htitle, size=10, bold=True, color=MUTED))
        
    # Table entry
    p.append(line(525, 228, 885, 228, color="#e5e7eb", sw=1))
    p.append(text(560, 248, "seq = 4", size=11, bold=True, color=INK))
    p.append(text(640, 248, "3", size=11, color=MUTED))
    p.append(text(720, 248, "2", size=12, bold=True, color=POS))
    p.append(text(820, 248, "seq := 1 (стрибок)", size=10.5, bold=True, color=FIELD))
    
    p.append(text(705, 280, "Ітерація 1: залишок 3 -> 2, стрибок на seq 1", size=10, color=MUTED))
    p.append(text(705, 300, "Ітерація 2: залишок 2 -> 1, стрибок на seq 1", size=10, color=MUTED))
    p.append(text(705, 320, "Ітерація 3: залишок 1 -> 0, вихід на seq 5", size=10, color=MUTED))

    # Guard Box
    p.append(rect(510, 355, 390, 65, fill="#fef2f2", stroke="#fecaca", rx=6))
    p.append(text(705, 378, "Захист: скидання лічильників при зміні місії", size=11, bold=True, color=POS))
    p.append(text(705, 398, "Перезавантаження або команда RESTART обнуляє RAM-таблицю", size=10, color=INK))

    # Connection arrow between Flash DO_JUMP and RAM state
    p.append(carrow(435, 335, 508, 248, FIELD, "G", sw=2.2))

    render(os.path.join(OUT, "do-jump-state.svg"), W, H, *p)


# ── 3. condition-evaluation.svg: Конвеєр умов та неблокуюче оцінювання ───────
def fig_condition_evaluation():
    W, H = 960, 470
    p = [COL_MARKERS]
    
    p.append(text(W / 2, 26, "Неблокуючий конвеєр оцінювання умов у польотному циклі автопілота", size=14, bold=True, color=INK))
    
    # 3 major stages
    # 1: Flight telemetry feed
    p.append(cblock(40, 65, 250, 110, [
        "ТЕЛЕМЕТРІЯ ТА ДАВАЧІ",
        "• GNSS: дистанція до точки",
        "• Компас/IMU: кут рискання",
        "• Таймер: dt від старту умови",
        "• Батарея: напруга, струм, SoC"
    ], "#f8fafc", "#94a3b8", size=11))
    
    # 2: Condition Gate Evaluator
    p.append(cblock(350, 65, 260, 110, [
        "ГЕЙТ ОЦІНКИ УМОВИ",
        "CONDITION_DELAY: dt &gt;= T",
        "CONDITION_DISTANCE: dist &lt;= D",
        "CONDITION_YAW: |yaw - target| &lt; eps",
        "BATTERY_GUARD: soc &gt;= limit"
    ], "#eff6ff", NEG, color=NEG, size=11))
    
    # 3: Flow Dispatcher
    p.append(cblock(670, 65, 250, 110, [
        "ДИСПЕТЧЕР ВИКОНАННЯ",
        "• Умова TRUE: advance_pc()",
        "• Умова FALSE: hold_state()",
        "• Аварія: jump_emergency()",
        "НЕ блокує навігаційний контур!"
    ], "#f0fdf4", FIELD, color=FIELD, size=11))

    # Horizontal arrows between top blocks
    p.append(carrow(292, 120, 348, 120, INK, "Ink", sw=2.0))
    p.append(text(320, 110, "виміри", size=10, color=MUTED))
    p.append(carrow(612, 120, 668, 120, INK, "Ink", sw=2.0))
    p.append(text(640, 110, "статус", size=10, color=MUTED))

    # Bottom: Step by step timeline in 50Hz control loop
    p.append(rect(40, 205, 880, 240, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(480, 230, "Поведінка всередині кванту часу 20 мс (50 Гц Main Loop)", size=12, bold=True, color=INK))

    ticks = [
        ("Такт t = 0 мс", ["NAV_WAYPOINT активний", "Команда: CONDITION_DIST 50m", "dist = 180m &gt; 50m", "-> Результат: FALSE (вихід)"], "#ffffff", LINE),
        ("Такт t = 20 мс ... 1.2 с", ["Контур стабілізації працює", "Мотори коригують крен/тангаж", "dist = 120m -> 80m -> 52m", "-> Результат: FALSE (вихід)"], "#ffffff", LINE),
        ("Такт t = 1.24 с", ["dist = 48m &lt;= 50m", "Умову CONDITION_DIST виконано!", "-> Результат: TRUE", "Запуск: DO_SET_SERVO 1900"], "#ecfdf5", FIELD),
        ("Такт t = 1.26 с", ["Сервопривід відкрито", "Вказівник: seq := seq + 1", "Перехід до наступного пункту", "Політ триває без затримок"], "#f0f9ff", NEG)
    ]
    
    tx = 60
    for title_txt, desc_lines, fill_c, strk_c in ticks:
        p.append(cblock(tx, 255, 195, 160, [title_txt] + desc_lines, fill_c, strk_c, size=10.5))
        if tx < 650:
            p.append(carrow(tx + 197, 335, tx + 218, 335, INK, "Ink", sw=1.6))
        tx += 220

    render(os.path.join(OUT, "condition-evaluation.svg"), W, H, *p)


# ── 4. mission-vm-architecture.svg: Архітектура віртуальної машини ────────────
def fig_mission_vm_architecture():
    W, H = 960, 480
    p = [COL_MARKERS]
    
    p.append(text(W / 2, 28, "Архітектура бортової віртуальної машини місій (Mission VM)", size=14, bold=True, color=INK))
    
    # Left column: Program Memory & Bytecode Loader
    p.append(rect(35, 60, 245, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=8))
    p.append(text(157, 88, "ПРОГРАМНА ПАМ'ЯТЬ", size=12, bold=True, color=INK))
    p.append(text(157, 106, "(Байткод місії в ROM/RAM)", size=10, color=MUTED))
    
    bcode_samples = [
        "0x00: OP_TAKEOFF [30m, 5m/s]",
        "0x01: OP_NAV_WP  [lat1, lon1]",
        "0x02: OP_COND_DIST [40m]",
        "0x03: OP_SET_ACT [ch5, 1800]",
        "0x04: OP_NAV_WP  [lat2, lon2]",
        "0x05: OP_JUMP_IF [bat&lt;30, 0x08]",
        "0x06: OP_LOOP    [tgt=1, cnt=3]",
        "0x07: OP_RTL     []",
        "0x08: OP_LAND_NOW []"
    ]
    by = 125
    for bcode in bcode_samples:
        p.append(rect(45, by, 225, 28, fill="#ffffff", stroke="#e2e8f0", rx=4))
        p.append(text(157, by + 18, bcode, size=10, color=INK))
        by += 35

    # Center column: The VM Engine Core
    p.append(rect(305, 60, 350, 395, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(480, 88, "ЯДРО MISSION VM (RTOS Task / Tick)", size=12, bold=True, color=NEG))
    
    # Internal VM registers
    p.append(rect(320, 110, 320, 100, fill="#f0f9ff", stroke="#bae6fd", rx=6))
    p.append(text(480, 130, "Регістри та контекст VM", size=11, bold=True, color=INK))
    p.append(text(480, 150, "PC (Program Counter): 0x05", size=10.5, bold=True, color=NEG))
    p.append(text(480, 170, "Loop Counter [0..MAX_LOOPS]: {1: 2}", size=10.5, color=INK))
    p.append(text(480, 190, "Tick Timer: 1420 ms | Status: RUNNING", size=10.5, color=MUTED))

    # Core Execution stages inside VM
    p.append(cblock(320, 225, 320, 42, ["1. FETCH: Читання інструкції за PC"], "#f8fafc", LINE, size=11))
    p.append(cblock(320, 280, 320, 42, ["2. DECODE: Селектор Opcode &amp; Аргументи"], "#f8fafc", LINE, size=11))
    p.append(cblock(320, 335, 320, 42, ["3. EVAL &amp; DISPATCH: Умови / Дії / Стрибки"], "#eafaef", FIELD, color=FIELD, size=11))
    p.append(cblock(320, 395, 320, 45, ["4. SAFETY GUARD: Перевірка лічильника", "зациклення та ліміту часу кроку"], "#fef2f2", POS, color=POS, size=10.5))

    # Right column: Interfaces & Hardware
    p.append(rect(680, 60, 245, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=8))
    p.append(text(802, 88, "БОРТОВІ СИСТЕМИ", size=12, bold=True, color=INK))
    p.append(text(802, 106, "(Виконання та сенсорика)", size=10, color=MUTED))
    
    hw_blocks = [
        ("Навігаційний контур", ["Уставка цілі: WP (x, y, z)", "Контроль радіуса прийняття"], "#eff6ff", NEG),
        ("Виконавчі приводи", ["PWM сервоприводів", "Корисне навантаження / реле"], "#fff7ed", "#ea580c"),
        ("Оцінювач EKF / Сенсори", ["Позиція, висота, yaw", "Напруга та залишок АКБ"], "#f0fdf4", FIELD),
        ("Failsafe Supervisor", ["Перехоплення керування", "Аварійне переривання VM"], "#fef2f2", POS)
    ]
    hy = 125
    for hname, hdesc, hfill, hstroke in hw_blocks:
        p.append(cblock(692, hy, 220, 68, [hname] + hdesc, hfill, hstroke, size=10.5))
        hy += 78

    # Connecting arrows
    p.append(carrow(282, 246, 318, 246, INK, "Ink", sw=2.0))
    p.append(carrow(642, 355, 690, 160, NEG, "B", sw=1.8))
    p.append(carrow(642, 360, 690, 235, "#ea580c", "Ink", sw=1.8))
    p.append(carrow(690, 315, 642, 365, FIELD, "G", sw=1.8))
    p.append(carrow(690, 395, 642, 415, POS, "R", sw=2.0))

    render(os.path.join(OUT, "mission-vm-architecture.svg"), W, H, *p)


if __name__ == "__main__":
    fig_mission_graph()
    fig_do_jump_state()
    fig_condition_evaluation()
    fig_mission_vm_architecture()
    print("Figures generated successfully.")
