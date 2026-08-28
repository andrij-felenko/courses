# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))

def block(x, y, w, h, lines, fill, stroke, color=INK, size=12.0, bold=True):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.7, rx=8)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out

# ── 1. control-sources-hierarchy: Архітектура множинності джерел та арбітражу ─
def fig_sources_hierarchy():
    W, H = 980, 480
    p = [COL_MARKERS]
    p.append(text(W / 2, 34, "Ієрархія та шлях проходження сигналів керування: від джерел до приводів",
                  size=14, color=INK, bold=True))
    
    src_y = [70, 150, 230, 310]
    src_data = [
        ("Аварійний Failsafe", ["КРИТИЧНИЙ FAILSAFE", "втрата зв'язку, батарея, геозона", "Пріоритет 1 (Найвищий)"], "#fdecea", POS),
        ("Пульт RC (Pilot)", ["РУЧНИЙ ПУЛЬТ RC", "стіки пілота (CRSF / ELRS / SBUS)", "Пріоритет 2 (Перехоплення)"], "#fff5e6", "#d98a00"),
        ("Бортовий комп'ютер", ["OFFBOARD КОМПАНЬЙОН", "комп'ютерний зір, локальне планування", "Пріоритет 3 (Автономія)"], "#eef2ff", NEG),
        ("Наземна станція (GCS)", ["НАЗЕМНА СТАНЦІЯ GCS", "операторські місії, вейпойнти", "Пріоритет 4 (Базовий)"], "#eafaef", FIELD)
    ]
    
    for i, (tag, lines, fill_col, strk_col) in enumerate(src_data):
        y = src_y[i]
        p.append(block(30, y, 230, 64, lines, fill_col, strk_col, size=11, bold=True))
        p.append(arrow(260, y + 32, 310, y + 32, color=INK, sw=1.6))
    
    p.append(block(310, 60, 160, 324, 
                   ["ДЕТЕКТОР", "ЖИТТЯ ТА", "АКТИВНОСТІ", "", "• Heartbeat", "• Watchdog", "• Валідність кадру", "• Детект стіків", "• Таймаут зв'язку"],
                   "#f4f4f5", INK, size=11.5, bold=True))
    
    p.append(arrow(470, 222, 520, 222, color=INK, sw=2.2))
    p.append(text(495, 212, "статуси", size=10, color=MUTED))
    
    p.append(block(520, 110, 170, 224, 
                   ["ПРІОРИТЕТНИЙ", "СЕЛЕКТОР (MUX)", "", "Арбітраж за", "матрицею прав:", "Failsafe &gt; RC &gt;", "Offboard &gt; GCS"],
                   "#eef6ff", NEG, color=NEG, size=12, bold=True))
    
    p.append(carrow(690, 222, 740, 222, NEG, "B", sw=2.2))
    p.append(text(715, 212, "вибране", size=10, color=NEG))
    
    p.append(block(740, 110, 190, 224, 
                   ["БЕЗУДАРНИЙ", "ФІЛЬТР ТА SLEW-RATE", "", "• Захоплення стану", "• Обмеження темпу du/dt", "• Зшивання інтегратора", "• Захист від ударів"],
                   "#eafaef", FIELD, color=FIELD, size=11.5, bold=True))
    
    p.append(carrow(835, 334, 835, 390, FIELD, "G", sw=2.2))
    p.append(block(690, 390, 260, 60, 
                   ["ВНУТРІШНІЙ РЕГУЛЯТОР ТА ПРИВОДИ", "каскадні ПІД-контури → мікшер моторів"],
                   "#ffffff", INK, size=11, bold=True))
    
    p.append(text(W / 2, 468, 
                  "Селектор не пропускає команди «напряму»: кожне джерело проходить перевірку життєздатності та фільтр безударного перемикання.",
                  size=11, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "control-sources-hierarchy.svg"), W, H, *p,
           title="Архітектура множинності джерел та арбітражу керування")

# ── 2. source-arbitration-flow: Блок-схема прийняття рішень арбітром ──────────
def fig_arbitration_flow():
    W, H = 960, 450
    p = [COL_MARKERS]
    p.append(text(W / 2, 28, "Алгоритм арбітражу: послідовна оцінка авторитету на кожному такті петлі",
                  size=14, color=INK, bold=True))
    
    # Старт ліворуч
    p.append(block(20, 75, 100, 50, ["Новий такт", "100–400 Гц"], "#ffffff", INK, size=10.5))
    p.append(arrow(120, 100, 150, 100, color=INK, sw=1.6))
    
    # Ряд 1: Умови (y = 65..135, h = 70)
    # Умова 1: Failsafe
    p.append(block(150, 65, 130, 70, ["Умова FAILSAFE?", "батарея / геозона /", "втрата зв'язку"], "#fdecea", POS, size=10.5))
    p.append(carrow(215, 135, 215, 195, POS, "R", sw=1.8))
    p.append(text(225, 165, "ТАК", size=10, color=POS, bold=True, anchor="start"))
    p.append(arrow(280, 100, 310, 100, color=INK, sw=1.6))
    p.append(text(295, 90, "НІ", size=9.5, color=MUTED, bold=True))
    
    # Умова 2: RC Sticks
    p.append(block(310, 65, 135, 70, ["RC активний І", "рух стіків?", "|stick| &gt; поріг"], "#fff5e6", "#d98a00", size=10.5))
    p.append(carrow(377, 135, 377, 195, "#d98a00", "B", sw=1.8))
    p.append(text(387, 165, "ТАК", size=10, color="#d98a00", bold=True, anchor="start"))
    p.append(arrow(445, 100, 475, 100, color=INK, sw=1.6))
    p.append(text(460, 90, "НІ", size=9.5, color=MUTED, bold=True))
    
    # Умова 3: Offboard
    p.append(block(475, 65, 135, 70, ["Offboard живий?", "Heartbeat &lt; 500мс", "+ потік даних"], "#eef2ff", NEG, size=10.5))
    p.append(carrow(542, 135, 542, 195, NEG, "B", sw=1.8))
    p.append(text(552, 165, "ТАК", size=10, color=NEG, bold=True, anchor="start"))
    p.append(arrow(610, 100, 640, 100, color=INK, sw=1.6))
    p.append(text(625, 90, "НІ", size=9.5, color=MUTED, bold=True))
    
    # Умова 4: GCS / Mission
    p.append(block(640, 65, 130, 70, ["Місія GCS активна?", "Автопілот веде", "за точками"], "#eafaef", FIELD, size=10.5))
    p.append(carrow(705, 135, 705, 195, FIELD, "G", sw=1.8))
    p.append(text(715, 165, "ТАК", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(carrow(770, 100, 805, 100, POS, "R", sw=1.6))
    p.append(text(787, 90, "НІ", size=9.5, color=POS, bold=True))
    
    # Відмова (всі мовчать)
    p.append(block(805, 65, 135, 70, ["Всі джерела німі", "Критичний збій", "керування"], "#fdecea", POS, size=10.5))
    p.append(carrow(872, 135, 872, 195, POS, "R", sw=1.8))
    
    # Ряд 2: Вибрані джерела / дії (y = 195..255, h = 60)
    p.append(block(150, 195, 130, 60, ["ДЖЕРЕЛО: FAILSAFE", "Аварійне RTL / Land", "Термінація"], "#fdecea", POS, size=10))
    p.append(block(310, 195, 135, 60, ["ДЖЕРЕЛО: RC PILOT", "Ручне перехоплення", "Прямий кут/швидкість"], "#fff5e6", "#d98a00", size=10))
    p.append(block(475, 195, 135, 60, ["ДЖЕРЕЛО: OFFBOARD", "Компаньйон / AI", "Уставки зору / SLAM"], "#eef2ff", NEG, size=10))
    p.append(block(640, 195, 130, 60, ["ДЖЕРЕЛО: GCS AUTO", "Автономна місія", "Навігація за планом"], "#eafaef", FIELD, size=10))
    p.append(block(805, 195, 135, 60, ["РЕАКЦІЯ: FAILSAFE", "Перехід у безпечний", "стан зупинки"], "#fdecea", POS, size=10))
    
    # Збір виходів у шину (y = 255 -> 310)
    cx_list = [215, 377, 542, 705, 872]
    for cx in cx_list:
        p.append(line(cx, 255, cx, 310, color=MUTED, sw=1.4))
    
    p.append(line(215, 310, 872, 310, color=MUTED, sw=1.6))
    p.append(carrow(542, 310, 542, 355, FIELD, "G", sw=2.2))
    
    p.append(block(310, 355, 465, 55, 
                   ["ПЕРЕДАТИ ОБРАНУ УСТАВКУ В БЕЗУДАРНИЙ ФІЛЬТР", "перевірка стрибка Δu, обмеження slew rate, зшивання інтегратора"],
                   "#ffffff", FIELD, color=FIELD, size=11, bold=True))
    
    p.append(text(W / 2, 435, 
                  "Будь-яке витіснення (наприклад, рух стіка пілота) перемикає джерело миттєво, але на вихід подається через згладжувальний фільтр.",
                  size=11, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "source-arbitration-flow.svg"), W, H, *p,
           title="Блок-схема арбітражу джерел керування")

# ── 3. bumpless-transition: Ступінчастий удар проти плавного перемикання ──────
def fig_bumpless_transition():
    W, H = 940, 420
    p = [COL_MARKERS]
    p.append(text(W / 2, 32, "Перемикання джерел: ступінчастий удар проти безударного зшивання (Slew Rate)",
                  size=14, color=INK, bold=True))
    
    # Ліва панель: Ударне перемикання
    p.append(rect(40, 60, 410, 300, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    p.append(text(245, 85, "БЕЗ ЗШИВАННЯ: Ступінчастий удар", size=12.5, color=POS, bold=True))
    
    p.append(line(80, 310, 420, 310, color=LINE, sw=1.2))
    p.append(line(80, 310, 80, 110, color=LINE, sw=1.2))
    p.append(text(420, 325, "час t", size=10, color=MUTED, anchor="end"))
    p.append(text(75, 115, "u(t)", size=10, color=MUTED, anchor="end"))
    
    p.append(line(80, 240, 230, 240, color=NEG, sw=2.2))
    p.append(text(155, 230, "Джерело 1 (Offboard: 30%)", size=10, color=NEG))
    
    p.append(line(230, 240, 230, 140, color=POS, sw=2.4, dash="4 3"))
    p.append(carrow(245, 235, 245, 145, POS, "R", sw=1.5))
    p.append(text(255, 190, "Стрибок Δu = 50%", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(255, 205, "(за 1 такт, 2.5 мс)", size=9.5, color=POS, anchor="start"))
    
    p.append(line(230, 140, 410, 140, color="#d98a00", sw=2.2))
    p.append(text(330, 130, "Джерело 2 (RC: 80%)", size=10, color="#d98a00"))
    
    p.append(block(60, 325, 370, 25, ["Наслідок: піковий момент, зрив ПІД-інтегратора, удар по моторах"],
                   "#fdecea", POS, color=POS, size=10))

    # Права панель: Безударне зшивання
    p.append(rect(490, 60, 410, 300, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(695, 85, "БЕЗУДАРНЕ ЗШИВАННЯ: Slew-Rate лімітер", size=12.5, color=FIELD, bold=True))
    
    p.append(line(530, 310, 870, 310, color=LINE, sw=1.2))
    p.append(line(530, 310, 530, 110, color=LINE, sw=1.2))
    p.append(text(870, 325, "час t", size=10, color=MUTED, anchor="end"))
    p.append(text(525, 115, "u(t)", size=10, color=MUTED, anchor="end"))
    
    p.append(line(530, 240, 650, 240, color=NEG, sw=2.2))
    p.append(text(590, 230, "Джерело 1 (30%)", size=10, color=NEG))
    
    p.append(line(650, 240, 750, 140, color=FIELD, sw=2.8))
    p.append(text(710, 205, "Керований нахил", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(710, 220, "du/dt ≤ max_rate", size=9.5, color=FIELD, anchor="start"))
    
    p.append(line(650, 140, 750, 140, color="#d98a00", sw=1.5, dash="3 3"))
    p.append(line(750, 140, 860, 140, color="#d98a00", sw=2.2))
    p.append(text(800, 130, "Джерело 2 (80%)", size=10, color="#d98a00"))
    
    p.append(line(650, 310, 650, 240, color=MUTED, sw=1.0, dash="2 2"))
    p.append(line(750, 310, 750, 140, color=MUTED, sw=1.0, dash="2 2"))
    p.append(line(650, 290, 750, 290, color=FIELD, sw=1.4))
    p.append(text(700, 282, "t_ramp (150–300 мс)", size=9.5, color=FIELD))
    
    p.append(block(510, 325, 370, 25, ["Наслідок: плавна динаміка, відсутність струмових піків, керованість"],
                   "#eafaef", FIELD, color=FIELD, size=10))

    p.append(text(W / 2, 400, 
                  "Безударний фільтр затискає похідну уставки: внутрішній контур сприймає зміну як плавний маневр, а не аварійний стрибок.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bumpless-transition.svg"), W, H, *p,
           title="Порівняння ударного та безударного перемикання джерел керування")

if __name__ == "__main__":
    fig_sources_hierarchy()
    fig_arbitration_flow()
    fig_bumpless_transition()
    print("Figures generated successfully.")
