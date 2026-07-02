# -*- coding: utf-8 -*-
"""Фігури до теми «Синфазна і диференціальна завади» (аналогова електроніка).
  two-modes.svg     — та сама пара дротів у двох ладах: синфазний (обидва разом) і диференціальний (назустріч)
  coupling.svg      — три шляхи, якими завада сідає на пару: ємність до корпусу, магнітне поле, спільний опір землі
  why-common.svg    — поле б'є по обох дротах однаково → завада лягає у спільний лад, сигнал лишається в різниці
  conversion.svg    — асиметрія (різні опори до землі) перетворює частину синфазного на диференціальне → лазівка
  divider.svg       — [вставка math] поділ синфазної напруги між Z₁≠Z₂ дає різницю на входах приймача
  conv-db.svg       — [вставка math] коефіцієнт перетворення = відносний розбаланс, у дБ (−20 дБ/декада); точка 1%→−40 дБ
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def two_modes():
    """Дві панелі: синфазний лад (стрілки разом) і диференціальний (назустріч)."""
    W, H = 720, 340
    p = [text(W / 2, 26, "Два лади однієї пари дротів", size=17, bold=True)]

    def panel(x0, title, sub, arrows_same):
        out = [fitbox(x0, 56, 300, 28, title, size=15, bold=True,
                      fill="#eef2ff", stroke=NEG)]
        # два горизонтальні дроти
        wy1, wy2 = 150, 230
        out.append(line(x0 + 30, wy1, x0 + 270, wy1, color=POS, sw=3))
        out.append(line(x0 + 30, wy2, x0 + 270, wy2, color=NEG, sw=3))
        out.append(text(x0 + 18, wy1 + 5, "A", size=14, color=POS, bold=True, anchor="end"))
        out.append(text(x0 + 18, wy2 + 5, "B", size=14, color=NEG, bold=True, anchor="end"))
        # земля-опора
        gy = 285
        out.append(line(x0 + 30, gy, x0 + 270, gy, color=MUTED, sw=1.5, dash="4 4"))
        out.append(text(x0 + 150, gy + 18, "спільна земля (опора)", size=11, color=MUTED))
        # вертикальні стрілки руху напруги відносно землі
        cx = x0 + 150
        if arrows_same:
            # обидва вгору
            out.append(arrow(cx - 60, wy1 + 22, cx - 60, wy1 - 22, color=POS, sw=2.4))
            out.append(arrow(cx + 60, wy2 + 22, cx + 60, wy2 - 22, color=NEG, sw=2.4))
        else:
            # назустріч: A вгору, B вниз
            out.append(arrow(cx - 60, wy1 + 22, cx - 60, wy1 - 22, color=POS, sw=2.4))
            out.append(arrow(cx + 60, wy2 - 22, cx + 60, wy2 + 22, color=NEG, sw=2.4))
        out.append(fitbox(x0 + 30, 300, 240, 26, sub, size=11, fill=BG, stroke=MUTED))
        return "".join(out)

    p.append(panel(20, "СИНФАЗНИЙ лад",
                   "обидва дроти йдуть в один бік разом", True))
    p.append(panel(400, "ДИФЕРЕНЦІАЛЬНИЙ лад",
                   "дроти йдуть назустріч — різниця росте", False))
    p.append(line(370, 56, 370, 326, color="#d0d4da", sw=1))
    render(os.path.join(OUT, "two-modes.svg"), W, H, *p)


def coupling():
    """Три шляхи завади на пару дротів: ємність до корпусу, магнітне поле, спільний опір землі."""
    W, H = 740, 360
    p = [text(W / 2, 26, "Звідки береться синфазна завада: три шляхи", size=17, bold=True)]

    # пара сигнальних дротів посередині
    wy1, wy2 = 175, 215
    p.append(line(150, wy1, 590, wy1, color=POS, sw=3))
    p.append(line(150, wy2, 590, wy2, color=NEG, sw=3))
    p.append(text(605, wy1 + 5, "A", size=13, color=POS, bold=True))
    p.append(text(605, wy2 + 5, "B", size=13, color=NEG, bold=True))

    # 1) ЄМНІСТЬ до корпусу (зверху)
    p.append(line(150, 70, 590, 70, color=MUTED, sw=2))
    p.append(text(155, 62, "шумний вузол / корпус", size=11, color=MUTED, anchor="start"))
    for cx in (240, 330):
        p.append(line(cx, 70, cx, wy1, color=FIELD, sw=1.6, dash="3 4"))
        p.append(text(cx + 6, 120, "C", size=11, color=FIELD, italic=True, anchor="start"))
    p.append(fitbox(20, 55, 124, 40, "1. ЄМНІСТЬ\n(електр. поле)", size=11, bold=True,
                    fill="#eafaf1", stroke=FIELD))

    # 2) МАГНІТНЕ поле (петля поряд)
    p.append(circle(420, 120, 26, fill=BG, stroke=FIELD, sw=2))
    p.append(text(420, 125, "I~", size=13, color=FIELD, bold=True))
    p.append(arrow(455, 120, 500, 150, color=FIELD, sw=1.8))
    p.append(fitbox(360, 70, 150, 24, "змінний струм поряд", size=11, fill=BG, stroke=MUTED))
    p.append(fitbox(600, 95, 130, 40, "2. МАГНІТНЕ ПОЛЕ\nнаводить ЕРС у петлю", size=10.5,
                    bold=True, fill="#eafaf1", stroke=FIELD))

    # 3) СПІЛЬНИЙ ОПІР землі (знизу)
    gy = 300
    p.append(line(150, gy, 590, gy, color=MUTED, sw=2))
    # спільний шматок землі з опором
    p.append(fitbox(330, gy - 13, 80, 26, "Rземлі", size=11, bold=True, fill="#fef3f2", stroke=POS))
    p.append(arrow(200, gy, 320, gy, color=POS, sw=2))
    p.append(arrow(540, gy, 420, gy, color=POS, sw=2))
    p.append(text(255, gy + 20, "струми інших вузлів", size=11, color=POS))
    # зв'язок землі з опорою пари
    p.append(line(370, wy2, 370, gy - 13, color=MUTED, sw=1.4, dash="3 3"))
    p.append(fitbox(8, 285, 136, 40, "3. СПІЛЬНИЙ ОПІР\nземлі гойдає опору", size=10.5,
                    bold=True, fill="#fef3f2", stroke=POS))

    p.append(fitbox(150, 250, 440, 26,
                    "усі три б'ють по А і В майже однаково → завада лягає у СПІЛЬНИЙ лад",
                    size=11.5, bold=True, fill="#eef2ff", stroke=NEG))
    render(os.path.join(OUT, "coupling.svg"), W, H, *p)


def why_common():
    """Однакова наводка на обидва дроти лягає у спільне; різниця її не бачить."""
    W, H = 720, 320
    p = [text(W / 2, 26, "Чому завада потрапляє саме в спільний лад", size=17, bold=True)]

    # зліва: дроти + однакова наводка δ
    x0 = 60
    wy1, wy2 = 130, 200
    p.append(line(x0, wy1, x0 + 240, wy1, color=POS, sw=3))
    p.append(line(x0, wy2, x0 + 240, wy2, color=NEG, sw=3))
    p.append(text(x0 - 12, wy1 + 5, "A", size=13, color=POS, bold=True, anchor="end"))
    p.append(text(x0 - 12, wy2 + 5, "B", size=13, color=NEG, bold=True, anchor="end"))
    # однакові стрілки δ вгору на обидва
    for yy in (wy1, wy2):
        p.append(arrow(x0 + 120, yy + 26, x0 + 120, yy + 4, color=FIELD, sw=2.2))
    p.append(text(x0 + 120, wy2 + 48, "однакове +δ на обидва", size=11, color=FIELD))
    p.append(fitbox(x0, 70, 240, 26, "зовнішнє поле б'є по А і В рівно", size=11.5,
                    bold=True, fill="#eafaf1", stroke=FIELD))

    # стрілка-перехід
    p.append(arrow(330, 165, 400, 165, color=INK, sw=2.4))

    # справа: розклад
    bx = 430
    p.append(fitbox(bx, 95, 250, 60,
                    "СПІЛЬНЕ (середнє):\n(A+B)/2  росте на +δ", size=12.5, bold=True,
                    fill="#eef2ff", stroke=NEG))
    p.append(fitbox(bx, 175, 250, 60,
                    "РІЗНИЦЯ:\nA − B  не змінилась (δ−δ=0)", size=12.5, bold=True,
                    fill=BG, stroke=INK))
    p.append(text(bx + 125, 270, "сигнал у різниці — цілий; завада — у спільному",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "why-common.svg"), W, H, *p)


def conversion():
    """Асиметрія опорів до землі перетворює частину синфазного на диференціальне."""
    W, H = 740, 340
    p = [text(W / 2, 26, "Лазівка: асиметрія перетворює спільне на різницю", size=17, bold=True)]

    # джерело синфазної завади Vс зліва
    p.append(fitbox(30, 140, 110, 50, "синфазна\nзавада Vс", size=12, bold=True,
                    fill="#eafaf1", stroke=FIELD))
    # два дроти з різними опорами до землі (приймача)
    wy1, wy2 = 120, 230
    p.append(line(140, wy1, 470, wy1, color=POS, sw=3))
    p.append(line(140, wy2, 470, wy2, color=NEG, sw=3))
    # опори до землі — РІЗНІ
    p.append(fitbox(300, wy1 - 16, 70, 32, "Z₁", size=13, bold=True, fill="#fef3f2", stroke=POS))
    p.append(line(335, wy1 + 16, 335, 290, color=POS, sw=1.6))
    p.append(fitbox(300, wy2 - 16, 70, 32, "Z₂ ≠ Z₁", size=12, bold=True, fill="#eaf0fd", stroke=NEG))
    p.append(line(335, wy2 + 16, 335, 290, color=NEG, sw=1.6))
    p.append(line(140, 290, 470, 290, color=MUTED, sw=2))
    p.append(text(305, 308, "земля приймача", size=11, color=MUTED, anchor="end"))

    # приймач справа бачить різницю
    p.append(arrow(470, 175, 530, 175, color=INK, sw=2.2))
    p.append(fitbox(540, 145, 175, 60,
                    "приймач бачить\nфальшиву РІЗНИЦЮ", size=12.5, bold=True,
                    fill="#fef3f2", stroke=POS))

    p.append(fitbox(120, 70, 500, 30,
                    "рівні Z до землі → завада однакова → різниця нуль (усе гаразд)",
                    size=11.5, fill=BG, stroke=MUTED))
    p.append(fitbox(120, 305, 500, 28,
                    "РІЗНІ Z → завада сідає нерівно → у різниці з'являється бруд",
                    size=11.5, bold=True, fill="#fef3f2", stroke=POS))
    render(os.path.join(OUT, "conversion.svg"), W, H, *p)


def choke_bifilar():
    """Біфілярне намотування: диференціальний струм гасить потік, синфазний — складає."""
    W, H = 740, 360
    p = [text(W / 2, 26, "Синфазний дросель: один сердечник, дві обмотки", size=17, bold=True)]

    def panel(x0, title, dirs, flux_word, flux_color, box_fill, box_stroke):
        # dirs = (a_dir, b_dir): +1 струм праворуч, -1 ліворуч
        out = [fitbox(x0, 52, 300, 26, title, size=14, bold=True,
                      fill=box_fill, stroke=box_stroke)]
        # тороїд-осердя — два горизонтальні «вуса» з кільцем посередині
        cy = 170
        out.append(circle(x0 + 150, cy, 46, fill="#f0ece4", stroke=MUTED, sw=10))
        out.append(text(x0 + 150, cy + 5, "осердя", size=11, color=MUTED))
        # два дроти, що входять у кільце з боків
        wy1, wy2 = cy - 70, cy + 70
        for wy, col, lab in ((wy1, POS, "A"), (wy2, NEG, "B")):
            out.append(line(x0 + 18, wy, x0 + 104, wy, color=col, sw=3))
            out.append(line(x0 + 196, wy, x0 + 282, wy, color=col, sw=3))
            # виток через осердя
            out.append(line(x0 + 104, wy, x0 + 150, cy - (46 if wy < cy else -46),
                            color=col, sw=2.4))
            out.append(line(x0 + 150, cy - (46 if wy < cy else -46), x0 + 196, wy,
                            color=col, sw=2.4))
            out.append(text(x0 + 10, wy + 5, lab, size=13, color=col, bold=True, anchor="end"))
        # стрілки напряму струму
        ax = x0 + 250
        for wy, d, col in ((wy1, dirs[0], POS), (wy2, dirs[1], NEG)):
            if d > 0:
                out.append(arrow(ax, wy, ax + 24, wy, color=col, sw=2.2))
            else:
                out.append(arrow(ax + 24, wy, ax, wy, color=col, sw=2.2))
        # підсумок потоку всередині осердя
        out.append(fitbox(x0 + 12, 282, 276, 56, flux_word, size=11, bold=True,
                          fill=box_fill, stroke=flux_color))
        return "".join(out)

    p.append(panel(20, "Корисний (диференціальний) струм",
                   (+1, -1),
                   "в осерді струми НАЗУСТРІЧ\nпотоки гасяться → мала L\nсигнал ПРОХОДИТЬ",
                   FIELD, "#eafaf1", FIELD))
    p.append(panel(400, "Синфазна завада",
                   (+1, +1),
                   "в осерді струми РАЗОМ\nпотоки складаються → велика L\nзавада ДУШИТЬСЯ",
                   POS, "#fef3f2", POS))
    p.append(line(370, 52, 370, 340, color="#d0d4da", sw=1))
    render(os.path.join(OUT, "choke-bifilar.svg"), W, H, *p)


def choke_inline():
    """Типове ввімкнення синфазного дроселя в лінію (живлення/дані) між джерелом і навантаженням."""
    W, H = 740, 280
    p = [text(W / 2, 26, "Як дросель вмикають у лінію", size=17, bold=True)]

    # джерело зліва, навантаження справа, дросель посередині (обидва дроти крізь нього)
    p.append(fitbox(24, 95, 110, 70, "джерело\n(порт / шина)", size=12, bold=True,
                    fill=BG, stroke=MUTED))
    p.append(fitbox(606, 95, 110, 70, "приймач\n/ навантаження", size=12, bold=True,
                    fill=BG, stroke=MUTED))

    wy1, wy2 = 110, 150
    # дроти до дроселя
    p.append(line(134, wy1, 300, wy1, color=POS, sw=3))
    p.append(line(134, wy2, 300, wy2, color=NEG, sw=3))
    # дросель — рамка з двома обмотками на спільному осерді
    p.append(rect(300, 88, 140, 84, fill="#f0ece4", stroke=MUTED, sw=2))
    p.append(text(370, 82, "синфазний дросель", size=11, color=MUTED))
    for yy, col in ((wy1, POS), (wy2, NEG)):
        # три «горбики» обмотки
        for k in range(3):
            cxk = 318 + k * 35
            p.append(line(cxk, yy, cxk + 17, yy - 14, color=col, sw=2.4))
            p.append(line(cxk + 17, yy - 14, cxk + 34, yy, color=col, sw=2.4))
    # центральна риска осердя між обмотками
    p.append(line(303, 130, 437, 130, color=MUTED, sw=1.4, dash="3 3"))
    # дроти після дроселя
    p.append(line(440, wy1, 606, wy1, color=POS, sw=3))
    p.append(line(440, wy2, 606, wy2, color=NEG, sw=3))

    # пояснення під лінією
    p.append(fitbox(150, 205, 440, 28,
                    "обидва дроти пари йдуть крізь ОДНЕ осердя — у РОЗРІЗ лінії, не на землю",
                    size=11.5, bold=True, fill="#eef2ff", stroke=NEG))
    render(os.path.join(OUT, "choke-inline.svg"), W, H, *p)


def choke_window():
    """Імпеданс синфазного й диференціального ладу від частоти: вікно прозорості й де воно ламається."""
    W, H = 720, 380
    p = [text(W / 2, 26, "Дві криві опору: що дросель пропускає, а що душить", size=16, bold=True)]

    # осі (лог-лог схематично)
    ox, oy = 90, 300
    p.append(line(ox, oy, ox + 560, oy, color=INK, sw=2))      # вісь X — частота
    p.append(line(ox, oy, ox, 70, color=INK, sw=2))            # вісь Y — опір
    p.append(text(ox + 560, oy + 24, "частота →", size=12, color=INK, anchor="end"))
    p.append(text(ox - 8, 78, "опір", size=12, color=INK, anchor="end"))

    # крива СИНФАЗНОГО опору: росте з частотою (ωL), потім завал на самрезонансі
    cm = ["%d,%d" % (ox + 10, oy - 6)]
    pts = [(40, 30), (120, 80), (220, 150), (320, 200), (400, 215),
           (470, 195), (540, 150)]  # підйом і завал після піка
    for dx, dy in pts:
        cm.append("%d,%d" % (ox + dx, oy - dy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(cm), POS))
    p.append(text(ox + 300, oy - 232, "СИНФАЗНИЙ опір (ωL): велика перепона", size=12,
                  color=POS, bold=True))

    # крива ДИФЕРЕНЦІАЛЬНОГО опору: майже нуль, повзе вгору лише на високих (leakage)
    dm = ["%d,%d" % (ox + 10, oy - 4)]
    for dx, dy in [(120, 6), (240, 12), (340, 22), (430, 45), (510, 90), (560, 130)]:
        dm.append("%d,%d" % (ox + dx, oy - dy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(dm), FIELD))
    p.append(text(ox + 200, oy - 30, "ДИФЕРЕНЦІАЛЬНИЙ опір (leakage): майже нуль",
                  size=12, color=FIELD, bold=True))

    # вікно прозорості — підсвічена смуга зліва
    p.append('<rect x="%d" y="70" width="190" height="230" fill="#eafaf1" '
             'opacity="0.5"/>' % (ox + 5))
    p.append(text(ox + 100, 90, "ВІКНО", size=12, color=FIELD, bold=True))
    p.append(text(ox + 100, 106, "прозорості", size=11, color=FIELD))

    # межі справа: де дросель перестає бути «прозорим»
    p.append(line(ox + 430, 70, ox + 430, oy, color=MUTED, sw=1.4, dash="4 4"))
    p.append(fitbox(ox + 360, 40, 200, 26, "тут сигнал теж глушиться", size=10.5,
                    bold=True, fill="#fef3f2", stroke=POS))
    render(os.path.join(OUT, "choke-window.svg"), W, H, *p)


def divider():
    """[math] Поділ синфазної напруги між Z₁ і Z₂ до входу приймача → різниця на входах."""
    W, H = 740, 360
    p = [text(W / 2, 26, "Поділ синфазної напруги між двома опорами", size=17, bold=True)]

    # синфазне джерело Vс зліва — спільне для обох дротів
    p.append(fitbox(24, 150, 96, 56, "синфазна\nVс", size=12.5, bold=True,
                    fill="#eafaf1", stroke=FIELD))
    # вузол розгалуження
    nx = 150
    p.append(line(120, 178, nx, 178, color=INK, sw=2.4))
    p.append(circle(nx, 178, 4, fill=INK, stroke=INK, sw=1))
    p.append(line(nx, 110, nx, 246, color=INK, sw=2))   # шина від джерела до обох опорів

    # дріт A — опір Z₁ до входу
    wyA, wyB = 110, 246
    p.append(fitbox(nx + 70, wyA - 18, 96, 36, "Z₁", size=14, bold=True,
                    fill="#fef3f2", stroke=POS))
    p.append(line(nx, wyA, nx + 70, wyA, color=POS, sw=2.4))
    p.append(line(nx + 166, wyA, 470, wyA, color=POS, sw=3))
    p.append(text(nx + 30, wyA - 12, "струм A", size=10.5, color=POS))
    # дріт B — опір Z₂ до входу
    p.append(fitbox(nx + 70, wyB - 18, 96, 36, "Z₂", size=14, bold=True,
                    fill="#eaf0fd", stroke=NEG))
    p.append(line(nx, wyB, nx + 70, wyB, color=NEG, sw=2.4))
    p.append(line(nx + 166, wyB, 470, wyB, color=NEG, sw=3))
    p.append(text(nx + 30, wyB + 18, "струм B", size=10.5, color=NEG))

    # входи приймача (Zвх однаковий) праворуч
    p.append(text(478, wyA + 5, "V_A", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(478, wyB + 5, "V_B", size=13, color=NEG, bold=True, anchor="start"))
    p.append(fitbox(540, 150, 170, 56, "приймач:\nVдиф = V_A − V_B", size=12.5, bold=True,
                    fill=BG, stroke=INK))
    p.append(arrow(470, 178, 532, 178, color=INK, sw=2.2))

    # дві умови — внизу
    p.append(fitbox(120, 290, 250, 30, "Z₁ = Z₂  →  Vдиф = 0", size=12.5,
                    bold=True, fill=BG, stroke=MUTED))
    p.append(fitbox(390, 290, 320, 30, "Z₁ ≠ Z₂  →  Vдиф ≈ Vс·ΔZ/Z  (бруд!)",
                    size=12, bold=True, fill="#fef3f2", stroke=POS))
    render(os.path.join(OUT, "divider.svg"), W, H, *p)


def conv_db():
    """[math] Коефіцієнт перетворення = відносний розбаланс, у дБ: пряма −20 дБ/декада, точка 1%→−40 дБ."""
    import math
    W, H = 720, 380
    p = [text(W / 2, 26, "Коефіцієнт перетворення = відносний розбаланс (у дБ)", size=16, bold=True)]

    ox, oy = 96, 300          # початок осей
    plot_w, plot_h = 520, 220  # поле графіка
    # вісь X: log10(розбаланс) від 0.001 (0.1%) до 0.1 (10%) → 3 декади
    x_lo, x_hi = -3.0, -1.0   # log10
    # вісь Y: дБ від -60 до -20
    y_lo, y_hi = -60.0, -20.0

    def X(log_rel):
        return ox + (log_rel - x_lo) / (x_hi - x_lo) * plot_w

    def Y(db):
        return oy - (db - y_lo) / (y_hi - y_lo) * plot_h

    # осі
    p.append(line(ox, oy, ox + plot_w, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - plot_h, color=INK, sw=2))

    # сітка й підписи X (декади розбалансу)
    for lr, lab in [(-3, "0.1%"), (-2, "1%"), (-1, "10%")]:
        xx = X(lr)
        p.append(line(xx, oy, xx, oy - plot_h, color="#e3e6ea", sw=1))
        p.append(text(xx, oy + 22, lab, size=12, color=INK))
    p.append(text(ox + plot_w / 2, oy + 44, "відносний розбаланс ΔZ/Z →", size=12, color=INK))

    # сітка й підписи Y (дБ)
    for db in (-20, -30, -40, -50, -60):
        yy = Y(db)
        p.append(line(ox, yy, ox + plot_w, yy, color="#e3e6ea", sw=1))
        p.append(text(ox - 10, yy + 5, "%d" % db, size=11, color=INK, anchor="end"))
    p.append(text(ox - 64, oy - plot_h / 2, "коеф., дБ", size=12, color=INK))

    # пряма: коеф_дБ = 20·log10(розбаланс) — рівно діагональ -20 дБ/декада
    line_pts = []
    for lr in (x_lo, x_hi):
        db = 20.0 * lr   # 20*log10(10^lr) = 20*lr
        line_pts.append("%.1f,%.1f" % (X(lr), Y(db)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(line_pts), NEG))
    p.append(text(X(-2.55), Y(-44) - 10, "−20 дБ на декаду", size=12, color=NEG,
                  bold=True, anchor="start"))

    # робоча точка прикладу: 1% → -40 дБ
    px, py = X(-2.0), Y(-40.0)
    p.append(circle(px, py, 6, fill=POS, stroke=POS, sw=1))
    p.append(fitbox(px + 12, py - 16, 168, 30, "приклад: 1% → −40 дБ", size=11.5,
                    bold=True, fill="#fef3f2", stroke=POS))

    # права шкала-нагадування: те саме як LCL балансу (дзеркало знака)
    p.append(fitbox(ox + plot_w - 196, oy - plot_h - 6, 196, 26,
                    "LCL = −коеф: вище = краща лінія", size=10.5, bold=True,
                    fill="#eef2ff", stroke=NEG))
    render(os.path.join(OUT, "conv-db.svg"), W, H, *p)


if __name__ == "__main__":
    two_modes()
    coupling()
    why_common()
    conversion()
    choke_bifilar()
    choke_inline()
    choke_window()
    divider()
    conv_db()
    print("OK: 9 SVG ->", OUT)
