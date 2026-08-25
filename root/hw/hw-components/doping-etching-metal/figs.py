# -*- coding: utf-8 -*-
"""Фігури до теми «Шар за шаром: легування, травлення, метал».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── локальна палітра шарів (узгоджена з INK/POS/NEG/FIELD svgkit) ────────────
SUB  = "#cdd9ec"   # кремнієва підкладка
OXID = "#cfe0a8"   # оксид SiO₂ (зеленавий — як FIELD-родина)
POLY = "#c9c9c9"   # полікремній затвора
NPLUS = "#f3c0bb"  # n⁺-області (рожеві — гаряча домішка)
METAL = "#e0a020"  # метал (мідь)
METED = "#a06000"  # обведення металу
TUNG = "#8a8a8a"   # вольфрам/via
DIEL = "#e7eef8"   # міжшаровий діелектрик


def srect(x, y, w, h, fill, stroke=INK, sw=1.6):
    """Прямокутник із прямими кутами (rx=0) — для шарів у розрізі."""
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — buildup: як на пластині росте транзистор, крок за кроком
# ════════════════════════════════════════════════════════════════════════════
def fig_buildup():
    W, H = 760, 470
    s = [text(W / 2, 26, "Як на пластині росте транзистор (розріз)", size=17, bold=True)]

    # ── (1) Окислення ────────────────────────────────────────────────────
    s.append(text(50, 58, "1. Окислення: вирощують ізолятор", size=12, bold=True, anchor="start"))
    s.append(srect(50, 98, 200, 26, SUB))
    s.append(srect(50, 86, 200, 12, OXID, stroke="#7a9a3a", sw=1.4))
    s.append(text(258, 92, "оксид SiO₂", size=11, color="#5a7a1a", anchor="start"))

    # ── (2) Затвор ───────────────────────────────────────────────────────
    s.append(text(286, 58, "2. Затвор: оксид + полікремній", size=12, bold=True, anchor="start"))
    s.append(srect(286, 98, 200, 26, SUB))
    s.append(srect(286, 88, 200, 10, OXID, stroke="#7a9a3a", sw=1.4))
    s.append(srect(360, 68, 52, 20, POLY))
    s.append(text(386, 64, "затвор", size=10, bold=True))

    # ── (3) Легування ────────────────────────────────────────────────────
    s.append(text(50, 174, "3. Легування: іони у витік і стік", size=12, bold=True, anchor="start"))
    s.append(srect(50, 214, 200, 26, SUB))
    s.append(srect(50, 204, 200, 10, OXID, stroke="#7a9a3a", sw=1.4))
    s.append(srect(124, 184, 52, 20, POLY))
    for x in (80, 100, 200, 220):
        s.append(line(x, 178, x, 202, color=POS, sw=1.4))
        s.append('<polygon points="%.1f,202 %.1f,196 %.1f,196" fill="%s"/>' % (x, x - 3, x + 3, POS))
    s.append(srect(60, 214, 56, 18, NPLUS, stroke=POS, sw=1.4))
    s.append(srect(184, 214, 56, 18, NPLUS, stroke=POS, sw=1.4))
    s.append(text(88, 227, "n⁺", size=11, color=POS, bold=True))
    s.append(text(212, 227, "n⁺", size=11, color=POS, bold=True))

    # ── (4) Контакти ─────────────────────────────────────────────────────
    s.append(text(286, 174, "4. Контакти: вертикальні з'єднання", size=12, bold=True, anchor="start"))
    s.append(srect(286, 214, 200, 26, SUB))
    s.append(srect(286, 194, 200, 20, DIEL, stroke="#9fb0c8", sw=1.2))
    s.append(srect(296, 214, 56, 18, NPLUS, stroke=POS, sw=1.2))
    s.append(srect(420, 214, 56, 18, NPLUS, stroke=POS, sw=1.2))
    s.append(srect(364, 194, 44, 14, POLY, sw=1.2))
    for x in (315, 381, 447):
        s.append(srect(x, 194, 10, 20, TUNG, sw=1.2))
    s.append(text(494, 200, "вольфрамові", size=10, color=MUTED, anchor="start"))
    s.append(text(494, 213, "пробки (via)", size=10, color=MUTED, anchor="start"))

    # ── (5) Перший шар металу ────────────────────────────────────────────
    s.append(text(50, 290, "5. Метал: перший шар проводів", size=12, bold=True, anchor="start"))
    s.append(srect(50, 330, 200, 26, SUB))
    s.append(srect(50, 310, 200, 20, DIEL, stroke="#9fb0c8", sw=1.2))
    for x in (79, 145, 211):
        s.append(srect(x, 310, 10, 20, TUNG, sw=1.2))
    s.append(srect(66, 302, 60, 9, METAL, stroke=METED, sw=1.2))
    s.append(srect(154, 302, 80, 9, METAL, stroke=METED, sw=1.2))
    s.append(text(258, 308, "метал 1 (Cu)", size=10, color=METED, anchor="start"))

    # ── (6) Стек з'єднань ────────────────────────────────────────────────
    s.append(text(286, 290, "6. Стек з'єднань: 10+ шарів металу", size=12, bold=True, anchor="start"))
    s.append(srect(286, 330, 200, 26, SUB))
    s.append(srect(286, 306, 200, 24, DIEL, stroke="#9fb0c8", sw=1.0))
    for row_y in (278, 286, 294, 302):
        for bx, bw in ((306, 50), (376, 40), (436, 36)):
            s.append(srect(bx, row_y, bw, 6, METAL, stroke=METED, sw=0.8))
    for x in (336, 406, 456):
        s.append('<line x1="%.1f" y1="278" x2="%.1f" y2="306" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (x, x, TUNG))
    s.append(text(494, 292, "багато шарів", size=10, color=METED, anchor="start"))
    s.append(text(494, 305, "металу (10+)", size=10, color=METED, anchor="start"))

    render(os.path.join(IMG, "buildup.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — mosfet-full: готовий MOSFET у розрізі
# ════════════════════════════════════════════════════════════════════════════
def fig_mosfet_full():
    W, H = 720, 320
    s = [text(W / 2, 28, "Готовий MOSFET у розрізі: що збудували", size=17, bold=True)]

    s.append(srect(140, 110, 440, 150, SUB, sw=2))
    s.append(text(570, 248, "підкладка p-Si", size=12, color=NEG, anchor="end"))

    s.append(srect(170, 110, 90, 46, NPLUS, stroke=POS, sw=1.6))
    s.append(srect(460, 110, 90, 46, NPLUS, stroke=POS, sw=1.6))
    s.append(text(215, 138, "n⁺", size=14, color=POS, bold=True))
    s.append(text(505, 138, "n⁺", size=14, color=POS, bold=True))

    s.append(srect(260, 102, 200, 8, OXID, stroke="#5a7a1a", sw=1.4))
    s.append(srect(260, 76, 200, 26, POLY, sw=1.8))
    s.append(text(360, 93, "затвор (полікремній)", size=12, bold=True))
    s.append(rect(260, 110, 200, 12, fill="none", stroke=FIELD, sw=2, rx=0))
    s.append(text(360, 144, "канал (поле відкриває провідність)", size=11, color=FIELD))

    s.append('<line x1="215" y1="110" x2="215" y2="60" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % MUTED)
    s.append(text(215, 52, "Витік (S)", size=12, bold=True))
    s.append('<line x1="505" y1="110" x2="505" y2="60" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % MUTED)
    s.append(text(505, 52, "Стік (D)", size=12, bold=True))
    s.append(text(360, 66, "G", size=12))

    s.append(line(260, 106, 210, 128, color="#5a7a1a", sw=1.4))
    s.append('<polygon points="210,128 215,122 218,129" fill="#5a7a1a"/>')
    s.append(text(190, 144, "тонкий оксид", size=11, color="#5a7a1a"))

    s.append(text(W / 2, 296, "Будова «затвор–ізолятор–канал» — підсумок окремих кроків фабрикації:", size=12, color=MUTED, italic=True))
    s.append(text(W / 2, 314, "оксид виростили, затвор осадили, n⁺-області вживили, контакти пробили.", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "mosfet-full.svg"), W, H, *s)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — etch: дві дії над шаром (додати / прибрати)
# ════════════════════════════════════════════════════════════════════════════
def fig_etch():
    W, H = 720, 300
    s = [text(W / 2, 28, "Дві дії над шаром: додати або прибрати", size=17, bold=True)]

    # ліва половина — травлення
    s.append(text(220, 64, "Травлення — прибрати зайве", size=14, color=POS, bold=True))
    s.append(srect(70, 100, 300, 22, SUB))
    s.append(srect(70, 78, 300, 22, METAL, stroke=METED, sw=1.6))
    s.append(srect(100, 64, 60, 14, "#f6d6a8", stroke="#b8863a", sw=1.4))
    s.append(srect(240, 64, 80, 14, "#f6d6a8", stroke="#b8863a", sw=1.4))
    s.append(arrow(220, 132, 220, 156))
    s.append(srect(70, 190, 300, 22, SUB))
    s.append(srect(100, 168, 60, 22, METAL, stroke=METED, sw=1.6))
    s.append(srect(240, 168, 80, 22, METAL, stroke=METED, sw=1.6))
    s.append(text(220, 230, "лишилося лише під маскою", size=11, color=MUTED))

    # права половина — осадження/легування
    s.append(text(560, 64, "Осадження / легування — додати шар", size=14, color=FIELD, bold=True))
    s.append(srect(410, 100, 300, 22, SUB))
    s.append(arrow(560, 132, 560, 156))
    s.append(srect(410, 190, 300, 22, SUB))
    s.append(srect(410, 168, 300, 22, OXID, stroke="#5a7a1a", sw=1.6))
    s.append(text(560, 230, "новий суцільний шар згори", size=11, color=MUTED))

    s.append(text(W / 2, 286, "Чергуючи «додати — накрити маскою — прибрати зайве» десятки разів, нарощують увесь чіп.", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "etch.svg"), W, H, *s)


if __name__ == "__main__":
    fig_buildup()
    fig_mosfet_full()
    fig_etch()
    print("OK: buildup.svg, mosfet-full.svg, etch.svg -> ./img/")
