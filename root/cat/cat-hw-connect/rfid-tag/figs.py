# -*- coding: utf-8 -*-
"""Фігури об'єкта «RFID-брелок (13.56 МГц)» (catalog/connect/rfid).
Запуск: python figs.py → ./img/*.svg. svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: як працює пасивна мітка ────────────────────────────────────────
# Зчитувач жене магнітне поле 13.56 МГц у свою котушку; котушка брелка ловить
# його, годується енергією й відповідає, змінюючи власне навантаження
# (load modulation). Дротів між ними нема.
def fig_principle():
    W, H = 760, 380
    parts = []

    # зчитувач зліва
    parts.append(fitbox(40, 150, 150, 90, "Зчитувач\n(RC522 тощо)\nживить поле",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.8, color=INK, bold=True))
    # котушка зчитувача — вертикальні витки
    rcx = 210
    for i in range(3):
        parts.append(circle(rcx, 150, 34 - i * 9, fill="none", stroke=NEG, sw=2.0))
    parts.append(text(rcx, 232, "котушка", 11, NEG, "middle"))
    parts.append(text(rcx, 248, "зчитувача", 11, NEG, "middle"))

    # магнітне поле — дуги між котушками
    for dy, r in ((0, 0), (-52, 1), (52, 1)):
        cy = 150 + dy
        parts.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" '
                     'stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
                     % (rcx + 20, cy, 380, cy - 26 * (1 if dy <= 0 else -1),
                        550, cy, POS))
    parts.append(text(380, 118, "магнітне поле 13.56 МГц", 12, POS, "middle", bold=True))

    # котушка брелка
    tcx = 560
    for i in range(3):
        parts.append(circle(tcx, 150, 34 - i * 9, fill="none", stroke=FIELD, sw=2.0))
    parts.append(text(tcx, 232, "котушка", 11, FIELD, "middle"))
    parts.append(text(tcx, 248, "брелка", 11, FIELD, "middle"))

    # чип брелка справа
    parts.append(fitbox(620, 130, 110, 60, "чип:\nживиться\nз поля",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))
    parts.append(line(tcx + 20, 150, 620, 150, color=FIELD, sw=1.8))

    # відповідь назад — load modulation
    parts.append(arrow(545, 300, 235, 300, color="#8e44ad", sw=2.0))
    parts.append(text(390, 322, "відповідь: брелок «підсаджує» поле "
                                 "(load modulation)", 12, "#8e44ad", "middle", bold=True))

    parts.append(text(390, 352, "жодного дроту й батарейки в брелку — "
                                 "лише котушка й чип", 11, MUTED, "middle"))

    render(os.path.join(IMG, "principle.svg"), W, H, *parts,
           title="Як працює пасивна мітка: поле годує брелок, брелок відповідає полем")


# ── Фігура 2: що всередині брелка ────────────────────────────────────────────
# Уся «плата» = котушка-антена (кілька витків по краю) + резонансний конденсатор
# + крихітний чип (аналоговий фронт + логіка + EEPROM). Ніяких контактів назовні.
def fig_inside():
    W, H = 700, 420
    parts = []

    # корпус брелка — овал/скруглений прямокутник
    parts.append(rect(60, 60, 580, 300, fill="#fbfcfd", stroke=MUTED, sw=1.6, rx=28))
    parts.append(text(350, 46, "усередині брелка (одна котушка + чип, "
                               "без контактів)", 12, MUTED, "middle"))

    # антена-котушка — концентричні скруглені рамки по периметру
    for i in range(4):
        m = 24 + i * 12
        parts.append(rect(100 + m, 100 + m, 500 - 2 * m, 220 - 2 * m,
                          fill="none", stroke=FIELD, sw=2.0, rx=20))
    parts.append(text(350, 96, "антена — котушка на кілька витків", 12, FIELD,
                     "middle", bold=True))

    # конденсатор резонансу — символ біля котушки зліва
    capx, capy = 176, 300
    parts.append(line(capx, capy - 22, capx, capy - 8, color=NEG, sw=2.0))
    parts.append(line(capx - 13, capy - 8, capx + 13, capy - 8, color=NEG, sw=2.8))
    parts.append(line(capx - 13, capy, capx + 13, capy, color=NEG, sw=2.8))
    parts.append(line(capx, capy, capx, capy + 14, color=NEG, sw=2.0))
    parts.append(fitbox(capx - 84, capy + 18, 168, 40,
                        "конденсатор:\nналаштовує на 13.56 МГц",
                        size=10, fill="#eaf0fd", stroke=NEG, sw=1.2, color=INK))

    # чип у центрі
    parts.append(fitbox(300, 175, 150, 80, "чип\nфронт + логіка\n+ EEPROM (памʼять)",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.8, color=INK, bold=True))
    # два дроти від чипа до котушки
    parts.append(line(300, 200, 148, 200, color=INK, sw=1.6))
    parts.append(line(450, 200, 556, 200, color=INK, sw=1.6))

    render(os.path.join(IMG, "inside.svg"), W, H, *parts,
           title="Що всередині брелка: антена-котушка, конденсатор і крихітний чип")


# ── Фігура 3: карта памʼяті MIFARE Classic 1K ────────────────────────────────
# 1 КБ = 16 секторів по 4 блоки по 16 байт. Останній блок кожного сектора —
# трейлер: ключі A/B і біти доступу. Блок 0 сектора 0 — UID, лише читання.
def fig_memory():
    W, H = 760, 470
    parts = []
    parts.append(text(380, 44, "16 секторів · 4 блоки по 16 байт = 1024 байти",
                     12, MUTED, "middle"))

    # намалюємо кілька секторів як стовпчики блоків
    x0, y0 = 70, 70
    bw, bh, gap = 150, 34, 10
    sec_gap = 26

    def sector(x, title, blocks, tint):
        out = [text(x + bw / 2, y0 - 10, title, 11, INK, "middle", bold=True)]
        for i, (lbl, col, fill) in enumerate(blocks):
            y = y0 + i * (bh + 4)
            out.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.6, rx=5))
            out.append(text(x + bw / 2, y + bh / 2 + 4, lbl, 10, INK, "middle"))
        return out

    trailer = ("трейлер: ключ A · біти · ключ B", INK, "#fdf0e0")
    data = ("дані (16 байт)", INK, "#eef2f7")

    # Сектор 0 — особливий: блок 0 = UID
    parts += sector(x0, "Сектор 0",
                    [("блок 0: UID виробника (RO)", POS, "#fdecea"),
                     data, data, trailer], POS)
    # Сектор 1
    parts += sector(x0 + bw + sec_gap, "Сектор 1",
                    [data, data, data, trailer], INK)
    # три крапки
    dotx = x0 + 2 * (bw + sec_gap) + 30
    parts.append(text(dotx, y0 + 2 * (bh + 4), "· · ·", 22, MUTED, "middle"))
    # Сектор 15
    parts += sector(x0 + 2 * (bw + sec_gap) + 60, "Сектор 15",
                    [data, data, data, trailer], INK)

    # пояснення знизу — рознесено, щоб не накладалось
    yb = y0 + 4 * (bh + 4) + 30
    parts.append(fitbox(70, yb, 300, 62,
                        "Блок 0 сектора 0 — UID, зашитий\nвиробником: лише читання,\n"
                        "унікальний серійний номер.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    parts.append(fitbox(400, yb, 300, 62,
                        "Останній блок кожного сектора —\nтрейлер: два ключі (A, B) і біти\n"
                        "доступу. Без ключа сектор не чути.",
                        size=11, fill="#fdf0e0", stroke="#d68910", sw=1.2, color=INK))

    render(os.path.join(IMG, "memory.svg"), W, H, *parts,
           title="Карта памʼяті MIFARE Classic 1K: сектори, блоки, ключі")


# ── Фігура 4 (math-coupling): резонансна крива контуру ────────────────────────
# Відгук LC-контуру на частоту: вузький гострий пік на f0=13.56 МГц. Що вища
# добротність Q, то вужчий пік і то вища напруга на резонансі. Показуємо дві
# криві (низька й висока Q) на спільній осі частот.
def fig_resonance():
    import math
    W, H = 760, 440
    parts = []

    # осі
    ox, oy = 110, 360          # початок координат (лівий-нижній)
    ax_w, ax_h = 560, 280      # довжина осей
    parts.append(arrow(ox, oy, ox + ax_w + 14, oy, color=INK, sw=1.8))   # X
    parts.append(arrow(ox, oy, ox, oy - ax_h - 14, color=INK, sw=1.8))   # Y
    parts.append(text(ox + ax_w + 4, oy + 22, "частота", 12, INK, "end"))
    parts.append(text(ox + ax_w + 44, oy + 22, "f →", 12, MUTED, "end"))
    # підпис осі Y — вертикально
    parts.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">'
                 'напруга на контурі</text>' % (ox - 42, oy - ax_h / 2, FONT, INK,
                                                ox - 42, oy - ax_h / 2))

    # позначка f0
    f0x = ox + ax_w * 0.5
    parts.append(line(f0x, oy, f0x, oy - ax_h - 4, color=MUTED, sw=1.2, dash="4 4"))
    parts.append(text(f0x, oy + 22, "13.56 МГц", 12, INK, "middle", bold=True))
    parts.append(text(f0x, oy + 38, "(f₀ — резонанс)", 11, MUTED, "middle"))

    # резонансні криві: амплітуда ~ 1/sqrt((1-(f/f0)^2)^2 + (1/Q)^2 (f/f0)^2)
    def curve(Q, peak_px, color, dash=None):
        pts = []
        for i in range(0, 561, 4):
            fr = 0.55 + (i / 560.0) * 0.9        # f/f0 від 0.55 до 1.45
            denom = math.sqrt((1 - fr * fr) ** 2 + (fr / Q) ** 2)
            amp = (1.0 / Q) / denom               # нормуємо так, щоб пік ≈ 1
            px = ox + i
            py = oy - amp * peak_px
            pts.append("%.1f %.1f" % (px, py))
        d = "M " + " L ".join(pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"%s/>'
                % (d, color, da))

    # висока Q — гострий високий пік
    parts.append(curve(Q=45, peak_px=250, color=POS))
    # низька Q — тупий низький пік
    parts.append(curve(Q=8, peak_px=250 * 8 / 45, color=NEG, dash="7 5"))

    # підписи кривих (рознесено, поза лініями)
    parts.append(fitbox(430, 70, 250, 46,
                        "висока Q — вузький, високий пік:\nбагатократний підйом напруги",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    parts.append(fitbox(430, 205, 250, 44,
                        "низька Q — тупий, низький пік:\nвідгук слабший",
                        size=11, fill="#eaf0fd", stroke=NEG, sw=1.2, color=INK))

    render(os.path.join(IMG, "resonance.svg"), W, H, *parts,
           title="Резонанс LC: пік на 13.56 МГц, гостроту задає добротність Q")


# ── Фігура 5 (math-coupling): спадання поля ближньої зони ─────────────────────
# H(r) на осі витка: майже плато при r≪a, різкий злам у 1/r³ при r≫a. Через це
# дальність — сантиметри. Лог-лог осі, щоб 1/r³ була прямою.
def fig_falloff():
    import math
    W, H = 760, 440
    parts = []
    ox, oy = 110, 360
    ax_w, ax_h = 560, 280
    parts.append(arrow(ox, oy, ox + ax_w + 14, oy, color=INK, sw=1.8))
    parts.append(arrow(ox, oy, ox, oy - ax_h - 14, color=INK, sw=1.8))
    parts.append(text(ox + ax_w + 8, oy + 22, "відстань r (лог)", 12, INK, "end"))
    parts.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">'
                 'сила поля H (лог)</text>' % (ox - 42, oy - ax_h / 2, FONT, INK,
                                              ox - 42, oy - ax_h / 2))

    # H(r) = a^2 / (2 (a^2+r^2)^{3/2}); a — радіус котушки. Осі логарифмічні.
    a = 0.02   # 2 см
    rmin, rmax = 0.004, 0.5
    import math as m
    lx0, lx1 = m.log10(rmin), m.log10(rmax)
    # значення H для нормування по вертикалі
    def Hval(r): return a * a / (2 * (a * a + r * r) ** 1.5)
    hy0, hy1 = m.log10(Hval(rmax)), m.log10(Hval(rmin))  # low, high

    def X(r): return ox + (m.log10(r) - lx0) / (lx1 - lx0) * ax_w
    def Y(h): return oy - (m.log10(h) - hy0) / (hy1 - hy0) * ax_h

    pts = []
    r = rmin
    while r <= rmax:
        pts.append("%.1f %.1f" % (X(r), Y(Hval(r))))
        r *= 1.06
    parts.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" L ".join(pts), FIELD))

    # позначка радіуса котушки a — там злам
    parts.append(line(X(a), oy, X(a), Y(Hval(a)), color=MUTED, sw=1.2, dash="4 4"))
    parts.append(text(X(a), oy + 22, "≈ розмір котушки", 11, MUTED, "middle"))

    # мітки відстаней на осі X
    for r, lbl in ((0.01, "1 см"), (0.05, "5 см"), (0.1, "10 см"), (0.3, "30 см")):
        parts.append(line(X(r), oy, X(r), oy + 5, color=INK, sw=1.4))
        parts.append(text(X(r), oy + 38, lbl, 10, INK, "middle"))

    # підпис нахилу 1/r^3 у дальній зоні (пряма на лог-лог)
    parts.append(fitbox(430, 250, 250, 56,
                        "далеко (r ≫ котушки):\nпряма з нахилом −3 →\nH ∝ 1/r³ (утричі далі — /27)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.2, color=INK))
    # підпис плато зблизька
    parts.append(fitbox(150, 66, 220, 44,
                        "близько (r ≲ котушки):\nполе майже не падає",
                        size=11, fill="#f4f6f8", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(IMG, "falloff.svg"), W, H, *parts,
           title="Поле ближньої зони: плато зблизька, злам у 1/r³ далі")


# ── Фігура 6 (math-coupling): взаємна індуктивність двох котушок ──────────────
# Дві котушки — слабко зв'язаний трансформатор. Частина потоку однієї пронизує
# другу; частка спільного потоку = коефіцієнт зв'язку k = M/√(L1 L2), тут k мале.
def fig_coupling():
    W, H = 760, 380
    parts = []

    # котушка 1 (зчитувач) зліва — витки
    c1x, c1y = 170, 180
    for i in range(3):
        parts.append(circle(c1x, c1y, 46 - i * 12, fill="none", stroke=NEG, sw=2.2))
    parts.append(text(c1x, 262, "котушка зчитувача", 11, NEG, "middle", bold=True))
    parts.append(text(c1x, 278, "L₁, струм I₁", 11, NEG, "middle"))

    # котушка 2 (брелок) справа
    c2x, c2y = 590, 180
    for i in range(3):
        parts.append(circle(c2x, c2y, 46 - i * 12, fill="none", stroke=FIELD, sw=2.2))
    parts.append(text(c2x, 262, "котушка брелка", 11, FIELD, "middle", bold=True))
    parts.append(text(c2x, 278, "L₂", 11, FIELD, "middle"))

    # силові лінії: широкий сніп від L1, лише частина доходить до L2
    for dy in (-58, -20, 20, 58):
        parts.append('<path d="M %.0f %.0f C %.0f %.0f %.0f %.0f %.0f %.0f" '
                     'fill="none" stroke="%s" stroke-width="1.5" '
                     'stroke-dasharray="5 4"/>'
                     % (c1x + 18, c1y + dy, 320, c1y + dy * 0.4,
                        440, c1y + dy * 0.4, c2x - 18, c2y + dy,
                        POS if abs(dy) < 40 else MUTED))
    parts.append(text(380, 96, "магнітний потік від котушки 1", 12, POS, "middle", bold=True))
    parts.append(text(380, 300, "лише частина потоку пронизує котушку 2 →  "
                                 "звʼязок слабкий", 11, MUTED, "middle"))

    # формула-рамка знизу
    parts.append(fitbox(230, 322, 300, 40,
                        "коефіцієнт звʼязку  k = M / √(L₁·L₂),  тут k ≈ 0.01…0.1",
                        size=12, fill="#f4f6f8", stroke=INK, sw=1.4, color=INK, bold=True))

    render(os.path.join(IMG, "coupling.svg"), W, H, *parts,
           title="Взаємна індуктивність: слабко звʼязаний трансформатор без осердя")


fig_principle()
fig_inside()
fig_memory()
fig_resonance()
fig_falloff()
fig_coupling()
print("Done. SVG in", IMG)
