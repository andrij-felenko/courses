# -*- coding: utf-8 -*-
"""Фігури до теми «CSMA/CA: уникнення колізій у спільному ефірі».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os

# Імпорт спільного svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. CSMA/CD у дроті проти безсилля в ефірі ──────────────────────────────
def fig_cd_vs_ca():
    """Порівняння фізики Ethernet (дріт, спільні рівні) та радіоефіру
    (затухання за законом обернених квадратів, засліплення приймача власним TX)."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Чому виявлення колізій (CSMA/CD) не працює в радіоефірі", size=16, bold=True)]

    # Ліва колонка: Ethernet (дріт)
    f.append(rect(30, 55, 370, 320, fill="#f8fafc", stroke=NEG, sw=1.6))
    f.append(text(215, 82, "Дротовий Ethernet (CSMA/CD)", size=14, bold=True, color=NEG))

    # Дріт
    f.append(line(55, 175, 375, 175, color=LINE, sw=4))
    f.append(text(215, 160, "Спільний кабель (коаксіал / вита пара)", size=11, color=MUTED))

    # Вузли A і B
    f.append(circle(95, 175, 24, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(95, 179, "Вузол A", size=10, bold=True, color=NEG))
    f.append(circle(335, 175, 24, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(335, 179, "Вузол B", size=10, bold=True, color=NEG))

    # Сигнали та амплітуда
    f.append(text(95, 230, "TX: 2.0 В", size=11, bold=True, color=INK))
    f.append(text(335, 230, "TX: 2.0 В", size=11, bold=True, color=INK))
    f.append(rect(130, 250, 170, 48, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(215, 268, "Накладання сигналів", size=11, bold=True, color=POS))
    f.append(text(215, 286, "U = 2.0 В + 1.8 В ≈ 3.8 В", size=11, color=POS))
    f.append(text(215, 335, "Рівні напруги співмірні → приймач легко", size=11, color=INK))
    f.append(text(215, 355, "детектує стрибок напруги під час передачі", size=11, color=INK))

    # Права колонка: Радіоефір (Wi-Fi)
    f.append(rect(440, 55, 370, 320, fill="#f8fafc", stroke=POS, sw=1.6))
    f.append(text(625, 82, "Бездротовий ефір (Wi-Fi)", size=14, bold=True, color=POS))

    # Антени A і B
    f.append(circle(495, 175, 24, fill="#fff7e6", stroke=POS, sw=1.8))
    f.append(text(495, 179, "Станція A", size=10, bold=True, color=POS))
    f.append(circle(755, 175, 24, fill="#fff7e6", stroke=POS, sw=1.8))
    f.append(text(755, 179, "Станція B", size=10, bold=True, color=POS))

    # Потужність
    f.append(text(495, 130, "TX: +20 дБм (100 мВт)", size=10, bold=True, color=POS))
    f.append(text(755, 130, "TX: +20 дБм (100 мВт)", size=10, bold=True, color=POS))

    # Затухання хвилі
    f.append(line(525, 175, 725, 175, color=POS, sw=1.5, dash="4 4"))
    f.append(text(625, 160, "Затухання у просторі (-80 дБ)", size=11, italic=True, color=MUTED))

    f.append(rect(500, 240, 250, 68, fill="#fff2e8", stroke=POS, sw=1.4))
    f.append(text(625, 258, "Власний TX: 100 мВт (+20 дБм)", size=10, bold=True, color=POS))
    f.append(text(625, 276, "Чужий сигнал: 0.00001 мВт (-80 дБм)", size=10, color=MUTED))
    f.append(text(625, 294, "Різниця 10 000 000 разів (100 дБ)", size=10, bold=True, color=POS))

    f.append(text(625, 335, "Власний передавач глушить приймач:", size=11, color=INK))
    f.append(text(625, 355, "чути чужу колізію під час мовлення неможливо", size=11, bold=True, color=POS))

    f.append(text(W / 2, 402, "У радіоефірі колізію не можна вчасно перервати — її слід уникати наперед (Collision Avoidance).",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "csma-cd-vs-ca.svg"), W, H, *f)


# ── 2. Ієрархія міжкадрових інтервалів (IFS) ──────────────────────────────
def fig_interframe_spaces():
    """Ієрархія SIFS, PIFS, DIFS, EIFS та тайм-слоти змагань."""
    W, H = 840, 360
    f = [text(W / 2, 28, "Ієрархія міжкадрових інтервалів (IFS) у стандарті IEEE 802.11", size=16, bold=True)]

    # Вісь часу
    y_axis = 140
    f.append(line(50, y_axis, 790, y_axis, color=LINE, sw=2))
    f.append(arrow(780, y_axis, 810, y_axis, color=LINE, sw=2))
    f.append(text(810, y_axis + 20, "Час", size=11, bold=True, color=LINE, anchor="end"))

    # Блок «Канал звільнився»
    f.append(rect(50, y_axis - 60, 110, 60, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(105, y_axis - 35, "Попередня", size=11, bold=True, color=POS))
    f.append(text(105, y_axis - 18, "передача", size=11, color=POS))
    f.append(line(160, y_axis - 70, 160, y_axis + 140, color=MUTED, sw=1.2, dash="3 3"))

    # SIFS (16 мкс)
    f.append(rect(160, y_axis + 15, 80, 26, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(text(200, y_axis + 32, "SIFS (16 мкс)", size=10, bold=True, color=FIELD))
    f.append(rect(240, y_axis + 10, 120, 36, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(text(300, y_axis + 26, "ACK / CTS / фрагмент", size=10, bold=True, color=FIELD))
    f.append(text(300, y_axis + 40, "(найвищий пріоритет)", size=9, color=FIELD))

    # PIFS (25 мкс)
    f.append(rect(160, y_axis + 60, 130, 26, fill="#fff7e6", stroke="#d97706", sw=1.4))
    f.append(text(225, y_axis + 77, "PIFS (25 мкс) = SIFS + 1 слот", size=10, bold=True, color="#d97706"))
    f.append(rect(290, y_axis + 55, 110, 36, fill="#fff7e6", stroke="#d97706", sw=1.4))
    f.append(text(345, y_axis + 71, "Опитування AP", size=10, bold=True, color="#d97706"))
    f.append(text(345, y_axis + 85, "(режим PCF / маяки)", size=9, color="#d97706"))

    # DIFS (34 мкс)
    f.append(rect(160, y_axis + 105, 180, 26, fill="#eef3ff", stroke=NEG, sw=1.4))
    f.append(text(250, y_axis + 122, "DIFS (34 мкс) = SIFS + 2 слоти", size=10, bold=True, color=NEG))
    f.append(rect(340, y_axis + 100, 130, 36, fill="#eef3ff", stroke=NEG, sw=1.4))
    f.append(text(405, y_axis + 116, "Звичайні дані (DCF)", size=10, bold=True, color=NEG))
    f.append(text(405, y_axis + 130, "+ випадковий Backoff", size=9, color=NEG))

    # Слоти відкату Backoff Slots
    bx = 475
    slot_w = 32
    for i in range(7):
        f.append(rect(bx + i * slot_w, y_axis - 35, slot_w, 35, fill="#ffffff", stroke=NEG, sw=1.2))
        f.append(text(bx + i * slot_w + slot_w / 2, y_axis - 14, str(i + 1), size=10, color=NEG))
    f.append(text(bx + 3.5 * slot_w, y_axis - 45, "Слоти змагань (Backoff Slots, по 9 мкс)", size=11, bold=True, color=NEG))

    # EIFS внизу
    f.append(rect(160, y_axis - 110, 420, 28, fill="#f4f6f8", stroke=MUTED, sw=1.4))
    f.append(text(370, y_axis - 92, "EIFS (SIFS + DIFS + ACK) — пауза при отриманні битого кадру", size=11, bold=True, color=MUTED))

    f.append(text(W / 2, 335, "Коротша пауза гарантує вищий пріоритет: термінові службові кадри (ACK) випереджають звичайні дані.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "interframe-spaces.svg"), W, H, *f)


# ── 3. Процедура відкату (Backoff timeline) ────────────────────────────────
def fig_backoff_timeline():
    """Часова діаграма DCF: DIFS, зворотний відлік слотів, заморожування при появі чужого кадру,
    відновлення після DIFS і передача кадру."""
    W, H = 840, 390
    f = [text(W / 2, 28, "Процедура випадкового відкату (Backoff) та заморожування таймера", size=16, bold=True)]

    y_a = 90
    y_b = 230

    # Рядок станції A
    f.append(text(85, y_a + 25, "Станція A\n(Backoff = 3)", size=11, bold=True, color=NEG))
    f.append(line(160, y_a + 20, 800, y_a + 20, color=LINE, sw=1.8))

    # Рядок станції B
    f.append(text(85, y_b + 25, "Станція B\n(Backoff = 7)", size=11, bold=True, color=POS))
    f.append(line(160, y_b + 20, 800, y_b + 20, color=LINE, sw=1.8))

    # DIFS пауза на початку для обох
    f.append(rect(160, y_a, 60, 40, fill="#eef3ff", stroke=NEG, sw=1.4))
    f.append(text(190, y_a + 24, "DIFS", size=10, bold=True, color=NEG))
    f.append(rect(160, y_b, 60, 40, fill="#fff7e6", stroke=POS, sw=1.4))
    f.append(text(190, y_b + 24, "DIFS", size=10, bold=True, color=POS))

    # Відлік слотів: 3 слоти для обох
    sw = 28
    for i in range(3):
        # A: 3, 2, 1 -> 0
        f.append(rect(220 + i * sw, y_a, sw, 40, fill="#ffffff", stroke=NEG, sw=1.2))
        f.append(text(220 + i * sw + sw / 2, y_a + 24, str(3 - i), size=10, bold=True, color=NEG))
        # B: 7, 6, 5 (лишилося 4)
        f.append(rect(220 + i * sw, y_b, sw, 40, fill="#ffffff", stroke=POS, sw=1.2))
        f.append(text(220 + i * sw + sw / 2, y_b + 24, str(7 - i), size=10, bold=True, color=POS))

    # Станція A починає передачу DATA + SIFS + ACK
    f.append(rect(304, y_a - 10, 200, 60, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(404, y_a + 16, "Кадр DATA (Станція A)", size=11, bold=True, color=FIELD))
    f.append(text(404, y_a + 34, "Ефір зайнятий", size=10, color=FIELD))

    f.append(rect(504, y_a + 5, 30, 30, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    f.append(text(519, y_a + 23, "SIFS", size=9, color=MUTED))

    f.append(rect(534, y_a, 50, 40, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(559, y_a + 24, "ACK", size=10, bold=True, color=FIELD))

    # Станція B у цей час заморожена
    f.append(rect(304, y_b, 280, 40, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(444, y_b + 24, "Таймер ЗАМОРОЖЕНО (залишок = 4)", size=11, bold=True, color=POS))

    # Після закінчення передачі: пауза DIFS для B
    f.append(rect(584, y_b, 60, 40, fill="#fff7e6", stroke=POS, sw=1.4))
    f.append(text(614, y_b + 24, "DIFS", size=10, bold=True, color=POS))

    # Станція B продовжує відлік решти 4 слотів
    for i in range(4):
        f.append(rect(644 + i * sw, y_b, sw, 40, fill="#ffffff", stroke=POS, sw=1.2))
        f.append(text(644 + i * sw + sw / 2, y_b + 24, str(4 - i), size=10, bold=True, color=POS))

    # Станція B починає свою передачу
    f.append(rect(756, y_b - 10, 60, 60, fill="#fff7e6", stroke=POS, sw=1.6))
    f.append(text(786, y_b + 25, "DATA B", size=10, bold=True, color=POS))

    f.append(text(W / 2, 360, "Вузол із меншим лічильником передає першим; суперник зберігає свій прогрес і не починає з нуля.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "backoff-timeline.svg"), W, H, *f)


# ── 4. Прихований та засвічений вузол ──────────────────────────────────────
def fig_hidden_exposed():
    """Топологічні проблеми: Hidden Node (A і C не чують одне одного, колізія на B)
    та Exposed Node (C чує передачу B до A, але міг би безпечно передавати до D)."""
    W, H = 840, 430
    f = [text(W / 2, 28, "Топологічні аномалії спільного радіоефіру", size=16, bold=True)]

    # Ліва половина: Прихований вузол (Hidden Node)
    f.append(rect(25, 55, 380, 335, fill="#f8fafc", stroke=POS, sw=1.6))
    f.append(text(215, 82, "1. Проблема прихованого вузла", size=13, bold=True, color=POS))

    # Радіуси покриття
    f.append(circle(95, 185, 80, fill="#eef3ff", stroke=NEG, sw=1.2))
    f.append(circle(335, 185, 80, fill="#fdecea", stroke=POS, sw=1.2))

    # Вузли A, B, C
    f.append(circle(95, 185, 20, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(95, 189, "A", size=11, bold=True, color=NEG))

    f.append(circle(215, 185, 22, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(215, 189, "B (AP)", size=11, bold=True, color=FIELD))

    f.append(circle(335, 185, 20, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(335, 189, "C", size=11, bold=True, color=POS))

    # Стрілки передачі до B
    f.append(arrow(120, 185, 190, 185, color=NEG, sw=2))
    f.append(text(155, 172, "DATA", size=10, bold=True, color=NEG))
    f.append(arrow(310, 185, 240, 185, color=POS, sw=2))
    f.append(text(275, 172, "DATA", size=10, bold=True, color=POS))

    # Хрест колізії на B
    f.append(rect(145, 275, 140, 46, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(215, 293, "Колізія на вузлі B!", size=11, bold=True, color=POS))
    f.append(text(215, 310, "A і C не чують одне одного", size=10, color=POS))
    f.append(text(215, 345, "Фізичне прослуховування безсиле:", size=11, color=INK))
    f.append(text(215, 365, "A і C вважають, що канал вільний.", size=11, bold=True, color=INK))

    # Права половина: Засвічений вузол (Exposed Node)
    f.append(rect(435, 55, 380, 335, fill="#f8fafc", stroke=NEG, sw=1.6))
    f.append(text(625, 82, "2. Проблема засвіченого вузла", size=13, bold=True, color=NEG))

    # 4 вузли в лінію: A <- B    C -> D
    nodes = [(475, "A"), (565, "B"), (685, "C"), (775, "D")]
    for nx, nlab in nodes:
        col = FIELD if nlab in ("B", "C") else INK
        f.append(circle(nx, 185, 18, fill="#ffffff", stroke=col, sw=1.6))
        f.append(text(nx, 189, nlab, size=11, bold=True, color=col))

    # Передача B -> A
    f.append(arrow(545, 185, 498, 185, color=POS, sw=2))
    f.append(text(522, 172, "B → A", size=10, bold=True, color=POS))

    # Бажана передача C -> D
    f.append(line(705, 185, 752, 185, color=FIELD, sw=2, dash="3 3"))
    f.append(arrow(745, 185, 754, 185, color=FIELD, sw=2))
    f.append(text(730, 172, "C → D", size=10, bold=True, color=FIELD))

    # C чує B
    f.append(line(585, 185, 665, 185, color=MUTED, sw=1.2, dash="2 2"))
    f.append(text(625, 172, "чує B", size=9, italic=True, color=MUTED))

    f.append(rect(540, 275, 170, 46, fill="#fff7e6", stroke="#d97706", sw=1.4))
    f.append(text(625, 293, "Хибне мовчання вузла C", size=11, bold=True, color="#d97706"))
    f.append(text(625, 310, "Передача C → D не шкодить A!", size=10, color="#d97706"))

    f.append(text(625, 345, "C чує мовлення B і блокує відправку,", size=11, color=INK))
    f.append(text(625, 365, "даремно втрачаючи ємність каналу.", size=11, bold=True, color=INK))

    f.append(text(W / 2, 412, "Приховані вузли руйнують кадри колізіями; засвічені вузли блокують паралельні незалежні передачі.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "hidden-exposed-nodes.svg"), W, H, *f)


# ── 5. Рукостискання RTS/CTS та віртуальний вектор NAV ────────────────────
def fig_rts_cts_nav():
    """Діаграма 4-way handshake: RTS, CTS, DATA, ACK із таймерами NAV для сусідів."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Механізм RTS/CTS та захист ефіру через вектор виділення мережі (NAV)", size=16, bold=True)]

    # 4 лінії часу: Відправник (A), Приймач (B), Сусід A (засвічений), Сусід B (прихований)
    tracks = [
        (80, "Відправник A"),
        (155, "Приймач B"),
        (230, "Сусід A (чує RTS)"),
        (305, "Сусід B (чує CTS)")
    ]
    for ty, tname in tracks:
        f.append(text(125, ty + 14, tname, size=11, bold=True, color=INK, anchor="end"))
        f.append(line(135, ty + 10, 810, ty + 10, color=LINE, sw=1.5))

    # Послідовність кадрів
    # 1. RTS від A до B
    f.append(rect(145, 70, 70, 30, fill="#eef3ff", stroke=NEG, sw=1.6))
    f.append(text(180, 89, "RTS", size=11, bold=True, color=NEG))
    f.append(arrow(180, 100, 180, 150, color=NEG, sw=1.5))

    # SIFS
    f.append(rect(215, 145, 25, 20, fill="#f4f6f8", stroke=MUTED, sw=1))
    f.append(text(227, 159, "SIFS", size=9, color=MUTED))

    # 2. CTS від B до A
    f.append(rect(240, 145, 70, 30, fill="#fff7e6", stroke=POS, sw=1.6))
    f.append(text(275, 164, "CTS", size=11, bold=True, color=POS))
    f.append(arrow(275, 145, 275, 95, color=POS, sw=1.5))

    # SIFS
    f.append(rect(310, 70, 25, 20, fill="#f4f6f8", stroke=MUTED, sw=1))
    f.append(text(322, 84, "SIFS", size=9, color=MUTED))

    # 3. DATA від A до B
    f.append(rect(335, 65, 280, 40, fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(text(475, 89, "DATA (Кадр даних)", size=12, bold=True, color=FIELD))
    f.append(arrow(475, 105, 475, 145, color=FIELD, sw=1.5))

    # SIFS
    f.append(rect(615, 145, 25, 20, fill="#f4f6f8", stroke=MUTED, sw=1))
    f.append(text(627, 159, "SIFS", size=9, color=MUTED))

    # 4. ACK від B до A
    f.append(rect(640, 145, 60, 30, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(670, 164, "ACK", size=11, bold=True, color=FIELD))
    f.append(arrow(670, 145, 670, 95, color=FIELD, sw=1.5))

    # Вектори NAV
    # NAV для сусіда A (починається з кінця RTS, триває до кінця ACK)
    f.append(rect(215, 225, 485, 20, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text(457, 239, "NAV (встановлено за полем Duration у RTS: CTS + DATA + ACK + 3×SIFS)", size=10, bold=True, color=POS))

    # NAV для сусіда B (починається з кінця CTS, триває до кінця ACK)
    f.append(rect(310, 300, 390, 20, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text(505, 314, "NAV (встановлено за полем Duration у CTS: DATA + ACK + 2×SIFS)", size=10, bold=True, color=POS))

    f.append(text(W / 2, 385, "Кадр CTS резервує ефір навколо приймача, примушуючи мовчати навіть ті вузли, які не чули RTS.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "rts-cts-nav.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cd_vs_ca()
    fig_interframe_spaces()
    fig_backoff_timeline()
    fig_hidden_exposed()
    fig_rts_cts_nav()
    print("All figures generated successfully.")
