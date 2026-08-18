# -*- coding: utf-8 -*-
"""Фігури до теми «CSMA/CD: колізії у спільному дроті Ethernet».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Часова діаграма виявлення колізії (Worst-case Collision) ──────────────
def fig_csma_timeline():
    """Часова шкала найгіршого випадку колізії: станція A починає о t=0,
    станція B починає за мить до приходу фронту (t = tau - eps).
    Хвиля колізії повертається до A о t = 2*tau - eps."""
    W, H = 820, 500
    f = [text(W / 2, 26, "Часова діаграма колізії та критичного вікна 2τ", size=15, bold=True)]

    # Вертикальні осі станцій A та B
    xa, xb = 160, 660
    f.append(line(xa, 60, xa, 430, color=LINE, sw=2))
    f.append(line(xb, 60, xb, 430, color=LINE, sw=2))

    # Заголовки вузлів
    f.append(fitbox(xa - 70, 50, 140, 32, "Станція A (TX)", size=12, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(fitbox(xb - 70, 50, 140, 32, "Станція B (TX)", size=12, bold=True, fill="#eef3ff", stroke=NEG))

    # Вісь часу зліва
    f.append(arrow(60, 80, 60, 440, color=MUTED, sw=1.5))
    f.append(text(45, 260, "Час t", size=11, color=MUTED, anchor="middle", bold=True))

    # Позначки часу на осі A
    f.append(text(xa - 15, 100, "t = 0", size=11, color=INK, anchor="end", bold=True))
    f.append(text(xa - 15, 230, "t = τ", size=11, color=MUTED, anchor="end"))
    f.append(text(xa - 15, 370, "t = 2τ − ε", size=11, color=POS, anchor="end", bold=True))

    # Позначки часу на осі B
    f.append(text(xb + 15, 215, "t = τ − ε", size=11, color=INK, anchor="start", bold=True))
    f.append(text(xb + 15, 240, "t = τ", size=11, color=POS, anchor="start", bold=True))

    # 1. Сигнал від A до B
    f.append(line(xa, 100, xb, 230, color=NEG, sw=2.5))
    f.append(arrow(xa, 100, (xa + xb) / 2 + 10, 165, color=NEG, sw=2.5))
    f.append(fitbox(270, 125, 220, 26, "Фронт передачі кадру від A", size=10, fill="#f4f6f8", stroke=NEG))

    # Початок передачі B о t = tau - eps
    f.append(circle(xb, 215, 4, fill=POS, stroke=POS))
    f.append(fitbox(xb + 20, 175, 130, 34, "B чує «тишу»\nі починає передачу", size=9.5, fill="#fff7e6", stroke=POS))

    # Точка колізії біля B
    f.append(circle(xb - 10, 230, 6, fill="#fdecea", stroke=POS, sw=2))
    f.append(fitbox(520, 245, 130, 34, "Колізія сигналів\nбіля станції B!", size=10, bold=True, fill="#fdecea", stroke=POS))

    # 2. Зворотний фронт колізії від B до A
    f.append(line(xb - 10, 230, xa, 370, color=POS, sw=2.5, dash="5,3"))
    f.append(arrow(xb - 10, 230, (xa + xb) / 2 - 10, 300, color=POS, sw=2.5))
    f.append(fitbox(260, 305, 230, 26, "Фронт спотвореного сигналу + Jam", size=10, fill="#fdecea", stroke=POS))

    # Станція B надсилає Jam
    f.append(rect(xb, 230, 18, 50, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(xb + 30, 260, "Jam (32 біти)", size=10, color=POS, anchor="start"))

    # Станція A виявляє колізію о t = 2*tau - eps
    f.append(circle(xa, 370, 5, fill=POS, stroke=POS))
    f.append(rect(xa, 370, 18, 50, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(xa - 150, 390, 140, 34, "A виявляє колізію\nі надсилає свій Jam", size=10, bold=True, fill="#fdecea", stroke=POS))

    # Фігурні дужки / виділення тривалості передачі
    f.append(rect(xa - 4, 100, 8, 270, fill="#2457d6", stroke=NEG, sw=1))
    f.append(fitbox(70, 450, 680, 42,
                    "Умова надійного виявлення: T_кадру ≥ 2τ. Якщо кадр коротший за 2τ, станція A завершить\n"
                    "передачу до приходу колізії і помилково вважатиме кадр успішно доставленим!",
                    size=10.5, bold=True, fill="#fff7e6", stroke=POS))

    render(os.path.join(IMG, "csma-timeline.svg"), W, H, *f)


# ── 2. Фізичні схеми виявлення колізій (Coax vs UTP) ────────────────────────
def fig_collision_circuits():
    """Фізика виявлення колізій:
    Ліворуч: 10BASE5/10BASE2 коаксіал — просідання постійної напруги нижче -1.5В при 2х82мА на 25 Ом.
    Праворуч: 10BASE-T вита пара — одночасна активність на парах TX та RX у напівдуплексі."""
    W, H = 820, 420
    f = [text(W / 2, 24, "Фізичні механізми виявлення колізій у середовищі Ethernet", size=15, bold=True)]

    # Ліва панель: Коаксіал
    f.append(rect(20, 45, 380, 360, fill="#fafbfc", stroke=LINE, sw=1.2))
    f.append(text(210, 68, "Коаксіальний кабель (10BASE5 / 10BASE2)", size=12, bold=True, color=NEG))

    # Спільний коаксіальний дріт
    f.append(line(45, 140, 375, 140, color=LINE, sw=3))
    # Термінатори 50 Ом
    f.append(fitbox(35, 115, 30, 50, "50\nΩ", size=9, fill="#eef3ff", stroke=LINE))
    f.append(fitbox(355, 115, 30, 50, "50\nΩ", size=9, fill="#eef3ff", stroke=LINE))
    f.append(text(210, 125, "Спільний сегмент: R_екв = 50 || 50 = 25 Ом", size=9.5, color=MUTED))

    # Джерело струму MAU 1
    f.append(arrow(110, 200, 110, 145, color=NEG, sw=2))
    f.append(fitbox(70, 205, 90, 32, "TX 1: 82 мА\n(генератор)", size=9.5, fill="#eef3ff", stroke=NEG))

    # Джерело струму MAU 2
    f.append(arrow(310, 200, 310, 145, color=NEG, sw=2))
    f.append(fitbox(270, 205, 90, 32, "TX 2: 82 мА\n(генератор)", size=9.5, fill="#eef3ff", stroke=NEG))

    # Рівні напруги в коаксіалі
    f.append(rect(35, 255, 350, 135, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(210, 275, "Рівні напруги на центральній жилі:", size=10.5, bold=True))
    f.append(line(45, 290, 375, 290, color="#cccccc", sw=1, dash="2,2"))
    f.append(text(55, 305, "0 станцій (тиша):", size=10, bold=True))
    f.append(text(365, 305, "U = 0.0 В", size=10, color=INK, anchor="end"))
    f.append(text(55, 325, "1 станція передає:", size=10, bold=True))
    f.append(text(365, 325, "U_сер ≈ −1.02 В", size=10, color=NEG, anchor="end"))
    f.append(text(55, 345, "Поріг компаратора CD:", size=10, bold=True, color=POS))
    f.append(text(365, 345, "U_ref = −1.50 В", size=10, color=POS, anchor="end", bold=True))
    f.append(text(55, 370, "2 станції (колізія):", size=10, bold=True, color=POS))
    f.append(text(365, 370, "U_сер < −1.6 В  (CD!)", size=10, color=POS, anchor="end", bold=True))

    # Права панель: Вита пара (10BASE-T Hub)
    f.append(rect(420, 45, 380, 360, fill="#fafbfc", stroke=LINE, sw=1.2))
    f.append(text(610, 68, "Вита пара на хабі (10BASE-T Half-Duplex)", size=12, bold=True, color=FIELD))

    # Блок NIC
    f.append(rect(440, 100, 100, 130, fill="#eef3ff", stroke=NEG, sw=1.5))
    f.append(text(490, 120, "Мережева\nкарта (NIC)", size=10.5, bold=True, anchor="middle"))

    # Блок Hub
    f.append(rect(680, 100, 100, 130, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(730, 120, "Концентратор\n(Multiport Hub)", size=10.5, bold=True, anchor="middle"))

    # Лінії TX та RX
    f.append(arrow(540, 150, 680, 150, color=NEG, sw=2))
    f.append(fitbox(565, 132, 90, 20, "Пара TX (1-2)", size=9, fill="#ffffff", stroke=NEG))

    f.append(arrow(680, 190, 540, 190, color=FIELD, sw=2))
    f.append(fitbox(565, 195, 90, 20, "Пара RX (3-6)", size=9, fill="#ffffff", stroke=FIELD))

    # Блок логіки колізії в 10BASE-T
    f.append(rect(435, 255, 350, 135, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(610, 275, "Логічне виявлення колізії в напівдуплексі:", size=10.5, bold=True))
    f.append(fitbox(445, 290, 330, 42,
                    "TX активний І RX активний одночасно\n=> Контролер фіксує колізію (Collision Detect)",
                    size=10, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(445, 340, 330, 42,
                    "У повному дуплексі (Full-Duplex на світчі):\nTX і RX розділені повністю, колізій НЕ буває!",
                    size=10, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "collision-detection-circuits.svg"), W, H, *f)


# ── 3. Блок-схема алгоритму CSMA/CD та BEB ──────────────────────────────────
def fig_beb_state_machine():
    """Алгоритм CSMA/CD з експоненційним відкатом Truncated Binary Exponential Backoff.
    1-persistent carrier sense -> IFG 9.6 мкс -> передача + CD -> Jam -> r in [0, 2^k - 1]."""
    W, H = 820, 560
    f = [text(W / 2, 24, "Алгоритм CSMA/CD та експоненційний відкат (BEB)", size=15, bold=True)]

    # 1. Початок
    f.append(fitbox(330, 45, 160, 32, "Готовий кадр до відправки\nk = 0 (лічильник спроб)", size=10, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(arrow(410, 77, 410, 105, color=LINE))

    # 2. Перевірка каналу (Carrier Sense)
    f.append(fitbox(310, 105, 200, 38, "1-Persistent Carrier Sense:\nЧи є сигнал у дроті?", size=10.5, bold=True, fill="#ffffff", stroke=LINE))

    # Гілка зайнято
    f.append(line(510, 124, 570, 124, color=POS, sw=1.5))
    f.append(line(570, 124, 570, 160, color=POS, sw=1.5))
    f.append(fitbox(525, 160, 90, 26, "Зайнято: чекати", size=9.5, fill="#fff7e6", stroke=POS))
    f.append(line(570, 186, 570, 124, color=POS, sw=1.5))

    # Гілка вільно
    f.append(arrow(410, 143, 410, 175, color=FIELD, sw=1.8))
    f.append(text(420, 160, "Вільно", size=10, color=FIELD, bold=True))

    # 3. Міжкадровий інтервал IFG
    f.append(fitbox(300, 175, 220, 34, "Міжкадровий інтервал (IFG):\nОчікування 96 біт-часів (9.6 мкс)", size=10, fill="#eafaf0", stroke=FIELD))
    f.append(arrow(410, 209, 410, 240, color=LINE))

    # 4. Передача та моніторинг колізій
    f.append(fitbox(280, 240, 260, 40, "Передача кадру (TX)\n+ прослуховування лінії на колізію (CD)", size=10.5, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(arrow(410, 280, 410, 315, color=LINE))

    # 5. Ромб / блок перевірки колізії
    f.append(fitbox(300, 315, 220, 36, "Колізію виявлено?", size=11, bold=True, fill="#ffffff", stroke=POS))

    # Успіх (ліворуч)
    f.append(line(300, 333, 160, 333, color=FIELD, sw=1.8))
    f.append(arrow(160, 333, 160, 375, color=FIELD, sw=1.8))
    f.append(text(220, 325, "Ні (успіх)", size=10, color=FIELD, bold=True))
    f.append(fitbox(80, 375, 160, 45, "Кадр передано успішно!\nСкидання k = 0\nГотовність до наступного", size=10, bold=True, fill="#eafaf0", stroke=FIELD))

    # Колізія (праворуч)
    f.append(line(520, 333, 660, 333, color=POS, sw=1.8))
    f.append(arrow(660, 333, 660, 365, color=POS, sw=1.8))
    f.append(text(580, 325, "Так (колізія!)", size=10, color=POS, bold=True))

    # Обробка колізії
    f.append(fitbox(560, 365, 200, 36, "Передача сигналу Jam\n(32 біти послідовності 1010...)", size=10, bold=True, fill="#fdecea", stroke=POS))
    f.append(arrow(660, 401, 660, 425, color=POS, sw=1.5))

    # Збільшення лічильника
    f.append(fitbox(570, 425, 180, 32, "Інкремент спроб: k = k + 1", size=10.5, bold=True, fill="#ffffff", stroke=LINE))
    f.append(arrow(660, 457, 660, 480, color=LINE))

    # Перевірка k > 16
    f.append(fitbox(540, 480, 240, 65,
                    "k > 16?  => Фатальна помилка (Drop)\n"
                    "Інакше BEB: вибір випадкового r:\n"
                    "r ∈ [0, 2^(min(k, 10)) − 1]\n"
                    "Затримка = r × 512 біт-часів (51.2 мкс)",
                    size=9.5, fill="#fff7e6", stroke=POS))

    # Петля повернення на початок
    f.append(line(540, 512, 45, 512, color=MUTED, sw=1.5, dash="4,3"))
    f.append(line(45, 512, 45, 124, color=MUTED, sw=1.5, dash="4,3"))
    f.append(arrow(45, 124, 310, 124, color=MUTED, sw=1.5))
    f.append(text(140, 502, "Після затримки r × 51.2 мкс: повернення до прослуховування", size=9.5, color=MUTED))

    render(os.path.join(IMG, "beb-state-machine.svg"), W, H, *f)


# ── 4. Правило 5-4-3 та розрахунок часового бюджету RTT ──────────────────────
def fig_slot_topology():
    """Топологія максимального колізійного домену за правилом 5-4-3:
    5 сегментів (до 2500 м), 4 репітери, 3 змішані сегменти.
    Бюджет поширення сигналу вкладається у 512 біт-часів (51.2 мкс = 64 байти)."""
    W, H = 820, 410
    f = [text(W / 2, 24, "Топологія правила 5-4-3 та колізійний бюджет Slot Time", size=15, bold=True)]

    # 5 сегментів та 4 репітери по горизонталі
    xs = [50, 210, 370, 530, 690]
    seg_names = [
        "Сегмент 1 (500м)\n[Змішаний / Вузли]",
        "Сегмент 2 (500м)\n[Міжрепітерний лінк]",
        "Сегмент 3 (500м)\n[Змішаний / Вузли]",
        "Сегмент 4 (500м)\n[Міжрепітерний лінк]",
        "Сегмент 5 (500м)\n[Змішаний / Вузли]"
    ]

    for i in range(5):
        is_mixed = (i % 2 == 0)
        fill = "#eef3ff" if is_mixed else "#fafbfc"
        stroke = NEG if is_mixed else MUTED
        f.append(fitbox(xs[i], 55, 80, 55, seg_names[i], size=8.5, fill=fill, stroke=stroke))

    # 4 репітери між сегментами
    xr = [140, 300, 460, 620]
    for i in range(4):
        f.append(line(xs[i] + 80, 82, xr[i], 82, color=LINE, sw=2))
        f.append(fitbox(xr[i], 67, 50, 30, f"R{i+1}", size=11, bold=True, fill="#eafaf0", stroke=FIELD))
        f.append(line(xr[i] + 50, 82, xs[i+1], 82, color=LINE, sw=2))

    # Станції на краях (A ліворуч, B праворуч)
    f.append(fitbox(45, 130, 90, 34, "Вузол A\n(Крайній TX)", size=10, bold=True, fill="#fdecea", stroke=POS))
    f.append(arrow(90, 130, 90, 110, color=POS, sw=1.8))

    f.append(fitbox(685, 130, 90, 34, "Вузол B\n(Крайній RX)", size=10, bold=True, fill="#fdecea", stroke=POS))
    f.append(arrow(730, 130, 730, 110, color=POS, sw=1.8))

    # Загальна довжина коаксіалу
    f.append(line(50, 182, 770, 182, color=LINE, sw=1.5))
    f.append(text(410, 175, "Максимальна фізична довжина траси = 2500 м (5 × 500 м) + AUI кабелі (до 100 м)", size=10, bold=True))

    # Таблиця розрахунку бюджету RTT
    f.append(rect(40, 195, 740, 150, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(410, 215, "Бюджет подвійного обороту сигналу (Worst-Case Round Trip Time — RTT):", size=11, bold=True))

    items = [
        ("Затримка кабелю (2500 м коаксіал + 100 м AUI в обидва боки):", "≈ 22.8 мкс", "(228 біт-часів)"),
        ("Затримка 4 репітерів (регенерація та ретаймінг в обидва боки):", "≈ 6.4 мкс", "(64 біт-часів)"),
        ("Затримка трансиверів DTE / MAU + логіка виявлення колізії:", "≈ 3.2 мкс", "(32 біт-часів)"),
        ("Передача глушильної послідовності Jam (32–48 біт):", "≈ 4.8 мкс", "(48 біт-часів)"),
        ("Сумарний критичний час RTT + Jam (з технологічним запасом):", "≈ 46.5 мкс", "(465 біт-часів)"),
    ]

    y_pos = 236
    for desc, val, bits in items:
        f.append(text(55, y_pos, desc, size=9.5, color=INK))
        f.append(text(580, y_pos, val, size=9.5, color=NEG, bold=True, anchor="end"))
        f.append(text(760, y_pos, bits, size=9.5, color=MUTED, anchor="end"))
        y_pos += 20

    f.append(fitbox(40, 360, 740, 30,
                    "Еталонний Slot Time = 512 біт-часів = 51.2 мкс (64 байти) > 46.5 мкс — 100% гарантія виявлення!",
                    size=10, bold=True, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "slot-time-topology.svg"), W, H, *f)


if __name__ == "__main__":
    fig_csma_timeline()
    fig_collision_circuits()
    fig_beb_state_machine()
    fig_slot_topology()
    print("Всі фігури згенеровано успішно.")
